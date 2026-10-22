"""One owner-approved full-byte recovery; immutable additive binding only."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import resource
import stat
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.oulu import _sha256
from recover_oulu_archive_identity import ANCHORS, file_identity
from verify_oulu_archive_guard_batch09 import ARCHIVE_SIZES, IDENTITY_FIELDS, read_verified_json, verified_archive_identities

BASE = Path("/mnt/e/FAS-private/artifacts/phase1")
PACKAGE = BASE / "oulu_preprocessing276_v1"
RECOVERY_CAPS = {"wall_seconds": 7200, "rss_bytes": 1024 ** 3, "output_bytes": 16 * 1024 ** 2,
                 "archive_bytes": sum(ARCHIVE_SIZES.values())}


def context() -> tuple[dict, dict]:
    parent = read_verified_json(BASE / "oulu_investigation257_preflight_v1.json",
                                "5021a83530b34cf2bad7051d94a41efea9845a6c54b9b2aac33a81c9d00c9916")
    guard = copy.deepcopy(parent["guard_context"])
    guard["pinned_file_sha256"][str(ROOT / "tests/test_oulu.py")] = _sha256(ROOT / "tests/test_oulu.py")
    return parent, guard


def inherited_guard(input_root: Path, archive_records: Path, guard: dict) -> None:
    try:
        verified_archive_identities(input_root, archive_records, guard)
    except ValueError as error:
        if str(error) != "archive identity drift from accepted219; separate review required":
            raise


def approval() -> dict:
    record = json.loads((PACKAGE / "owner_approval.json").read_bytes())
    if record["explicit_owner_approval"] is not True or record["recovery_caps"] != RECOVERY_CAPS or record["review275_sha256"] != _sha256(ROOT / "docs/275-review-doc274-scrfd-and-pilot-recovery.md"):
        raise ValueError("exact combined275 recovery and pilot authority required")
    return record


def recovered_identities(input_root: Path, archive_records: Path, guard: dict, binding_path: Path, digest: str) -> dict:
    approval()
    inherited_guard(input_root, archive_records, guard)
    binding = read_verified_json(binding_path, digest)
    if binding["approval_sha256"] != _sha256(PACKAGE / "owner_approval.json") or binding["recovery_code_sha256"] != _sha256(Path(__file__)) or binding["caps"] != RECOVERY_CAPS or binding["whole_file_equality"] is not True:
        raise ValueError("recovery authority/code/equality commitment drift")
    if set(binding["archives"]) != set(ANCHORS):
        raise ValueError("exact three recovered archives required")
    old = json.loads(Path(guard["accepted219_binding_path"]).read_bytes())
    if binding["accepted219_binding_sha256"] != _sha256(Path(guard["accepted219_binding_path"])):
        raise ValueError("accepted219 binding drift")
    identities = {}
    for name, row in binding["archives"].items():
        if row != read_verified_json(binding_path.parent / (name + ".rehash.json"), binding["record_sha256"][name]):
            raise ValueError("recovery row binding drift")
        current_stat = (input_root / name).lstat()
        current = file_identity(current_stat)
        accepted = old["archives"][name]["current_file_identity"]
        if row["accepted219_identity"] != accepted or row["current_identity"] != current or row["sha256"] != ANCHORS[name] or row["bytes_read"] != ARCHIVE_SIZES[name] or not stat.S_ISREG(current_stat.st_mode):
            raise ValueError("recovered archive identity or full-byte commitment drift")
        if any(current[key] != accepted[key] for key in IDENTITY_FIELDS if key != "device"):
            raise ValueError("recovery is restricted to device-only transition")
        identities[name] = tuple(current[key] for key in IDENTITY_FIELDS)
    return identities


def recover() -> dict:
    approval()
    parent, guard = context()
    input_root = Path(parent["paths"]["input_root"])
    inherited_guard(input_root, Path(parent["paths"]["archive_records"]), guard)
    old_path = Path(guard["accepted219_binding_path"])
    old = json.loads(old_path.read_bytes())
    output = PACKAGE / "recovery"
    if output.exists():
        raise FileExistsError("one recovery attempt only; no automatic retry")
    started = time.monotonic()
    deadline = started + RECOVERY_CAPS["wall_seconds"]
    write_immutable_record(output / "attempt.json", {"started_unix_seconds": time.time(), "caps": RECOVERY_CAPS,
                           "approval_sha256": _sha256(PACKAGE / "owner_approval.json"),
                           "recovery_code_sha256": _sha256(Path(__file__))})
    total, peak = 0, 0
    rows, pins = {}, {}
    for name in sorted(ANCHORS):
        path = input_root / name
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb", buffering=0) as handle:
            initial_stat = os.fstat(handle.fileno())
            initial = file_identity(initial_stat)
            accepted = old["archives"][name]["current_file_identity"]
            if not stat.S_ISREG(initial_stat.st_mode) or initial != file_identity(path.lstat()) or initial["byte_size"] != ARCHIVE_SIZES[name] or any(initial[key] != accepted[key] for key in IDENTITY_FIELDS if key != "device"):
                raise ValueError("stable device-only regular archive required")
            digest, count = hashlib.sha256(), 0
            while block := handle.read(8 * 1024 ** 2):
                count += len(block)
                total += len(block)
                peak = max(peak, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
                if time.monotonic() >= deadline or peak > RECOVERY_CAPS["rss_bytes"] or count > ARCHIVE_SIZES[name] or total > RECOVERY_CAPS["archive_bytes"]:
                    raise TimeoutError("recovery time/RSS/exact-byte cap")
                digest.update(block)
            if initial != file_identity(os.fstat(handle.fileno())) or initial != file_identity(path.lstat()):
                raise ValueError("archive changed during full-byte recovery")
            if count != ARCHIVE_SIZES[name] or digest.hexdigest() != ANCHORS[name]:
                raise ValueError("archive byte count/hash does not match accepted pin")
        row = {"accepted219_identity": accepted, "current_identity": initial,
               "sha256": digest.hexdigest(), "bytes_read": count, "stable_descriptor_and_path": True}
        record_path = output / (name + ".rehash.json")
        write_immutable_record(record_path, row)
        rows[name], pins[name] = row, _sha256(record_path)
        print("RECOVERY276", name, count, "HASH_MATCH", round(time.monotonic() - started, 3), flush=True)
    if total != RECOVERY_CAPS["archive_bytes"] or time.monotonic() >= deadline:
        raise ValueError("incomplete/late recovery")
    for name, row in rows.items():
        if file_identity((input_root / name).lstat()) != row["current_identity"]:
            raise ValueError("archive changed before binding publication")
    record = {"checkpoint": 276, "approval_sha256": _sha256(PACKAGE / "owner_approval.json"),
              "recovery_code_sha256": _sha256(Path(__file__)), "accepted219_binding_sha256": _sha256(old_path),
              "caps": RECOVERY_CAPS, "archives": rows, "record_sha256": pins, "whole_file_equality": True,
              "bytes_read": total, "rss_peak_bytes": peak, "wall_seconds": time.monotonic() - started,
              "automatic_retry": False, "archive_mutation": False, "model_execution": False}
    if sum(path.stat().st_size for path in output.iterdir()) + len(json.dumps(record).encode()) > RECOVERY_CAPS["output_bytes"]:
        raise ValueError("recovery record cap")
    write_immutable_record(output / "binding.json", record)
    assert json.loads((output / "binding.json").read_bytes()) == record
    print("RECOVERY276_COMPLETE", json.dumps({key:record[key] for key in ("bytes_read", "rss_peak_bytes", "wall_seconds")}), flush=True)
    return record


if __name__ == "__main__":
    recover()