"""CASIA frozen-group, actual RAR transport and complete-output regressions."""

import copy
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import shutil
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch
import zlib

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import preprocess_casia285 as job
from fas.casia import inventory_headers, parse_media_path, REFERENCE_CODES
from fas.preprocessing import REFERENCE_112

EXTRACTOR = job.EXTRACTOR if job.EXTRACTOR.is_file() else shutil.which("bsdtar")


def rar_header(body):
    framed = vint(len(body)) + body
    return struct.pack("<I", zlib.crc32(framed)) + framed


def vint(value):
    result = bytearray()
    while value >= 128:
        result.append((value & 127) | 128)
        value >>= 7
    result.append(value)
    return bytes(result)


def stored_rar(entries):
    result = bytearray(b"Rar!\x1a\x07\x01\x00")
    result.extend(rar_header(vint(1) + vint(0) + vint(0)))
    for name, payload, directory in entries:
        encoded = name.encode()
        body = vint(2) + vint(2) + vint(len(payload)) + vint(1 if directory else 4)
        body += vint(len(payload)) + vint(0o40755 if directory else 0o100644)
        if not directory:
            body += struct.pack("<I", zlib.crc32(payload))
        body += vint(0) + vint(1) + vint(len(encoded)) + encoded
        result.extend(rar_header(body))
        result.extend(payload)
    result.extend(rar_header(vint(5) + vint(0) + vint(0)))
    return bytes(result)


