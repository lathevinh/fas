"""Exact decoded-content evidence without inferring acquisition provenance."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction


PRIORITY_NAMES = (
    "cross_role_conflicting_label", "cross_role", "cross_partition",
    "conflicting_label", "remaining",
)


def candidate_priority(pair: dict) -> int:
    for key in ("cross_role", "cross_partition", "conflicting_label"):
        if not isinstance(pair[key], bool):
            raise ValueError("invalid candidate boundary flag")
    if pair["cross_role"]:
        return 0 if pair["conflicting_label"] else 1
    if pair["cross_partition"]:
        return 2
    return 3 if pair["conflicting_label"] else 4


def decoded_tokens(media: dict) -> list[tuple]:
    index = media["frame_index"]
    count = media["frame_count"]
    if media["decode_status"] != "decoded" or isinstance(count, bool) or not isinstance(count, int) or count <= 0 or count != len(index):
        raise ValueError("missing successful full-frame evidence")
    tokens = []
    previous = None
    for order, frame in enumerate(index):
        digest = frame["rgb_sha256"]
        if not isinstance(digest, str) or len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ValueError("invalid accepted RGB digest")
        if frame["decode_order"] != order or isinstance(frame["decode_order"], bool) or frame["decode_success"] is not True:
            raise ValueError("invalid accepted frame order")
        for key in ("width", "height"):
            if isinstance(frame[key], bool) or not isinstance(frame[key], int) or frame[key] <= 0:
                raise ValueError("invalid accepted frame dimensions")
        timestamp = Fraction(frame["timestamp_seconds"])
        if previous is not None and timestamp < previous:
            raise ValueError("nonmonotone accepted timestamp")
        previous = timestamp
        tokens.append((frame["width"], frame["height"], digest))
    return tokens


def exact_content_evidence(left: dict, right: dict) -> dict:
    first, second = decoded_tokens(left), decoded_tokens(right)
    positions = defaultdict(list)
    for order, token in enumerate(second):
        positions[token].append(order)
    previous = {}
    longest, first_start, second_start = 0, None, None
    shared_comparisons = 0
    for first_order, token in enumerate(first):
        current = {}
        for second_order in positions[token]:
            shared_comparisons += 1
            length = previous.get(second_order - 1, 0) + 1
            current[second_order] = length
            if length > longest:
                longest = length
                first_start = first_order - length + 1
                second_start = second_order - length + 1
        previous = current
    shared_unique = len(set(first) & set(second))
    complete_shorter = longest == min(len(first), len(second))
    moving_evidence = complete_shorter and len(set(first[first_start:first_start + longest])) >= 2
    confirmed = bool(moving_evidence)
    return {
        "left_frame_count": len(first), "right_frame_count": len(second),
        "shared_unique_rgb_frames": shared_unique, "equal_frame_position_comparisons": shared_comparisons,
        "longest_exact_contiguous_run": longest, "left_run_start": first_start, "right_run_start": second_start,
        "complete_shorter_sequence_contained": complete_shorter,
        "evidence_scope": "dimension_and_RGB_SHA256_equal_ordered_decoded_content_only",
        "disposition": "confirmed_same_content_or_derived_lineage" if confirmed else "uncertain_insufficient_evidence",
        "reason": "complete_shorter_ordered_RGB_sequence_with_multiple_distinct_frames" if confirmed else
                  "exact_overlap_does_not_resolve_reencoded_cropped_or_independent_capture_relation",
        "capture_provenance_confirmed": False, "visual_review_performed": False,
        "false_positive_rejection_authorized": False,
    }