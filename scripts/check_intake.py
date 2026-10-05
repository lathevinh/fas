#!/usr/bin/env python3
"""Check a private acquisition receipt and emit a redacted immutable report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.intake import check_intake
from fas.preregistration import load_config


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True, help="private JSON-compatible receipt outside Git")
    parser.add_argument("--data-root", type=Path, required=True, help="authorized private local release root")
    parser.add_argument("--out", type=Path, help="create a new redacted immutable report")
    args = parser.parse_args()
    try:
        if args.receipt.resolve().is_relative_to(ROOT):
            raise ValueError("receipt must be stored outside the repository")
        result = check_intake(ROOT, args.data_root, load_config(args.receipt))
        if args.out:
            output = args.out.resolve()
            if output == args.receipt.resolve() or output.is_relative_to(args.data_root.resolve()):
                raise ValueError("report output must not overlap private acquisition inputs")
            write_immutable_record(args.out, result)
    except (ValueError, OSError, RuntimeError):
        print("INTAKE CHECK FAILED: invalid input/output or inaccessible private evidence", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())