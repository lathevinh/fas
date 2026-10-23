"""Fixed low/high-quality transport checks, not detector selection or pilots."""

import hashlib
from pathlib import Path
import time
import zlib

import casia_probe287 as probe
from msu_replay282 import strict_replay


def main():
    prior, root = probe.prior, probe.diagnosis.OUTPUT
    plan = probe.diagnosis.bound_prior()
    selections = [(index, row) for index, row in enumerate(plan["videos"])
                  if row["media_relpath"] in {"test_release/1/2.avi", "test_release/1/HR_1.avi"}]
    if len(selections) != 2:
        raise ValueError("two predeclared same-subject quality representatives required")
    prior.write(root / "representative_selection.json", {
        "indices": [index for index, _ in selections], "selection": "fixed first subject low2/highHR_1; before observed outcomes",
        "no_detector_inference_or_favorable_replacement": True})
    previous = prior.read(probe.diagnosis.prior.OUTPUT / "release_integrity.json")
    result = []
    for index, original in selections:
        prefix = root / "representatives" / original["quality"] / "extraction"
        record, payload, errors = probe.diagnosis.capture(
            [str(prior.EXTRACTOR), "-xOf", str(prior.ARCHIVE), original["media_relpath"]],
            prefix, stdout_cap=original["byte_size"], timeout=120)
        pin = previous["video_payload_pins"][original["media_relpath"]]
        if record["returncode"] or errors or len(payload) != pin["byte_size"] or zlib.crc32(payload) != pin["crc32"] or hashlib.sha256(payload).hexdigest() != pin["sha256"]:
            raise ValueError("fixed representative CRC/size/SHA drift")
        media = probe.probe_video(prefix.with_suffix(".stdout"), prefix.parent / "probe")
        if media["decode_status"] != "decoded":
            raise ValueError("fixed representative correction failed: " + media["failure_reason"])
        strict_replay(prefix.with_suffix(".stdout"), media, lambda order, rgb: None,
                      prefix.parent / "strict-replay",
                      timeout=min(180, probe.diagnosis.authority()["deadline_unix_seconds"] - time.time()))
        result.append({"index": index, "quality": original["quality"], "frame_count": media["frame_count"],
                       "timestamp_transport": media["timestamp_transport"], "full_native_rgb_replay": True,
                       "replay_receipt_sha256": prior.sha(prefix.parent / "strict-replay.json"),
                       "probe_record_sha256": media["probe_result_sha256"], "original_payload_pin": pin})
        print("REPRESENTATIVE287", original["quality"], media["frame_count"], flush=True)
    prior.guard(plan)
    prior.write(root / "representatives_validation.json", {
        "rows": result, "source_sha256": prior.sha(Path(__file__)), "probe_source_sha256": prior.sha(Path(probe.__file__)),
        "all_predeclared_representatives_passed": True, "new_detector_inference": False})


if __name__ == "__main__":
    main()
