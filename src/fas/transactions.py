"""Prospective primary-frame selection and pre-detector failure disposition."""

from __future__ import annotations

import math
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from fractions import Fraction
from typing import Any


FROZEN_TRANSACTION_POLICY = {
    "version": 1, "state": "frozen_before_model_execution",
    "primary_frame": {
        "position": "middle_successfully_decoded_frame_in_valid_interval",
        "zero_based_rank": "floor((eligible_frame_count - 1) / 2)",
        "even_length_tie": "earlier_decoded_frame", "interval_boundary": "inclusive",
        "oulu_interval": "whole_supplied_video_no_temporal_bounds_in_accepted_metadata",
        "detector_success_replacement": False,
    },
    "technical_failure": {
        "action": "terminal_non_accept", "retain_canonical_id_and_role": True,
        "include_original_class_denominators": True, "include_technical_coverage_denominators": True,
        "exclude_score_dependent_fit_and_metrics": True, "calibration_fit_requires_valid_model_score": True,
        "model_score": None, "classifier_error": None, "detector_status": "not_run",
    },
    "canonical_or_role_rewrite_allowed": False, "split_or_seed_retry_allowed": False,
    "model_execution_authorized": False, "scientific_readiness": False,
}


def validate_transaction_policy(policy: Mapping[str, Any]) -> None:
    if json.dumps(policy, sort_keys=True) != json.dumps(FROZEN_TRANSACTION_POLICY, sort_keys=True):
        raise ValueError("transaction policy disagrees with frozen implementation")


def select_primary_frame(
    media: Mapping[str, Any], *, interval: tuple[str, str] | None = None,
) -> dict[str, Any] | None:
    status = media.get("decode_status")
    frames = media.get("frame_index")
    count = media.get("frame_count")
    if status not in {"decoded", "failed"} or not isinstance(frames, list) or type(count) is not int:
        raise ValueError("invalid media evidence")
    if status == "failed":
        if count != 0 or frames:
            raise ValueError("failed evidence cannot provide successful frames")
        return None
    if count <= 0 or len(frames) != count:
        raise ValueError("incomplete decode index")
    bounds = None if interval is None else tuple(Fraction(value) for value in interval)
    if bounds is not None and (len(bounds) != 2 or bounds[0] < 0 or bounds[1] < bounds[0]):
        raise ValueError("invalid official interval")
    eligible = []
    previous = None
    for order, frame in enumerate(frames):
        if not isinstance(frame, Mapping):
            raise ValueError("invalid frame evidence")
        timestamp = Fraction(frame["timestamp_seconds"])
        digest = frame.get("rgb_sha256")
        if (
            frame.get("decode_order") != order or type(frame.get("decode_order")) is not int
            or frame.get("decode_success") is not True
            or type(frame.get("width")) is not int or frame["width"] <= 0
            or type(frame.get("height")) is not int or frame["height"] <= 0
            or not isinstance(digest, str) or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
            or (previous is not None and timestamp < previous)
        ):
            raise ValueError("invalid successful frame evidence")
        previous = timestamp
        if bounds is None or bounds[0] <= timestamp <= bounds[1]:
            eligible.append(frame)
    if not eligible:
        return None
    frame = eligible[(len(eligible) - 1) // 2]
    return {
        "decode_order": frame["decode_order"], "timestamp_seconds": frame["timestamp_seconds"],
        "rgb_sha256": frame["rgb_sha256"], "width": frame["width"], "height": frame["height"],
        "eligible_frame_count": len(eligible), "even_length_tie": "earlier_decoded_frame",
    }


def technical_transaction(
    media: Mapping[str, Any], *, interval: tuple[str, str] | None = None,
) -> dict[str, Any]:
    if media.get("binary_label") not in {"attack", "bona_fide"}:
        raise ValueError("unknown transaction label")
    if media.get("role") not in {"train", "branch_calibration", "g_domain"}:
        raise ValueError("unknown permanent source role")
    if not isinstance(media.get("video_id"), str) or not media["video_id"]:
        raise ValueError("missing canonical identity")
    selected = select_primary_frame(media, interval=interval)
    failed = selected is None
    return {
        "video_id": media["video_id"], "binary_label": media["binary_label"], "role": media["role"],
        "selected_frame": selected,
        "technical_status": "terminal_failure" if failed else "primary_frame_available",
        "failure_stage": ("decode" if media["decode_status"] == "failed" else "valid_interval") if failed else None,
        "final_k1_action": "non_accept" if failed else None,
        "model_score": None, "classifier_error": None, "detector_status": "not_run",
        "score_fit_status": "ineligible_technical_failure" if failed else "pending_detector_and_model_score",
        "retain_original_denominator": True,
    }


def calibration_fit_rows(rows: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    result = []
    identities = set()
    for row in rows:
        identity = row.get("video_id")
        if not isinstance(identity, str) or not identity or identity in identities:
            raise ValueError("invalid or duplicate calibration transaction identity")
        identities.add(identity)
        if row.get("role") != "branch_calibration" or row.get("binary_label") not in {"attack", "bona_fide"}:
            raise ValueError("invalid calibration population")
        status = row.get("technical_status")
        if status not in {"terminal_failure", "primary_frame_available"}:
            raise ValueError("unknown technical disposition")
        score = row.get("model_score")
        if status == "terminal_failure":
            if score is not None or row.get("classifier_error") is not None or row.get("final_k1_action") != "non_accept":
                raise ValueError("technical failure cannot have classifier evidence")
            continue
        if score is None:
            continue
        if row.get("detector_status") != "success" or row.get("selected_frame") is None:
            raise ValueError("scores require successful detector and selected frame")
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score):
            raise ValueError("invalid calibration score")
        result.append(row)
    return result


def technical_population_counts(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter()
    identities = set()
    for row in rows:
        identity = row.get("video_id")
        if not isinstance(identity, str) or not identity or identity in identities:
            raise ValueError("invalid or duplicate population identity")
        identities.add(identity)
        role, label = row.get("role"), row.get("binary_label")
        if role not in {"train", "branch_calibration", "g_domain"} or label not in {"attack", "bona_fide"}:
            raise ValueError("unknown population stratum")
        status = row.get("technical_status")
        if row.get("retain_original_denominator") is not True or status not in {"terminal_failure", "primary_frame_available"}:
            raise ValueError("transaction cannot disappear from original denominator")
        if status == "terminal_failure" and (
            row.get("final_k1_action") != "non_accept" or row.get("model_score") is not None
            or row.get("classifier_error") is not None or row.get("selected_frame") is not None
        ):
            raise ValueError("invalid technical failure accounting")
        counts[(role, label, "population")] += 1
        counts[(role, label, status)] += 1
    return [{
        "role": role, "binary_label": label,
        "original_denominator": counts[(role, label, "population")],
        "terminal_technical_failures": counts[(role, label, "terminal_failure")],
        "primary_frame_available": counts[(role, label, "primary_frame_available")],
        "forced_bfnr_numerator": counts[(role, label, "terminal_failure")] if label == "bona_fide" else 0,
        "forced_false_accept_numerator": 0,
    } for role, label in sorted({(role, label) for role, label, _ in counts})]