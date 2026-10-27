"""Synthetic checks for the exploratory geometry-preserving input candidate."""

import sys
import unittest
import builtins
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.geometry_candidate import fit_source_risk_candidate, pad_shared_crop


class PadSharedCropTest(unittest.TestCase):
    def test_padding_is_centered_and_metadata_is_exact(self):
        image = np.full((2, 4, 3), (10, 30, 90), dtype=np.uint8)
        actual, geometry = pad_shared_crop(image, 4)

        self.assertEqual(actual.shape, (4, 4, 3))
        np.testing.assert_array_equal(actual[0], np.zeros((4, 3), dtype=np.uint8))
        np.testing.assert_array_equal(actual[1:3], image)
        np.testing.assert_array_equal(actual[3], np.zeros((4, 3), dtype=np.uint8))
        self.assertEqual(geometry["padding_top_bottom_left_right"], [1, 1, 0, 0])
        self.assertEqual(geometry["input_height_width"], [2, 4])
        self.assertEqual(geometry["square_height_width"], [4, 4])

    def test_portrait_odd_padding_puts_remainder_on_right(self):
        image = np.full((5, 2, 3), 90, dtype=np.uint8)
        actual, geometry = pad_shared_crop(image, 5)
        self.assertEqual(geometry["padding_top_bottom_left_right"], [0, 0, 1, 2])
        np.testing.assert_array_equal(actual[:, 1:3], image)
        np.testing.assert_array_equal(actual[:, :1], 0)
        np.testing.assert_array_equal(actual[:, 3:], 0)
        np.testing.assert_array_equal(image, 90)

    def test_square_crop_keeps_the_baseline_resize(self):
        image = np.random.default_rng(304).integers(0, 256, (80, 80, 3), dtype=np.uint8)
        for resolution in (224, 518):
            candidate, geometry = pad_shared_crop(image, resolution)
            baseline = cv2.resize(image, (resolution, resolution), interpolation=cv2.INTER_CUBIC)
            np.testing.assert_array_equal(candidate, baseline)
            self.assertEqual(geometry["padding_top_bottom_left_right"], [0, 0, 0, 0])

    def test_isotropic_resize_preserves_shape_aspect_ratio(self):
        image = np.zeros((100, 200, 3), dtype=np.uint8)
        cv2.rectangle(image, (80, 30), (119, 69), (255, 255, 255), thickness=-1)

        actual, geometry = pad_shared_crop(image, 200)
        mask = actual[:, :, 0] > 127
        ys, xs = np.where(mask)

        self.assertEqual(actual.shape, (200, 200, 3))
        self.assertEqual(geometry["padding_top_bottom_left_right"], [50, 50, 0, 0])
        self.assertAlmostEqual((xs.max() - xs.min() + 1) / (ys.max() - ys.min() + 1), 1.0, delta=0.08)

    def test_invalid_images_and_resolutions_fail_closed(self):
        for image in (
            np.zeros((0, 2, 3), dtype=np.uint8),
            np.zeros((2, 2), dtype=np.uint8),
            np.zeros((2, 2, 3), dtype=np.float32),
        ):
            with self.assertRaises(ValueError):
                pad_shared_crop(image, 8)
        for resolution in (0, -1, 2.5, True):
            with self.assertRaises(ValueError):
                pad_shared_crop(np.zeros((2, 2, 3), dtype=np.uint8), resolution)

    def test_candidate_risk_optimizer_uses_declared_line_search_and_converges(self):
        rng = np.random.default_rng(304)
        features = rng.normal(size=(120, 4))
        domains = ["a"] * 40 + ["b"] * 40 + ["c"] * 40
        errors = (features[:, 0] + 0.25 * features[:, 1] > 0).astype(np.int64)
        guard_calls = []
        model = fit_source_risk_candidate(features, errors, domains, lambda: guard_calls.append(True))

        self.assertTrue(model["optimizer_success"])
        self.assertEqual(model["line_search_maximum"], 50)
        self.assertEqual(model["error_count"], int(errors.sum()))
        self.assertGreater(len(guard_calls), 0)

    def test_candidate_risk_optimizer_failure_is_not_accepted(self):
        features = np.array([[0.1], [0.9]])
        errors = np.array([0, 1])
        with patch("scipy.optimize.minimize") as minimize:
            minimize.return_value.success = False
            minimize.return_value.message = "ABNORMAL"
            with self.assertRaisesRegex(RuntimeError, "ABNORMAL"):
                fit_source_risk_candidate(features, errors, ["a", "a"], lambda: None)
            self.assertEqual(minimize.call_args.kwargs["options"]["maxls"], 50)

    def test_candidate_risk_invalid_inputs_fail_closed(self):
        for errors in (np.array([0, 0]), np.array([0]), np.array([[0], [1]])):
            with self.assertRaises(ValueError):
                fit_source_risk_candidate(np.array([[0.1], [0.9]]), errors, ["a", "a"], lambda: None)

    def test_invalid_risk_inputs_do_not_require_scipy(self):
        original_import = builtins.__import__

        def without_scipy(name, *args, **kwargs):
            if name.startswith("scipy"):
                raise ModuleNotFoundError("scipy is not installed")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=without_scipy):
            with self.assertRaisesRegex(ValueError, "finite risk features"):
                fit_source_risk_candidate(np.array([[0.1], [0.9]]), np.array([0, 0]),
                                          ["a", "a"], lambda: None)


if __name__ == "__main__":
    unittest.main()
