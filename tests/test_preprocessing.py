"""Focused deterministic preprocessing checks, without model or study media."""

import hashlib
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

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

    def test_supervisor_rejects_worker_zero_without_completion(self):
        import preprocess_oulu274 as pilot

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            started = time.time()
            plan = {"deadline_unix_seconds": started + 60, "videos": []}
            pilot.write_immutable_record(output / "plan.json", plan)
            pilot.write_immutable_record(output / "owner_approval.json", {"started_unix_seconds": started})
            process = Mock(pid=424242)
            process.wait.return_value = 0
            usage = {"rss_bytes": 100, "output_bytes": 100, "temporary_bytes": 0}
            with patch.object(pilot, "OUTPUT", output), patch.object(pilot, "make_plan", return_value=plan), \
                    patch.object(pilot.subprocess, "Popen", return_value=process), \
                    patch.object(pilot, "measured_usage", return_value=usage), patch.object(pilot.os, "killpg"):
                with self.assertRaisesRegex(RuntimeError, "pilot attempt failed"):
                    pilot.supervise()
            self.assertFalse(pilot.read_json(output / "resources.json")["completion_claimed"])

    def completion_fixture(self, output, pilot):
        import cv2
        from fas.visual import png_bytes

        model = b"synthetic model fixture, never executable"
        (output / "det_10g.onnx").write_bytes(model)
        model_sha = hashlib.sha256(model).hexdigest()
        config_path = str(ROOT / "configs/preprocessing_pilot_v1.yaml")
        config_sha = pilot._sha256(Path(config_path))
        plan = {"videos": [], "sources": {config_path: config_sha}, "model_sha256": model_sha,
                "deadline_unix_seconds": time.time() + 60}
        image = np.full((112, 112, 3), (30, 70, 90), dtype=np.uint8)
        crop, geometry = shared_context_crop(image, np.array([10, 10, 110, 110]), REFERENCE_112)
        sheet = np.full((8 * 180, 4 * 160, 3), 255, dtype=np.uint8)
        for index in range(32):
            media_path = output / f"media-{index:02d}.json"
            pilot.write_immutable_record(media_path, {"media_sha256": "f" * 64, "frame_count": 1, "byte_size": 10})
            transaction = {"video_id": f"fixture-{index:02d}", "role": "train",
                           "binary_label": "bona_fide" if index < 16 else "attack",
                           "selected_frame": {"height": 112, "width": 112, "decode_order": 0, "rgb_sha256": hashlib.sha256(image.tobytes()).hexdigest()},
                           "media_record_sha256": pilot._sha256(media_path), "media_sha256": "f" * 64}
            plan["videos"].append({"transaction": transaction, "media_path": str(media_path)})
            plan["sources"][str(media_path)] = transaction["media_record_sha256"]
            row = {**transaction, "index": index, "model_sha256": model_sha, "config_sha256": config_sha,
                   "retain_original_denominator": True, "replacement": False, "model_score": None}
            tile = np.zeros((224, 224, 3), dtype=np.uint8)
            frame_path = output / "frames" / f"{index:02d}.png"
            frame_path.parent.mkdir(exist_ok=True)
            frame_path.write_bytes(png_bytes(image))
            row.update(selected_RGB_asset={"path": f"frames/{index:02d}.png", "sha256": pilot._sha256(frame_path)})
            if index == 31:
                row.update({"detector_status": "failed", "final_k1_action": "non_accept", "failure": "no_face_above_frozen_threshold"})
            else:
                row.update({"detector_status": "success", "face_box_xyxy": [10, 10, 110, 110], "detector_confidence": 0.9,
                            "landmarks": REFERENCE_112.tolist(), "geometry": geometry, "crop_shape": list(crop.shape),
                            "crop_RGB_sha256": hashlib.sha256(crop.tobytes()).hexdigest(), "assets": {}})
                for name in ("shared", "224", "518"):
                    resized = crop if name == "shared" else cv2.resize(crop, (int(name), int(name)), interpolation=cv2.INTER_CUBIC)
                    relative = f"crops/{index:02d}-{name}.png"
                    path = output / relative
                    path.parent.mkdir(exist_ok=True)
                    path.write_bytes(png_bytes(resized))
                    row["assets"][relative] = {"sha256": pilot._sha256(path), "RGB_sha256": hashlib.sha256(resized.tobytes()).hexdigest(), "shape": list(resized.shape)}
                    if name == "224":
                        tile = resized
            pilot.write_immutable_record(output / "transactions" / f"{index:02d}.json", row)
            top, left = index // 4 * 180, index % 4 * 160
            cv2.putText(sheet, f"{index:02d}", (left + 3, top + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
            sheet[top + 20:top + 180, left:left + 160] = cv2.resize(tile, (160, 160), interpolation=cv2.INTER_CUBIC)
        (output / "contact_sheet.png").write_bytes(png_bytes(sheet))
        pilot.write_immutable_record(output / "worker_completion.json", {
            "transactions": 32, "detector_success": 31, "detector_failure": 1, "verified_native_frames": 32,
            "selected_payload_bytes": 320, "gpu_seconds": 0, "provider": ["CPUExecutionProvider"],
            "archive_guard_before_after_equal": True, "original_population": 4950, "selected_population": 4949,
            "retained_preexisting_failure": 1, "calibration_original": 990, "calibration_frame_available": 989,
            "calibration_score_fit": 0, "scientific_readiness": False})
        pilot.write_immutable_record(output / "plan.json", plan)
        pilot.write_immutable_record(output / "owner_approval.json", {"started_unix_seconds": time.time()})
        return plan, model_sha

    def test_completion_exact_success_and_rejects_partial_corrupt_or_mismatched_outputs(self):
        import preprocess_oulu274 as pilot

        for mode in ("success", "missing_row", "corrupt_crop", "wrong_parent", "wrong_counts", "failed_row_accept", "geometry", "sheet"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                plan, model_sha = self.completion_fixture(output, pilot)
                row_path = output / "transactions" / ("31.json" if mode == "failed_row_accept" else "00.json")
                row = pilot.read_json(row_path)
                if mode == "missing_row":
                    row_path.unlink()
                elif mode == "corrupt_crop":
                    (output / "crops/00-224.png").write_bytes(b"corrupt PNG fixture")
                elif mode == "sheet":
                    (output / "contact_sheet.png").write_bytes((output / "crops/00-224.png").read_bytes())
                elif mode == "wrong_counts":
                    path = output / "worker_completion.json"
                    value = pilot.read_json(path)
                    value["detector_success"] = 32
                    path.write_text(json.dumps(value))
                elif mode in {"wrong_parent", "failed_row_accept", "geometry"}:
                    if mode == "wrong_parent":
                        row["selected_frame"] = dict(row["selected_frame"], decode_order=1)
                    elif mode == "failed_row_accept":
                        row["final_k1_action"] = "accept"
                    else:
                        row["geometry"]["crop_xyxy_half_open"][0] = 1
                    row_path.write_text(json.dumps(row))
                with patch.object(pilot, "OUTPUT", output), patch.object(pilot, "MODEL_SHA", model_sha):
                    if mode == "success":
                        readback = pilot.validate_completion(plan)
                        self.assertEqual(readback["transactions"], 32)
                        self.assertEqual(readback["detector_success"], 31)
                        self.assertEqual(readback["detector_failure"], 1)
                        self.assertFalse(readback["sheet_inspected"])
                    else:
                        with self.assertRaises((ValueError, FileNotFoundError)):
                            pilot.validate_completion(plan)

    def test_supervisor_final_caps_and_partial_rows(self):
        import preprocess_oulu274 as pilot

        for mode in ("success", "missing_completion", "final_storage_cap", "final_rss_cap", "final_deadline", "spawn_failure"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                plan, model_sha = self.completion_fixture(output, pilot)
                if mode == "missing_completion":
                    (output / "worker_completion.json").unlink()
                process = Mock(pid=424242)
                process.wait.return_value = 0
                usage = {"rss_bytes": 100, "output_bytes": 100, "temporary_bytes": 0}
                final = dict(usage)
                if mode == "final_storage_cap":
                    final["output_bytes"] = pilot.CAPS["output_bytes"] + 1
                if mode == "final_rss_cap":
                    final["rss_bytes"] = pilot.CAPS["rss_bytes"] + 1
                original = pilot.validate_completion

                def validate(value):
                    result = original(value)
                    if mode == "final_deadline":
                        plan["deadline_unix_seconds"] = time.time() - 1
                    return result

                with patch.object(pilot, "OUTPUT", output), patch.object(pilot, "MODEL_SHA", model_sha), \
                        patch.object(pilot, "make_plan", return_value=plan), patch.object(pilot.subprocess, "Popen", return_value=process, side_effect=OSError("synthetic spawn error") if mode == "spawn_failure" else None), \
                        patch.object(pilot, "measured_usage", side_effect=[dict(usage), dict(final)]), \
                        patch.object(pilot, "validate_completion", side_effect=validate), patch.object(pilot.os, "killpg"):
                    if mode == "success":
                        self.assertTrue(pilot.supervise()["completion_claimed"])
                    else:
                        with self.assertRaisesRegex(RuntimeError, "pilot attempt failed"):
                            pilot.supervise()
                resources = pilot.read_json(output / "resources.json")
                self.assertEqual(resources["completion_claimed"], mode == "success")
                if mode != "success":
                    rows = list((output / "failure_rows").glob("*.json"))
                    self.assertEqual(len(rows), 32)
                    self.assertTrue(all(pilot.read_json(path)["final_k1_action"] == "non_accept" for path in rows))

    def test_recovery_single_pass_equality_or_no_binding(self):
        import recover_oulu276 as recovery

        for mode in ("success", "mismatch", "rss_cap", "deadline"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                package, archives = root / "package", root / "archives"
                archives.mkdir()
                anchors, sizes, rows = {}, {}, {}
                for name in ("Dev_files.tar", "Test_files.tar", "Train_files.tar"):
                    payload = (name * 100).encode()
                    (archives / name).write_bytes(payload)
                    anchors[name], sizes[name] = hashlib.sha256(payload).hexdigest(), len(payload)
                    identity = recovery.file_identity((archives / name).stat())
                    rows[name] = {"current_file_identity": dict(identity, device=identity["device"] - 1)}
                old_path = root / "accepted219.json"
                recovery.write_immutable_record(old_path, {"archives": rows})
                recovery.write_immutable_record(package / "owner_approval.json", {"fixture": True})
                guard = {"accepted219_binding_path": str(old_path)}
                parent = {"paths": {"input_root": str(archives), "archive_records": str(root)}}
                caps = {"wall_seconds": -1 if mode == "deadline" else 60, "rss_bytes": 1 if mode == "rss_cap" else 1024 ** 3,
                        "output_bytes": 16 * 1024 ** 2, "archive_bytes": sum(sizes.values())}
                if mode == "mismatch":
                    anchors["Dev_files.tar"] = "0" * 64
                with patch.object(recovery, "PACKAGE", package), patch.object(recovery, "ANCHORS", anchors), \
                        patch.object(recovery, "ARCHIVE_SIZES", sizes), patch.object(recovery, "RECOVERY_CAPS", caps), \
                        patch.object(recovery, "approval"), patch.object(recovery, "inherited_guard"), \
                        patch.object(recovery, "context", return_value=(parent, guard)):
                    if mode == "success":
                        result = recovery.recover()
                        self.assertEqual(result["bytes_read"], sum(sizes.values()))
                        binding_path = package / "recovery/binding.json"
                        identities = recovery.recovered_identities(archives, root, guard, binding_path, recovery._sha256(binding_path))
                        self.assertEqual(len(identities), 3)
                        import preprocess_oulu274 as pilot
                        import verify_oulu_archive_guard_batch09 as historical

                        plan = {"paths": parent["paths"], "guard_context": guard,
                            "recovery_binding_path": str(binding_path), "recovery_binding_sha256": recovery._sha256(binding_path)}
                        with patch.object(historical, "verified_guard_authority", return_value={"private_binding_sha256": recovery._sha256(old_path)}), \
                            patch.object(historical, "verified_archive_identities", side_effect=AssertionError("no history replay")):
                            self.assertEqual(pilot.archive_guard(plan), identities)
                        with self.assertRaises(FileExistsError):
                            recovery.recover()
                    else:
                        with self.assertRaises((ValueError, TimeoutError)):
                            recovery.recover()
                        self.assertFalse((package / "recovery/binding.json").exists())