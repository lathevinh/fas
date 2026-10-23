"""Bounded SiW-Mv2 local audit and fixed-image preparation, never evaluation."""

from __future__ import annotations

import argparse
from collections import Counter
import copy
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import casia_budget289 as budget
import casia_probe287 as strict
import finish_casia289 as historical
import inventory_siwmv2 as native
import preprocess_msu282 as shared
from fas.freeze import write_immutable_record
from fas.siwmv2 import inventory_headers, verify_reference_sources
from fas.transactions import select_primary_frame, technical_transaction
from msu_replay282 import replay_command, strict_replay

OUTPUT = shared.BASE / "siwmv2_preprocessing291_v1"
IPC = Path.home() / ".cache/fas/siwmv2-native-ipc291"
ARCHIVE = ROOT / "SiW/SiW-Mv2.zip"
REFERENCE = Path("/mnt/e/FAS-private/reference-sources/Multi-domain-learning-FAS/"
                 "8667dbcd316b38141729c057adf7517fe0602608/source_SiW_Mv2")
INVENTORY = shared.BASE / "siwmv2_metadata_inventory_v1.json"
POPULATION = shared.BASE / "siwmv2_protocol_i_intersection_v1.json"
FROZEN = shared.FROZEN
SUMMARY = ROOT / "results/phase1/siwmv2-preprocessing291-v1.json"
ROOTS = (*historical.ROOTS, OUTPUT, IPC)
CAPS = {"wall_seconds": 21600, "rss_bytes": 4 * 1024 ** 3,
        "output_bytes": 48 * 1024 ** 3, "gpu_seconds": 0}
ROLES = {"train": 632, "branch_calibration": 215, "g_domain": 210}
FILE_LIMIT = 16 * 1024 ** 2
CLIENT = None


def read(path):
    return shared.read_json(path)


def sha(path):
    return shared._sha256(path)


def write(path, value):
    shared.write_immutable_record(path, value)


def authority():
    row = read(OUTPUT / "owner_approval.json")
    if (row["explicit_owner_approval"] is not True
            or row["selected_answer"] != "approve_combined_siw291_full1680"
            or row["caps"] != CAPS or row["originals"] != 1680
            or row["source_originals"] != 1057 or row["test_originals"] != 623
            or row["automatic_retry"] is not False or row["new_tools_models"] is not False
            or row["deadline_unix_seconds"] != row["started_unix_seconds"] + CAPS["wall_seconds"]
            or row["work_deadline_unix_seconds"] != row["deadline_unix_seconds"] - 600
            or row["governing_review_sha256"] != sha(ROOT / "docs/290-review-doc289-casia-completion.md")):
        raise ValueError("explicit unchanged full1680 SiW291 authority required")
    return row


def enforce(value, *, work=True):
    row = authority()
    if time.time() >= row["work_deadline_unix_seconds" if work else "deadline_unix_seconds"]:
        raise budget.BudgetError("SiW291 original work/final deadline")
    if value["rss_bytes"] > CAPS["rss_bytes"]:
        raise budget.BudgetError("SiW291 combined4GiB RSS cap")
    if value["output_bytes"] > CAPS["output_bytes"] - shared.RESERVE:
        raise budget.BudgetError("SiW291 combined48GiB storage cap")


def usage(group):
    value = shared.usage(group, OUTPUT / ".unused")
    for pid in {os.getpid(), read(IPC / "processes.json")["scanner_pid"]} - {group}:
        extra = shared.usage(pid, OUTPUT / ".unused")
        value["rss_bytes"] += extra["rss_bytes"]
        value["temporary_bytes"] += extra["temporary_bytes"]
    return value


def reconcile(videos, roles):
    lookup = {row["video_id"]: row for row in roles}
    identities = {row["video_id"] for row in videos}
    if len(videos) != 1680 or len(identities) != 1680 or len(lookup) != len(roles):
        raise ValueError("exact1680 unique originals and unique source-role rows required")
    source = {row["video_id"] for row in videos if row["official_split"] == "train"}
    if len(source) != 1057 or set(lookup) != source or Counter(row["role"] for row in roles) != ROLES:
        raise ValueError("exact frozen1057 source roles and disjoint623 test required")
    result = []
    for video in videos:
        if (video["dataset"] != "SiW-Mv2" or video["subject_id"] is not None
                or video["participant_identity_verified"] is not False
                or video["group_unit"] != "video" or video["group_id"] != video["video_id"]
                or video["official_split"] not in {"train", "test"} or video["role"] is not None):
            raise ValueError("unchanged video grouping, unknown subjects and null canonical roles required")
        role = lookup.get(video["video_id"])
        if role is not None and any(role[key] != ("" if key == "subject_id" else video[key])
                                    for key in ("dataset", "subject_id", "binary_label")):
            raise ValueError("source role/class/unknown-subject binding drift")
        result.append({**video, "role": role["role"] if role else None})
    return result


