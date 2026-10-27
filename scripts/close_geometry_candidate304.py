"""Verify saved G2 source-only artifacts and publish an aggregate comparison."""

from __future__ import annotations

from collections import Counter
import io
import json
from pathlib import Path
import sys
import time

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import build_geometry_candidate304 as builder
import run_geometry_candidate304 as base
import run_geometry_candidate304_v2 as candidate
from close_source299 import check_heads, check_predictions
from fas.feature_cache import digest, payload_digest
from fas.freeze import write_immutable_record
from fas.frozen_features import mean_cosine_logit
from fas.geometry_candidate import pad_shared_crop
from fas.source_diagnostics import design, weighted_ranking
from fas.source_experiment import predict, system_scores
from fas.source_fitting import calibrate, head_logits, identity, operating_threshold, sigmoid

PUBLIC = ROOT / "results/phase1/source-geometry304-closure-v1.json"
SYSTEMS = ("dino_reg", "openclip", "heterogeneous", "same_family")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify_images(rows: list[dict], failures: list[dict]) -> dict:
    receipt = builder.read_json(builder.OUTPUT / "generation_receipt.json")
    entries = {entry["sample_key_sha256"]: entry for entry in receipt["entries"]}
    count = byte_count = 0
    for row in rows:
        rgb, _ = builder.checked_shared_crop(row)
        entry = entries[builder.sample_key(row)]
        for resolution in (224, 518):
            artifact = entry["crops"][str(resolution)]
            expected, geometry = pad_shared_crop(rgb, resolution)
            payload = (builder.OUTPUT / artifact["path"]).read_bytes()
            require(builder.sha256(payload) == artifact["sha256"], "candidate crop file hash drift")
            with Image.open(io.BytesIO(payload)) as image:
                require(image.mode == "RGB", "candidate crop is not RGB")
                actual = np.asarray(image)
            require(np.array_equal(actual, expected), "candidate geometry pixels do not reconstruct")
            require(artifact["geometry"] == geometry, "candidate geometry metadata does not reconstruct")
            require(row["crops"][str(resolution)]["sha256"] == artifact["sha256"], "model crop join drift")
            count += 1
            byte_count += len(payload)
        if count % 1000 == 0:
            print(f"GEOMETRY304_IMAGES_VERIFIED {count}/13710", flush=True)
    for row in failures:
        entry = entries[builder.sample_key(row)]
        require(entry["status"] == "terminal_non_accept" and not entry["crops"],
                "failed source original acquired candidate features")
    require(count == 13710 and len(failures) == 27, "candidate image/failure coverage drift")
    require(byte_count == receipt["candidate_output_bytes"], "candidate image byte count drift")
    return {"images_pixel_verified": count, "image_bytes": byte_count,
            "retained_source_failures": len(failures)}


def verify_policy(fitted: dict, rows: list[dict], features: dict, clip: np.ndarray) -> None:
    positions = {identity(row): index for index, row in enumerate(rows)}
    indices = np.asarray([positions[key] for key in fitted["split"]["calibration"]])
    logits = {name: head_logits(fitted["heads"][name], features[name][indices])
              for name in ("dino_reg", "dino_plain")}
    logits["openclip"] = clip[indices]
    probabilities = {name: calibrate(fitted["calibrators"][name], values)
                     for name, values in logits.items()}
    for name, values in system_scores(probabilities).items():
        expected = operating_threshold(values, [rows[index] for index in indices], alpha=0.05)
        recorded = fitted["policies"][name]
        require(np.isclose(expected["threshold"], recorded["threshold"], rtol=1e-12, atol=1e-12)
                and {key: value for key, value in expected.items() if key != "threshold"}
                == {key: value for key, value in recorded.items() if key != "threshold"},
                "source operating policy does not reconstruct")


