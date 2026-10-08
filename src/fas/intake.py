"""Read-only acquisition evidence checks, without parsing media or labels."""

from __future__ import annotations

import hashlib
import re
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any

from .contracts import CORE_DOMAINS, MCIO_DOMAINS

DATASETS = CORE_DOMAINS | MCIO_DOMAINS | {"SiW-M", "CelebA-Spoof"}
PERMISSIONS = ("redistribution", "derived_frames", "model_weights", "metadata_counts")
EVIDENCE = ("channel", "license", "access_approval", "release", "protocol_documentation")
RECEIPT_FIELDS = {
    "version", "status", "dataset", "release_id", "protocol_id", "owner", "channel",
    "channel_reference", "downloaded_on", "permissions", "evidence", "raw_root",
    "archives", "protocols",
}


def _relative_path(value: Any) -> PurePosixPath | None:
    if not isinstance(value, str) or not value:
        return None
    if any(character in value for character in ("\\", ":")) or any(ord(character) < 32 or ord(character) == 127 for character in value):
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value or value == ".":
        return None
    return path


def check_intake(repo: Path, data_root: Path, receipt: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    repo = repo.resolve()
    data_root = data_root.resolve()
    if data_root.is_relative_to(repo) or repo.is_relative_to(data_root):
        errors.append("data_root must not overlap the repository")
    if not data_root.is_dir():
        errors.append("data_root must be an existing private directory")
    if set(receipt) != RECEIPT_FIELDS:
        errors.append("receipt must contain exactly the version-1 acquisition fields")
    if type(receipt.get("version")) is not int or receipt.get("version") != 1:
        errors.append("version must be integer 1")
    if receipt.get("status") != "complete":
        errors.append("status must be complete")
    dataset = receipt.get("dataset")
    if not isinstance(dataset, str) or dataset not in DATASETS:
        errors.append("dataset must be a registered dataset")
    for field in ("release_id", "protocol_id", "owner", "channel_reference"):
        value = receipt.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a nonempty steward-supplied identifier")
    downloaded = receipt.get("downloaded_on")
    try:
        if not isinstance(downloaded, str) or date.fromisoformat(downloaded).isoformat() != downloaded:
            raise ValueError
    except ValueError:
        errors.append("downloaded_on must be an ISO calendar date")
    channel = receipt.get("channel")
    if channel not in ("official", "owner_designated", "owner_confirmed_mirror"):
        errors.append("channel must be official, owner_designated or owner_confirmed_mirror")
    permissions = receipt.get("permissions")
    if not isinstance(permissions, dict) or set(permissions) != set(PERMISSIONS):
        errors.append("permissions must explicitly cover the four publication/use categories")
    elif any(value not in ("allowed", "prohibited", "unknown") for value in permissions.values()):
        errors.append("permission values must be allowed, prohibited or unknown")

    def artifact(value: Any, field: str, prefix: PurePosixPath | None = None) -> Path | None:
        if not isinstance(value, dict) or set(value) != {"id", "relpath", "sha256"}:
            errors.append(f"{field} must contain exactly id, relpath and sha256")
            return
        if not isinstance(value["id"], str) or not value["id"].strip():
            errors.append(f"{field}.id must be nonempty")
        relative_path = _relative_path(value["relpath"])
        if relative_path is None:
            errors.append(f"{field}.relpath must be a safe POSIX relative path")
            return
        if prefix is not None and not relative_path.is_relative_to(prefix):
            errors.append(f"{field}.relpath must be under its declared storage category")
            return
        digest = value["sha256"]
        if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            errors.append(f"{field}.sha256 must be an actual SHA-256")
            return
        if errors and any(error.startswith("data_root") for error in errors):
            return
        try:
            path = (data_root / relative_path).resolve()
            if not path.is_relative_to(data_root) or path.is_relative_to(repo):
                errors.append(f"{field}.relpath escapes the private root")
                return
            if not path.is_file():
                raise ValueError("not a regular file")
            if path.stat().st_size == 0:
                errors.append(f"{field} must not be empty")
                return
            with path.open("rb") as source:
                actual = hashlib.file_digest(source, "sha256").hexdigest()
            if actual != digest:
                errors.append(f"{field}.sha256 differs from actual file bytes")
            return path
        except (OSError, ValueError, RuntimeError):
            errors.append(f"{field} is missing or unreadable")

    evidence = receipt.get("evidence")
    required = set(EVIDENCE) | ({"mirror_equivalence"} if channel == "owner_confirmed_mirror" else set())
    if not isinstance(evidence, dict) or set(evidence) != required:
        errors.append("evidence must contain the exact required agreement/release/protocol records")
    if isinstance(evidence, dict):
        for name in sorted(required):
            artifact(evidence.get(name), f"evidence.{name}")
    raw_prefix = _relative_path(receipt.get("raw_root"))
    if raw_prefix is not None and len(raw_prefix.parts) > 1 and raw_prefix.parts[0] == "raw":
        try:
            resolved_raw = (data_root / raw_prefix).resolve()
            if not resolved_raw.is_relative_to(data_root) or resolved_raw.is_relative_to(repo) or not resolved_raw.is_dir():
                errors.append("raw_root must be an existing contained private raw directory")
        except (OSError, RuntimeError):
            errors.append("raw_root must be an existing contained private raw directory")
    else:
        raw_prefix = None
        errors.append("raw_root must be a safe relative directory under raw/")
    for group, prefix in (("archives", PurePosixPath("downloads")), ("protocols", raw_prefix / "official_protocols" if raw_prefix else None)):
        entries = receipt.get(group)
        if not isinstance(entries, list) or not entries:
            errors.append(f"{group} must be a nonempty artifact list")
            continue
        if group == "protocols" and raw_prefix is None:
            continue
        identifiers: set[str] = set()
        paths: set[str] = set()
        resolved_paths: set[Path] = set()
        for index, entry in enumerate(entries):
            field = f"{group}[{index}]"
            resolved = artifact(entry, field, prefix)
            if resolved is not None:
                if resolved in resolved_paths:
                    errors.append(f"{field}.relpath aliases an already declared file")
                resolved_paths.add(resolved)
            if isinstance(entry, dict):
                for key, seen in (("id", identifiers), ("relpath", paths)):
                    value = entry.get(key)
                    if isinstance(value, str):
                        if value in seen:
                            errors.append(f"{field}.{key} is duplicated")
                        seen.add(value)
    return {
        "version": 1, "status": "verified" if not errors else "blocked", "errors": errors,
        "scope": "declared acquisition evidence and hashes only; not media inventory, license interpretation, data audit or extraction authorization",
        "no_media_decoding": True,
    }