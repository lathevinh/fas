"""Strict CASIA probe with explicitly guarded native-DTS PTS transport."""

from __future__ import annotations

import csv
from fractions import Fraction
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import time

import diagnose_casia287 as diagnosis
import casia_counts287 as counts

prior = diagnosis.prior
ROOTS = (prior.shared.retained.ACQUISITION, prior.shared.retained.PILOT,
         prior.shared.retained.OUTPUT, prior.shared.images.OUTPUT, prior.shared.OUTPUT,
         prior.msu_recovery.OUTPUT, prior.OUTPUT, diagnosis.OUTPUT)


class ProbeFailure(ValueError):
    def __init__(self, stage, reason):
        super().__init__(reason)
        self.stage = stage
        self.reason = reason


def measured(group):
    result = prior.shared.usage(group, diagnosis.OUTPUT / ".unused")
    result["output_bytes"] = sum(prior.shared.retained.tree_bytes(root) for root in ROOTS) + result["temporary_bytes"]
    return result


def capture(command, prefix, *, timeout=180):
    stdout, stderr = prefix.with_suffix(".stdout"), prefix.with_suffix(".stderr")
    prefix.parent.mkdir(parents=True, exist_ok=True)
    process = None
    try:
        with stdout.open("xb") as out, stderr.open("xb") as err:
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=out, stderr=err)
            started = time.monotonic()
            while True:
                diagnosis.enforce(measured(os.getpgrp()))
                if stdout.stat().st_size > 16 * 1024 ** 2 or stderr.stat().st_size > 1024 ** 2:
                    raise OSError("strict probe diagnostic byte cap")
                if time.monotonic() - started >= timeout:
                    raise TimeoutError("strict probe command deadline")
                try:
                    code = process.wait(timeout=0.2)
                    break
                except subprocess.TimeoutExpired:
                    continue
        record = {"command": command, "returncode": code, "stdout_bytes": stdout.stat().st_size,
                  "stderr_bytes": stderr.stat().st_size, "stdout_sha256": prior.sha(stdout),
                  "stderr_sha256": prior.sha(stderr)}
        prior.write(prefix.with_suffix(".json"), record)
        if code or record["stderr_bytes"]:
            raise ProbeFailure(prefix.name, f"strict_exit_{code}_stderr_{record['stderr_bytes']}")
        return stdout.read_text()
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait()


def fraction(value, stage):
    try:
        return Fraction(value)
    except (ValueError, TypeError, ZeroDivisionError) as error:
        raise ProbeFailure(stage, "invalid_rational") from error


def metadata(payload, count_evidence=None, packets=None):
    try:
        stream, frames = payload["streams"][0], payload["frames"]
        rate = fraction(stream["avg_frame_rate"], "stream_metadata")
        duration = fraction(payload["format"]["duration"], "stream_metadata")
        if rate <= 0 or duration <= 0 or not frames:
            raise ProbeFailure("stream_metadata", "nonpositive_rate_duration_or_empty_frames")
        if any(frame["width"] <= 0 or frame["height"] <= 0 for frame in frames):
            raise ProbeFailure("frame_metadata", "invalid_dimensions")
        if any(frame["key_frame"] not in {0, 1} for frame in frames):
            raise ProbeFailure("frame_metadata", "invalid_key_frame")
        declared = stream.get("nb_frames")
        if declared not in (None, "N/A") and int(declared) != len(frames):
            if count_evidence is None or packets is None:
                raise ProbeFailure("frame_metadata", "declared_frame_count_mismatch")
            try:
                counts.validate(payload, packets, count_evidence)
            except (counts.CountFailure, KeyError, TypeError, ValueError) as error:
                raise ProbeFailure("native_count_reconciliation", str(error)) from error
        gaps = [index for index, frame in enumerate(frames) if "best_effort_timestamp_time" not in frame]
        previous = None
        for frame in frames:
            if "best_effort_timestamp_time" in frame:
                timestamp = fraction(frame["best_effort_timestamp_time"], "frame_metadata")
                if previous is not None and timestamp < previous:
                    raise ProbeFailure("frame_metadata", "nonmonotone_timestamps")
                previous = timestamp
        if gaps and (gaps != [len(frames) - 1] or payload["format"]["format_name"] != "avi"
                     or stream["codec_name"] != "mpeg4" or stream["has_b_frames"] <= 0):
            raise ProbeFailure("frame_metadata", "unsupported_missing_timestamp_pattern")
        return stream, frames, gaps, rate, duration
    except (KeyError, IndexError, TypeError, ValueError) as error:
        if isinstance(error, ProbeFailure):
            raise
        raise ProbeFailure("stream_metadata", type(error).__name__ + ":" + str(error)) from error


