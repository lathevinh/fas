# 192 — Review of Document 191: OULU Batch-07 Packet Preparation

Date: 2026-10-15  
Repository: `lathevinh/fas`  
Reviewed commit: `999b31ace9eb92d4923df812380588be5fcaf3e6`  
Reviewed document: `docs/191-review-response-doc190-oulu-batch07-packets.md`  
Reviewed aggregate: `results/phase1/oulu-batch07-packets-v1.json`  
Reviewed runner: `scripts/prepare_oulu_visual_batch07.py`  
Reviewed regression addition: `tests/test_oulu.py`

## Verdict

**DOCUMENT 191 — ACCEPTED WITHOUT REWORK.**

**BATCH-07 PRIVATE PACKET PREPARATION FOR EXACT RANKS 60..69 — ACCEPTED.**

**THE PACKET-PREPARATION CHECKPOINT IS TECHNICALLY COMPLETE.**

**AI VISUAL PROPOSAL / SCREENING FOR EXACT RANKS 60..69 IS NOW AUTHORIZED.**

**ACCEPTED CURRENT EFFECTIVE SCREEN-LEVEL TOTAL REMAINS 60.**

**AI-SCREEN COVERAGE REMAINS 60/85 UNTIL THE NEW TEN PACKETS ARE ACTUALLY VISUALLY REVIEWED.**

**HUMAN ADJUDICATION, EFFECTIVE ACTIVATION, RANK70+, OTHER DATASETS, SOURCE DRY RUN, ANALYSIS FREEZE, LOCKED EVALUATION, AND RESEARCH-MODEL EXECUTION REMAIN BLOCKED.**

---

## 1. Review190 authority existed before packet preparation

Review190 was committed at `2b79eda448d8c16b3373c2ca41498be0df901d66` before Document191.

Review190 explicitly:

- accepted Document189;
- closed batch06 screen-level review;
- advanced accepted effective total from 50 to 60;
- authorized preparation of the next frozen queue block beginning at rank60.

There is no process-order violation.

## 2. Scope is the exact next frozen block

The batch07 runner requires exactly:

`60,61,62,63,64,65,66,67,68,69`.

Ranks are required to be strict integers.

The selection is explicitly recorded as:

`fixed_next_ten_no_outcome_selection`.

No candidate is skipped or replaced based on visual outcome.

This preserves the frozen-priority interpretation of queue rank.

## 3. Historical Document189 state is preserved rather than rewritten

The runner explicitly checks historical189 creation-time facts including:

- activation checkpoint review pending;
- accepted batch06 current dispositions = 0 at creation time;
- ten materialized activation rows;
- accepted current total = 50 at creation time;
- prospective total = 60;
- batch06 closed = false at creation time.

Review190 supplies the additive current authority.

This is correct.

## 4. Accepted current total is correctly carried forward as 60

The new batch07 preparation does not create an effective scientific disposition.

Therefore:

**accepted current effective screen-level total = 60.**

Packet preparation does not advance this number.

## 5. Review190 is cryptographically bound

The runner requires exact Review190 SHA:

`6187b4bdc810c5e1e8dda38a4945e6551cd7020e5f5436b678e087d1c97ac0a2`.

It also verifies the Review190 file itself has that digest.

This is appropriate additive governance.

## 6. Accepted Document189 aggregate is bound

The runner requires exact accepted189 aggregate SHA:

`351b4d234455bfae4c74b912a06aff267b9729dff888f91725fe31b074f8fdb1`.

A different activation state cannot silently authorize packet preparation.

## 7. Exact successful Document189 publication CI is bound

The preflight requires exactly:

- head `a81bd9259478a8a49ad0783fdb777329791a99d5`;
- run `38696814671`;
- validate job `116295204960`;
- run completed/success;
- job completed/success.

This is the exact source state accepted by Review190.

## 8. Batch06 activation private evidence is revalidated

Before selecting ranks60..69, the runner checks the accepted batch06 activation root:

- activation summary;
- activation authority;
- successful source-CI observation;
- exact ten-row bundle.

Each historical rank50..59 row is checked for its accepted activation state and Review188 semantic authority.

This prevents queue advancement from relying only on a public summary count.

## 9. Full frozen 6640-pair queue remains bound

The runner requires:

- exactly 6640 private queue records;
- accepted queue bundle SHA;
- accepted queue summary SHA.

It selects records 60 through 69 only after queue integrity is established.

This is strong frozen-queue provenance.

