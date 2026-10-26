"""Single-authority bounded checkpoint acquisition and frozen source encoder pilot."""

from __future__ import annotations

import argparse
import gc
import hashlib
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from fas.environment import inspect_environment, verify_source_checkout
from fas.freeze import write_immutable_record
from fas.frozen_features import check_feature, dino_pool, feature_key, mean_cosine_logit, normalize_rgb, parity
from fas.source_stage import require_source_input

PRIVATE = Path("/mnt/e/FAS-private/artifacts/phase1")
APPROVAL_ROOT = PRIVATE / "source_pilot295_v1"
INTEGRATION = PRIVATE / "source_integration295_v1"
NATIVE = Path.home() / ".cache/fas/source-pilot295-v1"
CONFIG = ROOT / "configs/source_pilot295_v1.yaml"
UPSTREAM = Path.home() / ".cache/fas/upstream/dinov2-7764ea0"
GIB = 1024 ** 3


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 ** 2), b""):
            value.update(chunk)
    return value.hexdigest()


def read(path: Path) -> dict:
    return json.loads(path.read_bytes())


def authority() -> tuple[dict, dict]:
    config, approval = read(CONFIG), read(APPROVAL_ROOT / "owner_approval.json")
    if (approval["explicit_owner_approval"] is not True
            or approval["selected_answer"] != "approve_source295_checkpoint_and_frozen_encoder_pilot"
            or approval["pilot_config_sha256"] != digest(CONFIG)
            or approval["deadline_unix_seconds"] != approval["started_unix_seconds"] + 5400
            or approval["caps"] != {"wall_seconds": 5400, "rss_bytes": 8 * GIB,
                                    "cuda_bytes": 12 * GIB, "output_bytes": 8 * GIB}
            or approval["automatic_retry"] is not False):
        raise ValueError("exact original pilot authority and caps required")
    return config, approval


def size() -> int:
    return sum(path.stat().st_size for root in (NATIVE, APPROVAL_ROOT) if root.exists()
               for path in root.rglob("*") if path.is_file())


def enforce(approval: dict, *, final: bool = False) -> None:
    if time.time() >= approval["deadline_unix_seconds" if final else "work_deadline_unix_seconds"]:
        raise TimeoutError("original source295 work/final deadline")
    if size() > approval["caps"]["output_bytes"]:
        raise MemoryError("source295 owned new+temporary8GiB artifact cap")


def acquire(name: str, spec: dict, approval: dict) -> dict:
    folder = NATIVE / "checkpoints"
    folder.mkdir(parents=True, exist_ok=True)
    path, temporary = folder / f"{name}.pth", folder / f"{name}.part"
    if path.exists() or temporary.exists():
        raise FileExistsError("no automatic checkpoint retry or overwrite")
    value, count, started = hashlib.sha256(), 0, time.monotonic()
    with urllib.request.urlopen(spec["url"], timeout=60) as response, temporary.open("xb") as handle:
        if int(response.headers["Content-Length"]) != spec["bytes"]:
            raise ValueError("checkpoint response length differs from the approved official endpoint")
        while chunk := response.read(1024 ** 2):
            count += len(chunk)
            if count > spec["bytes"]:
                raise ValueError("checkpoint response exceeds declared size")
            handle.write(chunk)
            value.update(chunk)
            enforce(approval)
        handle.flush()
        os.fsync(handle.fileno())
    if count != spec["bytes"] or (spec["upstream_sha256"] is not None and value.hexdigest() != spec["upstream_sha256"]):
        raise ValueError("checkpoint exact EOF size/upstream SHA mismatch")
    temporary.rename(path)
    row = {"name": name, "sha256": value.hexdigest(), "bytes": count,
           "upstream_sha256_available": spec["upstream_sha256"] is not None,
           "url": spec["url"], "wall_seconds": time.monotonic() - started}
    write_immutable_record(NATIVE / f"{name}-acquisition.json", row)
    print("SOURCE295_ACQUIRED", json.dumps(row), flush=True)
    return row


