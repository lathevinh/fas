#!/usr/bin/env python3
"""Prepare blank human review for accepted batch04 AI proposals, with scrutiny notices."""

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

HEIGHTENED_SCRUTINY_RANKS = (38, 39)
HEIGHTENED_SCRUTINY_NOTICE = (
    "Haze/veil reduces some torso detail in this sparse evidence. "
    "Assess whether the remaining visible content independently supports your judgment, "
    "and give pair-specific reasoning and limitations. "
    "Uncertainty remains valid if that evidence is insufficient; no answer is prescribed."
)


def render_batch04(definition: dict, digest: str) -> str:
    pairs = definition["pairs"]
    if [pair["queue_rank"] for pair in pairs] != list(range(30, 40)) or any(type(pair["queue_rank"]) is not int for pair in pairs):
        raise ValueError("fixed batch04 ranks required")
    for pair in pairs:
        expected = HEIGHTENED_SCRUTINY_NOTICE if pair["queue_rank"] in HEIGHTENED_SCRUTINY_RANKS else ""
        if pair.get("human_review_notice") != expected:
            raise ValueError("bound neutral scrutiny notices required")
    page = PAGE
    replacements = {
        "Batch 01": "Batch 04",
        "queue_rank:rank,packet_sha256": "queue_rank:pair.queue_rank,packet_sha256",
        "'Pair '+(rank+1)": "'Queue '+pair.queue_rank",
        "oulu-batch01-human-review.json": "oulu-batch04-human-review.json",
        "panel.append(heading);const evidence=": "panel.append(heading);if(pair.human_review_notice){const notice=document.createElement('p');notice.setAttribute('role','note');notice.textContent=pair.human_review_notice;panel.append(notice)}const evidence=",
    }
    for before, after in replacements.items():
        if before not in page:
            raise ValueError("accepted page adapter mismatch")
        page = page.replace(before, after)
    data = json.dumps({"definition": definition, "sha256": digest}).replace("<", "\\u003c")
    return page.replace("__DATA__", data)


def prepare(args: argparse.Namespace) -> dict:
    preflight_path = args.ai_root.parent / "oulu_batch04_handoff_preflight_v1.json"
    private_output(args.out_root, [args.ai_root, args.packet_root, preflight_path])
    preflight = json.loads(preflight_path.read_bytes())
    protected = [Path(name) for name in preflight["protected_snapshots"]]
    private_output(args.out_root, protected)
    if _sha256(Path(__file__)) != preflight["handoff_runner_sha256"]:
        raise ValueError("handoff implementation drift")

    def verify_protected() -> None:
        for root, expected in preflight["protected_snapshots"].items():
            path = Path(root)
            current = {str(file.relative_to(path)): _sha256(file) for file in sorted(path.rglob("*")) if file.is_file()}
            if current != expected:
                raise ValueError("protected evidence drift")
        for name, expected in {**preflight["study_config_sha256"], **preflight["pinned_prior_implementation_sha256"]}.items():
            if _sha256(ROOT / name) != expected:
                raise ValueError("accepted config or implementation drift")

    verify_protected()
    check = preflight["AI_checkpoint_CI"]
    if check["head_sha"] != "a9f1e78bceb5f6c0c2a16e855aa82ca270ff0392" or check["run_id"] != 38332170137 or check["job_id"] != 115084143725 or check["status"] != "completed" or check["conclusion"] != "success":
        raise ValueError("exact successful AI checkpoint CI required")
    review_path = ROOT / "docs/148-review-doc147-oulu-batch04-ai-review.md"
    public_path = ROOT / "results/phase1/oulu-visual-review-batch04-v1.json"
    packets_public_path = ROOT / "results/phase1/oulu-batch04-packets-v1.json"
    if _sha256(review_path) != preflight["review148_sha256"] or _sha256(public_path) != preflight["accepted_AI_report_sha256"]:
        raise ValueError("accepted review/report authority drift")
    accepted = json.loads(public_path.read_bytes())
    if _sha256(packets_public_path) != accepted["accepted_packet_report_sha256"]:
        raise ValueError("accepted packet report drift")
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
                  "AI_proposals_initially_collapsed": True, "import_requires_separate_batch04_rank30_through39_adapter": True,
                  "heightened_scrutiny_ranks": list(HEIGHTENED_SCRUTINY_RANKS), "scrutiny_notice_prescribes_no_answer": True,
                  "disagreement_rule": "preserve_both_uncertain_until_separate_reconciliation",
                  "confirmed_cross_role_action": "stop_for_explicit_prospective_scientific_decision",
                  "no_automatic_effective_activation": True, "model_execution_authorized": False, "scientific_readiness": False}
    for rank, path in enumerate(paths, 30):
        ai = json.loads(path.read_bytes())
        packet_path = args.packet_root / "pairs" / f"{rank:06d}" / "packet.json"
        packet = json.loads(packet_path.read_bytes())
        if ai["queue_rank"] != rank or packet["queue_rank"] != rank or ai["packet_sha256"] != _sha256(packet_path) or ai["candidate"] != packet["candidate"] or ai["definition_sha256"] != accepted["definition_sha256"] or ai["proposed_disposition"] != "rejected_false_positive" or ai["AI_visual_review_performed"] is not True or ai["human_review_performed"] is not False or ai["effective_disposition_activated"] is not False:
            raise ValueError("fixed accepted batch04 AI-only proposal mismatch")
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
                                    "human_review_notice": HEIGHTENED_SCRUTINY_NOTICE if rank in HEIGHTENED_SCRUTINY_RANKS else "",
                                    "required_assets_sha256": assets, "full_resolution": []})
    write_immutable_record(args.out_root / "review_definition.json", definition)
    digest = _sha256(args.out_root / "review_definition.json")
    with (args.out_root / "index.html").open("x") as handle:
        handle.write(render_batch04(definition, digest))
    verify_protected()
    result = {"version": 1, "status": "human_review_required_not_completed", "queue_ranks": list(range(30, 40)),
              "pairs_prepared": 10, "required_bound_images": 30, "actual_human_reviews": 0, "new_effective_dispositions": 0,
              "review_definition_sha256": digest, "page_sha256": _sha256(args.out_root / "index.html"), "full_resolution_frames_added": 0,
              "heightened_scrutiny_ranks": list(HEIGHTENED_SCRUTINY_RANKS), "scrutiny_notice_prescribes_no_answer": True,
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
        print("BATCH04 HUMAN HANDOFF FAILED: no human review or clearance claimed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())