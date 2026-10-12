# 135 — Review of Document 134: OULU Batch-02 Additive Activation

Date: 2026-10-12  
Repository: `lathevinh/fas`  
Reviewed commit: `0ec57d5919cdb9f29eac958c879b10bcede5e113`  
Reviewed document: `docs/134-review-response-doc133-oulu-batch02-activation.md`

## Verdict

**DOCUMENT 134 — ACCEPTED.**

**CHECKPOINT 1.5R OULU BATCH-02 ADDITIVE CURRENT-LEDGER ACTIVATION — ACCEPTED WITHOUT REWORK.**

**BATCH 02 IS NOW CLOSED AT SCREEN LEVEL: 10 REJECTED, 0 UNCERTAIN, 0 CONFIRMED SAME/DERIVED.**

The activation follows the additive provenance model required by Review 133. It creates a new current effective ledger for ranks 10–19 without rewriting the AI proposal ledger, human-import ledger, owner JSON or historical activation state.

With this review acceptance, the next frozen queue batch may now be prepared. This does not complete the OULU lineage audit or authorize model execution.

## 1. Activation scope is exactly correct

Document 134 activates exactly queue ranks 10 through 19.

The current batch-02 state is:

| Effective disposition | Count |
|---|---:|
| `rejected_false_positive` | 10 |
| `uncertain_insufficient_evidence` | 0 |
| `confirmed_same_content_or_derived_lineage` | 0 |

It also reports:

- `effective_dispositions_activated = 10`;
- `batch02_accepted_reconciled_disposition_state = true`.

This matches the authority granted by Review 133.

## 2. The activation is genuinely additive

The strongest aspect of this checkpoint is that it does not retroactively rewrite history.

The earlier human-import checkpoint remains:

- effective activations: 0;
- batch-02 accepted reconciled state: false;
- every historical row still `effective_disposition_activated = false`.

The new current ledger is separate from those historical records.

This is the correct provenance model.

## 3. AI and human histories remain preserved

The checkpoint reports that:

- original AI proposal records are unchanged;
- original human-import records are unchanged;
- original owner JSON bytes are unchanged;
- submitted human rationales are unchanged;
- packet and handoff records are unchanged.

The current rows carry forward historical AI/human/comparison state rather than pretending the effective decision existed earlier.

This is scientifically and procedurally correct.

## 4. No hidden reconciliation is introduced

Batch 02 had:

- AI rejection proposals: 10;
- human rejections: 10;
- disagreements: 0;
- confirmed same/derived: 0.

Therefore no pair-specific reconciliation step was required.

Document 134 does not fabricate one.

This is correct.

## 5. The generic human-rationale limitation is properly preserved

The ten human rationales remain identical/general.

Document 134 continues to disclose that:

- this is not ten independently detailed pair-specific human rationales;
- human review was not fully blinded;
- no inter-rater reliability is claimed;
- no disposition-accuracy validation is claimed.

This limitation remains real, but Review 133 already determined that it does not block narrow screen-level activation when all ten human outcomes agree with the separately recorded pair-specific AI proposals and no disagreement exists.

I agree with preserving this as a limitation rather than reopening the batch.

## 6. Activation authority is adequately bound

The activation binds:

- Review 133;
- Document 132 and its public import report;
- exact successful import CI;
- original human JSON;
- review definition/assets;
- accepted AI report;
- AI and human pair bundles;
- import lineage/summary;
- immutable writer;
- all frozen artifact hashes.

This is an appropriate authority chain for an additive current ledger.

## 7. Current rows retain source authority and history

Each new row reportedly binds:

- exact AI pair digest;
- exact human pair digest;
- packet digest;
- Review 133 authority;
- activation digest.

It also retains:

- historical AI disposition;
- historical human disposition;
- historical comparison disposition;
- previous activation=false state;
- disagreement/reconciliation flags.

That is the right structure for an auditable current decision record.

## 8. Reproducibility and immutability are adequate

The activation export contains:

- activation record;
- successful-CI observation;
- ten current pair rows;
- summary.

Total:

**13 files.**

Serialization replay is:

**13 / 13 byte-identical.**

Existing-record overwrite is refused.

