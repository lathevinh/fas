# 182 — Review of Document 181: OULU Batch-06 Packet Retry

Date: 2026-10-15  
Repository: `lathevinh/fas`  
Reviewed commit: `d03de2fb2488a8ebfa578019ad7fd6cf9e81fd22`  
Reviewed document: `docs/181-review-response-doc180-oulu-batch06-packet-retry.md`  
Reviewed aggregate: `results/phase1/oulu-batch06-packet-retry-v1.json`  
Reviewed runner: `scripts/prepare_oulu_visual_batch06.py`

## Verdict

**DOCUMENT 181 — ACCEPTED WITHOUT REWORK.**

**BATCH-06 PRIVATE PACKET PREPARATION FOR EXACT RANKS 50..59 — ACCEPTED.**

**THE PACKET-PREPARATION RETRY IS TECHNICALLY COMPLETE.**

**AI VISUAL PROPOSAL/SCREENING FOR RANKS 50..59 IS NOW AUTHORIZED.**

**HUMAN ADJUDICATION, EFFECTIVE DISPOSITION ACTIVATION, RANK60+, OTHER DATASETS, AND RESEARCH-MODEL EXECUTION REMAIN BLOCKED.**

Accepted current screen-level total remains **50**. AI-reviewed coverage remains **50/85** until the new ten packets are actually visually adjudicated.

---

## 1. Review180 authority is implemented explicitly

Review180 required the new packet preflight to bind:

- Review180;
- exact accepted Document179 aggregate;
- accepted historical Document179 runner;
- exact successful Document179 publication CI;
- accepted Recovery177 lineage;
- exact ranks 50..59.

Document181 implements this through `verified_packet_authority()`.

A bare `packet_preparation_authorized=true` boolean is not sufficient.

This directly resolves the main next-checkpoint requirement from Review180.

## 2. Review180 SHA is checked

The runner reads:

`docs/180-review-doc179-oulu-recovery-aware-guard.md`

and verifies its SHA against the packet authority block.

This makes Review180 an explicit additive authorization, rather than an informal assumption.

## 3. Accepted Document179 aggregate is checked

The runner verifies the exact SHA of:

`results/phase1/oulu-recovery-aware-guard-v1.json`

against the authority block.

It also confirms the historical Document179 state still records:

- guard integration review pending;
- packet preparation unauthorized.

Thus the new packet authority is additive and does not rewrite historical179 state.

## 4. Accepted Document179 runner is bound

The packet authority explicitly requires the historical accepted179 runner SHA:

`4996ee828d1a159184616669033e324b1dadf3335a480402cb2ad62e8e9fd62b`.

The accepted179 aggregate must report the same value.

This prevents substituting a different guard implementation as the basis for Review180 acceptance.

## 5. Exact successful Document179 publication CI is checked

The packet authority requires exactly:

- head SHA `63505d1c1b2f940fa077398127ef29a49ede95ef`;
- run `38676766354`;
- job `116232038205`;
- run status `completed`;
- run conclusion `success`;
- job status `completed`;
- job conclusion `success`.

This satisfies Review180's explicit CI-binding requirement.

## 6. Packet scope is locked to checkpoint181 and ranks50..59

The authority requires:

`packet_preparation_checkpoint = "181"`

and the preflight must contain exactly:

`[50,51,52,53,54,55,56,57,58,59]`.

This prevents a valid Review180 authorization from being silently reused for later queue blocks.

## 7. Recovery lineage remains bound

The new packet authority verifies that its accepted recovery fields match the accepted179 aggregate for:

- environment binding SHA;
- Recovery177 report SHA;
- archive-pin report SHA;
- Review178 SHA.

The runner then performs the full recovery-aware archive-identity verification.

This preserves the chain:

frozen content authority
→ Recovery177
→ Review178
→ Guard179
→ Review180
→ Packet181.

## 8. Current runner is separately pinned by the new preflight

The runner still verifies:

`_sha256(Path(__file__)) == preflight["preparation_code_sha256"]`.

Therefore Review180 accepts the historical guard runner, while the new immutable181 preflight separately pins the explicitly modified packet181 runner.

This distinction is correct.

## 9. Historical175/177/179 records are not reused or rewritten

Document181 creates a new preflight and verification.

The historical:

- Document175 blocked packet preflight;
- Recovery177 records;
- Guard179 preflight/verification

remain immutable.

Packet authority is enabled only in the new181 preflight.

This is the correct additive workflow.

## 10. Fixed queue selection remains exact

The runner still selects:

`records[50:60]`

and requires exact integer ranks 50 through 59 with the frozen priority.

