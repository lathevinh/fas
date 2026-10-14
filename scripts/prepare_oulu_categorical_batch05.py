#!/usr/bin/env python3
"""Prepare categorical-only batch05 review without importing owner decisions."""

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
from prepare_oulu_clarification_batch05 import MANDATORY_CLARIFICATION_RANKS, TARGET_RANKS
from prepare_oulu_owner_batch05 import VISIBILITY_LIMITS
from prepare_oulu_owner_review import PAGE, private_output

CATEGORICAL_RULES = [
    {"evidence_sufficient": False, "same_or_derived_content": None, "disposition": "uncertain_insufficient_evidence"},
    {"evidence_sufficient": True, "same_or_derived_content": True, "disposition": "confirmed_same_content_or_derived_lineage"},
    {"evidence_sufficient": True, "same_or_derived_content": False, "disposition": "rejected_false_positive"},
]
NOTICE = " Insufficient evidence preserves uncertainty; same or derived content requires a scientific stop. No answer or agreement is prescribed."
IDENTICAL_EVIDENCE_NOTICE = (
    "All three bound images are byte-identical to rank47. Prior personal inspection "
    "of those identical images may be relied upon; new visual inspection is not "
    "required solely because this is a separate candidate. Affirm your own rank48 "
    "categorical decision. No earlier answer is copied and no disposition is prescribed."
)

