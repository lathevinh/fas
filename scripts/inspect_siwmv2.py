#!/usr/bin/env python3
"""Inspect SiW-Mv2 headers and pinned Protocol I lists without accepting the dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.contracts import SIWMV2_ATTACK_FAMILIES

REFERENCE_COMMIT = "8667dbcd316b38141729c057adf7517fe0602608"
REFERENCE_URL = "https://github.com/CHELSEA234/Multi-domain-learning-FAS"
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


def load_sources(root: Path) -> dict[str, bytes]:
    resolved = root.resolve()
    if not resolved.is_dir() or resolved.is_relative_to(ROOT):
        raise ValueError("reference cache must be private and outside the repository")
    payloads = {}
    for relative, expected in SOURCE_SHA256.items():
        path = resolved / relative
        if path.is_symlink() or not path.resolve().is_relative_to(resolved):
            raise ValueError("unsafe reference source")
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != expected:
            raise ValueError("reference differs from pinned bytes")
        payloads[relative] = payload
    return payloads


def _tokens(payload: bytes, live: bool) -> list[str]:
    tokens = payload.decode("utf-8").splitlines()
    allowed = {"Live"} if live else set(PREFIX_BY_FOLDER.values()) - {"Live"}
    if not tokens:
        raise ValueError("empty protocol list")
    for token in tokens:
        prefix, separator, number = token.rpartition("_")
        if not separator or prefix not in allowed or not re.fullmatch(r"[1-9][0-9]*", number):
            raise ValueError("invalid protocol token")
    return tokens


def inspect_headers(entries: list[zipfile.ZipInfo], sources: dict[str, bytes]) -> dict:
    seen_paths = set()
    media_tokens = set()
    groups = Counter()
    extensions = Counter()
    headers = []
    directories = {"SiW-Mv2", "SiW-Mv2/Spoof", *("SiW-Mv2/" + folder for folder in PREFIX_BY_FOLDER)}
    documents = {"SiW-Mv2/README.pdf", "SiW-Mv2/DRA.pdf"}
    document_count = 0
    for entry in entries:
        name = entry.filename
        normalized = name[:-1] if entry.is_dir() else name
        parts = normalized.split("/")
        if any(part in {"", ".", ".."} for part in parts) or any(char in name for char in ("\\", "\x00", ":")):
            raise ValueError("unsafe member path")
        if normalized in seen_paths:
            raise ValueError("duplicate member path")
        seen_paths.add(normalized)
        mode = entry.external_attr >> 16
        if entry.flag_bits & 1 or stat.S_ISLNK(mode) or (stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR)):
            raise ValueError("encrypted or unsupported member")
        if entry.is_dir():
            if normalized not in directories:
                raise ValueError("unknown directory")
        elif name in documents:
            if entry.file_size <= 0:
                raise ValueError("empty document")
            document_count += 1
        else:
            path = PurePosixPath(name)
            folder = str(path.parent).removeprefix("SiW-Mv2/")
            prefix = PREFIX_BY_FOLDER.get(folder)
            if not name.startswith("SiW-Mv2/") or prefix is None or path.suffix not in {".mov", ".mp4", ".avi"}:
                raise ValueError("unknown media member")
            if not re.fullmatch(re.escape(prefix) + r"_[1-9][0-9]*", path.stem) or entry.file_size <= 0:
                raise ValueError("invalid video token or empty media")
            if path.stem in media_tokens:
                raise ValueError("duplicate video token")
            media_tokens.add(path.stem)
            groups[folder] += 1
            extensions[path.suffix] += 1
        headers.append({"path": name, "size": entry.file_size, "crc32": entry.CRC,
                        "compressed_size": entry.compress_size, "flags": entry.flag_bits,
                        "external_attr": entry.external_attr})
    if not media_tokens:
        raise ValueError("no media headers")
    lists = {}
    for category in ("live", "all"):
        for split in ("train", "test"):
            relative = f"pro_3_text/{split}list_{category}.txt"
            lists[relative] = _tokens(sources[relative], live=category == "live")
    list_counts = {}
    for relative, tokens in lists.items():
        unique = set(tokens)
        list_counts[relative] = {"rows": len(tokens), "unique_tokens": len(unique),
                                "balancing_repeat_rows": len(tokens) - len(unique),
                                "listed_missing_from_archive": len(unique - media_tokens)}
    reconciliation = {}
    for category in ("live", "all"):
        train = set(lists[f"pro_3_text/trainlist_{category}.txt"])
        test = set(lists[f"pro_3_text/testlist_{category}.txt"])
        observed = {token for token in media_tokens if token.startswith("Live_") == (category == "live")}
        reconciliation[category] = {
            "train_test_video_token_overlap": len(train & test),
            "observed_unlisted": len(observed - (train | test)),
            "listed_unobserved": len((train | test) - observed),
            "observed_train": len(train & observed), "observed_test": len(test & observed),
        }
    live_count = groups["Live"]
    counts_match = live_count == 785 and len(media_tokens) - live_count == 915 and document_count == 2
    partitions_match = all(not row[key] for row in reconciliation.values()
                           for key in ("train_test_video_token_overlap", "observed_unlisted", "listed_unobserved"))
    blockers = ["subject/source-identity mapping unavailable; video tokens must not be treated as subjects",
                "authorized acquisition receipt and archive/media integrity/decode audit remain unverified"]
    if not counts_match:
        blockers.append("headers do not match README release counts")
    if not partitions_match:
        blockers.append("pinned Protocol I lists do not reconcile exactly with archive video tokens")
    payload = json.dumps(sorted(headers, key=lambda row: row["path"]), sort_keys=True, separators=(",", ":"))
    return {
        "version": 1, "dataset": "SiW-Mv2", "status": "blocked",
        "scope": "redacted header/partition prerequisites only; not an accepted metadata adapter",
        "reference_url": REFERENCE_URL, "reference_commit": REFERENCE_COMMIT,
        "reference_sha256": {name: hashlib.sha256(value).hexdigest() for name, value in sorted(sources.items())},
        "header_inventory_sha256": hashlib.sha256(payload.encode()).hexdigest(),
        "header_members": len(entries), "document_headers": document_count,
        "video_headers": len(media_tokens), "live_video_headers": live_count,
        "spoof_video_headers": len(media_tokens) - live_count,
        "attack_folder_counts": dict(sorted((name, count) for name, count in groups.items() if name != "Live")),
        "media_extensions": dict(sorted(extensions.items())),
        "readme_header_counts_match": counts_match, "protocol_i_lists": list_counts,
        "protocol_i_reconciliation": reconciliation, "protocol_i_exact_match": partitions_match,
        "subject_identity_verified": False, "acquisition_verified": False,
        "archive_sha256_verified": False, "media_integrity_verified": False,
        "media_decode_verified": False, "scientific_readiness": False,
        "core_replacement_activated": False, "no_media_payload_read": True,
        "no_model_inference_or_training": True, "blockers": blockers,
    }


def build_intersection_record(entries: list[zipfile.ZipInfo], sources: dict[str, bytes]) -> dict:
    inspected = inspect_headers(entries, sources)
    if any(row["train_test_video_token_overlap"] for row in inspected["protocol_i_reconciliation"].values()):
        raise ValueError("overlapping protocol membership cannot define a population")
    observed = {PurePosixPath(entry.filename).stem for entry in entries
                if not entry.is_dir() and PurePosixPath(entry.filename).suffix in {".mov", ".mp4", ".avi"}}
    eligible = []
    missing = []
    listed = set()
    for split in ("train", "test"):
        for category in ("live", "all"):
            tokens = set(_tokens(sources[f"pro_3_text/{split}list_{category}.txt"], category == "live"))
            listed.update(tokens)
            for token in sorted(tokens):
                if token not in observed:
                    missing.append({"video_id": token, "official_split": split, "reason": "listed_missing_from_archive"})
                    continue
                attack_type = None if category == "live" else token.rpartition("_")[0]
                eligible.append({"video_id": token, "official_split": split,
                                 "binary_label": "bona_fide" if category == "live" else "attack",
                                 "reference_attack_type": attack_type,
                                 "attack_family": None if attack_type is None else SIWMV2_ATTACK_FAMILIES[attack_type],
                                 "subject_id": None, "group_unit": "video", "group_id": token})
    excluded = [{"video_id": token, "reason": "out_of_protocol",
                 "reference_attack_type": None if token.startswith("Live_") else token.rpartition("_")[0]}
                for token in sorted(observed - listed)]
    return {"version": 1, "population_id": "siwmv2_protocol_i_intersection_v1",
            "dataset": "SiW-Mv2", "scope": "header/list population definition; not media audit or canonical roles",
            "reference_commit": REFERENCE_COMMIT, "reference_sha256": inspected["reference_sha256"],
            "header_inventory_sha256": inspected["header_inventory_sha256"],
            "mapping_version": "siwmv2_attack_family_v1", "attack_family_mapping": SIWMV2_ATTACK_FAMILIES,
            "eligible_videos": sorted(eligible, key=lambda row: row["video_id"]),
            "excluded_videos": excluded, "missing_references": sorted(missing, key=lambda row: row["video_id"])}


def intersection_summary(record: dict) -> dict:
    rows = record["eligible_videos"]
    coverage = {}
    for attack_type in SIWMV2_ATTACK_FAMILIES:
        counts = {split: sum(row["reference_attack_type"] == attack_type and row["official_split"] == split
                             for row in rows) for split in ("train", "test")}
        coverage[attack_type] = {**counts, "total": sum(counts.values()),
                                 "excluded": sum(row["reference_attack_type"] == attack_type
                                                 for row in record["excluded_videos"])}
    def token_hash(tokens: list[str]) -> str:
        return hashlib.sha256(("\n".join(sorted(tokens)) + "\n").encode()).hexdigest()
    payload = json.dumps(record, indent=2, sort_keys=True) + "\n"
    return {"version": 1, "population_id": record["population_id"],
            "private_membership_sha256": hashlib.sha256(payload.encode()).hexdigest(),
            "reference_commit": record["reference_commit"], "reference_sha256": record["reference_sha256"],
            "header_inventory_sha256": record["header_inventory_sha256"],
            "mapping_version": record["mapping_version"], "attack_family_mapping": record["attack_family_mapping"],
            "partitions": {split: {"bona_fide": sum(row["binary_label"] == "bona_fide" and row["official_split"] == split for row in rows),
                                    "attack": sum(row["binary_label"] == "attack" and row["official_split"] == split for row in rows),
                                    "eligible_ids_sha256": token_hash([row["video_id"] for row in rows if row["official_split"] == split])}
                           for split in ("train", "test")},
            "eligible_total": len(rows), "excluded_total": len(record["excluded_videos"]),
            "missing_reference_total": len(record["missing_references"]), "reference_attack_type_coverage": coverage,
            "all_14_types_in_each_partition": all(row["train"] > 0 and row["test"] > 0 for row in coverage.values()),
            "no_media_payload_read": True, "no_model_inference_or_training": True,
            "scientific_readiness": False}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="new immutable redacted JSON report")
    parser.add_argument("--intersection-private-out", type=Path, help="freeze exact intersection IDs outside Git; does not audit media")
    args = parser.parse_args()
    try:
        archive_path = args.archive.resolve()
        output = args.out.resolve()
        if not archive_path.is_file() or output == archive_path or output.exists():
            raise ValueError("invalid input/output")
        if output.is_relative_to(archive_path.parent) or output.is_relative_to(args.reference_root.resolve()):
            raise ValueError("output overlaps private inputs")
        sources = load_sources(args.reference_root)
        with zipfile.ZipFile(archive_path) as archive:
            entries = archive.infolist()
        report = inspect_headers(entries, sources)
        if args.intersection_private_out is not None:
            if not report["readme_header_counts_match"]:
                raise ValueError("archive differs from reviewed release counts")
            private_output = args.intersection_private_out.resolve()
            if (private_output.exists() or private_output == output or private_output.is_relative_to(ROOT)
                    or private_output.is_relative_to(archive_path.parent)
                    or private_output.is_relative_to(args.reference_root.resolve())):
                raise ValueError("intersection IDs must be new and outside Git and input directories")
            record = build_intersection_record(entries, sources)
            report = intersection_summary(record)
            if (report["eligible_total"] != 1680 or report["excluded_total"] != 20
                    or report["missing_reference_total"] != 11 or not report["all_14_types_in_each_partition"]
                    or {split: (row["bona_fide"], row["attack"]) for split, row in report["partitions"].items()}
                    != {"train": (524, 533), "test": (261, 362)}):
                raise ValueError("population differs from the reviewed intersection")
            write_immutable_record(private_output, record)
        else:
            report["archive_byte_size"] = archive_path.stat().st_size
        write_immutable_record(output, report)
    except (ValueError, OSError, RuntimeError, UnicodeError, KeyError, zipfile.BadZipFile):
        print("SIW-MV2 INSPECTION FAILED: invalid headers, reference provenance or output", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if args.intersection_private_out is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())