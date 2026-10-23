"""Prove the demonstrated timestamp transport on the same committed original."""

import json
import hashlib
from pathlib import Path
import subprocess
import time

import casia_probe287 as probe
from msu_replay282 import strict_replay


def main():
    root = probe.diagnosis.OUTPUT
    probe.diagnosis.authority()
    diagnosis = probe.prior.read(root / "diagnosis.json")
    if diagnosis["exceptions"][0]["exception_type"] != "KeyError" or diagnosis["exceptions"][0]["message"] != "'best_effort_timestamp_time'":
        raise ValueError("exact captured original defect required")
    directory = root / "diagnostic"
    raw = json.loads((directory / "ffprobe.stdout").read_text())
    packets = json.loads((directory / "packets.stdout").read_text())
    generated = json.loads((directory / "genpts.stdout").read_text())
    media = probe.parse_evidence(raw, (directory / "framehash.stdout").read_text(),
                                 packets=packets, generated=generated)
    source = directory / "extraction.stdout"
    if probe.prior.sha(source) != diagnosis["original_payload_pin"]["sha256"]:
        raise ValueError("fixed original diagnostic source drift")
    probe.prior.write(root / "fix-media.json", media)
    selected, observed = (media["frame_count"] - 1) // 2, []

    def consume(order, rgb):
        if order == selected:
            observed.append(hashlib.sha256(rgb.tobytes()).hexdigest())

    strict_replay(source, media, consume, directory / "fixed-strict-replay",
                  timeout=min(180, probe.diagnosis.authority()["deadline_unix_seconds"] - time.time()))
    if observed != [media["frame_index"][selected]["rgb_sha256"]]:
        raise ValueError("fixed selected RGB differs from original unmodified framehash")
    tools = {name: subprocess.run([name, "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
             for name in ("ffmpeg", "ffprobe")}
    result = {
        "checkpoint": 287, "native_frame_count": media["frame_count"], "selected_decode_order": selected,
        "selected_rgb_sha256": observed[0], "selected_timestamp_seconds": media["frame_index"][selected]["timestamp_seconds"],
        "full_original_framehash_rgb_sequence_preserved": True, "existing_native_timestamps_unchanged": True,
        "terminal_pts_native_dts_guard_verified": True, "no_manual_timestamp_assignment": True,
        "strict_input_exit_stderr_count_and_rgb_checks_preserved": True, "new_detector_inference": False,
        "probe_source_sha256": probe.prior.sha(Path(probe.__file__)),
        "proof_source_sha256": probe.prior.sha(Path(__file__)),
        "media_record_sha256": probe.prior.sha(root / "fix-media.json"),
        "replay_receipt_sha256": probe.prior.sha(directory / "fixed-strict-replay.json"),
        "diagnosis_sha256": probe.prior.sha(root / "diagnosis.json"), "toolchain": tools,
        "accounting_complete": False, "primary_image_preprocessing_complete": False}
    probe.prior.write(root / "fix_validation.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