def prepare():
    approval = authority()
    old = read(INVENTORY)
    if sha(INVENTORY) != read(ROOT / "results/phase1/siwmv2-adapter-inventory-v1.json")["inventory_sha256"]:
        raise ValueError("accepted private inventory bytes drift")
    verify_reference_sources(REFERENCE)
    fresh = inventory_headers(native.read_headers(ARCHIVE), population_payload=POPULATION.read_bytes(),
                              release_id=old["release_id"], archive_name=ARCHIVE.name)
    if fresh != old:
        raise ValueError("current ZIP header/native inventory drift")
    canonical = read(FROZEN / "siw_mv2_canonical.json")
    if canonical["videos"] != old["videos"]:
        raise ValueError("canonical/native inventory exact equality required")
    from complete_casia287 import csv_rows
    videos = reconcile(canonical["videos"], csv_rows(FROZEN / "siw_mv2_roles.csv"))
    # First committed units cover every supplied container and both partitions.
    representatives = {}
    for row in videos:
        representatives.setdefault((Path(row["media_relpath"]).suffix, row["official_split"]), row["video_id"])
    first = set(representatives.values())
    videos = [row for row in videos if row["video_id"] in first] + [row for row in videos if row["video_id"] not in first]
    strata = {}
    for index, row in enumerate(videos):
        strata.setdefault((row["role"], row["binary_label"], row["reference_attack_type"]), index)
    fixed = sorted(set(strata.values()) | set(range(0, 1680, 80)))
    shared.images.check_policy()
    if sha(shared.retained.MODEL) != shared.MODEL_SHA256:
        raise ValueError("accepted detector weight drift")
    sources = [ROOT / name for name in (
        "scripts/preprocess_siw291.py", "scripts/complete_siw291.py", "tests/test_siw_preprocessing.py",
        "scripts/casia_budget289.py", "scripts/casia_probe287.py", "scripts/casia_resource287.py",
        "scripts/msu_replay282.py", "scripts/preprocess_msu282.py", "scripts/preprocess_oulu280.py",
        "src/fas/siwmv2.py", "src/fas/transactions.py", "src/fas/preprocessing.py",
        "configs/preprocessing_v3.yaml", "configs/preprocessing_pilot_v1.yaml",
        "docs/290-review-doc289-casia-completion.md")]
    sources += [INVENTORY, POPULATION, shared.retained.MODEL, OUTPUT / "owner_approval.json"]
    sources += [FROZEN / name for name in ("siw_mv2_canonical.json", "siw_mv2_roles.csv",
                                         "siw_mv2_metadata.csv", "source_role_freeze.json")]
    sources += [REFERENCE / name for name in fresh["reference_sha256_verified"]]
    headers = native.read_headers(ARCHIVE)
    plan = {"checkpoint": 291, "videos": videos, "visual_indices": fixed,
            "compatibility_indices": [i for i, row in enumerate(videos) if row["video_id"] in first],
            "archive_identity": shared.identity(ARCHIVE), "headers": headers,
            "header_inventory_sha256": fresh["header_inventory_sha256"],
            "sources": {str(path): sha(path) for path in sources},
            "active_config_sha256": sha(shared.images.ACTIVE), "model_sha256": shared.MODEL_SHA256,
            "deadline_unix_seconds": approval["work_deadline_unix_seconds"],
            "excluded_originals": len(fresh["out_of_protocol_videos"]),
            "missing_references": len(fresh["missing_references"]),
            "unknown_subjects_preserved": True, "target_source_roles": 0,
            "test_scope": approval["test_scope"], "automatic_retry": False,
            "ffmpeg": subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True,
                                     check=True, timeout=10).stdout.splitlines()[0]}
    write(OUTPUT / "plan.json", plan)
    for folder in ("attempts", "transactions", "media", "probe", "replay", "frames", "crops", "temporary"):
        (OUTPUT / folder).mkdir(exist_ok=False)
    print(json.dumps({"prepared": True, "originals": 1680, "source_roles": ROLES, "null_role_test": 623,
                      "compatibility_units": len(first), "fixed_tiles": len(fixed),
                      "archive_bytes": plan["archive_identity"][2], "no_media_payload_read": True}))


def guard(plan):
    if shared.identity(ARCHIVE) != plan["archive_identity"]:
        raise ValueError("SiW archive identity drift")


