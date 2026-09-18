from __future__ import annotations

import sys
import csv
import hashlib
import json
import shutil
import tempfile
import unittest
from contextlib import contextmanager
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.preregistration import (
    CONFIG_FILES,
    DATASET_COLUMNS,
    SPLIT_COLUMNS,
    artifact_hashes,
    validate,
    validate_stage,
)


class PreregistrationTest(unittest.TestCase):
    def test_frozen_config_schema_is_valid(self) -> None:
        self.assertEqual(validate(ROOT, require_counts=False), [])

    def test_readiness_is_blocked_until_real_counts_are_audited(self) -> None:
        errors = validate(ROOT, require_counts=True)
        self.assertTrue(any("unaudited dataset" in error for error in errors))

    def test_all_frozen_artifacts_have_hashes(self) -> None:
        hashes = artifact_hashes(ROOT)
        self.assertGreater(len(hashes), len(CONFIG_FILES) + 2)
        self.assertIn("src/fas/contracts.py", hashes)
        self.assertIn("scripts/write_freeze_record.py", hashes)
        self.assertTrue(all(len(digest) == 64 for digest in hashes.values()))

    def test_schema_rejects_empty_critical_configs(self) -> None:
        with self._copy() as copy:
            for name in ("preprocessing_v2.yaml", "claims_v1.yaml", "prompts_aux_v1.yaml"):
                (copy / "configs" / name).write_text("{}", encoding="utf-8")
            errors = validate_stage(copy, "schema")
            self.assertTrue(any("preprocessing requires" in error for error in errors))
            self.assertTrue(any("claim spec" in error for error in errors))
            self.assertTrue(any("auxiliary prompts" in error for error in errors))

    def test_schema_rejects_attack_family_names_in_core_prompts(self) -> None:
        with self._copy() as copy:
            path = copy / "configs" / "prompts_core_v1.yaml"
            config = json.loads(path.read_text())
            config["classes"]["spoof"].append("a printed face")
            path.write_text(json.dumps(config), encoding="utf-8")
            errors = validate_stage(copy, "schema")
            self.assertTrue(any("must not name" in error for error in errors))

    def test_later_stages_remain_explicitly_blocked(self) -> None:
        source_errors = validate_stage(ROOT, "source-dry-run")
        freeze_errors = validate_stage(ROOT, "analysis-freeze")
        locked_errors = validate_stage(ROOT, "locked-evaluation")
        self.assertTrue(any("source-dry-run evidence" in error for error in source_errors))
        self.assertTrue(any("missing immutable analysis-freeze record" in error for error in freeze_errors))
        self.assertTrue(any("locked-evaluation remains blocked" in error for error in locked_errors))

    def test_fake_counts_and_hashes_do_not_pass_data_stage(self) -> None:
        with self._copy() as copy:
            for name in ("dataset_summary.csv", "split_summary.csv"):
                path = copy / "manifests" / name
                path.write_text(path.read_text().replace("not_audited", "complete").replace(",,,,", ",1,1,1,1,"), encoding="utf-8")
            errors = validate_stage(copy, "data-audit")
            self.assertTrue(any("must be a positive integer" in error or "missing private evidence" in error for error in errors))

    def test_schema_rejects_changed_primary_effect(self) -> None:
        with self._copy() as copy:
            claims_path = copy / "configs" / "claims_v1.yaml"
            claims = json.loads(claims_path.read_text())
            claims["claims"]["rq2_complete_system"]["delta_min"] = 0
            claims_path.write_text(json.dumps(claims), encoding="utf-8")
            errors = validate_stage(copy, "schema")
            self.assertTrue(any("RQ2 claim" in error for error in errors))

    def test_data_stage_accepts_reconciled_synthetic_evidence(self) -> None:
        with self._copy() as copy:
            self._write_synthetic_evidence(copy)
            self.assertEqual(validate_stage(copy, "data-audit"), [])

    def test_data_stage_rejects_subject_role_overlap(self) -> None:
        with self._copy() as copy:
            self._write_synthetic_evidence(copy)
            role_path = copy / "manifests" / "private" / "oulu_npu_roles.csv"
            with role_path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            rows[2]["subject_id"] = rows[0]["subject_id"]
            self._write_csv(role_path, tuple(rows[0]), rows)
            self._update_hash(copy / "manifests" / "split_summary.csv", "OULU-NPU", "role_manifest_sha256", role_path)
            errors = validate_stage(copy, "data-audit")
            self.assertTrue(any("multiple roles" in error for error in errors))

    @contextmanager
    def _copy(self) -> Iterator[Path]:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "repo"
            shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            yield destination

    def _write_synthetic_evidence(self, root: Path) -> None:
        private = root / "manifests" / "private"
        private.mkdir(parents=True)
        dataset_rows = []
        split_rows = []
        for dataset in ("OULU-NPU", "CASIA-FASD", "Replay-Attack", "MSU-MFSD", "SiW-M"):
            roles = ["train", "branch_calibration", "routing_validation", "g_attack" if dataset == "SiW-M" else "g_domain"]
            metadata = []
            role_records = []
            for index, role in enumerate(roles):
                for label in ("attack", "bona_fide"):
                    subject = f"s{index}_{label}"
                    video = f"v{index}_{label}"
                    metadata.append({"dataset": dataset, "subject_id": subject, "video_id": video, "binary_label": label, "attack_family": "print" if label == "attack" else "", "official_split": "train"})
                    role_records.append({"dataset": dataset, "subject_id": subject, "video_id": video, "binary_label": label, "role": role})
            slug = dataset.lower().replace("-", "_")
            metadata_path = private / f"{slug}_metadata.csv"
            role_path = private / f"{slug}_roles.csv"
            self._write_csv(metadata_path, tuple(metadata[0]), metadata)
            self._write_csv(role_path, tuple(role_records[0]), role_records)
            dataset_rows.append({"dataset": dataset, "audit_status": "complete", "subjects": "8", "bona_videos": "4", "attack_videos": "4", "attack_families": "1", "metadata_source": "synthetic_test", "manifest_sha256": self._digest(metadata_path)})
            role_values = {f"{role}_{suffix}": "" for role in ("train", "branch_calibration", "g_domain", "routing_validation", "g_attack") for suffix in ("subjects", "attack_videos")}
            for role in roles:
                role_values[f"{role}_subjects"] = "2"
                role_values[f"{role}_attack_videos"] = "1"
            split_rows.append({"dataset": dataset, "audit_status": "complete", **role_values, "role_manifest_sha256": self._digest(role_path)})
        self._write_csv(root / "manifests" / "dataset_summary.csv", DATASET_COLUMNS, dataset_rows)
        self._write_csv(root / "manifests" / "split_summary.csv", SPLIT_COLUMNS, split_rows)

    @staticmethod
    def _write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, str]]) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _update_hash(self, summary_path: Path, dataset: str, column: str, evidence: Path) -> None:
        with summary_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            if row["dataset"] == dataset:
                row[column] = self._digest(evidence)
        self._write_csv(summary_path, tuple(rows[0]), rows)


if __name__ == "__main__":
    unittest.main()
