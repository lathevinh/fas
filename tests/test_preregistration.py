from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.preregistration import artifact_hashes, validate


class PreregistrationTest(unittest.TestCase):
    def test_frozen_config_schema_is_valid(self) -> None:
        self.assertEqual(validate(ROOT, require_counts=False), [])

    def test_readiness_is_blocked_until_real_counts_are_audited(self) -> None:
        errors = validate(ROOT, require_counts=True)
        self.assertTrue(any("unaudited datasets" in error for error in errors))

    def test_all_frozen_artifacts_have_hashes(self) -> None:
        hashes = artifact_hashes(ROOT)
        self.assertEqual(len(hashes), 9)
        self.assertTrue(all(len(digest) == 64 for digest in hashes.values()))


if __name__ == "__main__":
    unittest.main()
