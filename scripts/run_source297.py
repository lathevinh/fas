"""Bounded resumable source caching and genuine first-fold source fitting/OOF."""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from fas.environment import inspect_environment, verify_source_checkout
from fas.feature_cache import cache_key, digest, load_shard, payload_digest, save_shard
from fas.freeze import write_immutable_record
from fas.frozen_features import check_feature, dino_pool, feature_key, mean_cosine_logit, normalize_rgb
from fas.source_fitting import (
    calibrate, fit_calibrator, fit_head, fit_risk, head_logits, identity, partitions,
    operating_threshold, quality_vector, risk_features, sigmoid,
)
from fas.source_stage import population_counts, require_source_input
from fas.preregistration import validate_stage
import integrate_source295 as integration
import pilot_source295 as pilot

CONFIG = ROOT / "configs/source_run297_v1.yaml"
OUTPUT = Path("/mnt/e/FAS-private/artifacts/phase1/source_run297_v1")
CACHE = Path.home() / ".cache/fas/source-run297-v1"
CODE = ("scripts/run_source297.py", "src/fas/source_fitting.py", "src/fas/feature_cache.py",
        "src/fas/frozen_features.py", "src/fas/source_stage.py", "scripts/pilot_source295.py",
        "configs/source_recipe_v2.yaml", "configs/experiment_core_v1.yaml", "configs/prompts_core_v1.yaml",
        "configs/preprocessing_v3.yaml", "configs/source_pilot295_v1.yaml", "configs/seeds_v1.yaml",
        "configs/siwmv2_source_use_v1.yaml", "configs/claims_v1.yaml")


def seal(path: Path, record: dict) -> None:
    if path.exists():
        if read(path) != record:
            raise ValueError(f"immutable stage checkpoint differs: {path.name}")
    else:
        write_immutable_record(path, record)


def read(path: Path) -> dict:
    return json.loads(path.read_bytes())


def runtime() -> dict:
    import torch
    versions = {name: importlib.metadata.version(name) for name in (
        "numpy", "scipy", "scikit-learn", "torch", "open_clip_torch", "opencv-python-headless", "Pillow")}
    return {"python": sys.version, "versions": versions, "torch_cuda": torch.version.cuda,
            "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "precision": "float32", "batch_size": 1, "tf32": False,
            "deterministic_algorithms": True, "CUBLAS_WORKSPACE_CONFIG": ":4096:8"}


def source_rows(config: dict) -> tuple[list[dict], dict]:
    path = pilot.INTEGRATION / "source_manifest.json"
    if digest(path) != config["source_manifest_sha256"]:
        raise ValueError("accepted sealed integrated source manifest drift")
    manifest = read(path)
    for path_string, expected in manifest["input_sha256"].items():
        path = Path(path_string)
        if path.is_relative_to(ROOT) and digest(path) != expected:
            raise ValueError(f"accepted integration implementation/config drift: {path.name}")
    accepted = read(ROOT / "results/phase1/source-integration295-v1.json")
    if manifest["source_use_binding"] != accepted["source_use_binding"]:
        raise ValueError("exact accepted SiW adopted binding required")
    rows = sorted((row for row in manifest["rows"]
                   if row["dataset"] != config["outer_target"] and row["source_use_eligible"]),
                  key=identity)
    for row in rows:
        purpose = {"train": "fitting", "branch_calibration": "calibration", "g_domain": "domain_use"}[row["role"]]
        require_source_input(row, outer_target=config["outer_target"], purpose=purpose)
    counts = population_counts(rows)
    if (counts["source_use"] != config["source_use_denominator"]
            or counts["model_input"] != config["successful_inputs"]
            or counts["source_use_failures"] != config["source_failures"]):
        raise ValueError("exact first-fold source/failure population required")
    return rows, counts