def configure(client):
    global CLIENT
    CLIENT = client
    shared.OUTPUT = shared.images.OUTPUT = OUTPUT
    # Null is a separately checked test partition, never a fabricated source role.
    shared.images.ROLE_COUNTS = {**ROLES, None: 623}
    strict.measured = client.measure
    strict.diagnosis.enforce = enforce
    original_write, original_png = shared.write_immutable_record, shared.write_png

    def record(path, value):
        with client.reserve(2 * len((json.dumps(value, indent=2, sort_keys=True) + "\n").encode())):
            original_write(path, value)

    def png(relative, rgb):
        if str(rgb.dtype) != "uint8" or len(rgb.shape) != 3 or rgb.shape[2] != 3:
            raise ValueError("RGB uint8 PNG required")
        with client.reserve(4 * rgb.nbytes + 1024 ** 2):
            return original_png(relative, rgb)

    shared.write_immutable_record, shared.write_png = record, png


def capture(command, prefix):
    with CLIENT.reserve(2 * FILE_LIMIT):
        return strict.capture(budget.limited_command(command, FILE_LIMIT), prefix, timeout=180)


def parse_probe(raw, hashes):
    normalized = copy.deepcopy(raw)
    try:
        dimensions = [tuple(map(int, line.split(":", 1)[1].strip().split("x")))
                      for line in hashes.splitlines() if line.startswith("#dimensions 0:")]
        if len(dimensions) != 1 or any((frame["width"], frame["height"]) != dimensions[0]
                                       for frame in raw["frames"]):
            raise ValueError("native metadata/framehash output dimensions disagree")
        tick = Fraction(raw["streams"][0]["time_base"])
        if tick <= 0:
            raise ValueError("nonpositive timebase")
        for frame in normalized["frames"]:
            native_time = int(frame["best_effort_timestamp"]) * tick
            text = frame["best_effort_timestamp_time"]
            precision = Fraction(1, 10 ** len(text.partition(".")[2])) if "." in text else Fraction(1)
            if abs(native_time - Fraction(text)) > precision / 2:
                raise ValueError("native integer/display timestamp disagreement")
            frame["best_effort_timestamp_time"] = str(native_time)
    except (KeyError, IndexError, TypeError, ValueError, ZeroDivisionError) as error:
        raise strict.ProbeFailure("native_integer_timestamps", type(error).__name__ + ":" + str(error)) from error
    result = strict.parse_evidence(normalized, hashes)
    result["timestamp_transport"] = "native_integer_ticks_preserved_encoder_timebase"
    return result


def probe(path, folder):
    folder.mkdir()
    metadata = ["ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_frames", "-show_streams", "-show_format", "-of", "json", str(path)]
    framehash = ["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-err_detect", "explode",
                 "-threads", "1", "-i", str(path), "-map", "0:v:0", "-an", "-sn", "-dn",
                 "-pix_fmt", "rgb24", "-threads", "1", "-vsync", "0",
                 "-enc_time_base", "-1", "-f", "framehash", "-hash", "sha256", "-"]
    try:
        raw = json.loads(capture(metadata, folder / "metadata"))
        hashes = capture(framehash, folder / "framehash")
        result = parse_probe(raw, hashes)
    except (strict.ProbeFailure, json.JSONDecodeError) as error:
        stage = error.stage if isinstance(error, strict.ProbeFailure) else "metadata_json"
        reason = error.reason if isinstance(error, strict.ProbeFailure) else str(error)
        failure = {"stage": stage, "reason": reason, "exception_type": type(error).__name__}
        write(folder / "failure.json", failure)
        result = {"decode_status": "failed", "container": None, "codec": None,
                  "duration_ms": None, "fps": None, "frame_count": 0, "frame_index": [],
                  "decoded_rgb_sequence_sha256": None, "middle_decoded_candidates": [],
                  "failure_reason": stage + ":" + reason, "probe_failure": failure}
    write(folder / "result.json", result)
    return result


def transaction(media):
    if media["official_split"] == "train":
        return technical_transaction(media)
    if media["official_split"] != "test" or media["role"] is not None:
        raise ValueError("test preparation must retain null role and never enter source policy")
    selected = select_primary_frame(media)
    return {"video_id": media["video_id"], "binary_label": media["binary_label"], "role": None,
            "selected_frame": selected, "technical_status": "primary_frame_available" if selected else "terminal_failure",
            "failure_stage": None if selected else "decode", "final_k1_action": None if selected else "non_accept",
            "model_score": None, "classifier_error": None, "detector_status": "not_run",
            "score_fit_status": "not_authorized_test_preparation_only", "retain_original_denominator": True}


