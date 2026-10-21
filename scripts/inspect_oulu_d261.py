"""Single owner-authorized D crop investigation; no automatic disposition."""

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

from fas.freeze import write_immutable_record
from fas.lineage import decoded_tokens
from fas.oulu import _sha256
from fas.visual import png_bytes
from prepare_oulu_owner_review import private_output
from prepare_oulu_pilot243 import CAPS as PILOT_CAPS, check_bindings, checked_member, stream_frames, usage
from verify_oulu_archive_guard_batch09 import read_verified_json, verified_archive_identities

WINDOW = [86, 1132, 929, 1824]
ORDERS = {"left": [54, 72, 90], "right": [18, 37, 56]}
CAPS = dict(PILOT_CAPS)
MIB = 1024 * 1024
BASE = Path("/mnt/e/FAS-private/artifacts/phase1")
APPROVAL_SHA = "3f636ae85f9d078bdfc0feb2b83a41f176acfafabc8cda15a26bb1319ce6c4c9"
ANALYSIS_SHA = "f593249cfe9e3b13975835ed629f4f4f792510f8a9c42b11c640b7ee5b6b05f6"
PARENT_PREFLIGHT_SHA = "5021a83530b34cf2bad7051d94a41efea9845a6c54b9b2aac33a81c9d00c9916"
REVIEW_SHA = "74124cb34e513bd9d945e6d40d95032a50463efa988eb9421d7973f25f4eded2"
INTERPRETATION = {
    "linked_distinctive_temporal_or_recording_detail": "strengthens_specific_derivation_allegation_not_automatic_disposition",
    "motif_similarity_alone": "insufficient",
    "divergence": "may_reject_specific_alignment_or_localized_copy_not_whole_edge",
    "incidental_detail_absent_or_ambiguous": "inconclusive_stop_no_automatic_tier",
    "same_recording_cues": "dependent_not_independent_replication",
    "upper_regions_other_edges_394_negatives": "not_cleared",
}


def crop_frames(path: Path, media: dict, orders: list[int], *, command: list[str] | None = None) -> list[dict]:
    tokens = decoded_tokens(media)
    if (len(orders) != 3 or any(type(order) is not int for order in orders) or
            sorted(set(orders)) != orders or orders[0] < 0 or orders[-1] >= len(tokens)):
        raise ValueError("exact three distinct chronological orders required")
    if any(token[:2] != (1080, 1920) for token in tokens):
        raise ValueError("fixed native dimensions required")
    crops = []

    def consume(order, rgb):
        if order in orders:
            left, top, right, bottom = WINDOW
            crop = np.ascontiguousarray(rgb[top:bottom, left:right]).copy()
            crops.append({"decode_order": order, "source_RGB_sha256": tokens[order][2],
                          "crop_RGB_sha256": hashlib.sha256(crop.tobytes()).hexdigest(), "rgb": crop})

    stream_frames(path, media, consume, timeout=180, command=command)
    if [crop["decode_order"] for crop in crops] != orders:
        raise ValueError("crop order/count drift")
    return crops


def validate_scope(record: dict) -> None:
    if (record.get("checkpoint") != 261 or record.get("caps") != CAPS or
            record.get("approval_sha256") != APPROVAL_SHA or record.get("orders") != ORDERS or
            record.get("window_xyxy_half_open") != WINDOW or record.get("interpretation") != INTERPRETATION):
        raise ValueError("fixed approved261 scope required")


