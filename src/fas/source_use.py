"""Adopted use eligibility, separate from immutable archived SiW inventory."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType
from typing import Any

POLICY_PATH = "configs/siwmv2_source_use_v1.yaml"
POLICY_ID = "siwmv2-source-use-exclusions-v1"
PURPOSE_ROLES = {"fitting": "train", "calibration": "branch_calibration", "domain_use": "g_domain"}
PRIORITY = ("g_domain", "branch_calibration", "train")
BINDING_FIELDS = ("policy_id", "policy_sha256", "overlay_sha256", "effective_manifest_sha256")


def use_binding(policy_payload: bytes) -> dict[str, str]:
    policy = json.loads(policy_payload)
    return {"policy_id": policy["policy_id"],
            "policy_sha256": hashlib.sha256(policy_payload).hexdigest(),
            "overlay_sha256": policy["overlay_sha256"],
            "effective_manifest_sha256": policy["effective_manifest_sha256"]}


def validate_policy(policy: Mapping[str, Any]) -> None:
    if (policy.get("version") != 1 or policy.get("policy_id") != POLICY_ID
            or policy.get("state") != "owner_adopted"
            or policy.get("source_role_retention_priority") != list(PRIORITY)
            or policy.get("official_test_retained") is not True
            or policy.get("archived_membership_and_roles_unchanged") is not True
            or policy.get("training_authorized") is not False
            or policy.get("target_evaluation_authorized") is not False
            or policy.get("scientific_readiness") is not False):
        raise ValueError("explicit adopted finite source-use policy required")
    for field in ("overlay_sha256", "effective_manifest_sha256", "owner_adoption_sha256",
                  "private_proposal_sha256", "original_plan_sha256", "review292_sha256"):
        value = policy.get(field)
        if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise ValueError(f"source-use policy requires a SHA256: {field}")


@dataclass(frozen=True)
class SourceUseContext:
    binding: Mapping[str, str]
    rows: tuple[Mapping[str, Any], ...]

    def source_rows(self, purpose: str) -> tuple[Mapping[str, Any], ...]:
        if purpose not in PURPOSE_ROLES:
            raise ValueError("unknown source consumer purpose")
        return tuple(row for row in self.rows
                     if row["source_use_eligible"] and row["role"] == PURPOSE_ROLES[purpose])

    def require_row(self, row: Mapping[str, Any], purpose: str) -> None:
        if purpose not in PURPOSE_ROLES:
            raise ValueError("unknown source consumer purpose")
        matches = [item for item in self.rows if item["video_id"] == row.get("video_id")]
        if len(matches) != 1:
            raise ValueError("source consumer identity is absent from the adopted manifest")
        expected = matches[0]
        if not expected["source_use_eligible"] or expected["role"] != PURPOSE_ROLES[purpose]:
            raise ValueError("excluded, test/null or wrong-role original cannot enter source consumer")
        fields = ("dataset", "index", "video_id", "official_split", "role", "binary_label",
                  "source_use_eligible", "source_use_policy_id", "transaction_sha256")
        if any(row.get(key) != expected[key] for key in fields):
            raise ValueError("source consumer row does not match adopted eligibility provenance")
        if row.get("source_use_binding") != self.binding:
            raise ValueError("source consumer must bind the exact policy/overlay/effective manifest")

    def bind_transaction(self, payload: bytes, purpose: str) -> dict[str, Any]:
        transaction = json.loads(payload)
        matches = [item for item in self.rows if item["video_id"] == transaction.get("video_id")]
        if len(matches) != 1:
            raise ValueError("transaction is absent from adopted inventory")
        metadata = matches[0]
        if hashlib.sha256(payload).hexdigest() != metadata["transaction_sha256"]:
            raise ValueError("saved source transaction SHA256 mismatch")
        for key in ("index", "video_id", "role", "binary_label", "detector_status"):
            if transaction.get(key) != metadata[key]:
                raise ValueError("saved transaction/frozen eligibility join mismatch")
        row = {**transaction, **metadata}
        self.require_row(row, purpose)
        return row


def load_source_use(
    policy_payload: bytes, manifest_payload: bytes, overlay_payload: bytes, adoption_payload: bytes,
) -> SourceUseContext:
    policy = json.loads(policy_payload)
    validate_policy(policy)
    for payload, key in ((manifest_payload, "effective_manifest_sha256"),
                         (overlay_payload, "overlay_sha256"), (adoption_payload, "owner_adoption_sha256")):
        if hashlib.sha256(payload).hexdigest() != policy[key]:
            raise ValueError(f"adopted source-use evidence SHA256 mismatch: {key}")
    manifest, overlay, adoption = map(json.loads, (manifest_payload, overlay_payload, adoption_payload))
    if (adoption.get("explicit_owner_adoption") is not True
            or adoption.get("selected_answer") != "adopt_siw293_source_use_exclusions_v1"
            or adoption.get("policy_id") != POLICY_ID
            or adoption.get("private_proposal_sha256") != policy["private_proposal_sha256"]
            or adoption.get("governing_review_sha256") != policy["review292_sha256"]):
        raise ValueError("owner adoption does not bind this complete amendment")
    for artifact in (manifest, overlay):
        if (artifact.get("version") != 1 or artifact.get("policy_id") != POLICY_ID
                or artifact.get("private_proposal_sha256") != policy["private_proposal_sha256"]
                or artifact.get("original_plan_sha256") != policy["original_plan_sha256"]
                or artifact.get("owner_adoption_sha256") != policy["owner_adoption_sha256"]):
            raise ValueError("source-use manifest/overlay provenance mismatch")
    exclusions = overlay["exclusions"]
    indices = [item["excluded_index"] for item in exclusions]
    if (len(set(indices)) != len(indices) or indices != policy["source_excluded_indices"]
            or indices != adoption["source_excluded_indices"]):
        raise ValueError("overlay differs from the owner's exact exclusions")
    rows = manifest["rows"]
    if len(rows) != policy["archived_originals"] or len({r["video_id"] for r in rows}) != len(rows):
        raise ValueError("complete unchanged unique archived inventory required")
    excluded = set(indices)
    if any(type(i) is not int or not 0 <= i < len(rows)
           for item in exclusions for i in (item["excluded_index"], item["retained_index"])):
        raise ValueError("overlay indices must identify archived originals")
    for index, row in enumerate(rows):
        source = row["official_split"] == "train"
        if (type(row["index"]) is not int or row["index"] != index or row["dataset"] != "SiW-Mv2"
                or row["binary_label"] not in {"attack", "bona_fide"}
                or row["detector_status"] not in {"success", "failed"}
                or row["official_split"] not in {"train", "test"}
                or (source and row["role"] not in PRIORITY)
                or (not source and row["role"] is not None)
                or row["source_use_policy_id"] != POLICY_ID
                or row["source_use_eligible"] is not (source and index not in excluded)):
            raise ValueError("archived source/null-test eligibility drift")
    for item in exclusions:
        left, right = rows[item["excluded_index"]], rows[item["retained_index"]]
        if (left["official_split"] != "train" or left["video_id"] != item["excluded_video_id"]
                or right["video_id"] != item["retained_video_id"]
                or right["index"] in excluded
                or any(left[key] != right[key] for key in (
                    "media_sha256", "decoded_rgb_sequence_sha256", "binary_label"))):
            raise ValueError("exclusion is not joined to a retained exact-content original")
        if right["official_split"] == "train" and PRIORITY.index(right["role"]) >= PRIORITY.index(left["role"]):
            raise ValueError("source retention violates the adopted fixed role priority")
    active = [row for row in rows if row["source_use_eligible"] or row["official_split"] == "test"]
    for field in ("media_sha256", "decoded_rgb_sequence_sha256"):
        signatures = {}
        for row in active:
            digest = row[field]
            if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
                raise ValueError("active exact-content SHA256 required")
            signature = (row["official_split"], row["role"], row["binary_label"])
            if digest in signatures and signatures[digest] != signature:
                raise ValueError("effective use has forbidden exact-content crossing")
            signatures[digest] = signature
    expected = policy["effective_role_counts"]
    for role in (*PRIORITY, None):
        selected = [row for row in active if row["role"] == role]
        entry = expected[role or "official_test_null_role"]
        actual = {"originals": len(selected), "bona_fide": sum(r["binary_label"] == "bona_fide" for r in selected),
                  "attack": sum(r["binary_label"] == "attack" for r in selected),
                  "detector_success": sum(r["detector_status"] == "success" for r in selected),
                  "detector_failure": sum(r["detector_status"] == "failed" for r in selected)}
        if any(entry[key] != value for key, value in actual.items()):
            raise ValueError("effective role/class/detector counts do not reconcile")
    if (sum(r["source_use_eligible"] for r in rows) != policy["source_use_originals"]
            or len(active) != policy["active_originals"]
            or sum(r["official_split"] == "test" for r in rows) != policy["official_test_originals"]):
        raise ValueError("source/test use denominators do not reconcile")
    binding = use_binding(policy_payload)
    return SourceUseContext(MappingProxyType(binding),
                            tuple(MappingProxyType({**row, "source_use_binding": dict(binding)}) for row in rows))