class CasiaPreprocessingTest(unittest.TestCase):
    def population(self):
        videos, roles, headers = [], [], []
        counter = 0
        for split, count in (("train_release", 20), ("test_release", 30)):
            headers.append({"relpath": split, "byte_size": 0, "kind": "directory", "encrypted": False})
            for subject in range(1, count + 1):
                role = "train" if counter < 30 else "branch_calibration" if counter < 40 else "g_domain"
                counter += 1
                headers.append({"relpath": f"{split}/{subject}", "byte_size": 0, "kind": "directory", "encrypted": False})
                for token in REFERENCE_CODES:
                    path = f"{split}/{subject}/{token}.avi"
                    native = parse_media_path(path)
                    size = len(b"payload:" + path.encode())
                    headers.append({"relpath": path, "byte_size": size, "kind": "file", "encrypted": False})
                    videos.append({
                        **native, "byte_size": size, "release_id": "synthetic", "protocol_id": "reference",
                        "media_archive": "CASIA_faceAntisp.rar", "media_sha256": None,
                        "container": None, "codec": None, "duration_ms": None, "fps": None,
                        "frame_count": None, "decode_status": "not_probed",
                        "role": role, "group_id": native["subject_id"], "group_unit": "subject"})
                    roles.append({key: videos[-1][key] for key in ("video_id", "dataset", "subject_id", "binary_label", "role")})
        return sorted(videos, key=lambda row: row["video_id"]), roles, headers

    def test_exact600_reference_groups_and_null_role_projection(self):
        videos, roles, headers = self.population()
        self.assertEqual(job.group_checks(videos, roles)["forbidden_subject_crossings"], 0)
        native = [dict(row, role=None) for row in videos]
        self.assertEqual(job.group_checks(native, roles)["subjects"], 50)
        job.reconcile_headers(headers, videos)
        for mode in ("duplicate", "missing", "native_mapping", "group", "wrong_label"):
            current, assigned = copy.deepcopy(videos), copy.deepcopy(roles)
            if mode == "duplicate":
                current[-1] = current[0]
            elif mode == "missing":
                assigned.pop()
            elif mode == "native_mapping":
                current[0]["subject_id"] = "subject-01"
            elif mode == "group":
                current[0]["group_id"] = "other"
            else:
                assigned[0]["binary_label"] = "wrong"
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                job.group_checks(current, assigned)

    def test_typed_headers_reject_links_unsafe_duplicates_and_wrong_shape(self):
        valid = "-rw-r--r-- 0 0 0 12 Jul 9 2019 test_release/1/1.avi"
        self.assertEqual(job.typed_headers(valid)[0]["byte_size"], 12)
        for text in ("", valid + "\n" + valid, valid.replace("-rw", "lrw"),
                     valid.replace("test_release/1/1.avi", "../bad"),
                     valid.replace("12 Jul", "unknown Jul"), valid + " extra"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                job.typed_headers(text)

    @unittest.skipUnless(EXTRACTOR, "existing bsdtar required for actual RAR5 transport regression")
    def test_actual_rar_listing_extraction_crc_and_source_identity(self):
        videos, _, headers = self.population()
        for mode in ("success", "crc", "identity", "missing_member"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                output = root / "output"
                output.mkdir()
                archive = root / "CASIA_faceAntisp.rar"
                entries = [(row["relpath"], b"" if row["kind"] == "directory" else b"payload:" + row["relpath"].encode(),
                            row["kind"] == "directory") for row in headers]
                payload = stored_rar(entries)
                if mode == "crc":
                    payload = payload.replace(b"payload:", b"payloae:", 1)
                elif mode == "missing_member":
                    payload = stored_rar(entries[:-1])
                archive.write_bytes(payload)
                plan = {
                    "archive_identity": job.shared.identity(archive), "extractor_identity": job.shared.identity(Path(EXTRACTOR)),
                    "headers": headers, "videos": videos, "deadline_unix_seconds": time.time() + 60}
                with patch.object(job, "ARCHIVE", archive), patch.object(job, "OUTPUT", output), patch.object(job, "EXTRACTOR", Path(EXTRACTOR)):
                    # The fixture has real RAR headers/CRCs, not a mocked extractor.
                    actual_headers = job.list_headers()
                    plan["headers"] = actual_headers
                    plan["crc_headers"] = job.read_file_headers(archive)
                    if mode == "identity":
                        plan["archive_identity"][3] += 1
                    if mode == "success":
                        job.reconcile_headers(actual_headers, videos)
                        job.stage_release(plan)
                        receipt = job.read(output / "release_integrity.json")
                        self.assertEqual(receipt["archive_sha256"], job.sha(archive))
                        self.assertTrue(receipt["independent_unpacked_crc32_verified"])
                        self.assertEqual(receipt["extracted_videos"], 600)
                        job.cleanup()
                        self.assertEqual(list((output / "temporary").iterdir()), [])
                    else:
                        with self.assertRaises(ValueError):
                            job.stage_release(plan)
                        self.assertFalse((output / "release_integrity.json").exists())

    def test_rar5_header_crc_bounds_and_unsafe_metadata_fail_closed(self):
        valid = stored_rar([("test_release/1/1.avi", b"native", False)])
        for mode in ("valid", "crc", "truncated", "wrong_format", "missing_end", "trailing", "unsafe", "directory_data"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "synthetic.rar"
                payload = valid
                if mode == "crc":
                    payload = valid[:8] + bytes([valid[8] ^ 1]) + valid[9:]
                elif mode == "truncated":
                    payload = valid[:11]
                elif mode == "wrong_format":
                    payload = b"Rar!\x1a\x07\x00"
                elif mode == "missing_end":
                    payload = valid[:-8]
                elif mode == "trailing":
                    payload = valid + b"extra"
                elif mode == "unsafe":
                    payload = stored_rar([("../escape", b"payload", False)])
                elif mode == "directory_data":
                    payload = stored_rar([("test_release", b"unexpected", True)])
                path.write_bytes(payload)
                if mode == "valid":
                    rows = job.read_file_headers(path)
                    self.assertEqual(rows[0]["crc32"], zlib.crc32(b"native"))
                    self.assertEqual(rows[0]["byte_size"], 6)
                else:
                    with self.assertRaises(ValueError):
                        job.read_file_headers(path)

    def manifest(self):
        videos, _, _ = self.population()
        rows = [dict(row, index=index, selected_frame={"decode_order": 1}, detector_status="success",
                     active_config_sha256="a" * 64, replacement=False, retain_original_denominator=True,
                     model_score=None, classifier_error=None, final_k1_action=None,
                     asset_sha256={"frame.png": "b" * 64}) for index, row in enumerate(videos)]
        rows[-1].update(selected_frame=None, detector_status="not_run", final_k1_action="non_accept", asset_sha256={})
        rows[-2].update(detector_status="failed", final_k1_action="non_accept")
        return {"videos": videos, "active_config_sha256": "a" * 64}, rows

    def test_full600_denominators_and_both_failure_types(self):
        plan, rows = self.manifest()
        self.assertEqual(job.validate_manifest(plan, rows), {
            "originals": 600, "selected": 599, "pre_detector_failure": 1,
            "detector_success": 598, "detector_failure": 1})
        for mode in ("missing", "duplicate", "role", "config", "score", "failure_image", "failure_accept"):
            current = copy.deepcopy(rows)
            if mode == "missing":
                current.pop()
            elif mode == "duplicate":
                current[-1] = current[0]
            elif mode == "role":
                current[0]["role"] = "target"
            elif mode == "config":
                current[0]["active_config_sha256"] = "wrong"
            elif mode == "score":
                current[0]["model_score"] = 0.5
            elif mode == "failure_image":
                current[-1]["asset_sha256"] = {"fabricated.png": "x"}
            else:
                current[-2]["final_k1_action"] = "accept"
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                job.validate_manifest(plan, current)

    def test_real_decode_and_fixed_middle_detector_outcome(self):
        for mode in ("success", "detector_failure", "decode_failure"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                path = output / "temporary/train_release/1/1.avi"
                path.parent.mkdir(parents=True)
                if mode == "decode_failure":
                    path.write_bytes(b"invalid synthetic AVI")
                else:
                    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                                    "color=c=gray:s=112x112:r=2:d=2", "-threads", "1", "-c:v", "mpeg4",
                                    str(path)], check=True, capture_output=True)
                original = {"dataset": "CASIA-FASD", "video_id": "train_release/1/1", "role": "train",
                            "binary_label": "bona_fide", "official_split": "train", "subject_id": "subject-01",
                            "media_relpath": "train_release/1/1.avi", "byte_size": path.stat().st_size}
                plan = {"deadline_unix_seconds": time.time() + 60,
                        "active_config_sha256": job.sha(job.shared.images.ACTIVE)}
                job.write(output / "release_integrity.json", {"video_payload_pins": {
                    original["media_relpath"]: {"sha256": job.sha(path), "byte_size": path.stat().st_size}}})
                with patch.object(job, "OUTPUT", output), patch.object(job.shared, "OUTPUT", output), \
                        patch("fas.preprocessing.detect_face", return_value=(np.array([10, 10, 110, 110, 0.9]), REFERENCE_112),
                              side_effect=ValueError("no_face_above_frozen_threshold") if mode == "detector_failure" else None):
                    row, media = job.produce_unit(plan, 0, original, Mock())
                    if mode == "decode_failure":
                        self.assertIsNone(row["selected_frame"])
                        self.assertEqual(row["detector_status"], "not_run")
                        self.assertEqual(row["final_k1_action"], "non_accept")
                    else:
                        self.assertEqual(row["selected_frame"]["decode_order"], 1)
                        self.assertEqual(media["frame_count"], 4)
                        self.assertEqual(row["detector_status"], "failed" if mode == "detector_failure" else "success")
                        transaction = job.shared.technical_transaction(media)
                        transaction.update(media_sha256=media["media_sha256"], media_record_sha256=row["media_record_sha256"])
                        _, assets = job.shared.images.validate_unit(
                            {"transaction": transaction, "media_path": str(output / "media/0000.json")},
                            output, 0, 4, plan["active_config_sha256"])
                        self.assertEqual(len(assets), 1 if mode == "detector_failure" else 4)

    def test_fixed_visuals_cover_quality_role_class_subtypes_before_outcomes(self):
        videos, _, _ = self.population()
        indices = job.fixed_indices(videos)
        self.assertTrue(set(range(0, 600, 20)) <= set(indices))
        strata = {(row["role"], row["binary_label"], row["quality"], row["reference_attack_type"]) for row in videos}
        self.assertEqual({(videos[index]["role"], videos[index]["binary_label"], videos[index]["quality"],
                           videos[index]["reference_attack_type"]) for index in indices}, strata)
        self.assertEqual(indices, job.fixed_indices([dict(row, detector_status="failed") for row in videos]))

    def verifier_fixture(self, output):
        videos, _, headers = self.population()
        plan = {"videos": videos, "sources": {}, "active_config_sha256": job.sha(job.shared.images.ACTIVE),
                "visual_indices": [0, 20], "archive_identity": [1, 2, 3, 4, 5],
                "crc_headers": [dict(row, crc32=123) for row in headers],
                "deadline_unix_seconds": time.time() + 60}
        pins, media_rows = {}, []
        for index, original in enumerate(videos):
            media = {key: original[key] for key in ("video_id", "role", "binary_label", "official_split", "subject_id", "media_relpath", "byte_size")}
            media.update(media_sha256=hashlib.sha256(original["video_id"].encode()).hexdigest(),
                         archive_crc_validated=True, decode_status="failed", frame_count=0, frame_index=[],
                         decoded_rgb_sequence_sha256=None, failure_reason="synthetic technical failure")
            media_path = output / "media" / f"{index:04d}.json"
            job.write(media_path, media)
            transaction = job.shared.technical_transaction(media)
            transaction.update(media_sha256=media["media_sha256"], media_record_sha256=job.sha(media_path))
            job.write(output / "transactions" / f"{index:04d}.json",
                      dict(transaction, index=index, config_sha256=plan["active_config_sha256"],
                           model_sha256=job.shared.MODEL_SHA256, assets={}, replacement=False))
            job.write(output / "attempts" / f"{index:04d}.json",
                      {"index": index, "video_id": original["video_id"], "role": original["role"], "status": "started"})
            pins[original["media_relpath"]] = {"crc32": 123, "sha256": media["media_sha256"], "byte_size": media["byte_size"]}
            media_rows.append(media)
        total_bytes = sum(row["byte_size"] for row in videos)
        job.write(output / "content_checks.json", {"exact_groups": [], "forbidden_exact_crossings": 0})
        job.write(output / "worker_completion.json", {
            "transactions": 600, "video_crc_checked": 600, "native_frames": 0, "video_payload_bytes": total_bytes,
            "provider": ["CPUExecutionProvider"], "gpu_seconds": 0, "model_scores": 0, "fitted_scores": 0})
        (output / "extraction.stderr").write_bytes(b"")
        job.write(output / "release_integrity.json", {
            "archive_identity": plan["archive_identity"], "archive_bytes": 3, "extracted_videos": 600,
            "video_payload_bytes": total_bytes, "extractor_returncode": 0, "extractor_stderr_bytes": 0,
            "independent_unpacked_crc32_verified": True, "extractor_stderr_sha256": job.sha(output / "extraction.stderr"),
            "video_payload_pins": pins})
        (output / "temporary").mkdir()
        return plan

    def test_whole600_readback_rejects_partial_or_orphaned_or_changed_evidence(self):
        for mode in ("success", "missing", "orphan", "attempt_drift", "crc_drift", "completion", "stderr", "temporary"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                plan = self.verifier_fixture(output)
                if mode == "missing":
                    (output / "transactions/0599.json").unlink()
                elif mode == "orphan":
                    (output / "frames").mkdir()
                    (output / "frames/orphan.png").write_bytes(b"unexpected")
                elif mode == "attempt_drift":
                    (output / "attempts/0000.json").write_text("{}")
                elif mode == "crc_drift":
                    plan["crc_headers"][-1]["crc32"] = 124
                elif mode == "completion":
                    value = job.read(output / "worker_completion.json")
                    value["video_crc_checked"] = 599
                    (output / "worker_completion.json").write_text(json.dumps(value))
                elif mode == "stderr":
                    (output / "extraction.stderr").write_bytes(b"diagnostic")
                elif mode == "temporary":
                    (output / "temporary/unremoved").write_bytes(b"payload")
                with patch.object(job, "OUTPUT", output), patch.object(job.shared, "OUTPUT", output), patch.object(job, "guard"), \
                        patch.object(job, "sha", side_effect=lambda path: job.shared.MODEL_SHA256 if path == job.shared.retained.MODEL
                                     else hashlib.sha256(path.read_bytes()).hexdigest()):
                    if mode == "success":
                        readback = job.verify(plan)
                        self.assertEqual(readback["originals"], 600)
                        self.assertEqual(readback["pre_detector_failure"], 600)
                        self.assertEqual(readback["strict_replay_count"], 0)
                        self.assertFalse(readback["visual_inspection_completed"])
                    else:
                        with self.assertRaises((ValueError, KeyError)):
                            job.verify(plan)
                        self.assertFalse((output / "readback.json").exists())

    def test_supervisor_requires_readback_and_enforces_final_caps_without_retry(self):
        for mode in ("success", "spawn", "missing_readback", "rss", "storage", "deadline"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                plan, manifest = self.manifest()
                plan.update(deadline_unix_seconds=time.time() + (60 if mode != "deadline" else -1), sources={})
                job.write(output / "plan.json", plan)
                job.write(output / "full_manifest.json", {"rows": manifest, "active_config_sha256": plan["active_config_sha256"]})
                for name in ("release_integrity", "content_checks"):
                    job.write(output / (name + ".json"), {})
                readback = {**job.validate_manifest(plan, manifest), "full_manifest_sha256": job.sha(output / "full_manifest.json"),
                            "per_unit_sha256": {}, **{name + "_sha256": job.sha(output / (name + ".json"))
                                                     for name in ("release_integrity", "content_checks")}}
                if mode != "missing_readback":
                    job.write(output / "readback.json", readback)
                owned = output / "temporary/train_release"
                owned.mkdir(parents=True)
                (owned / "owned.avi").write_bytes(b"owned")
                process = Mock(pid=424242)
                process.wait.return_value = 0
                normal = {"rss_bytes": 100, "output_bytes": 100, "temporary_bytes": 0}
                final = dict(normal)
                if mode == "rss":
                    final["rss_bytes"] = job.CAPS["rss_bytes"] + 1
                elif mode == "storage":
                    final["output_bytes"] = job.CAPS["output_bytes"] + 1
                with patch.object(job, "OUTPUT", output), patch.object(job, "guard"), patch.object(job.shared, "check_bindings"), \
                        patch.object(job, "authority", return_value={"started_unix_seconds": time.time() - 1}), \
                        patch.object(job, "sha", side_effect=lambda path: plan["active_config_sha256"] if path == job.shared.images.ACTIVE
                                     else hashlib.sha256(path.read_bytes()).hexdigest()), \
                        patch.object(job, "measured", side_effect=[normal, normal, final]), \
                        patch.object(job.subprocess, "Popen", return_value=process,
                                     side_effect=OSError("synthetic spawn failure") if mode == "spawn" else None), \
                        patch.object(job.os, "killpg"):
                    result = job.supervise(plan)
                self.assertEqual(result["completion_claimed"], mode == "success")
                self.assertEqual(result["attempts"], 1)
                self.assertFalse(result["automatic_retry"])
                self.assertFalse(owned.exists())
                if mode != "success":
                    failed = job.read(output / "failure_rows.json")["rows"]
                    self.assertEqual(len(failed), 600)
                    self.assertTrue(all(row["final_k1_action"] == "non_accept" for row in failed))

    def test_cleanup_refuses_unowned_entries_and_symlink_roots(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(job, "OUTPUT", Path(directory)):
            temporary = Path(directory) / "temporary"
            temporary.mkdir()
            sentinel = temporary / "unowned"
            sentinel.write_text("preserve")
            with self.assertRaises(ValueError):
                job.cleanup()
            self.assertTrue(sentinel.exists())
            sentinel.unlink()
            (temporary / "train_release").symlink_to(Path(directory), target_is_directory=True)
            with self.assertRaises(ValueError):
                job.cleanup()


if __name__ == "__main__":
    unittest.main()
