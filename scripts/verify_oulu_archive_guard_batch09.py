#!/usr/bin/env python3
"""Explicit Review220/Recovery219 fast guard; no packet preparation."""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.oulu import _sha256
from import_oulu_categorical_batch08 import strict_json, verify_preservation
from prepare_oulu_owner_review import private_output
from recover_oulu_archive_identity import ANCHORS, file_identity

AUTHORITY_BINDINGS = {
    "docs/220-review-doc219-oulu-archive-identity-recovery.md": "ad516d31c0b9df653b24fc32509f019d3fb8af9af94c54b54c2b7041dec40e3a",
    "docs/219-review-response-doc218-oulu-archive-identity-recovery.md": "d944f7165035affdecad9baf23e9b7cb044bb4fe0b3de76754f3f3111bb81740",
    "results/phase1/oulu-archive-identity-recovery219-v1.json": "919fd1d4f5f0f129e46f2d89eebf0887f78ed43cfb7d945ca4b58fcc25ac8cb1",
    "scripts/recover_oulu_archive_identity_batch09.py": "8ae6e3cc5483caf0d965ba2d05e0d06e5aa25ea55d0059e511a0371390267a0c",
}
SOURCE219_CI = {"head_sha": "3eed781b6d68fb6dddf725a56be9a3b69c25b505", "run_id": 39359791576,
                "job_id": 118423022731, "status": "completed", "conclusion": "success",
                "job_status": "completed", "job_conclusion": "success",
                "listed_successful_steps": 12, "all_steps_success": True}
ARCHIVE_SIZES = {"Dev_files.tar": 28151992320, "Test_files.tar": 39211162112, "Train_files.tar": 37753662976}
IDENTITY_FIELDS = ("device", "inode", "byte_size", "mtime_ns", "ctime_ns")


def read_verified_json(path: Path, digest: str) -> dict:
    if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode):
        raise ValueError("regular non-symlink evidence required")
    payload = path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != digest:
        raise ValueError("accepted evidence SHA mismatch")
    return strict_json(payload)


def verified_guard_authority(preflight: dict) -> dict:
    expected = {"checkpoint": 221, "accepted_by_Review220": True, "guard_integration_authorized": True,
                "packet_retry_authorized": False, "packet_preparation_authorized": False, "recovery_authorized": False}
    if any(type(preflight.get(key)) is not type(value) or preflight[key] != value for key, value in expected.items()):
        raise ValueError("explicit Review220 guard-only authority required")
    if preflight.get("authority_sha256") != AUTHORITY_BINDINGS:
        raise ValueError("exact Review220 and accepted219 authority bindings required")
    for name, digest in AUTHORITY_BINDINGS.items():
        if _sha256(ROOT / name) != digest:
            raise ValueError("Review220 or accepted219 public authority drift")
    check = preflight.get("source219_CI")
    if not isinstance(check, dict) or any(type(check.get(key)) is not type(value) or check[key] != value for key, value in SOURCE219_CI.items()):
        raise ValueError("exact successful219 head/run/job/all12 CI required")
    if _sha256(Path(__file__)) != preflight["guard_code_sha256"]:
        raise ValueError("guard221 implementation drift")
    return strict_json((ROOT / "results/phase1/oulu-archive-identity-recovery219-v1.json").read_bytes())


