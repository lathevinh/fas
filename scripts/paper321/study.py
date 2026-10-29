"""Source-policy, saved-score and paired conditional analysis for paper321."""

from __future__ import annotations

from fractions import Fraction
from html import escape
from itertools import combinations

import numpy as np

from fas.fusion_study import check_isolation, components
from fas.source_diagnostics import weighted_ranking
from fas.source_fitting import identity

SYSTEMS = ("dino_reg", "supervised_clip", "fixed_equal_two_dino", "matched_deeppixbis")
ALPHAS = (Fraction(1, 20), Fraction(1, 100), Fraction(1, 10))


def isolation(pools: list[list[dict]]) -> None:
    check_isolation(pools)
    subjects = [{(row["dataset"], row["subject_id"]) for row in pool if row["subject_id"]}
                for pool in pools]
    if any(left & right for left, right in combinations(subjects, 2)):
        raise ValueError("known subject crosses a fitting/validation/calibration/evaluation boundary")


def threshold(scores: np.ndarray, rows: list[dict], alpha: Fraction) -> dict:
    if (len(scores) != len(rows) or not len(rows) or not np.isfinite(scores).all()
            or np.any((scores < 0) | (scores > 1)) or not isinstance(alpha, Fraction) or not 0 <= alpha < 1):
        raise ValueError("finite joined calibration scores required")
    sources = {}
    for domain in sorted({row["dataset"] for row in rows}):
        attacks = np.asarray([score for score, row in zip(scores, rows, strict=True)
                              if row["dataset"] == domain and row["binary_label"] == "attack"])
        if not len(attacks):
            raise ValueError("successful calibration attacks required in each source")
        budget = len(attacks) * alpha.numerator // alpha.denominator
        upper = float(np.partition(attacks, budget)[budget])
        sources[domain] = {"successful_attacks": len(attacks), "error_budget": budget, "safe_upper": upper}
    value = min(item["safe_upper"] for item in sources.values())
    for domain, item in sources.items():
        item["accepted_attacks"] = sum(
            score < value for score, row in zip(scores.tolist(), rows, strict=True)
            if row["dataset"] == domain and row["binary_label"] == "attack")
    return {"threshold": value, "alpha": str(alpha), "sources": sources,
            "limiting_sources": [domain for domain, item in sources.items() if item["safe_upper"] == value]}


def score_inputs(scores: np.ndarray, originals: list[dict]) -> tuple[np.ndarray, np.ndarray]:
    positions = np.asarray([i for i, row in enumerate(originals) if row["detector_status"] == "success"])
    labels = np.asarray([row["binary_label"] == "attack" for row in originals], dtype=int)
    if (scores.shape != positions.shape or not len(positions) or not np.isfinite(scores).all()
            or np.any((scores < 0) | (scores > 1)) or set(labels.tolist()) != {0, 1}):
        raise ValueError("exact finite usable-score/original-denominator join required")
    return positions, labels


def metrics(scores: np.ndarray, originals: list[dict], value: float, weights=None) -> dict:
    positions, labels = score_inputs(scores, originals)
    weights = np.ones(len(originals)) if weights is None else weights
    if (weights.shape != labels.shape or not np.isfinite(weights).all() or np.any(weights < 0)):
        raise ValueError("finite nonnegative original weights required")
    attack, real = float(weights @ labels), float(weights @ (1 - labels))
    accepted = scores < value
    successful_y, successful_w = labels[positions], weights[positions]
    accepted_attack = float(successful_w @ (accepted & (successful_y == 1)))
    accepted_real = float(successful_w @ (accepted & (successful_y == 0)))
    usable_attack = float(successful_w @ successful_y)
    usable_real = float(successful_w @ (1 - successful_y))
    return {
        "original_attack": attack, "original_bona_fide": real,
        "accepted_attack": accepted_attack, "accepted_bona_fide": accepted_real,
        "FA": accepted_attack / attack if attack else None,
        "BFA": accepted_real / real if real else None,
        "AUROC_usable": weighted_ranking(successful_y, scores, successful_w, "auroc"),
        "usable_attack": usable_attack, "usable_bona_fide": usable_real,
        "FA_usable": accepted_attack / usable_attack if usable_attack else None,
        "BF_rejection_usable": 1 - accepted_real / usable_real if usable_real else None,
    }


