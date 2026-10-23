"""One bounded owner-approved CASIA release, primary-image and local-audit package."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import stat
import subprocess
import sys
import time
import zlib

import preprocess_msu282 as shared
import recover_msu282 as msu_recovery
from fas.casia import inventory_headers, parse_media_path, verify_bob_sources
from fas.lineage import decoded_tokens
from fas.rar5 import read_file_headers
from msu_replay282 import strict_replay

ROOT = shared.ROOT
BASE = shared.BASE
OUTPUT = BASE / "casia_preprocessing285_v1"
ARCHIVE = Path("/mnt/e/FAS-private/data/downloads/casia-fasd/CASIA_faceAntisp.rar")
EXTRACTOR = Path("/home/lathevinh/miniforge3/bin/bsdtar")
REFERENCE = Path("/mnt/e/FAS-private/reference-sources/bob.db.casia_fasd/5320dac3101de913874242f56c5baa5961d2c13b")
FROZEN = shared.FROZEN
CAPS = {"wall_seconds": 14400, "rss_bytes": 4 * 1024 ** 3,
        "output_bytes": 32 * 1024 ** 3, "gpu_seconds": 0}
ROLES = {"train": 360, "branch_calibration": 120, "g_domain": 120}
GROUPS = {"train": 30, "branch_calibration": 10, "g_domain": 10}
APPROVAL_CLOCK_START = 1792714975.0
APPROVAL = (
    "Đồng ý trọn gói CASIA600: code/tests + release/role/integrity + "
    "decode/frame/preprocess + manifest/readback/visual/audit và push; "
    "CPU-only 4 giờ/4 GiB RSS/32 GiB tổng private; không retry/nới cap"
)


def read(path):
    return shared.read_json(path)


def write(path, value):
    shared.write_immutable_record(path, value)


def sha(path):
    return shared._sha256(path)


def guard(plan):
    if shared.identity(ARCHIVE) != plan["archive_identity"]:
        raise ValueError("CASIA archive identity drift; no automatic recovery")
    if shared.identity(EXTRACTOR) != plan["extractor_identity"]:
        raise ValueError("pinned extractor identity drift")


def measured(group):
    result = shared.usage(group, OUTPUT / ".unused")
    result["rss_bytes"] = max(result["rss_bytes"], resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
    roots = (shared.retained.ACQUISITION, shared.retained.PILOT, shared.retained.OUTPUT,
             shared.images.OUTPUT, shared.OUTPUT, msu_recovery.OUTPUT, OUTPUT)
    result["output_bytes"] = sum(shared.retained.tree_bytes(path) for path in roots) + result["temporary_bytes"]
    return result


def enforce(plan, value):
    if time.time() >= plan["deadline_unix_seconds"]:
        raise TimeoutError("four-hour CASIA package deadline")
    if value["rss_bytes"] > CAPS["rss_bytes"]:
        raise MemoryError("4GiB combined group RSS cap")
    if value["output_bytes"] > CAPS["output_bytes"] - shared.RESERVE:
        raise OSError("32GiB historical/new/temporary private-output cap")


def group_checks(videos, roles):
    canonical = {row["video_id"]: row for row in videos}
    assigned = {row["video_id"]: row for row in roles}
    if len(videos) != 600 or len(canonical) != 600 or len(roles) != 600 or len(assigned) != 600 or set(canonical) != set(assigned):
        raise ValueError("exact600 canonical/frozen-role IDs required")
    if Counter(row["role"] for row in roles) != ROLES:
        raise ValueError("exact360/120/120 frozen roles required")
    groups, official, combinations = defaultdict(set), defaultdict(set), defaultdict(set)
    for identity, row in canonical.items():
        role = assigned[identity]
        if row["dataset"] != "CASIA-FASD" or any(row[key] != role[key] for key in ("dataset", "subject_id", "binary_label")):
            raise ValueError("frozen CASIA identity/class/subject join drift")
        native = parse_media_path(row["media_relpath"])
        if any(row[key] != value for key, value in native.items()):
            raise ValueError("pinned reference path/label/subject mapping drift")
        if row["group_id"] != row["subject_id"] or row["group_unit"] != "subject":
            raise ValueError("native subject grouping required")
        groups[role["role"]].add(row["subject_id"])
        official[row["official_split"]].add(row["subject_id"])
        combinations[row["subject_id"]].add(row["raw_label_token"])
    if {role: len(value) for role, value in groups.items()} != GROUPS:
        raise ValueError("exact30/10/10 frozen subject groups required")
    if len(official["train"]) != 20 or len(official["test"]) != 30 or official["train"] & official["test"]:
        raise ValueError("reference20/30 official subject partitions must be disjoint")
    for left in groups:
        for right in groups:
            if left != right and groups[left] & groups[right]:
                raise ValueError("forbidden cross-role subject overlap")
    from fas.casia import REFERENCE_CODES
    if len(combinations) != 50 or any(value != set(REFERENCE_CODES) for value in combinations.values()):
        raise ValueError("twelve reference codes per subject required")
    return {"videos": 600, "subjects": 50, "role_videos": ROLES, "role_subjects": GROUPS,
            "official_subjects": {"train": 20, "test": 30}, "forbidden_subject_crossings": 0}


def typed_headers(text):
    headers, seen = [], set()
    for line in text.splitlines():
        values = line.split()
        if len(values) != 9 or values[0][0] not in {"-", "d"} or not values[4].isdigit():
            raise ValueError("unsupported typed RAR listing")
        relative = values[-1].rstrip("/")
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts or path.as_posix() != relative or "\\" in relative or relative in seen:
            raise ValueError("unsafe/duplicate RAR header")
        seen.add(relative)
        headers.append({"relpath": relative, "byte_size": int(values[4]),
                        "kind": "directory" if values[0][0] == "d" else "file", "encrypted": False})
    if not headers:
        raise ValueError("missing RAR headers")
    return headers


def list_headers():
    result = subprocess.run([str(EXTRACTOR), "-tvf", str(ARCHIVE)], stdin=subprocess.DEVNULL,
                            capture_output=True, text=True, timeout=60, check=False,
                            env={**os.environ, "LC_ALL": "C"})
    if result.returncode or result.stderr.strip():
        raise ValueError("RAR header utility failed: " + result.stderr.strip())
    return typed_headers(result.stdout)


def reconcile_headers(headers, videos):
    first = videos[0]
    inventory = inventory_headers(headers, release_id=first["release_id"], protocol_id=first["protocol_id"],
                                  archive_name=ARCHIVE.name, require_full_reference=True)
    projected = [{key: value for key, value in row.items() if key not in {"group_id", "group_unit", "role"}} for row in videos]
    if inventory["videos"] != projected:
        raise ValueError("exact reference inventory/header/canonical fields differ")
    return inventory


def fixed_indices(videos):
    strata = {}
    for index, row in enumerate(videos):
        strata.setdefault((row["role"], row["binary_label"], row["quality"], row["reference_attack_type"]), index)
    return sorted(set(strata.values()) | set(range(0, len(videos), 20)))


def authority():
    row = read(OUTPUT / "owner_approval.json")
    if row["selected_answer"] != APPROVAL or row["explicit_owner_approval"] is not True or row["caps"] != CAPS:
        raise ValueError("exact combined CASIA authority required")
    if row["review284_sha256"] != sha(ROOT / "docs/284-review-msu282-local-audit-and-image-completion.md"):
        raise ValueError("approved review284 drift")
    if row["started_unix_seconds"] != APPROVAL_CLOCK_START or row["deadline_unix_seconds"] != APPROVAL_CLOCK_START + CAPS["wall_seconds"]:
        raise ValueError("combined approval clock must not be reset at launch")
    return row


def make_plan():
    approval = authority()
    shared.images.check_policy()
    registry = read(ROOT / "configs/role_policy_frozen_v2.yaml")
    sources, bundle = {}, {}
    for name in ("casia_fasd_canonical.json", "casia_fasd_metadata.csv", "casia_fasd_roles.csv"):
        path = FROZEN / name
        expected = registry["frozen_artifact_sha256"][name]
        if sha(path) != expected:
            raise ValueError("permanent CASIA source artifact drift")
        sources[str(path)] = expected
        bundle[name] = read(path) if name.endswith(".json") else list(csv.DictReader(path.read_text().splitlines()))
    canonical = bundle["casia_fasd_canonical.json"]
    inventory_path = BASE / "casia-inventory-20261006.json"
    inventory = shared.read_verified_json(inventory_path, canonical["inventory_sha256"])
    if inventory["videos"] != [{key: value for key, value in row.items() if key not in {"group_id", "group_unit", "role"}}
                               for row in canonical["videos"]]:
        raise ValueError("accepted reference inventory/canonical projection drift")
    sources[str(inventory_path)] = canonical["inventory_sha256"]
    groups = group_checks(canonical["videos"], bundle["casia_fasd_roles.csv"])
    roles = {row["video_id"]: row["role"] for row in bundle["casia_fasd_roles.csv"]}
    metadata = {row["video_id"]: row for row in bundle["casia_fasd_metadata.csv"]}
    videos = sorted(({**row, "role": roles[row["video_id"]]} for row in canonical["videos"]), key=lambda row: row["video_id"])
    if len(metadata) != 600 or set(metadata) != set(roles):
        raise ValueError("exact600 frozen metadata IDs required")
    for row in videos:
        if any(metadata[row["video_id"]][key] != row[key] for key in ("dataset", "subject_id", "binary_label", "official_split")):
            raise ValueError("frozen metadata label/subject/partition drift")
    headers = list_headers()
    reconcile_headers(headers, videos)
    crc_headers = read_file_headers(ARCHIVE)
    if [{key: row[key] for key in ("relpath", "byte_size", "kind", "encrypted")} for row in crc_headers] != headers:
        raise ValueError("independent RAR5 CRC headers differ from extractor listing")
    references = verify_bob_sources(REFERENCE)
    for name, expected in references.items():
        sources[str(REFERENCE / Path(name).name)] = expected
    for path in (
        Path(__file__), ROOT / "tests/test_casia_preprocessing.py", ROOT / "src/fas/casia.py",
        ROOT / "src/fas/media.py", ROOT / "src/fas/lineage.py", ROOT / "src/fas/transactions.py", ROOT / "src/fas/rar5.py",
        ROOT / "src/fas/preprocessing.py", ROOT / "src/fas/preprocessing_policy.py",
        ROOT / "src/fas/visual.py", ROOT / "src/fas/freeze.py", ROOT / "src/fas/oulu.py",
        ROOT / "scripts/msu_replay282.py", ROOT / "scripts/preprocess_msu282.py",
        ROOT / "scripts/recover_msu282.py", ROOT / "scripts/diagnose_msu282_recovery.py",
        ROOT / "scripts/preprocess_oulu280.py", ROOT / "scripts/preprocess_oulu278.py",
        ROOT / "scripts/prepare_oulu_pilot243.py", ROOT / "scripts/inspect_oulu_d261.py",
        ROOT / "scripts/verify_oulu_archive_guard_batch09.py", EXTRACTOR,
        shared.images.ACTIVE, shared.images.LEGACY, ROOT / "configs/environment_v1.yaml",
        ROOT / "configs/experiment_core_v1.yaml", ROOT / "configs/transaction_policy_v1.yaml",
        ROOT / "configs/role_policy_frozen_v2.yaml", OUTPUT / "owner_approval.json",
        ROOT / "docs/284-review-msu282-local-audit-and-image-completion.md",
    ):
        sources[str(path)] = sha(path)
    toolchain = {name: subprocess.run([name, "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
                 for name in ("ffmpeg", "ffprobe")}
    if toolchain["ffmpeg"] != read(ROOT / "configs/environment_v1.yaml")["host_tools"]["ffmpeg_version_line"]:
        raise ValueError("accepted FFmpeg toolchain required")
    extractor_version = subprocess.run([str(EXTRACTOR), "--version"], capture_output=True, text=True, check=True).stdout.strip()
    plan = {
        "checkpoint": 285, "dataset": "CASIA-FASD", "videos": videos, "sources": sources,
        "archive_identity": shared.identity(ARCHIVE), "extractor_identity": shared.identity(EXTRACTOR),
        "headers": headers, "crc_headers": crc_headers, "group_checks": groups, "bob_source_sha256": references,
        "extractor_version": extractor_version, "toolchain": toolchain,
        "active_config_sha256": sha(shared.images.ACTIVE), "model_sha256": shared.MODEL_SHA256,
        "caps": CAPS, "deadline_unix_seconds": approval["deadline_unix_seconds"],
        "visual_indices": fixed_indices(videos),
        "storage_scope": "all274_276_278_280_failed282_recovery282_285_including_model_and_temporary"}
    if plan["archive_identity"][2] != 876296302 or sum(row["byte_size"] for row in videos) != 866586586:
        raise ValueError("approved exact archive/video byte population required")
    if sha(shared.retained.MODEL) != shared.MODEL_SHA256:
        raise ValueError("accepted reused model drift")
    guard(plan)
    shared.check_bindings(sources)
    enforce(plan, measured(os.getpgrp()))
    write(OUTPUT / "plan.json", plan)
    print("PLAN285", len(videos), "originals", len(plan["visual_indices"]), "fixed visual tiles", flush=True)
    return plan


def cleanup():
    temporary = OUTPUT / "temporary"
    if not temporary.exists():
        return
    expected = {"test_release", "train_release"}
    if {path.name for path in temporary.iterdir()} - expected:
        raise ValueError("refuse cleanup of unexpected temporary root")
    for name in sorted(expected):
        target = temporary / name
        if target.is_symlink():
            raise ValueError("refuse cleanup through temporary symlink")
        if target.exists():
            shutil.rmtree(target)


def stage_release(plan):
    guard(plan)
    descriptor = os.open(ARCHIVE, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as source:
        before = os.fstat(source.fileno())
        if [before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns] != plan["archive_identity"]:
            raise ValueError("stable original archive descriptor required")
        digest, count = hashlib.sha256(), 0
        while block := source.read(8 * 1024 ** 2):
            count += len(block)
            if count > before.st_size or time.time() >= plan["deadline_unix_seconds"]:
                raise TimeoutError("archive hashing byte/deadline cap")
            digest.update(block)
        after = os.fstat(source.fileno())
        if count != before.st_size or [after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns] != plan["archive_identity"]:
            raise ValueError("archive mutated during local baseline hashing")
    guard(plan)
    archive_digest = digest.hexdigest()
    if list_headers() != plan["headers"]:
        raise ValueError("typed RAR header inventory drift")
    if read_file_headers(ARCHIVE) != plan["crc_headers"]:
        raise ValueError("RAR5 header CRC/unpacked checksum commitment drift")
    print("ARCHIVE285_PINNED", count, flush=True)
    temporary = OUTPUT / "temporary"
    temporary.mkdir()
    errors = OUTPUT / "extraction.stderr"
    with errors.open("xb") as handle:
        result = subprocess.run(
            [str(EXTRACTOR), "-xf", str(ARCHIVE), "-C", str(temporary),
             "--no-same-owner", "--no-same-permissions", "--keep-old-files"],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=handle,
            timeout=max(0.001, plan["deadline_unix_seconds"] - time.time()), check=False)
    if result.returncode or errors.stat().st_size:
        raise ValueError(f"strict RAR extraction/CRC failed: exit={result.returncode}; retained stderr")
    expected = {row["media_relpath"]: row["byte_size"] for row in plan["videos"]}
    crc_headers = {row["relpath"]: row for row in plan["crc_headers"] if row["kind"] == "file"}
    seen = set()
    payload_pins = {}
    for path in temporary.rglob("*"):
        value = path.lstat()
        relative = path.relative_to(temporary).as_posix()
        if stat.S_ISDIR(value.st_mode):
            if not any(row["relpath"] == relative and row["kind"] == "directory" for row in plan["headers"]):
                raise ValueError("unexpected extracted directory")
        elif not stat.S_ISREG(value.st_mode) or relative not in expected or value.st_size != expected[relative]:
            raise ValueError("unexpected/nonregular/wrong-size extracted member")
        else:
            crc, digest = 0, hashlib.sha256()
            with path.open("rb") as source:
                while block := source.read(1024 ** 2):
                    if time.time() >= plan["deadline_unix_seconds"]:
                        raise TimeoutError("extracted media CRC deadline")
                    crc = zlib.crc32(block, crc)
                    digest.update(block)
            if crc != crc_headers[relative]["crc32"]:
                raise ValueError("extracted video differs from RAR5 unpacked CRC32")
            payload_pins[relative] = {"crc32": crc, "sha256": digest.hexdigest(), "byte_size": value.st_size}
            seen.add(relative)
    if seen != set(expected):
        raise ValueError("exact600 extracted original files required")
    guard(plan)
    write(OUTPUT / "release_integrity.json", {
        "archive_sha256": archive_digest, "archive_bytes": count,
        "archive_identity": plan["archive_identity"], "publisher_checksum_verified": False,
        "headers_and_reference_universe_verified": True, "extracted_videos": len(seen),
        "video_payload_bytes": sum(expected.values()), "extractor_returncode": result.returncode,
        "extractor_stderr_bytes": 0, "extractor_stderr_sha256": sha(errors),
        "extraction_and_independent_crc_validation_succeeded": True,
        "independent_unpacked_crc32_verified": True, "video_payload_pins": payload_pins,
        "extraction_scope": "600 canonical regular AVI entries and their52 native directories",
        "bundled_executables_run": 0, "model_downloads": 0})
    print("RAR285_CRC_EXTRACT_OK", len(seen), flush=True)


def produce_unit(plan, index, original, session):
    path = OUTPUT / "temporary" / original["media_relpath"]
    if original["dataset"] != "CASIA-FASD" or original["role"] not in ROLES:
        raise ValueError("frozen CASIA source roles only")
    initial = shared.identity(path)
    if initial[2] != original["byte_size"]:
        raise ValueError("extracted canonical byte size drift")
    write(OUTPUT / "attempts" / f"{index:04d}.json", {
        "index": index, "video_id": original["video_id"], "role": original["role"], "status": "started"})
    media_digest = sha(path)
    pin = read(OUTPUT / "release_integrity.json")["video_payload_pins"][original["media_relpath"]]
    if media_digest != pin["sha256"] or initial[2] != pin["byte_size"]:
        raise ValueError("extracted payload differs from CRC/SHA stage commitment")
    media = {key: original[key] for key in ("video_id", "role", "binary_label", "official_split", "subject_id", "media_relpath")}
    media.update(media_sha256=media_digest, byte_size=initial[2], archive_crc_validated=True,
                 **shared.probe_video(path, timeout_seconds=max(1, min(180, int(plan["deadline_unix_seconds"] - time.time())))))
    if shared.identity(path) != initial:
        raise ValueError("extracted payload changed during strict probe")
    media_path = OUTPUT / "media" / f"{index:04d}.json"
    write(media_path, media)
    transaction = shared.technical_transaction(media)
    transaction.update(media_sha256=media_digest, media_record_sha256=sha(media_path))
    row = {**transaction, "index": index, "replacement": False, "model_sha256": shared.MODEL_SHA256,
           "config_sha256": plan["active_config_sha256"], "assets": {}}
    if transaction["selected_frame"] is not None:
        selected, captured = transaction["selected_frame"], []

        def consume(order, rgb):
            if order == selected["decode_order"]:
                if hashlib.sha256(rgb.tobytes()).hexdigest() != selected["rgb_sha256"]:
                    raise ValueError("frozen primary RGB drift")
                captured.append(rgb.copy())

        prefix = OUTPUT / "replay" / f"{index:04d}"
        strict_replay(path, media, consume, prefix,
                      timeout=min(180, max(0.001, plan["deadline_unix_seconds"] - time.time())))
        if len(captured) != 1:
            raise ValueError("one frozen middle frame only; no replacement")
        row["replay_record_sha256"] = sha(prefix.with_suffix(".json"))
        relative = f"frames/{index:04d}.png"
        row["selected_RGB_asset"] = {"path": relative, **shared.write_png(relative, captured[0])}
        shared.infer_image(session, captured[0], row)
    write(OUTPUT / "transactions" / f"{index:04d}.json", row)
    return row, media


def worker(plan):
    import cv2
    import onnxruntime as ort

    shared.check_bindings(plan["sources"])
    shared.images.check_policy()
    if sha(shared.retained.MODEL) != shared.MODEL_SHA256:
        raise ValueError("reused model drift")
    guard(plan)
    try:
        stage_release(plan)
        options = ort.SessionOptions()
        options.intra_op_num_threads = options.inter_op_num_threads = 1
        session = ort.InferenceSession(str(shared.retained.MODEL), sess_options=options, providers=["CPUExecutionProvider"])
        if session.get_providers() != ["CPUExecutionProvider"]:
            raise ValueError("CPU-only inference required")
        cv2.setNumThreads(1)
        media_rows = []
        for index, original in enumerate(plan["videos"]):
            guard(plan)
            row, media = produce_unit(plan, index, original, session)
            media_rows.append(media)
            print("CASIA285", index, row["role"], row["detector_status"], flush=True)
        findings = shared.exact_checks(media_rows, {row["video_id"]: row for row in plan["videos"]})
        write(OUTPUT / "content_checks.json", {
            "exact_groups": findings, "forbidden_exact_crossings": 0,
            "known_parent_scope": "reference subject-scoped print/replay construction preserved",
            "near_duplicate_independence_certified": False, "joined_cross_dataset_ancestry_certified": False})
        shared.check_bindings(plan["sources"])
        guard(plan)
        write(OUTPUT / "worker_completion.json", {
            "transactions": len(media_rows), "video_crc_checked": len(media_rows),
            "native_frames": sum(row["frame_count"] for row in media_rows),
            "video_payload_bytes": sum(row["byte_size"] for row in media_rows),
            "provider": ["CPUExecutionProvider"], "gpu_seconds": 0, "model_scores": 0, "fitted_scores": 0})
    finally:
        cleanup()


def validate_manifest(plan, rows):
    canonical = {row["video_id"]: row for row in plan["videos"]}
    identities = [row["video_id"] for row in rows]
    if len(identities) != 600 or len(set(identities)) != 600 or set(identities) != set(canonical):
        raise ValueError("exact600 original manifest IDs required")
    counts, selected, terminal = Counter(), 0, 0
    for row in rows:
        original = canonical[row["video_id"]]
        if any(row[key] != original[key] for key in ("role", "binary_label", "subject_id", "official_split")):
            raise ValueError("manifest parent role/class/subject/partition drift")
        if row["active_config_sha256"] != plan["active_config_sha256"] or row["model_score"] is not None or row["classifier_error"] is not None or row["replacement"] is not False or row["retain_original_denominator"] is not True:
            raise ValueError("scoreless fixed-config original denominator accounting required")
        counts[row["detector_status"]] += 1
        if row["selected_frame"] is None:
            terminal += 1
            if row["detector_status"] != "not_run" or row["final_k1_action"] != "non_accept" or row["asset_sha256"]:
                raise ValueError("pre-detector failure must not fabricate pixels or acceptance")
        else:
            selected += 1
            if row["detector_status"] not in {"success", "failed"}:
                raise ValueError("explicit selected-frame detector outcome required")
            if row["detector_status"] == "failed" and row["final_k1_action"] != "non_accept":
                raise ValueError("detector failure must remain non_accept")
    if Counter(row["role"] for row in rows) != ROLES:
        raise ValueError("frozen role denominators drift")
    return {"originals": 600, "selected": selected, "pre_detector_failure": terminal,
            "detector_success": counts["success"], "detector_failure": counts["failed"]}


def verify(plan):
    shared.check_bindings(plan["sources"])
    guard(plan)
    shared.images.check_policy()
    if sha(shared.retained.MODEL) != shared.MODEL_SHA256:
        raise ValueError("final model drift")
    expected = {f"{index:04d}.json" for index in range(600)}
    for folder in ("media", "transactions", "attempts"):
        if {path.name for path in (OUTPUT / folder).iterdir()} != expected:
            raise ValueError("exact600 per-unit records required")
    manifest, assets, media_rows, records, replay_paths = [], {}, [], {}, set()
    for index, original in enumerate(plan["videos"]):
        row_path, media_path = OUTPUT / "transactions" / f"{index:04d}.json", OUTPUT / "media" / f"{index:04d}.json"
        row = read(row_path)
        attempt = read(OUTPUT / "attempts" / f"{index:04d}.json")
        if attempt != {"index": index, "video_id": original["video_id"], "role": original["role"], "status": "started"}:
            raise ValueError("single original-attempt identity drift")
        media = shared.read_verified_json(media_path, row["media_record_sha256"])
        if any(media[key] != original[key] for key in ("video_id", "role", "binary_label", "official_split", "subject_id", "media_relpath", "byte_size")):
            raise ValueError("media native/frozen parent drift")
        if media["archive_crc_validated"] is not True:
            raise ValueError("full archive CRC validation required")
        transaction = shared.technical_transaction(media)
        transaction.update(media_sha256=media["media_sha256"], media_record_sha256=sha(media_path))
        if any(row[key] != value for key, value in transaction.items() if key not in {"detector_status", "final_k1_action"}):
            raise ValueError("fixed primary transaction drift")
        if row["index"] != index or row["config_sha256"] != plan["active_config_sha256"] or row["model_sha256"] != shared.MODEL_SHA256:
            raise ValueError("index/config/model pin drift")
        if transaction["selected_frame"] is None:
            if row["detector_status"] != "not_run" or row["final_k1_action"] != "non_accept" or row["assets"] or "selected_RGB_asset" in row or "replay_record_sha256" in row:
                raise ValueError("terminal probe failure fabricated output")
            entry = {**transaction, "asset_sha256": {}, "record_sha256": sha(row_path)}
        else:
            decoded_tokens(media)
            relative, stderr = f"replay/{index:04d}.json", f"replay/{index:04d}.stderr"
            replay = shared.read_verified_json(OUTPUT / relative, row["replay_record_sha256"])
            if replay["strict_success"] is not True or replay["frames_verified"] != media["frame_count"] or replay["frame_count"] != media["frame_count"] or replay["decoded_rgb_sequence_sha256"] != media["decoded_rgb_sequence_sha256"]:
                raise ValueError("full native-frame replay identity mismatch")
            if replay["returncode"] != 0 or replay["stderr_bytes"] != 0 or replay["failure"] is not None or replay["frame_substitution"] is not False or (OUTPUT / stderr).stat().st_size or sha(OUTPUT / stderr) != replay["stderr_sha256"]:
                raise ValueError("strict replay exit/stderr/EOF accounting drift")
            replay_paths.update((relative, stderr))
            records[relative], records[stderr] = sha(OUTPUT / relative), sha(OUTPUT / stderr)
            entry, unit_assets = shared.images.validate_unit(
                {"transaction": transaction, "media_path": str(media_path)}, OUTPUT, index, 4,
                plan["active_config_sha256"], sha(row_path))
            assets.update(unit_assets)
        entry.update(index=index, subject_id=original["subject_id"], official_split=original["official_split"],
                     active_config_sha256=plan["active_config_sha256"], replacement=False,
                     retain_original_denominator=True, model_score=None, classifier_error=None)
        manifest.append(entry)
        media_rows.append(media)
        for path in (row_path, media_path, OUTPUT / "attempts" / f"{index:04d}.json"):
            records[path.relative_to(OUTPUT).as_posix()] = sha(path)
        if index % 20 == 0:
            print("READBACK285", index, flush=True)
    if {path.relative_to(OUTPUT).as_posix() for path in (OUTPUT / "replay").glob("*")} != replay_paths:
        raise ValueError("exact replay diagnostic/receipt set required")
    if {path.relative_to(OUTPUT).as_posix() for folder in ("frames", "crops") for path in (OUTPUT / folder).glob("*")} != set(assets):
        raise ValueError("exact selected image/crop set required")
    counts = validate_manifest(plan, manifest)
    findings = shared.exact_checks(media_rows, {row["video_id"]: row for row in plan["videos"]})
    content = read(OUTPUT / "content_checks.json")
    if content["exact_groups"] != findings or content["forbidden_exact_crossings"] != 0:
        raise ValueError("exact content/boundary accounting drift")
    required = {
        "transactions": 600, "video_crc_checked": 600,
        "native_frames": sum(row["frame_count"] for row in media_rows),
        "video_payload_bytes": sum(row["byte_size"] for row in media_rows),
        "provider": ["CPUExecutionProvider"], "gpu_seconds": 0, "model_scores": 0, "fitted_scores": 0}
    completion = read(OUTPUT / "worker_completion.json")
    if any(type(completion.get(key)) is not type(value) or completion[key] != value for key, value in required.items()):
        raise ValueError("worker completion/full CRC/frame accounting drift")
    integrity = read(OUTPUT / "release_integrity.json")
    if integrity["archive_identity"] != plan["archive_identity"] or integrity["archive_bytes"] != plan["archive_identity"][2] or integrity["extracted_videos"] != 600 or integrity["video_payload_bytes"] != required["video_payload_bytes"]:
        raise ValueError("exact release/container/media byte accounting drift")
    if integrity["extractor_returncode"] != 0 or integrity["extractor_stderr_bytes"] != 0 or integrity["independent_unpacked_crc32_verified"] is not True or sha(OUTPUT / "extraction.stderr") != integrity["extractor_stderr_sha256"]:
        raise ValueError("RAR extraction diagnostic/CRC drift")
    pins = integrity["video_payload_pins"]
    if set(pins) != {row["media_relpath"] for row in plan["videos"]}:
        raise ValueError("exact600 media CRC/SHA pins required")
    crc_headers = {row["relpath"]: row for row in plan["crc_headers"] if row["kind"] == "file"}
    for media in media_rows:
        pin = pins[media["media_relpath"]]
        if pin["sha256"] != media["media_sha256"] or pin["byte_size"] != media["byte_size"] or pin["crc32"] != crc_headers[media["media_relpath"]]["crc32"]:
            raise ValueError("per-video header CRC/SHA/size parent drift")
    if list((OUTPUT / "temporary").iterdir()):
        raise ValueError("owned staged videos must be removed before final readback")
    sheets = shared.make_sheets(plan, manifest)
    write(OUTPUT / "full_manifest.json", {
        "dataset": "CASIA-FASD", "rows": manifest, **counts,
        "active_config_sha256": plan["active_config_sha256"], "scientific_readiness": False})
    validate_manifest(plan, read(OUTPUT / "full_manifest.json")["rows"])
    shared.check_bindings(plan["sources"])
    guard(plan)
    result = {
        **required, **counts, "role_originals": dict(Counter(row["role"] for row in manifest)),
        "full_manifest_sha256": sha(OUTPUT / "full_manifest.json"),
        "release_integrity_sha256": sha(OUTPUT / "release_integrity.json"),
        "content_checks_sha256": sha(OUTPUT / "content_checks.json"),
        "per_unit_sha256": records, "asset_sha256": assets, "visual_sheets": sheets,
        "strict_replay_count": len(replay_paths) // 2, "visual_inspection_completed": False,
        "exact_duplicate_groups": len(findings), "forbidden_exact_crossings": 0, "scientific_readiness": False}
    write(OUTPUT / "readback.json", result)
    return result


def failure_rows(plan, failure):
    write(OUTPUT / "failure_rows.json", {
        "rows": [{"index": index, "video_id": row["video_id"], "role": row["role"],
                  "binary_label": row["binary_label"], "retain_original_denominator": True,
                  "detector_status": "unverified_after_package_failure", "final_k1_action": "non_accept",
                  "failure": failure} for index, row in enumerate(plan["videos"])],
        "automatic_retry": False})


def supervise(plan):
    write(OUTPUT / "attempt_lock.json", {"parent_pid": os.getpid(), "plan_sha256": sha(OUTPUT / "plan.json"),
                                       "attempts_authorized": 1, "automatic_retry": False})
    process, failure, readback = None, None, None
    peaks = {"rss_bytes": 0, "output_bytes": 0, "temporary_bytes": 0}
    started = time.monotonic()
    try:
        for mode in ("--worker", "--verify"):
            process = subprocess.Popen([sys.executable, str(Path(__file__)), mode], start_new_session=True)
            while True:
                value = measured(process.pid)
                peaks = {key: max(peaks[key], value[key]) for key in peaks}
                enforce(plan, value)
                try:
                    if process.wait(timeout=2):
                        raise RuntimeError(mode + " failed; no retry")
                    break
                except subprocess.TimeoutExpired:
                    continue
            process = None
        readback = read(OUTPUT / "readback.json")
        manifest = shared.read_verified_json(OUTPUT / "full_manifest.json", readback["full_manifest_sha256"])
        if any(readback[key] != value for key, value in validate_manifest(plan, manifest["rows"]).items()):
            raise ValueError("final full600 manifest count mismatch")
        for relative, expected in readback["per_unit_sha256"].items():
            if sha(OUTPUT / relative) != expected:
                raise ValueError("final per-unit/replay record drift")
        for name in ("release_integrity", "content_checks"):
            shared.read_verified_json(OUTPUT / (name + ".json"), readback[name + "_sha256"])
        if manifest["active_config_sha256"] != sha(shared.images.ACTIVE):
            raise ValueError("final active policy drift")
        shared.check_bindings(plan["sources"])
        guard(plan)
        value = measured(os.getpgrp())
        value["rss_bytes"] = max(value["rss_bytes"], resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024)
        peaks = {key: max(peaks[key], value[key]) for key in peaks}
        enforce(plan, peaks)
    except Exception as error:
        failure = type(error).__name__ + ": " + str(error)
        print("CASIA285_FAILED", failure, flush=True)
    finally:
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
        cleanup()
    if failure:
        failure_rows(plan, failure)
    result = {
        "checkpoint": 285, "dataset": "CASIA-FASD", "completion_claimed": failure is None and readback is not None,
        "failure": failure, "caps": CAPS, "sampled_peaks": peaks,
        "package_wall_seconds": time.time() - authority()["started_unix_seconds"],
        "supervised_wall_seconds": time.monotonic() - started,
        "readback_sha256": sha(OUTPUT / "readback.json") if readback else None,
        "attempts": 1, "automatic_retry": False, "gpu_seconds": 0,
        "visual_inspection_pending": failure is None, "scientific_readiness": False}
    write(OUTPUT / "resources.json", result)
    if read(OUTPUT / "resources.json") != result:
        raise ValueError("terminal resources readback drift")
    print("CASIA285_TERMINAL", json.dumps(result), flush=True)
    return result


def publish(result):
    readback = read(OUTPUT / "readback.json") if result["completion_claimed"] else None
    write(ROOT / "results/phase1/casia-preprocessing285-v1.json", {
        **result, "originals": 600, "subjects": 50, "role_originals": ROLES, "role_subjects": GROUPS,
        "status": "software_complete_visual_review_pending" if result["completion_claimed"] else "concrete_defect_stopped_no_retry",
        "visual_inspection_completed": False, "audit_summary_statuses_changed": False,
        **{key: readback[key] if readback else None for key in (
            "selected", "pre_detector_failure", "detector_success", "detector_failure", "native_frames",
            "video_payload_bytes", "strict_replay_count", "exact_duplicate_groups", "forbidden_exact_crossings")},
        "active_config_sha256": sha(shared.images.ACTIVE), "model_scores": 0, "fitted_scores": 0,
        "target_access": False, "model_downloads": 0, "near_duplicate_independence_certified": False,
        "private_record_sha256": {name: sha(OUTPUT / name) for name in (
            "owner_approval.json", "supervisor.json", "plan.json", "attempt_lock.json",
            "release_integrity.json", "content_checks.json", "worker_completion.json", "full_manifest.json",
            "readback.json", "resources.json", "package_failure.json") if (OUTPUT / name).exists()}})


def status():
    return {
        "checkpoint": 285, "originals": 600, "written_records": len(list((OUTPUT / "transactions").glob("*.json"))),
        "plan_committed": (OUTPUT / "plan.json").exists(), "release_verified": (OUTPUT / "release_integrity.json").exists(),
        "worker_complete": (OUTPUT / "worker_completion.json").exists(),
        "terminal": read(OUTPUT / "resources.json") if (OUTPUT / "resources.json").exists() else None,
        "package_failure": read(OUTPUT / "package_failure.json") if (OUTPUT / "package_failure.json").exists() else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    for name in ("record-approval", "run-once", "worker", "verify", "status"):
        mode.add_argument("--" + name, action="store_true")
    args = parser.parse_args()
    if args.status:
        print(json.dumps(status(), indent=2))
        return 0
    if args.record_approval:
        if OUTPUT.exists() or OUTPUT.is_symlink():
            raise FileExistsError("one approved CASIA package only")
        now = APPROVAL_CLOCK_START
        write(OUTPUT / "owner_approval.json", {
            "checkpoint": 285, "explicit_owner_approval": True, "selected_answer": APPROVAL, "caps": CAPS,
            "started_unix_seconds": now, "deadline_unix_seconds": now + CAPS["wall_seconds"],
            "recorded_unix_seconds": time.time(),
            "clock_basis": "conservative review284 request2026-10-23T00:22:55Z; includes code/tests before receipt creation",
            "review284_sha256": sha(ROOT / "docs/284-review-msu282-local-audit-and-image-completion.md"),
            "archive_bytes": 876296302, "video_payload_bytes": 866586586,
            "frame_count_before_execution": None, "temporary_cleanup_authorized": True,
            "automatic_retry": False, "model_download": False})
        return 0
    if args.worker or args.verify:
        plan = read(OUTPUT / "plan.json")
        lease = read(OUTPUT / "attempt_lock.json")
        if lease["parent_pid"] != os.getppid() or lease["plan_sha256"] != sha(OUTPUT / "plan.json") or os.getsid(0) != os.getpid():
            raise ValueError("single supervised child/plan lease required")
        shared.retained.arm_deadline(plan["deadline_unix_seconds"])
        shared.OUTPUT = OUTPUT
        worker(plan) if args.worker else verify(plan)
        return 0
    authority()
    if (OUTPUT / "supervisor.json").exists() or (OUTPUT / "resources.json").exists():
        raise FileExistsError("one authorized CASIA attempt; no retry")
    write(OUTPUT / "supervisor.json", {
        "pid": os.getpid(), "started_unix_seconds": time.time(),
        "runner_sha256": sha(Path(__file__)), "automatic_retry": False})
    with (OUTPUT / "execution.log").open("xb", buffering=0) as log:
        os.dup2(log.fileno(), 1)
        os.dup2(log.fileno(), 2)
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    shared.retained.arm_deadline(authority()["deadline_unix_seconds"])
    try:
        plan = make_plan()
        result = supervise(plan)
        publish(result)
        return 0 if result["completion_claimed"] else 1
    except Exception as error:
        write(OUTPUT / "package_failure.json", {
            "error_type": type(error).__name__, "message": str(error),
            "automatic_retry": False, "scientific_readiness": False})
        if not (ROOT / "results/phase1/casia-preprocessing285-v1.json").exists():
            publish({"completion_claimed": False, "failure": type(error).__name__ + ": " + str(error)})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
