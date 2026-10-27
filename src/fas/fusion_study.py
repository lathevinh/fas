"""Nested fixed-recipe PAD mixtures and feasibility-first conditional comparisons."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

import numpy as np

from .feature_cache import payload_digest
from .source_diagnostics import weighted_ranking
from .source_fitting import group_assignments, identity

BRANCHES = ("dino_reg", "dino_plain", "openclip")
FAMILIES = {"dino_clip": "openclip", "two_dino": "dino_plain"}
SYSTEMS = ("dino_only", "plain_only", "clip_only", "fixed_two_dino",
           "selected_two_dino", "fixed_dino_clip", "dino_clip", "two_dino")
COMPARATORS = ("dino_only", "two_dino")


def components(rows: list[dict]) -> dict[str, str]:
    if len({identity(row) for row in rows}) != len(rows):
        raise ValueError("unique originals required for connected components")
    parents = {identity(row): identity(row) for row in rows}

    def root(key: str) -> str:
        while parents[key] != key:
            parents[key] = parents[parents[key]]
            key = parents[key]
        return key

    seen = {}
    for row in rows:
        keys = [("group", row["dataset"], row["group_id"])]
        frame = row.get("selected_frame")
        if frame is not None and frame.get("rgb_sha256"):
            keys.append(("frame", frame["rgb_sha256"]))
        for key in keys:
            current = identity(row)
            if key in seen:
                first, second = sorted((root(current), root(seen[key])))
                parents[second] = first
            seen[key] = current
    return {key: root(key) for key in parents}


def check_isolation(pools: list[list[dict]]) -> None:
    rows = [row for pool in pools for row in pool]
    mapping = components(rows)
    sets = [{mapping[identity(row)] for row in pool} for pool in pools]
    if any(first & second for index, first in enumerate(sets) for second in sets[index + 1:]):
        raise ValueError("source group or exact-frame connected component crosses a boundary")


def make_split(rows: list[dict], allowed: list[str], seed: int) -> dict:
    if not allowed or len(set(allowed)) != len(allowed):
        raise ValueError("nonempty unique permitted source domains required")
    selected = [row for row in rows if row["dataset"] in allowed]
    if {row["dataset"] for row in selected} != set(allowed):
        raise ValueError("every permitted source must have usable rows")
    train = [row for row in selected if row["role"] == "train"]
    assignments = group_assignments(train, seed, 5)
    split = {
        "fitting": [identity(row) for row in train if assignments[identity(row)] != 0],
        "validation": [identity(row) for row in train if assignments[identity(row)] == 0],
        "calibration": [identity(row) for row in selected if row["role"] == "branch_calibration"],
    }
    indexed = {identity(row): row for row in rows}
    pools = [[indexed[key] for key in split[name]] for name in split]
    pools.append([row for row in selected if row["role"] == "g_domain"])
    check_isolation(pools)
    return split


def job_key(allowed: list[str], seed: int, split: dict) -> str:
    return payload_digest({"allowed": sorted(allowed), "seed": seed, "split": split})


def support(rows: list[dict]) -> dict:
    mapping = components(rows)
    result = {}
    for domain in sorted({row["dataset"] for row in rows}):
        result[domain] = {}
        for label in ("bona_fide", "attack"):
            subset = [row for row in rows if row["dataset"] == domain and row["binary_label"] == label]
            usable = [row for row in subset if row["model_input_eligible"]]
            result[domain][label] = {
                "originals": len(subset), "usable": len(usable),
                "technical_failures": len(subset) - len(usable),
                "registered_groups": len({row["group_id"] for row in subset}),
                "components": len({mapping[identity(row)] for row in subset}),
                "usable_components": len({mapping[identity(row)] for row in usable}),
                "original_rate_step": 1 / len(subset) if subset else None,
                "successful_rate_step": 1 / len(usable) if usable else None,
            }
    return result


def require_support(inventory: dict, rule: dict, location: str) -> None:
    if not inventory:
        raise ValueError(f"empty support at {location}; no fallback")
    for domain, classes in inventory.items():
        for label, item in classes.items():
            if (item["usable"] < rule["usable_per_class"]
                    or item["usable_components"] < rule["components_per_class"]):
                raise ValueError(f"insufficient declared support: {location}/{domain}/{label}")


def operating_metrics(scores: np.ndarray, threshold: float, rows: list[dict],
                      originals: list[dict], config: dict, *, ranking: bool = False) -> dict:
    expected = [row for row in originals if row["model_input_eligible"]]
    if ([identity(row) for row in expected] != [identity(row) for row in rows]
            or scores.shape != (len(rows),) or not np.isfinite(scores).all()
            or np.any((scores < 0) | (scores > 1))
            or not np.isfinite(threshold) or not 0 <= threshold <= np.nextafter(1.0, 2.0)):
        raise ValueError("exact original/successful joins and finite PAD scores/threshold required")
    result = {}
    for domain in sorted({row["dataset"] for row in originals}):
        mask = np.asarray([row["dataset"] == domain for row in rows])
        labels = np.asarray([row["binary_label"] == "attack" for row in rows])[mask]
        p = scores[mask]
        accepted = p < threshold
        original_counts = {label: sum(row["dataset"] == domain and row["binary_label"] == label
                                      for row in originals) for label in ("attack", "bona_fide")}
        if not all(original_counts.values()) or set(labels.tolist()) != {False, True}:
            raise ValueError("both original and successful classes required")
        fa = float(accepted[labels].sum() / original_counts["attack"])
        bona_fide = float(accepted[~labels].sum() / original_counts["bona_fide"])
        item = {
            "original_attack_FA": fa, "original_bona_fide_acceptance": bona_fide,
            "original_bona_fide_non_acceptance": 1 - bona_fide,
            "original_acceptance_fraction": float(accepted.sum() / sum(original_counts.values())),
            "original_counts": original_counts, "successful": int(mask.sum()),
            "technical_failures": sum(original_counts.values()) - int(mask.sum()),
            "empirical_utility_feasible": bool(fa <= config["alpha"]
                                             and bona_fide >= config["minimum_bona_fide_acceptance"]),
        }
        if ranking:
            item.update({
                "successful_AUROC": weighted_ranking(labels.astype(int), p, np.ones(len(p)), "auroc"),
                "successful_ACER": float((accepted[labels].mean() + (~accepted[~labels]).mean()) / 2),
                "successful_Brier": float(np.mean((p - labels) ** 2)),
            })
        result[domain] = item
    return result


def select_weight(candidates: list[dict], config: dict) -> dict:
    if [item["weight"] for item in candidates] != config["weights"]:
        raise ValueError("complete ordered equal-opportunity weight grid required")
    if not candidates or not candidates[0]["per_domain"]:
        raise ValueError("nonempty inner held-out source results required")
    domains = set(candidates[0]["per_domain"])
    for candidate in candidates:
        if set(candidate["per_domain"]) != domains:
            raise ValueError("identical inner source coverage required for every weight")
        for item in candidate["per_domain"].values():
            if any(not np.isfinite(item[name]) or not 0 <= item[name] <= 1
                   for name in ("original_attack_FA", "original_bona_fide_acceptance")):
                raise ValueError("finite inner original-denominator rates required")
    feasible = [item for item in candidates if all(
        value["original_attack_FA"] <= config["alpha"]
        and value["original_bona_fide_acceptance"] >= config["minimum_bona_fide_acceptance"]
        for value in item["per_domain"].values())]
    if not feasible:
        return {"status": "no_candidate_meets_declared_utility", "weight": None}
    chosen = min(feasible, key=lambda item: (
        -min(value["original_bona_fide_acceptance"] for value in item["per_domain"].values()),
        max(value["original_attack_FA"] for value in item["per_domain"].values()), item["weight"]))
    return {"status": "selected", "weight": chosen["weight"]}


def summarize(folds: list[dict], config: dict) -> dict:
    if not folds or len({fold["id"] for fold in folds}) != len(folds):
        raise ValueError("nonempty unique full evaluation fold denominator required")
    systems = {}
    for name in SYSTEMS:
        per_domain = defaultdict(list)
        states = {key: 0 for key in ("transfer_feasible", "transfer_failure", "no_candidate_meets_declared_utility")}
        for fold in folds:
            if set(fold["systems"]) != set(SYSTEMS):
                raise ValueError("all fixed and selected systems required on every fold")
            item = fold["systems"][name]
            if item["status"] not in states:
                raise ValueError("unknown selected-policy evaluation status")
            states[item["status"]] += 1
            if item["status"] in {"transfer_feasible", "transfer_failure"}:
                rates = item["metrics"]
                if any(not np.isfinite(rates[key]) or not 0 <= rates[key] <= 1
                       for key in ("original_attack_FA", "original_bona_fide_acceptance")):
                    raise ValueError("finite full-fold rates required")
                feasible = (rates["original_attack_FA"] <= config["alpha"]
                            and rates["original_bona_fide_acceptance"] >= config["minimum_bona_fide_acceptance"])
                if feasible != (item["status"] == "transfer_feasible"):
                    raise ValueError("transfer status contradicts held-out utility")
                per_domain[fold["dataset"]].append(item["metrics"])
        complete = sum(states[key] for key in ("transfer_feasible", "transfer_failure")) == len(folds)
        means = {domain: {
            metric: float(np.mean([item[metric] for item in items]))
            for metric in ("original_attack_FA", "original_bona_fide_acceptance")
        } for domain, items in per_domain.items()} if complete else None
        systems[name] = {
            "fold_denominator": len(folds), "outcome_counts": dict(states),
            "selected_policy_fraction": sum(states[key] for key in ("transfer_feasible", "transfer_failure")) / len(folds),
            "transfer_feasible_fraction": states["transfer_feasible"] / len(folds),
            "full_endpoint_estimable": complete,
            "all_folds_empirically_feasible": states["transfer_feasible"] == len(folds),
            "per_source_equal_context_seed_means": means,
            "worst_source_mean_bona_fide_acceptance": (
                min(item["original_bona_fide_acceptance"] for item in means.values()) if means else None),
        }
    clip = systems["dino_clip"]
    comparisons = {}
    for name in COMPARATORS:
        other = systems[name]
        if not clip["all_folds_empirically_feasible"]:
            status, delta, no_worsening = "clip_not_feasible_on_all_declared_folds", None, None
        elif not other["all_folds_empirically_feasible"]:
            status, delta, no_worsening = "feasibility_advantage_only", None, None
        else:
            delta = clip["worst_source_mean_bona_fide_acceptance"] - other["worst_source_mean_bona_fide_acceptance"]
            no_worsening = all(
                item["original_bona_fide_acceptance"] + 1e-12
                >= other["per_source_equal_context_seed_means"][domain]["original_bona_fide_acceptance"]
                for domain, item in clip["per_source_equal_context_seed_means"].items())
            status = "practical_gain" if delta + 1e-12 >= config["practical_gain"] and no_worsening else "no_practical_gain"
        source_deltas = None
        if clip["full_endpoint_estimable"] and other["full_endpoint_estimable"]:
            source_deltas = {
                domain: {metric: value - other["per_source_equal_context_seed_means"][domain][metric]
                         for metric, value in rates.items()}
                for domain, rates in clip["per_source_equal_context_seed_means"].items()}
        comparisons[name] = {"status": status, "worst_source_gain": delta,
                             "no_source_mean_bona_fide_worsening": no_worsening,
                             "descriptive_source_mean_differences": source_deltas}
    retain = all(item["status"] in {"feasibility_advantage_only", "practical_gain"}
                 for item in comparisons.values())
    return {
        "systems": systems, "clip_comparisons": comparisons,
        "decision": "retain_for_independent_validation" if retain else "no_demonstrated_incremental_value",
        "decision_scope": "exploratory_point_screen_not_security_certification",
        "uncertainty_is_descriptive_not_an_additional_selection_gate": True,
    }


def paired_uncertainty(folds: list[dict], originals: list[dict], accepted: dict,
                       config: dict, guard: Callable[[], None]) -> dict:
    """Resample each source component once, sharing its draw across every seed/fold/system."""
    mapping = components(originals)
    indexed = {identity(row): row for row in originals}
    grouped = defaultdict(list)
    for row in originals:
        grouped[row["dataset"]].append(row)
    matrices = {}
    for domain, rows in sorted(grouped.items()):
        keys = sorted({mapping[identity(row)] for row in rows})
        if any(indexed[key]["dataset"] != domain for key in keys):
            raise ValueError("cross-source component cannot be dataset-stratified independently")
        key_index = {key: position for position, key in enumerate(keys)}
        counts = np.zeros((len(keys), 2))
        for row in rows:
            counts[key_index[mapping[identity(row)]], int(row["binary_label"] == "attack")] += 1
        matching = [fold for fold in folds if fold["dataset"] == domain]
        totals = np.zeros((len(keys), len(matching), len(SYSTEMS), 2))
        valid = np.ones(len(SYSTEMS), dtype=bool)
        for number, fold in enumerate(matching):
            for system_index, name in enumerate(SYSTEMS):
                if fold["systems"][name]["status"] == "no_candidate_meets_declared_utility":
                    valid[system_index] = False
                    continue
                ids = accepted[fold["id"]][name]
                if not set(ids) <= {identity(row) for row in rows if row["model_input_eligible"]}:
                    raise ValueError("only successful original identities can be accepted")
                for key in ids:
                    row = indexed[key]
                    totals[key_index[mapping[key]], number, system_index, int(row["binary_label"] == "attack")] += 1
        matrices[domain] = (counts, totals.mean(axis=1), valid)
    samples = {name: [] for name in SYSTEMS}
    differences = {name: [] for name in COMPARATORS}
    source_differences = {name: {domain: [] for domain in matrices} for name in COMPARATORS}
    source_fa_differences = {name: {domain: [] for domain in matrices} for name in COMPARATORS}
    rng = np.random.default_rng(config["bootstrap_seed"])
    valid_count = 0
    for _ in range(config["bootstrap_repetitions"]):
        guard()
        source_values = {}
        for domain, (counts, totals, valid) in matrices.items():
            weights = rng.multinomial(len(counts), np.full(len(counts), 1 / len(counts)))
            denominator = weights @ counts
            if not np.all(denominator > 0):
                break
            source_values[domain] = (
                weights @ totals[:, :, 0] / denominator[0],
                weights @ totals[:, :, 1] / denominator[1], valid)
        if len(source_values) != len(matrices):
            continue
        valid_count += 1
        values = {}
        for index, name in enumerate(SYSTEMS):
            if all(item[2][index] for item in source_values.values()):
                values[name] = min(float(item[0][index]) for item in source_values.values())
                samples[name].append(values[name])
        for name in COMPARATORS:
            if "dino_clip" in values and name in values:
                differences[name].append(values["dino_clip"] - values[name])
                for domain, (rates, fa, _) in source_values.items():
                    source_differences[name][domain].append(
                        float(rates[SYSTEMS.index("dino_clip")] - rates[SYSTEMS.index(name)]))
                    source_fa_differences[name][domain].append(
                        float(fa[SYSTEMS.index("dino_clip")] - fa[SYSTEMS.index(name)]))
    enough = valid_count >= config["bootstrap_repetitions"] * config["minimum_valid_bootstrap_fraction"]

    def interval(values: list[float]) -> dict:
        return {"status": "estimable" if enough and values else "unestimable",
                "ci95": np.quantile(values, [0.025, 0.975]).tolist() if enough and values else None}

    return {
        "scope": "conditional_saved_predictors_source_component_paired_not_retraining_or_unseen_domain",
        "requested": config["bootstrap_repetitions"], "valid": valid_count,
        "status": "estimable" if enough else "unestimable_insufficient_valid_replicates",
        "worst_source_mean_bona_fide_acceptance": {name: interval(values) for name, values in samples.items()},
        "clip_minus": {name: interval(values) for name, values in differences.items()},
        "per_source_bona_fide_clip_minus": {
            name: {domain: interval(values) for domain, values in domains.items()}
            for name, domains in source_differences.items()},
        "per_source_attack_FA_clip_minus": {
            name: {domain: interval(values) for domain, values in domains.items()}
            for name, domains in source_fa_differences.items()},
        "selection_and_feasibility_not_recomputed_in_bootstrap": True,
    }
