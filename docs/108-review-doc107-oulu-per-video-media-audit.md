# 108 — Review of Document 107: OULU Per-Video Media Audit

Date: 2026-10-09  
Repository: `lathevinh/fas`  
Reviewed audit commit: `7b7653f57fdc448adb604228e21b162828cecb6e`  
Reviewed current follow-up commit: `1ed78292a53b09d8d47133ac163afc071ad63c55`  
Reviewed document: `docs/107-review-response-doc106-oulu-per-video-audit.md`

## Verdict

**DOCUMENT 107 — ACCEPTED.**

**CHECKPOINT 1.5D OULU PER-VIDEO PAYLOAD / STRICT-DECODE / EXACT-DUPLICATE AUDIT — ACCEPTED WITHOUT REWORK.**

**FULL OULU / CORE SCIENTIFIC READINESS — STILL PENDING.**

## Main findings

- Exactly **4,950** frozen OULU video IDs were audited and reconciled to canonical IDs, archive paths/sizes and permanent roles.
- All per-video payload hashes are complete.
- Strict full decode passed for **4,949** videos and failed for **1** video.
- The failure is a bona-fide sample in original `train`, permanent role `branch_calibration`.
- The failed video is retained as a terminally failed record; it is not repaired, replaced, silently accepted, excluded, reassigned or used to retry the split.
- **13 exact AVI duplicate pairs** and **13 exact decoded-RGB-sequence duplicate pairs** were found.
- There are **0 cross-role**, **0 cross-partition** and **0 conflicting-label** exact duplicate groups.
- All 13 frozen artifacts remain byte-identical; no canonical row or frozen role changed.
- 4,949 videos have physically available central decoded-frame candidates; the failed video has none.
- Near-duplicate and cross-dataset duplicate audits remain incomplete.
- Schema passes; data-audit, source-dry-run, analysis-freeze and locked-evaluation remain blocked.

## Strict decode implementation

The probe is appropriately fail-closed. It requires:

- successful `ffprobe -v error`;
- positive duration/FPS;
- nonzero frames;
- positive dimensions;
- monotone timestamps;
- full FFmpeg RGB24 decoding;
- `-xerror -err_detect explode`;
- ffprobe/framehash count agreement;
- declared frame-count agreement when available;
- valid SHA-256 frame hashes.

Any ffprobe/FFmpeg stderr is treated as failure even if the process exit code is zero.

This correctly catches the observed MJPEG corruption.

## Exact duplicate interpretation

The result supports the narrow statement:

> No exact OULU content duplicate crosses frozen roles or native partitions.

It does **not** yet support the broader statement:

> The benchmark is content-disjoint.

Near-duplicate, re-encoded/derived-content and cross-dataset lineage checks are still pending.

## Important unresolved issue: one failed calibration transaction

The single undecodable video belongs to `branch_calibration`.

This does not invalidate checkpoint 1.5D, but downstream handling must be frozen before model execution.

The project must explicitly define how a technically unusable pre-detector source transaction affects:

- calibration fitting;
- end-to-end technical-failure accounting;
- any relevant denominators.

It must not be silently dropped only where convenient.

No media failure may trigger role regeneration, seed retry or post-hoc split repair.

## CI follow-up

The first pushed audit checkpoint failed CI because the CI host lacked FFmpeg for synthetic media tests.

Follow-up commit `1ed78292a53b09d8d47133ac163afc071ad63c55` only installs FFmpeg in the CI workflow and documents that distinction. It does not change the audit implementation, private evidence or immutable public result.

Fresh CI on that follow-up commit succeeds.

The CI host FFmpeg should not be described as reproducing the exact research-runtime FFmpeg binary; the real audit records FFmpeg/ffprobe 4.4.2.

## Required next actions

1. Freeze the protocol-level handling of the one undecodable `branch_calibration` transaction.
2. Implement/freeze the final primary-frame selector/tie convention consistently with the strict single-image protocol.
3. Perform near-duplicate/content-lineage analysis.
4. Perform cross-dataset duplicate checks once equivalent media evidence exists for the other domains.
5. Audit CASIA-FASD, MSU-MFSD and SiW-Mv2 media populations.
6. Keep frozen roles and split seed `20261009` immutable.

## Final disposition

**DOCUMENT 107 — ACCEPTED.**

**CHECKPOINT 1.5D OULU PER-VIDEO EVIDENCE COLLECTION — ACCEPTED WITHOUT REWORK.**

The audit successfully exposes and preserves one genuine media failure and thirteen exact duplicate pairs without altering the study split.

**Full OULU/core readiness remains pending because transaction handling, near-duplicate/cross-dataset lineage and the other three dataset media audits are unresolved.**
