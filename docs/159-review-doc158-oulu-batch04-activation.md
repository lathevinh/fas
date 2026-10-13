# 159 — Review of Document 158: OULU Batch-04 Additive Activation

Date: 2026-10-13  
Repository: `lathevinh/fas`  
Reviewed commit: `4a6215d5aaf575d80d434ca783e3e8f892974e62`  
Reviewed document: `docs/158-review-response-doc157-oulu-batch04-activation.md`

## Verdict

**DOCUMENT 158 — ACCEPTED.**

**CHECKPOINT 1.5AF OULU BATCH-04 ADDITIVE ACTIVATION — ACCEPTED WITHOUT REWORK.**

**BATCH 04 IS NOW CLOSED AT SCREEN LEVEL.**

Accepted batch-04 current outcome:

**10 `rejected_false_positive`, 0 uncertain, 0 confirmed same/derived.**

Accepted cumulative screen-level total:

**40 relationships.**

The next frozen queue batch beginning at rank 40 may now be prepared.

## 1. Activation scope is correct

Document 158 materializes exactly ten current ledger rows for ranks 30–39, with no skipped rank, no extra candidate and no ranks 40+.

The current materialized disposition set is:

`{"rejected_false_positive": 10}`.

This matches the authorization from Review 157.

## 2. AI/human agreement state is complete

All ten batch-04 relationships have an AI reject proposal, an original human reject answer, no disagreement, no confirmed same/derived content and no reconciliation requirement.

For ranks 38–39, activation additionally binds the accepted targeted scrutiny and pair-specific clarification chain.

This is sufficient for current-ledger activation.

## 3. Ranks 38–39 are correctly linked to semantic acceptance

The activation does not rely merely on the original generic human rationale.

Ranks 38–39 additionally bind targeted scrutiny, pair-specific clarification and Review 157 semantic acceptance.

This is important because Review 157, not the importer, resolved the heightened-scrutiny semantic blocker.

The historical semantic-pending flags remain unchanged, which is correct provenance behavior.

## 4. Historical human imports remain nonactivating

The activation correctly preserves the older import records with:

`effective_disposition_activated = false`.

The original human-import artifacts are therefore not rewritten to make activation appear retroactive.

The new activation ledger is additive.

## 5. Source JSONs remain immutable

All three owner/source JSON records remain unchanged.

No previous human answer, scrutiny answer or clarification answer is rewritten.

This preserves the evidentiary chain.

## 6. Current activation rows are separately materialized

The ten current rows set:

`effective_disposition_activated = true`.

This is appropriate for the newly materialized activation ledger.

At publication time they also retain:

- `activation_checkpoint_review_pending = true`;
- `counts_as_accepted_current_effective_disposition = false`.

This correctly distinguishes ledger materialization from review acceptance.

## 7. Review acceptance now resolves the pending checkpoint state

The artifact itself correctly remained review-pending before this review.

This Review 159 accepts checkpoint 1.5AF.

Therefore the ten batch-04 current rows are now accepted for scientific current-ledger counting.

Do not retroactively rewrite the Document-158 artifact to set historical pending fields to false.

The acceptance should exist as a new additive authority: this review.

## 8. Effective cumulative count is now 40

Before Review 159 acceptance:

- accepted current total = 30;
- prospective after checkpoint acceptance = 40.

After this review:

**40 screen-level rejection relationships are accepted current outcomes.**

The previous 30 from batches 01–03 remain unchanged.

## 9. Scope remains screen-level only

The accepted outcomes represent rejected perceptual-screen rendered-content candidate relationships.

They do not establish independent capture provenance, cleared videos, full-video independence, absence of all common source material, absence of arbitrary crop/shift/transform overlap or global OULU lineage clearance.

These limitations remain important.

## 10. Correlated foreground limitation remains

Some batch-04 candidates share or reuse related foreground configurations.

The accepted pair decisions may remain separate candidate records, but they must not be interpreted as ten statistically independent measurements of screening accuracy.

Activation does not remove that correlation limitation.

## 11. Sparse evidence limitation remains

The lineage decisions are based on the accepted bound sparse evidence rather than exhaustive visual inspection of all frames/full videos.

The activation is therefore valid only at the declared screen-level audit scope.

## 12. No new visual or human judgments are introduced

Document 158 creates no new visual review and no new human decision.

It only materializes the already authorized accepted dispositions.

This is correct for an activation checkpoint.

## 13. Reproducibility is strong

The private activation ledger contains activation authority, successful-CI observation, ten current pair rows and summary.

Total:

**13 files.**

Independent serialization replay reproduces:

**13 / 13 byte-identically.**

