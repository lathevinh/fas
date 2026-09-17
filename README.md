# Dual-Evidence Single RGB Image PAD

Research dossier for a practical and publishable face presentation attack detection
(PAD) system using one RGB image. The proposed system combines:

- localized forensic evidence from DINOv2 with Registers;
- structured semantic evidence from a vision-language model (VLM);
- evidence- and decision-level consistency for prediction, uncertainty, and abstention.

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

Can complementary forensic and semantic evidence improve cross-domain and
unknown-attack reliability over a strong DINOv2-Reg classifier and a conventional
ensemble, while preserving interpretable evidence and deployable inference?

## Document map

1. [Project charter](docs/00-project-charter.md)
2. [Related work and novelty boundary](docs/01-related-work-and-novelty.md)
3. [Research questions and falsifiable hypotheses](docs/02-research-questions.md)
4. [Proposed method](docs/03-method.md)
5. [Datasets and processing](docs/04-data-and-protocols.md)
6. [Experiment and implementation plan](docs/05-experiment-plan.md)
7. [Risks, alternatives, and decisions](docs/06-risks-and-decisions.md)
8. [External review guide](docs/07-external-review.md)
9. [Reading list](references/reading-list.md)

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
- the proposed model outperforms any baseline.

## Reproduction policy

Experiments must preserve official dataset protocols, subject/video separation,
source-only model selection, fixed seeds, configuration snapshots, and per-domain
results. Dataset files and pretrained weights must not be committed.
