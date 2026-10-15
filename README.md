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
    uncertain pair; 67 private files reproduce byte-identically. At preparation,
    human reviews were 0/10 and browser usability was unverified.
    [Owner human-review import](docs/119-review-response-doc118-oulu-human-review-import.md)
    now records 10 owner-submitted rejections: 9 AI/human agreements and 1
    disagreement (Pair 5), whose effective disposition stays uncertain pending
    reconciliation. Twelve human-ledger files replay byte-identically; the next
    75 are not started and the original evidence/AI ledgers remain unchanged.
    [Pair-5 reconciliation proposal](docs/121-review-response-doc120-oulu-pair5-reconciliation.md)
    inspects six bound full-resolution frames and proposes a scoped screen-level
    rejection with frame-specific rationale. Acceptance is pending; the original
    effective ledger remains 9 rejected / 1 uncertain and no next batch is started.
    [Explicit owner acceptance](docs/123-review-response-doc122-oulu-batch01-owner-acceptance.md)
    now accepts that scoped Pair-5 rejection separately. Activation/closure still
    waits for exact proposal CI run 38015159060, observed in progress at FFmpeg
    installation; the original ledger is unchanged and the next 75 remain paused.
    [Additive batch-01 activation](docs/125-review-response-doc124-oulu-batch01-activation.md)
    now binds both successful exact CI runs and the existing owner acceptance.
    Current batch01 closes at 10 screen-level rejections, 0 uncertain; historical
    records stay unchanged. Thirteen files replay byte-identically. The next75
    remained paused at publication until review of activation.
    [Review126](docs/126-review-doc125-oulu-batch01-activation.md) now accepts closure.
    [Next fixed batch02 packets](docs/127-review-response-doc126-oulu-batch02-packets.md)
    prepare exactly queue ranks10..19:15 videos,2135 verified RGB frames,2192
    private files; independent redecode/reexport is byte-identical. The accepted
    batch01 evidence/code remain unchanged. No new visual/human dispositions:
    all75 highest-risk remaining pairs are still unreviewed,10 prepared and65
    not yet prepared.53 focused /240 full regression tests pass. Stop for this
    preparation checkpoint review before adjudication; scientific gates stay blocked.
    [Review128](docs/128-review-doc127-oulu-batch02-packets.md) accepts preparation.
    [Batch02 AI visual proposals](docs/129-review-response-doc128-oulu-batch02-ai-review.md)
    now inspect30 bound images for ranks10..19 and record10 scoped rejection
    proposals,0 uncertain/confirmed, with zero human/effective dispositions.
    Twelve ledger files serialize byte-identically; prior evidence/frozen inputs
    stay unchanged.53 focused tests pass;240 full tests were not rerun here.
    Batch02 is not closed;65 highest-risk pairs still lack AI review. Stop for
    this checkpoint review before genuine human handoff or any further batch.
    [Review130](docs/130-review-doc129-oulu-batch02-ai-review.md) accepts AI-proposal scope.
    [Batch02 bound human handoff](docs/131-review-response-doc130-oulu-batch02-human-handoff.md)
    now prepares30 same bound images with blank human answers for original ranks10..19;
    AI proposals are initially collapsed.33 private files reproduce byte-identically,
    54 focused /241 full tests pass. Integrated browser still refuses the private
    folder (403), so actual UI/export interaction is unverified. Human reviews/effective
    dispositions remain0/0. Stop for handoff checkpoint review before separate bound
    human import; the batch01 importer must not be used directly for batch02.
    [Owner batch02 human import](docs/132-oulu-batch02-human-review-import.md)
    now records the owner's supplied10 rejections, with10 AI/human agreements,
    0 disagreements and0 effective activations. Original ranks10..19 and submitted
    answers are preserved; all10 rationale texts are identical/general, disclosed
    without AI rewriting.13 private files independently reimport byte-identically;
    55 focused /242 full tests pass. Direct owner continuation authorizes import,
    not scientific closure. Stop for review before separate additive activation
    or ranks20+; source/frozen evidence and scientific gates remain unchanged.
    [Review133](docs/133-review-doc132-oulu-batch02-human-import.md) accepts import
    and authorizes scoped activation without repeat human review.
    [Additive batch02 activation](docs/134-review-response-doc133-oulu-batch02-activation.md)
    now creates a separate current ledger:10 screen-level rejections,0 uncertain,
    0 confirmed. Historical import activation=false and all prior records remain
    unchanged.13 files serialize byte-identically;55 focused tests pass; full242
    was not rerun here. Generic human rationales/non-blinded review remain disclosed.
    Ranks20+ stay paused for activation checkpoint review; scientific gates remain blocked.
    [Review135](docs/135-review-doc134-oulu-batch02-activation.md) accepts activation
    without rework and authorizes the next frozen queue preparation.
    [Batch03 packets](docs/136-review-response-doc135-oulu-batch03-packets.md)
    prepare exactly20..29:17 videos,2417 verified RGB frames,30 panels/triggers;
    2476 private files independently redecode/reexport byte-identically.
    56 focused /243 full tests pass;13 protected roots/frozen artifacts unchanged.
    Zero new visual/human/effective outcomes;20 prior screen rejections remain current.
    Stop for preparation review before AI inspection or ranks30+; scientific gates remain blocked.
    [Review137](docs/137-review-doc136-oulu-batch03-packets.md) accepts preparation
    and authorizes AI inspection only20..29.
    [Batch03 AI proposals](docs/138-review-response-doc137-oulu-batch03-ai-review.md)
    actually inspect30 bound panels/triggers and record10 pair-specific rejections,
    0 uncertain/confirmed,0 human/effective dispositions; batch03 is not closed.
    12 ledger files replay byte-identically;56 focused tests pass;14 protected
    roots/frozen13 unchanged. Reused foregrounds are correlated evidence, not
    independent accuracy/rater measurements. AI coverage30/85 leaves55 unreviewed.
    Stop for AI checkpoint review before human handoff or ranks30+; models remain locked.
    [Review139](docs/139-review-doc138-oulu-batch03-ai-review.md) accepts AI-proposal
    scope and requires genuine human handoff only20..29.
    [Batch03 human handoff](docs/140-review-response-doc139-oulu-batch03-human-handoff.md)
    preserves30 bound images, blank answers, collapsed AI notes and original ranks
    in download.33 private files independently reexport byte-identically;
    57 focused /244 full tests pass;15 protected roots/frozen13 unchanged.
    Exact77d3e7b CI success observed via Actions web after REST403; actual private
    browser interaction remains unverified(file403), not claimed from static tests.
    No human/effective outcomes. Stop for checkpoint review and genuine human input;
    separate batch03 rank-adapter import is required, no ranks30+ or model execution.
    [Batch03 human import](docs/141-oulu-batch03-human-review-import.md) now records
    the owner's actual JSON:10 rejections,10 AI agreements,0 disagreement and0
    effective activation.13-file independent reimport is byte-identical;
    58 focused /245 full tests pass;16 protected roots/frozen13 unchanged.
    Original answers/JSON preserved; all10 generic rationales share one text,
    disclosed without AI rewriting or independent-accuracy/authorship claims.
    Exact2fb3246 handoff CI success observed via Actions web. Comparison states
    are not current activation; stop for import checkpoint review before separate
    additive activation or ranks30+. No repeat human JSON/review is requested.
    [Review142](docs/142-review-doc141-oulu-batch03-human-import.md) accepts import
    without rework and authorizes separate additive activation only20..29.
    [Batch03 activation](docs/143-review-response-doc142-oulu-batch03-activation.md)
    now adds10 current screen-level rejections,0 uncertain/confirmed; historical
    import remains0 activated/accepted-state=false.13-file serialization replay
    is byte-identical;58 focused tests pass;18 protected roots/frozen13 unchanged.
    Exactede6e12 import CI success observed via Actions web; full245 not rerun here.
    Generic/non-blinded/correlated evidence limitations remain. Total30 resolved
    screen relationships are not global lineage clearance;55 highest-risk remain
    unreviewed. Stop for activation checkpoint review before ranks30+ or models.
    [Review144](docs/144-review-doc143-oulu-batch03-activation.md) accepts batch03
    closure without rework and permits preparation beginning at rank30.
    [Batch04 packets](docs/145-review-response-doc144-oulu-batch04-packets.md)
    prepare exactly30..39:15 videos,1690 accepted RGB frames,30 panels/triggers;
    1747 private files independently redecode/reexport byte-identically.
    59 focused /246 full tests pass;20 protected roots/frozen13 unchanged.
    Exactec244d2 activation CI success observed via Actions web;0 new AI/human/
    effective outcomes. Highest-risk AI coverage remains30/85,55 unreviewed
    (10 prepared/45 not yet prepared). Stop for packet review before actual AI
    inspection or ranks40+; research models and scientific gates remain locked.
    [Review146](docs/146-review-doc145-oulu-batch04-packets.md) accepts preparation
    without rework and authorizes AI review only30..39.
    [Batch04 AI proposals](docs/147-review-response-doc146-oulu-batch04-ai-review.md)
    now record actual30 bound image views and10 pair-specific rejection proposals,
    0 uncertain/confirmed,0 human/effective outcomes.12-file serialization replay
    is byte-identical;59 focused tests pass;22 protected roots/frozen13 unchanged.
    Exactd13904f preparation CI Success is observed via Actions web; full246
    not rerun here. Sparse/correlated and haze-detail limitations remain disclosed,
    not capture certification or independent accuracy. Highest-risk AI coverage
    is40/85,45 unreviewed; prior30 accepted screen relationships remain current.
    Batch04 is not closed. Stop for AI-checkpoint review before separate human
    handoff, ranks40+, activation or research-model execution.
    [Review148](docs/148-review-doc147-oulu-batch04-ai-review.md) accepts AI proposals
    without rework and requires a separate human handoff only30..39.
    [Batch04 human handoff](docs/149-review-response-doc148-oulu-batch04-human-handoff.md)
    now supplies blank answers, collapsed AI notes and a neutral heightened-scrutiny
    notice for38..39 outside those notes, with no prescribed disposition.
    Same30 bound images;33/33 independent reexport byte-identical.60 focused /
    247 full tests pass;24 protected roots/frozen13 and prior AI records unchanged.
    Exacta9f1e78 AI CI Success observed via Actions web. Actual private browser
    interaction remains unverified(file403); static/readback checks are not human
    inspection.0 human/effective outcomes; a separate bound30..39 importer and
    genuine human JSON are required later. Stop for handoff checkpoint review
    before import, activation, ranks40+, other-dataset or model work.
    [Batch04 human import](docs/150-oulu-batch04-human-review-import.md) now records
    the owner's actual exported JSON:10 rejects,10 AI agreements,0 disagreements
    and0 effective activation. Original30..39/raw JSON/answers preserved;
    13/13 independent reimport byte-identical,61 focused /248 full tests pass,
    26 protected roots/frozen13 unchanged. Exact5ec33a8 handoff CI Success observed.
    All10 human rationales share one generic text, preserved without AI rewriting;
    heightened-scrutiny reasoning for38..39 remains unresolved, not certified by
    agreement. No missing-human-JSON blocker or repeat whole-review request.
    Comparison states are not current activation; prior30 outcomes remain current.
    Stop for import-checkpoint review before separate scrutiny resolution,
    reconciliation, activation, ranks40+ or research-model work.
    [Review151](docs/151-review-doc150-oulu-batch04-human-import.md) accepts import
    without rework, forbids activation and requires targeted human reasoning38..39.
    [Targeted scrutiny handoff](docs/152-review-response-doc151-oulu-targeted-scrutiny-handoff.md)
    now prepares only2 pairs/6 existing bound assets, blank structure/sufficiency/
    disposition/rationale/attestation fields, original-row references and collapsed
    AI notes.9/9 independent export byte-identical;62 focused /249 full tests pass;
    28 protected roots/frozen13 unchanged. Exact1532e80 import CI Success observed.
    Private browser interaction remains unverified(file403); no semantic reasoning
    sufficiency or new human resolution is claimed. Original10-pair JSON and30..37
    remain untouched. Stop for152 review and genuine separate2-pair resolution JSON,
    before targeted import, activation, ranks40+, other-dataset or model work.
    [Targeted human import153](docs/153-oulu-batch04-targeted-human-import.md)
    now preserves the genuine separate38..39 JSON:2 rejects/0 disagreement,
    0 activation;5/5 independent immutable import files match.63 focused/250 full
    tests pass;30 protected roots/frozen13 unchanged. Both structure descriptions
    and brief background-only rationales repeat; semantic scrutiny sufficiency
    remains pending, not manufactured by AI. New input exists; no whole-batch
    repeat or original JSON replacement is requested. Stop for153 review before
    clarification/reconciliation, separate activation, ranks40+ or model work.
    [Review154](docs/154-review-doc153-oulu-batch04-targeted-human-import.md)
    accepts153 import without rework but rejects semantic scrutiny resolution.
    [Additive clarification handoff155](docs/155-review-response-doc154-oulu-clarification-handoff.md)
    now prepares38..39 only: blank left/right foreground, temporal/trigger reasoning,
    haze limitation and sufficiency/disposition/attestation, with dual old human-row
    and153 scrutiny-row bindings.9/9 independent export byte-identical;64 focused/
    251 full tests pass;32 roots/frozen13 unchanged. Actual private browser remains
    file403/unverified.0 new clarification/0 activation; both old JSONs stay intact.
    Stop for155 review and new separate pair-specific clarification JSON, before
    its import/review, activation, ranks40+, other datasets or model execution.
    [Genuine clarification import156](docs/156-oulu-batch04-pair-specific-clarification-import.md)
    now binds the new owner38..39 JSON:2 rejects/0 disagreement/0 activation,
    distinct left/right foreground, haze and rationale text;5/5 independent immutable
    import files match.65 focused/252 full tests pass;34 roots/frozen13 and all three
    source JSONs unchanged. Fresh exact155 REST CI Success resolves stale web status.
    No validation-only field persists. Genuine clarification is present; semantic
    acceptance is a separate review, not a uniqueness check. Stop for156 review,
    before reconciliation, separate activation, ranks40+, other datasets or models.
    [Review157](docs/157-review-doc156-oulu-batch04-pair-specific-clarification.md)
    accepts156 and semantic scrutiny38..39, permitting a separate activation ledger.
    [Batch04 activation158](docs/158-review-response-doc157-oulu-batch04-activation.md)
    now materializes10 rejection rows30..39 in a new review-pending ledger;
    accepted current total remains30, prospective40 only after158 acceptance.
    13/13 serialization replay matches;30 image hashes/36 roots/frozen13 unchanged;
    65 existing focused tests pass. No code/test change; accepted full252 baseline
    is not locally rerun. Prior human/AI/import flags and source JSONs remain intact.
    Stop for158 review before any queue40+, other datasets or models.
    [Review159](docs/159-review-doc158-oulu-batch04-activation.md) accepts158,
    closes batch04 and supplies additive authority for40 accepted screen-level
    relationships, leaving all historical158/import pending flags unchanged.
    [Batch05 preparation160](docs/160-review-response-doc159-oulu-batch05-packets.md)
    prepares only frozen40..49:16 videos/1956 RGB frames,2014 private files;
    independent redecode/reexport2014/2014 matches and all1986 PNGs verified.
    66 focused/253 full tests pass;38 protected roots/frozen13 remain unchanged.
    Zero new AI/human/effective dispositions;40/85 AI reviewed,45 still unreviewed
    (10 prepared/35 not prepared). Stop for160 review and exact CI before AI visual
    inspection40..49, human handoff, ranks50+, other datasets or research models.
    [Review161](docs/161-review-doc160-oulu-batch05-packets.md) accepts160 and
    authorizes AI-only visual inspection of the30 bound assets for40..49.
    [Batch05 AI proposals162](docs/162-review-response-doc161-oulu-batch05-ai-review.md)
    records10 rejection proposals/0 uncertain/0 confirmed after30 actual image views;
    zero human/effective dispositions, accepted current total remains40.
    AI coverage50/85 leaves35 unreviewed;12/12 serialization replay matches,
    40 protected roots/frozen13 unchanged,66 focused tests pass; full253 is the
    accepted160 baseline, not rerun locally. Correlation and veil/dark-detail
    limitations remain; proposals are not capture independence or global clearance.
    Stop for162 review and exact CI before human handoff/import/activation,
    ranks50+, other datasets or research-model execution.
    [Review163](docs/163-review-doc162-oulu-batch05-ai-review.md) accepts162 and
    authorizes genuine human handoff for40..49 only, not activation or rank50+.
    [Batch05 human handoff164](docs/164-review-response-doc163-oulu-batch05-human-handoff.md)
    prepares blank disposition/visible-structure/rationale and false attestation,
    with neutral visibility warnings40..43/49 and collapsed AI notes; no quota.
    Original ranks/30 bound images are retained;33/33 reexport files match.
    Zero human/effective dispositions; current accepted40, AI50/85,35 unreviewed.
    67 focused/254 full tests pass;42 protected roots/frozen13 unchanged.
    Pure JS completion8 synthetic cases pass, not actual UI/human review:
    integrated private HTML is403; desktop/mobile interaction remains unverified.
    No private-asset bypass, extra decode or packages. Stop for164 review, then
    genuine human input and separate rank40..49/structure-aware import; no activation,
    ranks50+, other datasets or research models.
    The owner's exported JSON supplies scoped continuation for
    [Batch05 human import165](docs/165-oulu-batch05-human-import.md), with no new
    formal external review of164 claimed. Ten genuine rejection answers imported;
    zero disagreement/activation, accepted current total40. Original bytes and
    every human field preserved;13/13 serialization replay is not another review.
    Reference-only42/43/48/49 and duplicate-text groups are recorded neutrally;
    all pair-specific semantic review remains pending, with no answer override/quota.
    68 focused/255 full tests pass;44 protected roots/frozen13/config17 unchanged;
    original33 main handoff files unchanged plus only the pinned owner JSON.
    Stop for165 review and semantic follow-up before clarification/reconciliation/
    activation, ranks50+, other datasets or research models.
    [Review166](docs/166-review-doc165-oulu-batch05-human-import.md) accepts165 for
    mechanical/provenance import only, retrospectively accepts164 technically,
    and blocks semantic clearance/activation pending additive follow-up.
    [Governance/clarification handoff167](docs/167-review-response-doc166-oulu-batch05-clarification-handoff.md)
    records the process-order deviation and scopes importer nonmutation separately
    from AI-assisted wording; no independent blinded rationale authorship claimed.
    Only40/41/42/43/48/49 prepared,18 old assets/21 files;21/21 reexport matches.
    All human fields blank, including own-choice and wording-assistance disclosure;
    rank48 binds identical47 evidence without copying answers or forcing reinspection.
    No clean44..47 reopening, new clarification or activation; accepted current40.
    69 focused/256 full tests pass;46 roots/frozen13/config17 unchanged.
    Pure JS21 synthetic gate cases pass, not private UI verification; browser403,
    desktop/mobile/render/export unverified. No privacy/package/server bypass.
    Restore formal167 review before new human input/import; stop for that review
    before semantic follow-up/reconciliation/activation, ranks50+ or research models.
    [Review168](docs/168-review-doc167-oulu-batch05-clarification-handoff.md)
    accepts167 governance/scope/provenance but requires categorical-only UX before
    human use. [Categorical handoff169](docs/169-review-response-doc168-oulu-batch05-categorical-handoff.md)
    replaces typed descriptions/rationale/wording disclosure with sufficiency,
    conditional same/derived and personal-inspection/own-decision Yes/No choices.
    Earlier AI context stays hidden until pair submission; edits invalidate it.
    Old167 form and already supplied JSON are retained unimported, not converted.
    Exact6 ranks/18 old PNGs/21 files;21/21 reexport,48 prior roots/frozen13/config17
    unchanged;70 focused/257 full tests and32 pure JS synthetic cases pass.
    Actual private UI403; desktop/mobile/render/interaction/export unverified.
    No new categorical answers, machine narrative, activation, decode or AI views;
    accepted current40. All future manual checks are categorical, not required prose.
    Publish with fresh exact CI and stop for169 formal review BEFOREnew owner
    decisions and separately reviewed categorical import/semantic follow-up.
    No reconciliation/activation, ranks50+, other datasets or research models.
    [Review170](docs/170-review-doc169-oulu-batch05-categorical-handoff.md)
    accepts169 without rework and authorizes owner categorical use. The new JSON
    is now recorded by [categorical import171](docs/171-oulu-batch05-categorical-import.md):
    exact6 target ranks,6 reject answers,0 AI disagreement/prior-human changes,
    no scientific stop; every supplied field and raw source bytes preserved.
    Old167 JSON is not converted; original10 human records and historical flags
    remain unchanged.9/9 serialization replay is not another human adjudication.
    71 focused/258 full tests pass;50 prior roots/frozen13/config17 unchanged.
    No prose, new images/decode/AI views or machine narrative; categorical6,
    activation0/current40, batch05 open and semantic acceptance pending.
    Stop for171 review after fresh publication CI before semantic follow-up,
    reconciliation/activation, ranks50+, other datasets or research models.
    [Review172](docs/172-review-doc171-oulu-batch05-categorical-import.md)
    accepts171 and clears all six semantic blockers without more owner input.
    [Separate activation173](docs/173-review-response-doc172-oulu-batch05-activation.md)
    materializes10 batch05 screen-level rejects in a new review-pending ledger:
    six accepted categorical bindings plus four clean prior rows, no reconciliation
    or hard stop.13/13 serialization replay,30 image-hash bindings and52 prior
    roots/frozen13/config17 preservation pass;71 focused tests pass, accepted171
    full258 baseline is not locally rerun. No production code/test/policy changes,
    new judgments, images, decode or model work. New rows are not yet counted as
    accepted: current40, prospective50 after173 acceptance only; batch05 open.
    Source171 CI is successful but distinct from required fresh173 publication CI.
    Stop for173 activation review before ranks50+, other datasets or models.
    [Review174](docs/174-review-doc173-oulu-batch05-activation.md) accepts173,
    closes batch05 and advances accepted screen-level total to50 additively,
    without rewriting historical flags or requiring more owner input for40..49.
    [Batch06 preparation175](docs/175-review-response-doc174-oulu-batch06-packets.md)
    targets fixed50..59 but is BLOCKED before selected payload access: all3 archive
    stat identities differ only in device ID. Other stat fields match; current
    archive bytes were not rehashed, so unchanged content is not inferred.
    Strict guard retained;0 packets/PNGs/decode, no output roots or replay claim.
    72 focused/259 full tests pass;54 prior roots/frozen13/config17 unchanged.
    Stop for175 technical-blocker review and fresh exact publication CI; no AI/
    human handoff, later queue, other dataset or model work. Recovery needs an
    authorized additive technical identity check, not repeated owner/license review.
    [Review176](docs/176-review-doc175-oulu-batch06-archive-device-blocker.md)
    accepts175 as a blocker record and authorizes separate full-archive recovery.
    [Recovery177](docs/177-review-response-doc176-oulu-archive-identity-recovery.md)
    rehashes all105116817408 bytes: all3 whole-file SHA values equal the original
    frozen authority. New immutable observations and an additive environment binding
    record device-only drift; no remount cause is independently established.
    Old pins/guards/history,54 prior roots/frozen13/config17 remain unchanged;
    73 focused/260 full tests and immutable readback/refusal checks pass.
    Binding is review-pending, not a guard bypass or permission to retry packets:
    current50, AI50/85,0 new packets/decode/judgments. Publish177 with fresh exact
    CI, then stop for recovery review before a separate batch06 preparation retry.
    No repeated owner, license, administrative or human visual input is required.
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
