#!/usr/bin/env python3
"""Import two genuine scrutiny answers without modifying history or activating them."""

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
from fas.human_review import DISPOSITIONS
from fas.oulu import _sha256
from prepare_oulu_owner_review import private_output


def validate_scrutiny(record: dict, definition: dict) -> list[dict]:
    expected = definition.get("pairs", [])
    if [pair.get("queue_rank") for pair in expected] != [38, 39] or any(type(pair.get("queue_rank")) is not int for pair in expected):
        raise ValueError("exact targeted definition required")
    if type(record.get("version")) is not int or record["version"] != 1 or record.get("record_type") != "targeted_human_scrutiny_resolution":
        raise ValueError("targeted human record required")
    reviewer = record.get("reviewer", {})
    if reviewer.get("kind") not in {"owner_human", "designated_human"} or not isinstance(reviewer.get("id"), str) or not reviewer["id"].strip() or reviewer.get("personally_inspected_bound_evidence") is not True:
        raise ValueError("personal human attestation required")
    if record.get("review_definition_sha256") != definition["sha256"]:
        raise ValueError("definition drift")
    stamp = record.get("reviewed_at_utc")
    if not isinstance(stamp, str):
        raise ValueError("UTC timestamp required")
    timestamp = datetime.fromisoformat(stamp)
    if timestamp.utcoffset() is None or timestamp.utcoffset().total_seconds() != 0:
        raise ValueError("UTC timestamp required")
    rows = record.get("pairs")
    if not isinstance(rows, list) or len(rows) != 2 or any(not isinstance(row, dict) or type(row.get("queue_rank")) is not int for row in rows) or {row["queue_rank"] for row in rows} != {38, 39}:
        raise ValueError("exact two original integer ranks required")
    outcomes = []
    for row in sorted(rows, key=lambda item: item["queue_rank"]):
        pair = expected[row["queue_rank"] - 38]
        for field, expected_field in (("imported_human_record_sha256", "imported_human_record_sha256"), ("packet_sha256", "packet_sha256"), ("reviewed_assets_sha256", "required_assets_sha256")):
            if row.get(field) != pair[expected_field]:
                raise ValueError("original row, packet or viewed assets drift")
        if row.get("personally_reviewed") is not True or row.get("disposition") not in DISPOSITIONS or row.get("capture_provenance_certified") is not False:
            raise ValueError("human disposition and limited attestation required")
        if any(not isinstance(row.get(field), str) or not row[field].strip() for field in ("visible_rendered_structure", "rationale")):
            raise ValueError("human structure and rationale required")
        sufficient = row.get("remaining_evidence_sufficient")
        if type(sufficient) is not bool or sufficient != (row["disposition"] != "uncertain_insufficient_evidence"):
            raise ValueError("sufficiency and disposition inconsistent")
        disagreement = row["disposition"] != pair["ai_disposition"]
        outcomes.append({**row, "ai_disposition": pair["ai_disposition"], "disagreement": disagreement,
                         "reconciliation_required": disagreement, "effective_disposition_activated": False,
                         "comparison_disposition": "uncertain_insufficient_evidence" if disagreement else row["disposition"],
                         "stop_for_prospective_scientific_decision": row["disposition"] == "confirmed_same_content_or_derived_lineage",
                         "pair_specific_reasoning_semantically_verified": False,
                         "model_execution_authorized": False, "scientific_readiness": False})
    stop = any(row["stop_for_prospective_scientific_decision"] for row in outcomes)
    if type(record.get("stop_for_prospective_scientific_decision")) is not bool or record["stop_for_prospective_scientific_decision"] != stop:
        raise ValueError("scientific stop flag inconsistent")
    return outcomes


