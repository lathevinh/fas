# 190 — Review of Document 189: OULU Batch-06 Additive Activation

Date: 2026-10-15  
Repository: `lathevinh/fas`  
Reviewed commit: `a81bd9259478a8a49ad0783fdb777329791a99d5`  
Reviewed document: `docs/189-review-response-doc188-oulu-batch06-activation.md`  
Reviewed aggregate: `results/phase1/oulu-batch06-activation-v1.json`

## Verdict

**DOCUMENT 189 — ACCEPTED WITHOUT REWORK.**

**BATCH-06 ADDITIVE ACTIVATION — ACCEPTED.**

**BATCH-06 SCREEN-LEVEL REVIEW — CLOSED.**

**ACCEPTED CURRENT EFFECTIVE SCREEN-LEVEL TOTAL ADVANCES FROM 50 TO 60.**

**AI-SCREEN COVERAGE REMAINS 60/85; 25 HIGHEST-RISK CANDIDATES REMAIN NOT YET AI-SCREENED.**

**PREPARATION OF THE NEXT FROZEN QUEUE BLOCK BEGINNING AT RANK60 IS AUTHORIZED.**

**NO FURTHER OWNER/HUMAN INPUT IS REQUIRED FOR RANKS50..59.**

Historical pending/nonactivation fields must remain immutable history. Review190 is the additive acceptance authority for the batch06 activation.

Research-model execution and later scientific stages remain blocked.

---

## 1. Scope is exact

Document189 materializes activation records for exactly:

`50,51,52,53,54,55,56,57,58,59`.

No later rank is included.

This preserves the bounded sequential audit order.

## 2. Review188 existed before activation

Review188 was committed before Document189 and explicitly:

- accepted Document187;
- accepted all ten owner categorical decisions;
- cleared semantic/reconciliation blockers;
- authorized a separate additive activation checkpoint.

There is no process-order violation.

## 3. Source owner decisions are already semantically accepted

The accepted Document187 state for ranks50..59 is:

- `rejected_false_positive`: 10;
- confirmed same/derived: 0;
- uncertain: 0;
- AI/human disagreements: 0;
- reconciliation-required ranks: none;
- scientific hard stop: false.

Document189 does not perform new semantic adjudication.

This is correct.

## 4. Activation is additive rather than a rewrite

Historical Document187 import rows remain nonactivated creation-time records.

Document189 creates new activation rows rather than rewriting prior records.

This is the correct additive-history model.

## 5. Only the new activation rows materialize effective disposition state

The new rows set:

`effective_disposition_activated = true`.

At the same time they retain:

`activation_checkpoint_review_pending = true`

and:

`counts_as_accepted_current_effective_disposition = false`.

This correctly prevented the ledger from counting the ten rows as accepted before formal Review190.

## 6. Historical pending/nonactivation fields remain unchanged

Document189 explicitly preserves the historical Document187 facts, including:

- semantic acceptance pending at creation time;
- import nonactivation state;
- original owner fields;
- prior pending-review flags.

Review190 supplies additive current acceptance.

Do not edit earlier records to make them appear retrospectively accepted.

## 7. Ten materialized rows are exactly ten rejections

The activation ledger contains:

- materialized rows: 10;
- current materialized disposition count: 10 rejection;
- uncertain: 0;
- confirmed same/derived: 0;
- reconciliation required: 0.

There is no disposition invention or reinterpretation during activation.

## 8. No scientific hard stop is triggered

The activation set contains no confirmed same/derived content decision.

Therefore:

`stop_for_prospective_scientific_decision = false`.

This is consistent with accepted Document187 semantics.

## 9. Source187 authority is strongly bound

Document189 binds:

- Review188;
- Document187 document;
- Document187 aggregate;
- original received owner input digest;
- canonical owner snapshot;
- accepted imported ten-row bundle;
- review definition;
- import lineage.

This is sufficient provenance for materializing the already accepted screen-level dispositions.

