"""Prepare and run one owner-approved, cache-only nested fusion utility study."""

from __future__ import annotations

import argparse
from html import escape
from itertools import combinations
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import numpy as np
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from fas.feature_cache import digest, payload_digest
from fas.freeze import write_immutable_record
from fas.fusion_study import (
    BRANCHES, FAMILIES, SYSTEMS, check_isolation, components, job_key, make_split,
    operating_metrics, paired_uncertainty, require_support, select_weight, summarize, support,
)
from fas.readout_study import check_head, transform
from fas.source_fitting import (
    calibrate, fit_calibrator, fit_head, head_logits, identity, objective_weights, operating_threshold,
)
import run_readout308 as prior

CONFIG = ROOT / "configs/fusion313_v1.yaml"
read = prior.read
check_reconstruction = prior.check_reconstruction


def output(config: dict) -> Path:
    return Path(config["private_root"]) / config["output_name"]


def code_pins() -> dict:
    paths = {*ROOT.glob("src/fas/*.py"), *ROOT.glob("scripts/*.py"),
             *ROOT.glob("configs/*.yaml"), ROOT / "configs/ci-synthetic308.in",
             ROOT / "tests/test_readout308.py", ROOT / "tests/test_fusion313.py",
             ROOT / "docs/313-bounded-nested-fusion-utility-execution-package.md"}
    return {str(path.relative_to(ROOT)): digest(path) for path in sorted(paths)}


def load_inputs(config: dict, guard) -> tuple[dict, list[dict], dict, dict, dict]:
    inherited = read(prior.CONFIG)
    if (digest(prior.CONFIG) != config["readout_config_sha256"]
            or inherited["private_root"] != config["private_root"]
            or inherited["seeds"] != config["seeds"]
            or set(inherited["outer_exclusions"]) != set(config["domains"])):
        raise ValueError("fixed original readout input/recipe configuration required")
    root = Path(config["private_root"])
    for filename, sha in (
        ("worker_completion.json", config["readout_completion_sha256"]),
        ("execution_plan.json", config["readout_plan_sha256"]),
    ):
        if digest(root / inherited["output_name"] / filename) != sha:
            raise ValueError("completed308 saved-state receipt drift")
    prior.check_runtime(inherited)
    inputs, originals, features, _, bindings = prior.load_inputs(inherited, guard)
    return inputs, originals, features, bindings, inherited


def allowed_rows(originals: list[dict], domains: list[str], *, g_domain: bool) -> list[dict]:
    return [row for row in originals if row["dataset"] in domains
            and (row["role"] == "g_domain") == g_domain]


def registry(inputs: dict, inherited: dict, guard) -> dict:
    root = Path(inherited["private_root"])
    old_receipt = read(root / inherited["baseline"] / "worker_completion.json")
    new_receipt = read(root / inherited["output_name"] / "worker_completion.json")
    indexed = {identity(row): row for row in inputs["rows"]}
    result = {}
    for context in sorted(inputs["contexts"], key=lambda item: item["key"]):
        old_context = next(item for item in old_receipt["combinations"] if item["key"] == context["key"])
        new_context = next(item for item in new_receipt["combinations"] if item["key"] == context["key"])
        for split in prior.study_splits(context):
            guard()
            thin = {name: split[name] for name in ("fitting", "validation", "calibration")}
            domains = sorted({indexed[key]["dataset"] for key in thin["fitting"]})
            key = job_key(domains, context["seed"], thin)
            old_path = prior.fit_path(inherited, context, split)
            old_sha = next(item["sha256"] for item in old_context["contexts"] if item["context"] == split["name"])
            artifact = new_context["fit_artifacts"][split["name"]]
            new_path = Path(artifact["path"])
            if digest(old_path) != old_sha or digest(new_path) != artifact["sha256"]:
                raise ValueError("published saved model bytes changed")
            old, new = read(old_path)["fitted"], read(new_path)["fitted"]
            if (old["split"] != split or new["split"] != split
                    or new["selected"]["openclip"] != 2
                    or inherited["candidates"][2] != {
                        "name": "higher_lr", "transform": "raw", "settings": {"learning_rate": 0.01}}):
                raise ValueError("exact split and fixed supervised309 CLIP recipe/calibrator required")
            value = {"baseline_path": str(old_path), "baseline_sha256": old_sha,
                     "readout_path": str(new_path), "readout_sha256": artifact["sha256"]}
            if key not in result:
                result[key] = value
    return result


