# Related Work and Novelty Boundary

## Closest work

| Work | Relevant overlap | Consequence for this project |
|---|---|---|
| DINOv2 with Registers | Smooth, useful dense ViT features | Registers alone are not a PAD contribution |
| FLIP, ICCV 2023 | Language-guided cross-domain FAS | Generic class text prompts are not novel |
| TeG-DG, 2023/2024 | Text-guided domain generalization | Text/visual consistency alone is too broad |
| MVP-FAS, ICCV 2025 | Patch embeddings and multi-text alignment | Patch-text heatmaps alone are strongly overlapped |
| SLIP, AAAI 2025 | Language-guided spoof cues and one-class FAS | Prompt-driven cue maps need a distinct setting |
| FaceShield, AAAI 2025 | MLLM reasoning and attack localization | Generated explanations/localization are not enough |
| Evidential Semantic Consistency, TIFS 2024 | Unknown PAI, semantic consistency, evidential uncertainty | Generic semantic-consistency and unknown-aware claims are occupied |
| Confidence Aware Learning, TIFS 2025 | Reliability and confidence-aware FAS | Reliability alone is not a contribution |
| FaceCoT, CVPR 2026 | CoT data and MLLM reasoning for FAS | CoT is not the proposed novelty |
| DINO-VPT, IJCB 2026 | DINO visual prompt tuning for physical/digital FAS | DINO plus prompt tuning is already occupied |
| VFM benchmark, CVPRW 2026 | DINOv2-Reg as a strong DG-FAS baseline | This must be reproduced or fairly compared |
| Primitive-driven prompting, 2026 | Patch-aware compositional forensic primitives | Compositional visual evidence is a close competitor |
| RPSR-FAS, September 2026 | Organized VLM semantics and reliability-aware FAS | Semantic pools plus reliability substantially overlap the original plan |

Bibliographic links are maintained in the reading list. Acceptance/publication
metadata must be checked against publisher pages before manuscript submission.

## Rejected initial formulation

The initial design proposed native cosine similarity

$$A_{ik}=\cos(d_i,t_k)$$

between a DINO patch embedding $d_i$ and a VLM text embedding $t_k$. This is not
well-defined because independently trained DINO and text encoders do not share an
aligned embedding space. A learned projection would make it computable, but the
result would closely resemble existing patch-text alignment methods and would not
by itself establish forensic meaning.

## Superseded consistency formulation

The previous plan trained branch decisions toward agreement while using their
disagreement to detect unknown attacks. These objectives conflict: minimizing
$D_{JS}(p_D,p_V)$ removes the signal later used for selective prediction. Generic
semantic consistency and reliability are also occupied by the TIFS 2024 and
RPSR-FAS work above.

## Current novelty hypothesis

The remaining defensible hypothesis is narrower:

- DINOv2-Reg and the VLM remain independently trained to preserve error diversity.
- Disagreement is observed, not minimized as a training objective.
- A reliability model is trained only from cross-fitted source-domain predictions,
  including held-out source domains or attack families as pseudo-shifts.
- The core output is selective prediction with explicit security, usability, and
  coverage accounting. Conditional VLM invocation is secondary.

Cross-model disagreement is standard ensemble machinery and is not novel by itself.
The candidate contribution is source-only cross-fitted failure-risk estimation from
independently trained heterogeneous foundation predictors, with separate operational
validation under PAD domain shifts and attack-family shifts. Explicit disagreement belongs in the
title/contribution only if its preregistered incremental test passes.

## Publication positioning

This is not claimed as a fundamentally new ensemble or uncertainty algorithm. Its
defensible contribution is an empirical-method result: whether heterogeneous
foundation predictors provide transferable, security-useful failure information in
single-image PAD when every selector and calibrator is source-only. The same-family
control, fixed-error risk comparisons, and strict outer-domain protocol distinguish
that claim from merely averaging two pretrained models.

A Q3 submission is plausible, not guaranteed, if the confirmatory evidence shows
transferable error-ranking and selective-utility gains over conventional uncertainty,
sample-OOF risk training, capacity-matched learned-risk baselines, and the DINOv2-Reg
+ plain-DINOv2 same-family system. Realized fusion rescue supports a separate
classifier-benefit claim; it is not a prerequisite for useful failure ranking.
Conditional routing is not part of the minimum novelty claim. A Q1/top-conference
claim would likely require a stronger algorithmic contribution than this plan
currently contains.

## Claims that require evidence

| Candidate claim | Minimum supporting evidence |
|---|---|
| Branches are complementary | Joint-error table, class-conditional oracle gain, REF/FARR, and subgroup analysis |
| Cross-foundation diversity matters | Positive heterogeneity advantage over shared-encoder and stronger same-family controls |
| Explicit disagreement matters | Capacity-matched with/without-disagreement risk models on fixed prediction errors |
| Failure risk generalizes | Source-only cross-fitting, held-out gate threshold selection, and confirmatory targets |
| Method beats uncertainty heuristics | Fused MSP/entropy, simple disagreement, Mahalanobis, and capacity-matched risk comparisons |
| Selective decisions are useful | AUPR, AURC/selective curves, attack/bona-fide coverage, and end-to-end FA/BFNR accounting |
| Routing saves compute | Conditional-call latency, memory, throughput, and coverage comparison; secondary claim only |

## Novelty kill conditions

Reframe or stop the model-centric risk paper if any holds:

- failure ranking and selective utility do not improve over the required baselines;
- domain-OOF error supervision does not improve over matched sample-OOF training;
- heterogeneous risk transfer does not exceed same-family diversity, requiring a
  broader selective-ensemble framing;
- agreement is high when both branches are wrong;
- gains disappear under source-only hyperparameter selection;
- the method only improves CelebA-Spoof in-domain performance;
- a newer paper implements the same source-only cross-foundation risk estimation.

Negligible fusion rescue removes only the classifier-improvement claim. Failure of the
capacity-matched disagreement test removes disagreement wording. Failure of optional
routing removes only the compute-saving claim.
