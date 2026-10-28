"""Seal or execute one explicitly approved fixed paper319 comparison."""

from __future__ import annotations

import argparse
import gc
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/diagnostics"))
import numpy as np
from threadpoolctl import threadpool_limits
from fas.feature_cache import cache_key, digest, load_shard
from fas.freeze import write_immutable_record
from fas.frozen_features import normalize_rgb
from fas.source_fitting import calibrate, fit_calibrator, fit_head, head_logits, identity
import prepare_paper319 as preparation
import oracle316
import run_source297 as legacy
import run_fusion313 as frozen
import study

SPEC = ROOT / "docs/paper319/supplementary-protocol.json"
OUTPUT = preparation.PRIVATE / "paper_comparison321_v1"
PUBLIC = ROOT / "results/phase1/paper321-execution-plan-v1.json"
ANSWER = "approve_paper321_bounded_comparison_with_SiW_video_groups"
BRANCHES = ("dino_reg", "dino_plain", "openclip", "matched_deeppixbis")


def read(path: Path) -> dict:
    return json.loads(path.read_bytes())


def runtime() -> dict:
    import importlib.metadata
    result = legacy.runtime()
    result["torchvision"] = importlib.metadata.version("torchvision")
    if result["device"] is None:
        raise RuntimeError("CUDA required for the fixed specialist; no CPU scientific fallback")
    return result


def code_pins() -> dict:
    paths = [*Path(__file__).parent.glob("*"), ROOT / "tests/test_paper321.py", SPEC,
             ROOT / "docs/321-executable-comparison-and-review320-response.md",
             ROOT / "scripts/diagnostics/prepare_paper319.py", ROOT / "tests/test_paper319.py"]
    return {**frozen.code_pins(), **{str(p.relative_to(ROOT)): digest(p) for p in paths if p.is_file()}}


def bind(files: dict, path: Path, expected: str | None = None) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"regular bound file required: {path.name}")
    sha = digest(path)
    if expected is not None and sha != expected:
        raise ValueError(f"input byte commitment changed: {path.name}")
    files[str(path)] = sha


def load_features(rows: list[dict], files: dict, guard) -> tuple[list[str], dict]:
    pilot = read(legacy.pilot.CONFIG)
    previous = read(preparation.PRIVATE / "source_run297_v1/extraction.json")
    collected = {name: {} for name in BRANCHES[:3]}
    for directory, expected in preparation.RECEIPTS.items():
        path = preparation.PRIVATE / directory / "extraction.json"
        bind(files, path, expected)
        receipt = read(path)
        models = receipt.get("models", receipt)
        if directory == "source_run297_v1":
            ids = models["dino_reg"]["ids"]
        elif directory == "source_run299_v1":
            ids = [key for key in receipt["ids"] if key.startswith("OULU-NPU/")]
        else:
            ids = [key for key in receipt["success_ids"] if key.startswith("SiW-Mv2/")]
        indexed = {identity(row): row for row in rows}
        for name in collected:
            guard()
            model = models[name]
            contract = model["contract"]
            if (contract["runtime"] != legacy.runtime()
                    or contract["feature_contract_sha256"] != digest(ROOT / "src/fas/frozen_features.py")
                    or contract["resolution"] != pilot["models"][name]["resolution"]):
                raise ValueError("exact original cache runtime, feature contract and resolution required")
            checkpoint_sha = previous[name]["checkpoint_sha256"]
            bind(files, legacy.pilot.NATIVE / "checkpoints" / f"{name}.pth", checkpoint_sha)
            keys = [cache_key(legacy.base_key(indexed[key], name, pilot, checkpoint_sha), contract) for key in ids]
            if keys != model.get("feature_keys", model.get("keys")) or len(set(keys)) != len(keys):
                raise ValueError("complete image/checkpoint/recipe cache-key join changed")
            parts, offset = [], 0
            for shard in model["shards"]:
                guard()
                path = Path(shard["path"])
                bind(files, path, shard["sha256"])
                count = shard["count"]
                parts.append(load_shard(path, keys[offset:offset+count], model["shape"][1]))
                offset += count
            if offset != len(ids):
                raise ValueError("cache coverage mismatch")
            values = np.concatenate(parts)
            for key, value in zip(ids, values, strict=True):
                if key in collected[name]:
                    raise ValueError("duplicate cached image identity")
                collected[name][key] = value
    ids = sorted(identity(row) for row in rows if row["detector_status"] == "success")
    if any(set(values) != set(ids) for values in collected.values()):
        raise ValueError("exact7474-image cache coverage required")
    features = {name: np.asarray([values[key] for key in ids]) for name, values in collected.items()}
    return ids, features


