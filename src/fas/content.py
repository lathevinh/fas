"""Model-free temporal fingerprint screening, not provenance certification."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import cv2
import numpy as np


def temporal_orders(count: int) -> list[int]:
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise ValueError("invalid decoded frame count")
    return [(count - 1) * numerator // 4 for numerator in range(5)]


def perceptual_hash(rgb: np.ndarray) -> str:
    if rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[2] != 3 or min(rgb.shape[:2]) <= 0:
        raise ValueError("invalid RGB frame")
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    small = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA)
    low = cv2.dct(small.astype(np.float32))[:8, :8].reshape(-1)
    bits = low > np.median(low[1:])
    bits[0] = False
    return np.packbits(bits).tobytes().hex()


def fingerprint_video(path: Path, media: dict) -> dict:
    if media["decode_status"] != "decoded":
        if media["frame_count"] != 0 or media["frame_index"]:
            raise ValueError("invalid failed media evidence")
        return {"status": "unavailable_decode_failure", "samples": []}
    index = media["frame_index"]
    if len(index) != media["frame_count"] or any(frame["decode_order"] != order for order, frame in enumerate(index)):
        raise ValueError("invalid accepted index")
    orders = temporal_orders(len(index))
    unique = sorted(set(orders))
    dimensions = {(index[order]["width"], index[order]["height"]) for order in unique}
    if len(dimensions) != 1:
        raise ValueError("variable sampled dimensions unsupported")
    width, height = dimensions.pop()
    expression = "+".join(f"eq(n\\,{order})" for order in unique)
    result = subprocess.run([
        "ffmpeg", "-nostdin", "-v", "error", "-xerror", "-err_detect", "explode",
        "-threads", "1", "-i", str(path), "-map", "0:v:0", "-an", "-sn", "-dn",
        "-vf", "select=" + expression, "-pix_fmt", "rgb24", "-threads", "1",
        "-vsync", "0", "-f", "rawvideo", "-",
    ], capture_output=True, timeout=180, check=False)
    size = width * height * 3
    if result.returncode or result.stderr.strip() or len(result.stdout) != size * len(unique):
        raise ValueError("fingerprint decode failed")
    samples = {}
    for position, order in enumerate(unique):
        payload = result.stdout[position * size:(position + 1) * size]
        digest = hashlib.sha256(payload).hexdigest()
        if digest != index[order]["rgb_sha256"]:
            raise ValueError("accepted RGB identity mismatch")
        rgb = np.frombuffer(payload, dtype=np.uint8).reshape(height, width, 3)
        samples[order] = {"decode_order": order, "rgb_sha256": digest,
                          "phash64": perceptual_hash(rgb)}
    return {"status": "fingerprinted", "samples": [samples[order] for order in orders]}


def candidate_pairs(records: list[dict], *, block_size: int = 128):
    if not isinstance(block_size, int) or isinstance(block_size, bool) or block_size < 1:
        raise ValueError("invalid comparison block")
    if len({row["video_id"] for row in records}) != len(records):
        raise ValueError("duplicate identities")
    usable = sorted((row for row in records if row["status"] == "fingerprinted"), key=lambda row: row["video_id"])
    for row in records:
        if row["status"] not in ("fingerprinted", "unavailable_decode_failure"):
            raise ValueError("unknown fingerprint status")
        samples = row["samples"]
        if row["status"] == "unavailable_decode_failure" and samples:
            raise ValueError("failed fingerprint has samples")
        if row["status"] == "fingerprinted" and (len(samples) != 5 or any(
            len(sample["phash64"]) != 16 or any(character not in "0123456789abcdef" for character in sample["phash64"])
            for sample in samples
        )):
            raise ValueError("invalid fingerprint")
    hashes = np.array([[int(sample["phash64"], 16) for sample in row["samples"]] for row in usable], dtype=np.uint64).reshape(-1, 5)
    lookup = np.array([value.bit_count() for value in range(256)], dtype=np.uint8)
    for start in range(0, len(usable), block_size):
        stop = min(start + block_size, len(usable))
        minimum = np.full((stop - start, len(usable)), 64, dtype=np.uint8)
        aligned = np.zeros_like(minimum)
        for left_slot in range(5):
            for right_slot in range(5):
                xor = hashes[start:stop, left_slot, None] ^ hashes[None, :, right_slot]
                distance = lookup[xor.view(np.uint8).reshape(stop - start, len(usable), 8)].sum(axis=2, dtype=np.uint8)
                np.minimum(minimum, distance, out=minimum)
                if left_slot == right_slot:
                    aligned += distance <= 8
        matches = (minimum <= 4) | (aligned >= 3)
        for local, right in zip(*np.nonzero(matches)):
            left = start + int(local)
            if left < right:
                yield {"left": usable[left]["video_id"], "right": usable[int(right)]["video_id"],
                       "minimum_hamming": int(minimum[local, right]),
                       "aligned_slots_within_8": int(aligned[local, right]),
                       "disposition": "unresolved_candidate_not_confirmed_lineage"}