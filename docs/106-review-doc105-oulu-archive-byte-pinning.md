# 106 — Review of Document 105: OULU Whole-Archive Byte Pinning

Date: 2026-10-09  
Repository: `lathevinh/fas`  
Reviewed commit: `606e7a238428febf340428f43dc1732293f1f646`  
Reviewed document: `docs/105-review-response-doc104-oulu-archive-hashes.md`

## Verdict

**DOCUMENT 105 — ACCEPTED.**

**OULU WHOLE-ARCHIVE BYTE PINNING / CHECKPOINT 1.5C — ACCEPTED WITHOUT REWORK.**

**FULL OULU MEDIA AUDIT / CORE CHECKPOINT 1.5 — STILL PENDING.**

The checkpoint correctly closes the whole-archive byte-integrity gap identified in Review 104. It does not overclaim per-video integrity, decoding, content-level disjointness, or scientific readiness.

## 1. All three OULU media archives are now cryptographically pinned

The full files were read byte-for-byte and SHA-256 digests were completed:

| Archive | Bytes | SHA-256 |
|---|---:|---|
| `Dev_files.tar` | 28,151,992,320 | `3c3a17e0ebbea6d42aaa15d2d43fc9cc257f43372e424f5e5786f4b5a9e2d5f6` |
| `Test_files.tar` | 39,211,162,112 | `2f1f9d752751fdf2d09a763d4f2424cba8ced548800fd4d0bdc189a652274383` |
| `Train_files.tar` | 37,753,662,976 | `966127b8bc11b00215a1a2af530c2345ce50b12a54b59cc717650a0b9236a4d4` |

Total bytes hashed:

`105,116,817,408`

This closes the archive-byte pinning requirement from Review 104.

## 2. File identity stability was checked during hashing

For each TAR, file identity, size and modification metadata were checked before and after the full-byte read and remained unchanged.

That is appropriate protection against accidentally hashing a moving or replaced input.

Each completed digest was also written into a separate immutable private record before publication of the aggregate report.

## 3. These are local reproducibility baselines, not publisher checksums

Document 105 correctly distinguishes:

- local supplied archive SHA-256;
- independently published/provider checksum verification.

`publisher_checksum_verification = false` remains correct.

The hashes prove the exact local archive bytes used by this study can now be identified reproducibly. They do not prove that those bytes are independently certified as an official publisher release.

This distinction must be preserved in paper/provenance language.

## 4. Frozen experiment inputs remain unchanged

The checkpoint reports:

- all 13 frozen artifacts unchanged;
- OULU frozen role hash unchanged;
- frozen registry hash unchanged;
- audit summary counts unchanged;
- prior header/protocol preflight preserved rather than overwritten.

No role generation or reallocation occurred.

This is mandatory after the permanent role freeze and is correctly enforced.

## 5. Scientific stage gating remains correct

The checkpoint does not promote readiness.

Current stage state remains:

- schema: pass;
- data-audit: blocked;
- source-dry-run: blocked;
- analysis-freeze: blocked;
- locked-evaluation: blocked.

This is correct.

Whole-archive hashing alone must not authorize model training or target evaluation.

## 6. Per-video content identity is still not established

The report explicitly states:

`per_video_media_hashes_complete = false`

and:

`content_duplicate_audit = not_verified_no_per_video_media_hashes`

Therefore this checkpoint does **not** establish that:

- each individual video payload is intact;
- two different video IDs do not contain identical content;
- cross-role media duplication is absent;
- source/target media content is disjoint.

Those claims require per-video payload-level evidence.

## 7. Decode/media viability is still unverified

No individual video payload was opened.

No decoding was performed.

Therefore the following remain pending:

- container/demux success;
- codec identification;
- decode success;
- duration;
- FPS;
- frame count;
- zero-frame/corrupt/truncated media detection;
- deterministic middle-frame availability;
- later detector-success adequacy.

This limitation is correctly stated in Document 105.

## 8. Test evidence is adequate for this bounded checkpoint

OULU focused tests remain:

- 17/17 passed;
- zero failures/errors.

The existing hashing implementation was checked against a known synthetic payload.

No Python source/config changed, so not rerunning the entire regression suite is acceptable for this evidence-only checkpoint.

## 9. Fresh CI passes

Fresh GitHub Actions for exact commit:

`606e7a238428febf340428f43dc1732293f1f646`

completed successfully.

Thus the published archive hashes and documentation are backed by the exact pushed checkpoint commit.

## 10. No background/incomplete hashing ambiguity remains

Document 105 explicitly states that:

- all three hashes completed;
- aggregate completion time was recorded;
- no background hashing job remains active.

This is important because Document 103 had an intentionally stopped hash attempt. Document 105 cleanly supersedes that incomplete state without rewriting the earlier report.

## 11. Required next checkpoint

The next OULU checkpoint should move from archive-level identity to per-video media integrity.

At minimum it should:

1. enumerate exactly the 4,950 accepted OULU video members;
2. stream/read every individual video payload;
3. compute per-video SHA-256;
4. verify payload size against canonical/archive metadata;
5. run deterministic media probe/decode checks;
6. record duration, FPS and frame count;
7. identify corrupt/truncated/zero-frame videos;
8. confirm the frozen middle-frame transaction is physically available;
9. perform exact-content duplicate checks across IDs, roles and relevant partitions;
10. reconcile all outputs to frozen canonical IDs and frozen role assignments.

A useful distinction is:

- archive SHA-256 answers: **“which three TAR files were used?”**
- per-video SHA-256 answers: **“which exact media payload corresponds to each canonical video?”**
- decode audit answers: **“can each frozen transaction actually be evaluated?”**

All three layers are needed before OULU media readiness can be considered complete.

## 12. Role split must remain immutable

No later media problem, classifier error count, detector-success rate, or target behavior may trigger automatic role reallocation or seed retry.

If a video is technically unusable, it must be handled by the already frozen protocol/applicability rules and documented as such.

The permanent split itself remains immutable unless an explicit prospective protocol amendment is separately reviewed.

## Final disposition

**DOCUMENT 105 — ACCEPTED.**

**CHECKPOINT 1.5C OULU WHOLE-ARCHIVE BYTE PINNING — ACCEPTED WITHOUT REWORK.**

The supplied OULU TAR bytes are now reproducibly pinned.

**Per-video integrity, decode validation, content-duplicate audit and full OULU/core scientific readiness remain pending.**
