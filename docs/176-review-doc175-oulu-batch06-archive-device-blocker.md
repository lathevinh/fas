# 176 — Review of Document 175: OULU Batch-06 Packet Preparation Blocked by Archive Device Identity Drift

Date: 2026-10-15  
Repository: `lathevinh/fas`  
Reviewed commit: `d54f6723f3852bd1a0ef2d8d1862f1799639a0cb`  
Reviewed document: `docs/175-review-response-doc174-oulu-batch06-packets.md`  
Reviewed aggregate: `results/phase1/oulu-batch06-packets-v1.json`  
Reviewed runner: `scripts/prepare_oulu_visual_batch06.py`

## Verdict

**DOCUMENT 175 — ACCEPTED AS A VALID FAIL-CLOSED TECHNICAL-BLOCKER RECORD.**

**BATCH-06 PACKET PREPARATION — NOT ACCEPTED / NOT COMPLETE.**

**THE ARCHIVE-IDENTITY BLOCKER IS REAL AND WAS HANDLED CORRECTLY.**

**A NARROW ADDITIVE TECHNICAL RECOVERY IS AUTHORIZED.**

**NO AI/HUMAN REVIEW, NO RANK60+, NO OTHER DATASET WORK, AND NO MODEL EXECUTION IS AUTHORIZED UNTIL RECOVERY AND SUCCESSFUL BATCH-06 PACKET PREPARATION ARE REVIEWED.**

Document175 correctly refuses to reinterpret a device-only stat mismatch as either content drift or harmless remount. The current evidence is insufficient to prove either conclusion because the current archive bytes were not rehashed.

The correct next step is to establish current archive byte identity against the already frozen whole-file SHA-256 values.

---

## 1. Batch-05 closure is correctly carried forward

Review174 closed batch05 at screen level and advanced the accepted current screen-level total to 50.

Document175 preserves the historical Document173 review-pending fields rather than rewriting them and uses Review174 as additive authority.

This is correct.

No further owner input for ranks40..49 is required.

## 2. Intended batch-06 scope is correct

The planned next frozen queue block is exactly:

`50,51,52,53,54,55,56,57,58,59`.

The runner slices the accepted frozen queue as `records[50:60]` and additionally checks exact integer queue ranks and the expected priority.

There is no outcome-dependent skipping.

This is the correct queue continuation.

## 3. Packet preparation did not occur

Observed state is unambiguous:

- planned ranks: 50..59;
- actual packets: 0;
- expected selected videos: 16;
- decoded videos: 0;
- expected RGB frames: 2126;
- verified RGB frames: 0;
- exported PNGs: 0;
- main output root: absent;
- sibling output root: absent.

Therefore this checkpoint must not be described as a prepared packet batch.

Document175 correctly labels it blocked.

## 4. Failure occurred before selected payload access

The runner verifies protected/frozen records and archive identity before opening the selected media payloads.

The actual failure is:

`ValueError: archive identity drift`

and occurs before output creation and before selected payload access.

This is desirable fail-closed behavior.

## 5. The exact mismatch is narrow but not ignorable

For all three archives, the only changed stat field is:

`st_dev`.

The following continue to match their old pins:

- inode;
- byte size;
- mtime;
- ctime.

This pattern is compatible with a filesystem remount/device-number change, but it is not proof of one.

Conversely, `st_dev` drift alone is not evidence that the archive contents changed.

Document175 correctly asserts neither interpretation.

## 6. The current archive bytes have not yet been verified

The critical fact is:

`current_archive_bytes_rehashed = false`.

Therefore matching size/inode/timestamps cannot be used as a substitute for content verification.

The packet runner must remain blocked until byte identity is established.

## 7. Frozen whole-file SHA-256 anchors already exist

The accepted archive-byte-pinning checkpoint contains whole-file SHA-256 anchors:

- `Dev_files.tar`  
  `3c3a17e0ebbea6d42aaa15d2d43fc9cc257f43372e424f5e5786f4b5a9e2d5f6`
- `Test_files.tar`  
  `2f1f9d752751fdf2d09a763d4f2424cba8ced548800fd4d0bdc189a652274383`
