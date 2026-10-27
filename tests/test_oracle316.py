import copy
from fractions import Fraction
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/diagnostics"))
import oracle316 as run


def case(domain, real=0.6, attack=0.8):
    return {
        "job": "same-fit", "system": "dino_only", "stage": "two_source_domain_oof",
        "seed": 7, "dataset": domain,
        "oracle": run.oracle(np.array([real, attack]), np.array([0, 1]), 1, 1),
    }


class OracleThresholdTests(unittest.TestCase):
    def test_exact_five_percent_original_attack_budget(self):
        labels = np.r_[np.ones(20, dtype=int), np.zeros(2, dtype=int)]
        scores = np.r_[np.arange(20) / 20, [0.01, 0.02]]
        result = run.oracle(scores, labels, 20, 2)
        self.assertEqual(result["attack_error_budget"], 1)
        self.assertEqual(result["oracle_threshold_not_deployable"], 0.05)
        self.assertEqual(result["oracle_FA"], 0.05)
        self.assertEqual(result["oracle_max_BFA"], 1)
        self.assertEqual(run.oracle(scores, labels, 39, 2)["attack_error_budget"], 1)
        self.assertEqual(run.oracle(scores, labels, 40, 2)["attack_error_budget"], 2)

    def test_tied_attack_scores_are_never_partially_accepted(self):
        result = run.oracle(np.array([0.2, 0.2, 0.1]), np.array([1, 1, 0]), 20, 1)
        self.assertEqual(result["attack_error_budget"], 1)
        self.assertEqual(result["oracle_accepted_attack"], 0)
        self.assertEqual(result["oracle_threshold_not_deployable"], 0.2)
        run.curve_check(result, np.array([0.2, 0.2, 0.1]), np.array([1, 1, 0]))

    def test_tied_bona_fide_lower_bound_is_strict(self):
        result = run.oracle(np.array([0.5, 0.5]), np.array([0, 1]), 1, 1)
        self.assertFalse(result["empirically_attainable"])
        self.assertEqual(result["threshold_interval"]["lower_exclusive"], 0.5)
        self.assertEqual(result["threshold_interval"]["upper_inclusive"], 0.5)
        self.assertEqual(result["oracle_max_BFA"], 0)

    def test_technical_failures_remain_nonacceptance_without_invented_scores(self):
        result = run.oracle(np.r_[np.zeros(4), 1.0], np.array([0, 0, 0, 0, 1]), 20, 10)
        self.assertEqual(result["oracle_max_BFA"], 0.4)
        self.assertEqual(result["required_bona_fide_acceptances"], 5)
        self.assertFalse(result["empirically_attainable"])
        self.assertEqual(result["reason"], "technical_failure_BFA_ceiling")
        self.assertIsNone(result["threshold_interval"]["lower_exclusive"])
        run.curve_check(result, np.r_[np.zeros(4), 1.0], np.array([0, 0, 0, 0, 1]))

    def test_zero_successful_scores_and_saturated_probabilities_are_supported(self):
        for scores, labels in ((np.array([]), np.array([], dtype=int)),
                               (np.array([0.0, 1.0]), np.array([0, 1]))):
            result = run.oracle(scores, labels, 20, 1)
            run.curve_check(result, scores, labels)
            self.assertEqual(result["oracle_threshold_not_deployable"], np.nextafter(1.0, 2.0))
        empty = run.oracle(np.array([]), np.array([], dtype=int), 20, 1)
        self.assertFalse(empty["empirically_attainable"])
        self.assertEqual(empty["oracle_max_BFA"], 0)

    def test_odd_original_bona_fide_count_requires_ceiling_half(self):
        result = run.oracle(np.array([0.1, 0.2, 0.8]), np.array([0, 0, 1]), 1, 3)
        self.assertEqual(result["required_bona_fide_acceptances"], 2)
        self.assertTrue(result["empirically_attainable"])

    def test_safe_original_threshold_cannot_exceed_oracle_and_unsafe_bfa_is_not_a_gain(self):
        scores, labels = np.array([0.8, 0.9, 0.1]), np.array([0, 0, 1])
        result = run.oracle(scores, labels, 1, 2)
        original = run.original_rates(scores, labels, 1.0, result)
        self.assertFalse(original["FA_within_constraint"])
        self.assertEqual(result["oracle_max_BFA"] - original["original_BFA"], -1)
        with self.assertRaises(ValueError):
            run.original_rates(scores, labels, float("nan"), result)

    def test_order_statistics_match_exhaustive_search_and_independent_grouped_curve(self):
        rng = np.random.default_rng(42)
        for _ in range(150):
            n = int(rng.integers(0, 35))
            scores = rng.choice([0, 0.1, 0.2, 0.5, 0.9, 1.0], n)
            labels = rng.integers(0, 2, n)
            original_attack = max(1, int((labels == 1).sum()) + int(rng.integers(0, 8)))
            original_real = max(1, int((labels == 0).sum()) + int(rng.integers(0, 8)))
            alpha = rng.choice([0, 1, 5])
            result = run.oracle(scores, labels, original_attack, original_real,
                                alpha=Fraction(int(alpha), 10))
            thresholds = np.unique(np.r_[0.0, scores, np.nextafter(1.0, 2.0)])
            permitted = [float(t) for t in thresholds
                         if np.sum((scores < t) & (labels == 1)) <= result["attack_error_budget"]]
            expected = max(permitted)
            self.assertEqual(result["oracle_threshold_not_deployable"], expected)
            self.assertEqual(result["oracle_accepted_bona_fide"],
                             int(np.sum((scores < expected) & (labels == 0))))
            run.curve_check(result, scores, labels)

    def test_invalid_inputs_fail_explicitly(self):
        invalid = (
            (np.array([np.nan]), np.array([0]), 1, 1),
            (np.array([1.1]), np.array([0]), 1, 1),
            (np.ones((1, 1)), np.array([0]), 1, 1),
            (np.array([0.1]), np.array([2]), 1, 1),
            (np.array([0.1]), np.array([0]), 0, 1),
            (np.array([0.1]), np.array([0]), True, 1),
            (np.array([0.1, 0.2]), np.array([0, 0]), 1, 1),
        )
        for args in invalid:
            with self.assertRaises(ValueError):
                run.oracle(*args)
        with self.assertRaises(ValueError):
            run.oracle(np.array([0.1]), np.array([0]), 1, 1, alpha=0.05)


