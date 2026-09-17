#!/usr/bin/env python3
"""Validate frozen protocol artifacts and print their SHA-256 hashes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.preregistration import artifact_hashes, validate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-incomplete-counts",
        action="store_true",
        help="validate frozen config schema while dataset audit is pending",
    )
    args = parser.parse_args()
    errors = validate(ROOT, require_counts=not args.allow_incomplete_counts)
    for name, digest in artifact_hashes(ROOT).items():
        print(f"{digest}  {name}")
    if errors:
        print("\nNOT READY:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    status = "CONFIG FROZEN; COUNTS PENDING" if args.allow_incomplete_counts else "PREREGISTRATION READY"
    print(f"\n{status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
