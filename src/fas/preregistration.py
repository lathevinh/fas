"""Typed, evidence-backed validation for staged preregistration readiness."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
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
    "source_recipe_v1.yaml",
    "environment_v1.yaml",
)
MICO_DOMAINS = {"OULU-NPU", "CASIA-FASD", "Replay-Attack", "MSU-MFSD"}
ALL_DATASETS = MICO_DOMAINS | {"SiW-M"}
STAGES = ("schema", "data", "pre-pilot", "confirmatory")
DATASET_COLUMNS = (
    "dataset", "audit_status", "subjects", "bona_videos", "attack_videos",
    "attack_families", "metadata_source", "manifest_sha256",
)
SPLIT_COLUMNS = (
    "dataset", "audit_status", "train_subjects", "branch_calibration_subjects",
    "g_domain_subjects", "routing_validation_subjects", "g_attack_subjects",
    "train_attack_videos", "branch_calibration_attack_videos",
    "g_domain_attack_videos", "routing_validation_attack_videos",
    "g_attack_attack_videos", "role_manifest_sha256",
)
FAMILY_TERMS = {"print", "printed", "display", "displayed", "replay", "mask", "masked"}
METADATA_COLUMNS = ("dataset", "subject_id", "video_id", "binary_label", "attack_family", "official_split")
ROLE_COLUMNS = ("dataset", "subject_id", "video_id", "binary_label", "role")
ROLES = ("train", "branch_calibration", "g_domain", "routing_validation", "g_attack")


def load_config(path: Path) -> dict[str, Any]:
    """Load JSON-compatible YAML without adding a runtime YAML dependency."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def validate(root: Path, require_counts: bool = True) -> list[str]:
    """Backward-compatible validation; strict mode means confirmatory readiness."""
    return validate_stage(root, "confirmatory" if require_counts else "schema")


def validate_stage(root: Path, stage: str) -> list[str]:
    if stage not in STAGES:
        raise ValueError(f"stage must be one of {', '.join(STAGES)}")
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

    _validate_config_schema(configs, errors)

    if STAGES.index(stage) >= STAGES.index("data"):
        _validate_data_evidence(root, errors)
    if STAGES.index(stage) >= STAGES.index("pre-pilot"):
        pilot = configs.get("pilot_selection_v1.yaml", {})
        if pilot.get("pilot_label_access_status") != "attested_not_inspected":
            errors.append("owner must attest that pilot labels were not inspected before freeze")
        freeze_path = root / "results" / "stage0" / "freeze_record.json"
        if not freeze_path.exists():
            errors.append("missing immutable Stage-0 freeze record")
        else:
            _validate_freeze_record(root, freeze_path, errors)
        _validate_model_pins(root, configs, errors)
    if stage == "confirmatory":
        _validate_confirmatory_thresholds(configs.get("evaluation_v1.yaml", {}), errors)
    return errors


def artifact_hashes(root: Path) -> dict[str, str]:
    paths = [root / "configs" / name for name in CONFIG_FILES]
    paths += [root / "manifests" / "dataset_summary.csv", root / "manifests" / "split_summary.csv"]
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths
        if path.exists()
    }


def _validate_freeze_record(root: Path, path: Path, errors: list[str]) -> None:
    try:
        record = load_config(path)
    except (ValueError, json.JSONDecodeError) as exc:
        errors.append(f"invalid freeze record: {exc}")
        return
    recorded = record.get("artifact_sha256")
    if not isinstance(recorded, dict) or recorded != artifact_hashes(root):
        errors.append("freeze record hashes do not match current artifacts")
    if not isinstance(record.get("created_from_commit"), str) or len(record["created_from_commit"]) != 40:
        errors.append("freeze record requires a 40-character source commit")


