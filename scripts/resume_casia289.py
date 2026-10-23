"""Fresh, bounded CASIA closure: reuse447 without decoding; process only153."""

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import time
import zlib

import casia_budget289 as budget
import recover_casia287 as previous
from msu_replay282 import replay_command

prior = previous.prior
SOURCE = previous.OUTPUT
OUTPUT = prior.shared.BASE / "casia_resume289_v1"
SUMMARY = prior.ROOT / "results/phase1/casia-preprocessing289-resume-v1.json"
CAPS = {"wall_seconds": 7200, "rss_bytes": 4 * 1024 ** 3,
        "output_bytes": 32 * 1024 ** 3, "gpu_seconds": 0}
ROOTS = (*previous.probe.ROOTS, OUTPUT)
OBSERVER = OUTPUT / "observer"
RETAINED = 447
FILE_LIMIT = 16 * 1024 ** 2
SHUTDOWN_RESERVE_SECONDS = 600


def authority():
    value = prior.read(OUTPUT / "owner_approval.json")
    if value["selected_answer"] != "approve_combined_casia289" or value["explicit_owner_approval"] is not True:
        raise ValueError("fresh combined CASIA289 authority required")
    if value["caps"] != CAPS or value["deadline_unix_seconds"] != value["started_unix_seconds"] + CAPS["wall_seconds"]:
        raise ValueError("fresh clock/caps may not change")
    if value["review288_sha256"] != prior.sha(prior.ROOT / "docs/288-review-doc287-casia-recovery-and-partial-progress.md"):
        raise ValueError("review288 authority binding drift")
    return value


def enforce(value, *, work=True):
    deadline = authority()["deadline_unix_seconds"] - (SHUTDOWN_RESERVE_SECONDS if work else 0)
    if time.time() >= deadline:
        raise budget.BudgetError("fresh CASIA289 work deadline" if work else "fresh CASIA289 final deadline")
    if value["rss_bytes"] > CAPS["rss_bytes"]:
        raise budget.BudgetError("combined4GiB RSS cap")
    if value["output_bytes"] > CAPS["output_bytes"] - prior.shared.RESERVE:
        raise budget.BudgetError("combined32GiB retained/temporary cap")


def usage(group):
    value = prior.shared.usage(group, OUTPUT / ".unused")
    lease = prior.read(OUTPUT / "lease.json")
    scanner = lease.get("scanner_pid")
    if scanner is not None and scanner != group:
        other = prior.shared.usage(scanner, OUTPUT / ".unused")
        value["rss_bytes"] += other["rss_bytes"]
        value["temporary_bytes"] += other["temporary_bytes"]
    return value


