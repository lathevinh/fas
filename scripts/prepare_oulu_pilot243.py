#!/usr/bin/env python3
"""Bounded Review242 pilot; historical preparation helpers remain unchanged."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import selectors
import signal
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import cv2
import numpy as np

from fas.freeze import write_immutable_record
from fas.lineage import decoded_tokens
from fas.oulu import _sha256
from fas.visual import png_bytes
from import_oulu_categorical_batch08 import strict_json
from prepare_oulu_owner_review import private_output
from verify_oulu_archive_guard_batch09 import read_verified_json, verified_archive_identities

MIB = 1024 * 1024
CAPS = {"whole_seconds": 1800, "decoder_seconds": 180, "rss_bytes": 2048 * MIB,
        "output_bytes": 256 * MIB, "temporary_bytes": 128 * MIB, "reserve_bytes": 640 * MIB}
AUTHORITY = {
    "docs/242-review-doc241-oulu-protocol-and-streamlined-workflow.md": "e1ea4314f3c80b7b432a89ab2c39a0c504b77ee6626ead46e3a78e89ca009798",
    "docs/241-review-response-doc240-oulu-residual-cross-role-protocol.md": "7e4464fb57222f07aca2edcfee767dbae455b4566301f33d82642781c3f1e2a1",
    "results/phase1/oulu-cross-role-protocol241-v1.json": "0aa0d6a4ade1de8a3eb99e90bac1c224c1c4768050e1589c2f99c667af970556",
}
PROVENANCE_SHA = "fa35cd8ed4281c6d9848b21374de9cd7d5b9f992044002b7d936437dc6b34c29"
MEMBERSHIP_SHA = "e4daafcc78a35b9a65f5fb07d330240aa908f94096c8daac67a2cf84e244c595"
RANKS_SHA = "b0dbeefdb0f5081ae91422ac9f321480380039999854b78cd4fa19239b876cff"
SELECTION_SHA = "8c6691a416ec0a3ceba7db837476651334414554abe87a79afd414d963a51155"


def compact_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def stream_frames(path: Path, media: dict, consume, *, timeout: float = 180, command: list[str] | None = None) -> None:
    tokens = decoded_tokens(media)
    if len({token[:2] for token in tokens}) != 1:
        raise ValueError("variable dimensions")
    width, height = tokens[0][:2]
    size = width * height * 3
    deadline = time.monotonic() + timeout
    command = command or ["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-err_detect", "explode",
                          "-threads", "1", "-i", str(path), "-map", "0:v:0", "-an", "-sn", "-dn",
                          "-pix_fmt", "rgb24", "-threads", "1", "-vsync", "0", "-f", "rawvideo", "-"]
    with tempfile.TemporaryFile() as errors, selectors.DefaultSelector() as selector:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=errors, bufsize=0)
        selector.register(process.stdout, selectors.EVENT_READ)

        def read_exact(count: int) -> bytes:
            payload = bytearray()
            while len(payload) < count:
                remaining = deadline - time.monotonic()
                if remaining <= 0 or not selector.select(remaining):
                    raise TimeoutError("absolute decoder deadline")
                if os.fstat(errors.fileno()).st_size > CAPS["temporary_bytes"]:
                    raise ValueError("decoder stderr resource cap")
                block = os.read(process.stdout.fileno(), min(count - len(payload), MIB))
                if not block:
                    break
                payload.extend(block)
            return bytes(payload)

        try:
            for order, token in enumerate(tokens):
                payload = read_exact(size)
                if len(payload) != size or hashlib.sha256(payload).hexdigest() != token[2]:
                    raise ValueError("RGB identity/count mismatch")
                consume(order, np.frombuffer(payload, np.uint8).reshape(height, width, 3))
            if read_exact(1):
                raise ValueError("extra RGB bytes")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("absolute decoder deadline")
            if process.wait(timeout=remaining) or os.fstat(errors.fileno()).st_size:
                raise ValueError("strict decoder exit/stderr")
        finally:
            if process.poll() is None:
                process.kill()
            process.wait()
            process.stdout.close()


def gallery(frames: list[np.ndarray], start: int) -> np.ndarray:
    if not frames or type(start) is not int or start < 0 or start % 16 or start >= len(frames):
        raise ValueError("invalid chronological gallery start")
    height, width = frames[0].shape[:2]
    result = np.full((4 * (height + 28), 4 * width, 3), 255, np.uint8)
    for slot, frame in enumerate(frames[start:start + 16]):
        if frame.shape != frames[0].shape:
            raise ValueError("gallery dimensions drift")
        top, left = (slot // 4) * (height + 28), (slot % 4) * width
        cv2.putText(result, f"n={start + slot}", (left + 4, top + 19), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
        result[top + 28:top + 28 + height, left:left + width] = frame
    return result


def checked_member(member, expected: dict) -> None:
    name = PurePosixPath(member.name)
    if not member.isfile() or name.is_absolute() or ".." in name.parts or "\\" in member.name or member.name != expected["media_relpath"] or member.size != expected["byte_size"]:
        raise ValueError("unsafe or drifting selected tar member")


def check_bindings(bindings: dict) -> None:
    for name, digest in bindings.items():
        path = Path(name)
        if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode) or _sha256(path) != digest:
            raise ValueError("bound source drift")


def selected_sources(preflight: dict) -> tuple[dict, list[dict], list[dict]]:
    if preflight.get("checkpoint") != 243 or type(preflight["checkpoint"]) is not int or preflight.get("caps") != CAPS or preflight.get("review242_consolidated_pilot_authorized") is not True:
        raise ValueError("explicit fixed Review242 pilot authority required")
    for field, expected in (("membership_sha256", MEMBERSHIP_SHA), ("rank_list_sha256", RANKS_SHA), ("selected_pair_sha256", SELECTION_SHA)):
        if preflight.get(field) != expected:
            raise ValueError("fixed accepted241 commitment required")
    for name, digest in AUTHORITY.items():
        if preflight["source_sha256"].get(str(ROOT / name)) != digest:
            raise ValueError("fixed accepted241/Review242 authority required")
    if preflight["source_sha256"].get(preflight["provenance_path"]) != PROVENANCE_SHA or preflight["source_sha256"].get(str(Path(__file__))) != _sha256(Path(__file__)):
        raise ValueError("fixed provenance and runner binding required")
    check_bindings(preflight["source_sha256"])
    provenance = read_verified_json(Path(preflight["provenance_path"]), preflight["source_sha256"][preflight["provenance_path"]])
    reconciliation = provenance["metadata_reconciliation"]
    if compact_sha(reconciliation["members"]) != preflight["membership_sha256"] or compact_sha(reconciliation["actual_queue_ranks"]) != preflight["rank_list_sha256"]:
        raise ValueError("accepted399 commitments drift")
    paths = preflight["execution_paths"]
    rank = reconciliation["selected_queue_rank"]
    exact = read_verified_json(Path(paths["exact_root"]) / "pairs" / f"{rank:06d}.json", reconciliation["selected_pair_record_sha256"])
    selection = {"queue_rank": rank, "candidate": exact["candidate"], "record_sha256": reconciliation["selected_pair_record_sha256"]}
    if compact_sha(selection) != preflight["selected_pair_sha256"]:
        raise ValueError("accepted pilot selection drift")
    videos = reconciliation["selected_video_bindings"]
    if [row["video_id"] for row in videos] != [exact["candidate"][side] for side in ("left", "right")]:
        raise ValueError("pair/video join drift")
    media, fingerprints = [], []
    for side, row in zip(("left", "right"), videos, strict=True):
        identity = row["video_id"]
        record = read_verified_json(Path(paths["audit_root"]) / "videos" / (identity + ".json"), row["media_record_sha256"])
        fingerprint = read_verified_json(Path(paths["screen_root"]) / "fingerprints" / (identity + ".json"), row["fingerprint_sha256"])
        if fingerprint["video_id"] != identity or fingerprint["accepted_media_record_sha256"] != row["media_record_sha256"] or exact[side + "_media_record_sha256"] != row["media_record_sha256"]:
            raise ValueError("fingerprint/exact parent join drift")
        tokens = decoded_tokens(record)
        for field in ("media_relpath", "media_archive", "byte_size", "media_sha256", "frame_count"):
            if record[field] != row[field]:
                raise ValueError("selected media metadata drift")
        if any(token[:2] != (row["width"], row["height"]) for token in tokens) or tokens[row["trigger_decode_order"]][2] != row["trigger_rgb_sha256"]:
            raise ValueError("selected full-frame/trigger drift")
        media.append(record)
        fingerprints.append(fingerprint)
    distance, left_slot, right_slot = min(((int(first["phash64"], 16) ^ int(second["phash64"], 16)).bit_count(), left_slot, right_slot)
                                         for left_slot, first in enumerate(fingerprints[0]["samples"])
                                         for right_slot, second in enumerate(fingerprints[1]["samples"]))
    if distance != exact["candidate"]["minimum_hamming"] or [fingerprints[side]["samples"][slot]["decode_order"] for side, slot in enumerate((left_slot, right_slot))] != [row["trigger_decode_order"] for row in videos]:
        raise ValueError("earliest trigger drift")
    if [row["frame_count"] for row in videos] != [151, 146] or any((row["width"], row["height"]) != (1080, 1920) for row in videos):
        raise ValueError("fixed pilot evidence quantities drift")
    return selection, videos, media


def prepare(preflight_path: Path, output: Path) -> dict:
    import tarfile

    preflight = strict_json(preflight_path.read_bytes())
    if preflight.get("checkpoint") != 243 or preflight.get("caps") != CAPS or preflight.get("review242_consolidated_pilot_authorized") is not True:
        raise ValueError("explicit fixed Review242 pilot authority required")
    private_output(output, [preflight_path, *map(Path, preflight["source_sha256"]), *map(Path, preflight["execution_paths"].values())])
    selection, videos, media = selected_sources(preflight)
    paths = {key: Path(value) for key, value in preflight["execution_paths"].items()}
    identities = verified_archive_identities(paths["input_root"], paths["archive_records"], preflight["guard_context"])
    ffmpeg = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    if ffmpeg != preflight["ffmpeg"]:
        raise ValueError("accepted decoder version drift")
    output = output.resolve()
    write_immutable_record(output / "lineage.json", {"checkpoint": 243, "preflight_sha256": _sha256(preflight_path),
                            "selected_pair_sha256": preflight["selected_pair_sha256"], "source_sha256": preflight["source_sha256"],
                            "ffmpeg": ffmpeg, "effective_dispositions": 0, "scientific_readiness": False})
    image_map, manifests = {}, {}

    def save(relative: str, rgb: np.ndarray) -> dict:
        path = output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = png_bytes(rgb)
        if sum(entry.stat().st_size for entry in output.rglob("*") if entry.is_file()) + len(payload) > CAPS["output_bytes"]:
            raise ValueError("output resource cap")
        with path.open("xb") as handle:
            handle.write(payload)
        restored = cv2.cvtColor(cv2.imdecode(np.frombuffer(payload, np.uint8), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
        if not np.array_equal(restored, rgb):
            raise ValueError("PNG RGB roundtrip")
        value = {"sha256": hashlib.sha256(payload).hexdigest(), "width": rgb.shape[1], "height": rgb.shape[0]}
        image_map[relative] = value
        return value

    for archive_name in sorted({row["media_archive"] for row in videos}):
        archive_path = paths["input_root"] / archive_name
        descriptor = os.open(archive_path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as handle:
            def identity():
                value = os.fstat(handle.fileno())
                return (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)

            if identity() != identities[archive_name]:
                raise ValueError("archive descriptor identity drift")
            with tarfile.open(fileobj=handle, mode="r:") as archive:
                wanted = {row["media_relpath"]: [] for row in videos if row["media_archive"] == archive_name}
                for member in archive:
                    if member.name in wanted:
                        wanted[member.name].append(member)
                if any(len(entries) != 1 for entries in wanted.values()):
                    raise ValueError("duplicate/missing selected tar members")
                if identity() != identities[archive_name]:
                    raise ValueError("archive changed before extraction")
                for binding, record in zip(videos, media, strict=True):
                    if binding["media_archive"] != archive_name:
                        continue
                    member = wanted[binding["media_relpath"]][0]
                    checked_member(member, binding)
                    frames, frame_assets, native = [], [], {}
                    with tempfile.TemporaryDirectory(prefix=".payload243-", dir=output) as directory:
                        payload_path = Path(directory) / "media.avi"
                        with archive.extractfile(member) as source, payload_path.open("xb") as target:
                            total = 0
                            while block := source.read(MIB):
                                total += len(block)
                                if total > binding["byte_size"] or total > CAPS["temporary_bytes"]:
                                    raise ValueError("temporary payload cap")
                                target.write(block)
                        if total != binding["byte_size"] or _sha256(payload_path) != binding["media_sha256"] or identity() != identities[archive_name]:
                            raise ValueError("payload/descriptor drift")

                        def consume(order, rgb):
                            thumb = cv2.resize(rgb, (256, 455), interpolation=cv2.INTER_AREA)
                            frames.append(thumb)
                            relative = f"videos/{binding['video_id']}/{order:06d}.png"
                            frame_assets.append({"decode_order": order, "accepted_rgb_sha256": record["frame_index"][order]["rgb_sha256"],
                                                 "path": relative, **save(relative, thumb)})
                            if order == binding["trigger_decode_order"]:
                                relative = f"videos/{binding['video_id']}/trigger.png"
                                native.update({"decode_order": order, "accepted_rgb_sha256": binding["trigger_rgb_sha256"], "path": relative, **save(relative, rgb)})

                        stream_frames(payload_path, record, consume, timeout=CAPS["decoder_seconds"])
                    galleries = []
                    for start in range(0, len(frames), 16):
                        relative = f"videos/{binding['video_id']}/gallery_{start // 16:02d}.png"
                        galleries.append({"decode_orders": list(range(start, min(start + 16, len(frames)))), "path": relative, **save(relative, gallery(frames, start))})
                    relative = f"videos/{binding['video_id']}/manifest.json"
                    write_immutable_record(output / relative, {"binding": binding, "frames": frame_assets, "galleries": galleries, "native_trigger": native})
                    manifests[relative] = _sha256(output / relative)
                    print("PASS243 video full-RGB/PNG/galleries", len(frames), flush=True)
            if identity() != identities[archive_name]:
                raise ValueError("archive descriptor changed after export")
    if verified_archive_identities(paths["input_root"], paths["archive_records"], preflight["guard_context"]) != identities:
        raise ValueError("archive path changed after export")
    check_bindings(preflight["source_sha256"])
    if len(image_map) != 319 or len(manifests) != 2:
        raise ValueError("fixed asset count mismatch")
    write_immutable_record(output / "pair.json", {"selection": selection, "manifests_sha256": manifests, "images": image_map,
                                                  "visual_review_performed": False, "effective_disposition_activated": False})
    before = {str(path.relative_to(output)): _sha256(path) for path in output.rglob("*") if path.is_file()}
    if len(before) != 323:
        raise ValueError("exact pre-completion file count")
    summary = {"checkpoint": 243, "status": "technical_assets_verified_adequacy_review_pending", "files_with_summary": 324,
               "RGB_frames_verified": 297, "image_count": 319, "file_sha256_without_summary": before,
               "scientific_readiness": False, "new_effective_dispositions": 0}
    write_immutable_record(output / "summary.json", summary)
    return summary


def usage(group: int, output: Path) -> dict:
    rss, temporary = 0, 0
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            if int(entry.name) != os.getpid() and os.getpgid(int(entry.name)) != group:
                continue
            for line in (entry / "status").read_text().splitlines():
                if line.startswith("VmRSS:"):
                    rss += int(line.split()[1]) * 1024
            for descriptor in (entry / "fd").iterdir():
                target = os.readlink(descriptor)
                if "(deleted)" in target:
                    temporary += descriptor.stat().st_size
        except (OSError, ProcessLookupError):
            continue
    final = 0
    if output.exists():
        for path in output.rglob("*"):
            if path.is_file():
                if any(part.startswith(".payload243-") for part in path.parts):
                    temporary += path.stat().st_size
                else:
                    final += path.stat().st_size
    return {"rss_bytes": rss, "temporary_bytes": temporary, "output_bytes": final}


def supervise(preflight: Path, output: Path, metrics: Path) -> int:
    private_output(output, [preflight])
    private_output(metrics, [preflight, output])
    ancestor = output.parent
    while not ancestor.exists():
        ancestor = ancestor.parent
    space = os.statvfs(ancestor)
    if space.f_bavail * space.f_frsize < CAPS["reserve_bytes"]:
        raise ValueError("initial free-space reserve")
    started = time.monotonic()
    peak = {key: 0 for key in ("rss_bytes", "temporary_bytes", "output_bytes")}
    process = subprocess.Popen([sys.executable, str(Path(__file__)), "--preflight", str(preflight), "--out-root", str(output), "--worker"], start_new_session=True)
    failure = None
    try:
        while True:
            measured = usage(process.pid, output)
            peak = {key: max(peak[key], value) for key, value in measured.items()}
            if time.monotonic() - started > CAPS["whole_seconds"] or any(value > CAPS[key] for key, value in measured.items()):
                raise TimeoutError("parent wall/RSS/storage watchdog cap")
            try:
                code = process.wait(timeout=0.05)
                break
            except subprocess.TimeoutExpired:
                pass
        if code:
            failure = "worker_failed_no_inspection_authorized"
    except (OSError, TimeoutError) as error:
        failure = str(error)
        code = 1
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
    record = {"checkpoint": 243, "elapsed_seconds": round(time.monotonic() - started, 3), "sampled_peaks": peak,
              "watchdog_interval_seconds": 0.05, "caps": CAPS, "returncode": code, "failure": failure,
              "completion_claimed": code == 0, "preflight_sha256": _sha256(preflight)}
    write_immutable_record(metrics, record)
    print("PASS243 export watchdog" if not code else "FAIL243 export watchdog", json.dumps(record, sort_keys=True), flush=True)
    return code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--out-root", type=Path, required=True)
    parser.add_argument("--metrics", type=Path)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        if args.worker:
            prepare(args.preflight, args.out_root)
            return 0
        if args.metrics is None:
            raise ValueError("private metrics path required")
        return supervise(args.preflight, args.out_root, args.metrics)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError):
        print("PILOT243 FAILED: no inspection or clearance claimed", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())