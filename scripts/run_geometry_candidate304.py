"""Fit the G2 candidate under source-only group-safe validation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time

if os.environ.get("CUBLAS_WORKSPACE_CONFIG") not in {None, ":4096:8"}:
    raise RuntimeError("registered deterministic CUDA workspace setting required")
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np

import run_source299 as source299
from fas.feature_cache import digest
from fas.freeze import write_immutable_record
from fas.frozen_features import check_feature, dino_pool, normalize_rgb
from fas.source_diagnostics import budget_split
from fas.source_fitting import identity, partitions, quality_vector
from fas.source_stage import population_counts

CONFIG = ROOT / "configs/source_geometry304_v1.yaml"
GEOMETRY_CONFIG = ROOT / "configs/geometry_candidate304_v1.yaml"
SOURCE_MANIFEST = Path("/mnt/e/FAS-private/artifacts/phase1/source_integration295_v1/source_manifest.json")
CANDIDATE_ROOT = Path("/mnt/e/FAS-private/artifacts/phase1/geometry_candidate304_source_v1")
GENERATION_RECEIPT = CANDIDATE_ROOT / "generation_receipt.json"
OUTPUT = Path("/mnt/e/FAS-private/artifacts/phase1/source_geometry304_v4")
SOURCE_SHA256 = "7f9f54e6b097d7da0618cf8b3784e9eb3726b6aba8a3957455e26dda20da4580"
EXPECTED_SOURCE_CONFIG_SHA256 = "8e1feed43b371f4b07333d8a407f76f22e7ccf366fe93999de5bad42ccfab0b3"
MAX_WALL_SECONDS = 21600
MAX_RSS_BYTES = 12 * 1024**3
MAX_CUDA_BYTES = 12 * 1024**3
MAX_OUTPUT_BYTES = 8 * 1024**3
_LAST_OUTPUT_CHECK = 0.0


def read_json(path: Path) -> dict:
    return json.loads(path.read_bytes())


def source_inputs() -> tuple[list[dict], list[dict], dict]:
    if digest(SOURCE_MANIFEST) != SOURCE_SHA256:
        raise ValueError("accepted source manifest hash changed")
    if digest(source299.CONFIG) != EXPECTED_SOURCE_CONFIG_SHA256:
        raise ValueError("accepted source299 settings changed")
    if digest(GEOMETRY_CONFIG) != read_json(GENERATION_RECEIPT)["config_sha256"]:
        raise ValueError("candidate preprocessing config changed")
    receipt = read_json(GENERATION_RECEIPT)
    if (receipt["status"] != "complete" or receipt["candidate"] != "G2"
            or receipt["source_manifest_sha256"] != SOURCE_SHA256
            or receipt["source_originals_processed"] != 6882
            or receipt["successful_inputs"] != 6855
            or receipt["retained_terminal_failures"] != 27):
        raise ValueError("complete source-only G2 generation receipt required")

    manifest = read_json(SOURCE_MANIFEST)
    entries = {entry["sample_key_sha256"]: entry for entry in receipt["entries"]}
    if len(entries) != 6882:
        raise ValueError("exact G2 source-only row coverage required")
    eligible = sorted(
        (row for row in manifest["rows"] if row["source_use_eligible"]),
        key=identity,
    )
    rows, failures = [], []
    for row in eligible:
        if row["role"] not in {"train", "branch_calibration", "g_domain"}:
            raise ValueError(f"unexpected source role: {identity(row)}")
        key = hashlib.sha256(f"{row['dataset']}\0{row['video_id']}".encode("utf-8")).hexdigest()
        entry = entries.pop(key, None)
        if (entry is None or entry["source_record_sha256"] != row["record_sha256"]
                or entry["role"] != row["role"]):
            raise ValueError(f"candidate transaction join mismatch: {identity(row)}")
        if row["model_input_eligible"]:
            if entry["status"] != "ready" or set(entry["crops"]) != {"224", "518"}:
                raise ValueError(f"candidate crop missing: {identity(row)}")
            row = dict(row)
            row["crops"] = {
                resolution: {
                    "path": str(CANDIDATE_ROOT / entry["crops"][resolution]["path"]),
                    "sha256": entry["crops"][resolution]["sha256"],
                }
                for resolution in ("224", "518")
            }
            rows.append(row)
        else:
            if entry["status"] != "terminal_non_accept" or entry["crops"]:
                raise ValueError(f"source failure disposition changed: {identity(row)}")
            failures.append(row)
    if entries or (len(rows), len(failures)) != (6855, 27):
        raise ValueError("exact source-only success/failure denominator required")
    return rows, failures, manifest


def candidate_features(rows: list[dict], started: float, approval: dict) -> tuple[dict, np.ndarray, dict]:
    import open_clip
    import torch

    runtime = source299.old.runtime()
    accepted_plan = read_json(source299.OUTPUT / "execution_plan.json")
    if runtime != accepted_plan["runtime"]:
        raise ValueError("source299 exact numerical runtime required")
    if not torch.cuda.is_available():
        raise RuntimeError("registered encoder extraction requires CUDA; no CPU fallback")
    torch.set_num_threads(2)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(20260917)
    torch.cuda.set_per_process_memory_fraction(
        MAX_CUDA_BYTES / torch.cuda.get_device_properties(0).total_memory
    )
    sys.path.insert(0, str(source299.old.pilot.UPSTREAM))
    from dinov2.hub import backbones

    pilot_config = source299.read(source299.old.pilot.CONFIG)
    acquisitions = read_json(ROOT / "results/phase1/source-encoder-pilot295-v1.json")["acquisitions"]
    source_extraction_path = source299.old.OUTPUT / "extraction.json"
    source_worker = read_json(source299.old.OUTPUT / "worker_completion.json")
    if digest(source_extraction_path) != source_worker["extraction_sha256"]:
        raise ValueError("accepted fixed prompt embedding receipt changed")
    source_extraction = read_json(source_extraction_path)
    text_path = Path(source_extraction["text"]["path"])
    if digest(text_path) != source_extraction["text"]["sha256"]:
        raise ValueError("accepted fixed prompt embeddings changed")
    text = np.load(text_path, allow_pickle=False)
    prior_path = source299.OUTPUT / "extraction.json"
    prior_worker = read_json(source299.OUTPUT / "worker_completion.json")
    if digest(prior_path) != prior_worker["extraction_sha256"]:
        raise ValueError("accepted source299 encoder contract receipt changed")
    prior = read_json(prior_path)
    feature_dir = OUTPUT / "features"
    feature_dir.mkdir(parents=True, exist_ok=True)
    input_sha256 = digest(OUTPUT / "inputs.json")
    feature_rows: dict[str, np.ndarray] = {}
    extraction_records = {}
    qualities = []
    transactions = []
    for row in rows:
        transaction_path = Path(row["record_path"])
        if digest(transaction_path) != row["record_sha256"]:
            raise ValueError(f"source transaction hash changed: {identity(row)}")
        transactions.append(read_json(transaction_path))
        rgb = source299.old.bound_rgb(row, 224)
        qualities.append(quality_vector(rgb, transactions[-1]))
    quality = np.asarray(qualities, dtype=np.float64)
    quality_path = feature_dir / "quality.npy"
    quality_receipt_path = feature_dir / "quality.json"
    if quality_path.exists() or quality_receipt_path.exists():
        if not quality_path.is_file() or not quality_receipt_path.is_file():
            raise ValueError("partial quality cache is not resumable")
        quality_receipt = read_json(quality_receipt_path)
        if (quality_receipt["inputs_sha256"] != input_sha256
                or quality_receipt["artifact_sha256"] != digest(quality_path)):
            raise ValueError("candidate quality cache binding mismatch")
        quality = np.load(quality_path, allow_pickle=False)
        if quality.shape != (len(rows), 5) or not np.isfinite(quality).all():
            raise ValueError("candidate quality cache shape or finite-value mismatch")
    else:
        np.save(quality_path, quality, allow_pickle=False)
        write_immutable_record(quality_receipt_path, {
            "inputs_sha256": input_sha256,
            "artifact_sha256": digest(quality_path),
            "shape": list(quality.shape),
        })

    for name, spec in pilot_config["models"].items():
        enforce(approval)
        checkpoint_path = source299.old.pilot.NATIVE / "checkpoints" / f"{name}.pth"
        checkpoint_sha = acquisitions[name]["sha256"]
        if digest(checkpoint_path) != checkpoint_sha:
            raise ValueError(f"registered checkpoint hash mismatch: {name}")
        prior_contract = prior[name]["contract"]
        if (prior[name]["checkpoint_sha256"] != checkpoint_sha
                or prior_contract["runtime"] != runtime
                or prior_contract["resolution"] != spec["resolution"]):
            raise ValueError(f"accepted encoder preprocessing contract mismatch: {name}")
        feature_path = feature_dir / f"{name}.npy"
        feature_receipt_path = feature_dir / f"{name}.json"
        if feature_path.exists() or feature_receipt_path.exists():
            if not feature_path.is_file() or not feature_receipt_path.is_file():
                raise ValueError(f"partial {name} feature cache is not resumable")
            saved = read_json(feature_receipt_path)
            if (saved["inputs_sha256"] != input_sha256
                    or saved["checkpoint_sha256"] != checkpoint_sha
                    or saved["runtime"] != runtime
                    or saved["artifact_sha256"] != digest(feature_path)):
                raise ValueError(f"{name} feature cache binding mismatch")
            features = np.load(feature_path, allow_pickle=False)
            check_feature(features, len(rows), spec["feature_dimension"])
            feature_rows[name] = features
            extraction_records[name] = saved
            continue
        if name.startswith("dino"):
            model = getattr(backbones, spec["local_factory"])(pretrained=False)
            model.load_state_dict(
                torch.load(checkpoint_path, map_location="cpu", weights_only=True), strict=True
            )
        else:
            model = open_clip.create_model("ViT-B-16", pretrained=None, precision="fp32")
            incompatible = open_clip.load_checkpoint(
                model, str(checkpoint_path), strict=True, weights_only=True
            )
            if incompatible.missing_keys or incompatible.unexpected_keys:
                raise ValueError("strict OpenCLIP state loading failed")
        model.requires_grad_(False).eval().cuda()
        mean = tuple(prior_contract["normalization_mean"])
        std = tuple(prior_contract["normalization_std"])
        values = []
        torch.cuda.reset_peak_memory_stats()
        for index, row in enumerate(rows):
            enforce(approval)
            rgb = source299.old.bound_rgb(row, spec["resolution"])
            tensor = torch.from_numpy(normalize_rgb(rgb, spec["resolution"], mean, std)[None]).cuda()
            with torch.inference_mode():
                if name.startswith("dino"):
                    output = model.forward_features(tensor)
                    value = dino_pool(
                        output["x_norm_clstoken"].cpu().numpy(),
                        output["x_norm_patchtokens"].cpu().numpy(),
                    )
                    del output
                else:
                    value = model.encode_image(tensor, normalize=True).cpu().numpy()
            del tensor
            check_feature(value, 1, spec["feature_dimension"])
            values.append(value[0])
            if max(torch.cuda.max_memory_allocated(), torch.cuda.max_memory_reserved()) > MAX_CUDA_BYTES:
                raise MemoryError("source geometry304 CUDA cap exceeded")
            if (index + 1) % 500 == 0:
                print(f"features={name} {index + 1}/{len(rows)}", flush=True)
        model.cpu()
        del model
        torch.cuda.empty_cache()
        feature_rows[name] = np.asarray(values, dtype=np.float32)
        check_feature(feature_rows[name], len(rows), spec["feature_dimension"])
        np.save(feature_path, feature_rows[name], allow_pickle=False)
        extraction_records[name] = {
            "inputs_sha256": input_sha256,
            "checkpoint_sha256": checkpoint_sha,
            "runtime": runtime,
            "shape": list(feature_rows[name].shape),
            "feature_sha256": hashlib.sha256(feature_rows[name].tobytes()).hexdigest(),
            "artifact_path": str(feature_path),
            "artifact_sha256": digest(feature_path),
            "forward_count": len(rows),
            "peak_cuda_allocated_bytes": torch.cuda.max_memory_allocated(),
            "peak_cuda_reserved_bytes": torch.cuda.max_memory_reserved(),
        }
        write_immutable_record(feature_receipt_path, extraction_records[name])

    expected_forwards = sum(record["forward_count"] for record in extraction_records.values())
    if expected_forwards != 20565:
        raise ValueError("exact one-pass encoder coverage required")

    for name, features in feature_rows.items():
        check_feature(features, len(rows), pilot_config["models"][name]["feature_dimension"])
    receipt = {
        "version": 1,
        "checkpoint": 304,
        "candidate": "G2",
        "rows_sha256": digest(OUTPUT / "inputs.json"),
        "runtime": runtime,
        "models": extraction_records,
        "quality": {
            "artifact_path": str(quality_path),
            "artifact_sha256": digest(quality_path),
            "shape": list(quality.shape),
        },
        "fixed_prompt_embedding_sha256": source_extraction["text"]["sha256"],
        "target_predictions": False,
        "model_downloads": 0,
        "new_image_forwards": expected_forwards,
        "wall_seconds": time.monotonic() - started,
    }
    extraction_path = OUTPUT / "extraction.json"
    if extraction_path.exists():
        if read_json(extraction_path) != receipt:
            raise ValueError("existing candidate extraction receipt differs")
    else:
        write_immutable_record(extraction_path, receipt)
    return feature_rows, quality, {"text": text, "receipt": receipt}


def output_bytes() -> int:
    return sum(path.stat().st_size for path in OUTPUT.rglob("*") if path.is_file())


def enforce(approval: dict, *, final: bool = False) -> None:
    global _LAST_OUTPUT_CHECK
    deadline = approval["deadline_unix_seconds"]
    if time.time() >= deadline:
        raise TimeoutError("source geometry304 original deadline")
    rss_bytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    if rss_bytes > MAX_RSS_BYTES:
        raise MemoryError("source geometry304 process RSS cap exceeded")
    now = time.monotonic()
    if OUTPUT.exists() and now - _LAST_OUTPUT_CHECK >= 30:
        _LAST_OUTPUT_CHECK = now
        if output_bytes() > MAX_OUTPUT_BYTES:
            raise MemoryError("source geometry304 output-byte cap exceeded")


def prepare_inputs(rows: list[dict], failures: list[dict], manifest: dict) -> dict:
    contexts = []
    for target in ("OULU-NPU", "CASIA-FASD", "MSU-MFSD", "SiW-Mv2"):
        source_rows = [row for row in rows if row["dataset"] != target]
        original_rows = [row for row in manifest["rows"]
                         if row["source_use_eligible"] and row["dataset"] != target]
        for seed in (20260917, 20260923, 20261001):
            splits = partitions(source_rows, target, seed)
            cap = min(len(split["fitting"]) for split in splits if split["name"] != "final")
            indexed = {identity(row): row for row in source_rows}
            sensitivity = [
                budget_split(split, indexed, cap, seed)
                for split in splits if split["name"] != "final"
            ]
            contexts.append({
                "key": f"{target}-{seed}",
                "outer_target": target,
                "seed": seed,
                "row_ids": [identity(row) for row in source_rows],
                "partitions": splits,
                "budget_partitions": sensitivity,
                "budget_cap": cap,
                "original_counts": population_counts(original_rows),
                "reuse297": False,
            })
    return {
        "version": 1,
        "checkpoint": 304,
        "source_use_binding": manifest["source_use_binding"],
        "rows": rows,
        "failure_rows": failures,
        "contexts": contexts,
        "config_sha256": digest(CONFIG),
        "geometry_generation_sha256": digest(GENERATION_RECEIPT),
    }


def execute(*, confirm_source_only: bool) -> dict:
    if not confirm_source_only:
        raise ValueError("explicit --confirm-source-only is required")
    geometry = read_json(GEOMETRY_CONFIG)
    config = read_json(CONFIG)
    inherited_source_config = source299.read(source299.CONFIG)
    if (config["checkpoint"] != 304 or config["candidate"] != "G2"
            or digest(source299.CONFIG) != config["inherited_source_config_sha256"]
            or digest(GEOMETRY_CONFIG) != read_json(GENERATION_RECEIPT)["config_sha256"]
            or geometry["scope"]["target_predictions"] is not False):
        raise ValueError("exact source-only geometry304 config pins required")

    rows, failures, manifest = source_inputs()
    if len(rows) != 6855 or len(failures) != 27:
        raise ValueError("source-only rows must retain exact accepted denominators")
    inputs = prepare_inputs(rows, failures, manifest)
    if OUTPUT.exists():
        if (OUTPUT / "worker_completion.json").exists():
            raise FileExistsError(f"completed source geometry304 output already exists: {OUTPUT}")
        saved_inputs = OUTPUT / "inputs.json"
        if not saved_inputs.is_file() or read_json(saved_inputs) != inputs:
            raise ValueError("existing source geometry304 attempt has different or missing inputs")
    else:
        OUTPUT.mkdir(parents=True, exist_ok=False)
        write_immutable_record(OUTPUT / "inputs.json", inputs)
    started = time.monotonic()
    approval = {
        "started_unix_seconds": time.time(),
        "deadline_unix_seconds": time.time() + MAX_WALL_SECONDS,
    }
    features, quality, extracted = candidate_features(rows, started, approval)
    fit_config_path, output_path, enforce_fn = source299.CONFIG, source299.OUTPUT, source299.enforce
    source299.CONFIG, source299.OUTPUT, source299.enforce = CONFIG, OUTPUT, enforce
    try:
        results = [
            source299.combination(
                context, rows, features, quality, extracted["text"],
                inherited_source_config, source299.read(source299.old.CONFIG), approval,
            )
            for context in inputs["contexts"]
        ]
    finally:
        source299.CONFIG, source299.OUTPUT, source299.enforce = fit_config_path, output_path, enforce_fn
    completion = {
        "version": 1,
        "checkpoint": 304,
        "status": "complete_source_only_exploratory",
        "config_sha256": digest(CONFIG),
        "inputs_sha256": digest(OUTPUT / "inputs.json"),
        "extraction_sha256": digest(OUTPUT / "extraction.json"),
        "combinations": results,
        "combination_count": len(results),
        "source_only": True,
        "independent_target_evidence": False,
        "target_predictions": False,
        "target_tuning": False,
        "locked_evaluation_authorized": False,
        "wall_seconds": time.monotonic() - started,
        "output_bytes": output_bytes(),
        "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
    }
    write_immutable_record(OUTPUT / "worker_completion.json", completion)
    return {
        key: value for key, value in completion.items()
        if key != "combinations"
    } | {"combinations": len(results)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-source-only", action="store_true")
    args = parser.parse_args()
    print(json.dumps(execute(confirm_source_only=args.confirm_source_only), indent=2))


if __name__ == "__main__":
    main()