def make_plan():
    approval = authority()
    terminal = prior.read(prior.ROOT / "results/phase1/casia-preprocessing287-recovery-v1.json")
    for name, digest in terminal["private_record_sha256"].items():
        if prior.sha(SOURCE / name) != digest:
            raise ValueError("immutable287 terminal parent drift")
    plan = prior.read(SOURCE / "plan.json")
    partial = prior.read(prior.ROOT / "results/phase1/casia-preprocessing287-partial-v1.json")
    if partial["execution_counts"] != {"committed_provisional": 447, "interrupted_before_commit": 1,
                                      "not_attempted_after_deadline": 152}:
        raise ValueError("exact447 retained/153 remaining source state required")
    if {path.name for path in (SOURCE / "transactions").glob("*.json")} != {f"{i:04d}.json" for i in range(RETAINED)}:
        raise ValueError("exact immutable447 committed prefix required")
    proof = prior.read(SOURCE / "native_fix_validation.json")
    if proof["probe_source_sha256"] != prior.sha(Path(previous.probe.__file__)) or proof["count_source_sha256"] != prior.sha(Path(previous.counts.__file__)):
        raise ValueError("unchanged accepted native parser proof required")
    preflight = prior.read(prior.ROOT / "results/phase1/casia-observer289-preflight-v1.json")
    if preflight["source_sha256"]["casia_budget289.py"] != prior.sha(Path(budget.__file__)):
        raise ValueError("populated-tree observer proof/source drift")
    if preflight["foreground_p95_seconds"] >= 0.05 or preflight["foreground_max_seconds"] >= 0.25:
        raise ValueError("corrected600-tree foreground latency proof required")
    sources = dict(plan["sources"])
    for path in (
        Path(__file__), Path(budget.__file__), prior.ROOT / "scripts/benchmark_casia289_observer.py",
        prior.ROOT / "scripts/complete_casia289.py", prior.ROOT / "tests/test_casia_budget.py",
        prior.ROOT / "tests/test_casia_resume.py",
        prior.ROOT / "docs/288-review-doc287-casia-recovery-and-partial-progress.md",
        prior.ROOT / "results/phase1/casia-observer289-preflight-v1.json",
        prior.ROOT / "results/phase1/casia-preprocessing287-recovery-v1.json",
        prior.ROOT / "results/phase1/casia-preprocessing287-partial-v1.json",
        SOURCE / "resources.json", SOURCE / "plan.json", SOURCE / "failure_rows.json",
        SOURCE / "release_integrity.json", SOURCE / "extraction.stderr",
        SOURCE / "partial_accounting.json", OUTPUT / "owner_approval.json",
    ):
        sources[str(path)] = prior.sha(path)
    plan.update(checkpoint=289, sources=sources, caps=CAPS,
                deadline_unix_seconds=approval["deadline_unix_seconds"] - SHUTDOWN_RESERVE_SECONDS,
                retained_transactions=RETAINED, remaining_indices=list(range(RETAINED, 600)),
                remaining_payload_bytes=sum(row["byte_size"] for row in plan["videos"][RETAINED:]),
                images_reused_from287=441, images_reused_from285=0,
                retained_units_must_not_decode_or_infer=True, systemic_stop_consecutive=3)
    prior.shared.check_bindings(sources)
    prior.guard(plan)
    prior.write(OUTPUT / "plan.json", plan)
    return plan


def verify_commands(folder, media):
    expected = media["probe_evidence_sha256"]
    if {path.relative_to(OUTPUT).as_posix() for path in folder.iterdir()} != set(expected):
        raise ValueError("exact per-original durable probe set required")
    for relative, digest in expected.items():
        if prior.sha(OUTPUT / relative) != digest:
            raise ValueError("raw probe evidence drift")
    for path in folder.glob("*.json"):
        if path.name in {"probe_result.json", "native-count.json"}:
            continue
        record = prior.read(path)
        for kind in ("stdout", "stderr"):
            file = path.with_suffix("." + kind)
            if file.stat().st_size != record[kind + "_bytes"] or prior.sha(file) != record[kind + "_sha256"]:
                raise ValueError("strict probe command commitment drift")
        if media["decode_status"] == "decoded" and (record["returncode"] or record["stderr_bytes"]):
            raise ValueError("accepted probe has decoder exit/stderr failure")


def verify_probe(index):
    media = prior.read(OUTPUT / "media" / f"{index:04d}.json")
    folder = OUTPUT / "probe" / f"{index:04d}"
    verify_commands(folder, media)
    saved = prior.shared.read_verified_json(folder / "probe_result.json", media["probe_result_sha256"])
    if any(media[key] != value for key, value in saved.items()):
        raise ValueError("saved strict probe/media drift")
    if media["decode_status"] == "decoded":
        def optional(name):
            path = folder / name
            return prior.read(path) if path.exists() else None
        count = optional("native-count.json")
        if count is not None and (count["source_sha256"] != media["media_sha256"] or count["source_bytes"] != media["byte_size"]):
            raise ValueError("native count/source binding drift")
        result = previous.probe.parse_evidence(
            prior.read(folder / "original-metadata.stdout"), (folder / "native-framehash.stdout").read_text(),
            packets=optional("native-packets.stdout"), generated=optional("guarded-genpts.stdout"),
            count_evidence=count)
        if any(media[key] != value for key, value in result.items()):
            raise ValueError("strict native clock/count/RGB evidence readback drift")
    elif not media.get("probe_failure") or media["failure_reason"] != media["probe_failure"]["stage"] + ":" + media["probe_failure"]["reason"]:
        raise ValueError("technical failure lacks exact durable stage/reason")
    return media


