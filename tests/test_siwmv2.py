from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import stat
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("inspect_siwmv2", ROOT / "scripts" / "inspect_siwmv2.py")
assert SPEC is not None and SPEC.loader is not None
inspection = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inspection)


class SiWMv2PrerequisitesTest(unittest.TestCase):
    def sources(self) -> dict[str, bytes]:
        return {"README.md": b"synthetic", "dataset.py": b"synthetic",
                "pro_3_text/trainlist_live.txt": b"Live_1\n",
                "pro_3_text/testlist_live.txt": b"Live_2\n",
                "pro_3_text/trainlist_all.txt": b"Paper_1\nPaper_1\n",
                "pro_3_text/testlist_all.txt": b"Replay_1\n"}

    def entries(self) -> list[zipfile.ZipInfo]:
        names = ["SiW-Mv2/Live/Live_1.mov", "SiW-Mv2/Live/Live_2.mp4",
                 "SiW-Mv2/Spoof/Paper/Paper_1.avi", "SiW-Mv2/Spoof/Replay/Replay_1.mov",
                 "SiW-Mv2/README.pdf", "SiW-Mv2/DRA.pdf"]
        entries = [zipfile.ZipInfo(name) for name in names]
        for entry in entries:
            entry.file_size = 100
            entry.CRC = 0
        return entries

    def test_exact_video_reconciliation_never_claims_subject_or_acquisition_readiness(self) -> None:
        report = inspection.inspect_headers(self.entries(), self.sources())
        self.assertTrue(report["protocol_i_exact_match"])
        self.assertEqual(report["status"], "blocked")
        for key in ("subject_identity_verified", "acquisition_verified", "archive_sha256_verified",
                    "media_integrity_verified", "media_decode_verified", "scientific_readiness", "core_replacement_activated"):
            self.assertFalse(report[key])
        self.assertTrue(report["no_media_payload_read"])
        self.assertNotIn("Live_1", json.dumps(report))
        self.assertEqual(report["protocol_i_lists"]["pro_3_text/trainlist_all.txt"]["balancing_repeat_rows"], 1)

    def test_missing_unlisted_and_cross_split_tokens_are_reported_not_silently_fixed(self) -> None:
        sources = self.sources()
        sources["pro_3_text/trainlist_live.txt"] = b"Live_1\nLive_3\n"
        sources["pro_3_text/testlist_live.txt"] = b"Live_1\n"
        report = inspection.inspect_headers(self.entries(), sources)
        self.assertEqual(report["protocol_i_reconciliation"]["live"], {
            "train_test_video_token_overlap": 1, "observed_unlisted": 1,
            "listed_unobserved": 1, "observed_train": 1, "observed_test": 1})
        self.assertFalse(report["protocol_i_exact_match"])

    def test_inventory_is_deterministic_under_archive_order(self) -> None:
        self.assertEqual(inspection.inspect_headers(self.entries(), self.sources()),
                         inspection.inspect_headers(list(reversed(self.entries())), self.sources()))

    def test_intersection_deduplicates_and_preserves_unknown_subjects_and_taxonomy(self) -> None:
        record = inspection.build_intersection_record(self.entries(), self.sources())
        self.assertEqual(len(record["eligible_videos"]), 4)
        self.assertTrue(all(row["subject_id"] is None and row["group_id"] == row["video_id"]
                            for row in record["eligible_videos"]))
        paper = next(row for row in record["eligible_videos"] if row["video_id"] == "Paper_1")
        self.assertEqual((paper["reference_attack_type"], paper["attack_family"]), ("Paper", "print"))
        summary = inspection.intersection_summary(record)
        self.assertEqual(summary["partitions"]["train"]["attack"], 1)
        self.assertFalse(summary["all_14_types_in_each_partition"])
        self.assertNotIn("Paper_1", json.dumps(summary))
        self.assertEqual(summary["private_membership_sha256"], hashlib.sha256(
            (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()).hexdigest())
        self.assertEqual(record, inspection.build_intersection_record(list(reversed(self.entries())), self.sources()))

    def test_intersection_freezes_explicit_exclusions_and_missing_references(self) -> None:
        sources = self.sources()
        sources["pro_3_text/trainlist_live.txt"] = b"Live_1\nLive_3\n"
        sources["pro_3_text/testlist_all.txt"] = b"Replay_2\n"
        record = inspection.build_intersection_record(self.entries(), sources)
        self.assertEqual(record["excluded_videos"], [{"video_id": "Replay_1", "reason": "out_of_protocol", "reference_attack_type": "Replay"}])
        self.assertEqual({row["video_id"] for row in record["missing_references"]}, {"Live_3", "Replay_2"})
        sources["pro_3_text/testlist_live.txt"] = b"Live_1\n"
        with self.assertRaises(ValueError):
            inspection.build_intersection_record(self.entries(), sources)

    def test_unsafe_unknown_and_empty_members_fail_closed(self) -> None:
        for name in ("../outside.mov", "/SiW-Mv2/Live/Live_1.mov", "SiW-Mv2//Live/Live_1.mov",
                     "SiW-Mv2/./Live/Live_1.mov", "SiW-Mv2\\Live\\Live_1.mov",
                     "SiW-Mv2/Spoof/Other/Other_1.mov", "SiW-Mv2/Live/Paper_1.mov",
                     "SiW-Mv2/Live/Live_01.mov", "SiW-Mv2/Live/Live_0.mov",
                     "SiW-Mv2/Live/Live_3.MOV", "SiW-Mv2/Live/Live_3.png"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                entry = zipfile.ZipInfo(name)
                entry.file_size = 10
                inspection.inspect_headers([entry, *self.entries()], self.sources())
        entries = self.entries()
        entries[0].file_size = 0
        with self.assertRaises(ValueError):
            inspection.inspect_headers(entries, self.sources())

    def test_links_encryption_duplicate_paths_and_video_tokens_fail_closed(self) -> None:
        for mutation in ("encrypted", "symlink", "duplicate-path", "duplicate-token"):
            entries = self.entries()
            if mutation == "encrypted":
                entries[0].flag_bits = 1
            elif mutation == "symlink":
                entries[0].external_attr = (stat.S_IFLNK | 0o777) << 16
            elif mutation == "duplicate-path":
                entries.append(entries[0])
            else:
                entry = zipfile.ZipInfo("SiW-Mv2/Live/Live_1.avi")
                entry.file_size = 10
                entries.append(entry)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                inspection.inspect_headers(entries, self.sources())

    def test_invalid_wrong_class_and_empty_partition_tokens_fail_closed(self) -> None:
        for payload in (b"", b"Live_01\n", b"../Live_1\n", b"Paper_1\n", b"Live_1 \n", b"\xff"):
            sources = self.sources()
            sources["pro_3_text/trainlist_live.txt"] = payload
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                inspection.inspect_headers(self.entries(), sources)

    def test_actual_source_bytes_are_verified_and_symlink_escape_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "reference"
            sources = self.sources()
            for name, payload in sources.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
            pins = {name: hashlib.sha256(payload).hexdigest() for name, payload in sources.items()}
            with patch.dict(inspection.SOURCE_SHA256, pins, clear=True):
                self.assertEqual(inspection.load_sources(root), sources)
                (root / "README.md").write_bytes(b"changed")
                with self.assertRaises(ValueError):
                    inspection.load_sources(root)
                (root / "README.md").unlink()
                outside = Path(temporary) / "outside"
                outside.write_bytes(b"synthetic")
                (root / "README.md").symlink_to(outside)
                with self.assertRaises(ValueError):
                    inspection.load_sources(root)

    def test_cli_reads_only_headers_publishes_blocked_report_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive_path = root / "inputs" / "dataset.zip"
            archive_path.parent.mkdir()
            with zipfile.ZipFile(archive_path, "w") as archive:
                for entry in self.entries():
                    archive.writestr(entry.filename, b"synthetic payload")
            output = root / "reports" / "report.json"
            args = ["inspect_siwmv2", "--archive", str(archive_path), "--reference-root", str(root / "reference"), "--out", str(output)]
            with patch.object(sys, "argv", args), patch.object(inspection, "load_sources", return_value=self.sources()), patch.object(zipfile.ZipFile, "open", side_effect=AssertionError("payload must not be read")), redirect_stdout(io.StringIO()):
                self.assertEqual(inspection.main(), 1)
            original = output.read_bytes()
            self.assertFalse(json.loads(original)["scientific_readiness"])
            with patch.object(sys, "argv", args), redirect_stderr(io.StringIO()):
                self.assertEqual(inspection.main(), 2)
            self.assertEqual(output.read_bytes(), original)

    def test_intersection_cli_rejects_private_ids_inside_git(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive_path = Path(temporary) / "dataset.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                for entry in self.entries():
                    archive.writestr(entry.filename, b"synthetic payload")
            output = Path(temporary) / "public" / "report.json"
            args = ["inspect_siwmv2", "--archive", str(archive_path), "--reference-root", str(Path(temporary) / "reference"),
                    "--out", str(output), "--intersection-private-out", str(ROOT / "manifests" / "private" / "forbidden.json")]
            with patch.object(sys, "argv", args), patch.object(inspection, "load_sources", return_value=self.sources()), redirect_stderr(io.StringIO()):
                self.assertEqual(inspection.main(), 2)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()