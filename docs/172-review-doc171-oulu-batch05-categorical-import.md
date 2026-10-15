# 172 — Review of Document 171: OULU Batch-05 Categorical Human Import

Date: 2026-10-15  
Repository: `lathevinh/fas`  
Reviewed commit: `35567282cf6217f2dc3f63fa4510780bb99b1759`  
Reviewed document: `docs/171-oulu-batch05-categorical-import.md`  
Reviewed aggregate: `results/phase1/oulu-categorical-import-batch05-v1.json`  
Reviewed importer: `scripts/import_oulu_categorical_batch05.py`  
Reviewed regression addition: `tests/test_oulu.py`

## Verdict

**DOCUMENT 171 — ACCEPTED WITHOUT REWORK.**

**CATEGORICAL IMPORT — ACCEPTED FOR MECHANICAL, PROVENANCE, AND SEMANTIC-ADJUDICATION SCOPE.**

**THE SIX TARGETED BATCH-05 SEMANTIC BLOCKERS ARE CLEARED.**

**NO FURTHER OWNER/HUMAN INPUT IS REQUIRED FOR RANKS 40, 41, 42, 43, 48, 49.**

**BATCH-05 SCREEN-LEVEL DISPOSITIONS ARE NOW ELIGIBLE FOR A SEPARATE ADDITIVE ACTIVATION CHECKPOINT.**

**DO NOT ACTIVATE IN PLACE, DO NOT REWRITE PRIOR RECORDS, AND DO NOT START RANK 50+ UNTIL THE SEPARATE ACTIVATION CHECKPOINT IS REVIEWED.**

The categorical-only redesign introduced by Review168/Document169 has now completed its intended purpose. The owner supplied six new categorical judgments using the accepted form, the dedicated importer validated them strictly, all six judgments agree with both the earlier AI proposal and the earlier owner disposition, and no hard-stop condition was triggered.

This is sufficient to clear the targeted semantic-review blockers that remained after Review166. No prose rationale is required.

## 1. Scope is exact and correct

The imported categorical review covers exactly:

`40, 41, 42, 43, 48, 49`.

These are the six ranks authorized by Review170.

Clean ranks `44..47` are not reopened.

No rank 50+, other dataset, new frame, new video decode, new AI inspection, or research-model execution is involved.

## 2. Formal review ordering is now correct

Unlike the earlier batch-05 handoff deviation, the categorical workflow follows the intended order:

1. categorical form preparation;
2. formal Review170 acceptance;
3. genuine owner categorical input;
4. separate categorical import;
5. this formal Review172.

Document171 explicitly binds Review170 before import.

No acceptance is backdated.

## 3. All six categorical decisions are valid and internally consistent

For all six ranks:

- `evidence_sufficient = true`;
- `same_or_derived_content = false`;
- `personal_inspection_attested = true`;
- `owner_decision_attested = true`;
- disposition = `rejected_false_positive`.

Therefore the categorical mapping is valid for all six pairs.

## 4. No scientific hard stop is triggered

No pair has sufficient evidence plus same/derived = Yes.

The aggregate stop flag is therefore correctly false.

The importer verifies both per-row and aggregate stop consistency.

## 5. Strict boolean/null typing is correctly enforced

The importer rejects integer/string substitutes for booleans, missing or malformed target ranks, insufficient evidence with a populated same/derived answer, contradictory dispositions, and contradictory stop flags.

This exact-type discipline is appropriate for a scientific audit record.

## 6. Exact evidence and authority bindings are strong

Each imported row is bound to:

- exact queue rank;
- packet SHA;
- prior imported-human-row SHA;
- reviewed asset SHA map;
- AI candidate/record;
- accepted categorical form definition;
- governance record;
- Review168/Review170 authority;
- exact successful source169 CI.

This prevents detached or substituted adjudication records.

## 7. Rank48 handling remains correct

Rank48 remains bound to evidence byte-identical to rank47.

The identity metadata is preserved, but rank48 still carries its own categorical decision.

No answer is copied silently.

## 8. Every supplied human field is preserved

The importer preserves every owner-supplied field and rejects collisions with importer-derived metadata.

The regression test also verifies preservation of an extra synthetic owner field.

This is a strong nonmutation property.

## 9. Raw source and canonical parsed input are correctly distinguished

The raw owner JSON stays byte-unchanged and separately hash-pinned.

Canonical parsed JSON is stored separately.

Document171 correctly does not conflate canonical serialization with raw serialization.

## 10. Old prose-form input is not repurposed

The prior Document167 input remains historical only.

It is not imported, converted, prefilled, or relabeled as categorical review.

The accepted categorical source is a distinct owner export.

## 11. No human prose is required or generated

The authoritative human contribution is the categorical choice plus personal-inspection and decision-ownership attestations.

No descriptive rationale is required.

No machine narrative is generated here.

## 12. AI/human comparison is conservative

Any disagreement with the AI or change from the prior human disposition would force reconciliation and a comparison state of uncertainty.

This is a good fail-safe.

## 13. Actual observed comparison requires no reconciliation

For this batch:

- disagreements with AI: **0**;
- changes from prior human: **0**;
- reconciliation-required ranks: **none**.

Therefore no reconciliation checkpoint is required before activation.

Agreement does not prove correctness; it only means no unresolved disagreement remains.

## 14. The six targeted semantic blockers are resolved