No outcome-based skipping or replacement is introduced.

## 11. Archive identity is checked before packet work

The runner validates:

- accepted old archive pins;
- Recovery177 evidence;
- all five accepted current stat fields.

It checks archive identity once early and again immediately before payload access.

This preserves the accepted recovery-aware guard behavior.

## 12. Frozen content authority remains SHA-256 + byte size

The fast stat binding does not replace the original content authority.

For every selected media payload, the runner additionally verifies:

- tar member is a file;
- tar member size equals accepted media size;
- extracted file size equals accepted media size;
- extracted media SHA-256 equals accepted per-video media SHA.

Thus selected payload integrity is cryptographically checked during each export.

## 13. All accepted RGB frames are reverified

Document181 reports:

**2126 accepted RGB frames per export**

for the 16 selected videos.

Both main and sibling independently decode and verify these accepted frame identities.

Across both exports:

**4252 frame verifications** are reported.

This is strong technical evidence that packet images derive from the accepted audited media/frame records.

## 14. Main and sibling are genuinely separate exports

The main and sibling runs use separate output roots.

Each independently:

- reopens the source archives;
- extracts selected payloads;
- verifies selected payload SHA-256;
- decodes source videos;
- verifies RGB frames;
- generates thumbnails;
- builds panels and triggers.

Sibling images are not copied from the main export.

This is materially stronger than simply duplicating an already-generated packet tree.

## 15. Output count is internally consistent

Each root contains **2184 files**, consisting of:

- 2126 frame-thumbnail PNGs;
- 16 video manifests;
- 10 packet JSON records;
- 20 temporal-panel PNGs;
- 10 trigger PNGs;
- 1 lineage record;
- 1 summary record.

Total:

`2126 + 16 + 10 + 20 + 10 + 1 + 1 = 2184`.

The reported count is consistent.

## 16. PNG count is also internally consistent

Each root contains:

- 2126 frame thumbnails;
- 20 temporal panels;
- 10 triggers.

Therefore:

`2126 + 20 + 10 = 2156 PNG files per root`.

Across main and sibling:

**4312 PNGs**.

This agrees with Document181.

## 17. Full output replay matches exactly

The verification reports:

**2184 / 2184 files byte-identical**

between independently generated main and sibling roots.

This is strong deterministic-reproduction evidence for the packet-generation pipeline.

It does not constitute independent human adjudication, and Document181 does not claim that it does.

## 18. PNG readback is comprehensive

All:

**2156 PNG files per root**

are read back.

The verification additionally re-encodes every main thumbnail and compares exact output.

This is substantially stronger than merely checking that filenames exist.

## 19. Temporal panels are reconstructed

For each of the ten packets, both temporal panel variants are reconstructed and checked.

That gives:

**20 temporal-panel reconstructions per root.**

This verifies that the review panels are correctly derived from the bound decoded frames and fixed temporal ordering.

## 20. Trigger witnesses are reconstructed

Each of the ten packet trigger images is reconstructed using the accepted pHash sample positions.

The runner verifies that the computed minimum Hamming distance equals the frozen candidate record.

This gives:

**10 trigger reconstructions per root.**

The trigger evidence is therefore technically bound to the frozen candidate selection.

## 21. Packet records remain non-adjudicated

Every packet is written with:

`review_performed = false`

and:

`disposition = "awaiting_visual_review"`.

This is exactly correct for a packet-preparation checkpoint.

The technical preparation has not been mislabeled as an AI or human judgment.

## 22. No screen-level total changes

Document181 correctly leaves:

`accepted_current_total = 50`.

There are:

- 0 new AI dispositions;
- 0 new human dispositions;
- 0 new effective dispositions.

The project must not report an accepted total of 60 at this stage.

## 23. AI coverage also remains 50/85 until visual review occurs

The existence of ten packets does not mean those ten candidates have been visually reviewed.

Current AI visual coverage remains:

**50 / 85**.

The remaining unreviewed count remains:

**35**.

After the authorized AI visual stage actually evaluates ranks50..59, AI coverage may become 60/85, subject to that stage's review.

## 24. Temporary media cleanup passes

Document181 reports no residual extracted AVI or temporary decode directory after preparation.

This is appropriate both for reproducibility hygiene and private-media handling.

## 25. Output refusal behavior remains strong

Actual checks confirm refusal for:

- existing output;
- repository output;
- source-overlap output;
- immutable preflight overwrite.

The preflight overwrite produces the expected immutable-write failure.

This preserves the no-overwrite audit discipline.

## 26. Protected prior evidence remains stable

Document181 reports:

- 55 protected prior roots unchanged;
- 13 frozen artifacts unchanged;
- 17 study configs unchanged.

Historical175/177/179 records remain unchanged.

The only accepted source transitions are the explicitly reviewed runner change and one added test method.

## 27. Test coverage is strong

Document181 reports:

- focused tests: **75/75 passed**;
- full tests: **262/262 passed**.

The new packet-authority test covers the valid authority and numerous negative variants, including:

- missing guard acceptance;
- packet authorization false;
- wrong queue ranks;
- Review180 acceptance false;
- wrong checkpoint number;
- Review180 SHA mismatch;
- Document179 aggregate mismatch;
- accepted179 runner mismatch;
- wrong CI head;
- wrong run ID;
- wrong job ID;
- incomplete/failing run;
- incomplete/failing job;
- accepted recovery lineage mismatches;
- integrated refusal before output.

This is adequate for the new authority logic.

## 28. Fresh exact Document181 publication CI passes

Exact reviewed commit:

`d03de2fb2488a8ebfa578019ad7fd6cf9e81fd22`.

Fresh GitHub Actions run:

`38679467987`

is:

`completed / success`.

Validate job:

`116240464089`

is:

`completed / success`.

The job completed at:

`2026-10-15T04:04:40Z`.

All workflow validation steps completed successfully.

There is no publication-CI blocker.

## 29. Terminal-notification provenance is not relied upon as sole evidence

Document181 notes that the main command's automatic terminal notification included old terminal history.

This would be weak evidence by itself.

However, acceptance here does not depend on terminal text alone because the checkpoint independently verifies:

- immutable output trees;
- exact file maps;
- all PNG readbacks;
- reconstructed panels/triggers;
- queue/media/manifest bindings;
- full main/sibling byte equality;
- fresh source commit CI.

Therefore the noisy terminal-history observation is not a blocker.

## 30. Packet preparation may now be accepted additively

The aggregate retains:

`packet_preparation_checkpoint_review_pending = true`

and:

`AI_visual_adjudication_authorized = false`.

Do not rewrite those historical fields.

Review182 is the additive authority accepting the packet preparation and opening the next stage.

## 31. Next authorized stage: AI visual proposal only

The next checkpoint may perform AI visual review of exactly ranks:

`50..59`

using the accepted private packet assets.

The AI stage should:

- inspect the fixed temporal panels and trigger;
- preserve packet SHA/image bindings;
- provide a proposed disposition for each pair;
- record visibility/uncertainty where relevant;
- never claim biometric identity matching;
- use non-identity visual evidence such as garment/render structure/background/context;
- keep `confirmed_same_content_or_derived_lineage`, `rejected_false_positive`, and `uncertain_insufficient_evidence` available.

This AI stage remains a proposal/screening stage, not final human adjudication.

## 32. Human workflow should remain categorical-only

If human review is required after the AI proposals, preserve the accepted simplified protocol:

- Evidence sufficient? Yes/No
- Same or derived content? Yes/No
- Personally inspected? Yes/No
- Own decision? Yes/No

Do not reintroduce mandatory free-text visual descriptions or rationales.

## 33. Do not start rank60+ yet

Even though packet181 is accepted, the workflow should finish the ranks50..59 adjudication/import/activation chain before preparing the next frozen queue block.

This maintains sequential bounded review and avoids outcome-dependent queue movement.

## 34. No model or scientific-stage authorization

Review182 does not clear:

- global OULU content independence;
- capture independence;
- source-dry-run;
- analysis freeze;
- locked target evaluation;
- classifier/risk-model execution;
- other datasets.

The existing scientific-stage blockers remain unchanged.

## Final disposition

**DOCUMENT 181 — ACCEPTED WITHOUT REWORK.**

**BATCH06 PRIVATE PACKETS FOR RANKS50..59 — TECHNICALLY ACCEPTED.**

**TEN PACKETS, SIXTEEN VIDEOS, 2126 ACCEPTED RGB FRAMES PER EXPORT, AND 2184/2184 BYTE-IDENTICAL MAIN/SIBLING FILES ARE SUFFICIENT TO ACCEPT THE PACKET-PREPARATION CHECKPOINT.**

**AI VISUAL PROPOSAL/SCREENING FOR EXACT RANKS50..59 IS NOW AUTHORIZED.**

No owner/human input is required merely to begin the AI proposal stage.

Human review, if later needed, remains categorical-only.

Accepted current total remains **50** and AI coverage remains **50/85** until the new AI review is actually completed and reviewed.

Do not proceed to rank60+, other datasets, or research-model execution.
