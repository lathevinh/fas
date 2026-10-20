#!/usr/bin/env python3
"""Read-only Review218 recovery; propose a pending checkpoint219 binding."""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.oulu import _sha256
from prepare_oulu_owner_review import private_output
from recover_oulu_archive_identity import ANCHORS, file_identity, rehash_archive, verify_preserved

REVIEW218_SHA256 = "7d3d16b6dac0800f47814e2bcab7e6cec818bf342c5e8b0255e784653199d29b"
ACCEPTED217_DOCUMENT_SHA256 = "98cb6f20d75d7db880030be0ca094dd9bda4c97cb4c528b33754cc05675257ab"
ACCEPTED217_REPORT_SHA256 = "47fe9d7c5372b532988c023846aa22c99f8650b00145971ba993049cbd9909e9"
ACCEPTED217_BLOCKER_SHA256 = "9dec3dfc794b1b6572aa2a640331841e274a4990ab82013fb6c9cf842efffc8e"


def verified_recovery_authority(preflight: dict) -> dict:
    expected = {"checkpoint": 219, "recovery_authorized": True, "packet_retry_authorized": False,
                "guard_integration_authorized": False, "review218_sha256": REVIEW218_SHA256,
                "accepted217_document_sha256": ACCEPTED217_DOCUMENT_SHA256,
                "accepted217_report_sha256": ACCEPTED217_REPORT_SHA256,
                "accepted217_blocker_sha256": ACCEPTED217_BLOCKER_SHA256}
    if any(type(preflight.get(key)) is not type(value) or preflight[key] != value for key, value in expected.items()):
        raise ValueError("explicit bounded Review218 recovery-only authority required")
    for name, digest in (("docs/218-review-doc217-oulu-batch09-archive-device-blocker.md", REVIEW218_SHA256),
                         ("docs/217-review-response-doc216-oulu-batch09-packets.md", ACCEPTED217_DOCUMENT_SHA256),
                         ("results/phase1/oulu-batch09-packet-preparation-blocker-v1.json", ACCEPTED217_REPORT_SHA256)):
        if _sha256(ROOT / name) != digest:
            raise ValueError("Review218 or accepted217 public authority drift")
    report = json.loads((ROOT / "results/phase1/oulu-batch09-packet-preparation-blocker-v1.json").read_bytes())
    if report["private_blocker_sha256"] != ACCEPTED217_BLOCKER_SHA256 or _sha256(Path(preflight["blocker_path"])) != ACCEPTED217_BLOCKER_SHA256:
        raise ValueError("accepted217 private blocker drift")
    blocker = json.loads(Path(preflight["blocker_path"]).read_bytes())
    if blocker["accepted_recovery"] != preflight["accepted_recovery"] or preflight.get("archive_anchor_sha256") != ANCHORS:
        raise ValueError("accepted recovery lineage or frozen content anchors drift")
    check = preflight.get("source217_CI")
    expected_ci = {"head_sha": "9082585c811ee3b1636b33145e5748876083ef30", "run_id": 39354730481,
                   "job_id": 118406801611, "status": "completed", "conclusion": "success",
                   "job_status": "completed", "job_conclusion": "success", "listed_successful_steps": 12,
                   "all_steps_success": True}
    if not isinstance(check, dict) or any(type(check.get(key)) is not type(value) or check[key] != value for key, value in expected_ci.items()):
        raise ValueError("exact successful217 head/run/job/all12 CI required")
    return blocker


