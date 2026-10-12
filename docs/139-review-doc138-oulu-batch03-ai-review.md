# 139 — Review of Document 138: OULU Batch-03 AI Visual Proposals

Date: 2026-10-12  
Repository: `lathevinh/fas`  
Reviewed commit: `77d3e7b14b2688451d5ce9bed171c96a55533ce0`  
Reviewed document: `docs/138-review-response-doc137-oulu-batch03-ai-review.md`

## Verdict

**DOCUMENT 138 — ACCEPTED FOR AI-PROPOSAL SCOPE.**

**CHECKPOINT 1.5T OULU BATCH-03 AI-ASSISTED VISUAL PROPOSALS — ACCEPTED WITHOUT METHOD REWORK.**

**BATCH 03 EFFECTIVE / SCIENTIFIC CLOSURE — NOT ACCEPTED YET.**

Document 138 correctly performs the bounded AI-assisted visual inspection authorized by Review 137 for ranks 20–29, records only AI proposals, preserves accepted packets and prior histories, and stops before any human/effective disposition is created.

## Key findings

- Exactly ranks 20–29 were reviewed; no other pair was opened.
- 30 bound images were actually inspected: two temporal panels + one trigger per pair.
- AI proposals are 10 `rejected_false_positive`, 0 uncertain, 0 confirmed same/derived.
- Human dispositions = 0; effective dispositions = 0; batch 03 remains open.
- Pair-specific nonblank unique rationales = 10.
- Ranks 26–29 share repeated foreground configurations; this is correctly disclosed as correlated evidence, not independent replicates.
- The proposal scope is limited to the observed sparse rendered-content evidence; it does not certify capture provenance, full-video independence, or absence of all shifted/partial/transformed common material.
- Private AI ledger has 12 files and reproduces 12/12 byte-identically; overwrite is refused.
- Original 2,476 packet files and 14 protected prior roots remain unchanged.
- Focused regression: 56/56 passed.
- Full 243-test suite was not rerun because code/tests/policy/environment did not change; this is acceptable for an observation-ledger checkpoint.
- Fresh CI for exact commit `77d3e7b14b2688451d5ce9bed171c96a55533ce0` completed successfully.

## Assessment of the 10/10 rejection result

A third consecutive 10/10 rejection batch deserves attention, but is not by itself a methodological failure. The queue was frozen, thresholds were unchanged, uncertainty/confirmation remained allowed, no rejection quota was imposed, and each pair reportedly has its own concrete rationale.

The pattern may later indicate that the perceptual-screening heuristic has low precision/high false-positive yield in this part of the queue. That is a property to report, not a reason to invalidate this checkpoint.

## Correlated evidence limitation

The repeated foreground configurations in ranks 26–29 mean these outcomes must not later be treated as ten statistically independent accuracy measurements.

They can remain separate candidate-level adjudication records because each pair is independently bound to its own candidate, packet, panels, trigger and manifests.

## Required next step

Prepare a separate genuine human-review handoff for exactly ranks 20–29:

1. preserve the AI ledger unchanged;
2. use the same 30 bound assets;
3. start human answers blank;
4. do not pre-select AI dispositions;
5. preferably keep AI proposals collapsed initially;
6. require explicit human disposition, rationale and personal-review attestation for each pair;
7. preserve original ranks 20–29 in the exported JSON.

Conservative resolution remains mandatory:

- AI reject + human reject → eligible for later additive activation;
- AI reject + human uncertain → remain uncertain pending reconciliation;
- human confirmed same/derived → immediate scientific hard stop.

Do not begin ranks 30+ until batch-03 human review, any reconciliation, and separate additive activation are complete and reviewed.

## Final disposition

**DOCUMENT 138 — ACCEPTED FOR ITS AI-PROPOSAL SCOPE.**

**CHECKPOINT 1.5T — ACCEPTED WITHOUT METHOD REWORK.**

Current state:

**10 AI rejects, 0 uncertain, 0 confirmed, 0 human, 0 effective.**

Next: **genuine human review handoff for ranks 20–29 only.**
