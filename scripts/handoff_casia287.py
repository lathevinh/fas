"""One explicitly approved same-deadline continuation; never repeat committed units."""

import argparse
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

import casia_resource287 as resources
import recover_casia287 as recovery

prior, OUTPUT = recovery.prior, recovery.OUTPUT
HANDOFF = OUTPUT / "handoff"
SNAPSHOT = HANDOFF / "retained-usage.json"


def committed_prefix(plan):
    paths = sorted((OUTPUT / "transactions").glob("*.json"))
    if [path.name for path in paths] != [f"{index:04d}.json" for index in range(len(paths))]:
        raise ValueError("only an exact committed prefix can be continued")
    for index, path in enumerate(paths):
        row = prior.read(path)
        if row["index"] != index or row["video_id"] != plan["videos"][index]["video_id"]:
            raise ValueError("committed prefix original/index drift")
        prior.shared.read_verified_json(OUTPUT / "media" / path.name, row["media_record_sha256"])
        for relative, asset in row["assets"].items():
            if prior.sha(OUTPUT / relative) != asset["sha256"]:
                raise ValueError("committed prefix image drift")
        selected = row.get("selected_RGB_asset")
        if selected and prior.sha(OUTPUT / selected["path"]) != selected["sha256"]:
            raise ValueError("committed selected image drift")
    return len(paths)


def check(plan, continuation):
    if continuation["original_plan_sha256"] != prior.sha(OUTPUT / "plan.json"):
        raise ValueError("original immutable plan drift")
    prior.shared.check_bindings(plan["sources"])
    prior.shared.check_bindings(continuation["sources"])
    for relative, digest in continuation["preserved_sha256"].items():
        if prior.sha(OUTPUT / relative) != digest:
            raise ValueError("a previously committed unit was changed")
    prior.guard(plan)
    recovery.diagnostic.enforce(recovery.probe.measured(os.getpgrp()))


def prepare(plan, approval):
    for pid in (approval["old_supervisor_pid"], approval["old_worker_pid"]):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            continue
        raise RuntimeError("original supervisor/worker must have exited before handoff")
    if (OUTPUT / "systemic_stop.json").exists():
        raise ValueError("systemic media stop cannot be bypassed by an observer handoff")
    count = committed_prefix(plan)
    if count >= 600:
        raise ValueError("handoff cannot repeat an already completed run")
    HANDOFF.mkdir()
    preserved = {}
    quarantine = HANDOFF / "interrupted"
    for folder in ("transactions", "attempts", "media", "replay", "frames", "crops", "probe"):
        for path in sorted((OUTPUT / folder).iterdir()):
            if path.is_symlink() or not path.name[:4].isdigit() or not 0 <= int(path.name[:4]) < 600:
                raise ValueError("unexpected per-original handoff artifact")
            if int(path.name[:4]) >= count:
                target = quarantine / folder / path.name
                target.parent.mkdir(parents=True, exist_ok=True)
                path.rename(target)
            else:
                for file in ([path] if path.is_file() else path.rglob("*")):
                    if file.is_file():
                        preserved[file.relative_to(OUTPUT).as_posix()] = prior.sha(file)
    superseded = HANDOFF / "superseded"
    superseded.mkdir()
    for name in ("resources.json", "failure_rows.json", "package_failure.json"):
        path = OUTPUT / name
        if path.exists():
            path.rename(superseded / name)
    recovery.SUMMARY.rename(superseded / "public-terminal.json")
    if prior.read(superseded / "resources.json")["failure"] is None:
        raise ValueError("original interruption evidence must remain explicit")
    expected = {row["media_relpath"] for row in plan["videos"]}
    actual = {path.relative_to(OUTPUT / "temporary").as_posix()
              for path in (OUTPUT / "temporary").rglob("*") if path.is_file()}
    if actual != expected:
        raise ValueError("same600 already CRC-checked staged inputs required; no re-extraction")
    monitor = resources.HistoricalStorage(
        [root for root in recovery.probe.ROOTS if root != OUTPUT], OUTPUT, SNAPSHOT, {"preflight": True})
    monitor.scan()
    started = time.monotonic()
    value = monitor.measure(os.getpgrp())
    elapsed = time.monotonic() - started
    recovery.diagnostic.enforce(value)
    if elapsed >= 2:
        raise TimeoutError("foreground observer preflight too slow for same-deadline continuation")
    prior.write(HANDOFF / "observer_preflight.json", {
        "foreground_measurement_seconds": elapsed,
        "historical_full_scan_seconds": prior.read(SNAPSHOT)["scan_seconds"],
        "sample": value, "deadline_unix_seconds": approval["deadline_unix_seconds"],
        "all_historical_roots_still_fully_scanned": True, "current_root_fresh_every_measurement": True,
        "historical_storage_is_conservatively_monotone": True,
        "projected600_throughput_not_certified_by_partial_tree_measurement": True})
    sources = {str(path): prior.sha(path) for path in (
        Path(__file__), Path(resources.__file__), prior.ROOT / "tests/test_casia_resource_observer.py",
        OUTPUT / "handoff_approval.json", HANDOFF / "observer_preflight.json",
        OUTPUT / "release_integrity.json", superseded / "resources.json", superseded / "public-terminal.json")}
    prior.write(HANDOFF / "plan.json", {
        "original_plan_sha256": prior.sha(OUTPUT / "plan.json"), "sources": sources,
        "preserved_sha256": preserved, "committed_prefix": count,
        "interrupted_uncommitted_indices": sorted({int(path.name[:4]) for path in quarantine.glob("*/*")}),
        "deadline_unix_seconds": approval["deadline_unix_seconds"], "caps": approval["caps"],
        "automatic_retry": False, "completed_originals_must_not_repeat": True,
        "staged_originals_reused_without_reextraction": 600})
    print(json.dumps({"committed_prefix": count, "foreground_measurement_seconds": elapsed,
                      "remaining_minutes": (approval["deadline_unix_seconds"] - time.time()) / 60}))


