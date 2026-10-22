"""Approved fixed calibration/g_domain images and full OULU preprocessing manifest."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tarfile
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import preprocess_oulu278 as previous
from fas.freeze import write_immutable_record
from fas.oulu import _sha256
from fas.preprocessing_policy import MODEL_SHA256, validate_active_preprocessing, validate_legacy_equivalence
from prepare_oulu_pilot243 import check_bindings, checked_member, stream_frames, usage
from verify_oulu_archive_guard_batch09 import read_verified_json

BASE = previous.BASE
OUTPUT = BASE / "oulu_preprocessing280_v1"
ACTIVE = ROOT / "configs/preprocessing_v3.yaml"
LEGACY = ROOT / "configs/preprocessing_pilot_v1.yaml"
CAPS = {"wall_seconds": 14400, "rss_bytes": 4 * 1024 ** 3,
        "output_bytes": 24 * 1024 ** 3, "gpu_seconds": 0}
RESERVE = 64 * 1024 ** 2
NEW_ROLES = {"branch_calibration", "g_domain"}
ROLE_COUNTS = {"train": 2970, "branch_calibration": 990, "g_domain": 990}
APPROVAL = (
    "Đồng ý toàn gói: code/tests + 1.979 frames calibration/g_domain + full "
    "manifest/readback/visual + pin active v3; CPU-only, tối đa 4 giờ/4 GiB RSS/"
    "24 GiB tổng giữ lại gồm 274/276/278/280; không retry, không rehash archive "
    "nếu binding vẫn khớp"
)
MEASURED_PROPOSAL = {
    "branch_calibration_original": 990, "branch_calibration_selected": 989,
    "g_domain_original": 990, "g_domain_selected": 990,
    "retained_preexisting_failure": 1, "selected_payload_bytes": 42388241168,
    "verified_native_frames": 264824, "retained_before_batch_bytes": 9351144291,
    "estimated_new_output_bytes": 6017281770, "estimated_batch_seconds": 5566.7808129518835,
}


def read_json(path: Path) -> dict:
    return previous.read_json(path)


def check_policy() -> None:
    validate_active_preprocessing(read_json(ACTIVE))
    validate_legacy_equivalence(read_json(ACTIVE), read_json(LEGACY))
    if read_json(ROOT / "configs/experiment_core_v1.yaml")["preprocessing_spec"] != ACTIVE.name:
        raise ValueError("canonical active preprocessing reference required")


def partition(rows: list[dict], legacy_ids: list[str]) -> tuple[list[dict], list[dict]]:
    identities = [row["video_id"] for row in rows]
    if len(identities) != 4950 or len(set(identities)) != 4950:
        raise ValueError("exact4950 unique original transactions required")
    if Counter(row["role"] for row in rows) != ROLE_COUNTS:
        raise ValueError("frozen2970/990/990 source-role denominators required")
    train = {row["video_id"] for row in rows if row["role"] == "train"}
    if len(legacy_ids) != 2970 or len(set(legacy_ids)) != 2970 or set(legacy_ids) != train:
        raise ValueError("exact accepted2970 train reuse required")
    terminal = [row for row in rows if row["selected_frame"] is None]
    if len(terminal) != 1 or terminal[0]["role"] != "branch_calibration":
        raise ValueError("one unchanged calibration pre-detector failure required")
    if any(row["binary_label"] not in {"attack", "bona_fide"} for row in rows):
        raise ValueError("frozen binary label required")
    failure = terminal[0]
    if failure["final_k1_action"] != "non_accept" or failure["model_score"] is not None or failure["classifier_error"] is not None or failure["detector_status"] != "not_run":
        raise ValueError("preexisting failure cannot acquire detector or score evidence")
    new = [row for row in rows if row["role"] in NEW_ROLES and row["selected_frame"] is not None]
    if Counter(row["role"] for row in new) != {"branch_calibration": 989, "g_domain": 990}:
        raise ValueError("exact989 calibration plus990 g_domain selected frames required")
    return previous.ordered(new), terminal


def fixed_indices(videos: list[dict]) -> list[int]:
    strata = {}
    for index, video in enumerate(videos):
        row = video["transaction"]
        key = (row["role"], row["binary_label"], tuple(row["video_id"].split("_")[:2]))
        strata.setdefault(key, index)
    return sorted(set(strata.values()) | set(range(0, len(videos), 100)))


def accepted_train() -> tuple[dict, dict, dict]:
    report_path = ROOT / "results/phase1/oulu-preprocessing278-train-v1.json"
    report = read_json(report_path)
    records = {name: read_verified_json(previous.OUTPUT / name, digest)
               for name, digest in report["private_record_sha256"].items()}
    plan, resources = records["plan.json"], records["resources.json"]
    lease = read_json(previous.OUTPUT / "attempt_lock.json")
    hashes = {
        "scripts/preprocess_oulu278.py": "041709644b6ecf89ff6bb21ce2d0742a85495a672c239c40b28cbeb8b7ad770f",
        "scripts/recover_oulu278.py": "60e5ec158dca5b2be9feb7c5e098a6cc12644606a8f51be4dbdd6dbce3b21f1d",
        "tests/test_preprocessing_batch.py": "5045f3975fc05bd9e99ed2967d115851ffffb43b6f35d9959de28a8c303eb964",
    }
    if any(_sha256(ROOT / name) != expected for name, expected in hashes.items()):
        raise ValueError("review279 executed-source reconciliation drift")
    if records["supervisor.json"]["runner_sha256"] != hashes["scripts/preprocess_oulu278.py"] or lease["parent_pid"] != records["supervisor.json"]["pid"] or lease["plan_sha256"] != report["private_record_sha256"]["plan.json"]:
        raise ValueError("accepted278 launch/runner/attempt reconciliation drift")
    if resources["completion_claimed"] is not True or resources["attempts"] != 1 or resources["automatic_retry"] is not False:
        raise ValueError("accepted single completed278 attempt required")
    visual_report = read_json(ROOT / "results/phase1/oulu-preprocessing278-visual-review-v1.json")
    read_verified_json(previous.OUTPUT / "visual_review.json", visual_report["private_visual_review_sha256"])
    if visual_report["private_resources_sha256"] != report["private_record_sha256"]["resources.json"] or visual_report["private_readback_sha256"] != report["private_record_sha256"]["readback.json"]:
        raise ValueError("accepted278 visual/software receipt joins required")
    reconciliation = {
        "source_sha256": hashes, "supervisor_runner_hash_matches_review279": True,
        "attempt_parent_matches_supervisor": True, "attempt_plan_matches_accepted_plan": True,
        "reported_attempts": 1, "automatic_retry": False,
        "supervisor_sha256": report["private_record_sha256"]["supervisor.json"],
        "attempt_lock_sha256": _sha256(previous.OUTPUT / "attempt_lock.json"),
        "accepted_resources_sha256": report["private_record_sha256"]["resources.json"],
        "limitation": "reconciliation_of_existing_private_records_not_independent_execution_witness",
    }
    return plan, records["combined_ledger.json"], reconciliation


def measured_usage(group: int) -> dict:
    measured = usage(group, OUTPUT / ".unused")
    measured["rss_bytes"] = max(measured["rss_bytes"], resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
    measured["output_bytes"] = sum(previous.tree_bytes(path) for path in (
        previous.ACQUISITION, previous.PILOT, previous.OUTPUT, OUTPUT)) + measured["temporary_bytes"]
    return measured


def enforce(plan: dict, measured: dict) -> None:
    if time.time() >= plan["deadline_unix_seconds"]:
        raise TimeoutError("four-hour package execution/readback deadline")
    if measured["rss_bytes"] > CAPS["rss_bytes"]:
        raise MemoryError("4GiB process-group RSS cap")
    if measured["output_bytes"] > CAPS["output_bytes"] - RESERVE:
        raise OSError("24GiB total274/276/278/280 storage cap with final-record reserve")


def make_plan() -> dict:
    authority = read_json(OUTPUT / "owner_approval.json")
    if authority["explicit_owner_approval"] is not True or authority["caps"] != CAPS or authority["selected_answer"] != APPROVAL:
        raise ValueError("exact combined279 package authority required")
    check_policy()
    old, ledger, reconciliation = accepted_train()
    previous.guard(old)
    sources = dict(old["sources"])
    audit_path = BASE / "oulu_benchmark272_audit_v1.json"
    audit = read_verified_json(audit_path, "fdf57e7dbb06c637498a8d7501007948815c27cb18fa0a07e32b64244d801e1b")
    roles_path = previous.pilot.FROZEN / "oulu_npu_roles.csv"
    if _sha256(roles_path) != audit["source_sha256"][str(roles_path)]:
        raise ValueError("frozen role hash drift")
    roles = {row["video_id"]: row for row in csv.DictReader(roles_path.read_text().splitlines())}
    rows = []
    for path in sorted((previous.pilot.TRANSACTIONS / "transactions").glob("*.json")):
        row = read_verified_json(path, audit["source_sha256"][str(path)])
        if any(row[key] != roles[row["video_id"]][key] for key in ("role", "binary_label")):
            raise ValueError("frozen role/transaction join drift")
        sources[str(path)] = audit["source_sha256"][str(path)]
        rows.append(row)
    new, terminal = partition(rows, [row["video_id"] for row in ledger["rows"]])
    expected_train = {
        video["transaction"]["video_id"]: (video, previous.OUTPUT, index, 4)
        for index, video in enumerate(old["videos"])}
    expected_train.update({
        video["transaction"]["video_id"]: (video, previous.PILOT, index, 2)
        for index, video in enumerate(old["reused_videos"])})
    frozen = {row["video_id"]: row for row in rows}
    legacy = []
    for row in ledger["rows"]:
        video, root, index, digits = expected_train[row["video_id"]]
        if video["transaction"] != frozen[row["video_id"]] or row["record_path"] != str(root / "transactions" / f"{index:0{digits}d}.json") or row["detector_status"] != "success":
            raise ValueError("accepted train parent/location/outcome drift")
        legacy.append({"video": video, "root": str(root), "index": index, "digits": digits,
                       "record_sha256": row["record_sha256"],
                       "config_sha256": _sha256(LEGACY)})
        sources[row["record_path"]] = row["record_sha256"]
    videos = []
    frames, payload, selected_pixels = 0, 0, 0
    for row in new:
        path = BASE / "oulu_per_video_audit_v1/videos" / (row["video_id"] + ".json")
        media = read_verified_json(path, row["media_record_sha256"])
        if media["media_sha256"] != row["media_sha256"]:
            raise ValueError("remaining media parent drift")
        sources[str(path)] = row["media_record_sha256"]
        videos.append({"transaction": row, "media_path": str(path)})
        frames += media["frame_count"]
        payload += media["byte_size"]
        selected_pixels += row["selected_frame"]["height"] * row["selected_frame"]["width"]
    if frames != MEASURED_PROPOSAL["verified_native_frames"] or payload != MEASURED_PROPOSAL["selected_payload_bytes"]:
        raise ValueError("approved measured remaining-media scope drift")
    for path in (ACTIVE, LEGACY, ROOT / "configs/experiment_core_v1.yaml",
                 ROOT / "src/fas/preprocessing_policy.py", ROOT / "src/fas/preregistration.py",
                 Path(__file__), ROOT / "tests/test_preprocessing_completion.py",
                 ROOT / "tests/test_preregistration.py",
                 ROOT / "docs/279-review-doc278-train-batch-and-reconnection.md",
                 ROOT / "results/phase1/oulu-preprocessing278-train-v1.json",
                 ROOT / "results/phase1/oulu-preprocessing278-visual-review-v1.json",
                 OUTPUT / "owner_approval.json"):
        sources[str(path)] = _sha256(path)
    plan = {key: old[key] for key in ("paths", "guard_context", "archive_identities",
                                    "recovery_binding_path", "recovery_binding_sha256",
                                    "additive_recovery_binding_path", "additive_recovery_binding_sha256",
                                    "ffmpeg", "model_sha256")}
    plan.update(checkpoint=280, videos=videos, legacy=legacy, terminal_transactions=terminal,
                all_transactions=sorted(rows, key=lambda row: row["video_id"]), sources=sources,
                active_config_path=str(ACTIVE), active_config_sha256=_sha256(ACTIVE),
                historical_parameter_recipe_sha256=_sha256(LEGACY),
                accepted278_reconciliation=reconciliation, selected_pixels=selected_pixels,
                visual_indices=fixed_indices(videos), caps=CAPS,
                deadline_unix_seconds=authority["deadline_unix_seconds"],
                storage_scope="total274_276_278_280_including_model_frames_crops_temporary_manifests_logs_records")
    check_bindings(sources)
    previous.guard(plan)
    if _sha256(previous.MODEL) != MODEL_SHA256:
        raise ValueError("accepted detector weight drift")
    enforce(plan, measured_usage(os.getpgrp()))
    write_immutable_record(OUTPUT / "plan.json", plan)
    print("PLAN280", len(new), "new", len(legacy), "reused", len(terminal), "preexisting terminal", flush=True)
    return plan


def write_png(relative: str, rgb) -> dict:
    from fas.visual import png_bytes

    payload = png_bytes(rgb)
    path = OUTPUT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(payload)
    return {"sha256": hashlib.sha256(payload).hexdigest(),
            "RGB_sha256": hashlib.sha256(rgb.tobytes()).hexdigest(), "shape": list(rgb.shape)}


def produce_unit(session, index: int, video: dict, archive, member, plan: dict) -> dict:
    import cv2
    from fas.preprocessing import detect_face, shared_context_crop

    transaction = video["transaction"]
    if transaction["role"] not in NEW_ROLES or transaction["selected_frame"] is None:
        raise ValueError("only approved selected non-train source frames may be inferred")
    media = read_verified_json(Path(video["media_path"]), transaction["media_record_sha256"])
    checked_member(member, media)
    selected = transaction["selected_frame"]
    write_immutable_record(OUTPUT / "attempts" / f"{index:04d}.json", {
        "index": index, "video_id": transaction["video_id"], "role": transaction["role"], "status": "started"})
    captured = []
    with tempfile.TemporaryDirectory(prefix=".payload280-", dir=OUTPUT) as temporary:
        path = Path(temporary) / "selected.avi"
        digest, count = hashlib.sha256(), 0
        with archive.extractfile(member) as source, path.open("xb") as target:
            while block := source.read(1024 ** 2):
                count += len(block)
                if count > media["byte_size"] or count > 128 * 1024 ** 2:
                    raise ValueError("selected payload byte cap")
                digest.update(block)
                target.write(block)
        if count != media["byte_size"] or digest.hexdigest() != transaction["media_sha256"]:
            raise ValueError("selected media byte/hash drift")

        def consume(order, rgb):
            if order == selected["decode_order"]:
                if rgb.shape != (selected["height"], selected["width"], 3) or hashlib.sha256(rgb.tobytes()).hexdigest() != selected["rgb_sha256"]:
                    raise ValueError("frozen selected RGB identity drift")
                captured.append(rgb.copy())

        stream_frames(path, media, consume, timeout=min(180, max(0.001, plan["deadline_unix_seconds"] - time.time())))
        if len(captured) != 1:
            raise ValueError("exact frozen selected frame required; no replacement")
    row = {key: transaction[key] for key in ("video_id", "role", "binary_label", "selected_frame", "media_record_sha256", "media_sha256")}
    row.update(index=index, model_sha256=MODEL_SHA256, config_sha256=plan["active_config_sha256"],
               replacement=False, retain_original_denominator=True, model_score=None, classifier_error=None)
    relative = f"frames/{index:04d}.png"
    row["selected_RGB_asset"] = {"path": relative, **write_png(relative, captured[0])}
    started = time.monotonic()
    try:
        box, landmarks = detect_face(session, captured[0])
        crop, geometry = shared_context_crop(captured[0], box[:4], landmarks)
    except ValueError as error:
        if str(error) not in previous.FAILURES:
            raise
        row.update(detector_status="failed", final_k1_action="non_accept", failure=str(error), assets={})
    else:
        row.update(detector_status="success", face_box_xyxy=box[:4].tolist(), detector_confidence=float(box[4]),
                   landmarks=landmarks.tolist(), geometry=geometry, crop_shape=list(crop.shape),
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
    check_policy()
    previous.guard(plan)
    if _sha256(previous.MODEL) != MODEL_SHA256:
        raise ValueError("accepted detector weight drift")
    if subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0] != plan["ffmpeg"]:
        raise ValueError("accepted decoder version drift")
    options = ort.SessionOptions()
    options.intra_op_num_threads = options.inter_op_num_threads = 1
    session = ort.InferenceSession(str(previous.MODEL), sess_options=options, providers=["CPUExecutionProvider"])
    if session.get_providers() != ["CPUExecutionProvider"]:
        raise ValueError("CPU-only provider required")
    cv2.setNumThreads(1)
    indexed = {}
    for index, video in enumerate(plan["videos"]):
        media = read_json(Path(video["media_path"]))
        indexed.setdefault(media["media_archive"], []).append((index, video, media))
    counts, native, payload, seconds = Counter(), 0, 0, 0.0
    for name, members in sorted(indexed.items()):
        path = Path(plan["paths"]["input_root"]) / name
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as handle, tarfile.open(fileobj=handle, mode="r:") as archive:
            expected = tuple(plan["archive_identities"][name])
            if archive_identity(handle) != expected:
                raise ValueError("archive descriptor identity drift before payloads")
            wanted = {media["media_relpath"] for _, _, media in members}
            if len(wanted) != len(members):
                raise ValueError("duplicate selected archive member")
            headers = {}
            for member in archive:
                if member.name in wanted:
                    if member.name in headers:
                        raise ValueError("duplicate selected tar header")
                    headers[member.name] = member
            if set(headers) != wanted:
                raise ValueError("missing selected archive member")
            for index, video, media in members:
                if archive_identity(handle) != expected:
                    raise ValueError("archive identity drift before unit")
                if time.time() >= plan["deadline_unix_seconds"]:
                    raise TimeoutError("package deadline before unit")
                row = produce_unit(session, index, video, archive, headers[media["media_relpath"]], plan)
                counts[row["detector_status"]] += 1
                native += media["frame_count"]
                payload += media["byte_size"]
                seconds += row["detector_and_crop_wall_seconds"]
                print("BATCH280", index, row["role"], row["detector_status"], flush=True)
            if archive_identity(handle) != expected:
                raise ValueError("archive descriptor drift after payloads")
    check_bindings(plan["sources"])
    previous.guard(plan)
    write_immutable_record(OUTPUT / "worker_completion.json", {
        "transactions": len(plan["videos"]), "detector_success": counts["success"],
        "detector_failure": counts["failed"], "verified_native_frames": native,
        "selected_payload_bytes": payload, "detector_and_crop_wall_seconds": seconds,
        "provider": session.get_providers(), "gpu_seconds": 0, "model_scores": 0, "fitted_scores": 0})


def validate_unit(video: dict, root: Path, index: int, digits: int, config_sha: str,
                  record_sha: str | None = None) -> tuple[dict, dict]:
    import cv2
    import numpy as np
    from fas.preprocessing import shared_context_crop

    transaction = video["transaction"]
    path = root / "transactions" / f"{index:0{digits}d}.json"
    row = read_verified_json(path, record_sha or _sha256(path))
    if any(row[key] != transaction[key] for key in ("video_id", "role", "binary_label", "selected_frame", "media_record_sha256", "media_sha256")):
        raise ValueError("frozen source/frame/media/role parent join drift")
    if row["role"] not in ROLE_COUNTS or row["index"] != index or row["model_sha256"] != MODEL_SHA256 or row["config_sha256"] != config_sha or row["replacement"] is not False or row["retain_original_denominator"] is not True or row["model_score"] is not None or row.get("classifier_error") is not None:
        raise ValueError("config/model/scoreless/denominator/no-replacement join drift")
    media = read_verified_json(Path(video["media_path"]), transaction["media_record_sha256"])
    if media["media_sha256"] != transaction["media_sha256"]:
        raise ValueError("media content parent drift")
    assets = {}

    def image(relative, commitment):
        target = root / relative
        if target.is_symlink() or _sha256(target) != commitment["sha256"]:
            raise ValueError("PNG asset commitment drift")
        bgr = cv2.imread(str(target), cv2.IMREAD_UNCHANGED)
        if bgr is None or bgr.dtype != np.uint8 or bgr.ndim != 3 or bgr.shape[2] != 3:
            raise ValueError("uint8 RGB PNG required")
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        if "shape" in commitment and (list(rgb.shape) != commitment["shape"] or hashlib.sha256(rgb.tobytes()).hexdigest() != commitment["RGB_sha256"]):
            raise ValueError("RGB pixel/shape commitment drift")
        assets[relative] = commitment["sha256"]
        return rgb

    stem = f"{index:0{digits}d}"
    relative = f"frames/{stem}.png"
    if row["selected_RGB_asset"]["path"] != relative:
        raise ValueError("exact selected RGB asset path required")
    rgb = image(relative, row["selected_RGB_asset"])
    frame = transaction["selected_frame"]
    if frame is None or rgb.shape != (frame["height"], frame["width"], 3) or hashlib.sha256(rgb.tobytes()).hexdigest() != frame["rgb_sha256"]:
        raise ValueError("frozen selected RGB identity drift")
    if row["detector_status"] == "failed":
        if row.get("final_k1_action") != "non_accept" or row.get("assets") or row.get("failure") not in previous.FAILURES:
            raise ValueError("failed detection must retain terminal non_accept without crops")
    elif row["detector_status"] == "success":
        if not np.isfinite(row["detector_confidence"]) or not 0.5 <= row["detector_confidence"] <= 1:
            raise ValueError("frozen detector confidence threshold required")
        crop, geometry = shared_context_crop(rgb, np.asarray(row["face_box_xyxy"]), np.asarray(row["landmarks"]))
        required = {f"crops/{stem}-{name}.png" for name in ("shared", "224", "518")}
        if row["geometry"] != geometry or set(row["assets"]) != required or row["crop_shape"] != list(crop.shape) or row["crop_RGB_sha256"] != hashlib.sha256(crop.tobytes()).hexdigest():
            raise ValueError("shared-context geometry/asset commitment drift")
        for name in ("shared", "224", "518"):
            relative = f"crops/{stem}-{name}.png"
            expected = crop if name == "shared" else cv2.resize(crop, (int(name), int(name)), interpolation=cv2.INTER_CUBIC)
            if not np.array_equal(image(relative, row["assets"][relative]), expected):
                raise ValueError("shared crop or bicubic branch pixel join drift")
    else:
        raise ValueError("explicit detector success/failed outcome required")
    entry = {
        "video_id": row["video_id"], "role": row["role"], "binary_label": row["binary_label"],
        "selected_frame": frame, "detector_status": row["detector_status"],
        "final_k1_action": row.get("final_k1_action"), "model_score": None, "classifier_error": None,
        "replacement": False, "retain_original_denominator": True,
        "record_path": str(path), "record_sha256": _sha256(path),
        "source_record_config_sha256": row["config_sha256"], "model_sha256": row["model_sha256"],
        "asset_root": str(root), "asset_sha256": assets}
    return entry, assets


def validate_manifest(plan: dict, rows: list[dict]) -> None:
    original = {row["video_id"]: row for row in plan["all_transactions"]}
    ids = [row["video_id"] for row in rows]
    if len(original) != 4950 or len(ids) != 4950 or len(set(ids)) != 4950 or set(ids) != set(original):
        raise ValueError("exact4950 unique original manifest rows required")
    counts, selected, terminal = Counter(), 0, 0
    for row in rows:
        parent = original[row["video_id"]]
        if any(row[key] != parent[key] for key in ("role", "binary_label", "selected_frame")):
            raise ValueError("manifest frozen role/label/frame join drift")
        if row["model_score"] is not None or row["classifier_error"] is not None or row["retain_original_denominator"] is not True or row["replacement"] is not False or row["active_config_sha256"] != plan["active_config_sha256"]:
            raise ValueError("scoreless active-pin/denominator manifest required")
        counts[row["role"]] += 1
        if parent["selected_frame"] is None:
            terminal += 1
            if row["detector_status"] != "not_run" or row["final_k1_action"] != "non_accept" or row["asset_sha256"]:
                raise ValueError("pre-detector failure cannot receive fabricated pixels/outcomes")
        else:
            selected += 1
            if row["detector_status"] not in {"success", "failed"}:
                raise ValueError("selected manifest row needs explicit detector outcome")
            if row["detector_status"] == "failed" and row["final_k1_action"] != "non_accept":
                raise ValueError("failed selected row must remain non_accept")
    if counts != ROLE_COUNTS or selected != 4949 or terminal != 1:
        raise ValueError("exact4950/4949/one-failure original denominators required")


def make_sheets(plan: dict, new_rows: list[dict]) -> list[dict]:
    import cv2
    import numpy as np

    failures = {index for index, row in enumerate(new_rows) if row["detector_status"] == "failed"}
    sheets = []
    for kind, indices in (("fixed", plan["visual_indices"]), ("failures", sorted(failures))):
        for page, offset in enumerate(range(0, len(indices), 32)):
            subset = indices[offset:offset + 32]
            sheet = np.full((((len(subset) + 3) // 4) * 180, 640, 3), 255, np.uint8)
            for slot, index in enumerate(subset):
                relative = f"frames/{index:04d}.png" if index in failures else f"crops/{index:04d}-224.png"
                bgr = cv2.imread(str(OUTPUT / relative), cv2.IMREAD_COLOR)
                if bgr is None:
                    raise ValueError("fixed/failure visual source missing")
                top, left = slot // 4 * 180, slot % 4 * 160
                cv2.putText(sheet, f"{index:04d}", (left + 3, top + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
                sheet[top + 20:top + 180, left:left + 160] = cv2.resize(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), (160, 160), interpolation=cv2.INTER_CUBIC)
            relative = f"visual/{kind}-{page:02d}.png"
            commitment = write_png(relative, sheet)
            restored = cv2.imread(str(OUTPUT / relative), cv2.IMREAD_COLOR)
            if restored is None or not np.array_equal(cv2.cvtColor(restored, cv2.COLOR_BGR2RGB), sheet):
                raise ValueError("saved visual-sheet reconstruction mismatch")
            sheets.append({"path": relative, "indices": subset, "kind": kind, **commitment})
    return sheets


def validate_readback_summary(plan: dict, readback: dict, manifest: dict) -> None:
    rows = manifest["rows"]
    expected = {
        "originals": len(plan["all_transactions"]),
        "selected": sum(row["selected_frame"] is not None for row in plan["all_transactions"]),
        "preexisting_terminal_failure": len(plan["terminal_transactions"]),
        "reused_train": len(plan["legacy"]),
        "transactions": len(plan["videos"]),
        "combined_detector_success": sum(row["detector_status"] == "success" for row in rows),
        "combined_detector_failure": sum(row["detector_status"] == "failed" for row in rows),
        "detector_success": sum(row["detector_status"] == "success" and not row.get("reused", False) for row in rows),
        "detector_failure": sum(row["detector_status"] == "failed" and not row.get("reused", False) for row in rows),
        "active_config_sha256": plan["active_config_sha256"],
        "role_originals": dict(Counter(row["role"] for row in rows)),
        "role_detector_success": dict(Counter(row["role"] for row in rows if row["detector_status"] == "success")),
        "provider": ["CPUExecutionProvider"], "gpu_seconds": 0, "model_scores": 0, "fitted_scores": 0,
    }
    if any(type(readback.get(key)) is not type(value) or readback[key] != value for key, value in expected.items()):
        raise ValueError("final readback/manifest exact population and active-pin joins required")
    if manifest["originals"] != expected["originals"] or manifest["selected"] != expected["selected"] or manifest["active_config_sha256"] != plan["active_config_sha256"]:
        raise ValueError("full manifest header/population/config mismatch")


def verify(plan: dict) -> dict:
    check_bindings(plan["sources"])
    check_policy()
    previous.guard(plan)
    if _sha256(previous.MODEL) != MODEL_SHA256:
        raise ValueError("final detector model hash drift")
    expected_files = {f"{index:04d}.json" for index in range(len(plan["videos"]))}
    if {path.name for path in (OUTPUT / "transactions").iterdir()} != expected_files:
        raise ValueError("exact remaining transaction file set required")
    rows, new_rows, roots, counts = [], [], {}, Counter()
    native, payload = 0, 0
    for index, video in enumerate(plan["videos"]):
        entry, assets = validate_unit(video, OUTPUT, index, 4, plan["active_config_sha256"])
        roots.setdefault(str(OUTPUT), set()).update(assets)
        counts[entry["detector_status"]] += 1
        entry.update(active_config_sha256=plan["active_config_sha256"], reused=False)
        rows.append(entry)
        new_rows.append(entry)
        media = read_json(Path(video["media_path"]))
        native += media["frame_count"]
        payload += media["byte_size"]
        if index % 100 == 0:
            print("READBACK280_NEW", index, flush=True)
    completion = read_json(OUTPUT / "worker_completion.json")
    required = {"transactions": len(plan["videos"]), "detector_success": counts["success"],
                "detector_failure": counts["failed"], "verified_native_frames": native,
                "selected_payload_bytes": payload, "provider": ["CPUExecutionProvider"],
                "gpu_seconds": 0, "model_scores": 0, "fitted_scores": 0}
    if any(type(completion.get(key)) is not type(value) or completion[key] != value for key, value in required.items()):
        raise ValueError("worker exact completion/accounting mismatch")
    for number, legacy in enumerate(plan["legacy"]):
        root = Path(legacy["root"])
        entry, assets = validate_unit(legacy["video"], root, legacy["index"], legacy["digits"],
                                      legacy["config_sha256"], legacy["record_sha256"])
        if entry["role"] != "train" or entry["detector_status"] != "success":
            raise ValueError("accepted train output role/outcome drift")
        roots.setdefault(str(root), set()).update(assets)
        entry.update(active_config_sha256=plan["active_config_sha256"], reused=True)
        rows.append(entry)
        if number % 100 == 0:
            print("READBACK280_REUSED", number, flush=True)
    for root, expected in roots.items():
        observed = {path.relative_to(Path(root)).as_posix() for folder in ("frames", "crops")
                    for path in (Path(root) / folder).glob("*")}
        if observed != expected:
            raise ValueError("unexpected/missing image assets in full manifest")
    for original in plan["terminal_transactions"]:
        rows.append({**original, "active_config_sha256": plan["active_config_sha256"],
                     "asset_sha256": {}, "replacement": False, "reused": True})
    rows.sort(key=lambda row: row["video_id"])
    validate_manifest(plan, rows)
    sheets = make_sheets(plan, new_rows)
    check_bindings(plan["sources"])
    previous.guard(plan)
    originals = len(plan["all_transactions"])
    selected = sum(row["selected_frame"] is not None for row in plan["all_transactions"])
    manifest = {"checkpoint": 280, "originals": originals, "selected": selected,
                "preexisting_terminal_failure": len(plan["terminal_transactions"]), "rows": rows,
                "active_config_path": str(ACTIVE), "active_config_sha256": plan["active_config_sha256"],
                "historical_parameter_recipe_sha256": plan["historical_parameter_recipe_sha256"],
                "historical_recipe_equivalence_verified": True, "scientific_readiness": False}
    write_immutable_record(OUTPUT / "full_manifest.json", manifest)
    validate_manifest(plan, read_json(OUTPUT / "full_manifest.json")["rows"])
    result = {**required, "originals": originals, "selected": selected,
              "preexisting_terminal_failure": len(plan["terminal_transactions"]), "reused_train": len(plan["legacy"]),
              "combined_detector_success": sum(row["detector_status"] == "success" for row in rows),
              "combined_detector_failure": sum(row["detector_status"] == "failed" for row in rows),
              "full_manifest_sha256": _sha256(OUTPUT / "full_manifest.json"),
              "active_config_sha256": plan["active_config_sha256"],
              "visual_sheets": sheets, "visual_inspection_completed": False,
              "role_originals": dict(Counter(row["role"] for row in rows)),
              "role_detector_success": dict(Counter(row["role"] for row in rows if row["detector_status"] == "success")),
              "scientific_readiness": False}
    validate_readback_summary(plan, result, manifest)
    write_immutable_record(OUTPUT / "readback.json", result)
    return result


def failure_rows(plan: dict, failure: str) -> None:
    rows = []
    for index, video in enumerate(plan["videos"]):
        transaction = video["transaction"]
        path = OUTPUT / "transactions" / f"{index:04d}.json"
        rows.append({
            "index": index, "video_id": transaction["video_id"], "role": transaction["role"],
            "binary_label": transaction["binary_label"], "selected_frame": transaction["selected_frame"],
            "detector_status": "unverified_after_attempt_failure", "final_k1_action": "non_accept",
            "worker_record_sha256": _sha256(path) if path.is_file() and not path.is_symlink() else None,
            "retain_original_denominator": True, "replacement": False, "failure": failure})
    write_immutable_record(OUTPUT / "failure_rows.json", {
        "rows": rows, "accepted_train_untouched": 2970, "retained_preexisting_failure": 1,
        "automatic_retry": False})


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
        manifest = read_verified_json(OUTPUT / "full_manifest.json", readback["full_manifest_sha256"])
        validate_manifest(plan, manifest["rows"])
        validate_readback_summary(plan, readback, manifest)
        if manifest["active_config_sha256"] != _sha256(ACTIVE):
            raise ValueError("full manifest active configuration drift")
        for row in manifest["rows"]:
            if row["selected_frame"] is not None and _sha256(Path(row["record_path"])) != row["record_sha256"]:
                raise ValueError("final selected row commitment drift")
        check_bindings(plan["sources"])
        check_policy()
        previous.guard(plan)
        final = measured_usage(os.getpgrp())
        final["rss_bytes"] = max(final["rss_bytes"], resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024)
        peak = {key: max(peak[key], final[key]) for key in peak}
        enforce(plan, peak)
    except Exception as error:
        failure = type(error).__name__ + ": " + str(error)
        print("BATCH280 FAILED", failure, file=sys.stderr, flush=True)
    finally:
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
    if failure:
        failure_rows(plan, failure)
    result = {
        "checkpoint": 280, "completion_claimed": failure is None and readback is not None,
        "failure": failure, "caps": CAPS, "sampled_peaks": peak,
        "wall_seconds": time.monotonic() - started,
        "package_wall_seconds": time.time() - read_json(OUTPUT / "owner_approval.json")["started_unix_seconds"],
        "planned_new_selected": len(plan["videos"]), "reused_train": 2970,
        "preexisting_terminal_failure": 1, "active_config_sha256": plan["active_config_sha256"],
        "readback_sha256": _sha256(OUTPUT / "readback.json") if readback else None,
        "visual_inspection_pending": failure is None, "gpu_seconds": 0,
        "attempts": 1, "automatic_retry": False, "scientific_readiness": False}
    write_immutable_record(OUTPUT / "resources.json", result)
    if read_json(OUTPUT / "resources.json") != result:
        raise RuntimeError("resources receipt readback mismatch")
    print("BATCH280_TERMINAL", json.dumps(result), flush=True)
    return result


def publish_summary(result: dict) -> None:
    complete = result["completion_claimed"] is True
    readback = read_json(OUTPUT / "readback.json") if complete else None
    plan_path = OUTPUT / "plan.json"
    plan = read_json(plan_path) if plan_path.exists() else None
    summary = {
        "checkpoint": 280, "status": "software_complete_visual_review_pending" if complete else "stopped_failure_no_retry",
        "completion_claimed": complete, "visual_inspection_completed": False,
        "failure_category": result["failure"].split(":", 1)[0] if result.get("failure") else None,
        "caps": CAPS, "sampled_peaks": result.get("sampled_peaks"),
        "batch_package_wall_seconds": result.get("package_wall_seconds"),
        "new_originals": 1980, "new_selected": 1979, "reused_train": 2970,
        "originals": 4950, "selected": 4949, "preexisting_terminal_failure": 1,
        "new_detector_success": readback["detector_success"] if readback else None,
        "new_detector_failure": readback["detector_failure"] if readback else None,
        "combined_detector_success": readback["combined_detector_success"] if readback else None,
        "combined_detector_failure": readback["combined_detector_failure"] if readback else None,
        "verified_native_frames": readback["verified_native_frames"] if readback else None,
        "selected_payload_bytes": readback["selected_payload_bytes"] if readback else None,
        "role_originals": readback["role_originals"] if readback else None,
        "role_detector_success": readback["role_detector_success"] if readback else None,
        "active_preprocessing_config": "configs/preprocessing_v3.yaml",
        "active_config_sha256": _sha256(ACTIVE), "historical_v2_and_pilot_unchanged": True,
        "accepted278_reconciliation": plan["accepted278_reconciliation"] if plan else None,
        "automatic_retry": False, "archive_rehashes": 0, "model_downloads": 0,
        "gpu_seconds": 0, "calibration_fitted_scores": 0, "target_access": False,
        "oulu_audit_status": "complete", "other_domain_not_audited_fields": 6, "scientific_readiness": False,
        "private_record_sha256": {
            path.relative_to(OUTPUT).as_posix(): _sha256(path)
            for path in (OUTPUT / "owner_approval.json", OUTPUT / "supervisor.json",
                         OUTPUT / "plan.json", OUTPUT / "attempt_lock.json",
                         OUTPUT / "worker_completion.json", OUTPUT / "full_manifest.json",
                         OUTPUT / "readback.json", OUTPUT / "resources.json", OUTPUT / "package_failure.json")
            if path.exists()}}
    write_immutable_record(ROOT / "results/phase1/oulu-preprocessing280-completion-v1.json", summary)


def status() -> dict:
    authority = read_json(OUTPUT / "owner_approval.json")
    return {"checkpoint": 280, "new_records_written": len(list((OUTPUT / "transactions").glob("*.json"))),
            "new_records_expected": 1979, "reused_train": 2970, "preexisting_terminal_failure": 1,
            "deadline_unix_seconds": authority["deadline_unix_seconds"],
            "plan_committed": (OUTPUT / "plan.json").exists(),
            "terminal": read_json(OUTPUT / "resources.json") if (OUTPUT / "resources.json").exists() else None,
            "package_failure": read_json(OUTPUT / "package_failure.json") if (OUTPUT / "package_failure.json").exists() else None}


def child_plan() -> dict:
    plan = read_json(OUTPUT / "plan.json")
    lease = read_json(OUTPUT / "attempt_lock.json")
    if lease["plan_sha256"] != _sha256(OUTPUT / "plan.json") or lease["parent_pid"] != os.getppid() or os.getsid(0) != os.getpid():
        raise ValueError("single supervised parent/plan lease required")
    previous.arm_deadline(plan["deadline_unix_seconds"])
    return plan


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
        raise FileExistsError("one authorized package only; no automatic retry")
    check_policy()
    started = time.time()
    write_immutable_record(OUTPUT / "owner_approval.json", {
        "checkpoint": 280, "explicit_owner_approval": True, "selected_answer": APPROVAL,
        "caps": CAPS, "started_unix_seconds": started, "deadline_unix_seconds": started + CAPS["wall_seconds"],
        "review279_sha256": _sha256(ROOT / "docs/279-review-doc278-train-batch-and-reconnection.md"),
        "active_config_sha256": _sha256(ACTIVE), "measured_proposal": MEASURED_PROPOSAL,
        "scope": "selected_source_calibration_g_domain_images_full_manifest_active_pin_no_scores_fitting_target_access",
        "automatic_retry": False, "archive_rehash_authorized": False})
    with (OUTPUT / "execution.log").open("xb", buffering=0) as log:
        os.dup2(log.fileno(), 1)
        os.dup2(log.fileno(), 2)
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    write_immutable_record(OUTPUT / "supervisor.json", {
        "pid": os.getpid(), "started_unix_seconds": started,
        "runner_sha256": _sha256(Path(__file__)), "automatic_retry": False})
    print("BATCH280_START", os.getpid(), started, flush=True)
    previous.arm_deadline(started + CAPS["wall_seconds"])
    try:
        plan = make_plan()
        result = supervise(plan)
        publish_summary(result)
        return 0 if result["completion_claimed"] else 1
    except Exception as error:
        write_immutable_record(OUTPUT / "package_failure.json", {
            "error_type": type(error).__name__, "message": str(error),
            "automatic_retry": False, "scientific_readiness": False})
        if not (ROOT / "results/phase1/oulu-preprocessing280-completion-v1.json").exists():
            publish_summary({"completion_claimed": False, "failure": type(error).__name__ + ": " + str(error)})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
