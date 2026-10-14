#!/usr/bin/env python3
"""Prepare additive batch05 semantic clarification; never generate human answers."""

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
from prepare_oulu_owner_batch05 import HEIGHTENED_SCRUTINY_RANKS, SCRUTINY_NOTICE, VISIBILITY_LIMITS
from prepare_oulu_owner_review import PAGE, private_output

TARGET_RANKS = (40, 41, 42, 43, 48, 49)
MANDATORY_CLARIFICATION_RANKS = (42, 43, 48, 49)
IDENTICAL_EVIDENCE_NOTICE = (
    "All three bound images are byte-identical to rank47. Prior personal inspection "
    "of those identical images may be relied upon; new visual inspection is not "
    "required solely because this is a separate candidate. Describe the visible "
    "structures self-containedly and affirm your own rank48 decision. Do not "
    "silently copy an earlier answer; no disposition is prescribed."
)


def render_clarification(definition: dict, digest: str) -> str:
    pairs = definition["pairs"]
    if [pair["queue_rank"] for pair in pairs] != list(TARGET_RANKS) or any(type(pair["queue_rank"]) is not int for pair in pairs):
        raise ValueError("exact targeted batch05 integer ranks required")
    if not definition.get("governance_sha256"):
        raise ValueError("additive governance correction binding required")
    for pair in pairs:
        rank = pair["queue_rank"]
        expected = IDENTICAL_EVIDENCE_NOTICE if rank == 48 else VISIBILITY_LIMITS[rank] + SCRUTINY_NOTICE
        if not pair.get("imported_human_record_sha256") or pair.get("human_review_notice") != expected:
            raise ValueError("bound original human row and neutral notice required")
        if pair.get("bound_images_identical_to_rank47") is not (rank == 48):
            raise ValueError("rank48 identical-evidence binding required")
    controls = (
        "[['left_visible_foreground_structure','Left: visible foreground structure'],['right_visible_foreground_structure','Right: visible foreground structure'],['visibility_limitation','Visibility limitation for this pair']].forEach(([field,text])=>{const label=document.createElement('label');label.textContent=text;const input=document.createElement('textarea');input.value=item[field];input.addEventListener('input',()=>{item[field]=input.value;update()});label.append(input);panel.append(label)});"
        "const sufficientLabel=document.createElement('label');sufficientLabel.textContent='Remaining evidence sufficiency ';const sufficient=document.createElement('select');[['','Select sufficiency'],['true','Sufficient for a content judgment'],['false','Insufficient; retain uncertainty']].forEach(([value,text])=>sufficient.add(new Option(text,value)));sufficient.value=item.remaining_evidence_sufficient===null?'':String(item.remaining_evidence_sufficient);sufficient.addEventListener('change',()=>{item.remaining_evidence_sufficient=sufficient.value===''?null:sufficient.value==='true';update()});sufficientLabel.append(sufficient);panel.append(sufficientLabel);"
        "const ownLabel=document.createElement('label'),own=document.createElement('input');own.type='checkbox';own.checked=item.owner_disposition_is_own_decision;own.addEventListener('change',()=>{item.owner_disposition_is_own_decision=own.checked;update()});ownLabel.append(own,' This disposition is my own decision, not a prescribed AI answer');panel.append(ownLabel);"
        "const wordingLabel=document.createElement('label');wordingLabel.textContent='Wording assistance for this clarification ';const wording=document.createElement('select');[['','Select wording disclosure'],['not_used','No AI wording assistance used for this clarification'],['AI_assisted','AI-assisted wording used'],['cannot_exclude','AI wording assistance cannot be excluded']].forEach(([value,text])=>wording.add(new Option(text,value)));wording.value=item.wording_assistance_disclosure;wording.addEventListener('change',()=>{item.wording_assistance_disclosure=wording.value;update()});wordingLabel.append(wording);panel.append(wordingLabel);"
        "const rationale=document.createElement('label');"
    )
    replacements = {
        "Batch 01": "Batch 05 Targeted Clarification",
        "'Pair '+(rank+1)": "'Queue '+pair.queue_rank",
        "disposition:'',rationale:''": "disposition:'',left_visible_foreground_structure:'',right_visible_foreground_structure:'',visibility_limitation:'',remaining_evidence_sufficient:null,owner_disposition_is_own_decision:false,wording_assistance_disclosure:'',rationale:''",
        "return item.disposition&&item.rationale.trim()": "return item.left_visible_foreground_structure.trim()&&item.right_visible_foreground_structure.trim()&&item.visibility_limitation.trim()&&item.remaining_evidence_sufficient!==null&&(item.disposition==='uncertain_insufficient_evidence'?item.remaining_evidence_sufficient===false:item.remaining_evidence_sufficient===true)&&item.owner_disposition_is_own_decision&&item.wording_assistance_disclosure&&item.disposition&&item.rationale.trim()",
        "count+' / 10 human dispositions'": "count+' / '+pairs.length+' targeted clarifications'",
        "count!==10||": "count!==pairs.length||",
        "queue_rank:rank,packet_sha256": "queue_rank:pair.queue_rank,imported_human_record_sha256:pair.imported_human_record_sha256,bound_images_identical_to_rank47:pair.bound_images_identical_to_rank47,identical_evidence_reference_rank:pair.bound_images_identical_to_rank47?47:null,left_visible_foreground_structure:state[rank].left_visible_foreground_structure,right_visible_foreground_structure:state[rank].right_visible_foreground_structure,visibility_limitation:state[rank].visibility_limitation,remaining_evidence_sufficient:state[rank].remaining_evidence_sufficient,owner_disposition_is_own_decision:state[rank].owner_disposition_is_own_decision,wording_assistance_disclosure:state[rank].wording_assistance_disclosure,packet_sha256",
        "const rationale=document.createElement('label');": controls,
        "rationale.textContent='Evidence and limitations'": "rationale.textContent='Pair-specific rationale across temporal panels and trigger'",
        "panel.append(heading);const evidence=": "panel.append(heading);const notice=document.createElement('p');notice.setAttribute('role','note');notice.textContent=pair.human_review_notice;panel.append(notice);const evidence=",
        "const record={version:1,reviewer:": "const record={version:1,record_type:'batch05_targeted_semantic_clarification',governance_sha256:DATA.definition.governance_sha256,stop_for_prospective_scientific_decision:state.some(item=>item.disposition==='confirmed_same_content_or_derived_lineage'),reviewer:",
        "oulu-batch01-human-review.json": "oulu-batch05-targeted-clarification.json",
    }
    page = PAGE
    for before, after in replacements.items():
        if before not in page:
            raise ValueError("accepted PAGE adapter mismatch")
        page = page.replace(before, after)
    data = json.dumps({"definition": definition, "sha256": digest}).replace("<", "\\u003c")
    return page.replace("__DATA__", data)


