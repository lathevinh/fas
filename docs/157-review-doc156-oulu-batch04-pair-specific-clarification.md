# 157 — Review of Document 156: OULU Batch-04 Pair-Specific Clarification Import

Date: 2026-10-13  
Repository: `lathevinh/fas`  
Reviewed commit: `1a83893b02a45b9b6498059bb29c8c6b32548cde`  
Reviewed document: `docs/156-oulu-batch04-pair-specific-clarification-import.md`

## Verdict

**DOCUMENT 156 — ACCEPTED.**

**CHECKPOINT 1.5AE OULU BATCH-04 PAIR-SPECIFIC CLARIFICATION IMPORT — ACCEPTED WITHOUT REWORK.**

**HEIGHTENED-SCRUTINY RESOLUTION FOR RANKS 38–39 — ACCEPTED.**

**BATCH-04 IS NOW ELIGIBLE FOR A SEPARATE ADDITIVE ACTIVATION CHECKPOINT.**

Document 156 correctly imports genuine pair-specific human clarification for ranks 38–39, preserves prior evidence and source JSONs, performs no effective activation, and leaves semantic acceptance to this review checkpoint.

The pair-specific clarification now resolves the semantic deficiency identified in Review 154.

## 1. Clarification scope is correct

The checkpoint addresses only ranks 38 and 39. It does not reopen ranks 30–37 and does not replace the original ten-pair human review or the prior targeted scrutiny record.

## 2. Clarification result

| Item | Result |
|---|---:|
| Targeted ranks | 38, 39 |
| Human clarifications | 2 |
| Human `rejected_false_positive` | 2 |
| AI/human agreements | 2 |
| Disagreements | 0 |
| Confirmed same/derived | 0 |
| Effective activations | 0 |

No prospective scientific hard stop is triggered.

## 3. The previous semantic deficiency is resolved

Review 154 rejected the prior semantic resolution because the earlier scrutiny answers reused identical structure descriptions, reused identical rationales, and relied primarily on background differences.

Document 156 now reports:

- `unique_left_foreground_count = 2`;
- `unique_right_foreground_count = 2`;
- `unique_haze_limitation_count = 2`;
- `unique_human_rationale_count = 2`.

The new human clarification is therefore genuinely pair-specific at the record level.

## 4. Foreground reasoning is now aligned with the required criterion

The clarification explicitly supplies visible left-side foreground structure, visible right-side foreground structure, haze/veil limitation, persistent foreground comparison, and pair-specific disposition rationale.

This is materially stronger than the previous background-only response. The relevant scientific criterion is persistent rendered foreground structure, including stripe pattern, garment construction, hood/collar geometry, zipper/placket, layering, quilting and shoulder/torso outline.

## 5. Evidence supplied during review supports the clarification

The bound views supplied during review show clear foreground divergence, including a red-and-black horizontally striped garment on one side, dark outerwear/jacket construction on the other, different collar/layering structure, and no corresponding stripe pattern on the dark-outwear side. Haze reduces fine texture but leaves major garment structure visible.

These differences are structural rather than mere exposure/color changes.

## 6. Haze/veil limitation remains properly bounded

Haze/veil still reduces fine texture and local torso detail. The accepted conclusion is limited to visible rendered-content structure in the bound evidence.

It does not establish capture independence, full-video independence, absence of all shared source material, absence of crop/shift/transform relationships outside the inspected evidence, or global OULU lineage clearance.

## 7. No facial-identity reasoning is required or accepted

The disposition is based on foreground garment/rendered-content structure, not an identity claim about the people shown.

## 8. Importer design is correct

The clarification importer requires the separate `human_pair_specific_clarification` record and validates exact ranks 38–39, reviewer/personal-review attestation, UTC, historical scrutiny-row references, packet and asset hashes, foreground fields, haze limitation, rationale, sufficiency/disposition consistency and scientific-stop consistency.

It reuses the existing pure validator in memory only and does not rerun historical importers.

## 9. Temporary validation fields do not contaminate evidence

Document 156 records `temporary_validation_fields_not_persisted = true`. Temporary compatibility mappings exist only in memory; outputs restore original supplied human fields and only add derived nonactivation/comparison annotations.

## 10. All historical evidence remains immutable

