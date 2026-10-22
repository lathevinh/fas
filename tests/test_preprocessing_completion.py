"""Synthetic role-isolation, active-pin and full-denominator completion checks."""

import copy
import hashlib
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import preprocess_oulu280 as job
from fas.preprocessing import REFERENCE_112, shared_context_crop
from fas.preprocessing_policy import validate_active_preprocessing, validate_legacy_equivalence


class PreprocessingCompletionTest(unittest.TestCase):
    def population(self):
        rows = []
        for role, count in job.ROLE_COUNTS.items():
            for index in range(count):
                failed = role == "branch_calibration" and index == 0
                rows.append({
                    "video_id": f"{role}_{index:04d}", "role": role,
                    "binary_label": "bona_fide" if index % 5 == 0 else "attack",
                    "selected_frame": None if failed else {"decode_order": 1},
                    "detector_status": "not_run", "model_score": None, "classifier_error": None,
                    "final_k1_action": "non_accept" if failed else None,
                    "retain_original_denominator": True})
        return rows

    def test_active_pin_matches_accepted_recipe_without_rewriting_historical_configs(self):
        active, pilot = job.read_json(job.ACTIVE), job.read_json(job.LEGACY)
        validate_active_preprocessing(active)
        validate_legacy_equivalence(active, pilot)
        self.assertIsNone(job.read_json(ROOT / "configs/preprocessing_v2.yaml")["face"]["detector_weight_sha256"])
        self.assertEqual(job.read_json(ROOT / "configs/experiment_core_v1.yaml")["preprocessing_spec"], "preprocessing_v3.yaml")
        for key in ("score_threshold", "primary_face", "threads"):
            changed = copy.deepcopy(active)
            changed["detector_parameters"][key] = "changed"
            with self.assertRaises(ValueError):
                validate_active_preprocessing(changed)
        changed = copy.deepcopy(active)
        changed["image_export"]["score_fitting_performed"] = True
        with self.assertRaises(ValueError):
            validate_active_preprocessing(changed)
        with self.assertRaises(ValueError):
            validate_legacy_equivalence(active, dict(pilot, context_scale=1.4))

    def test_exact_remaining_partition_and_preexisting_failure(self):
        rows = self.population()
        train = [row["video_id"] for row in rows if row["role"] == "train"]
        selected, terminal = job.partition(rows, train)
        self.assertEqual(len(selected), 1979)
        self.assertEqual(len(terminal), 1)
        self.assertEqual(selected, job.partition(list(reversed(rows)), train)[0])
        self.assertTrue(all(row["role"] in job.NEW_ROLES for row in selected))
        for mode in ("duplicate", "missing", "target", "train_reuse", "failed_frame", "fabricated_failure_score"):
            current, reused = copy.deepcopy(rows), list(train)
            if mode == "duplicate":
                current[-1] = current[0]
            elif mode == "missing":
                current.pop()
            elif mode == "target":
                current[-1]["role"] = "target"
            elif mode == "train_reuse":
                reused[-1] = reused[0]
            elif mode == "failed_frame":
                current[-1]["selected_frame"] = None
            else:
                next(row for row in current if row["selected_frame"] is None)["model_score"] = 0.5
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                job.partition(current, reused)

    def test_full4950_manifest_refuses_missing_duplicates_score_or_failure_fabrication(self):
        original = self.population()
        plan = {"all_transactions": original, "active_config_sha256": "a" * 64}
        rows = [
            dict(row, active_config_sha256="a" * 64, replacement=False,
                 detector_status="not_run" if row["selected_frame"] is None else "success",
                 asset_sha256={} if row["selected_frame"] is None else {"frame.png": "b" * 64})
            for row in original]
        job.validate_manifest(plan, rows)
        for mode in ("missing", "duplicate", "wrong_role", "frame", "score", "failure_pixels", "config"):
            current = copy.deepcopy(rows)
            if mode == "missing":
                current.pop()
            elif mode == "duplicate":
                current[-1] = current[0]
            elif mode == "wrong_role":
                current[-1]["role"] = "train"
            elif mode == "frame":
                current[-1]["selected_frame"] = {"decode_order": 2}
            elif mode == "score":
                current[-1]["model_score"] = 0.5
            elif mode == "config":
                current[-1]["active_config_sha256"] = "b" * 64
            else:
                next(row for row in current if row["selected_frame"] is None)["asset_sha256"] = {"invented.png": "c" * 64}
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                job.validate_manifest(plan, current)

    def fixture(self, output):
        image = np.full((112, 112, 3), (30, 70, 90), dtype=np.uint8)
        crop, geometry = shared_context_crop(image, np.array([10, 10, 110, 110]), REFERENCE_112)
        plan = {"videos": [], "legacy": [], "all_transactions": [], "terminal_transactions": [],
                "active_config_sha256": job._sha256(job.ACTIVE), "visual_indices": [0, 1],
                "historical_parameter_recipe_sha256": job._sha256(job.LEGACY),
                "deadline_unix_seconds": time.time() + 60, "sources": {}}
        for index, role in enumerate(("branch_calibration", "g_domain", "train")):
            media_path = output / f"media{index}.json"
            job.write_immutable_record(media_path, {"media_sha256": "b" * 64, "frame_count": 1, "byte_size": 10})
            transaction = {
                "video_id": f"1_1_{index:02d}_1", "role": role, "binary_label": "attack",
                "selected_frame": {"decode_order": 0, "height": 112, "width": 112,
                                   "rgb_sha256": hashlib.sha256(image.tobytes()).hexdigest()},
                "media_record_sha256": job._sha256(media_path), "media_sha256": "b" * 64}
            plan["videos"].append({"transaction": transaction, "media_path": str(media_path)})
            plan["all_transactions"].append(transaction)
            row = dict(transaction, index=index, model_sha256=job.MODEL_SHA256,
                       config_sha256=plan["active_config_sha256"], model_score=None, classifier_error=None,
                       replacement=False, retain_original_denominator=True)
            relative = f"frames/{index:04d}.png"
            row["selected_RGB_asset"] = {"path": relative, **job.write_png(relative, image)}
            if index == 1:
                row.update(detector_status="failed", final_k1_action="non_accept",
                           failure="no_face_above_frozen_threshold", assets={})
            else:
                row.update(detector_status="success", face_box_xyxy=[10, 10, 110, 110],
                           detector_confidence=0.9, landmarks=REFERENCE_112.tolist(), geometry=geometry,
                           crop_shape=list(crop.shape), crop_RGB_sha256=hashlib.sha256(crop.tobytes()).hexdigest(),
                           assets={})
                for name in ("shared", "224", "518"):
                    resized = crop if name == "shared" else cv2.resize(crop, (int(name), int(name)), interpolation=cv2.INTER_CUBIC)
                    relative = f"crops/{index:04d}-{name}.png"
                    row["assets"][relative] = job.write_png(relative, resized)
            job.write_immutable_record(output / "transactions" / f"{index:04d}.json", row)
        job.write_immutable_record(output / "plan.json", plan)
        job.write_immutable_record(output / "owner_approval.json", {"started_unix_seconds": time.time()})
        return plan

    def test_pixel_readback_all_roles_and_historical_record_digests(self):
        for mode in ("success", "legacy_hash", "missing", "frame", "role", "config", "crop", "failed_accept", "score"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                with patch.object(job, "OUTPUT", output):
                    plan = self.fixture(output)
                    index = 1 if mode == "failed_accept" else 0
                    path = output / "transactions" / f"{index:04d}.json"
                    row = job.read_json(path)
                    if mode == "missing":
                        path.unlink()
                    elif mode == "frame":
                        (output / "frames/0000.png").write_bytes(b"bad PNG")
                    elif mode == "crop":
                        (output / "crops/0000-518.png").write_bytes((output / "crops/0000-224.png").read_bytes())
                    elif mode == "role":
                        row["role"] = "target"
                    elif mode == "config":
                        row["config_sha256"] = "f" * 64
                    elif mode == "failed_accept":
                        row["final_k1_action"] = "accept"
                    elif mode == "score":
                        row["model_score"] = 0.5
                    if path.exists():
                        path.write_text(json.dumps(row))
                    if mode == "success":
                        for position in range(3):
                            entry, assets = job.validate_unit(plan["videos"][position], output, position, 4, plan["active_config_sha256"])
                            self.assertEqual(entry["role"], plan["videos"][position]["transaction"]["role"])
                            self.assertEqual(len(assets), 1 if position == 1 else 4)
                    else:
                        with self.assertRaises((ValueError, FileNotFoundError)):
                            job.validate_unit(plan["videos"][index], output, index, 4, plan["active_config_sha256"],
                                              "f" * 64 if mode == "legacy_hash" else None)

    def test_producer_uses_active_pin_and_never_infers_train_or_target(self):
        for role in ("branch_calibration", "g_domain", "train", "target"):
            for failed in (False, True):
                with self.subTest(role=role, failed=failed), tempfile.TemporaryDirectory() as directory:
                    output = Path(directory)
                    with patch.object(job, "OUTPUT", output):
                        image = np.full((112, 112, 3), 90, dtype=np.uint8)
                        payload = output / "tiny.avi"
                        payload.write_bytes(b"synthetic payload never decoded")
                        archive_path = output / "tiny.tar"
                        with tarfile.open(archive_path, "w") as archive:
                            archive.add(payload, arcname="tiny.avi")
                        media_path = output / "media.json"
                        job.write_immutable_record(media_path, {"media_relpath": "tiny.avi",
                            "byte_size": payload.stat().st_size, "media_sha256": job._sha256(payload)})
                        transaction = {
                            "video_id": "1_1_01_1", "role": role, "binary_label": "attack",
                            "selected_frame": {"decode_order": 1, "height": 112, "width": 112,
                                               "rgb_sha256": hashlib.sha256(image.tobytes()).hexdigest()},
                            "media_record_sha256": job._sha256(media_path), "media_sha256": job._sha256(payload)}
                        plan = {"deadline_unix_seconds": time.time() + 60, "active_config_sha256": "a" * 64}
                        with tarfile.open(archive_path) as archive, \
                                patch.object(job, "stream_frames", side_effect=lambda path, media, consume, **kwargs: consume(1, image)), \
                                patch("fas.preprocessing.detect_face", return_value=(np.array([10, 10, 110, 110, 0.9]), REFERENCE_112),
                                      side_effect=ValueError("no_face_above_frozen_threshold") if failed else None) as detector:
                            if role in {"train", "target"}:
                                with self.assertRaises(ValueError):
                                    job.produce_unit(Mock(), 0, {"transaction": transaction, "media_path": str(media_path)}, archive, archive.getmember("tiny.avi"), plan)
                                detector.assert_not_called()
                                self.assertFalse((output / "attempts").exists())
                            else:
                                row = job.produce_unit(Mock(), 0, {"transaction": transaction, "media_path": str(media_path)}, archive, archive.getmember("tiny.avi"), plan)
                                self.assertEqual(row["config_sha256"], "a" * 64)
                                self.assertIsNone(row["model_score"])
                                self.assertIsNone(row["classifier_error"])
                                self.assertEqual(row["detector_status"], "failed" if failed else "success")

    def completion(self, plan, output):
        entries = [job.validate_unit(video, output, index, 4, plan["active_config_sha256"])[0]
                   for index, video in enumerate(plan["videos"])]
        for entry in entries:
            entry["active_config_sha256"] = plan["active_config_sha256"]
        manifest = {"rows": entries, "originals": 3, "selected": 3,
                    "active_config_sha256": plan["active_config_sha256"]}
        job.write_immutable_record(output / "full_manifest.json", manifest)
        readback = {
            "transactions": 3, "originals": 3, "selected": 3, "preexisting_terminal_failure": 0,
            "reused_train": 0, "combined_detector_success": 2, "combined_detector_failure": 1,
            "detector_success": 2, "detector_failure": 1,
            "active_config_sha256": plan["active_config_sha256"], "provider": ["CPUExecutionProvider"],
            "gpu_seconds": 0, "model_scores": 0, "fitted_scores": 0,
            "role_originals": {"branch_calibration": 1, "g_domain": 1, "train": 1},
            "role_detector_success": {"branch_calibration": 1, "train": 1},
            "full_manifest_sha256": job._sha256(output / "full_manifest.json")}
        return readback

    def test_verifier_requires_exact_assets_rows_and_worker_completion(self):
        for mode in ("success", "missing_completion", "wrong_count", "missing_row", "extra_row", "orphan"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                with patch.object(job, "OUTPUT", output):
                    plan = self.fixture(output)
                    completion = {
                        "transactions": 3, "detector_success": 2, "detector_failure": 1,
                        "verified_native_frames": 3, "selected_payload_bytes": 30,
                        "provider": ["CPUExecutionProvider"], "gpu_seconds": 0,
                        "model_scores": 0, "fitted_scores": 0}
                    if mode != "missing_completion":
                        job.write_immutable_record(output / "worker_completion.json",
                                                   dict(completion, transactions=2) if mode == "wrong_count" else completion)
                    if mode == "missing_row":
                        (output / "transactions/0002.json").unlink()
                    elif mode == "extra_row":
                        (output / "transactions/0003.json").write_text("{}")
                    elif mode == "orphan":
                        (output / "frames/orphan.png").write_bytes(b"orphan")
                    original_sha = job._sha256
                    with patch.object(job, "check_bindings"), patch.object(job.previous, "guard"), \
                            patch.object(job, "validate_manifest"), \
                            patch.object(job, "_sha256", side_effect=lambda path: job.MODEL_SHA256 if path == job.previous.MODEL else original_sha(path)):
                        if mode == "success":
                            result = job.verify(plan)
                            self.assertEqual(result["detector_success"], 2)
                            self.assertEqual(result["detector_failure"], 1)
                            self.assertFalse(result["visual_inspection_completed"])
                        else:
                            with self.assertRaises((ValueError, FileNotFoundError)):
                                job.verify(plan)
                            self.assertFalse((output / "readback.json").exists())

    def test_supervisor_requires_readback_and_checks_final_caps(self):
        for mode in ("success", "missing_readback", "spawn", "readback_count", "final_rss", "final_storage", "deadline"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                with patch.object(job, "OUTPUT", output):
                    plan = self.fixture(output)
                    readback = self.completion(plan, output)
                    if mode == "readback_count":
                        readback["selected"] = 2
                    if mode != "missing_readback":
                        job.write_immutable_record(output / "readback.json", readback)
                    process = Mock(pid=424242)
                    process.wait.return_value = 0
                    measured = {"rss_bytes": 100, "output_bytes": 100, "temporary_bytes": 0}
                    final = dict(measured)
                    if mode == "final_rss":
                        final["rss_bytes"] = job.CAPS["rss_bytes"] + 1
                    elif mode == "final_storage":
                        final["output_bytes"] = job.CAPS["output_bytes"] + 1

                    def guard(value):
                        if mode == "deadline":
                            value["deadline_unix_seconds"] = time.time() - 1

                    with patch.object(job.subprocess, "Popen", return_value=process,
                                      side_effect=OSError("synthetic spawn failure") if mode == "spawn" else None), \
                            patch.object(job, "measured_usage", side_effect=[measured, measured, final]), \
                            patch.object(job, "validate_manifest"), patch.object(job, "check_bindings"), \
                            patch.object(job, "check_policy"), patch.object(job.previous, "guard", side_effect=guard), \
                            patch.object(job.os, "killpg"):
                        result = job.supervise(plan)
                    self.assertEqual(result["completion_claimed"], mode == "success")
                    if mode != "success":
                        failures = job.read_json(output / "failure_rows.json")["rows"]
                        self.assertEqual(len(failures), 3)
                        self.assertTrue(all(row["final_k1_action"] == "non_accept" for row in failures))

    def test_visual_sample_is_fixed_and_failure_source_is_included(self):
        videos = [{"transaction": dict(row, video_id=f"1_1_{number:04d}_1")}
                  for number, row in enumerate(self.population()) if row["role"] in job.NEW_ROLES and row["selected_frame"] is not None]
        fixed = job.fixed_indices(videos)
        self.assertEqual(fixed, job.fixed_indices(videos))
        self.assertTrue(set(range(0, len(videos), 100)) <= set(fixed))
        with tempfile.TemporaryDirectory() as directory, patch.object(job, "OUTPUT", Path(directory)):
            plan = self.fixture(Path(directory))
            rows = [job.validate_unit(video, Path(directory), index, 4, plan["active_config_sha256"])[0]
                    for index, video in enumerate(plan["videos"])]
            sheets = job.make_sheets(plan, rows)
            self.assertEqual(sheets[0]["indices"], [0, 1])
            self.assertEqual(sheets[1]["indices"], [1])
            self.assertEqual(sheets[1]["kind"], "failures")
            self.assertEqual(job._sha256(Path(directory) / sheets[0]["path"]), sheets[0]["sha256"])


if __name__ == "__main__":
    unittest.main()
