# 221 - Response to Review220: Recovery219-Aware Archive Guard

Date: 2026-10-20

Authority: [Review220](220-review-doc219-oulu-archive-identity-recovery.md)
accepts the reported Recovery219 content match and new environment binding,
and authorizes a separate guard adapter and tests only. It does not authorize
packet retry. Original219 pending/proposed/nonactivation flags remain immutable
creation-time facts; later Review220 is additive acceptance, not a rewrite.

## Prospective Criteria

1. Add an explicit Recovery219-aware adapter without changing historical177/
   Review178 guard behavior, old callers, frozen content anchors, archive pins,
   recovery records, packet selection, visual policy or environment. No automatic
   fallback, optional device check, archive rehash, payload access or packet retry.
2. Require explicit Review220 guard-only authority, exact219 document/aggregate/
   completed-success head/run/job/all12 CI, accepted219 binding/preflight/
   verification/observation digests and unchanged original177 lineage. Check exact
   three archive records, whole-file hash/size anchors and binding/row agreement;
   keep original frozen, accepted177 and accepted219 environment identities distinct.
3. Compare all five current stat fields with the accepted219 hashed identity on
   every explicit guard call; reject stale177 identity, every future stat-field
   drift, symlinks, binding/row/anchor/review/CI mismatch and protected evidence
   drift before output/payload access. Recheck identities before completion.
   Expose the same explicit check for future before/after-export use, without
   implementing or authorizing export in this checkpoint.
4. Add focused synthetic success/refusal coverage in the existing test file,
   preserve all old test ASTs and helper bytes, run focused/full regression in fas,
   verify actual read-only study guard success where current identity still
   matches accepted219, and separately confirm historical guard refusal remains.
   Synthetic guard success and read-only study success are not study export success.
5. Before private writes, bind criteria, code/test transition, source CI and prior
   evidence. Use the unchanged immutable writer for new preflight/guard result/
   verification only; never regenerate existing outputs or probe owner raw bytes.
   Preserve all owner fields/answers/reviewer metadata, AI/formal/import/activation
   records, historical pending/disagreement/nonactivation flags, frozen13/config17
   and all prior protected roots; retain new219 records as protected evidence.
6. Publish aggregate-only evidence and exact new CI, then STOP for formal221 guard
   review. Guard integration acceptance and packet retry authority remain pending;
   no automatic next review, extraction/decode, final-five80..84 export/replay,
   visual judgments, owner input/prose, other datasets or scientific execution.
   Effective/semantic-owner/AI80/85, five unviewed, historical disagreement1/
   unresolved0 and scientific_readiness=false remain unchanged.

## Execution

**PASS: ACTUAL READ-ONLY RECOVERY219-AWARE STUDY GUARD VALIDATION.**

**GUARD INTEGRATION REMAINS REVIEW-PENDING. PACKET RETRY IS NOT AUTHORIZED.**

### Explicit Adapter

Added [guard adapter](../scripts/verify_oulu_archive_guard_batch09.py), separate
from the unchanged historical177/Review178 guard and every packet caller. The
explicit `verified_archive_identities` API can be invoked before payload access
and again after export by a later authorized caller. This checkpoint does not
wire an automatic fallback into a packet runner or implement an export path.
Its CLI performs two explicit read-only checks, compares returned identities and
writes one new immutable guard result only after success.

The adapter strictly checks Review220/accepted219 public digests and exact219
head/run/job/completed-success/all12 CI; accepted219 binding/preflight/verification
and exactly three observation digests; original frozen pin SHA256/size/record
identity; complete accepted177/Review178 report/binding/observation lineage;
original-to177-to219 device-only transitions; historical pending/unaccepted flags;
and binding/row/preflight identity agreement. All identity values must be integers,
with exactly device/inode/byte_size/mtime_ns/ctime_ns. Frozen content authority
is separate from accepted219 environment fast identity.

All90 inherited protected maps, frozen13/config17 and singleton pins are required;
the one explicit old-to-new test pin is validated by whole-module AST comparison.
Four accepted219 recovery files add the91st protected root. Each actual archive
identity is taken from one `lstat`; regular-file and all five fields must match
the accepted hashed219 identity. Symlinks and every future drift fail closed.
No archive descriptor, TAR payload, FFmpeg decode or new whole-byte read is used.
No device omission, Review178 relabeling or implicit binding selection occurs.

### Tests And Actual Execution

One new method in [existing tests](../tests/test_oulu.py) creates complete synthetic
original/177/219 lineage and successful guard CLI-function output. It patches
archive opens to raise, tests accepted219 success, stale177 rejection, each of
five future stat drifts, drift between the two explicit guard calls, symlinks,
binding/row/anchor/review/preflight/verification changes, protected-map omission,
protected-byte drift, unsafe output and20 invalid authority/CI/protection variants.
Historical guard refusal is exercised separately. Fixtures are synthetic, not
study export or independently repeated full-byte archive verification.

Actual fas results, zero failures/errors/skips:

