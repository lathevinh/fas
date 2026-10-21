"""Synthetic-only A/B test of camera-compensated residual-motion witnesses."""

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

from evaluate_oulu_method249 import scene, shared_camera_sequences, transform
from fas.content_correspondence import compare_features, sequence_features
from fas.freeze import write_immutable_record


METHOD = {"camera_model": "phase_correlation_translation", "minimum_response": 0.15,
          "maximum_shift_fraction": 0.1, "residual_difference": 12, "dilation": 5,
          "valid_support_erosion": 5, "features": 600, "FAST": 12,
          "failed_registration": "no_features_unknown_not_clearance"}
CASES = ("same_camera_content", "same_camera_content_JPEG60", "same_camera_content_translation16_12",
         "same_foreground_different_background", "shared_camera_background_different_foregrounds",
         "independent_camera_scenes", "static_identical", "black_identical")


def residual_mask(previous: np.ndarray, current: np.ndarray) -> tuple[np.ndarray, dict]:
    shift, response = cv2.phaseCorrelate(previous.astype(np.float32), current.astype(np.float32))
    height, width = current.shape
    supported = (np.isfinite([*shift, response]).all() and response >= 0.15
                 and abs(shift[0]) <= width * 0.1 and abs(shift[1]) <= height * 0.1)
    metadata = {"shift": [float(value) for value in shift], "response": float(response),
                "status": "registered_translation" if supported else "registration_unavailable",
                "valid_pixels": 0, "residual_pixels": 0}
    if not supported:
        return np.zeros_like(current), metadata
    matrix = np.array([[1, 0, shift[0]], [0, 1, shift[1]]], np.float32)
    warped = cv2.warpAffine(previous, matrix, (width, height))
    valid = cv2.warpAffine(np.full_like(previous, 255), matrix, (width, height), flags=cv2.INTER_NEAREST)
    kernel = np.ones((5, 5), np.uint8)
    valid = cv2.erode(valid, kernel, borderType=cv2.BORDER_CONSTANT, borderValue=0)
    mask = cv2.dilate(np.where(cv2.absdiff(warped, current) > 12, 255, 0).astype(np.uint8), kernel)
    mask = cv2.bitwise_and(mask, valid)
    metadata.update(valid_pixels=int(np.count_nonzero(valid)), residual_pixels=int(np.count_nonzero(mask)))
    return mask, metadata


def feature_sets(frames: list[np.ndarray]) -> tuple[list[dict], list[dict]]:
    baseline = sequence_features(frames)
    extractor = cv2.ORB_create(nfeatures=600, fastThreshold=12, edgeThreshold=15)
    previous = None
    revised = []
    for rgb, original in zip(frames, baseline, strict=True):
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        if gray.shape != original["shape"]:
            height, width = original["shape"]
            gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_AREA)
        if previous is None:
            mask, metadata = np.zeros_like(gray), {"status": "context_only"}
        else:
            mask, metadata = residual_mask(previous, gray)
        keypoints, descriptors = extractor.detectAndCompute(gray, mask)
        revised.append({**original, "points": np.array([point.pt for point in keypoints], np.float32).reshape(-1, 2),
                        "descriptors": descriptors, "camera_motion": metadata})
        previous = gray
    return baseline, revised


def camera(frames: list[np.ndarray]) -> list[np.ndarray]:
    return [cv2.warpAffine(rgb, np.array([[1, 0, 2 * slot], [0, 1, slot]], np.float32), (256, 384))
            for slot, rgb in enumerate(frames)]


