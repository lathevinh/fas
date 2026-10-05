# 69 — Review of Phase 1 Step 1.1 Environment Lock

Date: 2026-10-05
Repository: `lathevinh/fas`
Reviewed commit: `08d29c08ac151faa68b27f9a814784a4b8b1b46c`
Reviewed checkpoint: `docs/67-phase1-step1.1-environment-lock.md`

## Verdict

**APPROVED — Checkpoint 1.1 Environment Lock is complete.**

No blocker or major issue was found that could invalidate later scientific results, break reproducibility of the declared runtime stack, or falsely claim CUDA/model-stack readiness at this checkpoint.

Checkpoint 1.2 may proceed.

## Acceptance review

- Existing conda env `fas` now runs Python 3.12.14 and the locked preflight reports `status=ready`.
- Exact package versions are recorded for PyTorch, torchvision, OpenCLIP, Transformers, scikit-learn, NumPy/SciPy, ONNX Runtime GPU, OpenCV, PyArrow, Safetensors and CUDA runtime libraries.
- Wheel and native conda locks have recorded SHA-256 identities.
- Both layers were reconstructed in-place in the approved existing `fas` environment and post-reconstruction smoke matches the committed report.
- DINOv2 and SCRFD sources are pinned to exact 40-character commits and must be clean at those commits.
- CUDA smoke performs PyTorch MatMul vs CPU reference, torchvision CUDA NMS, and ONNX CUDA MatMul with CPU fallback disabled.
- FFmpeg version is pinned and checked.
- `pip check` passes.
- 76-test regression passes.
- Schema remains ready while data-audit/source-dry-run/analysis-freeze/locked-evaluation remain blocked as expected.
- Fresh CI for the exact Step-1.1 commit completed successfully.

## Non-blocking note

Reconstruction is in-place rather than a cold empty-environment rebuild. Given the explicit project constraint to keep and use only the existing `fas` environment, this is acceptable and does not block Step 1.1.

The generic preflight checker validates the wheel lock and package metadata; exact Python, conda-lock, source-checkout and CUDA checks are enforced by the smoke path. The combined evidence is sufficient for checkpoint acceptance.

## Final disposition

**CHECKPOINT 1.1 ENVIRONMENT LOCK — ACCEPTED**

Proceed to **Checkpoint 1.2 — Intake Contract**.

No Step-1.1 rework is required before continuing.
