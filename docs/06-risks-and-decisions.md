# Risks, Alternatives, and Decisions

This file records design arguments rather than presenting the current proposal as
settled fact.

## Decision 1: Preserve branch independence

**Chosen:** DINO and VLM predictors train independently. Their outputs are compared
post hoc through disagreement and a source-only failure-risk estimator.

**Alternative:** project DINO patches directly into the VLM text space and compute
patch-text cosine similarity.

**Reason:** native spaces are not aligned, learned patch-text alignment is close to
existing work, and forcing decision agreement destroys the proposed cross-branch
failure signal.

**Counterargument:** plain cross-model disagreement is standard ensemble machinery.

**Required test:** demonstrate source-only generalization beyond MSP, entropy, energy,
representation-space confidence, fixed averaging, capacity-matched risk baselines,
and learned score fusion.

## Decision 2: Structured VLM, not free-form MLLM

**Chosen:** CLIP/SigLIP-style concept scores for the core model.

**Alternative:** ask an MLLM to generate a rationale and attack label.

**Reason:** structured outputs are cheaper, deterministic, calibratable, and easier
to evaluate. MLLM captions may still generate offline annotation candidates.

**Counterargument:** global image-text models can miss tiny forensic artifacts.

**Mitigation:** DINO owns local artifacts; evaluate regional semantic scoring.

## Decision 3: No agreement objective in version 1

**Chosen:** do not minimize feature, evidence, or decision disagreement.

**Alternative:** confidence-weighted consistency on known source attacks.

**Reason:** forced agreement can propagate VLM errors, collapse branch diversity,
and directly weaken the signal used for failure detection under shift.

**Counterargument:** unconstrained branches may disagree for irrelevant calibration
or scale reasons.

**Mitigation:** independently calibrate source scores, compare multiple normalized
disagreement measures, and learn a regularized calibrator from out-of-fold sources.

## Decision 4: Physical PAD first

**Chosen:** bona fide, print, replay, and mask attacks.

**Alternative:** jointly include deepfake and face forgery.

**Reason:** presentation attacks and digital manipulation have different threat
models and artifacts. A narrow first paper permits defensible evaluation.

## Decision 5: Strict-source main protocol

**Chosen:** the primary MCIO results use only the three designated source PAD datasets
plus generic foundation-model pretraining. CelebA-Spoof is an explicit extra-data
ablation.

**Reason:** silently adding a large labeled PAD dataset would make comparison unfair
and weaken the source-only claim.

## Major risks

### Shared shortcuts

Both branches may learn dataset, camera, background, or compression cues and agree
for the wrong reason.

Mitigation: cross-domain evaluation, nuisance interventions, background/face
ablations, sensor stratification, and shared-error analysis.

### Disagreement misses shared failures

Both branches may confidently accept the same attack, yielding low disagreement.

Mitigation: report double-fault rate and shared-failure subgroups; compare disagreement
with image quality and single-branch uncertainty. Do not interpret failure risk as a
generic unknownness detector.

### Reliability-calibrator leakage

A gate trained on in-sample branch predictions can learn unrealistically clean error
patterns, while a gate tuned on the target invalidates domain-generalization claims.

Mitigation: generate risk-model training records only through held-out source-domain
or held-out attack-family folds. Permanently exclude $G_{domain}$ or $G_{attack}$ from
every base/risk fit, select only the corresponding final gate threshold on genuinely
out-of-sample predictions, and never refit with either holdout. Select spoof-only
routing on a separate validation partition.

### Fold-threshold reconstruction

The tuple $(\widehat p_D,\widehat p_V,m_F)$ algebraically reveals each OOF fold's
$\tau_{ref}^{(k)}$ and may act as a fold/domain identifier.

Mitigation: exclude $m_F$ from scientific $\Delta_{CF}$ and $\Delta_{dis}$ models;
measure it only as the separate operational $\Delta_{margin}$ contribution and retain
the OOF domain-identifiability audit.

### Apparent diversity from a weak branch

Large $P_{cw}+P_{wc}$ may arise because both predictors are weak rather than usefully
complementary.

Mitigation: require the frozen source-only competence rule, then report joint
correctness/double fault and one directional rescue summary with event counts. These
are diagnostics, not continuation gates; RQ2 uses the matched whole-system comparison.

### Meta-selection leakage

Risk-model flexibility can overfit concatenated OOF records even when branch
predictions are honestly held out.

Mitigation: preregister fixed-regularization logistic regression as primary. Treat
nested pseudo-domain model selection as sensitivity analysis, normalize using
source-side statistics, and audit OOF domain identifiability.

### Selective-metric denominator gaming

Covered-sample APCER can improve trivially when the gate abstains on most attacks.

Mitigation: always report attack and bona-fide coverage, covered-sample error rates,
and end-to-end false acceptance with explicit denominators under a fixed transaction
retry policy.

### Semantic evidence is too coarse

VLMs may identify `phone` or `paper` only when boundaries are visible, while tight
face crops remove them.

Mitigation: face/context views and explicit crop ablation.

### Synthetic cue invalidity

Generated moire or halftone may be easy synthetic shortcuts rather than realistic
physics.

Mitigation: use synthetic interventions for directional/causal tests, not as a
replacement for real attack evaluation.

### Label noise

Dataset attack labels do not prove that a specific cue is visible in every frame.

Mitigation: concept confidence, missing labels, human audit, positive-unlabeled
treatment where appropriate.

### Consistency collapse

Fine-tuning both branches on the same labels may make them copies even without an
explicit consistency loss.

Mitigation: frozen-backbone kill experiment first, branch-specific model selection,
error-diversity measurements, and no joint fine-tuning in version 1.

### Publication overlap

The field is moving rapidly; current work already covers semantic consistency,
confidence-aware FAS, reliability-aware VLMs, DINO prompting, and compositional
forensic prompts.

Mitigation: monthly literature delta search and explicit comparison against the
closest methods.

### Generic ensemble diversity

Cross-foundation rescue may be no stronger than diversity from ordinary independently
trained predictors.

Mitigation: use frozen DINOv2 without Registers as the required matched same-family
control for the complete-system comparison. A shared-encoder DINO head-diversity
analysis is an optional appendix diagnostic and is not an RQ1/RQ2 gate.

### Potential rescue is not realized rescue

A VLM may correctly block DINO false accepts while calibrated averaging fails to use
that information.

Mitigation: report both branch-level $REF_{VLM}/FARR_{VLM}$ and deployed-fusion
$REF_g/FARR_g$. Compare heterogeneous and same-family rescue on the same DINO failures
using paired subject/video inference.

## Open decisions

- What source-derived minimum meaningful effect and harm tolerance are supportable
  after the event-count audit?
- Which target journal and category define the Q3 requirement?

## Decisions closed at methodology freeze

- Primary VLM: OpenCLIP `ViT-B-16`, `laion2b_s34b_b88k`, native 224-pixel
  preprocessing, and one fixed 1.30 context crop in all folds.
- Primary DINO pooling: fixed class token concatenated with mean-pooled patch tokens;
  learned attention pooling is secondary.
- Primary risk records: domain-OOF for MCIO; matched sample-OOF is the attribution
  control. Attack-OOF is separate and only required for an attack-shift claim.
- Core continuation: failure-ranking and selective-utility evidence. Fusion rescue,
  explicit disagreement, and conditional routing each govern only their own claims.
