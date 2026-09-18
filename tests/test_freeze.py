from __future__ import annotations

import json
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import build_analysis_freeze_record, write_immutable_record
from fas.preregistration import (
    MICO_DOMAINS,
    _validate_analysis_freeze,
    artifact_hashes,
    load_config,
)


class AnalysisFreezeContractTest(unittest.TestCase):
    def test_payload_is_deterministic_for_identical_inputs(self) -> None:
        kwargs = {
            "created_at_utc": "2026-09-18T00:00:00+00:00",
            "created_from_commit": "a" * 40,
            "artifact_sha256": {"configs/claims_v1.yaml": "b" * 64},
            "source_evidence_sha256": "c" * 64,
            "source_policy_sha256": "d" * 64,
            "outer_targets": ["OULU-NPU", "CASIA-FASD", "Replay-Attack", "MSU-MFSD"],
            "seeds": [20260917, 20260923, 20261001],
            "no_target_selection_input": True,
        }
        self.assertEqual(
            build_analysis_freeze_record(**kwargs),
            build_analysis_freeze_record(**kwargs),
        )

    def test_payload_rejects_target_lineage_and_malformed_hashes(self) -> None:
        base = {
            "created_at_utc": "2026-09-18T00:00:00+00:00",
            "created_from_commit": "a" * 40,
            "artifact_sha256": {"config": "b" * 64},
            "source_evidence_sha256": "c" * 64,
            "source_policy_sha256": "d" * 64,
            "outer_targets": ["OULU-NPU", "CASIA-FASD", "Replay-Attack", "MSU-MFSD"],
            "seeds": [20260917, 20260923, 20261001],
        }
        with self.assertRaises(ValueError):
            build_analysis_freeze_record(**base, no_target_selection_input=False)
        with self.assertRaises(ValueError):
            build_analysis_freeze_record(
                **{**base, "source_evidence_sha256": "bad"},
                no_target_selection_input=True,
            )

    def test_immutable_writer_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "freeze.json"
            record = {"version": 2, "created_from_commit": "a" * 40}
            write_immutable_record(path, record)
            original = path.read_bytes()
            with self.assertRaises(FileExistsError):
                write_immutable_record(path, record)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(json.loads(path.read_text()), record)

    def test_validation_rederives_commit_lineage_and_exact_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            evidence_path = root / "results" / "source-dry-run" / "evidence.json"
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            evidence = {
                "version": 1,
                "no_target_selection_input": True,
                "artifact_sha256": {"synthetic": "e" * 64},
                "source_policy_sha256": "d" * 64,
            }
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            self._git(root, "init")
            self._git(root, "config", "user.email", "phase0@example.invalid")
            self._git(root, "config", "user.name", "Phase 0 Test")
            self._git(root, "add", ".")
            self._git(root, "commit", "-m", "synthetic source fixture")
            commit = self._git(root, "rev-parse", "HEAD")
            seeds = load_config(root / "configs" / "seeds_v1.yaml")["seeds"]
            record = build_analysis_freeze_record(
                created_at_utc="2026-09-18T00:00:00+00:00",
                created_from_commit=commit,
                artifact_sha256=artifact_hashes(root),
                source_evidence_sha256=hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
                source_policy_sha256=evidence["source_policy_sha256"],
                outer_targets=sorted(MICO_DOMAINS),
                seeds=seeds,
                no_target_selection_input=True,
            )
            record_path = root / "results" / "analysis-freeze" / "freeze_record.json"
            write_immutable_record(record_path, record)
            errors: list[str] = []
            _validate_analysis_freeze(root, errors)
            self.assertEqual(errors, [])

            contract_path = root / "src" / "fas" / "contracts.py"
            contract_path.write_text(contract_path.read_text() + "\n", encoding="utf-8")
            errors = []
            _validate_analysis_freeze(root, errors)
            self.assertTrue(any("clean worktree" in error for error in errors))
            self.assertTrue(any("current frozen artifacts" in error for error in errors))
            self._git(root, "checkout", "--", "src/fas/contracts.py")

            record_path.unlink()
            record["created_from_commit"] = "f" * 40
            record["artifact_sha256"]["unknown"] = "a" * 64
            write_immutable_record(record_path, record)
            errors = []
            _validate_analysis_freeze(root, errors)
            self.assertTrue(any("current frozen artifacts" in error for error in errors))

            record_path.unlink()
            evidence["no_target_selection_input"] = False
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            write_immutable_record(record_path, {**record, "created_from_commit": commit})
            errors = []
            _validate_analysis_freeze(root, errors)
            self.assertTrue(any("target selection" in error for error in errors))

    @staticmethod
    def _git(root: Path, *arguments: str) -> str:
        return subprocess.check_output(
            ["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()


if __name__ == "__main__":
    unittest.main()