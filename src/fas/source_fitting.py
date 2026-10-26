"""Deterministic source partitions, role-isolated fits and source risk features."""

from __future__ import annotations

from collections import defaultdict
import hashlib
from typing import Any

import numpy as np

from .source_stage import require_source_input


def identity(row: dict) -> str:
    return f"{row['dataset']}/{row['video_id']}"


def group_assignments(rows: list[dict], seed: int, folds: int) -> dict[str, int]:
    if folds < 2 or len({identity(row) for row in rows}) != len(rows):
        raise ValueError("unique originals and at least two group folds required")
    parent = list(range(len(rows)))

    def root(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    seen: dict[tuple, int] = {}
    for index, row in enumerate(rows):
        for key in (("group", row["dataset"], row["group_id"]),
                    ("frame", row["dataset"], row["selected_frame"]["rgb_sha256"])):
            if key in seen:
                parent[root(index)] = root(seen[key])
            seen[key] = index
    components: dict[int, list[dict]] = defaultdict(list)
    for index, row in enumerate(rows):
        components[root(index)].append(row)
    strata: dict[tuple, list[list[dict]]] = defaultdict(list)
    for component in components.values():
        labels = tuple(sorted({row["binary_label"] for row in component}))
        strata[(component[0]["dataset"], labels)].append(component)
    result = {}
    for components_in_stratum in strata.values():
        components_in_stratum.sort(key=lambda component: hashlib.sha256(
            f"{seed}:{min(identity(row) for row in component)}".encode()).hexdigest())
        for index, component in enumerate(components_in_stratum):
            for row in component:
                result[identity(row)] = index % folds
    return result


def check_classes(rows: list[dict]) -> None:
    domains = {row["dataset"] for row in rows}
    if not domains:
        raise ValueError("empty fitting/validation/calibration partition")
    for domain in domains:
        if {row["binary_label"] for row in rows if row["dataset"] == domain} != {"attack", "bona_fide"}:
            raise ValueError(f"both classes required in each source domain: {domain}")


def partitions(rows: list[dict], outer_target: str, seed: int) -> list[dict]:
    candidates = [row for row in rows if row["role"] != "g_domain"]
    matched = group_assignments(candidates, seed, 3)
    specifications: list[tuple[str, list[dict], list[dict]]] = [
        ("final", candidates, []),
    ]
    for domain in sorted({row["dataset"] for row in candidates}):
        specifications.append((f"domain_oof:{domain}",
                               [row for row in candidates if row["dataset"] != domain],
                               [row for row in candidates if row["dataset"] == domain]))
    for fold in range(3):
        specifications.append((f"matched_sample_oof:{fold}",
                               [row for row in candidates if matched[identity(row)] != fold],
                               [row for row in candidates if matched[identity(row)] == fold]))
    result = []
    for name, allowed, evaluation in specifications:
        train = [row for row in allowed if row["role"] == "train"]
        assignments = group_assignments(train, seed, 5)
        fitting = [row for row in train if assignments[identity(row)] != 0]
        validation = [row for row in train if assignments[identity(row)] == 0]
        calibration = [row for row in allowed if row["role"] == "branch_calibration"]
        for partition, purpose in ((fitting, "fitting"), (validation, "fitting"), (calibration, "calibration")):
            check_classes(partition)
            for row in partition:
                require_source_input(row, outer_target=outer_target, purpose=purpose, model_input=True)
        if evaluation:
            check_classes(evaluation)
        pools = (fitting, validation, calibration, evaluation)
        for index, pool in enumerate(pools):
            group = {(row["dataset"], row["group_id"]) for row in pool}
            content = {(row["dataset"], row["selected_frame"]["rgb_sha256"]) for row in pool}
            for other in pools[index + 1:]:
                if (group & {(row["dataset"], row["group_id"]) for row in other}
                        or content & {(row["dataset"], row["selected_frame"]["rgb_sha256"]) for row in other}):
                    raise ValueError("group or exact selected-frame content crosses a fit/evaluation boundary")
        if name.startswith("domain_oof:") and any(
            row["dataset"] == name.split(":", 1)[1] for row in fitting + validation + calibration
        ):
            raise ValueError("complete pseudo-target must be excluded from all fitting and selection")
        result.append({"name": name, "fitting": [identity(row) for row in fitting],
                       "validation": [identity(row) for row in validation],
                       "calibration": [identity(row) for row in calibration],
                       "evaluation": [identity(row) for row in evaluation]})
    return result


def objective_weights(labels: np.ndarray, domains: list[str], *, balanced: bool) -> np.ndarray:
    if labels.ndim != 1 or len(labels) != len(domains) or not len(labels) or not np.isin(labels, (0, 1)).all():
        raise ValueError("nonempty binary labels and exact domain joins required")
    result = np.zeros(len(labels), dtype=np.float64)
    unique = sorted(set(domains))
    for domain in unique:
        mask = np.asarray([value == domain for value in domains])
        if balanced:
            for label in (0, 1):
                selected = mask & (labels == label)
                if not selected.any():
                    raise ValueError("both classes required for domain/class-balanced BCE")
                result[selected] = 1 / (len(unique) * 2 * selected.sum())
        else:
            result[mask] = 1 / (len(unique) * mask.sum())
    return result


def sigmoid(values: np.ndarray) -> np.ndarray:
    from scipy.special import expit
    return expit(values)


def fit_head(
    x: np.ndarray, y: np.ndarray, domains: list[str], validation_x: np.ndarray,
    validation_y: np.ndarray, validation_domains: list[str], *, seed: int, settings: dict,
    guard,
) -> dict[str, Any]:
    if x.ndim != 2 or validation_x.shape[1:] != x.shape[1:] or not np.isfinite(x).all() or not np.isfinite(validation_x).all():
        raise ValueError("finite matching head features required")
    x, validation_x = x.astype(np.float64), validation_x.astype(np.float64)
    weights = objective_weights(y, domains, balanced=True)
    validation_weights = objective_weights(validation_y, validation_domains, balanced=True)
    rng = np.random.default_rng(seed)
    coefficients = np.r_[rng.normal(0, 0.001, x.shape[1]), 0.0]
    first, second = np.zeros_like(coefficients), np.zeros_like(coefficients)
    best_loss, best_epoch, best = float("inf"), 0, None
    history = []
    for epoch in range(1, settings["epochs"] + 1):
        guard()
        logits = x @ coefficients[:-1] + coefficients[-1]
        residual = weights * (sigmoid(logits) - y)
        gradient = np.r_[x.T @ residual, residual.sum()]
        first = 0.9 * first + 0.1 * gradient
        second = 0.999 * second + 0.001 * gradient * gradient
        update = (first / (1 - 0.9 ** epoch)) / (np.sqrt(second / (1 - 0.999 ** epoch)) + 1e-8)
        coefficients[:-1] *= 1 - settings["learning_rate"] * settings["weight_decay"]
        coefficients -= settings["learning_rate"] * update
        validation_logits = validation_x @ coefficients[:-1] + coefficients[-1]
        loss = float(validation_weights @ (np.logaddexp(0, validation_logits) - validation_y * validation_logits))
        if not np.isfinite(coefficients).all() or not np.isfinite(loss):
            raise ValueError("nonfinite head optimization")
        history.append(loss)
        if loss < best_loss:
            best_loss, best_epoch, best = loss, epoch, coefficients.copy()
    if best is None:
        raise ValueError("no fitted head checkpoint")
    return {"coefficients": best.tolist(), "selected_epoch": best_epoch,
            "validation_bce": best_loss, "validation_history": history,
            "optimizer": "full_batch_adamw_float64_bias_not_decayed", "seed": seed}


def head_logits(model: dict, features: np.ndarray) -> np.ndarray:
    coefficients = np.asarray(model["coefficients"])
    values = features @ coefficients[:-1] + coefficients[-1]
    if not np.isfinite(values).all():
        raise ValueError("nonfinite fitted head prediction")
    return values


def fit_calibrator(logits: np.ndarray, labels: np.ndarray, domains: list[str], guard) -> dict:
    from scipy.optimize import minimize
    weights = objective_weights(labels, domains, balanced=True)

    def loss(parameters):
        guard()
        theta, intercept = parameters
        slope = np.logaddexp(0, theta) + 1e-6
        values = slope * logits + intercept
        residual = weights * (sigmoid(values) - labels)
        objective = weights @ (np.logaddexp(0, values) - labels * values)
        return float(objective), np.array([residual @ logits * sigmoid(np.asarray(theta)), residual.sum()])

    fit = minimize(loss, np.array([np.log(np.expm1(1 - 1e-6)), 0.0]), jac=True, method="L-BFGS-B",
                   options={"maxiter": 1000, "ftol": 1e-12, "gtol": 1e-7})
    if not fit.success or not np.isfinite(fit.x).all() or not np.isfinite(fit.fun):
        raise RuntimeError(f"monotone calibration failed: {fit.message}")
    return {"theta": float(fit.x[0]), "intercept": float(fit.x[1]),
            "slope": float(np.logaddexp(0, fit.x[0]) + 1e-6), "bce": float(fit.fun),
            "iterations": int(fit.nit), "optimizer_success": True}


def calibrate(model: dict, logits: np.ndarray) -> np.ndarray:
    result = sigmoid(model["slope"] * logits + model["intercept"])
    if model["slope"] <= 0 or not np.isfinite(result).all():
        raise ValueError("finite strictly monotone calibration required")
    return result


def operating_threshold(scores: np.ndarray, rows: list[dict], *, alpha: float = 0.05) -> dict:
    if (len(scores) != len(rows) or not len(rows) or not np.isfinite(scores).all()
            or np.any((scores < 0) | (scores > 1)) or not 0 <= alpha < 1):
        raise ValueError("finite joined PAD probabilities and APCER constraint required")
    attacks = {
        domain: np.asarray([score for score, row in zip(scores, rows, strict=True)
                            if row["dataset"] == domain and row["binary_label"] == "attack"])
        for domain in sorted({row["dataset"] for row in rows})}
    if any(not len(values) for values in attacks.values()):
        raise ValueError("attack support required in each threshold-selection domain")
    candidates = np.unique(np.r_[0.0, scores, np.nextafter(1.0, 2.0)])
    threshold = max(float(value) for value in candidates
                    if all(np.mean(values < value) <= alpha for values in attacks.values()))
    return {"threshold": threshold, "alpha": alpha, "score_polarity": "attack_high_tie_is_attack",
            "selection": "largest_threshold_satisfying_each_source_domain_empirical_APCER",
            "failure_denominator_scope": "successful_calibration_images_only_conservative",
            "source_apcer": {domain: float(np.mean(values < threshold)) for domain, values in attacks.items()}}


def quality_vector(rgb: np.ndarray, transaction: dict) -> np.ndarray:
    import cv2
    if rgb.dtype != np.uint8 or rgb.shape != (224, 224, 3):
        raise ValueError("native224 RGB required for fixed quality features")
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float64) / 255
    box, frame = transaction["face_box_xyxy"], transaction["selected_frame"]
    area = (box[2] - box[0]) * (box[3] - box[1]) / (frame["width"] * frame["height"])
    result = np.asarray([cv2.Laplacian(gray, cv2.CV_64F, ksize=1).var(), gray.mean(), gray.std(),
                         area, transaction["detector_confidence"]], dtype=np.float64)
    if not np.isfinite(result).all() or area <= 0 or not 0 <= result[-1] <= 1:
        raise ValueError("finite saved geometry/confidence and quality features required")
    return result