def verified_archive_identities(input_root: Path, archive_records: Path, preflight: dict) -> dict:
    report = verified_guard_authority(preflight)
    binding_path = Path(preflight["accepted219_binding_path"])
    binding = read_verified_json(binding_path, report["private_binding_sha256"])
    prior = read_verified_json(Path(preflight["accepted219_preflight_path"]), report["private_preflight_sha256"])
    verification = read_verified_json(Path(preflight["accepted219_verification_path"]), report["private_verification_sha256"])
    historical = {"checkpoint": 219, "recovery_checkpoint_review_pending": True, "proposed_binding_accepted": False,
                  "packet_runner_guard_changed": False, "packet_preparation_authorized_by_this_record": False,
                  "archive_identity_blocker_closed": False, "original_pins_and_accepted177_records_unchanged": True}
    if any(type(binding.get(key)) is not type(value) or binding[key] != value for key, value in historical.items()):
        raise ValueError("unchanged historical219 binding flags required")
    if binding["preflight_sha256"] != report["private_preflight_sha256"] or binding["recovery_code_sha256"] != report["recovery_code_sha256"]:
        raise ValueError("accepted219 preflight/code lineage drift")
    for key in ("review218_sha256", "accepted217_document_sha256", "accepted217_report_sha256", "accepted217_blocker_sha256", "source217_CI"):
        if binding[key] != prior[key] or prior[key] != report[key]:
            raise ValueError("accepted217/218 recovery lineage drift")
    old = binding["latest_accepted_recovery"]
    if old != prior["accepted_recovery"] or old.get("accepted_by_Review178") is not True:
        raise ValueError("complete original177/Review178 lineage required")
    for name, key in (("docs/178-review-doc177-oulu-archive-identity-recovery.md", "review178_sha256"),
                      ("results/phase1/oulu-archive-identity-recovery-v1.json", "accepted177_report_sha256"),
                      ("results/phase1/oulu-archive-byte-pinning-v1.json", "archive_pin_report_sha256")):
        if _sha256(ROOT / name) != old[key] or old[key] != report[key]:
            raise ValueError("historical177/frozen authority drift")
    old_report = strict_json((ROOT / "results/phase1/oulu-archive-identity-recovery-v1.json").read_bytes())
    old_binding_path = Path(old["binding_path"])
    old_binding = read_verified_json(old_binding_path, old["binding_sha256"])
    if old["binding_sha256"] != report["latest_accepted_binding_sha256"] or old["binding_sha256"] != old_report["private_environment_binding_sha256"]:
        raise ValueError("accepted177 binding commitment drift")
    if old_binding.get("old_archive_pins_unchanged") is not True or old_binding.get("recovery_checkpoint_review_pending") is not True:
        raise ValueError("historical177 flags drift")
    if binding["archive_pin_report_sha256"] != old["archive_pin_report_sha256"] or old_binding["archive_pin_report_sha256"] != old["archive_pin_report_sha256"]:
        raise ValueError("frozen pin lineage drift")
    pins = strict_json((ROOT / "results/phase1/oulu-archive-byte-pinning-v1.json").read_bytes())["media_archives"]
    if any(set(rows) != set(ANCHORS) for rows in (pins, binding["archives"], old_binding["archives"], report["archive_results"])):
        raise ValueError("exact three archive records required")
    expected_files = {name + ".rehash.json" for name in ANCHORS} | {"environment_binding.json"}
    if {path.name for path in binding_path.parent.iterdir()} != expected_files or set(verification["recovery_file_sha256"]) != expected_files:
        raise ValueError("exact four accepted recovery files required")
    for name, digest in verification["recovery_file_sha256"].items():
        read_verified_json(binding_path.parent / name, digest)
    for field in ("protected_snapshots", "pinned_file_sha256", "frozen_file_sha256", "study_config_sha256"):
        for name, digest in prior[field].items():
            expected = _sha256(ROOT / "tests/test_oulu.py") if field == "pinned_file_sha256" and name == str(ROOT / "tests/test_oulu.py") else digest
            if preflight[field].get(name) != expected:
                raise ValueError("inherited protected evidence cannot be omitted or rebound")
    if preflight["protected_snapshots"].get(str(binding_path.parent)) != verification["recovery_file_sha256"]:
        raise ValueError("accepted219 recovery evidence protection required")
    identities = {}
    for name, pin in pins.items():
        original = read_verified_json(archive_records / (name + ".sha256.json"), pin["private_record_sha256"])["file_identity"]
        previous = read_verified_json(old_binding_path.parent / (name + ".rehash.json"), old_report["archive_results"][name]["rehash_record_sha256"])
        row = read_verified_json(binding_path.parent / (name + ".rehash.json"), report["archive_results"][name]["rehash_record_sha256"])
        if previous != old_binding["archives"][name] or row != binding["archives"][name]:
            raise ValueError("binding and whole-file observation disagree")
        if pin["sha256"] != ANCHORS[name] or type(pin["byte_size"]) is not int or pin["byte_size"] != ARCHIVE_SIZES[name]:
            raise ValueError("unchanged frozen SHA256 and byte size required")
        latest = previous["current_file_identity"]
        current = row["current_file_identity"]
        if previous["old_file_identity"] != original or previous["old_private_record_sha256"] != pin["private_record_sha256"]:
            raise ValueError("original frozen pin/177 identity lineage drift")
        for observation in (previous, row):
            if observation["current_sha256"] != pin["sha256"] or observation["frozen_sha256"] != pin["sha256"] or observation["byte_size"] != pin["byte_size"] or observation["changed_fields"] != ["device"] or any(observation[key] is not True for key in ("whole_file_read", "content_hash_matches_frozen", "stat_identity_stable_during_hash")):
                raise ValueError("accepted whole-file content evidence drift")
        if row["old_file_identity"] != latest or row["latest_accepted_environment_identity"] != latest or row["original_frozen_pin_file_identity"] != original or row["original_private_record_sha256"] != pin["private_record_sha256"]:
            raise ValueError("distinct original/177/219 identity lineage drift")
        if row["latest_accepted_binding_sha256"] != old["binding_sha256"] or row["preflight_sha256"] != report["private_preflight_sha256"] or row["review218_sha256"] != report["review218_sha256"] or row["proposed_binding_accepted"] is not False:
            raise ValueError("historical219 observation commitments drift")
        for before, after in (({**original, "byte_size": pin["byte_size"]}, latest), (latest, current)):
            if set(before) != set(IDENTITY_FIELDS) or set(after) != set(IDENTITY_FIELDS) or any(type(value) is not int for value in [*before.values(), *after.values()]) or sorted(key for key in before if before[key] != after[key]) != ["device"]:
                raise ValueError("historical device-only recovery transition required")
        if current != prior["observed_archive_identity"][name] or latest != prior["latest_accepted_archive_identity"][name] or current["byte_size"] != pin["byte_size"]:
            raise ValueError("accepted219 hashed identity agreement required")
        identities[name] = tuple(current[key] for key in IDENTITY_FIELDS)
    verify_preservation(preflight)
    for name, expected in identities.items():
        path = input_root / name
        current_stat = path.lstat()
        current = file_identity(current_stat)
        if not stat.S_ISREG(current_stat.st_mode) or tuple(current[key] for key in IDENTITY_FIELDS) != expected:
            raise ValueError("archive identity drift from accepted219; separate review required")
    return identities


