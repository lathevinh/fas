# 166 — Review of Document 165: OULU Batch-05 Human Import

Date: 2026-10-14  
Repository: `lathevinh/fas`  
Reviewed commit: `21a7ef1474829b8e11a2369700a6716155d3f1b2`  
Reviewed document: `docs/165-oulu-batch05-human-import.md`  
Reviewed aggregate: `results/phase1/oulu-human-review-batch05-v1.json`  
Context document additionally reviewed: `docs/164-review-response-doc163-oulu-batch05-human-handoff.md`

## Verdict

**DOCUMENT 165 — ACCEPTED FOR MECHANICAL/PROVENANCE IMPORT SCOPE ONLY.**

**CHECKPOINT 1.5AJ — NOT ACCEPTED FOR SEMANTIC CLEARANCE.**

**BATCH-05 ADDITIVE ACTIVATION — NOT AUTHORIZED.**

**RANKS 50+ — NOT AUTHORIZED.**

The import machinery, source binding, nonmutation discipline, regression evidence and exact CI are strong. However, semantic clearance is still blocked by pair-specific human-text deficiencies and by a governance/provenance issue around how the human rationale text was produced.

A separate additive follow-up is required before batch-05 activation.

## 1. Document 164 handoff is technically sound, but the prospective review order was not followed

Document 164 prepared the correct bounded human-review handoff for original ranks 40–49:

- exactly 10 pairs;
- exactly 30 already-bound images;
- human fields initially blank;
- all three dispositions retained;
- low-visibility warnings kept neutral;
- no human/effective disposition manufactured;
- 33/33 handoff files independently reproduced;
- focused 67/67 and full 254/254 tests passed.

Technically, the handoff preparation is acceptable.

However, Document 165 explicitly records:

`formal_external_review_of_handoff164_present = false`.

The owner then supplied human answers and the import proceeded before a formal external review checkpoint of Document 164 was created.

This is a **prospective process-order deviation** from the staged workflow previously specified:

`handoff preparation -> review handoff -> genuine human input -> import`.

The deviation does not automatically invalidate the raw owner answers because the handoff was immutable, source-bound and CI-verified. But the project must not later claim that batch 05 followed a strict external-review-before-human-input sequence.

### Required treatment

Do not rewrite Document 164 or Document 165.

Record the deviation additively in the next governance record:

- Document 164 was technically adequate;
- human review/import occurred before formal external acceptance of 164;
- no evidence was retrospectively altered;
- future batches should restore the intended ordering.

## 2. Mechanical import of the owner JSON is correct

The owner source JSON is hash-pinned and preserved byte-for-byte.

Document 165 reports raw source SHA256:

`97867bd166f61c6d384ac0dc0ac2d114d04d34b7d142d8cf1e565eb49d015441`.

The importer validates original integer ranks 40–49, exactly ten unique rows, expected batch-05 record type, nonblank `visible_rendered_structure`, scientific-stop consistency, exact handoff definition/page/summary, accepted AI ledger, packets, 30 bound assets, exact prerequisite CI, and protected/frozen/config evidence.

The temporary `rank-40` mapping exists only in memory for reuse of the accepted validator and is restored before persistence.

This is acceptable.

## 3. No historical artifact is rewritten

The import correctly preserves:

- original owner JSON bytes;
- earlier handoff artifacts;
- AI proposal ledger;
- packet ledger;
- earlier pending flags;
- previous current ledgers.

The new human answers live in a separate import ledger.

This is the correct additive-history model.

## 4. Imported human outcome state is internally consistent

Recorded human outcomes:

| Item | Result |
|---|---:|
| Human dispositions imported | 10 |
| `rejected_false_positive` | 10 |
| `uncertain_insufficient_evidence` | 0 |
| `confirmed_same_content_or_derived_lineage` | 0 |
| AI/human disagreements | 0 |
| Effective activations | 0 |
| Accepted current total | 40 |

The ten matching AI/human comparison states are correctly **not** counted as accepted current dispositions.

Batch 05 therefore remains open.

## 5. The 10/10 human rejection pattern is not itself a defect

Ten human rejection answers are not automatically invalid merely because the AI also proposed ten rejections.

The queue is deliberately populated with high-risk perceptual-similarity candidates, so a high false-positive rate is plausible.

There must still be no agreement quota, no rejection quota, no pressure to keep the queue moving, and uncertainty/same-derived must remain valid options.

Document 165 retains those safeguards.

## 6. Pair-specific semantic clearance is correctly still pending

The aggregate correctly reports:

`pair_specific_semantic_review_pending = true`

and:

`eligible_for_additive_activation_without_further_review = false`.

This is the right state.

The importer is not entitled to convert nonblank text into semantic adequacy automatically.

## 7. Ranks 42, 43, 48 and 49 have an explicit semantic defect

Document 165 reports reference-only/previous-queue wording in both the human structure description and rationale for:

`42, 43, 48, 49`.

These rows are not self-contained.

A phrase equivalent to `same with previous queue` is not enough to establish the visible rendered structures of the current pair.

