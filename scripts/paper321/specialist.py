# SPDX-License-Identifier: GPL-3.0-only
"""DeepPixBiS architecture retraining; see NOTICE and COPYING in this directory."""

from __future__ import annotations

import random
import re

import numpy as np
import torch
from torch import nn
from torchvision.models import densenet161


class Specialist(nn.Module):
    def __init__(self, initial_state: dict | None = None):
        super().__init__()
        backbone = densenet161(weights=None)
        if initial_state is not None:
            compatible = {}
            for key, value in initial_state.items():
                modern = re.sub(r"(\.denselayer[0-9]+\.(?:norm|relu|conv))\.([12])\.", r"\1\2.", key)
                if modern in compatible:
                    raise ValueError("colliding legacy and modern DenseNet initialization keys")
                compatible[modern] = value
            backbone.load_state_dict(compatible, strict=True)
        self.encoder = nn.Sequential(*list(backbone.features.children())[:8])
        self.pixel = nn.Conv2d(384, 1, kernel_size=1)
        self.global_head = nn.Linear(196, 1)

    def forward(self, images: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        if images.ndim != 4 or images.shape[1:] != (3, 224, 224):
            raise ValueError("native RGB224 image batches required")
        pixel_logits = self.pixel(self.encoder(images))
        global_logits = self.global_head(pixel_logits.sigmoid().flatten(1))
        return pixel_logits, global_logits


def configure(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cuda.matmul.allow_tf32 = False


def losses(outputs: tuple[torch.Tensor, torch.Tensor], bona_fide: torch.Tensor) -> torch.Tensor:
    pixel, global_logits = outputs
    target = bona_fide.reshape(-1, 1, 1, 1).expand_as(pixel)
    per_pixel = nn.functional.binary_cross_entropy_with_logits(pixel, target, reduction="none").flatten(1).mean(1)
    per_global = nn.functional.binary_cross_entropy_with_logits(
        global_logits.flatten(), bona_fide, reduction="none")
    return (per_pixel + per_global) / 2


def attack_scores(outputs: tuple[torch.Tensor, torch.Tensor]) -> torch.Tensor:
    return 1 - outputs[0].sigmoid().mean(dim=(1, 2, 3))


def train_model(model, fitting: list[dict], validation: list[dict], image_batch,
                seed: int, settings: dict, device: str, guard) -> dict:
    from fas.source_fitting import objective_weights
    configure(seed)
    model.to(device)
    labels = np.asarray([row["binary_label"] == "attack" for row in fitting], dtype=int)
    probabilities = torch.as_tensor(objective_weights(
        labels, [row["dataset"] for row in fitting], balanced=True), dtype=torch.double)
    validation_y = np.asarray([row["binary_label"] == "attack" for row in validation], dtype=int)
    validation_weights = objective_weights(
        validation_y, [row["dataset"] for row in validation], balanced=True)
    sampler = torch.Generator().manual_seed(seed + 1)
    augmentation = torch.Generator().manual_seed(seed + 2)
    optimizer = torch.optim.Adam(
        model.parameters(), lr=settings["learning_rate"], betas=tuple(settings["betas"]),
        eps=settings["epsilon"], weight_decay=settings["weight_decay"])
    best_loss, best_epoch, best_state = float("inf"), 0, None
    history, steps = [], 0
    for epoch in range(1, settings["epochs"] + 1):
        model.train()
        selected = torch.multinomial(probabilities, len(fitting), replacement=True, generator=sampler).tolist()
        for start in range(0, len(selected), settings["batch_size"]):
            guard()
            chosen = [fitting[index] for index in selected[start:start + settings["batch_size"]]]
            images = image_batch(chosen, device, augmentation)
            targets = torch.tensor([row["binary_label"] == "bona_fide" for row in chosen],
                                   dtype=torch.float32, device=device)
            optimizer.zero_grad(set_to_none=True)
            loss = losses(model(images), targets).mean()
            if not torch.isfinite(loss):
                raise ValueError("nonfinite specialist training loss")
            loss.backward()
            if any(parameter.grad is not None and not torch.isfinite(parameter.grad).all()
                   for parameter in model.parameters()):
                raise ValueError("nonfinite specialist gradient")
            optimizer.step()
            steps += 1
            guard()
        model.eval()
        total = 0.0
        with torch.inference_mode():
            for start in range(0, len(validation), settings["batch_size"]):
                guard()
                chosen = validation[start:start + settings["batch_size"]]
                images = image_batch(chosen, device, None)
                targets = torch.tensor([row["binary_label"] == "bona_fide" for row in chosen],
                                       dtype=torch.float32, device=device)
                values = losses(model(images), targets).cpu().numpy()
                total += float(values @ validation_weights[start:start + len(chosen)])
        if not np.isfinite(total):
            raise ValueError("nonfinite specialist validation loss")
        if any(not torch.isfinite(value).all() for value in model.state_dict().values()):
            raise ValueError("nonfinite specialist parameters or running state")
        history.append(total)
        if total < best_loss:
            best_loss, best_epoch = total, epoch
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
        print("SPECIALIST_EPOCH", seed, epoch, total, flush=True)
    if best_state is None:
        raise RuntimeError("no finite specialist checkpoint")
    model.load_state_dict(best_state, strict=True)
    model.eval()
    return {"selected_epoch": best_epoch, "validation_loss": best_loss, "history": history,
            "optimizer_steps": steps, "seed": seed, "state_dict": best_state}


def predict(model, rows: list[dict], image_batch, device: str, guard) -> np.ndarray:
    model.eval()
    result = []
    with torch.inference_mode():
        for start in range(0, len(rows), 16):
            guard()
            result.extend(attack_scores(model(image_batch(rows[start:start + 16], device, None))).cpu().tolist())
    values = np.asarray(result, dtype=np.float64)
    if not np.isfinite(values).all() or np.any((values < 0) | (values > 1)):
        raise ValueError("finite specialist attack probabilities required")
    return values
