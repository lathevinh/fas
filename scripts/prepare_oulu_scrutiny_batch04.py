#!/usr/bin/env python3
"""Prepare separate human scrutiny for ranks38..39 without changing prior answers."""

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
from prepare_oulu_owner_review import PAGE, private_output

NOTICE = (
    "Haze/veil limits some torso detail. Describe the rendered-content structure "
    "still visible for this pair, assess whether that evidence is sufficient, "
    "and explain your disposition and limitations. Insufficient evidence should "
    "remain uncertain. Same/derived content requires a scientific hard stop. "
    "No answer is prescribed; earlier answers remain unchanged."
)


def render_scrutiny(definition: dict, digest: str) -> str:
    pairs = definition["pairs"]
    if [pair["queue_rank"] for pair in pairs] != [38, 39] or any(type(pair["queue_rank"]) is not int for pair in pairs):
        raise ValueError("targeted ranks38..39 required")
    if any(not pair.get("imported_human_record_sha256") for pair in pairs):
        raise ValueError("original human row bindings required")
    controls = (
        "const visibleLabel=document.createElement('label');visibleLabel.textContent='Rendered structure still visible despite haze/veil';"
        "const visibleText=document.createElement('textarea');visibleText.value=item.visible_rendered_structure;"
        "visibleText.addEventListener('input',()=>{item.visible_rendered_structure=visibleText.value;update()});visibleLabel.append(visibleText);panel.append(visibleLabel);"
        "const sufficientLabel=document.createElement('label');sufficientLabel.textContent='Remaining evidence sufficiency ';"
        "const sufficientSelect=document.createElement('select');[['','Select sufficiency'],['true','Sufficient for a content judgment'],['false','Insufficient; retain uncertainty']].forEach(([value,text])=>sufficientSelect.add(new Option(text,value)));"
        "sufficientSelect.value=item.remaining_evidence_sufficient===null?'':String(item.remaining_evidence_sufficient);"
        "sufficientSelect.addEventListener('change',()=>{item.remaining_evidence_sufficient=sufficientSelect.value===''?null:sufficientSelect.value==='true';update()});sufficientLabel.append(sufficientSelect);panel.append(sufficientLabel);"
        "const rationale=document.createElement('label');"
    )
    replacements = {
        "Batch 01": "Batch 04 Targeted Scrutiny",
        "'Pair '+(rank+1)": "'Queue '+pair.queue_rank",
        "queue_rank:rank,packet_sha256": "queue_rank:pair.queue_rank,imported_human_record_sha256:pair.imported_human_record_sha256,visible_rendered_structure:state[rank].visible_rendered_structure,remaining_evidence_sufficient:state[rank].remaining_evidence_sufficient,packet_sha256",
        "disposition:'',rationale:''": "disposition:'',visible_rendered_structure:'',remaining_evidence_sufficient:null,rationale:''",
        "return item.disposition&&item.rationale.trim()": "return item.remaining_evidence_sufficient!==null&&item.visible_rendered_structure.trim()&&(item.disposition==='uncertain_insufficient_evidence'?item.remaining_evidence_sufficient===false:item.remaining_evidence_sufficient===true)&&item.disposition&&item.rationale.trim()",
        "count+' / 10 human dispositions'": "count+' / '+pairs.length+' scrutiny resolutions'",
        "count!==10||": "count!==pairs.length||",
        "const rationale=document.createElement('label');": controls,
        "rationale.textContent='Evidence and limitations'": "rationale.textContent='Pair-specific reasoning and limitations for this disposition'",
        "panel.append(heading);const evidence=": "panel.append(heading);const notice=document.createElement('p');notice.setAttribute('role','note');notice.textContent=DATA.definition.scrutiny_notice;panel.append(notice);const evidence=",
        "const record={version:1,reviewer:": "const record={version:1,record_type:'targeted_human_scrutiny_resolution',stop_for_prospective_scientific_decision:state.some(item=>item.disposition==='confirmed_same_content_or_derived_lineage'),reviewer:",
        "oulu-batch01-human-review.json": "oulu-batch04-scrutiny-resolution.json",
    }
    page = PAGE
    for before, after in replacements.items():
        if before not in page:
            raise ValueError("pinned page adapter mismatch")
        page = page.replace(before, after)
    data = json.dumps({"definition": definition, "sha256": digest}).replace("<", "\\u003c")
    return page.replace("__DATA__", data)


