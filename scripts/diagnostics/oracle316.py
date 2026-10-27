"""Evaluation-label oracle diagnostics on saved313 scores; never a deployable policy."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
import json
from pathlib import Path
import resource
import signal
import sys
import time

import numpy as np
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from fas.feature_cache import digest
from fas.freeze import write_immutable_record
from fas.source_fitting import identity
import run_fusion313 as frozen

ALPHA = Fraction(1, 20)
BETA = Fraction(1, 2)
SYSTEMS = ("dino_only", "plain_only", "clip_only", "fixed_two_dino",
           "selected_two_dino", "fixed_dino_clip")
STAGES = {1: "one_source_inner", 2: "two_source_domain_oof", 3: "three_source_g_domain"}
PRIVATE = Path("/mnt/e/FAS-private/artifacts/phase1")
OUTPUT = PRIVATE / "score_oracle316_v1"
PUBLIC = ROOT / "results/phase1/source-oracle316-v1.json"
TEST = ROOT / "tests/test_oracle316.py"
LIMITS = {"wall_seconds": 600, "process_peak_rss_bytes": 1073741824,
          "owned_output_bytes": 67108864, "blas_threads": 2}


def oracle(scores: np.ndarray, labels: np.ndarray, original_attack: int, original_bona_fide: int,
           *, alpha: Fraction = ALPHA, beta: Fraction = BETA) -> dict:
    if (not isinstance(original_attack, int) or isinstance(original_attack, bool) or original_attack <= 0
            or not isinstance(original_bona_fide, int) or isinstance(original_bona_fide, bool) or original_bona_fide <= 0
            or scores.ndim != 1 or labels.shape != scores.shape or not np.isfinite(scores).all()
            or np.any((scores < 0) | (scores > 1)) or not np.isin(labels, (0, 1)).all()
            or not isinstance(alpha, Fraction) or not 0 <= alpha < 1
            or not isinstance(beta, Fraction) or not 0 < beta <= 1):
        raise ValueError("finite joined PAD scores, binary labels, positive original counts and exact rate fractions required")
    attacks, real = scores[labels == 1], scores[labels == 0]
    if len(attacks) > original_attack or len(real) > original_bona_fide:
        raise ValueError("successful counts cannot exceed original class denominators")
    budget = original_attack * alpha.numerator // alpha.denominator
    needed = (original_bona_fide * beta.numerator + beta.denominator - 1) // beta.denominator
    upper = float(np.partition(attacks, budget)[budget]) if len(attacks) > budget else float(np.nextafter(1.0, 2.0))
    accepted_attack = int(np.sum(attacks < upper))
    accepted_real = int(np.sum(real < upper))
    lower = float(np.partition(real, needed - 1)[needed - 1]) if len(real) >= needed else None
    feasible = accepted_real >= needed
    if (lower is not None and (lower < upper) != feasible) or accepted_attack > budget:
        raise ValueError("oracle interval/order-statistic reconstruction failed")
    return {
        "original_attack": original_attack, "original_bona_fide": original_bona_fide,
        "successful_attack": len(attacks), "successful_bona_fide": len(real),
        "attack_error_budget": budget, "required_bona_fide_acceptances": needed,
        "oracle_accepted_attack": accepted_attack, "oracle_accepted_bona_fide": accepted_real,
        "oracle_FA": accepted_attack / original_attack,
        "oracle_max_BFA": accepted_real / original_bona_fide,
        "technical_failure_BFA_ceiling": len(real) / original_bona_fide,
        "empirically_attainable": feasible,
        "reason": ("attainable_on_this_sample" if feasible else
                   "technical_failure_BFA_ceiling" if lower is None else "low_FA_score_separation_insufficient"),
        "threshold_interval": {"lower_exclusive": lower, "upper_inclusive": upper,
                               "nonempty": feasible},
        "oracle_threshold_not_deployable": upper,
        "uses_evaluation_labels": True,
    }


def curve_check(result: dict, scores: np.ndarray, labels: np.ndarray) -> None:
    """Rebuild the complete grouped empirical curve, independently of order statistics."""
    values, inverse = np.unique(scores, return_inverse=True)
    attacks = np.bincount(inverse, weights=(labels == 1).astype(int), minlength=len(values)).astype(int)
    real = np.bincount(inverse, weights=(labels == 0).astype(int), minlength=len(values)).astype(int)
    thresholds = np.r_[0.0, values, np.nextafter(1.0, 2.0)]
    # Each score group is rejected at its own threshold; the last entry accepts all groups.
    accepted_attack = np.r_[0, np.cumsum(attacks) - attacks, attacks.sum()]
    accepted_real = np.r_[0, np.cumsum(real) - real, real.sum()]
    permitted = accepted_attack <= result["attack_error_budget"]
    chosen = int(np.flatnonzero(permitted)[-1])
    if (thresholds[chosen] != result["oracle_threshold_not_deployable"]
            or int(accepted_attack[chosen]) != result["oracle_accepted_attack"]
            or int(accepted_real[chosen]) != result["oracle_accepted_bona_fide"]):
        raise ValueError("independent grouped-curve oracle mismatch")
    lower = result["threshold_interval"]["lower_exclusive"]
    expected = permitted & (accepted_real >= result["required_bona_fide_acceptances"])
    membership = ((thresholds > lower) & (thresholds <= result["threshold_interval"]["upper_inclusive"])
                  if lower is not None else np.zeros(len(thresholds), dtype=bool))
    if not np.array_equal(expected, membership):
        raise ValueError("oracle feasible interval does not match the complete empirical curve")


def original_rates(scores: np.ndarray, labels: np.ndarray, threshold: float, result: dict) -> dict:
    if not np.isfinite(threshold) or not 0 <= threshold <= np.nextafter(1.0, 2.0):
        raise ValueError("finite inherited attack-high threshold required")
    accepted = scores < threshold
    attack = int(np.sum(accepted & (labels == 1)))
    real = int(np.sum(accepted & (labels == 0)))
    safe = attack <= result["attack_error_budget"]
    useful = real >= result["required_bona_fide_acceptances"]
    if safe and real > result["oracle_accepted_bona_fide"]:
        raise ValueError("safe inherited threshold exceeds empirical oracle bound")
    return {"original_FA": attack / result["original_attack"],
            "original_BFA": real / result["original_bona_fide"],
            "FA_within_constraint": safe, "utility_feasible": safe and useful}


def common_interval(cases: list[dict]) -> dict:
    if not cases or len({case["dataset"] for case in cases}) != len(cases):
        raise ValueError("one case per held-out source for the identical pipeline required")
    identity_keys = ("job", "system", "stage", "seed")
    if any(any(case[key] != cases[0][key] for key in identity_keys) for case in cases):
        raise ValueError("never intersect thresholds from different fitted pipelines")
    if any(not case["oracle"]["empirically_attainable"] for case in cases):
        status, lower, upper = "some_source_individually_unattainable", None, None
    else:
        lower = max(case["oracle"]["threshold_interval"]["lower_exclusive"] for case in cases)
        upper = min(case["oracle"]["threshold_interval"]["upper_inclusive"] for case in cases)
        status = "common_oracle_interval_exists" if lower < upper else "individual_oracles_exist_but_no_common_threshold"
    return {
        **{key: cases[0][key] for key in identity_keys}, "datasets": sorted(case["dataset"] for case in cases),
        "status": status, "lower_exclusive": lower, "upper_inclusive": upper,
        "uses_evaluation_labels": True, "deployable": False,
    }


def summarize(cases: list[dict], common: list[dict]) -> dict:
    result = {}
    for stage in STAGES.values():
        result[stage] = {}
        for system in SYSTEMS:
            selected = [case for case in cases if case["stage"] == stage and case["system"] == system]
            if not selected:
                continue
            domains = {}
            for domain in sorted({case["dataset"] for case in selected}):
                subset = [case for case in selected if case["dataset"] == domain]
                values = [case["oracle"]["oracle_max_BFA"] for case in subset]
                domains[domain] = {
                    "cases": len(subset), "oracle_attainable_cases": sum(case["oracle"]["empirically_attainable"] for case in subset),
                    "original_feasible_cases": sum(case["original"]["utility_feasible"] for case in subset),
                    "oracle_BFA_mean": float(np.mean(values)),
                    "oracle_BFA_min": min(values), "oracle_BFA_max": max(values),
                    "original_FA_mean": float(np.mean([case["original"]["original_FA"] for case in subset])),
                    "original_BFA_mean": float(np.mean([case["original"]["original_BFA"] for case in subset])),
                }
            groups = [item for item in common if item["stage"] == stage and item["system"] == system]
            result[stage][system] = {
                "cases": len(selected), "oracle_attainable_cases": sum(case["oracle"]["empirically_attainable"] for case in selected),
                "original_feasible_cases": sum(case["original"]["utility_feasible"] for case in selected),
                "oracle_attainable_original_infeasible": sum(
                    case["oracle"]["empirically_attainable"] and not case["original"]["utility_feasible"] for case in selected),
                "per_source": domains,
                "common_threshold_status_counts": {
                    status: sum(group["status"] == status for group in groups) for status in (
                        "some_source_individually_unattainable", "common_oracle_interval_exists",
                        "individual_oracles_exist_but_no_common_threshold")},
                "identical_pipeline_groups": len(groups),
            }
    return result


def source_plan() -> dict:
    root = PRIVATE / "source_fusion313_v1"
    plan = frozen.read(root / "execution_plan.json")
    completion = frozen.read(root / "worker_completion.json")
    terminal = frozen.read(root / "terminal.json")
    reconstructed = frozen.read(root / "saved_reconstruction.json")
    public = frozen.read(ROOT / "results/phase1/source-fusion313-closure-v1.json")
    if (terminal["status"] != "complete"
            or terminal["worker_completion_sha256"] != digest(root / "worker_completion.json")
            or terminal["saved_reconstruction_sha256"] != digest(root / "saved_reconstruction.json")
            or reconstructed["worker_completion_sha256"] != digest(root / "worker_completion.json")
            or reconstructed["all_models_predictions_selection_metrics_and_bootstrap_reconstructed"] is not True
            or public["worker_completion_sha256"] != digest(root / "worker_completion.json")
            or public["private_plan_sha256"] != digest(root / "execution_plan.json")
            or completion["plan_sha256"] != digest(root / "execution_plan.json")
            or plan["code_sha256"] != frozen.code_pins()):
        raise ValueError("completed313 provenance, reconstruction and unchanged sealed inventory required")
    paths = {
        str(root / "execution_plan.json"): digest(root / "execution_plan.json"),
        str(root / "worker_completion.json"): digest(root / "worker_completion.json"),
        str(root / "terminal.json"): digest(root / "terminal.json"),
        str(root / "saved_reconstruction.json"): digest(root / "saved_reconstruction.json"),
        str(ROOT / "results/phase1/source-fusion313-closure-v1.json"):
            digest(ROOT / "results/phase1/source-fusion313-closure-v1.json"),
    }
    manifest = PRIVATE / "source_integration295_v1/source_manifest.json"
    expected = plan["inherited_input_sha256"]["source_integration295_v1/source_manifest.json"]
    if digest(manifest) != expected:
        raise ValueError("original source manifest hash changed")
    paths[str(manifest)] = expected
    for key, sha in completion["prediction_artifacts"].items():
        paths[str(root / "predictions" / f"{key}.json")] = sha
    for key, artifact in completion["fit_artifacts"].items():
        paths[str(root / "fits" / f"{key}.json")] = artifact["sha256"]
    return {
        "study": "saved_score_oracle316_v1", "authority": "owner_chat_approval_of_saved_score_diagnostic",
        "protocol": {"alpha": [1, 20], "minimum_BFA": [1, 2], "systems": list(SYSTEMS),
                     "threshold_polarity": "attack_high_accept_strictly_below_threshold",
                     "oracle_uses_evaluation_labels_not_a_policy": True,
                     "new_weights_or_recipes": False, "bootstrap_or_population_guarantees": False},
        "code_sha256": digest(Path(__file__)), "test_sha256": digest(TEST),
        "input_sha256": paths, "limits": LIMITS,
        "expected_prediction_tasks": len(plan["predictions"]),
        "expected_cases": sum(5 + (len(plan["jobs"][task["job"]]["domains"]) > 1)
                              for task in plan["predictions"].values()),
        "new_fits": 0, "new_model_predictions": 0, "encoder_forwards": 0, "new_target_evaluations": 0,
    }


def score_systems(prediction: dict) -> dict[str, tuple[np.ndarray, str]]:
    p = {key: np.asarray(prediction["p"][key], dtype=float) for key in ("dino_reg", "dino_plain", "openclip")}
    scores = {
        "dino_only": (p["dino_reg"], "dino_only"),
        "plain_only": (p["dino_plain"], "two_dino:1"),
        "clip_only": (p["openclip"], "dino_clip:1"),
        "fixed_two_dino": (0.5 * p["dino_reg"] + 0.5 * p["dino_plain"], "two_dino:0.5"),
        "fixed_dino_clip": (0.5 * p["dino_reg"] + 0.5 * p["openclip"], "dino_clip:0.5"),
    }
    if prediction["selected_two_dino"] is not None:
        scores["selected_two_dino"] = (np.asarray(prediction["selected_two_dino"]), "selected_two_dino")
    return scores


def analyze(binding: dict, *, independent_check: bool, guard) -> dict:
    for name, sha in binding["input_sha256"].items():
        guard()
        if digest(Path(name)) != sha:
            raise ValueError(f"saved-input hash drift: {name}")
    root = PRIVATE / "source_fusion313_v1"
    plan = frozen.read(root / "execution_plan.json")
    originals = [row for row in frozen.read(PRIVATE / "source_integration295_v1/source_manifest.json")["rows"]
                 if row["source_use_eligible"]]
    if (len(originals) != plan["originals"] or len({identity(row) for row in originals}) != len(originals)
            or sum(row["model_input_eligible"] for row in originals) != plan["usable"]):
        raise ValueError("exact unique original and usable source populations required")
    fitted = {key: frozen.read(root / "fits" / f"{key}.json")["fitted"]["policies"] for key in plan["jobs"]}
    cases, grouped, arrays = [], defaultdict(list), {}
    for key, task in plan["predictions"].items():
        guard()
        job = plan["jobs"][task["job"]]
        stage = STAGES[len(job["domains"])]
        if (task["pool"] == "g_domain") != (stage == "three_source_g_domain"):
            raise ValueError("one/two-source holdouts and final g_domain must remain separate")
        pred = frozen.read(root / "predictions" / f"{key}.json")
        population = [row for row in originals if row["dataset"] == task["dataset"]
                      and (row["role"] == "g_domain") == (task["pool"] == "g_domain")]
        successful = [row for row in population if row["model_input_eligible"]]
        if pred["ids"] != [identity(row) for row in successful]:
            raise ValueError("exact ordered successful prediction coverage required")
        labels = np.asarray([row["binary_label"] == "attack" for row in successful], dtype=int)
        counts = {label: sum(row["binary_label"] == label for row in population) for label in ("attack", "bona_fide")}
        for system, (scores, policy) in score_systems(pred).items():
            result = oracle(scores, labels, counts["attack"], counts["bona_fide"])
            if independent_check:
                curve_check(result, scores, labels)
            threshold = fitted[task["job"]][policy]["threshold"]
            original = original_rates(scores, labels, threshold, result)
            if original["utility_feasible"] and not result["empirically_attainable"]:
                raise ValueError("original feasible policy cannot have an infeasible oracle")
            case = {
                "id": f"{key}/{system}", "job": task["job"], "dataset": task["dataset"],
                "allowed_sources": job["domains"], "seed": job["seed"], "stage": stage, "system": system,
                "original": original, "oracle": result,
                "oracle_minus_original_BFA": result["oracle_max_BFA"] - original["original_BFA"],
                "original_registered_groups": len({row["group_id"] for row in population}),
            }
            cases.append(case)
            grouped[(task["job"], stage, system)].append(case)
            arrays[case["id"]] = (scores, labels)
    common = [common_interval(group) for group in grouped.values()]
    if independent_check:
        for group, result in zip(grouped.values(), common, strict=True):
            threshold = min(case["oracle"]["oracle_threshold_not_deployable"] for case in group)
            possible = all(original_rates(*arrays[case["id"]], threshold, case["oracle"])["utility_feasible"]
                           for case in group)
            if possible != (result["status"] == "common_oracle_interval_exists"):
                raise ValueError("common-threshold intersection differs from direct empirical evaluation")
    if len(cases) != binding["expected_cases"] or len(plan["predictions"]) != binding["expected_prediction_tasks"]:
        raise ValueError("all declared source/system cases required; no omission or new reference")
    return {"study": binding["study"], "cases": cases, "common_thresholds": common,
            "summary": summarize(cases, common),
            "case_count": len(cases), "prediction_tasks": len(plan["predictions"]),
            "selected_fusion_policies_are_missing_and_not_analyzed": True,
            "uses_evaluation_labels": True, "deployable": False,
            "new_fits": 0, "new_model_predictions": 0, "encoder_forwards": 0, "new_target_evaluations": 0}


def public_result(result: dict) -> dict:
    public = json.loads(json.dumps(result))
    for case in public["cases"]:
        case["oracle"].pop("oracle_threshold_not_deployable")
        case["oracle"].pop("threshold_interval")
    for group in public["common_thresholds"]:
        group.pop("lower_exclusive")
        group.pop("upper_inclusive")
    public["oracle_threshold_values_not_exported"] = True
    return public


def write_checked(path: Path, value: dict, guard) -> None:
    guard()
    payload_bytes = len((json.dumps(value, indent=2, sort_keys=True) + "\n").encode())
    owned = sum(item.stat().st_size for item in OUTPUT.rglob("*") if item.is_file())
    if PUBLIC.exists():
        owned += PUBLIC.stat().st_size
    if owned + 2 * payload_bytes > LIMITS["owned_output_bytes"]:
        raise MemoryError("owned diagnostic output plus atomic temporary copy cap exceeded")
    write_immutable_record(path, value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--execute", action="store_true")
    actions.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    started = time.monotonic()

    def timeout(signum, frame):
        raise TimeoutError("saved-score diagnostic deadline reached")

    old_handler = signal.signal(signal.SIGALRM, timeout)
    signal.setitimer(signal.ITIMER_REAL, LIMITS["wall_seconds"])

    def guard():
        if time.monotonic() - started > LIMITS["wall_seconds"]:
            raise TimeoutError("saved-score diagnostic time cap exceeded")
        if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024 > LIMITS["process_peak_rss_bytes"]:
            raise MemoryError("saved-score diagnostic peak RSS cap exceeded")

    try:
        with threadpool_limits(limits=LIMITS["blas_threads"]):
            binding = source_plan()
            if args.execute:
                write_checked(OUTPUT / "analysis_plan.json", binding, guard)
                write_checked(OUTPUT / "attempt.json", {
                    "analysis_plan_sha256": digest(OUTPUT / "analysis_plan.json"), "automatic_retry": False}, guard)
            else:
                frozen.check_reconstruction(frozen.read(OUTPUT / "analysis_plan.json"), binding)
            result = analyze(binding, independent_check=args.verify, guard=guard)
            guard()
            path = OUTPUT / "result.json"
            if args.execute:
                write_checked(path, result, guard)
            else:
                frozen.check_reconstruction(frozen.read(path), result)
            public = public_result(result)
            public["analysis_plan"] = binding
            public["private_result_sha256"] = digest(path)
            if args.execute:
                write_checked(PUBLIC, public, guard)
            else:
                frozen.check_reconstruction(frozen.read(PUBLIC), public)
                proof = {
                    "result_sha256": digest(path), "public_sha256": digest(PUBLIC),
                    "independent_grouped_curve_and_common_interval_checks": True,
                    "cases": len(result["cases"]), "new_fits": 0, "new_model_predictions": 0}
                proof_path = OUTPUT / "verification.json"
                if proof_path.exists():
                    frozen.check_reconstruction(frozen.read(proof_path), proof)
                else:
                    write_checked(proof_path, proof, guard)
            print(json.dumps({
                "status": "verified" if args.verify else "complete",
                "cases": len(result["cases"]), "prediction_tasks": result["prediction_tasks"],
                "wall_seconds": time.monotonic() - started,
                "process_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                "public_sha256": digest(PUBLIC), "summary": result["summary"]}, indent=2), flush=True)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
