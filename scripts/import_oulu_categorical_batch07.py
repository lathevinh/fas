#!/usr/bin/env python3
"""Import genuine batch07 categorical choices without acceptance or activation."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.oulu import _sha256
from prepare_oulu_categorical_batch07 import AI_REPORT_SHA256, CATEGORICAL_RULES, REVIEW_SHA256, TARGET_RANKS, is_digest
from prepare_oulu_owner_review import private_output
from prepare_oulu_visual_batch05 import bundle
from recover_oulu_archive_identity import verify_preserved

REVIEW_FILE = "docs/196-review-doc195-oulu-batch07-categorical-handoff.md"
REVIEW196_SHA256 = "7fb3b81d8e40482b8ec8557ac39eb22a1831c00c9c99f7aede703a7db1e0b210"
HANDOFF_REPORT = "results/phase1/oulu-categorical-handoff-batch07-v1.json"
IMPORT_AUTHORITY = "Review196_accepted195_genuine_owner_export_import_only"


def validate_categorical(record: dict, definition: dict) -> list[dict]:
    if type(record.get("version")) is not int or record["version"] != 1 or record.get("record_type") != "batch07_categorical_review":
        raise ValueError("categorical batch07 version/type required")
    reviewer = record.get("reviewer")
    if not isinstance(reviewer, dict) or reviewer.get("kind") not in {"owner_human", "designated_human"} or not isinstance(reviewer.get("id"), str) or not reviewer["id"].strip() or reviewer.get("personally_inspected_bound_evidence") is not True:
        raise ValueError("identified human and personal-inspection attestation required")
    if definition.get("review194_sha256") != REVIEW_SHA256 or definition.get("accepted_AI_report_sha256") != AI_REPORT_SHA256 or not is_digest(definition.get("sha256")):
        raise ValueError("accepted batch07 authority required")
    for field in ("review_definition_sha256", "review194_sha256", "accepted_AI_report_sha256"):
        if record.get(field) != definition["sha256" if field == "review_definition_sha256" else field]:
            raise ValueError("exact categorical authority/definition binding required")
    timestamp = record.get("reviewed_at_utc")
    if not isinstance(timestamp, str):
        raise ValueError("UTC review timestamp required")
    parsed = datetime.fromisoformat(timestamp)
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError("UTC review timestamp required")
    pairs = definition.get("pairs")
    if not isinstance(pairs, list) or any(not isinstance(pair, dict) for pair in pairs) or [pair.get("queue_rank") for pair in pairs] != list(TARGET_RANKS) or any(type(pair.get("queue_rank")) is not int for pair in pairs):
        raise ValueError("exact ordered ten-rank definition required")
    if json.dumps(definition.get("categorical_rules"), sort_keys=True) != json.dumps(CATEGORICAL_RULES, sort_keys=True):
        raise ValueError("strict categorical mapping required")
    rows = record.get("pairs")
    if not isinstance(rows, list) or len(rows) != 10 or any(not isinstance(row, dict) or type(row.get("queue_rank")) is not int for row in rows) or {row["queue_rank"] for row in rows} != set(TARGET_RANKS):
        raise ValueError("ten unique integer ranks60..69 required")
    expected_by_rank = {pair["queue_rank"]: pair for pair in pairs}
    outcomes = []
    for row in sorted(rows, key=lambda item: item["queue_rank"]):
        expected = expected_by_rank[row["queue_rank"]]
        for field in ("packet_sha256", "ai_record_sha256", "exact_pair_record_sha256"):
            if not is_digest(expected.get(field)) or row.get(field) != expected[field]:
                raise ValueError("exact packet/AI/queue binding required")
        assets = expected.get("required_assets_sha256")
        names = {f"assets/{row['queue_rank']:06d}/{name}.png" for name in ("temporal_a", "temporal_b", "trigger")}
        if not isinstance(assets, dict) or set(assets) != names or any(not is_digest(value) for value in assets.values()) or row.get("reviewed_assets_sha256") != assets:
            raise ValueError("exact three reviewed assets required")
        if row.get("personal_inspection_attested") is not True or row.get("owner_decision_attested") is not True or row.get("capture_provenance_certified") is not False:
            raise ValueError("inspection/own-decision attestations and no capture certification required")
        if type(row.get("evidence_sufficient")) is not bool or "same_or_derived_content" not in row:
            raise ValueError("explicit categorical sufficiency and same/derived required")
        same = row["same_or_derived_content"]
        if (row["evidence_sufficient"] and type(same) is not bool) or (not row["evidence_sufficient"] and same is not None):
            raise ValueError("strict boolean/null categorical combination required")
        disposition = next(rule["disposition"] for rule in CATEGORICAL_RULES if rule["evidence_sufficient"] is row["evidence_sufficient"] and rule["same_or_derived_content"] is same)
        stop = disposition == "confirmed_same_content_or_derived_lineage"
        if row.get("disposition") != disposition or type(row.get("stop_for_prospective_scientific_decision")) is not bool or row["stop_for_prospective_scientific_decision"] != stop:
            raise ValueError("exported disposition/stop contradicts categorical answers")
        ai = expected.get("ai_disposition")
        if ai not in {rule["disposition"] for rule in CATEGORICAL_RULES}:
            raise ValueError("bound AI proposal required")
        disagreement = disposition != ai
        derived = {"validated_disposition": disposition, "ai_disposition": ai, "disagreement_with_AI": disagreement,
                   "reconciliation_required": disagreement, "comparison_disposition": "uncertain_insufficient_evidence" if disagreement else disposition,
                   "semantic_acceptance_pending": True, "effective_disposition_activated": False,
                   "counts_as_accepted_current_effective_disposition": False, "model_execution_authorized": False, "scientific_readiness": False}
        if row.keys() & derived.keys():
            raise ValueError("owner fields collide with derived importer metadata")
        outcomes.append({**row, **derived})
    stop = any(row["stop_for_prospective_scientific_decision"] for row in outcomes)
    if type(record.get("stop_for_prospective_scientific_decision")) is not bool or record["stop_for_prospective_scientific_decision"] != stop:
        raise ValueError("aggregate scientific stop mismatch")
    return outcomes


def verify_authority(preflight: dict) -> None:
    if type(preflight.get("checkpoint")) is not int or preflight["checkpoint"] != 197 or preflight.get("review196_sha256") != REVIEW196_SHA256 or preflight.get("import_authority") != IMPORT_AUTHORITY:
        raise ValueError("Review196 and actual owner export import-only authority required")
    for field in ("activation_authorized", "model_execution_authorized", "scientific_readiness"):
        if preflight.get(field) is not False:
            raise ValueError("no activation or model authority")
    check = preflight["handoff195_CI"]
    expected = {"head_sha": "3f648377a7d273fc1f35202d101692423e4d9d40", "run_id": 38710625142, "job_id": 116340807019,
                "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success"}
    if any(type(check.get(field)) is not type(value) or check[field] != value for field, value in expected.items()):
        raise ValueError("exact successful195 handoff CI required")


def import_review(args: argparse.Namespace) -> dict:
    private_output(args.out_root, [args.preflight, args.review_root, args.human_input])
    preflight = json.loads(args.preflight.read_bytes())
    private_output(args.out_root, [Path(name) for name in preflight["protected_snapshots"]])
    verify_authority(preflight)
    verify_preserved(preflight)
    if _sha256(Path(__file__)) != preflight["import_code_sha256"] or _sha256(ROOT / REVIEW_FILE) != REVIEW196_SHA256 or _sha256(ROOT / HANDOFF_REPORT) != preflight["handoff195_report_sha256"]:
        raise ValueError("import implementation or authority drift")
    if str(args.review_root.resolve()) != preflight["review_root"] or args.human_input.is_symlink() or args.human_input.resolve() != (args.review_root / "oulu-batch07-categorical-review.json").resolve() or _sha256(args.human_input) != preflight["human_input_sha256"]:
        raise ValueError("exact received owner export required")
    public = json.loads((ROOT / HANDOFF_REPORT).read_bytes())
    definition_path = args.review_root / "review_definition.json"
    digest = _sha256(definition_path)
    if digest != public["review_definition_sha256"] or _sha256(args.review_root / "index.html") != public["page_sha256"] or _sha256(args.review_root / "summary.json") != public["private_summary_sha256"]:
        raise ValueError("accepted195 form drift")
    definition = json.loads(definition_path.read_bytes())
    ai_root = Path(definition["ai_root"])
    ai_public_path = ROOT / "results/phase1/oulu-visual-review-batch07-v1.json"
    if _sha256(ai_public_path) != definition["accepted_AI_report_sha256"]:
        raise ValueError("accepted193 report drift")
    ai_public = json.loads(ai_public_path.read_bytes())
    ai_paths = sorted((ai_root / "pairs").glob("*.json"))
    if len(ai_paths) != 10 or bundle(ai_paths) != ai_public["pair_record_bundle_sha256"]:
        raise ValueError("accepted AI bundle drift")
    queue_root = Path(preflight["queue_root"])
    queue_public = json.loads((ROOT / "results/phase1/oulu-lineage-exact-evidence-v1.json").read_bytes())
    queue_paths = sorted((queue_root / "pairs").glob("*.json"))
    if len(queue_paths) != 6640 or bundle(queue_paths) != queue_public["pair_record_bundle_sha256"] or _sha256(queue_root / "summary.json") != queue_public["private_summary_sha256"]:
        raise ValueError("accepted frozen queue drift")
    for pair in definition["pairs"]:
        rank = pair["queue_rank"]
        if type(rank) is not int or rank not in TARGET_RANKS:
            raise ValueError("exact batch07 rank required")
        packet_path = Path(definition["packet_root"]) / "pairs" / f"{rank:06d}" / "packet.json"
        ai_path = ai_root / "pairs" / f"{rank:06d}.json"
        packet = json.loads(packet_path.read_bytes())
        ai = json.loads(ai_path.read_bytes())
        queue = json.loads(queue_paths[rank].read_bytes())
        if _sha256(packet_path) != pair["packet_sha256"] or _sha256(ai_path) != pair["ai_record_sha256"] or _sha256(queue_paths[rank]) != pair["exact_pair_record_sha256"]:
            raise ValueError("original packet/AI/queue record drift")
        if packet["queue_rank"] != rank or ai["queue_rank"] != rank or queue["queue_rank"] != rank or queue["candidate"] != packet["candidate"] or packet["candidate"] != ai["candidate"] or ai["proposed_disposition"] != pair["ai_disposition"]:
            raise ValueError("exact source candidate/AI proposal mismatch")
        if ai["packet_sha256"] != pair["packet_sha256"] or ai["exact_pair_record_sha256"] != pair["exact_pair_record_sha256"] or packet["exact_pair_record_sha256"] != pair["exact_pair_record_sha256"] or ai["assets_actually_viewed_sha256"] != packet["image_sha256"]:
            raise ValueError("source provenance binding mismatch")
        if ai["human_review_performed"] is not False or ai["effective_disposition_activated"] is not False:
            raise ValueError("historical AI-only state required")
        for name, expected in pair["required_assets_sha256"].items():
            asset = args.review_root / name
            original = packet_path.parent / Path(name).name
            if asset.is_symlink() or not asset.resolve().is_relative_to(args.review_root.resolve()) or _sha256(asset) != expected or _sha256(original) != expected or packet["image_sha256"][Path(name).name] != expected:
                raise ValueError("actual reviewed image drift")
    human = json.loads(args.human_input.read_bytes())
    outcomes = validate_categorical(human, {**definition, "sha256": digest})
    write_immutable_record(args.out_root / "human_input.json", human)
    lineage = {"version": 1, "review196_sha256": REVIEW196_SHA256, "handoff195_report_sha256": preflight["handoff195_report_sha256"],
               "review_definition_sha256": digest, "page_sha256": public["page_sha256"], "review194_sha256": definition["review194_sha256"],
               "accepted_AI_report_sha256": definition["accepted_AI_report_sha256"], "human_input_sha256": preflight["human_input_sha256"],
               "canonical_human_input_sha256": _sha256(args.out_root / "human_input.json"), "preflight_sha256": _sha256(args.preflight),
               "handoff195_CI": preflight["handoff195_CI"], "import_code_sha256": _sha256(Path(__file__)), "import_authority": IMPORT_AUTHORITY,
               "formal_review196_present_before_import": True, "no_automatic_effective_activation": True, "scientific_readiness": False}
    write_immutable_record(args.out_root / "lineage.json", lineage)
    for row in outcomes:
        write_immutable_record(args.out_root / "pairs" / f"{row['queue_rank']:06d}.json", row)
    verify_preserved(preflight)
    if _sha256(args.human_input) != preflight["human_input_sha256"] or bundle(queue_paths) != queue_public["pair_record_bundle_sha256"]:
        raise ValueError("owner input or queue changed during import")
    result = {"version": 1, "status": "categorical_human_decisions_imported_pending_review_no_activation", "queue_ranks": list(TARGET_RANKS),
              "human_categorical_reviews": len(outcomes), "disposition_counts": dict(Counter(row["disposition"] for row in outcomes)),
              "AI_proposed_disposition_counts": dict(Counter(pair["ai_disposition"] for pair in definition["pairs"])),
              "disagreements_with_AI": sum(row["disagreement_with_AI"] for row in outcomes),
              "reconciliation_required_ranks": [row["queue_rank"] for row in outcomes if row["reconciliation_required"]],
              "comparison_disposition_counts": dict(Counter(row["comparison_disposition"] for row in outcomes)),
              "comparison_states_are_not_activated_dispositions": True,
              "stop_for_prospective_scientific_decision": any(row["stop_for_prospective_scientific_decision"] for row in outcomes),
              "effective_dispositions_activated": 0, "accepted_current_total": 60, "batch07_closed": False, "semantic_acceptance_pending": True,
              "human_input_sha256": preflight["human_input_sha256"], "canonical_human_input_sha256": lineage["canonical_human_input_sha256"],
              "review_definition_sha256": digest, "lineage_sha256": _sha256(args.out_root / "lineage.json"),
              "pair_record_bundle_sha256": bundle(sorted((args.out_root / "pairs").glob("*.json"))),
              "human_authorship": "categorical_choices_and_inspection_attested_not_independently_authenticated",
              "all_supplied_owner_fields_preserved": True, "original_owner_bytes_unchanged": True,
              "human_prose_required_or_generated": False, "machine_narrative_generated": False, "historical_pending_review_flags_unchanged": True,
              "queue_continued": False, "model_execution_authorized": False, "scientific_readiness": False}
    write_immutable_record(args.out_root / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("preflight", "review-root", "human-input", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        print(json.dumps(import_review(parser.parse_args()), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError):
        print("BATCH07 CATEGORICAL IMPORT FAILED: no semantic acceptance or activation", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())