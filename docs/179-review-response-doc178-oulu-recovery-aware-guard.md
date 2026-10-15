# Response to Review178: Recovery-Aware OULU Fast Stat Guard

## Prospective Criteria

[Review178](178-review-doc177-oulu-archive-identity-recovery.md) accepts Recovery177
and its additive environment binding without rewriting historical pending flags.
The175 archive-content blocker is resolved. This checkpoint integrates and tests
the fast guard only; packet preparation must wait for separate guard acceptance.

- Bind Review178, accepted177 report/binding/three rehash records, unchanged old
  archive-pin authority, and exact successful177 publication CI.
- Keep original frozen whole-file SHA-256 plus size as content authority. Use
  accepted177 current device/inode/size/mtime/ctime as the new fast stat authority.
  Do not make device optional or silently substitute the old environment identity.
- Check every accepted binding/observation/old-pin hash and all three live regular,
  non-symlink archive identities before payload access. Future drift in any stat
  field must fail closed and require a new separately authorized narrow recovery.
- Integrate directly into the batch06 preparation runner with an explicit fresh
  preflight option. Keep the legacy old-stat branch; old175 preflight remains
  immutable and its implementation pin must reject the changed runner.
- Add guard-only operation that returns before queue/media access or any output
  creation. The179 guard preflight must forbid packet execution even if guard-only
  is omitted. Future packet retry needs separately accepted guard authority and a
  new packet preflight, never rewriting175/177/179 private records.
- Preserve exact fixed ranks50..59 selection and existing payload type/size/hash,
  RGB-frame verification, temporal panels, trigger selection and final-stat checks.
- Test exact binding acceptance, old-stat rejection, future device/inode/size/
  mtime/ctime drift, binding/authority SHA mismatch, protected evidence drift,
  unchanged prior test AST and no output on failure.
- Record these criteria before live179 guard execution. Preserve55 prior roots
  (previous54 plus the four-file recovery root), frozen13, config17, old archive
  pins, recovery/blocked records, original owner answers and accepted shared code.
  Explicitly record the narrow batch06-runner and sole-test-method transitions.
- Run focused/full tests in existing conda fas, live guard-only and fail-closed
  checks without rehashing105 GB or opening selected payloads. Use unchanged
  immutable writer/output guards for new preflight and verification records.
- Publish aggregate counts/hashes only, commit/push, obtain fresh exact179 CI and
  stop for formal guard review before any packet retry, AI/human stage, rank60+,
  other dataset, scientific execution or research model. No owner/admin/license/
  human visual re-review is required.

## Scope

Accepted current total remains50, AI coverage50/85 and35 highest-risk candidates
remain unreviewed. Integration is not packet preparation, candidate clearance,
capture certification or scientific readiness. Source177 CI is not new179 CI.

## Execution

**RECOVERY-AWARE GUARD INTEGRATED AND VERIFIED. GUARD ACCEPTANCE IS PENDING.**

**NO BATCH06 PACKET RETRY WAS PERFORMED OR AUTHORIZED BY THIS CHECKPOINT.**

The [batch06 runner](../scripts/prepare_oulu_visual_batch06.py) now has a dedicated
`verified_archive_identities()` path. Its default branch retains the full old
stat identity. The explicit recovery branch binds Review178, accepted177 report,
environment binding, three rehash observations, original private archive records,
frozen whole-file SHA-256 and byte sizes before comparing all five current stat
fields to the accepted Recovery177 identity. Device is never optional.

`--preflight` selects a fresh explicitly pinned preflight; `--guard-only` returns
after protected-input and archive-identity checks, before queue/media access or
output creation. The new179 preflight has `packet_preparation_authorized=false`;
omitting guard-only is actually refused. Reusing the immutable175 preflight with
the changed implementation is also actually refused by its old code SHA pin.
No historical preflight is rewritten to make the new implementation pass.

The normal preparation path rechecks accepted archive identities immediately
before payload access and retains the final stat check. Its lineage would bind
the accepted recovery authority. AST checks establish unchanged fixed selection,
payload extraction/RGB verification, PNG/temporal-panel/trigger loops and final
stat comparison. These downstream paths were not executed on private media here;
their deterministic sibling replay and PNG readback remain future preparation work.

| Check | Observed Result |
|---|---|
| Actual guard-only CLI | return0;3 archive stat identities accepted |
| Direct fast guard with archive-open denial instrumentation | pass; no archive bytes opened |
| Legacy old device identity | rejected, not silently substituted |
| Simulated future device/inode/size/mtime/ctime drift | all5 rejected |
| Binding/archive-pin/report/review SHA mismatch | all rejected |
| Protected evidence drift | synthetic integrated test rejected before output |
| Packet execution using179 preflight | refused before payload/output |
| Historical175 preflight reuse | implementation drift refused |
| Actual immutable overwrite / existing/repository/source output | refused |
| Protected prior roots / frozen / study configs | 55 / 13 / 17 unchanged |
| Focused / full regression in fas | 74 / 261 passed |
| New packets / video decode / PNGs / rehashed archive bytes | 0 / 0 / 0 / 0 |

