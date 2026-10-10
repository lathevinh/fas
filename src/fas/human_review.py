"""Bound human attestations, never synthesized by the assistant."""

from __future__ import annotations

import hashlib
import subprocess
from datetime import datetime
from pathlib import Path

import numpy as np

from .lineage import decoded_tokens


DISPOSITIONS = {"confirmed_same_content_or_derived_lineage", "rejected_false_positive", "uncertain_insufficient_evidence"}


def full_resolution_frames(path: Path, media: dict, orders: list[int]) -> dict[int, np.ndarray]:
    tokens = decoded_tokens(media)
    if not orders or len(set(orders)) != len(orders) or any(isinstance(order, bool) or not isinstance(order, int) or not 0 <= order < len(tokens) for order in orders):
        raise ValueError("invalid full-resolution ranks")
    if len({token[:2] for token in tokens}) != 1:
        raise ValueError("variable dimensions unsupported")
    width, height = tokens[0][:2]
    selected = sorted(orders)
    expression = "+".join(f"eq(n\\,{order})" for order in selected)
    result = subprocess.run([
        "ffmpeg", "-nostdin", "-v", "error", "-xerror", "-err_detect", "explode",
        "-threads", "1", "-i", str(path), "-map", "0:v:0", "-an", "-sn", "-dn",
        "-vf", "select=" + expression, "-pix_fmt", "rgb24", "-threads", "1",
        "-vsync", "0", "-f", "rawvideo", "-",
    ], capture_output=True, timeout=180, check=False)
    size = width * height * 3
    if result.returncode or result.stderr.strip() or len(result.stdout) != size * len(selected):
        raise ValueError("full-resolution decode failed")
    frames = {}
    for position, order in enumerate(selected):
        payload = result.stdout[position * size:(position + 1) * size]
        if hashlib.sha256(payload).hexdigest() != tokens[order][2]:
            raise ValueError("accepted full-resolution RGB mismatch")
        frames[order] = np.frombuffer(payload, dtype=np.uint8).reshape(height, width, 3).copy()
    return frames


def validate_human_review(record: dict, definition: dict) -> list[dict]:
    if record.get("version") != 1 or isinstance(record.get("version"), bool):
        raise ValueError("invalid human review version")
    reviewer = record.get("reviewer", {})
    if reviewer.get("kind") not in {"owner_human", "designated_human"} or not isinstance(reviewer.get("id"), str) or not reviewer["id"].strip():
        raise ValueError("actual owner/human reviewer required")
    if reviewer.get("personally_inspected_bound_evidence") is not True:
        raise ValueError("personal inspection attestation required")
    if record.get("review_definition_sha256") != definition["sha256"]:
        raise ValueError("review definition drift")
    timestamp = datetime.fromisoformat(record.get("reviewed_at_utc", ""))
    if timestamp.utcoffset() is None or timestamp.utcoffset().total_seconds() != 0:
        raise ValueError("UTC review timestamp required")
    rows = record.get("pairs")
    if not isinstance(rows, list) or len(rows) != 10 or {row.get("queue_rank") for row in rows} != set(range(10)):
        raise ValueError("all ten unique pair dispositions required")
    outcomes = []
    for row in sorted(rows, key=lambda row: row["queue_rank"]):
        rank = row["queue_rank"]
        if isinstance(rank, bool) or not isinstance(rank, int):
            raise ValueError("invalid queue rank")
        expected = definition["pairs"][rank]
        if row.get("packet_sha256") != expected["packet_sha256"] or row.get("reviewed_assets_sha256") != expected["required_assets_sha256"]:
            raise ValueError("bound packet/full-resolution evidence required")
        if row.get("personally_reviewed") is not True or row.get("disposition") not in DISPOSITIONS:
            raise ValueError("actual per-pair human disposition required")
        if not isinstance(row.get("rationale"), str) or not row["rationale"].strip():
            raise ValueError("pair rationale required")
        if row.get("capture_provenance_certified") is not False:
            raise ValueError("visual evidence cannot certify capture provenance")
        disagreement = row["disposition"] != expected["ai_disposition"]
        outcomes.append({**row, "ai_disposition": expected["ai_disposition"], "disagreement": disagreement,
                         "reconciliation_required": disagreement,
                         "effective_disposition": "uncertain_insufficient_evidence" if disagreement else row["disposition"],
                         "stop_for_prospective_scientific_decision": row["disposition"] == "confirmed_same_content_or_derived_lineage",
                         "model_execution_authorized": False, "scientific_readiness": False})
    return outcomes