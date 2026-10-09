#!/usr/bin/env python3
"""Immutable pairwise exact-evidence triage of accepted OULU candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.lineage import PRIORITY_NAMES, candidate_priority, exact_content_evidence
from fas.oulu import _sha256


def triage(screen_root: Path, audit_root: Path, frozen_root: Path, out_root: Path) -> dict:
    screening, audit, frozen, output = (path.resolve() for path in (screen_root, audit_root, frozen_root, out_root))
    if out_root.exists() or out_root.is_symlink() or not all(path.is_dir() for path in (screening, audit, frozen)):
        raise ValueError("missing input or existing output")
    if any(output.is_relative_to(path) or path.is_relative_to(output) for path in (ROOT, screening, audit, frozen)):
        raise ValueError("unsafe private output boundary")
    public_path = ROOT / "results/phase1/oulu-content-screening-v1.json"
    accepted = json.loads(public_path.read_bytes())
    if _sha256(screening / "summary.json") != accepted["private_summary_sha256"]:
        raise ValueError("accepted screening summary drift")
    summary = json.loads((screening / "summary.json").read_bytes())
    if _sha256(screening / "lineage.json") != summary["lineage_sha256"] or summary["lineage_sha256"] != accepted["lineage_sha256"]:
        raise ValueError("screening lineage drift")
    media_report_path = ROOT / "results/phase1/oulu-per-video-media-audit-v1.json"
    media_report = json.loads(media_report_path.read_bytes())
    if _sha256(audit / "summary.json") != media_report["private_summary_sha256"]:
        raise ValueError("accepted media summary drift")
    paths = sorted((audit / "videos").glob("*.json"))
    bundle = hashlib.sha256("".join(f"{path.stem}:{_sha256(path)}\n" for path in paths).encode()).hexdigest()
    if len(paths) != 4950 or bundle != media_report["video_record_bundle_sha256"]:
        raise ValueError("accepted full-frame media evidence drift")
    frozen_hashes = {path.name: _sha256(path) for path in frozen.iterdir()}
    if frozen_hashes != accepted["frozen_artifact_sha256"] or frozen_hashes != media_report["frozen_artifact_sha256"]:
        raise ValueError("frozen canonical/role drift")
    pairs = []
    for chunk in summary["candidate_chunks"]:
        name = chunk["name"]
        if Path(name).name != name or not name.endswith(".json"):
            raise ValueError("unsafe candidate chunk")
        path = screening / "pairs" / name
        if _sha256(path) != chunk["sha256"] or chunk["sha256"] not in accepted["candidate_chunk_sha256"]:
            raise ValueError("accepted pair chunk drift")
        pairs.extend(json.loads(path.read_bytes())["pairs"])
    if len(pairs) != 6653 or sum(pair["exact_full_video_evidence"] for pair in pairs) != 13:
        raise ValueError("candidate population drift")
    if len({(pair["left"], pair["right"]) for pair in pairs}) != len(pairs) or any(pair["left"] >= pair["right"] for pair in pairs):
        raise ValueError("duplicate or unordered pair identity")
    unresolved = sorted((pair for pair in pairs if not pair["exact_full_video_evidence"]),
                        key=lambda pair: (candidate_priority(pair), pair["left"], pair["right"]))
    if len(unresolved) != 6640:
        raise ValueError("unresolved population drift")
    media = {path.stem: json.loads(path.read_bytes()) for path in paths}
    hashes = {path.stem: _sha256(path) for path in paths}
    policy_path = ROOT / "configs/content_adjudication_v1.yaml"
    policy = json.loads(policy_path.read_bytes())
    if policy["priority"] != list(PRIORITY_NAMES) or policy["confirmation"] != "complete_shorter_sequence_contained_and_at_least_two_distinct_RGB_frames" or policy["no_sufficient_exact_evidence"] != "uncertain_insufficient_evidence_never_rejected_false_positive":
        raise ValueError("adjudication policy drift")
    if any(policy[key] is not False for key in ("phash_equivalence_threshold_used", "visual_review_performed", "role_or_selector_or_seed_rewrite", "model_execution_authorized", "scientific_readiness")):
        raise ValueError("unauthorized adjudication policy")
    lineage = {"version": 1, "policy": policy, "policy_sha256": _sha256(policy_path),
               "review_sha256": _sha256(ROOT / "docs/112-review-doc111-oulu-content-screening.md"),
               "accepted_screening_report_sha256": _sha256(public_path),
               "accepted_media_report_sha256": _sha256(media_report_path),
               "accepted_media_record_bundle_sha256": bundle, "frozen_artifact_sha256": frozen_hashes,
               "transaction_policy_sha256": _sha256(ROOT / "configs/transaction_policy_v1.yaml"),
               "screening_policy_sha256": _sha256(ROOT / "configs/content_screening_v1.yaml"),
               "evidence_code_sha256": _sha256(ROOT / "src/fas/lineage.py"), "runner_sha256": _sha256(Path(__file__)),
               "model_execution_authorized": False, "scientific_readiness": False}
    write_immutable_record(output / "lineage.json", lineage)
    counts, priorities = Counter(), Counter()
    records = []
    confirmed_cross_role = 0
    for rank, pair in enumerate(unresolved):
        left, right = media[pair["left"]], media[pair["right"]]
        if left["video_id"] != pair["left"] or right["video_id"] != pair["right"]:
            raise ValueError("media identity mismatch")
        expected = {"cross_role": left["role"] != right["role"], "cross_partition": left["official_split"] != right["official_split"],
                    "conflicting_label": left["binary_label"] != right["binary_label"]}
        if any(pair[key] != value for key, value in expected.items()):
            raise ValueError("candidate boundary metadata drift")
        if left["media_sha256"] == right["media_sha256"] or left["decoded_rgb_sequence_sha256"] == right["decoded_rgb_sequence_sha256"]:
            raise ValueError("nonexact pair unexpectedly exact")
        evidence = exact_content_evidence(left, right)
        priority = PRIORITY_NAMES[candidate_priority(pair)]
        record = {"version": 1, "queue_rank": rank, "priority": priority, "candidate": pair,
                  "left_media_record_sha256": hashes[pair["left"]], "right_media_record_sha256": hashes[pair["right"]],
                  "left_metadata": {key: left[key] for key in ("role", "binary_label", "official_split")},
                  "right_metadata": {key: right[key] for key in ("role", "binary_label", "official_split")},
                  "evidence": evidence, "scientific_remediation_applied": False}
        path = output / "pairs" / f"{rank:06d}.json"
        write_immutable_record(path, record)
        records.append({"name": path.name, "sha256": _sha256(path)})
        counts[evidence["disposition"]] += 1
        counts["pairs_with_any_exact_RGB_overlap"] += evidence["shared_unique_rgb_frames"] > 0
        priorities[priority] += 1
        if evidence["disposition"] == "confirmed_same_content_or_derived_lineage" and pair["cross_role"]:
            confirmed_cross_role += 1
            print("CONFIRMED CROSS-ROLE DECODED CONTENT: execution remains blocked; scientific decision required", flush=True)
        if (rank + 1) % 1000 == 0:
            print(f"PAIR EVIDENCE {rank + 1}/6640", flush=True)
    if {path.name: _sha256(path) for path in frozen.iterdir()} != frozen_hashes or _sha256(policy_path) != lineage["policy_sha256"]:
        raise ValueError("frozen inputs changed during evidence pass")
    if any(_sha256(audit / "videos" / (identity + ".json")) != digest for identity, digest in hashes.items()):
        raise ValueError("accepted frame evidence changed during pass")
    result = {"version": 1, "status": "exact_evidence_pass_complete_content_adjudication_pending",
              "original_video_denominator": 4950, "retained_decode_failures": 1, "candidate_pairs": 6653,
              "known_exact_pairs_preserved_separately": 13, "nonexact_pairs_examined": len(records),
              "exclusive_priority_counts": dict(sorted(priorities.items())), "evidence_counts": dict(sorted(counts.items())),
              "confirmed_cross_role_decoded_content": confirmed_cross_role,
              "prospective_scientific_decision_required": confirmed_cross_role > 0,
              "pair_record_bundle_sha256": hashlib.sha256("".join(f"{row['name']}:{row['sha256']}\n" for row in records).encode()).hexdigest(),
              "lineage_sha256": _sha256(output / "lineage.json"), "full_frame_indexes_used": True,
              "media_reopened": False, "visual_review_performed": False, "capture_provenance_certified": False,
              "frozen_inputs_unchanged": True, "model_execution_authorized": False, "scientific_readiness": False}
    write_immutable_record(output / "summary.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("screen-root", "audit-root", "frozen-root", "out-root"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(triage(args.screen_root, args.audit_root, args.frozen_root, args.out_root), sort_keys=True), flush=True)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, ZeroDivisionError):
        print("LINEAGE EVIDENCE PASS FAILED: inspect private partial evidence; no completion claimed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())