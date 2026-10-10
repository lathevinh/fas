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
CASIA-FASD, has an accepted owner-authorized, pinned Bob-reference metadata adapter.
This is not CASIA-owner schema certification; no real acquisition/media audit is
accepted. SiW-Mv2 prerequisites are accepted, and the
[dated benchmark amendment](docs/88-phase1-benchmark-amendment-siwmv2.md) replaces
Replay-Attack in the active study specification, accepted in
[review 89](docs/89-review-doc88-benchmark-amendment.md). The
new core is OULU-NPU/CASIA-FASD/MSU-MFSD/SiW-Mv2 with a frozen 1680-video Protocol-I
intersection and explicit video grouping for SiW-Mv2. MCIO remains historical context.
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
76. [CASIA archive inspection, private storage and remaining schema blocker](docs/77-phase1-step1.3-casia-archive-schema-check.md)
77. [CASIA reference-derived metadata adapter and acceptance evidence](docs/78-phase1-step1.3-casia-reference-metadata-adapter.md)
78. [CASIA reference-derived metadata acceptance review](docs/79-review-phase1-step1.3-casia-reference-metadata-adapter.md)
79. [Replay-Attack prerequisites and exact owner input](docs/80-phase1-step1.3-replay-attack-prerequisites.md)
80. [AxonData assessment and protocol decision](docs/81-axondata-dataset-assessment-and-protocol-decision.md)
81. [Reasoning-supervision paper review](docs/82-paper-review-reasoning-supervision-fas.md)
82. [SiW-Mv2 prerequisites and conditional replacement decision](docs/83-phase1-siwmv2-prerequisites-and-replacement-decision.md)
83. [SiW-Mv2 amendment correction](docs/85-review-response-doc84-siwmv2-amendment.md)
84. [Eligible-coverage requirement review](docs/86-review-doc85-siwmv2-amendment-response.md)
85. [Verified eligible attack coverage](docs/87-review-response-doc86-eligible-attack-coverage.md)
86. [Dated benchmark/config amendment and acceptance criteria](docs/88-phase1-benchmark-amendment-siwmv2.md)
87. [Benchmark amendment acceptance review](docs/89-review-doc88-benchmark-amendment.md)
88. [Dataset holdout and evaluation-population clarification](docs/90-review-response-doc89-population-clarification.md)
89. [Reading list](references/reading-list.md)

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
[Document 42](docs/42-data-to-experiment-implementation-plan.md), with the dated
[Document 88](docs/88-phase1-benchmark-amendment-siwmv2.md) population/grouping amendment.

## Current status

- Status: research plan and canonical implementation specification frozen; Phase 0
    source-evidence/gate rework, environment lock and intake contract accepted
- Current work package: [owner-authorized technical audit](docs/103-owner-authorized-technical-audit.md).
    The owner attests all supplied core datasets permitted for research and removes
    administrative-receipt prerequisites. OULU technical archive/header/protocol
    [reconciliation passes](results/phase1/oulu-technical-archive-preflight-v1.json):
    4950 videos / 42 protocol files, 17 focused tests, frozen hashes unchanged.
    [Review 104](docs/104-review-doc103-oulu-technical-preflight.md) accepts that
    bounded preflight without rework. [Whole-archive byte pinning](docs/105-review-response-doc104-oulu-archive-hashes.md)
    now completes SHA-256 of all three OULU media TARs (105116817408 bytes),
    with immutable records and frozen hashes unchanged. [Per-video audit](docs/107-review-response-doc106-oulu-per-video-audit.md)
    now pins all 4950 payloads: 4949 strict full-decode passes, 1 MJPEG failure,
    13 exact duplicate pairs and no exact cross-role/partition duplicates.
    [Transaction/selector definition](docs/109-review-response-doc108-transaction-selector-freeze.md)
    now freezes lower-median selection and scoreless terminal-failure accounting:
    4949 primary identities, calibration denominator 990 / 989 frame-available /
    zero fitted score rows, original/rerun byte-identical, source roles unchanged.
    [Review 110](docs/110-review-doc109-transaction-selector-freeze.md) accepts that freeze.
    [OULU content screening](docs/111-review-response-doc110-oulu-content-screening.md)
    compares 12243826 pairs: 6653 candidates, including 13 known exact pairs and
    6640 unresolved non-exact pairs (484 cross-role). Screening is not lineage
    certification; adjudication remains pending and roles/selector are unchanged.
    [Full-frame exact-evidence pass](docs/113-review-response-doc112-oulu-lineage-exact-evidence.md)
    processes all 6640 non-exact pairs in risk-priority order; no exact RGB token
    overlap is found, but all 6640 remain uncertain, not cleared false positives.
    [Private visual batch 01](docs/115-review-response-doc114-oulu-visual-batch01.md)
    reviews the first 10 highest-risk pairs: 9 screen-rejection proposals and 1
    uncertain, pending owner review, not capture-provenance clearance. All 2624
    decoded RGB frames of 19 videos are verified; 30 private images actually viewed.
    [Bound human-review handoff](docs/117-review-response-doc116-oulu-human-review-handoff.md)
    prepares the same ten packets plus 34 full-resolution temporal frames for the
    uncertain pair; 67 private files reproduce byte-identically. Actual human
    reviews remain 0/10, browser usability unverified; the next 75 are not started.
    Confirmed near-duplicate/cross-dataset lineage, other media audits and model applicability
    remain pending; no archive migration, role regeneration or model execution.
    Stop for checkpoint review before further media/model work.
    [Review 101](docs/101-review-doc100-permanent-source-role-freeze.md) accepts
    1.4B permanent-role freeze without rework; frozen inputs must not be regenerated.
    [Review 99](docs/99-review-doc98-role-policy-v2.md) accepts v2 for freeze without
    further rework. The [permanent registry](configs/role_policy_frozen_v2.yaml)
    locks exact accepted assignments before source prediction errors; execution and
    scientific readiness remain false. Full 1.4 feasibility/content audit is not complete.
    [Review 94](docs/94-review-doc93-msu-mfsd-metadata-adapter.md)
    accepts MSU without rework and records all four core adapters as implemented/accepted;
    [response 95](docs/95-review-response-doc94.md) preserves the audit limitations.
    Metadata adapters are accepted. The preceding
    [benchmark amendment](docs/88-phase1-benchmark-amendment-siwmv2.md) is accepted by
    [review 89](docs/89-review-doc88-benchmark-amendment.md), with
    [population wording clarified](docs/90-review-response-doc89-population-clarification.md).
    Independent acquisition-document verification remains unclaimed, not a blocker
    to owner-authorized technical inspection. Media/decode/content-duplicate audits
    and scientific readiness remain pending; no bulk extraction, inference or training
