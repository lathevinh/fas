# Batch03 Bound Owner-Human Review Import

Date: 2026-10-12
Base commit: `2fb32461a78578930bceb088b847cb7782a31706`
Prior handoff: [Document140](140-review-response-doc139-oulu-batch03-human-handoff.md)

## Authority And Prospective Criteria

The owner reports completing review and placing the exported JSON alongside the
private batch03 page. This supplies genuine input for checkpoint1.5V import only,
not acceptance of scientific/effective closure. No formal external review141 was
present on origin/main at import start; this document is an import record, not a
fabricated external verdict. Direct-owner import-only scope is bound in preflight.

- Verify published definition/page/summary, accepted AI/packet hashes, pinned
  implementation and exact successful handoff CI before importing.
- Preserve original JSON bytes, submitted rationale and attestations. Validate ten
  unique integer ranks20..29 and every bound packet/asset without authoring answers.
- Reuse the unchanged validator through in-memory local ranks0..9, restoring20..29
  afterward. Preserve disagreement as uncertain and human confirmation as a
  scientific hard stop; never automatically activate agreement.
- Create immutable private ledgers and independently reimport into a fresh root.
  Verify readback, overwrite refusal, protected/frozen evidence and scientific gates.
- Run focused/full regression, publish aggregate evidence and stop for checkpoint
  review before separate additive activation or queue ranks30+.

## Actual Import Results

The actual JSON alongside the page declares an owner-human reviewer, personal
bound-evidence inspection and answers timestamped `2026-10-12T10:45:39.048Z`.
All answers bind to the published batch03 definition. Authorship and inspection
remain explicit human attestations, not independent authentication.

| Item | Result |
|---|---:|
| Original queue ranks imported | 20..29 |
| Human `rejected_false_positive` answers | 10 |
| AI/human agreements / disagreements | 10 / 0 |
| Human confirmed same/derived / scientific hard stop | 0 / false |
| Unique submitted rationale texts | 1 |
| New effective dispositions activated | 0 |
| Private import ledger files | 13 |
| Independent reimport byte-identical | 13 / 13 |
| Bound image asset hashes verified | 30 / 30 |
| Focused regression in existing `fas` | 58 passed |
| Full regression in existing `fas` | 245 passed, 0 errors/failures |

All ten rationale fields contain the same general text. They are nonblank and
schema-valid, but **are not ten independently detailed pair-specific human
rationales**. Original text is preserved verbatim, not expanded or substituted
with AI observations. This limitation remains for checkpoint review. Agreement
does not demonstrate judgment accuracy, independent raters or capture independence.
Collapsed AI notes are not full blinding; reused/correlated foreground evidence
and sparse-slot coverage limitations from139 remain unchanged.

Original submitted JSON bytes and SHA256 remain unchanged. Stored `human_input.json`
uses the existing immutable writer's canonical serialization and has identical
parsed content; it is not claimed byte-identical to the original serialization.
Every imported answer/rationale/rank equals its original submitted field. The
adapter never mutates the input or published definition. Synthetic tests cover
rank completeness/uniqueness/integer checks, nonmutation, wrong hashes/assets,
blank rationale, missing attestations, uncertainty and confirmed-content hard stop.

The validator's row field `effective_disposition` is **comparison only, not an
activated current ledger**. Every row explicitly has
`effective_disposition_activated = false`; summary has zero activations and
`batch03_accepted_reconciled_disposition_state = false`. No sample removal, mask
update or role repair is performed. Confirmation would stop further scientific
work; disagreement would retain uncertain comparison state pending reconciliation.

## Prerequisite And Preservation

