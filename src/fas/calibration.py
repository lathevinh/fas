"""Dependency-free monotone affine calibration primitives."""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence


class MonotoneAffineCalibrator:
    """Map logits through sigmoid(a * logit + b) with a strictly positive."""

    def __init__(self, theta: float, intercept: float, epsilon: float = 1e-6) -> None:
        if not all(math.isfinite(value) for value in (theta, intercept, epsilon)):
            raise ValueError("calibration parameters must be finite")
        if epsilon <= 0:
            raise ValueError("epsilon must be positive")
        self.theta = theta
        self.intercept = intercept
        self.epsilon = epsilon

    @property
    def slope(self) -> float:
        return _softplus(self.theta) + self.epsilon

    def transform_one(self, logit: float) -> float:
        if not math.isfinite(logit):
            raise ValueError("logit must be finite")
        value = self.slope * logit + self.intercept
        if value >= 0:
            return 1.0 / (1.0 + math.exp(-value))
        exp_value = math.exp(value)
        return exp_value / (1.0 + exp_value)

    def transform(self, logits: Iterable[float]) -> list[float]:
        return [self.transform_one(logit) for logit in logits]


def equal_domain_log_loss(
    probabilities: Sequence[float],
    labels: Sequence[int],
    domains: Sequence[str],
) -> float:
    """Average natural-prevalence BCE within domains, then equally across domains."""
    _validate_probability_inputs(probabilities, labels, domains)
    losses: dict[str, list[float]] = {}
    for probability, label, domain in zip(probabilities, labels, domains, strict=True):
        clipped = min(max(probability, 1e-12), 1.0 - 1e-12)
        loss = -(label * math.log(clipped) + (1 - label) * math.log(1.0 - clipped))
        losses.setdefault(domain, []).append(loss)
    return sum(sum(values) / len(values) for values in losses.values()) / len(losses)


def class_balanced_equal_domain_log_loss(
    probabilities: Sequence[float],
    labels: Sequence[int],
    domains: Sequence[str],
) -> float:
    """Average class BCE within each domain, then equally across domains."""
    _validate_probability_inputs(probabilities, labels, domains)
    losses: dict[str, dict[int, list[float]]] = {}
    for probability, label, domain in zip(probabilities, labels, domains, strict=True):
        clipped = min(max(probability, 1e-12), 1.0 - 1e-12)
        loss = -(label * math.log(clipped) + (1 - label) * math.log(1.0 - clipped))
        losses.setdefault(domain, {0: [], 1: []})[label].append(loss)
    domain_losses = []
    for domain, class_losses in losses.items():
        if not class_losses[0] or not class_losses[1]:
            raise ValueError(f"domain {domain!r} must contain both classes")
        domain_losses.append(
            sum(sum(values) / len(values) for values in class_losses.values()) / 2
        )
    return sum(domain_losses) / len(domain_losses)


def _validate_probability_inputs(
    probabilities: Sequence[float],
    labels: Sequence[int],
    domains: Sequence[str],
) -> None:
    if not probabilities or not (len(probabilities) == len(labels) == len(domains)):
        raise ValueError("probabilities, labels, and domains must have equal nonzero length")
    for probability, label in zip(probabilities, labels, strict=True):
        if label not in (0, 1) or not math.isfinite(probability):
            raise ValueError("labels must be binary and probabilities finite")
        if not 0.0 <= probability <= 1.0:
            raise ValueError("probabilities must be in [0, 1]")


def _softplus(value: float) -> float:
    if value > 20:
        return value
    if value < -20:
        return math.exp(value)
    return math.log1p(math.exp(value))
