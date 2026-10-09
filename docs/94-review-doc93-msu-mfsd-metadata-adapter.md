# 94 — Review of Document 93: MSU-MFSD Native Metadata Adapter

Date: 2026-10-09
Repository: `lathevinh/fas`
Reviewed commit: `9355294e2dbb4dbcdf29269f336b1ff1af230708`
Reviewed document: `docs/93-phase1-msu-mfsd-metadata-adapter.md`

## Verdict

**DOCUMENT 93 / MSU-MFSD METADATA ADAPTER — ACCEPTED.**

No blocker or major methodological issue was found that would corrupt labels, train/test membership, subject grouping, attack-family semantics, or the later cross-dataset evaluation.

The adapter may proceed to the next checkpoint. Media/acquisition readiness remains correctly blocked.

## Main findings

### 1. Native authority is appropriate

The adapter uses the supplied release's own README and official train/test subject lists as the controlling metadata authority.

Those exact raw bytes are SHA-256 pinned before text decoding.

The inner README BOM is part of the provenance check, and the outer README is separately pinned rather than assumed byte-identical.

This is stronger than inferring labels or splits from directory names alone.

### 2. Subject namespace and split semantics are correct

Train and test use the same native subject namespace, canonicalized to three digits without artificial split offsets.

Duplicate or overlapping subject membership fails closed.

The actual inventory preserves:
- 15 train subjects / 120 videos;
- 20 test subjects / 160 videos;
- 35 subjects / 280 videos total.

These native train/test partitions remain metadata. They are not source-role assignments.

### 3. Label polarity and attack mapping are explicit

The model boundary is:
- bona fide = 0;
- attack = 1.

Reference attack types:
- `ipad_video` -> replay;
- `iphone_video` -> replay;
- `printed_photo` -> print.

The type/family mapping is versioned and pinned through the mapping hash.

### 4. Exact population reconciliation is stronger than count checking

The adapter requires every official subject to have exactly eight distinct `(camera, attack_type)` combinations:
- Android + bona fide;
- Android + three attacks;
- laptop + bona fide;
- laptop + three attacks.

Each video must also have a matching `.face` sidecar identity.

Thus the observed 280-video population is reconciled at subject/video identity level rather than accepted merely because aggregate counts happen to equal 280.

### 5. Leakage protection is appropriate

Every normalized media row carries:
- stable native `subject_id`;
- `group_unit = subject`;
- `group_id = subject_id`;
- preserved official split;
- no assigned experiment role.

This gives the later role allocator the correct unit for preventing subject leakage.

### 6. Fail-close behavior is substantive

Negative tests cover:
- overlapping/duplicate subject lists;
- wrong subject namespace;
- unknown/unsafe aliases;
- incorrect folder/label combinations;
- wrong camera extension;
- incomplete or replaced video identities;
- missing/nonmatching sidecars;
- changed pinned README/list bytes;
- BOM drift;
- unsafe paths;
- duplicate archive entries;
- symlinks;
- encrypted entries;
- empty/invalid members;
- missing/duplicate/unknown split volumes;
- corrupt/decompression-failing ZIPs;
- output overwrite attempts;
- private-path/redaction boundaries.

A possible duplicate-canonical-video concern was examined: under the accepted filename grammar there is only one valid path for a given canonical video ID because Android is constrained to `.mp4`, laptop to `.mov`, category is part of the canonical path, and exact duplicate paths are already rejected. No practical silent-overwrite path remains.

### 7. Reader-scope limitation is stated correctly

The implementation does not claim zero underlying compressed-byte access.

Seeking across split outer ZIP volumes may decompress opaque container bytes, but no inner video, `.face` sidecar, or helper payload is opened or interpreted.

Therefore this checkpoint still does not establish:
- archive integrity;
- media integrity;
- video decode success;
- codec/FPS/duration/frame count;
- face-sidecar validity;
- acquisition/licensing verification;
- scientific readiness.

Document 93 states those limitations correctly.

### 8. Actual execution evidence is consistent

Verification reports:
- focused MSU tests: 18/18;
- full regression: 180/180;
- zero failures/errors/skips;
- actual CLI exit 0;
- immutable-output overwrite attempt exit 2;
- actual inventory rederived from private headers and pinned raw metadata;
- video/sidecar/helper-entry guard passed.

Readiness stages remain:
- schema: 0;
- data-audit: 1 blocked;
- source-dry-run: 1 blocked;
- analysis-freeze: 1 blocked;
- locked-evaluation: 1 blocked.

This is the correct stage state for a metadata-only checkpoint.

### 9. Fresh CI

The exact implementation commit:

`9355294e2dbb4dbcdf29269f336b1ff1af230708`

has a completed successful GitHub Actions run.

## Non-blocking notes

1. `participant_identity_verified=false` is conservative even though native client IDs are available. That is acceptable at this checkpoint because the adapter verifies namespace/list semantics, not independent identity truth.
2. `.face` sidecars are only identity-paired by header name and are not parsed. This is appropriate because the current pipeline does not use those annotations yet.
3. README-described capture device/resolution semantics should still be checked against actual decoded media during the later media audit rather than treated as media-level verification now.

## Final disposition

**CHECKPOINT 1.3 / MSU-MFSD METADATA ADAPTER — ACCEPTED WITHOUT REWORK.**

No change is required before proceeding.

With OULU-NPU, CASIA-FASD, SiW-Mv2 and MSU-MFSD metadata adapters now implemented/accepted, the next logical boundary is the canonical immutable manifest / role-assignment stage and then the full core data audit, subject to the repository's frozen checkpoint order.

Do not interpret this acceptance as media readiness or authorization for target evaluation.
