# 137 — Review of Document 136: OULU Batch-03 Evidence Packet Preparation

Date: 2026-10-12  
Repository: `lathevinh/fas`  
Reviewed commit: `09d2e5d884d16f20cabd0c6502c5bb546d4885b2`  
Reviewed document: `docs/136-review-response-doc135-oulu-batch03-packets.md`

## Verdict

**DOCUMENT 136 — ACCEPTED.**

**CHECKPOINT 1.5S OULU BATCH-03 EVIDENCE PREPARATION — ACCEPTED WITHOUT REWORK.**

**VISUAL ADJUDICATION OF BATCH 03 HAS NOT STARTED YET.**

Document 136 correctly performs only the next bounded preparation step after accepted batch-02 closure. It prepares exactly frozen queue ranks 20–29, generates and verifies private evidence packets, and does not infer any new AI/human/effective disposition from decode/hash success.

With this review acceptance, AI-assisted visual review of ranks 20–29 may begin. Queue ranks 30+ should remain paused until the batch-03 review chain reaches the same appropriate boundary.

## 1. Queue progression is correct

The new runner explicitly requires the previous batch-02 activation state to satisfy:

- `batch02_accepted_reconciled_disposition_state = true`;
- `effective_dispositions_activated = 10`;
- current effective counts exactly `{rejected_false_positive: 10}`.

Only then does it select exactly queue entries 20 through 29.

It additionally requires every selected row to retain `priority = cross_role_conflicting_label`.

This is a strong fail-closed continuation rule.

## 2. No cherry-picking or outcome-dependent selection is visible

The selected queue is fixed to ranks 20–29.

There is no candidate replacement, outcome-based skipping or screening-threshold retuning.

The public aggregate explicitly reports `outcome_dependent_selection = false`.

## 3. Preparation is correctly separated from adjudication

All batch-03 packets are written with:

- `review_performed = false`;
- `disposition = awaiting_visual_review`.

The public report also records:

- images actually visually reviewed: 0;
- new AI dispositions: 0;
- new human dispositions: 0;
- new effective dispositions: 0.

Successful image generation, decode checks or hash checks are therefore not treated as evidence of content independence.

## 4. Evidence generation is strong and internally consistent

Document 136 reports:

- 10 prepared pairs;
- 17 distinct videos;
- 2,417 decoded RGB frames verified against the accepted frame index;
- 2,417 persisted verified-frame PNGs;
- 30 temporal panel / trigger PNGs;
- 17 video manifests;
- 10 pair packets;
- lineage + summary.

The total `2417 + 30 + 17 + 10 + 2 = 2476` is correct.

The readable/hash-verified PNG count `2417 + 30 = 2447` is also internally consistent.

## 5. Full-frame verification and trigger reconstruction are stronger than simple file-existence checks

The runner reopens pinned media payloads and verifies payload size, payload SHA-256, accepted frame identities, full RGB frames, thumbnail hashes and 17 fixed temporal sampling orders.

The verification also reconstructs both temporal panels from persisted thumbnails and recomputes the earliest minimum-Hamming trigger witness from accepted fingerprints.

This gives a strong binding between source media, accepted screening evidence and displayed review assets.

## 6. Trigger selection is deterministic

The trigger witness uses the minimum Hamming distance across accepted fingerprint samples and deterministic slot-order tie breaking.

The runner verifies that the recomputed minimum equals the accepted candidate `minimum_hamming`.

This prevents later substitution of a visually convenient trigger.

## 7. Existing accepted queue and evidence are checked before export

The runner verifies:

- accepted batch-02 activation/current-ledger hashes;
- exact-candidate queue bundle;
- frozen artifacts;
- accepted media/fingerprint bundles;
- archive byte pins;
- locked FFmpeg version;
- visual module/policy hashes;
- previous batch runner integrity;
- Review 135 authority.

This is an appropriate precondition chain.

## 8. Protected evidence remains unchanged

Thirteen protected prior roots are reported unchanged.

All thirteen frozen hashes match the accepted registry.

No prior AI, human, reconciliation or activation record is modified.

No source role, selector, split seed or screening threshold changes occur.

## 9. Reproducibility is excellent for a preparation checkpoint

The first export contains **2,476 files**.

The independent reread/redecode/reexport reproduces **2,476 / 2,476 byte-identically**.

Existing-output reuse fails rather than overwriting accepted evidence.

Temporary AVI extraction files are removed.

## 10. The new selector test adds useful protection

Document 136 reports a regression test that rejects:

- unclosed batch 02;
- fewer than ten effective activations;
- wrong effective counts;
- incomplete/reordered queue;
- wrong priority;
- repository output;
- existing output.

This directly protects the newly introduced batch-transition logic.

## 11. Local tests are strong

- Focused regression: **56/56 passed**
- Full regression: **243/243 passed**
- Zero failures/errors

The full suite was rerun because a new runner and selector test were introduced.

## 12. Exact checkpoint CI passes

Fresh GitHub Actions for exact commit `09d2e5d884d16f20cabd0c6502c5bb546d4885b2` completed successfully.

The exact CI job passes synthetic regression, canonical schema validation, unavailable-stage fail-closed checks and legacy-stage rejection checks.

There is no CI blocker on checkpoint 1.5S.

## 13. Public evidence still cannot inspect private pair bodies

The public repository exposes counts, hashes, queue ranks, reproducibility outcomes and scope flags, not biometric PNGs or private candidate contents.

This review therefore validates the preparation/provenance mechanism and public consistency, not the private visual content of the ten pairs.

## 14. Current queue state is correct

After this checkpoint:

- prior resolved candidate relationships: 20;
- remaining highest-risk candidates lacking AI visual review: 65;
- prepared for immediate batch-03 review: 10;
- not yet prepared: 55.

No rank 30+ was selected.

## 15. Next permitted step

The project may now perform AI-assisted visual inspection of the 30 bound assets for ranks 20–29.

The same rules remain:

- use only fixed prepared evidence;
- preserve queue order;
- record pair-specific rationale;
- leave insufficient cases `uncertain_insufficient_evidence`;
- hard-stop if any pair is `confirmed_same_content_or_derived_lineage`;
- do not create human/effective dispositions during the AI-proposal checkpoint.

## 16. Do not prepare ranks 30+ yet

Ranks 30+ should remain untouched until the batch-03 AI proposal checkpoint is published and reviewed.

## 17. Scope remains narrow

Packet preparation does not establish content independence, capture provenance, full-video independence, absence of partial/shifted/transformed shared material, or global OULU lineage clearance.

No such overclaim is made.

## 18. Scientific/model gates remain blocked

This checkpoint does not authorize data-audit completion, source-dry-run, analysis freeze, locked target evaluation, detector/model execution, target-domain experiments or scientific readiness.

## Final disposition

**DOCUMENT 136 — ACCEPTED.**

**CHECKPOINT 1.5S OULU BATCH-03 EVIDENCE PREPARATION — ACCEPTED WITHOUT REWORK.**

Batch 03 is now validly prepared:

**10 fixed pairs (ranks 20–29), 17 videos, 2,417 verified source frames, 30 bound review images, 0 new dispositions.**

**The next permitted step is AI-assisted visual review of ranks 20–29 only.**

This acceptance does not imply any new lineage clearance or permission to begin ranks 30+ or model execution.