### Hash diagnostic

| Rank | Three bound images equal to preceding rank |
|---|---:|
| 42 | 0/3 |
| 43 | 0/3 |
| 48 | 3/3 |
| 49 | 0/3 |

### Ranks 42, 43 and 49

Their bound assets are not identical to the preceding pair.

Therefore a reference-only answer cannot be accepted as pair-specific semantic reasoning.

These ranks **require additive human clarification**.

### Rank 48

Its three bound images are byte-identical to rank 47.

This explains why repeated wording may be substantively reasonable, but the current reference-only phrase is still not self-contained enough for an auditable record.

Rank 48 does not necessarily require new visual inspection, but it should receive a short additive clarification that explicitly states that the bound evidence is identical to rank 47, the same visible structures are therefore being relied upon, and the human disposition remains independently affirmed for rank 48.

Do not silently copy rank 47 prose into rank 48.

## 8. Duplicate human-text groups require semantic scrutiny, not automatic rejection

Document 165 reports identical structure/rationale text in groups:

- 40/41;
- 42/43;
- 48/49.

Text duplication alone is not a protocol failure.

Correlated evidence can legitimately produce repeated observations.

But duplicate text cannot substitute for candidate-level semantic review.

For 42/43 and 48/49, the separate reference-only problem already requires follow-up.

For 40/41, the duplicated text must be checked against each pair's bound evidence, especially because both are in the heightened-scrutiny/visibility group.

## 9. Heightened-scrutiny ranks remain unresolved

Document 165 correctly preserves heightened scrutiny for:

`40, 41, 42, 43, 49`.

These include darkness/veil-limited pairs from the prior AI checkpoint.

No visibility warning should be cleared merely because the human selected rejection or entered nonblank text.

For each of these pairs, semantic review must establish that the remaining visible foreground structure is sufficient for the chosen disposition.

If not, the correct outcome remains `uncertain_insufficient_evidence`.

## 10. Important governance issue: the rationale-authorship claim is not supportable as written

The public aggregate contains:

`human_reasoning_generated_or_replaced_by_assistant = false`.

That field is too strong.

During the human-review phase, the assistant in this conversation supplied pair-specific draft wording for multiple batch-05 pairs after viewing the screenshots. Therefore AI-assisted drafting of human rationale text occurred in the workflow, even if the owner personally inspected the evidence, independently chose the disposition, and the importer itself did not generate or overwrite any field.

These are different claims.

### What can still be claimed

The project can claim, if accurate:

- the **human disposition was selected by the owner**;
- the owner **personally inspected the bound evidence**;
- the raw exported JSON was not modified by the importer;
- the importer did not synthesize human fields.

### What should not be claimed without qualification

The project should not claim that the human rationale wording was fully independent of AI assistance.

This matters because the handoff was already not fully blinded: AI notes were available collapsed, and external AI assistance supplied proposed wording during review.

### Required additive correction

Do not rewrite Document 165.

Add a provenance clarification such as:

- `human_disposition_owner_selected = true`;
- `human_personal_inspection_attested = true`;
- `importer_generated_human_reasoning = false`;
- `AI_assisted_rationale_drafting_occurred_or_cannot_be_excluded = true`;
- `independent_blinded_human_rationale_authorship_claimed = false`.

This preserves the scientifically meaningful distinction between **human decision ownership** and **wording authorship**.

## 11. AI-assisted wording does not automatically invalidate the human disposition

The human dispositions need not be discarded solely because AI-assisted wording was used.

The relevant question is whether the owner personally inspected the evidence, independently chose the disposition, and agreed that the written rationale accurately describes what was observed.

If those conditions hold, the disposition may still be usable as a human-adjudicated outcome.

But it should be described as **AI-assisted human adjudication / AI-assisted rationale drafting**, not as a fully independent blinded human rationale.

This limitation should also be reflected in any eventual paper/supplement if the audit is described.

## 12. Serialization reproducibility is strong

The original and replay human-import roots each contain:

- lineage;
- canonical parsed human input;
- 10 pair rows;
- summary.

Total: **13 files**.

Independent serialization replay reproduces **13/13 byte-identically**.

This establishes deterministic import processing, not an independent second human review.

## 13. Handoff preservation is handled correctly

Document 165 reports that the prior main handoff originally contained 33 files and now contains exactly one additional owner JSON.

The original 33 files remain unchanged.

The sibling reexport remains at its original 33 files.

This is acceptable because the owner JSON is explicitly treated as a declared addition rather than silently modifying the accepted handoff evidence.

## 14. Protected evidence remains stable

The checkpoint reports:

- 44 protected roots unchanged;
- frozen 13 unchanged;
- 17 study configs unchanged;
- prior source/implementation pins unchanged.

The previous human-0 handoff state and AI pending flags remain historical records rather than being patched.

This is correct.

## 15. Regression evidence is strong

Document 165 reports:

- focused OULU: **68/68 passed**;
- full regression: **255/255 passed**;
- zero failures/errors.

