"""One additive CASIA600 recovery after the demonstrated strict-probe correction."""

from __future__ import annotations

import argparse
from collections import Counter
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
import zlib

import casia_probe287 as probe
import casia_counts287 as counts
import diagnose_casia287 as diagnostic
from msu_replay282 import strict_replay

prior = diagnostic.prior
PRIOR = prior.OUTPUT
OUTPUT = diagnostic.OUTPUT
SUMMARY = prior.ROOT / "results/phase1/casia-preprocessing287-recovery-v1.json"


def make_plan():
    approval = diagnostic.authority()
    plan = diagnostic.bound_prior()
    proof = prior.read(OUTPUT / "native_fix_validation.json")
    if proof["probe_source_sha256"] != prior.sha(Path(probe.__file__)) or proof["count_source_sha256"] != prior.sha(Path(counts.__file__)) or proof["no_manual_timestamp_or_frame_assignment"] is not True:
        raise ValueError("validated probe source and native timestamp guard required")
    if proof["all_predeclared_sources_passed"] is not True or [row["index"] for row in proof["rows"]] != [0, 1, 8]:
        raise ValueError("same normal/low/high originals must pass")
    for row in proof["rows"]:
        replay = prior.shared.read_verified_json(OUTPUT / "native-validation-final" / f"{row['index']:04d}" / "strict-replay.json", row["strict_replay_sha256"])
        if replay["strict_success"] is not True or replay["stderr_bytes"] or replay["returncode"] or replay["frames_verified"] != row["frame_count"]:
            raise ValueError("same-original full strict RGB proof required")
    current_tools = {name: subprocess.run([name, "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
                     for name in ("ffmpeg", "ffprobe")}
    if current_tools != proof["toolchain"] or current_tools != plan["toolchain"]:
        raise ValueError("unchanged accepted toolchain required")
    sources = dict(plan["sources"])
    for path in (Path(__file__), Path(probe.__file__), Path(counts.__file__), Path(diagnostic.__file__),
                 prior.ROOT / "scripts/validate_casia287_fix.py", prior.ROOT / "scripts/validate_casia287_representatives.py",
                 prior.ROOT / "scripts/validate_casia287_native_fix.py",
                 prior.ROOT / "tests/test_casia_recovery.py",
                 prior.ROOT / "docs/286-review-doc285-casia-systematic-probe-blocker.md",
                 OUTPUT / "owner_approval.json", OUTPUT / "diagnosis.json", OUTPUT / "fix_validation.json",
                 OUTPUT / "fix-media.json", OUTPUT / "representative_selection.json", OUTPUT / "native_validation_selection.json",
                 OUTPUT / "native_fix_validation.json",
                 OUTPUT / "diagnostic/fixed-strict-replay.json",
                 OUTPUT / "diagnostic/fixed-strict-replay.stderr",
                 PRIOR / "plan.json", PRIOR / "resources.json", PRIOR / "release_integrity.json",
                 PRIOR / "readback.json", PRIOR / "full_manifest.json"):
        sources[str(path)] = prior.sha(path)
    for path in (OUTPUT / "diagnostic").glob("*"):
        if path.is_file():
            sources[str(path)] = prior.sha(path)
    for path in (OUTPUT / "representatives").rglob("*"):
        if path.is_file():
            sources[str(path)] = prior.sha(path)
    for path in (OUTPUT / "native-validation-final").rglob("*"):
        if path.is_file():
            sources[str(path)] = prior.sha(path)
    plan.update(checkpoint=287, sources=sources, caps=diagnostic.CAPS,
                deadline_unix_seconds=approval["deadline_unix_seconds"],
                recovery_of_blocked285=True, images_reused_from285=0, systemic_stop_consecutive=3)
    prior.shared.check_bindings(sources)
    diagnostic.enforce(probe.measured(os.getpgrp()))
    prior.write(OUTPUT / "plan.json", plan)
    return plan


def stage_release(plan):
    prior.guard(plan)
    if prior.list_headers() != plan["headers"] or prior.read_file_headers(prior.ARCHIVE) != plan["crc_headers"]:
        raise ValueError("current archive typed/header-CRC commitments differ")
    previous = prior.read(PRIOR / "release_integrity.json")
    temporary = OUTPUT / "temporary"
    temporary.mkdir()
    stderr = OUTPUT / "extraction.stderr"
    with stderr.open("xb") as errors:
        command = [str(prior.EXTRACTOR), "-xf", str(prior.ARCHIVE), "-C", str(temporary),
                   "--no-same-owner", "--no-same-permissions", "--keep-old-files"]
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=errors, stdin=subprocess.DEVNULL,
                                timeout=max(0.001, plan["deadline_unix_seconds"] - time.time()), check=False)
    if result.returncode or stderr.stat().st_size:
        raise ValueError("strict recovery extraction exit/stderr; retained diagnostics")
    expected = {row["media_relpath"]: row for row in plan["videos"]}
    headers = {row["relpath"]: row for row in plan["crc_headers"]}
    pins = {}
    for path in temporary.rglob("*"):
        relative, value = path.relative_to(temporary).as_posix(), path.lstat()
        if stat.S_ISDIR(value.st_mode):
            if relative not in headers or headers[relative]["kind"] != "directory":
                raise ValueError("unexpected extracted directory")
            continue
        if not stat.S_ISREG(value.st_mode) or relative not in expected or value.st_size != expected[relative]["byte_size"]:
            raise ValueError("unexpected/unsafe/wrong-size extracted video")
        crc, digest = 0, hashlib.sha256()
        with path.open("rb") as source:
            while block := source.read(1024 ** 2):
                if time.time() >= plan["deadline_unix_seconds"]:
                    raise TimeoutError("recovery extraction CRC/SHA deadline")
                crc = zlib.crc32(block, crc)
                digest.update(block)
        pin = {"crc32": crc, "sha256": digest.hexdigest(), "byte_size": value.st_size}
        if pin != previous["video_payload_pins"][relative] or crc != headers[relative]["crc32"]:
            raise ValueError("current extracted payload differs from native CRC/retained SHA")
        pins[relative] = pin
    if set(pins) != set(expected):
        raise ValueError("exact600 guarded extracted originals required")
    prior.guard(plan)
    prior.write(OUTPUT / "release_integrity.json", {
        "archive_sha256": previous["archive_sha256"], "archive_bytes": plan["archive_identity"][2],
        "archive_identity": plan["archive_identity"], "archive_rehashed": False,
        "archive_sha_reused_with_exact_identity_and_current_header_crc_guards": True,
        "prior_release_integrity_sha256": prior.sha(PRIOR / "release_integrity.json"),
        "publisher_checksum_verified": False, "extracted_videos": 600,
        "video_payload_bytes": sum(pin["byte_size"] for pin in pins.values()),
        "extractor_command": command, "extractor_returncode": result.returncode,
        "extractor_stderr_bytes": 0, "extractor_stderr_sha256": prior.sha(stderr),
        "independent_unpacked_crc32_verified": True, "video_payload_pins": pins})
    print("RECOVERY287_STAGE_OK 600", flush=True)


def produce_unit(plan, index, original, session):
    path = OUTPUT / "temporary" / original["media_relpath"]
    identity = prior.shared.identity(path)
    pin = prior.read(OUTPUT / "release_integrity.json")["video_payload_pins"][original["media_relpath"]]
    if identity[2] != original["byte_size"] or prior.sha(path) != pin["sha256"]:
        raise ValueError("fixed original SHA/size drift")
    prior.write(OUTPUT / "attempts" / f"{index:04d}.json", {
        "index": index, "video_id": original["video_id"], "role": original["role"], "status": "started"})
    prefix = OUTPUT / "probe" / f"{index:04d}"
    media = {key: original[key] for key in ("video_id", "role", "binary_label", "official_split", "subject_id", "media_relpath")}
    media.update(media_sha256=pin["sha256"], byte_size=identity[2], archive_crc_validated=True,
                 **probe.probe_video(path, prefix, timeout_seconds=max(1, min(180, int(plan["deadline_unix_seconds"] - time.time())))))
    if prior.shared.identity(path) != identity:
        raise ValueError("source changed during corrected strict probe")
    media["probe_evidence_sha256"] = {file.relative_to(OUTPUT).as_posix(): prior.sha(file) for file in prefix.iterdir()}
    media_path = OUTPUT / "media" / f"{index:04d}.json"
    prior.write(media_path, media)
    transaction = prior.shared.technical_transaction(media)
    transaction.update(media_sha256=pin["sha256"], media_record_sha256=prior.sha(media_path))
    row = {**transaction, "index": index, "replacement": False, "model_sha256": prior.shared.MODEL_SHA256,
           "config_sha256": plan["active_config_sha256"], "assets": {}}
    if transaction["selected_frame"] is not None:
        selected, captured = transaction["selected_frame"], []

        def consume(order, rgb):
            if order == selected["decode_order"]:
                if hashlib.sha256(rgb.tobytes()).hexdigest() != selected["rgb_sha256"]:
                    raise ValueError("frozen middle RGB differs from native framehash")
                captured.append(rgb.copy())

        strict_replay(path, media, consume, OUTPUT / "replay" / f"{index:04d}",
                      timeout=min(180, max(0.001, plan["deadline_unix_seconds"] - time.time())))
        if len(captured) != 1:
            raise ValueError("one unchanged fixed middle frame only")
        row["replay_record_sha256"] = prior.sha(OUTPUT / "replay" / f"{index:04d}.json")
        relative = f"frames/{index:04d}.png"
        row["selected_RGB_asset"] = {"path": relative, **prior.shared.write_png(relative, captured[0])}
        prior.shared.infer_image(session, captured[0], row)
    prior.write(OUTPUT / "transactions" / f"{index:04d}.json", row)
    return row, media


def failure_signature(media):
    failure = media.get("probe_failure")
    if not failure:
        return None
    return failure["stage"] + ":" + failure["reason"].split("_stderr_", 1)[0].split(":", 1)[0]


def worker(plan):
    import cv2
    import onnxruntime as ort

    prior.shared.check_bindings(plan["sources"])
    try:
        stage_release(plan)
        options = ort.SessionOptions()
        options.intra_op_num_threads = options.inter_op_num_threads = 1
        session = ort.InferenceSession(str(prior.shared.retained.MODEL), sess_options=options, providers=["CPUExecutionProvider"])
        if session.get_providers() != ["CPUExecutionProvider"]:
            raise ValueError("CPU-only inference required")
        cv2.setNumThreads(1)
        media_rows, previous, consecutive = [], None, 0
        for index, original in enumerate(plan["videos"]):
            prior.guard(plan)
            row, media = produce_unit(plan, index, original, session)
            media_rows.append(media)
            signature = failure_signature(media)
            consecutive = consecutive + 1 if signature and signature == previous else int(signature is not None)
            previous = signature
            print("CASIA287", index, row["role"], row["detector_status"], media["failure_reason"], flush=True)
            if consecutive >= plan["systemic_stop_consecutive"]:
                prior.write(OUTPUT / "systemic_stop.json", {"index": index, "failure_signature": signature,
                                                           "consecutive": consecutive, "automatic_retry": False})
                raise RuntimeError("three consecutive same strict-probe failures: " + signature)
        findings = prior.shared.exact_checks(media_rows, {row["video_id"]: row for row in plan["videos"]})
        prior.write(OUTPUT / "content_checks.json", {"exact_groups": findings, "forbidden_exact_crossings": 0,
                    "near_duplicate_independence_certified": False, "joined_cross_dataset_ancestry_certified": False})
        prior.shared.check_bindings(plan["sources"])
        prior.guard(plan)
        prior.write(OUTPUT / "worker_completion.json", {
            "transactions": 600, "video_crc_checked": 600, "native_frames": sum(row["frame_count"] for row in media_rows),
            "video_payload_bytes": sum(row["byte_size"] for row in media_rows), "provider": ["CPUExecutionProvider"],
            "gpu_seconds": 0, "model_scores": 0, "fitted_scores": 0})
    finally:
        prior.cleanup()


def verify_probes(plan):
    all_records, transports = {}, Counter()
    for index in range(600):
        media = prior.read(OUTPUT / "media" / f"{index:04d}.json")
        folder = OUTPUT / "probe" / f"{index:04d}"
        expected = media["probe_evidence_sha256"]
        if {file.relative_to(OUTPUT).as_posix() for file in folder.iterdir()} != set(expected):
            raise ValueError("exact durable per-original probe evidence set required")
        for relative, digest in expected.items():
            if prior.sha(OUTPUT / relative) != digest:
                raise ValueError("stage-specific raw probe evidence drift")
        saved = prior.shared.read_verified_json(folder / "probe_result.json", media["probe_result_sha256"])
        if any(media[key] != value for key, value in saved.items()):
            raise ValueError("saved strict-probe result/media drift")
        for path in folder.glob("*.json"):
            if path.name == "probe_result.json":
                continue
            command = prior.read(path)
            for kind in ("stdout", "stderr"):
                artifact = path.with_suffix("." + kind)
                if artifact.stat().st_size != command[kind + "_bytes"] or prior.sha(artifact) != command[kind + "_sha256"]:
                    raise ValueError("probe command exit/output commitment drift")
            if media["decode_status"] == "decoded" and (command["returncode"] or command["stderr_bytes"]):
                raise ValueError("accepted probe has nonzero exit/stderr")
        if media["decode_status"] == "decoded":
            raw = json.loads((folder / "original-metadata.stdout").read_text())
            packets = json.loads((folder / "native-packets.stdout").read_text()) if (folder / "native-packets.stdout").exists() else None
            generated = json.loads((folder / "guarded-genpts.stdout").read_text()) if (folder / "guarded-genpts.stdout").exists() else None
            count_evidence = prior.read(folder / "native-count.json") if (folder / "native-count.json").exists() else None
            if count_evidence is not None and (count_evidence["source_sha256"] != media["media_sha256"] or count_evidence["source_bytes"] != media["byte_size"]):
                raise ValueError("native coded-picture evidence/source drift")
            computed = probe.parse_evidence(raw, (folder / "native-framehash.stdout").read_text(),
                                             packets=packets, generated=generated, count_evidence=count_evidence)
            if any(media[key] != value for key, value in computed.items()):
                raise ValueError("full saved probe/native clock/framehash readback drift")
            transports[media["timestamp_transport"]] += 1
        elif not media.get("probe_failure") or media["failure_reason"] != media["probe_failure"]["stage"] + ":" + media["probe_failure"]["reason"]:
            raise ValueError("remaining failure lacks durable exact stage/reason")
        all_records.update(expected)
    return {"per_probe_sha256": all_records, "timestamp_transports": dict(transports), "originals": 600}


def verify(plan):
    evidence = verify_probes(plan)
    result = prior.verify(plan)
    prior.write(OUTPUT / "probe_readback.json", {**evidence, "full_readback_sha256": prior.sha(OUTPUT / "readback.json"),
                                               "selected": result["selected"], "pre_detector_failure": result["pre_detector_failure"]})


def failed_ledger(plan, failure):
    rows = []
    for index, original in enumerate(plan["videos"]):
        path = OUTPUT / "transactions" / f"{index:04d}.json"
        rows.append({**{key: original[key] for key in ("video_id", "role", "binary_label", "subject_id", "official_split")},
                     "index": index, "execution_status": "attempted_unaccepted_package" if path.exists() else "not_attempted_after_stop",
                     "record_sha256": prior.sha(path) if path.exists() else None, "selected_frame": None,
                     "final_k1_action": "non_accept", "model_score": None, "retain_original_denominator": True, "failure": failure})
    prior.write(OUTPUT / "failure_rows.json", {"rows": rows, "automatic_retry": False,
                                            "accounting_complete": False, "primary_image_preprocessing_complete": False})


def supervise(plan):
    prior.write(OUTPUT / "attempt_lock.json", {"parent_pid": os.getpid(), "plan_sha256": prior.sha(OUTPUT / "plan.json"),
                                            "recovery_attempts_authorized": 1, "automatic_retry": False})
    process, failure, readback = None, None, None
    peaks = {"rss_bytes": 0, "output_bytes": 0, "temporary_bytes": 0}
    started = time.monotonic()
    try:
        for mode in ("--worker", "--verify"):
            process = subprocess.Popen([sys.executable, str(Path(__file__)), mode], start_new_session=True)
            while True:
                value = probe.measured(process.pid)
                peaks = {key: max(peaks[key], value[key]) for key in peaks}
                diagnostic.enforce(value)
                try:
                    if process.wait(timeout=2):
                        raise RuntimeError(mode + " failed; no retry")
                    break
                except subprocess.TimeoutExpired:
                    continue
            process = None
        readback = prior.read(OUTPUT / "readback.json")
        ledger = prior.shared.read_verified_json(OUTPUT / "full_manifest.json", readback["full_manifest_sha256"])
        if any(readback[key] != value for key, value in prior.validate_manifest(plan, ledger["rows"]).items()):
            raise ValueError("final full600 counts drift")
        for relative, digest in {**readback["per_unit_sha256"], **readback["asset_sha256"],
                                 **prior.read(OUTPUT / "probe_readback.json")["per_probe_sha256"]}.items():
            if prior.sha(OUTPUT / relative) != digest:
                raise ValueError("final record/image/probe output drift")
        prior.shared.check_bindings(plan["sources"])
        prior.guard(plan)
        value = probe.measured(os.getpgrp())
        value["rss_bytes"] = max(value["rss_bytes"], resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024)
        peaks = {key: max(peaks[key], value[key]) for key in peaks}
        diagnostic.enforce(peaks)
    except Exception as error:
        failure = type(error).__name__ + ": " + str(error)
        print("RECOVERY287_FAILED", failure, flush=True)
    finally:
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
        prior.cleanup()
    if failure:
        failed_ledger(plan, failure)
    result = {
        "checkpoint": 287, "dataset": "CASIA-FASD", "accounting_complete": failure is None and readback is not None,
        "image_export_software_complete": failure is None and readback is not None and readback["detector_success"] > 0,
        "primary_image_preprocessing_complete": False, "local_audit_complete": False,
        "failure": failure, "attempts": 1, "automatic_retry": False, "caps": diagnostic.CAPS,
        "sampled_peaks": peaks, "package_wall_seconds": time.time() - diagnostic.authority()["started_unix_seconds"],
        "supervised_wall_seconds": time.monotonic() - started, "gpu_seconds": 0,
        "originals": 600, **{key: readback[key] if readback else None for key in
            ("selected", "detector_success", "detector_failure", "pre_detector_failure", "native_frames", "strict_replay_count")},
        "visual_inspection_pending": failure is None and readback is not None and readback["detector_success"] > 0,
        "scientific_readiness": False}
    prior.write(OUTPUT / "resources.json", result)
    prior.write(SUMMARY, {**result, "role_originals": prior.ROLES, "role_subjects": prior.GROUPS,
                         "audit_summary_statuses_changed": False, "images_reused_from285": 0,
                         "private_record_sha256": {path.name: prior.sha(path) for path in OUTPUT.glob("*.json")},
                         "active_config_sha256": plan["active_config_sha256"], "model_scores": 0, "fitted_scores": 0})
    print("RECOVERY287_TERMINAL", json.dumps(result), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    for mode in ("run-once", "worker", "verify"):
        modes.add_argument("--" + mode, action="store_true")
    args = parser.parse_args()
    approval = diagnostic.authority()
    prior.shared.retained.arm_deadline(approval["deadline_unix_seconds"])
    if args.worker or args.verify:
        plan = prior.read(OUTPUT / "plan.json")
        lease = prior.read(OUTPUT / "attempt_lock.json")
        if lease["parent_pid"] != os.getppid() or lease["plan_sha256"] != prior.sha(OUTPUT / "plan.json") or os.getsid(0) != os.getpid():
            raise ValueError("one supervised recovery child/plan lease required")
        prior.OUTPUT = OUTPUT
        prior.shared.OUTPUT = OUTPUT
        worker(plan) if args.worker else verify(plan)
        return 0
    if (OUTPUT / "supervisor.json").exists():
        raise FileExistsError("single additional CASIA recovery; no retry")
    prior.write(OUTPUT / "supervisor.json", {"pid": os.getpid(), "runner_sha256": prior.sha(Path(__file__))})
    with (OUTPUT / "execution.log").open("xb", buffering=0) as log:
        os.dup2(log.fileno(), 1)
        os.dup2(log.fileno(), 2)
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    try:
        result = supervise(make_plan())
        return 0 if result["accounting_complete"] else 1
    except Exception as error:
        prior.write(OUTPUT / "package_failure.json", {"error_type": type(error).__name__, "message": str(error),
                    "accounting_complete": False, "primary_image_preprocessing_complete": False, "automatic_retry": False})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
