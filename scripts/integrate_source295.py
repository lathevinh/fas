"""Join accepted prepared source inputs without models, image decoding or media access."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.freeze import write_immutable_record
from fas.preregistration import validate_stage
from fas.source_stage import join_prepared, pilot_inputs, population_counts, require_source_input, source_inputs
from fas.source_use import POLICY_PATH, load_source_use

BASE = Path("/mnt/e/FAS-private/artifacts/phase1")
FROZEN = Path("/mnt/e/FAS-private/frozen/source_roles_v2")
USE = BASE / "siwmv2_source_use293_v1"
OUTPUT = BASE / "source_integration295_v1"
SPECS = {
    "OULU-NPU": ("oulu_preprocessing280_v1", "results/phase1/oulu-preprocessing280-completion-v1.json"),
    "MSU-MFSD": ("msu_recovery282_v1", "results/phase1/msu-local-audit282-v1.json"),
    "CASIA-FASD": ("casia_resume289_v1", "results/phase1/casia-local-audit289-v1.json"),
    "SiW-Mv2": ("siwmv2_preprocessing291_v1/blocked_closure", "results/phase1/siwmv2-blocked-readback291-v1.json"),
}


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def read_bound(path: Path, digest: str | None, pins: dict[str, str]) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"regular evidence required: {path.name}")
    payload = path.read_bytes()
    actual = sha(payload)
    if digest is not None and actual != digest:
        raise ValueError(f"accepted evidence SHA256 drift: {path.name}")
    pins[str(path)] = actual
    return json.loads(payload)


def verify_record(entry: dict, pins: dict[str, str]) -> None:
    path = Path(entry["record_path"])
    if not path.is_relative_to(BASE):
        raise ValueError("prepared transaction path escaped the accepted artifact root")
    txn = read_bound(path, entry["record_sha256"], pins)
    for key in ("video_id", "role", "binary_label", "detector_status", "selected_frame"):
        if txn[key] != entry[key]:
            raise ValueError("prepared manifest/raw transaction join drift")
    legacy = (entry.get("reused") is True
              and txn.get("config_sha256") == "ae051c75b2b8e2ee82463be9f344e5312380fe9848c64d370e1a45fa7ae97283")
    if "classifier_error" not in txn and not legacy:
        raise ValueError("only the accepted historical OULU image schema may omit classifier_error")
    if (txn["model_score"] is not None or ("classifier_error" in txn and txn["classifier_error"] is not None)
            or txn["replacement"]):
        raise ValueError("source integration may not invent classifier results or replace frames")
    for relative in entry.get("asset_sha256", {}):
        supplied = Path(entry["asset_root"]) / relative
        if (Path(relative).is_absolute() or ".." in Path(relative).parts
                or supplied.is_symlink() or not supplied.resolve().is_relative_to(BASE)
                or not supplied.is_file()):
            raise ValueError("prepared asset missing or escaped the accepted root")


def exercise(rows: list[dict]) -> dict:
    result = {}
    for target in sorted(SPECS):
        roles = {}
        for purpose in ("fitting", "calibration", "domain_use"):
            inputs = source_inputs(rows, outer_target=target, purpose=purpose)
            models = source_inputs(rows, outer_target=target, purpose=purpose, model_inputs_only=True)
            for row in inputs:
                require_source_input(row, outer_target=target, purpose=purpose)
            rejected = 0
            for row in rows:
                if row["dataset"] == target or not row["source_use_eligible"] or row["role"] != {
                        "fitting": "train", "calibration": "branch_calibration", "domain_use": "g_domain"}[purpose]:
                    try:
                        require_source_input(row, outer_target=target, purpose=purpose)
                    except ValueError:
                        rejected += 1
                    else:
                        raise ValueError("forbidden row entered fold-local source consumer")
            roles[purpose] = {"denominator": len(inputs), "model_inputs": len(models),
                              "retained_failures": len(inputs) - len(models), "rejected": rejected,
                              "domains": dict(Counter(row["dataset"] for row in inputs))}
        pseudo = {}
        for heldout in sorted(set(SPECS) - {target}):
            subset = source_inputs(rows, outer_target=target, pseudo_target=heldout, purpose="fitting")
            if any(row["dataset"] in {target, heldout} for row in subset):
                raise ValueError("whole outer/pseudo-target domain exclusion failed")
            pseudo[heldout] = len(subset)
        result[target] = {"roles": roles, "domain_oof_fit_denominators": pseudo}
    return result


def main() -> None:
    started = time.monotonic()
    pins = {}
    registry = json.loads((ROOT / "configs/role_policy_frozen_v2.yaml").read_bytes())
    context = load_source_use((ROOT / POLICY_PATH).read_bytes(), (USE / "effective_use_manifest.json").read_bytes(),
                              (USE / "overlay.json").read_bytes(), (USE / "owner_adoption.json").read_bytes())
    all_rows, totals = [], {}
    config_digest = sha((ROOT / "configs/preprocessing_v3.yaml").read_bytes())
    for dataset, (directory, public) in SPECS.items():
        slug = dataset.lower().replace("-", "_")
        canonical = read_bound(FROZEN / f"{slug}_canonical.json",
                               registry["frozen_artifact_sha256"][f"{slug}_canonical.json"], pins)
        role_path = FROZEN / f"{slug}_roles.csv"
        role_payload = role_path.read_bytes()
        if sha(role_payload) != registry["frozen_artifact_sha256"][role_path.name]:
            raise ValueError("permanent role bytes drift")
        pins[str(role_path)] = sha(role_payload)
        roles = list(csv.DictReader(role_payload.decode().splitlines()))
        receipt = read_bound(ROOT / public, None, pins)
        if dataset == "OULU-NPU":
            readback_hash = receipt["private_record_sha256"]["readback.json"]
            manifest_hash = receipt["private_record_sha256"]["full_manifest.json"]
        else:
            readback_hash = receipt["private_readback_sha256"] if dataset == "SiW-Mv2" else receipt["readback_sha256"]
            manifest_hash = receipt["full_manifest_sha256"] if dataset != "CASIA-FASD" else None
        directory = BASE / directory
        readback = read_bound(directory / "readback.json", readback_hash, pins)
        if manifest_hash is not None and manifest_hash != readback["full_manifest_sha256"]:
            raise ValueError("accepted full-manifest/readback link drift")
        manifest = read_bound(directory / "full_manifest.json", readback["full_manifest_sha256"], pins)
        for entry in manifest["rows"]:
            if entry.get("record_path") is not None:
                verify_record(entry, pins)
                if dataset == "SiW-Mv2":
                    parent = next(row for row in context.rows if row["video_id"] == entry["video_id"])
                    if parent["source_use_eligible"]:
                        purpose = {"train": "fitting", "branch_calibration": "calibration", "g_domain": "domain_use"}[parent["role"]]
                        context.bind_transaction(Path(entry["record_path"]).read_bytes(), purpose)
            elif dataset == "OULU-NPU" and entry["selected_frame"] is None:
                plan = read_bound(directory / "plan.json", receipt["private_record_sha256"]["plan.json"], pins)
                terminal = next(row for row in plan["terminal_transactions"] if row["video_id"] == entry["video_id"])
                if any(entry[key] != value for key, value in terminal.items()):
                    raise ValueError("preserved pre-detector OULU terminal drift")
            else:
                raise ValueError("prepared transaction lacks accepted provenance")
        joined = join_prepared(dataset, canonical["videos"], roles, manifest["rows"],
                               active_config_sha256=config_digest, siw_context=context if dataset == "SiW-Mv2" else None)
        all_rows.extend(joined)
        totals[dataset] = population_counts(joined)
    consumers = exercise(all_rows)
    chosen = pilot_inputs(all_rows)
    checks = {stage: validate_stage(ROOT, stage, frozen_root=FROZEN, source_use_root=USE)
              for stage in ("schema", "data-audit", "source-dry-run")}
    if checks["schema"] or checks["data-audit"]:
        raise ValueError(f"accepted schema/data audit failed during integration: {checks}")
    for name in ("configs/experiment_core_v1.yaml", "configs/preprocessing_v3.yaml",
                 "configs/source_recipe_v2.yaml", "configs/seeds_v1.yaml", POLICY_PATH,
                 "docs/294-review-doc293-siw-closure-and-four-dataset-handoff.md",
                 "scripts/integrate_source295.py", "src/fas/source_stage.py"):
        pins[str(ROOT / name)] = sha((ROOT / name).read_bytes())
    manifest = {"version": 1, "checkpoint": 295, "rows": all_rows, "input_sha256": pins,
                "source_use_binding": dict(context.binding), "active_config_sha256": config_digest}
    write_immutable_record(OUTPUT / "source_manifest.json", manifest)
    write_immutable_record(OUTPUT / "pilot_inputs.json", {"version": 1, "outer_target": "OULU-NPU",
                           "selection": "four_per_source_class_train_sha256_source295-pilot",
                           "source_manifest_sha256": sha((OUTPUT / "source_manifest.json").read_bytes()),
                           "rows": chosen})
    report = {
        "version": 1, "checkpoint": 295, "status": "model_free_source_integration_complete",
        "source_manifest_sha256": sha((OUTPUT / "source_manifest.json").read_bytes()),
        "pilot_inputs_sha256": sha((OUTPUT / "pilot_inputs.json").read_bytes()),
        "source_use_binding": dict(context.binding), "datasets": totals,
        "combined": population_counts(all_rows), "fold_consumers": consumers,
        "stage_errors": checks, "model_free_consumer_checks_passed": True,
        "model_free_checks_are_not_scientific_source_dry_run": True,
        "accepted_input_files": len(pins), "wall_seconds": time.monotonic() - started,
        "image_pixels_redecoded": 0, "media_decode_calls": 0, "detector_calls": 0,
        "model_forward_calls": 0, "fitted_scores": 0, "target_evaluation": False,
        "scientific_readiness": False,
    }
    write_immutable_record(OUTPUT / "integration.json", report)
    write_immutable_record(ROOT / "results/phase1/source-integration295-v1.json", report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    main()
