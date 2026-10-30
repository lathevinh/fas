# 329 - Implemented controlled DINO adaptation package

Date: 2026-10-30.
Status: **owner approved exact plan v2 and scientific execution started.**
The first real OULU-held-out reference epoch completed under the persistent
supervisor. See [start receipt](../results/phase1/paper329-start-v2.json).
The preparation and zero-start statements below describe sealing/publication
of the package before the subsequent explicit owner decision, not live status.
Implements [review328](328-review-doc327-controlled-adaptation-and-expansion-gate.md)
without another research-direction selection.

## 1. Deliverable and exact boundary

The [controller](../scripts/paper329/runner.py) implements the initial
eight-run study: independent reference versus the same reference plus the
fixed hardest-attack term, four held-out targets, seed20260917. It provides
read-only preparation, hash checking, explicit approval, supervised fitting,
source calibration/thresholds, prediction, paired analysis and a separate
saved-checkpoint reconstruction process.

The [specification](paper327/specification.json) and
[public execution plan](../results/phase1/paper329-execution-plan-v2.json)
bind the recipe and inventory. Private execution-plan SHA256:

`87786e1c0a2fd0f3d5ae022414d5fae6da1bb4efc1746db61c42c55413e0c691`

Preparation bound **7492 files** in30.830s, including7474 accepted RGB224
crops, original manifest/partitions, verified local pretrained DINO weights,
the integrated probe and CC0 profile assets. It read crop bytes for hashing,
but decoded no PAD images, fitted no PAD model and generated no PAD
predictions. A separate `--check` successfully revalidated the complete plan.
No owner approval, attempt or scientific fit-start record existed at sealing.

This package is not approval. The additional16 training runs are not
implemented as an automatic continuation and cannot start under its authority.
The preserved v1 plan/probe were unapproved preparation snapshots. The final
v2 adds explicit orphan-worker detection: loss of the recorded supervisor
parent stops the worker at its next guard. The unchanged model/data recipe
was re-probed and all inputs re-sealed; only v2 is executable by this controller.

## 2. Full reconstructed reference, not a BCE-only stand-in

