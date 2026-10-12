# Response to Review 135: Next Fixed Batch-03 Evidence Packets

Date: 2026-10-12
Base commit: `bf652a9`
Review: [Document 135](135-review-doc134-oulu-batch02-activation.md)

Review135 accepts batch02 additive activation without rework and authorizes
preparing the next frozen queue batch beginning at20. This checkpoint **1.5S
prepares exactly batch03 ranks20..29**. It performs no visual adjudication,
human review, effective activation or scientific/model execution. Batch01 and
batch02 remain closed at ten screen-level rejections each, not cleared videos
or certified independent captures. No accepted batch is reopened.

## Prospective Completion Criteria

- Verify exact successful batch02 activation CI and accepted current-ledger hashes.
- Select exactly20..29 in frozen order, all cross-role + conflicting-label;
  no skipping, replacement, threshold retuning, role repair or outcome selection.
- Preserve accepted batch01/batch02 runners and the original visual module/policy.
  A separate prospective runner changes queue/authority only; existing visual
  utilities still own full-RGB verification,17 fixed temporal slots, two panels
  and the earliest minimum-Hamming trigger witness.
- Verify accepted queue/media/fingerprint bundles, payload pins, locked FFmpeg
  and all13 frozen artifacts before private export.
- Produce immutable manifests/packets with `review_performed=false` and
  `awaiting_visual_review`, not AI/human/effective dispositions.
- Independently redecode/reexport, read back every PNG and source binding,
  reconstruct panels/triggers, refuse overwrite, preserve prior snapshots and gates.
- Publish and push for review before inspecting new images or preparing later ranks.

The fixed selector and its focused test were implemented before actual decoding.
The private preflight pins exact CI and13 protected-root snapshots before either
export. All criteria below passed in existing conda `fas`; no package, Python,
FFmpeg or CI workflow change was made.

## Actual Results

| Item | Result |
|---|---:|
| Frozen queue ranks prepared | 20..29, exactly ten |
| Distinct videos | 17 |
| Full decoded RGB frames verified against accepted frame index | 2417 |
| Verified-frame PNGs | 2417 |
| Temporal panels + trigger PNGs | 30 |
| Video manifests / pair packets / lineage + summary | 17 / 10 / 2 |
| Total private files | 2476 |
| Independent redecode/reexport byte-identical | 2476 / 2476 |
| Persisted PNGs readable and hash-verified | 2447 / 2447 |
| Focused OULU regression | 56 passed, 0 failures/errors |
| Full regression | 243 passed, 0 failures/errors |
| Images actually visually reviewed | 0 |
| New AI / human / effective dispositions | 0 / 0 / 0 |

Total file arithmetic is `2417 + 30 + 17 + 10 + 2 = 2476`. Each video manifest
matches accepted frame counts, RGB-index references, thumbnail hashes and17
temporal decode orders. Each packet matches its accepted exact candidate/rank,
media manifests and image hashes. The verification reconstructs both panels
from persisted thumbnails and independently recomputes the earliest minimum
Hamming witness from accepted fingerprints. This verifies image construction,
not human/AI visual inspection or classification accuracy.

Both exports clean up temporary AVI payloads. Existing-output invocation returns
exit1 and leaves the original2476 files unchanged. All13 protected roots remain
identical to preflight, including frozen roles and prior private packet, AI,
owner/human, reconciliation and activation evidence. All13 frozen hashes match
the accepted registry. Accepted runners/visual policy/module remain unchanged.

The new regression test rejects an unclosed batch02, fewer than ten activations,
wrong current counts, an incomplete/reordered queue, wrong priority, repository
output and existing output. Existing review/import disagreement and hard-stop
tests remain passing. Editor diagnostics report no errors in the touched Python
files; executed tests use the explicit `fas` environment, not base.

Exact activation CI was freshly observed as completed/success: commit
`0ec57d5919cdb9f29eac958c879b10bcede5e113`, run `38224058842`,
check `114727096275`, completed `2026-10-12T08:32:01Z`. It is a prerequisite
bound to the new lineage, not fresh CI for this new checkpoint commit.

## Evidence Bindings

