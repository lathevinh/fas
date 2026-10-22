"""One newly authorized MSU282 recovery: preserve originals and capture decoder evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import zipfile

import preprocess_msu282 as job

PRIOR = job.OUTPUT
OUTPUT = job.BASE / "msu_recovery282_v1"
APPROVAL = (
    "Đồng ý trọn gói chẩn đoán/sửa/test + một lượt khôi phục MSU như trên, "
    "CPU-only 4 giờ/4 GiB/40 GiB; giữ bằng chứng cũ, không retry thêm"
)


def measured(group):
    value = job.measured_usage(group)
    value["output_bytes"] += job.retained.tree_bytes(OUTPUT)
    return value


def authority():
    row = job.read_json(OUTPUT / "owner_approval.json")
    if row["selected_answer"] != APPROVAL or row["caps"] != job.CAPS or row["explicit_owner_approval"] is not True:
        raise ValueError("exact additional recovery authority required")
    return row


def bound_plan():
    row = authority()
    plan = job.read_json(PRIOR / "plan.json")
    if job._sha256(PRIOR / "plan.json") != row["prior_plan_sha256"] or job._sha256(PRIOR / "resources.json") != row["prior_resources_sha256"]:
        raise ValueError("prior failed attempt commitment drift")
    job.check_bindings(plan["sources"])
    job.archive_guard(plan)
    return {**plan, "deadline_unix_seconds": row["deadline_unix_seconds"]}


def stage(plan):
    previous = job.read_json(PRIOR / "release_integrity.json")
    volumes = {}
    for record in plan["outer_headers"]:
        with zipfile.ZipFile(job.INPUT / record["archive"]) as archive:
            if [job.native.header_record(entry) for entry in archive.infolist()] != record["headers"]:
                raise ValueError("prior outer header drift")
            for entry in archive.infolist():
                job.native.safe_entry(entry)
                if ".zip." in entry.filename:
                    number = int(entry.filename.rsplit(".", 1)[1])
                    if number in volumes:
                        raise ValueError("duplicate split volume")
                    volumes[number] = (record["archive"], entry.filename, entry.file_size)
    if set(volumes) != set(range(1, 17)):
        raise ValueError("exact16 volumes required")
    temporary = OUTPUT / "temporary"
    temporary.mkdir()
    joined = temporary / "MSU-MFSD-Publish.zip"
    rows = []
    with joined.open("xb") as target:
        for number, (name, member, size) in sorted(volumes.items()):
            with zipfile.ZipFile(job.INPUT / name) as archive, archive.open(member) as source:
                digest = job.checked_copy(source, target, size, deadline=plan["deadline_unix_seconds"])
            old = previous["volumes"][number - 1]
            if old["volume"] != number or old["sha256"] != digest["sha256"] or old["byte_size"] != size:
                raise ValueError("prior split-volume SHA/size drift")
            rows.append({"volume": number, **digest, "outer_crc_checked_to_eof": True})
            print("RECOVERY282_VOLUME", number, flush=True)
    if joined.stat().st_size != previous["joined_zip_bytes"]:
        raise ValueError("prior joined ZIP byte count drift")
    with zipfile.ZipFile(joined) as inner:
        if [job.native.header_record(entry) for entry in inner.infolist()] != plan["inner_headers"]:
            raise ValueError("prior inner header drift")
        for name, expected in job.METADATA_SHA256.items():
            if hashlib.sha256(inner.read(name)).hexdigest() != expected:
                raise ValueError("native metadata SHA drift")
    job.archive_guard(plan)
    job.write_immutable_record(OUTPUT / "stage.json", {
        "volumes": rows, "joined_zip_bytes": joined.stat().st_size,
        "prior_release_sha256": job._sha256(PRIOR / "release_integrity.json"),
        "archive_hashes_reused_with_exact_identity_guard": True,
        "original_archive_rehash": False, "inner_headers_and_metadata_verified": True})
    return joined


def diagnose():
    plan = bound_plan()
    joined = stage(plan)
    original = plan["videos"][4]
    prior_media_path = PRIOR / "media/0004.json"
    media = job.read_json(prior_media_path)
    if media["video_id"] != original["video_id"] or media["decode_status"] != "decoded":
        raise ValueError("exact interrupted fifth unit required")
    path = OUTPUT / "temporary" / ("diagnostic" + Path(original["media_relpath"]).suffix)
    diagnostics = OUTPUT / "diagnostics"
    diagnostics.mkdir()
    try:
        with zipfile.ZipFile(joined) as inner, inner.open(original["media_relpath"]) as source, path.open("xb") as target:
            digest = job.checked_copy(source, target, original["byte_size"], deadline=plan["deadline_unix_seconds"])
        if digest["sha256"] != media["media_sha256"]:
            raise ValueError("diagnostic payload differs from failed original")
        command = ["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-err_detect", "explode",
                   "-threads", "1", "-i", str(path), "-map", "0:v:0", "-an", "-sn", "-dn",
                   "-pix_fmt", "rgb24", "-threads", "1", "-vsync", "0", "-f", "rawvideo", "-"]
        stderr_path = diagnostics / "original-rawvideo.stderr"
        with stderr_path.open("xb") as errors:
            process = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=errors, timeout=180, check=False)
        result = {
            "interrupted_index": 4, "prior_media_sha256": job._sha256(prior_media_path),
            "video_payload_sha256": digest["sha256"], "native_frame_count": media["frame_count"],
            "returncode": process.returncode, "stderr_bytes": stderr_path.stat().st_size,
            "stderr_sha256": job._sha256(stderr_path), "stdout_discarded_not_pixel_readback": True,
            "original_command_replayed_once": True, "new_inference": False,
            "package_completion_claimed": False}
        job.write_immutable_record(OUTPUT / "diagnosis.json", result)
        print("RECOVERY282_DIAGNOSIS", json.dumps(result), flush=True)
    finally:
        if path.exists():
            path.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-approved", action="store_true")
    parser.add_argument("--worker", action="store_true")
    args = parser.parse_args()
    if args.worker:
        lease = job.read_json(OUTPUT / "diagnosis_lease.json")
        if lease["parent_pid"] != os.getppid() or lease["source_sha256"] != job._sha256(Path(__file__)) or os.getsid(0) != os.getpid():
            raise ValueError("one bound diagnostic worker required")
        job.retained.arm_deadline(authority()["deadline_unix_seconds"])
        diagnose()
        return 0
    if not args.start_approved:
        parser.error("--start-approved or --worker required")
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise FileExistsError("single recovery package only")
    previous = job.read_json(PRIOR / "resources.json")
    if previous["completion_claimed"] is not False:
        raise ValueError("recovery requires the preserved failed attempt")
    started = time.time()
    job.write_immutable_record(OUTPUT / "owner_approval.json", {
        "explicit_owner_approval": True, "selected_answer": APPROVAL, "caps": job.CAPS,
        "started_unix_seconds": started, "deadline_unix_seconds": started + job.CAPS["wall_seconds"],
        "prior_plan_sha256": job._sha256(PRIOR / "plan.json"),
        "prior_resources_sha256": job._sha256(PRIOR / "resources.json"),
        "scope": "one_diagnosis_fix_tests_and_one_recovery_with_readback_visual_publication",
        "automatic_retry": False, "preserve_prior_attempt": True})
    with (OUTPUT / "diagnosis.log").open("xb", buffering=0) as log:
        os.dup2(log.fileno(), 1)
        os.dup2(log.fileno(), 2)
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    job.write_immutable_record(OUTPUT / "diagnosis_lease.json", {
        "parent_pid": os.getpid(), "source_sha256": job._sha256(Path(__file__))})
    plan = bound_plan()
    job.retained.arm_deadline(plan["deadline_unix_seconds"])
    process, failure = None, None
    peaks = {"rss_bytes": 0, "output_bytes": 0, "temporary_bytes": 0}
    try:
        process = subprocess.Popen([sys.executable, str(Path(__file__)), "--worker"], start_new_session=True)
        while True:
            value = measured(process.pid)
            peaks = {key: max(peaks[key], value[key]) for key in peaks}
            job.enforce(plan, value)
            try:
                if process.wait(timeout=2):
                    raise RuntimeError("single diagnostic worker failed; no retry")
                break
            except subprocess.TimeoutExpired:
                continue
        result = job.read_json(OUTPUT / "diagnosis.json")
        if job._sha256(OUTPUT / "diagnostics/original-rawvideo.stderr") != result["stderr_sha256"]:
            raise ValueError("captured stderr commitment drift")
        job.enforce(plan, measured(os.getpgrp()))
    except Exception as error:
        failure = type(error).__name__ + ": " + str(error)
        print("RECOVERY282_DIAGNOSIS_FAILED", failure, flush=True)
    finally:
        if process is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        if failure:
            for name in ("MSU-MFSD-Publish.zip", "diagnostic.mp4", "diagnostic.mov"):
                path = OUTPUT / "temporary" / name
                if path.exists():
                    path.unlink()
    job.write_immutable_record(OUTPUT / "diagnosis_resources.json", {
        "diagnosis_completed": failure is None, "failure": failure, "sampled_peaks": peaks,
        "elapsed_seconds": time.time() - started, "joined_zip_retained_for_same_authorized_recovery": failure is None,
        "package_completion_claimed": False, "automatic_retry": False})
    return 1 if failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
