"""Fixed target estimands and source-only K=1 selection; no model fitting."""

from __future__ import annotations

import numpy as np

from .contracts import CORE_DOMAINS, PRIMARY_SEEDS, evaluate_rq1_applicability, validate_transaction_ledger
from .source_diagnostics import weighted_ranking
from .source_fitting import identity

SYSTEMS = ("heterogeneous", "same_family")
STRATEGIES = ("domain_oof", "matched_sample_oof")


def raw_aurc(errors: np.ndarray, risk: np.ndarray, weights: np.ndarray) -> float | None:
    """Discrete raw AURC, with expected random order inside exact-risk ties."""
    if not (errors.shape == risk.shape == weights.shape) or not np.isfinite(risk).all():
        raise ValueError("finite aligned AURC arrays required")
    if not np.isin(errors, [0, 1]).all() or not np.isfinite(weights).all() or (weights < 0).any():
        raise ValueError("binary errors and nonnegative finite multiplicities required")
    if not np.equal(weights, np.floor(weights)).all():
        raise ValueError("cluster bootstrap AURC requires integer multiplicities")
    selected = weights > 0
    if not selected.any():
        return None
    order = np.argsort(risk[selected], kind="stable")
    scores, e, w = risk[selected][order], errors[selected][order], weights[selected][order]
    starts = np.r_[0, np.flatnonzero(scores[1:] != scores[:-1]) + 1]
    mass = np.add.reduceat(w, starts)
    average = np.add.reduceat(w * e, starts) / mass
    expected_errors = np.repeat(average, mass.astype(np.int64))
    return float(np.mean(np.cumsum(expected_errors) / np.arange(1, len(expected_errors) + 1)))


def operating_summary(originals: list[dict], predictions: list[dict], risk: np.ndarray,
                      system: str, threshold: float, weights: dict[str, int] | None = None) -> dict:
    if system not in SYSTEMS or len(risk) != len(predictions) or not np.isfinite(risk).all():
        raise ValueError("aligned finite system risk required")
    by_id = {row["id"]: (row, float(value)) for row, value in zip(predictions, risk, strict=True)}
    if len(by_id) != len(predictions) or set(by_id) != {
        identity(row) for row in originals if row["detector_status"] == "success"
    }:
        raise ValueError("exact common detector-success mask required; no missing/duplicate scores")
    counts = {label: {"original": 0, "detected": 0, "covered": 0, "accepted": 0, "ungated": 0}
              for label in (0, 1)}
    domains = {}
    for original in originals:
        if original["binary_label"] not in {"attack", "bona_fide"}:
            raise ValueError("original binary label required")
        label = int(original["binary_label"] == "attack")
        weight = 1 if weights is None else weights[original["group_id"]]
        if type(weight) is not int or weight < 0:
            raise ValueError("integer original-cluster multiplicity required")
        cell = counts[label]
        cell["original"] += weight
        domain = domains.setdefault(original["dataset"], {0: [0, 0, 0], 1: [0, 0, 0]})
        domain[label][0] += weight
        if original["detector_status"] == "success":
            row, value = by_id[identity(original)]
            if row["label"] != label or row["group_id"] != original["group_id"]:
                raise ValueError("prediction label/cluster join drift")
            live = row["scores"][system] < row["thresholds"][system]
            accept = live and value <= threshold
            covered = not live or accept
            cell["detected"] += weight
            cell["covered"] += weight * covered
            cell["ungated"] += weight * live
            cell["accepted"] += weight * accept
            domain[label][1] += weight * accept
            domain[label][2] += weight * covered
        elif original["detector_status"] not in {"failed", "not_run"}:
            raise ValueError("unknown terminal detector disposition")
    if not all(counts[label]["original"] for label in counts):
        return {"estimable": False, "reason": "missing_original_class"}
    a, b = counts[1], counts[0]
    return {
        "estimable": True, "attack_originals": a["original"], "bona_fide_originals": b["original"],
        "fa_end2end": a["accepted"] / a["original"], "bfnr_end2end": 1 - b["accepted"] / b["original"],
        "attack_detector_coverage": a["detected"] / a["original"],
        "bona_fide_detector_coverage": b["detected"] / b["original"],
        "attack_coverage": a["covered"] / a["original"], "bona_fide_coverage": b["covered"] / b["original"],
        "coverage": (a["covered"] + b["covered"]) / (a["original"] + b["original"]),
        "attacks_newly_blocked": a["ungated"] - a["accepted"], "attacks_newly_admitted": 0,
        "bona_fide_newly_rejected": b["ungated"] - b["accepted"],
        "attack_failures": a["original"] - a["detected"], "bona_fide_failures": b["original"] - b["detected"],
        "covered_apcer": a["accepted"] / a["covered"] if a["covered"] else None,
        "covered_bpcer": 1 - b["accepted"] / b["covered"] if b["covered"] else None,
        "source_class_counts": domains,
    }


