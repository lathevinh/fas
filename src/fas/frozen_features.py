"""Frozen encoder input, pooling, cache and parity contracts."""

from __future__ import annotations

import hashlib
import json

import numpy as np


def normalize_rgb(rgb: np.ndarray, resolution: int, mean: tuple, std: tuple) -> np.ndarray:
    if rgb.dtype != np.uint8 or rgb.shape != (resolution, resolution, 3):
        raise ValueError("existing native-resolution uint8 RGB crop required; no resizing")
    if len(mean) != 3 or len(std) != 3 or any(value <= 0 for value in std):
        raise ValueError("three-channel checkpoint-native normalization required")
    scaled = rgb.astype(np.float32) / np.float32(255)
    return np.ascontiguousarray(
        ((scaled - np.asarray(mean, dtype=np.float32)) / np.asarray(std, dtype=np.float32)).transpose(2, 0, 1))


def dino_pool(cls: np.ndarray, patches: np.ndarray) -> np.ndarray:
    if (cls.shape != (1, 768) or patches.shape != (1, 1369, 768)
            or cls.dtype != np.float32 or patches.dtype != np.float32
            or not np.isfinite(cls).all() or not np.isfinite(patches).all()):
        raise ValueError("native518 DINO CLS and patch-only FP32 tensors required")
    return np.concatenate((cls, patches.mean(axis=1)), axis=1)


def feature_key(
    *, dataset: str, video_id: str, crop_sha256: str, checkpoint_sha256: str,
    preprocessing_sha256: str, representation: str,
) -> str:
    values = (crop_sha256, checkpoint_sha256, preprocessing_sha256)
    if any(len(value) != 64 or any(c not in "0123456789abcdef" for c in value) for value in values):
        raise ValueError("cache key requires exact crop/checkpoint/preprocessing SHA256")
    payload = {"dataset": dataset, "video_id": video_id, "crop_sha256": crop_sha256,
               "checkpoint_sha256": checkpoint_sha256, "preprocessing_sha256": preprocessing_sha256,
               "representation": representation, "dtype": "float32"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def check_feature(value: np.ndarray, count: int, dimension: int) -> None:
    if value.shape != (count, dimension) or value.dtype != np.float32 or not np.isfinite(value).all():
        raise ValueError("feature shard must have exact sample/feature shape, finite FP32 values")


def parity(first: np.ndarray, second: np.ndarray, *, rtol: float = 1e-5, atol: float = 1e-6) -> float:
    if (first.shape != second.shape or first.dtype != np.float32 or second.dtype != np.float32
            or not np.isfinite(first).all() or not np.isfinite(second).all()
            or not np.allclose(first, second, rtol=rtol, atol=atol)):
        raise ValueError("frozen encoder repeated extraction parity failed")
    return float(np.max(np.abs(first - second)))


def mean_cosine_logit(images: np.ndarray, text: np.ndarray, live_count: int) -> np.ndarray:
    if (images.ndim != 2 or text.ndim != 2 or images.shape[1] != text.shape[1]
            or not 0 < live_count < len(text) or not np.isfinite(images).all() or not np.isfinite(text).all()):
        raise ValueError("finite image/text features and fixed live/spoof prompts required")
    image_norm, text_norm = np.linalg.norm(images, axis=1, keepdims=True), np.linalg.norm(text, axis=1, keepdims=True)
    if np.any(image_norm == 0) or np.any(text_norm == 0):
        raise ValueError("zero image/text features cannot define cosine logits")
    cosine = (images / image_norm) @ (text / text_norm).T
    return (cosine[:, live_count:].mean(axis=1) - cosine[:, :live_count].mean(axis=1)).astype(np.float32)