## 10. Exact source187 CI is bound

The activation checkpoint binds the successful Document187 publication state:

- head `2411877763a2bdcc71df8c61d184c9c214d43126`;
- run `38694502603`;
- validate job `116287801095`;
- completed/success.

This prevents activation from relying on an unreviewed or different import state.

## 11. Frozen queue and candidate lineage remain bound

Document189 reports verification of the accepted 6640-record queue bundle and exact rank/candidate bindings.

Queue candidate, packet candidate, and AI candidate are consistent for every target rank.

This preserves original queue identity.

## 12. Existing packet / AI / image provenance is retained

Each activation row remains linked to:

- accepted import row;
- frozen queue record;
- packet record;
- AI record;
- accepted definition;
- three existing bound image hashes.

No new visual evidence is introduced.

## 13. Thirty image hashes are bindings, not independent samples

The activation checkpoint correctly preserves the distinction between:

- 30 technical image-hash bindings;
- independent captures or independent scientific observations.

The 30 bindings must not be reported as 30 independent samples.

## 14. Correlation limitations remain in force

Ranks56..59 remain correlated because of reused source videos/configurations.

Separate owner answers and activation rows do not make these candidates statistically independent.

This limitation should remain in later reporting.

## 15. Visibility limitations remain historical context

Ranks54/56/58/59 retain previously disclosed visibility limitations.

Those ranks were nonetheless adjudicated by the owner as sufficient evidence and rejected as same/derived matches.

Review190 does not require another owner pass.

## 16. No new human input occurred

Document189 performs no new:

- human review;
- owner decision;
- rationale writing;
- replacement JSON;
- reconciliation.

This is appropriate for a pure activation checkpoint.

## 17. No new AI visual work occurred

There is no new:

- AI proposal;
- media inspection;
- asset generation;
- frame opening;
- visual model execution.

This keeps activation mechanical.

## 18. No new media processing occurred

Document189 performs no:

- decode;
- extraction;
- archive rehash;
- source-media mutation;
- packet regeneration.

This is correct.

## 19. Main and sibling activation roots are deterministic

Each private activation root contains:

- activation authority;
- successful source187 CI observation;
- ten activation rows;
- summary.

Total:

**13 files per root.**

Main and sibling match:

**13/13 byte-identically.**

This verifies serialization reproducibility only.

It is not another adjudication or independent rater.

## 20. Protected prior evidence remains unchanged

Document189 reports:

- protected prior roots: 63 unchanged;
- frozen artifacts: 13 unchanged;
- study configs: 17 unchanged;
- historical owner/source/helper pins unchanged.

This is appropriate additive preservation.

## 21. Output guard remains fail-closed

The unchanged private-output guard refuses:

- existing main output;
- existing sibling output;
- repository output;
- source-overlap output;
- symlink output.

These refusals protect against accidental overwrite or evidence mixing.

## 22. Immutable overwrite checks pass

Overwrite attempts against:

- preflight;
- activation authority;
- first activation row

raise `FileExistsError`.

This is correct immutable-ledger behavior.

## 23. No production-code or policy change occurred

Document189 reports no changes to:

- production code;
- tests;
- screening policy;
- environment;
- CI workflow;
- source roles;
- selector;
- seeds.

Therefore this checkpoint is a pure evidence/ledger transition.

## 24. Focused regression passes

The existing focused suite reports:

**77/77 passed.**

No new test failure is present.

## 25. Full regression baseline is appropriately retained

Document189 does not claim a new local full-suite run.

The accepted Document187 baseline remains:

**264/264 passed.**

Because Document189 makes no production-code/test/policy/environment changes, this is acceptable.

## 26. Fresh exact Document189 publication CI passes

Exact reviewed commit:

`a81bd9259478a8a49ad0783fdb777329791a99d5`

Fresh GitHub Actions run:

`38696814671`

is:

`completed / success`.

Validate job:

`116295204960`

