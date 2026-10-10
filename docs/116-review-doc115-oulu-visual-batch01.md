# 116 — Review of Document 115: OULU Private Visual Review Batch 01

Date: 2026-10-10  
Repository: `lathevinh/fas`  
Reviewed commit: `334cdb5ae7bf408b3aff6d9ba29c5c76a7caab27`  
Reviewed document: `docs/115-review-response-doc114-oulu-visual-batch01.md`

## Verdict

**DOCUMENT 115 — ACCEPTED FOR ITS BOUNDED AI-ASSISTED REVIEW SCOPE.**

**CHECKPOINT 1.5H OULU PRIVATE VISUAL REVIEW BATCH 01 — ACCEPTED AS A PROPOSAL/EVIDENCE-GENERATION CHECKPOINT WITHOUT REWORK.**

**THE NINE `rejected_false_positive` PROPOSALS ARE NOT YET ACCEPTED AS FINAL LINEAGE CLEARANCES.**

The method, packet construction, frozen queue selection, evidence binding and reproducibility controls are sound. However, the actual pair-level visual judgments remain private AI-assisted proposals and have not been independently reviewed here or by a second human reviewer.

Therefore this checkpoint may be accepted as completion of the first bounded visual-review batch, but it does not close those nine candidate relationships scientifically.

## 1. Batch selection is prospective and non-cherry-picked

The reviewed population is exactly:

- priority population: cross-role + conflicting-label;
- queue ranks: 0 through 9;
- batch size: 10 pairs.

The policy explicitly states:

`queue_ranks_0_through_9_no_outcome_cherry_pick`

This is the correct way to start manual/private adjudication.

Selection is not based on apparent ease, screening distance after inspection, expected outcome, role desirability or downstream model behavior.

## 2. The visual-review rule is defined before observation

The policy freezes three dispositions:

- `confirmed_same_content_or_derived_lineage`;
- `rejected_false_positive`;
- `uncertain_insufficient_evidence`.

Confirmation requires recognizable shared rendered sequence or a specific derivation supported by temporal correspondence.

Rejection requires clear content divergence that explains the screening trigger without a recognizable corresponding rendered sequence.

Uncertainty is retained whenever sampling, resolution, transformation or provenance ambiguity prevents a supported decision.

This is a reasonable conservative visual-review rule.

## 3. The evidence packet is strongly bound to accepted media

For the ten reviewed pairs:

- 19 unique source videos are involved;
- 2,624 full-resolution decoded RGB frames are reverified against accepted frame identities;
- packet construction rereads and redecodes the pinned source media;
- frame count, dimensions, order and RGB digests are rechecked;
- temporary AVI files are removed;
- thumbnail evidence is bound by hashes.

This is substantially stronger than reviewing unbound screenshots or arbitrary exported frames.

## 4. Visual coverage is explicit but incomplete

Each pair provides:

- two temporal panels using 17 fixed ranks;
- one trigger-witness image.

Exactly 30 images were actually viewed for ten pairs.

The document correctly states that not every original frame was visually inspected.

Sparse temporal panels and resized thumbnails may miss short shared subsequences, small overlays, localized crops, transformed regions or temporal shifts.

Therefore a visual rejection proposal cannot be interpreted as proof that no possible shared source content exists.

## 5. Observed reviewer proposals

For the first ten highest-risk pairs:

| Proposed disposition | Count |
|---|---:|
| Confirmed same/derived content | 0 |
| Rejected screen false positive | 9 |
| Uncertain insufficient evidence | 1 |

These counts are internally consistent with the public report.

However, the nine rejection results are explicitly reviewer proposals, not accepted scientific clearances.

## 6. AI-assisted reviewer disclosure is correct

The reviewer is disclosed as GitHub Copilot using AI-assisted visual observation.

The checkpoint does not claim independent human review, blinded second review, validated visual-lineage classifier or inter-rater reliability.

This disclosure is essential and is handled correctly.

## 7. Why I do not accept the nine proposals as final lineage dispositions

The private pair identities, visual panels and pair-specific rationales are intentionally not published.

Therefore this review can verify the method, queue selection, packet construction, artifact hashes, coverage counts, reproducibility and policy constraints.

