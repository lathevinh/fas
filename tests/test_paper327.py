from fractions import Fraction
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
HAS_TORCH = importlib.util.find_spec("torch") is not None


class ExpansionGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("paper327_gate", ROOT/"scripts/paper327/gate.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        cls.gate = module

    def cases(self):
        count = self.gate.OperatingCounts
        return {target: (count(100, 100, 5, 45), count(100, 100, 5, 50))
                for target in self.gate.TARGETS}

    def test_exact_operating_boundaries_and_no_execution_authority(self):
        result = self.gate.assess_expansion(self.cases())
        self.assertEqual(result["decision"], "eligible_for_owner_review")
        self.assertEqual(result["reference_joint_targets"], 0)
        self.assertEqual(result["candidate_joint_targets"], 4)
        self.assertFalse(result["scientific_execution_authorized"])
        count = self.gate.OperatingCounts
        self.assertTrue(count(20, 2, 1, 1).joint)
        self.assertFalse(count(19, 2, 1, 1).safe)

    def test_cross_target_gain_security_regression_and_joint_requirements(self):
        count = self.gate.OperatingCounts
        for pair, reason in (
                ((count(100, 100, 5, 45), count(100, 100, 6, 70)), "new_FA_unsafe_targets"),
                ((count(100, 100, 5, 80), count(100, 100, 5, 74)), "BFA_regression_exceeds_5pp")):
            cases = self.cases()
            cases["OULU-NPU"] = pair
            result = self.gate.assess_expansion(cases)
            self.assertEqual(result["decision"], "stop")
            self.assertIn(reason, result["reasons"])
        cases = {target: (count(100, 100, 5, 10), count(100, 100, 5, 15))
                 for target in self.gate.TARGETS}
        self.assertIn("joint_utility_target_count_gain_below_one",
                      self.gate.assess_expansion(cases)["reasons"])
        cases = self.cases()
        for target in self.gate.TARGETS[1:]:
            cases[target] = (count(100, 100, 5, 45), count(100, 100, 5, 49))
        self.assertIn("fewer_than_two_operationally_improved_targets",
                      self.gate.assess_expansion(cases)["reasons"])
        cases = self.cases()
        cases["OULU-NPU"] = (count(100, 100, 5, 80), count(100, 100, 5, 75))
        self.assertEqual(self.gate.assess_expansion(cases)["decision"], "eligible_for_owner_review")

    def test_review328_unsafe_acceptances_are_not_a_usability_baseline(self):
        count = self.gate.OperatingCounts
        rows = [(40, 90, 5, 60), (0, 40, 0, 60), (20, 90, 5, 65), (10, 80, 5, 60)]
        cases = {target: (count(100, 100, a, b), count(100, 100, c, d))
                 for target, (a, b, c, d) in zip(self.gate.TARGETS, rows)}
        result = self.gate.assess_expansion(cases)
        self.assertEqual(result["decision"], "eligible_for_owner_review")
        self.assertEqual(result["candidate_joint_targets"], 4)
        self.assertEqual(len(result["improved_targets"]), 4)
        self.assertEqual(result["regression_targets"], [])

    def test_missing_policy_is_not_zero_or_a_success(self):
        cases = self.cases()
        cases["OULU-NPU"] = (None, cases["OULU-NPU"][1])
        result = self.gate.assess_expansion(cases)
        self.assertEqual(result["decision"], "stop")
        self.assertEqual(result["reasons"], ["missing_primary_policy:OULU-NPU:reference"])
        self.assertNotIn("reference_joint_targets", result)

    def test_malformed_counts_inventory_or_pairing_raise(self):
        count = self.gate.OperatingCounts
        for values in ((0, 100, 0, 1), (100, 100, 101, 1), (True, 100, 0, 1),
                       (100, 100, 0, -1), (100., 100, 0, 1)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                count(*values)
        with self.assertRaises(ValueError):
            self.gate.assess_expansion({})
        cases = self.cases()
        cases["OULU-NPU"] = (count(100, 100, 5, 45), count(100, 99, 5, 50))
        with self.assertRaises(ValueError):
            self.gate.assess_expansion(cases)
        cases["OULU-NPU"] = [None, None]
        with self.assertRaises(ValueError):
            self.gate.assess_expansion(cases)

    def test_specification_matches_gate_and_stays_blocked(self):
        spec = json.loads((ROOT/"docs/paper327/specification.json").read_text())
        self.assertFalse(spec["scientific_execution_authorized"])
        self.assertTrue(spec["remaining_execution_blockers"])
        self.assertEqual(spec["inventory"]["targets"], list(self.gate.TARGETS))
        self.assertEqual(spec["inventory"]["initial_training_starts"], 8)
        self.assertEqual(spec["inventory"]["additional_training_starts"], 16)
        self.assertEqual(Fraction(spec["evaluation"]["primary_FA"]), self.gate.ALPHA)
        self.assertEqual(Fraction(spec["evaluation"]["primary_BFA"]), self.gate.MINIMUM_BFA)
        self.assertEqual(spec["expansion_gate"]["maximum_BFA_regression_both_FA_safe_pp"]/100,
                         float(self.gate.MAXIMUM_REGRESSION))
        self.assertEqual(self.gate.PRACTICAL_GAIN, Fraction(1, 20))
        self.assertFalse(spec["reference"]["BCE_only_substitution_allowed"])
        self.assertEqual(spec["tail_objective"]["fraction"], "1/20")
        self.assertEqual(spec["tail_objective"]["weight"], .1)

    def test_synthetic_receipt_is_bound_to_code_and_not_scientific_evidence(self):
        receipt = json.loads((ROOT/"results/phase1/dino327-synthetic-probe-v1.json").read_text())
        for name, digest in receipt["code_sha256"].items():
            path = ROOT/"scripts/paper327"/name
            self.assertEqual(hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest(), digest)
        for key in ("scientific_training_starts", "dataset_image_reads", "target_evaluations",
                    "saved_trained_checkpoints"):
            self.assertEqual(receipt[key], 0)
        self.assertFalse(receipt["scientific_execution_authorized"])
        self.assertEqual(receipt["synthetic_optimizer_steps"], 10)
        self.assertEqual(len(receipt["results"]), 2)
        for result in receipt["results"]:
            self.assertTrue(result["finite_full_backbone_gradient_observed"])
            self.assertEqual(len(result["step_seconds"]), 3)
            self.assertTrue(all(math.isfinite(value) and value > 0
                                for value in result["step_seconds"]))
            self.assertLessEqual(result["cuda_peak_reserved"], receipt["caps"]["own_cuda_bytes"])


@unittest.skipUnless(HAS_TORCH, "synthetic objective checks require the existing fas torch environment")
class ObjectiveTests(unittest.TestCase):
    def test_tail_values_gradients_orientation_and_fail_closed_inputs(self):
        if os.environ.get("PAPER327_TEST_CHILD") != "1":
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "test_paper327.ObjectiveTests", "-v"],
                cwd=ROOT/"tests", env={**os.environ, "PAPER327_TEST_CHILD": "1"},
                capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            return
        import torch
        sys.path.insert(0, str(ROOT/"scripts/paper327"))
        from objective import attack_tail_ranking, upper_tail_mean
        torch.set_num_threads(2)
        values = torch.tensor([1., 2., 3.], dtype=torch.float64, requires_grad=True)
        value = upper_tail_mean(values, Fraction(1, 2))
        self.assertAlmostEqual(value.item(), 8/3)
        value.backward()
        torch.testing.assert_close(values.grad, torch.tensor([0., 1/3, 2/3], dtype=torch.float64))
        self.assertEqual(upper_tail_mean(values, Fraction(1, 20)).item(), 3.)
        self.assertEqual(upper_tail_mean(values, Fraction(1)).item(), 2.)
        logits = torch.tensor([-2., 3., 0., -1., 4., .2, -.5, 5., .1],
                              dtype=torch.float64, requires_grad=True)
        attacks = torch.tensor([1, 1, 0]*3)
        domains = torch.tensor([0]*3+[1]*3+[2]*3)
        actual = attack_tail_ranking(logits, attacks, domains)
        expected = sum(
            sum(math.log1p(math.exp(1+b-a)) for b in (0., .2, .1))/3
            for a in (-2., -1., -.5))/3
        self.assertAlmostEqual(actual.item(), expected)
        actual.backward()
        self.assertTrue((logits.grad[[0, 3, 6]] < 0).all())
        self.assertTrue((logits.grad[[1, 4, 7]] == 0).all())
        self.assertTrue((logits.grad[[2, 5, 8]] > 0).all())
        self.assertAlmostEqual(logits.grad.sum().item(), 0.)
        order = torch.tensor([8, 2, 4, 1, 6, 0, 3, 7, 5])
        torch.testing.assert_close(actual, attack_tail_ranking(logits[order], attacks[order], domains[order]))
        torch.testing.assert_close(actual, attack_tail_ranking(logits+100, attacks, domains))
        torch.testing.assert_close(actual, attack_tail_ranking(
            logits.repeat_interleave(2), attacks.repeat_interleave(2), domains.repeat_interleave(2)))
        self.assertTrue(torch.autograd.gradcheck(
            lambda x: attack_tail_ranking(x, attacks, domains), (logits.detach().requires_grad_(),)))
        for invalid in (Fraction(0), Fraction(2), .05):
            with self.subTest(fraction=invalid), self.assertRaises(ValueError):
                upper_tail_mean(values, invalid)
        for invalid in (torch.tensor([]), torch.tensor([float("nan")]), torch.tensor([1, 2])):
            with self.assertRaises(ValueError):
                upper_tail_mean(invalid, Fraction(1, 20))
        for a, d, margin in (
                (attacks[:-1], domains, 1.),
                (torch.ones_like(attacks), domains, 1.),
                (attacks, torch.zeros_like(domains), 1.),
                (attacks, -domains, 1.),
                (attacks+1, domains, 1.),
                (attacks, domains, float("nan")),
                (attacks, domains, -1.)):
            with self.subTest(margin=margin), self.assertRaises(ValueError):
                attack_tail_ranking(logits, a, d, margin=margin)


if __name__ == "__main__":
    unittest.main()
