#!/usr/bin/env python3
"""Prepare final fixed ranks80..84 under additive Review216 acceptance."""

from __future__ import annotations

import argparse
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
from prepare_oulu_visual_batch06 import verified_archive_identities
from recover_oulu_archive_identity import verify_preserved

REVIEW216_SHA256 = "93b35ec407286f9c6815842af0edad32cfeabb10d67fcffb9871bbd6cb71a50e"
ACCEPTED215_REPORT_SHA256 = "99262c56e92e03cf22120f09e7f2a75a3f88ceca2789869c11a170435ef80ef3"
ACCEPTED215_DOCUMENT_SHA256 = "8dfdaa1a7bac2981a8eb8e4975df9b6d53aa0fc12c16b5cd13cbc41bb464e0d3"
TARGET_RANKS = list(range(80, 85))


def verified_packet_authority(preflight: dict) -> dict:
    acceptance = preflight.get("acceptance")
    if not isinstance(acceptance, dict) or acceptance.get("review216_sha256") != REVIEW216_SHA256:
        raise ValueError("explicit additive Review216 authority required")
    if _sha256(ROOT / "docs/216-review-doc215-oulu-batch08-activation.md") != REVIEW216_SHA256:
        raise ValueError("Review216 authority drift")
    if preflight.get("accepted_prior_report_sha256") != ACCEPTED215_REPORT_SHA256 or _sha256(ROOT / "results/phase1/oulu-batch08-activation-v1.json") != ACCEPTED215_REPORT_SHA256:
        raise ValueError("accepted215 report drift")
    if preflight.get("accepted_prior_document_sha256") != ACCEPTED215_DOCUMENT_SHA256 or _sha256(ROOT / "docs/215-review-response-doc214-oulu-batch08-activation.md") != ACCEPTED215_DOCUMENT_SHA256:
        raise ValueError("accepted215 document drift")
    if type(preflight.get("checkpoint")) is not int or preflight["checkpoint"] != 217 or preflight.get("packet_preparation_authorized") is not True:
        raise ValueError("checkpoint217 packet preparation required")
    ranks = preflight.get("queue_ranks")
    if ranks != TARGET_RANKS or any(type(rank) is not int for rank in ranks):
        raise ValueError("final five fixed integer ranks80 through84 required")
    check = preflight.get("activation_CI")
    expected = {"head_sha": "c240a8c90870c548f8bafdd35e59992d17e94784", "run_id": 39353105356,
                "job_id": 118401642331, "status": "completed", "conclusion": "success",
                "job_status": "completed", "job_conclusion": "success"}
    if not isinstance(check, dict) or any(type(check.get(key)) is not type(value) or check[key] != value for key, value in expected.items()):
        raise ValueError("exact successful215 head/run/validate CI required")
    recovery = preflight.get("accepted_recovery")
    if not isinstance(recovery, dict) or recovery.get("accepted_by_Review178") is not True:
        raise ValueError("accepted archive recovery required")
    return acceptance


def fixed_next_records(records: list[dict], prior: dict, acceptance: dict) -> list[dict]:
    expected_acceptance = {"batch08_activation_checkpoint_accepted": True, "batch08_screen_level_review_closed": True,
                           "accepted_current_total": 80, "accepted_batch08_disposition_counts": {"rejected_false_positive": 10},
                           "accepted_AI_screen_coverage": 80, "accepted_semantic_owner_outcomes_total": 80,
                           "historical_disagreements": 1, "historical_unresolved_reconciliations": 0}
    if any(type(acceptance.get(key)) is not type(value) or acceptance[key] != value for key, value in expected_acceptance.items()):
        raise ValueError("additive Review216 batch08 closure required")
    expected_prior = {"activation_checkpoint_review_pending": True, "accepted_batch08_current_effective_dispositions": 0,
                      "materialized_activation_rows": 10, "current_materialized_disposition_counts": {"rejected_false_positive": 10},
                      "accepted_current_total": 70, "prospective_total_after_acceptance": 80, "batch08_closed": False,
                      "stop_for_prospective_scientific_decision": False, "historical_disagreements": 1,
                      "historical_unresolved_reconciliations": 0, "batch08_agreements_with_AI": 10,
                      "batch08_disagreements_with_AI": 0, "batch08_unresolved_reconciliation_requirements": 0,
                      "original_import_pending_nonactivation_and_counting_flags_unchanged": True,
                      "new_rows_count_as_accepted_current_effective_dispositions": False}
    if any(type(prior.get(key)) is not type(value) or prior[key] != value for key, value in expected_prior.items()):
        raise ValueError("unchanged historical215 activation required")
    if len(records) != 85 or any(type(row.get("queue_rank")) is not int or row["queue_rank"] != rank or row.get("priority") != "cross_role_conflicting_label" for rank, row in enumerate(records)):
        raise ValueError("complete fixed highest-risk prefix0 through84 required")
    return records[80:85]