def risk_features(probabilities: np.ndarray, quality: np.ndarray, threshold: float, variant: str) -> np.ndarray:
    if probabilities.ndim != 2 or probabilities.shape[1] != 2 or quality.shape != (len(probabilities), 5):
        raise ValueError("exact two branch probabilities and five quality features required")
    dino, other = probabilities[:, :1], probabilities[:, 1:]
    variants = {"R_q": [], "R_D": [dino], "R_V": [other], "R_DV": [dino, other],
                "R_DVd": [dino, other, abs(dino - other)],
                "R_DVdm": [dino, other, abs(dino - other), probabilities.mean(axis=1, keepdims=True) - threshold]}
    if variant not in variants:
        raise ValueError("registered risk feature variant required")
    result = np.concatenate(variants[variant] + [quality], axis=1)
    if not np.isfinite(result).all():
        raise ValueError("finite risk features required")
    return result


def fit_risk(features: np.ndarray, errors: np.ndarray, domains: list[str], guard) -> dict:
    from scipy.optimize import minimize
    if not np.isfinite(features).all() or features.ndim != 2 or set(errors.tolist()) != {0, 1}:
        raise ValueError("finite risk features and both error/correct classes required")
    weights = objective_weights(errors, domains, balanced=False) * len(errors)

    def loss(parameters):
        guard()
        values = features @ parameters[:-1] + parameters[-1]
        residual = weights * (sigmoid(values) - errors)
        objective = weights @ (np.logaddexp(0, values) - errors * values) + 0.5 * (parameters[:-1] @ parameters[:-1])
        gradient = np.r_[features.T @ residual + parameters[:-1], residual.sum()]
        return float(objective), gradient

    fit = minimize(loss, np.zeros(features.shape[1] + 1), jac=True, method="L-BFGS-B",
                   options={"maxiter": 1000, "ftol": 1e-12, "gtol": 1e-7})
    if not fit.success or not np.isfinite(fit.x).all() or not np.isfinite(fit.fun):
        raise RuntimeError(f"equal-domain C=1 logistic risk fit failed: {fit.message}")
    return {"coefficients": fit.x.tolist(), "C": 1.0, "intercept_penalized": False,
            "objective": "sum_natural_prevalence_domain_balanced_BCE_plus_half_L2",
            "iterations": int(fit.nit), "optimizer_success": True,
            "error_count": int(errors.sum()), "correct_count": int(len(errors) - errors.sum())}