def prepare() -> None:
    config = read(CONFIG)
    rows, counts = source_rows(config)
    successful = [row for row in rows if row["model_input_eligible"]]
    splits = partitions(successful, config["outer_target"], config["seed"])
    gate = [row for row in successful if row["role"] == "g_domain"]
    nongate = [row for row in successful if row["role"] != "g_domain"]
    if ({(row["dataset"], row["group_id"]) for row in gate}
            & {(row["dataset"], row["group_id"]) for row in nongate}
            or {(row["dataset"], row["selected_frame"]["rgb_sha256"]) for row in gate}
            & {(row["dataset"], row["selected_frame"]["rgb_sha256"]) for row in nongate}):
        raise ValueError("permanent G_domain must not cross source fitting groups/content")
    if inspect_environment(ROOT, read(ROOT / "configs/environment_v1.yaml"))["status"] != "ready":
        raise RuntimeError("locked source runtime not ready")
    verify_source_checkout(pilot.UPSTREAM, read(pilot.CONFIG)["dinov2_source_commit"])
    prior = read(ROOT / "results/phase1/source-encoder-pilot295-v1.json")
    for name, spec in prior["acquisitions"].items():
        if digest(pilot.NATIVE / "checkpoints" / f"{name}.pth") != spec["sha256"]:
            raise ValueError("exact already acquired checkpoint required; no download")
    sampled = successful[::max(1, len(successful) // 24)][:24]
    started, byte_count = time.monotonic(), 0
    for row in sampled:
        for crop in row["crops"].values():
            payload = Path(crop["path"]).read_bytes()
            if hashlib.sha256(payload).hexdigest() != crop["sha256"]:
                raise ValueError("preflight crop SHA drift")
            byte_count += len(payload)
    io_seconds = time.monotonic() - started
    inputs = {"version": 1, "source_manifest_sha256": config["source_manifest_sha256"],
              "source_use_binding": read(pilot.INTEGRATION / "source_manifest.json")["source_use_binding"],
              "rows": successful, "failure_rows": [row for row in rows if not row["model_input_eligible"]],
              "partitions": splits}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    write_immutable_record(OUTPUT / "inputs.json", inputs)
    plan = {
        "version": 1, "checkpoint": 297, "config_sha256": digest(CONFIG),
        "inputs_sha256": digest(OUTPUT / "inputs.json"), "runtime": runtime(),
        "implementation_sha256": {name: digest(ROOT / name) for name in CODE},
        "accepted_summary_sha256": {name: digest(ROOT / name) for name in (
            "manifests/dataset_summary.csv", "manifests/split_summary.csv")},
        "counts": counts, "source_domains": config["source_domains"], "outer_target": config["outer_target"],
        "seed": config["seed"], "source_use_denominator": len(rows), "successful_inputs": len(successful),
        "failure_denominator": config["source_failures"], "folds": len(splits),
        "head_fits": 2 * len(splits), "calibrator_fits": 3 * len(splits),
        "maximum_risk_fits": 24, "gate_successes": len(gate), "oof_candidate_successes": len(nongate),
        "checkpoint_reuse_bytes": sum(value["bytes"] for value in prior["acquisitions"].values()),
        "new_checkpoint_downloads": 0, "max_new_image_forwards": (len(successful) - 24) * 3,
        "new_text_forwards": 0, "feature_payload_bytes": len(successful) * (1536 + 1536 + 512) * 4,
        "io_sample": {"count": len(sampled), "crop_reads": len(sampled) * 2, "bytes": byte_count,
                      "wall_seconds": io_seconds, "sample_method": "24_evenly_spaced_identity_sorted_source_rows",
                      "no_pixel_decode_or_model_forward": True,
                      "linear_three_encoder_plus_quality_read_projection_seconds":
                          io_seconds / len(sampled) * len(successful) * 2,
                      "projection_is_wall_guarantee": False},
        "limits": config["limits"], "scientific_readiness": False,
    }
    write_immutable_record(OUTPUT / "execution_plan.json", plan)
    write_immutable_record(ROOT / "results/phase1/source-plan297-v1.json", {
        **plan, "private_inputs_published": False,
        "execution_plan_sha256": digest(OUTPUT / "execution_plan.json")})
    print(json.dumps(plan, indent=2), flush=True)


def authority() -> tuple[dict, dict, dict]:
    config, plan, approval = read(CONFIG), read(OUTPUT / "execution_plan.json"), read(OUTPUT / "owner_approval.json")
    if (approval["explicit_owner_approval"] is not True
            or approval["selected_answer"] != "approve_source297_full_features_and_source_fitting"
            or approval["execution_plan_sha256"] != digest(OUTPUT / "execution_plan.json")
            or approval["config_sha256"] != digest(CONFIG) or plan["config_sha256"] != digest(CONFIG)
            or approval["limits"] != config["limits"]
            or approval["deadline_unix_seconds"] != approval["started_unix_seconds"] + config["limits"]["wall_seconds"]
            or approval["work_deadline_unix_seconds"] != approval["started_unix_seconds"] + config["limits"]["work_seconds"]
            or approval["automatic_retry"] is not False):
        raise ValueError("fresh exact combined source297 authority and original caps required")
    for name, expected in plan["implementation_sha256"].items():
        if digest(ROOT / name) != expected:
            raise ValueError(f"approved executed implementation drift: {name}")
    if digest(OUTPUT / "inputs.json") != plan["inputs_sha256"]:
        raise ValueError("approved exact fold-local inputs/partitions changed")
    return config, plan, approval


def owned_size() -> int:
    return sum(path.stat().st_size for root in (CACHE, OUTPUT) if root.exists()
               for path in root.rglob("*") if path.is_file())


def enforce(approval: dict, *, final: bool = False) -> None:
    deadline = "deadline_unix_seconds" if final else "work_deadline_unix_seconds"
    if time.time() >= approval[deadline]:
        raise TimeoutError("original source297 authority deadline")
    if owned_size() > approval["limits"]["output_bytes"]:
        raise MemoryError("source297 owned new+temporary artifact cap")


def bound_rgb(row: dict, resolution: int):
    import numpy as np
    from PIL import Image
    crop = row["crops"][str(resolution)]
    payload = Path(crop["path"]).read_bytes()
    if hashlib.sha256(payload).hexdigest() != crop["sha256"]:
        raise ValueError("prepared source crop SHA changed")
    with Image.open(io.BytesIO(payload)) as image:
        if image.mode != "RGB" or image.size != (resolution, resolution):
            raise ValueError("exact prepared RGB native dimensions required")
        return np.asarray(image).copy()


def base_key(row: dict, name: str, pilot_config: dict, checkpoint_sha: str) -> str:
    spec = pilot_config["models"][name]
    return feature_key(dataset=row["dataset"], video_id=row["video_id"],
                       crop_sha256=row["crops"][str(spec["resolution"])]["sha256"],
                       checkpoint_sha256=checkpoint_sha,
                       preprocessing_sha256=pilot_config["preprocessing_sha256"],
                       representation=spec.get("representation", "normalized_image_embedding"))


def pilot_reuse(name: str, pilot_config: dict):
    import numpy as np
    public = read(ROOT / "results/phase1/source-encoder-pilot295-v1.json")
    if (digest(pilot.CONFIG) != read(CONFIG)["pilot_config_sha256"]
            or digest(pilot.NATIVE / "worker_completion.json") != public["worker_completion_sha256"]):
        raise ValueError("accepted295 worker/config pin required for compatible reuse")
    worker = read(pilot.NATIVE / "worker_completion.json")
    model = worker["models"][name]
    if digest(pilot.NATIVE / f"{name}-features.npy") != model["shard_sha256"]:
        raise ValueError("accepted295 feature bytes drift")
    features = np.load(pilot.NATIVE / f"{name}-features.npy", allow_pickle=False)
    check_feature(features, 24, pilot_config["models"][name]["feature_dimension"])
    inputs = pilot.INTEGRATION / "pilot_inputs.json"
    if digest(inputs) != pilot_config["pilot_inputs_sha256"]:
        raise ValueError("accepted295 sample join drift")
    keys = [base_key(row, name, pilot_config, model["checkpoint_sha256"]) for row in read(inputs)["rows"]]
    if keys != model["feature_keys"] or len(set(keys)) != 24:
        raise ValueError("accepted295 exact unique crop/feature keys required")
    return dict(zip(keys, features, strict=True)), model


def extraction(rows: list[dict], config: dict, plan: dict, approval: dict) -> dict:
    import numpy as np
    import torch
    import open_clip

    if runtime() != plan["runtime"]:
        raise ValueError("approved exact numerical runtime changed")
    completed = OUTPUT / "extraction.json"
    if completed.exists():
        saved = read(completed)
        for name in ("dino_reg", "dino_plain", "openclip"):
            if saved[name]["ids"] != [identity(row) for row in rows]:
                raise ValueError("completed extraction sample coverage changed")
            load_features(saved, name)
        if digest(Path(saved["text"]["path"])) != saved["text"]["sha256"]:
            raise ValueError("completed extraction fixed text drift")
        return saved
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA required for encoders; no CPU fallback")
    verify_source_checkout(pilot.UPSTREAM, read(pilot.CONFIG)["dinov2_source_commit"])
    torch.set_num_threads(2)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(config["seed"])
    torch.cuda.set_per_process_memory_fraction(
        approval["limits"]["cuda_bytes"] / torch.cuda.get_device_properties(0).total_memory)
    sys.path.insert(0, str(pilot.UPSTREAM))
    from dinov2.hub import backbones

    pilot_config = read(pilot.CONFIG)
    checkpoint_specs = read(ROOT / "results/phase1/source-encoder-pilot295-v1.json")["acquisitions"]
    results = {}
    for name, spec in pilot_config["models"].items():
        enforce(approval)
        started = time.monotonic()
        checkpoint_sha = checkpoint_specs[name]["sha256"]
        checkpoint = pilot.NATIVE / "checkpoints" / f"{name}.pth"
        if digest(checkpoint) != checkpoint_sha:
            raise ValueError("exact cached checkpoint drift; never redownload")
        reused, prior = pilot_reuse(name, pilot_config)
        mean, std = tuple(prior["normalization_mean"]), tuple(prior["normalization_std"])
        if name.startswith("dino"):
            if (mean, std) != ((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)):
                raise ValueError("native DINO normalization drift")
        else:
            native = open_clip.get_pretrained_cfg("ViT-B-16", "laion2b_s34b_b88k")
            if mean != tuple(native["mean"]) or std != tuple(native["std"]):
                raise ValueError("native OpenCLIP normalization drift")
        contract = {
            "runtime": plan["runtime"], "normalization_mean": mean, "normalization_std": std,
            "resolution": spec["resolution"], "pooling": spec.get("representation", "normalized_image_embedding"),
            "feature_contract_sha256": digest(ROOT / "src/fas/frozen_features.py"),
            "controller_sha256": digest(Path(__file__)),
            "upstream_commit": pilot_config["dinov2_source_commit"] if name.startswith("dino") else None,
            "pilot_compatibility_adapter": {"config_sha256": digest(pilot.CONFIG),
                                           "worker_sha256": digest(pilot.NATIVE / "worker_completion.json"),
                                           "original_controller_sha256": digest(ROOT / "scripts/pilot_source295.py")},
        }
        keys = [cache_key(base_key(row, name, pilot_config, checkpoint_sha), contract) for row in rows]
        if len(set(keys)) != len(rows):
            raise ValueError("one-to-one full extraction keys required")
        model, parts, shards = None, [], []
        calls, reused_count, existing_count = 0, 0, 0
        torch.cuda.reset_peak_memory_stats()
        for start in range(0, len(rows), config["shard_size"]):
            enforce(approval)
            selected = rows[start:start + config["shard_size"]]
            shard_keys = keys[start:start + len(selected)]
            path = CACHE / name / f"{start:06d}.npz"
            receipt_path = path.with_suffix(".json")
            if path.exists():
                if receipt_path.exists() and digest(path) != read(receipt_path)["sha256"]:
                    raise ValueError("committed source feature shard hash drift")
                values = load_shard(path, shard_keys, spec["feature_dimension"])
                existing_count += len(selected)
            else:
                values_list = []
                for row in selected:
                    enforce(approval)
                    key = base_key(row, name, pilot_config, checkpoint_sha)
                    if key in reused:
                        values_list.append(reused[key][None, :])
                        reused_count += 1
                        continue
                    if model is None:
                        if name.startswith("dino"):
                            model = getattr(backbones, spec["local_factory"])(pretrained=False)
                            model.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True), strict=True)
                        else:
                            model = open_clip.create_model("ViT-B-16", pretrained=None, precision="fp32")
                            incompatible = open_clip.load_checkpoint(model, str(checkpoint), strict=True, weights_only=True)
                            if incompatible.missing_keys or incompatible.unexpected_keys:
                                raise ValueError("strict local OpenCLIP checkpoint mismatch")
                        model.requires_grad_(False).eval().cuda()
                    rgb = bound_rgb(row, spec["resolution"])
                    tensor = torch.from_numpy(normalize_rgb(rgb, spec["resolution"], mean, std)[None]).cuda()
                    with torch.inference_mode():
                        if name.startswith("dino"):
                            output = model.forward_features(tensor)
                            feature = dino_pool(output["x_norm_clstoken"].cpu().numpy(),
                                                output["x_norm_patchtokens"].cpu().numpy())
                            del output
                        else:
                            feature = model.encode_image(tensor, normalize=True).cpu().numpy()
                    del tensor
                    check_feature(feature, 1, spec["feature_dimension"])
                    values_list.append(feature)
                    calls += 1
                    if max(torch.cuda.max_memory_allocated(), torch.cuda.max_memory_reserved()) > approval["limits"]["cuda_bytes"]:
                        raise MemoryError("source297 CUDA allocated/reserved cap")
                values = np.concatenate(values_list)
                save_shard(path, shard_keys, values)
            if not receipt_path.exists():
                write_immutable_record(receipt_path, {
                    "sha256": digest(path), "keys_sha256": payload_digest({"keys": shard_keys}),
                    "shape": list(values.shape), "contract_sha256": payload_digest(contract),
                    "recovered_after_atomic_commit": path.exists() and existing_count > 0})
            parts.append(values)
            shards.append({"path": str(path), "sha256": digest(path), "count": len(selected)})
            print("SOURCE297_EXTRACTION", name, start + len(selected), len(rows), "forwards", calls, flush=True)
        complete = np.concatenate(parts)
        check_feature(complete, len(rows), spec["feature_dimension"])
        results[name] = {
            "count": len(rows), "shape": list(complete.shape), "shards": shards,
            "checkpoint_sha256": checkpoint_sha, "contract": contract,
            "feature_keys": keys, "ids": [identity(row) for row in rows],
            "new_image_forwards": calls, "reused295_rows": reused_count, "existing297_rows": existing_count,
            "wall_seconds": time.monotonic() - started,
            "final_max_allocated_bytes": torch.cuda.max_memory_allocated(),
            "final_max_reserved_bytes": torch.cuda.max_memory_reserved(),
            "text_work": "none_reuse_hash_bound295_text",
        }
        if model is not None:
            del model
        gc.collect()
        torch.cuda.empty_cache()
    text_path = pilot.NATIVE / "openclip-text.npy"
    prior_clip = read(pilot.NATIVE / "worker_completion.json")["models"]["openclip"]
    if (digest(text_path) != prior_clip["text_sha256"]
            or digest(ROOT / "configs/prompts_core_v1.yaml") != prior_clip["prompts_sha256"]):
        raise ValueError("fixed accepted prompt/text artifact drift")
    results["text"] = {"path": str(text_path), "sha256": digest(text_path), "new_text_forwards": 0,
                       "prompts_sha256": prior_clip["prompts_sha256"]}
    write_immutable_record(OUTPUT / "extraction.json", results)
    return results


