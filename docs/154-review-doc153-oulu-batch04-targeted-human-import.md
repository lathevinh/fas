# 154 — Review of Document 153: OULU Batch-04 Targeted Human Scrutiny Import

Date: 2026-10-13  
Repository: `lathevinh/fas`  
Reviewed commit: `ea1d1d5f9865b272530ef300f6632ddbac2f6241`  
Reviewed document: `docs/153-oulu-batch04-targeted-human-import.md`

## Verdict

**DOCUMENT 153 — ACCEPTED FOR TARGETED-IMPORT SCOPE.**

**CHECKPOINT 1.5AC TARGETED HUMAN SCRUTINY IMPORT — ACCEPTED WITHOUT IMPORT REWORK.**

**HEIGHTENED-SCRUTINY SEMANTIC RESOLUTION — NOT ACCEPTED.**

**BATCH-04 ADDITIVE ACTIVATION — NOT AUTHORIZED.**

Document 153 correctly imports the genuine additive human scrutiny answers for ranks 38–39, preserves all historical evidence, performs no effective activation, and maintains fail-closed state.

However, the imported human scrutiny text still does not satisfy the pair-specific semantic requirement established by Review 151.

## 1. Targeted import scope is correct

The checkpoint imports only ranks 38 and 39. It does not reopen ranks 30–37 and does not replace the original ten-pair human JSON.

## 2. Human scrutiny results

| Item | Result |
|---|---:|
| Targeted ranks | 38, 39 |
| Human rejects | 2 |
| AI/human agreements | 2 |
| Disagreements | 0 |
| Confirmed same/derived | 0 |
| Effective activations | 0 |

No prospective scientific hard stop is currently triggered.

## 3. Import/provenance are acceptable

The targeted importer validates exact original ranks, genuine human record type, reviewer identity, personal inspection attestation, UTC timestamp, original human-row hashes, packet hashes, reviewed-asset hashes, nonblank visible-structure/rationale fields, sufficiency/disposition consistency, capture-provenance noncertification, and confirmed-content stop consistency.

It correctly preserves history and sets `effective_disposition_activated = false`.

## 4. Original inputs remain immutable

The original ten-pair human JSON, prior imported answers, AI/packet/current evidence, frozen artifacts and source targeted JSON remain unchanged.

## 5. Reproducibility is strong

The targeted import produces five immutable files and independent reimport reproduces **5/5 byte-identically**. Existing-output reuse is refused.

This demonstrates deterministic import processing, not independent adjudication accuracy.

## 6. Semantic scrutiny remains unresolved

The public state records:

- `unique_visible_structure_count = 1`;
- `unique_human_rationale_count = 1`;
- `heightened_scrutiny_pair_specific_reasoning_verified = false`;
- `review148_haze_scrutiny_resolution_pending = true`;
- `eligible_for_additive_activation_without_further_review = false`.

These flags are correct.

The two structure descriptions are identical and the two rationales are identical. Therefore the targeted review still does not provide genuinely pair-specific reasoning.

## 7. Background difference alone is insufficient

A brief background-difference statement is not enough to exclude a same/derived-content relationship.

A derived, cropped, transformed or replayed sequence may have different visible background.

The human reasoning should instead identify persistent rendered foreground structure such as hood geometry, collar/neckline, zipper/placket, quilting, garment layering, printed patterns, shoulder/torso construction, and persistent differences across temporal panels and trigger.

Background differences may be supporting evidence, but should not be the sole basis.

## 8. `visible_rendered_structure` must describe actual structure

A response such as `Yes` does not satisfy the intended semantic requirement.

The field should describe what remains visible, for example:

`The hood outline, center zipper, collar geometry and shoulder contour remain visible despite haze.`

Ranks 38 and 39 should have their own pair-specific observations.

## 9. The importer correctly does not certify semantics

The importer deliberately records `pair_specific_reasoning_semantically_verified = false`.

This is correct. Software should validate bindings and consistency, not pretend that nonblank human text is scientifically adequate.

## 10. No whole-batch repeat is required

Ranks 30–37 should remain untouched. The original ten-pair input should remain immutable.

The remaining remediation is limited to ranks 38–39.

## 11. Required next step: additive pair-specific clarification

Create a separate immutable clarification record for rank 38 and rank 39.

For each pair, the human reviewer should explicitly provide:

1. the concrete visible rendered/foreground structure that remains despite haze/veil;
2. whether that remaining evidence is sufficient;
3. pair-specific reasoning explaining the structural divergence and the limitation introduced by haze/veil.

The existing imported rows and targeted JSON must not be rewritten.

## 12. Conservative decision rule

For each rank:

- clear persistent structural divergence remains visible → rejection may be reaffirmed;
- evidence is too obscured → `uncertain_insufficient_evidence`;
- same/derived rendered content becomes apparent → immediate scientific hard stop.

No answer should be forced merely to agree with the earlier AI proposal.

## 13. AI must not author missing human reasoning

The missing pair-specific reasoning must come from the human reviewer. AI may preserve and bind the clarification record, but must not manufacture the owner's justification.

## 14. Regression evidence

Document 153 reports:

- focused regression: **63/63 passed**;
- full regression: **250/250 passed**;
- zero failures/errors.

## 15. Fresh exact CI passes

Exact commit:

`ea1d1d5f9865b272530ef300f6632ddbac2f6241`

Fresh GitHub Actions:

- run `38341972399`;
- validate job `115114774603`;
- status/conclusion: `completed / success`.

Synthetic regression, canonical schema validation and fail-closed checks pass.

## 16. Batch 04 remains open

Current effective state remains:

- prior accepted screen-level relationships: 30;
- batch-04 AI proposals: 10;
- original batch-04 human answers: 10;
- targeted scrutiny answers: 2;
- batch-04 effective activations: 0.

The project must not report 40 accepted screen-level relationships yet.

## 17. Ranks 40+ remain blocked

Required order:

1. accept Document 153 for targeted-import scope;
2. obtain pair-specific additive clarification for ranks 38–39;
3. review that clarification;
4. perform any necessary reconciliation;
5. create separate additive activation for eligible batch-04 outcomes;
6. review that activation;
7. only then continue to ranks 40+.

## 18. Scientific/model gates remain blocked

This checkpoint does not authorize OULU audit completion, source-dry-run, analysis freeze, locked target evaluation, research-model execution, target-domain evaluation or scientific readiness.

## Final disposition

**DOCUMENT 153 — ACCEPTED FOR TARGETED-IMPORT SCOPE.**

**CHECKPOINT 1.5AC — ACCEPTED WITHOUT IMPORT REWORK.**

But:

**HEIGHTENED-SCRUTINY SEMANTIC RESOLUTION FOR RANKS 38–39 — NOT ACCEPTED.**

The imported two-pair human input is genuine and correctly bound, but the identical visible-structure text and identical background-oriented rationale do not satisfy the pair-specific semantic requirement from Review 151.

**BATCH-04 ADDITIVE ACTIVATION REMAINS BLOCKED.**

The next step is a narrow additive clarification for ranks 38–39 only, with concrete pair-specific foreground/rendered-structure reasoning. Do not reopen ranks 30–37 and do not begin ranks 40+ yet.
