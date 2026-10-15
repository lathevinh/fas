# 188 — Review of Document 187: OULU Batch-06 Categorical Human Import

Date: 2026-10-15  
Repository: `lathevinh/fas`  
Reviewed commit: `2411877763a2bdcc71df8c61d184c9c214d43126`  
Reviewed document: `docs/187-oulu-batch06-categorical-import.md`  
Reviewed aggregate: `results/phase1/oulu-categorical-import-batch06-v1.json`  
Reviewed importer: `scripts/import_oulu_categorical_batch06.py`  
Reviewed regression addition: `tests/test_oulu.py`

## Verdict

**DOCUMENT 187 — ACCEPTED WITHOUT REWORK.**

**BATCH-06 CATEGORICAL IMPORT — ACCEPTED FOR MECHANICAL, PROVENANCE, AND SEMANTIC-ADJUDICATION SCOPE.**

**ALL TEN OWNER DECISIONS FOR RANKS 50..59 ARE ACCEPTED.**

**NO AI/HUMAN DISAGREEMENT EXISTS IN THE ACTUAL IMPORTED SET.**

**NO RECONCILIATION IS REQUIRED.**

**NO SCIENTIFIC HARD STOP IS TRIGGERED.**

**NO FURTHER OWNER/HUMAN INPUT IS REQUIRED FOR RANKS 50..59.**

**THE TEN BATCH-06 SCREEN-LEVEL DISPOSITIONS ARE NOW ELIGIBLE FOR A SEPARATE ADDITIVE ACTIVATION CHECKPOINT.**

**CURRENT ACCEPTED EFFECTIVE TOTAL REMAINS 50 UNTIL THAT ACTIVATION IS SEPARATELY MATERIALIZED AND REVIEWED.**

**DO NOT START RANK60+, OTHER DATASETS, OR RESEARCH-MODEL EXECUTION BEFORE THE ACTIVATION REVIEW.**

---

## 1. Scope is exact

The categorical import covers exactly original frozen queue ranks:

`50,51,52,53,54,55,56,57,58,59`.

No later rank is imported.

No rank is omitted.

This preserves the bounded sequential review protocol.

## 2. Review186 authority is correctly bound

The importer requires the exact Review186 SHA:

`b431758859bf7d01692612f2e934eb25c274742158a13a73ec96fd85f06ebc66`.

It also requires the exact accepted Document185 handoff aggregate and exact successful Document185 publication CI.

This is the correct additive authority chain.

## 3. Exact source185 publication CI is bound before import

The importer requires exactly:

- head `ad9d5d7edc86a69e2e48a40f4a0ec13ed1d75a16`;
- run `38690950258`;
- job `116276475624`;
- run completed/success;
- job completed/success.

This prevents a handoff state other than the formally accepted source185 state from authorizing import.

## 4. The actual received owner export is byte-pinned

The import preflight binds the exact received source SHA:

`5e4ebaa7a24e5ad0398763d119d605c432b57c6693a0a1d63083f458db1c049b`.

The importer requires:

- a non-symlink source;
- the exact expected filename/location beside the accepted form;
- exact byte SHA equality before import.

This is appropriate.

## 5. Original owner bytes are preserved

The public result reports:

`original_owner_bytes_unchanged = true`.

The source remains in the received location.

The canonical imported snapshot is stored separately.

This is the correct distinction between received evidence and normalized internal representation.

## 6. Canonical serialization is not misrepresented as original bytes

The original source SHA and canonical human-input SHA are intentionally different:

- received source: `5e4ebaa7...1c049b`;
- canonical snapshot: `040d199d...88549`.

Document187 correctly states that canonical serialization preserves structured values, not original formatting/key order.

This is scientifically and technically correct.

## 7. Human record version/type is strictly validated

The importer requires:

- integer version exactly `1`;
- record type exactly `batch06_categorical_review`.

Boolean or floating-point substitutes for the version are rejected by the tests.

This exact typing is appropriate.

## 8. Human reviewer metadata is validated

The importer requires:

- reviewer object;
- permitted human-reviewer kind;
- nonblank reviewer ID;
- top-level personal-inspection attestation = true.