def _validate_model_pins(root: Path, configs: dict[str, dict[str, Any]], errors: list[str]) -> None:
    environment = configs.get("environment_v1.yaml", {})
    packages = environment.get("packages", {})
    lockfile = environment.get("lockfile")
    if environment.get("status") != "locked" or not isinstance(packages, dict) or not packages or any(not value for value in packages.values()):
        errors.append("model environment must have exact package pins before pilot")
    if not isinstance(lockfile, str) or not lockfile or not _sha256_string(environment.get("lockfile_sha256", "")):
        errors.append("model environment lockfile and SHA-256 are required before pilot")
    elif not (root / lockfile).exists() or hashlib.sha256((root / lockfile).read_bytes()).hexdigest() != environment["lockfile_sha256"]:
        errors.append("model environment lockfile hash does not match")

    candidates = configs.get("vlm_candidates_v1.yaml", {}).get("candidates", [])
    if any(not candidate.get("library_revision") or not _sha256_string(candidate.get("weight_sha256", "")) for candidate in candidates if isinstance(candidate, dict)):
        errors.append("every VLM candidate requires a library revision and weight SHA-256 before pilot")
    detector_hash = configs.get("preprocessing_v1.yaml", {}).get("face", {}).get("detector_weight_sha256")
    if not _sha256_string(detector_hash or ""):
        errors.append("detector weight SHA-256 is required before pilot")
    if not (root / "results" / "stage0" / "anchor_registry.json").exists():
        errors.append("source-trained DINO anchor registry is required before pilot")


