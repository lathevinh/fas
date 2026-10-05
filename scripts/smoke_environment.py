#!/usr/bin/env python3
"""Run weight-free imports and synthetic CUDA checks for checkpoint 1.1."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import subprocess
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fas.environment import inspect_environment, verify_source_checkout
from fas.freeze import write_immutable_record
from fas.preregistration import load_config


def smoke(config: dict, upstream_root: Path) -> dict:
    environment = inspect_environment(ROOT, config)
    if environment["status"] != "ready":
        raise RuntimeError("environment declarations or dependency lock are not ready")
    if list(sys.version_info[:3]) != config["python_version"]:
        raise RuntimeError("Python runtime differs from the exact conda lock")
    conda_lock = ROOT / config["conda_lockfile"]
    if hashlib.sha256(conda_lock.read_bytes()).hexdigest() != config["conda_lockfile_sha256"]:
        raise RuntimeError("conda lock hash is stale")
    sources = {}
    for name, source in config["sources"].items():
        path = upstream_root / source["directory"]
        sources[name] = verify_source_checkout(path, source["commit"])
    import torch
    import torchvision
    import numpy as np
    import onnx
    import onnxruntime as ort
    import open_clip
    for module in ("transformers", "sklearn", "scipy", "cv2", "pyarrow", "safetensors"):
        importlib.import_module(module)
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable in fas")
    torch.backends.cuda.matmul.allow_tf32 = False
    source = torch.arange(16, device="cuda", dtype=torch.float32).reshape(4, 4)
    actual = source @ source.T
    torch.cuda.synchronize()
    if not torch.equal(actual.cpu(), source.cpu() @ source.cpu().T):
        raise RuntimeError("CUDA matmul differs from the synthetic CPU reference")
    boxes = torch.tensor([[0, 0, 10, 10], [0, 0, 10, 10]], device="cuda", dtype=torch.float32)
    selected = torchvision.ops.nms(boxes, torch.tensor([0.9, 0.8], device="cuda"), 0.5)
    if selected.tolist() != [0]:
        raise RuntimeError("torchvision CUDA NMS failed")
    if not open_clip.get_pretrained_cfg("ViT-B-16", "laion2b_s34b_b88k"):
        raise RuntimeError("OpenCLIP lacks the frozen checkpoint recipe")
    sys.path.insert(0, str(upstream_root / config["sources"]["dinov2"]["directory"]))
    backbones = importlib.import_module("dinov2.hub.backbones")
    importlib.import_module("dinov2.models.vision_transformer")
    if not Path(backbones.__file__).resolve().is_relative_to((upstream_root / config["sources"]["dinov2"]["directory"]).resolve()):
        raise RuntimeError("DINO import is not from the verified checkout")
    if not all(callable(getattr(backbones, name, None)) for name in ("dinov2_vitb14", "dinov2_vitb14_reg")):
        raise RuntimeError("DINO source lacks the required plain/register backbone factories")
    detector = upstream_root / config["sources"]["scrfd"]["directory"] / "python-package/insightface/model_zoo"
    namespace = types.ModuleType("_fas_scrfd_source")
    namespace.__path__ = [str(detector)]
    sys.modules[namespace.__name__] = namespace
    scrfd = importlib.import_module("_fas_scrfd_source.scrfd")
    if not Path(scrfd.__file__).resolve().is_relative_to(detector.resolve()):
        raise RuntimeError("SCRFD import is not from the verified checkout")
    if not callable(scrfd.SCRFD):
        raise RuntimeError("SCRFD source import failed")
    graph = onnx.helper.make_graph(
        [onnx.helper.make_node("MatMul", ["input", "right"], ["output"])],
        "fas_synthetic_cuda",
        [onnx.helper.make_tensor_value_info("input", onnx.TensorProto.FLOAT, [4, 4])],
        [onnx.helper.make_tensor_value_info("output", onnx.TensorProto.FLOAT, [4, 4])],
        [onnx.numpy_helper.from_array(np.arange(16, dtype=np.float32).reshape(4, 4).T.copy(), name="right")],
    )
    model = onnx.helper.make_model(graph, opset_imports=[onnx.helper.make_opsetid("", 17)], ir_version=10)
    onnx.checker.check_model(model)
    ort.preload_dlls()
    options = ort.SessionOptions()
    options.add_session_config_entry("session.disable_cpu_ep_fallback", "1")
    session = ort.InferenceSession(model.SerializeToString(), sess_options=options, providers=["CUDAExecutionProvider"])
    if session.get_providers()[0] != "CUDAExecutionProvider":
        raise RuntimeError("ONNX session silently fell back from CUDA")
    values = np.arange(16, dtype=np.float32).reshape(4, 4)
    if not np.allclose(session.run(None, {"input": values})[0], values @ values.T):
        raise RuntimeError("ONNX CUDA MatMul failed")
    ffmpeg = subprocess.check_output(["ffmpeg", "-version"], text=True).splitlines()[0]
    if ffmpeg != config["host_tools"]["ffmpeg_version_line"]:
        raise RuntimeError("FFmpeg differs from the pinned version")
    dependencies = subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True, text=True, check=True)
    return {
        "version": 1, "status": "pass", "environment": environment, "sources": sources,
        "python_version": list(sys.version_info[:3]),
        "conda_lockfile_sha256": hashlib.sha256(conda_lock.read_bytes()).hexdigest(),
        "imports": "pass", "torch_cuda_matmul": "pass", "torchvision_cuda_nms": "pass",
        "onnx_cuda_matmul": "pass", "onnx_providers": session.get_providers(),
        "onnx_cpu_fallback_disabled": True, "torch_version": torch.__version__,
        "gpu": torch.cuda.get_device_name(0), "torch_cuda": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(), "ffmpeg": ffmpeg,
        "pip_check": dependencies.stdout.strip(),
        "environment_config_sha256": hashlib.sha256((ROOT / "configs/environment_v1.yaml").read_bytes()).hexdigest(),
        "no_dataset_or_model_weights_accessed": True,
        "scope": "imports and synthetic operators only; not pretrained model or feature-extraction readiness",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-root", type=Path, default=Path.home() / ".cache/fas/upstream")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    sys.dont_write_bytecode = True
    try:
        result = smoke(load_config(ROOT / "configs/environment_v1.yaml"), args.upstream_root)
    except (ImportError, OSError, RuntimeError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"version": 1, "status": "blocked", "error": str(exc)}, indent=2))
        return 1
    if args.out:
        try:
            write_immutable_record(args.out, result)
        except OSError as exc:
            print(str(exc), file=sys.stderr)
            return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())