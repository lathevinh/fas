#!/usr/bin/env python3
"""Import bound categorical decisions without semantic acceptance or activation."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.oulu import _sha256

from prepare_oulu_categorical_batch05 import CATEGORICAL_RULES, TARGET_RANKS
from prepare_oulu_owner_review import private_output


def validate_categorical(record: dict, definition: dict) -> list[dict]:
    if type(record.get("version")) is not int or record["version"] != 1 or record.get("record_type") != "batch05_targeted_categorical_review":
        raise ValueError("categorical batch05 version/type required")
    reviewer = record.get("reviewer")
    if not isinstance(reviewer, dict) or reviewer.get("kind") not in {"owner_human", "designated_human"} or not isinstance(reviewer.get("id"), str) or not reviewer["id"].strip() or reviewer.get("personally_inspected_bound_evidence") is not True:
        raise ValueError("identified actual human and personal-inspection attestation required")
    for field in ("review_definition_sha256", "governance_sha256", "review168_sha256"):
        expected = definition.get("sha256" if field == "review_definition_sha256" else field)
        if not expected or record.get(field) != expected:
            raise ValueError("categorical authority/definition binding mismatch")
    timestamp = record.get("reviewed_at_utc")
    if not isinstance(timestamp, str):
        raise ValueError("UTC review timestamp required")
    parsed = datetime.fromisoformat(timestamp)
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError("UTC review timestamp required")
    pairs = definition.get("pairs", [])
    if [pair.get("queue_rank") for pair in pairs] != list(TARGET_RANKS) or any(type(pair.get("queue_rank")) is not int for pair in pairs):
        raise ValueError("exact ordered six-rank definition required")
    if json.dumps(definition.get("categorical_rules"), sort_keys=True) != json.dumps(CATEGORICAL_RULES, sort_keys=True):
        raise ValueError("accepted strict categorical mapping required")
    rows = record.get("pairs")
    if not isinstance(rows, list) or len(rows) != 6 or any(not isinstance(row, dict) or type(row.get("queue_rank")) is not int for row in rows) or {row["queue_rank"] for row in rows} != set(TARGET_RANKS):
        raise ValueError("six unique integer target ranks required")
    expected_by_rank = {pair["queue_rank"]: pair for pair in pairs}
    outcomes = []
    for row in sorted(rows, key=lambda item: item["queue_rank"]):
        rank = row["queue_rank"]
        expected = expected_by_rank[rank]
        for field, target in (("packet_sha256", "packet_sha256"), ("imported_human_record_sha256", "imported_human_record_sha256"), ("reviewed_assets_sha256", "required_assets_sha256")):
            if not expected.get(target) or row.get(field) != expected[target]:
                raise ValueError("exact packet/asset/prior-human-row binding required")
        if row.get("personal_inspection_attested") is not True or row.get("owner_decision_attested") is not True or row.get("capture_provenance_certified") is not False:
            raise ValueError("truthful inspection/ownership and no capture certification required")
        if row.get("bound_images_identical_to_rank47") is not (rank == 48) or expected.get("bound_images_identical_to_rank47") is not (rank == 48):
            raise ValueError("rank48 identity binding mismatch")
        reference = row.get("identical_evidence_reference_rank")
        if "identical_evidence_reference_rank" not in row or (rank == 48 and (type(reference) is not int or reference != 47)) or (rank != 48 and reference is not None):
            raise ValueError("rank47 identity reference mismatch")
        if type(row.get("evidence_sufficient")) is not bool or "same_or_derived_content" not in row:
            raise ValueError("explicit categorical sufficiency and same/derived answer required")
        same = row["same_or_derived_content"]
        if (row["evidence_sufficient"] and type(same) is not bool) or (not row["evidence_sufficient"] and same is not None):
            raise ValueError("invalid sufficient/same-derived combination")
        disposition = next(rule["disposition"] for rule in CATEGORICAL_RULES if rule["evidence_sufficient"] is row["evidence_sufficient"] and rule["same_or_derived_content"] is same)
        stop = disposition == "confirmed_same_content_or_derived_lineage"
        if row.get("disposition") != disposition or type(row.get("stop_for_prospective_scientific_decision")) is not bool or row["stop_for_prospective_scientific_decision"] != stop:
            raise ValueError("exported disposition/stop must match categorical answers")
        ai = expected["ai_disposition"]
        prior = expected["prior_human_disposition"]
        if ai not in {rule["disposition"] for rule in CATEGORICAL_RULES} or prior not in {rule["disposition"] for rule in CATEGORICAL_RULES}:
            raise ValueError("bound prior dispositions required")
        disagreement = disposition != ai
        changed = disposition != prior
        derived = {"validated_disposition": disposition, "ai_disposition": ai, "prior_human_disposition": prior,
                   "disagreement_with_AI": disagreement, "disposition_changed_from_prior_human": changed,
                   "reconciliation_required": disagreement or changed,
                   "comparison_disposition": "uncertain_insufficient_evidence" if disagreement or changed else disposition,
                   "semantic_acceptance_pending": True, "effective_disposition_activated": False,
                   "counts_as_accepted_current_effective_disposition": False, "model_execution_authorized": False, "scientific_readiness": False}
        if row.keys() & derived.keys():
            raise ValueError("human input collides with importer metadata")
        outcomes.append({**row, **derived})
    stop = any(row["stop_for_prospective_scientific_decision"] for row in outcomes)
    if type(record.get("stop_for_prospective_scientific_decision")) is not bool or record["stop_for_prospective_scientific_decision"] != stop:
        raise ValueError("aggregate scientific stop mismatch")
    return outcomes


def import_review(args: argparse.Namespace) -> dict:
    preflight_path = args.review_root.parent / "oulu_batch05_categorical_import_preflight_v1.json"
    private_output(args.out_root, [args.review_root, args.human_input, preflight_path])
    preflight = json.loads(preflight_path.read_bytes())
    private_output(args.out_root, [Path(name) for name in preflight["protected_snapshots"]])

    def verify_inputs() -> None:
        for name, expected in preflight["protected_snapshots"].items():
            folder = Path(name)
            actual = {str(path.relative_to(folder)): _sha256(path) for path in sorted(folder.rglob("*")) if path.is_file()}
            if actual != expected:
                raise ValueError("protected evidence drift")
        for name, digest in {**preflight["pinned_file_sha256"], **preflight["frozen_file_sha256"], **preflight["study_config_sha256"]}.items():
            if _sha256(Path(name)) != digest:
                raise ValueError("authority/source/config drift")
        if _sha256(Path(__file__)) != preflight["import_code_sha256"]:
            raise ValueError("categorical import implementation drift")

    verify_inputs()
    check = preflight["handoff169_CI"]
    if check["head_sha"] != "de9ab7fcd15bb5772ba1a63b67f3946a08bf1f95" or check["run_id"] != 38555628657 or check["job_id"] != 115823926504 or check["status"] != "completed" or check["conclusion"] != "success":
        raise ValueError("exact successful categorical handoff CI required")
    if preflight["import_authority"] != "Review170_accepted169_owner_supplied_new_categorical_JSON_import_only" or preflight["activation_authorized"] is not False:
        raise ValueError("Review170 and owner-supplied input authority required; no activation")
    review_path = ROOT / "docs/170-review-doc169-oulu-batch05-categorical-handoff.md"
    public_path = ROOT / "results/phase1/oulu-categorical-handoff-batch05-v1.json"
    if _sha256(review_path) != preflight["review170_sha256"] or _sha256(public_path) != preflight["handoff169_report_sha256"]:
        raise ValueError("accepted handoff/Review170 drift")
    public = json.loads(public_path.read_bytes())
    definition_path = args.review_root / "review_definition.json"
    digest = _sha256(definition_path)
    if digest != public["review_definition_sha256"] or _sha256(args.review_root / "index.html") != public["page_sha256"] or _sha256(args.review_root / "summary.json") != public["private_summary_sha256"]:
        raise ValueError("accepted categorical form drift")
    if str(args.review_root.resolve()) != preflight["review_root"] or args.human_input.resolve() != (args.review_root / "oulu-batch05-categorical-review.json").resolve() or _sha256(args.human_input) != preflight["human_input_sha256"]:
        raise ValueError("exact new categorical owner source required")
    definition = json.loads(definition_path.read_bytes())
    governance_path = args.review_root.parent / "oulu_batch05_governance_clarification_v1.json"
    if _sha256(governance_path) != definition["governance_sha256"] or _sha256(ROOT / "docs/168-review-doc167-oulu-batch05-clarification-handoff.md") != definition["review168_sha256"]:
        raise ValueError("categorical governance/Review168 binding drift")
    original_import = Path(definition["original_import_root"])
    rows = sorted((original_import / "pairs").glob("*.json"))
    bundle = hashlib.sha256("".join(f"{path.name}:{_sha256(path)}\n" for path in rows).encode()).hexdigest()
    if len(rows) != 10 or bundle != definition["human_record_bundle_sha256"]:
        raise ValueError("original ten human records drift")
    old_definition = json.loads((Path(definition["source_review_root"]) / "review_definition.json").read_bytes())
    original = json.loads((Path(old_definition["previous_review_root"]) / "review_definition.json").read_bytes())
    validated_pairs = []
    for pair in definition["pairs"]:
        rank = pair["queue_rank"]
        row_path = original_import / "pairs" / f"{rank:06d}.json"
        row = json.loads(row_path.read_bytes())
        if _sha256(row_path) != pair["imported_human_record_sha256"] or row["queue_rank"] != rank or row["packet_sha256"] != pair["packet_sha256"] or row["reviewed_assets_sha256"] != pair["required_assets_sha256"] or row["effective_disposition_activated"] is not False:
            raise ValueError("prior human binding drift")
        packet_path = Path(original["packet_root"]) / "pairs" / f"{rank:06d}" / "packet.json"
        ai_path = Path(original["ai_review_root"]) / "pairs" / f"{rank:06d}.json"
        packet = json.loads(packet_path.read_bytes())
        ai = json.loads(ai_path.read_bytes())
        if _sha256(packet_path) != pair["packet_sha256"] or _sha256(ai_path) != pair["ai_record_sha256"] or packet["candidate"] != ai["candidate"] or ai["proposed_disposition"] != pair["ai_disposition"]:
            raise ValueError("bound packet/AI drift")
        if len(pair["required_assets_sha256"]) != 3 or {Path(name).name for name in pair["required_assets_sha256"]} != {"temporal_a.png", "temporal_b.png", "trigger.png"}:
            raise ValueError("three accepted images required")
        for name, expected in pair["required_assets_sha256"].items():
            asset = (args.review_root / name).resolve()
            if not asset.is_relative_to(args.review_root.resolve()) or _sha256(asset) != expected or packet["image_sha256"][Path(name).name] != expected:
                raise ValueError("exact reviewed asset drift")
        if rank == 48 and {Path(name).name: value for name, value in pair["required_assets_sha256"].items()} != {Path(name).name: value for name, value in original["pairs"][7]["required_assets_sha256"].items()}:
            raise ValueError("rank48/47 identity drift")
        validated_pairs.append({**pair, "prior_human_disposition": row["disposition"]})
    human = json.loads(args.human_input.read_bytes())
    outcomes = validate_categorical(human, {**definition, "sha256": digest, "pairs": validated_pairs})
    lineage = {"version": 1, "review170_sha256": _sha256(review_path), "handoff169_report_sha256": _sha256(public_path),
               "review_definition_sha256": digest, "page_sha256": public["page_sha256"], "governance_sha256": definition["governance_sha256"],
               "human_input_sha256": _sha256(args.human_input), "preflight_sha256": _sha256(preflight_path), "handoff169_CI": check,
               "import_code_sha256": _sha256(Path(__file__)), "original_human_record_bundle_sha256": bundle,
               "import_authority": preflight["import_authority"], "formal_review170_present_before_import": True,
               "no_automatic_effective_activation": True, "scientific_readiness": False}
    write_immutable_record(args.out_root / "lineage.json", lineage)
    write_immutable_record(args.out_root / "human_input.json", human)
    for row in outcomes:
        write_immutable_record(args.out_root / "pairs" / f"{row['queue_rank']:06d}.json", row)
    verify_inputs()
    if _sha256(args.human_input) != preflight["human_input_sha256"]:
        raise ValueError("owner input changed during import")
    result = {"version": 1, "status": "categorical_human_decisions_imported_no_semantic_acceptance_or_activation", "queue_ranks": list(TARGET_RANKS),
              "human_categorical_reviews": len(outcomes), "disposition_counts": dict(Counter(row["disposition"] for row in outcomes)),
              "disagreements_with_AI": sum(row["disagreement_with_AI"] for row in outcomes),
              "disposition_changes_from_prior_human": sum(row["disposition_changed_from_prior_human"] for row in outcomes),
              "reconciliation_required_ranks": [row["queue_rank"] for row in outcomes if row["reconciliation_required"]],
              "comparison_disposition_counts": dict(Counter(row["comparison_disposition"] for row in outcomes)),
              "comparison_states_are_not_activated_dispositions": True, "stop_for_prospective_scientific_decision": any(row["stop_for_prospective_scientific_decision"] for row in outcomes),
              "effective_dispositions_activated": 0, "accepted_current_total": 40, "batch05_closed": False, "semantic_acceptance_pending": True,
              "human_input_sha256": preflight["human_input_sha256"], "review_definition_sha256": digest,
              "lineage_sha256": _sha256(args.out_root / "lineage.json"), "human_authorship": "categorical_choices_and_inspection_attested_not_independently_authenticated",
              "human_prose_required_or_generated": False, "machine_narrative_generated": False, "old167_input_imported_or_converted": False,
              "original_ten_human_records_unchanged": True, "historical_pending_review_flags_unchanged": True,
              "queue_continued": False, "model_execution_authorized": False, "scientific_readiness": False}
    write_immutable_record(args.out_root / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("review-root", "human-input", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        print(json.dumps(import_review(parser.parse_args()), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError):
        print("CATEGORICAL IMPORT FAILED: no semantic acceptance or activation", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())