def select_k1(originals: list[dict], predictions: list[dict], risks: np.ndarray,
              system: str, outer_target: str, alpha: float = 0.01) -> dict:
    if not np.isfinite(alpha) or not 0 <= alpha <= 1:
        raise ValueError("finite source security rate in [0,1] required")
    if (not originals or any(row["dataset"] == outer_target or row["role"] != "g_domain"
                             or not row["source_use_eligible"] for row in originals)
            or set(row["dataset"] for row in originals) != CORE_DOMAINS - {outer_target}):
        raise ValueError("only permanent eligible non-target G_domain may select gates")
    candidates = sorted(set([-1.0, 1.0, *map(float, risks)]))
    feasible = []
    for threshold in candidates:
        summary = operating_summary(originals, predictions, risks, system, threshold)
        domains = summary["source_class_counts"]
        if any(not domains[d][label][0] for d in domains for label in (0, 1)):
            raise ValueError("source policy requires both original classes in every domain")
        fa = [values[1][1] / values[1][0] for values in domains.values()]
        bfnr = [1 - values[0][1] / values[0][0] for values in domains.values()]
        coverage = [(values[0][2] + values[1][2]) / (values[0][0] + values[1][0]) for values in domains.values()]
        if max(fa) <= alpha:
            feasible.append(((-float(np.mean(coverage)), float(np.mean(bfnr)), float(np.mean(fa)), threshold),
                             summary))
    if not feasible:
        raise ValueError("terminal non-accept policy must be feasible; source accounting is invalid")
    key, summary = min(feasible, key=lambda item: item[0])
    return {"threshold": key[3], "alpha": alpha, "selection": "equal_domain_max_coverage_then_macro_BFNR_FA_threshold",
            "population": "eligible_source_G_domain_all_originals", "source_summary": summary,
            "source_macro_coverage": -key[0], "source_macro_bfnr": key[1], "source_macro_fa": key[2],
            "certified_security_claim": False, "target_selection_input": False}


def arrays(originals: list[dict], predictions: list[dict], risks: dict[str, np.ndarray],
           policies: dict[str, dict]) -> dict:
    if len({identity(row) for row in originals}) != len(originals):
        raise ValueError("unique original transactions required")
    # This check also validates failure handling and the exact successful-image join.
    operating_summary(originals, predictions, np.zeros(len(predictions)), "heterogeneous", 1.0)
    ids = [row["id"] for row in predictions]
    if not predictions or any(row["dataset"] != originals[0]["dataset"] for row in predictions):
        raise ValueError("one complete held-out target per evaluation cell required")
    for row in predictions:
        for system in ("dino_reg", "openclip", *SYSTEMS):
            score, threshold = row["scores"][system], row["thresholds"][system]
            if not np.isfinite([score, threshold]).all() or not 0 <= score <= 1:
                raise ValueError("finite calibrated scores/source thresholds required")
            if row["errors"][system] != int((score >= threshold) != bool(row["label"])):
                raise ValueError("classifier error must be derived from its fixed source threshold")
    if any(len(value) != len(ids) or not np.isfinite(value).all() for value in risks.values()):
        raise ValueError("all risk variants require exact finite target coverage")
    required = {f"{strategy}/{system}/R_DVd" for strategy in STRATEGIES for system in SYSTEMS}
    if not required.issubset(risks) or set(policies) != required:
        raise ValueError("all fixed primary risks and source-selected gates required")
    index = {row["id"]: i for i, row in enumerate(predictions)}
    original_labels = np.asarray([row["binary_label"] == "attack" for row in originals])
    accepted = {}
    for system in SYSTEMS:
        name = f"domain_oof/{system}/R_DVd"
        accepted[system] = np.asarray([
            row["detector_status"] == "success"
            and predictions[index[identity(row)]]["scores"][system] < predictions[index[identity(row)]]["thresholds"][system]
            and risks[name][index[identity(row)]] <= policies[name]["threshold"] for row in originals])
    return {"originals": originals, "predictions": predictions, "risks": risks, "policies": policies,
            "labels": np.asarray([row["label"] for row in predictions]),
            "clusters": [row["group_id"] for row in predictions],
            "original_labels": original_labels, "accepted": accepted,
            "errors": {name: np.asarray([row["errors"][name] for row in predictions]) for name in SYSTEMS}}


