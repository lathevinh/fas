# 148 — Review of Document 147: OULU Batch-04 AI Visual Proposals

Date: 2026-10-13  
Repository: `lathevinh/fas`  
Reviewed commit: `a9f1e78bceb5f6c0c2a16e855aa82ca270ff0392`  
Reviewed document: `docs/147-review-response-doc146-oulu-batch04-ai-review.md`

## Verdict

**DOCUMENT 147 — ACCEPTED FOR AI-PROPOSAL SCOPE.**

**CHECKPOINT 1.5Y OULU BATCH-04 AI-ASSISTED VISUAL PROPOSALS — ACCEPTED WITHOUT METHOD REWORK.**

**BATCH 04 EFFECTIVE / SCIENTIFIC CLOSURE — NOT ACCEPTED YET.**

Document 147 correctly reviews only frozen ranks 30–39, records AI proposals only, preserves accepted packet/history state, and stops before any human or effective disposition is created.

## Main findings

- 10 fixed pairs reviewed.
- 30 bound images actually viewed: `temporal_a`, `temporal_b`, `trigger`.
- AI proposals: **10 `rejected_false_positive`**, 0 uncertain, 0 confirmed same/derived.
- Human dispositions: 0.
- Effective activations: 0.
- Batch-04 accepted/reconciled state remains false.
- Pair-specific nonblank unique AI rationales: 10.
- Private AI ledger: 12 files.
- Serialization replay: **12/12 byte-identical**.
- Focused regression: **59/59 passed**.
- Prior full regression: **246/246 passed**.

## Repeated 10/10 rejection pattern

Another 10/10 rejection batch deserves attention, but is not itself a protocol defect. Queue order was frozen, no candidate was skipped/replaced, uncertainty and confirmation remained allowed, no rejection quota was imposed, and no threshold/role/seed/selector change occurred.

This pattern should later be reported as an empirical property of the screening queue rather than hidden.

## Correlated evidence

Ranks 31–32 reuse one foreground, 34–35 another, and 36–39 repeat a banded-coat foreground with related opposite configurations. These records may remain separate candidate decisions, but **must not be interpreted as independent statistical validations**.

## Haze/veil limitation in ranks 38–39

Document 147 explicitly discloses that haze/veil reduces some torso detail in ranks 38–39.

I do **not** require those AI proposals to be automatically downgraded to `uncertain_insufficient_evidence`, because the published rationale states that rejection is based on still-visible garment structure and scene-layout divergence rather than haze itself.

However, these two pairs should be treated as **heightened-scrutiny cases during human review**. The human reviewer should give pair-specific reasoning for ranks 38–39 and should choose `uncertain_insufficient_evidence` if the remaining visible evidence is not independently sufficient.

A generic rationale reused across all ten human pairs would be particularly weak for ranks 38–39.

## Evidence scope

The proposals concern only the observed sparse rendered-content evidence.

They do not establish:

- full-video independence;
- capture provenance;
- absence of partial/cropped/shifted/transformed overlap;
- absence of all shared source material;
- global OULU lineage clearance.

Only the 30 bound sparse assets were visually inspected, not all 1,690 original frames or full videos.

## Provenance

Each private AI row is reportedly bound to:

- exact candidate;
- exact packet;
- three viewed asset hashes;
- both video manifests;
- temporal decode orders;
- trigger decode order / accepted RGB identity;
- review and policy authority.

All 22 protected roots, frozen artifacts and prior AI/human/current/historical evidence remain unchanged.

## CI

Prerequisite packet-preparation CI is correctly bound to exact commit:

`d13904f450c7642d4be5b7cbd866771793b4fe68`

run `38328370472`, validate job `115072236960`, completed/success.

Fresh CI for the exact Document-147 commit also passes:

- commit: `a9f1e78bceb5f6c0c2a16e855aa82ca270ff0392`
- run: `38332170137`
- validate job: `115084143725`
- status/conclusion: `completed / success`

Synthetic regression, canonical schema validation and fail-closed checks all pass.

## Current state

Highest-risk AI review coverage is now:

**40 / 85**

with:

**45 / 85 still not AI visually reviewed.**

The prior 30 accepted screen-level relationships remain the only current effective outcomes. Batch 04 is still open.

## Required next step

Prepare a separate genuine human-review handoff for exactly ranks 30–39.

Requirements:

1. preserve AI ledger unchanged;
2. use the same 30 bound assets;
3. start human dispositions/rationales blank;
4. do not pre-select AI answers;
5. keep AI notes collapsed initially;
6. require explicit human disposition, rationale and personal-review attestation per pair;
7. preserve original ranks 30–39;
8. surface the haze/veil limitation for ranks 38–39 without prescribing an answer.

Conservative resolution must remain:

- AI reject + human reject → eligible for later additive activation;
- AI reject + human uncertain → remain uncertain pending reconciliation;
- human confirmed same/derived → immediate scientific hard stop.

Do not begin ranks 40+ yet.

## Final disposition

**DOCUMENT 147 — ACCEPTED FOR AI-PROPOSAL SCOPE.**

**CHECKPOINT 1.5Y — ACCEPTED WITHOUT METHOD REWORK.**

Current result:

**10 AI rejects, 0 uncertain, 0 confirmed, 0 human, 0 effective.**

The haze/veil in ranks 38–39 and correlated foreground reuse are real limitations but do not invalidate the checkpoint. Ranks 38–39 should receive heightened scrutiny in the genuine human review.

**Next: human-review handoff for ranks 30–39 only.**
