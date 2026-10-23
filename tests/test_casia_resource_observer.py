import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

import casia_resource287 as resource
import handoff_casia287 as handoff


class ObserverTests(unittest.TestCase):
    def test_current_growth_is_fresh_and_historical_budget_never_decreases(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old, current = root / "old", root / "new"
            old.mkdir()
            current.mkdir()
            (old / "payload").write_bytes(b"a" * 17)
            monitor = resource.HistoricalStorage([old], current, current / "usage.json", {"lease": 1})
            monitor.scan()
            with patch.object(resource.probe.prior.shared, "usage", return_value={"rss_bytes": 9, "temporary_bytes": 3}):
                initial = monitor.measure(1)["output_bytes"]
                (current / "image").write_bytes(b"b" * 123)
                self.assertEqual(monitor.measure(1)["output_bytes"], initial + 123)
                (old / "payload").unlink()
                monitor.scan()
                self.assertEqual(json.loads(monitor.snapshot.read_text())["root_peak_bytes"][str(old)], 17)

    def test_stale_or_wrong_lease_cannot_return_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = root / "usage.json"
            resource.publish(snapshot, {"binding": {"lease": 1}, "root_peak_bytes": {},
                                        "completed_unix_seconds": time.time() - 31})
            with self.assertRaises(TimeoutError):
                resource.measured(1, root, snapshot, {"lease": 1})
            with self.assertRaises(ValueError):
                resource.measured(1, root, snapshot, {"lease": 2})

    def test_background_scan_error_is_fatal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            monitor = resource.HistoricalStorage([], root, root / "usage.json", {})
            monitor.scan()
            monitor.error = OSError("retained source unavailable")
            with self.assertRaisesRegex(RuntimeError, "scan failed"):
                monitor.measure(1)
            with self.assertRaisesRegex(RuntimeError, "scan failed"):
                monitor.close()

    def test_background_scan_refreshes_actual_historical_growth(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old, current = root / "old", root / "new"
            old.mkdir()
            current.mkdir()
            monitor = resource.HistoricalStorage([old], current, current / "usage.json", {}).start()
            try:
                (old / "payload").write_bytes(b"a" * 27)
                deadline = time.monotonic() + 2
                while json.loads(monitor.snapshot.read_text())["root_peak_bytes"][str(old)] != 27:
                    if time.monotonic() >= deadline:
                        self.fail("background scanner did not observe real historical growth")
                    time.sleep(0.02)
            finally:
                monitor.close()

    def test_current_root_cannot_also_be_historical(self):
        with self.assertRaises(ValueError):
            resource.HistoricalStorage([Path("/same")], Path("/same"), Path("/snapshot"), {})

    def test_holes_in_committed_prefix_cannot_skip_originals(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "transactions").mkdir()
            (root / "transactions/0001.json").write_text("{}")
            with patch.object(handoff, "OUTPUT", root), self.assertRaisesRegex(ValueError, "exact committed prefix"):
                handoff.committed_prefix({"videos": []})


if __name__ == "__main__":
    unittest.main()
