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


class OuluHumanReviewTest(unittest.TestCase):
    def test_correspondence253_camera_compensation_and_unknown_registration(self) -> None:
        import numpy as np

        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import evaluate_oulu_motion253 as experiment

            previous = np.random.default_rng(17).integers(0, 256, (128, 128), dtype=np.uint8)
            current = np.roll(previous, (1, 2), axis=(0, 1))
            mask, metadata = experiment.residual_mask(previous, current)
            self.assertEqual(metadata["status"], "registered_translation")
            np.testing.assert_allclose(metadata["shift"], [2, 1], atol=0.01)
            self.assertFalse(np.any(mask))
            first, second = experiment.dynamic_background_sequences(600)
            self.assertEqual((len(first), len(second)), (9, 9))
            np.testing.assert_array_equal(first[0][32, 32], second[0][32, 32])
            self.assertTrue(np.any(first[0][128, 80] != second[0][128, 80]))
            blank = np.zeros((64, 64, 3), np.uint8)
            baseline, revised = experiment.feature_sets([blank] * 9)
            self.assertEqual([value["rgb_sha256"] for value in baseline], [value["rgb_sha256"] for value in revised])
            self.assertTrue(all(value["camera_motion"]["status"] == "registration_unavailable" for value in revised[1:]))
            finding = experiment.compare_features(revised, revised)
            self.assertIsNone(finding["scientific_disposition"])
            self.assertFalse(finding["capture_independence"])
            self.assertFalse(finding["witnesses"])
        finally:
            sys.path.pop(0)

    def test_correspondence251_component_connectivity_and_disjointness(self) -> None:
        from fas.content_correspondence import planned_edge_rows

        for right, valid, invalid in [
                ("c", [{"ranks": [19, 86], "videos": ["a", "b", "c"]}],
                 [{"ranks": [19], "videos": ["a", "b"]}, {"ranks": [86], "videos": ["b", "c"]}]),
                ("d", [{"ranks": [19], "videos": ["a", "b"]}, {"ranks": [86], "videos": ["c", "d"]}],
                 [{"ranks": [19, 86], "videos": ["a", "b", "c", "d"]}])]:
            members = [{"queue_rank": 19, "left": "a", "right": "b", "record_sha256": "a" * 64},
                       {"queue_rank": 86, "left": "b" if right == "c" else "c", "right": right,
                        "record_sha256": "b" * 64}]
            counts = {member[side]: 151 for member in members for side in ("left", "right")}
            with self.subTest(right=right):
                rows = planned_edge_rows(members, valid, counts)
                self.assertEqual([row["queue_rank"] for row in rows], [19, 86])
                self.assertEqual([{key: row[key] for key in members[0]} for row in rows], members)
                self.assertTrue(all(row["effective_disposition"] is None for row in rows))
                with self.assertRaises(ValueError):
                    planned_edge_rows(members, invalid, counts)

    def test_correspondence249_complete_edge_plan_and_fail_closed_joins(self) -> None:
        from copy import deepcopy
        from fas.content_correspondence import planned_edge_rows

        members = [{"queue_rank": rank, "left": "left", "right": right, "record_sha256": "a" * 64}
                   for rank, right in [(19, "right1"), (86, "right2")]]
        components = [{"ranks": [19, 86], "videos": ["left", "right1", "right2"]}]
        counts = {"left": 151, "right1": 146, "right2": 150}
        rows = planned_edge_rows(members, components, counts)
        self.assertEqual([row["queue_rank"] for row in rows], [19, 86])
        self.assertTrue(all(row["candidate_finding"] is None and row["effective_disposition"] is None for row in rows))
        self.assertEqual(len(rows[0]["planned_orders"]["left"]), 9)
        for changed_members, changed_components, changed_counts in [
                (members + members[:1], components, counts), (members, [], counts),
                (members, components + components, counts), (members, components, {"left": 151})]:
            with self.assertRaises(ValueError):
                planned_edge_rows(changed_members, changed_components, changed_counts)
        changed = deepcopy(components)
        changed[0]["videos"].append("extra")
        with self.assertRaises(ValueError):
            planned_edge_rows(members, changed, counts)

    def test_correspondence249_synthetic_replay_and_shared_camera_confound(self) -> None:
        from fas.content_correspondence import compare_features, sequence_features

        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import evaluate_oulu_method249 as controls

            original = sequence_features(controls.scene(100))
            first = compare_features(original, original)
            self.assertTrue(first["witnesses"])
            self.assertEqual(first, compare_features(original, original))
            left, right = controls.shared_camera_sequences(300)
            confounded = compare_features(sequence_features(left), sequence_features(right))
            self.assertTrue(confounded["witnesses"])
            self.assertIsNone(confounded["scientific_disposition"])
            self.assertFalse(confounded["capture_independence"])
        finally:
            sys.path.pop(0)

    def test_correspondence249_orders_input_and_temporal_geometry(self) -> None:
        import numpy as np
        from fas.content_correspondence import compare_features, sample_orders, sequence_features, temporal_chain

        self.assertEqual(sample_orders(151), [0, 18, 37, 56, 75, 93, 112, 131, 150])
        self.assertEqual(sample_orders(2), [0, 1])
        for invalid in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                sample_orders(invalid)
        for frames in ([], [np.zeros((16, 16, 3), np.uint8)], [np.zeros((64, 64, 3), np.float32)]):
            with self.assertRaises(ValueError):
                sequence_features(frames)
        blank = sequence_features([np.zeros((64, 64, 3), np.uint8)] * 9)
        result = compare_features(blank, blank)
        self.assertEqual(result["finding"], "no_supported_witness_not_clearance")
        self.assertIsNone(result["scientific_disposition"])
        self.assertEqual(result["tested_slot_pairs"], 34)
        hits = {(slot, slot): {"projected_corners": [[0, 0], [1, 0], [0, 1], [1, 1]]} for slot in (1, 2, 3)}
        self.assertEqual(len(temporal_chain(hits)), 3)
        self.assertEqual(temporal_chain({key: value for key, value in hits.items() if key[0] < 3}), [])
        hits[3, 3] = {"projected_corners": [[20, 0], [21, 0], [20, 1], [21, 1]]}
        self.assertEqual(temporal_chain(hits), [])

    def test_pilot243_authority_output_and_parent_watchdog_refusals(self) -> None:
        from unittest.mock import MagicMock

        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_pilot243 as module
            for preflight in ({}, {"checkpoint": True}, {"checkpoint": 243, "caps": {}, "review242_consolidated_pilot_authorized": True},
                              {"checkpoint": 243, "caps": module.CAPS, "review242_consolidated_pilot_authorized": False},
                              {"checkpoint": 243, "caps": module.CAPS, "review242_consolidated_pilot_authorized": True, "membership_sha256": "drift"}):
                with self.assertRaises(ValueError):
                    module.selected_sources(preflight)
            with tempfile.TemporaryDirectory() as directory:
                home = Path(directory)
                source = home / "source.json"
                source.write_text("{}")
                existing = home / "existing"
                existing.mkdir()
                for output in (existing, ROOT / "results/refused243", home / "source.json/child"):
                    with self.assertRaises(ValueError):
                        module.supervise(source, output, home / "metrics.json")
                for field in ("rss_bytes", "temporary_bytes", "output_bytes"):
                    process = MagicMock(pid=12345)
                    measured = {key: 0 for key in ("rss_bytes", "temporary_bytes", "output_bytes")}
                    measured[field] = module.CAPS[field] + 1
                    records = []
                    with patch.object(module.subprocess, "Popen", return_value=process), patch.object(module, "usage", return_value=measured), \
                         patch.object(module.os, "killpg") as kill, patch.object(module, "write_immutable_record", side_effect=lambda path, record: records.append(record)):
                        self.assertEqual(module.supervise(source, home / "out", home / "metrics.json"), 1)
                        kill.assert_called_once()
                        process.wait.assert_called_once()
                    self.assertFalse(records[0]["completion_claimed"])
                    self.assertEqual(records[0]["sampled_peaks"][field], measured[field])
                with patch.object(module.subprocess, "Popen", return_value=MagicMock(pid=12345)), \
                     patch.object(module, "usage", return_value={key: 0 for key in measured}), \
                     patch.object(module.time, "monotonic", side_effect=[0, 1801, 1802]), \
                     patch.object(module.os, "killpg"), patch.object(module, "write_immutable_record") as writer:
                    self.assertEqual(module.supervise(source, home / "out", home / "metrics.json"), 1)
                    self.assertFalse(writer.call_args.args[1]["completion_claimed"])
        finally:
            sys.path.pop(0)

    def test_pilot243_stream_deadline_integrity_and_chronological_gallery(self) -> None:
        import numpy as np
        from types import SimpleNamespace

        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_pilot243 as module
            frames = [np.full((2, 3, 3), value, np.uint8) for value in (11, 23)]
            payload = b"".join(frame.tobytes() for frame in frames)
            media = {"decode_status": "decoded", "frame_count": 2, "frame_index": [
                {"decode_order": order, "decode_success": True, "width": 3, "height": 2,
                 "timestamp_seconds": str(order), "rgb_sha256": hashlib.sha256(frame.tobytes()).hexdigest()}
                for order, frame in enumerate(frames)]}
            command = [sys.executable, "-c", f"import os;os.write(1,{payload!r})"]
            received = []
            module.stream_frames(Path("unused"), media, lambda order, rgb: received.append((order, rgb.copy())), command=command)
            self.assertEqual([order for order, rgb in received], [0, 1])
            self.assertTrue(all(np.array_equal(rgb, frames[order]) for order, rgb in received))
            for changed in (payload[:-1], payload + b"x", b"x" + payload[1:]):
                with self.subTest(size=len(changed)), self.assertRaises(ValueError):
                    module.stream_frames(Path("unused"), media, lambda *args: None,
                                         command=[sys.executable, "-c", f"import os;os.write(1,{changed!r})"])
            for suffix in (";os.write(2,b'error')", ";raise SystemExit(1)"):
                with self.assertRaises(ValueError):
                    module.stream_frames(Path("unused"), media, lambda *args: None,
                                         command=[sys.executable, "-c", f"import os;os.write(1,{payload!r})" + suffix])
            with self.assertRaises(TimeoutError):
                module.stream_frames(Path("unused"), media, lambda *args: None, timeout=0.1,
                                     command=[sys.executable, "-c", "import threading;threading.Event().wait()"])
            tiles = [np.full((455, 256, 3), order, np.uint8) for order in range(19)]
            for start in (0, 16):
                sheet = module.gallery(tiles, start)
                self.assertEqual(sheet.shape, (1932, 1024, 3))
                for slot in range(16):
                    top, left = slot // 4 * 483 + 28, slot % 4 * 256
                    self.assertTrue(np.all(sheet[top:top + 455, left:left + 256] == (start + slot if start + slot < 19 else 255)))
            for start in (-1, 1, 32, True):
                with self.assertRaises(ValueError):
                    module.gallery(tiles, start)
            valid = SimpleNamespace(name="train/a.avi", size=18, isfile=lambda: True)
            module.checked_member(valid, {"media_relpath": "train/a.avi", "byte_size": 18})
            for member in (SimpleNamespace(name="../a", size=18, isfile=lambda: True),
                           SimpleNamespace(name="train/a.avi", size=19, isfile=lambda: True),
                           SimpleNamespace(name="train/a.avi", size=18, isfile=lambda: False)):
                with self.assertRaises(ValueError):
                    module.checked_member(member, {"media_relpath": "train/a.avi", "byte_size": 18})
        finally:
            sys.path.pop(0)

    def test_batch08_categorical_import_receipt_strict_JSON_and_derived_stops(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_categorical_batch08 as module
            digest = "a" * 64
            pairs = [{"queue_rank": rank, "packet_sha256": digest, "ai_record_sha256": digest, "formal_review_record_sha256": digest,
                      "exact_pair_record_sha256": digest, "ai_disposition": "rejected_false_positive",
                      "required_assets_sha256": {f"assets/{rank:06d}/{name}.png": digest for name in ("temporal_a", "temporal_b", "trigger")}} for rank in module.TARGET_RANKS]
            authority = {"review208_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256, "accepted_formal_report_sha256": module.FORMAL_REPORT_SHA256}
            definition = {**authority, "sha256": digest, "categorical_rules": module.CATEGORICAL_RULES, "pairs": pairs}
            human = {**authority, "version": 1, "record_type": "batch08_categorical_review", "review_definition_sha256": digest,
                     "reviewer": {"kind": "owner_human", "id": "synthetic", "personally_inspected_bound_evidence": True},
                     "reviewed_at_utc": "2026-10-20T00:00:00Z", "stop_for_prospective_scientific_decision": False, "owner_extra": {"keep": [True, None, 1]},
                     "pairs": [{"queue_rank": pair["queue_rank"], "packet_sha256": digest, "ai_record_sha256": digest, "formal_review_record_sha256": digest,
                                "exact_pair_record_sha256": digest, "reviewed_assets_sha256": pair["required_assets_sha256"], "evidence_sufficient": True,
                                "same_or_derived_content": False, "personal_inspection_attested": True, "owner_decision_attested": True,
                                "capture_provenance_certified": False, "disposition": "rejected_false_positive", "stop_for_prospective_scientific_decision": False,
                                "owner_extra": {"preserve": [False, None]}} for pair in pairs]}
            before = json.dumps([human, definition], sort_keys=True)
            rows = module.validate_categorical(human, definition)
            self.assertEqual(json.dumps([human, definition], sort_keys=True), before)
            self.assertEqual(sum(row["disagreement_with_AI"] for row in rows), 0)
            for original, row in zip(human["pairs"], rows, strict=True):
                self.assertTrue(all(row[field] == value for field, value in original.items()))
                self.assertTrue(row["checkpoint_review_pending"] and row["semantic_acceptance_pending"])
                self.assertFalse(row["effective_disposition_activated"] or row["counts_as_accepted_current_effective_disposition"])
                self.assertNotIn("rationale", row)
            for rule in module.CATEGORICAL_RULES:
                stop = rule["same_or_derived_content"] is True
                changed = {**human["pairs"][0], **rule, "stop_for_prospective_scientific_decision": stop}
                result = module.validate_categorical({**human, "pairs": [changed, *human["pairs"][1:]], "stop_for_prospective_scientific_decision": stop}, definition)[0]
                self.assertEqual(result["validated_disposition"], rule["disposition"])
                self.assertIs(result["scientific_stop_independently_derived"], stop)
                self.assertEqual(result["reconciliation_required"], rule["disposition"] != "rejected_false_positive")
                if result["reconciliation_required"]:
                    self.assertEqual(result["comparison_disposition"], "uncertain_insufficient_evidence")
            for field, value in (("queue_rank", True), ("queue_rank", 70.0), ("queue_rank", 71), ("queue_rank", 80), ("packet_sha256", "drift"),
                                 ("ai_record_sha256", "drift"), ("formal_review_record_sha256", "drift"), ("exact_pair_record_sha256", "drift"),
                                 ("reviewed_assets_sha256", {}), ("evidence_sufficient", None), ("evidence_sufficient", 1), ("evidence_sufficient", "true"),
                                 ("same_or_derived_content", 0), ("same_or_derived_content", None), ("same_or_derived_content", "false"),
                                 ("personal_inspection_attested", 1), ("owner_decision_attested", False), ("capture_provenance_certified", 0),
                                 ("disposition", "uncertain_insufficient_evidence"), ("stop_for_prospective_scientific_decision", True),
                                 ("stop_for_prospective_scientific_decision", 0), ("semantic_acceptance_pending", True), ("ai_disposition", "rejected_false_positive")):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    module.validate_categorical({**human, "pairs": [{**human["pairs"][0], field: value}, *human["pairs"][1:]]}, definition)
            for same in (True, False, 0, "false"):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, "pairs": [{**human["pairs"][0], "evidence_sufficient": False, "same_or_derived_content": same}, *human["pairs"][1:]]}, definition)
            for changes in ({"version": True}, {"version": 1.0}, {"record_type": "batch07_categorical_review"}, {"review_definition_sha256": "drift"},
                            *({field: "drift"} for field in authority), {"reviewed_at_utc": None}, {"reviewed_at_utc": "2026-10-20"},
                            {"reviewed_at_utc": "2026-10-20T00:00:00+01:00"}, {"reviewer": []}, {"reviewer": {**human["reviewer"], "id": " "}},
                            {"reviewer": {**human["reviewer"], "kind": []}}, {"reviewer": {**human["reviewer"], "personally_inspected_bound_evidence": 1}},
                            {"pairs": human["pairs"][:-1]}, {"pairs": [*human["pairs"], human["pairs"][0]]}, {"stop_for_prospective_scientific_decision": True}):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, **changes}, definition)
            for changes in ({"pairs": pairs[:-1]}, {"pairs": list(reversed(pairs))}, {"pairs": [{**pairs[0], "queue_rank": 70.0}, *pairs[1:]]},
                            {"categorical_rules": []}, {"categorical_rules": [{**module.CATEGORICAL_RULES[0], "evidence_sufficient": 0}, *module.CATEGORICAL_RULES[1:]]},
                            *({field: "drift"} for field in authority)):
                with self.assertRaises(ValueError):
                    module.validate_categorical(human, {**definition, **changes})
            self.assertEqual(len(module.validate_categorical({**human, "pairs": list(reversed(human["pairs"]))}, definition)), 10)
            for payload in ('{"x":1,"x":2}', '{"nested":{"x":1,"x":2}}', '{"x":NaN}', '{"x":Infinity}', '{"x":1e999}', '[]', 'null', '{broken'):
                with self.assertRaises(ValueError):
                    module.strict_json(payload)
            self.assertEqual(module.strict_json(json.dumps(human)), human)
            check = {"head_sha": "9c01c585e52045462499a18361d6a930571dd059", "run_id": 39347602537, "job_id": 118383870057,
                     "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success"}
            preflight = {"checkpoint": 213, "queue_ranks": list(module.TARGET_RANKS), "review212_sha256": module.REVIEW212_SHA256,
                         "review210_sha256": module.REVIEW210_SHA256, "import_authority": module.IMPORT_AUTHORITY, "source211_CI": check,
                                 "import_authorized": True, "activation_authorized": False, "effective_activation_authorized": False, "model_execution_authorized": False, "scientific_readiness": False}
            module.verify_authority(preflight)
            for changes in ({"checkpoint": 213.0}, {"review212_sha256": "drift"}, {"review210_sha256": "drift"}, {"import_authority": "prepare_only"},
                                     {"import_authorized": False}, {"import_authorized": 1}, {"activation_authorized": True}, {"effective_activation_authorized": True}, {"model_execution_authorized": True}, {"scientific_readiness": True},
                            {"queue_ranks": [70.0, *module.TARGET_RANKS[1:]]}, {"source211_CI": {**check, "run_id": float(check["run_id"])}},
                            *({"source211_CI": {**check, field: "drift"}} for field in check)):
                with self.assertRaises(ValueError):
                    module.verify_authority({**preflight, **changes})
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source = root / "input.json"
                payload = json.dumps(human).encode()
                source.write_bytes(payload)
                self.assertEqual(module.read_receipted_input(source, hashlib.sha256(payload).hexdigest(), len(payload)), human)
                for expected_hash, expected_size in ((digest, len(payload)), (hashlib.sha256(payload).hexdigest(), len(payload) + 1), (digest, True)):
                    with patch.object(module, "strict_json", side_effect=AssertionError("must not parse before receipt check")), self.assertRaises(ValueError):
                        module.read_receipted_input(source, expected_hash, expected_size)
                linked = root / "linked.json"
                linked.symlink_to(source)
                with self.assertRaises(ValueError):
                    module.read_receipted_input(linked, hashlib.sha256(payload).hexdigest(), len(payload))
                self.assertEqual(source.read_bytes(), payload)
                for output in (root, ROOT / "results/refused-batch08-import", root / "review/overlap"):
                    with self.assertRaises(ValueError):
                        module.import_review(Namespace(preflight=root / "preflight.json", review_root=root / "review", human_input=source, out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch07_categorical_import_strict_answers_and_preserved_AI_uncertainty(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_categorical_batch07 as module
            digest = "a" * 64
            pairs = [{"queue_rank": rank, "packet_sha256": digest, "ai_record_sha256": digest, "exact_pair_record_sha256": digest,
                      "required_assets_sha256": {f"assets/{rank:06d}/{name}.png": digest for name in ("temporal_a", "temporal_b", "trigger")},
                      "ai_disposition": "uncertain_insufficient_evidence" if rank == 66 else "rejected_false_positive"} for rank in module.TARGET_RANKS]
            definition = {"sha256": digest, "review194_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                          "categorical_rules": module.CATEGORICAL_RULES, "pairs": pairs}
            human = {"version": 1, "record_type": "batch07_categorical_review", "review_definition_sha256": digest,
                     "review194_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                     "reviewer": {"kind": "owner_human", "id": "synthetic", "personally_inspected_bound_evidence": True},
                     "reviewed_at_utc": "2026-10-15T10:00:00Z", "stop_for_prospective_scientific_decision": False, "owner_extra": {"preserve": [1, False, None]},
                     "pairs": [{"queue_rank": pair["queue_rank"], "packet_sha256": digest, "ai_record_sha256": digest, "exact_pair_record_sha256": digest,
                                "reviewed_assets_sha256": pair["required_assets_sha256"], "evidence_sufficient": True, "same_or_derived_content": False,
                                "personal_inspection_attested": True, "owner_decision_attested": True, "capture_provenance_certified": False,
                                "disposition": "rejected_false_positive", "stop_for_prospective_scientific_decision": False, "owner_extra": {"preserve": [True, None]}} for pair in pairs]}
            before = json.dumps([human, definition], sort_keys=True)
            rows = module.validate_categorical(human, definition)
            self.assertEqual(json.dumps([human, definition], sort_keys=True), before)
            self.assertEqual(sum(row["disagreement_with_AI"] for row in rows), 1)
            self.assertEqual(rows[6]["ai_disposition"], "uncertain_insufficient_evidence")
            self.assertEqual(rows[6]["comparison_disposition"], "uncertain_insufficient_evidence")
            self.assertEqual(rows[6]["disposition"], "rejected_false_positive")
            for original, row in zip(human["pairs"], rows, strict=True):
                self.assertTrue(all(row[field] == value for field, value in original.items()))
                self.assertFalse(row["effective_disposition_activated"] or row["counts_as_accepted_current_effective_disposition"])
                self.assertTrue(row["semantic_acceptance_pending"])
                self.assertNotIn("rationale", row)
            for field, value in (("queue_rank", 60.0), ("queue_rank", True), ("queue_rank", 61), ("packet_sha256", "drift"), ("ai_record_sha256", "drift"),
                                 ("exact_pair_record_sha256", "drift"), ("reviewed_assets_sha256", {}), ("evidence_sufficient", 1), ("same_or_derived_content", 0),
                                 ("same_or_derived_content", None), ("personal_inspection_attested", 1), ("owner_decision_attested", False), ("capture_provenance_certified", 0),
                                 ("disposition", "uncertain_insufficient_evidence"), ("stop_for_prospective_scientific_decision", 0), ("effective_disposition_activated", False),
                                 ("ai_disposition", "rejected_false_positive"), ("semantic_acceptance_pending", True)):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, "pairs": [{**human["pairs"][0], field: value}, *human["pairs"][1:]]}, definition)
            for changes in ({"version": True}, {"version": 1.0}, {"record_type": "batch06_categorical_review"}, {"review_definition_sha256": "drift"},
                            {"review194_sha256": "drift"}, {"accepted_AI_report_sha256": "drift"}, {"reviewed_at_utc": "2026-10-15T10:00:00"},
                            {"reviewed_at_utc": "2026-10-15T10:00:00+01:00"}, {"reviewer": {**human["reviewer"], "personally_inspected_bound_evidence": False}},
                            {"reviewer": {**human["reviewer"], "id": " "}}, {"pairs": human["pairs"][:-1]}, {"stop_for_prospective_scientific_decision": True}):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, **changes}, definition)
            for changes in ({"pairs": pairs[:-1]}, {"pairs": list(reversed(pairs))}, {"pairs": [{**pairs[0], "queue_rank": 60.0}, *pairs[1:]]},
                            {"categorical_rules": []}, {"categorical_rules": [{**module.CATEGORICAL_RULES[0], "evidence_sufficient": 0}, *module.CATEGORICAL_RULES[1:]]},
                            {"review194_sha256": "drift"}, {"accepted_AI_report_sha256": "drift"}):
                with self.assertRaises(ValueError):
                    module.validate_categorical(human, {**definition, **changes})
            for rule in module.CATEGORICAL_RULES:
                stop = rule["same_or_derived_content"] is True
                changed = {**human["pairs"][6], **rule, "stop_for_prospective_scientific_decision": stop}
                result = module.validate_categorical({**human, "pairs": [*human["pairs"][:6], changed, *human["pairs"][7:]], "stop_for_prospective_scientific_decision": stop}, definition)[6]
                self.assertEqual(result["validated_disposition"], rule["disposition"])
                self.assertEqual(result["stop_for_prospective_scientific_decision"], stop)
                self.assertEqual(result["reconciliation_required"], rule["disposition"] != "uncertain_insufficient_evidence")
                self.assertEqual(result["comparison_disposition"], "uncertain_insufficient_evidence")
                self.assertEqual(result["disposition"], rule["disposition"])
            for same in (True, False, 0, "false"):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, "pairs": [{**human["pairs"][0], "evidence_sufficient": False, "same_or_derived_content": same}, *human["pairs"][1:]]}, definition)
            self.assertEqual(len(module.validate_categorical({**human, "pairs": list(reversed(human["pairs"]))}, definition)), 10)
            check = {"head_sha": "3f648377a7d273fc1f35202d101692423e4d9d40", "run_id": 38710625142, "job_id": 116340807019,
                     "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success"}
            authority = {"checkpoint": 197, "review196_sha256": module.REVIEW196_SHA256, "import_authority": module.IMPORT_AUTHORITY,
                         "handoff195_CI": check, "activation_authorized": False, "model_execution_authorized": False, "scientific_readiness": False}
            module.verify_authority(authority)
            for changes in ({"checkpoint": 197.0}, {"review196_sha256": "drift"}, {"import_authority": "prepare_only"}, {"activation_authorized": True},
                            {"model_execution_authorized": True}, {"scientific_readiness": True}, {"handoff195_CI": {**check, "run_id": float(check["run_id"])}},
                            *({"handoff195_CI": {**check, field: "drift"}} for field in check)):
                with self.assertRaises(ValueError):
                    module.verify_authority({**authority, **changes})
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-batch07-import", root / "review/overlap"):
                    with self.assertRaises(ValueError):
                        module.import_review(Namespace(preflight=root / "preflight.json", review_root=root / "review", human_input=root / "review/input.json", out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch09_import_review230_strict_outcomes_preservation_and_pending(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_categorical_batch09 as module
            import diagnose_oulu_batch09_input as diagnostic
            digest = "a" * 64
            dispositions = [rule["disposition"] for rule in module.CATEGORICAL_RULES]
            definition = {field: digest for field in diagnostic.GLOBAL_BINDINGS}
            definition.update({"categorical_rules": module.CATEGORICAL_RULES,
                               "pairs": [{"queue_rank": rank, **{field: digest for field in diagnostic.PAIR_BINDINGS},
                                          "required_assets_sha256": {f"assets/{rank:06d}/{name}.png": digest for name in ("temporal_a", "temporal_b", "trigger")},
                                          "ai_disposition": "rejected_false_positive"} for rank in range(80, 85)]})
            record = {field: digest for field in diagnostic.GLOBAL_BINDINGS}
            record.update({"version": 1, "record_type": "batch09_categorical_review", "review_definition_sha256": digest,
                           "reviewer": {"kind": "owner_human", "id": "synthetic-only", "personally_inspected_bound_evidence": True},
                           "reviewed_at_utc": "2026-10-20T00:00:00Z", "stop_for_prospective_scientific_decision": False,
                           "pairs": [{**{field: pair[field] for field in ("queue_rank", *diagnostic.PAIR_BINDINGS)},
                                      "reviewed_assets_sha256": pair["required_assets_sha256"], "evidence_sufficient": True,
                                      "same_or_derived_content": False, "personal_inspection_attested": True, "owner_decision_attested": True,
                                      "disposition": "rejected_false_positive", "capture_provenance_certified": False,
                                      "stop_for_prospective_scientific_decision": False} for pair in definition["pairs"]]})
            def validate(value, source=definition):
                return module.validate_input(json.dumps(value).encode(), source, digest)
            original, outcomes = validate(record)
            self.assertEqual(original, record)
            self.assertTrue(all(not row["reconciliation_required"] for row in outcomes))
            for row, supplied in zip(outcomes, record["pairs"], strict=True):
                self.assertEqual({field: row[field] for field in supplied}, supplied)
                for field in ("effective_disposition_activated", "counts_as_accepted_current_effective_disposition", "model_execution_authorized", "scientific_readiness"):
                    self.assertIs(row[field], False)
                self.assertTrue(row["checkpoint_review_pending"] and row["semantic_acceptance_pending"])
            for sufficient, same, disposition in [(False, None, "uncertain_insufficient_evidence"), (True, True, "confirmed_same_content_or_derived_lineage"), (True, False, "rejected_false_positive")]:
                stop = same is True
                changed = {**record, "stop_for_prospective_scientific_decision": stop,
                           "pairs": [{**record["pairs"][0], "evidence_sufficient": sufficient, "same_or_derived_content": same,
                                      "disposition": disposition, "stop_for_prospective_scientific_decision": stop}, *record["pairs"][1:]]}
                _, rows = validate(changed)
                self.assertEqual(rows[0]["validated_disposition"], disposition)
                self.assertIs(rows[0]["scientific_stop_independently_derived"], stop)
                self.assertEqual(rows[0]["reconciliation_required"], disposition != "rejected_false_positive")
                with self.assertRaises(module.OutcomeDiscrepancy) as error:
                    validate({**changed, "stop_for_prospective_scientific_decision": not stop})
                self.assertIs(error.exception.scientific_stop_required, stop)
            self.assertEqual(set(dispositions), {"uncertain_insufficient_evidence", "confirmed_same_content_or_derived_lineage", "rejected_false_positive"})
            for field in ("personal_inspection_attested", "owner_decision_attested", "capture_provenance_certified"):
                changed = {**record, "pairs": [{**record["pairs"][0], field: field == "capture_provenance_certified"}, *record["pairs"][1:]]}
                self.assertTrue(diagnostic.diagnose_bytes(json.dumps(changed).encode(), definition, digest)["structure_types_pass"])
                with self.assertRaises(ValueError):
                    validate(changed)
            bad_rows = [{"evidence_sufficient": None}, {"evidence_sufficient": 1}, {"same_or_derived_content": None},
                        {"disposition": "clear"}, {"stop_for_prospective_scientific_decision": True}, {"queue_rank": 80.0},
                        *({field: "drift"} for field in diagnostic.PAIR_BINDINGS), {"reviewed_assets_sha256": {}}]
            for changes in bad_rows:
                with self.assertRaises(ValueError):
                    validate({**record, "pairs": [{**record["pairs"][0], **changes}, *record["pairs"][1:]]})
            for field in module.DERIVED_FIELDS:
                with self.assertRaises(ValueError):
                    validate({**record, "pairs": [{**record["pairs"][0], field: False}, *record["pairs"][1:]]})
            for changes in ({"version": True}, {"record_type": "batch08_categorical_review"}, {"reviewer": {**record["reviewer"], "id": " "}},
                            {"reviewer": {**record["reviewer"], "personally_inspected_bound_evidence": False}}, {"reviewed_at_utc": "2026-10-20T00:00:00+01:00"},
                            {"pairs": record["pairs"][:-1]}, {"pairs": [record["pairs"][0]] * 5}, *({field: "drift"} for field in diagnostic.GLOBAL_BINDINGS)):
                with self.assertRaises(ValueError):
                    validate({**record, **changes})
            with self.assertRaises(ValueError):
                validate(record, {**definition, "categorical_rules": [{**module.CATEGORICAL_RULES[0], "evidence_sufficient": 0}, *module.CATEGORICAL_RULES[1:]]})
            for payload in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e999}', b'[]', b'null', b'{', b'\xff'):
                with self.assertRaises(ValueError):
                    module.validate_input(payload, definition, digest)
            import ast
            import hashlib
            from argparse import Namespace
            from unittest.mock import patch
            flags = {"import_authorized": True, **{field: False for field in ("human_input_collection_authorized", "effective_activation_authorized", "model_execution_authorized", "scientific_readiness")}}
            authority = {**flags, "checkpoint": 231, "review230_sha256": module.REVIEW_SHA256, "review228_sha256": diagnostic.REVIEW_SHA256,
                         "diagnostic_document_sha256": module.DIAGNOSTIC_DOCUMENT_SHA256, "diagnostic_report_sha256": module.DIAGNOSTIC_REPORT_SHA256,
                         "prospective_criteria_sha256": module.CRITERIA_SHA256, "input_sha256": module.INPUT_SHA256, "input_byte_size": 6710, "source229_CI": module.SOURCE229_CI}
            module.verify_authority(authority)
            for changes in ({"checkpoint": 231.0}, {"review230_sha256": digest}, {"input_sha256": digest}, {"input_byte_size": 6710.0},
                            *({field: not value} for field, value in flags.items()), {"source229_CI": {**module.SOURCE229_CI, "run_id": 0}},
                            {"source229_CI": {**module.SOURCE229_CI, "all_steps_success": 1}}):
                with self.assertRaises(ValueError):
                    module.verify_authority({**authority, **changes})
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                current_test = root / "tests/test_oulu.py"
                current_test.parent.mkdir()
                prior_source = "class PriorTests:\n    def existing_test(self):\n        pass\n"
                current_source = prior_source + f"    def {module.NEW_TEST_METHOD}(self):\n        pass\n"
                current_test.write_text(current_source)
                prior_sha = hashlib.sha256(prior_source.encode()).hexdigest()
                prior_ast = hashlib.sha256(ast.dump(ast.parse(prior_source)).encode()).hexdigest()
                original = {"protected_snapshots": {str(root / f"prior{index}"): {} for index in range(98)},
                            "pinned_file_sha256": {str(current_test): prior_sha, **{str(root / f"pin{index}"): digest for index in range(277)}},
                            "frozen_file_sha256": {}, "study_config_sha256": {}, "main_root": str(root / "main"), "sibling_root": str(root / "sibling"),
                            "input_path": str(root / "main" / diagnostic.INPUT_NAME), "input_identity": {"synthetic": 1}, "input_sha256": module.INPUT_SHA256, "input_byte_size": 6710}
                confirmation = {"input_sha256": module.INPUT_SHA256, "classification": "owner_self_attested_genuine_export_intended_submission",
                                "blank_form_sequence": "owner_attested_completed_before_genuine_judgments", "separate_synthetic_sequence": "owner_attested_completed_before_genuine_judgments",
                                "independent_owner_authentication_claimed": False, "retrospective_collection_authority": False}
                records = {"diagnostic_preflight_path": ("private_preflight_sha256", original),
                           "diagnostic_main_path": ("private_diagnostic_main_sha256", {}), "diagnostic_sibling_path": ("private_diagnostic_sibling_sha256", {}),
                           "owner_confirmation_path": ("private_owner_confirmation_sha256", confirmation)}
                report, paths = {}, {}
                for field, (public_field, value) in records.items():
                    path = root / field / "record.json"
                    path.parent.mkdir()
                    path.write_text(json.dumps(value))
                    paths[field] = str(path)
                    report[public_field] = module._sha256(path)
                verification_path = root / "verification.json"
                verification_path.write_text(json.dumps({"owner_confirmation_sha256": report["private_owner_confirmation_sha256"], "input_sha256": module.INPUT_SHA256}))
                paths["diagnostic_verification_path"] = str(verification_path)
                report["private_verification_sha256"] = module._sha256(verification_path)
                context = {**original, **paths, "pinned_file_sha256": {**original["pinned_file_sha256"], str(current_test): module._sha256(current_test)},
                           "protected_snapshots": {**original["protected_snapshots"], **{str(Path(paths[field]).parent): {"record.json": report[public_field]}
                                                   for field, public_field in (("diagnostic_main_path", "private_diagnostic_main_sha256"), ("diagnostic_sibling_path", "private_diagnostic_sibling_sha256"))}},
                           "test_transition": {"old_sha256": prior_sha, "new_sha256": module._sha256(current_test), "only_added_test": module.NEW_TEST_METHOD, "prior_test_AST_unchanged": True}}
                with patch.object(module, "ROOT", root), patch.object(module, "OLD_TEST_SHA256", prior_sha), patch.object(module, "OLD_TEST_AST_SHA256", prior_ast):
                    self.assertEqual(module.verify_context(context, report), original)
                    for changes in ({"pinned_file_sha256": {}}, {"frozen_file_sha256": {"drift": digest}}, {"study_config_sha256": {"drift": digest}},
                                    {"protected_snapshots": original["protected_snapshots"]}, {"input_identity": {"drift": 1}}, {"input_path": str(root / "other.json")},
                                    {"test_transition": {**context["test_transition"], "only_added_test": "wrong"}}):
                        with self.assertRaises(ValueError):
                            module.verify_context({**context, **changes}, report)
                    with self.assertRaises(ValueError):
                        module.verify_context(context, {**report, "private_owner_confirmation_sha256": digest})
                    current_test.write_text(current_source.replace("def existing_test", "def changed_prior_test"))
                    with self.assertRaises(ValueError):
                        module.verify_context({**context, "test_transition": {**context["test_transition"], "new_sha256": module._sha256(current_test)}}, report)
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused231", root / "source"):
                    with self.assertRaises(ValueError):
                        module.import_review(Namespace(preflight=root / "absent.json", human_input=root / "source/input.json", out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch09_input_diagnostics_review228_strict_read_and_bindings_only(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import diagnose_oulu_batch09_input as module
            from argparse import Namespace
            from unittest.mock import patch
            digest = "a" * 64
            definition = {field: digest for field in module.GLOBAL_BINDINGS}
            definition["pairs"] = [{"queue_rank": rank, **{field: digest for field in module.PAIR_BINDINGS},
                                    "required_assets_sha256": {f"assets/{rank:06d}/{name}.png": digest for name in ("temporal_a", "temporal_b", "trigger")}}
                                   for rank in range(80, 85)]
            record = {field: digest for field in module.GLOBAL_BINDINGS}
            record.update({"version": 1, "record_type": "batch09_categorical_review", "review_definition_sha256": digest,
                           "reviewer": {"kind": "owner_human", "id": "synthetic-only", "personally_inspected_bound_evidence": True},
                           "reviewed_at_utc": "2026-10-20T00:00:00Z", "stop_for_prospective_scientific_decision": False,
                           "pairs": [{**{field: pair[field] for field in ("queue_rank", *module.PAIR_BINDINGS)},
                                      "reviewed_assets_sha256": pair["required_assets_sha256"], "evidence_sufficient": False,
                                      "same_or_derived_content": None, "personal_inspection_attested": True, "owner_decision_attested": True,
                                      "disposition": "not-validated-by-diagnostic", "capture_provenance_certified": False,
                                      "stop_for_prospective_scientific_decision": False} for pair in definition["pairs"]]})
            def check(value):
                return module.diagnose_bytes(json.dumps(value).encode(), definition, digest)
            result = check(record)
            self.assertTrue(all(result[field] for field in ("strict_JSON_pass", "structure_types_pass", "source_bindings_pass", "exact_ordered_ranks_pass")))
            self.assertEqual(result["rows_examined"], 5)
            self.assertFalse(result["outcomes_validated"])
            self.assertFalse(result["scientific_stop_flags_validated"])
            self.assertEqual(result["normalized_human_rows_created"], 0)
            for payload in (b'{"a":1,"a":2}', b'{"a":{"b":1,"b":2}}', b'{"a":NaN}', b'{"a":Infinity}', b'{"a":1e999}', b'[]', b'null', b'{', b'\xff'):
                self.assertFalse(module.diagnose_bytes(payload, definition, digest)["strict_JSON_pass"])
            for field in module.GLOBAL_BINDINGS:
                self.assertFalse(check({**record, field: "drift"})["source_bindings_pass"])
            self.assertFalse(check({**record, "review_definition_sha256": "drift"})["source_bindings_pass"])
            for rows in (record["pairs"][:-1], list(reversed(record["pairs"])), [{**record["pairs"][0], "queue_rank": 80.0}, *record["pairs"][1:]], [record["pairs"][0]] * 5):
                self.assertFalse(check({**record, "pairs": rows})["exact_ordered_ranks_pass"])
            for changes in ({"version": True}, {"reviewer": {}}, {"reviewed_at_utc": "2026-10-20"}, {"stop_for_prospective_scientific_decision": 0}, {"human_rationale": "not-requested"}):
                self.assertFalse(check({**record, **changes})["structure_types_pass"])
            for changes in ({"evidence_sufficient": 0}, {"same_or_derived_content": False}, {"owner_decision_attested": 1}, {"disposition": None}, {"stop_for_prospective_scientific_decision": "false"}):
                self.assertFalse(check({**record, "pairs": [{**record["pairs"][0], **changes}, *record["pairs"][1:]]})["structure_types_pass"])
            for field in (*module.PAIR_BINDINGS, "reviewed_assets_sha256"):
                self.assertFalse(check({**record, "pairs": [{**record["pairs"][0], field: {}}, *record["pairs"][1:]]})["source_bindings_pass"])
            changed_labels = {**record, "stop_for_prospective_scientific_decision": True,
                              "pairs": [{**row, "disposition": "another-unvalidated-label", "stop_for_prospective_scientific_decision": True} for row in record["pairs"]]}
            self.assertEqual(check(changed_labels), result)
            flags = {field: False for field in ("human_input_collection_authorized", "import_authorized", "effective_activation_authorized", "model_execution_authorized", "scientific_readiness")}
            authority = {**flags, "checkpoint": 229, "review228_sha256": module.REVIEW_SHA256,
                         "handoff_document_sha256": module.HANDOFF_DOCUMENT_SHA256, "handoff_report_sha256": module.HANDOFF_REPORT_SHA256,
                         "prospective_criteria_sha256": module.CRITERIA_SHA256, "diagnostic_only_authorized": True, "source227_CI": module.SOURCE227_CI}
            module.verify_authority(authority)
            for changes in ({"checkpoint": 229.0}, {"review228_sha256": digest}, {"diagnostic_only_authorized": False},
                            *({field: True} for field in flags), {"source227_CI": {**module.SOURCE227_CI, "run_id": 0}}):
                with self.assertRaises(ValueError):
                    module.verify_authority({**authority, **changes})
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                path = root / "input.json"
                payload = json.dumps(record).encode()
                path.write_bytes(payload)
                data, identity = module.stable_read(path)
                self.assertEqual(data, payload)
                self.assertEqual(module.stable_read(path, identity), (payload, identity))
                with self.assertRaises(ValueError):
                    module.stable_read(path, {**identity, "byte_size": 0})
                link = root / "link"
                link.symlink_to(path)
                with self.assertRaises(ValueError):
                    module.stable_read(link)
                with self.assertRaises(ValueError):
                    module.snapshot(root)
                link.unlink()
                original_identity = module.file_identity
                for changed_call in (2, 3, 4):
                    calls = []
                    def unstable(value):
                        calls.append(value)
                        found = original_identity(value)
                        return {**found, "inode": -1} if len(calls) == changed_call else found
                    with patch.object(module, "file_identity", side_effect=unstable), self.assertRaises(ValueError):
                        module.stable_read(path)
                with self.assertRaises(ValueError):
                    module.stable_read(root)
                for output in (root, ROOT / "results/refused229", root / "source"):
                    with self.assertRaises(ValueError):
                        module.diagnose(Namespace(preflight=root / "absent.json", input=root / "source/input.json", out_root=output))
            import ast
            import hashlib
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                current_test = root / "tests/test_oulu.py"
                current_test.parent.mkdir()
                prior_source = "class PriorTests:\n    def existing_test(self):\n        pass\n"
                current_source = prior_source + f"    def {module.NEW_TEST_METHOD}(self):\n        pass\n"
                current_test.write_text(current_source)
                prior_sha = hashlib.sha256(prior_source.encode()).hexdigest()
                prior_ast = hashlib.sha256(ast.dump(ast.parse(prior_source)).encode()).hexdigest()
                original = {"protected_snapshots": {str(root / f"prior{index}"): {} for index in range(96)},
                            "pinned_file_sha256": {str(current_test): prior_sha, **{str(root / f"pin{index}"): digest for index in range(271)}},
                            "frozen_file_sha256": {}, "study_config_sha256": {}}
                original_path = root / "original.json"
                original_path.write_text(json.dumps(original))
                core = {f"prepared{index}": digest for index in range(18)}
                verification = {"prepared_core_file_sha256": core, "main_root": str(root / "main"), "sibling_root": str(root / "sibling")}
                verification_path = root / "verification.json"
                verification_path.write_text(json.dumps(verification))
                report = {"private_preflight_sha256": module._sha256(original_path), "private_blocked_verification_sha256": module._sha256(verification_path),
                          "prepared_core_map_sha256": hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode()).hexdigest()}
                context = {**original, "protected_snapshots": {**original["protected_snapshots"], verification["main_root"]: {**core, module.INPUT_NAME: digest}, verification["sibling_root"]: core},
                           "pinned_file_sha256": {**original["pinned_file_sha256"], str(current_test): module._sha256(current_test)},
                           "handoff_preflight_path": str(original_path), "handoff_verification_path": str(verification_path), "original_prepared_core_sha256": core,
                           "main_root": verification["main_root"], "sibling_root": verification["sibling_root"],
                           "input_path": str(root / "main" / module.INPUT_NAME), "input_sha256": digest,
                           "test_transition": {"old_sha256": prior_sha, "new_sha256": module._sha256(current_test), "only_added_test": module.NEW_TEST_METHOD, "prior_test_AST_unchanged": True}}
                with patch.object(module, "ROOT", root), patch.object(module, "OLD_TEST_SHA256", prior_sha), patch.object(module, "OLD_TEST_AST_SHA256", prior_ast):
                    self.assertEqual(module.verify_context(context, report), verification)
                    for changes in ({"pinned_file_sha256": {}}, {"frozen_file_sha256": {"drift": digest}}, {"study_config_sha256": {"drift": digest}},
                                    {"protected_snapshots": original["protected_snapshots"]}, {"input_sha256": "drift"}, {"input_path": str(root / "other.json")},
                                    {"original_prepared_core_sha256": {}}, {"test_transition": {**context["test_transition"], "only_added_test": "wrong"}}):
                        with self.assertRaises(ValueError):
                            module.verify_context({**context, **changes}, report)
                    with self.assertRaises(ValueError):
                        module.verify_context(context, {**report, "private_blocked_verification_sha256": digest})
                    current_test.write_text(current_source.replace("def existing_test", "def changed_prior_test"))
                    with self.assertRaises(ValueError):
                        module.verify_context({**context, "test_transition": {**context["test_transition"], "new_sha256": module._sha256(current_test)}}, report)
        finally:
            sys.path.pop(0)

    def test_batch09_categorical_handoff_review226_blank_controls_and_provenance(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_categorical_batch09 as module
            digest = "a" * 64
            dependence = {"exact_reused_video_rank_groups": {"synthetic": [81, 82]},
                          "visually_correlated_configuration_rank_groups": [{"ranks": [81, 82, 84]}]}
            pairs = [{"queue_rank": rank, "packet_sha256": digest, "ai_record_sha256": digest, "source_sampling_provenance_sha256": digest,
                      "exact_pair_record_sha256": digest, "ai_disposition": "uncertain_insufficient_evidence", "ai_observations": ["</script>"],
                      "human_review_notice": module.human_notice(rank, dependence),
                      "required_assets_sha256": {f"assets/{rank:06d}/{name}.png": digest for name in ("temporal_a", "temporal_b", "trigger")}} for rank in module.TARGET_RANKS]
            authority = {"review226_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                         "accepted_AI_document_sha256": module.AI_DOCUMENT_SHA256, "accepted_packet_report_sha256": module.PACKET_REPORT_SHA256}
            definition = {**authority, "pairs": pairs, "preflight_sha256": digest, "observation_input_sha256": digest,
                          "source_packet_lineage_sha256": digest, "source_packet_summary_sha256": digest,
                          "categorical_rules": module.CATEGORICAL_RULES, "dependence": dependence, "dependence_sha256": module.structured_digest(dependence)}
            before = json.dumps(definition, sort_keys=True)
            page = module.render_categorical(definition, digest)
            data, _ = json.JSONDecoder().raw_decode(page.split("const DATA=", 1)[1])
            self.assertEqual(data, {"definition": definition, "sha256": digest})
            self.assertEqual(before, json.dumps(definition, sort_keys=True))
            for fragment in ("evidence_sufficient:null", "same_or_derived_content:null", "personal_inspection_attested:null", "owner_decision_attested:null",
                             "submitted:false", "names.length===3", "names.every", "item.personal_inspection_attested===true", "item.owner_decision_attested===true",
                             "state[current].same_or_derived_content=null", "state[current].submitted=false", "details.hidden=true", "state[current].submitted!==true",
                             "if(!exportReady())return", "source_sampling_provenance_sha256:pair.source_sampling_provenance_sha256",
                             "review226_sha256:DATA.definition.review226_sha256", "observation_input_sha256:DATA.definition.observation_input_sha256",
                             "accepted_AI_document_sha256:DATA.definition.accepted_AI_document_sha256", "dependence_sha256:DATA.definition.dependence_sha256",
                             "batch09_categorical_review", "oulu-batch09-categorical-review.json", "rows.some", "\\u003c/script>"):
                self.assertIn(fragment, page)
            for fragment in ("createElement('textarea')", "rationale:", "formal_review_record_sha256", "review194", "batch07_categorical_review"):
                self.assertNotIn(fragment, page)
            for changes in ({**{field: digest for field in authority}}, {"preflight_sha256": ""}, {"observation_input_sha256": ""},
                            {"source_packet_lineage_sha256": ""}, {"dependence_sha256": digest}, {"categorical_rules": []},
                            {"categorical_rules": [{**module.CATEGORICAL_RULES[0], "evidence_sufficient": 0}, *module.CATEGORICAL_RULES[1:]]},
                            {"pairs": pairs[:-1]}, {"pairs": list(reversed(pairs))}, {"pairs": [{**pairs[0], "queue_rank": 80.0}, *pairs[1:]]},
                            {"pairs": [{**pairs[0], "human_review_notice": "Reject"}, *pairs[1:]]}, {"pairs": [{**pairs[0], "source_sampling_provenance_sha256": ""}, *pairs[1:]]},
                            {"pairs": [{**pairs[0], "required_assets_sha256": {}}, *pairs[1:]]}, {"pairs": [{**pairs[0], "ai_disposition": "clear"}, *pairs[1:]]}):
                with self.assertRaises(ValueError):
                    module.render_categorical({**definition, **changes}, digest)
            flags = {field: False for field in ("human_input_collection_authorized", "import_authorized", "effective_activation_authorized", "model_execution_authorized", "scientific_readiness")}
            preflight = {**authority, **flags, "checkpoint": 227, "queue_ranks": list(module.TARGET_RANKS), "source225_CI": module.SOURCE225_CI}
            module.verify_authority(preflight)
            for changes in ({"checkpoint": 227.0}, {"queue_ranks": list(range(80, 90))}, {"queue_ranks": [80.0, *range(81, 85)]},
                            *({field: True} for field in flags), *({field: digest} for field in authority),
                            *({"source225_CI": {**module.SOURCE225_CI, field: "drift"}} for field in module.SOURCE225_CI),
                            {"source225_CI": {**module.SOURCE225_CI, "run_id": float(module.SOURCE225_CI["run_id"])}}):
                with self.assertRaises(ValueError):
                    module.verify_authority({**preflight, **changes})
            self.assertIn("exact source video", module.human_notice(81, dependence))
            self.assertIn("dependent", module.human_notice(82, dependence))
            self.assertIn("correlated", module.human_notice(84, dependence))
            import ast
            import hashlib
            from unittest.mock import patch
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                current_test = root / "tests/test_oulu.py"
                current_test.parent.mkdir()
                prior_source = "class EarlierTests:\n    def existing_test(self):\n        pass\n"
                current_source = prior_source + f"    def {module.NEW_TEST_METHOD}(self):\n        pass\n"
                current_test.write_text(current_source)
                prior_sha = hashlib.sha256(prior_source.encode()).hexdigest()
                prior_ast = hashlib.sha256(ast.dump(ast.parse(prior_source)).encode()).hexdigest()
                original = {"protected_snapshots": {str(root / f"prior{index}"): {} for index in range(94)},
                            "pinned_file_sha256": {str(current_test): prior_sha}, "frozen_file_sha256": {}, "study_config_sha256": {}}
                original_path = root / "original.json"
                original_path.write_text(json.dumps(original))
                observed = {**dependence, "preflight_sha256": module._sha256(original_path)}
                observed_path = root / "observations.json"
                observed_path.write_text(json.dumps(observed))
                verification_path = root / "verification.json"
                file_map = {"definition.json": digest}
                verification_path.write_text(json.dumps({"output_file_sha256": file_map}))
                report = {"private_preflight_sha256": module._sha256(original_path), "observation_input_sha256": module._sha256(observed_path),
                          "private_verification_sha256": module._sha256(verification_path)}
                context = {**original, "protected_snapshots": {**original["protected_snapshots"], str(root / "ai"): file_map, str(root / "sibling"): file_map},
                           "pinned_file_sha256": {str(current_test): module._sha256(current_test)}, "AI_preflight_path": str(original_path),
                           "observations_path": str(observed_path), "AI_verification_path": str(verification_path), "ai_root": str(root / "ai"),
                           "ai_sibling_root": str(root / "sibling"), "dependence": dependence,
                           "test_transition": {"old_sha256": prior_sha, "new_sha256": module._sha256(current_test),
                                               "only_added_test": module.NEW_TEST_METHOD, "prior_test_AST_unchanged": True}}
                with patch.object(module, "ROOT", root), patch.object(module, "OLD_TEST_SHA256", prior_sha), patch.object(module, "OLD_TEST_AST_SHA256", prior_ast):
                    self.assertEqual(module.verify_source_context(context, report), observed)
                    for changes in ({"pinned_file_sha256": {}}, {"frozen_file_sha256": {"drift": digest}}, {"study_config_sha256": {"drift": digest}},
                                    {"protected_snapshots": original["protected_snapshots"]},
                                    {"protected_snapshots": {name: value for name, value in context["protected_snapshots"].items() if name != str(root / "prior0")}},
                                    {"dependence": {**dependence, "exact_reused_video_rank_groups": {}}},
                                    {"test_transition": {**context["test_transition"], "only_added_test": "wrong"}}):
                        with self.assertRaises(ValueError):
                            module.verify_source_context({**context, **changes}, report)
                    with self.assertRaises(ValueError):
                        module.verify_source_context(context, {**report, "observation_input_sha256": digest})
                    current_test.write_text(current_source.replace("def existing_test", "def changed_prior_test"))
                    with self.assertRaises(ValueError):
                        module.verify_source_context({**context, "test_transition": {**context["test_transition"], "new_sha256": module._sha256(current_test)}}, report)
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-batch09-categorical", root / "source/overlap"):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(preflight=root / "preflight.json", packet_root=root / "source", ai_root=root / "ai", out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch08_categorical_handoff_acceptance_authority_and_blank_controls(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_categorical_batch08 as module
            digest = "a" * 64
            pairs = [{"queue_rank": rank, "packet_sha256": digest, "ai_record_sha256": digest, "formal_review_record_sha256": digest,
                      "exact_pair_record_sha256": digest, "ai_disposition": "rejected_false_positive", "ai_observations": ["</script>"],
                      "human_review_notice": module.human_notice(rank),
                      "required_assets_sha256": {f"assets/{rank:06d}/{name}.png": digest for name in ("temporal_a", "temporal_b", "trigger")}} for rank in module.TARGET_RANKS]
            definition = {"pairs": pairs, "review208_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                          "accepted_formal_report_sha256": module.FORMAL_REPORT_SHA256, "preflight_sha256": digest, "categorical_rules": module.CATEGORICAL_RULES}
            before = json.dumps(definition, sort_keys=True)
            page = module.render_categorical(definition, digest)
            data, _ = json.JSONDecoder().raw_decode(page.split("const DATA=", 1)[1])
            self.assertEqual(data, {"definition": definition, "sha256": digest})
            self.assertEqual(json.dumps(definition, sort_keys=True), before)
            for fragment in ("evidence_sufficient:null", "same_or_derived_content:null", "personal_inspection_attested:null", "owner_decision_attested:null",
                             "submitted:false", "item.personal_inspection_attested===true", "item.owner_decision_attested===true", "names.length===3", "names.every",
                             "state[current].same_or_derived_content=null", "state[current].submitted=false", "details.hidden=true", "state[current].submitted!==true",
                             "if(!exportReady())return", "ai_record_sha256:pair.ai_record_sha256", "formal_review_record_sha256:pair.formal_review_record_sha256",
                             "exact_pair_record_sha256:pair.exact_pair_record_sha256", "review208_sha256:DATA.definition.review208_sha256",
                             "accepted_formal_report_sha256:DATA.definition.accepted_formal_report_sha256", "batch08_categorical_review",
                             "oulu-batch08-categorical-review.json", "rows.some", "\\u003c/script>"):
                self.assertIn(fragment, page)
            for fragment in ("createElement('textarea')", "rationale:", "imported_human_record", "review194", "batch07_categorical_review"):
                self.assertNotIn(fragment, page)
            for changes in ({"review208_sha256": digest}, {"accepted_AI_report_sha256": digest}, {"accepted_formal_report_sha256": digest},
                            {"preflight_sha256": ""}, {"categorical_rules": []}, {"categorical_rules": [{**module.CATEGORICAL_RULES[0], "evidence_sufficient": 0}, *module.CATEGORICAL_RULES[1:]]},
                            {"pairs": pairs[:-1]}, {"pairs": list(reversed(pairs))}, {"pairs": [{**pairs[0], "queue_rank": 70.0}, *pairs[1:]]},
                            {"pairs": [{**pairs[0], "human_review_notice": "Reject"}, *pairs[1:]]}, {"pairs": [{**pairs[0], "formal_review_record_sha256": ""}, *pairs[1:]]},
                            {"pairs": [{**pairs[0], "required_assets_sha256": {}}, *pairs[1:]]}, {"pairs": [{**pairs[0], "ai_disposition": "clear"}, *pairs[1:]]}):
                with self.assertRaises(ValueError):
                    module.render_categorical({**definition, **changes}, digest)
            check = {"head_sha": "aca26b2be9be330811401a5a6e861fbca2667bf1", "run_id": 38865644147, "job_id": 116857727094,
                     "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success"}
            authority = {"checkpoint": 209, "review208_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                         "accepted_formal_report_sha256": module.FORMAL_REPORT_SHA256, "queue_ranks": list(module.TARGET_RANKS), "source207_CI": check,
                         **{field: False for field in ("human_input_collection_authorized", "import_authorized", "effective_activation_authorized", "model_execution_authorized", "scientific_readiness")}}
            module.verify_authority(authority)
            for changes in ({"checkpoint": 209.0}, {"queue_ranks": list(range(80, 85))}, {"queue_ranks": [70.0, *range(71, 80)]},
                            {"human_input_collection_authorized": True}, {"import_authorized": True}, {"effective_activation_authorized": True},
                            {"model_execution_authorized": True}, {"scientific_readiness": True}, {"review208_sha256": digest},
                            {"accepted_formal_report_sha256": digest}, {"source207_CI": {**check, "run_id": float(check["run_id"])}},
                            *({"source207_CI": {**check, field: "drift"}} for field in check)):
                with self.assertRaises(ValueError):
                    module.verify_authority({**authority, **changes})
            self.assertIn("Underexposure", module.human_notice(73))
            for rank in (70, 71, 72, 73, 74, 79):
                self.assertIn("correlated", module.human_notice(rank))
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-batch08-categorical", root / "source/overlap"):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(preflight=root / "preflight.json", packet_root=root / "source", ai_root=root / "ai", formal_root=root / "formal", out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch07_categorical_handoff_authority_blank_answers_and_uncertainty(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_categorical_batch07 as module
            digest = "a" * 64
            pairs = [{"queue_rank": rank, "packet_sha256": digest, "ai_record_sha256": digest, "exact_pair_record_sha256": digest,
                      "ai_disposition": "uncertain_insufficient_evidence" if rank == 66 else "rejected_false_positive",
                      "ai_observations": ["</script>"], "human_review_notice": module.human_notice(rank),
                      "required_assets_sha256": {f"assets/{rank:06d}/{name}.png": digest for name in ("temporal_a", "temporal_b", "trigger")}} for rank in module.TARGET_RANKS]
            definition = {"pairs": pairs, "review194_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                          "preflight_sha256": digest, "categorical_rules": module.CATEGORICAL_RULES}
            before = json.dumps(definition, sort_keys=True)
            page = module.render_categorical(definition, digest)
            data, _ = json.JSONDecoder().raw_decode(page.split("const DATA=", 1)[1])
            self.assertEqual(data, {"definition": definition, "sha256": digest})
            self.assertEqual(json.dumps(definition, sort_keys=True), before)
            for fragment in ("evidence_sufficient:null", "same_or_derived_content:null", "personal_inspection_attested:null", "owner_decision_attested:null",
                             "submitted:false", "item.personal_inspection_attested===true", "item.owner_decision_attested===true", "names.length===3", "names.every",
                             "state[current].same_or_derived_content=null", "state[current].submitted=false", "details.hidden=true", "state[current].submitted!==true",
                             "if(!exportReady())return", "ai_record_sha256:pair.ai_record_sha256", "exact_pair_record_sha256:pair.exact_pair_record_sha256",
                             "review194_sha256:DATA.definition.review194_sha256", "batch07_categorical_review", "oulu-batch07-categorical-review.json", "rows.some", "\\u003c/script>"):
                self.assertIn(fragment, page)
            for fragment in ("createElement('textarea')", "rationale:", "imported_human_record", "review184", "rank47", "batch06_categorical_review"):
                self.assertNotIn(fragment, page)
            for changes in ({"review194_sha256": digest}, {"accepted_AI_report_sha256": digest}, {"preflight_sha256": ""}, {"categorical_rules": []},
                            {"categorical_rules": [{**module.CATEGORICAL_RULES[0], "evidence_sufficient": 0}, *module.CATEGORICAL_RULES[1:]]},
                            {"pairs": pairs[:-1]}, {"pairs": list(reversed(pairs))}, {"pairs": [{**pairs[0], "queue_rank": 60.0}, *pairs[1:]]},
                            {"pairs": [{**pairs[0], "human_review_notice": "Reject"}, *pairs[1:]]}, {"pairs": [{**pairs[0], "ai_record_sha256": ""}, *pairs[1:]]},
                            {"pairs": [{**pairs[0], "required_assets_sha256": {}}, *pairs[1:]]}, {"pairs": [{**pairs[0], "ai_disposition": "clear"}, *pairs[1:]]}):
                with self.assertRaises(ValueError):
                    module.render_categorical({**definition, **changes}, digest)
            check = {"head_sha": "7f998d71dabd8f629f9f117970ce58acdacf7931", "run_id": 38706506199, "job_id": 116327125698,
                     "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success"}
            authority = {"checkpoint": 195, "review194_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                         "queue_ranks": list(module.TARGET_RANKS), "source193_CI": check,
                         **{field: False for field in ("human_input_collection_authorized", "import_authorized", "effective_activation_authorized", "model_execution_authorized", "scientific_readiness")}}
            module.verify_authority(authority)
            for changes in ({"checkpoint": 195.0}, {"queue_ranks": list(range(70, 80))}, {"queue_ranks": [60.0, *range(61, 70)]},
                            {"human_input_collection_authorized": True}, {"import_authorized": True}, {"effective_activation_authorized": True},
                            {"model_execution_authorized": True}, {"scientific_readiness": True}, {"review194_sha256": digest},
                            {"source193_CI": {**check, "run_id": float(check["run_id"])}},
                            *({"source193_CI": {**check, field: "drift"}} for field in check)):
                with self.assertRaises(ValueError):
                    module.verify_authority({**authority, **changes})
            self.assertIn("underexposure", module.human_notice(66))
            self.assertNotIn("uncertain_insufficient_evidence", module.human_notice(66))
            for rank in (67, 68):
                self.assertIn("correlated", module.human_notice(rank))
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-batch07-categorical", root / "source/overlap"):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(preflight=root / "preflight.json", packet_root=root / "source", ai_root=root / "ai", out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch06_categorical_import_strict_answers_bindings_and_owner_preservation(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_categorical_batch06 as module
            digest = "a" * 64
            pairs = [{"queue_rank": rank, "packet_sha256": digest, "ai_record_sha256": digest, "exact_pair_record_sha256": digest,
                      "required_assets_sha256": {f"assets/{rank:06d}/{name}.png": digest for name in ("temporal_a", "temporal_b", "trigger")},
                      "ai_disposition": "rejected_false_positive"} for rank in module.TARGET_RANKS]
            definition = {"sha256": digest, "review184_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                          "categorical_rules": module.CATEGORICAL_RULES, "pairs": pairs}
            human = {"version": 1, "record_type": "batch06_categorical_review", "review_definition_sha256": digest,
                     "review184_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                     "reviewer": {"kind": "owner_human", "id": "synthetic", "personally_inspected_bound_evidence": True},
                     "reviewed_at_utc": "2026-10-15T07:00:00Z", "stop_for_prospective_scientific_decision": False, "owner_extra": {"preserve": [1, False, None]},
                     "pairs": [{"queue_rank": pair["queue_rank"], "packet_sha256": digest, "ai_record_sha256": digest, "exact_pair_record_sha256": digest,
                                "reviewed_assets_sha256": pair["required_assets_sha256"], "evidence_sufficient": True, "same_or_derived_content": False,
                                "personal_inspection_attested": True, "owner_decision_attested": True, "capture_provenance_certified": False,
                                "disposition": "rejected_false_positive", "stop_for_prospective_scientific_decision": False, "owner_extra": {"preserve": [True, None]}} for pair in pairs]}
            before = json.dumps([human, definition], sort_keys=True)
            rows = module.validate_categorical(human, definition)
            self.assertEqual(json.dumps([human, definition], sort_keys=True), before)
            for original, row in zip(human["pairs"], rows, strict=True):
                self.assertTrue(all(row[field] == value for field, value in original.items()))
                self.assertFalse(row["effective_disposition_activated"] or row["reconciliation_required"])
                self.assertTrue(row["semantic_acceptance_pending"])
                self.assertNotIn("rationale", row)
            for field, value in (("queue_rank", 50.0), ("queue_rank", True), ("queue_rank", 51), ("packet_sha256", "drift"), ("ai_record_sha256", "drift"),
                                 ("exact_pair_record_sha256", "drift"), ("reviewed_assets_sha256", {}), ("evidence_sufficient", 1), ("same_or_derived_content", 0),
                                 ("same_or_derived_content", None), ("personal_inspection_attested", 1), ("owner_decision_attested", False), ("capture_provenance_certified", 0),
                                 ("disposition", "uncertain_insufficient_evidence"), ("stop_for_prospective_scientific_decision", 0), ("effective_disposition_activated", False),
                                 ("ai_disposition", "rejected_false_positive"), ("semantic_acceptance_pending", True)):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, "pairs": [{**human["pairs"][0], field: value}, *human["pairs"][1:]]}, definition)
            for changes in ({"version": True}, {"version": 1.0}, {"record_type": "batch05_targeted_categorical_review"}, {"review_definition_sha256": "drift"},
                            {"review184_sha256": "drift"}, {"accepted_AI_report_sha256": "drift"}, {"reviewed_at_utc": "2026-10-15T07:00:00"},
                            {"reviewed_at_utc": "2026-10-15T07:00:00+01:00"}, {"reviewer": {**human["reviewer"], "personally_inspected_bound_evidence": False}},
                            {"reviewer": {**human["reviewer"], "id": " "}}, {"pairs": human["pairs"][:-1]}, {"stop_for_prospective_scientific_decision": True}):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, **changes}, definition)
            for changes in ({"pairs": pairs[:-1]}, {"pairs": list(reversed(pairs))}, {"pairs": [{**pairs[0], "queue_rank": 50.0}, *pairs[1:]]},
                            {"categorical_rules": []}, {"categorical_rules": [{**module.CATEGORICAL_RULES[0], "evidence_sufficient": 0}, *module.CATEGORICAL_RULES[1:]]},
                            {"review184_sha256": "drift"}, {"accepted_AI_report_sha256": "drift"}):
                with self.assertRaises(ValueError):
                    module.validate_categorical(human, {**definition, **changes})
            for rule in module.CATEGORICAL_RULES:
                stop = rule["same_or_derived_content"] is True
                changed = {**human["pairs"][0], **rule, "stop_for_prospective_scientific_decision": stop}
                result = module.validate_categorical({**human, "pairs": [changed, *human["pairs"][1:]], "stop_for_prospective_scientific_decision": stop}, definition)[0]
                self.assertEqual(result["validated_disposition"], rule["disposition"])
                self.assertEqual(result["stop_for_prospective_scientific_decision"], stop)
                self.assertEqual(result["reconciliation_required"], rule["disposition"] != "rejected_false_positive")
                self.assertEqual(result["comparison_disposition"], "uncertain_insufficient_evidence" if result["reconciliation_required"] else result["disposition"])
                self.assertEqual(result["disposition"], rule["disposition"])
            for same in (True, False, 0, "false"):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, "pairs": [{**human["pairs"][0], "evidence_sufficient": False, "same_or_derived_content": same}, *human["pairs"][1:]]}, definition)
            self.assertEqual(len(module.validate_categorical({**human, "pairs": list(reversed(human["pairs"]))}, definition)), 10)
            check = {"head_sha": "ad9d5d7edc86a69e2e48a40f4a0ec13ed1d75a16", "run_id": 38690950258, "job_id": 116276475624,
                     "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success"}
            authority = {"checkpoint": 187, "review186_sha256": module.REVIEW186_SHA256, "import_authority": module.IMPORT_AUTHORITY,
                         "handoff185_CI": check, "activation_authorized": False, "model_execution_authorized": False, "scientific_readiness": False}
            module.verify_authority(authority)
            for changes in ({"checkpoint": 187.0}, {"review186_sha256": "drift"}, {"import_authority": "prepare_only"}, {"activation_authorized": True},
                            {"model_execution_authorized": True}, {"scientific_readiness": True}, *({"handoff185_CI": {**check, field: "drift"}} for field in check)):
                with self.assertRaises(ValueError):
                    module.verify_authority({**authority, **changes})
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-batch06-import", root / "review/overlap"):
                    with self.assertRaises(ValueError):
                        module.import_review(Namespace(preflight=root / "preflight.json", review_root=root / "review", human_input=root / "review/input.json", out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch06_categorical_handoff_exact_authority_blank_answers_and_notices(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_categorical_batch06 as module
            digest = "a" * 64
            pairs = [{"queue_rank": rank, "packet_sha256": digest, "ai_record_sha256": digest, "exact_pair_record_sha256": digest,
                      "ai_observations": ["</script>"], "human_review_notice": module.human_notice(rank),
                      "required_assets_sha256": {f"assets/{rank:06d}/{name}.png": digest for name in ("temporal_a", "temporal_b", "trigger")}} for rank in module.TARGET_RANKS]
            definition = {"pairs": pairs, "review184_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                          "preflight_sha256": digest, "categorical_rules": module.CATEGORICAL_RULES}
            before = json.dumps(definition, sort_keys=True)
            page = module.render_categorical(definition, digest)
            data, _ = json.JSONDecoder().raw_decode(page.split("const DATA=", 1)[1])
            self.assertEqual(data, {"definition": definition, "sha256": digest})
            self.assertEqual(json.dumps(definition, sort_keys=True), before)
            for fragment in ("evidence_sufficient:null", "same_or_derived_content:null", "personal_inspection_attested:null", "owner_decision_attested:null",
                             "submitted:false", "item.personal_inspection_attested===true", "item.owner_decision_attested===true", "names.length===3", "names.every",
                             "state[current].same_or_derived_content=null", "state[current].submitted=false", "details.hidden=true", "state[current].submitted!==true",
                             "if(!exportReady())return", "ai_record_sha256:pair.ai_record_sha256", "exact_pair_record_sha256:pair.exact_pair_record_sha256",
                             "review184_sha256:DATA.definition.review184_sha256", "batch06_categorical_review", "oulu-batch06-categorical-review.json", "rows.some", "\\u003c/script>"):
                self.assertIn(fragment, page)
            for fragment in ("createElement('textarea')", "rationale:", "imported_human_record", "governance_sha256", "review168", "rank47", "batch05_targeted"):
                self.assertNotIn(fragment, page)
            for changes in ({"review184_sha256": digest}, {"accepted_AI_report_sha256": digest}, {"preflight_sha256": ""}, {"categorical_rules": []},
                            {"categorical_rules": [{**module.CATEGORICAL_RULES[0], "evidence_sufficient": 0}, *module.CATEGORICAL_RULES[1:]]},
                            {"pairs": pairs[:-1]}, {"pairs": list(reversed(pairs))}, {"pairs": [{**pairs[0], "queue_rank": 50.0}, *pairs[1:]]},
                            {"pairs": [{**pairs[0], "human_review_notice": "Reject"}, *pairs[1:]]}, {"pairs": [{**pairs[0], "ai_record_sha256": ""}, *pairs[1:]]},
                            {"pairs": [{**pairs[0], "required_assets_sha256": {}}, *pairs[1:]]}):
                with self.assertRaises(ValueError):
                    module.render_categorical({**definition, **changes}, digest)
            check = {"head_sha": "38e0263c0e20d0d3a27df431142a6550335d8db6", "run_id": 38683111522, "job_id": 116251844389,
                     "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success"}
            authority = {"checkpoint": 185, "review184_sha256": module.REVIEW_SHA256, "accepted_AI_report_sha256": module.AI_REPORT_SHA256,
                         "queue_ranks": list(module.TARGET_RANKS), "source183_CI": check,
                         **{field: False for field in ("human_input_collection_authorized", "import_authorized", "effective_activation_authorized", "model_execution_authorized", "scientific_readiness")}}
            module.verify_authority(authority)
            for changes in ({"checkpoint": 183}, {"queue_ranks": list(range(60, 70))}, {"queue_ranks": [50.0, *range(51, 60)]},
                            {"human_input_collection_authorized": True}, {"import_authorized": True}, {"effective_activation_authorized": True},
                            {"model_execution_authorized": True}, {"scientific_readiness": True}, {"review184_sha256": digest},
                            *({"source183_CI": {**check, field: "drift"}} for field in check)):
                with self.assertRaises(ValueError):
                    module.verify_authority({**authority, **changes})
            self.assertIn("Haze", module.human_notice(54))
            for rank in (56, 58, 59):
                self.assertIn("lower garment", module.human_notice(rank))
            for rank in range(56, 60):
                self.assertIn("correlated", module.human_notice(rank))
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-batch06-categorical", root / "source/overlap"):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(preflight=root / "preflight.json", packet_root=root / "source", ai_root=root / "ai", out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch05_categorical_import_strict_mapping_bindings_and_preservation(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_categorical_batch05 as module
            pairs = [{"queue_rank": rank, "packet_sha256": str(rank), "imported_human_record_sha256": "prior",
                      "required_assets_sha256": {"image": str(rank)}, "ai_disposition": "rejected_false_positive",
                      "prior_human_disposition": "rejected_false_positive", "bound_images_identical_to_rank47": rank == 48} for rank in module.TARGET_RANKS]
            definition = {"sha256": "definition", "governance_sha256": "governance", "review168_sha256": "review", "categorical_rules": module.CATEGORICAL_RULES, "pairs": pairs}
            human = {"version": 1, "record_type": "batch05_targeted_categorical_review", "review_definition_sha256": "definition", "governance_sha256": "governance", "review168_sha256": "review",
                     "reviewer": {"kind": "owner_human", "id": "synthetic", "personally_inspected_bound_evidence": True}, "reviewed_at_utc": "2026-10-15T00:52:21.261Z", "stop_for_prospective_scientific_decision": False,
                     "pairs": [{"queue_rank": pair["queue_rank"], "packet_sha256": pair["packet_sha256"], "imported_human_record_sha256": "prior", "reviewed_assets_sha256": pair["required_assets_sha256"],
                                "evidence_sufficient": True, "same_or_derived_content": False, "personal_inspection_attested": True, "owner_decision_attested": True,
                                "disposition": "rejected_false_positive", "stop_for_prospective_scientific_decision": False, "capture_provenance_certified": False,
                                "bound_images_identical_to_rank47": pair["queue_rank"] == 48, "identical_evidence_reference_rank": 47 if pair["queue_rank"] == 48 else None, "owner_extra": "preserve"} for pair in pairs]}
            before = json.dumps([human, definition], sort_keys=True)
            rows = module.validate_categorical(human, definition)
            self.assertEqual(json.dumps([human, definition], sort_keys=True), before)
            for original, row in zip(human["pairs"], rows, strict=True):
                self.assertTrue(all(row[field] == value for field, value in original.items()))
                self.assertNotIn("rationale", row)
                self.assertFalse(row["effective_disposition_activated"] or row["reconciliation_required"])
            for field, value in (("queue_rank", 40.0), ("queue_rank", 41), ("evidence_sufficient", 1), ("same_or_derived_content", 0), ("same_or_derived_content", None),
                                 ("personal_inspection_attested", 1), ("owner_decision_attested", False), ("packet_sha256", "drift"), ("imported_human_record_sha256", "drift"),
                                 ("reviewed_assets_sha256", {}), ("capture_provenance_certified", True), ("bound_images_identical_to_rank47", 0), ("identical_evidence_reference_rank", 47),
                                 ("disposition", "uncertain_insufficient_evidence"), ("stop_for_prospective_scientific_decision", 0), ("effective_disposition_activated", True)):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, "pairs": [{**human["pairs"][0], field: value}, *human["pairs"][1:]]}, definition)
            for changes in ({"version": True}, {"version": 1.0}, {"record_type": "batch05_targeted_semantic_clarification"}, {"review_definition_sha256": "drift"},
                            {"governance_sha256": "drift"}, {"review168_sha256": "drift"}, {"reviewed_at_utc": "2026-10-15T00:52:21"}, {"stop_for_prospective_scientific_decision": True},
                            {"reviewer": {**human["reviewer"], "personally_inspected_bound_evidence": False}}, {"pairs": human["pairs"][:-1]}):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, **changes}, definition)
            for rule in module.CATEGORICAL_RULES:
                row = {**human["pairs"][0], **rule, "stop_for_prospective_scientific_decision": rule["same_or_derived_content"] is True}
                candidate = {**human, "pairs": [row, *human["pairs"][1:]], "stop_for_prospective_scientific_decision": row["stop_for_prospective_scientific_decision"]}
                outcome = module.validate_categorical(candidate, definition)[0]
                self.assertEqual(outcome["validated_disposition"], rule["disposition"])
                self.assertEqual(outcome["stop_for_prospective_scientific_decision"], rule["same_or_derived_content"] is True)
                self.assertEqual(outcome["reconciliation_required"], rule["disposition"] != "rejected_false_positive")
            for same in (True, False, 0, "false"):
                with self.assertRaises(ValueError):
                    module.validate_categorical({**human, "pairs": [{**human["pairs"][0], "evidence_sufficient": False, "same_or_derived_content": same}, *human["pairs"][1:]]}, definition)
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)
                for output in (folder, ROOT / "results/refused-categorical-import"):
                    with self.assertRaises(ValueError):
                        module.import_review(Namespace(review_root=folder, human_input=folder / "input.json", out_root=output))
        finally:
            sys.path.pop(0)

    def test_clarification_import_preserves_foreground_and_dual_bindings(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_clarification_batch04 as module
            pairs = [{"queue_rank": rank, "imported_human_record_sha256": str(rank), "imported_scrutiny_record_sha256": "scrutiny",
                      "packet_sha256": str(rank), "required_assets_sha256": {"image": str(rank)}, "ai_disposition": "rejected_false_positive"} for rank in (38, 39)]
            definition = {"sha256": "bound", "pairs": pairs}
            human = {"version": 1, "record_type": "human_pair_specific_clarification", "stop_for_prospective_scientific_decision": False,
                     "reviewer": {"kind": "owner_human", "id": "owner", "personally_inspected_bound_evidence": True},
                     "review_definition_sha256": "bound", "reviewed_at_utc": "2026-10-13T03:54:29.393Z",
                     "pairs": [{"queue_rank": pair["queue_rank"], "imported_human_record_sha256": pair["imported_human_record_sha256"],
                                "imported_scrutiny_record_sha256": "scrutiny", "packet_sha256": pair["packet_sha256"],
                                "reviewed_assets_sha256": pair["required_assets_sha256"], "left_visible_foreground_structure": "Owner left",
                                "right_visible_foreground_structure": "Owner right", "haze_veil_limitation": "Owner limitation",
                                "remaining_evidence_sufficient": True, "personally_reviewed": True, "disposition": "rejected_false_positive",
                                "rationale": "Owner comparison", "capture_provenance_certified": False} for pair in pairs]}
            before = json.dumps([human, definition], sort_keys=True)
            outcomes = module.validate_clarification(human, definition)
            self.assertEqual(json.dumps([human, definition], sort_keys=True), before)
            for original, row in zip(human["pairs"], outcomes, strict=True):
                self.assertTrue(all(row[field] == value for field, value in original.items()))
                self.assertNotIn("visible_rendered_structure", row)
                self.assertFalse(row["effective_disposition_activated"])
                self.assertFalse(row["pair_specific_reasoning_semantically_verified"])
            for field, value in (("queue_rank", 38.0), ("queue_rank", 39), ("imported_human_record_sha256", "drift"),
                                 ("imported_scrutiny_record_sha256", "drift"), ("packet_sha256", "drift"), ("reviewed_assets_sha256", {}),
                                 ("left_visible_foreground_structure", ""), ("right_visible_foreground_structure", " "),
                                 ("haze_veil_limitation", None), ("remaining_evidence_sufficient", 1), ("personally_reviewed", False)):
                with self.assertRaises(ValueError):
                    module.validate_clarification({**human, "pairs": [{**human["pairs"][0], field: value}, human["pairs"][1]]}, definition)
            with self.assertRaises(ValueError):
                module.validate_clarification({**human, "record_type": "targeted_human_scrutiny_resolution"}, definition)
            human["pairs"][0].update(disposition="uncertain_insufficient_evidence", remaining_evidence_sufficient=False)
            human["pairs"][1]["disposition"] = "confirmed_same_content_or_derived_lineage"
            with self.assertRaises(ValueError):
                module.validate_clarification(human, definition)
            human["stop_for_prospective_scientific_decision"] = True
            outcomes = module.validate_clarification(human, definition)
            self.assertTrue(outcomes[1]["stop_for_prospective_scientific_decision"])
            self.assertTrue(all(row["comparison_disposition"] == "uncertain_insufficient_evidence" for row in outcomes))
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-clarification-import"):
                    with self.assertRaises(ValueError):
                        module.import_review(Namespace(review_root=root, human_input=root / "input.json", out_root=output))
        finally:
            sys.path.pop(0)

    def test_pair_specific_clarification_blank_foreground_fields_and_bindings(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_clarification_batch04 as module
            pairs = [{"queue_rank": rank, "imported_human_record_sha256": str(rank), "imported_scrutiny_record_sha256": "bound",
                      "ai_observations": ["</script>visible_rendered_structure:'',targeted_human_scrutiny_resolution"]} for rank in (38, 39)]
            definition = {"pairs": pairs, "scrutiny_notice": module.NOTICE}
            before = json.dumps(definition, sort_keys=True)
            page = module.render_clarification(definition, "definition")
            data, _ = json.JSONDecoder().raw_decode(page.split("const DATA=", 1)[1])
            self.assertEqual(data, {"definition": definition, "sha256": "definition"})
            self.assertEqual(json.dumps(definition, sort_keys=True), before)
            for fragment in ("left_visible_foreground_structure:''", "right_visible_foreground_structure:''", "haze_veil_limitation:''",
                             "item.left_visible_foreground_structure.trim()", "item.right_visible_foreground_structure.trim()", "item.haze_veil_limitation.trim()",
                             "disposition:''", "rationale:''", "remaining_evidence_sufficient:null", "personally_reviewed:false",
                             "count!==pairs.length", "queue_rank:pair.queue_rank", "imported_scrutiny_record_sha256:pair.imported_scrutiny_record_sha256",
                             "item.remaining_evidence_sufficient===false", "item.remaining_evidence_sufficient===true", "item.rationale.trim()",
                             "Object.keys(pair.required_assets_sha256)", "human_pair_specific_clarification", "stop_for_prospective_scientific_decision",
                             "oulu-batch04-pair-specific-clarification.json", "temporal panels and trigger", "document.createElement('details')", "\\u003c/script>"):
                self.assertIn(fragment, page)
            self.assertNotIn("details.open", page)
            for altered in (pairs[:1], list(reversed(pairs)), [{**pairs[0], "queue_rank": 38.0}, pairs[1]],
                            [{**pairs[0], "imported_human_record_sha256": ""}, pairs[1]], [{**pairs[0], "imported_scrutiny_record_sha256": ""}, pairs[1]]):
                with self.assertRaises(ValueError):
                    module.render_clarification({"pairs": altered}, "bound")
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-clarification"):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(scrutiny_root=root, review_root=root, out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch05_targeted_clarification_requires_blank_fields_and_provenance(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_clarification_batch05 as module
            pairs = [{"queue_rank": rank, "imported_human_record_sha256": str(rank), "ai_observations": ["</script>disposition:''"],
                      "human_review_notice": module.IDENTICAL_EVIDENCE_NOTICE if rank == 48 else module.VISIBILITY_LIMITS[rank] + module.SCRUTINY_NOTICE,
                      "bound_images_identical_to_rank47": rank == 48} for rank in module.TARGET_RANKS]
            definition = {"pairs": pairs, "governance_sha256": "governance"}
            original = json.dumps(definition, sort_keys=True)
            page = module.render_clarification(definition, "bound")
            embedded, _ = json.JSONDecoder().raw_decode(page.split("const DATA=", 1)[1])
            self.assertEqual(embedded, {"definition": definition, "sha256": "bound"})
            self.assertEqual(json.dumps(definition, sort_keys=True), original)
            self.assertEqual(module.TARGET_RANKS, (40, 41, 42, 43, 48, 49))
            for fragment in ("left_visible_foreground_structure:''", "right_visible_foreground_structure:''", "visibility_limitation:''",
                             "remaining_evidence_sufficient:null", "owner_disposition_is_own_decision:false", "wording_assistance_disclosure:''", "disposition:''", "rationale:''", "personally_reviewed:false",
                             "item.left_visible_foreground_structure.trim()", "item.right_visible_foreground_structure.trim()", "item.visibility_limitation.trim()",
                             "item.owner_disposition_is_own_decision&&item.wording_assistance_disclosure", "item.remaining_evidence_sufficient===false", "item.remaining_evidence_sufficient===true",
                             "count!==pairs.length", "queue_rank:pair.queue_rank", "imported_human_record_sha256:pair.imported_human_record_sha256", "wording_assistance_disclosure:state[rank].wording_assistance_disclosure",
                             "bound_images_identical_to_rank47:pair.bound_images_identical_to_rank47", "identical_evidence_reference_rank:pair.bound_images_identical_to_rank47?47:null",
                             "governance_sha256:DATA.definition.governance_sha256", "batch05_targeted_semantic_clarification", "stop_for_prospective_scientific_decision",
                             "oulu-batch05-targeted-clarification.json", "['','Select disposition']", "['AI_assisted'", "['cannot_exclude'", "document.createElement('details')", "\\u003c/script>"):
                self.assertIn(fragment, page)
            self.assertNotIn("details.open", page)
            self.assertNotIn("count!==10", page)
            self.assertLess(page.index("notice.textContent"), page.index("document.createElement('details')"))
            for altered in (pairs[:-1], list(reversed(pairs)), [{**pairs[0], "queue_rank": 40.0}, *pairs[1:]],
                            [{**pairs[0], "imported_human_record_sha256": ""}, *pairs[1:]], [{**pairs[0], "human_review_notice": "Reject"}, *pairs[1:]],
                            [*pairs[:4], {**pairs[4], "bound_images_identical_to_rank47": False}, pairs[5]], [{**pairs[0], "bound_images_identical_to_rank47": 0}, *pairs[1:]]):
                with self.assertRaises(ValueError):
                    module.render_clarification({**definition, "pairs": altered}, "bound")
            with self.assertRaises(ValueError):
                module.render_clarification({**definition, "governance_sha256": ""}, "bound")
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-batch05-clarification"):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(import_root=root, review_root=root, out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch05_categorical_handoff_removes_prose_and_preserves_scope(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_categorical_batch05 as module
            pairs = [{"queue_rank": rank, "imported_human_record_sha256": str(rank), "ai_observations": ["</script>"],
                      "required_assets_sha256": {f"assets/{rank:06d}/{name}.png": name for name in ("temporal_a", "temporal_b", "trigger")},
                      "human_review_notice": module.IDENTICAL_EVIDENCE_NOTICE if rank == 48 else module.VISIBILITY_LIMITS[rank] + module.NOTICE,
                      "bound_images_identical_to_rank47": rank == 48} for rank in module.TARGET_RANKS]
            definition = {"pairs": pairs, "governance_sha256": "governance", "review168_sha256": "review", "categorical_rules": module.CATEGORICAL_RULES}
            before = json.dumps(definition, sort_keys=True)
            page = module.render_categorical(definition, "bound")
            embedded, _ = json.JSONDecoder().raw_decode(page.split("const DATA=", 1)[1])
            self.assertEqual(embedded, {"definition": definition, "sha256": "bound"})
            self.assertEqual(json.dumps(definition, sort_keys=True), before)
            for fragment in ("evidence_sufficient:null", "same_or_derived_content:null", "personal_inspection_attested:null", "owner_decision_attested:null",
                             "submitted:false", "rule.evidence_sufficient===item.evidence_sufficient", "rule.same_or_derived_content===item.same_or_derived_content",
                             "item.personal_inspection_attested===true", "item.owner_decision_attested===true", "names.length===3", "names.every",
                             "if(item.evidence_sufficient===true)", "state[current].same_or_derived_content=null", "state[current].submitted=false",
                             "details.hidden=true", "state[current].submitted!==true", "if(!exportReady())return", "queue_rank:pair.queue_rank",
                             "capture_provenance_certified:false", "stop_for_prospective_scientific_decision", "rows.some", "bound_images_identical_to_rank47",
                             "batch05_targeted_categorical_review", "oulu-batch05-categorical-review.json", "\\u003c/script>"):
                self.assertIn(fragment, page)
            for fragment in ("createElement('textarea')", "rationale:", "wording_assistance_disclosure", "left_visible_foreground_structure", "Select disposition", "count!==10"):
                self.assertNotIn(fragment, page)
            for changes in ({"governance_sha256": ""}, {"review168_sha256": ""}, {"categorical_rules": []},
                            {"categorical_rules": [{**module.CATEGORICAL_RULES[0], "evidence_sufficient": 0}, *module.CATEGORICAL_RULES[1:]]},
                            {"pairs": pairs[:-1]}, {"pairs": list(reversed(pairs))}, {"pairs": [{**pairs[0], "queue_rank": 40.0}, *pairs[1:]]},
                            {"pairs": [{**pairs[0], "human_review_notice": "Reject"}, *pairs[1:]]},
                            {"pairs": [{**pairs[0], "required_assets_sha256": {}}, *pairs[1:]]},
                            {"pairs": [*pairs[:4], {**pairs[4], "bound_images_identical_to_rank47": False}, pairs[5]]}):
                with self.assertRaises(ValueError):
                    module.render_categorical({**definition, **changes}, "bound")
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-categorical"):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(review_root=root, out_root=output))
        finally:
            sys.path.pop(0)

    def test_targeted_scrutiny_import_preserves_two_answers_and_stop_rules(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_scrutiny_batch04 as module
            pairs = [{"queue_rank": rank, "imported_human_record_sha256": str(rank), "packet_sha256": str(rank),
                      "required_assets_sha256": {"image": str(rank)}, "ai_disposition": "rejected_false_positive"} for rank in (38, 39)]
            definition = {"sha256": "bound", "pairs": pairs}
            human = {"version": 1, "record_type": "targeted_human_scrutiny_resolution", "stop_for_prospective_scientific_decision": False,
                     "reviewer": {"kind": "owner_human", "id": "owner", "personally_inspected_bound_evidence": True},
                     "review_definition_sha256": "bound", "reviewed_at_utc": "2026-10-13T03:15:48.951Z",
                     "pairs": [{"queue_rank": pair["queue_rank"], "imported_human_record_sha256": str(pair["queue_rank"]),
                                "packet_sha256": pair["packet_sha256"], "reviewed_assets_sha256": pair["required_assets_sha256"],
                                "visible_rendered_structure": "Owner words", "remaining_evidence_sufficient": True,
                                "personally_reviewed": True, "disposition": "rejected_false_positive", "rationale": "Owner reason",
                                "capture_provenance_certified": False} for pair in pairs]}
            before = json.dumps([human, definition], sort_keys=True)
            rows = module.validate_scrutiny(human, definition)
            self.assertEqual([row["queue_rank"] for row in rows], [38, 39])
            self.assertTrue(all(not row["effective_disposition_activated"] and not row["pair_specific_reasoning_semantically_verified"] for row in rows))
            self.assertEqual(json.dumps([human, definition], sort_keys=True), before)
            for field, value in (("queue_rank", 38.0), ("queue_rank", 39), ("imported_human_record_sha256", "drift"),
                                 ("packet_sha256", "drift"), ("reviewed_assets_sha256", {}), ("personally_reviewed", False),
                                 ("visible_rendered_structure", ""), ("rationale", " "), ("remaining_evidence_sufficient", 1),
                                 ("remaining_evidence_sufficient", False), ("capture_provenance_certified", True)):
                with self.assertRaises(ValueError):
                    module.validate_scrutiny({**human, "pairs": [{**human["pairs"][0], field: value}, human["pairs"][1]]}, definition)
            for altered in ({**human, "pairs": human["pairs"][:1]}, {**human, "version": True}, {**human, "review_definition_sha256": "drift"},
                            {**human, "reviewed_at_utc": "2026-10-13"}, {**human, "record_type": "ten_pair_review"},
                            {**human, "stop_for_prospective_scientific_decision": 0}, {**human, "reviewer": {}}):
                with self.assertRaises(ValueError):
                    module.validate_scrutiny(altered, definition)
            human["pairs"][0].update(disposition="uncertain_insufficient_evidence", remaining_evidence_sufficient=False)
            human["pairs"][1]["disposition"] = "confirmed_same_content_or_derived_lineage"
            with self.assertRaises(ValueError):
                module.validate_scrutiny(human, definition)
            human["stop_for_prospective_scientific_decision"] = True
            rows = module.validate_scrutiny(human, definition)
            self.assertTrue(rows[1]["stop_for_prospective_scientific_decision"])
            self.assertTrue(all(row["comparison_disposition"] == "uncertain_insufficient_evidence" for row in rows))
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (root, ROOT / "results/refused-scrutiny-import"):
                    with self.assertRaises(ValueError):
                        module.import_review(Namespace(review_root=root, human_input=root / "input.json", out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch04_targeted_scrutiny_blank_fields_and_two_original_ranks(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_scrutiny_batch04 as module
            pairs = [{"queue_rank": rank, "imported_human_record_sha256": str(rank), "ai_observations": ["</script>note"]} for rank in (38, 39)]
            definition = {"pairs": pairs, "scrutiny_notice": module.NOTICE}
            before = json.dumps(definition, sort_keys=True)
            page = module.render_scrutiny(definition, "bound")
            self.assertEqual(json.dumps(definition, sort_keys=True), before)
            data, _ = json.JSONDecoder().raw_decode(page.split("const DATA=", 1)[1])
            self.assertEqual(data, {"definition": definition, "sha256": "bound"})
            for fragment in ("visible_rendered_structure:''", "remaining_evidence_sufficient:null", "disposition:''", "rationale:''",
                             "personally_reviewed:false", "count!==pairs.length", "queue_rank:pair.queue_rank", "imported_human_record_sha256:pair.imported_human_record_sha256",
                             "remaining_evidence_sufficient:state[rank].remaining_evidence_sufficient", "item.visible_rendered_structure.trim()",
                             "item.remaining_evidence_sufficient===false", "item.remaining_evidence_sufficient===true", "item.rationale.trim()",
                             "item.personally_reviewed", "Object.keys(pair.required_assets_sha256)", "review_definition_sha256:DATA.sha256",
                             "oulu-batch04-scrutiny-resolution.json", "targeted_human_scrutiny_resolution", "stop_for_prospective_scientific_decision",
                             "document.createElement('details')", "\\u003c/script>"):
                self.assertIn(fragment, page)
            self.assertNotIn("count!==10", page)
            self.assertNotIn("queue_rank:rank,", page)
            self.assertNotIn("details.open", page)
            for altered in (pairs[:1], list(reversed(pairs)), [{**pairs[0], "queue_rank": 38.0}, pairs[1]],
                            [{**pairs[0], "imported_human_record_sha256": ""}, pairs[1]], [{**pair, "queue_rank": pair["queue_rank"] - 30} for pair in pairs]):
                with self.assertRaises(ValueError):
                    module.render_scrutiny({"pairs": altered}, "bound")
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (ROOT / "results/refused-scrutiny", root):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(import_root=root, review_root=root, out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch04_human_rank_adapter_preserves_answers_and_conservative_rules(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_human_batch04 as module
            pairs = [{"queue_rank": rank, "packet_sha256": str(rank), "required_assets_sha256": {"image": str(rank)},
                      "ai_disposition": "rejected_false_positive"} for rank in range(30, 40)]
            definition = {"sha256": "bound", "pairs": pairs}
            human = {"version": 1, "reviewer": {"kind": "owner_human", "id": "owner", "personally_inspected_bound_evidence": True},
                     "review_definition_sha256": "bound", "reviewed_at_utc": "2026-10-13T02:16:39.495Z",
                     "pairs": [{"queue_rank": pair["queue_rank"], "packet_sha256": pair["packet_sha256"],
                                "reviewed_assets_sha256": pair["required_assets_sha256"], "personally_reviewed": True,
                                "disposition": "rejected_false_positive", "rationale": "Original owner rationale", "capture_provenance_certified": False} for pair in pairs]}
            original = json.dumps([human, definition], sort_keys=True)
            rows = module.validate_batch04(human, definition)
            self.assertEqual([row["queue_rank"] for row in rows], list(range(30, 40)))
            self.assertTrue(all(not row["disagreement"] and not row["effective_disposition_activated"] for row in rows))
            self.assertTrue(all(row["rationale"] == "Original owner rationale" for row in rows))
            self.assertEqual(json.dumps([human, definition], sort_keys=True), original)
            human["pairs"][8]["disposition"] = "uncertain_insufficient_evidence"
            human["pairs"][9]["disposition"] = "confirmed_same_content_or_derived_lineage"
            rows = module.validate_batch04(human, definition)
            self.assertTrue(rows[8]["disagreement"])
            self.assertEqual(rows[8]["effective_disposition"], "uncertain_insufficient_evidence")
            self.assertTrue(rows[9]["stop_for_prospective_scientific_decision"])
            self.assertEqual(rows[9]["effective_disposition"], "uncertain_insufficient_evidence")
            self.assertTrue(all(not row["effective_disposition_activated"] for row in rows))
            for key, value in (("queue_rank", 0), ("queue_rank", True), ("queue_rank", 30.0), ("queue_rank", 31),
                               ("rationale", ""), ("packet_sha256", "drift"), ("personally_reviewed", False), ("reviewed_assets_sha256", {})):
                with self.assertRaises(ValueError):
                    module.validate_batch04({**human, "pairs": [{**human["pairs"][0], key: value}, *human["pairs"][1:]]}, definition)
            for altered in ({**human, "pairs": human["pairs"][:-1]}, {**human, "review_definition_sha256": "drift"},
                            {**human, "reviewer": {**human["reviewer"], "personally_inspected_bound_evidence": False}}):
                with self.assertRaises(ValueError):
                    module.validate_batch04(altered, definition)
            with self.assertRaises(ValueError):
                module.validate_batch04(human, {**definition, "pairs": list(reversed(pairs))})
        finally:
            sys.path.pop(0)

    def test_batch05_handoff_requires_blank_pair_specific_structure_and_neutral_visibility(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_owner_batch05 as module
            pairs = [{"queue_rank": rank, "ai_observations": ["</script>queue_rank:rank,packet_sha256"],
                      "human_review_notice": module.VISIBILITY_LIMITS[rank] + module.SCRUTINY_NOTICE if rank in module.HEIGHTENED_SCRUTINY_RANKS else ""} for rank in range(40, 50)]
            definition = {"pairs": pairs}
            original = json.dumps(definition, sort_keys=True)
            page = module.render_batch05(definition, "bound")
            embedded, _ = json.JSONDecoder().raw_decode(page.split("const DATA=", 1)[1])
            self.assertEqual(embedded, {"definition": definition, "sha256": "bound"})
            self.assertEqual(json.dumps(definition, sort_keys=True), original)
            for text in ("Batch 05", "oulu-batch05-human-review.json", "disposition:''", "visible_rendered_structure:''", "rationale:''", "personally_reviewed:false",
                         "item.visible_rendered_structure.trim()&&item.rationale.trim()", "Object.keys(pair.required_assets_sha256)",
                         "visibleText.value=item.visible_rendered_structure", "visible_rendered_structure:state[rank].visible_rendered_structure",
                         "queue_rank:pair.queue_rank", "batch05_human_review_with_pair_specific_structure", "review_definition_sha256:DATA.sha256",
                         "['','Select disposition']", "['confirmed_same_content_or_derived_lineage'", "['rejected_false_positive'", "['uncertain_insufficient_evidence'",
                         "stop_for_prospective_scientific_decision:state.some", "document.createElement('details')", "\\u003c/script>"):
                self.assertIn(text, page)
            self.assertNotIn("details.open", page)
            self.assertIn("notice.textContent=pair.human_review_notice", page)
            self.assertLess(page.index("notice.textContent"), page.index("document.createElement('details')"))
            self.assertEqual(module.HEIGHTENED_SCRUTINY_RANKS, (40, 41, 42, 43, 49))
            for altered in (pairs[:-1], list(reversed(pairs)), [{**pair, "queue_rank": pair["queue_rank"] - 10} for pair in pairs],
                            [{**pairs[0], "queue_rank": 40.0}, *pairs[1:]], [{**pairs[0], "human_review_notice": ""}, *pairs[1:]],
                            [*pairs[:4], {**pairs[4], "human_review_notice": "Reject"}, *pairs[5:]]):
                with self.assertRaises(ValueError):
                    module.render_batch05({"pairs": altered}, "bound")
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (ROOT / "results/refused-owner-batch05", root):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(ai_root=root, packet_root=root, out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch04_handoff_preserves_blank_answers_and_visible_scrutiny(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_owner_batch04 as module
            pairs = [{"queue_rank": rank, "ai_observations": ["</script>observed"],
                      "human_review_notice": module.HEIGHTENED_SCRUTINY_NOTICE if rank in (38, 39) else ""} for rank in range(30, 40)]
            definition = {"pairs": pairs}
            original = json.dumps(definition, sort_keys=True)
            page = module.render_batch04(definition, "bound")
            self.assertEqual(json.dumps(definition, sort_keys=True), original)
            embedded, _ = json.JSONDecoder().raw_decode(page.split("const DATA=", 1)[1])
            self.assertEqual(embedded, {"definition": definition, "sha256": "bound"})
            self.assertIn("Batch 04", page)
            self.assertIn("oulu-batch04-human-review.json", page)
            self.assertIn("queue_rank:pair.queue_rank,packet_sha256", page)
            self.assertNotIn("queue_rank:rank,packet_sha256", page)
            for text in ("disposition:''", "rationale:''", "personally_reviewed:false", "['','Select disposition']",
                         "item.disposition&&item.rationale.trim()&&item.personally_reviewed", "Object.keys(pair.required_assets_sha256)",
                         "document.createElement('details')", "review_definition_sha256:DATA.sha256", "\\u003c/script>"):
                self.assertIn(text, page)
            self.assertNotIn("details.open", page)
            self.assertIn("notice.textContent=pair.human_review_notice", page)
            self.assertLess(page.index("notice.textContent"), page.index("document.createElement('details')"))
            for altered in (pairs[:9], list(reversed(pairs)), [{**pair, "queue_rank": pair["queue_rank"] - 10} for pair in pairs],
                            [{**pairs[0], "queue_rank": 30.0}, *pairs[1:]], [*pairs[:8], {**pairs[8], "human_review_notice": ""}, pairs[9]]):
                with self.assertRaises(ValueError):
                    module.render_batch04({"pairs": altered}, "bound")
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (ROOT / "results/refused-owner-batch04", root):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(ai_root=root, packet_root=root, out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch05_human_rank_adapter_preserves_structure_and_pending_semantics(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_human_batch05 as module
            pairs = [{"queue_rank": rank, "packet_sha256": str(rank), "required_assets_sha256": {"image": str(rank)},
                      "ai_disposition": "rejected_false_positive"} for rank in range(40, 50)]
            definition = {"sha256": "bound", "pairs": pairs}
            human = {"version": 1, "record_type": "batch05_human_review_with_pair_specific_structure", "stop_for_prospective_scientific_decision": False,
                     "reviewer": {"kind": "owner_human", "id": "owner", "personally_inspected_bound_evidence": True},
                     "review_definition_sha256": "bound", "reviewed_at_utc": "2026-10-14T09:47:25Z",
                     "pairs": [{"queue_rank": pair["queue_rank"], "packet_sha256": pair["packet_sha256"],
                                "reviewed_assets_sha256": pair["required_assets_sha256"], "personally_reviewed": True,
                                "disposition": "rejected_false_positive", "visible_rendered_structure": "Observed structure",
                                "rationale": "Observed evidence", "capture_provenance_certified": False} for pair in pairs]}
            original = json.dumps([human, definition], sort_keys=True)
            rows = module.validate_batch05(human, definition)
            self.assertEqual([row["queue_rank"] for row in rows], list(range(40, 50)))
            self.assertEqual(json.dumps([human, definition], sort_keys=True), original)
            self.assertTrue(all(row["visible_rendered_structure"] == "Observed structure" and not row["effective_disposition_activated"] and row["pair_specific_semantic_review_pending"] for row in rows))
            human["pairs"][0]["disposition"] = "uncertain_insufficient_evidence"
            human["pairs"][1]["disposition"] = "confirmed_same_content_or_derived_lineage"
            human["stop_for_prospective_scientific_decision"] = True
            human["pairs"][2]["rationale"] = "Same with previous queue"
            rows = module.validate_batch05(human, definition)
            self.assertTrue(rows[0]["disagreement"])
            self.assertEqual(rows[0]["effective_disposition"], "uncertain_insufficient_evidence")
            self.assertTrue(rows[1]["stop_for_prospective_scientific_decision"])
            self.assertEqual(rows[1]["effective_disposition"], "uncertain_insufficient_evidence")
            self.assertTrue(rows[2]["reference_only_marker_in_human_text"])
            self.assertEqual(rows[2]["rationale"], "Same with previous queue")
            for key, value in (("queue_rank", 0), ("queue_rank", True), ("queue_rank", 40.0), ("queue_rank", 41), ("visible_rendered_structure", " "), ("visible_rendered_structure", None), ("rationale", ""), ("packet_sha256", "drift"), ("personally_reviewed", False), ("reviewed_assets_sha256", {}), ("capture_provenance_certified", True)):
                with self.assertRaises(ValueError):
                    module.validate_batch05({**human, "pairs": [{**human["pairs"][0], key: value}, *human["pairs"][1:]]}, definition)
            for altered in ({**human, "pairs": human["pairs"][:-1]}, {**human, "record_type": "wrong"}, {**human, "stop_for_prospective_scientific_decision": False}, {**human, "stop_for_prospective_scientific_decision": 1}, {**human, "review_definition_sha256": "drift"}, {**human, "reviewer": {**human["reviewer"], "personally_inspected_bound_evidence": False}}):
                with self.assertRaises(ValueError):
                    module.validate_batch05(altered, definition)
            with self.assertRaises(ValueError):
                module.validate_batch05(human, {**definition, "pairs": list(reversed(pairs))})
        finally:
            sys.path.pop(0)

    def test_batch03_human_rank_adapter_preserves_attestations_and_conservative_rules(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_human_batch03 as module
            pairs = [{"queue_rank": rank, "packet_sha256": str(rank), "required_assets_sha256": {"image": str(rank)},
                      "ai_disposition": "rejected_false_positive"} for rank in range(20, 30)]
            definition = {"sha256": "bound", "pairs": pairs}
            human = {"version": 1, "reviewer": {"kind": "owner_human", "id": "owner", "personally_inspected_bound_evidence": True},
                     "review_definition_sha256": "bound", "reviewed_at_utc": "2026-10-12T10:45:39Z",
                     "pairs": [{"queue_rank": pair["queue_rank"], "packet_sha256": pair["packet_sha256"],
                                "reviewed_assets_sha256": pair["required_assets_sha256"], "personally_reviewed": True,
                                "disposition": "rejected_false_positive", "rationale": "Observed evidence", "capture_provenance_certified": False} for pair in pairs]}
            original = json.dumps([human, definition], sort_keys=True)
            rows = module.validate_batch03(human, definition)
            self.assertEqual([row["queue_rank"] for row in rows], list(range(20, 30)))
            self.assertTrue(all(not row["disagreement"] and not row["effective_disposition_activated"] for row in rows))
            self.assertEqual(json.dumps([human, definition], sort_keys=True), original)
            human["pairs"][0]["disposition"] = "uncertain_insufficient_evidence"
            human["pairs"][1]["disposition"] = "confirmed_same_content_or_derived_lineage"
            rows = module.validate_batch03(human, definition)
            self.assertTrue(rows[0]["disagreement"])
            self.assertEqual(rows[0]["effective_disposition"], "uncertain_insufficient_evidence")
            self.assertTrue(rows[1]["stop_for_prospective_scientific_decision"])
            self.assertEqual(rows[1]["effective_disposition"], "uncertain_insufficient_evidence")
            self.assertTrue(all(not row["effective_disposition_activated"] for row in rows))
            with self.assertRaises(ValueError):
                module.validate_batch03({**human, "pairs": human["pairs"][:-1]}, definition)
            for key, value in (("queue_rank", 0), ("queue_rank", True), ("queue_rank", 20.0), ("queue_rank", 21), ("rationale", ""), ("packet_sha256", "drift"), ("personally_reviewed", False), ("reviewed_assets_sha256", {})):
                altered = {**human, "pairs": [{**human["pairs"][0], key: value}, *human["pairs"][1:]]}
                with self.assertRaises(ValueError):
                    module.validate_batch03(altered, definition)
            with self.assertRaises(ValueError):
                module.validate_batch03({**human, "review_definition_sha256": "drift"}, definition)
            with self.assertRaises(ValueError):
                module.validate_batch03(human, {**definition, "pairs": list(reversed(pairs))})
            with self.assertRaises(ValueError):
                module.validate_batch03({**human, "reviewer": {**human["reviewer"], "personally_inspected_bound_evidence": False}}, definition)
        finally:
            sys.path.pop(0)

    def test_batch03_handoff_preserves_original_ranks_and_blank_answers(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_owner_batch03 as module
            definition = {"pairs": [{"queue_rank": rank, "ai_observations": ["</script>observed"]} for rank in range(20, 30)]}
            original = json.dumps(definition, sort_keys=True)
            page = module.render_batch03(definition, "bound")
            self.assertEqual(json.dumps(definition, sort_keys=True), original)
            self.assertIn("Batch 03", page)
            self.assertIn("oulu-batch03-human-review.json", page)
            self.assertIn("queue_rank:pair.queue_rank,packet_sha256", page)
            self.assertNotIn("queue_rank:rank,packet_sha256", page)
            self.assertIn("disposition:''", page)
            self.assertIn("rationale:''", page)
            self.assertIn("personally_reviewed:false", page)
            self.assertIn("document.createElement('details')", page)
            self.assertNotIn("details.open", page)
            self.assertIn("\\u003c/script>", page)
            self.assertIn("review_definition_sha256:DATA.sha256", page)
            for pairs in (definition["pairs"][:9], list(reversed(definition["pairs"])), [{"queue_rank": rank} for rank in range(10, 20)]):
                with self.assertRaises(ValueError):
                    module.render_batch03({"pairs": pairs}, "bound")
        finally:
            sys.path.pop(0)

    def test_batch09_final_five_authority_selection_and_historical_activation(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_visual_batch09 as module
            from argparse import Namespace
            from fas.freeze import write_immutable_record
            records = [{"queue_rank": rank, "priority": "cross_role_conflicting_label"} for rank in range(85)]
            prior = {"activation_checkpoint_review_pending": True, "accepted_batch08_current_effective_dispositions": 0,
                     "materialized_activation_rows": 10, "current_materialized_disposition_counts": {"rejected_false_positive": 10},
                     "accepted_current_total": 70, "prospective_total_after_acceptance": 80, "batch08_closed": False,
                     "stop_for_prospective_scientific_decision": False, "historical_disagreements": 1,
                     "historical_unresolved_reconciliations": 0, "batch08_agreements_with_AI": 10,
                     "batch08_disagreements_with_AI": 0, "batch08_unresolved_reconciliation_requirements": 0,
                     "original_import_pending_nonactivation_and_counting_flags_unchanged": True,
                     "new_rows_count_as_accepted_current_effective_dispositions": False, "activation_sha256": "a" * 64}
            acceptance = {"batch08_activation_checkpoint_accepted": True, "batch08_screen_level_review_closed": True,
                          "accepted_current_total": 80, "accepted_batch08_disposition_counts": {"rejected_false_positive": 10},
                          "accepted_AI_screen_coverage": 80, "accepted_semantic_owner_outcomes_total": 80,
                          "historical_disagreements": 1, "historical_unresolved_reconciliations": 0}
            before = json.dumps([records, prior, acceptance], sort_keys=True)
            self.assertEqual([row["queue_rank"] for row in module.fixed_next_records(records, prior, acceptance)], list(range(80, 85)))
            for source in (prior, acceptance):
                for key, value in source.items():
                    if key == "activation_sha256":
                        continue
                    bad = {**source, key: not value if type(value) is bool else {} if isinstance(value, dict) else float(value)}
                    with self.assertRaises(ValueError):
                        module.fixed_next_records(records, bad if source is prior else prior, bad if source is acceptance else acceptance)
            for altered in (records[:-1], records + [{"queue_rank": 85, "priority": "cross_role_conflicting_label"}],
                            list(reversed(records)), [*records[:80], {**records[80], "queue_rank": 80.0}, *records[81:]],
                            [*records[:80], {**records[80], "queue_rank": True}, *records[81:]],
                            [*records[:84], {**records[84], "priority": "other"}]):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(altered, prior, acceptance)
            self.assertEqual(json.dumps([records, prior, acceptance], sort_keys=True), before)
            rows = [{"queue_rank": rank, "effective_disposition": "rejected_false_positive", "owner_disposition": "rejected_false_positive",
                     "effective_disposition_activated": True, "activation_checkpoint_review_pending": True,
                     "counts_as_accepted_current_effective_disposition": False, "activation_sha256": prior["activation_sha256"],
                     "screen_semantic_acceptance_source": "Review214", "semantic_outcome_accepted_by_Review214": True,
                     "stop_for_prospective_scientific_decision": False, "reconciliation_required": False,
                     "AI_disposition_rewritten": False, "ai_disposition": "rejected_false_positive", "disagreement_with_AI": False,
                     "historical_import_reconciliation_required": False, "historical_import_comparison_disposition": "rejected_false_positive",
                     "historical_import_effective_disposition_activated": False,
                     "historical_import_counts_as_accepted_current_effective_disposition": False,
                     "historical_import_checkpoint_review_pending": True, "historical_import_semantic_acceptance_pending": True}
                    for rank in range(70, 80)]
            snapshot = json.dumps(rows, sort_keys=True)
            self.assertIsNone(module.verified_prior_rows(rows, prior))
            for key, value in rows[0].items():
                bad = {**rows[0], key: not value if type(value) is bool else float(value) if type(value) is int else "drift"}
                with self.assertRaises(ValueError):
                    module.verified_prior_rows([bad, *rows[1:]], prior)
            for altered in (rows[:-1], list(reversed(rows))):
                with self.assertRaises(ValueError):
                    module.verified_prior_rows(altered, prior)
            self.assertEqual(json.dumps(rows, sort_keys=True), snapshot)
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repo = root / "repo"
                review = repo / "docs/216-review-doc215-oulu-batch08-activation.md"
                review.parent.mkdir(parents=True)
                review.write_text("synthetic Review216 acceptance", encoding="ascii")
                document = repo / "docs/215-review-response-doc214-oulu-batch08-activation.md"
                document.write_text("synthetic historical215", encoding="ascii")
                report = repo / "results/phase1/oulu-batch08-activation-v1.json"
                write_immutable_record(report, prior)
                check = {"head_sha": "c240a8c90870c548f8bafdd35e59992d17e94784", "run_id": 39353105356,
                         "job_id": 118401642331, "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success"}
                authority = {**acceptance, "review216_sha256": module._sha256(review)}
                preflight = {"checkpoint": 217, "acceptance": authority, "activation_CI": check, "packet_preparation_authorized": True,
                             "queue_ranks": list(range(80, 85)), "accepted_prior_report_sha256": module._sha256(report),
                             "accepted_prior_document_sha256": module._sha256(document),
                             "accepted_recovery": {"accepted_by_Review178": True}, "protected_snapshots": {}}
                original = json.dumps(preflight, sort_keys=True)
                with patch.object(module, "ROOT", repo), patch.object(module, "REVIEW216_SHA256", module._sha256(review)), patch.object(module, "ACCEPTED215_REPORT_SHA256", module._sha256(report)), patch.object(module, "ACCEPTED215_DOCUMENT_SHA256", module._sha256(document)):
                    self.assertEqual(module.verified_packet_authority(preflight), authority)
                    invalid = [{**preflight, "acceptance": None}, {**preflight, "acceptance": {**authority, "review216_sha256": "0" * 64}},
                               {**preflight, "checkpoint": 217.0}, {**preflight, "packet_preparation_authorized": False},
                               {**preflight, "queue_ranks": list(range(80, 90))}, {**preflight, "queue_ranks": [80.0, *range(81, 85)]},
                               {**preflight, "queue_ranks": [*range(80, 84), True]}, {**preflight, "accepted_prior_report_sha256": "0" * 64},
                               {**preflight, "accepted_prior_document_sha256": "0" * 64}, {**preflight, "activation_CI": None},
                               {**preflight, "accepted_recovery": None}, {**preflight, "accepted_recovery": {"accepted_by_Review178": False}}]
                    for key, value in (("head_sha", "0" * 40), ("run_id", 39351736047), ("run_id", float(check["run_id"])),
                                       ("job_id", 118397259824), ("status", "in_progress"), ("conclusion", "failure"),
                                       ("job_status", "queued"), ("job_conclusion", "failure")):
                        invalid.append({**preflight, "activation_CI": {**check, key: value}})
                    for index, bad in enumerate(invalid):
                        with self.assertRaises(ValueError):
                            module.verified_packet_authority(bad)
                        path = root / f"bad-{index}.json"
                        write_immutable_record(path, bad)
                        args = Namespace(input_root=root / "source", audit_root=root / "audit", exact_root=root / "exact",
                            screen_root=root / "screen", frozen_root=root / "frozen", archive_records=root / "pins",
                            activation_root=root / "activation", preflight=path, out_root=root / "never-created")
                        with patch.object(module, "verified_archive_identities", side_effect=AssertionError("must not reach archives")):
                            with self.assertRaises(ValueError):
                                module.prepare(args)
                        self.assertFalse(args.out_root.exists())
                    for output in (ROOT / "results/refused-visual-batch09", root, root / "source/refused"):
                        with self.assertRaises(ValueError):
                            module.prepare(Namespace(input_root=root, audit_root=root, exact_root=root, screen_root=root,
                                frozen_root=root, archive_records=root, activation_root=root, preflight=root / "missing", out_root=output))
                self.assertEqual(json.dumps(preflight, sort_keys=True), original)
        finally:
            sys.path.pop(0)

    def test_batch08_packet_authority_selection_and_preserved_disagreement(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_visual_batch08 as module
            from argparse import Namespace
            from fas.freeze import write_immutable_record
            records = [{"queue_rank": rank, "priority": "cross_role_conflicting_label"} for rank in range(80)]
            prior = {"activation_checkpoint_review_pending": True, "accepted_batch07_current_effective_dispositions": 0,
                     "effective_dispositions_activated": 10, "current_materialized_disposition_counts": {"rejected_false_positive": 10},
                     "accepted_current_total": 60, "prospective_total_after_acceptance": 70, "batch07_closed": False,
                     "stop_for_prospective_scientific_decision": False, "historical_disagreements_with_AI": 1,
                     "unresolved_reconciliation_blockers_after_Review198": 0, "AI_uncertainty_and_disagreement_history_preserved": True,
                     "private_activation_sha256": "a" * 64}
            acceptance = {"batch07_activation_checkpoint_accepted": True, "batch07_screen_level_review_closed": True,
                          "accepted_current_total": 70, "accepted_batch07_disposition_counts": {"rejected_false_positive": 10},
                          "historical_disagreements_with_AI": 1, "unresolved_reconciliation_blockers": 0}
            before = json.dumps([records, prior, acceptance], sort_keys=True)
            self.assertEqual([row["queue_rank"] for row in module.fixed_next_records(records, prior, acceptance)], list(range(70, 80)))
            for key, value in (("batch07_activation_checkpoint_accepted", False), ("batch07_screen_level_review_closed", False),
                               ("accepted_current_total", 70.0), ("historical_disagreements_with_AI", 0),
                               ("unresolved_reconciliation_blockers", True), ("accepted_batch07_disposition_counts", {})):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(records, prior, {**acceptance, key: value})
            for key, value in (("activation_checkpoint_review_pending", False), ("accepted_batch07_current_effective_dispositions", 10),
                               ("effective_dispositions_activated", 0), ("current_materialized_disposition_counts", {}),
                               ("accepted_current_total", 70), ("prospective_total_after_acceptance", 60), ("batch07_closed", True),
                               ("stop_for_prospective_scientific_decision", True), ("historical_disagreements_with_AI", 0),
                               ("unresolved_reconciliation_blockers_after_Review198", 1), ("AI_uncertainty_and_disagreement_history_preserved", False)):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(records, {**prior, key: value}, acceptance)
            for altered in (records[:-1], list(reversed(records)), [*records[:70], {**records[70], "queue_rank": 70.0}, *records[71:]],
                            [*records[:70], {**records[70], "queue_rank": True}, *records[71:]], [*records[:70], {**records[70], "priority": "other"}, *records[71:]]):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(altered, prior, acceptance)
            self.assertEqual(json.dumps([records, prior, acceptance], sort_keys=True), before)
            rows = [{"queue_rank": rank, "effective_disposition": "rejected_false_positive", "owner_disposition": "rejected_false_positive",
                     "effective_disposition_activated": True, "activation_checkpoint_review_pending": True,
                     "counts_as_accepted_current_effective_disposition": False, "activation_sha256": prior["private_activation_sha256"],
                     "screen_semantic_acceptance_source": "Review198", "stop_for_prospective_scientific_decision": False,
                     "reconciliation_required": False, "AI_disposition_rewritten": False, "ai_disposition": "rejected_false_positive",
                     "disagreement_with_AI": False, "historical_import_reconciliation_required": False,
                     "historical_import_comparison_disposition": "rejected_false_positive", "governance_reconciliation_source": "not_required_AI_owner_agreement"}
                    for rank in range(60, 70)]
            rows[6].update(ai_disposition="uncertain_insufficient_evidence", disagreement_with_AI=True,
                           historical_import_reconciliation_required=True, historical_import_comparison_disposition="uncertain_insufficient_evidence",
                           governance_reconciliation_source="Review198")
            snapshot = json.dumps(rows, sort_keys=True)
            self.assertIsNone(module.verified_prior_rows(rows, prior))
            for key, value in (("queue_rank", 66.0), ("disagreement_with_AI", False), ("ai_disposition", "rejected_false_positive"),
                               ("historical_import_reconciliation_required", False), ("historical_import_comparison_disposition", "rejected_false_positive"),
                               ("reconciliation_required", True), ("governance_reconciliation_source", "owner_override"),
                               ("AI_disposition_rewritten", True), ("counts_as_accepted_current_effective_disposition", True),
                               ("activation_checkpoint_review_pending", False), ("screen_semantic_acceptance_source", "Review200")):
                with self.assertRaises(ValueError):
                    module.verified_prior_rows([*rows[:6], {**rows[6], key: value}, *rows[7:]], prior)
            for altered in (rows[:-1], list(reversed(rows)), [{**row, "ai_disposition": "rejected_false_positive", "disagreement_with_AI": False,
                              "historical_import_reconciliation_required": False, "historical_import_comparison_disposition": "rejected_false_positive",
                              "governance_reconciliation_source": "not_required_AI_owner_agreement"} for row in rows]):
                with self.assertRaises(ValueError):
                    module.verified_prior_rows(altered, prior)
            self.assertEqual(json.dumps(rows, sort_keys=True), snapshot)
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repo = root / "repo"
                review = repo / "docs/200-review-doc199-oulu-batch07-activation.md"
                review.parent.mkdir(parents=True)
                review.write_text("synthetic Review200 acceptance", encoding="ascii")
                report = repo / "results/phase1/oulu-batch07-activation-v1.json"
                write_immutable_record(report, prior)
                check = {"head_sha": "4ab5d05b6b85faa4f849361224653d41dacc19e6", "run_id": 38844328951,
                         "job_id": 116791294915, "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success"}
                authority = {**acceptance, "review200_sha256": module._sha256(review)}
                preflight = {"checkpoint": 201, "acceptance": authority, "activation_CI": check, "packet_preparation_authorized": True,
                             "queue_ranks": list(range(70, 80)), "accepted_prior_report_sha256": module._sha256(report),
                             "accepted_recovery": {"accepted_by_Review178": True}, "protected_snapshots": {}}
                original = json.dumps(preflight, sort_keys=True)
                with patch.object(module, "ROOT", repo), patch.object(module, "REVIEW200_SHA256", module._sha256(review)), patch.object(module, "ACCEPTED199_REPORT_SHA256", module._sha256(report)):
                    self.assertEqual(module.verified_packet_authority(preflight), authority)
                    invalid = [{**preflight, "acceptance": None}, {**preflight, "acceptance": {**authority, "review200_sha256": "0" * 64}},
                               {**preflight, "checkpoint": 201.0}, {**preflight, "packet_preparation_authorized": False},
                               {**preflight, "queue_ranks": list(range(80, 90))}, {**preflight, "queue_ranks": [70.0, *range(71, 80)]},
                               {**preflight, "accepted_prior_report_sha256": "0" * 64}, {**preflight, "activation_CI": None},
                               {**preflight, "accepted_recovery": None}, {**preflight, "accepted_recovery": {"accepted_by_Review178": False}}]
                    for key, value in (("head_sha", "0" * 40), ("run_id", 38719866755), ("run_id", float(check["run_id"])),
                                       ("job_id", 116371485847), ("status", "in_progress"), ("conclusion", "failure"),
                                       ("job_status", "queued"), ("job_conclusion", "failure")):
                        invalid.append({**preflight, "activation_CI": {**check, key: value}})
                    for index, bad in enumerate(invalid):
                        with self.assertRaises(ValueError):
                            module.verified_packet_authority(bad)
                        path = root / f"bad-{index}.json"
                        write_immutable_record(path, bad)
                        args = Namespace(input_root=root / "source", audit_root=root / "audit", exact_root=root / "exact",
                            screen_root=root / "screen", frozen_root=root / "frozen", archive_records=root / "pins",
                            activation_root=root / "activation", preflight=path, out_root=root / "never-created")
                        with patch.object(module, "verified_archive_identities", side_effect=AssertionError("must not reach archives")):
                            with self.assertRaises(ValueError):
                                module.prepare(args)
                        self.assertFalse(args.out_root.exists())
                    for output in (ROOT / "results/refused-visual-batch08", root, root / "source/refused"):
                        with self.assertRaises(ValueError):
                            module.prepare(Namespace(input_root=root, audit_root=root, exact_root=root, screen_root=root,
                                frozen_root=root, archive_records=root, activation_root=root, preflight=root / "missing", out_root=output))
                self.assertEqual(json.dumps(preflight, sort_keys=True), original)
        finally:
            sys.path.pop(0)

    def test_batch07_packet_authority_selection_and_unchanged_history(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_visual_batch07 as module
            from argparse import Namespace
            from fas.freeze import write_immutable_record
            records = [{"queue_rank": rank, "priority": "cross_role_conflicting_label"} for rank in range(70)]
            prior = {"activation_checkpoint_review_pending": True, "batch06_accepted_reconciled_disposition_state": False,
                     "accepted_batch06_current_effective_dispositions": 0, "effective_dispositions_activated": 10,
                     "current_materialized_disposition_counts": {"rejected_false_positive": 10},
                     "accepted_current_total": 50, "prospective_total_after_acceptance": 60, "batch06_closed": False,
                     "stop_for_prospective_scientific_decision": False}
            acceptance = {"batch06_activation_checkpoint_accepted": True, "batch06_screen_level_review_closed": True,
                          "accepted_current_total": 60, "accepted_batch06_disposition_counts": {"rejected_false_positive": 10}}
            before = json.dumps([records, prior, acceptance], sort_keys=True)
            self.assertEqual([row["queue_rank"] for row in module.fixed_next_records(records, prior, acceptance)], list(range(60, 70)))
            for key, value in (("batch06_activation_checkpoint_accepted", False), ("batch06_screen_level_review_closed", False),
                               ("accepted_current_total", 60.0), ("accepted_batch06_disposition_counts", {"rejected_false_positive": 9})):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(records, prior, {**acceptance, key: value})
            for key, value in (("activation_checkpoint_review_pending", False), ("batch06_accepted_reconciled_disposition_state", True),
                               ("accepted_batch06_current_effective_dispositions", 10), ("effective_dispositions_activated", 0),
                               ("current_materialized_disposition_counts", {}), ("accepted_current_total", 60),
                               ("prospective_total_after_acceptance", 50), ("batch06_closed", True), ("stop_for_prospective_scientific_decision", True)):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(records, {**prior, key: value}, acceptance)
            for altered in (records[:-1], list(reversed(records)), [*records[:60], {**records[60], "queue_rank": 60.0}, *records[61:]],
                            [*records[:60], {**records[60], "queue_rank": True}, *records[61:]], [*records[:60], {**records[60], "priority": "other"}, *records[61:]]):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(altered, prior, acceptance)
            self.assertEqual(json.dumps([records, prior, acceptance], sort_keys=True), before)
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repo = root / "repo"
                review = repo / "docs/190-review-doc189-oulu-batch06-activation.md"
                review.parent.mkdir(parents=True)
                review.write_text("synthetic Review190 acceptance", encoding="ascii")
                report = repo / "results/phase1/oulu-batch06-activation-v1.json"
                write_immutable_record(report, prior)
                check = {"head_sha": "a81bd9259478a8a49ad0783fdb777329791a99d5", "run_id": 38696814671,
                         "job_id": 116295204960, "status": "completed", "conclusion": "success",
                         "job_status": "completed", "job_conclusion": "success"}
                authority = {**acceptance, "review190_sha256": module._sha256(review)}
                preflight = {"checkpoint": 191, "acceptance": authority, "activation_CI": check,
                             "packet_preparation_authorized": True, "queue_ranks": list(range(60, 70)),
                             "accepted_prior_report_sha256": module._sha256(report),
                             "accepted_recovery": {"accepted_by_Review178": True}, "protected_snapshots": {}}
                original = json.dumps(preflight, sort_keys=True)
                with patch.object(module, "ROOT", repo), patch.object(module, "REVIEW190_SHA256", module._sha256(review)), patch.object(module, "ACCEPTED189_REPORT_SHA256", module._sha256(report)):
                    self.assertEqual(module.verified_packet_authority(preflight), authority)
                    invalid = [{**preflight, "acceptance": None}, {**preflight, "acceptance": {**authority, "review190_sha256": "0" * 64}},
                               {**preflight, "checkpoint": 191.0}, {**preflight, "packet_preparation_authorized": False},
                               {**preflight, "queue_ranks": list(range(50, 60))}, {**preflight, "queue_ranks": [60.0, *range(61, 70)]},
                               {**preflight, "accepted_prior_report_sha256": "0" * 64}, {**preflight, "activation_CI": None},
                               {**preflight, "accepted_recovery": None}, {**preflight, "accepted_recovery": {"accepted_by_Review178": False}}]
                    for key, value in (("head_sha", "0" * 40), ("run_id", 38694502603), ("run_id", float(check["run_id"])),
                                       ("job_id", 116287801095), ("status", "in_progress"), ("conclusion", "failure"),
                                       ("job_status", "queued"), ("job_conclusion", "failure")):
                        invalid.append({**preflight, "activation_CI": {**check, key: value}})
                    for index, bad in enumerate(invalid):
                        with self.assertRaises(ValueError):
                            module.verified_packet_authority(bad)
                        path = root / f"bad-{index}.json"
                        write_immutable_record(path, bad)
                        args = Namespace(input_root=root / "source", audit_root=root / "audit", exact_root=root / "exact",
                            screen_root=root / "screen", frozen_root=root / "frozen", archive_records=root / "pins",
                            activation_root=root / "activation", preflight=path, out_root=root / "never-created")
                        with patch.object(module, "verified_archive_identities", side_effect=AssertionError("must not reach archives")):
                            with self.assertRaises(ValueError):
                                module.prepare(args)
                        self.assertFalse(args.out_root.exists())
                    for output in (ROOT / "results/refused-visual-batch07", root, root / "source/refused"):
                        with self.assertRaises(ValueError):
                            module.prepare(Namespace(input_root=root, audit_root=root, exact_root=root, screen_root=root,
                                frozen_root=root, archive_records=root, activation_root=root, preflight=root / "missing", out_root=output))
                self.assertEqual(json.dumps(preflight, sort_keys=True), original)
        finally:
            sys.path.pop(0)

    def test_batch06_packet_selection_requires_additive_acceptance_and_unchanged_history(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_visual_batch06 as module
            records = [{"queue_rank": rank, "priority": "cross_role_conflicting_label"} for rank in range(60)]
            prior = {"activation_checkpoint_review_pending": True, "batch05_accepted_reconciled_disposition_state": False,
                     "accepted_batch05_current_effective_dispositions": 0, "effective_dispositions_activated": 10,
                     "current_materialized_disposition_counts": {"rejected_false_positive": 10},
                     "accepted_current_total": 40, "prospective_total_after_acceptance": 50, "batch05_closed": False}
            acceptance = {"batch05_activation_checkpoint_accepted": True, "accepted_current_total": 50,
                          "accepted_batch05_disposition_counts": {"rejected_false_positive": 10}}
            original = json.dumps([records, prior, acceptance], sort_keys=True)
            self.assertEqual([row["queue_rank"] for row in module.fixed_next_records(records, prior, acceptance)], list(range(50, 60)))
            self.assertEqual(json.dumps([records, prior, acceptance], sort_keys=True), original)
            for key, value in (("batch05_activation_checkpoint_accepted", False), ("accepted_current_total", 40), ("accepted_batch05_disposition_counts", {"rejected_false_positive": 9})):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(records, prior, {**acceptance, key: value})
            for key, value in (("activation_checkpoint_review_pending", False), ("batch05_accepted_reconciled_disposition_state", True), ("accepted_batch05_current_effective_dispositions", 10), ("effective_dispositions_activated", 0), ("current_materialized_disposition_counts", {}), ("accepted_current_total", 50), ("prospective_total_after_acceptance", 40), ("batch05_closed", True)):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(records, {**prior, key: value}, acceptance)
            for altered in (records[:-1], list(reversed(records)), [*records[:50], {**records[50], "queue_rank": 50.0}, *records[51:]], [*records[:50], {**records[50], "queue_rank": True}, *records[51:]], [*records[:50], {**records[50], "priority": "other"}, *records[51:]]):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(altered, prior, acceptance)
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (ROOT / "results/refused-visual-batch06", root, root / "source/refused"):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(input_root=root, audit_root=root, exact_root=root, screen_root=root,
                                                 frozen_root=root, archive_records=root, activation_root=root, out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch05_packet_selection_requires_additive_acceptance_and_unchanged_history(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_visual_batch05 as module
            records = [{"queue_rank": rank, "priority": "cross_role_conflicting_label"} for rank in range(50)]
            prior = {"activation_checkpoint_review_pending": True, "batch04_accepted_reconciled_disposition_state": False,
                     "accepted_batch04_current_effective_dispositions": 0, "effective_dispositions_activated": 10,
                     "current_materialized_disposition_counts": {"rejected_false_positive": 10},
                     "accepted_current_total": 30, "prospective_total_after_acceptance": 40}
            acceptance = {"batch04_activation_checkpoint_accepted": True, "accepted_current_total": 40,
                          "accepted_batch04_disposition_counts": {"rejected_false_positive": 10}}
            original = json.dumps([records, prior, acceptance], sort_keys=True)
            self.assertEqual([row["queue_rank"] for row in module.fixed_next_records(records, prior, acceptance)], list(range(40, 50)))
            self.assertEqual(json.dumps([records, prior, acceptance], sort_keys=True), original)
            for key, value in (("batch04_activation_checkpoint_accepted", False), ("accepted_current_total", 30), ("accepted_batch04_disposition_counts", {"rejected_false_positive": 9})):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(records, prior, {**acceptance, key: value})
            for key, value in (("activation_checkpoint_review_pending", False), ("batch04_accepted_reconciled_disposition_state", True), ("accepted_batch04_current_effective_dispositions", 10), ("effective_dispositions_activated", 0), ("current_materialized_disposition_counts", {}), ("accepted_current_total", 40), ("prospective_total_after_acceptance", 30)):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(records, {**prior, key: value}, acceptance)
            for altered in (records[:-1], list(reversed(records)), [*records[:40], {**records[40], "queue_rank": 40.0}, *records[41:]], [*records[:40], {**records[40], "priority": "other"}, *records[41:]]):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(altered, prior, acceptance)
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for output in (ROOT / "results/refused-visual-batch05", root):
                    with self.assertRaises(ValueError):
                        module.prepare(Namespace(input_root=root, audit_root=root, exact_root=root, screen_root=root,
                                                 frozen_root=root, archive_records=root, activation_root=root, out_root=output))
        finally:
            sys.path.pop(0)

    def test_batch04_packet_selection_requires_closed_batch03_and_exact_queue(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_visual_batch04 as module
            records = [{"queue_rank": rank, "priority": "cross_role_conflicting_label"} for rank in range(40)]
            prior = {"batch03_accepted_reconciled_disposition_state": True, "effective_dispositions_activated": 10,
                     "current_effective_disposition_counts": {"rejected_false_positive": 10}}
            original = json.dumps(records, sort_keys=True)
            self.assertEqual([row["queue_rank"] for row in module.fixed_next_records(records, prior)], list(range(30, 40)))
            self.assertEqual(json.dumps(records, sort_keys=True), original)
            for altered in ({**prior, "batch03_accepted_reconciled_disposition_state": False}, {**prior, "effective_dispositions_activated": 0}, {**prior, "current_effective_disposition_counts": {"rejected_false_positive": 9}}):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(records, altered)
            with self.assertRaises(ValueError):
                module.fixed_next_records(records[:39], prior)
            records[30], records[31] = records[31], records[30]
            with self.assertRaises(ValueError):
                module.fixed_next_records(records, prior)
            records[30], records[31] = records[31], records[30]
            records[30]["priority"] = "cross_role"
            with self.assertRaises(ValueError):
                module.fixed_next_records(records, prior)
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                args = Namespace(activation_root=root, out_root=ROOT / "results/refused-batch04", input_root=root, audit_root=root,
                                 exact_root=root, screen_root=root, frozen_root=root, archive_records=root)
                with self.assertRaises(ValueError):
                    module.prepare(args)
                args.out_root = root
                with self.assertRaises(ValueError):
                    module.prepare(args)
        finally:
            sys.path.pop(0)

    def test_batch03_packet_selection_requires_closed_batch02_and_exact_queue(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_visual_batch03 as module
            records = [{"queue_rank": rank, "priority": "cross_role_conflicting_label"} for rank in range(30)]
            prior = {"batch02_accepted_reconciled_disposition_state": True, "effective_dispositions_activated": 10,
                     "current_effective_disposition_counts": {"rejected_false_positive": 10}}
            self.assertEqual([row["queue_rank"] for row in module.fixed_next_records(records, prior)], list(range(20, 30)))
            for altered in ({**prior, "batch02_accepted_reconciled_disposition_state": False}, {**prior, "effective_dispositions_activated": 0}, {**prior, "current_effective_disposition_counts": {"rejected_false_positive": 9}}):
                with self.assertRaises(ValueError):
                    module.fixed_next_records(records, altered)
            with self.assertRaises(ValueError):
                module.fixed_next_records(records[:29], prior)
            records[20], records[21] = records[21], records[20]
            with self.assertRaises(ValueError):
                module.fixed_next_records(records, prior)
            records[20], records[21] = records[21], records[20]
            records[20]["priority"] = "cross_role"
            with self.assertRaises(ValueError):
                module.fixed_next_records(records, prior)
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                args = Namespace(activation_root=root, out_root=ROOT / "results/refused-batch03", input_root=root, audit_root=root,
                                 exact_root=root, screen_root=root, frozen_root=root, archive_records=root)
                with self.assertRaises(ValueError):
                    module.prepare(args)
                args.out_root = root
                with self.assertRaises(ValueError):
                    module.prepare(args)
        finally:
            sys.path.pop(0)

    def test_batch02_human_rank_adapter_preserves_disagreement_and_hard_stop(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import import_oulu_human_batch02 as module
            pairs = [{"queue_rank": rank, "packet_sha256": str(rank), "required_assets_sha256": {"image": str(rank)},
                      "ai_disposition": "rejected_false_positive"} for rank in range(10, 20)]
            definition = {"sha256": "bound", "pairs": pairs}
            human = {"version": 1, "reviewer": {"kind": "owner_human", "id": "owner", "personally_inspected_bound_evidence": True},
                     "review_definition_sha256": "bound", "reviewed_at_utc": "2026-10-10T09:27:15Z",
                     "pairs": [{"queue_rank": pair["queue_rank"], "packet_sha256": pair["packet_sha256"],
                                "reviewed_assets_sha256": pair["required_assets_sha256"], "personally_reviewed": True,
                                "disposition": "rejected_false_positive", "rationale": "Observed evidence", "capture_provenance_certified": False} for pair in pairs]}
            original = json.dumps(human, sort_keys=True)
            rows = module.validate_batch02(human, definition)
            self.assertEqual([row["queue_rank"] for row in rows], list(range(10, 20)))
            self.assertTrue(all(not row["disagreement"] and not row["effective_disposition_activated"] for row in rows))
            self.assertEqual(json.dumps(human, sort_keys=True), original)
            human["pairs"][0]["disposition"] = "uncertain_insufficient_evidence"
            human["pairs"][1]["disposition"] = "confirmed_same_content_or_derived_lineage"
            rows = module.validate_batch02(human, definition)
            self.assertEqual(rows[0]["effective_disposition"], "uncertain_insufficient_evidence")
            self.assertTrue(rows[1]["stop_for_prospective_scientific_decision"])
            self.assertEqual(rows[1]["effective_disposition"], "uncertain_insufficient_evidence")
            with self.assertRaises(ValueError):
                module.validate_batch02({**human, "pairs": human["pairs"][:-1]}, definition)
            for key, value in (("queue_rank", 0), ("queue_rank", True), ("queue_rank", 11), ("rationale", ""), ("packet_sha256", "drift"), ("personally_reviewed", False), ("reviewed_assets_sha256", {})):
                altered = {**human, "pairs": [{**human["pairs"][0], key: value}, *human["pairs"][1:]]}
                with self.assertRaises(ValueError):
                    module.validate_batch02(altered, definition)
        finally:
            sys.path.pop(0)

    def test_batch02_handoff_exports_original_queue_ranks_and_blank_answers(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_owner_batch02 as module
            definition = {"pairs": [{"queue_rank": rank} for rank in range(10, 20)]}
            page = module.render_batch02(definition, "digest")
            self.assertIn("queue_rank:pair.queue_rank,packet_sha256", page)
            self.assertNotIn("queue_rank:rank,packet_sha256", page)
            self.assertIn("disposition:'',rationale:''", page)
            self.assertIn("oulu-batch02-human-review.json", page)
            self.assertIn("'Queue '+pair.queue_rank", page)
            self.assertNotIn("Batch 01", page)
            with self.assertRaises(ValueError):
                module.render_batch02({"pairs": [{"queue_rank": rank} for rank in range(10)]}, "digest")
            escaped = module.render_batch02({**definition, "text": "</script>"}, "digest")
            self.assertIn("\\u003c/script>", escaped)
        finally:
            sys.path.pop(0)

    def test_next_visual_batch_requires_closed_prior_and_exact_order(self) -> None:
        spec = importlib.util.spec_from_file_location("prepare_oulu_visual_batch02", ROOT / "scripts/prepare_oulu_visual_batch02.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        records = [{"queue_rank": rank, "priority": "cross_role_conflicting_label"} for rank in range(20)]
        prior = {"batch01_accepted_reconciled_disposition_state": True, "current_effective_disposition_counts": {"rejected_false_positive": 10}}
        self.assertEqual([row["queue_rank"] for row in module.fixed_next_records(records, prior)], list(range(10, 20)))
        with self.assertRaises(ValueError):
            module.fixed_next_records(records, {**prior, "batch01_accepted_reconciled_disposition_state": False})
        with self.assertRaises(ValueError):
            module.fixed_next_records(records[:19], prior)
        records[10], records[11] = records[11], records[10]
        with self.assertRaises(ValueError):
            module.fixed_next_records(records, prior)
        from argparse import Namespace
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            arguments = Namespace(out_root=ROOT / "results/refused-batch02", input_root=source,
                                  audit_root=source, exact_root=source, screen_root=source,
                                  frozen_root=source, archive_records=source, activation_root=source)
            with self.assertRaises(ValueError):
                module.prepare(arguments)
            arguments.out_root = source
            with self.assertRaises(ValueError):
                module.prepare(arguments)

    def test_handoff_private_output_refused_and_definition_escaped(self) -> None:
        spec = importlib.util.spec_from_file_location("prepare_oulu_owner_review", ROOT / "scripts/prepare_oulu_owner_review.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            with self.assertRaises(ValueError):
                module.private_output(ROOT / "results/refused-human-output", [source])
            with self.assertRaises(ValueError):
                module.private_output(source, [source])
        page = module.render_page({"pairs": [], "text": "</script><script>bad</script>"}, "a" * 64)
        self.assertNotIn("</script><script>bad", page)
        self.assertIn("\\u003c", page)

    def fixture(self):
        definition = {"sha256": "a" * 64, "pairs": [{"packet_sha256": format(rank, "064x"),
                      "required_assets_sha256": {"temporal": "b" * 64, **({"full_resolution": "c" * 64} if rank == 4 else {})},
                      "ai_disposition": "uncertain_insufficient_evidence" if rank == 4 else "rejected_false_positive"} for rank in range(10)]}
        record = {"version": 1, "reviewer": {"kind": "owner_human", "id": "synthetic-reviewer", "personally_inspected_bound_evidence": True},
                  "review_definition_sha256": definition["sha256"], "reviewed_at_utc": "2026-10-10T00:00:00+00:00",
                  "pairs": [{"queue_rank": rank, "packet_sha256": pair["packet_sha256"],
                             "reviewed_assets_sha256": dict(pair["required_assets_sha256"]), "personally_reviewed": True,
                             "disposition": pair["ai_disposition"], "rationale": "Synthetic fixture only", "capture_provenance_certified": False}
                            for rank, pair in enumerate(definition["pairs"])]}
        return record, definition

    def test_human_attestation_required_not_ai_or_blank_template(self) -> None:
        from fas.human_review import validate_human_review
        record, definition = self.fixture()
        self.assertEqual(len(validate_human_review(record, definition)), 10)
        record["reviewer"]["kind"] = "AI"
        with self.assertRaises(ValueError):
            validate_human_review(record, definition)
        record["reviewer"]["kind"] = "owner_human"
        record["reviewer"]["personally_inspected_bound_evidence"] = False
        with self.assertRaises(ValueError):
            validate_human_review(record, definition)

    def test_incomplete_or_duplicate_pair_review_is_rejected(self) -> None:
        from fas.human_review import validate_human_review
        record, definition = self.fixture()
        record["pairs"].pop()
        with self.assertRaises(ValueError):
            validate_human_review(record, definition)
        record["pairs"].append(record["pairs"][0])
        with self.assertRaises(ValueError):
            validate_human_review(record, definition)

    def test_full_resolution_hash_and_rationale_are_required(self) -> None:
        from fas.human_review import validate_human_review
        record, definition = self.fixture()
        record["pairs"][4]["reviewed_assets_sha256"].pop("full_resolution")
        with self.assertRaises(ValueError):
            validate_human_review(record, definition)
        record, definition = self.fixture()
        record["pairs"][0]["rationale"] = " "
        with self.assertRaises(ValueError):
            validate_human_review(record, definition)

    def test_disagreement_is_preserved_and_confirmation_stops_execution(self) -> None:
        from fas.human_review import validate_human_review
        record, definition = self.fixture()
        record["pairs"][0]["disposition"] = "confirmed_same_content_or_derived_lineage"
        result = validate_human_review(record, definition)[0]
        self.assertTrue(result["disagreement"])
        self.assertTrue(result["stop_for_prospective_scientific_decision"])
        self.assertEqual(result["effective_disposition"], "uncertain_insufficient_evidence")
        self.assertFalse(result["model_execution_authorized"])

    def test_full_resolution_export_preserves_accepted_rgb_identity(self) -> None:
        from fas.human_review import full_resolution_frames
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "clip.avi"
            subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=64x48:rate=5",
                            "-frames:v", "4", "-c:v", "mjpeg", "-threads", "1", str(path)], check=True)
            media = probe_video(path)
            frames = full_resolution_frames(path, media, [0, 2, 3])
            self.assertEqual(frames[2].shape, (48, 64, 3))
            self.assertEqual(hashlib.sha256(frames[2].tobytes()).hexdigest(), media["frame_index"][2]["rgb_sha256"])
            media["frame_index"][2]["rgb_sha256"] = "0" * 64
            with self.assertRaises(ValueError):
                full_resolution_frames(path, media, [2])


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
    def test_batch06_packet_retry_requires_review180_and_exact179_CI(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_visual_batch06 as module
            from argparse import Namespace
            from fas.freeze import write_immutable_record
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repo = root / "repo"
                review = repo / "docs/180-review-doc179-oulu-recovery-aware-guard.md"
                review.parent.mkdir(parents=True)
                review.write_text("synthetic Review180 acceptance", encoding="ascii")
                recovery = {"binding_sha256": "a" * 64, "accepted177_report_sha256": "b" * 64,
                            "archive_pin_report_sha256": "c" * 64, "review178_sha256": "d" * 64}
                report = repo / "results/phase1/oulu-recovery-aware-guard-v1.json"
                runner = "4996ee828d1a159184616669033e324b1dadf3335a480402cb2ad62e8e9fd62b"
                write_immutable_record(report, {"runner_sha256": runner, "guard_integration_checkpoint_review_pending": True,
                    "packet_preparation_authorized": False, "accepted_environment_binding_sha256": recovery["binding_sha256"],
                    **{field: recovery[field] for field in ("accepted177_report_sha256", "archive_pin_report_sha256", "review178_sha256")}})
                check = {"head_sha": "63505d1c1b2f940fa077398127ef29a49ede95ef", "run_id": 38676766354,
                         "job_id": 116232038205, "status": "completed", "conclusion": "success",
                         "job_status": "completed", "job_conclusion": "success"}
                authority = {"accepted_by_Review180": True, "packet_preparation_checkpoint": "181",
                    "review180_sha256": module._sha256(review), "accepted179_report_sha256": module._sha256(report),
                    "accepted179_runner_sha256": runner, "publication_CI": check}
                preflight = {"guard_acceptance": authority, "packet_preparation_authorized": True,
                             "queue_ranks": list(range(50, 60)), "accepted_recovery": recovery, "protected_snapshots": {}}
                before = json.dumps(preflight, sort_keys=True)
                with patch.object(module, "ROOT", repo):
                    self.assertEqual(module.verified_packet_authority(preflight), authority)
                    invalid = [{**preflight, "guard_acceptance": None}, {**preflight, "packet_preparation_authorized": False},
                               {**preflight, "queue_ranks": list(range(60, 70))}]
                    for field, value in (("accepted_by_Review180", False), ("packet_preparation_checkpoint", "179"),
                                         ("review180_sha256", "0" * 64), ("accepted179_report_sha256", "0" * 64),
                                         ("accepted179_runner_sha256", "0" * 64)):
                        invalid.append({**preflight, "guard_acceptance": {**authority, field: value}})
                    for field, value in (("head_sha", "0" * 40), ("run_id", 38673838230), ("job_id", 116222822739),
                                         ("status", "in_progress"), ("conclusion", "failure"), ("job_status", "queued"), ("job_conclusion", "failure")):
                        invalid.append({**preflight, "guard_acceptance": {**authority, "publication_CI": {**check, field: value}}})
                    for field in recovery:
                        invalid.append({**preflight, "accepted_recovery": {**recovery, field: "0" * 64}})
                    for index, bad in enumerate(invalid):
                        with self.assertRaises(ValueError):
                            module.verified_packet_authority(bad)
                        path = root / f"bad-{index}.json"
                        write_immutable_record(path, bad)
                        args = Namespace(input_root=root / "source", audit_root=root / "audit", exact_root=root / "exact",
                            screen_root=root / "screen", frozen_root=root / "frozen", archive_records=root / "pins",
                            activation_root=root / "activation", preflight=path, guard_only=False, out_root=root / "never-created")
                        with self.assertRaises(ValueError):
                            module.prepare(args)
                        self.assertFalse(args.out_root.exists())
                    self.assertEqual(json.dumps(preflight, sort_keys=True), before)
        finally:
            sys.path.pop(0)

    def test_recovery_aware_fast_guard_binds_authority_and_rejects_every_stat_drift(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import prepare_oulu_visual_batch06 as module
            from argparse import Namespace
            from fas.freeze import write_immutable_record
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source, pins_root, recovered, repo = (root / name for name in ("source", "pins", "recovered", "repo"))
                for folder in (source, pins_root, recovered):
                    folder.mkdir()
                pins, rows, anchors = {}, {}, {}
                for name in module.ANCHORS:
                    path = source / name
                    path.write_bytes(b"synthetic bytes")
                    current = module.file_identity(path.stat())
                    old = {key: value for key, value in current.items() if key != "byte_size"}
                    old["device"] += 1
                    pin_path = pins_root / (name + ".sha256.json")
                    write_immutable_record(pin_path, {"file_identity": old})
                    digest = hashlib.sha256(path.read_bytes()).hexdigest()
                    anchors[name] = digest
                    pins[name] = {"sha256": digest, "byte_size": current["byte_size"], "private_record_sha256": module._sha256(pin_path)}
                    rows[name] = {"old_private_record_sha256": module._sha256(pin_path), "old_file_identity": old,
                                  "current_file_identity": current, "byte_size": current["byte_size"], "current_sha256": digest,
                                  "frozen_sha256": digest, "whole_file_read": True, "content_hash_matches_frozen": True,
                                  "stat_identity_stable_during_hash": True, "changed_fields": ["device"]}
                    write_immutable_record(recovered / (name + ".rehash.json"), rows[name])
                public = repo / "results/phase1/oulu-archive-byte-pinning-v1.json"
                write_immutable_record(public, {"media_archives": pins})
                binding_path = recovered / "environment_binding.json"
                write_immutable_record(binding_path, {"archives": rows, "recovery_checkpoint_review_pending": True,
                                                     "old_archive_pins_unchanged": True, "archive_pin_report_sha256": module._sha256(public)})
                report_path = repo / "results/phase1/oulu-archive-identity-recovery-v1.json"
                write_immutable_record(report_path, {"private_environment_binding_sha256": module._sha256(binding_path),
                                                     "archive_pin_report_sha256": module._sha256(public),
                                                     "archive_results": {name: {"rehash_record_sha256": module._sha256(recovered / (name + ".rehash.json"))} for name in pins}})
                review = repo / "docs/178-review-doc177-oulu-archive-identity-recovery.md"
                review.parent.mkdir(parents=True)
                review.write_text("synthetic acceptance", encoding="ascii")
                recovery = {"accepted_by_Review178": True, "review178_sha256": module._sha256(review),
                            "accepted177_report_sha256": module._sha256(report_path), "archive_pin_report_sha256": module._sha256(public),
                            "binding_path": str(binding_path), "binding_sha256": module._sha256(binding_path)}
                marker = root / "protected/marker.json"
                write_immutable_record(marker, {"prior": True})
                preflight = root / "preflight.json"
                write_immutable_record(preflight, {"accepted_recovery": recovery, "packet_preparation_authorized": False,
                    "protected_snapshots": {str(marker.parent): {marker.name: module._sha256(marker)}},
                    "pinned_file_sha256": {}, "frozen_file_sha256": {}, "study_config_sha256": {},
                    "preparation_code_sha256": module._sha256(Path(module.__file__)),
                    "activation_CI": {"head_sha": "226943f77710a938b54581ccb03381e69c0d7fba", "run_id": 38666749697,
                                      "job_id": 116200334607, "status": "completed", "conclusion": "success"}})
                args = Namespace(input_root=source, audit_root=root / "audit", exact_root=root / "exact", screen_root=root / "screen",
                                 frozen_root=root / "frozen", archive_records=pins_root, activation_root=root / "activation",
                                 preflight=preflight, guard_only=True, out_root=root / "never-created")
                before = json.dumps(recovery, sort_keys=True)
                with patch.object(module, "ROOT", repo), patch.object(module, "ANCHORS", anchors):
                    self.assertEqual(len(module.verified_archive_identities(source, pins_root, recovery)), 3)
                    self.assertEqual(module.prepare(args)["archives_verified"], 3)
                    self.assertFalse(args.out_root.exists())
                    with self.assertRaises(ValueError):
                        module.verified_archive_identities(source, pins_root)
                    original = module.file_identity
                    for field in ("device", "inode", "byte_size", "mtime_ns", "ctime_ns"):
                        with patch.object(module, "file_identity", side_effect=lambda value, field=field: {**original(value), field: original(value)[field] + 1}):
                            with self.assertRaisesRegex(ValueError, "archive identity drift"):
                                module.prepare(args)
                            self.assertFalse(args.out_root.exists())
                    for field, value in (("binding_sha256", "0" * 64), ("archive_pin_report_sha256", "0" * 64),
                                         ("accepted177_report_sha256", "0" * 64), ("review178_sha256", "0" * 64), ("accepted_by_Review178", False)):
                        with self.assertRaises(ValueError):
                            module.verified_archive_identities(source, pins_root, {**recovery, field: value})
                    with self.assertRaisesRegex(ValueError, "requires review"):
                        module.prepare(Namespace(**{**vars(args), "guard_only": False}))
                    marker.write_bytes(b"changed prior evidence")
                    with self.assertRaisesRegex(ValueError, "protected prior evidence drift"):
                        module.prepare(args)
                    self.assertFalse(args.out_root.exists())
                    self.assertEqual(json.dumps(recovery, sort_keys=True), before)
        finally:
            sys.path.pop(0)

    def test_batch09_recovery_uses_latest_accepted_identity_and_current_authority(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import recover_oulu_archive_identity_batch09 as module
            from argparse import Namespace
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source, pin_root, repo, previous = (root / name for name in ("source", "pins", "repo", "accepted177"))
                source.mkdir()
                payload = b"synthetic219 whole archive, not video payload"
                anchors, pins, rows, observations = {}, {}, {}, {}
                for name in module.ANCHORS:
                    archive = source / name
                    archive.write_bytes(payload)
                    current = module.file_identity(archive.stat())
                    latest = {**current, "device": current["device"] + 1}
                    original = {key: value for key, value in {**current, "device": current["device"] + 2}.items() if key != "byte_size"}
                    expected = {"sha256": hashlib.sha256(payload).hexdigest(), "byte_size": len(payload)}
                    before = json.dumps([expected, latest, current], sort_keys=True)
                    row = module.rehash_current_archive(archive, expected, latest, current)
                    self.assertEqual(row["old_file_identity"], latest)
                    self.assertNotEqual(row["old_file_identity"], original)
                    self.assertFalse(row["proposed_binding_accepted"])
                    self.assertEqual(json.dumps([expected, latest, current], sort_keys=True), before)
                    for wrong in ({**latest, "device": current["device"]}, {**latest, "inode": latest["inode"] + 1},
                                  {**latest, "byte_size": True}, {**latest, "ctime_ns": latest["ctime_ns"] + 1}):
                        with patch.object(module, "rehash_archive", side_effect=AssertionError("must refuse before full hash")):
                            with self.assertRaises(ValueError):
                                module.rehash_current_archive(archive, expected, wrong, current)
                    with self.assertRaises(ValueError):
                        module.rehash_current_archive(archive, {**expected, "sha256": "0" * 64}, latest, current)
                    with self.assertRaises(ValueError):
                        module.rehash_current_archive(archive, expected, latest, {**current, "device": current["device"] + 3})
                    link = root / (name + ".link")
                    link.symlink_to(archive)
                    with self.assertRaises(ValueError):
                        module.rehash_current_archive(link, expected, latest, current)
                    pin_path = pin_root / (name + ".sha256.json")
                    module.write_immutable_record(pin_path, {"file_identity": original})
                    anchors[name] = expected["sha256"]
                    pins[name] = {**expected, "private_record_sha256": module._sha256(pin_path)}
                    rows[name] = {"old_file_identity": original, "old_private_record_sha256": module._sha256(pin_path),
                                  "current_file_identity": latest, "current_sha256": expected["sha256"], "frozen_sha256": expected["sha256"],
                                  "byte_size": len(payload), "whole_file_read": True, "content_hash_matches_frozen": True,
                                  "stat_identity_stable_during_hash": True, "changed_fields": ["device"]}
                    module.write_immutable_record(previous / (name + ".rehash.json"), rows[name])
                    observations[name] = {"observed_file_identity": current}
                pin_report = repo / "results/phase1/oulu-archive-byte-pinning-v1.json"
                module.write_immutable_record(pin_report, {"media_archives": pins})
                binding_path = previous / "environment_binding.json"
                module.write_immutable_record(binding_path, {"archive_pin_report_sha256": module._sha256(pin_report), "archives": rows,
                    "recovery_checkpoint_review_pending": True, "old_archive_pins_unchanged": True})
                old_report = repo / "results/phase1/oulu-archive-identity-recovery-v1.json"
                module.write_immutable_record(old_report, {"private_environment_binding_sha256": module._sha256(binding_path),
                    "archive_pin_report_sha256": module._sha256(pin_report), "archive_results": {name: {"rehash_record_sha256": module._sha256(previous / (name + ".rehash.json"))} for name in anchors}})
                old_review = repo / "docs/178-review-doc177-oulu-archive-identity-recovery.md"
                old_review.parent.mkdir(parents=True)
                old_review.write_text("synthetic accepted177", encoding="ascii")
                recovery = {"accepted_by_Review178": True, "review178_sha256": module._sha256(old_review),
                    "archive_pin_report_sha256": module._sha256(pin_report), "accepted177_report_sha256": module._sha256(old_report),
                    "binding_path": str(binding_path), "binding_sha256": module._sha256(binding_path)}
                blocker_path = root / "blocker217.json"
                module.write_immutable_record(blocker_path, {"accepted_recovery": recovery, "archive_observations": observations})
                report = repo / "results/phase1/oulu-batch09-packet-preparation-blocker-v1.json"
                module.write_immutable_record(report, {"private_blocker_sha256": module._sha256(blocker_path)})
                review = repo / "docs/218-review-doc217-oulu-batch09-archive-device-blocker.md"
                review.write_text("synthetic bounded Review218", encoding="ascii")
                document = repo / "docs/217-review-response-doc216-oulu-batch09-packets.md"
                document.write_text("synthetic217 blocker", encoding="ascii")
                preflight = {"checkpoint": 219, "recovery_authorized": True, "packet_retry_authorized": False, "guard_integration_authorized": False,
                    "review218_sha256": module._sha256(review), "accepted217_document_sha256": module._sha256(document),
                    "accepted217_report_sha256": module._sha256(report), "accepted217_blocker_sha256": module._sha256(blocker_path),
                    "blocker_path": str(blocker_path), "accepted_recovery": recovery, "archive_anchor_sha256": anchors,
                    "archive_pin_report_sha256": module._sha256(pin_report), "latest_accepted_archive_identity": {name: row["current_file_identity"] for name, row in rows.items()},
                    "observed_archive_identity": {name: row["observed_file_identity"] for name, row in observations.items()},
                    "source217_CI": {"head_sha": "9082585c811ee3b1636b33145e5748876083ef30", "run_id": 39354730481,
                        "job_id": 118406801611, "status": "completed", "conclusion": "success", "job_status": "completed", "job_conclusion": "success",
                        "listed_successful_steps": 12, "all_steps_success": True},
                    "protected_snapshots": {}, "pinned_file_sha256": {}, "frozen_file_sha256": {}, "study_config_sha256": {},
                    "recovery_code_sha256": module._sha256(Path(module.__file__))}
                original = json.dumps(preflight, sort_keys=True)
                preflight_path = root / "preflight219.json"
                module.write_immutable_record(preflight_path, preflight)
                args = Namespace(input_root=source, archive_records=pin_root, preflight=preflight_path, out_root=root / "recovery219")
                with patch.object(module, "ROOT", repo), patch.object(module, "ANCHORS", anchors), patch.object(module, "REVIEW218_SHA256", module._sha256(review)), patch.object(module, "ACCEPTED217_DOCUMENT_SHA256", module._sha256(document)), patch.object(module, "ACCEPTED217_REPORT_SHA256", module._sha256(report)), patch.object(module, "ACCEPTED217_BLOCKER_SHA256", module._sha256(blocker_path)):
                    result = module.recover(args)
                    self.assertEqual(result["total_bytes_hashed"], len(payload) * 3)
                    self.assertTrue(result["recovery_checkpoint_review_pending"])
                    for key in ("proposed_binding_accepted", "packet_runner_guard_changed", "packet_preparation_authorized_by_this_record", "archive_identity_blocker_closed", "individual_video_payloads_opened", "media_decoding_or_extraction_performed"):
                        self.assertFalse(result[key])
                    self.assertEqual(len(list(args.out_root.iterdir())), 4)
                    for name, row in result["archives"].items():
                        self.assertEqual(row["old_file_identity"], rows[name]["current_file_identity"])
                        self.assertEqual(row["original_frozen_pin_file_identity"], rows[name]["old_file_identity"])
                    invalid = [{**preflight, key: value} for key, value in (("checkpoint", 219.0), ("recovery_authorized", False),
                        ("packet_retry_authorized", True), ("guard_integration_authorized", True), ("review218_sha256", "0" * 64),
                        ("accepted217_document_sha256", "0" * 64), ("accepted217_report_sha256", "0" * 64),
                        ("accepted217_blocker_sha256", "0" * 64), ("archive_anchor_sha256", {}), ("recovery_code_sha256", "0" * 64))]
                    for key, value in (("head_sha", "0" * 40), ("run_id", 39353105356), ("run_id", float(preflight["source217_CI"]["run_id"])),
                                       ("job_id", 118401642331), ("status", "in_progress"), ("conclusion", "failure"),
                                       ("job_status", "queued"), ("job_conclusion", "failure"), ("listed_successful_steps", 11), ("all_steps_success", False)):
                        invalid.append({**preflight, "source217_CI": {**preflight["source217_CI"], key: value}})
                    for index, bad in enumerate(invalid):
                        bad_path = root / f"bad219-{index}.json"
                        module.write_immutable_record(bad_path, bad)
                        rejected = Namespace(**{**vars(args), "preflight": bad_path, "out_root": root / "never-created"})
                        with patch.object(module, "rehash_archive", side_effect=AssertionError("must not hash")):
                            with self.assertRaises(ValueError):
                                module.recover(rejected)
                        self.assertFalse(rejected.out_root.exists())
                    for output in (args.out_root, ROOT / "results/refused-recovery219", source / "refused", root):
                        with self.assertRaises(ValueError):
                            module.recover(Namespace(**{**vars(args), "out_root": output}))
                self.assertEqual(json.dumps(preflight, sort_keys=True), original)
        finally:
            sys.path.pop(0)

    def test_recovery219_guard_requires_review220_and_rejects_future_drift(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import verify_oulu_archive_guard_batch09 as module
            import prepare_oulu_visual_batch06 as historical
            from argparse import Namespace
            from contextlib import ExitStack
            from fas.freeze import write_immutable_record
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source, pins_root, old_root, recovered, repo = (root / name for name in ("source", "pins", "old177", "recovery219", "repo"))
                source.mkdir()
                pins, old_rows, rows, anchors, sizes = {}, {}, {}, {}, {}
                for name in module.ANCHORS:
                    archive = source / name
                    archive.write_bytes(b"synthetic221 guard archive")
                    current = module.file_identity(archive.stat())
                    latest = {**current, "device": current["device"] + 1}
                    original = {key: value for key, value in {**current, "device": current["device"] + 2}.items() if key != "byte_size"}
                    pin_path = pins_root / (name + ".sha256.json")
                    write_immutable_record(pin_path, {"file_identity": original})
                    anchors[name] = hashlib.sha256(archive.read_bytes()).hexdigest()
                    sizes[name] = current["byte_size"]
                    pins[name] = {"private_record_sha256": module._sha256(pin_path), "sha256": anchors[name], "byte_size": sizes[name]}
                    old_rows[name] = {"old_file_identity": original, "current_file_identity": latest, "old_private_record_sha256": module._sha256(pin_path),
                        "current_sha256": anchors[name], "frozen_sha256": anchors[name], "byte_size": sizes[name], "changed_fields": ["device"],
                        "whole_file_read": True, "content_hash_matches_frozen": True, "stat_identity_stable_during_hash": True}
                    write_immutable_record(old_root / (name + ".rehash.json"), old_rows[name])
                    rows[name] = {**old_rows[name], "old_file_identity": latest, "latest_accepted_environment_identity": latest,
                        "current_file_identity": current, "original_frozen_pin_file_identity": original,
                        "original_private_record_sha256": module._sha256(pin_path), "proposed_binding_accepted": False}
                pin_report = repo / "results/phase1/oulu-archive-byte-pinning-v1.json"
                write_immutable_record(pin_report, {"media_archives": pins})
                old_binding_path = old_root / "environment_binding.json"
                write_immutable_record(old_binding_path, {"archives": old_rows, "archive_pin_report_sha256": module._sha256(pin_report),
                    "old_archive_pins_unchanged": True, "recovery_checkpoint_review_pending": True})
                old_report_path = repo / "results/phase1/oulu-archive-identity-recovery-v1.json"
                write_immutable_record(old_report_path, {"private_environment_binding_sha256": module._sha256(old_binding_path),
                    "archive_pin_report_sha256": module._sha256(pin_report),
                    "archive_results": {name: {"rehash_record_sha256": module._sha256(old_root / (name + ".rehash.json"))} for name in anchors}})
                review178 = repo / "docs/178-review-doc177-oulu-archive-identity-recovery.md"
                review178.parent.mkdir()
                review178.write_text("synthetic Review178", encoding="ascii")
                recovery = {"accepted_by_Review178": True, "review178_sha256": module._sha256(review178),
                    "binding_path": str(old_binding_path), "binding_sha256": module._sha256(old_binding_path),
                    "accepted177_report_sha256": module._sha256(old_report_path), "archive_pin_report_sha256": module._sha256(pin_report)}
                marker = root / "protected/prior.json"
                write_immutable_record(marker, {"preserve": True})
                lineage = {"review218_sha256": "1" * 64, "accepted217_document_sha256": "2" * 64,
                    "accepted217_report_sha256": "3" * 64, "accepted217_blocker_sha256": "4" * 64, "source217_CI": {"synthetic": True}}
                prior_path = root / "preflight219.json"
                write_immutable_record(prior_path, {**lineage, "accepted_recovery": recovery,
                    "latest_accepted_archive_identity": {name: row["current_file_identity"] for name, row in old_rows.items()},
                    "observed_archive_identity": {name: row["current_file_identity"] for name, row in rows.items()},
                    "protected_snapshots": {str(marker.parent): {marker.name: module._sha256(marker)}},
                    "pinned_file_sha256": {}, "frozen_file_sha256": {}, "study_config_sha256": {}})
                for name, row in rows.items():
                    row.update({"latest_accepted_binding_sha256": module._sha256(old_binding_path),
                        "preflight_sha256": module._sha256(prior_path), "review218_sha256": lineage["review218_sha256"]})
                    write_immutable_record(recovered / (name + ".rehash.json"), row)
                code = repo / "scripts/recover_oulu_archive_identity_batch09.py"
                code.parent.mkdir()
                code.write_text("synthetic recovery219 runner", encoding="ascii")
                binding_path = recovered / "environment_binding.json"
                write_immutable_record(binding_path, {**lineage, "checkpoint": 219, "archives": rows, "latest_accepted_recovery": recovery,
                    "preflight_sha256": module._sha256(prior_path), "recovery_code_sha256": module._sha256(code),
                    "archive_pin_report_sha256": module._sha256(pin_report), "recovery_checkpoint_review_pending": True,
                    "proposed_binding_accepted": False, "packet_runner_guard_changed": False, "packet_preparation_authorized_by_this_record": False,
                    "archive_identity_blocker_closed": False, "original_pins_and_accepted177_records_unchanged": True})
                verification_path = root / "verification219.json"
                write_immutable_record(verification_path, {"recovery_file_sha256": {path.name: module._sha256(path) for path in recovered.iterdir()}})
                report_path = repo / "results/phase1/oulu-archive-identity-recovery219-v1.json"
                report = {**lineage, "private_binding_sha256": module._sha256(binding_path), "private_preflight_sha256": module._sha256(prior_path),
                    "private_verification_sha256": module._sha256(verification_path), "recovery_code_sha256": module._sha256(code),
                    "latest_accepted_binding_sha256": module._sha256(old_binding_path),
                    **{key: recovery[key] for key in ("archive_pin_report_sha256", "review178_sha256", "accepted177_report_sha256")},
                    "archive_results": {name: {"rehash_record_sha256": module._sha256(recovered / (name + ".rehash.json"))} for name in anchors}}
                write_immutable_record(report_path, report)
                authority = {}
                for filename in module.AUTHORITY_BINDINGS:
                    path = repo / filename
                    if not path.exists():
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text("synthetic221 authority", encoding="ascii")
                    authority[filename] = module._sha256(path)
                preflight = {"checkpoint": 221, "accepted_by_Review220": True, "guard_integration_authorized": True,
                    "packet_retry_authorized": False, "packet_preparation_authorized": False, "recovery_authorized": False,
                    "authority_sha256": authority, "source219_CI": module.SOURCE219_CI.copy(), "guard_code_sha256": module._sha256(Path(module.__file__)),
                    "accepted219_binding_path": str(binding_path), "accepted219_preflight_path": str(prior_path),
                    "accepted219_verification_path": str(verification_path), "protected_snapshots": {
                        str(marker.parent): {marker.name: module._sha256(marker)},
                        str(recovered): {path.name: module._sha256(path) for path in recovered.iterdir()}},
                    "pinned_file_sha256": {}, "frozen_file_sha256": {}, "study_config_sha256": {}}
                preflight_path = root / "preflight221.json"
                write_immutable_record(preflight_path, preflight)
                args = Namespace(input_root=source, archive_records=pins_root, preflight=preflight_path, out_root=root / "guard-output")
                before = json.dumps(preflight, sort_keys=True)
                with ExitStack() as stack:
                    for target, key, value in ((module, "ROOT", repo), (module, "ANCHORS", anchors), (module, "ARCHIVE_SIZES", sizes),
                                               (module, "AUTHORITY_BINDINGS", authority), (historical, "ROOT", repo), (historical, "ANCHORS", anchors)):
                        stack.enter_context(patch.object(target, key, value))
                    real_open = Path.open
                    def no_archive_reads(path, *arguments, **keywords):
                        if path.parent == source:
                            raise AssertionError("no archive or payload bytes may be opened")
                        return real_open(path, *arguments, **keywords)
                    stack.enter_context(patch.object(Path, "open", no_archive_reads))
                    self.assertEqual(len(module.verified_archive_identities(source, pins_root, preflight)), 3)
                    self.assertFalse(args.out_root.exists())
                    result = module.verify(args)
                    self.assertEqual(result["archives_verified"], 3)
                    self.assertTrue(result["guard_integration_checkpoint_review_pending"])
                    for key in ("guard_integration_accepted", "packet_preparation_authorized", "packet_retry_authorized", "selected_payloads_opened", "scientific_readiness"):
                        self.assertFalse(result[key])
                    self.assertEqual(len(list(args.out_root.iterdir())), 1)
                    with self.assertRaisesRegex(ValueError, "archive identity drift"):
                        historical.verified_archive_identities(source, pins_root, recovery)
                    original_identity = module.file_identity
                    stale = lambda value: {**original_identity(value), "device": original_identity(value)["device"] + 1}
                    for changed_identity in [stale, *[lambda value, field=field: {**original_identity(value), field: original_identity(value)[field] + 2} for field in module.IDENTITY_FIELDS]]:
                        with patch.object(module, "file_identity", side_effect=changed_identity):
                            with self.assertRaisesRegex(ValueError, "archive identity drift"):
                                module.verified_archive_identities(source, pins_root, preflight)
                    invalid = [{**preflight, key: value} for key, value in (("checkpoint", 221.0), ("accepted_by_Review220", False),
                        ("guard_integration_authorized", False), ("packet_retry_authorized", True), ("packet_preparation_authorized", True),
                        ("recovery_authorized", True), ("authority_sha256", {}), ("guard_code_sha256", "0" * 64))]
                    for key, value in (("head_sha", "0" * 40), ("run_id", 39354730481), ("run_id", float(module.SOURCE219_CI["run_id"])),
                        ("job_id", 118406801611), ("status", "in_progress"), ("conclusion", "failure"), ("job_status", "queued"),
                        ("job_conclusion", "failure"), ("listed_successful_steps", 11), ("all_steps_success", False)):
                        invalid.append({**preflight, "source219_CI": {**preflight["source219_CI"], key: value}})
                    invalid.extend([{**preflight, "protected_snapshots": {}},
                        {**preflight, "protected_snapshots": {str(recovered): preflight["protected_snapshots"][str(recovered)]}}])
                    for index, bad in enumerate(invalid):
                        bad_path = root / f"invalid221-{index}.json"
                        write_immutable_record(bad_path, bad)
                        rejected = Namespace(**{**vars(args), "preflight": bad_path, "out_root": root / "never-created"})
                        with self.assertRaises(ValueError):
                            module.verify(rejected)
                        self.assertFalse(rejected.out_root.exists())
                    for output in (args.out_root, ROOT / "results/refused221", source / "refused", root):
                        with self.assertRaises(ValueError):
                            module.verify(Namespace(**{**vars(args), "out_root": output}))
                    accepted = module.verified_archive_identities(source, pins_root, preflight)
                    changed = {**accepted, "Dev_files.tar": (0, *accepted["Dev_files.tar"][1:])}
                    with patch.object(module, "verified_archive_identities", side_effect=[accepted, changed]):
                        with self.assertRaisesRegex(ValueError, "changed during guard"):
                            module.verify(Namespace(**{**vars(args), "out_root": root / "never-created"}))
                    self.assertFalse((root / "never-created").exists())
                    for path in (binding_path, recovered / "Dev_files.tar.rehash.json", pin_report, review178, prior_path, verification_path):
                        payload = path.read_bytes()
                        path.write_bytes(b"synthetic changed evidence")
                        with self.assertRaises(ValueError):
                            module.verified_archive_identities(source, pins_root, preflight)
                        path.write_bytes(payload)
                    archive = source / "Dev_files.tar"
                    alias = source / "archive-alias"
                    archive.rename(alias)
                    archive.symlink_to(alias)
                    with self.assertRaisesRegex(ValueError, "archive identity drift"):
                        module.verified_archive_identities(source, pins_root, preflight)
                    archive.unlink()
                    alias.rename(archive)
                    marker.write_bytes(b"changed protected evidence")
                    with self.assertRaisesRegex(ValueError, "protected prior evidence drift"):
                        module.verify(Namespace(**{**vars(args), "out_root": root / "never-created"}))
                    self.assertFalse((root / "never-created").exists())
                self.assertEqual(json.dumps(preflight, sort_keys=True), before)
        finally:
            sys.path.pop(0)

    def test_batch09_retry223_binds_review222_guard_context_and_test_transition(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import ast
            import copy
            import prepare_oulu_visual_batch09_retry223 as module
            from argparse import Namespace
            from contextlib import ExitStack
            from fas.freeze import write_immutable_record
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repo = root / "repo"
                for filename in module.AUTHORITY_BINDINGS:
                    path = repo / filename
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("synthetic authority " + filename, encoding="ascii")
                test_path = repo / "tests/test_oulu.py"
                test_path.parent.mkdir()
                baseline = "class SyntheticTests:\n    def test_existing(self):\n        pass\n"
                test_path.write_text(baseline + f"    def {module.NEW_TEST_METHOD}(self):\n        pass\n", encoding="ascii")
                old_test_sha = hashlib.sha256(baseline.encode()).hexdigest()
                old = {"checkpoint": 221, "packet_preparation_authorized": False, "packet_retry_authorized": False,
                    "guard_integration_authorized": True, "guard_code_sha256": module._sha256(repo / "scripts/verify_oulu_archive_guard_batch09.py"),
                    "protected_snapshots": {str(root / "protected"): {"prior.json": "1" * 64}},
                    "pinned_file_sha256": {str(test_path): old_test_sha}, "frozen_file_sha256": {}, "study_config_sha256": {}}
                old_path = root / "accepted/preflight221.json"
                result_path = root / "accepted/guard/guard_validation.json"
                verification_path = root / "accepted/verification221.json"
                write_immutable_record(old_path, old)
                write_immutable_record(result_path, {"guard_integration_checkpoint_review_pending": True,
                    "packet_preparation_authorized": False, "packet_retry_authorized": False, "archives_verified": 3})
                write_immutable_record(verification_path, {"synthetic": True})
                report = {"guard_code_sha256": old["guard_code_sha256"], "test_file_sha256": old_test_sha,
                    "private_preflight_sha256": module._sha256(old_path), "private_guard_result_sha256": module._sha256(result_path),
                    "private_verification_sha256": module._sha256(verification_path)}
                report_path = repo / "results/phase1/oulu-recovery219-aware-guard-v1.json"
                report_path.unlink()
                write_immutable_record(report_path, report)
                authority = {filename: module._sha256(repo / filename) for filename in module.AUTHORITY_BINDINGS}
                context = copy.deepcopy(old)
                context["pinned_file_sha256"][str(test_path)] = module._sha256(test_path)
                context["protected_snapshots"][str(result_path.parent)] = {"guard_validation.json": module._sha256(result_path)}
                preflight = {"checkpoint": 223, "accepted_by_Review222": True, "packet_preparation_authorized": True,
                    "packet_retry_authorized": True, "visual_review_authorized": False, "queue_ranks": list(range(80, 85)),
                    "authority_sha256": authority, "source221_CI": module.SOURCE221_CI.copy(), "guard_context": context,
                    "test_pin_transition": {"old_sha256": old_test_sha, "new_sha256": module._sha256(test_path),
                        "only_added_method": module.NEW_TEST_METHOD, "all_prior_test_ASTs_unchanged": True},
                    "accepted221_preflight_path": str(old_path), "accepted221_result_path": str(result_path),
                    "accepted221_verification_path": str(verification_path), "accepted_prior_report_sha256": module.ACCEPTED215_REPORT_SHA256,
                    "accepted_prior_document_sha256": module.ACCEPTED215_DOCUMENT_SHA256,
                    "acceptance": {"review216_sha256": module.REVIEW216_SHA256},
                    "preparation_code_sha256": module._sha256(Path(module.__file__)),
                    **{field: context[field] for field in ("protected_snapshots", "pinned_file_sha256", "frozen_file_sha256", "study_config_sha256")}}
                before = json.dumps(preflight, sort_keys=True)
                with ExitStack() as stack:
                    for key, value in (("ROOT", repo), ("AUTHORITY_BINDINGS", authority), ("OLD_TEST_SHA256", old_test_sha),
                                       ("OLD_TEST_AST_SHA256", hashlib.sha256(ast.dump(ast.parse(baseline)).encode()).hexdigest())):
                        stack.enter_context(patch.object(module, key, value))
                    stack.enter_context(patch.object(module.tarfile, "open", side_effect=AssertionError("no payload access before accepted guard")))
                    self.assertEqual(module.verified_retry_authority(preflight), context)
                    invalid = [{**preflight, key: value} for key, value in (("checkpoint", 223.0), ("accepted_by_Review222", False),
                        ("packet_preparation_authorized", False), ("packet_retry_authorized", False), ("visual_review_authorized", True),
                        ("queue_ranks", list(range(80, 90))), ("queue_ranks", [80.0, 81, 82, 83, 84]),
                        ("authority_sha256", {}), ("accepted_prior_report_sha256", "0" * 64))]
                    for key, value in (("head_sha", "0" * 40), ("run_id", 39359791576), ("run_id", float(module.SOURCE221_CI["run_id"])),
                                       ("job_id", 118423022731), ("status", "queued"), ("conclusion", "failure"),
                                       ("job_status", "in_progress"), ("job_conclusion", "failure"), ("listed_successful_steps", 11), ("all_steps_success", False)):
                        invalid.append({**preflight, "source221_CI": {**preflight["source221_CI"], key: value}})
                    for field, value in (("packet_preparation_authorized", True), ("packet_retry_authorized", True),
                                         ("protected_snapshots", {}), ("pinned_file_sha256", {})):
                        invalid.append({**preflight, "guard_context": {**context, field: value}})
                    invalid.append({**preflight, "test_pin_transition": {**preflight["test_pin_transition"], "new_sha256": "0" * 64}})
                    for bad in invalid:
                        with self.assertRaises(ValueError):
                            module.verified_retry_authority(bad)
                    path = root / "preflight223.json"
                    write_immutable_record(path, preflight)
                    args = Namespace(**{name: root / name for name in ("input_root", "audit_root", "exact_root", "screen_root", "frozen_root", "archive_records", "activation_root")},
                                     preflight=path, out_root=root / "never-created")
                    with patch.object(module, "verified_archive_identities", side_effect=ValueError("synthetic accepted219 identity drift")) as guard:
                        with self.assertRaisesRegex(ValueError, "identity drift"):
                            module.prepare(args)
                        guard.assert_called_once_with(args.input_root, args.archive_records, context)
                    self.assertFalse(args.out_root.exists())
                    test_path.write_text(test_path.read_text().replace("def test_existing(self):", "def changed_existing(self):"), encoding="ascii")
                    changed = {**preflight, "test_pin_transition": {**preflight["test_pin_transition"], "new_sha256": module._sha256(test_path)}}
                    with self.assertRaisesRegex(ValueError, "prior test AST drift"):
                        module.verified_retry_authority(changed)
                self.assertEqual(json.dumps(preflight, sort_keys=True), before)
        finally:
            sys.path.pop(0)

    def test_archive_identity_recovery_requires_full_hash_and_stable_device_only_drift(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import recover_oulu_archive_identity as module
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                path = root / "synthetic.tar"
                payload = b"synthetic archive container, not a decoded video"
                path.write_bytes(payload)
                old = {**module.file_identity(path.stat()), "device": path.stat().st_dev + 1}
                expected = {"sha256": hashlib.sha256(payload).hexdigest(), "byte_size": len(payload)}
                before = json.dumps([expected, old], sort_keys=True)
                row = module.rehash_archive(path, expected, old)
                self.assertEqual(row["current_sha256"], expected["sha256"])
                self.assertEqual(row["changed_fields"], ["device"])
                self.assertTrue(row["whole_file_read"] and row["stat_identity_stable_during_hash"])
                self.assertEqual(json.dumps([expected, old], sort_keys=True), before)
                for wrong in ({**expected, "sha256": "0" * 64}, {**expected, "byte_size": len(payload) + 1}):
                    with self.assertRaises(ValueError):
                        module.rehash_archive(path, wrong, old)
                for wrong in ({**old, "device": path.stat().st_dev}, {**old, "inode": old["inode"] + 1}):
                    with self.assertRaises(ValueError):
                        module.rehash_archive(path, expected, wrong)
                original = module.hashlib.file_digest

                def mutate(source, algorithm):
                    digest = original(source, algorithm)
                    path.write_bytes(payload + b"changed during read")
                    return digest

                with patch.object(module.hashlib, "file_digest", side_effect=mutate):
                    with self.assertRaisesRegex(ValueError, "changed during hash"):
                        module.rehash_archive(path, expected, old)
                path.write_bytes(payload)
                link = root / "link.tar"
                link.symlink_to(path)
                with self.assertRaises(ValueError):
                    module.rehash_archive(link, expected, old)
                from argparse import Namespace
                for output in (ROOT / "results/refused-recovery", root, root / "source/refused"):
                    with self.assertRaises(ValueError):
                        module.recover(Namespace(input_root=root / "source", archive_records=root / "pins",
                                                 preflight=root / "preflight.json", out_root=output))
                source_root, pin_root, repo = root / "source", root / "pins", root / "repo"
                source_root.mkdir()
                pin_root.mkdir()
                anchors = {name: expected["sha256"] for name in module.ANCHORS}
                pins = {}
                for name, digest in anchors.items():
                    archive = source_root / name
                    archive.write_bytes(payload)
                    record = pin_root / (name + ".sha256.json")
                    module.write_immutable_record(record, {"file_identity": {**module.file_identity(archive.stat()), "device": archive.stat().st_dev + 1}})
                    pins[name] = {"sha256": digest, "byte_size": len(payload), "private_record_sha256": module._sha256(record)}
                report = repo / "results/phase1/oulu-archive-byte-pinning-v1.json"
                review = repo / "docs/176-review-doc175-oulu-batch06-archive-device-blocker.md"
                module.write_immutable_record(report, {"media_archives": pins})
                review.parent.mkdir(parents=True)
                review.write_text("synthetic recovery authority", encoding="ascii")
                preflight = root / "preflight.json"
                module.write_immutable_record(preflight, {
                    "protected_snapshots": {str(pin_root): {item.name: module._sha256(item) for item in pin_root.iterdir()}},
                    "pinned_file_sha256": {}, "frozen_file_sha256": {}, "study_config_sha256": {},
                    "recovery_code_sha256": module._sha256(Path(module.__file__)), "review176_sha256": module._sha256(review),
                    "archive_anchor_sha256": anchors, "archive_pin_report_sha256": module._sha256(report),
                    "source175_CI": {"head_sha": "d54f6723f3852bd1a0ef2d8d1862f1799639a0cb", "run_id": 38669499099,
                                     "job_id": 116209003838, "status": "completed", "conclusion": "success"}})
                with patch.object(module, "ROOT", repo), patch.object(module, "ANCHORS", anchors):
                    output = root / "success"
                    binding = module.recover(Namespace(input_root=source_root, archive_records=pin_root, preflight=preflight, out_root=output))
                    self.assertEqual(len(binding["archives"]), 3)
                    self.assertEqual(binding["total_bytes_hashed"], 3 * len(payload))
                    self.assertTrue(binding["recovery_checkpoint_review_pending"])
                    self.assertFalse(binding["packet_preparation_authorized_by_this_record"])
                    with self.assertRaises(ValueError):
                        module.recover(Namespace(input_root=source_root, archive_records=pin_root, preflight=preflight, out_root=output))
                    (source_root / "Test_files.tar").write_bytes(payload.replace(b"synthetic", b"different"))
                    refused = root / "mismatch"
                    with self.assertRaisesRegex(ValueError, "SHA-256 differs"):
                        module.recover(Namespace(input_root=source_root, archive_records=pin_root, preflight=preflight, out_root=refused))
                    self.assertTrue((refused / "Dev_files.tar.rehash.json").is_file())
                    self.assertFalse((refused / "environment_binding.json").exists())
                    self.assertFalse((refused / "Train_files.tar.rehash.json").exists())
        finally:
            sys.path.pop(0)

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