- `Train_files.tar`  
  `966127b8bc11b00215a1a2af530c2345ce50b12a54b59cc717650a0b9236a4d4`

These are the correct content anchors for recovery.

No new arbitrary checksum should replace them.

## 8. Recovery must rehash all three archives

Because all three current archives show device-identity drift, recovery should recompute the full SHA-256 of all three current archive files.

Do not verify only the 16 selected videos and call the archive-identity problem resolved.

Selected payload hashes are useful downstream, but the present blocker concerns the identity of the archive containers that were previously frozen.

The recovery should compare exact current whole-file hashes against the existing accepted anchors.

## 9. Required recovery decision rule

For each archive:

### If current SHA-256 equals the frozen SHA-256

Then content identity is established despite the changed `st_dev`.

The project may create a **new additive technical environment-identity record** containing:

- archive name;
- frozen SHA-256 authority;
- old immutable stat identity;
- newly observed stat identity;
- explicit statement that only filesystem/environment identity changed;
- current full-file SHA-256 result;
- exact equality to the frozen content hash;
- Review176 authority.

The old pin must remain unchanged.

### If any SHA-256 differs

Then this is a genuine content-integrity blocker.

Stop immediately.

Do not decode selected payloads, do not regenerate archive pins, and do not continue batch06 until the changed archive source is investigated and separately reviewed.

## 10. Do not simply remove `st_dev` from the guard in place

The current guard is accepted historical code.

A recovery must not silently weaken:

```text
(device, inode, size, mtime, ctime)
```

to ignore the device field merely because it now fails.

That would convert an observed integrity event into an unreviewed policy change.

Any change in guard semantics must be explicit and additive.

## 11. Recommended long-term identity semantics

The project should distinguish two concepts:

**content identity**
- authoritative whole-file SHA-256;
- byte size.

**filesystem/environment identity**
- device;
- inode;
- mtime;
- ctime.

`st_dev` is an environment locator, not a content digest.

The frozen whole-file SHA-256 is stronger evidence of archive byte identity than a device number.

Therefore, after current full rehash equality is established, it is reasonable for a new reviewed guard to accept the current environment identity while retaining the frozen content hash as the content authority.

## 12. Avoid paying the 105-GB rehash cost on every batch

The three frozen archives total approximately 105 GB.

A sensible recovery design is:

1. full-rehash all three once now;
2. establish equality to the frozen hashes;
3. create an immutable additive current-environment binding;
4. subsequent packet batches may use the new reviewed stat identity as the fast pre-payload guard;
5. selected extracted video payloads continue to be verified against their accepted per-video hashes.

If the archive stat identity drifts again, fail closed and repeat the narrow identity-recovery procedure.

This retains rigor without forcing a 105-GB full rehash before every ten-pair batch.

## 13. Old archive pins must never be rewritten

The accepted October 9 archive pin records must remain historical authority.

Do not:

- overwrite old `file_identity`;
- replace old private pin records;
- change old SHA fields;
- pretend the new device ID was always present.

Recovery must create a new immutable record referencing the old one.

## 14. No license/administrative re-review is needed

This is a technical storage-identity issue.

It does not invalidate the previously accepted owner permission/license basis.

Do not ask the owner to repeat administrative or dataset-access attestations.

## 15. No human visual judgment is needed for recovery

Recovery is purely technical.

Do not ask the owner to inspect images or answer categorical content questions.

Only after successful packet preparation and later visual-review authorization should candidate adjudication resume.

## 16. Runner behavior is appropriately strict

The runner checks the live stat tuple:

```text
(st_dev, st_ino, st_size, st_mtime_ns, st_ctime_ns)
```

against the accepted private archive identity and stops on any mismatch.

Given the existing policy, this is correct behavior.

The problem is not that the runner failed; the failure is the evidence that triggered the required recovery path.

## 17. Downstream payload verification remains strong

Once the archive identity blocker is resolved, the runner still verifies each extracted selected media file by:

- tar member type;
- accepted member byte size;
- extracted file size;
- accepted per-video media SHA-256;
- accepted decoded RGB frame hashes;
- frozen pHash trigger witness.

