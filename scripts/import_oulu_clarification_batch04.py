#!/usr/bin/env python3
"""Bind genuine additive clarification without rewriting history or activating it."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.oulu import _sha256
from import_oulu_scrutiny_batch04 import validate_scrutiny
from prepare_oulu_owner_review import private_output


def validate_clarification(record: dict, definition: dict) -> list[dict]:
    if record.get("record_type") != "human_pair_specific_clarification":
        raise ValueError("separate clarification record required")
    rows = record.get("pairs")
    if not isinstance(rows, list) or len(rows) != 2 or any(not isinstance(row, dict) for row in rows):
        raise ValueError("two human clarification rows required")
    expected = {pair["queue_rank"]: pair for pair in definition["pairs"]}
    for row in rows:
        if any(not isinstance(row.get(field), str) or not row[field].strip() for field in
               ("left_visible_foreground_structure", "right_visible_foreground_structure", "haze_veil_limitation")):
            raise ValueError("actual human foreground and haze text required")
        if row.get("queue_rank") not in expected or not expected[row["queue_rank"]].get("imported_scrutiny_record_sha256") or row.get("imported_scrutiny_record_sha256") != expected[row["queue_rank"]]["imported_scrutiny_record_sha256"]:
            raise ValueError("accepted scrutiny row drift")
    local = {**record, "record_type": "targeted_human_scrutiny_resolution",
             "pairs": [{**row, "visible_rendered_structure": row["left_visible_foreground_structure"]} for row in rows]}
    validated = validate_scrutiny(local, definition)
    originals = {row["queue_rank"]: row for row in rows}
    annotations = ("ai_disposition", "disagreement", "reconciliation_required", "effective_disposition_activated",
                   "comparison_disposition", "stop_for_prospective_scientific_decision",
                   "pair_specific_reasoning_semantically_verified", "model_execution_authorized", "scientific_readiness")
    return [{**originals[row["queue_rank"]], **{field: row[field] for field in annotations}} for row in validated]


def import_review(args: argparse.Namespace) -> dict:
    preflight_path = args.review_root.parent / "oulu_batch04_clarification_import_preflight_v1.json"
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
                raise ValueError("pinned authority or implementation drift")
        if _sha256(Path(__file__)) != preflight["import_code_sha256"] or _sha256(args.human_input) != preflight["owner_input_sha256"]:
            raise ValueError("import code or original owner input drift")

    verify_inputs()
    check = preflight["handoff_CI"]
    if check["head_sha"] != "e3e82ebed767073b923112b7dde43c6313cd48c8" or check["run_id"] != 38343639077 or check["job_id"] != 115119974087 or check["status"] != "completed" or check["conclusion"] != "success":
        raise ValueError("exact successful clarification handoff CI required")
    if preflight["owner_continue_authorization"] != "owner_supplied_pair_specific_clarification_JSON_import_only_no_activation":
        raise ValueError("scoped owner import authority required")
    public_path = ROOT / "results/phase1/oulu-clarification-handoff-batch04-v1.json"
    public = json.loads(public_path.read_bytes())
    for name, field in (("review_definition.json", "review_definition_sha256"), ("index.html", "page_sha256"), ("summary.json", "private_summary_sha256")):
        if _sha256(args.review_root / name) != public[field]:
            raise ValueError("published clarification handoff drift")
    path = args.review_root / "review_definition.json"
    definition = json.loads(path.read_bytes())
    previous_path = Path(definition["previous_review_root"]) / "review_definition.json"
    if _sha256(previous_path) != definition["previous_review_definition_sha256"]:
        raise ValueError("previous scrutiny definition drift")
    previous = json.loads(previous_path.read_bytes())
    for pair in definition["pairs"]:
        rank = pair["queue_rank"]
        original_path = Path(previous["import_root"]) / "pairs" / f"{rank:06d}.json"
        scrutiny_path = Path(definition["scrutiny_root"]) / "pairs" / f"{rank:06d}.json"
        for row_path, field in ((original_path, "imported_human_record_sha256"), (scrutiny_path, "imported_scrutiny_record_sha256")):
            if _sha256(row_path) != pair[field]:
                raise ValueError("bound original human or scrutiny row drift")
            old = json.loads(row_path.read_bytes())
            if old["queue_rank"] != rank or old["packet_sha256"] != pair["packet_sha256"] or old["effective_disposition_activated"] is not False or sorted(old["reviewed_assets_sha256"].values()) != sorted(pair["required_assets_sha256"].values()):
                raise ValueError("old human row state or assets drift")
        for name, digest in pair["required_assets_sha256"].items():
            asset = (args.review_root / name).resolve()
            if not asset.is_relative_to(args.review_root.resolve()) or _sha256(asset) != digest:
                raise ValueError("viewed image drift")
    human = json.loads(args.human_input.read_bytes())
    outcomes = validate_clarification(human, {**definition, "sha256": _sha256(path)})
    lineage = {"version": 1, "human_input_sha256": _sha256(args.human_input), "review_definition_sha256": _sha256(path),
               "published_handoff_report_sha256": _sha256(public_path), "preflight_sha256": _sha256(preflight_path),
               "import_code_sha256": _sha256(Path(__file__)), "validation_dependency_sha256": _sha256(ROOT / "scripts/import_oulu_scrutiny_batch04.py"),
               "handoff_CI": check, "owner_continue_authorization": preflight["owner_continue_authorization"],
               "formal_external_review_of_handoff155_present": preflight["formal_external_review_of_handoff155_present"],
               "no_automatic_effective_activation": True, "scientific_readiness": False}
    write_immutable_record(args.out_root / "lineage.json", lineage)
    write_immutable_record(args.out_root / "human_input.json", human)
    for row in outcomes:
        write_immutable_record(args.out_root / "pairs" / f"{row['queue_rank']:06d}.json", row)
    verify_inputs()
    result = {"version": 1, "status": "bound_human_clarifications_imported_pending_review_no_activation",
              "queue_ranks": [38, 39], "human_clarifications_imported": 2,
              "disposition_counts": dict(Counter(row["disposition"] for row in outcomes)),
              "disagreements": sum(row["disagreement"] for row in outcomes),
              "unique_left_foreground_count": len({row["left_visible_foreground_structure"] for row in outcomes}),
              "unique_right_foreground_count": len({row["right_visible_foreground_structure"] for row in outcomes}),
              "unique_haze_limitation_count": len({row["haze_veil_limitation"] for row in outcomes}),
              "unique_human_rationale_count": len({row["rationale"] for row in outcomes}),
              "stop_for_prospective_scientific_decision": any(row["stop_for_prospective_scientific_decision"] for row in outcomes),
              "effective_dispositions_activated": 0, "heightened_scrutiny_pair_specific_reasoning_verified": False,
              "review148_haze_scrutiny_resolution_pending": True, "semantic_review_required": True,
              "eligible_for_additive_activation_without_further_review": False, "batch04_accepted_reconciled_disposition_state": False,
              "human_input_sha256": _sha256(args.human_input), "review_definition_sha256": _sha256(path),
              "lineage_sha256": _sha256(args.out_root / "lineage.json"), "historical_inputs_unchanged": True,
              "human_authorship": "reviewer_attestation_not_independently_authenticated", "queue_continued": False,
              "model_execution_authorized": False, "scientific_readiness": False}
    write_immutable_record(args.out_root / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("review-root", "human-input", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        print(json.dumps(import_review(parser.parse_args()), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError):
        print("CLARIFICATION IMPORT FAILED: no manufactured human reasoning or activation", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())