def copy_member(archive, entry, target, expected, deadline):
    digest, crc, count = hashlib.sha256(), 0, 0
    import zlib
    with archive.open(entry) as source, target.open("xb") as out:
        while block := source.read(1024 ** 2):
            if time.time() >= deadline:
                raise TimeoutError("member copy deadline")
            count += len(block)
            if count > expected or count > 64 * 1024 ** 2:
                raise ValueError("member byte cap/drift")
            digest.update(block)
            crc = zlib.crc32(block, crc)
            out.write(block)
    if count != expected or crc & 0xffffffff != entry.CRC:
        raise ValueError("exact native member EOF/size/CRC required")
    return {"byte_size": count, "sha256": digest.hexdigest(), "crc32": f"{crc & 0xffffffff:08x}"}


def unit(plan, index, archive, session):
    original = plan["videos"][index]
    write(OUTPUT / "attempts" / f"{index:04d}.json",
          {"index": index, "video_id": original["video_id"], "role": original["role"], "status": "started"})
    entry = archive.getinfo(original["media_relpath"])
    expected = next(row for row in plan["headers"] if row["path"] == original["media_relpath"])
    current = {"path": entry.filename, "size": entry.file_size, "crc32": entry.CRC,
               "compressed_size": entry.compress_size, "flags": entry.flag_bits, "external_attr": entry.external_attr}
    if current != expected or entry.file_size != original["byte_size"]:
        raise ValueError("native ZIP header/canonical byte binding drift")
    path = OUTPUT / "temporary" / ("current" + Path(entry.filename).suffix)
    try:
        with CLIENT.reserve(entry.file_size):
            pin = copy_member(archive, entry, path, entry.file_size, plan["deadline_unix_seconds"])
        initial = shared.identity(path)
        media = {key: original[key] for key in ("video_id", "role", "binary_label", "official_split", "subject_id", "media_relpath")}
        media.update(media_sha256=pin["sha256"], byte_size=pin["byte_size"], native_crc32=pin["crc32"],
                     archive_crc_validated=True, **probe(path, OUTPUT / "probe" / f"{index:04d}"))
        if shared.identity(path) != initial or sha(path) != pin["sha256"]:
            raise ValueError("source changed during strict decode")
        folder = OUTPUT / "probe" / f"{index:04d}"
        media["probe_evidence_sha256"] = {p.relative_to(OUTPUT).as_posix(): sha(p) for p in folder.iterdir()}
        media_path = OUTPUT / "media" / f"{index:04d}.json"
        write(media_path, media)
        txn = transaction(media)
        txn.update(media_sha256=media["media_sha256"], media_record_sha256=sha(media_path))
        row = {**txn, "index": index, "replacement": False, "model_sha256": shared.MODEL_SHA256,
               "config_sha256": plan["active_config_sha256"], "assets": {}}
        if txn["selected_frame"] is not None:
            selected, captured = txn["selected_frame"], []

            def consume(order, rgb):
                if order == selected["decode_order"]:
                    if hashlib.sha256(rgb.tobytes()).hexdigest() != selected["rgb_sha256"]:
                        raise ValueError("fixed middle RGB mismatch")
                    captured.append(rgb.copy())

            prefix = OUTPUT / "replay" / f"{index:04d}"
            with CLIENT.reserve(FILE_LIMIT + 1024 ** 2):
                strict_replay(path, media, consume, prefix, timeout=180,
                              command=budget.limited_command(replay_command(path), FILE_LIMIT))
            if len(captured) != 1:
                raise ValueError("exactly one fixed middle frame; no replacement")
            row["replay_record_sha256"] = sha(prefix.with_suffix(".json"))
            relative = f"frames/{index:04d}.png"
            row["selected_RGB_asset"] = {"path": relative, **shared.write_png(relative, captured[0])}
            shared.infer_image(session, captured[0], row)
        write(OUTPUT / "transactions" / f"{index:04d}.json", row)
        return row, media
    finally:
        if path.exists():
            path.unlink()