Fresh official Actions web evidence links exact handoff commit
`2fb32461a78578930bceb088b847cb7782a31706`, [run38238303749](https://github.com/lathevinh/fas/actions/runs/38238303749),
shows Status Success and [validate job114774331366](https://github.com/lathevinh/fas/actions/runs/38238303749/job/114774331366)
completed successfully. Preflight/lineage bind this web source, exact run/job and
commit. Absolute completion timestamp is unavailable in that fetched content and
null, not invented. This is prerequisite CI, not CI for the new import commit.

Each ledger contains lineage, canonical human input, ten pair rows and summary.
Independent reimport executes again against the unchanged input and produces13/13
byte-identical files; reproducible import is not independent human re-review.
Existing-output invocation exits1 with all13 original files unchanged.

Sixteen protected roots and13 frozen files remain unchanged, including prior
batch01/batch02 historical/current records, batch03 packets/AI evidence and the
current human handoff. That handoff now has34 files: original33 prepared files
plus the newly supplied owner JSON. Original33 files remain unchanged; no historical
report is rewritten to change its earlier human=0 or file=33 observation.
Accepted preparation runners, PAGE, validator, visual policy, environment and CI
workflow are unchanged. Only the separate importer, one existing test, this
document, aggregate report and README are published.

## Evidence Bindings

The [aggregate report](../results/phase1/oulu-human-review-import-batch03-v1.json)
contains counts/hashes/scope only. Owner JSON, reviewer ID, images, candidate
bodies and detailed private records remain outside Git.

| Record | SHA256 |
|---|---|
| Original owner JSON | `075ee2019913a484a176ff97e136b1479391d3ff2f1623a557e29e765e111a9b` |
| Import adapter | `dc79e315c54b211aedb191b7a445c97c957a194c651d059e147693e32292c185` |
| Private preflight | `c1e255ca969c8f91caad7206b1b37f6786bb1106231fd1c7acd4b546ba821f52` |
| Private lineage | `33ed6172196c2d3de2b9d309821ad94b04ae32c8865e1c1a8292fd194717960b` |
| Human pair bundle | `223c8ee522a4568ae59bb6329ac0d9c3bcb9658169b19fa8218e5c1cb32dcc1e` |
| Private summary | `d71ea744473fe151687e3031a073c986a0948625cdf458ed8ecbbd2a1ffa07a9` |
| Private verification | `b4fff358f76726b51439a01e1c8a03756b15e60551d4848a07eb78ad8c116c50` |

Pair bundle is SHA256 of ascending `six_digit_rank.json:sha256\n` lines.
Private lineage binds original input, published handoff report/definition,
preflight, successful CI, new importer and pinned validator. Direct-owner
import-only authorization is separate from formal checkpoint acceptance.

Actual command:

```bash
conda run --no-capture-output -n fas python scripts/import_oulu_human_batch03.py \
  --review-root /mnt/e/FAS-private/artifacts/phase1/oulu_owner_review_batch03_v1 \
  --human-input /mnt/e/FAS-private/artifacts/phase1/oulu_owner_review_batch03_v1/oulu-batch03-human-review.json \
  --out-root /mnt/e/FAS-private/artifacts/phase1/oulu_human_dispositions_batch03_v1
```

The independent output is the private sibling `oulu_human_dispositions_batch03_rerun_v1`.
Both roots already exist and refuse overwrite. Preflight/verification are
`oulu_batch03_human_import_preflight_v1.json` and
`oulu_batch03_human_import_verification_v1.json` under the same private phase1 root.
Any future authorized replay requires a fresh sibling, never editing evidence.

## Completion And Stop

**Checkpoint1.5V import is complete; batch03 effective closure remains pending
review.** Ten actual owner answers agree with AI proposals, but no additive
activation/current ledger has been created. Review this pushed import checkpoint
and its exact CI before any separate immutable activation. No replacement JSON
or repeat human review is requested. Ranks30+ stay paused until human/reconciliation
and separate additive activation requirements are complete and reviewed.

Earlier integrated-browser403 remains historical: the submitted JSON permits
bound import but does not independently certify desktop/mobile UI or authorship.
Prior20 accepted screen-level relationships remain unchanged;55 highest-risk
candidates still lack AI visual review. No new visual inspection, video decoding,
extraction, research detector/model or target evaluation occurred. Schema passes;
data-audit, source-dry-run, analysis-freeze and locked-evaluation remain blocked.
Roles/selector/seed/screening are unchanged; global lineage clearance, capture
provenance certification and scientific readiness remain false.