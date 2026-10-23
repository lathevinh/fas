import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import readback_siw291_blocked as blocked


class ExactCrossingTests(unittest.TestCase):
    def test_byte_and_decoded_pairs_are_not_double_counted_or_waived(self):
        rows = []
        for pair, strata in enumerate((
                (("train", "train"), ("train", "branch_calibration")),
                (("train", "train"), ("train", "g_domain")),
                (("test", None), ("train", "train")),
                (("test", None), ("train", "g_domain")),
                (("test", None), ("train", "train")),
                (("train", "train"), ("train", "train")))):
            for split, role in strata:
                rows.append({"video_id": f"synthetic_{len(rows)}", "official_split": split,
                             "role": role, "binary_label": "attack",
                             "media_sha256": str(pair) * 64, "decoded_rgb_sequence_sha256": str(pair + 1) * 64})
        groups = blocked.duplicate_groups(rows)
        result = blocked.summary(groups)
        self.assertEqual(result["duplicate_groups_by_kind"], {"media_sha256": 6, "decoded_rgb_sequence_sha256": 6})
        self.assertEqual(result["unique_duplicate_member_sets"], 6)
        self.assertEqual(result["unique_duplicated_originals"], 12)
        self.assertEqual(result["forbidden_unique_groups"], 5)
        self.assertEqual(result["official_train_test_crossing_groups"], 3)
        self.assertEqual(result["source_role_only_crossing_groups"], 2)
        self.assertEqual(result["within_one_partition_role_class_groups"], 1)
        self.assertFalse(result["local_audit_complete"])
        self.assertFalse(result["promotion_permitted"])
        self.assertTrue(all(g["participant_identity_verified"] is False for g in groups))

    def test_class_crossing_remains_forbidden_within_one_role(self):
        common = {"official_split": "train", "role": "train", "media_sha256": "a" * 64,
                  "decoded_rgb_sequence_sha256": "b" * 64}
        rows = [{**common, "video_id": "a", "binary_label": "attack"},
                {**common, "video_id": "b", "binary_label": "bona_fide"}]
        result = blocked.summary(blocked.duplicate_groups(rows))
        self.assertEqual(result["binary_label_crossing_groups"], 1)
        self.assertEqual(result["forbidden_unique_groups"], 1)

    def test_no_false_duplicate_for_distinct_saved_content(self):
        rows = [{"video_id": str(i), "role": None, "official_split": "test", "binary_label": "attack",
                 "media_sha256": str(i) * 64, "decoded_rgb_sequence_sha256": str(i + 3) * 64}
                for i in range(3)]
        self.assertEqual(blocked.duplicate_groups(rows), [])


if __name__ == "__main__":
    unittest.main()
