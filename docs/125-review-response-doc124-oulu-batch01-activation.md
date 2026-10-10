# Response to Review 124: Additive Batch-01 Activation

Date: 2026-10-10
Base commit: `c7be795`
Review: [Document 124](124-review-doc123-oulu-owner-acceptance.md)

Review 124 accepts the recorded owner decision and reports the exact CI blocker
cleared. This checkpoint activates batch 01 through a separate immutable record
and current effective ledger. No owner acceptance or human JSON is requested again.

## Completion Criteria

- Verify exact proposal CI `38015159060` / `ba2add2` and owner-acceptance CI
  for `6e05787` are completed/success through live GitHub API observations.
- Bind existing owner acceptance, Pair-5 reconciliation and nine agreements
  accepted by Review 120; preserve all original records and pending CI snapshot.
- Create ten additive current effective rows, each scoped screen-level rejection,
  retaining original dispositions, historical disagreement and source-row hashes.
- Verify readback, deterministic serialization replay, overwrite refusal and
  unchanged protected artifacts; retain blocked scientific gates.
- Publish activation for checkpoint review before starting the remaining75 pairs.

## Actual Results

Checkpoint **1.5M activates and closes batch 01 at screen level only**.
The new current effective ledger contains **10 rejected_false_positive,
0 uncertain, 0 confirmed same/derived content**. No repeated owner acceptance,
new human inspection, new visual judgment or replacement human JSON is invented.

Live cache-disabled GitHub REST checks verify both exact prerequisites:

| Commit | Run / check | Result | Completed UTC |
| --- | --- | --- | --- |
| `ba2add2ffcd9a562f89fa5b2cdd141b207021e12` | 38015159060 / 114103685821 | completed / success | 2026-10-10T02:06:33Z |
| `6e05787d4b939a29094192d904be20c967304c7c` | 38015828271 / 114105721122 | completed / success | 2026-10-10T02:08:45Z |

The new CI observation records include head SHA, check/run IDs, result, completion
time, API HTTP date and observation timestamp. This does not replace or edit the
earlier pending snapshot from Document 123.

## Additive Authority and Provenance

Nine current rows inherit the screen-level AI/human agreements explicitly accepted
by Review 120. Pair 5 inherits the separately bound explicit owner acceptance
after exact CI success. The activation binds Review 124, Document 123, owner
decision/summary, historical CI snapshot, Pair-5 proposal, original owner JSON,
AI/human pair bundles, accepted handoff definition and all 13 frozen artifacts.

Every new row retains original AI/human/effective dispositions, historical
disagreement and reconciliation-required flags, original pair hashes and its
acceptance authority. Current `reconciliation_required` is false; the original
Pair-5 disagreement remains true in history. The original imported ledger still
contains its historical nine rejections/one uncertain. The new current ledger,
not a rewrite of that history, represents the accepted ten screen-level rejections.

Private output roots:

```text
/mnt/e/FAS-private/artifacts/phase1/oulu_batch01_activation_v1
/mnt/e/FAS-private/artifacts/phase1/oulu_batch01_activation_rerun_v1
```

Each contains `activation.json`, `ci_success_observations.json`, ten pair rows
and `summary.json`: **13 files**, byte-identical under serialization replay.
Replay is not a second independent adjudication or a second live CI result.
The existing immutable writer refuses overwrite. Readback checks all ten current
rows and authority mappings. Protected snapshots of original AI/human ledgers,
proposal, owner decision/pending snapshot, packet/handoff roots and 13 frozen
files remain unchanged. The 67 accepted handoff files still match their accepted
preparation rerun. Pair identities and detailed evidence stay outside Git.

[Public aggregate](../results/phase1/oulu-batch01-activation-v1.json) bindings:

- Activation SHA-256: `14b6c969c30a5f817f030322507109ab0ef2eae2474ef9cd15b090ba193028a5`.
- Successful-CI observations SHA-256: `65825fd7466f61e7f22d4914394c96cee420d3383a53ffc001a2099875bc7a62`.
- Current pair bundle SHA-256: `308c7f78695b5449ddad84e63a5c76cb50a17ab5798271e3bbc75d636cf0d245`.
- Summary SHA-256: `f822d562a25aead825cf584de7489f9f14a1d64283b1b4093026f37e0da9b876`.

## Verification and Stop Point

Focused regression: **52/52**, zero failures/errors (4.182 seconds). Actual
activation checks cover exact live CI, accepted source bundles, authority for all
ten rows, readback, immutable replay/refusal, unchanged protected artifacts and
stage gates. Production code/tests/policies/environment are unchanged. The full
239-test regression is not rerun locally for this data/documentation-only step;
fresh publication CI runs the standard suite/gates.

`effective_reconciliation_activated=true` and
`batch01_accepted_reconciled_disposition_state=true` now describe the additive
current batch state. This closes only the observed rendered-content screening
relationships reviewed in these ten pairs. It does not prove independent capture,
full-video independence, absence of every shared source or global OULU lineage
clearance. No sample is removed, reassigned or repaired; roles/selector/seed and
screening are unchanged.

**Stop for review of this published activation checkpoint before the next batch.**
The remaining75 highest-risk pairs are not started. After approval, the next
bounded batch must follow frozen queue order, without outcome-dependent skipping
or threshold tuning. No further acceptance or human JSON for batch 01 is needed.
Core data-audit, source-dry-run, analysis-freeze and locked-evaluation remain
blocked; model authorization and scientific readiness remain false. No new media
extraction/decode, detector/model, training or target evaluation occurs here.