def prepare(args: argparse.Namespace) -> dict:
    preflight_path = args.import_root.parent / "oulu_batch04_scrutiny_handoff_preflight_v1.json"
    private_output(args.out_root, [args.import_root, args.review_root, preflight_path])
    preflight = json.loads(preflight_path.read_bytes())
    private_output(args.out_root, [Path(name) for name in preflight["protected_snapshots"]])

    def verify_inputs() -> None:
        for name, expected in preflight["protected_snapshots"].items():
            root = Path(name)
            actual = {str(path.relative_to(root)): _sha256(path) for path in sorted(root.rglob("*")) if path.is_file()}
            if actual != expected:
                raise ValueError("protected evidence drift")
        for name, digest in preflight["pinned_file_sha256"].items():
            if _sha256(Path(name)) != digest:
                raise ValueError("pinned authority or implementation drift")
        if _sha256(Path(__file__)) != preflight["runner_sha256"]:
            raise ValueError("scrutiny runner drift")

    verify_inputs()
    check = preflight["import_CI"]
    if check["head_sha"] != "1532e801038e3d47ec97dc154d894162dc534f70" or check["run_id"] != 38337553237 or check["job_id"] != 115100971471 or check["status"] != "completed" or check["conclusion"] != "success":
        raise ValueError("exact successful import CI required")
    public_path = ROOT / "results/phase1/oulu-human-review-import-batch04-v1.json"
    public = json.loads(public_path.read_bytes())
    if _sha256(public_path) != preflight["accepted_import_report_sha256"] or _sha256(args.import_root / "summary.json") != public["private_summary_sha256"] or _sha256(args.import_root / "lineage.json") != public["lineage_sha256"]:
        raise ValueError("accepted import authority drift")
    previous_path = args.review_root / "review_definition.json"
    if _sha256(previous_path) != public["review_definition_sha256"]:
        raise ValueError("previous handoff definition drift")
    previous = json.loads(previous_path.read_bytes())
    definition = {"version": 1, "state": "awaiting_genuine_human_scrutiny_resolution_only38_39", "pairs": [],
                  "scrutiny_notice": NOTICE, "review151_sha256": preflight["review151_sha256"],
                  "accepted_import_report_sha256": _sha256(public_path), "import_root": str(args.import_root.resolve()),
                  "previous_review_root": str(args.review_root.resolve()), "previous_review_definition_sha256": _sha256(previous_path),
                  "original_owner_JSON_sha256": public["original_owner_JSON_sha256"], "import_summary_sha256": public["private_summary_sha256"],
                  "preflight_sha256": _sha256(preflight_path), "preparation_code_sha256": _sha256(Path(__file__)),
                  "page_source_sha256": _sha256(ROOT / "scripts/prepare_oulu_owner_review.py"), "import_CI": check,
                  "human_fields_prefilled": False, "earlier_AI_notes_initially_collapsed": True,
                  "original_human_answers_not_modified": True, "requires_separate_two_pair_resolution_import": True,
                  "uncertainty_rule": "insufficient_visible_evidence_remains_uncertain", "confirmed_action": "immediate_scientific_hard_stop",
                  "no_automatic_effective_activation": True, "model_execution_authorized": False, "scientific_readiness": False}
    for rank in (38, 39):
        pair = next(pair for pair in previous["pairs"] if pair["queue_rank"] == rank)
        row_path = args.import_root / "pairs" / f"{rank:06d}.json"
        row = json.loads(row_path.read_bytes())
        if row["queue_rank"] != rank or row["packet_sha256"] != pair["packet_sha256"] or row["reviewed_assets_sha256"] != pair["required_assets_sha256"] or row["effective_disposition_activated"] is not False:
            raise ValueError("imported human row binding drift")
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
        definition["pairs"].append({"queue_rank": rank, "imported_human_record_sha256": _sha256(row_path),
                                    "packet_sha256": pair["packet_sha256"], "ai_record_sha256": pair["ai_record_sha256"],
                                    "ai_disposition": pair["ai_disposition"], "ai_observations": pair["ai_observations"],
                                    "ai_limitation": pair["ai_limitation"], "required_assets_sha256": assets, "full_resolution": []})
    write_immutable_record(args.out_root / "review_definition.json", definition)
    digest = _sha256(args.out_root / "review_definition.json")
    with (args.out_root / "index.html").open("x") as handle:
        handle.write(render_scrutiny(definition, digest))
    verify_inputs()
    result = {"version": 1, "status": "targeted_human_scrutiny_input_required_not_resolved", "queue_ranks": [38, 39],
              "pairs_prepared": 2, "required_bound_images": 6, "actual_human_scrutiny_resolutions": 0,
              "effective_dispositions_activated": 0, "review148_haze_scrutiny_resolution_pending": True,
              "review_definition_sha256": digest, "page_sha256": _sha256(args.out_root / "index.html"),
              "historical_inputs_unchanged": True, "queue_continued": False, "scientific_readiness": False}
    write_immutable_record(args.out_root / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("import-root", "review-root", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        print(json.dumps(prepare(parser.parse_args()), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError, StopIteration):
        print("BATCH04 SCRUTINY HANDOFF FAILED: no human reasoning or closure manufactured", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())