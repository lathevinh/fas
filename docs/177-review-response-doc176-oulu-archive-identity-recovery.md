# Response to Review176: OULU Archive Identity Recovery

## Prospective Criteria

[Review176](176-review-doc175-oulu-batch06-archive-device-blocker.md) accepts
[175](175-review-response-doc174-oulu-batch06-packets.md) as a fail-closed blocker
record, not as completed batch06 packet preparation. Only this separate technical
recovery is authorized. Current accepted screen-level total remains50.

- Bind Review176,175 evidence, exact successful175 publication CI, the accepted
  archive-byte-pinning report and all three unchanged private October9 pin records.
- Independently read every byte of Dev_files.tar, Test_files.tar and Train_files.tar
  using SHA-256 in existing conda fas. Compare each full-file digest and size to
  the existing frozen content authority, never to a newly chosen checksum.
- Check the open descriptor and live path stat identities before/after each hash,
  then all archives again before binding. Reject symlinks, unstable identity,
  hash/size mismatch or drift outside the authorized device-only event. Stop on
  the first failure; no environment binding may be emitted unless all three pass.
- If all match, create a fresh immutable additive environment-identity binding
  referencing old pins, old/new stat identities, whole-file hashes and Review176.
  Distinguish unchanged content from changed filesystem identity; do not claim an
  independently established remount cause. Preserve all old pins byte-for-byte.
- Preserve54 prior roots, frozen13, config17, accepted shared helpers/runners,
  owner answers, historical pending flags, roles, selector, thresholds and seeds.
  Keep the175 preflight/blocked verification unchanged and pin both additionally.
- The binding is a review-pending proposal for a later explicit fast stat guard.
  Do not change or bypass the accepted packet runner, rerun packet preparation,
  extract/decode selected payloads, create batch06 packets or perform AI/human
  adjudication. Do not start ranks60+, other datasets or research models.
- Test full-hash mismatch, size mismatch, file mutation during read, unauthorized
  stat drift, output refusal, input nonmutation, all-three success and immediate
  stop without binding on a later archive mismatch. Preserve all prior test AST.
- Verify private immutable readbacks, actual overwrite refusal and all protected
  maps before/after execution; publish aggregate hashes/counts only, run focused
  and full regressions, commit/push and obtain fresh exact177 software CI.
- Stop for formal recovery review before any separate packet-preparation retry.
  No administrative, license, human visual or repeated owner input is required.

## Scope

This checkpoint establishes technical content identity only, if all full-file
hashes match. It does not certify capture independence, clear visual candidates,
advance screen-level dispositions or establish scientific readiness. Source175
software CI is not new177 publication CI. Later scientific gates remain blocked.

## Execution

**ALL THREE CURRENT WHOLE-FILE SHA-256 VALUES MATCH THE FROZEN AUTHORITY.**

**ADDITIVE ENVIRONMENT BINDING CREATED; FORMAL RECOVERY REVIEW IS STILL PENDING.**

The separate [recovery runner](../scripts/recover_oulu_archive_identity.py)
independently reads105116817408 bytes using `hashlib.file_digest`. The immutable
preflight recorded the criteria above before any current archive bytes were read.
The runner emitted its final success aggregate with3 verified archives only after
post-hash protected-input checks and a final live-stat check of all three archives.

| Archive | Bytes Read | Full SHA256 Equal To Frozen Authority | Hash Seconds |
|---|---:|---|---:|
| Dev_files.tar | 28151992320 | Yes | 335.876 |
| Test_files.tar | 39211162112 | Yes | 481.524 |
| Train_files.tar | 37753662976 | Yes | 432.949 |

The exact frozen digests remain those in the accepted
[archive-byte-pinning aggregate](../results/phase1/oulu-archive-byte-pinning-v1.json)
and Review176. The [new aggregate](../results/phase1/oulu-archive-identity-recovery-v1.json)
publishes those same digests and equality results, not replacement content anchors.
Each private observation binds its old immutable pin, old/new stat identities,
current whole-file hash, byte size, Review176 and this new preflight.

For each archive, only `device` differs from the old stat identity; inode, size,
mtime and ctime match. Descriptor and path stat identities stayed stable throughout
each full-file read and still match at final verification. Content equality is now
established by SHA-256, not inferred from metadata. The changed identity is limited
to filesystem/environment identity; a remount cause is not independently proven.

Four immutable recovery output files exist: three whole-archive rehash observations
and one additive environment binding. Independent readback verifies every binding
and all four file hashes. Actual immutable overwrite, existing-output, repository
output and source-overlap attempts are refused without changing any output bytes.
This is record readback, not a second independent105-GB rehash or media inspection.

