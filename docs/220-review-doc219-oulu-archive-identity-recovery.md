# 220 — Review of Document219: OULU Archive Identity Recovery

Date: 2026-10-20

## Verdict and evidence basis

Reviewed commit: `3eed781b6d68fb6dddf725a56be9a3b69c25b505`.

Reviewed [Document219](219-review-response-doc218-oulu-archive-identity-recovery.md), its [aggregate](../results/phase1/oulu-archive-identity-recovery219-v1.json), new recovery runner, inherited full-byte hash helper, added synthetic test, Review218, historical recovery authority and fresh exact219 CI.

**DOCUMENT219 — ACCEPTED WITHOUT REWORK FOR TECHNICAL ARCHIVE-IDENTITY RECOVERY.**

**THE REPORTED THREE FULL-BYTE SHA256 / SIZE MATCHES ARE ACCEPTED; RECOVERY219'S NEW ENVIRONMENT BINDING IS ACCEPTED AS ADDITIVE CURRENT-ENVIRONMENT AUTHORITY.**

**NEXT AUTHORIZED STEP: SEPARATE EXPLICIT RECOVERY219-AWARE GUARD INTEGRATION AND TESTING. PACKET RETRY IS NOT YET AUTHORIZED.**

This Windows reviewer inspected public code/tests, checked public provenance hashes and exact CI, but did not access or hash the private105-GB archives, read their private stat observations or reproduce private preservation checks. Acceptance of actual whole-byte execution and private binding contents relies on the recorded recovery report and published commitments. This is not an independent full-byte verification by this reviewer.

## Authority and implementation assessment

Review218 permits read-only recovery for exactly the three existing archives, not guard updates or export retry.219 enforces current Review218/accepted217/blocker/CI authority and requires recovery=true, packet_retry=false and guard_integration=false before execution.

The wrapper binds original frozen SHA256/size/pin records and validates accepted177/Review178 report, binding and observations. It checks original pre177 identity separately from the latest accepted177 environment identity. Device-only drift is required against the latter before full reads; this avoids treating an older original pin as the current accepted environment.

The unchanged full-byte helper checks regular non-symlink files, byte size, source/open-descriptor/post-hash five-field identities and SHA256 against frozen content authority. The wrapper requires exact preflight identity before/after each hash and rechecks source/descriptors before binding. Additional non-device drift, identity changes or hash mismatch fail closed. No weakening of device checks or silent fallback was identified.

Only new immutable observations and a proposed binding are produced. Recovery177, original pins, packet guards and prior records remain historical authority.219 correctly does not label itself accepted_by_Review178 or claim it has updated a packet guard. Its pending/proposed=false fields are creation-time facts; Review220 supplies later acceptance without rewriting them.

The newly added test includes a successful complete synthetic recovery, not only source-string assertions. It checks original/latest identity distinction, exact synthetic hashes, pending flags, expanded drift/symlink/hash failures, authority/CI/code refusals before hashing and unsafe outputs. Reported local new1/focused85/full272 passes are separate from direct CI observations; no local tests or prior-module AST comparison were rerun by this reviewer. The disclosed initial wrong-class loader is not a substantive failure after the correctly discovered method passed.

## Reported actual execution and counting

| Archive | Reported bytes hashed | Frozen SHA256 |
|---|---:|---|
| Dev_files.tar | 28151992320 | `3c3a17e0ebbea6d42aaa15d2d43fc9cc257f43372e424f5e5786f4b5a9e2d5f6` |
| Test_files.tar | 39211162112 | `2f1f9d752751fdf2d09a763d4f2424cba8ced548800fd4d0bdc189a652274383` |
| Train_files.tar | 37753662976 | `966127b8bc11b00215a1a2af530c2345ce50b12a54b59cc717650a0b9236a4d4` |

The sum is105116817408 bytes, matching the aggregate and frozen sizes. Reported hash times sum to1251.989 seconds;2094.668 seconds is whole-CLI wall time including preservation and record work. The two measures are explicitly distinguished and not contradictory.

Reported four new files comprise three rehash observations and environment_binding.json. Five actual CLI output refusals, four authority refusals, three distinct overwrite-refusal targets and90-root/frozen13/config17 preservation are reported private results. Owner raw bytes were not probe targets. No independent replay of a second105-GB rehash is needed solely for reassurance.

