# Response to Review144: Batch04 Private Packet Preparation

Date: 2026-10-13
Base commit: `a11c96e`
Review: [Document144](144-review-doc143-oulu-batch03-activation.md)

## Prospective Criteria

Checkpoint1.5X prepares packets only for the next ten fixed ranks30..39 after
Review144 accepts batch03 closure. It does not perform AI/human review or activate
any new disposition, and does not start ranks40+ or research-model execution.

- Verify exact successful activation CI, Review144 authority, accepted current
  ledger, immutable queue/media/fingerprint/archives, policy and frozen13 hashes.
- Reuse unchanged visual/writer/boundary helpers through a separate batch04 runner;
  preserve accepted runners, roles, selector, seeds and screening thresholds.
- Strictly redecode the selected payloads and verify every RGB frame against the
  accepted index before exporting private thumbnails,17-slot panels and triggers.
- Independently redecode/reexport into a fresh private root; verify file equality,
  image/manifest/packet bindings, overwrite refusal and protected evidence.
- Run focused/full regression in existing `fas`, publish aggregate counts/hashes,
  and stop for packet checkpoint review before actual visual inspection.

Prepared images are integrity evidence, not a research frame bank, new human
judgment, capture-provenance certification or global lineage clearance.

## Actual Results

**Checkpoint1.5X preparation is complete; actual visual review has not started.**
The new runner selects exactly ranks30..39 from the existing frozen queue, with
no outcome-dependent skipping. Prior30 accepted screen-level relationships and
all historical proposal/human/import/current records remain unchanged.

| Item | Result |
|---|---:|
| Frozen queue ranks / pair packets | 30..39 / 10 |
| Unique source videos | 15 |
| Strict accepted RGB frames verified / private frame PNGs | 1690 / 1690 |
| Temporal panels / trigger PNGs | 20 / 10 |
| Video manifests / lineage+summary | 15 / 2 |
| Private export files | 1747 |
| Persisted PNGs decoded and hash-verified | 1720 / 1720 |
| Independent redecode/reexport byte-identical | 1747 / 1747 |
| New AI/human/effective dispositions | 0 / 0 / 0 |
| Focused OULU regression in existing `fas` | 59 passed |
| Full regression in existing `fas` | 246 passed, 0 errors/failures |

The [separate runner](../scripts/prepare_oulu_visual_batch04.py) reuses the pinned
visual/writer/output helpers without altering batch01/batch02/batch03 runners.
It requires accepted batch03 closure, exact successful activation CI, bound
Review144/public activation report, protected snapshots and its own pinned code.
Accepted queue/media/fingerprint bundles, frozen13, archive record/stat identities,
visual policy and locked FFmpeg version verify before selected payload access.

Every selected payload SHA256 and every full-resolution decoded RGB frame match
the accepted media audit before private256-wide thumbnails are saved. This is
the existing bounded integrity export, not research-frame selection or a new
capture-provenance claim. Temporary AVI files are removed. The lower-median
primary selector, failed transaction, permanent roles, seed and thresholds are
not changed or rerun.

Readback checks1690 thumbnail manifests against accepted frame indices/hashes,
all1720 PNG hashes/readability, every packet's original candidate/queue digest,
media/manifests,17-slot panel reconstruction and earliest minimum-Hamming trigger
with bound decode orders. Independent replay actually reopens and redecode-verifies
the same15 source payloads into a fresh root, not merely serializing old JSON.
All1747 files are byte-identical. Existing-output CLI exits1 and changes no bytes.
Both outputs retain no AVI payloads.

Software image decode/hash/reconstruction checks are not AI visual inspection or
human review. All ten packets retain `review_performed = false` and
`disposition = awaiting_visual_review`. No rejection, uncertainty resolution,
confirmation, human attestation or effective activation is invented here.

## Exact CI And Evidence