The actual checkpoint describes the supplied source as the owner export authorized by Review186.

As before, this remains an attested human-review record rather than independently authenticated identity.

That limitation is properly disclosed.

## 9. UTC review timestamp is required

The importer parses the supplied timestamp and requires an explicit zero UTC offset.

Naive timestamps and non-UTC offsets are rejected by the regression test.

This is appropriate provenance validation.

## 10. Exact definition authority is validated

The human export must match the accepted handoff definition for:

- definition SHA;
- Review184 SHA;
- accepted AI183 aggregate SHA.

The imported answer file therefore cannot be detached from the accepted batch06 form.

## 11. Exact ten-rank human set is required

The input must contain ten unique integer ranks50..59.

Wrong count, float/bool rank types, duplicated/substituted ranks, or malformed rank sets fail validation.

Input row order may vary because rows are explicitly sorted by queue rank before derived processing.

That is acceptable.

## 12. Every pair is bound to the accepted packet, AI row, and frozen queue record

For each rank, the importer verifies:

- packet SHA;
- AI-record SHA;
- exact frozen pair-record SHA;
- rank equality in packet/AI/queue;
- candidate equality across queue, packet, and AI record;
- AI proposal equality to the definition.

This is a strong provenance chain.

## 13. The full accepted 6640-record frozen queue is revalidated

The importer verifies:

- exactly 6640 queue records;
- frozen queue bundle SHA;
- frozen queue summary SHA.

This prevents the selected rank bindings from being evaluated against a silently modified queue.

## 14. All 30 reviewed assets are re-bound

Each human row must contain the exact three reviewed asset hashes from the accepted definition.

The importer then verifies those handoff asset bytes and original packet image bytes against the same expected SHA values.

The public result reports:

**30 bound asset hashes verified.**

This is sufficient evidence that the imported human answers refer to the accepted review evidence.

## 15. Strict categorical typing is enforced

For every pair:

- `evidence_sufficient` must be an actual boolean;
- if sufficient, `same_or_derived_content` must be an actual boolean;
- if insufficient, `same_or_derived_content` must be exactly null.

Integer/string stand-ins are rejected.

This is the correct fail-closed behavior.

## 16. Both pair-level human attestations are required

The importer requires:

- `personal_inspection_attested = true`;
- `owner_decision_attested = true`.

False, missing, or non-boolean forms are rejected.

This preserves the accepted human-decision ownership model.

## 17. Capture provenance is not overclaimed

Every row must explicitly state:

`capture_provenance_certified = false`.

The importer rejects any attempt to convert this perceptual content-screen adjudication into a capture-provenance certification.

This is scientifically important.

## 18. Dispositions are independently re-derived

The importer does not trust the exported disposition field by itself.

It recomputes the disposition from the strict categorical answers using the accepted mapping.

The exported disposition must match that derived result exactly.

This is correct.

## 19. Scientific hard-stop flags are independently re-derived

A row is hard-stop positive exactly when the derived disposition is:

`confirmed_same_content_or_derived_lineage`.

The importer also independently derives the aggregate stop flag and requires exact equality with the supplied aggregate value.

Contradictory pair or aggregate stop fields are rejected.

## 20. Actual owner result is ten valid rejections

The imported set contains:

- `rejected_false_positive`: **10**;
- `confirmed_same_content_or_derived_lineage`: **0**;
- `uncertain_insufficient_evidence`: **0**.

Because rejection requires sufficient evidence + same/derived No under the accepted mapping, all ten owner decisions are sufficient-evidence negative lineage judgments.

This is a valid categorical result.

## 21. No scientific hard stop is triggered

There are no confirmed same/derived owner decisions.

The aggregate prospective scientific-stop flag is therefore false.

This is consistent with the per-pair results.

## 22. AI and human agree on all ten ranks

Document183 proposed rejection for every rank50..59.

The owner independently supplied rejection for every rank50..59.

The import records:

- disagreements with AI: **0**;
- reconciliation-required ranks: **none**.

Therefore a separate disagreement-reconciliation stage is unnecessary for this actual batch.

## 23. AI/human agreement is not treated as proof of correctness

