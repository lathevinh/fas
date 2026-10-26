"""Generalized bounded source-only twelve-combination experiment."""

from __future__ import annotations

import argparse
import gc
import hashlib
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import numpy as np

from fas.feature_cache import cache_key, digest, load_shard, payload_digest, save_shard
from fas.freeze import write_immutable_record
from fas.frozen_features import check_feature, dino_pool, mean_cosine_logit, normalize_rgb
from fas.source_stage import population_counts, require_source_input
from fas.source_fitting import identity, partitions, quality_vector
from fas.source_diagnostics import budget_split, competence, design, paired_ap
from fas.source_experiment import diagnostics, fit_context, predict, risk_run, seal
from fas.environment import verify_source_checkout
from fas.preregistration import validate_stage, SOURCE_POLICY_PATH
import run_source297 as old

CONFIG = ROOT / "configs/source_run299_v1.yaml"
OUTPUT = Path("/mnt/e/FAS-private/artifacts/phase1/source_run299_v1")
CACHE = Path.home() / ".cache/fas/source-run299-v1"
CODE = (*old.CODE, "scripts/run_source299.py", "src/fas/source_experiment.py",
        "src/fas/source_diagnostics.py", "src/fas/preregistration.py", "scripts/write_freeze_record.py")


def read(path: Path) -> dict:
    return old.read(path)


def accepted() -> tuple[dict, dict, dict]:
    config = read(CONFIG)
    if digest(old.CONFIG) != config["inherited_config_sha256"]:
        raise ValueError("unchanged297 execution settings required")
    if (digest(old.OUTPUT / "worker_completion.json") != config["completed297_worker_sha256"]
            or read(old.OUTPUT / "terminal.json")["status"] != "complete"):
        raise ValueError("accepted297 completion and successful terminal required")
    worker = read(old.OUTPUT / "worker_completion.json")
    for model in worker["fitting"]["folds"]:
        path = old.OUTPUT / "fits" / f"{payload_digest({'name': model['fold']})}.json"
        prediction = path.with_name(path.stem + "-predictions.json")
        if digest(path) != model["fit_sha256"] or digest(prediction) != model["predictions_sha256"]:
            raise ValueError("completed297 fitted context/prediction bytes changed")
    for risk in worker["fitting"]["risk_results"]:
        if risk["status"] == "fitted":
            path = old.OUTPUT / "risks" / f"{risk['strategy']}-{risk['system']}-{risk['variant']}.json"
            if digest(path) != risk["model_sha256"]:
                raise ValueError("completed297 fitted risk bytes changed")
    old.authority()
    old.source_rows(read(old.CONFIG))
    manifest = read(old.pilot.INTEGRATION / "source_manifest.json")
    if digest(old.pilot.INTEGRATION / "source_manifest.json") != config["source_manifest_sha256"]:
        raise ValueError("sealed accepted source manifest changed")
    return config, read(old.CONFIG), manifest


