# 200 — Review of Document 199: OULU Batch-07 Additive Activation

Date: 2026-10-16  
Repository: `lathevinh/fas`  
Reviewed commit: `4ab5d05b6b85faa4f849361224653d41dacc19e6`  
Reviewed document: `docs/199-review-response-doc198-oulu-batch07-activation.md`  
Reviewed aggregate: `results/phase1/oulu-batch07-activation-v1.json`

## Verdict

**DOCUMENT 199 — ACCEPTED WITHOUT REWORK.**

**BATCH-07 ADDITIVE ACTIVATION — ACCEPTED.**

**BATCH-07 SCREEN-LEVEL REVIEW — CLOSED.**

**ACCEPTED CURRENT EFFECTIVE SCREEN-LEVEL TOTAL ADVANCES FROM 60 TO 70.**

**AI-SCREEN COVERAGE REMAINS 70/85.**

**THE SINGLE HISTORICAL AI-UNCERTAIN / OWNER-REJECTION DISAGREEMENT REMAINS PRESERVED AS PROVENANCE; UNRESOLVED RECONCILIATION BLOCKERS = 0.**

**NO SCIENTIFIC HARD STOP IS TRIGGERED.**

**PREPARATION OF THE NEXT FROZEN QUEUE BLOCK, RANKS 70..79, IS AUTHORIZED.**

**RANK80+, OTHER DATASETS, SOURCE DRY RUN, ANALYSIS FREEZE, LOCKED EVALUATION, AND RESEARCH-MODEL EXECUTION REMAIN BLOCKED UNTIL THEIR SEPARATE GOVERNANCE GATES ARE CLEARED.**

---

## Review findings

Review198 was committed before Document199 and explicitly accepted Document197, all ten owner rejections for ranks60..69, reconciled the single AI-uncertain / owner-rejection disagreement, preserved the original AI uncertainty as historical provenance, and authorized a separate additive activation checkpoint. There is no ordering violation.

Document199 activates exactly ranks `60..69`. It does not rewrite Document197 import rows, the original owner bytes, AI193 proposal records, historical comparison uncertainty, or the original `reconciliation_required=true` creation-time state.

The new activation ledger contains ten rows, all `rejected_false_positive`, with zero uncertain effective dispositions and zero confirmed same/derived dispositions. No scientific hard stop is present.

The accepted AI history remains nine rejections and one `uncertain_insufficient_evidence`. The historical disagreement count therefore remains one. Review198 resolved the governance blocker, so unresolved reconciliation blockers are now zero. This must not be reported as ten AI-human agreements.

The activation rows preserve original AI disposition, disagreement flag, historical import reconciliation state and historical comparison disposition. They correctly avoid claiming AI error, independent owner accuracy, capture independence or inter-rater reliability.

Only the new activation rows set `effective_disposition_activated=true`. Before Review200 they also retain `activation_checkpoint_review_pending=true` and `counts_as_accepted_current_effective_disposition=false`, so Document199 did not self-authorize the 60→70 transition. Review200 supplies that additive acceptance.

Provenance is sufficient: Document199 binds Review198, Document197 document/aggregate, accepted import row bundle, original owner input SHA, canonical owner snapshot, import lineage, review definition, packet/AI/queue records and the 30 existing image hashes. No new visual evidence, human review, AI review, decode, extraction or archive rehash occurs.

Main and sibling activation roots each contain 13 files and match 13/13 byte-identically. This is deterministic serialization replay, not another adjudication.

Protected history remains unchanged: 73 protected prior roots, frozen13, study17 configs and prior source/helper/test/policy pins remain stable. Output guards refuse existing main/sibling outputs, repository paths, source-overlap paths and symlink outputs. Immutable overwrite attempts against preflight, activation authority and first activation row fail with `FileExistsError`.

No production code, tests, policy, environment, workflow, roles, selector or seeds change in this checkpoint. Focused regression remains 80/80 passed. The accepted Document197 full-suite baseline remains 267/267; Document199 does not falsely claim a fresh local full-suite run.

During preparation, one head-filtered REST query for source197 encountered a 403 rate-limit. This is not treated as CI failure. More importantly, fresh exact publication CI for Document199 itself passes:

- commit `4ab5d05b6b85faa4f849361224653d41dacc19e6`
- run `38844328951` — completed/success
- validate job `116791294915` — completed/success
- validate job completed at `2026-10-16T03:13:03Z`

There is no publication-CI blocker.

## Additive acceptance

Historical Document199 creation-time fields must remain unchanged, including current total60, prospective70, activation-review pending and `batch07_closed=false`.

Review200 now supplies the additive acceptance authority.

Therefore:

- prior accepted effective total = 60
- newly accepted batch07 effective dispositions = 10
- accepted current effective total = **70**
- batch07 screen-level review = **closed**
- historical AI/human disagreements = **1**
- unresolved reconciliation blockers = **0**
- confirmed same/derived = **0**
- scientific hard stop = **false**

No further owner input is required for ranks60..69.

## Next authorized work

AI-screen coverage remains **70/85**. Fifteen candidates remain not yet AI-screened: ranks70..84.

The next authorized bounded block is:

`70..79`

Maintaining a ten-candidate block preserves the established prospective audit granularity. Do not jump directly to `70..84`.

The expected sequence remains packet preparation → packet review → AI proposals → AI review → categorical handoff → handoff review → owner decisions → import/reconciliation → import review → separate activation → activation review.

Rank80..84 remains blocked until batch08 reaches its accepted continuation boundary.

Other datasets and research/scientific stages remain blocked, including source dry run, classifier/branch execution, risk-model training, analysis freeze, locked evaluation and target evaluation.

## Current state after Review200

- accepted effective screen-level total: **70/85**
- accepted AI-screen coverage: **70/85**
- historical AI/human disagreements: **1**
- unresolved reconciliation blockers: **0**
- confirmed same/derived: **0**
- scientific hard stop: **false**
- remaining not yet AI-screened: **15**
- next authorized frozen block: **70..79**

## Final disposition

**DOCUMENT 199 — ACCEPTED WITHOUT REWORK.**

**BATCH07 ADDITIVE ACTIVATION — ACCEPTED.**

**BATCH07 SCREEN-LEVEL REVIEW — CLOSED.**

**ACCEPTED CURRENT EFFECTIVE SCREEN-LEVEL TOTAL = 70.**

**AI-SCREEN COVERAGE = 70/85.**

**THE SINGLE HISTORICAL AI-UNCERTAIN / OWNER-REJECTION DISAGREEMENT REMAINS PRESERVED AS PROVENANCE.**

**UNRESOLVED RECONCILIATION BLOCKERS = 0.**

**NO SCIENTIFIC HARD STOP IS TRIGGERED.**

**PREPARATION OF THE NEXT FROZEN QUEUE BLOCK, RANKS70..79, IS AUTHORIZED.**

**RANK80+, OTHER DATASETS, AND RESEARCH-MODEL / LATER SCIENTIFIC STAGES REMAIN BLOCKED.**
