"""Geometry-preserving square inputs for the exploratory 304 candidate."""

from __future__ import annotations

import cv2
import numpy as np


def pad_shared_crop(rgb: np.ndarray, resolution: int) -> tuple[np.ndarray, dict[str, object]]:
    if rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[2] != 3 or min(rgb.shape[:2]) < 1:
        raise ValueError("nonempty uint8 RGB shared crop required")
    if type(resolution) is not int or resolution < 1:
        raise ValueError("positive integer resolution required")

    height, width = rgb.shape[:2]
    side = max(height, width)
    vertical = side - height
    horizontal = side - width
    top, left = vertical // 2, horizontal // 2
    bottom, right = vertical - top, horizontal - left
    square = cv2.copyMakeBorder(
        rgb, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(0, 0, 0)
    )
    resized = cv2.resize(square, (resolution, resolution), interpolation=cv2.INTER_CUBIC)
    geometry: dict[str, object] = {
        "strategy": "centered_constant_zero_pad_shared_crop_then_isotropic_resize",
        "input_height_width": [height, width],
        "square_height_width": [side, side],
        "padding_top_bottom_left_right": [top, bottom, left, right],
        "padding_rgb": [0, 0, 0],
        "resolution": resolution,
        "interpolation": "bicubic",
    }
    return resized, geometry


def fit_source_risk_candidate(
    features: np.ndarray, errors: np.ndarray, domains: list[str], guard
) -> dict:
    if (features.ndim != 2 or errors.ndim != 1 or not np.isfinite(features).all()
            or len(errors) != len(features) or len(domains) != len(errors)
            or set(errors.tolist()) != {0, 1}):
        raise ValueError("finite risk features and both error/correct classes required")
    from scipy.optimize import minimize

    from .source_fitting import objective_weights, sigmoid

    weights = objective_weights(errors, domains, balanced=False) * len(errors)

    def loss(parameters: np.ndarray) -> tuple[float, np.ndarray]:
        guard()
        logits = features @ parameters[:-1] + parameters[-1]
        residual = weights * (sigmoid(logits) - errors)
        objective = weights @ (np.logaddexp(0, logits) - errors * logits)
        objective += 0.5 * (parameters[:-1] @ parameters[:-1])
        gradient = np.r_[features.T @ residual + parameters[:-1], residual.sum()]
        return float(objective), gradient

    options = {"maxiter": 1000, "ftol": 1e-12, "gtol": 1e-7, "maxls": 50}
    fit = minimize(loss, np.zeros(features.shape[1] + 1), jac=True, method="L-BFGS-B", options=options)
    if not fit.success or not np.isfinite(fit.x).all() or not np.isfinite(fit.fun):
        raise RuntimeError(f"source candidate C=1 logistic risk fit failed: {fit.message}")
    return {
        "coefficients": fit.x.tolist(),
        "C": 1.0,
        "intercept_penalized": False,
        "objective": "sum_natural_prevalence_domain_balanced_BCE_plus_half_L2",
        "iterations": int(fit.nit),
        "optimizer_success": True,
        "line_search_maximum": options["maxls"],
        "error_count": int(errors.sum()),
        "correct_count": int(len(errors) - errors.sum()),
    }
