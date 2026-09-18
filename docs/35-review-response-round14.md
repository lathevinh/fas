# Response to Review Round 14 - Core Methodology Frozen

Date: 2026-09-18

## Decision

The owner accepts the Round-14 review and its three requested methodology changes.
The review correctly separates scientific validity from the premature executable
readiness work in Rounds 11-13.

**RESEARCH DIRECTION ACCEPTED. REVISED CORE METHODOLOGY FROZEN FOR IMPLEMENTATION
PLANNING.**

This is authorization to prepare a dependency-ordered implementation and experiment
plan. It is not authorization to inspect target labels, and it does not turn any
hypothesis into an observed result. Existing configs, validators, and tests remain
provisional until reconciled with the frozen method.

## Decision 1: fixed primary VLM and pooling

The primary system uses one globally fixed VLM in every MICO fold:

- OpenCLIP `ViT-B-16`;
- `laion2b_s34b_b88k` pretrained weights;
- checkpoint-native tokenizer and normalization at 224 pixels;
- the existing immutable generic binary core prompt bank;
- one fixed 1.30 context crop.

This choice is made a priori for scope and compute control, not from target results.
The ViT-L/14 candidate, alternative preprocessing, and source-tuned prompts move to a
secondary robustness study. They cannot replace the primary confirmatory system.
Consequently, a held-out pseudo-domain cannot influence a VLM selector that produced
its risk record.

The primary frozen DINO representation is the class token concatenated with mean-pooled
patch tokens. Learned attention pooling is secondary. This makes pooled-feature caching
lineage-safe and avoids an unnecessary fold-trained component. If attention pooling is
later run, it must use frozen patch-token caches generated per view and preserve
fold-local fitting lineage.

## Decision 2: independent claim structure

The core paper asks whether source-domain cross-fitted error supervision improves
transferable failure ranking and selective security-usability for a fixed heterogeneous
classifier. Its primary evidence is prediction-error AUPR plus selective utility and
class-specific harm accounting on four strict outer-domain-unseen MICO folds.

The following claims are tested separately:

1. **Cross-fitting:** domain-OOF must improve over matched sample-OOF risk training on
   identical final base predictions.
2. **Heterogeneous predictive value:** the heterogeneous risk system must beat both
   single-branch learned-risk controls and the DINOv2-Reg plus plain-DINOv2 same-family
   system at the endpoint being claimed.
3. **Classifier benefit:** fusion rescue, net APCER change, and BPCER/BFNR change
   determine only whether fusion improves PAD classification.
4. **Explicit disagreement:** absolute difference enters the framing only if it beats
   a capacity-matched nonlinear probability-only risk model.
5. **Routing:** compute saving is optional and determines only a routing claim.

Fusion rescue is therefore not a logical prerequisite for failure-risk transfer.
FARR remains descriptive because it sees only one direction of attack changes. The
classifier analysis must also count attacks newly admitted by fusion and report net
APCER and bona-fide harm at source-selected thresholds.

## Decision 3: minimum paper scope

The core consists of frozen DINOv2-Reg, the fixed OpenCLIP primary, independent affine
branch calibration, calibrated-average `g_ref`, source-domain OOF risk training,
strict target-blind abstention evaluation, and the required attribution baselines.
Conditional routing, latency ceilings, LoRA, distillation, generative MLLMs, cue
ontologies, localization, and evidence maps are not minimum-paper requirements.

SiW-M remains a separate attack-shift track if access and protocol verification
succeed. If it is unavailable, the attack-shift claim is removed before evaluation;
it is not replaced after viewing results. The four-fold MICO domain-shift study remains
the core.

## Frozen inference rule and evidence boundary

Before any outer-target result is viewed, source-only information must determine the
minimum meaningful gain, harm tolerance, and resampling procedure. The primary paired
four-target macro gain passes only with:

- a positive lower confidence bound;
- at least three of four positive target point estimates;
- no target beyond the preregistered class-specific harm tolerance;
- at least two of three seeds with positive four-target macro deltas.

Event counts determine whether a planned endpoint is estimable, not whether its
threshold may be moved after target inspection. Underpowered endpoints are reported as
inconclusive. AUPR comparisons use paired within-target deltas and disclose error
prevalence. Selective tables report attack and bona-fide coverage, `FA_end2end`, and
`BFNR_end2end`; covered accuracy alone is insufficient.

## Feasibility and novelty verdict

The study is feasible in GPU memory on one RTX 4080 16 GB with sequential frozen
encoders and fixed pooled-feature caching. Runtime is not yet measured. Dataset access,
subject/video lineage, independent error counts, and storage/I/O are the practical
risks to audit first.

The novelty is appropriate as a conditional empirical-method contribution, not as a
new ensemble, calibration algorithm, or foundation architecture. A defensible paper
requires positive evidence for transferable error ranking, selective utility, the
source-domain cross-fitting comparison, and heterogeneous advantage at the claimed
endpoint. Failure of those results requires reframe or stop; failure of fusion rescue,
explicit disagreement, or routing only removes the corresponding optional claim.

## Handoff

The normative charter, novelty boundary, research questions, method, protocol, risk
register, and evidence plan now encode these decisions. The next artifact should be an
implementation plan that maps each frozen scientific requirement to data audits,
lineage checks, modules, tests, and staged experiments. No model implementation or
confirmatory target evaluation is started by this response.
