#!/usr/bin/env python3
"""Diagnose Review228-authorized existing bytes without importing outcomes."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import stat
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.oulu import _sha256
from import_oulu_categorical_batch08 import strict_json, verify_preservation
from prepare_oulu_owner_review import private_output
from recover_oulu_archive_identity import file_identity

REVIEW_FILE = "docs/228-review-doc227-oulu-batch09-handoff-unprocessed-input.md"
REVIEW_SHA256 = "de571a6f18aaade72f3e6802abdb58d5511e21d9eb6c4194da04739e318666d6"
HANDOFF_DOCUMENT = "docs/227-review-response-doc226-oulu-batch09-categorical-handoff.md"
HANDOFF_DOCUMENT_SHA256 = "63a0da175df014aa85cd2be4c585dfcc9df77df1773268bf881a548310e02966"
HANDOFF_REPORT = "results/phase1/oulu-categorical-handoff-batch09-v1.json"
HANDOFF_REPORT_SHA256 = "5ec23ec5963afc4e9dd91b6e4b7f1debe7c9a0995fa1d81b52f23f7a148489d2"
CRITERIA_DOCUMENT = "docs/229-review-response-doc228-oulu-batch09-input-diagnostics.md"
CRITERIA_SHA256 = "2b4d3375b5dd2fb6d68f22d915ddc18ea0de6b8d6dd2a4dbf7414f563208b516"
OLD_TEST_SHA256 = "73040da6f9c6210e7d4449cf54233a73de9eb7f0394f3af7bed97030d1883cbe"
OLD_TEST_AST_SHA256 = "0bceffe2665e0a56e51669f3cf8faa0193e10372d15e065726553ff9e086438e"
NEW_TEST_METHOD = "test_batch09_input_diagnostics_review228_strict_read_and_bindings_only"
INPUT_NAME = "oulu-batch09-categorical-review.json"
SOURCE227_CI = {"head_sha": "19dc18cad6e8430241ab4c9358400a0afe651ff5", "run_id": 39375374555, "job_id": 118472218036,
                "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success",
                "listed_successful_steps": 12, "all_steps_success": True}
GLOBAL_BINDINGS = ("review226_sha256", "accepted_AI_report_sha256", "accepted_AI_document_sha256", "observation_input_sha256",
                   "accepted_packet_report_sha256", "source_packet_lineage_sha256", "source_packet_summary_sha256", "dependence_sha256")
PAIR_BINDINGS = ("packet_sha256", "ai_record_sha256", "source_sampling_provenance_sha256", "exact_pair_record_sha256")


def stable_read(path: Path, expected: dict | None = None) -> tuple[bytes, dict]:
    before = path.lstat()
    identity = file_identity(before)
    if not stat.S_ISREG(before.st_mode) or (expected is not None and identity != expected):
        raise ValueError("regular stable pinned file required")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as handle:
        opened = os.fstat(handle.fileno())
        if not stat.S_ISREG(opened.st_mode) or file_identity(opened) != identity:
            raise ValueError("path/open identity mismatch")
        payload = handle.read()
        if file_identity(os.fstat(handle.fileno())) != identity:
            raise ValueError("open file changed during read")
    after = path.lstat()
    if not stat.S_ISREG(after.st_mode) or file_identity(after) != identity or len(payload) != identity["byte_size"]:
        raise ValueError("path changed during read")
    return payload, identity


def snapshot(root: Path) -> dict:
    if root.is_symlink() or not root.is_dir() or root.resolve() != root:
        raise ValueError("canonical nonsymlink root required")
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("symlink in protected root")
        if not path.is_dir():
            payload, _ = stable_read(path)
            result[str(path.relative_to(root))] = hashlib.sha256(payload).hexdigest()
    return result


def diagnose_bytes(payload: bytes, definition: dict, definition_sha256: str) -> dict:
    findings = []
    result = {"strict_JSON_pass": False, "structure_types_pass": False, "source_bindings_pass": False,
              "exact_ordered_ranks_pass": False, "rows_examined": 0, "discrepancies": findings,
              "outcomes_validated": False, "scientific_stop_flags_validated": False, "normalized_human_rows_created": 0}
    try:
        record = strict_json(payload)
    except (ValueError, RecursionError):
        findings.append("strict_JSON_parse_failed")
        return result
    result["strict_JSON_pass"] = True
    schema = True
    bindings = True
    top_fields = {"version", "record_type", "reviewer", "review_definition_sha256", "reviewed_at_utc",
                  "stop_for_prospective_scientific_decision", "pairs", *GLOBAL_BINDINGS}
    if set(record) != top_fields or type(record.get("version")) is not int or record["version"] != 1 or record.get("record_type") != "batch09_categorical_review":
        schema = False
    reviewer = record.get("reviewer")
    if type(reviewer) is not dict or set(reviewer) != {"kind", "id", "personally_inspected_bound_evidence"} or reviewer.get("kind") not in ("owner_human", "designated_human") or type(reviewer.get("id")) is not str or not reviewer["id"].strip() or type(reviewer.get("personally_inspected_bound_evidence")) is not bool:
        schema = False
    try:
        timestamp = record.get("reviewed_at_utc")
        if type(timestamp) is not str:
            raise ValueError("timestamp type")
        parsed = datetime.fromisoformat(timestamp)
        if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
            raise ValueError("timestamp zone")
    except ValueError:
        schema = False
    if type(record.get("stop_for_prospective_scientific_decision")) is not bool:
        schema = False
    if record.get("review_definition_sha256") != definition_sha256 or any(type(record.get(field)) is not str or record[field] != definition[field] for field in GLOBAL_BINDINGS):
        bindings = False
    rows = record.get("pairs")
    ranks_pass = type(rows) is list and len(rows) == 5 and all(type(row) is dict and type(row.get("queue_rank")) is int for row in rows) and [row["queue_rank"] for row in rows] == list(range(80, 85))
    result["exact_ordered_ranks_pass"] = ranks_pass
    if not ranks_pass:
        schema = False
        bindings = False
    else:
        pair_fields = {"queue_rank", "reviewed_assets_sha256", "evidence_sufficient", "same_or_derived_content",
                       "personal_inspection_attested", "owner_decision_attested", "disposition", "capture_provenance_certified",
                       "stop_for_prospective_scientific_decision", *PAIR_BINDINGS}
        for row, expected in zip(rows, definition["pairs"], strict=True):
            result["rows_examined"] += 1
            sufficient, same = row.get("evidence_sufficient"), row.get("same_or_derived_content")
            if set(row) != pair_fields or type(sufficient) is not bool or (sufficient and type(same) is not bool) or (not sufficient and same is not None):
                schema = False
            if any(type(row.get(field)) is not bool for field in ("personal_inspection_attested", "owner_decision_attested", "capture_provenance_certified", "stop_for_prospective_scientific_decision")) or type(row.get("disposition")) is not str:
                schema = False
            if any(type(row.get(field)) is not str or row[field] != expected[field] for field in PAIR_BINDINGS) or type(row.get("reviewed_assets_sha256")) is not dict or row["reviewed_assets_sha256"] != expected["required_assets_sha256"]:
                bindings = False
    result["structure_types_pass"] = schema
    result["source_bindings_pass"] = bindings
    if not schema:
        findings.append("export_structure_or_types_mismatch")
    if not bindings:
        findings.append("source_bindings_or_ranks_mismatch")
    return result


def verify_authority(preflight: dict) -> None:
    expected = {"checkpoint": 229, "review228_sha256": REVIEW_SHA256, "handoff_document_sha256": HANDOFF_DOCUMENT_SHA256,
                "handoff_report_sha256": HANDOFF_REPORT_SHA256, "prospective_criteria_sha256": CRITERIA_SHA256,
                "diagnostic_only_authorized": True, "human_input_collection_authorized": False, "import_authorized": False,
                "effective_activation_authorized": False, "model_execution_authorized": False, "scientific_readiness": False}
    if any(type(preflight.get(field)) is not type(value) or preflight[field] != value for field, value in expected.items()):
        raise ValueError("exact Review228 diagnostic-only authority required")
    if any(type(preflight.get("source227_CI", {}).get(field)) is not type(value) or preflight["source227_CI"][field] != value for field, value in SOURCE227_CI.items()):
        raise ValueError("exact successful227 CI required")


def verify_context(preflight: dict, report: dict) -> dict:
    records = {}
    for field, digest_field in (("handoff_preflight_path", "private_preflight_sha256"), ("handoff_verification_path", "private_blocked_verification_sha256")):
        payload, _ = stable_read(Path(preflight[field]))
        if hashlib.sha256(payload).hexdigest() != report[digest_field]:
            raise ValueError("original227 singleton drift")
        records[field] = strict_json(payload)
    original, verification = records["handoff_preflight_path"], records["handoff_verification_path"]
    current_test = ROOT / "tests/test_oulu.py"
    transition = {"old_sha256": OLD_TEST_SHA256, "new_sha256": _sha256(current_test), "only_added_test": NEW_TEST_METHOD, "prior_test_AST_unchanged": True}
    if preflight["test_transition"] != transition:
        raise ValueError("explicit229 test transition required")
    tree = ast.parse(current_test.read_bytes())
    removed = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [item for item in node.body if isinstance(item, ast.FunctionDef) and item.name == NEW_TEST_METHOD]
            removed += len(methods)
            node.body = [item for item in node.body if item not in methods]
    if removed != 1 or hashlib.sha256(ast.dump(tree).encode()).hexdigest() != OLD_TEST_AST_SHA256:
        raise ValueError("prior test AST drift")
    if len(original["protected_snapshots"]) != 96 or len(original["pinned_file_sha256"]) != 272:
        raise ValueError("original96 roots/272 pins required")
    for field in ("frozen_file_sha256", "study_config_sha256"):
        if preflight[field] != original[field]:
            raise ValueError("inherited frozen/config drift")
    for name, digest in original["pinned_file_sha256"].items():
        expected = transition["new_sha256"] if Path(name).resolve() == current_test.resolve() else digest
        if preflight["pinned_file_sha256"].get(name) != expected:
            raise ValueError("inherited source pin omitted/rebound")
    core = verification["prepared_core_file_sha256"]
    core_digest = hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if len(core) != 18 or core_digest != report["prepared_core_map_sha256"] or preflight["original_prepared_core_sha256"] != core:
        raise ValueError("exact original18-file core required")
    main, sibling = verification["main_root"], verification["sibling_root"]
    expected_roots = {**original["protected_snapshots"], main: {**core, INPUT_NAME: preflight["input_sha256"]}, sibling: core}
    if len(expected_roots) != 98 or preflight["protected_snapshots"] != expected_roots or preflight["main_root"] != main or preflight["sibling_root"] != sibling or preflight["input_path"] != str(Path(main) / INPUT_NAME):
        raise ValueError("exact complete19/18 maps and original96 roots required")
    return verification


def diagnose(args: argparse.Namespace) -> dict:
    private_output(args.out_root, [args.preflight, args.input])
    preflight = strict_json(stable_read(args.preflight)[0])
    private_output(args.out_root, [Path(name) for name in preflight["protected_snapshots"]])
    verify_authority(preflight)
    for name, expected in ((REVIEW_FILE, REVIEW_SHA256), (HANDOFF_DOCUMENT, HANDOFF_DOCUMENT_SHA256), (HANDOFF_REPORT, HANDOFF_REPORT_SHA256)):
        if _sha256(ROOT / name) != expected:
            raise ValueError("committed public authority drift")
    criteria = (ROOT / CRITERIA_DOCUMENT).read_text().split("## Prospective Criteria\n", 1)[1].split("\n## Execution", 1)[0]
    if hashlib.sha256(criteria.encode()).hexdigest() != CRITERIA_SHA256 or criteria != preflight["prospective_criteria_text"] or _sha256(Path(__file__)) != preflight["runner_sha256"] or str(args.input) != preflight["input_path"]:
        raise ValueError("criteria/runner/input binding drift")
    report = strict_json((ROOT / HANDOFF_REPORT).read_bytes())
    verify_context(preflight, report)
    verify_preservation(preflight)
    payload, identity = stable_read(args.input, preflight["input_identity"])
    if hashlib.sha256(payload).hexdigest() != preflight["input_sha256"] or len(payload) != preflight["input_byte_size"]:
        raise ValueError("pinned input size/hash mismatch")
    definition_path = Path(preflight["main_root"]) / "review_definition.json"
    definition_payload, _ = stable_read(definition_path)
    if hashlib.sha256(definition_payload).hexdigest() != report["review_definition_sha256"]:
        raise ValueError("original definition binding drift")
    checks = diagnose_bytes(payload, strict_json(definition_payload), report["review_definition_sha256"])
    verify_preservation(preflight)
    for root in (preflight["main_root"], preflight["sibling_root"]):
        if snapshot(Path(root)) != preflight["protected_snapshots"][root]:
            raise ValueError("post-read complete root drift")
    if file_identity(args.input.lstat()) != identity:
        raise ValueError("input identity changed after diagnosis")
    result = {"version": 1, "checkpoint": 229, "record_type": "unprocessed_input_structural_diagnostic",
              "status": "unverified_input_pending_owner_origin_functional_sequence_and_formal_review",
              "review228_sha256": REVIEW_SHA256, "preflight_sha256": _sha256(args.preflight), "input_sha256": preflight["input_sha256"],
              "input_byte_size": len(payload), "stable_input_identity_verified": True, "input_preserved_in_place": True,
              "complete_main_sibling_file_counts": [19, 18], "original_prepared_core_files_unchanged": 18,
              "checks": checks, "authenticity_established": False, "functional_sequence_established": False,
              "independent_owner_authentication_claimed": False, "retrospective_collection_authority": False,
              "owner_answers_accepted": 0, "import_rows_created": 0, "effective_dispositions_activated": 0,
              "human_input_collection_authorized": False, "import_authorized": False, "effective_activation_authorized": False,
              "model_execution_authorized": False, "scientific_readiness": False, "original227_failed_criterion_rewritten": False}
    private_output(args.out_root, [Path(name) for name in preflight["protected_snapshots"]])
    write_immutable_record(args.out_root / "diagnostic.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("preflight", "input", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        result = diagnose(parser.parse_args())
        print(json.dumps({"status": result["status"], "checks": result["checks"], "import_rows_created": 0}, sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        print("BATCH09 INPUT DIAGNOSTIC REFUSED: no owner outcomes accepted or imported", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())