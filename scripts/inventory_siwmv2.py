#!/usr/bin/env python3
"""Write a private SiW-Mv2 metadata inventory without reading video payloads."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.siwmv2 import inventory_headers, load_population, verify_reference_sources


def read_headers(archive_path: Path) -> list[dict]:
    with zipfile.ZipFile(archive_path) as archive:
        return [{"path": entry.filename, "size": entry.file_size, "crc32": entry.CRC,
                 "compressed_size": entry.compress_size, "flags": entry.flag_bits,
                 "external_attr": entry.external_attr} for entry in archive.infolist()]


def redacted_summary(result: dict, inventory_sha256: str) -> dict:
    videos = result["videos"]
    coverage = {}
    for attack_type in result["label_mapping"]["attack_family_mapping"]:
        coverage[attack_type] = {split: sum(row["reference_attack_type"] == attack_type and row["official_split"] == split
                                           for row in videos) for split in ("train", "test")}
    return {
        "version": 1, "dataset": "SiW-Mv2", "status": result["status"],
        "scope": "reference-derived metadata only; not acquisition, media audit, roles or scientific readiness",
        "metadata_authority": result["metadata_authority"], "inventory_sha256": inventory_sha256,
        "population_id": result["population_id"], "population_sha256_verified": result["population_sha256_verified"],
        "header_inventory_sha256": result["header_inventory_sha256"],
        "reference_sha256_verified": result["reference_sha256_verified"],
        "label_mapping": result["label_mapping"], "label_mapping_hash": result["label_mapping_hash"],
        "reader_provenance": result["reader_provenance"],
        "eligible_videos": len(videos), "out_of_protocol_videos": len(result["out_of_protocol_videos"]),
        "missing_references": len(result["missing_references"]),
        "partitions": {split: {label: sum(row["official_split"] == split and row["binary_label"] == label for row in videos)
                               for label in ("bona_fide", "attack")} for split in ("train", "test")},
        "reference_attack_type_coverage": coverage,
        **{field: result[field] for field in (
            "acquisition_verified", "archive_sha256_verified", "media_integrity_verified", "media_decode_verified",
            "participant_identity_verified", "scientific_readiness", "no_media_payload_read", "no_model_inference_or_training", "roles_assigned",
        )},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--reference-root", type=Path, required=True, help="private pinned reference files outside Git")
    parser.add_argument("--population", type=Path, required=True, help="accepted private exact-ID intersection record")
    parser.add_argument("--release-id", required=True, help="explicit steward identifier, not verified acquisition identity")
    parser.add_argument("--unverified-local", action="store_true", required=True)
    parser.add_argument("--out", type=Path, required=True, help="new immutable private inventory outside Git")
    args = parser.parse_args()
    try:
        archive = args.archive.resolve()
        references = args.reference_root.resolve()
        population = args.population.resolve()
        output = args.out.resolve()
        if not archive.is_file() or not references.is_dir() or not population.is_file():
            raise ValueError("private inputs must exist")
        if args.population.is_symlink() or population.is_relative_to(ROOT) or references.is_relative_to(ROOT) or ROOT.is_relative_to(references):
            raise ValueError("reference and population inputs must be outside Git")
        if archive.is_relative_to(ROOT) and archive != (ROOT / "SiW" / "SiW-Mv2.zip").resolve():
            raise ValueError("only the supplied ignored archive is allowed inside the repository")
        if (args.out.exists() or args.out.is_symlink() or output.is_relative_to(ROOT)
                or output.is_relative_to(archive.parent) or output.is_relative_to(references)
                or output == population):
            raise ValueError("output must be new, private and separate from inputs")
        source_hashes = verify_reference_sources(references)
        payload = population.read_bytes()
        load_population(payload)
    except (ValueError, OSError, RuntimeError, UnicodeError):
        print("SIW-MV2 INVENTORY FAILED: invalid private inputs/output or reference/population provenance", file=sys.stderr)
        return 2
    try:
        result = inventory_headers(read_headers(archive), population_payload=payload,
                                   release_id=args.release_id, archive_name=archive.name)
        if result["reference_sha256_verified"] != source_hashes:
            raise ValueError("reference provenance mismatch")
    except (ValueError, OSError, RuntimeError, UnicodeError, KeyError, zipfile.BadZipFile):
        print(json.dumps({"status": "blocked", "errors": ["unsafe or frozen-inventory-incompatible archive metadata"]}))
        return 1
    try:
        write_immutable_record(output, result)
        digest = hashlib.sha256(output.read_bytes()).hexdigest()
    except (ValueError, OSError, RuntimeError):
        print("SIW-MV2 INVENTORY FAILED: private output unavailable or already exists", file=sys.stderr)
        return 2
    print(json.dumps(redacted_summary(result, digest), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())