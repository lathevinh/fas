#!/usr/bin/env python3
"""Prepare fixed queue ranks30..39 after accepted batch03 activation."""

from __future__ import annotations

import argparse
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


def fixed_next_records(records: list[dict], prior: dict) -> list[dict]:
    if prior.get("batch03_accepted_reconciled_disposition_state") is not True or prior.get("effective_dispositions_activated") != 10 or prior.get("current_effective_disposition_counts") != {"rejected_false_positive": 10}:
        raise ValueError("accepted batch03 closure required")
    selected = records[30:40]
    if len(selected) != 10 or any(row.get("queue_rank") != rank or row.get("priority") != "cross_role_conflicting_label" for rank, row in enumerate(selected, 30)):
        raise ValueError("fixed next ranks30 through39 required")
    return selected


def bundle(paths: list[Path], stems: bool = False) -> str:
    return hashlib.sha256("".join(f"{path.stem if stems else path.name}:{_sha256(path)}\n" for path in paths).encode()).hexdigest()


def prepare(args: argparse.Namespace) -> dict:
    phase = args.activation_root.parent
    preflight_path = phase / "oulu_batch04_preparation_preflight_v1.json"
    private_output(args.out_root, [args.input_root, args.audit_root, args.exact_root, args.screen_root, args.frozen_root, args.archive_records, args.activation_root, preflight_path])
    preflight = json.loads(preflight_path.read_bytes())
    private_output(args.out_root, [Path(name) for name in preflight["protected_snapshots"]])
    check = preflight["activation_CI"]
    if check["head_sha"] != "ec244d2ff9a7c6db28d236aa6b0dc01f83c36e43" or check["run_id"] != 38325981545 or check["job_id"] != 115064633017 or check["status"] != "completed" or check["conclusion"] != "success":
        raise ValueError("exact successful batch03 activation CI required")
    if _sha256(Path(__file__)) != preflight["preparation_code_sha256"]:
        raise ValueError("preparation implementation drift")
    def verify_protected() -> None:
        for root, expected in preflight["protected_snapshots"].items():
            folder = Path(root)
            actual = {str(path.relative_to(folder)): _sha256(path) for path in sorted(folder.rglob("*")) if path.is_file()}
            if actual != expected:
                raise ValueError("protected prior evidence drift")
    verify_protected()
    prior_path = ROOT / "results/phase1/oulu-batch03-activation-v1.json"
    prior = json.loads(prior_path.read_bytes())
    if _sha256(prior_path) != preflight["accepted_prior_report_sha256"] or _sha256(args.activation_root / "summary.json") != prior["private_summary_sha256"] or _sha256(args.activation_root / "activation.json") != prior["private_activation_sha256"] or _sha256(args.activation_root / "successful_CI_observation.json") != prior["private_successful_CI_observation_sha256"]:
        raise ValueError("accepted activation drift")
    rows = sorted((args.activation_root / "pairs").glob("*.json"))
    if len(rows) != 10 or bundle(rows) != prior["current_effective_pair_bundle_sha256"]:
        raise ValueError("accepted current ledger drift")
    exact_path = ROOT / "results/phase1/oulu-lineage-exact-evidence-v1.json"
    exact = json.loads(exact_path.read_bytes())
    paths = sorted((args.exact_root / "pairs").glob("*.json"))
    if len(paths) != 6640 or bundle(paths) != exact["pair_record_bundle_sha256"] or _sha256(args.exact_root / "summary.json") != exact["private_summary_sha256"]:
        raise ValueError("accepted queue drift")
    records = fixed_next_records([json.loads(path.read_bytes()) for path in paths[:40]], prior)
    frozen = {path.name: _sha256(path) for path in args.frozen_root.iterdir()}
    if frozen != exact["frozen_artifact_sha256"]:
        raise ValueError("frozen input drift")
    visual = json.loads((ROOT / "results/phase1/oulu-visual-review-batch01-v1.json").read_bytes())
    for name, digest in visual["implementation_sha256"].items():
        if _sha256(ROOT / name) != digest:
            raise ValueError("accepted visual implementation drift")
    if _sha256(ROOT / visual["policy_file"]) != visual["policy_sha256"]:
        raise ValueError("accepted visual evidence policy drift")
    for report_name in ("oulu-batch02-packets-v1.json", "oulu-batch03-packets-v1.json"):
        accepted = json.loads((ROOT / "results/phase1" / report_name).read_bytes())
        if _sha256(ROOT / accepted["runner_file"]) != accepted["runner_sha256"]:
            raise ValueError("accepted prior batch runner drift")
    for folder, report, field in ((args.audit_root / "videos", "oulu-per-video-media-audit-v1.json", "video_record_bundle_sha256"), (args.screen_root / "fingerprints", "oulu-content-screening-v1.json", "fingerprint_bundle_sha256")):
        files = sorted(folder.glob("*.json"))
        if len(files) != 4950 or bundle(files, True) != json.loads((ROOT / "results/phase1" / report).read_bytes())[field]:
            raise ValueError("accepted media/fingerprint bundle drift")
    pins = json.loads((ROOT / "results/phase1/oulu-archive-byte-pinning-v1.json").read_bytes())
    identities = {}
    for name, pin in pins["media_archives"].items():
        path = args.archive_records / (name + ".sha256.json")
        if _sha256(path) != pin["private_record_sha256"]:
            raise ValueError("archive pin drift")
        identity = json.loads(path.read_bytes())["file_identity"]
        stat = (args.input_root / name).stat()
        current = (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
        if current != (identity["device"], identity["inode"], pin["byte_size"], identity["mtime_ns"], identity["ctime_ns"]):
            raise ValueError("archive identity drift")
        identities[name] = current
    version = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    if version != json.loads((ROOT / "configs/environment_v1.yaml").read_bytes())["host_tools"]["ffmpeg_version_line"]:
        raise ValueError("research FFmpeg mismatch")
    review_path = ROOT / "docs/144-review-doc143-oulu-batch03-activation.md"
    if _sha256(review_path) != preflight["review144_sha256"]:
        raise ValueError("review authority drift")
    lineage = {"version": 1, "batch": "batch04", "queue_ranks": list(range(30, 40)), "selection": "fixed_next_ten_no_outcome_selection",
               "review144_sha256": _sha256(review_path), "preflight_sha256": _sha256(preflight_path), "activation_CI": check,
               "accepted_prior_report_sha256": _sha256(prior_path), "prior_activation_sha256": prior["private_activation_sha256"], "prior_effective_bundle_sha256": prior["current_effective_pair_bundle_sha256"],
               "accepted_exact_report_sha256": _sha256(exact_path), "exact_pair_bundle_sha256": exact["pair_record_bundle_sha256"],
               "accepted_visual_evidence_policy_sha256": visual["policy_sha256"], "visual_code_sha256": _sha256(ROOT / "src/fas/visual.py"),
               "runner_sha256": _sha256(Path(__file__)), "frozen_artifact_sha256": frozen, "ffmpeg": version, "no_prior_artifacts_overwritten": True}
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
                with tempfile.TemporaryDirectory(prefix="fas-visual-b04-", dir=output) as directory:
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
                print(f"VERIFIED BATCH04 VIDEO {len(frames)}/{len(ids)}", flush=True)
    packets = []
    for rank, row in enumerate(records, 30):
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
    verify_protected()
    for name, expected in identities.items():
        stat = (args.input_root / name).stat()
        if (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns) != expected:
            raise ValueError("archive changed during export")
    result = {"version": 1, "status": "batch04_private_packets_prepared_review_pending", "queue_ranks": list(range(30, 40)), "packets": packets,
              "unique_videos": len(ids), "all_RGB_frames_verified": sum(len(value) for value in frames.values()), "lineage_sha256": _sha256(output / "lineage.json"),
              "frozen_inputs_unchanged": True, "prior_evidence_unchanged": True, "research_detector_or_model_executed": False, "scientific_readiness": False}
    write_immutable_record(output / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("input-root", "audit-root", "exact-root", "screen-root", "frozen-root", "archive-records", "activation-root", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        print(json.dumps(prepare(parser.parse_args()), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError, tarfile.TarError):
        print("BATCH04 EXPORT FAILED: no visual adjudication or clearance claimed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())