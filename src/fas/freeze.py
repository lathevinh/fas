"""Immutable analysis-freeze record construction."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any


MCIO_DOMAINS = {"OULU-NPU", "CASIA-FASD", "Replay-Attack", "MSU-MFSD"}


def build_analysis_freeze_record(
    *,
    created_at_utc: str,
    created_from_commit: str,
    artifact_sha256: Mapping[str, str],
    source_evidence_sha256: str,
    source_policy_sha256: str,
    outer_targets: Sequence[str],
    seeds: Sequence[int],
    no_target_selection_input: bool,
) -> dict[str, Any]:
    """Validate source-only inputs and return a deterministic freeze payload."""
    try:
        timestamp = datetime.fromisoformat(created_at_utc)
    except ValueError as exc:
        raise ValueError("created_at_utc must be an ISO-8601 timestamp") from exc
    if timestamp.utcoffset() is None or timestamp.utcoffset().total_seconds() != 0:
        raise ValueError("created_at_utc must include the UTC offset")
    if not _hex_digest(created_from_commit, length=40):
        raise ValueError("created_from_commit must be a 40-character hexadecimal commit")
    if not artifact_sha256 or any(
        not isinstance(name, str) or not name or not _hex_digest(digest)
        for name, digest in artifact_sha256.items()
    ):
        raise ValueError("artifact_sha256 requires named SHA-256 digests")
    if not _hex_digest(source_evidence_sha256) or not _hex_digest(source_policy_sha256):
        raise ValueError("source evidence and policy require SHA-256 digests")
    if set(outer_targets) != MCIO_DOMAINS or len(outer_targets) != 4:
        raise ValueError("freeze record requires each MCIO outer target exactly once")
    if len(seeds) != 3 or len(set(seeds)) != 3 or any(
        not isinstance(seed, int) or isinstance(seed, bool) for seed in seeds
    ):
        raise ValueError("freeze record requires exactly three unique integer seeds")
    if no_target_selection_input is not True:
        raise ValueError("target-derived selection lineage is forbidden")
    return {
        "version": 2,
        "created_at_utc": created_at_utc,
        "created_from_commit": created_from_commit,
        "artifact_sha256": dict(sorted(artifact_sha256.items())),
        "source_evidence_sha256": source_evidence_sha256,
        "source_policy_sha256": source_policy_sha256,
        "outer_targets": sorted(outer_targets),
        "seeds": list(seeds),
        "no_target_selection_input": True,
    }


def write_immutable_record(path: Path, record: Mapping[str, Any]) -> None:
    """Atomically create a JSON record without permitting overwrite."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"immutable record already exists: {path}")
    payload = json.dumps(record, indent=2, sort_keys=True) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            raise FileExistsError(f"immutable record already exists: {path}") from None
    finally:
        temporary.unlink(missing_ok=True)


def _hex_digest(value: object, length: int = 64) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(character in "0123456789abcdef" for character in value)
    )