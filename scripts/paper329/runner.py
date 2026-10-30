"""Seal, approve or supervise the fixed eight-run independent DINO study."""

from __future__ import annotations

import argparse
import gc
import hashlib
from itertools import zip_longest
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/"src"), str(ROOT/"scripts"), str(ROOT/"scripts/diagnostics"),
                str(ROOT/"scripts/paper321"), str(ROOT/"scripts/paper327")]
import numpy as np
from threadpoolctl import threadpool_limits
from fas.feature_cache import digest
from fas.freeze import write_immutable_record
from fas.source_fitting import calibrate, fit_calibrator, identity
import prepare_paper319 as preparation
import run_source297 as legacy
from paper321 import runner as prior
import study
import assets
from gate import OperatingCounts, assess_expansion
from analysis import ARMS, summarize

OUTPUT = preparation.PRIVATE/"paper_adaptation329_v2"
PUBLIC = ROOT/"results/phase1/paper329-execution-plan-v2.json"
SPEC = ROOT/"docs/paper327/specification.json"
PROBE = ROOT/"results/phase1/dino329-integrated-probe-v2.json"
ANSWER = "approve_paper329_eight_runs_independent_reconstruction_source_only_SiW_limits_72h_no_retry"
CHECKPOINT = Path.home()/".cache/fas/source-pilot295-v1/checkpoints/dino_reg.pth"
CHECKPOINT_SHA = "73182a088cf94833c94b1666d1c99e02fe87e2007bff57b564fb6206e25dba71"
LIMITS = {"wall_seconds": 72*3600, "worker_seconds": 54*3600,
          "context_seconds": 6*3600, "verify_seconds": 12*3600, "analysis_seconds": 6*3600,
          "GPU_bytes": 12*1024**3, "RSS_bytes": 6*1024**3, "output_bytes": 32*1024**3}


def read(path: Path) -> dict:
    return json.loads(path.read_bytes())


def code_pins() -> dict:
    paths = [*Path(__file__).parent.glob("*.py"), ROOT/"scripts/paper327/gate.py",
             ROOT/"scripts/paper327/objective.py", ROOT/"tests/test_paper327.py",
             ROOT/"tests/test_paper329.py", SPEC]
    return {**prior.code_pins(), **{str(path.relative_to(ROOT)): digest(path) for path in paths}}


def runtime() -> dict:
    import cv2
    import importlib.metadata
    result = prior.runtime()
    result.update({name: importlib.metadata.version(name) for name in ("Pillow", "scipy")})
    result["OpenCV"] = cv2.__version__
    result.update({"batch_size": 32, "deterministic_algorithms": False,
                   "randomness": "seeded_model_and_addressed_data_not_bitwise_deterministic",
                   "XFORMERS_DISABLED": True})
    return result


def input_contexts() -> tuple[list[dict], list[dict]]:
    manifest = read(preparation.MANIFEST)
    if digest(preparation.MANIFEST) != preparation.MANIFEST_SHA:
        raise ValueError("accepted manifest changed")
    rows = preparation.active_rows(manifest["rows"])
    partitions = read(preparation.OUTPUT/"partitions.json")
    rebuilt, _ = preparation.build_partitions(manifest["rows"])
    if partitions != rebuilt:
        raise ValueError("accepted source/evaluation partitions changed")
    prior.validate_partitions(rows, partitions)
    contexts = [context for context in partitions["contexts"] if context["seed"] == 20260917]
    if len(contexts) != 4 or {context["target"] for context in contexts} != set(preparation.DOMAINS):
        raise ValueError("four targets at the one initial seed required")
    return rows, contexts