| Check | Tests | Seconds Including Discovery |
|---|---:|---:|
| New guard test | 1 | 0.459 |
| Focused OULU | 86 | 6.303 |
| Full regression | 273 | 62.257 |

Removing only the new method yields the exact accepted old module AST. All tracked
source/helper/guard/config/manifest bytes remain identical to the accepted base;
no code/test edits followed the final runs. REHASH/REHASH219 lines during regression
come only from inherited tiny synthetic fixtures, not another study105-GB read.

New immutable preflight was written/read back after frozen criteria, authority,
test-pin transition, current219 stat identities,91-root preservation and fresh
source219 CI were verified. Actual guard-only CLI ran once using fas's interpreter,
passed all three study archives and wrote exactly `guard_validation.json` under
new `oulu_archive_guard221_v1`; wall time59.774s includes two provenance/preservation
checks. Three current identities were independently rechecked afterwards. This is
actual read-only study guard success, not extraction/decode/export/replay success.

Five actual CLI output refusals covered existing221 preflight, existing221 output,
repository output, source overlap and dangling symlink. Four actual authority CLI
refusals covered wrong220, wrong219 run, missing guard authority and retry=true.
All returned the generic failure before any output; nonexistent targets remained
absent. Two overwrite probes targeted only the new preflight and new guard result,
both FileExistsError with unchanged bytes. Owner raw export was never a probe.

Post-execution preservation passed91 roots/all pins/frozen13/config17 and original
11681-byte owner export/all fields/answers/reviewer metadata. Original AI/formal/
import/activation records and disagreement/pending/nonactivation/counting flags
are unchanged. New immutable verification binds tests, source CI, source pins,
guard result, preservation, refusals and limits; structured readback plus a separate
independent digest/count/status check passed. The unchanged historical guard still
actually refuses current219 identity, as expected; no old behavior was bypassed.
All four planned batch09 packet/preflight/verification output paths remain absent.

### Evidence Bindings

The [aggregate](../results/phase1/oulu-recovery219-aware-guard-v1.json) exposes only
counts, digests and limits. Actual stat values, maps, owner metadata/answers,
candidate/video IDs and biometric assets stay private.

| Record | SHA256 |
|---|---|
| Review220 | `ad516d31c0b9df653b24fc32509f019d3fb8af9af94c54b54c2b7041dec40e3a` |
| Accepted219 document | `d944f7165035affdecad9baf23e9b7cb044bb4fe0b3de76754f3f3111bb81740` |
| Accepted219 aggregate | `919fd1d4f5f0f129e46f2d89eebf0887f78ed43cfb7d945ca4b58fcc25ac8cb1` |
| Accepted219 binding | `76f8ce03703ef512d25b9bf2212f20d1e156e2ba7a64be545a56e81d95b0ca38` |
| New guard adapter | `ac732a581d033275a361e147e11dd58f40aa20f0f7283d7b353b60516bee26fb` |
| Updated test file | `5aa711455344d6fa823f56b1ee8b8fe6407c8b9f568e0b1e785ed014af468288` |
| New221 preflight | `28f2845a53aad2f1951db83e026fc6abdd010cd6358ecd8f62fc51de90c4816e` |
| New221 guard result | `12b04b9e4c32aad143d4456984fdb7c312f804cbc4863fdf28f0ab62e4ab3dc5` |
| New221 verification | `256974dc8baced3a09f8da7e4fed7c2bc81281f277c67573611887e548528a03` |

Fresh source219 CI observed2026-10-20T02:51:27.878751+00:00: exact head
`3eed781b6d68fb6dddf725a56be9a3b69c25b505`, run39359791576/job118423022731,
both completed/success, all12 including Complete job; actual job completion
2026-10-20T02:36:43Z. Run completion is null, not inferred. This source CI is not
NEW221 publication CI and does not independently inspect private archive bytes.

### Stop Boundary

Publish221 and verify exact NEW head/run/job completed/success/all12 steps, then
**STOP FOR FORMAL221 GUARD INTEGRATION REVIEW**. Recovery219 is accepted by220,
but this new guard integration is pending, old packet callers remain unchanged,
and operational packet readiness stays blocked. A later accepted guard review
must explicitly authorize retry of exact80..84 with unchanged selection/evidence
rules and deliberate use of this explicit guard before and after export.

No automatic next review, packet retry, extraction/decode, replay, visual screening,
owner input/prose, archive repair/replacement/download, other datasets, research
models/training/evaluation, source dry run, analysis freeze or locked evaluation.
Current effective/semantic-owner/AI80/85, batch08 closed by216, five80..84 unviewed,
historical disagreement1/unresolved0, zero new packets/judgments/dispositions.
Original217 blocker and219 pending/unaccepted/blockerfalse flags are immutable
creation-time facts. Gates remain0/63/64/65/66; scientific_readiness=false.

Review220's private-byte acceptance remains reported-execution/commitment based,
not independent Windows hashing. Stat matching is a fast accepted-environment
check, not a perpetual cryptographic guarantee. Filesystem-change cause, capture
independence, global lineage clearance and independent scientific replication
are not established by this guard or software/CI success.