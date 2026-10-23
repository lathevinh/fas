"""Actual bounded visual review and SiW-only local-audit summary promotion."""

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import time

import preprocess_siw291 as run
from complete_casia287 import csv_rows, baseline_errors
from fas.preregistration import validate_stage

PROVENANCE = ("bounded pinned-reference Protocol-I intersection release/integrity/decoded-exact audit291; "
              "video grouping only; participant/joined ancestry not certified")


def checks():
    output = run.OUTPUT
    public = run.read(run.SUMMARY)
    for relative, digest in public["private_record_sha256"].items():
        if run.sha(output / relative) != digest:
            raise ValueError("creation-time software record drift")
    resources = run.read(output / "resources.json")
    if (resources["accounting_complete"] is not True or resources["image_export_software_complete"] is not True
            or resources["failure"] is not None or resources["package_wall_seconds"] >= run.CAPS["wall_seconds"]
            or resources["model_scores"] or resources["fitted_scores"] or resources["evaluation"]):
        raise ValueError("successful full software/resources and no classifier evaluation required")
    run.enforce(resources["sampled_peaks"], work=False)
    actual = run.shared.usage(os.getpgrp(), output / ".unused")
    actual["output_bytes"] = sum(run.shared.retained.tree_bytes(root) for root in run.ROOTS) + actual["temporary_bytes"]
    run.enforce(actual, work=False)
    plan = run.read(output / "plan.json")
    run.shared.check_bindings(plan["sources"])
    run.guard(plan)
    canonical = run.read(run.FROZEN / "siw_mv2_canonical.json")
    expected = run.reconcile(canonical["videos"], csv_rows(run.FROZEN / "siw_mv2_roles.csv"))
    if {r["video_id"]: r for r in expected} != {r["video_id"]: r for r in plan["videos"]}:
        raise ValueError("exact canonical/source/null-test join drift")
    readback = run.read(output / "readback.json")
    manifest = run.shared.read_verified_json(output / "full_manifest.json", readback["full_manifest_sha256"])["rows"]
    if len(manifest) != 1680 or {r["video_id"] for r in manifest} != {r["video_id"] for r in expected}:
        raise ValueError("exact1680 original-denominator manifest required")
    original = {r["video_id"]: r for r in expected}
    for row in manifest:
        parent = original[row["video_id"]]
        if (any(row[key] != parent[key] for key in ("role", "binary_label", "official_split", "subject_id"))
                or row["replacement"] is not False or row["retain_original_denominator"] is not True
                or row["model_score"] is not None or row["classifier_error"] is not None):
            raise ValueError("manifest original/scoreless/null-role boundary drift")
    for relative, digest in {**readback["per_unit_sha256"], **readback["asset_sha256"]}.items():
        if run.sha(output / relative) != digest:
            raise ValueError("full native/image/replay commitment drift")
    if any((output / "temporary").iterdir()):
        raise ValueError("owned staging must be empty")
    counts = {"originals": len(manifest), "selected": sum(r["selected_frame"] is not None for r in manifest),
              "detector_success": sum(r["detector_status"] == "success" for r in manifest),
              "detector_failure": sum(r["detector_status"] == "failed" for r in manifest),
              "pre_detector_failure": sum(r["selected_frame"] is None for r in manifest)}
    if any(readback[key] != value or resources[key] != value for key, value in counts.items()):
        raise ValueError("manifest/readback/resource aggregate drift")
    return resources, readback, manifest, counts


def visual(opened, observations, crop_pass):
    resources, readback, rows, _ = checks()
    expected = {s["path"] for s in readback["visual_sheets"]}
    if not observations or set(opened) != expected or len(opened) != len(expected):
        raise ValueError("all fixed/failure sheets must actually be opened and described")
    lookup, totals = {r["index"]: r for r in rows}, Counter()
    for sheet in readback["visual_sheets"]:
        if run.sha(run.OUTPUT / sheet["path"]) != sheet["sha256"]:
            raise ValueError("opened sheet hash drift")
        for index in sheet["indices"]:
            row = lookup[index]
            totals["tiles"] += 1
            totals["no_image_placeholders" if row["selected_frame"] is None else
                   "face_crops" if row["detector_status"] == "success" else "selected_failure_images"] += 1
    if crop_pass and not totals["face_crops"]:
        raise ValueError("no crop usability pass without real face crops")
    receipt = {"checkpoint": 291, "dataset": "SiW-Mv2", "visual_inspection_completed": True,
               "sample_crop_usability_check_pass": crop_pass, "observations": observations,
               "opened_tiles": totals["tiles"], "inspected_face_crops": totals["face_crops"],
               "selected_failure_images": totals["selected_failure_images"],
               "no_image_placeholders": totals["no_image_placeholders"],
               "all_images_visually_inspected": False, "primary_image_preprocessing_complete": crop_pass,
               "opened_sheet_sha256": {name: run.sha(run.OUTPUT / name) for name in opened},
               "resources_sha256": run.sha(run.OUTPUT / "resources.json"),
               "readback_sha256": run.sha(run.OUTPUT / "readback.json"),
               "checker_sha256": run.sha(Path(__file__)), "recorded_unix_seconds": time.time(),
               "accounting_complete": resources["accounting_complete"]}
    run.write(run.OUTPUT / "visual_review.json", receipt)
    run.write(run.ROOT / "results/phase1/siwmv2-preprocessing291-visual-review-v1.json",
              {**{k: v for k, v in receipt.items() if k != "opened_sheet_sha256"},
               "private_visual_review_sha256": run.sha(run.OUTPUT / "visual_review.json")})