is:

`completed / success`.

The validate job completed at:

`2026-10-15T07:09:37Z`.

There is no publication-CI blocker.

## 27. The activation may now be accepted additively

Before Review190, Document189 correctly reported:

- accepted batch06 current effective dispositions: 0;
- accepted current total: 50;
- prospective total after acceptance: 60;
- batch06 closed: false.

Review190 now supplies the additive acceptance authority.

The historical Document189 fields should remain unchanged.

## 28. Accepted current effective total is now 60

With Review190 acceptance:

- prior accepted total: 50;
- newly accepted batch06 effective dispositions: 10;
- new accepted current effective total: **60**.

This transition should be interpreted additively rather than by editing earlier aggregates.

## 29. Batch06 screen-level review is now closed

The complete accepted batch06 set is:

- reject: 10;
- uncertain: 0;
- confirmed same/derived: 0;
- hard stop: false.

No pair-specific semantic/reconciliation blocker remains.

Therefore batch06 screen-level review is closed.

## 30. No further owner input is required

Do not ask the owner to:

- reopen ranks50..59;
- repeat categorical decisions;
- provide prose;
- reconfirm AI proposals;
- repeat inspection;
- provide new license/admin attestations.

Batch06 human adjudication is complete.

## 31. AI-screen coverage remains 60/85

Activation does not change AI-screen coverage.

Current accepted AI-screen coverage remains:

**60/85**.

Therefore:

**25 highest-risk candidates remain not yet AI-screened.**

## 32. Next queue block may now begin at rank60

Review190 authorizes preparation of the next bounded frozen queue block beginning at:

`rank60`.

The preferred next block is:

`60..69`

unless a pre-existing frozen block-size rule specifies otherwise.

Do not skip ranks to improve apparent yield.

## 33. Next block must remain a separate checkpoint

Recommended sequence:

1. prepare packet block for ranks60..69;
2. review packet preparation;
3. perform AI visual proposal stage;
4. prepare categorical human handoff if required;
5. import/reconcile;
6. review import;
7. materialize separate activation;
8. review activation.

Continue the same bounded sequential discipline.

## 34. No scientific execution is authorized

Review190 does not authorize:

- source dry run;
- analysis freeze;
- locked target evaluation;
- classifier execution;
- risk-model execution;
- other scientific model stages.

Those remain blocked by later governance/data-audit gates.

## 35. Global data-audit scope is still incomplete

Closing batch06 does not establish:

- exhaustive OULU content independence;
- capture independence;
- transformed-region independence;
- cross-dataset independence;
- global lineage clearance.

The audit still has 25 highest-risk candidates not yet AI-screened.

## 36. Capture provenance remains uncertified

The screen-level content-lineage audit is not a capture-provenance certification.

This limitation remains explicit.

## 37. Software/CI success is not scientific readiness

The successful activation and CI demonstrate technical/governance consistency.

They do not independently establish model validity, dataset independence, or publication-level scientific readiness.

## Final disposition

**DOCUMENT 189 — ACCEPTED WITHOUT REWORK.**

**BATCH06 ADDITIVE ACTIVATION — ACCEPTED.**

**BATCH06 SCREEN-LEVEL REVIEW — CLOSED.**

**ACCEPTED CURRENT EFFECTIVE SCREEN-LEVEL TOTAL = 60.**

**AI-SCREEN COVERAGE = 60/85.**

**25 HIGHEST-RISK CANDIDATES REMAIN NOT YET AI-SCREENED.**

**NO FURTHER OWNER INPUT IS REQUIRED FOR RANKS50..59.**

**PREPARATION OF THE NEXT FROZEN QUEUE BLOCK BEGINNING AT RANK60 IS AUTHORIZED.**

Historical pending/nonactivation fields remain immutable creation-time facts. Review190 is the additive acceptance authority.

Do not proceed to research-model execution or later scientific stages until their separate audit/governance gates are satisfied.
