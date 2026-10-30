# 327 - Controlled DINO adaptation: independent reconstruction preparation

Status: **preparation, not an executable or authorized scientific run.**
Follows [recommendation326](326-recommendation-dino-adaptation-and-low-fa-controlled-study.md).
The owner selected **independent paper-based reimplementation**, rather than
waiting for author training code. This decision removes the requirement to
obtain that code; it does not establish reproduction fidelity or authorize
eight training runs.

## 1. Decision and reference audit

Use the full vision-only pipeline described by
[Feng et al.](https://arxiv.org/html/2604.19196v2), not a BCE-only substitute:
all-layer DINOv2-Reg ViT-B/14 adaptation, FAS-Aug, PDA, global classification
and attention-weighted patch loss (APL). The two arms differ only by one
additional declared tail-ranking term.

The paper specifies 224 inputs, batch32, AdamW, head LR5e-5, encoder LR5e-6,
maximum200 epochs, patience20, FAS-Aug probability0.2 and PDA probability0.2.
Within PDA, live-patch replacement probability is0.5.
No released training implementation was located in the checked primary
sources: the [official project](https://gsisaoki.github.io/FAS-VFMbenchmark-CVPRW2026/)
and the author's public repository search. A related project repository was a
website for another paper, not the desired implementation. This is a bounded
search result, not proof that code exists nowhere.

**Do not label our eventual implementation “author-code reproduction” or
reproduce the paper's performance claims.** Our accepted single middle-frame
aligned crops, SiW local intersection instead of Replay-Attack, source-only
checkpoint selection and source-calibrated operating thresholds depart from
the paper's five-frame/dlib/MICO description and testing-set EER threshold.
Existing frozen DINO518/CLS-plus-mean-patch results are historical context,
not a matched224/class-token control.

## 2. Concrete contract and remaining integration

The [machine-readable specification](paper327/specification.json) separates:

1. Settings stated in the paper.
2. Researcher-fixed **proposed reconstruction choices**, not author settings.
3. Measured synthetic evidence.
4. Outstanding execution blockers.

The proposed reconstruction uses a two-logit global head and a separate
two-logit patch head, feature-normalization scale16, final-block CLS-to-image
attention averaged across heads, renormalized after excluding register/CLS
tokens and detached as APL weights. Its optimizer details, augmentation
ranges, class/source reductions and validation rule are explicitly recorded,
not inferred to be Feng's unreported implementation.

Both arms must share initialization, addressed data/augmentation RNG streams,
sampling, source-only selection and training opportunity. Label-changing
FAS-Aug makes original class balance insufficient. The proposed common
sampler redraws an entire augmented batch if any source loses either
post-augmentation class, at most32 attempts before explicit failure. It
never silently returns zero tail loss or changes sampling only for the
candidate. This conditional sampling is another disclosed reconstruction
choice. PDA uses source-fitting bona-fide donors; patch labels follow the
replacement mask while the spoof image label stays spoof.

**The full reconstruction is not implemented yet.** The eight FAS-Aug
transforms, their parameters and label rules still need primary-reference
audit; any borrowed implementation requires license verification. The
attention/APL path, augmentation integration, paired randomness and source
evaluation need implementation and integrated tests. No arbitrary substitute
is accepted as complete FAS-Aug, and a backbone-only benchmark cannot close
these blockers.

## 3. One fixed low-FA candidate, with prior-art limits

The implemented [objective](../scripts/paper327/objective.py) uses attack-high
global logits. For an attack score `a` and bona-fide score `b`, pair hardness
is `softplus(1 + b - a)`. Average first within each bona-fide source and then
equally across sources. Take the upper5% empirical hardness tail separately
within each attack source, then average attack sources equally.

The candidate loss is `L_reference + 0.1 * L_tail`. Margin1, fraction1/20 and
weight0.1 are fixed proposals, not target-selected settings. Fractional tail
mass is exact; stable sorting defines a tie-subgradient choice.

This is **not a new CVaR/pAUC algorithm**. Existing
[LibAUC DRO-CVaR partial-AUC loss](https://docs.libauc.org/api/libauc.losses.html#libauc.losses.auc.pAUC_CVaR_Loss)
already emphasizes hard negative pairs in a bounded-FPR region. With our
score orientation, attacks correspond to false-accept negatives in the
accept-class interpretation. Our source balancing and order of averaging
and tail aggregation are not mathematically identical to that objective;
there is no proof here that the candidate optimizes population pAUC.
A comprehensive closest-PAD-loss novelty clearance remains open.

**Important resolution limit:** batch32 across three sources and two classes
provides only5-6 attacks/source. A5% empirical tail is then the single hardest
attack, not a resolved population5% tail. This must remain in the eventual
method and limitations, even if measured results are favorable.

The [tests](../tests/test_paper327.py) cover hand-calculated values, fractional
mass and gradients, attack/BF gradient directions, permutation/shift/
duplication invariance, autograd gradcheck and invalid-input failures.

## 4. Actual synthetic GPU evidence

Used the existing `fas` conda environment, local verified pretrained DINO-Reg
checkpoint and RTX4080 SUPER. No new environment or checkpoint download.
The [receipt](../results/phase1/dino327-synthetic-probe-v1.json) records:

| Synthetic engineering proxy | Mean measured step | Peak allocated | Peak reserved |
|---|---:|---:|---:|
| Global BCE |0.18946s|6.407GiB|6.748GiB|
| Same BCE +0.1 tail |0.19304s|6.407GiB|6.732GiB|

Full-backbone batch32, RGB224, FP32, no AMP/TF32;86,583,552 trainable backbone
parameters and769 proxy-head parameters. Finite nonzero gradients reached
the first attention block. Each arm used two warmup and three measured steps.
Whole probe wall time5.362s, peak process RSS1.711GiB.

The [probe](../scripts/paper327/probe.py) is explicitly a one-logit
engineering proxy, **not** the proposed two-logit/full-pipeline reconstruction.
It excludes FAS-Aug, PDA, APL, real image I/O, validation, calibration,
reconstruction and bootstrap. These timings do not estimate completed
scientific runtime or demonstrate PAD improvement. Seeding was used but
bitwise deterministic algorithms were not enabled.

Scientific training starts: **0**. Dataset image reads: **0**.
Target evaluations: **0**. Saved trained checkpoints: **0**.
Synthetic optimizer steps:10.

## 5. Eight runs and a testable, proposed expansion gate

Initial inventory: reference versus reference+tail, four train-three/test-one
rotations, seed20260917: **eight training starts and eight calibrator fits**.
Preserve the accepted source fit/validation/calibration partitions, exclusions,
original failure denominators and SiW unknown-subject limitation. Checkpoint
selection uses unaugmented, equal-source/equal-class source-validation global
cross-entropy in both arms, never target labels or the extra tail term.
Calibration and strict source-derived thresholds retain the319/324 contract.

At primary FA<=5% and BFA>=50%, all of the following proposed gates must hold:

* All eight runs complete and independently reconstruct; no missing primary
  policies or target rows.
* At least **two targets** have both policies FA-safe and candidate BFA gain
  **at least5 percentage points**.
* Candidate joint-utility target count exceeds reference by **at least one**.
* **Zero** newly FA-unsafe targets where the reference is FA-safe.
* No target BFA regression **greater than5 percentage points**.

The [gate](../scripts/paper327/gate.py) evaluates exact integer counts on
identical original supports; tests include equality boundaries and missing
policy failures. It does not evaluate completion/reconstruction receipts;
the future controller must verify those before calling it. Missing policy
is explicit, not converted into a zero-valued observation. AUROC and oracle
gains alone do not pass.

Passing means **eligible for owner review**, never automatic expansion.
Only separate approval permits the other two seeds:16 additional training
starts and16 calibrators,24 training starts total. These are exploratory
observed targets, not independent confirmation. Failing stops this objective,
not a hidden retuning, fusion or backbone search. The numeric gate itself
remains a review proposal until the execution plan is approved.

## 6. Resource and readiness boundary

Proposed stop ceilings, **not measured completion estimates**:
72h total;6h per training/validation/calibration/prediction context;
12h total independent reconstruction;6h aggregate analysis;
12GiB GPU reserved;6GiB combined worker/supervisor RSS;32GiB owned outputs.
Phase work must also fit the global deadline. No automatic retry, extra fit
or shortened “successful” recipe after timeout/OOM/numerical failure.

These are not yet a sealed execution budget. Before scientific execution:

1. Audit and implement the complete independent reference and disclosed choices.
2. Test full FAS-Aug/PDA/APL, source isolation, paired controls and failure paths.
3. Benchmark that actual integrated recipe on synthetic data; measure costs
   omitted from the present probe and preflight bound private inputs.
4. Seal code/recipe/input hashes, all phase caps, exact inventory, checkpoint
   reconstruction and reporting contracts.
5. Obtain approval of that exact execution package.

[Completed324 evidence](324-completed-comparison-results-and-paper-update.md)
and the [existing manuscript](paper319/manuscript.md) remain unchanged.
Nothing in this preparation establishes novelty, a successful operating
policy, submission readiness or Q3 acceptance.

## 7. Preparation verification

The existing `fas` interpreter passed all601 repository tests, including
seven327 checks, in257.214s. Python3.12 AST parsing passed for all four new
Python files; the editor syntax tool could not locate these workspace files,
so no Pylance validation is claimed. Specification inventory and local links
passed. The327 receipt test binds the measured probe to the unchanged probe
and objective code hashes.

`paper324/export.py --verify` reproduced all six immutable exports, including
aggregate SHA256
`5dea308b3170310dc14017166e4af196fdcdfb1d95a35be41f56e1f7b12e32c6`.
This verifies preservation of prior evidence, not scientific readiness of327.