def build_plan(config: dict, inputs: dict, originals: list[dict], bindings: dict,
               inherited: dict, guard) -> dict:
    if (config["weights"] != [0, 0.1, 0.25, 0.5, 0.75, 1]
            or config["automatic_retry"] is not False or config["encoder_forwards"] != 0
            or config["new_target_evaluations"] != 0):
        raise ValueError("fixed bounded fusion protocol required")
    rows = inputs["rows"]
    indexed = {identity(row): row for row in rows}
    reuse = registry(inputs, inherited, guard)
    jobs = {}
    for seed in config["seeds"]:
        for count in (1, 2, 3):
            for domains_tuple in combinations(sorted(config["domains"]), count):
                guard()
                domains = list(domains_tuple)
                split = make_split(rows, domains, seed)
                key = job_key(domains, seed, split)
                inventories = {}
                for name, ids in split.items():
                    pool = [indexed[value] for value in ids]
                    inventories[name] = support(pool)
                    require_support(inventories[name], config["support"][name], f"{key}/{name}")
                inventories["training_role_original"] = support([
                    row for row in originals if row["dataset"] in domains and row["role"] == "train"])
                inventories["calibration_role_original"] = support([
                    row for row in originals if row["dataset"] in domains and row["role"] == "branch_calibration"])
                jobs[key] = {"id": key, "domains": domains, "seed": seed, "split": split,
                             "support": inventories, "reuse": reuse.get(key)}
    by_sources = {(tuple(job["domains"]), job["seed"]): job["id"] for job in jobs.values()}
    predictions = {}

    def prediction(key: str, domain: str, pool: str) -> str:
        pkey = payload_digest({"job": key, "dataset": domain, "pool": pool})
        if pkey not in predictions:
            original = allowed_rows(originals, [domain], g_domain=pool == "g_domain")
            fitting_pools = [[indexed[value] for value in ids] for ids in jobs[key]["split"].values()]
            check_isolation([*fitting_pools, original])
            inventory = support(original)
            require_support(inventory, config["support"]["evaluation"], f"prediction/{pkey}")
            predictions[pkey] = {"id": pkey, "job": key, "dataset": domain,
                                 "pool": pool, "support": inventory}
        return pkey

    for job in jobs.values():
        job["inner_predictions"] = []
        if len(job["domains"]) > 1:
            for domain in job["domains"]:
                child = by_sources[(tuple(value for value in job["domains"] if value != domain), job["seed"])]
                job["inner_predictions"].append(prediction(child, domain, "domain_oof"))
    evaluations = []
    for context in inputs["contexts"]:
        domains = sorted(set(config["domains"]) - {context["outer_target"]})
        for split in prior.study_splits(context):
            is_final = split["name"] == "final"
            evaluation_domains = domains if is_final else [split["name"].split(":", 1)[1]]
            allowed = domains if is_final else [value for value in domains if value not in evaluation_domains]
            key = by_sources[(tuple(allowed), context["seed"])]
            if any(jobs[key]["split"][name] != split[name] for name in jobs[key]["split"]):
                raise ValueError("new pipeline must preserve inherited exact role/group membership")
            for domain in evaluation_domains:
                pool = "g_domain" if is_final else "domain_oof"
                evaluations.append({
                    "id": f"{context['key']}/{split['name']}/{domain}",
                    "outer_exclusion": context["outer_target"], "dataset": domain,
                    "seed": context["seed"], "pool": pool, "job": key,
                    "prediction": prediction(key, domain, pool),
                })
    if any(job["reuse"] is None for job in jobs.values() if len(job["domains"]) > 1):
        raise ValueError("all inherited two/three-source states must be reused, not rerun")
    new = sum(job["reuse"] is None for job in jobs.values())
    counts = {
        "unique_core_pipelines": len(jobs), "new_head_fits": new * 3,
        "new_calibrator_fits": new * 3, "reused_core_heads": (len(jobs) - new) * 3,
        "reused_core_calibrators": (len(jobs) - new) * 3,
        "reused_selected_reference_head_slots": (len(jobs) - new) * 2,
        "reused_selected_reference_calibrator_slots": (len(jobs) - new) * 2,
        "unique_threshold_policies": len(jobs) * 11 + len(jobs) - new,
        "family_weight_selections": sum(len(job["domains"]) > 1 for job in jobs.values()) * 2,
        "unique_prediction_tasks": len(predictions),
        "domain_oof_evaluation_folds": sum(item["pool"] == "domain_oof" for item in evaluations),
        "g_domain_evaluation_folds": sum(item["pool"] == "g_domain" for item in evaluations),
        "maximum_new_training_epochs": new * 3 * inherited["head"]["epochs"],
    }
    return {
        "study": config["study"], "status": "prepared_not_authorized",
        "config_sha256": digest(CONFIG), "code_sha256": code_pins(),
        "runtime": prior.check_runtime(inherited), "cache_bindings": bindings,
        "inherited_input_sha256": inherited["pinned_inputs"],
        "readout_completion_sha256": config["readout_completion_sha256"],
        "jobs": jobs, "predictions": predictions, "evaluations": evaluations, "counts": counts,
        "limits": config["limits"], "originals": len(originals), "usable": len(rows),
        "technical_failures": len(originals) - len(rows),
        "encoder_forwards": 0, "new_target_evaluations": 0,
    }


