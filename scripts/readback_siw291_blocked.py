"""Non-accepting saved-output readback after SiW291's exact-content stop.

Never extracts, decodes, infers, changes membership, or waives the crossing gate.
"""

import argparse
from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import preprocess_siw291 as run

OUTPUT = run.OUTPUT / "blocked_closure"
IPC = Path.home() / ".cache/fas/siwmv2-blocked-readback291"
ROOTS = (*run.ROOTS, IPC)


def duplicate_groups(media):
    groups = []
    for field in ("media_sha256", "decoded_rgb_sequence_sha256"):
        indexed = defaultdict(list)
        for index, row in enumerate(media):
            if row[field] is not None:
                indexed[row[field]].append(index)
        for digest, indices in indexed.items():
            if len(indices) < 2:
                continue
            crossing = [key for key in ("official_split", "role", "binary_label")
                        if len({media[i][key] for i in indices}) > 1]
            groups.append({"kind": field, "sha256": digest, "indices": indices,
                           "video_ids": [media[i]["video_id"] for i in indices],
                           "crossed_boundaries": crossing, "forbidden": bool(crossing),
                           "participant_identity_verified": False})
    return groups


def summary(groups):
    pairs = {}
    for group in groups:
        key = tuple(group["indices"])
        if key in pairs and pairs[key] != group["crossed_boundaries"]:
            raise ValueError("byte/decoded duplicate boundary disagreement")
        pairs[key] = group["crossed_boundaries"]
    forbidden = sum(bool(value) for value in pairs.values())
    return {"duplicate_groups_by_kind": dict(Counter(g["kind"] for g in groups)),
            "unique_duplicate_member_sets": len(pairs),
            "unique_duplicated_originals": len({i for key in pairs for i in key}),
            "forbidden_unique_groups": forbidden,
            "official_train_test_crossing_groups": sum("official_split" in value for value in pairs.values()),
            "source_role_only_crossing_groups": sum("role" in value and "official_split" not in value for value in pairs.values()),
            "within_one_partition_role_class_groups": sum(not value for value in pairs.values()),
            "binary_label_crossing_groups": sum("binary_label" in value for value in pairs.values()),
            "local_audit_complete": False, "promotion_permitted": False,
            "scientific_readiness": False}


def prepare():
    run.authority()
    old = run.read(run.OUTPUT / "resources.json")
    if old["accounting_complete"] is not False or old["automatic_retry"] is not False:
        raise ValueError("preserved stopped SiW291 package required")
    original = run.read(run.OUTPUT / "plan.json")
    run.shared.check_bindings(original["sources"])
    run.guard(original)
    pins = {}
    for folder in ("attempts", "transactions", "media"):
        expected = {f"{i:04d}.json" for i in range(1680)}
        if {p.name for p in (run.OUTPUT / folder).iterdir()} != expected:
            raise ValueError("exact1680 committed originals required, not media retry")
        for path in sorted((run.OUTPUT / folder).iterdir()):
            pins[path.relative_to(run.OUTPUT).as_posix()] = run.sha(path)
    media = [run.read(run.OUTPUT / "media" / f"{i:04d}.json") for i in range(1680)]
    groups = duplicate_groups(media)
    if not summary(groups)["forbidden_unique_groups"]:
        raise ValueError("an actual forbidden-content stop is required")
    sources = [Path(__file__), run.ROOT / "tests/test_siw_blocked_closure.py",
               run.OUTPUT / "resources.json", run.OUTPUT / "failure_rows.json",
               run.OUTPUT / "archive_integrity.json", run.OUTPUT / "plan.json", run.SUMMARY]
    plan = {"checkpoint": 291, "purpose": "readback_of_committed_outputs_only_no_acceptance",
            "sources": {str(p): run.sha(p) for p in sources}, "per_record_sha256": pins,
            "original_deadline_unix_seconds": run.authority()["deadline_unix_seconds"],
            "media_decode_calls": 0, "detector_calls": 0, "membership_changed": False,
            "duplicate_summary": summary(groups)}
    run.write(OUTPUT / "plan.json", plan)
    run.write(OUTPUT / "exact_groups.json", {"groups": groups, **summary(groups)})
    print(json.dumps(summary(groups), indent=2))


