"""Native canonical null roles project only through immutable assigned roles."""

import copy
import unittest

import test_msu_preprocessing as fixtures
from complete_msu282 import reconcile_frozen


class MsuLocalCompletionTest(unittest.TestCase):
    def test_native_null_role_projects_to_frozen_assignment_not_native_null(self):
        videos, roles = fixtures.MsuPackageTest().population()
        canonical = [dict(row, role=None) for row in videos]
        self.assertEqual(reconcile_frozen(videos, canonical, roles)["forbidden_subject_crossings"], 0)
        for mode in ("wrong_assigned_role", "wrong_canonical", "missing_field", "extra_field", "duplicate_canonical"):
            current, native = copy.deepcopy(videos), copy.deepcopy(canonical)
            if mode == "wrong_assigned_role":
                current[0]["role"] = "g_domain"
            elif mode == "wrong_canonical":
                native[0]["sensor_id"] = "wrong"
            elif mode == "missing_field":
                current[0].pop("sensor_id")
            elif mode == "extra_field":
                current[0]["unapproved"] = True
            else:
                native[-1] = native[0]
            with self.subTest(mode=mode), self.assertRaises((ValueError, KeyError)):
                reconcile_frozen(current, native, roles)


if __name__ == "__main__":
    unittest.main()
