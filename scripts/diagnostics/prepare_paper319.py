"""Prepare private partitions and public counts; no image, feature or model evaluation."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from fas.feature_cache import digest
from fas.freeze import write_immutable_record
from fas.fusion_study import components
from fas.source_fitting import identity

PRIVATE = Path("/mnt/e/FAS-private/artifacts/phase1")
MANIFEST = PRIVATE / "source_integration295_v1/source_manifest.json"
MANIFEST_SHA = "7f9f54e6b097d7da0618cf8b3784e9eb3726b6aba8a3957455e26dda20da4580"
OUTPUT = PRIVATE / "paper_completion319_v1"
PUBLIC = ROOT / "results/phase1/paper319-metadata-preflight-v1.json"
DOMAINS = ("OULU-NPU", "CASIA-FASD", "MSU-MFSD", "SiW-Mv2")
SEEDS = (20260917, 20260923, 20261001)
SPLIT_SEED = 20261028
RECEIPTS = {
    "source_run297_v1": "37229d3d99da38a5ab6fd20e17bcfd508321e65b3356627aab7bb6580084d841",
    "source_run299_v1": "43a30681311357b166b28e8f75e1d969da805f816398542b79ce363e68098c88",
    "locked_run301_v3": "375c1777b148a616d1b5327aad864a87de98bbd8250300b25733771b627b1d2b",
}


def active_rows(rows: list[dict]) -> list[dict]:
    if not rows or len({identity(row) for row in rows}) != len(rows):
        raise ValueError("nonempty unique original identities required")
    for row in rows:
        if (row["dataset"] not in DOMAINS or row["official_split"] not in {"train", "development", "test"}
                or row["binary_label"] not in {"bona_fide", "attack"}
                or row["detector_status"] not in {"success", "failed", "not_run"}
                or not row["group_id"]):
            raise ValueError("declared dataset, official split, label, disposition and group required")
        if row["dataset"] != "SiW-Mv2" and not row["subject_id"]:
            raise ValueError("known-subject datasets require subject metadata")
    return [row for row in rows if not (
        row["dataset"] == "SiW-Mv2" and row["official_split"] == "train"
        and not row["source_use_eligible"])]


def assign_roles(rows: list[dict]) -> tuple[dict[str, str], dict[str, str]]:
    mapping = components(rows)
    grouped = defaultdict(list)
    for row in rows:
        grouped[mapping[identity(row)]].append(row)
    strata = defaultdict(list)
    roles = {}
    for component, members in grouped.items():
        domains = {row["dataset"] for row in members}
        splits = {row["official_split"] for row in members}
        if len(domains) != 1 or len(splits) != 1:
            raise ValueError("exact-frame/group component crosses an official or dataset boundary")
        domain, split = next(iter(domains)), next(iter(splits))
        if split == "test":
            role = "evaluation"
        elif domain == "OULU-NPU" and split == "train":
            role = "fitting"
        elif split == "development" and domain != "OULU-NPU":
            raise ValueError("only OULU has a registered native development split")
        else:
            signature = tuple(sorted({row["binary_label"] for row in members}))
            strata[(domain, split, signature)].append(component)
            continue
        roles.update({identity(row): role for row in members})
    for (domain, split, _), group in sorted(strata.items()):
        group.sort(key=lambda key: hashlib.sha256(f"{SPLIT_SEED}:{key}".encode()).hexdigest())
        for index, key in enumerate(group):
            if domain == "OULU-NPU" and split == "development":
                role = ("validation", "calibration")[index % 2]
            else:
                role = ("validation", "calibration", "fitting", "fitting", "fitting")[index % 5]
            roles.update({identity(row): role for row in grouped[key]})
    if set(roles) != {identity(row) for row in rows}:
        raise ValueError("incomplete role assignment")
    return roles, mapping


def counts(rows: list[dict], mapping: dict[str, str]) -> dict:
    result = {}
    for label in ("bona_fide", "attack"):
        subset = [row for row in rows if row["binary_label"] == label]
        usable = [row for row in subset if row["detector_status"] == "success"]
        result[label] = {
            "originals": len(subset), "usable": len(usable),
            "technical_failures": len(subset) - len(usable),
            "components": len({mapping[identity(row)] for row in subset}),
            "usable_components": len({mapping[identity(row)] for row in usable}),
            "unknown_subject_originals": sum(not row["subject_id"] for row in subset),
        }
    return result


def build_partitions(rows: list[dict]) -> tuple[dict, dict]:
    selected = active_rows(rows)
    roles, mapping = assign_roles(selected)
    populations = {}
    for domain in DOMAINS:
        populations[domain] = {}
        for role in ("fitting", "validation", "calibration", "evaluation"):
            subset = [row for row in selected if row["dataset"] == domain and roles[identity(row)] == role]
            summary = counts(subset, mapping)
            for item in summary.values():
                minimum = 5 if role in {"calibration", "evaluation"} else 2
                if item["usable"] < minimum or item["usable_components"] < 2:
                    raise ValueError(f"insufficient declared support: {domain}/{role}")
            populations[domain][role] = summary
    contexts = []
    for target in DOMAINS:
        pools = {role: sorted(identity(row) for row in selected if
                 (row["dataset"] == target if role == "evaluation" else row["dataset"] != target)
                 and roles[identity(row)] == role)
                 for role in ("fitting", "validation", "calibration", "evaluation")}
        sets = [{mapping[key] for key in pool} for pool in pools.values()]
        if any(a & b for index, a in enumerate(sets) for b in sets[index + 1:]):
            raise ValueError("component leaks between fitting, validation, calibration or evaluation")
        for seed in SEEDS:
            contexts.append({"target": target, "seed": seed, **pools})
    private = {
        "version": 1, "study": "paper_completion319_v1", "split_seed": SPLIT_SEED,
        "training_seeds": list(SEEDS), "contexts": contexts,
        "source_manifest_sha256": MANIFEST_SHA,
        "scientific_execution_authorized": False,
    }
    public = {
        "version": 1, "status": "metadata_preparation_complete_not_execution_ready",
        "source_manifest_sha256": MANIFEST_SHA, "split_seed": SPLIT_SEED,
        "training_seeds": list(SEEDS), "context_count": len(contexts),
        "populations": populations,
        "archived_originals": len(rows), "active_originals": len(selected),
        "inherited_source_exclusions": len(rows) - len(selected),
        "unknown_subject_originals": dict(Counter(row["dataset"] for row in selected if not row["subject_id"])),
        "subject_disjointness_verified_for_all_datasets": False,
        "group_and_saved_exact_frame_isolation_passed": True,
        "scientific_execution_authorized": False,
        "new_fits": 0, "image_decodes": 0, "feature_array_loads": 0,
        "model_predictions": 0, "target_evaluations": 0,
        "execution_blockers": [
            "SiW_subject_identity_unavailable_video_grouping_requires_explicit_scope_acceptance",
            "specialist_training_controller_and_synthetic_resource_checks_not_yet_implemented",
            "fresh_owner_approval_of_final_code_input_runtime_and_budget_required",
        ],
    }
    return private, public


def cache_inventory(root: Path, rows: list[dict]) -> dict:
    selected = active_rows(rows)
    wanted = {identity(row) for row in selected if row["detector_status"] == "success"}
    covered = {name: set() for name in ("dino_reg", "dino_plain", "openclip")}
    receipt_hashes, shards = {}, {}
    for directory, expected in RECEIPTS.items():
        path = root / directory / "extraction.json"
        if path.is_symlink() or digest(path) != expected:
            raise ValueError(f"accepted extraction receipt drift: {directory}")
        receipt_hashes[directory] = expected
        record = json.loads(path.read_bytes())
        models = record.get("models", record)
        if directory == "source_run297_v1":
            ids = record["dino_reg"]["ids"]
        elif directory == "source_run299_v1":
            ids = [key for key in record["ids"] if key.startswith("OULU-NPU/")]
        else:
            ids = [key for key in record["success_ids"] if key.startswith("SiW-Mv2/")]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate IDs in cache receipt")
        for name in covered:
            if sum(shard["count"] for shard in models[name]["shards"]) != len(ids):
                raise ValueError("cache shard counts do not match bound population")
            for shard in models[name]["shards"]:
                path = Path(shard["path"])
                if path.is_symlink() or digest(path) != shard["sha256"]:
                    raise ValueError("existing feature shard byte commitment failed")
                shards[str(path)] = path.stat().st_size
            covered[name].update(ids)
    missing = {name: len(wanted - ids) for name, ids in covered.items()}
    if any(missing.values()):
        raise ValueError("not all proposed usable originals have receipt-bound cached features")
    return {
        "extraction_receipt_sha256": receipt_hashes, "required_unique_usable_originals": len(wanted),
        "receipt_coverage_per_branch": {name: len(ids & wanted) for name, ids in covered.items()},
        "missing_per_branch": missing, "verified_shard_files": len(shards),
        "verified_shard_bytes": sum(shards.values()),
        "scope": "receipt_ID_coverage_and_shard_bytes_only_not_array_key_or_runtime_revalidation",
        "new_encoder_forwards_planned_if_full_revalidation_passes": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", required=True)
    parser.parse_args()
    if MANIFEST.is_symlink() or digest(MANIFEST) != MANIFEST_SHA:
        raise ValueError("accepted manifest byte commitment failed")
    rows = json.loads(MANIFEST.read_bytes())["rows"]
    private, public = build_partitions(rows)
    public["cache_inventory"] = cache_inventory(PRIVATE, rows)
    public["implementation_sha256"] = {
        name: digest(ROOT / name) for name in (
            "scripts/diagnostics/prepare_paper319.py", "tests/test_paper319.py",
            "src/fas/fusion_study.py", "src/fas/source_fitting.py")}
    write_immutable_record(OUTPUT / "partitions.json", private)
    public["private_partitions_sha256"] = digest(OUTPUT / "partitions.json")
    write_immutable_record(PUBLIC, public)
    print(json.dumps({"status": public["status"], "contexts": public["context_count"],
                      "populations": public["populations"], "cache": public["cache_inventory"]}, indent=2))


if __name__ == "__main__":
    main()
