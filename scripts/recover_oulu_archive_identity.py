#!/usr/bin/env python3
"""Rehash frozen OULU archives and propose an additive environment binding."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.oulu import _sha256
from prepare_oulu_owner_review import private_output

ANCHORS = {
    "Dev_files.tar": "3c3a17e0ebbea6d42aaa15d2d43fc9cc257f43372e424f5e5786f4b5a9e2d5f6",
    "Test_files.tar": "2f1f9d752751fdf2d09a763d4f2424cba8ced548800fd4d0bdc189a652274383",
    "Train_files.tar": "966127b8bc11b00215a1a2af530c2345ce50b12a54b59cc717650a0b9236a4d4",
}


def file_identity(value: os.stat_result) -> dict:
    return {"device": value.st_dev, "inode": value.st_ino, "byte_size": value.st_size,
            "mtime_ns": value.st_mtime_ns, "ctime_ns": value.st_ctime_ns}


def rehash_archive(path: Path, expected: dict, old_identity: dict) -> dict:
    started = datetime.now(timezone.utc).isoformat()
    clock = monotonic()
    if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode):
        raise ValueError("regular non-symlink archive required")
    before = file_identity(path.stat())
    if before["byte_size"] != expected["byte_size"]:
        raise ValueError("archive byte size differs from frozen authority")
    with path.open("rb") as source:
        if file_identity(os.fstat(source.fileno())) != before:
            raise ValueError("archive identity changed before hash")
        digest = hashlib.file_digest(source, "sha256").hexdigest()
        after_descriptor = file_identity(os.fstat(source.fileno()))
    if path.is_symlink() or after_descriptor != before or file_identity(path.stat()) != before:
        raise ValueError("archive identity changed during hash")
    if digest != expected["sha256"]:
        raise ValueError("archive whole-file SHA-256 differs from frozen authority")
    old = {**{key: old_identity[key] for key in ("device", "inode", "mtime_ns", "ctime_ns")},
           "byte_size": expected["byte_size"]}
    changed = sorted(key for key in before if before[key] != old[key])
    if changed != ["device"]:
        raise ValueError("recovery scope requires device-only identity drift")
    return {"archive_name": path.name, "frozen_sha256": expected["sha256"], "current_sha256": digest,
            "byte_size": before["byte_size"], "whole_file_read": True, "content_hash_matches_frozen": True,
            "old_file_identity": old_identity, "current_file_identity": before, "changed_fields": changed,
            "stat_identity_stable_during_hash": True, "only_filesystem_environment_identity_changed": True,
            "filesystem_change_cause_independently_established": False,
            "started_at_utc": started, "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": round(monotonic() - clock, 3)}


def verify_preserved(preflight: dict) -> None:
    for name, expected in preflight["protected_snapshots"].items():
        folder = Path(name)
        actual = {str(path.relative_to(folder)): _sha256(path) for path in sorted(folder.rglob("*")) if path.is_file()}
        if actual != expected:
            raise ValueError("protected prior evidence drift")
    for field in ("pinned_file_sha256", "frozen_file_sha256", "study_config_sha256"):
        for name, digest in preflight[field].items():
            if _sha256(Path(name)) != digest:
                raise ValueError("accepted source/config/frozen pin drift")


def recover(args: argparse.Namespace) -> dict:
    private_output(args.out_root, [args.input_root, args.archive_records, args.preflight])
    preflight = json.loads(args.preflight.read_bytes())
    private_output(args.out_root, [Path(name) for name in preflight["protected_snapshots"]])
    verify_preserved(preflight)
    if _sha256(Path(__file__)) != preflight["recovery_code_sha256"]:
        raise ValueError("recovery implementation drift")
    review = ROOT / "docs/176-review-doc175-oulu-batch06-archive-device-blocker.md"
    if _sha256(review) != preflight["review176_sha256"] or preflight["archive_anchor_sha256"] != ANCHORS:
        raise ValueError("Review176 recovery authority drift")
    check = preflight["source175_CI"]
    if check["head_sha"] != "d54f6723f3852bd1a0ef2d8d1862f1799639a0cb" or check["run_id"] != 38669499099 or check["job_id"] != 116209003838 or check["status"] != "completed" or check["conclusion"] != "success":
        raise ValueError("exact successful source175 CI required")
    public_path = ROOT / "results/phase1/oulu-archive-byte-pinning-v1.json"
    if _sha256(public_path) != preflight["archive_pin_report_sha256"]:
        raise ValueError("frozen archive authority drift")
    pins = json.loads(public_path.read_bytes())["media_archives"]
    if {name: pin["sha256"] for name, pin in pins.items()} != ANCHORS:
        raise ValueError("frozen archive content anchors drift")
    old_records = {}
    for name in ANCHORS:
        path = args.archive_records / (name + ".sha256.json")
        if _sha256(path) != pins[name]["private_record_sha256"]:
            raise ValueError("old immutable archive record drift")
        old_records[name] = json.loads(path.read_bytes())
    rows = {}
    for name in ANCHORS:
        print("REHASH START " + name, flush=True)
        row = rehash_archive(args.input_root / name, pins[name], old_records[name]["file_identity"])
        row.update({"old_private_record_sha256": pins[name]["private_record_sha256"],
                    "review176_sha256": preflight["review176_sha256"], "preflight_sha256": _sha256(args.preflight)})
        write_immutable_record(args.out_root / (name + ".rehash.json"), row)
        rows[name] = row
        print("REHASH MATCH " + name, flush=True)
    verify_preserved(preflight)
    for name, row in rows.items():
        path = args.input_root / name
        if path.is_symlink() or file_identity(path.stat()) != row["current_file_identity"]:
            raise ValueError("archive changed before binding")
    binding = {"version": 1, "status": "content_identity_verified_environment_binding_review_pending",
               "review176_sha256": preflight["review176_sha256"], "preflight_sha256": _sha256(args.preflight),
               "archive_pin_report_sha256": _sha256(public_path), "recovery_code_sha256": _sha256(Path(__file__)),
               "source175_CI": check, "archives": rows, "total_bytes_hashed": sum(row["byte_size"] for row in rows.values()),
               "content_authority": "unchanged_frozen_whole_file_SHA256_and_byte_size",
               "environment_identity": "new_stable_device_inode_size_mtime_ctime",
               "old_archive_pins_unchanged": True, "all_prior_inputs_unchanged": True,
               "recovery_checkpoint_review_pending": True, "packet_runner_guard_changed": False,
               "packet_preparation_authorized_by_this_record": False,
               "individual_video_payloads_opened": False, "media_decoding_or_extraction_performed": False,
               "accepted_current_total": 50, "new_AI_human_effective_dispositions": 0,
               "scientific_readiness": False}
    write_immutable_record(args.out_root / "environment_binding.json", binding)
    return binding


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("input-root", "archive-records", "preflight", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        result = recover(parser.parse_args())
    except (OSError, ValueError, KeyError, TypeError):
        print("ARCHIVE RECOVERY FAILED: no environment binding or packet clearance claimed", file=sys.stderr)
        return 1
    print(json.dumps({"status": result["status"], "archives_verified": len(result["archives"]),
                      "total_bytes_hashed": result["total_bytes_hashed"]}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())