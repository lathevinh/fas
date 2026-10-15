# 178 — Review of Document 177: OULU Archive Identity Recovery

Date: 2026-10-15  
Repository: `lathevinh/fas`  
Reviewed commit: `4b6d3037e7ddbc21bbea0b321daf63ec9a33da5e`  
Reviewed document: `docs/177-review-response-doc176-oulu-archive-identity-recovery.md`  
Reviewed aggregate: `results/phase1/oulu-archive-identity-recovery-v1.json`  
Reviewed recovery runner: `scripts/recover_oulu_archive_identity.py`

## Verdict

**DOCUMENT 177 — ACCEPTED WITHOUT REWORK.**

**ARCHIVE CONTENT-IDENTITY RECOVERY — ACCEPTED.**

**THE DOCUMENT175 TECHNICAL ARCHIVE-CONTENT BLOCKER IS RESOLVED.**

**THE ADDITIVE ENVIRONMENT-IDENTITY BINDING IS ACCEPTED.**

**BATCH-06 PACKET PREPARATION ITSELF IS STILL NOT COMPLETE.**

**NEXT AUTHORIZED STEP: ADD A SEPARATELY REVIEWED RECOVERY-AWARE FAST STAT GUARD, THEN RERUN BATCH-06 PACKET PREPARATION FOR EXACT RANKS 50..59.**

No owner, license, administrative, or human visual re-review is required.

## 1. Review176 recovery requirement is satisfied

Review176 required a full-byte rehash of all three current OULU archives against the existing frozen whole-file SHA-256 anchors.

Document177 does exactly that.

All three current archives were read in full and compared to the previously accepted content authority.

## 2. All three whole-file hashes match the frozen authority

The recovery reads a total of:

**105,116,817,408 bytes**

and reports exact equality for all three archives.

- `Dev_files.tar` frozen/current: `3c3a17e0ebbea6d42aaa15d2d43fc9cc257f43372e424f5e5786f4b5a9e2d5f6`
- `Test_files.tar` frozen/current: `2f1f9d752751fdf2d09a763d4f2424cba8ced548800fd4d0bdc189a652274383`
- `Train_files.tar` frozen/current: `966127b8bc11b00215a1a2af530c2345ce50b12a54b59cc717650a0b9236a4d4`

Therefore the current archive bytes are identical to the previously frozen content authority.

## 3. The original device-only event is now correctly characterized

For each archive, the only stat field differing from the old immutable identity is `device`.

The following remain equal to the old records:

- inode;
- byte size;
- mtime;
- ctime.

This confirms that the previously observed event is limited to filesystem/environment identity rather than archive-content drift.

A specific cause such as remounting is still not independently proven, and Document177 correctly avoids claiming one.

## 4. Content identity is now established by SHA-256, not metadata inference

At Document175, matching inode/size/timestamps was insufficient to infer content equality.

Document177 now establishes content equality using the accepted whole-file SHA-256 anchors.

The archive-content blocker is therefore resolved.

## 5. Descriptor/path identity is stable during full-file hashing

The recovery runner checks regular non-symlink files, path identity before hashing, descriptor identity after opening, descriptor identity after hashing, live path identity after hashing, and final live identities before environment binding.

This prevents a file replacement or mutation during hashing from being silently accepted.

## 6. Recovery correctly fails outside the authorized device-only scope

`rehash_archive()` computes changed stat fields and requires exactly `["device"]`.

A size/hash mismatch, mutation during hashing, symlink, or any additional stat drift fails closed.

That is appropriate for this narrow recovery.

## 7. Old archive pins remain authoritative and unchanged

The October 9 archive pin records are not rewritten or repinned.

The new recovery references the old records and frozen hashes additively.

## 8. The new environment binding is properly additive

The new environment binding distinguishes:

- content authority = unchanged frozen SHA-256 + byte size;
- environment identity = current stable stat identity.

This is the correct conceptual separation.

## 9. Recovery does not silently change the packet runner

Document177 explicitly records:

`packet_runner_guard_changed = false`

and:

`packet_preparation_authorized_by_this_record = false`.

This is correct. The accepted recovery does not itself make Document175's old strict stat check pass.

## 10. No packet preparation occurred during recovery

Document177 correctly reports:

- pair packets: 0;
- selected videos decoded: 0;
- PNGs exported: 0;
- new AI judgments: 0;
- new human judgments: 0;
- new effective dispositions: 0.

Therefore Document177 is technical recovery only.

## 11. Current accepted screen-level state remains unchanged

Accepted current total remains **50**.

AI visual coverage remains **50 / 85**.

There are still **35** highest-risk candidates not yet AI visually reviewed.

