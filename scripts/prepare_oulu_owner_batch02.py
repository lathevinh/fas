#!/usr/bin/env python3
"""Prepare a separate blank human handoff for accepted batch02 AI proposals."""

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


def render_batch02(definition: dict, digest: str) -> str:
    if [pair["queue_rank"] for pair in definition["pairs"]] != list(range(10, 20)):
        raise ValueError("fixed batch02 ranks required")
    page = PAGE
    replacements = {
        "Batch 01": "Batch 02",
        "queue_rank:rank,packet_sha256": "queue_rank:pair.queue_rank,packet_sha256",
        "'Pair '+(rank+1)": "'Queue '+pair.queue_rank",
        "oulu-batch01-human-review.json": "oulu-batch02-human-review.json",
    }
    for before, after in replacements.items():
        if before not in page:
            raise ValueError("accepted page adapter mismatch")
        page = page.replace(before, after)
    data = json.dumps({"definition": definition, "sha256": digest}).replace("<", "\\u003c")
    return page.replace("__DATA__", data)


def prepare(args: argparse.Namespace) -> dict:
    phase = args.ai_root.parent
    preflight_path = phase / "oulu_batch02_handoff_preflight_v1.json"
    preflight = json.loads(preflight_path.read_bytes())
    protected = [Path(name) for name in preflight["protected_snapshots"]]
    private_output(args.out_root, [args.ai_root, args.packet_root, preflight_path, *protected])
    def verify_protected() -> None:
        for root, expected in preflight["protected_snapshots"].items():
            path = Path(root)
            actual = {str(file.relative_to(path)): _sha256(file) for file in sorted(path.rglob("*")) if file.is_file()}
            if actual != expected:
                raise ValueError("protected evidence drift")
    verify_protected()
    check = preflight["AI_checkpoint_CI"]
    if check["head_sha"] != "44c774aeea87945c1617780c8cb64ffc4e6fb2dc" or check["status"] != "completed" or check["conclusion"] != "success":
        raise ValueError("exact successful AI checkpoint CI required")
    public_path = ROOT / "results/phase1/oulu-visual-review-batch02-v1.json"
    accepted = json.loads(public_path.read_bytes())
    packets_public = json.loads((ROOT / "results/phase1/oulu-batch02-packets-v1.json").read_bytes())
    if _sha256(args.ai_root / "summary.json") != accepted["private_summary_sha256"] or _sha256(args.ai_root / "definition.json") != accepted["definition_sha256"]:
        raise ValueError("accepted AI summary/definition drift")
    if _sha256(args.packet_root / "summary.json") != packets_public["private_summary_sha256"] or _sha256(args.packet_root / "lineage.json") != packets_public["private_lineage_sha256"]:
        raise ValueError("accepted packet summary/lineage drift")
    paths = sorted((args.ai_root / "pairs").glob("*.json"))
    bundle = hashlib.sha256("".join(f"{path.name}:{_sha256(path)}\n" for path in paths).encode()).hexdigest()
    if len(paths) != 10 or bundle != accepted["pair_record_bundle_sha256"]:
        raise ValueError("accepted AI bundle drift")
    historical = json.loads((ROOT / "results/phase1/oulu-human-review-handoff-v1.json").read_bytes())
    for name, expected in historical["implementation_sha256"].items():
        if _sha256(ROOT / name) != expected:
            raise ValueError("accepted human implementation drift")
    definition = {"version": 1, "state": "awaiting_actual_owner_or_designated_human_review", "pairs": [],
                  "ai_review_root": str(args.ai_root.resolve()), "packet_root": str(args.packet_root.resolve()),
                  "protected_input_roots": [str(path.resolve()) for path in protected],
                  "accepted_visual_report_sha256": _sha256(public_path), "ai_record_bundle_sha256": bundle,
                  "review_sha256": _sha256(ROOT / "docs/130-review-doc129-oulu-batch02-ai-review.md"),
                  "preflight_sha256": _sha256(preflight_path), "AI_checkpoint_CI": check,
                  "preparation_code_sha256": _sha256(Path(__file__)), "page_source_sha256": _sha256(ROOT / "scripts/prepare_oulu_owner_review.py"),
                  "validation_code_sha256": _sha256(ROOT / "src/fas/human_review.py"),
                  "human_dispositions_prefilled": False, "AI_proposals_initially_collapsed": True,
                  "disagreement_rule": "preserve_both_uncertain_until_separate_reconciliation",
                  "confirmed_cross_role_action": "stop_for_explicit_prospective_scientific_decision",
                  "no_automatic_effective_activation": True, "model_execution_authorized": False, "scientific_readiness": False}
    for rank, path in enumerate(paths, 10):
        ai = json.loads(path.read_bytes())
        packet_path = args.packet_root / "pairs" / f"{rank:06d}" / "packet.json"
        packet = json.loads(packet_path.read_bytes())
        if ai["queue_rank"] != rank or ai["packet_sha256"] != _sha256(packet_path) or ai["proposed_disposition"] != "rejected_false_positive":
            raise ValueError("fixed accepted batch02 proposal mismatch")
        assets = {}
        for name, expected in packet["image_sha256"].items():
            source = packet_path.parent / name
            if Path(name).name != name or _sha256(source) != expected or ai["assets_actually_viewed_sha256"][name] != expected:
                raise ValueError("bound image drift")
            target = args.out_root / "assets" / f"{rank:06d}" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with source.open("rb") as handle, target.open("xb") as destination:
                shutil.copyfileobj(handle, destination)
            assets[str(target.relative_to(args.out_root))] = _sha256(target)
        definition["pairs"].append({"queue_rank": rank, "packet_sha256": _sha256(packet_path), "ai_record_sha256": _sha256(path),
                                    "ai_disposition": ai["proposed_disposition"], "ai_observations": [ai["rationale"]], "ai_limitation": ai["limitation"],
                                    "required_assets_sha256": assets, "full_resolution": []})
    write_immutable_record(args.out_root / "review_definition.json", definition)
    digest = _sha256(args.out_root / "review_definition.json")
    with (args.out_root / "index.html").open("x") as handle:
        handle.write(render_batch02(definition, digest))
    verify_protected()
    result = {"version": 1, "status": "human_review_required_not_completed", "queue_ranks": list(range(10, 20)),
              "pairs_prepared": 10, "required_bound_images": 30, "actual_human_reviews": 0,
              "new_effective_dispositions": 0, "review_definition_sha256": digest, "page_sha256": _sha256(args.out_root / "index.html"),
              "full_resolution_frames_added": 0, "AI_ledger_and_protected_evidence_unchanged": True,
              "queue_continued": False, "model_execution_authorized": False, "scientific_readiness": False}
    write_immutable_record(args.out_root / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("packet-root", "ai-root", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        print(json.dumps(prepare(parser.parse_args()), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError):
        print("BATCH02 HUMAN HANDOFF FAILED: no human review or clearance claimed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())