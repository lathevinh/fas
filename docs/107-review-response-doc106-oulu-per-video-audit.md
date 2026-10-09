# Response to Review 106: OULU Per-Video Media Audit

Date: 2026-10-09
Base commit: `4db4e84`
Review: [Document 106](106-review-doc105-oulu-archive-byte-pinning.md)

Review 106 accepts the three-TAR byte pinning without rework. Checkpoint 1.5D
now audits only the 4950 frozen OULU video IDs. It does not authorize a different
dataset, face detector, model training, source predictions or target evaluation.

## Completion Criteria

- Match every supplied member path/size to the frozen canonical row and join
  exactly one permanent role per video; preserve all 13 frozen artifacts.
- Read/hash every AVI payload through an ephemeral private file, without
  exporting any biometric content to Git. Persist immutable private per-ID records.
- Use the installed, locked FFmpeg/ffprobe to record full-decode counts, codec,
  container, duration, FPS, timestamps, keyframe flags and dimensions. Confirm
  ffprobe/framehash counts agree and fail closed on errors or zero frames.
- Record decoded RGB frame identities and the physically available central
  decoded frame(s), before any face detection. Do not replace failed media or
  change role allocations. For an even-length sequence both central candidates
  are reported; this audit does not amend the final selector's tie convention.
- Check identical payloads and identical complete decoded RGB sequences across
  IDs, roles and original partitions. Preserve private duplicate-group evidence.
- Publish actual aggregate counts/hashes and tests, push, then stop for review.

Accepted OULU metadata supplies no temporal trim bounds. This audit indexes the
whole supplied video; it does not invent an independently certified interval.
Near-duplicate and cross-dataset checks, detector adequacy and scientific gates
remain separate obligations. Exact duplicate absence alone is not full content
disjointness. No failed record may trigger a split/seed retry.

## Implementation and Status

[Probe](../src/fas/media.py) uses ffprobe frame metadata and strict FFmpeg RGB
framehash decoding. [Runner](../scripts/audit_oulu_media.py) checks accepted
archive-record identities, frozen lineage, full header/protocol reconciliation
and private output boundaries before processing. Temporary payloads are removed
after each probe; private frame indexes and identity hashes remain outside Git.
Records are written after each video, progress is logged every 50 completed
videos, and the completion summary is written last. Existing output is refused.

Focused OULU tests pass **22/22**; full regression passes **209/209**, with zero
failures/errors. Coverage includes reproducible full decode, corrupt media,
timeout, decode-count mismatch and refusal of repository output. The locked
FFmpeg 4.4.2 uses `-vsync 0` for frame passthrough; no environment change occurred.
The CI workflow explicitly installs FFmpeg for synthetic media regression; its
host tools are separate from the pinned `fas` research runtime. The first pushed
checkpoint's CI failed, and this dependency declaration is a separate follow-up;
private media evidence and the immutable public report are not rewritten.

## Actual Result

The [immutable public report](../results/phase1/oulu-per-video-media-audit-v1.json)
binds the private summary, lineage, duplicate groups and complete per-video record
bundle by SHA-256. All 4950 payloads were hashed and size/identity/role reconciled.
Every private decoded frame index was independently checked against the reported
frame count, order, monotone timestamps, central candidates and RGB sequence hash.
All 13 frozen artifacts remain byte-identical. No canonical row or role changed.

- **4949** videos pass strict full decode, with codec/container, duration, FPS,
  dimensions, timestamps, keyframe status and RGB hashes recorded privately.
- **1** supplied training-partition bona fide in `branch_calibration` fails strict
  decoding. ffprobe reports MJPEG `error dc` and an additional decode error despite
  returning exit code 0. The record is terminally failed, not silently accepted,
  repaired, replaced, excluded or reassigned. Its payload identity is still pinned.
- **4949** videos have physically available central decoded-frame candidates.
  The failed video has none. Successful videos have at most 151 decoded frames.
- **13 pairs** have identical AVI payload bytes; **13 pairs** have identical full
  decoded RGB sequences. There are **0 cross-role**, **0 cross-partition** and
  **0 conflicting-label** duplicate groups. This is exact-content evidence for
  OULU only, not near-duplicate or cross-dataset leakage certification.

Schema passes. Data-audit, source-dry-run, analysis-freeze and locked-evaluation
remain blocked; audit summary counts are not promoted. Temporary AVI files were
removed. No final primary-frame selector, frame bank, detector, model or target
output was executed, and no background audit job remains active.

**Per-video evidence collection is complete; it found a real media defect and
duplicates. Full OULU/core scientific readiness is not claimed.** Stop for owner
review after publication. The next checkpoint must address unresolved content
lineage and transaction/applicability handling under the existing frozen policy,
without repairing the dataset or retrying the split automatically.