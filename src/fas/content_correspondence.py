"""Finite moving-content witnesses; no negative lineage dispositions."""

from __future__ import annotations

import hashlib
import json

import cv2
import numpy as np


PARAMETERS = {
    "quantiles": 9, "max_dimension": 512, "features": 600,
    "fast_threshold": 12, "motion_difference": 12, "motion_dilation": 5,
    "ratio": 0.7, "ransac_pixels": 3.0, "minimum_inliers": 20,
    "minimum_inlier_fraction": 0.6, "minimum_hull_fraction": 0.02,
    "temporal_offsets": [-2, -1, 0, 1, 2], "consecutive_support": 3,
    "maximum_corner_drift": 6.0,
}


def sample_orders(count: int) -> list[int]:
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise ValueError("invalid decoded count")
    return sorted({(count - 1) * slot // 8 for slot in range(9)})


def sequence_features(frames: list[np.ndarray]) -> list[dict]:
    if not frames or len(frames) > 9:
        raise ValueError("expected one to nine chronological RGB samples")
    cv2.setNumThreads(1)
    extractor = cv2.ORB_create(nfeatures=600, fastThreshold=12, edgeThreshold=15)
    previous = None
    shape = None
    result = []
    for rgb in frames:
        if rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[2] != 3 or min(rgb.shape[:2]) < 32:
            raise ValueError("invalid RGB sample")
        if shape is not None and rgb.shape != shape:
            raise ValueError("variable dimensions require an explicit method decision")
        shape = rgb.shape
        scale = min(1.0, 512 / max(rgb.shape[:2]))
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        if scale < 1:
            gray = cv2.resize(gray, (round(gray.shape[1] * scale), round(gray.shape[0] * scale)), interpolation=cv2.INTER_AREA)
        mask = np.zeros_like(gray) if previous is None else np.where(cv2.absdiff(gray, previous) > 12, 255, 0).astype(np.uint8)
        mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
        keypoints, descriptors = extractor.detectAndCompute(gray, mask)
        points = np.array([point.pt for point in keypoints], np.float32).reshape(-1, 2)
        result.append({"points": points, "descriptors": descriptors, "shape": gray.shape,
                       "rgb_sha256": hashlib.sha256(rgb.tobytes()).hexdigest()})
        previous = gray
    return result


def frame_witness(left: dict, right: dict) -> dict | None:
    if left["descriptors"] is None or right["descriptors"] is None or min(len(left["points"]), len(right["points"])) < 20:
        return None
    pairs = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(left["descriptors"], right["descriptors"], k=2)
    candidates = sorted((pair[0] for pair in pairs if len(pair) == 2 and pair[0].distance < 0.7 * pair[1].distance),
                        key=lambda match: (match.distance, match.queryIdx, match.trainIdx))
    used = set()
    matches = []
    for match in candidates:
        if match.trainIdx not in used:
            used.add(match.trainIdx)
            matches.append(match)
    if len(matches) < 20:
        return None
    first = np.array([left["points"][match.queryIdx] for match in matches], np.float32)
    second = np.array([right["points"][match.trainIdx] for match in matches], np.float32)
    cv2.setRNGSeed(0)
    matrix, mask = cv2.estimateAffinePartial2D(first, second, method=cv2.RANSAC,
                                            ransacReprojThreshold=3, maxIters=2000, confidence=0.99, refineIters=10)
    if matrix is None or mask is None or not np.isfinite(matrix).all():
        return None
    selected = mask.ravel().astype(bool)
    count = int(selected.sum())
    if count < 20 or count / len(matches) < 0.6:
        return None
    for points, feature in [(first[selected], left), (second[selected], right)]:
        if cv2.contourArea(cv2.convexHull(points)) / np.prod(feature["shape"]) < 0.02:
            return None
    height, width = left["shape"]
    corners = np.array([[0, 0, 1], [width, 0, 1], [0, height, 1], [width, height, 1]], np.float64) @ matrix.T
    quadrants = []
    for points, feature in [(first[selected], left), (second[selected], right)]:
        height, width = feature["shape"]
        cells = (points[:, 0] >= width / 2).astype(int) + 2 * (points[:, 1] >= height / 2).astype(int)
        quadrants.append(np.bincount(cells, minlength=4).tolist())
    return {"matrix": matrix.tolist(), "projected_corners": corners.tolist(), "inliers": count,
            "ratio_matches": len(matches), "quadrant_inliers": quadrants,
            "inlier_points": {"left": first[selected].tolist(), "right": second[selected].tolist()}}


def temporal_chain(hits: dict[tuple[int, int], dict]) -> list[dict]:
    for offset in PARAMETERS["temporal_offsets"]:
        for start in range(1, 7):
            keys = [(slot, slot + offset) for slot in range(start, start + 3)]
            if not all(key in hits for key in keys):
                continue
            witnesses = [hits[key] for key in keys]
            anchor = np.asarray(witnesses[0]["projected_corners"])
            if all(np.max(np.linalg.norm(np.asarray(value["projected_corners"]) - anchor, axis=1)) <= 6 for value in witnesses[1:]):
                return [{"left_slot": key[0], "right_slot": key[1], **value} for key, value in zip(keys, witnesses, strict=True)]
    return []


def compare_features(left: list[dict], right: list[dict]) -> dict:
    hits = {}
    tested = 0
    for first in range(1, len(left)):
        for offset in PARAMETERS["temporal_offsets"]:
            second = first + offset
            if 1 <= second < len(right):
                tested += 1
                witness = frame_witness(left[first], right[second])
                if witness is not None:
                    hits[first, second] = witness
    chain = temporal_chain(hits)
    return {"finding": "moving_content_correspondence_witness" if chain else "no_supported_witness_not_clearance",
            "tested_slot_pairs": tested, "geometric_hits": len(hits), "witnesses": chain,
            "feature_counts": [[len(value["points"]) for value in side] for side in (left, right)],
            "scientific_disposition": None, "capture_independence": False,
            "unresolved_reason": "witness_requires_scientific_review" if chain else "finite_method_non_detection_or_insufficient_features"}


def planned_edge_rows(members: list[dict], components: list[dict], frame_counts: dict[str, int]) -> list[dict]:
    ranks = [member["queue_rank"] for member in members]
    if any(isinstance(rank, bool) or not isinstance(rank, int) or rank < 0 for rank in ranks) or len(set(ranks)) != len(ranks):
        raise ValueError("invalid or duplicate frozen edge ranks")
    by_rank = {member["queue_rank"]: member for member in members}
    membership = {}
    for index, component in enumerate(components):
        vertices = set()
        if not component["ranks"] or len(set(component["ranks"])) != len(component["ranks"]):
            raise ValueError("empty or duplicate component ranks")
        digest = hashlib.sha256(json.dumps(component, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        for rank in component["ranks"]:
            if rank not in by_rank or rank in membership:
                raise ValueError("component edge mismatch")
            vertices.update((by_rank[rank]["left"], by_rank[rank]["right"]))
            membership[rank] = (index, digest)
        if vertices != set(component["videos"]) or len(vertices) != len(component["videos"]):
            raise ValueError("component endpoint mismatch")
    if set(membership) != set(ranks):
        raise ValueError("missing frozen component edge")
    endpoints = {member[side] for member in members for side in ("left", "right")}
    if set(frame_counts) != endpoints:
        raise ValueError("endpoint count mapping mismatch")
    rows = []
    for rank in sorted(ranks):
        member = by_rank[rank]
        digest = member["record_sha256"]
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ValueError("invalid frozen pair commitment")
        orders = {side: sample_orders(frame_counts[member[side]]) for side in ("left", "right")}
        rows.append({**member, "component_index": membership[rank][0], "component_sha256": membership[rank][1],
                     "planned_orders": orders, "method_coverage": "not_run_proposed_quantiles_motion_regions_only",
                     "evidence": [], "candidate_finding": None, "real_screening_performed": False,
                     "unresolved_reason": "real_media_method_execution_not_authorized",
                     "required_scientific_disposition": "pending_future_evidence_no_accepted_outcome",
                     "effective_disposition": None})
    return rows