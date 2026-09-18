#!/usr/bin/env python3
"""Write an immutable source-only analysis-freeze record."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import build_analysis_freeze_record, write_immutable_record
from fas.preregistration import MICO_DOMAINS, artifact_hashes, load_config, validate_stage


def main() -> int:
    errors = validate_stage(ROOT, "source-dry-run")
    if errors:
        print("SOURCE DRY RUN NOT READY; freeze record not written:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip()
    if dirty:
        print("DIRTY WORKTREE; freeze record not written", file=sys.stderr)
        return 1
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    evidence_path = ROOT / "results" / "source-dry-run" / "evidence.json"
    evidence = load_config(evidence_path)
    seeds = load_config(ROOT / "configs" / "seeds_v1.yaml")["seeds"]
    record = build_analysis_freeze_record(
        created_at_utc=datetime.now(timezone.utc).isoformat(),
        created_from_commit=commit,
        artifact_sha256=artifact_hashes(ROOT),
        source_evidence_sha256=hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
        source_policy_sha256=evidence["source_policy_sha256"],
        outer_targets=sorted(MICO_DOMAINS),
        seeds=seeds,
        no_target_selection_input=evidence["no_target_selection_input"],
    )
    path = ROOT / "results" / "analysis-freeze" / "freeze_record.json"
    try:
        write_immutable_record(path, record)
    except FileExistsError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())