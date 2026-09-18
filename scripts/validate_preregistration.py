#!/usr/bin/env python3
"""Validate frozen protocol artifacts and print their SHA-256 hashes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.preregistration import STAGES, artifact_hashes, validate_stage


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=STAGES, default="schema")
    args = parser.parse_args()
    errors = validate_stage(ROOT, args.stage)
    for name, digest in artifact_hashes(ROOT).items():
        print(f"{digest}  {name}")
    if errors:
        print("\nNOT READY:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"\n{args.stage.upper()} READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
