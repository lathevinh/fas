"""One approved fixed-original CASIA probe diagnosis, with bounded raw evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import os
import signal
import subprocess
import sys
import time
from unittest.mock import patch
import zlib

import preprocess_casia285 as prior
from fas.media import probe_video

OUTPUT = prior.BASE / "casia_recovery287_v1"
CAPS = {"wall_seconds": 7200, "rss_bytes": 4 * 1024 ** 3,
        "output_bytes": 32 * 1024 ** 3, "gpu_seconds": 0}


def authority():
    row = prior.read(OUTPUT / "owner_approval.json")
    if row["selected_answer"] != "approve_combined_casia287" or row["explicit_owner_approval"] is not True or row["caps"] != CAPS:
        raise ValueError("new combined CASIA287 authority required")
    if row["deadline_unix_seconds"] != row["started_unix_seconds"] + CAPS["wall_seconds"]:
        raise ValueError("combined two-hour clock may not be reset")
    if row["review286_sha256"] != prior.sha(prior.ROOT / "docs/286-review-doc285-casia-systematic-probe-blocker.md"):
        raise ValueError("review286 authority drift")
    return row


def measured(group):
    value = prior.measured(group)
    value["output_bytes"] += prior.shared.retained.tree_bytes(OUTPUT)
    return value


def enforce(value):
    if time.time() >= authority()["deadline_unix_seconds"]:
        raise TimeoutError("combined two-hour CASIA287 deadline")
    if value["rss_bytes"] > CAPS["rss_bytes"]:
        raise MemoryError("combined4GiB process-group RSS cap")
    if value["output_bytes"] > CAPS["output_bytes"] - prior.shared.RESERVE:
        raise OSError("combined32GiB retained/temporary artifact cap")


def capture(command, prefix, *, stdout_cap=16 * 1024 ** 2, timeout=180):
    stdout_path, stderr_path = prefix.with_suffix(".stdout"), prefix.with_suffix(".stderr")
    prefix.parent.mkdir(parents=True, exist_ok=True)
    process = None
    started = time.monotonic()
    peaks = {"rss_bytes": 0, "output_bytes": 0, "temporary_bytes": 0}
    try:
        with stdout_path.open("xb") as out, stderr_path.open("xb") as err:
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=out, stderr=err, start_new_session=True)
            while True:
                value = measured(process.pid)
                peaks = {key: max(peaks[key], value[key]) for key in peaks}
                enforce(value)
                if stdout_path.stat().st_size > stdout_cap or stderr_path.stat().st_size > 1024 ** 2:
                    raise OSError("bounded diagnostic stdout/stderr cap")
                if time.monotonic() - started >= timeout:
                    raise TimeoutError("single diagnostic command timeout")
                try:
                    returncode = process.wait(timeout=0.2)
                    break
                except subprocess.TimeoutExpired:
                    continue
        record = {
            "command": command, "returncode": returncode, "wall_seconds": time.monotonic() - started,
            "stdout_bytes": stdout_path.stat().st_size, "stderr_bytes": stderr_path.stat().st_size,
            "stdout_sha256": prior.sha(stdout_path), "stderr_sha256": prior.sha(stderr_path),
            "sampled_peaks": peaks}
        prior.write(prefix.with_suffix(".json"), record)
        return record, stdout_path.read_bytes(), stderr_path.read_bytes()
    finally:
        if process is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()


def bound_prior():
    plan = prior.read(prior.OUTPUT / "plan.json")
    report = prior.read(prior.ROOT / "results/phase1/casia-preprocessing285-v1.json")
    for name, expected in report["private_record_sha256"].items():
        if prior.sha(prior.OUTPUT / name) != expected:
            raise ValueError("retained285 terminal commitment drift")
    prior.shared.check_bindings(plan["sources"])
    prior.guard(plan)
    if prior.list_headers() != plan["headers"] or prior.read_file_headers(prior.ARCHIVE) != plan["crc_headers"]:
        raise ValueError("original typed/CRC header drift")
    return plan


def diagnose():
    approval = authority()
    prior.shared.retained.arm_deadline(approval["deadline_unix_seconds"])
    if (OUTPUT / "diagnosis_started.json").exists():
        raise FileExistsError("fixed diagnostic already attempted; no automatic retry")
    prior.write(OUTPUT / "diagnosis_started.json", {"pid": os.getpid(), "source_sha256": prior.sha(Path(__file__))})
    plan = bound_prior()
    original = plan["videos"][approval["diagnostic_original_index"]]
    old_media = prior.read(prior.OUTPUT / "media/0000.json")
    if original["video_id"] != old_media["video_id"] or old_media["decode_status"] != "failed":
        raise ValueError("fixed first failed original only")
    prefix = OUTPUT / "diagnostic/extraction"
    extraction, payload, errors = capture(
        [str(prior.EXTRACTOR), "-xOf", str(prior.ARCHIVE), original["media_relpath"]],
        prefix, stdout_cap=original["byte_size"], timeout=120)
    pin = prior.read(prior.OUTPUT / "release_integrity.json")["video_payload_pins"][original["media_relpath"]]
    if extraction["returncode"] or errors or len(payload) != pin["byte_size"] or zlib.crc32(payload) != pin["crc32"] or hashlib.sha256(payload).hexdigest() != pin["sha256"] or pin["sha256"] != old_media["media_sha256"]:
        raise ValueError("fixed diagnostic original CRC/size/SHA mismatch")
    path = prefix.with_suffix(".stdout")
    calls, exceptions = [], []

    def recording_run(command, *, capture_output, text, timeout, check):
        if not capture_output or not text or check or command[0] not in {"ffprobe", "ffmpeg"}:
            raise ValueError("unexpected legacy probe command")
        name = "ffprobe" if command[0] == "ffprobe" else "framehash"
        record, stdout, stderr = capture(command, OUTPUT / "diagnostic" / name, timeout=timeout)
        calls.append(record)
        return subprocess.CompletedProcess(command, record["returncode"], stdout.decode("utf-8"), stderr.decode("utf-8"))

    def trace(frame, event, arg):
        if frame.f_code is probe_video.__code__ and event == "exception":
            kind, error, _ = arg
            local = frame.f_locals
            exceptions.append({
                "exception_type": kind.__name__, "message": str(error), "line": frame.f_lineno,
                "frame_order": local.get("order"), "parsed_frame_count": len(local.get("index", [])),
                "failing_frame_metadata": local.get("frame"),
                "declared_frame_count": local.get("stream", {}).get("nb_frames")})
        return trace

    previous_trace = sys.gettrace()
    try:
        sys.settrace(trace)
        with patch("fas.media.subprocess.run", side_effect=recording_run):
            result = probe_video(path, timeout_seconds=180)
    finally:
        sys.settrace(previous_trace)
    if not any(record["command"][0] == "ffmpeg" for record in calls):
        record, _, _ = capture(
            ["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-err_detect", "explode",
             "-threads", "1", "-i", str(path), "-map", "0:v:0", "-an", "-sn", "-dn",
             "-pix_fmt", "rgb24", "-threads", "1", "-vsync", "0", "-f", "framehash", "-hash", "sha256", "-"],
            OUTPUT / "diagnostic/framehash", timeout=180)
        calls.append(record)
    prior.guard(plan)
    diagnosis = {
        "checkpoint": 287, "fixed_original_index": 0, "original": original,
        "original_payload_pin": pin, "prior_media_record_sha256": prior.sha(prior.OUTPUT / "media/0000.json"),
        "prior_plan_sha256": prior.sha(prior.OUTPUT / "plan.json"),
        "source_sha256": prior.sha(Path(__file__)), "legacy_probe_source_sha256": prior.sha(prior.ROOT / "src/fas/media.py"),
        "legacy_result": result, "exceptions": exceptions, "commands": calls,
        "archive_sha_reused_under_exact_identity_and_current_header_crc_guards": True,
        "archive_rehashed": False, "new_inference": False, "accounting_complete": False,
        "primary_image_preprocessing_complete": False}
    prior.write(OUTPUT / "diagnosis.json", diagnosis)
    print(json.dumps({"legacy_failure": result["failure_reason"], "exceptions": exceptions,
                      "commands": [{key: record[key] for key in ("returncode", "stdout_bytes", "stderr_bytes")}
                                   for record in calls]}, indent=2))


if __name__ == "__main__":
    diagnose()
