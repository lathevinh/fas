"""Source-only clustered uncertainty and fixed diagnostic controls."""

from __future__ import annotations

from collections import defaultdict
import hashlib

import numpy as np

from .source_fitting import check_classes, identity, risk_features


def budget_split(split: dict, indexed: dict[str, dict], budget: int, seed: int) -> dict:
    rows = [indexed[key] for key in split["fitting"]]
    # Connected group/frame components must remain intact even in a budget control.
    components: dict[tuple, list[dict]] = defaultdict(list)
    group_links = {}
    for row in rows:
        group = (row["dataset"], row["group_id"])
        content = (row["dataset"], row["selected_frame"]["rgb_sha256"])
        group_links.setdefault(content, set()).add(group)
    parent = {(row["dataset"], row["group_id"]): (row["dataset"], row["group_id"]) for row in rows}

    def root(group):
        while parent[group] != group:
            parent[group] = parent[parent[group]]
            group = parent[group]
        return group

    for linked in group_links.values():
        linked = sorted(linked)
        for group in linked[1:]:
            parent[root(group)] = root(linked[0])
    for row in rows:
        components[root((row["dataset"], row["group_id"]))].append(row)
    strata: dict[tuple, list[list[dict]]] = defaultdict(list)
    for component in components.values():
        strata[(component[0]["dataset"], tuple(sorted({r["binary_label"] for r in component})))].append(component)
    for values in strata.values():
        values.sort(key=lambda group: hashlib.sha256(
            f"budget299:{seed}:{min(identity(row) for row in group)}".encode()).hexdigest())
    selected, remaining = [], budget
    while any(strata.values()):
        for key in sorted(strata):
            if strata[key]:
                component = strata[key].pop(0)
                if len(component) <= remaining:
                    selected.extend(identity(row) for row in component)
                    remaining -= len(component)
    check_classes([indexed[key] for key in selected])
    if not selected or len(selected) > budget:
        raise ValueError("whole-group budget-matched source fit is not feasible")
    selected_keys = set(selected)
    result = {**split, "fitting": [key for key in split["fitting"] if key in selected_keys]}
    return result


def design(records: list[dict], system: str, variant: str, mean: np.ndarray, scale: np.ndarray) -> np.ndarray:
    other = "openclip" if system == "heterogeneous" else "dino_plain"
    probabilities = np.asarray([[row["probabilities"]["dino_reg"], row["probabilities"][other]] for row in records])
    quality = (np.asarray([row["quality"] for row in records]) - mean) / scale
    base = variant.removesuffix("_noq")
    values = risk_features(probabilities, quality, 0.0, base)
    if base == "R_DVdm":
        values[:, 3] = probabilities.mean(axis=1) - np.asarray([row["thresholds"][system] for row in records])
    return values[:, :-5] if variant.endswith("_noq") else values


def cluster_weights(records: list[dict], rng: np.random.Generator) -> np.ndarray:
    domains = sorted({row["dataset"] for row in records})
    weights = np.zeros(len(records), dtype=np.float64)
    for domain in domains:
        positions = [index for index, row in enumerate(records) if row["dataset"] == domain]
        groups = sorted({records[index]["group_id"] for index in positions})
        counts = rng.multinomial(len(groups), np.full(len(groups), 1 / len(groups)))
        counts_by_group = dict(zip(groups, counts, strict=True))
        weights[positions] = [counts_by_group[records[index]["group_id"]] for index in positions]
    return weights


def weighted_ranking(labels: np.ndarray, scores: np.ndarray, weights: np.ndarray, metric: str) -> float | None:
    if (labels.shape != scores.shape or scores.shape != weights.shape or not np.isfinite(scores).all()
            or not np.isfinite(weights).all() or (weights < 0).any() or not np.isin(labels, (0, 1)).all()):
        raise ValueError("exact finite weighted binary ranking inputs required")
    positive, negative = np.sum(weights * labels), np.sum(weights * (1 - labels))
    if positive <= 0 or negative <= 0:
        return None
    order = np.argsort(-scores, kind="stable")
    ranked, y, w = scores[order], labels[order], weights[order]
    ends = np.r_[np.flatnonzero(ranked[1:] != ranked[:-1]), len(ranked) - 1]
    tp, fp = np.cumsum(w * y)[ends], np.cumsum(w * (1 - y))[ends]
    if metric == "ap":
        return float(np.sum(np.diff(np.r_[0.0, tp]) / positive * tp / np.maximum(tp + fp, 1e-300)))
    if metric == "auroc":
        return float(np.sum(np.diff(np.r_[0.0, fp]) / negative * (tp + np.r_[0.0, tp[:-1]]) / (2 * positive)))
    raise ValueError("registered AP or AUROC metric required")