def configure(client):
    previous.OUTPUT = OUTPUT
    prior.OUTPUT = prior.shared.OUTPUT = OUTPUT
    previous.probe.measured = client.measure
    previous.probe.diagnosis.enforce = enforce
    original_record = prior.shared.write_immutable_record
    original_png = prior.shared.write_png
    original_capture = previous.probe.capture
    original_replay = previous.strict_replay

    def record(path, value):
        maximum = 2 * len((json.dumps(value, indent=2, sort_keys=True) + "\n").encode())
        with client.reserve(maximum):
            return original_record(path, value)

    def png(relative, rgb):
        if str(rgb.dtype) != "uint8" or len(rgb.shape) != 3 or rgb.shape[2] != 3:
            raise ValueError("bounded RGB uint8 PNG required")
        with client.reserve(4 * rgb.nbytes + 1024 ** 2):
            return original_png(relative, rgb)

    def capture(command, prefix, *, timeout=180):
        with client.reserve(2 * FILE_LIMIT):
            return original_capture(budget.limited_command(command, FILE_LIMIT), prefix, timeout=timeout)

    def replay(path, media, consume, receipt, *, timeout=180):
        with client.reserve(FILE_LIMIT + 1024 ** 2):
            return original_replay(path, media, consume, receipt, timeout=timeout,
                                   command=budget.limited_command(replay_command(path), FILE_LIMIT))

    prior.shared.write_immutable_record = record
    prior.shared.write_png = png
    previous.probe.capture = capture
    previous.strict_replay = replay