## 10. Frozen artifacts remain exact

The frozen input directory is rehashed and compared against the accepted exact-evidence report.

Any frozen-artifact change fails preparation.

This is appropriate.

## 11. Accepted media and fingerprint bundles remain bound

The runner revalidates:

- all 4950 accepted per-video media records;
- all 4950 accepted fingerprint records;
- their accepted bundle digests.

This prevents packet construction from using a modified technical evidence population.

## 12. Visual evidence policy and helpers remain pinned

The accepted visual policy and implementation hashes are checked before export.

Prior accepted batch runners are also checked for drift.

Document191 does not silently change the visual-review evidence definition.

## 13. The recovery-aware archive guard is reused unchanged

The batch07 runner imports the accepted archive-identity guard rather than inventing another archive-integrity rule.

All three recovered five-field stat identities must match.

The guard is checked:

1. before payload work;
2. again before payload access;
3. after export/readback.

Future stat drift therefore still fails closed.

## 14. Fast stat checking is not overclaimed

Document191 correctly records:

`source_archive_rehash_executed = false`

and:

`fast_stat_is_not_fresh_whole_archive_cryptographic_proof = true`.

The accepted Recovery177 full-file hash remains the content-recovery authority.

This limitation is correct.

## 15. Every selected payload is cryptographically verified

For each selected video, the runner checks:

- tar member is a file;
- tar member size equals accepted byte size;
- extracted file size;
- extracted media SHA-256 equals accepted media SHA.

Thus the selected media used for batch07 are independently content-verified during each export.

## 16. Every accepted decoded RGB frame is reverified

There are:

**2464 accepted full-RGB frames per export.**

Across main and sibling:

**4928 full-RGB frame verifications.**

The frame identities are checked against accepted per-video media records before thumbnails are used.

This is strong packet-source integrity evidence.

## 17. Exact batch07 media scale is internally consistent

The ten selected pairs require:

**19 unique videos per export.**

Main and sibling independently decode those videos, for:

**38 decode invocations total.**

This matches the reported packet composition.

## 18. Main and sibling exports are independently regenerated

The sibling output is not copied from the main output.

Each export independently:

- reopens the archives;
- extracts selected media;
- hashes selected payloads;
- redecodes accepted frames;
- creates thumbnails;
- creates temporal panels;
- creates trigger witnesses;
- writes manifests and packet records.

This is the correct technical-reproducibility design.

## 19. Output file counts are internally consistent

Each root contains:

- 2464 thumbnail PNGs;
- 19 video manifests;
- 10 packet JSON records;
- 20 temporal-panel PNGs;
- 10 trigger PNGs;
- 1 lineage record;
- 1 summary record.

Total:

`2464 + 19 + 10 + 20 + 10 + 1 + 1 = 2525`.

The aggregate reports exactly **2525 files per export**.

## 20. PNG counts are internally consistent

Each root contains:

- 2464 thumbnails;
- 20 temporal panels;
- 10 trigger witnesses.

Therefore:

`2464 + 20 + 10 = 2494 PNG files per root`.

Across both roots:

**4988 PNG readbacks.**

The reported counts are consistent.

## 21. Full main/sibling output equality passes

The verification reports:

**2525 / 2525 files byte-identical.**

This is strong deterministic replay evidence.

It is not independent scientific adjudication, and Document191 correctly avoids claiming otherwise.

## 22. Every PNG is read back

All **2494 PNG files per root** are decoded/read back.

The aggregate additionally reports exact PNG decode/re-encode byte verification.

This is stronger than filename-only existence checking.

## 23. Temporal panels are reconstructed

There are:

**20 temporal panels per export.**

The review verification reconstructs the panel/trigger outputs from read-back source thumbnails.

These reconstructions pass for both exports.

## 24. Trigger witnesses are deterministic

Each packet includes the minimum-Hamming pHash witness.

When multiple pairs share the same minimum Hamming distance, the tuple ordering selects the earliest witness deterministically.

There are:

**10 trigger witnesses per root.**

The frozen candidate minimum-Hamming value must match before packet creation.

## 25. Temporal/trigger reconstruction count is correct

Per root:

- temporal panels = 20;
- triggers = 10.

Therefore:

**30 reconstruction checks per root.**

All pass.

## 26. Packet records remain explicitly non-adjudicated

Every packet retains:

`review_performed = false`

and:

`disposition = "awaiting_visual_review"`.

This is essential.

Technical packet preparation is not mislabeled as AI or human screening.

