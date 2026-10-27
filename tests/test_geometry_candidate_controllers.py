"""Model-free controller checks for the separately versioned source study."""

import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import build_geometry_candidate304 as builder
import close_geometry_candidate304 as closure
import run_geometry_candidate304 as base
import run_geometry_candidate304_v2 as revised


class CandidateControllersTest(unittest.TestCase):
    def test_controller_entry_points_import_with_required_helpers(self):
        self.assertTrue(callable(base.normalize_rgb))
        self.assertTrue(callable(base.dino_pool))
        self.assertTrue(callable(base.quality_vector))
        self.assertNotEqual(base.OUTPUT, revised.OUTPUT)
        self.assertNotEqual(base.CONFIG, revised.CONFIG)

    def test_no_owner_confirmation_stops_before_reading_private_inputs(self):
        with patch.object(builder, "read_json", side_effect=AssertionError("unexpected input access")):
            with self.assertRaisesRegex(ValueError, "confirm-source-only"):
                builder.build(confirm_source_only=False, limit=None)
        with patch.object(revised, "read_json", side_effect=AssertionError("unexpected input access")):
            with self.assertRaisesRegex(ValueError, "confirm-source-only"):
                revised.execute(confirm_source_only=False)

    def test_revised_controller_restores_base_paths_after_error(self):
        original_config, original_output = base.CONFIG, base.OUTPUT

        def fail(**kwargs):
            base.CONFIG = revised.CONFIG
            base.OUTPUT = revised.OUTPUT
            raise RuntimeError("synthetic execution failure")

        with patch.object(revised, "_execute", side_effect=fail):
            with self.assertRaisesRegex(RuntimeError, "synthetic execution failure"):
                revised.execute(confirm_source_only=True)
        self.assertEqual(base.CONFIG, original_config)
        self.assertEqual(base.OUTPUT, original_output)

    def test_comparison_preserves_all_contexts_and_signed_deltas(self):
        baseline = []
        for index in range(12):
            baseline.append({
                "key": f"context-{index}", "outer_target": f"excluded-{index // 3}",
                "seed": index % 3, "source_domains": ["a", "b", "c"], "denominators": {"source_use": 100},
                "systems": {name: {"macro_auroc": 0.8, "pass": True} for name in closure.SYSTEMS},
            })
        revised_results = copy.deepcopy(baseline)
        for row in revised_results:
            row["systems"]["dino_reg"]["macro_auroc"] = 0.81
            row["systems"]["openclip"] = {"macro_auroc": 0.5, "pass": False}
        result = closure.compare_results(baseline, list(reversed(revised_results)))
        summary = result["descriptive_mean_over_overlapping_contexts"]
        self.assertEqual(len(result["context_comparisons"]), 12)
        self.assertAlmostEqual(summary["dino_reg"]["mean_delta"], 0.01)
        self.assertAlmostEqual(summary["openclip"]["mean_delta"], -0.3)
        self.assertEqual(summary["openclip"]["positive_contexts"], 0)
        self.assertEqual(summary["openclip"]["candidate_competence_pass_contexts"], 0)
        self.assertFalse(result["independent_replicates"])
        self.assertIsNone(result["geometry_effect_confidence_interval"])

        for invalid in (revised_results[:-1], revised_results + [revised_results[0]]):
            with self.assertRaises(ValueError):
                closure.compare_results(baseline, invalid)
        revised_results[0]["denominators"] = {"source_use": 99}
        with self.assertRaisesRegex(ValueError, "population drift"):
            closure.compare_results(baseline, revised_results)


if __name__ == "__main__":
    unittest.main()