SCRIPT = r'''<script>
const DATA=__DATA__;
const pairs=DATA.definition.pairs;
const state=pairs.map(()=>({evidence_sufficient:null,same_or_derived_content:null,personal_inspection_attested:null,owner_decision_attested:null,submitted:false,viewed:new Set()}));
let current=0;
const panel=document.getElementById('pair'),queue=document.getElementById('queue');
function deriveDisposition(item){
    const rule=DATA.definition.categorical_rules.find(rule=>rule.evidence_sufficient===item.evidence_sufficient&&rule.same_or_derived_content===item.same_or_derived_content);
    return rule?rule.disposition:null;
}
function complete(item,pair){
    const names=Object.keys(pair.required_assets_sha256);
    return deriveDisposition(item)!==null&&item.personal_inspection_attested===true&&item.owner_decision_attested===true&&names.length===3&&names.every(name=>item.viewed.has(name));
}
function exportReady(){return state.every((item,rank)=>item.submitted===true&&complete(item,pairs[rank]))&&document.getElementById('reviewer').value.trim()!==''}
function update(){
    const count=state.filter((item,rank)=>item.submitted===true&&complete(item,pairs[rank])).length;
    document.getElementById('status').textContent=count+' / '+pairs.length+' categorical judgments';
    document.getElementById('export').disabled=!exportReady();
    const submit=document.getElementById('submit-pair');if(submit)submit.disabled=!complete(state[current],pairs[current]);
    const notes=document.getElementById('ai-context');if(notes){notes.hidden=state[current].submitted!==true||!complete(state[current],pairs[current]);if(notes.hidden)notes.open=false}
}
function asset(name,caption){
    const rank=current,figure=document.createElement('figure'),image=document.createElement('img'),label=document.createElement('figcaption');
    image.src=name;image.alt=caption;image.className='panel';image.tabIndex=0;image.setAttribute('role','button');image.title='Open original-resolution evidence';label.textContent=caption;
    const open=()=>{document.getElementById('large').src=name;document.getElementById('zoom').showModal()};
    image.addEventListener('click',open);image.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();open()}});
    image.addEventListener('load',()=>{if(image.naturalWidth>0&&image.naturalHeight>0)state[rank].viewed.add(name);update()},{once:true});
    image.addEventListener('error',()=>{state[rank].viewed.delete(name);state[rank].submitted=false;update()});
    figure.append(image,label);return figure;
}
function question(field,title){
    const group=document.createElement('fieldset'),legend=document.createElement('legend');legend.textContent=title;group.append(legend);
    for(const [answer,text] of [[true,'Yes'],[false,'No']]){
        const label=document.createElement('label'),input=document.createElement('input');input.type='radio';input.name=field;input.value=String(answer);input.checked=state[current][field]===answer;
        input.addEventListener('change',()=>{state[current][field]=answer;state[current].submitted=false;if(field==='evidence_sufficient')state[current].same_or_derived_content=null;show(current)});
        label.append(input,text);group.append(label);
    }
    return group;
}
function show(rank){
    current=rank;const pair=pairs[rank],item=state[rank];panel.replaceChildren();
    queue.querySelectorAll('button').forEach((button,index)=>button.setAttribute('aria-current',index===rank?'true':'false'));
    const heading=document.createElement('h2');heading.textContent='Queue '+pair.queue_rank+' - Cross-role / conflicting-label';panel.append(heading);
    const notice=document.createElement('p');notice.setAttribute('role','note');notice.textContent=pair.human_review_notice;panel.append(notice);
    const evidence=document.createElement('div');evidence.className='evidence';Object.keys(pair.required_assets_sha256).forEach(name=>evidence.append(asset(name,name.split('/').pop())));panel.append(evidence);
    panel.append(question('evidence_sufficient','Is the bound evidence sufficient for a content-lineage judgment?'));
    if(item.evidence_sufficient===true)panel.append(question('same_or_derived_content','Does the pair show the same rendered content or content derived from the same source?'));
    panel.append(question('personal_inspection_attested','Did you personally inspect the bound evidence for this pair?'));
    panel.append(question('owner_decision_attested','Is this categorical disposition your own decision?'));
    const submit=document.createElement('button');submit.id='submit-pair';submit.textContent='Submit pair judgment';submit.addEventListener('click',()=>{if(complete(item,pair)){item.submitted=true;update()}});panel.append(submit);
    const details=document.createElement('details'),summary=document.createElement('summary'),notes=document.createElement('div');details.id='ai-context';details.hidden=true;
    summary.textContent='Earlier AI proposal (not a final disposition)';notes.textContent=pair.ai_disposition+' - '+pair.ai_observations.join(' ')+' '+pair.ai_limitation;details.append(summary,notes);panel.append(details);update();
}
function pairRecord(item,pair){
    const disposition=deriveDisposition(item);
    return {queue_rank:pair.queue_rank,packet_sha256:pair.packet_sha256,imported_human_record_sha256:pair.imported_human_record_sha256,reviewed_assets_sha256:pair.required_assets_sha256,
        evidence_sufficient:item.evidence_sufficient,same_or_derived_content:item.same_or_derived_content,personal_inspection_attested:item.personal_inspection_attested,owner_decision_attested:item.owner_decision_attested,
        disposition:disposition,bound_images_identical_to_rank47:pair.bound_images_identical_to_rank47,identical_evidence_reference_rank:pair.bound_images_identical_to_rank47?47:null,
        capture_provenance_certified:false,stop_for_prospective_scientific_decision:disposition==='confirmed_same_content_or_derived_lineage'};
}
function buildRecord(){
    const rows=pairs.map((pair,rank)=>pairRecord(state[rank],pair));
    return {version:1,record_type:'batch05_targeted_categorical_review',reviewer:{kind:document.getElementById('kind').value,id:document.getElementById('reviewer').value.trim(),personally_inspected_bound_evidence:true},
        review_definition_sha256:DATA.sha256,governance_sha256:DATA.definition.governance_sha256,review168_sha256:DATA.definition.review168_sha256,reviewed_at_utc:new Date().toISOString(),
        stop_for_prospective_scientific_decision:rows.some(row=>row.stop_for_prospective_scientific_decision),pairs:rows};
}
pairs.forEach((pair,rank)=>{const button=document.createElement('button');button.textContent='Queue '+pair.queue_rank;button.addEventListener('click',()=>show(rank));queue.append(button)});
document.getElementById('reviewer').addEventListener('input',update);document.getElementById('close').addEventListener('click',()=>document.getElementById('zoom').close());
document.getElementById('export').addEventListener('click',()=>{
    if(!exportReady())return;
    const blob=new Blob([JSON.stringify(buildRecord(),null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download='oulu-batch05-categorical-review.json';link.click();URL.revokeObjectURL(url);
});show(0);
</script>'''


def render_categorical(definition: dict, digest: str) -> str:
    pairs = definition["pairs"]
    if [pair["queue_rank"] for pair in pairs] != list(TARGET_RANKS) or any(type(pair["queue_rank"]) is not int for pair in pairs):
        raise ValueError("exact targeted batch05 integer ranks required")
    if not definition.get("governance_sha256") or not definition.get("review168_sha256"):
        raise ValueError("governance and Review168 bindings required")
    if json.dumps(definition.get("categorical_rules"), sort_keys=True) != json.dumps(CATEGORICAL_RULES, sort_keys=True):
        raise ValueError("strict categorical mapping required")
    for pair in pairs:
        rank = pair["queue_rank"]
        expected = IDENTICAL_EVIDENCE_NOTICE if rank == 48 else VISIBILITY_LIMITS[rank] + NOTICE
        if not pair.get("imported_human_record_sha256") or pair.get("human_review_notice") != expected:
            raise ValueError("original human row and neutral categorical notice required")
        if pair.get("bound_images_identical_to_rank47") is not (rank == 48):
            raise ValueError("rank48 identical-evidence binding required")
        assets = pair["required_assets_sha256"]
        if len(assets) != 3 or {Path(name).name for name in assets} != {"temporal_a.png", "temporal_b.png", "trigger.png"}:
            raise ValueError("exact three historical assets required")
    shell = PAGE.split("<script>", 1)[0].replace("Batch 01", "Batch 05 Categorical Review")
    shell = shell.replace("</style>", "fieldset{margin:14px 0;padding:12px;border:1px solid var(--line);min-width:0}legend{max-width:100%;overflow-wrap:anywhere}fieldset label{display:inline-flex;gap:8px;align-items:center;margin:8px 24px 0 0}[hidden]{display:none!important}</style>")
    data = json.dumps({"definition": definition, "sha256": digest}).replace("<", "\\u003c")
    return shell + SCRIPT.replace("__DATA__", data) + PAGE.split("</script>", 1)[1]