def validate_partitions(rows: list[dict], partitions: dict) -> None:
    indexed = {identity(row): row for row in rows}
    for context in partitions["contexts"]:
        pools = [[indexed[key] for key in context[role]]
                 for role in ("fitting", "validation", "calibration", "evaluation")]
        study.isolation(pools)
        for pool in pools[:3]:
            if any(row["dataset"] == context["target"] or row["official_split"] == "test" for row in pool):
                raise ValueError("target or official source test entered a source fitting role")
        expected = {identity(row) for row in rows if row["dataset"] == context["target"]
                    and row["official_split"] == "test"}
        if set(context["evaluation"]) != expected:
            raise ValueError("exact declared target-test intersection required")


def prepare() -> None:
    started = time.monotonic()
    def guard():
        if time.monotonic() - started > 1800:
            raise TimeoutError("30-minute read-only preparation ceiling")
    files = {}
    bind(files, preparation.MANIFEST, preparation.MANIFEST_SHA)
    manifest = read(preparation.MANIFEST)
    rows = preparation.active_rows(manifest["rows"])
    previous = read(preparation.PUBLIC)
    partitions_path = preparation.OUTPUT / "partitions.json"
    bind(files, partitions_path, previous["private_partitions_sha256"])
    bind(files, preparation.PUBLIC)
    partitions = read(partitions_path)
    reconstructed, _ = preparation.build_partitions(manifest["rows"])
    if partitions != reconstructed:
        raise ValueError("exact accepted319 populations required")
    validate_partitions(rows, partitions)
    for row in rows:
        guard()
        if row["detector_status"] == "success":
            for crop in row["crops"].values():
                bind(files, Path(crop["path"]), crop["sha256"])
        elif row["final_k1_action"] != "non_accept":
            raise ValueError("failures must remain nonacceptance")
    ids, features = load_features(rows, files, guard)
    if len(ids) != 7474:
        raise ValueError("fixed usable-image population required")
    config = read(SPEC)
    usable = set(ids)
    fitting = sum(len([key for key in c["fitting"] if key in usable]) for c in partitions["contexts"])
    validation = sum(len([key for key in c["validation"] if key in usable]) for c in partitions["contexts"])
    inference = sum(len([key for role in ("calibration", "evaluation") for key in c[role] if key in usable])
                    for c in partitions["contexts"])
    optimizer_steps = sum(
        ((sum(key in usable for key in context["fitting"]) + 15) // 16) * 50
        for context in partitions["contexts"])
    if optimizer_steps != 74400 or len(partitions["contexts"]) != 12:
        raise ValueError("fixed12-context/74400-step scientific inventory required")
    plan = {
        "version": 1, "study": "paper_comparison321_v1", "spec_sha256": digest(SPEC),
        "files": files, "implementation_sha256": code_pins(), "runtime": runtime(),
        "limits": config["proposed_limits"], "counts": config["inventory"],
        "actual_source_population_checked": True, "known_subject_isolation_checked": True,
        "SiW_subject_independence_verified": False, "scientific_execution_authorized": False,
        "feature_arrays": {name: {"shape": list(x.shape), "dtype": str(x.dtype)}
                           for name, x in features.items()},
        "specialist_optimizer_steps": optimizer_steps, "specialist_image_forwards": {
            "fitting_draws": fitting * 50, "validation": validation * 50,
            "calibration_plus_target_per_prediction_pass": inference,
            "saved_checkpoint_reconstruction_passes": 1},
        "calibrator_initialization": {"theta": float(np.log(np.expm1(1-1e-6))), "intercept": 0.0},
        "specialist_randomness": "model_seed_before_construction_sampler_seed_plus1_flip_seed_plus2",
        "initialization_acquisition": {"url": config["specialist"]["initialization_url"],
                                      "sha256_prefix": "8d451a50", "max_bytes": 268435456},
    }
    write_immutable_record(OUTPUT / "execution_plan.json", plan)
    write_immutable_record(PUBLIC, {
        key: value for key, value in {**plan, "execution_plan_sha256": digest(OUTPUT / "execution_plan.json"),
                                     "bound_file_count": len(files), "preparation_wall_seconds": time.monotonic()-started}.items()
        if key != "files"})
    print("PAPER321_SEALED", digest(OUTPUT / "execution_plan.json"), flush=True)


def check_plan(guard=lambda: None) -> dict:
    guard()
    plan = read(OUTPUT / "execution_plan.json")
    if plan["implementation_sha256"] != code_pins() or plan["spec_sha256"] != digest(SPEC):
        raise ValueError("sealed implementation or specification changed")
    if plan["runtime"] != runtime():
        raise ValueError("sealed runtime changed")
    for filename, sha in plan["files"].items():
        guard()
        bind({}, Path(filename), sha)
    guard()
    return plan


def approve(answer: str | None) -> None:
    if answer != ANSWER:
        raise ValueError("one explicit integrated owner decision including SiW limitation required")
    plan = check_plan()
    now = time.time()
    write_immutable_record(OUTPUT / "owner_approval.json", {
        "explicit_owner_approval": True, "selected_answer": answer,
        "plan_sha256": digest(OUTPUT / "execution_plan.json"), "started_unix": now,
        "started_monotonic": time.monotonic(), "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
        "limits": plan["limits"], "automatic_retry": False})


def clock(approval: dict, *, final: bool = False, context_started: float | None = None) -> None:
    limits = approval["limits"]
    if (approval["boot_id"] != Path("/proc/sys/kernel/random/boot_id").read_text().strip()
            or time.monotonic() - approval["started_monotonic"] >= limits[
                "wall_seconds_total" if final else "work_cutoff_seconds"]):
        raise TimeoutError("original nonresettable paper321 deadline")
    if context_started is not None and time.monotonic() - context_started >= limits["specialist_seconds_per_context"]:
        raise TimeoutError("fixed40-minute context ceiling; no shortened successful recipe")


def authority() -> tuple[dict, dict]:
    approval = read(OUTPUT / "owner_approval.json")
    clock(approval, final=True)
    plan = check_plan(lambda: clock(approval, final=True))
    if (approval["explicit_owner_approval"] is not True or approval["selected_answer"] != ANSWER
            or approval["plan_sha256"] != digest(OUTPUT / "execution_plan.json")
            or approval["limits"] != plan["limits"] or approval["automatic_retry"] is not False):
        raise ValueError("exact fresh paper321 authority required")
    clock(approval, final=True)
    return plan, approval


def owned_size() -> int:
    return sum(path.stat().st_size for path in OUTPUT.rglob("*") if path.is_file())


def resources(approval: dict, *, final: bool = False, context_started=None, cuda: bool = False) -> None:
    clock(approval, final=final, context_started=context_started)
    if owned_size() + 268435456 > approval["limits"]["owned_new_and_temporary_output_bytes"]:
        raise MemoryError("owned artifacts cap, including256MiB operational/terminal reserve")
    if cuda:
        import torch
        if max(torch.cuda.max_memory_allocated(), torch.cuda.max_memory_reserved()) > approval["limits"]["CUDA_allocated_and_reserved_each_bytes"]:
            raise MemoryError("own CUDA allocation/reservation cap")


def acquire(plan: dict, guard) -> Path:
    spec = plan["initialization_acquisition"]
    path = OUTPUT / "initialization.pth"
    temporary = OUTPUT / "initialization.partial"
    if path.exists() or temporary.exists():
        raise FileExistsError("initialization acquisition is single-attempt, not an automatic resume")
    count = 0
    with urllib.request.urlopen(spec["url"], timeout=30) as response, temporary.open("xb") as stream:
        length = response.headers.get("Content-Length")
        if length is None or not length.isdecimal() or int(length) <= 0:
            raise ValueError("positive initialization Content-Length required for bounded acquisition")
        if int(length) > spec["max_bytes"]:
            raise MemoryError("initialization download allowance exceeded")
        while count < int(length):
            guard()
            chunk = response.read(min(1024*1024, int(length)-count))
            if not chunk:
                raise ValueError("truncated initialization download")
            count += len(chunk)
            stream.write(chunk)
    sha = digest(temporary)
    if not sha.startswith(spec["sha256_prefix"]):
        raise ValueError("torchvision upstream initialization hash prefix mismatch")
    os.link(temporary, path)
    temporary.unlink()
    write_immutable_record(OUTPUT / "initialization.json", {
        "url": spec["url"], "sha256": sha, "bytes": count,
        "upstream_full_sha256_claimed": False})
    return path


def image_batch(rows: list[dict], device: str, augmentation=None):
    import torch
    values = []
    for row in rows:
        rgb = legacy.bound_rgb(row, 224)
        tensor = torch.from_numpy(normalize_rgb(
            rgb, 224, (.485, .456, .406), (.229, .224, .225)))
        if augmentation is not None and torch.rand((), generator=augmentation).item() < .5:
            tensor = tensor.flip(-1)
        values.append(tensor)
    return torch.stack(values).to(device)


def atomic_checkpoint(path: Path, record: dict, guard) -> None:
    import torch
    temporary = path.with_suffix(".partial")
    if path.exists() or temporary.exists():
        raise FileExistsError("immutable checkpoint already present")
    allowance = sum(value.nelement() * value.element_size() for value in record["state_dict"].values()) + 2097152
    if allowance > 134217728:
        raise MemoryError("checkpoint exceeds prewrite reservation")
    guard()
    with temporary.open("xb") as stream:
        torch.save(record, stream)
        stream.flush()
        os.fsync(stream.fileno())
    if temporary.stat().st_size > allowance:
        raise MemoryError("serialized checkpoint exceeded its prewrite allowance")
    guard()
    os.link(temporary, path)
    temporary.unlink()


def start(kind: str, key: str) -> None:
    write_immutable_record(OUTPUT / "starts" / f"{kind}-{key}.json", {"kind": kind, "key": key})


def active_context(key: str, phase: str, begun: float) -> None:
    record = {"context": key, "phase": phase, "started_monotonic": begun}
    path = OUTPUT / "active_context.json"
    temporary = path.with_suffix(".temporary")
    with temporary.open("x") as stream:
        json.dump(record, stream)
    os.replace(temporary, path)


def execute_phase(*, replay: bool) -> None:
    import torch
    import specialist
    plan, approval = authority()
    attempt = read(OUTPUT / "attempt.json")
    if (attempt["supervisor_pid"] != os.getppid()
            or attempt["plan_sha256"] != digest(OUTPUT / "execution_plan.json")):
        raise ValueError("worker/verification require the owning resource supervisor")
    config = read(SPEC)
    specialist.configure(20260917)
    torch.cuda.set_per_process_memory_fraction(
        plan["limits"]["CUDA_allocated_and_reserved_each_bytes"] / torch.cuda.get_device_properties(0).total_memory)
    guard = lambda: resources(approval, final=replay, cuda=True)
    initialization = OUTPUT / "initialization.pth" if replay else acquire(plan, guard)
    if replay and digest(initialization) != read(OUTPUT / "initialization.json")["sha256"]:
        raise ValueError("acquired initialization changed")
    initial_state = torch.load(initialization, map_location="cpu", weights_only=True)
    if not isinstance(initial_state, dict) or any(
        not isinstance(value, torch.Tensor) or not torch.isfinite(value).all() for value in initial_state.values()):
        raise ValueError("finite torchvision ImageNet initialization state required")
    probe = specialist.Specialist(initial_state)
    del probe
    gc.collect()
    rows = preparation.active_rows(read(preparation.MANIFEST)["rows"])
    indexed = {identity(row): row for row in rows}
    partitions = read(preparation.OUTPUT / "partitions.json")
    validate_partitions(rows, partitions)
    ids, features = load_features(rows, {}, guard)
    positions = {key: i for i, key in enumerate(ids)}
    all_results = []
    for context in partitions["contexts"]:
        begun = time.monotonic()
        guard = lambda: resources(approval, final=replay, context_started=begun, cuda=True)
        guard()
        key = f"{context['target']}-{context['seed']}"
        active_context(key, "verify" if replay else "worker", begun)
        folder = OUTPUT / "contexts" / key
        folder.mkdir(parents=True, exist_ok=True)
        pools = {role: [indexed[value] for value in context[role] if value in positions]
                 for role in ("fitting", "validation", "calibration", "evaluation")}
        originals = [indexed[value] for value in context["evaluation"]]
        frozen_models, calibration_logits, evaluation_logits = {}, {}, {}
        saved = read(folder / "models.json") if replay else None
        for name in BRANCHES[:3]:
            def x(role):
                return features[name][[positions[identity(row)] for row in pools[role]]]
            settings = {"epochs": 200, "learning_rate": .01 if name == "openclip" else .001, "weight_decay": .05}
            if replay:
                model = saved["heads"][name]
            else:
                start("frozen", f"{key}-{name}")
                model = fit_head(
                    x("fitting"), np.asarray([row["binary_label"] == "attack" for row in pools["fitting"]], dtype=int),
                    [row["dataset"] for row in pools["fitting"]], x("validation"),
                    np.asarray([row["binary_label"] == "attack" for row in pools["validation"]], dtype=int),
                    [row["dataset"] for row in pools["validation"]],
                    seed=context["seed"], settings=settings, guard=guard)
            frozen_models[name] = model
            calibration_logits[name] = head_logits(model, x("calibration"))
            evaluation_logits[name] = head_logits(model, x("evaluation"))
        specialist.configure(context["seed"])
        model = specialist.Specialist(initial_state).cuda()
        checkpoint = folder / "specialist.pth"
        if replay:
            state = torch.load(checkpoint, map_location="cpu", weights_only=True)
            model.load_state_dict(state["state_dict"], strict=True)
        else:
            start("specialist", key)
            state = specialist.train_model(model, pools["fitting"], pools["validation"], image_batch,
                                           context["seed"], config["specialist"], "cuda", guard)
            if (len(state["history"]) != config["specialist"]["epochs"]
                    or state["optimizer_steps"] != (
                        (len(pools["fitting"])+15)//16)*config["specialist"]["epochs"]
                    or not 1 <= state["selected_epoch"] <= config["specialist"]["epochs"]):
                raise ValueError("complete fixed specialist recipe required; no shortened success")
            atomic_checkpoint(checkpoint, state, guard)
            restored = specialist.Specialist().cuda()
            restored.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True)["state_dict"], strict=True)
            del model
            model = restored
        for role, destination in (("calibration", calibration_logits), ("evaluation", evaluation_logits)):
            raw = specialist.predict(model, pools[role], image_batch, "cuda", guard)
            clipped = np.clip(raw, 1e-6, 1-1e-6)
            destination["matched_deeppixbis"] = np.log(clipped/(1-clipped))
        del model
        gc.collect()
        torch.cuda.empty_cache()
        calibrators, calibrated = {}, {"calibration": {}, "evaluation": {}}
        for name in BRANCHES:
            if replay:
                calibrator = saved["calibrators"][name]
            else:
                start("calibrator", f"{key}-{name}")
                calibrator = fit_calibrator(calibration_logits[name],
                    np.asarray([row["binary_label"] == "attack" for row in pools["calibration"]], dtype=int),
                    [row["dataset"] for row in pools["calibration"]], guard)
            calibrators[name] = calibrator
            for role, logits in (("calibration", calibration_logits), ("evaluation", evaluation_logits)):
                calibrated[role][name] = calibrate(calibrator, logits[name])
        for role in calibrated:
            calibrated[role]["fixed_equal_two_dino"] = (
                calibrated[role]["dino_reg"] + calibrated[role]["dino_plain"]) / 2
            calibrated[role]["supervised_clip"] = calibrated[role].pop("openclip")
            calibrated[role].pop("dino_plain")
        policies = {system: {str(alpha): study.threshold(
            calibrated["calibration"][system], pools["calibration"], alpha) for alpha in study.ALPHAS}
                    for system in study.SYSTEMS}
        prediction = {system: calibrated["evaluation"][system].tolist() for system in study.SYSTEMS}
        artifact = {
            "heads": frozen_models, "calibrators": calibrators, "policies": policies,
            "specialist_sha256": digest(checkpoint), "specialist_selected_epoch": state["selected_epoch"],
            "specialist_optimizer_steps": state["optimizer_steps"]}
        result = {"target": context["target"], "seed": context["seed"],
                  "usable_ids": [identity(row) for row in pools["evaluation"]], "prediction": prediction,
                  "analysis": study.summarize_context(prediction, originals, policies, oracle316.oracle, guard)}
        if replay:
            frozen.check_reconstruction(saved, artifact)
            frozen.check_reconstruction(read(folder / "prediction_analysis.json"), result)
        else:
            write_immutable_record(folder / "models.json", artifact)
            write_immutable_record(folder / "prediction_analysis.json", result)
        all_results.append(result)
        print("PAPER321_CONTEXT_VERIFIED" if replay else "PAPER321_CONTEXT_COMPLETE", key, flush=True)
    guard = lambda: resources(approval, final=True, cuda=True)
    guard()
    actual = {kind: len(list((OUTPUT / "starts").glob(f"{kind}-*.json")))
              for kind in ("frozen", "specialist", "calibrator")}
    if actual != {"frozen": 36, "specialist": 12, "calibrator": 48}:
        raise ValueError("all and only declared fit starts required")
    if sum(len(context["analysis"]["cases"]) for context in all_results) != 144:
        raise ValueError("all144 source-policy/oracle cases required")
    aggregate = study.aggregate(all_results)
    figure = study.plot(all_results)
    if replay:
        frozen.check_reconstruction(read(OUTPUT / "worker_completion.json")["aggregate"], aggregate)
        if (OUTPUT / "low-fa.svg").read_text() != figure:
            raise ValueError("saved low-FA figure differs")
        write_immutable_record(OUTPUT / "verification.json", {
            "plan_sha256": digest(OUTPUT / "execution_plan.json"),
            "all12_contexts_reconstructed": True, "new_fits": 0,
            "specialist_checkpoint_predictions_replayed": True,
            "worker_sha256": digest(OUTPUT / "worker_completion.json")})
    else:
        with (OUTPUT / "low-fa.svg").open("x") as stream:
            stream.write(figure)
        write_immutable_record(OUTPUT / "worker_completion.json", {
            "plan_sha256": digest(OUTPUT / "execution_plan.json"), "fit_starts": actual,
            "contexts": [{"target": result["target"], "seed": result["seed"],
                          "analysis": result["analysis"]} for result in all_results],
            "aggregate": aggregate,
            "low_FA_plot_sha256": digest(OUTPUT / "low-fa.svg"),
            "new_foundation_encoder_forwards": 0, "oracle_is_diagnostic": True})


