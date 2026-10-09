"""MSU-MFSD metadata from the supplied native README and subject lists."""

from __future__ import annotations

import hashlib
import json
import re
import stat
from collections.abc import Sequence
from typing import Any

from .intake import _relative_path

METADATA_SHA256 = {
    "README.txt": "6e0f2f1ce5d8601fee4f3096e6b300929d0ec259dd947fcf1e08f75080c14497",
    "train_sub_list.txt": "08d55993685dd1bf0a7161a10ce18cf991559358c2c062466fba1f52363436f2",
    "test_sub_list.txt": "87ee61282553af3ed61a4fba9afea5eb7cb7883368bb6fadfe608528d01885bd",
}
ATTACK_TYPES = {"ipad_video": "replay", "iphone_video": "replay", "printed_photo": "print"}
LABEL_MAPPING = {
    "id": "msu-mfsd-native-readme", "version": 1,
    "authority": "supplied release README and official subject lists; acquisition unverified",
    "metadata_sha256": METADATA_SHA256,
    "binary_classes": {"real": "bona_fide", "attack": "attack"},
    "attack_families": ATTACK_TYPES, "model_boundary": {"bona_fide": 0, "attack": 1},
    "subject_namespace": "native client ID, three-digit canonical form, no split offset",
    "group_unit": "subject", "partitions": ["train", "test"],
}
LABEL_MAPPING_HASH = hashlib.sha256(json.dumps(LABEL_MAPPING, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def encode_label(binary_label: str) -> int:
    if binary_label not in ("bona_fide", "attack"):
        raise ValueError("unknown canonical label")
    return int(binary_label == "attack")


def parse_subject_lists(train: str, test: str) -> dict[str, str]:
    subjects = {}
    for split, text in (("train", train), ("test", test)):
        if not isinstance(text, str) or not text.split():
            raise ValueError("empty or invalid native subject list")
        for token in text.split():
            if re.fullmatch(r"[0-9]{2}", token) is None or not 1 <= int(token) <= 55:
                raise ValueError("invalid native subject token")
            subject = f"{int(token):03d}"
            if subject in subjects:
                raise ValueError("duplicate or overlapping subject lists")
            subjects[subject] = split
    return subjects


def parse_media_path(media_relpath: str, subjects: dict[str, str]) -> dict[str, Any]:
    path = _relative_path(media_relpath)
    if path is None or len(path.parts) != 3 or path.parts[0] != "scene01":
        raise ValueError("invalid MSU media path")
    match = re.fullmatch(r"(real|attack)_client([0-9]{3})_(android|laptop)_(SD|HD)(?:_(ipad_video|iphone_video|printed_photo))?_scene01\.(mp4|mov)", path.name)
    if match is None:
        raise ValueError("unknown MSU filename grammar")
    category, subject, camera, resolution, attack_type, extension = match.groups()
    if (path.parts[1] != category or (category == "attack") != (attack_type is not None)
            or extension != ("mp4" if camera == "android" else "mov")
            or not 1 <= int(subject) <= 55 or subjects.get(subject) not in ("train", "test")):
        raise ValueError("inconsistent MSU label, camera or membership")
    subject_id = f"subject-{subject}"
    return {
        "dataset": "MSU-MFSD", "video_id": path.with_suffix("").as_posix(),
        "source_record_id": path.with_suffix("").as_posix(), "subject_id": subject_id,
        "raw_subject_token": subject, "official_split": subjects[subject],
        "partition_source": f"{subjects[subject]}_sub_list.txt", "label_source": "README.txt#sections-3-4",
        "metadata_authority": "supplied-release-readme-and-official-lists",
        "media_relpath": media_relpath, "binary_label": LABEL_MAPPING["binary_classes"][category],
        "raw_label_token": category, "reference_attack_type": attack_type or "none",
        "attack_family": ATTACK_TYPES[attack_type] if attack_type else "none",
        "sensor_id": camera, "resolution_token": resolution, "scenario": "scene01",
        "instrument": {"ipad_video": "iPad Air", "iphone_video": "iPhone 5S", "printed_photo": "A3 printed photo"}.get(attack_type, "none"),
        "material": "paper" if attack_type == "printed_photo" else "unknown",
        "environment": "unknown", "session_id": "unknown", "role": None,
        "group_unit": "subject", "group_id": subject_id,
        "label_mapping_id": LABEL_MAPPING["id"], "label_mapping_version": 1,
        "label_mapping_hash": LABEL_MAPPING_HASH,
    }


def inventory_headers(headers: Sequence[dict[str, Any]], metadata: dict[str, bytes], *, release_id: str, require_full_release: bool = True) -> dict[str, Any]:
    if not isinstance(release_id, str) or not release_id.strip() or type(require_full_release) is not bool:
        raise ValueError("explicit release identifier and boolean completeness required")
    if set(metadata) != set(METADATA_SHA256):
        raise ValueError("missing native metadata")
    hashes = {name: hashlib.sha256(payload).hexdigest() for name, payload in metadata.items()}
    if hashes != METADATA_SHA256:
        raise ValueError("native metadata bytes changed")
    subjects = parse_subject_lists(metadata["train_sub_list.txt"].decode("utf-8-sig"), metadata["test_sub_list.txt"].decode("utf-8-sig"))
    if require_full_release and (sum(split == "train" for split in subjects.values()), sum(split == "test" for split in subjects.values())) != (15, 20):
        raise ValueError("native release subject counts differ")
    paths, records, sidecars = set(), {}, set()
    for header in headers:
        if not isinstance(header, dict) or set(header) != {"path", "size", "crc32", "compressed_size", "flags", "external_attr"}:
            raise ValueError("invalid inner header fields")
        if any(type(header[field]) is not int or header[field] < 0 for field in ("size", "crc32", "compressed_size", "flags", "external_attr")):
            raise ValueError("invalid numeric header")
        if header["crc32"] > 0xFFFFFFFF or header["external_attr"] > 0xFFFFFFFF:
            raise ValueError("invalid header bounds")
        name = header["path"]
        directory = isinstance(name, str) and name.endswith("/")
        path = _relative_path(name.removesuffix("/") if directory else name)
        if path is None or path.as_posix() in paths:
            raise ValueError("unsafe or duplicate member")
        paths.add(path.as_posix())
        mode = stat.S_IFMT(header["external_attr"] >> 16)
        if header["flags"] & 1 or mode not in (0, stat.S_IFDIR if directory else stat.S_IFREG):
            raise ValueError("encrypted or unsupported member")
        if directory:
            if path.parts[0] == "ffmpeg" or path.as_posix() in {"scene01", "scene01/real", "scene01/attack"}:
                continue
            raise ValueError("unknown directory")
        if header["size"] == 0:
            raise ValueError("empty file")
        if name in METADATA_SHA256 or name in {"DecFrames.m", "DecFrames_attack_scene01.m", "DecFrames_real_scene01.m"} or path.parts[0] == "ffmpeg":
            continue
        if path.suffix == ".face":
            if len(path.parts) != 3 or path.parts[0] != "scene01" or path.parts[1] not in ("real", "attack"):
                raise ValueError("invalid face sidecar path")
            sidecars.add(path.with_suffix("").as_posix())
            continue
        row = parse_media_path(name, subjects)
        records[row["video_id"]] = {**row, "release_id": release_id, "byte_size": header["size"], "archive_header": header,
            "media_sha256": None, "container": None, "codec": None, "duration_ms": None,
            "fps": None, "frame_count": None, "decode_status": "not_probed"}
    expected = {(camera, attack_type) for camera in ("android", "laptop") for attack_type in ("none", *ATTACK_TYPES)}
    for subject in subjects:
        rows = [row for row in records.values() if row["raw_subject_token"] == subject]
        if len(rows) != 8 or {(row["sensor_id"], row["reference_attack_type"]) for row in rows} != expected:
            raise ValueError("missing or duplicated native subject video combinations")
    if set(records) != sidecars or not set(METADATA_SHA256).issubset(paths):
        raise ValueError("missing metadata or nonmatching face sidecars")
    return {"version": 1, "dataset": "MSU-MFSD", "status": "native_metadata_reconciled", "release_id": release_id,
        "metadata_authority": "supplied-release-readme-and-official-lists", "metadata_sha256_verified": hashes,
        "label_mapping": LABEL_MAPPING, "label_mapping_hash": LABEL_MAPPING_HASH, "full_native_universe_checked": require_full_release,
        "header_inventory_sha256": hashlib.sha256(json.dumps(sorted(headers, key=lambda row: row["path"]), sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "acquisition_verified": False, "archive_integrity_verified": False, "media_integrity_verified": False,
        "media_decode_verified": False, "participant_identity_verified": False, "scientific_readiness": False,
        "roles_assigned": False, "no_video_entry_opened": True, "no_model_inference_or_training": True,
        "face_annotations_used": False, "videos": [records[key] for key in sorted(records)]}