"""Actual visual/local closure of the retained447 plus153 CASIA package."""

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import time

import resume_casia289 as recovery
from complete_casia287 import baseline_errors, csv_rows, reconcile_frozen
from fas.preregistration import validate_stage

prior, OUTPUT = recovery.prior, recovery.OUTPUT
DATA_PROVENANCE = "bounded Bob-reference release/subject/integrity/decoded-exact audit289; transformed/joined ancestry not certified"
PUBLIC_LOCAL = prior.ROOT / "results/phase1/casia-local-audit289-v1.json"


def checks():
    public = prior.read(recovery.SUMMARY)
    for name, digest in public["private_record_sha256"].items():
        if prior.sha(OUTPUT / name) != digest:
            raise ValueError("terminal resource/source receipt drift")
    resources = prior.read(OUTPUT / "resources.json")
    if (resources["accounting_complete"] is not True or resources["image_export_software_complete"] is not True
            or resources["failure"] is not None or resources["package_wall_seconds"] >= recovery.CAPS["wall_seconds"]):
        raise ValueError("successful full600 software/resource terminal required")
    recovery.enforce(resources["sampled_peaks"], work=False)
    actual = prior.shared.usage(os.getpgrp(), OUTPUT / ".unused")
    actual["output_bytes"] = sum(prior.shared.retained.tree_bytes(root) for root in recovery.ROOTS) + actual["temporary_bytes"]
    recovery.enforce(actual, work=False)
    plan = prior.read(OUTPUT / "plan.json")
    prior.shared.check_bindings(plan["sources"])
    prior.guard(plan)
    canonical = prior.read(prior.FROZEN / "casia_fasd_canonical.json")
    groups = reconcile_frozen(plan["videos"], canonical["videos"], csv_rows(prior.FROZEN / "casia_fasd_roles.csv"))
    readback = prior.read(OUTPUT / "readback.json")
    manifest = prior.shared.read_verified_json(OUTPUT / "full_manifest.json", readback["full_manifest_sha256"])
    counts = prior.validate_manifest(plan, manifest["rows"])
    if any(resources[key] != value or readback[key] != value for key, value in counts.items()):
        raise ValueError("full600 row/terminal count drift")
    probes = prior.read(OUTPUT / "probe_readback.json")
    if probes["full_readback_sha256"] != prior.sha(OUTPUT / "readback.json"):
        raise ValueError("strict probe/full image readback drift")
    for relative, digest in {**readback["per_unit_sha256"], **readback["asset_sha256"],
                             **probes["per_probe_sha256"]}.items():
        if prior.sha(OUTPUT / relative) != digest:
            raise ValueError("full image/unit/native evidence commitment drift")
    retained = prior.read(OUTPUT / "retained_readback.json")
    if retained["originals"] != 447 or retained["retained_decode_calls"] or retained["retained_detector_calls"]:
        raise ValueError("exact447 retained originals without decode/inference required")
    for relative, digest in retained["source_record_and_asset_sha256"].items():
        if prior.sha(recovery.SOURCE / relative) != digest or prior.sha(OUTPUT / relative) != digest:
            raise ValueError("retained original/copy was modified")
    staging = prior.read(OUTPUT / "selective_staging.json")
    release = prior.read(OUTPUT / "release_integrity.json")
    expected = {plan["videos"][index]["media_relpath"] for index in plan["remaining_indices"]}
    if staging["new_extracted_videos"] != 153 or set(staging["source_pins"]) != expected or staging["full600_extraction_repeated"]:
        raise ValueError("exact153 selective staging required")
    if (staging["extractor_returncode"] or staging["extractor_stderr_bytes"]
            or prior.sha(OUTPUT / "selective-extraction.stderr") != staging["extractor_stderr_sha256"]):
        raise ValueError("selective extraction exit/stderr drift")
    if len(release["video_payload_pins"]) != 600 or release["independent_unpacked_crc32_verified"] is not True:
        raise ValueError("exact600 historical/current native CRC commitments required")
    if any(pin != release["video_payload_pins"][name] for name, pin in staging["source_pins"].items()):
        raise ValueError("remaining153 native CRC/size/SHA commitment drift")
    if list((OUTPUT / "temporary").iterdir()):
        raise ValueError("owned staged originals remain")
    media = [prior.read(OUTPUT / "media" / f"{index:04d}.json") for index in range(600)]
    for row in media:
        pin = release["video_payload_pins"][row["media_relpath"]]
        if (row["archive_crc_validated"] is not True or row["media_sha256"] != pin["sha256"]
                or row["byte_size"] != pin["byte_size"]):
            raise ValueError("per-original source integrity join drift")
    findings = prior.shared.exact_checks(media, {row["video_id"]: row for row in plan["videos"]})
    if findings != prior.read(OUTPUT / "content_checks.json")["exact_groups"]:
        raise ValueError("exact native sequence/boundary findings drift")
    return resources, readback, manifest["rows"], groups, media, release, counts


