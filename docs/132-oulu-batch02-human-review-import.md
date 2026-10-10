# Batch02 Bound Owner-Human Review Import

Date: 2026-10-10
Base commit: `d92ff056e4adafd67a5ecf91233e01b9eace2a41`
Prior handoff: [Document131](131-review-response-doc130-oulu-batch02-human-handoff.md)

## Authority And Prospective Criteria

The owner supplied the private batch02 human-review JSON and explicitly requested
continuation. This is direct authorization for checkpoint1.5Q import only, not an
external review132 verdict or acceptance of scientific/effective closure. No new
formal external review was present on origin/main when this import started.

- Verify the published definition/page/summary and exact successful handoff CI.
- Preserve the genuine input bytes, reviewer attestation and every submitted
  rationale; validate all ten unique integer ranks10..19 and exact image/packet
  bindings without rewriting human answers.
- Reuse the pinned human validator through a local-rank adapter. Restore original
  ranks in outputs; preserve disagreement as uncertain and confirmed content as
  scientific hard stop. No automatic effective activation, even on agreement.
- Write a new immutable private import ledger and independent replay; verify
  input/readback hashes, overwrite refusal, prior evidence/frozen inputs and gates.
- Run focused/full regression for the new importer and test. Publish counts/hashes
  and stop for checkpoint review before any additive activation or queue ranks20+.

Authorship is an explicit owner-human attestation, not independent authentication
or interrater reliability. Actual browser export remains owner-reported, not
independently verified by the integrated browser.

## Actual Import Results

The provided path was normalized by adding the missing leading slash, without
changing the owner file. It contains a declared owner-human reviewer, personal
bound-evidence attestation and ten explicit answers timestamped
`2026-10-10T09:27:15.569Z`, bound to the published batch02 definition.

| Item | Result |
|---|---:|
| Original queue ranks imported | 10..19 |
| Human `rejected_false_positive` answers | 10 |
| AI/human agreements / disagreements | 10 / 0 |
| Human confirmed same/derived / scientific hard stop | 0 / false |
| Unique submitted rationale texts | 1 |
| New effective dispositions activated | 0 |
| Private import ledger files | 13 |
| Independent reimport byte-identical | 13 / 13 |
| Focused regression | 55 passed |
| Full regression | 242 passed, 0 errors/failures |

All ten owner rationale fields contain the same general explanation of foreground
and scene differences at sampled slots. They are nonblank and satisfy the existing
schema, but **are not ten independently detailed pair-specific human rationales**.
No owner rationale was edited, expanded or replaced with the AI's more specific
private descriptions. This limitation is preserved for checkpoint review, not
silently repaired by the assistant. AI/human agreement alone is not proof of
judgment accuracy, independent raters or capture independence.

The original JSON bytes and digest remain unchanged. The imported `human_input.json`
is the existing writer's canonical serialization of the same parsed content,
not a claim of byte identity with the differently ordered original JSON. Every
original per-pair field equals its imported field; original ranks10..19 survive.
Thirty asset hashes, packet hashes, published definition/page/summary, accepted
AI bundle and pinned renderer/validator hashes all verify.

The adapter creates temporary in-memory local ranks0..9 only when invoking the
unchanged pinned validator and restores ranks10..19 afterward. It never mutates
the input or published definition. Synthetic tests verify no mutation, exact
rank completeness/uniqueness/integer checks, wrong-rank/hash/asset/rationale/
attestation rejection, human uncertainty and confirmed-content hard stop.

Rows retain the validator's comparison field `effective_disposition`, but this
is **not an activated current ledger**. Each row also explicitly has
`effective_disposition_activated = false`; summary has zero activated dispositions
and `batch02_accepted_reconciled_disposition_state = false`.
If disagreement appears in a future separately authorized import, the validator
preserves both statements with uncertain comparison state. Human confirmation
also triggers the scientific hard stop. No automatic sample removal or role repair.

## Exact Prerequisite And Evidence

Fresh observed handoff CI for exact commit
`d92ff056e4adafd67a5ecf91233e01b9eace2a41`, run `38041197817`, check
`114181622105`, is completed/success at `2026-10-10T09:24:05Z`.
This successful prerequisite is newly bound in preflight/lineage; it does not
substitute for CI of the newly pushed import checkpoint.