def _validate_config_schema(configs: dict[str, dict[str, Any]], errors: list[str]) -> None:
    core = configs.get("prompts_core_v1.yaml", {})
    classes = core.get("classes")
    if not isinstance(classes, dict) or not _string_list(classes.get("live")) or not _string_list(classes.get("spoof")):
        errors.append("core prompts require nonempty live and spoof string lists")
    elif any(re.search(rf"\b{term}\b", prompt.lower()) for prompt in classes["spoof"] for term in FAMILY_TERMS):
        errors.append("core spoof prompts must not name held-out attack families")

    auxiliary = configs.get("prompts_aux_v1.yaml", {})
    if auxiliary.get("affects_core_probability") is not False or not isinstance(auxiliary.get("concepts"), dict):
        errors.append("auxiliary prompts must define concepts and never affect core probability")

    candidate_config = configs.get("vlm_candidates_v1.yaml", {})
    candidates = candidate_config.get("candidates")
    required_candidate = {"id", "library", "library_revision", "model", "pretrained", "weight_sha256", "resolution", "crop_mode", "normalization", "tokenizer", "precision", "backend"}
    if candidate_config.get("immutable_ids") is not True or not isinstance(candidates, list) or len(candidates) < 2:
        errors.append("VLM candidates require immutable IDs and at least two entries")
    else:
        ids = []
        for candidate in candidates:
            if not isinstance(candidate, dict) or not required_candidate <= candidate.keys():
                errors.append("every VLM candidate must contain the complete typed recipe")
                continue
            ids.append(candidate["id"])
            if not isinstance(candidate["id"], str) or not candidate["id"] or not _positive_int(candidate["resolution"]):
                errors.append("candidate ID must be nonempty and resolution a positive integer")
        if len(ids) != len(set(ids)):
            errors.append("VLM candidate IDs must be unique")

    pilot = configs.get("pilot_selection_v1.yaml", {})
    confirmatory = pilot.get("confirmatory_domains")
    if not isinstance(confirmatory, list):
        errors.append("confirmatory domains must be a list")
    else:
        domains = {pilot.get("pilot_domain"), *confirmatory}
        if domains != MICO_DOMAINS or len(confirmatory) != 3:
            errors.append("pilot and three confirmatory domains must partition MICO")
    if not _positive_number(pilot.get("latency_ceiling_ms")) or pilot.get("optimization") != "minimize":
        errors.append("pilot selection requires a positive latency ceiling and minimize objective")
    selection_dino = pilot.get("selection_dino")
    if not isinstance(selection_dino, dict) or not isinstance(selection_dino.get("seed"), int) or not selection_dino.get("model"):
        errors.append("pilot selection requires a fixed DINO model and integer seed")

    preprocessing = configs.get("preprocessing_v1.yaml", {})
    for section in ("frame_policy", "face", "dino", "latency"):
        if not isinstance(preprocessing.get(section), dict) or not preprocessing[section]:
            errors.append(f"preprocessing requires nonempty {section} section")
    latency = preprocessing.get("latency", {})
    for key in ("batch_size", "warmup_runs", "timed_runs"):
        if not _positive_int(latency.get(key)):
            errors.append(f"latency {key} must be a positive integer")
    if not _positive_number(latency.get("ceiling_ms")):
        errors.append("latency ceiling_ms must be positive")

    seeds = configs.get("seeds_v1.yaml", {}).get("seeds")
    if not isinstance(seeds, list) or len(seeds) != 3 or len(seeds) != len(set(seeds)) or not all(isinstance(seed, int) for seed in seeds):
        errors.append("exactly three unique integer primary seeds are required")

    evaluation = configs.get("evaluation_v1.yaml", {})
    if evaluation.get("risk_population") != "face_detector_success_only" or evaluation.get("end_to_end_population") != "all_original_transactions":
        errors.append("evaluation populations must distinguish risk from end-to-end transactions")
    bootstrap = evaluation.get("bootstrap_unit")
    if not isinstance(bootstrap, dict) or set(bootstrap) != ALL_DATASETS or not all(value in {"subject", "video"} for value in bootstrap.values()):
        errors.append("bootstrap units must cover every dataset with subject or video")
    if not isinstance(evaluation.get("minimum_effects"), dict) or not isinstance(evaluation.get("oof_to_final_validity"), dict):
        errors.append("evaluation requires effect and OOF-validity specifications")
    if evaluation.get("confirmatory_firewall") != "official_target_evaluation_partitions_unseen":
        errors.append("evaluation must declare the test-partition-unseen firewall")
    inference = evaluation.get("confirmatory_inference", {})
    if not _positive_int(inference.get("bootstrap_repetitions")) or not _unit_interval(inference.get("confidence_level"), strict=True):
        errors.append("confirmatory inference requires bootstrap repetitions and confidence level")
    if inference.get("below_n_min") != "inconclusive_not_fail" or inference.get("target_threshold_switching") is not False:
        errors.append("confirmatory inference must freeze inconclusive and threshold-switching rules")
    security = evaluation.get("security_operating_point", {})
    if not _unit_interval(security.get("primary_alpha"), strict=True) or security.get("interpretation") != "nominal_empirical_constraint":
        errors.append("primary security point must be a nominal empirical alpha")

    recipe = configs.get("source_recipe_v1.yaml", {})
    for section in ("anchor", "branch_calibration", "risk_model", "source_threshold"):
        if not isinstance(recipe.get(section), dict) or not recipe[section]:
            errors.append(f"source recipe requires nonempty {section} section")
    threshold = recipe.get("source_threshold", {})
    if not _unit_interval(threshold.get("primary_alpha"), strict=True):
        errors.append("primary source alpha must be strictly between zero and one")
    if threshold.get("selection_rule") != "largest threshold satisfying empirical APCER <= alpha in every source domain":
        errors.append("source threshold rule must match spoof-score polarity")

    environment = configs.get("environment_v1.yaml", {})
    if not environment.get("python_requires") or not isinstance(environment.get("packages"), dict):
        errors.append("environment config requires Python range and package map")


def _validate_data_evidence(root: Path, errors: list[str]) -> None:
    datasets = _read_summary(root / "manifests" / "dataset_summary.csv", DATASET_COLUMNS, errors)
    splits = _read_summary(root / "manifests" / "split_summary.csv", SPLIT_COLUMNS, errors)
    if not datasets or not splits:
        return
    metadata_records = _validate_dataset_rows(root, datasets, errors)
    role_records = _validate_split_rows(root, splits, errors)
    for dataset in ALL_DATASETS:
        metadata = {
            (row["subject_id"], row["video_id"]): row["binary_label"]
            for row in metadata_records.get(dataset, [])
        }
        for row in role_records.get(dataset, []):
            key = (row["subject_id"], row["video_id"])
            if key not in metadata or metadata[key] != row["binary_label"]:
                errors.append(f"{dataset} role record does not match audited metadata: {key}")


