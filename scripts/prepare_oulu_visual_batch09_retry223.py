#!/usr/bin/env python3
"""Prepare exact final-five packets under explicit Review222 retry authority."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np

from fas.freeze import write_immutable_record
from fas.oulu import _sha256
from fas.visual import pair_sheet, png_bytes, review_orders, verified_thumbnails
from prepare_oulu_owner_review import private_output
from prepare_oulu_visual_batch05 import bundle
from prepare_oulu_visual_batch09 import ACCEPTED215_DOCUMENT_SHA256, ACCEPTED215_REPORT_SHA256, REVIEW216_SHA256, TARGET_RANKS, fixed_next_records, verified_prior_rows
from verify_oulu_archive_guard_batch09 import read_verified_json, verified_archive_identities

AUTHORITY_BINDINGS = {
    "docs/222-review-doc221-oulu-recovery219-aware-guard.md": "648bf5d83a8724dca155b446e1dac2c92372a8c05e8a049ebdf270912a2490a6",
    "docs/221-review-response-doc220-oulu-recovery219-aware-guard.md": "90b4cbf95d36dea70396402453d26c072b08a7ec488f6e414922726e34d5bc43",
    "results/phase1/oulu-recovery219-aware-guard-v1.json": "dcaee4e96d92145091a0982c7157b27676772bdd3e47c88cefacacb50a593405",
    "scripts/verify_oulu_archive_guard_batch09.py": "ac732a581d033275a361e147e11dd58f40aa20f0f7283d7b353b60516bee26fb",
    "scripts/prepare_oulu_visual_batch09.py": "0d6345fe3f2c9d87bf961596ed280c17e60cd1997c2d344e397496d733c0794e",
    "docs/216-review-doc215-oulu-batch08-activation.md": REVIEW216_SHA256,
    "docs/215-review-response-doc214-oulu-batch08-activation.md": ACCEPTED215_DOCUMENT_SHA256,
    "results/phase1/oulu-batch08-activation-v1.json": ACCEPTED215_REPORT_SHA256,
}
SOURCE221_CI = {"head_sha": "dac0f59a9bb7be6c43b60718f4f1540ff7a932f7", "run_id": 39361766058,
                "job_id": 118429341568, "status": "completed", "conclusion": "success",
                "job_status": "completed", "job_conclusion": "success", "listed_successful_steps": 12, "all_steps_success": True}
OLD_TEST_SHA256 = "5aa711455344d6fa823f56b1ee8b8fe6407c8b9f568e0b1e785ed014af468288"
OLD_TEST_AST_SHA256 = "69fa1fa50fd068bb727cd17a27436647c63ccef933e525f5f037944a80bdc7d8"
NEW_TEST_METHOD = "test_batch09_retry223_binds_review222_guard_context_and_test_transition"


def verified_retry_authority(preflight: dict) -> dict:
    expected = {"checkpoint": 223, "accepted_by_Review222": True, "packet_preparation_authorized": True,
                "packet_retry_authorized": True, "visual_review_authorized": False}
    if any(type(preflight.get(key)) is not type(value) or preflight[key] != value for key, value in expected.items()):
        raise ValueError("explicit Review222 preparation-only retry authority required")
    if preflight.get("queue_ranks") != TARGET_RANKS or any(type(rank) is not int for rank in preflight["queue_ranks"]):
        raise ValueError("exact final-five integer ranks80 through84 required")
    if preflight.get("authority_sha256") != AUTHORITY_BINDINGS:
        raise ValueError("exact Review222 and accepted221 source bindings required")
    for name, digest in AUTHORITY_BINDINGS.items():
        if _sha256(ROOT / name) != digest:
            raise ValueError("Review222 or accepted221 authority drift")
    check = preflight.get("source221_CI")
    if not isinstance(check, dict) or any(type(check.get(key)) is not type(value) or check[key] != value for key, value in SOURCE221_CI.items()):
        raise ValueError("exact successful221 head/run/job/all12 CI required")
    transition = preflight["test_pin_transition"]
    test_path = ROOT / "tests/test_oulu.py"
    if transition != {"old_sha256": OLD_TEST_SHA256, "new_sha256": _sha256(test_path), "only_added_method": NEW_TEST_METHOD, "all_prior_test_ASTs_unchanged": True}:
        raise ValueError("explicit accepted221 to223 test pin transition required")
    module = ast.parse(test_path.read_bytes())
    removed = 0
    for node in ast.walk(module):
        if isinstance(node, ast.ClassDef):
            added = [entry for entry in node.body if isinstance(entry, ast.FunctionDef) and entry.name == NEW_TEST_METHOD]
            removed += len(added)
            node.body = [entry for entry in node.body if entry not in added]
    if removed != 1 or hashlib.sha256(ast.dump(module).encode()).hexdigest() != OLD_TEST_AST_SHA256:
        raise ValueError("accepted221 complete prior test AST drift")
    report = json.loads((ROOT / "results/phase1/oulu-recovery219-aware-guard-v1.json").read_bytes())
    if report["guard_code_sha256"] != AUTHORITY_BINDINGS["scripts/verify_oulu_archive_guard_batch09.py"] or report["test_file_sha256"] != OLD_TEST_SHA256:
        raise ValueError("accepted221 code/test commitment drift")
    old = read_verified_json(Path(preflight["accepted221_preflight_path"]), report["private_preflight_sha256"])
    result = read_verified_json(Path(preflight["accepted221_result_path"]), report["private_guard_result_sha256"])
    read_verified_json(Path(preflight["accepted221_verification_path"]), report["private_verification_sha256"])
    if result["guard_integration_checkpoint_review_pending"] is not True or result["packet_preparation_authorized"] is not False or result["packet_retry_authorized"] is not False or result["archives_verified"] != 3:
        raise ValueError("historical221 guard-only result flags drift")
    context = preflight["guard_context"]
    for key, value in old.items():
        if key not in ("pinned_file_sha256", "protected_snapshots") and context.get(key) != value:
            raise ValueError("historical221 guard-only context drift")
    for field in ("pinned_file_sha256", "protected_snapshots"):
        for name, digest in old[field].items():
            expected_pin = transition["new_sha256"] if field == "pinned_file_sha256" and name == str(test_path) else digest
            if context[field].get(name) != expected_pin:
                raise ValueError("accepted221 protected evidence cannot be omitted or rebound")
    if context["protected_snapshots"].get(str(Path(preflight["accepted221_result_path"]).parent)) != {"guard_validation.json": report["private_guard_result_sha256"]}:
        raise ValueError("accepted221 guard result protection required")
    for field in ("protected_snapshots", "pinned_file_sha256", "frozen_file_sha256", "study_config_sha256"):
        if preflight[field] != context[field]:
            raise ValueError("retry and guard preservation contexts disagree")
    if preflight["accepted_prior_report_sha256"] != ACCEPTED215_REPORT_SHA256 or preflight["accepted_prior_document_sha256"] != ACCEPTED215_DOCUMENT_SHA256 or preflight["acceptance"].get("review216_sha256") != REVIEW216_SHA256:
        raise ValueError("Review216 final-five selection authority drift")
    return context


def prepare(args: argparse.Namespace) -> dict:
    private_output(args.out_root, [args.input_root, args.audit_root, args.exact_root, args.screen_root,
                                  args.frozen_root, args.archive_records, args.activation_root, args.preflight])
    preflight = json.loads(args.preflight.read_bytes())
    private_output(args.out_root, [Path(name) for name in preflight["protected_snapshots"]] +
                   [Path(preflight[key]) for key in ("accepted221_preflight_path", "accepted221_result_path", "accepted221_verification_path")])
    context = verified_retry_authority(preflight)
    if _sha256(Path(__file__)) != preflight["preparation_code_sha256"]:
        raise ValueError("retry223 implementation drift")
    identities = verified_archive_identities(args.input_root, args.archive_records, context)
    prior_path = ROOT / "results/phase1/oulu-batch08-activation-v1.json"
    prior = json.loads(prior_path.read_bytes())
    for name, field in (("summary.json", "private_summary_sha256"), ("activation.json", "activation_sha256"),
                        ("successful_CI_observation.json", "successful_CI_observation_sha256")):
        if _sha256(args.activation_root / name) != prior[field]:
            raise ValueError("accepted215 private activation drift")
    if _sha256(Path(preflight["accepted_prior_verification_path"])) != prior["private_verification_sha256"]:
        raise ValueError("accepted215 private verification drift")
    rows = sorted((args.activation_root / "pairs").glob("*.json"))
    if len(rows) != 10 or bundle(rows) != prior["materialized_activation_row_bundle_sha256"]:
        raise ValueError("accepted215 ten-row bundle drift")
    verified_prior_rows([json.loads(path.read_bytes()) for path in rows], prior)
    exact_path = ROOT / "results/phase1/oulu-lineage-exact-evidence-v1.json"
    exact = json.loads(exact_path.read_bytes())
    paths = sorted((args.exact_root / "pairs").glob("*.json"))
    if len(paths) != 6640 or bundle(paths) != exact["pair_record_bundle_sha256"] or _sha256(args.exact_root / "summary.json") != exact["private_summary_sha256"]:
        raise ValueError("accepted queue drift")
    acceptance = preflight["acceptance"]
    records = fixed_next_records([json.loads(path.read_bytes()) for path in paths[:85]], prior, acceptance)
    frozen = {path.name: _sha256(path) for path in args.frozen_root.iterdir()}
    if frozen != exact["frozen_artifact_sha256"]:
        raise ValueError("frozen input drift")
    visual = json.loads((ROOT / "results/phase1/oulu-visual-review-batch01-v1.json").read_bytes())
    for name, digest in visual["implementation_sha256"].items():
        if _sha256(ROOT / name) != digest:
            raise ValueError("accepted visual implementation drift")
    if _sha256(ROOT / visual["policy_file"]) != visual["policy_sha256"]:
        raise ValueError("accepted visual evidence policy drift")
    for report_name in ("oulu-batch02-packets-v1.json", "oulu-batch03-packets-v1.json", "oulu-batch04-packets-v1.json", "oulu-batch05-packets-v1.json", "oulu-batch06-packet-retry-v1.json", "oulu-batch07-packets-v1.json", "oulu-batch08-packets-v1.json"):
        accepted = json.loads((ROOT / "results/phase1" / report_name).read_bytes())
        if _sha256(ROOT / accepted["runner_file"]) != accepted["runner_sha256"]:
            raise ValueError("accepted prior batch runner drift")
    for folder, report_name, field in ((args.audit_root / "videos", "oulu-per-video-media-audit-v1.json", "video_record_bundle_sha256"), (args.screen_root / "fingerprints", "oulu-content-screening-v1.json", "fingerprint_bundle_sha256")):
        files = sorted(folder.glob("*.json"))
        if len(files) != 4950 or bundle(files, True) != json.loads((ROOT / "results/phase1" / report_name).read_bytes())[field]:
            raise ValueError("accepted media/fingerprint bundle drift")
    if verified_archive_identities(args.input_root, args.archive_records, context) != identities:
        raise ValueError("archive identity changed before payload access")
    version = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    if version != json.loads((ROOT / "configs/environment_v1.yaml").read_bytes())["host_tools"]["ffmpeg_version_line"]:
        raise ValueError("research FFmpeg mismatch")
    lineage = {"version": 1, "checkpoint": 223, "batch": "batch09_retry223", "queue_ranks": TARGET_RANKS,
               "selection": "fixed_next_final_five_no_outcome_selection", "acceptance": acceptance,
               "historical215_pending_fields_unchanged": True, "historical_AI_uncertainty_and_disagreement_preserved": True,
               "preflight_sha256": _sha256(args.preflight), "source221_CI": preflight["source221_CI"],
               "authority_sha256": preflight["authority_sha256"], "test_pin_transition": preflight["test_pin_transition"],
               "accepted_prior_report_sha256": _sha256(prior_path), "accepted_prior_document_sha256": ACCEPTED215_DOCUMENT_SHA256,
               "prior_activation_sha256": prior["activation_sha256"], "prior_effective_bundle_sha256": prior["materialized_activation_row_bundle_sha256"],
               "accepted_prior_verification_sha256": prior["private_verification_sha256"],
               "accepted_exact_report_sha256": _sha256(exact_path), "exact_pair_bundle_sha256": exact["pair_record_bundle_sha256"],
               "accepted_visual_evidence_policy_sha256": visual["policy_sha256"], "visual_code_sha256": _sha256(ROOT / "src/fas/visual.py"),
               "runner_sha256": _sha256(Path(__file__)), "frozen_artifact_sha256": frozen, "ffmpeg": version,
               "no_prior_artifacts_overwritten": True, "accepted219_binding_sha256": _sha256(Path(context["accepted219_binding_path"])),
               "accepted221_result_sha256": _sha256(Path(preflight["accepted221_result_path"]))}
    output = args.out_root.resolve()
    write_immutable_record(output / "lineage.json", lineage)
    ids = sorted({row["candidate"][side] for row in records for side in ("left", "right")})
    media = {identity: json.loads((args.audit_root / "videos" / (identity + ".json")).read_bytes()) for identity in ids}
    frames, manifests = {}, {}

    def save(path: Path, rgb: np.ndarray) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            handle.write(png_bytes(rgb))
        return _sha256(path)

    for name in sorted({row["media_archive"] for row in media.values()}):
        with tarfile.open(args.input_root / name, "r:") as archive:
            for identity in sorted(identity for identity in ids if media[identity]["media_archive"] == name):
                row = media[identity]
                member = archive.getmember(row["media_relpath"])
                if not member.isfile() or member.size != row["byte_size"]:
                    raise ValueError("media payload metadata drift")
                with tempfile.TemporaryDirectory(prefix="fas-visual-b09-", dir=output) as directory:
                    path = Path(directory) / "media.avi"
                    with archive.extractfile(member) as source, path.open("wb") as target:
                        shutil.copyfileobj(source, target, length=1024 * 1024)
                    if path.stat().st_size != row["byte_size"] or _sha256(path) != row["media_sha256"]:
                        raise ValueError("accepted payload drift")
                    frames[identity] = verified_thumbnails(path, row)
                assets = [{"decode_order": order, "accepted_rgb_sha256": row["frame_index"][order]["rgb_sha256"], "thumbnail_sha256": save(output / "videos" / identity / f"{order:06d}.png", frame)} for order, frame in enumerate(frames[identity])]
                path = output / "videos" / identity / "manifest.json"
                write_immutable_record(path, {"video_id": identity, "media_record_sha256": _sha256(args.audit_root / "videos" / (identity + ".json")), "verified_frames": assets, "temporal_orders": review_orders(len(assets))})
                manifests[identity] = _sha256(path)
                print(f"VERIFIED BATCH09 VIDEO {len(frames)}/{len(ids)}", flush=True)
    packets = []
    for rank, row in enumerate(records, 80):
        left, right = (row["candidate"][side] for side in ("left", "right"))
        assets = {name + ".png": save(output / "pairs" / f"{rank:06d}" / (name + ".png"), pair_sheet(frames[left], frames[right], slots)) for name, slots in (("temporal_a", list(range(0, 17, 2))), ("temporal_b", list(range(1, 17, 2))))}
        fingerprints = [json.loads((args.screen_root / "fingerprints" / (identity + ".json")).read_bytes()) for identity in (left, right)]
        distance, left_slot, right_slot = min(((int(first["phash64"], 16) ^ int(second["phash64"], 16)).bit_count(), left_slot, right_slot) for left_slot, first in enumerate(fingerprints[0]["samples"]) for right_slot, second in enumerate(fingerprints[1]["samples"]))
        if distance != row["candidate"]["minimum_hamming"]:
            raise ValueError("trigger witness drift")
        orders = [fingerprints[0]["samples"][left_slot]["decode_order"], fingerprints[1]["samples"][right_slot]["decode_order"]]
        assets["trigger.png"] = save(output / "pairs" / f"{rank:06d}" / "trigger.png", np.concatenate((frames[left][orders[0]], frames[right][orders[1]]), axis=1))
        path = output / "pairs" / f"{rank:06d}" / "packet.json"
        write_immutable_record(path, {"version": 1, "queue_rank": rank, "priority": row["priority"], "candidate": row["candidate"], "exact_pair_record_sha256": _sha256(paths[rank]),
                                     "video_manifest_sha256": {left: manifests[left], right: manifests[right]}, "image_sha256": assets, "trigger_hamming": distance, "trigger_decode_orders": orders,
                                     "review_performed": False, "disposition": "awaiting_visual_review"})
        packets.append({"queue_rank": rank, "packet_sha256": _sha256(path)})
    if verified_archive_identities(args.input_root, args.archive_records, context) != identities:
        raise ValueError("archive changed during export")
    result = {"version": 1, "status": "batch09_retry223_private_packets_prepared_review_pending", "queue_ranks": TARGET_RANKS, "packets": packets,
              "unique_videos": len(ids), "all_RGB_frames_verified": sum(len(value) for value in frames.values()), "lineage_sha256": _sha256(output / "lineage.json"),
              "accepted_current_total": 80, "accepted_AI_screen_coverage": 80, "accepted_semantic_owner_outcomes_total": 80,
              "remaining_not_AI_screened": 5, "new_AI_human_effective_dispositions": 0, "historical215_pending_fields_unchanged": True,
              "historical_disagreements": 1, "historical_unresolved_reconciliations": 0,
              "historical_AI_uncertainty_and_disagreement_preserved": True, "frozen_inputs_unchanged": True, "prior_evidence_unchanged": True,
              "research_detector_or_model_executed": False, "scientific_readiness": False}
    write_immutable_record(output / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("input-root", "audit-root", "exact-root", "screen-root", "frozen-root", "archive-records", "activation-root", "preflight", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        print(json.dumps(prepare(parser.parse_args()), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError, tarfile.TarError):
        print("BATCH09 RETRY223 FAILED: no visual adjudication or clearance claimed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())