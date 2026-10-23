"""Add the explicitly approved native-IPC handoff gates to CASIA289 closure."""

import json
from pathlib import Path

import complete_casia289 as original
import finish_casia289 as finish


def additional_checks():
    prior, output = finish.prior, finish.OUTPUT
    addendum = prior.read(finish.HANDOFF / "plan.json")
    finish.check(addendum)
    retained = prior.read(finish.HANDOFF / "retained_readback.json")
    if retained["retained_committed"] != 464 or retained["retained_decode_calls"] or retained["retained_detector_calls"]:
        raise ValueError("464 retained units must not be decoded/inferred again")
    if retained["original447_readback_sha256"] != prior.sha(output / "retained_readback.json"):
        raise ValueError("original447 readback identity drift")
    for relative, digest in retained["additional17_asset_sha256"].items():
        if prior.sha(output / relative) != digest:
            raise ValueError("additional17 retained assets changed")
    staging = prior.read(finish.HANDOFF / "restaging.json")
    plan = prior.read(output / "plan.json")
    expected = {plan["videos"][i]["media_relpath"] for i in range(464, 600)}
    if staging["new_extracted_videos"] != 136 or set(staging["source_pins"]) != expected:
        raise ValueError("exact136 same-clock restaging required")
    pins = prior.read(output / "release_integrity.json")["video_payload_pins"]
    if any(pin != pins[name] for name, pin in staging["source_pins"].items()):
        raise ValueError("136 restaged native commitments drift")
    if (staging["extractor_returncode"] or staging["extractor_stderr_bytes"]
            or prior.sha(finish.HANDOFF / "restaging.stderr") != staging["extractor_stderr_sha256"]):
        raise ValueError("136 restaging strict exit/stderr drift")
    return addendum


def main():
    original.recovery.ROOTS = finish.ROOTS
    original_checks = original.checks

    def checks():
        result = original_checks()
        additional_checks()
        return result

    original.checks = checks
    original.main()
    if (finish.OUTPUT / "local_audit.json").exists():
        receipt = {
            "checkpoint": 289, "explicit_same_clock_handoff": True,
            "native_handoff_plan_sha256": finish.prior.sha(finish.HANDOFF / "plan.json"),
            "handoff_retained_readback_sha256": finish.prior.sha(finish.HANDOFF / "retained_readback.json"),
            "handoff_restaging_sha256": finish.prior.sha(finish.HANDOFF / "restaging.json"),
            "local_audit_sha256": finish.prior.sha(finish.OUTPUT / "local_audit.json"),
            "completion_gate_sha256": finish.prior.sha(Path(__file__)),
            "retained_without_repeat": 464, "new_handoff_attempts": 136, "scientific_readiness": False}
        finish.prior.write(finish.prior.ROOT / "results/phase1/casia-native-ipc-handoff289-v1.json", receipt)
        print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