def check(plan):
    run.shared.check_bindings(plan["sources"])
    original = run.read(run.OUTPUT / "plan.json")
    run.shared.check_bindings(original["sources"])
    run.guard(original)
    if plan["original_deadline_unix_seconds"] != run.authority()["deadline_unix_seconds"]:
        raise ValueError("no clock reset permitted")
    for relative, digest in plan["per_record_sha256"].items():
        if run.sha(run.OUTPUT / relative) != digest:
            raise ValueError("retained committed record changed")
    return original


def usage(group):
    value = run.shared.usage(group, OUTPUT / ".unused")
    for pid in {os.getpid(), run.read(IPC / "processes.json")["scanner_pid"]} - {group}:
        other = run.shared.usage(pid, OUTPUT / ".unused")
        value["rss_bytes"] += other["rss_bytes"]
        value["temporary_bytes"] += other["temporary_bytes"]
    return value


def duplicate_sheet(groups, rows):
    import cv2
    import numpy as np
    indices = sorted({i for group in groups for i in group["indices"]})
    lookup = {row["index"]: row for row in rows}
    canvas = np.full((((len(indices) + 3) // 4) * 180, 640, 3), 255, np.uint8)
    for slot, index in enumerate(indices):
        row = lookup[index]
        relative = f"crops/{index:04d}-224.png" if row["detector_status"] == "success" else f"frames/{index:04d}.png"
        image = cv2.imread(str(run.OUTPUT / relative), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("duplicate review image missing")
        top, left = slot // 4 * 180, slot % 4 * 160
        cv2.putText(canvas, f"{index:04d}", (left + 3, top + 15), cv2.FONT_HERSHEY_SIMPLEX, .4, (0, 0, 0), 1)
        canvas[top + 20:top + 180, left:left + 160] = cv2.resize(
            cv2.cvtColor(image, cv2.COLOR_BGR2RGB), (160, 160), interpolation=cv2.INTER_CUBIC)
    relative = "blocked_closure/visual/duplicates-00.png"
    commitment = run.shared.write_png(relative, canvas)
    restored = cv2.imread(str(run.OUTPUT / relative), cv2.IMREAD_COLOR)
    if restored is None or not np.array_equal(cv2.cvtColor(restored, cv2.COLOR_BGR2RGB), canvas):
        raise ValueError("duplicate sheet RGB reconstruction mismatch")
    return {"path": relative, "kind": "duplicates", "indices": indices, **commitment}


def readback(plan, client):
    original = check(plan)
    run.configure(client)
    assets, records, rows, media_rows = {}, {}, [], []
    for index, parent in enumerate(original["videos"]):
        row_path = run.OUTPUT / "transactions" / f"{index:04d}.json"
        media_path = run.OUTPUT / "media" / f"{index:04d}.json"
        row, media = run.read(row_path), run.read(media_path)
        if any(media[key] != parent[key] for key in ("video_id", "role", "binary_label", "official_split", "subject_id", "media_relpath")):
            raise ValueError("original/source/null-test binding drift")
        header = next(h for h in original["headers"] if h["path"] == parent["media_relpath"])
        if (media["decode_status"] != "decoded" or media["byte_size"] != parent["byte_size"]
                or media["archive_crc_validated"] is not True or media["native_crc32"] != f'{header["crc32"]:08x}'):
            raise ValueError("exact native CRC/size and existing successful decode required")
        run.verify_probe(index, media)
        txn = run.transaction(media)
        txn.update(media_sha256=media["media_sha256"], media_record_sha256=run.sha(media_path))
        if any(row[key] != value for key, value in txn.items() if key not in {"detector_status", "final_k1_action"}):
            raise ValueError("retained fixed-middle/fit-ineligibility transaction drift")
        entry, unit_assets = run.shared.images.validate_unit(
            {"transaction": txn, "media_path": str(media_path)}, run.OUTPUT, index, 4,
            original["active_config_sha256"], run.sha(row_path))
        assets.update(unit_assets)
        prefix = run.OUTPUT / "replay" / f"{index:04d}"
        replay = run.shared.read_verified_json(prefix.with_suffix(".json"), row["replay_record_sha256"])
        error_file = prefix.with_suffix(".stderr")
        if (replay["strict_success"] is not True or replay["returncode"] or replay["stderr_bytes"]
                or replay["frames_verified"] != media["frame_count"] or replay["frame_count"] != media["frame_count"]
                or replay["decoded_rgb_sequence_sha256"] != media["decoded_rgb_sequence_sha256"]
                or replay["frame_substitution"] is not False or replay["failure"] is not None
                or error_file.stat().st_size or run.sha(error_file) != replay["stderr_sha256"]):
            raise ValueError("existing strict RGB replay receipt drift")
        entry.update(index=index, official_split=parent["official_split"], subject_id=None,
                     active_config_sha256=original["active_config_sha256"], replacement=False)
        rows.append(entry)
        media_rows.append(media)
        for path in (row_path, media_path, prefix.with_suffix(".json"), error_file,
                     *(run.OUTPUT / "probe" / f"{index:04d}").iterdir()):
            records[path.relative_to(run.OUTPUT).as_posix()] = run.sha(path)
        if index % 20 == 0:
            run.enforce(client.measure(os.getpgrp()))
            print("BLOCKED_READBACK291", index, flush=True)
    if (Counter(r["role"] for r in rows if r["role"] is not None) != run.ROLES
            or sum(r["role"] is None for r in rows) != 623 or any((run.OUTPUT / "temporary").iterdir())):
        raise ValueError("source1057/test623 denominators or staging drift")
    observed = {p.relative_to(run.OUTPUT).as_posix()
                for folder in ("frames", "crops") for p in (run.OUTPUT / folder).iterdir()}
    if observed != set(assets):
        raise ValueError("exact6672 image set required; no unbound extra/missing pixels")
    groups = duplicate_groups(media_rows)
    if groups != run.read(OUTPUT / "exact_groups.json")["groups"]:
        raise ValueError("exact crossing evidence drift")
    details = summary(groups)
    if not details["forbidden_unique_groups"]:
        raise ValueError("cannot reinterpret this blocked readback as acceptance")
    with client.reserve(2 * 1024 ** 3):
        sheets = run.shared.make_sheets(original, rows)
        sheets.append(duplicate_sheet(groups, rows))
        run.write(OUTPUT / "full_manifest.json", {"dataset": "SiW-Mv2", "rows": rows,
                  "local_audit_complete": False, "promotion_permitted": False})
        receipt = {**details, "originals": len(rows), "selected": len(rows),
                   "detector_success": sum(r["detector_status"] == "success" for r in rows),
                   "detector_failure": sum(r["detector_status"] == "failed" for r in rows),
                   "pre_detector_failure": 0, "strict_replay_count": len(rows),
                   "native_frames": sum(r["frame_count"] for r in media_rows),
                   "image_assets": len(assets), "full_image_readback_complete": True,
                   "media_decode_calls": 0, "detector_calls": 0, "membership_changed": False,
                   "per_record_sha256": records, "asset_sha256": assets, "visual_sheets": sheets,
                   "full_manifest_sha256": run.sha(OUTPUT / "full_manifest.json"),
                   "exact_groups_sha256": run.sha(OUTPUT / "exact_groups.json"),
                   "checker_sha256": run.sha(Path(__file__)), "visual_inspection_completed": False,
                   "model_scores": 0, "fitted_scores": 0, "evaluation": False}
        run.write(OUTPUT / "readback.json", receipt)


def supervise(plan):
    binding = {"parent_pid": os.getpid(), "plan_sha256": run.sha(OUTPUT / "plan.json")}
    run.write(OUTPUT / "lease.json", binding)
    run.budget.initialize(IPC, binding)
    scanner = subprocess.Popen([sys.executable, str(Path(__file__)), "--scan"], start_new_session=True)
    run.budget.publish(IPC / "processes.json", {"scanner_pid": scanner.pid})
    client = run.budget.Client(IPC, binding, usage, run.enforce)
    process, failure = None, None
    peaks = run.read(run.OUTPUT / "resources.json")["sampled_peaks"]
    try:
        while not (IPC / "snapshot.json").exists():
            if scanner.poll() is not None:
                raise RuntimeError("blocked-readback native scanner failed")
            run.enforce({"rss_bytes": 0, "output_bytes": 0})
            time.sleep(.1)
        process = subprocess.Popen([sys.executable, str(Path(__file__)), "--readback"], start_new_session=True)
        while True:
            if scanner.poll() is not None:
                raise RuntimeError("blocked-readback scanner exited")
            value = client.measure(process.pid)
            peaks = {key: max(peaks[key], value[key]) for key in peaks}
            run.enforce(value)
            try:
                if process.wait(timeout=.5):
                    raise RuntimeError("saved-output readback failed; no media retry")
                break
            except subprocess.TimeoutExpired:
                continue
        check(plan)
    except Exception as error:
        failure = type(error).__name__ + ": " + str(error)
    finally:
        for child in (process, scanner):
            if child is not None:
                run.budget.stop_group(child)
    result = {"checkpoint": 291, "failure": failure, "saved_output_readback_complete": failure is None,
              "local_audit_complete": False, "promotion_permitted": False, "scientific_readiness": False,
              "caps": run.CAPS, "sampled_peaks": peaks, "media_decode_calls": 0, "detector_calls": 0,
              "membership_changed": False, "automatic_retry": False,
              "combined_wall_seconds": time.time() - run.authority()["started_unix_seconds"],
              "original_resources_sha256": run.sha(run.OUTPUT / "resources.json"),
              "closure_plan_sha256": run.sha(OUTPUT / "plan.json"), "checker_sha256": run.sha(Path(__file__))}
    run.write(OUTPUT / "resources.json", result)
    if failure is None:
        saved = run.read(OUTPUT / "readback.json")
        aggregate = {k: v for k, v in saved.items()
                     if k not in {"per_record_sha256", "asset_sha256", "visual_sheets"}}
        run.write(run.ROOT / "results/phase1/siwmv2-blocked-readback291-v1.json",
                  {**aggregate, **result, "private_readback_sha256": run.sha(OUTPUT / "readback.json"),
                   "private_resources_sha256": run.sha(OUTPUT / "resources.json")})
    print(json.dumps(result), flush=True)
    return failure is None


def visual(plan, opened, observations, crop_pass):
    check(plan)
    resources = run.read(OUTPUT / "resources.json")
    if resources["saved_output_readback_complete"] is not True or resources["failure"] is not None:
        raise ValueError("successful non-accepting saved-output readback required")
    run.enforce(resources["sampled_peaks"], work=False)
    actual = run.shared.usage(os.getpgrp(), OUTPUT / ".unused")
    actual["output_bytes"] = sum(run.shared.retained.tree_bytes(root) for root in ROOTS) + actual["temporary_bytes"]
    run.enforce(actual, work=False)
    saved = run.read(OUTPUT / "readback.json")
    for relative, digest in {**saved["per_record_sha256"], **saved["asset_sha256"]}.items():
        if run.sha(run.OUTPUT / relative) != digest:
            raise ValueError("readback/image commitment drift before actual visual record")
    rows = run.shared.read_verified_json(OUTPUT / "full_manifest.json", saved["full_manifest_sha256"])["rows"]
    expected = {sheet["path"] for sheet in saved["visual_sheets"]}
    if not observations or set(opened) != expected or len(opened) != len(expected):
        raise ValueError("all fixed/failure/duplicate sheets must actually be opened")
    lookup, totals = {row["index"]: row for row in rows}, Counter()
    for sheet in saved["visual_sheets"]:
        if run.sha(run.OUTPUT / sheet["path"]) != sheet["sha256"]:
            raise ValueError("actually opened sheet hash drift")
        for index in sheet["indices"]:
            row = lookup[index]
            totals["tiles"] += 1
            totals["face_crops" if row["detector_status"] == "success" else "selected_failure_images"] += 1
    if crop_pass and not totals["face_crops"]:
        raise ValueError("no usability pass without real crops")
    from complete_casia287 import baseline_errors
    from fas.preregistration import validate_stage
    errors = validate_stage(run.ROOT, "data-audit", frozen_root=run.FROZEN)
    if set(errors) != baseline_errors(("SiW-Mv2",)) or len(errors) != 2:
        raise ValueError("SiW must remain unaudited; other accepted summaries cannot change")
    receipt = {"checkpoint": 291, "dataset": "SiW-Mv2", "visual_inspection_completed": True,
               "sample_crop_usability_check_pass": crop_pass, "observations": observations,
               "opened_tiles": totals["tiles"], "inspected_face_crops": totals["face_crops"],
               "selected_failure_images": totals["selected_failure_images"], "no_image_placeholders": 0,
               "all_images_visually_inspected": False, "local_audit_complete": False,
               "primary_image_preprocessing_complete": False, "promotion_permitted": False,
               "scientific_readiness": False, "normal_validator_remaining_errors": errors,
               "readback_sha256": run.sha(OUTPUT / "readback.json"),
               "resources_sha256": run.sha(OUTPUT / "resources.json"),
               "checker_sha256": run.sha(Path(__file__)),
               "combined_wall_seconds_through_visual": time.time() - run.authority()["started_unix_seconds"],
               "opened_sheet_sha256": {name: run.sha(run.OUTPUT / name) for name in opened}}
    run.write(OUTPUT / "visual_review.json", receipt)
    run.write(run.ROOT / "results/phase1/siwmv2-blocked-visual291-v1.json",
              {**{k: v for k, v in receipt.items() if k != "opened_sheet_sha256"},
               "private_visual_review_sha256": run.sha(OUTPUT / "visual_review.json")})
    print(json.dumps({k: v for k, v in receipt.items() if k != "opened_sheet_sha256"}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    for mode in ("prepare", "run-once", "scan", "readback", "record-visual"):
        modes.add_argument("--" + mode, action="store_true")
    parser.add_argument("--opened", action="append", default=[])
    parser.add_argument("--observations")
    parser.add_argument("--crop-usability-pass", action="store_true")
    args = parser.parse_args()
    run.shared.retained.arm_deadline(run.authority()[
        "deadline_unix_seconds" if args.record_visual else "work_deadline_unix_seconds"])
    if args.prepare:
        prepare()
        return 0
    plan = run.read(OUTPUT / "plan.json")
    if args.record_visual:
        visual(plan, args.opened, args.observations, args.crop_usability_pass)
        return 0
    if args.scan or args.readback:
        lease = run.read(OUTPUT / "lease.json")
        if lease["parent_pid"] != os.getppid() or lease["plan_sha256"] != run.sha(OUTPUT / "plan.json") or os.getsid(0) != os.getpid():
            raise ValueError("leased readback child required; never an unsupervised media worker")
        if args.scan:
            run.budget.scan_forever(ROOTS, IPC, lease, run.shared.retained.tree_bytes)
        else:
            readback(plan, run.budget.Client(IPC, lease, usage, run.enforce))
        return 0
    run.write(OUTPUT / "supervisor.json", {"pid": os.getpid(), "source_sha256": run.sha(Path(__file__))})
    with (OUTPUT / "execution.log").open("xb", buffering=0) as log:
        os.dup2(log.fileno(), 1)
        os.dup2(log.fileno(), 2)
    sys.stdout.reconfigure(line_buffering=True)
    return 0 if supervise(plan) else 1


if __name__ == "__main__":
    raise SystemExit(main())
