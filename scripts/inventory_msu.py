#!/usr/bin/env python3
"""Inspect nested split MSU ZIPs without opening any video entry."""

from __future__ import annotations

import argparse
import bisect
import contextlib
import hashlib
import io
import json
import platform
import re
import stat
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.intake import _relative_path
from fas.msu import METADATA_SHA256, inventory_headers

OUTER_README_SHA256 = "e48d19e415ace32796d7cc242cbd6caed0de488447188587066f070851b65b24"


def header_record(entry: zipfile.ZipInfo) -> dict:
    return {"path": entry.filename, "size": entry.file_size, "crc32": entry.CRC,
            "compressed_size": entry.compress_size, "flags": entry.flag_bits, "external_attr": entry.external_attr}


def safe_entry(entry: zipfile.ZipInfo) -> None:
    directory = entry.is_dir()
    if (_relative_path(entry.filename.removesuffix("/") if directory else entry.filename) is None
            or entry.flag_bits & 1 or entry.file_size < 0
            or stat.S_IFMT(entry.external_attr >> 16) not in (0, stat.S_IFDIR if directory else stat.S_IFREG)):
        raise ValueError("unsafe package entry")


class SplitZipReader(io.RawIOBase):
    def __init__(self, parts: list[tuple[Path, zipfile.ZipInfo]], stack: contextlib.ExitStack):
        self.parts, self.stack = parts, stack
        self.position = 0
        self.streams = {}
        self.offsets = [0]
        for _, entry in parts:
            self.offsets.append(self.offsets[-1] + entry.file_size)

    def seekable(self) -> bool:
        return True

    def readable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.position

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence not in (0, 1, 2):
            raise ValueError("invalid seek origin")
        position = offset + (self.position if whence == 1 else self.offsets[-1] if whence == 2 else 0)
        if position < 0:
            raise ValueError("negative seek")
        self.position = position
        return position

    def read(self, size: int = -1) -> bytes:
        remaining = max(0, self.offsets[-1] - self.position)
        size = remaining if size < 0 else min(size, remaining)
        if size > 8 * 1024 * 1024:
            raise ValueError("metadata read exceeds limit")
        chunks = []
        while size:
            index = bisect.bisect_right(self.offsets, self.position) - 1
            archive_path, entry = self.parts[index]
            if index not in self.streams:
                outer = self.stack.enter_context(zipfile.ZipFile(archive_path))
                if header_record(outer.getinfo(entry.filename)) != header_record(entry):
                    raise ValueError("volume header changed")
                self.streams[index] = self.stack.enter_context(outer.open(entry.filename))
            stream = self.streams[index]
            stream.seek(self.position - self.offsets[index])
            chunk = stream.read(min(size, self.offsets[index + 1] - self.position))
            if not chunk:
                raise ValueError("truncated volume")
            chunks.append(chunk)
            self.position += len(chunk)
            size -= len(chunk)
        return b"".join(chunks)


