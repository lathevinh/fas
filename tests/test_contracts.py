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
            self._ledger_row("heterogeneous", detector_status="failure"),
            self._ledger_row("same_family", detector_status="failure"),
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
            {**self._ledger_row("heterogeneous", detector_status="failure"), "pad_score": 0.2},
            self._ledger_row("same_family", detector_status="success"),
        ]
        errors = validate_transaction_ledger(rows)
        self.assertTrue(any("null scores" in error for error in errors))
        self.assertTrue(any("bit-identical" in error for error in errors))

    def test_ledger_rejects_missing_cluster_and_lineage_fields(self) -> None:
        left = self._ledger_row("heterogeneous")
        right = self._ledger_row("same_family")
        del left["subject_id"]
        del right["policy_artifact_hash"]
        errors = validate_transaction_ledger([left, right])
        self.assertTrue(any("subject_id" in error for error in errors))
        self.assertTrue(any("policy_artifact_hash" in error for error in errors))

    def test_ledger_rejects_paired_cluster_or_fold_mismatch(self) -> None:
        left = self._ledger_row("heterogeneous")
        right = self._ledger_row("same_family")
        right["video_id"] = "v2"
        right["outer_target"] = "CASIA-FASD"
        errors = validate_transaction_ledger([left, right])
        self.assertTrue(any("paired identity" in error for error in errors))

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

    @staticmethod
    def _ledger_row(system: str, detector_status: str = "success") -> dict[str, object]:
        failed = detector_status == "failure"
        return {
            "transaction_id": "t1",
            "sample_id": "OULU-NPU/r1/s1/v1/middle/10",
            "dataset": "OULU-NPU",
            "subject_id": "s1",
            "video_id": "v1",
            "outer_target": "OULU-NPU",
            "system": system,
            "ground_truth": "attack",
            "detector_status": detector_status,
            "pad_score": None if failed else 0.8,
            "pad_threshold": None if failed else 0.5,
            "pad_decision": None if failed else "bona_fide",
            "risk_score": None if failed else 0.2,
            "gate_threshold": None if failed else 0.4,
            "gate_action": None if failed else "accept",
            "final_k1_action": "non_accept" if failed else "accept",
            "classifier_artifact_hash": "a" * 64,
            "risk_artifact_hash": "b" * 64,
            "policy_artifact_hash": "c" * 64,
        }


if __name__ == "__main__":
    unittest.main()
