# 104 — Review of Document 103: Owner-Authorized OULU Technical Audit Preflight

Date: 2026-10-09  
Repository: `lathevinh/fas`  
Reviewed commit: `a6b56e4c2732e56c3ae78682384584d9aebd3a43`  
Reviewed document: `docs/103-owner-authorized-technical-audit.md`

## Verdict

**DOCUMENT 103 — ACCEPTED FOR ITS BOUNDED SCOPE.**

**OULU HEADER/PROTOCOL TECHNICAL PREFLIGHT — ACCEPTED.**

**FULL OULU MEDIA AUDIT / CHECKPOINT 1.5 — NOT YET COMPLETE.**

No blocker was found in the technical header/protocol reconciliation itself. The report correctly preserves all downstream scientific gates as blocked and does not overclaim unfinished media verification.

## 1. Administrative-receipt prerequisite is correctly separated from technical evidence

Document 103 records the owner's direct research-use attestation for the supplied datasets and explicitly states that this is not independent publisher/license verification.

That is acceptable as an operational project decision.

The document correctly does not fabricate acquisition receipts, download dates, publisher checksums, upstream release certification, or redistribution rights.

Technical inspection may therefore proceed under owner authorization, but manuscript/release language must not describe this as independently verified licensing or provenance.

## 2. Frozen role/canonical lineage remains intact

The OULU preflight binds against the already frozen source-role registry and accepted canonical records.

Reported immutable anchors include:

- frozen OULU roles SHA-256: `ed415897ecf8b0c4abcb110f660c25b19a36b3a35b8780858e10f7d1acd2f38d`;
- frozen registry SHA-256: `dcb6860522c04bc1a69d7c5a4b62809a7c046ee57e25132b6988b131e59a4e8f`;
- all 13 frozen artifacts unchanged.

No role reallocation occurred.

## 3. OULU identity/protocol reconciliation is accepted

The technical result reports:

- 4,950 canonical videos reconciled;
- 42 protocol files reconciled;
- README hash matches accepted inventory;
- protocol archive hash matches accepted inventory;
- every parsed video field equals the frozen canonical record.

The checked equality covers identity, label, original partition, archive member path/size and protocol memberships.

This is stronger than an aggregate count-only check and is sufficient for a bounded header/protocol preflight.

## 4. Container inspection is not media validation

The report explicitly states that no individual video payload was opened or decoded.

Reading TAR headers and opaque archive bytes does not establish:

- video payload integrity;
- successful decoding;
- codec/FPS/frame-count correctness;
- frame-selection viability;
- detector success;
- content-level duplicate absence.

This distinction is scientifically correct and must be retained.

## 5. Mandatory remaining step: complete archive hashing

The three OULU media TARs are:

- `Dev_files.tar`: 28,151,992,320 bytes;
- `Test_files.tar`: 39,211,162,112 bytes;
- `Train_files.tar`: 37,753,662,976 bytes.

Total: `105,116,817,408` bytes.

However, all three SHA-256 values remain `null`.

The full-byte hashing attempt was explicitly stopped before completion.

Therefore the local media archive bytes are **not yet cryptographically pinned**.

This is not a defect in Document 103 because the document clearly labels the hashes as pending. It is, however, a mandatory next technical step before claiming archive-integrity completion.

## 6. Media-level audit remains required after archive pinning

After complete archive hashing, the OULU audit still needs media-level checks according to the frozen protocol, including at minimum:

- open every eligible media entry;
- compute per-video SHA-256 or equivalent immutable content identity;
- verify successful demux/decode;
- record codec/container;
- record duration;
- record FPS;
- record frame count;
- identify corrupt/truncated/zero-frame videos;
- confirm deterministic middle-frame selection can be performed;
- perform content duplicate / near-duplicate lineage checks required by the study.

These checks must reconcile back to the exact frozen canonical IDs and permanent roles.

## 7. Content disjointness is still unproven

The current status:

`content_duplicate_audit = not_verified_no_media_hashes`

is correct.

Subject/video identity disjointness from the frozen role stage does not prove that two different IDs do not contain duplicated or derived media.

Do not promote source-role leakage safety from identity-level to content-level until media hashes/duplicate audit are complete.

## 8. Scientific stage gating remains correct

Document 103 leaves:

- data-audit blocked;
- source-dry-run blocked;
- analysis-freeze blocked;
- locked-evaluation blocked.

Only schema remains unblocked.

That is the correct state.

A successful header/protocol reconciliation must not authorize training, detector inference or target evaluation.

## 9. Test and CI evidence

OULU focused tests report 17/17 pass with zero failures/errors.

No Python code/config was changed for the technical result, and the document explicitly states that full regression was not rerun.

That is acceptable for this bounded documentation/evidence update.

Fresh GitHub Actions on exact commit `a6b56e4c2732e56c3ae78682384584d9aebd3a43` completed successfully.

## 10. Wording recommendation

Use a precise label such as:

**“OULU archive-header/protocol reconciliation passed; media integrity pending.”**

Avoid shortening this to:

**“OULU audit passed”**

because that would imply archive hashes, per-video payload integrity and decoding were already verified.

## Required next action

Continue the OULU technical audit without changing the frozen split:

1. finish SHA-256 of all three complete TAR files;
2. record those hashes immutably;
3. verify per-video payload integrity and decode metadata;
4. perform content duplicate checks;
5. reconcile all resulting evidence to the existing canonical IDs and frozen roles;
6. keep all model/source-dry-run/target stages blocked until their own gates are satisfied.

No role regeneration or policy revision is permitted in response to media/model outcomes unless a separate prospective protocol amendment is explicitly reviewed.

## Final disposition

**DOCUMENT 103 — ACCEPTED.**

**OULU HEADER/PROTOCOL TECHNICAL PREFLIGHT — ACCEPTED WITHOUT REWORK.**

**FULL OULU MEDIA AUDIT / CORE CHECKPOINT 1.5 — STILL PENDING.**