def prepare() -> None:
    config, inherited, manifest = accepted()
    rows = sorted([row for row in manifest["rows"] if row["source_use_eligible"] and row["model_input_eligible"]], key=identity)
    failures = [row for row in manifest["rows"] if row["source_use_eligible"] and not row["model_input_eligible"]]
    if len(rows) != 6855 or len(failures) != 27:
        raise ValueError("exact source union required")
    indexed = {identity(row): row for row in rows}
    contexts = []
    new_contexts = 0
    for target in config["outer_targets"]:
        source_rows = [row for row in rows if row["dataset"] != target]
        original = [row for row in manifest["rows"] if row["source_use_eligible"] and row["dataset"] != target]
        for row in source_rows:
            purpose = {"train": "fitting", "branch_calibration": "calibration", "g_domain": "domain_use"}[row["role"]]
            require_source_input(row, outer_target=target, purpose=purpose, model_input=True)
        for seed in config["seeds"]:
            splits = partitions(source_rows, target, seed)
            cap = min(len(split["fitting"]) for split in splits if split["name"] != "final")
            sensitivities = [budget_split(split, indexed, cap, seed) for split in splits if split["name"] != "final"]
            retained297 = target == "OULU-NPU" and seed == 20260917
            if retained297 and splits != read(old.OUTPUT / "inputs.json")["partitions"]:
                raise ValueError("completed297 exact group splits must not change")
            new_contexts += (0 if retained297 else 7) + sum(
                sensitivity != primary for sensitivity, primary in zip(sensitivities, splits[1:], strict=True))
            contexts.append({"key": f"{target}-{seed}", "outer_target": target, "seed": seed,
                             "row_ids": [identity(row) for row in source_rows], "partitions": splits,
                             "budget_partitions": sensitivities, "budget_cap": cap,
                             "original_counts": population_counts(original), "reuse297": retained297})
    inputs = {"rows": rows, "failure_rows": failures, "contexts": contexts,
              "source_use_binding": manifest["source_use_binding"]}
    write_immutable_record(OUTPUT / "inputs.json", inputs)
    runtime = old.runtime()
    previous = read(old.OUTPUT / "execution_plan.json")["runtime"]
    if runtime != previous:
        raise ValueError("compatible exact297 numerical runtime required; no silent re-extraction")
    summary = {
        "version": 1, "checkpoint": 299, "config_sha256": digest(CONFIG),
        "inputs_sha256": digest(OUTPUT / "inputs.json"), "runtime": runtime,
        "implementation_sha256": {name: digest(ROOT / name) for name in dict.fromkeys(CODE)},
        "summaries_sha256": {name: digest(ROOT / name) for name in ("manifests/dataset_summary.csv", "manifests/split_summary.csv")},
        "combination_count": 12, "completed_primary_contexts_reused": 7,
        "new_head_fit_maximum": new_contexts * 2, "new_calibrator_fit_maximum": new_contexts * 3,
        "primary_risk_models_reused": 24, "new_risk_fit_maximum": 456,
        "domain_audit_fit_maximum": 48, "new_feature_inputs": 4949,
        "existing_feature_inputs": 1906, "new_image_forwards": 14847, "new_text_forwards": 0,
        "feature_payload_union_bytes": 6855 * 3584 * 4,
        "io_estimate_basis": {"observed297_full_run_seconds": read(old.OUTPUT / "terminal.json")["wall_seconds_from_original_approval"],
                              "observed297_extraction_seconds": {
                                  name: value["wall_seconds"] for name, value in read(old.OUTPUT / "extraction.json").items()
                                  if name != "text"}, "new_OULU_pixels_not_read_in_preflight": True},
        "fold_populations": [{"outer_target": c["outer_target"], "seed": c["seed"],
                              "source_denominator": c["original_counts"]["source_use"],
                              "successful_inputs": len(c["row_ids"]), "budget_cap": c["budget_cap"],
                              "budget_actual_counts": [len(s["fitting"]) for s in c["budget_partitions"]]}
                             for c in contexts],
        "limits": config["limits"], "no_target_predictions": True, "scientific_readiness": False}
    write_immutable_record(OUTPUT / "execution_plan.json", summary)
    write_immutable_record(ROOT / "results/phase1/source-plan299-v1.json",
                           {**summary, "execution_plan_sha256": digest(OUTPUT / "execution_plan.json")})
    print(read(OUTPUT / "execution_plan.json"))


def authority():
    config, plan, approval = read(CONFIG), read(OUTPUT / "execution_plan.json"), read(OUTPUT / "owner_approval.json")
    if (approval["explicit_owner_approval"] is not True
            or approval["selected_answer"] != "approve_source299_complete_fixed_source_experiment"
            or approval["config_sha256"] != digest(CONFIG) or plan["config_sha256"] != digest(CONFIG)
            or approval["execution_plan_sha256"] != digest(OUTPUT / "execution_plan.json")
            or approval["limits"] != config["limits"] or approval["automatic_retry"] is not False):
        raise ValueError("fresh exact source299 combined authority required")
    for field, seconds in (("deadline_unix_seconds", config["limits"]["wall_seconds"]),
                           ("work_deadline_unix_seconds", config["limits"]["work_seconds"])):
        if approval[field] != approval["started_unix_seconds"] + seconds:
            raise ValueError("non-resettable original deadline required")
    for name, expected in plan["implementation_sha256"].items():
        if digest(ROOT / name) != expected:
            raise ValueError(f"approved executable code/config changed: {name}")
    if digest(OUTPUT / "inputs.json") != plan["inputs_sha256"]:
        raise ValueError("sealed exact source/context inputs changed")
    return config, plan, approval


