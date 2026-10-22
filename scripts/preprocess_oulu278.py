"""One approved remaining-train batch; accepted274/276 evidence stays immutable."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import resource
import signal
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import preprocess_oulu274 as pilot
from fas.freeze import write_immutable_record
from fas.oulu import _sha256
from prepare_oulu_pilot243 import checked_member, check_bindings, stream_frames, usage
from verify_oulu_archive_guard_batch09 import read_verified_json

BASE = pilot.BASE
OUTPUT = BASE / "oulu_preprocessing278_v1"
PILOT = BASE / "oulu_preprocessing276_v1"
ACQUISITION = BASE / "oulu_preprocessing274_v1"
MODEL = ACQUISITION / "det_10g.onnx"
CAPS = {"wall_seconds": 21600, "rss_bytes": 4 * 1024 ** 3,
        "output_bytes": 24 * 1024 ** 3, "gpu_seconds": 0}
RESERVE = 64 * 1024 ** 2
FAILURES = {"no_face_above_frozen_threshold", "degenerate facial landmarks",
            "invalid similarity transform", "positive finite face box required",
            "face context outside image"}
APPROVAL = (
    "Đồng ý: sửa mã + kiểm thử + chạy 2.938 mẫu + readback/kiểm tra ảnh; "
    "CPU-only, tối đa 6 giờ, RSS 4 GiB, tổng dung lượng giữ lại 24 GiB gồm cả "
    "32 mẫu cũ và model; không tự retry/nới cap"
)


def read_json(path: Path) -> dict:
    return pilot.read_json(path)


def ordered(rows: list[dict]) -> list[dict]:
    return sorted(rows, key=lambda row: hashlib.sha256(("oulu274:" + row["video_id"]).encode()).hexdigest())


def partition_train(rows: list[dict], reused: list[dict], *, total: int = 2970,
                    reused_count: int = 32) -> list[dict]:
    if len({row["video_id"] for row in rows}) != len(rows):
        raise ValueError("duplicate frozen transaction ID")
    train = {row["video_id"]: row for row in rows if row["role"] == "train"}
    reuse = {row["video_id"]: row for row in reused}
    if len(train) != total or len(reused) != reused_count or len(reuse) != reused_count:
        raise ValueError("exact train/reused population required")
    if not reuse.keys() <= train.keys() or any(train[key] != row for key, row in reuse.items()):
        raise ValueError("exact reused parent/frame/role/config joins required")
    if any(row["selected_frame"] is None or row["binary_label"] not in {"bona_fide", "attack"} for row in train.values()):
        raise ValueError("train selected frame/label required; no substitution")
    return ordered([row for key, row in train.items() if key not in reuse])


def visual_indices(videos: list[dict]) -> list[int]:
    # Fixed before outcomes: both labels and every frozen session/device stratum.
    strata = {}
    for index, video in enumerate(videos):
        row = video["transaction"]
        parts = row["video_id"].split("_")
        key = (row["binary_label"], tuple(parts[:2]))
        strata.setdefault(key, []).append(index)
    return sorted({indices[0] for indices in strata.values()} |
                  {index for index in range(0, len(videos), 100)})


def accepted_pilot() -> tuple[dict, dict]:
    print("PREFLIGHT278 accepted pilot commitments and32-output readback", flush=True)
    report = read_json(ROOT / "results/phase1/oulu-preprocessing276-recovery-pilot-v1.json")
    records = {name: read_verified_json(PILOT / name, digest)
               for name, digest in report["private_record_sha256"].items()}
    plan, receipt = records["plan.json"], records["resources.json"]
    if receipt["completion_claimed"] is not True or receipt["returncode"] != 0 or receipt["plan_sha256"] != _sha256(PILOT / "plan.json"):
        raise ValueError("accepted pilot completion required")
    previous = pilot.OUTPUT
    try:
        pilot.OUTPUT = PILOT
        if pilot.validate_completion(plan) != receipt["validated_readback"]:
            raise ValueError("accepted pilot exact readback drift")
    finally:
        pilot.OUTPUT = previous
    print("PREFLIGHT278 accepted pilot readback matched", flush=True)
    return plan, receipt


def guard(plan: dict) -> None:
    if "additive_recovery_binding_sha256" in plan:
        import recover_oulu278

        identities = recover_oulu278.verified_identities(plan)
    else:
        identities = pilot.archive_guard(plan)
    if identities != {name: tuple(value) for name, value in plan["archive_identities"].items()}:
        raise ValueError("recovered archive identity drift; no automatic recovery")


def tree_bytes(root: Path) -> int:
    total = 0
    if not root.exists():
        return total
    with os.scandir(root) as entries:
        for entry in entries:
            if entry.is_symlink():
                raise ValueError("no symlinks in retained packages")
            try:
                if entry.is_dir(follow_symlinks=False):
                    total += tree_bytes(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    total += entry.stat(follow_symlinks=False).st_size
            except FileNotFoundError:
                continue
    return total


def measured_usage(group: int) -> dict:
    measured = usage(group, OUTPUT / ".unused")
    measured["output_bytes"] = sum(tree_bytes(root) for root in (OUTPUT, PILOT, ACQUISITION)) + measured["temporary_bytes"]
    measured["rss_bytes"] = max(measured["rss_bytes"], resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
    return measured


def enforce(plan: dict, measured: dict) -> None:
    if time.time() >= plan["deadline_unix_seconds"]:
        raise TimeoutError("six-hour execution/readback deadline")
    if measured["rss_bytes"] > CAPS["rss_bytes"]:
        raise MemoryError("4GiB process-group RSS cap")
    if measured["output_bytes"] > CAPS["output_bytes"] - RESERVE:
        raise OSError("24GiB total retained storage cap including records reserve")


def make_plan() -> dict:
    authority = read_json(OUTPUT / "owner_approval.json")
    if authority["explicit_owner_approval"] is not True or authority["caps"] != CAPS or authority["selected_answer"] != APPROVAL:
        raise ValueError("exact combined277 batch approval required")
    import recover_oulu278

    old_plan, _ = recover_oulu278.accepted_binding()
    binding_path = OUTPUT / "recovery/binding.json"
    recovery = {"additive_recovery_binding_path": str(binding_path),
                "additive_recovery_binding_sha256": _sha256(binding_path)}
    current = recover_oulu278.verified_identities({**old_plan, **recovery})
    old, receipt = accepted_pilot()
    sources = dict(old["sources"])
    for name, digest in read_json(ROOT / "results/phase1/oulu-preprocessing276-recovery-pilot-v1.json")["private_record_sha256"].items():
        sources[str(PILOT / name)] = digest
    audit = read_verified_json(BASE / "oulu_benchmark272_audit_v1.json",
                               "fdf57e7dbb06c637498a8d7501007948815c27cb18fa0a07e32b64244d801e1b")
    rows = []
    roles_path = pilot.FROZEN / "oulu_npu_roles.csv"
    if _sha256(roles_path) != audit["source_sha256"][str(roles_path)]:
        raise ValueError("frozen role parent drift")
    roles = {row["video_id"]: row for row in csv.DictReader(roles_path.read_text().splitlines())}
    print("PREFLIGHT278 joining frozen4950 transactions", flush=True)
    for path in sorted((pilot.TRANSACTIONS / "transactions").glob("*.json")):
        row = read_verified_json(path, audit["source_sha256"][str(path)])
        if any(row[key] != roles[row["video_id"]][key] for key in ("role", "binary_label")):
            raise ValueError("frozen role/transaction drift")
        sources[str(path)] = audit["source_sha256"][str(path)]
        rows.append(row)
    if len(rows) != 4950 or sum(row["selected_frame"] is not None for row in rows) != 4949:
        raise ValueError("unchanged4950/4949 population required")
    remaining = partition_train(rows, [row["transaction"] for row in old["videos"]])
    print("PREFLIGHT278 exact2970 train minus32 reused equals", len(remaining), flush=True)
    videos = []
    for row in remaining:
        path = BASE / "oulu_per_video_audit_v1/videos" / (row["video_id"] + ".json")
        media = read_verified_json(path, row["media_record_sha256"])
        if media["media_sha256"] != row["media_sha256"]:
            raise ValueError("frozen media commitment drift")
        sources[str(path)] = row["media_record_sha256"]
        videos.append({"transaction": row, "media_path": str(path)})
    for path in (Path(__file__), ROOT / "tests/test_preprocessing_batch.py",
                 ROOT / "scripts/recover_oulu278.py",
                 ROOT / "docs/277-review-doc276-recovery-and-preprocessing-pilot.md",
                 ROOT / "results/phase1/oulu-preprocessing276-recovery-pilot-v1.json",
                 OUTPUT / "owner_approval.json", OUTPUT / "batch_authority.json", binding_path):
        sources[str(path)] = _sha256(path)
    plan = {key: old[key] for key in ("paths", "guard_context", "archive_identities",
                                    "recovery_binding_path", "recovery_binding_sha256", "ffmpeg", "model_sha256")}
    batch_authority = read_json(OUTPUT / "batch_authority.json")
    plan.update(checkpoint=278, sources=sources, videos=videos, reused_videos=old["videos"],
                reused_transaction_sha256=receipt["validated_readback"]["transaction_sha256"],
                caps=CAPS, deadline_unix_seconds=batch_authority["deadline_unix_seconds"],
                visual_indices=visual_indices(videos), storage_scope="total278_plus276_plus274_including_pack_model_temporary_manifests_records")
    plan.update(recovery)
    plan["archive_identities"] = {name: list(value) for name, value in current.items()}
    check_bindings(sources)
    guard(plan)
    enforce(plan, measured_usage(os.getpgrp()))
    write_immutable_record(OUTPUT / "plan.json", plan)
    print("PREFLIGHT278 plan committed", flush=True)
    return plan


def write_png(relative: str, image) -> dict:
    import cv2
    import numpy as np
    from fas.visual import png_bytes

    payload = png_bytes(image)
    restored = cv2.imdecode(np.frombuffer(payload, np.uint8), cv2.IMREAD_COLOR)
    if restored is None or not np.array_equal(cv2.cvtColor(restored, cv2.COLOR_BGR2RGB), image):
        raise RuntimeError("lossless PNG RGB roundtrip required")
    path = OUTPUT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(payload)
    return {"sha256": hashlib.sha256(payload).hexdigest(),
            "RGB_sha256": hashlib.sha256(image.tobytes()).hexdigest(), "shape": list(image.shape)}


def produce_unit(session, index: int, video: dict, archive, member, plan: dict) -> dict:
    import cv2
    from fas.preprocessing import detect_face, shared_context_crop

    transaction = video["transaction"]
    media = read_verified_json(Path(video["media_path"]), transaction["media_record_sha256"])
    selected = transaction["selected_frame"]
    checked_member(member, media)
    write_immutable_record(OUTPUT / "attempts" / f"{index:04d}.json",
                           {"index": index, "status": "started", "video_id": transaction["video_id"]})
    captured = []
    with tempfile.TemporaryDirectory(prefix=".payload278-", dir=OUTPUT) as temporary:
        path = Path(temporary) / "selected.avi"
        digest, total = hashlib.sha256(), 0
        with archive.extractfile(member) as source, path.open("xb") as target:
            while block := source.read(1024 ** 2):
                total += len(block)
                if total > media["byte_size"] or total > 128 * 1024 ** 2:
                    raise ValueError("selected payload cap")
                digest.update(block)
                target.write(block)
        if total != media["byte_size"] or digest.hexdigest() != transaction["media_sha256"]:
            raise ValueError("selected payload byte/hash drift")

        def consume(order, rgb):
            if order == selected["decode_order"]:
                if rgb.shape != (selected["height"], selected["width"], 3) or hashlib.sha256(rgb.tobytes()).hexdigest() != selected["rgb_sha256"]:
                    raise ValueError("frozen selected RGB drift")
                captured.append(rgb.copy())

        stream_frames(path, media, consume, timeout=min(180, max(0.001, plan["deadline_unix_seconds"] - time.time())))
        if len(captured) != 1:
            raise ValueError("exact selected frame required; no replacement")
    row = {key: transaction[key] for key in ("video_id", "role", "binary_label", "selected_frame", "media_record_sha256", "media_sha256")}
    row.update(index=index, model_sha256=pilot.MODEL_SHA,
               config_sha256=plan["sources"][str(ROOT / "configs/preprocessing_pilot_v1.yaml")],
               replacement=False, retain_original_denominator=True, model_score=None)
    relative = f"frames/{index:04d}.png"
    row["selected_RGB_asset"] = {"path": relative, **write_png(relative, captured[0])}
    started = time.monotonic()
    try:
        box, landmarks = detect_face(session, captured[0])
        crop, geometry = shared_context_crop(captured[0], box[:4], landmarks)
    except ValueError as error:
        if str(error) not in FAILURES:
            raise
        row.update(detector_status="failed", final_k1_action="non_accept", failure=str(error), assets={})
    else:
        row.update(detector_status="success", face_box_xyxy=box[:4].tolist(),
                   detector_confidence=float(box[4]), landmarks=landmarks.tolist(),
                   geometry=geometry, crop_shape=list(crop.shape),
                   crop_RGB_sha256=hashlib.sha256(crop.tobytes()).hexdigest(), assets={})
        for name in ("shared", "224", "518"):
            image = crop if name == "shared" else cv2.resize(crop, (int(name), int(name)), interpolation=cv2.INTER_CUBIC)
            relative = f"crops/{index:04d}-{name}.png"
            row["assets"][relative] = write_png(relative, image)
    row["detector_and_crop_wall_seconds"] = time.monotonic() - started
    write_immutable_record(OUTPUT / "transactions" / f"{index:04d}.json", row)
    return row


def worker(plan: dict) -> None:
    import cv2
    import onnxruntime as ort
    from inspect_oulu_d261 import archive_identity

    check_bindings(plan["sources"])
    guard(plan)
    if _sha256(MODEL) != pilot.MODEL_SHA:
        raise ValueError("accepted model hash drift")
    if subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0] != plan["ffmpeg"]:
        raise ValueError("accepted decoder drift")
    options = ort.SessionOptions()
    options.intra_op_num_threads = options.inter_op_num_threads = 1
    session = ort.InferenceSession(str(MODEL), sess_options=options, providers=["CPUExecutionProvider"])
    if session.get_providers() != ["CPUExecutionProvider"]:
        raise ValueError("CPU-only provider required")
    cv2.setNumThreads(1)
    indexed = {}
    for index, video in enumerate(plan["videos"]):
        media = read_json(Path(video["media_path"]))
        indexed.setdefault(media["media_archive"], []).append((index, video, media))
    counts = {"success": 0, "failed": 0}
    native, payload, seconds = 0, 0, 0.0
    for name, members in sorted(indexed.items()):
        path = Path(plan["paths"]["input_root"]) / name
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as handle, tarfile.open(fileobj=handle, mode="r:") as archive:
            expected = tuple(plan["archive_identities"][name])
            if archive_identity(handle) != expected:
                raise ValueError("archive descriptor identity drift")
            wanted = {media["media_relpath"] for _, _, media in members}
            if len(wanted) != len(members):
                raise ValueError("duplicate selected archive member")
            headers = {}
            for member in archive:
                if member.name in wanted:
                    if member.name in headers:
                        raise ValueError("duplicate archive header")
                    headers[member.name] = member
            if set(headers) != wanted:
                raise ValueError("missing selected archive members")
            for index, video, media in members:
                if archive_identity(handle) != expected:
                    raise ValueError("archive changed before unit")
                if time.time() >= plan["deadline_unix_seconds"]:
                    raise TimeoutError("batch deadline before unit")
                row = produce_unit(session, index, video, archive, headers[media["media_relpath"]], plan)
                counts[row["detector_status"]] += 1
                native += media["frame_count"]
                payload += media["byte_size"]
                seconds += row["detector_and_crop_wall_seconds"]
                print("BATCH278", index, row["detector_status"], flush=True)
            if archive_identity(handle) != expected:
                raise ValueError("archive changed after units")
    check_bindings(plan["sources"])
    guard(plan)
    write_immutable_record(OUTPUT / "worker_completion.json", {
        "transactions": len(plan["videos"]), "detector_success": counts["success"],
        "detector_failure": counts["failed"], "verified_native_frames": native,
        "selected_payload_bytes": payload, "detector_and_crop_wall_seconds": seconds,
        "provider": session.get_providers(), "gpu_seconds": 0})


def validate_unit(plan: dict, index: int, *, root: Path = OUTPUT) -> tuple[dict, dict]:
    import cv2
    import numpy as np
    from fas.preprocessing import shared_context_crop

    video = plan["videos"][index]
    transaction = video["transaction"]
    path = root / "transactions" / f"{index:04d}.json"
    if path.is_symlink():
        raise ValueError("regular transaction required")
    row = read_json(path)
    if any(row[key] != transaction[key] for key in ("video_id", "role", "binary_label", "selected_frame", "media_record_sha256", "media_sha256")):
        raise ValueError("exact frozen transaction joins required")
    config_sha = plan["sources"][str(ROOT / "configs/preprocessing_pilot_v1.yaml")]
    if row["index"] != index or row["role"] != "train" or row["model_sha256"] != plan["model_sha256"] or row["config_sha256"] != config_sha or row["replacement"] is not False or row["retain_original_denominator"] is not True or row["model_score"] is not None:
        raise ValueError("model/config/denominator/no-replacement join drift")
    media = read_verified_json(Path(video["media_path"]), transaction["media_record_sha256"])
    if media["media_sha256"] != transaction["media_sha256"]:
        raise ValueError("selected media parent drift")
    assets = {}

    def image(relative: str, expected: dict):
        target = root / relative
        if target.is_symlink() or _sha256(target) != expected["sha256"]:
            raise ValueError("PNG asset commitment drift")
        decoded = cv2.imread(str(target), cv2.IMREAD_UNCHANGED)
        if decoded is None or decoded.dtype != np.uint8 or decoded.ndim != 3 or decoded.shape[2] != 3:
            raise ValueError("uint8 RGB asset required")
        rgb = cv2.cvtColor(decoded, cv2.COLOR_BGR2RGB)
        if "shape" in expected and (list(rgb.shape) != expected["shape"] or hashlib.sha256(rgb.tobytes()).hexdigest() != expected["RGB_sha256"]):
            raise ValueError("PNG RGB/shape drift")
        assets[relative] = expected["sha256"]
        return rgb

    relative = f"frames/{index:04d}.png"
    if row["selected_RGB_asset"]["path"] != relative:
        raise ValueError("selected frame path drift")
    rgb = image(relative, row["selected_RGB_asset"])
    frame = transaction["selected_frame"]
    if rgb.shape != (frame["height"], frame["width"], 3) or hashlib.sha256(rgb.tobytes()).hexdigest() != frame["rgb_sha256"]:
        raise ValueError("frozen selected pixels drift")
    if row["detector_status"] == "failed":
        if row.get("final_k1_action") != "non_accept" or row.get("assets") or row.get("failure") not in FAILURES:
            raise ValueError("terminal failed detection must remain non_accept")
    elif row["detector_status"] == "success":
        if not np.isfinite(row["detector_confidence"]) or not 0.5 <= row["detector_confidence"] <= 1:
            raise ValueError("detector confidence outside frozen threshold")
        crop, geometry = shared_context_crop(rgb, np.asarray(row["face_box_xyxy"]), np.asarray(row["landmarks"]))
        required = {f"crops/{index:04d}-{name}.png" for name in ("shared", "224", "518")}
        if set(row["assets"]) != required or row["geometry"] != geometry:
            raise ValueError("shared crop asset/geometry drift")
        if row["crop_shape"] != list(crop.shape) or row["crop_RGB_sha256"] != hashlib.sha256(crop.tobytes()).hexdigest():
            raise ValueError("shared crop pixel commitment drift")
        for name in ("shared", "224", "518"):
            relative = f"crops/{index:04d}-{name}.png"
            expected = crop if name == "shared" else cv2.resize(crop, (int(name), int(name)), interpolation=cv2.INTER_CUBIC)
            if not np.array_equal(image(relative, row["assets"][relative]), expected):
                raise ValueError("shared-context/bicubic branch pixel join drift")
    else:
        raise ValueError("explicit success/failed detector outcome required")
    return row, assets


def validate_ledger(plan: dict, ledger: list[dict]) -> None:
    expected = {video["transaction"]["video_id"] for video in plan["videos"] + plan["reused_videos"]}
    ids = [row["video_id"] for row in ledger]
    if len(expected) != len(plan["videos"]) + len(plan["reused_videos"]) or len(ids) != len(expected) or len(set(ids)) != len(ids) or set(ids) != expected:
        raise ValueError("exact combined unique train ledger required")
    for row in ledger:
        if row["detector_status"] not in {"success", "failed"} or row["role"] != "train":
            raise ValueError("explicit train detector outcome required")
        if row["detector_status"] == "failed" and row["final_k1_action"] != "non_accept":
            raise ValueError("failed ledger row must be non_accept")


def make_sheets(plan: dict, ledger: list[dict]) -> list[dict]:
    import cv2
    import numpy as np

    selected = set(plan["visual_indices"])
    failures = {row["index"] for row in ledger if not row["reused"] and row["detector_status"] == "failed"}
    records = []
    for kind, indices in (("fixed", sorted(selected)), ("failures", sorted(failures))):
        for page, offset in enumerate(range(0, len(indices), 32)):
            subset = indices[offset:offset + 32]
            sheet = np.full((((len(subset) + 3) // 4) * 180, 640, 3), 255, np.uint8)
            for slot, index in enumerate(subset):
                relative = f"frames/{index:04d}.png" if index in failures else f"crops/{index:04d}-224.png"
                bgr = cv2.imread(str(OUTPUT / relative), cv2.IMREAD_COLOR)
                if bgr is None:
                    raise ValueError("visual coverage source missing")
                rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                top, left = slot // 4 * 180, slot % 4 * 160
                cv2.putText(sheet, f"{index:04d}", (left + 3, top + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
                sheet[top + 20:top + 180, left:left + 160] = cv2.resize(rgb, (160, 160), interpolation=cv2.INTER_CUBIC)
            relative = f"visual/{kind}-{page:02d}.png"
            commitment = write_png(relative, sheet)
            restored = cv2.imread(str(OUTPUT / relative), cv2.IMREAD_COLOR)
            if restored is None or not np.array_equal(cv2.cvtColor(restored, cv2.COLOR_BGR2RGB), sheet):
                raise ValueError("saved visual sheet reconstruction mismatch")
            records.append({"path": relative, "indices": subset, "kind": kind, **commitment})
    return records


def verify(plan: dict) -> dict:
    check_bindings(plan["sources"])
    guard(plan)
    old, _ = accepted_pilot()
    if old["videos"] != plan["reused_videos"] or _sha256(MODEL) != plan["model_sha256"]:
        raise ValueError("reused pilot/model drift")
    expected_files = {f"{index:04d}.json" for index in range(len(plan["videos"]))}
    if {path.name for path in (OUTPUT / "transactions").iterdir()} != expected_files:
        raise ValueError("exact new transaction file set required")
    ledger, assets = [], {}
    counts = {"success": 0, "failed": 0}
    native, payload = 0, 0
    for index, video in enumerate(plan["videos"]):
        row, unit_assets = validate_unit(plan, index, root=OUTPUT)
        assets.update(unit_assets)
        counts[row["detector_status"]] += 1
        media = read_json(Path(video["media_path"]))
        native += media["frame_count"]
        payload += media["byte_size"]
        path = OUTPUT / "transactions" / f"{index:04d}.json"
        ledger.append(ledger_row(row, path, False))
        if index % 100 == 0:
            print("READBACK278", index, flush=True)
    observed = {path.relative_to(OUTPUT).as_posix() for folder in ("frames", "crops") for path in (OUTPUT / folder).glob("*")}
    if observed != set(assets):
        raise ValueError("orphan/missing frame or crop asset")
    completion = read_json(OUTPUT / "worker_completion.json")
    required = {"transactions": len(plan["videos"]), "detector_success": counts["success"],
                "detector_failure": counts["failed"], "verified_native_frames": native,
                "selected_payload_bytes": payload, "provider": ["CPUExecutionProvider"], "gpu_seconds": 0}
    if any(type(completion.get(key)) is not type(value) or completion[key] != value for key, value in required.items()):
        raise ValueError("worker completion counts mismatch")
    for index, video in enumerate(plan["reused_videos"]):
        path = PILOT / "transactions" / f"{index:02d}.json"
        row = read_verified_json(path, plan["reused_transaction_sha256"][str(index)])
        if row["video_id"] != video["transaction"]["video_id"]:
            raise ValueError("reused row ID mismatch")
        ledger.append(ledger_row(row, path, True))
    validate_ledger(plan, ledger)
    sheets = make_sheets(plan, ledger)
    check_bindings(plan["sources"])
    guard(plan)
    ledger_path = OUTPUT / "combined_ledger.json"
    write_immutable_record(ledger_path, {"rows": ledger, "transactions": len(ledger), "scientific_readiness": False})
    if read_json(ledger_path)["rows"] != ledger:
        raise RuntimeError("combined ledger readback mismatch")
    result = {**required, "reused_transactions": len(plan["reused_videos"]),
              "combined_transactions": len(ledger), "asset_sha256": assets,
              "combined_ledger_sha256": _sha256(ledger_path), "visual_sheets": sheets,
              "sheet_inspected": False, "scientific_readiness": False,
              "combined_detector_success": sum(row["detector_status"] == "success" for row in ledger),
              "combined_detector_failure": sum(row["detector_status"] == "failed" for row in ledger)}
    write_immutable_record(OUTPUT / "readback.json", result)
    return result


def ledger_row(row: dict, path: Path, reused: bool) -> dict:
    return {**{key: row[key] for key in ("index", "video_id", "role", "binary_label", "detector_status")},
            "final_k1_action": row.get("final_k1_action"), "reused": reused,
            "record_path": str(path), "record_sha256": _sha256(path),
            "replacement": False, "retain_original_denominator": True}


def failure_rows(plan: dict, failure: str) -> None:
    rows = []
    for index, video in enumerate(plan["videos"]):
        row = video["transaction"]
        path = OUTPUT / "transactions" / f"{index:04d}.json"
        rows.append({"index": index, "video_id": row["video_id"], "role": row["role"],
                     "detector_status": "unverified_after_attempt_failure", "final_k1_action": "non_accept",
                     "worker_record_sha256": _sha256(path) if path.is_file() and not path.is_symlink() else None,
                     "retain_original_denominator": True, "replacement": False, "failure": failure})
    write_immutable_record(OUTPUT / "failure_rows.json", {"rows": rows, "automatic_retry": False})


def supervise(plan: dict) -> dict:
    write_immutable_record(OUTPUT / "attempt_lock.json", {
        "plan_sha256": _sha256(OUTPUT / "plan.json"), "parent_pid": os.getpid(),
        "attempts_authorized": 1, "automatic_retry": False})
    peak = {"rss_bytes": 0, "output_bytes": 0, "temporary_bytes": 0}
    process, failure, readback = None, None, None
    started = time.monotonic()
    try:
        for mode in ("--worker", "--verify"):
            process = subprocess.Popen([sys.executable, str(Path(__file__)), mode], start_new_session=True)
            while True:
                measured = measured_usage(process.pid)
                peak = {key: max(peak[key], measured[key]) for key in peak}
                enforce(plan, measured)
                try:
                    if process.wait(timeout=2):
                        raise RuntimeError(mode + " failed; no retry")
                    break
                except subprocess.TimeoutExpired:
                    continue
            process = None
        readback = read_json(OUTPUT / "readback.json")
        ledger = read_verified_json(OUTPUT / "combined_ledger.json", readback["combined_ledger_sha256"])
        validate_ledger(plan, ledger["rows"])
        for row in ledger["rows"]:
            if _sha256(Path(row["record_path"])) != row["record_sha256"]:
                raise ValueError("final combined ledger record drift")
        check_bindings(plan["sources"])
        guard(plan)
        final = measured_usage(os.getpgrp())
        final["rss_bytes"] = max(final["rss_bytes"], resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024)
        peak = {key: max(peak[key], final[key]) for key in peak}
        enforce(plan, peak)
    except Exception as error:
        failure = type(error).__name__ + ": " + str(error)
        print("BATCH278 FAILED", failure, file=sys.stderr, flush=True)
    finally:
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
    if failure:
        failure_rows(plan, failure)
    result = {"checkpoint": 278, "completion_claimed": failure is None and readback is not None,
              "failure": failure, "sampled_peaks": peak, "caps": CAPS,
              "wall_seconds": time.monotonic() - started,
              "package_wall_seconds": time.time() - read_json(OUTPUT / "batch_authority.json")["started_unix_seconds"],
              "planned_transactions": len(plan["videos"]), "reused_transactions": len(plan["reused_videos"]),
              "readback_sha256": _sha256(OUTPUT / "readback.json") if readback else None,
              "visual_inspection_pending": failure is None, "gpu_seconds": 0,
              "automatic_retry": False, "attempts": 1, "scientific_readiness": False}
    write_immutable_record(OUTPUT / "resources.json", result)
    if read_json(OUTPUT / "resources.json") != result:
        raise RuntimeError("resource receipt readback mismatch")
    print("BATCH278_TERMINAL", json.dumps(result), flush=True)
    return result


def publish_summary(result: dict) -> None:
    import recover_oulu278

    complete = result["completion_claimed"] is True
    readback = read_json(OUTPUT / "readback.json") if complete else None
    recovery_path = OUTPUT / "recovery/binding.json"
    recovery = read_json(recovery_path) if recovery_path.exists() else None
    summary = {
        "checkpoint": 278,
        "status": "software_complete_visual_review_pending" if complete else "stopped_failure_no_retry",
        "completion_claimed": complete, "visual_inspection_completed": False,
        "failure_category": result["failure"].split(":", 1)[0] if result.get("failure") else None,
        "caps": CAPS, "storage_scope": "total278_plus276_plus274_including_pack_model_temporary_manifests_records",
        "recovery_caps": recover_oulu278.RECOVERY_CAPS,
        "recovery_bytes_read": recovery["bytes_read"] if recovery else None,
        "recovery_wall_seconds": recovery["wall_seconds"] if recovery else None,
        "recovery_rss_peak_bytes": recovery["rss_peak_bytes"] if recovery else None,
        "recovery_whole_file_equality": recovery["whole_file_equality"] if recovery else False,
        "new_planned": 2938, "reused": 32, "train_originals": 2970,
        "new_detector_success": readback["detector_success"] if readback else None,
        "new_detector_failure": readback["detector_failure"] if readback else None,
        "combined_detector_success": readback["combined_detector_success"] if readback else None,
        "combined_detector_failure": readback["combined_detector_failure"] if readback else None,
        "verified_native_frames": readback["verified_native_frames"] if readback else None,
        "selected_payload_bytes": readback["selected_payload_bytes"] if readback else None,
        "visual_sheets_prepared": len(readback["visual_sheets"]) if readback else 0,
        "sampled_peaks": result.get("sampled_peaks"), "batch_package_wall_seconds": result.get("package_wall_seconds"),
        "automatic_retry": False, "gpu_seconds": 0, "model_downloads": 0,
        "active_preprocessing_config_changed": False, "scientific_readiness": False,
        "oulu_audit_status": "complete", "other_domain_not_audited_fields": 6,
        "originals": 4950, "selected": 4949, "preexisting_terminal_failure": 1,
        "calibration_originals": 990, "calibration_selected": 989, "calibration_fitted_scores": 0,
        "private_record_sha256": {
            path.relative_to(OUTPUT).as_posix(): _sha256(path)
            for path in (OUTPUT / "owner_approval.json", OUTPUT / "supervisor.json",
                         OUTPUT / "recovery/binding.json", OUTPUT / "batch_authority.json",
                         OUTPUT / "plan.json", OUTPUT / "worker_completion.json",
                         OUTPUT / "readback.json", OUTPUT / "combined_ledger.json",
                         OUTPUT / "resources.json", OUTPUT / "package_failure.json")
            if path.exists()}}
    write_immutable_record(ROOT / "results/phase1/oulu-preprocessing278-train-v1.json", summary)


def arm_deadline(deadline: float) -> None:
    remaining = deadline - time.time()
    if remaining <= 0:
        raise TimeoutError("package deadline")
    signal.signal(signal.SIGALRM, lambda signum, frame: (_ for _ in ()).throw(TimeoutError("package deadline")))
    signal.setitimer(signal.ITIMER_REAL, remaining)


def child_plan() -> dict:
    plan = read_json(OUTPUT / "plan.json")
    lease = read_json(OUTPUT / "attempt_lock.json")
    if lease["plan_sha256"] != _sha256(OUTPUT / "plan.json") or lease["parent_pid"] != os.getppid() or os.getsid(0) != os.getpid():
        raise ValueError("single supervised child required")
    arm_deadline(plan["deadline_unix_seconds"])
    return plan


def status() -> dict:
    authority = read_json(OUTPUT / "owner_approval.json")
    batch_clock = OUTPUT / "batch_authority.json"
    completed = list((OUTPUT / "transactions").glob("*.json"))
    terminal = OUTPUT / "resources.json"
    package_failure = OUTPUT / "package_failure.json"
    return {"checkpoint": 278, "new_records_written": len(completed),
            "new_records_expected": 2938, "reused_records": 32,
            "phase": "batch" if batch_clock.exists() else "recovery",
            "deadline_unix_seconds": read_json(batch_clock)["deadline_unix_seconds"] if batch_clock.exists() else authority["recovery_deadline_unix_seconds"],
            "plan_committed": (OUTPUT / "plan.json").exists(),
            "terminal": read_json(terminal) if terminal.exists() else None,
            "package_failure": read_json(package_failure) if package_failure.exists() else None}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run-approved", action="store_true")
    mode.add_argument("--worker", action="store_true")
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--status", action="store_true")
    args = parser.parse_args()
    if args.status:
        print(json.dumps(status(), indent=2))
        return 0
    if args.worker or args.verify:
        plan = child_plan()
        worker(plan) if args.worker else verify(plan)
        return 0
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise FileExistsError("one approved package only; no automatic retry")
    started = time.time()
    import recover_oulu278

    write_immutable_record(OUTPUT / "owner_approval.json", {
        "checkpoint": 278, "explicit_owner_approval": True, "selected_answer": APPROVAL,
        "caps": CAPS, "started_unix_seconds": started,
        "recovery_selected_answer": recover_oulu278.APPROVAL,
        "recovery_caps": recover_oulu278.RECOVERY_CAPS,
        "recovery_deadline_unix_seconds": started + recover_oulu278.RECOVERY_CAPS["wall_seconds"],
        "scope": "code_generalization_tests_one_remaining_train_batch_readback_visual_review",
        "storage_scope": "total278_plus276_plus274_including_pack_model_temporary_manifests_records",
        "review277_sha256": _sha256(ROOT / "docs/277-review-doc276-recovery-and-preprocessing-pilot.md"),
        "automatic_retry": False, "environment_changes": False, "model_download": False})
    with (OUTPUT / "execution.log").open("xb", buffering=0) as log:
        os.dup2(log.fileno(), 1)
        os.dup2(log.fileno(), 2)
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    print("BATCH278_START", os.getpid(), started, flush=True)
    write_immutable_record(OUTPUT / "supervisor.json", {
        "pid": os.getpid(), "started_unix_seconds": started,
        "runner_sha256": _sha256(Path(__file__)), "automatic_retry": False})
    try:
        arm_deadline(started + recover_oulu278.RECOVERY_CAPS["wall_seconds"])
        recover_oulu278.recover()
        batch_started = time.time()
        write_immutable_record(OUTPUT / "batch_authority.json", {
            "started_unix_seconds": batch_started, "deadline_unix_seconds": batch_started + CAPS["wall_seconds"],
            "owner_approval_sha256": _sha256(OUTPUT / "owner_approval.json"),
            "recovery_binding_sha256": _sha256(OUTPUT / "recovery/binding.json"),
            "caps": CAPS, "automatic_retry": False})
        arm_deadline(batch_started + CAPS["wall_seconds"])
        plan = make_plan()
        result = supervise(plan)
        publish_summary(result)
        return 0 if result["completion_claimed"] else 1
    except Exception as error:
        write_immutable_record(OUTPUT / "package_failure.json", {
            "error_type": type(error).__name__, "message": str(error),
            "automatic_retry": False, "scientific_readiness": False})
        if not (ROOT / "results/phase1/oulu-preprocessing278-train-v1.json").exists():
            publish_summary({"completion_claimed": False, "failure": type(error).__name__ + ": " + str(error)})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
