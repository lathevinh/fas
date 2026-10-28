# 321 - Executable bounded comparison and response to review320

Date:2026-10-28.
Status: implementation and read-only sealing, **not scientific execution
approval or a new scientific result**.

This implements the existing [319 specification](paper319/supplementary-protocol.json)
and [review320](320-review-doc319-and-paper319-preparation-and-manuscript.md).
It does not reopen model choice, add datasets or launch another search.
The [manuscript](paper319/manuscript.md) retains pending supplementary results.

## 1. Concrete review response

| Review requirement | Implemented disposition |
|---|---|
| Standalone completed-study methods | Manuscript4.0 distinguishes historical6882/6855/27 populations, outer exclusions, pseudo-targets, two-source primary heads, one-source inner selectors, calibration, six references and all three oracle stages.309's CLIP mean is explicitly source-domain-OOF. |
| Paired policy/oracle evidence | Manuscript Table3 gives policy FA/BFA, oracle BFA and individual FA-safe/utility counts for three fixed systems across four sources. All12 rows were recomputed from316's public cases, without refitting. Unsafe-policy BFA differences are not same-security gains. |
| Prior-work overlap and author errors | Corrected Lorenz/George/Marcel and Feng/Gallin-Martel/Ito/Aoki using primary arXiv author metadata. Incorporated320's Costa-Pazo full-text evidence and explicitly disclaimed constrained-ROC novelty. The implementation host's retrieval failures are not concealed or treated as an independent full-text reread. |
| SiW limitation and subject checks | Direct known-subject isolation supplements registered-group/exact-frame checks. SiW remains a video-grouped Protocol-I local intersection, not participant-independent or full-release evaluation. No identity recovery/new dataset prerequisite is introduced. |
| Real controller and specialist compatibility | Added a fixed trainer, source calibration, threshold/analysis code, checkpoint replay and an independent subprocess resource supervisor; exercised them synthetically. Actual GPU training feasibility is still unmeasured. |

No certified provider/year/category Q3 venue has been established.
The [venue brief](paper319/related-work-and-venues.md) keeps this unresolved,
without using it to delay the existing bounded technical package.

## 2. Executable surfaces and fixed scientific inventory

- [Controller](../scripts/paper321/runner.py): preparation, immutable input
  commitments, approval receipt, one attempt, worker, separate-process
  checkpoint reconstruction and terminal status.
- [Specialist](../scripts/paper321/specialist.py): DenseNet161 first eight
  feature children,384x14x14 representation,1x1 pixel head,196-to1 global
  head; mean pixel/global BCE with bona-fide target1, attack score
  `1-mean(sigmoid(pixel_logits))`.
- [Analysis](../scripts/paper321/study.py): direct subject isolation,
  exact integer attack budgets and limiting sources, original-denominator
  FA/BFA, usable-only FA/BF rejection/AUROC, oracle diagnostics, paired
  conditional bootstrap, equal-target macro/worst-target summaries and
  compact low-FA SVG with source-policy markers.
- [Tests](../tests/test_paper321.py) and specialist [NOTICE](../scripts/paper321/NOTICE) /
  [GPL license](../scripts/paper321/COPYING).

The fixed inventory is12 target/seed contexts,36 frozen-head starts,
12 specialist starts and48 calibrators. There are48 primary
system/target/seed rows;1%/10% sensitivities bring policy/oracle records
to144 each. Every specialist completes50 epochs, for600 total epochs
and74400 optimizer steps on the actual declared fitting populations.
No grid, new foundation-model forward, PAD-pretrained initialization,
post-selection refit or automatic retry is allowed.

The inherited319 recipe is unchanged:200-epoch FP64 frozen heads;
specialist batch16, Adam1e-4/weight-decay1e-6, FP32 deterministic computation,
no AMP/TF32, horizontal-flip-only augmentation and source-validation
earliest best checkpoint. Per epoch, replacement sampling makes exactly
the usable fitting-pool number of draws with expected equal-source/class
weighting. The model seed is set before construction; sampler and flip
generators use seed+1 and seed+2. Four positive-affine sigmoid calibrators
per context retain FP64 L-BFGS-B, maxiter1000,ftol1e-12,gtol1e-7;
initial slope1/intercept0 is fixed through the softplus parameterization.

This is matched-input DeepPixBiS architecture retraining with a
researcher-fixed recipe, not an exact reproduction of original training
hyperparameters. Synthetic compatibility is not a measured PAD result.

## 3. Read-only sealing and exact cache reuse

Run the following only for preparation:

```sh
python scripts/paper321/runner.py --prepare
```

The [public seal receipt](../results/phase1/paper321-execution-plan-v1.json)
records implementation/runtime/specification hashes, aggregate inventory,
feature shapes and the private execution-plan digest. Actual file paths
and per-video membership stay private.

