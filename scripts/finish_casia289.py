"""Explicit same-clock handoff after reproduced v9fs control-publication failure."""

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import zlib
import hashlib
import stat

import resume_casia289 as base

prior, OUTPUT = base.prior, base.OUTPUT
HANDOFF = OUTPUT / "native_handoff"
IPC = Path.home() / ".cache/fas/casia289-native-ipc"
ROOTS = (*base.ROOTS, IPC)
RETAINED = 464


def authority():
    original = base.authority()
    extra = prior.read(OUTPUT / "native_ipc_handoff_approval.json")
    if (extra["selected_answer"] != "approve_native_ipc_handoff289_same_deadline"
            or extra["explicit_owner_approval"] is not True or extra["caps"] != original["caps"]
            or extra["deadline_unix_seconds"] != original["deadline_unix_seconds"]):
        raise ValueError("explicit same-clock native-IPC handoff required")
    if time.time() >= original["deadline_unix_seconds"] - base.SHUTDOWN_RESERVE_SECONDS:
        raise TimeoutError("no authority after original289 work cutoff")
    return original


def prepare():
    authority()
    old = prior.read(OUTPUT / "supervisor.json")
    try:
        os.kill(old["pid"], 0)
    except ProcessLookupError:
        pass
    else:
        raise RuntimeError("old supervisor must be stopped")
    plan = prior.read(OUTPUT / "plan.json")
    prior.shared.check_bindings(plan["sources"])
    if {path.name for path in (OUTPUT / "transactions").glob("*.json")} != {f"{i:04d}.json" for i in range(RETAINED)}:
        raise ValueError("exact464 committed originals required")
    if (OUTPUT / "systemic_stop.json").exists():
        raise ValueError("observer handoff cannot bypass a systemic media stop")
    HANDOFF.mkdir()
    IPC.mkdir(parents=True)
    superseded = HANDOFF / "superseded"
    superseded.mkdir()
    for name in ("resources.json", "failure_rows.json", "lease.json"):
        (OUTPUT / name).rename(superseded / name)
    base.SUMMARY.rename(superseded / "public-terminal.json")
    if "FileNotFoundError" not in prior.read(superseded / "resources.json")["failure"]:
        raise ValueError("captured observer-control interruption required")
    for folder in ("attempts", "media", "probe", "replay", "frames", "crops"):
        for path in (OUTPUT / folder).iterdir():
            if path.name[:4].isdigit() and int(path.name[:4]) >= RETAINED:
                target = HANDOFF / "interrupted" / folder / path.name
                target.parent.mkdir(parents=True, exist_ok=True)
                path.rename(target)
    retained = {f"transactions/{i:04d}.json": prior.sha(OUTPUT / "transactions" / f"{i:04d}.json")
                for i in range(RETAINED)}
    sources = {str(path): prior.sha(path) for path in (
        Path(__file__), prior.ROOT / "scripts/complete_finish289.py",
        prior.ROOT / "tests/test_casia_finish.py", OUTPUT / "native_ipc_handoff_approval.json",
        superseded / "resources.json", superseded / "failure_rows.json", superseded / "public-terminal.json",
        OUTPUT / "plan.json", OUTPUT / "retained_readback.json", OUTPUT / "selective_staging.json")}
    prior.write(HANDOFF / "plan.json", {
        "sources": sources, "retained_transaction_sha256": retained, "remaining_indices": list(range(RETAINED, 600)),
        "retained_committed": RETAINED, "new_remaining": 136, "original_plan_sha256": prior.sha(OUTPUT / "plan.json"),
        "control_filesystem": "native Linux; data artifacts remain on original filesystem",
        "deadline_unix_seconds": base.authority()["deadline_unix_seconds"], "caps": base.CAPS,
        "automatic_retry": False})
    print("NATIVE_IPC_HANDOFF_PREPARED 464+136", flush=True)


