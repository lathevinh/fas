from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.contracts import (
    aggregate_seed_then_target,
    class_balanced_aurc,
    competence_allows_claim,
    evaluate_rq1_applicability,
    k1_end_to_end_summary,
    paired_cluster_multiplicities,
    validate_rq1_pair,
    validate_risk_view,
    validate_transaction_ledger,
)


class StatisticalContractTest(unittest.TestCase):
    def test_seed_then_target_aggregation_uses_every_seed(self) -> None:
        deltas = {
            "OULU-NPU": [0.03, 0.00, 0.06],
            "CASIA-FASD": [0.01, 0.02, 0.03],
            "Replay-Attack": [-0.01, 0.02, 0.02],
            "MSU-MFSD": [0.04, 0.04, 0.04],
        }
        target, macro = aggregate_seed_then_target(deltas)
        self.assertAlmostEqual(target["OULU-NPU"], 0.03)
        self.assertAlmostEqual(macro, sum(target.values()) / 4)

    def test_aggregation_rejects_missing_or_nonfinite_seed(self) -> None:
        with self.assertRaises(ValueError):
            aggregate_seed_then_target({"OULU-NPU": [0.1, 0.2]})
        with self.assertRaises(ValueError):
            aggregate_seed_then_target({"OULU-NPU": [0.1, math.nan, 0.2]})

    def test_underpowered_seed_remains_estimable_but_not_event_support(self) -> None:
        state = evaluate_rq1_applicability([25, 8, 21], [True, True, True])
        self.assertTrue(state.target_eligible)
        self.assertEqual(state.supporting_seed_count, 2)
        self.assertEqual(state.status, "eligible")

    def test_one_class_seed_makes_target_inconclusive(self) -> None:
        state = evaluate_rq1_applicability([25, 25, 25], [True, False, True])
        self.assertFalse(state.target_eligible)
        self.assertEqual(state.status, "inconclusive")

    def test_tied_aurc_is_invariant_to_transaction_order(self) -> None:
        first = class_balanced_aurc(
            [(0.1, 1), (0.1, 0), (0.7, 1)],
            [(0.2, 0), (0.2, 1), (0.9, 0)],
        )
        second = class_balanced_aurc(
            [(0.1, 0), (0.1, 1), (0.7, 1)],
            [(0.2, 1), (0.2, 0), (0.9, 0)],
        )
        self.assertAlmostEqual(first, second)

    def test_zero_error_class_has_zero_aurc(self) -> None:
        value = class_balanced_aurc(
            [(0.1, 0), (0.2, 0)],
            [(0.1, 1), (0.2, 0)],
        )
        self.assertAlmostEqual(value, 0.375)

    def test_cluster_resampling_is_paired_and_reproducible(self) -> None:
        first = paired_cluster_multiplicities(["s1", "s1", "s2", "s3"], 5, 17)
        second = paired_cluster_multiplicities(["s3", "s2", "s1", "s1"], 5, 17)
        self.assertEqual(first, second)
        self.assertTrue(all(sum(replicate.values()) == 3 for replicate in first))
        self.assertNotEqual(first, paired_cluster_multiplicities(["s1", "s2", "s3"], 5, 18))


class PairingAndLedgerContractTest(unittest.TestCase):
    def test_rq1_requires_identical_ids_predictions_and_errors(self) -> None:
        domain = [
            {"transaction_id": "t1", "prediction": "live", "error": 0},
            {"transaction_id": "t2", "prediction": "spoof", "error": 1},
        ]
        sample = [dict(row) for row in domain]
        self.assertEqual(validate_rq1_pair(domain, sample), [])
        sample[1]["error"] = 0
        self.assertTrue(validate_rq1_pair(domain, sample))

    def test_detector_failure_stays_in_ledger_with_null_scores(self) -> None:
        rows = [
            {
                "transaction_id": "t1",
                "system": "heterogeneous",
                "label": "attack",
                "detector_status": "failure",
                "classifier_score": None,
                "risk_score": None,
                "final_k1_action": "non_accept",
            },
            {
                "transaction_id": "t1",
                "system": "same_family",
                "label": "attack",
                "detector_status": "failure",
                "classifier_score": None,
                "risk_score": None,
                "final_k1_action": "non_accept",
            },
        ]
        self.assertEqual(validate_transaction_ledger(rows), [])

    def test_k1_summary_uses_original_denominators(self) -> None:
        rows = [
            {"label": "attack", "detector_status": "failure", "final_k1_action": "non_accept"},
            {"label": "attack", "detector_status": "success", "final_k1_action": "accept"},
            {"label": "bona_fide", "detector_status": "failure", "final_k1_action": "non_accept"},
            {"label": "bona_fide", "detector_status": "success", "final_k1_action": "accept"},
        ]
        summary = k1_end_to_end_summary(rows)
        self.assertEqual(summary["attack_total"], 2)
        self.assertEqual(summary["bona_fide_total"], 2)
        self.assertEqual(summary["fa_end2end"], 0.5)
        self.assertEqual(summary["bfnr_end2end"], 0.5)
        self.assertEqual(summary["attack_detector_coverage"], 0.5)
        self.assertEqual(summary["bona_fide_detector_coverage"], 0.5)

    def test_ledger_rejects_score_after_failure_and_mask_mismatch(self) -> None:
        rows = [
            {
                "transaction_id": "t1",
                "system": "heterogeneous",
                "label": "attack",
                "detector_status": "failure",
                "classifier_score": 0.2,
                "risk_score": None,
                "final_k1_action": "non_accept",
            },
            {
                "transaction_id": "t1",
                "system": "same_family",
                "label": "attack",
                "detector_status": "success",
                "classifier_score": 0.2,
                "risk_score": 0.3,
                "final_k1_action": "accept",
            },
        ]
        errors = validate_transaction_ledger(rows)
        self.assertTrue(any("null scores" in error for error in errors))
        self.assertTrue(any("bit-identical" in error for error in errors))

    def test_risk_view_rejects_detector_failures(self) -> None:
        rows = [
            {"transaction_id": "t1", "detector_status": "success", "risk_score": 0.2},
            {"transaction_id": "t2", "detector_status": "failure", "risk_score": None},
        ]
        self.assertTrue(any("detector-successful" in error for error in validate_risk_view(rows)))

    def test_standalone_branch_failure_does_not_kill_core_claim(self) -> None:
        competence = {
            "heterogeneous_complete_competence": True,
            "same_family_complete_competence": True,
            "dino_anchor_nondegeneracy": True,
            "openclip_standalone_competence": False,
        }
        self.assertTrue(competence_allows_claim("rq1_oof_transfer", competence))
        self.assertTrue(competence_allows_claim("rq2_complete_system", competence))
        self.assertFalse(competence_allows_claim("openclip_standalone", competence))


if __name__ == "__main__":
    unittest.main()