def owned_size() -> int:
    private = sum(path.stat().st_size for root in (OUTPUT, CACHE) if root.exists()
                  for path in root.rglob("*") if path.is_file())
    public_paths = [ROOT / "results/phase1" / name for name in ("source-plan299-v1.json", "source-run299-v1.json")]
    public_paths += [ROOT / "results/source-dry-run" / name for name in ("evidence.json", "competence.json", "applicability.json")]
    return private + sum(path.stat().st_size for path in public_paths if path.is_file())


def enforce(approval: dict, *, final=False):
    if time.time() >= approval["deadline_unix_seconds" if final else "work_deadline_unix_seconds"]:
        raise TimeoutError("original299 authority deadline")


def load_quality(receipt: dict) -> np.ndarray:
    parts, offset = [], 0
    for shard in receipt["shards"]:
        path = Path(shard["path"])
        if digest(path) != shard["sha256"]:
            raise ValueError("quality shard hash drift")
        parts.append(load_shard(path, receipt["keys"][offset:offset + shard["count"]], 5))
        offset += shard["count"]
    return np.concatenate(parts).astype(np.float64)


def extract(rows: list[dict], plan: dict, approval: dict) -> tuple[dict, np.ndarray, dict]:
    import torch
    import open_clip
    config = read(CONFIG)
    if old.runtime() != plan["runtime"]:
        raise ValueError("exact compatible runtime drift")
    old_receipt = read(old.OUTPUT / "extraction.json")
    old_worker = read(old.OUTPUT / "worker_completion.json")
    if (digest(old.OUTPUT / "extraction.json") != old_worker["extraction_sha256"]
            or digest(old.OUTPUT / "quality.json") != old_worker["quality_sha256"]):
        raise ValueError("accepted297 feature/quality receipt drift")
    old_ids = old_receipt["dino_reg"]["ids"]
    old_quality = load_quality(read(old.OUTPUT / "quality.json"))
    missing = [row for row in rows if row["dataset"] == "OULU-NPU"]
    if len(missing) != 4949 or set(old_ids) != {identity(row) for row in rows if row["dataset"] != "OULU-NPU"}:
        raise ValueError("exact1906 compatible existing plus4949 missing source features required")
    verify_source_checkout(old.pilot.UPSTREAM, read(old.pilot.CONFIG)["dinov2_source_commit"])
    if not torch.cuda.is_available():
        raise RuntimeError("source encoders require CUDA; no CPU fallback")
    torch.set_num_threads(2)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(20260917)
    torch.cuda.set_per_process_memory_fraction(config["limits"]["cuda_bytes"] / torch.cuda.get_device_properties(0).total_memory)
    sys.path.insert(0, str(old.pilot.UPSTREAM))
    from dinov2.hub import backbones
    pilot_config = read(old.pilot.CONFIG)
    mapping = {key: position for position, key in enumerate(old_ids + [identity(row) for row in missing])}
    order = [mapping[identity(row)] for row in rows]
    all_features, receipts = {}, {}
    for name, spec in pilot_config["models"].items():
        previous = old.load_features(old_receipt, name)
        checkpoint_sha = old_receipt[name]["checkpoint_sha256"]
        checkpoint = old.pilot.NATIVE / "checkpoints" / f"{name}.pth"
        if digest(checkpoint) != checkpoint_sha:
            raise ValueError("existing exact checkpoint required; no re-download")
        original_contract = old_receipt[name]["contract"]
        if original_contract["runtime"] != plan["runtime"]:
            raise ValueError("existing feature numerical contract is incompatible")
        contract = {**original_contract, "generalized_controller_sha256": digest(Path(__file__)),
                    "approved_source_access": ["outer_CASIA", "outer_MSU", "outer_SiW"],
                    "compatible297_extraction_sha256": digest(old.OUTPUT / "extraction.json")}
        keys = [cache_key(old.base_key(row, name, pilot_config, checkpoint_sha), contract) for row in missing]
        parts, shards, calls, model = [], [], 0, None
        mean, std = tuple(contract["normalization_mean"]), tuple(contract["normalization_std"])
        started = time.monotonic()
        torch.cuda.reset_peak_memory_stats()
        for start in range(0, len(missing), 32):
            enforce(approval)
            selected = missing[start:start + 32]
            selected_keys = keys[start:start + len(selected)]
            path = CACHE / name / f"{start:06d}.npz"
            hash_path = path.with_suffix(".json")
            if path.exists():
                if hash_path.exists() and read(hash_path)["sha256"] != digest(path):
                    raise ValueError("immutable299 shard drift")
                values = load_shard(path, selected_keys, spec["feature_dimension"])
            else:
                if model is None:
                    if name.startswith("dino"):
                        model = getattr(backbones, spec["local_factory"])(pretrained=False)
                        model.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True), strict=True)
                    else:
                        model = open_clip.create_model("ViT-B-16", pretrained=None, precision="fp32")
                        incompatible = open_clip.load_checkpoint(model, str(checkpoint), strict=True, weights_only=True)
                        if incompatible.missing_keys or incompatible.unexpected_keys:
                            raise ValueError("strict OpenCLIP loading failed")
                    model.requires_grad_(False).eval().cuda()
                values_list = []
                for row in selected:
                    enforce(approval)
                    rgb = old.bound_rgb(row, spec["resolution"])
                    tensor = torch.from_numpy(normalize_rgb(rgb, spec["resolution"], mean, std)[None]).cuda()
                    with torch.inference_mode():
                        if name.startswith("dino"):
                            output = model.forward_features(tensor)
                            value = dino_pool(output["x_norm_clstoken"].cpu().numpy(), output["x_norm_patchtokens"].cpu().numpy())
                            del output
                        else:
                            value = model.encode_image(tensor, normalize=True).cpu().numpy()
                    del tensor
                    check_feature(value, 1, spec["feature_dimension"])
                    values_list.append(value)
                    calls += 1
                    if max(torch.cuda.max_memory_allocated(), torch.cuda.max_memory_reserved()) > config["limits"]["cuda_bytes"]:
                        raise MemoryError("original299 CUDA allocator cap")
                values = np.concatenate(values_list)
                save_shard(path, selected_keys, values)
            if not hash_path.exists():
                write_immutable_record(hash_path, {"sha256": digest(path), "keys_sha256": payload_digest({"keys": selected_keys})})
            parts.append(values)
            shards.append({"path": str(path), "sha256": digest(path), "count": len(selected)})
            print("SOURCE299_EXTRACTION", name, start + len(selected), 4949, flush=True)
        all_features[name] = np.concatenate([previous, np.concatenate(parts)])[order]
        check_feature(all_features[name], 6855, spec["feature_dimension"])
        receipts[name] = {"shards": shards, "keys": keys, "contract": contract,
                          "checkpoint_sha256": checkpoint_sha, "new_image_forwards": calls,
                          "reused297_rows": 1906, "shape": [6855, spec["feature_dimension"]],
                          "final_peak_allocated": torch.cuda.max_memory_allocated(),
                          "final_peak_reserved": torch.cuda.max_memory_reserved(),
                          "wall_seconds": time.monotonic() - started}
        if model is not None:
            del model
        gc.collect()
        torch.cuda.empty_cache()
    quality_keys = [payload_digest({"id": identity(row), "crop": row["crops"]["224"]["sha256"],
                                   "record": row["record_sha256"], "quality_code": digest(ROOT / "src/fas/source_fitting.py")})
                    for row in missing]
    parts, shards = [], []
    for start in range(0, len(missing), 32):
        enforce(approval)
        selected = missing[start:start + 32]
        keys = quality_keys[start:start + len(selected)]
        path = CACHE / "quality" / f"{start:06d}.npz"
        if path.exists():
            values = load_shard(path, keys, 5)
        else:
            values_list = []
            for row in selected:
                transaction_path = Path(row["record_path"])
                if digest(transaction_path) != row["record_sha256"]:
                    raise ValueError("OULU saved detector transaction drift")
                transaction = read(transaction_path)
                if transaction["selected_frame"] != row["selected_frame"] or transaction["video_id"] != row["video_id"]:
                    raise ValueError("OULU source quality frame/identity join drift")
                values_list.append(quality_vector(old.bound_rgb(row, 224), transaction))
            values = np.asarray(values_list, dtype=np.float32)
            save_shard(path, keys, values)
        parts.append(values)
        shards.append({"path": str(path), "sha256": digest(path), "count": len(selected)})
    quality = np.concatenate([old_quality, np.concatenate(parts).astype(np.float64)])[order]
    receipts["quality"] = {"shards": shards, "keys": quality_keys, "shape": [6855, 5]}
    receipts["ids"] = [identity(row) for row in rows]
    text_path = Path(old_receipt["text"]["path"])
    if digest(text_path) != old_receipt["text"]["sha256"]:
        raise ValueError("fixed295 text bytes changed")
    text = np.load(text_path, allow_pickle=False)
    seal(OUTPUT / "extraction.json", receipts)
    return all_features, quality, {"text": text, "receipt": receipts}


