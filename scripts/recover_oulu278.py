"""Additional owner-approved device-only remount recovery, without historical replay."""

from __future__ import annotations

import json
import os
import resource
import stat
import time
from pathlib import Path

from recover_oulu276 import ANCHORS, ARCHIVE_SIZES, RECOVERY_CAPS, file_identity
from fas.freeze import write_immutable_record
from fas.oulu import _sha256
from verify_oulu_archive_guard_batch09 import read_verified_json

ROOT = Path(__file__).resolve().parents[1]
BASE = Path("/mnt/e/FAS-private/artifacts/phase1")
OUTPUT = BASE / "oulu_preprocessing278_v1"
PILOT = BASE / "oulu_preprocessing276_v1"
APPROVAL = (
    "Phê duyệt một recovery bổ sung: đọc tuần tự đúng 105.116.817.408 byte, "
    "tối đa 120 phút/1 GiB RSS/16 MiB records; chỉ khi hash khớp mới chạy batch "
    "2.938 mẫu với cap 6 giờ/4 GiB/24 GiB tổng đã duyệt; không retry"
)


def accepted_binding() -> tuple[dict, dict]:
    report = json.loads((ROOT / "results/phase1/oulu-preprocessing276-recovery-pilot-v1.json").read_bytes())
    pins = report["private_record_sha256"]
    plan = read_verified_json(PILOT / "plan.json", pins["plan.json"])
    binding = read_verified_json(PILOT / "recovery/binding.json", pins["recovery/binding.json"])
    if binding["whole_file_equality"] is not True or binding["bytes_read"] != sum(ARCHIVE_SIZES.values()):
        raise ValueError("accepted276 full-byte equality required")
    for name, row in binding["archives"].items():
        if row != read_verified_json(PILOT / "recovery" / (name + ".rehash.json"), binding["record_sha256"][name]):
            raise ValueError("accepted276 recovery row drift")
        if row["sha256"] != ANCHORS[name] or row["bytes_read"] != ARCHIVE_SIZES[name]:
            raise ValueError("accepted276 exact content commitments required")
    if set(binding["archives"]) != set(ANCHORS):
        raise ValueError("exact accepted three archives required")
    return plan, binding


def authority() -> dict:
    record = json.loads((OUTPUT / "owner_approval.json").read_bytes())
    if record["explicit_owner_approval"] is not True or record["recovery_selected_answer"] != APPROVAL or record["recovery_caps"] != RECOVERY_CAPS:
        raise ValueError("exact additional remount recovery approval required")
    if record["review277_sha256"] != _sha256(ROOT / "docs/277-review-doc276-recovery-and-preprocessing-pilot.md"):
        raise ValueError("review277 authority drift")
    return record


def check_device_only(current: dict, accepted: dict) -> None:
    if any(current[key] != value for key, value in accepted.items() if key != "device"):
        raise ValueError("only device-only remount is authorized; other identity drift")


