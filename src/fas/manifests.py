"""Canonical metadata projections, without promoting media-audit readiness."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from typing import Any

from .contracts import CORE_DOMAINS
from .intake import _relative_path
from .casia import LABEL_MAPPING_HASH as CASIA_MAPPING_HASH
from .msu import LABEL_MAPPING_HASH as MSU_MAPPING_HASH
from .oulu import LABEL_MAPPING_HASH as OULU_MAPPING_HASH
from .siwmv2 import LABEL_MAPPING_HASH as SIWMV2_MAPPING_HASH

MAPPING_HASHES = {"OULU-NPU": OULU_MAPPING_HASH, "CASIA-FASD": CASIA_MAPPING_HASH,
                  "MSU-MFSD": MSU_MAPPING_HASH, "SiW-Mv2": SIWMV2_MAPPING_HASH}

VIDEO_FIELDS = (
    "dataset", "release_id", "source_record_id", "subject_id", "video_id",
    "official_split", "binary_label", "attack_family", "instrument", "material",
    "session_id", "sensor_id", "environment", "media_relpath", "media_sha256",
    "duration_ms", "fps", "frame_count", "decode_status", "label_source",
    "raw_label_token", "label_mapping_id", "label_mapping_version", "label_mapping_hash",
)


def canonicalize_inventory(payload: bytes, expected_sha256: str, dataset: str) -> dict[str, Any]:
    if dataset not in CORE_DOMAINS or hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise ValueError("unsupported dataset or changed accepted inventory bytes")
    inventory = json.loads(payload)
    if not isinstance(inventory, dict) or inventory.get("dataset") != dataset or not isinstance(inventory.get("videos"), list) or not inventory["videos"]:
        raise ValueError("invalid accepted inventory")
    mapping_hash = hashlib.sha256(json.dumps(inventory.get("label_mapping"), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if mapping_hash != inventory.get("label_mapping_hash") or mapping_hash != MAPPING_HASHES[dataset]:
        raise ValueError("inventory label mapping differs from accepted adapter")
    records, keys, paths = [], set(), set()
    for row in inventory["videos"]:
        if not isinstance(row, dict) or not set(VIDEO_FIELDS).issubset(row):
            raise ValueError("missing canonical video fields")
        if row["dataset"] != dataset or row["binary_label"] not in ("bona_fide", "attack"):
            raise ValueError("invalid canonical dataset or label")
        if not all(isinstance(row[field], str) and row[field].strip() for field in ("release_id", "source_record_id", "video_id", "official_split", "label_source", "raw_label_token", "label_mapping_id")):
            raise ValueError("empty canonical identity or provenance")
        if type(row["label_mapping_version"]) is not int or row["label_mapping_version"] < 1 or row["label_mapping_hash"] != inventory.get("label_mapping_hash"):
            raise ValueError("invalid label mapping provenance")
        path = _relative_path(row["media_relpath"])
        if path is None or row["video_id"] in keys or path.as_posix() in paths:
            raise ValueError("unsafe or duplicate canonical identity")
        subject = row["subject_id"]
        if dataset == "SiW-Mv2":
            if subject is not None:
                raise ValueError("SiW-Mv2 subject identity must remain unknown")
        elif not isinstance(subject, str) or not subject.strip():
            raise ValueError("known-subject datasets require subject IDs")
        if row.get("role") is not None:
            raise ValueError("adapter inventory must not preassign experiment roles")
        if dataset == "SiW-Mv2" and (row["official_split"] not in ("train", "test")
                or row.get("source_eligible") is not (row["official_split"] == "train")
                or row.get("outer_target_eligible") is not (row["official_split"] == "test")):
            raise ValueError("SiW-Mv2 eligibility drift")
        keys.add(row["video_id"])
        paths.add(path.as_posix())
        records.append({**row, "group_unit": "video" if dataset == "SiW-Mv2" else "subject",
                        "group_id": row["video_id"] if dataset == "SiW-Mv2" else subject, "role": None})
    return {"version": 1, "dataset": dataset, "status": "canonical_metadata_only",
            "inventory_sha256": expected_sha256, "label_mapping_hash": inventory["label_mapping_hash"],
            "scientific_readiness": False, "media_audit_verified": False,
            "roles_assigned": False, "videos": sorted(records, key=lambda row: row["video_id"])}


def propose_source_roles(canonical: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    fields = {"version", "state", "track", "split_seed", "initial_role_weights", "source_partitions",
              "minimum_metadata_class_videos_per_role", "stratification_fields"}
    if set(policy) != fields or type(policy["version"]) is not int or policy["version"] not in (1, 2):
        raise ValueError("invalid role policy fields/version")
    if policy["state"] != "proposal_not_approved" or policy["track"] != "strict_single_image_track_b":
        raise ValueError("this builder only creates unapproved Track-B proposals")
    if type(policy["split_seed"]) is not int or policy["split_seed"] < 0:
        raise ValueError("explicit nonnegative split seed required")
    weights = policy["initial_role_weights"]
    if not isinstance(weights, dict) or set(weights) != {"train", "branch_calibration", "g_domain"} or any(type(value) is not int or value <= 0 for value in weights.values()):
        raise ValueError("positive integer initial role weights required")
    partitions = policy["source_partitions"]
    if not isinstance(partitions, dict) or set(partitions) != CORE_DOMAINS or partitions["SiW-Mv2"] != ["train"]:
        raise ValueError("explicit core source partitions and SiW train-only policy required")
    if any(not isinstance(values, list) or not values or any(not isinstance(value, str) or not value for value in values) or len(set(values)) != len(values) for values in partitions.values()):
        raise ValueError("invalid source partition lists")
    strata_fields = ["official_split", "binary_label", "attack_family", "sensor_id", "session_id", "environment"]
    if policy["version"] == 2:
        strata_fields.insert(3, "reference_attack_type")
    if policy["stratification_fields"] != strata_fields:
        raise ValueError("versioned stratification priority required")
    minimum = policy["minimum_metadata_class_videos_per_role"]
    if type(minimum) is not int or minimum < 1:
        raise ValueError("positive metadata-class minimum required")
    dataset = canonical["dataset"]
    if dataset not in CORE_DOMAINS or canonical.get("status") != "canonical_metadata_only" or canonical.get("roles_assigned") is not False:
        raise ValueError("unassigned canonical metadata required")
    groups = defaultdict(list)
    excluded_groups = set()
    for row in canonical["videos"]:
        if row["official_split"] in partitions[dataset]:
            if dataset == "SiW-Mv2" and (row.get("source_eligible") is not True or row["subject_id"] is not None):
                raise ValueError("SiW-Mv2 source population mismatch")
            groups[row["group_id"]].append(row)
        else:
            excluded_groups.add(row["group_id"])
    if set(groups) & excluded_groups:
        raise ValueError("source partition policy cuts a complete group")
    if not groups:
        raise ValueError("empty source-eligible population")
    strata = defaultdict(list)
    for group, rows in groups.items():
        signature = tuple(tuple(sorted({str(row.get(field) or "unknown") if field == "reference_attack_type" else str(row[field]) for row in rows})) for field in strata_fields)
        strata[signature].append(group)
    roles = ("train", "branch_calibration", "g_domain")
    total_weight = sum(weights.values())
    policy_hash = hashlib.sha256(json.dumps(policy, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assignments = {}
    for signature, group_ids in sorted(strata.items()):
        def rank(group: str) -> str:
            releases = sorted({row["release_id"] for row in groups[group]})
            return hashlib.sha256(json.dumps([dataset, releases, policy_hash, policy["split_seed"], group], separators=(",", ":")).encode()).hexdigest()
        ordered = sorted(group_ids, key=lambda group: (rank(group), group))
        quotas = {role: len(ordered) * weights[role] // total_weight for role in roles}
        remainder_order = sorted(roles, key=lambda role: (-(len(ordered) * weights[role] % total_weight), roles.index(role)))
        for role in remainder_order[:len(ordered) - sum(quotas.values())]:
            quotas[role] += 1
        offset = 0
        for role in roles:
            for group in ordered[offset:offset + quotas[role]]:
                assignments[group] = role
            offset += quotas[role]
    records = [{**row, "role": assignments[group]} for group, rows in groups.items() for row in rows]
    counts = {role: {"groups": len({row["group_id"] for row in records if row["role"] == role}),
                     **{label: sum(row["role"] == role and row["binary_label"] == label for row in records) for label in ("bona_fide", "attack")}} for role in roles}
    feasible = all(counts[role][label] >= minimum for role in roles for label in ("bona_fide", "attack"))
    return {"version": 1, "dataset": dataset, "state": "proposal_not_approved", "policy_sha256": policy_hash,
            "inventory_sha256": canonical["inventory_sha256"], "source_eligible_videos": len(records),
            "source_eligible_groups": len(groups), "role_counts": counts, "metadata_class_feasible": feasible,
            "fitted_error_and_gate_event_feasibility": "not_evaluated_no_source_predictions",
            "content_duplicate_audit": "not_verified_no_media_hashes", "scientific_readiness": False,
            "policy_approved": False, "roles_frozen_for_execution": False,
            "videos": sorted(records, key=lambda row: row["video_id"])}