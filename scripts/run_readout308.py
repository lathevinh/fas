"""Prepare, authorize and supervise the source-only cache readout comparison."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from fas.feature_cache import cache_key, digest, load_shard, payload_digest
from fas.freeze import write_immutable_record
from fas.frozen_features import mean_cosine_logit
from fas.readout_study import (
    BRANCHES, SYSTEMS, check_head, error_overlap, evaluation_ids, fit_readouts, metrics,
    paired_uncertainty, score_readouts, selected_index, transform, validate_context,
)
from fas.source_fitting import calibrate, head_logits, identity, objective_weights, operating_threshold
from threadpoolctl import threadpool_limits
import run_source297 as baseline

CONFIG = ROOT / "configs/readout308_v1.yaml"


def read(path: Path) -> dict:
    return json.loads(path.read_bytes())


def output(config: dict) -> Path:
    return Path(config["private_root"]) / config["output_name"]


def code_pins() -> dict:
    paths = [*ROOT.glob("src/fas/*.py"), *ROOT.glob("scripts/*.py"),
             baseline.pilot.CONFIG, ROOT / "configs/source_run297_v1.yaml",
             ROOT / "configs/prompts_core_v1.yaml", ROOT / "configs/ci-synthetic308.in",
             ROOT / "tests/test_readout308.py"]
    return {str(path.relative_to(ROOT)): digest(path) for path in sorted(paths)}


def check_runtime(config: dict) -> dict:
    actual = {"python": platform.python_version(),
              **{name: importlib.metadata.version(name) for name in ("numpy", "scipy", "threadpoolctl")}}
    if actual != config["runtime"]:
        raise ValueError(f"exact readout runtime required, observed {actual}")
    return actual


def shard_matrix(model: dict, keys: list[str], dimension: int, guard) -> np.ndarray:
    if len(set(keys)) != len(keys):
        raise ValueError("unique complete cache keys required")
    parts, offset = [], 0
    for shard in model["shards"]:
        guard()
        path = Path(shard["path"])
        if digest(path) != shard["sha256"]:
            raise ValueError("original baseline feature shard hash drift")
        count = shard["count"]
        parts.append(load_shard(path, keys[offset:offset + count], dimension))
        offset += count
    if offset != len(keys):
        raise ValueError("complete original cache shard coverage required")
    return np.concatenate(parts)


def fit_path(config: dict, context: dict, split: dict) -> Path:
    return (Path(config["private_root"]) / config["baseline"] / "combinations" /
            context["key"] / "fits" / f"{payload_digest({'split': split})}.json")


def study_splits(context: dict) -> list[dict]:
    return [split for split in context["partitions"]
            if split["name"] == "final" or split["name"].startswith("domain_oof:")]


def load_inputs(config: dict, guard) -> tuple[dict, list[dict], dict, np.ndarray, dict]:
    root = Path(config["private_root"])
    for name, sha in config["pinned_inputs"].items():
        guard()
        if digest(root / name) != sha:
            raise ValueError(f"readout input binding drift: {name}")
    if config["head"] != read(ROOT / "configs/source_run297_v1.yaml")["head"]:
        raise ValueError("exact original head recipe must remain the shared anchor")
    anchor = {"name": "old_recipe", "transform": "raw", "settings": {}}
    if len(config["candidates"]) != 4 or config["candidates"][0] != anchor:
        raise ValueError("four equal-budget candidates including exact old anchor required")
    originals = [row for row in read(root / "source_integration295_v1/source_manifest.json")["rows"]
                 if row["source_use_eligible"]]
    inputs = read(root / config["baseline"] / "inputs.json")
    rows = inputs["rows"]
    if (len(originals) != config["expected_originals"] or len(rows) != config["expected_successes"]
            or {identity(row) for row in rows} != {identity(row) for row in originals if row["model_input_eligible"]}
            or len({identity(row) for row in rows}) != len(rows)):
        raise ValueError("unchanged original/successful source populations required")
    indexed_originals = {identity(row): row for row in originals}
    if any(row != indexed_originals[identity(row)] for row in rows):
        raise ValueError("exact source-use row/role/crop provenance required")
    if inputs["failure_rows"] != [row for row in originals if not row["model_input_eligible"]]:
        raise ValueError("all original terminal failures must remain in the denominator")
    if any(row["final_k1_action"] != "non_accept" or row["retain_original_denominator"] is not True
           for row in inputs["failure_rows"]):
        raise ValueError("terminal failures must be retained original-denominator non-acceptances")
    receipt = read(root / config["baseline"] / "extraction.json")
    prior = read(root / config["prior"] / "extraction.json")
    if receipt["ids"] != [identity(row) for row in rows]:
        raise ValueError("ordered baseline feature identities required")
    missing = [row for row in rows if row["dataset"] == "OULU-NPU"]
    prior_ids = prior["dino_reg"]["ids"]
    union_ids = prior_ids + [identity(row) for row in missing]
    if len(set(union_ids)) != len(rows) or set(union_ids) != {identity(row) for row in rows}:
        raise ValueError("one-to-one predecessor/new-source cache union required")
    union_index = {key: position for position, key in enumerate(union_ids)}
    order = [union_index[identity(row)] for row in rows]
    pilot = read(baseline.pilot.CONFIG)
    indexed = {identity(row): row for row in rows}
    features, bindings = {}, {}
    for name in BRANCHES:
        guard()
        old, new = prior[name], receipt[name]
        dimension = 512 if name == "openclip" else 1536
        if (old["ids"] != prior_ids or old["checkpoint_sha256"] != new["checkpoint_sha256"]
                or old["shape"][1] != dimension or new["shape"][1] != dimension):
            raise ValueError("original checkpoint, feature dimension and prior identity binding required")
        keys_old = [cache_key(baseline.base_key(indexed[key], name, pilot, old["checkpoint_sha256"]),
                              old["contract"]) for key in prior_ids]
        keys_new = [cache_key(baseline.base_key(row, name, pilot, new["checkpoint_sha256"]),
                              new["contract"]) for row in missing]
        if old["feature_keys"] != keys_old or new["keys"] != keys_new:
            raise ValueError("exact crop/transform/checkpoint/runtime cache keys required")
        first = shard_matrix(old, keys_old, dimension, guard)
        second = shard_matrix(new, keys_new, dimension, guard)
        features[name] = np.concatenate((first, second))[order]
        bindings[name] = {
            "shape": list(features[name].shape), "checkpoint_sha256": new["checkpoint_sha256"],
            "ordered_feature_bytes_sha256": hashlib.sha256(features[name].tobytes()).hexdigest(),
            "prior_contract_sha256": payload_digest(old["contract"]),
            "new_contract_sha256": payload_digest(new["contract"]),
            "shards": old["shards"] + new["shards"],
        }
    if not np.allclose(np.linalg.norm(features["openclip"], axis=1), 1, rtol=1e-5, atol=1e-5):
        raise ValueError("original normalized OpenCLIP embeddings required")
    text_path = Path(prior["text"]["path"])
    if digest(text_path) != prior["text"]["sha256"]:
        raise ValueError("fixed cached text embedding bytes changed; never infer or download")
    text = np.load(text_path, allow_pickle=False)
    bindings["fixed_text"] = {"path": str(text_path), "sha256": prior["text"]["sha256"]}
    return inputs, originals, features, text, bindings


def build_plan(config: dict, inputs: dict, originals: list[dict], features: dict, bindings: dict, guard) -> dict:
    expected = {(domain, seed) for domain in config["outer_exclusions"] for seed in config["seeds"]}
    if (len(inputs["contexts"]) != len(expected)
            or {(item["outer_target"], item["seed"]) for item in inputs["contexts"]} != expected
            or len({item["key"] for item in inputs["contexts"]}) != len(expected)):
        raise ValueError("all twelve original exclusion/seed contexts exactly once required")
    index = {identity(row): position for position, row in enumerate(inputs["rows"])}
    worker = read(Path(config["private_root"]) / config["baseline"] / "worker_completion.json")
    contexts, models = [], {}
    for context in inputs["contexts"]:
        guard()
        ids = context["row_ids"]
        if (len(ids) != len(set(ids)) or set(ids) !=
                {identity(row) for row in inputs["rows"] if row["dataset"] != context["outer_target"]}):
            raise ValueError("complete original source-only context population required")
        local_rows = [inputs["rows"][index[key]] for key in ids]
        local_index = {identity(row): position for position, row in enumerate(local_rows)}
        local = {name: values[[index[key] for key in ids]] for name, values in features.items()}
        published = next(item for item in worker["combinations"] if item["key"] == context["key"])
        splits = study_splits(context)
        if len(splits) != 4:
            raise ValueError("one final and three domain-OOF partitions required")
        for split in splits:
            guard()
            validate_context(local_rows, split, context["outer_target"], context["seed"])
            path = fit_path(config, context, split)
            sha = digest(path)
            saved = next(item for item in published["contexts"] if item["context"] == split["name"])
            fitted = read(path)["fitted"]
            if sha != saved["sha256"] or fitted["split"] != split:
                raise ValueError("exact original saved head/calibrator/policy binding required")
            validation = np.asarray([local_index[key] for key in split["validation"]])
            labels = np.asarray([local_rows[position]["binary_label"] == "attack" for position in validation])
            domains = [local_rows[position]["dataset"] for position in validation]
            for name in ("dino_reg", "dino_plain"):
                check_head(fitted["heads"][name], local[name][validation], labels, domains, config["head"]["epochs"])
            models[str(path)] = sha
        eligible = [row for row in originals if row["dataset"] != context["outer_target"]]
        contexts.append({
            "key": context["key"], "outer_exclusion": context["outer_target"], "seed": context["seed"],
            "originals": len(eligible), "successful": len(local_rows),
            "technical_failures": len(eligible) - len(local_rows),
            "split_counts": {split["name"]: {key: len(evaluation_ids(local_rows, split)) if key == "evaluation" else len(split[key]) for key in
                                           ("fitting", "validation", "calibration", "evaluation")} for split in splits},
        })
    return {
        "study": config["study"], "status": "prepared_not_authorized",
        "config_sha256": digest(CONFIG), "code_sha256": code_pins(), "runtime": check_runtime(config),
        "input_sha256": config["pinned_inputs"], "cache_bindings": bindings, "baseline_models": models,
        "originals": len(originals), "successes": len(inputs["rows"]),
        "failures": len(originals) - len(inputs["rows"]), "contexts": contexts,
        "candidate_heads_including_anchors": 576, "reused_baseline_heads": 96,
        "new_head_fits": 480, "new_calibrator_fits": 144, "maximum_new_training_epochs": 96000,
        "limits": config["limits"], "encoder_forwards": 0, "new_target_evaluations": 0,
        "systems": list(SYSTEMS), "new_fusion_or_risk_models": False,
    }


def prepare() -> dict:
    config = read(CONFIG)
    inputs, originals, features, _, bindings = load_inputs(config, lambda: None)
    plan = build_plan(config, inputs, originals, features, bindings, lambda: None)
    private = output(config) / "execution_plan.json"
    public = ROOT / "results/phase1/readout308-plan-v1.json"
    for path in (private, public):
        if path.exists():
            if read(path) != plan:
                raise ValueError("sealed readout plan drift; revise the protocol/version rather than overwrite")
        else:
            write_immutable_record(path, plan)
    print(json.dumps({"plan_sha256": digest(private), "new_head_fits": plan["new_head_fits"],
                      "new_calibrator_fits": plan["new_calibrator_fits"], "status": plan["status"]}), flush=True)
    return plan


def authority() -> tuple[dict, dict, dict]:
    config = read(CONFIG)
    root = output(config)
    plan = read(root / "execution_plan.json")
    approval = read(root / "execution_approval.json")
    if (plan["config_sha256"] != digest(CONFIG) or plan["code_sha256"] != code_pins()
            or approval["plan_sha256"] != digest(root / "execution_plan.json")
            or approval["owner"] != "lathevinh" or approval["scope"] != config["study"]):
        raise ValueError("exact sealed code/config/plan and owner approval required")
    return config, plan, approval


def deadline_guard(approval: dict) -> None:
    if time.time() >= approval["deadline_unix"]:
        raise TimeoutError("original approval deadline reached; no retry or clock reset")


def approve() -> None:
    config = read(CONFIG)
    root = output(config)
    plan = read(root / "execution_plan.json")
    if plan["config_sha256"] != digest(CONFIG) or plan["code_sha256"] != code_pins():
        raise ValueError("prepare the exact tested package before owner approval")
    started = time.time()
    write_immutable_record(root / "execution_approval.json", {
        "owner": "lathevinh", "scope": config["study"], "plan_sha256": digest(root / "execution_plan.json"),
        "started_unix": started, "deadline_unix": started + config["limits"]["wall_seconds"],
        "authority": "explicit_owner_chat_approval_recorded_by_operator", "automatic_retry": False,
    })


def verify_fit(rows: list[dict], features: dict, fitted: dict, config: dict) -> None:
    index = {identity(row): position for position, row in enumerate(rows)}
    split = fitted["split"]
    validation = np.asarray([index[key] for key in split["validation"]])
    calibration = np.asarray([index[key] for key in split["calibration"]])
    y = np.asarray([row["binary_label"] == "attack" for row in rows], dtype=np.float64)
    domains = [rows[position]["dataset"] for position in validation]
    p = {}
    for name in BRANCHES:
        if fitted["selected"][name] != selected_index(fitted["candidates"][name]):
            raise ValueError("saved candidate selection drift")
        if len(fitted["candidates"][name]) != len(config["candidates"]):
            raise ValueError("all candidate models must remain visible")
        for candidate, saved in zip(config["candidates"], fitted["candidates"][name], strict=True):
            if saved["candidate"] != candidate["name"]:
                raise ValueError("saved candidate order drift")
            values = transform(features[name][validation], candidate["transform"])
            check_head(saved["model"], values, y[validation], domains, config["head"]["epochs"])
        selected = fitted["selected"][name]
        candidate = config["candidates"][selected]
        logits = head_logits(fitted["candidates"][name][selected]["model"],
                             transform(features[name][calibration], candidate["transform"]))
        model = fitted["calibrators"][name]
        if not model["optimizer_success"] or not np.isfinite(model["slope"]) or model["slope"] <= 0:
            raise ValueError("successful finite monotone calibration required")
        calibrated_logits = model["slope"] * logits + model["intercept"]
        weight = objective_weights(y[calibration], [rows[position]["dataset"] for position in calibration], balanced=True)
        bce = float(weight @ (np.logaddexp(0, calibrated_logits) - y[calibration] * calibrated_logits))
        if not np.isclose(bce, model["bce"], rtol=1e-10, atol=1e-10):
            raise ValueError("saved calibration objective drift")
        p[name] = calibrate(model, logits)
    scores = {"selected_dino_reg": p["dino_reg"], "selected_two_dino": (p["dino_reg"] + p["dino_plain"]) / 2,
              "supervised_clip": p["openclip"]}
    for name, values in scores.items():
        policy = operating_threshold(values, [rows[position] for position in calibration], alpha=config["reference_alpha"])
        if policy != fitted["policies"][name]:
            raise ValueError("saved calibration-only operating policy drift")


def check_reconstruction(saved, rebuilt, location: str = "result") -> None:
    if isinstance(saved, dict) and isinstance(rebuilt, dict) and saved.keys() == rebuilt.keys():
        for key in saved:
            check_reconstruction(saved[key], rebuilt[key], f"{location}.{key}")
    elif isinstance(saved, list) and isinstance(rebuilt, list) and len(saved) == len(rebuilt):
        for index, (first, second) in enumerate(zip(saved, rebuilt, strict=True)):
            check_reconstruction(first, second, f"{location}[{index}]")
    elif isinstance(saved, float) and isinstance(rebuilt, float):
        if not np.isfinite(saved) or not np.isfinite(rebuilt) or not np.isclose(saved, rebuilt, rtol=1e-12, atol=1e-12):
            raise ValueError(f"saved numeric readback drift: {location}")
    elif type(saved) is not type(rebuilt) or saved != rebuilt:
        raise ValueError(f"saved readback drift: {location}")


def run_worker(*, verify_only: bool = False) -> dict:
    config, plan, approval = authority()
    root = output(config)
    guard = (lambda: None) if verify_only else lambda: deadline_guard(approval)
    if not verify_only:
        attempt = read(root / "attempt_lock.json")
        if os.getppid() != attempt["supervisor_pid"]:
            raise RuntimeError("scientific worker requires its live approving supervisor")
    guard()
    inputs, originals, features, text, bindings = load_inputs(config, guard)
    if build_plan(config, inputs, originals, features, bindings, guard) != plan:
        raise ValueError("full input/cache/split preflight must match the sealed plan before any fit")
    counters = {"new_head_fits": 0, "new_calibrator_fits": 0}
    audited = {"new_head_fits": 0, "new_calibrator_fits": 0}
    index = {identity(row): position for position, row in enumerate(inputs["rows"])}
    live_count = len(read(ROOT / "configs/prompts_core_v1.yaml")["classes"]["live"])
    summaries = []
    for context in inputs["contexts"]:
        guard()
        positions = [index[key] for key in context["row_ids"]]
        rows = [inputs["rows"][position] for position in positions]
        local = {name: values[positions] for name, values in features.items()}
        clip = mean_cosine_logit(local["openclip"], text, live_count)
        pools = {"domain_oof": [], "g_domain": []}
        candidate_reports, selections, fit_artifacts = {}, {}, {}
        for split in study_splits(context):
            guard()
            base_path = fit_path(config, context, split)
            old = read(base_path)["fitted"]
            path = root / "combinations" / context["key"] / f"{payload_digest({'split': split})}.json"

            def checkpoint(name: str, value: dict) -> None:
                write_immutable_record(path.parent / "checkpoints" / f"{path.stem}-{name}.json", {
                    "plan_sha256": digest(root / "execution_plan.json"),
                    "baseline_sha256": digest(base_path), "value": value})
                print("READOUT308_CHECKPOINT", context["key"], split["name"], name, flush=True)

            if not verify_only:
                fitted = fit_readouts(rows, local, old, split, config, context["seed"], guard, counters, checkpoint)
                write_immutable_record(path, {"fitted": fitted, "baseline_sha256": digest(base_path),
                                              "plan_sha256": digest(root / "execution_plan.json"),
                                              "fit_counts_at_completion": dict(counters)})
            saved = read(path)
            if (saved["baseline_sha256"] != digest(base_path) or saved["fitted"]["split"] != split
                    or saved["plan_sha256"] != digest(root / "execution_plan.json")):
                raise ValueError("saved readout model provenance drift")
            fitted = saved["fitted"]
            verify_fit(rows, local, fitted, config)
            for name in BRANCHES:
                for number, item in enumerate(fitted["candidates"][name]):
                    expected_origin = "baseline299_anchor" if number == 0 and name != "openclip" else "new_readout"
                    if item["origin"] != expected_origin:
                        raise ValueError("saved anchor/new-fit accounting drift")
                    audited["new_head_fits"] += int(item["origin"] == "new_readout")
                    complete = read(path.parent / "checkpoints" / f"{path.stem}-head-{name}-{number}-complete.json")
                    check_reconstruction(complete["value"], item)
                complete = read(path.parent / "checkpoints" / f"{path.stem}-calibrator-{name}-complete.json")
                check_reconstruction(complete["value"], fitted["calibrators"][name])
                audited["new_calibrator_fits"] += 1
            if saved["fit_counts_at_completion"] != audited:
                raise ValueError("saved incremental fit-attempt ledger drift")
            fit_artifacts[split["name"]] = {
                "path": str(path), "sha256": digest(path),
                "checkpoint_sha256": {item.name: digest(item)
                                      for item in sorted((path.parent / "checkpoints").glob(f"{path.stem}-*.json"))},
            }
            predicted, report = score_readouts(rows, local, clip, old, fitted, config)
            pools["g_domain" if split["name"] == "final" else "domain_oof"].extend(predicted)
            candidate_reports[split["name"]] = report
            selections[split["name"]] = {
                name: {"candidate": config["candidates"][number]["name"],
                       "selected_epoch": fitted["candidates"][name][number]["model"]["selected_epoch"],
                       "validation_bce": fitted["candidates"][name][number]["model"]["validation_bce"]}
                for name, number in fitted["selected"].items()}
        evaluation = {}
        for name, records in pools.items():
            population = [row for row in originals if row["dataset"] != context["outer_target"]
                          and (row["role"] == "g_domain") == (name == "g_domain")]
            values = metrics(records, population)
            uncertainty = paired_uncertainty(records, config["bootstrap_repetitions"],
                                             context["seed"] + (1 if name == "g_domain" else 0), guard)
            gate = {}
            for system in SYSTEMS:
                macro = values["equal_source_macro"][system]
                score_range = np.ptp([row["scores"][system] for row in records])
                gate[system] = bool(macro["auroc"] >= 0.55 and macro["successful_balanced_accuracy"] >= 0.55
                                    and uncertainty["macro_auroc_ci95"][system][0] > 0.5 and score_range > 1e-6)
            evaluation[name] = {"metrics": values, "uncertainty": uncertainty, "competence_screen": gate,
                                "error_overlap": error_overlap(records)}
        summary = {"key": context["key"], "selections": selections, "evaluation": evaluation,
                   "fit_artifacts": fit_artifacts,
                   "all_candidate_held_out_ranking_diagnostic_only": candidate_reports}
        result_path = root / "combinations" / context["key"] / "result.json"
        predictions_path = result_path.with_name("predictions.json")
        if verify_only:
            check_reconstruction(read(result_path), summary)
            check_reconstruction(read(predictions_path), pools)
        else:
            write_immutable_record(predictions_path, pools)
            write_immutable_record(result_path, summary)
            check_reconstruction(read(result_path), summary)
            check_reconstruction(read(predictions_path), pools)
        summaries.append(summary)
        print("READOUT308_VERIFIED" if verify_only else "READOUT308_COMPLETED", context["key"], flush=True)
    expected_counts = {key: plan[key] for key in ("new_head_fits", "new_calibrator_fits")}
    if audited != expected_counts or (not verify_only and counters != expected_counts):
        raise ValueError("all registered fits exactly once required for completion")
    result = {"study": config["study"], "plan_sha256": digest(root / "execution_plan.json"),
              "combinations": summaries, "fit_counts": {"new_head_fits": plan["new_head_fits"],
                                                        "new_calibrator_fits": plan["new_calibrator_fits"]},
              "encoder_forwards": 0, "new_target_evaluations": 0, "no_target_performance_claim": True}
    if verify_only:
        check_reconstruction(read(root / "worker_completion.json"), result)
    else:
        guard()
        write_immutable_record(root / "worker_completion.json", result)
    return result


def owned_size(root: Path) -> int:
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def supervise() -> int:
    config, _, approval = authority()
    root = output(config)
    limits = config["limits"]
    deadline_guard(approval)
    write_immutable_record(root / "attempt_lock.json", {
        "supervisor_pid": os.getpid(), "plan_sha256": digest(root / "execution_plan.json"), "automatic_retry": False})
    env = {**os.environ, "OPENBLAS_NUM_THREADS": str(limits["blas_threads"]),
           "OMP_NUM_THREADS": str(limits["blas_threads"]), "MKL_NUM_THREADS": str(limits["blas_threads"]),
           "CUDA_VISIBLE_DEVICES": "", "HF_HUB_OFFLINE": "1", "PYTHONDONTWRITEBYTECODE": "1",
           "TMPDIR": str(root / "temporary")}
    (root / "temporary").mkdir(exist_ok=False)
    failure, peak_rss, peak_bytes = None, 0, owned_size(root)
    child = None
    try:
        if peak_bytes + limits["terminal_reserve_bytes"] > limits["owned_output_bytes"]:
            raise MemoryError("insufficient owned output budget before worker launch")
        with (root / "worker.log").open("x") as log:
            child = subprocess.Popen([sys.executable, str(Path(__file__)), "--worker"],
                                     env=env, start_new_session=True, stdout=log, stderr=subprocess.STDOUT)
            while child.poll() is None:
                deadline_guard(approval)
                own_rss = next(int(line.split()[1]) * 1024
                               for line in Path(f"/proc/{os.getpid()}/status").read_text().splitlines()
                               if line.startswith("VmRSS:"))
                rss = baseline.pilot.group_rss(child.pid) + own_rss
                peak_rss, peak_bytes = max(peak_rss, rss), max(peak_bytes, owned_size(root))
                if (peak_rss > limits["combined_sampled_rss_bytes"]
                        or peak_bytes + limits["terminal_reserve_bytes"] > limits["owned_output_bytes"]):
                    raise MemoryError("combined sampled RSS or owned output/temporary-byte cap exceeded")
                time.sleep(limits["sample_interval_seconds"])
            if child.returncode:
                raise RuntimeError(f"readout worker exit{child.returncode}; see worker.log; no retry")
            deadline_guard(approval)
            peak_bytes = max(peak_bytes, owned_size(root))
            if peak_bytes + limits["terminal_reserve_bytes"] > limits["owned_output_bytes"]:
                raise MemoryError("final owned output cap exceeded")
            if not (root / "worker_completion.json").is_file():
                raise RuntimeError("worker exited without scientific completion")
    except (OSError, ValueError, RuntimeError, TimeoutError, MemoryError) as exc:
        failure = f"{type(exc).__name__}: {exc}"
        print("READOUT308_STOP", failure, file=sys.stderr, flush=True)
    finally:
        if child is not None and child.poll() is None:
            os.kill(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.kill(child.pid, signal.SIGKILL)
                child.wait()
    peak_bytes = max(peak_bytes, owned_size(root))
    wall = time.time() - approval["started_unix"]
    if failure is None and peak_bytes + limits["terminal_reserve_bytes"] > limits["owned_output_bytes"]:
        failure = "MemoryError: final output inventory exceeded the reserved-space cap"
    if failure is None and wall > limits["wall_seconds"]:
        failure = "TimeoutError: original approval deadline exceeded during final resource accounting"
    terminal = {
        "status": "complete" if failure is None else "stopped_no_retry", "failure": failure,
        "wall_seconds_from_original_approval": wall,
        "sampled_peak_combined_rss": peak_rss, "peak_owned_bytes_before_terminal": peak_bytes,
        "limits": limits, "automatic_retry": False,
        "worker_completion_sha256": digest(root / "worker_completion.json") if failure is None else None,
    }
    if 2 * len((json.dumps(terminal, indent=2, sort_keys=True) + "\n").encode()) > limits["terminal_reserve_bytes"]:
        raise RuntimeError("terminal plus atomic temporary copy exceeds reserved audit space")
    write_immutable_record(root / "terminal.json", terminal)
    print("READOUT308_TERMINAL", json.dumps(terminal), flush=True)
    return int(failure is not None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    for name in ("prepare", "approve", "execute", "worker", "verify"):
        actions.add_argument(f"--{name}", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        prepare()
    elif args.approve:
        approve()
    elif args.execute:
        return supervise()
    elif args.worker:
        with threadpool_limits(limits=read(CONFIG)["limits"]["blas_threads"]):
            run_worker()
    else:
        config, _, _ = authority()
        terminal = read(output(config) / "terminal.json")
        if (terminal["status"] != "complete" or terminal["failure"] is not None
                or terminal["limits"] != config["limits"]
                or terminal["wall_seconds_from_original_approval"] > config["limits"]["wall_seconds"]
                or terminal["sampled_peak_combined_rss"] > config["limits"]["combined_sampled_rss_bytes"]
                or terminal["peak_owned_bytes_before_terminal"] + config["limits"]["terminal_reserve_bytes"]
                > config["limits"]["owned_output_bytes"]
                or terminal["worker_completion_sha256"] != digest(output(config) / "worker_completion.json")):
            raise ValueError("successful terminal with exact worker completion required for saved-output closure")
        with threadpool_limits(limits=config["limits"]["blas_threads"]):
            run_worker(verify_only=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
