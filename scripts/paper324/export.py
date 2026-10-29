"""Publish aggregate-only evidence from the verified paper323 comparison."""

from __future__ import annotations

import argparse
import csv
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import statistics
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/paper321"))
import runner

PRIVATE = runner.preparation.PRIVATE / "paper_comparison323_v1"
PUBLIC = ROOT / "results/phase1"
STEM = "paper324"
SYSTEMS = runner.study.SYSTEMS
ALPHAS = tuple(str(a) for a in runner.study.ALPHAS)
METRICS = ("FA", "BFA", "AUROC_usable")
TARGETS = ("OULU-NPU", "CASIA-FASD", "MSU-MFSD", "SiW-Mv2")
SEEDS = (20260917, 20260923, 20261001)


def close(a, b):
    return bool(np.isclose(a, b, rtol=1e-12, atol=1e-12))


def validate(completion: dict) -> None:
    contexts = completion["contexts"]
    expected = {(target, seed) for target in TARGETS for seed in SEEDS}
    if len(contexts) != 12 or {(c["target"], c["seed"]) for c in contexts} != expected:
        raise ValueError("exact twelve target/seed contexts required")
    if (completion["fit_starts"] != {"frozen": 24, "specialist": 7, "calibrator": 32}
            or completion["cumulative_fit_starts"] != {"frozen": 39, "specialist": 12, "calibrator": 52}
            or completion["retained_complete_contexts"] != 4
            or completion["new_foundation_encoder_forwards"] != 0
            or completion["oracle_is_diagnostic"] is not True):
        raise ValueError("declared continuation inventory required")
    supports = {}
    for context in contexts:
        analysis = context["analysis"]
        cases = analysis["cases"]
        keys = {(c["system"], c["alpha"]) for c in cases}
        if len(cases) != 12 or keys != {(s, a) for s in SYSTEMS for a in ALPHAS}:
            raise ValueError("all twelve system/alpha cases required per context")
        for case in cases:
            policy, oracle = case["policy"], case["oracle"]
            n_a, n_b = policy["original_attack"], policy["original_bona_fide"]
            if min(n_a, n_b) <= 0 or int(n_a) != n_a or int(n_b) != n_b:
                raise ValueError("positive integer original supports required")
            support = (n_a, n_b, policy["usable_attack"], policy["usable_bona_fide"])
            if supports.setdefault(context["target"], support) != support:
                raise ValueError("target supports must agree across systems and seeds")
            alpha = Fraction(case["alpha"])
            budget = int(n_a)*alpha.numerator//alpha.denominator
            for name, count, denominator in (
                    ("FA", policy["accepted_attack"], n_a),
                    ("BFA", policy["accepted_bona_fide"], n_b)):
                if count != int(count) or not 0 <= count <= denominator or not close(policy[name], count/denominator):
                    raise ValueError("policy integer counts and original-denominator rates disagree")
            safe = policy["accepted_attack"] <= budget
            if policy["FA_within_constraint"] != safe or policy["utility_feasible"] != (safe and policy["BFA"] >= .5):
                raise ValueError("policy feasibility must use integer attack budgets")
            points = analysis["curves"][case["system"]]
            if any(not (0 <= fa <= 1 and 0 <= bfa <= 1) for fa, bfa in points):
                raise ValueError("finite bounded grouped ROC points required")
            curve = np.asarray(points)
            if (not len(points) or not np.isfinite(curve).all()
                    or np.any(np.diff(curve, axis=0) < 0)):
                raise ValueError("monotone finite grouped ROC required")
            feasible = [(fa, bfa) for fa, bfa in points if round(fa*n_a) <= budget]
            if not feasible:
                raise ValueError("zero-acceptance curve point required")
            fa, bfa = feasible[-1]
            if (oracle["attack_error_budget"] != budget
                    or oracle["original_attack"] != n_a or oracle["original_bona_fide"] != n_b
                    or not close(oracle["oracle_FA"], fa) or not close(oracle["oracle_max_BFA"], bfa)
                    or oracle["oracle_accepted_attack"] != round(fa*n_a)
                    or oracle["oracle_accepted_bona_fide"] != round(bfa*n_b)
                    or oracle["empirically_attainable"] != (bfa >= .5)
                    or oracle["uses_evaluation_labels"] is not True):
                raise ValueError("saved oracle must agree with the independent grouped curve")
        for field, systems in (("conditional_intervals", SYSTEMS), ("paired_minus_dino_reg", SYSTEMS[1:])):
            intervals = analysis[field]
            expected_keys = {(s, a, m) for s in systems for a in ALPHAS for m in METRICS}
            if (len(intervals) != len(expected_keys)
                    or {(r["system"], r["alpha"], r["metric"]) for r in intervals} != expected_keys):
                raise ValueError("complete conditional and paired interval inventories required")
            for item in intervals:
                valid, total, interval = item["valid_repetitions"], item["total_repetitions"], item["percentile95"]
                if total != 2000 or not 0 <= valid <= total:
                    raise ValueError("exact 2000-draw valid-replicate accounting required")
                if (interval is None) != (valid < .95*total):
                    raise ValueError("undefined intervals must retain the 95-percent valid-draw rule")
                if interval is not None and (len(interval) != 2 or not np.isfinite(interval).all()
                                             or interval[0] > interval[1]):
                    raise ValueError("ordered finite percentile intervals required")
        expected_unit = ("video_exact_frame_component" if context["target"] == "SiW-Mv2"
                         else "subject_exact_frame_component")
        if analysis["bootstrap_unit"] != expected_unit or analysis["oracle_intervals"] is not None:
            raise ValueError("bootstrap grouping and descriptive-only oracle must remain explicit")
    runner.frozen.check_reconstruction(completion["aggregate"], runner.study.aggregate(contexts))


