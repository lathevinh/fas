"""Synthetic MSU grouping, split transport, fixed selection and supervision."""

import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import preprocess_msu282 as job
from fas.preprocessing import REFERENCE_112
from fas.transactions import technical_transaction


class MsuPackageTest(unittest.TestCase):
    def population(self):
        videos, roles = [], []
        for subject in range(35):
            role = "train" if subject < 21 else "branch_calibration" if subject < 28 else "g_domain"
            for sensor in ("android", "laptop"):
                for attack in ("none", "ipad_video", "iphone_video", "printed_photo"):
                    identity = f"{subject:03d}-{sensor}-{attack}"
                    row = {"video_id": identity, "dataset": "MSU-MFSD", "subject_id": f"subject-{subject:03d}",
                           "group_id": f"subject-{subject:03d}", "group_unit": "subject",
                           "official_split": "train" if subject < 15 else "test",
                           "binary_label": "bona_fide" if attack == "none" else "attack",
                           "sensor_id": sensor, "reference_attack_type": attack, "role": role}
                    videos.append(row)
                    roles.append({key: row[key] for key in ("video_id", "dataset", "subject_id", "binary_label", "role")})
        return videos, roles

    def test_exact_native_population_frozen_groups_and_no_role_repair(self):
        videos, roles = self.population()
        self.assertEqual(job.group_checks(videos, roles)["forbidden_subject_crossings"], 0)
        for mode in ("duplicate", "missing", "subject_crossing", "role_swap", "official_overlap", "type"):
            current, assigned = copy.deepcopy(videos), copy.deepcopy(roles)
            if mode == "duplicate":
                current[-1] = current[0]
            elif mode == "missing":
                assigned.pop()
            elif mode == "subject_crossing":
                for row in current[-8:]:
                    row["subject_id"] = current[0]["subject_id"]
                    row["group_id"] = row["subject_id"]
                for row in assigned[-8:]:
                    row["subject_id"] = current[0]["subject_id"]
            elif mode == "role_swap":
                assigned[0]["role"] = "g_domain"
            elif mode == "official_overlap":
                current[0]["official_split"] = "test"
            else:
                current[0]["reference_attack_type"] = "unknown"
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                job.group_checks(current, assigned)

    def test_full_manifest_requires_every_original_and_preserves_both_failure_types(self):
        videos, _ = self.population()
        rows = [dict(row, selected_frame={"decode_order": 1}, detector_status="success",
                     active_config_sha256="a" * 64, model_score=None, classifier_error=None,
                     replacement=False, retain_original_denominator=True, final_k1_action=None,
                     asset_sha256={"frame.png": "b" * 64}) for row in videos]
        rows[-1].update(selected_frame=None, detector_status="not_run", final_k1_action="non_accept", asset_sha256={})
        rows[-2].update(detector_status="failed", final_k1_action="non_accept")
        plan = {"videos": videos, "active_config_sha256": "a" * 64}
        counts = job.validate_manifest(plan, rows)
        self.assertEqual(counts, {"originals": 280, "selected": 279, "pre_detector_failure": 1,
                                  "detector_success": 278, "detector_failure": 1})
        for mode in ("duplicate", "missing", "role", "score", "failure_accept", "failure_image", "config"):
            current = copy.deepcopy(rows)
            if mode == "duplicate":
                current[-1] = current[0]
            elif mode == "missing":
                current.pop()
            elif mode == "role":
                current[0]["role"] = "target"
            elif mode == "score":
                current[0]["model_score"] = 0.5
            elif mode == "failure_accept":
                current[-2]["final_k1_action"] = "accept"
            elif mode == "failure_image":
                current[-1]["asset_sha256"] = {"fake.png": "f" * 64}
            else:
                current[0]["active_config_sha256"] = "f" * 64
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                job.validate_manifest(plan, current)

    def test_exact_content_groups_stop_for_prohibited_boundaries(self):
        videos, _ = self.population()
        canonical = {row["video_id"]: row for row in videos}
        media = [{"video_id": row["video_id"], "media_sha256": hashlib.sha256(row["video_id"].encode()).hexdigest(),
                  "decoded_rgb_sequence_sha256": None} for row in videos]
        self.assertEqual(job.exact_checks(media, canonical), [])
        # Two attacks of one subject/class/split/role may be exact without dropping either ID.
        media[2]["media_sha256"] = media[1]["media_sha256"]
        self.assertEqual(len(job.exact_checks(media, canonical)), 1)
        media[-1]["media_sha256"] = media[1]["media_sha256"]
        with self.assertRaisesRegex(ValueError, "forbidden exact"):
            job.exact_checks(media, canonical)

    def transport(self, root, corrupt=False):
        inputs, output = root / "input", root / "output"
        inputs.mkdir()
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w", compression=zipfile.ZIP_STORED) as inner:
            for name in job.METADATA_SHA256:
                inner.writestr(name, b"synthetic native text")
            inner.writestr("tiny.mp4", b"synthetic video bytes, no decoder")
        raw = payload.getvalue()
        size = (len(raw) + 15) // 16
        parts = [raw[index * size:(index + 1) * size] for index in range(16)]
        outer_rows = []
        for index in range(8):
            path = inputs / f"outer{index}.zip"
            with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
                if index == 0:
                    archive.writestr("MSU-MFSD/README.txt", b"outer README")
                for number in (index * 2, index * 2 + 1):
                    archive.writestr(f"MSU-MFSD/MSU-MFSD-Publish.zip.{number + 1:03d}", parts[number])
            with zipfile.ZipFile(path) as archive:
                headers = [job.native.header_record(entry) for entry in archive.infolist()]
                if corrupt and index == 0:
                    entry = archive.infolist()[1]
                    offset = entry.header_offset + 30 + len(entry.filename.encode()) + len(entry.extra)
            if corrupt and index == 0:
                content = bytearray(path.read_bytes())
                content[offset] ^= 1
                path.write_bytes(content)
            outer_rows.append({"archive": path.name, "headers": headers})
        with zipfile.ZipFile(io.BytesIO(raw)) as inner:
            inner_headers = [job.native.header_record(entry) for entry in inner.infolist()]
        plan = {"archive_identities": {path.name: job.identity(path) for path in inputs.glob("*.zip")},
                "outer_headers": outer_rows, "inner_headers": inner_headers,
                "videos": [{"video_id": "fixture", "release_id": "fixture", "role": "train"}],
                "deadline_unix_seconds": time.time() + 60}
        output.mkdir()
        return inputs, output, plan, raw

    def test_actual_sixteen_volume_transport_crc_hash_and_identity_guard(self):
        for mode in ("success", "crc", "missing_header", "deadline", "identity"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                inputs, output, plan, raw = self.transport(Path(directory), corrupt=mode == "crc")
                if mode == "missing_header":
                    plan["outer_headers"][0]["headers"].pop()
                elif mode == "deadline":
                    plan["deadline_unix_seconds"] = time.time() - 1
                elif mode == "identity":
                    plan["archive_identities"]["outer0.zip"][3] += 1
                inventory = {"videos": [{"video_id": "fixture", "release_id": "fixture", "role": None}]}
                with patch.object(job, "INPUT", inputs), patch.object(job, "OUTPUT", output), \
                        patch.object(job.native, "OUTER_README_SHA256", hashlib.sha256(b"outer README").hexdigest()), \
                        patch.object(job, "inventory_headers", return_value=inventory):
                    if mode == "success":
                        joined, receipt = job.stage_release(plan)
                        self.assertEqual(joined.read_bytes(), raw)
                        self.assertEqual(len(receipt["volumes"]), 16)
                        self.assertEqual(sum(row["byte_size"] for row in receipt["volumes"]), len(raw))
                        self.assertTrue(receipt["native_metadata_and_headers_verified"])
                        self.assertFalse(receipt["original_archives_modified"])
                        with self.assertRaises(FileExistsError):
                            job.stage_release(plan)
                    else:
                        with self.assertRaises((ValueError, TimeoutError, zipfile.BadZipFile)):
                            job.stage_release(plan)
                        self.assertFalse((output / "release_integrity.json").exists())

    def test_payload_exact_sizes_and_deadline(self):
        for count, expected, deadline in ((5, 5, time.time() + 60), (5, 4, time.time() + 60),
                                          (4, 5, time.time() + 60), (5, 5, time.time() - 1)):
            source, target = io.BytesIO(b"x" * count), io.BytesIO()
            if count == expected and deadline > time.time():
                result = job.checked_copy(source, target, expected, deadline=deadline)
                self.assertEqual(result["sha256"], hashlib.sha256(b"x" * count).hexdigest())
            else:
                with self.assertRaises(ValueError):
                    job.checked_copy(source, target, expected, deadline=deadline)

    def test_real_strict_decode_middle_frame_and_saved_pixel_readback(self):
        for mode in ("success", "detector_failure", "decode_failure"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                (output / "temporary").mkdir()
                source = output / "fixture.mp4"
                if mode == "decode_failure":
                    source.write_bytes(b"invalid video fixture")
                else:
                    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                                    "color=c=gray:s=112x112:r=2:d=2", "-threads", "1", "-c:v", "mpeg4",
                                    str(source)], check=True, capture_output=True)
                archive_path = output / "fixture.zip"
                with zipfile.ZipFile(archive_path, "w") as archive:
                    archive.write(source, "fixture.mp4")
                with zipfile.ZipFile(archive_path) as archive:
                    original = {"dataset": "MSU-MFSD", "video_id": "fixture", "role": "branch_calibration",
                                "binary_label": "attack", "official_split": "train", "subject_id": "subject-001",
                                "media_relpath": "fixture.mp4",
                                "archive_header": job.native.header_record(archive.getinfo("fixture.mp4"))}
                    plan = {"active_config_sha256": job._sha256(job.images.ACTIVE), "deadline_unix_seconds": time.time() + 60}
                    with patch.object(job, "OUTPUT", output), \
                            patch("fas.preprocessing.detect_face", return_value=(np.array([10, 10, 110, 110, 0.9]), REFERENCE_112),
                                  side_effect=ValueError("no_face_above_frozen_threshold") if mode == "detector_failure" else None):
                        row, media = job.produce_unit(plan, 0, original, archive, Mock())
                    self.assertFalse((output / "temporary/selected.mp4").exists())
                    self.assertIsNone(row["model_score"])
                    if mode == "decode_failure":
                        self.assertIsNone(row["selected_frame"])
                        self.assertEqual(row["detector_status"], "not_run")
                        self.assertEqual(row["final_k1_action"], "non_accept")
                        self.assertNotIn("selected_RGB_asset", row)
                    else:
                        self.assertEqual(row["selected_frame"]["decode_order"], 1)
                        self.assertEqual(media["frame_count"], 4)
                        self.assertEqual(row["detector_status"], "failed" if mode == "detector_failure" else "success")
                        transaction = technical_transaction(media)
                        transaction.update(media_sha256=media["media_sha256"], media_record_sha256=row["media_record_sha256"])
                        entry, assets = job.images.validate_unit(
                            {"transaction": transaction, "media_path": str(output / "media/0000.json")},
                            output, 0, 4, plan["active_config_sha256"])
                        self.assertEqual(len(assets), 1 if mode == "detector_failure" else 4)
                        self.assertEqual(entry["video_id"], "fixture")

    def supervisor_fixture(self, output):
        videos, _ = self.population()
        plan = {"videos": videos, "active_config_sha256": job._sha256(job.images.ACTIVE),
                "deadline_unix_seconds": time.time() + 60, "sources": {}}
        job.write_immutable_record(output / "plan.json", plan)
        job.write_immutable_record(output / "owner_approval.json", {"started_unix_seconds": time.time()})
        rows = [dict(row, selected_frame=None, detector_status="not_run", final_k1_action="non_accept",
                     active_config_sha256=plan["active_config_sha256"], model_score=None, classifier_error=None,
                     replacement=False, retain_original_denominator=True, asset_sha256={}) for row in videos]
        job.write_immutable_record(output / "full_manifest.json", {"rows": rows, "active_config_sha256": plan["active_config_sha256"]})
        for name in ("release_integrity", "content_checks"):
            job.write_immutable_record(output / (name + ".json"), {})
        readback = {**job.validate_manifest(plan, rows),
                    "full_manifest_sha256": job._sha256(output / "full_manifest.json"),
                    "per_unit_sha256": {}, "release_integrity_sha256": job._sha256(output / "release_integrity.json"),
                    "content_checks_sha256": job._sha256(output / "content_checks.json")}
        return plan, readback

    def test_supervisor_zero_without_readback_final_caps_and_owned_cleanup(self):
        for mode in ("success", "missing_readback", "spawn", "wrong_count", "rss", "storage", "deadline"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                with patch.object(job, "OUTPUT", output):
                    plan, readback = self.supervisor_fixture(output)
                    (output / "temporary").mkdir()
                    (output / "temporary/MSU-MFSD-Publish.zip").write_bytes(b"owned temporary")
                    (output / "temporary/not-owned").write_bytes(b"preserved fixture")
                    if mode == "wrong_count":
                        readback["originals"] = 279
                    if mode != "missing_readback":
                        job.write_immutable_record(output / "readback.json", readback)
                    measured = {"rss_bytes": 100, "output_bytes": 100, "temporary_bytes": 0}
                    final = dict(measured)
                    if mode == "rss":
                        final["rss_bytes"] = job.CAPS["rss_bytes"] + 1
                    elif mode == "storage":
                        final["output_bytes"] = job.CAPS["output_bytes"] + 1
                    process = Mock(pid=424242)
                    process.wait.return_value = 0

                    def guard(value):
                        if mode == "deadline":
                            value["deadline_unix_seconds"] = time.time() - 1

                    with patch.object(job.subprocess, "Popen", return_value=process,
                                      side_effect=OSError("synthetic spawn failure") if mode == "spawn" else None), \
                            patch.object(job, "check_bindings"), patch.object(job, "archive_guard", side_effect=guard), \
                            patch.object(job, "measured_usage", side_effect=[measured, measured, final]), \
                            patch.object(job.os, "killpg"):
                        result = job.supervise(plan)
                    self.assertEqual(result["completion_claimed"], mode == "success")
                    self.assertFalse((output / "temporary/MSU-MFSD-Publish.zip").exists())
                    self.assertTrue((output / "temporary/not-owned").exists())
                    if mode != "success":
                        failed = job.read_json(output / "failure_rows.json")["rows"]
                        self.assertEqual(len(failed), 280)
                        self.assertTrue(all(row["final_k1_action"] == "non_accept" for row in failed))

    def test_fixed_visuals_are_outcome_independent_and_decode_failures_are_explicit(self):
        videos, _ = self.population()
        indices = job.fixed_indices(videos)
        changed = [dict(row, detector_status="failed") for row in videos]
        self.assertEqual(indices, job.fixed_indices(changed))
        self.assertTrue(set(range(0, 280, 20)) <= set(indices))
        with tempfile.TemporaryDirectory() as directory, patch.object(job, "OUTPUT", Path(directory)):
            rgb = np.full((112, 112, 3), 90, np.uint8)
            job.write_png("frames/0001.png", rgb)
            rows = [{"index": 0, "selected_frame": None, "detector_status": "not_run"},
                    {"index": 1, "selected_frame": {"decode_order": 1}, "detector_status": "failed"}]
            sheets = job.make_sheets({"visual_indices": [0, 1]}, rows)
            self.assertEqual(sheets[0]["indices"], [0, 1])
            self.assertEqual(sheets[1]["indices"], [1])
            self.assertEqual(sheets[1]["kind"], "failures")

    def verifier_fixture(self, output):
        videos, _ = self.population()
        for index, row in enumerate(videos):
            row.update(media_relpath=f"synthetic/{index:04d}.mp4", byte_size=index + 1)
        plan = {
            "videos": videos, "active_config_sha256": job._sha256(job.images.ACTIVE),
            "sources": {}, "visual_indices": [0, 20],
            "archive_identities": {"outer.zip": [1, 2, 3, 4, 5]}, "inner_headers": []}
        media_rows = []
        for index, original in enumerate(videos):
            media = {key: original[key] for key in ("video_id", "role", "binary_label", "official_split", "subject_id", "media_relpath")}
            media.update(
                media_sha256=hashlib.sha256(original["video_id"].encode()).hexdigest(),
                byte_size=original["byte_size"], inner_crc_checked_to_eof=True,
                decode_status="failed", frame_count=0, frame_index=[],
                decoded_rgb_sequence_sha256=None, failure_reason="synthetic failed media")
            media_path = output / "media" / f"{index:04d}.json"
            job.write_immutable_record(media_path, media)
            transaction = technical_transaction(media)
            transaction.update(media_sha256=media["media_sha256"], media_record_sha256=job._sha256(media_path))
            row = dict(transaction, index=index, replacement=False,
                       model_sha256=job.MODEL_SHA256, config_sha256=plan["active_config_sha256"], assets={})
            job.write_immutable_record(output / "transactions" / f"{index:04d}.json", row)
            job.write_immutable_record(output / "attempts" / f"{index:04d}.json", {"index": index, "status": "started"})
            media_rows.append(media)
        job.write_immutable_record(output / "content_checks.json", {"exact_groups": [], "forbidden_exact_crossings": 0})
        job.write_immutable_record(output / "release_integrity.json", {
            "archive_pins": {"outer.zip": {"file_identity": [1, 2, 3, 4, 5], "bytes_read": 3}},
            "archive_bytes": 3, "joined_zip_bytes": 16,
            "volumes": [{"volume": number, "byte_size": 1, "outer_crc_checked_to_eof": True}
                        for number in range(1, 17)]})
        completion = {
            "transactions": 280, "media_crc_checked": 280, "native_frames": 0,
            "selected_payload_bytes": sum(row["byte_size"] for row in media_rows),
            "provider": ["CPUExecutionProvider"], "gpu_seconds": 0, "model_scores": 0, "fitted_scores": 0,
            "ancillary_entries": {}}
        (output / "temporary").mkdir()
        return plan, completion

    def test_verifier_exact280_missing_completion_denominators_and_orphan_refusal(self):
        for mode in ("success", "missing_completion", "wrong_count", "missing_row", "extra_row", "orphan", "temporary", "auxiliary"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                with patch.object(job, "OUTPUT", output):
                    plan, completion = self.verifier_fixture(output)
                    if mode != "missing_completion":
                        job.write_immutable_record(output / "worker_completion.json",
                                                   dict(completion, transactions=279) if mode == "wrong_count" else completion)
                    if mode == "missing_row":
                        (output / "transactions/0000.json").unlink()
                    elif mode == "extra_row":
                        (output / "transactions/0280.json").write_text("{}")
                    elif mode == "orphan":
                        (output / "frames").mkdir()
                        (output / "frames/orphan.png").write_bytes(b"orphan")
                    elif mode == "temporary":
                        (output / "temporary/selected.mp4").write_bytes(b"unremoved")
                    elif mode == "auxiliary":
                        plan["inner_headers"] = [{"path": "annotation.face", "size": 10}]
                    original_sha = job._sha256
                    with patch.object(job, "check_bindings"), patch.object(job, "archive_guard"), \
                            patch.object(job, "_sha256", side_effect=lambda path: job.MODEL_SHA256 if path == job.retained.MODEL else original_sha(path)):
                        if mode == "success":
                            result = job.verify(plan)
                            self.assertEqual(result["originals"], 280)
                            self.assertEqual(result["pre_detector_failure"], 280)
                            self.assertEqual(result["selected"], 0)
                            self.assertEqual(result["detector_success"], 0)
                            self.assertFalse(result["visual_inspection_completed"])
                        else:
                            with self.assertRaises((ValueError, FileNotFoundError)):
                                job.verify(plan)
                            self.assertFalse((output / "readback.json").exists())


if __name__ == "__main__":
    unittest.main()
