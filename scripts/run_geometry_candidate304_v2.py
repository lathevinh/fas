"""Uniformly rerun G2 source-only analysis with the pinned line-search amendment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np

import run_geometry_candidate304 as base
from fas import source_experiment
from fas.feature_cache import digest
from fas.freeze import write_immutable_record
from fas.frozen_features import check_feature
from fas.geometry_candidate import fit_source_risk_candidate
from fas.source_fitting import identity

CONFIG = ROOT / "configs/source_geometry304_v2.yaml"
FEATURE_CACHE = Path("/mnt/e/FAS-private/artifacts/phase1/source_geometry304_v4")
OUTPUT = Path("/mnt/e/FAS-private/artifacts/phase1/source_geometry304_v5")
MAX_WALL_SECONDS = 21600
MAX_RSS_BYTES = 12 * 1024**3
MAX_OUTPUT_BYTES = 8 * 1024**3
_LAST_OUTPUT_CHECK = 0.0


def read_json(path: Path) -> dict:
    return json.loads(path.read_bytes())


def output_bytes() -> int:
    return sum(path.stat().st_size for path in OUTPUT.rglob("*") if path.is_file())


def enforce(approval: dict, *, final: bool = False) -> None:
    global _LAST_OUTPUT_CHECK
    if time.time() >= approval["deadline_unix_seconds"]:
        raise TimeoutError("source geometry304 v2 original deadline")
    if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024 > MAX_RSS_BYTES:
        raise MemoryError("source geometry304 v2 process RSS cap exceeded")
    now = time.monotonic()
    if OUTPUT.exists() and now - _LAST_OUTPUT_CHECK >= 30:
        _LAST_OUTPUT_CHECK = now
        if output_bytes() > MAX_OUTPUT_BYTES:
            raise MemoryError("source geometry304 v2 output-byte cap exceeded")


def load_verified_features(rows: list[dict], started: float, approval: dict) -> tuple[dict, np.ndarray, dict]:
    enforce(approval)
    cfg = read_json(CONFIG)
    cache_cfg = cfg["verified_candidate_feature_cache"]
    cache_extraction_path = FEATURE_CACHE / "extraction.json"
    if digest(cache_extraction_path) != cache_cfg["extraction_sha256"]:
        raise ValueError("verified candidate feature extraction receipt changed")
    cache_extraction = read_json(cache_extraction_path)
    cache_inputs = read_json(FEATURE_CACHE / "inputs.json")
    if (cache_extraction["candidate"] != "G2"
            or cache_extraction["rows_sha256"] != digest(FEATURE_CACHE / "inputs.json")
            or cache_extraction["new_image_forwards"] != 20565
            or [identity(row) for row in cache_inputs["rows"]] != [identity(row) for row in rows]):
        raise ValueError("exact complete G2 feature-cache sample join required")

    expected_hashes = {
        "dino_reg": cache_cfg["dino_reg_sha256"],
        "dino_plain": cache_cfg["dino_plain_sha256"],
        "openclip": cache_cfg["openclip_sha256"],
    }
    features = {}
    model_records = {}
    for name in ("dino_reg", "dino_plain", "openclip"):
        path = FEATURE_CACHE / "features" / f"{name}.npy"
        record = cache_extraction["models"][name]
        if (digest(path) != expected_hashes[name]
                or record["artifact_sha256"] != expected_hashes[name]
                or record["forward_count"] != len(rows)):
            raise ValueError(f"{name} candidate features do not match the pinned cache")
        values = np.load(path, allow_pickle=False)
        check_feature(values, len(rows), {"dino_reg": 1536, "dino_plain": 1536, "openclip": 512}[name])
        if hashlib.sha256(values.tobytes()).hexdigest() != record["feature_sha256"]:
            raise ValueError(f"{name} candidate feature payload hash mismatch")
        features[name] = values
        model_records[name] = {
            **record,
            "reused_from": str(path),
            "source_cache_sha256": expected_hashes[name],
        }

    quality_path = FEATURE_CACHE / "features" / "quality.npy"
    quality_hash = cache_cfg["quality_sha256"]
    quality = np.load(quality_path, allow_pickle=False)
    if (digest(quality_path) != quality_hash or quality.shape != (len(rows), 5)
            or not np.isfinite(quality).all()):
        raise ValueError("candidate quality cache mismatch")

    old_extraction_path = base.source299.old.OUTPUT / "extraction.json"
    old_worker = read_json(base.source299.old.OUTPUT / "worker_completion.json")
    if digest(old_extraction_path) != old_worker["extraction_sha256"]:
        raise ValueError("accepted fixed prompt embedding receipt changed")
    old_extraction = read_json(old_extraction_path)
    text_path = Path(old_extraction["text"]["path"])
    if digest(text_path) != old_extraction["text"]["sha256"]:
        raise ValueError("accepted fixed prompt embeddings changed")
    text = np.load(text_path, allow_pickle=False)

    receipt = {
        "version": 2,
        "checkpoint": 304,
        "candidate": "G2",
        "rows_sha256": digest(OUTPUT / "inputs.json"),
        "source_feature_cache_sha256": cache_cfg["extraction_sha256"],
        "runtime": cache_extraction["runtime"],
        "models": model_records,
        "quality": {
            "artifact_path": str(quality_path),
            "artifact_sha256": quality_hash,
            "shape": list(quality.shape),
        },
        "fixed_prompt_embedding_sha256": old_extraction["text"]["sha256"],
        "target_predictions": False,
        "model_downloads": 0,
        "new_image_forwards": 0,
        "wall_seconds": time.monotonic() - started,
    }
    receipt_path = OUTPUT / "extraction.json"
    if receipt_path.exists():
        saved_receipt = read_json(receipt_path)
        if ({key: value for key, value in saved_receipt.items() if key != "wall_seconds"}
                != {key: value for key, value in receipt.items() if key != "wall_seconds"}):
            raise ValueError("resumed geometry304 v2 extraction receipt differs")
        receipt = saved_receipt
    else:
        write_immutable_record(receipt_path, receipt)
    return features, quality, {"text": text, "receipt": receipt}


def _execute(*, confirm_source_only: bool) -> dict:
    if not confirm_source_only:
        raise ValueError("explicit --confirm-source-only is required")
    cfg = read_json(CONFIG)
    base.CONFIG = CONFIG
    base.OUTPUT = OUTPUT
    geometry = read_json(base.GEOMETRY_CONFIG)
    if (cfg["checkpoint"] != 304 or cfg["candidate"] != "G2"
            or digest(base.SOURCE_MANIFEST) != cfg["source_manifest_sha256"]
            or digest(base.GEOMETRY_CONFIG) != cfg["geometry_config_sha256"]
            or digest(base.GENERATION_RECEIPT) != cfg["geometry_generation_receipt_sha256"]
            or digest(base.source299.CONFIG) != cfg["inherited_source_config_sha256"]
            or geometry["scope"]["target_predictions"] is not False
            or cfg["risk_optimizer"]["maxls"] != 50):
        raise ValueError("exact geometry304 v2 pins required")

    rows, failures, manifest = base.source_inputs()
    inputs = base.prepare_inputs(rows, failures, manifest)
    if OUTPUT.exists():
        if (OUTPUT / "worker_completion.json").exists():
            raise FileExistsError(f"completed geometry304 v2 output already exists: {OUTPUT}")
        if not (OUTPUT / "inputs.json").is_file() or read_json(OUTPUT / "inputs.json") != inputs:
            raise ValueError("existing geometry304 v2 attempt has different inputs")
    else:
        OUTPUT.mkdir(parents=True, exist_ok=False)
        write_immutable_record(OUTPUT / "inputs.json", inputs)

    started = time.monotonic()
    approval = {
        "started_unix_seconds": time.time(),
        "deadline_unix_seconds": time.time() + MAX_WALL_SECONDS,
    }
    features, quality, extracted = load_verified_features(rows, started, approval)
    fit_config_path, output_path, enforce_fn = (
        base.source299.CONFIG, base.source299.OUTPUT, base.source299.enforce
    )
    original_fit_risk = source_experiment.fit_risk
    base.source299.CONFIG, base.source299.OUTPUT, base.source299.enforce = (
        CONFIG, OUTPUT, enforce
    )
    source_experiment.fit_risk = fit_source_risk_candidate
    try:
        inherited_source_config = base.source299.read(base.source299.old.CONFIG)
        source_config = base.source299.read(ROOT / "configs/source_run299_v1.yaml")
        results = []
        for context in inputs["contexts"]:
            enforce(approval)
            results.append(base.source299.combination(
                context, rows, features, quality, extracted["text"],
                source_config, inherited_source_config, approval,
            ))
    finally:
        source_experiment.fit_risk = original_fit_risk
        base.source299.CONFIG, base.source299.OUTPUT, base.source299.enforce = (
            fit_config_path, output_path, enforce_fn
        )
    completion = {
        "version": 2,
        "checkpoint": 304,
        "status": "complete_source_only_exploratory",
        "config_sha256": digest(CONFIG),
        "inputs_sha256": digest(OUTPUT / "inputs.json"),
        "extraction_sha256": digest(OUTPUT / "extraction.json"),
        "combinations": results,
        "combination_count": len(results),
        "risk_optimizer": cfg["risk_optimizer"],
        "source_only": True,
        "independent_target_evidence": False,
        "target_predictions": False,
        "target_tuning": False,
        "locked_evaluation_authorized": False,
        "wall_seconds": time.monotonic() - started,
        "output_bytes": output_bytes(),
        "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
    }
    completion_path = OUTPUT / "worker_completion.json"
    if completion_path.exists():
        if read_json(completion_path) != completion:
            raise ValueError("resumed geometry304 v2 completion differs")
    else:
        write_immutable_record(completion_path, completion)
    return {
        "status": completion["status"],
        "combination_count": completion["combination_count"],
        "wall_seconds": completion["wall_seconds"],
        "output_bytes": completion["output_bytes"],
        "peak_rss_bytes": completion["peak_rss_bytes"],
    }


def execute(*, confirm_source_only: bool) -> dict:
    original_config, original_output = base.CONFIG, base.OUTPUT
    try:
        return _execute(confirm_source_only=confirm_source_only)
    finally:
        base.CONFIG, base.OUTPUT = original_config, original_output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-source-only", action="store_true")
    args = parser.parse_args()
    print(json.dumps(execute(confirm_source_only=args.confirm_source_only), indent=2))


if __name__ == "__main__":
    main()
