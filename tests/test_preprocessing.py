"""Focused deterministic preprocessing checks, without model or study media."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from fas.preprocessing import REFERENCE_112, align_face, alignment_matrix, shared_context_crop, decode_scrfd, detect_face


class FacePreprocessingTest(unittest.TestCase):
    def test_similarity_context_and_dimensions(self):
        angle = 0.3
        rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        landmarks = REFERENCE_112 @ rotation.T * 2.0 + np.array([50.0, 30.0])
        for resolution in (224, 518):
            matrix = alignment_matrix(landmarks, resolution)
            mapped = landmarks @ matrix[:, :2].T + matrix[:, 2]
            expected = (REFERENCE_112 / 112.0 - 0.5) * resolution / 1.30 + resolution / 2.0
            np.testing.assert_allclose(mapped, expected, atol=1e-10)
            image = np.full((300, 300, 3), (10, 30, 90), dtype=np.uint8)
            crop, repeated = align_face(image, landmarks, resolution)
            self.assertEqual(crop.shape, (resolution, resolution, 3))
            np.testing.assert_array_equal(repeated, matrix)
            np.testing.assert_array_equal(crop[resolution // 2, resolution // 2], [10, 30, 90])
            np.testing.assert_array_equal(crop, align_face(image, landmarks, resolution)[0])

    def test_invalid_landmarks_fail_closed(self):
        for points in (np.zeros((5, 2)), np.ones((4, 2)), np.full((5, 2), np.nan)):
            with self.assertRaises(ValueError):
                alignment_matrix(points, 224)
        with self.assertRaises(ValueError):
            alignment_matrix(REFERENCE_112, 224, 1.0)

    def test_shared_context_box_expansion_and_clipping(self):
        image = np.full((112, 112, 3), 90, dtype=np.uint8)
        crop, geometry = shared_context_crop(image, np.array([10, 10, 110, 110]), REFERENCE_112)
        self.assertEqual(geometry["crop_xyxy_half_open"], [0, 0, 112, 112])
        self.assertEqual(crop.shape, image.shape)
        np.testing.assert_allclose(np.asarray(geometry["alignment_matrix"])[:, :2], np.eye(2), atol=1e-12)
        with self.assertRaises(ValueError):
            shared_context_crop(image, np.array([30, 30, 20, 20]), REFERENCE_112)

    def test_scrfd_decode_threshold_nms_and_no_face(self):
        outputs = [np.zeros((count, dimensions), dtype=np.float32)
                   for dimensions in (1, 4, 10) for count in (12800, 3200, 800)]
        outputs[0][:2] = 0.9
        outputs[3][:2] = 1
        boxes, points = decode_scrfd(outputs, 0.5)
        self.assertEqual(boxes.shape, (1, 5))
        self.assertEqual(points.shape, (1, 5, 2))
        np.testing.assert_array_equal(boxes[0, :4], [-16, -16, 16, 16])
        outputs[0][:] = 0
        self.assertEqual(decode_scrfd(outputs, 1)[0].shape, (0, 5))

        class Session:
            def get_inputs(self):
                return [type("Input", (), {"name": "input"})()]

            def run(self, names, inputs):
                self.blob = inputs["input"]
                return outputs

        session = Session()
        with self.assertRaisesRegex(ValueError, "no_face"):
            detect_face(session, np.full((640, 640, 3), [0, 127, 255], dtype=np.uint8))
        np.testing.assert_allclose(session.blob[0, :, 0, 0], (np.array([0, 127, 255]) - 127.5) / 128)
        outputs[0][0] = np.nan
        with self.assertRaises(ValueError):
            decode_scrfd(outputs, 1)

    def test_source_selection_is_balanced_fixed_and_never_replaces_failure(self):
        from preprocess_oulu274 import selection

        rows = [{"video_id": f"{label}-{index}", "role": "train", "binary_label": label,
                 "selected_frame": None if index == 0 else {"decode_order": 10}}
                for label in ("bona_fide", "attack") for index in range(20)]
        rows.extend({"video_id": f"target-{index}", "role": "g_domain", "binary_label": "attack"} for index in range(20))
        selected = selection(rows)
        self.assertEqual(len(selected), 32)
        self.assertEqual(sum(row["binary_label"] == "bona_fide" for row in selected), 16)
        self.assertTrue(all(row["role"] == "train" for row in selected))
        self.assertEqual(selected, selection(list(reversed(rows))))
        failed = [dict(row, selected_frame=None) for row in rows]
        self.assertEqual([row["video_id"] for row in selected], [row["video_id"] for row in selection(failed)])
        with self.assertRaises(ValueError):
            selection(rows + [rows[0]])
        with self.assertRaises(ValueError):
            selection(rows[:10])

    def test_recorded_archive_blocker_stops_before_any_media_or_model(self):
        import preprocess_oulu274 as pilot

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            with patch.object(pilot, "OUTPUT", output), patch.object(pilot, "read_json", side_effect=AssertionError("must not read parents")):
                with patch.object(Path, "exists", return_value=True):
                    with self.assertRaisesRegex(ValueError, "recorded archive identity blocker"):
                        pilot.make_plan()