def quality_cache(rows: list[dict], approval: dict):
    import numpy as np
    keys = [payload_digest({"crop_sha256": row["crops"]["224"]["sha256"],
                            "record_sha256": row["record_sha256"],
                            "code_sha256": digest(ROOT / "src/fas/source_fitting.py"),
                            "identity": identity(row)}) for row in rows]
    completed = OUTPUT / "quality.json"
    if completed.exists():
        saved = read(completed)
        if saved["keys"] != keys:
            raise ValueError("completed quality/cache sample join drift")
        parts, offset = [], 0
        for shard in saved["shards"]:
            if digest(Path(shard["path"])) != shard["sha256"]:
                raise ValueError("completed quality shard drift")
            parts.append(load_shard(Path(shard["path"]), keys[offset:offset + shard["count"]], 5))
            offset += shard["count"]
        if offset != len(rows):
            raise ValueError("completed quality coverage gap")
        return np.concatenate(parts).astype(np.float64)
    parts, receipts = [], []
    for start in range(0, len(rows), 32):
        enforce(approval)
        path = CACHE / "quality" / f"{start:06d}.npz"
        selected = rows[start:start + 32]
        selected_keys = keys[start:start + len(selected)]
        if path.exists():
            values = load_shard(path, selected_keys, 5)
        else:
            values_list = []
            for row in selected:
                enforce(approval)
                transaction_path = Path(row["record_path"])
                if digest(transaction_path) != row["record_sha256"]:
                    raise ValueError("saved quality detector transaction drift")
                transaction = read(transaction_path)
                if (transaction["video_id"] != row["video_id"] or transaction["selected_frame"] != row["selected_frame"]
                        or transaction["detector_status"] != "success"):
                    raise ValueError("saved quality identity/frame/detector join drift")
                values_list.append(quality_vector(bound_rgb(row, 224), transaction))
            values = np.asarray(values_list, dtype=np.float32)
            save_shard(path, selected_keys, values)
        parts.append(values)
        receipts.append({"path": str(path), "sha256": digest(path), "count": len(selected)})
    write_immutable_record(OUTPUT / "quality.json", {"shards": receipts, "shape": [len(rows), 5], "keys": keys})
    return np.concatenate(parts).astype(np.float64)