def verified_prior_binding(args: argparse.Namespace, preflight: dict) -> tuple[dict, dict, dict]:
    recovery = preflight["accepted_recovery"]
    pin_path = ROOT / "results/phase1/oulu-archive-byte-pinning-v1.json"
    report_path = ROOT / "results/phase1/oulu-archive-identity-recovery-v1.json"
    if recovery.get("accepted_by_Review178") is not True or _sha256(ROOT / "docs/178-review-doc177-oulu-archive-identity-recovery.md") != recovery["review178_sha256"]:
        raise ValueError("latest accepted177/Review178 authority required")
    if _sha256(pin_path) != recovery["archive_pin_report_sha256"] or _sha256(pin_path) != preflight["archive_pin_report_sha256"] or _sha256(report_path) != recovery["accepted177_report_sha256"]:
        raise ValueError("frozen pins or latest accepted recovery report drift")
    report = json.loads(report_path.read_bytes())
    binding_path = Path(recovery["binding_path"])
    private_output(args.out_root, [binding_path.parent])
    if _sha256(binding_path) != recovery["binding_sha256"] or recovery["binding_sha256"] != report["private_environment_binding_sha256"] or report["archive_pin_report_sha256"] != recovery["archive_pin_report_sha256"]:
        raise ValueError("latest accepted environment binding SHA mismatch")
    binding = json.loads(binding_path.read_bytes())
    if binding.get("recovery_checkpoint_review_pending") is not True or binding.get("old_archive_pins_unchanged") is not True or binding["archive_pin_report_sha256"] != recovery["archive_pin_report_sha256"]:
        raise ValueError("historical177 pending binding fields drift")
    pins = json.loads(pin_path.read_bytes())["media_archives"]
    if set(pins) != set(ANCHORS) or set(binding["archives"]) != set(ANCHORS) or {name: row["sha256"] for name, row in pins.items()} != ANCHORS:
        raise ValueError("exact three frozen archive anchors required")
    originals, latest = {}, {}
    for name, pin in pins.items():
        record_path = args.archive_records / (name + ".sha256.json")
        row_path = binding_path.parent / (name + ".rehash.json")
        if _sha256(record_path) != pin["private_record_sha256"] or _sha256(row_path) != report["archive_results"][name]["rehash_record_sha256"]:
            raise ValueError("original pin or accepted177 observation drift")
        originals[name] = json.loads(record_path.read_bytes())["file_identity"]
        row = binding["archives"][name]
        if json.loads(row_path.read_bytes()) != row or row["old_file_identity"] != originals[name] or row["old_private_record_sha256"] != pin["private_record_sha256"]:
            raise ValueError("original frozen identity lineage drift")
        if row["current_sha256"] != pin["sha256"] or row["frozen_sha256"] != pin["sha256"] or row["byte_size"] != pin["byte_size"] or row["whole_file_read"] is not True or row["content_hash_matches_frozen"] is not True or row["stat_identity_stable_during_hash"] is not True or row["changed_fields"] != ["device"]:
            raise ValueError("latest accepted content recovery observation drift")
        original = {**originals[name], "byte_size": pin["byte_size"]}
        latest[name] = row["current_file_identity"]
        if set(latest[name]) != set(original) or sorted(key for key in original if original[key] != latest[name][key]) != ["device"]:
            raise ValueError("accepted177 device-only identity transition required")
    if latest != preflight["latest_accepted_archive_identity"]:
        raise ValueError("latest accepted identity preflight drift")
    return pins, originals, latest


def rehash_current_archive(path: Path, expected: dict, latest: dict, observed: dict) -> dict:
    if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode):
        raise ValueError("regular non-symlink archive required")
    before = file_identity(path.stat())
    if set(latest) != set(before) or any(type(value) is not int for value in latest.values()) or before != observed:
        raise ValueError("current or latest accepted five-field identity drift")
    if before["byte_size"] != expected["byte_size"] or sorted(key for key in before if before[key] != latest[key]) != ["device"]:
        raise ValueError("device-only drift from latest accepted identity required before hash")
    row = rehash_archive(path, expected, latest)
    if row["current_file_identity"] != observed:
        raise ValueError("archive differs from preflight identity after hash")
    row.update({"latest_accepted_environment_identity": latest,
                "identity_comparison_basis": "accepted177_Review178_environment_not_original_pre177_pin",
                "old_file_identity_means": "latest_accepted_environment_identity",
                "proposed_binding_accepted": False})
    return row


