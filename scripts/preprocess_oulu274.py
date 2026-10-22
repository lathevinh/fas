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


def model_path() -> Path:
    return BASE / "oulu_preprocessing274_v1/det_10g.onnx" if OUTPUT.name == "oulu_preprocessing276_v1" else OUTPUT / "det_10g.onnx"


def pilot_approval() -> dict:
    return read_json(OUTPUT / ("pilot_authority.json" if OUTPUT.name == "oulu_preprocessing276_v1" else "owner_approval.json"))


def archive_guard(plan: dict) -> dict:
    from verify_oulu_archive_guard_batch09 import verified_archive_identities

    if "recovery_binding_sha256" in plan:
        import stat
        import recover_oulu276 as recovery
        from verify_oulu_archive_guard_batch09 import read_verified_json, verified_guard_authority, IDENTITY_FIELDS

        recovery.approval()
        guard = plan["guard_context"]
        report = verified_guard_authority(guard)
        binding_path = Path(plan["recovery_binding_path"])
        binding = read_verified_json(binding_path, plan["recovery_binding_sha256"])
        old_path = Path(guard["accepted219_binding_path"])
        old = read_verified_json(old_path, report["private_binding_sha256"])
        if binding["approval_sha256"] != _sha256(recovery.PACKAGE / "owner_approval.json") or binding["recovery_code_sha256"] != _sha256(Path(recovery.__file__)) or binding["accepted219_binding_sha256"] != report["private_binding_sha256"] or binding["caps"] != recovery.RECOVERY_CAPS or binding["whole_file_equality"] is not True or binding["bytes_read"] != sum(recovery.ARCHIVE_SIZES.values()):
            raise ValueError("verified full-byte recovery binding required")
        if set(binding["archives"]) != set(recovery.ANCHORS):
            raise ValueError("exact three recovered archives required")
        identities = {}
        for name, row in binding["archives"].items():
            if row != read_verified_json(binding_path.parent / (name + ".rehash.json"), binding["record_sha256"][name]):
                raise ValueError("recovery row binding drift")
            current_stat = (Path(plan["paths"]["input_root"]) / name).lstat()
            current = recovery.file_identity(current_stat)
            accepted = old["archives"][name]["current_file_identity"]
            if not stat.S_ISREG(current_stat.st_mode) or row["current_identity"] != current or row["accepted219_identity"] != accepted or row["sha256"] != recovery.ANCHORS[name] or row["bytes_read"] != recovery.ARCHIVE_SIZES[name] or row["stable_descriptor_and_path"] is not True or any(current[key] != accepted[key] for key in IDENTITY_FIELDS if key != "device"):
                raise ValueError("full-byte recovered identity drift")
            identities[name] = tuple(current[key] for key in IDENTITY_FIELDS)
        return identities
    return verified_archive_identities(Path(plan["paths"]["input_root"]), Path(plan["paths"]["archive_records"]), plan["guard_context"])


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
    approval = pilot_approval()
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
    recovery = {}
    if OUTPUT.name == "oulu_preprocessing276_v1":
        recovery_path = OUTPUT / "recovery/binding.json"
        recovery = {"recovery_binding_path": str(recovery_path), "recovery_binding_sha256": _sha256(recovery_path)}
    identities = archive_guard({"paths": parent["paths"], "guard_context": guard, **recovery})
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
    if _sha256(model_path()) != MODEL_SHA:
        raise ValueError("approved model weight drift")
    for name in ("owner_approval.json", "acquisition.json"):
        path = BASE / "oulu_preprocessing274_v1" / name if name == "acquisition.json" and recovery else OUTPUT / name
        sources[str(path)] = _sha256(path)
    if recovery:
        for path in (OUTPUT / "pilot_authority.json", ROOT / "scripts/recover_oulu276.py", ROOT / "docs/275-review-doc274-scrfd-and-pilot-recovery.md"):
            sources[str(path)] = _sha256(path)
    plan = {"checkpoint": 276 if recovery else 274, "videos": videos, "sources": sources, **recovery,
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
    if OUTPUT.name == "oulu_preprocessing276_v1":
        total += sum(path.stat().st_size for path in (BASE / "oulu_preprocessing274_v1").rglob("*") if path.is_file())
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
    if _sha256(model_path()) != MODEL_SHA:
        raise ValueError("model drift before inference")
    if subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0] != plan["ffmpeg"]:
        raise ValueError("accepted decoder version drift")
    options = ort.SessionOptions()
    options.intra_op_num_threads = options.inter_op_num_threads = 1
    session = ort.InferenceSession(str(model_path()), sess_options=options, providers=["CPUExecutionProvider"])
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
                          "media_sha256": transaction["media_sha256"], "model_sha256": MODEL_SHA,
                          "config_sha256": plan["sources"][str(ROOT / "configs/preprocessing_pilot_v1.yaml")],
                          "retain_original_denominator": True, "model_score": None, "replacement": False}
                frame_path = OUTPUT / "frames" / f"{index:02d}.png"
                frame_path.parent.mkdir(exist_ok=True)
                with frame_path.open("xb") as destination:
                    destination.write(png_bytes(captured[0]))
                result["selected_RGB_asset"] = {"path": f"frames/{index:02d}.png", "sha256": _sha256(frame_path)}
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
    if archive_guard(plan) != {name: tuple(value) for name, value in plan["archive_identities"].items()}:
        raise ValueError("final archive guard drift")
    check_bindings(plan["sources"])
    if _sha256(model_path()) != MODEL_SHA:
        raise ValueError("final model drift")
    sheet = np.full((8 * 180, 4 * 160, 3), 255, dtype=np.uint8)
    for index, tile in tiles:
        top, left = index // 4 * 180, index % 4 * 160
        cv2.putText(sheet, f"{index:02d}", (left + 3, top + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        sheet[top + 20:top + 180, left:left + 160] = cv2.resize(tile, (160, 160), interpolation=cv2.INTER_CUBIC)
    with (OUTPUT / "contact_sheet.png").open("xb") as destination:
        destination.write(png_bytes(sheet))
    write_immutable_record(OUTPUT / "worker_completion.json", {
        "checkpoint": plan["checkpoint"], "transactions": len(results), "detector_success": sum(row["detector_status"] == "success" for row in results),
        "detector_failure": sum(row["detector_status"] == "failed" for row in results),
        "verified_native_frames": native_frames, "selected_payload_bytes": payload_bytes,
        "detector_and_crop_wall_seconds": inference_seconds, "gpu_seconds": 0,
        "provider": session.get_providers(), "archive_guard_before_after_equal": True,
        "original_population": 4950, "selected_population": 4949, "retained_preexisting_failure": 1,
        "calibration_original": 990, "calibration_frame_available": 989, "calibration_score_fit": 0,
        "scientific_readiness": False})


def validate_completion(plan: dict) -> dict:
    import cv2
    import numpy as np
    from fas.preprocessing import shared_context_crop
    from prepare_oulu_pilot243 import check_bindings

    completion = read_json(OUTPUT / "worker_completion.json")
    videos = plan["videos"]
    if len(videos) != 32 or len({row["transaction"]["video_id"] for row in videos}) != 32:
        raise ValueError("exact32 unique planned transactions required")
    if any(sum(row["transaction"]["binary_label"] == label for row in videos) != 16 for label in ("bona_fide", "attack")):
        raise ValueError("fixed16/16 class accounting required")
    expected_files = {f"{index:02d}.json" for index in range(32)}
    if {path.name for path in (OUTPUT / "transactions").iterdir()} != expected_files:
        raise ValueError("exact32 transaction records required")
    check_bindings(plan["sources"])
    if _sha256(model_path()) != MODEL_SHA or plan["model_sha256"] != MODEL_SHA:
        raise ValueError("final model hash drift")
    config_sha = _sha256(ROOT / "configs/preprocessing_pilot_v1.yaml")
    if plan["sources"][str(ROOT / "configs/preprocessing_pilot_v1.yaml")] != config_sha:
        raise ValueError("final config hash drift")
    counts = {"success": 0, "failed": 0}
    native_frames, payload_bytes, assets, records, tiles = 0, 0, {}, {}, []
    for index, video in enumerate(videos):
        transaction = video["transaction"]
        path = OUTPUT / "transactions" / f"{index:02d}.json"
        if path.is_symlink():
            raise ValueError("regular transaction required")
        row = read_json(path)
        records[str(index)] = _sha256(path)
        for key in ("video_id", "binary_label", "role", "selected_frame", "media_record_sha256", "media_sha256"):
            if row[key] != transaction[key]:
                raise ValueError("transaction/frame/media parent join drift")
        if row["index"] != index or row["role"] != "train" or row["model_sha256"] != MODEL_SHA or row["config_sha256"] != config_sha or row["replacement"] is not False or row["retain_original_denominator"] is not True or row["model_score"] is not None:
            raise ValueError("model/config/denominator/no-replacement drift")
        media_path = Path(video["media_path"])
        if _sha256(media_path) != transaction["media_record_sha256"]:
            raise ValueError("selected media parent drift")
        media = read_json(media_path)
        if media["media_sha256"] != transaction["media_sha256"]:
            raise ValueError("selected payload commitment drift")
        frame = transaction["selected_frame"]
        frame_asset = row["selected_RGB_asset"]
        frame_relative = f"frames/{index:02d}.png"
        frame_path = OUTPUT / frame_relative
        if frame_asset["path"] != frame_relative or frame_path.is_symlink() or _sha256(frame_path) != frame_asset["sha256"]:
            raise ValueError("selected RGB PNG commitment drift")
        selected_rgb = cv2.imread(str(frame_path), cv2.IMREAD_COLOR)
        if selected_rgb is None or selected_rgb.shape != (frame["height"], frame["width"], 3):
            raise ValueError("selected RGB shape drift")
        selected_rgb = cv2.cvtColor(selected_rgb, cv2.COLOR_BGR2RGB)
        if hashlib.sha256(selected_rgb.tobytes()).hexdigest() != frame["rgb_sha256"]:
            raise ValueError("frozen selected RGB hash drift")
        assets[frame_relative] = frame_asset["sha256"]
        native_frames += media["frame_count"]
        payload_bytes += media["byte_size"]
        status = row["detector_status"]
        if status not in counts:
            raise ValueError("explicit detector outcome required")
        counts[status] += 1
        if status == "failed":
            if row.get("final_k1_action") != "non_accept" or row.get("assets") or row.get("failure") not in {"no_face_above_frozen_threshold", "degenerate facial landmarks", "invalid similarity transform", "positive finite face box required", "face context outside image"}:
                raise ValueError("failed row must retain non-accept without replacement")
            tiles.append((index, np.zeros((224, 224, 3), dtype=np.uint8)))
            continue
        if not np.isfinite(row["detector_confidence"]) or not 0.5 <= row["detector_confidence"] <= 1:
            raise ValueError("invalid detector confidence")
        expected_crop, geometry = shared_context_crop(selected_rgb, np.asarray(row["face_box_xyxy"]), np.asarray(row["landmarks"]))
        if row["geometry"] != geometry:
            raise ValueError("fixed shared context geometry drift")
        expected_assets = {f"crops/{index:02d}-{name}.png" for name in ("shared", "224", "518")}
        if set(row["assets"]) != expected_assets:
            raise ValueError("exact three success assets required")
        images = {}
        for name in ("shared", "224", "518"):
            relative = f"crops/{index:02d}-{name}.png"
            target, expected = OUTPUT / relative, row["assets"][relative]
            if target.is_symlink() or _sha256(target) != expected["sha256"]:
                raise ValueError("crop PNG hash drift")
            image = cv2.imdecode(np.frombuffer(target.read_bytes(), np.uint8), cv2.IMREAD_UNCHANGED)
            if image is None or image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3:
                raise ValueError("uint8 RGB PNG required")
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            if list(image.shape) != expected["shape"] or hashlib.sha256(image.tobytes()).hexdigest() != expected["RGB_sha256"]:
                raise ValueError("crop RGB/shape hash drift")
            images[name] = image
            assets[relative] = expected["sha256"]
        left, top, right, bottom = geometry["crop_xyxy_half_open"]
        if images["shared"].shape != (bottom - top, right - left, 3) or list(images["shared"].shape) != row["crop_shape"] or hashlib.sha256(images["shared"].tobytes()).hexdigest() != row["crop_RGB_sha256"]:
            raise ValueError("shared crop geometry/hash drift")
        if not np.array_equal(images["shared"], expected_crop):
            raise ValueError("shared crop is not from frozen selected RGB")
        for size in (224, 518):
            if images[str(size)].shape != (size, size, 3) or not np.array_equal(images[str(size)], cv2.resize(images["shared"], (size, size), interpolation=cv2.INTER_CUBIC)):
                raise ValueError("branch resize/RGB drift")
        tiles.append((index, images["224"]))
    observed_assets = {path.relative_to(OUTPUT).as_posix() for folder in ("crops", "frames") for path in (OUTPUT / folder).glob("*")}
    if observed_assets != set(assets):
        raise ValueError("unexpected or orphan crop assets")
    expected_sheet = np.full((8 * 180, 4 * 160, 3), 255, dtype=np.uint8)
    for index, tile in tiles:
        top, left = index // 4 * 180, index % 4 * 160
        cv2.putText(expected_sheet, f"{index:02d}", (left + 3, top + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        expected_sheet[top + 20:top + 180, left:left + 160] = cv2.resize(tile, (160, 160), interpolation=cv2.INTER_CUBIC)
    sheet_path = OUTPUT / "contact_sheet.png"
    sheet = cv2.imread(str(sheet_path), cv2.IMREAD_COLOR)
    if sheet_path.is_symlink() or sheet is None or not np.array_equal(cv2.cvtColor(sheet, cv2.COLOR_BGR2RGB), expected_sheet):
        raise ValueError("source-only contact sheet join drift")
    required = {"transactions": 32, "detector_success": counts["success"], "detector_failure": counts["failed"],
                "verified_native_frames": native_frames, "selected_payload_bytes": payload_bytes,
                "gpu_seconds": 0, "provider": ["CPUExecutionProvider"], "archive_guard_before_after_equal": True,
                "original_population": 4950, "selected_population": 4949, "retained_preexisting_failure": 1,
                "calibration_original": 990, "calibration_frame_available": 989, "calibration_score_fit": 0,
                "scientific_readiness": False}
    if any(type(completion.get(key)) is not type(value) or completion[key] != value for key, value in required.items()):
        raise ValueError("worker completion/accounting mismatch")
    check_bindings(plan["sources"])
    return {**required, "transaction_sha256": records, "asset_sha256": assets,
            "contact_sheet_sha256": _sha256(sheet_path), "sheet_inspected": False}


def materialize_partial_rows(plan: dict, failure: str) -> None:
    for index, video in enumerate(plan["videos"]):
        transaction = video["transaction"]
        path = OUTPUT / "transactions" / f"{index:02d}.json"
        write_immutable_record(OUTPUT / "failure_rows" / f"{index:02d}.json", {
            "index": index, "video_id": transaction["video_id"], "role": transaction["role"],
            "binary_label": transaction["binary_label"], "selected_frame": transaction["selected_frame"],
            "detector_status": "unverified_after_attempt_failure", "final_k1_action": "non_accept",
            "failure": failure, "worker_record_sha256": _sha256(path) if path.is_file() and not path.is_symlink() else None,
            "retain_original_denominator": True, "replacement": False})


def supervise() -> dict:
    plan = make_plan()
    write_immutable_record(OUTPUT / "attempt_lock.json", {"plan_sha256": _sha256(OUTPUT / "plan.json"),
                           "parent_pid": os.getpid(), "attempts_authorized": 1, "automatic_retry": False})
    process = None
    started = time.monotonic()
    peak = {"rss_bytes": 0, "output_bytes": 0, "temporary_bytes": 0}
    readback = None
    failure, code = None, 1
    try:
        process = subprocess.Popen([sys.executable, str(Path(__file__)), "--worker", "--package", "276" if OUTPUT.name == "oulu_preprocessing276_v1" else "274"], start_new_session=True)
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
        else:
            readback = validate_completion(plan)
    except Exception as error:
        failure = type(error).__name__ + ": " + str(error)
        code = 1
    finally:
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
    approval = pilot_approval()
    final = measured_usage(os.getpgrp())
    import resource
    final["rss_bytes"] = max(final["rss_bytes"], resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                             resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024)
    peak = {key: max(peak[key], final[key]) for key in peak}
    if time.time() >= plan["deadline_unix_seconds"] or peak["rss_bytes"] > CAPS["rss_bytes"] or final["output_bytes"] > CAPS["output_bytes"] - 4 * 1024 ** 2:
        failure, code = "final deadline/RSS/storage cap", 1
    if code:
        materialize_partial_rows(plan, failure)
    result = {"checkpoint": plan.get("checkpoint", 274), "completion_claimed": code == 0 and readback is not None, "returncode": code,
              "failure": failure, "sampled_peaks": peak, "watchdog_interval_seconds": 0.05,
              "validated_readback": readback, "planned_transactions": len(plan["videos"]),
              "failed_attempt_rows": len(plan["videos"]) if code else 0,
              "caps": CAPS, "pilot_supervised_wall_seconds": time.monotonic() - started,
              "package_wall_seconds": time.time() - approval["started_unix_seconds"],
              "gpu_seconds": 0, "attempts": 1, "automatic_retry": False,
              "plan_sha256": _sha256(OUTPUT / "plan.json")}
    write_immutable_record(OUTPUT / "resources.json", result)
    if read_json(OUTPUT / "resources.json") != result:
        raise RuntimeError("resources readback failed")
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
    global OUTPUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", choices=("274", "276"), default="274")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--acquire", action="store_true")
    mode.add_argument("--pilot", action="store_true")
    mode.add_argument("--worker", action="store_true")
    args = parser.parse_args()
    OUTPUT = BASE / f"oulu_preprocessing{args.package}_v1"
    if args.acquire and args.package != "274":
        raise ValueError("276 reuses acquired model; no download authorized")
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