def load_features(extracted: dict, name: str):
    import numpy as np
    model, parts, offset = extracted[name], [], 0
    for shard in model["shards"]:
        path = Path(shard["path"])
        if digest(path) != shard["sha256"]:
            raise ValueError("feature shard SHA drift before fit")
        keys = model["feature_keys"][offset:offset + shard["count"]]
        parts.append(load_shard(path, keys, model["shape"][1]))
        offset += shard["count"]
    result = np.concatenate(parts)
    check_feature(result, model["count"], model["shape"][1])
    if offset != model["count"]:
        raise ValueError("feature coverage gap")
    return result


def source_fit(inputs: dict, extracted: dict, quality, config: dict, approval: dict) -> dict:
    import numpy as np
    from sklearn.metrics import roc_auc_score, balanced_accuracy_score, average_precision_score

    rows = inputs["rows"]
    indexed = {identity(row): index for index, row in enumerate(rows)}
    guard = lambda: enforce(approval)
    features = {name: load_features(extracted, name) for name in ("dino_reg", "dino_plain", "openclip")}
    text = np.load(extracted["text"]["path"], allow_pickle=False)
    prompts = read(ROOT / "configs/prompts_core_v1.yaml")["classes"]
    fixed_clip_logits = mean_cosine_logit(features["openclip"], text, len(prompts["live"]))
    labels = np.array([row["binary_label"] == "attack" for row in rows], dtype=np.float64)
    summaries, records, final = [], {"domain_oof": [], "matched_sample_oof": []}, None
    gate_ids = [identity(row) for row in rows if row["role"] == "g_domain"]

    def positions(ids):
        return np.array([indexed[value] for value in ids], dtype=np.int64)

    def domains(indices):
        return [rows[index]["dataset"] for index in indices]

    for split in inputs["partitions"]:
        guard()
        fit, validation, calibration = (positions(split[key]) for key in ("fitting", "validation", "calibration"))
        predicted_ids = gate_ids if split["name"] == "final" else split["evaluation"]
        predicted = positions(predicted_ids)
        model_path = OUTPUT / "fits" / f"{payload_digest({'name': split['name']})}.json"
        model_binding = {"split_sha256": payload_digest(split), "config_sha256": digest(CONFIG),
                         "extraction_sha256": digest(OUTPUT / "extraction.json"),
                         "inputs_sha256": digest(OUTPUT / "inputs.json")}
        if model_path.exists():
            fitted = read(model_path)
            if fitted["binding"] != model_binding:
                raise ValueError("completed fit provenance differs; never silently retrain")
        else:
            heads, calibrators, all_logits = {}, {}, {"openclip": fixed_clip_logits}
            for name in ("dino_reg", "dino_plain"):
                heads[name] = fit_head(
                    features[name][fit], labels[fit], domains(fit), features[name][validation],
                    labels[validation], domains(validation), seed=config["seed"], settings=config["head"], guard=guard)
                all_logits[name] = head_logits(heads[name], features[name])
            for name in ("dino_reg", "dino_plain", "openclip"):
                calibrators[name] = fit_calibrator(all_logits[name][calibration], labels[calibration], domains(calibration), guard)
            probabilities = {name: calibrate(calibrators[name], all_logits[name][calibration]) for name in all_logits}
            systems = {"dino_reg": probabilities["dino_reg"], "openclip": probabilities["openclip"],
                       "heterogeneous": (probabilities["dino_reg"] + probabilities["openclip"]) / 2,
                       "same_family": (probabilities["dino_reg"] + probabilities["dino_plain"]) / 2}
            thresholds = {name: operating_threshold(
                values, [rows[index] for index in calibration], alpha=config["reference_policy"]["alpha"])
                          for name, values in systems.items()}
            fitted = {"binding": model_binding, "split": split, "heads": heads, "calibrators": calibrators,
                      "policies": thresholds, "target_images_accessed": False}
            write_immutable_record(model_path, fitted)
        all_logits = {name: head_logits(fitted["heads"][name], features[name][predicted])
                      for name in ("dino_reg", "dino_plain")}
        all_logits["openclip"] = fixed_clip_logits[predicted]
        p = {name: calibrate(fitted["calibrators"][name], values) for name, values in all_logits.items()}
        prediction_rows = []
        for local, index in enumerate(predicted):
            values = {name: float(array[local]) for name, array in p.items()}
            system_scores = {"dino_reg": values["dino_reg"], "openclip": values["openclip"],
                             "heterogeneous": (values["dino_reg"] + values["openclip"]) / 2,
                             "same_family": (values["dino_reg"] + values["dino_plain"]) / 2}
            prediction_rows.append({
                "id": identity(rows[index]), "dataset": rows[index]["dataset"], "role": rows[index]["role"],
                "group_id": rows[index]["group_id"], "label": int(labels[index]),
                "probabilities": values, "scores": system_scores, "fold": split["name"],
                "thresholds": {name: policy["threshold"] for name, policy in fitted["policies"].items()},
                "errors": {name: int((score >= fitted["policies"][name]["threshold"]) != bool(labels[index]))
                           for name, score in system_scores.items()},
                "fit_sha256": digest(model_path), "quality": quality[index].tolist(),
            })
        prediction_path = model_path.with_name(model_path.stem + "-predictions.json")
        if prediction_path.exists():
            if read(prediction_path)["rows"] != prediction_rows:
                raise ValueError("completed source prediction readback/provenance drift")
        else:
            write_immutable_record(prediction_path, {"rows": prediction_rows, "fit_sha256": digest(model_path)})
        if read(prediction_path)["rows"] != prediction_rows:
            raise ValueError("saved source prediction readback failed")
        summary = {"fold": split["name"], "fit_sha256": digest(model_path),
                   "predictions_sha256": digest(prediction_path), "counts": {
                       key: len(split[key]) for key in ("fitting", "validation", "calibration")},
                   "predicted": len(prediction_rows),
                   "fit_domain_counts": {
                       domain: sum(rows[index]["dataset"] == domain for index in fit)
                       for domain in sorted(set(domains(fit)))},
                   "oof_errors": {
                       name: sum(row["errors"][name] for row in prediction_rows)
                       for name in fitted["policies"]},
                   "oof_error_prevalence": {
                       name: sum(row["errors"][name] for row in prediction_rows) / len(prediction_rows)
                       for name in fitted["policies"]},
                   "selected_epochs": {name: head["selected_epoch"] for name, head in fitted["heads"].items()},
                   "thresholds": {name: policy["threshold"] for name, policy in fitted["policies"].items()}}
        summaries.append(summary)
        if split["name"] == "final":
            final = prediction_rows
        else:
            records[split["name"].split(":", 1)[0]].extend(prediction_rows)
        print("SOURCE297_FITTED", json.dumps(summary), flush=True)
    if final is None:
        raise ValueError("final source model/g_domain predictions absent")
    expected = {identity(row) for row in rows if row["role"] != "g_domain"}
    for strategy, values in records.items():
        if len(values) != len(expected) or {row["id"] for row in values} != expected:
            raise ValueError("one-to-one identical candidate coverage required for both OOF strategies")
        if any(row["role"] == "g_domain" for row in values):
            raise ValueError("G_domain leaked into OOF/risk fit")
        seal(OUTPUT / f"{strategy}-predictions.json", {"rows": values})
    final_split = next(split for split in inputs["partitions"] if split["name"] == "final")
    fitting_quality = quality[positions(final_split["fitting"])]
    quality_mean, raw_scale = fitting_quality.mean(axis=0), fitting_quality.std(axis=0)
    constants = np.flatnonzero(raw_scale == 0).tolist()
    quality_scale = np.where(raw_scale == 0, 1.0, raw_scale)
    risk_summaries = []

    def design(predictions, system, variant):
        other = "openclip" if system == "heterogeneous" else "dino_plain"
        probability = np.asarray([[row["probabilities"]["dino_reg"], row["probabilities"][other]] for row in predictions])
        q = (np.asarray([row["quality"] for row in predictions]) - quality_mean) / quality_scale
        thresholds = np.asarray([row["thresholds"][system] for row in predictions])
        # Only the operational feature varies by each record's source-selected threshold.
        return np.concatenate([
            risk_features(probability[index:index + 1], q[index:index + 1], thresholds[index], variant)
            for index in range(len(predictions))])

    for strategy, values in records.items():
        for system in config["risk"]["systems"]:
            errors = np.array([row["errors"][system] for row in values], dtype=np.int64)
            event_counts = {"errors": int(errors.sum()), "correct": int(len(errors) - errors.sum())}
            if min(event_counts.values()) < 20:
                risk_summaries.append({"strategy": strategy, "system": system, **event_counts,
                                       "status": "not_applicable_insufficient_20_error_20_correct_support"})
                continue
            for variant in config["risk"]["variants"]:
                guard()
                path = OUTPUT / "risks" / f"{strategy}-{system}-{variant}.json"
                binding = {"config_sha256": digest(CONFIG), "quality_sha256": digest(OUTPUT / "quality.json"),
                           "inputs_sha256": digest(OUTPUT / "inputs.json")}
                if path.exists():
                    previous = read(path)
                    if previous["binding"] != binding:
                        raise ValueError("completed risk fit binding drift")
                    fitted = previous["model"]
                else:
                    fitted = fit_risk(design(values, system, variant), errors, [row["dataset"] for row in values], guard)
                predicted = sigmoid(head_logits(fitted, design(final, system, variant)))
                gate_errors = np.array([row["errors"][system] for row in final], dtype=np.int64)
                artifact = {
                    "binding": binding, "model": fitted, "strategy": strategy, "system": system, "variant": variant,
                    "oof_predictions_sha256": digest(OUTPUT / f"{strategy}-predictions.json"),
                    "final_prediction_sha256": summaries[0]["predictions_sha256"],
                    "quality_mean": quality_mean.tolist(), "quality_scale": quality_scale.tolist(),
                    "constant_quality_indices": constants, "statistics_ids": final_split["fitting"],
                    "g_domain_predictions": [{"id": row["id"], "risk": float(score), "error": row["errors"][system]}
                                             for row, score in zip(final, predicted, strict=True)],
                    "calibrated_probability_claim": False, "gate_selected": False}
                seal(path, artifact)
                if read(path) != artifact:
                    raise ValueError("risk model/prediction exact saved readback failed")
                estimable = len(set(gate_errors.tolist())) == 2
                risk_summaries.append({
                    "strategy": strategy, "system": system, "variant": variant, **event_counts,
                    "status": "fitted", "model_sha256": digest(path),
                    "g_domain_prediction_count": len(final),
                    "g_domain_error_count": int(gate_errors.sum()),
                    "g_domain_error_AP": float(average_precision_score(gate_errors, predicted)) if estimable else None,
                    "g_domain_brier": float(np.mean((predicted - gate_errors) ** 2)),
                    "g_domain_nll": float(np.mean(np.logaddexp(0, head_logits(fitted, design(final, system, variant)))
                                                 - gate_errors * head_logits(fitted, design(final, system, variant)))),
                    "diagnostic_only_not_gate_selection": True,
                })
    metrics = {}
    for strategy, values in records.items():
        metrics[strategy] = {}
        for system in ("dino_reg", "openclip", "heterogeneous", "same_family"):
            per_domain = {}
            for domain in config["source_domains"]:
                selected = [row for row in values if row["dataset"] == domain]
                y = [row["label"] for row in selected]
                score = [row["scores"][system] for row in selected]
                predicted = [row["scores"][system] >= row["thresholds"][system] for row in selected]
                per_domain[domain] = {"auroc": float(roc_auc_score(y, score)),
                                      "balanced_accuracy": float(balanced_accuracy_score(y, predicted)),
                                      "errors": sum(row["errors"][system] for row in selected),
                                      "count": len(selected)}
            metrics[strategy][system] = {
                "per_domain": per_domain,
                "macro_auroc": float(np.mean([row["auroc"] for row in per_domain.values()])),
                "macro_balanced_accuracy": float(np.mean([row["balanced_accuracy"] for row in per_domain.values()])),
                "score_range": float(np.ptp([row["scores"][system] for row in values])),
                "competence_lcb": None,
                "competence_status": "not_certified_bootstrap_and_remaining_fold_seed_evidence_absent"}
    result = {
        "folds": summaries, "head_fits": 14, "calibrator_fits": 21,
        "risk_fits": sum(row["status"] == "fitted" for row in risk_summaries),
        "risk_results": risk_summaries, "oof_metrics": metrics,
        "oof_candidate_count_per_strategy": len(expected), "identical_candidate_joins_passed": True,
        "g_domain_successes": len(final), "quality_statistics_scope": "final_head_fitting_only",
        "no_gate_selection": True, "scientific_source_dry_run_complete": False,
        "remaining": ["three_outer_rotations_and_remaining_seeds",
                      "cluster_bootstrap_competence_and_claim_specific_applicability",
                      "budget_matched_branch_fit_size_sensitivity_for_material_size_differences",
                      "registered_no_q_attribution_and_domain_identifiability_drift_diagnostics",
                      "gate_policy_and_complete_normal_validator_evidence_bundle"],
        "target_images_accessed": False, "target_predictions": False,
    }
    seal(OUTPUT / "fitting.json", result)
    return result


