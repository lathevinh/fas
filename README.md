# Source-Domain Cross-Fitted Failure-Risk Estimation for Selective Face Presentation Attack Detection

Research dossier for a practical and publishable face presentation attack detection
(PAD) system using one RGB image. The proposed system studies:

- a self-supervised visual predictor based on DINOv2 with Registers;
- a fixed, independently pretrained OpenCLIP ViT-B/16 predictor;
- source-domain cross-fitted failure-risk estimation for failure detection and
    abstention; fusion rescue, explicit disagreement, and routing remain separate claims.

The research plan, methodology, paper contract, and data-to-experiment implementation
plan are frozen. Existing executable preregistration files remain provisional
scaffolding from review rounds 11-12; coding begins with their Phase-0 migration before
any dataset-facing implementation.

## Scope

The first paper targets physical presentation attacks:

- bona fide;
- print;
- replay/display;
- 2D/3D mask where data are available.

Digital face forgery is excluded from the first scope because it is not necessarily
an attack at the biometric capture device under ISO/IEC 30107 terminology.

## Research question

Does source-domain cross-fitted error supervision make heterogeneous frozen foundation
predictors useful for selective single-image PAD under unseen domains, beyond
single-branch confidence and a matched same-family ensemble?

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
21. [ChatGPT review round 7](docs/20-chatgpt-review-round7.md)
22. [Response to ChatGPT review round 7](docs/21-review-response-round7.md)
23. [ChatGPT review round 8](docs/22-chatgpt-review-round8.md)
24. [Response to ChatGPT review round 8](docs/23-review-response-round8.md)
25. [ChatGPT review round 9](docs/24-chatgpt-review-round9.md)
26. [Response to ChatGPT review round 9](docs/25-review-response-round9.md)
27. [ChatGPT review round 10](docs/26-chatgpt-review-round10.md)
28. [Response to ChatGPT review round 10](docs/27-review-response-round10.md)
29. [ChatGPT review round 11](docs/28-chatgpt-review-round11.md)
30. [Response to ChatGPT review round 11](docs/29-review-response-round11.md)
31. [ChatGPT review round 12](docs/30-chatgpt-review-round12.md)
32. [Response to ChatGPT review round 12](docs/31-review-response-round12.md)
33. [ChatGPT review round 13](docs/32-chatgpt-review-round13.md)
34. [Response to ChatGPT review round 13](docs/33-review-response-round13.md)
35. [ChatGPT review round 14](docs/34-chatgpt-review-round14.md)
36. [Response to ChatGPT review round 14](docs/35-review-response-round14.md)
37. [ChatGPT review round 15](docs/36-chatgpt-review-round15.md)
38. [Response to ChatGPT review round 15](docs/37-review-response-round15.md)
39. [Implementation plan](docs/38-implementation-plan.md)
40. [ChatGPT review round 16](docs/39-chatgpt-review-round16-q3-plan.md)
41. [Frozen paper skeleton](docs/40-paper-skeleton.md)
42. [Response to ChatGPT review round 16](docs/41-review-response-round16.md)
43. [Data-to-experiment implementation plan](docs/42-data-to-experiment-implementation-plan.md)
44. [ChatGPT review of the implementation plan](docs/43-chatgpt-review-doc42.md)
45. [Response to implementation-plan review](docs/44-review-response-doc43.md)
46. [ChatGPT review of the implementation-plan response](docs/45-chatgpt-review-doc44.md)
47. [Response to Track-A benchmark review](docs/46-review-response-doc45.md)
48. [Reading list](references/reading-list.md)

## Provisional readiness scaffold

```bash
python -m unittest discover -s tests -v
python scripts/validate_preregistration.py --stage schema
python scripts/validate_preregistration.py --stage data
python scripts/validate_preregistration.py --stage pre-pilot
python scripts/validate_preregistration.py --stage confirmatory
```

These commands document prior scaffold behavior; they do not authorize implementation
or target inspection. The normative method is the strict source-only design in the
current charter, method, protocol, experiment plan, Round-14 methodology freeze, and
Round-15 estimand specification. Superseded pilot-oriented names and rules in the
scaffold must be replaced according to the implementation plan before use.

## Current status

- Status: research and implementation plans frozen; Phase 0 coding authorized
- Last reviewed: 2026-09-18
- Code: Stage-0 validator and monotone calibration primitive implemented
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
