"""Validate both native-clock and exact coded-picture accounting on fixed sources."""

import hashlib
from pathlib import Path
import time

import casia_probe287 as probe
import casia_counts287 as counts
from msu_replay282 import strict_replay


def main():
    root, prior = probe.diagnosis.OUTPUT, probe.prior
    plan = probe.diagnosis.bound_prior()
    selected = [(0, root / "diagnostic/extraction.stdout"),
                (1, root / "representatives/low/extraction.stdout"),
                (8, root / "representatives/high/extraction.stdout")]
    selection = {"indices": [index for index, _ in selected],
                 "selection": "same previously fixed normal/low/high sources; no favorable replacement"}
    selection_path = root / "native_validation_selection.json"
    if selection_path.exists():
        if prior.read(selection_path) != selection:
            raise ValueError("fixed validation selection drift")
    else:
        prior.write(selection_path, selection)
    pins = prior.read(prior.OUTPUT / "release_integrity.json")["video_payload_pins"]
    results = []
    for index, source in selected:
        original = plan["videos"][index]
        pin = pins[original["media_relpath"]]
        if prior.sha(source) != pin["sha256"] or source.stat().st_size != pin["byte_size"]:
            raise ValueError("same fixed original SHA/size required")
        folder = root / "native-validation-final" / f"{index:04d}"
        media = probe.probe_video(source, folder / "probe")
        if media["decode_status"] != "decoded":
            raise ValueError("same-original native correction not validated: " + media["failure_reason"])
        observed, middle = [], (media["frame_count"] - 1) // 2

        def consume(order, rgb):
            if order == middle:
                observed.append(hashlib.sha256(rgb.tobytes()).hexdigest())

        strict_replay(source, media, consume, folder / "strict-replay",
                      timeout=min(180, probe.diagnosis.authority()["deadline_unix_seconds"] - time.time()))
        if observed != [media["frame_index"][middle]["rgb_sha256"]]:
            raise ValueError("fixed middle does not match unchanged native framehash")
        results.append({"index": index, "quality": original["quality"], "frame_count": media["frame_count"],
                        "timestamp_transport": media["timestamp_transport"], "native_count_accounting": media["native_count_accounting"],
                        "selected_decode_order": middle, "selected_rgb_sha256": observed[0],
                        "all_original_rgb_hashes_verified": True,
                        "probe_result_sha256": media["probe_result_sha256"],
                        "strict_replay_sha256": prior.sha(folder / "strict-replay.json")})
        print("NATIVE_PROOF287", original["quality"], media["frame_count"], media["native_count_accounting"], flush=True)
    prior.guard(plan)
    prior.write(root / "native_fix_validation.json", {
        "rows": results, "all_predeclared_sources_passed": True,
        "probe_source_sha256": prior.sha(Path(probe.__file__)), "count_source_sha256": prior.sha(Path(counts.__file__)),
        "validation_source_sha256": prior.sha(Path(__file__)), "toolchain": plan["toolchain"],
        "full_input_rgb_exit_stderr_eof_preserved": True, "no_manual_timestamp_or_frame_assignment": True,
        "no_ignored_or_dropped_coded_pictures": True, "detector_inference": False})


if __name__ == "__main__":
    main()