def worker(resume: bool = False) -> None:
    config, plan, approval = authority()
    attempt = read(OUTPUT / ("resume_attempt_lock.json" if resume else "attempt_lock.json"))
    if os.getppid() != attempt["supervisor_pid"]:
        raise ValueError("single original source297 supervisor required")
    enforce(approval)
    source_rows(config)
    inputs = read(OUTPUT / "inputs.json")
    CACHE.mkdir(parents=True, exist_ok=True)
    extracted = extraction(inputs["rows"], config, plan, approval)
    quality = quality_cache(inputs["rows"], approval)
    fitted = source_fit(inputs, extracted, quality, config, approval)
    stage_errors = {stage: validate_stage(ROOT, stage, frozen_root=integration.FROZEN, source_use_root=integration.USE)
                    for stage in ("schema", "data-audit", "source-dry-run", "analysis-freeze", "locked-evaluation")}
    if stage_errors["schema"] or stage_errors["data-audit"]:
        raise ValueError("accepted schema/data prerequisites drifted")
    for name, expected in plan["accepted_summary_sha256"].items():
        if digest(ROOT / name) != expected:
            raise ValueError("accepted dataset summaries changed")
    enforce(approval, final=True)
    public_models = {name: {key: value for key, value in model.items()
                            if key not in {"shards", "feature_keys", "ids"}}
                     for name, model in extracted.items() if name != "text"}
    result = {
        "version": 1, "checkpoint": 297, "status": "first_source_fold_features_and_fitting_complete",
        "config_sha256": digest(CONFIG), "inputs_sha256": plan["inputs_sha256"],
        "execution_plan_sha256": digest(OUTPUT / "execution_plan.json"),
        "owner_approval_sha256": digest(OUTPUT / "owner_approval.json"),
        "extraction_sha256": digest(OUTPUT / "extraction.json"),
        "fitting_sha256": digest(OUTPUT / "fitting.json"),
        "quality_sha256": digest(OUTPUT / "quality.json"),
        "outer_target": config["outer_target"], "seed": config["seed"],
        "source_use_denominator": 1932, "successful_feature_inputs": 1906, "retained_source_failures": 26,
        "models": public_models, "fitting": fitted, "stage_errors": stage_errors,
        "scientific_source_dry_run_complete": False, "scientific_readiness": False,
        "new_video_decodes": 0, "detector_calls": 0, "target_images_accessed": False,
        "target_predictions": False, "new_checkpoint_downloads": 0, "new_text_forwards": 0,
        "accepted_summaries_unchanged": True, "automatic_retry": False,
    }
    seal(OUTPUT / "worker_completion.json", result)