def verify_context(context: dict, result: dict, union: list[dict], features: dict,
                   quality: np.ndarray, text: np.ndarray, worker: dict) -> dict:
    root = candidate.OUTPUT / "combinations" / context["key"]
    require(candidate.read_json(root / "result.json") == result, "worker/result mismatch")
    positions = {identity(row): index for index, row in enumerate(union)}
    selected = [positions[key] for key in context["row_ids"]]
    rows = [union[index] for index in selected]
    require(all(row["dataset"] != context["outer_target"] for row in rows), "outer exclusion violated")
    local = {name: values[selected] for name, values in features.items()}
    q = quality[selected]
    index = {identity(row): i for i, row in enumerate(rows)}
    prompts = candidate.read_json(ROOT / "configs/prompts_core_v1.yaml")["classes"]
    clip = mean_cosine_logit(local["openclip"], text, len(prompts["live"]))
    gate_ids = [identity(row) for row in rows if row["role"] == "g_domain"]
    candidate_ids = {identity(row) for row in rows if row["role"] != "g_domain"}
    expected_binding = {"config_sha256": worker["config_sha256"], "inputs_sha256": worker["inputs_sha256"],
                        "extraction_sha256": worker["extraction_sha256"],
                        "outer_target": context["outer_target"], "seed": context["seed"]}
    reconstructed = {}
    strategies = {name: [] for name in (
        "domain_oof", "matched_sample_oof", "budget_domain_oof", "budget_matched_sample_oof")}
    heads = predictions = calibrators = 0
    for budget, splits in ((False, context["partitions"]), (True, context["budget_partitions"])):
        for split in splits:
            primary = next(item for item in context["partitions"] if item["name"] == split["name"])
            strategy = ("budget_" if budget else "") + split["name"].split(":", 1)[0]
            if budget and split == primary:
                strategies[strategy].extend(reconstructed[split["name"]])
                continue
            directory = "budget-fits" if budget else "fits"
            path = root / directory / f"{payload_digest({'split': split})}.json"
            name = ("budget_" if budget else "") + split["name"]
            meta = next(item for item in result["contexts"] if item["context"] == name)
            require(digest(path) == meta["sha256"], "fitted source state hash drift")
            fitted = candidate.read_json(path)["fitted"]
            require(fitted["split"] == split and fitted["binding"] == expected_binding,
                    "fitted source split/binding drift")
            check_heads(fitted, rows, local, index)
            verify_policy(fitted, rows, local, clip)
            ids = gate_ids if split["name"] == "final" else split["evaluation"]
            rebuilt = predict(rows, local, clip, q, ids, fitted, meta["sha256"])
            if budget:
                evaluation = set(ids)
                saved = [record for record in candidate.read_json(root / f"{strategy}.json")["rows"]
                         if record["id"] in evaluation]
                require(len(split["fitting"]) <= context["budget_cap"], "fit-size control exceeds cap")
            else:
                saved_path = root / "predictions" / f"{payload_digest({'name': split['name']})}.json"
                saved = candidate.read_json(saved_path)["rows"]
                reconstructed[split["name"]] = saved
            check_predictions(saved, rebuilt)
            if split["name"] != "final":
                strategies[strategy].extend(rebuilt)
            heads += 2
            calibrators += 3
            predictions += len(saved)
    for strategy, records in strategies.items():
        require(len(records) == len(candidate_ids) and {r["id"] for r in records} == candidate_ids,
                "OOF coverage is not exactly once per non-gate source original")
        check_predictions(candidate.read_json(root / f"{strategy}.json")["rows"], records)
    fitting_ids = context["partitions"][0]["fitting"]
    statistics = q[[index[key] for key in fitting_ids]]
    mean, raw_scale = statistics.mean(axis=0), statistics.std(axis=0)
    scale = np.where(raw_scale == 0, 1.0, raw_scale)
    recorded_stats = candidate.read_json(root / "risk_statistics.json")
    require(recorded_stats["fitting_ids"] == fitting_ids
            and recorded_stats["quality_mean"] == mean.tolist()
            and recorded_stats["quality_scale"] == scale.tolist(), "risk statistics lineage drift")
    final = reconstructed["final"]
    risks = 0
    for summary in result["risk_fits"]:
        strategy, system, variant = (summary[key] for key in ("strategy", "system", "variant"))
        path = root / "risks" / strategy / f"{system}-{variant}.json"
        saved = candidate.read_json(path)
        require(all(saved[key] == value for key, value in summary.items() if key != "strategy"),
                "risk worker summary drift")
        source = strategies[strategy]
        errors = sum(row["errors"][system] for row in source)
        require(saved["error_count"] == errors and saved["correct_count"] == len(source) - errors,
                "risk supervision count drift")
        require(saved["status"] == "fitted" and saved["model"]["line_search_maximum"] == 50,
                "uniform amended risk optimizer missing")
        require(saved["binding"] == {**expected_binding, "oof_sha256": digest(root / f"{strategy}.json")}
                and saved["quality_mean"] == mean.tolist() and saved["quality_scale"] == scale.tolist(),
                "risk model input binding drift")
        logits = head_logits(saved["model"], design(final, system, variant, mean, scale))
        scores = sigmoid(logits)
        actual = np.asarray([row["risk"] for row in saved["predictions"]])
        labels = np.asarray([row["errors"][system] for row in final])
        require([row["id"] for row in saved["predictions"]] == gate_ids
                and [row["error"] for row in saved["predictions"]] == labels.tolist()
                and np.allclose(scores, actual, rtol=1e-12, atol=1e-12),
                "saved G_domain risk predictions do not reconstruct")
        ap = weighted_ranking(labels, scores, np.ones(len(labels)), "ap")
        require(ap is not None and np.isclose(ap, saved["held_out_error_AP"], rtol=1e-12, atol=1e-12),
                "held-out risk AP drift")
        risks += 1
    for system in SYSTEMS:
        records = strategies["domain_oof"]
        aucs, bas = [], []
        for domain in sorted({row["dataset"] for row in records}):
            domain_rows = [row for row in records if row["dataset"] == domain]
            labels = np.asarray([row["label"] for row in domain_rows])
            scores = np.asarray([row["scores"][system] for row in domain_rows])
            aucs.append(weighted_ranking(labels, scores, np.ones(len(labels)), "auroc"))
            bas.append(np.mean([np.mean([row["errors"][system] == 0 for row in domain_rows
                                         if row["label"] == label]) for label in (0, 1)]))
        require(all(value is not None for value in aucs)
                and np.isclose(np.mean(aucs), result["systems"][system]["macro_auroc"])
                and np.isclose(np.mean(bas), result["systems"][system]["macro_balanced_accuracy"]),
                "source competence point metrics drift")
    print(f"GEOMETRY304_CONTEXT_VERIFIED {context['key']}", flush=True)
    return {"heads": heads, "calibrators": calibrators, "prediction_rows": predictions, "risks": risks}


