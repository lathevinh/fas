import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from fas.contracts import CORE_DOMAINS, PRIMARY_SEEDS, class_balanced_aurc
from fas.locked_metrics import (
    aggregate, arrays, cell_metrics, decide, evaluate, operating_summary, raw_aurc, select_k1, transaction_ledger,
)
from fas.source_fitting import identity
import run_locked301 as run


def fixture(target="OULU-NPU", count=240):
    originals, predictions = [], []
    for i in range(count):
        label, error = i % 2, int(i // 2 % 7 == 0)
        score = 0.9 if bool(label) != bool(error) else 0.1
        original = {"dataset": target, "video_id": str(i), "group_id": f"{target}/g{i // 2}",
                    "subject_id": None if target == "SiW-Mv2" else str(i // 2),
                    "binary_label": "attack" if label else "bona_fide", "detector_status": "success",
                    "role": "g_domain", "source_use_eligible": True}
        originals.append(original)
        predictions.append({"id": identity(original), "dataset": target, "group_id": original["group_id"], "label": label,
                            "scores": {name: score for name in ("heterogeneous", "same_family", "dino_reg", "openclip")},
                            "thresholds": {name: 0.5 for name in ("heterogeneous", "same_family", "dino_reg", "openclip")},
                            "errors": {name: error for name in ("heterogeneous", "same_family", "dino_reg", "openclip")}})
    errors = np.asarray([row["errors"]["heterogeneous"] for row in predictions], dtype=float)
    risks = {f"{strategy}/{system}/R_DVd": (errors if strategy == "domain_oof" else 1 - errors).copy()
             for strategy in ("domain_oof", "matched_sample_oof") for system in ("heterogeneous", "same_family")}
    policies = {name: {"threshold": 1.0} for name in risks}
    return originals, predictions, risks, policies


class Locked301Tests(unittest.TestCase):
    def test_raw_aurc_matches_registered_tie_expectation_and_integer_bootstrap(self):
        errors, risk, weights = np.array([1, 0, 1, 0]), np.array([0.3, 0.3, 0.7, 0.1]), np.array([2, 3, 1, 4])
        expanded = list(zip(np.repeat(risk, weights).tolist(), np.repeat(errors, weights).tolist()))
        expected = class_balanced_aurc(expanded, expanded)
        self.assertAlmostEqual(raw_aurc(errors, risk, weights), expected)
        self.assertEqual(raw_aurc(errors, np.zeros(4), np.ones(4)), 0.5)
        self.assertIsNone(raw_aurc(errors, risk, np.zeros(4)))
        with self.assertRaises(ValueError):
            raw_aurc(errors, risk, np.full(4, 0.5))

    def test_original_failures_remain_nonaccept_without_fabricated_scores(self):
        originals, predictions, risks, policies = fixture(count=8)
        for i, status in ((0, "not_run"), (1, "failed")):
            originals[i]["detector_status"] = status
        predictions = predictions[2:]
        summary = operating_summary(originals, predictions, np.ones(6), "heterogeneous", 1)
        self.assertEqual(summary["attack_originals"], 4)
        self.assertEqual(summary["bona_fide_originals"], 4)
        self.assertEqual(summary["attack_failures"], 1)
        self.assertEqual(summary["bona_fide_failures"], 1)
        self.assertEqual(summary["attack_detector_coverage"], 0.75)
        none = operating_summary(originals, predictions, np.ones(6), "heterogeneous", -1)
        self.assertEqual(none["fa_end2end"], 0)
        self.assertEqual(none["bfnr_end2end"], 1)
        with self.assertRaises(ValueError):
            operating_summary(originals, predictions[:-1], np.ones(5), "heterogeneous", 1)

    def test_source_gate_excludes_entire_outer_target_and_is_deterministic(self):
        originals, predictions, scores = [], [], []
        for target in CORE_DOMAINS - {"OULU-NPU"}:
            a, b, _, _ = fixture(target, 80)
            originals.extend(a)
            predictions.extend(b)
            scores.extend(row["errors"]["heterogeneous"] for row in b)
        policy = select_k1(originals, predictions, np.asarray(scores), "heterogeneous", "OULU-NPU")
        self.assertEqual(policy["source_macro_fa"], 0)
        self.assertEqual(policy["threshold"], 0)
        self.assertEqual(policy, select_k1(originals, predictions, np.asarray(scores), "heterogeneous", "OULU-NPU"))
        originals[0]["dataset"] = "OULU-NPU"
        with self.assertRaises(ValueError):
            select_k1(originals, predictions, np.asarray(scores), "heterogeneous", "OULU-NPU")

    def test_spoof_decisions_are_not_abstained_by_a_live_only_gate(self):
        originals, predictions, _, _ = fixture(count=8)
        for row in predictions:
            row["scores"]["heterogeneous"] = 0.9
        result = operating_summary(originals, predictions, np.ones(8), "heterogeneous", -1)
        self.assertEqual(result["coverage"], 1)
        self.assertEqual(result["fa_end2end"], 0)
        self.assertEqual(result["bfnr_end2end"], 1)

    def test_typed_ledger_retains_pre_detector_failure_and_never_gates_spoof(self):
        originals, predictions, risks, policies = fixture(count=8)
        originals[0]["detector_status"] = "not_run"
        predictions = predictions[1:]
        risks = {name: value[1:] for name, value in risks.items()}
        ledgers = transaction_ledger(originals, predictions, risks, policies, "a" * 64,
                                     dict.fromkeys(risks, "b" * 64), "c" * 64)
        for rows in ledgers.values():
            self.assertEqual(len(rows), 16)
            failed = [row for row in rows if row["detector_status"] == "not_run"]
            self.assertEqual(len(failed), 2)
            self.assertTrue(all(row["pad_score"] is None and row["classifier_error"] is None for row in failed))
            self.assertTrue(all(row["gate_action"] is None for row in rows if row["pad_decision"] == "attack"))

    def test_shared_masks_wrong_errors_and_risk_shapes_fail_closed(self):
        args = fixture()
        cell = arrays(*args)
        expected = cell_metrics(cell)
        self.assertGreater(expected["rq1_delta"], 0)
        self.assertEqual(expected["rq2_delta"], 0)
        broken = copy.deepcopy(args)
        broken[1][0]["errors"]["heterogeneous"] ^= 1
        with self.assertRaises(ValueError):
            arrays(*broken)
        broken = copy.deepcopy(args)
        broken[2]["domain_oof/heterogeneous/R_DVd"] = np.ones(2)
        with self.assertRaises(ValueError):
            arrays(*broken)

    def test_bootstrap_is_paired_across_seeds_and_underpowered_seed_is_not_dropped(self):
        cells = {target: {seed: arrays(*fixture(target)) for seed in PRIMARY_SEEDS} for target in CORE_DOMAINS}
        result = evaluate(cells, {"rq1": True, "rq2": True}, 30, 7, lambda: None)
        self.assertEqual(result["bootstrap_valid"]["rq1"]["macro"], 30)
        self.assertEqual(result["ci95"]["rq2"]["macro"], [0, 0])
        self.assertEqual(result["claims"]["rq1"]["status"], "pass")
        self.assertNotEqual(result["claims"]["rq2"]["status"], "pass")
        for seed_value in result["rq1"]["seed_macros"].values():
            self.assertEqual(seed_value, result["rq1"]["macro"])
        points = {target: {seed: {"delta": value} for seed, value in zip(PRIMARY_SEEDS, [1.0, 0.0, -0.4], strict=True)}
                  for target in CORE_DOMAINS}
        self.assertAlmostEqual(aggregate(points, "delta")["macro"], 0.2)

    def test_one_class_ap_is_undefined_and_forces_four_target_inconclusive(self):
        cells = {target: {seed: arrays(*fixture(target, 40)) for seed in PRIMARY_SEEDS} for target in CORE_DOMAINS}
        args = fixture("OULU-NPU", 40)
        for row in args[1]:
            row["errors"] = {name: 0 for name in row["errors"]}
            row["scores"] = {name: (0.9 if row["label"] else 0.1) for name in row["scores"]}
        cells["OULU-NPU"][PRIMARY_SEEDS[0]] = arrays(*args)
        result = evaluate(cells, {"rq1": True, "rq2": True}, 10, 2, lambda: None)
        self.assertIsNone(result["rq1"]["macro"])
        self.assertIsNone(result["rq1"]["targets"]["OULU-NPU"])
        self.assertEqual(result["claims"]["rq1"]["status"], "inconclusive")
        self.assertFalse(result["event_eligible_targets"]["OULU-NPU"])
        del cells["OULU-NPU"][PRIMARY_SEEDS[0]]
        with self.assertRaises(ValueError):
            evaluate(cells, {"rq1": True, "rq2": True}, 10, 2, lambda: None)

    def test_claims_preserve_harmful_negative_inconclusive_and_inapplicable_states(self):
        values = {"macro": 0.03, "targets": dict.fromkeys(CORE_DOMAINS, 0.03),
                  "seed_macros": dict.fromkeys(map(str, PRIMARY_SEEDS), 0.03)}
        rq2 = {**values, "operational_harms": {name: {"macro": 0.0, "targets": dict.fromkeys(CORE_DOMAINS, 0.0)}
                                              for name in ("fa_end2end", "bfnr_end2end")}}
        intervals = {"rq1": {"macro": [0.01, 0.05]}, "rq2": {"macro": [0.01, 0.05]}}
        support, dependencies = dict.fromkeys(CORE_DOMAINS, True), {"rq1": True, "rq2": True}
        self.assertEqual(decide(values, rq2, intervals, support, dependencies)["rq2"]["status"], "pass")
        harmful = copy.deepcopy(rq2)
        harmful["operational_harms"]["bfnr_end2end"]["targets"]["OULU-NPU"] = 0.021
        self.assertEqual(decide(values, harmful, intervals, support, dependencies)["rq2"]["status"], "evidence_against")
        negative = {"rq1": {"macro": [-0.1, -0.01]}, "rq2": intervals["rq2"]}
        self.assertEqual(decide(values, rq2, negative, support, dependencies)["rq1"]["status"], "evidence_against")
        self.assertEqual(decide(values, rq2, intervals, dict.fromkeys(CORE_DOMAINS, False), dependencies)["rq1"]["status"], "inconclusive")
        self.assertEqual(decide(values, rq2, intervals, support, {"rq1": False, "rq2": False})["rq1"]["status"], "not_applicable")

    def test_original_deadline_and_typed_authority_reject_implicit_execution(self):
        with self.assertRaises(ValueError):
            run.authorize("prepare_only")
        with patch.object(run.time, "time", return_value=101):
            with self.assertRaises(TimeoutError):
                run.guard({"started_unix_seconds": 1, "limits": {"work_seconds": 99, "wall_seconds": 100}})

    def test_supervisor_does_not_dirty_frozen_release_before_saved_only_closure(self):
        with tempfile.TemporaryDirectory() as temporary:
            output, public = Path(temporary) / "private", Path(temporary) / "public"
            output.mkdir()
            (output / "worker_completion.json").write_text('{"complete":true}')
            limits = {"work_seconds": 100, "wall_seconds": 200, "rss_bytes": 1000000, "output_bytes": 1000000}
            approval = {"started_unix_seconds": 1, "limits": limits}
            config = {"limits": limits, "execution_manifest": "manifest.json"}
            child = unittest.mock.Mock(returncode=0)
            child.poll.return_value = 0
            with (patch.object(run, "OUTPUT", output), patch.object(run, "PUBLIC", public),
                  patch.object(run, "authority", return_value=(config, {}, {}, approval)),
                  patch.object(run, "digest", return_value="a" * 64),
                  patch.object(run, "owned_size", return_value=100),
                  patch.object(run.time, "time", return_value=2),
                  patch.object(run.subprocess, "Popen", return_value=child)):
                run.supervise()
            self.assertEqual(json.loads((output / "terminal.json").read_text())["status"], "complete")
            self.assertFalse((public / "run301-v1.json").exists())


if __name__ == "__main__":
    unittest.main()