def read_package(directory: Path) -> tuple[list[dict], dict[str, bytes], dict]:
    parts, outer_records, names = {}, [], set()
    outer_readme = None
    for archive_path in sorted(directory.glob("*.zip")):
        if archive_path.is_symlink() or not archive_path.is_file():
            raise ValueError("unsafe archive input")
        with zipfile.ZipFile(archive_path) as outer:
            entries = outer.infolist()
            outer_records.append({"archive": archive_path.name, "archive_bytes": archive_path.stat().st_size,
                                  "headers": [header_record(entry) for entry in entries]})
            for entry in entries:
                safe_entry(entry)
                if entry.is_dir():
                    if entry.filename != "MSU-MFSD/":
                        raise ValueError("unknown outer directory")
                    continue
                if entry.filename in names or entry.file_size == 0:
                    raise ValueError("duplicate or empty outer entry")
                names.add(entry.filename)
                if entry.filename == "MSU-MFSD/README.txt":
                    if entry.file_size > 65536:
                        raise ValueError("oversized README")
                    outer_readme = outer.read(entry.filename)
                else:
                    match = re.fullmatch(r"MSU-MFSD/MSU-MFSD-Publish\.zip\.([0-9]{3})", entry.filename)
                    if match is None:
                        raise ValueError("unknown volume name")
                    parts[int(match.group(1))] = (archive_path, entry)
    if set(parts) != set(range(1, 17)) or outer_readme is None:
        raise ValueError("incomplete native volume set")
    sizes = [parts[index][1].file_size for index in range(1, 17)]
    if len(set(sizes[:-1])) != 1 or sizes[-1] > sizes[0]:
        raise ValueError("inconsistent volume boundaries")
    metadata = {}
    with contextlib.ExitStack() as stack:
        reader = SplitZipReader([parts[index] for index in range(1, 17)], stack)
        with zipfile.ZipFile(reader) as inner:
            entries = inner.infolist()
            inner_names = set()
            for entry in entries:
                safe_entry(entry)
                normalized = entry.filename.removesuffix("/")
                if normalized in inner_names:
                    raise ValueError("duplicate inner entry")
                inner_names.add(normalized)
                if entry.filename in METADATA_SHA256:
                    if not 0 < entry.file_size <= 65536:
                        raise ValueError("invalid metadata size")
                    metadata[entry.filename] = inner.read(entry.filename)
            headers = [header_record(entry) for entry in entries]
    outer_readme_hash = hashlib.sha256(outer_readme).hexdigest()
    if outer_readme_hash != OUTER_README_SHA256:
        raise ValueError("outer README differs from supplied packaging reference")
    provenance = {"library": "zipfile", "python_version": platform.python_version(),
        "scope": "outer volume streams, inner central directory and three bounded native text files",
        "outer_archives": len(outer_records), "volumes": len(parts),
        "outer_archive_bytes": sum(row["archive_bytes"] for row in outer_records),
        "outer_header_inventory_sha256": hashlib.sha256(json.dumps(outer_records, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "outer_readme_sha256_verified": outer_readme_hash,
        "readme_copies_identical": metadata.get("README.txt") == outer_readme,
        "schema_authority": "inner native README plus official subject lists",
        "volume_payload_seek_may_decompress_container_bytes": True,
        "outer_volume_integrity_fully_verified": False, "no_video_entry_opened": True}
    return headers, metadata, provenance


def redacted_summary(result: dict, digest: str) -> dict:
    rows = result["videos"]
    return {"version": 1, "dataset": "MSU-MFSD", "status": result["status"], "inventory_sha256": digest,
        "eligible_videos": len(rows), "subjects": len({row["subject_id"] for row in rows}),
        "partitions": {split: {"subjects": len({row["subject_id"] for row in rows if row["official_split"] == split}),
                               **{label: sum(row["official_split"] == split and row["binary_label"] == label for row in rows) for label in ("bona_fide", "attack")}} for split in ("train", "test")},
        "attack_type_counts": {token: sum(row["reference_attack_type"] == token for row in rows) for token in ("none", "ipad_video", "iphone_video", "printed_photo")},
        **{field: result[field] for field in ("metadata_authority", "metadata_sha256_verified", "label_mapping", "label_mapping_hash", "header_inventory_sha256", "reader_provenance", "full_native_universe_checked", "acquisition_verified", "archive_integrity_verified", "media_integrity_verified", "media_decode_verified", "participant_identity_verified", "scientific_readiness", "roles_assigned", "no_video_entry_opened", "no_model_inference_or_training", "face_annotations_used")}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive-dir", type=Path, required=True)
    parser.add_argument("--release-id", required=True)
    parser.add_argument("--unverified-local", action="store_true", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        directory, output = args.archive_dir.resolve(), args.out.resolve()
        if (not directory.is_dir() or args.out.exists() or args.out.is_symlink()
                or output.is_relative_to(ROOT) or output.is_relative_to(directory)
                or (directory.is_relative_to(ROOT) and directory != (ROOT / "MSU").resolve())):
            raise ValueError("invalid private input/output")
    except (ValueError, OSError, RuntimeError):
        print("MSU INVENTORY FAILED: invalid private input or new output", file=sys.stderr)
        return 2
    try:
        headers, metadata, provenance = read_package(directory)
        result = inventory_headers(headers, metadata, release_id=args.release_id)
        result["reader_provenance"] = provenance
    except (ValueError, OSError, RuntimeError, UnicodeError, KeyError, EOFError, zipfile.BadZipFile, NotImplementedError, zlib.error):
        print(json.dumps({"status": "blocked", "errors": ["unsafe, incomplete or native-metadata-incompatible archive package"]}))
        return 1
    try:
        write_immutable_record(output, result)
        digest = hashlib.sha256(output.read_bytes()).hexdigest()
    except (ValueError, OSError, RuntimeError):
        print("MSU INVENTORY FAILED: private output unavailable or already exists", file=sys.stderr)
        return 2
    print(json.dumps(redacted_summary(result, digest), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())