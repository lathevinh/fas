# 66 — Review of Phase 1 Step 1.0 Preflight

Date: 2026-10-05  
Repository: `lathevinh/fas`  
Reviewed commit: `c035fbe8bbb084a5d96c47255f9df71ec116b622`  
Reviewed plan: `docs/65-phase1-checkpoints-and-preflight.md`

## Verdict

**APPROVED — Checkpoint 1.0 Preflight is complete.**

No blocker or major issue was found that could cause scientific results to be wrong, violate the frozen source/target protocol, or falsely authorize dataset/model execution at this checkpoint.

Checkpoint 1.1 may proceed.

## What was verified

### 1. Scope is correctly limited

Step 1.0 is explicitly read-only and does not install packages, access datasets, download model weights, run training, or claim GPU/model readiness.

The checker output is scoped as:

```text
runtime declarations and lock identity only; not model/GPU/data readiness
```

This is appropriate for a preflight checkpoint.

### 2. Pending environment correctly fails closed

The tracked environment config is still:

```text
status = pending_model_stack_lock
python_requires = >=3.11,<3.13
package pins = null
lockfile = null
```

The committed real preflight report correctly returns:

```text
status = blocked
```

for the current interpreter/environment.

This is the expected outcome before checkpoint 1.1, not a failure of checkpoint 1.0.

### 3. Core negative checks are covered

The implementation/tests reject:

- unsupported Python versions;
- wrong platform;
- wrong schema version;
- missing or changed required packages;
- non-exact package pins;
- omitted required packages;
- missing lockfile;
- modified lockfile;
- lockfile outside the repository;
- malformed Python requirement;
- overwriting an existing evidence report.

These checks are sufficient for the stated Step-1.0 scope.

### 4. Positive path exists

A matching synthetic environment with:

- compatible Python;
- matching platform;
- exact package versions;
- `status=locked`;
- matching lockfile SHA-256;

returns `ready`.

Therefore the checker is not simply hard-coded to block.

### 5. CLI behavior is usable and testable

The CLI distinguishes:

```text
0 = ready
1 = legitimate readiness blockers
2 = checker/output failure
```

and emits structured JSON.

The immutable-output behavior is also tested.

### 6. CI evidence is now independently present

The latest commit has a GitHub Actions run:

```text
Run: 37282319436
Head: c035fbe8bbb084a5d96c47255f9df71ec116b622
Status: completed
Conclusion: success
```

So the earlier Phase-0 problem of having tests but no independently visible run is no longer present.

## Acceptance criteria assessment

The Step-1.0 acceptance criteria are appropriate:

- matching synthetic environment passes;
- Python boundary behavior is tested;
- missing/changed/unpinned package declarations fail;
- lock identity is checked from actual bytes;
- current real pending environment remains blocked;
- JSON/exit-code behavior is defined;
- report overwrite is refused;
- no dataset/model/training/provisioning side effects occur.

There is no need to make Step 1.0 validate CUDA, import actual model libraries, transitive dependency completeness, model weights, or detector checkpoints. Those belong to checkpoint 1.1 and later backbone/model checkpoints.

## Non-blocking note for checkpoint 1.1

Document 38 requires the final environment lock to capture exact identities for the relevant model stack, including PyTorch, OpenCLIP, DINO, detector, and metric libraries.

The current Step-1.0 `REQUIRED_PACKAGES` list is intentionally narrower and is acceptable for preflight.

However, checkpoint 1.1 must not interpret this list as the complete reproducibility specification. It should add/freeze the actual source/package identities required by the implementation, especially:

- exact Python 3.12 runtime;
- PyTorch / torchvision;
- OpenCLIP;
- DINOv2 source/model identity;
- face detector implementation/checkpoint identity;
- numerical/metric dependencies actually used;
- CUDA runtime compatibility;
- FFmpeg identity where video decoding reproducibility depends on it.

This is a checkpoint-1.1 requirement, not a defect in checkpoint 1.0.

## Final disposition

\[
\boxed{\text{CHECKPOINT 1.0 PREFLIGHT — ACCEPTED}}
\]

Proceed to **Checkpoint 1.1 Environment Lock**.

No need to revise Step 1.0 before continuing.
