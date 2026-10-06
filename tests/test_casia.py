from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.casia import BOB_COMMIT, BOB_SOURCE_SHA256, LABEL_MAPPING, LABEL_MAPPING_HASH, REFERENCE_CODES, encode_label, inventory_headers, parse_media_path, verify_bob_sources


class CasiaTest(unittest.TestCase):
    def test_all_twelve_codes_preserve_polarity_quality_and_attack_type(self) -> None:
        expected = {
            "1": (0, "none", "normal"), "2": (0, "none", "low"), "HR_1": (0, "none", "high"),
            "3": (1, "warped", "normal"), "4": (1, "warped", "low"), "HR_2": (1, "warped", "high"),
            "5": (1, "cut", "normal"), "6": (1, "cut", "low"), "HR_3": (1, "cut", "high"),
            "7": (1, "video", "normal"), "8": (1, "video", "low"), "HR_4": (1, "video", "high"),
        }
        for token, (encoded, subtype, quality) in expected.items():
            with self.subTest(token=token):
                row = parse_media_path(f"train_release/1/{token}.avi")
                self.assertEqual(encode_label(row["binary_label"]), encoded)
                self.assertEqual(row["reference_attack_type"], subtype)
                self.assertEqual(row["quality"], quality)
                self.assertEqual(row["raw_label_token"], token)
                self.assertEqual(row["attack_family"], "none" if not encoded else "replay" if subtype == "video" else "print")
                self.assertEqual(row["metadata_authority"], "bob-reference")
                self.assertTrue(all(row[field] == "unknown" for field in ("material", "session_id", "sensor_id", "environment")))

    def test_subject_namespace_preserves_train_test_and_stable_video_identity(self) -> None:
        train = parse_media_path("train_release/1/1.avi")
        test = parse_media_path("test_release/1/1.avi")
        self.assertEqual((train["subject_id"], test["subject_id"]), ("subject-01", "subject-21"))
        self.assertNotEqual(train["video_id"], test["video_id"])
        self.assertEqual(train["video_id"], "train_release/1/1")
        self.assertEqual(test["raw_subject_token"], "1")
        self.assertEqual(parse_media_path("test_release/30/HR_4.avi")["subject_id"], "subject-50")
        self.assertEqual((train["official_split"], test["official_split"]), ("train", "test"))
        self.assertFalse(LABEL_MAPPING["bob_cross_validation_adopted"])

    def test_unknown_tokens_aliases_and_unsafe_paths_fail_closed(self) -> None:
        for value in (None, 12, "../train_release/1/1.avi", "/train_release/1/1.avi", "train_release//1/1.avi", "train_release/./1/1.avi", "train_release\\1\\1.avi", "train_release/1/9.avi", "train_release/1/HR_5.avi", "train_release/1/hr_1.avi", "train_release/1/01.avi", "train_release/01/1.avi", "train_release/21/1.avi", "test_release/31/1.avi", "train_release/0/1.avi", "dev_release/1/1.avi", "train_release/1/1.AVI", "train_release/1/1.png", "train_release/1/nested/1.avi", "train_release/1/1.avi\x00"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_media_path(value)

    def test_mapping_provenance_hash_and_fixed_score_error_contract(self) -> None:
        digest = hashlib.sha256(json.dumps(LABEL_MAPPING, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(digest, LABEL_MAPPING_HASH)
        self.assertEqual(len(BOB_COMMIT), 40)
        self.assertEqual(len(BOB_SOURCE_SHA256), 2)
        self.assertEqual(parse_media_path("train_release/1/1.avi")["label_mapping_hash"], digest)
        for label in ("bona_fide", "attack"):
            truth = encode_label(label)
            for score in (0.1, 0.9):
                prediction = int(score >= 0.5)
                error = int(prediction != truth)
                self.assertEqual(error, 0 if prediction == truth else 1)
        with self.assertRaises(ValueError):
            encode_label("unknown")


class CasiaInventoryTest(unittest.TestCase):
    def headers(self, full: bool = False) -> list[dict]:
        return [
            {"relpath": f"{partition}/{subject}/{token}.avi", "byte_size": 100,
             "kind": "file", "encrypted": False}
            for partition, identifiers in (("train_release", range(1, 21) if full else (1,)), ("test_release", range(1, 31) if full else (1,)))
            for subject in identifiers for token in REFERENCE_CODES
        ]

    def inventory(self, headers=None, **options) -> dict:
        return inventory_headers(self.headers() if headers is None else headers, release_id="synthetic-release", protocol_id="synthetic-protocol", archive_name="synthetic.rar", **options)

    def test_synthetic_inventory_preserves_reference_labels_and_unknown_media(self) -> None:
        result = self.inventory()
        self.assertEqual(len(result["videos"]), 24)
        self.assertEqual(sum(row["binary_label"] == "bona_fide" for row in result["videos"]), 6)
        self.assertFalse(result["acquisition_verified"])
        self.assertFalse(result["owner_schema_certified"])
        self.assertFalse(result["scientific_readiness"])
        self.assertFalse(result["bob_cross_validation_adopted"])
        for row in result["videos"]:
            self.assertEqual(row["decode_status"], "not_probed")
            self.assertTrue(all(row[field] is None for field in ("media_sha256", "container", "codec", "duration_ms", "fps", "frame_count")))
        self.assertEqual(result, self.inventory(list(reversed(self.headers()))))

    def test_full_reference_compares_identifiers_not_only_counts(self) -> None:
        with self.assertRaisesRegex(ValueError, "full Bob"):
            self.inventory(require_full_reference=True)
        result = self.inventory(self.headers(full=True), require_full_reference=True)
        self.assertEqual(len(result["videos"]), 600)
        self.assertTrue(result["full_reference_universe_checked"])
        headers = self.headers(full=True)
        headers[-1] = dict(headers[0])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.inventory(headers, require_full_reference=True)

    def test_missing_codes_empty_input_and_missing_partition_are_blocked(self) -> None:
        for headers in ([], self.headers()[1:], self.headers()[:12]):
            with self.subTest(size=len(headers)), self.assertRaises(ValueError):
                self.inventory(headers)

    def test_directory_members_are_validated_and_aliases_rejected(self) -> None:
        directory = {"relpath": "train_release/1/", "byte_size": 0, "kind": "directory", "encrypted": False}
        self.assertEqual(len(self.inventory([directory, *self.headers()])["videos"]), 24)
        duplicate = {**directory, "relpath": "train_release/1"}
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.inventory([directory, duplicate, *self.headers()])
        for relative in ("../outside/", "train_release/1/nested/", "test_release/31/", "dev_release/"):
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                self.inventory([{**directory, "relpath": relative}, *self.headers()])

    def test_bad_header_types_links_encryption_and_zero_bytes_are_blocked(self) -> None:
        for change in ({"byte_size": True}, {"byte_size": 1.0}, {"byte_size": -1}, {"byte_size": 0}, {"encrypted": True}, {"encrypted": 0}, {"kind": "symlink"}, {"kind": "hardlink"}, {"relpath": "../outside"}, {"relpath": "train_release/1/README.txt"}, {"extra": "unknown"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.inventory([{**self.headers()[0], **change}, *self.headers()[1:]])
        with self.assertRaises(ValueError):
            inventory_headers(self.headers(), release_id="", protocol_id="synthetic", archive_name="synthetic.rar")
        with self.assertRaises(ValueError):
            inventory_headers(self.headers(), release_id="synthetic", protocol_id="synthetic", archive_name="../archive.rar")
        with self.assertRaises(ValueError):
            self.inventory(require_full_reference=1)

    def test_bob_source_verifier_hashes_actual_bytes_and_rejects_changed_or_escaped_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "sources"
            root.mkdir()
            pins = {}
            for relative in BOB_SOURCE_SHA256:
                path = root / Path(relative).name
                path.write_bytes(b"synthetic source bytes " + path.name.encode())
                pins[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
            with patch.dict(BOB_SOURCE_SHA256, pins, clear=True):
                self.assertEqual(verify_bob_sources(root), pins)
                (root / "models.py").write_bytes(b"changed")
                with self.assertRaisesRegex(ValueError, "pinned bytes"):
                    verify_bob_sources(root)
                (root / "models.py").unlink()
                outside = root.parent / "outside.py"
                outside.write_bytes(b"outside source")
                (root / "models.py").symlink_to(outside)
                with self.assertRaisesRegex(ValueError, "unsafe"):
                    verify_bob_sources(root)


class CasiaCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.input = self.home / "private-input"
        self.input.mkdir()
        self.archive = self.input / "synthetic.rar"
        self.archive.write_bytes(b"synthetic archive placeholder; reader is stubbed")
        self.wheel = self.home / "reader.whl"
        self.wheel.write_bytes(b"synthetic wheel placeholder")
        self.sources = self.home / "sources"
        self.sources.mkdir()
        self.output = self.home / "inventory.json"
        spec = importlib.util.spec_from_file_location("casia_inventory_cli", ROOT / "scripts" / "inventory_casia.py")
        self.cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.cli)
        self.headers = CasiaInventoryTest().headers()
        self.archive_encrypted = False
        self.reader_error = None
        owner = self

        class Archive:
            def __enter__(self):
                if owner.reader_error:
                    raise owner.reader_error
                return self
            def __exit__(self, *args):
                return False
            def needs_password(self):
                return owner.archive_encrypted
            def infolist(self):
                return [SimpleNamespace(
                    filename=header["relpath"], file_size=header["byte_size"],
                    file_redir=header.get("redirect"),
                    is_symlink=lambda value=header: value["kind"] == "link",
                    is_dir=lambda value=header: value["kind"] == "directory",
                    is_file=lambda value=header: value["kind"] == "file",
                    needs_password=lambda value=header: value["encrypted"],
                ) for header in owner.headers]
            @property
            def comment(self):
                raise AssertionError("archive comments must not be read")
            def open(self, *args):
                raise AssertionError("media payload must not be opened")
            def read(self, *args):
                raise AssertionError("media payload must not be read")
            def extract(self, *args):
                raise AssertionError("media payload must not be extracted")
        self.reader = SimpleNamespace(RarFile=lambda path: Archive(), Error=OSError)

    def command(self, *extra: str) -> tuple[int, str, str]:
        arguments = ["inventory_casia.py", "--archive", str(self.archive), "--reader-wheel", str(self.wheel),
                     "--bob-source-root", str(self.sources), "--release-id", "synthetic-private-release",
                     "--protocol-id", "synthetic-private-protocol", "--unverified-local", "--out", str(self.output), *extra]
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(sys, "argv", arguments), patch.object(self.cli, "load_reader", return_value=self.reader), patch.object(self.cli, "verify_bob_sources", return_value=dict(BOB_SOURCE_SHA256)), redirect_stdout(stdout), redirect_stderr(stderr):
            status = self.cli.main()
        return status, stdout.getvalue(), stderr.getvalue()

    def test_private_cli_redaction_immutability_and_no_payload_or_comment_access(self) -> None:
        status, stdout, stderr = self.command()
        self.assertEqual(status, 0, stderr)
        summary = json.loads(stdout)
        self.assertEqual(summary["status"], "reference_metadata_reconciled")
        self.assertFalse(summary["acquisition_verified"])
        self.assertFalse(summary["owner_schema_certified"])
        self.assertFalse(summary["scientific_readiness"])
        self.assertNotIn("videos", summary)
        for private in (str(self.home), "synthetic-private-release", "subject-01", "train_release/1/1"):
            self.assertNotIn(private, stdout + stderr)
        original = self.output.read_bytes()
        self.assertEqual(len(json.loads(original)["videos"]), 24)
        self.assertEqual(self.command()[0], 2)
        self.assertEqual(self.output.read_bytes(), original)

    def test_cli_blocks_semantic_omissions_corruption_and_full_reference_mismatch(self) -> None:
        self.headers = self.headers[1:]
        self.assertEqual(self.command()[0], 1)
        self.assertFalse(self.output.exists())
        self.headers = CasiaInventoryTest().headers()
        self.assertEqual(self.command("--require-full-reference")[0], 1)
        self.reader_error = OSError("synthetic private details " + str(self.input))
        status, stdout, stderr = self.command()
        self.assertEqual(status, 1)
        self.assertNotIn(str(self.input), stdout + stderr)
        self.assertNotIn("Traceback", stdout + stderr)

    def test_cli_refuses_output_repo_and_input_collisions(self) -> None:
        original = self.archive.read_bytes()
        for output in (self.archive, self.input / "new.json", self.sources / "new.json", self.wheel, ROOT / "results" / "refused-casia.json"):
            with self.subTest(output=output):
                self.output = output
                self.assertEqual(self.command()[0], 2)
        self.assertEqual(self.archive.read_bytes(), original)
        self.assertFalse((ROOT / "results" / "refused-casia.json").exists())

    def test_cli_blocks_encrypted_and_redirected_members(self) -> None:
        self.archive_encrypted = True
        self.assertEqual(self.command()[0], 1)
        self.archive_encrypted = False
        self.headers[0]["redirect"] = (4, "private-target")
        self.assertEqual(self.command()[0], 1)
        self.assertFalse(self.output.exists())

    def test_cli_refuses_symlink_loop_without_private_traceback(self) -> None:
        self.archive.unlink()
        self.archive.symlink_to(self.archive.name)
        status, stdout, stderr = self.command()
        self.assertEqual(status, 2)
        self.assertNotIn(str(self.home), stdout + stderr)
        self.assertNotIn("Traceback", stdout + stderr)

    def test_reader_hash_checked_before_import_and_import_origin_checked(self) -> None:
        with patch.object(self.cli.importlib, "import_module") as importer:
            with self.assertRaisesRegex(ValueError, "pinned bytes"):
                self.cli.load_reader(self.wheel)
            importer.assert_not_called()
        digest = hashlib.sha256(self.wheel.read_bytes()).hexdigest()
        with patch.dict(self.cli.RAR_READER, {"wheel_sha256": digest}), patch.object(self.cli.importlib, "import_module", return_value=SimpleNamespace(__version__="4.2", __file__=str(self.home / "outside.py"))):
            with self.assertRaisesRegex(ValueError, "originate"):
                self.cli.load_reader(self.wheel)

    def test_cli_failed_source_provenance_is_redacted(self) -> None:
        arguments = ["inventory_casia.py", "--archive", str(self.archive), "--reader-wheel", str(self.wheel), "--bob-source-root", str(self.sources), "--release-id", "synthetic", "--protocol-id", "synthetic", "--unverified-local", "--out", str(self.output)]
        stderr = io.StringIO()
        with patch.object(sys, "argv", arguments), patch.object(self.cli, "verify_bob_sources", side_effect=ValueError(str(self.sources))), redirect_stderr(stderr):
            self.assertEqual(self.cli.main(), 2)
        self.assertNotIn(str(self.sources), stderr.getvalue())
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()