def worker(plan):
    import cv2
    import onnxruntime as ort

    guard(plan)
    shared.check_bindings(plan["sources"])
    shared.images.check_policy()
    digest, size = hashlib.sha256(), 0
    with ARCHIVE.open("rb") as source:
        while block := source.read(4 * 1024 ** 2):
            digest.update(block)
            size += len(block)
    guard(plan)
    if size != plan["archive_identity"][2]:
        raise ValueError("full archive SHA byte count drift")
    write(OUTPUT / "archive_integrity.json", {"archive_sha256": digest.hexdigest(),
          "archive_bytes": size, "file_identity": plan["archive_identity"], "archive_rehashes": 0})
    options = ort.SessionOptions()
    options.intra_op_num_threads = options.inter_op_num_threads = 1
    session = ort.InferenceSession(str(shared.retained.MODEL), sess_options=options, providers=["CPUExecutionProvider"])
    if session.get_providers() != ["CPUExecutionProvider"]:
        raise ValueError("CPU-only provider required")
    cv2.setNumThreads(1)
    rows, media_rows, timings = [], [], []
    started = time.monotonic()
    with zipfile.ZipFile(ARCHIVE) as archive:
        for index, original in enumerate(plan["videos"]):
            guard(plan)
            unit_start = time.monotonic()
            row, media = unit(plan, index, archive, session)
            timings.append(time.monotonic() - unit_start)
            rows.append(row)
            media_rows.append(media)
            budget.publish(IPC / "progress.json", {
                "phase": "processing", "committed": len(rows), "originals": 1680,
                "detector_success": sum(r["detector_status"] == "success" for r in rows),
                "detector_failure": sum(r["detector_status"] == "failed" for r in rows),
                "source_committed": sum(r["role"] is not None for r in rows),
                "test_committed": sum(r["role"] is None for r in rows), "last_unit_seconds": timings[-1]})
            print("SIW291", index, original["official_split"], row["role"], row["detector_status"], flush=True)
            if len(media_rows) >= 3 and all(r["decode_status"] == "failed" for r in media_rows[-3:]):
                raise RuntimeError("three consecutive strict probe failures; inspect precise evidence before further media")
            if len(rows) == len(plan["compatibility_indices"]):
                if any(r["decode_status"] != "decoded" for r in media_rows):
                    raise RuntimeError("compatibility sample has an explicit probe failure; no bulk all-failure processing")
                estimate = max(timings) * (1680 - len(rows)) + 2400
                receipt = {"committed": len(rows), "no_repeat_decode_or_inference": True,
                           "per_unit_seconds": timings, "remaining_upper_estimate_seconds": estimate,
                           "remaining_work_seconds": plan["deadline_unix_seconds"] - time.time(),
                           "containers": dict(Counter(r["container"] for r in media_rows)),
                           "codecs": dict(Counter(r["codec"] for r in media_rows))}
                write(OUTPUT / "compatibility.json", receipt)
                if estimate >= receipt["remaining_work_seconds"]:
                    raise TimeoutError("actual compatibility/resource estimate cannot fit approved envelope")
    findings = shared.exact_checks(media_rows, {r["video_id"]: r for r in plan["videos"]})
    write(OUTPUT / "content_checks.json", {"exact_groups": findings, "forbidden_exact_crossings": 0,
          "participant_identity_verified": False, "near_duplicate_independence_certified": False})
    shared.check_bindings(plan["sources"])
    guard(plan)
    write(OUTPUT / "worker_completion.json", {
        "transactions": len(rows), "video_crc_checked": len(rows),
        "video_payload_bytes": sum(r["byte_size"] for r in media_rows),
        "native_frames": sum(r["frame_count"] for r in media_rows),
        "processing_wall_seconds": time.monotonic() - started,
        "provider": ["CPUExecutionProvider"], "model_scores": 0, "fitted_scores": 0, "evaluation": False})


def verify_probe(index, media):
    folder = OUTPUT / "probe" / f"{index:04d}"
    expected = media["probe_evidence_sha256"]
    if {p.relative_to(OUTPUT).as_posix() for p in folder.iterdir()} != set(expected):
        raise ValueError("exact durable generic probe set required")
    for relative, digest in expected.items():
        if sha(OUTPUT / relative) != digest:
            raise ValueError("probe commitment drift")
    for stem in ("metadata", "framehash"):
        if not (folder / (stem + ".json")).exists():
            if media["decode_status"] == "decoded" or stem == "metadata":
                raise ValueError("required probe command receipt missing")
            continue
        receipt = read(folder / (stem + ".json"))
        if media["decode_status"] == "decoded" and (receipt["returncode"] or receipt["stderr_bytes"]):
            raise ValueError("strict command exit/stderr failure")
        for kind in ("stdout", "stderr"):
            path = folder / (stem + "." + kind)
            if path.stat().st_size != receipt[kind + "_bytes"] or sha(path) != receipt[kind + "_sha256"]:
                raise ValueError("command diagnostic commitment drift")
    saved = read(folder / "result.json")
    if any(media[key] != value for key, value in saved.items()):
        raise ValueError("saved generic probe/media drift")
    if media["decode_status"] == "decoded":
        reparsed = parse_probe(read(folder / "metadata.stdout"), (folder / "framehash.stdout").read_text())
        if reparsed != saved:
            raise ValueError("native generic timestamp/count/RGB reparse drift")
    elif (media["probe_failure"] != read(folder / "failure.json")
          or media["failure_reason"] != media["probe_failure"]["stage"] + ":" + media["probe_failure"]["reason"]
          or media["frame_count"] or media["frame_index"]):
        raise ValueError("exact durable failure reason and no invented decoded frames required")


