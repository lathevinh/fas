"""Complete actual CASIA visual/local checks; never decode or infer again."""

import argparse
from collections import Counter
import csv
import json
import os
from pathlib import Path
import time

import recover_casia287 as recovery
from fas.preregistration import validate_stage

prior, OUTPUT = recovery.prior, recovery.OUTPUT
DATA_PROVENANCE = "bounded Bob-reference release/subject/integrity/decoded-exact audit287; transformed/joined ancestry not certified"
PUBLIC_LOCAL = prior.ROOT / "results/phase1/casia-local-audit287-v1.json"


def partial_ledger(videos, transactions, attempts):
    if len(videos) != 600 or not set(transactions) <= set(attempts) or not set(attempts) <= set(range(600)):
        raise ValueError("exact600 denominator and committed/started index accounting required")
    rows = []
    for index, original in enumerate(videos):
        for record in (transactions.get(index), attempts.get(index)):
            if record is not None and (record["index"] != index or record["video_id"] != original["video_id"]
                                       or record["role"] != original["role"]):
                raise ValueError("partial receipt original/index/role drift")
        status = ("committed_provisional" if index in transactions else
                  "interrupted_before_commit" if index in attempts else "not_attempted_after_deadline")
        rows.append({
            **{key: original[key] for key in ("video_id", "role", "binary_label", "subject_id", "official_split")},
            "index": index, "execution_status": status, "package_accepted": False,
            "retain_original_denominator": True, "final_k1_action": "non_accept", "model_score": None})
    return rows


def report_partial():
    terminal = prior.read(OUTPUT / "resources.json")
    if terminal["failure"] is None or terminal["accounting_complete"] or terminal["image_export_software_complete"]:
        raise ValueError("partial report requires an explicitly failed, unaccepted terminal package")
    plan = prior.read(OUTPUT / "plan.json")
    transactions = {int(path.stem): prior.read(path) for path in (OUTPUT / "transactions").glob("*.json")}
    attempts = {int(path.stem): prior.read(path) for path in (OUTPUT / "attempts").glob("*.json")}
    rows = partial_ledger(plan["videos"], transactions, attempts)
    execution = dict(Counter(row["execution_status"] for row in rows))
    outcomes = dict(Counter(row["detector_status"] for row in transactions.values()))
    media = [prior.read(OUTPUT / "media" / f"{index:04d}.json") for index in sorted(transactions)]
    private = {
        "checkpoint": 287, "rows": rows, "execution_counts": execution,
        "accounting_complete": False, "primary_image_preprocessing_complete": False,
        "resources_sha256": prior.sha(OUTPUT / "resources.json"),
        "original_failure_rows_sha256": prior.sha(OUTPUT / "failure_rows.json"),
        "clarification": "A started original without a transaction is interrupted, not never attempted.",
        "administrative_metadata_inventory_only": True, "fresh_media_or_pixel_readback": False}
    prior.write(OUTPUT / "partial_accounting.json", private)
    public = {
        "checkpoint": 287, "dataset": "CASIA-FASD", "originals": 600, "execution_counts": execution,
        "producer_reported_committed_outcomes": outcomes,
        "producer_reported_committed_selected": sum(row["selected_frame"] is not None for row in transactions.values()),
        "producer_reported_committed_native_frames": sum(row["frame_count"] for row in media),
        "producer_reported_timestamp_transports": dict(Counter(row["timestamp_transport"] for row in media)),
        "producer_reported_explicit_non_coded_vops": sum(
            (row.get("native_count_accounting") or {}).get("explicit_non_coded_vops", 0) for row in media),
        "committed_image_asset_references": sum(
            len(row["assets"]) + int(row.get("selected_RGB_asset") is not None) for row in transactions.values()),
        "owned_image_files_present": sum(len(list((OUTPUT / folder).glob("*.png"))) for folder in ("frames", "crops")),
        "committed_role_counts": dict(Counter(row["role"] for row in transactions.values())),
        "full600_readback_completed": (OUTPUT / "readback.json").exists(),
        "actual_bounded_crop_review_completed": (OUTPUT / "visual_review.json").exists(),
        "accounting_complete": False, "image_export_software_complete": False,
        "primary_image_preprocessing_complete": False, "local_audit_complete": False,
        "audit_summary_statuses_changed": False, "scientific_readiness": False,
        "failure": terminal["failure"], "package_wall_seconds": terminal["package_wall_seconds"],
        "wall_cap_compliance_claimed": False, "sampled_peaks": terminal["sampled_peaks"],
        "automatic_retry": False, "async_storage_approval_executed": False,
        "administrative_metadata_inventory_only": True, "fresh_media_or_pixel_readback": False,
        "private_partial_accounting_sha256": prior.sha(OUTPUT / "partial_accounting.json"),
        "resources_sha256": prior.sha(OUTPUT / "resources.json"),
        "checker_sha256": prior.sha(Path(__file__))}
    prior.write(prior.ROOT / "results/phase1/casia-preprocessing287-partial-v1.json", public)
    print(json.dumps(public, indent=2))


