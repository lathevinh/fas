# Source-Domain Cross-Fitted Failure-Risk Estimation for Selective Face Presentation Attack Detection

Research dossier for a practical and publishable face presentation attack detection
(PAD) system using one RGB image. The proposed system studies:

- a self-supervised visual predictor based on DINOv2 with Registers;
- a fixed, independently pretrained OpenCLIP ViT-B/16 predictor;
- source-domain cross-fitted failure-risk estimation for failure detection and
    abstention; fusion rescue, explicit disagreement, and routing remain separate claims.

The research plan, methodology, paper contract, and data-to-experiment implementation
plan are frozen. Phase 0 has replaced the provisional pilot scaffold with final
governance, typed contract, staged-readiness, and immutable-freeze primitives.
Post-rework source-evidence and gate repairs passed fresh CI and owner approval.
Phase 1 environment lock is accepted in existing conda env `fas`. Acquisition
receipt/protocol-file intake contracts are accepted in checkpoint 1.2. The first
checkpoint-1.3 metadata adapter, OULU-NPU, is accepted. The next adapter,
CASIA-FASD, is blocked on official schema documentation; no real acquisition/media
audit is accepted.
Training and target evaluation remain locked.

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
43. [Canonical final data-to-experiment implementation plan](docs/42-data-to-experiment-implementation-plan.md)
44. [ChatGPT review of the implementation plan](docs/43-chatgpt-review-doc42.md)
45. [Response to implementation-plan review](docs/44-review-response-doc43.md)
46. [ChatGPT review of the implementation-plan response](docs/45-chatgpt-review-doc44.md)
47. [Response to Track-A benchmark review](docs/46-review-response-doc45.md)
48. [ChatGPT review of Track-A benchmark response](docs/47-chatgpt-review-doc46.md)
49. [Response to Track-A execution review](docs/48-review-response-doc47.md)
50. [ChatGPT review of Track-A execution response](docs/49-chatgpt-review-doc48.md)
51. [Response to Track-A metric-semantics review](docs/50-review-response-doc49.md)
52. [ChatGPT review of Track-A metric-semantics response](docs/51-chatgpt-review-doc50.md)
53. [Final response closing Track-A semantics](docs/52-review-response-doc51.md)
54. [Final one-pass Q3 plan audit](docs/53-chatgpt-review-doc52-final-plan-audit.md)
55. [Response to final core-plan audit](docs/54-review-response-doc53.md)
56. [Final decision-rule review](docs/55-chatgpt-review-doc54-final.md)
57. [Response closing final decision rules](docs/56-review-response-doc55.md)
58. [Population and coverage clarification review](docs/57-chatgpt-review-doc56.md)
59. [Response closing population and coverage semantics](docs/58-review-response-doc57.md)
60. [Final research-plan acceptance](docs/59-chatgpt-review-doc58.md)
61. [Response and final implementation freeze](docs/60-review-response-doc59-final-implementation-freeze.md)
62. [Phase 0 governance migration and validation plan](docs/61-phase0-governance-migration-and-validation-plan.md)
63. [Phase 0 implementation rework review](docs/63-phase0-implementation-rework-review.md)
64. [Response to Phase 0 implementation rework](docs/64-review-response-doc63-phase0-rework.md)
65. [Phase 0 rework verification review](docs/65-review-phase0-after-doc64.md)
66. [Phase 1 checkpoints and preflight](docs/65-phase1-checkpoints-and-preflight.md)
67. [Source-evidence and gate prerequisite rework](docs/66-review-response-doc65-source-evidence-and-gate.md)
68. [Environment lock and CUDA smoke](docs/67-phase1-step1.1-environment-lock.md)
69. [Environment-lock acceptance review](docs/69-review-phase1-step1.1-environment-lock.md)
70. [Intake contract and acceptance evidence](docs/70-phase1-step1.2-intake-contract.md)
71. [Intake-contract acceptance review](docs/72-review-phase1-step1.2-intake-contract.md)
72. [OULU-NPU schema prerequisite and blocker](docs/73-phase1-step1.3-oulu-schema-blocker.md)
73. [OULU-NPU metadata adapter and acceptance evidence](docs/74-phase1-step1.3-oulu-metadata-adapter.md)
74. [OULU-NPU metadata-adapter acceptance review](docs/75-review-phase1-step1.3-oulu-metadata-adapter.md)
75. [CASIA-FASD schema prerequisite and owner action](docs/76-phase1-step1.3-casia-schema-blocker.md)
76. [Reading list](references/reading-list.md)

## Readiness validation

```bash
conda run -n fas python -m unittest discover -s tests -v
conda run -n fas python scripts/validate_preregistration.py --stage schema
conda run -n fas python scripts/validate_preregistration.py --stage data-audit
conda run -n fas python scripts/validate_preregistration.py --stage source-dry-run
conda run -n fas python scripts/validate_preregistration.py --stage analysis-freeze
conda run -n fas python scripts/validate_preregistration.py --stage locked-evaluation
```

Only `schema` is expected to pass before audited data and source-only evidence exist.
Every later stage must fail closed with explicit missing-prerequisite errors. These
commands do not authorize target inspection; the normative implementation authority
is the strict source-only design consolidated in
[Document 42](docs/42-data-to-experiment-implementation-plan.md).

## Current status

- Status: research plan and canonical implementation specification frozen; Phase 0
    source-evidence/gate rework, environment lock and intake contract accepted
- Current work package: [Checkpoint 1.3 CASIA-FASD](docs/76-phase1-step1.3-casia-schema-blocker.md);
    blocked on official schema documentation; OULU metadata accepted, real media audit pending
- Last reviewed: 2026-10-06
- Code: final staged validator, typed synthetic contracts, immutable analysis-freeze
    primitive, and monotone calibration primitive implemented
- Results: none; all expected outcomes are hypotheses, not findings
- Intake: private acquisition/protocol receipts, read-only hash/path checks and
    redacted immutable CLI reports; [17-test intake / 93-test regression evidence](results/phase1/intake-contract-verification.json)
    passes on synthetic fixtures. No real dataset release has been accepted
- OULU-NPU: official metadata parser, versioned label mapping, all protocol/fold
    memberships and private archive-header reconciliation implemented;
    [17-test adapter / 110-test regression evidence](results/phase1/oulu-adapter-verification-v2.json).
    Metadata checkpoint accepted by [review 75](docs/75-review-phase1-step1.3-oulu-metadata-adapter.md),
    which confirms fresh CI success for the implementation commit.
    Owner-supplied local metadata reconcile, but receipt identity/permissions,
    real media hashes and decoding remain unverified; no readiness count is changed
- Environment: existing conda env `fas`, approved Python 3.12.14, exact native/wheel
    locks and upstream commits; [preflight](results/phase1/environment-preflight-locked.json)
    ready, [CUDA smoke](results/phase1/environment-smoke-locked.json) pass and
    [76-test regression/reconstruction](results/phase1/environment-lock-verification.json)
    pass. The old [report](results/phase1/environment-preflight.json) remains historical.
    No pretrained weights or datasets were loaded; environment readiness is not
    scientific or extraction readiness

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