def verify(args: argparse.Namespace) -> dict:
    private_output(args.out_root, [args.input_root, args.archive_records, args.preflight])
    preflight = strict_json(args.preflight.read_bytes())
    private_output(args.out_root, [Path(name) for name in preflight["protected_snapshots"]] +
                   [Path(preflight[key]) for key in ("accepted219_binding_path", "accepted219_preflight_path", "accepted219_verification_path")])
    before = verified_archive_identities(args.input_root, args.archive_records, preflight)
    if verified_archive_identities(args.input_root, args.archive_records, preflight) != before:
        raise ValueError("archive identity changed during guard validation")
    result = {"version": 1, "checkpoint": 221, "status": "recovery219_aware_guard_passed_no_packet_preparation",
              "accepted_by_Review220": True, "preflight_sha256": _sha256(args.preflight),
              "authority_sha256": preflight["authority_sha256"], "source219_CI": preflight["source219_CI"],
              "guard_code_sha256": _sha256(Path(__file__)), "accepted219_binding_sha256": _sha256(Path(preflight["accepted219_binding_path"])),
              "archive_identities": {name: list(identity) for name, identity in before.items()}, "archives_verified": len(before),
              "guard_integration_checkpoint_review_pending": True, "guard_integration_accepted": False,
              "packet_preparation_authorized": False, "packet_retry_authorized": False,
              "archive_identity_blocker_closed": False, "actual_pair_packets": 0, "selected_payloads_opened": False,
              "archive_bytes_rehashed": 0, "media_decoding_or_extraction_performed": False,
              "accepted_current_total": 80, "accepted_AI_screen_coverage": 80, "accepted_semantic_owner_outcomes_total": 80,
              "remaining_not_AI_screened": 5, "historical_disagreements": 1, "historical_unresolved_reconciliations": 0,
              "scientific_readiness": False}
    write_immutable_record(args.out_root / "guard_validation.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("input-root", "archive-records", "preflight", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        result = verify(parser.parse_args())
    except (OSError, RuntimeError, ValueError, KeyError, TypeError):
        print("GUARD221 FAILED: no payload access or packet clearance claimed", file=sys.stderr)
        return 1
    print(json.dumps({key: result[key] for key in ("status", "archives_verified", "actual_pair_packets", "packet_retry_authorized")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())