- Last reviewed: 2026-10-09
- Code: final staged validator, typed synthetic contracts, immutable analysis-freeze
    primitive, and monotone calibration primitive implemented
- Results: none; all expected outcomes are hypotheses, not findings
- Manifests/roles: [24 focused / 204 regression tests](results/phase1/source-role-freeze-verification-v2.json)
    passed at the accepted freeze checkpoint, not rerun in this prerequisite turn.
    [Accepted v2 aggregate report](results/phase1/manifest-role-proposal-summary-v2.json)
    records 7510 canonical / 6887 source-proposal videos, group-disjoint roles and
    byte-identical reruns. Canonical bytes and all v1 artifacts are preserved;
    prospective native-subtype strata yield Mask_Paper 7/2/2 instead of 11/0/0.
    All 6887 source assignments are now permanently frozen without changing their
    hashes; the 13-file frozen export is byte-identical on rerun.
    Prediction-event feasibility and media-content duplicate
    audit remain unverified; original proposal files stay historical, and the separate
    approved registry does not authorize execution or certify audited readiness
- Core audit prerequisites: [bounded private inspection](results/phase1/core-audit-prerequisites-v1.json)
    checked 10 staged JSON files, found zero core acquisition receipt-schema matches,
    and reverified all 13 frozen artifacts. Schema passes; four later stages remain
    blocked. This is historical Document-102 evidence; the owner's subsequent
    research-use attestation supersedes the administrative block without inventing receipts
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
- CASIA-FASD: strict twelve-code Bob-reference mapping, disjoint subject namespace,
    source/reader provenance checks and immutable private header inventory implemented;
    [17 CASIA / 127 regression tests](results/phase1/casia-adapter-verification.json) pass.
    Supplied headers reconcile with the complete reference; owner schema certification,
    acquisition, media hashes/decode and scientific readiness remain unverified.
    Accepted by [review 79](docs/79-review-phase1-step1.3-casia-reference-metadata-adapter.md),
    which confirms fresh CI success on exact implementation commit `33051d2`. Earlier
    [storage-isolation evidence](results/phase1/casia-private-storage-verification.json)
    remains a safety check, not semantic or acquisition certification
- Replay-Attack: prerequisite check only; no local input found in checked locations.
    The provider page's GET DATA link retrieved on 2026-10-06 points to VoicePA,
    not face Replay-Attack. Correct schema/local input is needed before implementation;
    no Replay parser was implemented. Replay is historical rather than active core
    under the accepted benchmark amendment
- SiW-Mv2: accepted Protocol-I intersection and actual archive headers reconcile;
    [27 focused / 162 regression tests](results/phase1/siwmv2-adapter-verification.json)
    pass. [Metadata inventory](results/phase1/siwmv2-adapter-inventory-v1.json)
    contains 1680 eligible videos (1057 source-train; 623 target-test), with 20
    observed exclusions and 11 absent references kept separate. Subject IDs remain
    null and groups are videos; acquisition, media hashes/decode and scientific
    readiness remain unverified. The earlier blocked prerequisite report is historical;
    aggregate owner acceptance is recorded in review 94's final disposition
- MSU-MFSD: native inner README and official subject lists are pinned as raw bytes;
    all 16 volumes in the eight supplied ZIPs reconcile to 280 videos / 35 subjects.
    [18 focused / 180 regression tests](results/phase1/msu-adapter-verification.json)
    pass. [Redacted inventory](results/phase1/msu-adapter-inventory-v1.json) preserves
    train 15 subjects / 120 videos and test 20 / 160. No video/sidecar/helper entry
    opened; container seeking may decompress opaque volume bytes. Roles, acquisition,
    archive/media integrity and scientific readiness remain unverified. Accepted without
    rework by [review 94](docs/94-review-doc93-msu-mfsd-metadata-adapter.md), with fresh
    exact-commit CI on `9355294` independently verified successful
- AxonData alternative: [public metadata assessment](docs/81-axondata-dataset-assessment-and-protocol-decision.md)
    found 51 public videos, not the advertised full commercial corpus, with no
    annotation/identity/protocol manifest. Not adopted as a Replay replacement;
    optional external-candidate use requires further evidence and a frozen separate
    protocol. MCIO configs, data counts and readiness remain unchanged
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