Therefore accepting an additive archive-environment recovery does not remove downstream content checks.

## 18. Test evidence is satisfactory

Document175 reports:

- focused regression: **72/72 passed**;
- full regression: **259/259 passed**;
- prior test AST preserved apart from the one new method;
- diagnostics clean.

The new test covers Review174 acceptance/history/order, strict integer ranks, nonmutation, and output refusals.

There is no software-regression blocker.

## 19. Fresh exact publication CI passes

Exact reviewed commit:

`d54f6723f3852bd1a0ef2d8d1862f1799639a0cb`

Fresh GitHub Actions run:

`38669499099`

is:

`completed / success`.

Validate job:

`116209003838`

is also:

`completed / success`.

The successful CI establishes repository/software consistency for Document175.

It does not resolve the live archive-byte identity blocker.

## 20. Preservation evidence is good

Document175 reports:

- 54 protected prior roots unchanged;
- frozen13 unchanged;
- config17 unchanged;
- accepted visual helpers unchanged;
- old archive-pin records unchanged;
- previous owner/categorical/prose records unchanged.

This is the correct nonmutation behavior for a blocked checkpoint.

## 21. Zero-output state is important

Because the run stopped before output-root creation, there is no partially prepared batch06 packet tree that needs to be trusted, cleaned up, or merged.

The planned main and sibling roots do not exist.

This makes recovery cleaner.

Do not create an “empty successful batch” record from their absence.

## 22. Recommended recovery checkpoint

The next checkpoint should be narrow and named as a technical archive-identity recovery, not as batch06 packet preparation.

It should:

1. bind Review176 and Document175;
2. read the accepted archive-byte-pinning report;
3. independently hash all three current archive files;
4. record current stat identities;
5. compare each full SHA-256 exactly to the frozen SHA-256;
6. fail closed on any mismatch;
7. if all three match, write a fresh immutable additive environment-identity binding;
8. preserve old pins byte-for-byte;
9. run focused/full tests as appropriate;
10. publish aggregate results and fresh exact CI;
11. stop for review before rerunning batch06 packet preparation.

## 23. Batch06 packet preparation must remain a later checkpoint

Do not combine technical recovery and visual packet generation into one opaque step.

Preferred sequence:

`175 blocked record`
→ `Review176`
→ `archive identity recovery`
→ `review recovery`
→ `rerun batch06 packet preparation`
→ `review prepared packets`
→ `AI visual stage`.

This provides a clear audit trail.

## 24. Current scientific state

Current accepted screen-level total remains:

**50**.

AI visual coverage remains:

**50 / 85**.

Highest-risk pairs not yet AI visually reviewed:

**35**.

No progress on ranks50..59 should be counted from Document175 because zero packets were actually prepared.

## 25. Later stages remain blocked

Review176 does not authorize:

- AI visual adjudication for batch06;
- human categorical adjudication;
- rank60+;
- other datasets;
- research model execution;
- source dry run;
- analysis freeze;
- locked evaluation.

Only the narrow archive-identity recovery is authorized.

## Final disposition

**DOCUMENT 175 — ACCEPTED AS A CORRECT FAIL-CLOSED BLOCKER RECORD.**

**BATCH06 PACKET PREPARATION — NOT COMPLETE AND NOT ACCEPTED.**

**NO DATA LOSS OR CONTENT CHANGE IS INFERRED FROM `st_dev` DRIFT ALONE.**

**NO CONTENT EQUALITY IS INFERRED FROM MATCHING INODE/SIZE/TIMESTAMPS ALONE.**

**AUTHORIZED NEXT STEP: REHASH ALL THREE CURRENT OULU ARCHIVES AGAINST THE EXISTING FROZEN WHOLE-FILE SHA-256 VALUES.**

If all hashes match, create a separate additive environment-identity binding and obtain formal review before rerunning batch06 packet preparation.

If any hash differs, retain the hard technical stop and investigate the archive source; do not repin around the mismatch.

No owner/admin/human visual re-review is required for this technical recovery.