def native_dts(raw, packets, count_evidence=None):
    stream, frames, _, _, _ = metadata(raw, count_evidence, packets)
    try:
        packet_stream = packets["streams"][0]
        if any(stream[key] != packet_stream[key] for key in ("codec_name", "time_base", "nb_frames")):
            raise ProbeFailure("native_packet_dts", "stream_identity_mismatch")
        rows = packets["packets"]
        declared = int(stream["nb_frames"]) if count_evidence is not None else len(frames)
        if len(rows) != declared:
            raise ProbeFailure("native_packet_dts", "packet_frame_count_mismatch")
        time_base = fraction(stream["time_base"], "native_packet_dts")
        previous = None
        for row in rows:
            dts = int(row["dts"])
            duration = int(row["duration"])
            if duration <= 0 or time_base <= 0 or fraction(row["dts_time"], "native_packet_dts") != dts * time_base:
                raise ProbeFailure("native_packet_dts", "invalid_native_dts_duration")
            if previous is not None and dts <= previous:
                raise ProbeFailure("native_packet_dts", "nonmonotone_native_dts")
            previous = dts
        matching = [row for row in rows if str(row["pos"]) == str(frames[-1]["pkt_pos"])]
        if len(matching) != 1:
            raise ProbeFailure("native_packet_dts", "terminal_packet_identity_mismatch")
        return (int(rows[-1]["dts"]) + int(rows[-1]["duration"])) * time_base
    except (KeyError, IndexError, TypeError, ValueError) as error:
        if isinstance(error, ProbeFailure):
            raise
        raise ProbeFailure("native_packet_dts", type(error).__name__ + ":" + str(error)) from error


