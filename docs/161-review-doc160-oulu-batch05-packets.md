# 161 — Review of Document 160: OULU Batch-05 Private Packet Preparation

Date: 2026-10-13  
Repository: `lathevinh/fas`  
Reviewed commit: `acfce3aecd2345a91f146835afab93f1c9cadeae`  
Reviewed document: `docs/160-review-response-doc159-oulu-batch05-packets.md`  
Reviewed aggregate: `results/phase1/oulu-batch05-packets-v1.json`

## Verdict

**DOCUMENT 160 — ACCEPTED.**

**CHECKPOINT 1.5AG OULU BATCH-05 PRIVATE PACKET PREPARATION — ACCEPTED WITHOUT REWORK.**

**AI-ASSISTED VISUAL ADJUDICATION IS AUTHORIZED FOR RANKS 40–49 ONLY.**

No human disposition, effective disposition, rank-50+ work, other-dataset work or research-model execution is authorized by this review.

The accepted current screen-level total remains **40 relationships**. Batch 05 currently contains **10 prepared but still unreviewed candidates**.

## 1. Scope is correctly restricted to the next fixed queue block

Document 160 selects exactly ranks `40..49` from the frozen queue. The runner requires exact integer ranks, preserved queue order, priority `cross_role_conflicting_label`, and no outcome-dependent skipping. This satisfies the prospective queue discipline established by Review 159.

## 2. Review 159 is used as additive authority rather than retroactive mutation

The runner explicitly requires Review 159 acceptance of batch 04 and accepted current total 40, while also requiring the historical Document-158 activation report to remain in its original review-pending state.

This is the correct provenance model. Acceptance is additive through Review 159; historical artifacts are not rewritten.

## 3. No new adjudication is manufactured

Document 160 correctly records zero new AI dispositions, zero human dispositions, zero effective dispositions, and zero images actually visually reviewed.

All ten packets remain `review_performed = false` and `disposition = awaiting_visual_review`.

Preparation is therefore cleanly separated from adjudication.

## 4. Media-integrity verification is strong

The selected batch contains:

- 16 unique source videos;
- 1956 accepted decoded RGB frames;
- 1956 private frame PNGs;
- 20 temporal-panel PNGs;
- 10 trigger PNGs;
- 16 video manifests;
- 10 pair packets;
- lineage + summary.

The arithmetic is internally consistent:

- total PNGs = `1956 + 20 + 10 = 1986`;
- total private files = `1986 + 16 + 10 + 2 = 2014`.

No count inconsistency is present.

## 5. Every decoded RGB frame is checked against the accepted audit

Before thumbnails are persisted, the runner reopens the selected source payloads and verifies each decoded full-resolution RGB frame against the accepted media-audit RGB hash.

This is stronger than checking only selected review frames and provides a strong provenance chain from accepted source media to private review assets.

## 6. Independent replay is genuine redecode/reexport

The second export is not merely JSON reserialization. It reopens and redecode-verifies all 16 selected source payloads into a fresh sibling root.

Reported result:

**2014 / 2014 files byte-identical.**

This strongly supports deterministic packet preparation, while still not constituting independent visual adjudication.

## 7. Temporal evidence construction is deterministic

The accepted visual helper defines 17 deterministic temporal positions spanning each decoded sequence.

Batch 05 generates `temporal_a` from alternating even review slots and `temporal_b` from alternating odd review slots. Together the two panels cover all 17 fixed temporal review slots.

This does not introduce a new adaptive frame selector.

## 8. Trigger construction is correctly frozen

For each pair, the runner reconstructs the minimum-Hamming witness from the accepted pHash sample records and verifies that the reconstructed distance equals the frozen candidate's recorded minimum Hamming distance.

Tuple ordering makes the selected witness deterministic in case of ties. The trigger is therefore not chosen after looking at the images.

## 9. Source/queue/packet lineage is adequately bound

Preparation pins and verifies the accepted queue bundle, all 4950 media-audit records, all 4950 fingerprint records, accepted visual policy/implementation, prior accepted batch runners, archive-byte records, frozen artifacts, exact FFmpeg version, batch-04 activation evidence and Review 159.

This is appropriately conservative.

## 10. Archive identity and overwrite guards are correct

Archive identity is checked using device, inode, size, modification time and change time, with payload hashes verified on extraction.

Existing-output invocation refuses overwrite and leaves original files unchanged. Zero temporary AVI payloads are retained.

## 11. Protected prior evidence remains unchanged

