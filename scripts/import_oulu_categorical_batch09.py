#!/usr/bin/env python3
"""Import only the existing Review230-authorized export without activation."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import diagnose_oulu_batch09_input as diagnostic
import prepare_oulu_categorical_batch09 as handoff
from diagnose_oulu_batch09_input import diagnose_bytes, stable_read, strict_json
from fas.freeze import write_immutable_record
from fas.oulu import _sha256
from import_oulu_categorical_batch08 import verify_preservation
from prepare_oulu_categorical_batch09 import CATEGORICAL_RULES
from prepare_oulu_owner_review import private_output
from prepare_oulu_visual_batch05 import bundle

REVIEW_FILE = "docs/230-review-doc229-oulu-batch09-input-diagnostics.md"
REVIEW_SHA256 = "ff917d89b672c9e571582de90b1e921d3e099033143cb49f5d38745169903d49"
DIAGNOSTIC_DOCUMENT = "docs/229-review-response-doc228-oulu-batch09-input-diagnostics.md"
DIAGNOSTIC_DOCUMENT_SHA256 = "9492a6933ca83a438be1721e97f927feb94f38dfabd6c98f432bf4dfe879ca4a"
DIAGNOSTIC_REPORT = "results/phase1/oulu-batch09-input-diagnostic-v1.json"
DIAGNOSTIC_REPORT_SHA256 = "c9d3de85715fef6a74f06ef77b05bd01d73379d770a0b51583f57260a3ceff4c"
CRITERIA_DOCUMENT = "docs/231-review-response-doc230-oulu-batch09-categorical-import.md"
CRITERIA_SHA256 = "094e30a0c678c005e47edab6a4346f7a0b612c162d575dbeeb70031d4685e635"
INPUT_SHA256 = "c845cdfd58044b9a03628ff0b6a137a25d75e7533c28609b8b3c32b727516883"
OLD_TEST_SHA256 = "f697dc83fc73c033f380477661d0c82db6e32c8a3aac4738d9284e109987b302"
OLD_TEST_AST_SHA256 = "38b3b3371110bcc95ef15bcbcab52ff687c2ea3ad2260ffb612b0bbc2c2f283b"
NEW_TEST_METHOD = "test_batch09_import_review230_strict_outcomes_preservation_and_pending"
SOURCE229_CI = {"head_sha": "299d4ede3f0ec452fe8174befbec390c8b85a611", "run_id": 39378725578, "job_id": 118482649397,
                "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success",
                "listed_successful_steps": 12, "all_steps_success": True}
AUTHORITY_BINDINGS = {REVIEW_FILE: REVIEW_SHA256, DIAGNOSTIC_DOCUMENT: DIAGNOSTIC_DOCUMENT_SHA256,
                      DIAGNOSTIC_REPORT: DIAGNOSTIC_REPORT_SHA256, diagnostic.REVIEW_FILE: diagnostic.REVIEW_SHA256,
                      diagnostic.HANDOFF_DOCUMENT: diagnostic.HANDOFF_DOCUMENT_SHA256,
                      diagnostic.HANDOFF_REPORT: diagnostic.HANDOFF_REPORT_SHA256,
                      handoff.REVIEW_FILE: handoff.REVIEW_SHA256, handoff.AI_DOCUMENT_FILE: handoff.AI_DOCUMENT_SHA256,
                      handoff.AI_REPORT_FILE: handoff.AI_REPORT_SHA256, handoff.PACKET_REPORT_FILE: handoff.PACKET_REPORT_SHA256}

DERIVED_FIELDS = {"validated_disposition", "ai_disposition", "disagreement_with_AI", "reconciliation_required",
                  "comparison_disposition", "scientific_stop_independently_derived", "checkpoint_review_pending",
                  "semantic_acceptance_pending", "effective_disposition_activated", "counts_as_accepted_current_effective_disposition",
                  "model_execution_authorized", "scientific_readiness"}


class OutcomeDiscrepancy(ValueError):
    def __init__(self, scientific_stop_required: bool):
        super().__init__("reported categorical outcome or stop mismatch")
        self.scientific_stop_required = scientific_stop_required


def validate_input(payload: bytes, definition: dict, digest: str) -> tuple[dict, list[dict]]:
    record = strict_json(payload)
    rows = record.get("pairs")
    if type(rows) is list and any(type(row) is dict and row.keys() & DERIVED_FIELDS for row in rows):
        raise ValueError("supplied owner field collides with importer metadata")
    checks = diagnose_bytes(payload, definition, digest)
    if not all(checks[field] is True for field in ("strict_JSON_pass", "structure_types_pass", "source_bindings_pass", "exact_ordered_ranks_pass")):
        raise ValueError("strict categorical structure/types/source bindings required")
    if json.dumps(definition.get("categorical_rules"), sort_keys=True) != json.dumps(CATEGORICAL_RULES, sort_keys=True):
        raise ValueError("unchanged strict categorical rules required")
    if record["reviewer"]["personally_inspected_bound_evidence"] is not True:
        raise ValueError("reviewer personal-inspection attestation required")
    outcomes = []
    mismatched = False
    for row, expected in zip(rows, definition["pairs"], strict=True):
        if row["personal_inspection_attested"] is not True or row["owner_decision_attested"] is not True or row["capture_provenance_certified"] is not False:
            raise ValueError("both true attestations and no capture certification required")
        sufficient, same = row["evidence_sufficient"], row["same_or_derived_content"]
        if type(sufficient) is not bool or (sufficient and type(same) is not bool) or (not sufficient and same is not None):
            raise ValueError("explicit valid boolean/null categorical answers required")
        disposition = next(rule["disposition"] for rule in CATEGORICAL_RULES if rule["evidence_sufficient"] is sufficient and rule["same_or_derived_content"] is same)
        stop = disposition == "confirmed_same_content_or_derived_lineage"
        ai = expected["ai_disposition"]
        if type(ai) is not str or ai not in {rule["disposition"] for rule in CATEGORICAL_RULES}:
            raise ValueError("valid distinct original AI proposal required")
        mismatched |= row["disposition"] != disposition or row["stop_for_prospective_scientific_decision"] is not stop
        disagreement = disposition != ai
        outcomes.append({**row, "validated_disposition": disposition, "ai_disposition": ai, "disagreement_with_AI": disagreement,
                         "reconciliation_required": disagreement, "comparison_disposition": "uncertain_insufficient_evidence" if disagreement else disposition,
                         "scientific_stop_independently_derived": stop, "checkpoint_review_pending": True, "semantic_acceptance_pending": True,
                         "effective_disposition_activated": False, "counts_as_accepted_current_effective_disposition": False,
                         "model_execution_authorized": False, "scientific_readiness": False})
    stop = any(row["scientific_stop_independently_derived"] for row in outcomes)
    if mismatched or record["stop_for_prospective_scientific_decision"] is not stop:
        raise OutcomeDiscrepancy(stop)
    return record, outcomes


def verify_authority(preflight: dict) -> None:
    expected = {"checkpoint": 231, "review230_sha256": REVIEW_SHA256, "review228_sha256": diagnostic.REVIEW_SHA256,
                "diagnostic_document_sha256": DIAGNOSTIC_DOCUMENT_SHA256, "diagnostic_report_sha256": DIAGNOSTIC_REPORT_SHA256,
                "prospective_criteria_sha256": CRITERIA_SHA256, "input_sha256": INPUT_SHA256, "input_byte_size": 6710,
                "import_authorized": True, "human_input_collection_authorized": False, "effective_activation_authorized": False,
                "model_execution_authorized": False, "scientific_readiness": False}
    if any(type(preflight.get(field)) is not type(value) or preflight[field] != value for field, value in expected.items()):
        raise ValueError("exact Review230 existing-input import-only authority required")
    check = preflight.get("source229_CI")
    if type(check) is not dict or any(type(check.get(field)) is not type(value) or check[field] != value for field, value in SOURCE229_CI.items()):
        raise ValueError("exact successful229 CI required")


def verify_context(preflight: dict, report: dict) -> dict:
    records = {}
    fields = {"diagnostic_preflight_path": "private_preflight_sha256", "diagnostic_main_path": "private_diagnostic_main_sha256",
              "diagnostic_sibling_path": "private_diagnostic_sibling_sha256", "owner_confirmation_path": "private_owner_confirmation_sha256",
              "diagnostic_verification_path": "private_verification_sha256"}
    for field, digest_field in fields.items():
        payload, _ = stable_read(Path(preflight[field]))
        if hashlib.sha256(payload).hexdigest() != report[digest_field]:
            raise ValueError("exact229 private evidence drift")
        records[field] = strict_json(payload)
    original = records["diagnostic_preflight_path"]
    current_test = ROOT / "tests/test_oulu.py"
    transition = {"old_sha256": OLD_TEST_SHA256, "new_sha256": _sha256(current_test), "only_added_test": NEW_TEST_METHOD, "prior_test_AST_unchanged": True}
    if preflight["test_transition"] != transition:
        raise ValueError("explicit231 test transition required")
    tree = ast.parse(current_test.read_bytes())
    removed = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [item for item in node.body if isinstance(item, ast.FunctionDef) and item.name == NEW_TEST_METHOD]
            removed += len(methods)
            node.body = [item for item in node.body if item not in methods]
    if removed != 1 or hashlib.sha256(ast.dump(tree).encode()).hexdigest() != OLD_TEST_AST_SHA256:
        raise ValueError("prior complete test AST drift")
    if len(original["protected_snapshots"]) != 98 or len(original["pinned_file_sha256"]) != 278:
        raise ValueError("original98 roots/278 pins required")
    for field in ("frozen_file_sha256", "study_config_sha256"):
        if preflight[field] != original[field]:
            raise ValueError("inherited frozen/config protection drift")
    for name, digest in original["pinned_file_sha256"].items():
        expected = transition["new_sha256"] if Path(name).resolve() == current_test.resolve() else digest
        if preflight["pinned_file_sha256"].get(name) != expected:
            raise ValueError("inherited pin omitted/rebound")
    expected_roots = {**original["protected_snapshots"]}
    for field in ("diagnostic_main_path", "diagnostic_sibling_path"):
        path = Path(preflight[field])
        expected_roots[str(path.parent)] = {path.name: report[fields[field]]}
    if len(expected_roots) != 100 or preflight["protected_snapshots"] != expected_roots:
        raise ValueError("exact100 inherited/diagnostic roots required")
    for field in ("main_root", "sibling_root", "input_path", "input_identity", "input_sha256", "input_byte_size"):
        if preflight[field] != original[field]:
            raise ValueError("exact existing input/core/identity binding required")
    confirmation = records["owner_confirmation_path"]
    if confirmation["input_sha256"] != INPUT_SHA256 or confirmation["classification"] != "owner_self_attested_genuine_export_intended_submission" or confirmation["blank_form_sequence"] != "owner_attested_completed_before_genuine_judgments" or confirmation["separate_synthetic_sequence"] != "owner_attested_completed_before_genuine_judgments" or confirmation["independent_owner_authentication_claimed"] is not False or confirmation["retrospective_collection_authority"] is not False:
        raise ValueError("original owner self-attestation and limits required")
    verification = records["diagnostic_verification_path"]
    if verification["owner_confirmation_sha256"] != report["private_owner_confirmation_sha256"] or verification["input_sha256"] != INPUT_SHA256:
        raise ValueError("accepted229 confirmation/input chain required")
    return original


def verify_sources(definition: dict, preflight: dict) -> list[Path]:
    ai_report = strict_json((ROOT / handoff.AI_REPORT_FILE).read_bytes())
    packet_report = strict_json((ROOT / handoff.PACKET_REPORT_FILE).read_bytes())
    ai_root, packet_root = Path(definition["ai_root"]), Path(definition["packet_root"])
    for name, field in (("definition.json", "private_definition_sha256"), ("ledger.json", "private_ledger_sha256"), ("summary.json", "private_summary_sha256")):
        if _sha256(ai_root / name) != ai_report[field]:
            raise ValueError("original225 AI source drift")
    for name, field in (("lineage.json", "private_lineage_sha256"), ("summary.json", "private_summary_sha256")):
        if _sha256(packet_root / name) != packet_report[field]:
            raise ValueError("accepted223 packet source drift")
    ai_paths = sorted((ai_root / "pairs").glob("*.json"))
    if [path.name for path in ai_paths] != [f"{rank:06d}.json" for rank in range(80, 85)] or bundle(ai_paths) != ai_report["pair_record_bundle_sha256"]:
        raise ValueError("exact original225 proposal bundle required")
    observation_payload, _ = stable_read(Path(preflight["observations_path"]))
    if hashlib.sha256(observation_payload).hexdigest() != ai_report["observation_input_sha256"] or definition["observation_input_sha256"] != ai_report["observation_input_sha256"]:
        raise ValueError("original225 observation drift")
    observations = strict_json(observation_payload)
    dependence = {field: observations[field] for field in ("exact_reused_video_rank_groups", "visually_correlated_configuration_rank_groups")}
    if definition["dependence"] != dependence or definition["dependence_sha256"] != handoff.structured_digest(dependence) or definition["source_packet_lineage_sha256"] != packet_report["private_lineage_sha256"] or definition["source_packet_summary_sha256"] != packet_report["private_summary_sha256"]:
        raise ValueError("original dependence/packet provenance drift")
    queue_root = Path(preflight["queue_root"])
    queue_public = strict_json((ROOT / "results/phase1/oulu-lineage-exact-evidence-v1.json").read_bytes())
    queue_paths = sorted((queue_root / "pairs").glob("*.json"))
    if len(queue_paths) != 6640 or bundle(queue_paths) != queue_public["pair_record_bundle_sha256"] or _sha256(queue_root / "summary.json") != queue_public["private_summary_sha256"]:
        raise ValueError("exact complete6640 frozen queue required")
    for pair, observed in zip(definition["pairs"], observations["pairs"], strict=True):
        rank = pair["queue_rank"]
        packet_path, ai_path = packet_root / "pairs" / f"{rank:06d}" / "packet.json", ai_root / "pairs" / f"{rank:06d}.json"
        packet, ai, queue = [strict_json(stable_read(path)[0]) for path in (packet_path, ai_path, queue_paths[rank])]
        for path, field in ((packet_path, "packet_sha256"), (ai_path, "ai_record_sha256"), (queue_paths[rank], "exact_pair_record_sha256")):
            if _sha256(path) != pair[field]:
                raise ValueError("original packet/AI/queue row drift")
        if any(type(source["queue_rank"]) is not int or source["queue_rank"] != rank for source in (packet, ai, queue, observed)) or packet["candidate"] != ai["candidate"] or packet["candidate"] != queue["candidate"] or ai["proposed_disposition"] != pair["ai_disposition"] or ai["proposed_disposition"] != observed["proposed_disposition"]:
            raise ValueError("exact rank/candidate/original proposal mismatch")
        if ai["packet_sha256"] != pair["packet_sha256"] or ai["exact_pair_record_sha256"] != packet["exact_pair_record_sha256"] or packet["exact_pair_record_sha256"] != pair["exact_pair_record_sha256"] or handoff.structured_digest(ai["video_sampling_provenance"]) != pair["source_sampling_provenance_sha256"] or ai["video_manifest_sha256"] != packet["video_manifest_sha256"] or ai["video_manifest_sha256"] != pair["video_manifest_sha256"]:
            raise ValueError("original sampling/manifests/source references mismatch")
        if ai["assets_actually_viewed_sha256"] != packet["image_sha256"] or observed["assets_actually_viewed_sha256"] != packet["image_sha256"] or ai["human_review_performed"] is not False or ai["effective_disposition_activated"] is not False:
            raise ValueError("original AI-only/image history mismatch")
        for name, expected in pair["required_assets_sha256"].items():
            copied, source = Path(preflight["main_root"]) / name, packet_path.parent / Path(name).name
            if copied.is_symlink() or source.is_symlink() or not copied.resolve().is_relative_to(Path(preflight["main_root"])) or _sha256(copied) != expected or _sha256(source) != expected or packet["image_sha256"][Path(name).name] != expected:
                raise ValueError("original/copied bound asset drift")
    return queue_paths


def import_review(args: argparse.Namespace) -> dict:
    private_output(args.out_root, [args.preflight, args.human_input])
    preflight = strict_json(stable_read(args.preflight)[0])
    private_output(args.out_root, [Path(name) for name in preflight["protected_snapshots"]])
    verify_authority(preflight)
    for name, digest in AUTHORITY_BINDINGS.items():
        if _sha256(ROOT / name) != digest:
            raise ValueError("committed import authority/source drift")
    criteria = (ROOT / CRITERIA_DOCUMENT).read_text().split("## Prospective Criteria\n", 1)[1].split("\n## Execution", 1)[0]
    if criteria != preflight["prospective_criteria_text"] or hashlib.sha256(criteria.encode()).hexdigest() != CRITERIA_SHA256 or _sha256(Path(__file__)) != preflight["import_code_sha256"] or str(args.human_input) != preflight["input_path"]:
        raise ValueError("criteria/code/existing input path drift")
    report = strict_json((ROOT / DIAGNOSTIC_REPORT).read_bytes())
    verify_context(preflight, report)
    verify_preservation(preflight)
    payload, identity = stable_read(args.human_input, preflight["input_identity"])
    if len(payload) != 6710 or hashlib.sha256(payload).hexdigest() != INPUT_SHA256:
        raise ValueError("exact existing raw bytes required")
    handoff_report = strict_json((ROOT / diagnostic.HANDOFF_REPORT).read_bytes())
    definition_payload, _ = stable_read(Path(preflight["main_root"]) / "review_definition.json")
    digest = hashlib.sha256(definition_payload).hexdigest()
    if digest != handoff_report["review_definition_sha256"]:
        raise ValueError("accepted227 definition drift")
    definition = strict_json(definition_payload)
    queue_paths = verify_sources(definition, preflight)
    human, outcomes = validate_input(payload, definition, digest)
    write_immutable_record(args.out_root / "human_input.json", human)
    lineage = {"version": 1, "review230_sha256": REVIEW_SHA256, "review228_sha256": diagnostic.REVIEW_SHA256,
               "public_authority_sha256": AUTHORITY_BINDINGS, "review_definition_sha256": digest,
               "original229_private_evidence_sha256": {field: report[field] for field in ("private_preflight_sha256", "private_diagnostic_main_sha256", "private_diagnostic_sibling_sha256", "private_owner_confirmation_sha256", "private_verification_sha256")},
               "raw_human_input_sha256": INPUT_SHA256, "raw_human_input_byte_size": 6710,
               "canonical_human_input_sha256": _sha256(args.out_root / "human_input.json"), "preflight_sha256": _sha256(args.preflight),
               "source229_CI": preflight["source229_CI"], "import_code_sha256": _sha256(Path(__file__)),
               "import_authority": "Review230_prospective_use_of_existing_self_attested_input_strict_import_only",
               "structured_copy_is_not_original_raw_bytes": True, "original_owner_bytes_preserved_in_place": True,
               "owner_authorship_and_prior_functional_checks_attested_not_independently_verified": True,
               "retrospective_collection_authority": False, "original227_failed_criterion_rewritten": False,
               "checkpoint_review_pending": True, "semantic_acceptance_pending": True, "activation_authorized": False, "scientific_readiness": False}
    write_immutable_record(args.out_root / "lineage.json", lineage)
    for row in outcomes:
        write_immutable_record(args.out_root / "pairs" / f"{row['queue_rank']:06d}.json", row)
    verify_preservation(preflight)
    after, _ = stable_read(args.human_input, identity)
    if after != payload or bundle(queue_paths) != strict_json((ROOT / "results/phase1/oulu-lineage-exact-evidence-v1.json").read_bytes())["pair_record_bundle_sha256"]:
        raise ValueError("raw input or full queue changed during import")
    result = {"version": 1, "status": "categorical_human_decisions_imported_pending_review_no_activation", "queue_ranks": list(range(80, 85)),
              "human_categorical_reviews": len(outcomes), "disposition_counts": dict(Counter(row["validated_disposition"] for row in outcomes)),
              "AI_proposed_disposition_counts": dict(Counter(row["ai_disposition"] for row in outcomes)),
              "new_agreements_with_AI": sum(not row["disagreement_with_AI"] for row in outcomes),
              "new_disagreements_with_AI": sum(row["disagreement_with_AI"] for row in outcomes),
              "new_uncertainties": sum(row["validated_disposition"] == "uncertain_insufficient_evidence" for row in outcomes),
              "new_unresolved_reconciliations": sum(row["reconciliation_required"] for row in outcomes),
              "reconciliation_required_ranks": [row["queue_rank"] for row in outcomes if row["reconciliation_required"]],
              "comparison_disposition_counts": dict(Counter(row["comparison_disposition"] for row in outcomes)),
              "comparison_states_are_not_activated_dispositions": True,
              "stop_for_prospective_scientific_decision": any(row["scientific_stop_independently_derived"] for row in outcomes),
              "dispositions_row_and_aggregate_stops_independently_rederived": True, "reported_outcomes_and_stops_all_match": True,
              "historical_disagreements": 1, "historical_unresolved_reconciliations": 0, "effective_dispositions_activated": 0,
              "accepted_current_total": 80, "accepted_semantic_owner_outcomes_total": 80, "accepted_AI_screen_coverage": 85,
              "highest_risk_remaining_unreviewed": 0, "batch09_closed": False, "semantic_acceptance_pending": True, "checkpoint_review_pending": True,
              "raw_human_input_sha256": INPUT_SHA256, "canonical_human_input_sha256": lineage["canonical_human_input_sha256"],
              "lineage_sha256": _sha256(args.out_root / "lineage.json"), "pair_record_bundle_sha256": bundle(sorted((args.out_root / "pairs").glob("*.json"))),
              "all_supplied_owner_fields_preserved": True, "original_owner_bytes_unchanged": True, "human_prose_required_or_generated": False,
              "historical_pending_review_flags_unchanged": True, "human_authorship": "owner_attested_not_independently_authenticated",
              "retrospective_collection_authority": False, "original227_failed_criterion_rewritten": False,
              "queue_continued": False, "activation_authorized": False, "model_execution_authorized": False, "scientific_readiness": False}
    write_immutable_record(args.out_root / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("preflight", "human-input", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        print(json.dumps(import_review(parser.parse_args()), sort_keys=True), flush=True)
    except OutcomeDiscrepancy as error:
        print(json.dumps({"error": "reported_outcome_or_stop_mismatch_no_import", "scientific_stop_required": error.scientific_stop_required}), file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        print("BATCH09 CATEGORICAL IMPORT REFUSED: no semantic acceptance or activation", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())