def csv_rows(path):
    return list(csv.DictReader(path.read_text().splitlines()))


def reconcile_frozen(videos, canonical_rows, roles):
    groups = prior.group_checks(videos, roles)
    canonical = {row["video_id"]: row for row in canonical_rows}
    assigned = {row["video_id"]: row["role"] for row in roles}
    if len(canonical_rows) != 600 or len(canonical) != 600 or set(canonical) != set(assigned):
        raise ValueError("exact600 frozen canonical/assigned-role parents required")
    for row in videos:
        if row != {**canonical[row["video_id"]], "role": assigned[row["video_id"]]}:
            raise ValueError("only canonical null-role to frozen assigned-role projection permitted")
    return groups


def baseline_errors(datasets):
    return {f"{name}_summary.csv has unaudited dataset: {dataset}"
            for name in ("dataset", "split") for dataset in datasets}


def checks():
    public = prior.read(recovery.SUMMARY)
    for name, digest in public["private_record_sha256"].items():
        if prior.sha(OUTPUT / name) != digest:
            raise ValueError("software terminal commitment drift")
    resources = prior.read(OUTPUT / "resources.json")
    if resources["accounting_complete"] is not True or resources["image_export_software_complete"] is not True or resources["failure"] is not None:
        raise ValueError("full accounting and nonzero accepted image exports required")
    if resources["package_wall_seconds"] >= recovery.diagnostic.CAPS["wall_seconds"]:
        raise ValueError("software terminal exceeded combined clock")
    recovery.diagnostic.enforce(resources["sampled_peaks"])
    recovery.diagnostic.enforce(recovery.probe.measured(os.getpgrp()))
    plan = prior.read(OUTPUT / "plan.json")
    prior.shared.check_bindings(plan["sources"])
    prior.guard(plan)
    canonical = prior.read(prior.FROZEN / "casia_fasd_canonical.json")
    roles = csv_rows(prior.FROZEN / "casia_fasd_roles.csv")
    groups = reconcile_frozen(plan["videos"], canonical["videos"], roles)
    readback = prior.read(OUTPUT / "readback.json")
    manifest = prior.shared.read_verified_json(OUTPUT / "full_manifest.json", readback["full_manifest_sha256"])
    counts = prior.validate_manifest(plan, manifest["rows"])
    if any(resources[key] != value or readback[key] != value for key, value in counts.items()):
        raise ValueError("terminal counts/full600 manifest drift")
    probe_readback = prior.read(OUTPUT / "probe_readback.json")
    if probe_readback["full_readback_sha256"] != prior.sha(OUTPUT / "readback.json"):
        raise ValueError("native probe/full readback commitment drift")
    for relative, digest in {**readback["per_unit_sha256"], **readback["asset_sha256"],
                             **probe_readback["per_probe_sha256"]}.items():
        if prior.sha(OUTPUT / relative) != digest:
            raise ValueError("full unit/image/raw diagnostic commitment drift")
    if list((OUTPUT / "temporary").iterdir()):
        raise ValueError("owned staged originals remain")
    media = [prior.read(OUTPUT / "media" / f"{index:04d}.json") for index in range(600)]
    release = prior.read(OUTPUT / "release_integrity.json")
    if len(release["video_payload_pins"]) != 600 or release["independent_unpacked_crc32_verified"] is not True:
        raise ValueError("all600 native CRC/size/SHA joins required")
    for row in media:
        pin = release["video_payload_pins"][row["media_relpath"]]
        if row["archive_crc_validated"] is not True or row["media_sha256"] != pin["sha256"] or row["byte_size"] != pin["byte_size"]:
            raise ValueError("per-original source integrity drift")
    findings = prior.shared.exact_checks(media, {row["video_id"]: row for row in plan["videos"]})
    if findings != prior.read(OUTPUT / "content_checks.json")["exact_groups"]:
        raise ValueError("native exact/boundary accounting drift")
    return resources, readback, manifest["rows"], groups, media, release, counts


