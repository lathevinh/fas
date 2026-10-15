# 180 — Review of Document 179: Recovery-Aware OULU Fast Stat Guard

Date: 2026-10-15  
Repository: `lathevinh/fas`  
Reviewed commit: `63505d1c1b2f940fa077398127ef29a49ede95ef`  
Reviewed document: `docs/179-review-response-doc178-oulu-recovery-aware-guard.md`  
Reviewed aggregate: `results/phase1/oulu-recovery-aware-guard-v1.json`  
Reviewed runner: `scripts/prepare_oulu_visual_batch06.py`

## Verdict

**DOCUMENT 179 — ACCEPTED WITHOUT REWORK.**

**RECOVERY-AWARE FAST ARCHIVE GUARD — ACCEPTED.**

**THE ACCEPTED RECOVERY177 CURRENT ENVIRONMENT IDENTITY IS NOW VALID FOR FAST FAIL-CLOSED ARCHIVE CHECKING.**

**BATCH-06 PACKET PREPARATION IS STILL NOT COMPLETE.**

**NEXT AUTHORIZED STEP: CREATE A NEW IMMUTABLE PACKET-PREPARATION PREFLIGHT THAT BINDS REVIEW180 AND THE EXACT SUCCESSFUL DOCUMENT179 CI, THEN RETRY EXACT RANKS 50..59.**

**DO NOT REUSE OR MODIFY THE DOCUMENT175 OR DOCUMENT179 PREFLIGHTS.**

No owner, license, administrative, or human visual re-review is required at this stage.

---

## 1. Review178 requirements are implemented correctly

Review178 accepted Recovery177 and required a recovery-aware fast guard that:

- retains frozen whole-file SHA-256 + byte size as content authority;
- binds the accepted Recovery177 current stat identity;
- checks all five stat fields;
- does not make `st_dev` optional;
- fails closed on future drift;
- preserves the normal packet-integrity path;
- does not run packet preparation before formal guard review.

Document179 implements these requirements.

## 2. Content authority remains unchanged

The new guard does not replace the original archive content anchors.

The runner continues to bind the accepted archive-pin aggregate and verifies that the frozen archive SHA-256 values equal the known accepted anchors.

Recovery177 is therefore used as **environment-identity authority**, not as a replacement content checksum.

This distinction is correct.

## 3. All five current stat fields are bound

For each archive, the accepted Recovery177 identity includes:

- device;
- inode;
- byte size;
- mtime;
- ctime.

The runner compares the live archive identity against all five fields.

`device` is not ignored.

This directly satisfies Review178.

## 4. Old and new identities are both checked semantically

The recovery branch validates that:

- the old private archive record SHA matches the original frozen authority;
- the recovery observation points back to that exact old record;
- old file identity equals the historical record;
- current SHA equals the frozen SHA;
- frozen SHA equals the accepted archive-pin SHA;
- byte size equals the accepted pin;
- the archive was fully read;
- content hash matched frozen authority;
- stat identity was stable during recovery hashing;
- changed fields were exactly `["device"]`.

Only then is the recovered current identity accepted as the fast stat identity.

This is appropriately strict.

## 5. Recovery observations are individually rebound

The runner does not trust only the public recovery aggregate.

For each archive it loads the corresponding private `.rehash.json` record and verifies:

- its SHA against the accepted recovery aggregate;
- its parsed content against the environment binding row.

This materially strengthens provenance.

## 6. Review178 acceptance is explicitly bound

The recovery-aware path requires:

`accepted_by_Review178 = true`

and verifies the SHA of:

`docs/178-review-doc177-oulu-archive-identity-recovery.md`.

Thus historical `recovery_checkpoint_review_pending=true` in the Recovery177 record is not rewritten; Review178 supplies the additive acceptance authority.

This matches the project's additive-history policy.

## 7. The historical old-stat path is not silently repurposed

The default branch retains the old strict stat identity logic.

Because the batch06 runner itself changed, the old Document175 preflight's implementation SHA no longer matches and reuse is rejected.

This is correct.

The project does not edit the old preflight to make the new runner pass.

## 8. Explicit fresh preflight is required for the recovery path

When an explicit `--preflight` is provided, the runner requires an accepted recovery block.