def check(addendum):
    prior.shared.check_bindings(addendum["sources"])
    for relative, digest in addendum["retained_transaction_sha256"].items():
        if prior.sha(OUTPUT / relative) != digest:
            raise ValueError("previously committed transaction changed")


def retained(plan, addendum):
    check(addendum)
    original = prior.read(OUTPUT / "retained_readback.json")
    for relative, digest in original["source_record_and_asset_sha256"].items():
        if prior.sha(OUTPUT / relative) != digest or prior.sha(base.SOURCE / relative) != digest:
            raise ValueError("original447 readback bindings changed")
    media_rows, assets = [], {}
    for index in range(RETAINED):
        row = prior.shared.read_verified_json(OUTPUT / "transactions" / f"{index:04d}.json",
                                            addendum["retained_transaction_sha256"][f"transactions/{index:04d}.json"])
        media_path = OUTPUT / "media" / f"{index:04d}.json"
        media = prior.shared.read_verified_json(media_path, row["media_record_sha256"])
        native = plan["videos"][index]
        if any(media[key] != native[key] for key in
               ("video_id", "role", "binary_label", "official_split", "subject_id", "media_relpath", "byte_size")):
            raise ValueError("retained464 native/frozen identity drift")
        transaction = prior.shared.technical_transaction(media)
        transaction.update(media_sha256=media["media_sha256"], media_record_sha256=prior.sha(media_path))
        if any(row[key] != value for key, value in transaction.items() if key not in {"detector_status", "final_k1_action"}):
            raise ValueError("retained464 fixed-middle identity drift")
        if row["index"] != index or row["model_sha256"] != prior.shared.MODEL_SHA256 or row["config_sha256"] != plan["active_config_sha256"]:
            raise ValueError("retained464 detector/config drift")
        if index >= 447:
            replay = prior.shared.read_verified_json(OUTPUT / "replay" / f"{index:04d}.json", row["replay_record_sha256"])
            stderr = OUTPUT / "replay" / f"{index:04d}.stderr"
            if (not replay["strict_success"] or replay["returncode"] or replay["stderr_bytes"] or replay["failure"] is not None
                    or replay["frames_verified"] != media["frame_count"] or replay["frame_count"] != media["frame_count"]
                    or replay["decoded_rgb_sequence_sha256"] != media["decoded_rgb_sequence_sha256"]
                    or replay["frame_substitution"] is not False or stderr.stat().st_size
                    or prior.sha(stderr) != replay["stderr_sha256"]):
                raise ValueError("additional17 strict replay receipt drift")
            _, unit_assets = prior.shared.images.validate_unit(
                {"transaction": transaction, "media_path": str(media_path)}, OUTPUT, index, 4,
                plan["active_config_sha256"], prior.sha(OUTPUT / "transactions" / f"{index:04d}.json"))
            assets.update(unit_assets)
        base.verify_probe(index)
        media_rows.append(media)
    if Counter(prior.read(OUTPUT / "transactions" / f"{i:04d}.json")["detector_status"] for i in range(RETAINED)) != {"success": 458, "failed": 6}:
        raise ValueError("464 retained outcome accounting drift")
    prior.write(HANDOFF / "retained_readback.json", {
        "retained_committed": 464, "original447_readback_sha256": prior.sha(OUTPUT / "retained_readback.json"),
        "additional17_asset_sha256": assets, "retained_decode_calls": 0, "retained_detector_calls": 0})
    return media_rows


