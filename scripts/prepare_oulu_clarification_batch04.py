#!/usr/bin/env python3
"""Prepare additive human foreground clarification without altering prior answers."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.oulu import _sha256
from prepare_oulu_owner_review import private_output
from prepare_oulu_scrutiny_batch04 import render_scrutiny

NOTICE = (
    "For this queue pair, describe actual visible foreground structure on each side, "
    "compare persistent structure across temporal panels and trigger, and state the "
    "haze/veil limitation. Background difference alone cannot exclude derived content. "
    "No answer is prescribed. If evidence is too obscured, retain uncertainty; "
    "same/derived content requires an immediate scientific hard stop. "
    "Earlier answers remain unchanged."
)


def render_clarification(definition: dict, digest: str) -> str:
    if any(not pair.get("imported_scrutiny_record_sha256") for pair in definition["pairs"]):
        raise ValueError("accepted scrutiny row bindings required")
    page = render_scrutiny(definition, digest)
    prefix, marker, remainder = page.partition("const DATA=")
    if not marker:
        raise ValueError("embedded data missing")
    _, end = json.JSONDecoder().raw_decode(remainder)
    page = prefix + marker + "__DATA__" + remainder[end:]
    old_controls = (
        "const visibleLabel=document.createElement('label');visibleLabel.textContent='Rendered structure still visible despite haze/veil';"
        "const visibleText=document.createElement('textarea');visibleText.value=item.visible_rendered_structure;"
        "visibleText.addEventListener('input',()=>{item.visible_rendered_structure=visibleText.value;update()});visibleLabel.append(visibleText);panel.append(visibleLabel);"
    )
    controls = (
        "[['left_visible_foreground_structure','Left: visible foreground structure despite haze/veil'],"
        "['right_visible_foreground_structure','Right: visible foreground structure despite haze/veil'],"
        "['haze_veil_limitation','Haze/veil limitation for this pair']].forEach(([field,text])=>{"
        "const label=document.createElement('label');label.textContent=text;const input=document.createElement('textarea');"
        "input.value=item[field];input.addEventListener('input',()=>{item[field]=input.value;update()});label.append(input);panel.append(label)});"
    )
    replacements = {
        "Batch 04 Targeted Scrutiny": "Batch 04 Pair-Specific Clarification",
        old_controls: controls,
        "visible_rendered_structure:''": "left_visible_foreground_structure:'',right_visible_foreground_structure:'',haze_veil_limitation:''",
        "item.visible_rendered_structure.trim()": "item.left_visible_foreground_structure.trim()&&item.right_visible_foreground_structure.trim()&&item.haze_veil_limitation.trim()",
        "visible_rendered_structure:state[rank].visible_rendered_structure,": "imported_scrutiny_record_sha256:pair.imported_scrutiny_record_sha256,left_visible_foreground_structure:state[rank].left_visible_foreground_structure,right_visible_foreground_structure:state[rank].right_visible_foreground_structure,haze_veil_limitation:state[rank].haze_veil_limitation,",
        "Pair-specific reasoning and limitations for this disposition": "Persistent foreground comparison across temporal panels and trigger; reasoning for this disposition",
        "targeted_human_scrutiny_resolution": "human_pair_specific_clarification",
        "oulu-batch04-scrutiny-resolution.json": "oulu-batch04-pair-specific-clarification.json",
        "scrutiny resolutions": "pair-specific clarifications",
    }
    for before, after in replacements.items():
        if before not in page:
            raise ValueError("pinned scrutiny renderer mismatch")
        page = page.replace(before, after)
    data = json.dumps({"definition": definition, "sha256": digest}).replace("<", "\\u003c")
    return page.replace("__DATA__", data)


def prepare(args: argparse.Namespace) -> dict:
    preflight_path = args.scrutiny_root.parent / "oulu_batch04_clarification_handoff_preflight_v1.json"
    private_output(args.out_root, [args.scrutiny_root, args.review_root, preflight_path])
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
        if _sha256(Path(__file__)) != preflight["runner_sha256"]:
            raise ValueError("clarification runner drift")

    verify_inputs()
    check = preflight["import_CI"]
    if check["head_sha"] != "ea1d1d5f9865b272530ef300f6632ddbac2f6241" or check["run_id"] != 38341972399 or check["job_id"] != 115114774603 or check["status"] != "completed" or check["conclusion"] != "success":
        raise ValueError("exact successful targeted import CI required")
    public_path = ROOT / "results/phase1/oulu-scrutiny-import-batch04-v1.json"
    public = json.loads(public_path.read_bytes())
    if _sha256(args.scrutiny_root / "summary.json") != public["private_summary_sha256"] or _sha256(args.scrutiny_root / "lineage.json") != public["lineage_sha256"]:
        raise ValueError("accepted targeted import drift")
    previous_path = args.review_root / "review_definition.json"
    if _sha256(previous_path) != public["review_definition_sha256"]:
        raise ValueError("previous definition drift")
    previous = json.loads(previous_path.read_bytes())
    definition = {
        "version": 1, "state": "awaiting_genuine_pair_specific_clarification_only38_39", "pairs": [],
        "scrutiny_notice": NOTICE, "review154_sha256": preflight["review154_sha256"],
        "accepted_scrutiny_report_sha256": _sha256(public_path), "scrutiny_root": str(args.scrutiny_root.resolve()),
        "previous_review_root": str(args.review_root.resolve()), "previous_review_definition_sha256": _sha256(previous_path),
        "prior_scrutiny_source_JSON_sha256": public["human_input_sha256"], "scrutiny_summary_sha256": public["private_summary_sha256"],
        "preflight_sha256": _sha256(preflight_path), "preparation_code_sha256": _sha256(Path(__file__)),
        "scrutiny_renderer_sha256": _sha256(ROOT / "scripts/prepare_oulu_scrutiny_batch04.py"), "import_CI": check,
        "human_fields_prefilled": False, "earlier_AI_notes_initially_collapsed": True,
        "all_prior_human_answers_not_modified": True, "requires_separate_clarification_import": True,
        "semantic_reasoning_automatically_certified": False, "no_automatic_effective_activation": True,
        "confirmed_action": "immediate_scientific_hard_stop", "model_execution_authorized": False, "scientific_readiness": False,
    }
    if [pair["queue_rank"] for pair in previous["pairs"]] != [38, 39]:
        raise ValueError("exact previous targeted scope required")
    for pair in previous["pairs"]:
        rank = pair["queue_rank"]
        row_path = args.scrutiny_root / "pairs" / f"{rank:06d}.json"
        row = json.loads(row_path.read_bytes())
        if row["queue_rank"] != rank or row["imported_human_record_sha256"] != pair["imported_human_record_sha256"] or row["packet_sha256"] != pair["packet_sha256"] or row["reviewed_assets_sha256"] != pair["required_assets_sha256"] or row["effective_disposition_activated"] is not False:
            raise ValueError("accepted scrutiny row binding drift")
        assets = {}
        if len(pair["required_assets_sha256"]) != 3 or {Path(name).name for name in pair["required_assets_sha256"]} != {"temporal_a.png", "temporal_b.png", "trigger.png"}:
            raise ValueError("exact three historical assets required")
        for name, digest in pair["required_assets_sha256"].items():
            source = (args.review_root / name).resolve()
            if not source.is_relative_to(args.review_root.resolve()) or _sha256(source) != digest:
                raise ValueError("historical asset drift")
            target = args.out_root / "assets" / f"{rank:06d}" / Path(name).name
            target.parent.mkdir(parents=True, exist_ok=True)
            with source.open("rb") as handle, target.open("xb") as destination:
                shutil.copyfileobj(handle, destination)
            if _sha256(target) != digest:
                raise ValueError("copied asset drift")
            assets[str(target.relative_to(args.out_root))] = digest
        definition["pairs"].append({**pair, "imported_scrutiny_record_sha256": _sha256(row_path), "required_assets_sha256": assets})
    write_immutable_record(args.out_root / "review_definition.json", definition)
    digest = _sha256(args.out_root / "review_definition.json")
    with (args.out_root / "index.html").open("x") as handle:
        handle.write(render_clarification(definition, digest))
    verify_inputs()
    result = {"version": 1, "status": "pair_specific_clarification_handoff_prepared_human_input_required",
              "queue_ranks": [38, 39], "pairs_prepared": 2, "required_bound_images": 6,
              "actual_human_clarifications": 0, "effective_dispositions_activated": 0,
              "review148_haze_scrutiny_resolution_pending": True, "review_definition_sha256": digest,
              "page_sha256": _sha256(args.out_root / "index.html"), "historical_inputs_unchanged": True,
              "queue_continued": False, "scientific_readiness": False}
    write_immutable_record(args.out_root / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("scrutiny-root", "review-root", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        print(json.dumps(prepare(parser.parse_args()), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError):
        print("CLARIFICATION HANDOFF FAILED: no human reasoning manufactured", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())