The categorical workflow directly answers the questions that mattered scientifically:

- Is evidence sufficient?
- Is the content same/derived?
- Did the owner inspect it?
- Is the decision the owner's own?

All six targeted ranks answer:

- sufficient = Yes;
- same/derived = No;
- inspected = Yes;
- own decision = Yes.

That is enough to clear the targeted semantic blockers.

## 15. Clean ranks 44–47 should not be reopened

No new evidence or disagreement requires reopening clean ranks `44..47`.

Reopening them would add workload without resolving an identified blocker.

No more owner review is needed there.

## 16. Batch-05 screen-level disposition set is semantically ready for activation

The earlier ten-row batch05 import already contained ten rejection dispositions.

The only remaining semantic blockers were the six ranks now remediated categorically.

Those six show no disposition changes.

Therefore the full batch05 screen-level disposition set is eligible for a separate additive activation checkpoint:

- reject: 10;
- uncertain: 0;
- confirmed same/derived: 0.

This is eligibility for activation, not activation itself.

## 17. Current accepted total correctly remains 40

Document171 correctly leaves:

`accepted_current_total = 40`

and:

`effective_dispositions_activated = 0`

for batch05.

A separately accepted ten-row activation would move the current total to **50**, but that must not be reported yet.

## 18. Serialization replay is correct but not a second adjudication

Each import root contains:

- lineage;
- canonical human input;
- six pair rows;
- summary.

Total: **9 files**.

Replay matches **9/9 byte-identically**.

This demonstrates deterministic import serialization only.

## 19. Protected evidence remains stable

Document171 reports:

- 50 protected prior roots unchanged;
- frozen13 unchanged;
- config17 unchanged;
- original ten human rows unchanged;
- old167 input unchanged;
- historical pending flags unchanged.

This preserves additive history correctly.

## 20. Regression test directly exercises the importer

The added test `test_batch05_categorical_import_strict_mapping_bindings_and_preservation` checks:

- exact field preservation;
- no rationale requirement;
- no automatic activation;
- strict rank/boolean typing;
- asset/packet/prior-row binding failure;
- rank48 identity reference;
- contradictory disposition/stop rejection;
- all three categorical mappings;
- hard-stop behavior;
- invalid insufficient-evidence combinations;
- output refusal.

This is an appropriate importer-specific regression.

## 21. Full regression evidence is strong

Document171 reports:

- focused: **71/71 passed**;
- full: **258/258 passed**;
- diagnostics clean.

No software-regression blocker remains.

## 22. Fresh exact publication CI passes

Exact reviewed commit:

`35567282cf6217f2dc3f63fa4510780bb99b1759`

Fresh publication run:

`38664083043`

is `completed / success`.

Validate job:

`116191848895`

is also `completed / success`.

There is no publication-CI blocker.

## 23. Private-UI limitation remains acceptable

The project still cannot independently prove from automation that every intended UI interaction occurred.

That limitation is already disclosed.

The accepted protocol relies on explicit owner attestations, not independent authentication of visual attention.

This does not block categorical semantic acceptance.

## 24. No more manual human review is required for these six pairs

Do not ask the owner to:

- re-open these six pairs;
- type descriptions;
- type rationales;
- reconfirm generated prose;
- repeat another Yes/No pass just to enable activation.

The next step is mechanical/governance work only.

## 25. Next permitted step: separate additive activation

The next checkpoint may prepare an activation ledger for exactly batch05 ranks `40..49`.

It should materialize:

- 10 `rejected_false_positive`;
- 0 uncertain;
- 0 confirmed same/derived.

The activation checkpoint must bind Review172, Document171 aggregate/import rows, accepted clean prior rows, and exact successful171 publication CI.

It must not rewrite older pending/import records.

## 26. Activation remains separate

Review172 authorizes activation preparation, not activation by implication.

The activation checkpoint should explicitly record:

- ten effective dispositions activated;
- accepted current total 40 -> 50;
- no hard stop;
- batch05 closure only after activation review acceptance.

Until then, batch05 remains open.

## 27. Ranks50+ remain blocked until activation review

Required order:

1. Review172 accepts Document171;
2. prepare separate additive batch05 activation;
3. publish and obtain fresh CI;
4. review activation;
5. only then continue to the next frozen queue block.

## 28. Scientific/model gates remain blocked

This review does not establish global capture independence, complete content-lineage independence, cross-dataset independence, source-dry-run readiness, analysis freeze, locked evaluation, or model-execution readiness.

It is limited to the declared batch05 candidate-screen adjudication scope.

## Final disposition

**DOCUMENT 171 — ACCEPTED WITHOUT REWORK.**

**THE SIX NEW CATEGORICAL OWNER DECISIONS ARE ACCEPTED.**

**TARGETED BATCH-05 SEMANTIC REMEDIATION IS COMPLETE.**

**NO RECONCILIATION IS REQUIRED.**

**NO FURTHER OWNER INPUT IS REQUIRED FOR RANKS 40,41,42,43,48,49.**

**THE FULL TEN-PAIR BATCH-05 SCREEN-LEVEL DISPOSITION SET IS ELIGIBLE FOR A SEPARATE ADDITIVE ACTIVATION CHECKPOINT.**

Current accepted total remains **40** until that activation is separately materialized and reviewed.

The next step is mechanical activation preparation only; do not ask the owner to review these pairs again and do not proceed to rank50+ yet.