def record_visual(opened, observations, crop_pass):
    resources, readback, rows, _, _, _, _ = checks()
    expected = {sheet["path"] for sheet in readback["visual_sheets"]}
    if not observations or set(opened) != expected or len(opened) != len(expected):
        raise ValueError("explicit actually opened complete sheet set and observations required")
    lookup = {row["index"]: row for row in rows}
    inspected = Counter()
    for sheet in readback["visual_sheets"]:
        if prior.sha(OUTPUT / sheet["path"]) != sheet["sha256"]:
            raise ValueError("actual opened sheet content drift")
        for index in sheet["indices"]:
            row = lookup[index]
            inspected["tiles"] += 1
            inspected["no_image_placeholders" if row["selected_frame"] is None else
                      "face_crops" if row["detector_status"] == "success" else "selected_failure_images"] += 1
    if crop_pass and inspected["face_crops"] <= 0:
        raise ValueError("no crop usability acceptance from placeholders")
    receipt = {
        "checkpoint": 287, "dataset": "CASIA-FASD", "visual_inspection_completed": True,
        "sample_crop_usability_check_pass": crop_pass, "observations": observations,
        "opened_sheet_paths": opened, "opened_sheet_sha256": {name: prior.sha(OUTPUT / name) for name in opened},
        "opened_tiles": inspected["tiles"], "inspected_face_crops": inspected["face_crops"],
        "selected_failure_images": inspected["selected_failure_images"], "no_image_placeholders": inspected["no_image_placeholders"],
        "all_images_visually_inspected": False, "accounting_complete": resources["accounting_complete"],
        "primary_image_preprocessing_complete": crop_pass, "recorded_unix_seconds": time.time(),
        "resources_sha256": prior.sha(OUTPUT / "resources.json"), "readback_sha256": prior.sha(OUTPUT / "readback.json"),
        "checker_sha256": prior.sha(Path(__file__))}
    prior.write(OUTPUT / "visual_review.json", receipt)
    prior.write(prior.ROOT / "results/phase1/casia-preprocessing287-visual-review-v1.json", {
        **{key: value for key, value in receipt.items() if key not in {"opened_sheet_paths", "opened_sheet_sha256"}},
        "private_visual_review_sha256": prior.sha(OUTPUT / "visual_review.json")})