## 27. AI coverage therefore remains 60/85

Ranks60..69 now have technically accepted review packets, but they have not yet been AI visually reviewed.

Therefore:

**AI-screen coverage remains 60/85.**

Do not report 70/85 yet.

## 28. Twenty-five candidates remain not yet AI-screened

The highest-risk frozen screen contains 85 candidates.

Accepted AI screening currently covers 60.

Therefore:

**25 candidates remain not yet AI visually screened.**

Of these:

- ranks60..69: 10 now have accepted technical packets after Review192;
- ranks70..84: 15 have not yet reached this packet-preparation stage.

## 29. No new human decision exists

Document191 creates:

**0 new human dispositions.**

No human handoff is prepared.

No owner input is required for already closed ranks50..59.

This is correct.

## 30. No new effective disposition exists

Document191 creates:

**0 new effective dispositions.**

Accepted effective total remains 60.

The ten batch07 packets cannot count toward effective closure until later AI/human/import/activation stages are completed as applicable.

## 31. Temporary extracted media are cleaned

The checkpoint reports no residual temporary AVI or decode tree in either output root.

This is appropriate private-media and reproducibility hygiene.

## 32. Prior evidence is preserved

Document191 reports:

- 65 protected prior roots unchanged;
- frozen13 unchanged;
- config17 unchanged;
- owner source bytes/answers unchanged;
- historical pending/nonactivation flags unchanged;
- accepted prior helpers/runners unchanged.

This is satisfactory additive preservation.

## 33. Output refusal behavior remains fail-closed

Actual CLI probes reject:

- existing main output;
- existing sibling output;
- repository output;
- source-overlap output;
- symlink output.

No unsafe output path is accepted.

## 34. Authority refusal behavior is tested in actual CLI probes

Additional probes reject:

- wrong source189 CI;
- missing preparation authorization;
- wrong Review190 digest.

These failures occur without creating output.

This is meaningful authority enforcement.

## 35. Immutable overwrite refusal remains active

Attempts to overwrite:

- preflight;
- lineage;
- first packet

raise the immutable-write failure.

No prior evidence is rewritten.

## 36. New runner is a bounded batch-specific transition

Document191 adds a new batch07 runner rather than modifying the accepted batch06 runner.

The accepted batch06 guard/runner hash remains fixed.

This is preferable to mutating historical packet-generation code.

## 37. Core export loops remain equivalent to the accepted batch06 path

Document191 reports the payload/RGB/PNG/panel/trigger export logic as AST-identical to batch06 after only rank/batch-label normalization.

This materially reduces implementation drift between batches.

## 38. Regression test targets the new authority boundary

One new method is added to the existing test file.

It covers:

- Review190 additive closure;
- unchanged historical189 creation-time state;
- exact strict-integer ranks60..69;
- source preservation;
- negative authority variants;
- integrated no-output refusal before archive access.

Accepted prior test ASTs remain unchanged.

## 39. Local regressions are clean

The new focused test:

**1/1 passed.**

Focused suite:

**78/78 passed.**

Full suite:

**265/265 passed.**

No regression blocker remains.

## 40. Fresh exact Document191 publication CI passes

Exact reviewed commit:

`999b31ace9eb92d4923df812380588be5fcaf3e6`.

Fresh GitHub Actions run:

`38701736375`

is:

`completed / success`.

Validate job:

`116311307258`

is:

`completed / success`.

The validate job completed at:

`2026-10-15T07:53:39Z`.

All listed workflow validation steps completed successfully.

There is no publication-CI blocker.

## 41. Packet preparation may now be accepted additively

The Document191 aggregate retains:

`packet_review_performed = false`

and:

`packet_preparation_review_pending = true`.

Do not rewrite those historical creation-time fields.

Review192 is the additive authority accepting the technical packet-preparation checkpoint.

## 42. Next authorized stage is AI visual proposal for ranks60..69

The next checkpoint may perform AI visual inspection/proposal using exactly the accepted batch07 packet assets.

It should preserve:

- exact queue rank;
- packet SHA;
- exact frozen pair-record SHA;
- image hashes;
- manifest/frame lineage;
- three-outcome proposal vocabulary.

The AI stage must remain non-binding.

## 43. AI visual reasoning must remain non-identity based

As in prior batches, the AI screen may use visible:

- garment structure;
- rendering geometry;
- scene/context;
- presentation structure;
- other non-biometric visual relationships.

It must not rely on identifying the depicted people.

## 44. All three AI outcomes must remain available