def supervise() -> int:
    plan, approval = authority()
    write_immutable_record(OUTPUT / "attempt.json", {
        "plan_sha256": digest(OUTPUT / "execution_plan.json"), "automatic_retry": False,
        "supervisor_pid": os.getpid()})
    child, failure, peak_rss = None, None, 0
    env = {**os.environ, "OPENBLAS_NUM_THREADS": "2", "OMP_NUM_THREADS": "2", "MKL_NUM_THREADS": "2",
           "CUBLAS_WORKSPACE_CONFIG": ":4096:8", "HF_HUB_OFFLINE": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        for phase in ("worker", "verify"):
            resources(approval, final=phase == "verify")
            (OUTPUT / "active_context.json").unlink(missing_ok=True)
            with (OUTPUT / f"{phase}.log").open("x") as log:
                child = subprocess.Popen([sys.executable, str(Path(__file__)), f"--{phase}"],
                                         env=env, start_new_session=True, stdout=log, stderr=subprocess.STDOUT)
                while child.poll() is None:
                    resources(approval, final=phase == "verify")
                    active = OUTPUT / "active_context.json"
                    if active.exists():
                        clock(approval, final=phase == "verify",
                              context_started=read(active)["started_monotonic"])
                    own = next(int(line.split()[1])*1024 for line in Path("/proc/self/status").read_text().splitlines()
                               if line.startswith("VmRSS:"))
                    peak_rss = max(peak_rss, own + legacy.pilot.group_rss(child.pid))
                    if peak_rss > plan["limits"]["combined_sampled_RSS_bytes"]:
                        raise MemoryError("combined process-group RSS ceiling")
                    time.sleep(.5)
                if child.returncode:
                    raise RuntimeError(f"{phase} exited {child.returncode}; see retained log; no retry")
        if not (OUTPUT / "verification.json").is_file():
            raise RuntimeError("no independent checkpoint reconstruction receipt")
    except (OSError, ValueError, RuntimeError, TimeoutError, MemoryError) as exc:
        failure = f"{type(exc).__name__}: {exc}"
        print("PAPER321_STOP", failure, file=sys.stderr, flush=True)
    finally:
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
    try:
        resources(approval, final=True)
    except (TimeoutError, MemoryError) as exc:
        failure = failure or f"{type(exc).__name__}: {exc}"
    write_immutable_record(OUTPUT / "terminal.json", {
        "status": "complete" if failure is None else "stopped_no_retry", "failure": failure,
        "sampled_peak_combined_RSS": peak_rss, "owned_bytes_before_terminal": owned_size(),
        "wall_seconds": time.monotonic()-approval["started_monotonic"], "automatic_retry": False})
    return int(failure is not None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    for action in ("prepare", "approve", "execute", "worker", "verify"):
        group.add_argument(f"--{action}", action="store_true")
    parser.add_argument("--answer")
    args = parser.parse_args()
    with threadpool_limits(limits=2):
        if args.prepare:
            prepare()
        elif args.approve:
            approve(args.answer)
        elif args.execute:
            return supervise()
        else:
            execute_phase(replay=args.verify)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
