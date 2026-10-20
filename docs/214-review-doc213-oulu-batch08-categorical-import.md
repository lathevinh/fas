# 214 — Review of Document213: OULU Batch08 Categorical Import

Date: 2026-10-20

## Verdict and review basis

Reviewed commit: `4d819c7a350cc30955723fbda57af589148a40e5`.

Reviewed [Document213](213-review-response-doc212-oulu-batch08-categorical-import.md), its [aggregate](../results/phase1/oulu-human-review-import-batch08-v1.json), the complete new importer, added test and existing source bindings, Review212 and fresh exact213 CI.

**DOCUMENT213 — ACCEPTED WITHOUT REWORK FOR CATEGORICAL IMPORT / RECONCILIATION SCOPE.**

**TEN IMPORTED OWNER CATEGORICAL REJECTIONS FOR EXACT RANKS70..79 — ACCEPTED AT THIS REVIEW STAGE.**

**NEW BATCH08 AGREEMENTS10 / DISAGREEMENTS0 / UNRESOLVED RECONCILIATION REQUIREMENTS0 ARE ACCEPTED AS THE REPORTED VALIDATED IMPORT RESULT.**

**NEXT AUTHORIZED STEP: SEPARATE ADDITIVE BATCH08 EFFECTIVE ACTIVATION CHECKPOINT; EFFECTIVE TOTAL REMAINS70 UNTIL THAT CHECKPOINT IS REVIEWED AND ACCEPTED.**

This Windows reviewer inspected public implementation and tests and checked public hashes/CI. The private raw export, ten import rows, source assets, preflight and verification were unavailable here. Acceptance of actual private execution and owner decisions relies on the reported validated import and prior accepted owner attestation, not a private-byte rerun, independent human authentication or new visual adjudication by this reviewer. No such independent verification is claimed.

## Authority and historical state

Review212 explicitly permits separate import/reconciliation for exact70..79 and requires a later activation review.213 implements that authority with exact Review208/210/212 and source211 CI bindings, strict integer ranks and import=true while activation/model/scientific flags remain false.

The ten imported rows retain activation=false, checkpoint-review-pending, semantic-acceptance-pending and counts-as-accepted-effective=false. These are correct creation-time facts and remain immutable after this review. Review214 is later additive acceptance, not authority to rewrite213 or older209/211 prohibitions.

No new disagreement requires adjudication on the reported actual input. Prior batch07 historical disagreement1/unresolved0 remains separately preserved. New batch08 zero disagreement must not reset the historical count to0 or be presented as evidence that the earlier AI and owner agreed.

## Implementation assessment

The importer checks the receipted byte size and SHA256 before parsing the owner payload. Its strict parser rejects duplicate keys recursively, nonfinite constants/overflowing floating-point numbers and non-object JSON. It preserves raw bytes in place and writes a separately identified structured all-field copy; canonical serialization is not misrepresented as the original raw export.

Categorical validation requires exact version/type and definition/authority bindings, an identified human reviewer with personal-inspection attestation, a timezone-aware zero-offset timestamp, ten unique integer ranks and exact packet/AI/formal/queue/three-asset references. Booleans are checked strictly; missing or untouched sufficiency cannot silently become uncertainty.

Disposition and row/aggregate stop are rederived from the strict three-way rules, then compared with all reported outcomes and flags. Confirmation remains a scientific-stop condition. Unknown owner fields are preserved unless they collide with importer-derived metadata, in which case import fails rather than overwriting them.

AI proposals and human dispositions remain distinct. Disagreement is derived from their actual dispositions; a conservative comparison state on disagreement is not substituted for the original human result or treated as activation. Actual213 reports ten derived rejections, ten agreements, no uncertainty/confirmation and no reconciliation requirement.

The complete import path checks the accepted receipt/private preflight, additive209 correction, actual handoff definition/page/summary, AI/formal ten-row bundles, full6640-record frozen queue, candidate/rank cross-bindings and both copied/original asset hashes before writing outcomes. Source preservation and raw/queue integrity are checked again after output writes. Output guard and immutable writer are reused.

No blocking implementation defect was identified for this receipted input and authorized scope. Strict structural validation and source integrity do not independently prove personal inspection, ownership, capture independence or scientific correctness.

## Tests and public evidence

The diff adds one test method containing meaningful positive/negative cases: all three mappings, stop propagation, disagreement preservation, strict ranks/types/attestations/UTC metadata, outcome/stop mismatches, binding drift, metadata collisions, recursive duplicate keys, nonfinite JSON, receipt-before-parse, symlink input and unsafe outputs. Successful validation also checks original fields and nonactivation.