def combination(context: dict, union: list[dict], all_features: dict, quality: np.ndarray,
                text: np.ndarray, config: dict, inherited: dict, approval: dict) -> dict:
    guard = lambda: enforce(approval)
    root = OUTPUT / "combinations" / context["key"]
    indexed_union = {identity(row): index for index, row in enumerate(union)}
    selected = [indexed_union[key] for key in context["row_ids"]]
    rows = [union[index] for index in selected]
    if any(row["dataset"] == context["outer_target"] for row in rows):
        raise ValueError("whole outer target leaked into fitted/prediction context")
    features = {name: value[selected] for name, value in all_features.items()}
    q = quality[selected]
    indexed = {identity(row): row for row in rows}
    positions = {identity(row): index for index, row in enumerate(rows)}
    local_config = {**inherited, "seed": context["seed"], "outer_target": context["outer_target"],
                    "source_domains": sorted({row["dataset"] for row in rows})}
    prompts = read(ROOT / "configs/prompts_core_v1.yaml")["classes"]
    clip = mean_cosine_logit(features["openclip"], text, len(prompts["live"]))
    gate_ids = [identity(row) for row in rows if row["role"] == "g_domain"]
    candidates = [identity(row) for row in rows if row["role"] != "g_domain"]
    binding = {"config_sha256": digest(CONFIG), "inputs_sha256": digest(OUTPUT / "inputs.json"),
               "outer_target": context["outer_target"], "seed": context["seed"],
               "extraction_sha256": digest(OUTPUT / "extraction.json")}
    records = {"domain_oof": [], "matched_sample_oof": [], "budget_domain_oof": [], "budget_matched_sample_oof": []}
    fitted_primary, predictions_primary, metas = {}, {}, []
    final, reference = None, None
    for split in context["partitions"]:
        guard()
        reuse, old_path = None, None
        if context["reuse297"]:
            old_path = old.OUTPUT / "fits" / f"{payload_digest({'name': split['name']})}.json"
            reuse = read(old_path)
        fitted, meta = fit_context(rows, features, clip, split, local_config, root / "fits", binding, guard, reuse)
        fitted_primary[split["name"]] = fitted
        predicted_ids = gate_ids if split["name"] == "final" else split["evaluation"]
        if old_path is not None:
            prediction_path = old_path.with_name(old_path.stem + "-predictions.json")
            predicted = read(prediction_path)["rows"]
            meta["original_model_sha256"] = digest(old_path)
            meta["original_predictions_sha256"] = digest(prediction_path)
        else:
            predicted = predict(rows, features, clip, q, predicted_ids, fitted, meta["sha256"])
        if [row["id"] for row in predicted] != predicted_ids:
            raise ValueError("source context exact prediction identities required")
        predictions_primary[split["name"]] = predicted
        seal(root / "predictions" / f"{payload_digest({'name': split['name']})}.json", {"rows": predicted, "model": meta})
        metas.append({"context": split["name"], **meta})
        if split["name"] == "final":
            final = predicted
            reference = predict(rows, features, clip, q, candidates, fitted, meta["sha256"])
        else:
            records[split["name"].split(":", 1)[0]].extend(predicted)
    if final is None or reference is None:
        raise ValueError("complete final-source predictions required")
    for split in context["budget_partitions"]:
        primary_split = next(value for value in context["partitions"] if value["name"] == split["name"])
        if split == primary_split:
            predicted = predictions_primary[split["name"]]
            meta = {"origin": "identical_primary_context_reuse", "fit": len(split["fitting"])}
        else:
            fitted, meta = fit_context(rows, features, clip, split, local_config, root / "budget-fits", binding, guard)
            predicted = predict(rows, features, clip, q, split["evaluation"], fitted, meta["sha256"])
        records["budget_" + split["name"].split(":", 1)[0]].extend(predicted)
        metas.append({"context": "budget_" + split["name"], **meta, "requested_fit_cap": context["budget_cap"]})
    for name, predicted in records.items():
        if len(predicted) != len(candidates) or {row["id"] for row in predicted} != set(candidates):
            raise ValueError("one-to-one identical OOF candidate coverage required for all controls")
        seal(root / f"{name}.json", {"rows": predicted})
    fitting_ids = context["partitions"][0]["fitting"]
    statistics = q[[positions[key] for key in fitting_ids]]
    mean, raw_scale = statistics.mean(axis=0), statistics.std(axis=0)
    scale = np.where(raw_scale == 0, 1.0, raw_scale)
    risks, public_risks = {}, []
    for strategy, predicted in records.items():
        variants = ["R_DVd", "R_DVd_noq"] if strategy.startswith("budget_") else inherited["risk"]["variants"] + config["no_quality_attribution"]
        for system in ("heterogeneous", "same_family"):
            for variant in variants:
                guard()
                reuse = None
                if context["reuse297"] and not strategy.startswith("budget_") and variant in inherited["risk"]["variants"]:
                    reuse = read(old.OUTPUT / "risks" / f"{strategy}-{system}-{variant}.json")
                model = risk_run(predicted, final, system, variant, mean, scale, root / "risks" / strategy,
                                 {**binding, "oof_sha256": digest(root / f"{strategy}.json")}, guard, reuse)
                risks[(strategy, system, variant)] = model
                public_risks.append({key: value for key, value in model.items()
                                     if key in {"status", "error_count", "correct_count", "origin", "system", "variant",
                                                "held_out_error_AP", "held_out_error_count", "held_out_brier", "held_out_nll"}}
                                    | {"strategy": strategy})
    seal(root / "risk_statistics.json", {
        "fitting_ids": fitting_ids, "quality_mean": mean.tolist(), "quality_scale": scale.tolist(),
        "constant_indices": np.flatnonzero(raw_scale == 0).tolist(),
        "statistics_convention": "shared_final_head_fitting_only_not_pseudo_domain_local"})
    finite_calibration = all(
        np.isfinite([calibration["theta"], calibration["slope"], calibration["intercept"]]).all()
        and calibration["slope"] > 0
        for fitted in fitted_primary.values() for calibration in fitted["calibrators"].values())
    competence_metrics = competence(records["domain_oof"], config["bootstrap"]["repetitions"],
                                    config["bootstrap"]["seed"], guard, finite_calibration=bool(finite_calibration))
    paired, attribution, audits = [], [], []
    for system in ("heterogeneous", "same_family"):
        for variant in ("R_DVd", "R_DVd_noq"):
            for prefix in ("", "budget_"):
                first = risks[(prefix + "domain_oof", system, variant)]
                second = risks[(prefix + "matched_sample_oof", system, variant)]
                if first["status"] != "fitted" or second["status"] != "fitted":
                    paired.append({"system": system, "variant": variant, "budget_matched": bool(prefix),
                                   "status": "not_applicable_insufficient_source_risk_events"})
                    continue
                compared = paired_ap(final, np.asarray([r["risk"] for r in first["predictions"]]),
                                     np.asarray([r["risk"] for r in second["predictions"]]), system,
                                     config["bootstrap"]["repetitions"], config["bootstrap"]["seed"], guard)
                paired.append({"system": system, "variant": variant, "budget_matched": bool(prefix), **compared})
        for strategy in ("domain_oof", "matched_sample_oof"):
            for contrast, first_variant, second_variant in (
                ("with_minus_without_quality", "R_DVd", "R_DVd_noq"),
                ("disagreement_without_quality", "R_DVd_noq", "R_DV_noq"),
            ):
                first = risks[(strategy, system, first_variant)]
                second = risks[(strategy, system, second_variant)]
                if first["status"] == second["status"] == "fitted":
                    compared = paired_ap(final, np.asarray([r["risk"] for r in first["predictions"]]),
                                         np.asarray([r["risk"] for r in second["predictions"]]), system,
                                         config["bootstrap"]["repetitions"], config["bootstrap"]["seed"], guard)
                else:
                    compared = {"status": "not_applicable_insufficient_source_risk_events"}
                attribution.append({"system": system, "strategy": strategy, "contrast": contrast, **compared})
            diagnostic = diagnostics(records[strategy], reference, indexed, system, mean, scale, context["seed"], guard)
            seal(root / "diagnostics" / f"{strategy}-{system}.json", diagnostic)
            audits.append({"system": system, "strategy": strategy, **diagnostic})
    errors = sum(row["errors"]["heterogeneous"] for row in records["domain_oof"])
    event_record = {"error_count": errors, "correct_count": len(candidates) - errors,
                    "pass": errors >= 20 and len(candidates) - errors >= 20}
    anchor = bool(competence_metrics["dino_reg"]["score_range"] > 1e-6)
    rq1 = competence_metrics["heterogeneous"]["pass"] and anchor and event_record["pass"]
    rq2 = competence_metrics["heterogeneous"]["pass"] and competence_metrics["same_family"]["pass"] and anchor
    source_events = {}
    for domain in sorted({row["dataset"] for row in rows}):
        domain_rows = [row for row in records["domain_oof"] if row["dataset"] == domain]
        count = sum(row["errors"]["heterogeneous"] for row in domain_rows)
        source_events[domain] = {"error_count": count, "correct_count": len(domain_rows) - count,
                                 "ap_estimable": 0 < count < len(domain_rows),
                                 "meets_n_error_min": 20 <= count < len(domain_rows)}
    result = {"key": context["key"], "outer_target": context["outer_target"], "seed": context["seed"],
              "source_domains": sorted({row["dataset"] for row in rows}), "source_use_binding": read(OUTPUT / "inputs.json")["source_use_binding"],
              "denominators": context["original_counts"], "oof_candidate_count": len(candidates), "g_domain_count": len(final),
              "contexts": [{key: value for key, value in meta.items() if key != "path"} for meta in metas],
              "risk_fits": public_risks, "paired_source_diagnostics": paired,
              "paired_no_quality_attribution": attribution,
              "audits": audits, "systems": competence_metrics, "dino_anchor_pass": anchor,
              "heterogeneous_risk_fit": event_record, "source_events": source_events,
              "claims": {"rq1_oof_transfer": "eligible" if rq1 else "not_applicable",
                         "rq2_complete_system": "eligible" if rq2 else "not_applicable"},
              "no_target_predictions": True, "reuse297_preserved": context["reuse297"]}
    seal(root / "result.json", result)
    print("SOURCE299_COMBINATION_COMPLETE", context["key"], result["claims"], flush=True)
    return result


