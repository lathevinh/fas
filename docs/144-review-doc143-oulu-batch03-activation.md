# 144 — Review of Document 143: OULU Batch-03 Additive Activation

Date: 2026-10-13  
Repository: `lathevinh/fas`  
Reviewed commit: `ec244d2ff9a7c6db28d236aa6b0dc01f83c36e43`  
Reviewed document: `docs/143-review-response-doc142-oulu-batch03-activation.md`

## Verdict

**DOCUMENT 143 — ACCEPTED.**

**CHECKPOINT 1.5W OULU BATCH-03 ADDITIVE CURRENT-LEDGER ACTIVATION — ACCEPTED WITHOUT REWORK.**

**BATCH 03 IS NOW CLOSED AT SCREEN LEVEL: 10 REJECTED, 0 UNCERTAIN, 0 CONFIRMED SAME/DERIVED.**

Document 143 correctly performs the separate additive activation authorized by Review 142. It promotes only the already agreed AI/human screen-level outcomes for frozen ranks 20–29 into a new current ledger, while preserving the original AI proposals, human JSON, human-import comparison records, and all prior batches as immutable history.

With this review acceptance, the project may proceed to prepare the next frozen queue batch beginning at rank 30. This does not complete the OULU lineage audit or authorize research-model execution.

## 1. Activation scope is exactly correct

The current batch-03 ledger covers only ranks 20–29, with 10 `rejected_false_positive`, 0 uncertain, 0 confirmed same/derived and 10 effective activations.

The public aggregate records `batch03_accepted_reconciled_disposition_state = true` and `effective_dispositions_activated = 10`.

This matches Review 142 authority.

## 2. Historical import state remains immutable

The accepted human-import checkpoint remains at 0 effective activations and accepted/reconciled state false. Historical rows retain `effective_disposition_activated = false`.

The new current ledger is additive rather than a mutation of prior history.

## 3. AI and human evidence are not retroactively rewritten

The checkpoint preserves the original AI proposals, owner-human JSON, human answers/rationales, comparison records, packets and prior batch records.

The current rows bind the old records by digest rather than pretending the effective state existed earlier.

## 4. No hidden reconciliation is introduced

Batch 03 had 10 AI rejects, 10 human rejects, 0 disagreements and 0 confirmed same/derived cases.

Therefore no reconciliation checkpoint is needed, and Document 143 correctly does not fabricate one.

## 5. Human-review limitations remain disclosed

All ten human rationales remain the same general text. The review was not fully blinded, and correlated foreground configurations are not independent statistical replicates.

Document 143 correctly preserves these as limitations and does not claim inter-rater reliability, blinded adjudication or independently validated disposition accuracy.

## 6. Activation authority is adequately bound

The activation binds Review 142, Document 141/public import report, exact successful import CI, owner input, review definition/assets, accepted AI report, AI/human bundles, import lineage/summary/verification, the activation preflight, immutable writer and frozen hashes.

This is an appropriate authority chain.

## 7. Current rows retain source and historical context

Each current row reportedly binds Review 142 authority, the activation digest, original AI/human pair digests and packet digest, while retaining historical AI/human/comparison states and activation=false metadata.

This makes the current state auditable.

## 8. Reproducibility and immutability are strong

The private activation export contains 13 files: activation, successful-CI observation, ten current pair rows and summary.

Independent replay produces **13 / 13 byte-identical files**. Existing-output reuse and record overwrite are refused.

## 9. Protected evidence remains unchanged

The checkpoint reports 18 protected roots and all 13 frozen artifacts unchanged. Prior batch records and batch-03 packet/AI/handoff/owner/import evidence remain unchanged.

No role, selector, seed or screening-threshold change is introduced.

## 10. Two initial preflight field-name mistakes are not a blocker

Two early preflight checks used incorrect metadata field names. They were corrected by inspecting the accepted source schema before any new preflight or activation artifact existed.

No accepted evidence was edited to make the check pass.

I classify this as a check-implementation correction, not evidence contamination or a scientific defect.

## 11. Focused regression is sufficient

Focused OULU regression reports **58/58 passed**.

The prior accepted import checkpoint had **245/245** full regression tests. Since no production code, tests, policy, environment or CI workflow changed in Document 143, not rerunning the full suite locally is acceptable.

## 12. Fresh exact activation CI passes

Fresh GitHub Actions for exact commit `ec244d2ff9a7c6db28d236aa6b0dc01f83c36e43` completed successfully.

Run `38325981545`, validate job `115064633017`, completed successfully and passed synthetic regression, schema validation and fail-closed checks.

There is no CI blocker on checkpoint 1.5W.

## 13. Batch 03 is now formally closed at screen level

Current accepted screen-level state:

- Batch 01: 10 rejected;
- Batch 02: 10 rejected;
- Batch 03: 10 rejected.

Total: **30 resolved perceptual-screen candidate relationships.**

These are not 30 cleared videos and do not prove independent capture provenance.

## 14. Ranks 30+ may now proceed

With this review acceptance, the next frozen queue batch may be prepared beginning at rank 30.

The same rules remain mandatory: fixed queue order, no outcome-dependent skipping, no threshold retuning, no role repair, no seed retry, no silent sample deletion and no selector changes.

Any future confirmed same/derived cross-role case remains a scientific hard stop.

## 15. Global lineage audit remains incomplete

After this activation, 30/85 highest-risk candidates have completed the current review chain and 55 still lack AI visual review.

Broader cross-role, non-exact and future cross-dataset lineage checks remain incomplete.

## 16. Scientific/model gates remain blocked

This checkpoint does not authorize data-audit completion, source-dry-run, analysis freeze, locked target evaluation, detector/model execution, target-domain experiments or scientific readiness.

## Final disposition

**DOCUMENT 143 — ACCEPTED.**

**CHECKPOINT 1.5W OULU BATCH-03 ADDITIVE ACTIVATION — ACCEPTED WITHOUT REWORK.**

Batch 03 is now formally closed at screen level:

**10 rejected, 0 uncertain, 0 confirmed same/derived.**

Across batches 01–03 there are now **30 accepted screen-level rejections**.

**The next fixed queue batch beginning at rank 30 may now be prepared.**

This acceptance does not imply global lineage clearance, capture-provenance certification, data-audit completion or authorization to execute the research models.
