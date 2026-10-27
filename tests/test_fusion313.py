import copy
import builtins
from itertools import combinations
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
from fas.feature_cache import digest, payload_digest
from fas.freeze import write_immutable_record
from fas.fusion_study import (
    BRANCHES, FAMILIES, SYSTEMS, check_isolation, components, job_key, make_split,
    operating_metrics, paired_uncertainty, require_support, select_weight, summarize, support,
)
from fas.source_fitting import calibrate, fit_calibrator, fit_head, head_logits, identity, operating_threshold
import run_fusion313 as run
from test_readout308 import fixture


def example_fold(name="example", clip_bf=0.7, control_bf=0.65):
    return {
        "id": name, "dataset": "CASIA-FASD", "systems": {
            system: {"status": "transfer_feasible", "metrics": {
                "original_attack_FA": 0.02,
                "original_bona_fide_acceptance": clip_bf if system == "dino_clip" else control_bf}}
            for system in SYSTEMS}}


class FusionContractTests(unittest.TestCase):
    def setUp(self):
        self.config = run.read(run.CONFIG)

    def test_components_are_transitive_and_exact_frames_are_global(self):
        rows = [
            {"dataset": "A", "video_id": "1", "group_id": "a", "selected_frame": {"rgb_sha256": "x"}},
            {"dataset": "A", "video_id": "2", "group_id": "a", "selected_frame": {"rgb_sha256": "y"}},
            {"dataset": "B", "video_id": "3", "group_id": "b", "selected_frame": {"rgb_sha256": "y"}},
        ]
        self.assertEqual(len(set(components(rows).values())), 1)
        with self.assertRaisesRegex(ValueError, "component crosses"):
            check_isolation([rows[:1], rows[1:]])

    def test_technical_failures_have_no_scores_but_stay_in_original_denominators(self):
        rows = [
            {"dataset": "A", "video_id": str(i), "group_id": str(i), "binary_label": label,
             "model_input_eligible": i < 4}
            for i, label in enumerate(["attack", "attack", "bona_fide", "bona_fide", "attack", "bona_fide"])]
        result = operating_metrics(np.array([0.1, 0.9, 0.1, 0.9]), 0.5, rows[:4], rows, self.config)["A"]
        self.assertEqual(result["original_attack_FA"], 1 / 3)
        self.assertEqual(result["original_bona_fide_acceptance"], 1 / 3)
        self.assertEqual(result["technical_failures"], 2)
        with self.assertRaises(ValueError):
            operating_metrics(np.ones(6), 0.5, rows, rows, self.config)

    def test_threshold_tie_is_attack_and_invalid_scores_fail(self):
        rows = [
            {"dataset": "A", "video_id": str(i), "group_id": str(i), "binary_label": label,
             "model_input_eligible": True}
            for i, label in enumerate(["attack", "bona_fide"])]
        result = operating_metrics(np.array([0.5, 0.5]), 0.5, rows, rows, self.config)["A"]
        self.assertEqual(result["original_attack_FA"], 0)
        self.assertEqual(result["original_bona_fide_acceptance"], 0)
        for scores, threshold in ((np.array([np.nan, 0]), 0.5), (np.array([0, 2]), 0.5),
                                  (np.array([0, 1]), np.inf)):
            with self.assertRaises(ValueError):
                operating_metrics(scores, threshold, rows, rows, self.config)

    def candidates(self, bf=0.6, fa=0.03):
        return [{"weight": weight, "per_domain": {
            domain: {"original_attack_FA": fa, "original_bona_fide_acceptance": bf}
            for domain in ("A", "B")}} for weight in self.config["weights"]]

    def test_selector_uses_worst_source_then_fa_then_lower_added_weight(self):
        candidates = self.candidates()
        self.assertEqual(select_weight(candidates, self.config)["weight"], 0)
        candidates[2]["per_domain"]["A"]["original_bona_fide_acceptance"] = 0.9
        self.assertEqual(select_weight(candidates, self.config)["weight"], 0)
        candidates[3]["per_domain"] = self.candidates(bf=0.7)[0]["per_domain"]
        self.assertEqual(select_weight(candidates, self.config)["weight"], 0.5)
        candidates[4]["per_domain"] = self.candidates(bf=0.7, fa=0.01)[0]["per_domain"]
        self.assertEqual(select_weight(candidates, self.config)["weight"], 0.75)

    def test_no_feasible_grid_returns_no_policy_and_never_relaxes_constraints(self):
        for candidates in (self.candidates(bf=0), self.candidates(fa=0.2)):
            self.assertEqual(select_weight(candidates, self.config),
                             {"status": "no_candidate_meets_declared_utility", "weight": None})
        with self.assertRaises(ValueError):
            select_weight(self.candidates()[:-1], self.config)
        bad = self.candidates()
        bad[0]["per_domain"]["B"]["original_attack_FA"] = float("nan")
        with self.assertRaises(ValueError):
            select_weight(bad, self.config)

    def test_feasibility_first_does_not_reward_insecure_high_acceptance(self):
        fold = example_fold(clip_bf=0.65, control_bf=0.85)
        for name in ("dino_only", "two_dino"):
            fold["systems"][name]["status"] = "transfer_failure"
            fold["systems"][name]["metrics"]["original_attack_FA"] = 0.3
        result = summarize([fold], self.config)
        self.assertEqual(result["decision"], "retain_for_independent_validation")
        self.assertTrue(all(item["status"] == "feasibility_advantage_only"
                            for item in result["clip_comparisons"].values()))
        self.assertTrue(all(item["worst_source_gain"] is None
                            for item in result["clip_comparisons"].values()))

    def test_both_feasible_require_two_absolute_points_and_no_source_mean_worsening(self):
        for gain, expected in ((0.019, "no_demonstrated_incremental_value"),
                               (0.02, "retain_for_independent_validation")):
            result = summarize([example_fold(clip_bf=0.8 + gain, control_bf=0.8)], self.config)
            self.assertEqual(result["decision"], expected)
        first = example_fold("first", clip_bf=0.7, control_bf=0.6)
        second = example_fold("second", clip_bf=0.8, control_bf=0.9)
        second["dataset"] = "MSU-MFSD"
        self.assertEqual(summarize([first, second], self.config)["decision"], "no_demonstrated_incremental_value")

    def test_one_bad_seed_or_missing_policy_is_not_dropped_from_the_denominator(self):
        first, second = example_fold("first"), example_fold("second")
        second["systems"]["dino_clip"] = {
            "status": "no_candidate_meets_declared_utility", "metrics": None}
        result = summarize([first, second], self.config)
        item = result["systems"]["dino_clip"]
        self.assertEqual(item["fold_denominator"], 2)
        self.assertEqual(item["selected_policy_fraction"], 0.5)
        self.assertIsNone(item["worst_source_mean_bona_fide_acceptance"])
        self.assertEqual(result["decision"], "no_demonstrated_incremental_value")
        bad = example_fold()
        bad["systems"]["dino_clip"]["metrics"]["original_attack_FA"] = 0.3
        with self.assertRaisesRegex(ValueError, "contradicts"):
            summarize([bad], self.config)

    def test_support_uses_usable_connected_components_not_error_count(self):
        rows = [
            {"dataset": "A", "video_id": str(i), "group_id": "same",
             "binary_label": "attack" if i % 2 else "bona_fide", "model_input_eligible": True}
            for i in range(40)]
        inventory = support(rows)
        self.assertEqual(inventory["A"]["attack"]["originals"], 20)
        self.assertEqual(inventory["A"]["attack"]["components"], 1)
        with self.assertRaisesRegex(ValueError, "insufficient declared support"):
            require_support(inventory, self.config["support"]["evaluation"], "test")


class FusionPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows, features, _, _, splits, inherited, old = fixture()
        cls.rows, cls.features, cls.inherited = rows, features, inherited
        cls.config = run.read(run.CONFIG)
        cls.config["domains"] = sorted({row["dataset"] for row in rows})
        cls.config["seeds"] = [20260917]
        cls.config["bootstrap_repetitions"] = 24
        cls.jobs, cls.reuse = {}, {}
        index = {identity(row): position for position, row in enumerate(rows)}
        y = np.asarray([row["binary_label"] == "attack" for row in rows], dtype=float)
        for count in (1, 2, 3):
            for domains in combinations(cls.config["domains"], count):
                split = make_split(rows, list(domains), 20260917)
                key = job_key(list(domains), 20260917, split)
                job = {"id": key, "domains": list(domains), "seed": 20260917,
                       "split": split, "reuse": {"synthetic": True} if count > 1 else None}
                cls.jobs[key] = job
                if count == 1:
                    continue
                prior_split = next(item for item in splits if all(
                    item[name] == split[name] for name in split))
                saved = old[prior_split["name"]]
                positions = {name: np.asarray([index[value] for value in ids]) for name, ids in split.items()}
                fit, val, cal = (positions[name] for name in ("fitting", "validation", "calibration"))
                domains_at = lambda selected: [rows[position]["dataset"] for position in selected]
                head = fit_head(features["openclip"][fit], y[fit], domains_at(fit),
                                features["openclip"][val], y[val], domains_at(val), seed=20260917,
                                settings=run.recipe(inherited, "openclip"), guard=lambda: None)
                calibrator = fit_calibrator(head_logits(head, features["openclip"][cal]),
                                            y[cal], domains_at(cal), lambda: None)
                core = {branch: {"model": saved["heads"][branch], "calibrator": saved["calibrators"][branch],
                                 "transform": "raw"} for branch in ("dino_reg", "dino_plain")}
                core["openclip"] = {"model": head, "calibrator": calibrator, "transform": "raw"}
                cls.reuse[key] = {"core": core, "selected_reference": {
                    branch: copy.deepcopy(core[branch]) for branch in ("dino_reg", "dino_plain")}}
        cls.by_sources = {tuple(job["domains"]): key for key, job in cls.jobs.items()}
        cls.plan = {"jobs": cls.jobs, "predictions": {}, "evaluations": [],
                    "counts": {"new_head_fits": 9, "new_calibrator_fits": 9}}

        def prediction(key, domain, pool):
            pkey = payload_digest({"job": key, "dataset": domain, "pool": pool})
            cls.plan["predictions"][pkey] = {
                "id": pkey, "job": key, "dataset": domain, "pool": pool}
            return pkey

        for key, job in cls.jobs.items():
            job["inner_predictions"] = [
                prediction(cls.by_sources[tuple(value for value in job["domains"] if value != domain)],
                           domain, "domain_oof")
                for domain in job["domains"]] if len(job["domains"]) > 1 else []
            if len(job["domains"]) == 1:
                continue
            domains = ([value for value in cls.config["domains"] if value not in job["domains"]]
                       if len(job["domains"]) == 2 else job["domains"])
            pool = "domain_oof" if len(job["domains"]) == 2 else "g_domain"
            for domain in domains:
                cls.plan["evaluations"].append({
                    "id": f"{key}/{domain}", "job": key, "dataset": domain, "pool": pool,
                    "seed": job["seed"], "outer_exclusion": "OULU-NPU",
                    "prediction": prediction(key, domain, pool)})

    def test_single_source_fit_has_group_validation_and_no_other_source_or_g_domain(self):
        for job in self.jobs.values():
            ids = [key for values in job["split"].values() for key in values]
            selected = [row for row in self.rows if identity(row) in ids]
            self.assertEqual({row["dataset"] for row in selected}, set(job["domains"]))
            self.assertNotIn("g_domain", {row["role"] for row in selected})
            self.assertEqual(len(ids), len(set(ids)))

    def test_both_families_share_exact_dino_zero_endpoint_and_threshold(self):
        key = self.by_sources[tuple(self.config["domains"])]
        job = self.jobs[key]
        models = self.reuse[key]
        policies = run.thresholds(models, job, self.rows, self.features, self.config)
        self.assertEqual(run.policy_key("dino_clip", 0), run.policy_key("two_dino", 0))
        self.assertEqual(len(policies), 12)
        self.assertEqual(policies["dino_only"]["score_polarity"], "attack_high_tie_is_attack")
        self.assertTrue(all(0 <= value <= 0.05 for value in policies["dino_only"]["source_apcer"].values()))

    def test_new_head_and_calibrator_budget_is_fail_closed_with_immutable_starts(self):
        job = next(item for item in self.jobs.values() if len(item["domains"]) == 1)
        events = []
        with patch.object(run, "fit_calibrator", side_effect=RuntimeError("solver failure")):
            with self.assertRaisesRegex(RuntimeError, "solver failure"):
                run.fit_job(job, self.rows, self.features, self.inherited, self.config, lambda: None,
                            {"new_head_fits": 0, "new_calibrator_fits": 0}, self.plan["counts"],
                            lambda name, value: events.append(name))
        self.assertEqual(events, ["dino_reg-head-start", "dino_reg-head-complete", "dino_reg-calibrator-start"])
        with patch.object(run, "fit_head") as fit:
            with self.assertRaisesRegex(RuntimeError, "head-fit budget"):
                run.fit_job(job, self.rows, self.features, self.inherited, self.config, lambda: None,
                            {"new_head_fits": 9, "new_calibrator_fits": 0}, self.plan["counts"], lambda *args: None)
            fit.assert_not_called()

    def test_synthetic_end_to_end_and_independent_saved_reconstruction_never_fit(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = {**self.config, "private_root": temporary, "output_name": "study"}
            root = Path(temporary) / "study"
            write_immutable_record(root / "execution_plan.json", self.plan)
            write_immutable_record(root / "attempt_lock.json", {"supervisor_pid": os.getppid()})
            approval = {"started_unix": time.time(), "deadline_unix": time.time() + 120}
            with (
                patch.object(run, "authority", return_value=(config, self.plan, approval)),
                patch.object(run, "load_inputs", return_value=(
                    {"rows": self.rows}, self.rows, self.features, {}, self.inherited)),
                patch.object(run, "build_plan", return_value=self.plan),
                patch.object(run, "reused_models", side_effect=lambda job, inherited: self.reuse[job["id"]]),
            ):
                result = run.run_worker()
                self.assertEqual(result["counts"]["new_head_fits"], 9)
                self.assertEqual(len(result["folds"]), 6)
                self.assertEqual(result["evaluation"]["domain_oof"]["uncertainty"]["valid"], 24)
                self.assertEqual(result["encoder_forwards"], 0)
                with (patch.object(run, "fit_head", side_effect=AssertionError("no refit")),
                      patch.object(run, "fit_calibrator", side_effect=AssertionError("no recalibration"))):
                    self.assertEqual(result, run.run_worker(reconstruct=True))
                self.assertTrue(run.read(root / "saved_reconstruction.json")["all_models_predictions_selection_metrics_and_bootstrap_reconstructed"])

    def test_outer_label_changes_cannot_affect_inner_weights_or_thresholds(self):
        key = next(key for key, job in self.jobs.items() if len(job["domains"]) == 2)
        job = self.jobs[key]
        fitted, predictions = {}, {}
        for child in {self.plan["predictions"][pkey]["job"] for pkey in job["inner_predictions"]}:
            fitted[child] = run.fit_job(
                self.jobs[child], self.rows, self.features, self.inherited, self.config, lambda: None,
                {"new_head_fits": 0, "new_calibrator_fits": 0}, self.plan["counts"], lambda *args: None)
        for pkey in job["inner_predictions"]:
            task = self.plan["predictions"][pkey]
            predictions[pkey] = run.predict(task, self.jobs[task["job"]], fitted[task["job"]],
                                           self.rows, self.rows, self.features)
        expected = run.select(job, self.plan, predictions, fitted, self.rows, self.config)
        changed = copy.deepcopy(self.rows)
        for row in changed:
            if row["dataset"] not in job["domains"] or row["role"] == "g_domain":
                row["binary_label"] = "attack" if row["binary_label"] == "bona_fide" else "bona_fide"
        self.assertEqual(expected, run.select(job, self.plan, predictions, fitted, changed, self.config))

    def test_outer_features_and_g_domain_labels_cannot_affect_any_head_or_threshold(self):
        job = next(item for item in self.jobs.values() if len(item["domains"]) == 1)
        changed_rows, changed_features = copy.deepcopy(self.rows), copy.deepcopy(self.features)
        for position, row in enumerate(changed_rows):
            if row["dataset"] not in job["domains"] or row["role"] == "g_domain":
                row["binary_label"] = "attack" if row["binary_label"] == "bona_fide" else "bona_fide"
                for values in changed_features.values():
                    values[position] = 100
        first = run.fit_job(job, self.rows, self.features, self.inherited, self.config, lambda: None,
                            {"new_head_fits": 0, "new_calibrator_fits": 0}, self.plan["counts"], lambda *args: None)
        second = run.fit_job(job, changed_rows, changed_features, self.inherited, self.config, lambda: None,
                             {"new_head_fits": 0, "new_calibrator_fits": 0}, self.plan["counts"], lambda *args: None)
        self.assertEqual(first, second)

    def test_saved_pipeline_has_no_image_or_encoder_dependencies(self):
        original_import = builtins.__import__

        def guarded(name, *args, **kwargs):
            if name.split(".", 1)[0] in {"torch", "timm", "open_clip", "transformers", "cv2", "PIL"}:
                raise AssertionError(f"forbidden encoder/image dependency: {name}")
            return original_import(name, *args, **kwargs)

        job = next(item for item in self.jobs.values() if len(item["domains"]) == 1)
        with patch("builtins.__import__", side_effect=guarded):
            fitted = run.fit_job(job, self.rows, self.features, self.inherited, self.config, lambda: None,
                                 {"new_head_fits": 0, "new_calibrator_fits": 0}, self.plan["counts"], lambda *args: None)
            self.assertEqual(set(fitted["models"]["core"]), set(BRANCHES))

    def test_infeasible_inner_selection_and_outer_transfer_failure_remain_distinct(self):
        key = self.by_sources[tuple(self.config["domains"])]
        job = self.jobs[key]
        fitted = {"models": self.reuse[key], "policies": run.thresholds(
            self.reuse[key], job, self.rows, self.features, self.config)}
        evaluation = next(item for item in self.plan["evaluations"] if item["job"] == key)
        task = self.plan["predictions"][evaluation["prediction"]]
        prediction = run.predict(task, job, fitted, self.rows, self.rows, self.features)
        selection = {family: {"selection": {"status": "no_candidate_meets_declared_utility", "weight": None}}
                     for family in FAMILIES}
        fold, accepted = run.evaluate(evaluation, fitted, prediction, selection, self.rows, self.config)
        self.assertEqual(fold["systems"]["dino_clip"]["status"], "no_candidate_meets_declared_utility")
        self.assertNotIn("dino_clip", accepted)
        selection["dino_clip"]["selection"] = {"status": "selected", "weight": 0}
        fitted["policies"]["dino_only"] = operating_threshold(
            np.ones(2), [
                {"dataset": "A", "binary_label": "attack"}, {"dataset": "A", "binary_label": "bona_fide"}])
        fitted["policies"]["dino_only"]["threshold"] = 0.0
        fold, accepted = run.evaluate(evaluation, fitted, prediction, selection, self.rows, self.config)
        self.assertEqual(fold["systems"]["dino_clip"]["status"], "transfer_failure")
        self.assertEqual(accepted["dino_clip"], [])

    def test_bootstrap_pairs_original_components_across_duplicate_contexts(self):
        rows = [
            {"dataset": "CASIA-FASD", "video_id": str(i), "group_id": str(i),
             "binary_label": "attack" if i % 2 else "bona_fide", "model_input_eligible": True}
            for i in range(12)]
        one = example_fold("one")
        accepted = {"one": {name: ["CASIA-FASD/0", "CASIA-FASD/2"] for name in SYSTEMS}}
        config = {**self.config, "bootstrap_repetitions": 100}
        first = paired_uncertainty([one], rows, accepted, config, lambda: None)
        second = copy.deepcopy(one)
        second["id"] = "two"
        accepted["two"] = copy.deepcopy(accepted["one"])
        repeated = paired_uncertainty([one, second], rows, accepted, config, lambda: None)
        self.assertEqual(first, repeated)
        self.assertEqual(first["clip_minus"]["two_dino"]["ci95"], [0, 0])


class FusionControllerTests(unittest.TestCase):
    def test_scientific_success_requires_a_separate_reconstruction_under_same_clock(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = run.read(run.CONFIG)
            config.update({"private_root": temporary, "output_name": "study"})
            root = Path(temporary) / "study"
            write_immutable_record(root / "execution_plan.json", {"synthetic": True})
            write_immutable_record(root / "worker_completion.json", {"synthetic": True})
            write_immutable_record(root / "saved_reconstruction.json", {"synthetic": True})
            approval = {"started_unix": time.time() - 1, "deadline_unix": time.time() + 120}
            with (patch.object(run, "authority", return_value=(config, {}, approval)),
                  patch.object(run.subprocess, "Popen") as start):
                start.return_value.poll.return_value = 0
                start.return_value.returncode = 0
                self.assertEqual(run.supervise(), 0)
                self.assertEqual([call.args[0][-1] for call in start.call_args_list], ["--worker", "--reconstruct"])
            terminal = run.read(root / "terminal.json")
            self.assertEqual(terminal["status"], "complete")
            self.assertGreaterEqual(terminal["wall_seconds_from_original_approval"], 1)
            self.assertEqual(terminal["saved_reconstruction_sha256"], digest(root / "saved_reconstruction.json"))

    def test_worker_exit_failure_never_launches_another_fit_or_reconstruction(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = run.read(run.CONFIG)
            config.update({"private_root": temporary, "output_name": "study"})
            root = Path(temporary) / "study"
            write_immutable_record(root / "execution_plan.json", {"synthetic": True})
            approval = {"started_unix": time.time(), "deadline_unix": time.time() + 120}
            with (patch.object(run, "authority", return_value=(config, {}, approval)),
                  patch.object(run.subprocess, "Popen") as start):
                start.return_value.poll.return_value = 1
                start.return_value.returncode = 1
                self.assertEqual(run.supervise(), 1)
                start.assert_called_once()
            self.assertIn("worker exited 1", run.read(root / "terminal.json")["failure"])

    def test_absent_approval_expired_clock_existing_attempt_and_worker_bypass_are_blocked(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = run.read(run.CONFIG)
            config.update({"private_root": temporary, "output_name": "study"})
            path = Path(temporary) / "config.json"
            path.write_text(json.dumps(config))
            root = Path(temporary) / "study"
            plan = {"config_sha256": digest(path), "code_sha256": {}}
            write_immutable_record(root / "execution_plan.json", plan)
            with patch.object(run, "CONFIG", path), patch.object(run, "code_pins", return_value={}):
                with self.assertRaises(FileNotFoundError):
                    run.authority()
            approval = {"started_unix": time.time() - 10, "deadline_unix": time.time() - 1}
            with patch.object(run, "authority", return_value=(config, plan, approval)), patch.object(run.subprocess, "Popen") as start:
                with self.assertRaises(TimeoutError):
                    run.supervise()
                start.assert_not_called()
            approval["deadline_unix"] = time.time() + 120
            write_immutable_record(root / "attempt_lock.json", {"supervisor_pid": -1})
            with patch.object(run, "authority", return_value=(config, plan, approval)), patch.object(run.subprocess, "Popen") as start:
                with self.assertRaises(FileExistsError):
                    run.supervise()
                start.assert_not_called()
                with self.assertRaisesRegex(RuntimeError, "live approving supervisor"):
                    run.run_worker()

    def test_resource_caps_stop_specific_worker_group_without_retry(self):
        for limit in ("combined_sampled_rss_bytes", "owned_output_bytes"):
            with self.subTest(limit=limit), tempfile.TemporaryDirectory() as temporary:
                config = run.read(run.CONFIG)
                config.update({"private_root": temporary, "output_name": "study"})
                config["limits"].update({"combined_sampled_rss_bytes": 10**15, "owned_output_bytes": 10**15})
                config["limits"][limit] = 100000 if limit == "owned_output_bytes" else 1
                root = Path(temporary) / "study"
                write_immutable_record(root / "execution_plan.json", {"synthetic": True})
                approval = {"started_unix": time.time(), "deadline_unix": time.time() + 120}
                with (patch.object(run, "authority", return_value=(config, {}, approval)),
                      patch.object(run.subprocess, "Popen") as start,
                      patch.object(run.os, "killpg") as stop,
                      patch.object(run.prior, "owned_size", side_effect=lambda path: 200000 if start.called else 100),
                      patch.object(run.prior.baseline.pilot, "group_rss", return_value=1024)):
                    start.return_value.pid = 87654
                    start.return_value.poll.return_value = None
                    self.assertEqual(run.supervise(), 1)
                    start.assert_called_once()
                    stop.assert_called_once_with(87654, run.signal.SIGTERM)
                    self.assertEqual(run.read(root / "terminal.json")["status"], "stopped_no_retry")


if __name__ == "__main__":
    unittest.main()
