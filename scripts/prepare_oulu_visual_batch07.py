#!/usr/bin/env python3
"""Prepare fixed ranks60..69 under additive Review190 batch06 acceptance."""

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

REVIEW190_SHA256 = "6187b4bdc810c5e1e8dda38a4945e6551cd7020e5f5436b678e087d1c97ac0a2"
ACCEPTED189_REPORT_SHA256 = "351b4d234455bfae4c74b912a06aff267b9729dff888f91725fe31b074f8fdb1"
TARGET_RANKS = list(range(60, 70))


def verified_packet_authority(preflight: dict) -> dict:
    acceptance = preflight.get("acceptance")
    if not isinstance(acceptance, dict) or acceptance.get("review190_sha256") != REVIEW190_SHA256:
        raise ValueError("explicit additive Review190 authority required")
    if _sha256(ROOT / "docs/190-review-doc189-oulu-batch06-activation.md") != REVIEW190_SHA256:
        raise ValueError("Review190 authority drift")
    if preflight.get("accepted_prior_report_sha256") != ACCEPTED189_REPORT_SHA256 or _sha256(ROOT / "results/phase1/oulu-batch06-activation-v1.json") != ACCEPTED189_REPORT_SHA256:
        raise ValueError("accepted189 report drift")
    if type(preflight.get("checkpoint")) is not int or preflight["checkpoint"] != 191 or preflight.get("packet_preparation_authorized") is not True:
        raise ValueError("checkpoint191 packet preparation required")
    ranks = preflight.get("queue_ranks")
    if ranks != TARGET_RANKS or any(type(rank) is not int for rank in ranks):
        raise ValueError("fixed integer ranks60 through69 required")
    check = preflight.get("activation_CI")
    expected = {"head_sha": "a81bd9259478a8a49ad0783fdb777329791a99d5", "run_id": 38696814671,
                "job_id": 116295204960, "status": "completed", "conclusion": "success",
                "job_status": "completed", "job_conclusion": "success"}
    if not isinstance(check, dict) or any(type(check.get(key)) is not type(value) or check[key] != value for key, value in expected.items()):
        raise ValueError("exact successful189 head/run/validate CI required")
    recovery = preflight.get("accepted_recovery")
    if not isinstance(recovery, dict) or recovery.get("accepted_by_Review178") is not True:
        raise ValueError("accepted archive recovery required")
    return acceptance