def prepare_local():
    resources, readback, rows, counts = checks()
    inspected = run.read(run.OUTPUT / "visual_review.json")
    if (inspected["visual_inspection_completed"] is not True or inspected["sample_crop_usability_check_pass"] is not True
            or inspected["resources_sha256"] != run.sha(run.OUTPUT / "resources.json")
            or inspected["readback_sha256"] != run.sha(run.OUTPUT / "readback.json")
            or inspected["checker_sha256"] != run.sha(Path(__file__))):
        raise ValueError("current actual visual/crop usability pass required")
    errors = validate_stage(run.ROOT, "data-audit", frozen_root=run.FROZEN)
    if set(errors) != baseline_errors(("SiW-Mv2",)) or len(errors) != 2:
        raise ValueError("exact two SiW baseline errors required: " + repr(errors))
    plan = run.read(run.OUTPUT / "plan.json")
    public = {"checkpoint": 291, "dataset": "SiW-Mv2", **counts,
              "source_role_originals": run.ROLES, "null_role_test_originals": 623,
              "source_originals": 1057, "participant_identity_verified": False,
              "group_unit": "video", "subjects": None, "target_source_roles": 0,
              "native_frames": readback["native_frames"], "strict_replay_count": readback["strict_replay_count"],
              "image_assets": readback["image_assets"], "video_crc_checked": 1680,
              "archive_sha256": run.read(run.OUTPUT / "archive_integrity.json")["archive_sha256"],
              "excluded_videos_not_processed": plan["excluded_originals"],
              "missing_references_not_invented": plan["missing_references"],
              "exact_duplicate_groups": readback["exact_duplicate_groups"], "forbidden_exact_crossings": 0,
              "participant_disjointness_certified": False, "near_duplicate_independence_certified": False,
              "joined_domain_assurance": False, "model_scores": 0, "fitted_scores": 0, "evaluation": False,
              "scientific_readiness": False, "accounting_complete": True,
              "primary_image_preprocessing_complete": True, "local_audit_complete": False,
              "resources_sha256": run.sha(run.OUTPUT / "resources.json"),
              "readback_sha256": run.sha(run.OUTPUT / "readback.json"),
              "visual_review_sha256": run.sha(run.OUTPUT / "visual_review.json"),
              "checker_sha256": run.sha(Path(__file__)), "normal_validator_baseline_errors": errors,
              "summary_before_rows": {name: csv_rows(run.ROOT / "manifests" / name)
                                      for name in ("dataset_summary.csv", "split_summary.csv")}}
    run.write(run.OUTPUT / "local_checks.json", public)


def finalize():
    checks()
    certificate = run.read(run.OUTPUT / "local_checks.json")
    if certificate["checker_sha256"] != run.sha(Path(__file__)):
        raise ValueError("local checker identity drift")
    for name, before in certificate["summary_before_rows"].items():
        expected = [{**row, **({"audit_status": "complete", **({"metadata_source": PROVENANCE}
                     if name == "dataset_summary.csv" else {})} if row["dataset"] == "SiW-Mv2" else {})}
                    for row in before]
        if csv_rows(run.ROOT / "manifests" / name) != expected:
            raise ValueError("only SiW status/provenance fields may change")
    errors = validate_stage(run.ROOT, "data-audit", frozen_root=run.FROZEN)
    if errors:
        raise ValueError("normal external-frozen-root data-audit must pass: " + repr(errors))
    result = {k: v for k, v in certificate.items() if k != "summary_before_rows"}
    result.update(local_audit_complete=True, audit_summary_statuses_changed=True,
                  status="local_release_video_group_integrity_and_primary_image_complete",
                  normal_validator_remaining_errors=errors,
                  combined_wall_seconds_through_local_completion=time.time() - run.authority()["started_unix_seconds"],
                  summary_after_sha256={name: run.sha(run.ROOT / "manifests" / name)
                                        for name in certificate["summary_before_rows"]},
                  local_checks_sha256=run.sha(run.OUTPUT / "local_checks.json"))
    run.write(run.OUTPUT / "local_audit.json", result)
    run.write(run.ROOT / "results/phase1/siwmv2-local-audit291-v1.json",
              {**result, "private_local_audit_sha256": run.sha(run.OUTPUT / "local_audit.json")})
    print(json.dumps({k: result[k] for k in ("originals", "selected", "detector_success",
                                           "detector_failure", "local_audit_complete")}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    for mode in ("record-visual", "prepare-local", "finalize-local"):
        modes.add_argument("--" + mode, action="store_true")
    parser.add_argument("--opened", action="append", default=[])
    parser.add_argument("--observations")
    parser.add_argument("--crop-usability-pass", action="store_true")
    args = parser.parse_args()
    run.shared.retained.arm_deadline(run.authority()["deadline_unix_seconds"])
    if args.record_visual:
        visual(args.opened, args.observations, args.crop_usability_pass)
    elif args.prepare_local:
        prepare_local()
    else:
        finalize()


if __name__ == "__main__":
    main()
