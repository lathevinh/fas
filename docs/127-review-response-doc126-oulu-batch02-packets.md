# Response to Review 126: Next Fixed Batch-02 Evidence Packets

Date: 2026-10-10
Base commit: `447bcee`
Review: [Document 126](126-review-doc125-oulu-batch01-activation.md)

Review 126 accepts batch01 closure and permits the next frozen queue batch.
This checkpoint **1.5N prepares evidence for batch02, queue ranks 10 through 19**,
the next ten of the remaining75 highest-risk candidates. It is packet preparation,
not visual adjudication or completion of all75. No batch01 records are reopened.

## Prospective Criteria

- Verify accepted batch01 activation/current ledger and exact activation CI.
- Select exactly ranks10..19, in order, all cross-role + conflicting-label; no
  skipping, replacements, outcome-based selection or screening retuning.
- Preserve the pinned original visual module, batch01 runner and visual policy.
  A separate runner owns new queue selection; evidence uses the same full-RGB
  verification, 17 fixed temporal slots, two panels and earliest-minimum trigger.
- Verify accepted queue/media/fingerprint bundles, payload pins, FFmpeg lock and
  all13 frozen artifacts before generating private images.
- Export immutable private manifests/packets, with no dispositions or human
  answers; verify actual reread/redecode replay, image hashes and cleanup.
- Preserve prior evidence and scientific gates; publish results for checkpoint
  review before visual adjudication or any further queue batch.

## Actual Results

All criteria above passed in the existing conda `fas` environment. No package,
Python version, FFmpeg installation or CI workflow was changed.

| Item | Result |
|---|---:|
| Frozen queue ranks prepared | 10..19, exactly ten |
| Distinct videos | 15 |
| Every decoded RGB frame verified against accepted index | 2135 |
| Persisted verified-frame PNGs | 2135 |
| Temporal panels + trigger PNGs | 30 |
| Video manifests / pair packets / lineage + summary | 15 / 10 / 2 |
| Total private export files | 2192 |
| Independent redecode/reexport byte-identical | 2192 / 2192 |
| Focused OULU regression | 53 passed |
| Full regression | 240 passed, 0 errors/failures |
| Images actually visually reviewed this checkpoint | 0 |
| New AI/human/effective dispositions | 0 |

The initial readback check incorrectly expected2182 files; the corrected sum
`2135 + 30 + 15 + 10 + 2 = 2192` passed. No exported bytes were changed to satisfy
that check. Every persisted PNG decodes successfully; all file hashes, packet
bindings and accepted RGB-index bindings pass. No temporary AVI remains.

The pinned activation CI was freshly observed as completed/success:
commit `5f3c22c4a473770b5653a4439bf350379fc5032f`, run `38016294243`,
check `114107181776`, completed `2026-10-10T02:16:07Z`.
That prerequisite is bound in the private preflight and new packet lineage;
it is not substituted for fresh CI of this new checkpoint commit.

Existing output returns exit1 without changing any exported file. Full snapshots
of prior packets, AI records, human handoff/import, Pair-5 proposal, owner acceptance,
activation and all13 frozen artifacts are unchanged after both runs. The handoff
snapshot now has68 files because the owner's submitted JSON is present in addition
to the historical67-file prepared handoff; this is not a rewrite of those67 files.
The accepted batch01 visual runner/module/policy remain byte-for-byte unchanged.

## Evidence Bindings

The [aggregate report](../results/phase1/oulu-batch02-packets-v1.json) publishes
only counts, evidence hashes, regression outcomes and scope flags. Biometric
PNGs, video identities, media paths and candidate rows remain outside Git.

| Bound record | SHA256 |
|---|---|
| Review126 | `feb71ef422a96569f75b66c2fde5ea89ed39fd73c8b18c41f785515c2b86b249` |
| New runner | `b9c238de737111bb93592cc57a8e5220ea4455499668fed017e52c2371fd13af` |
| Private preflight | `a1c510e046b2547a001d2eea6e8e6f4551b276cf9763a11215e6a73030eff74b` |
| Private lineage | `1fbfc7ab62db6eaa88b8e7ac5d1ecaff5ffe9a30afe8ab5f2765ba5ac83e3cc9` |
| Private packet summary | `9894c343fdbcc27063e3395e5835871d57a0507a7f2929143f00fea771e3ab73` |
| Packet bundle | `44b62e4e442abb82e5f1534450ba4c60c344f779c9e36a5ec473bde6278aae92` |
| Private verification | `793ed4897256e5a6cfcda5b6baff4dc842d977253200e6489ddbb6e2906e9a21` |

Packet bundle convention: SHA256 of concatenated ascending
`six_digit_queue_rank:packet_sha256\n` lines. The private lineage additionally binds
the accepted queue, batch01 activation/current ledger, frozen files and reused
visual evidence policy. The report does not claim human authorship or visual
inspection from image-decode checks.

Private outputs:

```text
/mnt/e/FAS-private/artifacts/phase1/oulu_visual_packets_batch02_v1
/mnt/e/FAS-private/artifacts/phase1/oulu_visual_packets_batch02_rerun_v1
/mnt/e/FAS-private/artifacts/phase1/oulu_batch02_preparation_preflight_v1.json
/mnt/e/FAS-private/artifacts/phase1/oulu_batch02_preparation_verification_v1.json
```

Each pair directory is its original zero-based queue rank, not local batch rank.
It contains two interleaved temporal panels, trigger witness and bound packet.
The private preflight/verification were generated through the existing immutable
writer. The runner consumes the preflight; it does not perform network access.

The independently executed replay command was:

```bash
conda run --no-capture-output -n fas python scripts/prepare_oulu_visual_batch02.py \
  --input-root oulu-npu \
  --audit-root /mnt/e/FAS-private/artifacts/phase1/oulu_per_video_audit_v1 \
  --exact-root /mnt/e/FAS-private/artifacts/phase1/oulu_lineage_evidence_v1 \
  --screen-root /mnt/e/FAS-private/artifacts/phase1/oulu_content_screening_v1 \
  --frozen-root /mnt/e/FAS-private/frozen/source_roles_v2 \
  --archive-records /mnt/e/FAS-private/artifacts/phase1/oulu_archive_hashes_v1 \
  --activation-root /mnt/e/FAS-private/artifacts/phase1/oulu_batch01_activation_v1 \
  --out-root /mnt/e/FAS-private/artifacts/phase1/oulu_visual_packets_batch02_rerun_v1
```

Both listed outputs already exist and are intentionally refused on subsequent
invocation. A further replay needs a fresh private sibling output, never an
overwrite or a path nested within accepted evidence roots.

## Completion And Next Boundary

**Checkpoint1.5N preparation is complete; checkpoint review is required before
visual adjudication.** Batch02 has ten prepared pairs and zero reviewed pairs.
Of the75 remaining highest-risk candidates,10 are now prepared and65 not yet
prepared; all75 still lack new visual dispositions. Batch01 remains closed10/0/0.

No further ranks were selected. Next, after review of this pushed checkpoint and
its exact CI, inspect the30 bound panels/triggers for ranks10..19 and record only
supported AI proposals. Ambiguous cases retain uncertainty and receive fixed
additional evidence rather than unsupported clearance. Genuine human review and
any disagreement reconciliation remain separate future checkpoints. A confirmed
same/derived cross-role relationship triggers an explicit scientific decision stop.

Schema passes; data-audit, source-dry-run, analysis-freeze and locked-evaluation
all still fail closed. There is no sample deletion, role/selector/seed change,
capture-provenance certification, global lineage clearance, detector/model
execution, target evaluation or scientific readiness.