def aggregate(contexts: list[dict]) -> list[dict]:
    records = []
    for seed in sorted({context["seed"] for context in contexts}):
        selected = [context for context in contexts if context["seed"] == seed]
        if len(selected) != 4 or len({context["target"] for context in selected}) != 4:
            raise ValueError("four distinct target domains required per seed")
        for system in SYSTEMS:
            for alpha in ALPHAS:
                cases = [(context["target"], case["policy"]) for context in selected
                         for case in context["analysis"]["cases"]
                         if case["system"] == system and case["alpha"] == str(alpha)]
                if len(cases) != 4:
                    raise ValueError("one operating case per system/alpha/target required")
                worst = min(point["BFA"] for _, point in cases)
                records.append({
                    "seed": seed, "system": system, "alpha": str(alpha),
                    "equal_target_macro": {
                        metric: float(np.mean([point[metric] for _, point in cases]))
                        for metric in ("FA", "BFA", "AUROC_usable")},
                    "worst_target_BFA": worst,
                    "worst_target_operating_points": [
                        {"target": target, "FA": point["FA"], "BFA": point["BFA"]}
                        for target, point in cases if point["BFA"] == worst],
                    "FA_safe_targets": sum(point["FA_within_constraint"] for _, point in cases),
                    "utility_feasible_targets": sum(point["utility_feasible"] for _, point in cases)})
    return records


def curve(scores: np.ndarray, originals: list[dict]) -> list[list[float]]:
    positions, labels = score_inputs(scores, originals)
    y = labels[positions]
    values, inverse = np.unique(scores, return_inverse=True)
    attacks = np.bincount(inverse, weights=y, minlength=len(values))
    real = np.bincount(inverse, weights=1-y, minlength=len(values))
    return np.column_stack((
        np.r_[0, np.cumsum(attacks)] / labels.sum(),
        np.r_[0, np.cumsum(real)] / (1-labels).sum())).tolist()