def stage(plan, client, indices):
    if indices != list(range(RETAINED, 600)):
        raise ValueError("exact136 remaining originals required")
    prior.guard(plan)
    if prior.list_headers() != plan["headers"] or prior.read_file_headers(prior.ARCHIVE) != plan["crc_headers"]:
        raise ValueError("archive native header/CRC drift")
    selected = {plan["videos"][i]["media_relpath"]: plan["videos"][i] for i in indices}
    temporary = OUTPUT / "temporary"
    if list(temporary.iterdir()):
        raise ValueError("owned staging must be empty")
    errors = HANDOFF / "restaging.stderr"
    command = [str(prior.EXTRACTOR), "-xf", str(prior.ARCHIVE), "-C", str(temporary),
               "--no-same-owner", "--no-same-permissions", "--keep-old-files", "--", *selected]
    with client.reserve(sum(row["byte_size"] for row in plan["videos"]) + base.FILE_LIMIT):
        with errors.open("xb") as stream:
            result = subprocess.run(base.budget.limited_command(command, base.FILE_LIMIT), stdin=subprocess.DEVNULL,
                                    stdout=subprocess.DEVNULL, stderr=stream, check=False,
                                    timeout=max(0.001, plan["deadline_unix_seconds"] - time.time()))
        if result.returncode or errors.stat().st_size:
            raise ValueError("strict136 selective extraction exit/stderr failure")
        pins, checked = prior.read(OUTPUT / "release_integrity.json")["video_payload_pins"], {}
        directories = {parent.as_posix() for name in selected for parent in Path(name).parents if parent != Path(".")}
        for path in temporary.rglob("*"):
            relative, entry = path.relative_to(temporary).as_posix(), path.lstat()
            if stat.S_ISDIR(entry.st_mode):
                if relative not in directories:
                    raise ValueError("unexpected restaging directory")
                continue
            if not stat.S_ISREG(entry.st_mode) or relative not in selected:
                raise ValueError("unexpected restaged file")
            crc, digest = 0, hashlib.sha256()
            with path.open("rb") as stream:
                while block := stream.read(1024 ** 2):
                    base.enforce(client.measure(os.getpgrp()))
                    crc = zlib.crc32(block, crc)
                    digest.update(block)
            pin = {"byte_size": entry.st_size, "crc32": crc, "sha256": digest.hexdigest()}
            if pin != pins[relative]:
                raise ValueError("restaged native CRC/size/SHA drift")
            checked[relative] = pin
        if set(checked) != set(selected):
            raise ValueError("exact136 selectively restaged inputs required")
        prior.write(HANDOFF / "restaging.json", {
            "new_extracted_videos": 136, "source_pins": checked, "extractor_returncode": 0,
            "extractor_stderr_bytes": 0, "extractor_stderr_sha256": prior.sha(errors),
            "full600_extraction_repeated": False, "command": command})
    prior.guard(plan)


def worker(plan, addendum, client):
    import cv2
    import onnxruntime as ort
    media_rows = retained(plan, addendum)
    stage(plan, client, addendum["remaining_indices"])
    options = ort.SessionOptions()
    options.intra_op_num_threads = options.inter_op_num_threads = 1
    session = ort.InferenceSession(str(prior.shared.retained.MODEL), sess_options=options,
                                  providers=["CPUExecutionProvider"])
    if session.get_providers() != ["CPUExecutionProvider"]:
        raise ValueError("CPU-only inference required")
    cv2.setNumThreads(1)
    previous, consecutive = None, 0
    try:
        for index in addendum["remaining_indices"]:
            base.enforce(client.measure(os.getpgrp()))
            row, media = base.previous.produce_unit(plan, index, plan["videos"][index], session)
            media_rows.append(media)
            signature = base.previous.failure_signature(media)
            consecutive = consecutive + 1 if signature and signature == previous else int(signature is not None)
            previous = signature
            print("CASIA289_FINISH", index, row["role"], row["detector_status"], media["failure_reason"], flush=True)
            if consecutive >= 3:
                prior.write(OUTPUT / "systemic_stop.json", {"index": index, "signature": signature,
                                                         "consecutive": consecutive, "automatic_retry": False})
                raise RuntimeError("three consecutive same strict-probe failures")
        findings = prior.shared.exact_checks(media_rows, {row["video_id"]: row for row in plan["videos"]})
        prior.write(OUTPUT / "content_checks.json", {
            "exact_groups": findings, "forbidden_exact_crossings": 0,
            "near_duplicate_independence_certified": False, "joined_cross_dataset_ancestry_certified": False})
        prior.write(OUTPUT / "worker_completion.json", {
            "transactions": 600, "video_crc_checked": 600, "native_frames": sum(row["frame_count"] for row in media_rows),
            "video_payload_bytes": sum(row["byte_size"] for row in media_rows),
            "provider": ["CPUExecutionProvider"], "gpu_seconds": 0, "model_scores": 0, "fitted_scores": 0,
            "retained_without_decode_or_inference": 447, "new_attempts": 153,
            "handoff_retained_without_repeat": 464, "handoff_new_attempts": 136})
    finally:
        prior.cleanup()