def gpu_check(torch, approval):
    allocated, reserved = torch.cuda.max_memory_allocated(), torch.cuda.max_memory_reserved()
    if max(allocated, reserved) > approval["caps"]["cuda_bytes"]:
        raise MemoryError("source29512GiB CUDA allocated/reserved cap")
    return {"max_allocated_bytes": allocated, "max_reserved_bytes": reserved}


def worker() -> None:
    import numpy as np
    from PIL import Image
    import torch
    import open_clip

    config, approval = authority()
    attempt = read(APPROVAL_ROOT / "attempt_lock.json")
    if os.getppid() != attempt["supervisor_pid"]:
        raise ValueError("worker must belong to its single original supervisor")
    enforce(approval)
    if inspect_environment(ROOT, read(ROOT / "configs/environment_v1.yaml"))["status"] != "ready":
        raise RuntimeError("locked runtime must pass before model acquisition")
    verify_source_checkout(UPSTREAM, config["dinov2_source_commit"])
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; no CPU fallback")
    torch.set_num_threads(2)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)
    torch.cuda.set_per_process_memory_fraction(approval["caps"]["cuda_bytes"] / torch.cuda.get_device_properties(0).total_memory)
    torch.manual_seed(20260917)
    sys.path.insert(0, str(UPSTREAM))
    from dinov2.hub import backbones

    if digest(INTEGRATION / "pilot_inputs.json") != config["pilot_inputs_sha256"]:
        raise ValueError("sealed24 pilot input bytes changed")
    if digest(INTEGRATION / "source_manifest.json") != config["source_manifest_sha256"]:
        raise ValueError("sealed integrated population changed")
    inputs = read(INTEGRATION / "pilot_inputs.json")["rows"]
    if len(inputs) != 24 or len({(r["dataset"], r["video_id"]) for r in inputs}) != 24:
        raise ValueError("exact24 unique approved source train inputs required")
    for row in inputs:
        require_source_input(row, outer_target="OULU-NPU", purpose="fitting", model_input=True)
        if row["dataset"] not in config["source_domains"]:
            raise ValueError("unapproved pilot source dataset")
    acquisitions = {name: acquire(name, spec, approval) for name, spec in config["models"].items()}
    all_results = {}
    image_calls, text_calls = 0, 0
    for name, spec in config["models"].items():
        enforce(approval)
        started = time.monotonic()
        checkpoint = NATIVE / "checkpoints" / f"{name}.pth"
        if digest(checkpoint) != acquisitions[name]["sha256"]:
            raise ValueError("checkpoint bytes changed before strict local loading")
        torch.cuda.reset_peak_memory_stats()
        if name.startswith("dino"):
            model = getattr(backbones, spec["local_factory"])(pretrained=False)
            model.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True), strict=True)
            mean, std = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)
        else:
            model = open_clip.create_model("ViT-B-16", pretrained=None, precision="fp32")
            incompatible = open_clip.load_checkpoint(model, str(checkpoint), strict=True, weights_only=True)
            if incompatible.missing_keys or incompatible.unexpected_keys:
                raise ValueError("OpenCLIP strict registered checkpoint mismatch")
            native = open_clip.get_pretrained_cfg("ViT-B-16", "laion2b_s34b_b88k")
            mean, std = tuple(native["mean"]), tuple(native["std"])
        model.requires_grad_(False).eval().cuda()
        rows, keys, first_values, second_values, durations = [], [], [], [], []
        for index, row in enumerate(inputs):
            enforce(approval)
            crop = row["crops"][str(spec["resolution"])]
            payload = Path(crop["path"]).read_bytes()
            if hashlib.sha256(payload).hexdigest() != crop["sha256"]:
                raise ValueError("approved source crop SHA256 mismatch")
            with Image.open(io.BytesIO(payload)) as image:
                if image.mode != "RGB" or image.size != (spec["resolution"], spec["resolution"]):
                    raise ValueError("native RGB crop shape/mode drift; no recrop/resize")
                rgb = np.asarray(image)
            tensor = torch.from_numpy(normalize_rgb(rgb, spec["resolution"], mean, std)).unsqueeze(0).cuda()
            values = []
            for repeat in range(2):
                torch.cuda.synchronize()
                before = time.perf_counter()
                with torch.inference_mode():
                    if name.startswith("dino"):
                        output = model.forward_features(tensor)
                        feature = dino_pool(output["x_norm_clstoken"].cpu().numpy(),
                                            output["x_norm_patchtokens"].cpu().numpy())
                    else:
                        feature = model.encode_image(tensor, normalize=True).cpu().numpy()
                torch.cuda.synchronize()
                durations.append(time.perf_counter() - before)
                check_feature(feature, 1, spec["feature_dimension"])
                values.append(feature.copy())
                image_calls += 1
                gpu_check(torch, approval)
            parity(values[0], values[1])
            first_values.append(values[0])
            second_values.append(values[1])
            keys.append(feature_key(dataset=row["dataset"], video_id=row["video_id"],
                                    crop_sha256=crop["sha256"], checkpoint_sha256=acquisitions[name]["sha256"],
                                    preprocessing_sha256=config["preprocessing_sha256"],
                                    representation=spec.get("representation", "normalized_image_embedding")))
            rows.append({"dataset": row["dataset"], "video_id": row["video_id"], "crop_sha256": crop["sha256"]})
            print("SOURCE295_PROGRESS", name, index + 1, 24, flush=True)
        first, second = np.concatenate(first_values), np.concatenate(second_values)
        check_feature(first, 24, spec["feature_dimension"])
        max_difference = parity(first, second)
        shard = NATIVE / f"{name}-features.npy"
        with shard.open("xb") as handle:
            np.save(handle, first, allow_pickle=False)
        restored = np.load(shard, allow_pickle=False)
        if not np.array_equal(first, restored):
            raise ValueError("saved feature shard exact readback mismatch")
        result = {
            "checkpoint_sha256": acquisitions[name]["sha256"], "input_count": 24,
            "shape": list(first.shape), "dtype": str(first.dtype),
            "feature_payload_bytes": first.nbytes, "shard_bytes": shard.stat().st_size,
            "shard_sha256": digest(shard), "max_repeat_abs_difference": max_difference,
            "wall_seconds": time.monotonic() - started,
            "forward_seconds": sum(durations), "median_forward_seconds": float(np.median(durations)),
            "forward_calls": 48, "rows": rows, "feature_keys": keys,
            "normalization_mean": mean, "normalization_std": std, **gpu_check(torch, approval)}
        if name == "openclip":
            prompts = read(ROOT / "configs/prompts_core_v1.yaml")["classes"]
            texts = prompts["live"] + prompts["spoof"]
            tokens = open_clip.get_tokenizer("ViT-B-16")(texts).cuda()
            text_features = []
            for _ in range(2):
                with torch.inference_mode():
                    text_features.append(model.encode_text(tokens, normalize=True).cpu().numpy())
                text_calls += 1
                gpu_check(torch, approval)
            parity(text_features[0], text_features[1])
            logits = mean_cosine_logit(first, text_features[0], len(prompts["live"]))
            parity(logits, mean_cosine_logit(second, text_features[1], len(prompts["live"])))
            text_path, logit_path = NATIVE / "openclip-text.npy", NATIVE / "openclip-prompt-logits.npy"
            for path, value in ((text_path, text_features[0]), (logit_path, logits)):
                with path.open("xb") as handle:
                    np.save(handle, value, allow_pickle=False)
                if not np.array_equal(value, np.load(path, allow_pickle=False)):
                    raise ValueError("fixed prompt text/logit exact saved readback mismatch")
            result.update(text_sha256=digest(text_path), prompt_logits_sha256=digest(logit_path),
                          text_shape=list(text_features[0].shape), prompt_logits_shape=list(logits.shape),
                          prompts_sha256=digest(ROOT / "configs/prompts_core_v1.yaml"),
                          text_calls=2, class_scores_used_for_selection=False, calibrated=False)
        write_immutable_record(NATIVE / f"{name}-feature-manifest.json", result)
        all_results[name] = result
        del model, tensor
        if name.startswith("dino"):
            del output
        gc.collect()
        torch.cuda.empty_cache()
    enforce(approval)
    result = {"version": 1, "checkpoint": 295, "status": "technical_source_encoder_pilot_passed",
              "config_sha256": digest(CONFIG), "pilot_inputs_sha256": config["pilot_inputs_sha256"],
              "source_manifest_sha256": config["source_manifest_sha256"], "image_forward_calls": image_calls,
              "text_forward_calls": text_calls, "models": all_results, "acquisitions": acquisitions,
              "classifier_fits": 0, "calibration_fits": 0, "risk_fits": 0, "target_evaluation": False,
              "scientific_source_dry_run_complete": False, "scientific_readiness": False}
    write_immutable_record(NATIVE / "worker_completion.json", result)