def supervise(resume: bool = False) -> int:
    config, plan, approval = authority()
    enforce(approval)
    if resume:
        permission = read(OUTPUT / "resume_authorization.json")
        prior = OUTPUT / "terminal.json"
        if (permission.get("explicit_owner_resume") is not True
                or permission.get("original_approval_sha256") != digest(OUTPUT / "owner_approval.json")
                or permission.get("failed_terminal_sha256") != digest(prior)
                or read(prior)["status"] != "stopped_no_retry"):
            raise ValueError("explicit resume authority binding original failed terminal/deadline required")
    write_immutable_record(OUTPUT / ("resume_attempt_lock.json" if resume else "attempt_lock.json"), {
        "supervisor_pid": os.getpid(), "config_sha256": digest(CONFIG),
        "implementation_sha256": plan["implementation_sha256"], "automatic_retry": False})
    env = {**os.environ, "CUBLAS_WORKSPACE_CONFIG": ":4096:8", "HF_HUB_OFFLINE": "1",
           "OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2", "MKL_NUM_THREADS": "2"}
    command = [sys.executable, str(Path(__file__)), "--worker"]
    if resume:
        command.append("--resume")
    child = subprocess.Popen(command, start_new_session=True, env=env)
    failure, peak_rss, peak_bytes = None, 0, 0
    try:
        while child.poll() is None:
            enforce(approval)
            own_rss = next(int(line.split()[1]) * 1024
                           for line in Path(f"/proc/{os.getpid()}/status").read_text().splitlines()
                           if line.startswith("VmRSS:"))
            peak_rss = max(peak_rss, pilot.group_rss(child.pid) + own_rss)
            peak_bytes = max(peak_bytes, owned_size())
            if peak_rss > approval["limits"]["rss_bytes"]:
                raise MemoryError("combined source297 process-tree RSS cap")
            time.sleep(0.5)
        if child.returncode:
            raise RuntimeError(f"source297 worker exit {child.returncode}; no automatic retry")
        enforce(approval, final=True)
    except (OSError, ValueError, RuntimeError, TimeoutError, MemoryError) as exc:
        failure = f"{type(exc).__name__}: {exc}"
        print("SOURCE297_STOP", failure, file=sys.stderr, flush=True)
    finally:
        if child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
    terminal = {
        "version": 1, "checkpoint": 297, "status": "complete" if failure is None else "stopped_no_retry",
        "failure": failure, "sampled_peak_rss_bytes": peak_rss,
        "peak_owned_new_temporary_bytes": max(peak_bytes, owned_size()),
        "wall_seconds_from_original_approval": time.time() - approval["started_unix_seconds"],
        "limits": config["limits"], "automatic_retry": False,
        "worker_completion_sha256": digest(OUTPUT / "worker_completion.json") if failure is None else None,
        "successful_shards_preserved": True, "target_evaluation": False, "scientific_readiness": False}
    write_immutable_record(OUTPUT / ("resume_terminal.json" if resume else "terminal.json"), terminal)
    public = {**read(OUTPUT / "worker_completion.json"), "terminal": terminal} if failure is None else terminal
    write_immutable_record(ROOT / f"results/phase1/source-run297{'-resume' if resume else ''}-v1.json", public)
    print("SOURCE297_TERMINAL", json.dumps(terminal), flush=True)
    return int(failure is not None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--worker", action="store_true")
    parser.add_argument("--resume", action="store_true", help="requires separate explicit original-deadline resume authority")
    args = parser.parse_args()
    if args.prepare:
        prepare()
    elif args.worker:
        worker(args.resume)
    else:
        raise SystemExit(supervise(args.resume))
