"""Close the source handoff from sealed integration and saved pilot outputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from fas.freeze import write_immutable_record
from fas.frozen_features import check_feature, feature_key, mean_cosine_logit, parity
from fas.preregistration import validate_stage
import integrate_source295 as integration
import pilot_source295 as pilot


def close() -> None:
    import numpy as np
    config, approval = pilot.authority()
    pilot.enforce(approval, final=True)
    config_sha = pilot.digest(pilot.CONFIG)
    terminal = pilot.read(pilot.APPROVAL_ROOT / "terminal.json")
    attempt = pilot.read(pilot.APPROVAL_ROOT / "attempt_lock.json")
    for path, field in ((ROOT / "scripts/pilot_source295.py", "script_sha256"),
                        (ROOT / "src/fas/frozen_features.py", "feature_contract_sha256")):
        if pilot.digest(path) != attempt[field]:
            raise ValueError("executed pilot source changed")
    if (terminal["failure"] is not None or terminal["status"] != "technical_source_encoder_pilot_passed"
            or terminal["config_sha256"] != config_sha
            or terminal["sampled_peak_rss_bytes"] > approval["caps"]["rss_bytes"]
            or terminal["peak_new_temporary_bytes"] > approval["caps"]["output_bytes"]):
        raise ValueError("successful original authority/resource terminal required")
    if pilot.digest(pilot.NATIVE / "worker_completion.json") != terminal["worker_completion_sha256"]:
        raise ValueError("pilot completion changed")
    worker = pilot.read(pilot.NATIVE / "worker_completion.json")
    if worker["image_forward_calls"] != 144 or worker["text_forward_calls"] != 2:
        raise ValueError("exact approved repeated image/text forwards required")
    if (pilot.digest(pilot.INTEGRATION / "source_manifest.json") != config["source_manifest_sha256"]
            or pilot.digest(pilot.INTEGRATION / "pilot_inputs.json") != config["pilot_inputs_sha256"]):
        raise ValueError("source input population changed")
    manifest = pilot.read(pilot.INTEGRATION / "source_manifest.json")
    for relative in ("scripts/integrate_source295.py", "src/fas/source_stage.py",
                     "configs/experiment_core_v1.yaml", "configs/preprocessing_v3.yaml",
                     "configs/source_recipe_v2.yaml", "configs/seeds_v1.yaml"):
        path = ROOT / relative
        if pilot.digest(path) != manifest["input_sha256"][str(path)]:
            raise ValueError("executed integration source/recipe changed")
    selected = pilot.read(pilot.INTEGRATION / "pilot_inputs.json")["rows"]
    saved = {}
    for name, spec in config["models"].items():
        result = worker["models"][name]
        if pilot.digest(pilot.NATIVE / f"{name}-features.npy") != result["shard_sha256"]:
            raise ValueError("feature shard bytes changed")
        checkpoint = pilot.NATIVE / "checkpoints" / f"{name}.pth"
        if pilot.digest(checkpoint) != worker["acquisitions"][name]["sha256"]:
            raise ValueError("acquired checkpoint bytes changed")
        feature = np.load(pilot.NATIVE / f"{name}-features.npy", allow_pickle=False)
        check_feature(feature, 24, spec["feature_dimension"])
        keys = []
        for row in selected:
            crop = row["crops"][str(spec["resolution"])]
            if pilot.digest(Path(crop["path"])) != crop["sha256"]:
                raise ValueError("pilot input crop changed after execution")
            keys.append(feature_key(
                dataset=row["dataset"], video_id=row["video_id"], crop_sha256=crop["sha256"],
                checkpoint_sha256=result["checkpoint_sha256"],
                preprocessing_sha256=config["preprocessing_sha256"],
                representation=spec.get("representation", "normalized_image_embedding")))
        if keys != result["feature_keys"] or len(set(keys)) != 24:
            raise ValueError("saved feature/sample/cache-key join drift")
        saved[name] = feature
    clip = worker["models"]["openclip"]
    text_path, logit_path = pilot.NATIVE / "openclip-text.npy", pilot.NATIVE / "openclip-prompt-logits.npy"
    if (pilot.digest(text_path) != clip["text_sha256"] or pilot.digest(logit_path) != clip["prompt_logits_sha256"]
            or pilot.digest(ROOT / "configs/prompts_core_v1.yaml") != clip["prompts_sha256"]):
        raise ValueError("fixed prompt text/logit provenance drift")
    prompts = pilot.read(ROOT / "configs/prompts_core_v1.yaml")["classes"]
    parity(np.load(logit_path, allow_pickle=False),
           mean_cosine_logit(saved["openclip"], np.load(text_path, allow_pickle=False), len(prompts["live"])))
    stage_errors = {stage: validate_stage(ROOT, stage, frozen_root=integration.FROZEN, source_use_root=integration.USE)
                    for stage in ("schema", "data-audit", "source-dry-run", "analysis-freeze", "locked-evaluation")}
    if stage_errors["schema"] or stage_errors["data-audit"]:
        raise ValueError("accepted schema/data prerequisites drifted")
    original = pilot.read(pilot.INTEGRATION / "integration.json")
    expected = {"archived": 7510, "source_use": 6882, "model_input": 6855,
                "actual_score_fit": 0, "source_use_failures": 27,
                "pre_detector_failure": 9, "detector_failure": 22, "source_excluded": 5, "null_role_test": 623}
    if any(original["combined"][key] != value for key, value in expected.items()):
        raise ValueError("integrated source/failure/archive arithmetic drift")
    report = {
        "version": 1, "checkpoint": 295, "status": "source_integration_and_authorized_technical_pilot_complete",
        "source_use_binding": original["source_use_binding"], "combined": original["combined"],
        "integration_sha256": pilot.digest(pilot.INTEGRATION / "integration.json"),
        "source_manifest_sha256": config["source_manifest_sha256"], "pilot_inputs_sha256": config["pilot_inputs_sha256"],
        "owner_approval_sha256": pilot.digest(pilot.APPROVAL_ROOT / "owner_approval.json"),
        "original_pilot_terminal_sha256": pilot.digest(pilot.APPROVAL_ROOT / "terminal.json"),
        "worker_completion_sha256": terminal["worker_completion_sha256"],
        "pilot_image_forwards": 144, "pilot_text_forwards": 2,
        "repeat_parity_passed": True, "feature_sample_join_and_saved_readback_passed": True,
        "saved_prompt_logit_reconstruction_passed": True, "cache_keys_include_labels": False,
        "model_free_all_outer_and_pseudo_domain_consumer_checks_passed": True,
        "pilot_outer_target": "OULU-NPU", "pilot_sources": config["source_domains"],
        "pilot_input_count": 24, "media_decode_calls": 0, "detector_calls": 0,
        "full_feature_extraction": False, "classifier_fits": 0, "calibrator_fits": 0, "risk_fits": 0,
        "target_evaluation": False, "scientific_source_dry_run_complete": False, "scientific_readiness": False,
        "stage_errors": stage_errors,
        "gpu_peak_receipt_scope": "persisted_per_model_peaks_cover_image_pass; text_pass_caps_checked_but_final_peak_not_persisted",
        "technical_full_source_projection": {
            "not_execution_authority": True, "source_successes": 6855,
            "float32_feature_payload_bytes": 6855 * (1536 + 1536 + 512) * 4,
            "image_forward_only_seconds": sum(
                value["forward_seconds"] / value["forward_calls"] * 6855 for value in worker["models"].values()),
            "limitations": "24-source-sample projection excludes full input hash/PNG IO, startup, text, sharding, fold logic and retries; not wall-time guarantee",
        },
        "wall_seconds_from_original_approval_through_closure": time.time() - approval["started_unix_seconds"],
        "current_owned_new_temporary_bytes": pilot.size(),
        "implementation_sha256": {name: pilot.digest(ROOT / name) for name in (
            "scripts/integrate_source295.py", "scripts/pilot_source295.py", "scripts/close_source295.py",
            "src/fas/source_stage.py", "src/fas/frozen_features.py",
            "tests/test_source_stage.py", "tests/test_frozen_features.py")},
        "summary_sha256": {name: pilot.digest(ROOT / "manifests" / name)
                           for name in ("dataset_summary.csv", "split_summary.csv")},
        "final_exact_commit_ci": "collect_after_publication",
    }
    pilot.enforce(approval, final=True)
    write_immutable_record(pilot.APPROVAL_ROOT / "closure.json", report)
    write_immutable_record(ROOT / "results/phase1/source-handoff295-v1.json", report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    close()
