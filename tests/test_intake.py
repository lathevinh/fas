from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.intake import EVIDENCE, PERMISSIONS, check_intake


class IntakeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.repo = self.home / "repo"
        self.repo.mkdir()
        self.data = self.home / "private"
        self.data.mkdir()
        self.receipt = {
            "version": 1, "status": "complete", "dataset": "OULU-NPU",
            "release_id": "synthetic-release", "protocol_id": "synthetic-protocol",
            "owner": "synthetic-owner", "channel": "official",
            "channel_reference": "synthetic-official-record", "downloaded_on": "2026-09-18",
            "permissions": {name: "unknown" for name in PERMISSIONS},
            "evidence": {name: self.file(f"agreements/{name}.txt") for name in EVIDENCE},
            "raw_root": "raw/oulu_npu/synthetic-release",
            "archives": [self.file("downloads/oulu_npu/synthetic-release/archive.bin")],
            "protocols": [self.file("raw/oulu_npu/synthetic-release/official_protocols/train.txt")],
        }

    def file(self, relative: str) -> dict:
        path = self.data / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"synthetic evidence only\n")
        return {"id": path.stem, "relpath": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

    def check(self) -> dict:
        return check_intake(self.repo, self.data, self.receipt)

    def test_complete_synthetic_receipt_verifies_without_media(self) -> None:
        result = self.check()
        self.assertEqual(result["status"], "verified", result["errors"])
        self.assertTrue(result["no_media_decoding"])

    def test_archive_and_protocol_hash_changes_are_blocked(self) -> None:
        for group in ("archives", "protocols"):
            with self.subTest(group=group):
                path = self.data / self.receipt[group][0]["relpath"]
                original = path.read_bytes()
                path.write_bytes(b"changed")
                self.assertEqual(self.check()["status"], "blocked")
                path.write_bytes(original)

    def test_unsafe_paths_are_blocked(self) -> None:
        for relative in ("../outside", "/tmp/archive", "downloads/../archive", "downloads//archive", "downloads/./archive", "C:\\archive", "downloads/\\archive", "downloads/archive\x00"):
            with self.subTest(relative=relative):
                self.receipt["archives"][0]["relpath"] = relative
                self.assertEqual(self.check()["status"], "blocked")

    def test_missing_identity_and_evidence_are_blocked(self) -> None:
        original = copy.deepcopy(self.receipt)
        for field in ("release_id", "protocol_id", "owner", "channel_reference", "downloaded_on", "permissions", "evidence", "archives", "protocols", "raw_root"):
            with self.subTest(field=field):
                self.receipt = copy.deepcopy(original)
                del self.receipt[field]
                self.assertEqual(self.check()["status"], "blocked")

    def test_mirror_requires_owner_equivalence_evidence(self) -> None:
        self.receipt["channel"] = "unofficial_mirror"
        self.assertEqual(self.check()["status"], "blocked")
        self.receipt["channel"] = "owner_confirmed_mirror"
        self.assertEqual(self.check()["status"], "blocked")
        self.receipt["evidence"]["mirror_equivalence"] = self.file("agreements/equivalence.txt")
        self.assertEqual(self.check()["status"], "verified")
        for channel in ("official", "owner_designated"):
            self.receipt["channel"] = channel
            self.assertEqual(self.check()["status"], "blocked")
        del self.receipt["evidence"]["mirror_equivalence"]
        self.assertEqual(self.check()["status"], "verified")

    def test_typed_schema_rejects_unknown_fields_and_malformed_values(self) -> None:
        original = copy.deepcopy(self.receipt)
        for field, value in (("version", True), ("version", 1.0), ("status", "pending"), ("dataset", "unregistered"), ("dataset", []), ("downloaded_on", "2026-02-30"), ("downloaded_on", "20260918"), ("release_id", " "), ("protocol_id", 12), ("archives", []), ("protocols", {}), ("evidence", []), ("permissions", {name: True for name in PERMISSIONS}), ("official_split", "inferred-from-folder")):
            with self.subTest(field=field, value=value):
                self.receipt = copy.deepcopy(original)
                self.receipt[field] = value
                self.assertEqual(self.check()["status"], "blocked")

    def test_artifact_shape_missing_empty_and_invalid_hash_are_blocked(self) -> None:
        original = copy.deepcopy(self.receipt)
        for value in (None, {}, {"id": "archive", "relpath": "downloads/archive", "sha256": "a" * 64}, {"id": "", "relpath": original["archives"][0]["relpath"], "sha256": "not-a-hash"}):
            self.receipt = copy.deepcopy(original)
            self.receipt["archives"] = [value]
            self.assertEqual(self.check()["status"], "blocked")
        self.receipt = copy.deepcopy(original)
        artifact = self.receipt["evidence"]["license"]
        (self.data / artifact["relpath"]).write_bytes(b"")
        artifact["sha256"] = hashlib.sha256(b"").hexdigest()
        self.assertEqual(self.check()["status"], "blocked")

    def test_duplicate_artifact_ids_and_paths_are_blocked(self) -> None:
        for group in ("archives", "protocols"):
            original = copy.deepcopy(self.receipt[group])
            self.receipt[group].append(copy.deepcopy(original[0]))
            self.assertEqual(self.check()["status"], "blocked")
            self.receipt[group] = original

    def test_storage_categories_and_raw_root_are_checked(self) -> None:
        original = copy.deepcopy(self.receipt)
        self.receipt["archives"] = [self.file("agreements/archive.bin")]
        self.assertEqual(self.check()["status"], "blocked")
        self.receipt = copy.deepcopy(original)
        self.receipt["protocols"] = [self.file("raw/other/official_protocols/train.txt")]
        self.assertEqual(self.check()["status"], "blocked")
        for relative in ("raw/../other", "raw//other", "/raw/other", "raw", "raw/missing", "downloads/oulu_npu"):
            self.receipt = copy.deepcopy(original)
            self.receipt["raw_root"] = relative
            self.assertEqual(self.check()["status"], "blocked")

    def test_symlink_escape_and_loop_are_blocked(self) -> None:
        outside = self.home / "outside.bin"
        outside.write_bytes(b"synthetic evidence only\n")
        link = self.data / "downloads/link.bin"
        link.symlink_to(outside)
        self.receipt["archives"][0]["relpath"] = "downloads/link.bin"
        self.assertEqual(self.check()["status"], "blocked")
        link.unlink()
        link.symlink_to(link)
        self.assertEqual(self.check()["status"], "blocked")

    def test_symlink_alias_duplicate_is_blocked(self) -> None:
        original = self.receipt["protocols"][0]
        link = self.data / "raw/oulu_npu/synthetic-release/official_protocols/alias.txt"
        link.symlink_to(self.data / original["relpath"])
        self.receipt["protocols"].append({"id": "alias", "relpath": str(link.relative_to(self.data)), "sha256": original["sha256"]})
        self.assertEqual(self.check()["status"], "blocked")

    def test_media_is_not_opened_or_decoded(self) -> None:
        media = self.data / "raw/oulu_npu/synthetic-release/media/not-a-video.bin"
        media.parent.mkdir()
        media.write_bytes(b"not a valid video")
        original_open = Path.open

        def guarded_open(path: Path, *arguments, **options):
            if path == media:
                raise AssertionError("intake must not open media")
            return original_open(path, *arguments, **options)

        with patch("fas.intake.Path.open", guarded_open):
            self.assertEqual(self.check()["status"], "verified")
            self.receipt["raw_root"] = None
            self.receipt["protocols"] = [{"id": "not-a-protocol", "relpath": str(media.relative_to(self.data)), "sha256": hashlib.sha256(b"not a valid video").hexdigest()}]
            self.assertEqual(self.check()["status"], "blocked")

    def test_private_roots_must_not_overlap_repository(self) -> None:
        for root in (self.repo, self.repo / "data", self.home):
            self.assertEqual(check_intake(self.repo, root, self.receipt)["status"], "blocked")

    def test_negative_permissions_do_not_authorize_or_block_hash_verification(self) -> None:
        self.receipt["permissions"] = {name: "prohibited" for name in PERMISSIONS}
        self.assertEqual(self.check()["status"], "verified")
        self.assertIn("not media inventory, license interpretation", self.check()["scope"])

    def command(self, receipt: Path, *arguments: str) -> list[str]:
        return [sys.executable, str(ROOT / "scripts/check_intake.py"), "--receipt", str(receipt), "--data-root", str(self.data), *arguments]

    def test_cli_redacts_private_content_and_writes_immutable_report(self) -> None:
        self.receipt["channel_reference"] = "https://private.invalid/protected-link"
        path = self.data / "receipt.json"
        path.write_text(json.dumps(self.receipt), encoding="utf-8")
        output = self.home / "public-report.json"
        command = self.command(path, "--out", str(output))
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "verified")
        for private in (str(self.data), "protected-link", "synthetic-owner", "synthetic-release"):
            self.assertNotIn(private, result.stdout)
            self.assertNotIn(private, output.read_text())
        before = output.read_bytes()
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(output.read_bytes(), before)

    def test_cli_blocks_pending_template_and_private_output(self) -> None:
        path = self.data / "receipt.json"
        path.write_bytes((ROOT / "manifests/intake_template_v1.json").read_bytes())
        result = subprocess.run(self.command(path), capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "blocked")
        path.write_text(json.dumps(self.receipt), encoding="utf-8")
        before = path.read_bytes()
        for output in (path, self.data / "agreements/new-report.json"):
            result = subprocess.run(self.command(path, "--out", str(output)), capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse((self.data / "agreements/new-report.json").exists())

    def test_cli_rejects_repository_receipt_and_malformed_json(self) -> None:
        result = subprocess.run(self.command(ROOT / "manifests/intake_template_v1.json"), capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        path = self.data / "bad.json"
        for content in ("not JSON", "[]"):
            path.write_text(content, encoding="utf-8")
            result = subprocess.run(self.command(path), capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()