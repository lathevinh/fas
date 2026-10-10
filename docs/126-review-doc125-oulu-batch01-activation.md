# 126 — Review of Document 125: OULU Batch-01 Additive Activation

Date: 2026-10-10  
Repository: `lathevinh/fas`  
Reviewed commit: `5f3c22c4a473770b5653a4439bf350379fc5032f`  
Reviewed document: `docs/125-review-response-doc124-oulu-batch01-activation.md`

## Verdict

**DOCUMENT 125 — ACCEPTED.**

**CHECKPOINT 1.5M OULU BATCH-01 ADDITIVE ACTIVATION — ACCEPTED WITHOUT REWORK.**

**BATCH 01 IS NOW CLOSED AT SCREEN LEVEL: 10 REJECTED, 0 UNCERTAIN, 0 CONFIRMED SAME/DERIVED.**

This checkpoint correctly completes the provenance chain requested by Review 124. It creates a new current effective ledger instead of retroactively editing the historical AI/human/import/reconciliation records.

The next frozen queue batch may now start, but no broader OULU data-audit or model stage is unlocked by this acceptance.

## 1. Additive activation is the correct provenance model

Document 125 does not rewrite the historical effective ledger.

It creates a separate current effective ledger of ten rows.

Historical state remains preserved, including:

- the original Pair-5 AI uncertainty;
- the owner-human rejection;
- the original disagreement flag;
- the prior pending-CI snapshot.

This is exactly the right design.

## 2. Batch-01 current effective state is now complete

Current effective dispositions are:

| Disposition | Count |
|---|---:|
| `rejected_false_positive` | 10 |
| `uncertain_insufficient_evidence` | 0 |
| `confirmed_same_content_or_derived_lineage` | 0 |

Therefore:

`batch01_accepted_reconciled_disposition_state = true`

is justified.

## 3. Pair 5 activation authority is valid

The Pair-5 row derives from:

- the original human rejection;
- the separate evidence-linked reconciliation proposal;
- explicit owner acceptance;
- successful exact prerequisite CI.

No additional owner review or replacement ten-item JSON is needed.

## 4. Exact CI prerequisites are correctly bound

Document 125 binds both exact successful CI runs:

- proposal commit `ba2add2ffcd9a562f89fa5b2cdd141b207021e12`, run `38015159060`: completed / success;
- owner-acceptance commit `6e05787d4b939a29094192d904be20c967304c7c`, run `38015828271`: completed / success.

These are the exact runs required by the prior reviews.

## 5. Fresh CI for Document 125 also passes

Fresh GitHub Actions for exact activation commit:

`5f3c22c4a473770b5653a4439bf350379fc5032f`

completed successfully.

Thus the activation checkpoint itself is also backed by a green pushed commit.

## 6. Historical disagreement remains preserved

The current ledger marks Pair 5 reconciled, but the historical disagreement is still retained.

That distinction matters.

Current reconciliation does not rewrite history into a false claim that AI and human agreed from the start.

## 7. Scope remains appropriately narrow

The ten rows are closed only for:

> the observed perceptual-screen rendered-content relationship.

This does not prove:

- independent original capture;
- absence of all possible shared source material;
- full-video independence;
- global OULU content-lineage clearance.

Document 125 correctly maintains that boundary.

## 8. No sample or frozen role is changed

The checkpoint does not:

- delete videos;
- reassign roles;
- retry the split seed;
- change the selector;
- change screening thresholds;
- alter the canonical population.

All 13 frozen artifacts remain unchanged.

This is correct.

## 9. Reproducibility evidence is adequate

The activation export contains:

- `activation.json`;
- successful-CI observations;
- ten pair rows;
- `summary.json`.

Total: 13 files.

Serialization replay is byte-identical.

Existing output is refused.

This is appropriate immutable activation behavior.

## 10. Tests are adequate

Focused regression:

- 52/52 passed;
- zero failures/errors.

No production code, policy, test or environment change occurred.

The full local regression was not rerun, but the exact pushed activation commit has successful CI.

That is adequate for this data/provenance-only checkpoint.

## 11. The next 75 pairs were correctly not started early

At publication:

- `queue_continued = false`;
- `highest_risk_pairs_not_yet_started = 75`.

This is important.

The project correctly waited for activation review before advancing the frozen queue.

## 12. Queue progression is now permitted

With this review acceptance, the project may proceed to the remaining 75 pairs in the highest-risk cross-role + conflicting-label population.

Requirements for that next work:

- preserve frozen queue order;
- no outcome-dependent skipping;
- no threshold retuning;
- preserve prior batch-01 records;
- no automatic sample deletion or role repair;
- confirmed same/derived cross-role content still triggers an explicit prospective scientific decision stop.

## 13. Batch-01 closure does not close OULU lineage review

Even after this activation, the following remain:

- 75 highest-risk pairs in the first priority population;
- 399 other cross-role candidates;
- additional cross-partition/conflicting-label candidates;
- remaining non-exact candidates as required for closure.

Therefore:

`content_lineage_adjudication_complete = false`

remains correct.

## 14. Scientific gates remain blocked

This checkpoint does not authorize:

- data-audit completion;
- source-dry-run;
- analysis-freeze;
- locked target evaluation;
- model execution.

Those gates must remain blocked until the broader data-integrity requirements are complete.

## Final disposition

**DOCUMENT 125 — ACCEPTED.**

**CHECKPOINT 1.5M OULU BATCH-01 ADDITIVE ACTIVATION — ACCEPTED WITHOUT REWORK.**

Batch 01 is now formally closed at the intended screen-level scope:

**10 rejected, 0 uncertain, 0 confirmed same/derived.**

The project may now continue the frozen queue with the remaining 75 highest-risk pairs.

This acceptance does not imply global OULU content-lineage clearance or scientific readiness.
