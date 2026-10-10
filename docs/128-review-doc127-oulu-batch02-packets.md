# 128 — Review of Document 127: OULU Batch-02 Evidence Preparation

Date: 2026-10-10  
Repository: `lathevinh/fas`  
Reviewed commit: `b9acf99df111346b4ebbf304cc2d6102be10a261`  
Reviewed document: `docs/127-review-response-doc126-oulu-batch02-packets.md`

## Verdict

**DOCUMENT 127 — ACCEPTED.**

**CHECKPOINT 1.5N OULU BATCH-02 EVIDENCE PREPARATION — ACCEPTED WITHOUT REWORK.**

Document 127 correctly implements the next bounded queue step after batch-01 closure. It prepares, but does not adjudicate, the next fixed ten high-risk candidates.

## 1. Queue selection is correct

The checkpoint prepares exactly:

- queue ranks 10 through 19;
- ten pairs;
- all in frozen order;
- no skipping;
- no replacement;
- no outcome-dependent selection;
- no screening-threshold retuning.

This satisfies the queue-progression requirements from Review 126.

## 2. Batch-02 scope is preparation only

The checkpoint creates evidence packets only.

It does **not** claim:

- visual adjudication;
- AI dispositions;
- human dispositions;
- effective dispositions;
- scientific clearance.

Reported counts correctly remain:

- images visually reviewed: 0;
- new AI dispositions: 0;
- new human dispositions: 0;
- new effective dispositions: 0.

This separation between evidence generation and adjudication is methodologically sound.

## 3. Evidence generation is strongly bound and reproducible

Batch-02 preparation includes:

- 15 distinct videos;
- 2,135 decoded RGB frames verified against the accepted media index;
- 2,135 persisted verified-frame PNGs;
- 30 temporal-panel / trigger PNGs;
- 15 video manifests;
- 10 pair packets;
- lineage and summary records.

Total private export:

**2,192 files.**

The independent reread/redecode/reexport reproduces all:

**2,192 / 2,192 files byte-identically.**

This is strong evidence-generation reproducibility.

## 4. Initial file-count mistake is not a scientific defect

The first readback check incorrectly expected 2,182 files.

The corrected count is:

\[
2135 + 30 + 15 + 10 + 2 = 2192
\]

The exported evidence was not modified to satisfy the corrected assertion.

Therefore this was an accounting/check expectation error, not evidence tampering or a reproducibility failure.

The corrected replay remains byte-identical.

## 5. Existing accepted evidence remains unchanged

The checkpoint preserves:

- accepted batch-01 activation/current ledger;
- prior visual packet roots;
- AI records;
- human handoff/import records;
- Pair-5 reconciliation proposal;
- owner acceptance;
- all 13 frozen artifacts.

The accepted batch-01 visual runner/module/policy also remain byte-for-byte unchanged.

This is correct.

## 6. Existing-output behavior remains fail-closed

Attempting to reuse an accepted output root returns a failure rather than overwriting evidence.

The original output remains unchanged.

No temporary AVI files remain.

This is appropriate immutable-evidence behavior.

## 7. Tests pass

Reported tests:

- focused OULU regression: **53/53 passed**;
- full regression: **240/240 passed**;
- zero failures/errors.

This is stronger than the prior data-only checkpoints because the full regression was rerun locally.

## 8. Exact checkpoint CI passes

Fresh GitHub Actions for exact commit:

`b9acf99df111346b4ebbf304cc2d6102be10a261`

completed successfully.

Therefore the preparation checkpoint is backed by:

- successful focused tests;
- successful full local regression;
- successful exact pushed-commit CI.

## 9. Current queue state is accurately represented

After this checkpoint, of the 75 high-risk candidates remaining after batch 01:

- 10 are prepared for review;
- 65 are not yet prepared;
- all 75 remain unreviewed in this new phase.

This is correctly reported.

## 10. Batch-02 visual review may now begin

With this review acceptance, visual adjudication may begin for:

- queue ranks 10 through 19.

The reviewer should inspect the bound panels/triggers and create supported proposals only.

Ambiguous cases should remain:

`uncertain_insufficient_evidence`

until stronger evidence is obtained.

## 11. Confirmed lineage remains a hard stop

If any batch-02 pair is judged:

`confirmed_same_content_or_derived_lineage`

the workflow must stop for an explicit prospective scientific decision.

Do not:

- automatically delete a video;
- reassign a role;
- retry the split seed;
- alter the selector;
- retune the screening threshold;
- silently continue the queue.

## 12. Human adjudication remains separate

AI-assisted proposals in batch 02 should remain proposals.

Any owner/human review and disagreement reconciliation should be recorded in separate bound checkpoints, preserving the same provenance discipline used in batch 01.

## 13. Broader scientific gates remain blocked

This checkpoint does not complete:

- all remaining high-risk OULU pairs;
- remaining cross-role candidates;
- cross-partition/conflicting-label candidates;
- overall OULU lineage adjudication;
- cross-dataset lineage checks;
- core data audit.

Therefore:

- data-audit remains blocked;
- source-dry-run remains blocked;
- analysis-freeze remains blocked;
- locked evaluation remains blocked;
- model execution remains unauthorized;
- scientific readiness remains false.

## Final disposition

**DOCUMENT 127 — ACCEPTED.**

**CHECKPOINT 1.5N OULU BATCH-02 EVIDENCE PREPARATION — ACCEPTED WITHOUT REWORK.**

Batch 02 is now validly prepared for visual adjudication:

**10 prepared pairs (queue ranks 10–19), 0 reviewed, 0 dispositions.**

The next permitted step is visual review of those ten fixed pairs only.
