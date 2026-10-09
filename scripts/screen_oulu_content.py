#!/usr/bin/env python3
"""Private model-free OULU content candidate screening from pinned media."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from collections import Counter
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import cv2
import numpy as np

from fas.content import candidate_pairs, fingerprint_video
from fas.freeze import write_immutable_record
from fas.oulu import _sha256


def screen(args: argparse.Namespace) -> dict:
    inputs, source, frozen, output = (path.resolve() for path in (args.input_root, args.audit_root, args.frozen_root, args.out_root))
    if args.out_root.exists() or args.out_root.is_symlink() or not all(path.is_dir() for path in (inputs, source, frozen)):
        raise ValueError("missing input or existing output")
    if any(output.is_relative_to(path) or path.is_relative_to(output) for path in (ROOT, inputs, source, frozen, args.archive_records.resolve())):
        raise ValueError("unsafe private output boundary")
    if not 1 <= args.workers <= 8:
        raise ValueError("invalid workers")
    report_path = ROOT / "results/phase1/oulu-per-video-media-audit-v1.json"
    accepted = json.loads(report_path.read_bytes())
    if _sha256(source / "summary.json") != accepted["private_summary_sha256"]:
        raise ValueError("accepted summary drift")
    paths = sorted((source / "videos").glob("*.json"))
    bundle = hashlib.sha256("".join(f"{path.stem}:{_sha256(path)}\n" for path in paths).encode()).hexdigest()
    if len(paths) != 4950 or bundle != accepted["video_record_bundle_sha256"]:
        raise ValueError("accepted media bundle drift")
    frozen_hashes = {path.name: _sha256(path) for path in frozen.iterdir()}
    if frozen_hashes != accepted["frozen_artifact_sha256"]:
        raise ValueError("frozen input drift")
    media = {path.stem: json.loads(path.read_bytes()) for path in paths}
    if any(identity != row["video_id"] for identity, row in media.items()):
        raise ValueError("media identity mismatch")
    pin_path = ROOT / "results/phase1/oulu-archive-byte-pinning-v1.json"
    pins = json.loads(pin_path.read_bytes())
    identities = {}
    for name, pin in pins["media_archives"].items():
        record_path = args.archive_records / (name + ".sha256.json")
        if _sha256(record_path) != pin["private_record_sha256"]:
            raise ValueError("archive record drift")
        record = json.loads(record_path.read_bytes())["file_identity"]
        stat = (inputs / name).stat()
        actual = (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
        if actual != (record["device"], record["inode"], pin["byte_size"], record["mtime_ns"], record["ctime_ns"]):
            raise ValueError("archive identity drift")
        identities[name] = actual
    version = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    if version != json.loads((ROOT / "configs/environment_v1.yaml").read_bytes())["host_tools"]["ffmpeg_version_line"]:
        raise ValueError("research FFmpeg mismatch")
    policy_path = ROOT / "configs/content_screening_v1.yaml"
    lineage = {"version": 1, "policy": json.loads(policy_path.read_bytes()), "policy_sha256": _sha256(policy_path),
               "review_sha256": _sha256(ROOT / "docs/110-review-doc109-transaction-selector-freeze.md"),
               "accepted_media_report_sha256": _sha256(report_path), "media_record_bundle_sha256": bundle,
               "archive_pin_report_sha256": _sha256(pin_path), "frozen_artifact_sha256": frozen_hashes,
               "fingerprint_code_sha256": _sha256(ROOT / "src/fas/content.py"), "runner_sha256": _sha256(Path(__file__)),
               "transaction_policy_sha256": _sha256(ROOT / "configs/transaction_policy_v1.yaml"),
               "preprocessing_sha256": _sha256(ROOT / "configs/preprocessing_v2.yaml"),
               "ffmpeg": version, "opencv": cv2.__version__, "numpy": np.__version__,
               "model_execution_authorized": False, "scientific_readiness": False}
    write_immutable_record(output / "lineage.json", lineage)
    completed = []

    def finish(row: dict, temporary: tempfile.TemporaryDirectory | None, path: Path) -> dict:
        try:
            if temporary is not None and (_sha256(path) != row["media_sha256"] or path.stat().st_size != row["byte_size"]):
                raise ValueError("accepted payload identity drift")
            record = {"video_id": row["video_id"], "role": row["role"], "official_split": row["official_split"],
                      "binary_label": row["binary_label"], "media_sha256": row["media_sha256"],
                      "decoded_rgb_sequence_sha256": row["decoded_rgb_sequence_sha256"],
                      "accepted_media_record_sha256": _sha256(source / "videos" / (row["video_id"] + ".json")),
                      **fingerprint_video(path, row)}
            write_immutable_record(output / "fingerprints" / (row["video_id"] + ".json"), record)
            return record
        finally:
            if temporary is not None:
                temporary.cleanup()

    def collect(pending: set) -> set:
        done, remaining = wait(pending, return_when=FIRST_COMPLETED)
        completed.extend(future.result() for future in done)
        if len(completed) // 100 > (len(completed) - len(done)) // 100:
            print(f"FINGERPRINTS {len(completed)}/4950", flush=True)
        return remaining

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        pending = set()
        for name in sorted(pins["media_archives"]):
            with tarfile.open(inputs / name, "r:") as archive:
                members = {member.name: member for member in archive.getmembers()}
                for row in sorted((row for row in media.values() if row["media_archive"] == name), key=lambda row: row["video_id"]):
                    if len(pending) >= args.workers:
                        pending = collect(pending)
                    if row["decode_status"] != "decoded":
                        completed.append(finish(row, None, inputs / name))
                        continue
                    member = members[row["media_relpath"]]
                    if not member.isfile() or member.size != row["byte_size"]:
                        raise ValueError("archive payload metadata drift")
                    temporary = tempfile.TemporaryDirectory(prefix="fas-content-", dir=output)
                    try:
                        path = Path(temporary.name) / "media.avi"
                        with archive.extractfile(member) as handle, path.open("wb") as target:
                            shutil.copyfileobj(handle, target, length=1024 * 1024)
                        pending.add(executor.submit(finish, row, temporary, path))
                    except BaseException:
                        temporary.cleanup()
                        raise
            print(f"ARCHIVE READ COMPLETE {name}", flush=True)
        while pending:
            pending = collect(pending)
    if len(completed) != 4950 or {row["video_id"] for row in completed} != set(media):
        raise ValueError("fingerprint population mismatch")
    counts = Counter()
    chunks, batch = [], []
    for pair in candidate_pairs(completed):
        left, right = media[pair["left"]], media[pair["right"]]
        exact = left["media_sha256"] == right["media_sha256"] or left["decoded_rgb_sequence_sha256"] == right["decoded_rgb_sequence_sha256"]
        pair.update(exact_full_video_evidence=exact, cross_role=left["role"] != right["role"],
                    cross_partition=left["official_split"] != right["official_split"], conflicting_label=left["binary_label"] != right["binary_label"])
        counts["candidate_pairs"] += 1
        counts["known_exact_pairs" if exact else "unresolved_nonexact_pairs"] += 1
        for key in ("cross_role", "cross_partition", "conflicting_label"):
            counts[key + "_candidate_pairs"] += pair[key]
            counts[key + "_unresolved_nonexact_pairs"] += pair[key] and not exact
        batch.append(pair)
        if len(batch) == 10000:
            target = output / "pairs" / f"{len(chunks):06d}.json"
            write_immutable_record(target, {"pairs": batch})
            chunks.append({"name": target.name, "sha256": _sha256(target)})
            batch = []
    if batch:
        target = output / "pairs" / f"{len(chunks):06d}.json"
        write_immutable_record(target, {"pairs": batch})
        chunks.append({"name": target.name, "sha256": _sha256(target)})
    if {path.name: _sha256(path) for path in frozen.iterdir()} != frozen_hashes or _sha256(policy_path) != lineage["policy_sha256"]:
        raise ValueError("frozen inputs changed during screening")
    for name, expected in identities.items():
        stat = (inputs / name).stat()
        if (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns) != expected:
            raise ValueError("archive changed during screening")
    record_paths = sorted((output / "fingerprints").glob("*.json"))
    result = {"version": 1, "status": "screening_complete_lineage_adjudication_pending", "original_population": 4950,
              "fingerprinted_videos": sum(row["status"] == "fingerprinted" for row in completed),
              "unavailable_decode_failures": sum(row["status"] != "fingerprinted" for row in completed),
              "all_successful_unordered_pairs_compared": 4949 * 4948 // 2,
              "candidate_counts": dict(sorted(counts.items())), "candidate_chunks": chunks,
              "fingerprint_bundle_sha256": hashlib.sha256("".join(f"{path.stem}:{_sha256(path)}\n" for path in record_paths).encode()).hexdigest(),
              "lineage_sha256": _sha256(output / "lineage.json"), "frame_pixels_persisted": False,
              "frozen_inputs_unchanged": True, "model_or_detector_executed": False,
              "near_duplicate_lineage_certified": False, "scientific_readiness": False}
    write_immutable_record(output / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for flag in ("input-root", "audit-root", "frozen-root", "archive-records", "out-root"):
        parser.add_argument("--" + flag, type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    try:
        print(json.dumps(screen(parser.parse_args()), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError, tarfile.TarError):
        print("CONTENT SCREEN FAILED: inspect private partial evidence; no completion claimed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())