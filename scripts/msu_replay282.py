"""Strict decoded-RGB replay with durable decoder diagnostics."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import selectors
import subprocess
import time

import numpy as np

from fas.freeze import write_immutable_record
from fas.lineage import decoded_tokens
from fas.oulu import _sha256


def replay_command(path: Path) -> list[str]:
    return ["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-err_detect", "explode",
            "-threads", "1", "-i", str(path), "-map", "0:v:0", "-an", "-sn", "-dn",
            "-pix_fmt", "rgb24", "-threads", "1", "-vsync", "0",
            "-enc_time_base", "-1", "-f", "rawvideo", "-"]


def strict_replay(path: Path, media: dict, consume, receipt: Path, *,
                  timeout: float = 180, command: list[str] | None = None) -> None:
    tokens = decoded_tokens(media)
    if len({token[:2] for token in tokens}) != 1:
        raise ValueError("variable dimensions")
    width, height = tokens[0][:2]
    size = width * height * 3
    deadline = time.monotonic() + timeout
    argv = command if command is not None else replay_command(path)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    errors_path = receipt.with_suffix(".stderr")
    process, failure, verified = None, None, 0
    try:
        with errors_path.open("xb") as errors, selectors.DefaultSelector() as selector:
            process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=errors, bufsize=0)
            if process.stdout is None:
                raise RuntimeError("decoder stdout pipe required")
            selector.register(process.stdout, selectors.EVENT_READ)

            def read_exact(count):
                payload = bytearray()
                while len(payload) < count:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0 or not selector.select(remaining):
                        raise TimeoutError("absolute decoder deadline")
                    if os.fstat(errors.fileno()).st_size > 16 * 1024 ** 2:
                        raise ValueError("decoder stderr16MiB cap")
                    block = os.read(process.stdout.fileno(), min(count - len(payload), 1024 ** 2))
                    if not block:
                        break
                    payload.extend(block)
                return bytes(payload)

            for order, token in enumerate(tokens):
                payload = read_exact(size)
                if len(payload) != size or hashlib.sha256(payload).hexdigest() != token[2]:
                    raise ValueError("RGB identity/count mismatch")
                consume(order, np.frombuffer(payload, np.uint8).reshape(height, width, 3))
                verified += 1
            if read_exact(1):
                raise ValueError("extra RGB bytes")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("absolute decoder deadline")
            code = process.wait(timeout=remaining)
            if code or errors_path.stat().st_size:
                raise ValueError(f"strict decoder returncode={code} stderr_bytes={errors_path.stat().st_size}; retained diagnostic")
    except Exception as error:
        failure = type(error).__name__ + ": " + str(error)
        raise
    finally:
        if process is not None:
            if process.poll() is None:
                process.kill()
            process.wait()
            if process.stdout is not None:
                process.stdout.close()
        write_immutable_record(receipt.with_suffix(".json"), {
            "frame_count": len(tokens), "frames_verified": verified,
            "decoded_rgb_sequence_sha256": media["decoded_rgb_sequence_sha256"],
            "returncode": process.returncode if process is not None else None,
            "stderr_bytes": errors_path.stat().st_size if errors_path.exists() else None,
            "stderr_sha256": _sha256(errors_path) if errors_path.exists() else None,
            "strict_success": failure is None and verified == len(tokens),
            "failure": failure, "command": argv, "frame_substitution": False})