def compare_results(baseline: list[dict], revised: list[dict]) -> dict:
    old = {row["key"]: row for row in baseline}
    new = {row["key"]: row for row in revised}
    require(len(old) == len(baseline) and len(new) == len(revised) and set(old) == set(new),
            "baseline/candidate context coverage differs or contains duplicates")
    require(len(new) == 12, "exactly 12 contexts required for the comparison")
    comparisons = []
    for key in sorted(new):
        require(old[key]["seed"] == new[key]["seed"]
                and old[key]["source_domains"] == new[key]["source_domains"]
                and old[key]["denominators"] == new[key]["denominators"], "comparison population drift")
        systems = {}
        for name in SYSTEMS:
            baseline_auc = old[key]["systems"][name]["macro_auroc"]
            candidate_auc = new[key]["systems"][name]["macro_auroc"]
            systems[name] = {"baseline_source_macro_auroc": baseline_auc,
                             "candidate_source_macro_auroc": candidate_auc,
                             "candidate_minus_baseline": candidate_auc - baseline_auc,
                             "candidate_source_competence_pass": new[key]["systems"][name]["pass"]}
        comparisons.append({"context": key, "outer_source_exclusion": new[key]["outer_target"],
                            "seed": new[key]["seed"], "systems": systems})
    summary = {}
    for name in SYSTEMS:
        values = [row["systems"][name] for row in comparisons]
        deltas = [row["candidate_minus_baseline"] for row in values]
        summary[name] = {
            "baseline_mean": float(np.mean([row["baseline_source_macro_auroc"] for row in values])),
            "candidate_mean": float(np.mean([row["candidate_source_macro_auroc"] for row in values])),
            "mean_delta": float(np.mean(deltas)),
            "positive_contexts": sum(value > 0 for value in deltas),
            "candidate_competence_pass_contexts": sum(row["candidate_source_competence_pass"] for row in values),
        }
    return {"context_comparisons": comparisons, "descriptive_mean_over_overlapping_contexts": summary,
            "independent_replicates": False, "geometry_effect_confidence_interval": None}


