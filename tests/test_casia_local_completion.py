"""Exact CASIA canonical-role projection without native-field or ID drift."""

import copy
import unittest

import test_casia_preprocessing as fixtures
from complete_casia287 import partial_ledger, reconcile_frozen


class CasiaLocalCompletionTest(unittest.TestCase):
    def test_partial_ledger_distinguishes_interrupted_from_never_started(self):
        videos, _, _ = fixtures.CasiaPreprocessingTest().population()
        attempts = {index: {"index": index, "video_id": videos[index]["video_id"], "role": videos[index]["role"]}
                    for index in (0, 1)}
        rows = partial_ledger(videos, {0: attempts[0]}, attempts)
        self.assertEqual(len(rows), 600)
        self.assertEqual(rows[0]["execution_status"], "committed_provisional")
        self.assertEqual(rows[1]["execution_status"], "interrupted_before_commit")
        self.assertEqual(rows[2]["execution_status"], "not_attempted_after_deadline")
        self.assertTrue(all(row["final_k1_action"] == "non_accept" and not row["package_accepted"] for row in rows))

    def test_partial_ledger_rejects_missing_attempt_or_changed_role(self):
        videos, _, _ = fixtures.CasiaPreprocessingTest().population()
        row = {"index": 0, "video_id": videos[0]["video_id"], "role": videos[0]["role"]}
        with self.assertRaises(ValueError):
            partial_ledger(videos, {0: row}, {})
        with self.assertRaises(ValueError):
            partial_ledger(videos, {}, {0: {**row, "role": "unapproved"}})

    def test_only_frozen_assigned_roles_may_overlay_exact600_native_rows(self):
        videos, roles, _ = fixtures.CasiaPreprocessingTest().population()
        native = [dict(row, role=None) for row in videos]
        self.assertEqual(reconcile_frozen(videos, native, roles)["subjects"], 50)
        for mode in ("assigned_role", "native_field", "missing", "extra", "duplicate"):
            planned, canonical = copy.deepcopy(videos), copy.deepcopy(native)
            if mode == "assigned_role":
                planned[0]["role"] = "g_domain"
            elif mode == "native_field":
                canonical[0]["quality"] = "different"
            elif mode == "missing":
                planned[0].pop("sensor_id")
            elif mode == "extra":
                planned[0]["unapproved"] = True
            else:
                canonical[-1] = canonical[0]
            with self.subTest(mode=mode), self.assertRaises((ValueError, KeyError)):
                reconcile_frozen(planned, canonical, roles)
