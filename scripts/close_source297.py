"""Additive saved-output verification; no encoder, optimization or target calls."""

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
from fas.source_fitting import calibrate, head_logits, identity, operating_threshold, risk_features, sigmoid
from fas.frozen_features import mean_cosine_logit
import run_source297 as run


def close() -> None:
    config, plan, approval = run.authority()
    run.enforce(approval, final=True)
    terminal = run.read(run.OUTPUT / "terminal.json")
    worker_path = run.OUTPUT / "worker_completion.json"
    if (terminal["status"] != "complete" or terminal["failure"] is not None
            or digest(worker_path) != terminal["worker_completion_sha256"]
            or terminal["sampled_peak_rss_bytes"] > config["limits"]["rss_bytes"]
            or terminal["peak_owned_new_temporary_bytes"] > config["limits"]["output_bytes"]):
        raise ValueError("successful exact authority/resource terminal required")
    worker = run.read(worker_path)
    if (worker["target_images_accessed"] or worker["target_predictions"]
            or worker["new_checkpoint_downloads"] or worker["new_text_forwards"]):
        raise ValueError("approved source-only model scope violated")
    inputs = run.read(run.OUTPUT / "inputs.json")
    rows, splits = inputs["rows"], inputs["partitions"]
    ids = [identity(row) for row in rows]
    index = {key: position for position, key in enumerate(ids)}
    if len(index) != 1906 or any(row["dataset"] == "OULU-NPU" for row in rows):
        raise ValueError("exact target-free successful source coverage required")
    features = {}
    extracted = run.read(run.OUTPUT / "extraction.json")
    if digest(run.OUTPUT / "extraction.json") != worker["extraction_sha256"]:
        raise ValueError("executed extraction receipt drift")
    pilot_config = run.read(run.pilot.CONFIG)
    for name in ("dino_reg", "dino_plain", "openclip"):
        model = extracted[name]
        keys = [cache_key(run.base_key(row, name, pilot_config, model["checkpoint_sha256"]), model["contract"])
                for row in rows]
        if model["ids"] != ids or keys != model["feature_keys"]:
            raise ValueError("saved complete feature/identity/runtime-contract join drift")
        if model["new_image_forwards"] != 1882 or model["reused295_rows"] != 24:
            raise ValueError("exact non-repeated newly extracted/pilot reuse accounting required")
        if max(model["final_max_allocated_bytes"], model["final_max_reserved_bytes"]) > config["limits"]["cuda_bytes"]:
            raise ValueError("final allocator peak cap exceeded")
        features[name] = run.load_features(extracted, name)
    text_path = Path(extracted["text"]["path"])
    if digest(text_path) != extracted["text"]["sha256"]:
        raise ValueError("saved fixed prompt text drift")
    prompts = run.read(ROOT / "configs/prompts_core_v1.yaml")["classes"]
    clip_logits = mean_cosine_logit(features["openclip"], np.load(text_path, allow_pickle=False), len(prompts["live"]))
    quality_receipt = run.read(run.OUTPUT / "quality.json")
    if digest(run.OUTPUT / "quality.json") != worker["quality_sha256"]:
        raise ValueError("saved quality receipt drift")
    quality_parts, offset = [], 0
    for shard in quality_receipt["shards"]:
        path = Path(shard["path"])
        if digest(path) != shard["sha256"]:
            raise ValueError("saved quality shard drift")
        quality_parts.append(load_shard(path, quality_receipt["keys"][offset:offset + shard["count"]], 5))
        offset += shard["count"]
    quality = np.concatenate(quality_parts).astype(np.float64)
    if quality.shape != (1906, 5):
        raise ValueError("complete saved quality coverage required")
    reconstructed, final_rows = {"domain_oof": [], "matched_sample_oof": []}, None
    reconstructed_count = 0
    for split in splits:
        run.enforce(approval, final=True)
        path = run.OUTPUT / "fits" / f"{payload_digest({'name': split['name']})}.json"
        fitted = run.read(path)
        if fitted["split"] != split or fitted["binding"]["split_sha256"] != payload_digest(split):
            raise ValueError("saved model/frozen group split drift")
        for head in fitted["heads"].values():
            losses = head["validation_history"]
            if (head["selected_epoch"] != int(np.argmin(losses)) + 1
                    or head["validation_bce"] != min(losses) or len(losses) != 200):
                raise ValueError("saved head is not the earliest minimum validation BCE checkpoint")
        logits = {name: head_logits(fitted["heads"][name], features[name]) for name in ("dino_reg", "dino_plain")}
        logits["openclip"] = clip_logits
        calibration = np.asarray([index[key] for key in split["calibration"]])
        calibration_rows = [rows[position] for position in calibration]
        calibration_p = {name: calibrate(fitted["calibrators"][name], values[calibration])
                         for name, values in logits.items()}
        calibration_scores = {
            "dino_reg": calibration_p["dino_reg"], "openclip": calibration_p["openclip"],
            "heterogeneous": (calibration_p["dino_reg"] + calibration_p["openclip"]) / 2,
            "same_family": (calibration_p["dino_reg"] + calibration_p["dino_plain"]) / 2}
        for name, scores in calibration_scores.items():
            policy = operating_threshold(scores, calibration_rows, alpha=0.05)
            if policy != fitted["policies"][name]:
                raise ValueError("saved reference threshold does not reconstruct from allowed calibration remainder")
        prediction_path = path.with_name(path.stem + "-predictions.json")
        saved = run.read(prediction_path)
        if saved["fit_sha256"] != digest(path):
            raise ValueError("saved prediction/model byte binding drift")
        predicted_rows = saved["rows"]
        expected = ([identity(row) for row in rows if row["role"] == "g_domain"]
                    if split["name"] == "final" else split["evaluation"])
        if [row["id"] for row in predicted_rows] != expected:
            raise ValueError("saved source OOF/G_domain exact ordered join drift")
        predicted_indices = np.asarray([index[key] for key in expected])
        p = {name: calibrate(fitted["calibrators"][name], values[predicted_indices]) for name, values in logits.items()}
        for local, record in enumerate(predicted_rows):
            original = rows[index[record["id"]]]
            if (record["label"] != int(original["binary_label"] == "attack")
                    or record["role"] != original["role"]
                    or record["quality"] != quality[index[record["id"]]].tolist()):
                raise ValueError("saved prediction label/role/quality provenance drift")
            for name, values in p.items():
                if not np.isclose(record["probabilities"][name], values[local], rtol=1e-12, atol=1e-12):
                    raise ValueError("saved fitted branch probability does not reconstruct")
            branch = record["probabilities"]
            scores = {"dino_reg": branch["dino_reg"], "openclip": branch["openclip"],
                      "heterogeneous": (branch["dino_reg"] + branch["openclip"]) / 2,
                      "same_family": (branch["dino_reg"] + branch["dino_plain"]) / 2}
            for name, score in scores.items():
                threshold = fitted["policies"][name]["threshold"]
                if (score != record["scores"][name] or threshold != record["thresholds"][name]
                        or int((score >= threshold) != bool(record["label"])) != record["errors"][name]):
                    raise ValueError("saved complete-system score/threshold/genuine error label mismatch")
        reconstructed_count += len(predicted_rows)
        if split["name"] == "final":
            final_rows = predicted_rows
        else:
            reconstructed[split["name"].split(":", 1)[0]].extend(predicted_rows)
    if final_rows is None:
        raise ValueError("saved final source predictions absent")
    for strategy, predictions in reconstructed.items():
        saved = run.read(run.OUTPUT / f"{strategy}-predictions.json")["rows"]
        if saved != predictions or len(predictions) != 1524 or len({row["id"] for row in predictions}) != 1524:
            raise ValueError("saved OOF coverage/binding mismatch")
    final_split = next(split for split in splits if split["name"] == "final")
    statistics = quality[np.asarray([index[key] for key in final_split["fitting"]])]
    mean, raw_std = statistics.mean(axis=0), statistics.std(axis=0)
    scale = np.where(raw_std == 0, 1.0, raw_std)
    risk_count = 0
    fitting = run.read(run.OUTPUT / "fitting.json")
    if digest(run.OUTPUT / "fitting.json") != worker["fitting_sha256"]:
        raise ValueError("fitting summary drift")
    for result in fitting["risk_results"]:
        if result["status"] != "fitted":
            continue
        strategy, system, variant = result["strategy"], result["system"], result["variant"]
        path = run.OUTPUT / "risks" / f"{strategy}-{system}-{variant}.json"
        model = run.read(path)
        if (digest(path) != result["model_sha256"] or model["statistics_ids"] != final_split["fitting"]
                or model["quality_mean"] != mean.tolist() or model["quality_scale"] != scale.tolist()
                or model["oof_predictions_sha256"] != digest(run.OUTPUT / f"{strategy}-predictions.json")):
            raise ValueError("risk model/OOF/quality-statistics saved provenance drift")
        other = "openclip" if system == "heterogeneous" else "dino_plain"
        design = np.concatenate([
            risk_features(np.asarray([[record["probabilities"]["dino_reg"], record["probabilities"][other]]]),
                          ((np.asarray(record["quality"]) - mean) / scale)[None],
                          record["thresholds"][system], variant)
            for record in final_rows])
        probabilities = sigmoid(head_logits(model["model"], design))
        if [row["id"] for row in model["g_domain_predictions"]] != [row["id"] for row in final_rows]:
            raise ValueError("risk G_domain sample join drift")
        if not np.allclose([row["risk"] for row in model["g_domain_predictions"]], probabilities, rtol=1e-12, atol=1e-12):
            raise ValueError("saved risk predictions do not reconstruct from fitted model")
        risk_count += 1
    run.enforce(approval, final=True)
    closure = {
        "version": 1, "checkpoint": 297, "status": "saved_source_feature_model_oof_and_risk_readback_verified",
        "terminal_sha256": digest(run.OUTPUT / "terminal.json"), "worker_sha256": digest(worker_path),
        "closure_script_sha256": digest(Path(__file__)), "feature_rows_per_model": 1906,
        "new_image_forwards": 5646, "reused295_feature_rows": 72,
        "head_checkpoints_verified": 14, "calibrators_and_threshold_policies_verified": 21,
        "reconstructed_source_prediction_rows": reconstructed_count,
        "oof_rows_per_strategy": 1524, "g_domain_predictions": 382,
        "risk_models_and_saved_predictions_verified": risk_count,
        "new_encoder_calls": 0, "new_optimization_calls": 0, "target_image_access": False,
        "scientific_source_dry_run_complete": False, "scientific_readiness": False,
        "wall_seconds_from_original_approval": time.time() - approval["started_unix_seconds"],
        "stage_errors": worker["stage_errors"],
        "remaining_components": fitting["remaining"],
    }
    write_immutable_record(run.OUTPUT / "closure.json", closure)
    write_immutable_record(ROOT / "results/phase1/source-closure297-v1.json", closure)
    print(json.dumps(closure, indent=2))


if __name__ == "__main__":
    close()