def close() -> dict:
    require(not PUBLIC.exists(), "304 aggregate closure already exists; do not overwrite")
    started = time.monotonic()
    worker = candidate.read_json(candidate.OUTPUT / "worker_completion.json")
    cfg = candidate.read_json(candidate.CONFIG)
    require(worker["status"] == "complete_source_only_exploratory"
            and worker["config_sha256"] == digest(candidate.CONFIG)
            and worker["inputs_sha256"] == digest(candidate.OUTPUT / "inputs.json")
            and worker["extraction_sha256"] == digest(candidate.OUTPUT / "extraction.json"),
            "completed G2 worker bindings drift")
    rows, failures, manifest = base.source_inputs()
    original_config = base.CONFIG
    base.CONFIG = candidate.CONFIG
    try:
        expected_inputs = base.prepare_inputs(rows, failures, manifest)
    finally:
        base.CONFIG = original_config
    inputs = candidate.read_json(candidate.OUTPUT / "inputs.json")
    require(inputs == expected_inputs, "saved source-only partitions do not reconstruct")
    features, quality, extracted = candidate.load_verified_features(
        rows, started, {"deadline_unix_seconds": time.time() + 7200})
    images = verify_images(rows, failures)
    indexed = {row["key"]: row for row in worker["combinations"]}
    require(len(indexed) == 12 and len(worker["combinations"]) == 12, "worker context coverage drift")
    verified = Counter()
    for context in inputs["contexts"]:
        verified.update(verify_context(context, indexed[context["key"]], rows,
                                       features, quality, extracted["text"], worker))
    require(verified["risks"] == 480, "full 480-risk-model coverage required")
    baseline_path = base.source299.OUTPUT / "worker_completion.json"
    baseline = candidate.read_json(baseline_path)
    published_baseline = candidate.read_json(ROOT / "results/phase1/source-run299-v1.json")
    terminal = candidate.read_json(base.source299.OUTPUT / "terminal.json")
    require(published_baseline == {**baseline, "terminal": terminal}
            and terminal["status"] == "complete"
            and terminal["worker_completion_sha256"] == digest(baseline_path),
            "accepted baseline worker/public evidence drift")
    comparison = compare_results(baseline["combinations"], worker["combinations"])
    primary = [next(p for p in row["paired_source_diagnostics"]
                    if p["system"] == "heterogeneous" and p["variant"] == "R_DVd"
                    and not p["budget_matched"]) for row in worker["combinations"]]
    receipt = {
        "version": 1, "checkpoint": 304, "status": "saved_source_only_geometry_verified",
        "closure_script_sha256": digest(Path(__file__)),
        "worker_sha256": digest(candidate.OUTPUT / "worker_completion.json"),
        "config_sha256": digest(candidate.CONFIG), "baseline_worker_sha256": digest(baseline_path),
        "geometry_generation_sha256": digest(base.GENERATION_RECEIPT),
        "source_originals": len(rows) + len(failures), "source_successes": len(rows),
        "candidate_feature_rows_per_encoder": len(rows), "combination_count": len(indexed),
        "verification": {**images, **verified},
        "comparison": comparison,
        "heterogeneous_domain_minus_sample_AP": {
            "saved_interval_status_counts": dict(Counter(p["status"] for p in primary)),
            "positive_point_contexts": sum(p["delta"] > 0 for p in primary),
            "per_context": [{"context": row["key"], **p}
                            for row, p in zip(worker["combinations"], primary, strict=True)],
        },
        "candidate_generation_wall_seconds": builder.read_json(base.GENERATION_RECEIPT)["wall_seconds"],
        "final_source_fit_wall_seconds": worker["wall_seconds"],
        "final_source_fit_peak_rss_bytes": worker["peak_rss_bytes"],
        "scope": {"source_only_exploratory": True, "independent_target_evidence": False,
                  "target_predictions": False, "new_encoder_calls_in_closure": 0,
                  "new_optimization_calls_in_closure": 0, "bootstrap_resampling_in_closure": False,
                  "crop_pixel_reconstruction_in_closure": True,
                  "nested_fusion_selection_completed": False},
        "risk_optimizer": cfg["risk_optimizer"],
        "closure_wall_seconds": time.monotonic() - started,
    }
    write_immutable_record(candidate.OUTPUT / "closure.json", receipt)
    write_immutable_record(PUBLIC, receipt)
    return receipt


if __name__ == "__main__":
    result = close()
    print(json.dumps({key: value for key, value in result.items()
                      if key not in {"comparison", "heterogeneous_domain_minus_sample_AP"}}, indent=2))