def _read_summary(path: Path, columns: tuple[str, ...], errors: list[str]) -> dict[str, dict[str, str]]:
    if not path.exists():
        errors.append(f"missing manifest summary: {path}")
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != columns:
            errors.append(f"{path.name} columns do not match the required schema")
            return {}
        rows = list(reader)
    names = [row["dataset"] for row in rows]
    if set(names) != ALL_DATASETS or len(names) != len(set(names)):
        errors.append(f"{path.name} must contain each required dataset exactly once")
        return {}
    return {row["dataset"]: row for row in rows}


def _validate_dataset_rows(
    root: Path,
    rows: dict[str, dict[str, str]],
    errors: list[str],
) -> dict[str, list[dict[str, str]]]:
    evidence_records: dict[str, list[dict[str, str]]] = {}
    for dataset, row in rows.items():
        if row["audit_status"] != "complete":
            errors.append(f"dataset_summary.csv has unaudited dataset: {dataset}")
        for column in ("subjects", "bona_videos", "attack_videos", "attack_families"):
            if not _nonnegative_integer_string(row[column], positive=True):
                errors.append(f"dataset_summary.csv {dataset} {column} must be a positive integer")
        if not row["metadata_source"]:
            errors.append(f"dataset_summary.csv {dataset} metadata_source is required")
        evidence = root / "manifests" / "private" / f"{_slug(dataset)}_metadata.csv"
        if _validate_evidence_hash(evidence, row["manifest_sha256"], f"{dataset} metadata", errors):
            records = _read_evidence(evidence, METADATA_COLUMNS, dataset, errors)
            if records:
                evidence_records[dataset] = records
                _reconcile_dataset_summary(dataset, row, records, errors)
    return evidence_records


def _validate_split_rows(
    root: Path,
    rows: dict[str, dict[str, str]],
    errors: list[str],
) -> dict[str, list[dict[str, str]]]:
    evidence_records: dict[str, list[dict[str, str]]] = {}
    for dataset, row in rows.items():
        if row["audit_status"] != "complete":
            errors.append(f"split_summary.csv has unaudited dataset: {dataset}")
        required_roles = {"train", "branch_calibration", "routing_validation"}
        required_roles.add("g_attack" if dataset == "SiW-M" else "g_domain")
        for role in ROLES:
            for suffix in ("subjects", "attack_videos"):
                column = f"{role}_{suffix}"
                if role in required_roles and not _nonnegative_integer_string(row[column], positive=True):
                    errors.append(f"split_summary.csv {dataset} {column} must be a positive integer")
                if role not in required_roles and row[column] not in ("", "0"):
                    errors.append(f"split_summary.csv {dataset} {column} is not applicable")
        evidence = root / "manifests" / "private" / f"{_slug(dataset)}_roles.csv"
        if _validate_evidence_hash(evidence, row["role_manifest_sha256"], f"{dataset} roles", errors):
            records = _read_evidence(evidence, ROLE_COLUMNS, dataset, errors)
            if records:
                evidence_records[dataset] = records
                _reconcile_split_summary(dataset, row, records, errors)
    return evidence_records


def _validate_evidence_hash(path: Path, expected: str, label: str, errors: list[str]) -> bool:
    if not path.exists():
        errors.append(f"missing private evidence file for {label}: {path.name}")
        return False
    if not _sha256_string(expected):
        errors.append(f"{label} SHA-256 must be 64 lowercase hexadecimal characters")
        return False
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        errors.append(f"{label} SHA-256 does not match the evidence file")
        return False
    return True


def _read_evidence(
    path: Path,
    columns: tuple[str, ...],
    dataset: str,
    errors: list[str],
) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != columns:
            errors.append(f"{path.name} columns do not match the required schema")
            return []
        rows = list(reader)
    if not rows or any(row["dataset"] != dataset for row in rows):
        errors.append(f"{path.name} must contain nonempty records only for {dataset}")
        return []
    keys = [(row["subject_id"], row["video_id"]) for row in rows]
    if any(not subject or not video for subject, video in keys) or len(keys) != len(set(keys)):
        errors.append(f"{path.name} requires unique nonempty subject/video keys")
    if any(row["binary_label"] not in {"bona_fide", "attack"} for row in rows):
        errors.append(f"{path.name} contains invalid binary labels")
    return rows