def verified_prior_rows(rows: list[dict], prior: dict) -> None:
    if len(rows) != 10:
        raise ValueError("ten unchanged historical215 activation rows required")
    expected = {"effective_disposition": "rejected_false_positive", "owner_disposition": "rejected_false_positive",
                "effective_disposition_activated": True, "activation_checkpoint_review_pending": True,
                "counts_as_accepted_current_effective_disposition": False, "activation_sha256": prior["activation_sha256"],
                "screen_semantic_acceptance_source": "Review214", "semantic_outcome_accepted_by_Review214": True,
                "stop_for_prospective_scientific_decision": False, "reconciliation_required": False,
                "AI_disposition_rewritten": False, "ai_disposition": "rejected_false_positive", "disagreement_with_AI": False,
                "historical_import_reconciliation_required": False, "historical_import_comparison_disposition": "rejected_false_positive",
                "historical_import_effective_disposition_activated": False,
                "historical_import_counts_as_accepted_current_effective_disposition": False,
                "historical_import_checkpoint_review_pending": True, "historical_import_semantic_acceptance_pending": True}
    for rank, row in enumerate(rows, 70):
        if type(row.get("queue_rank")) is not int or row["queue_rank"] != rank or any(type(row.get(key)) is not type(value) or row[key] != value for key, value in expected.items()):
            raise ValueError("historical215 activation/import/AI state drift")


def prepare(args: argparse.Namespace) -> dict:
    private_output(args.out_root, [args.input_root, args.audit_root, args.exact_root, args.screen_root,
                                  args.frozen_root, args.archive_records, args.activation_root, args.preflight])
    preflight = json.loads(args.preflight.read_bytes())
    private_output(args.out_root, [Path(name) for name in preflight["protected_snapshots"]])
    acceptance = verified_packet_authority(preflight)
    if _sha256(Path(__file__)) != preflight["preparation_code_sha256"]:
        raise ValueError("preparation implementation drift")
    verify_preserved(preflight)
    recovery = preflight["accepted_recovery"]
    private_output(args.out_root, [Path(recovery["binding_path"]).parent])
    identities = verified_archive_identities(args.input_root, args.archive_records, recovery)
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
    if verified_archive_identities(args.input_root, args.archive_records, recovery) != identities:
        raise ValueError("archive identity changed before payload access")
    version = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    if version != json.loads((ROOT / "configs/environment_v1.yaml").read_bytes())["host_tools"]["ffmpeg_version_line"]:
        raise ValueError("research FFmpeg mismatch")
    lineage = {"version": 1, "batch": "batch09", "queue_ranks": TARGET_RANKS, "selection": "fixed_next_final_five_no_outcome_selection",
               "acceptance": acceptance, "historical215_pending_fields_unchanged": True, "historical_AI_uncertainty_and_disagreement_preserved": True,
               "preflight_sha256": _sha256(args.preflight), "activation_CI": preflight["activation_CI"],
               "accepted_prior_report_sha256": _sha256(prior_path), "accepted_prior_document_sha256": ACCEPTED215_DOCUMENT_SHA256,
               "prior_activation_sha256": prior["activation_sha256"], "prior_effective_bundle_sha256": prior["materialized_activation_row_bundle_sha256"],
               "accepted_prior_verification_sha256": prior["private_verification_sha256"],
               "accepted_exact_report_sha256": _sha256(exact_path), "exact_pair_bundle_sha256": exact["pair_record_bundle_sha256"],
               "accepted_visual_evidence_policy_sha256": visual["policy_sha256"], "visual_code_sha256": _sha256(ROOT / "src/fas/visual.py"),
               "runner_sha256": _sha256(Path(__file__)), "frozen_artifact_sha256": frozen, "ffmpeg": version, "no_prior_artifacts_overwritten": True,
               "accepted_archive_recovery": recovery, "archive_guard_runner_sha256": _sha256(ROOT / "scripts/prepare_oulu_visual_batch06.py")}
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
    verify_preserved(preflight)
    if verified_archive_identities(args.input_root, args.archive_records, recovery) != identities:
        raise ValueError("archive changed during export")
    result = {"version": 1, "status": "batch09_private_packets_prepared_review_pending", "queue_ranks": TARGET_RANKS, "packets": packets,
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
        print("BATCH09 EXPORT FAILED: no visual adjudication or clearance claimed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())