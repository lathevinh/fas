# Proposed Method

## Overview

For image $x$, the system produces two independent evidence views and only then
compares them.

### Forensic branch

DINOv2-Reg returns patch, class, and register tokens:

$$
D=f_D(x)=\{d_1,\ldots,d_N,d_{cls},d_{reg}^1,\ldots,d_{reg}^R\}.
$$

A patch head produces $M$ cue maps:

$$H^F=h_F(d_1,\ldots,d_N)\in\mathbb R^{N\times M}.$$

Candidate cues include halftone, paper texture, print blur, moire, pixel grid,
color banding, reflection, flat geometry, rigid texture, and mask boundary.
Register/class tokens condition pooling or gating but are not spatial heatmaps.
The branch produces attack probabilities $p^F$ and forensic concept scores $e^F$.

### Semantic branch

A pretrained CLIP/SigLIP-style model scores prompt ensembles for structured concepts:

- material: natural skin, paper, display, silicone/latex, rigid material;
- geometry: natural facial depth, flat surface, rigid mask, partial boundary;
- artifact semantics: printed pattern, recaptured display, artificial reflection;
- nuisance: blur, compression, illumination, sensor noise.

It produces semantic evidence $e^S$ and attack probabilities $p^S$. Free-form
generated text is not part of the core training target.

### Ontology-guided consistency

A sparse mapping $W_{onto}$ connects compatible forensic and semantic concepts:

$$\hat e^F=\sigma(W_{onto}\operatorname{Pool}(H^F)).$$

Examples:

- moire + pixel grid + display reflection -> replay/display;
- halftone + paper texture + flat surface -> print/paper;
- rigid texture + eye/mouth boundary + facial depth anomaly -> mask.

The mapping is initialized from domain knowledge. An ablation compares fixed,
learnable sparse, and unconstrained mappings.

## Losses

$$
\mathcal L =
\mathcal L_{pad}+
\lambda_a\mathcal L_{attack}+
\lambda_f\mathcal L_{forensic}+
\lambda_s\mathcal L_{semantic}+
\lambda_e\mathcal L_{evidence-consistency}+
\lambda_d\mathcal L_{decision-consistency}+
\lambda_c\mathcal L_{counterfactual}.
$$

- `PAD`: binary bona-fide/attack classification.
- `attack`: print/replay/mask/other when labels exist.
- `forensic`: cue supervision from verified labels, intervention masks, or trusted pseudo-labels.
- `semantic`: multi-label material/geometry concepts.
- `evidence-consistency`: confidence-masked agreement between compatible evidence.
- `decision-consistency`: Jensen-Shannon divergence between branch predictions.
- `counterfactual`: intended evidence changes under controlled cue intervention.

Consistency weights start at zero and warm up only after both branches are useful.
Low-confidence semantic pseudo-labels do not impose consistency.

## Reliability and final decision

A small reliability gate uses branch entropy, evidence confidence, image quality,
and branch divergence:

$$p=w_Fp^F+w_Sp^S,\qquad w_F+w_S=1.$$

Large disagreement triggers abstention or recapture. The gate must be compared
against fixed averaging and ordinary learned score fusion.

## Training strategy

### DINO branch

1. Start with pretrained `dinov2_vitb14_reg4`, fully frozen, and train heads.
2. Add LoRA/adapters to the last four blocks if the frozen baseline saturates.
3. Unfreeze two to four final blocks only if source validation improves without
   degrading held-out-source generalization.
4. Do not full-fine-tune from the beginning.

### VLM branch

1. Start with frozen OpenCLIP or SigLIP image/text encoders.
2. Train prompt weights, calibration, and a sparse semantic-to-attack head.
3. If necessary, apply LoRA to the last image blocks; keep the text encoder frozen.
4. Use a generative MLLM only offline for candidate annotation, followed by audit.

### Joint stage

1. Freeze stable backbones and train the ontology and reliability gate.
2. Warm up consistency weights.
3. Optionally unfreeze adapters at a learning rate ten times below head learning rate.
4. Distill semantic evidence to a compact production head after establishing the
   full model as an upper bound.