def _reconcile_dataset_summary(
    dataset: str,
    summary: dict[str, str],
    records: list[dict[str, str]],
    errors: list[str],
) -> None:
    expected = {
        "subjects": len({row["subject_id"] for row in records}),
        "bona_videos": sum(row["binary_label"] == "bona_fide" for row in records),
        "attack_videos": sum(row["binary_label"] == "attack" for row in records),
        "attack_families": len({row["attack_family"] for row in records if row["binary_label"] == "attack"}),
    }
    for column, value in expected.items():
        if summary[column].isdigit() and int(summary[column]) != value:
            errors.append(f"dataset_summary.csv {dataset} {column} does not reconcile with metadata")


def _reconcile_split_summary(
    dataset: str,
    summary: dict[str, str],
    records: list[dict[str, str]],
    errors: list[str],
) -> None:
    subject_roles: dict[str, set[str]] = {}
    for row in records:
        if row["role"] not in ROLES:
            errors.append(f"{dataset} role manifest contains invalid role {row['role']!r}")
            continue
        subject_roles.setdefault(row["subject_id"], set()).add(row["role"])
    overlap = [subject for subject, roles in subject_roles.items() if len(roles) > 1]
    if overlap:
        errors.append(f"{dataset} role manifest assigns subjects to multiple roles")
    for role in ROLES:
        role_rows = [row for row in records if row["role"] == role]
        expected = {
            f"{role}_subjects": len({row["subject_id"] for row in role_rows}),
            f"{role}_attack_videos": sum(row["binary_label"] == "attack" for row in role_rows),
        }
        for column, value in expected.items():
            if summary[column] not in ("", "0") and summary[column].isdigit() and int(summary[column]) != value:
                errors.append(f"split_summary.csv {dataset} {column} does not reconcile with roles")


def _validate_confirmatory_thresholds(evaluation: dict[str, Any], errors: list[str]) -> None:
    effects = evaluation.get("minimum_effects", {})
    effect_keys = ("delta_hetero", "delta_cf_aupr", "delta_dis_aupr", "target_harm_tolerance")
    if effects.get("status") != "frozen" or not all(_positive_number(effects.get(key)) for key in effect_keys):
        errors.append("confirmatory minimum effects must be frozen, finite, and positive")
    validity = evaluation.get("oof_to_final_validity", {})
    if validity.get("sanity_threshold_status") != "frozen" or not _positive_number(validity.get("threshold_value")):
        errors.append("OOF-to-final validity threshold must be frozen, finite, and positive")
    if validity.get("metric") not in {"prediction_error_aupr", "auroc"} or validity.get("direction") != "greater_equal":
        errors.append("OOF-to-final validity requires an executable metric and direction")
    gates = evaluation.get("source_derived_gates", {})
    if gates.get("status") != "frozen":
        errors.append("source-derived continuation and routing gates must be frozen")
    if not _positive_int(gates.get("n_min_false_accepts")):
        errors.append("N_min false accepts must be a positive integer")
    for key in ("farr_lcb_gamma", "diagnostic_apcer", "routing_bpcerr_increase_beta", "branch_competency_balanced_accuracy"):
        if not _unit_interval(gates.get(key), strict=True):
            errors.append(f"source-derived {key} must be strictly between zero and one")


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0


def _unit_interval(value: Any, strict: bool = False) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        return False
    return 0 < value < 1 if strict else 0 <= value <= 1


def _nonnegative_integer_string(value: str, positive: bool = False) -> bool:
    if not value or not value.isdigit():
        return False
    number = int(value)
    return number > 0 if positive else number >= 0


def _sha256_string(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _slug(dataset: str) -> str:
    return dataset.lower().replace("-", "_")