def worker(plan, continuation):
    import cv2
    import onnxruntime as ort

    check(plan, continuation)
    options = ort.SessionOptions()
    options.intra_op_num_threads = options.inter_op_num_threads = 1
    session = ort.InferenceSession(str(prior.shared.retained.MODEL), sess_options=options,
                                  providers=["CPUExecutionProvider"])
    if session.get_providers() != ["CPUExecutionProvider"]:
        raise ValueError("CPU-only inference required")
    cv2.setNumThreads(1)
    media_rows = [prior.read(OUTPUT / "media" / f"{index:04d}.json")
                  for index in range(continuation["committed_prefix"])]
    previous, consecutive = None, 0
    for media in media_rows:
        signature = recovery.failure_signature(media)
        consecutive = consecutive + 1 if signature and signature == previous else int(signature is not None)
        previous = signature
    try:
        for index in range(continuation["committed_prefix"], 600):
            if consecutive >= plan["systemic_stop_consecutive"]:
                raise RuntimeError("preserved prefix already reached systemic stop")
            prior.guard(plan)
            row, media = recovery.produce_unit(plan, index, plan["videos"][index], session)
            media_rows.append(media)
            signature = recovery.failure_signature(media)
            consecutive = consecutive + 1 if signature and signature == previous else int(signature is not None)
            previous = signature
            print("CASIA287", index, row["role"], row["detector_status"], media["failure_reason"], flush=True)
            if consecutive >= plan["systemic_stop_consecutive"]:
                prior.write(OUTPUT / "systemic_stop.json", {"index": index, "failure_signature": signature,
                                                         "consecutive": consecutive, "automatic_retry": False})
                raise RuntimeError("three consecutive same strict-probe failures: " + signature)
        findings = prior.shared.exact_checks(media_rows, {row["video_id"]: row for row in plan["videos"]})
        prior.write(OUTPUT / "content_checks.json", {
            "exact_groups": findings, "forbidden_exact_crossings": 0,
            "near_duplicate_independence_certified": False, "joined_cross_dataset_ancestry_certified": False})
        check(plan, continuation)
        prior.write(OUTPUT / "worker_completion.json", {
            "transactions": 600, "video_crc_checked": 600,
            "native_frames": sum(row["frame_count"] for row in media_rows),
            "video_payload_bytes": sum(row["byte_size"] for row in media_rows),
            "provider": ["CPUExecutionProvider"], "gpu_seconds": 0, "model_scores": 0, "fitted_scores": 0,
            "committed_units_reused_without_decode_or_inference": continuation["committed_prefix"]})
    finally:
        prior.cleanup()