The [aggregate report](../results/phase1/oulu-batch03-packets-v1.json) publishes
counts/hashes/check outcomes only. Biometric PNGs, candidate bodies, video IDs
and media paths remain outside Git. Public evidence cannot independently inspect
private pair bodies; this checkpoint does not claim otherwise.

| Bound record | SHA256 |
|---|---|
| Review135 | `55c1cb5721c5118ec5db76ae10551ddfaf1189f3a62ceb6c40e507d2664d516f` |
| New runner | `7130d72cca4925870e8d4ffa3e424ed452cbc70776be878f4a44bd4ff9fd361f` |
| Private preflight | `536489c4c15119bb2fc6661397b8a9ac3884ba0cbc303136a4ceb93ea1cf9ed6` |
| Private lineage | `51f7176b63675f562fa3160b5d3355025d8b813b10f7bc0c944e28df8e1a2b68` |
| Private summary | `02ca468e67a45f4b8faff12bab7fc58da22e66aca2ecd6eb2310bba0fd0f6d47` |
| Packet bundle | `7133f2246894f256e1611ff14cb357413c9974cd9de16625daa29528fa4d79b3` |
| Private verification | `bbf68cc482a4b19a2da29e807816c9af25bb1cd532b3bd1b19f21bccedba394b` |

Packet bundle is SHA256 of ascending `six_digit_queue_rank:packet_sha256\n`
lines. Lineage additionally binds the accepted batch02 activation/report/current
ledger, exact queue/report, original evidence policy, new runner, FFmpeg lock
and frozen artifacts. Preflight/verification use the existing immutable writer;
the runner consumes preflight without network access.

Private outputs:

```text
/mnt/e/FAS-private/artifacts/phase1/oulu_visual_packets_batch03_v1
/mnt/e/FAS-private/artifacts/phase1/oulu_visual_packets_batch03_rerun_v1
/mnt/e/FAS-private/artifacts/phase1/oulu_batch03_preparation_preflight_v1.json
/mnt/e/FAS-private/artifacts/phase1/oulu_batch03_preparation_verification_v1.json
```

Pair directories retain their original queue ranks. Each contains two temporal
panels, trigger PNG and packet. The independent replay actually executed was:

```bash
conda run --no-capture-output -n fas python scripts/prepare_oulu_visual_batch03.py \
  --input-root oulu-npu \
  --audit-root /mnt/e/FAS-private/artifacts/phase1/oulu_per_video_audit_v1 \
  --exact-root /mnt/e/FAS-private/artifacts/phase1/oulu_lineage_evidence_v1 \
  --screen-root /mnt/e/FAS-private/artifacts/phase1/oulu_content_screening_v1 \
  --frozen-root /mnt/e/FAS-private/frozen/source_roles_v2 \
  --archive-records /mnt/e/FAS-private/artifacts/phase1/oulu_archive_hashes_v1 \
  --activation-root /mnt/e/FAS-private/artifacts/phase1/oulu_batch02_activation_v1 \
  --out-root /mnt/e/FAS-private/artifacts/phase1/oulu_visual_packets_batch03_rerun_v1
```

Both outputs exist now; another invocation must refuse them. A replay requires
a fresh private sibling, never an overwrite or nesting within protected evidence.

## Completion And Stop Boundary

**Checkpoint1.5S preparation is complete and awaits review.** The20 previously
resolved candidate relationships remain unchanged. All65 remaining highest-risk
candidates still lack AI visual review:10 are now prepared,55 not yet prepared.
No rank30+ was selected and no new outcome was inferred from decode/hash success.

After acceptance of this pushed checkpoint and exact CI, the next separate stage
may inspect30 bound images for20..29 and record supported AI proposals. Uncertain
cases must remain uncertain; genuine human review and reconciliation are separate.
A confirmed same/derived cross-role case remains a scientific hard stop.

Schema passes. Data-audit, source-dry-run, analysis-freeze and locked-evaluation
still fail closed. Global OULU/cross-dataset lineage closure, other media audits
and research models remain pending. There is no sample deletion, role/selector/
seed change, acquisition-provenance certification, full-video independence claim,
model execution, target evaluation or scientific readiness.