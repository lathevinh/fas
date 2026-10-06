#!/usr/bin/env python3
"""Reconcile private OULU metadata without granting acquisition readiness."""

from __future__ import annotations

import argparse
import json
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.oulu import inventory_archives


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True, help="private directory containing supplied OULU archives and Readme.pdf")
    parser.add_argument("--release-id", required=True, help="explicit local identifier; acquisition identity remains unverified")
    parser.add_argument("--protocol-id", required=True, help="explicit local protocol identifier, not an intake acceptance")
    parser.add_argument("--unverified-local", action="store_true", required=True, help="acknowledge this is not a verified acquisition or data-audit run")
    parser.add_argument("--require-full-release", action="store_true", help="require the complete documented Phone/Session/User/File universe")
    parser.add_argument("--hash-media", action="store_true", help="read all archive/video bytes for SHA-256, without decoding; expensive on a full release")
    parser.add_argument("--out", type=Path, required=True, help="new immutable private inventory outside the repo and input directory")
    args = parser.parse_args()
    try:
        root = args.input_root.resolve()
        output = args.out.resolve()
        if root.is_relative_to(ROOT) or ROOT.is_relative_to(root) or not root.is_dir():
            raise ValueError("input root must be private")
        if output.is_relative_to(ROOT) or output.is_relative_to(root) or args.out.exists():
            raise ValueError("output must be a new private artifact")
    except (ValueError, OSError, RuntimeError):
        print("OULU INVENTORY FAILED: invalid or overlapping private input/output", file=sys.stderr)
        return 2
    try:
        result = inventory_archives(
            root, release_id=args.release_id, protocol_id=args.protocol_id,
            require_full_release=args.require_full_release, hash_media=args.hash_media,
        )
    except (ValueError, OSError, UnicodeError, RuntimeError, tarfile.TarError):
        print(json.dumps({"status": "blocked", "errors": ["local archive/protocol validation failed"]}))
        return 1
    try:
        write_immutable_record(args.out, result)
    except (ValueError, OSError, RuntimeError):
        print("OULU INVENTORY FAILED: private output unavailable or already exists", file=sys.stderr)
        return 2
    print(json.dumps({
        "status": result["status"], "acquisition_verified": False, "scientific_readiness": False,
        "no_media_decoding": True, "no_training_tensors": True,
        "scope": "local metadata reconciliation only; private inventory, unverified acquisition identity and unprobed media",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())