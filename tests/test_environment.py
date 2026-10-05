from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.environment import REQUIRED_PACKAGES, check_environment, verify_source_checkout


class EnvironmentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.lock = self.root / "requirements.lock"
        self.lock.write_text("synthetic-lock-fixture\n", encoding="utf-8")
        self.packages = {name: "1.2.3" for name in REQUIRED_PACKAGES}
        self.config = {
            "version": 1,
            "status": "locked",
            "python_requires": ">=3.11,<3.13",
            "platform": "linux_x86_64",
            "packages": dict(self.packages),
            "lockfile": "requirements.lock",
            "lockfile_sha256": hashlib.sha256(self.lock.read_bytes()).hexdigest(),
        }

    def check(self, version: tuple[int, int, int] = (3, 12, 0)) -> dict:
        return check_environment(
            self.root, self.config, python_version=version,
            runtime_platform="linux_x86_64", installed_packages=self.packages,
        )

    def test_matching_synthetic_environment_is_ready(self) -> None:
        self.assertEqual(self.check()["status"], "ready")

    def test_source_checkout_requires_exact_clean_commit(self) -> None:
        with patch("fas.environment.subprocess.check_output", side_effect=["a" * 40, ""]):
            self.assertEqual(verify_source_checkout(self.root, "a" * 40)["status"], "clean")
        for commit, status in (("b" * 40, ""), ("a" * 40, " M model.py")):
            with self.subTest(commit=commit, status=status), patch("fas.environment.subprocess.check_output", side_effect=[commit, status]):
                with self.assertRaises(ValueError):
                    verify_source_checkout(self.root, "a" * 40)
        with self.assertRaises(ValueError):
            verify_source_checkout(self.root, "main")

    def test_python_boundaries(self) -> None:
        for version, expected in (((3, 10, 9), "blocked"), ((3, 11, 0), "ready"), ((3, 12, 9), "ready"), ((3, 13, 0), "blocked")):
            with self.subTest(version=version):
                self.assertEqual(self.check(version)["status"], expected)

    def test_pending_config_stays_blocked(self) -> None:
        self.config["status"] = "pending_model_stack_lock"
        result = self.check()
        self.assertEqual(result["status"], "blocked")

    def test_changed_or_missing_lock_is_blocked(self) -> None:
        self.lock.write_text("modified\n", encoding="utf-8")
        self.assertEqual(self.check()["status"], "blocked")
        self.lock.unlink()
        self.assertEqual(self.check()["status"], "blocked")

    def test_outside_repository_lock_is_blocked(self) -> None:
        self.config["lockfile"] = "../outside.lock"
        self.assertEqual(self.check()["status"], "blocked")
        self.config["lockfile"] = str(self.lock)
        self.assertEqual(self.check()["status"], "blocked")

    def test_missing_or_changed_package_is_blocked(self) -> None:
        self.packages["torch"] = None
        self.assertEqual(self.check()["status"], "blocked")
        self.packages["torch"] = "1.2.4"
        self.assertEqual(self.check()["status"], "blocked")

    def test_unpinned_or_omitted_package_is_blocked(self) -> None:
        self.config["packages"]["torch"] = ">=1.2.3"
        self.assertEqual(self.check()["status"], "blocked")
        del self.config["packages"]["torch"]
        self.assertEqual(self.check()["status"], "blocked")

    def test_wrong_platform_or_schema_is_blocked(self) -> None:
        self.config["platform"] = "win32_AMD64"
        self.assertEqual(self.check()["status"], "blocked")
        self.config["platform"] = "linux_x86_64"
        self.config["version"] = 2
        self.assertEqual(self.check()["status"], "blocked")

    def test_malformed_python_requirement_is_blocked(self) -> None:
        self.config["python_requires"] = "any"
        self.assertEqual(self.check()["status"], "blocked")

    def test_cli_reports_current_blockers_without_writing(self) -> None:
        config_path = self._pending_config()
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/check_environment.py"), "--config", str(config_path)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "blocked")

    def test_cli_writes_immutable_report_and_refuses_overwrite(self) -> None:
        output = self.root / "report.json"
        config_path = self._pending_config()
        command = [sys.executable, str(ROOT / "scripts/check_environment.py"), "--config", str(config_path), "--out", str(output)]
        first = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(first.returncode, 1)
        original = output.read_bytes()
        self.assertEqual(json.loads(original)["status"], "blocked")
        second = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(second.returncode, 2)
        self.assertEqual(output.read_bytes(), original)

    def _pending_config(self) -> Path:
        path = self.root / "pending.json"
        path.write_text(json.dumps({"version": 1, "status": "pending_model_stack_lock"}), encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()