def recover(args: argparse.Namespace) -> dict:
    private_output(args.out_root, [args.input_root, args.archive_records, args.preflight])
    preflight = json.loads(args.preflight.read_bytes())
    private_output(args.out_root, [Path(name) for name in preflight["protected_snapshots"]] + [Path(preflight["blocker_path"])])
    blocker = verified_recovery_authority(preflight)
    if _sha256(Path(__file__)) != preflight["recovery_code_sha256"]:
        raise ValueError("recovery219 implementation drift")
    verify_preserved(preflight)
    pins, originals, latest = verified_prior_binding(args, preflight)
    observed = preflight["observed_archive_identity"]
    if set(observed) != set(ANCHORS) or any(observed[name] != blocker["archive_observations"][name]["observed_file_identity"] for name in ANCHORS):
        raise ValueError("accepted217 observed identity drift")
    for name in ANCHORS:
        path = args.input_root / name
        if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode) or file_identity(path.stat()) != observed[name] or sorted(key for key in latest[name] if latest[name][key] != observed[name][key]) != ["device"]:
            raise ValueError("all three archives require preflight-stable latest-device-only drift")
    rows = {}
    for name in ANCHORS:
        print("REHASH219 START " + name, flush=True)
        row = rehash_current_archive(args.input_root / name, pins[name], latest[name], observed[name])
        row.update({"original_frozen_pin_file_identity": originals[name],
                    "original_private_record_sha256": pins[name]["private_record_sha256"],
                    "latest_accepted_binding_sha256": preflight["accepted_recovery"]["binding_sha256"],
                    "review218_sha256": preflight["review218_sha256"], "preflight_sha256": _sha256(args.preflight)})
        write_immutable_record(args.out_root / (name + ".rehash.json"), row)
        rows[name] = row
        print("REHASH219 MATCH " + name + " bytes=" + str(row["byte_size"]) + " seconds=" + str(row["elapsed_seconds"]), flush=True)
    verify_preserved(preflight)
    for name, row in rows.items():
        path = args.input_root / name
        if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode) or file_identity(path.stat()) != row["current_file_identity"]:
            raise ValueError("archive changed before proposed219 binding")
        with path.open("rb") as source:
            if file_identity(os.fstat(source.fileno())) != row["current_file_identity"]:
                raise ValueError("archive descriptor changed before proposed219 binding")
        if file_identity(path.stat()) != row["current_file_identity"]:
            raise ValueError("archive changed after final descriptor check")
    binding = {"version": 1, "checkpoint": 219, "status": "content_identity_verified_new_environment_binding_review_pending",
               "review218_sha256": preflight["review218_sha256"], "preflight_sha256": _sha256(args.preflight),
               "accepted217_document_sha256": preflight["accepted217_document_sha256"],
               "accepted217_report_sha256": preflight["accepted217_report_sha256"],
               "accepted217_blocker_sha256": preflight["accepted217_blocker_sha256"], "source217_CI": preflight["source217_CI"],
               "archive_pin_report_sha256": preflight["archive_pin_report_sha256"],
               "latest_accepted_recovery": preflight["accepted_recovery"], "archives": rows,
               "recovery_code_sha256": _sha256(Path(__file__)), "total_bytes_hashed": sum(row["byte_size"] for row in rows.values()),
               "content_authority": "unchanged_frozen_whole_file_SHA256_and_byte_size",
               "identity_comparison_basis": "latest_accepted177_Review178_environment",
               "original_pins_and_accepted177_records_unchanged": True, "all_prior_inputs_unchanged": True,
               "recovery_checkpoint_review_pending": True, "proposed_binding_accepted": False,
               "packet_runner_guard_changed": False, "packet_preparation_authorized_by_this_record": False,
               "archive_identity_blocker_closed": False, "individual_video_payloads_opened": False,
               "media_decoding_or_extraction_performed": False, "filesystem_change_cause_independently_established": False,
               "accepted_current_total": 80, "accepted_AI_screen_coverage": 80, "accepted_semantic_owner_outcomes_total": 80,
               "remaining_not_AI_screened": 5, "historical_disagreements": 1, "historical_unresolved_reconciliations": 0,
               "new_AI_human_effective_dispositions": 0, "scientific_readiness": False}
    write_immutable_record(args.out_root / "environment_binding.json", binding)
    return binding


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("input-root", "archive-records", "preflight", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        result = recover(parser.parse_args())
    except (OSError, ValueError, KeyError, TypeError):
        print("RECOVERY219 FAILED: no binding acceptance, guard integration or packet clearance claimed", file=sys.stderr)
        return 1
    print(json.dumps({"status": result["status"], "archives_verified": len(result["archives"]),
                      "total_bytes_hashed": result["total_bytes_hashed"]}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())