The new method exercises validators and refusal paths; it is not a full synthetic successful CLI import with all private source trees. Actual two-CLI13/13 execution, preservation/provenance postchecks and authority probes are reported private evidence. The report and tests together support this acceptance without claiming that unit tests alone prove private execution.

Four checked public SHA256 bindings match after Windows CRLF-to-repository-LF normalization:

| Record | SHA256 |
|---|---|
| Review212 | `e64484d0ef0f4a1fab48b8c2a7580f45097b2743bdac39e654726cad37779781` |
| Accepted211 aggregate | `a394a05c412ffe37f38c9951d5aa2063987b17a806a24fc82bdab676aa315380` |
| Importer | `c12b12299314357737831d33def77f32c3e5ee72a708d01bc7d9bfabc3870b63` |
| Updated test file | `e4511827dbeffb1048b562be75fb542de8821a2c7355346114a5a352bd2bae1c` |

Reported local results are new test1 passed, focused83/83 and full270/270 after the final code edit. The full run is explicitly new213 execution, not inherited269. This reviewer did not locally rerun those suites or independently compare the entire prior module AST.

### Fresh exact213 CI

GitHub API observations independently confirm:

| Item | Verified result |
|---|---|
| Exact head | `4d819c7a350cc30955723fbda57af589148a40e5` |
| [Run39351736047](https://github.com/lathevinh/fas/actions/runs/39351736047) | completed / success |
| [Validate118397259824](https://github.com/lathevinh/fas/actions/runs/39351736047/job/118397259824) | completed / success |
| Job completion | `2026-10-20T01:09:10Z` |
| Listed steps | 12/12 success |

Synthetic regression, schema and fail-closed stage checks passed. No fresh213 CI blocker remains. CI metadata is not used to infer private results or exact regression counts.

## Preservation and limitations

213 reports86 prior roots,13 frozen files and17 configs preserved; owner bytes/all fields and historical flags unchanged;13/13 main/replay records identical; four CLI output refusals, two prior-authority refusals and three immutable overwrite refusals. Original owner bytes were not overwrite-probe targets. These private checks were not independently repeated here.

The aborted queue-snapshot assumption was corrected before output materialization by checking the canonical accepted queue summary and full bundle. The report describes no weakening of evidence hashes or rewriting/regeneration of source evidence. No rework is identified on that account.

Serialization equality proves deterministic record production, not a second human judgment or independent scientific replication. Agreement counts are categorical comparison results, not accuracy estimates or interrater reliability. Stop=false is not global lineage clearance or scientific readiness.

## State after this review

| Measure | State |
|---|---|
| Accepted effective screen-level total | 70/85, unchanged |
| Accepted owner categorical outcomes including batch08 | 80/85 at semantic-review level; ten newly accepted outcomes remain inactive |
| Accepted AI-screen coverage | 80/85 |
| Batch08 human / AI dispositions | 10 reject /10 reject |
| New batch08 disagreements / unresolved requirements | 0 /0 |
| Historical prior disagreement / unresolved reconciliation | 1 /0 preserved |
| New effective activations | 0 |
| Not yet AI-screened | 5, ranks80..84 |
| Batch08 complete screen-level workflow | Not closed |

## Bounded activation authority and stop boundary

After Review214 is committed, prepare a separate immutable additive activation for exact70..79. Bind this review, exact accepted213 document/aggregate/CI, receipt/raw/canonical input, lineage and exact ten-row bundle, plus source AI/formal/packet/queue/image provenance. Materialize only the ten accepted categorical rejections; do not re-adjudicate, regenerate assets or replace original human answers.

Preserve all historical pending/nonactivation flags and historical disagreement1/unresolved0. Activation records must explicitly distinguish the currently accepted effective total70 from prospective80 and remain activation-checkpoint-review-pending; do not count them as accepted current effective dispositions before that checkpoint is formally reviewed. Verify deterministic record replay, preservation and exact new publication CI, then stop for activation review.

No new owner input, explanatory human prose or duplicate visual screening is required. A binding mismatch or credible confirmed cross-role finding requires stopping under existing rules, not silently repairing evidence or continuing.

This review does not itself activate dispositions, close batch08, authorize ranks80..84 or continue other datasets. Source dry run, research-model execution, analysis freeze and locked evaluation remain blocked. Scientific readiness remains false.
