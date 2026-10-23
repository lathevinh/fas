import contextlib
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import preprocess_siw291 as run


class SyntheticBudget:
    def reserve(self, size):
        if type(size) is not int or size < 0:
            raise ValueError("invalid reservation")
        return contextlib.nullcontext()


def population():
    rows, roles = [], []
    names = [role for role, count in run.ROLES.items() for _ in range(count)]
    for index in range(1680):
        row = {"dataset": "SiW-Mv2", "video_id": f"fixture_{index}", "subject_id": None,
               "group_unit": "video", "group_id": f"fixture_{index}",
               "participant_identity_verified": False, "binary_label": "attack", "role": None,
               "official_split": "train" if index < 1057 else "test"}
        rows.append(row)
        if index < 1057:
            roles.append({**{k: row[k] for k in ("dataset", "video_id", "binary_label")},
                          "subject_id": "", "role": names[index]})
    return rows, roles


def rational_probe():
    frames = [{"best_effort_timestamp": order * 1001,
               "best_effort_timestamp_time": f"{float(Fraction(order * 1001, 30000)):.6f}",
               "width": 2, "height": 2, "key_frame": int(order == 0)}
              for order in range(3)]
    raw = {"streams": [{"time_base": "1/30000", "avg_frame_rate": "30000/1001",
                        "nb_frames": "3", "codec_name": "h264"}],
           "frames": frames, "format": {"format_name": "mov,mp4,m4a,3gp,3g2,mj2", "duration": "0.1001"}}
    hashes = "#tb 0: 1/30000\n#dimensions 0: 2x2\n" + "\n".join(
        f"0, {order * 1001}, {order * 1001}, 1001, 12, {'a' * 64}" for order in range(3))
    return raw, hashes