def prepare(*, seal: bool) -> dict:
    config = read(CONFIG)
    inputs, originals, _, bindings, inherited = load_inputs(config, lambda: None)
    plan = build_plan(config, inputs, originals, bindings, inherited, lambda: None)
    if seal:
        private = output(config) / "execution_plan.json"
        if private.exists():
            check_reconstruction(read(private), plan)
        else:
            write_immutable_record(private, plan)
        public = {key: value for key, value in plan.items() if key not in {"jobs", "predictions", "evaluations"}}
        public["private_plan_sha256"] = digest(private)
        public["pipeline_inventory"] = [
            {key: job[key] for key in ("id", "domains", "seed", "support", "reuse")}
            for job in plan["jobs"].values()]
        public["prediction_support"] = list(plan["predictions"].values())
        path = ROOT / "results/phase1/fusion313-plan-v1.json"
        if path.exists():
            check_reconstruction(read(path), public)
        else:
            write_immutable_record(path, public)
    print(json.dumps({"status": plan["status"], "counts": plan["counts"],
                      "limits": plan["limits"], "sealed": seal}), flush=True)
    return plan


def authority() -> tuple[dict, dict, dict]:
    config = read(CONFIG)
    root = output(config)
    plan = read(root / "execution_plan.json")
    approval = read(root / "execution_approval.json")
    if (plan["config_sha256"] != digest(CONFIG) or plan["code_sha256"] != code_pins()
            or approval["plan_sha256"] != digest(root / "execution_plan.json")
            or approval["owner"] != "lathevinh" or approval["scope"] != config["study"]
            or approval["deadline_unix"] != approval["started_unix"] + config["limits"]["wall_seconds"]):
        raise ValueError("exact tested code/config/plan and explicit scoped owner approval required")
    return config, plan, approval


def approve() -> None:
    config = read(CONFIG)
    root = output(config)
    plan = read(root / "execution_plan.json")
    if plan["config_sha256"] != digest(CONFIG) or plan["code_sha256"] != code_pins():
        raise ValueError("seal the complete tested package before approval")
    started = time.time()
    write_immutable_record(root / "execution_approval.json", {
        "owner": "lathevinh", "scope": config["study"], "plan_sha256": digest(root / "execution_plan.json"),
        "started_unix": started, "deadline_unix": started + config["limits"]["wall_seconds"],
        "authority": "explicit_owner_chat_approval_recorded_by_operator", "automatic_retry": False,
    })


def recipe(inherited: dict, branch: str) -> dict:
    return {**inherited["head"], **({"learning_rate": 0.01} if branch == "openclip" else {})}


def reused_models(job: dict, inherited: dict) -> dict:
    source = job["reuse"]
    old = read(Path(source["baseline_path"]))["fitted"]
    new = read(Path(source["readout_path"]))["fitted"]
    core = {
        branch: {"model": old["heads"][branch], "calibrator": old["calibrators"][branch], "transform": "raw"}
        for branch in ("dino_reg", "dino_plain")}
    core["openclip"] = {"model": new["candidates"]["openclip"][2]["model"],
                        "calibrator": new["calibrators"]["openclip"], "transform": "raw"}
    reference = {
        branch: {"model": new["candidates"][branch][new["selected"][branch]]["model"],
                 "calibrator": new["calibrators"][branch],
                 "transform": inherited["candidates"][new["selected"][branch]]["transform"]}
        for branch in ("dino_reg", "dino_plain")}
    return {"core": core, "selected_reference": reference}


def policy_key(family: str, weight: float) -> str:
    return "dino_only" if weight == 0 else f"{family}:{weight:g}"


def probabilities(models: dict, features: dict, positions: np.ndarray) -> dict:
    return {
        branch: calibrate(item["calibrator"], head_logits(
            item["model"], transform(features[branch][positions], item["transform"])))
        for branch, item in models.items()}


