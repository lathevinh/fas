# 198 — Review of Document 197: OULU Batch-07 Categorical Owner Import

Date: 2026-10-15  
Repository: `lathevinh/fas`  
Reviewed commit: `024616c42d5bd42c395e3dbd41cdb5ef0995505d`  
Reviewed document: `docs/197-oulu-batch07-categorical-import.md`  
Reviewed aggregate: `results/phase1/oulu-categorical-import-batch07-v1.json`  
Reviewed importer: `scripts/import_oulu_categorical_batch07.py`

## Verdict

**DOCUMENT 197 — ACCEPTED WITHOUT REWORK.**

**BATCH-07 CATEGORICAL IMPORT — ACCEPTED FOR MECHANICAL, PROVENANCE, AND SEMANTIC-ADJUDICATION SCOPE.**

**ALL TEN OWNER CATEGORICAL DECISIONS FOR RANKS 60..69 ARE ACCEPTED AS `rejected_false_positive`.**

**THE SINGLE AI/HUMAN DISAGREEMENT IS FORMALLY RECONCILED BY REVIEW198 WITHOUT REQUIRING NEW OWNER INPUT.**

**THE ORIGINAL AI `uncertain_insufficient_evidence` PROPOSAL MUST REMAIN PRESERVED AS HISTORICAL NON-BINDING AI METADATA.**

**NO SCIENTIFIC HARD STOP IS TRIGGERED.**

**NO FURTHER OWNER/HUMAN INPUT IS REQUIRED FOR RANKS 60..69.**

**NEXT AUTHORIZED STEP: PREPARE A SEPARATE ADDITIVE BATCH-07 ACTIVATION CHECKPOINT.**

**CURRENT ACCEPTED EFFECTIVE SCREEN-LEVEL TOTAL REMAINS 60 UNTIL THAT ACTIVATION IS SEPARATELY MATERIALIZED AND REVIEWED.**

**AI-SCREEN COVERAGE REMAINS 70/85.**

**RANK70+, OTHER DATASETS, SOURCE DRY RUN, ANALYSIS FREEZE, LOCKED EVALUATION, AND RESEARCH-MODEL EXECUTION REMAIN BLOCKED UNTIL THE BATCH-07 ACTIVATION REVIEW.**

---

## 1. Authority and ordering

Review196 was committed before Document197 at `f03134d62b2c0a88e0a7ca33e71911264ea126a3`.

Review196 authorized genuine owner use of the accepted batch07 categorical form and required a separate importer/reconciliation checkpoint after export.

Document197 is therefore in the correct prospective order.

## 2. Exact scope

The import covers exactly integer ranks:

`60,61,62,63,64,65,66,67,68,69`.

No later queue rank is included and no rank is skipped.

## 3. Exact genuine owner export is bound

The received source is byte-pinned by SHA-256:

`cf8769cdaf6a8019e74def17ff8c3c4c0ad9f3e50a59ca418d95ac247a86d763`.

The importer requires the exact file location, rejects symlinks, and verifies this digest before import.

The original owner bytes remain unchanged.

## 4. Canonical snapshot is correctly separate

The canonical structured snapshot has SHA:

`f8c6ef80bcaf2d8a1a4eb2cca15d6e44033c290f9d8623b43446f27a13573197`.

This is correctly treated as a normalized structured representation rather than a claim of raw-byte identity.

## 5. Owner fields are preserved

The importer preserves all supplied owner top-level and per-pair fields.

Derived importer metadata is added only after checking for key collisions; a collision fails closed.

No human prose or machine narrative is invented.

## 6. Human-authorship claim remains bounded

The aggregate correctly states that categorical choices and inspection are attested but not independently authenticated by software.

This review does not elevate that to identity authentication, inter-rater reliability, or capture-provenance certification.

## 7. Exact handoff authority is rebound

The import binds Review196, accepted195 aggregate, accepted review-definition digest, owner export digest, accepted193 AI report and exact successful Document195 CI.

This prevents an unrelated handoff or owner file from authorizing import.

## 8. Strict categorical validation is correct

The importer requires exact version/type, identified human reviewer metadata, UTC review timestamp, exact ranks60..69, exact packet/AI/queue/image bindings, strict bool/null categorical values, both inspection/own-decision attestations, and `capture_provenance_certified=false`.

