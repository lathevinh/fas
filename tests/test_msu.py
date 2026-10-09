from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import stat
import tempfile
import sys
import unittest
import zipfile
import zlib
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas import msu
from fas.msu import ATTACK_TYPES, LABEL_MAPPING, LABEL_MAPPING_HASH, encode_label, inventory_headers, parse_media_path, parse_subject_lists


class MsuMetadataTest(unittest.TestCase):
    def test_native_types_cameras_and_polarity(self) -> None:
        subjects = parse_subject_lists("01", "02")
        for camera, extension in (("android", "mp4"), ("laptop", "mov")):
            for category, attack_type in (("real", None), *(("attack", token) for token in ATTACK_TYPES)):
                token = f"_{attack_type}" if attack_type else ""
                row = parse_media_path(f"scene01/{category}/{category}_client001_{camera}_SD{token}_scene01.{extension}", subjects)
                self.assertEqual(encode_label(row["binary_label"]), int(category == "attack"))
                self.assertEqual(row["attack_family"], ATTACK_TYPES[attack_type] if attack_type else "none")
                self.assertEqual(row["sensor_id"], camera)
                self.assertEqual((row["group_unit"], row["group_id"]), ("subject", "subject-001"))
                self.assertEqual(row["environment"], "unknown")
                self.assertIsNone(row["role"])

    def test_official_lists_keep_native_namespace_and_disjoint_subjects(self) -> None:
        subjects = parse_subject_lists("01\n03\n", "02\n04\n")
        self.assertEqual(subjects, {"001": "train", "003": "train", "002": "test", "004": "test"})
        for train, test in (("01 01", "02"), ("01", "01"), ("", "02"), ("1", "02"), ("00", "02"), ("56", "02"), ("01", "02.0")):
            with self.subTest(train=train, test=test), self.assertRaises(ValueError):
                parse_subject_lists(train, test)

    def test_unknown_alias_unsafe_paths_and_membership_fail_closed(self) -> None:
        valid = "scene01/real/real_client001_android_SD_scene01.mp4"
        subjects = parse_subject_lists("01", "02")
        for path in (None, 1, "../" + valid, "/" + valid, valid.replace("/", "//"), valid.replace("/", "\\"), valid.replace("001", "003"), valid.replace("real/", "attack/"), valid.replace("android", "other"), valid.replace("mp4", "mov"), valid.replace("SD", "sd"), valid.replace("client001", "client01"), valid.replace("scene01", "scene02"), valid.replace(".mp4", ".MP4"), valid.replace("_SD_", "_SD_ipad_video_")):
            with self.subTest(path=path), self.assertRaises(ValueError):
                parse_media_path(path, subjects)

    def test_mapping_hash_and_fixed_prediction_error_polarity(self) -> None:
        self.assertEqual(LABEL_MAPPING_HASH, hashlib.sha256(json.dumps(LABEL_MAPPING, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
        for label, score, expected_error in (("bona_fide", 0.1, 0), ("bona_fide", 0.9, 1), ("attack", 0.1, 1), ("attack", 0.9, 0)):
            self.assertEqual(int(int(score >= 0.5) != encode_label(label)), expected_error)
        with self.assertRaises(ValueError):
            encode_label("unknown")


class MsuInventoryTest(unittest.TestCase):
    def metadata(self):
        return {"README.txt": b"synthetic native README", "train_sub_list.txt": b"01\n", "test_sub_list.txt": b"02\n"}

    def headers(self):
        names = list(self.metadata())
        for subject in ("001", "002"):
            for camera, extension in (("android", "mp4"), ("laptop", "mov")):
                for category, attack_type in (("real", None), *(("attack", token) for token in ATTACK_TYPES)):
                    token = f"_{attack_type}" if attack_type else ""
                    stem = f"scene01/{category}/{category}_client{subject}_{camera}_SD{token}_scene01"
                    names.extend((f"{stem}.{extension}", f"{stem}.face"))
        return [{"path": name, "size": 100, "crc32": 0, "compressed_size": 100, "flags": 0, "external_attr": 0} for name in names]

    def inventory(self, headers=None, metadata=None, **kwargs):
        payloads = self.metadata()
        with patch.dict(msu.METADATA_SHA256, {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()}, clear=True):
            return inventory_headers(self.headers() if headers is None else headers, payloads if metadata is None else metadata,
                                     release_id="synthetic-release", require_full_release=kwargs.get("full", False))

    def test_inventory_deterministic_complete_groups_and_unprobed_media(self):
        result = self.inventory()
        self.assertEqual(result, self.inventory(list(reversed(self.headers()))))
        self.assertEqual(len(result["videos"]), 16)
        self.assertEqual(sum(row["binary_label"] == "bona_fide" for row in result["videos"]), 4)
        self.assertFalse(result["scientific_readiness"])
        self.assertFalse(result["face_annotations_used"])
        for row in result["videos"]:
            self.assertIsNone(row["role"])
            self.assertEqual(row["decode_status"], "not_probed")
            self.assertTrue(all(row[key] is None for key in ("media_sha256", "codec", "container", "duration_ms", "fps", "frame_count")))

    def test_missing_duplicate_replaced_ids_and_sidecars_rejected(self):
        headers = self.headers()
        for changed in (headers[:-1], headers + [headers[-1]], headers[1:], [dict(row, path=row["path"].replace("client002", "client003")) for row in headers]):
            with self.assertRaises(ValueError):
                self.inventory(changed)

    def test_unsafe_link_encrypted_empty_and_untyped_headers_rejected(self):
        for change in ({"path": "../outside"}, {"path": "scene01//real/file.mp4"}, {"size": 0}, {"size": True}, {"flags": 1}, {"external_attr": (stat.S_IFLNK | 0o777) << 16}, {"external_attr": (stat.S_IFDIR | 0o755) << 16}, {"crc32": -1}, {"extra": 1}):
            headers = self.headers()
            headers[-1] = {**headers[-1], **change}
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.inventory(headers)

    def test_pinned_metadata_and_full_release_counts_fail_closed(self):
        for changed in ({**self.metadata(), "README.txt": b"changed"}, {**self.metadata(), "train_sub_list.txt": b"01\n\n"}, {"README.txt": b"synthetic native README"}):
            with self.assertRaises(ValueError):
                self.inventory(metadata=changed)
        with self.assertRaises(ValueError):
            self.inventory(full=True)

    def test_raw_metadata_bom_is_bound_before_text_decoding(self):
        payloads = self.metadata()
        payloads["README.txt"] = bytes.fromhex("efbbbf") + payloads["README.txt"]
        pins = {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()}
        with patch.dict(msu.METADATA_SHA256, pins, clear=True):
            result = inventory_headers(self.headers(), payloads, release_id="synthetic-bom-release", require_full_release=False)
            self.assertEqual(result["metadata_sha256_verified"], pins)
            payloads["README.txt"] = payloads["README.txt"].decode("utf-8-sig").encode()
            with self.assertRaises(ValueError):
                inventory_headers(self.headers(), payloads, release_id="synthetic-bom-release", require_full_release=False)


class MsuCliTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.directory = self.home / "inputs"
        self.directory.mkdir()
        self.output = self.home / "private.json"
        self.metadata = {"README.txt": b"synthetic native README", "train_sub_list.txt": "\n".join(f"{subject:02d}" for subject in range(1, 16)).encode(), "test_sub_list.txt": "\n".join(f"{subject:02d}" for subject in range(16, 36)).encode()}
        self.pins = {name: hashlib.sha256(payload).hexdigest() for name, payload in self.metadata.items()}
        spec = importlib.util.spec_from_file_location("msu_cli", ROOT / "scripts/inventory_msu.py")
        self.cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.cli)
        self.package()

    def package(self, change_readme=False, missing_video=False):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as inner:
            for name, payload in self.metadata.items():
                inner.writestr(name, payload + b"changed" if change_readme and name == "README.txt" else payload)
            templates = [row["path"] for row in MsuInventoryTest().headers() if "client001" in row["path"]]
            for subject in range(1, 36):
                for template in templates:
                    if missing_video and subject == 1 and template.endswith(".mp4"):
                        continue
                    inner.writestr(template.replace("client001", f"client{subject:03d}"), b"synthetic payload")
        payload = buffer.getvalue()
        width = (len(payload) + 15) // 16
        for archive_number in range(8):
            with zipfile.ZipFile(self.directory / f"transport-{archive_number}.zip", "w", compression=zipfile.ZIP_DEFLATED) as outer:
                if archive_number == 0:
                    outer.writestr("MSU-MFSD/README.txt", self.metadata["README.txt"])
                for index in (archive_number * 2, archive_number * 2 + 1):
                    outer.writestr(f"MSU-MFSD/MSU-MFSD-Publish.zip.{index + 1:03d}", payload[index * width:(index + 1) * width])

    def command(self, *extra):
        stdout, stderr = io.StringIO(), io.StringIO()
        original_open = zipfile.ZipFile.open
        def guarded_open(archive, name, *args, **kwargs):
            filename = name.filename if isinstance(name, zipfile.ZipInfo) else name
            if filename not in msu.METADATA_SHA256 and filename != "MSU-MFSD/README.txt" and not filename.startswith("MSU-MFSD/MSU-MFSD-Publish.zip."):
                raise AssertionError("video/sidecar/helper entry opened")
            return original_open(archive, name, *args, **kwargs)
        with patch.object(sys, "argv", ["inventory_msu", "--archive-dir", str(self.directory), "--release-id", "private-synthetic-release", "--unverified-local", "--out", str(self.output), *extra]), patch.dict(msu.METADATA_SHA256, self.pins, clear=True), patch.object(self.cli, "OUTER_README_SHA256", self.pins["README.txt"]), patch.object(zipfile.ZipFile, "open", guarded_open), redirect_stdout(stdout), redirect_stderr(stderr):
            status = self.cli.main()
        return status, stdout.getvalue(), stderr.getvalue()

    def test_actual_stream_fixture_redaction_no_video_open_and_immutable_output(self):
        status, stdout, stderr = self.command()
        self.assertEqual(status, 0, stderr)
        summary = json.loads(stdout)
        self.assertEqual((summary["eligible_videos"], summary["subjects"]), (280, 35))
        self.assertEqual(summary["inventory_sha256"], hashlib.sha256(self.output.read_bytes()).hexdigest())
        for private in (str(self.home), "private-synthetic-release", "client001", "subject-001"):
            self.assertNotIn(private, stdout + stderr)
        original = self.output.read_bytes()
        self.assertEqual(self.command()[0], 2)
        self.assertEqual(self.output.read_bytes(), original)

    def test_missing_duplicate_or_unknown_volumes_rejected(self):
        archive = self.directory / "transport-7.zip"
        payload = archive.read_bytes()
        archive.unlink()
        self.assertEqual(self.command()[0], 1)
        archive.write_bytes(payload)
        (self.directory / "extra.zip").write_bytes(payload)
        self.assertEqual(self.command()[0], 1)
        (self.directory / "extra.zip").unlink()
        with zipfile.ZipFile(archive, "a") as outer:
            outer.writestr("MSU-MFSD/unexpected.bin", b"unknown")
        self.assertEqual(self.command()[0], 1)

    def test_changed_metadata_incomplete_native_inventory_and_corrupt_zip_rejected(self):
        self.package(change_readme=True)
        self.assertEqual(self.command()[0], 1)
        self.package(missing_video=True)
        self.assertEqual(self.command()[0], 1)
        (self.directory / "transport-7.zip").write_bytes(b"private invalid ZIP")
        status, stdout, stderr = self.command()
        self.assertEqual(status, 1)
        self.assertNotIn("Traceback", stdout + stderr)

    def test_private_output_boundaries_and_symlink_loops_rejected(self):
        for target in (ROOT / "manifests/private/forbidden.json", self.directory / "new.json", self.directory / "transport-0.zip"):
            self.assertEqual(self.command("--out", str(target))[0], 2)
        link = self.home / "loop"
        link.symlink_to(link)
        status, stdout, stderr = self.command("--out", str(link))
        self.assertEqual(status, 2)
        self.assertNotIn(str(self.home), stdout + stderr)
        link.unlink()
        link.symlink_to(self.home / "not-created.json")
        self.assertEqual(self.command("--out", str(link))[0], 2)

    def test_source_symlink_and_unsafe_outer_entry_rejected(self):
        original = self.directory / "transport-0.zip"
        moved = self.home / "outside.zip"
        original.rename(moved)
        original.symlink_to(moved)
        self.assertEqual(self.command()[0], 1)
        original.unlink()
        moved.rename(original)
        with zipfile.ZipFile(original, "a") as outer:
            outer.writestr("../unsafe", b"private")
        self.assertEqual(self.command()[0], 1)

    def test_reader_cross_boundary_seek_and_read_limits(self):
        import contextlib
        with zipfile.ZipFile(self.directory / "transport-0.zip") as archive:
            parts = [(self.directory / "transport-0.zip", entry) for entry in archive.infolist() if entry.filename.endswith((".001", ".002"))]
            expected = b"".join(archive.read(entry.filename) for _, entry in parts)
        with contextlib.ExitStack() as stack:
            reader = self.cli.SplitZipReader(parts, stack)
            boundary = parts[0][1].file_size
            reader.seek(boundary - 2)
            self.assertEqual(reader.read(4), expected[boundary - 2:boundary + 2])
            reader.seek(-4, 2)
            self.assertEqual(reader.read(), expected[-4:])
            self.assertEqual(reader.read(1), b"")
            with self.assertRaises(ValueError):
                reader.offsets[-1] = 16 * 1024 * 1024
                reader.seek(0)
                reader.read(9 * 1024 * 1024)
            with self.assertRaises(ValueError):
                reader.seek(-1)
            with self.assertRaises(ValueError):
                reader.seek(0, 3)

    def test_encrypted_link_and_wrong_file_kind_entries_rejected(self):
        for flags, mode in ((1, stat.S_IFREG), (0, stat.S_IFLNK), (0, stat.S_IFDIR)):
            entry = zipfile.ZipInfo("MSU-MFSD/MSU-MFSD-Publish.zip.001")
            entry.flag_bits = flags
            entry.external_attr = (mode | 0o644) << 16
            with self.assertRaises(ValueError):
                self.cli.safe_entry(entry)

    def test_decompression_failure_is_sanitized(self):
        with patch.object(self.cli, "read_package", side_effect=zlib.error("private data failure")):
            status, stdout, stderr = self.command()
        self.assertEqual(status, 1)
        self.assertNotIn("private data failure", stdout + stderr)
        self.assertNotIn("Traceback", stdout + stderr)

    def test_outer_readme_has_separate_pin_and_inner_remains_schema_authority(self):
        with patch.object(self.cli, "OUTER_README_SHA256", "0" * 64):
            with patch.dict(msu.METADATA_SHA256, self.pins, clear=True):
                with self.assertRaises(ValueError):
                    self.cli.read_package(self.directory)
        with patch.object(self.cli, "OUTER_README_SHA256", self.pins["README.txt"]):
            headers, metadata, provenance = self.cli.read_package(self.directory)
        self.assertEqual(metadata, self.metadata)
        self.assertEqual(provenance["schema_authority"], "inner native README plus official subject lists")