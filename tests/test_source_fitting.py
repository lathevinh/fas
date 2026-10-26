import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fas.feature_cache import cache_key, load_shard, save_shard
from fas.source_fitting import (
    calibrate, fit_calibrator, fit_head, fit_risk, group_assignments, head_logits,
    identity, objective_weights, operating_threshold, partitions, quality_vector, risk_features,
)
import run_source297 as run


def synthetic_rows():
    rows = []
    for domain in ("CASIA-FASD", "MSU-MFSD", "SiW-Mv2"):
        for role in ("train", "branch_calibration", "g_domain"):
            for label in ("attack", "bona_fide"):
                for index in range(30):
                    name = f"{role}-{label}-{index}"
                    rows.append({
                        "dataset": domain, "video_id": name, "group_id": name, "group_unit": "video",
                        "binary_label": label, "role": role, "source_use_eligible": True,
                        "source_use_binding": {"policy_id": "synthetic"}, "model_input_eligible": True,
                        "selected_frame": {"rgb_sha256": f"{domain}-{name}"},
                    })
    return rows


class SourcePartitionTests(unittest.TestCase):
    def test_all_domain_exclusions_and_same_candidate_universe(self):
        rows = synthetic_rows()
        splits = partitions(rows, "OULU-NPU", 20260917)
        indexed = {identity(row): row for row in rows}
        self.assertEqual(len(splits), 7)
        candidates = {identity(row) for row in rows if row["role"] != "g_domain"}
        universes = {"domain_oof": [], "matched_sample_oof": []}
        for split in splits:
            used = split["fitting"] + split["validation"] + split["calibration"]
            self.assertFalse(set(used) & set(split["evaluation"]))
            self.assertTrue(all(indexed[value]["role"] == "train" for value in split["fitting"] + split["validation"]))
            self.assertTrue(all(indexed[value]["role"] == "branch_calibration" for value in split["calibration"]))
            if split["name"].startswith("domain_oof:"):
                excluded = split["name"].split(":", 1)[1]
                self.assertTrue(all(indexed[value]["dataset"] != excluded for value in used))
            if split["name"] != "final":
                universes[split["name"].split(":", 1)[0]].extend(split["evaluation"])
        for values in universes.values():
            self.assertEqual(set(values), candidates)
            self.assertEqual(len(values), len(candidates))
        self.assertEqual(splits, partitions(rows, "OULU-NPU", 20260917))

    def test_groups_and_exact_frame_duplicates_stay_together(self):
        rows = synthetic_rows()[:30]
        rows[1]["group_id"] = rows[0]["group_id"]
        rows[2]["selected_frame"] = copy.deepcopy(rows[1]["selected_frame"])
        assignment = group_assignments(rows, 7, 3)
        self.assertEqual(assignment[identity(rows[0])], assignment[identity(rows[1])])
        self.assertEqual(assignment[identity(rows[1])], assignment[identity(rows[2])])
        self.assertEqual(assignment, group_assignments(list(reversed(rows)), 7, 3))

    def test_gate_wrong_roles_target_and_one_class_are_rejected(self):
        rows = synthetic_rows()
        rows[0]["source_use_eligible"] = False
        with self.assertRaises(ValueError):
            partitions(rows, "OULU-NPU", 7)
        with self.assertRaises(ValueError):
            partitions(synthetic_rows(), "CASIA-FASD", 7)
        rows = [row for row in synthetic_rows() if row["binary_label"] == "attack"]
        with self.assertRaises(ValueError):
            partitions(rows, "OULU-NPU", 7)

    def test_objective_weights_preserve_natural_risk_prevalence(self):
        y = np.array([0, 0, 0, 1, 0, 1])
        domains = ["A"] * 4 + ["B"] * 2
        risk = objective_weights(y, domains, balanced=False)
        balanced = objective_weights(y, domains, balanced=True)
        self.assertAlmostEqual(risk[:4].sum(), 0.5)
        self.assertAlmostEqual(risk[-2:].sum(), 0.5)
        self.assertAlmostEqual(risk[:3].sum() / risk[3], 3)
        self.assertAlmostEqual(balanced[:3].sum(), balanced[3])

    def test_operating_threshold_ties_and_worst_domain_constraint(self):
        rows = [{"dataset": domain, "binary_label": "attack"} for domain in ("A", "A", "B", "B")]
        policy = operating_threshold(np.array([0.2, 0.8, 0.4, 0.9]), rows, alpha=0)
        self.assertEqual(policy["threshold"], 0.2)
        self.assertEqual(policy["source_apcer"], {"A": 0, "B": 0})
        policy = operating_threshold(np.array([0.2, 0.2, 0.4, 0.9]), rows, alpha=0.5)
        self.assertEqual(policy["threshold"], 0.2)
        with self.assertRaises(ValueError):
            operating_threshold(np.array([np.nan]), rows[:1])

    def test_risk_variants_keep_probabilities_unstandardized_and_signed_margin(self):
        p, q = np.array([[0.2, 0.8]]), np.arange(5)[None, :]
        expected = {"R_q": 5, "R_D": 6, "R_V": 6, "R_DV": 7, "R_DVd": 8, "R_DVdm": 9}
        for variant, dimension in expected.items():
            self.assertEqual(risk_features(p, q, 0.6, variant).shape, (1, dimension))
        values = risk_features(p, q, 0.6, "R_DVdm")
        np.testing.assert_allclose(values[0, :4], [0.2, 0.8, 0.6, -0.1])

    def test_quality_uses_native_crop_and_hash_bound_geometry_without_detector(self):
        rgb = np.full((224, 224, 3), 128, dtype=np.uint8)
        txn = {"face_box_xyxy": [0, 0, 10, 20], "selected_frame": {"width": 100, "height": 200},
               "detector_confidence": 0.9}
        q = quality_vector(rgb, txn)
        np.testing.assert_allclose(q, [0, 128 / 255, 0, 0.01, 0.9], atol=1e-12)
        with self.assertRaises(ValueError):
            quality_vector(rgb[:100], txn)


