from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fas.calibration import MonotoneAffineCalibrator, equal_domain_log_loss


class MonotoneAffineCalibratorTest(unittest.TestCase):
    def test_slope_is_strictly_positive_and_order_is_preserved(self) -> None:
        calibrator = MonotoneAffineCalibrator(theta=-100.0, intercept=0.0)
        values = calibrator.transform([-2.0, 0.0, 2.0])
        self.assertGreater(calibrator.slope, 0.0)
        self.assertLess(values[0], values[1])
        self.assertLess(values[1], values[2])

    def test_extreme_logits_produce_finite_probabilities(self) -> None:
        calibrator = MonotoneAffineCalibrator(theta=2.0, intercept=-0.5)
        for probability in calibrator.transform([-1e6, 0.0, 1e6]):
            self.assertTrue(math.isfinite(probability))
            self.assertGreaterEqual(probability, 0.0)
            self.assertLessEqual(probability, 1.0)

    def test_equal_domain_loss_does_not_weight_by_domain_size(self) -> None:
        probabilities = [0.9, 0.9, 0.9, 0.1]
        labels = [1, 1, 1, 1]
        domains = ["large", "large", "large", "small"]
        expected = (-math.log(0.9) - math.log(0.1)) / 2
        self.assertAlmostEqual(equal_domain_log_loss(probabilities, labels, domains), expected)

    def test_rejects_nonfinite_input(self) -> None:
        calibrator = MonotoneAffineCalibrator(theta=0.0, intercept=0.0)
        with self.assertRaises(ValueError):
            calibrator.transform_one(float("nan"))


if __name__ == "__main__":
    unittest.main()