def verify(plan):
    shared.check_bindings(plan["sources"])
    guard(plan)
    records, assets, manifest, media_rows, replay_count = {}, {}, [], [], 0
    expected = {f"{i:04d}.json" for i in range(1680)}
    for folder in ("transactions", "attempts", "media"):
        if {p.name for p in (OUTPUT / folder).iterdir()} != expected:
            raise ValueError("exact1680 per-original record set required")
    for index, original in enumerate(plan["videos"]):
        row_path, media_path = OUTPUT / "transactions" / f"{index:04d}.json", OUTPUT / "media" / f"{index:04d}.json"
        row, media = read(row_path), read(media_path)
        if any(media[key] != original[key] for key in ("video_id", "role", "binary_label", "official_split", "subject_id", "media_relpath")):
            raise ValueError("frozen/native original join drift")
        header = next(h for h in plan["headers"] if h["path"] == original["media_relpath"])
        if (media["byte_size"] != original["byte_size"] or media["archive_crc_validated"] is not True
                or media["native_crc32"] != f'{header["crc32"]:08x}'):
            raise ValueError("native size/CRC join drift")
        verify_probe(index, media)
        txn = transaction(media)
        txn.update(media_sha256=media["media_sha256"], media_record_sha256=sha(media_path))
        if any(row[key] != value for key, value in txn.items() if key not in {"detector_status", "final_k1_action"}):
            raise ValueError("fixed original transaction drift")
        if txn["selected_frame"] is None:
            if (row["detector_status"] != "not_run" or row["final_k1_action"] != "non_accept" or row["assets"]
                    or "selected_RGB_asset" in row or row["config_sha256"] != plan["active_config_sha256"]
                    or row["model_sha256"] != shared.MODEL_SHA256 or row["index"] != index
                    or row["replacement"] is not False):
                raise ValueError("technical failure must retain denominator without invented images or acceptance")
            entry = {**txn, "asset_sha256": {}, "record_path": str(row_path), "record_sha256": sha(row_path)}
            replay_paths = ()
        else:
            entry, unit_assets = shared.images.validate_unit(
                {"transaction": txn, "media_path": str(media_path)}, OUTPUT, index, 4, plan["active_config_sha256"], sha(row_path))
            assets.update(unit_assets)
            prefix = OUTPUT / "replay" / f"{index:04d}"
            replay = shared.read_verified_json(prefix.with_suffix(".json"), row["replay_record_sha256"])
            error_file = prefix.with_suffix(".stderr")
            if (replay["strict_success"] is not True or replay["returncode"] or replay["stderr_bytes"]
                    or replay["frames_verified"] != media["frame_count"] or replay["frame_count"] != media["frame_count"]
                    or replay["decoded_rgb_sequence_sha256"] != media["decoded_rgb_sequence_sha256"]
                    or replay["frame_substitution"] is not False or replay["failure"] is not None
                    or error_file.stat().st_size or sha(error_file) != replay["stderr_sha256"]):
                raise ValueError("strict full RGB replay receipt mismatch")
            replay_count += 1
            replay_paths = (prefix.with_suffix(".json"), error_file)
        entry.update(index=index, official_split=original["official_split"], subject_id=None,
                     active_config_sha256=plan["active_config_sha256"], replacement=False)
        manifest.append(entry)
        media_rows.append(media)
        for path in (row_path, media_path, OUTPUT / "attempts" / f"{index:04d}.json",
                     *replay_paths, *(OUTPUT / "probe" / f"{index:04d}").iterdir()):
            records[path.relative_to(OUTPUT).as_posix()] = sha(path)
        if index % 20 == 0:
            CLIENT.enforce(CLIENT.measure(os.getpgrp()))
            budget.publish(IPC / "progress.json", {"phase": "readback", "verified": index, "originals": 1680})
            print("READBACK291", index, flush=True)
    if Counter(r["role"] for r in manifest if r["role"] is not None) != ROLES or sum(r["role"] is None for r in manifest) != 623:
        raise ValueError("source/null-test partition drift")
    observed = {p.relative_to(OUTPUT).as_posix() for folder in ("frames", "crops") for p in (OUTPUT / folder).iterdir()}
    if observed != set(assets) or any((OUTPUT / "temporary").iterdir()):
        raise ValueError("exact image set and empty staging required")
    findings = shared.exact_checks(media_rows, {r["video_id"]: r for r in plan["videos"]})
    if findings != read(OUTPUT / "content_checks.json")["exact_groups"]:
        raise ValueError("exact native sequence/boundary findings drift")
    completion = read(OUTPUT / "worker_completion.json")
    required = {"transactions": 1680, "video_crc_checked": 1680,
                "video_payload_bytes": sum(r["byte_size"] for r in media_rows),
                "native_frames": sum(r["frame_count"] for r in media_rows),
                "provider": ["CPUExecutionProvider"], "model_scores": 0, "fitted_scores": 0, "evaluation": False}
    if any(type(completion.get(k)) is not type(v) or completion[k] != v for k, v in required.items()):
        raise ValueError("full worker/native accounting drift")
    integrity = read(OUTPUT / "archive_integrity.json")
    if integrity["file_identity"] != plan["archive_identity"] or integrity["archive_bytes"] != plan["archive_identity"][2]:
        raise ValueError("whole archive identity/hash-byte binding drift")
    sheets = shared.make_sheets(plan, manifest)
    write(OUTPUT / "full_manifest.json", {"dataset": "SiW-Mv2", "rows": manifest, "classifier_scores": False})
    result = {"originals": 1680, "selected": sum(r["selected_frame"] is not None for r in manifest),
              "detector_success": sum(r["detector_status"] == "success" for r in manifest),
              "detector_failure": sum(r["detector_status"] == "failed" for r in manifest),
              "pre_detector_failure": sum(r["selected_frame"] is None for r in manifest),
              "pre_detector_failure_reasons": dict(Counter(r["failure_reason"] for r in media_rows if r["decode_status"] == "failed")),
              "source_originals": 1057, "null_role_test_originals": 623,
              "native_frames": required["native_frames"], "strict_replay_count": replay_count,
              "image_assets": len(assets), "per_unit_sha256": records, "asset_sha256": assets,
              "full_manifest_sha256": sha(OUTPUT / "full_manifest.json"),
              "visual_sheets": sheets, "exact_duplicate_groups": len(findings),
              "forbidden_exact_crossings": 0, "participant_identity_verified": False,
              "model_scores": 0, "fitted_scores": 0, "evaluation": False, "scientific_readiness": False}
    write(OUTPUT / "readback.json", result)
    return result


