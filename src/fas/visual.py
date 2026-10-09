"""Verified private RGB review evidence, separate from research preprocessing."""

from __future__ import annotations

import hashlib
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np

from .lineage import decoded_tokens


def review_orders(count: int) -> list[int]:
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise ValueError("invalid review frame count")
    return [(count - 1) * slot // 16 for slot in range(17)]


def verified_thumbnails(path: Path, media: dict) -> list[np.ndarray]:
    tokens = decoded_tokens(media)
    if len({token[:2] for token in tokens}) != 1:
        raise ValueError("variable review dimensions unsupported")
    width, height = tokens[0][:2]
    size = width * height * 3
    thumbnails = []
    with tempfile.TemporaryFile() as errors:
        process = subprocess.Popen([
            "ffmpeg", "-nostdin", "-v", "error", "-xerror", "-err_detect", "explode",
            "-threads", "1", "-i", str(path), "-map", "0:v:0", "-an", "-sn", "-dn",
            "-pix_fmt", "rgb24", "-threads", "1", "-vsync", "0", "-f", "rawvideo", "-",
        ], stdout=subprocess.PIPE, stderr=errors)
        try:
            for token in tokens:
                payload = process.stdout.read(size)
                if len(payload) != size or hashlib.sha256(payload).hexdigest() != token[2]:
                    raise ValueError("accepted review RGB identity mismatch")
                rgb = np.frombuffer(payload, dtype=np.uint8).reshape(height, width, 3)
                thumbnails.append(cv2.resize(rgb, (256, max(1, height * 256 // width)), interpolation=cv2.INTER_AREA))
            if process.stdout.read(1):
                raise ValueError("extra review frames")
            if process.wait(timeout=180):
                raise ValueError("review decode failed")
            errors.seek(0)
            if errors.read(1):
                raise ValueError("strict review decode error")
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            process.stdout.close()
    return thumbnails


def png_bytes(rgb: np.ndarray) -> bytes:
    success, payload = cv2.imencode(".png", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    if not success:
        raise ValueError("PNG encoding failed")
    return payload.tobytes()


def pair_sheet(left: list[np.ndarray], right: list[np.ndarray], slots: list[int]) -> np.ndarray:
    if not slots or any(isinstance(slot, bool) or not isinstance(slot, int) or not 0 <= slot <= 16 for slot in slots):
        raise ValueError("invalid temporal review slots")
    orders = [review_orders(len(left)), review_orders(len(right))]
    tile_width = 160
    tile_height = max(frame.shape[0] * tile_width // frame.shape[1] for frames in (left, right) for frame in frames[:1])
    result = np.full((2 * (tile_height + 28), tile_width * len(slots), 3), 255, dtype=np.uint8)
    for side, frames in enumerate((left, right)):
        for column, slot in enumerate(slots):
            order = orders[side][slot]
            frame = frames[order]
            resized = cv2.resize(frame, (tile_width, frame.shape[0] * tile_width // frame.shape[1]), interpolation=cv2.INTER_AREA)
            top, start = side * (tile_height + 28), column * tile_width
            cv2.putText(result, f"{'L' if side == 0 else 'R'} n={order}", (start + 4, top + 19), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
            result[top + 28:top + 28 + resized.shape[0], start:start + tile_width] = resized
    return result