def recover() -> dict:
    import hashlib

    approval = authority()
    plan, accepted = accepted_binding()
    folder = OUTPUT / "recovery"
    started = time.monotonic()
    deadline = approval["recovery_deadline_unix_seconds"]
    approval_sha = _sha256(OUTPUT / "owner_approval.json")
    code_sha = _sha256(Path(__file__))
    write_immutable_record(folder / "attempt.json", {
        "approval_sha256": approval_sha,
        "runner_sha256": code_sha, "automatic_retry": False,
        "started_unix_seconds": time.time(), "caps": RECOVERY_CAPS})
    rows, pins, total, peak = {}, {}, 0, 0
    for name in sorted(ANCHORS):
        path = Path(plan["paths"]["input_root"]) / name
        old = accepted["archives"][name]["current_identity"]
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb", buffering=0) as handle:
            initial_stat = os.fstat(handle.fileno())
            initial = file_identity(initial_stat)
            check_device_only(initial, old)
            if not stat.S_ISREG(initial_stat.st_mode) or initial != file_identity(path.lstat()):
                raise ValueError("stable regular non-symlink archive required")
            digest, count, next_progress = hashlib.sha256(), 0, 1024 ** 3
            while block := handle.read(8 * 1024 ** 2):
                count += len(block)
                total += len(block)
                peak = max(peak, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
                if time.time() >= deadline or peak > RECOVERY_CAPS["rss_bytes"] or count > ARCHIVE_SIZES[name] or total > RECOVERY_CAPS["archive_bytes"]:
                    raise TimeoutError("recovery time/RSS/exact-byte cap; no retry")
                digest.update(block)
                if count >= next_progress:
                    print("RECOVERY278_PROGRESS", name, count, total, round(time.monotonic() - started, 3), flush=True)
                    next_progress += 1024 ** 3
            if initial != file_identity(os.fstat(handle.fileno())) or initial != file_identity(path.lstat()):
                raise ValueError("archive changed during recovery")
            if count != ARCHIVE_SIZES[name] or digest.hexdigest() != ANCHORS[name]:
                raise ValueError("accepted archive content hash/byte mismatch")
        row = {"accepted276_identity": old, "current_identity": initial, "sha256": digest.hexdigest(),
               "bytes_read": count, "stable_descriptor_and_path": True}
        record_path = folder / (name + ".rehash.json")
        write_immutable_record(record_path, row)
        rows[name], pins[name] = row, _sha256(record_path)
        print("RECOVERY278_HASH_MATCH", name, count, flush=True)
    if total != RECOVERY_CAPS["archive_bytes"] or time.time() >= deadline:
        raise TimeoutError("incomplete or late recovery")
    for name, row in rows.items():
        if row["current_identity"] != file_identity((Path(plan["paths"]["input_root"]) / name).lstat()):
            raise ValueError("archive changed before binding publication")
    if _sha256(OUTPUT / "owner_approval.json") != approval_sha or _sha256(Path(__file__)) != code_sha:
        raise ValueError("recovery authority/code changed during read")
    result = {"checkpoint": 278, "whole_file_equality": True, "bytes_read": total,
              "archives": rows, "record_sha256": pins, "caps": RECOVERY_CAPS,
              "approval_sha256": approval_sha,
              "accepted276_binding_sha256": _sha256(PILOT / "recovery/binding.json"),
              "recovery_code_sha256": code_sha,
              "rss_peak_bytes": peak, "wall_seconds": time.monotonic() - started,
              "archive_mutation": False, "automatic_retry": False}
    if sum(path.stat().st_size for path in folder.iterdir()) + len(json.dumps(result, indent=2).encode()) + 1 > RECOVERY_CAPS["output_bytes"]:
        raise OSError("16MiB recovery record cap")
    write_immutable_record(folder / "binding.json", result)
    if read_verified_json(folder / "binding.json", _sha256(folder / "binding.json")) != result:
        raise RuntimeError("recovery binding readback mismatch")
    print("RECOVERY278_COMPLETE", total, round(result["wall_seconds"], 3), flush=True)
    return result


def verified_identities(plan: dict) -> dict:
    authority()
    _, accepted = accepted_binding()
    path = Path(plan["additive_recovery_binding_path"])
    binding = read_verified_json(path, plan["additive_recovery_binding_sha256"])
    if binding["approval_sha256"] != _sha256(OUTPUT / "owner_approval.json") or binding["recovery_code_sha256"] != _sha256(Path(__file__)) or binding["accepted276_binding_sha256"] != _sha256(PILOT / "recovery/binding.json") or binding["caps"] != RECOVERY_CAPS or binding["whole_file_equality"] is not True or binding["bytes_read"] != RECOVERY_CAPS["archive_bytes"]:
        raise ValueError("additional recovery authority/code/content commitment drift")
    if set(binding["archives"]) != set(ANCHORS):
        raise ValueError("exact three additionally recovered archives required")
    identities = {}
    for name, row in binding["archives"].items():
        if row != read_verified_json(path.parent / (name + ".rehash.json"), binding["record_sha256"][name]):
            raise ValueError("additional recovery row drift")
        current_stat = (Path(plan["paths"]["input_root"]) / name).lstat()
        current = file_identity(current_stat)
        previous = accepted["archives"][name]["current_identity"]
        check_device_only(current, previous)
        if not stat.S_ISREG(current_stat.st_mode) or current != row["current_identity"] or row["accepted276_identity"] != previous or row["sha256"] != ANCHORS[name] or row["bytes_read"] != ARCHIVE_SIZES[name] or row["stable_descriptor_and_path"] is not True:
            raise ValueError("additional recovered archive identity drift")
        identities[name] = tuple(current[key] for key in ("device", "inode", "byte_size", "mtime_ns", "ctime_ns"))
    return identities
