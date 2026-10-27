import builtins
import copy
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
from fas.feature_cache import digest, save_shard
from fas.freeze import write_immutable_record
from fas.frozen_features import mean_cosine_logit
from fas.readout_study import (
    BRANCHES, SYSTEMS, check_predictions, error_overlap, fit_readouts, metrics,
    paired_uncertainty, score_readouts, selected_index, transform, validate_context,
)
from fas.source_experiment import predict
from fas.source_fitting import calibrate, fit_calibrator, fit_head, head_logits, identity, operating_threshold, partitions
import run_readout308 as run


def fixture():
    rows = []
    for domain in ("CASIA-FASD", "MSU-MFSD", "SiW-Mv2"):
        for role in ("train", "branch_calibration", "g_domain"):
            for label in ("bona_fide", "attack"):
                for number in range(24):
                    key = f"{role}-{label}-{number}"
                    rows.append({
                        "dataset": domain, "video_id": key, "group_id": key, "group_unit": "video",
                        "role": role, "binary_label": label, "source_use_eligible": True,
                        "source_use_binding": {"policy_id": "synthetic"}, "model_input_eligible": True,
                        "selected_frame": {"rgb_sha256": f"{domain}-{key}"},
                    })
    config = run.read(run.CONFIG)
    config["head"]["epochs"] = 8
    config["bootstrap_repetitions"] = 24
    rng = np.random.default_rng(42)
    y = np.asarray([row["binary_label"] == "attack" for row in rows], dtype=np.float64)
    features = {name: rng.normal(size=(len(rows), 4)).astype(np.float32) for name in BRANCHES}
    for values in features.values():
        values[:, 0] += y
    features["openclip"] = transform(features["openclip"], "unit_l2").astype(np.float32)
    text = rng.normal(size=(4, 4)).astype(np.float32)
    clip = mean_cosine_logit(features["openclip"], text, 2)
    splits = partitions(rows, "OULU-NPU", 20260917)
    old = {}
    index = {identity(row): position for position, row in enumerate(rows)}
    for split in splits[:4]:
        positions = {key: np.asarray([index[value] for value in split[key]]) for key in
                     ("fitting", "validation", "calibration")}
        fit, validation, calibration = (positions[key] for key in ("fitting", "validation", "calibration"))
        domains = lambda selected: [rows[position]["dataset"] for position in selected]
        heads = {name: fit_head(features[name][fit], y[fit], domains(fit), features[name][validation],
                                y[validation], domains(validation), seed=20260917,
                                settings=config["head"], guard=lambda: None) for name in ("dino_reg", "dino_plain")}
        logits = {name: head_logits(model, features[name][calibration]) for name, model in heads.items()}
        logits["openclip"] = clip[calibration]
        calibrators = {name: fit_calibrator(values.astype(np.float64), y[calibration], domains(calibration), lambda: None)
                       for name, values in logits.items()}
        p = {name: calibrate(calibrators[name], values) for name, values in logits.items()}
        systems = {"dino_reg": p["dino_reg"], "openclip": p["openclip"],
                   "same_family": (p["dino_reg"] + p["dino_plain"]) / 2,
                   "heterogeneous": (p["dino_reg"] + p["openclip"]) / 2}
        policies = {name: operating_threshold(values, [rows[position] for position in calibration], alpha=0.05)
                    for name, values in systems.items()}
        old[split["name"]] = {"split": split, "heads": heads, "calibrators": calibrators, "policies": policies}
    return rows, features, text, clip, splits[:4], config, old


class ReadoutCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.features, cls.text, cls.clip, cls.splits, cls.config, cls.old = fixture()
        cls.split = cls.splits[1]
        cls.fitted = fit_readouts(
            cls.rows, cls.features, cls.old[cls.split["name"]], cls.split, cls.config, 20260917,
            lambda: None, {"new_head_fits": 0, "new_calibrator_fits": 0})

    def test_feature_transform_is_per_vector_deterministic_and_fail_closed(self):
        values = np.asarray([[3.0, 4.0], [0.0, 2.0]], dtype=np.float32)
        np.testing.assert_array_equal(transform(values, "raw"), values)
        np.testing.assert_array_equal(transform(values, "unit_l2"), [[0.6, 0.8], [0, 1]])
        np.testing.assert_array_equal(transform(values, "unit_l2")[0], transform(values[:1], "unit_l2")[0])
        for values, name in ((np.zeros((1, 2)), "unit_l2"), (np.ones((1, 2)), "learned"),
                             (np.asarray([[np.nan]]), "raw"), (np.ones((0, 2)), "raw")):
            with self.assertRaises(ValueError):
                transform(values, name)

    def test_candidate_ties_use_declared_order_and_nonfinite_is_failure(self):
        self.assertEqual(selected_index([{"model": {"validation_bce": 1.0}}] * 4), 0)
        with self.assertRaises(ValueError):
            selected_index([{"model": {"validation_bce": np.nan}}])

    def test_exact_nested_roles_groups_and_domain_exclusions_are_required(self):
        for split in self.splits:
            validate_context(self.rows, split, "OULU-NPU", 20260917)
        bad = copy.deepcopy(self.split)
        bad["fitting"].append(bad["evaluation"][0])
        with self.assertRaises(ValueError):
            validate_context(self.rows, bad, "OULU-NPU", 20260917)
        with self.assertRaises(ValueError):
            validate_context(self.rows, self.splits[0], "CASIA-FASD", 20260917)
        bad = copy.deepcopy(self.split)
        bad["name"] = "matched_sample_oof:0"
        with self.assertRaises(ValueError):
            validate_context(self.rows, bad, "OULU-NPU", 20260917)

    def test_exact_anchor_reuse_and_new_fit_counts(self):
        counters = {"new_head_fits": 0, "new_calibrator_fits": 0}
        fitted = fit_readouts(self.rows, self.features, self.old[self.split["name"]], self.split,
                              self.config, 20260917, lambda: None, counters)
        self.assertEqual(counters, {"new_head_fits": 10, "new_calibrator_fits": 3})
        for name in ("dino_reg", "dino_plain"):
            self.assertEqual(fitted["candidates"][name][0]["model"], self.old[self.split["name"]]["heads"][name])
            self.assertEqual(fitted["candidates"][name][0]["origin"], "baseline299_anchor")
        self.assertTrue(all(item["origin"] == "new_readout" for item in fitted["candidates"]["openclip"]))

    def test_evaluation_labels_cannot_select_candidates_or_calibration(self):
        rows = copy.deepcopy(self.rows)
        held_out = set(self.split["evaluation"])
        for row in rows:
            if identity(row) in held_out:
                row["binary_label"] = "bona_fide" if row["binary_label"] == "attack" else "attack"
        fitted = fit_readouts(rows, self.features, self.old[self.split["name"]], self.split, self.config,
                              20260917, lambda: None, {"new_head_fits": 0, "new_calibrator_fits": 0})
        self.assertEqual(fitted, self.fitted)

    def test_fit_budget_stops_before_an_extra_model(self):
        with patch("fas.readout_study.fit_head") as fit:
            with self.assertRaisesRegex(RuntimeError, "head-fit budget"):
                fit_readouts(self.rows, self.features, self.old[self.split["name"]], self.split, self.config,
                              20260917, lambda: None,
                              {"new_head_fits": self.config["limits"]["new_head_fits"], "new_calibrator_fits": 0})
            fit.assert_not_called()

    def test_calibrator_budget_stops_before_an_extra_calibration(self):
        with patch("fas.readout_study.fit_calibrator") as fit:
            with self.assertRaisesRegex(RuntimeError, "calibrator-fit budget"):
                fit_readouts(self.rows, self.features, self.old[self.split["name"]], self.split, self.config,
                              20260917, lambda: None,
                              {"new_head_fits": 0, "new_calibrator_fits": self.config["limits"]["new_calibrator_fits"]})
            fit.assert_not_called()

    def test_optimizer_failure_preserves_completed_candidates_and_does_not_retry(self):
        checkpoints = {}
        with patch("fas.readout_study.fit_calibrator", side_effect=RuntimeError("ABNORMAL")) as fit:
            with self.assertRaisesRegex(RuntimeError, "ABNORMAL"):
                fit_readouts(self.rows, self.features, self.old[self.split["name"]], self.split, self.config,
                              20260917, lambda: None, {"new_head_fits": 0, "new_calibrator_fits": 0},
                              lambda name, value: checkpoints.update({name: value}))
            fit.assert_called_once()
        self.assertEqual(len([name for name in checkpoints if name.startswith("head-") and name.endswith("-complete")]), 4)
        self.assertIn("calibrator-dino_reg-started", checkpoints)
        self.assertNotIn("calibrator-dino_reg-complete", checkpoints)

    def test_scoring_preserves_all_original_baselines(self):
        old = self.old[self.split["name"]]
        records, candidates = score_readouts(self.rows, self.features, self.clip, old, self.fitted, self.config)
        historical = predict(self.rows, self.features, self.clip, np.zeros((len(self.rows), 5)),
                             self.split["evaluation"], old, "synthetic")
        for row, original in zip(records, historical, strict=True):
            self.assertEqual(row["id"], original["id"])
            for name, prior in (("old_dino_reg", "dino_reg"), ("old_two_dino", "same_family"),
                                ("zero_shot_clip", "openclip")):
                self.assertEqual(row["scores"][name], original["scores"][prior])
                self.assertEqual(row["thresholds"][name], original["thresholds"][prior])
        self.assertEqual(set(candidates), set(BRANCHES))
        self.assertTrue(all(len(items) == 4 for items in candidates.values()))

    def test_saved_models_calibration_selection_and_policy_reconstruct(self):
        run.verify_fit(self.rows, self.features, self.fitted, self.config)
        for field in ("selection", "objective", "policy"):
            fitted = copy.deepcopy(self.fitted)
            if field == "selection":
                fitted["selected"]["openclip"] = (fitted["selected"]["openclip"] + 1) % 4
            elif field == "objective":
                fitted["calibrators"]["openclip"]["bce"] += 0.1
            else:
                fitted["policies"]["supervised_clip"]["threshold"] += 0.1
            with self.assertRaises(ValueError):
                run.verify_fit(self.rows, self.features, fitted, self.config)

    def test_no_encoder_or_decoder_import_is_needed_for_fitting(self):
        original_import = builtins.__import__

        def guarded(name, *args, **kwargs):
            if name.split(".")[0] in {"torch", "open_clip", "PIL"}:
                raise AssertionError(f"forbidden encoder/image dependency {name}")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=guarded):
            fit_readouts(self.rows, self.features, self.old[self.split["name"]], self.split, self.config,
                         20260917, lambda: None, {"new_head_fits": 0, "new_calibrator_fits": 0})

    def test_paired_bootstrap_is_deterministic_and_not_new_domain_uncertainty(self):
        records, _ = score_readouts(self.rows, self.features, self.clip, self.old[self.split["name"]],
                                    self.fitted, self.config)
        first = paired_uncertainty(records, 24, 7, lambda: None)
        self.assertEqual(first, paired_uncertainty(records, 24, 7, lambda: None))
        self.assertEqual(set(first["supervised_clip_minus"]), {"zero_shot_clip", "selected_dino_reg", "selected_two_dino"})
        self.assertIn("not_training_or_new_domain", first["scope"])
        one_class = [{**row, "label": 0} for row in records]
        with self.assertRaises(ValueError):
            paired_uncertainty(one_class, 24, 7, lambda: None)
        with self.assertRaises(ValueError):
            paired_uncertainty(records, 0, 7, lambda: None)