Ledger:lineage,canonical human input,ten pair rows,summary. Independent reimport
validates the same genuine input again and writes a fresh13-file root; all files
match byte-for-byte. This is reproducible import, not independent re-review.
Existing output returns exit1 and remains unchanged. Readback compares every
answer/rationale/rank with the original input and verifies the bound assets.

Eleven protected-root snapshots remain unchanged, including all batch01 historical
and current records, batch02 packets/AI proposals, human handoff and frozen13.
The batch02 handoff now has34 files because the owner JSON was supplied alongside
the original33 prepared files; the original33 files are unchanged. No preparation
runner, visual policy, human validator, environment or CI workflow was changed.
Only the separate import adapter, one existing test, this document, aggregate
report and README are published.

The [aggregate report](../results/phase1/oulu-human-review-import-batch02-v1.json)
contains counts/hashes only. The owner JSON, reviewer identifier, candidate rows,
images and detailed private records remain outside Git.

| Record | SHA256 |
|---|---|
| Original owner JSON | `6dce069e4a234c9447a0d60ba7731efd4786933a1d07022d52c42afb84f072f8` |
| Import adapter | `9d6101a7f80411b2d6cb8fe94c3b5421dc9e66e07b1fea3a5363e61386dc62da` |
| Private preflight | `47efb5b4f47b7247709c44a4ef0f25ec300f92f0d8a13a7287609c81e72ccdbf` |
| Private lineage | `bbcbb8e45378e12f7315b2d66417357e905515ea748e083ce1eff8788a08d13c` |
| Human pair bundle | `b37ae3f2ce26795db13cf205c2f292e63fe2be391ee0057a487d414f5ca6911a` |
| Private summary | `e75897ddfc71f05f1339ee3c11b3cd454328ae2d1437fa1b74787e01b39c8a4c` |
| Private verification | `48e695cf70d7e331e43f9311afe526ef4a4506015d84f7d401f68c5948b5a982` |

Pair bundle is SHA256 of ascending `six_digit_rank.json:sha256\n` lines.
Source input SHA, published handoff report/definition, preflight, successful CI,
import code and pinned validator are bound by the private lineage. The owner's
direct continuation request is recorded separately from formal external review.

Actual private paths:

```text
/mnt/e/FAS-private/artifacts/phase1/oulu_owner_review_batch02_v1/oulu-batch02-human-review.json
/mnt/e/FAS-private/artifacts/phase1/oulu_human_dispositions_batch02_v1
/mnt/e/FAS-private/artifacts/phase1/oulu_human_dispositions_batch02_rerun_v1
/mnt/e/FAS-private/artifacts/phase1/oulu_batch02_human_import_preflight_v1.json
/mnt/e/FAS-private/artifacts/phase1/oulu_batch02_human_import_verification_v1.json
```

Actual import command:

```bash
conda run --no-capture-output -n fas python scripts/import_oulu_human_batch02.py \
  --review-root /mnt/e/FAS-private/artifacts/phase1/oulu_owner_review_batch02_v1 \
  --human-input /mnt/e/FAS-private/artifacts/phase1/oulu_owner_review_batch02_v1/oulu-batch02-human-review.json \
  --out-root /mnt/e/FAS-private/artifacts/phase1/oulu_human_dispositions_batch02_v1
```

Listed output roots already exist and intentionally refuse overwrite. Further
authorized replay requires a fresh private sibling root, never source edits.

## Completion And Stop

**Checkpoint1.5Q import is complete; batch02 effective closure is pending review.**
Ten actual owner answers are recorded, all agreeing with AI rejections, but no
additive activation/current ledger has been created. The identical general
rationale is disclosed, not treated as independent scientific validation.

Review this pushed import checkpoint and its exact CI before any additive activation.
No replacement JSON or repeat human review is requested at this checkpoint.
If review accepts the scope/evidence, activation must be a separate immutable
record that preserves this import and original AI history; do not relabel them
as previously accepted effective judgments. Do not begin ranks20+ before batch02
closure/reconciliation requirements are explicitly resolved.

The integrated browser's earlier403 remains historical; owner submission enables
bound human import but does not independently certify browser usability or human
authorship. No new visual inspection, media decode, extraction, detector/model or
target-domain execution occurred. Schema passes; data-audit, source-dry-run,
analysis-freeze and locked-evaluation remain blocked. Roles/selector/seed/threshold
are unchanged; global lineage clearance and scientific readiness remain false.