def supervise(plan, continuation):
    binding = {"parent_pid": os.getpid(), "continuation_sha256": prior.sha(HANDOFF / "plan.json")}
    prior.write(HANDOFF / "lease.json", binding)
    monitor = resources.HistoricalStorage(
        [root for root in recovery.probe.ROOTS if root != OUTPUT], OUTPUT, SNAPSHOT, binding).start()
    recovery.probe.measured = monitor.measure
    process, failure, readback = None, None, None
    peaks = prior.read(HANDOFF / "superseded" / "resources.json")["sampled_peaks"]
    started = time.monotonic()
    try:
        check(plan, continuation)
        for mode in ("--worker", "--verify"):
            process = subprocess.Popen([sys.executable, str(Path(__file__)), mode], start_new_session=True)
            while True:
                value = monitor.measure(process.pid)
                peaks = {key: max(peaks[key], value[key]) for key in peaks}
                recovery.diagnostic.enforce(value)
                try:
                    if process.wait(timeout=2):
                        raise RuntimeError(mode + " failed during approved continuation; no retry")
                    break
                except subprocess.TimeoutExpired:
                    continue
            process = None
        readback = prior.read(OUTPUT / "readback.json")
        manifest = prior.shared.read_verified_json(OUTPUT / "full_manifest.json", readback["full_manifest_sha256"])
        if any(readback[key] != value for key, value in prior.validate_manifest(plan, manifest["rows"]).items()):
            raise ValueError("final600 counts drift")
        for relative, digest in {**readback["per_unit_sha256"], **readback["asset_sha256"],
                                 **prior.read(OUTPUT / "probe_readback.json")["per_probe_sha256"]}.items():
            if prior.sha(OUTPUT / relative) != digest:
                raise ValueError("final complete image/record/probe commitment drift")
        check(plan, continuation)
        monitor.close()
        value = recovery.probe.measured(os.getpgrp())
        value["rss_bytes"] = max(value["rss_bytes"], resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024)
        peaks = {key: max(peaks[key], value[key]) for key in peaks}
        recovery.diagnostic.enforce(peaks)
    except Exception as error:
        failure = type(error).__name__ + ": " + str(error)
        print("HANDOFF287_FAILED", failure, flush=True)
    finally:
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
        prior.cleanup()
        try:
            monitor.close()
        except Exception as error:
            failure = (failure + "; " if failure else "") + type(error).__name__ + ": " + str(error)
            print("HANDOFF287_OBSERVER_FAILED", failure, flush=True)
    if failure:
        recovery.failed_ledger(plan, failure)
    result = {
        "checkpoint": 287, "dataset": "CASIA-FASD", "accounting_complete": failure is None and readback is not None,
        "image_export_software_complete": failure is None and readback is not None and readback["detector_success"] > 0,
        "primary_image_preprocessing_complete": False, "local_audit_complete": False,
        "failure": failure, "attempts": 1, "automatic_retry": False, "caps": recovery.diagnostic.CAPS,
        "sampled_peaks": peaks, "package_wall_seconds": time.time() - recovery.diagnostic.authority()["started_unix_seconds"],
        "supervised_wall_seconds": time.monotonic() - started, "gpu_seconds": 0, "originals": 600,
        **{key: readback[key] if readback else None for key in
           ("selected", "detector_success", "detector_failure", "pre_detector_failure", "native_frames", "strict_replay_count")},
        "visual_inspection_pending": failure is None and readback is not None and readback["detector_success"] > 0,
        "scientific_readiness": False, "approved_same_deadline_handoff": True,
        "committed_units_not_repeated": continuation["committed_prefix"],
        "continuation_plan_sha256": prior.sha(HANDOFF / "plan.json")}
    prior.write(OUTPUT / "resources.json", result)
    prior.write(recovery.SUMMARY, {
        **result, "role_originals": prior.ROLES, "role_subjects": prior.GROUPS,
        "audit_summary_statuses_changed": False, "images_reused_from285": 0,
        "private_record_sha256": {path.name: prior.sha(path) for path in OUTPUT.glob("*.json")},
        "active_config_sha256": plan["active_config_sha256"], "model_scores": 0, "fitted_scores": 0})
    print("RECOVERY287_TERMINAL", json.dumps(result), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    for mode in ("prepare", "continue-once", "worker", "verify"):
        modes.add_argument("--" + mode, action="store_true")
    args = parser.parse_args()
    approval = prior.read(OUTPUT / "handoff_approval.json")
    authority = recovery.diagnostic.authority()
    if approval["selected_answer"] != "approve_controlled_handoff_same_deadline" or approval["explicit_owner_approval"] is not True:
        raise ValueError("explicit controlled-handoff authority required")
    if approval["deadline_unix_seconds"] != authority["deadline_unix_seconds"] or approval["caps"] != authority["caps"]:
        raise ValueError("original combined deadline/caps cannot change")
    prior.shared.retained.arm_deadline(authority["deadline_unix_seconds"])
    plan = prior.read(OUTPUT / "plan.json")
    if args.prepare:
        prepare(plan, approval)
        return 0
    continuation = prior.read(HANDOFF / "plan.json")
    prior.OUTPUT = prior.shared.OUTPUT = OUTPUT
    if args.worker or args.verify:
        lease = prior.read(HANDOFF / "lease.json")
        if lease["parent_pid"] != os.getppid() or lease["continuation_sha256"] != prior.sha(HANDOFF / "plan.json") or os.getsid(0) != os.getpid():
            raise ValueError("one supervised continuation child lease required")
        recovery.probe.measured = lambda group: resources.measured(group, OUTPUT, SNAPSHOT, lease)
        check(plan, continuation)
        worker(plan, continuation) if args.worker else recovery.verify(plan)
        return 0
    prior.write(HANDOFF / "supervisor.json", {"pid": os.getpid(), "source_sha256": prior.sha(Path(__file__))})
    with (HANDOFF / "execution.log").open("xb", buffering=0) as log:
        os.dup2(log.fileno(), 1)
        os.dup2(log.fileno(), 2)
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    try:
        return 0 if supervise(plan, continuation)["accounting_complete"] else 1
    except Exception as error:
        prior.write(OUTPUT / "package_failure.json", {
            "error_type": type(error).__name__, "message": str(error), "accounting_complete": False,
            "primary_image_preprocessing_complete": False, "automatic_retry": False,
            "approved_same_deadline_handoff": True})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