def competence(records: list[dict], repetitions: int, seed: int, guard, *, finite_calibration: bool) -> dict:
    names = ("dino_reg", "openclip", "heterogeneous", "same_family")
    domains = sorted({row["dataset"] for row in records})
    y = np.asarray([row["label"] for row in records])
    masks = {domain: np.asarray([row["dataset"] == domain for row in records]) for domain in domains}
    scores = {name: np.asarray([row["scores"][name] for row in records]) for name in names}
    correct = {name: np.asarray([row["errors"][name] == 0 for row in records]) for name in names}
    bootstrap = {name: [] for name in names}
    rng = np.random.default_rng(seed)
    for _ in range(repetitions):
        guard()
        weight = cluster_weights(records, rng)
        for name in names:
            aucs = [weighted_ranking(y[mask], scores[name][mask], weight[mask], "auroc") for mask in masks.values()]
            if all(value is not None for value in aucs):
                bootstrap[name].append(float(np.mean(aucs)))
    result = {}
    for name in names:
        aucs = [weighted_ranking(y[mask], scores[name][mask], np.ones(mask.sum()), "auroc") for mask in masks.values()]
        if any(value is None for value in aucs) or len(bootstrap[name]) < repetitions * 0.95:
            raise ValueError("source competence bootstrap lacks both-class support in at least95% replicates")
        ba = [np.mean([correct[name][mask & (y == label)].mean() for label in (0, 1)]) for mask in masks.values()]
        metrics = {"macro_auroc": float(np.mean(aucs)), "macro_balanced_accuracy": float(np.mean(ba)),
                   "macro_auroc_lcb": float(np.quantile(bootstrap[name], 0.025)),
                   "score_range": float(np.ptp(scores[name])), "finite_scores": bool(np.isfinite(scores[name]).all()),
                   "both_classes": True, "finite_calibration": finite_calibration,
                   "bootstrap_valid_repetitions": len(bootstrap[name]), "bootstrap_requested": repetitions,
                   "uncertainty_scope": "conditional_saved_predictors_group_bootstrap_within_source_domain"}
        metrics["pass"] = bool(finite_calibration and metrics["macro_auroc"] >= 0.55 and metrics["macro_balanced_accuracy"] >= 0.55
                               and metrics["macro_auroc_lcb"] > 0.5 and metrics["score_range"] > 1e-6)
        result[name] = metrics
    return result


def paired_ap(records: list[dict], first: np.ndarray, second: np.ndarray, system: str,
              repetitions: int, seed: int, guard) -> dict:
    errors = np.asarray([row["errors"][system] for row in records])
    a = weighted_ranking(errors, first, np.ones(len(errors)), "ap")
    b = weighted_ranking(errors, second, np.ones(len(errors)), "ap")
    result = {"count": len(records), "errors": int(errors.sum()), "correct": int(len(errors) - errors.sum()),
              "first_ap": a, "second_ap": b, "estimable": a is not None and b is not None,
              "minimum20_error_support": bool(errors.sum() >= 20), "diagnostic_not_target_rq_verdict": True}
    if a is None or b is None:
        return {**result, "status": "not_applicable_one_class_errors", "delta": None, "ci95": None}
    rng, values = np.random.default_rng(seed), []
    for _ in range(repetitions):
        guard()
        weights = cluster_weights(records, rng)
        first_ap = weighted_ranking(errors, first, weights, "ap")
        second_ap = weighted_ranking(errors, second, weights, "ap")
        if first_ap is not None and second_ap is not None:
            values.append(first_ap - second_ap)
    interval = np.quantile(values, [0.025, 0.975]).tolist() if len(values) >= repetitions * 0.95 else None
    return {**result, "delta": a - b, "ci95": interval, "bootstrap_valid": len(values),
            "bootstrap_requested": repetitions,
            "status": "underpowered" if errors.sum() < 20 or interval is None else
                      "positive" if interval[0] > 0 else "negative" if interval[1] < 0 else "inconclusive"}


def drift(oof: np.ndarray, final: np.ndarray) -> list[dict]:
    from scipy.stats import ks_2samp
    if oof.shape != final.shape or not np.isfinite(oof).all() or not np.isfinite(final).all():
        raise ValueError("same-original finite OOF/final feature coverage required")
    return [{"feature_index": index, "oof_mean": float(oof[:, index].mean()),
             "final_mean": float(final[:, index].mean()), "mean_shift": float(final[:, index].mean() - oof[:, index].mean()),
             "oof_std": float(oof[:, index].std()), "final_std": float(final[:, index].std()),
             "ks_distance": float(ks_2samp(oof[:, index], final[:, index]).statistic)}
            for index in range(oof.shape[1])]
