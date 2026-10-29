"""Explicit paper323 continuation of the stopped paper322 comparison."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import time
import types

import numpy as np
from threadpoolctl import threadpool_limits

import runner

PARENT = runner.OUTPUT
PARENT_COMMIT = "72b98295c3016348c53b208c25e39723c08fbe6c"
OUTPUT = runner.preparation.PRIVATE / "paper_comparison323_v1"
PUBLIC = runner.ROOT / "results/phase1/paper323-execution-plan-v1.json"
ANSWER = "approve_paper323_complete_fixed_recipe_phase_budgets_and_declared_recovery_refits"


def install() -> None:
    runner.OUTPUT = OUTPUT
    runner.PUBLIC = PUBLIC
    runner.ANSWER = ANSWER
    runner.ENTRYPOINT = Path(__file__)
    runner.RETAINED_OUTPUTS = (PARENT,)


def contexts_and_rows() -> tuple[list[dict], dict]:
    contexts = runner.read(runner.preparation.OUTPUT / "partitions.json")["contexts"]
    rows = runner.preparation.active_rows(runner.read(runner.preparation.MANIFEST)["rows"])
    return contexts, {runner.identity(row): row for row in rows}


def recovery_inventory(contexts: list[dict], indexed: dict, files: dict) -> dict:
    import torch
    complete, checkpoints = {}, {}
    expected_starts = set()
    existing = {p.name for p in (PARENT / "contexts").iterdir() if p.is_dir()}
    for context in contexts:
        key = f"{context['target']}-{context['seed']}"
        folder = PARENT / "contexts" / key
        if not folder.exists():
            continue
        expected_starts.update(f"frozen-{key}-{branch}.json" for branch in runner.BRANCHES[:3])
        expected_starts.update(f"calibrator-{key}-{branch}.json" for branch in runner.BRANCHES)
        expected_starts.add(f"specialist-{key}.json")
        checkpoint = folder / "specialist.pth"
        runner.bind(files, checkpoint)
        state = torch.load(checkpoint, map_location="cpu", weights_only=True)
        count = sum(indexed[k]["detector_status"] == "success" for k in context["fitting"])
        if (len(state["history"]) != 50 or not np.isfinite(state["history"]).all()
                or state["seed"] != context["seed"] or state["optimizer_steps"] != ((count+15)//16)*50
                or state["selected_epoch"] != int(np.argmin(state["history"]))+1
                or state["validation_loss"] != min(state["history"])
                or any(not torch.isfinite(value).all() for value in state["state_dict"].values())):
            raise ValueError(f"incomplete or inconsistent retained checkpoint: {key}")
        model_path, result_path = folder / "models.json", folder / "prediction_analysis.json"
        if model_path.exists() != result_path.exists():
            raise ValueError("partial retained model/result pair requires explicit disposition")
        if model_path.exists():
            runner.bind(files, model_path)
            runner.bind(files, result_path)
            model, result = runner.read(model_path), runner.read(result_path)
            if (model["specialist_sha256"] != files[str(checkpoint)]
                    or model["specialist_selected_epoch"] != state["selected_epoch"]
                    or model["specialist_optimizer_steps"] != state["optimizer_steps"]
                    or result["target"] != context["target"] or result["seed"] != context["seed"]
                    or result["usable_ids"] != [k for k in context["evaluation"]
                                               if indexed[k]["detector_status"] == "success"]):
                raise ValueError("retained model/result identity or checkpoint commitment drift")
            complete[key] = str(folder)
        else:
            checkpoints[key] = str(checkpoint)
    if (len(complete) != 4 or len(checkpoints) != 1
            or set(complete) | set(checkpoints) != existing
            or set(checkpoints) != {"CASIA-FASD-20260923"}):
        raise ValueError("expected exactly four complete contexts and one checkpoint-only context")
    starts = list((PARENT / "starts").glob("*.json"))
    if {p.name for p in starts} != expected_starts:
        raise ValueError("retained fit-start inventory differs from completed and checkpoint-only work")
    for path in starts:
        runner.bind(files, path)
        record = runner.read(path)
        if path.name != f"{record['kind']}-{record['key']}.json":
            raise ValueError("retained fit-start identity differs")
    return {"complete_contexts": complete, "checkpoint_contexts": checkpoints,
            "new_fit_starts": {"frozen": 24, "specialist": 7, "calibrator": 32},
            "prior_fit_starts": {"frozen": 15, "specialist": 5, "calibrator": 20},
            "recovery_refits": {"frozen": 3, "specialist": 0, "calibrator": 4},
            "cumulative_fit_starts": {"frozen": 39, "specialist": 12, "calibrator": 52}}


def benchmark() -> None:
    contexts, indexed = contexts_and_rows()
    source = subprocess.check_output(
        ["git", "show", f"{PARENT_COMMIT}:scripts/paper321/study.py"], cwd=runner.ROOT)
    old = types.ModuleType("paper322_reference")
    exec(compile(source, "paper322_reference", "exec"), old.__dict__)
    records = []
    for context in contexts:
        folder = PARENT / "contexts" / f"{context['target']}-{context['seed']}"
        if not (folder / "models.json").exists():
            continue
        model, result = runner.read(folder / "models.json"), runner.read(folder / "prediction_analysis.json")
        args = (result["prediction"], [indexed[k] for k in context["evaluation"]], model["policies"],
                runner.oracle316.oracle, lambda: None)
        started = time.monotonic()
        reference = old.summarize_context(*args, repetitions=20)
        baseline = time.monotonic()-started
        started = time.monotonic()
        optimized = runner.study.summarize_context(*args, repetitions=20)
        elapsed = time.monotonic()-started
        runner.frozen.check_reconstruction(reference, optimized)
        started = time.monotonic()
        full = runner.study.summarize_context(*args)
        full_seconds = time.monotonic()-started
        runner.frozen.check_reconstruction(result["analysis"], full)
        record = {"context": folder.name, "reference20_seconds": baseline, "optimized20_seconds": elapsed,
                  "speedup20": baseline/elapsed, "optimized2000_seconds": full_seconds,
                  "all_saved2000_output_fields_equivalent_rtol_atol_1e_12": True}
        records.append(record)
        print("PAPER323_ANALYSIS_BENCHMARK", record, flush=True)
    if len(records) != 4:
        raise ValueError("all four retained analyses must be checked")
    runner.write_immutable_record(OUTPUT / "analysis_benchmark.json", {
        "reference_commit": PARENT_COMMIT, "records": records, "new_fits": 0, "new_image_forwards": 0})


def prepare() -> None:
    started = time.monotonic()
    def guard():
        if time.monotonic()-started > 1800:
            raise TimeoutError("30-minute read-only continuation preparation ceiling")
    parent = runner.read(PARENT / "execution_plan.json")
    parent_public = runner.ROOT / "results/phase1/paper322-execution-plan-v1.json"
    if runner.digest(PARENT / "execution_plan.json") != runner.read(parent_public)["execution_plan_sha256"]:
        raise ValueError("parent plan differs from its published seal")
    if parent["runtime"] != runner.runtime() or parent["spec_sha256"] != runner.digest(runner.SPEC):
        raise ValueError("original runtime and scientific recipe must remain unchanged")
    for filename, sha in parent["implementation_sha256"].items():
        path = runner.ROOT / filename
        if runner.digest(path) != sha:
            original = subprocess.check_output(["git", "show", f"{PARENT_COMMIT}:{filename}"], cwd=runner.ROOT)
            if hashlib.sha256(original).hexdigest() != sha:
                raise ValueError(f"parent implementation cannot be reconstructed: {filename}")
    files = dict(parent["files"])
    runner.bind(files, parent_public)
    for filename, sha in list(files.items()):
        guard()
        runner.bind(files, Path(filename), sha)
    for name in ("execution_plan.json", "owner_approval.json", "terminal.json", "worker.log", "attempt.json"):
        runner.bind(files, PARENT / name)
    terminal = runner.read(PARENT / "terminal.json")
    if (terminal["status"] != "stopped_no_retry"
            or "context ceiling" not in terminal["failure"]):
        raise ValueError("continuation applies only to the retained stopped context-timeout attempt")
    attempt = runner.read(PARENT / "attempt.json")
    old_approval = runner.read(PARENT / "owner_approval.json")
    parent_sha = runner.digest(PARENT / "execution_plan.json")
    if (attempt["plan_sha256"] != parent_sha or old_approval["plan_sha256"] != parent_sha
            or old_approval["explicit_owner_approval"] is not True
            or old_approval["selected_answer"] != "approve_paper322_initialization_fix_same_original_deadline"
            or old_approval["limits"] != parent["limits"]):
        raise ValueError("prior attempt must bind its original explicit approval and sealed limits")
    if Path(f"/proc/{attempt['supervisor_pid']}").exists():
        raise ValueError("prior supervisor PID still exists; inspect before continuing")
    runner.bind(files, OUTPUT / "analysis_benchmark.json")
    proof = runner.read(OUTPUT / "analysis_benchmark.json")
    if len(proof["records"]) != 4 or not all(
            r["all_saved2000_output_fields_equivalent_rtol_atol_1e_12"]
            and r["optimized2000_seconds"] < 600 for r in proof["records"]):
        raise ValueError("four equivalent full analyses within the new analysis budget required")
    contexts, indexed = contexts_and_rows()
    runner.validate_partitions(list(indexed.values()), {"contexts": contexts})
    recovery = recovery_inventory(contexts, indexed, files)
    ids, _ = runner.load_features(list(indexed.values()), {}, guard)
    if len(ids) != 7474:
        raise ValueError("original full cache population required")
    limits = {**parent["limits"], "wall_seconds_total": 24*3600, "work_cutoff_seconds": 22*3600,
              "phase_seconds": {"heads": 600, "specialist": 5400, "prediction": 1800, "analysis": 600}}
    del limits["specialist_seconds_per_context"]
    counts = {**parent["counts"], "frozen_head_fit_starts_max": 39, "frozen_head_epochs_max": 7800,
              "calibrator_fit_starts_max": 52}
    plan = {**parent, "study": "paper_comparison323_v1", "files": files, "limits": limits, "counts": counts,
            "implementation_sha256": runner.code_pins(), "continuation": recovery,
            "parent_commit": PARENT_COMMIT, "parent_plan_sha256": runner.digest(PARENT / "execution_plan.json"),
            "clock_amendment": "new_explicit_approval_not_a_reset_of_old321_or322",
            "analysis_benchmark": proof}
    runner.write_immutable_record(OUTPUT / "execution_plan.json", plan)
    public = {key: value for key, value in plan.items()
              if key not in {"files", "initialization_reuse", "continuation", "prior_attempt"}}
    public["initialization_reuse"] = {k: v for k, v in plan["initialization_reuse"].items() if k != "path"}
    public["continuation"] = {k: v for k, v in recovery.items() if k not in {"complete_contexts", "checkpoint_contexts"}}
    public["continuation"]["complete_contexts"] = sorted(recovery["complete_contexts"])
    public["continuation"]["checkpoint_contexts"] = sorted(recovery["checkpoint_contexts"])
    public["execution_plan_sha256"] = runner.digest(OUTPUT / "execution_plan.json")
    public["preparation_wall_seconds"] = time.monotonic()-started
    runner.write_immutable_record(PUBLIC, public)
    print("PAPER323_SEALED", public["execution_plan_sha256"], flush=True)


def approve(answer: str | None) -> None:
    if answer != ANSWER:
        raise ValueError("explicit continuation approval required")
    plan = runner.check_plan()
    runner.write_immutable_record(OUTPUT / "owner_approval.json", {
        "explicit_owner_approval": True, "selected_answer": ANSWER,
        "plan_sha256": runner.digest(OUTPUT / "execution_plan.json"), "limits": plan["limits"],
        "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
        "started_unix": time.time(), "started_monotonic": time.monotonic(), "automatic_retry": False})


def main() -> int:
    install()
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    for action in ("benchmark", "prepare", "approve", "execute", "worker", "verify"):
        group.add_argument(f"--{action}", action="store_true")
    parser.add_argument("--answer")
    args = parser.parse_args()
    with threadpool_limits(limits=2):
        if args.benchmark:
            benchmark()
        elif args.prepare:
            prepare()
        elif args.approve:
            approve(args.answer)
        elif args.execute:
            return runner.supervise()
        else:
            runner.execute_phase(replay=args.verify)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
