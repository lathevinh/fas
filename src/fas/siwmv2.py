"""SiW-Mv2 metadata under the accepted Protocol-I intersection amendment."""

from __future__ import annotations

import hashlib
import json
import platform
import re
import stat
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .contracts import SIWMV2_ATTACK_FAMILIES
from .intake import _relative_path

REFERENCE_URL = "https://github.com/CHELSEA234/Multi-domain-learning-FAS"
REFERENCE_COMMIT = "8667dbcd316b38141729c057adf7517fe0602608"
POPULATION_ID = "siwmv2_protocol_i_intersection_v1"
MAPPING_VERSION = "siwmv2_attack_family_v1"
MEMBERSHIP_SHA256 = "47ca2bb8896d5937ff7ea735242dd410f83f8a65e6b5655a6709ef2b4e1fb3ae"
SOURCE_SHA256 = {
    "README.md": "3168b03e638fe52052de70bbeb221352f6e2418124a2e1bf0af59820b857b5d2",
    "dataset.py": "0003fcb00cb08da5ea61cec729fcaedc108cc6ffb72ff977f8c8c3a1d3b97f66",
    "pro_3_text/trainlist_live.txt": "ab808d5e38c0ccc5b5f547d5d2fc68c8ed6b0ab3d758c71e0e114c8c44998d76",
    "pro_3_text/testlist_live.txt": "6b14040b2be41896e7fad242ec743aab10d5bc073ebcbaa3e1575523eb0d3f23",
    "pro_3_text/trainlist_all.txt": "ee10b1d1bd092b8383b6e726503499ca44f219b9bd4c92c3b3b2943aef0cf54b",
    "pro_3_text/testlist_all.txt": "87fc74696498173b2a53d3af656650d3fead3f43fc499b09afd4a7d7a956c0c4",
}
PREFIX_BY_FOLDER = {
    "Live": "Live", "Spoof/Makeup_Cosmetic": "Makeup_Co",
    "Spoof/Makeup_Impersonation": "Makeup_Im", "Spoof/Makeup_Obfuscation": "Makeup_Ob",
    "Spoof/Mannequin": "Mask_Mann", "Spoof/Silicone": "Mask_Silicone",
    "Spoof/Paper": "Paper", "Spoof/Replay": "Replay",
    "Spoof/Partial_FunnyeyeGlasses": "Partial_Funnyeye",
    "Spoof/Partial_PaperGlasses": "Partial_Paperglass", "Spoof/Partial_Eye": "Partial_Eye",
    "Spoof/Partial_Mouth": "Partial_Mouth", "Spoof/Mask_HalfMask": "Mask_Half",
    "Spoof/Mask_PaperMask": "Mask_Paper", "Spoof/Mask_TransparentMask": "Mask_Trans",
}
LABEL_MAPPING = {
    "id": "siwmv2-protocol-i-intersection", "version": 1,
    "authority": "pinned reference lists plus accepted project intersection policy",
    "reference_url": REFERENCE_URL, "reference_commit": REFERENCE_COMMIT,
    "source_sha256": SOURCE_SHA256, "population_id": POPULATION_ID,
    "membership_sha256": MEMBERSHIP_SHA256,
    "attack_mapping_version": MAPPING_VERSION, "attack_family_mapping": SIWMV2_ATTACK_FAMILIES,
    "model_boundary": {"bona_fide": 0, "attack": 1},
    "source_partition": "train", "target_partition": "test",
    "group_unit": "video", "list_repeats": "unique_tokens_no_transaction_or_weight",
    "provider_family_ontology_claimed": False,
}
LABEL_MAPPING_HASH = hashlib.sha256(
    json.dumps(LABEL_MAPPING, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()


def encode_label(binary_label: str) -> int:
    if binary_label not in ("bona_fide", "attack"):
        raise ValueError("unknown canonical label")
    return 0 if binary_label == "bona_fide" else 1


def _media_path(media_relpath: str):
    path = _relative_path(media_relpath)
    if path is None or path.parts[0] != "SiW-Mv2" or path.suffix not in {".mov", ".mp4", ".avi"}:
        raise ValueError("invalid SiW-Mv2 media reference")
    folder = path.parent.as_posix().removeprefix("SiW-Mv2/")
    prefix = PREFIX_BY_FOLDER.get(folder)
    if prefix is None or re.fullmatch(re.escape(prefix) + r"_[1-9][0-9]*", path.stem) is None:
        raise ValueError("unknown SiW-Mv2 media type or video token")
    return path, prefix


def parse_media_path(media_relpath: str, membership: Mapping[str, Any]) -> dict[str, Any]:
    path, prefix = _media_path(media_relpath)
    if not isinstance(membership, Mapping) or membership.get("official_split") not in ("train", "test"):
        raise ValueError("media requires frozen train/test membership")
    split = membership["official_split"]
    live = prefix == "Live"
    expected = {
        "video_id": path.stem, "official_split": split,
        "binary_label": "bona_fide" if live else "attack",
        "reference_attack_type": None if live else prefix,
        "attack_family": None if live else SIWMV2_ATTACK_FAMILIES[prefix],
        "subject_id": None, "group_unit": "video", "group_id": path.stem,
    }
    if dict(membership) != expected:
        raise ValueError("media path differs from frozen metadata or has fabricated identity")
    source = f"{REFERENCE_URL}/blob/{REFERENCE_COMMIT}/source_SiW_Mv2/pro_3_text/{split}list_{'live' if live else 'all'}.txt"
    return {
        "dataset": "SiW-Mv2", **expected, "source_record_id": path.stem,
        "media_relpath": path.as_posix(), "raw_label_token": prefix,
        "label_source": source, "partition_source": source,
        "metadata_authority": "pinned-reference-protocol-i-intersection",
        "population_id": POPULATION_ID, "attack_mapping_version": MAPPING_VERSION,
        "label_mapping_id": LABEL_MAPPING["id"], "label_mapping_version": LABEL_MAPPING["version"],
        "label_mapping_hash": LABEL_MAPPING_HASH,
        "instrument": "none" if live else "unknown", "material": "unknown",
        "session_id": "unknown", "sensor_id": "unknown", "environment": "unknown",
        "participant_identity_verified": False,
        "source_eligible": split == "train", "outer_target_eligible": split == "test",
        "role": None,
    }


def load_population(payload: bytes) -> dict[str, Any]:
    if hashlib.sha256(payload).hexdigest() != MEMBERSHIP_SHA256:
        raise ValueError("membership differs from the accepted frozen bytes")
    value = json.loads(payload)
    if (not isinstance(value, dict) or type(value.get("version")) is not int or value.get("version") != 1
            or value.get("dataset") != "SiW-Mv2" or value.get("population_id") != POPULATION_ID
            or value.get("reference_commit") != REFERENCE_COMMIT or value.get("reference_sha256") != SOURCE_SHA256
            or value.get("mapping_version") != MAPPING_VERSION or value.get("attack_family_mapping") != SIWMV2_ATTACK_FAMILIES):
        raise ValueError("population provenance differs from the accepted amendment")
    return value


def verify_reference_sources(root: Path) -> dict[str, str]:
    resolved = root.resolve()
    verified = {}
    for relative, expected in SOURCE_SHA256.items():
        path = resolved / relative
        if path.is_symlink() or not path.resolve().is_relative_to(resolved) or not path.is_file():
            raise ValueError("missing or unsafe pinned reference source")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != expected:
            raise ValueError("reference differs from pinned bytes")
        verified[relative] = digest
    return verified


def inventory_headers(
    headers: Sequence[dict[str, Any]], *, population_payload: bytes,
    release_id: str, archive_name: str,
) -> dict[str, Any]:
    population = load_population(population_payload)
    if not isinstance(release_id, str) or not release_id.strip():
        raise ValueError("release identifier must be explicit")
    archive = _relative_path(archive_name)
    if archive is None or len(archive.parts) != 1:
        raise ValueError("archive name must be a safe basename")
    eligible = {row["video_id"]: row for row in population["eligible_videos"]}
    excluded = {row["video_id"]: row for row in population["excluded_videos"]}
    missing = {row["video_id"] for row in population["missing_references"]}
    if (len(eligible) != len(population["eligible_videos"]) or len(excluded) != len(population["excluded_videos"])
            or len(missing) != len(population["missing_references"])
            or set(eligible) & set(excluded) or missing & (set(eligible) | set(excluded))):
        raise ValueError("population contains duplicate or overlapping video identities")
    paths = set()
    seen_videos = set()
    videos = []
    excluded_videos = []
    documents = {"SiW-Mv2/README.pdf", "SiW-Mv2/DRA.pdf"}
    directories = {"SiW-Mv2", "SiW-Mv2/Spoof", *("SiW-Mv2/" + folder for folder in PREFIX_BY_FOLDER)}
    expected_fields = {"path", "size", "crc32", "compressed_size", "flags", "external_attr"}
    for header in headers:
        if not isinstance(header, dict) or set(header) != expected_fields:
            raise ValueError("invalid archive header fields")
        if any(type(header[field]) is not int or header[field] < 0 for field in expected_fields - {"path"}):
            raise ValueError("invalid archive header values")
        if header["crc32"] > 0xffffffff or header["external_attr"] > 0xffffffff:
            raise ValueError("invalid archive header integers")
        relative = header["path"]
        if not isinstance(relative, str):
            raise ValueError("invalid archive member path")
        directory = relative.endswith("/")
        path = _relative_path(relative.removesuffix("/") if directory else relative)
        mode = header["external_attr"] >> 16
        if path is None or path.as_posix() in paths:
            raise ValueError("unsafe or duplicate archive member")
        paths.add(path.as_posix())
        if header["flags"] & 1 or stat.S_IFMT(mode) not in (0, stat.S_IFDIR if directory else stat.S_IFREG):
            raise ValueError("encrypted or unsupported archive member")
        if directory:
            if path.as_posix() not in directories:
                raise ValueError("unknown archive directory")
            continue
        if header["size"] == 0:
            raise ValueError("empty archive member")
        if relative in documents:
            continue
        media, prefix = _media_path(relative)
        token = media.stem
        if token in seen_videos:
            raise ValueError("duplicate video token")
        seen_videos.add(token)
        facts = {"media_archive": archive_name, "byte_size": header["size"],
                 "media_sha256": None, "container": None, "codec": None, "duration_ms": None,
                 "fps": None, "frame_count": None, "decode_status": "not_probed"}
        if token in eligible:
            videos.append({**parse_media_path(relative, eligible[token]), **facts, "release_id": release_id})
        elif token in excluded:
            attack_type = None if prefix == "Live" else prefix
            if excluded[token] != {"video_id": token, "reason": "out_of_protocol", "reference_attack_type": attack_type}:
                raise ValueError("excluded video differs from frozen exclusion semantics")
            excluded_videos.append({"dataset": "SiW-Mv2", "video_id": token, "media_relpath": relative,
                                    "reference_attack_type": attack_type, "reason": "out_of_protocol",
                                    "official_split": None, "subject_id": None, "role": None,
                                    "source_eligible": False, "outer_target_eligible": False, **facts})
        else:
            raise ValueError("observed video is outside the frozen inventory")
    if seen_videos != set(eligible) | set(excluded):
        raise ValueError("archive membership differs from frozen video identities")
    header_digest = hashlib.sha256(json.dumps(
        sorted(headers, key=lambda row: row["path"]), sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    if header_digest != population["header_inventory_sha256"]:
        raise ValueError("archive headers differ from the frozen inventory digest")
    return {
        "version": 1, "dataset": "SiW-Mv2", "status": "reference_metadata_reconciled",
        "metadata_authority": "pinned-reference-protocol-i-intersection",
        "release_id": release_id, "identity_status": "steward_identifier_unverified",
        "population_id": POPULATION_ID, "population_sha256_verified": MEMBERSHIP_SHA256,
        "reference_sha256_verified": population["reference_sha256"], "header_inventory_sha256": header_digest,
        "label_mapping": LABEL_MAPPING, "label_mapping_hash": LABEL_MAPPING_HASH,
        "reader_provenance": {"library": "zipfile", "python_version": platform.python_version(), "scope": "central_directory_headers_only"},
        "acquisition_verified": False, "archive_sha256_verified": False, "media_integrity_verified": False,
        "media_decode_verified": False, "participant_identity_verified": False, "scientific_readiness": False,
        "no_media_payload_read": True, "no_model_inference_or_training": True, "roles_assigned": False,
        "videos": sorted(videos, key=lambda row: row["video_id"]),
        "out_of_protocol_videos": sorted(excluded_videos, key=lambda row: row["video_id"]),
        "missing_references": population["missing_references"],
    }