All54 prior roots, frozen13, study configs17, old archive records and accepted
helpers/runners remain unchanged. The175 preflight and blocked verification are
additionally hash-pinned and preserved. Historical173 pending flags, original owner
answers and categorical/prose records are not rewritten. Review174 still supplies
the additive accepted current50 interpretation and batch05 closure.

The existing test file adds one synthetic recovery method, preserving all prior
test AST. It exercises whole-hash/size mismatches, mutation during hashing,
non-device drift, symlink/output refusal, nonmutation, all-three success, and a
second-archive mismatch stopping before any binding or third-archive read.
Focused73 tests pass in4.473s; full260 pass in46.919s in existing conda fas.
No code/test edits follow these regressions; diagnostics and publication checks
are required before commit.

An early final-readback attempt observed no binding while the runner was still
performing post-hash checks and stopped before writing verification. After the
actual completion notification and final binding, the same focused check passed
and wrote the new immutable verification. No hash was rerun, no preflight or
observation was regenerated, and no absent binding was treated as success.

## Evidence Bindings

| Record | SHA256 |
|---|---|
| Review176 | `e5cf397ba1d1eaa24449c82a2d48547a78553ae344d598a98b6c59b79143738b` |
| New recovery runner | `cbfd32dd216e613687e1b051af85ee3c68b25a4b1128764e62f382c0678f6095` |
| Existing test file with one new method | `52c547d479beaf7dfca515252fcc13cb4e3c6499e6660784ba8ed7d54c94c4ab` |
| Accepted archive-pin aggregate | `412b6a6d1e239d70edffc8136997890b822ab21c00ecb09ebfa7c4c0371dd875` |
| New private preflight | `1e67d34e800ec006fe7c72732ebe947fbf79bccc4e3d1a6a70cb825af487c12b` |
| Dev rehash observation | `e3114656e440b1dcecb2a0fceb1a93c1a4c3869db88ff9afb3d4473537a09e05` |
| Test rehash observation | `b09dd1144fb4697ea8ed980a9c9708aa93df9e6eedac3af054c6b0be7c69bb11` |
| Train rehash observation | `b609b5e5b1a7f5a1a9cd1dc41e3a34c7b632560646d595b505835e7de30ad16b` |
| Additive environment binding | `c82ac8cace2b19a75ed65d6974e8d9dccaf5dbd051f95b2998d5d9837a14b0b4` |
| New private verification | `a7c52975c070edb1611cce848356aa7635d25e51434c580bcd48a14efb798724` |

Private immutable records use the new `oulu_archive_identity_recovery_v1` root,
`oulu_archive_identity_recovery_preflight_v1.json` and
`oulu_archive_identity_recovery_verification_v1.json`. Do not regenerate them.
Device/inode numbers, private paths, candidate IDs, owner identifiers, answers and
biometric assets are excluded from the public aggregate.

## Exact Source CI

Source175 full head `d54f6723f3852bd1a0ef2d8d1862f1799639a0cb` is successful:
[run38669499099](https://github.com/lathevinh/fas/actions/runs/38669499099)
links that exact full commit and reports Success;
[validate116209003838](https://github.com/lathevinh/fas/actions/runs/38669499099/job/116209003838)
reports succeeded and Complete job. One fresh no-cache REST request returned403;
the exact official run/job pages provide the fallback observation. Absolute
completion times remain null, not inferred from relative page text.

Source175 CI is not new177 publication CI. Publish this recovery and independently
observe exact177 software CI before handoff. Neither CI substitutes for full-file
equality or formal recovery acceptance.

## Stop Boundary

Stop for formal177 recovery review. The new binding remains review-pending and
does not authorize packet preparation. No accepted guard was changed or bypassed.
A later explicitly reviewed guard may use this binding's current stat identity
as a fast check while keeping the original frozen SHA-256 and size as content
authority. Future stat drift must fail closed and require new narrow recovery.
This checkpoint does not implement or silently activate that future guard.

Batch06 main and sibling packet roots are still absent:0 packets,0 selected-video
decodes,0 PNGs and0 new AI/human/effective dispositions. Do not rerun batch06,
start ranks60+, other datasets, models or scientific stages. No owner, license,
administrative or human visual input is needed for this recovery.

Accepted current total remains50; AI coverage50/85 leaves35 highest-risk pairs
unreviewed. Scientific blockers remain schema0/data-audit63/source-dry-run64/
analysis-freeze65/locked-evaluation66. Technical content identity is not visual
clearance, capture certification or scientific readiness.