def summaries(contexts: list[dict]) -> list[dict]:
    records = []
    for alpha in ALPHAS:
        for target in TARGETS:
            for system in SYSTEMS:
                cases = [v for c in contexts if c["target"] == target for v in c["analysis"]["cases"]
                         if v["system"] == system and v["alpha"] == alpha]
                record = {"target": target, "system": system, "alpha": alpha, "training_seeds": 3,
                          "policy_FA_safe": sum(c["policy"]["FA_within_constraint"] for c in cases),
                          "policy_utility_feasible": sum(c["policy"]["utility_feasible"] for c in cases),
                          "oracle_utility_attainable": sum(c["oracle"]["empirically_attainable"] for c in cases)}
                for metric in METRICS:
                    values = [c["policy"][metric] for c in cases]
                    record[f"mean_{metric}"] = statistics.mean(values)
                    record[f"min_seed_{metric}"], record[f"max_seed_{metric}"] = min(values), max(values)
                values = [c["oracle"]["oracle_max_BFA"] for c in cases]
                record["mean_oracle_BFA"] = statistics.mean(values)
                record["min_seed_oracle_BFA"], record["max_seed_oracle_BFA"] = min(values), max(values)
                records.append(record)
    return records


def csv_bytes(rows: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def case_rows(contexts: list[dict]) -> list[dict]:
    rows = []
    for context in contexts:
        for case in context["analysis"]["cases"]:
            rows.append({
                "target": context["target"], "seed": context["seed"], "system": case["system"],
                "alpha": case["alpha"], **case["policy"], **case["oracle"],
                "limiting_sources": ";".join(case["limiting_sources"]),
                "source_attack_budgets": json.dumps(case["source_attack_budgets"], sort_keys=True)})
    return rows


def interval_rows(contexts: list[dict]) -> list[dict]:
    rows = []
    for context in contexts:
        analysis = context["analysis"]
        cases = {(c["system"], c["alpha"]): c["policy"] for c in analysis["cases"]}
        for field in ("conditional_intervals", "paired_minus_dino_reg"):
            for interval in analysis[field]:
                system, alpha, metric = (interval[k] for k in ("system", "alpha", "metric"))
                value = cases[(system, alpha)][metric]
                if field == "paired_minus_dino_reg":
                    value -= cases[("dino_reg", alpha)][metric]
                bounds = interval["percentile95"]
                rows.append({
                    "target": context["target"], "seed": context["seed"], "system": system,
                    "alpha": alpha, "metric": metric, "kind": field, "estimate": value,
                    "lower95": None if bounds is None else bounds[0],
                    "upper95": None if bounds is None else bounds[1],
                    "valid_repetitions": interval["valid_repetitions"], "total_repetitions": 2000,
                    "bootstrap_unit": analysis["bootstrap_unit"]})
    return rows


def tables(contexts: list[dict], summary: list[dict], intervals: list[dict]) -> bytes:
    lines = ["# Paper324 - Complete primary tables", "",
             "All rates and AUROC below are percentages. Alpha=5%; no seed is omitted.",
             "Intervals are conditional paired-cluster percentile95 intervals, not security guarantees.",
             "Oracle BFA uses evaluation labels and has no confidence interval in this package.", "",
             "## Equal-seed descriptive summaries", "",
             "| Target | System | AUROC | Policy FA | Policy BFA | Oracle BFA | FA-safe /3 | Policy utility /3 | Oracle utility /3 |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for row in summary:
        if row["alpha"] == "1/20":
            lines.append(f"| {row['target']} | {row['system']} | {100*row['mean_AUROC_usable']:.2f} | "
                         f"{100*row['mean_FA']:.2f} | {100*row['mean_BFA']:.2f} | "
                         f"{100*row['mean_oracle_BFA']:.2f} | {row['policy_FA_safe']} | "
                         f"{row['policy_utility_feasible']} | {row['oracle_utility_attainable']} |")
    lines += ["", "## All 48 target/system/seed primary rows", "",
              "Usable/original supports are attack,bona-fide respectively.",
              "Acceptance counts use all-original denominators.", "",
              "| Target | Seed | System | Usable / original | Accepted attack,BF | FA [95%] | BFA [95%] | AUROC [95%] | Oracle BFA |",
              "|---|---:|---|---|---|---:|---:|---:|---:|"]
    lookup = {(r["target"], r["seed"], r["system"], r["alpha"], r["metric"], r["kind"]): r for r in intervals}
    def formatted(target, seed, system, metric, value):
        record = lookup[(target, seed, system, "1/20", metric, "conditional_intervals")]
        bounds = ("undefined" if record["lower95"] is None
                  else f"{100*record['lower95']:.2f}, {100*record['upper95']:.2f}")
        return f"{100*value:.2f} [{bounds}]"
    for context in contexts:
        for case in context["analysis"]["cases"]:
            if case["alpha"] != "1/20":
                continue
            p = case["policy"]
            columns = [formatted(context["target"], context["seed"], case["system"], m, p[m]) for m in METRICS]
            lines.append(f"| {context['target']} | {context['seed']} | {case['system']} | "
                         f"{int(p['usable_attack'])},{int(p['usable_bona_fide'])} / "
                         f"{int(p['original_attack'])},{int(p['original_bona_fide'])} | "
                         f"{int(p['accepted_attack'])},{int(p['accepted_bona_fide'])} | "
                         f"{columns[0]} | {columns[1]} | {columns[2]} | "
                         f"{100*case['oracle']['oracle_max_BFA']:.2f} |")
    lines += ["", "## All primary paired differences against DINO-Reg", "",
              "Differences and intervals are percentage points. Policies may violate different",
              "attack-FA constraints: BFA differences alone are not same-security gains.",
              "Seeds share evaluation observations; these intervals are not multiple-testing-adjusted.", "",
              "| Target | Seed | System minus DINO-Reg | Metric | Difference | Conditional 95% | Valid /2000 |",
              "|---|---:|---|---|---:|---:|---:|"]
    for row in intervals:
        if row["alpha"] != "1/20" or row["kind"] != "paired_minus_dino_reg":
            continue
        bounds = ("undefined" if row["lower95"] is None
                  else f"[{100*row['lower95']:.2f}, {100*row['upper95']:.2f}]")
        lines.append(f"| {row['target']} | {row['seed']} | {row['system']} | {row['metric']} | "
                     f"{100*row['estimate']:.2f} | {bounds} | {row['valid_repetitions']} |")
    lines += ["", "All 144 operating cases, including 1%/10% sensitivities:",
              "[cases CSV](paper324-cases-v1.csv). All 756 conditional/paired interval records:",
              "[intervals CSV](paper324-intervals-v1.csv).",
              "Descriptive macro/worst-target results for every seed and alpha:",
              "[closure JSON](paper324-comparison-v1.json).", ""]
    return "\n".join(lines).encode()


def build() -> dict[str, bytes]:
    plan = runner.read(PRIVATE / "execution_plan.json")
    approval = runner.read(PRIVATE / "owner_approval.json")
    verification = runner.read(PRIVATE / "verification.json")
    terminal = runner.read(PRIVATE / "terminal.json")
    completion = runner.read(PRIVATE / "worker_completion.json")
    plan_sha = runner.digest(PRIVATE / "execution_plan.json")
    if (runner.read(PUBLIC / "paper323-execution-plan-v1.json")["execution_plan_sha256"] != plan_sha
            or plan["implementation_sha256"] != runner.code_pins()
            or plan["spec_sha256"] != runner.digest(runner.SPEC)):
        raise ValueError("published seal and exact scientific implementation required")
    if (terminal["status"] != "complete" or terminal["failure"] is not None
            or terminal["automatic_retry"] is not False
            or verification["all12_contexts_reconstructed"] is not True or verification["new_fits"] != 0
            or verification["specialist_checkpoint_predictions_replayed"] is not True
            or verification["worker_sha256"] != runner.digest(PRIVATE / "worker_completion.json")
            or any(r["plan_sha256"] != plan_sha for r in (approval, completion, verification))
            or approval["explicit_owner_approval"] is not True
            or approval["selected_answer"] !=
            "approve_paper323_complete_fixed_recipe_phase_budgets_and_declared_recovery_refits"
            or approval["limits"] != plan["limits"]):
        raise ValueError("complete explicitly approved attempt and bound no-fit reconstruction required")
    validate(completion)
    contexts = completion["contexts"]
    summary, cases, intervals = summaries(contexts), case_rows(contexts), interval_rows(contexts)
    figure = (PRIVATE / "low-fa.svg").read_bytes()
    if hashlib.sha256(figure).hexdigest() != completion["low_FA_plot_sha256"]:
        raise ValueError("saved figure hash changed")
    products = {
        f"{STEM}-cases-v1.csv": csv_bytes(cases),
        f"{STEM}-intervals-v1.csv": csv_bytes(intervals),
        f"{STEM}-target-summary-v1.csv": csv_bytes(summary),
        f"{STEM}-primary-tables-v1.md": tables(contexts, summary, intervals),
        f"{STEM}-low-fa-v1.svg": figure}
    source_hashes = {name: runner.digest(PRIVATE / name) for name in (
        "execution_plan.json", "owner_approval.json", "attempt.json", "worker_completion.json",
        "verification.json", "terminal.json", "low-fa.svg")}
    source_hashes["paper322_terminal.json"] = runner.digest(
        runner.preparation.PRIVATE / "paper_comparison322_v1/terminal.json")
    counts = {}
    for alpha in ALPHAS:
        selected = [c for c in cases if c["alpha"] == alpha]
        counts[alpha] = {
            "cases": len(selected), "policy_FA_safe": sum(c["FA_within_constraint"] for c in selected),
            "policy_utility_feasible": sum(c["utility_feasible"] for c in selected),
            "oracle_utility_attainable": sum(c["empirically_attainable"] for c in selected)}
    public = {
        "version": 1, "study": "paper324_verified_comparison323_export", "status": "complete",
        "source_sha256": source_hashes, "terminal": terminal, "verification": verification,
        "new_fit_starts": completion["fit_starts"], "cumulative_fit_starts": completion["cumulative_fit_starts"],
        "retained_complete_contexts": 4, "specialist_epochs": 600, "specialist_optimizer_steps": 74400,
        "new_foundation_encoder_forwards": 0, "export_fits_or_predictions": 0,
        "original_clock_amended_explicitly": True, "SiW_subject_independence_verified": False,
        "inventory": {"primary_cases": 48, "all_cases": len(cases), "interval_records": len(intervals)},
        "feasibility_counts": counts, "target_system_summary": summary, "aggregate": completion["aggregate"],
        "contexts": [{"target": c["target"], "seed": c["seed"], "analysis": {
            k: v for k, v in c["analysis"].items() if k != "curves"}} for c in contexts],
        "interpretation": {
            "alpha_primary": "1/20", "minimum_BFA": .5, "oracle_uses_evaluation_labels": True,
            "oracle_is_deployable": False, "oracle_confidence_intervals": None,
            "seed_means_are_descriptive_not_pooled": True, "paired_intervals_are_conditional": True,
            "superiority_or_population_security_claim": False},
        "export_sha256": {name: hashlib.sha256(value).hexdigest() for name, value in products.items()},
        "export_code_sha256": runner.digest(Path(__file__))}
    products[f"{STEM}-comparison-v1.json"] = (json.dumps(public, sort_keys=True, indent=2, allow_nan=False)+"\n").encode()
    return products


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    products = build()
    if args.verify:
        for name, value in products.items():
            if (PUBLIC / name).read_bytes() != value:
                raise ValueError(f"public export differs: {name}")
    else:
        if any((PUBLIC / name).exists() for name in products):
            raise FileExistsError("public export is immutable; use --verify")
        for name, value in products.items():
            with (PUBLIC / name).open("xb") as stream:
                stream.write(value)
    print("PAPER324_VERIFIED" if args.verify else "PAPER324_EXPORTED",
          json.dumps({name: hashlib.sha256(value).hexdigest() for name, value in products.items()}), flush=True)


if __name__ == "__main__":
    main()