class CommonOracleTests(unittest.TestCase):
    def test_common_interval_exists_only_with_strict_lower_and_closed_upper(self):
        first, second = case("A", real=0.6, attack=0.8), case("B", real=0.7, attack=0.9)
        result = run.common_interval([first, second])
        self.assertEqual(result["status"], "common_oracle_interval_exists")
        self.assertEqual(result["lower_exclusive"], 0.7)
        self.assertEqual(result["upper_inclusive"], 0.8)
        second = case("B", real=0.8, attack=0.9)
        result = run.common_interval([first, second])
        self.assertEqual(result["status"], "individual_oracles_exist_but_no_common_threshold")

    def test_individual_unattainability_is_distinct_from_threshold_incompatibility(self):
        result = run.common_interval([case("A"), case("B", real=0.9, attack=0.8)])
        self.assertEqual(result["status"], "some_source_individually_unattainable")

    def test_never_intersect_different_fitted_models_or_duplicate_sources(self):
        first, second = case("A"), case("B")
        for key in ("job", "system", "stage", "seed"):
            bad = copy.deepcopy(second)
            bad[key] = "different"
            with self.assertRaisesRegex(ValueError, "different fitted"):
                run.common_interval([first, bad])
        with self.assertRaises(ValueError):
            run.common_interval([first, first])

    def test_public_export_is_aggregate_only_and_does_not_export_oracle_thresholds(self):
        sample = case("A")
        result = {"cases": [sample], "common_thresholds": [run.common_interval([sample])]}
        exported = run.public_result(result)
        self.assertNotIn("oracle_threshold_not_deployable", exported["cases"][0]["oracle"])
        self.assertNotIn("threshold_interval", exported["cases"][0]["oracle"])
        self.assertNotIn("upper_inclusive", exported["common_thresholds"][0])
        self.assertTrue(exported["oracle_threshold_values_not_exported"])
        self.assertIn("oracle_threshold_not_deployable", sample["oracle"])


