"""Owner-authorized bounded real-media correspondence investigation."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time
from contextlib import ExitStack
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import cv2
import numpy as np

from evaluate_oulu_motion253 import feature_sets
from fas.content_correspondence import PARAMETERS, frame_witness, planned_edge_rows, sample_orders, temporal_chain
from fas.freeze import write_immutable_record
from fas.oulu import _sha256
from fas.visual import png_bytes
from prepare_oulu_owner_review import private_output
from prepare_oulu_pilot243 import check_bindings, checked_member, compact_sha, stream_frames, usage
from verify_oulu_archive_guard_batch09 import read_verified_json, verified_archive_identities


MIB = 1024 * 1024
CAPS = {"whole_seconds": 7200, "decoder_seconds": 180, "rss_bytes": 2048 * MIB,
        "temporary_bytes": 128 * MIB, "feature_bytes": 128 * MIB,
        "output_bytes": 256 * MIB, "reserve_bytes": 640 * MIB}
BASE = Path("/mnt/e/FAS-private/artifacts/phase1")
APPROVAL_SHA = "2fa580a235ff9f2b7aa30cadb64a05c2ca68f9f0939a5c5c9682676b093db34d"
PLAN_SHA = "67520c44ba519afa45d9a4b76275daa33b1139dd7dc34ba56ce6713cb3dbebb9"
PILOT_SHA = "111bc614362b6e719a6aded8cff962dfef6964333ac8e3324b6087365b8ca85e"
PROVENANCE_SHA = "fa35cd8ed4281c6d9848b21374de9cd7d5b9f992044002b7d936437dc6b34c29"


def sample_features(path: Path, media: dict, *, command: list[str] | None = None) -> dict:
    orders = sample_orders(media["frame_count"])
    selected = set(orders)
    samples = []

    def consume(order, rgb):
        if order in selected:
            samples.append(rgb.copy())

    stream_frames(path, media, consume, timeout=CAPS["decoder_seconds"], command=command)
    baseline, compensated = feature_sets(samples)
    if [value["rgb_sha256"] for value in baseline] != [media["frame_index"][order]["rgb_sha256"] for order in orders]:
        raise ValueError("sample order/RGB binding drift")
    gallery = np.full((573, 288, 3), 255, np.uint8)
    for slot, (order, rgb) in enumerate(zip(orders, samples, strict=True)):
        scale = min(96 / rgb.shape[1], 171 / rgb.shape[0], 1)
        thumb = cv2.resize(rgb, (round(rgb.shape[1] * scale), round(rgb.shape[0] * scale)), interpolation=cv2.INTER_AREA)
        top, left = slot // 3 * 191, slot % 3 * 96
        cv2.putText(gallery, f"n={order}", (left + 2, top + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 0), 1)
        gallery[top + 20:top + 20 + thumb.shape[0], left:left + thumb.shape[1]] = thumb
    array_bytes = sum(value["points"].nbytes + (0 if value["descriptors"] is None else value["descriptors"].nbytes)
                      for side in (baseline, compensated) for value in side)
    return {"baseline": baseline, "compensated": compensated, "orders": orders,
            "gallery": gallery, "feature_bytes": array_bytes}


def compare_complete(left: list[dict], right: list[dict]) -> dict:
    hits = {}
    tested = []
    for first in range(1, len(left)):
        for offset in PARAMETERS["temporal_offsets"]:
            second = first + offset
            if not 1 <= second < len(right):
                continue
            witness = frame_witness(left[first], right[second])
            detail = {"left_slot": first, "right_slot": second,
                      "status": "supported_geometry" if witness is not None else "no_supported_geometry"}
            if witness is not None:
                hits[first, second] = witness
                detail.update({key: value for key, value in witness.items() if key != "inlier_points"})
            tested.append(detail)
    chain = temporal_chain(hits)
    return {"finding": "moving_content_correspondence_witness" if chain else "no_supported_witness_not_clearance",
            "tested_slot_pairs": len(tested), "geometric_hits": len(hits), "witnesses": chain,
            "feature_counts": [[len(value["points"]) for value in side] for side in (left, right)],
            "scientific_disposition": None, "capture_independence": False,
            "unresolved_reason": "witness_requires_scientific_review" if chain else "finite_method_non_detection_or_insufficient_features",
            "tested_pairs": tested}


def make_preflight(destination: Path) -> dict:
    approval_path = BASE / "oulu_investigation255_owner_approval_v1.json"
    approval = read_verified_json(approval_path, APPROVAL_SHA)
    if approval.get("explicit_owner_approval") is not True or approval.get("caps") != CAPS:
        raise ValueError("explicit fixed investigation approval required")
    pilot_path = BASE / "oulu_pilot243_preflight_v1.json"
    pilot = read_verified_json(pilot_path, PILOT_SHA)
    plan_path = BASE / "oulu_method249_plan_verification_v1.json"
    plan = read_verified_json(plan_path, PLAN_SHA)
    provenance_path = BASE / "oulu_cross_role_protocol241_provenance_v1.json"
    provenance = read_verified_json(provenance_path, PROVENANCE_SHA)["metadata_reconciliation"]
    source = dict(plan["source_record_sha256"])
    source.update({str(approval_path): APPROVAL_SHA, str(pilot_path): PILOT_SHA,
                   str(plan_path): PLAN_SHA, str(provenance_path): PROVENANCE_SHA})
    for name in ("scripts/investigate_oulu255.py", "scripts/evaluate_oulu_motion253.py",
                 "scripts/evaluate_oulu_method249.py", "scripts/prepare_oulu_pilot243.py",
                 "scripts/verify_oulu_archive_guard_batch09.py", "src/fas/content_correspondence.py",
                 "src/fas/freeze.py", "src/fas/visual.py", "src/fas/lineage.py", "tests/test_oulu.py",
                 "docs/254-review-doc253-camera-compensated-motion.md"):
        source[str(ROOT / name)] = _sha256(ROOT / name)
    if source[str(ROOT / "docs/254-review-doc253-camera-compensated-motion.md")] != approval["authority254_sha256"]:
        raise ValueError("Review254 authority drift")
    check_bindings(source)
    paths = pilot["execution_paths"]
    counts = {name: read_verified_json(Path(paths["audit_root"]) / "videos" / f"{name}.json",
                                     value["record_sha256"])["frame_count"] for name, value in plan["videos"].items()}
    rows = planned_edge_rows(provenance["members"], provenance["shared_video_components"], counts)
    previous = {row["queue_rank"]: row for row in plan["rows"]}
    if len(rows) != 399 or len(counts) != 438 or len(plan["components"]) != 91:
        raise ValueError("exact399/438/91 population required")
    for row in rows:
        if any(value != previous[row["queue_rank"]][key] for key, value in row.items()):
            raise ValueError("frozen row drift")
    guard = copy.deepcopy(pilot["guard_context"])
    test_path = str(ROOT / "tests/test_oulu.py")
    before = guard["pinned_file_sha256"][test_path]
    guard["pinned_file_sha256"][test_path] = source[test_path]
    record = {"checkpoint": 255, "caps": CAPS, "approval_sha256": APPROVAL_SHA,
              "source_sha256": source, "paths": paths, "guard_context": guard,
              "test_pin_transition": {"from243": before, "to255": source[test_path], "historical_records_unchanged": True},
              "rows": rows, "videos": plan["videos"], "components": plan["components"], "ffmpeg": pilot["ffmpeg"]}
    private_output(destination, [Path(name) for name in source])
    if destination.resolve().parent != BASE.resolve():
        raise ValueError("fixed private preflight parent required")
    write_immutable_record(destination, record)
    return record


def load_preflight(path: Path) -> dict:
    record = json.loads(path.read_bytes())
    if record.get("checkpoint") != 255 or record.get("caps") != CAPS or record.get("approval_sha256") != APPROVAL_SHA:
        raise ValueError("fixed approved255 execution required")
    approval = read_verified_json(BASE / "oulu_investigation255_owner_approval_v1.json", APPROVAL_SHA)
    if approval.get("explicit_owner_approval") is not True or approval.get("caps") != CAPS:
        raise ValueError("owner authority mismatch")
    check_bindings(record["source_sha256"])
    if record["source_sha256"].get(str(Path(__file__))) != _sha256(Path(__file__)):
        raise ValueError("runner binding required")
    plan = read_verified_json(BASE / "oulu_method249_plan_verification_v1.json", PLAN_SHA)
    if record["videos"] != plan["videos"] or record["components"] != plan["components"]:
        raise ValueError("frozen endpoint/component drift")
    expected_rows = [{key: value for key, value in row.items() if key != "existing_evidence"} for row in plan["rows"]]
    if len(record["rows"]) != 399 or record["rows"] != expected_rows:
        raise ValueError("frozen edge drift")
    return record


def archive_identity(handle) -> tuple[int, ...]:
    value = os.fstat(handle.fileno())
    return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns


def worker(preflight_path: Path, output: Path) -> None:
    preflight = load_preflight(preflight_path)
    paths = {key: Path(value) for key, value in preflight["paths"].items()}
    private_output(output, [preflight_path, *paths.values(), *map(Path, preflight["source_sha256"])])
    identities = verified_archive_identities(paths["input_root"], paths["archive_records"], preflight["guard_context"])
    if subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0] != preflight["ffmpeg"]:
        raise ValueError("accepted FFmpeg version drift")
    write_immutable_record(output / "lineage.json", {"checkpoint": 255, "preflight_sha256": _sha256(preflight_path),
                            "approval_sha256": APPROVAL_SHA, "scientific_readiness": False})
    media = {name: read_verified_json(paths["audit_root"] / "videos" / f"{name}.json", row["record_sha256"])
             for name, row in preflight["videos"].items()}
    by_rank = {row["queue_rank"]: row for row in preflight["rows"]}
    with ExitStack() as stack:
        archives = {}
        for archive_name in sorted({record["media_archive"] for record in media.values()}):
            descriptor = os.open(paths["input_root"] / archive_name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            handle = stack.enter_context(os.fdopen(descriptor, "rb"))
            if archive_identity(handle) != identities[archive_name]:
                raise ValueError("archive descriptor identity drift")
            archive = stack.enter_context(tarfile.open(fileobj=handle, mode="r:"))
            wanted = {record["media_relpath"]: [] for record in media.values() if record["media_archive"] == archive_name}
            for member in archive:
                if member.name in wanted:
                    wanted[member.name].append(member)
            if any(len(matches) != 1 for matches in wanted.values()):
                raise ValueError("duplicate/missing selected archive members")
            if archive_identity(handle) != identities[archive_name]:
                raise ValueError("archive changed during member scan")
            archives[archive_name] = handle, archive, {name: matches[0] for name, matches in wanted.items()}
        for component in preflight["components"]:
            features = {}
            feature_bytes = 0
            for identity in sorted(component["videos"]):
                record = media[identity]
                write_immutable_record(output / "attempts" / f"{identity}.json", {"checkpoint": 255,
                                       "video_id": identity, "status": "started",
                                       "media_record_sha256": preflight["videos"][identity]["record_sha256"]})
                archive_name = record["media_archive"]
                handle, archive, members = archives[archive_name]
                member = members[record["media_relpath"]]
                checked_member(member, record)
                if archive_identity(handle) != identities[archive_name]:
                    raise ValueError("archive changed before payload read")
                with tempfile.TemporaryDirectory(prefix=".payload255-", dir=output) as directory:
                    payload_path = Path(directory) / "media.avi"
                    total = 0
                    digest = hashlib.sha256()
                    with archive.extractfile(member) as source, payload_path.open("xb") as destination:
                        while block := source.read(MIB):
                            total += len(block)
                            if total > record["byte_size"] or total > CAPS["temporary_bytes"]:
                                raise ValueError("temporary payload cap")
                            digest.update(block)
                            destination.write(block)
                    if total != record["byte_size"] or digest.hexdigest() != record["media_sha256"]:
                        raise ValueError("selected payload identity drift")
                    value = sample_features(payload_path, record)
                if archive_identity(handle) != identities[archive_name]:
                    raise ValueError("archive changed during payload/decode")
                feature_bytes += value["feature_bytes"]
                if feature_bytes > CAPS["feature_bytes"]:
                    raise ValueError("component feature array cap")
                gallery = value.pop("gallery")
                encoded = png_bytes(gallery)
                restored = cv2.cvtColor(cv2.imdecode(np.frombuffer(encoded, np.uint8), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
                if not np.array_equal(restored, gallery):
                    raise ValueError("diagnostic PNG roundtrip")
                gallery_path = output / "galleries" / f"{identity}.png"
                gallery_path.parent.mkdir(parents=True, exist_ok=True)
                with gallery_path.open("xb") as destination:
                    destination.write(encoded)
                endpoint = {"checkpoint": 255, "video_id": identity, "status": "success", "orders": value["orders"],
                            "media_record_sha256": preflight["videos"][identity]["record_sha256"],
                            "strict_RGB_frames_verified": record["frame_count"], "payload_bytes": total,
                            "feature_array_bytes": value["feature_bytes"], "resident_component_feature_bytes": feature_bytes,
                            "gallery": {"path": str(gallery_path.relative_to(output)), "sha256": hashlib.sha256(encoded).hexdigest()},
                            "branches": {branch: [{"shape": item["shape"], "rgb_sha256": item["rgb_sha256"],
                                         "feature_count": len(item["points"]), "points_sha256": hashlib.sha256(item["points"].tobytes()).hexdigest(),
                                         "descriptors_sha256": None if item["descriptors"] is None else hashlib.sha256(item["descriptors"].tobytes()).hexdigest(),
                                         "registration": item.get("camera_motion")} for item in value[branch]]
                                         for branch in ("baseline", "compensated")}, "scientific_disposition": None}
                write_immutable_record(output / "endpoints" / f"{identity}.json", endpoint)
                features[identity] = value
            for rank in sorted(component["ranks"]):
                row = by_rank[rank]
                first, second = features[row["left"]], features[row["right"]]
                findings = {branch: compare_complete(first[branch], second[branch]) for branch in ("baseline", "compensated")}
                hit = any(value["witnesses"] for value in findings.values())
                parents = {side: _sha256(output / "endpoints" / f"{row[side]}.json") for side in ("left", "right")}
                result = {**row, "checkpoint": 255, "status": "screened_witness" if hit else "screened_non_detection",
                          "real_screening_performed": True, "method_coverage": "nine_quantiles_motion_regions_only",
                          "candidate_finding": "witness_requires_review" if hit else "non_detection_not_clearance",
                          "evidence": [{"endpoint_record_sha256": parents}], "branches": findings,
                          "unresolved_reason": "scientific_region_content_interpretation_pending" if hit else "finite_method_non_detection_not_clearance",
                          "effective_disposition": None}
                write_immutable_record(output / "pairs" / f"{rank:06d}.json", result)
            features.clear()
            print("COMPONENT255", len(component["videos"]), len(component["ranks"]), flush=True)
        for name, (handle, archive, members) in archives.items():
            if archive_identity(handle) != identities[name]:
                raise ValueError("final archive descriptor drift")
    if verified_archive_identities(paths["input_root"], paths["archive_records"], preflight["guard_context"]) != identities:
        raise ValueError("final archive guard drift")
    write_immutable_record(output / "worker_completion.json", {"checkpoint": 255, "preflight_sha256": _sha256(preflight_path),
                           "endpoints": 438, "pairs": 399, "guard_before_after_equal": True, "scientific_dispositions": 0})


def measured_usage(group: int, output: Path) -> dict:
    measured = usage(group, output / ".process-only")
    for path in output.rglob("*"):
        try:
            if not path.is_file():
                continue
            size = path.stat().st_size
        except FileNotFoundError:
            continue
        key = "temporary_bytes" if any(part.startswith(".payload255-") for part in path.relative_to(output).parts) else "output_bytes"
        measured[key] += size
    return measured


def finalize(preflight: dict, output: Path, failure: str | None) -> dict:
    for identity, original in preflight["videos"].items():
        path = output / "endpoints" / f"{identity}.json"
        if not path.exists():
            status = "failed_or_interrupted" if (output / "attempts" / f"{identity}.json").exists() else "not_run_after_stop"
            write_immutable_record(path, {"checkpoint": 255, "video_id": identity, "status": status,
                                   "media_record_sha256": original["record_sha256"], "reason": failure or "missing endpoint",
                                   "scientific_disposition": None})
    for row in preflight["rows"]:
        path = output / "pairs" / f"{row['queue_rank']:06d}.json"
        if not path.exists():
            write_immutable_record(path, {**row, "checkpoint": 255, "status": "not_screened_after_stop",
                                   "unresolved_reason": failure or "missing pair", "real_screening_performed": False})
    files = {str(path.relative_to(output)): _sha256(path) for path in output.rglob("*") if path.is_file()}
    endpoints = [json.loads((output / "endpoints" / f"{identity}.json").read_bytes()) for identity in preflight["videos"]]
    pairs = [json.loads((output / "pairs" / f"{row['queue_rank']:06d}.json").read_bytes()) for row in preflight["rows"]]
    successful = [row for row in endpoints if row["status"] == "success"]
    screened = [row for row in pairs if row["real_screening_performed"]]
    if failure is None and (len(successful) != 438 or len(screened) != 399 or not (output / "worker_completion.json").exists()):
        raise ValueError("worker zero exit lacks complete readback")
    if any(row["effective_disposition"] is not None for row in pairs):
        raise ValueError("unexpected scientific disposition")
    summary = {"checkpoint": 255, "technical_complete": failure is None, "failure": failure,
               "endpoint_rows": len(endpoints), "edge_rows": len(pairs), "successful_endpoints": len(successful),
               "pairs_screened": len(screened), "strict_RGB_frames_verified": sum(row["strict_RGB_frames_verified"] for row in successful),
               "selected_payload_bytes": sum(row["payload_bytes"] for row in successful),
               "maximum_component_feature_array_bytes": max((row["resident_component_feature_bytes"] for row in successful), default=0),
               "witness_pairs": {branch: sum(bool(row["branches"][branch]["witnesses"]) for row in screened)
                                 for branch in ("baseline", "compensated")},
               "any_witness_pairs": sum(any(value["witnesses"] for value in row["branches"].values()) for row in screened),
               "file_sha256_without_summary": files, "new_dispositions": 0, "scientific_readiness": False}
    write_immutable_record(output / "summary.json", summary)
    return summary


def supervise(preflight_path: Path, output: Path, metrics_path: Path) -> int:
    preflight = load_preflight(preflight_path)
    private_output(output, [preflight_path, *map(Path, preflight["source_sha256"])])
    private_output(metrics_path, [preflight_path, output])
    if output.resolve().parent != BASE.resolve() or metrics_path.resolve().parent != BASE.resolve():
        raise ValueError("fixed private output parent required")
    space = os.statvfs(BASE)
    if space.f_bavail * space.f_frsize < CAPS["reserve_bytes"]:
        raise ValueError("initial free-space reserve")
    started = time.monotonic()
    process = subprocess.Popen([sys.executable, str(Path(__file__)), "--preflight", str(preflight_path),
                                "--out-root", str(output), "--worker"], start_new_session=True)
    peaks = {key: 0 for key in ("rss_bytes", "temporary_bytes", "output_bytes")}
    failure = None
    code = 1
    try:
        while True:
            measured = measured_usage(process.pid, output)
            measured["output_bytes"] += preflight_path.stat().st_size
            peaks = {key: max(peaks[key], value) for key, value in measured.items()}
            if (time.monotonic() - started > CAPS["whole_seconds"] or
                    any(value > CAPS[key] for key, value in measured.items()) or
                    measured["output_bytes"] > CAPS["output_bytes"] - 8 * MIB):
                raise TimeoutError("parent wall/RSS/storage watchdog cap")
            try:
                code = process.wait(timeout=0.05)
                break
            except subprocess.TimeoutExpired:
                pass
        if code:
            failure = "worker failure; affected rows retained, no completion"
    except (OSError, TimeoutError) as error:
        failure = str(error)
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
    for path in output.glob(".payload255-*"):
        shutil.rmtree(path)
    try:
        summary = finalize(preflight, output, failure)
    except ValueError as error:
        failure = failure or str(error)
        summary = finalize(preflight, output, failure)
    if time.monotonic() - started > CAPS["whole_seconds"] or sum(path.stat().st_size for path in output.rglob("*") if path.is_file()) > CAPS["output_bytes"]:
        failure = failure or "final readback resource cap"
    metrics = {"checkpoint": 255, "caps": CAPS, "preflight_sha256": _sha256(preflight_path),
               "elapsed_seconds": round(time.monotonic() - started, 3), "sampled_peaks": peaks,
               "watchdog_interval_seconds": 0.05, "returncode": code, "failure": failure,
               "completion_claimed": failure is None and summary["technical_complete"], "summary_sha256": _sha256(output / "summary.json")}
    write_immutable_record(metrics_path, metrics)
    print("COMPLETE255" if metrics["completion_claimed"] else "PARTIAL255", json.dumps({key: value for key, value in summary.items() if key != "file_sha256_without_summary"}), flush=True)
    return 0 if metrics["completion_claimed"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-preflight", type=Path)
    parser.add_argument("--preflight", type=Path)
    parser.add_argument("--out-root", type=Path)
    parser.add_argument("--metrics", type=Path)
    parser.add_argument("--worker", action="store_true")
    args = parser.parse_args()
    if args.build_preflight:
        make_preflight(args.build_preflight)
        return 0
    if args.preflight is None or args.out_root is None:
        raise ValueError("preflight/output required")
    if args.worker:
        try:
            worker(args.preflight, args.out_root)
            return 0
        except Exception as error:
            write_immutable_record(args.out_root / "worker_failure.json", {"checkpoint": 255, "failure": type(error).__name__ + ": " + str(error)})
            return 1
    if args.metrics is None:
        raise ValueError("parent metrics required")
    return supervise(args.preflight, args.out_root, args.metrics)


if __name__ == "__main__":
    raise SystemExit(main())