class FeatureCacheTests(unittest.TestCase):
    def test_atomic_shard_exact_readback_and_non_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "features.npz"
            value = np.arange(12, dtype=np.float32).reshape(3, 4)
            save_shard(path, ["a", "b", "c"], value)
            np.testing.assert_array_equal(load_shard(path, ["a", "b", "c"], 4), value)
            with self.assertRaises(FileExistsError):
                save_shard(path, ["a", "b", "c"], value)
            with self.assertRaises(ValueError):
                load_shard(path, ["b", "a", "c"], 4)
            self.assertEqual([p.name for p in path.parent.iterdir()], ["features.npz"])

    def test_runtime_transform_contract_is_in_key_not_labels(self):
        contract = {"precision": "float32", "normalization": [0.5], "code": "a"}
        key = cache_key("base", contract)
        for field, value in (("precision", "float16"), ("normalization", [0.4]), ("code", "b")):
            self.assertNotEqual(key, cache_key("base", {**contract, field: value}))

    def test_failure_before_commit_preserves_successful_shards_and_removes_temp(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "features.npz"
            with patch("fas.feature_cache.os.link", side_effect=OSError("fixture interrupted")):
                with self.assertRaises(OSError):
                    save_shard(path, ["a"], np.ones((1, 4), dtype=np.float32))
            self.assertFalse(path.exists())
            self.assertEqual(list(path.parent.iterdir()), [])
            save_shard(path, ["a"], np.ones((1, 4), dtype=np.float32))
            self.assertEqual(load_shard(path, ["a"], 4).shape, (1, 4))

    def test_missing_authority_deadline_storage_and_seal_fail_explicitly(self):
        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(run, "OUTPUT", Path(temporary)):
                with self.assertRaises(FileNotFoundError):
                    run.authority()
                path = Path(temporary) / "record.json"
                run.seal(path, {"x": 1})
                run.seal(path, {"x": 1})
                with self.assertRaises(ValueError):
                    run.seal(path, {"x": 2})
        approval = {"work_deadline_unix_seconds": 5, "deadline_unix_seconds": 10,
                    "limits": {"output_bytes": 100}}
        with patch.object(run.time, "time", return_value=6):
            with self.assertRaises(TimeoutError):
                run.enforce(approval)
        with patch.object(run.time, "time", return_value=1), patch.object(run, "owned_size", return_value=101):
            with self.assertRaises(MemoryError):
                run.enforce(approval)


@unittest.skipUnless(importlib.util.find_spec("scipy"), "fitting runtime scipy is not a model-free CI dependency")
class NumericalFittingTests(unittest.TestCase):
    def test_head_selection_is_earliest_minimum_validation_loss_and_repeatable(self):
        x = np.array([[-2], [-1], [1], [2]], dtype=np.float32)
        y = np.array([0, 0, 1, 1])
        settings = {"epochs": 40, "learning_rate": 0.01, "weight_decay": 0.05}
        args = (x, y, ["A"] * 4, x, y, ["A"] * 4)
        fitted = fit_head(*args, seed=7, settings=settings, guard=lambda: None)
        self.assertEqual(fitted["selected_epoch"], int(np.argmin(fitted["validation_history"])) + 1)
        self.assertEqual(fitted, fit_head(*args, seed=7, settings=settings, guard=lambda: None))
        self.assertTrue(np.all(np.diff(head_logits(fitted, x)) > 0))
        with self.assertRaises(TimeoutError):
            fit_head(*args, seed=7, settings=settings, guard=lambda: (_ for _ in ()).throw(TimeoutError()))

    def test_monotone_calibration_is_fitted_once_and_finite(self):
        logits, y = np.array([-2, 1, -1, 2, 0.3, -0.4]), np.array([0, 0, 1, 1, 1, 0])
        fitted = fit_calibrator(logits, y, ["A"] * 6, lambda: None)
        self.assertGreater(fitted["slope"], 0)
        probabilities = calibrate(fitted, np.sort(logits))
        self.assertTrue(np.all(np.diff(probabilities) > 0))
        self.assertTrue(fitted["optimizer_success"])

    def test_risk_fit_fixed_regularization_no_class_weighting(self):
        x = np.array([[-2], [-1], [0.5], [2], [3]], dtype=np.float64)
        y = np.array([0, 0, 0, 1, 1])
        fit = fit_risk(x, y, ["A", "A", "A", "B", "B"], lambda: None)
        self.assertEqual((fit["error_count"], fit["correct_count"], fit["C"]), (2, 3, 1))
        self.assertGreater(fit["coefficients"][0], 0)
        with self.assertRaises(ValueError):
            fit_risk(x, np.zeros(5), ["A"] * 5, lambda: None)

    def test_actual_controller_oof_joins_gate_isolation_and_completed_fit_resume(self):
        rows = synthetic_rows()
        split = partitions(rows, "OULU-NPU", 20260917)
        rng = np.random.default_rng(7)
        features = {name: rng.normal(size=(len(rows), 4)).astype(np.float32)
                    for name in ("dino_reg", "dino_plain", "openclip")}
        quality = rng.normal(size=(len(rows), 5))
        config = json.loads(run.CONFIG.read_text())
        config["head"] = {**config["head"], "epochs": 6}
        inputs = {"rows": rows, "partitions": split}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "inputs.json").write_text(json.dumps(inputs))
            (root / "extraction.json").write_text("{}")
            (root / "quality.json").write_text("{}")
            text_path = root / "text.npy"
            np.save(text_path, rng.normal(size=(8, 4)).astype(np.float32))
            extracted = {"text": {"path": str(text_path)}}
            with (patch.object(run, "OUTPUT", root), patch.object(run, "enforce"),
                  patch.object(run, "load_features", side_effect=lambda _, name: features[name]),
                  patch("builtins.print")):
                result = run.source_fit(inputs, extracted, quality, config, {})
                self.assertEqual(result["head_fits"], 14)
                self.assertEqual(result["calibrator_fits"], 21)
                self.assertEqual(result["oof_candidate_count_per_strategy"], 360)
                self.assertEqual(result["g_domain_successes"], 180)
                self.assertEqual(result["risk_fits"], 24)
                self.assertFalse(result["scientific_source_dry_run_complete"])
                candidate = {identity(row) for row in rows if row["role"] != "g_domain"}
                for strategy in ("domain_oof", "matched_sample_oof"):
                    predicted = json.loads((root / f"{strategy}-predictions.json").read_text())["rows"]
                    self.assertEqual({row["id"] for row in predicted}, candidate)
                    self.assertEqual(len(predicted), len(candidate))
                with (patch.object(run, "fit_head", side_effect=AssertionError("repeated head fit")),
                      patch.object(run, "fit_risk", side_effect=AssertionError("repeated risk fit")),
                      patch.object(run, "fit_calibrator", side_effect=AssertionError("repeated calibration"))):
                    self.assertEqual(result, run.source_fit(inputs, extracted, quality, config, {}))


if __name__ == "__main__":
    unittest.main()
