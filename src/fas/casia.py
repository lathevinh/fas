"""CASIA-FASD metadata rules from a pinned Bob reference, not owner certification."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from .intake import _relative_path

BOB_REPOSITORY = "https://github.com/183amir/bob.db.casia_fasd"
BOB_COMMIT = "5320dac3101de913874242f56c5baa5961d2c13b"
BOB_SOURCE_SHA256 = {
    "bob/db/casia_fasd/__init__.py": "c94996cf187279c2ca2a01eba277a088de92680471ff5edcde5e0ce42026dd1d",
    "bob/db/casia_fasd/models.py": "270c0933d6d517e4977683f86a50e658954b05baa4967a49c13faa7639fd227a",
}
REFERENCE_CODES = {
    "1": ("real", "normal"), "2": ("real", "low"), "HR_1": ("real", "high"),
    "3": ("warped", "normal"), "4": ("warped", "low"), "HR_2": ("warped", "high"),
    "5": ("cut", "normal"), "6": ("cut", "low"), "HR_3": ("cut", "high"),
    "7": ("video", "normal"), "8": ("video", "low"), "HR_4": ("video", "high"),
}
LABEL_MAPPING = {
    "id": "casia-fasd-bob-reference", "version": 1,
    "authority": "Bob/Idiap reference; not CASIA-owner release documentation",
    "repository": BOB_REPOSITORY, "commit": BOB_COMMIT,
    "source_sha256": BOB_SOURCE_SHA256, "reference_codes": REFERENCE_CODES,
    "binary_classes": {"real": "bona_fide", "warped": "attack", "cut": "attack", "video": "attack"},
    "attack_families": {"real": "none", "warped": "print", "cut": "print", "video": "replay"},
    "subject_namespace": {"train_release": "raw subject 1-20", "test_release": "raw subject 1-30 plus 20"},
    "partitions": {"train_release": "train", "test_release": "test"},
    "model_boundary": {"bona_fide": 0, "attack": 1},
    "bob_cross_validation_adopted": False,
}
LABEL_MAPPING_HASH = hashlib.sha256(
    json.dumps(LABEL_MAPPING, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()
LABEL_SOURCE = f"{BOB_REPOSITORY}/blob/{BOB_COMMIT}/bob/db/casia_fasd/__init__.py"
RAR_READER = {
    "distribution": "rarfile", "version": "4.2",
    "wheel_sha256": "8757e1e3757e32962e229cab2432efc1f15f210823cc96ccba0f6a39d17370c9",
    "scope": "RAR header utility, not installed into the locked model stack",
}


def encode_label(binary_label: str) -> int:
    if binary_label not in ("bona_fide", "attack"):
        raise ValueError("unknown canonical label")
    return 0 if binary_label == "bona_fide" else 1


def parse_media_path(media_relpath: str) -> dict[str, Any]:
    path = _relative_path(media_relpath)
    if path is None or len(path.parts) != 3 or path.suffix != ".avi":
        raise ValueError("invalid CASIA media reference")
    partition, subject_token = path.parts[:2]
    if partition not in ("train_release", "test_release"):
        raise ValueError("unknown CASIA reference partition")
    if re.fullmatch(r"[1-9]|[12][0-9]|30", subject_token) is None:
        raise ValueError("invalid CASIA subject identifier")
    subject = int(subject_token)
    if partition == "train_release" and subject > 20:
        raise ValueError("subject outside Bob reference partition")
    token = path.stem
    if token not in REFERENCE_CODES:
        raise ValueError("unknown CASIA filename label code")
    reference_class, quality = REFERENCE_CODES[token]
    split = LABEL_MAPPING["partitions"][partition]
    canonical_subject = subject if split == "train" else subject + 20
    return {
        "dataset": "CASIA-FASD", "source_record_id": path.with_suffix("").as_posix(),
        "video_id": path.with_suffix("").as_posix(), "subject_id": f"subject-{canonical_subject:02d}",
        "raw_subject_token": subject_token, "official_split": split,
        "partition_source": LABEL_SOURCE, "metadata_authority": "bob-reference",
        "binary_label": LABEL_MAPPING["binary_classes"][reference_class],
        "attack_family": LABEL_MAPPING["attack_families"][reference_class],
        "reference_attack_type": "none" if reference_class == "real" else reference_class,
        "quality": quality, "instrument": "none" if reference_class == "real" else "unknown",
        "material": "unknown", "session_id": "unknown", "sensor_id": "unknown", "environment": "unknown",
        "media_relpath": media_relpath, "label_source": LABEL_SOURCE, "raw_label_token": token,
        "label_mapping_id": LABEL_MAPPING["id"], "label_mapping_version": LABEL_MAPPING["version"],
        "label_mapping_hash": LABEL_MAPPING_HASH,
    }


def verify_bob_sources(source_root: Path) -> dict[str, str]:
    root = source_root.resolve()
    verified: dict[str, str] = {}
    for relative, expected in BOB_SOURCE_SHA256.items():
        path = (root / Path(relative).name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError("missing or unsafe pinned Bob source")
        with path.open("rb") as source:
            actual = hashlib.file_digest(source, "sha256").hexdigest()
        if actual != expected:
            raise ValueError("Bob source differs from pinned bytes")
        verified[relative] = actual
    return verified


def inventory_headers(
    headers: Sequence[dict[str, Any]], *, release_id: str, protocol_id: str,
    archive_name: str, require_full_reference: bool = False,
) -> dict[str, Any]:
    for identifier in (release_id, protocol_id):
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("release and protocol identifiers must be explicit")
    archive = _relative_path(archive_name)
    if archive is None or len(archive.parts) != 1:
        raise ValueError("archive name must be a safe basename")
    if type(require_full_reference) is not bool:
        raise ValueError("full-reference flag must be boolean")
    records: dict[str, dict[str, Any]] = {}
    paths: set[str] = set()
    subjects: dict[tuple[str, str], set[str]] = {}
    for header in headers:
        if not isinstance(header, dict) or set(header) != {"relpath", "byte_size", "kind", "encrypted"}:
            raise ValueError("invalid archive header fields")
        if header["kind"] not in ("file", "directory") or type(header["encrypted"]) is not bool or header["encrypted"]:
            raise ValueError("unsupported or encrypted archive member")
        if type(header["byte_size"]) is not int or header["byte_size"] < 0:
            raise ValueError("invalid archive member byte size")
        relative = header["relpath"]
        if header["kind"] == "directory" and isinstance(relative, str):
            relative = relative.removesuffix("/")
        path = _relative_path(relative)
        if path is None:
            raise ValueError("unsafe archive member path")
        if path.as_posix() in paths:
            raise ValueError("duplicate archive member path")
        paths.add(path.as_posix())
        if header["kind"] == "directory":
            if len(path.parts) == 1 and path.parts[0] in ("train_release", "test_release"):
                continue
            if len(path.parts) != 2:
                raise ValueError("unexpected archive directory")
            parse_media_path(f"{path.as_posix()}/1.avi")
            continue
        if header["byte_size"] == 0:
            raise ValueError("empty media member")
        metadata = parse_media_path(path.as_posix())
        key = (path.parts[0], metadata["raw_subject_token"])
        subjects.setdefault(key, set()).add(metadata["raw_label_token"])
        records[path.as_posix()] = {
            **metadata, "release_id": release_id, "protocol_id": protocol_id,
            "media_archive": archive_name, "byte_size": header["byte_size"],
            "media_sha256": None, "container": None, "codec": None, "duration_ms": None,
            "fps": None, "frame_count": None, "decode_status": "not_probed",
        }
    if not records or any(tokens != set(REFERENCE_CODES) for tokens in subjects.values()):
        raise ValueError("observed subjects must contain all twelve reference codes")
    if {partition for partition, subject in subjects} != {"train_release", "test_release"}:
        raise ValueError("both reference partitions must be present")
    expected = {
        f"{partition}/{subject}/{token}.avi"
        for partition, identifiers in (("train_release", range(1, 21)), ("test_release", range(1, 31)))
        for subject in identifiers for token in REFERENCE_CODES
    }
    if require_full_reference and set(records) != expected:
        raise ValueError("archive differs from full Bob reference membership")
    return {
        "version": 1, "dataset": "CASIA-FASD", "status": "reference_metadata_reconciled",
        "release_id": release_id, "protocol_id": protocol_id,
        "identity_status": "steward_identifiers_unverified", "metadata_authority": "bob-reference",
        "acquisition_verified": False, "owner_schema_certified": False, "scientific_readiness": False,
        "no_media_decoding": True, "no_training_tensors": True, "media_hashes_computed": False,
        "full_reference_universe_checked": require_full_reference,
        "bob_cross_validation_adopted": False, "label_mapping": LABEL_MAPPING,
        "label_mapping_hash": LABEL_MAPPING_HASH, "reader_provenance": RAR_READER,
        "videos": [records[path] for path in sorted(records)],
    }