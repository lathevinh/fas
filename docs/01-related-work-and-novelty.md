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
| FaceCoT, CVPR 2026 | CoT data and MLLM reasoning for FAS | CoT is not the proposed novelty |
| DINO-VPT, IJCB 2026 | DINO visual prompt tuning for physical/digital FAS | DINO plus prompt tuning is already occupied |
| VFM benchmark, CVPRW 2026 | DINOv2-Reg as a strong DG-FAS baseline | This must be reproduced or fairly compared |
| Primitive-driven prompting, 2026 | Patch-aware compositional forensic primitives | Compositional visual evidence is a close competitor |

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

## Current novelty hypothesis

The defensible gap is not multimodal fusion. It is the use of two deliberately
different evidence mechanisms and testing whether their agreement or disagreement
improves reliability:

- DINO learns local, low-level forensic cues without being forced into text space.
- The VLM supplies structured material/geometry/attack semantics.
- A sparse ontology maps forensic cues to semantic claims.
- Counterfactual tests determine whether agreement is causal or merely correlational.
- Disagreement becomes an operational signal for abstention and unknown attacks.

## Claims that require evidence

| Candidate claim | Minimum supporting evidence |
|---|---|
| Branches are complementary | Error diversity and conditional mutual information analyses |
| Heatmaps are forensic | Localization, deletion/insertion, and controlled intervention tests |
| Consistency improves PAD | Better results than score/feature fusion under equal capacity |
| Disagreement detects unknowns | AUROC/AUPR and risk-coverage on held-out attacks/domains |
| Method is deployable | Latency, memory, throughput, and distilled model comparison |

## Novelty kill conditions

Reframe or stop the model-centric paper if any holds:

- simple averaging performs as well as evidence consistency;
- agreement is high when both branches are wrong;
- gains disappear under source-only hyperparameter selection;
- concept annotations are mostly unverifiable VLM pseudo-labels;
- the method only improves CelebA-Spoof in-domain performance;
- a newer paper implements the same ontology-guided dual-evidence mechanism.
