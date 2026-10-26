"""Reusable context fitting and risk diagnostics for the sealed source experiment."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .feature_cache import digest, payload_digest
from .freeze import write_immutable_record
from .source_fitting import (
    calibrate, fit_calibrator, fit_head, fit_risk, group_assignments, head_logits,
    identity, operating_threshold, sigmoid,
)
from .source_diagnostics import design, drift, weighted_ranking
from .source_stage import require_source_input


def seal(path: Path, value: dict) -> None:
    import json
    if path.exists():
        if json.loads(path.read_bytes()) != value:
            raise ValueError(f"immutable experiment checkpoint drift: {path.name}")
    else:
        write_immutable_record(path, value)


def fit_context(rows: list[dict], features: dict, clip_logits: np.ndarray, split: dict, config: dict,
                root: Path, binding: dict, guard, reuse: dict | None = None) -> tuple[dict, dict]:
    for row in rows:
        purpose = {"train": "fitting", "branch_calibration": "calibration", "g_domain": "domain_use"}[row["role"]]
        require_source_input(row, outer_target=config["outer_target"], purpose=purpose, model_input=True)
    ids = {identity(row): index for index, row in enumerate(rows)}
    positions = lambda key: np.asarray([ids[value] for value in split[key]], dtype=np.int64)
    fit, validation, calibration = (positions(key) for key in ("fitting", "validation", "calibration"))
    labels = np.asarray([row["binary_label"] == "attack" for row in rows], dtype=np.float64)
    domains = lambda indices: [rows[index]["dataset"] for index in indices]
    path = root / f"{payload_digest({'split': split})}.json"
    if reuse is not None:
        if reuse["split"] != split:
            raise ValueError("unchanged completed context must have its exact original split")
        fitted = reuse
        origin = {"kind": "verified_completed_context_reuse", "original_binding": reuse["binding"]}
    elif path.exists():
        import json
        fitted = json.loads(path.read_bytes())["fitted"]
        if fitted["binding"] != binding or fitted["split"] != split:
            raise ValueError("completed context cache binding drift")
        origin = {"kind": "completed299_checkpoint"}
    else:
        heads, calibrators = {}, {}
        logits = {"openclip": clip_logits}
        for name in ("dino_reg", "dino_plain"):
            guard()
            heads[name] = fit_head(features[name][fit], labels[fit], domains(fit), features[name][validation],
                                   labels[validation], domains(validation), seed=config["seed"],
                                   settings=config["head"], guard=guard)
            logits[name] = head_logits(heads[name], features[name])
        for name in logits:
            calibrators[name] = fit_calibrator(logits[name][calibration].astype(np.float64),
                                               labels[calibration], domains(calibration), guard)
        p = {name: calibrate(calibrators[name], values[calibration]) for name, values in logits.items()}
        scores = system_scores(p)
        policies = {name: operating_threshold(values, [rows[index] for index in calibration], alpha=0.05)
                    for name, values in scores.items()}
        fitted = {"binding": binding, "split": split, "heads": heads, "calibrators": calibrators, "policies": policies}
        origin = {"kind": "new299_source_fit"}
    artifact = {"fitted": fitted, "origin": origin}
    if not path.exists():
        write_immutable_record(path, artifact)
    return fitted, {"path": str(path), "sha256": digest(path), "origin": origin["kind"],
                    "fit": len(fit), "validation": len(validation), "calibration": len(calibration),
                    "selected_epochs": {name: value["selected_epoch"] for name, value in fitted["heads"].items()}}


def system_scores(p: dict) -> dict:
    return {"dino_reg": p["dino_reg"], "openclip": p["openclip"],
            "heterogeneous": (p["dino_reg"] + p["openclip"]) / 2,
            "same_family": (p["dino_reg"] + p["dino_plain"]) / 2}


def predict(rows: list[dict], features: dict, clip_logits: np.ndarray, quality: np.ndarray,
            ids: list[str], fitted: dict, model_sha: str) -> list[dict]:
    indexed = {identity(row): index for index, row in enumerate(rows)}
    indices = np.asarray([indexed[key] for key in ids])
    logits = {name: head_logits(fitted["heads"][name], features[name][indices]) for name in ("dino_reg", "dino_plain")}
    logits["openclip"] = clip_logits[indices]
    p = {name: calibrate(fitted["calibrators"][name], value) for name, value in logits.items()}
    scores = system_scores(p)
    result = []
    for local, index in enumerate(indices):
        original = rows[index]
        label = int(original["binary_label"] == "attack")
        thresholds = {name: policy["threshold"] for name, policy in fitted["policies"].items()}
        values = {name: float(value[local]) for name, value in scores.items()}
        result.append({
            "id": identity(original), "dataset": original["dataset"], "group_id": original["group_id"],
            "role": original["role"], "label": label, "probabilities": {name: float(value[local]) for name, value in p.items()},
            "scores": values, "thresholds": thresholds,
            "errors": {name: int((value >= thresholds[name]) != bool(label)) for name, value in values.items()},
            "quality": quality[index].tolist(), "fit_sha256": model_sha,
        })
    return result


def risk_run(oof: list[dict], gate: list[dict], system: str, variant: str, mean: np.ndarray, scale: np.ndarray,
             root: Path, binding: dict, guard, reuse: dict | None = None) -> dict:
    path = root / f"{system}-{variant}.json"
    errors = np.asarray([row["errors"][system] for row in oof], dtype=np.int64)
    counts = {"error_count": int(errors.sum()), "correct_count": int(len(errors) - errors.sum())}
    if min(counts.values()) < 20:
        result = {"status": "not_applicable_insufficient_source_events", **counts,
                  "system": system, "variant": variant, "binding": binding}
        seal(path, result)
        return result
    if reuse is not None:
        if (reuse["quality_mean"] != mean.tolist() or reuse["quality_scale"] != scale.tolist()
                or reuse["model"]["error_count"] != counts["error_count"]
                or reuse["model"]["correct_count"] != counts["correct_count"]):
            raise ValueError("completed297 risk statistics/event binding drift")
        model = reuse["model"]
        origin = "verified297_risk_reuse"
    elif path.exists():
        import json
        saved = json.loads(path.read_bytes())
        if saved["binding"] != binding:
            raise ValueError("completed source risk provenance drift")
        return saved
    else:
        model = fit_risk(design(oof, system, variant, mean, scale), errors,
                         [row["dataset"] for row in oof], guard)
        origin = "new299_risk_fit"
    logits = head_logits(model, design(gate, system, variant, mean, scale))
    scores = sigmoid(logits)
    gate_errors = np.asarray([row["errors"][system] for row in gate])
    if reuse is not None and not np.allclose(
        [row["risk"] for row in reuse["g_domain_predictions"]], scores, rtol=1e-12, atol=1e-12
    ):
        raise ValueError("reused297 risk predictions must reconstruct before reuse")
    result = {"status": "fitted", **counts, "model": model, "origin": origin, "binding": binding,
              "system": system, "variant": variant, "quality_mean": mean.tolist(), "quality_scale": scale.tolist(),
              "held_out_error_AP": weighted_ranking(gate_errors, scores, np.ones(len(gate)), "ap"),
              "held_out_error_count": int(gate_errors.sum()),
              "held_out_brier": float(np.mean((scores - gate_errors) ** 2)),
              "held_out_nll": float(np.mean(np.logaddexp(0, logits) - gate_errors * logits)),
              "probability_calibration_claim": False,
              "predictions": [{"id": row["id"], "risk": float(value), "error": row["errors"][system]}
                              for row, value in zip(gate, scores, strict=True)]}
    seal(path, result)
    return result


def diagnostics(oof: list[dict], final_reference: list[dict], indexed: dict[str, dict],
                system: str, mean: np.ndarray, scale: np.ndarray, seed: int, guard) -> dict:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import balanced_accuracy_score
    import warnings
    from sklearn.exceptions import ConvergenceWarning

    reference = {row["id"]: row for row in final_reference}
    final = [reference[row["id"]] for row in oof]
    x = design(oof, system, "R_DVd", mean, scale)
    final_x = design(final, system, "R_DVd", mean, scale)
    assignments = group_assignments([indexed[row["id"]] for row in oof], seed, 3)
    training = np.asarray([assignments[row["id"]] != 0 for row in oof])
    domains = sorted({row["dataset"] for row in oof})
    y = np.asarray([domains.index(row["dataset"]) for row in oof])
    if set(y[training]) != set(range(3)) or set(y[~training]) != set(range(3)):
        raise ValueError("group-safe domain-identifiability audit requires all three domains on both sides")
    weights = np.zeros(training.sum())
    for domain in range(3):
        selected = y[training] == domain
        weights[selected] = training.sum() / (3 * selected.sum())
    guard()
    audit = LogisticRegression(C=1.0, max_iter=1000, tol=1e-7, random_state=seed)
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        audit.fit(x[training], y[training], sample_weight=weights)
    return {"domain_identifiability": {
        "holdout_balanced_accuracy": float(balanced_accuracy_score(y[~training], audit.predict(x[~training]))),
        "chance": 1 / 3, "training_count": int(training.sum()), "holdout_count": int((~training).sum()),
        "group_safe": True, "coefficients": audit.coef_.tolist(), "intercepts": audit.intercept_.tolist(),
        "diagnostic_only_no_feature_selection": True},
        "oof_to_final_drift": drift(x, final_x),
        "drift_per_source_domain": {domain: drift(x[y == index], final_x[y == index])
                                    for index, domain in enumerate(domains)},
        "final_reference_scope": "same_non_gate_originals_final_source_model_in_sample_not_competence"}