def transaction_ledger(originals: list[dict], predictions: list[dict], risks: dict[str, np.ndarray],
                       policies: dict[str, dict], model_sha: str, risk_shas: dict[str, str], policy_sha: str) -> dict:
    positions = {row["id"]: i for i, row in enumerate(predictions)}
    ledgers = {}
    for strategy in STRATEGIES:
        records = []
        for system in SYSTEMS:
            name = f"{strategy}/{system}/R_DVd"
            for original in originals:
                key = identity(original)
                success = original["detector_status"] == "success"
                prediction = predictions[positions[key]] if success else None
                score = prediction["scores"][system] if success else None
                threshold = prediction["thresholds"][system] if success else None
                live = success and score < threshold
                risk = float(risks[name][positions[key]]) if success else None
                accept = live and risk <= policies[name]["threshold"]
                records.append({
                    "transaction_id": key, "sample_id": key, "dataset": original["dataset"],
                    "subject_id": original["subject_id"], "video_id": original["video_id"],
                    "outer_target": original["dataset"], "system": system, "ground_truth": original["binary_label"],
                    "detector_status": "failure" if original["detector_status"] == "failed" else original["detector_status"],
                    "technical_status": "terminal_failure" if original["detector_status"] == "not_run" else "completed",
                    "pad_score": score, "pad_threshold": threshold,
                    "pad_decision": ("bona_fide" if live else "attack") if success else None,
                    "classifier_error": prediction["errors"][system] if success else None,
                    "risk_score": risk, "gate_threshold": policies[name]["threshold"] if live else None,
                    "gate_action": ("accept" if accept else "non_accept") if live else None,
                    "final_k1_action": "accept" if accept else "non_accept",
                    "operationally_covered": bool(success and (not live or accept)),
                    "classifier_artifact_hash": model_sha, "risk_artifact_hash": risk_shas[name],
                    "policy_artifact_hash": policy_sha,
                })
        errors = validate_transaction_ledger(records)
        if errors:
            raise ValueError(f"fixed K1 transaction ledger violates its registered contract: {errors[:5]}")
        ledgers[strategy] = records
    return ledgers