def prepare_local(prior_checker):
    resources, readback, rows, groups, media, release, counts = checks()
    visual = prior.read(OUTPUT / "visual_review.json")
    if visual["visual_inspection_completed"] is not True or visual["sample_crop_usability_check_pass"] is not True:
        raise ValueError("actual nonzero bounded face-crop usability review must pass")
    errors = validate_stage(prior.ROOT, "data-audit", frozen_root=prior.FROZEN)
    if set(errors) != baseline_errors(("CASIA-FASD", "SiW-Mv2")) or len(errors) != 4:
        raise ValueError("unexpected normal frozen-root validator baseline: " + repr(errors))
    previous_checker_sha = prior.read(prior.ROOT / "results/phase1/casia-local-audit285-v1.json")["checker_sha256"]
    if prior_checker.name != "record_casia285_visual_review.py" or prior.sha(prior_checker) != previous_checker_sha:
        raise ValueError("actual historical285 checker source identity required")
    summaries = {name: csv_rows(prior.ROOT / "manifests" / name) for name in ("dataset_summary.csv", "split_summary.csv")}
    certificate = {
        "checkpoint": 287, "dataset": "CASIA-FASD", "accounting_complete": True,
        "primary_image_preprocessing_complete": True, "local_audit_complete": False,
        "status": "checks_passed_pending_summary_promotion", **counts, "groups": groups,
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
        "prior285_checker_source": {"basename": prior_checker.name, "sha256": previous_checker_sha,
                                   "public_source_available": False, "used_as_recovery_acceptance_gate": False},
        "checker_sha256": prior.sha(Path(__file__)), "scientific_readiness": False,
        "model_scores": 0, "fitted_scores": 0, "target_access": False,
        "joined_domain_assurance": False, "near_duplicate_independence_certified": False}
    prior.write(OUTPUT / "local_checks.json", certificate)


def finalize_local():
    checks()
    certificate = prior.read(OUTPUT / "local_checks.json")
    if certificate["checker_sha256"] != prior.sha(Path(__file__)):
        raise ValueError("local completion checker drift")
    for name, before in certificate["summary_before_rows"].items():
        after = csv_rows(prior.ROOT / "manifests" / name)
        expected = [{**row, **({"audit_status": "complete", **({"metadata_source": DATA_PROVENANCE} if name == "dataset_summary.csv" else {})}
                              if row["dataset"] == "CASIA-FASD" else {})} for row in before]
        if after != expected:
            raise ValueError("only CASIA audit_status/provenance promotion permitted")
    errors = validate_stage(prior.ROOT, "data-audit", frozen_root=prior.FROZEN)
    if set(errors) != baseline_errors(("SiW-Mv2",)) or len(errors) != 2:
        raise ValueError("normal validator must retain exactly the two SiW audit-status errors")
    public = {key: value for key, value in certificate.items() if key != "summary_before_rows"}
    public.update(status="local_release_subject_integrity_and_primary_image_complete", local_audit_complete=True,
                  audit_summary_statuses_changed=True, normal_validator_remaining_errors=errors,
                  summary_after_sha256={name: prior.sha(prior.ROOT / "manifests" / name) for name in certificate["summary_before_rows"]},
                  local_checks_sha256=prior.sha(OUTPUT / "local_checks.json"),
                  combined_wall_seconds_through_local_completion=time.time() - recovery.diagnostic.authority()["started_unix_seconds"])
    prior.write(OUTPUT / "local_audit.json", public)
    prior.write(PUBLIC_LOCAL, {**public, "private_local_audit_sha256": prior.sha(OUTPUT / "local_audit.json")})
    print(json.dumps({key: public[key] for key in ("originals", "selected", "detector_success", "pre_detector_failure",
                                                 "local_audit_complete", "primary_image_preprocessing_complete")}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    for mode in ("report-partial", "record-visual", "prepare-local", "finalize-local"):
        modes.add_argument("--" + mode, action="store_true")
    parser.add_argument("--opened", action="append", default=[])
    parser.add_argument("--observations")
    parser.add_argument("--crop-usability-pass", action="store_true")
    parser.add_argument("--prior-checker-source", type=Path)
    args = parser.parse_args()
    if args.report_partial:
        report_partial()
    elif args.record_visual:
        record_visual(args.opened, args.observations, args.crop_usability_pass)
    elif args.prepare_local:
        if args.prior_checker_source is None:
            parser.error("--prior-checker-source is required")
        prepare_local(args.prior_checker_source)
    else:
        finalize_local()


if __name__ == "__main__":
    main()