It cannot independently verify that each of the nine specific visual judgments is correct.

In addition, the checkpoint itself states:

`independent_human_review_claimed = false`

and:

`validated_disposition_accuracy_or_interrater_reliability = false`.

Accordingly, the correct status is:

> Nine AI-assisted screen-rejection proposals were generated.

not:

> Nine cross-role candidate pairs are scientifically cleared.

## 8. The uncertain pair is correctly retained

One pair remains `uncertain_insufficient_evidence`.

This is a positive methodological sign.

The reviewer did not force every pair into a binary answer.

## 9. No frozen study definition is modified

The checkpoint does not change canonical IDs, source roles, split seed `20261009`, primary-frame selector, transaction policy, screening thresholds or prior candidate dispositions.

No reviewed pair is automatically removed from training/evaluation populations.

This is correct.

## 10. Reproducibility evidence is strong

Original and rerun packet exports contain 2,685 byte-identical artifacts each.

The rerun rereads and redecodes the 19 videos rather than merely replaying saved fingerprints.

Verification checks 2,624 frame/thumbnail digests, 19 manifests, 10 pair packets, viewed-image bindings, policy/code/frozen hashes, cleanup and byte identity.

This is good evidence-generation reproducibility.

It does not validate the correctness of the visual judgment itself, which Document 115 correctly acknowledges.

## 11. Tests and CI pass

Reported tests:

- focused: 46/46;
- full regression: 233/233;
- zero failures/errors.

Fresh GitHub Actions on exact commit `334cdb5ae7bf408b3aff6d9ba29c5c76a7caab27` completed successfully.

## 12. Coverage remains very incomplete

After this batch:

- highest-risk cross-role + conflicting-label pairs remaining: 75;
- all cross-role pairs not yet visually reviewed: 474;
- all non-exact candidates not yet visually reviewed: 6,630.

Therefore this checkpoint is only an initial slice.

It cannot be used to claim OULU content-lineage closure.

## 13. Required next action

Before accepting any of the nine rejection proposals as final adjudications, perform a bound owner/human review of the ten pair packets.

Recommended procedure:

1. preserve the AI-assisted proposal ledger unchanged;
2. have the owner or designated reviewer inspect the same bound private evidence;
3. record a second disposition for each of the ten pairs;
4. preserve disagreements explicitly;
5. do not overwrite the AI proposal;
6. use `uncertain` whenever the available evidence remains insufficient.

For the one already uncertain pair, use higher-detail/full-resolution temporal evidence before attempting closure.

## 14. Continue the frozen priority queue only after the first batch is dispositioned

Once batch 01 receives owner/human dispositions, continue the remaining 75 highest-risk pairs in their existing queue order.

Do not reorder by apparent difficulty, skip inconvenient pairs, tune screening thresholds, regenerate roles, retry the split seed or delete candidate videos automatically.

## 15. Scientific action if a cross-role relationship is confirmed

If any pair is confirmed as same/derived rendered content across roles:

- stop before model execution;
- preserve the affected IDs and evidence privately;
- document an explicit prospective scientific decision;
- do not silently exclude one sample;
- do not reassign roles;
- do not retry seed `20261009`.

The frozen-study constraint remains unchanged.

## 16. Scientific gates remain blocked

Current state remains correctly:

- schema: pass;
- data-audit: blocked;
- source-dry-run: blocked;
- analysis-freeze: blocked;
- locked-evaluation: blocked;
- model execution unauthorized;
- scientific readiness false.

## Final disposition

**DOCUMENT 115 — ACCEPTED.**

**CHECKPOINT 1.5H OULU PRIVATE VISUAL REVIEW BATCH 01 — ACCEPTED AS A BOUNDED AI-ASSISTED EVIDENCE/PROPOSAL CHECKPOINT.**

Observed proposals:

- 9 proposed screen false positives;
- 1 uncertain;
- 0 proposed same/derived-content confirmations.

However:

**the nine rejection proposals are not yet final scientific lineage clearances.**

A bound owner/human review of this first batch is required before those candidate relationships can be considered adjudicated.
