"""Conservative write races, bounded shutdown and non-traversing foreground checks."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import casia_budget289 as budget


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.controls = self.root / "control"
        self.binding = {"plan": "fixed"}
        budget.initialize(self.controls, self.binding)
        self.total = 100
        self.scan()
        self.client = budget.Client(self.controls, self.binding,
                                    lambda group: {"rss_bytes": 7, "temporary_bytes": 3}, lambda value: None)

    def scan(self):
        budget.scan_once([self.root], self.controls, self.binding, lambda root: self.total)

    def counted(self):
        return self.client.measure(os.getpgrp())["output_bytes"] - budget.CONTROL_RESERVE - 3

    def test_completed_write_remains_reserved_until_a_later_scan_starts(self):
        with self.client.reserve(40):
            self.assertEqual(self.counted(), 140)
            self.total += 40
        self.assertEqual(self.counted(), 140)
        self.scan()
        self.assertEqual(self.counted(), 140)

    def test_active_write_cannot_be_credited_by_an_in_progress_scan(self):
        with self.client.reserve(40):
            self.scan()
            self.total += 40
            self.assertEqual(self.counted(), 140)
        self.assertEqual(self.counted(), 140)
        self.scan()
        self.assertEqual(self.counted(), 140)

    def test_write_starting_during_scan_is_conservatively_added(self):
        entered, release = threading.Event(), threading.Event()

        def blocked(root):
            entered.set()
            if not release.wait(2):
                raise TimeoutError("test scanner not released")
            return 100

        thread = threading.Thread(target=budget.scan_once,
                                  args=([self.root], self.controls, self.binding, blocked))
        thread.start()
        self.assertTrue(entered.wait(1))
        try:
            with self.client.reserve(90):
                self.total += 90
            release.set()
            thread.join(2)
            self.assertFalse(thread.is_alive())
            self.assertEqual(self.counted(), 190)
        finally:
            release.set()
            thread.join(2)

    def test_nested_write_does_not_release_outer_reservation(self):
        with self.client.reserve(80):
            with self.client.reserve(20):
                self.total += 20
            state = budget.read_control(self.controls / "writes.json", self.binding)
            self.assertEqual(state["completed"], 0)
            self.scan()
            self.total += 80
            self.assertGreaterEqual(self.counted(), self.total)
        self.scan()
        self.assertEqual(self.counted(), self.total)

    def test_stale_failed_and_wrong_lease_are_fatal(self):
        path = self.controls / "snapshot.json"
        saved = budget.read_control(path, self.binding)
        budget.publish(path, {**saved, "scan_started": time.time() - budget.MAX_SNAPSHOT_AGE - 1})
        with self.assertRaisesRegex(budget.BudgetError, "stale"):
            self.counted()
        budget.publish(path, {"binding": self.binding, "error": "OSError: scan failed"})
        with self.assertRaisesRegex(budget.BudgetError, "scanner failed"):
            self.counted()
        budget.publish(path, {**saved, "binding": {"plan": "changed"}})
        with self.assertRaisesRegex(budget.BudgetError, "binding drift"):
            self.counted()

    def test_actual_scan_exception_is_published_and_propagated(self):
        with self.assertRaisesRegex(OSError, "unavailable"):
            budget.scan_forever([self.root], self.controls, self.binding,
                                Mock(side_effect=OSError("unavailable")))
        with self.assertRaisesRegex(budget.BudgetError, "scanner failed"):
            self.counted()

    def test_foreground_never_waits_for_tree_walk(self):
        walker = Mock(side_effect=AssertionError("foreground traversal"))
        self.client.measure(1)
        walker.assert_not_called()
        self.assertNotIn("tree_bytes", budget.Client.measure.__code__.co_names)

    def test_reservation_threshold_is_checked_before_writing(self):
        self.client.enforce = lambda value: (_ for _ in ()).throw(budget.BudgetError("storage cap"))
        with self.assertRaisesRegex(budget.BudgetError, "storage cap"):
            with self.client.reserve(100):
                self.fail("write must not start")

    def test_command_file_limit_and_shutdown_are_real(self):
        path = self.root / "large"
        command = budget.limited_command(
            [sys.executable, "-c", "import sys;open(sys.argv[1],'wb').write(b'x'*1000000)", str(path)], 4096)
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertLessEqual(path.stat().st_size, 4096)
        process = subprocess.Popen([sys.executable, "-c",
                                    "import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);print('ready',flush=True);time.sleep(60)"],
                                   stdout=subprocess.PIPE, text=True, start_new_session=True)
        try:
            self.assertEqual(process.stdout.readline().strip(), "ready")
            started = time.monotonic()
            budget.stop_group(process, timeout=0.15)
            self.assertLess(time.monotonic() - started, 0.6)
        finally:
            if process.poll() is None:
                budget.stop_group(process)
            process.stdout.close()


if __name__ == "__main__":
    unittest.main()