Document187 explicitly states that agreement with AI does not independently establish correctness or specificity.

Review188 agrees.

Agreement removes a reconciliation blocker; it does not convert correlated AI/human evidence into independent validation.

## 24. Disagreement handling is nevertheless fail-closed

For hypothetical disagreement, the importer:

- retains owner disposition;
- retains AI disposition separately;
- sets `disagreement_with_AI = true`;
- sets `reconciliation_required = true`;
- sets comparison state to uncertainty;
- does not activate the result.

Importantly, a confirmed owner disposition still retains its separate scientific hard-stop flag.

This design is appropriate.

## 25. Comparison state is not effective disposition

The public aggregate explicitly records:

`comparison_states_are_not_activated_dispositions = true`.

The importer also sets:

`effective_disposition_activated = false`

for every imported row.

This prevents the AI comparison layer from silently becoming the scientific ledger.

## 26. Owner fields are preserved exactly

Before adding derived importer metadata, the importer checks for key collisions.

If an owner-supplied field collides with a derived importer field, the import fails rather than overwriting the owner value.

The synthetic test also verifies preservation of nested extra fields.

This is strong nonmutation behavior.

## 27. No rationale is manufactured

The importer does not require or generate a human rationale.

No machine narrative is generated.

This preserves the accepted categorical-only review policy and avoids falsely attributing AI/system prose to the owner.

## 28. Main and sibling imports are deterministic

Each private import root contains:

- lineage;
- canonical owner input;
- ten imported rows;
- summary.

Total:

**13 files per root.**

Main and sibling match:

**13/13 byte-identically**.

This is deterministic import replay only, not independent human adjudication.

## 29. Protected history remains stable

Document187 reports:

- 61 prior roots unchanged;
- frozen13 unchanged;
- config17 unchanged;
- prior owner records unchanged;
- accepted helpers/policies/historical importers unchanged;
- historical pending-review flags unchanged.

This satisfies additive-history discipline.

## 30. No new media or visual review occurs

The import checkpoint performs no:

- media decode;
- archive extraction;
- archive rehash;
- image generation;
- new AI visual review.

This is correct.

## 31. Output and authority refusal checks are meaningful

Actual CLI probes reject:

- existing main output;
- existing sibling output;
- repository output;
- source-overlap output;
- symlink output;
- wrong source CI;
- activation authority;
- wrong owner digest.

The immutable writer additionally refuses overwrite of:

- preflight;
- canonical input;
- first imported row.

This is strong fail-closed behavior.

## 32. Regression test directly exercises the importer

The new importer test covers:

- exact owner-field preservation;
- strict rank typing;
- strict categorical bool/null typing;
- packet/AI/exact-pair/asset binding drift;
- inspection/decision attestations;
- capture-provenance false requirement;
- exported disposition/stop contradiction;
- all three categorical outcomes;
- aggregate hard-stop behavior;
- AI disagreement behavior;
- derived-metadata collision;
- exact Review186/import authority;
- exact source185 CI;
- unsafe output refusal.

This is meaningful checkpoint-specific coverage.

## 33. Local regressions are clean

Document187 reports:

- focused: **77/77 passed**;
- full: **264/264 passed**.

The prior accepted test ASTs are preserved apart from one explicit new method.

No regression blocker remains.

## 34. Fresh exact Document187 publication CI passes

Exact reviewed commit:

`2411877763a2bdcc71df8c61d184c9c214d43126`.

Fresh GitHub Actions run:

`38694502603`

is:

`completed / success`.

Validate job:

`116287801095`

is:

`completed / success`.

The job completed at:

`2026-10-15T06:47:53Z`.

All listed workflow validation steps completed successfully.

There is no publication-CI blocker.

## 35. Semantic import blockers are cleared

The human review was performed under the formally accepted categorical handoff.

The imported answers:

- satisfy strict mapping;
- bind the accepted evidence;
- contain required human attestations;
- produce no uncertainty;
- produce no confirmed lineage;
- produce no AI disagreement.

There is therefore no remaining pair-specific semantic/reconciliation blocker for ranks50..59.

## 36. Visibility-limited ranks do not require another review pass

