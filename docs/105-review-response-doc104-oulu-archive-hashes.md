# Response to Review 104: OULU Archive Byte Pinning

Date: 2026-10-09
Review: [Document 104](104-review-doc103-oulu-technical-preflight.md)
Base commit: `7f2839c`

Document 104 accepts the previous bounded header/protocol checkpoint without
rework. This next checkpoint completes whole-file SHA-256 for the three OULU
media TARs only. No extraction, individual video opening, decoding, detector or
model execution, role allocation, or other dataset is included.

## Completion Criteria

- Read every byte of Dev_files.tar, Test_files.tar and Train_files.tar.
- Check sizes against the [accepted preflight](../results/phase1/oulu-technical-archive-preflight-v1.json):
  28151992320, 39211162112 and 37753662976 bytes respectively.
- Check file identity, size and modification metadata before and after hashing.
- Save each completed digest as an immutable private record outside Git, then
  publish an aggregate report containing all three complete digests.
- Verify all 13 frozen artifacts, source-role registry and previous study
  artifacts remain unchanged; schema passes and later stages remain blocked.
- Push the actual evidence and stop for owner review before decoded-media work.

These hashes pin supplied local archive bytes. They are not publisher-checksum
verification, successful media decoding, per-video content identity or proof of
content disjointness. Full checkpoint 1.5 remains incomplete.

## Actual Result

OULU focused tests pass 17/17 in `fas`, with zero failures or errors. The existing
whole-file hashing implementation was also checked against a known synthetic
payload. No Python source/config changes or full regression rerun are included.

The [immutable aggregate report](../results/phase1/oulu-archive-byte-pinning-v1.json)
records all three complete TAR hashes, with total bytes read **105116817408**.
The job completed at 2026-10-09T07:05:17.323660+00:00. Each digest was saved as
an immutable private record immediately after its full-file read; the aggregate
binds those private records by SHA-256 without publishing filesystem identities.

| Archive | Bytes | SHA-256 | Hashing seconds |
|---|---:|---|---:|
| Dev_files.tar | 28151992320 | `3c3a17e0ebbea6d42aaa15d2d43fc9cc257f43372e424f5e5786f4b5a9e2d5f6` | 316.734 |
| Test_files.tar | 39211162112 | `2f1f9d752751fdf2d09a763d4f2424cba8ced548800fd4d0bdc189a652274383` | 464.140 |
| Train_files.tar | 37753662976 | `966127b8bc11b00215a1a2af530c2345ce50b12a54b59cc717650a0b9236a4d4` | 415.560 |

All three file identities, sizes and modification metadata remained unchanged
across their reads. All 13 frozen artifacts and the previous study artifact
hashes remain unchanged. Schema passes; data-audit, source-dry-run,
analysis-freeze and locked-evaluation remain blocked. Audit summary counts
remain unchanged. The earlier preflight report is preserved, not overwritten.

**OULU whole-archive byte pinning is complete; full media audit remains pending.**
No individual video payload was opened, and no extraction, migration, decoding,
detector/model execution or role regeneration occurred. After publication, stop
for owner confirmation before the separate per-video integrity/decode/content
duplicate checkpoint. No background hashing job remains active.