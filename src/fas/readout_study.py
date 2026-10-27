"""Cache-only readout selection, held-out scoring and original-denominator metrics."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from .source_diagnostics import cluster_weights, weighted_ranking
from .source_fitting import (
    calibrate, fit_calibrator, fit_head, head_logits, identity, objective_weights,
    operating_threshold, partitions, check_classes,
)
from .source_stage import require_source_input

BRANCHES = ("dino_reg", "dino_plain", "openclip")
SYSTEMS = ("old_dino_reg", "old_two_dino", "zero_shot_clip",
           "selected_dino_reg", "selected_two_dino", "supervised_clip")
CONTRASTS = ("zero_shot_clip", "selected_dino_reg", "selected_two_dino")


def transform(features: np.ndarray, name: str) -> np.ndarray:
    if features.ndim != 2 or not features.size or not np.isfinite(features).all():
        raise ValueError("finite nonempty feature matrix required")
    values = features.astype(np.float64)
    if name == "raw":
        return values
    if name != "unit_l2":
        raise ValueError("registered raw or unit_l2 transform required")
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    if (norms == 0).any():
        raise ValueError("zero vector cannot be L2 normalized")
    return values / norms


def check_head(model: dict, features: np.ndarray, labels: np.ndarray, domains: list[str], epochs: int) -> None:
    history = np.asarray(model["validation_history"])
    if (history.shape != (epochs,) or not np.isfinite(history).all()
            or model["selected_epoch"] != int(np.argmin(history)) + 1):
        raise ValueError("finite complete history and earliest minimum epoch required")
    logits = head_logits(model, features)
    loss = float(objective_weights(labels, domains, balanced=True) @
                 (np.logaddexp(0, logits) - labels * logits))
    if (not np.isclose(loss, model["validation_bce"], rtol=1e-10, atol=1e-10)
            or not np.isclose(loss, history[model["selected_epoch"] - 1], rtol=1e-10, atol=1e-10)):
        raise ValueError("saved selected-head validation BCE does not reconstruct")


def selected_index(candidates: list[dict]) -> int:
    if not candidates or any(not np.isfinite(item["model"]["validation_bce"]) for item in candidates):
        raise ValueError("finite candidate validation objectives required")
    return min(range(len(candidates)), key=lambda index: (candidates[index]["model"]["validation_bce"], index))


def validate_context(rows: list[dict], split: dict, outer_target: str, seed: int) -> None:
    expected = partitions(rows, outer_target, seed)
    if (split["name"] != "final" and not split["name"].startswith("domain_oof:")) or split not in expected:
        raise ValueError("exact inherited final/domain-OOF source partition required")
    for row in rows:
        purpose = {"train": "fitting", "branch_calibration": "calibration", "g_domain": "domain_use"}[row["role"]]
        require_source_input(row, outer_target=outer_target, purpose=purpose, model_input=True)
    if split["name"] == "final":
        evaluation = [row for row in rows if row["role"] == "g_domain"]
        check_classes(evaluation)
        used = [row for row in rows if row["role"] != "g_domain"]
        groups = {(row["dataset"], row["group_id"]) for row in used}
        frames = {(row["dataset"], row["selected_frame"]["rgb_sha256"]) for row in used}
        if (groups & {(row["dataset"], row["group_id"]) for row in evaluation}
                or frames & {(row["dataset"], row["selected_frame"]["rgb_sha256"]) for row in evaluation}):
            raise ValueError("g_domain group/content must stay outside all readout selection and calibration")


def evaluation_ids(rows: list[dict], split: dict) -> list[str]:
    return ([identity(row) for row in rows if row["role"] == "g_domain"]
            if split["name"] == "final" else split["evaluation"])


def fit_readouts(rows: list[dict], features: dict[str, np.ndarray], baseline: dict,
                 split: dict, config: dict, seed: int, guard, counters: dict[str, int],
                 checkpoint: Callable[[str, dict], None] | None = None) -> dict:
    if baseline["split"] != split or set(features) != set(BRANCHES):
        raise ValueError("exact baseline split and three cached branches required")
    index = {identity(row): position for position, row in enumerate(rows)}
    if len(index) != len(rows) or any(len(value) != len(rows) for value in features.values()):
        raise ValueError("one-to-one ordered feature/row join required")
    positions = {key: np.asarray([index[value] for value in split[key]], dtype=np.int64)
                 for key in ("fitting", "validation", "calibration")}
    labels = np.asarray([row["binary_label"] == "attack" for row in rows], dtype=np.float64)
    domains = lambda selected: [rows[position]["dataset"] for position in selected]
    fit, validation, calibration = (positions[key] for key in ("fitting", "validation", "calibration"))
    candidates, selected, calibrators, calibration_p = {}, {}, {}, {}
    for branch in BRANCHES:
        candidates[branch] = []
        for number, candidate in enumerate(config["candidates"]):
            guard()
            values = transform(features[branch], candidate["transform"])
            settings = {**config["head"], **candidate["settings"]}
            reused = number == 0 and branch in baseline["heads"]
            if not reused:
                counters["new_head_fits"] += 1
                if counters["new_head_fits"] > config["limits"]["new_head_fits"]:
                    raise RuntimeError("registered head-fit budget exhausted; no retry")
            if checkpoint is not None:
                checkpoint(f"head-{branch}-{number}-started", {"reused": reused, "fit_counts": dict(counters)})
            model = baseline["heads"][branch] if reused else fit_head(
                values[fit], labels[fit], domains(fit), values[validation], labels[validation],
                domains(validation), seed=seed, settings=settings, guard=guard)
            check_head(model, values[validation], labels[validation], domains(validation), settings["epochs"])
            candidates[branch].append({"candidate": candidate["name"], "model": model,
                                       "origin": "baseline299_anchor" if reused else "new_readout"})
            if checkpoint is not None:
                checkpoint(f"head-{branch}-{number}-complete", candidates[branch][-1])
        selected[branch] = selected_index(candidates[branch])
        candidate = config["candidates"][selected[branch]]
        values = transform(features[branch][calibration], candidate["transform"])
        logits = head_logits(candidates[branch][selected[branch]]["model"], values)
        counters["new_calibrator_fits"] += 1
        if counters["new_calibrator_fits"] > config["limits"]["new_calibrator_fits"]:
            raise RuntimeError("registered calibrator-fit budget exhausted; no retry")
        if checkpoint is not None:
            checkpoint(f"calibrator-{branch}-started", {"selected": selected[branch], "fit_counts": dict(counters)})
        calibrators[branch] = fit_calibrator(logits, labels[calibration], domains(calibration), guard)
        if checkpoint is not None:
            checkpoint(f"calibrator-{branch}-complete", calibrators[branch])
        calibration_p[branch] = calibrate(calibrators[branch], logits)
    scores = {
        "selected_dino_reg": calibration_p["dino_reg"],
        "selected_two_dino": (calibration_p["dino_reg"] + calibration_p["dino_plain"]) / 2,
        "supervised_clip": calibration_p["openclip"],
    }
    policies = {name: operating_threshold(values, [rows[position] for position in calibration],
                                          alpha=config["reference_alpha"])
                for name, values in scores.items()}
    return {"split": split, "candidates": candidates, "selected": selected,
            "calibrators": calibrators, "policies": policies}


def score_readouts(rows: list[dict], features: dict[str, np.ndarray], clip_logits: np.ndarray,
                   baseline: dict, fitted: dict, config: dict) -> tuple[list[dict], dict]:
    index = {identity(row): position for position, row in enumerate(rows)}
    evaluation = np.asarray([index[key] for key in evaluation_ids(rows, fitted["split"])], dtype=np.int64)
    logits = {branch: head_logits(baseline["heads"][branch], features[branch][evaluation])
              for branch in ("dino_reg", "dino_plain")}
    logits["openclip"] = clip_logits[evaluation]
    old_p = {branch: calibrate(baseline["calibrators"][branch], values) for branch, values in logits.items()}
    new_p, candidate_scores = {}, {}
    labels = np.asarray([rows[position]["binary_label"] == "attack" for position in evaluation])
    masks = {domain: np.asarray([rows[position]["dataset"] == domain for position in evaluation])
             for domain in sorted({rows[position]["dataset"] for position in evaluation})}
    for branch in BRANCHES:
        candidate_scores[branch] = []
        for number, candidate in enumerate(config["candidates"]):
            values = transform(features[branch][evaluation], candidate["transform"])
            raw = head_logits(fitted["candidates"][branch][number]["model"], values)
            auc = {domain: weighted_ranking(labels[mask], raw[mask], np.ones(mask.sum()), "auroc")
                   for domain, mask in masks.items()}
            if any(value is None for value in auc.values()):
                raise ValueError("both held-out classes required for candidate ranking")
            candidate_scores[branch].append({"candidate": candidate["name"], "held_out_auroc": auc,
                                              "not_used_for_selection": True})
            if number == fitted["selected"][branch]:
                new_p[branch] = calibrate(fitted["calibrators"][branch], raw)
    scores = {
        "old_dino_reg": old_p["dino_reg"],
        "old_two_dino": (old_p["dino_reg"] + old_p["dino_plain"]) / 2,
        "zero_shot_clip": old_p["openclip"],
        "selected_dino_reg": new_p["dino_reg"],
        "selected_two_dino": (new_p["dino_reg"] + new_p["dino_plain"]) / 2,
        "supervised_clip": new_p["openclip"],
    }
    thresholds = {name: baseline["policies"][original]["threshold"] for name, original in (
        ("old_dino_reg", "dino_reg"), ("old_two_dino", "same_family"), ("zero_shot_clip", "openclip"))}
    thresholds.update({name: policy["threshold"] for name, policy in fitted["policies"].items()})
    predictions = []
    for local, position in enumerate(evaluation):
        row = rows[position]
        predictions.append({
            "id": identity(row), "dataset": row["dataset"], "group_id": row["group_id"],
            "role": row["role"], "label": int(labels[local]), "fold": fitted["split"]["name"],
            "scores": {name: float(values[local]) for name, values in scores.items()},
            "thresholds": thresholds,
        })
    return predictions, candidate_scores


def check_predictions(records: list[dict], originals: list[dict]) -> None:
    successful = {identity(row): row for row in originals if row["model_input_eligible"]}
    if len(successful) != len(records) or {row["id"] for row in records} != set(successful):
        raise ValueError("exact one-to-one successful evaluation coverage required")
    if len({identity(row) for row in originals}) != len(originals):
        raise ValueError("unique original-denominator identities required")
    for record in records:
        row = successful[record["id"]]
        if (record["dataset"] != row["dataset"] or record["group_id"] != row["group_id"]
                or record["role"] != row["role"] or record["label"] != int(row["binary_label"] == "attack")):
            raise ValueError("evaluation label/group/role identity drift")
        if set(record["scores"]) != set(SYSTEMS) or set(record["thresholds"]) != set(SYSTEMS):
            raise ValueError("all six systems required on the same successful population")
        if any(not np.isfinite(score) or not 0 <= score <= 1 for score in record["scores"].values()):
            raise ValueError("finite calibrated probabilities required")
        if any(not np.isfinite(threshold) or not 0 <= threshold <= np.nextafter(1.0, 2.0)
               for threshold in record["thresholds"].values()):
            raise ValueError("finite attack-high operating thresholds required")
    if any(not row["source_use_eligible"] or row["binary_label"] not in {"attack", "bona_fide"}
           for row in originals):
        raise ValueError("eligible labelled original evaluation population required")


def metrics(records: list[dict], originals: list[dict]) -> dict:
    check_predictions(records, originals)
    result = {}
    for domain in sorted({row["dataset"] for row in originals}):
        subset = [row for row in records if row["dataset"] == domain]
        all_rows = [row for row in originals if row["dataset"] == domain]
        y = np.asarray([row["label"] for row in subset])
        original_counts = [sum(row["binary_label"] == label for row in all_rows)
                           for label in ("bona_fide", "attack")]
        if any(not count for count in original_counts) or any(not (y == label).any() for label in (0, 1)):
            raise ValueError("both original and successful classes required in each source domain")
        systems = {}
        for name in SYSTEMS:
            p = np.asarray([row["scores"][name] for row in subset])
            accepted = p < np.asarray([row["thresholds"][name] for row in subset])
            fa = float(accepted[y == 1].mean())
            bfnr = float((~accepted[y == 0]).mean())
            clipped = np.clip(p, 1e-12, 1 - 1e-12)
            systems[name] = {
                "auroc": weighted_ranking(y, p, np.ones(len(y)), "auroc"),
                "successful_balanced_accuracy": 1 - (fa + bfnr) / 2,
                "successful_ACER": (fa + bfnr) / 2,
                "successful_APCER": fa, "successful_BPCER": bfnr,
                "successful_brier": float(np.mean((p - y) ** 2)),
                "successful_nll_epsilon_1e_minus12": float(np.mean(-y * np.log(clipped) - (1 - y) * np.log1p(-clipped))),
                "original_attack_FA": float(accepted[y == 1].sum() / original_counts[1]),
                "original_bona_fide_non_acceptance": float(1 - accepted[y == 0].sum() / original_counts[0]),
                "original_operational_acceptance_coverage": float(accepted.sum() / len(all_rows)),
                "successful_score_range": [float(p.min()), float(p.max())],
            }
        result[domain] = {
            "original_count": len(all_rows), "successful_count": len(subset),
            "technical_failures": len(all_rows) - len(subset),
            "original_class_counts": dict(zip(("bona_fide", "attack"), original_counts, strict=True)),
            "technical_failure_class_counts": {
                label: original_counts[number] - int((y == number).sum())
                for number, label in enumerate(("bona_fide", "attack"))},
            "ranking_coverage": len(subset) / len(all_rows), "systems": systems,
        }
    macro = {name: {metric: float(np.mean([item["systems"][name][metric] for item in result.values()]))
                    for metric in ("auroc", "successful_balanced_accuracy", "successful_ACER", "successful_brier",
                                   "successful_nll_epsilon_1e_minus12", "original_attack_FA",
                                   "original_bona_fide_non_acceptance", "original_operational_acceptance_coverage")}
             for name in SYSTEMS}
    return {"per_domain": result, "equal_source_macro": macro}


def paired_uncertainty(records: list[dict], repetitions: int, seed: int, guard) -> dict:
    if not isinstance(repetitions, int) or repetitions < 1:
        raise ValueError("positive registered bootstrap repetition count required")
    y = np.asarray([row["label"] for row in records])
    scores = {name: np.asarray([row["scores"][name] for row in records]) for name in SYSTEMS}
    masks = [np.asarray([row["dataset"] == domain for row in records])
             for domain in sorted({row["dataset"] for row in records})]

    def aucs(weight):
        values = {name: [weighted_ranking(y[mask], p[mask], weight[mask], "auroc") for mask in masks]
                  for name, p in scores.items()}
        if any(value is None for items in values.values() for value in items):
            return None
        return {name: float(np.mean(items)) for name, items in values.items()}

    point = aucs(np.ones(len(y)))
    if point is None:
        raise ValueError("both-class point AUROC support required")
    rng, samples = np.random.default_rng(seed), {name: [] for name in SYSTEMS}
    differences = {name: [] for name in CONTRASTS}
    for _ in range(repetitions):
        guard()
        values = aucs(cluster_weights(records, rng))
        if values is not None:
            for name in SYSTEMS:
                samples[name].append(values[name])
            for name in CONTRASTS:
                differences[name].append(values["supervised_clip"] - values[name])
    valid = len(samples["supervised_clip"])
    if valid < repetitions * 0.95:
        raise ValueError("at least95% paired bootstrap replicates must have both source classes")
    return {
        "requested": repetitions, "valid": valid,
        "scope": "conditional_saved_predictors_dataset_stratified_group_bootstrap_not_training_or_new_domain_uncertainty",
        "macro_auroc_ci95": {name: np.quantile(values, [0.025, 0.975]).tolist()
                             for name, values in samples.items()},
        "supervised_clip_minus": {
            name: {"delta": point["supervised_clip"] - point[name],
                   "ci95": np.quantile(values, [0.025, 0.975]).tolist()}
            for name, values in differences.items()},
    }


def error_overlap(records: list[dict]) -> dict:
    y = np.asarray([row["label"] for row in records])
    errors = {name: np.asarray([row["scores"][name] >= row["thresholds"][name] for row in records]) != y
              for name in SYSTEMS}
    return {name: {
        "both_wrong": int(np.sum(errors["supervised_clip"] & errors[name])),
        "clip_only_wrong": int(np.sum(errors["supervised_clip"] & ~errors[name])),
        "comparator_only_wrong": int(np.sum(~errors["supervised_clip"] & errors[name])),
        "both_correct": int(np.sum(~errors["supervised_clip"] & ~errors[name])),
        "population": "common_successful_images_only_not_a_fusion_selection_objective",
    } for name in ("selected_dino_reg", "selected_two_dino")}
