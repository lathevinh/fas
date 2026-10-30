"""Bounded full-reference synthetic fit/attention/checkpoint/replay benchmark."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
import time

import numpy as np
import torch

from augmentation import FAMILIES, FASAug, background, blue, moire, paired_batch
from model import (CHECKPOINT, Reference, check_gradients, configure, losses,
                   optimizer_for, tensor_images)
import assets

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"src"))
from fas.feature_cache import digest
from fas.freeze import write_immutable_record
from fas.source_fitting import calibrate, fit_calibrator

DEFAULT = ROOT/"results/phase1/dino329-integrated-probe-v2.json"
GIB = 1024**3


def main(output: Path) -> None:
    if output.exists():
        raise FileExistsError("immutable integrated probe receipt already exists")
    started = time.monotonic()
    caps = {"wall_seconds": 600, "GPU_bytes": 12*GIB, "RSS_bytes": 6*GIB,
            "temporary_bytes": 2*GIB, "warmup_steps_per_arm": 2, "measured_steps_per_arm": 3}
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA required; no feasibility-shaped CPU fallback")
    torch.cuda.set_per_process_memory_fraction(caps["GPU_bytes"]/torch.cuda.get_device_properties(0).total_memory)
    def guard():
        if time.monotonic()-started >= caps["wall_seconds"]:
            raise TimeoutError("integrated synthetic probe ceiling")
        rss = sum(resource.getrusage(who).ru_maxrss for who in (resource.RUSAGE_SELF, resource.RUSAGE_CHILDREN))*1024
        if rss > caps["RSS_bytes"]:
            raise MemoryError("integrated synthetic RSS cap")
        if torch.cuda.max_memory_reserved() > caps["GPU_bytes"]:
            raise MemoryError("integrated synthetic GPU cap")
    augmenter = FASAug()
    rows = [{"dataset": source, "binary_label": label, "index": i}
            for i, (source, label) in enumerate((source, label)
                for source in ("A", "B", "C") for label in ("bona_fide", "attack"))]
    random = np.random.default_rng(329)
    images = random.integers(0, 256, (6, 224, 224, 3), dtype=np.uint8)
    load = lambda row: images[row["index"]].copy()
    # Force every family once; ordinary steps below use the exact proposed p=0.2.
    family_checks = {}
    for i, family in enumerate(FAMILIES):
        transformed, label, _ = augmenter.apply(images[0], 0, np.random.default_rng(i), family)
        family_checks[family] = {"output_sha256": hashlib.sha256(transformed.tobytes()).hexdigest(),
                                "attack_label": label}
    results, initial, paired_traces = [], None, []
    with tempfile.TemporaryDirectory(prefix="fas329-probe-") as directory:
        folder = Path(directory)
        for arm in ("reference", "reference_plus_tail"):
            for cache in (background, blue, moire):
                cache.cache_clear()
            augmenter = FASAug()
            configure(20260917)
            model = Reference().cuda().train()
            optimizer = optimizer_for(model)
            fingerprint = hashlib.sha256()
            for value in model.state_dict().values():
                fingerprint.update(value.detach().cpu().numpy().tobytes())
            fingerprint = fingerprint.hexdigest()
            if initial is not None and initial != fingerprint:
                raise ValueError("paired model initialization differs")
            initial = fingerprint
            torch.cuda.reset_peak_memory_stats()
            timings, logs, traces = [], [], []
            for step in range(5):
                guard()
                torch.cuda.synchronize()
                begun = time.monotonic()
                batch = paired_batch(rows, load, augmenter, 20260917, 1, step)
                traces.append(batch.trace)
                labels = torch.from_numpy(batch.labels).cuda()
                domains = torch.from_numpy(batch.domains).cuda()
                patches = torch.from_numpy(batch.patch_labels).cuda()
                optimizer.zero_grad(set_to_none=True)
                outputs = model(tensor_images(batch.images, "cuda"))
                values = losses(outputs, labels, domains, patches, tail=arm.endswith("tail"))
                values["total"].backward()
                check_gradients(model)
                optimizer.step()
                torch.cuda.synchronize()
                if step >= 2:
                    timings.append(time.monotonic()-begun)
                    logs.append({key: value.item() for key, value in values.items()})
            guard()
            model.eval()
            validation_started = time.monotonic()
            with torch.no_grad():
                baseline = model(tensor_images(images, "cuda"))[0].cpu()
            torch.cuda.synchronize()
            validation_seconds = time.monotonic()-validation_started
            checkpoint = folder/f"{arm}.pth"
            save_started = time.monotonic()
            with checkpoint.open("xb") as stream:
                torch.save({"state_dict": model.state_dict()}, stream)
            save_seconds = time.monotonic()-save_started
            if sum(path.stat().st_size for path in folder.iterdir()) > caps["temporary_bytes"]:
                raise MemoryError("integrated synthetic checkpoint cap")
            allocated, reserved = torch.cuda.max_memory_allocated(), torch.cuda.max_memory_reserved()
            del optimizer, values, outputs, model
            gc.collect()
            torch.cuda.empty_cache()
            replay_started = time.monotonic()
            restored = Reference(initialize=False).cuda().eval()
            restored.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True)["state_dict"])
            with torch.no_grad():
                replay = restored(tensor_images(images, "cuda"))[0].cpu()
            torch.testing.assert_close(baseline, replay, rtol=0, atol=0)
            replay_seconds = time.monotonic()-replay_started
            independent_started = time.monotonic()
            completed = subprocess.run(
                [sys.executable, str(Path(__file__)), "--synthetic-replay", str(checkpoint),
                 "--checkpoint-sha256", digest(checkpoint)],
                capture_output=True, text=True, timeout=90, env={
                    **os.environ, "XFORMERS_DISABLED": "1", "CUBLAS_WORKSPACE_CONFIG": ":4096:8"})
            if completed.returncode:
                raise RuntimeError(f"independent synthetic replay failed: {completed.stderr}")
            independent = torch.tensor(json.loads(completed.stdout)["logits"], dtype=replay.dtype)
            torch.testing.assert_close(baseline, independent, rtol=0, atol=0)
            independent_seconds = time.monotonic()-independent_started
            raw = (replay[:, 1]-replay[:, 0]).double().numpy()
            calibration_started = time.monotonic()
            calibrator = fit_calibrator(raw, np.array([0, 1]*3), ["A", "A", "B", "B", "C", "C"], guard)
            if not np.isfinite(calibrate(calibrator, raw)).all():
                raise ValueError("nonfinite synthetic calibration")
            results.append({"arm": arm, "step_seconds": timings, "losses": logs,
                            "mean_step_seconds": sum(timings)/len(timings),
                            "validation_seconds": validation_seconds, "save_seconds": save_seconds,
                            "replay_seconds": replay_seconds,
                            "independent_process_replay_seconds": independent_seconds,
                            "calibration_seconds": time.monotonic()-calibration_started,
                            "checkpoint_bytes": checkpoint.stat().st_size,
                            "peak_allocated": allocated, "peak_reserved": reserved,
                            "initial_state_sha256": fingerprint})
            paired_traces.append(traces)
            del restored
            gc.collect()
            torch.cuda.empty_cache()
    if paired_traces[0] != paired_traces[1]:
        raise ValueError("paired synthetic data/donor/mask/redraw mismatch")
    guard()
    record = {"status": "complete", "scope": "integrated_independent_reference_synthetic_not_PAD_accuracy",
              "caps": caps, "results": results, "family_checks": family_checks,
              "paired_batch_traces": paired_traces[0], "checkpoint_reconstruction_verified": True,
              "actual_attention": "final_qkv_hook_CLS_plus4registers_plus256patches_detached_normalized",
              "precision": "FP32_no_AMP_no_TF32_seeded_not_bitwise_deterministic",
              "checkpoint_sha256": digest(CHECKPOINT), "asset_receipt": assets.verify(),
              "implementation_sha256": {str(path.relative_to(ROOT)): digest(path)
                                        for path in Path(__file__).parent.glob("*.py")},
              "objective_sha256": digest(ROOT/"scripts/paper327/objective.py"),
              "wall_seconds": time.monotonic()-started,
              "peak_process_RSS": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
              "conservative_parent_plus_child_peak_RSS": sum(resource.getrusage(who).ru_maxrss
                  for who in (resource.RUSAGE_SELF, resource.RUSAGE_CHILDREN))*1024,
              "synthetic_optimizer_steps": 10, "dataset_image_reads": 0,
              "scientific_training_starts": 0, "target_evaluations": 0,
              "saved_trained_checkpoints_retained": 0, "scientific_execution_authorized": False,
              "excluded_costs": ["real_image_IO", "full_epochs", "full_validation_calibration_population",
                                 "all_target_predictions", "full_cluster_bootstrap"],
              "python": sys.version, "torch": torch.__version__, "gpu": torch.cuda.get_device_name(0)}
    write_immutable_record(output, record)
    print("PAD329_INTEGRATED_PROBE", json.dumps(record["results"]), flush=True)


def synthetic_replay(checkpoint: Path, expected: str) -> None:
    if not checkpoint.parent.name.startswith("fas329-probe-") or digest(checkpoint) != expected:
        raise ValueError("bound synthetic-only temporary checkpoint required")
    configure(20260917)
    torch.cuda.set_per_process_memory_fraction(12*GIB/torch.cuda.get_device_properties(0).total_memory)
    images = np.random.default_rng(329).integers(0, 256, (6, 224, 224, 3), dtype=np.uint8)
    model = Reference(initialize=False).cuda().eval()
    model.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True)["state_dict"])
    with torch.no_grad():
        logits = model(tensor_images(images, "cuda"))[0].cpu().tolist()
    print(json.dumps({"logits": logits}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT)
    parser.add_argument("--synthetic-replay", type=Path)
    parser.add_argument("--checkpoint-sha256")
    args = parser.parse_args()
    if args.synthetic_replay:
        synthetic_replay(args.synthetic_replay, args.checkpoint_sha256)
    else:
        main(args.output)