def verify_models(models: dict, job: dict, rows: list[dict], features: dict, inherited: dict) -> None:
    index = {identity(row): position for position, row in enumerate(rows)}
    positions = {key: np.asarray([index[value] for value in job["split"][key]], dtype=np.int64)
                 for key in ("validation", "calibration")}
    labels = np.asarray([row["binary_label"] == "attack" for row in rows], dtype=float)
    for group in ("core", "selected_reference"):
        for branch, item in models[group].items():
            if item["model"]["seed"] != job["seed"]:
                raise ValueError("saved model seed must match the declared unique fit")
            val, cal = positions["validation"], positions["calibration"]
            domains = [rows[position]["dataset"] for position in val]
            check_head(item["model"], transform(features[branch][val], item["transform"]),
                       labels[val], domains, inherited["head"]["epochs"])
            model = item["calibrator"]
            if (model["optimizer_success"] is not True or not np.isfinite(model["slope"])
                    or model["slope"] <= 0 or not np.isfinite(model["intercept"])):
                raise ValueError("successful finite monotone calibrator required")
            logits = head_logits(item["model"], transform(features[branch][cal], item["transform"]))
            z = model["slope"] * logits + model["intercept"]
            weights = objective_weights(labels[cal], [rows[position]["dataset"] for position in cal], balanced=True)
            if not np.isclose(weights @ (np.logaddexp(0, z) - labels[cal] * z),
                              model["bce"], rtol=1e-10, atol=1e-10):
                raise ValueError("saved calibration objective does not reconstruct")


def thresholds(models: dict, job: dict, rows: list[dict], features: dict, config: dict) -> dict:
    index = {identity(row): position for position, row in enumerate(rows)}
    positions = np.asarray([index[key] for key in job["split"]["calibration"]], dtype=np.int64)
    calibration = [rows[position] for position in positions]
    p = probabilities(models["core"], features, positions)
    result = {}
    for family, branch in FAMILIES.items():
        for weight in config["weights"]:
            key = policy_key(family, weight)
            if key not in result:
                result[key] = operating_threshold(
                    (1 - weight) * p["dino_reg"] + weight * p[branch], calibration, alpha=config["alpha"])
    if models["selected_reference"]:
        reference = probabilities(models["selected_reference"], features, positions)
        result["selected_two_dino"] = operating_threshold(
            (reference["dino_reg"] + reference["dino_plain"]) / 2, calibration, alpha=config["alpha"])
    return result


def fit_job(job: dict, rows: list[dict], features: dict, inherited: dict, config: dict,
            guard, counters: dict, counts: dict, checkpoint) -> dict:
    if job["reuse"] is not None:
        models = reused_models(job, inherited)
    else:
        models = {"core": {}, "selected_reference": {}}
        index = {identity(row): position for position, row in enumerate(rows)}
        positions = {name: np.asarray([index[key] for key in ids], dtype=np.int64)
                     for name, ids in job["split"].items()}
        y = np.asarray([row["binary_label"] == "attack" for row in rows], dtype=float)
        domains = lambda selected: [rows[position]["dataset"] for position in selected]
        fit, val, cal = (positions[name] for name in ("fitting", "validation", "calibration"))
        for branch in BRANCHES:
            guard()
            counters["new_head_fits"] += 1
            if counters["new_head_fits"] > counts["new_head_fits"]:
                raise RuntimeError("registered unique head-fit budget exhausted; no retry")
            checkpoint(f"{branch}-head-start", {"counts": dict(counters)})
            model = fit_head(features[branch][fit], y[fit], domains(fit),
                             features[branch][val], y[val], domains(val), seed=job["seed"],
                             settings=recipe(inherited, branch), guard=guard)
            checkpoint(f"{branch}-head-complete", model)
            counters["new_calibrator_fits"] += 1
            if counters["new_calibrator_fits"] > counts["new_calibrator_fits"]:
                raise RuntimeError("registered unique calibrator budget exhausted; no retry")
            checkpoint(f"{branch}-calibrator-start", {"counts": dict(counters)})
            calibrated = fit_calibrator(head_logits(model, features[branch][cal]), y[cal], domains(cal), guard)
            checkpoint(f"{branch}-calibrator-complete", calibrated)
            models["core"][branch] = {"model": model, "calibrator": calibrated, "transform": "raw"}
    verify_models(models, job, rows, features, inherited)
    return {"models": models, "policies": thresholds(models, job, rows, features, config),
            "diagnostic_only": diagnostics(models, job, rows, features)}


def quantiles(values: np.ndarray, rows: list[dict]) -> dict:
    return {
        label: np.quantile(values[[row["binary_label"] == label for row in rows]],
                           [0, 0.1, 0.5, 0.9, 1]).tolist()
        for label in ("bona_fide", "attack")}


