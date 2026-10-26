import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from fas.source_diagnostics import budget_split, cluster_weights, competence, design, paired_ap, weighted_ranking
from fas.source_experiment import fit_context, predict, risk_run
from fas.source_fitting import identity, partitions
from fas.freeze import build_analysis_freeze_record, write_immutable_record
from fas.preregistration import _validate_analysis_freeze, artifact_hashes
from fas.feature_cache import digest
from test_source_fitting import synthetic_rows
import run_source299 as run
import close_source299 as closure


class Source299Contracts(unittest.TestCase):
    def test_whole_group_budget_controls_preserve_roles_and_identical_oof_universe(self):
        rows = synthetic_rows()
        indexed = {identity(row): row for row in rows}
        primary = partitions(rows, "OULU-NPU", 20260917)[1:]
        cap = min(len(split["fitting"]) for split in primary)
        for split in primary:
            sensitivity = budget_split(split, indexed, cap, 20260917)
            self.assertLessEqual(len(sensitivity["fitting"]), cap)
            self.assertEqual(sensitivity["evaluation"], split["evaluation"])
            self.assertEqual(sensitivity["validation"], split["validation"])
            self.assertEqual(sensitivity["calibration"], split["calibration"])
            self.assertTrue(set(sensitivity["fitting"]).issubset(split["fitting"]))
            self.assertEqual(sensitivity, budget_split(split, indexed, cap, 20260917))

    def test_tie_stable_weighted_ap_and_auroc_exact_values(self):
        y, scores = np.array([1, 0, 1, 0]), np.array([0.9, 0.8, 0.7, 0.6])
        self.assertAlmostEqual(weighted_ranking(y, scores, np.ones(4), "auroc"), 0.75)
        self.assertAlmostEqual(weighted_ranking(y, scores, np.ones(4), "ap"), 5 / 6)
        self.assertEqual(weighted_ranking(y, np.ones(4), np.ones(4), "auroc"), 0.5)
        self.assertEqual(weighted_ranking(y, np.ones(4), np.ones(4), "ap"), 0.5)
        self.assertIsNone(weighted_ranking(np.zeros(4), scores, np.ones(4), "ap"))
        weighted = weighted_ranking(y, scores, np.array([2, 1, 3, 2]), "ap")
        expanded = weighted_ranking(np.repeat(y, [2, 1, 3, 2]), np.repeat(scores, [2, 1, 3, 2]), np.ones(8), "ap")
        self.assertEqual(weighted, expanded)

    def records(self):
        return [{"id": str(index), "dataset": f"domain{index // 40}", "group_id": str(index // 2),
                 "label": index % 2, "errors": {name: int(index % 7 == 0) for name in
                                               ("dino_reg", "openclip", "heterogeneous", "same_family")},
                 "scores": {name: (0.1 if index % 2 == 0 else 0.9) for name in
                            ("dino_reg", "openclip", "heterogeneous", "same_family")}}
                for index in range(120)]

    def test_clusters_share_weights_and_competence_uses_real_uncertainty(self):
        rows = self.records()
        weights = cluster_weights(rows, np.random.default_rng(7))
        np.testing.assert_array_equal(weights[::2], weights[1::2])
        result = competence(rows, 25, 7, lambda: None, finite_calibration=True)
        self.assertEqual(result["heterogeneous"]["macro_auroc_lcb"], 1)
        self.assertEqual(result["heterogeneous"]["bootstrap_valid_repetitions"], 25)
        failed = competence(rows, 25, 7, lambda: None, finite_calibration=False)
        self.assertFalse(failed["heterogeneous"]["pass"])

    def test_paired_identical_scores_have_zero_interval_and_one_class_is_explicit(self):
        rows = self.records()
        risk = np.arange(len(rows), dtype=np.float64)
        result = paired_ap(rows, risk, risk, "heterogeneous", 50, 7, lambda: None)
        self.assertEqual(result["delta"], 0)
        self.assertEqual(result["ci95"], [0, 0])
        for row in rows:
            row["errors"]["heterogeneous"] = 0
        result = paired_ap(rows, risk, risk, "heterogeneous", 50, 7, lambda: None)
        self.assertFalse(result["estimable"])
        self.assertIsNone(result["ci95"])

    def test_no_quality_removes_only_registered_quality_dimensions(self):
        row = {"probabilities": {"dino_reg": 0.2, "openclip": 0.8},
               "thresholds": {"heterogeneous": 0.6}, "quality": [1, 2, 3, 4, 5]}
        values = design([row], "heterogeneous", "R_DVd_noq", np.zeros(5), np.ones(5))
        np.testing.assert_allclose(values, [[0.2, 0.8, 0.6]])
        margin = design([row], "heterogeneous", "R_DVdm", np.zeros(5), np.ones(5))
        np.testing.assert_allclose(margin[0, :4], [0.2, 0.8, 0.6, -0.1])

    def test_authority_and_original_clock_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(run, "OUTPUT", Path(temporary)):
            with self.assertRaises(FileNotFoundError):
                run.authority()
        with patch.object(run.time, "time", return_value=11):
            with self.assertRaises(TimeoutError):
                run.enforce({"deadline_unix_seconds": 10, "work_deadline_unix_seconds": 9})

    def test_saved_output_closure_rejects_invented_errors_or_scores(self):
        record = {"id": "synthetic", "dataset": "CASIA-FASD", "group_id": "synthetic",
                  "role": "train", "label": 1, "errors": {"heterogeneous": 0},
                  "thresholds": {"heterogeneous": 0.5}, "scores": {"heterogeneous": 0.7},
                  "probabilities": {"dino_reg": 0.8, "openclip": 0.6}, "quality": [1, 2, 3, 4, 5],
                  "fit_sha256": "synthetic"}
        closure.check_predictions([record], [record])
        for changed in ({"errors": {"heterogeneous": 1}}, {"probabilities": {"dino_reg": 0.2, "openclip": 0.6}},
                        {"fit_sha256": "different"}):
            with self.assertRaises(ValueError):
                closure.check_predictions([record], [{**record, **changed}])

    def test_saved_head_closure_checks_checkpoint_selection_and_actual_loss(self):
        rows = [{"binary_label": label, "dataset": "CASIA-FASD"} for label in ("bona_fide", "attack")]
        head = {"coefficients": [0.0, 0.0], "validation_history": [1.0] * 199 + [float(np.log(2))],
                "selected_epoch": 200, "validation_bce": float(np.log(2))}
        fitted = {"split": {"validation": ["a", "b"]}, "heads": {"dino_reg": head}}
        arguments = (rows, {"dino_reg": np.zeros((2, 1))}, {"a": 0, "b": 1})
        closure.check_heads(fitted, *arguments)
        head["validation_bce"] = 0.1
        with self.assertRaises(ValueError):
            closure.check_heads(fitted, *arguments)
        head["validation_bce"] = float(np.log(2))
        head["validation_history"][0] = float(np.log(2))
        with self.assertRaises(ValueError):
            closure.check_heads(fitted, *arguments)


@unittest.skipUnless(importlib.util.find_spec("scipy"), "numerical fitting runtime not installed in model-free CI")
class Source299Numerical(unittest.TestCase):
    def test_complete_synthetic_combination_exercises_all_controls_and_evidence(self):
        rows = synthetic_rows()
        rng = np.random.default_rng(19)
        features = {name: rng.normal(size=(len(rows), 4)).astype(np.float32)
                    for name in ("dino_reg", "dino_plain", "openclip")}
        quality = rng.normal(size=(len(rows), 5))
        text = rng.normal(size=(8, 4)).astype(np.float32)
        splits = partitions(rows, "OULU-NPU", 7)
        cap = min(len(split["fitting"]) for split in splits[1:])
        indexed = {identity(row): row for row in rows}
        context = {"key": "synthetic-combination", "outer_target": "OULU-NPU", "seed": 7,
                   "row_ids": [identity(row) for row in rows], "partitions": splits,
                   "budget_partitions": [budget_split(split, indexed, cap, 7) for split in splits[1:]],
                   "budget_cap": cap, "reuse297": False, "original_counts": {"fixture": True}}
        config = json.loads(run.CONFIG.read_text())
        config["bootstrap"]["repetitions"] = 10
        inherited = json.loads(run.old.CONFIG.read_text())
        inherited["head"]["epochs"] = 5
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "inputs.json").write_text('{"source_use_binding":{"fixture":true}}')
            (root / "extraction.json").write_text("{}")
            with (patch.object(run, "OUTPUT", root), patch.object(run, "enforce"), patch("builtins.print")):
                result = run.combination(context, rows, features, quality, text, config, inherited, {})
            self.assertEqual(result["oof_candidate_count"], 360)
            self.assertEqual(result["g_domain_count"], 180)
            self.assertEqual(len(result["risk_fits"]), 40)
            self.assertEqual(len(result["paired_source_diagnostics"]), 8)
            self.assertEqual(len(result["paired_no_quality_attribution"]), 8)
            self.assertEqual(len(result["audits"]), 4)
            self.assertTrue(result["no_target_predictions"])

    def test_context_fit_and_risk_are_actual_and_unchanged_state_is_reused(self):
        rows = synthetic_rows()
        rng = np.random.default_rng(7)
        features = {name: rng.normal(size=(len(rows), 4)).astype(np.float32) for name in ("dino_reg", "dino_plain")}
        clip = rng.normal(size=len(rows)).astype(np.float32)
        q = rng.normal(size=(len(rows), 5))
        split = partitions(rows, "OULU-NPU", 7)[0]
        config = {"seed": 7, "outer_target": "OULU-NPU",
                  "head": {"epochs": 5, "learning_rate": 0.001, "weight_decay": 0.05}}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fitted, meta = fit_context(rows, features, clip, split, config, root / "fits", {"fixture": True}, lambda: None)
            ids = [identity(row) for row in rows]
            records = predict(rows, features, clip, q, ids, fitted, meta["sha256"])
            nongate = [record for record in records if record["role"] != "g_domain"]
            gate = [record for record in records if record["role"] == "g_domain"]
            risk = risk_run(nongate, gate, "heterogeneous", "R_DVd_noq", np.zeros(5), np.ones(5),
                            root / "risks", {"fixture": True}, lambda: None)
            self.assertEqual(risk["status"], "fitted")
            self.assertEqual(len(risk["predictions"]), len(gate))
            with patch("fas.source_experiment.fit_head", side_effect=AssertionError("unexpected retrain")):
                restored, _ = fit_context(rows, features, clip, split, config, root / "fits", {"fixture": True}, lambda: None)
                self.assertEqual(restored, fitted)
            with patch("fas.source_experiment.fit_risk", side_effect=AssertionError("unexpected refit")):
                self.assertEqual(risk, risk_run(nongate, gate, "heterogeneous", "R_DVd_noq",
                                               np.zeros(5), np.ones(5), root / "risks", {"fixture": True}, lambda: None))
            with self.assertRaises(ValueError):
                fit_context(rows, features, clip, split, {**config, "outer_target": "CASIA-FASD"},
                            root / "forbidden", {"fixture": True}, lambda: None)


