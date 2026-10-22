"""Additional authority and original-byte-preserving MSU recovery staging."""

import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch
import zipfile

import numpy as np

import test_msu_preprocessing as original
import diagnose_msu282_recovery as recovery
import recover_msu282 as runner
from msu_replay282 import replay_command, strict_replay
from fas.preprocessing import REFERENCE_112


class MsuRecoveryTest(unittest.TestCase):
    def test_staging_reuses_exact_prior_volume_digests_and_rejects_drift(self):
        for changed in (False, True):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                inputs, output, plan, raw = original.MsuPackageTest().transport(root)
                prior = root / "prior"
                prior.mkdir()
                volumes = []
                for outer in sorted(inputs.glob("*.zip")):
                    with zipfile.ZipFile(outer) as archive:
                        for entry in archive.infolist():
                            if ".zip." in entry.filename:
                                data = archive.read(entry)
                                volumes.append({"volume": int(entry.filename.rsplit(".", 1)[1]),
                                                "byte_size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
                volumes.sort(key=lambda row: row["volume"])
                if changed:
                    volumes[0]["sha256"] = "0" * 64
                recovery.job.write_immutable_record(prior / "release_integrity.json", {
                    "volumes": volumes, "joined_zip_bytes": len(raw)})
                metadata = {key: hashlib.sha256(b"synthetic native text").hexdigest() for key in recovery.job.METADATA_SHA256}
                with patch.object(recovery, "OUTPUT", output), patch.object(recovery, "PRIOR", prior), \
                        patch.object(recovery.job, "INPUT", inputs), patch.object(recovery.job, "METADATA_SHA256", metadata):
                    if changed:
                        with self.assertRaisesRegex(ValueError, "volume SHA"):
                            recovery.stage(plan)
                        self.assertFalse((output / "stage.json").exists())
                    else:
                        result = recovery.stage(plan)
                        self.assertEqual(result.read_bytes(), raw)
                        receipt = recovery.job.read_json(output / "stage.json")
                        self.assertFalse(receipt["original_archive_rehash"])
                        self.assertEqual(len(receipt["volumes"]), 16)

    def test_exact_additional_approval_and_caps_required(self):
        for valid in (False, True):
            with self.subTest(valid=valid), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                recovery.job.write_immutable_record(output / "owner_approval.json", {
                    "selected_answer": recovery.APPROVAL if valid else "continue",
                    "explicit_owner_approval": True, "caps": recovery.job.CAPS})
                with patch.object(recovery, "OUTPUT", output):
                    if valid:
                        self.assertEqual(recovery.authority()["selected_answer"], recovery.APPROVAL)
                    else:
                        with self.assertRaises(ValueError):
                            recovery.authority()

    def test_provisional_output_reuse_reconstructs_pixels_without_inference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prior, output = root / "prior", root / "recovery"
            (prior / "temporary").mkdir(parents=True)
            output.mkdir()
            source = root / "fixture.mp4"
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                            "color=c=gray:s=112x112:r=2:d=2", "-threads", "1", "-c:v", "mpeg4",
                            str(source)], check=True, capture_output=True)
            archive_path = root / "fixture.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.write(source, "fixture.mp4")
            with zipfile.ZipFile(archive_path) as archive:
                original_row = {"dataset": "MSU-MFSD", "video_id": "fixture", "role": "branch_calibration",
                                "binary_label": "attack", "official_split": "train", "subject_id": "subject-001",
                                "media_relpath": "fixture.mp4",
                                "archive_header": recovery.job.native.header_record(archive.getinfo("fixture.mp4"))}
                plan = {"active_config_sha256": recovery.job._sha256(recovery.job.images.ACTIVE),
                        "deadline_unix_seconds": time.time() + 60, "videos": [original_row]}
                with patch.object(recovery.job, "OUTPUT", prior), \
                        patch("fas.preprocessing.detect_face", return_value=(np.array([10, 10, 110, 110, 0.9]), REFERENCE_112)):
                    row, media = recovery.job.produce_unit(plan, 0, original_row, archive, Mock())
            plan["sources"] = {str(path): recovery.job._sha256(path) for path in prior.rglob("*") if path.is_file()}
            with patch.object(runner, "PRIOR", prior), patch.object(runner, "OUTPUT", output), \
                    patch("fas.preprocessing.detect_face", side_effect=AssertionError("reuse must not infer")):
                actual, reused_media = runner.reuse_unit(plan, 0)
            self.assertEqual(actual, row)
            self.assertEqual(reused_media, media)
            for path in output.rglob("*"):
                if path.is_file():
                    self.assertEqual(path.read_bytes(), (prior / path.relative_to(output)).read_bytes())

    def test_recovery_supervisor_missing_readback_caps_and_cleanup(self):
        for mode in ("success", "missing_readback", "rss", "storage"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                with patch.object(runner, "OUTPUT", output), patch.object(recovery.job, "OUTPUT", output):
                    plan, readback = original.MsuPackageTest().supervisor_fixture(output)
                    if mode != "missing_readback":
                        recovery.job.write_immutable_record(output / "readback.json", readback)
                    recovery.job.write_immutable_record(output / "replay_readback.json", {"record_sha256": {}})
                    recovery.job.write_immutable_record(output / "diagnosis_resources.json", {
                        "sampled_peaks": {"rss_bytes": 100, "output_bytes": 100, "temporary_bytes": 0}})
                    (output / "temporary").mkdir()
                    (output / "temporary/MSU-MFSD-Publish.zip").write_bytes(b"owned")
                    normal = {"rss_bytes": 100, "output_bytes": 100, "temporary_bytes": 0}
                    final = dict(normal)
                    if mode == "rss":
                        final["rss_bytes"] = recovery.job.CAPS["rss_bytes"] + 1
                    elif mode == "storage":
                        final["output_bytes"] = recovery.job.CAPS["output_bytes"] + 1
                    process = Mock(pid=424242)
                    process.wait.return_value = 0
                    with patch.object(runner.subprocess, "Popen", return_value=process), \
                            patch.object(recovery.job, "check_bindings"), patch.object(recovery.job, "archive_guard"), \
                            patch.object(runner, "measured", side_effect=[normal, normal, final]), \
                            patch.object(recovery, "authority", return_value={"started_unix_seconds": time.time()}), \
                            patch.object(runner.os, "killpg"):
                        result = runner.supervise(plan)
                    self.assertEqual(result["completion_claimed"], mode == "success")
                    self.assertFalse((output / "temporary/MSU-MFSD-Publish.zip").exists())

    def test_replay_checks_every_rgb_eof_exit_stderr_and_preserves_diagnostics(self):
        frames = [bytes([index + 1] * 12) for index in range(4)]
        media = {
            "decode_status": "decoded", "frame_count": 4, "decoded_rgb_sequence_sha256": "a" * 64,
            "frame_index": [{"decode_order": index, "timestamp_seconds": str(index), "decode_success": True,
                             "width": 2, "height": 2, "rgb_sha256": hashlib.sha256(frame).hexdigest()}
                            for index, frame in enumerate(frames)]}
        for mode in ("success", "stderr", "exit", "missing", "extra", "corrupt", "deadline"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                payload = b"".join(frames)
                if mode == "missing":
                    payload = payload[:-1]
                elif mode == "extra":
                    payload += b"x"
                elif mode == "corrupt":
                    payload = b"x" + payload[1:]
                code = f"import sys,time; sys.stdout.buffer.write({payload!r});sys.stdout.flush();"
                if mode == "stderr":
                    code += "sys.stderr.write('retained decoder error');"
                elif mode == "exit":
                    code += "sys.exit(7);"
                elif mode == "deadline":
                    code += "time.sleep(10);"
                receipt = Path(directory) / "0004"
                seen = []
                call = lambda: strict_replay(Path("unused"), media, lambda order, rgb: seen.append(order), receipt,
                                             command=[sys.executable, "-c", code],
                                             timeout=0.1 if mode == "deadline" else 10)
                if mode == "success":
                    call()
                    self.assertEqual(seen, [0, 1, 2, 3])
                else:
                    with self.assertRaises((ValueError, TimeoutError)):
                        call()
                record = recovery.job.read_json(receipt.with_suffix(".json"))
                self.assertEqual(record["strict_success"], mode == "success")
                if mode == "stderr":
                    self.assertEqual(receipt.with_suffix(".stderr").read_text(), "retained decoder error")
                    self.assertEqual(record["returncode"], 0)
                elif mode == "exit":
                    self.assertEqual(record["returncode"], 7)

    def test_source_timebase_prevents_raw_muxer_dts_collision_without_changing_rgb(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "fractional.mov"
            subprocess.run([
                "ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i", "testsrc2=s=112x112:r=30:d=1",
                "-vf", r"settb=1/30000,setpts=if(eq(N\,2)\,1440\,N*1000)",
                "-threads", "1", "-c:v", "prores_ks", "-profile:v", "0", "-vsync", "0",
                "-enc_time_base", "1:30000", "-video_track_timescale", "30000", str(source),
            ], check=True, capture_output=True)
            media = recovery.job.probe_video(source)
            self.assertEqual(media["decode_status"], "decoded")
            command = replay_command(source)
            offset = command.index("-enc_time_base")
            original_command = command[:offset] + command[offset + 2:]
            with self.assertRaisesRegex(ValueError, "stderr_bytes"):
                strict_replay(source, media, lambda order, rgb: None, root / "before", command=original_command)
            self.assertIn("non monotonically increasing dts", (root / "before.stderr").read_text())
            seen = []
            strict_replay(source, media, lambda order, rgb: seen.append(order), root / "after")
            result = recovery.job.read_json(root / "after.json")
            self.assertEqual(seen, list(range(media["frame_count"])))
            self.assertEqual(result["frames_verified"], media["frame_count"])
            self.assertTrue(result["strict_success"])
            self.assertEqual(result["stderr_bytes"], 0)

    def test_recovery_verifier_requires_complete_strict_replay_and_exact_diagnostics(self):
        for mode in ("success", "missing", "bad_exit", "bad_count", "orphan", "stderr"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                for index in range(4, 280):
                    recovery.job.write_immutable_record(output / "transactions" / f"{index:04d}.json",
                                                        {"selected_frame": None})
                replay_dir = output / "replay"
                replay_dir.mkdir()
                error_path = replay_dir / "0004.stderr"
                error_path.write_bytes(b"bad" if mode == "stderr" else b"")
                receipt = {
                    "strict_success": True, "frames_verified": 301 if mode != "bad_count" else 300,
                    "frame_count": 301, "decoded_rgb_sequence_sha256": "a" * 64,
                    "returncode": 0 if mode != "bad_exit" else 1, "stderr_bytes": 0, "failure": None,
                    "frame_substitution": False, "stderr_sha256": hashlib.sha256(b"").hexdigest()}
                if mode != "missing":
                    recovery.job.write_immutable_record(replay_dir / "0004.json", receipt)
                transaction = output / "transactions/0004.json"
                transaction.unlink()
                recovery.job.write_immutable_record(transaction, {
                    "selected_frame": {"decode_order": 150},
                    "replay_record_sha256": recovery.job._sha256(replay_dir / "0004.json") if mode != "missing" else "f" * 64})
                recovery.job.write_immutable_record(output / "media/0004.json", {
                    "frame_count": 301, "decoded_rgb_sequence_sha256": "a" * 64})
                recovery.job.write_immutable_record(output / "readback.json", {})
                if mode == "orphan":
                    (replay_dir / "orphan.json").write_text("{}")
                with patch.object(runner, "OUTPUT", output), patch.object(recovery.job, "verify", return_value={"ok": True}):
                    if mode == "success":
                        self.assertTrue(runner.verify({})["ok"])
                        self.assertEqual(recovery.job.read_json(output / "replay_readback.json")["strict_replay_count"], 1)
                    else:
                        with self.assertRaises((ValueError, FileNotFoundError)):
                            runner.verify({})
                        self.assertFalse((output / "replay_readback.json").exists())


if __name__ == "__main__":
    unittest.main()
