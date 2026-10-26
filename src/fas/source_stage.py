"""Model-free prepared-source joins and fold-local input contracts."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import hashlib
from typing import Any

from .contracts import CORE_DOMAINS
from .source_use import PURPOSE_ROLES, SourceUseContext


def join_prepared(
    dataset: str, canonical: Sequence[Mapping[str, Any]], roles: Sequence[Mapping[str, Any]],
    prepared: Sequence[Mapping[str, Any]], *, active_config_sha256: str,
    siw_context: SourceUseContext | None = None,
) -> list[dict[str, Any]]:
    if dataset not in CORE_DOMAINS:
        raise ValueError("registered core dataset required")
    parents = {row["video_id"]: row for row in canonical}
    assigned = {row["video_id"]: row for row in roles}
    images = {row["video_id"]: row for row in prepared}
    if (len(parents) != len(canonical) or len(assigned) != len(roles)
            or len(images) != len(prepared) or set(images) != set(parents)
            or not set(assigned).issubset(parents)):
        raise ValueError("exact unique prepared/canonical/frozen-role identities required")
    if dataset == "SiW-Mv2":
        if siw_context is None or {r["video_id"] for r in siw_context.rows} != set(parents):
            raise ValueError("complete adopted SiW use context required")
        context = {row["video_id"]: row for row in siw_context.rows}
        if set(assigned) != {row["video_id"] for row in canonical if row["official_split"] == "train"}:
            raise ValueError("SiW frozen roles must match only the official train population")
    elif set(assigned) != set(parents):
        raise ValueError("all non-SiW originals require a permanent source role")
    result = []
    for identity, parent in parents.items():
        image = images[identity]
        role = assigned[identity]["role"] if identity in assigned else None
        if (parent["dataset"] != dataset or parent["binary_label"] not in {"bona_fide", "attack"}
                or image["binary_label"] != parent["binary_label"] or image["role"] != role
                or image["active_config_sha256"] != active_config_sha256
                or image["retain_original_denominator"] is not True or image["replacement"] is not False
                or image["model_score"] is not None or image["classifier_error"] is not None):
            raise ValueError("prepared image/label/role/preprocessing/score provenance drift")
        if role is not None:
            assigned_row = assigned[identity]
            if (role not in PURPOSE_ROLES.values() or assigned_row["binary_label"] != parent["binary_label"]
                    or assigned_row["dataset"] != dataset
                    or assigned_row["subject_id"] != (parent["subject_id"] or "")):
                raise ValueError("frozen role/class/group binding drift")
        selected = image["selected_frame"]
        detector = image["detector_status"]
        if detector not in {"success", "failed", "not_run"}:
            raise ValueError("unknown prepared detector disposition")
        if ((detector == "not_run") != (selected is None)
                or (detector != "success" and image["final_k1_action"] != "non_accept")):
            raise ValueError("technical/detector failure must retain non_accept and original denominator")
        if selected is not None and (
            selected.get("decode_order") is None or selected.get("rgb_sha256") is None
            or selected.get("even_length_tie") != "earlier_decoded_frame"
            or selected["decode_order"] != (selected["eligible_frame_count"] - 1) // 2
        ):
            raise ValueError("prepared original must preserve the fixed earlier-middle frame")
        crops = {}
        for resolution in (224, 518):
            matching = [path for path in image.get("asset_sha256", {}) if path.endswith(f"-{resolution}.png")]
            if detector == "success":
                if len(matching) != 1:
                    raise ValueError("successful prepared source requires each native branch crop")
                crops[str(resolution)] = {
                    "path": str(image["asset_root"]) + "/" + matching[0],
                    "sha256": image["asset_sha256"][matching[0]],
                }
            elif matching:
                raise ValueError("failed source cannot provide model-input crops")
        binding = None
        source_eligible = role is not None
        if dataset == "SiW-Mv2":
            use = context[identity]
            if (use["official_split"] != parent["official_split"] or use["role"] != role
                    or use["binary_label"] != parent["binary_label"]
                    or use["detector_status"] != detector):
                raise ValueError("prepared/adopted SiW eligibility join drift")
            source_eligible = use["source_use_eligible"]
            binding = dict(siw_context.binding)
        result.append({
            "dataset": dataset, "video_id": identity, "subject_id": parent["subject_id"],
            "official_split": parent["official_split"], "role": role,
            "binary_label": parent["binary_label"], "group_unit": parent["group_unit"],
            "group_id": parent["group_id"], "source_use_eligible": source_eligible,
            "source_use_binding": binding, "detector_status": detector,
            "selected_frame": selected, "model_input_eligible": source_eligible and detector == "success",
            "score_fit_eligible": False, "model_score": None, "classifier_error": None,
            "final_k1_action": image["final_k1_action"], "retain_original_denominator": True,
            "active_config_sha256": active_config_sha256, "crops": crops,
            "record_path": image.get("record_path"), "record_sha256": image.get("record_sha256"),
            "failure_kind": "pre_detector" if selected is None else "detector" if detector == "failed" else None,
        })
    return result


def population_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if len({(row["dataset"], row["video_id"]) for row in rows}) != len(rows):
        raise ValueError("duplicate integrated source identity")
    return {
        "archived": len(rows),
        "source_use": sum(row["source_use_eligible"] for row in rows),
        "model_input": sum(row["model_input_eligible"] for row in rows),
        "actual_score_fit": sum(row["score_fit_eligible"] for row in rows),
        "pre_detector_failure": sum(row["failure_kind"] == "pre_detector" for row in rows),
        "detector_failure": sum(row["failure_kind"] == "detector" for row in rows),
        "source_use_failures": sum(row["source_use_eligible"] and row["failure_kind"] is not None for row in rows),
        "source_excluded": sum(not row["source_use_eligible"] and row["role"] is not None for row in rows),
        "null_role_test": sum(row["role"] is None for row in rows),
        "roles": {
            role: {
                "archived": sum(row["role"] == role for row in rows),
                "source_use": sum(row["role"] == role and row["source_use_eligible"] for row in rows),
                "model_input": sum(row["role"] == role and row["model_input_eligible"] for row in rows),
                "class_counts": dict(Counter(row["binary_label"] for row in rows
                                            if row["role"] == role and row["source_use_eligible"])),
            } for role in PURPOSE_ROLES.values()},
    }


def source_inputs(
    rows: Sequence[Mapping[str, Any]], *, outer_target: str, purpose: str,
    pseudo_target: str | None = None, model_inputs_only: bool = False,
) -> list[Mapping[str, Any]]:
    if (outer_target not in CORE_DOMAINS or purpose not in PURPOSE_ROLES
            or (pseudo_target is not None and (pseudo_target not in CORE_DOMAINS or pseudo_target == outer_target))):
        raise ValueError("registered outer/pseudo-target and consumer purpose required")
    result = []
    for row in rows:
        if row["dataset"] in {outer_target, pseudo_target} or not row["source_use_eligible"]:
            continue
        if row["role"] != PURPOSE_ROLES[purpose]:
            continue
        if row["dataset"] == "SiW-Mv2" and not row["source_use_binding"]:
            raise ValueError("SiW source consumer requires exact adopted use binding")
        if model_inputs_only and not row["model_input_eligible"]:
            continue
        result.append(row)
    return result


def require_source_input(
    row: Mapping[str, Any], *, outer_target: str, purpose: str, pseudo_target: str | None = None,
    model_input: bool = False,
) -> None:
    if not source_inputs([row], outer_target=outer_target, purpose=purpose,
                         pseudo_target=pseudo_target, model_inputs_only=model_input):
        raise ValueError("outer/pseudo-target, excluded/test, wrong-role or failed input is forbidden")


def pilot_inputs(rows: Sequence[Mapping[str, Any]], *, outer_target: str = "OULU-NPU") -> list[Mapping[str, Any]]:
    candidates = source_inputs(rows, outer_target=outer_target, purpose="fitting", model_inputs_only=True)
    selected = []
    for dataset in sorted(CORE_DOMAINS - {outer_target}):
        for label in ("bona_fide", "attack"):
            group = [row for row in candidates if row["dataset"] == dataset and row["binary_label"] == label]
            group.sort(key=lambda row: hashlib.sha256(
                f"source295-pilot:{dataset}:{row['video_id']}".encode()).hexdigest())
            if len(group) < 4:
                raise ValueError("four deterministic successful train inputs per source/class required")
            selected.extend(group[:4])
    return selected
