# Phase 1.1: Environment Lock and Weight-Free CUDA Smoke

Authority: Document 42 and the checkpoint plan in Document 65
Status: accepted in Document 69; checkpoint 1.2 authorized

## Entry and scope

The owner approved Python 3.12 in the existing conda environment `fas`.
Document 66's preflight review approved checkpoint 1.0. Phase-0 rework commit
`7775937fbe76a9e096e50804e774eba282dbff0a` has a completed successful workflow:
https://github.com/lathevinh/fas/actions/runs/37284417602/job/111679801964

No other environment is created. All Python execution, installation and validation
use `conda run -n fas`. The editor uses the existing interpreter path; actual runtime
Python, not cached editor metadata, determines the observed version.

This step locks executable dependencies and source identities. It does not acquire
FAS datasets, load pretrained weights, extract features, train models, measure
scientific competence, or authorize target evaluation.

## Acceptance criteria

1. `fas` runs Python 3.12 within the registered range without changing `base`.
2. Model-stack imports and `pip check` pass in that interpreter.
3. Transitive Python dependency locks contain exact pins and hashes. The conda
   layer separately pins Python/native packages; config digests match lock bytes.
4. Reinstall locked packages with required hashes in the same `fas`; verify versions
   and smoke afterward. No separate cold environment is created under the owner's
   single-environment constraint.
5. Clean DINOv2 and SCRFD checkouts at exact commits import their required entry
   points without downloading weights.
6. PyTorch CUDA MatMul, torchvision CUDA NMS and synthetic ONNX CUDA MatMul match
   references. ONNX CPU fallback is explicitly disabled.
7. Pin/check FFmpeg; record GPU, CUDA and cuDNN. Another host's driver/hardware
   compatibility is not guaranteed by this dependency lock.
8. Full synthetic suite, schema and unavailable-stage refusal matrix still pass.
9. Publish actual JSON evidence and commands, commit/push, then stop for owner
   confirmation before checkpoint 1.2.

## Dependency and source boundaries

Direct requirements: `configs/environment-linux-py312.in`. Pins include matching
PyTorch 2.7.1/torchvision 0.22.1, OpenCLIP 3.0.0, Transformers 4.51.3,
scikit-learn 1.6.1 and ONNX Runtime GPU 1.22.0. These instantiate the frozen recipes;
they do not select alternative backbones or detector checkpoints.

The lock is Linux x86-64 / CPython 3.12 specific, with glibc >= 2.28 (observed
2.35). Native conda artifacts, hashed
wheels, upstream commits and runtime smoke are separate evidence. One requirements
file hash alone does not certify all of them.

Source checkouts stay outside Git under `$HOME/.cache/fas/upstream`:

| Source | Commit | Directory |
|---|---|---|
| facebookresearch/dinov2 | 7764ea0f912e53c92e82eb78a2a1631e92725fc8 | dinov2-7764ea0 |
| deepinsight/insightface SCRFD | 81929474ec02e54e3655f6841bced800009c592d | insightface-8192947 |

DINO uses the registered torch-hub source rather than a PyPI substitute. SCRFD
imports its pinned `model_zoo` code with actual relative helpers, not the whole
InsightFace application bundle. No `FaceAnalysis`, detector weights or pretrained
backbone constructor is called. Weight hashes and pretrained-model parity remain
later extraction prerequisites; import success is not coverage or accuracy evidence.

## Recheck

```bash
conda run -n fas python scripts/check_environment.py
conda run -n fas python scripts/smoke_environment.py
conda run -n fas python -m pip check
conda run -n fas python -m unittest discover -s tests -v
conda run -n fas python scripts/validate_preregistration.py --stage schema
conda run -n fas python scripts/validate_preregistration.py --stage data-audit
git diff --check
```

After lock completion the first five commands must succeed; data audit must still
return 1 because real manifests are missing. An environment check cannot unlock
analysis or evaluation. Use `--out` with a new path for immutable reports; retain
the checkpoint-1.0 JSON as a historical snapshot.

## Actual evidence

All executable acceptance checks passed in existing `fas`, Python 3.12.14:

| Check | Actual result |
|---|---|
| Exact package metadata and wheel lock identity | `ready`, exit 0 |
| Hash-required wheel reconstruction | 61 packages force-reinstalled, exit 0 |
| Native conda reconstruction | Explicit lock force-reinstalled, exit 0; inventory equals lock |
| Post-reconstruction smoke | `pass`, exit 0; byte-identical to immutable smoke report |
| PyTorch | 2.7.1+cu126, CUDA 12.6, cuDNN runtime 90501 |
| GPU | NVIDIA GeForce RTX 4080 SUPER; host driver 591.86 |
| Imports and source identity | OpenCLIP/DINO/SCRFD and numerical stack pass; clean exact source commits |
| Synthetic CUDA | PyTorch MatMul, torchvision NMS, ONNX MatMul pass |
| ONNX session | CUDA first; `session.disable_cpu_ep_fallback=1`; CPU remains listed but no fallback permitted |
| FFmpeg | Exact registered version line matches |
| Dependency consistency | `No broken requirements found.` |
| Focused/full tests | 12 environment tests / 76 total tests, OK |
| Readiness matrix | schema 0; four unavailable stages 1; three retired stages 2 |
| Freeze writer | Exit 1; no record created/changed |
| Whitespace validation | `git diff --check`, exit 0 |

Immutable reports:

- [Runtime declarations](../results/phase1/environment-preflight-locked.json)
- [Imports and CUDA smoke](../results/phase1/environment-smoke-locked.json)
- [Reconstruction and regression](../results/phase1/environment-lock-verification.json)

Wheel lock SHA-256: `7a44a8c07dafcf032615c248ae711af9920d0196089a9fba66486bf7a02f36e2`.
Native lock SHA-256: `598cb94c58b9e78b72824c463c890ecc20d4e4e6959d7916c8c3157bd2bbcb00`.
Environment config SHA-256: `686a5020f68096bfaa29e3ab57aedf5355d958d1dbdf5830a98c133bd0321380`.

Reconstruction uses both layers, in this order, in the same environment:

```bash
conda install -n fas -y --force-reinstall --file configs/environment-conda-linux-64.lock
conda run -n fas python -m pip install --require-hashes --force-reinstall --no-deps -r configs/environment-linux-py312.lock
conda run -n fas python -m pip check
conda list -n fas --explicit --md5 | diff - configs/environment-conda-linux-64.lock
conda run -n fas python scripts/smoke_environment.py
```

Provision sources outside the repository when absent; never substitute a moving
branch for the commit. The smoke refuses missing, changed or dirty checkouts:

```bash
git clone https://github.com/facebookresearch/dinov2.git "$HOME/.cache/fas/upstream/dinov2-7764ea0"
git -C "$HOME/.cache/fas/upstream/dinov2-7764ea0" checkout --detach 7764ea0f912e53c92e82eb78a2a1631e92725fc8
git clone https://github.com/deepinsight/insightface.git "$HOME/.cache/fas/upstream/insightface-8192947"
git -C "$HOME/.cache/fas/upstream/insightface-8192947" checkout --detach 81929474ec02e54e3655f6841bced800009c592d
```

The native layer supplies pip/wheel; the wheel layer also reinstalls packaging and
setuptools at matching versions. Export/generate locks only after selecting the
actual interpreter, constrain resolution to observed versions, and avoid conda
build-time direct URLs from `pip freeze`. The generic Linux resolver selected a
too-old wheel ABI; successful compilation used actual host/interpreter tags.

DINO emitted expected xFormers-unavailable warnings; its ordinary PyTorch path is
available. No xFormers acceleration, pretrained inference or extraction parity is
certified. Model/detector weights and their hashes remain later prerequisites.
FFmpeg is a checked host prerequisite, not installed by either lock. This step
does not lock the entire OS, GPU driver, or GPU hardware. In-place reconstruction
is verified; a fresh empty-environment rebuild was not performed because the owner
requires the existing `fas` exclusively.

The first installation was interrupted and the generic installer response was not
supported by imports in `fas`; neither was counted as a pass. Actual evidence is
from explicit environment-bound pip, subsequent reconstruction, and runtime checks.
The entry CI above covers the prerequisite commit, not this checkpoint's new files.
Owner confirmation and successful fresh remote CI for 08d29c0 are recorded in
[Document 69](69-review-phase1-step1.1-environment-lock.md); checkpoint 1.1 is accepted.