class SavedOracleTests(unittest.TestCase):
    def test_absent_selected_reference_is_not_manufactured_for_one_source_models(self):
        prediction = {"p": {name: [0.2, 0.8] for name in ("dino_reg", "dino_plain", "openclip")},
                      "selected_two_dino": None}
        systems = run.score_systems(prediction)
        self.assertEqual(len(systems), 5)
        self.assertNotIn("selected_two_dino", systems)

    def build(self, root):
        rows = []
        for domain in ("C", "D"):
            for i, label in enumerate(("bona_fide", "bona_fide", "attack", "attack")):
                rows.append({
                    "dataset": domain, "video_id": str(i), "group_id": str(i), "binary_label": label,
                    "role": "train", "source_use_eligible": True,
                    "model_input_eligible": not ((domain == "C" and i == 1) or (domain == "D" and i == 3)),
                })
        tasks = {d: {"dataset": d, "pool": "domain_oof", "job": "job"} for d in ("C", "D")}
        plan = {"originals": 8, "usable": 6, "jobs": {"job": {"domains": ["A", "B"], "seed": 7}},
                "predictions": tasks}
        base = root / "source_fusion313_v1"
        run.write_immutable_record(base / "execution_plan.json", plan)
        run.write_immutable_record(root / "source_integration295_v1/source_manifest.json", {"rows": rows})
        policies = {name: {"threshold": 0.5} for name in (
            "dino_only", "two_dino:1", "dino_clip:1", "two_dino:0.5", "dino_clip:0.5", "selected_two_dino")}
        run.write_immutable_record(base / "fits/job.json", {"fitted": {"policies": policies}})
        for domain in ("C", "D"):
            selected = [row for row in rows if row["dataset"] == domain and row["model_input_eligible"]]
            p = [0.2 if row["binary_label"] == "bona_fide" else 0.8 for row in selected]
            run.write_immutable_record(base / f"predictions/{domain}.json", {
                "ids": [run.identity(row) for row in selected],
                "p": {name: p for name in ("dino_reg", "dino_plain", "openclip")}, "selected_two_dino": p})
        return {
            "study": "synthetic_oracle", "expected_cases": 12, "expected_prediction_tasks": 2,
            "input_sha256": {str(p): run.digest(p) for p in root.rglob("*.json")},
        }

    def test_end_to_end_and_independent_check_never_load_features_fit_or_predict(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            binding = self.build(root)
            forbidden = AssertionError("saved-score analysis must not fit, load features or predict")
            with (patch.object(run, "PRIVATE", root),
                  patch.object(run.frozen, "fit_head", side_effect=forbidden),
                  patch.object(run.frozen, "fit_calibrator", side_effect=forbidden),
                  patch.object(run.frozen, "load_inputs", side_effect=forbidden),
                  patch.object(run.frozen, "predict", side_effect=forbidden)):
                first = run.analyze(binding, independent_check=False, guard=lambda: None)
                second = run.analyze(binding, independent_check=True, guard=lambda: None)
            self.assertEqual(first, second)
            self.assertEqual(first["case_count"], 12)
            self.assertEqual(len(first["common_thresholds"]), 6)
            self.assertFalse(first["deployable"])
            self.assertEqual(first["new_fits"], 0)
            self.assertEqual(first["summary"]["two_source_domain_oof"]["dino_only"]["oracle_attainable_cases"], 2)

    def test_saved_hash_drift_is_an_error_not_an_empty_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            binding = self.build(root)
            binding["input_sha256"][next(iter(binding["input_sha256"]))] = "0" * 64
            with patch.object(run, "PRIVATE", root):
                with self.assertRaisesRegex(ValueError, "hash drift"):
                    run.analyze(binding, independent_check=False, guard=lambda: None)

    def test_missing_case_denominators_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            binding = self.build(root)
            binding["expected_cases"] = 13
            with patch.object(run, "PRIVATE", root):
                with self.assertRaisesRegex(ValueError, "all declared"):
                    run.analyze(binding, independent_check=False, guard=lambda: None)

    def test_output_budget_is_checked_before_creating_an_immutable_record(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with (patch.object(run, "OUTPUT", root / "owned"), patch.object(run, "PUBLIC", root / "public.json"),
                  patch.object(run, "LIMITS", {"owned_output_bytes": 1}),
                  patch.object(run, "write_immutable_record") as write):
                with self.assertRaises(MemoryError):
                    run.write_checked(root / "owned/file.json", {"too": "large"}, lambda: None)
                write.assert_not_called()

    def test_cli_executes_once_and_saved_verification_can_repeat_without_overwriting(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            binding = self.build(root)
            with (patch.object(run, "PRIVATE", root), patch.object(run, "OUTPUT", root / "oracle"),
                  patch.object(run, "PUBLIC", root / "public.json"),
                  patch.object(run, "source_plan", return_value=binding),
                  patch.object(run, "LIMITS", {**run.LIMITS, "process_peak_rss_bytes": 10**15}),
                  patch("sys.stdout", new_callable=io.StringIO)):
                for mode in ("--execute", "--verify", "--verify"):
                    with patch("sys.argv", ["oracle316.py", mode]):
                        self.assertEqual(run.main(), 0)
                previous = run.digest(root / "oracle/result.json")
                with patch("sys.argv", ["oracle316.py", "--execute"]):
                    with self.assertRaises(FileExistsError):
                        run.main()
                self.assertEqual(previous, run.digest(root / "oracle/result.json"))


if __name__ == "__main__":
    unittest.main()
