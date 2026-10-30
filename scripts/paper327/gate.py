"""Proposed first-stage operating-policy gate; never authorizes execution."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping

TARGETS = ("OULU-NPU", "CASIA-FASD", "MSU-MFSD", "SiW-Mv2")
ALPHA = Fraction(1, 20)
MINIMUM_BFA = Fraction(1, 2)
PRACTICAL_GAIN = Fraction(1, 20)
MAXIMUM_REGRESSION = Fraction(1, 20)


@dataclass(frozen=True)
class OperatingCounts:
    attacks: int
    bona_fide: int
    accepted_attacks: int
    accepted_bona_fide: int

    def __post_init__(self) -> None:
        counts = (self.attacks, self.bona_fide, self.accepted_attacks, self.accepted_bona_fide)
        if (any(type(value) is not int for value in counts)
                or self.attacks <= 0 or self.bona_fide <= 0
                or not 0 <= self.accepted_attacks <= self.attacks
                or not 0 <= self.accepted_bona_fide <= self.bona_fide):
            raise ValueError("positive original supports and bounded integer acceptance counts required")

    @property
    def safe(self) -> bool:
        return Fraction(self.accepted_attacks, self.attacks) <= ALPHA

    @property
    def bfa(self) -> Fraction:
        return Fraction(self.accepted_bona_fide, self.bona_fide)

    @property
    def joint(self) -> bool:
        return self.safe and self.bfa >= MINIMUM_BFA


def assess_expansion(
    results: Mapping[str, tuple[OperatingCounts | None, OperatingCounts | None]],
) -> dict[str, object]:
    """Compare (reference, reference+tail), using original-denominator counts."""
    if set(results) != set(TARGETS):
        raise ValueError("exactly the four declared targets required")
    missing = []
    for target in TARGETS:
        pair = results[target]
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise ValueError("each target requires a reference/candidate pair")
        for arm, counts in zip(("reference", "tail"), pair):
            if counts is None:
                missing.append(f"missing_primary_policy:{target}:{arm}")
            elif not isinstance(counts, OperatingCounts):
                raise ValueError("OperatingCounts or explicit missing policy required")
        reference, candidate = pair
        if (reference is not None and candidate is not None
                and (reference.attacks, reference.bona_fide)
                != (candidate.attacks, candidate.bona_fide)):
            raise ValueError("paired arms must have identical original supports")
    if missing:
        return {"decision": "stop", "reasons": missing,
                "scientific_execution_authorized": False}
    gains, new_unsafe, regressions = [], [], []
    reference_joint = candidate_joint = 0
    for target in TARGETS:
        reference, candidate = results[target]
        if reference is None or candidate is None:
            raise RuntimeError("validated complete policy inventory required")
        delta = candidate.bfa-reference.bfa
        if reference.safe and candidate.safe and delta >= PRACTICAL_GAIN:
            gains.append(target)
        if reference.safe and not candidate.safe:
            new_unsafe.append(target)
        if delta < -MAXIMUM_REGRESSION:
            regressions.append(target)
        reference_joint += int(reference.joint)
        candidate_joint += int(candidate.joint)
    reasons = []
    if len(gains) < 2:
        reasons.append("fewer_than_two_FA_safe_paired_BFA_gains_of_5pp")
    if candidate_joint-reference_joint < 1:
        reasons.append("joint_utility_target_count_gain_below_one")
    if new_unsafe:
        reasons.append("new_FA_unsafe_targets")
    if regressions:
        reasons.append("BFA_regression_exceeds_5pp")
    return {
        "decision": "stop" if reasons else "eligible_for_owner_review",
        "reasons": reasons, "safe_gain_targets": gains,
        "new_unsafe_targets": new_unsafe, "regression_targets": regressions,
        "reference_joint_targets": reference_joint,
        "candidate_joint_targets": candidate_joint,
        "scientific_execution_authorized": False,
    }