def record_visual(opened, observations, crop_pass):
    resources, readback, rows, _, _, _, _ = checks()
    expected = {sheet["path"] for sheet in readback["visual_sheets"]}
    if not observations or set(opened) != expected or len(opened) != len(expected):
        raise ValueError("all actual fixed/failure sheets must be opened and described")
    lookup, inspected = {row["index"]: row for row in rows}, Counter()
    for sheet in readback["visual_sheets"]:
        if prior.sha(OUTPUT / sheet["path"]) != sheet["sha256"]:
            raise ValueError("actually opened sheet drift")
        for index in sheet["indices"]:
            row = lookup[index]
            inspected["tiles"] += 1
            inspected["no_image_placeholders" if row["selected_frame"] is None else
                      "face_crops" if row["detector_status"] == "success" else "selected_failure_images"] += 1
    if crop_pass and inspected["face_crops"] <= 0:
        raise ValueError("no crop acceptance without actual nonzero face crops")
    receipt = {
        "checkpoint": 289, "dataset": "CASIA-FASD", "visual_inspection_completed": True,
        "sample_crop_usability_check_pass": crop_pass, "observations": observations,
        "opened_sheet_paths": opened, "opened_sheet_sha256": {name: prior.sha(OUTPUT / name) for name in opened},
        "opened_tiles": inspected["tiles"], "inspected_face_crops": inspected["face_crops"],
        "selected_failure_images": inspected["selected_failure_images"], "no_image_placeholders": inspected["no_image_placeholders"],
        "all_images_visually_inspected": False, "primary_image_preprocessing_complete": crop_pass,
        "accounting_complete": resources["accounting_complete"], "recorded_unix_seconds": time.time(),
        "resources_sha256": prior.sha(OUTPUT / "resources.json"), "readback_sha256": prior.sha(OUTPUT / "readback.json"),
        "checker_sha256": prior.sha(Path(__file__))}
    prior.write(OUTPUT / "visual_review.json", receipt)
    prior.write(prior.ROOT / "results/phase1/casia-preprocessing289-visual-review-v1.json", {
        **{key: value for key, value in receipt.items() if key not in {"opened_sheet_paths", "opened_sheet_sha256"}},
        "private_visual_review_sha256": prior.sha(OUTPUT / "visual_review.json")})


