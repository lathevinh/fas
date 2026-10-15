# 174 — Review of Document 173: OULU Batch-05 Separate Additive Activation

Date: 2026-10-15  
Repository: `lathevinh/fas`  
Reviewed commit: `226943f77710a938b54581ccb03381e69c0d7fba`  
Reviewed document: `docs/173-review-response-doc172-oulu-batch05-activation.md`  
Reviewed aggregate: `results/phase1/oulu-batch05-activation-v1.json`

## Verdict

**DOCUMENT 173 — ACCEPTED WITHOUT REWORK.**

**BATCH-05 SEPARATE ADDITIVE ACTIVATION — ACCEPTED.**

**BATCH-05 SCREEN-LEVEL REVIEW IS NOW CLOSED.**

**ACCEPTED CURRENT SCREEN-LEVEL TOTAL ADVANCES ADDITIVELY FROM 40 TO 50.**

**PREPARATION OF THE NEXT FROZEN QUEUE BLOCK, RANKS 50+, IS NOW AUTHORIZED.**

This acceptance applies only to the declared perceptual-screen content-lineage adjudication scope. It does not certify capture independence, global lineage independence, full-video shared-source absence, cross-dataset independence, or scientific readiness for model execution.

## 1. Scope is exact

Document173 materializes exactly original queue ranks:

`40,41,42,43,44,45,46,47,48,49`.

The resulting activation set is:

- `rejected_false_positive`: 10;
- uncertain: 0;
- confirmed same/derived: 0.

No rank50+ is included in this ledger.

## 2. Six remediated ranks are correctly bound to accepted categorical decisions

Ranks:

`40,41,42,43,48,49`

bind their accepted Document171 categorical records.

These are the six ranks whose semantic blockers were explicitly cleared by Review172.

No new human judgment is manufactured at activation time.

## 3. Clean ranks 44–47 are correctly not reopened

Ranks:

`44,45,46,47`

reuse their accepted prior human dispositions.

There is no new categorical record for these clean ranks and no requirement for repeated owner review.

This is consistent with Review172.

## 4. Ten materialized effective dispositions are appropriate

All ten activation rows set:

`effective_disposition_activated = true`

in the new activation ledger only.

The historical nonactivation/pending records remain unchanged.

This is the correct additive-history model.

## 5. Review-pending activation state was correctly preserved before this review

Before Review174 acceptance, the new rows correctly retained:

- `activation_checkpoint_review_pending = true`;
- `counts_as_accepted_current_effective_disposition = false`;
- accepted current total = 40;
- prospective total = 50.

This prevented the project from counting the activation before formal review.

## 6. Review174 supplies the additive acceptance authority

With this review, the ten batch-05 materialized dispositions may now be treated as accepted current effective screen-level dispositions.

The accepted current screen-level total therefore becomes:

**50.**

The prior pending fields should not be retroactively edited merely to erase history.

Review174 is the additive authority that changes current interpretation.

## 7. Batch-05 screen-level state is now closed

After Review174:

- batch05 accepted dispositions: 10 reject;
- uncertain: 0;
- confirmed same/derived: 0;
- scientific hard stop: false;
- accepted current total: 50.

Therefore the batch05 screen-level adjudication checkpoint is closed.

## 8. No scientific hard stop is triggered

Document173 reports:

- disagreements with AI: 0;
- changes from prior human: 0;
- confirmed same/derived: 0;
- scientific hard stop: false.

This is consistent with the accepted semantic state from Review172.

## 9. Evidence binding is strong

The activation ledger binds:

- Review172;
- Document171 aggregate;
- Document171 imported rows;
- exact successful Document171 CI;
- original human inputs;
- categorical definition/governance;
- queue/AI/packet records;
- 30 existing image hashes.

This is sufficient provenance for activation of the already-adjudicated screen-level dispositions.

## 10. Thirty hash bindings do not imply thirty independent samples

The aggregate correctly states that the 30 image-hash bindings do not imply 30 independent images or captures.

This matters because some evidence is correlated and rank48 is byte-identical to rank47 at the image level.

No independence claim should be made from this count.

## 11. Rank48 remains properly distinguished as a separate candidate

Although rank48 is image-identical to rank47, it retains its own accepted categorical decision and its own activation row.

This is correct because queue candidates are distinct records even when bound evidence coincides.

## 12. Serialization replay is deterministic

The private activation ledger contains 13 files and the independent replay matches:

**13/13 byte-identically.**

This verifies deterministic serialization only.

It is not a second adjudication and should not be described as one.

## 13. Protected history remains intact

Document173 reports:

- 52 protected prior roots unchanged;
- frozen 13 unchanged;
- study configs 17 unchanged;
- owner source JSONs unchanged;
- original ten human rows unchanged;
- categorical supplied fields unchanged;
- old167 input not converted;
- historical semantic-pending flags unchanged.

This is the correct preservation discipline.

## 14. No code/test/policy/environment change occurred

Document173 explicitly reports no production code, test, policy, environment, CI-workflow, role, selector, seed, or screening change.

This is important when judging the regression evidence.

## 15. Focused regression is sufficient for this activation-only checkpoint

Focused regression reports:

**71/71 passed.**

The full suite was not rerun locally.

That is acceptable because Document173 is an activation-record checkpoint with no production code/test/policy changes.

The accepted full baseline remains:

**258/258 passed**

from Document171.

No rework is required merely to repeat the same full suite.

## 16. Fresh exact publication CI passes

Exact reviewed commit:

`226943f77710a938b54581ccb03381e69c0d7fba`

Fresh GitHub Actions run:

`38666749697`

completed with:

`success`.

Validate job:

`116200334607`

also completed with:

`success`.

The job passes checkout, Python setup, FFmpeg setup, model-free screening dependencies, synthetic regression, schema validation, fail-closed unavailable-stage checks, and legacy-stage rejection checks.

There is no publication-CI blocker.

## 17. No additional owner input is needed

Document173 correctly requires no further:

- human review;
- typed prose;
- replacement JSON;
- repeat inspection;
- reconciliation.

Review174 agrees.

Do not ask the owner to re-review ranks40..49.

## 18. Next queue block is now authorized

Because batch05 activation is now accepted, the next frozen queue block may be prepared.

That means the project may proceed from the currently reviewed top-50 candidates to the next frozen ranks starting at:

`50+`.

This should still use the same staged pattern:

1. prepare exact next frozen block;
2. review preparation;
3. AI proposal stage;
4. categorical human adjudication only where required;
5. import/reconciliation if required;
6. separate activation;
7. review activation.

Do not skip/reorder ranks to improve apparent yield.

## 19. Future manual checks should remain categorical-only

The protocol improvement from Review168 remains in force.

If owner review is required in later batches, use categorical questions only, such as:

- evidence sufficient? Yes/No;
- same/derived? Yes/No;
- personally inspected? Yes/No;
- own decision? Yes/No.

Do not reintroduce mandatory typed visual descriptions or rationales.

## 20. Current AI-screen coverage interpretation

After batch05 closure:

- AI-screen reviewed highest-risk candidates: 50/85;
- remaining not yet AI visually reviewed: 35.

This does not mean 50 accepted independent scientific samples.

It means the first 50 frozen queue candidates have completed the declared screen-level audit workflow.

## 21. Scope limitation remains critical

Review174 accepts only the **screen-level perceptual adjudication state**.

It does not prove:

- capture independence;
- subject/session independence beyond dataset protocol;
- absence of every transformed/cropped derivative;
- full-video lineage independence;
- global OULU content independence;
- cross-dataset independence.

These limitations should remain explicit in the eventual paper/supplement.

## 22. Scientific/model stages remain blocked

Batch05 closure does not automatically authorize:

- source-dry-run;
- analysis freeze;
- locked target evaluation;
- classifier/risk-model execution;
- other-dataset processing;
- scientific-readiness claim.

Those remain controlled by later data-audit/governance gates.

## Final disposition

**DOCUMENT 173 — ACCEPTED WITHOUT REWORK.**

**BATCH-05 ADDITIVE ACTIVATION — ACCEPTED.**

**BATCH-05 SCREEN-LEVEL REVIEW — CLOSED.**

**ACCEPTED CURRENT SCREEN-LEVEL TOTAL = 50.**

**NO FURTHER OWNER INPUT IS REQUIRED FOR RANKS40..49.**

**PREPARATION OF THE NEXT FROZEN QUEUE BLOCK, BEGINNING AT RANK50, IS AUTHORIZED.**

Continue to preserve all historical pending/nonactivation fields as immutable history. Review174 is the additive acceptance authority; do not retroactively rewrite earlier records merely to make them look current.

Models, other datasets, and later scientific stages remain blocked until their own gates are satisfied.