Document 156 reports that all three human source JSONs, prior human answers, prior AI records, packet/current/historical evidence and frozen artifacts remain unchanged.

## 11. Reproducibility is strong

Each clarification import produces five immutable files. Independent import reproduces **5/5 byte-identically**. Existing-output reuse is refused.

## 12. Protected evidence remains unchanged

The checkpoint reports 34 protected prior roots unchanged, all 13 frozen artifacts unchanged, and no new image extraction, media decode or model execution.

## 13. Regression evidence is strong

- focused regression: **65/65 passed**;
- full regression: **252/252 passed**;
- zero failures/errors/diagnostics.

## 14. Fresh exact CI for Document 156 passes

Exact reviewed commit:

`1a83893b02a45b9b6498059bb29c8c6b32548cde`

Fresh GitHub Actions:

- run `38345477284`;
- status/conclusion: `completed / success`;
- validate job `115125781824` completed successfully.

Synthetic regression, canonical schema validation and fail-closed checks pass.

## 15. Semantic acceptance is a review decision, not an importer decision

The public aggregate correctly retains `heightened_scrutiny_pair_specific_reasoning_verified = false`, `semantic_review_required = true`, and `eligible_for_additive_activation_without_further_review = false` because the importer must not self-certify scientific adequacy.

This review now provides the semantic acceptance. Historical import records should remain unchanged rather than patched retroactively.

## 16. Ranks 38–39 are now eligible for activation

Based on the pair-specific clarification and review evidence, the heightened-scrutiny blocker for ranks 38–39 is resolved. The two dispositions remain `rejected_false_positive` and are now eligible for later current-ledger activation.

## 17. Entire batch 04 is now activation-eligible

Batch 04 now has 10 AI reject proposals, 10 original human reject answers, 2 targeted scrutiny answers, 2 pair-specific clarifications, 0 disagreements, 0 confirmed same/derived, and accepted semantic scrutiny for ranks 38–39.

Expected activation state:

| Effective disposition | Expected count |
|---|---:|
| `rejected_false_positive` | 10 |
| `uncertain_insufficient_evidence` | 0 |
| `confirmed_same_content_or_derived_lineage` | 0 |

## 18. Document 156 itself must remain non-activating

The current public state correctly still reports `effective_dispositions_activated = 0` because Document 156 is an import/review checkpoint, not the current-ledger activation checkpoint.

Do not rewrite Document 156 or historical imported rows to simulate activation.

## 19. Required next step: separate additive batch-04 activation

The next checkpoint should create a separate immutable current ledger for ranks 30–39 and bind the accepted batch-04 AI proposal ledger, original human import, targeted scrutiny import, pair-specific clarification import, this Review 157 semantic acceptance, exact successful Document-156 CI, and packet/candidate evidence bindings.

It should activate exactly ten screen-level rejection dispositions.

## 20. Ranks 40+ remain paused until activation review

The correct sequence is:

1. accept Document 156 and Review 157;
2. create separate batch-04 additive activation;
3. publish and review that activation;
4. only then prepare the next frozen queue batch beginning at rank 40.

## 21. Effective count remains 30 until activation

Before the separate activation checkpoint is accepted, the current effective total remains **30 accepted screen-level relationships**.

After valid batch-04 activation is accepted, the expected total becomes **40 accepted screen-level rejections**.

## 22. Scientific/model gates remain blocked

This checkpoint does not authorize OULU data-audit completion, source-dry-run, analysis freeze, locked target evaluation, classifier/risk-model execution, target-domain evaluation, global lineage clearance or scientific readiness.

## Final disposition

**DOCUMENT 156 — ACCEPTED.**

**CHECKPOINT 1.5AE — ACCEPTED WITHOUT REWORK.**

**HEIGHTENED-SCRUTINY RESOLUTION FOR RANKS 38–39 — ACCEPTED.**

The new clarification supplies pair-specific foreground structure, haze limitations and distinct human rationales, resolving the semantic deficiency identified in Review 154.

**BATCH 04 IS NOW ELIGIBLE FOR SEPARATE ADDITIVE ACTIVATION OF 10 SCREEN-LEVEL REJECTIONS.**

Do not count those ten as effective yet. Create and review the additive activation checkpoint first, then continue to ranks 40+.