def prepare_local(prior_checker):
    resources, readback, rows, groups, media, release, counts = checks()
    visual = prior.read(OUTPUT / "visual_review.json")
    if visual["visual_inspection_completed"] is not True or visual["sample_crop_usability_check_pass"] is not True:
        raise ValueError("actual bounded crop usability review must pass")
    errors = validate_stage(prior.ROOT, "data-audit", frozen_root=prior.FROZEN)
    if set(errors) != baseline_errors(("CASIA-FASD", "SiW-Mv2")) or len(errors) != 4:
        raise ValueError("unexpected normal external-frozen-root validator baseline: " + repr(errors))
    old_checker_sha = prior.read(prior.ROOT / "results/phase1/casia-local-audit285-v1.json")["checker_sha256"]
    if prior_checker.name != "record_casia285_visual_review.py" or prior.sha(prior_checker) != old_checker_sha:
        raise ValueError("actual historical285 checker source identity required")
    summaries = {name: csv_rows(prior.ROOT / "manifests" / name) for name in ("dataset_summary.csv", "split_summary.csv")}
    certificate = {
        "checkpoint": 289, "dataset": "CASIA-FASD", **counts, "groups": groups,
        "accounting_complete": True, "primary_image_preprocessing_complete": True, "local_audit_complete": False,
        "status": "checks_passed_pending_summary_promotion", "retained_without_decode_or_inference": 447,
        "new_attempts": 153, "new_extracted_videos": 153, "full600_extraction_repeated": False,
        "role_originals": dict(Counter(row["role"] for row in rows)),
        "role_selected": dict(Counter(row["role"] for row in rows if row["selected_frame"] is not None)),
        "pre_detector_failure_reasons": dict(Counter(row["failure_reason"] for row in media if row["decode_status"] != "decoded")),
        "native_frames": readback["native_frames"], "strict_replay_count": readback["strict_replay_count"],
        "image_assets": len(readback["asset_sha256"]), "video_crc_checked": 600,
        "video_payload_bytes": release["video_payload_bytes"], "archive_rehashed": False,
        "timestamp_transports": prior.read(OUTPUT / "probe_readback.json")["timestamp_transports"],
        "explicit_non_coded_vops": sum((row.get("native_count_accounting") or {}).get("explicit_non_coded_vops", 0) for row in media),
        "exact_duplicate_groups": readback["exact_duplicate_groups"], "forbidden_exact_crossings": 0,
        "normal_validator_baseline_errors": errors, "summary_before_rows": summaries,
        "summary_before_sha256": {name: prior.sha(prior.ROOT / "manifests" / name) for name in summaries},
        "resources_sha256": prior.sha(OUTPUT / "resources.json"), "readback_sha256": prior.sha(OUTPUT / "readback.json"),
        "probe_readback_sha256": prior.sha(OUTPUT / "probe_readback.json"),
        "visual_review_sha256": prior.sha(OUTPUT / "visual_review.json"),
        "retained_readback_sha256": prior.sha(OUTPUT / "retained_readback.json"),
        "selective_staging_sha256": prior.sha(OUTPUT / "selective_staging.json"),
        "prior285_checker_source": {"basename": prior_checker.name, "sha256": old_checker_sha,
                                   "public_source_available": False, "used_as_recovery_acceptance_gate": False},
        "checker_sha256": prior.sha(Path(__file__)), "scientific_readiness": False,
        "model_scores": 0, "fitted_scores": 0, "target_access": False,
        "joined_domain_assurance": False, "near_duplicate_independence_certified": False}
    prior.write(OUTPUT / "local_checks.json", certificate)


def finalize_local():
    checks()
    certificate = prior.read(OUTPUT / "local_checks.json")
    if certificate["checker_sha256"] != prior.sha(Path(__file__)):
        raise ValueError("local checker source drift")
    for name, before in certificate["summary_before_rows"].items():
        after = csv_rows(prior.ROOT / "manifests" / name)
        expected = [{**row, **({"audit_status": "complete", **({"metadata_source": DATA_PROVENANCE}
                     if name == "dataset_summary.csv" else {})} if row["dataset"] == "CASIA-FASD" else {})}
                    for row in before]
        if after != expected:
            raise ValueError("only CASIA audit status/provenance promotion is permitted")
    errors = validate_stage(prior.ROOT, "data-audit", frozen_root=prior.FROZEN)
    if set(errors) != baseline_errors(("SiW-Mv2",)) or len(errors) != 2:
        raise ValueError("normal validator must retain exactly the two SiW audit-status errors")
    public = {key: value for key, value in certificate.items() if key != "summary_before_rows"}
    public.update(
        status="local_release_subject_integrity_and_primary_image_complete", local_audit_complete=True,
        audit_summary_statuses_changed=True, normal_validator_remaining_errors=errors,
        summary_after_sha256={name: prior.sha(prior.ROOT / "manifests" / name) for name in certificate["summary_before_rows"]},
        local_checks_sha256=prior.sha(OUTPUT / "local_checks.json"),
        combined_wall_seconds_through_local_completion=time.time() - recovery.authority()["started_unix_seconds"])
    prior.write(OUTPUT / "local_audit.json", public)
    prior.write(PUBLIC_LOCAL, {**public, "private_local_audit_sha256": prior.sha(OUTPUT / "local_audit.json")})
    print(json.dumps({key: public[key] for key in ("originals", "selected", "detector_success",
                                                 "pre_detector_failure", "local_audit_complete")}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    for mode in ("record-visual", "prepare-local", "finalize-local"):
        modes.add_argument("--" + mode, action="store_true")
    parser.add_argument("--opened", action="append", default=[])
    parser.add_argument("--observations")
    parser.add_argument("--crop-usability-pass", action="store_true")
    parser.add_argument("--prior-checker-source", type=Path)
    args = parser.parse_args()
    prior.shared.retained.arm_deadline(recovery.authority()["deadline_unix_seconds"])
    if args.record_visual:
        record_visual(args.opened, args.observations, args.crop_usability_pass)
    elif args.prepare_local:
        if args.prior_checker_source is None:
            parser.error("--prior-checker-source is required")
        prepare_local(args.prior_checker_source)
    else:
        finalize_local()


if __name__ == "__main__":
    raise SystemExit(main())
