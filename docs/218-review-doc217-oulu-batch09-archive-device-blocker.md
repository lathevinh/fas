# 218 — Review of Document217: OULU Batch09 Archive Device Blocker

Date: 2026-10-20

## Verdict

Reviewed commit: `9082585c811ee3b1636b33145e5748876083ef30`.

Reviewed [Document217](217-review-response-doc216-oulu-batch09-packets.md), its [aggregate](../results/phase1/oulu-batch09-packet-preparation-blocker-v1.json), new batch09 runner and test diff, accepted215/Review216, recovery helper and existing recovery-aware guard, and exact217 CI.

**DOCUMENT217 — ACCEPTED WITHOUT REWORK AS A FAIL-CLOSED ARCHIVE-IDENTITY BLOCKER CHECKPOINT.**

**FINAL-FIVE PACKET PREPARATION IS NOT COMPLETE: ZERO PACKETS, NO EXPORT/REPLAY ACCEPTANCE.**

**SEPARATE BOUNDED WHOLE-ARCHIVE CONTENT-IDENTITY RECOVERY IS AUTHORIZED; PACKET RETRY IS NOT YET AUTHORIZED.**

This Windows reviewer did not inspect the private stat observations, blocker record, archives or preservation maps. Acceptance relies on the reported private diagnostic, inspected public implementation/test changes, matching public hashes and exact CI. It is not independent observation of device drift or proof of current archive content identity.

## Main assessment

The unchanged archive guard rejects a mismatch against the accepted environment binding.217 reports device-only drift across all three regular non-symlink study archives, stable repeated stat observations and matching inode/size/mtime/ctime. It does not assert a proven filesystem cause, content corruption or fresh byte identity.

Stopping before preflight/payload access and reporting0 exports is correct. Equal non-device stat fields do not justify dropping device from the guard or editing the old accepted binding. Conversely, device drift alone does not invalidate the previously accepted80 screen-level outcomes or prove archive corruption.

The report properly separates implemented/tested code from unexecuted preparation criteria. No actual study export CLI, extraction, decode, packet preflight, packet verification, sibling replay or study CLI-negative/overwrite probes are claimed. The helper refusal is not mislabeled a CLI refusal. These missing execution checks prevent packet acceptance, but are not reporting defects requiring217 rework.

## Scope, code and history

The new runner enforces Review216/accepted215 authority, exact source215 CI and fixed final integer ranks80..84 from the85-record highest-risk prefix, itself bound to the complete6640-record queue. Historical215 current70/prospective80/pending/count-false fields are checked separately from Review216's later current80/closed acceptance. Prior disagreement1/unresolved0 remains distinct from batch08 disagreement0.

The runner retains payload-size/SHA, accepted RGB-frame, thumbnail, temporal-panel and earliest minimum-Hamming trigger checks. Public source inspection shows the existing archive helper is used before payload access and after export. The claimed normalized AST equality and prior-module AST preservation remain reported checks, not independently recomputed here.

One new test method exercises strict final-five selection, historical activation fields, authority/CI drift and integrated refusal before archive access with no output. It does not establish successful real export or current archive content identity. Reported local new1/focused84/full271 pass results are distinct from direct CI observations; this reviewer did not locally rerun them.

No shared guard, old runner, frozen study policy, workflow or environment file changes occur in the commit. The only existing test-file transition is the one added method. No blocker in the bounded implementation/reporting scope was identified.

## Public hashes and fresh217 CI

Five public hashes match after Windows CRLF-to-repository-LF normalization:

| Record | SHA256 |
|---|---|
| Review216 | `93b35ec407286f9c6815842af0edad32cfeabb10d67fcffb9871bbd6cb71a50e` |
| Accepted215 document | `8dfdaa1a7bac2981a8eb8e4975df9b6d53aa0fc12c16b5cd13cbc41bb464e0d3` |
| Accepted215 aggregate | `99262c56e92e03cf22120f09e7f2a75a3f88ceca2789869c11a170435ef80ef3` |
| New batch09 runner | `0d6345fe3f2c9d87bf961596ed280c17e60cd1997c2d344e397496d733c0794e` |
| Updated test file | `2b832c2b50f0b07d138cdfab27c18b3b2c13cea1a0e9deda6fd11d0cedf5b2f9` |