def summarize_context(prediction: dict, originals: list[dict], policies: dict, oracle, guard,
                      repetitions: int = 2000) -> dict:
    cases, curves = [], {}
    for system in SYSTEMS:
        scores = np.asarray(prediction[system], dtype=np.float64)
        positions, labels = score_inputs(scores, originals)
        curves[system] = curve(scores, originals)
        for alpha in ALPHAS:
            policy = policies[system][str(alpha)]
            point = metrics(scores, originals, policy["threshold"])
            hindsight = oracle(scores, labels[positions], int(labels.sum()), int((1-labels).sum()), alpha=alpha)
            hindsight = {key: value for key, value in hindsight.items() if key not in {
                "threshold_interval", "oracle_threshold_not_deployable"}}
            point["FA_within_constraint"] = point["accepted_attack"] <= (
                int(point["original_attack"]) * alpha.numerator // alpha.denominator)
            point["utility_feasible"] = point["FA_within_constraint"] and point["BFA"] >= .5
            cases.append({"system": system, "alpha": str(alpha), "policy": point, "oracle": hindsight,
                          "limiting_sources": policy["limiting_sources"],
                          "source_attack_budgets": {d: item["error_budget"] for d, item in policy["sources"].items()}})
    mapping = components([{**row, "group_id": row["subject_id"] or row["group_id"]} for row in originals])
    groups = sorted(set(mapping.values()))
    indexes = np.asarray([groups.index(mapping[identity(row)]) for row in originals])
    rng = np.random.default_rng(20261028)
    samples = {(system, str(alpha), metric): [] for system in SYSTEMS for alpha in ALPHAS
               for metric in ("FA", "BFA", "AUROC_usable")}
    paired = {(system, str(alpha), metric): [] for system in SYSTEMS[1:] for alpha in ALPHAS
              for metric in ("FA", "BFA", "AUROC_usable")}
    prepared = {}
    for system in SYSTEMS:
        scores = np.asarray(prediction[system], dtype=np.float64)
        order = np.argsort(-scores, kind="stable")
        ranked = scores[order]
        ends = np.r_[np.flatnonzero(ranked[1:] != ranked[:-1]), len(ranked) - 1]
        prepared[system] = (order, ends, {
            str(alpha): scores < policies[system][str(alpha)]["threshold"] for alpha in ALPHAS})
    successful_y = labels[positions]
    for _ in range(repetitions):
        guard()
        weights = rng.multinomial(len(groups), np.full(len(groups), 1 / len(groups)))[indexes]
        attack, real = float(weights @ labels), float(weights @ (1-labels))
        successful_w = weights[positions]
        positive = np.sum(successful_w * successful_y)
        negative = np.sum(successful_w * (1-successful_y))
        current = {}
        for system in SYSTEMS:
            order, ends, accepted = prepared[system]
            auc = None
            if positive > 0 and negative > 0:
                y, w = successful_y[order], successful_w[order]
                tp, fp = np.cumsum(w*y)[ends], np.cumsum(w*(1-y))[ends]
                auc = float(np.sum(np.diff(np.r_[0.0, fp]) / negative
                                   * (tp + np.r_[0.0, tp[:-1]]) / (2*positive)))
            for alpha in ALPHAS:
                mask = accepted[str(alpha)]
                point = {
                    "FA": float(successful_w @ (mask & (successful_y == 1))) / attack if attack else None,
                    "BFA": float(successful_w @ (mask & (successful_y == 0))) / real if real else None,
                    "AUROC_usable": auc,
                }
                for metric in ("FA", "BFA", "AUROC_usable"):
                    value = point[metric]
                    current[(system, str(alpha), metric)] = value
                    if value is not None:
                        samples[(system, str(alpha), metric)].append(value)
        for key in paired:
            anchor = ("dino_reg", key[1], key[2])
            if current[key] is not None and current[anchor] is not None:
                paired[key].append(current[key] - current[anchor])

    def intervals(records):
        return [{"system": key[0], "alpha": key[1], "metric": key[2],
                 "valid_repetitions": len(values), "total_repetitions": repetitions,
                 "percentile95": np.quantile(values, [.025, .975]).tolist()
                 if len(values) >= repetitions * .95 and values else None}
                for key, values in records.items()]
    return {"cases": cases, "curves": curves,
            "conditional_intervals": intervals(samples), "paired_minus_dino_reg": intervals(paired),
            "bootstrap_unit": "video_exact_frame_component" if originals[0]["dataset"] == "SiW-Mv2"
            else "subject_exact_frame_component",
            "oracle_intervals": None}


def plot(contexts: list[dict]) -> str:
    domains = ("OULU-NPU", "CASIA-FASD", "MSU-MFSD", "SiW-Mv2")
    colors = ("#1f77b4", "#d62728", "#2ca02c", "#9467bd")
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="760" viewBox="0 0 1040 760">',
             '<rect width="1040" height="760" fill="white"/>',
             '<text x="20" y="24">Original-denominator low-FA curves; each thin line is one training seed</text>']
    for i, domain in enumerate(domains):
        x, y = 55 + i % 2 * 510, 65 + i // 2 * 315
        parts += [f'<defs><clipPath id="p{i}"><rect x="{x}" y="{y}" width="420" height="240"/></clipPath></defs>',
                  f'<rect x="{x}" y="{y}" width="420" height="240" fill="none" stroke="black"/>',
                  f'<text x="{x}" y="{y-10}">{escape(domain)}</text>',
                  f'<text x="{x}" y="{y+260}">FA: 0 to 10%; BFA: 0 to 100%</text>']
        for context in contexts:
            if context["target"] != domain:
                continue
            for system, color in zip(SYSTEMS, colors, strict=True):
                points = " ".join(f"{x+fa*4200:.3f},{y+240-bfa*240:.3f}"
                                  for fa, bfa in context["analysis"]["curves"][system])
                parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" opacity=".5" clip-path="url(#p{i})"/>')
        outside = sum(case["policy"]["FA"] > .1 for context in contexts if context["target"] == domain
                      for case in context["analysis"]["cases"] if case["alpha"] == "1/20")
        for context in contexts:
            if context["target"] == domain:
                for case in context["analysis"]["cases"]:
                    if case["alpha"] == "1/20" and case["policy"]["FA"] <= .1:
                        color = colors[SYSTEMS.index(case["system"])]
                        px, py = x+case["policy"]["FA"]*4200, y+240-case["policy"]["BFA"]*240
                        parts.append(f'<circle cx="{px:.3f}" cy="{py:.3f}" r="3" fill="{color}"/>')
        parts.append(f'<text x="{x}" y="{y+278}">5% source-policy markers outside window: {outside}</text>')
    for index, (system, color) in enumerate(zip(SYSTEMS, colors, strict=True)):
        parts.append(f'<text x="20" y="{700+index*15}" fill="{color}">{escape(system)}</text>')
    parts.append('</svg>\n')
    return "\n".join(parts)