The proposal stage must retain:

- `rejected_false_positive`;
- `confirmed_same_content_or_derived_lineage`;
- `uncertain_insufficient_evidence`.

A confirmed proposal still requires prospective hard-stop handling.

Uncertainty must not be forced into rejection.

## 45. Do not prepare human handoff before AI checkpoint review

Recommended sequence remains:

1. Review192 accepts packet191.
2. AI visual proposal for exact ranks60..69.
3. Formal review of the AI checkpoint.
4. Prepare categorical-only human handoff if required by the accepted workflow.
5. Human import/reconciliation.
6. Import review.
7. Separate additive activation.
8. Activation review.
9. Only then continue rank70+.

Do not collapse these governance boundaries.

## 46. Human workflow, if required, remains categorical-only

Do not reintroduce mandatory free-text prose.

Use the accepted categorical structure:

- evidence sufficient;
- same/derived if sufficient;
- personal inspection attestation;
- own-decision attestation.

AI proposal should not be prefilled as the human answer.

## 47. Rank70+ remains blocked

Document191 and Review192 cover only ranks60..69.

Do not prepare or inspect ranks70+ before the batch07 chain reaches its next authorized boundary.

This prevents outcome-dependent queue advancement.

## 48. Other datasets remain blocked

No CASIA/MSU/SiW audit execution is authorized by this packet checkpoint.

The present work remains the OULU content-lineage audit.

## 49. Research-model execution remains blocked

Review192 does not authorize:

- classifier training;
- branch inference for the study;
- risk-model training;
- source dry run;
- target evaluation;
- analysis freeze;
- locked evaluation.

The audit/gating workflow is still incomplete.

## 50. Scientific readiness is still false

The aggregate correctly reports scientific readiness as false.

Packet reproducibility and successful CI are necessary technical evidence, not proof of:

- global content independence;
- capture independence;
- transformed-source independence;
- cross-dataset independence;
- model validity.

## Current project state after Review192

### Completed and accepted

- OULU frozen role/content-audit infrastructure is established.
- Exact/near-duplicate queue and bounded visual-review process are established.
- Ranks0..59 have completed their accepted screen-level workflow.
- Batch06 is closed.
- Accepted effective screen-level total: **60**.
- AI-screen coverage through rank59: **60/85**.
- No confirmed same/derived hard stop has been activated in the accepted first60 candidates.
- Batch07 technical packet generation for ranks60..69 is now accepted by Review192.

### Prepared but not yet visually adjudicated

- Ranks60..69:
  - 10 packets;
  - 19 unique videos;
  - 2464 verified full-RGB frames per export;
  - 2494 PNG review assets/readbacks per export;
  - main/sibling 2525/2525 files byte-identical.

These ten candidates are technically ready for AI visual screening.

### Not yet reached

- Ranks70..84: **15 candidates** have not yet entered the new packet/AI review chain.
- AI screening for ranks60..69 has not yet occurred.
- Human adjudication/import/activation for batch07 has not occurred.
- Other dataset audits have not started under this sequence.
- Source dry run, analysis freeze, locked evaluation and research-model execution remain blocked.

### Numerical summary

- Frozen highest-risk candidates: **85**
- Accepted effective screen-level dispositions: **60 / 85**
- AI visually screened: **60 / 85**
- Technically packet-prepared but not AI-screened: **10 / 85** (`60..69`)
- Not yet packet-reviewed in the new continuation: **15 / 85** (`70..84`)
- Remaining not yet AI-screened: **25 / 85**

## Final disposition

**DOCUMENT 191 — ACCEPTED WITHOUT REWORK.**

**BATCH07 PACKET PREPARATION FOR EXACT RANKS60..69 — ACCEPTED.**

**AI VISUAL PROPOSAL / SCREENING FOR EXACT RANKS60..69 — AUTHORIZED.**

**ACCEPTED CURRENT EFFECTIVE TOTAL REMAINS 60.**

**AI-SCREEN COVERAGE REMAINS 60/85 UNTIL THE NEW TEN CANDIDATES ARE ACTUALLY SCREENED.**

**25 HIGHEST-RISK CANDIDATES REMAIN NOT YET AI-SCREENED.**

**RANK70+, OTHER DATASETS, AND RESEARCH-MODEL / SCIENTIFIC EXECUTION REMAIN BLOCKED.**

Historical pending/review fields remain immutable creation-time facts. Review192 is the additive acceptance authority for Document191 packet preparation.