GitHub API observations confirm:

| Item | Verified result |
|---|---|
| Exact head | `9082585c811ee3b1636b33145e5748876083ef30` |
| [Run39354730481](https://github.com/lathevinh/fas/actions/runs/39354730481) | completed / success |
| [Validate118406801611](https://github.com/lathevinh/fas/actions/runs/39354730481/job/118406801611) | completed / success |
| Job completion | `2026-10-20T01:41:02Z` |
| Listed steps | 12/12 success |

Synthetic regression, schema and fail-closed checks passed. Publication CI is clear; archive identity remains blocked. Software success cannot waive the archive guard or substitute for byte recovery.

## Bounded recovery authority

After Review218 is committed, perform a separate read-only content-identity recovery for exactly the three existing OULU archives, using the established recovery pattern:

1. Freeze new recovery criteria/preflight and bind this review, exact217/blocker evidence/CI, frozen archive SHA256 plus byte sizes, prior archive pins and accepted177/Review178 binding. Preserve the reported90 roots and all singleton/frozen/config/history/owner pins.
2. Require regular non-symlink source files. Compare device-only drift against the latest accepted environment identity, not merely the original pre177 identity. If additional identity fields differ, stop this device-only recovery and report the expanded discrepancy rather than silently broadening scope.
3. Read every byte of each archive and compare SHA256 and byte size against the unchanged frozen content anchors. Check five-field identity before opening, via the open descriptor, after hashing and before binding. A mismatch or change during reading fails closed.
4. Write separate immutable rehash observations and a proposed current-environment binding. Keep old pins and Recovery177 immutable. Distinguish old frozen content authority, latest accepted environment identity and newly observed identity. Record actual timings/bytes, preservation and tests; publish aggregate-only results with exact new CI.
5. Stop for formal recovery review. A favorable hash result alone does not accept its new binding, update the guard or authorize packet retry.

This authorization permits full-byte recovery reads and new additive recovery records only. No archive repair, migration, replacement, automatic download, packet extraction/decode, new visual judgment or human input is authorized.

The existing recovery CLI is hardcoded to Review176/source175 and the packet guard to accepted177/Review178. Do not relabel a new recovery as those historical events or overwrite their files. Any adaptation must explicitly bind current recovery authority while preserving old paths and tests. A later guard integration must select the newly accepted binding explicitly, retain all five stat checks and frozen content anchors, and have its own reviewed tests. Do not make st_dev globally optional, introduce silent fallback, or merely set accepted_by_Review178 on a new binding.

Only after recovery acceptance and reviewed guard integration may a separate authorization permit retry of exact80..84 packet preparation. Existing Review216 selection authority remains the bounded destination; this review does not waive the recovery/retry gates. No extra owner judgments, prose, license or administrative acceptance is required for technical recovery.

## Retained state

| Measure | State |
|---|---|
| Accepted effective / semantic owner / AI coverage | 80/85 each |
| Batch08 | Closed by Review216 |
| Final-five packets exported | 0 |
| Remaining not AI-screened | 5, exact80..84 |
| Historical disagreement / unresolved reconciliation | 1 /0 preserved |
| New AI/human/effective dispositions | 0 |
| Archive identity blocker | Open, pending recovery |

The technical archive blocker is separate from historical human reconciliation0. It must not be erased by unchanged stat fields or CI, nor confused with a new categorical disagreement.

No AI visual proposal, human handoff, queue extension, other dataset, source dry run, model/training/evaluation, analysis freeze or locked evaluation is authorized. Scientific readiness remains false. Technical replay, prior agreement and screen-level80/85 are not global lineage clearance or independent scientific replication.