def measure() -> dict:
    started = time.monotonic()
    rows = []
    for group, seeds in (("development", range(400, 408)), ("held_out", range(500, 508))):
        for seed in seeds:
            left, shared_background = shared_camera_sequences(seed)
            variants = {"same_camera_content": left,
                        "same_camera_content_JPEG60": transform(left, "JPEG60"),
                        "same_camera_content_translation16_12": transform(left, "translation16_12"),
                        "same_foreground_different_background": camera(scene(seed, seed + 19000)),
                        "shared_camera_background_different_foregrounds": shared_background,
                        "independent_camera_scenes": camera(scene(seed + 20000))}
            for name in CASES:
                if time.monotonic() - started > 900:
                    raise TimeoutError("new synthetic A/B budget exceeded")
                first_frames = left
                expected = "common_foreground_content" if name.startswith("same_") else "no_common_foreground"
                if name in ("static_identical", "black_identical"):
                    first_frames = scene(seed, static=True) if name == "static_identical" else [np.zeros_like(frame) for frame in left]
                    second_frames = first_frames
                    expected = "outside_residual_motion_claim_not_clearance"
                else:
                    second_frames = variants[name]
                before = time.monotonic()
                first_baseline, first_revised = feature_sets(first_frames)
                second_baseline, second_revised = feature_sets(second_frames)
                rows.append({"group": group, "seed": seed, "case": name, "expected": expected,
                             "left_RGB_sha256": [value["rgb_sha256"] for value in first_baseline],
                             "right_RGB_sha256": [value["rgb_sha256"] for value in second_baseline],
                             "baseline": compare_features(first_baseline, second_baseline),
                             "compensated": compare_features(first_revised, second_revised),
                             "camera_motion": [[value["camera_motion"] for value in side] for side in (first_revised, second_revised)],
                             "elapsed_seconds": time.monotonic() - before})
    summary = {group: {name: {"cases": len(subset),
                              "baseline_witnesses": sum(bool(row["baseline"]["witnesses"]) for row in subset),
                              "compensated_witnesses": sum(bool(row["compensated"]["witnesses"]) for row in subset)}
                      for name in CASES
                      for subset in [[row for row in rows if row["group"] == group and row["case"] == name]]}
               for group in ("development", "held_out")}
    root = Path(__file__).resolve().parents[1]
    paths = [Path(__file__).resolve(), root / "scripts/evaluate_oulu_method249.py", root / "src/fas/content_correspondence.py"]
    return {"version": 1, "checkpoint": 253, "method": METHOD, "rows": rows, "summary": summary,
            "elapsed_seconds": time.monotonic() - started,
            "process_peak_RSS_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            "opencv": cv2.__version__, "numpy": np.__version__,
            "code_sha256": {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
            "scientific_tolerance_adopted": False, "real_pairs_screened": 0,
            "purpose": "paired synthetic comparison for shared-camera-background confound, not capture adjudication"}


def dynamic_background_sequences(seed: int) -> tuple[list[np.ndarray], list[np.ndarray]]:
    generator = np.random.default_rng(seed + 70000)
    panel = cv2.GaussianBlur(generator.integers(0, 256, (72, 112, 3), dtype=np.uint8), (3, 3), 0)
    sequences = (scene(seed, seed + 9000), scene(seed + 10000, seed + 9000))
    for frames in sequences:
        for slot, rgb in enumerate(frames):
            left = 16 + slot
            rgb[8:80, left:left + 112] = panel
    return tuple(camera(frames) for frames in sequences)


def challenge_measure() -> dict:
    started = time.monotonic()
    rows = []
    for seed in range(600, 608):
        left, right = dynamic_background_sequences(seed)
        first_baseline, first_revised = feature_sets(left)
        second_baseline, second_revised = feature_sets(right)
        rows.append({"seed": seed, "case": "shared_independently_moving_background_panel_different_foregrounds",
                     "expected": "no_common_foreground_but_shared_recorded_background_content",
                     "left_RGB_sha256": [value["rgb_sha256"] for value in first_baseline],
                     "right_RGB_sha256": [value["rgb_sha256"] for value in second_baseline],
                     "baseline": compare_features(first_baseline, second_baseline),
                     "compensated": compare_features(first_revised, second_revised),
                     "camera_motion": [[value["camera_motion"] for value in side] for side in (first_revised, second_revised)]})
    root = Path(__file__).resolve().parents[1]
    return {"version": 1, "checkpoint": 253, "challenge_only": True, "rows": rows,
            "method": METHOD, "elapsed_seconds": time.monotonic() - started,
            "process_peak_RSS_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            "baseline_witnesses": sum(bool(row["baseline"]["witnesses"]) for row in rows),
            "compensated_witnesses": sum(bool(row["compensated"]["witnesses"]) for row in rows),
            "code_sha256": {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in [Path(__file__).resolve(), root / "scripts/evaluate_oulu_method249.py",
                                         root / "src/fas/content_correspondence.py"]},
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
    print("PASS253 new synthetic A/B", len(result["rows"]), round(result["elapsed_seconds"], 3))
    print(result.get("summary", {"challenge_witnesses": result.get("compensated_witnesses")}))


if __name__ == "__main__":
    main()