def worker():
    config, plan, approval = authority()
    if os.getppid() != read(OUTPUT / "attempt_lock.json")["supervisor_pid"]:
        raise ValueError("original supervised299 worker required")
    enforce(approval)
    inputs = read(OUTPUT / "inputs.json")
    features, quality, extracted = extract(inputs["rows"], plan, approval)
    inherited = read(old.CONFIG)
    results = [combination(context, inputs["rows"], features, quality, extracted["text"], config, inherited, approval)
               for context in inputs["contexts"]]
    competent = {"version": 1, "no_target_selection_input": True, "records": [
        {key: result[key] for key in ("outer_target", "seed", "source_domains", "source_use_binding",
                                      "systems", "dino_anchor_pass", "heterogeneous_risk_fit")} for result in results]}
    applicable = {"version": 1, "no_target_selection_input": True, "n_error_min": 20,
                  "target_event_support": "not_inspected", "records": [
        {key: result[key] for key in ("outer_target", "seed", "source_domains", "source_use_binding", "claims", "source_events")}
        for result in results]}
    for name, value in (("competence.json", competent), ("applicability.json", applicable)):
        write_immutable_record(ROOT / "results/source-dry-run" / name, value)
    evidence = {"version": 1, "no_target_selection_input": True,
                "source_use_binding": inputs["source_use_binding"],
                "artifact_sha256": {f"results/source-dry-run/{name}": digest(ROOT / "results/source-dry-run" / name)
                                   for name in ("competence.json", "applicability.json")},
                "source_policy_path": SOURCE_POLICY_PATH, "source_policy_sha256": digest(ROOT / SOURCE_POLICY_PATH)}
    write_immutable_record(ROOT / "results/source-dry-run/evidence.json", evidence)
    stage_errors = {stage: validate_stage(ROOT, stage, frozen_root=old.integration.FROZEN, source_use_root=old.integration.USE)
                    for stage in ("schema", "data-audit", "source-dry-run")}
    if stage_errors["schema"] or stage_errors["data-audit"]:
        raise ValueError("accepted schema/data prerequisites changed")
    for name, expected in plan["summaries_sha256"].items():
        if digest(ROOT / name) != expected:
            raise ValueError("accepted summary changed")
    public = {"version": 1, "checkpoint": 299, "status": "complete_source_experiment_evidence_produced",
              "config_sha256": digest(CONFIG), "inputs_sha256": plan["inputs_sha256"],
              "source_manifest_sha256": config["source_manifest_sha256"],
              "extraction_sha256": digest(OUTPUT / "extraction.json"), "owner_approval_sha256": digest(OUTPUT / "owner_approval.json"),
              "feature_coverage": {name: {key: value for key, value in receipt.items()
                                        if key in {"checkpoint_sha256", "new_image_forwards", "reused297_rows", "shape",
                                                   "final_peak_allocated", "final_peak_reserved", "wall_seconds"}}
                                   for name, receipt in extracted["receipt"].items() if name in features},
              "combination_count": len(results), "combinations": results,
              "stage_errors": stage_errors, "source_dry_run_validator_passed": not stage_errors["source-dry-run"],
              "target_predictions": False, "target_tuning": False, "locked_evaluation_authorized": False,
              "gate_selected": False, "target_RQ1_RQ2_verdict": "not_evaluated",
              "analysis_freeze": "pending_clean_commit_and_existing_gate" if not stage_errors["source-dry-run"] else "blocked",
              "accepted_summaries_unchanged": True}
    write_immutable_record(OUTPUT / "worker_completion.json", public)


