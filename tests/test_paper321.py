import contextlib
from fractions import Fraction
import hashlib
import importlib.util
import io
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/paper321"))
import runner
import study

HAS_TORCH = importlib.util.find_spec("torch") is not None and importlib.util.find_spec("torchvision") is not None
if HAS_TORCH and os.environ.get("PAPER321_TEST_CHILD") == "1":
    import torch
    import specialist


def row(domain, group, label, split="train", success=True):
    return {"dataset": domain, "group_id": group, "subject_id": None if domain == "SiW-Mv2" else group,
            "video_id": f"{group}-{label}", "binary_label": label, "official_split": split,
            "source_use_eligible": True, "detector_status": "success" if success else "failed",
            "selected_frame": {"rgb_sha256": f"{domain}:{group}:{label}"}}


def isolated_network_test(function):
    def run(self):
        if os.environ.get("PAPER321_TEST_CHILD") == "1":
            function(self)
            return
        result = subprocess.run(
            [sys.executable, "-m", "unittest", f"test_paper321.SpecialistTests.{function.__name__}", "-v"],
            cwd=ROOT / "tests", env={**os.environ, "PAPER321_TEST_CHILD": "1"},
            capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    return run


class AnalysisTests(unittest.TestCase):
    def test_direct_subject_check_catches_inconsistent_group_ids(self):
        first = row("MSU-MFSD", "a", "attack")
        second = row("MSU-MFSD", "b", "bona_fide")
        second["subject_id"] = first["subject_id"]
        with self.assertRaisesRegex(ValueError, "known subject"):
            study.isolation([[first], [second]])

    def test_exact_integer_calibration_budgets_and_limiting_source(self):
        rows = [row("MSU-MFSD", str(i), "attack") for i in range(18)]
        rows += [row("CASIA-FASD", str(i), "attack") for i in range(20)]
        scores = np.r_[np.linspace(.4, .9, 18), np.linspace(.2, .8, 20)]
        one = study.threshold(scores, rows, Fraction(1, 100))
        five = study.threshold(scores, rows, Fraction(1, 20))
        self.assertEqual(one["sources"]["MSU-MFSD"]["error_budget"], 0)
        self.assertEqual(five["sources"]["MSU-MFSD"]["error_budget"], 0)
        self.assertEqual(five["sources"]["CASIA-FASD"]["error_budget"], 1)
        self.assertEqual(five["limiting_sources"], ["CASIA-FASD"])
        self.assertEqual(five["threshold"], scores[19])

    def test_ties_at_threshold_reject_and_failures_keep_denominators(self):
        originals = [row("MSU-MFSD", "a", "attack"), row("MSU-MFSD", "b", "bona_fide"),
                     row("MSU-MFSD", "c", "bona_fide", success=False)]
        point = study.metrics(np.array([.5, .2]), originals, .5)
        self.assertEqual(point["FA"], 0)
        self.assertEqual(point["BFA"], .5)
        self.assertEqual(point["FA_usable"], 0)
        self.assertEqual(point["BF_rejection_usable"], 0)
        self.assertEqual(point["original_bona_fide"], 2)
        self.assertEqual(study.curve(np.array([.5, .2]), originals)[-1], [1, .5])

    def test_invalid_or_unjoined_scores_rejected(self):
        rows = [row("MSU-MFSD", "a", "attack"), row("MSU-MFSD", "b", "bona_fide")]
        for scores in [np.array([.1]), np.array([np.nan, .1]), np.array([1.1, .1])]:
            with self.assertRaises(ValueError):
                study.metrics(scores, rows, .5)
        with self.assertRaises(ValueError):
            study.threshold(np.array([.1, .2]), rows, Fraction(1))

    def test_paired_bootstrap_and_oracle_are_explicitly_separate(self):
        rows = [row("MSU-MFSD", str(i//2), "attack" if i%2 else "bona_fide") for i in range(8)]
        prediction = {system: [.1, .9]*4 for system in study.SYSTEMS}
        policies = {system: {str(alpha): study.threshold(np.array(prediction[system]), rows, alpha)
                             for alpha in study.ALPHAS} for system in study.SYSTEMS}
        a = study.summarize_context(prediction, rows, policies, runner.oracle316.oracle, lambda: None, repetitions=30)
        b = study.summarize_context(prediction, rows, policies, runner.oracle316.oracle, lambda: None, repetitions=30)
        self.assertEqual(a, b)
        self.assertEqual(len(a["cases"]), 12)
        self.assertIsNone(a["oracle_intervals"])
        self.assertTrue(all(item["percentile95"] == [0, 0] for item in a["paired_minus_dino_reg"]))
        self.assertNotIn("oracle_threshold_not_deployable", json.dumps(a))

    def test_unknown_siw_bootstrap_label_is_video_not_subject(self):
        rows = [row("SiW-Mv2", str(i), "attack" if i%2 else "bona_fide") for i in range(8)]
        prediction = {system: [.1, .9]*4 for system in study.SYSTEMS}
        policies = {system: {str(alpha): study.threshold(np.array(prediction[system]), rows, alpha)
                             for alpha in study.ALPHAS} for system in study.SYSTEMS}
        result = study.summarize_context(prediction, rows, policies, runner.oracle316.oracle,
                                        lambda: None, repetitions=20)
        self.assertEqual(result["bootstrap_unit"], "video_exact_frame_component")
        svg = study.plot([{"target": "SiW-Mv2", "analysis": result}])
        self.assertIn("<svg", svg)
        self.assertIn("clipPath", svg)

    def test_optimized_bootstrap_matches_reference_with_ties_failures_and_one_class_draws(self):
        for domain in ("MSU-MFSD", "SiW-Mv2"):
            rows = [row(domain, str(i//3), "attack" if i < 6 else "bona_fide",
                        success=i not in (1, 8)) for i in range(12)]
            for i, record in enumerate(rows):
                record["video_id"] = f"video-{i}"
                record["selected_frame"]["rgb_sha256"] = f"frame-{i}"
            rng = np.random.default_rng(42)
            prediction = {system: rng.choice([.1, .3, .5, .9], 10).tolist() for system in study.SYSTEMS}
            policies = {system: {str(alpha): {"threshold": .3 if alpha == study.ALPHAS[0] else .5,
                                             "limiting_sources": [], "sources": {}}
                                 for alpha in study.ALPHAS} for system in study.SYSTEMS}
            result = study.summarize_context(prediction, rows, policies, runner.oracle316.oracle,
                                            lambda: None, repetitions=200)
            mapping = study.components([{**r, "group_id": r["subject_id"] or r["group_id"]} for r in rows])
            groups = sorted(set(mapping.values()))
            indexes = np.array([groups.index(mapping[runner.identity(r)]) for r in rows])
            rng = np.random.default_rng(20261028)
            samples = {}
            paired = {}
            for _ in range(200):
                weights = rng.multinomial(len(groups), np.full(len(groups), 1/len(groups)))[indexes]
                current = {}
                for system in study.SYSTEMS:
                    for alpha in study.ALPHAS:
                        point = study.metrics(np.array(prediction[system]), rows,
                                              policies[system][str(alpha)]["threshold"], weights)
                        for metric in ("FA", "BFA", "AUROC_usable"):
                            key = (system, str(alpha), metric)
                            current[key] = point[metric]
                            samples.setdefault(key, [])
                            if point[metric] is not None:
                                samples[key].append(point[metric])
                for key, value in current.items():
                    if key[0] == "dino_reg":
                        continue
                    anchor = current[("dino_reg", key[1], key[2])]
                    paired.setdefault(key, [])
                    if value is not None and anchor is not None:
                        paired[key].append(value-anchor)
            for field, expected in (("conditional_intervals", samples), ("paired_minus_dino_reg", paired)):
                for item in result[field]:
                    values = expected[(item["system"], item["alpha"], item["metric"])]
                    self.assertEqual(item["valid_repetitions"], len(values))
                    interval = np.quantile(values, [.025, .975]).tolist() if len(values) >= 190 else None
                    self.assertEqual(item["percentile95"], interval)


class AuthorityAndBudgetTests(unittest.TestCase):
    def approval(self):
        return {"boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
                "started_monotonic": time.monotonic(),
                "limits": runner.read(runner.SPEC)["proposed_limits"]}

    def test_wrong_approval_does_not_create_authority(self):
        with patch.object(runner, "check_plan", side_effect=AssertionError("not reached")):
            with self.assertRaisesRegex(ValueError, "explicit"):
                runner.approve("review_accepted")
        original = {**self.approval(), "started_unix": time.time()-120}
        with tempfile.TemporaryDirectory() as directory:
            previous, amended = Path(directory)/"old", Path(directory)/"new"
            runner.write_immutable_record(previous/"owner_approval.json", original)
            runner.write_immutable_record(amended/"execution_plan.json", {})
            with patch.object(runner, "PREVIOUS", previous), patch.object(runner, "OUTPUT", amended), \
                 patch.object(runner, "check_plan", return_value={"limits": original["limits"]}):
                runner.approve(runner.ANSWER)
            receipt = runner.read(amended/"owner_approval.json")
            for key in ("started_monotonic", "started_unix", "boot_id", "limits"):
                self.assertEqual(receipt[key], original[key])

    def test_original_work_final_and_context_deadlines(self):
        a = self.approval()
        a["started_monotonic"] -= a["limits"]["work_cutoff_seconds"] + 1
        with self.assertRaises(TimeoutError):
            runner.clock(a)
        runner.clock(a, final=True)
        with self.assertRaises(TimeoutError):
            runner.clock(self.approval(), context_started=time.monotonic()-2401)
        a["started_monotonic"] -= 3600
        with self.assertRaises(TimeoutError):
            runner.clock(a, final=True)

    def test_storage_and_cuda_caps_surface_errors(self):
        a = self.approval()
        with patch.object(runner, "owned_size", return_value=a["limits"]["owned_new_and_temporary_output_bytes"]):
            with self.assertRaises(MemoryError):
                runner.resources(a)
        fake = SimpleNamespace(cuda=SimpleNamespace(
            max_memory_allocated=lambda: 2**40, max_memory_reserved=lambda: 0))
        with patch.object(runner, "owned_size", return_value=0), patch.dict(sys.modules, {"torch": fake}):
            with self.assertRaises(MemoryError):
                runner.resources(a, cuda=True)

    def test_download_is_bounded_hash_checked_and_immutable_without_network(self):
        payload = b"synthetic-checkpoint-not-a-model"
        def response():
            class Response(io.BytesIO):
                headers = {"Content-Length": str(len(payload))}
            return Response(payload)
        plan = {"initialization_acquisition": {"url": "https://example.invalid",
                "sha256_prefix": hashlib.sha256(payload).hexdigest()[:8], "max_bytes": len(payload)}}
        with tempfile.TemporaryDirectory() as directory, patch.object(runner, "OUTPUT", Path(directory)):
            with patch.object(runner.urllib.request, "urlopen", return_value=response()):
                path = runner.acquire(plan, lambda: None)
            self.assertEqual(path.read_bytes(), payload)
            with self.assertRaises(FileExistsError):
                runner.acquire(plan, lambda: None)
        plan["initialization_acquisition"]["max_bytes"] = 1
        with tempfile.TemporaryDirectory() as directory, patch.object(runner, "OUTPUT", Path(directory)), \
             patch.object(runner.urllib.request, "urlopen", return_value=response()):
            with self.assertRaises(MemoryError):
                runner.acquire(plan, lambda: None)
        plan["initialization_acquisition"].update(max_bytes=len(payload), sha256_prefix="00000000")
        with tempfile.TemporaryDirectory() as directory, patch.object(runner, "OUTPUT", Path(directory)), \
             patch.object(runner.urllib.request, "urlopen", return_value=response()):
            with self.assertRaisesRegex(ValueError, "hash prefix"):
                runner.acquire(plan, lambda: None)

    def test_watchdog_stops_hung_child_for_rss_and_context_time(self):
        for reason in ("rss", "context"):
            with self.subTest(reason=reason), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                a = self.approval()
                runner.write_immutable_record(root/"execution_plan.json", {})
                fake = SimpleNamespace(pid=999999, returncode=None)
                fake.poll = lambda: fake.returncode
                def stop(*args, **kwargs):
                    fake.returncode = -15
                fake.wait = stop
                def spawn(*args, **kwargs):
                    if reason == "context":
                        runner.active_context("synthetic", "worker", time.monotonic()-2401)
                    return fake
                with patch.object(runner, "OUTPUT", root), \
                     patch.object(runner, "authority", return_value=({"limits": a["limits"]}, a)), \
                     patch.object(runner.subprocess, "Popen", side_effect=spawn) as launched, \
                     patch.object(runner.os, "killpg") as kill, \
                     patch.object(runner.legacy.pilot, "group_rss", return_value=2**40):
                    self.assertEqual(runner.supervise(), 1)
                    self.assertEqual(launched.call_count, 1)
                    kill.assert_called_once_with(999999, runner.signal.SIGTERM)
                    terminal = runner.read(root/"terminal.json")
                    self.assertIn("RSS" if reason == "rss" else "context ceiling", terminal["failure"])

    def test_supervisor_reports_nonzero_worker_as_incomplete_without_retry(self):
        a = self.approval()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runner.write_immutable_record(root/"execution_plan.json", {})
            fake = SimpleNamespace(poll=lambda: 1, returncode=1)
            with patch.object(runner, "OUTPUT", root), \
                 patch.object(runner, "authority", return_value=({"limits": a["limits"]}, a)), \
                 patch.object(runner.subprocess, "Popen", return_value=fake) as spawn:
                self.assertEqual(runner.supervise(), 1)
                self.assertEqual(spawn.call_count, 1)
                self.assertEqual(runner.read(root/"terminal.json")["status"], "stopped_no_retry")
                with self.assertRaises(FileExistsError):
                    runner.supervise()

    def test_subject_leak_in_final_private_partitions_rejected(self):
        first = row("CASIA-FASD", "a", "attack")
        second = row("CASIA-FASD", "b", "bona_fide")
        second["subject_id"] = first["subject_id"]
        target = row("MSU-MFSD", "test", "attack", "test")
        context = {"target": "MSU-MFSD", "seed": 1, "fitting": [runner.identity(first)],
                   "validation": [runner.identity(second)], "calibration": [],
                   "evaluation": [runner.identity(target)]}
        with self.assertRaisesRegex(ValueError, "known subject"):
            runner.validate_partitions([first, second, target], {"contexts": [context]})

    def test_bound_file_drift_and_missing_file_are_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"input"
            path.write_bytes(b"one")
            with self.assertRaisesRegex(ValueError, "changed"):
                runner.bind({}, path, "0"*64)
            path.unlink()
            with self.assertRaisesRegex(ValueError, "regular"):
                runner.bind({}, path)


@unittest.skipUnless(HAS_TORCH, "torch/torchvision absent; actual specialist tests require the FAS environment")
class SpecialistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get("PAPER321_TEST_CHILD") == "1":
            specialist.configure(7)

    @isolated_network_test
    def test_exact_architecture_loss_gradient_initialization_and_restore(self):
        from torchvision.models import densenet161
        initial = densenet161(weights=None).state_dict()
        model = specialist.Specialist(initial)
        legacy = {
            re.sub(r"(\.denselayer[0-9]+\.(?:norm|relu|conv))([12])\.", r"\1.\2.", key): value
            for key, value in initial.items() if not key.endswith("num_batches_tracked")}
        converted = specialist.Specialist(legacy)
        for key, value in model.encoder.state_dict().items():
            torch.testing.assert_close(converted.encoder.state_dict()[key], value, rtol=0, atol=0)
        bad = dict(legacy)
        bad["features.denseblock1.denselayer1.norm1.weight"] = initial[
            "features.denseblock1.denselayer1.norm1.weight"]
        with self.assertRaisesRegex(ValueError, "colliding"):
            specialist.Specialist(bad)
        del converted
        self.assertTrue(torch.equal(model.encoder[0].weight, initial["features.conv0.weight"]))
        images = torch.randn(2, 3, 224, 224)
        model.train()
        pixel, global_logits = model(images)
        self.assertEqual(tuple(pixel.shape), (2, 1, 14, 14))
        self.assertEqual(tuple(global_logits.shape), (2, 1))
        self.assertTrue(torch.allclose(global_logits, model.global_head(pixel.sigmoid().flatten(1))))
        targets = torch.tensor([0., 1.])
        specialist.losses((pixel, global_logits), targets).mean().backward()
        for parameter in [model.encoder[0].weight, model.pixel.weight, model.global_head.weight]:
            self.assertIsNotNone(parameter.grad)
            self.assertGreater(float(parameter.grad.abs().sum()), 0)
        model.eval()
        with torch.inference_mode():
            outputs = model(images)
            expected = 1-outputs[0].sigmoid().mean((1, 2, 3))
            self.assertTrue(torch.equal(specialist.attack_scores(outputs), expected))
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)/"model.pth"
            runner.atomic_checkpoint(p, {"state_dict": model.state_dict()}, lambda: None)
            restored = specialist.Specialist()
            restored.load_state_dict(torch.load(p, weights_only=True)["state_dict"], strict=True)
            restored.eval()
            with torch.inference_mode():
                self.assertTrue(torch.equal(restored(images)[0], outputs[0]))
            with self.assertRaises(FileExistsError):
                runner.atomic_checkpoint(p, {"state_dict": model.state_dict()}, lambda: None)

    @isolated_network_test
    def test_eval_does_not_update_batchnorm_and_bad_resolution_rejected(self):
        model = specialist.Specialist().eval()
        before = model.encoder[1].running_mean.clone()
        with torch.inference_mode():
            model(torch.randn(2, 3, 224, 224))
        self.assertTrue(torch.equal(before, model.encoder[1].running_mean))
        with self.assertRaises(ValueError):
            model(torch.randn(2, 3, 112, 112))

    @isolated_network_test
    def test_sampler_augmentation_and_checkpoint_selection_repeat_exactly(self):
        class Toy(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.weight = torch.nn.Parameter(torch.tensor(.1))
            def forward(self, images):
                x = images[:, :1, :1, :1] * self.weight
                return x, x.flatten(1)
        rows = [row("MSU-MFSD", str(i), "attack" if i%2 else "bona_fide") for i in range(8)]
        traces = []
        def batch(chosen, device, generator):
            flips = torch.rand(len(chosen), generator=generator).tolist() if generator is not None else []
            traces.append(([r["video_id"] for r in chosen], flips))
            return torch.tensor([[[[1. if r["binary_label"] == "bona_fide" else -1.]]]
                                 for r in chosen])
        settings = {**runner.read(runner.SPEC)["specialist"], "epochs": 3, "batch_size": 3}
        with contextlib.redirect_stdout(io.StringIO()):
            a = specialist.train_model(Toy(), rows, rows, batch, 7, settings, "cpu", lambda: None)
            first = traces.copy()
            traces.clear()
            b = specialist.train_model(Toy(), rows, rows, batch, 7, settings, "cpu", lambda: None)
        self.assertEqual(first, traces)
        self.assertEqual(a["history"], b["history"])
        self.assertEqual(a["optimizer_steps"], 9)
        self.assertEqual(a["selected_epoch"], int(np.argmin(a["history"]))+1)

    @isolated_network_test
    def test_full_twelve_context_controller_and_no_fit_checkpoint_reconstruction(self):
        class FakeSpecialist(torch.nn.Module):
            def __init__(self, initial=None):
                super().__init__()
                self.weight = torch.nn.Parameter(torch.ones(1))
            def cuda(self):
                return self
        def fake_train(model, *args):
            epochs = args[4]["epochs"]
            return {"state_dict": model.state_dict(), "selected_epoch": 1,
                    "history": [.5]*epochs, "optimizer_steps": ((len(args[0])+15)//16)*epochs,
                    "validation_loss": .5, "seed": args[3]}
        def fake_predict(model, rows, *args):
            return np.asarray([.1 if r["binary_label"] == "bona_fide" else .9 for r in rows])
        rows, contexts = [], []
        domains = runner.preparation.DOMAINS
        for d in domains:
            for role in ("fitting", "validation", "calibration", "evaluation"):
                for label in ("bona_fide", "attack"):
                    r = row(d, role, label, "test" if role == "evaluation" else "train")
                    r["test_role"] = role
                    rows.append(r)
        for target in domains:
            for seed in runner.preparation.SEEDS:
                context = {"target": target, "seed": seed}
                for role in ("fitting", "validation", "calibration", "evaluation"):
                    context[role] = sorted(runner.identity(r) for r in rows if r["test_role"] == role
                                           and (r["dataset"] == target if role == "evaluation" else r["dataset"] != target))
                contexts.append(context)
        ids = sorted(runner.identity(r) for r in rows)
        indexed = {runner.identity(r): r for r in rows}
        features = {name: np.asarray([[float(indexed[key]["binary_label"] == "attack")] for key in ids])
                    for name in runner.BRANCHES[:3]}
        summarize = study.summarize_context
        def small_analysis(*args):
            return summarize(*args, repetitions=10)
        with tempfile.TemporaryDirectory() as directory, contextlib.ExitStack() as stack:
            root = Path(directory)/"run"
            root.mkdir()
            source = Path(directory)/"source.json"
            runner.write_immutable_record(source, {"rows": rows})
            split = Path(directory)/"partitions.json"
            runner.write_immutable_record(split, {"contexts": contexts})
            runner.write_immutable_record(root/"execution_plan.json", {})
            runner.write_immutable_record(root/"attempt.json", {
                "supervisor_pid": os.getppid(), "plan_sha256": runner.digest(root/"execution_plan.json")})
            torch.save({"synthetic": torch.ones(1)}, root/"initialization.pth")
            runner.write_immutable_record(root/"initialization.json", {
                "sha256": runner.digest(root/"initialization.pth")})
            config = runner.read(runner.SPEC)
            stack.enter_context(patch.object(runner, "OUTPUT", root))
            stack.enter_context(patch.object(runner.preparation, "MANIFEST", source))
            stack.enter_context(patch.object(runner.preparation, "OUTPUT", Path(directory)))
            stack.enter_context(patch.object(runner, "authority", return_value=(
                {"limits": config["proposed_limits"]}, {"limits": config["proposed_limits"]})))
            stack.enter_context(patch.object(runner, "resources"))
            stack.enter_context(patch.object(runner, "acquire", return_value=root/"initialization.pth"))
            stack.enter_context(patch.object(runner, "load_features", return_value=(ids, features)))
            stack.enter_context(patch.object(torch.cuda, "set_per_process_memory_fraction"))
            stack.enter_context(patch.object(torch.cuda, "get_device_properties", return_value=SimpleNamespace(total_memory=2**34)))
            stack.enter_context(patch.object(specialist, "Specialist", FakeSpecialist))
            train = stack.enter_context(patch.object(specialist, "train_model", side_effect=fake_train))
            stack.enter_context(patch.object(specialist, "predict", side_effect=fake_predict))
            head = stack.enter_context(patch.object(runner, "fit_head", return_value={"coefficients": [1., 0.]}))
            calibration = stack.enter_context(patch.object(runner, "fit_calibrator", return_value={"slope": 1., "intercept": 0.}))
            stack.enter_context(patch.object(study, "summarize_context", side_effect=small_analysis))
            with contextlib.redirect_stdout(io.StringIO()):
                with patch.object(runner.os, "getppid", return_value=-1):
                    with self.assertRaisesRegex(ValueError, "supervisor"):
                        runner.execute_phase(replay=False)
                runner.execute_phase(replay=False)
                self.assertEqual((head.call_count, train.call_count, calibration.call_count), (36, 12, 48))
                for mock in (head, train, calibration):
                    mock.side_effect = AssertionError("reconstruction must not fit")
                runner.execute_phase(replay=True)
            self.assertTrue(runner.read(root/"verification.json")["all12_contexts_reconstructed"])
            completion = runner.read(root/"worker_completion.json")
            self.assertEqual(sum(len(c["analysis"]["cases"]) for c in completion["contexts"]), 144)
            self.assertEqual(len(completion["aggregate"]), 36)
            self.assertTrue(all(item["equal_target_macro"]["FA"] == 0
                                and item["equal_target_macro"]["BFA"] == 1
                                for item in completion["aggregate"]))
            self.assertNotIn("usable_ids", json.dumps(completion))
            retained = root
            resumed = Path(directory)/"continued"
            resumed.mkdir()
            keys = [f"{c['target']}-{c['seed']}" for c in contexts]
            plan = {
                "limits": {**config["proposed_limits"],
                           "phase_seconds": {"heads": 600, "specialist": 5400,
                                             "prediction": 1800, "analysis": 600}},
                "initialization_reuse": {"path": str(retained/"initialization.pth"),
                                         "sha256": runner.digest(retained/"initialization.pth")},
                "continuation": {
                    "complete_contexts": {key: str(retained/"contexts"/key) for key in keys[:4]},
                    "checkpoint_contexts": {keys[4]: str(retained/"contexts"/keys[4]/"specialist.pth")},
                    "new_fit_starts": {"frozen": 24, "specialist": 7, "calibrator": 32}}}
            runner.write_immutable_record(resumed/"execution_plan.json", plan)
            runner.write_immutable_record(resumed/"attempt.json", {
                "supervisor_pid": os.getppid(), "plan_sha256": runner.digest(resumed/"execution_plan.json")})
            for mock in (head, train, calibration):
                mock.reset_mock()
                mock.side_effect = None
            train.side_effect = fake_train
            with patch.object(runner, "OUTPUT", resumed), \
                 patch.object(runner, "authority", return_value=(plan, {"limits": plan["limits"]})), \
                 contextlib.redirect_stdout(io.StringIO()):
                runner.execute_phase(replay=False)
                self.assertEqual((head.call_count, train.call_count, calibration.call_count), (24, 7, 32))
                for mock in (head, train, calibration):
                    mock.side_effect = AssertionError("continuation reconstruction must not fit")
                runner.execute_phase(replay=True)
            self.assertTrue(runner.read(resumed/"verification.json")["all12_contexts_reconstructed"])
            runner.frozen.check_reconstruction(
                runner.read(retained/"worker_completion.json")["aggregate"],
                runner.read(resumed/"worker_completion.json")["aggregate"])


if __name__ == "__main__":
    unittest.main()