## 12. Protected history remains intact

Document177 reports:

- 54 protected prior roots unchanged;
- frozen13 unchanged;
- study configs17 unchanged;
- old archive pins unchanged;
- Document175 blocked records unchanged;
- historical173 fields unchanged;
- prior owner/categorical/prose records unchanged.

## 13. Immutable recovery outputs are appropriately bounded

The recovery creates four immutable output records: three whole-archive rehash observations and one additive environment binding.

The records are independently read back and verified.

This readback is not a second independent 105-GB hash.

## 14. Overwrite/source-overlap protections pass

The checkpoint reports successful refusal of immutable overwrite, existing output, repository output, and source-overlap output.

## 15. Test coverage is strong

Focused regression: **73/73 passed**.

Full regression: **260/260 passed**.

The new synthetic recovery test exercises full-hash mismatch, size mismatch, archive mutation during hashing, unauthorized non-device stat drift, symlink/output refusal, input nonmutation, all-three success, and fail-fast behavior.

## 16. Fresh exact publication CI passes

Exact reviewed commit:

`4b6d3037e7ddbc21bbea0b321daf63ec9a33da5e`

Fresh GitHub Actions run:

`38673838230`

is `completed / success`.

Validate job:

`116222822739`

is also `completed / success`.

There is no publication-CI blocker.

## 17. The recovery record may now be treated as accepted technical authority

Before this review, the environment binding was correctly marked review-pending.

Review178 now accepts it as the additive current-environment identity authority for the three archives.

Do not rewrite the recovery JSON to remove its historical review-pending field. Review178 is the additive acceptance authority.

## 18. Next step must explicitly integrate the accepted environment binding

The next checkpoint should modify or wrap the batch06 preparation guard so that it can use the accepted current environment identity.

Preferred semantics:

1. frozen whole-file SHA-256 + byte size remain authoritative content identity;
2. accepted Recovery177 stat identity becomes the fast current-environment identity;
3. current stat identity must match the accepted Recovery177 binding before payload access;
4. if it matches, packet preparation may proceed without another 105-GB rehash;
5. selected extracted media must still match accepted per-video hashes and RGB-frame hashes;
6. any future stat drift fails closed and requires another narrow recovery.

## 19. Do not make `st_dev` globally optional

The next guard should not simply delete `st_dev` from identity checks.

The accepted event was resolved by a specific full-byte recovery and additive environment binding.

The correct implementation is to bind to the new accepted identity, not weaken the guard generically.

## 20. Recovery-aware guard needs its own tests

Test at minimum:

- exact current Recovery177 stat identity accepted;
- old pre-recovery stat identity not silently substituted;
- future device drift rejected;
- inode drift rejected;
- size drift rejected;
- mtime/ctime drift rejected;
- binding SHA mismatch rejected;
- archive-pin authority mismatch rejected;
- protected evidence drift rejected;
- no output on guard failure.

## 21. Then rerun batch06 preparation separately

After the recovery-aware guard checkpoint is reviewed, rerun fixed batch06 preparation for exact ranks `50..59`.

Normal downstream checks must remain: frozen queue order, tar member type/size, payload SHA-256, accepted RGB-frame hashes, temporal panels, minimum-Hamming trigger witness, deterministic sibling replay, and PNG/readback checks.

## 22. No owner or administrative action is required

This is purely technical integrity recovery.

Do not ask the owner to re-accept a license, repeat dataset permission, re-review ranks40..49, inspect images, or answer categorical questions.

## 23. Current authorized boundary

Review178 authorizes only a separate recovery-aware guard integration and subsequent batch06 packet-preparation retry path for ranks50..59.

It does not yet authorize AI visual adjudication, human categorical adjudication, rank60+, other datasets, source dry run, analysis freeze, locked evaluation, or research model execution.

## Final disposition

**DOCUMENT 177 — ACCEPTED WITHOUT REWORK.**

**ALL THREE CURRENT OULU ARCHIVE CONTENT HASHES MATCH THE FROZEN AUTHORITY.**

**THE DOCUMENT175 ARCHIVE-CONTENT INTEGRITY BLOCKER IS RESOLVED.**

**THE ADDITIVE CURRENT-ENVIRONMENT IDENTITY BINDING IS ACCEPTED.**

**BATCH06 PACKET PREPARATION REMAINS UNFINISHED.**

Next, create a separately reviewed recovery-aware fast guard using the accepted Recovery177 environment identity while retaining the original frozen SHA-256 + byte size as content authority. After that guard is accepted, rerun batch06 packet preparation for exact ranks50..59.

Future stat drift must continue to fail closed.

No owner/license/admin/human visual re-review is required.
