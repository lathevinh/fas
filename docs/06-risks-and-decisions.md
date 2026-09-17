# Risks, Alternatives, and Decisions

This file records design arguments rather than presenting the current proposal as
settled fact.

## Decision 1: Separate evidence spaces

**Chosen:** DINO produces forensic evidence; the VLM produces semantic evidence;
comparison occurs through an explicit ontology.

**Alternative:** project DINO patches directly into the VLM text space and compute
patch-text cosine similarity.

**Reason:** native spaces are not aligned, and learned patch-text alignment is close
to existing work. Separate branches preserve complementary inductive biases.

**Counterargument:** an ontology introduces hand-designed assumptions and label cost.

**Required test:** compare fixed, sparse learned, unconstrained, and no ontology.

## Decision 2: Structured VLM, not free-form MLLM

**Chosen:** CLIP/SigLIP-style concept scores for the core model.

**Alternative:** ask an MLLM to generate a rationale and attack label.

**Reason:** structured outputs are cheaper, deterministic, calibratable, and easier
to evaluate. MLLM captions may still generate offline annotation candidates.

**Counterargument:** global image-text models can miss tiny forensic artifacts.

**Mitigation:** DINO owns local artifacts; evaluate regional semantic scoring.

## Decision 3: Consistency is confidence-weighted

**Chosen:** delay consistency and apply it only to trusted concepts.

**Alternative:** force agreement throughout training.

**Reason:** forced agreement can propagate VLM hallucinations and destroy useful
error diversity.

**Counterargument:** weak consistency may not affect learning.

**Required test:** weight schedules and pseudo-label confidence thresholds.

## Decision 4: Physical PAD first

**Chosen:** bona fide, print, replay, and mask attacks.

**Alternative:** jointly include deepfake and face forgery.

**Reason:** presentation attacks and digital manipulation have different threat
models and artifacts. A narrow first paper permits defensible evaluation.

## Major risks

### Shared shortcuts

Both branches may learn dataset, camera, background, or compression cues and agree
for the wrong reason.

Mitigation: cross-domain evaluation, nuisance interventions, background/face
ablations, sensor stratification, and shared-error analysis.

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

Branches may become copies, increasing agreement without accuracy.

Mitigation: independent pretraining, branch-specific supervision, stop-gradient
ablation, error diversity measurements, and no feature-level forced alignment.

### Publication overlap

The field is moving rapidly; 2026 work already covers DINO prompting and
compositional forensic prompts.

Mitigation: monthly literature delta search and explicit comparison against the
closest methods.

## Open decisions

- Which exact OpenCLIP/SigLIP checkpoint gives the best accuracy/compute tradeoff?
- Does the VLM consume the context crop, face crop, or both?
- Which concepts survive human precision audit?
- Should ontology edges be signed to represent negative evidence?
- Is abstention evaluated per image or per authentication transaction?
- Which target journal and category define the Q3 requirement?
