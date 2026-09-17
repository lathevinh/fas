# Cross-Foundation Disagreement for Single RGB Image PAD

Research dossier for a practical and publishable face presentation attack detection
(PAD) system using one RGB image. The proposed system studies:

- a self-supervised visual predictor based on DINOv2 with Registers;
- an independently pretrained vision-language semantic predictor;
- source-only disagreement calibration for failure detection, abstention, and
  conditional VLM inference.

This repository is documentation-first. Its immediate purpose is to make the
research proposal auditable and easy to challenge before implementation.

## Scope

The first paper targets physical presentation attacks:

- bona fide;
- print;
- replay/display;
- 2D/3D mask where data are available.

Digital face forgery is excluded from the first scope because it is not necessarily
an attack at the biometric capture device under ISO/IEC 30107 terminology.

## Research question

Do independently pretrained visual and vision-language foundation models make
usefully different errors under domain and attack shift, and can their natural
disagreement support better selective PAD than conventional uncertainty and fusion?

## Document map

1. [Project charter](docs/00-project-charter.md)
2. [Related work and novelty boundary](docs/01-related-work-and-novelty.md)
3. [Research questions and falsifiable hypotheses](docs/02-research-questions.md)
4. [Proposed method](docs/03-method.md)
5. [Datasets and processing](docs/04-data-and-protocols.md)
6. [Experiment and implementation plan](docs/05-experiment-plan.md)
7. [Risks, alternatives, and decisions](docs/06-risks-and-decisions.md)
8. [External review guide](docs/07-external-review.md)
9. [ChatGPT review](docs/08-chatgpt-review.md)
10. [Response to ChatGPT review](docs/09-review-response.md)
11. [ChatGPT review round 2](docs/10-chatgpt-review-round2.md)
12. [Response to ChatGPT review round 2](docs/11-review-response-round2.md)
13. [ChatGPT review round 3](docs/12-chatgpt-review-round3.md)
14. [Response to ChatGPT review round 3](docs/13-review-response-round3.md)
15. [ChatGPT review round 4](docs/14-chatgpt-review-round4.md)
16. [Response to ChatGPT review round 4](docs/15-review-response-round4.md)
17. [ChatGPT review round 5](docs/16-chatgpt-review-round5.md)
18. [Response to ChatGPT review round 5](docs/17-review-response-round5.md)
19. [ChatGPT review round 6](docs/18-chatgpt-review-round6.md)
20. [Response to ChatGPT review round 6](docs/19-review-response-round6.md)
21. [Reading list](references/reading-list.md)

## Current status

- Status: proposal and literature-audit stage
- Last reviewed: 2026-09-17
- Code: not implemented
- Results: none; all expected outcomes are hypotheses, not findings

## Non-claims

This project does not currently claim that:

- combining DINO and a VLM is itself novel;
- cosine similarity across their native embeddings is meaningful;
- a visually plausible heatmap is faithful evidence;
- consistency implies correctness;
- cross-model disagreement alone is a novel algorithm;
- the proposed model outperforms any baseline.

## Reproduction policy

Experiments must preserve official dataset protocols, subject/video separation,
source-only model selection, fixed seeds, configuration snapshots, and per-domain
results. Dataset files and pretrained weights must not be committed.