def supervise():
    config, plan, approval = authority()
    enforce(approval)
    write_immutable_record(OUTPUT / "attempt_lock.json", {"supervisor_pid": os.getpid(),
                                                        "plan_sha256": digest(OUTPUT / "execution_plan.json")})
    env = {**os.environ, "CUBLAS_WORKSPACE_CONFIG": ":4096:8", "HF_HUB_OFFLINE": "1",
           "OPENBLAS_NUM_THREADS": "2", "OMP_NUM_THREADS": "2", "MKL_NUM_THREADS": "2"}
    child = subprocess.Popen([sys.executable, str(Path(__file__)), "--worker"], start_new_session=True, env=env)
    failure, peak_rss, peak_size = None, 0, 0
    try:
        while child.poll() is None:
            enforce(approval)
            own_rss = next(int(line.split()[1]) * 1024
                           for line in Path(f"/proc/{os.getpid()}/status").read_text().splitlines()
                           if line.startswith("VmRSS:"))
            rss = old.pilot.group_rss(child.pid) + own_rss
            peak_rss, peak_size = max(peak_rss, rss), max(peak_size, owned_size())
            if peak_rss > config["limits"]["rss_bytes"] or peak_size > config["limits"]["output_bytes"]:
                raise MemoryError("combined299 RSS or owned new+temporary artifact cap")
            time.sleep(0.5)
        if child.returncode:
            raise RuntimeError(f"source299 worker exit{child.returncode}; no automatic retry")
        enforce(approval, final=True)
    except (OSError, ValueError, RuntimeError, TimeoutError, MemoryError) as exc:
        failure = f"{type(exc).__name__}: {exc}"
        print("SOURCE299_STOP", failure, file=sys.stderr, flush=True)
    finally:
        if child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
    terminal = {"status": "complete" if failure is None else "stopped_no_retry", "failure": failure,
                "wall_seconds_from_original_approval": time.time() - approval["started_unix_seconds"],
                "sampled_peak_combined_rss": peak_rss, "peak_owned_new_temporary_bytes": max(peak_size, owned_size()),
                "limits": config["limits"], "automatic_retry": False, "successful_shards_and_contexts_preserved": True,
                "worker_completion_sha256": digest(OUTPUT / "worker_completion.json") if failure is None else None}
    write_immutable_record(OUTPUT / "terminal.json", terminal)
    result = {**read(OUTPUT / "worker_completion.json"), "terminal": terminal} if failure is None else terminal
    write_immutable_record(ROOT / "results/phase1/source-run299-v1.json", result)
    print("SOURCE299_TERMINAL", terminal, flush=True)
    return int(failure is not None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--prepare", action="store_true")
    actions.add_argument("--worker", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        prepare()
    elif args.worker:
        worker()
    else:
        raise SystemExit(supervise())
