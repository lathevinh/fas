#!/usr/bin/env python3
"""Audit supplied OULU payloads without changing frozen research inputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from collections import Counter, defaultdict
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.media import probe_video
from fas.oulu import _sha256, inventory_archives


def audit(args: argparse.Namespace) -> dict:
    inputs = args.input_root.resolve()
    frozen = args.frozen_root.resolve()
    output = args.out_root.resolve()
    if not inputs.is_dir() or not frozen.is_dir() or args.out_root.exists():
        raise ValueError("missing input or existing output")
    if any(output.is_relative_to(path) or path.is_relative_to(output) for path in (ROOT, inputs, frozen)):
        raise ValueError("unsafe output boundary")
    if not 1 <= args.workers <= 8:
        raise ValueError("invalid worker count")
    pin_path = ROOT / "results/phase1/oulu-archive-byte-pinning-v1.json"
    pins = json.loads(pin_path.read_bytes())
    archive_records = Path(args.archive_records).resolve()
    identities = {}
    for name, pin in pins["media_archives"].items():
        private_record = archive_records / (name + ".sha256.json")
        if _sha256(private_record) != pin["private_record_sha256"]:
            raise ValueError("archive record drift")
        record = json.loads(private_record.read_bytes())
        stat = (inputs / name).stat()
        identity = record["file_identity"]
        actual = (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
        if actual != (identity["device"], identity["inode"], pin["byte_size"], identity["mtime_ns"], identity["ctime_ns"]):
            raise ValueError("pinned archive identity drift")
        identities[name] = actual
    frozen_hashes = {path.name: _sha256(path) for path in frozen.iterdir()}
    approved = json.loads((ROOT / "results/phase1/source-role-freeze-verification-v2.json").read_bytes())
    if frozen_hashes != approved["private_frozen_bundle_artifact_sha256"]:
        raise ValueError("frozen artifact drift")
    canonical = json.loads((frozen / "oulu_npu_canonical.json").read_bytes())
    videos = {row["video_id"]: row for row in canonical["videos"]}
    first = next(iter(videos.values()))
    inventory = inventory_archives(inputs, release_id=first["release_id"], protocol_id=first["protocol_id"], require_full_release=True)
    if len(videos) != 4950 or len(inventory["videos"]) != 4950:
        raise ValueError("population mismatch")
    if not all(all(videos[row["video_id"]][key] == value for key, value in row.items()) for row in inventory["videos"]):
        raise ValueError("canonical metadata drift")
    with (frozen / "oulu_npu_roles.csv").open(newline="") as source:
        role_rows = list(csv.DictReader(source))
    roles = {row["video_id"]: row for row in role_rows}
    if len(roles) != len(role_rows) or set(roles) != set(videos):
        raise ValueError("role population mismatch")
    if any(roles[name]["binary_label"] != row["binary_label"] or roles[name]["subject_id"] != row["subject_id"] for name, row in videos.items()):
        raise ValueError("role identity mismatch")
    tools = {name: subprocess.run([name, "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0] for name in ("ffmpeg", "ffprobe")}
    environment = json.loads((ROOT / "configs/environment_v1.yaml").read_bytes())
    if tools["ffmpeg"] != environment["host_tools"]["ffmpeg_version_line"]:
        raise ValueError("FFmpeg lock mismatch")
    lineage = {"archive_pin_report_sha256": _sha256(pin_path), "frozen_artifact_sha256": frozen_hashes,
               "tools": tools, "media_probe_sha256": _sha256(ROOT / "src/fas/media.py"),
               "runner_sha256": _sha256(Path(__file__)), "preprocessing_sha256": _sha256(ROOT / "configs/preprocessing_v2.yaml")}
    write_immutable_record(output / "lineage.json", lineage)
    completed = []

    def finish(row: dict, temporary: tempfile.TemporaryDirectory, path: Path, media_hash: str) -> dict:
        try:
            record = {"video_id": row["video_id"], "official_split": row["official_split"],
                      "role": roles[row["video_id"]]["role"], "binary_label": row["binary_label"],
                      "media_archive": row["media_archive"], "media_relpath": row["media_relpath"],
                      "byte_size": row["byte_size"], "media_sha256": media_hash,
                      "archive_sha256": pins["media_archives"][row["media_archive"]]["sha256"],
                      "interval_scope": "whole_supplied_video_no_temporal_bounds_in_accepted_metadata",
                      **probe_video(path)}
            write_immutable_record(output / "videos" / (row["video_id"] + ".json"), record)
            return {key: value for key, value in record.items() if key != "frame_index"}
        finally:
            temporary.cleanup()

    def collect(pending: set) -> set:
        done, remaining = wait(pending, return_when=FIRST_COMPLETED)
        for future in done:
            completed.append(future.result())
            if len(completed) % 50 == 0:
                print(f"PROGRESS {len(completed)}/4950; failed={sum(row['decode_status'] != 'decoded' for row in completed)}", flush=True)
        return remaining

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        pending = set()
        for name in sorted(pins["media_archives"]):
            with tarfile.open(inputs / name, "r:") as archive:
                members = {member.name: member for member in archive.getmembers()}
                for row in sorted((row for row in videos.values() if row["media_archive"] == name), key=lambda row: row["video_id"]):
                    if len(pending) >= args.workers:
                        pending = collect(pending)
                    member = members[row["media_relpath"]]
                    if not member.isfile() or member.size != row["byte_size"]:
                        raise ValueError("payload metadata mismatch")
                    temporary = tempfile.TemporaryDirectory(prefix="fas-oulu-media-")
                    try:
                        path = Path(temporary.name) / "media.avi"
                        with archive.extractfile(member) as source, path.open("wb") as target:
                            shutil.copyfileobj(source, target, length=1024 * 1024)
                        if path.stat().st_size != row["byte_size"]:
                            raise ValueError("payload size mismatch")
                        pending.add(executor.submit(finish, row, temporary, path, _sha256(path)))
                    except BaseException:
                        temporary.cleanup()
                        raise
            print(f"READ COMPLETE {name}", flush=True)
        while pending:
            pending = collect(pending)
    if len(completed) != 4950 or {row["video_id"] for row in completed} != set(videos):
        raise ValueError("incomplete media audit")
    if {path.name: _sha256(path) for path in frozen.iterdir()} != frozen_hashes:
        raise ValueError("frozen artifact changed during audit")
    for name, expected in identities.items():
        stat = (inputs / name).stat()
        if (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns) != expected:
            raise ValueError("archive changed during audit")
    groups = []
    for field in ("media_sha256", "decoded_rgb_sequence_sha256"):
        buckets = defaultdict(list)
        for row in completed:
            if row[field] is not None:
                buckets[row[field]].append(row)
        for value, rows in sorted(buckets.items()):
            if len(rows) > 1:
                groups.append({"identity_type": field, "sha256": value, "video_ids": sorted(row["video_id"] for row in rows),
                               "roles": sorted({row["role"] for row in rows}), "partitions": sorted({row["official_split"] for row in rows})})
    write_immutable_record(output / "duplicate_groups.json", {"groups": groups})
    summary = {"version": 1, "status": "per_video_audit_completed_scientific_readiness_pending", "videos": len(completed),
               "decode_counts": dict(Counter(row["decode_status"] for row in completed)),
               "codecs": dict(Counter(str(row["codec"]) for row in completed)),
               "frame_count_min": min(row["frame_count"] for row in completed), "frame_count_max": max(row["frame_count"] for row in completed),
               "exact_duplicate_groups": dict(Counter(row["identity_type"] for row in groups)),
               "cross_role_duplicate_groups": sum(len(row["roles"]) > 1 for row in groups),
               "cross_partition_duplicate_groups": sum(len(row["partitions"]) > 1 for row in groups),
               "middle_decoded_candidates_available": sum(bool(row["middle_decoded_candidates"]) for row in completed),
               "per_video_hashes_complete": True, "frozen_inputs_unchanged": True,
               "near_duplicate_audit_complete": False, "cross_dataset_duplicate_audit_complete": False,
               "detector_or_model_execution": False, "scientific_readiness": False,
               "lineage_sha256": _sha256(output / "lineage.json"),
               "duplicate_groups_sha256": _sha256(output / "duplicate_groups.json"),
               "video_record_bundle_sha256": hashlib.sha256("".join(f"{row['video_id']}:{_sha256(output / 'videos' / (row['video_id'] + '.json'))}\n" for row in sorted(completed, key=lambda row: row["video_id"])).encode()).hexdigest()}
    write_immutable_record(output / "summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--frozen-root", type=Path, required=True)
    parser.add_argument("--archive-records", type=Path, required=True)
    parser.add_argument("--out-root", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    try:
        print(json.dumps(audit(args), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError, tarfile.TarError):
        print("OULU MEDIA AUDIT FAILED: inspect private partial evidence; no completion claimed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())