def parse_evidence(raw, framehash, *, packets=None, generated=None, count_evidence=None):
    stream, original_frames, gaps, rate, duration = metadata(raw, count_evidence, packets)
    frames = original_frames
    ignored_candidate_changes = []
    if gaps:
        if packets is None or generated is None:
            raise ProbeFailure("timestamp_transport", "native_packet_and_generated_evidence_required")
        terminal = native_dts(raw, packets, count_evidence)
        fixed_stream, candidates, fixed_gaps, _, _ = metadata(generated, count_evidence, packets)
        if fixed_gaps or len(candidates) != len(original_frames) or fixed_stream != stream or generated["format"] != raw["format"]:
            raise ProbeFailure("timestamp_transport", "stream_format_count_or_timestamp_drift")
        identity_keys = ("width", "height", "key_frame", "coded_picture_number", "pkt_pos", "pkt_size", "pict_type")
        frames = []
        for order, (old, new) in enumerate(zip(original_frames, candidates, strict=True)):
            if any(old.get(key) != new.get(key) for key in identity_keys):
                raise ProbeFailure("timestamp_transport", "decoded_frame_metadata_identity_drift")
            if "best_effort_timestamp_time" in old:
                if fraction(old["best_effort_timestamp_time"], "timestamp_transport") != fraction(new["best_effort_timestamp_time"], "timestamp_transport"):
                    ignored_candidate_changes.append(order)
                frames.append(old)
            else:
                frames.append({**old, "best_effort_timestamp_time": new["best_effort_timestamp_time"]})
        if fraction(frames[-1]["best_effort_timestamp_time"], "timestamp_transport") != terminal:
            raise ProbeFailure("timestamp_transport", "terminal_pts_not_bound_to_native_packet_end")
    lines = [line for line in framehash.splitlines() if line and not line.startswith("#")]
    hashes = list(csv.reader(io.StringIO("\n".join(lines)), skipinitialspace=True))
    if len(hashes) != len(frames):
        raise ProbeFailure("framehash", "decode_count_mismatch")
    time_bases = [line.split(":", 1)[1].strip() for line in framehash.splitlines() if line.startswith("#tb 0:")]
    if len(time_bases) != 1:
        raise ProbeFailure("framehash", "one_timebase_required")
    hash_time_base = fraction(time_bases[0], "framehash")
    index, sequence = [], hashlib.sha256()
    for order, (frame, row) in enumerate(zip(frames, hashes, strict=True)):
        if len(row) != 6 or row[0].strip() != "0":
            raise ProbeFailure("framehash", "invalid_framehash_shape")
        digest = row[-1].strip()
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ProbeFailure("framehash", "invalid_rgb_hash")
        if row[4].strip() != str(frame["width"] * frame["height"] * 3):
            raise ProbeFailure("framehash", "rgb_byte_count_mismatch")
        if fraction(row[2].strip(), "framehash") * hash_time_base != fraction(frame["best_effort_timestamp_time"], "frame_metadata"):
            raise ProbeFailure("framehash", "native_framehash_timestamp_mismatch")
        timestamp = fraction(frame["best_effort_timestamp_time"], "frame_metadata")
        if index and timestamp < fraction(index[-1]["timestamp_seconds"], "frame_metadata"):
            raise ProbeFailure("timestamp_transport", "nonmonotone_reconciled_timestamps")
        index.append({"decode_order": order, "timestamp_seconds": str(timestamp),
                      "key_frame": bool(frame["key_frame"]), "width": frame["width"], "height": frame["height"],
                      "decode_success": True, "rgb_sha256": digest})
        sequence.update(f"{frame['width']}:{frame['height']}:{row[4].strip()}:{digest}\n".encode())
    return {
        "decode_status": "decoded", "container": raw["format"]["format_name"], "codec": stream["codec_name"],
        "duration_ms": float(duration * 1000), "fps": str(rate), "frame_count": len(index), "frame_index": index,
        "decoded_rgb_sequence_sha256": sequence.hexdigest(),
        "middle_decoded_candidates": sorted({(len(index) - 1) // 2, len(index) // 2}), "failure_reason": None,
        "timestamp_transport": "native_packet_dts_guarded_genpts" if gaps else "unchanged_native_metadata",
        "original_missing_timestamp_orders": gaps, "existing_native_timestamps_unchanged": True,
        "ignored_generated_existing_timestamp_changes": ignored_candidate_changes,
        "framehash_input_flags_unchanged": True,
        "native_count_accounting": counts.validate(raw, packets, count_evidence) if count_evidence is not None else None}


def probe_video(path: Path, prefix: Path, *, timeout_seconds=180):
    result = {"decode_status": "failed", "container": None, "codec": None, "duration_ms": None,
              "fps": None, "frame_count": 0, "frame_index": [], "decoded_rgb_sequence_sha256": None,
              "middle_decoded_candidates": [], "failure_reason": None}
    prefix.mkdir(parents=True)
    try:
        command = ["ffprobe", "-v", "error", "-show_data", "-select_streams", "v:0",
                   "-show_frames", "-show_streams", "-show_format", "-of", "json", str(path)]
        raw = json.loads(capture(command, prefix / "original-metadata", timeout=timeout_seconds))
        packets, generated, count_evidence = None, None, None
        try:
            declared = raw["streams"][0].get("nb_frames")
            count_mismatch = declared not in (None, "N/A") and int(declared) != len(raw["frames"])
        except (KeyError, IndexError, ValueError, TypeError) as error:
            raise ProbeFailure("stream_metadata", str(error)) from error
        packet_command = ["ffprobe", "-v", "error", "-select_streams", "v:0",
                          "-show_packets", "-show_streams", "-of", "json", str(path)]
        if count_mismatch:
            packets = json.loads(capture(packet_command, prefix / "native-packets", timeout=timeout_seconds))
            try:
                count_evidence = counts.build(path, raw, packets)
            except (counts.CountFailure, KeyError, ValueError, TypeError) as error:
                raise ProbeFailure("native_count_reconciliation", str(error)) from error
            prior.write(prefix / "native-count.json", count_evidence)
        stream, _, gaps, rate, duration = metadata(raw, count_evidence, packets)
        result.update(container=raw["format"]["format_name"], codec=stream["codec_name"],
                      fps=str(rate), duration_ms=float(duration * 1000))
        if gaps:
            if packets is None:
                packets = json.loads(capture(packet_command, prefix / "native-packets", timeout=timeout_seconds))
            native_dts(raw, packets, count_evidence)
            generated = json.loads(capture(command[:3] + ["-fflags", "+genpts"] + command[3:],
                                           prefix / "guarded-genpts", timeout=timeout_seconds))
        framehash_command = ["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-err_detect", "explode",
                             "-threads", "1", "-i", str(path), "-map", "0:v:0", "-an", "-sn", "-dn",
                             "-pix_fmt", "rgb24", "-threads", "1", "-vsync", "0",
                             "-f", "framehash", "-hash", "sha256", "-"]
        framehash = capture(framehash_command, prefix / "native-framehash", timeout=timeout_seconds)
        result = parse_evidence(raw, framehash, packets=packets, generated=generated, count_evidence=count_evidence)
    except (ProbeFailure, json.JSONDecodeError) as error:
        stage = error.stage if isinstance(error, ProbeFailure) else "json"
        reason = error.reason if isinstance(error, ProbeFailure) else str(error)
        result.update(failure_reason=stage + ":" + reason, probe_failure={"stage": stage, "reason": reason, "exception_type": type(error).__name__})
    prior.write(prefix / "probe_result.json", result)
    result["probe_result_sha256"] = prior.sha(prefix / "probe_result.json")
    return result
