#!/usr/bin/env python3
"""Prepare the next fixed ten private packets after accepted batch01 closure."""

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


def fixed_next_records(records: list[dict], prior: dict) -> list[dict]:
    if prior.get("batch01_accepted_reconciled_disposition_state") is not True or prior.get("current_effective_disposition_counts") != {"rejected_false_positive": 10}:
        raise ValueError("accepted batch01 closure required")
    selected = records[10:20]
    if len(selected) != 10 or any(record.get("queue_rank") != rank or record.get("priority") != "cross_role_conflicting_label" for rank, record in enumerate(selected, 10)):
        raise ValueError("fixed next queue ranks 10 through 19 required")
    return selected


def prepare(args: argparse.Namespace) -> dict:
    output = args.out_root.resolve()
    inputs = [ROOT, args.input_root, args.audit_root, args.exact_root, args.screen_root, args.frozen_root, args.archive_records, args.activation_root]
    inputs.extend(args.activation_root.parent / name for name in (
        "oulu_visual_packets_batch01_v1", "oulu_visual_review_batch01_v1", "oulu_owner_review_batch01_v1",
        "oulu_human_dispositions_batch01_v1", "oulu_pair5_reconciliation_v1", "oulu_batch01_owner_acceptance_v1",
    ))
    if args.out_root.exists() or args.out_root.is_symlink() or any(output.is_relative_to(path.resolve()) or path.resolve().is_relative_to(output) for path in inputs):
        raise ValueError("unsafe or existing output")
    preflight_path = args.activation_root.parent / "oulu_batch02_preparation_preflight_v1.json"
    preflight = json.loads(preflight_path.read_bytes())
    check = preflight["CI"]
    if check["id"] != 114107181776 or check["head_sha"] != "5f3c22c4a473770b5653a4439bf350379fc5032f" or check["status"] != "completed" or check["conclusion"] != "success":
        raise ValueError("exact successful activation CI required")
    def verify_protected() -> None:
        for root, expected in preflight["protected_snapshot"].items():
            path = Path(root)
            current = {str(file.relative_to(path)): _sha256(file) for file in sorted(path.rglob("*")) if file.is_file()}
            if current != expected:
                raise ValueError("protected prior evidence drift")
    verify_protected()
    prior = json.loads((ROOT / "results/phase1/oulu-batch01-activation-v1.json").read_bytes())
    if _sha256(args.activation_root / "summary.json") != prior["private_summary_sha256"] or _sha256(args.activation_root / "activation.json") != prior["private_activation_sha256"]:
        raise ValueError("accepted activation drift")
    prior_rows = sorted((args.activation_root / "pairs").glob("*.json"))
    def bundle(paths: list[Path], stems: bool = False) -> str:
        return hashlib.sha256("".join(f"{path.stem if stems else path.name}:{_sha256(path)}\n" for path in paths).encode()).hexdigest()
    if len(prior_rows) != 10 or bundle(prior_rows) != prior["current_effective_pair_bundle_sha256"]:
        raise ValueError("accepted current ledger drift")
    exact = json.loads((ROOT / "results/phase1/oulu-lineage-exact-evidence-v1.json").read_bytes())
    pair_paths = sorted((args.exact_root / "pairs").glob("*.json"))
    if len(pair_paths) != 6640 or bundle(pair_paths) != exact["pair_record_bundle_sha256"] or _sha256(args.exact_root / "summary.json") != exact["private_summary_sha256"]:
        raise ValueError("accepted queue drift")
    records = fixed_next_records([json.loads(path.read_bytes()) for path in pair_paths[:20]], prior)
    frozen_hashes = {path.name: _sha256(path) for path in args.frozen_root.iterdir()}
    if frozen_hashes != exact["frozen_artifact_sha256"]:
        raise ValueError("frozen inputs drift")
    visual = json.loads((ROOT / "results/phase1/oulu-visual-review-batch01-v1.json").read_bytes())
    for name, digest in visual["implementation_sha256"].items():
        if _sha256(ROOT / name) != digest:
            raise ValueError("accepted visual implementation drift")
    if _sha256(ROOT / visual["policy_file"]) != visual["policy_sha256"]:
        raise ValueError("accepted visual evidence policy drift")
    for folder, report_name, field, count in (
        (args.audit_root / "videos", "oulu-per-video-media-audit-v1.json", "video_record_bundle_sha256", 4950),
        (args.screen_root / "fingerprints", "oulu-content-screening-v1.json", "fingerprint_bundle_sha256", 4950),
    ):
        paths = sorted(folder.glob("*.json"))
        public = json.loads((ROOT / "results/phase1" / report_name).read_bytes())
        if len(paths) != count or bundle(paths, True) != public[field]:
            raise ValueError("accepted media/fingerprint bundle drift")
    identities = {}
    pins = json.loads((ROOT / "results/phase1/oulu-archive-byte-pinning-v1.json").read_bytes())
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
    lineage = {"version": 1, "batch": "batch02", "queue_ranks": list(range(10, 20)), "selection": "fixed_next_ten_no_outcome_selection",
               "preflight_sha256": _sha256(preflight_path), "activation_CI": check,
               "review126_sha256": _sha256(ROOT / "docs/126-review-doc125-oulu-batch01-activation.md"),
               "prior_activation_sha256": prior["private_activation_sha256"], "prior_effective_bundle_sha256": prior["current_effective_pair_bundle_sha256"],
               "exact_pair_bundle_sha256": exact["pair_record_bundle_sha256"], "accepted_visual_evidence_policy_sha256": visual["policy_sha256"],
               "visual_code_sha256": _sha256(ROOT / "src/fas/visual.py"), "runner_sha256": _sha256(Path(__file__)),
               "frozen_artifact_sha256": frozen_hashes, "ffmpeg": version, "no_prior_artifacts_overwritten": True}
    write_immutable_record(output / "lineage.json", lineage)
    ids = sorted({record["candidate"][side] for record in records for side in ("left", "right")})
    media = {identity: json.loads((args.audit_root / "videos" / (identity + ".json")).read_bytes()) for identity in ids}
    frames, manifests = {}, {}
    def save(path: Path, rgb: np.ndarray) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            handle.write(png_bytes(rgb))
        return _sha256(path)
    for name in sorted({row["media_archive"] for row in media.values()}):
        with tarfile.open(args.input_root / name, "r:") as archive:
            members = {member.name: member for member in archive.getmembers()}
            for identity in sorted(identity for identity in ids if media[identity]["media_archive"] == name):
                row = media[identity]
                member = members[row["media_relpath"]]
                if not member.isfile() or member.size != row["byte_size"]:
                    raise ValueError("media payload metadata drift")
                with tempfile.TemporaryDirectory(prefix="fas-visual-b02-", dir=output) as directory:
                    path = Path(directory) / "media.avi"
                    with archive.extractfile(member) as source, path.open("wb") as target:
                        shutil.copyfileobj(source, target, length=1024 * 1024)
                    if _sha256(path) != row["media_sha256"]:
                        raise ValueError("accepted payload drift")
                    frames[identity] = verified_thumbnails(path, row)
                assets = [{"decode_order": order, "accepted_rgb_sha256": row["frame_index"][order]["rgb_sha256"],
                           "thumbnail_sha256": save(output / "videos" / identity / f"{order:06d}.png", rgb)}
                          for order, rgb in enumerate(frames[identity])]
                path = output / "videos" / identity / "manifest.json"
                write_immutable_record(path, {"video_id": identity, "media_record_sha256": _sha256(args.audit_root / "videos" / (identity + ".json")),
                                             "verified_frames": assets, "temporal_orders": review_orders(len(assets))})
                manifests[identity] = _sha256(path)
                print(f"VERIFIED BATCH02 VIDEO {len(frames)}/{len(ids)}", flush=True)
    packets = []
    for rank, record in enumerate(records, 10):
        left, right = (record["candidate"][side] for side in ("left", "right"))
        assets = {name + ".png": save(output / "pairs" / f"{rank:06d}" / (name + ".png"), pair_sheet(frames[left], frames[right], slots))
                  for name, slots in (("temporal_a", list(range(0, 17, 2))), ("temporal_b", list(range(1, 17, 2))))}
        fingerprints = [json.loads((args.screen_root / "fingerprints" / (identity + ".json")).read_bytes()) for identity in (left, right)]
        distance, left_slot, right_slot = min(((int(first["phash64"], 16) ^ int(second["phash64"], 16)).bit_count(), left_slot, right_slot)
            for left_slot, first in enumerate(fingerprints[0]["samples"]) for right_slot, second in enumerate(fingerprints[1]["samples"]))
        if distance != record["candidate"]["minimum_hamming"]:
            raise ValueError("trigger witness drift")
        orders = [fingerprints[0]["samples"][left_slot]["decode_order"], fingerprints[1]["samples"][right_slot]["decode_order"]]
        assets["trigger.png"] = save(output / "pairs" / f"{rank:06d}" / "trigger.png", np.concatenate((frames[left][orders[0]], frames[right][orders[1]]), axis=1))
        path = output / "pairs" / f"{rank:06d}" / "packet.json"
        write_immutable_record(path, {"version": 1, "queue_rank": rank, "priority": record["priority"], "candidate": record["candidate"],
                                     "exact_pair_record_sha256": _sha256(pair_paths[rank]), "video_manifest_sha256": {left: manifests[left], right: manifests[right]},
                                     "image_sha256": assets, "trigger_hamming": distance, "trigger_decode_orders": orders,
                                     "review_performed": False, "disposition": "awaiting_visual_review"})
        packets.append({"queue_rank": rank, "packet_sha256": _sha256(path)})
    verify_protected()
    if {path.name: _sha256(path) for path in args.frozen_root.iterdir()} != frozen_hashes:
        raise ValueError("frozen inputs changed during export")
    for name, expected in identities.items():
        stat = (args.input_root / name).stat()
        if (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns) != expected:
            raise ValueError("archive changed during export")
    result = {"version": 1, "status": "batch02_private_packets_prepared_review_pending", "queue_ranks": list(range(10, 20)),
              "packets": packets, "unique_videos": len(ids), "all_RGB_frames_verified": sum(len(value) for value in frames.values()),
              "lineage_sha256": _sha256(output / "lineage.json"), "frozen_inputs_unchanged": True,
              "research_detector_or_model_executed": False, "scientific_readiness": False}
    write_immutable_record(output / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("input-root", "audit-root", "exact-root", "screen-root", "frozen-root", "archive-records", "activation-root", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        print(json.dumps(prepare(parser.parse_args()), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError, tarfile.TarError):
        print("BATCH02 EXPORT FAILED: no visual adjudication or closure claimed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())