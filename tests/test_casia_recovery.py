"""Actual AVI/B-frame transport regression and strict native-clock refusal cases."""

import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import casia_probe287 as probe
import casia_counts287 as counts
from fas.media import probe_video as legacy_probe
from msu_replay282 import strict_replay


class CasiaRecoveryTest(unittest.TestCase):
    def evidence(self):
        frames = [{"width": 8, "height": 8, "key_frame": int(index == 0), "coded_picture_number": index,
                   "pkt_pos": str((index + 1) * 100), "pkt_size": "10", "pict_type": "P",
                   **({"best_effort_timestamp_time": str((index + 1) / 25)} if index != 2 else {})}
                  for index in range(3)]
        raw = {"streams": [{"codec_name": "mpeg4", "avg_frame_rate": "25/1", "has_b_frames": 1,
                             "time_base": "1/25", "nb_frames": "3"}],
               "format": {"format_name": "avi", "duration": "0.12"}, "frames": frames}
        generated = copy.deepcopy(raw)
        generated["frames"][-1]["best_effort_timestamp_time"] = "0.12"
        packets = {"streams": copy.deepcopy(raw["streams"]),
                   "packets": [{"dts": index, "dts_time": str(index / 25), "duration": 1, "pos": str((index + 1) * 100)}
                               for index in range(3)]}
        framehash = "#tb 0: 1/25\n" + "\n".join(f"0,{index + 1},{index + 1},1,192,{hashlib.sha256(str(index).encode()).hexdigest()}" for index in range(3))
        return raw, packets, generated, framehash

    def test_exact_legacy_keyerror_shape_then_guarded_native_clock_correction(self):
        raw, packets, generated, framehash = self.evidence()
        completed = subprocess.CompletedProcess([], 0, json.dumps(raw), "")
        with patch("fas.media.subprocess.run", return_value=completed):
            failed = legacy_probe(Path("synthetic.avi"))
        self.assertEqual(failed["failure_reason"], "invalid_or_undecodable_media")
        self.assertEqual(failed["frame_count"], 0)
        with self.assertRaisesRegex(probe.ProbeFailure, "evidence_required"):
            probe.parse_evidence(raw, framehash)
        result = probe.parse_evidence(raw, framehash, packets=packets, generated=generated)
        self.assertEqual(result["frame_count"], 3)
        self.assertEqual(result["frame_index"][-1]["timestamp_seconds"], "3/25")
        self.assertEqual(result["original_missing_timestamp_orders"], [2])
        self.assertEqual(result["frame_index"][1]["rgb_sha256"], hashlib.sha256(b"1").hexdigest())

    def test_refuses_missing_or_nonmonotone_native_clock_or_changed_frames(self):
        for mode in ("missing_dts", "nonmonotone", "duration", "packet_count", "packet_identity",
                     "unsupported_gap", "old_pts_changed", "made_up_pts", "metadata_changed",
                     "missing_generated_pts", "wrong_frame_count", "bad_rgb_bytes", "bad_hash",
                     "hash_pts", "nonmonotone_metadata"):
            raw, packets, generated, framehash = self.evidence()
            if mode == "missing_dts":
                packets["packets"][-1].pop("dts")
            elif mode == "nonmonotone":
                packets["packets"][-1].update(dts=1, dts_time="0.04")
            elif mode == "duration":
                packets["packets"][-1]["duration"] = 0
            elif mode == "packet_count":
                packets["packets"].pop()
            elif mode == "packet_identity":
                packets["packets"][-1]["pos"] = "999"
            elif mode == "unsupported_gap":
                raw["frames"][0].pop("best_effort_timestamp_time")
            elif mode == "old_pts_changed":
                raw["frames"][0]["best_effort_timestamp_time"] = "0.041"
            elif mode == "made_up_pts":
                generated["frames"][-1]["best_effort_timestamp_time"] = "0.13"
            elif mode == "metadata_changed":
                generated["frames"][1]["coded_picture_number"] = 99
            elif mode == "missing_generated_pts":
                generated["frames"][-1].pop("best_effort_timestamp_time")
            elif mode == "wrong_frame_count":
                raw["streams"][0]["nb_frames"] = "4"
            elif mode == "bad_rgb_bytes":
                framehash = framehash.replace(",192,", ",191,", 1)
            elif mode == "bad_hash":
                framehash = framehash.replace(hashlib.sha256(b"1").hexdigest(), "z" * 64)
            elif mode == "hash_pts":
                framehash = framehash.replace("0,1,1,1,", "0,1,0,1,", 1)
            else:
                raw["frames"][1]["best_effort_timestamp_time"] = "0.00"
            with self.subTest(mode=mode), self.assertRaises(probe.ProbeFailure):
                probe.parse_evidence(raw, framehash, packets=packets, generated=generated)

    def test_generated_pts_cannot_replace_any_existing_native_timestamp(self):
        raw, packets, generated, framehash = self.evidence()
        generated["frames"][0]["best_effort_timestamp_time"] = "0.02"
        result = probe.parse_evidence(raw, framehash, packets=packets, generated=generated)
        self.assertEqual(result["frame_index"][0]["timestamp_seconds"], "1/25")
        self.assertEqual(result["ignored_generated_existing_timestamp_changes"], [0])

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "existing FFmpeg required")
    def test_actual_avi_bframes_keep_every_rgb_and_fixed_middle_with_durable_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "bframes.avi"
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                            "testsrc2=size=64x64:rate=25:duration=1", "-c:v", "mpeg4",
                            "-bf", "2", "-g", "12", "-threads", "1", str(source)],
                           check=True, capture_output=True)
            with patch.object(probe.diagnosis, "enforce"), patch.object(probe, "measured", return_value={
                    "rss_bytes": 100, "output_bytes": 100, "temporary_bytes": 0}):
                result = probe.probe_video(source, root / "evidence")
            self.assertEqual(result["decode_status"], "decoded", result)
            self.assertEqual(result["frame_count"], 25)
            self.assertEqual(result["failure_reason"], None)
            selected = (result["frame_count"] - 1) // 2
            observed = []
            strict_replay(source, result, lambda order, rgb: observed.append(hashlib.sha256(rgb.tobytes()).hexdigest())
                          if order == selected else None, root / "replay")
            self.assertEqual(observed, [result["frame_index"][selected]["rgb_sha256"]])
            self.assertTrue((root / "evidence/native-framehash.stderr").is_file())
            self.assertEqual((root / "evidence/native-framehash.stderr").stat().st_size, 0)
            self.assertEqual(result["probe_result_sha256"], probe.prior.sha(root / "evidence/probe_result.json"))

    def test_command_failure_is_specific_and_raw_diagnostics_are_retained(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(probe.diagnosis, "enforce"), patch.object(probe, "measured", return_value={
                    "rss_bytes": 100, "output_bytes": 100, "temporary_bytes": 0}):
                result = probe.probe_video(root / "absent.avi", root / "evidence")
            self.assertEqual(result["decode_status"], "failed")
            self.assertEqual(result["probe_failure"]["stage"], "original-metadata")
            self.assertTrue((root / "evidence/original-metadata.json").is_file())
            self.assertGreater((root / "evidence/original-metadata.stderr").stat().st_size, 0)
            self.assertIsNone(result["decoded_rgb_sequence_sha256"])

    def count_fixture(self, path):
        def packed(bits):
            bits += "0" * ((-len(bits)) % 8)
            return int(bits, 2).to_bytes(len(bits) // 8, "big")

        vol = b"\x00\x00\x01\x20" + packed("0" + format(17, "08b") + "0" + "0001" + "0" + "00" + "1" + format(25, "016b") + "1")
        data, packets = bytearray(512), []
        for order in range(4):
            coded = order != 1
            payload = b"\x00\x00\x01\xb6" + packed("01" + "0" + "1" + format(order, "05b") + "1" + str(int(coded)))
            pos = (order + 1) * 100
            data[pos:pos + len(payload)] = payload
            packets.append({"pos": str(pos), "size": str(len(payload)), "dts": order,
                            "dts_time": str(order / 25), "duration": 1})
        path.write_bytes(data)
        raw, _, generated, framehash = self.evidence()
        raw["streams"][0].update(nb_frames="4", extradata=f"\n00000000: {vol.hex()}  header\n", extradata_size=len(vol))
        raw["format"]["duration"] = "0.16"
        for frame, pos in zip(raw["frames"], (100, 300, 400), strict=True):
            frame["pkt_pos"] = str(pos)
        raw["frames"][1]["best_effort_timestamp_time"] = "0.12"
        generated = copy.deepcopy(raw)
        generated["frames"][-1]["best_effort_timestamp_time"] = "0.16"
        packet_data = {"streams": copy.deepcopy(raw["streams"]), "packets": packets}
        framehash = "#tb 0: 1/25\n" + "\n".join(
            f"0,{pts},{pts},1,192,{hashlib.sha256(str(index).encode()).hexdigest()}"
            for index, pts in enumerate((1, 3, 4)))
        return raw, packet_data, generated, framehash

    def test_every_declared_sample_reconciles_without_dropping_or_inventing_picture(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "packet-fixture.bin"
            raw, packets, generated, framehash = self.count_fixture(source)
            evidence = counts.build(source, raw, packets)
            result = probe.parse_evidence(raw, framehash, packets=packets, generated=generated, count_evidence=evidence)
            self.assertEqual(result["frame_count"], 3)
            self.assertEqual(result["native_count_accounting"], {
                "declared_timing_samples": 4, "native_packets": 4, "decoded_pictures": 3,
                "explicit_non_coded_vops": 1, "non_coded_vop_native_dts": [1], "all_declared_samples_accounted": True})
            self.assertEqual([row["timestamp_seconds"] for row in result["frame_index"]], ["1/25", "3/25", "4/25"])
            for mode in ("missing_coded_picture", "declared_count", "packet_identity", "coded_flag", "vol_marker", "missing_native_evidence"):
                current, native, proof = copy.deepcopy(raw), copy.deepcopy(packets), copy.deepcopy(evidence)
                if mode == "missing_coded_picture":
                    current["frames"][1]["pkt_pos"] = "200"
                elif mode == "declared_count":
                    current["streams"][0]["nb_frames"] = "5"
                elif mode == "packet_identity":
                    native["packets"][0]["pos"] = "99"
                elif mode == "coded_flag":
                    proof["packets"][1]["vop_coded"] = True
                elif mode == "vol_marker":
                    proof["codec_extradata_hex"] = "00"
                else:
                    proof = None
                with self.subTest(mode=mode), self.assertRaises(probe.ProbeFailure):
                    probe.parse_evidence(current, framehash, packets=native, generated=generated, count_evidence=proof)

    def test_worker_stops_on_three_same_failures_and_retains_not_run_denominator(self):
        import recover_casia287 as recovery

        for successful_prefix in (0, 1):
            with self.subTest(successful_prefix=successful_prefix), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                videos = [{"video_id": str(index), "role": "train", "binary_label": "bona_fide",
                           "subject_id": "synthetic", "official_split": "train"} for index in range(600)]
                plan = {"videos": videos, "sources": {}, "systemic_stop_consecutive": 3}
                ort = Mock()
                ort.InferenceSession.return_value.get_providers.return_value = ["CPUExecutionProvider"]

                def produce(plan, index, original, session):
                    failure = index >= successful_prefix
                    media = {"failure_reason": "frame_metadata:specific" if failure else None,
                             **({"probe_failure": {"stage": "frame_metadata", "reason": "specific"}} if failure else {})}
                    row = {"role": "train", "detector_status": "not_run" if failure else "success"}
                    probe.prior.write(output / "transactions" / f"{index:04d}.json", row)
                    return row, media

                with patch.dict(sys.modules, {"onnxruntime": ort}), patch.object(recovery, "OUTPUT", output), \
                        patch.object(recovery.prior, "OUTPUT", output), patch.object(recovery, "stage_release"), \
                        patch.object(recovery.prior, "guard"), patch.object(recovery, "produce_unit", side_effect=produce) as produce_mock:
                    with self.assertRaisesRegex(RuntimeError, "three consecutive"):
                        recovery.worker(plan)
                    recovery.failed_ledger(plan, "systemic_stop")
                self.assertEqual(produce_mock.call_count, successful_prefix + 3)
                ledger = probe.prior.read(output / "failure_rows.json")["rows"]
                self.assertEqual(len(ledger), 600)
                self.assertEqual(sum(row["execution_status"] == "not_attempted_after_stop" for row in ledger), 600 - successful_prefix - 3)
                self.assertTrue(all(row["final_k1_action"] == "non_accept" for row in ledger))

    def test_supervisor_separates_accounting_images_and_acceptance_and_enforces_caps(self):
        import recover_casia287 as recovery
        from test_casia_preprocessing import CasiaPreprocessingTest

        for mode in ("software_success", "zero_images", "missing_readback", "spawn", "rss", "storage", "deadline"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                plan, rows = CasiaPreprocessingTest().manifest()
                plan["sources"] = {}
                if mode == "zero_images":
                    for row in rows:
                        row.update(selected_frame=None, detector_status="not_run", final_k1_action="non_accept", asset_sha256={})
                probe.prior.write(output / "plan.json", plan)
                probe.prior.write(output / "full_manifest.json", {"rows": rows})
                readback = {**probe.prior.validate_manifest(plan, rows), "per_unit_sha256": {}, "asset_sha256": {},
                            "full_manifest_sha256": probe.prior.sha(output / "full_manifest.json"),
                            "native_frames": 0, "strict_replay_count": 0}
                if mode != "missing_readback":
                    probe.prior.write(output / "readback.json", readback)
                probe.prior.write(output / "probe_readback.json", {"per_probe_sha256": {}})
                owned = output / "temporary/train_release"
                owned.mkdir(parents=True)
                (owned / "owned.avi").write_bytes(b"owned")
                process = Mock(pid=424242)
                process.wait.return_value = 0
                normal = {"rss_bytes": 100, "output_bytes": 100, "temporary_bytes": 0}
                final = dict(normal)
                if mode == "rss":
                    final["rss_bytes"] = probe.diagnosis.CAPS["rss_bytes"] + 1
                elif mode == "storage":
                    final["output_bytes"] = probe.diagnosis.CAPS["output_bytes"] + 1
                authority = {"started_unix_seconds": time.time() - 1,
                             "deadline_unix_seconds": time.time() + (-1 if mode == "deadline" else 60)}
                with patch.object(recovery, "OUTPUT", output), patch.object(recovery, "SUMMARY", output / "public.json"), \
                        patch.object(recovery.prior, "OUTPUT", output), patch.object(recovery.prior, "guard"), \
                        patch.object(recovery.prior.shared, "check_bindings"), \
                        patch.object(recovery.diagnostic, "authority", return_value=authority), \
                        patch.object(recovery.probe, "measured", side_effect=[normal, normal, final]), \
                        patch.object(recovery.subprocess, "Popen", return_value=process,
                                     side_effect=OSError("synthetic spawn failure") if mode == "spawn" else None), \
                        patch.object(recovery.os, "killpg"):
                    result = recovery.supervise(plan)
                accepted_accounting = mode in {"software_success", "zero_images"}
                self.assertEqual(result["accounting_complete"], accepted_accounting)
                self.assertEqual(result["image_export_software_complete"], mode == "software_success")
                self.assertFalse(result["primary_image_preprocessing_complete"])
                self.assertFalse(result["local_audit_complete"])
                self.assertFalse(result["automatic_retry"])
                self.assertEqual(result["attempts"], 1)
                self.assertFalse(owned.exists())
                if not accepted_accounting:
                    self.assertEqual(len(probe.prior.read(output / "failure_rows.json")["rows"]), 600)


if __name__ == "__main__":
    unittest.main()
