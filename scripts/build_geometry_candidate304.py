"""Build source-only G2 square inputs without changing accepted artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from fas.freeze import write_immutable_record
from fas.geometry_candidate import pad_shared_crop

SOURCE_MANIFEST = Path("/mnt/e/FAS-private/artifacts/phase1/source_integration295_v1/source_manifest.json")
EXPECTED_SOURCE_MANIFEST_SHA256 = "7f9f54e6b097d7da0618cf8b3784e9eb3726b6aba8a3957455e26dda20da4580"
EXPECTED_CONFIG_SHA256 = "1943be65c9b1281269b06df1c9ffa87275e7d76d3a7ad455e772e169ee5ad315"
OUTPUT = Path("/mnt/e/FAS-private/artifacts/phase1/geometry_candidate304_source_v1")
CONFIG = ROOT / "configs/geometry_candidate304_v1.yaml"
MAX_WALL_SECONDS = 7200
MAX_RSS_BYTES = 8 * 1024**3
MAX_OUTPUT_BYTES = 16 * 1024**3
EXPECTED_SOURCE_ORIGINALS = 6882
EXPECTED_SUCCESSFUL_INPUTS = 6855
EXPECTED_FAILURES = 27


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_bytes())


def sample_key(row: dict) -> str:
    payload = f"{row['dataset']}\0{row['video_id']}".encode("utf-8")
    return sha256(payload)


def checked_shared_crop(row: dict) -> tuple[np.ndarray, dict]:
    transaction_path = Path(row["record_path"])
    transaction_payload = transaction_path.read_bytes()
    if sha256(transaction_payload) != row["record_sha256"]:
        raise ValueError(f"source transaction hash mismatch: {row['dataset']}:{row['video_id']}")
    transaction = json.loads(transaction_payload)
    if (transaction.get("video_id") != row["video_id"]
            or transaction.get("role") != row["role"]
            or transaction.get("selected_frame") != row["selected_frame"]):
        raise ValueError(f"source transaction join mismatch: {row['dataset']}:{row['video_id']}")
    shared = [path for path in transaction.get("assets", []) if path.endswith("-shared.png")]
    if len(shared) != 1:
        raise ValueError(f"exact shared crop required: {row['dataset']}:{row['video_id']}")
    shared_path = transaction_path.parent.parent / shared[0]
    with Image.open(shared_path) as image:
        if image.mode != "RGB":
            raise ValueError(f"shared crop must be RGB: {row['dataset']}:{row['video_id']}")
        rgb = np.asarray(image).copy()
    if (list(rgb.shape) != transaction.get("crop_shape")
            or sha256(rgb.tobytes()) != transaction.get("crop_RGB_sha256")):
        raise ValueError(f"shared crop pixel hash/shape mismatch: {row['dataset']}:{row['video_id']}")
    return rgb, transaction


def png_payload(rgb: np.ndarray) -> bytes:
    ok, encoded = cv2.imencode(".png", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    if not ok:
        raise RuntimeError("OpenCV failed to encode candidate PNG")
    return encoded.tobytes()


def write_identical_or_new(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"candidate output already exists with different bytes: {path}")
        return
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def current_rss_bytes() -> int:
    # Linux reports ru_maxrss in KiB.
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024


def enforce(started: float, output_bytes: int) -> None:
    if time.monotonic() - started > MAX_WALL_SECONDS:
        raise TimeoutError("geometry candidate 304 wall-time limit exceeded")
    if current_rss_bytes() > MAX_RSS_BYTES:
        raise MemoryError("geometry candidate 304 process RSS limit exceeded")
    if output_bytes > MAX_OUTPUT_BYTES:
        raise MemoryError("geometry candidate 304 output-byte limit exceeded")


def build(*, confirm_source_only: bool, limit: int | None) -> dict:
    if not confirm_source_only:
        raise ValueError("explicit --confirm-source-only is required")
    if sha256(SOURCE_MANIFEST.read_bytes()) != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise ValueError("accepted source manifest hash changed")
    config = read_json(CONFIG)
    if (sha256(CONFIG.read_bytes()) != EXPECTED_CONFIG_SHA256
            or config["checkpoint"] != 304 or config["candidate"] != "G2"):
        raise ValueError("candidate config mismatch")

    manifest = read_json(SOURCE_MANIFEST)
    rows = sorted(
        (row for row in manifest["rows"] if row["source_use_eligible"]),
        key=lambda row: (row["dataset"], row["video_id"]),
    )
    if len(rows) != EXPECTED_SOURCE_ORIGINALS:
        raise ValueError("accepted source-only original denominator changed")
    for row in rows:
        if row["role"] not in {"train", "branch_calibration", "g_domain"}:
            raise ValueError(f"unexpected source role: {row['dataset']}:{row['video_id']}")
    if limit is not None and (type(limit) is not int or limit < 1):
        raise ValueError("limit must be a positive integer")
    selected = rows if limit is None else rows[:limit]
    output = OUTPUT if limit is None else OUTPUT.with_name(f"{OUTPUT.name}_pilot_{limit}")
    if (output / "generation_receipt.json").exists():
        raise FileExistsError(f"completed candidate generation already exists: {output}")

    started = time.monotonic()
    entries = []
    output_bytes = 0
    successful = failed = 0
    for index, row in enumerate(selected, 1):
        is_success = row["model_input_eligible"] is True
        entry = {
            "dataset": row["dataset"],
            "sample_key_sha256": sample_key(row),
            "role": row["role"],
            "source_record_sha256": row["record_sha256"],
            "status": "ready" if is_success else "terminal_non_accept",
            "failure_kind": None if is_success else row["failure_kind"],
            "crops": {},
        }
        if is_success:
            rgb, _ = checked_shared_crop(row)
            for resolution in (224, 518):
                candidate, geometry = pad_shared_crop(rgb, resolution)
                payload = png_payload(candidate)
                relative = Path("crops") / row["dataset"].lower().replace("-", "_") / sample_key(row) / f"{resolution}.png"
                output_path = output / relative
                enforce(started, output_bytes + len(payload))
                write_identical_or_new(output_path, payload)
                output_bytes += len(payload)
                entry["crops"][str(resolution)] = {
                    "path": str(relative),
                    "sha256": sha256(payload),
                    "geometry": geometry,
                }
            successful += 1
        else:
            failed += 1
        entries.append(entry)
        if index % 250 == 0:
            enforce(started, output_bytes)
            print(f"processed={index}/{len(selected)} successful={successful} failures={failed} output_bytes={output_bytes}", flush=True)

    complete = limit is None
    if complete and (successful != EXPECTED_SUCCESSFUL_INPUTS or failed != EXPECTED_FAILURES):
        raise ValueError("source-only success/failure denominator mismatch")
    receipt = {
        "version": 1,
        "checkpoint": 304,
        "status": "complete" if complete else "bounded_pilot",
        "source_manifest_sha256": EXPECTED_SOURCE_MANIFEST_SHA256,
        "config_sha256": sha256(CONFIG.read_bytes()),
        "candidate": "G2",
        "source_originals_processed": len(selected),
        "successful_inputs": successful,
        "retained_terminal_failures": failed,
        "candidate_image_files": successful * 2,
        "candidate_output_bytes": output_bytes,
        "wall_seconds": time.monotonic() - started,
        "peak_rss_bytes": current_rss_bytes(),
        "target_predictions": False,
        "training_or_model_scores": False,
        "entries": entries,
    }
    write_immutable_record(output / "generation_receipt.json", receipt)
    return {key: value for key, value in receipt.items() if key != "entries"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-source-only", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    print(json.dumps(build(confirm_source_only=args.confirm_source_only, limit=args.limit), indent=2))


if __name__ == "__main__":
    main()