def diagnostics(models: dict, job: dict, rows: list[dict], features: dict) -> dict:
    index = {identity(row): position for position, row in enumerate(rows)}
    cal = np.asarray([index[key] for key in job["split"]["calibration"]], dtype=np.int64)
    result = {"calibration_score_quantiles": {}, "validation_tails_not_stationarity_tests": {}}
    for domain in job["domains"]:
        positions = cal[[rows[position]["dataset"] == domain for position in cal]]
        selected = [rows[position] for position in positions]
        result["calibration_score_quantiles"][domain] = {}
        for branch, item in models["core"].items():
            raw = head_logits(item["model"], transform(features[branch][positions], item["transform"]))
            result["calibration_score_quantiles"][domain][branch] = {
                "raw": quantiles(raw, selected),
                "calibrated": quantiles(calibrate(item["calibrator"], raw), selected)}
    for branch, item in models["core"].items():
        history = item["model"]["validation_history"]
        start = max(1, len(history) - 20)
        drop = history[start - 1] - history[-1]
        result["validation_tails_not_stationarity_tests"][branch] = {
            "selected_epoch": item["model"]["selected_epoch"],
            "tail_start_epoch": start, "tail_end_epoch": len(history),
            "absolute_drop": drop,
            "relative_drop": drop / history[start - 1] if history[start - 1] else None,
            "relative_drop_estimable": bool(history[start - 1]),
        }
    return result


def diagnostic_plot(folds: list[dict], domain: str, pool: str, config: dict) -> str:
    subset = [fold for fold in folds if fold["dataset"] == domain and fold["pool"] == pool]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="460" viewBox="0 0 600 460">',
        '<rect width="600" height="460" fill="white"/>',
        f'<text x="50" y="25">{escape(domain)} / {pool}: descriptive held-out operating points</text>',
        '<path d="M50 50 V390 H550" fill="none" stroke="black"/>',
        '<text x="180" y="440">Original attack FA (0 to 100%)</text>',
        '<text x="55" y="45">Original bona-fide acceptance (0 to 100%)</text>',
        f'<path d="M{50 + 500 * config["alpha"]:.6f} 50 V390" stroke="#888888" stroke-dasharray="4 4"/>',
        f'<path d="M50 {390 - 340 * config["minimum_bona_fide_acceptance"]:.6f} H550" stroke="#888888" stroke-dasharray="4 4"/>',
    ]
    for name, color in (("dino_clip", "#c43c39"), ("two_dino", "#2463a5"), ("dino_only", "#555555")):
        missing = 0
        for fold in subset:
            item = fold["systems"][name]
            if item["metrics"] is None:
                missing += 1
                continue
            x = 50 + 500 * item["metrics"]["original_attack_FA"]
            y = 390 - 340 * item["metrics"]["original_bona_fide_acceptance"]
            parts.append(f'<circle cx="{x:.6f}" cy="{y:.6f}" r="4" fill="{color}" fill-opacity="0.6"/>')
        number = ("dino_clip", "two_dino", "dino_only").index(name)
        parts.append(f'<text x="320" y="{70 + number * 20}" fill="{color}">{name}: {missing} missing policies</text>')
    parts.append('</svg>\n')
    return "\n".join(parts)


def predict(task: dict, job: dict, fitted: dict, originals: list[dict],
            rows: list[dict], features: dict) -> dict:
    population = allowed_rows(originals, [task["dataset"]], g_domain=task["pool"] == "g_domain")
    successful = [row for row in population if row["model_input_eligible"]]
    index = {identity(row): position for position, row in enumerate(rows)}
    positions = np.asarray([index[identity(row)] for row in successful], dtype=np.int64)
    models = fitted["models"]
    p = probabilities(models["core"], features, positions)
    result = {"ids": [identity(row) for row in successful],
              "p": {name: values.tolist() for name, values in p.items()},
              "selected_two_dino": None, "diagnostic_only_quantiles": {}}
    if models["selected_reference"]:
        reference = probabilities(models["selected_reference"], features, positions)
        result["selected_two_dino"] = ((reference["dino_reg"] + reference["dino_plain"]) / 2).tolist()
    for branch in BRANCHES:
        item = models["core"][branch]
        raw = head_logits(item["model"], transform(features[branch][positions], item["transform"]))
        result["diagnostic_only_quantiles"][branch] = {
            "raw": quantiles(raw, successful), "calibrated": quantiles(p[branch], successful)}
    return result


