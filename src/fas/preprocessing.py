"""Deterministic five-point face alignment for the frozen preprocessing policy."""

from __future__ import annotations

import cv2
import numpy as np


REFERENCE_112 = np.array([[38.2946, 51.6963], [73.5318, 51.5014],
                          [56.0252, 71.7366], [41.5493, 92.3655],
                          [70.7299, 92.2041]], dtype=np.float64)


def alignment_matrix(landmarks: np.ndarray, resolution: int, context_scale: float = 1.30) -> np.ndarray:
    points = np.asarray(landmarks, dtype=np.float64)
    if points.shape != (5, 2) or not np.isfinite(points).all():
        raise ValueError("five finite facial landmarks required")
    if type(resolution) is not int or resolution < 1 or context_scale != 1.30:
        raise ValueError("positive resolution and frozen context scale required")
    target = (REFERENCE_112 / 112.0 - 0.5) * resolution / context_scale + resolution / 2.0
    centered = points - points.mean(axis=0)
    target_centered = target - target.mean(axis=0)
    variance = np.sum(centered ** 2)
    if variance <= np.finfo(np.float64).eps:
        raise ValueError("degenerate facial landmarks")
    left, singular, right = np.linalg.svd(centered.T @ target_centered)
    correction = np.ones(2)
    correction[-1] = np.sign(np.linalg.det(left @ right))
    rotation = left @ np.diag(correction) @ right
    scale = np.sum(singular * correction) / variance
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError("invalid similarity transform")
    linear = scale * rotation.T
    return np.column_stack((linear, target.mean(axis=0) - linear @ points.mean(axis=0)))


def align_face(rgb: np.ndarray, landmarks: np.ndarray, resolution: int) -> tuple[np.ndarray, np.ndarray]:
    if rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[2] != 3 or min(rgb.shape[:2]) < 1:
        raise ValueError("nonempty uint8 RGB image required")
    matrix = alignment_matrix(landmarks, resolution)
    crop = cv2.warpAffine(rgb, matrix, (resolution, resolution), flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    return crop, matrix


def shared_context_crop(rgb: np.ndarray, box: np.ndarray, landmarks: np.ndarray) -> tuple[np.ndarray, dict]:
    if rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError("uint8 RGB image required")
    bounds = np.asarray(box, dtype=np.float64)
    if bounds.shape != (4,) or not np.isfinite(bounds).all() or np.any(bounds[2:] <= bounds[:2]):
        raise ValueError("positive finite face box required")
    fitted = alignment_matrix(landmarks, 112)
    rotation = fitted[:, :2] / np.linalg.norm(fitted[:, 0])
    eye_center = np.asarray(landmarks, dtype=np.float64)[:2].mean(axis=0)
    matrix = np.column_stack((rotation, eye_center - rotation @ eye_center))
    corners = np.array([[bounds[0], bounds[1]], [bounds[2], bounds[1]],
                        [bounds[2], bounds[3]], [bounds[0], bounds[3]]])
    transformed = corners @ rotation.T + matrix[:, 2]
    low, high = transformed.min(axis=0), transformed.max(axis=0)
    center, half = (low + high) / 2.0, (high - low) * 1.30 / 2.0
    height, width = rgb.shape[:2]
    lower = np.maximum(np.floor(center - half).astype(int), [0, 0])
    upper = np.minimum(np.ceil(center + half).astype(int), [width, height])
    if np.any(upper <= lower):
        raise ValueError("face context outside image")
    aligned = cv2.warpAffine(rgb, matrix, (width, height), flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    crop = np.ascontiguousarray(aligned[lower[1]:upper[1], lower[0]:upper[0]])
    return crop, {"alignment_matrix": matrix.tolist(), "context_scale": 1.30,
                  "crop_xyxy_half_open": [*lower.tolist(), *upper.tolist()],
                  "alignment": "five_point_similarity_rotation_about_eye_midpoint",
                  "border": "constant_zero", "interpolation": "bicubic"}


def decode_scrfd(outputs: list[np.ndarray], scale: float) -> tuple[np.ndarray, np.ndarray]:
    if len(outputs) != 9 or not np.isfinite(scale) or scale <= 0:
        raise ValueError("three-stride SCRFD keypoint outputs required")
    boxes, landmarks = [], []
    for index, stride in enumerate((8, 16, 32)):
        scores = np.asarray(outputs[index]).reshape(-1)
        distances = np.asarray(outputs[index + 3])
        offsets = np.asarray(outputs[index + 6])
        count = 2 * (640 // stride) ** 2
        if (scores.shape != (count,) or distances.shape != (count, 4) or offsets.shape != (count, 10)
                or not all(np.isfinite(value).all() for value in (scores, distances, offsets))):
            raise ValueError("SCRFD output shape or finite-value mismatch")
        centers = np.stack(np.mgrid[:640 // stride, :640 // stride][::-1], axis=-1).reshape(-1, 2) * stride
        centers = np.repeat(centers, 2, axis=0)
        selected = np.flatnonzero(scores >= 0.5)
        centers = centers[selected]
        distances = distances[selected] * stride
        coordinates = np.column_stack((centers - distances[:, :2], centers + distances[:, 2:])) / scale
        boxes.append(np.column_stack((coordinates, scores[selected])))
        landmarks.append((offsets[selected].reshape(-1, 5, 2) * stride + centers[:, None, :]) / scale)
    candidates, points = np.vstack(boxes), np.concatenate(landmarks)
    order = np.argsort(-candidates[:, 4], kind="stable")
    retained = []
    while order.size:
        chosen = int(order[0])
        retained.append(chosen)
        others = order[1:]
        low = np.maximum(candidates[chosen, :2], candidates[others, :2])
        high = np.minimum(candidates[chosen, 2:4], candidates[others, 2:4])
        intersection = np.prod(np.maximum(high - low + 1, 0), axis=1)
        areas = np.prod(candidates[:, 2:4] - candidates[:, :2] + 1, axis=1)
        overlap = intersection / np.maximum(areas[chosen] + areas[others] - intersection, 1e-12)
        order = others[overlap <= 0.4]
    return candidates[retained], points[retained]


def detect_face(session, rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    height, width = rgb.shape[:2]
    resized_height = 640 if height >= width else int(640 * height / width)
    resized_width = 640 if width >= height else int(640 * width / height)
    canvas = np.zeros((640, 640, 3), dtype=np.uint8)
    canvas[:resized_height, :resized_width] = cv2.resize(rgb, (resized_width, resized_height))
    blob = cv2.dnn.blobFromImage(canvas, 1.0 / 128.0, (640, 640), (127.5,) * 3, swapRB=False)
    outputs = session.run(None, {session.get_inputs()[0].name: blob})
    boxes, points = decode_scrfd(outputs, resized_height / height)
    if not len(boxes):
        raise ValueError("no_face_above_frozen_threshold")
    selected = min(range(len(boxes)), key=lambda index: (
        -float(np.prod(boxes[index, 2:4] - boxes[index, :2])),
        -float(boxes[index, 4]), *boxes[index, :4].tolist()))
    return boxes[selected], points[selected]