def copy_file(source, target, digest):
    identity = prior.shared.identity(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    actual = hashlib.sha256()
    with source.open("rb") as incoming, target.open("xb") as outgoing:
        while block := incoming.read(1024 ** 2):
            actual.update(block)
            outgoing.write(block)
    if actual.hexdigest() != digest or prior.shared.identity(source) != identity:
        raise ValueError("retained source drift during immutable copy")


def reuse(plan, client):
    failed = prior.read(SOURCE / "failure_rows.json")["rows"]
    files, media_rows, outcomes = {}, [], Counter()
    for index in range(RETAINED):
        relative = f"transactions/{index:04d}.json"
        row = prior.shared.read_verified_json(SOURCE / relative, failed[index]["record_sha256"])
        original = plan["videos"][index]
        if row["index"] != index or row["video_id"] != original["video_id"] or row["role"] != original["role"]:
            raise ValueError("retained original/index/role drift")
        if row["config_sha256"] != plan["active_config_sha256"] or row["model_sha256"] != prior.shared.MODEL_SHA256:
            raise ValueError("retained detector/config binding drift")
        media_path = SOURCE / "media" / f"{index:04d}.json"
        media = prior.shared.read_verified_json(media_path, row["media_record_sha256"])
        if any(media[key] != original[key] for key in
               ("video_id", "role", "binary_label", "official_split", "subject_id", "media_relpath", "byte_size")):
            raise ValueError("retained native/frozen original drift")
        transaction = prior.shared.technical_transaction(media)
        transaction.update(media_sha256=media["media_sha256"], media_record_sha256=prior.sha(media_path))
        if any(row[key] != value for key, value in transaction.items()
               if key not in {"detector_status", "final_k1_action"}):
            raise ValueError("retained fixed-middle transaction drift")
        attempt = SOURCE / "attempts" / f"{index:04d}.json"
        if prior.read(attempt) != {"index": index, "video_id": original["video_id"], "role": original["role"], "status": "started"}:
            raise ValueError("retained attempt identity drift")
        replay = SOURCE / "replay" / f"{index:04d}.json"
        evidence = prior.shared.read_verified_json(replay, row["replay_record_sha256"])
        stderr = SOURCE / "replay" / f"{index:04d}.stderr"
        if (evidence["strict_success"] is not True or evidence["frames_verified"] != media["frame_count"]
                or evidence["frame_count"] != media["frame_count"] or evidence["returncode"] or evidence["stderr_bytes"]
                or evidence["failure"] is not None or evidence["frame_substitution"] is not False
                or evidence["decoded_rgb_sequence_sha256"] != media["decoded_rgb_sequence_sha256"]
                or stderr.stat().st_size or prior.sha(stderr) != evidence["stderr_sha256"]):
            raise ValueError("retained strict RGB replay receipt drift")
        _, assets = prior.shared.images.validate_unit(
            {"transaction": transaction, "media_path": str(media_path)}, SOURCE, index, 4,
            plan["active_config_sha256"], failed[index]["record_sha256"])
        files.update(assets)
        files[relative] = failed[index]["record_sha256"]
        files[f"media/{index:04d}.json"] = row["media_record_sha256"]
        files[f"attempts/{index:04d}.json"] = prior.sha(attempt)
        files[f"replay/{index:04d}.json"] = row["replay_record_sha256"]
        files[f"replay/{index:04d}.stderr"] = evidence["stderr_sha256"]
        files.update(media["probe_evidence_sha256"])
        media_rows.append(media)
        outcomes[row["detector_status"]] += 1
        if index % 20 == 0:
            print("RETAINED289_PIXEL", index + 1, flush=True)
    if outcomes != {"success": 441, "failed": 6}:
        raise ValueError("retained441 success/six detector-failure rows required")
    files["release_integrity.json"] = prior.sha(SOURCE / "release_integrity.json")
    files["extraction.stderr"] = prior.sha(SOURCE / "extraction.stderr")
    total = sum((SOURCE / relative).stat().st_size for relative in files)
    with client.reserve(total):
        for relative, digest in files.items():
            copy_file(SOURCE / relative, OUTPUT / relative, digest)
    for index in range(RETAINED):
        verify_probe(index)
    quarantined = {}
    for folder in ("attempts", "media", "probe", "replay", "frames", "crops"):
        for path in (SOURCE / folder).iterdir():
            if path.name[:4].isdigit() and int(path.name[:4]) >= RETAINED:
                for file in ([path] if path.is_file() else path.rglob("*")):
                    if file.is_file():
                        relative = file.relative_to(SOURCE).as_posix()
                        with client.reserve(file.stat().st_size):
                            digest = prior.sha(file)
                            copy_file(file, OUTPUT / "quarantine" / relative, digest)
                        quarantined[relative] = digest
    prior.write(OUTPUT / "retained_readback.json", {
        "originals": RETAINED, "detector_success": 441, "detector_failure": 6,
        "asset_references": 1770, "source_record_and_asset_sha256": files,
        "retained_decode_calls": 0, "retained_detector_calls": 0,
        "pixel_readback_completed": True, "quarantined_uncommitted_sha256": quarantined})
    return media_rows


def stage_remaining(plan, client):
    check_remaining(plan)
    prior.guard(plan)
    if prior.list_headers() != plan["headers"] or prior.read_file_headers(prior.ARCHIVE) != plan["crc_headers"]:
        raise ValueError("current archive typed/native CRC headers drift")
    selected = {plan["videos"][index]["media_relpath"]: plan["videos"][index]
                for index in plan["remaining_indices"]}
    temporary = OUTPUT / "temporary"
    temporary.mkdir()
    errors = OUTPUT / "selective-extraction.stderr"
    command = [str(prior.EXTRACTOR), "-xf", str(prior.ARCHIVE), "-C", str(temporary),
               "--no-same-owner", "--no-same-permissions", "--keep-old-files", "--", *selected]
    with client.reserve(sum(row["byte_size"] for row in plan["videos"]) + FILE_LIMIT):
        with errors.open("xb") as stderr:
            result = subprocess.run(budget.limited_command(command, FILE_LIMIT), stdin=subprocess.DEVNULL,
                                    stdout=subprocess.DEVNULL, stderr=stderr, check=False,
                                    timeout=max(0.001, plan["deadline_unix_seconds"] - time.time()))
        if result.returncode or errors.stat().st_size:
            raise ValueError("selective extraction strict exit/stderr failure")
        pins = prior.read(SOURCE / "release_integrity.json")["video_payload_pins"]
        actual, checked = set(), {}
        directories = {parent.as_posix() for name in selected for parent in Path(name).parents if parent != Path(".")}
        for path in temporary.rglob("*"):
            relative, entry = path.relative_to(temporary).as_posix(), path.lstat()
            if stat.S_ISDIR(entry.st_mode):
                if relative not in directories:
                    raise ValueError("unexpected selective extraction directory")
                continue
            if not stat.S_ISREG(entry.st_mode) or relative not in selected:
                raise ValueError("selective extraction added an unrequested/unsafe file")
            crc, digest = 0, hashlib.sha256()
            with path.open("rb") as stream:
                while block := stream.read(1024 ** 2):
                    enforce(client.measure(os.getpgrp()))
                    crc = zlib.crc32(block, crc)
                    digest.update(block)
            pin = {"crc32": crc, "sha256": digest.hexdigest(), "byte_size": entry.st_size}
            if pin != pins[relative]:
                raise ValueError("remaining original native CRC/size/SHA drift")
            actual.add(relative)
            checked[relative] = pin
        if actual != set(selected):
            raise ValueError("exact153 selected extracted originals required")
        prior.write(OUTPUT / "selective_staging.json", {
            "new_extracted_videos": 153, "video_payload_bytes": sum(pin["byte_size"] for pin in checked.values()),
            "source_pins": checked, "extractor_returncode": result.returncode, "extractor_stderr_bytes": 0,
            "extractor_stderr_sha256": prior.sha(errors), "command": command,
            "full600_extraction_repeated": False, "archive_rehashed": False})
    prior.guard(plan)
    print("SELECTIVE289_STAGE_OK 153", flush=True)


def worker(plan, client):
    import cv2
    import onnxruntime as ort
    check_remaining(plan)
    media_rows = reuse(plan, client)
    stage_remaining(plan, client)
    options = ort.SessionOptions()
    options.intra_op_num_threads = options.inter_op_num_threads = 1
    session = ort.InferenceSession(str(prior.shared.retained.MODEL), sess_options=options,
                                  providers=["CPUExecutionProvider"])
    if session.get_providers() != ["CPUExecutionProvider"]:
        raise ValueError("CPU-only inference required")
    cv2.setNumThreads(1)
    previous_signature, consecutive = None, 0
    try:
        for index in plan["remaining_indices"]:
            enforce(client.measure(os.getpgrp()))
            row, media = previous.produce_unit(plan, index, plan["videos"][index], session)
            media_rows.append(media)
            signature = previous.failure_signature(media)
            consecutive = consecutive + 1 if signature and signature == previous_signature else int(signature is not None)
            previous_signature = signature
            print("CASIA289", index, row["role"], row["detector_status"], media["failure_reason"], flush=True)
            if consecutive >= 3:
                prior.write(OUTPUT / "systemic_stop.json", {"index": index, "signature": signature,
                                                         "consecutive": consecutive, "automatic_retry": False})
                raise RuntimeError("three consecutive same strict-probe failures")
        findings = prior.shared.exact_checks(media_rows, {row["video_id"]: row for row in plan["videos"]})
        prior.write(OUTPUT / "content_checks.json", {
            "exact_groups": findings, "forbidden_exact_crossings": 0,
            "near_duplicate_independence_certified": False, "joined_cross_dataset_ancestry_certified": False})
        prior.write(OUTPUT / "worker_completion.json", {
            "transactions": 600, "video_crc_checked": 600,
            "native_frames": sum(row["frame_count"] for row in media_rows),
            "video_payload_bytes": sum(row["byte_size"] for row in media_rows),
            "provider": ["CPUExecutionProvider"], "gpu_seconds": 0, "model_scores": 0, "fitted_scores": 0,
            "retained_without_decode_or_inference": RETAINED, "new_attempts": 153})
    finally:
        prior.cleanup()


def check_remaining(plan):
    if len(plan["videos"]) != 600 or plan["remaining_indices"] != list(range(RETAINED, 600)):
        raise ValueError("only the exact153 previously uncommitted originals may run")


def verify(plan, client):
    with client.reserve(2 * 1024 ** 3):
        records, transports = {}, Counter()
        for index in range(600):
            media = verify_probe(index)
            records.update(media["probe_evidence_sha256"])
            if media["decode_status"] == "decoded":
                transports[media["timestamp_transport"]] += 1
        result = prior.verify(plan)
        prior.write(OUTPUT / "probe_readback.json", {
            "originals": 600, "per_probe_sha256": records, "timestamp_transports": dict(transports),
            "full_readback_sha256": prior.sha(OUTPUT / "readback.json"),
            "selected": result["selected"], "pre_detector_failure": result["pre_detector_failure"]})


def supervise(plan):
    binding = {"parent_pid": os.getpid(), "plan_sha256": prior.sha(OUTPUT / "plan.json")}
    prior.write(OUTPUT / "lease.json", binding)
    budget.initialize(OBSERVER, binding)
    scanner, process, failure, readback = None, None, None, None
    peaks = {"rss_bytes": 0, "temporary_bytes": 0, "output_bytes": 0}
    client = budget.Client(OBSERVER, binding, usage, enforce)
    started = time.monotonic()
    try:
        scanner = subprocess.Popen([sys.executable, str(Path(__file__)), "--scan"], start_new_session=True)
        budget.publish(OUTPUT / "lease.json", {**binding, "scanner_pid": scanner.pid})
        while not (OBSERVER / "snapshot.json").exists():
            if scanner.poll() is not None:
                raise RuntimeError("initial storage scanner failed")
            if time.time() >= plan["deadline_unix_seconds"]:
                raise TimeoutError("initial storage preflight deadline")
            if usage(scanner.pid)["rss_bytes"] > CAPS["rss_bytes"]:
                raise budget.BudgetError("initial scanner RSS cap")
            time.sleep(0.1)
        enforce(client.measure(os.getpgrp()))
        for mode in ("--worker", "--verify"):
            process = subprocess.Popen([sys.executable, str(Path(__file__)), mode], start_new_session=True)
            while True:
                if scanner.poll() is not None:
                    raise RuntimeError("storage scanner exited unexpectedly")
                value = client.measure(process.pid)
                peaks = {key: max(peaks[key], value[key]) for key in peaks}
                enforce(value)
                try:
                    if process.wait(timeout=0.5):
                        raise RuntimeError(mode + " failed; no retry")
                    break
                except subprocess.TimeoutExpired:
                    continue
            process = None
        readback = prior.read(OUTPUT / "readback.json")
        prior.shared.check_bindings(plan["sources"])
        prior.guard(plan)
        retained = prior.read(OUTPUT / "retained_readback.json")
        for relative, digest in retained["source_record_and_asset_sha256"].items():
            if prior.sha(SOURCE / relative) != digest or prior.sha(OUTPUT / relative) != digest:
                raise ValueError("immutable retained source/copy changed during resume")
    except Exception as error:
        failure = type(error).__name__ + ": " + str(error)
        print("CASIA289_FAILED", failure, flush=True)
    finally:
        for child in (process, scanner):
            if child is not None:
                budget.stop_group(child)
        signal.setitimer(signal.ITIMER_REAL, 0)
        prior.shared.retained.arm_deadline(authority()["deadline_unix_seconds"])
        cleanup = subprocess.Popen([sys.executable, str(Path(__file__)), "--cleanup"], start_new_session=True)
        try:
            if cleanup.wait(timeout=30):
                raise RuntimeError("owned selective staging cleanup failed")
        except Exception as error:
            budget.stop_group(cleanup)
            failure = (failure + "; " if failure else "") + type(error).__name__ + ": " + str(error)
        if failure is None:
            try:
                budget.scan_once(ROOTS, OBSERVER, binding, prior.shared.retained.tree_bytes)
                value = client.measure(os.getpgrp())
                peaks = {key: max(peaks[key], value[key]) for key in peaks}
                enforce(value, work=False)
            except Exception as error:
                failure = type(error).__name__ + ": " + str(error)
                print("CASIA289_FINAL_RESOURCE_FAILURE", failure, flush=True)
    if failure is not None:
        from complete_casia287 import partial_ledger
        transactions = {int(path.stem): prior.read(path) for path in (OUTPUT / "transactions").glob("*.json")}
        attempts = {int(path.stem): prior.read(path) for path in (OUTPUT / "attempts").glob("*.json")}
        prior.write(OUTPUT / "failure_rows.json", {
            "rows": partial_ledger(plan["videos"], transactions, attempts), "failure": failure,
            "automatic_retry": False, "retained_originals_preserved": True})
    result = {
        "checkpoint": 289, "dataset": "CASIA-FASD", "originals": 600,
        "accounting_complete": failure is None and readback is not None,
        "image_export_software_complete": failure is None and readback is not None and readback["detector_success"] > 0,
        "primary_image_preprocessing_complete": False, "local_audit_complete": False, "failure": failure,
        "retained_without_decode_or_inference": RETAINED, "remaining_authorized": 153,
        "automatic_retry": False, "attempts": 1, "caps": CAPS, "sampled_peaks": peaks,
        "package_wall_seconds": time.time() - authority()["started_unix_seconds"],
        "supervised_wall_seconds": time.monotonic() - started,
        **{key: readback[key] if readback else None for key in
           ("selected", "detector_success", "detector_failure", "pre_detector_failure", "native_frames", "strict_replay_count")},
        "gpu_seconds": 0, "model_scores": 0, "fitted_scores": 0, "scientific_readiness": False}
    prior.write(OUTPUT / "resources.json", result)
    prior.write(SUMMARY, {
        **result, "private_record_sha256": {path.name: prior.sha(path) for path in OUTPUT.glob("*.json")},
        "role_originals": prior.ROLES, "role_subjects": prior.GROUPS,
        "audit_summary_statuses_changed": False})
    print("CASIA289_TERMINAL", json.dumps(result), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    for mode in ("run-once", "scan", "worker", "verify", "cleanup"):
        modes.add_argument("--" + mode, action="store_true")
    args = parser.parse_args()
    approval = authority()
    prior.shared.retained.arm_deadline(
        approval["deadline_unix_seconds"] - (0 if args.cleanup else SHUTDOWN_RESERVE_SECONDS))
    prior.OUTPUT = prior.shared.OUTPUT = OUTPUT
    if not args.run_once:
        plan, lease = prior.read(OUTPUT / "plan.json"), prior.read(OUTPUT / "lease.json")
        binding = {key: lease[key] for key in ("parent_pid", "plan_sha256")}
        if lease["parent_pid"] != os.getppid() or lease["plan_sha256"] != prior.sha(OUTPUT / "plan.json") or os.getsid(0) != os.getpid():
            raise ValueError("single supervised CASIA289 child/plan lease required")
        if args.cleanup:
            prior.cleanup()
            return 0
        if args.scan:
            budget.scan_forever(ROOTS, OBSERVER, binding, prior.shared.retained.tree_bytes)
            return 0
        prior.shared.check_bindings(plan["sources"])
        prior.guard(plan)
        client = budget.Client(OBSERVER, binding, usage, enforce)
        configure(client)
        worker(plan, client) if args.worker else verify(plan, client)
        return 0
    prior.write(OUTPUT / "supervisor.json", {"pid": os.getpid(), "source_sha256": prior.sha(Path(__file__))})
    with (OUTPUT / "execution.log").open("xb", buffering=0) as log:
        os.dup2(log.fileno(), 1)
        os.dup2(log.fileno(), 2)
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    try:
        return 0 if supervise(make_plan())["accounting_complete"] else 1
    except Exception as error:
        prior.write(OUTPUT / "package_failure.json", {
            "error_type": type(error).__name__, "message": str(error), "automatic_retry": False,
            "accounting_complete": False, "primary_image_preprocessing_complete": False})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