class PersistedFreezeTests(unittest.TestCase):
    def test_published_freeze_survives_commit_but_rejects_changed_pinned_artifact(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for folder in ("configs", "results/source-dry-run", "scripts"):
                (root / folder).mkdir(parents=True)
            (root / "configs/experiment_core_v1.yaml").write_text(json.dumps({
                "outer_domains": ["OULU-NPU", "CASIA-FASD", "MSU-MFSD", "SiW-Mv2"]}))
            (root / "configs/seeds_v1.yaml").write_text('{"seeds":[20260917,20260923,20261001]}')
            (root / "configs/source_recipe_v2.yaml").write_text("{}")
            evidence = {"source_policy_sha256": digest(root / "configs/source_recipe_v2.yaml"),
                        "no_target_selection_input": True}
            (root / "results/source-dry-run/evidence.json").write_text(json.dumps(evidence))
            for name in ("competence.json", "applicability.json"):
                (root / "results/source-dry-run" / name).write_text("{}")

            def git(*args):
                return subprocess.check_output(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                                                "-c", "commit.gpgsign=false", *args], cwd=root,
                                               stderr=subprocess.DEVNULL, text=True).strip()

            def commit():
                git("add", ".")
                git("commit", "-qm", "Fixture\n\nCo-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>")

            git("init", "-q")
            commit()
            record = build_analysis_freeze_record(
                created_at_utc="2026-10-26T00:00:00+00:00", created_from_commit=git("rev-parse", "HEAD"),
                artifact_sha256=artifact_hashes(root),
                source_evidence_sha256=digest(root / "results/source-dry-run/evidence.json"),
                source_policy_sha256=evidence["source_policy_sha256"],
                outer_targets=["OULU-NPU", "CASIA-FASD", "MSU-MFSD", "SiW-Mv2"],
                seeds=[20260917, 20260923, 20261001], no_target_selection_input=True)
            write_immutable_record(root / "results/analysis-freeze/freeze_record.json", record)
            errors = []
            _validate_analysis_freeze(root, errors)
            self.assertEqual(errors, [])
            commit()
            errors = []
            _validate_analysis_freeze(root, errors)
            self.assertEqual(errors, [])
            (root / "scripts/new_evaluator.py").write_text('"""Synthetic successor artifact."""\n')
            commit()
            errors = []
            _validate_analysis_freeze(root, errors)
            self.assertTrue(errors)
            predecessor_bytes = (root / "results/analysis-freeze/freeze_record.json").read_bytes()
            successor = {**record, "created_from_commit": git("rev-parse", "HEAD"),
                         "artifact_sha256": artifact_hashes(root)}
            successor_path = Path("results/analysis-freeze/freeze_record301-v1.json")
            write_immutable_record(root / successor_path, successor)
            errors = []
            _validate_analysis_freeze(root, errors, successor_path)
            self.assertEqual(errors, [])
            commit()
            errors = []
            _validate_analysis_freeze(root, errors, successor_path)
            self.assertEqual(errors, [])
            self.assertEqual((root / "results/analysis-freeze/freeze_record.json").read_bytes(), predecessor_bytes)
            (root / "configs/source_recipe_v2.yaml").write_text('{"changed":true}')
            commit()
            errors = []
            _validate_analysis_freeze(root, errors, successor_path)
            self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