def group_rss(group: int) -> int:
    total = 0
    for path in Path("/proc").iterdir():
        if not path.name.isdigit():
            continue
        try:
            stat = (path / "stat").read_text().rsplit(")", 1)[1].split()
            if int(stat[2]) == group:
                fields = (path / "status").read_text().splitlines()
                total += next(int(line.split()[1]) * 1024 for line in fields if line.startswith("VmRSS:"))
        except (FileNotFoundError, ProcessLookupError):
            continue
        except StopIteration:
            if stat[0] not in {"Z", "X"}:
                raise RuntimeError("live pilot process lacks measurable RSS")
    return total


def supervise() -> int:
    config, approval = authority()
    enforce(approval)
    write_immutable_record(APPROVAL_ROOT / "attempt_lock.json", {
        "supervisor_pid": os.getpid(), "config_sha256": digest(CONFIG),
        "script_sha256": digest(Path(__file__)), "feature_contract_sha256": digest(ROOT / "src/fas/frozen_features.py"),
        "automatic_retry": False})
    NATIVE.mkdir(parents=True, exist_ok=False)
    env = {**os.environ, "CUBLAS_WORKSPACE_CONFIG": ":4096:8", "HF_HUB_OFFLINE": "1"}
    child = subprocess.Popen([sys.executable, str(Path(__file__)), "--worker"],
                             start_new_session=True, env=env)
    failure, peak_rss, peak_bytes = None, 0, 0
    try:
        while child.poll() is None:
            enforce(approval)
            supervisor_rss = next(int(line.split()[1]) * 1024
                                  for line in Path(f"/proc/{os.getpid()}/status").read_text().splitlines()
                                  if line.startswith("VmRSS:"))
            rss = group_rss(child.pid) + supervisor_rss
            peak_rss, peak_bytes = max(peak_rss, rss), max(peak_bytes, size())
            if rss > approval["caps"]["rss_bytes"]:
                raise MemoryError("source295 combined process-tree8GiB RSS cap")
            time.sleep(0.5)
        if child.returncode:
            raise RuntimeError(f"source295 worker exit{child.returncode}; no automatic retry")
        enforce(approval, final=True)
    except (OSError, ValueError, RuntimeError, TimeoutError, MemoryError) as exc:
        failure = f"{type(exc).__name__}: {exc}"
        print("SOURCE295_STOP", failure, file=sys.stderr, flush=True)
    finally:
        if child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
    completed = read(NATIVE / "worker_completion.json") if failure is None else None
    result = {
        "version": 1, "checkpoint": 295, "failure": failure,
        "status": "technical_source_encoder_pilot_passed" if failure is None else "stopped_no_retry",
        "wall_seconds_from_original_approval": time.time() - approval["started_unix_seconds"],
        "sampled_peak_rss_bytes": peak_rss, "peak_new_temporary_bytes": max(peak_bytes, size()),
        "caps": approval["caps"], "automatic_retry": False,
        "config_sha256": digest(CONFIG), "worker_completion_sha256": digest(NATIVE / "worker_completion.json") if completed else None,
        "source_integration_complete": True, "scientific_source_dry_run_complete": False,
        "classifier_fits": 0, "target_evaluation": False, "scientific_readiness": False}
    write_immutable_record(APPROVAL_ROOT / "terminal.json", result)
    public = {**result, "models": {
        name: {key: value for key, value in row.items() if key not in {"rows", "feature_keys"}}
        for name, row in completed["models"].items()} if completed else {},
        "acquisitions": completed["acquisitions"] if completed else {}}
    write_immutable_record(ROOT / "results/phase1/source-encoder-pilot295-v1.json", public)
    print("SOURCE295_TERMINAL", json.dumps(result), flush=True)
    return 0 if failure is None else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        worker()
    else:
        raise SystemExit(supervise())