def select(job: dict, plan: dict, predictions: dict, fitted: dict,
           originals: list[dict], config: dict) -> dict:
    result = {}
    for family, branch in FAMILIES.items():
        candidates = []
        for weight in config["weights"]:
            per_domain = {}
            for pkey in job["inner_predictions"]:
                task = plan["predictions"][pkey]
                if task["dataset"] not in job["domains"] or task["pool"] != "domain_oof":
                    raise ValueError("inner selection must use permitted non-g_domain sources only")
                child = plan["jobs"][task["job"]]
                if set(child["domains"]) != set(job["domains"]) - {task["dataset"]}:
                    raise ValueError("complete inner held-out domain must be excluded from fitted pipeline")
                pred = predictions[pkey]
                population = allowed_rows(originals, [task["dataset"]], g_domain=False)
                successful = [row for row in population if row["model_input_eligible"]]
                if pred["ids"] != [identity(row) for row in successful]:
                    raise ValueError("exact inner prediction identity order required")
                score = (1 - weight) * np.asarray(pred["p"]["dino_reg"]) + weight * np.asarray(pred["p"][branch])
                policy = fitted[child["id"]]["policies"][policy_key(family, weight)]
                per_domain.update(operating_metrics(score, policy["threshold"], successful, population, config))
            candidates.append({"weight": weight, "per_domain": per_domain})
        result[family] = {"selection": select_weight(candidates, config), "candidates": candidates}
    return result


def evaluate(evaluation: dict, fitted: dict, prediction: dict, selection: dict,
             originals: list[dict], config: dict) -> tuple[dict, dict]:
    population = allowed_rows(originals, [evaluation["dataset"]], g_domain=evaluation["pool"] == "g_domain")
    rows = [row for row in population if row["model_input_eligible"]]
    if prediction["ids"] != [identity(row) for row in rows]:
        raise ValueError("exact evaluation prediction identity order required")
    p = {name: np.asarray(values) for name, values in prediction["p"].items()}
    specifications = {
        "dino_only": ("dino_clip", 0), "plain_only": ("two_dino", 1),
        "clip_only": ("dino_clip", 1), "fixed_two_dino": ("two_dino", 0.5),
        "fixed_dino_clip": ("dino_clip", 0.5),
    }
    for family in FAMILIES:
        specifications[family] = (family, selection[family]["selection"]["weight"])
    result = {key: value for key, value in evaluation.items() if key != "prediction"}
    result["systems"], accepted = {}, {}
    for name in SYSTEMS:
        if name == "selected_two_dino":
            if prediction[name] is None:
                raise ValueError("inherited selected two-DINO reference required in outer evaluations")
            scores = np.asarray(prediction[name])
            policy = fitted["policies"][name]
        else:
            family, weight = specifications[name]
            if weight is None:
                result["systems"][name] = {
                    "status": "no_candidate_meets_declared_utility", "weight": None,
                    "metrics": None, "policy": None}
                continue
            scores = (1 - weight) * p["dino_reg"] + weight * p[FAMILIES[family]]
            policy = fitted["policies"][policy_key(family, weight)]
        metrics = operating_metrics(scores, policy["threshold"], rows, population, config, ranking=True)[evaluation["dataset"]]
        result["systems"][name] = {
            "status": "transfer_feasible" if metrics["empirical_utility_feasible"] else "transfer_failure",
            "weight": None if name == "selected_two_dino" else specifications[name][1],
            "metrics": metrics, "policy": policy}
        accepted[name] = [identity(row) for row, accept in zip(rows, scores < policy["threshold"], strict=True) if accept]
    return result, accepted


