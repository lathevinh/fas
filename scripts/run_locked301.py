"""Prepare, authorize, execute and reconstruct the fixed locked-target package."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
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
from fas.locked_metrics import SYSTEMS, STRATEGIES, arrays, cell_metrics, evaluate, select_k1, transaction_ledger
from fas.preregistration import artifact_hashes, validate_stage
from fas.source_diagnostics import design
from fas.source_experiment import predict
from fas.source_fitting import head_logits, identity, quality_vector, sigmoid
import run_source299 as source
from close_source299 import check_predictions

CONFIG = ROOT / "configs/locked_run301_v1.yaml"
OUTPUT = Path("/mnt/e/FAS-private/artifacts/phase1/locked_run301_v3")
CACHE = Path.home() / ".cache/fas/locked-run301-v3"
PUBLIC = ROOT / "results/locked-evaluation"
POLICIES = PUBLIC / "source-policies301-v3.json"
ANSWER = "approve_locked301_fixed_target_evaluation"


def read(path: Path) -> dict:
    return json.loads(path.read_bytes())


def primary_names() -> list[str]:
    return [f"{strategy}/{system}/R_DVd" for strategy in STRATEGIES for system in SYSTEMS]


def bind(files: dict, key: str, path: Path) -> None:
    files[key] = {"path": str(path), "sha256": digest(path)}


def check_files(files: dict) -> None:
    for key, record in files.items():
        path = Path(record["path"])
        if path.is_symlink() or not path.is_file() or digest(path) != record["sha256"]:
            raise ValueError(f"sealed artifact drift: {key}")


def prepare() -> None:
    config = read(CONFIG)
    errors = validate_stage(ROOT, "source-dry-run", frozen_root=source.old.integration.FROZEN,
                            source_use_root=source.old.integration.USE)
    if errors:
        raise ValueError(f"normal source prerequisites fail: {errors}")
    manifest_path = source.old.pilot.INTEGRATION / "source_manifest.json"
    if digest(manifest_path) != config["source_manifest_sha256"]:
        raise ValueError("accepted complete transaction manifest changed")
    historical = read(ROOT / config["source_freeze"])
    for name, expected in historical["artifact_sha256"].items():
        content = subprocess.check_output(["git", "show", f"{historical['created_from_commit']}:{name}"], cwd=ROOT)
        if hashlib.sha256(content).hexdigest() != expected:
            raise ValueError("immutable historical source baseline does not reconstruct from Git")
    manifest = read(manifest_path)
    rows = sorted([row for row in manifest["rows"] if row["official_split"] == "test"], key=identity)
    cached_ids = {identity(row) for row in read(source.OUTPUT / "inputs.json")["rows"]}
    success_ids = {identity(row) for row in rows if row["detector_status"] == "success"}
    missing_ids = success_ids - cached_ids
    if (len(rows) != 2943 or len(success_ids) != 2929 or len(success_ids & cached_ids) != 2310
            or len(missing_ids) != 619 or any(not key.startswith("SiW-Mv2/") for key in missing_ids)):
        raise ValueError("exact2310 compatible cached targets plus619 new SiW test images required")
    expected = {"OULU-NPU": (1800, 1800), "CASIA-FASD": (360, 354),
                "MSU-MFSD": (160, 156), "SiW-Mv2": (623, 619)}
    files = {}
    bind(files, "source_manifest", manifest_path)
    bind(files, "accepted_source_worker", source.OUTPUT / "worker_completion.json")
    bind(files, "accepted_source_terminal", source.OUTPUT / "terminal.json")
    bind(files, "accepted_source_closure", source.OUTPUT / "closure.json")
    bind(files, "source_extraction", source.OUTPUT / "extraction.json")
    bind(files, "source_inputs", source.OUTPUT / "inputs.json")
    bind(files, "prior_extraction", source.old.OUTPUT / "extraction.json")
    bind(files, "prior_quality", source.old.OUTPUT / "quality.json")
    for public_name in ("source-run299-v1.json", "source-closure299-v1.json"):
        bind(files, public_name, ROOT / "results/phase1" / public_name)
    worker = read(source.OUTPUT / "worker_completion.json")
    if (digest(source.OUTPUT / "worker_completion.json") != read(source.OUTPUT / "terminal.json")["worker_completion_sha256"]
            or read(source.OUTPUT / "terminal.json")["status"] != "complete"
            or digest(source.OUTPUT / "extraction.json") != worker["extraction_sha256"]
            or not worker["source_dry_run_validator_passed"]):
        raise ValueError("exact successful accepted source completion required")
    public_worker = read(ROOT / "results/phase1/source-run299-v1.json")
    if any(public_worker[key] != value for key, value in worker.items()):
        raise ValueError("accepted public/private worker commitments disagree")
    for target, counts in expected.items():
        population = [row for row in rows if row["dataset"] == target]
        if (len(population), sum(row["detector_status"] == "success" for row in population)) != counts:
            raise ValueError("exact frozen official-test population/mask required")
        for row in population:
            bind(files, "transaction/" + identity(row), Path(row["record_path"]))
            if files["transaction/" + identity(row)]["sha256"] != row["record_sha256"]:
                raise ValueError("accepted target transaction drift")
    prior = read(source.old.OUTPUT / "extraction.json")
    extracted = read(source.OUTPUT / "extraction.json")
    for name in ("dino_reg", "dino_plain", "openclip"):
        bind(files, f"checkpoint/{name}", source.old.pilot.NATIVE / "checkpoints" / f"{name}.pth")
        if files[f"checkpoint/{name}"]["sha256"] != prior[name]["checkpoint_sha256"]:
            raise ValueError("exact registered checkpoint required")
        for origin, receipt in (("prior", prior[name]), ("source", extracted[name])):
            for index, shard in enumerate(receipt["shards"]):
                bind(files, f"cache/{origin}/{name}/{index}", Path(shard["path"]))
                if files[f"cache/{origin}/{name}/{index}"]["sha256"] != shard["sha256"]:
                    raise ValueError("accepted feature shard drift")
    bind(files, "fixed_text", Path(prior["text"]["path"]))
    if files["fixed_text"]["sha256"] != prior["text"]["sha256"]:
        raise ValueError("fixed text embedding changed")
    for origin, receipt in (("prior", read(source.old.OUTPUT / "quality.json")), ("source", extracted["quality"])):
        for index, shard in enumerate(receipt["shards"]):
            bind(files, f"quality/{origin}/{index}", Path(shard["path"]))
            if files[f"quality/{origin}/{index}"]["sha256"] != shard["sha256"]:
                raise ValueError("accepted quality shard drift")
    combinations, policies = [], []
    for context in read(source.OUTPUT / "inputs.json")["contexts"]:
        key, target = context["key"], context["outer_target"]
        root = source.OUTPUT / "combinations" / key
        result = read(root / "result.json")
        if result != next(value for value in worker["combinations"] if value["key"] == key):
            raise ValueError("exact published combination required")
        split = context["partitions"][0]
        model_path = root / "fits" / f"{payload_digest({'split': split})}.json"
        bind(files, key + "/final", model_path)
        model_meta = next(meta for meta in result["contexts"] if meta["context"] == "final")
        if digest(model_path) != model_meta["sha256"]:
            raise ValueError("selected final head/calibrator/threshold bytes changed")
        final_path = root / "predictions" / f"{payload_digest({'name': 'final'})}.json"
        bind(files, key + "/source_gate_predictions", final_path)
        final = read(final_path)["rows"]
        originals = [row for row in manifest["rows"] if row["source_use_eligible"]
                     and row["dataset"] != target and row["role"] == "g_domain"]
        local_policies = {}
        risk_refs = {}
        for record in result["risk_fits"]:
            name = f"{record['strategy']}/{record['system']}/{record['variant']}"
            path = root / "risks" / record["strategy"] / f"{record['system']}-{record['variant']}.json"
            model = read(path)
            if any(model[k] != v for k, v in record.items() if k != "strategy") or model["status"] != "fitted":
                raise ValueError("complete accepted fitted risk records required")
            ref = key + "/risk/" + name
            bind(files, ref, path)
            risk_refs[name] = ref
            if name in primary_names():
                if [row["id"] for row in model["predictions"]] != [row["id"] for row in final]:
                    raise ValueError("paired source policy risk/sample join drift")
                risks = np.asarray([row["risk"] for row in model["predictions"]])
                local_policies[name] = select_k1(originals, final, risks, record["system"], target,
                                                 config["source_k1"]["alpha"])
        combinations.append({"key": key, "outer_target": target, "seed": context["seed"],
                             "model_ref": key + "/final", "risk_refs": risk_refs, "policies": local_policies,
                             "claims": result["claims"], "reuse297": context["reuse297"],
                             "final_split_sha256": payload_digest({"split": split})})
        policies.append({"key": key, "outer_target": target, "seed": context["seed"], "policies": local_policies})
    public_policies = {"version": 1, "owner_selected": config["source_k1"]["owner_selected"],
                       "target_predictions": False, "records": policies}
    populations = {target: {"originals": counts[0], "successes": counts[1], "failures": counts[0] - counts[1],
                           "population_and_mask_sha256": payload_digest({"rows": [
                               {"id": identity(row), "group": row["group_id"], "label": row["binary_label"],
                                "status": row["detector_status"], "crops": row["crops"]}
                               for row in rows if row["dataset"] == target]})} for target, counts in expected.items()}
    inputs = {"target_rows": rows, "combinations": combinations, "files": files}
    write_immutable_record(OUTPUT / "inputs.json", inputs)
    write_immutable_record(POLICIES, public_policies)
    # Public logical IDs must not contain original video/subject identifiers.
    public_bindings = {key: value["sha256"] for key, value in files.items() if not key.startswith("transaction/")}
    changed = [name for name, value in historical["artifact_sha256"].items()
               if not (ROOT / name).exists() or digest(ROOT / name) != value]
    package = {
        "version": 3, "checkpoint": 301, "state": "sealed_package_not_execution_authority",
        "config_sha256": digest(CONFIG), "inputs_sha256": digest(OUTPUT / "inputs.json"),
        "predecessor_freeze_sha256": digest(ROOT / config["source_freeze"]),
        "predecessor_frozen_paths_changed": changed, "source_models_retrained": 0,
        "superseded_unapproved_preflights": [
            {"path": str(path.relative_to(ROOT)), "sha256": digest(path), "never_authorized_or_executed": True}
            for path in sorted(PUBLIC.glob("execution-manifest301-v*.json"))],
        "public_bindings_sha256": public_bindings,
        "private_all_artifact_bindings_sha256": payload_digest(files),
        "target_populations": populations, "combination_count": len(combinations),
        "runtime": source.old.runtime(), "source_policies_sha256": digest(POLICIES),
        "implementation_sha256": artifact_hashes(ROOT),
        "additional_configs_sha256": {name: digest(ROOT / name) for name in
            ("configs/source_pilot295_v1.yaml", "configs/source_run297_v1.yaml", "configs/source_run299_v1.yaml")},
        "target_successes": 2929, "target_originals": 2943, "cached_target_successes": 2310,
        "new_SiW_test_images": 619, "new_image_forwards_maximum": 1857, "new_text_forwards": 0,
        "new_head_calibrator_risk_fits": 0, "limits": config["limits"],
        "target_pixels_features_or_predictions_read_in_preflight": False,
        "target_metadata_and_hashes_only": True,
    }
    # The manifest cannot recursively hash itself or policies added by its own preparation.
    package["implementation_sha256"] = {k: v for k, v in package["implementation_sha256"].items()
                                         if not k.startswith("results/locked-evaluation/")}
    write_immutable_record(ROOT / config["execution_manifest"], package)
    print(json.dumps({"populations": populations, "new_forwards": 1857, "policies": len(policies) * 4,
                      "manifest_sha256": digest(ROOT / config["execution_manifest"])}, indent=2))


def validate_package(*, authorized: bool) -> tuple[dict, dict, dict]:
    config = read(CONFIG)
    package = read(ROOT / config["execution_manifest"])
    inputs = read(OUTPUT / "inputs.json")
    if (digest(CONFIG) != package["config_sha256"] or digest(OUTPUT / "inputs.json") != package["inputs_sha256"]
            or digest(POLICIES) != package["source_policies_sha256"]
            or digest(ROOT / config["source_freeze"]) != package["predecessor_freeze_sha256"]):
        raise ValueError("sealed package/config/source-policy/predecessor drift")
    for name, expected in (package["implementation_sha256"] | package["additional_configs_sha256"]).items():
        if digest(ROOT / name) != expected:
            raise ValueError(f"sealed implementation/config drift: {name}")
    if payload_digest(inputs["files"]) != package["private_all_artifact_bindings_sha256"]:
        raise ValueError("private fitted-artifact/crop manifest binding drift")
    check_files(inputs["files"])
    if source.old.runtime() != package["runtime"]:
        raise ValueError("exact compatible encoder/numerical runtime required")
    errors = validate_stage(ROOT, "locked-evaluation" if authorized else "analysis-freeze",
                            frozen_root=source.old.integration.FROZEN, source_use_root=source.old.integration.USE,
                            freeze_record=Path(config["successor_freeze"]))
    if errors:
        raise ValueError(f"normal immutable successor gate fails: {errors}")
    return config, package, inputs


def authorize(answer: str) -> None:
    if answer != ANSWER:
        raise ValueError("exact typed owner answer required; preparation is not authority")
    config, package, inputs = validate_package(authorized=False)
    freeze_path = ROOT / config["successor_freeze"]
    freeze = read(freeze_path)
    approval = {"explicit_owner_approval": True, "selected_answer": answer, "automatic_retry": False,
                "manifest_sha256": digest(ROOT / config["execution_manifest"]),
                "successor_freeze_sha256": digest(freeze_path), "config_sha256": digest(CONFIG),
                "started_unix_seconds": time.time(), "limits": config["limits"]}
    write_immutable_record(OUTPUT / "owner_approval.json", approval)
    write_immutable_record(PUBLIC / "authorization.json", {
        "version": 1, "state": "authorized", "analysis_freeze_sha256": digest(freeze_path),
        "created_from_commit": freeze["created_from_commit"],
        "experiment_config_sha256": freeze["artifact_sha256"]["configs/experiment_core_v1.yaml"],
        "claim_spec_sha256": freeze["artifact_sha256"]["configs/claims_v1.yaml"],
        "outer_targets": freeze["outer_targets"], "seeds": freeze["seeds"]})
    write_immutable_record(PUBLIC / "authority301-v1.json", {
        **approval, "private_approval_sha256": digest(OUTPUT / "owner_approval.json"),
        "outer_targets": config["outer_targets"], "seeds": config["seeds"],
        "target_scope": package["target_populations"], "tuning_or_training_authorized": False})


def authority(*, final: bool = False) -> tuple[dict, dict, dict, dict]:
    config, package, inputs = validate_package(authorized=True)
    approval = read(OUTPUT / "owner_approval.json")
    if (approval["explicit_owner_approval"] is not True or approval["selected_answer"] != ANSWER
            or approval["automatic_retry"] is not False or approval["limits"] != config["limits"]
            or approval["config_sha256"] != digest(CONFIG)
            or approval["manifest_sha256"] != digest(ROOT / config["execution_manifest"])
            or approval["successor_freeze_sha256"] != digest(ROOT / config["successor_freeze"])):
        raise ValueError("exact fresh locked301 owner authority required")
    guard(approval, final=final)
    return config, package, inputs, approval


def guard(approval: dict, *, final: bool = False) -> None:
    limit = approval["limits"]["wall_seconds" if final else "work_seconds"]
    if time.time() >= approval["started_unix_seconds"] + limit:
        raise TimeoutError("original locked301 authority deadline expired; no reset/extension")


def source_cache(inputs: dict) -> tuple[list[str], dict[str, np.ndarray], np.ndarray]:
    prior = read(source.old.OUTPUT / "extraction.json")
    receipt = read(source.OUTPUT / "extraction.json")
    rows = read(source.OUTPUT / "inputs.json")["rows"]
    oulu = [row for row in rows if row["dataset"] == "OULU-NPU"]
    joined_ids = prior["dino_reg"]["ids"] + [identity(row) for row in oulu]
    positions = {key: index for index, key in enumerate(joined_ids)}
    order = [positions[identity(row)] for row in rows]
    features = {}
    pilot = read(source.old.pilot.CONFIG)
    for name in ("dino_reg", "dino_plain", "openclip"):
        model = receipt[name]
        keys = [cache_key(source.old.base_key(row, name, pilot, model["checkpoint_sha256"]), model["contract"]) for row in oulu]
        if keys != model["keys"]:
            raise ValueError("compatible source cache/native-crop contract drift")
        parts, offset = [], 0
        for shard in model["shards"]:
            parts.append(load_shard(Path(shard["path"]), keys[offset:offset + shard["count"]], model["shape"][1]))
            offset += shard["count"]
        if offset != 4949:
            raise ValueError("complete source cache coverage required")
        features[name] = np.concatenate([source.old.load_features(prior, name), np.concatenate(parts)])[order]
    quality = np.concatenate([source.load_quality(read(source.old.OUTPUT / "quality.json")),
                              source.load_quality(receipt["quality"])])[order]
    return [identity(row) for row in rows], features, quality


def target_features(inputs: dict, config: dict, approval: dict, *, replay: bool = False):
    import torch
    from fas.environment import verify_source_checkout
    rows = [row for row in inputs["target_rows"] if row["detector_status"] == "success"]
    source_ids, existing, source_quality = source_cache(inputs)
    positions = {key: index for index, key in enumerate(source_ids)}
    missing = [row for row in rows if identity(row) not in positions]
    if len(missing) != 619 or any(row["dataset"] != "SiW-Mv2" or row["official_split"] != "test" for row in missing):
        raise ValueError("only619 uncached official SiW test crops may be extracted")
    pilot = read(source.old.pilot.CONFIG)
    verify_source_checkout(source.old.pilot.UPSTREAM, pilot["dinov2_source_commit"])
    prior = read(source.old.OUTPUT / "extraction.json")
    if not replay and not torch.cuda.is_available():
        raise RuntimeError("CUDA required; no fallback/download/substitution")
    torch.set_num_threads(2)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(20260917)
    if not replay:
        torch.cuda.set_per_process_memory_fraction(config["limits"]["cuda_bytes"] / torch.cuda.get_device_properties(0).total_memory)
    sys.path.insert(0, str(source.old.pilot.UPSTREAM))
    from dinov2.hub import backbones
    features, receipts, calls = {}, {}, 0
    for name, spec in pilot["models"].items():
        contract = {**prior[name]["contract"], "locked_manifest_sha256": digest(ROOT / config["execution_manifest"])}
        keys = [cache_key(source.old.base_key(row, name, pilot, prior[name]["checkpoint_sha256"]), contract) for row in missing]
        parts, shards, model, model_calls = [], [], None, 0
        if not replay:
            torch.cuda.reset_peak_memory_stats()
        for start in range(0, len(missing), 32):
            guard(approval, final=replay)
            selected, selected_keys = missing[start:start + 32], keys[start:start + 32]
            path = CACHE / name / f"{start:06d}.npz"
            if replay:
                values = load_shard(path, selected_keys, spec["feature_dimension"])
            else:
                if model is None:
                    checkpoint = source.old.pilot.NATIVE / "checkpoints" / f"{name}.pth"
                    if name.startswith("dino"):
                        model = getattr(backbones, spec["local_factory"])(pretrained=False)
                        model.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True), strict=True)
                    else:
                        import open_clip
                        model = open_clip.create_model("ViT-B-16", pretrained=None, precision="fp32")
                        incompatible = open_clip.load_checkpoint(model, str(checkpoint), strict=True, weights_only=True)
                        if incompatible.missing_keys or incompatible.unexpected_keys:
                            raise ValueError("strict local OpenCLIP state required")
                    model.requires_grad_(False).eval().cuda()
                vectors = []
                for row in selected:
                    guard(approval)
                    rgb = source.old.bound_rgb(row, spec["resolution"])
                    tensor = torch.from_numpy(normalize_rgb(
                        rgb, spec["resolution"], tuple(contract["normalization_mean"]), tuple(contract["normalization_std"]))[None]).cuda()
                    with torch.inference_mode():
                        if name.startswith("dino"):
                            output = model.forward_features(tensor)
                            value = dino_pool(output["x_norm_clstoken"].cpu().numpy(), output["x_norm_patchtokens"].cpu().numpy())
                            del output
                        else:
                            value = model.encode_image(tensor, normalize=True).cpu().numpy()
                    del tensor
                    check_feature(value, 1, spec["feature_dimension"])
                    vectors.append(value)
                    model_calls += 1
                    if max(torch.cuda.max_memory_allocated(), torch.cuda.max_memory_reserved()) > config["limits"]["cuda_bytes"]:
                        raise MemoryError("original locked301 CUDA cap")
                values = np.concatenate(vectors)
                save_shard(path, selected_keys, values)
                print("LOCKED301_EXTRACTION", name, start + len(selected), 619, flush=True)
            parts.append(values)
            shards.append({"path": str(path), "sha256": digest(path), "count": len(selected)})
        new = np.concatenate(parts)
        added = {identity(row): i for i, row in enumerate(missing)}
        features[name] = np.asarray([existing[name][positions[identity(row)]] if identity(row) in positions
                                     else new[added[identity(row)]] for row in rows], dtype=np.float32)
        check_feature(features[name], 2929, spec["feature_dimension"])
        receipts[name] = {"keys": keys, "contract": contract, "shards": shards, "new_image_forwards": model_calls,
                          "shape": list(features[name].shape), "reused_source_rows": 2310,
                          "final_peak_allocated": 0 if replay else torch.cuda.max_memory_allocated(),
                          "final_peak_reserved": 0 if replay else torch.cuda.max_memory_reserved()}
        calls += model_calls
        if model is not None:
            del model
        gc.collect()
        if not replay:
            torch.cuda.empty_cache()
    quality_keys = [payload_digest({"row": identity(row), "crop": row["crops"]["224"]["sha256"],
                                   "transaction": row["record_sha256"], "quality_code": digest(ROOT / "src/fas/source_fitting.py")})
                    for row in missing]
    quality_path = CACHE / "quality.npz"
    if replay:
        new_quality = load_shard(quality_path, quality_keys, 5)
    else:
        vectors = []
        for row in missing:
            guard(approval)
            transaction = read(Path(row["record_path"]))
            if transaction["selected_frame"] != row["selected_frame"] or transaction["video_id"] != row["video_id"]:
                raise ValueError("target detector transaction/selected frame drift")
            vectors.append(quality_vector(source.old.bound_rgb(row, 224), transaction))
        new_quality = np.asarray(vectors, dtype=np.float32)
        save_shard(quality_path, quality_keys, new_quality)
    quality = np.asarray([source_quality[positions[identity(row)]] if identity(row) in positions
                          else new_quality[added[identity(row)]] for row in rows], dtype=np.float64)
    text = np.load(Path(prior["text"]["path"]), allow_pickle=False)
    receipt = {"models": receipts, "new_image_forwards": calls, "new_text_forwards": 0,
               "quality_sha256": digest(quality_path), "quality_keys": quality_keys,
               "quality_path": str(quality_path), "success_ids": [identity(row) for row in rows]}
    if replay:
        saved = read(OUTPUT / "extraction.json")
        if (saved["quality_sha256"] != receipt["quality_sha256"] or saved["success_ids"] != receipt["success_ids"]
                or saved["quality_keys"] != quality_keys or saved["new_image_forwards"] != 1857):
            raise ValueError("saved target extraction coverage drift")
        for name, value in receipts.items():
            if any(saved["models"][name][key] != value[key] for key in ("keys", "contract", "shards", "shape", "reused_source_rows")):
                raise ValueError("saved locked target shard/native-contract hash drift")
    else:
        if calls != 1857:
            raise ValueError("exact approved new target forward budget required")
        write_immutable_record(OUTPUT / "extraction.json", receipt)
    return rows, features, quality, text


def predictions(inputs: dict, config: dict, approval: dict, *, replay: bool = False):
    rows, features, quality, text = target_features(inputs, config, approval, replay=replay)
    prompts = read(ROOT / "configs/prompts_core_v1.yaml")["classes"]
    positions = {identity(row): i for i, row in enumerate(rows)}
    cells = {target: {} for target in config["outer_targets"]}
    hashes, prediction_rows, risk_values = {}, 0, 0
    for context in inputs["combinations"]:
        guard(approval, final=replay)
        target, key = context["outer_target"], context["key"]
        originals = [row for row in inputs["target_rows"] if row["dataset"] == target]
        selected = [row for row in rows if row["dataset"] == target]
        indices = [positions[identity(row)] for row in selected]
        model_file = inputs["files"][context["model_ref"]]
        fitted = read(Path(model_file["path"]))["fitted"]
        if context["reuse297"]:
            correct_binding = (target == "OULU-NPU" and context["seed"] == 20260917
                               and fitted["binding"]["config_sha256"] == digest(source.old.CONFIG))
        else:
            correct_binding = fitted["binding"]["outer_target"] == target and fitted["binding"]["seed"] == context["seed"]
        if (not correct_binding or payload_digest({"split": fitted["split"]}) != context["final_split_sha256"]
                or any(key.startswith(target + "/") for field in ("fitting", "validation", "calibration")
                       for key in fitted["split"][field])):
            raise ValueError("outer-excluded selected fitted state required")
        local_features = {name: value[indices] for name, value in features.items()}
        clip = mean_cosine_logit(local_features["openclip"], text, len(prompts["live"]))
        predicted = predict(selected, local_features, clip, quality[indices], [identity(row) for row in selected],
                            fitted, model_file["sha256"])
        risk_scores = {}
        for name, ref in context["risk_refs"].items():
            model = read(Path(inputs["files"][ref]["path"]))
            if model["binding"]["outer_target"] != target or model["binding"]["seed"] != context["seed"]:
                raise ValueError("fold-local source risk state required")
            values = design(predicted, model["system"], model["variant"], np.asarray(model["quality_mean"]),
                            np.asarray(model["quality_scale"]))
            risk_scores[name] = sigmoid(head_logits(model["model"], values))
        for system in SYSTEMS:
            p = np.asarray([row["scores"][system] for row in predicted])
            threshold = fitted["policies"][system]["threshold"]
            branches = ("dino_reg", "openclip" if system == "heterogeneous" else "dino_plain")
            disagreement = np.asarray([abs(row["probabilities"][branches[0]] - row["probabilities"][branches[1]])
                                       for row in predicted])
            clipped = np.clip(p, 1e-12, 1 - 1e-12)
            for name, value in {"MSP": np.minimum(p, 1 - p), "entropy": -clipped * np.log(clipped) - (1 - clipped) * np.log(1 - clipped),
                                "operational_margin": -abs(p - threshold), "absolute_disagreement": disagreement}.items():
                risk_scores[f"nonlearned/{system}/{name}"] = value
        path = OUTPUT / "predictions" / f"{key}.json"
        saved = {"rows": predicted, "risk_scores": {name: value.tolist() for name, value in risk_scores.items()},
                 "fitted_sha256": model_file["sha256"], "manifest_sha256": digest(ROOT / config["execution_manifest"])}
        ledgers = transaction_ledger(originals, predicted, risk_scores, context["policies"], model_file["sha256"],
                                     {name: inputs["files"][ref]["sha256"] for name, ref in context["risk_refs"].items()},
                                     digest(POLICIES))
        saved["transaction_ledgers"] = ledgers
        if replay:
            prior = read(path)
            check_predictions(prior["rows"], predicted)
            if (set(prior["risk_scores"]) != set(saved["risk_scores"])
                    or any(not np.allclose(prior["risk_scores"][name], values, rtol=1e-12, atol=1e-12)
                           for name, values in risk_scores.items())):
                raise ValueError("saved target risk values do not reconstruct")
            if prior["transaction_ledgers"] != ledgers:
                raise ValueError("saved original-denominator technical failure/actions do not reconstruct")
        else:
            write_immutable_record(path, saved)
        hashes[key] = digest(path)
        cells[target][context["seed"]] = arrays(originals, predicted, risk_scores, context["policies"])
        prediction_rows += len(predicted)
        risk_values += len(predicted) * len(risk_scores)
        print("LOCKED301_PREDICTIONS_VERIFIED" if replay else "LOCKED301_PREDICTIONS", key, len(predicted), flush=True)
    return cells, hashes, prediction_rows, risk_values


def worker() -> None:
    config, package, inputs, approval = authority()
    if os.getppid() != read(OUTPUT / "attempt_lock.json")["supervisor_pid"]:
        raise ValueError("original supervised locked301 worker required")
    cells, hashes, prediction_rows, risk_values = predictions(inputs, config, approval)
    dependencies = {name: all(context["claims"][claim] == "eligible" for context in inputs["combinations"])
                    for name, claim in (("rq1", "rq1_oof_transfer"), ("rq2", "rq2_complete_system"))}
    result = evaluate(cells, dependencies, config["bootstrap_repetitions"], config["bootstrap_seed"], lambda: guard(approval))
    check_files(inputs["files"])
    guard(approval)
    write_immutable_record(OUTPUT / "evaluation.json", result)
    receipt = {"version": 1, "checkpoint": 301, "status": "fixed_locked_target_evaluation_complete",
               "manifest_sha256": digest(ROOT / config["execution_manifest"]),
               "successor_freeze_sha256": digest(ROOT / config["successor_freeze"]),
               "owner_approval_sha256": digest(OUTPUT / "owner_approval.json"),
               "extraction_sha256": digest(OUTPUT / "extraction.json"), "evaluation_sha256": digest(OUTPUT / "evaluation.json"),
               "target_prediction_sha256": hashes, "target_prediction_rows": prediction_rows, "risk_values": risk_values,
               "new_optimization_calls": 0, "new_text_forwards": 0, "target_tuning": False,
               "source_states_changed": False, "evaluation": result}
    write_immutable_record(OUTPUT / "worker_completion.json", receipt)


def owned_size() -> int:
    total = 0
    for root in (OUTPUT, CACHE):
        if root.exists():
            total += sum(path.stat().st_size for path in root.rglob("*") if path.is_file())
    path = PUBLIC / "run301-v1.json"
    return total + (path.stat().st_size if path.exists() else 0)


def supervise() -> None:
    config, package, inputs, approval = authority()
    write_immutable_record(OUTPUT / "attempt_lock.json", {"supervisor_pid": os.getpid(),
                                                       "manifest_sha256": digest(ROOT / config["execution_manifest"])})
    env = {**os.environ, "CUBLAS_WORKSPACE_CONFIG": ":4096:8", "HF_HUB_OFFLINE": "1",
           "OPENBLAS_NUM_THREADS": "2", "OMP_NUM_THREADS": "2", "MKL_NUM_THREADS": "2"}
    child = subprocess.Popen([sys.executable, str(Path(__file__)), "--worker"], start_new_session=True, env=env)
    failure, peak_rss, peak_size = None, 0, 0
    try:
        while child.poll() is None:
            guard(approval)
            own_rss = next(int(line.split()[1]) * 1024 for line in Path(f"/proc/{os.getpid()}/status").read_text().splitlines()
                           if line.startswith("VmRSS:"))
            peak_rss = max(peak_rss, source.old.pilot.group_rss(child.pid) + own_rss)
            peak_size = max(peak_size, owned_size())
            if peak_rss > config["limits"]["rss_bytes"] or peak_size > config["limits"]["output_bytes"]:
                raise MemoryError("combined locked301 process-tree RSS or owned artifact cap")
            time.sleep(0.5)
        if child.returncode:
            raise RuntimeError(f"locked301 worker exit{child.returncode}; no automatic retry")
        guard(approval, final=True)
    except (OSError, ValueError, RuntimeError, TimeoutError, MemoryError) as exc:
        failure = f"{type(exc).__name__}: {exc}"
        print("LOCKED301_STOP", failure, file=sys.stderr, flush=True)
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
                "limits": config["limits"], "automatic_retry": False,
                "worker_completion_sha256": digest(OUTPUT / "worker_completion.json") if failure is None else None}
    write_immutable_record(OUTPUT / "terminal.json", terminal)
    if failure:
        write_immutable_record(PUBLIC / "run301-v1.json", terminal)
        raise SystemExit(1)
    print("LOCKED301_TERMINAL", json.dumps(terminal), flush=True)


def close() -> None:
    config, package, inputs, approval = authority(final=True)
    guard(approval, final=True)
    terminal = read(OUTPUT / "terminal.json")
    worker = read(OUTPUT / "worker_completion.json")
    if terminal["status"] != "complete" or digest(OUTPUT / "worker_completion.json") != terminal["worker_completion_sha256"]:
        raise ValueError("successful bound original locked301 terminal required")
    if digest(OUTPUT / "evaluation.json") != worker["evaluation_sha256"]:
        raise ValueError("saved evaluation digest drift")
    cells, hashes, prediction_rows, risk_values = predictions(inputs, config, approval, replay=True)
    if hashes != worker["target_prediction_sha256"] or prediction_rows != 8787 or risk_values != worker["risk_values"]:
        raise ValueError("exact saved target coverage/hash accounting drift")
    for target, seeds in cells.items():
        for seed, cell in seeds.items():
            point = cell_metrics(cell, explanatory=True)
            if point != worker["evaluation"]["points"][target][str(seed)]:
                raise ValueError("registered target metrics do not reconstruct from saved predictions")
    guard(approval, final=True)
    result = {"version": 1, "status": "saved_locked_target_outputs_verified",
              "worker_sha256": digest(OUTPUT / "worker_completion.json"), "terminal_sha256": digest(OUTPUT / "terminal.json"),
              "target_prediction_rows_reconstructed": prediction_rows, "risk_values_reconstructed": risk_values,
              "new_encoder_calls": 0, "new_optimization_calls": 0, "target_tuning": False,
              "bootstrap_resampling_repeated": False, "wall_seconds_from_original_approval": time.time() - approval["started_unix_seconds"]}
    write_immutable_record(OUTPUT / "closure.json", result)
    if owned_size() > config["limits"]["output_bytes"]:
        raise MemoryError("locked301 owned output cap before public closure")
    write_immutable_record(PUBLIC / "run301-v1.json", {**worker, "terminal": terminal})
    write_immutable_record(PUBLIC / "closure301-v1.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare", action="store_true")
    modes.add_argument("--authorize", choices=[ANSWER])
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--worker", action="store_true")
    modes.add_argument("--close", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        prepare()
    elif args.authorize:
        authorize(args.authorize)
    elif args.run:
        supervise()
    elif args.worker:
        worker()
    else:
        close()