def supervise(plan, addendum):
    binding = {"parent_pid": os.getpid(), "plan_sha256": prior.sha(HANDOFF / "plan.json")}
    prior.write(HANDOFF / "lease.json", binding)
    prior.write(OUTPUT / "lease.json", {"parent_pid": os.getpid(), "plan_sha256": prior.sha(OUTPUT / "plan.json")})
    base.budget.initialize(IPC, binding)
    client = base.budget.Client(IPC, binding, base.usage, base.enforce)
    scanner, process, failure, readback = None, None, None, None
    peaks = prior.read(HANDOFF / "superseded/resources.json")["sampled_peaks"]
    try:
        scanner = subprocess.Popen([sys.executable, str(Path(__file__)), "--scan"], start_new_session=True)
        base.budget.publish(OUTPUT / "lease.json", {
            "parent_pid": os.getpid(), "plan_sha256": prior.sha(OUTPUT / "plan.json"), "scanner_pid": scanner.pid})
        while not (IPC / "snapshot.json").exists():
            if scanner.poll() is not None:
                raise RuntimeError("native IPC scanner failed")
            if time.time() >= plan["deadline_unix_seconds"]:
                raise TimeoutError("same-clock preflight deadline")
            time.sleep(0.1)
        for mode in ("--worker", "--verify"):
            process = subprocess.Popen([sys.executable, str(Path(__file__)), mode], start_new_session=True)
            while True:
                if scanner.poll() is not None:
                    raise RuntimeError("native IPC scanner exited")
                value = client.measure(process.pid)
                peaks = {key: max(peaks[key], value[key]) for key in peaks}
                base.enforce(value)
                try:
                    if process.wait(timeout=0.5):
                        raise RuntimeError(mode + " failed; no automatic retry")
                    break
                except subprocess.TimeoutExpired:
                    continue
            process = None
        readback = prior.read(OUTPUT / "readback.json")
        check(addendum)
        prior.shared.check_bindings(plan["sources"])
        prior.guard(plan)
    except Exception as error:
        failure = type(error).__name__ + ": " + str(error)
        print("NATIVE_HANDOFF_FAILED", failure, flush=True)
    finally:
        for child in (process, scanner):
            if child is not None:
                base.budget.stop_group(child)
        signal.setitimer(signal.ITIMER_REAL, 0)
        prior.shared.retained.arm_deadline(base.authority()["deadline_unix_seconds"])
        cleanup = subprocess.Popen([sys.executable, str(Path(base.__file__)), "--cleanup"], start_new_session=True)
        try:
            if cleanup.wait(timeout=30):
                raise RuntimeError("selective cleanup failed")
        except Exception as error:
            base.budget.stop_group(cleanup)
            failure = (failure + "; " if failure else "") + type(error).__name__ + ": " + str(error)
        if failure is None:
            try:
                base.budget.scan_once(ROOTS, IPC, binding, prior.shared.retained.tree_bytes)
                value = client.measure(os.getpgrp())
                peaks = {key: max(peaks[key], value[key]) for key in peaks}
                base.enforce(value, work=False)
            except Exception as error:
                failure = type(error).__name__ + ": " + str(error)
    if failure:
        from complete_casia287 import partial_ledger
        rows = partial_ledger(
            plan["videos"], {int(p.stem): prior.read(p) for p in (OUTPUT / "transactions").glob("*.json")},
            {int(p.stem): prior.read(p) for p in (OUTPUT / "attempts").glob("*.json")})
        prior.write(OUTPUT / "failure_rows.json", {"rows": rows, "failure": failure, "automatic_retry": False})
    result = {
        "checkpoint": 289, "dataset": "CASIA-FASD", "originals": 600, "failure": failure,
        "accounting_complete": failure is None and readback is not None,
        "image_export_software_complete": failure is None and readback is not None and readback["detector_success"] > 0,
        "primary_image_preprocessing_complete": False, "local_audit_complete": False,
        "retained_without_decode_or_inference": 447, "remaining_authorized": 153,
        "handoff_retained_without_repeat": 464, "handoff_new_attempts": 136,
        "automatic_retry": False, "attempts": 1, "caps": base.CAPS, "sampled_peaks": peaks,
        "package_wall_seconds": time.time() - base.authority()["started_unix_seconds"],
        **{key: readback[key] if readback else None for key in
           ("selected", "detector_success", "detector_failure", "pre_detector_failure", "native_frames", "strict_replay_count")},
        "gpu_seconds": 0, "model_scores": 0, "fitted_scores": 0, "scientific_readiness": False,
        "native_handoff_plan_sha256": prior.sha(HANDOFF / "plan.json")}
    prior.write(OUTPUT / "resources.json", result)
    prior.write(base.SUMMARY, {
        **result, "private_record_sha256": {p.name: prior.sha(p) for p in OUTPUT.glob("*.json")},
        "role_originals": prior.ROLES, "role_subjects": prior.GROUPS, "audit_summary_statuses_changed": False})
    print("CASIA289_TERMINAL", json.dumps(result), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    for mode in ("prepare", "run-once", "scan", "worker", "verify"):
        modes.add_argument("--" + mode, action="store_true")
    args = parser.parse_args()
    authority()
    prior.shared.retained.arm_deadline(base.authority()["deadline_unix_seconds"] - base.SHUTDOWN_RESERVE_SECONDS)
    if args.prepare:
        prepare()
        return 0
    plan, addendum = prior.read(OUTPUT / "plan.json"), prior.read(HANDOFF / "plan.json")
    prior.OUTPUT = prior.shared.OUTPUT = OUTPUT
    if args.scan or args.worker or args.verify:
        lease = prior.read(HANDOFF / "lease.json")
        if lease["parent_pid"] != os.getppid() or lease["plan_sha256"] != prior.sha(HANDOFF / "plan.json") or os.getsid(0) != os.getpid():
            raise ValueError("explicit native handoff child lease required")
        if args.scan:
            base.budget.scan_forever(ROOTS, IPC, lease, prior.shared.retained.tree_bytes)
        else:
            check(addendum)
            prior.shared.check_bindings(plan["sources"])
            client = base.budget.Client(IPC, lease, base.usage, base.enforce)
            base.configure(client)
            worker(plan, addendum, client) if args.worker else base.verify(plan, client)
        return 0
    prior.write(HANDOFF / "supervisor.json", {"pid": os.getpid(), "source_sha256": prior.sha(Path(__file__))})
    with (HANDOFF / "execution.log").open("xb", buffering=0) as log:
        os.dup2(log.fileno(), 1)
        os.dup2(log.fileno(), 2)
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    try:
        return 0 if supervise(plan, addendum)["accounting_complete"] else 1
    except Exception as error:
        prior.write(OUTPUT / "package_failure.json", {
            "error_type": type(error).__name__, "message": str(error), "automatic_retry": False,
            "accounting_complete": False, "primary_image_preprocessing_complete": False})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