def run_worker(*, reconstruct: bool = False) -> dict:
    config, plan, approval = authority()
    root = output(config)
    attempt = read(root / "attempt_lock.json")
    if os.getppid() != attempt["supervisor_pid"]:
        raise RuntimeError("worker/reconstruction requires its live approving supervisor")
    guard = lambda: prior.deadline_guard(approval)
    guard()
    inputs, originals, features, bindings, inherited = load_inputs(config, guard)
    check_reconstruction(plan, build_plan(config, inputs, originals, bindings, inherited, guard))
    rows = inputs["rows"]
    counters = {"new_head_fits": 0, "new_calibrator_fits": 0}
    models, artifacts = {}, {}
    plan_sha = digest(root / "execution_plan.json")
    for key, job in plan["jobs"].items():
        guard()
        path = root / "fits" / f"{key}.json"

        def checkpoint(name: str, value: dict) -> None:
            write_immutable_record(root / "checkpoints" / f"{key}-{name}.json",
                                   {"job": key, "plan_sha256": plan_sha, "value": value})
            print("FUSION313_FIT", key, name, flush=True)

        if reconstruct:
            saved = read(path)
            if saved["plan_sha256"] != plan_sha or saved["job"] != job:
                raise ValueError("saved unique fit provenance drift")
            fitted = saved["fitted"]
            if job["reuse"] is not None:
                check_reconstruction(fitted["models"], reused_models(job, inherited))
            else:
                for branch in BRANCHES:
                    for kind, field in (("head", "model"), ("calibrator", "calibrator")):
                        counters["new_head_fits" if kind == "head" else "new_calibrator_fits"] += 1
                        started = read(root / "checkpoints" / f"{key}-{branch}-{kind}-start.json")
                        finished = read(root / "checkpoints" / f"{key}-{branch}-{kind}-complete.json")
                        if any(record["plan_sha256"] != plan_sha or record["job"] != key
                               for record in (started, finished)):
                            raise ValueError("checkpoint membership/plan drift")
                        check_reconstruction(started["value"]["counts"], counters)
                        check_reconstruction(finished["value"], fitted["models"]["core"][branch][field])
            verify_models(fitted["models"], job, rows, features, inherited)
            check_reconstruction(fitted["policies"], thresholds(fitted["models"], job, rows, features, config))
            check_reconstruction(fitted["diagnostic_only"], diagnostics(fitted["models"], job, rows, features))
        else:
            fitted = fit_job(job, rows, features, inherited, config, guard, counters, plan["counts"], checkpoint)
            write_immutable_record(path, {"plan_sha256": plan_sha, "job": job, "fitted": fitted,
                                         "fit_counts_at_completion": dict(counters)})
        if read(path)["fit_counts_at_completion"] != counters:
            raise ValueError("incremental unique fit-attempt ledger drift")
        models[key] = fitted
        artifacts[key] = {
            "sha256": digest(path), "reused": job["reuse"] is not None,
            "checkpoint_sha256": {item.name: digest(item)
                                  for item in sorted((root / "checkpoints").glob(f"{key}-*.json"))},
        }
    if counters != {name: plan["counts"][name] for name in counters}:
        raise ValueError("all and only registered unique fits required")
    predictions, prediction_artifacts = {}, {}
    for key, task in plan["predictions"].items():
        guard()
        value = predict(task, plan["jobs"][task["job"]], models[task["job"]], originals, rows, features)
        path = root / "predictions" / f"{key}.json"
        if reconstruct:
            check_reconstruction(read(path), value)
        else:
            write_immutable_record(path, value)
        predictions[key] = value
        prediction_artifacts[key] = digest(path)
    selections = {}
    for key, job in plan["jobs"].items():
        if job["inner_predictions"]:
            selections[key] = select(job, plan, predictions, models, originals, config)
    folds, accepted = [], {}
    for item in plan["evaluations"]:
        guard()
        fold, ids = evaluate(item, models[item["job"]], predictions[item["prediction"]],
                             selections[item["job"]], originals, config)
        folds.append(fold)
        accepted[item["id"]] = ids
    pools = {}
    plots = {}
    for pool in ("domain_oof", "g_domain"):
        subset = [fold for fold in folds if fold["pool"] == pool]
        population = allowed_rows(originals, config["domains"], g_domain=pool == "g_domain")
        pools[pool] = {
            "decision_role": "primary" if pool == "domain_oof" else "within_source_group_diagnostic_only",
            "summary": summarize(subset, config),
            "uncertainty": paired_uncertainty(subset, population, accepted, config, guard)}
        for domain in config["domains"]:
            text = diagnostic_plot(folds, domain, pool, config)
            path = root / "diagnostics" / f"{pool}-{domain}.svg"
            if reconstruct:
                if path.read_text() != text:
                    raise ValueError("deterministic diagnostic plot drift")
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("x") as stream:
                    stream.write(text)
            plots[f"{pool}/{domain}"] = digest(path)
    result = {
        "study": config["study"], "plan_sha256": plan_sha, "counts": plan["counts"],
        "fit_artifacts": artifacts, "prediction_artifacts": prediction_artifacts,
        "selections": selections, "folds": folds, "evaluation": pools,
        "diagnostic_plot_sha256": plots,
        "encoder_forwards": 0, "new_target_evaluations": 0,
        "no_independent_target_or_deployment_claim": True,
    }
    path = root / "worker_completion.json"
    if reconstruct:
        check_reconstruction(read(path), result)
        write_immutable_record(root / "saved_reconstruction.json", {
            "worker_completion_sha256": digest(path), "plan_sha256": plan_sha,
            "all_models_predictions_selection_metrics_and_bootstrap_reconstructed": True,
            "new_fits": 0, "encoder_forwards": 0})
    else:
        write_immutable_record(path, result)
    print("FUSION313_RECONSTRUCTED" if reconstruct else "FUSION313_COMPLETED",
          pools["domain_oof"]["summary"]["decision"], flush=True)
    return result


