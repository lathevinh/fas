#!/usr/bin/env python3
"""Import genuine batch04 answers, preserving history without effective activation."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.human_review import validate_human_review
from fas.oulu import _sha256
from prepare_oulu_owner_review import private_output


def validate_batch04(record: dict, definition: dict) -> list[dict]:
    expected = definition.get("pairs", [])
    if [pair.get("queue_rank") for pair in expected] != list(range(30, 40)) or any(type(pair.get("queue_rank")) is not int for pair in expected):
        raise ValueError("fixed batch04 definition ranks required")
    rows = record.get("pairs")
    if not isinstance(rows, list) or len(rows) != 10 or any(not isinstance(row, dict) or type(row.get("queue_rank")) is not int for row in rows):
        raise ValueError("ten integer batch04 ranks required")
    if {row["queue_rank"] for row in rows} != set(range(30, 40)):
        raise ValueError("exact ten unique batch04 ranks required")
    local = {**record, "pairs": [{**row, "queue_rank": row["queue_rank"] - 30} for row in rows]}
    local_definition = {**definition, "pairs": [{**pair, "queue_rank": pair["queue_rank"] - 30} for pair in expected]}
    return [{**row, "queue_rank": row["queue_rank"] + 30, "effective_disposition_activated": False}
            for row in validate_human_review(local, local_definition)]


def import_review(args: argparse.Namespace) -> dict:
    public_path = ROOT / "results/phase1/oulu-human-review-handoff-batch04-v1.json"
    public = json.loads(public_path.read_bytes())
    path = args.review_root / "review_definition.json"
    digest = _sha256(path)
    if digest != public["review_definition_sha256"] or _sha256(args.review_root / "index.html") != public["page_sha256"] or _sha256(args.review_root / "summary.json") != public["private_summary_sha256"]:
        raise ValueError("published handoff drift")
    definition = json.loads(path.read_bytes())
    private_output(args.out_root, [args.review_root, args.human_input, *(Path(name) for name in definition["protected_input_roots"])])
    if _sha256(ROOT / "scripts/prepare_oulu_owner_batch04.py") != definition["preparation_code_sha256"] or _sha256(ROOT / "src/fas/human_review.py") != definition["validation_code_sha256"] or _sha256(ROOT / "scripts/prepare_oulu_owner_review.py") != definition["page_source_sha256"]:
        raise ValueError("accepted human implementation drift")
    preflight_path = args.review_root.parent / "oulu_batch04_human_import_preflight_v1.json"
    preflight = json.loads(preflight_path.read_bytes())
    if _sha256(public_path) != preflight["published_handoff_report_sha256"] or _sha256(Path(__file__)) != preflight["import_code_sha256"]:
        raise ValueError("handoff authority or import implementation drift")
    check = preflight["handoff_CI"]
    if check["head_sha"] != "5ec33a829e8e3fcd65337f427a126ab01baf461c" or check["run_id"] != 38336188705 or check["job_id"] != 115096680331 or check["status"] != "completed" or check["conclusion"] != "success":
        raise ValueError("exact successful handoff CI required")
    if preflight["owner_continue_authorization"] != "owner_supplied_batch04_human_review_JSON_import_only_no_activation":
        raise ValueError("scoped owner import authorization required")

    def verify_protected() -> None:
        for root, expected in preflight["protected_snapshots"].items():
            folder = Path(root)
            current = {str(file.relative_to(folder)): _sha256(file) for file in sorted(folder.rglob("*")) if file.is_file()}
            if current != expected:
                raise ValueError("protected evidence drift")
        for name, expected in {**preflight["pinned_prior_implementation_sha256"], **preflight["study_config_sha256"], **preflight["pinned_private_evidence_sha256"]}.items():
            if _sha256(Path(name)) != expected:
                raise ValueError("pinned evidence or implementation drift")

    verify_protected()
    ai_root = Path(definition["ai_review_root"])
    ai_public_path = ROOT / "results/phase1/oulu-visual-review-batch04-v1.json"
    ai_public = json.loads(ai_public_path.read_bytes())
    if _sha256(ai_public_path) != definition["accepted_visual_report_sha256"]:
        raise ValueError("accepted AI report drift")
    ai_paths = sorted((ai_root / "pairs").glob("*.json"))
    bundle = hashlib.sha256("".join(f"{file.name}:{_sha256(file)}\n" for file in ai_paths).encode()).hexdigest()
    if len(ai_paths) != 10 or bundle != definition["ai_record_bundle_sha256"] or bundle != ai_public["observation_record_bundle_sha256"] or _sha256(ai_root / "summary.json") != ai_public["private_summary_sha256"] or _sha256(ai_root / "definition.json") != ai_public["definition_sha256"]:
        raise ValueError("accepted AI ledger drift")
    for pair in definition["pairs"]:
        rank = pair["queue_rank"]
        if _sha256(ai_root / "pairs" / f"{rank:06d}.json") != pair["ai_record_sha256"]:
            raise ValueError("bound AI proposal drift")
        packet_path = Path(definition["packet_root"]) / "pairs" / f"{rank:06d}" / "packet.json"
        if _sha256(packet_path) != pair["packet_sha256"]:
            raise ValueError("bound packet drift")
        for name, expected in pair["required_assets_sha256"].items():
            asset = (args.review_root / name).resolve()
            if not asset.is_relative_to(args.review_root.resolve()) or _sha256(asset) != expected:
                raise ValueError("bound reviewed image drift")
    input_digest = _sha256(args.human_input)
    if input_digest != preflight["owner_input_sha256"]:
        raise ValueError("owner input digest drift")
    human = json.loads(args.human_input.read_bytes())
    outcomes = validate_batch04(human, {**definition, "sha256": digest})
    lineage = {"version": 1, "review_definition_sha256": digest, "published_handoff_report_sha256": _sha256(public_path),
               "human_input_sha256": input_digest, "preflight_sha256": _sha256(preflight_path), "handoff_CI": check,
               "import_code_sha256": _sha256(Path(__file__)), "validation_code_sha256": definition["validation_code_sha256"],
               "owner_continue_authorization": preflight["owner_continue_authorization"],
               "formal_external_review_of_handoff149_present": preflight["formal_external_review_of_handoff149_present"],
               "no_automatic_effective_activation": True, "scientific_readiness": False}
    write_immutable_record(args.out_root / "lineage.json", lineage)
    write_immutable_record(args.out_root / "human_input.json", human)
    for row in outcomes:
        write_immutable_record(args.out_root / "pairs" / f"{row['queue_rank']:06d}.json", row)
    if _sha256(args.human_input) != input_digest:
        raise ValueError("human input changed during import")
    verify_protected()
    result = {"version": 1, "status": "bound_human_answers_imported_no_effective_activation", "queue_ranks": list(range(30, 40)),
              "human_dispositions": len(outcomes), "disposition_counts": dict(Counter(row["disposition"] for row in outcomes)),
              "disagreements": sum(row["disagreement"] for row in outcomes),
              "validated_comparison_state_counts": dict(Counter(row["effective_disposition"] for row in outcomes)),
              "effective_dispositions_activated": 0, "batch04_accepted_reconciled_disposition_state": False,
              "stop_for_prospective_scientific_decision": any(row["stop_for_prospective_scientific_decision"] for row in outcomes),
              "unique_human_rationale_count": len({row["rationale"] for row in outcomes}),
              "heightened_scrutiny_ranks": [38, 39], "heightened_scrutiny_pair_specific_reasoning_verified": False,
              "review148_haze_scrutiny_resolution_pending": True, "eligible_for_additive_activation_without_further_review": False,
              "human_authorship": "reviewer_attestation_not_independently_authenticated", "human_input_sha256": input_digest,
              "review_definition_sha256": digest, "lineage_sha256": _sha256(args.out_root / "lineage.json"),
              "AI_and_handoff_and_frozen_inputs_unchanged": True, "queue_continued": False,
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
        print("BATCH04 HUMAN IMPORT FAILED: no clearance or fabricated review", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())