The report's binding does not explain the filesystem-change cause or prove scientific independence. Acceptance establishes the reported content match and accepted environment binding at recovery time, subject to unchanged future-drift refusal. It is not a perpetual integrity guarantee.

## Public bindings and exact219 CI

Eight public SHA256 checks match after Windows CRLF-to-repository-LF normalization: Review218,217 document,217 aggregate, new recovery runner, updated test file, frozen archive-pin report, accepted177 aggregate and Review178. Runner hash is `8ae6e3cc5483caf0d965ba2d05e0d06e5aa25ea55d0059e511a0371390267a0c`; test hash is `e94b2003a64104403d9f99cae1dc39a34f2bd456161f293aac9914d731b2e2b2`.

Accepted private binding commitment: `76f8ce03703ef512d25b9bf2212f20d1e156e2ba7a64be545a56e81d95b0ca38`. Private binding/preflight/verification bytes were not independently opened here.

GitHub API observations directly verify:

| Item | Result |
|---|---|
| Exact head | `3eed781b6d68fb6dddf725a56be9a3b69c25b505` |
| [Run39359791576](https://github.com/lathevinh/fas/actions/runs/39359791576) | completed / success |
| [Validate118423022731](https://github.com/lathevinh/fas/actions/runs/39359791576/job/118423022731) | completed / success |
| Job completion | `2026-10-20T02:36:43Z` |
| Listed steps | 12/12 success |

Synthetic regression, schema and fail-closed checks passed. No fresh219 publication CI blocker remains. CI does not itself verify private archive hashes or replace the recovery report.

## What closes and what remains pending

The217 content-identity question is resolved at this review's accepted-report level by matching the unchanged frozen hashes and accepting the new stable environment binding. The old guard still refuses current device identity, correctly: it has not yet been integrated with accepted Recovery219. Operational packet-preparation readiness therefore remains blocked pending guard integration/review and explicit retry authority.

Do not rewrite217's blocker or219's archive_identity_blocker_closed=false/proposed_binding_accepted=false/pending fields. They describe earlier states. This review is the additive recovery acceptance, not evidence that the old guard has started passing.

## Guard-integration authority and required checks

After Review220 is committed, implement a separately reviewed explicit guard path for accepted Recovery219. Prefer a new wrapper/adapter that preserves old177/Review178 guard behavior and historical callers. Bind this review, exact219 document/aggregate/CI and accepted private binding/observation digests, with frozen SHA256/size and complete original177 lineage retained.

The new path must verify exact three archive records, binding/observation agreement, stable hashed current identities and all five current stat fields before payload access and after export. Keep archive content authority separate from environment fast identity. No automatic fallback, device omission, relabeling as Review178 acceptance or alteration of old immutable records is permitted.

Test the exact accepted219 identity, stale177 identity rejection on the new path, every future stat-field drift, binding/row/anchor/review/CI mismatch, symlinks, protected evidence drift, no output/payload access on failure, and continued historical guard behavior. Include actual read-only study guard validation against the accepted binding where available; synthetic success alone must not be called study export success.

Publish the guard integration and exact new CI, then stop for review. This review authorizes implementation/testing of the guard path only, not final-five payload extraction, decode, packet export/replay or visual screening. A later accepted guard review must explicitly authorize retry of exact80..84 under unchanged selection/evidence rules.

No new full-byte archive rehash is required merely because integration follows recovery if current identity still matches the accepted219 binding; any drift must fail closed and be reviewed. No archive repair/replacement/download, owner input/prose, other datasets or scientific execution is authorized.

## Retained accepted state

Effective total, semantic owner outcomes and AI coverage remain80/85 each. Batch08 remains closed by Review216. Five exact ranks80..84 remain not AI-screened; new packets/judgments/dispositions remain0. Historical disagreement1/unresolved0 is preserved separately from technical guard readiness.

Source dry run, research models/training/evaluation, analysis freeze and locked evaluation remain blocked. Scientific readiness is false. Byte identity, accepted recovery and software success do not establish capture independence, global lineage clearance or independent scientific replication.
