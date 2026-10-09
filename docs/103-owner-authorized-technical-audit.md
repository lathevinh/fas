# Owner-Authorized Technical Audit

Date: 2026-10-09
Base: `3ded7e0`

The owner directly confirms that all supplied core datasets are permitted for
research and instructs proceeding without acquisition-receipt administration.
This dated operational decision supersedes Document 102's receipt prerequisite
for technical inspection of the already supplied OULU-NPU, CASIA-FASD, MSU-MFSD
and SiW-Mv2 releases. Do not ask the owner for administrative JSON, email approvals
or license files as a prerequisite to this research workflow.

Permission basis is **owner attestation**, not independent official-channel or
license verification. Do not fabricate receipt fields, a download date, owner
checksum, upstream release identity or redistribution evidence. Historical receipts,
reports, frozen registry and allocation policy remain unchanged. Existing intake
checker semantics are not weakened or falsely reported as passed.

Read-only technical inspection of existing ignored archive locations is authorized
in place; do not move/copy the archives merely to satisfy a storage convention.
New private inventories, extracted media or other derived artifacts must remain
outside Git. No raw/biometric content may be published.

## Technical Checkpoint

Start with OULU only, using the accepted metadata parser and frozen canonical
records. Pin the actual local archive bytes with SHA-256, check safe TAR headers,
full documented media/sidecar universe and protocol memberships, and reconcile
every video identity, label, partition, member path and size with the accepted
canonical inventory. Preserve all exact source-role and canonical hashes.

These local archive hashes are reproducibility baselines, not confirmation against
an independently supplied publisher checksum. Reading whole archive bytes for
hashing is distinct from opening individual video streams or decoding frames.
Header/protocol reconciliation alone does not prove video integrity, decode success,
content-level duplicate absence, detector adequacy or scientific readiness.

No extraction, media decoding, detector/model execution, new role generation or
target-output inspection is included in this bounded checkpoint. Keep data-audit,
source-dry-run, analysis-freeze and locked-evaluation blocked until their technical
requirements are actually met. Later prediction-event insufficiency cannot change
the permanent split. Publish actual technical evidence, push, then stop for the
owner to confirm this checkpoint before another dataset or decoded-media work.

## Actual Technical Result

[Immutable OULU technical report](../results/phase1/oulu-technical-archive-preflight-v1.json)
records 4950 videos and 42 protocol files reconciled. Every parsed video field,
including identity, label, original split, archive-member path/size and protocol
memberships, equals the accepted frozen canonical record. README/protocol hashes
match the accepted inventory; all 13 frozen artifacts and source-role hashes remain
unchanged. OULU focused tests pass 17/17 in existing `fas`.

The three media TARs total 105116817408 bytes. Whole-archive SHA-256 was started,
then stopped before completion to keep this checkpoint bounded; those hashes are
explicitly pending, not reported as verified. The attempted hash read opaque
container bytes, but no individual video stream was opened or decoded. Full archive
hashing, per-video integrity, decoding and duplicate-content checks remain technical
follow-ups. No Python code/config or audit summary changed; full regression was not
rerun. Schema passes; four later scientific stages remain blocked.

**Administrative prerequisite removed; technical header/protocol check passed,
full media audit not complete.** Stop for checkpoint confirmation after publication.