def prepare(args: argparse.Namespace) -> dict:
    preflight_path = args.import_root.parent / "oulu_batch05_clarification_handoff_preflight_v1.json"
    governance_path = args.import_root.parent / "oulu_batch05_governance_clarification_v1.json"
    private_output(args.out_root, [args.import_root, args.review_root, preflight_path, governance_path])
    preflight = json.loads(preflight_path.read_bytes())
    private_output(args.out_root, [Path(name) for name in preflight["protected_snapshots"]])

    def verify_inputs() -> None:
        for name, expected in preflight["protected_snapshots"].items():
            folder = Path(name)
            actual = {str(path.relative_to(folder)): _sha256(path) for path in sorted(folder.rglob("*")) if path.is_file()}
            if actual != expected:
                raise ValueError("protected evidence drift")
        for name, digest in {**preflight["pinned_file_sha256"], **preflight["frozen_file_sha256"], **preflight["study_config_sha256"]}.items():
            if _sha256(Path(name)) != digest:
                raise ValueError("pinned authority/source/config drift")
        if _sha256(Path(__file__)) != preflight["runner_sha256"] or _sha256(governance_path) != preflight["governance_sha256"]:
            raise ValueError("clarification runner or governance drift")

    verify_inputs()
    check = preflight["import_CI"]
    if check["head_sha"] != "21a7ef1474829b8e11a2369700a6716155d3f1b2" or check["run_id"] != 38547153266 or check["job_id"] != 115795927764 or check["status"] != "completed" or check["conclusion"] != "success":
        raise ValueError("exact successful import CI required")
    public_path = ROOT / "results/phase1/oulu-human-review-batch05-v1.json"
    public = json.loads(public_path.read_bytes())
    if _sha256(public_path) != preflight["accepted_import_report_sha256"] or _sha256(args.import_root / "summary.json") != public["private_summary_sha256"] or _sha256(args.import_root / "lineage.json") != public["lineage_sha256"]:
        raise ValueError("accepted mechanical import drift")
    paths = sorted((args.import_root / "pairs").glob("*.json"))
    bundle = hashlib.sha256("".join(f"{path.name}:{_sha256(path)}\n" for path in paths).encode()).hexdigest()
    if len(paths) != 10 or bundle != public["human_record_bundle_sha256"]:
        raise ValueError("original imported human rows drift")
    previous_path = args.review_root / "review_definition.json"
    if _sha256(previous_path) != public["review_definition_sha256"]:
        raise ValueError("previous handoff definition drift")
    previous = json.loads(previous_path.read_bytes())
    if [pair["queue_rank"] for pair in previous["pairs"]] != list(range(40, 50)):
        raise ValueError("original batch05 scope required")
    if _sha256(ROOT / "docs/166-review-doc165-oulu-batch05-human-import.md") != preflight["review166_sha256"]:
        raise ValueError("Review166 authority drift")
    definition = {"version": 1, "state": "awaiting167_checkpoint_review_then_genuine_targeted_human_clarification", "pairs": [],
                  "review166_sha256": preflight["review166_sha256"], "governance_sha256": _sha256(governance_path),
                  "accepted_import_report_sha256": _sha256(public_path), "original_import_root": str(args.import_root.resolve()),
                  "previous_review_root": str(args.review_root.resolve()), "previous_review_definition_sha256": _sha256(previous_path),
                  "original_owner_input_sha256": public["human_input_sha256"], "human_record_bundle_sha256": bundle,
                  "preflight_sha256": _sha256(preflight_path), "preparation_code_sha256": _sha256(Path(__file__)),
                  "page_source_sha256": _sha256(ROOT / "scripts/prepare_oulu_owner_review.py"), "import_CI": check,
                  "target_ranks": list(TARGET_RANKS), "mandatory_clarification_ranks": list(MANDATORY_CLARIFICATION_RANKS),
                  "heightened_scrutiny_ranks": list(HEIGHTENED_SCRUTINY_RANKS), "human_fields_prefilled": False,
                  "earlier_AI_notes_initially_collapsed": True, "all_prior_human_answers_not_modified": True,
                  "independent_blinded_human_rationale_authorship_claimed": False, "no_answer_agreement_or_wording_quota": True,
                  "checkpoint_review_required_before_human_clarification": True, "formal_review_required_before_followup_import": True,
                  "requires_separate_six_rank_clarification_import": True, "semantic_reasoning_automatically_certified": False,
                  "no_automatic_effective_activation": True, "confirmed_action": "immediate_scientific_hard_stop",
                  "model_execution_authorized": False, "scientific_readiness": False}
    for rank in TARGET_RANKS:
        pair = previous["pairs"][rank - 40]
        row_path = args.import_root / "pairs" / f"{rank:06d}.json"
        row = json.loads(row_path.read_bytes())
        if row["queue_rank"] != rank or row["packet_sha256"] != pair["packet_sha256"] or row["reviewed_assets_sha256"] != pair["required_assets_sha256"] or row["effective_disposition_activated"] is not False:
            raise ValueError("original human row binding drift")
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
        identical = rank == 48
        if identical:
            rank47 = previous["pairs"][7]
            if {Path(name).name: digest for name, digest in pair["required_assets_sha256"].items()} != {Path(name).name: digest for name, digest in rank47["required_assets_sha256"].items()}:
                raise ValueError("rank48 evidence no longer identical to47")
        definition["pairs"].append({**pair, "required_assets_sha256": assets, "imported_human_record_sha256": _sha256(row_path),
                                    "human_review_notice": IDENTICAL_EVIDENCE_NOTICE if identical else VISIBILITY_LIMITS[rank] + SCRUTINY_NOTICE,
                                    "bound_images_identical_to_rank47": identical})
    write_immutable_record(args.out_root / "review_definition.json", definition)
    digest = _sha256(args.out_root / "review_definition.json")
    with (args.out_root / "index.html").open("x") as handle:
        handle.write(render_clarification(definition, digest))
    verify_inputs()
    result = {"version": 1, "status": "targeted_clarification_handoff_prepared_checkpoint_and_human_input_required",
              "queue_ranks": list(TARGET_RANKS), "pairs_prepared": 6, "required_bound_images": 18,
              "actual_human_clarifications": 0, "effective_dispositions_activated": 0, "accepted_current_total": 40,
              "review_definition_sha256": digest, "page_sha256": _sha256(args.out_root / "index.html"),
              "governance_sha256": _sha256(governance_path), "historical_inputs_unchanged": True,
              "rank48_identical_rank47_evidence_bound": True, "clean_ranks44_through47_reopened": False,
              "pair_specific_semantic_review_pending": True, "queue_continued": False,
              "model_execution_authorized": False, "scientific_readiness": False}
    write_immutable_record(args.out_root / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("import-root", "review-root", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        print(json.dumps(prepare(parser.parse_args()), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError):
        print("BATCH05 CLARIFICATION HANDOFF FAILED: no human reasoning or clearance manufactured", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())