def supervise(plan):
    binding = {"parent_pid": os.getpid(), "plan_sha256": sha(OUTPUT / "plan.json")}
    write(OUTPUT / "lease.json", binding)
    budget.initialize(IPC, binding)
    scanner = subprocess.Popen([sys.executable, str(Path(__file__)), "--scan"], start_new_session=True)
    budget.publish(IPC / "processes.json", {"scanner_pid": scanner.pid})
    client = budget.Client(IPC, binding, usage, enforce)
    process, failure, readback = None, None, None
    peaks = {"rss_bytes": 0, "temporary_bytes": 0, "output_bytes": 0}
    try:
        while not (IPC / "snapshot.json").exists():
            if scanner.poll() is not None:
                raise RuntimeError("native scanner failed at startup")
            enforce({"rss_bytes": 0, "output_bytes": 0})
            time.sleep(0.1)
        samples = []
        for _ in range(50):
            start = time.monotonic()
            value = client.measure(os.getpgrp())
            samples.append(time.monotonic() - start)
            enforce(value)
        p95, maximum = sorted(samples)[47], max(samples)
        write(OUTPUT / "observer_preflight.json", {"samples": 50, "p95_seconds": p95,
              "maximum_seconds": maximum, "native_ipc": True, "initial_accounted_bytes": value["output_bytes"]})
        if p95 >= 0.050 or maximum >= 0.250:
            raise RuntimeError("actual populated-root foreground latency threshold failed")
        for mode in ("--worker", "--verify"):
            process = subprocess.Popen([sys.executable, str(Path(__file__)), mode], start_new_session=True)
            while True:
                if scanner.poll() is not None:
                    raise RuntimeError("native scanner exited")
                value = client.measure(process.pid)
                peaks = {key: max(peaks[key], value[key]) for key in peaks}
                enforce(value)
                try:
                    if process.wait(timeout=0.5):
                        raise RuntimeError(mode + " failed; exact evidence retained, no automatic retry")
                    break
                except subprocess.TimeoutExpired:
                    continue
            process = None
        readback = read(OUTPUT / "readback.json")
        guard(plan)
        shared.check_bindings(plan["sources"])
    except Exception as error:
        failure = type(error).__name__ + ": " + str(error)
        print("SIW291_STOP", failure, flush=True)
    finally:
        for child in (process, scanner):
            if child is not None:
                budget.stop_group(child)
        signal.setitimer(signal.ITIMER_REAL, 0)
        shared.retained.arm_deadline(authority()["deadline_unix_seconds"])
        try:
            for path in (OUTPUT / "temporary").iterdir():
                if path.name not in {"current.avi", "current.mov", "current.mp4"} or not path.is_file() or path.is_symlink():
                    raise ValueError("unexpected owned staging entry; refuse broad cleanup")
                path.unlink()
        except Exception as error:
            failure = (failure + "; " if failure else "") + type(error).__name__ + ": " + str(error)
    if failure is None:
        try:
            budget.scan_once(ROOTS, IPC, binding, shared.retained.tree_bytes)
            value = client.measure(os.getpgrp())
            peaks = {key: max(peaks[key], value[key]) for key in peaks}
            enforce(value, work=False)
        except Exception as error:
            failure = type(error).__name__ + ": " + str(error)
    if failure is not None:
        ledger = []
        for index, original in enumerate(plan["videos"]):
            committed = (OUTPUT / "transactions" / f"{index:04d}.json").exists()
            started = (OUTPUT / "attempts" / f"{index:04d}.json").exists()
            ledger.append({"index": index, "video_id": original["video_id"], "role": original["role"],
                           "binary_label": original["binary_label"], "official_split": original["official_split"],
                           "status": "committed" if committed else "interrupted_before_commit" if started else "not_started"})
        write(OUTPUT / "failure_rows.json", {"originals": 1680, "rows": ledger, "failure": failure,
              "status_counts": dict(Counter(r["status"] for r in ledger)), "automatic_retry": False})
    result = {"checkpoint": 291, "dataset": "SiW-Mv2", "failure": failure,
              "accounting_complete": failure is None and readback is not None,
              "image_export_software_complete": failure is None and readback is not None and readback["detector_success"] > 0,
              "primary_image_preprocessing_complete": False, "local_audit_complete": False,
              "originals": 1680, "source_originals": 1057, "null_role_test_originals": 623,
              "excluded_videos_not_processed": plan["excluded_originals"], "missing_references_not_invented": plan["missing_references"],
              "package_wall_seconds": time.time() - authority()["started_unix_seconds"],
              "caps": CAPS, "sampled_peaks": peaks, "automatic_retry": False, "attempts": 1,
              **{key: readback[key] if readback else None for key in
                 ("selected", "detector_success", "detector_failure", "pre_detector_failure",
                  "native_frames", "strict_replay_count", "image_assets")},
              "gpu_seconds": 0, "model_scores": 0, "fitted_scores": 0, "evaluation": False,
              "participant_identity_verified": False, "scientific_readiness": False}
    if failure:
        result["specific_probe_failures"] = [read(path) for path in sorted((OUTPUT / "probe").glob("*/failure.json"))]
    write(OUTPUT / "resources.json", result)
    write(SUMMARY, {**result, "private_record_sha256": {p.name: sha(p) for p in OUTPUT.glob("*.json")}})
    print("SIW291_TERMINAL", json.dumps(result), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    for mode in ("prepare", "run-once", "scan", "worker", "verify"):
        modes.add_argument("--" + mode, action="store_true")
    args = parser.parse_args()
    shared.retained.arm_deadline(authority()["work_deadline_unix_seconds"])
    if args.prepare:
        prepare()
        return 0
    plan = read(OUTPUT / "plan.json")
    if args.scan or args.worker or args.verify:
        lease = read(OUTPUT / "lease.json")
        if (lease["parent_pid"] != os.getppid() or lease["plan_sha256"] != sha(OUTPUT / "plan.json")
                or os.getsid(0) != os.getpid()):
            raise ValueError("single supervised leased child required")
        if args.scan:
            budget.scan_forever(ROOTS, IPC, lease, shared.retained.tree_bytes)
        else:
            client = budget.Client(IPC, lease, usage, enforce)
            configure(client)
            worker(plan) if args.worker else verify(plan)
        return 0
    write(OUTPUT / "supervisor.json", {"pid": os.getpid(), "source_sha256": sha(Path(__file__))})
    with (OUTPUT / "execution.log").open("xb", buffering=0) as log:
        os.dup2(log.fileno(), 1)
        os.dup2(log.fileno(), 2)
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    return 0 if supervise(plan)["accounting_complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