def fixed_next_records(records: list[dict], prior: dict, acceptance: dict) -> list[dict]:
    if acceptance.get("batch06_activation_checkpoint_accepted") is not True or acceptance.get("batch06_screen_level_review_closed") is not True or type(acceptance.get("accepted_current_total")) is not int or acceptance["accepted_current_total"] != 60 or acceptance.get("accepted_batch06_disposition_counts") != {"rejected_false_positive": 10}:
        raise ValueError("additive Review190 batch06 closure required")
    if prior.get("activation_checkpoint_review_pending") is not True or prior.get("batch06_accepted_reconciled_disposition_state") is not False or prior.get("accepted_batch06_current_effective_dispositions") != 0 or prior.get("effective_dispositions_activated") != 10 or prior.get("current_materialized_disposition_counts") != {"rejected_false_positive": 10} or prior.get("accepted_current_total") != 50 or prior.get("prospective_total_after_acceptance") != 60 or prior.get("batch06_closed") is not False or prior.get("stop_for_prospective_scientific_decision") is not False:
        raise ValueError("unchanged historical189 activation required")
    selected = records[60:70]
    if len(selected) != 10 or any(type(row.get("queue_rank")) is not int or row["queue_rank"] != rank or row.get("priority") != "cross_role_conflicting_label" for rank, row in enumerate(selected, 60)):
        raise ValueError("fixed next integer ranks60 through69 required")
    return selected


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
    prior_path = ROOT / "results/phase1/oulu-batch06-activation-v1.json"
    prior = json.loads(prior_path.read_bytes())
    for name, field in (("summary.json", "private_summary_sha256"), ("activation.json", "private_activation_sha256"),
                        ("successful_CI_observation.json", "private_successful_CI_observation_sha256")):
        if _sha256(args.activation_root / name) != prior[field]:
            raise ValueError("accepted189 private activation drift")
    rows = sorted((args.activation_root / "pairs").glob("*.json"))
    if len(rows) != 10 or bundle(rows) != prior["current_effective_pair_bundle_sha256"]:
        raise ValueError("accepted189 ten-row bundle drift")
    for rank, path in enumerate(rows, 50):
        row = json.loads(path.read_bytes())
        if type(row["queue_rank"]) is not int or row["queue_rank"] != rank or row["effective_disposition"] != "rejected_false_positive" or row["effective_disposition_activated"] is not True or row["activation_checkpoint_review_pending"] is not True or row["counts_as_accepted_current_effective_disposition"] is not False or row["activation_sha256"] != prior["private_activation_sha256"] or row["screen_semantic_acceptance_source"] != "Review188" or row["stop_for_prospective_scientific_decision"] is not False:
            raise ValueError("historical189 activation row drift")
    exact_path = ROOT / "results/phase1/oulu-lineage-exact-evidence-v1.json"
    exact = json.loads(exact_path.read_bytes())
    paths = sorted((args.exact_root / "pairs").glob("*.json"))
    if len(paths) != 6640 or bundle(paths) != exact["pair_record_bundle_sha256"] or _sha256(args.exact_root / "summary.json") != exact["private_summary_sha256"]:
        raise ValueError("accepted queue drift")
    records = fixed_next_records([json.loads(path.read_bytes()) for path in paths[:70]], prior, acceptance)
    frozen = {path.name: _sha256(path) for path in args.frozen_root.iterdir()}
    if frozen != exact["frozen_artifact_sha256"]:
        raise ValueError("frozen input drift")
    visual = json.loads((ROOT / "results/phase1/oulu-visual-review-batch01-v1.json").read_bytes())
    for name, digest in visual["implementation_sha256"].items():
        if _sha256(ROOT / name) != digest:
            raise ValueError("accepted visual implementation drift")
    if _sha256(ROOT / visual["policy_file"]) != visual["policy_sha256"]:
        raise ValueError("accepted visual evidence policy drift")
    for report_name in ("oulu-batch02-packets-v1.json", "oulu-batch03-packets-v1.json", "oulu-batch04-packets-v1.json", "oulu-batch05-packets-v1.json", "oulu-batch06-packet-retry-v1.json"):
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
    lineage = {"version": 1, "batch": "batch07", "queue_ranks": TARGET_RANKS, "selection": "fixed_next_ten_no_outcome_selection",
               "acceptance": acceptance, "historical189_pending_fields_unchanged": True, "preflight_sha256": _sha256(args.preflight), "activation_CI": preflight["activation_CI"],
               "accepted_prior_report_sha256": _sha256(prior_path), "prior_activation_sha256": prior["private_activation_sha256"], "prior_effective_bundle_sha256": prior["current_effective_pair_bundle_sha256"],
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
                with tempfile.TemporaryDirectory(prefix="fas-visual-b07-", dir=output) as directory:
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
                print(f"VERIFIED BATCH07 VIDEO {len(frames)}/{len(ids)}", flush=True)
    packets = []
    for rank, row in enumerate(records, 60):
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
    result = {"version": 1, "status": "batch07_private_packets_prepared_review_pending", "queue_ranks": TARGET_RANKS, "packets": packets,
              "unique_videos": len(ids), "all_RGB_frames_verified": sum(len(value) for value in frames.values()), "lineage_sha256": _sha256(output / "lineage.json"),
              "accepted_current_total": 60, "new_AI_human_effective_dispositions": 0, "historical189_pending_fields_unchanged": True,
              "frozen_inputs_unchanged": True, "prior_evidence_unchanged": True, "research_detector_or_model_executed": False, "scientific_readiness": False}
    write_immutable_record(output / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("input-root", "audit-root", "exact-root", "screen-root", "frozen-root", "archive-records", "activation-root", "preflight", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        print(json.dumps(prepare(parser.parse_args()), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError, tarfile.TarError):
        print("BATCH07 EXPORT FAILED: no visual adjudication or clearance claimed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())