A new importer test was added and the full suite was rerun, which is appropriate because this checkpoint introduces a new batch-05 import adapter.

No regression blocker is present.

## 16. Exact prerequisite CI is correctly bound

The import binds the exact handoff commit:

`a2e26b358a2de8fd586cf5b51a665f024eb55c60`

with:

- run `38544464879`;
- validate job `115786974148`;
- completed/success.

This establishes the prerequisite handoff publication state.

## 17. Fresh exact CI for Document 165 passes

Exact reviewed commit:

`21a7ef1474829b8e11a2369700a6716155d3f1b2`

Fresh GitHub Actions:

- run `38547153266`;
- status `completed`;
- conclusion `success`.

Validate job:

`115795927764`

completed successfully.

The exact job passes checkout/setup, FFmpeg installation, model-free screening dependencies, synthetic regression, canonical schema validation, unavailable-stage fail-closed checks, and legacy-stage rejection checks.

There is no CI blocker.

## 18. Formal external review of Document 164 should now be recorded retrospectively, not invented prospectively

Document 165 correctly says no formal external review of 164 existed at import time.

This review can now state:

**Document 164 is technically acceptable as a handoff-preparation artifact.**

But this acceptance occurs **after** owner review/import.

Therefore it must be recorded as retrospective technical acceptance, not as if it existed before the human review.

This distinction preserves audit honesty.

## 19. Minimum remediation before activation

Batch-05 activation must remain blocked until an additive semantic follow-up is completed.

### Mandatory clarification

- rank 42;
- rank 43;
- rank 48;
- rank 49.

### Mandatory heightened-scrutiny semantic check

- rank 40;
- rank 41;
- rank 42;
- rank 43;
- rank 49.

### Provenance clarification

Record AI-assisted rationale drafting / lack of fully independent rationale authorship.

No prior owner JSON should be overwritten.

No historical imported row should be edited.

## 20. Recommended targeted clarification format

For each affected rank, create a separate immutable additive record containing:

1. Visible foreground structure on the left
2. Visible foreground structure on the right
3. Visibility limitation
4. Whether evidence is sufficient
5. Pair-specific disposition rationale
6. Owner attestation that the disposition remains their own decision
7. Disclosure that wording may have been AI-assisted, if applicable

For rank 48, the record may explicitly state that all three bound images are identical to rank 47 and explain why the same visual conclusion is being independently affirmed.

## 21. No need to repeat the entire human review

There is no justification for discarding all ten human answers.

The raw owner input is preserved and the import is mechanically sound.

The remediation should be narrow and additive.

Do not reopen clean pairs unnecessarily.

## 22. Batch 05 remains open

Current accepted state:

- AI proposals: 10 reject;
- imported human dispositions: 10 reject;
- disagreements: 0;
- effective batch-05 activations: 0;
- accepted current total: 40;
- batch-05 semantic clearance: pending.

Therefore batch 05 is **not closed**.

## 23. Ranks 50+ remain blocked

Do not continue to ranks 50+ yet.

Required order from here:

1. accept Document 165 for import/provenance scope only;
2. record the batch-05 process-order/rationale-authorship provenance clarification;
3. obtain targeted human semantic clarification for affected ranks;
4. review semantic clarification;
5. reconcile only if any disposition changes;
6. create a separate additive activation ledger;
7. review activation;
8. only then continue ranks 50+.

## 24. Scientific/model gates remain blocked

Document 165 does not authorize:

- OULU content-lineage completion;
- data-audit completion;
- source-dry-run;
- analysis freeze;
- locked target evaluation;
- detector/classifier/risk-model execution;
- other-dataset processing;
- capture-provenance certification;
- global content-independence certification;
- scientific readiness.

All later stages remain fail-closed.

## Final disposition

**DOCUMENT 165 — ACCEPTED FOR MECHANICAL/PROVENANCE IMPORT SCOPE.**

**CHECKPOINT 1.5AJ — SEMANTIC CLEARANCE NOT ACCEPTED.**

**BATCH-05 ACTIVATION — NOT AUTHORIZED.**

Strengths:

- exact 10-rank import;
- source JSON preserved;
- no effective activation;
- zero AI/human disagreement;
- 13/13 serialization replay;
- 44 protected roots stable;
- frozen/config evidence stable;
- focused 68/68 and full 255/255 pass;
- fresh exact CI succeeds.

Blocking findings:

1. Human review/import occurred before formal external review of Document 164; record this as a prospective-order deviation rather than rewriting history.
2. Ranks 42, 43, 48 and 49 use reference-only/non-self-contained human reasoning.
3. Heightened-scrutiny ranks 40, 41, 42, 43 and 49 still require semantic sufficiency review.
4. The public claim `human_reasoning_generated_or_replaced_by_assistant = false` is too strong because AI-assisted rationale drafting occurred in the human-review workflow. Preserve the owner's decision ownership, but disclose AI assistance in wording and do not claim fully independent blinded rationale authorship.

The correct next step is a **narrow additive semantic/provenance clarification**, not batch-05 activation and not rank 50+.
