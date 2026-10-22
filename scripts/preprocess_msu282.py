"""One owner-approved MSU release/integrity/primary-image package."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import stat
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import inventory_msu as native
import preprocess_oulu280 as images
import preprocess_oulu278 as retained
from fas.freeze import write_immutable_record
from fas.lineage import decoded_tokens
from fas.media import probe_video
from fas.msu import METADATA_SHA256, inventory_headers
from fas.oulu import _sha256
from fas.preprocessing_policy import MODEL_SHA256
from fas.transactions import technical_transaction
from prepare_oulu_pilot243 import check_bindings, stream_frames, usage
from verify_oulu_archive_guard_batch09 import read_verified_json

BASE = images.BASE
OUTPUT = BASE / "msu_preprocessing282_v1"
INPUT = ROOT / "MSU"
FROZEN = retained.pilot.FROZEN
CAPS = {"wall_seconds": 14400, "rss_bytes": 4 * 1024 ** 3,
        "output_bytes": 40 * 1024 ** 3, "gpu_seconds": 0}
RESERVE = 64 * 1024 ** 2
EXPECTED_ROLES = {"train": 168, "branch_calibration": 56, "g_domain": 56}
EXPECTED_GROUPS = {"train": 21, "branch_calibration": 7, "g_domain": 7}
APPROVAL = (
    "Đồng ý trọn gói MSU: code/tests + kiểm tra release/role/integrity + "
    "decode/chọn frame/preprocess 280 video + manifest/readback/visual; "
    "CPU-only, tối đa 4 giờ/4 GiB RSS/40 GiB tổng private giữ lại; không retry/nới cap"
)


def read_json(path: Path) -> dict:
    return retained.read_json(path)


def identity(path: Path) -> list[int]:
    value = path.lstat()
    if not stat.S_ISREG(value.st_mode):
        raise ValueError("regular non-symlink input required")
    return [value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns]


def archive_guard(plan: dict) -> None:
    if {path.name for path in INPUT.glob("*.zip")} != set(plan["archive_identities"]):
        raise ValueError("MSU archive population drift")
    for name, expected in plan["archive_identities"].items():
        if identity(INPUT / name) != expected:
            raise ValueError("MSU input identity drift; no automatic recovery")


def group_checks(videos: list[dict], roles: list[dict]) -> dict:
    canonical = {row["video_id"]: row for row in videos}
    assigned = {row["video_id"]: row for row in roles}
    if len(canonical) != 280 or len(videos) != 280 or len(assigned) != len(roles) or set(canonical) != set(assigned):
        raise ValueError("exact280 release/canonical/role IDs required")
    if Counter(row["role"] for row in roles) != EXPECTED_ROLES:
        raise ValueError("exact frozen168/56/56 role population required")
    subjects, official, combinations = defaultdict(set), defaultdict(set), defaultdict(set)
    for key, row in canonical.items():
        role = assigned[key]
        if any(row[field] != role[field] for field in ("dataset", "subject_id", "binary_label")):
            raise ValueError("canonical subject/class/role join drift")
        if row["dataset"] != "MSU-MFSD" or row["official_split"] not in {"train", "test"}:
            raise ValueError("native MSU source partition required")
        if row["group_id"] != row["subject_id"] or row["group_unit"] != "subject":
            raise ValueError("native subject grouping required")
        subjects[role["role"]].add(row["subject_id"])
        official[row["official_split"]].add(row["subject_id"])
        combinations[row["subject_id"]].add((row["sensor_id"], row["reference_attack_type"]))
    if {key: len(value) for key, value in subjects.items()} != EXPECTED_GROUPS:
        raise ValueError("frozen21/7/7 subject counts required")
    for left in subjects:
        for right in subjects:
            if left != right and subjects[left] & subjects[right]:
                raise ValueError("forbidden cross-role subject overlap")
    if official["train"] & official["test"] or len(official["train"]) != 15 or len(official["test"]) != 20:
        raise ValueError("native official15/20 subject partitions must be disjoint")
    expected = {(sensor, attack) for sensor in ("android", "laptop")
                for attack in ("none", "ipad_video", "iphone_video", "printed_photo")}
    if len(combinations) != 35 or any(value != expected for value in combinations.values()):
        raise ValueError("eight native camera/type combinations per subject required")
    return {"videos": 280, "subjects": 35, "role_videos": EXPECTED_ROLES,
            "role_subjects": EXPECTED_GROUPS, "official_subjects": {"train": 15, "test": 20},
            "forbidden_subject_crossings": 0}


def exact_checks(rows: list[dict], canonical: dict) -> list[dict]:
    findings = []
    for field in ("media_sha256", "decoded_rgb_sequence_sha256"):
        grouped = defaultdict(list)
        for row in rows:
            digest = row[field]
            if digest is not None:
                grouped[digest].append(row)
        for digest, members in grouped.items():
            if len(members) < 2:
                continue
            if any(len({canonical[row["video_id"]][key] for row in members}) != 1
                   for key in ("subject_id", "official_split", "binary_label", "role")):
                raise ValueError("forbidden exact media/decoded-content group crossing")
            findings.append({"kind": field, "sha256": digest, "video_ids": [row["video_id"] for row in members],
                             "within_one_subject_role_partition_class": True})
    return findings


def fixed_indices(videos: list[dict]) -> list[int]:
    strata = {}
    for index, row in enumerate(videos):
        key = (row["role"], row["binary_label"], row["sensor_id"], row["reference_attack_type"])
        strata.setdefault(key, index)
    return sorted(set(strata.values()) | set(range(0, len(videos), 20)))


def measured_usage(group: int) -> dict:
    result = usage(group, OUTPUT / ".unused")
    result["rss_bytes"] = max(result["rss_bytes"], resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
    result["output_bytes"] = sum(retained.tree_bytes(path) for path in (
        retained.ACQUISITION, retained.PILOT, retained.OUTPUT, images.OUTPUT, OUTPUT)) + result["temporary_bytes"]
    return result


def enforce(plan: dict, measured: dict) -> None:
    if time.time() >= plan["deadline_unix_seconds"]:
        raise TimeoutError("four-hour MSU package deadline")
    if measured["rss_bytes"] > CAPS["rss_bytes"]:
        raise MemoryError("4GiB group RSS cap")
    if measured["output_bytes"] > CAPS["output_bytes"] - RESERVE:
        raise OSError("40GiB combined OULU/MSU retained and temporary cap")


def make_plan() -> dict:
    authority = read_json(OUTPUT / "owner_approval.json")
    if authority["explicit_owner_approval"] is not True or authority["selected_answer"] != APPROVAL or authority["caps"] != CAPS:
        raise ValueError("exact combined MSU282 authority required")
    if authority["review281_sha256"] != _sha256(ROOT / "docs/281-review-doc280-oulu-image-preprocessing-complete.md") or authority["active_config_sha256"] != _sha256(images.ACTIVE):
        raise ValueError("approved review/active parameter commitment drift")
    images.check_policy()
    registry = read_json(ROOT / "configs/role_policy_frozen_v2.yaml")
    sources = {}
    bundle = {}
    for name in ("msu_mfsd_canonical.json", "msu_mfsd_metadata.csv", "msu_mfsd_roles.csv"):
        path = FROZEN / name
        expected = registry["frozen_artifact_sha256"][name]
        if _sha256(path) != expected:
            raise ValueError("frozen MSU source-role parent drift")
        sources[str(path)] = expected
        bundle[name] = read_json(path) if name.endswith(".json") else list(csv.DictReader(path.read_text().splitlines()))
    canonical = bundle["msu_mfsd_canonical.json"]
    inventory_path = BASE / "msu_metadata_inventory_v1.json"
    inventory = read_verified_json(inventory_path, canonical["inventory_sha256"])
    sources[str(inventory_path)] = canonical["inventory_sha256"]
    if inventory["videos"] != canonical["videos"]:
        raise ValueError("native inventory/canonical exact equality required")
    videos = canonical["videos"]
    roles = bundle["msu_mfsd_roles.csv"]
    groups = group_checks(videos, roles)
    metadata = {row["video_id"]: row for row in bundle["msu_mfsd_metadata.csv"]}
    if len(metadata) != 280:
        raise ValueError("exact280 metadata records required")
    assigned = {row["video_id"]: row for row in roles}
    prepared = []
    for row in sorted(videos, key=lambda value: value["video_id"]):
        if any(metadata[row["video_id"]][field] != row[field]
               for field in ("dataset", "subject_id", "binary_label", "official_split")):
            raise ValueError("frozen canonical metadata projection drift")
        prepared.append({**row, "role": assigned[row["video_id"]]["role"]})
    archives = {path.name: identity(path) for path in sorted(INPUT.glob("*.zip"))}
    if len(archives) != 8 or sum(value[2] for value in archives.values()) != 11095264656:
        raise ValueError("eight accepted MSU containers and exact byte population required")
    headers_path = BASE / "msu_supplied_headers_20261009_v1.json"
    headers = read_json(headers_path)
    inner_path = BASE / "msu_inner_metadata_20261009_v1.json"
    inner = read_json(inner_path)
    outer_rows = headers["archives"]
    compact = hashlib.sha256(json.dumps(outer_rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if compact != inventory["reader_provenance"]["outer_header_inventory_sha256"]:
        raise ValueError("accepted MSU outer-header commitment drift")
    inner_sha = hashlib.sha256(json.dumps(sorted(inner["headers"], key=lambda row: row["path"]),
                                         sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if inner_sha != inventory["header_inventory_sha256"]:
        raise ValueError("accepted MSU inner-header commitment drift")
    for path in (headers_path, inner_path, ROOT / "scripts/inventory_msu.py",
                 ROOT / "src/fas/msu.py", ROOT / "src/fas/media.py", ROOT / "src/fas/transactions.py",
                 ROOT / "src/fas/lineage.py", ROOT / "src/fas/freeze.py", ROOT / "src/fas/oulu.py", ROOT / "src/fas/visual.py",
                 ROOT / "src/fas/preprocessing.py", ROOT / "src/fas/preprocessing_policy.py",
                 ROOT / "scripts/preprocess_oulu280.py", ROOT / "scripts/preprocess_oulu278.py",
                 ROOT / "scripts/prepare_oulu_pilot243.py", ROOT / "scripts/inspect_oulu_d261.py",
                 ROOT / "scripts/verify_oulu_archive_guard_batch09.py",
                 Path(__file__), ROOT / "tests/test_msu_preprocessing.py",
                 images.ACTIVE, images.LEGACY, ROOT / "configs/experiment_core_v1.yaml",
                 ROOT / "configs/transaction_policy_v1.yaml", ROOT / "configs/role_policy_frozen_v2.yaml",
                 ROOT / "docs/281-review-doc280-oulu-image-preprocessing-complete.md",
                 OUTPUT / "owner_approval.json"):
        sources[str(path)] = _sha256(path)
    tools = {name: subprocess.run([name, "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
             for name in ("ffmpeg", "ffprobe")}
    if tools["ffmpeg"] != read_json(ROOT / "configs/environment_v1.yaml")["host_tools"]["ffmpeg_version_line"]:
        raise ValueError("accepted FFmpeg toolchain required")
    plan = {"checkpoint": 282, "dataset": "MSU-MFSD", "videos": prepared,
            "sources": sources, "archive_identities": archives,
            "outer_headers": outer_rows, "inner_headers": inner["headers"],
            "native_header_sha256": inventory["header_inventory_sha256"],
            "group_checks": groups, "tools": tools, "model_sha256": MODEL_SHA256,
            "active_config_sha256": _sha256(images.ACTIVE),
            "caps": CAPS, "deadline_unix_seconds": authority["deadline_unix_seconds"],
            "visual_indices": fixed_indices(prepared),
            "storage_scope": "total274_276_278_280_282_including_staged_zip_payloads_images_records"}
    archive_guard(plan)
    check_bindings(sources)
    if _sha256(retained.MODEL) != MODEL_SHA256:
        raise ValueError("reused acquired SCRFD weight drift")
    enforce(plan, measured_usage(os.getpgrp()))
    write_immutable_record(OUTPUT / "plan.json", plan)
    print("PLAN282", len(prepared), "videos", flush=True)
    return plan


def checked_copy(source, target, expected_size: int, *, deadline: float) -> dict:
    digest, count = hashlib.sha256(), 0
    while block := source.read(1024 ** 2):
        count += len(block)
        if count > expected_size or time.time() >= deadline:
            raise ValueError("exact payload byte/deadline cap")
        digest.update(block)
        target.write(block)
    if count != expected_size:
        raise ValueError("short payload; no replacement or retry")
    return {"sha256": digest.hexdigest(), "byte_size": count}


def stage_release(plan: dict) -> tuple[Path, dict]:
    archive_guard(plan)
    records, volumes = {}, {}
    for outer_record in plan["outer_headers"]:
        name = outer_record["archive"]
        path = INPUT / name
        initial = identity(path)
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as source:
            if list((os.fstat(source.fileno()).st_dev, os.fstat(source.fileno()).st_ino,
                     os.fstat(source.fileno()).st_size, os.fstat(source.fileno()).st_mtime_ns,
                     os.fstat(source.fileno()).st_ctime_ns)) != initial:
                raise ValueError("stable archive descriptor required")
            digest, count = hashlib.sha256(), 0
            while block := source.read(8 * 1024 ** 2):
                count += len(block)
                if count > initial[2] or time.time() >= plan["deadline_unix_seconds"]:
                    raise TimeoutError("archive hashing deadline/byte cap")
                digest.update(block)
            if count != initial[2] or identity(path) != initial:
                raise ValueError("archive changed during local reproducibility pinning")
            source.seek(0)
            with zipfile.ZipFile(source) as outer:
                entries = outer.infolist()
                if [native.header_record(entry) for entry in entries] != outer_record["headers"]:
                    raise ValueError("accepted outer headers changed")
                for entry in entries:
                    native.safe_entry(entry)
                    if ".zip." in entry.filename:
                        number = int(entry.filename.rsplit(".", 1)[1])
                        if number in volumes:
                            raise ValueError("duplicate native split volume")
                        volumes[number] = (name, entry.filename, entry.file_size)
                    elif entry.filename == "MSU-MFSD/README.txt":
                        if hashlib.sha256(outer.read(entry)).hexdigest() != native.OUTER_README_SHA256:
                            raise ValueError("outer native README changed")
                    elif not entry.is_dir():
                        raise ValueError("unknown outer release entry")
            final = os.fstat(source.fileno())
            if [final.st_dev, final.st_ino, final.st_size, final.st_mtime_ns, final.st_ctime_ns] != initial:
                raise ValueError("archive descriptor changed before pin publication")
        records[name] = {"sha256": digest.hexdigest(), "bytes_read": count,
                         "file_identity": initial, "publisher_hash_verified": False}
        print("ARCHIVE282_PINNED", len(records), "of", len(plan["outer_headers"]), flush=True)
    if set(volumes) != set(range(1, 17)):
        raise ValueError("exact sixteen contiguous native volumes required")
    temporary = OUTPUT / "temporary"
    temporary.mkdir()
    joined = temporary / "MSU-MFSD-Publish.zip"
    volume_rows = []
    with joined.open("xb") as target:
        for number in sorted(volumes):
            name, member, size = volumes[number]
            with zipfile.ZipFile(INPUT / name) as outer, outer.open(member) as source:
                commitment = checked_copy(source, target, size, deadline=plan["deadline_unix_seconds"])
            volume_rows.append({"volume": number, **commitment, "outer_crc_checked_to_eof": True})
            print("VOLUME282_CRC_OK", number, flush=True)
    archive_guard(plan)
    with zipfile.ZipFile(joined) as inner:
        headers = [native.header_record(entry) for entry in inner.infolist()]
        if headers != plan["inner_headers"]:
            raise ValueError("native inner directory drift")
        metadata = {name: inner.read(name) for name in METADATA_SHA256}
        inventory = inventory_headers(headers, metadata, release_id=plan["videos"][0]["release_id"])
        expected = {row["video_id"]: {key: value for key, value in row.items() if key != "role"}
                    for row in plan["videos"]}
        for row in inventory["videos"]:
            if any(expected[row["video_id"]].get(key) != value for key, value in row.items() if key != "role"):
                raise ValueError("current native metadata/canonical join drift")
    result = {"archive_pins": records, "archive_bytes": sum(row["bytes_read"] for row in records.values()),
              "volumes": volume_rows, "joined_zip_bytes": joined.stat().st_size,
              "native_metadata_and_headers_verified": True, "original_archives_modified": False}
    write_immutable_record(OUTPUT / "release_integrity.json", result)
    return joined, result


def infer_image(session, rgb, row: dict) -> None:
    import cv2
    from fas.preprocessing import detect_face, shared_context_crop

    try:
        box, landmarks = detect_face(session, rgb)
        crop, geometry = shared_context_crop(rgb, box[:4], landmarks)
    except ValueError as error:
        if str(error) not in retained.FAILURES:
            raise
        row.update(detector_status="failed", final_k1_action="non_accept", failure=str(error), assets={})
        return
    row.update(detector_status="success", face_box_xyxy=box[:4].tolist(),
               detector_confidence=float(box[4]), landmarks=landmarks.tolist(),
               geometry=geometry, crop_shape=list(crop.shape),
               crop_RGB_sha256=hashlib.sha256(crop.tobytes()).hexdigest(), assets={})
    for name in ("shared", "224", "518"):
        image = crop if name == "shared" else cv2.resize(crop, (int(name), int(name)), interpolation=cv2.INTER_CUBIC)
        relative = f"crops/{row['index']:04d}-{name}.png"
        row["assets"][relative] = write_png(relative, image)


def write_png(relative, rgb) -> dict:
    from fas.visual import png_bytes

    payload = png_bytes(rgb)
    path = OUTPUT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(payload)
    return {"sha256": hashlib.sha256(payload).hexdigest(),
            "RGB_sha256": hashlib.sha256(rgb.tobytes()).hexdigest(), "shape": list(rgb.shape)}


def produce_unit(plan: dict, index: int, original: dict, inner, session) -> tuple[dict, dict]:
    if original["role"] not in EXPECTED_ROLES or original["dataset"] != "MSU-MFSD":
        raise ValueError("frozen MSU source population only")
    entry = inner.getinfo(original["media_relpath"])
    native.safe_entry(entry)
    if native.header_record(entry) != original["archive_header"] or entry.file_size > 128 * 1024 ** 2:
        raise ValueError("canonical video header/byte cap drift")
    write_immutable_record(OUTPUT / "attempts" / f"{index:04d}.json", {
        "index": index, "status": "started", "video_id": original["video_id"], "role": original["role"]})
    path = OUTPUT / "temporary" / ("selected" + Path(original["media_relpath"]).suffix)
    try:
        with inner.open(entry) as source, path.open("xb") as target:
            payload = checked_copy(source, target, entry.file_size, deadline=plan["deadline_unix_seconds"])
        media = {key: original[key] for key in ("video_id", "role", "binary_label", "official_split", "subject_id", "media_relpath")}
        remaining = max(1, min(180, int(plan["deadline_unix_seconds"] - time.time())))
        media.update(media_sha256=payload["sha256"], byte_size=payload["byte_size"],
                     inner_crc_checked_to_eof=True, **probe_video(path, timeout_seconds=remaining))
        media_path = OUTPUT / "media" / f"{index:04d}.json"
        write_immutable_record(media_path, media)
        transaction = technical_transaction(media)
        transaction.update(media_sha256=media["media_sha256"], media_record_sha256=_sha256(media_path))
        row = {**transaction, "index": index, "replacement": False, "model_sha256": MODEL_SHA256,
               "config_sha256": plan["active_config_sha256"], "assets": {}}
        if transaction["selected_frame"] is not None:
            decoded_tokens(media)
            selected = transaction["selected_frame"]
            captured = []

            def consume(order, rgb):
                if order == selected["decode_order"]:
                    if hashlib.sha256(rgb.tobytes()).hexdigest() != selected["rgb_sha256"]:
                        raise ValueError("frozen primary selected RGB changed")
                    captured.append(rgb.copy())

            stream_frames(path, media, consume, timeout=min(180, max(0.001, plan["deadline_unix_seconds"] - time.time())))
            if len(captured) != 1:
                raise ValueError("one frozen middle frame required; no replacement")
            relative = f"frames/{index:04d}.png"
            row["selected_RGB_asset"] = {"path": relative, **write_png(relative, captured[0])}
            infer_image(session, captured[0], row)
        write_immutable_record(OUTPUT / "transactions" / f"{index:04d}.json", row)
        return row, media
    finally:
        if path.exists():
            path.unlink()


def worker(plan: dict) -> None:
    import cv2
    import onnxruntime as ort

    check_bindings(plan["sources"])
    images.check_policy()
    if _sha256(retained.MODEL) != MODEL_SHA256:
        raise ValueError("reused SCRFD weight drift")
    archive_guard(plan)
    joined = OUTPUT / "temporary/MSU-MFSD-Publish.zip"
    try:
        stage_release(plan)
        options = ort.SessionOptions()
        options.intra_op_num_threads = options.inter_op_num_threads = 1
        session = ort.InferenceSession(str(retained.MODEL), sess_options=options, providers=["CPUExecutionProvider"])
        if session.get_providers() != ["CPUExecutionProvider"]:
            raise ValueError("CPU-only inference required")
        cv2.setNumThreads(1)
        media_rows, auxiliary = [], {}
        with zipfile.ZipFile(joined) as inner:
            video_paths = {row["media_relpath"] for row in plan["videos"]}
            for entry in inner.infolist():
                native.safe_entry(entry)
                if entry.is_dir() or entry.filename in video_paths:
                    continue
                digest, count = hashlib.sha256(), 0
                with inner.open(entry) as source:
                    while block := source.read(1024 ** 2):
                        count += len(block)
                        if count > entry.file_size or time.time() >= plan["deadline_unix_seconds"]:
                            raise TimeoutError("ancillary CRC/byte deadline")
                        digest.update(block)
                if count != entry.file_size:
                    raise ValueError("short native auxiliary entry")
                auxiliary[entry.filename] = {"sha256": digest.hexdigest(), "byte_size": count, "crc_checked_to_eof": True}
            for index, original in enumerate(plan["videos"]):
                archive_guard(plan)
                row, media = produce_unit(plan, index, original, inner, session)
                media_rows.append(media)
                print("MSU282", index, row["role"], row["detector_status"], flush=True)
        exact = exact_checks(media_rows, {row["video_id"]: row for row in plan["videos"]})
        write_immutable_record(OUTPUT / "content_checks.json", {
            "exact_groups": exact, "forbidden_exact_crossings": 0,
            "near_duplicate_independence_certified": False,
            "known_parent_evidence": "native_same_subject_attack_construction_preserved_not_independent_capture_claim",
            "joined_cross_dataset_ancestry_certified": False})
        archive_guard(plan)
        check_bindings(plan["sources"])
        write_immutable_record(OUTPUT / "worker_completion.json", {
            "transactions": len(media_rows), "media_crc_checked": len(media_rows),
            "native_frames": sum(row["frame_count"] for row in media_rows),
            "selected_payload_bytes": sum(row["byte_size"] for row in media_rows),
            "ancillary_entries": auxiliary, "provider": ["CPUExecutionProvider"],
            "gpu_seconds": 0, "model_scores": 0, "fitted_scores": 0})
    finally:
        if joined.exists():
            joined.unlink()


def validate_manifest(plan: dict, rows: list[dict]) -> dict:
    canonical = {row["video_id"]: row for row in plan["videos"]}
    ids = [row["video_id"] for row in rows]
    if len(ids) != 280 or len(set(ids)) != 280 or set(ids) != set(canonical):
        raise ValueError("exact280 unique MSU original manifest IDs required")
    counts, selected, terminal = Counter(), 0, 0
    for row in rows:
        original = canonical[row["video_id"]]
        if any(row[key] != original[key] for key in ("role", "binary_label", "subject_id", "official_split")):
            raise ValueError("manifest role/class/subject/partition parent drift")
        if row["active_config_sha256"] != plan["active_config_sha256"] or row["model_score"] is not None or row["classifier_error"] is not None or row["replacement"] is not False or row["retain_original_denominator"] is not True:
            raise ValueError("scoreless fixed-config denominator-preserving manifest required")
        counts[row["detector_status"]] += 1
        if row["selected_frame"] is None:
            terminal += 1
            if row["detector_status"] != "not_run" or row["final_k1_action"] != "non_accept" or row.get("asset_sha256"):
                raise ValueError("pre-detector technical failure cannot acquire pixels/outcomes")
        else:
            selected += 1
            if row["detector_status"] not in {"success", "failed"}:
                raise ValueError("explicit detector outcome required")
            if row["detector_status"] == "failed" and row["final_k1_action"] != "non_accept":
                raise ValueError("failed detection must remain non_accept")
    return {"originals": len(rows), "selected": selected, "pre_detector_failure": terminal,
            "detector_success": counts["success"], "detector_failure": counts["failed"]}


def make_sheets(plan: dict, rows: list[dict]) -> list[dict]:
    import cv2
    import numpy as np

    sheets = []
    selected = {row["index"]: row for row in rows if row["selected_frame"] is not None}
    failures = [row["index"] for row in rows if row["selected_frame"] is not None and row["detector_status"] == "failed"]
    for kind, indices in (("fixed", plan["visual_indices"]), ("failures", failures)):
        for page, offset in enumerate(range(0, len(indices), 32)):
            subset = indices[offset:offset + 32]
            sheet = np.full((((len(subset) + 3) // 4) * 180, 640, 3), 255, np.uint8)
            for slot, index in enumerate(subset):
                top, left = slot // 4 * 180, slot % 4 * 160
                cv2.putText(sheet, f"{index:04d}", (left + 3, top + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
                if index not in selected:
                    cv2.putText(sheet, "DECODE FAILURE", (left + 3, top + 90),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
                    continue
                relative = f"crops/{index:04d}-224.png" if selected[index]["detector_status"] == "success" else f"frames/{index:04d}.png"
                bgr = cv2.imread(str(OUTPUT / relative), cv2.IMREAD_COLOR)
                if bgr is None:
                    raise ValueError("actual visual source missing")
                rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                sheet[top + 20:top + 180, left:left + 160] = cv2.resize(rgb, (160, 160), interpolation=cv2.INTER_CUBIC)
            relative = f"visual/{kind}-{page:02d}.png"
            commitment = write_png(relative, sheet)
            restored = cv2.imread(str(OUTPUT / relative), cv2.IMREAD_COLOR)
            if restored is None or not np.array_equal(cv2.cvtColor(restored, cv2.COLOR_BGR2RGB), sheet):
                raise ValueError("visual-sheet PNG reconstruction drift")
            sheets.append({"path": relative, "kind": kind, "indices": subset, **commitment})
    return sheets


def verify(plan: dict) -> dict:
    check_bindings(plan["sources"])
    archive_guard(plan)
    images.check_policy()
    if _sha256(retained.MODEL) != MODEL_SHA256:
        raise ValueError("final acquired detector hash drift")
    expected = {f"{index:04d}.json" for index in range(len(plan["videos"]))}
    for folder in ("transactions", "media", "attempts"):
        if {path.name for path in (OUTPUT / folder).iterdir()} != expected:
            raise ValueError("exact280 per-unit record set required")
    manifest, assets, media_rows, records = [], {}, [], {}
    for index, original in enumerate(plan["videos"]):
        row_path = OUTPUT / "transactions" / f"{index:04d}.json"
        row = read_verified_json(row_path, _sha256(row_path))
        media_path = OUTPUT / "media" / f"{index:04d}.json"
        media = read_verified_json(media_path, row["media_record_sha256"])
        if any(media[key] != original[key] for key in ("video_id", "role", "binary_label", "official_split", "subject_id", "media_relpath")):
            raise ValueError("native/frozen media parent drift")
        if media["byte_size"] != original["byte_size"] or media["inner_crc_checked_to_eof"] is not True:
            raise ValueError("native media bytes/CRC evidence required")
        transaction = technical_transaction(media)
        transaction.update(media_sha256=media["media_sha256"], media_record_sha256=_sha256(media_path))
        if any(row[key] != value for key, value in transaction.items()
               if key not in {"detector_status", "final_k1_action"}):
            raise ValueError("actual primary-selector/technical transaction drift")
        if row["index"] != index or row["config_sha256"] != plan["active_config_sha256"] or row["model_sha256"] != MODEL_SHA256:
            raise ValueError("per-unit index/active config/model drift")
        if transaction["selected_frame"] is None:
            if row["detector_status"] != "not_run" or row["final_k1_action"] != "non_accept" or row["assets"] or "selected_RGB_asset" in row:
                raise ValueError("terminal decode failure must not fabricate image/detection")
            entry = {**transaction, "asset_sha256": {}, "record_path": str(row_path), "record_sha256": _sha256(row_path)}
        else:
            entry, unit_assets = images.validate_unit(
                {"transaction": transaction, "media_path": str(media_path)},
                OUTPUT, index, 4, plan["active_config_sha256"], _sha256(row_path))
            assets.update(unit_assets)
        entry.update(index=index, subject_id=original["subject_id"], official_split=original["official_split"],
                     active_config_sha256=plan["active_config_sha256"],
                     replacement=False, retain_original_denominator=True, model_score=None, classifier_error=None)
        manifest.append(entry)
        media_rows.append(media)
        for path in (row_path, media_path, OUTPUT / "attempts" / f"{index:04d}.json"):
            records[path.relative_to(OUTPUT).as_posix()] = _sha256(path)
        if index % 20 == 0:
            print("READBACK282", index, flush=True)
    observed_assets = {path.relative_to(OUTPUT).as_posix() for folder in ("frames", "crops") for path in (OUTPUT / folder).glob("*")}
    if observed_assets != set(assets):
        raise ValueError("unexpected or missing MSU image assets")
    counts = validate_manifest(plan, manifest)
    findings = exact_checks(media_rows, {row["video_id"]: row for row in plan["videos"]})
    content = read_json(OUTPUT / "content_checks.json")
    if content["exact_groups"] != findings or content["forbidden_exact_crossings"] != 0:
        raise ValueError("exact-content accounting drift")
    completion = read_json(OUTPUT / "worker_completion.json")
    required = {"transactions": len(manifest), "media_crc_checked": len(manifest),
                "native_frames": sum(row["frame_count"] for row in media_rows),
                "selected_payload_bytes": sum(row["byte_size"] for row in media_rows),
                "provider": ["CPUExecutionProvider"], "gpu_seconds": 0, "model_scores": 0, "fitted_scores": 0}
    if any(type(completion.get(key)) is not type(value) or completion[key] != value for key, value in required.items()):
        raise ValueError("worker completion/CRC/frame accounting mismatch")
    integrity = read_json(OUTPUT / "release_integrity.json")
    if set(integrity["archive_pins"]) != set(plan["archive_identities"]) or integrity["archive_bytes"] != sum(value[2] for value in plan["archive_identities"].values()):
        raise ValueError("release archive pin population drift")
    if len(integrity["volumes"]) != 16 or sum(row["byte_size"] for row in integrity["volumes"]) != integrity["joined_zip_bytes"]:
        raise ValueError("native volume assembly accounting drift")
    for name, pin in integrity["archive_pins"].items():
        if pin["file_identity"] != plan["archive_identities"][name] or pin["bytes_read"] != pin["file_identity"][2]:
            raise ValueError("archive pin exact identity/size drift")
    if {row["volume"] for row in integrity["volumes"]} != set(range(1, 17)) or any(row["outer_crc_checked_to_eof"] is not True for row in integrity["volumes"]):
        raise ValueError("exact sixteen CRC-checked volume identities required")
    auxiliary_headers = {row["path"]: row for row in plan["inner_headers"]
                         if not row["path"].endswith("/") and row["path"] not in {video["media_relpath"] for video in plan["videos"]}}
    if set(completion["ancillary_entries"]) != set(auxiliary_headers):
        raise ValueError("exact native ancillary CRC accounting required")
    for name, row in completion["ancillary_entries"].items():
        if row["byte_size"] != auxiliary_headers[name]["size"] or row["crc_checked_to_eof"] is not True:
            raise ValueError("native ancillary byte/CRC evidence drift")
    if any((OUTPUT / "temporary").iterdir()):
        raise ValueError("owned temporary ZIP/media must be removed before acceptance")
    sheets = make_sheets(plan, manifest)
    write_immutable_record(OUTPUT / "full_manifest.json", {
        "dataset": "MSU-MFSD", "rows": manifest, **counts,
        "active_config_sha256": plan["active_config_sha256"], "scientific_readiness": False})
    validate_manifest(plan, read_json(OUTPUT / "full_manifest.json")["rows"])
    check_bindings(plan["sources"])
    archive_guard(plan)
    result = {**required, **counts, "role_originals": dict(Counter(row["role"] for row in manifest)),
              "full_manifest_sha256": _sha256(OUTPUT / "full_manifest.json"),
              "release_integrity_sha256": _sha256(OUTPUT / "release_integrity.json"),
              "content_checks_sha256": _sha256(OUTPUT / "content_checks.json"),
              "per_unit_sha256": records, "asset_sha256": assets,
              "visual_sheets": sheets, "visual_inspection_completed": False,
              "exact_duplicate_groups": len(findings), "forbidden_exact_crossings": 0,
              "scientific_readiness": False}
    write_immutable_record(OUTPUT / "readback.json", result)
    return result


def failure_rows(plan: dict, failure: str) -> None:
    rows = []
    for index, video in enumerate(plan["videos"]):
        path = OUTPUT / "transactions" / f"{index:04d}.json"
        rows.append({"index": index, "video_id": video["video_id"], "role": video["role"],
                     "binary_label": video["binary_label"], "retain_original_denominator": True,
                     "detector_status": "unverified_after_attempt_failure", "final_k1_action": "non_accept",
                     "record_sha256": _sha256(path) if path.is_file() else None, "failure": failure})
    write_immutable_record(OUTPUT / "failure_rows.json", {"rows": rows, "automatic_retry": False})


def supervise(plan: dict) -> dict:
    write_immutable_record(OUTPUT / "attempt_lock.json", {
        "plan_sha256": _sha256(OUTPUT / "plan.json"), "parent_pid": os.getpid(),
        "attempts_authorized": 1, "automatic_retry": False})
    process, failure, readback = None, None, None
    peak = {"rss_bytes": 0, "output_bytes": 0, "temporary_bytes": 0}
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
        counts = validate_manifest(plan, manifest["rows"])
        if any(readback[key] != value for key, value in counts.items()):
            raise ValueError("final manifest/readback count mismatch")
        for relative, digest in readback["per_unit_sha256"].items():
            if _sha256(OUTPUT / relative) != digest:
                raise ValueError("final per-unit source/record drift")
        for name in ("release_integrity", "content_checks"):
            read_verified_json(OUTPUT / (name + ".json"), readback[name + "_sha256"])
        if manifest["active_config_sha256"] != _sha256(images.ACTIVE):
            raise ValueError("final active policy pin drift")
        check_bindings(plan["sources"])
        archive_guard(plan)
        final = measured_usage(os.getpgrp())
        final["rss_bytes"] = max(final["rss_bytes"], resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024)
        peak = {key: max(peak[key], final[key]) for key in peak}
        enforce(plan, peak)
    except Exception as error:
        failure = type(error).__name__ + ": " + str(error)
        print("MSU282 FAILED", failure, file=sys.stderr, flush=True)
    finally:
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
        for name in ("MSU-MFSD-Publish.zip", "selected.mp4", "selected.mov"):
            path = OUTPUT / "temporary" / name
            if path.exists():
                path.unlink()
    if failure:
        failure_rows(plan, failure)
    result = {"checkpoint": 282, "completion_claimed": failure is None and readback is not None,
              "failure": failure, "caps": CAPS, "sampled_peaks": peak,
              "package_wall_seconds": time.time() - read_json(OUTPUT / "owner_approval.json")["started_unix_seconds"],
              "supervised_wall_seconds": time.monotonic() - started,
              "readback_sha256": _sha256(OUTPUT / "readback.json") if readback else None,
              "attempts": 1, "automatic_retry": False, "gpu_seconds": 0,
              "visual_inspection_pending": failure is None, "scientific_readiness": False}
    write_immutable_record(OUTPUT / "resources.json", result)
    if read_json(OUTPUT / "resources.json") != result:
        raise RuntimeError("terminal resources readback mismatch")
    print("MSU282_TERMINAL", json.dumps(result), flush=True)
    return result


def publish_summary(result: dict) -> None:
    complete = result["completion_claimed"] is True
    readback = read_json(OUTPUT / "readback.json") if complete else None
    summary = {
        "checkpoint": 282, "dataset": "MSU-MFSD",
        "status": "software_complete_visual_review_pending" if complete else "concrete_defect_stopped_no_retry",
        "completion_claimed": complete, "visual_inspection_completed": False,
        "failure_category": result["failure"].split(":", 1)[0] if result.get("failure") else None,
        "caps": CAPS, "sampled_peaks": result.get("sampled_peaks"),
        "package_wall_seconds": result.get("package_wall_seconds"),
        "originals": 280, "subjects": 35, "role_originals": EXPECTED_ROLES, "role_subjects": EXPECTED_GROUPS,
        **{key: readback[key] if readback else None for key in (
            "selected", "pre_detector_failure", "detector_success", "detector_failure",
            "native_frames", "selected_payload_bytes", "exact_duplicate_groups", "forbidden_exact_crossings")},
        "active_config_sha256": _sha256(images.ACTIVE),
        "model_scores": 0, "fitted_scores": 0, "target_access": False,
        "near_duplicate_independence_certified": False, "joined_domain_assurance": False,
        "audit_summary_statuses_changed": False, "scientific_readiness": False,
        "original_archive_bytes": 11095264656, "expected_joined_zip_bytes": 11092803150,
        "model_downloads": 0, "automatic_retry": False, "gpu_seconds": 0,
        "private_record_sha256": {
            path.relative_to(OUTPUT).as_posix(): _sha256(path)
            for path in (OUTPUT / "owner_approval.json", OUTPUT / "supervisor.json",
                         OUTPUT / "plan.json", OUTPUT / "attempt_lock.json",
                         OUTPUT / "release_integrity.json", OUTPUT / "content_checks.json",
                         OUTPUT / "worker_completion.json", OUTPUT / "full_manifest.json",
                         OUTPUT / "readback.json", OUTPUT / "resources.json", OUTPUT / "package_failure.json")
            if path.exists()}}
    write_immutable_record(ROOT / "results/phase1/msu-preprocessing282-v1.json", summary)


def status() -> dict:
    authority = read_json(OUTPUT / "owner_approval.json")
    return {"checkpoint": 282, "records_written": len(list((OUTPUT / "transactions").glob("*.json"))),
            "expected_originals": 280, "deadline_unix_seconds": authority["deadline_unix_seconds"],
            "plan_committed": (OUTPUT / "plan.json").exists(),
            "release_staged": (OUTPUT / "release_integrity.json").exists(),
            "worker_completed": (OUTPUT / "worker_completion.json").exists(),
            "terminal": read_json(OUTPUT / "resources.json") if (OUTPUT / "resources.json").exists() else None,
            "package_failure": read_json(OUTPUT / "package_failure.json") if (OUTPUT / "package_failure.json").exists() else None}


def child_plan() -> dict:
    plan = read_json(OUTPUT / "plan.json")
    lease = read_json(OUTPUT / "attempt_lock.json")
    if lease["parent_pid"] != os.getppid() or lease["plan_sha256"] != _sha256(OUTPUT / "plan.json") or os.getsid(0) != os.getpid():
        raise ValueError("single supervised parent/plan lease required")
    retained.arm_deadline(plan["deadline_unix_seconds"])
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    for name in ("run-approved", "worker", "verify", "status"):
        mode.add_argument("--" + name, action="store_true")
    args = parser.parse_args()
    if args.status:
        print(json.dumps(status(), indent=2))
        return 0
    if args.worker or args.verify:
        plan = child_plan()
        worker(plan) if args.worker else verify(plan)
        return 0
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise FileExistsError("one MSU package only; no automatic retry")
    images.check_policy()
    started = time.time()
    write_immutable_record(OUTPUT / "owner_approval.json", {
        "checkpoint": 282, "explicit_owner_approval": True, "selected_answer": APPROVAL, "caps": CAPS,
        "started_unix_seconds": started, "deadline_unix_seconds": started + CAPS["wall_seconds"],
        "review281_sha256": _sha256(ROOT / "docs/281-review-doc280-oulu-image-preprocessing-complete.md"),
        "active_config_sha256": _sha256(images.ACTIVE), "scope": "one_combined_MSU_source_image_package_no_scores_fits_target_work",
        "original_archive_bytes": 11095264656, "temporary_joined_zip_bytes": 11092803150,
        "media_bytes": 11099241100, "frame_count_before_execution": None,
        "temporary_cleanup_authorized": True, "automatic_retry": False, "model_download": False})
    with (OUTPUT / "execution.log").open("xb", buffering=0) as log:
        os.dup2(log.fileno(), 1)
        os.dup2(log.fileno(), 2)
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    write_immutable_record(OUTPUT / "supervisor.json", {
        "pid": os.getpid(), "started_unix_seconds": started,
        "runner_sha256": _sha256(Path(__file__)), "automatic_retry": False})
    print("MSU282_START", os.getpid(), started, flush=True)
    retained.arm_deadline(started + CAPS["wall_seconds"])
    try:
        plan = make_plan()
        result = supervise(plan)
        publish_summary(result)
        return 0 if result["completion_claimed"] else 1
    except Exception as error:
        write_immutable_record(OUTPUT / "package_failure.json", {
            "error_type": type(error).__name__, "message": str(error),
            "automatic_retry": False, "scientific_readiness": False})
        if not (ROOT / "results/phase1/msu-preprocessing282-v1.json").exists():
            publish_summary({"completion_claimed": False, "failure": type(error).__name__ + ": " + str(error)})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