def cell_metrics(cell: dict, cluster_weights: dict[str, int] | None = None, *, explanatory: bool = False) -> dict:
    predictions, risks = cell["predictions"], cell["risks"]
    weights = np.ones(len(predictions), dtype=np.int64) if cluster_weights is None else np.asarray(
        [cluster_weights[group] for group in cell["clusters"]], dtype=np.int64)
    e, y = cell["errors"], cell["labels"]
    ap = [weighted_ranking(e["heterogeneous"], risks[f"{strategy}/heterogeneous/R_DVd"], weights, "ap")
          for strategy in STRATEGIES]
    u = {}
    for system in SYSTEMS:
        risk = risks[f"domain_oof/{system}/R_DVd"]
        by_class = [raw_aurc(e[system][y == label], risk[y == label], weights[y == label]) for label in (0, 1)]
        u[system] = None if any(value is None for value in by_class) else float(np.mean(by_class))
    operational = {}
    for system in SYSTEMS:
        name = f"domain_oof/{system}/R_DVd"
        if cluster_weights is None:
            operational[system] = operating_summary(cell["originals"], predictions, risks[name], system,
                                                  cell["policies"][name]["threshold"])
        else:
            original_weights = np.asarray([cluster_weights[row["group_id"]] for row in cell["originals"]])
            labels = cell["original_labels"]
            denominator = [original_weights[labels == label].sum() for label in (0, 1)]
            accepted = [np.sum(original_weights[labels == label] * cell["accepted"][system][labels == label])
                        for label in (0, 1)]
            operational[system] = ({"estimable": False} if min(denominator) == 0 else
                                   {"estimable": True, "fa_end2end": float(accepted[1] / denominator[1]),
                                    "bfnr_end2end": float(1 - accepted[0] / denominator[0])})
    result = {"rq1_delta": None if any(value is None for value in ap) else ap[0] - ap[1],
              "rq1_domain_ap": ap[0], "rq1_sample_ap": ap[1],
              "error_count": int(np.sum(weights * e["heterogeneous"])),
              "rq2_delta": None if any(value is None for value in u.values()) else u["same_family"] - u["heterogeneous"],
              "U": u, "operational": operational}
    for metric in ("fa_end2end", "bfnr_end2end"):
        result[metric + "_harm"] = (
            operational["heterogeneous"][metric] - operational["same_family"][metric]
            if all(value["estimable"] for value in operational.values()) else None)
    if explanatory:
        result["risk_diagnostics"] = {}
        for name, risk in risks.items():
            system = name.split("/")[1]
            aucs = [raw_aurc(e[system][y == label], risk[y == label], weights[y == label]) for label in (0, 1)]
            oracle = [raw_aurc(e[system][y == label], e[system][y == label], weights[y == label]) for label in (0, 1)]
            result["risk_diagnostics"][name] = {
                "AP_error": weighted_ranking(e[system], risk, weights, "ap"),
                "AUROC_error": weighted_ranking(e[system], risk, weights, "auroc"),
                "error_prevalence": float(e[system].mean()),
                "class_raw_aurc": aucs,
                "class_excess_aurc": [None if a is None or b is None else a - b for a, b in zip(aucs, oracle, strict=True)],
            }
        result["secondary_operational"] = {
            name: operating_summary(cell["originals"], predictions, risks[name], name.split("/")[1],
                                    policy["threshold"]) for name, policy in cell["policies"].items()}
        classifier = {}
        for name in ("dino_reg", "openclip", *SYSTEMS):
            scores = np.asarray([row["scores"][name] for row in predictions])
            errors = np.asarray([row["errors"][name] for row in predictions])
            apcer = float(errors[y == 1].mean()) if (y == 1).any() else None
            bpcer = float(errors[y == 0].mean()) if (y == 0).any() else None
            classifier[name] = {"APCER": apcer, "BPCER": bpcer,
                                "ACER": (apcer + bpcer) / 2 if apcer is not None and bpcer is not None else None,
                                "AUROC": weighted_ranking(y, scores, weights, "auroc"),
                                "error_count": int(errors.sum()), "success_count": len(errors)}
        result["classifier"] = classifier
        d = np.asarray([row["errors"]["dino_reg"] for row in predictions])
        v = np.asarray([row["errors"]["openclip"] for row in predictions])
        f = e["heterogeneous"]
        result["complementarity"] = {
            "joint_counts_D_V": {f"{a}{b}": int(np.sum((d == a) & (v == b))) for a in (0, 1) for b in (0, 1)},
            "dino_errors": int(d.sum()), "vlm_rescues": int(np.sum((d == 1) & (v == 0))),
            "fusion_rescues": int(np.sum((d == 1) & (f == 0))),
            "attack_false_accepts_blocked": int(np.sum((y == 1) & (d == 1) & (f == 0))),
            "attack_false_accepts_newly_admitted": int(np.sum((y == 1) & (d == 0) & (f == 1))),
        }
    return result


def aggregate(points: dict[str, dict[int, dict]], field: str) -> dict:
    targets = {}
    for target, seeds in points.items():
        values = [seeds[seed][field] for seed in PRIMARY_SEEDS]
        targets[target] = None if any(value is None for value in values) else float(np.mean(values))
    macro = None if any(value is None for value in targets.values()) else float(np.mean(list(targets.values())))
    seed_macros = {str(seed): (None if any(points[t][seed][field] is None for t in points)
                              else float(np.mean([points[t][seed][field] for t in points]))) for seed in PRIMARY_SEEDS}
    return {"targets": targets, "macro": macro, "seed_macros": seed_macros}


def decide(rq1: dict, rq2: dict, intervals: dict, support: dict, dependencies: dict) -> dict:
    outcomes = {}
    for name, values in (("rq1", rq1), ("rq2", rq2)):
        ci = intervals[name]["macro"]
        if not dependencies[name]:
            outcomes[name] = {"status": "not_applicable", "reason": "source_claim_dependencies_fail"}
            continue
        if values["macro"] is None or ci is None or (name == "rq1" and sum(support.values()) < 3):
            outcomes[name] = {"status": "inconclusive", "reason": "insufficient_estimability_or_event_support"}
            continue
        if name == "rq1":
            predicates = {"positive_macro": values["macro"] > 0, "positive_lcb": ci[0] > 0,
                          "three_supported_positive_targets": sum(
                              support[t] and v is not None and v > 0 for t, v in values["targets"].items()) >= 3}
            against = ci[1] <= 0
        else:
            harms = values["operational_harms"]
            predicates = {
                "minimum_effect": values["macro"] >= 0.01, "positive_lcb": ci[0] > 0,
                "three_positive_targets": sum(v is not None and v > 0 for v in values["targets"].values()) >= 3,
                "two_positive_seed_macros": sum(v is not None and v > 0 for v in values["seed_macros"].values()) >= 2,
                "target_selective_harm": all(v is not None and v >= -0.02 for v in values["targets"].values()),
            }
            for metric, harm in harms.items():
                predicates[metric + "_macro"] = harm["macro"] is not None and harm["macro"] <= 0.01
                predicates[metric + "_targets"] = all(v is not None and v <= 0.02 for v in harm["targets"].values())
            against = ci[1] < 0.01 or not predicates["target_selective_harm"] or any(
                not value for key, value in predicates.items() if key.endswith(("_macro", "_targets")))
        outcomes[name] = {"status": "pass" if all(predicates.values()) else "evidence_against" if against else "inconclusive",
                          "predicates": predicates}
    return outcomes


