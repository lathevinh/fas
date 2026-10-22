"""Owner-authorized single SCRFD acquisition and source-only OULU pilot."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import os
import signal
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.oulu import _sha256

BASE = Path("/mnt/e/FAS-private/artifacts/phase1")
OUTPUT = BASE / "oulu_preprocessing274_v1"
URL = "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip"
CAPS = {"wall_seconds": 1800, "gpu_seconds": 600, "rss_bytes": 4 * 1024 ** 3,
        "output_bytes": 512 * 1024 ** 2, "transactions": 32}
MODEL_SHA = "5838f7fe053675b1c7a08b633df49e7af5495cee0493c7dcf6697200b85b5b91"
FROZEN = Path("/mnt/e/FAS-private/frozen/source_roles_v2")
TRANSACTIONS = Path("/mnt/e/FAS-private/frozen/oulu_transactions_v1")


def read_json(path: Path) -> dict:
    return json.loads(path.read_bytes())


def bind(path: Path, expected: str, sources: dict) -> dict:
    from verify_oulu_archive_guard_batch09 import read_verified_json

    value = read_verified_json(path, expected)
    sources[str(path)] = expected
    return value


def selection(rows: list[dict]) -> list[dict]:
    selected = []
    if len({row["video_id"] for row in rows}) != len(rows):
        raise ValueError("duplicate transaction identity")
    for label in ("bona_fide", "attack"):
        candidates = [row for row in rows if row["role"] == "train" and row["binary_label"] == label]
        candidates.sort(key=lambda row: hashlib.sha256(("oulu274:" + row["video_id"]).encode()).hexdigest())
        if len(candidates) < 16:
            raise ValueError("balanced source-only shard unavailable")
        selected.extend(candidates[:16])
    return sorted(selected, key=lambda row: hashlib.sha256(("oulu274:" + row["video_id"]).encode()).hexdigest())


def make_plan() -> dict:
    from verify_oulu_archive_guard_batch09 import verified_archive_identities

    if (OUTPUT / "archive_identity_blocker.json").exists():
        raise ValueError("recorded archive identity blocker requires separate recovery authority; no pilot")
    if (OUTPUT / "plan.json").exists() or (OUTPUT / "attempt_lock.json").exists():
        raise FileExistsError("single pilot plan/attempt already exists")
    approval = read_json(OUTPUT / "owner_approval.json")
    if approval["explicit_owner_approval"] is not True or approval["caps"] != CAPS:
        raise ValueError("explicit pilot approval required")
    if time.time() >= approval["deadline_unix_seconds"]:
        raise TimeoutError("package deadline before pilot")
    sources = {}
    audit = bind(BASE / "oulu_benchmark272_audit_v1.json",
                 "fdf57e7dbb06c637498a8d7501007948815c27cb18fa0a07e32b64244d801e1b", sources)
    parents = audit["source_sha256"]
    frozen_roles = FROZEN / "oulu_npu_roles.csv"
    if _sha256(frozen_roles) != parents[str(frozen_roles)]:
        raise ValueError("frozen roles drift")
    sources[str(frozen_roles)] = parents[str(frozen_roles)]
    roles = {row["video_id"]: row for row in csv.DictReader(frozen_roles.read_text().splitlines())}
    rows = []
    for path in sorted((TRANSACTIONS / "transactions").glob("*.json")):
        record = bind(path, parents[str(path)], sources)
        if record["role"] != roles[record["video_id"]]["role"] or record["binary_label"] != roles[record["video_id"]]["binary_label"]:
            raise ValueError("frozen transaction/role join drift")
        rows.append(record)
    if len(rows) != 4950 or sum(row["selected_frame"] is not None for row in rows) != 4949:
        raise ValueError("original population/terminal accounting drift")
    chosen = selection(rows)
    parent = bind(BASE / "oulu_investigation257_preflight_v1.json",
                  "5021a83530b34cf2bad7051d94a41efea9845a6c54b9b2aac33a81c9d00c9916", sources)
    guard = copy.deepcopy(parent["guard_context"])
    guard["pinned_file_sha256"][str(ROOT / "tests/test_oulu.py")] = _sha256(ROOT / "tests/test_oulu.py")
    identities = verified_archive_identities(Path(parent["paths"]["input_root"]),
                                              Path(parent["paths"]["archive_records"]), guard)
    videos = []
    for row in chosen:
        media_path = BASE / "oulu_per_video_audit_v1/videos" / (row["video_id"] + ".json")
        media = bind(media_path, row["media_record_sha256"], sources)
        if row["media_sha256"] != media["media_sha256"] or row["selected_frame"] is None:
            raise ValueError("selected frame/media mismatch; no substitution")
        videos.append({"transaction": row, "media_path": str(media_path)})
    for name in ("configs/preprocessing_pilot_v1.yaml", "configs/preprocessing_v2.yaml",
                 "src/fas/preprocessing.py", "scripts/preprocess_oulu274.py", "tests/test_preprocessing.py",
                 "scripts/prepare_oulu_pilot243.py", "scripts/verify_oulu_archive_guard_batch09.py",
                 "docs/273-review-doc272-oulu-local-audit-complete.md"):
        sources[str(ROOT / name)] = _sha256(ROOT / name)
    if _sha256(OUTPUT / "det_10g.onnx") != MODEL_SHA:
        raise ValueError("approved model weight drift")
    for name in ("owner_approval.json", "acquisition.json"):
        sources[str(OUTPUT / name)] = _sha256(OUTPUT / name)
    plan = {"checkpoint": 274, "videos": videos, "sources": sources,
            "caps": CAPS, "guard_context": guard, "paths": parent["paths"],
            "archive_identities": {name: list(value) for name, value in identities.items()},
            "ffmpeg": parent["ffmpeg"], "model_sha256": MODEL_SHA,
            "deadline_unix_seconds": approval["deadline_unix_seconds"],
            "selection_rule": "16_per_label_train_sha256_oulu274_colon_video_id_no_replacement"}
    write_immutable_record(OUTPUT / "plan.json", plan)
    return plan


def measured_usage(group: int) -> dict:
    from prepare_oulu_pilot243 import usage

    result = usage(group, OUTPUT / ".no_file_tree")
    total = 0
    for path in OUTPUT.rglob("*"):
        try:
            if path.is_file():
                total += path.stat().st_size
        except FileNotFoundError:
            continue
    result["output_bytes"] = total + result["temporary_bytes"]
    return result


def worker() -> None:
    import cv2
    import numpy as np
    import onnxruntime as ort
    from fas.preprocessing import detect_face, shared_context_crop
    from fas.visual import png_bytes
    from inspect_oulu_d261 import archive_identity
    from prepare_oulu_pilot243 import checked_member, check_bindings, stream_frames
    from verify_oulu_archive_guard_batch09 import verified_archive_identities

    plan = read_json(OUTPUT / "plan.json")
    lease = read_json(OUTPUT / "attempt_lock.json")
    if lease["plan_sha256"] != _sha256(OUTPUT / "plan.json") or lease["parent_pid"] != os.getppid() or os.getsid(0) != os.getpid():
        raise ValueError("single supervised attempt required")
    remaining = plan["deadline_unix_seconds"] - time.time()
    if remaining <= 0:
        raise TimeoutError("package deadline")
    signal.signal(signal.SIGALRM, lambda signum, frame: (_ for _ in ()).throw(TimeoutError("package deadline")))
    signal.setitimer(signal.ITIMER_REAL, remaining)
    check_bindings(plan["sources"])
    if _sha256(OUTPUT / "det_10g.onnx") != MODEL_SHA:
        raise ValueError("model drift before inference")
    if subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0] != plan["ffmpeg"]:
        raise ValueError("accepted decoder version drift")
    options = ort.SessionOptions()
    options.intra_op_num_threads = options.inter_op_num_threads = 1
    session = ort.InferenceSession(str(OUTPUT / "det_10g.onnx"), sess_options=options, providers=["CPUExecutionProvider"])
    if session.get_providers() != ["CPUExecutionProvider"]:
        raise ValueError("fixed CPU provider required")
    cv2.setNumThreads(1)
    results, tiles = [], []
    native_frames, payload_bytes, inference_seconds = 0, 0, 0.0
    indexed = {}
    for index, row in enumerate(plan["videos"]):
        media = read_json(Path(row["media_path"]))
        indexed.setdefault(media["media_archive"], []).append((index, row, media))
    for archive_name, members in sorted(indexed.items()):
        path = Path(plan["paths"]["input_root"]) / archive_name
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as handle, tarfile.open(fileobj=handle, mode="r:") as archive:
            expected_identity = tuple(plan["archive_identities"][archive_name])
            if archive_identity(handle) != expected_identity:
                raise ValueError("archive identity drift before payload")
            headers = {}
            wanted = {media["media_relpath"] for _, _, media in members}
            for member in archive:
                if member.name in wanted:
                    if member.name in headers:
                        raise ValueError("duplicate selected tar member")
                    headers[member.name] = member
            for index, row, media in members:
                transaction = row["transaction"]
                selected = transaction["selected_frame"]
                if archive_identity(handle) != expected_identity:
                    raise ValueError("archive drift before selected payload")
                member = headers[media["media_relpath"]]
                checked_member(member, media)
                write_immutable_record(OUTPUT / "attempts" / f"{index:02d}.json", {"index": index, "status": "started"})
                with tempfile.TemporaryDirectory(prefix=".payload274-", dir=OUTPUT) as temporary:
                    video_path = Path(temporary) / "selected.avi"
                    digest, total = hashlib.sha256(), 0
                    with archive.extractfile(member) as source, video_path.open("xb") as destination:
                        while block := source.read(1024 ** 2):
                            total += len(block)
                            if total > media["byte_size"] or total > 128 * 1024 ** 2:
                                raise ValueError("payload cap")
                            digest.update(block)
                            destination.write(block)
                    if total != media["byte_size"] or digest.hexdigest() != media["media_sha256"]:
                        raise ValueError("selected payload hash drift")
                    captured = []

                    def consume(order, rgb):
                        if order == selected["decode_order"]:
                            if hashlib.sha256(rgb.tobytes()).hexdigest() != selected["rgb_sha256"] or rgb.shape != (selected["height"], selected["width"], 3):
                                raise ValueError("frozen selected RGB drift")
                            captured.append(rgb.copy())

                    stream_frames(video_path, media, consume, timeout=min(180, max(0.001, plan["deadline_unix_seconds"] - time.time())))
                    if len(captured) != 1:
                        raise ValueError("exact selected frame missing")
                native_frames += media["frame_count"]
                payload_bytes += total
                result = {"index": index, "video_id": transaction["video_id"], "binary_label": transaction["binary_label"],
                          "role": transaction["role"], "selected_frame": selected, "media_record_sha256": transaction["media_record_sha256"],
                          "retain_original_denominator": True, "model_score": None, "replacement": False}
                started = time.monotonic()
                try:
                    box, landmarks = detect_face(session, captured[0])
                    crop, geometry = shared_context_crop(captured[0], box[:4], landmarks)
                    result.update({"detector_status": "success", "face_box_xyxy": box[:4].tolist(),
                                   "detector_confidence": float(box[4]), "landmarks": landmarks.tolist(),
                                   "geometry": geometry, "crop_RGB_sha256": hashlib.sha256(crop.tobytes()).hexdigest(),
                                   "crop_shape": list(crop.shape), "assets": {}})
                    images = {"shared": crop, "224": cv2.resize(crop, (224, 224), interpolation=cv2.INTER_CUBIC),
                              "518": cv2.resize(crop, (518, 518), interpolation=cv2.INTER_CUBIC)}
                    for name, image in images.items():
                        payload = png_bytes(image)
                        restored = cv2.cvtColor(cv2.imdecode(np.frombuffer(payload, np.uint8), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
                        if not np.array_equal(image, restored):
                            raise RuntimeError("lossless RGB PNG roundtrip mismatch")
                        relative = f"crops/{index:02d}-{name}.png"
                        target = OUTPUT / relative
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with target.open("xb") as destination:
                            destination.write(payload)
                        result["assets"][relative] = {"sha256": _sha256(target), "RGB_sha256": hashlib.sha256(image.tobytes()).hexdigest(), "shape": list(image.shape)}
                    tiles.append((index, images["224"]))
                except ValueError as error:
                    if str(error) not in {"no_face_above_frozen_threshold", "degenerate facial landmarks", "invalid similarity transform", "positive finite face box required", "face context outside image"}:
                        raise
                    result.update({"detector_status": "failed", "final_k1_action": "non_accept", "failure": str(error)})
                    tiles.append((index, np.zeros((224, 224, 3), dtype=np.uint8)))
                inference_seconds += time.monotonic() - started
                write_immutable_record(OUTPUT / "transactions" / f"{index:02d}.json", result)
                results.append(result)
                print("PILOT274", index, result["detector_status"], flush=True)
            if archive_identity(handle) != expected_identity:
                raise ValueError("archive descriptor changed during pilot")
    if verified_archive_identities(Path(plan["paths"]["input_root"]), Path(plan["paths"]["archive_records"]), plan["guard_context"]) != {name: tuple(value) for name, value in plan["archive_identities"].items()}:
        raise ValueError("final archive guard drift")
    check_bindings(plan["sources"])
    if _sha256(OUTPUT / "det_10g.onnx") != MODEL_SHA:
        raise ValueError("final model drift")
    sheet = np.full((8 * 180, 4 * 160, 3), 255, dtype=np.uint8)
    for index, tile in tiles:
        top, left = index // 4 * 180, index % 4 * 160
        cv2.putText(sheet, f"{index:02d}", (left + 3, top + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        sheet[top + 20:top + 180, left:left + 160] = cv2.resize(tile, (160, 160), interpolation=cv2.INTER_CUBIC)
    with (OUTPUT / "contact_sheet.png").open("xb") as destination:
        destination.write(png_bytes(sheet))
    write_immutable_record(OUTPUT / "worker_completion.json", {
        "checkpoint": 274, "transactions": len(results), "detector_success": sum(row["detector_status"] == "success" for row in results),
        "detector_failure": sum(row["detector_status"] == "failed" for row in results),
        "verified_native_frames": native_frames, "selected_payload_bytes": payload_bytes,
        "detector_and_crop_wall_seconds": inference_seconds, "gpu_seconds": 0,
        "provider": session.get_providers(), "archive_guard_before_after_equal": True,
        "original_population": 4950, "selected_population": 4949, "retained_preexisting_failure": 1,
        "calibration_original": 990, "calibration_frame_available": 989, "calibration_score_fit": 0,
        "scientific_readiness": False})


def supervise() -> dict:
    plan = make_plan()
    write_immutable_record(OUTPUT / "attempt_lock.json", {"plan_sha256": _sha256(OUTPUT / "plan.json"),
                           "parent_pid": os.getpid(), "attempts_authorized": 1, "automatic_retry": False})
    process = subprocess.Popen([sys.executable, str(Path(__file__)), "--worker"], start_new_session=True)
    started = time.monotonic()
    peak = {"rss_bytes": 0, "output_bytes": 0, "temporary_bytes": 0}
    failure, code = None, 1
    try:
        while True:
            measured = measured_usage(process.pid)
            peak = {key: max(peak[key], measured[key]) for key in peak}
            if time.time() >= plan["deadline_unix_seconds"] or measured["rss_bytes"] > CAPS["rss_bytes"] or measured["output_bytes"] > CAPS["output_bytes"] - 4 * 1024 ** 2:
                raise TimeoutError("package wall/RSS/storage watchdog cap")
            try:
                code = process.wait(timeout=0.05)
                break
            except subprocess.TimeoutExpired:
                continue
        if code:
            failure = "worker_failed_no_retry"
    except Exception as error:
        failure = type(error).__name__ + ": " + str(error)
        code = 1
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
    approval = read_json(OUTPUT / "owner_approval.json")
    result = {"checkpoint": 274, "completion_claimed": code == 0, "returncode": code,
              "failure": failure, "sampled_peaks": peak, "watchdog_interval_seconds": 0.05,
              "caps": CAPS, "pilot_supervised_wall_seconds": time.monotonic() - started,
              "package_wall_seconds": time.time() - approval["started_unix_seconds"],
              "gpu_seconds": 0, "attempts": 1, "automatic_retry": False,
              "plan_sha256": _sha256(OUTPUT / "plan.json")}
    write_immutable_record(OUTPUT / "resources.json", result)
    if code:
        raise RuntimeError("pilot attempt failed; no automatic retry")
    return result


def acquire() -> dict:
    import onnx
    import onnxruntime as ort

    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise FileExistsError("single package already started; no automatic retry")
    started = time.time()
    write_immutable_record(OUTPUT / "owner_approval.json", {
        "checkpoint": 274, "explicit_owner_approval": True,
        "selected_answer": "Phê duyệt trọn gói SCRFD và một pilot OULU",
        "free_text": None, "skipped": False, "source_url": URL,
        "expected_detector_member": "det_10g.onnx", "caps": CAPS,
        "started_unix_seconds": started, "deadline_unix_seconds": started + CAPS["wall_seconds"],
        "scope": "one acquisition and one source-only train-role pilot; no installations or target work",
        "review273_sha256": _sha256(ROOT / "docs/273-review-doc272-oulu-local-audit-complete.md"),
        "acquisition_runner_sha256": _sha256(Path(__file__)),
    })
    archive_path = OUTPUT / "buffalo_l.zip"
    request = urllib.request.Request(URL, headers={"User-Agent": "FAS-research-preprocessing274"})
    with urllib.request.urlopen(request, timeout=30) as response, archive_path.open("xb") as destination:
        total = 0
        while block := response.read(1024 ** 2):
            total += len(block)
            if total > 400 * 1024 ** 2 or time.time() >= started + CAPS["wall_seconds"]:
                raise ValueError("acquisition resource cap")
            destination.write(block)
        final_url = response.url
    with zipfile.ZipFile(archive_path) as archive:
        members = [member for member in archive.infolist() if member.filename == "det_10g.onnx"]
        if len(members) != 1 or not 1024 ** 2 < members[0].file_size < 64 * 1024 ** 2:
            raise ValueError("exact bounded detector member required")
        payload = archive.read(members[0])
    model_path = OUTPUT / "det_10g.onnx"
    with model_path.open("xb") as destination:
        destination.write(payload)
    model = onnx.load(str(model_path), load_external_data=False)
    onnx.checker.check_model(model)
    if len(model.graph.input) != 1 or len(model.graph.output) != 9:
        raise ValueError("SCRFD three-stride five-keypoint schema required")
    if any(value.data_location == onnx.TensorProto.EXTERNAL for value in model.graph.initializer):
        raise ValueError("external model tensors forbidden")
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    session = ort.InferenceSession(str(model_path), sess_options=options, providers=["CPUExecutionProvider"])
    shapes = [value.shape for value in session.get_outputs()]
    if [shape[-1] for shape in shapes] != [1, 1, 1, 4, 4, 4, 10, 10, 10]:
        raise ValueError("SCRFD score/box/five-landmark output mismatch")
    parameters = sum(__import__("math").prod(value.dims) for value in model.graph.initializer)
    if not 3_000_000 <= parameters <= 6_000_000:
        raise ValueError("SCRFD10G parameter class mismatch")
    record = {"checkpoint": 274, "source_url": URL,
              "redirect_host": urllib.parse.urlparse(final_url).hostname,
              "pack_sha256": _sha256(archive_path), "pack_bytes": total,
              "model_sha256": _sha256(model_path), "model_bytes": len(payload),
              "onnx_parameters": parameters, "output_shapes": shapes,
              "onnx_checker_pass": True, "five_keypoints": True,
              "provider": session.get_providers(), "onnxruntime_version": ort.__version__,
              "inference_executed": False, "wall_seconds": time.time() - started}
    write_immutable_record(OUTPUT / "acquisition.json", record)
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--acquire", action="store_true")
    mode.add_argument("--pilot", action="store_true")
    mode.add_argument("--worker", action="store_true")
    args = parser.parse_args()
    try:
        if args.worker:
            worker()
            return 0
        print(json.dumps(acquire() if args.acquire else supervise(), indent=2))
    except Exception as error:
        failure_path = OUTPUT / ("acquisition_failure.json" if args.acquire else "pilot_failure.json")
        if OUTPUT.exists() and not failure_path.exists() and not (OUTPUT / "archive_identity_blocker.json").exists():
            write_immutable_record(failure_path, {
                "checkpoint": 274, "error_type": type(error).__name__,
                "message": str(error).replace(str(OUTPUT), "PRIVATE_OUTPUT"),
                "inference_executed": False if args.acquire else "inspect_attempt_records", "automatic_retry": False})
            print("PREPROCESSING274 FAILED:", type(error).__name__, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())