def prepare(args: argparse.Namespace) -> dict:
    preflight_path = args.review_root.parent / "oulu_batch05_categorical_handoff_preflight_v1.json"
    private_output(args.out_root, [args.review_root, preflight_path])
    preflight = json.loads(preflight_path.read_bytes())
    private_output(args.out_root, [Path(name) for name in preflight["protected_snapshots"]])

    def verify_inputs() -> None:
        for name, expected in preflight["protected_snapshots"].items():
            root = Path(name)
            actual = {str(path.relative_to(root)): _sha256(path) for path in sorted(root.rglob("*")) if path.is_file()}
            if actual != expected:
                raise ValueError("protected evidence drift")
        for name, digest in {**preflight["pinned_file_sha256"], **preflight["study_config_sha256"], **preflight["frozen_file_sha256"]}.items():
            if _sha256(Path(name)) != digest:
                raise ValueError("pinned authority/source/config drift")
        if _sha256(Path(__file__)) != preflight["runner_sha256"] or str(args.review_root.resolve()) != preflight["source_review_root"]:
            raise ValueError("categorical runner or source root drift")

    verify_inputs()
    check = preflight["handoff167_CI"]
    if check["head_sha"] != "de75c0b5a7dc91e58b4a74db8792fc6fcbf884e0" or check["run_id"] != 38550598516 or check["job_id"] != 115807325949 or check["status"] != "completed" or check["conclusion"] != "success":
        raise ValueError("exact successful167 CI required")
    if preflight["human_input_collection_authorized"] is not False or preflight["import_authorized"] is not False:
        raise ValueError("preparation-only authority required")
    review_path = ROOT / "docs/168-review-doc167-oulu-batch05-clarification-handoff.md"
    public_path = ROOT / "results/phase1/oulu-clarification-handoff-batch05-v1.json"
    public = json.loads(public_path.read_bytes())
    if _sha256(review_path) != preflight["review168_sha256"] or _sha256(public_path) != preflight["handoff167_report_sha256"]:
        raise ValueError("Review168 or accepted technical report drift")
    previous_path = args.review_root / "review_definition.json"
    if _sha256(previous_path) != public["review_definition_sha256"] or _sha256(args.review_root / "index.html") != public["page_sha256"] or _sha256(args.review_root / "summary.json") != public["private_summary_sha256"]:
        raise ValueError("historical167 handoff drift")
    previous = json.loads(previous_path.read_bytes())
    if [pair["queue_rank"] for pair in previous["pairs"]] != list(TARGET_RANKS):
        raise ValueError("exact six historical targets required")
    governance_path = args.review_root.parent / "oulu_batch05_governance_clarification_v1.json"
    if _sha256(governance_path) != previous["governance_sha256"]:
        raise ValueError("accepted additive governance drift")
    supplied_path = args.review_root / "oulu-batch05-targeted-clarification.json"
    if _sha256(supplied_path) != preflight["received_old_form_input_sha256"]:
        raise ValueError("received old-form input drift")
    definition = {
        "version": 1, "state": "awaiting169_form_review_before_new_categorical_human_input", "pairs": [],
        "review168_sha256": _sha256(review_path), "governance_sha256": _sha256(governance_path),
        "source_review_root": str(args.review_root.resolve()), "source_review_definition_sha256": _sha256(previous_path),
        "handoff167_report_sha256": _sha256(public_path), "handoff167_CI": check,
        "original_import_root": previous["original_import_root"], "original_owner_input_sha256": previous["original_owner_input_sha256"],
        "human_record_bundle_sha256": previous["human_record_bundle_sha256"],
        "received_old_form_input_sha256": _sha256(supplied_path), "received_old_form_input_imported": False,
        "old_form_answers_converted_or_prefilled": False, "preflight_sha256": _sha256(preflight_path),
        "preparation_code_sha256": _sha256(Path(__file__)), "page_source_sha256": _sha256(ROOT / "scripts/prepare_oulu_owner_review.py"),
        "target_ranks": list(TARGET_RANKS), "mandatory_clarification_ranks": list(MANDATORY_CLARIFICATION_RANKS),
        "heightened_scrutiny_ranks": [40, 41, 42, 43, 49], "categorical_rules": CATEGORICAL_RULES,
        "required_human_pair_fields": ["evidence_sufficient", "same_or_derived_content", "personal_inspection_attested", "owner_decision_attested"],
        "human_fields_prefilled": False, "human_prose_required": False, "per_pair_wording_disclosure_required": False,
        "AI_context_hidden_until_pair_submission": True, "fully_blinded_human_review_claimed": False,
        "AI_generated_descriptive_prose_created": False, "historical_AI_wording_governance_unchanged": True,
        "checkpoint_review_required_before_new_human_input": True, "formal_review_required_before_followup_import": True,
        "requires_separate_categorical_importer": True, "no_automatic_effective_activation": True,
        "confirmed_action": "immediate_scientific_hard_stop", "model_execution_authorized": False, "scientific_readiness": False,
    }
    for pair in previous["pairs"]:
        rank = pair["queue_rank"]
        row_path = Path(previous["original_import_root"]) / "pairs" / f"{rank:06d}.json"
        row = json.loads(row_path.read_bytes())
        if _sha256(row_path) != pair["imported_human_record_sha256"] or row["packet_sha256"] != pair["packet_sha256"] or row["reviewed_assets_sha256"] != pair["required_assets_sha256"] or row["effective_disposition_activated"] is not False:
            raise ValueError("bound original import drift")
        if rank == 48:
            original = json.loads((Path(previous["previous_review_root"]) / "review_definition.json").read_bytes())
            rank47 = original["pairs"][7]
            if rank47["queue_rank"] != 47 or {Path(name).name: digest for name, digest in pair["required_assets_sha256"].items()} != {Path(name).name: digest for name, digest in rank47["required_assets_sha256"].items()}:
                raise ValueError("rank48 evidence no longer identical to47")
        assets = {}
        for name, digest in pair["required_assets_sha256"].items():
            source = (args.review_root / name).resolve()
            if not source.is_relative_to(args.review_root.resolve()) or _sha256(source) != digest:
                raise ValueError("bound historical image drift")
            target = args.out_root / "assets" / f"{rank:06d}" / Path(name).name
            target.parent.mkdir(parents=True, exist_ok=True)
            with source.open("rb") as handle, target.open("xb") as destination:
                shutil.copyfileobj(handle, destination)
            if _sha256(target) != digest:
                raise ValueError("copied image drift")
            assets[str(target.relative_to(args.out_root))] = digest
        definition["pairs"].append({**pair, "required_assets_sha256": assets,
                                    "human_review_notice": IDENTICAL_EVIDENCE_NOTICE if rank == 48 else VISIBILITY_LIMITS[rank] + NOTICE})
    render_categorical(definition, "pending")
    write_immutable_record(args.out_root / "review_definition.json", definition)
    digest = _sha256(args.out_root / "review_definition.json")
    with (args.out_root / "index.html").open("x") as handle:
        handle.write(render_categorical(definition, digest))
    verify_inputs()
    result = {
        "version": 1, "status": "categorical_handoff_prepared_review_required_before_human_use", "queue_ranks": list(TARGET_RANKS),
        "pairs_prepared": 6, "required_bound_images": 18, "actual_categorical_human_reviews": 0, "effective_dispositions_activated": 0,
        "accepted_current_total": 40, "review_definition_sha256": digest, "page_sha256": _sha256(args.out_root / "index.html"),
        "governance_sha256": _sha256(governance_path), "received_old_form_input_sha256": _sha256(supplied_path),
        "received_old_form_input_imported": False, "old_form_answers_converted_or_prefilled": False,
        "human_prose_required": False, "historical_inputs_unchanged": True, "rank48_identical_rank47_evidence_bound": True,
        "clean_ranks44_through47_reopened": False, "pair_specific_semantic_review_pending": True,
        "queue_continued": False, "model_execution_authorized": False, "scientific_readiness": False,
    }
    write_immutable_record(args.out_root / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("review-root", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        print(json.dumps(prepare(parser.parse_args()), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError):
        print("BATCH05 CATEGORICAL HANDOFF FAILED: no owner decisions imported or manufactured", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())