def import_review(args: argparse.Namespace) -> dict:
    preflight_path = args.review_root.parent / "oulu_batch04_scrutiny_import_preflight_v1.json"
    private_output(args.out_root, [args.review_root, args.human_input, preflight_path])
    preflight = json.loads(preflight_path.read_bytes())
    private_output(args.out_root, [Path(name) for name in preflight["protected_snapshots"]])

    def verify_inputs() -> None:
        for name, expected in preflight["protected_snapshots"].items():
            folder = Path(name)
            actual = {str(path.relative_to(folder)): _sha256(path) for path in sorted(folder.rglob("*")) if path.is_file()}
            if actual != expected:
                raise ValueError("protected evidence drift")
        for name, digest in {**preflight["pinned_file_sha256"], **preflight["frozen_file_sha256"]}.items():
            if _sha256(Path(name)) != digest:
                raise ValueError("pinned evidence drift")
        if _sha256(Path(__file__)) != preflight["import_code_sha256"] or _sha256(args.human_input) != preflight["owner_input_sha256"]:
            raise ValueError("import code or owner input drift")

    verify_inputs()
    check = preflight["handoff_CI"]
    if check["head_sha"] != "8ef665e0d72e2a9e9eacd491715f7a88c2526379" or check["run_id"] != 38340720035 or check["job_id"] != 115110856891 or check["status"] != "completed" or check["conclusion"] != "success":
        raise ValueError("exact successful scrutiny handoff CI required")
    if preflight["owner_continue_authorization"] != "owner_supplied_two_pair_scrutiny_JSON_import_only_no_activation":
        raise ValueError("scoped owner authorization required")
    public_path = ROOT / "results/phase1/oulu-scrutiny-handoff-batch04-v1.json"
    public = json.loads(public_path.read_bytes())
    for name, field in (("review_definition.json", "review_definition_sha256"), ("index.html", "page_sha256"), ("summary.json", "private_summary_sha256")):
        if _sha256(args.review_root / name) != public[field]:
            raise ValueError("published handoff drift")
    path = args.review_root / "review_definition.json"
    definition = json.loads(path.read_bytes())
    for pair in definition["pairs"]:
        old_path = Path(definition["import_root"]) / "pairs" / f"{pair['queue_rank']:06d}.json"
        if _sha256(old_path) != pair["imported_human_record_sha256"]:
            raise ValueError("original imported human row drift")
        old = json.loads(old_path.read_bytes())
        if old["packet_sha256"] != pair["packet_sha256"] or old["effective_disposition_activated"] is not False:
            raise ValueError("original row state drift")
        if sorted(old["reviewed_assets_sha256"].values()) != sorted(pair["required_assets_sha256"].values()):
            raise ValueError("original reviewed image drift")
        for name, digest in pair["required_assets_sha256"].items():
            asset = (args.review_root / name).resolve()
            if not asset.is_relative_to(args.review_root.resolve()) or _sha256(asset) != digest:
                raise ValueError("bound asset drift")
    human = json.loads(args.human_input.read_bytes())
    outcomes = validate_scrutiny(human, {**definition, "sha256": _sha256(path)})
    lineage = {"version": 1, "review_definition_sha256": _sha256(path), "human_input_sha256": _sha256(args.human_input),
               "published_handoff_report_sha256": _sha256(public_path), "preflight_sha256": _sha256(preflight_path),
               "import_code_sha256": _sha256(Path(__file__)), "handoff_CI": check,
               "owner_continue_authorization": preflight["owner_continue_authorization"],
               "formal_external_review_of_handoff152_present": preflight["formal_external_review_of_handoff152_present"],
               "no_automatic_effective_activation": True, "scientific_readiness": False}
    write_immutable_record(args.out_root / "lineage.json", lineage)
    write_immutable_record(args.out_root / "human_input.json", human)
    for row in outcomes:
        write_immutable_record(args.out_root / "pairs" / f"{row['queue_rank']:06d}.json", row)
    verify_inputs()
    result = {"version": 1, "status": "bound_targeted_human_answers_imported_pending_semantic_review_no_activation",
              "queue_ranks": [38, 39], "human_scrutiny_answers_imported": 2,
              "disposition_counts": dict(Counter(row["disposition"] for row in outcomes)),
              "disagreements": sum(row["disagreement"] for row in outcomes),
              "unique_visible_structure_count": len({row["visible_rendered_structure"] for row in outcomes}),
              "unique_human_rationale_count": len({row["rationale"] for row in outcomes}),
              "effective_dispositions_activated": 0, "batch04_accepted_reconciled_disposition_state": False,
              "stop_for_prospective_scientific_decision": any(row["stop_for_prospective_scientific_decision"] for row in outcomes),
              "heightened_scrutiny_pair_specific_reasoning_verified": False, "review148_haze_scrutiny_resolution_pending": True,
              "eligible_for_additive_activation_without_further_review": False,
              "human_input_sha256": _sha256(args.human_input), "review_definition_sha256": _sha256(path),
              "lineage_sha256": _sha256(args.out_root / "lineage.json"), "historical_inputs_unchanged": True,
              "human_authorship": "reviewer_attestation_not_independently_authenticated",
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
        print("SCRUTINY IMPORT FAILED: no fabricated reasoning or activation", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())