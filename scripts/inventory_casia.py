#!/usr/bin/env python3
"""Inspect private CASIA RAR headers using a pinned Bob schema and reader wheel."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.casia import RAR_READER, inventory_headers, verify_bob_sources
from fas.freeze import write_immutable_record


def load_reader(wheel: Path):
    resolved = wheel.resolve()
    with resolved.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    if digest != RAR_READER["wheel_sha256"]:
        raise ValueError("reader wheel differs from pinned bytes")
    sys.path.insert(0, str(resolved))
    try:
        reader = importlib.import_module("rarfile")
    finally:
        sys.path.remove(str(resolved))
    if reader.__version__ != RAR_READER["version"] or not Path(reader.__file__).resolve().is_relative_to(resolved):
        raise ValueError("reader import does not originate from the pinned wheel")
    return reader


def read_headers(reader, archive_path: Path) -> list[dict]:
    with reader.RarFile(archive_path) as archive:
        if archive.needs_password():
            raise ValueError("encrypted archive is not supported")
        records = []
        for info in archive.infolist():
            if info.is_symlink() or info.file_redir:
                kind = "link"
            elif info.is_dir():
                kind = "directory"
            elif info.is_file():
                kind = "file"
            else:
                kind = "unsupported"
            records.append({
                "relpath": info.filename, "byte_size": info.file_size,
                "kind": kind, "encrypted": info.needs_password(),
            })
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True, help="private local CASIA RAR outside the repository")
    parser.add_argument("--reader-wheel", type=Path, required=True, help="pinned rarfile wheel; not installed into the locked stack")
    parser.add_argument("--bob-source-root", type=Path, required=True, help="private reference cache containing pinned __init__.py and models.py")
    parser.add_argument("--release-id", required=True, help="explicit steward identifier, not an accepted acquisition identity")
    parser.add_argument("--protocol-id", required=True, help="explicit reference protocol identifier")
    parser.add_argument("--unverified-local", action="store_true", required=True, help="acknowledge unverified acquisition and owner schema")
    parser.add_argument("--require-full-reference", action="store_true", help="require every path in Bob's complete train/test universe")
    parser.add_argument("--out", type=Path, required=True, help="new immutable private inventory")
    args = parser.parse_args()
    try:
        archive = args.archive.resolve()
        wheel = args.reader_wheel.resolve()
        sources = args.bob_source_root.resolve()
        output = args.out.resolve()
        if not archive.is_file() or not wheel.is_file() or not sources.is_dir():
            raise ValueError("private inputs must exist")
        if any(path.is_relative_to(ROOT) for path in (archive, wheel, sources)) or ROOT.is_relative_to(archive.parent) or ROOT.is_relative_to(sources):
            raise ValueError("inputs must not overlap the repository")
        if output.is_relative_to(ROOT) or output.is_relative_to(archive.parent) or output.is_relative_to(sources) or output == wheel or args.out.exists():
            raise ValueError("output must be a new private artifact, separate from inputs")
        source_hashes = verify_bob_sources(sources)
        reader = load_reader(wheel)
    except (ValueError, OSError, RuntimeError, ImportError):
        print("CASIA INVENTORY FAILED: invalid private inputs/output or reference/reader provenance", file=sys.stderr)
        return 2
    try:
        result = inventory_headers(
            read_headers(reader, archive), release_id=args.release_id,
            protocol_id=args.protocol_id, archive_name=archive.name,
            require_full_reference=args.require_full_reference,
        )
    except (ValueError, OSError, RuntimeError, UnicodeError, reader.Error):
        print(json.dumps({"status": "blocked", "errors": ["unsafe, encrypted, unreadable or reference-incompatible archive metadata"]}))
        return 1
    result["bob_source_sha256_verified"] = source_hashes
    try:
        write_immutable_record(args.out, result)
    except (ValueError, OSError, RuntimeError):
        print("CASIA INVENTORY FAILED: private output unavailable or already exists", file=sys.stderr)
        return 2
    print(json.dumps({
        "status": result["status"], "metadata_authority": "bob-reference",
        "acquisition_verified": False, "owner_schema_certified": False, "scientific_readiness": False,
        "no_media_decoding": True, "no_training_tensors": True,
        "scope": "reference-derived metadata only; not acquisition, media audit or scientific readiness",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())