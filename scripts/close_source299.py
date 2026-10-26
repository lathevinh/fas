"""Verify the complete saved source experiment without inference or optimization."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from fas.feature_cache import cache_key, digest, load_shard, payload_digest
from fas.freeze import write_immutable_record
from fas.frozen_features import mean_cosine_logit
from fas.source_experiment import predict, system_scores
from fas.source_fitting import calibrate, head_logits, identity, objective_weights, operating_threshold, sigmoid
from fas.source_diagnostics import design, weighted_ranking
import run_source299 as run


def check_predictions(actual: list[dict], expected: list[dict]) -> None:
    if len(actual) != len(expected):
        raise ValueError("saved source prediction count drift")
    for saved, rebuilt in zip(actual, expected, strict=True):
        for key in ("id", "dataset", "group_id", "role", "label", "errors", "thresholds", "fit_sha256"):
            if saved[key] != rebuilt[key]:
                raise ValueError(f"saved source {key} does not reconstruct")
        for key in ("scores", "probabilities"):
            if set(saved[key]) != set(rebuilt[key]) or not np.allclose(
                list(saved[key].values()), [rebuilt[key][name] for name in saved[key]], rtol=1e-12, atol=1e-12
            ):
                raise ValueError("saved calibrated source scores do not reconstruct")
        if saved["quality"] != rebuilt["quality"]:
            raise ValueError("saved source quality does not reconstruct")


def check_heads(fitted: dict, rows: list[dict], features: dict[str, np.ndarray], index: dict[str, int]) -> None:
    validation = np.asarray([index[key] for key in fitted["split"]["validation"]])
    labels = np.asarray([rows[position]["binary_label"] == "attack" for position in validation])
    weights = objective_weights(labels, [rows[position]["dataset"] for position in validation], balanced=True)
    for name, head in fitted["heads"].items():
        losses = head["validation_history"]
        if len(losses) != 200 or head["selected_epoch"] != int(np.argmin(losses)) + 1:
            raise ValueError("saved head is not the earliest minimum checkpoint under200 epochs")
        logits = head_logits(head, features[name][validation])
        loss = float(weights @ (np.logaddexp(0, logits) - labels * logits))
        if not np.isclose(loss, head["validation_bce"], rtol=1e-10, atol=1e-10):
            raise ValueError("saved selected head validation objective does not reconstruct")


def close():
    config, plan, approval = run.authority()
    run.enforce(approval, final=True)
    terminal = run.read(run.OUTPUT / "terminal.json")
    worker = run.read(run.OUTPUT / "worker_completion.json")
    if (terminal["status"] != "complete" or terminal["failure"] is not None
            or digest(run.OUTPUT / "worker_completion.json") != terminal["worker_completion_sha256"]
            or terminal["sampled_peak_combined_rss"] > config["limits"]["rss_bytes"]
            or terminal["peak_owned_new_temporary_bytes"] > config["limits"]["output_bytes"]):
        raise ValueError("successful exact source299 resource terminal required")
    inputs = run.read(run.OUTPUT / "inputs.json")
    rows = inputs["rows"]
    receipt = run.read(run.OUTPUT / "extraction.json")
    if digest(run.OUTPUT / "extraction.json") != worker["extraction_sha256"]:
        raise ValueError("saved extraction receipt hash drift")
    prior = run.read(run.old.OUTPUT / "extraction.json")
    missing = [row for row in rows if row["dataset"] == "OULU-NPU"]
    union_ids = prior["dino_reg"]["ids"] + [identity(row) for row in missing]
    positions = {key: position for position, key in enumerate(union_ids)}
    order = [positions[identity(row)] for row in rows]
    pilot = run.read(run.old.pilot.CONFIG)
    features, new_calls = {}, 0
    for name in ("dino_reg", "dino_plain", "openclip"):
        model = receipt[name]
        keys = [cache_key(run.old.base_key(row, name, pilot, model["checkpoint_sha256"]), model["contract"]) for row in missing]
        if model["keys"] != keys or len(set(keys)) != 4949:
            raise ValueError("exact source/runtime/cache-key coverage drift")
        parts, offset = [], 0
        for shard in model["shards"]:
            path = Path(shard["path"])
            if digest(path) != shard["sha256"]:
                raise ValueError("saved new source shard SHA drift")
            parts.append(load_shard(path, keys[offset:offset + shard["count"]], model["shape"][1]))
            offset += shard["count"]
        if offset != 4949 or model["new_image_forwards"] != 4949:
            raise ValueError("no repeated or missing new OULU source feature rows allowed")
        if max(model["final_peak_allocated"], model["final_peak_reserved"]) > config["limits"]["cuda_bytes"]:
            raise ValueError("saved final CUDA allocator peak exceeded authority")
        old_features = run.old.load_features(prior, name)
        features[name] = np.concatenate([old_features, np.concatenate(parts)])[order]
        new_calls += model["new_image_forwards"]
    old_quality = run.load_quality(run.read(run.old.OUTPUT / "quality.json"))
    quality = np.concatenate([old_quality, run.load_quality(receipt["quality"])])[order]
    if receipt["ids"] != [identity(row) for row in rows] or quality.shape != (6855, 5):
        raise ValueError("exact complete union feature/quality identity join required")
    text_path = Path(prior["text"]["path"])
    if digest(text_path) != prior["text"]["sha256"]:
        raise ValueError("fixed prompt embedding bytes changed")
    text = np.load(text_path, allow_pickle=False)
    prompts = run.read(ROOT / "configs/prompts_core_v1.yaml")["classes"]
    union_index = {identity(row): index for index, row in enumerate(rows)}
    model_count, prediction_count, risk_count, reused_contexts = 0, 0, 0, 0
    for context in inputs["contexts"]:
        run.enforce(approval, final=True)
        root = run.OUTPUT / "combinations" / context["key"]
        result = run.read(root / "result.json")
        published = next(value for value in worker["combinations"] if value["key"] == context["key"])
        if result != published:
            raise ValueError("private/public source combination receipt mismatch")
        indices = [union_index[key] for key in context["row_ids"]]
        local_rows = [rows[index] for index in indices]
        if any(row["dataset"] == context["outer_target"] for row in local_rows):
            raise ValueError("outer target entered source reconstruction")
        local = {name: value[indices] for name, value in features.items()}
        q = quality[indices]
        clip = mean_cosine_logit(local["openclip"], text, len(prompts["live"]))
        candidate_ids = [identity(row) for row in local_rows if row["role"] != "g_domain"]
        gate_ids = [identity(row) for row in local_rows if row["role"] == "g_domain"]
        reconstructed = {}
        oof = {name: [] for name in ("domain_oof", "matched_sample_oof", "budget_domain_oof", "budget_matched_sample_oof")}
        for split in context["partitions"]:
            path = root / "fits" / f"{payload_digest({'split': split})}.json"
            meta = next(value for value in result["contexts"] if value["context"] == split["name"])
            if digest(path) != meta["sha256"]:
                raise ValueError("saved primary fitted context bytes drift")
            artifact = run.read(path)
            fitted = artifact["fitted"]
            if fitted["split"] != split:
                raise ValueError("saved primary context group partition drift")
            local_index = {identity(row): index for index, row in enumerate(local_rows)}
            check_heads(fitted, local_rows, local, local_index)
            calibration_indices = np.asarray([local_index[key] for key in split["calibration"]])
            logits = {name: head_logits(fitted["heads"][name], local[name]) for name in ("dino_reg", "dino_plain")}
            logits["openclip"] = clip
            calibrated = {name: calibrate(fitted["calibrators"][name], value[calibration_indices])
                          for name, value in logits.items()}
            systems = system_scores(calibrated)
            for name, values in systems.items():
                policy = operating_threshold(values, [local_rows[index] for index in calibration_indices], alpha=0.05)
                recorded = fitted["policies"][name]
                if (not np.isclose(policy["threshold"], recorded["threshold"], rtol=1e-12, atol=1e-12)
                        or policy["source_apcer"] != recorded["source_apcer"]):
                    raise ValueError("source threshold does not reconstruct from its allowed calibration remainder")
            saved_path = root / "predictions" / f"{payload_digest({'name': split['name']})}.json"
            saved = run.read(saved_path)["rows"]
            ids = gate_ids if split["name"] == "final" else split["evaluation"]
            rebuilt = predict(local_rows, local, clip, q, ids, fitted, meta.get("original_model_sha256", meta["sha256"]))
            check_predictions(saved, rebuilt)
            prediction_count += len(saved)
            model_count += 2
            if meta["origin"] == "verified_completed_context_reuse":
                reused_contexts += 1
            reconstructed[split["name"]] = saved
            if split["name"] != "final":
                oof[split["name"].split(":", 1)[0]].extend(saved)
        for split in context["budget_partitions"]:
            primary = next(value for value in context["partitions"] if value["name"] == split["name"])
            strategy = "budget_" + split["name"].split(":", 1)[0]
            if split == primary:
                oof[strategy].extend(reconstructed[split["name"]])
                continue
            path = root / "budget-fits" / f"{payload_digest({'split': split})}.json"
            meta = next(value for value in result["contexts"] if value["context"] == "budget_" + split["name"])
            if digest(path) != meta["sha256"]:
                raise ValueError("budget-matched fitted state hash drift")
            fitted = run.read(path)["fitted"]
            if fitted["split"] != split or len(split["fitting"]) > context["budget_cap"]:
                raise ValueError("budget-matched source partition/count drift")
            check_heads(fitted, local_rows, local, local_index)
            rebuilt = predict(local_rows, local, clip, q, split["evaluation"], fitted, meta["sha256"])
            evaluation_ids = set(split["evaluation"])
            saved = [record for record in run.read(root / f"{strategy}.json")["rows"] if record["id"] in evaluation_ids]
            check_predictions(saved, rebuilt)
            oof[strategy].extend(rebuilt)
            model_count += 2
            prediction_count += len(saved)
        for strategy, expected in oof.items():
            check_predictions(run.read(root / f"{strategy}.json")["rows"], expected)
        statistics_receipt = run.read(root / "risk_statistics.json")
        fitting_ids = context["partitions"][0]["fitting"]
        local_index = {identity(row): index for index, row in enumerate(local_rows)}
        statistics = q[[local_index[key] for key in fitting_ids]]
        mean, raw_scale = statistics.mean(axis=0), statistics.std(axis=0)
        scale = np.where(raw_scale == 0, 1.0, raw_scale)
        if (statistics_receipt["fitting_ids"] != fitting_ids or statistics_receipt["quality_mean"] != mean.tolist()
                or statistics_receipt["quality_scale"] != scale.tolist()):
            raise ValueError("fixed shared final-head-fitting quality-statistics convention drift")
        final = reconstructed["final"]
        for risk in result["risk_fits"]:
            strategy, system, variant = risk["strategy"], risk["system"], risk["variant"]
            path = root / "risks" / strategy / f"{system}-{variant}.json"
            model = run.read(path)
            if any(model[key] != value for key, value in risk.items() if key != "strategy"):
                raise ValueError("saved risk model summary differs from immutable worker receipt")
            source = run.read(root / f"{strategy}.json")["rows"]
            if len(source) != len(candidate_ids) or {row["id"] for row in source} != set(candidate_ids):
                raise ValueError("identical original OOF candidate universe not preserved")
            error_count = sum(row["errors"][system] for row in source)
            if error_count != model["error_count"] or len(source) - error_count != model["correct_count"]:
                raise ValueError("risk supervision contains invented or wrong source error events")
            if model["status"] != "fitted":
                if min(model["error_count"], model["correct_count"]) >= 20:
                    raise ValueError("unsupported risk applicability shortfall claim")
                continue
            if (model["binding"]["oof_sha256"] != digest(root / f"{strategy}.json")
                    or model["quality_mean"] != mean.tolist() or model["quality_scale"] != scale.tolist()):
                raise ValueError("risk fit supervision/statistics provenance drift")
            values = design(final, system, variant, mean, scale)
            scores = sigmoid(head_logits(model["model"], values))
            if ([row["id"] for row in model["predictions"]] != gate_ids
                    or not np.allclose(scores, [row["risk"] for row in model["predictions"]], rtol=1e-12, atol=1e-12)):
                raise ValueError("saved source risk score/sample joins do not reconstruct")
            errors = np.asarray([row["errors"][system] for row in final])
            if [row["error"] for row in model["predictions"]] != errors.tolist():
                raise ValueError("saved risk evaluation error labels do not reconstruct")
            ap = weighted_ranking(errors, scores, np.ones(len(final)), "ap")
            if (ap is None) != (model["held_out_error_AP"] is None) or (
                ap is not None and not np.isclose(ap, model["held_out_error_AP"], rtol=1e-12, atol=1e-12)
            ):
                raise ValueError("saved held-out source risk AP does not reconstruct")
            risk_count += 1
    if reused_contexts != 7 or len(worker["combinations"]) != 12 or new_calls != 14847:
        raise ValueError("complete execution/reuse accounting mismatch")
    run.enforce(approval, final=True)
    result = {"version": 1, "checkpoint": 299, "status": "saved_complete_source_experiment_verified",
              "worker_sha256": digest(run.OUTPUT / "worker_completion.json"),
              "terminal_sha256": digest(run.OUTPUT / "terminal.json"),
              "closure_script_sha256": digest(Path(__file__)), "combination_count": 12,
              "feature_rows_per_backbone": 6855, "new_image_forwards_verified": new_calls,
              "reused297_contexts_verified": reused_contexts, "head_models_verified": model_count,
              "source_prediction_rows_reconstructed": prediction_count, "risk_models_verified": risk_count,
              "new_encoder_calls": 0, "new_optimization_calls": 0, "target_predictions": False,
              "wall_seconds_from_original_approval": time.time() - approval["started_unix_seconds"],
              "source_dry_run_validator_passed": worker["source_dry_run_validator_passed"],
              "stage_errors": worker["stage_errors"], "locked_evaluation_authorized": False}
    write_immutable_record(run.OUTPUT / "closure.json", result)
    write_immutable_record(ROOT / "results/phase1/source-closure299-v1.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    close()