Therefore an arbitrary fresh preflight cannot silently enter the recovery-aware path without recovery authority.

This is appropriate.

## 9. Document179 preflight correctly forbids packet execution

The Document179 guard preflight records:

`packet_preparation_authorized = false`.

The runner refuses normal packet execution when an explicit preflight does not authorize packet preparation.

This ensures the guard-integration checkpoint cannot itself become packet preparation.

## 10. Guard-only mode is appropriately bounded

`--guard-only` returns after:

- protected evidence verification;
- archive/recovery authority verification;
- all three live stat checks.

It returns before:

- frozen queue access for candidate selection;
- selected archive payload extraction;
- FFmpeg decode;
- PNG creation;
- packet output.

The observed live guard-only CLI returned success for all three archives with no selected payload access.

This is the intended behavior.

## 11. Fast guard does not reopen the 105-GB archive bytes

Document179 reports:

- full archive bytes rehashed: 0;
- archive-open denial instrumentation: passed.

That is acceptable because Recovery177 already performed the authoritative full rehash and Review178 accepted it.

The purpose of Document179 is specifically to establish a reviewed fast identity check for the unchanged current environment.

## 12. Future device drift still fails closed

The tests explicitly reject simulated drift in:

- device;
- inode;
- byte size;
- mtime;
- ctime.

This is important: the recovery event is not turned into a general permission to ignore future device changes.

Any future stat drift requires another narrow recovery.

## 13. Legacy old identity is correctly rejected

The new recovery-aware branch does not silently accept the pre-recovery device identity.

This demonstrates that the current environment binding is a real identity binding, rather than a generic “either old or new is fine” rule.

That is the correct design.

## 14. Authority-drift checks are strong

Document179 reports rejection of mismatches in:

- Review178 SHA;
- accepted Recovery177 report;
- archive-pin aggregate;
- environment binding;
- per-archive recovery observations.

This prevents a caller from combining unrelated accepted artifacts.

## 15. Protected evidence remains fail-closed

The integrated synthetic test verifies protected-evidence drift is rejected before output.

The private output safety logic also refuses:

- existing output;
- repository output;
- source-overlap output;
- immutable overwrite.

No integrity regression is apparent.

## 16. Fixed batch selection remains unchanged

The runner still requires exact integer ranks:

`50..59`

from the frozen queue and retains the `cross_role_conflicting_label` priority condition.

No outcome-dependent skipping is introduced by the guard work.

## 17. Downstream packet integrity logic remains present

The normal preparation path still retains:

- exact queue binding;
- media/fingerprint bundle verification;
- accepted visual policy binding;
- locked FFmpeg check;
- tar member type/size check;
- extracted payload SHA-256 check;
- accepted RGB-frame verification;
- temporal panel generation;
- minimum-Hamming trigger witness verification;
- final archive stat comparison.

These downstream operations were not executed in Document179, which is correct.

## 18. Archive identity is rechecked immediately before payload access

The normal path calls the recovery-aware archive verification again after queue/media/fingerprint checks and immediately before FFmpeg/payload work.

It compares that second result to the first accepted identities.

This reduces the window in which environment drift could occur unnoticed before payload access.

## 19. Final archive stat check remains necessary and retained

The existing final stat comparison remains in the packet-export path.

Therefore the archive identity is checked:

1. near the beginning;
2. immediately before payload access;
3. after export.

This is a sensible fast-integrity envelope around packet generation.

## 20. One limitation of fast stat identity remains understood

A stat guard is not a cryptographic rehash of the whole 105-GB archive.

Its scientific acceptability here depends on:

- the recent accepted Recovery177 whole-file hash equality;
- exact current stat binding;
- fail-closed future stat drift;
- per-selected-video payload SHA checks during packet creation.

Document179 does not overclaim that fast stat checking independently proves whole-archive content identity forever.

This limitation should remain explicit.

## 21. Tests are strong

Document179 reports:

- focused regression: **74/74 passed**;
- full regression: **261/261 passed**.

The new test specifically exercises the recovery-aware guard and rejects each stat-field drift plus authority and protected-evidence failures.

All prior test AST is reported unchanged apart from the one new method.

No regression blocker is present.

## 22. Fresh exact Document179 publication CI passes

Exact reviewed head:

`63505d1c1b2f940fa077398127ef29a49ede95ef`

Fresh GitHub Actions run:

`38676766354`

is:

`completed / success`.

Validate job:

`116232038205`

is:

`completed / success`.

The exact job completed at:

`2026-10-15T03:32:57Z`.

There is no publication-CI blocker.

## 23. Document179 status may now be interpreted additively as accepted

The aggregate retains:

`guard_integration_checkpoint_review_pending = true`

and:

`packet_preparation_authorized = false`.

Do not rewrite these historical fields.

Review180 is the additive authority accepting the guard integration.

The guard may now be used by a **new later packet-preparation checkpoint**.

## 24. Current progress does not advance beyond 50 candidates

Document179 created:

- 0 packets;
- 0 decoded selected videos;
- 0 PNGs;
- 0 AI adjudications;
- 0 human adjudications;
- 0 effective dispositions.

Therefore:

- accepted current total remains **50**;
- AI coverage remains **50/85**;
- unreviewed highest-risk candidates remain **35**.

Do not report 60 reviewed candidates yet.

## 25. Required next packet-preparation preflight

The next checkpoint must create a **new immutable packet-preparation preflight**.

It must bind at minimum:

- Review180 SHA;
- Document179 commit `63505d1c1b2f940fa077398127ef29a49ede95ef`;
- fresh Document179 run `38676766354`;
- fresh Document179 validate job `116232038205`;
- accepted Document179 runner SHA;
- accepted Recovery177 report/binding/rehash records;
- original archive-pin content authority;
- Review174 batch05 closure authority;
- protected prior roots/frozen/config maps;
- exact fixed queue ranks `50..59`.

It must explicitly set packet preparation authority for that checkpoint only.

## 26. Do not authorize packets with a bare boolean alone

The current runner checks an explicit preflight's `packet_preparation_authorized` boolean.

For the next packet checkpoint, that boolean must not be treated as self-authenticating authority.

The new preflight must cryptographically bind Review180 and exact successful Document179 CI.

Preferably the runner/preflight validation should also explicitly verify the Review180 SHA or a clearly named additive guard-acceptance block rather than relying only on the generic boolean.

This is a **next-checkpoint requirement**, not a blocker to accepting Document179 itself, because Document179's own preflight keeps packet execution disabled.

## 27. Do not reuse Document179 guard preflight

The guard preflight was intentionally created with packet execution disabled.

Do not edit it from false to true.

Do not overwrite it.

Do not use it as the packet-preparation preflight.

Create a fresh immutable record for the packet retry.

## 28. Batch06 retry may occur only after the new preflight is created

Once the new packet-preparation preflight is correctly bound, the project may rerun the packet preparation for exact ranks:

`50..59`.

That retry should perform the full existing packet-integrity procedure and independent sibling re-export/redecode checks.

The successful packet preparation must then receive its own formal review before AI visual adjudication starts.

## 29. No owner input is required now

This checkpoint is infrastructure/integrity work.

Do not ask the owner for:

- license confirmation;
- administrative permission;
- visual descriptions;
- categorical Yes/No decisions.

Human input becomes relevant only if later candidate adjudication requires it.

## 30. Later stages remain blocked

Review180 does not authorize:

- AI adjudication before packet-preparation review;
- human adjudication;
- ranks60+;
- another dataset;
- source dry run;
- analysis freeze;
- locked target evaluation;
- research classifier/risk-model execution.

Scientific-stage blocker counts remain unchanged.

## Final disposition

**DOCUMENT 179 — ACCEPTED WITHOUT REWORK.**

**RECOVERY-AWARE FAST ARCHIVE GUARD — ACCEPTED.**

The implementation correctly binds the accepted Recovery177 environment identity, preserves original SHA-256 + byte-size content authority, retains all five stat fields, rejects old/future drift, and leaves packet execution disabled during the guard checkpoint.

Fresh exact Document179 CI is successful.

**NEXT:** create a fresh immutable packet-preparation preflight that binds Review180 and exact successful Document179 CI, then retry exact batch06 ranks50..59. Do not edit/reuse the Document175 or Document179 preflights.

After packet preparation succeeds, stop again for formal packet review before AI/human adjudication.

Accepted current total remains **50** and AI coverage remains **50/85**.
