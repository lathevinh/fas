#!/usr/bin/env python3
"""Freeze OULU transaction dispositions from accepted private media evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.oulu import _sha256
from fas.transactions import calibration_fit_rows, technical_population_counts, technical_transaction, validate_transaction_policy


def export(audit_root: Path, frozen_root: Path, out_root: Path) -> dict:
    source, frozen, output = audit_root.resolve(), frozen_root.resolve(), out_root.resolve()
    if out_root.exists() or out_root.is_symlink() or not source.is_dir() or not frozen.is_dir():
        raise ValueError("missing input or existing output")
    if any(output.is_relative_to(path) or path.is_relative_to(output) for path in (ROOT, source, frozen)):
        raise ValueError("unsafe private output boundary")
    policy_path = ROOT / "configs/transaction_policy_v1.yaml"
    policy = json.loads(policy_path.read_bytes())
    validate_transaction_policy(policy)
    public_path = ROOT / "results/phase1/oulu-per-video-media-audit-v1.json"
    accepted = json.loads(public_path.read_bytes())
    summary = json.loads((source / "summary.json").read_bytes())
    if _sha256(source / "summary.json") != accepted["private_summary_sha256"]:
        raise ValueError("accepted media summary drift")
    if _sha256(source / "lineage.json") != accepted["lineage_sha256"]:
        raise ValueError("accepted media lineage drift")
    if _sha256(source / "duplicate_groups.json") != accepted["duplicate_groups_sha256"]:
        raise ValueError("accepted duplicate evidence drift")
    frozen_hashes = {path.name: _sha256(path) for path in frozen.iterdir()}
    if frozen_hashes != accepted["frozen_artifact_sha256"]:
        raise ValueError("permanent role or canonical drift")
    paths = sorted((source / "videos").glob("*.json"))
    bundle = hashlib.sha256("".join(f"{path.stem}:{_sha256(path)}\n" for path in paths).encode()).hexdigest()
    if bundle != accepted["video_record_bundle_sha256"] or len(paths) != 4950:
        raise ValueError("accepted media record bundle drift")
    canonical = {row["video_id"]: row for row in json.loads((frozen / "oulu_npu_canonical.json").read_bytes())["videos"]}
    with (frozen / "oulu_npu_roles.csv").open(newline="") as handle:
        role_rows = list(csv.DictReader(handle))
    roles = {row["video_id"]: row for row in role_rows}
    if len(roles) != len(role_rows) or set(roles) != set(canonical) or {path.stem for path in paths} != set(canonical):
        raise ValueError("transaction identity population mismatch")
    records = []
    for path in paths:
        media = json.loads(path.read_bytes())
        identity = path.stem
        if media["video_id"] != identity or media["role"] != roles[identity]["role"]:
            raise ValueError("media identity or permanent role mismatch")
        if any(media[key] != canonical[identity][key] for key in ("binary_label", "official_split", "media_relpath", "media_archive", "byte_size")):
            raise ValueError("media canonical metadata mismatch")
        records.append({**technical_transaction(media), "media_record_sha256": _sha256(path),
                        "media_sha256": media["media_sha256"], "official_split": media["official_split"]})
    populations = technical_population_counts(records)
    calibration = [row for row in records if row["role"] == "branch_calibration"]
    if calibration_fit_rows(calibration):
        raise ValueError("model-free export cannot contain calibration scores")
    definition = {
        "version": 1, "state": "frozen_before_model_execution",
        "policy_file": "configs/transaction_policy_v1.yaml", "policy_sha256": _sha256(policy_path),
        "review_file": "docs/108-review-doc107-oulu-per-video-media-audit.md",
        "review_sha256": _sha256(ROOT / "docs/108-review-doc107-oulu-per-video-media-audit.md"),
        "accepted_media_report_sha256": _sha256(public_path),
        "accepted_media_record_bundle_sha256": bundle,
        "frozen_artifact_sha256": frozen_hashes,
        "selector_code_sha256": _sha256(ROOT / "src/fas/transactions.py"),
        "export_code_sha256": _sha256(Path(__file__)),
        "preprocessing_sha256": _sha256(ROOT / "configs/preprocessing_v2.yaml"),
        "scope": "OULU definition only; source fits only in folds where OULU is a source",
        "model_execution_authorized": False, "scientific_readiness": False,
    }
    write_immutable_record(output / "definition.json", definition)
    for row in records:
        write_immutable_record(output / "transactions" / (row["video_id"] + ".json"), row)
    if {path.name: _sha256(path) for path in frozen.iterdir()} != frozen_hashes:
        raise ValueError("frozen inputs changed during export")
    if _sha256(policy_path) != definition["policy_sha256"]:
        raise ValueError("policy changed during export")
    transaction_bundle = hashlib.sha256("".join(
        f"{row['video_id']}:{_sha256(output / 'transactions' / (row['video_id'] + '.json'))}\n"
        for row in records
    ).encode()).hexdigest()
    result = {
        "version": 1, "status": "transaction_definition_frozen_model_execution_blocked",
        "transactions": len(records), "populations": populations,
        "selected_primary_frames": sum(row["selected_frame"] is not None for row in records),
        "terminal_technical_failures": sum(row["technical_status"] == "terminal_failure" for row in records),
        "calibration_original_denominator": len(calibration),
        "calibration_frame_available": sum(row["selected_frame"] is not None for row in calibration),
        "calibration_actual_score_fit_rows": 0,
        "definition_sha256": _sha256(output / "definition.json"),
        "transaction_record_bundle_sha256": transaction_bundle,
        "frozen_inputs_unchanged": True, "detector_or_model_executed": False,
        "frame_pixels_exported": False, "scientific_readiness": False,
    }
    write_immutable_record(output / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-root", type=Path, required=True)
    parser.add_argument("--frozen-root", type=Path, required=True)
    parser.add_argument("--out-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(export(args.audit_root, args.frozen_root, args.out_root), sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError, RuntimeError):
        print("TRANSACTION EXPORT FAILED: private evidence/boundary/policy invalid; no completion claimed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())