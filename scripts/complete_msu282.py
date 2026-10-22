"""Reconcile existing terminal MSU evidence; never decode media or change summaries."""

from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import recover_msu282 as recovery
from fas.lineage import decoded_tokens
from fas.preregistration import validate_stage

job = recovery.job
OUTPUT = recovery.OUTPUT


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_rows(path):
    return list(csv.DictReader(path.read_text().splitlines()))


def reconcile_frozen(videos, canonical_rows, roles):
    groups = job.group_checks(videos, roles)
    canonical = {row["video_id"]: row for row in canonical_rows}
    assigned = {row["video_id"]: row["role"] for row in roles}
    if len(canonical_rows) != 280 or len(canonical) != 280 or set(canonical) != set(assigned):
        raise ValueError("exact280 frozen canonical/role parents required")
    for row in videos:
        expected = {**canonical[row["video_id"]], "role": assigned[row["video_id"]]}
        if row != expected:
            raise ValueError("canonical planned original or frozen assigned-role drift")
    return groups


def main():
    started = time.monotonic()
    report = job.read_json(recovery.SUMMARY)
    for name, expected in report["private_record_sha256"].items():
        if sha(OUTPUT / name) != expected:
            raise ValueError("terminal commitment drift: " + name)
    visual = job.read_json(ROOT / "results/phase1/msu-preprocessing282-visual-review-v1.json")
    if visual["visual_inspection_completed"] is not True or visual["sample_crop_usability_check_pass"] is not True:
        raise ValueError("actual bounded visual inspection must pass first")
    if sha(OUTPUT / "visual_review.json") != visual["private_visual_review_sha256"]:
        raise ValueError("visual receipt commitment drift")
    resources = job.read_json(OUTPUT / "resources.json")
    if resources["completion_claimed"] is not True or resources["failure"] is not None:
        raise ValueError("successful software terminal required")
    if resources["package_wall_seconds"] >= job.CAPS["wall_seconds"] or resources["sampled_peaks"]["rss_bytes"] > job.CAPS["rss_bytes"] or resources["sampled_peaks"]["output_bytes"] > job.CAPS["output_bytes"]:
        raise ValueError("terminal cap violation")
    plan = job.read_json(OUTPUT / "plan.json")
    job.check_bindings(plan["sources"])
    job.archive_guard(plan)
    registry = job.read_json(ROOT / "configs/role_policy_frozen_v2.yaml")
    for name in ("msu_mfsd_canonical.json", "msu_mfsd_metadata.csv", "msu_mfsd_roles.csv"):
        if sha(job.FROZEN / name) != registry["frozen_artifact_sha256"][name]:
            raise ValueError("frozen native/metadata/role parent drift")
    canonical = job.read_json(job.FROZEN / "msu_mfsd_canonical.json")
    roles = csv_rows(job.FROZEN / "msu_mfsd_roles.csv")
    groups = reconcile_frozen(plan["videos"], canonical["videos"], roles)
    manifest = job.read_json(OUTPUT / "full_manifest.json")
    counts = job.validate_manifest(plan, manifest["rows"])
    readback = job.read_json(OUTPUT / "readback.json")
    completion = job.read_json(OUTPUT / "worker_completion.json")
    release = job.read_json(OUTPUT / "release_integrity.json")
    stage = job.read_json(OUTPUT / "stage.json")
    replay = job.read_json(OUTPUT / "replay_readback.json")
    if any(readback[key] != value for key, value in counts.items()) or sha(OUTPUT / "full_manifest.json") != readback["full_manifest_sha256"]:
        raise ValueError("full280 final manifest/readback drift")
    for relative, expected in {**readback["per_unit_sha256"], **readback["asset_sha256"], **replay["record_sha256"]}.items():
        if sha(OUTPUT / relative) != expected:
            raise ValueError("terminal record/asset/replay drift")
    if sha(OUTPUT / "readback.json") != replay["full_readback_sha256"]:
        raise ValueError("replay/full-readback commitment drift")
    media_rows, failed = [], []
    for index, original in enumerate(plan["videos"]):
        row = job.read_json(OUTPUT / "media" / f"{index:04d}.json")
        if any(row[key] != original[key] for key in ("video_id", "role", "subject_id", "binary_label", "official_split", "media_relpath", "byte_size")):
            raise ValueError("media/canonical role/label/partition/size drift")
        if row["inner_crc_checked_to_eof"] is not True:
            raise ValueError("missing full video CRC read")
        if row["decode_status"] == "decoded":
            decoded_tokens(row)
        else:
            failed.append({"index": index, "role": row["role"], "failure_reason": row["failure_reason"]})
        media_rows.append(row)
    exact = job.exact_checks(media_rows, {row["video_id"]: row for row in plan["videos"]})
    content = job.read_json(OUTPUT / "content_checks.json")
    if exact != content["exact_groups"] or content["forbidden_exact_crossings"] != 0:
        raise ValueError("exact content/boundary drift")
    if len(media_rows) != 280 or completion["transactions"] != 280 or completion["media_crc_checked"] != 280 or completion["reused_after_pixel_readback"] != 4 or completion["new_attempts"] != 276:
        raise ValueError("original/reused/new attempt reconciliation failure")
    if sum(row["frame_count"] for row in media_rows) != readback["native_frames"] or len(failed) != counts["pre_detector_failure"]:
        raise ValueError("full media/decode/failure accounting drift")
    if release["archive_bytes"] != 11095264656 or release["joined_zip_bytes"] != 11092803150 or stage["joined_zip_bytes"] != release["joined_zip_bytes"]:
        raise ValueError("original/staged archive byte accounting drift")
    if stage["volumes"] != release["volumes"] or len(stage["volumes"]) != 16 or any(row["outer_crc_checked_to_eof"] is not True for row in stage["volumes"]):
        raise ValueError("all16 volume CRC/SHA accounting required")
    if set(release["archive_pins"]) != set(plan["archive_identities"]):
        raise ValueError("exact original archive pin set required")
    if list((OUTPUT / "temporary").iterdir()):
        raise ValueError("temporary ZIP/media remain")
    baseline_errors = validate_stage(ROOT, "data-audit", frozen_root=job.FROZEN)
    expected_errors = {f"{name}_summary.csv has unaudited dataset: {dataset}"
                       for name in ("dataset", "split") for dataset in ("CASIA-FASD", "MSU-MFSD", "SiW-Mv2")}
    if set(baseline_errors) != expected_errors or len(baseline_errors) != 6:
        raise ValueError("normal frozen-root validator has unexpected baseline defects: " + repr(baseline_errors))
    public = {
        "checkpoint": 282, "recovery": True, "dataset": "MSU-MFSD",
        "status": "local_release_subject_integrity_exact_and_primary_preprocessing_complete",
        "local_audit_complete": True, **counts, "groups": groups,
        "original_archive_count": 8, "original_archive_bytes": release["archive_bytes"],
        "crc_checked_volumes": 16, "video_crc_checked": 280,
        "ancillary_crc_checked": len(completion["ancillary_entries"]),
        "native_frames": readback["native_frames"], "selected_payload_bytes": readback["selected_payload_bytes"],
        "reused_after_pixel_readback": 4, "new_attempts": 276,
        "role_originals": dict(Counter(row["role"] for row in manifest["rows"])),
        "role_selected": dict(Counter(row["role"] for row in manifest["rows"] if row["selected_frame"] is not None)),
        "pre_detector_failure_reasons": dict(Counter(row["failure_reason"] for row in failed)),
        "pre_detector_failure_roles": dict(Counter(row["role"] for row in failed)),
        "exact_duplicate_groups": len(exact), "forbidden_exact_crossings": 0,
        "known_native_parent_group_crossings": 0,
        "known_parent_scope": "native documented subject-scoped print/replay construction; no independent-capture certification",
        "near_duplicate_transformed_independence_certified": False,
        "joined_domain_assurance": False, "all_images_visually_inspected": False,
        "scientific_readiness": False, "model_scores": 0, "fitted_scores": 0, "target_access": False,
        "summary_changes": {"dataset_summary.csv": {"MSU-MFSD": {"audit_status": ["not_audited", "complete"]}},
                            "split_summary.csv": {"MSU-MFSD": {"audit_status": ["not_audited", "complete"]}}},
        "normal_validator_baseline_errors": baseline_errors,
        "expected_remaining_unaudited": ["CASIA-FASD", "SiW-Mv2"],
        "resources_sha256": sha(OUTPUT / "resources.json"), "readback_sha256": sha(OUTPUT / "readback.json"),
        "full_manifest_sha256": sha(OUTPUT / "full_manifest.json"),
        "visual_review_sha256": sha(OUTPUT / "visual_review.json"),
        "summary_before_sha256": {name: sha(ROOT / "manifests" / name) for name in ("dataset_summary.csv", "split_summary.csv")},
        "checker_sha256": sha(Path(__file__)), "check_wall_seconds": time.monotonic() - started}
    private = {**public, "private_exact_groups": exact, "private_failures": failed,
               "source_sha256": plan["sources"], "baseline_summary_rows": {
                   name: csv_rows(ROOT / "manifests" / name) for name in ("dataset_summary.csv", "split_summary.csv")}}
    job.write_immutable_record(OUTPUT / "local_audit.json", private)
    public["private_local_audit_sha256"] = sha(OUTPUT / "local_audit.json")
    job.write_immutable_record(ROOT / "results/phase1/msu-local-audit282-v1.json", public)
    print(json.dumps(public, indent=2))


if __name__ == "__main__":
    main()