class ReadoutMetricTests(unittest.TestCase):
    def setUp(self):
        self.originals, self.records = [], []
        for number, (label, score) in enumerate(((0, 0.2), (0, 0.8), (1, 0.1), (1, 0.9), (0, None), (1, None))):
            row = {"dataset": "A", "video_id": str(number), "group_id": str(number), "role": "g_domain",
                   "source_use_eligible": True, "model_input_eligible": score is not None,
                   "binary_label": "attack" if label else "bona_fide"}
            self.originals.append(row)
            if score is not None:
                self.records.append({"id": identity(row), "dataset": "A", "group_id": str(number), "role": "g_domain",
                                     "label": label, "scores": dict.fromkeys(SYSTEMS, score),
                                     "thresholds": dict.fromkeys(SYSTEMS, 0.5)})

    def test_exact_original_and_successful_denominators_are_distinct(self):
        result = metrics(self.records, self.originals)
        domain = result["per_domain"]["A"]
        system = domain["systems"]["supervised_clip"]
        self.assertEqual(domain["technical_failures"], 2)
        self.assertEqual(domain["ranking_coverage"], 4 / 6)
        self.assertEqual(system["successful_ACER"], 0.5)
        self.assertEqual(system["successful_balanced_accuracy"], 0.5)
        self.assertEqual(system["original_attack_FA"], 1 / 3)
        self.assertAlmostEqual(system["original_bona_fide_non_acceptance"], 2 / 3)
        self.assertEqual(system["original_operational_acceptance_coverage"], 2 / 6)

    def test_attack_tie_is_not_accepted(self):
        for name in SYSTEMS:
            self.records[2]["scores"][name] = 0.5
        result = metrics(self.records, self.originals)["per_domain"]["A"]["systems"]["supervised_clip"]
        self.assertEqual(result["original_attack_FA"], 0.0)

    def test_missing_duplicate_mislabelled_nonfinite_and_role_drift_fail(self):
        bad_values = [self.records[:-1], self.records + self.records[:1]]
        for field, value in (("label", 1), ("group_id", "wrong"), ("role", "train")):
            records = copy.deepcopy(self.records)
            records[0][field] = value
            bad_values.append(records)
        records = copy.deepcopy(self.records)
        records[0]["scores"]["supervised_clip"] = np.nan
        bad_values.append(records)
        for records in bad_values:
            with self.assertRaises(ValueError):
                check_predictions(records, self.originals)

    def test_overlap_counts_are_on_the_common_successful_population(self):
        result = error_overlap(self.records)["selected_dino_reg"]
        self.assertEqual([result[key] for key in ("both_wrong", "clip_only_wrong", "comparator_only_wrong", "both_correct")],
                         [2, 0, 0, 2])

    def test_numeric_readback_tolerance_does_not_hide_identity_or_large_score_drift(self):
        run.check_reconstruction({"p": [0.1]}, {"p": [0.1 + 1e-16]})
        for rebuilt in ({"p": [0.1001]}, {"p": [0.1], "extra": 0}, {"p": [1]}):
            with self.assertRaises(ValueError):
                run.check_reconstruction({"p": [0.1]}, rebuilt)