def supervise() -> int:
    config, _, approval = authority()
    root, limits = output(config), config["limits"]
    prior.deadline_guard(approval)
    write_immutable_record(root / "attempt_lock.json", {
        "supervisor_pid": os.getpid(), "plan_sha256": digest(root / "execution_plan.json"),
        "automatic_retry": False})
    env = {**os.environ, "OPENBLAS_NUM_THREADS": str(limits["blas_threads"]),
           "OMP_NUM_THREADS": str(limits["blas_threads"]), "MKL_NUM_THREADS": str(limits["blas_threads"]),
           "CUDA_VISIBLE_DEVICES": "", "HF_HUB_OFFLINE": "1", "PYTHONDONTWRITEBYTECODE": "1",
           "TMPDIR": str(root / "temporary")}
    (root / "temporary").mkdir(exist_ok=False)
    child, failure, peak_rss, peak_bytes = None, None, 0, prior.owned_size(root)
    try:
        for phase in ("worker", "reconstruct"):
            prior.deadline_guard(approval)
            if prior.owned_size(root) + limits["terminal_reserve_bytes"] > limits["owned_output_bytes"]:
                raise MemoryError("insufficient reserved output space before phase")
            with (root / f"{phase}.log").open("x") as log:
                child = subprocess.Popen([sys.executable, str(Path(__file__)), f"--{phase}"],
                                         env=env, start_new_session=True, stdout=log, stderr=subprocess.STDOUT)
                while child.poll() is None:
                    prior.deadline_guard(approval)
                    own_rss = next(int(line.split()[1]) * 1024
                                   for line in Path(f"/proc/{os.getpid()}/status").read_text().splitlines()
                                   if line.startswith("VmRSS:"))
                    peak_rss = max(peak_rss, prior.baseline.pilot.group_rss(child.pid) + own_rss)
                    peak_bytes = max(peak_bytes, prior.owned_size(root))
                    if (peak_rss > limits["combined_sampled_rss_bytes"]
                            or peak_bytes + limits["terminal_reserve_bytes"] > limits["owned_output_bytes"]):
                        raise MemoryError("combined sampled RSS or owned output cap exceeded")
                    time.sleep(limits["sample_interval_seconds"])
                if child.returncode:
                    raise RuntimeError(f"{phase} exited {child.returncode}; see its log; no retry")
        if not (root / "saved_reconstruction.json").is_file():
            raise RuntimeError("independent saved reconstruction did not complete")
        prior.deadline_guard(approval)
    except (OSError, ValueError, RuntimeError, TimeoutError, MemoryError) as exc:
        failure = f"{type(exc).__name__}: {exc}"
        print("FUSION313_STOP", failure, file=sys.stderr, flush=True)
    finally:
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
    peak_bytes = max(peak_bytes, prior.owned_size(root))
    wall = time.time() - approval["started_unix"]
    if failure is None and (peak_bytes + limits["terminal_reserve_bytes"] > limits["owned_output_bytes"]
                            or wall > limits["wall_seconds"]):
        failure = "final resource inventory exceeded registered envelope"
    terminal = {
        "status": "complete" if failure is None else "stopped_no_retry", "failure": failure,
        "wall_seconds_from_original_approval": wall, "sampled_peak_combined_rss": peak_rss,
        "peak_owned_bytes_before_terminal": peak_bytes, "limits": limits, "automatic_retry": False,
        "worker_completion_sha256": digest(root / "worker_completion.json") if failure is None else None,
        "saved_reconstruction_sha256": digest(root / "saved_reconstruction.json") if failure is None else None,
    }
    if 2 * len((json.dumps(terminal, indent=2, sort_keys=True) + "\n").encode()) > limits["terminal_reserve_bytes"]:
        raise RuntimeError("terminal plus atomic temporary copy exceeds reserved audit space")
    write_immutable_record(root / "terminal.json", terminal)
    print("FUSION313_TERMINAL", json.dumps(terminal), flush=True)
    return int(failure is not None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    for name in ("inventory", "prepare", "approve", "execute", "worker", "reconstruct"):
        actions.add_argument(f"--{name}", action="store_true")
    args = parser.parse_args()
    if args.inventory or args.prepare:
        with threadpool_limits(limits=read(CONFIG)["limits"]["blas_threads"]):
            prepare(seal=args.prepare)
    elif args.approve:
        approve()
    elif args.execute:
        return supervise()
    else:
        with threadpool_limits(limits=read(CONFIG)["limits"]["blas_threads"]):
            run_worker(reconstruct=args.reconstruct)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
