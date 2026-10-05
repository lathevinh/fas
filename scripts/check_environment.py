#!/usr/bin/env python3
"""Report Phase-1 environment blockers without importing or downloading models."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.environment import inspect_environment
from fas.freeze import write_immutable_record
from fas.preregistration import load_config


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, help="create an immutable JSON report")
    args = parser.parse_args()
    try:
        result = inspect_environment(ROOT, load_config(ROOT / "configs/environment_v1.yaml"))
        if args.out:
            write_immutable_record(args.out, result)
    except (ValueError, OSError) as exc:
        print(f"ENVIRONMENT CHECK FAILED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())