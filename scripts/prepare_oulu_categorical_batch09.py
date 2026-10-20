#!/usr/bin/env python3
"""Prepare the Review226 handoff without collecting human answers."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.human_review import DISPOSITIONS
from fas.oulu import _sha256
from import_oulu_categorical_batch08 import verify_preservation
from prepare_oulu_categorical_batch07 import CATEGORICAL_RULES, NOTICE, SCRIPT as PREVIOUS_SCRIPT, is_digest
from prepare_oulu_owner_review import PAGE, private_output
from prepare_oulu_visual_batch05 import bundle

TARGET_RANKS = tuple(range(80, 85))
REVIEW_FILE = "docs/226-review-doc225-oulu-batch09-ai-proposals.md"
REVIEW_SHA256 = "0f12ab2e39a40ec6bc34f9e9b8b97fa426d23dca0e76d2c74438f8d8e6274d80"
AI_REPORT_FILE = "results/phase1/oulu-visual-review-batch09-v1.json"
AI_REPORT_SHA256 = "1feb416f464ed40581a08d7fcfa3a50c088580a059f1e0f664a52fdb95886216"
AI_DOCUMENT_FILE = "docs/225-review-response-doc224-oulu-batch09-ai-proposals.md"
AI_DOCUMENT_SHA256 = "b555a88356b0954eef09363994306fbe4b505e03f7afeb6653db8080bf924444"
PACKET_REPORT_FILE = "results/phase1/oulu-batch09-packet-retry223-v1.json"
PACKET_REPORT_SHA256 = "ddf60c68013c3065ccc420466778ee93fbc0493a56242110821ac49200336712"
OLD_TEST_SHA256 = "9a2b74dd70b1a2e6a8abc5181eda3882858484cee847322585d9b8551634145b"
OLD_TEST_AST_SHA256 = "01e0815e5a9d273f534a3dc2e525018eee71b44aceaf411aedbbb13d1791fa6b"
NEW_TEST_METHOD = "test_batch09_categorical_handoff_review226_blank_controls_and_provenance"
SOURCE225_CI = {"head_sha": "e29bf1aaf399d59869f44c8bd84d66d3ab9bbd8b", "run_id": 39371116634, "job_id": 118458973475,
                "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success",
                "listed_successful_steps": 12, "all_steps_success": True}
SCRIPT = PREVIOUS_SCRIPT.replace("review194", "review226").replace("batch07", "batch09").replace(
    "accepted_AI_report_sha256:DATA.definition.accepted_AI_report_sha256",
    "accepted_AI_report_sha256:DATA.definition.accepted_AI_report_sha256,accepted_AI_document_sha256:DATA.definition.accepted_AI_document_sha256,observation_input_sha256:DATA.definition.observation_input_sha256,accepted_packet_report_sha256:DATA.definition.accepted_packet_report_sha256,source_packet_lineage_sha256:DATA.definition.source_packet_lineage_sha256,source_packet_summary_sha256:DATA.definition.source_packet_summary_sha256,dependence_sha256:DATA.definition.dependence_sha256",
).replace("ai_record_sha256:pair.ai_record_sha256", "ai_record_sha256:pair.ai_record_sha256,source_sampling_provenance_sha256:pair.source_sampling_provenance_sha256")


def structured_digest(record: dict) -> str:
    return hashlib.sha256(json.dumps(record, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def human_notice(rank: int, dependence: dict) -> str:
    reuse = [ranks for ranks in dependence["exact_reused_video_rank_groups"].values() if rank in ranks]
    correlated = [group["ranks"] for group in dependence["visually_correlated_configuration_rank_groups"] if rank in group["ranks"]]
    notice = "Sampling, near-static views, exposure and thumbnail resolution limit unsampled or hidden regions. "
    if reuse:
        notice += "An exact source video is reused across ranks " + "; ".join(", ".join(map(str, ranks)) for ranks in reuse) + "; these rows are dependent. "
    if correlated:
        notice += "Configurations recur across ranks " + "; ".join(", ".join(map(str, ranks)) for ranks in correlated) + "; this is correlated context, not independent corroboration. "
    return notice + NOTICE


def verify_authority(preflight: dict) -> None:
    expected = {"checkpoint": 227, "review226_sha256": REVIEW_SHA256, "accepted_AI_report_sha256": AI_REPORT_SHA256,
                "accepted_AI_document_sha256": AI_DOCUMENT_SHA256, "accepted_packet_report_sha256": PACKET_REPORT_SHA256}
    if any(type(preflight.get(field)) is not type(value) or preflight[field] != value for field, value in expected.items()):
        raise ValueError("exact Review226 and original225/223 authority required")
    ranks = preflight.get("queue_ranks", [])
    if ranks != list(TARGET_RANKS) or any(type(rank) is not int for rank in ranks):
        raise ValueError("exact integer ranks80..84 required")
    for field in ("human_input_collection_authorized", "import_authorized", "effective_activation_authorized", "model_execution_authorized", "scientific_readiness"):
        if preflight.get(field) is not False:
            raise ValueError("preparation-only authority required")
    check = preflight["source225_CI"]
    if any(type(check.get(field)) is not type(value) or check[field] != value for field, value in SOURCE225_CI.items()):
        raise ValueError("exact successful225 CI required")


def verify_source_context(preflight: dict, report: dict) -> dict:
    records = {}
    for field, digest_field in (("AI_preflight_path", "private_preflight_sha256"), ("observations_path", "observation_input_sha256"), ("AI_verification_path", "private_verification_sha256")):
        path = Path(preflight[field])
        if path.is_symlink() or _sha256(path) != report[digest_field]:
            raise ValueError("original225 singleton drift")
        records[field] = json.loads(path.read_bytes())
    original = records["AI_preflight_path"]
    transition = preflight["test_transition"]
    current_test = ROOT / "tests/test_oulu.py"
    if transition != {"old_sha256": OLD_TEST_SHA256, "new_sha256": _sha256(current_test), "only_added_test": NEW_TEST_METHOD, "prior_test_AST_unchanged": True}:
        raise ValueError("explicit227 test transition required")
    tree = ast.parse(current_test.read_bytes())
    removed = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [item for item in node.body if isinstance(item, ast.FunctionDef) and item.name == NEW_TEST_METHOD]
            removed += len(methods)
            node.body = [item for item in node.body if item not in methods]
    if removed != 1 or hashlib.sha256(ast.dump(tree).encode()).hexdigest() != OLD_TEST_AST_SHA256:
        raise ValueError("prior test module AST drift")
    for field in ("frozen_file_sha256", "study_config_sha256"):
        if preflight[field] != original[field]:
            raise ValueError("inherited frozen/config protection drift")
    for name, digest in original["pinned_file_sha256"].items():
        expected = transition["new_sha256"] if Path(name).resolve() == current_test.resolve() else digest
        if preflight["pinned_file_sha256"].get(name) != expected:
            raise ValueError("inherited source pin omitted or rebound")
    expected_roots = {**original["protected_snapshots"]}
    for field in ("ai_root", "ai_sibling_root"):
        expected_roots[preflight[field]] = records["AI_verification_path"]["output_file_sha256"]
    if len(expected_roots) != 96 or preflight["protected_snapshots"] != expected_roots:
        raise ValueError("exact96 inherited and AI roots required")
    observations = records["observations_path"]
    dependence = {field: observations[field] for field in ("exact_reused_video_rank_groups", "visually_correlated_configuration_rank_groups")}
    if preflight["dependence"] != dependence or observations["preflight_sha256"] != report["private_preflight_sha256"]:
        raise ValueError("original observation/dependence binding required")
    return observations


def render_categorical(definition: dict, digest: str) -> str:
    pairs = definition["pairs"]
    if [pair["queue_rank"] for pair in pairs] != list(TARGET_RANKS) or any(type(pair["queue_rank"]) is not int for pair in pairs):
        raise ValueError("exact batch09 integer ranks required")
    expected = {"review226_sha256": REVIEW_SHA256, "accepted_AI_report_sha256": AI_REPORT_SHA256,
                "accepted_AI_document_sha256": AI_DOCUMENT_SHA256, "accepted_packet_report_sha256": PACKET_REPORT_SHA256}
    if any(definition.get(field) != value for field, value in expected.items()) or any(not is_digest(definition.get(field)) for field in ("preflight_sha256", "observation_input_sha256", "source_packet_lineage_sha256", "source_packet_summary_sha256")):
        raise ValueError("Review226/original225/223 provenance required")
    if structured_digest(definition["dependence"]) != definition.get("dependence_sha256") or json.dumps(definition.get("categorical_rules"), sort_keys=True) != json.dumps(CATEGORICAL_RULES, sort_keys=True):
        raise ValueError("bound dependence and strict categorical mapping required")
    for pair in pairs:
        rank = pair["queue_rank"]
        if pair.get("human_review_notice") != human_notice(rank, definition["dependence"]) or any(not is_digest(pair.get(field)) for field in ("packet_sha256", "ai_record_sha256", "exact_pair_record_sha256", "source_sampling_provenance_sha256")):
            raise ValueError("bound original pair/provenance and neutral notice required")
        if pair.get("ai_disposition") not in DISPOSITIONS:
            raise ValueError("non-binding AI disposition required")
        expected_names = {f"assets/{rank:06d}/{name}.png" for name in ("temporal_a", "temporal_b", "trigger")}
        if set(pair["required_assets_sha256"]) != expected_names or any(not is_digest(value) for value in pair["required_assets_sha256"].values()):
            raise ValueError("exact three bound assets required")
    shell = PAGE.split("<script>", 1)[0].replace("Batch 01", "Batch 09 Categorical Review")
    shell = shell.replace("</style>", "fieldset{margin:14px 0;padding:12px;border:1px solid var(--line);min-width:0}legend{max-width:100%;overflow-wrap:anywhere}fieldset label{display:inline-flex;gap:8px;align-items:center;margin:8px 24px 0 0}[hidden]{display:none!important}</style>")
    data = json.dumps({"definition": definition, "sha256": digest}).replace("<", "\\u003c")
    return shell + SCRIPT.replace("__DATA__", data) + PAGE.split("</script>", 1)[1]


def prepare(args: argparse.Namespace) -> dict:
    private_output(args.out_root, [args.preflight, args.packet_root, args.ai_root])
    preflight = json.loads(args.preflight.read_bytes())
    private_output(args.out_root, [Path(name) for name in preflight["protected_snapshots"]])
    verify_authority(preflight)
    for name, digest in ((REVIEW_FILE, REVIEW_SHA256), (AI_REPORT_FILE, AI_REPORT_SHA256), (AI_DOCUMENT_FILE, AI_DOCUMENT_SHA256), (PACKET_REPORT_FILE, PACKET_REPORT_SHA256)):
        if _sha256(ROOT / name) != digest:
            raise ValueError("accepted public authority drift")
    if _sha256(Path(__file__)) != preflight["runner_sha256"] or any(str(getattr(args, name).resolve()) != preflight[name] for name in ("packet_root", "ai_root")):
        raise ValueError("runner or source-root drift")
    report = json.loads((ROOT / AI_REPORT_FILE).read_bytes())
    observations = verify_source_context(preflight, report)
    verify_preservation(preflight)
    packet_report = json.loads((ROOT / PACKET_REPORT_FILE).read_bytes())
    for name, field in (("lineage.json", "private_lineage_sha256"), ("summary.json", "private_summary_sha256")):
        if _sha256(args.packet_root / name) != packet_report[field]:
            raise ValueError("accepted223 packet provenance drift")
    for name, field in (("definition.json", "private_definition_sha256"), ("ledger.json", "private_ledger_sha256"), ("summary.json", "private_summary_sha256")):
        if _sha256(args.ai_root / name) != report[field]:
            raise ValueError("original225 AI root drift")
    ai_paths = sorted((args.ai_root / "pairs").glob("*.json"))
    if [path.name for path in ai_paths] != [f"{rank:06d}.json" for rank in TARGET_RANKS] or bundle(ai_paths) != report["pair_record_bundle_sha256"]:
        raise ValueError("exact original five-row bundle required")
    definition = {
        "version": 1, "state": "awaiting227_form_review_before_genuine_human_answers", "pairs": [],
        "review226_sha256": REVIEW_SHA256, "accepted_AI_report_sha256": AI_REPORT_SHA256, "accepted_AI_document_sha256": AI_DOCUMENT_SHA256,
        "accepted_packet_report_sha256": PACKET_REPORT_SHA256, "observation_input_sha256": report["observation_input_sha256"],
        "source_packet_lineage_sha256": packet_report["private_lineage_sha256"], "source_packet_summary_sha256": packet_report["private_summary_sha256"],
        "source225_CI": preflight["source225_CI"], "preflight_sha256": _sha256(args.preflight),
        "acceptance_basis": "Review226_accepts_reported_AI_attestations_not_Windows_private_visual_inspection_human_agreement_or_scientific_clearance",
        "preparation_code_sha256": _sha256(Path(__file__)), "packet_root": str(args.packet_root.resolve()), "ai_root": str(args.ai_root.resolve()),
        "dependence": preflight["dependence"], "dependence_sha256": structured_digest(preflight["dependence"]),
        "categorical_rules": CATEGORICAL_RULES, "queue_ranks": list(TARGET_RANKS),
        "required_human_pair_fields": ["evidence_sufficient", "same_or_derived_content", "personal_inspection_attested", "owner_decision_attested"],
        "human_fields_prefilled": False, "human_prose_required": False, "AI_context_hidden_until_pair_submission": True,
        "AI_context_authorship": "AI_generated_non_binding_proposal_not_human_reasoning", "fully_blinded_review_claimed": False,
        "human_input_collection_authorized": False, "checkpoint_review_required_before_human_input": True, "requires_separate_categorical_importer": True,
        "import_authorized": False, "effective_activation_authorized": False, "confirmed_action": "immediate_scientific_hard_stop",
        "model_execution_authorized": False, "scientific_readiness": False,
    }
    copies = []
    for rank, ai_path, observed in zip(TARGET_RANKS, ai_paths, observations["pairs"], strict=True):
        ai = json.loads(ai_path.read_bytes())
        packet_path = args.packet_root / "pairs" / f"{rank:06d}" / "packet.json"
        packet = json.loads(packet_path.read_bytes())
        if any(type(row["queue_rank"]) is not int or row["queue_rank"] != rank for row in (ai, packet, observed)) or ai["packet_sha256"] != _sha256(packet_path) or ai["candidate"] != packet["candidate"] or ai["exact_pair_record_sha256"] != packet["exact_pair_record_sha256"]:
            raise ValueError("exact original candidate/queue/packet binding required")
        if ai["assets_actually_viewed_sha256"] != packet["image_sha256"] or observed["assets_actually_viewed_sha256"] != packet["image_sha256"] or set(packet["image_sha256"]) != {"temporal_a.png", "temporal_b.png", "trigger.png"}:
            raise ValueError("exact15 accepted image bindings required")
        if ai["human_review_performed"] is not False or ai["effective_disposition_activated"] is not False or ai["observation_input_sha256"] != report["observation_input_sha256"] or ai["proposed_disposition"] != observed["proposed_disposition"]:
            raise ValueError("original non-binding observation/proposal required")
        assets = {}
        for name in ("temporal_a.png", "temporal_b.png", "trigger.png"):
            source = packet_path.parent / name
            expected = packet["image_sha256"][name]
            if source.is_symlink() or _sha256(source) != expected:
                raise ValueError("bound image drift")
            relative = f"assets/{rank:06d}/{name}"
            assets[relative] = expected
            copies.append((source, args.out_root / relative, expected))
        definition["pairs"].append({
            "queue_rank": rank, "packet_sha256": _sha256(packet_path), "ai_record_sha256": _sha256(ai_path),
            "exact_pair_record_sha256": ai["exact_pair_record_sha256"], "required_assets_sha256": assets,
            "source_sampling_provenance_sha256": structured_digest(ai["video_sampling_provenance"]), "video_manifest_sha256": ai["video_manifest_sha256"],
            "ai_disposition": ai["proposed_disposition"], "ai_observations": [ai["rationale"]],
            "ai_limitation": ai["limitation"] + " " + ai["visibility_limitation"], "human_review_notice": human_notice(rank, preflight["dependence"]),
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
    verify_preservation(preflight)
    result = {"version": 1, "status": "categorical_handoff_prepared_review_required_before_human_use", "queue_ranks": list(TARGET_RANKS),
              "pairs_prepared": 5, "required_bound_images": 15, "actual_categorical_human_reviews": 0, "effective_dispositions_activated": 0,
              "accepted_current_total": 80, "accepted_semantic_owner_outcomes_total": 80, "accepted_AI_screen_coverage": 85, "highest_risk_remaining_unreviewed": 0,
              "review_definition_sha256": digest, "page_sha256": _sha256(args.out_root / "index.html"), "review226_sha256": REVIEW_SHA256,
              "accepted_AI_report_sha256": AI_REPORT_SHA256, "accepted_AI_document_sha256": AI_DOCUMENT_SHA256, "human_prose_required": False,
              "human_fields_prefilled": False, "historical_inputs_unchanged": True, "historical_disagreements": 1, "historical_unresolved_reconciliations": 0,
              "human_input_collection_authorized": False, "checkpoint_review_required_before_human_input": True, "new_media_decode_or_extraction_executed": False,
              "queue_continued": False, "model_execution_authorized": False, "scientific_readiness": False}
    write_immutable_record(args.out_root / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("preflight", "packet-root", "ai-root", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        print(json.dumps(prepare(parser.parse_args()), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError):
        print("BATCH09 CATEGORICAL HANDOFF FAILED: no human answers collected or imported", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())