def prepare() -> None:
    begun = time.monotonic()
    rows, contexts = input_contexts()
    files = {}
    for path, expected in ((preparation.MANIFEST, preparation.MANIFEST_SHA),
                           (preparation.OUTPUT/"partitions.json",
                            read(ROOT/"docs/paper319/supplementary-protocol.json")["private_partitions_sha256"]),
                           (CHECKPOINT, CHECKPOINT_SHA), (PROBE, None)):
        prior.bind(files, path, expected)
    receipt = read(PROBE)
    measured = {str(path.relative_to(ROOT)): digest(path) for path in Path(__file__).parent.glob("*.py")}
    if (receipt["implementation_sha256"] != measured or receipt["scientific_training_starts"] != 0
            or receipt["status"] != "complete" or receipt["checkpoint_sha256"] != CHECKPOINT_SHA
            or receipt["objective_sha256"] != digest(ROOT/"scripts/paper327/objective.py")
            or receipt["checkpoint_reconstruction_verified"] is not True):
        raise ValueError("successful integrated probe bound to this implementation required")
    asset_record = assets.verify()
    for name in (*asset_record["files"], "receipt.json"):
        prior.bind(files, assets.DIRECTORY/name)
    for row in rows:
        if time.monotonic()-begun > 1800:
            raise TimeoutError("read-only input binding ceiling")
        if row["detector_status"] == "success":
            crop = row["crops"]["224"]
            prior.bind(files, Path(crop["path"]), crop["sha256"])
        elif row["final_k1_action"] != "non_accept":
            raise ValueError("technical failures must remain nonaccept")
    usable = {identity(row) for row in rows if row["detector_status"] == "success"}
    inventory = [{"target": context["target"], "arm": arm, "seed": context["seed"],
                  "fitting_usable": sum(key in usable for key in context["fitting"]),
                  "validation_usable": sum(key in usable for key in context["validation"]),
                  "maximum_optimizer_steps": ((sum(key in usable for key in context["fitting"])+31)//32)*200}
                 for context in contexts for arm in ARMS]
    plan = {"study": "paper_adaptation329_v2", "scientific_execution_authorized": False,
            "implementation_sha256": code_pins(), "runtime": runtime(), "files": files,
            "limits": LIMITS, "inventory": inventory, "training_starts": 8, "calibrator_fits": 8,
            "integrated_probe_sha256": digest(PROBE), "spec_sha256": digest(SPEC),
            "SiW_subject_independence_verified": False, "actual_image_decodes": 0,
            "upstream_commit": "7764ea0f912e53c92e82eb78a2a1631e92725fc8"}
    write_immutable_record(OUTPUT/"execution_plan.json", plan)
    write_immutable_record(PUBLIC, {
        **{key: value for key, value in plan.items() if key != "files"},
        "execution_plan_sha256": digest(OUTPUT/"execution_plan.json"),
        "bound_file_count": len(files), "preparation_wall_seconds": time.monotonic()-begun})
    print("PAD329_PREPARED", digest(OUTPUT/"execution_plan.json"), flush=True)


def check_plan(guard=lambda: None) -> dict:
    plan = read(OUTPUT/"execution_plan.json")
    if (plan["implementation_sha256"] != code_pins() or plan["runtime"] != runtime()
            or plan["limits"] != LIMITS or plan["training_starts"] != 8 or plan["calibrator_fits"] != 8):
        raise ValueError("sealed code/runtime/recipe/inventory changed")
    for filename, expected in plan["files"].items():
        guard()
        prior.bind({}, Path(filename), expected)
    from fas.environment import verify_source_checkout
    verify_source_checkout(Path.home()/".cache/fas/upstream/dinov2-7764ea0", plan["upstream_commit"])
    return plan


def approve(answer: str | None, plan_sha256: str | None) -> None:
    if answer != ANSWER or plan_sha256 != digest(OUTPUT/"execution_plan.json"):
        raise ValueError("explicit exact-plan owner decision required")
    plan = check_plan()
    if (OUTPUT/"attempt.json").exists():
        raise FileExistsError("no second attempt or approval-clock reset")
    write_immutable_record(OUTPUT/"owner_approval.json", {
        "explicit_owner_approval": True, "answer": answer, "plan_sha256": plan_sha256,
        "limits": plan["limits"], "started_monotonic": time.monotonic(),
        "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip()})


def clock(approval: dict) -> None:
    if (approval["boot_id"] != Path("/proc/sys/kernel/random/boot_id").read_text().strip()
            or time.monotonic()-approval["started_monotonic"] >= LIMITS["wall_seconds"]):
        raise TimeoutError("nonresettable global72h clock")


def authority() -> tuple[dict, dict]:
    approval = read(OUTPUT/"owner_approval.json")
    clock(approval)
    if (approval["explicit_owner_approval"] is not True or approval["answer"] != ANSWER
            or approval["plan_sha256"] != digest(OUTPUT/"execution_plan.json")
            or approval["limits"] != LIMITS):
        raise ValueError("exact explicit owner authority required")
    return check_plan(lambda: clock(approval)), approval


def active(phase: str, started: float, key: str) -> None:
    temporary = OUTPUT/"active.partial"
    temporary.write_text(json.dumps({"phase": phase, "started": started, "key": key}))
    temporary.replace(OUTPUT/"active.json")


def start(kind: str, key: str, plan: dict) -> None:
    allowed = {f"{item['target']}-{item['arm']}" for item in plan["inventory"]}
    if kind not in {"training", "calibrator"} or key not in allowed:
        raise ValueError("undeclared fit start")
    write_immutable_record(OUTPUT/"starts"/f"{kind}-{key}.json", {"kind": kind, "key": key})


def owned_size() -> int:
    return sum(path.stat().st_size for path in OUTPUT.rglob("*") if path.is_file())


def guard_for(approval: dict):
    supervisor = read(OUTPUT/"attempt.json")["supervisor_pid"]
    last = -float("inf")
    def guard():
        nonlocal last
        clock(approval)
        if os.getppid() != supervisor:
            raise RuntimeError("approved supervisor disappeared; orphan worker must stop")
        now = time.monotonic()
        if now-last < 1:
            return
        last = now
        record = read(OUTPUT/"active.json")
        cap = LIMITS["analysis_seconds"] if record["phase"] == "analysis" else (
            LIMITS["verify_seconds"] if record["phase"] == "verify" else LIMITS["context_seconds"])
        if now-record["started"] >= cap:
            raise TimeoutError(f"{record['phase']} phase ceiling")
        if owned_size()+256*1024**2 > LIMITS["output_bytes"]:
            raise MemoryError("owned outputs plus operational reserve ceiling")
        import torch
        if max(torch.cuda.max_memory_reserved(), torch.cuda.max_memory_allocated()) > LIMITS["GPU_bytes"]:
            raise MemoryError("owned GPU ceiling")
    return guard


def verify_paired_traces(paths: list[Path], expected_steps: list[int]) -> None:
    counts = [0, 0]
    with paths[0].open() as first, paths[1].open() as second:
        for pair in zip_longest(first, second):
            if all(line is not None for line in pair) and pair[0] != pair[1]:
                raise ValueError("paired accepted data/augmentation traces differ")
            for index, line in enumerate(pair):
                if line is None:
                    continue
                record = json.loads(line)
                strata = record["post_augmentation_counts"]
                if (len(strata) != 3 or any(len(values) != 2 or min(values) < 1 for values in strata)
                        or sum(map(sum, strata)) != 32 or not 0 <= record["redraws"] < 32):
                    raise ValueError("invalid post-augmentation support/redraw trace")
                counts[index] += 1
    if counts != expected_steps:
        raise ValueError("training trace does not cover every declared optimizer step")


def execute_phase(replay: bool) -> None:
    plan, approval = authority()
    if read(OUTPUT/"attempt.json")["supervisor_pid"] != os.getppid():
        raise ValueError("worker/reconstruction must run under the approved supervisor")
    import torch
    from augmentation import FASAug
    from model import Reference, configure
    from training import fit, predict, validate_state
    torch.cuda.set_per_process_memory_fraction(LIMITS["GPU_bytes"]/torch.cuda.get_device_properties(0).total_memory)
    rows, contexts = input_contexts()
    indexed = {identity(row): row for row in rows}
    all_results = []
    phase_started = time.monotonic()
    guard = guard_for(approval)
    for context in contexts:
        target = context["target"]
        originals = [indexed[key] for key in context["evaluation"]]
        pools = {role: [indexed[key] for key in context[role] if indexed[key]["detector_status"] == "success"]
                 for role in ("fitting", "validation", "calibration", "evaluation")}
        predictions, policies, artifact_hashes, expected_steps = {}, {}, {}, []
        for arm in ARMS:
            key = f"{target}-{arm}"
            active("verify" if replay else "context", phase_started if replay else time.monotonic(), key)
            folder = OUTPUT/"contexts"/key
            folder.mkdir(parents=True, exist_ok=True)
            configure(context["seed"])
            model = Reference(initialize=not replay).cuda()
            checkpoint = folder/"model.pth"
            tail = arm == ARMS[1]
            if replay:
                state = torch.load(checkpoint, map_location="cpu", weights_only=True)
                model.load_state_dict(state["state_dict"], strict=True)
            else:
                start("training", key, plan)
                state = fit(model, pools["fitting"], pools["validation"], lambda row: legacy.bound_rgb(row, 224),
                            FASAug(), context["seed"], tail, "cuda", guard, folder/"batches.jsonl")
                with checkpoint.open("xb") as stream:
                    torch.save(state, stream)
            validate_state(state, len(pools["fitting"]), context["seed"], tail)
            expected_steps.append(state["optimizer_steps"])
            if hashlib.sha256((folder/"batches.jsonl").read_bytes()).hexdigest() != state["trace_sha256"]:
                raise ValueError("training trace changed")
            saved = read(folder/"operating.json") if replay else None
            logits = {role: predict(model, pools[role], lambda row: legacy.bound_rgb(row, 224), "cuda", guard)
                      for role in ("calibration", "evaluation")}
            if replay:
                calibrator = saved["calibrator"]
            else:
                start("calibrator", key, plan)
                calibrator = fit_calibrator(logits["calibration"],
                    np.asarray([row["binary_label"] == "attack" for row in pools["calibration"]], dtype=int),
                    [row["dataset"] for row in pools["calibration"]], guard)
            scores = {role: calibrate(calibrator, value) for role, value in logits.items()}
            policy = {str(alpha): study.threshold(scores["calibration"], pools["calibration"], alpha)
                      for alpha in study.ALPHAS}
            record = {"calibrator": calibrator, "policies": policy,
                      "prediction": scores["evaluation"].tolist(),
                      "usable_ids": [identity(row) for row in pools["evaluation"]],
                      "checkpoint_sha256": digest(checkpoint), "selected_epoch": state["selected_epoch"],
                      "optimizer_steps": state["optimizer_steps"]}
            if replay:
                prior.frozen.check_reconstruction(saved, record)
            else:
                write_immutable_record(folder/"operating.json", record)
            predictions[arm], policies[arm] = record["prediction"], policy
            artifact_hashes[arm] = {"checkpoint": digest(checkpoint),
                                    "operating": digest(folder/"operating.json"),
                                    "batch_trace": digest(folder/"batches.jsonl")}
            del model, state
            gc.collect()
            torch.cuda.empty_cache()
        # Compare accepted batch identities at every common step, including redraws and PDA.
        traces = [OUTPUT/"contexts"/f"{target}-{arm}"/"batches.jsonl" for arm in ARMS]
        verify_paired_traces(traces, expected_steps)
        all_results.append({"target": target, "seed": context["seed"],
                            "prediction": predictions, "policies": policies, "artifacts": artifact_hashes})
    active("verify" if replay else "analysis", phase_started if replay else time.monotonic(), "all-targets")
    for result, context in zip(all_results, contexts, strict=True):
        result["analysis"] = summarize(result["prediction"], [indexed[key] for key in context["evaluation"]],
                                       result["policies"], guard)
    closure = {"contexts": all_results, "scientific_training_starts": 8, "calibrator_fits": 8}
    if replay:
        prior.frozen.check_reconstruction(read(OUTPUT/"completion.json"), closure)
        pairs = {}
        for result in all_results:
            points = {case["system"]: case["policy"] for case in result["analysis"]["cases"]
                      if case["alpha"] == "1/20"}
            pairs[result["target"]] = tuple(OperatingCounts(
                *[int(points[arm][name]) for name in ("original_attack", "original_bona_fide",
                                                     "accepted_attack", "accepted_bona_fide")]) for arm in ARMS)
        starts = list((OUTPUT/"starts").glob("*.json"))
        if len(starts) != 16:
            raise ValueError("exact eight training and eight calibrator starts required")
        write_immutable_record(OUTPUT/"verification.json", {
            "completion_sha256": digest(OUTPUT/"completion.json"), "new_fits": 0,
            "contexts": 8, "expansion_gate": assess_expansion(pairs)})
    else:
        write_immutable_record(OUTPUT/"completion.json", closure)


def supervise() -> int:
    plan, approval = authority()
    write_immutable_record(OUTPUT/"attempt.json", {"supervisor_pid": os.getpid(), "automatic_retry": False})
    child, failure, peak = None, None, 0
    env = {**os.environ, "XFORMERS_DISABLED": "1", "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
           "OPENBLAS_NUM_THREADS": "2", "OMP_NUM_THREADS": "2", "MKL_NUM_THREADS": "2",
           "HF_HUB_OFFLINE": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        for phase in ("worker", "verify"):
            started = time.monotonic()
            (OUTPUT/"active.json").unlink(missing_ok=True)
            with (OUTPUT/f"{phase}.log").open("x") as stream:
                child = subprocess.Popen([sys.executable, str(Path(__file__)), f"--{phase}"],
                    stdout=stream, stderr=subprocess.STDOUT, env=env, start_new_session=True)
                while child.poll() is None:
                    clock(approval)
                    if time.monotonic()-started >= LIMITS[f"{phase}_seconds"]:
                        raise TimeoutError(f"{phase} total phase ceiling")
                    marker = OUTPUT/"active.json"
                    if marker.exists():
                        record = read(marker)
                        cap = LIMITS["analysis_seconds"] if record["phase"] == "analysis" else (
                            LIMITS["verify_seconds"] if record["phase"] == "verify" else LIMITS["context_seconds"])
                        if time.monotonic()-record["started"] >= cap:
                            raise TimeoutError("independently supervised active phase ceiling")
                    own = next(int(line.split()[1])*1024 for line in Path("/proc/self/status").read_text().splitlines()
                               if line.startswith("VmRSS:"))
                    peak = max(peak, own+legacy.pilot.group_rss(child.pid))
                    if peak > LIMITS["RSS_bytes"] or owned_size()+256*1024**2 > LIMITS["output_bytes"]:
                        raise MemoryError("independently supervised RSS/output ceiling")
                    time.sleep(.5)
                if child.returncode:
                    raise RuntimeError(f"{phase} exit{child.returncode}; see retained log, no retry")
        if not (OUTPUT/"verification.json").exists():
            raise RuntimeError("no independent reconstruction")
        clock(approval)
    except (OSError, ValueError, RuntimeError, TimeoutError, MemoryError) as exc:
        failure = f"{type(exc).__name__}: {exc}"
        print("PAD329_STOP", failure, file=sys.stderr, flush=True)
    finally:
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
    write_immutable_record(OUTPUT/"terminal.json", {
        "status": "complete" if failure is None else "stopped_no_retry", "failure": failure,
        "sampled_peak_combined_RSS": peak, "owned_output_bytes": owned_size(),
        "wall_seconds": time.monotonic()-approval["started_monotonic"], "automatic_retry": False,
        "verification_sha256": digest(OUTPUT/"verification.json") if failure is None else None})
    return int(failure is not None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    for action in ("prepare", "check", "approve", "execute", "worker", "verify"):
        group.add_argument(f"--{action}", action="store_true")
    parser.add_argument("--answer")
    parser.add_argument("--plan-sha256")
    args = parser.parse_args()
    with threadpool_limits(limits=2):
        if args.prepare:
            prepare()
        elif args.check:
            check_plan()
            print("PAD329_PLAN_VERIFIED")
        elif args.approve:
            approve(args.answer, args.plan_sha256)
        elif args.execute:
            return supervise()
        else:
            execute_phase(args.verify)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
