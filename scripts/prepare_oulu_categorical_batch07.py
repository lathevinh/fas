#!/usr/bin/env python3
"""Prepare the Review194 categorical handoff without collecting human answers."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.human_review import DISPOSITIONS
from fas.oulu import _sha256
from prepare_oulu_categorical_batch06 import CATEGORICAL_RULES, SCRIPT as PREVIOUS_SCRIPT, is_digest
from prepare_oulu_owner_review import PAGE, private_output
from prepare_oulu_visual_batch05 import bundle
from recover_oulu_archive_identity import verify_preserved

TARGET_RANKS = tuple(range(60, 70))
REVIEW_FILE = "docs/194-review-doc193-oulu-batch07-ai-proposals.md"
REVIEW_SHA256 = "6b7b1146c1607a53705f38babf11dfa11357ab5bb121ab5927050bff31f5c514"
AI_REPORT_FILE = "results/phase1/oulu-visual-review-batch07-v1.json"
AI_REPORT_SHA256 = "363529acf728c3e665f0b2b768acb194ff14adab10b4274f2828f171b1658c68"
NOTICE = "Assess this rank separately. Insufficient evidence preserves uncertainty; same or derived content requires a scientific stop. No answer or agreement is prescribed."
VISIBILITY_LIMITS = {
    60: "Reflection limits parts of the rendered view; hidden regions were not assessed. ",
    61: "Grain and color cast limit fine detail; hidden regions were not assessed. ",
    62: "Reflection limits parts of the rendered view; hidden regions were not assessed. ",
    63: "Haze and darkness limit lower garment detail; hidden regions were not assessed. ",
    64: "Foreground occlusion limits garment visibility; hidden regions were not assessed. ",
    65: "Dark lower garment regions limit visibility; hidden regions were not assessed. ",
    66: "Severe underexposure limits visible garment structure; hidden regions were not assessed. ",
    67: "Grain limits fine garment detail; hidden regions were not assessed. ",
    68: "A lower-view veil limits garment detail; hidden regions were not assessed. ",
    69: "Dark lower garment regions limit visibility; hidden regions were not assessed. ",
}
CORRELATION_NOTICE = "Some source videos or configurations recur among ranks67..68; this evidence is correlated. Give a separate decision for this rank. "
SCRIPT = PREVIOUS_SCRIPT.replace("review184", "review194").replace("batch06", "batch07")


def human_notice(rank: int) -> str:
    return VISIBILITY_LIMITS[rank] + (CORRELATION_NOTICE if rank in (67, 68) else "") + NOTICE


def verify_authority(preflight: dict) -> None:
    if type(preflight.get("checkpoint")) is not int or preflight["checkpoint"] != 195 or preflight.get("review194_sha256") != REVIEW_SHA256 or preflight.get("accepted_AI_report_sha256") != AI_REPORT_SHA256:
        raise ValueError("exact Review194 and accepted193 authority required")
    ranks = preflight.get("queue_ranks", [])
    if ranks != list(TARGET_RANKS) or any(type(rank) is not int for rank in ranks):
        raise ValueError("exact integer ranks60..69 required")
    for field in ("human_input_collection_authorized", "import_authorized", "effective_activation_authorized", "model_execution_authorized", "scientific_readiness"):
        if preflight.get(field) is not False:
            raise ValueError("preparation-only authority required")
    check = preflight["source193_CI"]
    expected = {"head_sha": "7f998d71dabd8f629f9f117970ce58acdacf7931", "run_id": 38706506199, "job_id": 116327125698,
                "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success"}
    if any(type(check.get(field)) is not type(value) or check[field] != value for field, value in expected.items()):
        raise ValueError("exact successful193 CI required")


def render_categorical(definition: dict, digest: str) -> str:
    pairs = definition["pairs"]
    if [pair["queue_rank"] for pair in pairs] != list(TARGET_RANKS) or any(type(pair["queue_rank"]) is not int for pair in pairs):
        raise ValueError("exact batch07 integer ranks required")
    if definition.get("review194_sha256") != REVIEW_SHA256 or definition.get("accepted_AI_report_sha256") != AI_REPORT_SHA256 or not is_digest(definition.get("preflight_sha256")):
        raise ValueError("Review194 and accepted193 bindings required")
    if json.dumps(definition.get("categorical_rules"), sort_keys=True) != json.dumps(CATEGORICAL_RULES, sort_keys=True):
        raise ValueError("strict categorical mapping required")
    for pair in pairs:
        rank = pair["queue_rank"]
        if pair.get("human_review_notice") != human_notice(rank) or any(not is_digest(pair.get(field)) for field in ("packet_sha256", "ai_record_sha256", "exact_pair_record_sha256")):
            raise ValueError("bound original pair and neutral notice required")
        if pair.get("ai_disposition") not in DISPOSITIONS:
            raise ValueError("accepted non-binding AI disposition required")
        expected_names = {f"assets/{rank:06d}/{name}.png" for name in ("temporal_a", "temporal_b", "trigger")}
        if set(pair["required_assets_sha256"]) != expected_names or any(not is_digest(value) for value in pair["required_assets_sha256"].values()):
            raise ValueError("exact three bound assets required")
    shell = PAGE.split("<script>", 1)[0].replace("Batch 01", "Batch 07 Categorical Review")
    shell = shell.replace("</style>", "fieldset{margin:14px 0;padding:12px;border:1px solid var(--line);min-width:0}legend{max-width:100%;overflow-wrap:anywhere}fieldset label{display:inline-flex;gap:8px;align-items:center;margin:8px 24px 0 0}[hidden]{display:none!important}</style>")
    data = json.dumps({"definition": definition, "sha256": digest}).replace("<", "\\u003c")
    return shell + SCRIPT.replace("__DATA__", data) + PAGE.split("</script>", 1)[1]


def prepare(args: argparse.Namespace) -> dict:
    private_output(args.out_root, [args.preflight, args.packet_root, args.ai_root])
    preflight = json.loads(args.preflight.read_bytes())
    private_output(args.out_root, [Path(name) for name in preflight["protected_snapshots"]])
    verify_authority(preflight)
    if _sha256(ROOT / REVIEW_FILE) != REVIEW_SHA256 or _sha256(ROOT / AI_REPORT_FILE) != AI_REPORT_SHA256:
        raise ValueError("accepted authority drift")
    if _sha256(Path(__file__)) != preflight["runner_sha256"] or str(args.packet_root.resolve()) != preflight["packet_root"] or str(args.ai_root.resolve()) != preflight["ai_root"]:
        raise ValueError("runner or source-root drift")
    verify_preserved(preflight)
    report = json.loads((ROOT / AI_REPORT_FILE).read_bytes())
    for name, field in (("definition.json", "private_definition_sha256"), ("ledger.json", "private_ledger_sha256"), ("summary.json", "private_summary_sha256")):
        if _sha256(args.ai_root / name) != report[field]:
            raise ValueError("accepted AI root drift")
    ai_paths = sorted((args.ai_root / "pairs").glob("*.json"))
    if [path.name for path in ai_paths] != [f"{rank:06d}.json" for rank in TARGET_RANKS] or bundle(ai_paths) != report["pair_record_bundle_sha256"]:
        raise ValueError("accepted ten-row AI bundle required")
    definition = {
        "version": 1, "state": "awaiting195_form_review_before_genuine_human_answers", "pairs": [],
        "review194_sha256": REVIEW_SHA256, "accepted_AI_report_sha256": AI_REPORT_SHA256,
        "source193_CI": preflight["source193_CI"], "preflight_sha256": _sha256(args.preflight),
        "preparation_code_sha256": _sha256(Path(__file__)), "packet_root": str(args.packet_root.resolve()), "ai_root": str(args.ai_root.resolve()),
        "categorical_rules": CATEGORICAL_RULES, "queue_ranks": list(TARGET_RANKS),
        "required_human_pair_fields": ["evidence_sufficient", "same_or_derived_content", "personal_inspection_attested", "owner_decision_attested"],
        "human_fields_prefilled": False, "human_prose_required": False, "AI_context_hidden_until_pair_submission": True,
        "AI_context_authorship": "AI_generated_non_binding_proposal_not_human_reasoning", "fully_blinded_review_claimed": False,
        "checkpoint_review_required_before_human_input": True, "requires_separate_categorical_importer": True,
        "import_authorized": False, "effective_activation_authorized": False,
        "confirmed_action": "immediate_scientific_hard_stop", "model_execution_authorized": False, "scientific_readiness": False,
    }
    copies = []
    for rank, ai_path in zip(TARGET_RANKS, ai_paths, strict=True):
        ai = json.loads(ai_path.read_bytes())
        packet_path = args.packet_root / "pairs" / f"{rank:06d}" / "packet.json"
        packet = json.loads(packet_path.read_bytes())
        if type(ai["queue_rank"]) is not int or type(packet["queue_rank"]) is not int or ai["queue_rank"] != rank or packet["queue_rank"] != rank or ai["packet_sha256"] != _sha256(packet_path) or ai["candidate"] != packet["candidate"] or ai["exact_pair_record_sha256"] != packet["exact_pair_record_sha256"]:
            raise ValueError("exact accepted candidate/queue/packet binding required")
        if ai["assets_actually_viewed_sha256"] != packet["image_sha256"] or set(packet["image_sha256"]) != {"temporal_a.png", "temporal_b.png", "trigger.png"}:
            raise ValueError("exact30 accepted images required")
        if ai["human_review_performed"] is not False or ai["effective_disposition_activated"] is not False:
            raise ValueError("AI proposal must not be treated as human or effective")
        assets = {}
        for name in ("temporal_a.png", "temporal_b.png", "trigger.png"):
            source = packet_path.parent / name
            expected = packet["image_sha256"][name]
            if source.is_symlink() or _sha256(source) != expected:
                raise ValueError("bound asset drift")
            relative = f"assets/{rank:06d}/{name}"
            assets[relative] = expected
            copies.append((source, args.out_root / relative, expected))
        definition["pairs"].append({
            "queue_rank": rank, "packet_sha256": _sha256(packet_path), "ai_record_sha256": _sha256(ai_path),
            "exact_pair_record_sha256": ai["exact_pair_record_sha256"], "required_assets_sha256": assets,
            "ai_disposition": ai["proposed_disposition"], "ai_observations": [ai["rationale"]],
            "ai_limitation": ai["limitation"] + " " + ai["visibility_limitation"], "human_review_notice": human_notice(rank),
        })
    render_categorical(definition, "pending")
    for source, target, expected in copies:
        target.parent.mkdir(parents=True, exist_ok=True)
        with source.open("rb") as handle, target.open("xb") as destination:
            shutil.copyfileobj(handle, destination)
        if _sha256(target) != expected:
            raise ValueError("copied image drift")
    write_immutable_record(args.out_root / "review_definition.json", definition)
    digest = _sha256(args.out_root / "review_definition.json")
    with (args.out_root / "index.html").open("x") as handle:
        handle.write(render_categorical(definition, digest))
    verify_preserved(preflight)
    result = {
        "version": 1, "status": "categorical_handoff_prepared_review_required_before_human_use", "queue_ranks": list(TARGET_RANKS),
        "pairs_prepared": 10, "required_bound_images": 30, "actual_categorical_human_reviews": 0, "effective_dispositions_activated": 0,
        "accepted_current_total": 60, "accepted_AI_screen_coverage": 70, "highest_risk_remaining_unreviewed": 15,
        "review_definition_sha256": digest, "page_sha256": _sha256(args.out_root / "index.html"), "review194_sha256": REVIEW_SHA256,
        "human_prose_required": False, "human_fields_prefilled": False, "historical_inputs_unchanged": True,
        "checkpoint_review_required_before_human_input": True, "new_media_decode_or_extraction_executed": False,
        "queue_continued": False, "model_execution_authorized": False, "scientific_readiness": False,
    }
    write_immutable_record(args.out_root / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("preflight", "packet-root", "ai-root", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        print(json.dumps(prepare(parser.parse_args()), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError):
        print("BATCH07 CATEGORICAL HANDOFF FAILED: no human answers collected or imported", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())