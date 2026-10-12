# 142 — Review of Document 141: OULU Batch-03 Owner Human-Review Import

Date: 2026-10-12  
Repository: `lathevinh/fas`  
Reviewed commit: `ede6e124704e15edc6930de4060c03025c404825`  
Reviewed document: `docs/141-oulu-batch03-human-review-import.md`

## Verdict

**DOCUMENT 141 — ACCEPTED FOR HUMAN-IMPORT SCOPE.**

**CHECKPOINT 1.5V OULU BATCH-03 OWNER HUMAN-REVIEW IMPORT — ACCEPTED WITHOUT REWORK.**

**BATCH-03 ADDITIVE EFFECTIVE ACTIVATION — AUTHORIZED AS THE NEXT STEP, BUT NOT YET COMPLETED.**

Document 141 correctly imports the owner's actual batch-03 human-review JSON for frozen ranks 20–29, preserves the existing AI/human evidence histories, reports ten AI/human agreements with no disagreement or confirmed-content case, and deliberately leaves effective activation at zero.

The next required step is a separate additive current-ledger activation for these ten agreed screen-level rejections. No repeat human review or replacement JSON is required.

## 1. Genuine owner-human input is present

The submitted JSON contains:

- ten explicit pair answers;
- original queue ranks 20–29;
- owner-human reviewer declaration;
- personal bound-evidence inspection attestation;
- timestamped submission;
- binding to the accepted batch-03 review definition and assets.

This resolves the human-review blocker from the prior AI-proposal checkpoint.

## 2. AI and human outcomes agree on all ten pairs

Current imported comparison result:

| Outcome | Count |
|---|---:|
| Human `rejected_false_positive` | 10 |
| AI/human agreements | 10 |
| AI/human disagreements | 0 |
| Human confirmed same/derived | 0 |
| Scientific hard stop | No |

There is therefore no pair requiring disagreement reconciliation at this checkpoint.

## 3. Effective activation is correctly still zero

Document 141 correctly keeps:

- `effective_dispositions_activated = 0`;
- `batch03_accepted_reconciled_disposition_state = false`;
- `comparison_state_is_activated_current_ledger = false`.

The validator's comparison field is not silently treated as a current effective ledger.

This is correct provenance handling.

## 4. The repeated generic human rationale is a real limitation

All ten human rationale fields contain the same general text.

Accordingly:

- `unique_human_rationale_count = 1`;
- these are not ten independently detailed pair-specific human rationales.

This limits what can be claimed from the human review.

It does **not**, however, require a repeat review at this checkpoint because:

1. all ten human dispositions agree with the previously recorded pair-specific AI proposals;
2. there is no disagreement requiring pair-specific reconciliation;
3. there is no human confirmation of same/derived content;
4. every human answer remains separately bound to its pair and reviewed assets;
5. the original human text is preserved rather than rewritten or expanded by AI.

The rationale duplication must remain disclosed as a quality limitation.

## 5. Human review is not fully blinded independent adjudication

The accepted handoff started with:

- blank disposition fields;
- blank rationales;
- no AI answer pre-selected.

However, AI notes were available in collapsed sections.

That is better than prefill but is not full blinding.

Therefore the project must not claim:

- blinded independent second review;
- inter-rater reliability;
- independently validated disposition accuracy.

The appropriate description is owner-human review/confirmation with separately preserved AI proposals.

## 6. Correlated foreground limitation remains

The correlation disclosed in the batch-03 AI review is not erased by human agreement.

Repeated/reused foreground configurations must not later be counted as independent statistical replicates or independent accuracy measurements.

Pair-level candidate decisions may remain separate because each is separately bound to its queue rank, packet and assets.

## 7. Rank 20–29 adapter is acceptable

The importer requires:

- accepted definition ranks exactly 20–29;
- exactly ten human rows;
- integer ranks only;
- the exact unique set 20–29.

It then:

1. maps queue rank `r` to `r - 20` in memory;
2. invokes the unchanged accepted human validator;
3. restores `+20` afterward;
4. explicitly sets `effective_disposition_activated = false`.

The original input and published definition are not mutated.

This is a reasonable compatibility adapter.

## 8. Important fail-closed bindings are present

Before import, the implementation verifies:

- published handoff definition/page/summary hashes;
- accepted human renderer/validator code hashes;
- exact successful handoff CI;
- scoped owner import authorization;
- protected evidence snapshots;
- accepted AI report/definition/summary and ten AI pair rows;
- ten packet hashes;
- all required reviewed-image hashes;
- original owner JSON digest.

This is a strong import boundary.

## 9. Original owner input is preserved

The original human JSON bytes and SHA-256 remain unchanged.

The stored `human_input.json` is canonical serialization of the parsed content, not falsely claimed as byte-identical serialization.

