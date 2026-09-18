"""Typed, evidence-backed validation for staged preregistration readiness."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from .freeze import build_analysis_freeze_record

CONFIG_FILES = (
    "experiment_core_v1.yaml",
    "claims_v1.yaml",
    "prompts_core_v1.yaml",
    "prompts_aux_v1.yaml",
    "preprocessing_v2.yaml",
    "seeds_v1.yaml",
    "source_recipe_v2.yaml",
    "environment_v1.yaml",
)
MICO_DOMAINS = {"OULU-NPU", "CASIA-FASD", "Replay-Attack", "MSU-MFSD"}
ALL_DATASETS = MICO_DOMAINS | {"SiW-M"}
STAGES = (
    "schema",
    "data-audit",
    "source-dry-run",
    "analysis-freeze",
    "locked-evaluation",
)
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
    """Validate schema or the first evidence-backed data stage."""
    return validate_stage(root, "data-audit" if require_counts else "schema")


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

    if STAGES.index(stage) >= STAGES.index("data-audit"):
        _validate_data_evidence(root, errors)
    if STAGES.index(stage) >= STAGES.index("source-dry-run"):
        _validate_source_dry_run(root, errors)
    if STAGES.index(stage) >= STAGES.index("analysis-freeze"):
        _validate_analysis_freeze(root, errors)
    if stage == "locked-evaluation":
        authorization = root / "results" / "locked-evaluation" / "authorization.json"
        if not authorization.exists():
            errors.append("locked-evaluation remains blocked until authorization exists")
    return errors


def artifact_hashes(root: Path) -> dict[str, str]:
    paths = [root / "configs" / name for name in CONFIG_FILES]
    paths += [root / "manifests" / "dataset_summary.csv", root / "manifests" / "split_summary.csv"]
    for directory in (root / "src" / "fas", root / "scripts"):
        paths.extend(sorted(directory.rglob("*.py")))
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths
        if path.exists()
    }


def _validate_source_dry_run(root: Path, errors: list[str]) -> None:
    path = root / "results" / "source-dry-run" / "evidence.json"
    if not path.exists():
        errors.append("missing source-dry-run evidence")
        return
    try:
        evidence = load_config(path)
    except (ValueError, json.JSONDecodeError) as exc:
        errors.append(f"invalid source-dry-run evidence: {exc}")
        return
    if evidence.get("version") != 1:
        errors.append("source-dry-run evidence requires schema version 1")
    if evidence.get("no_target_selection_input") is not True:
        errors.append("source-dry-run evidence must exclude target selection input")
    recorded = evidence.get("artifact_sha256")
    if not isinstance(recorded, dict) or not recorded or any(
        not isinstance(name, str) or not name or not _sha256_string(digest)
        for name, digest in recorded.items()
    ):
        errors.append("source-dry-run evidence requires named artifact SHA-256 values")
    if not _sha256_string(evidence.get("source_policy_sha256", "")):
        errors.append("source-dry-run evidence requires a source policy SHA-256")


def _validate_analysis_freeze(root: Path, errors: list[str]) -> None:
    path = root / "results" / "analysis-freeze" / "freeze_record.json"
    if not path.exists():
        errors.append("missing immutable analysis-freeze record")
        return
    evidence_path = root / "results" / "source-dry-run" / "evidence.json"
    if not evidence_path.exists():
        errors.append("analysis freeze requires source-dry-run evidence")
        return
    try:
        record = load_config(path)
        evidence = load_config(evidence_path)
        experiment = load_config(root / "configs" / "experiment_core_v1.yaml")
        seed_config = load_config(root / "configs" / "seeds_v1.yaml")
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
        status = subprocess.check_output(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).splitlines()
        allowed_untracked = "?? results/analysis-freeze/freeze_record.json"
        if any(line != allowed_untracked for line in status):
            errors.append("analysis freeze requires a clean worktree")
        if evidence.get("no_target_selection_input") is not True:
            errors.append("analysis freeze requires source evidence excluding target selection input")
            return
        expected = build_analysis_freeze_record(
            created_at_utc=record.get("created_at_utc", ""),
            created_from_commit=commit,
            artifact_sha256=artifact_hashes(root),
            source_evidence_sha256=hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
            source_policy_sha256=evidence.get("source_policy_sha256", ""),
            outer_targets=experiment.get("outer_domains", []),
            seeds=seed_config.get("seeds", []),
            no_target_selection_input=evidence.get("no_target_selection_input", False),
        )
    except (ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        errors.append(f"invalid analysis-freeze record: {exc}")
        return
    if record != expected:
        errors.append("analysis-freeze record does not match current frozen artifacts")


def _validate_config_schema(configs: dict[str, dict[str, Any]], errors: list[str]) -> None:
    experiment = configs.get("experiment_core_v1.yaml", {})
    forbidden = {
        "pilot_domain",
        "confirmatory_domains",
        "pilot_label_access_status",
        "claim_sequence",
        "selection_seed",
    }
    present_forbidden = sorted(forbidden & experiment.keys())
    if present_forbidden:
        errors.append(
            "experiment config contains forbidden legacy field(s): "
            + ", ".join(present_forbidden)
        )
    if experiment.get("version") != 1 or not experiment.get("study_id"):
        errors.append("canonical experiment requires version 1 and a study ID")
    domains = experiment.get("outer_domains")
    if not isinstance(domains, list) or set(domains) != MICO_DOMAINS or len(domains) != 4:
        errors.append("canonical experiment must contain each MCIO outer domain exactly once")
    expected_references = {
        "claim_spec": "claims_v1.yaml",
        "seed_spec": "seeds_v1.yaml",
        "preprocessing_spec": "preprocessing_v2.yaml",
        "source_recipe": "source_recipe_v2.yaml",
    }
    for field, expected in expected_references.items():
        if experiment.get(field) != expected:
            errors.append(f"canonical experiment {field} must reference {expected}")

    models = experiment.get("models", {})
    if not isinstance(models, dict) or set(models) != {"dino_reg", "dino_plain", "openclip"}:
        errors.append("canonical experiment requires exactly three frozen model recipes")
        models = {}
    dino_reg = models.get("dino_reg", {})
    dino_plain = models.get("dino_plain", {})
    openclip = models.get("openclip", {})
    if dino_reg.get("model") != "dinov2_vitb14_reg4" or dino_reg.get("state") != "frozen":
        errors.append("DINOv2-Reg must be frozen dinov2_vitb14_reg4")
    if dino_plain.get("model") != "dinov2_vitb14" or dino_plain.get("state") != "frozen":
        errors.append("same-family control must use frozen plain dinov2_vitb14")
    if any(model.get("pooling") != "cls_plus_mean_patch" for model in (dino_reg, dino_plain)):
        errors.append("both DINO branches require fixed CLS plus mean-patch pooling")
    expected_openclip = {
        "model": "ViT-B-16",
        "pretrained": "laion2b_s34b_b88k",
        "state": "frozen",
        "resolution": 224,
        "preprocessing": "checkpoint_native",
        "crop_scale": 1.30,
        "prompts": "prompts_core_v1.yaml",
    }
    if any(openclip.get(key) != value for key, value in expected_openclip.items()):
        errors.append("OpenCLIP must use the frozen ViT-B-16 LAION2B native-224 recipe")

    systems = experiment.get("systems", {})
    expected_systems = {
        "heterogeneous": ["dino_reg", "openclip"],
        "same_family": ["dino_reg", "dino_plain"],
    }
    for system_id, branches in expected_systems.items():
        system = systems.get(system_id, {}) if isinstance(systems, dict) else {}
        if system.get("branches") != branches or system.get("fusion") != "calibrated_equal_average":
            errors.append(f"{system_id} system recipe does not match the frozen contract")

    core = configs.get("prompts_core_v1.yaml", {})
    classes = core.get("classes")
    if not isinstance(classes, dict) or not _string_list(classes.get("live")) or not _string_list(classes.get("spoof")):
        errors.append("core prompts require nonempty live and spoof string lists")
    elif any(re.search(rf"\b{term}\b", prompt.lower()) for prompt in classes["spoof"] for term in FAMILY_TERMS):
        errors.append("core spoof prompts must not name held-out attack families")
    if core.get("frozen_before_target_evaluation") is not True:
        errors.append("core prompts must freeze before target evaluation")

    auxiliary = configs.get("prompts_aux_v1.yaml", {})
    if auxiliary.get("affects_core_probability") is not False or not isinstance(auxiliary.get("concepts"), dict):
        errors.append("auxiliary prompts must define concepts and never affect core probability")

    preprocessing = configs.get("preprocessing_v2.yaml", {})
    for section in ("frame_policy", "face", "dino", "openclip"):
        if not isinstance(preprocessing.get(section), dict) or not preprocessing[section]:
            errors.append(f"preprocessing requires nonempty {section} section")
    frame_policy = preprocessing.get("frame_policy", {})
    if frame_policy.get("primary") != "middle_decodable_frame_in_official_interval" or frame_policy.get("detector_success_replacement") is not False:
        errors.append("primary frame selection must be deterministic and precede detection")
    face = preprocessing.get("face", {})
    if face.get("context_scale") != 1.30 or face.get("detector_failure_action") != "terminal_non_accept":
        errors.append("face preprocessing must preserve the fixed crop and detector-failure action")
    if preprocessing.get("openclip") != {"resolution": 224, "normalization": "checkpoint_native"}:
        errors.append("OpenCLIP preprocessing must remain checkpoint-native at 224")

    seed_config = configs.get("seeds_v1.yaml", {})
    if forbidden & seed_config.keys():
        errors.append("seed config contains forbidden legacy selection field")
    seeds = seed_config.get("seeds")
    if not isinstance(seeds, list) or len(seeds) != 3 or len(seeds) != len(set(seeds)) or not all(isinstance(seed, int) for seed in seeds):
        errors.append("exactly three unique integer primary seeds are required")

    recipe = configs.get("source_recipe_v2.yaml", {})
    for section in ("representation", "branch_head", "branch_calibration", "risk_model"):
        if not isinstance(recipe.get(section), dict) or not recipe[section]:
            errors.append(f"source recipe requires nonempty {section} section")
    if recipe.get("representation") != {"dino_reg": "cls_plus_mean_patch", "dino_plain": "cls_plus_mean_patch"}:
        errors.append("source recipe requires fixed CLS plus mean-patch representations")
    expected_solver = {
        "branch_head": {
            "family": "linear_logistic",
            "checkpoint_rule": "lowest_source_validation_domain_macro_acer_then_earlier_epoch",
        },
        "branch_calibration": {
            "family": "monotone_affine_logistic",
            "slope_parameterization": "softplus_theta_plus_1e-6",
            "objective": "class_balanced_within_domain_equal_domain_bce",
        },
        "risk_model": {
            "family": "logistic_regression",
            "regularization": "l2",
            "inverse_regularization_strength": 1.0,
            "objective": "natural_prevalence_within_domain_equal_domain_bce",
        },
        "risk_features": ["R_q", "R_D", "R_V", "R_DV", "R_DVd", "R_DVdm"],
        "gate_partition": "G_domain",
    }
    if any(recipe.get(key) != value for key, value in expected_solver.items()):
        errors.append("source recipe does not match the frozen solver contract")
    if recipe.get("oof_strategies") != ["domain_oof", "matched_sample_oof"]:
        errors.append("source recipe requires matched domain and sample OOF strategies")
    if recipe.get("target_tuning_allowed") is not False:
        errors.append("source recipe must forbid target tuning")

    _validate_claims(configs.get("claims_v1.yaml", {}), errors)

    environment = configs.get("environment_v1.yaml", {})
    if not environment.get("python_requires") or not isinstance(environment.get("packages"), dict):
        errors.append("environment config requires Python range and package map")


def _validate_claims(config: dict[str, Any], errors: list[str]) -> None:
    claims = config.get("claims")
    required = {
        "rq1_oof_transfer",
        "rq1_operational_utility",
        "rq2_complete_system",
        "classifier_benefit",
        "cross_foundation_attribution",
        "explicit_disagreement",
        "quality_attribution",
        "optional_routing",
    }
    if config.get("version") != 1 or not isinstance(claims, dict) or set(claims) != required:
        errors.append("claim spec must define exactly the frozen typed claim set")
        return
    rq1 = claims["rq1_oof_transfer"]
    expected_rq1 = {
        "endpoint": "non_interpolated_prediction_error_ap",
        "population": "detector_success",
        "contrast": "domain_oof_minus_matched_sample_oof",
        "fixed_error_set": "heterogeneous_e_DV",
        "seed_aggregation": "equal_mean_all_three_estimable",
        "target_aggregation": "equal_mean_all_four",
        "n_error_min": 20,
        "minimum_eligible_targets": 3,
    }
    if any(rq1.get(key) != value for key, value in expected_rq1.items()):
        errors.append("RQ1 claim does not match the frozen fixed-error AP contract")
    if rq1.get("bootstrap_repetitions") != 2000 or rq1.get("confidence_level") != 0.95:
        errors.append("RQ1 requires the frozen paired cluster bootstrap")
    rq2 = claims["rq2_complete_system"]
    expected_rq2 = {
        "endpoint": "class_balanced_raw_aurc",
        "population": "common_detector_success_mask",
        "contrast": "U_same_minus_U_heterogeneous",
        "class_aggregation": "equal_attack_bona_fide_mean",
        "delta_min": 0.01,
        "minimum_positive_targets": 3,
        "minimum_positive_seed_macros": 2,
        "target_selective_harm_max": 0.02,
        "fa_end2end_macro_harm_max": 0.01,
        "fa_end2end_target_harm_max": 0.02,
        "bfnr_end2end_macro_harm_max": 0.01,
        "bfnr_end2end_target_harm_max": 0.02,
        "coverage_role": "required_explanatory_not_decision_predicate",
    }
    if any(rq2.get(key) != value for key, value in expected_rq2.items()):
        errors.append("RQ2 claim does not match the frozen complete-system contract")
    if claims["rq1_operational_utility"].get("role") != "secondary_not_rq1_conjunct":
        errors.append("RQ1 operational utility must remain a separate consequence")
    routing = claims["optional_routing"]
    if routing.get("enabled") is not False or routing.get("core_readiness_dependency") is not False:
        errors.append("optional routing cannot be a core readiness dependency")
    competence = config.get("competence", {})
    complete = competence.get("complete_system", {})
    expected_complete = {
        "macro_auroc_min": 0.55,
        "macro_balanced_accuracy_min": 0.55,
        "macro_auroc_lcb_min_exclusive": 0.50,
        "score_range_min_exclusive": 0.000001,
        "both_classes_required": True,
        "finite_calibration_required": True,
    }
    if complete != expected_complete:
        errors.append("complete-system competence does not match the frozen contract")
    if competence.get("heterogeneous_risk_fit") != {"minimum_errors": 20, "minimum_correct": 20}:
        errors.append("heterogeneous risk-fit competence requires 20 errors and 20 correct")
    if competence.get("dino_anchor") != {"nondegeneracy_required": True}:
        errors.append("DINO anchor competence must require nondegeneracy")
    if competence.get("standalone_branch_failure_scope") != "standalone_claim_only":
        errors.append("standalone branch failure must remain scoped to its own claim")


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


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _nonnegative_integer_string(value: str, positive: bool = False) -> bool:
    if not value or not value.isdigit():
        return False
    number = int(value)
    return number > 0 if positive else number >= 0


def _sha256_string(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _slug(dataset: str) -> str:
    return dataset.lower().replace("-", "_")
