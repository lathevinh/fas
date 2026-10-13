# 151 — Review of Document 150: OULU Batch-04 Genuine Human-Review Import

Date: 2026-10-13  
Repository: `lathevinh/fas`  
Reviewed commit: `1532e801038e3d47ec97dc154d894162dc534f70`  
Reviewed document: `docs/150-oulu-batch04-human-review-import.md`

## Verdict

**DOCUMENT 150 — ACCEPTED FOR HUMAN-IMPORT SCOPE.**

**CHECKPOINT 1.5AA OULU BATCH-04 GENUINE HUMAN-REVIEW IMPORT — ACCEPTED WITHOUT IMPORT REWORK.**

**BATCH-04 ADDITIVE ACTIVATION — NOT AUTHORIZED YET.**

The import itself is correct, reproducible and fail-closed. However, the heightened-scrutiny requirement established by Review 148 for ranks 38–39 remains unresolved because all ten human rationale strings are identical and do not provide pair-specific reasoning for those haze/veil cases.

The required next step is a **targeted scrutiny-resolution checkpoint for ranks 38–39 only**, not a repeat review of the entire batch.

## 1. Genuine owner-human input exists and is correctly imported

The imported owner JSON contains ten explicit answers for original queue ranks 30–39, owner-human reviewer declaration, global/per-pair personal-review attestations, timestamped submission, and binding to the accepted handoff definition, packet and image assets.

The genuine-input blocker is therefore resolved.

## 2. Human result

| Outcome | Count |
|---|---:|
| Human `rejected_false_positive` | 10 |
| AI/human agreements | 10 |
| AI/human disagreements | 0 |
| Human confirmed same/derived | 0 |
| Scientific hard stop | 0 |
| Effective activations | 0 |

The human answers agree with all ten AI proposals. However, agreement alone is not sufficient to close the batch because Review 148 imposed a separate evidence-quality requirement for ranks 38–39.

## 3. Comparison state is correctly not activated

The public state correctly remains:

- `effective_dispositions_activated = 0`;
- `batch04_accepted_reconciled_disposition_state = false`;
- `comparison_state_is_not_current_effective_activation = true`.

The validator's `effective_disposition` remains only a comparison/reconciliation output and is not silently promoted to the current scientific ledger.

## 4. Rank 30–39 adapter is appropriate

The importer requires exact definition ranks 30–39, exactly ten human rows, integer ranks only, and exact unique rank set 30–39.

It maps ranks in memory from 30–39 to 0–9 for the pinned validator, then restores the original ranks. The source human record and definition are not mutated.

## 5. Human input is preserved rather than repaired by AI

The importer preserves original dispositions, rationale strings, attestations, packet/asset bindings and raw source bytes. It does not rewrite weak human rationale using AI observations.

This is the correct provenance boundary.

## 6. Central limitation: one rationale text across all ten

The public aggregate reports `unique_human_rationale_count = 1`.

That is acceptable for establishing the presence of genuine nonblank human input, but it does not establish pair-specific assessment.

For ranks 38–39 this is blocking, because Review 148 explicitly required heightened scrutiny and pair-specific reasoning due to haze/veil limiting torso detail.

## 7. Review-148 scrutiny requirement remains unresolved

The correct public state is:

- `heightened_scrutiny_ranks = [38, 39]`;
- `heightened_scrutiny_pair_specific_reasoning_verified = false`;
- `review148_haze_scrutiny_resolution_pending = true`;
- `eligible_for_additive_activation_without_further_review = false`.

I agree with all four flags.

Human agreement with the AI result does not itself satisfy the requirement to explain what visible evidence remains sufficient despite haze/veil.

## 8. Do not relabel the original human answers

The human answers should remain recorded as `rejected_false_positive`.

The unresolved issue is not necessarily that the disposition is wrong; it is that the required supporting reasoning is missing.

A later targeted checkpoint may reaffirm the rejection with adequate reasoning or conservatively resolve the pair to uncertain.

## 9. No full repeat review is required

There is no reason to discard or repeat valid human input for ranks 30–37.

Do not replace the original ten-pair JSON, rewrite the original human record, or rerun the entire batch.

The unresolved requirement is limited to ranks 38–39.

## 10. Required remediation is targeted and additive

Create a separate immutable scrutiny-resolution record for ranks 38 and 39.

For each pair, the human reviewer should explicitly state:

1. what rendered-content structure remains visible despite haze/veil;
2. whether that remaining evidence is sufficient to support `rejected_false_positive`;
3. or whether evidence is insufficient, in which case the conservative outcome should be `uncertain_insufficient_evidence`.

The resolution should reference the existing bound assets and imported human rows rather than modifying them.

## 11. AI must not synthesize the missing human reasoning

AI must not manufacture pair-specific human justification after the fact.

If the resolution is intended to satisfy the human heightened-scrutiny requirement, it must be supplied by the human reviewer. AI may preserve and bind that record, but not author it on the reviewer's behalf.

## 12. Conservative resolution rules

For ranks 38–39:

- human reaffirms reject with specific sufficient evidence -> eligible for later activation;
- human determines evidence insufficient -> effective state should remain uncertain pending any allowed reconciliation;
- human identifies same/derived content -> immediate scientific hard stop.

No queue continuation should occur while this requirement remains unresolved.

## 13. Import provenance is strong

The importer verifies the published handoff report, review definition, page, private summary, preparation code, pinned human validator, page source, exact successful handoff CI, scoped owner authorization, protected snapshots, accepted AI ledger/report/definition/summary, packet hashes, required asset hashes, and original owner-input digest.

This is a strong fail-closed import boundary.

## 14. Original owner JSON is preserved correctly

The original owner JSON SHA-256 is:

`196ddd68ee2c51385f23de5b1c1d26b253ba8b9ec1f976f4d84ef62c10d42ab6`.

The source bytes are preserved. The canonical imported input is only claimed to have equivalent parsed content, not identical raw serialization.

That distinction is correct.

## 15. Independent import replay is reproducible

Each import output contains lineage, canonical human input, ten pair outcomes and summary: 13 files total.

Independent reimport reproduces **13/13 byte-identically**. Existing-output reuse is refused.

This demonstrates deterministic import processing, not independent human adjudication.

## 16. Protected evidence remains unchanged

Document 150 reports 26 protected roots unchanged, all 13 frozen artifacts unchanged, and accepted AI/current/historical evidence unchanged.

This is appropriate provenance preservation.

## 17. Regression evidence is strong

Reported testing:

- focused regression: **61/61 passed**;
- full regression: **248/248 passed**;
- zero failures/errors.

The increased test count is appropriate because the batch-04 importer and scrutiny-related tests were added.

## 18. Fresh exact CI passes

Fresh GitHub Actions for exact commit:

`1532e801038e3d47ec97dc154d894162dc534f70`

completed successfully.

Run:

`38337553237`

Validate job:

`115100971471`

completed successfully.

Synthetic regression, schema validation and fail-closed checks all pass.

There is no CI blocker on the import checkpoint itself.

## 19. Batch 04 is not closed

Current effective state remains:

- prior accepted screen-level relationships: 30;
- batch-04 AI proposals: 10;
- batch-04 imported human answers: 10;
- batch-04 effective activations: 0.

The project must not report 40 accepted screen-level relationships yet.

## 20. Ranks 40+ remain blocked

Required order:

1. accept Document 150 for import scope;
2. resolve heightened scrutiny for ranks 38–39 in a separate immutable human-backed record;
3. review that resolution;
4. perform any necessary reconciliation;
5. create separate additive activation for eligible batch-04 outcomes;
6. review that activation;
7. only then continue to ranks 40+.

## 21. Scientific/model gates remain blocked

This checkpoint does not authorize OULU data-audit completion, source-dry-run, analysis freeze, locked target evaluation, research-model execution, target-domain evaluation or scientific readiness.

## Final disposition

**DOCUMENT 150 — ACCEPTED FOR HUMAN-IMPORT SCOPE.**

**CHECKPOINT 1.5AA — ACCEPTED WITHOUT IMPORT REWORK.**

Imported result:

**10 human rejects, 10 AI-human agreements, 0 disagreements, 0 confirmed same/derived, 0 effective activations.**

However:

**RANKS 38–39 HEIGHTENED-SCRUTINY REQUIREMENT REMAINS UNRESOLVED.**

Therefore:

**BATCH-04 ADDITIVE ACTIVATION IS NOT YET AUTHORIZED.**

The next required step is a **targeted, additive human scrutiny-resolution checkpoint for ranks 38–39 only**. The original imported JSON and ranks 30–37 should remain untouched.
