#!/usr/bin/env python3
"""Prepare private human review; import only explicit bound human attestations."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.human_review import full_resolution_frames, validate_human_review
from fas.oulu import _sha256
from fas.visual import png_bytes, review_orders


def private_output(output: Path, sources: list[Path]) -> None:
    if output.exists() or output.is_symlink():
        raise ValueError("existing output")
    resolved = output.resolve()
    if any(resolved.is_relative_to(path.resolve()) or path.resolve().is_relative_to(resolved) for path in [ROOT, *sources]):
        raise ValueError("unsafe private output boundary")


def render_page(definition: dict, digest: str) -> str:
    data = json.dumps({"definition": definition, "sha256": digest}).replace("<", "\\u003c")
    return PAGE.replace("__DATA__", data)


def prepare(args: argparse.Namespace) -> dict:
    output = args.out_root.resolve()
    private_output(args.out_root, [args.packet_root, args.ai_root, args.audit_root, args.frozen_root, args.input_root, args.archive_records])
    public_path = ROOT / "results/phase1/oulu-visual-review-batch01-v1.json"
    accepted = json.loads(public_path.read_bytes())
    for name, digest in accepted["implementation_sha256"].items():
        if _sha256(ROOT / name) != digest:
            raise ValueError("accepted evidence implementation drift")
    if _sha256(ROOT / accepted["policy_file"]) != accepted["policy_sha256"]:
        raise ValueError("accepted visual policy drift")
    if _sha256(args.packet_root / "summary.json") != accepted["private_packet_summary_sha256"] or _sha256(args.ai_root / "summary.json") != accepted["private_review_summary_sha256"]:
        raise ValueError("accepted packet or AI summary drift")
    ai_paths = sorted((args.ai_root / "pairs").glob("*.json"))
    bundle = hashlib.sha256("".join(f"{path.name}:{_sha256(path)}\n" for path in ai_paths).encode()).hexdigest()
    if len(ai_paths) != 10 or bundle != accepted["observation_record_bundle_sha256"]:
        raise ValueError("AI proposal bundle drift")
    frozen_hashes = {path.name: _sha256(path) for path in args.frozen_root.iterdir()}
    if frozen_hashes != accepted["frozen_artifact_sha256"]:
        raise ValueError("frozen input drift")
    media_public = json.loads((ROOT / "results/phase1/oulu-per-video-media-audit-v1.json").read_bytes())
    media_paths = sorted((args.audit_root / "videos").glob("*.json"))
    media_bundle = hashlib.sha256("".join(f"{path.stem}:{_sha256(path)}\n" for path in media_paths).encode()).hexdigest()
    if len(media_paths) != 4950 or media_bundle != media_public["video_record_bundle_sha256"]:
        raise ValueError("accepted full frame bundle drift")
    pins = json.loads((ROOT / "results/phase1/oulu-archive-byte-pinning-v1.json").read_bytes())
    identities = {}
    for name, pin in pins["media_archives"].items():
        record_path = args.archive_records / (name + ".sha256.json")
        if _sha256(record_path) != pin["private_record_sha256"]:
            raise ValueError("archive record drift")
        identity = json.loads(record_path.read_bytes())["file_identity"]
        stat = (args.input_root / name).stat()
        actual = (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
        if actual != (identity["device"], identity["inode"], pin["byte_size"], identity["mtime_ns"], identity["ctime_ns"]):
            raise ValueError("archive identity drift")
        identities[name] = actual
    version = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    if version != json.loads((ROOT / "configs/environment_v1.yaml").read_bytes())["host_tools"]["ffmpeg_version_line"]:
        raise ValueError("research FFmpeg mismatch")
    definition = {"version": 1, "state": "awaiting_actual_owner_or_designated_human_review", "pairs": [],
                  "ai_review_root": str(args.ai_root.resolve()), "packet_root": str(args.packet_root.resolve()),
                  "protected_input_roots": [str(path.resolve()) for path in (args.packet_root, args.ai_root, args.audit_root, args.frozen_root, args.input_root, args.archive_records)],
                  "accepted_visual_report_sha256": _sha256(public_path), "ai_record_bundle_sha256": bundle,
                  "frozen_artifact_sha256": frozen_hashes, "review_sha256": _sha256(ROOT / "docs/116-review-doc115-oulu-visual-batch01.md"),
                  "preparation_code_sha256": _sha256(Path(__file__)), "validation_code_sha256": _sha256(ROOT / "src/fas/human_review.py"),
                  "human_dispositions_prefilled": False, "disagreement_rule": "preserve_both_reconcile_before_clearance",
                  "confirmed_cross_role_action": "stop_for_explicit_prospective_scientific_decision",
                  "model_execution_authorized": False, "scientific_readiness": False}
    output.mkdir(parents=True)
    full_resolution_count = 0
    for rank, ai_path in enumerate(ai_paths):
        ai = json.loads(ai_path.read_bytes())
        packet_path = args.packet_root / "pairs" / f"{rank:06d}" / "packet.json"
        packet = json.loads(packet_path.read_bytes())
        if ai["queue_rank"] != rank or ai["packet_sha256"] != _sha256(packet_path):
            raise ValueError("pair packet identity drift")
        assets, full_assets = {}, []
        for name, digest in packet["image_sha256"].items():
            source = packet_path.parent / name
            if Path(name).name != name or _sha256(source) != digest:
                raise ValueError("viewed image drift")
            target = output / "assets" / f"{rank:06d}" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with source.open("rb") as handle, target.open("xb") as destination:
                shutil.copyfileobj(handle, destination)
            assets[str(target.relative_to(output))] = _sha256(target)
        if ai["disposition"] == "uncertain_insufficient_evidence":
            for side, trigger_order in zip(("left", "right"), packet["trigger_decode_orders"], strict=True):
                identity = packet["candidate"][side]
                media = json.loads((args.audit_root / "videos" / (identity + ".json")).read_bytes())
                orders = sorted(set(review_orders(media["frame_count"]) + [trigger_order]))
                with tarfile.open(args.input_root / media["media_archive"], "r:") as archive:
                    member = archive.getmember(media["media_relpath"])
                    if not member.isfile() or member.size != media["byte_size"]:
                        raise ValueError("full resolution payload metadata drift")
                    with tempfile.TemporaryDirectory(prefix="fas-human-full-", dir=output) as directory:
                        video_path = Path(directory) / "media.avi"
                        with archive.extractfile(member) as source, video_path.open("wb") as destination:
                            shutil.copyfileobj(source, destination, length=1024 * 1024)
                        if _sha256(video_path) != media["media_sha256"]:
                            raise ValueError("full resolution payload digest drift")
                        frames = full_resolution_frames(video_path, media, orders)
                for order, rgb in frames.items():
                    target = output / "assets" / f"{rank:06d}" / f"{side}_{order:06d}_full.png"
                    with target.open("xb") as handle:
                        handle.write(png_bytes(rgb))
                    relative = str(target.relative_to(output))
                    assets[relative] = _sha256(target)
                    full_assets.append({"path": relative, "side": side, "decode_order": order, "rgb_sha256": media["frame_index"][order]["rgb_sha256"]})
                    full_resolution_count += 1
        definition["pairs"].append({"queue_rank": rank, "packet_sha256": _sha256(packet_path), "ai_record_sha256": _sha256(ai_path),
                                    "ai_disposition": ai["disposition"], "ai_observations": ai["observations"], "ai_limitation": ai["limitation"],
                                    "required_assets_sha256": assets, "full_resolution": full_assets})
    for name, expected in identities.items():
        stat = (args.input_root / name).stat()
        if (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns) != expected:
            raise ValueError("archive changed during export")
    if {path.name: _sha256(path) for path in args.frozen_root.iterdir()} != frozen_hashes:
        raise ValueError("frozen inputs changed during export")
    write_immutable_record(output / "review_definition.json", definition)
    digest = _sha256(output / "review_definition.json")
    with (output / "index.html").open("x") as handle:
        handle.write(render_page(definition, digest))
    result = {"version": 1, "status": "human_review_required_not_completed", "pairs_prepared": 10, "actual_human_reviews": 0,
              "full_resolution_frames": full_resolution_count, "full_resolution_pair_count": 1,
              "review_definition_sha256": digest, "page_sha256": _sha256(output / "index.html"),
              "frozen_inputs_unchanged": True, "ai_ledger_unchanged": True, "queue_continued": False,
              "model_execution_authorized": False, "scientific_readiness": False}
    write_immutable_record(output / "summary.json", result)
    return result


def import_review(args: argparse.Namespace) -> dict:
    private_output(args.out_root, [args.review_root, args.human_input])
    public = json.loads((ROOT / "results/phase1/oulu-human-review-handoff-v1.json").read_bytes())
    path = args.review_root / "review_definition.json"
    digest = _sha256(path)
    if digest != public["review_definition_sha256"]:
        raise ValueError("published review definition drift")
    definition = json.loads(path.read_bytes())
    private_output(args.out_root, [args.review_root, args.human_input, *(Path(name) for name in definition["protected_input_roots"])])
    for pair in definition["pairs"]:
        for name, expected in pair["required_assets_sha256"].items():
            if _sha256(args.review_root / name) != expected:
                raise ValueError("human reviewed asset drift")
        ai_path = Path(definition["ai_review_root"]) / "pairs" / f"{pair['queue_rank']:06d}.json"
        if _sha256(ai_path) != pair["ai_record_sha256"]:
            raise ValueError("original AI proposal drift")
    human = json.loads(args.human_input.read_bytes())
    outcomes = validate_human_review(human, {**definition, "sha256": digest})
    write_immutable_record(args.out_root / "human_input.json", human)
    for row in outcomes:
        write_immutable_record(args.out_root / "pairs" / f"{row['queue_rank']:06d}.json", row)
    result = {"version": 1, "status": "bound_human_attestations_recorded_no_automatic_clearance", "human_dispositions": len(outcomes),
              "input_sha256": _sha256(args.human_input), "review_definition_sha256": digest,
              "disposition_counts": dict(Counter(row["disposition"] for row in outcomes)), "disagreements": sum(row["disagreement"] for row in outcomes),
              "stop_for_prospective_scientific_decision": any(row["stop_for_prospective_scientific_decision"] for row in outcomes),
              "human_authorship": "reviewer_attestation_not_independently_authenticated", "ai_ledger_unchanged": True,
              "queue_continued": False, "model_execution_authorized": False, "scientific_readiness": False}
    write_immutable_record(args.out_root / "summary.json", result)
    return result


PAGE = r'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OULU Human Review · Batch 01</title>
<style>
:root{--ink:#17221e;--line:#cad3ce;--accent:#087c63;--paper:#f3f6f4}*{box-sizing:border-box}body{margin:0;color:var(--ink);background:var(--paper);font:15px Georgia,serif;letter-spacing:0}header{padding:16px 24px;background:#fff;border-bottom:1px solid var(--line);display:flex;gap:20px;align-items:center;flex-wrap:wrap}h1{font-size:22px;margin:0}main{display:grid;grid-template-columns:190px minmax(0,1fr);min-height:90vh}nav{padding:18px;border-right:1px solid var(--line)}nav button{display:block;width:100%;margin:0 0 8px;text-align:left}button,input,select,textarea{font:inherit;letter-spacing:0}button{padding:9px 12px;border:1px solid var(--line);border-radius:4px;background:#fff;cursor:pointer}button[aria-current=true]{border-color:var(--accent);color:var(--accent)}button:disabled{opacity:.4;cursor:default}section{padding:20px;min-width:0}h2{font-size:20px}img{display:block;max-width:100%;height:auto;background:#ddd}figure{margin:0 0 16px}figcaption{font-size:13px;margin:6px 0}.panel{width:100%}.evidence{border-bottom:1px solid var(--line);padding-bottom:10px}.full{display:flex;flex-wrap:wrap;gap:8px}.full a{width:90px}.full img{width:90px}label{display:block;margin:12px 0}select,input[type=text]{padding:8px;max-width:100%;border:1px solid var(--line);border-radius:4px}textarea{width:100%;min-height:100px;padding:10px;border:1px solid var(--line);border-radius:4px}details{margin:16px 0}summary{cursor:pointer}#status{font:14px Georgia,serif;color:#674019}dialog{border:1px solid var(--line);width:min(1100px,96vw);height:94vh;padding:14px}dialog img{max-width:none;width:auto;height:auto}dialog .scroll{height:calc(100% - 50px);overflow:auto}dialog button{margin-bottom:10px}@media(max-width:680px){main{grid-template-columns:1fr}nav{display:flex;gap:6px;overflow:auto;border-right:0;border-bottom:1px solid var(--line)}nav button{min-width:100px;width:auto}header,section{padding:14px}h1{font-size:19px}}
</style>
<header><h1>OULU · Human Review · Batch 01</h1><span id="status"></span><button id="export" disabled>Export Human Review</button></header>
<main><nav id="queue" aria-label="Pair queue"></nav><section><label>Reviewer ID <input id="reviewer" type="text" autocomplete="off"></label><label>Reviewer <select id="kind"><option value="owner_human">Owner (human)</option><option value="designated_human">Designated reviewer (human)</option></select></label><div id="pair"></div></section></main>
<dialog id="zoom"><button id="close" title="Close full-resolution image">Close</button><div class="scroll"><img id="large" alt="Full-resolution review frame"></div></dialog>
<script>
const DATA=__DATA__;const pairs=DATA.definition.pairs;const state=pairs.map(()=>({disposition:'',rationale:'',personally_reviewed:false,viewed:new Set()}));let current=0;
const panel=document.getElementById('pair'),queue=document.getElementById('queue');
function complete(item,pair){return item.disposition&&item.rationale.trim()&&item.personally_reviewed&&Object.keys(pair.required_assets_sha256).every(name=>item.viewed.has(name))}
function update(){const count=state.filter((item,rank)=>complete(item,pairs[rank])).length;document.getElementById('status').textContent=count+' / 10 human dispositions';document.getElementById('export').disabled=count!==10||!document.getElementById('reviewer').value.trim()}
function asset(name,caption,small=false){const rank=current,figure=document.createElement('figure'),image=document.createElement('img'),label=document.createElement('figcaption');image.src=name;image.alt=caption;label.textContent=caption;image.className=small?'small':'panel';image.tabIndex=0;image.setAttribute('role','button');image.title='Open original-resolution evidence';const open=()=>{document.getElementById('large').src=name;document.getElementById('zoom').showModal()};image.addEventListener('click',open);image.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();open()}});image.addEventListener('load',()=>{state[rank].viewed.add(name);update()},{once:true});figure.append(image,label);return figure}
function show(rank){current=rank;const pair=pairs[rank],item=state[rank];panel.replaceChildren();queue.querySelectorAll('button').forEach((button,index)=>button.setAttribute('aria-current',index===rank?'true':'false'));const heading=document.createElement('h2');heading.textContent='Pair '+(rank+1)+' · Cross-role / conflicting-label';panel.append(heading);const evidence=document.createElement('div');evidence.className='evidence';Object.keys(pair.required_assets_sha256).filter(name=>!name.endsWith('_full.png')).forEach(name=>evidence.append(asset(name,name.split('/').pop())));panel.append(evidence);if(pair.full_resolution.length){const title=document.createElement('h3');title.textContent='Full-resolution temporal evidence';panel.append(title);pair.full_resolution.forEach(frame=>panel.append(asset(frame.path,frame.side+' · frame '+frame.decode_order)))}const details=document.createElement('details'),summary=document.createElement('summary'),notes=document.createElement('div');summary.textContent='Earlier AI proposal (not a final disposition)';notes.textContent=pair.ai_disposition+' — '+pair.ai_observations.join(' ')+' '+pair.ai_limitation;details.append(summary,notes);panel.append(details);const label=document.createElement('label');label.textContent='Your disposition ';const select=document.createElement('select');[['','Select disposition'],['confirmed_same_content_or_derived_lineage','Confirmed same / derived rendered content'],['rejected_false_positive','Rejected screen false positive'],['uncertain_insufficient_evidence','Uncertain — insufficient evidence']].forEach(([value,text])=>select.add(new Option(text,value)));select.value=item.disposition;select.addEventListener('change',()=>{item.disposition=select.value;update()});label.append(select);panel.append(label);const rationale=document.createElement('label');rationale.textContent='Evidence and limitations';const text=document.createElement('textarea');text.value=item.rationale;text.addEventListener('input',()=>{item.rationale=text.value;update()});rationale.append(text);panel.append(rationale);const inspected=document.createElement('label'),check=document.createElement('input');check.type='checkbox';check.checked=item.personally_reviewed;check.addEventListener('change',()=>{item.personally_reviewed=check.checked;update()});inspected.append(check,document.createTextNode(' I personally inspected the bound evidence for this pair.'));panel.append(inspected);update()}
pairs.forEach((pair,rank)=>{const button=document.createElement('button');button.textContent='Pair '+(rank+1);button.addEventListener('click',()=>show(rank));queue.append(button)});document.getElementById('reviewer').addEventListener('input',update);document.getElementById('close').addEventListener('click',()=>document.getElementById('zoom').close());
document.getElementById('export').addEventListener('click',()=>{const record={version:1,reviewer:{kind:document.getElementById('kind').value,id:document.getElementById('reviewer').value.trim(),personally_inspected_bound_evidence:true},review_definition_sha256:DATA.sha256,reviewed_at_utc:new Date().toISOString(),pairs:pairs.map((pair,rank)=>({queue_rank:rank,packet_sha256:pair.packet_sha256,reviewed_assets_sha256:pair.required_assets_sha256,personally_reviewed:state[rank].personally_reviewed,disposition:state[rank].disposition,rationale:state[rank].rationale,capture_provenance_certified:false}))};const blob=new Blob([JSON.stringify(record,null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download='oulu-batch01-human-review.json';link.click();URL.revokeObjectURL(url)});show(0);
</script></html>'''


def main() -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_subparsers(dest="mode", required=True)
    preparation = modes.add_parser("prepare")
    for name in ("input-root", "archive-records", "audit-root", "packet-root", "ai-root", "frozen-root", "out-root"):
        preparation.add_argument("--" + name, type=Path, required=True)
    importer = modes.add_parser("import")
    for name in ("review-root", "human-input", "out-root"):
        importer.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    try:
        result = prepare(args) if args.mode == "prepare" else import_review(args)
        print(json.dumps(result, sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError, tarfile.TarError):
        print("HUMAN REVIEW HANDOFF FAILED: bound input or private output invalid; no human review fabricated", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())