#!/usr/bin/env python3
"""Prepare blank batch05 human review with neutral visibility and reasoning gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.oulu import _sha256
from prepare_oulu_owner_review import PAGE, private_output

HEIGHTENED_SCRUTINY_RANKS = (40, 41, 42, 43, 49)
VISIBILITY_LIMITS = {
    40: "Darkness limits some foreground detail.",
    41: "Veil limits fine and lower-torso detail.",
    42: "Stronger veil limits fine and lower-torso detail.",
    43: "Darkness limits some lower-chest detail.",
    49: "Darkness limits some torso detail.",
}
SCRUTINY_NOTICE = (
    " Assess the visible foreground structures on both sides and the limitations "
    "of this pair's temporal panels and trigger. Give your own pair-specific "
    "reasoning. Uncertainty is valid if evidence is insufficient; same/derived "
    "content requires a scientific stop. No answer or agreement is prescribed."
)


def render_batch05(definition: dict, digest: str) -> str:
    pairs = definition["pairs"]
    if [pair["queue_rank"] for pair in pairs] != list(range(40, 50)) or any(type(pair["queue_rank"]) is not int for pair in pairs):
        raise ValueError("fixed integer batch05 ranks required")
    for pair in pairs:
        expected = VISIBILITY_LIMITS[pair["queue_rank"]] + SCRUTINY_NOTICE if pair["queue_rank"] in HEIGHTENED_SCRUTINY_RANKS else ""
        if pair.get("human_review_notice") != expected:
            raise ValueError("bound neutral visibility notices required")
    controls = (
        "const visibleLabel=document.createElement('label');visibleLabel.textContent='Visible foreground structures on both sides and visibility limitations (this pair)';"
        "const visibleText=document.createElement('textarea');visibleText.value=item.visible_rendered_structure;"
        "visibleText.addEventListener('input',()=>{item.visible_rendered_structure=visibleText.value;update()});visibleLabel.append(visibleText);panel.append(visibleLabel);"
        "const rationale=document.createElement('label');"
    )
    replacements = {
        "Batch 01": "Batch 05",
        "'Pair '+(rank+1)": "'Queue '+pair.queue_rank",
        "disposition:'',rationale:''": "disposition:'',visible_rendered_structure:'',rationale:''",
        "return item.disposition&&item.rationale.trim()": "return item.disposition&&item.visible_rendered_structure.trim()&&item.rationale.trim()",
        "queue_rank:rank,packet_sha256": "queue_rank:pair.queue_rank,visible_rendered_structure:state[rank].visible_rendered_structure,packet_sha256",
        "const rationale=document.createElement('label');": controls,
        "rationale.textContent='Evidence and limitations'": "rationale.textContent='Pair-specific rationale for this disposition'",
        "panel.append(heading);const evidence=": "panel.append(heading);if(pair.human_review_notice){const notice=document.createElement('p');notice.setAttribute('role','note');notice.textContent=pair.human_review_notice;panel.append(notice)}const evidence=",
        "const record={version:1,reviewer:": "const record={version:1,record_type:'batch05_human_review_with_pair_specific_structure',stop_for_prospective_scientific_decision:state.some(item=>item.disposition==='confirmed_same_content_or_derived_lineage'),reviewer:",
        "oulu-batch01-human-review.json": "oulu-batch05-human-review.json",
    }
    page = PAGE
    for before, after in replacements.items():
        if before not in page:
            raise ValueError("accepted page adapter mismatch")
        page = page.replace(before, after)
    data = json.dumps({"definition": definition, "sha256": digest}).replace("<", "\\u003c")
    return page.replace("__DATA__", data)


def prepare(args: argparse.Namespace) -> dict:
    preflight_path = args.ai_root.parent / "oulu_batch05_handoff_preflight_v1.json"
    private_output(args.out_root, [args.ai_root, args.packet_root, preflight_path])
    preflight = json.loads(preflight_path.read_bytes())
    protected = [Path(name) for name in preflight["protected_snapshots"]]
    private_output(args.out_root, protected)
    if _sha256(Path(__file__)) != preflight["handoff_runner_sha256"]:
        raise ValueError("handoff implementation drift")

    def verify_protected() -> None:
        for root, expected in preflight["protected_snapshots"].items():
            folder = Path(root)
            current = {str(path.relative_to(folder)): _sha256(path) for path in sorted(folder.rglob("*")) if path.is_file()}
            if current != expected:
                raise ValueError("protected evidence drift")
        for name, expected in {**preflight["pinned_file_sha256"], **preflight["study_config_sha256"], **preflight["frozen_file_sha256"]}.items():
            if _sha256(Path(name)) != expected:
                raise ValueError("accepted source/config/frozen input drift")

    verify_protected()
    check = preflight["AI_checkpoint_CI"]
    if check["head_sha"] != "629c8020b16325a6fab0f32ad7f5a3d4f4e7372d" or check["run_id"] != 38384928998 or check["job_id"] != 115254244024 or check["status"] != "completed" or check["conclusion"] != "success":
        raise ValueError("exact successful AI checkpoint CI required")
    review_path = ROOT / "docs/163-review-doc162-oulu-batch05-ai-review.md"
    public_path = ROOT / "results/phase1/oulu-visual-review-batch05-v1.json"
    packets_public_path = ROOT / "results/phase1/oulu-batch05-packets-v1.json"
    if _sha256(review_path) != preflight["review163_sha256"] or _sha256(public_path) != preflight["accepted_AI_report_sha256"]:
        raise ValueError("accepted review/report authority drift")
    accepted = json.loads(public_path.read_bytes())
    if _sha256(packets_public_path) != accepted["accepted_packet_report_sha256"] or accepted["stop_for_prospective_scientific_decision"] is not False:
        raise ValueError("accepted packet authority or scientific-stop drift")
    packets_public = json.loads(packets_public_path.read_bytes())
    if _sha256(args.ai_root / "summary.json") != accepted["private_summary_sha256"] or _sha256(args.ai_root / "definition.json") != accepted["definition_sha256"]:
        raise ValueError("accepted AI summary/definition drift")
    if _sha256(args.packet_root / "summary.json") != packets_public["private_summary_sha256"] or _sha256(args.packet_root / "lineage.json") != packets_public["private_lineage_sha256"]:
        raise ValueError("accepted packet summary/lineage drift")
    paths = sorted((args.ai_root / "pairs").glob("*.json"))
    bundle = hashlib.sha256("".join(f"{path.name}:{_sha256(path)}\n" for path in paths).encode()).hexdigest()
    if len(paths) != 10 or bundle != accepted["observation_record_bundle_sha256"]:
        raise ValueError("accepted AI bundle drift")
    historical = json.loads((ROOT / "results/phase1/oulu-human-review-handoff-v1.json").read_bytes())
    for name, expected in historical["implementation_sha256"].items():
        if _sha256(ROOT / name) != expected:
            raise ValueError("accepted human implementation drift")
    definition = {"version": 1, "state": "awaiting_actual_owner_or_designated_human_review", "pairs": [],
                  "ai_review_root": str(args.ai_root.resolve()), "packet_root": str(args.packet_root.resolve()),
                  "protected_input_roots": [str(path.resolve()) for path in protected], "accepted_visual_report_sha256": _sha256(public_path),
                  "accepted_packet_report_sha256": _sha256(packets_public_path), "ai_record_bundle_sha256": bundle,
                  "review_sha256": _sha256(review_path), "preflight_sha256": _sha256(preflight_path), "AI_checkpoint_CI": check,
                  "preparation_code_sha256": _sha256(Path(__file__)), "page_source_sha256": _sha256(ROOT / "scripts/prepare_oulu_owner_review.py"),
                  "validation_code_sha256": _sha256(ROOT / "src/fas/human_review.py"), "human_dispositions_prefilled": False,
                  "AI_proposals_initially_collapsed": True, "import_requires_separate_batch05_rank40_through49_structure_adapter": True,
                  "required_human_pair_fields": ["visible_rendered_structure", "rationale", "personally_reviewed"],
                  "pair_specific_reasoning_required_all_pairs": True, "reasoning_semantics_independently_verified": False,
                  "heightened_scrutiny_ranks": list(HEIGHTENED_SCRUTINY_RANKS), "scrutiny_notice_prescribes_no_answer": True,
                  "correlated_evidence_rank_families": [[40, 41, 42, 43], [47, 48]], "no_agreement_or_rejection_quota": True,
                  "disagreement_rule": "preserve_both_uncertain_until_separate_reconciliation",
                  "confirmed_cross_role_action": "stop_for_explicit_prospective_scientific_decision",
                  "no_automatic_effective_activation": True, "model_execution_authorized": False, "scientific_readiness": False}
    for rank, path in enumerate(paths, 40):
        ai = json.loads(path.read_bytes())
        packet_path = args.packet_root / "pairs" / f"{rank:06d}" / "packet.json"
        packet = json.loads(packet_path.read_bytes())
        if type(ai["queue_rank"]) is not int or ai["queue_rank"] != rank or packet["queue_rank"] != rank or ai["packet_sha256"] != _sha256(packet_path) or ai["candidate"] != packet["candidate"] or ai["definition_sha256"] != accepted["definition_sha256"] or ai["proposed_disposition"] not in {"rejected_false_positive", "uncertain_insufficient_evidence", "confirmed_same_content_or_derived_lineage"} or ai["AI_visual_review_performed"] is not True or ai["human_review_performed"] is not False or ai["effective_disposition_activated"] is not False:
            raise ValueError("fixed accepted batch05 AI-only proposal mismatch")
        assets = {}
        if set(packet["image_sha256"]) != {"temporal_a.png", "temporal_b.png", "trigger.png"}:
            raise ValueError("exact three prepared assets required")
        for name, expected in packet["image_sha256"].items():
            source = packet_path.parent / name
            if Path(name).name != name or _sha256(source) != expected or ai["assets_actually_viewed_sha256"][name] != expected:
                raise ValueError("bound image drift")
            target = args.out_root / "assets" / f"{rank:06d}" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with source.open("rb") as handle, target.open("xb") as destination:
                shutil.copyfileobj(handle, destination)
            assets[str(target.relative_to(args.out_root))] = _sha256(target)
            if assets[str(target.relative_to(args.out_root))] != expected:
                raise ValueError("copied asset drift")
        definition["pairs"].append({"queue_rank": rank, "packet_sha256": _sha256(packet_path), "ai_record_sha256": _sha256(path),
                                    "ai_disposition": ai["proposed_disposition"], "ai_observations": [ai["rationale"]], "ai_limitation": ai["limitation"],
                                    "human_review_notice": VISIBILITY_LIMITS[rank] + SCRUTINY_NOTICE if rank in HEIGHTENED_SCRUTINY_RANKS else "",
                                    "required_assets_sha256": assets, "full_resolution": []})
    write_immutable_record(args.out_root / "review_definition.json", definition)
    digest = _sha256(args.out_root / "review_definition.json")
    with (args.out_root / "index.html").open("x") as handle:
        handle.write(render_batch05(definition, digest))
    verify_protected()
    result = {"version": 1, "status": "human_review_required_not_completed", "queue_ranks": list(range(40, 50)),
              "pairs_prepared": 10, "required_bound_images": 30, "actual_human_reviews": 0, "new_effective_dispositions": 0,
              "review_definition_sha256": digest, "page_sha256": _sha256(args.out_root / "index.html"), "full_resolution_frames_added": 0,
              "heightened_scrutiny_ranks": list(HEIGHTENED_SCRUTINY_RANKS), "pair_specific_reasoning_required_all_pairs": True,
              "scrutiny_notice_prescribes_no_answer": True, "no_agreement_or_rejection_quota": True,
              "AI_ledger_and_protected_evidence_unchanged": True, "queue_continued": False,
              "model_execution_authorized": False, "scientific_readiness": False}
    write_immutable_record(args.out_root / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("packet-root", "ai-root", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        print(json.dumps(prepare(parser.parse_args()), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError):
        print("BATCH05 HUMAN HANDOFF FAILED: no human review or clearance claimed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())