This demonstrates deterministic record generation and immutable output handling.

It does not constitute independent re-adjudication, and Document 134 correctly avoids that claim.

## 9. Protected prior evidence remains unchanged

Twelve protected roots remain unchanged, including:

- batch-01 historical/current records;
- batch-02 packets;
- batch-02 AI proposals;
- human handoff;
- owner JSON;
- human import;
- frozen artifacts.

No role, selector, seed or screening threshold changes occur.

This is correct.

## 10. Focused testing is sufficient for this activation-only checkpoint

Document 134 reruns:

- focused OULU regression: **55/55 passed**.

The prior accepted import checkpoint had:

- full regression: **242/242 passed**.

The full local suite was not rerun here because no production code, test, policy, environment or CI workflow changed.

For this record-only activation checkpoint, that is acceptable.

## 11. Fresh CI for the exact activation commit passes

Fresh GitHub Actions for exact commit:

`0ec57d5919cdb9f29eac958c879b10bcede5e113`

is:

- status: `completed`;
- conclusion: `success`.

The exact job successfully completes:

- checkout/setup;
- FFmpeg installation;
- model-free screening dependencies;
- synthetic regression suite;
- canonical schema validation;
- unavailable-stage fail-closed checks;
- legacy-stage rejection checks.

There is therefore no CI blocker on activation.

## 12. Public evidence cannot independently inspect private current rows

The detailed ten current rows remain private.

The public repository exposes their bundle hash, counts, authority checks and aggregate state, not the private row bodies.

Therefore this review accepts the activation/provenance mechanism based on the published bindings and prior accepted AI/human evidence; it does not claim independent reconstruction of every private current row.

This is an inherent private-evidence limitation, not a newly introduced defect.

## 13. Batch 02 is now formally closed at the intended scope

Batch 01 remains:

- 10 screen-level rejections.

Batch 02 is now:

- 10 screen-level rejections.

Therefore there are currently:

**20 resolved screen-level perceptual-screen candidates across batches 01–02.**

These are resolved candidate relationships, not “20 cleared videos” and not proof of independent acquisition.

## 14. Queue ranks 20+ may now proceed

Document 134 correctly kept ranks 20+ paused until this activation was reviewed.

With this review acceptance, the project may now prepare the next fixed frozen queue batch beginning at rank 20.

The same rules remain mandatory:

- frozen queue order;
- no outcome-dependent skipping;
- no threshold retuning;
- no role repair;
- no sample deletion;
- no seed retry;
- no silent selector changes.

A confirmed same/derived cross-role case remains an explicit scientific hard stop.

## 15. Do not interpret 20/85 coverage as lineage clearance

Current highest-risk AI review coverage is:

- 20 / 85 resolved through the current workflow;
- 65 highest-risk candidates remain not yet AI visually reviewed.

Beyond these, many other cross-role/non-exact candidates and later cross-dataset checks remain.

Therefore:

`content_lineage_adjudication_complete = false`

remains correct.

## 16. Scope remains screen-level only

The ten activated batch-02 outcomes establish only:

> accepted rejection of the observed perceptual-screen rendered-content relationship.

They do not establish:

- independent original capture;
- full-video independence;
- absence of all common source material;
- absence of shifted/partial/transformed overlap;
- global OULU lineage clearance.

## 17. Scientific/model gates remain correctly blocked

The checkpoint does not authorize:

- data-audit completion;
- source-dry-run;
- analysis freeze;
- locked target evaluation;
- detector/model execution;
- target-domain experiments;
- scientific readiness.

These stages must remain fail-closed.

## Final disposition

**DOCUMENT 134 — ACCEPTED.**

**CHECKPOINT 1.5R OULU BATCH-02 ADDITIVE ACTIVATION — ACCEPTED WITHOUT REWORK.**

Batch 02 is now formally closed at screen level:

**10 rejected, 0 uncertain, 0 confirmed same/derived.**

Together, batches 01–02 now contain **20 accepted screen-level rejections**.

**The next frozen queue batch beginning at rank 20 may now be prepared.**

This acceptance does not imply global OULU lineage clearance, capture-provenance certification, completion of the data audit or authorization to run the research models.
