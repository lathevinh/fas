#!/usr/bin/env python3
"""Write a Stage-0 freeze record after data evidence passes validation."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.preregistration import artifact_hashes, validate_stage


def main() -> int:
    errors = validate_stage(ROOT, "data")
    if errors:
        print("DATA NOT READY; freeze record not written:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    record = {
        "version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "created_from_commit": commit,
        "artifact_sha256": artifact_hashes(ROOT),
    }
    path = ROOT / "results" / "stage0" / "freeze_record.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())