class ReadoutControllerTests(unittest.TestCase):
    def test_shard_hash_order_and_complete_coverage_are_verified_without_inference(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "features.npz"
            features = np.ones((2, 3), dtype=np.float32)
            save_shard(path, ["a", "b"], features)
            model = {"shards": [{"path": str(path), "sha256": digest(path), "count": 2}]}
            np.testing.assert_array_equal(run.shard_matrix(model, ["a", "b"], 3, lambda: None), features)
            with self.assertRaises(ValueError):
                run.shard_matrix(model, ["b", "a"], 3, lambda: None)
            with self.assertRaises(ValueError):
                run.shard_matrix(model, ["a", "b", "c"], 3, lambda: None)
            model["shards"][0]["sha256"] = "0" * 64
            with self.assertRaises(ValueError):
                run.shard_matrix(model, ["a", "b"], 3, lambda: None)

    def test_absent_approval_expired_clock_and_existing_attempt_block_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = {"private_root": str(root), "output_name": "study", "study": "synthetic",
                      "limits": {"wall_seconds": 10}}
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config))
            plan = {"config_sha256": digest(config_path), "code_sha256": {}}
            write_immutable_record(root / "study/execution_plan.json", plan)
            with patch.object(run, "CONFIG", config_path), patch.object(run, "code_pins", return_value={}):
                with self.assertRaises(FileNotFoundError):
                    run.authority()
            approval = {"started_unix": time.time() - 20, "deadline_unix": time.time() - 10}
            with patch.object(run, "authority", return_value=(config, plan, approval)), patch.object(run.subprocess, "Popen") as start:
                with self.assertRaises(TimeoutError):
                    run.supervise()
                start.assert_not_called()
            approval["deadline_unix"] = time.time() + 10
            write_immutable_record(root / "study/attempt_lock.json", {"existing": True})
            with patch.object(run, "authority", return_value=(config, plan, approval)), patch.object(run.subprocess, "Popen") as start:
                with self.assertRaises(FileExistsError):
                    run.supervise()
                start.assert_not_called()

    def test_synthetic_end_to_end_and_saved_closure_do_not_refit(self):
        rows, features, text, _, splits, config, old = fixture()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = {**config, "private_root": temporary, "output_name": "synthetic", "baseline": "old"}
            context = {"key": "synthetic", "outer_target": "OULU-NPU", "seed": 20260917,
                       "row_ids": [identity(row) for row in rows], "partitions": splits}
            inputs = {"rows": rows, "contexts": [context]}
            plan = {"new_head_fits": 40, "new_calibrator_fits": 12}
            write_immutable_record(root / "synthetic/execution_plan.json", plan)
            write_immutable_record(root / "synthetic/attempt_lock.json", {"supervisor_pid": os.getppid()})
            for split in splits:
                write_immutable_record(run.fit_path(config, context, split), {"fitted": old[split["name"]]})
            approval = {"started_unix": time.time(), "deadline_unix": time.time() + 120}
            real_read = run.read
            with (patch.object(run, "authority", return_value=(config, plan, approval)),
                  patch.object(run, "load_inputs", return_value=(inputs, rows, features, text, {})),
                  patch.object(run, "build_plan", return_value=plan),
                  patch.object(run, "read", wraps=run.read) as reader):
                def values(path):
                    if path == ROOT / "configs/prompts_core_v1.yaml":
                        return {"classes": {"live": [0, 1]}}
                    return real_read(path)

                reader.side_effect = values
                result = run.run_worker()
                self.assertEqual(result["fit_counts"], {"new_head_fits": 40, "new_calibrator_fits": 12})
                self.assertEqual(result["encoder_forwards"], 0)
                self.assertEqual(len(result["combinations"][0]["selections"]), 4)
                with patch.object(run, "fit_readouts", side_effect=AssertionError("closure must not fit")):
                    self.assertEqual(result, run.run_worker(verify_only=True))

    def test_resource_caps_stop_the_specific_worker_without_retry(self):
        for exhausted in ("combined_sampled_rss_bytes", "owned_output_bytes"):
            with self.subTest(exhausted=exhausted), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                config = run.read(run.CONFIG)
                config.update({"private_root": temporary, "output_name": "synthetic"})
                config["limits"]["combined_sampled_rss_bytes"] = 10 ** 15
                config["limits"]["owned_output_bytes"] = 10 ** 15
                config["limits"][exhausted] = 100000 if exhausted == "owned_output_bytes" else 1
                write_immutable_record(root / "synthetic/execution_plan.json", {"synthetic": True})
                approval = {"started_unix": time.time(), "deadline_unix": time.time() + 120}
                with (patch.object(run, "authority", return_value=(config, {}, approval)),
                      patch.object(run.subprocess, "Popen") as start,
                      patch.object(run.os, "kill") as stop,
                      patch.object(run, "owned_size", side_effect=lambda path: 200000 if start.called else 200),
                      patch.object(run.baseline.pilot, "group_rss", return_value=1024)):
                    start.return_value.pid = 67890
                    start.return_value.poll.return_value = None
                    self.assertEqual(run.supervise(), 1)
                    start.assert_called_once()
                    stop.assert_called_once_with(67890, run.signal.SIGTERM)
                    terminal = run.read(root / "synthetic/terminal.json")
                    self.assertEqual(terminal["status"], "stopped_no_retry")
                    self.assertIn("MemoryError", terminal["failure"])


if __name__ == "__main__":
    unittest.main()
