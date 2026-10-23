"""Bind an adopted SiW use overlay to saved transactions; never process media."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

import resolve_siw293 as proposal_run
from fas.freeze import write_immutable_record
from fas.source_use import POLICY_PATH, load_source_use
from fas.preregistration import validate_stage

ROOT, OUTPUT = proposal_run.ROOT, proposal_run.OUTPUT
sha, verified = proposal_run.sha, proposal_run.verified
REVIEWED_COMMIT = "baecc438ed36f4b8dfb8cbf2eed39b093f3cda07"


def build() -> None:
    proposal_path = OUTPUT / "proposal.json"
    adoption_path = OUTPUT / "owner_adoption.json"
    adoption = json.loads(adoption_path.read_bytes())
    proposal = verified(proposal_path, adoption["private_proposal_sha256"])
    if (adoption["explicit_owner_adoption"] is not True
            or adoption["selected_answer"] != "adopt_siw293_source_use_exclusions_v1"):
        raise ValueError("explicit complete owner adoption required before building use artifacts")
    if sha(ROOT / "scripts/resolve_siw293.py") != proposal["preparer_sha256"]:
        raise ValueError("executed proposal preparer changed")
    for path, digest in proposal["saved_evidence_sha256"].items():
        if sha(Path(path)) != digest:
            raise ValueError("sealed291 evidence changed after proposal")
    current = proposal_run.propose(proposal["rows"])
    for key, value in current.items():
        if proposal[key] != value:
            raise ValueError("adopted proposal no longer reproduces")
    identity = {
        "version": 1, "policy_id": proposal["policy_id"],
        "private_proposal_sha256": sha(proposal_path),
        "original_plan_sha256": proposal["original_plan_sha256"],
        "owner_adoption_sha256": sha(adoption_path),
    }
    overlay = {**identity, "exclusions": proposal["exclusions"]}
    excluded = {item["excluded_index"] for item in overlay["exclusions"]}
    manifest = {**identity, "rows": [
        {**row, "dataset": "SiW-Mv2", "source_use_policy_id": proposal["policy_id"],
         "source_use_eligible": row["official_split"] == "train" and row["index"] not in excluded}
        for row in proposal["rows"]]}
    write_immutable_record(OUTPUT / "overlay.json", overlay)
    write_immutable_record(OUTPUT / "effective_use_manifest.json", manifest)
    original = verified(proposal_run.SAVED / "plan.json", proposal["original_plan_sha256"])
    frozen = {Path(path).name: digest for path, digest in original["sources"].items()
              if Path(path).parent == proposal_run.blocked.run.FROZEN}
    policy = {
        "version": 1, "policy_id": proposal["policy_id"], "state": "owner_adopted",
        "source_role_retention_priority": proposal["source_role_retention_priority"],
        "official_test_retained": True, "archived_membership_and_roles_unchanged": True,
        "training_authorized": False, "target_evaluation_authorized": False,
        "scientific_readiness": False, "private_proposal_sha256": sha(proposal_path),
        "owner_adoption_sha256": sha(adoption_path),
        "original_plan_sha256": proposal["original_plan_sha256"],
        "review292_sha256": proposal["review292_sha256"],
        "overlay_sha256": sha(OUTPUT / "overlay.json"),
        "effective_manifest_sha256": sha(OUTPUT / "effective_use_manifest.json"),
        "source_excluded_indices": sorted(excluded),
        "archived_originals": proposal["archived_originals"],
        "source_use_originals": proposal["proposed_source_use_originals"],
        "official_test_originals": proposal["official_test_originals"],
        "active_originals": proposal["proposed_active_originals"],
        "effective_role_counts": proposal["proposed_effective_counts"],
        "frozen_artifact_sha256": frozen,
        "historical_exact_groups": proposal["historical_exact_groups"],
    }
    write_immutable_record(ROOT / POLICY_PATH, policy)
    public = json.loads((OUTPUT / "public_proposal.json").read_bytes())
    public.update(status="owner_adopted_pending_closure", protocol_use_accepted=False,
                  owner_adoption_sha256=policy["owner_adoption_sha256"],
                  overlay_sha256=policy["overlay_sha256"],
                  effective_manifest_sha256=policy["effective_manifest_sha256"])
    write_immutable_record(ROOT / "results/phase1/siwmv2-source-use-overlay293-v1.json", public)
    verify()


def verify() -> dict:
    policy_payload = (ROOT / POLICY_PATH).read_bytes()
    context = load_source_use(policy_payload, (OUTPUT / "effective_use_manifest.json").read_bytes(),
                              (OUTPUT / "overlay.json").read_bytes(),
                              (OUTPUT / "owner_adoption.json").read_bytes())
    proposal = verified(OUTPUT / "proposal.json", json.loads(policy_payload)["private_proposal_sha256"])
    closure_plan_path = proposal_run.SAVED / "blocked_closure/plan.json"
    closure_plan = verified(closure_plan_path, proposal["saved_evidence_sha256"][str(closure_plan_path)])
    for relative, digest in closure_plan["per_record_sha256"].items():
        if sha(proposal_run.SAVED / relative) != digest:
            raise ValueError("original archived record changed during policy closure")
    for path, digest in proposal["saved_evidence_sha256"].items():
        if sha(Path(path)) != digest:
            raise ValueError("saved291 receipt changed during policy closure")
    rejected = Counter()
    from fas.transactions import calibration_fit_rows
    calibration = []
    for purpose in ("fitting", "calibration", "domain_use"):
        for row in context.source_rows(purpose):
            payload = (proposal_run.SAVED / f'transactions/{row["index"]:04d}.json').read_bytes()
            joined = context.bind_transaction(payload, purpose)
            if purpose == "calibration":
                calibration.append(joined)
        for row in context.rows:
            if row["source_use_eligible"]:
                continue
            try:
                context.require_row(row, purpose)
            except ValueError:
                rejected[purpose] += 1
            else:
                raise ValueError("excluded/test original entered a source consumer")
    if calibration_fit_rows(calibration, source_use=context):
        raise ValueError("classifier scores/fitting were not authorized")
    result = {
        "checkpoint": 293, "dataset": "SiW-Mv2", "status": "saved_evidence_use_validation_passed",
        "source_use_binding": dict(context.binding), "archived_originals": len(context.rows),
        "source_use_originals": sum(row["source_use_eligible"] for row in context.rows),
        "official_test_originals": sum(row["official_split"] == "test" for row in context.rows),
        "consumer_rejections": dict(rejected), "source_calibration_fit_rows": 0,
        "media_decode_calls": 0, "detector_calls": 0, "model_scores": 0,
        "fitted_scores": 0, "target_evaluation": False, "scientific_readiness": False,
        "historical_exact_groups": proposal["historical_exact_groups"],
        "effective_exact_groups": proposal["proposed_effective_exact_groups"],
        "saved_evidence_sha256": {Path(path).relative_to(proposal_run.SAVED).as_posix(): digest
                                  for path, digest in proposal["saved_evidence_sha256"].items()},
    }
    print(json.dumps(result, indent=2))
    return result


def close() -> None:
    result = verify()
    policy = json.loads((ROOT / POLICY_PATH).read_bytes())
    proposal = verified(OUTPUT / "proposal.json", policy["private_proposal_sha256"])
    original = verified(proposal_run.SAVED / "plan.json", proposal["original_plan_sha256"])
    historical_sources = {}
    for name, digest in original["sources"].items():
        path = Path(name)
        if path.is_relative_to(ROOT) and path.suffix == ".py":
            relative = path.relative_to(ROOT).as_posix()
            payload = subprocess.check_output(["git", "show", f"{REVIEWED_COMMIT}:{relative}"], cwd=ROOT)
            if hashlib.sha256(payload).hexdigest() != digest:
                raise ValueError("historical producer source does not match its pinned Git version")
            if sha(path) != digest:
                historical_sources[relative] = digest
    for name in ("dataset_summary.csv", "split_summary.csv"):
        baseline = subprocess.check_output(
            ["git", "show", f"{REVIEWED_COMMIT}:manifests/{name}"], cwd=ROOT, text=True)
        with (ROOT / "manifests" / name).open(newline="") as handle:
            current = list(csv.DictReader(handle))
        old = list(csv.DictReader(io.StringIO(baseline)))
        if len(current) != len(old):
            raise ValueError("summary population changed during use amendment")
        for before, after in zip(old, current, strict=True):
            permitted = {"audit_status", "metadata_source"} if name == "dataset_summary.csv" else {"audit_status"}
            if before["dataset"] != "SiW-Mv2":
                permitted = set()
            if any(before[key] != after[key] for key in before if key not in permitted):
                raise ValueError("archived count/hash or accepted dataset summary changed")
    errors = validate_stage(ROOT, "data-audit", frozen_root=proposal_run.blocked.run.FROZEN,
                            source_use_root=OUTPUT)
    if errors:
        raise ValueError(f"normal amended data-audit validator rejected closure: {errors}")
    if sha(ROOT / POLICY_PATH) != result["source_use_binding"]["policy_sha256"]:
        raise ValueError("adopted use policy changed during closure")
    result.update(
        status="local_audit_complete_under_adopted_source_use_policy",
        image_artifacts_verified=True, protocol_use_accepted=True, local_audit_complete=True,
        primary_image_preprocessing_complete=True, summary_promotion_permitted=True,
        clean_original_frozen_boundaries=False, archived_membership_and_roles_unchanged=True,
        normal_validator_errors=[], prepared_image_assets=proposal["prepared_image_assets"],
        archived_source_originals=proposal["archived_source_originals"],
        active_originals=proposal["proposed_active_originals"],
        before_counts=proposal["before_counts"], effective_counts=proposal["proposed_effective_counts"],
        owner_adoption_sha256=policy["owner_adoption_sha256"],
        private_proposal_sha256=policy["private_proposal_sha256"],
        historical_execution_commit=REVIEWED_COMMIT,
        evolved_source_contracts_with_preserved_historical_sha256=historical_sources,
        reviewed291_ci={"head_sha": REVIEWED_COMMIT, "run_id": 39936224548, "job_id": 120356301738,
                        "status": "completed", "conclusion": "success"},
        final_implementation_ci="collect_exact_published_commit_after_push",
        implementation_sha256={name: sha(ROOT / name) for name in (
            "scripts/resolve_siw293.py", "scripts/complete_siw293.py", "src/fas/source_use.py",
            "src/fas/transactions.py", "src/fas/preregistration.py", "scripts/validate_preregistration.py",
            "tests/test_siw_source_use.py")},
        summary_sha256={name: sha(ROOT / "manifests" / name)
                        for name in ("dataset_summary.csv", "split_summary.csv")},
        image_readback_and_visual_reused_by_hash=True, sheets_reopened=0,
        participant_identity_verified=False, joined_domain_assurance=False,
        near_duplicate_independence_certified=False,
    )
    write_immutable_record(OUTPUT / "closure.json", result)
    public = {**result, "private_closure_sha256": sha(OUTPUT / "closure.json")}
    write_immutable_record(ROOT / "results/phase1/siwmv2-local-closure293-v1.json", public)
    print("LOCAL CLOSURE ACCEPTED UNDER ADOPTED USE POLICY; SCIENTIFIC READINESS REMAINS FALSE")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("build", "verify", "close"))
    args = parser.parse_args()
    {"build": build, "verify": verify, "close": close}[args.mode]()
