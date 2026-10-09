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

from fas import siwmv2
from fas.siwmv2 import PREFIX_BY_FOLDER, encode_label, parse_media_path


class SiWMv2MetadataTest(unittest.TestCase):
    def membership(self, prefix: str = "Paper", split: str = "train") -> dict:
        live = prefix == "Live"
        return {"video_id": prefix + "_1", "official_split": split,
                "binary_label": "bona_fide" if live else "attack",
                "reference_attack_type": None if live else prefix,
                "attack_family": None if live else inspection.SIWMV2_ATTACK_FAMILIES[prefix],
                "subject_id": None, "group_unit": "video", "group_id": prefix + "_1"}

    def test_all_reference_types_and_live_preserve_labels_and_video_groups(self) -> None:
        for folder, prefix in PREFIX_BY_FOLDER.items():
            for split in ("train", "test"):
                with self.subTest(prefix=prefix, split=split):
                    row = parse_media_path(f"SiW-Mv2/{folder}/{prefix}_1.mov", self.membership(prefix, split))
                    self.assertEqual(encode_label(row["binary_label"]), 0 if prefix == "Live" else 1)
                    self.assertIsNone(row["subject_id"])
                    self.assertEqual(row["group_id"], row["video_id"])
                    self.assertIsNone(row["role"])
                    self.assertEqual(row["source_eligible"], split == "train")
                    self.assertEqual(row["outer_target_eligible"], split == "test")
                    self.assertIn(f"/{split}list_", row["partition_source"])
                    self.assertTrue(all(row[field] == "unknown" for field in ("material", "environment", "sensor_id", "session_id")))

    def test_parser_rejects_unsafe_paths_aliases_and_unknown_types(self) -> None:
        for path in (None, 1, "../SiW-Mv2/Spoof/Paper/Paper_1.mov", "/SiW-Mv2/Spoof/Paper/Paper_1.mov",
                     "SiW-Mv2//Spoof/Paper/Paper_1.mov", "SiW-Mv2/Spoof/./Paper/Paper_1.mov",
                     "SiW-Mv2\\Spoof\\Paper\\Paper_1.mov", "SiW-Mv2/Spoof/Other/Other_1.mov",
                     "SiW-Mv2/Spoof/Paper/Paper_01.mov", "SiW-Mv2/Spoof/Paper/Paper_0.mov",
                     "SiW-Mv2/Spoof/Paper/Replay_1.mov", "SiW-Mv2/Spoof/Paper/Paper_1.MOV",
                     "SiW-Mv2/Spoof/Paper/nested/Paper_1.mov", "SiW-Mv2/Spoof/Paper/Paper_1.png"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                parse_media_path(path, self.membership())

    def test_parser_rejects_membership_drift_and_fabricated_subjects(self) -> None:
        for change in ({"subject_id": "Paper_1"}, {"subject_id": "unknown"}, {"group_unit": "subject"},
                       {"video_id": "Paper_2"}, {"group_id": "other"}, {"official_split": "dev"},
                       {"binary_label": "bona_fide"}, {"attack_family": "mask"}, {"reference_attack_type": "Replay"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                parse_media_path("SiW-Mv2/Spoof/Paper/Paper_1.mov", {**self.membership(), **change})
        with self.assertRaises(ValueError):
            encode_label("unknown")

    def test_mapping_hash_and_prediction_error_polarity_are_explicit(self) -> None:
        digest = hashlib.sha256(json.dumps(siwmv2.LABEL_MAPPING, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(digest, siwmv2.LABEL_MAPPING_HASH)
        self.assertEqual(siwmv2.LABEL_MAPPING["model_boundary"], {"bona_fide": 0, "attack": 1})
        self.assertFalse(siwmv2.LABEL_MAPPING["provider_family_ontology_claimed"])
        for label in ("bona_fide", "attack"):
            for score in (0.1, 0.9):
                truth = encode_label(label)
                prediction = int(score >= 0.5)
                self.assertEqual(int(prediction != truth), 0 if prediction == truth else 1)


class SiWMv2InventoryTest(unittest.TestCase):
    def fixture(self):
        source = SiWMv2PrerequisitesTest()
        sources = source.sources()
        sources["pro_3_text/trainlist_live.txt"] += b"Live_3\n"
        sources["pro_3_text/testlist_all.txt"] = b"Replay_2\n"
        entries = source.entries()
        record = inspection.build_intersection_record(entries, sources)
        headers = [{"path": entry.filename, "size": entry.file_size, "crc32": entry.CRC,
                    "compressed_size": entry.compress_size, "flags": entry.flag_bits,
                    "external_attr": entry.external_attr} for entry in entries]
        return headers, record

    def inventory(self, headers=None, record=None, **options):
        fixture_headers, fixture_record = self.fixture()
        record = fixture_record if record is None else record
        payload = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
        with patch.object(siwmv2, "MEMBERSHIP_SHA256", hashlib.sha256(payload).hexdigest()), patch.dict(siwmv2.SOURCE_SHA256, record["reference_sha256"], clear=True):
            return siwmv2.inventory_headers(fixture_headers if headers is None else headers,
                                           population_payload=payload, release_id="synthetic-release",
                                           archive_name="synthetic.zip", **options)

    def test_inventory_keeps_exclusions_missing_references_and_unverified_media_separate(self) -> None:
        result = self.inventory()
        self.assertEqual(len(result["videos"]), 3)
        self.assertEqual(result["out_of_protocol_videos"][0]["video_id"], "Replay_1")
        self.assertIsNone(result["out_of_protocol_videos"][0]["official_split"])
        self.assertEqual(len(result["missing_references"]), 2)
        for key in ("acquisition_verified", "archive_sha256_verified", "media_integrity_verified", "media_decode_verified",
                    "participant_identity_verified", "scientific_readiness", "roles_assigned"):
            self.assertFalse(result[key])
        for row in result["videos"]:
            self.assertIsNone(row["subject_id"])
            self.assertIsNone(row["media_sha256"])
            self.assertIsNone(row["frame_count"])
            self.assertEqual(row["decode_status"], "not_probed")
        headers, record = self.fixture()
        self.assertEqual(result, self.inventory(list(reversed(headers)), record))

    def test_inventory_rejects_missing_duplicate_and_replaced_identifiers(self) -> None:
        headers, record = self.fixture()
        for changed in (headers[1:], [*headers, headers[0]], [{**headers[0], "path": "SiW-Mv2/Live/Live_999.mov"}, *headers[1:]]):
            with self.subTest(size=len(changed)), self.assertRaises(ValueError):
                self.inventory(changed, record)

    def test_inventory_checks_full_header_digest_not_just_membership_counts(self) -> None:
        headers, record = self.fixture()
        for field in ("size", "crc32", "compressed_size", "flags", "external_attr"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.inventory([{**headers[0], field: headers[0][field] + 2}, *headers[1:]], record)

    def test_inventory_rejects_unsafe_encrypted_link_empty_and_untyped_headers(self) -> None:
        headers, record = self.fixture()
        for change in ({"path": "../outside.mov"}, {"path": "SiW-Mv2//Live/Live_1.mov"}, {"flags": 1},
                       {"external_attr": (stat.S_IFLNK | 0o777) << 16}, {"size": 0}, {"size": True},
                       {"external_attr": (stat.S_IFDIR | 0o755) << 16},
                       {"crc32": -1}, {"crc32": 0x100000000}, {"extra": "unknown"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.inventory([{**headers[0], **change}, *headers[1:]], record)

    def test_population_requires_accepted_bytes_even_when_json_is_equivalent(self) -> None:
        headers, record = self.fixture()
        payload = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
        with patch.object(siwmv2, "MEMBERSHIP_SHA256", hashlib.sha256(payload).hexdigest()):
            with self.assertRaisesRegex(ValueError, "frozen bytes"):
                siwmv2.load_population(payload + b"\n")

    def test_population_rejects_changed_authority_and_identity_even_if_test_hash_is_repinned(self) -> None:
        headers, record = self.fixture()
        for change in ({"reference_commit": "a" * 40}, {"population_id": "another"},
                       {"attack_family_mapping": {}}, {"version": True}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.inventory(headers, {**record, **change})
        mutated = json.loads(json.dumps(record))
        mutated["eligible_videos"][0]["subject_id"] = "invented"
        with self.assertRaises(ValueError):
            self.inventory(headers, mutated)


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


class SiWMv2InventoryCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.input = self.home / "inputs"
        self.input.mkdir()
        self.archive = self.input / "dataset.zip"
        self.sources = SiWMv2PrerequisitesTest().sources()
        self.reference = self.home / "reference"
        for relative, payload in self.sources.items():
            path = self.reference / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        with zipfile.ZipFile(self.archive, "w") as archive:
            for entry in SiWMv2PrerequisitesTest().entries():
                archive.writestr(entry.filename, b"synthetic payload")
        with zipfile.ZipFile(self.archive) as archive:
            record = inspection.build_intersection_record(archive.infolist(), self.sources)
        self.population = self.home / "membership.json"
        self.population.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self.output = self.home / "inventory.json"
        self.population_pin = hashlib.sha256(self.population.read_bytes()).hexdigest()
        self.source_pins = {name: hashlib.sha256(payload).hexdigest() for name, payload in self.sources.items()}
        spec = importlib.util.spec_from_file_location("siwmv2_inventory_cli", ROOT / "scripts/inventory_siwmv2.py")
        self.cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.cli)

    def command(self, *extra) -> tuple[int, str, str]:
        args = ["inventory_siwmv2", "--archive", str(self.archive), "--reference-root", str(self.reference),
                "--population", str(self.population), "--release-id", "synthetic-private-release",
                "--unverified-local", "--out", str(self.output), *extra]
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(sys, "argv", args), patch.object(siwmv2, "MEMBERSHIP_SHA256", self.population_pin), \
             patch.dict(siwmv2.SOURCE_SHA256, self.source_pins, clear=True), \
             patch.object(zipfile.ZipFile, "open", side_effect=AssertionError("media payload must not be opened")), \
             redirect_stdout(stdout), redirect_stderr(stderr):
            status = self.cli.main()
        return status, stdout.getvalue(), stderr.getvalue()

    def test_cli_private_immutable_output_redacted_summary_and_no_payload_access(self) -> None:
        status, stdout, stderr = self.command()
        self.assertEqual(status, 0, stderr)
        report = json.loads(stdout)
        self.assertEqual(report["eligible_videos"], 4)
        self.assertEqual(report["inventory_sha256"], hashlib.sha256(self.output.read_bytes()).hexdigest())
        self.assertFalse(report["scientific_readiness"])
        self.assertFalse(report["roles_assigned"])
        for private in (str(self.home), "synthetic-private-release", "Live_1", "Paper_1"):
            self.assertNotIn(private, stdout + stderr)
        original = self.output.read_bytes()
        self.assertEqual(self.command()[0], 2)
        self.assertEqual(original, self.output.read_bytes())

    def test_cli_rejects_changed_actual_population_and_source_bytes(self) -> None:
        original = self.population.read_bytes()
        self.population.write_bytes(original + b"\n")
        self.assertEqual(self.command()[0], 2)
        self.assertFalse(self.output.exists())
        self.population.write_bytes(original)
        (self.reference / "dataset.py").write_bytes(b"changed private details")
        status, stdout, stderr = self.command()
        self.assertEqual(status, 2)
        self.assertNotIn(str(self.home), stdout + stderr)
        self.assertNotIn("Traceback", stdout + stderr)

    def test_cli_rejects_source_symlinks_and_population_symlinks(self) -> None:
        outside = self.home / "outside.py"
        outside.write_bytes(self.sources["dataset.py"])
        source = self.reference / "dataset.py"
        source.unlink()
        source.symlink_to(outside)
        self.assertEqual(self.command()[0], 2)
        source.unlink()
        source.write_bytes(self.sources["dataset.py"])
        alias = self.home / "membership-alias.json"
        alias.symlink_to(self.population)
        self.assertEqual(self.command("--population", str(alias))[0], 2)

    def test_cli_rejects_corrupt_archive_and_changed_header_inventory(self) -> None:
        self.archive.write_bytes(b"not a zip: private details")
        self.assertEqual(self.command()[0], 1)
        self.assertFalse(self.output.exists())
        with zipfile.ZipFile(self.archive, "w") as archive:
            for entry in SiWMv2PrerequisitesTest().entries():
                archive.writestr(entry.filename, b"different bytes")
        self.assertEqual(self.command()[0], 1)
        self.assertFalse(self.output.exists())

    def test_cli_rejects_repository_input_output_and_input_collisions(self) -> None:
        for output in (ROOT / "manifests/private/forbidden.json", self.archive, self.population, self.reference / "new.json"):
            with self.subTest(output=output):
                self.assertEqual(self.command("--out", str(output))[0], 2)
        self.assertEqual(self.command("--archive", str(ROOT / "README.md"))[0], 2)

    def test_cli_rejects_symlink_loops_and_dangling_output_links_without_private_traceback(self) -> None:
        alias = self.home / "loop"
        alias.symlink_to(alias)
        status, stdout, stderr = self.command("--out", str(alias))
        self.assertEqual(status, 2)
        self.assertNotIn(str(self.home), stdout + stderr)
        self.assertNotIn("Traceback", stdout + stderr)
        dangling = self.home / "dangling"
        target = self.home / "not-created.json"
        dangling.symlink_to(target)
        self.assertEqual(self.command("--out", str(dangling))[0], 2)
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()