def execution_definition() -> dict:
    approval_path = BASE / "oulu_d261_owner_approval_v1.json"
    approval = read_verified_json(approval_path, APPROVAL_SHA)
    analysis_path = BASE / "oulu_witness259_analysis_v1.json"
    analysis = read_verified_json(analysis_path, ANALYSIS_SHA)
    parent_path = BASE / "oulu_investigation257_preflight_v1.json"
    parent = read_verified_json(parent_path, PARENT_PREFLIGHT_SHA)
    proposal = analysis["proposal_only"]
    if (approval.get("explicit_owner_approval") is not True or
            type(approval.get("new_real_attempts_authorized")) is not int or approval["new_real_attempts_authorized"] != 1 or
            approval.get("automatic_retry_authorized") is not False or approval.get("caps") != CAPS or
            approval.get("authority260_sha256") != REVIEW_SHA or approval.get("proposal_only_parent") != proposal or
            proposal["native_orders"] != ORDERS or proposal["native_window_xyxy_half_open"] != WINDOW):
        raise ValueError("explicit single-attempt owner authority drift")
    selected = next(case for case in analysis["cases"] if case["alias"] == "D")
    pair = read_verified_json(Path(selected["pair_path"]), selected["pair_sha256"])
    if pair != selected["pair_record"] or pair["effective_disposition"] is not None:
        raise ValueError("exact D parent drift")
    sources = {str(approval_path): APPROVAL_SHA, str(analysis_path): ANALYSIS_SHA,
               str(parent_path): PARENT_PREFLIGHT_SHA, selected["pair_path"]: selected["pair_sha256"],
               str(ROOT / "docs/260-review-doc259-five-witness-analysis.md"): REVIEW_SHA}
    videos = {}
    for side in ("left", "right"):
        identity = pair[side]
        if identity != proposal[side]:
            raise ValueError("D endpoint drift")
        endpoint = analysis["endpoint_parents"][identity]
        for path_key, hash_key in (("endpoint_path", "endpoint_sha256"), ("native_media_record_path", "native_media_record_sha256"),
                                   ("gallery_path", "gallery_sha256")):
            sources[endpoint[path_key]] = endpoint[hash_key]
        media = read_verified_json(Path(endpoint["native_media_record_path"]), endpoint["native_media_record_sha256"])
        videos[side] = {"video_id": identity, "media_path": endpoint["native_media_record_path"],
                        "media_record_sha256": endpoint["native_media_record_sha256"],
                        "frame_count": media["frame_count"], "payload_bytes": media["byte_size"]}
    if [videos[side]["frame_count"] for side in ("left", "right")] != [146, 151]:
        raise ValueError("fixed two-video counts drift")
    for name in ("scripts/inspect_oulu_d261.py", "tests/test_oulu.py", "scripts/prepare_oulu_pilot243.py",
                 "scripts/verify_oulu_archive_guard_batch09.py", "scripts/prepare_oulu_owner_review.py",
                 "src/fas/freeze.py", "src/fas/lineage.py", "src/fas/visual.py", "src/fas/oulu.py",
                 "docs/259-five-witness-edge-evidence-analysis.md", "results/phase1/oulu-witness259-analysis-v1.json"):
        sources[str(ROOT / name)] = _sha256(ROOT / name)
    check_bindings(sources)
    guard = copy.deepcopy(parent["guard_context"])
    test_path = str(ROOT / "tests/test_oulu.py")
    previous = guard["pinned_file_sha256"][test_path]
    guard["pinned_file_sha256"][test_path] = sources[test_path]
    return {"checkpoint": 261, "caps": CAPS, "approval_sha256": APPROVAL_SHA, "analysis259_sha256": ANALYSIS_SHA,
            "selected_pair_sha256": selected["pair_sha256"], "source_sha256": sources,
            "paths": parent["paths"], "guard_context": guard, "videos": videos,
            "orders": ORDERS, "window_xyxy_half_open": WINDOW, "interpretation": INTERPRETATION,
            "test_pin_transition": {"from257": previous, "to261": sources[test_path], "historical_records_unchanged": True},
            "ffmpeg": parent["ffmpeg"]}


def load_preflight(path: Path) -> dict:
    record = json.loads(path.read_bytes())
    validate_scope(record)
    if record != execution_definition():
        raise ValueError("exact execution definition/source binding drift")
    return record


def make_preflight(path: Path) -> None:
    record = execution_definition()
    private_output(path, [*map(Path, record["source_sha256"]), *map(Path, record["paths"].values())])
    if path.resolve().parent != BASE.resolve():
        raise ValueError("fixed private preflight parent required")
    write_immutable_record(path, record)


def archive_identity(handle) -> tuple[int, ...]:
    value = os.fstat(handle.fileno())
    return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns


def worker(preflight_path: Path, output: Path) -> None:
    preflight = load_preflight(preflight_path)
    lease = json.loads((BASE / "oulu_d261_attempt_lock_v1.json").read_bytes())
    if (lease["preflight_sha256"] != _sha256(preflight_path) or lease["output"] != str(output.resolve()) or
            lease["parent_pid"] != os.getppid() or os.getsid(0) != os.getpid()):
        raise ValueError("supervised single attempt required")
    paths = {key: Path(value) for key, value in preflight["paths"].items()}
    private_output(output, [preflight_path, *paths.values(), *map(Path, preflight["source_sha256"])])
    identities = verified_archive_identities(paths["input_root"], paths["archive_records"], preflight["guard_context"])
    if subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0] != preflight["ffmpeg"]:
        raise ValueError("accepted FFmpeg drift")
    media = {side: read_verified_json(Path(value["media_path"]), value["media_record_sha256"])
             for side, value in preflight["videos"].items()}
    write_immutable_record(output / "lineage.json", {"checkpoint": 261, "preflight_sha256": _sha256(preflight_path),
                           "approval_sha256": APPROVAL_SHA, "interpretation": INTERPRETATION, "new_dispositions": 0})
    with ExitStack() as stack:
        archives = {}
        for name in sorted({record["media_archive"] for record in media.values()}):
            descriptor = os.open(paths["input_root"] / name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            handle = stack.enter_context(os.fdopen(descriptor, "rb"))
            if archive_identity(handle) != identities[name]:
                raise ValueError("archive descriptor identity drift")
            archive = stack.enter_context(tarfile.open(fileobj=handle, mode="r:"))
            wanted = {record["media_relpath"]: [] for record in media.values() if record["media_archive"] == name}
            for member in archive:
                if member.name in wanted:
                    wanted[member.name].append(member)
            if any(len(matches) != 1 for matches in wanted.values()) or archive_identity(handle) != identities[name]:
                raise ValueError("selected archive members/identity drift")
            archives[name] = handle, archive, {key: value[0] for key, value in wanted.items()}
        for side in ("left", "right"):
            record = media[side]
            write_immutable_record(output / "attempts" / f"{side}.json", {"checkpoint": 261, "status": "started",
                                   "media_record_sha256": preflight["videos"][side]["media_record_sha256"]})
            handle, archive, members = archives[record["media_archive"]]
            member = members[record["media_relpath"]]
            checked_member(member, record)
            if archive_identity(handle) != identities[record["media_archive"]]:
                raise ValueError("archive changed before selected payload")
            with tempfile.TemporaryDirectory(prefix=".payload261-", dir=output) as directory:
                payload_path = Path(directory) / "media.avi"
                total, digest = 0, hashlib.sha256()
                with archive.extractfile(member) as source, payload_path.open("xb") as destination:
                    while block := source.read(MIB):
                        total += len(block)
                        if total > record["byte_size"] or total > CAPS["temporary_bytes"]:
                            raise ValueError("temporary payload cap")
                        digest.update(block)
                        destination.write(block)
                if total != record["byte_size"] or digest.hexdigest() != record["media_sha256"]:
                    raise ValueError("selected payload identity drift")
                crops = crop_frames(payload_path, record, ORDERS[side])
            if archive_identity(handle) != identities[record["media_archive"]]:
                raise ValueError("archive changed during decode")
            assets = []
            for crop in crops:
                rgb = crop.pop("rgb")
                encoded = png_bytes(rgb)
                restored = cv2.cvtColor(cv2.imdecode(np.frombuffer(encoded, np.uint8), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
                if not np.array_equal(restored, rgb):
                    raise ValueError("crop PNG RGB roundtrip")
                if sum(path.stat().st_size for path in output.rglob("*") if path.is_file()) + len(encoded) > CAPS["output_bytes"] - 8 * MIB:
                    raise ValueError("diagnostic output cap")
                path = output / "crops" / f"{side}-{crop['decode_order']:06d}.png"
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("xb") as destination:
                    destination.write(encoded)
                assets.append({**crop, "path": str(path.relative_to(output)), "sha256": _sha256(path),
                               "width": 843, "height": 692, "window_xyxy_half_open": WINDOW})
            write_immutable_record(output / "endpoints" / f"{side}.json", {
                "checkpoint": 261, "status": "success", "media_record_sha256": preflight["videos"][side]["media_record_sha256"],
                "strict_RGB_frames_verified": record["frame_count"], "native_RGB_bytes": record["frame_count"] * 1080 * 1920 * 3,
                "payload_bytes": total, "crops": assets, "scientific_disposition": None})
        if any(archive_identity(handle) != identities[name] for name, (handle, _, _) in archives.items()):
            raise ValueError("final archive descriptor drift")
    if verified_archive_identities(paths["input_root"], paths["archive_records"], preflight["guard_context"]) != identities:
        raise ValueError("final archive guard drift")
    write_immutable_record(output / "worker_completion.json", {"checkpoint": 261, "endpoints": 2, "crops": 6,
                           "guard_before_after_equal": True, "preflight_sha256": _sha256(preflight_path)})


def measured_usage(group: int, output: Path) -> dict:
    measured = usage(group, output / ".process-only")
    for path in output.rglob("*"):
        try:
            if not path.is_file():
                continue
            size = path.stat().st_size
        except FileNotFoundError:
            continue
        key = "temporary_bytes" if any(part.startswith(".payload261-") for part in path.relative_to(output).parts) else "output_bytes"
        measured[key] += size
    return measured


def finalize(preflight: dict, output: Path, failure: str | None) -> dict:
    endpoints = []
    for side, binding in preflight["videos"].items():
        path = output / "endpoints" / f"{side}.json"
        if not path.exists():
            status = "failed_or_interrupted" if (output / "attempts" / f"{side}.json").exists() else "not_run_after_stop"
            write_immutable_record(path, {"checkpoint": 261, "status": status, "reason": failure or "missing endpoint",
                                   "media_record_sha256": binding["media_record_sha256"], "scientific_disposition": None})
        endpoint = json.loads(path.read_bytes())
        if endpoint["media_record_sha256"] != binding["media_record_sha256"] or endpoint["scientific_disposition"] is not None:
            raise ValueError("endpoint parent/disposition drift")
        endpoints.append(endpoint)
        if failure is None and endpoint["status"] == "success":
            media = read_verified_json(Path(binding["media_path"]), binding["media_record_sha256"])
            if ([crop["decode_order"] for crop in endpoint["crops"]] != ORDERS[side] or
                    endpoint["strict_RGB_frames_verified"] != binding["frame_count"] or endpoint["payload_bytes"] != binding["payload_bytes"] or
                    endpoint["native_RGB_bytes"] != binding["frame_count"] * 1080 * 1920 * 3):
                raise ValueError("complete endpoint readback drift")
            for crop in endpoint["crops"]:
                path = output / crop["path"]
                if crop["path"] != f"crops/{side}-{crop['decode_order']:06d}.png" or not path.is_file() or _sha256(path) != crop["sha256"]:
                    raise ValueError("crop image path/hash drift")
                decoded = cv2.imread(str(path))
                if decoded is None:
                    raise ValueError("undecodable crop image")
                rgb = cv2.cvtColor(decoded, cv2.COLOR_BGR2RGB)
                if (rgb.shape != (692, 843, 3) or
                        hashlib.sha256(rgb.tobytes()).hexdigest() != crop["crop_RGB_sha256"] or
                        crop["source_RGB_sha256"] != media["frame_index"][crop["decode_order"]]["rgb_sha256"] or
                        crop["window_xyxy_half_open"] != WINDOW):
                    raise ValueError("crop image/source parent readback drift")
    successful = [endpoint for endpoint in endpoints if endpoint["status"] == "success"]
    completion = output / "worker_completion.json"
    if failure is None and (len(successful) != 2 or not completion.exists() or json.loads(completion.read_bytes()) != {
            "checkpoint": 261, "endpoints": 2, "crops": 6, "guard_before_after_equal": True,
            "preflight_sha256": _sha256(Path(preflight["preflight_path"]))}):
        raise ValueError("zero worker exit lacks exact complete readback")
    return {"checkpoint": 261, "technical_complete": failure is None, "failure": failure, "endpoint_rows": len(endpoints),
            "successful_endpoints": len(successful), "persisted_crops": sum(len(row.get("crops", [])) for row in endpoints),
            "strict_RGB_frames_verified": sum(row["strict_RGB_frames_verified"] for row in successful),
            "native_RGB_bytes": sum(row["native_RGB_bytes"] for row in successful),
            "selected_payload_bytes": sum(row["payload_bytes"] for row in successful),
            "file_sha256_without_summary": {str(path.relative_to(output)): _sha256(path) for path in output.rglob("*") if path.is_file()},
            "new_dispositions": 0, "scientific_readiness": False}


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
    write_immutable_record(BASE / "oulu_d261_attempt_lock_v1.json", {"checkpoint": 261, "parent_pid": os.getpid(),
                           "preflight_sha256": _sha256(preflight_path), "output": str(output.resolve()), "automatic_retry": False})
    process, code, failure = None, 1, None
    peaks = {key: 0 for key in ("rss_bytes", "temporary_bytes", "output_bytes")}
    try:
        process = subprocess.Popen([sys.executable, str(Path(__file__)), "--preflight", str(preflight_path),
                                    "--out-root", str(output), "--worker"], start_new_session=True)
        while True:
            measured = measured_usage(process.pid, output)
            measured["output_bytes"] += preflight_path.stat().st_size
            peaks = {key: max(peaks[key], value) for key, value in measured.items()}
            if (time.monotonic() - started > CAPS["whole_seconds"] or any(value > CAPS[key] for key, value in measured.items()) or
                    measured["output_bytes"] > CAPS["output_bytes"] - 8 * MIB):
                raise TimeoutError("parent wall/RSS/storage watchdog cap")
            try:
                code = process.wait(timeout=0.05)
                break
            except subprocess.TimeoutExpired:
                pass
        if code:
            failure = "worker failed; affected endpoint rows retained"
    except (OSError, TimeoutError) as error:
        failure = str(error)
    finally:
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
    for path in output.glob(".payload261-*"):
        shutil.rmtree(path)
    preflight = {**preflight, "preflight_path": str(preflight_path)}
    try:
        summary = finalize(preflight, output, failure)
    except ValueError as error:
        failure = failure or str(error)
        summary = finalize(preflight, output, failure)
    metrics = {"checkpoint": 261, "caps": CAPS, "preflight_sha256": _sha256(preflight_path),
               "elapsed_seconds": round(time.monotonic() - started, 3), "sampled_peaks": peaks,
               "watchdog_interval_seconds": 0.05, "returncode": code, "failure": failure,
               "completion_claimed": failure is None, "summary_sha256": "0" * 64,
               "final_publication_headroom_bytes": 8 * MIB}
    final_bytes = preflight_path.stat().st_size + sum(path.stat().st_size for path in output.rglob("*") if path.is_file())
    final_bytes += sum(len((json.dumps(record, indent=2, sort_keys=True) + "\n").encode()) for record in (summary, metrics)) + 8 * MIB
    if time.monotonic() - started > CAPS["whole_seconds"] or final_bytes > CAPS["output_bytes"]:
        failure = failure or "final readback resource cap"
    summary.update(technical_complete=failure is None, failure=failure)
    metrics.update(completion_claimed=summary["technical_complete"], failure=failure)
    write_immutable_record(output / "summary.json", summary)
    metrics["summary_sha256"] = _sha256(output / "summary.json")
    write_immutable_record(metrics_path, metrics)
    print("COMPLETE261" if metrics["completion_claimed"] else "PARTIAL261", json.dumps({
        key: value for key, value in summary.items() if key != "file_sha256_without_summary"}), flush=True)
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
            write_immutable_record(args.out_root / "worker_failure.json", {"checkpoint": 261, "failure": type(error).__name__ + ": " + str(error)})
            return 1
    if args.metrics is None:
        raise ValueError("parent metrics required")
    return supervise(args.preflight, args.out_root, args.metrics)


if __name__ == "__main__":
    raise SystemExit(main())