Document 160 reports 38 protected prior roots unchanged, all 13 frozen artifacts unchanged, and all pinned prior implementations/configurations unchanged.

No previous accepted evidence is rewritten.

## 12. Regression evidence is sufficient

Local regression reports:

- focused OULU suite: **66/66 passed**;
- full regression: **253/253 passed**;
- zero failures/errors.

Because this checkpoint adds a new batch-05 runner and test, rerunning the full regression was appropriate.

## 13. Exact prerequisite CI is correctly bound

The preparation binds the accepted batch-04 publication CI:

- commit `4a6215d5aaf575d80d434ca783e3e8f892974e62`;
- run `38347742466`;
- validate job `115132944411`;
- `completed / success`.

The recorded REST 403 is correctly treated as a retrieval/rate-limit limitation rather than evidence of CI failure.

## 14. Fresh exact CI for Document 160 passes

Exact reviewed commit:

`acfce3aecd2345a91f146835afab93f1c9cadeae`

Fresh GitHub Actions:

- run `38377925777`;
- status `completed`;
- conclusion `success`.

Validate job:

`115230867707`

also completed successfully, including synthetic regression, canonical schema validation and fail-closed checks.

There is no publication-CI blocker.

## 15. Current queue progress is internally consistent

The aggregate reports:

- 40 candidates already AI visually reviewed from prior batches;
- 10 additional candidates prepared but not yet reviewed;
- 35 candidates not yet prepared;
- 45 candidates still not AI visually reviewed in total.

Do not describe the state as 50/85 reviewed until the batch-05 AI-adjudication checkpoint actually occurs.

## 16. Sparse-evidence limitation remains

The two temporal panels and one trigger per pair are intentionally bounded evidence.

They do not prove full-video independence, independent capture provenance, absence of all shared/cropped/transformed source content, disposition accuracy, inter-rater reliability or global OULU lineage clearance.

## 17. No research-frame-bank claim is allowed

The 1956 private per-frame thumbnails exist for integrity and deterministic packet construction. They must not silently become a new research frame bank, training set or target-informed preprocessing resource.

The separation from the research model path should remain explicit.

## 18. Scientific/model gates remain blocked

Checkpoint 1.5AG does not authorize OULU content-lineage completion, data-audit completion, source-dry-run, analysis freeze, locked target evaluation, detector/classifier/risk-model execution, other-dataset evaluation or scientific readiness.

Those gates remain fail-closed.

## 19. Authorized next step

After acceptance of this review, the next permitted step is:

**AI-assisted visual inspection of batch-05 ranks 40–49 only.**

The AI review should use only the already bound evidence:

- two temporal panels per pair;
- one trigger image per pair.

It should produce proposal dispositions only, with no human attestation or effective disposition.

## 20. Positive-lineage handling remains fail-closed

If AI inspection of any rank 40–49 finds credible evidence of `confirmed_same_content_or_derived_lineage`, the pipeline must preserve that finding and move toward the prospective scientific-stop path.

It must not skip/reorder candidates or continue merely to obtain ten rejection outcomes.

## 21. What is not yet authorized

This review does not authorize:

- human adjudication before the AI-proposal checkpoint is recorded and reviewed;
- batch-05 activation;
- ranks 50+ preparation;
- another dataset;
- model execution.

The staged order should remain:

1. packet preparation;
2. AI visual proposals;
3. review AI-proposal checkpoint;
4. genuine human handoff;
5. human import/reconciliation if required;
6. separate activation;
7. review activation;
8. only then continue the next queue block.

## Final disposition

**DOCUMENT 160 — ACCEPTED.**

**CHECKPOINT 1.5AG BATCH-05 PRIVATE PACKET PREPARATION — ACCEPTED WITHOUT REWORK.**

The packet preparation is deterministic, fixed-order, provenance-bound and reproducible:

- ranks 40–49 only;
- 10 pair packets;
- 16 source videos;
- 1956 accepted RGB frames;
- 1986 verified PNGs;
- 2014 private files;
- 2014/2014 independent redecode/reexport byte-identical;
- 66/66 focused tests passed;
- 253/253 full tests passed;
- exact publication CI succeeded.

The accepted current screen-level total remains **40**.

Batch-05 ranks 40–49 remain **prepared but unreviewed**.

**AI-assisted visual adjudication of ranks 40–49 is now authorized.**

Do not begin human adjudication, rank 50+, other datasets or research-model execution until the subsequent staged checkpoints are completed.
