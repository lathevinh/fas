#!/usr/bin/env python3
"""Import Review212-authorized categorical answers without effective activation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.oulu import _sha256
from prepare_oulu_categorical_batch08 import AI_REPORT_FILE, AI_REPORT_SHA256, CATEGORICAL_RULES, FORMAL_REPORT_FILE, FORMAL_REPORT_SHA256, REVIEW_FILE, REVIEW_SHA256, TARGET_RANKS, is_digest
from prepare_oulu_owner_review import private_output
from prepare_oulu_visual_batch05 import bundle
from recover_oulu_archive_identity import verify_preserved

REVIEW212_FILE = "docs/212-review-doc211-oulu-batch08-owner-export-receipt.md"
REVIEW212_SHA256 = "e64484d0ef0f4a1fab48b8c2a7580f45097b2743bdac39e654726cad37779781"
REVIEW210_FILE = "docs/210-review-doc209-oulu-batch08-categorical-handoff.md"
REVIEW210_SHA256 = "129e87260c506d389d1e54fb770b4ac21fd05d321ccd32b0df260f6b9b4c5458"
HANDOFF_REPORT = "results/phase1/oulu-categorical-handoff-batch08-v1.json"
RECEIPT_REPORT = "results/phase1/oulu-batch08-owner-export-receipt-v1.json"
IMPORT_AUTHORITY = "Review212_accepts211_separate_categorical_import_only"
AUTHORITY_BINDINGS = {
    REVIEW_FILE: REVIEW_SHA256, REVIEW210_FILE: REVIEW210_SHA256, REVIEW212_FILE: REVIEW212_SHA256,
    AI_REPORT_FILE: AI_REPORT_SHA256, FORMAL_REPORT_FILE: FORMAL_REPORT_SHA256,
    HANDOFF_REPORT: "a923c15643429778b6db6947fd7367530ad03194561790913a0c75768d7dadc0",
    RECEIPT_REPORT: "a394a05c412ffe37f38c9951d5aa2063987b17a806a24fc82bdab676aa315380",
}


def strict_json(payload: bytes | str) -> dict:
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError("nonfinite JSON value")

    def finite_float(value):
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ValueError("nonfinite JSON number")
        return parsed

    result = json.loads(payload, object_pairs_hook=unique_pairs, parse_constant=reject_constant, parse_float=finite_float)
    if type(result) is not dict:
        raise ValueError("JSON object required")
    return result


def read_receipted_input(path: Path, digest: str, size: int) -> dict:
    if path.is_symlink() or not is_digest(digest) or type(size) is not int or size <= 0:
        raise ValueError("regular receipted owner file required")
    payload = path.read_bytes()
    if len(payload) != size or hashlib.sha256(payload).hexdigest() != digest:
        raise ValueError("raw receipt size/hash mismatch before parsing")
    return strict_json(payload)


def validate_categorical(record: dict, definition: dict) -> list[dict]:
    if type(record) is not dict or type(definition) is not dict or type(record.get("version")) is not int or record["version"] != 1 or record.get("record_type") != "batch08_categorical_review":
        raise ValueError("categorical batch08 object/version/type required")
    reviewer = record.get("reviewer")
    if type(reviewer) is not dict or type(reviewer.get("kind")) is not str or reviewer["kind"] not in {"owner_human", "designated_human"} or type(reviewer.get("id")) is not str or not reviewer["id"].strip() or reviewer.get("personally_inspected_bound_evidence") is not True:
        raise ValueError("identified human and personal-inspection attestation required")
    authority = {"review208_sha256": REVIEW_SHA256, "accepted_AI_report_sha256": AI_REPORT_SHA256, "accepted_formal_report_sha256": FORMAL_REPORT_SHA256}
    if not is_digest(definition.get("sha256")) or any(definition.get(field) != value or record.get(field) != value for field, value in authority.items()) or record.get("review_definition_sha256") != definition["sha256"]:
        raise ValueError("exact definition/Review208/original203/formal207 binding required")
    timestamp = record.get("reviewed_at_utc")
    if type(timestamp) is not str:
        raise ValueError("UTC review timestamp required")
    parsed = datetime.fromisoformat(timestamp)
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError("UTC review timestamp required")
    pairs = definition.get("pairs")
    if type(pairs) is not list or any(type(pair) is not dict or type(pair.get("queue_rank")) is not int for pair in pairs) or [pair["queue_rank"] for pair in pairs] != list(TARGET_RANKS):
        raise ValueError("exact ordered integer ranks70..79 definition required")
    if json.dumps(definition.get("categorical_rules"), sort_keys=True) != json.dumps(CATEGORICAL_RULES, sort_keys=True):
        raise ValueError("strict categorical mapping required")
    rows = record.get("pairs")
    if type(rows) is not list or len(rows) != 10 or any(type(row) is not dict or type(row.get("queue_rank")) is not int for row in rows) or {row["queue_rank"] for row in rows} != set(TARGET_RANKS):
        raise ValueError("ten unique integer ranks70..79 required")
    expected_by_rank = {pair["queue_rank"]: pair for pair in pairs}
    outcomes = []
    for row in sorted(rows, key=lambda item: item["queue_rank"]):
        expected = expected_by_rank[row["queue_rank"]]
        for field in ("packet_sha256", "ai_record_sha256", "formal_review_record_sha256", "exact_pair_record_sha256"):
            if not is_digest(expected.get(field)) or row.get(field) != expected[field]:
                raise ValueError("exact packet/AI/formal/queue row binding required")
        assets = expected.get("required_assets_sha256")
        names = {f"assets/{row['queue_rank']:06d}/{name}.png" for name in ("temporal_a", "temporal_b", "trigger")}
        if type(assets) is not dict or set(assets) != names or any(not is_digest(value) for value in assets.values()) or row.get("reviewed_assets_sha256") != assets:
            raise ValueError("exact three reviewed assets required")
        if row.get("personal_inspection_attested") is not True or row.get("owner_decision_attested") is not True or row.get("capture_provenance_certified") is not False:
            raise ValueError("both attestations and no capture certification required")
        sufficient = row.get("evidence_sufficient")
        if type(sufficient) is not bool or "same_or_derived_content" not in row:
            raise ValueError("explicit boolean sufficiency and same/derived required")
        same = row["same_or_derived_content"]
        if (sufficient and type(same) is not bool) or (not sufficient and same is not None):
            raise ValueError("strict boolean/null categorical combination required")
        disposition = next(rule["disposition"] for rule in CATEGORICAL_RULES if rule["evidence_sufficient"] is sufficient and rule["same_or_derived_content"] is same)
        stop = disposition == "confirmed_same_content_or_derived_lineage"
        if row.get("disposition") != disposition or type(row.get("stop_for_prospective_scientific_decision")) is not bool or row["stop_for_prospective_scientific_decision"] != stop:
            raise ValueError("reported outcome/stop contradicts independently derived answers")
        ai = expected.get("ai_disposition")
        if type(ai) is not str or ai not in {rule["disposition"] for rule in CATEGORICAL_RULES}:
            raise ValueError("bound original AI proposal required")
        disagreement = disposition != ai
        derived = {"validated_disposition": disposition, "ai_disposition": ai, "disagreement_with_AI": disagreement,
                   "reconciliation_required": disagreement, "comparison_disposition": "uncertain_insufficient_evidence" if disagreement else disposition,
                   "scientific_stop_independently_derived": stop, "checkpoint_review_pending": True, "semantic_acceptance_pending": True,
                   "effective_disposition_activated": False, "counts_as_accepted_current_effective_disposition": False,
                   "model_execution_authorized": False, "scientific_readiness": False}
        if row.keys() & derived.keys():
            raise ValueError("owner fields collide with importer metadata")
        outcomes.append({**row, **derived})
    stop = any(row["scientific_stop_independently_derived"] for row in outcomes)
    if type(record.get("stop_for_prospective_scientific_decision")) is not bool or record["stop_for_prospective_scientific_decision"] != stop:
        raise ValueError("reported aggregate scientific stop mismatch")
    return outcomes


def verify_authority(preflight: dict) -> None:
    expected = {"checkpoint": 213, "review212_sha256": REVIEW212_SHA256, "review210_sha256": REVIEW210_SHA256, "import_authority": IMPORT_AUTHORITY,
                "import_authorized": True, "activation_authorized": False, "effective_activation_authorized": False, "model_execution_authorized": False, "scientific_readiness": False}
    if any(type(preflight.get(field)) is not type(value) or preflight[field] != value for field, value in expected.items()):
        raise ValueError("Review212 import-only authority required")
    ranks = preflight.get("queue_ranks")
    if type(ranks) is not list or ranks != list(TARGET_RANKS) or any(type(rank) is not int for rank in ranks):
        raise ValueError("exact integer ranks70..79 authority required")
    check = preflight.get("source211_CI")
    expected_ci = {"head_sha": "9c01c585e52045462499a18361d6a930571dd059", "run_id": 39347602537, "job_id": 118383870057,
                   "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success"}
    if type(check) is not dict or any(type(check.get(field)) is not type(value) or check[field] != value for field, value in expected_ci.items()):
        raise ValueError("exact successful211 receipt CI required")


def verify_preservation(preflight: dict) -> None:
    def check_root(item):
        name, expected = item
        verify_preserved({"protected_snapshots": {name: expected}, "pinned_file_sha256": {}, "frozen_file_sha256": {}, "study_config_sha256": {}})

    with ThreadPoolExecutor(max_workers=4) as workers:
        list(workers.map(check_root, preflight["protected_snapshots"].items()))
    verify_preserved({**preflight, "protected_snapshots": {}})


def import_review(args: argparse.Namespace) -> dict:
    private_output(args.out_root, [args.preflight, args.review_root, args.human_input])
    preflight = strict_json(args.preflight.read_bytes())
    private_output(args.out_root, [Path(name) for name in preflight["protected_snapshots"]])
    verify_authority(preflight)
    for name, digest in AUTHORITY_BINDINGS.items():
        if _sha256(ROOT / name) != digest:
            raise ValueError("accepted public authority drift")
    if _sha256(Path(__file__)) != preflight["import_code_sha256"] or str(args.review_root.resolve()) != preflight["review_root"] or args.human_input.resolve() != (args.review_root / "oulu-batch08-categorical-review.json").resolve():
        raise ValueError("import code or owner input path drift")
    receipt_public = strict_json((ROOT / RECEIPT_REPORT).read_bytes())
    for field, public_field in (("receipt211_preflight_path", "private_preflight_sha256"), ("receipt211_path", "private_receipt_sha256")):
        if _sha256(Path(preflight[field])) != receipt_public[public_field]:
            raise ValueError("accepted211 private receipt drift")
    receipt_preflight = strict_json(Path(preflight["receipt211_preflight_path"]).read_bytes())
    receipt = strict_json(Path(preflight["receipt211_path"]).read_bytes())
    for field in ("protected_snapshots", "frozen_file_sha256", "study_config_sha256"):
        if preflight[field] != receipt_preflight[field]:
            raise ValueError("accepted preservation set drift")
    if receipt["raw_export_sha256"] != receipt_public["raw_export_sha256"] or receipt["raw_export_byte_size"] != receipt_public["raw_export_byte_size"] or receipt["raw_export_path"] != str(args.human_input.resolve()):
        raise ValueError("exact211 raw receipt binding required")
    public = strict_json((ROOT / HANDOFF_REPORT).read_bytes())
    correction = strict_json(Path(preflight["metadata_correction_path"]).read_bytes())
    if _sha256(Path(preflight["metadata_correction_path"])) != public["private_metadata_correction_sha256"] or correction["original_preflight_sha256"] != _sha256(Path(preflight["handoff209_preflight_path"])) or correction["original_verification_sha256"] != _sha256(Path(preflight["handoff209_verification_path"])) or correction["corrected_value"] != public["added_test_method"] or correction["corrected_value"] != "test_batch08_categorical_handoff_acceptance_authority_and_blank_controls":
        raise ValueError("accepted209 additive correction binding required")
    verify_preservation(preflight)
    human = read_receipted_input(args.human_input, receipt_public["raw_export_sha256"], receipt_public["raw_export_byte_size"])
    definition_path = args.review_root / "review_definition.json"
    digest = _sha256(definition_path)
    if digest != public["review_definition_sha256"] or _sha256(args.review_root / "index.html") != public["page_sha256"] or _sha256(args.review_root / "summary.json") != public["private_summary_sha256"]:
        raise ValueError("accepted209 definition/form drift")
    definition = strict_json(definition_path.read_bytes())
    outcomes = validate_categorical(human, {**definition, "sha256": digest})
    ai_root, formal_root = Path(definition["ai_root"]), Path(definition["formal_root"])
    ai_public, formal_public = strict_json((ROOT / AI_REPORT_FILE).read_bytes()), strict_json((ROOT / FORMAL_REPORT_FILE).read_bytes())
    for name, field in (("definition.json", "private_definition_sha256"), ("ledger.json", "private_ledger_sha256"), ("summary.json", "private_summary_sha256")):
        if _sha256(ai_root / name) != ai_public[field]:
            raise ValueError("original203 AI root drift")
    for name, field in (("definition.json", "formal207_definition"), ("ledger.json", "formal207_ledger"), ("summary.json", "formal207_summary")):
        if _sha256(formal_root / name) != formal_public["evidence_sha256"][field]:
            raise ValueError("accepted207 formal root drift")
    ai_paths, formal_paths = sorted((ai_root / "pairs").glob("*.json")), sorted((formal_root / "pairs").glob("*.json"))
    names = [f"{rank:06d}.json" for rank in TARGET_RANKS]
    if [path.name for path in ai_paths] != names or bundle(ai_paths) != ai_public["pair_record_bundle_sha256"] or [path.name for path in formal_paths] != names or bundle(formal_paths) != formal_public["evidence_sha256"]["formal207_row_bundle"]:
        raise ValueError("exact original AI/formal ten-row bundles required")
    queue_root = Path(preflight["queue_root"])
    queue_public = strict_json((ROOT / "results/phase1/oulu-lineage-exact-evidence-v1.json").read_bytes())
    queue_paths = sorted((queue_root / "pairs").glob("*.json"))
    if len(queue_paths) != 6640 or bundle(queue_paths) != queue_public["pair_record_bundle_sha256"] or _sha256(queue_root / "summary.json") != queue_public["private_summary_sha256"]:
        raise ValueError("accepted complete frozen queue drift")
    for pair in definition["pairs"]:
        rank = pair["queue_rank"]
        packet_path = Path(definition["packet_root"]) / "pairs" / f"{rank:06d}" / "packet.json"
        ai_path, formal_path = ai_root / "pairs" / f"{rank:06d}.json", formal_root / "pairs" / f"{rank:06d}.json"
        packet, ai, formal, queue = [strict_json(path.read_bytes()) for path in (packet_path, ai_path, formal_path, queue_paths[rank])]
        for path, field in ((packet_path, "packet_sha256"), (ai_path, "ai_record_sha256"), (formal_path, "formal_review_record_sha256"), (queue_paths[rank], "exact_pair_record_sha256")):
            if _sha256(path) != pair[field]:
                raise ValueError("original packet/AI/formal/queue record drift")
        if any(type(source["queue_rank"]) is not int or source["queue_rank"] != rank for source in (packet, ai, formal, queue)) or queue["candidate"] != packet["candidate"] or packet["candidate"] != ai["candidate"] or ai["proposed_disposition"] != pair["ai_disposition"]:
            raise ValueError("exact source candidate/rank/AI proposal mismatch")
        if ai["packet_sha256"] != pair["packet_sha256"] or ai["exact_pair_record_sha256"] != pair["exact_pair_record_sha256"] or packet["exact_pair_record_sha256"] != pair["exact_pair_record_sha256"] or formal["original203_pair_record_sha256"] != pair["ai_record_sha256"] or formal["packet_sha256"] != pair["packet_sha256"]:
            raise ValueError("exact original203/formal207 provenance mismatch")
        if ai["assets_actually_viewed_sha256"] != packet["image_sha256"] or formal["assets_actually_viewed_sha256"] != packet["image_sha256"] or ai["human_review_performed"] is not False or ai["effective_disposition_activated"] is not False:
            raise ValueError("original AI-only history and reviewed image bindings required")
        for name, expected in pair["required_assets_sha256"].items():
            asset, original = args.review_root / name, packet_path.parent / Path(name).name
            if asset.is_symlink() or original.is_symlink() or not asset.resolve().is_relative_to(args.review_root.resolve()) or _sha256(asset) != expected or _sha256(original) != expected or packet["image_sha256"][Path(name).name] != expected:
                raise ValueError("actual reviewed image drift")
    write_immutable_record(args.out_root / "human_input.json", human)
    lineage = {"version": 1, "review212_sha256": REVIEW212_SHA256, "review210_sha256": REVIEW210_SHA256, "review208_sha256": REVIEW_SHA256,
               "public_authority_sha256": AUTHORITY_BINDINGS, "review_definition_sha256": digest,
               "receipt211_preflight_sha256": receipt_public["private_preflight_sha256"], "receipt211_sha256": receipt_public["private_receipt_sha256"],
               "metadata_correction_sha256": public["private_metadata_correction_sha256"], "raw_human_input_sha256": receipt_public["raw_export_sha256"],
               "raw_human_input_byte_size": receipt_public["raw_export_byte_size"], "canonical_human_input_sha256": _sha256(args.out_root / "human_input.json"),
               "preflight_sha256": _sha256(args.preflight), "source211_CI": preflight["source211_CI"], "import_code_sha256": _sha256(Path(__file__)),
               "import_authority": IMPORT_AUTHORITY, "original_owner_bytes_preserved_in_place": True, "structured_copy_is_not_original_raw_bytes": True,
               "owner_authorship_and_prior_functional_checks_attested_not_independently_verified": True,
               "checkpoint_review_pending": True, "activation_authorized": False, "scientific_readiness": False}
    write_immutable_record(args.out_root / "lineage.json", lineage)
    for row in outcomes:
        write_immutable_record(args.out_root / "pairs" / f"{row['queue_rank']:06d}.json", row)
    verify_preservation(preflight)
    if _sha256(args.human_input) != receipt_public["raw_export_sha256"] or args.human_input.stat().st_size != receipt_public["raw_export_byte_size"] or bundle(queue_paths) != queue_public["pair_record_bundle_sha256"]:
        raise ValueError("owner raw input or queue changed during import")
    result = {"version": 1, "status": "categorical_human_decisions_imported_pending_review_no_activation", "queue_ranks": list(TARGET_RANKS),
              "human_categorical_reviews": len(outcomes), "disposition_counts": dict(Counter(row["validated_disposition"] for row in outcomes)),
              "AI_proposed_disposition_counts": dict(Counter(row["ai_disposition"] for row in outcomes)),
              "new_agreements_with_AI": sum(not row["disagreement_with_AI"] for row in outcomes),
              "new_disagreements_with_AI": sum(row["disagreement_with_AI"] for row in outcomes),
              "new_uncertainties": sum(row["validated_disposition"] == "uncertain_insufficient_evidence" for row in outcomes),
              "reconciliation_required_ranks": [row["queue_rank"] for row in outcomes if row["reconciliation_required"]],
              "comparison_disposition_counts": dict(Counter(row["comparison_disposition"] for row in outcomes)),
              "comparison_states_are_not_activated_dispositions": True, "stop_for_prospective_scientific_decision": any(row["scientific_stop_independently_derived"] for row in outcomes),
              "dispositions_and_row_and_aggregate_stops_independently_rederived": True, "reported_outcomes_and_stops_all_match": True,
              "historical_disagreements": 1, "historical_unresolved_reconciliations": 0, "effective_dispositions_activated": 0,
              "accepted_current_total": 70, "accepted_AI_screen_coverage": 80, "remaining_unviewed": 5, "batch08_closed": False,
              "semantic_acceptance_pending": True, "checkpoint_review_pending": True, "raw_human_input_sha256": receipt_public["raw_export_sha256"],
              "canonical_human_input_sha256": lineage["canonical_human_input_sha256"], "lineage_sha256": _sha256(args.out_root / "lineage.json"),
              "pair_record_bundle_sha256": bundle(sorted((args.out_root / "pairs").glob("*.json"))), "all_supplied_owner_fields_preserved": True,
              "original_owner_bytes_unchanged": True, "human_prose_required_or_generated": False, "machine_narrative_generated": False,
              "historical_pending_review_flags_unchanged": True, "human_authorship": "owner_attested_not_independently_authenticated",
              "queue_continued": False, "activation_authorized": False, "model_execution_authorized": False, "scientific_readiness": False}
    write_immutable_record(args.out_root / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("preflight", "review-root", "human-input", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        print(json.dumps(import_review(parser.parse_args()), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError):
        print("BATCH08 CATEGORICAL IMPORT FAILED: no semantic acceptance or activation", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())