The document reports that every original answer, rationale and queue rank matches after import.

This is correct evidence handling.

## 10. Reimport reproducibility is strong

The private import ledger contains:

- lineage;
- canonical human input;
- ten pair records;
- summary.

Total:

**13 files.**

Independent reimport reproduces:

**13 / 13 byte-identically.**

Existing-output reuse is refused and leaves the accepted output unchanged.

This is appropriate immutable-import behavior.

## 11. Protected evidence remains unchanged

Document 141 reports:

- 16 protected roots unchanged;
- all 13 frozen artifacts unchanged;
- batch-01 / batch-02 historical and current records unchanged;
- batch-03 packets, AI review and handoff unchanged.

No source role, selector, seed or screening threshold changes occur.

This is correct.

## 12. Local regression evidence is strong

Reported local testing:

- focused regression: **58/58 passed**;
- full regression: **245/245 passed**;
- zero failures/errors.

The full suite increase is appropriate because a new batch-03 import adapter/test was introduced.

## 13. Fresh CI for the exact Document-141 commit passes

Fresh GitHub Actions for exact commit:

`ede6e124704e15edc6930de4060c03025c404825`

completed successfully.

Run:

`38239703977`

with validate job:

`114779001085`

completed successfully.

The job passes:

- FFmpeg setup;
- model-free screening dependencies;
- synthetic regression;
- canonical schema validation;
- unavailable-stage fail-closed checks;
- legacy-stage rejection checks.

There is therefore no CI blocker on this import checkpoint.

## 14. Browser verification remains a declared limitation

The prior integrated-browser 403 means browser interaction was not independently certified by the automation environment.

The supplied JSON nevertheless demonstrates that an owner review/export artifact exists and is correctly bound for import.

This does not independently authenticate:

- human authorship;
- exact browser behavior;
- desktop/mobile UI fidelity.

Document 141 correctly avoids those claims.

## 15. No repeat human review is required

Because all ten AI/human outcomes agree and no confirmed-content case exists, I do not require:

- a replacement JSON;
- a second review of ranks 20–29;
- pair-specific reconciliation records.

A repeat review would only become necessary if later evidence reveals binding corruption or an explicit independent-blinded-adjudication requirement is introduced.

## 16. Additive activation is now authorized

The next bounded checkpoint may create a separate current batch-03 ledger with expected state:

| Effective disposition | Expected count |
|---|---:|
| `rejected_false_positive` | 10 |
| `uncertain_insufficient_evidence` | 0 |
| `confirmed_same_content_or_derived_lineage` | 0 |

The activation must be additive.

It must not rewrite:

- original AI proposals;
- owner JSON;
- human-import rows;
- historical comparison state;
- prior batch records.

## 17. Ranks 30+ remain paused until activation is reviewed

The correct sequence is:

1. create batch-03 additive activation/current ledger;
2. bind Document 141 and exact successful import CI;
3. preserve all historical activation=false records;
4. publish the activation checkpoint;
5. review that checkpoint;
6. only then prepare the next fixed queue batch beginning at rank 30.

This matches the discipline used for batches 01 and 02.

## 18. Scope remains screen-level only

Even after activation, these ten outcomes may only be described as accepted rejection of the observed perceptual-screen rendered-content relationship.

They do not prove:

- independent capture provenance;
- full-video independence;
- absence of all shared source material;
- absence of partial/shifted/transformed overlap;
- global OULU lineage clearance.

## 19. Broader audit remains incomplete

There are still:

- 55 highest-risk candidates not yet AI visually reviewed;
- many additional cross-role candidates;
- the much larger unresolved non-exact population;
- future cross-dataset lineage checks.

Therefore content-lineage adjudication remains incomplete.

## 20. Scientific/model gates remain blocked

This checkpoint does not authorize:

- data-audit completion;
- source-dry-run;
- analysis freeze;
- locked target evaluation;
- detector/model execution;
- target-domain experiments;
- scientific readiness.

These gates remain fail-closed.

## Final disposition

**DOCUMENT 141 — ACCEPTED FOR HUMAN-IMPORT SCOPE.**

**CHECKPOINT 1.5V OULU BATCH-03 HUMAN IMPORT — ACCEPTED WITHOUT REWORK.**

Current imported result:

**10 human rejections, 10/10 AI-human agreements, 0 disagreements, 0 confirmed same/derived, 0 effective activations.**

The repeated generic human rationale and non-fully-blinded review remain disclosed limitations, but they do not block bounded screen-level activation because no disagreement or confirmed-content case exists.

**Required next step: create a separate additive batch-03 activation record for 10 screen-level rejections. Do not start ranks 30+ until that activation checkpoint is published and reviewed.**
