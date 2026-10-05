# 72 — Review of Phase 1 Step 1.2 Intake Contract

Date: 2026-10-05
Repository: `lathevinh/fas`
Reviewed commit: `e55641d70f6701e61f4e0da5f20aedb5d37c46ff`
Reviewed checkpoint: `docs/70-phase1-step1.2-intake-contract.md`

## Verdict

**APPROVED — Checkpoint 1.2 Intake Contract is complete.**

No blocker or major issue was found that could cause incorrect dataset lineage, silently accept changed acquisition artifacts, infer labels/splits from storage structure, or expose protected/private acquisition content.

Checkpoint 1.3 may proceed.

## What was verified

### 1. Acquisition identity is explicit

The receipt requires explicit:

- dataset
- release_id
- protocol_id
- owner
- acquisition channel
- channel reference
- download date
- permissions
- evidence records
- raw root
- archive inventory
- protocol inventory

Unknown/extra fields are rejected by exact schema matching.

### 2. Hashes are checked against actual bytes

Archive, protocol and evidence records contain `id`, `relpath`, and SHA-256.

The validator opens declared evidence files read-only and recomputes SHA-256 from actual bytes. Missing, unreadable, empty or changed files block verification.

This prevents a receipt from passing solely because a syntactically valid digest string was supplied.

### 3. Acquisition-channel contract is sufficiently strict

Allowed channels are:

- official
- owner_designated
- owner_confirmed_mirror

An owner-confirmed mirror additionally requires a hashed `mirror_equivalence` evidence record. Unconfirmed mirrors fail.

The validator verifies declared evidence identity/bytes; it correctly does not claim to authenticate the human author of an agreement.

### 4. Path safety is strong enough for this checkpoint

The implementation rejects:

- absolute paths
- `..` traversal
- noncanonical `//` and `./`
- Windows drive/backslash syntax
- control characters
- paths outside the private data root
- repository overlap
- wrong storage category
- symlink escape
- symlink loops
- duplicate IDs
- duplicate relpaths
- aliases resolving to the same file

This is more than sufficient to prevent intake lineage from silently pointing at unintended files.

### 5. No label/split inference exists

This checkpoint contains no dataset parser or media-label logic.

The receipt schema does not contain a label or split field. A test explicitly injects:

```text
official_split = inferred-from-folder
```

and expects rejection.

Therefore Step 1.2 cannot silently establish scientific labels or partitions from directory names.

### 6. No media decode occurs

The implementation reads only declared agreement/archive/protocol bytes for hashing.

A guarded-media test creates a file under the media directory and patches file opening so any access to that media raises immediately. The valid intake still verifies.

Thus no hidden media decode/inspection is occurring in Step 1.2.

### 7. Private information is redacted from CLI output

The CLI output contains only verification status, errors, scope and the no-media-decoding marker.

Tests verify that private root paths, protected references, owner identities and synthetic release IDs do not appear in stdout or the immutable public report.

Errors also avoid echoing user-supplied private values.

### 8. Output semantics are safe

The CLI:

- returns 0 for verified receipt;
- returns 1 for legitimate blockers;
- returns 2 for malformed/inaccessible input/output conditions;
- refuses repository-contained receipts;
- refuses output colliding with receipt/private data root;
- refuses overwrite through immutable-record semantics.

### 9. Permissions do not accidentally grant downstream rights

Permission categories must be explicitly one of:

- allowed
- prohibited
- unknown

Restrictive permissions do not block read-only hash verification, and successful intake does not imply extraction/training/publication authorization.

This separation is correct.

### 10. Tests and CI

The checkpoint reports:

- 17 intake tests: pass
- 93 total tests: pass
- environment/schema remain ready
- downstream scientific stages remain closed
- freeze writer remains blocked
- fresh CI for exact commit `e55641d70f6701e61f4e0da5f20aedb5d37c46ff`: completed / success

## Scope assessment

The checkpoint correctly does **not** claim:

- real release acceptance;
- protocol semantic correctness;
- official label mapping;
- subject/video identity correctness;
- media inventory completeness;
- frame decoding correctness;
- leakage-free manifests;
- target-evaluation readiness.

Those remain Steps 1.3–1.5.

## Non-blocking note

The intake validator verifies only files declared in the receipt. It does not prove that the steward listed every file belonging to an official release.

That is acceptable here because completeness/reconciliation belongs to the dataset adapters and core audit. It should not be promoted later as evidence of complete release coverage by itself.

## Final disposition

**CHECKPOINT 1.2 INTAKE CONTRACT — ACCEPTED**

Proceed to **Checkpoint 1.3 — Dataset Adapters**.

No Step-1.2 rework is required before continuing.
