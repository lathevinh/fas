#!/usr/bin/env python3
"""Export immutable metadata-only manifests and unapproved source-role proposals."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.contracts import CORE_DOMAINS
from fas.freeze import write_immutable_record
from fas.manifests import canonicalize_inventory, propose_source_roles, build_source_role_freeze_record
from fas.preregistration import METADATA_COLUMNS, SIWMV2_METADATA_COLUMNS, ROLE_COLUMNS


def write_csv(path: Path, columns: tuple[str, ...], rows: list[dict]) -> str:
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows({key: row.get(key) for key in columns} for row in rows)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(receipt: dict, policy: dict, output: Path) -> dict:
    if not isinstance(receipt, dict) or set(receipt) != {"version", "inventories"} or type(receipt["version"]) is not int or receipt["version"] != 1:
        raise ValueError("invalid inventory receipt")
    sources = receipt["inventories"]
    if not isinstance(sources, dict) or set(sources) != CORE_DOMAINS:
        raise ValueError("all four accepted inventories required")
    plans = []
    for dataset, source in sorted(sources.items()):
        if not isinstance(source, dict) or set(source) != {"path", "sha256"}:
            raise ValueError("invalid inventory pin")
        supplied = Path(source["path"])
        path = supplied.resolve()
        if supplied.is_symlink() or not path.is_file() or path.is_relative_to(ROOT) or output.is_relative_to(path.parent):
            raise ValueError("unsafe private input/output boundary")
        canonical = canonicalize_inventory(path.read_bytes(), source["sha256"], dataset)
        proposal = propose_source_roles(canonical, policy)
        plans.append((dataset, canonical, proposal))
    output.mkdir(parents=True, exist_ok=False)
    datasets = {}
    for dataset, canonical, proposal in plans:
        slug = dataset.lower().replace("-", "_")
        canonical_path = output / f"{slug}_canonical.json"
        proposal_path = output / f"{slug}_role_proposal.json"
        write_immutable_record(canonical_path, canonical)
        write_immutable_record(proposal_path, proposal)
        columns = SIWMV2_METADATA_COLUMNS if dataset == "SiW-Mv2" else METADATA_COLUMNS
        metadata_hash = write_csv(output / f"{slug}_metadata.csv", columns, canonical["videos"])
        roles_hash = write_csv(output / f"{slug}_roles_proposed.csv", ROLE_COLUMNS, proposal["videos"])
        rows = canonical["videos"]
        datasets[dataset] = {
            "inventory_sha256": canonical["inventory_sha256"], "canonical_sha256": hashlib.sha256(canonical_path.read_bytes()).hexdigest(),
            "metadata_csv_sha256": metadata_hash, "role_proposal_sha256": hashlib.sha256(proposal_path.read_bytes()).hexdigest(),
            "roles_proposed_csv_sha256": roles_hash, "label_mapping_hash": canonical["label_mapping_hash"],
            "videos": len(rows), "subjects": None if dataset == "SiW-Mv2" else len({row["subject_id"] for row in rows}),
            "groups": len({row["group_id"] for row in rows}), "group_unit": rows[0]["group_unit"],
            "partitions": {split: {label: sum(row["official_split"] == split and row["binary_label"] == label for row in rows) for label in ("bona_fide", "attack")} for split in sorted({row["official_split"] for row in rows})},
            **{field: proposal[field] for field in ("policy_sha256", "source_eligible_videos", "source_eligible_groups", "role_counts", "metadata_class_feasible", "fitted_error_and_gate_event_feasibility", "content_duplicate_audit")},
            "role_attack_family_coverage": {role: sorted({row["attack_family"] for row in proposal["videos"] if row["role"] == role and row["binary_label"] == "attack"}) for role in policy["initial_role_weights"]},
            "role_reference_attack_type_counts": {role: {subtype: sum(row["role"] == role and (row.get("reference_attack_type") or "unknown") == subtype for row in proposal["videos"]) for subtype in sorted({row.get("reference_attack_type") or "unknown" for row in proposal["videos"]})} for role in policy["initial_role_weights"]},
        }
    summary = {"version": 1, "status": "metadata_complete_role_policy_proposal_only", "datasets": datasets,
        "policy": policy, "scientific_readiness": False, "media_audit_verified": False,
        "policy_approved": False, "roles_frozen_for_execution": False,
        "metadata_class_feasible_all_sources": all(row["metadata_class_feasible"] for row in datasets.values()),
        "no_media_access": True, "no_model_inference_or_training": True}
    write_immutable_record(output / "bundle_summary.json", summary)
    return summary


def freeze_bundle(bundle: Path, policy_path: Path, registry_path: Path, output: Path) -> dict:
    registry_file = registry_path.resolve()
    if registry_path.is_symlink() or not registry_file.is_relative_to(ROOT) or not registry_file.is_file():
        raise ValueError("tracked owner-approved freeze registry required")
    registry = json.loads(registry_file.read_bytes())
    approval = registry["approval"]
    for field, hash_field in (("review_file", "review_sha256"), ("allocation_policy_file", "allocation_policy_file_sha256"),
                             ("accepted_summary_file", "accepted_summary_sha256")):
        supplied = ROOT / approval[field]
        public_path = supplied.resolve()
        if supplied.is_symlink() or not public_path.is_relative_to(ROOT) or not public_path.is_file() or hashlib.sha256(public_path.read_bytes()).hexdigest() != approval[hash_field]:
            raise ValueError("changed public approval evidence")
    if policy_path.is_symlink() or policy_path.resolve() != (ROOT / approval["allocation_policy_file"]).resolve():
        raise ValueError("use the exact accepted allocation policy")
    names = {"bundle_summary.json"}
    for dataset in CORE_DOMAINS:
        slug = dataset.lower().replace("-", "_")
        names.update(f"{slug}_{suffix}" for suffix in ("canonical.json", "metadata.csv", "role_proposal.json", "roles_proposed.csv"))
    if {path.name for path in bundle.iterdir()} != names:
        raise ValueError("complete accepted proposal bundle required")
    payloads = {}
    for name in sorted(names):
        path = bundle / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("regular private proposal artifacts required")
        payloads[name] = path.read_bytes()
    hashes = {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()}
    frozen = build_source_role_freeze_record(approval, policy_path.read_bytes(), payloads["bundle_summary.json"], hashes)
    if registry != frozen:
        raise ValueError("freeze registry differs from accepted policy, artifacts or approval scope")
    output.mkdir(parents=True, exist_ok=False)
    for name in frozen["frozen_artifact_sha256"]:
        source_name = name.replace("_roles.csv", "_roles_proposed.csv")
        with (output / name).open("xb") as handle:
            handle.write(payloads[source_name])
    write_immutable_record(output / "source_role_freeze.json", frozen)
    return frozen


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--inputs", type=Path)
    source.add_argument("--freeze-bundle", type=Path)
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        supplied = args.inputs if args.inputs is not None else args.freeze_bundle
        receipt_path, output = supplied.resolve(), args.out.resolve()
        if supplied.is_symlink() or receipt_path.is_relative_to(ROOT):
            raise ValueError("private inventory receipt or proposal bundle required")
        if args.out.exists() or args.out.is_symlink() or output.is_relative_to(ROOT) or output.is_relative_to(receipt_path.parent):
            raise ValueError("new private output separate from receipt required")
        if args.freeze_bundle is not None:
            if args.approval is None or not receipt_path.is_dir():
                raise ValueError("accepted bundle and approval registry required for freeze")
            summary = freeze_bundle(receipt_path, args.policy, args.approval, output)
        else:
            if args.approval is not None or not receipt_path.is_file():
                raise ValueError("private inventory receipt required for proposal export")
            receipt = json.loads(receipt_path.read_bytes())
            policy = json.loads(args.policy.read_bytes())
            summary = build(receipt, policy, output)
    except (ValueError, OSError, RuntimeError, UnicodeError, KeyError, TypeError):
        print("MANIFEST BUILD FAILED: invalid private inputs, proposal policy or immutable output", file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())