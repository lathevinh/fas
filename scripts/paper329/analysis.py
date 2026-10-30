"""Paired operating analysis using the established319/324 metric helpers."""

from __future__ import annotations

import numpy as np

from fas.fusion_study import components
from fas.source_fitting import identity
import study
import oracle316

ARMS = ("reference", "reference_plus_tail")


def summarize(prediction: dict, originals: list[dict], policies: dict, guard,
              repetitions: int = 2000) -> dict:
    if set(prediction) != set(ARMS) or set(policies) != set(ARMS) or repetitions < 1:
        raise ValueError("two complete paired systems and positive bootstrap repetitions required")
    cases, curves = [], {}
    positions, labels = study.score_inputs(np.asarray(prediction[ARMS[0]]), originals)
    for arm in ARMS:
        scores = np.asarray(prediction[arm], dtype=np.float64)
        study.score_inputs(scores, originals)
        curves[arm] = study.curve(scores, originals)
        for alpha in study.ALPHAS:
            policy = policies[arm][str(alpha)]
            point = study.metrics(scores, originals, policy["threshold"])
            point["FA_within_constraint"] = point["accepted_attack"] <= (
                int(point["original_attack"])*alpha.numerator//alpha.denominator)
            point["utility_feasible"] = point["FA_within_constraint"] and point["BFA"] >= .5
            hindsight = oracle316.oracle(scores, labels[positions], int(labels.sum()),
                                        int((1-labels).sum()), alpha=alpha)
            hindsight = {key: value for key, value in hindsight.items()
                         if key not in {"threshold_interval", "oracle_threshold_not_deployable"}}
            cases.append({"system": arm, "alpha": str(alpha), "policy": point,
                          "oracle": hindsight, "source_policy": policy})
    mapping = components([{**row, "group_id": row["subject_id"] or row["group_id"]} for row in originals])
    groups = sorted(set(mapping.values()))
    indexes = np.asarray([groups.index(mapping[identity(row)]) for row in originals])
    rng = np.random.default_rng(20261028)
    records = {(arm, str(alpha), metric): [] for arm in ARMS for alpha in study.ALPHAS
               for metric in ("FA", "BFA", "AUROC_usable")}
    paired = {(str(alpha), metric): [] for alpha in study.ALPHAS
              for metric in ("FA", "BFA", "AUROC_usable")}
    for _ in range(repetitions):
        guard()
        weights = rng.multinomial(len(groups), np.full(len(groups), 1/len(groups)))[indexes]
        current = {}
        for arm in ARMS:
            for alpha in study.ALPHAS:
                point = study.metrics(np.asarray(prediction[arm]), originals,
                                      policies[arm][str(alpha)]["threshold"], weights)
                for metric in ("FA", "BFA", "AUROC_usable"):
                    key = arm, str(alpha), metric
                    current[key] = point[metric]
                    if point[metric] is not None:
                        records[key].append(point[metric])
        for key in paired:
            first, second = current[(ARMS[0], *key)], current[(ARMS[1], *key)]
            if first is not None and second is not None:
                paired[key].append(second-first)

    def interval(values):
        return {"valid_repetitions": len(values), "total_repetitions": repetitions,
                "percentile95": np.quantile(values, [.025, .975]).tolist()
                if values and len(values) >= repetitions*.95 else None}
    return {"cases": cases, "curves": curves,
            "conditional_intervals": [{"system": arm, "alpha": alpha, "metric": metric, **interval(values)}
                                      for (arm, alpha, metric), values in records.items()],
            "paired_minus_reference": [{"alpha": alpha, "metric": metric, **interval(values)}
                                       for (alpha, metric), values in paired.items()],
            "oracle_intervals": None, "original_failures_nonaccept": True}
