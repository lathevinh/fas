# 122 — Review of Document 121: OULU Pair-5 Evidence-Linked Reconciliation

Date: 2026-10-10  
Repository: `lathevinh/fas`  
Reviewed commit: `ba2add2ffcd9a562f89fa5b2cdd141b207021e12`  
Reviewed document: `docs/121-review-response-doc120-oulu-pair5-reconciliation.md`

## Verdict

**DOCUMENT 121 — ACCEPTED FOR ITS RECONCILIATION-PROPOSAL SCOPE.**

**CHECKPOINT 1.5K PAIR-5 EVIDENCE-LINKED RECONCILIATION PROPOSAL — ACCEPTED WITHOUT METHOD REWORK.**

**PAIR-5 FINAL RECONCILIATION / BATCH-01 CLOSURE — NOT YET ACCEPTED.**

Document 121 satisfies the methodological requirements from Review 120: it treats Pair 5 separately, preserves both prior ledgers, introduces pair-specific frame-linked evidence, and does not silently promote the disputed human rejection into the effective ledger.

The checkpoint still explicitly labels the result as a proposal pending owner checkpoint review. That boundary is appropriate and should be preserved.

## 1. Pair 5 is isolated correctly

The checkpoint acts only on:

- Pair 5;
- queue rank 4;
- the one unresolved AI/human disagreement.

It does not reopen the other nine accepted screen-level rejection dispositions.

This is exactly the right scope.

## 2. Prior AI and human records remain immutable

Original dispositions remain:

- AI: `uncertain_insufficient_evidence`;
- Human owner: `rejected_false_positive`.

Neither is overwritten.

The original effective disposition also remains:

`uncertain_insufficient_evidence`.

This preserves provenance and prevents retrospective rewriting.

## 3. The reconciliation evidence is now pair-specific

Unlike the generic human rationale imported in Document 119, this checkpoint records concrete observations tied to specific full-resolution frames.

The newly inspected fixed positions are:

- left: decode orders 0, 75, 150;
- right: decode orders 0, 60, 120.

The positions were chosen before viewing.

This materially improves the evidence quality relative to the generic human rationale.

## 4. The recorded rationale addresses the earlier ambiguity

The reconciliation proposal states that the enlarged frames show persistent differences in:

- foreground garment construction;
- inner-layer details;
- background grid/fixture configuration.

It also explicitly explains why the earlier low-detail panels could have appeared similar: coarse bulky-outerwear / ceiling composition.

This is the type of pair-specific explanation required by Review 120.

## 5. Proposed disposition is scientifically narrow

The proposal is:

`rejected_false_positive`.

Its stated scope is only:

> the observed perceptual-screen rendered-content relationship.

It does **not** claim:

- independent acquisition provenance;
- different identities;
- absence of every possible shared source;
- full-video content independence.

That narrow scope is correct.

## 6. Six frames are useful evidence, but not full-video proof

Only six of the 34 available full-resolution PNGs were newly inspected.

No full continuous-video visual review was performed.

No temporal alignment was established.

No transformed-region search or geometric registration was performed.

Therefore the proposal cannot support a broad statement that the two videos have no possible common source.

Document 121 correctly acknowledges this.

## 7. The proposal does not improperly override the disagreement

This is one of the strongest aspects of the checkpoint.

Even though the reconciliation proposal agrees with the human rejection, the public state remains:

- 9 effective rejected pairs;
- 1 effective uncertain pair.

`reconciliation_accepted = false`

and:

`batch01_accepted_reconciled_disposition_state = false`.

That is correct until an explicit acceptance record is made.

## 8. No new human review is fabricated

The reconciliation reviewer is disclosed as AI-assisted GitHub Copilot inspection.

The checkpoint does not call this:

- a second human review;
- independent adjudication;
- inter-rater validation.

This distinction is correct.

## 9. Evidence binding is adequate

The reconciliation record binds:

- Review 120;
- accepted visual-review report;
- accepted human-import report;
- handoff definition;
- Pair-5 packet;
- original AI pair record;
- original human pair record;
- owner JSON;
- relevant pair bundles;
- all six inspected image/RGB hashes;
- frozen artifacts.

This is sufficient provenance for a bounded reconciliation proposal.

## 10. Reproducibility is adequate for the record layer

The checkpoint writes two private bound files:

- `record.json`;
- `summary.json`.

Serialization replay is byte-identical.

Protected prior evidence remains unchanged.

This verifies record reproducibility, though not independent correctness of the visual judgment.

## 11. Local tests pass

Focused regression reports:

- **52/52 passed**;
- zero failures/errors.

No production code, test, policy, package or environment change was introduced.

The full 239-test suite was not rerun locally because this is a data/documentation checkpoint.

## 12. CI status at review time

At the time of this review, GitHub Actions run `38015159060` for exact commit

`ba2add2ffcd9a562f89fa5b2cdd141b207021e12`

is still reported as:

`in_progress`

with no conclusion yet.

Therefore this review does **not** claim fresh CI success.

Final checkpoint publication should retain acceptance only if that exact run finishes successfully; a CI failure would require inspection before progression.

## 13. What is still required to close Pair 5

The owner should explicitly accept or reject this reconciliation proposal as a separate bound decision.

If accepted:

- Pair 5 may move from effective `uncertain` to scoped `rejected_false_positive`;
- batch 01 would then become 10/10 reconciled screen-level rejections;
- only then may the frozen queue proceed to the remaining 75 highest-risk pairs.

If the owner finds the six-frame evidence insufficient:

- keep Pair 5 uncertain;
- inspect additional full-resolution frames or continuous temporal evidence;
- do not force a rejection simply to advance the queue.

## 14. No queue advancement is yet authorized

Document 121 correctly leaves:

- remaining 75 highest-risk pairs: not started;
- data-audit: blocked;
- source-dry-run: blocked;
- analysis-freeze: blocked;
- locked-evaluation: blocked;
- model execution unauthorized;
- scientific readiness false.

This should remain unchanged until Pair-5 reconciliation is explicitly accepted and recorded.

## Final disposition

**DOCUMENT 121 — ACCEPTED FOR ITS PROPOSAL SCOPE.**

**CHECKPOINT 1.5K PAIR-5 EVIDENCE-LINKED RECONCILIATION PROPOSAL — ACCEPTED WITHOUT METHOD REWORK.**

The proposal now contains the pair-specific, frame-linked rationale missing in Document 119.

However:

**Pair 5 remains effectively uncertain and batch 01 remains open until a separate explicit owner acceptance/reconciliation record is created.**

Fresh CI on the exact commit was still in progress at the time of review and must complete successfully before progression.
