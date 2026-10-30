"""Bounded synthetic full-DINO backward probe, not a Feng baseline reproduction."""

from __future__ import annotations

import gc
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time

import torch
from torch import nn
from torch.nn.functional import binary_cross_entropy_with_logits

from objective import attack_tail_ranking

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = Path.home()/".cache/fas/upstream/dinov2-7764ea0"
CHECKPOINT = Path.home()/".cache/fas/source-pilot295-v1/checkpoints/dino_reg.pth"
OUTPUT = ROOT/"results/phase1/dino327-synthetic-probe-v1.json"
GIB = 1024**3


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError("immutable engineering probe receipt already exists")
    started = time.monotonic()
    caps = {"wall_seconds": 300, "own_cuda_bytes": 12*GIB, "process_rss_bytes": 6*GIB,
            "batch_size": 32, "warmup_steps_per_arm": 2, "measured_steps_per_arm": 3}
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA required for the declared engineering probe")
    torch.set_num_threads(2)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(False)
    torch.cuda.set_per_process_memory_fraction(caps["own_cuda_bytes"]/torch.cuda.get_device_properties(0).total_memory)
    sys.path.insert(0, str(UPSTREAM))
    from dinov2.hub import backbones
    sys.path.insert(0, str(ROOT/"src"))
    from fas.environment import verify_source_checkout
    verify_source_checkout(UPSTREAM, "7764ea0f912e53c92e82eb78a2a1631e92725fc8")
    original = json.loads((Path("/mnt/e/FAS-private/artifacts/phase1/source_run297_v1/extraction.json")).read_text())
    checkpoint_sha = sha(CHECKPOINT)
    if checkpoint_sha != original["dino_reg"]["checkpoint_sha256"]:
        raise ValueError("originally verified DINO-Reg checkpoint required")
    def guard():
        if time.monotonic()-started > caps["wall_seconds"]:
            raise TimeoutError("synthetic engineering probe wall ceiling")
        if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024 > caps["process_rss_bytes"]:
            raise MemoryError("synthetic engineering probe RSS ceiling")
        if max(torch.cuda.max_memory_reserved(), torch.cuda.max_memory_allocated()) > caps["own_cuda_bytes"]:
            raise MemoryError("synthetic engineering probe CUDA ceiling")
    results = []
    for arm in ("global_BCE_proxy", "global_BCE_plus_tail_proxy"):
        guard()
        torch.manual_seed(20260917)
        torch.cuda.manual_seed_all(20260917)
        backbone = backbones.dinov2_vitb14_reg(pretrained=False)
        backbone.load_state_dict(torch.load(CHECKPOINT, map_location="cpu", weights_only=True), strict=True)
        backbone = backbone.cuda().train()
        head = nn.Linear(768, 1).cuda()
        optimizer = torch.optim.AdamW([
            {"params": backbone.parameters(), "lr": 5e-6},
            {"params": head.parameters(), "lr": 5e-5}], weight_decay=.05)
        generator = torch.Generator().manual_seed(327)
        images = torch.randn(caps["batch_size"], 3, 224, 224, generator=generator).cuda()
        domains = (torch.arange(caps["batch_size"], device="cuda") % 3).long()
        labels = (torch.arange(caps["batch_size"], device="cuda") % 2).long()
        torch.cuda.reset_peak_memory_stats()
        times, losses = [], []
        for step in range(caps["warmup_steps_per_arm"]+caps["measured_steps_per_arm"]):
            guard()
            torch.cuda.synchronize()
            begun = time.monotonic()
            optimizer.zero_grad(set_to_none=True)
            outputs = backbone.forward_features(images)
            logits = head(outputs["x_norm_clstoken"]).flatten()
            loss = binary_cross_entropy_with_logits(logits, labels.float())
            if arm == "global_BCE_plus_tail_proxy":
                loss = loss + .1*attack_tail_ranking(logits, labels, domains)
            if not torch.isfinite(loss):
                raise ValueError("nonfinite synthetic loss")
            loss.backward()
            if (backbone.blocks[0].attn.qkv.weight.grad is None
                    or not torch.isfinite(backbone.blocks[0].attn.qkv.weight.grad).all()
                    or backbone.blocks[0].attn.qkv.weight.grad.abs().sum() == 0):
                raise ValueError("finite nonzero full-backbone gradient required")
            optimizer.step()
            torch.cuda.synchronize()
            elapsed = time.monotonic()-begun
            guard()
            if step >= caps["warmup_steps_per_arm"]:
                times.append(elapsed)
                losses.append(loss.item())
        results.append({
            "arm": arm, "step_seconds": times, "measured_losses": losses,
            "mean_step_seconds": sum(times)/len(times),
            "cuda_peak_allocated": torch.cuda.max_memory_allocated(),
            "cuda_peak_reserved": torch.cuda.max_memory_reserved(),
            "trainable_backbone_parameters": sum(p.numel() for p in backbone.parameters() if p.requires_grad),
            "trainable_head_parameters": sum(p.numel() for p in head.parameters()),
            "finite_full_backbone_gradient_observed": True})
        print("DINO327_SYNTHETIC_ARM", json.dumps(results[-1]), flush=True)
        del optimizer, loss, logits, outputs, images, labels, domains, backbone, head
        gc.collect()
        torch.cuda.empty_cache()
    result = {
        "version": 1, "scope": "synthetic_backbone_capacity_not_published_PAD_baseline",
        "interpreter": sys.executable, "torch": torch.__version__, "gpu": torch.cuda.get_device_name(0),
        "checkpoint_sha256": checkpoint_sha,
        "upstream_commit": "7764ea0f912e53c92e82eb78a2a1631e92725fc8",
        "code_sha256": {p.name: sha(p) for p in (Path(__file__), Path(__file__).with_name("objective.py"))},
        "caps": caps, "results": results, "wall_seconds": time.monotonic()-started,
        "peak_process_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
        "scientific_training_starts": 0, "dataset_image_reads": 0, "target_evaluations": 0,
        "synthetic_optimizer_steps": 10, "saved_trained_checkpoints": 0,
        "precision": "FP32_no_AMP_no_TF32_seeded_not_bitwise_deterministic",
        "excluded_costs": ["FAS-Aug", "PDA", "APL_attention_weights", "real_image_IO",
                           "validation", "calibration", "checkpoint_replay", "bootstrap"],
        "scientific_execution_authorized": False}
    from fas.freeze import write_immutable_record
    write_immutable_record(OUTPUT, result)
    print("DINO327_SYNTHETIC_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