[Feng's primary paper](https://arxiv.org/html/2604.19196v2) supplies the chosen
components: DINOv2-Reg B/14, all layers trainable,224 input, FAS-Aug/PDA,
global classification and APL; batch32, AdamW, head LR5e-5, encoder LR5e-6,
maximum200 epochs, source-only early-stopping reconstruction with patience20.
The [model](../scripts/paper329/model.py) has separate two-logit global and
patch heads; [training](../scripts/paper329/training.py) implements the fixed
sampling, source-only validation and no post-selection refit.

Actual final-block QKV output is captured without changing DINO's SDPA
attention backend. The hook reconstructs CLS attention over261 tokens,
excludes CLS and four register tokens, averages heads, renormalizes256 image
patch weights and detaches them. APL uses those weights and PDA-consistent
patch labels. The same attention path and architecture apply in both arms.
Patch feature L2 scale16, separate heads and the stated attention reduction
remain researcher-fixed choices, not verified unpublished author settings.

The source-validation criterion is unaugmented, equal-source/equal-class
global cross-entropy, identical for both arms. The extra term is not a
checkpoint-selection criterion. The earliest strictly best epoch is retained;
only200 epochs or the complete20-epoch patience rule permits successful
termination. Partial recipes, timeouts and numerical failures are not success.

### Eight augmentation families and label audit

The primary rules are in
[Cai et al., sections3.1.1-3.1.3](https://arxiv.org/html/2409.03501v1).
The [independent implementation](../scripts/paper329/augmentation.py) uses:

| Family | Label rule | Fixed construction |
|---|---|---|
| Hand motion | Preserve original | Four line-kernel directions, integer size3-16, reflected border |
| Low resolution | Preserve original | Uniform scale1/6-1, nearest-neighbor down/up sampling |
| Camera color diversity | Preserve original | ICC RGB-to-RGB mapping |
| Screen reflection | Set attack | Background blend gamma0.03-0.2 |
| Display moire | Set attack | Subpixel-layout/projective texture blend gamma0.01-0.3 |
| Clustered halftone | Set attack | Gray downsampling, ten levels, explicit3x3 dot ranks, blend0.01-0.2 |
| Printer color distortion | Set attack | RGB-to-CMYK conversion then CMYK-to-RGB ICC mapping |
| Blue-noise halftone | Set attack | Six texture modes, eight seeded instances/mode, blend0.01-0.4 |

Generic capture degradations are **not relabeled attack**. Recapture
simulations use the primary paper's spoof-label rationale.
Standard flip/rotation/brightness, FAS-Aug probability0.2, PDA probability0.2
and per-patch replacement probability0.5 are common to both arms.

### Explicit reconstruction departures and asset rights

The paper-linked FAS-Aug repositories did not provide a verified reusable
license in the checked repository inventory. **No code or photographs from
them were copied.** Newly written code implements the published concepts.

The [asset helper](../scripts/paper329/assets.py) acquired13 small CC0 files:
eleven RGB profiles, one CMYK profile and the license from
[Compact-ICC-Profiles](https://github.com/saucecontrol/Compact-ICC-Profiles/tree/bdd84663061bc4ae95ca70decff54f581e27f702).
The acquisition receipt pins revision and every byte digest. A separate
receipt file is also bound. Assets remain in the native cache, not distributed
as unlicensed author artifacts.

This is **not exact Feng or exact original FAS-Aug reproduction**:

* The RGB pool is independently selected; the CMYK pool has one profile,
  not the paper's seven. The effective color distribution therefore differs.
* Ninety procedural colored-rectangle backgrounds replace unlicensed internet
  photographs. Their appearances are not equivalent to the original scenes.
* Nineteen generated subpixel layouts with ten seeded projective instances
  replace the original layout assets. Each instance applies1-10 projective
  warps with corner radius0.1 of1024 pixels.
* Clustered-dot ranks are explicitly fixed in code. The blue-noise path uses
  high-pass spectral shaping and rank remapping, **not** the paper's
  void-and-cluster generator. Modes/alpha handling are explicit.

These are disclosed independent reconstruction choices, not claims that
unreported author code has been recovered. All eight families are present,
but their fidelity and competitive PAD performance remain unmeasured.
Conclusions must be relative to this reconstruction, not presumed original
paper strength or SOTA parity.

Keep the previously declared single-middle-frame/aligned-crop preprocessing,
SiW local intersection instead of Replay-Attack, source-only threshold
selection and unknown-SiW-subject limitation. The original paper's five-frame
dlib/MICO and test-EER operation are not reproduced. Frozen DINO518 is
historical context, not a matched frozen/adapted ablation; no extra arm is added.

## 3. Paired data and actual learning objective

Addressed NumPy RNG streams depend only on seed/epoch/step/attempt, never
model optimizer RNG. The two arms receive identical accepted source examples,
FAS-Aug choices, donor identities, PDA masks and redraw outcomes at common
steps. Six source/class strata supply five draws each plus two rotating extra
draws per32-image batch.

After label-changing augmentation, any missing source/class triggers a
whole-batch redraw in **both arms**, with at most32 attempts before explicit
failure. No zero-loss fallback or candidate-only resampling. PDA donors are
same-source, post-FAS-Aug bona-fide fitting samples, copied before any PDA.
Global spoof labels stay spoof while replacement patches become bona fide.

Private JSONL traces record source/class counts, redraw counts, selected
fitting indexes, augmentation families, donor indexes and full mask/batch
digests. Reconstruction checks their hashes and verifies every declared
optimizer step plus exact paired identity over common training steps.
Different early-stopping lengths are permitted under the same selection rule.

The existing tested [objective](../scripts/paper327/objective.py) is named
**source-balanced hardest-attack ranking with cross-source bona-fide comparison**.
It averages `softplus(1 + b - a)` equally across bona-fide sources, takes the
declared upper-tail mean within each attack source and averages attack sources.
Margin1, fraction1/20, additional weight0.1 remain fixed.

Under these32-image batches, accepted post-augmentation source/class support
leaves at most11 attacks/source. Hence `n * 0.05 <= 1`: the empirical tail
term is the hardest attack, not a resolved5% pAUC region. The5% evaluation
constraint does not prove that the loss optimizes population pAUC.
Global, APL, hardest-attack and total losses are separately logged in both
arms; the reference logs the hardest term but gives it zero training weight.
All used gradients must be finite and first-block QKV gradients nonzero.
The unused, unmasked DINO mask token is the explicit no-gradient exception.

### Compact closest-loss comparison

| Existing objective | Relation and distinction |
|---|---|
| Feng global classification + attention-weighted patch supervision | Our reconstructed reference retains these; the candidate adds global-logit hard-pair pressure, not a new patch-attention mechanism |
| [FAS-Aug SARE, section3.2](https://arxiv.org/html/2409.03501v1) | Equalizes variance of domain-level spoof empirical risks; our term selects hardest pairwise attack ranking within sources rather than minimizing variance of source attack risks |
| [LibAUC DRO-CVaR pAUC](https://docs.libauc.org/api/libauc.losses.html#libauc.losses.auc.pAUC_CVaR_Loss) | Existing hard-negative pairwise tail optimization; our source balancing/order of averaging is not mathematical equivalence or evidence of new CVaR/pAUC theory |

Measured benefit over this reference would support an empirical incremental
answer, not by itself establish methodological novelty or Q3 acceptance.

## 4. Corrected gate: one rule, sealed before outcomes

The [gate](../scripts/paper327/gate.py), specification and327 prose were amended
together. The unsafe-reference counterexample from328 now passes: joint
utility0/4 becomes4/4 despite removing unsafe acceptances.

Count a target once as improved when candidate achieves FA<=5%, BFA>=50%
and reference does not, **or** both are FA-safe and BFA gain is at least5pp.
Require at least two improved targets, at least one additional joint-utility
target, zero newly FA-unsafe targets where reference was safe, and no BFA
regression greater than5pp **where both policies are FA-safe**.

Exact original integer counts define every boundary. Missing policies,
missing targets and unequal paired supports fail explicitly. All other
FA/BFA changes are retained without using unsafe-reference acceptance as a
same-security usability veto. AUROC/oracle-only improvements do not pass.

The controller calls this gate only after all eight contexts reconstruct
and exactly eight training plus eight calibrator starts are verified. Passing
means eligibility for owner review, not statistical significance, population
security certification, untouched-target confirmation or automatic expansion.
Failure ends this objective without retuning, fusion or another encoder.

## 5. Integrated synthetic GPU measurements

The [immutable receipt](../results/phase1/dino329-integrated-probe-v2.json)
comes from the [integrated probe](../scripts/paper329/probe.py), using existing
`fas`, local verified pretrained weights and RTX4080 SUPER. All eight
families were explicitly executed; timed batches use the actual probability
rules. Texture/ICC caches are reset equally for both arms.

| Integrated synthetic arm | Measured mean step | Peak allocated | Peak reserved |
|---|---:|---:|---:|
| Reference, including FAS-Aug/PDA/APL |0.28758s|6.405GiB|6.850GiB|
| Same reference +0.1 hardest-attack term |0.27994s|6.405GiB|6.850GiB|

Batch32, RGB224, FP32, no AMP/TF32, two warmup and three measured steps/arm.
Initial full-model byte fingerprints and all five paired batch traces matched.
Each checkpoint was346,413,719 bytes; reload in both the current and a separate
process produced **exactly equal logits** on the synthetic six-image fixture.
Checkpoint saving, synthetic validation/calibration and separate-process replay
were exercised. Whole probe wall time13.510s; parent peak RSS2.29GB decimal;
conservative sum of parent/child RSS peaks4.58GB decimal, below6GiB.
Three timings per arm do not establish an overhead difference; the slightly
faster candidate in this repetition is not a speed-benefit claim.

The10 DINO optimizer steps in this published receipt are synthetic. Three
earlier successful development probes also used10 each. An initial synthetic
backward stopped because PyTorch lacks deterministic
`upsample_bicubic2d_aa_backward_out_cuda`. The implemented policy is therefore
explicitly seeded **not bitwise-deterministic training**, identical in both
arms, rather than a caught exception silently relaxing settings. Inference
checkpoint reconstruction passed bit-exactly for the tested fixture.

These are short engineering measurements, not training throughput guarantees
or PAD performance. Real image I/O, full epochs, full validation/calibration
populations, all target predictions and full cluster bootstrap remain excluded
from this probe. CPU fixtures separately exercise the actual training loop's
21-epoch patience termination, selected-state restoration and prediction.

## 6. Bound eight-run execution and limits

| Held-out target | Fitting usable /arm | Validation usable /arm | Maximum steps /arm |
|---|---:|---:|---:|
| OULU-NPU |837|277|5400|
| CASIA-FASD |2492|949|15600|
| MSU-MFSD |2567|974|16200|
| SiW local intersection |2012|791|12600|

Total maxima: eight training starts, eight source-only calibrator fits,
1600 epochs and99,600 optimizer steps. Early stopping is governed only by
the fixed source criterion. No pretrained PAD weights or model downloads.
Official source test partitions and the held-out target cannot enter fitting,
selection or calibration. Original failures stay nonaccept; no fabricated
failure scores enter usable-only AUROC.

Positive-affine source calibration, strict source attack order-statistic
thresholds, alpha1/20 primary and1/100/1/10 sensitivities retain the319/324
contract. Analysis retains every target/arm/alpha, oracle diagnostics and
2000 paired original-cluster bootstrap draws; SiW uses video/exact-frame
grouping, not a fabricated participant-disjoint claim. The metric adapter's
paired intervals are tested against the existing321 implementation.

Ceilings are **not completion-time predictions**:

* 72h nonresettable total, tied to approval monotonic time and boot ID.
* 6h per training/validation/calibration/prediction context.
* 54h worker total, including up to6h aggregate analysis;12h reconstruction.
* 12GiB own GPU reserved/allocated;6GiB combined sampled RSS;32GiB owned outputs,
 including a256MiB operational reserve.

An independent supervisor samples process-group RSS, disk usage and active
phase clocks. Worker guards also check GPU peaks. Direct worker/reconstruction
entry requires the recorded supervisor parent; each worker guard also checks
that this parent is still present. Every training/calibrator
start is immutable and restricted to the declared inventory. One attempt only;
no automatic retries, clock reset, recovery refits or shortened success after
timeouts/OOM/numerical errors. Stop preserves artifacts and writes an explicit
failure terminal; no empty-success or “timeout as contribution” path.

## 7. Verification and single execution decision

Producer validation in existing `fas`: **604 tests passed in280.816s**,
including the328 counterexample, security/gain/regression boundaries, missing
policy failures, LF-normalized historical receipt pins, paired augmentation,
source/donor exhaustion,32-attempt failure, full attention readback, losses,
early stopping, trace coverage, prior-analysis equivalence and supervised
child-failure/no-retry and orphan-worker handling. Canonical schema, local syntax/link checks
and exact-plan revalidation are separate checks.

[Completed324](324-completed-comparison-results-and-paper-update.md) remains
byte-identical under its exporter verification, including aggregate SHA256
`5dea308b3170310dc14017166e4af196fdcdfb1d95a35be41f56e1f7b12e32c6`.
The existing manuscript has not been filled with synthetic PAD results.

Read-only revalidation:

```bash
/home/lathevinh/miniforge3/envs/fas/bin/python scripts/paper329/runner.py --check
```

**Only after the owner explicitly approves this exact package**, record:

```bash
/home/lathevinh/miniforge3/envs/fas/bin/python scripts/paper329/runner.py \
  --approve \
  --plan-sha256 87786e1c0a2fd0f3d5ae022414d5fae6da1bb4efc1746db61c42c55413e0c691 \
  --answer approve_paper329_eight_runs_independent_reconstruction_source_only_SiW_limits_72h_no_retry
/home/lathevinh/miniforge3/envs/fas/bin/python scripts/paper329/runner.py --execute
```

The commands above are documentation, not evidence that they ran.
At publication: **zero scientific starts, zero new target predictions,
no execution authority granted**. Next action is the single exact-plan
decision, not another implementation-direction proposal.

## 8. Subsequent owner approval and verified start

After publishing package commit `58d92228de25eff4ec87c2636f7c56344d2410ab`,
the owner explicitly selected the exact-plan execution answer documented
above. The approval receipt binds the final v2 SHA256 and starts the
nonresettable clock; no sealed code, specification or input was changed.

The supervisor was launched persistently, independent of this chat turn.
Readiness verification observed its live process, the first declared training
start and a completed real OULU-held-out reference epoch. This is training
progress, **not** a completed comparison or target-performance result.
Only the approved eight runs may execute; no additional seeds or automatic
retry. Subsequent live progress is in the private worker log/active marker,
not the static preparation snapshots.
