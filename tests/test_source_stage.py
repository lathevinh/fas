import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from fas.source_stage import join_prepared, pilot_inputs, population_counts, require_source_input, source_inputs
from fas.source_use import SourceUseContext
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import integrate_source295 as integration


class SourceStageTests(unittest.TestCase):
    def prepared(self, dataset="CASIA-FASD"):
        parent = {"dataset": dataset, "video_id": "synthetic", "binary_label": "attack",
                  "official_split": "test", "subject_id": "subject", "group_unit": "subject", "group_id": "subject"}
        role = {**parent, "role": "train"}
        image = {"video_id": "synthetic", "binary_label": "attack", "role": "train",
                 "active_config_sha256": "a" * 64, "retain_original_denominator": True,
                 "replacement": False, "model_score": None, "classifier_error": None,
                 "selected_frame": {"decode_order": 1, "eligible_frame_count": 4,
                                    "rgb_sha256": "b" * 64, "even_length_tie": "earlier_decoded_frame"},
                 "detector_status": "success", "final_k1_action": None, "asset_root": "/private",
                 "asset_sha256": {"crops/0000-224.png": "c" * 64, "crops/0000-518.png": "d" * 64}}
        return parent, role, image

    def join(self, values, **kwargs):
        parent, role, image = values
        return join_prepared(parent["dataset"], [parent], [role], [image],
                             active_config_sha256="a" * 64, **kwargs)[0]

    def test_frozen_non_siw_source_policy_does_not_reject_official_test(self):
        row = self.join(self.prepared())
        self.assertTrue(row["model_input_eligible"])
        self.assertFalse(row["score_fit_eligible"])
        require_source_input(row, outer_target="OULU-NPU", purpose="fitting", model_input=True)

    def test_technical_and_detector_failures_keep_denominators_not_model_inputs(self):
        rows = []
        for status in ("not_run", "failed"):
            values = self.prepared()
            image = values[2]
            image.update(detector_status=status, final_k1_action="non_accept", asset_sha256={})
            if status == "not_run":
                image["selected_frame"] = None
            row = self.join(values)
            rows.append(row)
            require_source_input(row, outer_target="OULU-NPU", purpose="fitting")
            with self.assertRaises(ValueError):
                require_source_input(row, outer_target="OULU-NPU", purpose="fitting", model_input=True)
        rows[1]["video_id"] = "another"
        counts = population_counts(rows)
        self.assertEqual((counts["source_use"], counts["model_input"], counts["source_use_failures"]), (2, 0, 2))
        self.assertEqual((counts["pre_detector_failure"], counts["detector_failure"]), (1, 1))

    def test_changed_role_config_frame_score_or_crop_is_rejected(self):
        for field, value in (("role", "g_domain"), ("active_config_sha256", "f" * 64),
                             ("model_score", 0.5), ("replacement", True), ("asset_sha256", {})):
            values = self.prepared()
            values[2][field] = value
            with self.assertRaises(ValueError):
                self.join(values)
        values = self.prepared()
        values[2]["selected_frame"]["decode_order"] = 2
        with self.assertRaises(ValueError):
            self.join(values)

    def test_outer_pseudo_target_and_role_routes_are_strict(self):
        row = self.join(self.prepared())
        for kwargs in ({"outer_target": "CASIA-FASD", "purpose": "fitting"},
                       {"outer_target": "OULU-NPU", "pseudo_target": "CASIA-FASD", "purpose": "fitting"},
                       {"outer_target": "OULU-NPU", "purpose": "calibration"},
                       {"outer_target": "OULU-NPU", "purpose": "domain_use"}):
            with self.assertRaises(ValueError):
                require_source_input(row, **kwargs)

    def test_siw_adopted_context_required_and_excluded_or_test_rows_rejected(self):
        for split, role, eligible in (("train", "train", True), ("train", "train", False), ("test", None, False)):
            parent, assigned, image = self.prepared("SiW-Mv2")
            parent.update(official_split=split, subject_id=None, group_unit="video", group_id="synthetic")
            assigned.update(official_split=split, subject_id="", role=role)
            image["role"] = role
            use = {**parent, "role": role, "source_use_eligible": eligible, "detector_status": "success"}
            context = SourceUseContext({"policy_id": "synthetic-binding"}, (use,))
            role_rows = [assigned] if role is not None else []
            with self.assertRaises(ValueError):
                join_prepared("SiW-Mv2", [parent], role_rows, [image], active_config_sha256="a" * 64)
            row = join_prepared("SiW-Mv2", [parent], role_rows, [image],
                                active_config_sha256="a" * 64, siw_context=context)[0]
            self.assertEqual(row["source_use_eligible"], eligible)
            if not eligible:
                with self.assertRaises(ValueError):
                    require_source_input(row, outer_target="OULU-NPU", purpose="fitting")
            else:
                row["source_use_binding"] = None
                with self.assertRaises(ValueError):
                    require_source_input(row, outer_target="OULU-NPU", purpose="fitting")

    def test_identity_collision_or_missing_original_cannot_disappear(self):
        parent, role, image = self.prepared()
        for images in ([], [image, image]):
            with self.assertRaises(ValueError):
                join_prepared(parent["dataset"], [parent], [role], images, active_config_sha256="a" * 64)

    def test_pilot_is_deterministic_source_only_successful_train_and_keeps_label_out_of_rank(self):
        rows = []
        for dataset in ("OULU-NPU", "CASIA-FASD", "MSU-MFSD", "SiW-Mv2"):
            base = self.join(self.prepared())
            for label in ("attack", "bona_fide"):
                for index in range(5):
                    rows.append({**copy.deepcopy(base), "dataset": dataset,
                                 "video_id": f"{label}-{index}", "binary_label": label,
                                 "source_use_binding": {"policy_id": "synthetic"}})
        before = copy.deepcopy(rows)
        pilot = pilot_inputs(rows)
        self.assertEqual(pilot, pilot_inputs(list(reversed(rows))))
        self.assertEqual(rows, before)
        self.assertEqual(len(pilot), 24)
        self.assertTrue(all(row["dataset"] != "OULU-NPU" and row["role"] == "train" for row in pilot))
        self.assertEqual(len(source_inputs(rows, outer_target="OULU-NPU", purpose="calibration")), 0)

    def test_accepted_legacy_omitted_error_field_requires_exact_historical_recipe(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            transaction = {"video_id": "synthetic", "role": "train", "binary_label": "attack",
                           "detector_status": "success", "selected_frame": {}, "model_score": None,
                           "replacement": False,
                           "config_sha256": "ae051c75b2b8e2ee82463be9f344e5312380fe9848c64d370e1a45fa7ae97283"}
            path = root / "fixture.json"
            payload = json.dumps(transaction).encode()
            path.write_bytes(payload)
            entry = {**transaction, "record_path": str(path),
                     "record_sha256": hashlib.sha256(payload).hexdigest(), "reused": True}
            with patch.object(integration, "BASE", root):
                integration.verify_record(entry, {})
                entry["reused"] = False
                with self.assertRaisesRegex(ValueError, "historical OULU"):
                    integration.verify_record(entry, {})
                entry["reused"] = True
                path.write_bytes(payload + b" ")
                with self.assertRaisesRegex(ValueError, "SHA256"):
                    integration.verify_record(entry, {})


if __name__ == "__main__":
    unittest.main()
