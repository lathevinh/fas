from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.oulu import LABEL_MAPPING, LABEL_MAPPING_HASH, encode_label, inventory_archives, parse_protocol, parse_video_id
from fas.media import probe_video
from fas.transactions import calibration_fit_rows, select_primary_frame, technical_population_counts, technical_transaction, validate_transaction_policy


class OuluVisualTest(unittest.TestCase):
    def test_visual_runner_refuses_repository_and_existing_output(self) -> None:
        import argparse
        spec = importlib.util.spec_from_file_location("prepare_oulu_visual_review", ROOT / "scripts/prepare_oulu_visual_review.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            args = argparse.Namespace(input_root=source, audit_root=source, exact_root=source, screen_root=source,
                                      frozen_root=source, archive_records=source, out_root=ROOT / "results/refused-visual-output")
            with self.assertRaisesRegex(ValueError, "unsafe private output"):
                module.prepare(args)
            args.out_root = source
            with self.assertRaisesRegex(ValueError, "existing output"):
                module.prepare(args)

    def test_review_ranks_are_fixed_and_include_frozen_primary(self) -> None:
        from fas.visual import review_orders
        self.assertEqual(review_orders(1), [0] * 17)
        self.assertEqual(review_orders(8)[8], 3)
        self.assertEqual(review_orders(151)[-1], 150)
        with self.assertRaises(ValueError):
            review_orders(True)

    def test_full_rgb_redecode_reconciles_accepted_frames(self) -> None:
        from fas.visual import verified_thumbnails
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "clip.avi"
            subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=64x48:rate=5",
                            "-frames:v", "4", "-c:v", "mjpeg", "-threads", "1", str(path)], check=True)
            media = probe_video(path)
            frames = verified_thumbnails(path, media)
            self.assertEqual(len(frames), 4)
            self.assertEqual(frames[0].shape, (192, 256, 3))
            media["frame_index"][1]["rgb_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "RGB identity"):
                verified_thumbnails(path, media)

    def test_private_png_and_temporal_sheet_geometry(self) -> None:
        import cv2
        import numpy as np
        from fas.visual import pair_sheet, png_bytes
        frames = [np.full((48, 64, 3), [250, 10, 20], dtype=np.uint8)] * 4
        sheet = pair_sheet(frames, frames, list(range(0, 17, 2)))
        self.assertEqual(sheet.shape, (296, 1440, 3))
        decoded = cv2.imdecode(np.frombuffer(png_bytes(frames[0]), dtype=np.uint8), cv2.IMREAD_COLOR)
        self.assertTrue(np.array_equal(decoded[0, 0], [20, 10, 250]))
        with self.assertRaises(ValueError):
            pair_sheet(frames, frames, [17])


class OuluLineageTest(unittest.TestCase):
    def test_evidence_runner_refuses_repository_or_existing_output(self) -> None:
        spec = importlib.util.spec_from_file_location("triage_oulu_lineage", ROOT / "scripts/triage_oulu_lineage.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            with self.assertRaisesRegex(ValueError, "unsafe private output"):
                module.triage(source, source, source, ROOT / "results/refused-lineage-output")
            with self.assertRaisesRegex(ValueError, "existing output"):
                module.triage(source, source, source, source)

    def media(self, sequence):
        return {"decode_status": "decoded", "frame_count": len(sequence),
                "frame_index": [{"decode_order": order, "decode_success": True,
                                 "width": 32, "height": 24, "timestamp_seconds": str(order),
                                 "rgb_sha256": format(value, "064x")} for order, value in enumerate(sequence)]}

    def test_trimmed_full_sequence_is_rendered_content_not_capture_provenance(self) -> None:
        from fas.lineage import exact_content_evidence
        result = exact_content_evidence(self.media([1, 2, 3]), self.media([0, 1, 2, 3, 4]))
        self.assertEqual(result["disposition"], "confirmed_same_content_or_derived_lineage")
        self.assertEqual(result["longest_exact_contiguous_run"], 3)
        self.assertEqual(result["right_run_start"], 1)
        self.assertFalse(result["capture_provenance_confirmed"])
        reverse = exact_content_evidence(self.media([0, 1, 2, 3, 4]), self.media([1, 2, 3]))
        self.assertEqual(reverse["longest_exact_contiguous_run"], 3)
        self.assertEqual(reverse["left_run_start"], 1)

    def test_missing_or_partial_overlap_never_rejects_candidate(self) -> None:
        from fas.lineage import exact_content_evidence
        for left, right in (([1, 2, 3], [4, 5, 6]), ([1, 2, 3], [0, 1, 2, 4]),
                            ([1, 1], [0, 1, 1, 3]), ([1], [1, 2]), ([1, 2, 3], [3, 2, 1])):
            with self.subTest(left=left, right=right):
                result = exact_content_evidence(self.media(left), self.media(right))
                self.assertEqual(result["disposition"], "uncertain_insufficient_evidence")
                self.assertFalse(result["false_positive_rejection_authorized"])

    def test_repeated_frames_do_not_break_longest_run(self) -> None:
        from fas.lineage import exact_content_evidence
        result = exact_content_evidence(self.media([1, 2, 1, 2]), self.media([0, 1, 2, 1, 2, 3]))
        self.assertEqual(result["longest_exact_contiguous_run"], 4)
        self.assertEqual(result["right_run_start"], 1)

    def test_invalid_full_frame_evidence_fails_closed(self) -> None:
        from fas.lineage import exact_content_evidence
        for key, value in (("rgb_sha256", "bad"), ("decode_order", 7), ("decode_success", False), ("width", True)):
            media = self.media([1, 2])
            media["frame_index"][0][key] = value
            with self.assertRaises(ValueError):
                exact_content_evidence(media, self.media([1, 2]))
        with self.assertRaises(ValueError):
            exact_content_evidence({"decode_status": "failed", "frame_count": 0, "frame_index": []}, self.media([1]))

    def test_priority_is_exclusive_and_no_boundary_is_omitted(self) -> None:
        from fas.lineage import candidate_priority
        for pair, expected in (({"cross_role": True, "cross_partition": True, "conflicting_label": True}, 0),
                               ({"cross_role": True, "cross_partition": True, "conflicting_label": False}, 1),
                               ({"cross_role": False, "cross_partition": True, "conflicting_label": True}, 2),
                               ({"cross_role": False, "cross_partition": False, "conflicting_label": True}, 3),
                               ({"cross_role": False, "cross_partition": False, "conflicting_label": False}, 4)):
            self.assertEqual(candidate_priority(pair), expected)
        with self.assertRaises(ValueError):
            candidate_priority({"cross_role": "true", "cross_partition": False, "conflicting_label": False})


class OuluContentTest(unittest.TestCase):
    def test_runner_refuses_repository_and_existing_output(self) -> None:
        import argparse
        spec = importlib.util.spec_from_file_location("screen_oulu_content", ROOT / "scripts/screen_oulu_content.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            args = argparse.Namespace(input_root=source, audit_root=source, frozen_root=source,
                                      archive_records=source, out_root=ROOT / "results/refused-content-output", workers=4)
            with self.assertRaisesRegex(ValueError, "unsafe private output"):
                module.screen(args)
            args.out_root = source
            with self.assertRaisesRegex(ValueError, "existing output"):
                module.screen(args)

    def test_temporal_ranks_include_frozen_primary(self) -> None:
        from fas.content import temporal_orders
        self.assertEqual(temporal_orders(8), [0, 1, 3, 5, 7])
        self.assertEqual(temporal_orders(1), [0] * 5)
        for invalid in (0, -1, True, 2.5):
            with self.assertRaises(ValueError):
                temporal_orders(invalid)

    def test_phash_deterministic_and_brightness_invariant(self) -> None:
        import numpy as np
        from fas.content import perceptual_hash
        rgb = np.random.default_rng(42).integers(0, 180, (64, 64, 3), dtype=np.uint8)
        self.assertEqual(perceptual_hash(rgb), perceptual_hash(rgb.copy()))
        distance = (int(perceptual_hash(rgb), 16) ^ int(perceptual_hash(rgb + 30), 16)).bit_count()
        self.assertLessEqual(distance, 4)
        with self.assertRaises(ValueError):
            perceptual_hash(rgb.astype(float))

    def test_all_pairs_include_cross_role_and_failed_coverage(self) -> None:
        from fas.content import candidate_pairs
        def record(identity, value, role):
            return {"video_id": identity, "role": role, "status": "fingerprinted",
                    "samples": [{"phash64": value}] * 5}
        rows = [record("a", "0000000000000000", "train"),
                record("b", "000000000000000f", "branch_calibration"),
                record("c", "ffffffffffffffff", "g_domain"),
                {"video_id": "failed", "status": "unavailable_decode_failure", "samples": []}]
        pairs = list(candidate_pairs(rows, block_size=1))
        self.assertEqual([(pair["left"], pair["right"]) for pair in pairs], [("a", "b")])
        self.assertEqual(pairs[0]["disposition"], "unresolved_candidate_not_confirmed_lineage")
        with self.assertRaises(ValueError):
            list(candidate_pairs(rows + rows[:1]))
        self.assertEqual(list(candidate_pairs([])), [])

    def test_sampled_decode_matches_accepted_hash_and_reencode(self) -> None:
        from fas.content import fingerprint_video
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "clip.avi"
            other = Path(directory) / "reencoded.avi"
            subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=64x48:rate=5",
                            "-frames:v", "8", "-c:v", "mjpeg", "-threads", "1", str(path)], check=True)
            subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-c:v", "mjpeg", "-q:v", "6",
                            "-threads", "1", str(other)], check=True)
            media = probe_video(path)
            first = fingerprint_video(path, media)
            second = fingerprint_video(other, probe_video(other))
            self.assertEqual(len(first["samples"]), 5)
            from fas.content import candidate_pairs
            self.assertEqual(len(list(candidate_pairs([dict(first, video_id="a"), dict(second, video_id="b")]))), 1)
            media["frame_index"][0]["rgb_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "RGB identity"):
                fingerprint_video(path, media)
            failed = fingerprint_video(path, {"decode_status": "failed", "frame_count": 0, "frame_index": []})
            self.assertEqual(failed["samples"], [])


class OuluTransactionTest(unittest.TestCase):
    def test_end_to_end_failure_uses_original_denominators_without_fake_detector(self) -> None:
        from fas.contracts import k1_end_to_end_summary
        rows = [{"label": "attack", "detector_status": "success", "final_k1_action": "non_accept"},
                {"label": "bona_fide", "detector_status": "success", "final_k1_action": "accept"},
                {"label": "bona_fide", "detector_status": "not_run", "technical_status": "terminal_failure",
                 "final_k1_action": "non_accept", "model_score": None, "classifier_error": None}]
        result = k1_end_to_end_summary(rows)
        self.assertEqual(result["bona_fide_total"], 2)
        self.assertEqual(result["bfnr_end2end"], 0.5)
        self.assertEqual(result["bona_fide_detector_coverage"], 0.5)
        rows[-1]["model_score"] = 0.1
        with self.assertRaises(ValueError):
            k1_end_to_end_summary(rows)

    def test_transaction_export_refuses_repository_output(self) -> None:
        spec = importlib.util.spec_from_file_location("freeze_oulu_transactions", ROOT / "scripts/freeze_oulu_transactions.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            frozen = Path(directory) / "frozen"
            source.mkdir()
            frozen.mkdir()
            output = ROOT / "results" / "refused-transaction-test-output"
            with self.assertRaisesRegex(ValueError, "unsafe private output"):
                module.export(source, frozen, output)
            self.assertFalse(output.exists())

    def test_policy_bytes_bound_and_semantic_drift_rejected(self) -> None:
        from fas.preregistration import artifact_hashes
        path = ROOT / "configs/transaction_policy_v1.yaml"
        policy = json.loads(path.read_bytes())
        validate_transaction_policy(policy)
        self.assertEqual(artifact_hashes(ROOT)["configs/transaction_policy_v1.yaml"], hashlib.sha256(path.read_bytes()).hexdigest())
        policy["primary_frame"]["even_length_tie"] = "later_decoded_frame"
        with self.assertRaises(ValueError):
            validate_transaction_policy(policy)

    def test_population_denominators_do_not_drop_failed_bona_fide(self) -> None:
        good = technical_transaction(self.media(5))
        media = self.media(0)
        media.update(video_id="failed-id", decode_status="failed")
        failed = technical_transaction(media)
        result = technical_population_counts([good, failed])[0]
        self.assertEqual(result["original_denominator"], 2)
        self.assertEqual(result["primary_frame_available"], 1)
        self.assertEqual(result["terminal_technical_failures"], 1)
        self.assertEqual(result["forced_bfnr_numerator"], 1)
        failed["retain_original_denominator"] = False
        with self.assertRaises(ValueError):
            technical_population_counts([good, failed])

    def media(self, count: int) -> dict:
        return {"video_id": "synthetic-id", "binary_label": "bona_fide", "role": "branch_calibration",
                "decode_status": "decoded", "frame_count": count,
                "frame_index": [{"decode_order": order, "timestamp_seconds": str(order),
                                 "width": 32, "height": 24, "decode_success": True,
                                 "rgb_sha256": "a" * 64} for order in range(count)]}

    def test_odd_even_and_single_frame_primary(self) -> None:
        for count, expected in ((1, 0), (5, 2), (8, 3)):
            with self.subTest(count=count):
                self.assertEqual(select_primary_frame(self.media(count))["decode_order"], expected)

    def test_inclusive_interval_and_no_replacement(self) -> None:
        media = self.media(8)
        self.assertEqual(select_primary_frame(media, interval=("2", "5"))["decode_order"], 3)
        self.assertIsNone(select_primary_frame(media, interval=("10", "11")))
        self.assertEqual(technical_transaction(media, interval=("10", "11"))["final_k1_action"], "non_accept")
        with self.assertRaises(ValueError):
            select_primary_frame(media, interval=("5", "2"))

    def test_failed_calibration_transaction_retains_denominator_without_error(self) -> None:
        media = self.media(0)
        media["decode_status"] = "failed"
        transaction = technical_transaction(media)
        self.assertTrue(transaction["retain_original_denominator"])
        self.assertEqual(transaction["final_k1_action"], "non_accept")
        self.assertEqual(transaction["detector_status"], "not_run")
        self.assertIsNone(transaction["classifier_error"])
        self.assertEqual(calibration_fit_rows([transaction]), [])
        transaction["model_score"] = 0.1
        with self.assertRaises(ValueError):
            calibration_fit_rows([transaction])

    def test_successful_frame_is_not_a_model_score(self) -> None:
        transaction = technical_transaction(self.media(5))
        self.assertEqual(calibration_fit_rows([transaction]), [])
        transaction.update(model_score=0.2, detector_status="success")
        self.assertEqual(calibration_fit_rows([transaction]), [transaction])
        transaction["model_score"] = float("nan")
        with self.assertRaises(ValueError):
            calibration_fit_rows([transaction])

    def test_bad_index_unknown_decode_and_duplicate_ids_fail_closed(self) -> None:
        media = self.media(3)
        media["frame_index"][1]["decode_order"] = 0
        with self.assertRaises(ValueError):
            select_primary_frame(media)
        media["decode_status"] = "not_probed"
        with self.assertRaises(ValueError):
            select_primary_frame(media)
        transaction = technical_transaction(self.media(3))
        with self.assertRaises(ValueError):
            calibration_fit_rows([transaction, transaction])


class OuluMediaTest(unittest.TestCase):
    def test_decode_count_mismatch_fails_closed(self) -> None:
        probe = {"streams": [{"codec_name": "rawvideo", "avg_frame_rate": "4/1"}],
                 "format": {"format_name": "avi", "duration": "1"},
                 "frames": [{"best_effort_timestamp_time": "0", "width": 32, "height": 24, "key_frame": 1}]}
        responses = [subprocess.CompletedProcess([], 0, json.dumps(probe), ""),
                     subprocess.CompletedProcess([], 0, "# empty decoded output\n", "")]
        with patch("fas.media.subprocess.run", side_effect=responses):
            result = probe_video(Path("never-opened.avi"))
        self.assertEqual(result["decode_status"], "failed")
        self.assertEqual(result["middle_decoded_candidates"], [])

    def test_runner_refuses_new_output_inside_repository(self) -> None:
        spec = importlib.util.spec_from_file_location("audit_oulu_media", ROOT / "scripts/audit_oulu_media.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            inputs = Path(directory) / "input"
            frozen = Path(directory) / "frozen"
            inputs.mkdir()
            frozen.mkdir()
            output = ROOT / "results" / "refused-private-media-test-output"
            args = module.argparse.Namespace(input_root=inputs, frozen_root=frozen, out_root=output, workers=1)
            with self.assertRaisesRegex(ValueError, "unsafe output"):
                module.audit(args)
            self.assertFalse(output.exists())

    def test_probe_rejects_corrupt_video_without_leaking_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "private-corrupt.avi"
            path.write_bytes(b"not a video")
            result = probe_video(path)
        self.assertEqual(result["decode_status"], "failed")
        self.assertIsNone(result["decoded_rgb_sequence_sha256"])
        self.assertEqual(result["middle_decoded_candidates"], [])
        self.assertNotIn("private-corrupt", json.dumps(result))

    def test_full_decode_count_middle_and_reproducible_rgb_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.avi"
            subprocess.run([
                "ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                "testsrc=size=32x24:rate=4", "-frames:v", "8", "-c:v",
                "rawvideo", "-pix_fmt", "bgr24", "-threads", "1", str(path),
            ], check=True, capture_output=True)
            result = probe_video(path)
            self.assertEqual(result, probe_video(path))
        self.assertEqual(result["decode_status"], "decoded")
        self.assertEqual(result["frame_count"], 8)
        self.assertEqual(result["fps"], "4")
        self.assertEqual(result["duration_ms"], 2000)
        self.assertEqual(result["middle_decoded_candidates"], [3, 4])
        self.assertEqual(len(result["frame_index"]), 8)
        self.assertEqual(result["frame_index"][4]["timestamp_seconds"], "1")

    def test_timeout_is_terminal_not_a_frame_replacement(self) -> None:
        with patch("fas.media.subprocess.run", side_effect=subprocess.TimeoutExpired("ffprobe", 1)):
            result = probe_video(Path("never-opened.avi"), timeout_seconds=1)
        self.assertEqual(result["failure_reason"], "timeout")
        self.assertEqual(result["decode_status"], "failed")
        self.assertEqual(result["middle_decoded_candidates"], [])


class OuluTest(unittest.TestCase):
    def test_training_polarity_and_documented_identity(self) -> None:
        records = parse_protocol("+1,1_1_01_1\n-1,1_1_01_2\n-1,1_1_01_4\n", "Protocols/Protocol_1/Train.txt")
        self.assertEqual([encode_label(row["binary_label"]) for row in records], [0, 1, 1])
        self.assertEqual([row["attack_family"] for row in records], ["none", "print", "replay"])
        self.assertEqual(records[0]["subject_id"], "subject-01")
        self.assertEqual(records[0]["sensor_id"], "phone-1")
        self.assertEqual(records[0]["session_id"], "session-1")
        self.assertEqual(records[0]["environment"], "unknown")
        self.assertEqual(records[1]["instrument"], "printer-1")
        self.assertEqual(records[2]["instrument"], "display-1")
        self.assertEqual(records[2]["raw_label_token"], "-1")
        self.assertEqual(records[2]["label_source"], "Protocols/Protocol_1/Train.txt")

    def test_test_labels_distinguish_print_and_replay(self) -> None:
        records = parse_protocol("+1,1_3_36_1\n-1,1_3_36_3\n-2,1_3_36_5\n", "Protocols/Protocol_4/Test_1.txt")
        self.assertEqual([row["raw_label_token"] for row in records], ["+1", "-1", "-2"])
        self.assertEqual([encode_label(row["binary_label"]) for row in records], [0, 1, 1])
        self.assertTrue(all(row["official_split"] == "test" and row["protocol_fold"] == 1 for row in records))
        self.assertEqual(records[1]["instrument"], "printer-2")
        self.assertEqual(records[2]["instrument"], "display-2")

    def test_unknown_inconsistent_and_malformed_labels_fail(self) -> None:
        for text in ("0,1_1_01_1", "1,1_1_01_1", "-1,1_1_01_1", "+1,1_1_01_2", "-2,1_1_01_4", "", "\n", "label,video", "+1,1_1_01_1,extra", '"+1,1_1_01_1'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_protocol(text, "Protocols/Protocol_1/Train.txt")
        with self.assertRaises(ValueError):
            parse_protocol("-1,1_3_36_4", "Protocols/Protocol_1/Test.txt")
        with self.assertRaises(ValueError):
            encode_label("unknown")

    def test_duplicate_and_unsafe_identifiers_fail(self) -> None:
        with self.assertRaises(ValueError):
            parse_protocol("+1,1_1_01_1\n+1,1_1_01_1", "Protocols/Protocol_1/Train.txt")
        for value in ("../1_1_01_1", "1_1_01_1.avi", "1_1_1_1", "7_1_01_1", "1_4_01_1", "1_1_00_1", "1_1_56_1", "1_1_01_6", "1_1_01_1\x00"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_video_id(value)

    def test_protocol_membership_and_fold_authority(self) -> None:
        for text, path in (("+1,1_1_21_1", "Protocols/Protocol_1/Train.txt"), ("+1,1_3_01_1", "Protocols/Protocol_1/Train.txt"), ("-1,1_1_01_3", "Protocols/Protocol_2/Train.txt"), ("+1,1_1_01_1", "Protocols/Protocol_3/Train_1.txt"), ("+1,2_1_36_1", "Protocols/Protocol_3/Test_1.txt"), ("+1,1_1_01_1", "Protocols/Protocol_1/Train_1.txt"), ("+1,1_1_01_1", "Protocols/Protocol_3/Train.txt"), ("+1,1_1_01_1", "../Protocols/Protocol_1/Train.txt")):
            with self.subTest(path=path, text=text), self.assertRaises(ValueError):
                parse_protocol(text, path)
        records = parse_protocol("+1,2_2_21_1", "Protocols/Protocol_3/Dev_1.txt")
        self.assertEqual(records[0]["official_split"], "development")

    def test_mapping_hash_is_deterministic_and_score_contract(self) -> None:
        digest = hashlib.sha256(json.dumps(LABEL_MAPPING, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(digest, LABEL_MAPPING_HASH)
        self.assertEqual(parse_video_id("1_1_01_1")["label_mapping_hash"], digest)
        for binary_label in ("bona_fide", "attack"):
            truth = encode_label(binary_label)
            for attack_score in (0.1, 0.9):
                prediction = int(attack_score >= 0.5)
                error = int(prediction != truth)
                self.assertEqual(error, 0 if prediction == truth else 1)
        self.assertGreater(encode_label("attack"), encode_label("bona_fide"))


class OuluInventoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "private-input"
        self.root.mkdir()
        (self.root / "Readme.pdf").write_bytes(b"synthetic documentation, not a real PDF")
        self.archives: dict[str, dict[str, bytes]] = {}
        self.partitions: dict[str, list[str]] = {}
        for storage, subject, session in (("Train_files", 1, 1), ("Dev_files", 21, 1), ("Test_files", 36, 3)):
            identifiers = [f"{phone}_{session}_{subject:02d}_1" for phone in range(1, 7)]
            if storage == "Train_files":
                identifiers += ["1_1_01_2", "2_1_01_4"]
            if storage == "Test_files":
                identifiers += ["1_3_36_3", "2_3_36_5"]
            self.partitions[storage] = identifiers
            self.archives[f"{storage}.tar"] = {
                f"{storage}/{video_id}{suffix}": b"synthetic bytes " + video_id.encode()
                for video_id in identifiers for suffix in (".avi", ".txt")
            }
        protocols: dict[str, bytes] = {}
        for protocol in range(1, 5):
            for fold in ((None,) if protocol < 3 else range(1, 7)):
                for name, storage in (("Train", "Train_files"), ("Dev", "Dev_files"), ("Test", "Test_files")):
                    rows = []
                    for video_id in self.partitions[storage]:
                        phone, session, subject, access = (int(part) for part in video_id.split("_"))
                        if fold is not None and ((phone == fold) != (name == "Test")):
                            continue
                        if protocol in (2, 4) and access not in ((1, 3, 5) if name == "Test" else (1, 2, 4)):
                            continue
                        token = "+1" if access == 1 else "-2" if name == "Test" and access >= 4 else "-1"
                        rows.append(f"{token},{video_id}\n")
                    suffix = "" if fold is None else f"_{fold}"
                    protocols[f"Protocols/Protocol_{protocol}/{name}{suffix}.txt"] = "".join(rows).encode()
        self.archives["Protocols.tar"] = protocols
        self.write_archives()

    def write_archives(self) -> None:
        for name, entries in self.archives.items():
            with tarfile.open(self.root / name, "w") as archive:
                for relative, payload in entries.items():
                    member = tarfile.TarInfo(relative)
                    member.size = len(payload)
                    archive.addfile(member, io.BytesIO(payload))

    def inventory(self, **options) -> dict:
        return inventory_archives(self.root, release_id="synthetic-release", protocol_id="synthetic-protocol", **options)

    def test_reconciles_synthetic_media_and_all_protocol_memberships(self) -> None:
        result = self.inventory()
        self.assertEqual(len(result["videos"]), 22)
        self.assertEqual(len(result["protocol_sha256"]), 42)
        self.assertEqual(result, self.inventory())
        self.assertFalse(result["scientific_readiness"])
        self.assertFalse(result["acquisition_verified"])
        self.assertTrue(all(row["official_split"] and row["protocol_memberships"] for row in result["videos"]))
        self.assertTrue(all(row["raw_label_token"] and row["label_source"] for row in result["videos"]))
        replay = next(row for row in result["videos"] if row["video_id"] == "2_3_36_5")
        self.assertTrue(all(row["raw_label_token"] == "-2" for row in replay["protocol_memberships"]))

    def test_header_only_mode_never_opens_video_payload(self) -> None:
        original = tarfile.TarFile.extractfile
        def guarded(archive, member):
            if member.name.endswith(".avi"):
                raise AssertionError("header-only inventory opened a video")
            return original(archive, member)
        with patch.object(tarfile.TarFile, "extractfile", guarded):
            result = self.inventory()
        self.assertTrue(result["no_media_decoding"])
        self.assertTrue(all(row["media_sha256"] is None and row["decode_status"] == "not_probed" for row in result["videos"]))

    def test_optional_byte_hashes_do_not_imply_decoding(self) -> None:
        result = self.inventory(hash_media=True)
        self.assertTrue(result["media_hashes_computed"])
        for row in result["videos"]:
            payload = self.archives[row["media_archive"]][row["media_relpath"]]
            self.assertEqual(row["media_sha256"], hashlib.sha256(payload).hexdigest())
            self.assertEqual(row["decode_status"], "not_probed")
        self.assertTrue(all(value is not None for value in result["archive_sha256"].values()))

    def test_protocol_omission_or_missing_media_fails_closed(self) -> None:
        key = "Protocols/Protocol_1/Train.txt"
        original = self.archives["Protocols.tar"][key]
        self.archives["Protocols.tar"][key] = original.split(b"\n", 1)[1]
        self.write_archives()
        with self.assertRaisesRegex(ValueError, "membership disagree"):
            self.inventory()
        self.archives["Protocols.tar"][key] = original
        del self.archives["Train_files.tar"]["Train_files/1_1_01_1.avi"]
        self.write_archives()
        with self.assertRaises(ValueError):
            self.inventory()

    def test_missing_protocol_and_incomplete_release_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "full release"):
            self.inventory(require_full_release=True)
        del self.archives["Protocols.tar"]["Protocols/Protocol_4/Test_6.txt"]
        self.write_archives()
        with self.assertRaisesRegex(ValueError, "coverage"):
            self.inventory()

    def test_unsafe_members_links_and_duplicate_archive_paths_fail(self) -> None:
        archive = self.root / "Train_files.tar"
        for name, kind in (("../outside", tarfile.REGTYPE), ("Train_files/1_1_01_1.avi", tarfile.SYMTYPE), ("Train_files/1_1_01_1.avi", tarfile.LNKTYPE), ("Train_files/1_1_01_1.avi", tarfile.REGTYPE)):
            with self.subTest(name=name, kind=kind):
                self.write_archives()
                with tarfile.open(archive, "a") as target:
                    member = tarfile.TarInfo(name)
                    member.type = kind
                    member.size = 1 if kind == tarfile.REGTYPE else 0
                    member.linkname = "outside"
                    target.addfile(member, io.BytesIO(b"x") if member.size else None)
                with self.assertRaises(ValueError):
                    self.inventory()

    def command(self, output: Path, *extra: str) -> subprocess.CompletedProcess:
        return subprocess.run([
            sys.executable, str(ROOT / "scripts" / "inventory_oulu.py"),
            "--input-root", str(self.root), "--release-id", "synthetic-private-release",
            "--protocol-id", "synthetic-private-protocol", "--unverified-local",
            "--out", str(output), *extra,
        ], capture_output=True, text=True, check=False)

    def test_cli_writes_private_immutable_output_and_redacts_stdout(self) -> None:
        output = self.root.parent / "inventory.json"
        result = self.command(output)
        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary["status"], "metadata_reconciled")
        self.assertFalse(summary["scientific_readiness"])
        self.assertFalse(summary["acquisition_verified"])
        self.assertNotIn("videos", summary)
        for secret in (str(self.root), "synthetic-private-release", "subject-01", "1_1_01_1"):
            self.assertNotIn(secret, result.stdout + result.stderr)
        original = output.read_bytes()
        self.assertEqual(len(json.loads(original)["videos"]), 22)
        self.assertEqual(self.command(output).returncode, 2)
        self.assertEqual(output.read_bytes(), original)

    def test_cli_blocks_reconciliation_failures_and_preserves_inputs(self) -> None:
        key = "Protocols/Protocol_1/Train.txt"
        self.archives["Protocols.tar"][key] = b"0,1_1_01_1\n"
        self.write_archives()
        output = self.root.parent / "blocked.json"
        result = self.command(output)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(output.exists())
        self.assertNotIn("1_1_01_1", result.stdout + result.stderr)
        self.assertNotIn(str(self.root), result.stdout + result.stderr)
        original = (self.root / "Readme.pdf").read_bytes()
        self.assertEqual(self.command(self.root / "Readme.pdf").returncode, 2)
        self.assertEqual((self.root / "Readme.pdf").read_bytes(), original)
        self.assertEqual(self.command(ROOT / "results" / "refused-oulu.json").returncode, 2)

    def test_cli_full_release_flag_rejects_partial_synthetic_fixture(self) -> None:
        result = self.command(self.root.parent / "full.json", "--require-full-release")
        self.assertEqual(result.returncode, 1)
        self.assertFalse((self.root.parent / "full.json").exists())

    def test_invalid_documentation_symlink_and_corrupt_archive_fail_closed(self) -> None:
        document = self.root / "Readme.pdf"
        document.unlink()
        outside = self.root.parent / "outside.pdf"
        outside.write_bytes(b"outside documentation")
        document.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "unsafe"):
            self.inventory()
        document.unlink()
        document.write_bytes(b"synthetic documentation")
        (self.root / "Protocols.tar").write_bytes(b"not a tar archive")
        result = self.command(self.root.parent / "corrupt.json")
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(str(self.root), result.stdout + result.stderr)

    def test_cli_redacts_required_file_symlink_loop(self) -> None:
        document = self.root / "Readme.pdf"
        document.unlink()
        document.symlink_to(document.name)
        result = self.command(self.root.parent / "loop.json")
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(str(self.root), result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stdout + result.stderr)
        self.assertFalse((self.root.parent / "loop.json").exists())


if __name__ == "__main__":
    unittest.main()