Invalid types, contradictory dispositions, contradictory hard-stop flags, and metadata collisions fail.

## 9. Full queue and evidence lineage are checked

The importer validates the accepted 6640-record queue bundle.

For every imported rank it rechecks packet SHA, AI-record SHA, exact frozen pair SHA, candidate identity and the three reviewed asset hashes against both the handoff and original packet assets.

The owner decisions are therefore strongly bound to the accepted evidence.

## 10. Dispositions are independently re-derived

The importer does not trust the exported disposition string.

It recomputes disposition from the strict categorical values and independently derives per-pair and aggregate scientific hard-stop state.

This is correct fail-closed behavior.

## 11. Actual owner result

The actual imported owner results are:

- `rejected_false_positive`: **10**
- `uncertain_insufficient_evidence`: **0**
- `confirmed_same_content_or_derived_lineage`: **0**

Therefore no owner-triggered scientific hard stop is present.

## 12. Actual AI result remains distinct

The accepted AI193 proposals remain:

- `rejected_false_positive`: **9**
- `uncertain_insufficient_evidence`: **1**
- confirmed same/derived: **0**

Document197 does not rewrite this history.

## 13. Exactly one disagreement exists

One row is:

- AI: `uncertain_insufficient_evidence`
- owner: `rejected_false_positive`

The importer correctly records:

- `disagreement_with_AI=true`
- `reconciliation_required=true`
- `comparison_disposition=uncertain_insufficient_evidence`

The original owner rejection and AI uncertainty remain separate.

## 14. Comparison state is not an effective disposition

The conservative comparison uncertainty is audit metadata.

It does not replace the owner categorical result and is not activated.

This distinction is correctly preserved.

## 15. Why Review198 can reconcile the disagreement without another owner pass

This is not a contradiction between AI-confirmed same/derived lineage and a human rejection.

It is AI uncertainty versus an owner rejection.

The AI stage was explicitly non-binding.

The accepted human form began blank and hid AI context until after valid pair submission, so the owner supplied an independently owned categorical judgment on the fixed evidence.

The owner also attested personal inspection, decision ownership, evidence sufficiency and same/derived = No.

Accordingly, the formal review can accept the owner screen-level disposition while retaining the AI uncertainty as historical metadata.

No additional owner review adds a necessary governance fact here.

## 16. Reconciliation is not an accuracy claim

Review198 does not claim that the AI was wrong or that the owner decision is independently proven correct.

It only resolves the workflow authority:

- AI proposal remains non-binding and uncertain;
- owner categorical decision is the accepted semantic screen-level disposition after formal review;
- disagreement remains reportable historical provenance.

## 17. Nine agreeing rows are semantically clear

The nine AI/human rejection agreements contain no remaining reconciliation blocker.

They are accepted as owner screen-level dispositions.

## 18. The disagreement row is semantically accepted additively

Review198 accepts the independently supplied owner rejection for the single disagreement row.

The original import row must not be edited: its `reconciliation_required=true`, `semantic_acceptance_pending=true` and comparison uncertainty remain immutable creation-time facts.

Review198 is the additive reconciliation/semantic-acceptance authority.

## 19. No new owner input is required

Do not ask the owner to repeat the form, type rationale, expose more evidence, or re-answer the single disagreement.

No new human prose is required.

## 20. Import replay and preservation are sound

Main and sibling each contain 13 import files and match **13/13 byte-for-byte**.

This is serialization reproducibility, not a second human decision.

Document197 reports 71 protected prior roots, frozen13 and config17 unchanged, with historical packet/AI/form pending flags and prior helper/importer pins preserved.

## 21. Refusal behavior is fail-closed

Actual probes reject existing main/sibling outputs, repository output, source-overlap output and symlink output.

Additional probes reject wrong source195 CI, activation authority during import, and wrong owner digest without creating output.

Immutable overwrite attempts against preflight, canonical input and first imported row also fail.

## 22. Tests are clean

New focused importer test: **1/1 passed**.

Focused suite: **80/80 passed**.

Full suite: **267/267 passed**.

The new test explicitly covers the important case where AI remains uncertain while the owner rejects, preserving disagreement metadata, comparison uncertainty and all original owner fields.