Preparation reconstructs the accepted319 partitions, asserts known-subject
and component isolation, and binds the accepted manifest/partition hashes.
It hashes existing native crop bytes and frozen checkpoints, checks the
three original extraction receipts and recomputes complete cache keys from
image/checkpoint/preprocessing/representation contracts. All705 shards are
loaded through the existing finite-FP32/shape/key checks, covering exactly
7474 usable originals in all three branches. Thus this goes beyond319's
byte-only metadata coverage audit.

Preparation has a30-minute read-only ceiling and performs no image decode,
scientific model prediction, fitting or initialization download. Execution
revalidates these bindings and runtime; byte/input drift is an explicit
failure, not permission to rebuild an encoder cache. New code is nested
outside313's flat sealed inventory; old313/316 and319 implementations remain
unchanged.

## 4. Initialization and bounded execution

ImageNet weights are **not downloaded during preparation**. The sealed
acquisition is the torchvision DenseNet161 IMAGENET1K_V1 URL:
`https://download.pytorch.org/models/densenet161-8d451a50.pth`.
Acquisition has a256MiB ceiling, upstream SHA256 prefix`8d451a50`,
single-attempt partial-file handling and an immutable full received digest.
No upstream full SHA256 is claimed. Finite tensors and strict complete
torchvision-state compatibility are checked before any scientific fit.

After one explicit owner decision, the authority is bound to the exact
execution-plan hash and original boot/monotonic clock. The worker must be
a direct child of its owning supervisor. A second process restores saved
specialist checkpoints, frozen heads and calibrators, reconstructs all
predictions/policies/analyses and performs **zero additional fits**.
One reconstruction prediction pass is included in the budget.

| Bound | Enforcement / interpretation |
|---|---|
|12 hours total;11-hour work cutoff | Nonresettable clock; final hour reserved for reconstruction/closure, not more fitting |
|40 minutes per context | Independent supervisor watches active context time as well as worker guards; includes that context's head/specialist/analysis work |
|12GiB combined sampled RSS | Supervisor plus worker process group, sampled every0.5 seconds; not an unsampled instantaneous-peak guarantee |
|12GiB own CUDA allocated/reserved | PyTorch process allocation fraction plus allocated/reserved high-water checks; does not reserve the GPU from other users |
|8GiB owned new/temporary artifacts | Guards and prewrite checkpoint reservation;256MiB operational/terminal reserve is inside this cap |
|256MiB initialization | Bounded acquisition; received full digest retained |
|2 BLAS threads, loader workers0 | Fixed process environment/runtime; no parallel training workers |

There are no automatic restarts or shortened-success recipes. A deadline,
optimizer, input, resource or verification failure stops the one attempt
with retained incomplete evidence. Time limits are enforced ceilings,
**not proof that50-epoch training will finish inside them**.

Thresholds accept strictly below the minimum source-safe order statistic.
MSU calibration's18 attacks imply zero allowed attack errors at both1%
and5%; repeated thresholds may reflect sample resolution, not robustness.
The2000 paired target-cluster bootstrap draws per context condition on
saved models and fixed source policies. They do not resample training or
certify population security; oracle points get no confidence interval.
SiW intervals remain video/exact-frame-component conditional intervals.

## 5. Verification and remaining owner decision

Focused local validation:

```sh
python -m unittest discover -s tests -p test_paper321.py -v
```

The18 tests passed in the FAS runtime, including actual CPU synthetic
DeepPixBiS shape/loss/gradient/state initialization/restore and BatchNorm
checks; reproducible toy training; a mocked12-context controller execution
with exactly36/12/48 starts followed by no-fit reconstruction; strict ties,
denominators, source budgets, subject leakage, input drift, wrong approval,
download limits/hash mismatch and independent hung-child RSS/time stops.
The end-to-end controller test uses synthetic rows/features and a toy
specialist, not private scientific predictions. The actual network tests
use a synthetic DenseNet state; compatibility with acquired ImageNet bytes
is additionally checked at execution before fitting.
The four torch-dependent tests run in isolated child processes, so their
network-allocation high-water marks do not alter unrelated RSS-cap tests.

CI without torch/torchvision skips the four specialist/controller tests;
it must not be described as having run those actual CPU network checks.
Pylance transport was unavailable on this host; no editor/type-analysis
pass is claimed instead of the observed runtime tests.

One integrated execution decision must explicitly cover:

1. The fixed four systems, populations, three seeds,36/12/48 fitting starts,
  50 specialist epochs and no new encoder/dataset/grid.
2. ImageNet acquisition, all resource ceilings, one reconstruction pass
   and2000 paired bootstrap replicates/context, with no automatic retry.
3. SiW's missing participant identities, video grouping and local test-list
   intersection, affecting selection as well as uncertainty.

The controller's exact approval answer is
`approve_paper321_bounded_comparison_with_SiW_video_groups`.
Neither review320 nor acceptance of this implementation creates that
authority. Until the owner decides, there is no supplementary accuracy
result and no scientific training process to report.
