"""Validation for frozen preregistration artifacts and data-readiness counts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

CONFIG_FILES = (
    "prompts_core_v1.yaml",
    "prompts_aux_v1.yaml",
    "vlm_candidates_v1.yaml",
    "pilot_selection_v1.yaml",
    "preprocessing_v1.yaml",
    "seeds_v1.yaml",
    "evaluation_v1.yaml",
)
MICO_DOMAINS = {"OULU-NPU", "CASIA-FASD", "Replay-Attack", "MSU-MFSD"}


def load_config(path: Path) -> dict[str, Any]:
    """Load JSON-compatible YAML without adding a runtime YAML dependency."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def validate(root: Path, require_counts: bool = True) -> list[str]:
    errors: list[str] = []
    configs: dict[str, dict[str, Any]] = {}
    for name in CONFIG_FILES:
        path = root / "configs" / name
        if not path.exists():
            errors.append(f"missing config: {path.relative_to(root)}")
            continue
        try:
            configs[name] = load_config(path)
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(f"invalid config {name}: {exc}")

    if "prompts_core_v1.yaml" in configs:
        classes = configs["prompts_core_v1.yaml"].get("classes", {})
        if not classes.get("live") or not classes.get("spoof"):
            errors.append("core prompts require nonempty live and spoof lists")

    if "vlm_candidates_v1.yaml" in configs:
        candidates = configs["vlm_candidates_v1.yaml"].get("candidates", [])
        ids = [item.get("id") for item in candidates]
        if len(candidates) < 2 or None in ids or len(ids) != len(set(ids)):
            errors.append("VLM candidates require at least two unique immutable IDs")

    if "pilot_selection_v1.yaml" in configs:
        pilot = configs["pilot_selection_v1.yaml"]
        domains = {pilot.get("pilot_domain"), *pilot.get("confirmatory_domains", [])}
        if domains != MICO_DOMAINS or len(pilot.get("confirmatory_domains", [])) != 3:
            errors.append("pilot and three confirmatory domains must partition MICO")
        if require_counts and pilot.get("pilot_label_access_status") != "attested_not_inspected":
            errors.append("owner must attest that pilot labels were not inspected before freeze")

    if "seeds_v1.yaml" in configs:
        seeds = configs["seeds_v1.yaml"].get("seeds", [])
        if len(seeds) != 3 or len(seeds) != len(set(seeds)):
            errors.append("exactly three unique primary seeds are required")

    if require_counts and "evaluation_v1.yaml" in configs:
        evaluation = configs["evaluation_v1.yaml"]
        effects = evaluation.get("minimum_effects", {})
        if effects.get("status") != "frozen":
            errors.append("minimum meaningful effects are not frozen")
        validity = evaluation.get("oof_to_final_validity", {})
        if validity.get("sanity_threshold_status") != "frozen":
            errors.append("OOF-to-final validity threshold is not frozen")

    _validate_csv(root / "manifests" / "dataset_summary.csv", require_counts, errors)
    _validate_csv(root / "manifests" / "split_summary.csv", require_counts, errors)
    return errors


def artifact_hashes(root: Path) -> dict[str, str]:
    paths = [root / "configs" / name for name in CONFIG_FILES]
    paths += [root / "manifests" / "dataset_summary.csv", root / "manifests" / "split_summary.csv"]
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths
        if path.exists()
    }


def _validate_csv(path: Path, require_counts: bool, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing manifest summary: {path}")
        return
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        errors.append(f"empty manifest summary: {path.name}")
        return
    if require_counts:
        incomplete = [row.get("dataset", "unknown") for row in rows if row.get("audit_status") != "complete"]
        if incomplete:
            errors.append(f"{path.name} has unaudited datasets: {', '.join(incomplete)}")
        for row in rows:
            missing = [key for key, value in row.items() if key != "g_attack_subjects" and not value]
            if missing:
                errors.append(f"{path.name} {row.get('dataset', 'unknown')} missing: {', '.join(missing)}")
