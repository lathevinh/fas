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
- The output is selective prediction or conditional VLM invocation, with explicit
  security, coverage, and latency trade-offs.

Cross-model disagreement is standard ensemble machinery and is not novel by itself.
The candidate contribution is its source-only calibration and operational validation
under simultaneous PAD domain and attack shift.

## Claims that require evidence

| Candidate claim | Minimum supporting evidence |
|---|---|
| Branches are complementary | Two-sided error table, double-fault rate, oracle gain, and subgroup analysis |
| Disagreement generalizes | Source-only cross-fitting and untouched target evaluation |
| Disagreement detects unknowns | AUROC/AUPR and risk-coverage on held-out attacks/domains |
| Method beats ensemble heuristics | MSP, entropy, energy, average, and learned-fusion comparisons |
| Method is deployable | Conditional-call latency, memory, throughput, and coverage comparison |

## Novelty kill conditions

Reframe or stop the model-centric paper if any holds:

- one branch dominates and two-sided complementarity is negligible;
- oracle gain over the better branch is negligible;
- simple averaging or ordinary uncertainty performs as well as calibrated disagreement;
- agreement is high when both branches are wrong;
- gains disappear under source-only hyperparameter selection;
- the method only improves CelebA-Spoof in-domain performance;
- conditional VLM inference provides no useful security-latency trade-off;
- a newer paper implements the same source-only cross-foundation risk calibration.
