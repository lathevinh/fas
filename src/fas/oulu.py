"""OULU-NPU official metadata parsing; no model or frame extraction."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import tarfile
from pathlib import Path
from typing import Any

from .intake import _relative_path

ACCESS_TYPES = {
    "1": {"binary_label": "bona_fide", "attack_family": "none", "instrument": "none"},
    "2": {"binary_label": "attack", "attack_family": "print", "instrument": "printer-1"},
    "3": {"binary_label": "attack", "attack_family": "print", "instrument": "printer-2"},
    "4": {"binary_label": "attack", "attack_family": "replay", "instrument": "display-1"},
    "5": {"binary_label": "attack", "attack_family": "replay", "instrument": "display-2"},
}
LABEL_MAPPING = {
    "id": "oulu-npu-official",
    "version": 1,
    "authority": "release Readme.pdf pages 1-3; official Protocols archive",
    "train_development": {"+1": "bona_fide", "-1": "attack"},
    "test": {"+1": "bona_fide", "-1": "print", "-2": "replay"},
    "access_types": ACCESS_TYPES,
    "model_boundary": {"bona_fide": 0, "attack": 1},
}
LABEL_MAPPING_HASH = hashlib.sha256(
    json.dumps(LABEL_MAPPING, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()
SPLITS = {"Train": "train", "Dev": "development", "Test": "test"}
SUBJECT_RANGES = {"train": range(1, 21), "development": range(21, 36), "test": range(36, 56)}


def encode_label(binary_label: str) -> int:
    if binary_label not in ("bona_fide", "attack"):
        raise ValueError("unknown canonical label")
    return 0 if binary_label == "bona_fide" else 1


def parse_video_id(video_id: str) -> dict[str, Any]:
    if not isinstance(video_id, str) or re.fullmatch(r"[1-6]_[1-3]_(?:0[1-9]|[1-4][0-9]|5[0-5])_[1-5]", video_id) is None:
        raise ValueError("invalid OULU video identifier")
    phone, session, subject, access = video_id.split("_")
    return {
        "dataset": "OULU-NPU", "source_record_id": video_id, "video_id": video_id,
        "subject_id": f"subject-{subject}", "sensor_id": f"phone-{phone}",
        "session_id": f"session-{session}", "environment": "unknown", "material": "unknown",
        **ACCESS_TYPES[access], "label_mapping_id": LABEL_MAPPING["id"],
        "label_mapping_version": LABEL_MAPPING["version"], "label_mapping_hash": LABEL_MAPPING_HASH,
    }


def protocol_scope(protocol_relpath: str) -> tuple[int, int | None, str]:
    match = re.fullmatch(r"Protocols/Protocol_([1-4])/(Train|Dev|Test)(?:_([1-6]))?\.txt", protocol_relpath)
    if match is None:
        raise ValueError("invalid official protocol path")
    protocol, split, fold = match.groups()
    protocol = int(protocol)
    if (protocol in (3, 4)) != (fold is not None):
        raise ValueError("invalid protocol fold")
    return protocol, int(fold) if fold else None, SPLITS[split]


def _check_membership(video_id: str, protocol: int, fold: int | None, split: str) -> None:
    phone, session, subject, access = (int(part) for part in video_id.split("_"))
    if subject not in SUBJECT_RANGES[split]:
        raise ValueError("subject disagrees with official split")
    if protocol in (1, 4) and session not in ((3,) if split == "test" else (1, 2)):
        raise ValueError("session disagrees with official protocol")
    if protocol in (2, 4) and access not in ((1, 3, 5) if split == "test" else (1, 2, 4)):
        raise ValueError("access type disagrees with official protocol")
    if fold is not None and ((phone == fold) != (split == "test")):
        raise ValueError("sensor disagrees with official fold")


def parse_protocol(text: str, protocol_relpath: str) -> list[dict[str, Any]]:
    protocol, fold, split = protocol_scope(protocol_relpath)
    records: list[dict[str, Any]] = []
    identifiers: set[str] = set()
    try:
        rows = csv.reader(io.StringIO(text.removeprefix("\ufeff")), strict=True)
        for row in rows:
            if len(row) != 2:
                raise ValueError("protocol records must have exactly two CSV columns")
            token, video_id = (value.strip() for value in row)
            metadata = parse_video_id(video_id)
            if video_id in identifiers:
                raise ValueError("duplicate official video identifier")
            identifiers.add(video_id)
            expected = "+1" if metadata["binary_label"] == "bona_fide" else "-1"
            if split == "test" and metadata["attack_family"] == "replay":
                expected = "-2"
            if token != expected:
                raise ValueError("unknown or inconsistent raw label token")
            _check_membership(video_id, protocol, fold, split)
            records.append({
                **metadata, "official_split": split, "protocol_number": protocol,
                "protocol_fold": fold, "label_source": protocol_relpath,
                "raw_label_token": token,
            })
    except csv.Error:
        raise ValueError("unreadable protocol CSV") from None
    if not records:
        raise ValueError("official protocol must not be empty")
    return records


def _sha256(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def _regular_members(archive: tarfile.TarFile) -> list[tarfile.TarInfo]:
    members: list[tarfile.TarInfo] = []
    paths: set[str] = set()
    for member in archive.getmembers():
        relative = _relative_path(member.name.rstrip("/") if member.isdir() else member.name)
        if relative is None or (not member.isdir() and not member.isfile()):
            raise ValueError("unsafe or unsupported archive member")
        if member.name in paths:
            raise ValueError("duplicate archive member path")
        paths.add(member.name)
        if member.isfile():
            if member.size <= 0:
                raise ValueError("empty archive member")
            members.append(member)
    return members


def inventory_archives(
    input_root: Path, *, release_id: str, protocol_id: str,
    require_full_release: bool = False, hash_media: bool = False,
) -> dict[str, Any]:
    for value in (release_id, protocol_id):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("release and protocol identifiers must be explicit")
    root = input_root.resolve()
    required = ("Readme.pdf", "Protocols.tar", "Train_files.tar", "Dev_files.tar", "Test_files.tar")
    for name in required:
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file() or path.stat().st_size <= 0:
            raise ValueError("required local documentation or archive missing or unsafe")
    records: dict[str, dict[str, Any]] = {}
    archive_hashes: dict[str, str | None] = {"Protocols.tar": _sha256(root / "Protocols.tar")}
    for storage, split in (("Train_files", "train"), ("Dev_files", "development"), ("Test_files", "test")):
        archive_path = root / f"{storage}.tar"
        archive_hashes[archive_path.name] = _sha256(archive_path) if hash_media else None
        auxiliary: set[str] = set()
        video_ids: set[str] = set()
        with tarfile.open(archive_path, "r:*") as archive:
            for member in _regular_members(archive):
                path = _relative_path(member.name)
                if path is None or len(path.parts) != 2 or path.parts[0] != storage or path.suffix not in (".avi", ".txt"):
                    raise ValueError("unexpected media archive layout")
                metadata = parse_video_id(path.stem)
                subject = int(path.stem.split("_")[2])
                if subject not in SUBJECT_RANGES[split]:
                    raise ValueError("storage disagrees with documented subject partition")
                if path.suffix == ".txt":
                    auxiliary.add(path.stem)
                    continue
                if path.stem in records:
                    raise ValueError("duplicate media video identifier")
                video_ids.add(path.stem)
                digest = None
                if hash_media:
                    source = archive.extractfile(member)
                    if source is None:
                        raise ValueError("unreadable media member")
                    with source:
                        digest = hashlib.file_digest(source, "sha256").hexdigest()
                records[path.stem] = {
                    **metadata, "release_id": release_id, "protocol_id": protocol_id,
                    "official_split": None, "media_relpath": member.name,
                    "media_archive": archive_path.name, "byte_size": member.size,
                    "media_sha256": digest, "container": None, "codec": None,
                    "duration_ms": None, "fps": None, "frame_count": None,
                    "decode_status": "not_probed", "protocol_memberships": [],
                }
        if not video_ids or video_ids != auxiliary:
            raise ValueError("video and provided landmark-file inventories disagree")
    if require_full_release:
        expected = {
            f"{phone}_{session}_{subject:02d}_{access}"
            for phone in range(1, 7) for session in range(1, 4)
            for subject in range(1, 56) for access in range(1, 6)
        }
        if set(records) != expected:
            raise ValueError("media inventory differs from the documented full release")
    expected_protocols = {
        f"Protocols/Protocol_{protocol}/{split}{suffix}.txt"
        for protocol in range(1, 5) for split in ("Train", "Dev", "Test")
        for suffix in (("",) if protocol < 3 else tuple(f"_{fold}" for fold in range(1, 7)))
    }
    protocol_hashes: dict[str, str] = {}
    with tarfile.open(root / "Protocols.tar", "r:*") as archive:
        for member in _regular_members(archive):
            if member.name.endswith(".m"):
                continue
            if member.name not in expected_protocols:
                raise ValueError("unexpected official protocol file")
            source = archive.extractfile(member)
            if source is None:
                raise ValueError("unreadable official protocol")
            with source:
                payload = source.read()
            parsed = parse_protocol(payload.decode("utf-8-sig"), member.name)
            protocol_hashes[member.name] = hashlib.sha256(payload).hexdigest()
            protocol, fold, split = protocol_scope(member.name)
            eligible: set[str] = set()
            for video_id in records:
                try:
                    _check_membership(video_id, protocol, fold, split)
                except ValueError:
                    continue
                eligible.add(video_id)
            if {row["video_id"] for row in parsed} != eligible:
                raise ValueError("protocol and media inventory membership disagree")
            for row in parsed:
                record = records[row["video_id"]]
                if record["official_split"] not in (None, row["official_split"]):
                    raise ValueError("official protocol splits disagree")
                record["official_split"] = row["official_split"]
                record["protocol_memberships"].append({
                    key: row[key] for key in ("protocol_number", "protocol_fold", "official_split", "label_source", "raw_label_token")
                })
    if set(protocol_hashes) != expected_protocols or any(not record["protocol_memberships"] for record in records.values()):
        raise ValueError("incomplete official protocol coverage")
    for record in records.values():
        record["protocol_memberships"].sort(key=lambda membership: membership["label_source"])
        first = record["protocol_memberships"][0]
        if any(membership["raw_label_token"] != first["raw_label_token"] for membership in record["protocol_memberships"]):
            raise ValueError("raw labels disagree across official protocols")
        record["label_source"] = first["label_source"]
        record["raw_label_token"] = first["raw_label_token"]
    return {
        "version": 1, "dataset": "OULU-NPU", "status": "metadata_reconciled",
        "release_id": release_id, "protocol_id": protocol_id,
        "identity_status": "steward_identifiers_unverified", "acquisition_verified": False,
        "scientific_readiness": False, "no_media_decoding": True, "no_training_tensors": True,
        "full_release_checked": require_full_release, "media_hashes_computed": hash_media,
        "readme_sha256": _sha256(root / "Readme.pdf"), "archive_sha256": archive_hashes,
        "protocol_sha256": dict(sorted(protocol_hashes.items())),
        "label_mapping": LABEL_MAPPING, "label_mapping_hash": LABEL_MAPPING_HASH,
        "videos": [records[video_id] for video_id in sorted(records)],
    }