class SiWBoundaryTests(unittest.TestCase):
    def test_exact_source_roles_and_null_test_without_fabricated_subjects(self):
        rows, roles = population()
        result = run.reconcile(rows, roles)
        self.assertEqual(sum(r["role"] is None for r in result), 623)
        self.assertEqual({r["role"] for r in result if r["official_split"] == "train"}, set(run.ROLES))
        self.assertTrue(all(r["subject_id"] is None for r in result))
        self.assertTrue(all(r["role"] is None for r in rows))

    def test_target_cannot_enter_source_roles(self):
        rows, roles = population()
        roles[0]["video_id"] = rows[-1]["video_id"]
        with self.assertRaisesRegex(ValueError, "disjoint623"):
            run.reconcile(rows, roles)

    def test_duplicate_or_missing_source_roles_fail(self):
        rows, roles = population()
        with self.assertRaises(ValueError):
            run.reconcile(rows, roles[:-1])
        with self.assertRaises(ValueError):
            run.reconcile(rows, roles + [roles[0]])

    def test_subject_identity_must_stay_unknown(self):
        rows, roles = population()
        rows[0]["subject_id"] = "invented"
        with self.assertRaises(ValueError):
            run.reconcile(rows, roles)

    def test_label_or_group_drift_fails(self):
        rows, roles = population()
        roles[0]["binary_label"] = "bona_fide"
        with self.assertRaises(ValueError):
            run.reconcile(rows, roles)
        rows, roles = population()
        rows[0]["group_unit"] = "subject"
        with self.assertRaises(ValueError):
            run.reconcile(rows, roles)

    def test_native_integer_time_not_rounded_decimal_is_selected(self):
        raw, hashes = rational_probe()
        result = run.parse_probe(raw, hashes)
        self.assertEqual(result["frame_index"][1]["timestamp_seconds"], "1001/30000")
        self.assertEqual(raw["frames"][1]["best_effort_timestamp_time"], "0.033367")
        self.assertEqual(result["timestamp_transport"], "native_integer_ticks_preserved_encoder_timebase")
        self.assertIsNone(result["native_count_accounting"])

    def test_timestamp_disagreement_or_missing_ticks_does_not_use_casia_repair(self):
        raw, hashes = rational_probe()
        raw["frames"][-1].pop("best_effort_timestamp")
        with self.assertRaisesRegex(run.strict.ProbeFailure, "best_effort_timestamp"):
            run.parse_probe(raw, hashes)
        raw, hashes = rational_probe()
        raw["frames"][1]["best_effort_timestamp_time"] = "0.133367"
        with self.assertRaisesRegex(run.strict.ProbeFailure, "disagreement"):
            run.parse_probe(raw, hashes)

    def test_declared_count_mismatch_does_not_use_casia_vop_accounting(self):
        raw, hashes = rational_probe()
        raw["streams"][0]["nb_frames"] = "4"
        with self.assertRaisesRegex(run.strict.ProbeFailure, "declared_frame_count_mismatch"):
            run.parse_probe(raw, hashes)

    def test_framehash_time_and_rgb_bytes_are_checked(self):
        raw, hashes = rational_probe()
        with self.assertRaises(run.strict.ProbeFailure):
            run.parse_probe(raw, hashes.replace(", 12,", ", 13,"))
        with self.assertRaises(run.strict.ProbeFailure):
            run.parse_probe(raw, hashes.replace("0, 1001, 1001,", "0, 1001, 1002,"))
        with self.assertRaisesRegex(run.strict.ProbeFailure, "dimensions disagree"):
            run.parse_probe(raw, hashes.replace("2x2", "1x4"))

    def test_test_transaction_is_not_a_source_or_fit_candidate(self):
        raw, hashes = rational_probe()
        media = {**run.parse_probe(raw, hashes), "video_id": "fixture", "binary_label": "attack",
                 "official_split": "test", "role": None}
        row = run.transaction(media)
        self.assertIsNone(row["role"])
        self.assertEqual(row["selected_frame"]["decode_order"], 1)
        self.assertEqual(row["score_fit_status"], "not_authorized_test_preparation_only")
        media["role"] = "train"
        with self.assertRaisesRegex(ValueError, "null role"):
            run.transaction(media)

    def test_exact_member_eof_crc_sha_and_byte_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "fixture.zip"
            payload = b"synthetic zip payload"
            with zipfile.ZipFile(archive, "w") as out:
                out.writestr("clip.mov", payload)
            with zipfile.ZipFile(archive) as source:
                pin = run.copy_member(source, source.getinfo("clip.mov"), root / "copy.mov",
                                      len(payload), float("inf"))
                self.assertEqual(pin["sha256"], hashlib.sha256(payload).hexdigest())
                with self.assertRaises(ValueError):
                    run.copy_member(source, source.getinfo("clip.mov"), root / "bad.mov",
                                    len(payload) - 1, float("inf"))
                with self.assertRaises(TimeoutError):
                    run.copy_member(source, source.getinfo("clip.mov"), root / "late.mov",
                                    len(payload), 0)

    def test_supervisor_failure_keeps_denominator_and_never_retries(self):
        self._supervisor_failure(final_scan=False)

    def test_failed_final_scan_is_a_durable_failure_not_success(self):
        self._supervisor_failure(final_scan=True)

    def _supervisor_failure(self, final_scan):
        from unittest.mock import Mock
        rows, roles = population()
        plan = {"videos": run.reconcile(rows, roles), "sources": {},
                "excluded_originals": 20, "missing_references": 11}
        with tempfile.TemporaryDirectory() as directory:
            output, ipc = Path(directory) / "out", Path(directory) / "ipc"
            for folder in ("temporary", "transactions", "attempts", "probe"):
                (output / folder).mkdir(parents=True)
            ipc.mkdir()
            (ipc / "snapshot.json").write_text("{}")
            (output / "plan.json").write_text(json.dumps(plan))
            (output / "attempts/0000.json").write_text("{}")
            readback = {"selected": 1680, "detector_success": 1680, "detector_failure": 0,
                        "pre_detector_failure": 0, "native_frames": 1680, "strict_replay_count": 1680,
                        "image_assets": 6720}
            (output / "readback.json").write_text(json.dumps(readback))
            scanner = Mock(pid=990001)
            scanner.poll.return_value = None
            worker, verifier = Mock(pid=990002), Mock(pid=990003)
            worker.wait.return_value = 0 if final_scan else 1
            verifier.wait.return_value = 0
            client = Mock()
            client.measure.return_value = {"rss_bytes": 1, "output_bytes": 1, "temporary_bytes": 0}
            with (patch.object(run, "OUTPUT", output), patch.object(run, "IPC", ipc),
                  patch.object(run, "SUMMARY", Path(directory) / "public.json"),
                  patch.object(run, "authority", return_value={"started_unix_seconds": 0,
                                                              "deadline_unix_seconds": float("inf")}),
                  patch.object(run, "guard"), patch.object(run, "enforce"),
                  patch.object(run.budget, "initialize"), patch.object(run.budget, "publish"),
                  patch.object(run.budget, "Client", return_value=client),
                  patch.object(run.budget, "stop_group"),
                  patch.object(run.budget, "scan_once", side_effect=OSError("specific final scan failure")),
                  patch.object(run.subprocess, "Popen", side_effect=[scanner, worker, verifier]) as spawn,
                  patch.object(run.signal, "setitimer"), patch.object(run.shared.retained, "arm_deadline")):
                result = run.supervise(plan)
            self.assertFalse(result["accounting_complete"])
            self.assertFalse(result["automatic_retry"])
            self.assertEqual(spawn.call_count, 3 if final_scan else 2)
            if final_scan:
                self.assertIn("specific final scan failure", result["failure"])
            ledger = json.loads((output / "failure_rows.json").read_text())
            self.assertEqual(len(ledger["rows"]), 1680)
            self.assertEqual(ledger["status_counts"], {"interrupted_before_commit": 1, "not_started": 1679})


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "installed synthetic FFmpeg required")
class SiWRealTransportTests(unittest.TestCase):
    def test_corrupt_member_retains_exact_failed_probe_and_no_invented_pixels(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "probe"
            clip = root / "bad.avi"
            clip.write_bytes(b"synthetic invalid media, not a real participant")
            with (patch.object(run, "CLIENT", SyntheticBudget()),
                  patch.object(run.strict, "measured", return_value={}),
                  patch.object(run.strict.diagnosis, "enforce")):
                result = run.probe(clip, folder)
            self.assertEqual(result["decode_status"], "failed")
            self.assertEqual(result["frame_count"], 0)
            self.assertEqual(result["frame_index"], [])
            self.assertIn("strict_exit_", result["failure_reason"])
            self.assertTrue((folder / "metadata.stderr").stat().st_size)
            self.assertEqual(result["probe_failure"], json.loads((folder / "failure.json").read_text()))
            row = run.transaction({**result, "video_id": "fixture", "official_split": "test",
                                   "role": None, "binary_label": "attack"})
            self.assertEqual(row["final_k1_action"], "non_accept")
            self.assertIsNone(row["selected_frame"])
            self.assertIsNone(row["role"])
            self.assertIsNone(row["model_score"])

    def test_mov_mp4_avi_native_ticks_replay_png_and_target_readback(self):
        import numpy as np
        for extension, encoder in (
                (".mp4", ["-c:v", "libx264", "-bf", "2", "-pix_fmt", "yuv420p"]),
                (".mov", ["-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le"]),
                (".avi", ["-c:v", "ffv1"])):
            with self.subTest(extension=extension), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                clip = root / ("synthetic" + extension)
                subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                                "testsrc2=size=128x96:rate=30000/1001", "-frames:v", "8",
                                "-threads", "1", *encoder, str(clip)], check=True, capture_output=True)
                archive_path = root / "fixture.zip"
                member = "SiW-Mv2/Live/Live_1" + extension
                with zipfile.ZipFile(archive_path, "w") as archive:
                    archive.write(clip, member)
                output = root / "output"
                for folder in ("temporary", "probe", "media", "attempts", "transactions", "frames", "crops", "replay"):
                    (output / folder).mkdir(parents=True)
                original = {"dataset": "SiW-Mv2", "video_id": "Live_1", "role": None,
                            "official_split": "test", "binary_label": "bona_fide", "subject_id": None,
                            "media_relpath": member, "byte_size": clip.stat().st_size}
                plan = {"videos": [original], "headers": run.native.read_headers(archive_path),
                        "deadline_unix_seconds": float("inf"), "active_config_sha256": "0" * 64}
                box = np.asarray([10., 5., 110., 85., .99])
                landmarks = np.asarray([[40., 30.], [80., 30.], [60., 45.], [45., 60.], [75., 60.]])
                with (patch.object(run, "OUTPUT", output), patch.object(run.shared, "OUTPUT", output),
                      patch.object(run, "CLIENT", SyntheticBudget()),
                      patch.object(run.strict, "measured", return_value={}),
                      patch.object(run.strict.diagnosis, "enforce"),
                      patch.object(run.shared.images, "ROLE_COUNTS", {**run.ROLES, None: 623}),
                      patch("fas.preprocessing.detect_face", return_value=(box, landmarks)),
                      zipfile.ZipFile(archive_path) as archive):
                    row, media = run.unit(plan, 0, archive, object())
                    self.assertEqual(media["frame_count"], 8)
                    self.assertEqual(row["selected_frame"]["decode_order"], 3)
                    self.assertIsNone(row["role"])
                    self.assertEqual(row["detector_status"], "success")
                    self.assertEqual(len(row["assets"]), 3)
                    self.assertEqual(list((output / "temporary").iterdir()), [])
                    run.verify_probe(0, media)
                    txn = run.transaction(media)
                    txn.update(media_sha256=media["media_sha256"],
                               media_record_sha256=run.sha(output / "media/0000.json"))
                    entry, assets = run.shared.images.validate_unit(
                        {"transaction": txn, "media_path": str(output / "media/0000.json")},
                        output, 0, 4, "0" * 64)
                    self.assertIsNone(entry["role"])
                    self.assertEqual(len(assets), 4)
                    path = output / "probe/0000/result.json"
                    path.write_text("{}")
                    with self.assertRaisesRegex(ValueError, "probe commitment"):
                        run.verify_probe(0, media)


if __name__ == "__main__":
    unittest.main()
