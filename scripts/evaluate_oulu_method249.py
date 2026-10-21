"""Synthetic-only controls for the proposed finite temporal method."""

from __future__ import annotations

import argparse
import hashlib
import resource
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cv2
import numpy as np

from fas.content_correspondence import PARAMETERS, compare_features, sequence_features
from fas.freeze import write_immutable_record


TRANSFORMS = ("identity", "translation16_12", "scale0.8", "rotation6",
              "crop75percent", "brightness0.8_plus12", "JPEG60", "delay1")


def scene(seed: int, background_seed: int | None = None, *, static: bool = False) -> list[np.ndarray]:
    generator = np.random.default_rng(seed)
    background = np.random.default_rng(seed + 9000 if background_seed is None else background_seed)
    base = cv2.GaussianBlur(background.integers(0, 256, (384, 256, 3), dtype=np.uint8), (3, 3), 0)
    patch = cv2.GaussianBlur(generator.integers(0, 256, (128, 112, 3), dtype=np.uint8), (3, 3), 0)
    frames = []
    for slot in range(9):
        rgb = base.copy()
        left = 48 + (0 if static else 3 * slot)
        top = 96 + (0 if static else 2 * slot)
        rgb[top:top + 128, left:left + 112] = patch
        frames.append(rgb)
    return frames


def transform(frames: list[np.ndarray], name: str) -> list[np.ndarray]:
    if name not in TRANSFORMS:
        raise ValueError("undeclared synthetic transformation")
    if name == "delay1":
        return [frames[0].copy()] + [frame.copy() for frame in frames[:-1]]
    result = []
    for rgb in frames:
        if name == "identity":
            changed = rgb.copy()
        elif name == "translation16_12":
            changed = cv2.warpAffine(rgb, np.array([[1, 0, 16], [0, 1, 12]], np.float32), (256, 384))
        elif name in ("scale0.8", "rotation6"):
            matrix = cv2.getRotationMatrix2D((128, 192), 6 if name == "rotation6" else 0, 0.8 if name == "scale0.8" else 1)
            changed = cv2.warpAffine(rgb, matrix, (256, 384))
        elif name == "crop75percent":
            changed = cv2.resize(rgb[48:336, 32:224], (256, 384), interpolation=cv2.INTER_LINEAR)
        elif name == "brightness0.8_plus12":
            changed = np.clip(rgb.astype(np.float32) * 0.8 + 12, 0, 255).astype(np.uint8)
        else:
            success, encoded = cv2.imencode(".jpg", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 60])
            if not success:
                raise ValueError("synthetic JPEG encoding failed")
            changed = cv2.cvtColor(cv2.imdecode(encoded, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
        result.append(changed)
    return result


def measure() -> dict:
    started = time.monotonic()
    rows = []
    features_seconds = []
    comparisons_seconds = []

    def features(frames):
        before = time.monotonic()
        result = sequence_features(frames)
        features_seconds.append(time.monotonic() - before)
        return result

    for group, seeds in (("development", range(100, 108)), ("held_out", range(200, 208))):
        for seed in seeds:
            frames = scene(seed)
            left = features(frames)
            cases = [(name, "positive", transform(frames, name), left) for name in TRANSFORMS]
            cases += [("independent", "negative", scene(seed + 10000), left),
                      ("shared_static_background", "negative", scene(seed + 10000, seed + 9000), left)]
            static = scene(seed, static=True)
            cases += [("static_identical", "outside_claim", static, features(static)),
                      ("dark_identical", "outside_claim", [np.zeros_like(frame) for frame in frames],
                       features([np.zeros_like(frame) for frame in frames]))]
            for name, label, right_frames, first in cases:
                if time.monotonic() - started > 900:
                    raise TimeoutError("synthetic control budget exceeded")
                right = features(right_frames)
                before = time.monotonic()
                result = compare_features(first, right)
                duration = time.monotonic() - before
                comparisons_seconds.append(duration)
                rows.append({"group": group, "seed": seed, "case": name, "expected": label,
                             "left_RGB_sha256": [value["rgb_sha256"] for value in first],
                             "right_RGB_sha256": [value["rgb_sha256"] for value in right],
                             "comparison_seconds": duration, **result})
    summaries = {}
    for group in ("development", "held_out"):
        summaries[group] = {}
        for name in TRANSFORMS + ("independent", "shared_static_background", "static_identical", "dark_identical"):
            subset = [row for row in rows if row["group"] == group and row["case"] == name]
            summaries[group][name] = {"cases": len(subset), "witnesses": sum(bool(row["witnesses"]) for row in subset)}
    return {"version": 1, "checkpoint": 249, "parameters": PARAMETERS, "opencv": cv2.__version__,
            "numpy": np.__version__, "single_threaded": True, "rows": rows, "summary": summaries,
            "elapsed_seconds": time.monotonic() - started,
            "process_peak_RSS_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            "feature_seconds": features_seconds, "comparison_seconds": comparisons_seconds,
            "code_sha256": {str(path.relative_to(Path(__file__).resolve().parents[1])): hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in (Path(__file__).resolve(), Path(__file__).resolve().parents[1] / "src/fas/content_correspondence.py")},
            "real_media_or_images_opened": False, "real_pairs_screened": 0, "scientific_tolerance_adopted": False}


def shared_camera_sequences(seed: int) -> tuple[list[np.ndarray], list[np.ndarray]]:
    sequences = (scene(seed, seed + 9000), scene(seed + 10000, seed + 9000))
    return tuple([cv2.warpAffine(rgb, np.array([[1, 0, slot * 2], [0, 1, slot]], np.float32), (256, 384))
                  for slot, rgb in enumerate(frames)] for frames in sequences)


def challenge_measure() -> dict:
    started = time.monotonic()
    rows = []
    for seed in range(300, 308):
        left, right = shared_camera_sequences(seed)
        rows.append({"seed": seed, "expected": "negative_for_common_foreground_capture",
                     "case": "shared_moving_background_different_foregrounds",
                     **compare_features(sequence_features(left), sequence_features(right))})
    return {"version": 1, "checkpoint": 249, "challenge_only": True, "parameters": PARAMETERS,
            "rows": rows, "alarms": sum(bool(row["witnesses"]) for row in rows),
            "elapsed_seconds": time.monotonic() - started,
            "process_peak_RSS_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            "purpose": "supplemental confound test after primary controls; no threshold changes",
            "real_pairs_screened": 0, "scientific_tolerance_adopted": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--challenge-only", action="store_true")
    args = parser.parse_args()
    if args.out.exists() or args.out.is_symlink() or not args.out.resolve().is_relative_to(Path("/mnt/e/FAS-private/artifacts/phase1").resolve()):
        raise ValueError("fresh private immutable output required")
    result = challenge_measure() if args.challenge_only else measure()
    write_immutable_record(args.out, result)
    print("PASS249 synthetic controls", len(result["rows"]), "elapsed", round(result["elapsed_seconds"], 3))
    print(result.get("summary", {"challenge_alarms": result.get("alarms")}))


if __name__ == "__main__":
    main()