import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(importlib.util.find_spec("torch") and importlib.util.find_spec("cv2"),
                     "integrated reconstruction tests require existing fas torch and OpenCV")
class PipelineTests(unittest.TestCase):
    def test_paired_augmentation_attention_losses_and_checkpoint_contract(self):
        if os.environ.get("PAPER329_TEST_CHILD") != "1":
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "test_paper329.PipelineTests", "-v"],
                cwd=ROOT/"tests", env={**os.environ, "PAPER329_TEST_CHILD": "1"},
                capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            return
        import numpy as np
        import torch
        sys.path.insert(0, str(ROOT/"scripts/paper329"))
        import assets
        from augmentation import FAMILIES, SPOOF, FASAug, paired_batch
        from model import attention_weights, losses
        from training import validate_state
        import training
        torch.set_num_threads(2)
        rgb = np.random.default_rng(329).integers(0, 256, (224, 224, 3), dtype=np.uint8)
        aug = FASAug.__new__(FASAug)
        aug.transforms = {}
        for i, family in enumerate(FAMILIES):
            if "ICC" in family and not (assets.DIRECTORY/"receipt.json").exists():
                continue
            with self.subTest(family=family):
                result, label, name = aug.apply(rgb, 0, np.random.default_rng(i), family)
                self.assertEqual(label, int(family in SPOOF))
                self.assertEqual(name, family)
                self.assertEqual(result.shape, rgb.shape)
                self.assertEqual(result.dtype, np.uint8)
        rows = [{"dataset": source, "binary_label": label}
                for source in ("A", "B", "C") for label in ("bona_fide", "attack")]
        load = lambda row: np.full((224, 224, 3), 80 if row["binary_label"] == "bona_fide" else 180, np.uint8)
        first = paired_batch(rows, load, aug, 7, 1, 0, fas_probability=0, pda_probability=1)
        torch.rand(100)
        second = paired_batch(rows, load, aug, 7, 1, 0, fas_probability=0, pda_probability=1)
        self.assertEqual(first.trace, second.trace)
        np.testing.assert_array_equal(first.images, second.images)
        self.assertEqual(first.patch_labels.shape, (32, 256))
        self.assertTrue((first.patch_labels[first.labels == 0] == 0).all())
        self.assertTrue((first.patch_labels[first.labels == 1] == 0).any())
        for i, donor in enumerate(first.trace["donors"]):
            if donor >= 0:
                self.assertEqual(rows[donor]["binary_label"], "bona_fide")
                self.assertEqual(rows[donor]["dataset"], rows[first.trace["selected"][i]]["dataset"])
                self.assertEqual(first.labels[i], 1)
        class Exhaust:
            calls = 0
            def apply(self, rgb, label, rng):
                self.calls += 1
                return rgb, 1, "reflection"
        exhausted = Exhaust()
        with self.assertRaisesRegex(RuntimeError, "after32 attempts"):
            paired_batch(rows, load, exhausted, 1, 1, 0, fas_probability=1)
        self.assertEqual(exhausted.calls, 32*32)
        with self.assertRaisesRegex(ValueError, "exhausted"):
            paired_batch(rows[1:], load, aug, 1, 1, 0)
        qkv = torch.randn(2, 261, 2304, requires_grad=True)
        weights = attention_weights(qkv)
        q, k, _ = qkv.detach().reshape(2, 261, 3, 12, 64).unbind(2)
        full = ((q.transpose(1, 2) @ k.transpose(1, 2).transpose(-1, -2))*.125).softmax(-1)
        expected = full[:, :, 0, 5:].mean(1)
        expected /= expected.sum(-1, keepdim=True)
        torch.testing.assert_close(weights, expected)
        self.assertEqual(weights.shape, (2, 256))
        self.assertFalse(weights.requires_grad)
        with self.assertRaises(ValueError):
            attention_weights(qkv[:, :-1])
        global_logits = torch.randn(6, 2, requires_grad=True)
        patch_logits = torch.randn(6, 256, 2, requires_grad=True)
        labels = torch.tensor([0, 1]*3)
        domains = torch.tensor([0, 0, 1, 1, 2, 2])
        patches = labels[:, None].repeat(1, 256)
        outputs = global_logits, patch_logits, torch.full((6, 256), 1/256)
        ordinary = losses(outputs, labels, domains, patches, tail=False)
        candidate = losses(outputs, labels, domains, patches, tail=True)
        torch.testing.assert_close(candidate["total"], ordinary["total"]+.1*ordinary["hardest_attack"])
        candidate["total"].backward()
        self.assertTrue(torch.isfinite(global_logits.grad).all())
        self.assertTrue(torch.isfinite(patch_logits.grad).all())
        state = {"history": [{"epoch": i+1, "validation": 1. if i == 0 else 2.} for i in range(21)],
                 "seed": 7, "tail": False, "optimizer_steps": 21, "selected_epoch": 1,
                 "validation_loss": 1.}
        validate_state(state, 32, 7, False)
        state["history"] = state["history"][:-1]
        state["optimizer_steps"] -= 1
        with self.assertRaisesRegex(ValueError, "shortened"):
            validate_state(state, 32, 7, False)
        class Toy(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.backbone = torch.nn.Module()
                block = torch.nn.Module()
                block.attn = torch.nn.Module()
                block.attn.qkv = torch.nn.Linear(3, 3)
                self.backbone.blocks = torch.nn.ModuleList([block])
                self.global_head = torch.nn.Linear(3, 2)
                self.patch_head = torch.nn.Linear(3, 2)
            def forward(self, images):
                features = self.backbone.blocks[0].attn.qkv(images.mean((2, 3)))
                return (self.global_head(features), self.patch_head(features)[:, None].expand(-1, 256, -1),
                        images.new_full((len(images), 256), 1/256))
        class IdentityAug:
            def apply(self, rgb, label, rng):
                return rgb, label, "none"
        with tempfile.TemporaryDirectory() as folder, patch.object(training, "validation_loss", return_value=1.):
            fitted = Toy()
            saved = training.fit(fitted, rows, rows, load, IdentityAug(), 7, True, "cpu", lambda: None,
                                 Path(folder)/"trace.jsonl")
            training.validate_state(saved, len(rows), 7, True)
            self.assertEqual(len(saved["history"]), 21)
            self.assertEqual(saved["selected_epoch"], 1)
            rebuilt = Toy()
            rebuilt.load_state_dict(saved["state_dict"])
            np.testing.assert_array_equal(training.predict(fitted, rows, load, "cpu", lambda: None),
                                          training.predict(rebuilt, rows, load, "cpu", lambda: None))
        import runner
        self.assertNotEqual(runner.prior.__file__, runner.__file__)
        with self.assertRaises(ValueError):
            runner.start("training", "undeclared", {"inventory": []})
        with tempfile.TemporaryDirectory() as folder:
            paths = [Path(folder)/f"{index}.jsonl" for index in range(2)]
            trace = json.dumps({"post_augmentation_counts": [[6, 6], [5, 5], [5, 5]], "redraws": 0})+"\n"
            for path in paths:
                path.write_text(trace)
            runner.verify_paired_traces(paths, [1, 1])
            with self.assertRaisesRegex(ValueError, "every declared optimizer"):
                runner.verify_paired_traces(paths, [2, 1])
            paths[1].write_text(trace.replace('"redraws": 0', '"redraws": 1'))
            with self.assertRaisesRegex(ValueError, "traces differ"):
                runner.verify_paired_traces(paths, [1, 1])
        with self.assertRaises(TimeoutError):
            runner.clock({"boot_id": "wrong_boot", "started_monotonic": 0})
        with tempfile.TemporaryDirectory() as folder, patch.object(runner, "OUTPUT", Path(folder)), \
                patch.object(runner, "clock"):
            (Path(folder)/"attempt.json").write_text(json.dumps({"supervisor_pid": 0}))
            orphan_guard = runner.guard_for({})
            with self.assertRaisesRegex(RuntimeError, "orphan worker"):
                orphan_guard()
        from analysis import ARMS, summarize
        import study
        import oracle316
        originals = [{"dataset": "OULU-NPU", "video_id": str(i), "group_id": str(i),
                      "subject_id": str(i//2), "selected_frame": {"rgb_sha256": f"{i:064x}"},
                      "binary_label": "attack" if i % 2 else "bona_fide",
                      "detector_status": "success" if i < 18 else "failed"} for i in range(20)]
        predictions = {ARMS[0]: np.linspace(.05, .95, 18).tolist(),
                       ARMS[1]: np.linspace(.02, .92, 18).tolist()}
        policies = {arm: {str(alpha): {"threshold": .5, "limiting_sources": ["A"],
                                      "sources": {"A": {"error_budget": 0}}}
                          for alpha in study.ALPHAS} for arm in ARMS}
        actual = summarize(predictions, originals, policies, lambda: None, repetitions=20)
        converted = {system: predictions[ARMS[int(system == "supervised_clip")]] for system in study.SYSTEMS}
        converted_policies = {system: policies[ARMS[int(system == "supervised_clip")]] for system in study.SYSTEMS}
        reference = study.summarize_context(converted, originals, converted_policies,
                                            oracle316.oracle, lambda: None, repetitions=20)
        self.assertAlmostEqual(actual["cases"][0]["policy"]["FA"], .4)
        self.assertAlmostEqual(actual["cases"][0]["policy"]["BFA"], .5)
        for got, expected in zip(actual["paired_minus_reference"],
                                 [item for item in reference["paired_minus_dino_reg"]
                                  if item["system"] == "supervised_clip"], strict=True):
            self.assertEqual(got["valid_repetitions"], expected["valid_repetitions"])
            np.testing.assert_allclose(got["percentile95"], expected["percentile95"], atol=1e-12, rtol=1e-12)
        class FailedChild:
            returncode = 9
            def poll(self):
                return self.returncode
        with tempfile.TemporaryDirectory() as folder, patch.object(runner, "OUTPUT", Path(folder)), \
                patch.object(runner, "authority", return_value=({}, {"started_monotonic": time.monotonic()})), \
                patch.object(runner.subprocess, "Popen", return_value=FailedChild()):
            self.assertEqual(runner.supervise(), 1)
            self.assertIn("stopped_no_retry", (Path(folder)/"terminal.json").read_text())
            with self.assertRaises(FileExistsError):
                runner.supervise()


class AuthorityTests(unittest.TestCase):
    def test_controller_rejects_unapproved_execution_and_undeclared_starts(self):
        result = subprocess.run(
            [sys.executable, str(ROOT/"scripts/paper329/runner.py"), "--approve",
             "--answer", "not_owner_approval", "--plan-sha256", "0"*64],
            capture_output=True, text=True, timeout=45)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("explicit exact-plan owner decision required", result.stderr)


if __name__ == "__main__":
    unittest.main()