Focused74 tests pass in6.351s and full261 in53.101s. One new method in the
existing test file covers the recovery-aware fast guard; all earlier test AST
is unchanged. No code/test edits follow those runs. The only accepted-source
transitions are the batch06 runner and this test addition, explicitly pinned in
the new preflight. All other accepted runners, recovery implementation, shared
helpers, frozen roles, selector, seeds, configs and policies remain unchanged.

The55 prior roots comprise the previous54 plus Recovery177's four-file root.
Original archive pins,177 preflight/verification/binding/observations,175 blocked
records, historical173 fields and every original owner/categorical/prose record
remain unchanged. Review178 supplies additive recovery acceptance without editing
the historical177 review-pending flag. Review174 continues to supply current50.

The new preflight and verification are immutable private records. An initial
verification readback assertion compared runtime stat tuples directly with JSON
arrays after the record had been written. A focused corrected readback normalizes
only the in-memory representation and confirms all three exact identities and
stored results. No record was overwritten/regenerated, no production code changed,
and no archive rehash, selected payload access or packet retry occurred.

## Evidence Bindings

The [aggregate](../results/phase1/oulu-recovery-aware-guard-v1.json) contains only
counts, authority digests and verification results, not private stat numbers,
candidate identities, paths, owner identifiers, answers or biometric assets.

| Record | SHA256 |
|---|---|
| Review178 | `7cfec955f0607b2654c4d76d5062469a62a664c5dd1c6a9d5b633e681ae425b6` |
| Prior175 runner, preserved in git history | `f8e9cec23d4075ba2afcfc9a26895262c1bb21277ebdccb5cca19ba05f13d33c` |
| New batch06 runner | `4996ee828d1a159184616669033e324b1dadf3335a480402cb2ad62e8e9fd62b` |
| Prior177 test file, preserved in git history | `52c547d479beaf7dfca515252fcc13cb4e3c6499e6660784ba8ed7d54c94c4ab` |
| New existing test file | `9b94c8daf8e7b90ebfe372e29f02bde6739f63869432df857ee6183f29402f7d` |
| Accepted177 aggregate | `6c530eaf34f939a7a4f94099693ab44fbdf738ae7d0c801ae27073a71d7cc41f` |
| Original archive-pin aggregate | `412b6a6d1e239d70edffc8136997890b822ab21c00ecb09ebfa7c4c0371dd875` |
| Accepted177 environment binding | `c82ac8cace2b19a75ed65d6974e8d9dccaf5dbd051f95b2998d5d9837a14b0b4` |
| New private guard preflight | `80e9fe1b615998ebab6c0fe72c04d5818a502f0561634978f5bc54888f076be0` |
| New private guard verification | `f61cdc3deadf79134295d94630b32d9b16128cedbc00b667f46da8f11e5a7645` |

The new private records are `oulu_recovery_aware_guard_preflight_v1.json` and
`oulu_recovery_aware_guard_verification_v1.json`. Do not recreate or overwrite them.
Main/sibling batch06 packet roots and the guard probe output root remain absent.

## Exact Source CI

Source177 exact head `4b6d3037e7ddbc21bbea0b321daf63ec9a33da5e` is completed/success
via a fresh head-filtered REST retrieval and exact official
[run38673838230](https://github.com/lathevinh/fas/actions/runs/38673838230).
Fresh exact jobs REST and the official
[validate116222822739](https://github.com/lathevinh/fas/actions/runs/38673838230/job/116222822739)
confirm completed/success and Complete job. The REST job completion timestamp is
2026-10-15T02:59:33Z; absolute run completion remains unavailable/null, not inferred
from `updated_at` or relative page text.

This source177 observation is not new179 publication CI. Publish179 and obtain
fresh exact179 software CI before handoff; software CI does not accept the guard
or authorize packet preparation by implication.

## Stop Boundary

Stop for formal179 guard review. Only after that acceptance may a separate
preparation checkpoint create a new packet preflight and retry exact ranks50..59.
Retain accepted recovery hashes, full stat matching, per-video SHA/RGB checks,
frozen queue order, deterministic sibling redecode/reexport and PNG readback.
Any future stat drift must fail closed and require another narrow recovery.

No AI/human adjudication, rank60+, other dataset or model/scientific execution is
authorized here. No owner/license/admin/human visual re-review is needed.
Accepted total50, AI50/85 and35 unreviewed remain unchanged; scientific blockers
remain schema0/data-audit63/source-dry-run64/analysis-freeze65/locked-evaluation66.