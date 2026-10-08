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
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.preregistration import (
    CONFIG_FILES,
    DATASET_COLUMNS,
    SPLIT_COLUMNS,
    artifact_hashes,
    _validate_locked_authorization,
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

    def test_data_stage_accepts_core_roles_without_optional_routing(self) -> None:
        with self._copy() as copy:
            self._write_synthetic_evidence(copy)
            for path in (copy / "manifests" / "private").glob("*_roles.csv"):
                self.assertNotIn("routing_validation", path.read_text())
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

    def test_data_stage_rejects_siwmv2_id_and_type_drift_even_with_new_hash(self) -> None:
        for field, value, message in (("video_id", "Paper_999999", "IDs do not match"),
                                      ("reference_attack_type", "Replay", "type coverage"),
                                      ("subject_id", "invented_subject", "unknown SiW-Mv2 subject_id")):
            with self.subTest(field=field), self._copy() as copy:
                self._write_synthetic_evidence(copy)
                path = copy / "manifests/private/siw_mv2_metadata.csv"
                with path.open(newline="", encoding="utf-8") as handle:
                    rows = list(csv.DictReader(handle))
                changed = next(row for row in rows if row["binary_label"] == "attack") if field == "reference_attack_type" else rows[0]
                changed[field] = value
                self._write_csv(path, tuple(rows[0]), rows)
                self._update_hash(copy / "manifests/dataset_summary.csv", "SiW-Mv2", "manifest_sha256", path)
                self.assertTrue(any(message in error for error in validate_stage(copy, "data-audit")))

    def test_data_stage_rejects_siwmv2_test_video_in_source_roles(self) -> None:
        with self._copy() as copy:
            self._write_synthetic_evidence(copy)
            metadata_path = copy / "manifests/private/siw_mv2_metadata.csv"
            role_path = copy / "manifests/private/siw_mv2_roles.csv"
            with metadata_path.open(newline="", encoding="utf-8") as handle:
                metadata = list(csv.DictReader(handle))
            with role_path.open(newline="", encoding="utf-8") as handle:
                roles = list(csv.DictReader(handle))
            target = next(row for row in metadata if row["official_split"] == "test")
            roles[0].update(video_id=target["video_id"], binary_label=target["binary_label"])
            self._write_csv(role_path, tuple(roles[0]), roles)
            self._update_hash(copy / "manifests/split_summary.csv", "SiW-Mv2", "role_manifest_sha256", role_path)
            self.assertTrue(any("target test video" in error for error in validate_stage(copy, "data-audit")))

    def test_source_dry_run_reconciles_required_artifacts_and_policy(self) -> None:
        with self._copy() as copy:
            self._write_synthetic_evidence(copy)
            self._write_source_evidence(copy)
            self.assertEqual(validate_stage(copy, "source-dry-run"), [])

    def test_source_dry_run_rejects_correctly_hashed_empty_artifacts(self) -> None:
        for name in ("competence.json", "applicability.json"):
            with self.subTest(name=name), self._copy() as copy:
                self._write_synthetic_evidence(copy)
                evidence_path = self._write_source_evidence(copy)
                artifact_path = copy / "results/source-dry-run" / name
                artifact_path.write_text(json.dumps({"version": 1, "no_target_selection_input": True}), encoding="utf-8")
                evidence = json.loads(evidence_path.read_text())
                evidence["artifact_sha256"][f"results/source-dry-run/{name}"] = self._digest(artifact_path)
                evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
                for stage in ("source-dry-run", "analysis-freeze", "locked-evaluation"):
                    errors = validate_stage(copy, stage)
                    self.assertTrue(any(name in error and "contents" in error for error in errors), errors)

    def test_source_evidence_rejects_invalid_science_and_lineage(self) -> None:
        cases = (
            ("competence.json", lambda payload: payload.update(version=True)),
            ("competence.json", lambda payload: payload.update(no_target_selection_input=False)),
            ("competence.json", lambda payload: payload["records"].pop()),
            ("competence.json", lambda payload: payload["records"].__setitem__(1, payload["records"][0])),
            ("competence.json", lambda payload: payload["records"][0].update(seed=1)),
            ("competence.json", lambda payload: payload["records"][0].update(source_domains=["OULU-NPU", "CASIA-FASD", "Replay-Attack"])),
            ("competence.json", lambda payload: payload["records"][0]["systems"]["heterogeneous"].update(macro_auroc=0.54)),
            ("competence.json", lambda payload: payload["records"][0]["systems"]["heterogeneous"].update(macro_balanced_accuracy=0.54)),
            ("competence.json", lambda payload: payload["records"][0]["systems"]["heterogeneous"].update(macro_auroc_lcb=0.50)),
            ("competence.json", lambda payload: payload["records"][0]["systems"]["heterogeneous"].update(score_range=1e-6)),
            ("competence.json", lambda payload: payload["records"][0]["systems"]["heterogeneous"].update(macro_auroc=float("nan"))),
            ("competence.json", lambda payload: payload["records"][0]["systems"]["heterogeneous"].update(macro_auroc=True)),
            ("competence.json", lambda payload: payload["records"][0]["systems"]["heterogeneous"].update(macro_auroc=1.1)),
            ("competence.json", lambda payload: payload["records"][0]["systems"]["heterogeneous"].update(both_classes=False)),
            ("competence.json", lambda payload: payload["records"][0]["systems"]["heterogeneous"].update(finite_calibration=False)),
            ("competence.json", lambda payload: payload["records"][0]["systems"]["dino_reg"].update(score_range=0, **{"pass": False})),
            ("competence.json", lambda payload: payload["records"][0]["heterogeneous_risk_fit"].update(error_count=19)),
            ("competence.json", lambda payload: payload["records"][0]["heterogeneous_risk_fit"].update(correct_count=True)),
            ("applicability.json", lambda payload: payload.update(n_error_min=0)),
            ("applicability.json", lambda payload: payload.update(target_event_support="eligible")),
            ("applicability.json", lambda payload: payload["records"][0]["claims"].update(rq1_oof_transfer="not_applicable")),
            ("applicability.json", lambda payload: payload["records"][0]["source_events"]["CASIA-FASD"].update(error_count=21)),
            ("applicability.json", lambda payload: payload["records"][0]["source_events"]["CASIA-FASD"].update(error_count=-1)),
            ("applicability.json", lambda payload: payload["records"][0]["source_events"]["CASIA-FASD"].update(ap_estimable=False)),
            ("applicability.json", lambda payload: payload["records"][0]["source_events"].update({"OULU-NPU": {}})),
        )
        for index, (name, mutate) in enumerate(cases):
            with self.subTest(index=index, name=name), self._copy() as copy:
                self._write_synthetic_evidence(copy)
                self._write_source_evidence(copy)
                path = copy / "results/source-dry-run" / name
                payload = json.loads(path.read_text())
                mutate(payload)
                self._rewrite_source_artifact(copy, name, payload)
                errors = validate_stage(copy, "source-dry-run")
                self.assertTrue(any("contents" in error for error in errors), errors)

    def test_complete_competence_accepts_inclusive_minimums(self) -> None:
        with self._copy() as copy:
            self._write_synthetic_evidence(copy)
            self._write_source_evidence(copy)
            payload = json.loads((copy / "results/source-dry-run/competence.json").read_text())
            for record in payload["records"]:
                for values in record["systems"].values():
                    values.update(macro_auroc=0.55, macro_balanced_accuracy=0.55, macro_auroc_lcb=0.500001, score_range=0.0000011)
            self._rewrite_source_artifact(copy, "competence.json", payload)
            self.assertEqual(validate_stage(copy, "source-dry-run"), [])

    def test_weak_standalone_branches_do_not_block_core_readiness(self) -> None:
        with self._copy() as copy:
            self._write_synthetic_evidence(copy)
            self._write_source_evidence(copy)
            payload = json.loads((copy / "results/source-dry-run/competence.json").read_text())
            for record in payload["records"]:
                for name in ("dino_reg", "openclip"):
                    record["systems"][name].update(macro_auroc=0.51, **{"pass": False})
            self._rewrite_source_artifact(copy, "competence.json", payload)
            self.assertEqual(validate_stage(copy, "source-dry-run"), [])

    def test_same_family_failure_scopes_applicability_to_rq2(self) -> None:
        with self._copy() as copy:
            self._write_synthetic_evidence(copy)
            self._write_source_evidence(copy)
            competence = json.loads((copy / "results/source-dry-run/competence.json").read_text())
            applicability = json.loads((copy / "results/source-dry-run/applicability.json").read_text())
            for record in competence["records"]:
                record["systems"]["same_family"].update(macro_auroc=0.51, **{"pass": False})
            self._rewrite_source_artifact(copy, "competence.json", competence)
            self.assertTrue(validate_stage(copy, "source-dry-run"))
            for record in applicability["records"]:
                record["claims"]["rq2_complete_system"] = "not_applicable"
            self._rewrite_source_artifact(copy, "applicability.json", applicability)
            self.assertEqual(validate_stage(copy, "source-dry-run"), [])

    def test_source_low_event_and_one_class_support_is_reported_not_fabricated(self) -> None:
        for error_count, estimable in ((8, True), (0, False)):
            with self.subTest(error_count=error_count), self._copy() as copy:
                self._write_synthetic_evidence(copy)
                self._write_source_evidence(copy)
                competence = json.loads((copy / "results/source-dry-run/competence.json").read_text())
                applicability = json.loads((copy / "results/source-dry-run/applicability.json").read_text())
                competence["records"][0]["heterogeneous_risk_fit"]["error_count"] = 40 + error_count
                applicability["records"][0]["source_events"]["CASIA-FASD"].update(error_count=error_count, ap_estimable=estimable, meets_n_error_min=False)
                self._rewrite_source_artifact(copy, "competence.json", competence)
                self._rewrite_source_artifact(copy, "applicability.json", applicability)
                self.assertEqual(validate_stage(copy, "source-dry-run"), [])

    def _rewrite_source_artifact(self, root: Path, name: str, payload: dict) -> None:
        path = root / "results/source-dry-run" / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        evidence_path = root / "results/source-dry-run/evidence.json"
        evidence = json.loads(evidence_path.read_text())
        evidence["artifact_sha256"][f"results/source-dry-run/{name}"] = self._digest(path)
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

    def test_source_dry_run_rejects_fake_unknown_and_stale_hashes(self) -> None:
        with self._copy() as copy:
            self._write_synthetic_evidence(copy)
            evidence_path = self._write_source_evidence(copy)
            evidence = json.loads(evidence_path.read_text())
            competence_path = copy / "results" / "source-dry-run" / "competence.json"
            competence_path.write_text('{"no_target_selection_input": false}', encoding="utf-8")
            evidence["artifact_sha256"]["unknown"] = "a" * 64
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            errors = validate_stage(copy, "source-dry-run")
            self.assertTrue(any("artifact set" in error for error in errors))
            self.assertTrue(any("does not match" in error for error in errors))
            self.assertTrue(any("target selection" in error for error in errors))

    def test_source_dry_run_rejects_nonexistent_valid_looking_artifact(self) -> None:
        with self._copy() as copy:
            self._write_synthetic_evidence(copy)
            evidence_path = self._write_source_evidence(copy)
            (copy / "results" / "source-dry-run" / "applicability.json").unlink()
            errors = validate_stage(copy, "source-dry-run")
            self.assertTrue(any("missing source-dry-run artifact" in error for error in errors))

    def test_locked_authorization_is_tied_to_analysis_freeze(self) -> None:
        with self._copy() as copy:
            freeze_path = copy / "results" / "analysis-freeze" / "freeze_record.json"
            freeze_path.parent.mkdir(parents=True, exist_ok=True)
            freeze = {
                "version": 2,
                "created_from_commit": "a" * 40,
                "artifact_sha256": artifact_hashes(copy),
                "outer_targets": ["CASIA-FASD", "MSU-MFSD", "OULU-NPU", "SiW-Mv2"],
                "seeds": [20260917, 20260923, 20261001],
            }
            freeze_path.write_text(json.dumps(freeze), encoding="utf-8")
            authorization_path = copy / "results" / "locked-evaluation" / "authorization.json"
            authorization_path.parent.mkdir(parents=True, exist_ok=True)
            authorization = {
                "version": 1,
                "state": "authorized",
                "analysis_freeze_sha256": self._digest(freeze_path),
                "created_from_commit": freeze["created_from_commit"],
                "experiment_config_sha256": freeze["artifact_sha256"]["configs/experiment_core_v1.yaml"],
                "claim_spec_sha256": freeze["artifact_sha256"]["configs/claims_v1.yaml"],
                "outer_targets": freeze["outer_targets"],
                "seeds": freeze["seeds"],
            }
            authorization_path.write_text(json.dumps(authorization), encoding="utf-8")
            errors: list[str] = []
            _validate_locked_authorization(copy, errors)
            self.assertEqual(errors, [])

            authorization["analysis_freeze_sha256"] = "f" * 64
            authorization_path.write_text(json.dumps(authorization), encoding="utf-8")
            errors = []
            _validate_locked_authorization(copy, errors)
            self.assertTrue(any("does not match" in error for error in errors))

    def test_locked_authorization_rejects_empty_record(self) -> None:
        with self._copy() as copy:
            authorization_path = copy / "results" / "locked-evaluation" / "authorization.json"
            authorization_path.parent.mkdir(parents=True, exist_ok=True)
            authorization_path.write_text("{}", encoding="utf-8")
            errors: list[str] = []
            _validate_locked_authorization(copy, errors)
            self.assertTrue(any("analysis-freeze record" in error or "authorization" in error for error in errors))

    @contextmanager
    def _copy(self) -> Iterator[Path]:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "repo"
            shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns(".git", "__pycache__", "oulu-npu", "casia-fasd", "SiW"))
            self.assertFalse((destination / "oulu-npu").exists())
            self.assertFalse((destination / "casia-fasd").exists())
            self.assertFalse((destination / "SiW").exists())
            yield destination

    def _write_synthetic_evidence(self, root: Path) -> None:
        private = root / "manifests" / "private"
        private.mkdir(parents=True)
        dataset_rows = []
        split_rows = []
        for dataset in ("OULU-NPU", "CASIA-FASD", "SiW-Mv2", "MSU-MFSD"):
            roles = ["train", "branch_calibration", "g_attack" if dataset == "SiW-M" else "g_domain"]
            metadata = []
            role_records = []
            for index, role in enumerate(roles):
                for label in ("attack", "bona_fide"):
                    subject = "" if dataset == "SiW-Mv2" else f"s{index}_{label}"
                    video = f"v{index}_{label}"
                    metadata.append({"dataset": dataset, "subject_id": subject, "video_id": video, "binary_label": label, "attack_family": "print" if label == "attack" else "", "official_split": "train"})
                    role_records.append({"dataset": dataset, "subject_id": subject, "video_id": video, "binary_label": label, "role": role})
            if dataset == "SiW-Mv2":
                public_path = root / "results/phase1/siwmv2-intersection-v1.json"
                public = json.loads(public_path.read_text())
                metadata = []
                role_records = []
                for split, offset in (("train", 0), ("test", 10000)):
                    sizes = {"Live": public["partitions"][split]["bona_fide"],
                             **{name: values[split] for name, values in public["reference_attack_type_coverage"].items()}}
                    for prefix, count in sizes.items():
                        for index in range(count):
                            video = f"{prefix}_{offset + index + 1}"
                            label = "bona_fide" if prefix == "Live" else "attack"
                            metadata.append({"dataset": dataset, "subject_id": "", "video_id": video,
                                             "binary_label": label, "attack_family": "" if prefix == "Live" else public["attack_family_mapping"][prefix],
                                             "official_split": split, "reference_attack_type": "" if prefix == "Live" else prefix,
                                             "attack_mapping_version": "siwmv2_attack_family_v1"})
                            if split == "train":
                                role_records.append({"dataset": dataset, "subject_id": "", "video_id": video,
                                                     "binary_label": label, "role": roles[len(role_records) % len(roles)]})
                    tokens = sorted(row["video_id"] for row in metadata if row["official_split"] == split)
                    public["partitions"][split]["eligible_ids_sha256"] = hashlib.sha256(("\n".join(tokens) + "\n").encode()).hexdigest()
                public_path.write_text(json.dumps(public), encoding="utf-8")
                digest = self._digest(public_path)
                benchmark_path = root / "configs/benchmark_amendment_v2.yaml"
                benchmark = json.loads(benchmark_path.read_text())
                benchmark["siwmv2_population"]["evidence_sha256"] = digest
                benchmark_path.write_text(json.dumps(benchmark), encoding="utf-8")
                fixture_pin = patch("fas.preregistration.INTERSECTION_SHA256", digest)
                fixture_pin.start()
                self.addCleanup(fixture_pin.stop)
            slug = dataset.lower().replace("-", "_")
            metadata_path = private / f"{slug}_metadata.csv"
            role_path = private / f"{slug}_roles.csv"
            self._write_csv(metadata_path, tuple(metadata[0]), metadata)
            self._write_csv(role_path, tuple(role_records[0]), role_records)
            group_unit = "video" if dataset == "SiW-Mv2" else "subject"
            dataset_rows.append({"dataset": dataset, "audit_status": "complete", "subjects": "" if dataset == "SiW-Mv2" else "6",
                                 "group_unit": group_unit, "groups": str(len(metadata)),
                                 "bona_videos": str(sum(row["binary_label"] == "bona_fide" for row in metadata)),
                                 "attack_videos": str(sum(row["binary_label"] == "attack" for row in metadata)),
                                 "attack_families": str(len({row["attack_family"] for row in metadata if row["binary_label"] == "attack"})),
                                 "metadata_source": "synthetic_test", "manifest_sha256": self._digest(metadata_path)})
            role_values = {f"{role}_{suffix}": "" for role in ("train", "branch_calibration", "g_domain", "routing_validation", "g_attack") for suffix in ("groups", "attack_videos")}
            for role in roles:
                role_values[f"{role}_groups"] = str(sum(row["role"] == role for row in role_records))
                role_values[f"{role}_attack_videos"] = str(sum(row["role"] == role and row["binary_label"] == "attack" for row in role_records))
            split_rows.append({"dataset": dataset, "audit_status": "complete", "group_unit": group_unit, **role_values, "role_manifest_sha256": self._digest(role_path)})
        self._write_csv(root / "manifests" / "dataset_summary.csv", DATASET_COLUMNS, dataset_rows)
        self._write_csv(root / "manifests" / "split_summary.csv", SPLIT_COLUMNS, split_rows)

    def _write_source_evidence(self, root: Path) -> Path:
        directory = root / "results" / "source-dry-run"
        directory.mkdir(parents=True, exist_ok=True)
        artifacts = {}
        competence = {"version": 1, "no_target_selection_input": True, "records": []}
        applicability = {"version": 1, "no_target_selection_input": True, "n_error_min": 20, "target_event_support": "not_inspected", "records": []}
        domains = ("OULU-NPU", "CASIA-FASD", "SiW-Mv2", "MSU-MFSD")
        for target in domains:
            for seed in (20260917, 20260923, 20261001):
                identity = {"outer_target": target, "seed": seed, "source_domains": [domain for domain in domains if domain != target]}
                metrics = {"macro_auroc": 0.6, "macro_balanced_accuracy": 0.6, "macro_auroc_lcb": 0.51, "score_range": 0.4, "finite_scores": True, "both_classes": True, "finite_calibration": True, "pass": True}
                competence["records"].append({**identity, "systems": {name: dict(metrics) for name in ("dino_reg", "openclip", "heterogeneous", "same_family")}, "dino_anchor_pass": True, "heterogeneous_risk_fit": {"error_count": 60, "correct_count": 60, "pass": True}})
                applicability["records"].append({**identity, "claims": {"rq1_oof_transfer": "eligible", "rq2_complete_system": "eligible"}, "source_events": {domain: {"error_count": 20, "correct_count": 20, "ap_estimable": True, "meets_n_error_min": True} for domain in identity["source_domains"]}})
        for name, payload in (("competence.json", competence), ("applicability.json", applicability)):
            path = directory / name
            path.write_text(
                json.dumps(payload),
                encoding="utf-8",
            )
            artifacts[f"results/source-dry-run/{name}"] = self._digest(path)
        policy_path = root / "configs" / "source_recipe_v2.yaml"
        evidence_path = directory / "evidence.json"
        evidence_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "no_target_selection_input": True,
                    "artifact_sha256": artifacts,
                    "source_policy_path": "configs/source_recipe_v2.yaml",
                    "source_policy_sha256": self._digest(policy_path),
                }
            ),
            encoding="utf-8",
        )
        return evidence_path

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