This demonstrates deterministic record materialization, not independent re-adjudication.

## 14. Bound evidence readback is complete

The checkpoint verifies:

**30 bound image hashes.**

Each current row binds AI proposal, original human record, frozen candidate/queue record, packet and three image hashes.

Ranks 38–39 additionally bind scrutiny and clarification records.

This is an adequate provenance chain.

## 15. Protected evidence remains unchanged

Document 158 reports 36 protected prior roots unchanged, all 13 frozen artifacts unchanged and all historical input/evidence records unchanged.

This is appropriate.

## 16. Overwrite protection is correct

An actual overwrite attempt raises `FileExistsError` and leaves all thirteen activation files unchanged.

This is consistent with the project’s immutable-record discipline.

## 17. Focused regression is sufficient

Focused regression reports:

**65/65 passed.**

The full regression suite was not locally rerun.

That is acceptable because Document 158 reports no changes to production code, tests, policy, environment or CI workflow.

The last accepted full baseline is:

**252/252 passed** at the accepted Document-156 checkpoint.

This is sufficient for a record-only activation checkpoint.

## 18. Exact prerequisite CI is correctly bound

The activation binds the exact accepted Document-156 CI:

Commit:

`1a83893b02a45b9b6498059bb29c8c6b32548cde`

Run:

`38345477284`

Validate job:

`115125781824`

with:

`completed / success`.

This is the correct prerequisite authority.

## 19. Fresh exact CI for Document 158 also passes

Fresh GitHub Actions for exact activation commit:

`4a6215d5aaf575d80d434ca783e3e8f892974e62`

Run:

`38347742466`

completed successfully.

Validate job:

`115132944411`

also completed successfully.

The exact job passes checkout/setup, FFmpeg installation, model-free screening dependencies, synthetic regression, canonical schema validation, unavailable-stage fail-closed checks and legacy-stage rejection checks.

There is no CI blocker on checkpoint 1.5AF.

## 20. Batch 04 is now formally closed

Accepted batch-04 result:

| Effective disposition | Count |
|---|---:|
| `rejected_false_positive` | 10 |
| `uncertain_insufficient_evidence` | 0 |
| `confirmed_same_content_or_derived_lineage` | 0 |

Batch 04 is therefore closed at the declared screen-level audit scope.

## 21. Current high-risk queue progress

Accepted screen-level resolved highest-risk candidates:

**40 / 85**

Remaining highest-risk candidates without AI visual review:

**45 / 85**

The next queue batch may begin at rank 40.

## 22. Ranks 40+ may now proceed

With this review acceptance, the project may prepare the next fixed queue batch beginning at rank 40.

The same prospective controls remain mandatory:

- fixed queue order;
- no outcome-dependent skipping;
- no threshold retuning;
- no role repair;
- no seed retry;
- no silent sample deletion;
- no selector change.

Any future confirmed same/derived cross-role case remains an immediate prospective scientific hard stop.

## 23. Do not retroactively patch historical state

Earlier artifacts correctly record their state at the time they were created.

In particular, do not rewrite:

- Document 156 semantic-pending flags;
- original human import activation=false fields;
- targeted scrutiny pending fields;
- clarification import pending-review fields;
- Document 158 review-pending publication fields.

Review 159 supplies the additive acceptance authority.

This preserves an auditable state-transition history.

## 24. OULU lineage audit remains incomplete

Acceptance of batch 04 does not mean OULU is globally cleared.

There are still 45 highest-risk candidates without AI visual review, broader cross-role candidate relationships, the wider unresolved non-exact population and eventual cross-dataset lineage checks.

`content_lineage_adjudication_complete = false` remains correct.

## 25. Scientific/model gates remain blocked

This checkpoint does not authorize OULU data-audit completion, source-dry-run, analysis freeze, locked target evaluation, detector/classifier/risk-model execution, target-domain evaluation, global lineage clearance or scientific readiness.

These stages remain fail-closed.

## Final disposition

**DOCUMENT 158 — ACCEPTED.**

**CHECKPOINT 1.5AF OULU BATCH-04 ADDITIVE ACTIVATION — ACCEPTED WITHOUT REWORK.**

Batch 04 is now formally closed at screen level:

**10 rejected, 0 uncertain, 0 confirmed same/derived.**

Across batches 01–04, the accepted current total is now:

**40 screen-level rejections.**

Current high-risk progress:

**40 / 85 resolved, 45 / 85 not yet AI visually reviewed.**

**The next fixed queue batch beginning at rank 40 may now be prepared.**

This acceptance does not imply global lineage clearance, capture-provenance certification, data-audit completion or authorization to execute the research models.