def evaluate(cells: dict[str, dict[int, dict]], dependencies: dict, repetitions: int, seed: int, guard) -> dict:
    if set(cells) != CORE_DOMAINS or any(set(seeds) != set(PRIMARY_SEEDS) for seeds in cells.values()):
        raise ValueError("exact four-target three-seed grid required; no seed deletion or pooling")
    points = {target: {s: cell_metrics(cell, explanatory=True) for s, cell in seeds.items()}
              for target, seeds in cells.items()}
    clusters = {}
    for target, seeds in cells.items():
        first = seeds[PRIMARY_SEEDS[0]]
        population = [(identity(row), row["group_id"], row["binary_label"], row["detector_status"])
                      for row in first["originals"]]
        success_ids = [row["id"] for row in first["predictions"]]
        for cell in seeds.values():
            if ([(identity(row), row["group_id"], row["binary_label"], row["detector_status"])
                 for row in cell["originals"]] != population
                    or [row["id"] for row in cell["predictions"]] != success_ids
                    or cell["clusters"] != first["clusters"]):
                raise ValueError("identical target/cluster population required across all seeds")
        clusters[target] = sorted({row["group_id"] for row in first["originals"]})
    support = {target: evaluate_rq1_applicability(
        [points[target][s]["error_count"] for s in PRIMARY_SEEDS],
        [points[target][s]["rq1_delta"] is not None for s in PRIMARY_SEEDS]).target_eligible for target in points}
    rng = np.random.default_rng(seed)
    fields = {"rq1": "rq1_delta", "rq2": "rq2_delta",
              "fa_end2end_harm": "fa_end2end_harm", "bfnr_end2end_harm": "bfnr_end2end_harm"}
    samples = {name: {"macro": [], **{target: [] for target in cells},
                      **{f"{target}:{seed}": [] for target in cells for seed in PRIMARY_SEEDS}} for name in fields}
    for _ in range(repetitions):
        guard()
        replicated = {}
        for target, seeds in cells.items():
            groups = clusters[target]
            counts = rng.multinomial(len(groups), np.full(len(groups), 1 / len(groups)))
            weights = {group: int(count) for group, count in zip(groups, counts, strict=True)}
            replicated[target] = {s: cell_metrics(cell, weights) for s, cell in seeds.items()}
        for name in samples:
            value = aggregate(replicated, fields[name])
            for target, delta in value["targets"].items():
                if delta is not None:
                    samples[name][target].append(delta)
            if value["macro"] is not None:
                samples[name]["macro"].append(value["macro"])
            for target, seeds in replicated.items():
                for optimization_seed, cell in seeds.items():
                    if cell[fields[name]] is not None:
                        samples[name][f"{target}:{optimization_seed}"].append(cell[fields[name]])
    intervals = {name: {key: np.quantile(value, [0.025, 0.975]).tolist()
                        if len(value) >= repetitions * 0.95 else None for key, value in values.items()}
                 for name, values in samples.items()}
    rq1, rq2 = aggregate(points, "rq1_delta"), aggregate(points, "rq2_delta")
    rq2["operational_harms"] = {metric: aggregate(points, metric + "_harm")
                               for metric in ("fa_end2end", "bfnr_end2end")}
    return {"points": points, "rq1": rq1, "rq2": rq2, "event_eligible_targets": support, "ci95": intervals,
            "bootstrap_valid": {name: {key: len(value) for key, value in values.items()} for name, values in samples.items()},
            "bootstrap_requested": repetitions, "claims": decide(rq1, rq2, intervals, support, dependencies),
            "uncertainty_scope": "paired_subject_or_video_within_target_shared_across_all_seeds_conditional_saved_models",
            "seed_prediction_pooling": False, "target_tuning": False}