Ranks54/56/58/59 had neutral visibility warnings in the accepted form.

The owner nevertheless selected evidence sufficient and same/derived No for those ranks.

Because the form allowed uncertainty and the importer verifies the owner's own categorical choice, Review188 does not require a second manual pass merely because visibility was limited.

Do not ask the owner to re-review these ranks without new contradictory evidence.

## 37. Correlated ranks56..59 remain correlated evidence

The owner supplied separate judgments for each frozen rank.

That resolves the candidate-level adjudication requirement.

It does **not** make ranks56..59 statistically independent observations.

The correlation limitation should remain in the eventual audit/reporting language.

## 38. No further human input is required for batch06

Do not ask the owner to:

- reopen ranks50..59;
- type explanations;
- reconfirm AI text;
- repeat categorical decisions;
- provide license/admin attestations.

The next step is mechanical/governance activation preparation only.

## 39. Current effective total correctly remains 50

Document187 does not activate the imported decisions.

Current state remains:

`accepted_current_total = 50`

and:

`effective_dispositions_activated = 0`

for batch06.

This is correct.

## 40. Prospective total after accepted batch06 activation is 60

A future separate activation checkpoint may materialize the accepted batch06 screen-level disposition set:

- reject: 10;
- uncertain: 0;
- confirmed same/derived: 0.

If that activation is formally accepted, the effective accepted total will advance:

**50 -> 60**.

Do not report 60 as the current effective total before activation review.

## 41. AI coverage remains 60/85

AI-screen coverage is already accepted through rank59:

**60/85**.

There are still:

**25**

highest-risk candidates not yet AI visually screened.

Activation does not change AI coverage; it changes the accepted effective disposition ledger.

## 42. Next authorized step: separate additive activation

The next checkpoint may prepare a batch06 activation ledger for exactly ranks50..59.

It should bind:

- Review188;
- Document187 public aggregate;
- exact imported pair bundle;
- canonical owner snapshot;
- received owner source SHA;
- exact successful Document187 publication CI;
- accepted packet/AI/definition lineage.

It must not rewrite the existing import rows or historical pending flags.

## 43. Activation must remain separate

Review188 authorizes activation **preparation**, not activation by implication.

The activation checkpoint should explicitly record:

- ten effective batch06 dispositions materialized;
- all ten are `rejected_false_positive`;
- scientific hard stop false;
- accepted effective total prospectively 50 -> 60;
- batch06 closure pending activation review.

## 44. Rank60+ remains blocked until activation review

Required sequence:

1. Review188 accepts Document187.
2. Prepare separate additive batch06 activation.
3. Publish activation checkpoint and obtain fresh exact CI.
4. Formally review activation.
5. Only after activation acceptance may the next frozen queue block begin at rank60.

This preserves bounded sequential review.

## 45. Scientific/model stages remain blocked

Review188 does not establish:

- exhaustive OULU content independence;
- capture independence;
- transformed-region independence;
- cross-dataset independence;
- source-dry-run readiness;
- analysis freeze;
- locked evaluation;
- classifier/risk-model execution readiness.

Existing scientific-stage blockers remain unchanged.

## Final disposition

**DOCUMENT 187 — ACCEPTED WITHOUT REWORK.**

**THE TEN BATCH06 OWNER CATEGORICAL DECISIONS ARE ACCEPTED.**

**ALL TEN ARE `rejected_false_positive`.**

**NO AI/HUMAN DISAGREEMENT EXISTS.**

**NO RECONCILIATION IS REQUIRED.**

**NO SCIENTIFIC HARD STOP IS TRIGGERED.**

**NO FURTHER OWNER INPUT IS REQUIRED FOR RANKS50..59.**

**THE TEN BATCH06 SCREEN-LEVEL DISPOSITIONS ARE ELIGIBLE FOR A SEPARATE ADDITIVE ACTIVATION CHECKPOINT.**

Current accepted effective total remains **50** until that activation is separately materialized and reviewed.

AI-screen coverage remains **60/85** with **25** highest-risk candidates not yet AI visually screened.

Do not proceed to rank60+, other datasets, or research-model execution before the batch06 activation review.
