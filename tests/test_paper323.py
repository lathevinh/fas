import json
import os
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/paper321"))
import continuation
import runner


class ContinuationTests(unittest.TestCase):
    def test_phase_clocks_are_independent_and_unknown_phase_rejected(self):
        approval = {
            "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
            "started_monotonic": time.monotonic(),
            "limits": {"wall_seconds_total": 86400, "work_cutoff_seconds": 79200,
                       "phase_seconds": {"heads": 600, "specialist": 5400, "prediction": 1800,
                                         "analysis": 600}}}
        runner.clock(approval, context_started=time.monotonic()-2401, phase="specialist")
        for phase in approval["limits"]["phase_seconds"]:
            with self.subTest(phase=phase), self.assertRaises(TimeoutError):
                runner.clock(approval, context_started=time.monotonic()-approval["limits"]["phase_seconds"][phase]-1,
                             phase=phase)
        with self.assertRaisesRegex(ValueError, "declared"):
            runner.clock(approval, context_started=time.monotonic(), phase="worker")
        approval["started_monotonic"] -= 80000
        with self.assertRaises(TimeoutError):
            runner.clock(approval)
        runner.clock(approval, final=True)

    def test_fresh_explicit_approval_is_immutable_and_does_not_read_old_clock(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runner.write_immutable_record(root/"execution_plan.json", {})
            with patch.object(continuation, "OUTPUT", root), \
                 patch.object(runner, "check_plan", return_value={"limits": {"wall_seconds_total": 86400}}):
                with self.assertRaisesRegex(ValueError, "explicit"):
                    continuation.approve("old_approval")
                before = time.monotonic()
                continuation.approve(continuation.ANSWER)
                approval = runner.read(root/"owner_approval.json")
                self.assertGreaterEqual(approval["started_monotonic"], before)
                self.assertFalse(approval["automatic_retry"])
                with self.assertRaises(FileExistsError):
                    continuation.approve(continuation.ANSWER)

    def test_recovery_inventory_binds_checkpoints_and_rejects_drift(self):
        keys = [("OULU-NPU", seed) for seed in (20260917, 20260923, 20261001)]
        keys += [("CASIA-FASD", seed) for seed in (20260917, 20260923)]
        contexts = [{"target": domain, "seed": seed, "fitting": ["f"], "evaluation": ["e"]}
                    for domain, seed in keys]
        indexed = {"f": {"detector_status": "success"}, "e": {"detector_status": "success"}}
        states = {}
        fake_torch = SimpleNamespace(load=lambda path, **kwargs: states[str(path)], isfinite=np.isfinite)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for i, context in enumerate(contexts):
                key = f"{context['target']}-{context['seed']}"
                folder = root/"contexts"/key
                folder.mkdir(parents=True)
                checkpoint = folder/"specialist.pth"
                checkpoint.write_bytes(b"synthetic-checkpoint")
                states[str(checkpoint)] = {
                    "history": [.5]*50, "selected_epoch": 1, "validation_loss": .5,
                    "seed": context["seed"], "optimizer_steps": 50, "state_dict": {"weight": np.ones(1)}}
                if i < 4:
                    runner.write_immutable_record(folder/"models.json", {
                        "specialist_sha256": runner.digest(checkpoint), "specialist_selected_epoch": 1,
                        "specialist_optimizer_steps": 50})
                    runner.write_immutable_record(folder/"prediction_analysis.json", {
                        "target": context["target"], "seed": context["seed"], "usable_ids": ["e"]})
                for kind, names in (("specialist", [key]),
                                    ("frozen", [f"{key}-{branch}" for branch in runner.BRANCHES[:3]]),
                                    ("calibrator", [f"{key}-{branch}" for branch in runner.BRANCHES])):
                    for name in names:
                        runner.write_immutable_record(root/"starts"/f"{kind}-{name}.json",
                                                      {"kind": kind, "key": name})
            with patch.object(continuation, "PARENT", root), patch.dict(sys.modules, {"torch": fake_torch}):
                files = {}
                inventory = continuation.recovery_inventory(contexts, indexed, files)
                self.assertEqual(len(inventory["complete_contexts"]), 4)
                self.assertEqual(len(inventory["checkpoint_contexts"]), 1)
                self.assertEqual(inventory["new_fit_starts"], {"frozen": 24, "specialist": 7, "calibrator": 32})
                self.assertEqual(len(files), 53)
                states[str(checkpoint)]["history"] = [.5]*49
                with self.assertRaisesRegex(ValueError, "checkpoint"):
                    continuation.recovery_inventory(contexts, indexed, {})
                states[str(checkpoint)]["history"] = [.5]*50
                (root/"starts"/"unexpected.json").write_text(json.dumps({}))
                with self.assertRaisesRegex(ValueError, "inventory"):
                    continuation.recovery_inventory(contexts, indexed, {})


if __name__ == "__main__":
    unittest.main()
