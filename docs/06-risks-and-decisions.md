# Risks, Alternatives, and Decisions

This file records design arguments rather than presenting the current proposal as
settled fact.

## Decision 1: Preserve branch independence

**Chosen:** DINO and VLM predictors train independently. Their outputs are compared
post hoc through disagreement and a source-only failure-risk calibrator.

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

**Chosen:** the primary MICO results use only the three designated source PAD datasets
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
with image quality and single-branch uncertainty. Do not claim complete unknown detection.

### Reliability-calibrator leakage

A gate trained on in-sample branch predictions can learn unrealistically clean error
patterns, while a gate tuned on the target invalidates domain-generalization claims.

Mitigation: generate risk-model training records only through held-out source-domain
or held-out attack-family folds and freeze all thresholds before target inference.

### Apparent diversity from a weak branch

Large $P_{cw}+P_{wc}$ may arise because both predictors are weak rather than usefully
complementary.

Mitigation: require standalone competence, two-sided recovery, low double-fault,
oracle gain over the better branch, and achievable fusion gain.

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

## Open decisions

- Which exact OpenCLIP/SigLIP checkpoint gives the best accuracy/compute tradeoff?
- Does the VLM consume the context crop, face crop, or both?
- Which source-fold construction best approximates unseen domain and attack shifts?
- Which low-capacity calibrator avoids overfitting the out-of-fold records?
- What pre-registered minimum oracle/fusion gain justifies continuing?
- Is abstention evaluated per image or per authentication transaction?
- Which target journal and category define the Q3 requirement?
