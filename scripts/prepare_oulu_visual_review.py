#!/usr/bin/env python3
"""Prepare pinned private visual packets for the first ten risk-priority pairs."""

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

import cv2
import numpy as np

from fas.freeze import write_immutable_record
from fas.oulu import _sha256
from fas.visual import pair_sheet, png_bytes, review_orders, verified_thumbnails


def prepare(args: argparse.Namespace) -> dict:
    inputs, audit, exact, screening, frozen, output = (path.resolve() for path in
        (args.input_root, args.audit_root, args.exact_root, args.screen_root, args.frozen_root, args.out_root))
    if args.out_root.exists() or args.out_root.is_symlink() or not all(path.is_dir() for path in (inputs, audit, exact, screening, frozen)):
        raise ValueError("missing input or existing output")
    if any(output.is_relative_to(path) or path.is_relative_to(output) for path in (ROOT, inputs, audit, exact, screening, frozen, args.archive_records.resolve())):
        raise ValueError("unsafe private output boundary")
    exact_public = ROOT / "results/phase1/oulu-lineage-exact-evidence-v1.json"
    accepted = json.loads(exact_public.read_bytes())
    if _sha256(exact / "summary.json") != accepted["private_summary_sha256"]:
        raise ValueError("exact evidence summary drift")
    pair_paths = sorted((exact / "pairs").glob("*.json"))
    bundle = hashlib.sha256("".join(f"{path.name}:{_sha256(path)}\n" for path in pair_paths).encode()).hexdigest()
    if len(pair_paths) != 6640 or bundle != accepted["pair_record_bundle_sha256"]:
        raise ValueError("exact pair bundle drift")
    records = [json.loads(path.read_bytes()) for path in pair_paths[:10]]
    if any(record["queue_rank"] != rank or record["priority"] != "cross_role_conflicting_label" for rank, record in enumerate(records)):
        raise ValueError("fixed review batch mismatch")
    frozen_hashes = {path.name: _sha256(path) for path in frozen.iterdir()}
    if frozen_hashes != accepted["frozen_artifact_sha256"]:
        raise ValueError("frozen inputs drift")
    media_public = json.loads((ROOT / "results/phase1/oulu-per-video-media-audit-v1.json").read_bytes())
    media_paths = sorted((audit / "videos").glob("*.json"))
    media_bundle = hashlib.sha256("".join(f"{path.stem}:{_sha256(path)}\n" for path in media_paths).encode()).hexdigest()
    if len(media_paths) != 4950 or media_bundle != media_public["video_record_bundle_sha256"]:
        raise ValueError("accepted media bundle drift")
    screen_public = json.loads((ROOT / "results/phase1/oulu-content-screening-v1.json").read_bytes())
    fingerprint_paths = sorted((screening / "fingerprints").glob("*.json"))
    fingerprint_bundle = hashlib.sha256("".join(f"{path.stem}:{_sha256(path)}\n" for path in fingerprint_paths).encode()).hexdigest()
    if len(fingerprint_paths) != 4950 or fingerprint_bundle != screen_public["fingerprint_bundle_sha256"]:
        raise ValueError("accepted fingerprints drift")
    pins = json.loads((ROOT / "results/phase1/oulu-archive-byte-pinning-v1.json").read_bytes())
    identities = {}
    for name, pin in pins["media_archives"].items():
        record_path = args.archive_records / (name + ".sha256.json")
        if _sha256(record_path) != pin["private_record_sha256"]:
            raise ValueError("archive record drift")
        identity = json.loads(record_path.read_bytes())["file_identity"]
        stat = (inputs / name).stat()
        current = (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
        if current != (identity["device"], identity["inode"], pin["byte_size"], identity["mtime_ns"], identity["ctime_ns"]):
            raise ValueError("pinned archive identity drift")
        identities[name] = current
    version = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    if version != json.loads((ROOT / "configs/environment_v1.yaml").read_bytes())["host_tools"]["ffmpeg_version_line"]:
        raise ValueError("research FFmpeg mismatch")
    policy_path = ROOT / "configs/visual_review_v1.yaml"
    policy = json.loads(policy_path.read_bytes())
    if policy["selection"] != "queue_ranks_0_through_9_no_outcome_cherry_pick" or policy["independent_human_review_claimed"] is not False:
        raise ValueError("visual batch policy drift")
    lineage = {"version": 1, "policy": policy, "policy_sha256": _sha256(policy_path),
               "review_sha256": _sha256(ROOT / "docs/114-review-doc113-oulu-lineage-exact-evidence.md"),
               "accepted_exact_report_sha256": _sha256(exact_public), "exact_pair_bundle_sha256": bundle,
               "accepted_media_record_bundle_sha256": media_bundle, "fingerprint_bundle_sha256": fingerprint_bundle,
               "frozen_artifact_sha256": frozen_hashes, "visual_code_sha256": _sha256(ROOT / "src/fas/visual.py"),
               "runner_sha256": _sha256(Path(__file__)), "ffmpeg": version, "opencv": cv2.__version__, "numpy": np.__version__}
    write_immutable_record(output / "lineage.json", lineage)
    ids = sorted({record["candidate"][side] for record in records for side in ("left", "right")})
    media = {identity: json.loads((audit / "videos" / (identity + ".json")).read_bytes()) for identity in ids}
    frames = {}
    manifests = {}

    def save_png(path: Path, rgb: np.ndarray) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            handle.write(png_bytes(rgb))
        return _sha256(path)

    for name in sorted({row["media_archive"] for row in media.values()}):
        with tarfile.open(inputs / name, "r:") as archive:
            members = {member.name: member for member in archive.getmembers()}
            for identity in sorted(identity for identity, row in media.items() if row["media_archive"] == name):
                row = media[identity]
                member = members[row["media_relpath"]]
                if not member.isfile() or member.size != row["byte_size"]:
                    raise ValueError("media payload metadata drift")
                with tempfile.TemporaryDirectory(prefix="fas-visual-", dir=output) as directory:
                    path = Path(directory) / "media.avi"
                    with archive.extractfile(member) as source, path.open("wb") as target:
                        shutil.copyfileobj(source, target, length=1024 * 1024)
                    if path.stat().st_size != row["byte_size"] or _sha256(path) != row["media_sha256"]:
                        raise ValueError("accepted payload digest drift")
                    frames[identity] = verified_thumbnails(path, row)
                assets = []
                for order, frame in enumerate(frames[identity]):
                    path = output / "videos" / identity / f"{order:06d}.png"
                    assets.append({"decode_order": order, "accepted_rgb_sha256": row["frame_index"][order]["rgb_sha256"],
                                   "timestamp_seconds": row["frame_index"][order]["timestamp_seconds"], "thumbnail_sha256": save_png(path, frame)})
                manifest = {"video_id": identity, "media_record_sha256": _sha256(audit / "videos" / (identity + ".json")),
                            "media_sha256": row["media_sha256"], "verified_frames": assets, "temporal_orders": review_orders(len(assets))}
                path = output / "videos" / identity / "manifest.json"
                write_immutable_record(path, manifest)
                manifests[identity] = _sha256(path)
                print(f"VERIFIED PRIVATE REVIEW VIDEO {len(frames)}/{len(ids)}", flush=True)
    packets = []
    for rank, record in enumerate(records):
        left, right = (record["candidate"][side] for side in ("left", "right"))
        assets = {}
        for panel, slots in (("temporal_a", list(range(0, 17, 2))), ("temporal_b", list(range(1, 17, 2)))):
            assets[panel + ".png"] = save_png(output / "pairs" / f"{rank:06d}" / (panel + ".png"), pair_sheet(frames[left], frames[right], slots))
        fingerprints = [json.loads((screening / "fingerprints" / (identity + ".json")).read_bytes()) for identity in (left, right)]
        distance, left_slot, right_slot = min(((int(first["phash64"], 16) ^ int(second["phash64"], 16)).bit_count(), left_slot, right_slot)
            for left_slot, first in enumerate(fingerprints[0]["samples"]) for right_slot, second in enumerate(fingerprints[1]["samples"]))
        if distance != record["candidate"]["minimum_hamming"]:
            raise ValueError("trigger witness drift")
        orders = [fingerprints[0]["samples"][left_slot]["decode_order"], fingerprints[1]["samples"][right_slot]["decode_order"]]
        witness = np.concatenate((frames[left][orders[0]], frames[right][orders[1]]), axis=1)
        assets["trigger.png"] = save_png(output / "pairs" / f"{rank:06d}" / "trigger.png", witness)
        packet = {"version": 1, "queue_rank": rank, "priority": record["priority"], "candidate": record["candidate"],
                  "exact_pair_record_sha256": _sha256(pair_paths[rank]), "video_manifest_sha256": {left: manifests[left], right: manifests[right]},
                  "image_sha256": assets, "trigger_hamming": distance, "trigger_decode_orders": orders,
                  "review_performed": False, "disposition": "awaiting_visual_review"}
        path = output / "pairs" / f"{rank:06d}" / "packet.json"
        write_immutable_record(path, packet)
        packets.append({"queue_rank": rank, "packet_sha256": _sha256(path)})
    if {path.name: _sha256(path) for path in frozen.iterdir()} != frozen_hashes or _sha256(policy_path) != lineage["policy_sha256"]:
        raise ValueError("frozen inputs changed during visual export")
    for name, expected in identities.items():
        stat = (inputs / name).stat()
        if (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns) != expected:
            raise ValueError("archive changed during visual export")
    result = {"version": 1, "status": "private_visual_packets_prepared_review_pending", "fixed_batch_pairs": 10,
              "unique_videos": len(ids), "all_RGB_frames_verified": sum(len(value) for value in frames.values()),
              "packets": packets, "lineage_sha256": _sha256(output / "lineage.json"), "frozen_inputs_unchanged": True,
              "private_thumbnails_persisted": True, "research_detector_or_model_executed": False, "scientific_readiness": False}
    write_immutable_record(output / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("input-root", "audit-root", "exact-root", "screen-root", "frozen-root", "archive-records", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        print(json.dumps(prepare(parser.parse_args()), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError, tarfile.TarError):
        print("VISUAL PACKET EXPORT FAILED: inspect private partial evidence; no review completion claimed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())