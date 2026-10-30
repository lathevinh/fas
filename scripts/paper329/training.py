"""One fixed fit, source-only checkpoint selection and saved-model prediction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import torch

from augmentation import paired_batch
from model import check_gradients, losses, optimizer_for, tensor_images


@torch.no_grad()
def predict(model, rows: list[dict], load_rgb, device: str, guard) -> np.ndarray:
    model.eval()
    scores = []
    for offset in range(0, len(rows), 32):
        guard()
        images = np.stack([load_rgb(row) for row in rows[offset:offset+32]])
        global_logits, _, _ = model(tensor_images(images, device))
        score = global_logits[:, 1]-global_logits[:, 0]
        if not torch.isfinite(score).all():
            raise ValueError("nonfinite saved-model logits")
        scores.extend(score.cpu().double().tolist())
    return np.asarray(scores, dtype=np.float64)


def validation_loss(logits: np.ndarray, rows: list[dict]) -> float:
    if logits.shape != (len(rows),) or not np.isfinite(logits).all():
        raise ValueError("complete finite source-validation logits required")
    labels = np.asarray([row["binary_label"] == "attack" for row in rows], dtype=int)
    values = np.logaddexp(0., logits)-labels*logits
    terms = []
    for source in sorted({row["dataset"] for row in rows}):
        for label in (0, 1):
            mask = np.array([row["dataset"] == source for row in rows]) & (labels == label)
            if not mask.any():
                raise ValueError("source validation stratum missing")
            terms.append(float(values[mask].mean()))
    return float(np.mean(terms))


def fit(model, fitting: list[dict], validation: list[dict], load_rgb, augmenter,
        seed: int, tail: bool, device: str, guard, trace_path: Path) -> dict:
    optimizer = optimizer_for(model)
    steps = (len(fitting)+31)//32
    best_loss, best, selected, stale = float("inf"), None, 0, 0
    history, optimizer_steps = [], 0
    with trace_path.open("x") as stream:
        for epoch in range(1, 201):
            model.train()
            totals = {name: 0. for name in ("global", "APL", "hardest_attack", "total")}
            redraws = 0
            for step in range(steps):
                guard()
                batch = paired_batch(fitting, load_rgb, augmenter, seed, epoch, step)
                labels = torch.from_numpy(batch.labels).to(device)
                domains = torch.from_numpy(batch.domains).to(device)
                patch_labels = torch.from_numpy(batch.patch_labels).to(device)
                optimizer.zero_grad(set_to_none=True)
                values = losses(model(tensor_images(batch.images, device)),
                                labels, domains, patch_labels, tail=tail)
                values["total"].backward()
                check_gradients(model)
                optimizer.step()
                optimizer_steps += 1
                redraws += batch.trace["redraws"]
                for name, value in values.items():
                    totals[name] += value.item()
                stream.write(json.dumps({"epoch": epoch, "step": step, **batch.trace}, sort_keys=True)+"\n")
                stream.flush()
                guard()
            value = validation_loss(predict(model, validation, load_rgb, device, guard), validation)
            if not np.isfinite(value):
                raise ValueError("nonfinite source selection criterion")
            history.append({"epoch": epoch, "validation": value, "redraws": redraws,
                            "mean_training_losses": {name: total/steps for name, total in totals.items()}})
            if value < best_loss:
                best_loss, selected, stale = value, epoch, 0
                best = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            else:
                stale += 1
            print("PAD329_EPOCH", seed, "tail" if tail else "reference", json.dumps(history[-1]), flush=True)
            if stale >= 20:
                break
    if best is None:
        raise RuntimeError("no finite source-selected checkpoint")
    model.load_state_dict(best, strict=True)
    return {"state_dict": best, "history": history, "selected_epoch": selected,
            "validation_loss": best_loss, "optimizer_steps": optimizer_steps, "seed": seed,
            "tail": tail, "trace_sha256": hashlib.sha256(trace_path.read_bytes()).hexdigest()}


def validate_state(state: dict, fitting_count: int, seed: int, tail: bool) -> None:
    history = state["history"]
    values = [item["validation"] for item in history]
    if (not history or len(history) > 200 or not np.isfinite(values).all()
            or [item["epoch"] for item in history] != list(range(1, len(history)+1))
            or state["seed"] != seed or state["tail"] is not tail
            or state["optimizer_steps"] != len(history)*((fitting_count+31)//32)
            or state["selected_epoch"] != int(np.argmin(values))+1
            or state["validation_loss"] != min(values)):
        raise ValueError("checkpoint history/selection/step inventory mismatch")
    best, stale = float("inf"), 0
    for i, value in enumerate(values):
        stale = 0 if value < best else stale+1
        best = min(best, value)
        if stale >= 20 and i != len(values)-1:
            raise ValueError("training continued beyond patience")
    if len(history) < 200 and stale != 20:
        raise ValueError("shortened recipe is not successful early stopping")
