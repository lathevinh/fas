"""Model-free exact-population, pixel-readback and bounded-supervisor regressions."""

import hashlib
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import preprocess_oulu278 as batch
from fas.preprocessing import REFERENCE_112, shared_context_crop


class TrainBatchTest(unittest.TestCase):
    def transactions(self):
        return [{"video_id": f"1_1_{index:02d}_1", "role": "train",
                 "binary_label": "bona_fide" if index % 2 else "attack",
                 "selected_frame": {"decode_order": index}}
                for index in range(8)]

    def test_exact_partition_is_fixed_and_does_not_replace_failed_frames(self):
        rows = self.transactions()
        reused = rows[:2]
        remaining = batch.partition_train(rows, reused, total=8, reused_count=2)
        self.assertEqual(remaining, batch.partition_train(list(reversed(rows)), reused, total=8, reused_count=2))
        self.assertEqual({row["video_id"] for row in remaining}, {row["video_id"] for row in rows[2:]})
        for mode in ("duplicate", "missing", "reuse_duplicate", "wrong_parent", "target", "frame_failure"):
            current, reuse = [dict(row) for row in rows], [dict(row) for row in reused]
            if mode == "duplicate":
                current.append(current[0])
            elif mode == "missing":
                current.pop()
            elif mode == "reuse_duplicate":
                reuse[1] = reuse[0]
            elif mode == "wrong_parent":
                reuse[0]["selected_frame"] = {"decode_order": 100}
            elif mode == "target":
                current[2]["role"] = "g_domain"
            else:
                current[2]["selected_frame"] = None
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                batch.partition_train(current, reuse, total=8, reused_count=2)

    def fixture(self, output):
        image = np.full((112, 112, 3), (30, 70, 90), dtype=np.uint8)
        crop, geometry = shared_context_crop(image, np.array([10, 10, 110, 110]), REFERENCE_112)
        config = str(ROOT / "configs/preprocessing_pilot_v1.yaml")
        plan = {"videos": [], "reused_videos": [], "model_sha256": "a" * 64,
                "sources": {config: batch._sha256(Path(config))},
                "deadline_unix_seconds": time.time() + 60, "visual_indices": [0, 1]}
        for index in range(3):
            media_path = output / f"media{index}.json"
            batch.write_immutable_record(media_path, {"media_sha256": "b" * 64, "frame_count": 1, "byte_size": 10})
            transaction = {"video_id": f"1_1_{index:02d}_1", "role": "train", "binary_label": "attack",
                           "selected_frame": {"decode_order": 0, "height": 112, "width": 112,
                                              "rgb_sha256": hashlib.sha256(image.tobytes()).hexdigest()},
                           "media_record_sha256": batch._sha256(media_path), "media_sha256": "b" * 64}
            plan["videos"].append({"transaction": transaction, "media_path": str(media_path)})
            row = dict(transaction, index=index, model_sha256=plan["model_sha256"],
                       config_sha256=plan["sources"][config], model_score=None,
                       replacement=False, retain_original_denominator=True)
            relative = f"frames/{index:04d}.png"
            row["selected_RGB_asset"] = {"path": relative, **batch.write_png(relative, image)}
            if index == 1:
                row.update(detector_status="failed", final_k1_action="non_accept",
                           failure="no_face_above_frozen_threshold", assets={})
            else:
                row.update(detector_status="success", face_box_xyxy=[10, 10, 110, 110],
                           detector_confidence=0.9, landmarks=REFERENCE_112.tolist(), geometry=geometry,
                           crop_shape=list(crop.shape), crop_RGB_sha256=hashlib.sha256(crop.tobytes()).hexdigest(),
                           assets={})
                for name in ("shared", "224", "518"):
                    image_crop = crop if name == "shared" else cv2.resize(crop, (int(name), int(name)), interpolation=cv2.INTER_CUBIC)
                    relative = f"crops/{index:04d}-{name}.png"
                    row["assets"][relative] = batch.write_png(relative, image_crop)
            batch.write_immutable_record(output / "transactions" / f"{index:04d}.json", row)
        batch.write_immutable_record(output / "plan.json", plan)
        batch.write_immutable_record(output / "owner_approval.json", {"started_unix_seconds": time.time()})
        batch.write_immutable_record(output / "batch_authority.json", {"started_unix_seconds": time.time()})
        return plan

    def test_unit_pixel_readback_and_terminal_failure(self):
        for mode in ("success", "missing", "parent", "pixels", "crop", "geometry", "failed_accept", "status", "config", "replacement"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                with patch.object(batch, "OUTPUT", output):
                    plan = self.fixture(output)
                    index = 1 if mode == "failed_accept" else 0
                    path = output / "transactions" / f"{index:04d}.json"
                    row = batch.read_json(path)
                    if mode == "missing":
                        path.unlink()
                    elif mode == "parent":
                        row["selected_frame"] = dict(row["selected_frame"], decode_order=1)
                    elif mode == "pixels":
                        (output / "frames/0000.png").write_bytes(b"bad PNG")
                    elif mode == "crop":
                        (output / "crops/0000-518.png").write_bytes((output / "crops/0000-224.png").read_bytes())
                    elif mode == "geometry":
                        row["geometry"]["crop_xyxy_half_open"][0] = 1
                    elif mode == "failed_accept":
                        row["final_k1_action"] = "accept"
                    elif mode == "status":
                        row["detector_status"] = "unknown"
                    elif mode == "config":
                        row["config_sha256"] = "f" * 64
                    elif mode == "replacement":
                        row["replacement"] = True
                    if path.exists():
                        path.write_text(json.dumps(row))
                    if mode == "success":
                        for position in range(3):
                            actual, _ = batch.validate_unit(plan, position, root=output)
                            self.assertEqual(actual["detector_status"], "failed" if position == 1 else "success")
                    else:
                        with self.assertRaises((ValueError, FileNotFoundError)):
                            batch.validate_unit(plan, index, root=output)

    def test_combined_ledger_rejects_duplicates_missing_and_failed_accept(self):
        rows = self.transactions()
        plan = {"videos": [{"transaction": row} for row in rows[2:]],
                "reused_videos": [{"transaction": row} for row in rows[:2]]}
        ledger = [dict(row, detector_status="success") for row in rows]
        ledger[-1].update(detector_status="failed", final_k1_action="non_accept")
        batch.validate_ledger(plan, ledger)
        for broken in (ledger[:-1], ledger + [ledger[0]], ledger[:-1] + [ledger[0]],
                       ledger[:-1] + [dict(ledger[-1], final_k1_action="accept")]):
            with self.assertRaises(ValueError):
                batch.validate_ledger(plan, broken)

    def test_visual_coverage_is_fixed_and_includes_all_failures(self):
        videos = [{"transaction": row} for row in self.transactions()]
        fixed = batch.visual_indices(videos)
        self.assertIn(0, fixed)
        self.assertTrue({0, 1} <= set(fixed))
        with tempfile.TemporaryDirectory() as directory, patch.object(batch, "OUTPUT", Path(directory)):
            plan = self.fixture(Path(directory))
            ledger = [dict(index=index, reused=False, detector_status="failed" if index == 1 else "success") for index in range(3)]
            sheets = batch.make_sheets(plan, ledger)
            self.assertEqual(sheets[0]["indices"], [0, 1])
            self.assertEqual(sheets[1]["indices"], [1])
            self.assertEqual(sheets[1]["kind"], "failures")
            self.assertEqual(batch._sha256(Path(directory) / sheets[0]["path"]), sheets[0]["sha256"])

    def test_verify_exact_counts_and_asset_set(self):
        for mode in ("success", "missing_completion", "wrong_count", "missing_row", "extra_row", "orphan"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                with patch.object(batch, "OUTPUT", output):
                    plan = self.fixture(output)
                    # A tiny synthetic pilot has no reused rows; no model is loaded.
                    completion = {"transactions": 3, "detector_success": 2, "detector_failure": 1,
                                  "verified_native_frames": 3, "selected_payload_bytes": 30,
                                  "provider": ["CPUExecutionProvider"], "gpu_seconds": 0}
                    if mode != "missing_completion":
                        batch.write_immutable_record(output / "worker_completion.json",
                                                     dict(completion, transactions=2) if mode == "wrong_count" else completion)
                    if mode == "missing_row":
                        (output / "transactions/0002.json").unlink()
                    elif mode == "extra_row":
                        (output / "transactions/0003.json").write_text("{}")
                    elif mode == "orphan":
                        (output / "frames/orphan.png").write_bytes(b"orphan")
                    with patch.object(batch, "accepted_pilot", return_value=({"videos": []}, {})), \
                            patch.object(batch, "guard"), patch.object(batch, "check_bindings"), \
                            patch.object(batch, "_sha256", side_effect=lambda path: plan["model_sha256"] if path == batch.MODEL else hashlib.sha256(path.read_bytes()).hexdigest()):
                        if mode == "success":
                            result = batch.verify(plan)
                            self.assertEqual(result["combined_transactions"], 3)
                            self.assertEqual(result["combined_detector_failure"], 1)
                            self.assertFalse(result["sheet_inspected"])
                        else:
                            with self.assertRaises((ValueError, FileNotFoundError)):
                                batch.verify(plan)
                            self.assertFalse((output / "readback.json").exists())

    def test_supervisor_missing_completion_spawn_failure_and_final_caps(self):
        for mode in ("missing_readback", "spawn_failure", "final_rss", "final_storage", "final_deadline", "success"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                with patch.object(batch, "OUTPUT", output):
                    plan = self.fixture(output)
                    ledger = [batch.ledger_row(batch.read_json(path), path, False)
                              for path in sorted((output / "transactions").glob("*.json"))]
                    batch.write_immutable_record(output / "combined_ledger.json", {"rows": ledger})
                    if mode != "missing_readback":
                        batch.write_immutable_record(output / "readback.json",
                                                     {"combined_ledger_sha256": batch._sha256(output / "combined_ledger.json")})
                    measured = {"rss_bytes": 100, "output_bytes": 100, "temporary_bytes": 0}
                    final = dict(measured)
                    if mode == "final_rss":
                        final["rss_bytes"] = batch.CAPS["rss_bytes"] + 1
                    elif mode == "final_storage":
                        final["output_bytes"] = batch.CAPS["output_bytes"] + 1
                    process = Mock(pid=424242)
                    process.wait.return_value = 0

                    def final_guard(value):
                        if mode == "final_deadline":
                            value["deadline_unix_seconds"] = time.time() - 1

                    with patch.object(batch.subprocess, "Popen", return_value=process,
                                      side_effect=OSError("synthetic spawn failure") if mode == "spawn_failure" else None), \
                            patch.object(batch, "measured_usage", side_effect=[measured, measured, final]), \
                            patch.object(batch, "check_bindings"), patch.object(batch, "guard", side_effect=final_guard), \
                            patch.object(batch.os, "killpg"):
                        result = batch.supervise(plan)
                    self.assertEqual(result["completion_claimed"], mode == "success")
                    if mode != "success":
                        failures = batch.read_json(output / "failure_rows.json")["rows"]
                        self.assertEqual(len(failures), 3)
                        self.assertTrue(all(row["final_k1_action"] == "non_accept" for row in failures))
                        self.assertFalse(result["automatic_retry"])

    def test_storage_includes_both_retained_packages_and_deleted_temporaries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folders = [root / name for name in ("batch", "pilot", "acquisition")]
            for folder in folders:
                folder.mkdir()
                (folder / "data").write_bytes(b"12345")
            measured = {"rss_bytes": 0, "temporary_bytes": 7, "output_bytes": 0}
            with patch.object(batch, "OUTPUT", folders[0]), patch.object(batch, "PILOT", folders[1]), \
                    patch.object(batch, "ACQUISITION", folders[2]), patch.object(batch, "usage", return_value=measured):
                self.assertEqual(batch.measured_usage(0)["output_bytes"], 22)
            (folders[0] / "link").symlink_to(folders[1] / "data")
            with self.assertRaises(ValueError):
                batch.tree_bytes(folders[0])

    def test_single_unit_producer_saves_frozen_pixels_and_explicit_detector_failure(self):
        import tarfile

        for failed in (False, True):
            with self.subTest(failed=failed), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                with patch.object(batch, "OUTPUT", output):
                    image = np.full((112, 112, 3), 90, dtype=np.uint8)
                    payload = output / "tiny.avi"
                    payload.write_bytes(b"synthetic payload, never decoded")
                    archive_path = output / "tiny.tar"
                    with tarfile.open(archive_path, "w") as archive:
                        archive.add(payload, arcname="tiny.avi")
                    media_path = output / "media.json"
                    batch.write_immutable_record(media_path, {
                        "media_relpath": "tiny.avi", "byte_size": payload.stat().st_size,
                        "media_sha256": batch._sha256(payload)})
                    transaction = {"video_id": "1_1_01_1", "role": "train", "binary_label": "attack",
                                   "selected_frame": {"decode_order": 1, "height": 112, "width": 112,
                                                      "rgb_sha256": hashlib.sha256(image.tobytes()).hexdigest()},
                                   "media_record_sha256": batch._sha256(media_path),
                                   "media_sha256": batch._sha256(payload)}
                    plan = {"deadline_unix_seconds": time.time() + 60,
                            "sources": {str(ROOT / "configs/preprocessing_pilot_v1.yaml"): "c" * 64}}
                    with tarfile.open(archive_path) as archive, \
                            patch.object(batch, "stream_frames", side_effect=lambda path, media, consume, **kwargs: consume(1, image)), \
                            patch("fas.preprocessing.detect_face",
                                  return_value=(np.array([10, 10, 110, 110, 0.9]), REFERENCE_112),
                                  side_effect=ValueError("no_face_above_frozen_threshold") if failed else None):
                        row = batch.produce_unit(Mock(), 0, {"transaction": transaction, "media_path": str(media_path)},
                                                 archive, archive.getmember("tiny.avi"), plan)
                    self.assertEqual(row["detector_status"], "failed" if failed else "success")
                    self.assertFalse(row["replacement"])
                    self.assertEqual(len(row["assets"]), 0 if failed else 3)
                    self.assertEqual(batch.read_json(output / "transactions/0000.json"), row)

    def test_additional_remount_recovery_is_single_pass_and_fails_closed(self):
        import recover_oulu278 as recovery

        for mode in ("success", "mismatch", "deadline", "rss", "non_device_drift", "final_drift", "corrupt_row"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                output, old, archives = root / "output", root / "old", root / "archives"
                archives.mkdir()
                payloads = {name: (name.encode() * 10) for name in ("Dev.tar", "Test.tar", "Train.tar")}
                accepted = {"archives": {}}
                for name, payload in payloads.items():
                    path = archives / name
                    path.write_bytes(payload)
                    identity = recovery.file_identity(path.lstat())
                    identity["device"] += 1
                    if mode == "non_device_drift":
                        identity["inode"] += 1
                    accepted["archives"][name] = {"current_identity": identity}
                anchors = {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()}
                if mode == "mismatch":
                    anchors["Dev.tar"] = "f" * 64
                sizes = {name: len(payload) for name, payload in payloads.items()}
                caps = dict(recovery.RECOVERY_CAPS, archive_bytes=sum(sizes.values()))
                plan = {"paths": {"input_root": str(archives)}}
                approval = {"recovery_deadline_unix_seconds": time.time() + (-1 if mode == "deadline" else 60)}
                batch.write_immutable_record(output / "owner_approval.json", approval)
                batch.write_immutable_record(old / "recovery/binding.json", accepted)
                rss = Mock(ru_maxrss=2 * 1024 ** 2 if mode == "rss" else 100)
                with patch.object(recovery, "OUTPUT", output), patch.object(recovery, "PILOT", old), \
                        patch.object(recovery, "ANCHORS", anchors), patch.object(recovery, "ARCHIVE_SIZES", sizes), \
                        patch.object(recovery, "RECOVERY_CAPS", caps), patch.object(recovery, "authority", return_value=approval), \
                        patch.object(recovery, "accepted_binding", return_value=(plan, accepted)), \
                        patch.object(recovery.resource, "getrusage", return_value=rss):
                    if mode in {"mismatch", "deadline", "rss", "non_device_drift"}:
                        with self.assertRaises((ValueError, TimeoutError)):
                            recovery.recover()
                        self.assertFalse((output / "recovery/binding.json").exists())
                    else:
                        result = recovery.recover()
                        self.assertEqual(result["bytes_read"], sum(sizes.values()))
                        self.assertTrue(result["whole_file_equality"])
                        binding_path = output / "recovery/binding.json"
                        plan.update(additive_recovery_binding_path=str(binding_path),
                                    additive_recovery_binding_sha256=batch._sha256(binding_path))
                        if mode == "final_drift":
                            (archives / "Dev.tar").write_bytes(b"changed")
                        elif mode == "corrupt_row":
                            (output / "recovery/Dev.tar.rehash.json").write_text("{}")
                        if mode == "success":
                            self.assertEqual(set(recovery.verified_identities(plan)), set(payloads))
                        else:
                            with self.assertRaises(ValueError):
                                recovery.verified_identities(plan)
                    with self.assertRaises(FileExistsError):
                        recovery.recover()

    def test_terminal_public_summary_retains_failure_without_private_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "PRIVATE_OUTPUT"
            batch.write_immutable_record(output / "owner_approval.json", {"private_identity": "PRIVATE_VIDEO"})
            with patch.object(batch, "ROOT", root / "public"), patch.object(batch, "OUTPUT", output):
                batch.publish_summary({"completion_claimed": False,
                                       "failure": "ValueError: PRIVATE_OUTPUT/PRIVATE_VIDEO"})
            path = root / "public/results/phase1/oulu-preprocessing278-train-v1.json"
            report = batch.read_json(path)
            self.assertEqual(report["status"], "stopped_failure_no_retry")
            self.assertEqual(report["failure_category"], "ValueError")
            self.assertFalse(report["visual_inspection_completed"])
            self.assertNotIn("PRIVATE", path.read_text())


if __name__ == "__main__":
    unittest.main()
