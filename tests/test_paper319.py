import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/diagnostics"))
import prepare_paper319 as run


def originals():
    rows = []
    for domain in run.DOMAINS:
        for split in (("train", "development", "test") if domain == "OULU-NPU" else ("train", "test")):
            for group in range(20):
                for label in ("bona_fide", "attack"):
                    for video in range(3):
                        key = f"{domain}:{split}:{group}:{label}:{video}"
                        rows.append({
                            "dataset": domain, "official_split": split,
                            "binary_label": label, "detector_status": "success",
                            "subject_id": None if domain == "SiW-Mv2" else f"{split}:{group}",
                            "group_id": f"{split}:{group}" if domain != "SiW-Mv2" else key,
                            "video_id": key, "source_use_eligible": split != "test" or domain != "SiW-Mv2",
                            "selected_frame": {"rgb_sha256": key},
                        })
    return rows


class PaperPreparationTests(unittest.TestCase):
    def test_exact_contexts_and_source_official_partitions(self):
        rows = originals()
        private, public = run.build_partitions(rows)
        indexed = {run.identity(row): row for row in rows}
        self.assertEqual(len(private["contexts"]), 12)
        self.assertEqual(public["context_count"], 12)
        for context in private["contexts"]:
            for role in ("fitting", "validation", "calibration"):
                self.assertTrue(all(indexed[key]["dataset"] != context["target"]
                                    and indexed[key]["official_split"] != "test" for key in context[role]))
            self.assertTrue(all(indexed[key]["dataset"] == context["target"]
                                and indexed[key]["official_split"] == "test"
                                for key in context["evaluation"]))

    def test_split_is_deterministic_order_independent_and_shared_across_training_seeds(self):
        rows = originals()
        first, _ = run.build_partitions(rows)
        second, _ = run.build_partitions(list(reversed(rows)))
        self.assertEqual(first, second)
        for start in range(0, 12, 3):
            for role in ("fitting", "validation", "calibration", "evaluation"):
                self.assertEqual(first["contexts"][start][role], first["contexts"][start + 2][role])

    def test_native_development_is_not_fitting_or_target(self):
        rows = originals()
        roles, _ = run.assign_roles(run.active_rows(rows))
        for row in rows:
            if row["dataset"] == "OULU-NPU":
                allowed = {"train": {"fitting"}, "development": {"validation", "calibration"},
                           "test": {"evaluation"}}[row["official_split"]]
                self.assertIn(roles[run.identity(row)], allowed)

    def test_failures_remain_original_denominators(self):
        rows = originals()
        row = rows[0]
        row["detector_status"] = "not_run"
        row["selected_frame"] = None
        _, public = run.build_partitions(rows)
        item = public["populations"]["OULU-NPU"]["fitting"]["bona_fide"]
        self.assertEqual(item["originals"], 60)
        self.assertEqual(item["usable"], 59)
        self.assertEqual(item["technical_failures"], 1)

    def test_siw_exclusions_preserved_but_null_role_test_retained(self):
        rows = originals()
        excluded = next(row for row in rows if row["dataset"] == "SiW-Mv2"
                        and row["official_split"] == "train")
        excluded["source_use_eligible"] = False
        private, public = run.build_partitions(rows)
        self.assertEqual(public["inherited_source_exclusions"], 1)
        for context in private["contexts"]:
            self.assertFalse(any(run.identity(excluded) in context[role]
                                 for role in ("fitting", "validation", "calibration", "evaluation")))
            if context["target"] == "SiW-Mv2":
                self.assertEqual(len(context["evaluation"]), 120)

    def test_unknown_siw_subjects_are_not_promoted_to_subject_independence(self):
        _, public = run.build_partitions(originals())
        self.assertFalse(public["subject_disjointness_verified_for_all_datasets"])
        self.assertGreater(public["unknown_subject_originals"]["SiW-Mv2"], 0)
        self.assertFalse(public["scientific_execution_authorized"])
        self.assertEqual(public["new_fits"], 0)

    def test_duplicate_identity_rejected(self):
        rows = originals()
        with self.assertRaisesRegex(ValueError, "unique"):
            run.build_partitions(rows + [copy.deepcopy(rows[0])])

    def test_cross_official_exact_frame_rejected(self):
        rows = originals()
        first = rows[0]
        other = next(row for row in rows if row["dataset"] == first["dataset"]
                     and row["official_split"] == "test")
        other["selected_frame"] = copy.deepcopy(first["selected_frame"])
        with self.assertRaisesRegex(ValueError, "boundary"):
            run.build_partitions(rows)

    def test_exact_frame_components_are_never_split(self):
        rows = originals()
        members = [row for row in rows if row["dataset"] == "CASIA-FASD"
                   and row["official_split"] == "train" and row["binary_label"] == "attack"]
        members[3]["selected_frame"] = copy.deepcopy(members[0]["selected_frame"])
        roles, mapping = run.assign_roles(run.active_rows(rows))
        keys = [run.identity(members[index]) for index in (0, 3)]
        self.assertEqual(mapping[keys[0]], mapping[keys[1]])
        self.assertEqual(roles[keys[0]], roles[keys[1]])

    def test_missing_known_subject_metadata_rejected(self):
        rows = originals()
        rows[0]["subject_id"] = None
        with self.assertRaisesRegex(ValueError, "subject metadata"):
            run.build_partitions(rows)

    def test_insufficient_class_support_rejected(self):
        rows = [row for row in originals() if not (
            row["dataset"] == "MSU-MFSD" and row["binary_label"] == "bona_fide")]
        with self.assertRaisesRegex(ValueError, "support"):
            run.build_partitions(rows)

    def test_preparation_does_not_fit_predict_or_load_features(self):
        with patch("fas.source_fitting.fit_head", side_effect=AssertionError("fit forbidden")), \
             patch("fas.source_fitting.fit_calibrator", side_effect=AssertionError("fit forbidden")), \
             patch("fas.source_fitting.head_logits", side_effect=AssertionError("prediction forbidden")), \
             patch("fas.feature_cache.load_shard", side_effect=AssertionError("feature arrays forbidden")):
            run.build_partitions(originals())


if __name__ == "__main__":
    unittest.main()
