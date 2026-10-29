# 323 - Completing the fixed comparison after the context timeout

Date: 2026-10-29.
Status: continuation implementation and validation; no automatic retry.

## What stopped, and what it means

The approved 322 attempt stopped at its combined 40-minute context limit
after 8224.875 seconds on the original clock. Four contexts completed:
all three OULU seeds and CASIA seed 20260917. CASIA seed 20260923
completed all 50 specialist epochs and saved its selected checkpoint,
but timed out inside conditional bootstrap analysis before its heads,
calibrators and prediction/analysis record were persisted.

This is an execution-budget failure, not negative PAD performance evidence,
and is not a publishable scientific contribution. The goal remains a
completed four-system, four-target, three-seed comparison. No architecture,
data partition, hyperparameter, threshold, checkpoint-selection rule or
scientific endpoint changes.

## Measured analysis repair

The [analysis](../scripts/paper321/study.py) now prepares row joins,
threshold masks, stable score order and tie boundaries once. Each bootstrap
draw computes ranking once per system, not once per threshold. The same
NumPy multinomial stream, paired cluster weights, original denominators,
strict threshold ties and undefined one-class ranking behavior are preserved.

On the existing `fas` conda environment, reference-versus-optimized
20-draw comparisons measured 4.37--6.63x speedup. Full optimized 2000-draw
analyses took 0.29--0.47 seconds without filesystem resource guards. All
fields of all four saved full analyses reconstruct within the existing
`rtol=atol=1e-12` readback contract. Synthetic tests additionally cover ties,
technical failures and one-class bootstrap draws.

This does **not** establish that bootstrap arithmetic dominated runtime.
Twenty old storage-guard directory scans took 1.68 seconds on this host.
Those guards run repeatedly during both training and analysis; disk and
training work also count against the old combined context ceiling.
The measurements do not justify calling the entire stop a bootstrap
compute bottleneck. Storage checks remain enforced.

## Explicit continuation, not rewriting the stopped attempt

The [continuation entry point](../scripts/paper321/continuation.py) uses a
separate private `paper_comparison323_v1` package. Original 321/322 plans,
approvals, fit starts, checkpoints, logs and terminal receipts remain intact.
Preparation verifies the parent sealed inputs/runtime and reconstructs its
original implementation hashes from commit
`72b98295c3016348c53b208c25e39723c08fbe6c` where current files were amended.
Retained artifacts are hashed into the new plan. Checkpoint history, seed,
earliest minimum validation epoch, optimizer-step count, finite tensors and
saved model/usable-identity joins must pass before reuse.

| Work | Retained | New in 323 | Cumulative |
|---|---:|---:|---:|
| Frozen-head fit starts | 15 | 24 | 39 |
| Specialist fit starts | 5 | 7 | 12 |
| Calibrator fit starts | 20 | 32 | 52 |

Four complete contexts are reused without new fitting and independently
replayed during final verification. The fifth specialist checkpoint is
reused without specialist retraining. Its three lost frozen heads and four
lost calibrators require explicitly declared deterministic recipe refits;
they are **not** misreported as zero-fit recovery or original-budget fits.
The seven untouched contexts receive the original complete recipe.
There remain exactly 12 specialist fits, 600 specialist epochs and 74400
specialist optimizer steps across 322 and 323. No target-label selection,
new encoder forward, model search, shortened training or new download occurs.

## New phase budgets and approval

The old deadline has expired and cannot authorize continuation. A new
explicit approval binds the new seal and starts a separately disclosed
24-hour total / 22-hour work clock, leaving two hours for reconstruction.
Per-context phase ceilings are:

| Phase | Ceiling |
|---|---:|
| Frozen heads | 10 minutes |
| Specialist training and checkpoint persistence | 90 minutes |
| Saved-checkpoint loading, predictions and calibration | 30 minutes |
| Analysis, including 2000 paired draws | 10 minutes |

Both worker guards and the independent supervisor enforce phase clocks.
The original two-thread, 12GiB sampled combined RSS, 12GiB own CUDA and
8GiB artifact limits remain. Storage accounting includes all three attempt
directories. This is bounded operational headroom, not proof that all
remaining training will finish inside 90 minutes. Any new failure stops
without automatic retry.

Use the existing project environment, not a new environment:

```sh
/home/lathevinh/miniforge3/envs/fas/bin/python scripts/paper321/continuation.py --benchmark
/home/lathevinh/miniforge3/envs/fas/bin/python scripts/paper321/continuation.py --prepare
```

Only after explicit approval:

```sh
/home/lathevinh/miniforge3/envs/fas/bin/python scripts/paper321/continuation.py --approve \
  --answer approve_paper323_complete_fixed_recipe_phase_budgets_and_declared_recovery_refits
/home/lathevinh/miniforge3/envs/fas/bin/python scripts/paper321/continuation.py --execute
```

Completion still requires all 12 contexts, all 144 policy/oracle cases,
independent checkpoint reconstruction without further fits and a successful
terminal receipt. Manuscript result cells remain pending until then.
