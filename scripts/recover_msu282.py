"""Finish one additionally authorized MSU recovery without rewriting the failed attempt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import zipfile

import diagnose_msu282_recovery as diagnostic
import preprocess_msu282 as job
from fas.transactions import technical_transaction

PRIOR = diagnostic.PRIOR
OUTPUT = diagnostic.OUTPUT
SUMMARY = job.ROOT / "results/phase1/msu-preprocessing282-recovery-v1.json"


def measured(group):
    result = job.measured_usage(group)
    result["output_bytes"] += job.retained.tree_bytes(PRIOR)
    return result


def make_plan():
    authority = diagnostic.authority()
    plan = diagnostic.bound_plan()
    if job.read_json(OUTPUT / "diagnosis_resources.json")["diagnosis_completed"] is not True:
        raise ValueError("captured diagnosis must finish before one recovery execution")
    diagnosis = job.read_json(OUTPUT / "diagnosis.json")
    validation = job.read_json(OUTPUT / "fix_validation.json")
    fixed_receipt = job.read_verified_json(OUTPUT / "diagnostics/fixed-rawvideo.json", validation["replay_receipt_sha256"])
    if diagnosis["returncode"] != 0 or diagnosis["stderr_bytes"] <= 0 or job._sha256(OUTPUT / "diagnostics/original-rawvideo.stderr") != diagnosis["stderr_sha256"]:
        raise ValueError("exact captured rawvideo diagnostic required")
    if validation["replay_helper_sha256"] != job._sha256(job.ROOT / "scripts/msu_replay282.py") or validation["frozen_middle_RGB_unchanged"] is not True or validation["source_timebase_preserved"] is not True:
        raise ValueError("validated fixed helper and unchanged middle RGB required")
    if fixed_receipt["strict_success"] is not True or fixed_receipt["returncode"] != 0 or fixed_receipt["stderr_bytes"] != 0 or fixed_receipt["frames_verified"] != diagnosis["native_frame_count"]:
        raise ValueError("all native frames must pass fixed strict replay before recovery")
    sources = dict(plan["sources"])
    for path in (
        Path(__file__), Path(diagnostic.__file__), job.ROOT / "scripts/msu_replay282.py",
        job.ROOT / "tests/test_msu_recovery.py",
        OUTPUT / "owner_approval.json", OUTPUT / "stage.json", OUTPUT / "diagnosis.json",
        OUTPUT / "diagnosis_resources.json", OUTPUT / "diagnostics/original-rawvideo.stderr",
        OUTPUT / "fix_validation.json", OUTPUT / "diagnostics/fixed-rawvideo.json", OUTPUT / "diagnostics/fixed-rawvideo.stderr",
        PRIOR / "failure_rows.json", PRIOR / "release_integrity.json", PRIOR / "resources.json",
    ):
        sources[str(path)] = job._sha256(path)
    prior_failure = job.read_json(PRIOR / "failure_rows.json")["rows"]
    for index in range(4):
        record_path = PRIOR / "transactions" / f"{index:04d}.json"
        if job._sha256(record_path) != prior_failure[index]["record_sha256"]:
            raise ValueError("prior provisional transaction differs from terminal failure accounting")
        row = job.read_json(record_path)
        if row["detector_status"] != "success":
            raise ValueError("exact four provisional successes required for reuse")
        for relative in (f"transactions/{index:04d}.json", f"media/{index:04d}.json", f"attempts/{index:04d}.json",
                         row["selected_RGB_asset"]["path"], *row["assets"]):
            path = PRIOR / relative
            sources[str(path)] = job._sha256(path)
    plan.update(
        sources=sources, deadline_unix_seconds=authority["deadline_unix_seconds"],
        recovery_of_failed282=True, reused_indices=[0, 1, 2, 3], remaining_new_attempts=276,
        prior_plan_sha256=authority["prior_plan_sha256"],
        storage_scope="total274_276_278_280_failed282_recovery282_including_temporary_zip")
    job.check_bindings(sources)
    job.enforce(plan, measured(os.getpgrp()))
    job.write_immutable_record(OUTPUT / "plan.json", plan)
    return plan


def reuse_unit(plan, index):
    media_path = PRIOR / "media" / f"{index:04d}.json"
    media = job.read_json(media_path)
    transaction = technical_transaction(media)
    transaction.update(media_sha256=media["media_sha256"], media_record_sha256=job._sha256(media_path))
    entry, assets = job.images.validate_unit(
        {"transaction": transaction, "media_path": str(media_path)},
        PRIOR, index, 4, plan["active_config_sha256"])
    row = job.read_json(PRIOR / "transactions" / f"{index:04d}.json")
    if entry["video_id"] != plan["videos"][index]["video_id"]:
        raise ValueError("reused selected original identity drift")
    for relative in (f"transactions/{index:04d}.json", f"media/{index:04d}.json", f"attempts/{index:04d}.json", *assets):
        source, target = PRIOR / relative, OUTPUT / relative
        expected = plan["sources"][str(source)]
        target.parent.mkdir(parents=True, exist_ok=True)
        with source.open("rb") as reader, target.open("xb") as writer:
            receipt = job.checked_copy(reader, writer, job.identity(source)[2], deadline=plan["deadline_unix_seconds"])
        if receipt["sha256"] != expected:
            raise ValueError("provisional source/copy SHA drift")
    return row, media


def produce_unit(plan, index, original, inner, session):
    from msu_replay282 import strict_replay

    if original["role"] not in job.EXPECTED_ROLES or original["dataset"] != "MSU-MFSD":
        raise ValueError("frozen MSU source population only")
    entry = inner.getinfo(original["media_relpath"])
    job.native.safe_entry(entry)
    if job.native.header_record(entry) != original["archive_header"] or entry.file_size > 128 * 1024 ** 2:
        raise ValueError("canonical video header/byte cap drift")
    job.write_immutable_record(OUTPUT / "attempts" / f"{index:04d}.json", {
        "index": index, "status": "started", "video_id": original["video_id"], "role": original["role"],
        "single_additionally_authorized_recovery": True})
    path = OUTPUT / "temporary" / ("selected" + Path(original["media_relpath"]).suffix)
    try:
        with inner.open(entry) as source, path.open("xb") as target:
            payload = job.checked_copy(source, target, entry.file_size, deadline=plan["deadline_unix_seconds"])
        media = {key: original[key] for key in ("video_id", "role", "binary_label", "official_split", "subject_id", "media_relpath")}
        remaining = max(1, min(180, int(plan["deadline_unix_seconds"] - time.time())))
        media.update(media_sha256=payload["sha256"], byte_size=payload["byte_size"],
                     inner_crc_checked_to_eof=True, **job.probe_video(path, timeout_seconds=remaining))
        media_path = OUTPUT / "media" / f"{index:04d}.json"
        job.write_immutable_record(media_path, media)
        transaction = technical_transaction(media)
        transaction.update(media_sha256=media["media_sha256"], media_record_sha256=job._sha256(media_path))
        row = {**transaction, "index": index, "replacement": False, "model_sha256": job.MODEL_SHA256,
               "config_sha256": plan["active_config_sha256"], "assets": {}}
        if transaction["selected_frame"] is not None:
            selected = transaction["selected_frame"]
            captured = []

            def consume(order, rgb):
                if order == selected["decode_order"]:
                    if hashlib.sha256(rgb.tobytes()).hexdigest() != selected["rgb_sha256"]:
                        raise ValueError("frozen selected RGB changed")
                    captured.append(rgb.copy())

            strict_replay(path, media, consume, OUTPUT / "replay" / f"{index:04d}",
                          timeout=min(180, max(0.001, plan["deadline_unix_seconds"] - time.time())))
            row["replay_record_sha256"] = job._sha256(OUTPUT / "replay" / f"{index:04d}.json")
            if len(captured) != 1:
                raise ValueError("one frozen middle frame only; no replacement")
            relative = f"frames/{index:04d}.png"
            row["selected_RGB_asset"] = {"path": relative, **job.write_png(relative, captured[0])}
            job.infer_image(session, captured[0], row)
        job.write_immutable_record(OUTPUT / "transactions" / f"{index:04d}.json", row)
        return row, media
    finally:
        if path.exists():
            path.unlink()


def worker(plan):
    import cv2
    import onnxruntime as ort

    job.check_bindings(plan["sources"])
    job.images.check_policy()
    if job._sha256(job.retained.MODEL) != job.MODEL_SHA256:
        raise ValueError("reused model drift")
    job.archive_guard(plan)
    joined = OUTPUT / "temporary/MSU-MFSD-Publish.zip"
    try:
        with zipfile.ZipFile(joined) as inner:
            if [job.native.header_record(entry) for entry in inner.infolist()] != plan["inner_headers"]:
                raise ValueError("recovery staged ZIP header drift")
            job.write_immutable_record(OUTPUT / "release_integrity.json", {
                **job.read_json(PRIOR / "release_integrity.json"),
                "recovery_stage_sha256": job._sha256(OUTPUT / "stage.json"),
                "archive_hashes_reused_with_exact_identity_guard": True})
            options = ort.SessionOptions()
            options.intra_op_num_threads = options.inter_op_num_threads = 1
            session = ort.InferenceSession(str(job.retained.MODEL), sess_options=options, providers=["CPUExecutionProvider"])
            if session.get_providers() != ["CPUExecutionProvider"]:
                raise ValueError("CPU-only inference required")
            cv2.setNumThreads(1)
            video_paths = {row["media_relpath"] for row in plan["videos"]}
            auxiliary, media_rows = {}, []
            for entry in inner.infolist():
                job.native.safe_entry(entry)
                if entry.is_dir() or entry.filename in video_paths:
                    continue
                digest, count = hashlib.sha256(), 0
                with inner.open(entry) as source:
                    while block := source.read(1024 ** 2):
                        count += len(block)
                        if count > entry.file_size or time.time() >= plan["deadline_unix_seconds"]:
                            raise TimeoutError("ancillary CRC/size deadline")
                        digest.update(block)
                if count != entry.file_size:
                    raise ValueError("short native ancillary entry")
                auxiliary[entry.filename] = {"sha256": digest.hexdigest(), "byte_size": count, "crc_checked_to_eof": True}
            for index, original in enumerate(plan["videos"]):
                job.archive_guard(plan)
                row, media = reuse_unit(plan, index) if index < 4 else produce_unit(plan, index, original, inner, session)
                media_rows.append(media)
                print("MSU282", index, row["role"], row["detector_status"], "reused" if index < 4 else "new", flush=True)
        findings = job.exact_checks(media_rows, {row["video_id"]: row for row in plan["videos"]})
        job.write_immutable_record(OUTPUT / "content_checks.json", {
            "exact_groups": findings, "forbidden_exact_crossings": 0,
            "near_duplicate_independence_certified": False, "joined_cross_dataset_ancestry_certified": False,
            "known_parent_evidence": "native_same_subject_attack_construction_preserved_not_independent_capture_claim"})
        job.check_bindings(plan["sources"])
        job.archive_guard(plan)
        job.write_immutable_record(OUTPUT / "worker_completion.json", {
            "transactions": len(media_rows), "media_crc_checked": len(media_rows),
            "native_frames": sum(row["frame_count"] for row in media_rows),
            "selected_payload_bytes": sum(row["byte_size"] for row in media_rows),
            "ancillary_entries": auxiliary, "provider": ["CPUExecutionProvider"],
            "gpu_seconds": 0, "model_scores": 0, "fitted_scores": 0,
            "reused_after_pixel_readback": 4, "new_attempts": 276})
    finally:
        if joined.exists():
            joined.unlink()


def verify(plan):
    records = {}
    expected = set()
    for index in range(4, 280):
        row = job.read_json(OUTPUT / "transactions" / f"{index:04d}.json")
        if row["selected_frame"] is None:
            continue
        relative = f"replay/{index:04d}.json"
        errors = f"replay/{index:04d}.stderr"
        expected.update((relative, errors))
        replay = job.read_verified_json(OUTPUT / relative, row["replay_record_sha256"])
        media = job.read_json(OUTPUT / "media" / f"{index:04d}.json")
        if replay["strict_success"] is not True or replay["frames_verified"] != media["frame_count"] or replay["frame_count"] != media["frame_count"] or replay["decoded_rgb_sequence_sha256"] != media["decoded_rgb_sequence_sha256"]:
            raise ValueError("every new selected frame requires strict complete decoded-RGB replay")
        if replay["returncode"] != 0 or replay["stderr_bytes"] != 0 or replay["failure"] is not None or replay["frame_substitution"] is not False:
            raise ValueError("strict replay exit/stderr/fixed-frame accounting drift")
        if job._sha256(OUTPUT / errors) != replay["stderr_sha256"] or (OUTPUT / errors).stat().st_size:
            raise ValueError("preserved replay stderr drift")
        records[relative], records[errors] = job._sha256(OUTPUT / relative), job._sha256(OUTPUT / errors)
    actual = {path.relative_to(OUTPUT).as_posix() for path in (OUTPUT / "replay").glob("*")}
    if actual != expected:
        raise ValueError("exact new replay record/diagnostic population required")
    result = job.verify(plan)
    job.write_immutable_record(OUTPUT / "replay_readback.json", {
        "record_sha256": records, "strict_replay_count": len(expected) // 2,
        "full_readback_sha256": job._sha256(OUTPUT / "readback.json"),
        "reused_after_pixel_readback": 4, "scientific_readiness": False})
    return result


def supervise(plan):
    job.write_immutable_record(OUTPUT / "attempt_lock.json", {
        "plan_sha256": job._sha256(OUTPUT / "plan.json"), "parent_pid": os.getpid(),
        "attempts_authorized": 1, "automatic_retry": False})
    process, failure, readback = None, None, None
    diagnostic_peaks = job.read_json(OUTPUT / "diagnosis_resources.json")["sampled_peaks"]
    peaks = dict(diagnostic_peaks)
    started = time.monotonic()
    try:
        for mode in ("--worker", "--verify"):
            process = subprocess.Popen([sys.executable, str(Path(__file__)), mode], start_new_session=True)
            while True:
                value = measured(process.pid)
                peaks = {key: max(peaks[key], value[key]) for key in peaks}
                job.enforce(plan, value)
                try:
                    if process.wait(timeout=2):
                        raise RuntimeError(mode + " failed; no further retry")
                    break
                except subprocess.TimeoutExpired:
                    continue
            process = None
        readback = job.read_json(OUTPUT / "readback.json")
        replay_readback = job.read_json(OUTPUT / "replay_readback.json")
        for relative, digest in replay_readback["record_sha256"].items():
            if job._sha256(OUTPUT / relative) != digest:
                raise ValueError("final replay receipt/diagnostic drift")
        manifest = job.read_verified_json(OUTPUT / "full_manifest.json", readback["full_manifest_sha256"])
        if any(readback[key] != value for key, value in job.validate_manifest(plan, manifest["rows"]).items()):
            raise ValueError("final full280 count mismatch")
        for relative, digest in readback["per_unit_sha256"].items():
            if job._sha256(OUTPUT / relative) != digest:
                raise ValueError("final per-unit record drift")
        for name in ("release_integrity", "content_checks"):
            job.read_verified_json(OUTPUT / (name + ".json"), readback[name + "_sha256"])
        if manifest["active_config_sha256"] != job._sha256(job.images.ACTIVE):
            raise ValueError("final active-policy drift")
        job.check_bindings(plan["sources"])
        job.archive_guard(plan)
        final = measured(os.getpgrp())
        final["rss_bytes"] = max(final["rss_bytes"], resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024)
        peaks = {key: max(peaks[key], final[key]) for key in peaks}
        job.enforce(plan, peaks)
    except Exception as error:
        failure = type(error).__name__ + ": " + str(error)
        print("MSU282_RECOVERY_FAILED", failure, flush=True)
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
        job.failure_rows(plan, failure)
    result = {
        "checkpoint": 282, "recovery": True, "completion_claimed": failure is None and readback is not None,
        "failure": failure, "caps": job.CAPS, "sampled_peaks": peaks,
        "package_wall_seconds": time.time() - diagnostic.authority()["started_unix_seconds"],
        "supervised_wall_seconds": time.monotonic() - started,
        "readback_sha256": job._sha256(OUTPUT / "readback.json") if readback else None,
        "attempts": 1, "automatic_retry": False, "gpu_seconds": 0,
        "visual_inspection_pending": failure is None, "scientific_readiness": False}
    job.write_immutable_record(OUTPUT / "resources.json", result)
    if job.read_json(OUTPUT / "resources.json") != result:
        raise ValueError("terminal resources readback drift")
    print("MSU282_RECOVERY_TERMINAL", json.dumps(result), flush=True)
    return result


def publish(result):
    readback = job.read_json(OUTPUT / "readback.json") if result["completion_claimed"] else None
    job.write_immutable_record(SUMMARY, {
        **result, "dataset": "MSU-MFSD", "originals": 280, "subjects": 35,
        "status": "software_complete_visual_review_pending" if result["completion_claimed"] else "recovery_stopped_no_further_retry",
        "visual_inspection_completed": False, "role_originals": job.EXPECTED_ROLES,
        "role_subjects": job.EXPECTED_GROUPS, "reused_outputs": 4, "new_attempts_scope": 276,
        **{key: readback[key] if readback else None for key in (
            "selected", "pre_detector_failure", "detector_success", "detector_failure", "native_frames",
            "selected_payload_bytes", "exact_duplicate_groups", "forbidden_exact_crossings")},
        "model_scores": 0, "fitted_scores": 0, "target_access": False, "model_downloads": 0,
        "active_config_sha256": job._sha256(job.images.ACTIVE),
        "audit_summary_statuses_changed": False, "near_duplicate_independence_certified": False,
        "prior_failed_attempt_preserved": True,
        "private_record_sha256": {name: job._sha256(OUTPUT / name) for name in (
            "owner_approval.json", "stage.json", "diagnosis.json", "diagnosis_resources.json",
            "fix_validation.json",
            "plan.json", "supervisor.json", "attempt_lock.json", "release_integrity.json", "content_checks.json",
            "worker_completion.json", "full_manifest.json", "readback.json", "replay_readback.json", "resources.json")
            if (OUTPUT / name).exists()}})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    for name in ("run-once", "worker", "verify"):
        mode.add_argument("--" + name, action="store_true")
    args = parser.parse_args()
    job.OUTPUT = OUTPUT
    if args.worker or args.verify:
        plan = job.child_plan()
        worker(plan) if args.worker else verify(plan)
        return 0
    if (OUTPUT / "supervisor.json").exists() or (OUTPUT / "resources.json").exists():
        raise FileExistsError("one additionally authorized recovery only; no retry")
    diagnostic.authority()
    job.write_immutable_record(OUTPUT / "supervisor.json", {
        "pid": os.getpid(), "started_unix_seconds": time.time(),
        "runner_sha256": job._sha256(Path(__file__)), "automatic_retry": False})
    with (OUTPUT / "execution.log").open("xb", buffering=0) as log:
        os.dup2(log.fileno(), 1)
        os.dup2(log.fileno(), 2)
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    job.retained.arm_deadline(diagnostic.authority()["deadline_unix_seconds"])
    try:
        plan = make_plan()
        result = supervise(plan)
        publish(result)
        return 0 if result["completion_claimed"] else 1
    except Exception as error:
        job.write_immutable_record(OUTPUT / "package_failure.json", {
            "error_type": type(error).__name__, "message": str(error),
            "automatic_retry": False, "scientific_readiness": False})
        for name in ("MSU-MFSD-Publish.zip", "selected.mp4", "selected.mov"):
            path = OUTPUT / "temporary" / name
            if path.exists():
                path.unlink()
        raise


if __name__ == "__main__":
    raise SystemExit(main())
