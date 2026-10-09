"""Read-only full-decode evidence using the installed FFmpeg toolchain."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any


def probe_video(path: Path, *, timeout_seconds: int = 180) -> dict[str, Any]:
    result: dict[str, Any] = {
        "decode_status": "failed", "container": None, "codec": None,
        "duration_ms": None, "fps": None, "frame_count": 0,
        "frame_index": [], "decoded_rgb_sequence_sha256": None,
        "middle_decoded_candidates": [], "failure_reason": None,
    }
    try:
        probe = subprocess.run([
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_frames", "-show_streams", "-show_format", "-of", "json",
            str(path),
        ], capture_output=True, text=True, timeout=timeout_seconds, check=False)
        if probe.returncode or probe.stderr.strip():
            raise ValueError("probe_error")
        payload = json.loads(probe.stdout)
        stream = payload["streams"][0]
        result["container"] = payload["format"]["format_name"]
        result["codec"] = stream["codec_name"]
        rate = Fraction(stream["avg_frame_rate"])
        if rate <= 0:
            raise ValueError("invalid_fps")
        result["fps"] = str(rate)
        duration = Fraction(payload["format"]["duration"])
        if duration <= 0:
            raise ValueError("invalid_duration")
        result["duration_ms"] = float(duration * 1000)
        frames = payload["frames"]
        if not frames:
            raise ValueError("zero_frames")
        index = []
        for order, frame in enumerate(frames):
            timestamp = Fraction(frame["best_effort_timestamp_time"])
            if frame["width"] <= 0 or frame["height"] <= 0:
                raise ValueError("invalid_dimensions")
            if index and timestamp < Fraction(index[-1]["timestamp_seconds"]):
                raise ValueError("nonmonotone_timestamps")
            index.append({
                "decode_order": order, "timestamp_seconds": str(timestamp),
                "key_frame": bool(frame["key_frame"]),
                "width": frame["width"], "height": frame["height"],
                "decode_success": True,
            })
        decode = subprocess.run([
            "ffmpeg", "-nostdin", "-v", "error", "-xerror", "-err_detect",
            "explode", "-threads", "1", "-i", str(path), "-map", "0:v:0",
            "-an", "-sn", "-dn", "-pix_fmt", "rgb24", "-threads", "1",
            "-vsync", "0", "-f", "framehash", "-hash",
            "sha256", "-",
        ], capture_output=True, text=True, timeout=timeout_seconds, check=False)
        if decode.returncode or decode.stderr.strip():
            raise ValueError("decode_error")
        lines = [line for line in decode.stdout.splitlines() if line and not line.startswith("#")]
        hashes = list(csv.reader(io.StringIO("\n".join(lines)), skipinitialspace=True))
        if len(hashes) != len(index):
            raise ValueError("decode_count_mismatch")
        declared = stream.get("nb_frames")
        if declared not in (None, "N/A") and int(declared) != len(index):
            raise ValueError("declared_frame_count_mismatch")
        sequence = hashlib.sha256()
        for frame, row in zip(index, hashes, strict=True):
            if len(row) != 6 or row[0].strip() != "0":
                raise ValueError("invalid_framehash")
            frame_hash = row[-1].strip()
            if len(frame_hash) != 64 or any(character not in "0123456789abcdef" for character in frame_hash):
                raise ValueError("invalid_framehash")
            frame["rgb_sha256"] = frame_hash
            sequence.update(f"{frame['width']}:{frame['height']}:{row[4].strip()}:{frame_hash}\n".encode())
        result.update({
            "decode_status": "decoded", "frame_count": len(index),
            "frame_index": index, "decoded_rgb_sequence_sha256": sequence.hexdigest(),
            "middle_decoded_candidates": sorted({(len(index) - 1) // 2, len(index) // 2}),
        })
    except subprocess.TimeoutExpired:
        result["failure_reason"] = "timeout"
    except (ValueError, KeyError, IndexError, TypeError, ZeroDivisionError):
        result["failure_reason"] = "invalid_or_undecodable_media"
    return result