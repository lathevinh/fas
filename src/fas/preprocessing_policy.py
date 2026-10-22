"""Explicit active image-export parameters, equivalent to the accepted SCRFD recipe."""

from collections.abc import Mapping
import json

MODEL_SHA256 = "5838f7fe053675b1c7a08b633df49e7af5495cee0493c7dcf6697200b85b5b91"

FACE_PARAMETERS: dict[str, object] = {
    "detector": "SCRFD_10G_KPS",
    "detector_weight_sha256": MODEL_SHA256,
    "alignment": "five_point_similarity_rotation_about_eye_midpoint",
    "context_scale": 1.30,
    "clip_context_to_aligned_image": True,
    "border": "constant_zero",
    "color_mode": "RGB",
    "interpolation": "bicubic",
    "detector_failure_action": "terminal_non_accept",
}
DETECTOR_PARAMETERS: dict[str, object] = {
    "input_size": [640, 640], "input_mean": 127.5, "input_std": 128.0,
    "score_threshold": 0.5, "nms_threshold": 0.4,
    "provider": "CPUExecutionProvider", "threads": 1,
    "primary_face": "largest_area_then_confidence_then_lexicographic_box",
}
ACTIVE_PREPROCESSING_V3: dict[str, object] = {
    "version": 3,
    "state": "active_parameter_pin_not_execution_authority",
    "frame_policy": {
        "primary": "middle_decodable_frame_in_official_interval",
        "detector_success_replacement": False,
        "sensitivity_positions": [0.25, 0.5, 0.75],
    },
    "face": FACE_PARAMETERS,
    "detector_parameters": DETECTOR_PARAMETERS,
    "openclip": {"resolution": 224, "normalization": "checkpoint_native"},
    "dino": {"resolution": 518, "normalization": "official_dinov2"},
    "image_export": {
        "branch_resolutions": [224, 518],
        "backbone_normalization_applied": False,
        "model_scores_produced": False,
        "score_fitting_performed": False,
        "target_access_authorized": False,
    },
}


def validate_active_preprocessing(config: Mapping[str, object]) -> None:
    if json.dumps(dict(config), sort_keys=True) != json.dumps(ACTIVE_PREPROCESSING_V3, sort_keys=True):
        raise ValueError("active preprocessing v3 must match the accepted fixed image-export parameters")


def validate_legacy_equivalence(active: Mapping[str, object], pilot: Mapping[str, object]) -> None:
    validate_active_preprocessing(active)
    expected = {
        **DETECTOR_PARAMETERS,
        **FACE_PARAMETERS,
        "branch_resolutions": [224, 518],
        "replacement": False,
        "normalization": "not_applied_no_backbone_or_PAD_execution",
    }
    if any(pilot.get(key) != value for key, value in expected.items()):
        raise ValueError("active v3 and accepted pilot detector/geometry parameters differ")