All three categorical outcomes remain supported by synthetic branches.

## 23. No media/model work occurs

Document197 performs no new image opening, AI visual review, human re-review, media decode/extraction, archive rehash, model execution or other-dataset work.

No environment/workflow/policy/role/selector/seed change occurs.

## 24. Fresh exact Document197 publication CI passes

Exact reviewed commit:

`024616c42d5bd42c395e3dbd41cdb5ef0995505d`

Fresh GitHub Actions run:

`38719866755`

is `completed / success`.

Validate job:

`116371485847`

is `completed / success`.

The job completed at:

`2026-10-15T10:23:47Z`.

There is no publication-CI blocker.

## 25. Historical Document197 flags remain immutable

Document197 intentionally records:

- `semantic_acceptance_pending=true`
- `reconciliation_completed=false`
- `effective_dispositions_activated=0`
- `activation_authorized=false`
- `batch07_closed=false`

Do not rewrite these historical creation-time fields.

Review198 supplies additive semantic acceptance and reconciliation.

## 26. Next authorized checkpoint

The next checkpoint may create a **separate additive batch07 activation ledger** for exact ranks60..69.

It should bind at minimum:

- Review198
- Document197 aggregate
- exact imported ten-row bundle
- canonical owner snapshot
- original received owner SHA
- exact successful Document197 CI
- accepted packet/AI/definition lineage

The activation must preserve the historical AI uncertainty and disagreement.

## 27. Activation provenance requirement

The activation checkpoint should explicitly state:

- all ten accepted owner semantic dispositions are rejection;
- one original AI proposal was uncertainty;
- Review198 reconciled that AI-uncertain / owner-rejection difference at governance level;
- the original AI proposal is not rewritten;
- no confirmed same/derived hard stop exists.

## 28. Current and prospective totals

Before activation:

**accepted effective screen-level total = 60**.

If the separate activation is later formally accepted:

**60 -> 70**.

Do not report 70 as current before activation review.

AI-screen coverage remains:

**70/85**.

## 29. Queue continuation remains blocked

Fifteen highest-risk candidates remain not yet AI-screened.

Do not start rank70+ until the separate batch07 activation checkpoint has been published and formally reviewed.

## 30. Scientific stages remain blocked

This review does not authorize source dry run, analysis freeze, locked evaluation, classifier/risk-model execution, training, target evaluation or other dataset execution.

Scientific readiness remains false.

## Current state after Review198

- accepted effective screen-level total: **60 / 85**
- accepted AI-screen coverage: **70 / 85**
- accepted batch07 owner semantic decisions: **10 rejections**
- historical AI/human disagreements: **1**
- unresolved reconciliation blockers after Review198: **0**
- confirmed same/derived hard stops: **0**
- batch07 activated dispositions: **0**
- candidates not yet AI-screened: **15**

## Final disposition

**DOCUMENT 197 — ACCEPTED WITHOUT REWORK.**

**BATCH07 CATEGORICAL IMPORT — ACCEPTED.**

**ALL TEN OWNER CATEGORICAL DECISIONS ARE SEMANTICALLY ACCEPTED AS `rejected_false_positive`.**

**THE SINGLE AI-UNCERTAIN / OWNER-REJECTION DISAGREEMENT IS FORMALLY RECONCILED BY REVIEW198 WITHOUT NEW OWNER INPUT.**

**THE ORIGINAL AI UNCERTAINTY AND DISAGREEMENT METADATA MUST REMAIN IMMUTABLE HISTORICAL PROVENANCE.**

**NO SCIENTIFIC HARD STOP IS TRIGGERED.**

**NO FURTHER OWNER INPUT IS REQUIRED FOR RANKS60..69.**

**NEXT AUTHORIZED STEP: PREPARE A SEPARATE ADDITIVE BATCH07 ACTIVATION CHECKPOINT.**

**ACCEPTED EFFECTIVE TOTAL REMAINS 60 UNTIL ACTIVATION IS MATERIALIZED AND REVIEWED.**

**AI-SCREEN COVERAGE REMAINS 70/85.**

**RANK70+, OTHER DATASETS, AND RESEARCH-MODEL / LATER SCIENTIFIC STAGES REMAIN BLOCKED UNTIL THE BATCH07 ACTIVATION REVIEW.**
