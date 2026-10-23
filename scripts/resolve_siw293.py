"""Prepare a finite SiW source-use amendment from sealed saved evidence only."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import readback_siw291_blocked as blocked
from fas.freeze import write_immutable_record

ROOT = Path(__file__).resolve().parents[1]
SAVED = blocked.run.OUTPUT
OUTPUT = SAVED.parent / "siwmv2_source_use293_v1"
POLICY = "siwmv2-source-use-exclusions-v1"
PRIORITY = ("g_domain", "branch_calibration", "train")
FIELDS = ("video_id", "official_split", "role", "binary_label",
          "media_sha256", "decoded_rgb_sequence_sha256")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified(path: Path, digest: str) -> dict:
    payload = path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != digest:
        raise ValueError(f"saved evidence SHA256 mismatch: {path.name}")
    return json.loads(payload)


def counts(rows: list[dict]) -> dict:
    result = {}
    for role in (*reversed(PRIORITY), None):
        members = [row for row in rows if row["role"] == role]
        labels = Counter(row["binary_label"] for row in members)
        success = sum(row["detector_status"] == "success" for row in members)
        result[role or "official_test_null_role"] = {
            "originals": len(members), "bona_fide": labels["bona_fide"],
            "attack": labels["attack"], "detector_success": success,
            "detector_failure": len(members) - success,
            "class_detector_counts": {
                label: dict(Counter(row["detector_status"] for row in members
                                    if row["binary_label"] == label))
                for label in ("bona_fide", "attack")},
        }
    return result


def propose(rows: list[dict]) -> dict:
    if len({row["video_id"] for row in rows}) != len(rows):
        raise ValueError("unique original identities required")
    for index, row in enumerate(rows):
        if (row["index"] != index or row["binary_label"] not in {"attack", "bona_fide"}
                or row["detector_status"] not in {"success", "failed"}
                or row["official_split"] not in {"train", "test"}
                or (row["official_split"] == "test" and row["role"] is not None)
                or (row["official_split"] == "train" and row["role"] not in PRIORITY)):
            raise ValueError("unchanged indexed source/null-test population required")
    groups = blocked.duplicate_groups(rows)
    historical = blocked.summary(groups)
    if historical["binary_label_crossing_groups"]:
        raise ValueError("label conflicts are not covered by this amendment")
    sets = {tuple(group["indices"]): group for group in groups}
    if any(len(indices) != 2 for indices in sets):
        raise ValueError("only the reviewed disjoint duplicate pairs are covered")
    if sum(map(len, sets)) != len({i for indices in sets for i in indices}):
        raise ValueError("overlapping groups require a new protocol decision")
    kinds = {kind: {tuple(group["indices"]) for group in groups if group["kind"] == kind}
             for kind in ("media_sha256", "decoded_rgb_sequence_sha256")}
    if kinds["media_sha256"] != kinds["decoded_rgb_sequence_sha256"]:
        raise ValueError("the reviewed byte/full-sequence corroboration is required")
    exclusions = []
    for indices, group in sorted(sets.items()):
        if not group["forbidden"]:
            continue
        pair = [rows[index] for index in indices]
        test = [row for row in pair if row["official_split"] == "test"]
        if test:
            kept = test[0]
            excluded = next(row for row in pair if row["official_split"] == "train")
            reason = "retain_official_test_exclude_source_copy"
        else:
            kept, excluded = sorted(pair, key=lambda row: PRIORITY.index(row["role"]))
            reason = "retain_higher_priority_frozen_source_role"
        exclusions.append({
            "excluded_index": excluded["index"], "excluded_video_id": excluded["video_id"],
            "excluded_role": excluded["role"], "retained_index": kept["index"],
            "retained_video_id": kept["video_id"], "retained_role": kept["role"],
            "retained_official_split": kept["official_split"],
            "binary_label": excluded["binary_label"],
            "excluded_detector_status": excluded["detector_status"], "reason": reason,
        })
    excluded_indices = {row["excluded_index"] for row in exclusions}
    active = [row for row in rows if row["index"] not in excluded_indices]
    effective = blocked.summary(blocked.duplicate_groups(active))
    if effective["forbidden_unique_groups"]:
        raise ValueError("proposed effective use still crosses a forbidden boundary")
    return {
        "version": 1, "policy_id": POLICY, "status": "proposal_not_adopted",
        "source_role_retention_priority": list(PRIORITY), "exclusions": exclusions,
        "archived_originals": len(rows), "prepared_image_assets": sum(
            4 if row["detector_status"] == "success" else 1 for row in rows),
        "archived_source_originals": sum(row["official_split"] == "train" for row in rows),
        "proposed_source_use_originals": sum(row["official_split"] == "train" for row in active),
        "official_test_originals": sum(row["official_split"] == "test" for row in active),
        "proposed_active_originals": len(active),
        "before_counts": counts(rows), "proposed_effective_counts": counts(active),
        "historical_exact_groups": historical, "proposed_effective_exact_groups": effective,
        "canonical_membership_or_roles_changed": False, "media_decode_calls": 0,
        "detector_calls": 0, "image_artifacts_verified": True,
        "protocol_use_accepted": False, "scientific_readiness": False,
    }


def prepare() -> None:
    receipt = json.loads((ROOT / "results/phase1/siwmv2-blocked-readback291-v1.json").read_bytes())
    assessment = json.loads((ROOT / "results/phase1/siwmv2-local-assessment291-v1.json").read_bytes())
    closure = SAVED / "blocked_closure"
    pins = {
        closure / "plan.json": receipt["closure_plan_sha256"],
        closure / "readback.json": receipt["private_readback_sha256"],
        closure / "exact_groups.json": receipt["exact_groups_sha256"],
        closure / "full_manifest.json": receipt["full_manifest_sha256"],
        closure / "visual_review.json": assessment["private_visual_sha256"],
        closure / "resources.json": receipt["private_resources_sha256"],
        SAVED / "resources.json": receipt["original_resources_sha256"],
    }
    for path, digest in pins.items():
        if sha(path) != digest:
            raise ValueError(f"accepted saved receipt changed: {path.name}")
    plan = json.loads((closure / "plan.json").read_bytes())
    original_path = SAVED / "plan.json"
    original = verified(original_path, plan["sources"][str(original_path)])
    expected = {f"{folder}/{i:04d}.json"
                for folder in ("attempts", "media", "transactions") for i in range(1680)}
    if set(plan["per_record_sha256"]) != expected:
        raise ValueError("exact5040 original record seals required")
    records = {}
    for relative, digest in plan["per_record_sha256"].items():
        records[relative] = verified(SAVED / relative, digest)
    rows = []
    for index, parent in enumerate(original["videos"]):
        media = records[f"media/{index:04d}.json"]
        txn = records[f"transactions/{index:04d}.json"]
        if any(media[key] != parent[key] for key in ("video_id", "official_split", "role", "binary_label")):
            raise ValueError("frozen original binding changed")
        if any(txn[key] != media[key] for key in ("video_id", "role", "binary_label")):
            raise ValueError("transaction/media identity mismatch")
        rows.append({key: media[key] for key in FIELDS} | {
            "index": index, "detector_status": txn["detector_status"],
            "transaction_sha256": plan["per_record_sha256"][f"transactions/{index:04d}.json"]})
    proposal = propose(rows)
    if (any(proposal["historical_exact_groups"][key] != value
            for key, value in assessment["exact_duplicate_summary"].items())
            or len(proposal["exclusions"]) != 5 or proposal["proposed_source_use_originals"] != 1052
            or any(proposal["before_counts"][role][field] != expected[field]
                   for role, expected in assessment["role_counts"].items()
                   for field in ("originals", "detector_success", "detector_failure"))):
        raise ValueError("reviewed finite population or duplicate finding changed")
    for name, digest in assessment["unchanged_summary_sha256"].items():
        if sha(ROOT / "manifests" / name) != digest:
            raise ValueError("historical summaries changed before adoption")
    proposal["saved_evidence_sha256"] = {str(path): digest for path, digest in pins.items()}
    proposal["original_plan_sha256"] = sha(original_path)
    proposal["review292_sha256"] = sha(ROOT / "docs/292-review-doc291-siw-images-and-exact-crossing-resolution.md")
    proposal["preparer_sha256"] = sha(Path(__file__))
    proposal["rows"] = rows
    write_immutable_record(OUTPUT / "proposal.json", proposal)
    public = {key: value for key, value in proposal.items()
              if key not in {"rows", "saved_evidence_sha256", "exclusions"}}
    public["private_proposal_sha256"] = sha(OUTPUT / "proposal.json")
    public["exclusions"] = [{key: value for key, value in row.items()
                             if key not in {"excluded_video_id", "retained_video_id"}}
                            for row in proposal["exclusions"]]
    write_immutable_record(OUTPUT / "public_proposal.json", public)
    print(json.dumps({key: proposal[key] for key in (
        "exclusions", "before_counts", "proposed_effective_counts",
        "proposed_source_use_originals", "proposed_active_originals")}, indent=2))
    print("PRIVATE PROPOSAL SHA256", public["private_proposal_sha256"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    prepare()