Fresh official [Actions run38325981545](https://github.com/lathevinh/fas/actions/runs/38325981545)
links exact activation commit `ec244d2ff9a7c6db28d236aa6b0dc01f83c36e43`, shows
Status Success and [validate job115064633017](https://github.com/lathevinh/fas/actions/runs/38325981545/job/115064633017)
completed successfully. Preflight/lineage bind this exact web source and run/job.
Absolute completion timestamp is unavailable in fetched content and null, not
invented. This prerequisite is not CI for the new preparation commit.

Twenty protected roots remain byte-identical: the prior18 plus original/rerun
batch03 activation. Frozen13, all prior study configurations, accepted helpers
and runners remain unchanged. Existing human inputs are not requested again.
No environment, dependencies, CI workflow or dataset policy changed.

The [aggregate report](../results/phase1/oulu-batch04-packets-v1.json) contains
counts/hashes/scope only. Video IDs, candidate bodies, thumbnails and detailed
private records remain outside Git.

| Record | SHA256 |
|---|---|
| Review144 | `d2fd769b81ec052de53c69e117b64839bef382b8fe4687f936ab13cd358bbcba` |
| New runner | `a33ab6ed8a631cf1336fba4dce6bf9176847d6b58f9c4f7bc4ee0f567b5c65a1` |
| Private preflight | `dd10a3c534e60f981dbaeb9d0eab5438429bce20ea68a577ed646b1622ccfc5f` |
| Private lineage | `367dde07f171c93ff2bd3400f20446d24418e0577d0450461f900857c1551f2b` |
| Private summary | `a6d50d7d29773adcc61718701ca1d6ee4f86e72da9a025555b792183c109f821` |
| Packet bundle | `0ef05bdde0fae7222bbc1b2b428425f5ca5612e7fbde51577726307026ed3504` |
| Private verification | `5cc3e51cdcf4efeebe15de9f9d73b607af3a0b0635dca47d31db07f08f969c5c` |

Packet bundle is SHA256 of ascending `six_digit_rank.json:packet_sha256\n`
lines, computed from the ten private summary entries. Immutable preflight,
lineage, summary and verification preserve the source/authority chain.

Private outputs:

```text
/mnt/e/FAS-private/artifacts/phase1/oulu_visual_packets_batch04_v1
/mnt/e/FAS-private/artifacts/phase1/oulu_visual_packets_batch04_rerun_v1
/mnt/e/FAS-private/artifacts/phase1/oulu_batch04_preparation_preflight_v1.json
/mnt/e/FAS-private/artifacts/phase1/oulu_batch04_preparation_verification_v1.json
```

Actual independent redecode/reexport command:

```bash
conda run --no-capture-output -n fas python scripts/prepare_oulu_visual_batch04.py \
  --input-root /mnt/e/FAS/oulu-npu \
  --audit-root /mnt/e/FAS-private/artifacts/phase1/oulu_per_video_audit_v1 \
  --exact-root /mnt/e/FAS-private/artifacts/phase1/oulu_lineage_evidence_v1 \
  --screen-root /mnt/e/FAS-private/artifacts/phase1/oulu_content_screening_v1 \
  --frozen-root /mnt/e/FAS-private/frozen/source_roles_v2 \
  --archive-records /mnt/e/FAS-private/artifacts/phase1/oulu_archive_hashes_v1 \
  --activation-root /mnt/e/FAS-private/artifacts/phase1/oulu_batch03_activation_v1 \
  --out-root /mnt/e/FAS-private/artifacts/phase1/oulu_visual_packets_batch04_rerun_v1
```

Both roots already exist and intentionally refuse overwrite. Future authorized
replay requires a fresh private sibling, never nesting in or editing source evidence.
Only the new runner, one existing test, this document, aggregate report and README
are published. Focused59/full246 tests, actual integrity checks and scientific
stage validation passed in the existing `fas` environment.

## Completion And Stop

**Stop for review of this pushed packet-preparation checkpoint and its exact CI
before actual AI visual inspection of30..39.** No visual/human review, new
disposition, next handoff, ranks40+, other-dataset work, detector/model, training
or target evaluation was started.

Prior30 relationships remain accepted only at observed perceptual-screen scope.
Highest-risk AI coverage is still30/85, leaving55 unreviewed:10 now have prepared
packets and45 have not yet been prepared. Preparation is not adjudication or
clearance of these ten pairs. Any future confirmed same/derived cross-role case
still requires a scientific hard stop and explicit decision.

The17 fixed sparse slots and trigger are not full-video/transformed-overlap or
independent-capture proof. Broader OULU/cross-dataset lineage remains incomplete.
Schema passes; data-audit, source-dry-run, analysis-freeze and locked-evaluation
remain blocked. Model authorization, capture-provenance certification, global
content-lineage completion and scientific readiness remain false.