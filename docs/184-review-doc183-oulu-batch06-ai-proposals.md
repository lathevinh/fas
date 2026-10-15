# 184 — Review of Document 183: OULU Batch-06 AI Visual Proposals

Date: 2026-10-15  
Repository: `lathevinh/fas`  
Reviewed commit: `38e0263c0e20d0d3a27df431142a6550335d8db6`  
Reviewed document: `docs/183-review-response-doc182-oulu-batch06-ai-proposals.md`  
Reviewed aggregate: `results/phase1/oulu-visual-review-batch06-v1.json`

## Verdict

**DOCUMENT 183 — ACCEPTED WITHOUT REWORK FOR AI-SCREENING / PROVENANCE SCOPE.**

**THE TEN AI VISUAL PROPOSALS FOR RANKS 50..59 ARE ACCEPTED AS NON-BINDING AI PROPOSALS.**

**AI-SCREEN COVERAGE MAY NOW BE TREATED AS 60/85.**

**THE ACCEPTED CURRENT EFFECTIVE SCREEN-LEVEL TOTAL REMAINS 50.**

**THE TEN `rejected_false_positive` PROPOSALS ARE NOT HUMAN DISPOSITIONS AND MUST NOT BE ACTIVATED DIRECTLY.**

**NEXT AUTHORIZED STEP: PREPARE A SEPARATE CATEGORICAL-ONLY HUMAN HANDOFF FOR EXACT RANKS 50..59 USING THE ALREADY-BOUND 30 ASSETS.**

**DO NOT START RANK60+, DO NOT ACTIVATE BATCH06, AND DO NOT RUN RESEARCH MODELS.**

## 1. Scope is exact

Document183 covers exactly ranks `50..59`. No later queue rank is included.

## 2. Review182 authority is respected

Review182 authorized AI visual proposal/screening only. Document183 preserves historical181 pending/unauthorized fields and does not convert packet preparation into human review or activation.

## 3. The AI actually inspected the declared review assets

Document183 records actual opening of `temporal_a.png`, `temporal_b.png`, and `trigger.png` for each of the ten ranks: **30 assets total**.

## 4. The visual-inspection claim is properly bounded

The checkpoint explicitly does not claim that all 2126 source frames were visually inspected. Those frames were technically verified during packet181; Document183 visually inspected only the 30 fixed review assets.

## 5. AI reasoning is restricted to permitted non-identity evidence

The declared basis is visible upper-garment structure, clothing layering, closure/pattern/render geometry, and supplementary scene/context. Biometric identity was not inferred.

## 6. All three scientific outcomes remained available

The AI definition retained `rejected_false_positive`, `confirmed_same_content_or_derived_lineage`, and `uncertain_insufficient_evidence`. No forced-rejection quota is reported.

## 7. Observed AI outcome is ten rejections

The checkpoint records 10 proposed rejections, 0 confirmed same/derived, and 0 uncertain. No scientific hard stop is triggered by the AI proposal set.

This is acceptable as an AI proposal set, not as ten independently validated scientific decisions.

## 8. The all-reject outcome does not establish correctness

Ten out of ten rejection proposals are not a blocker because all outcomes remained available and pair-specific rationale/visibility limits were recorded. But the outcome also does not prove perfect specificity; human adjudication remains required before activation.

## 9. Visibility limitations are materially relevant

Document183 identifies haze at rank54 and dim/crushed garment regions at ranks56,58,59. These do not automatically invalidate the proposals, but they require particular attention during human review.

## 10. Hidden regions are correctly not treated as observed evidence

The document does not claim hidden lower-chest structure was assessed. Occlusion/darkness must not be converted into evidence of difference.

## 11. Correlation among ranks56..59 is correctly disclosed

Reused-video relations are reported for 56/57, 56/58, 57/59, and 58/59. These proposals are correlated evidence, not independent trials or raters.

## 12. Correlation does not remove per-rank adjudication

Ranks56..59 remain separate frozen queue candidates. A later human handoff should preserve a separate categorical answer for each rank and must not copy answers across the group.

## 13. Private rationale provenance is adequate for the AI-proposal stage

The public aggregate states that all ten proposed rows contain pair-specific nonblank rationales and visibility notes; the actual text remains private and hash-bound.

This review accepts the provenance/scope of those AI proposal records. It does not treat private AI prose as independently verified human reasoning.

## 14. Sibling replay is correctly characterized

Main and sibling AI roots match **13/13 files byte-for-byte**. This is serialization replay only, not a second AI pass, an independent reviewer, human adjudication, or inter-rater evidence.

## 15. Evidence bindings are strong

The AI checkpoint binds Review182 SHA, accepted packet181 aggregate, visual policy, immutable AI preflight, observation input, definition, ledger, summary, ten-row bundle, and private verification.

## 16. Packet/image/manifest provenance is preserved

Rows are reported as bound to exact packet, queue, image hashes, manifests, decode orders, accepted full-resolution RGB hashes, and trigger witness.

## 17. No media re-export or decode occurred

Document183 performs no new archive rehash, video extraction/decode, or packet generation. Evidence stays fixed after packet181 acceptance.

## 18. Protected prior evidence remains unchanged

The checkpoint reports 57 prior roots unchanged, frozen13 unchanged, config17 unchanged, both accepted packet roots unchanged, and prior policies/helpers/runners/owner records unchanged.

## 19. Commit scope confirms no production-code or test changes

The reviewed commit changes only `README.md`, Document183, and the public batch06 AI aggregate. No production code or test file changes occur.

## 20. Regression evidence is adequate

Document183 reports focused regression **75/75 passed**, with no local full-suite rerun and accepted Document181 full baseline **262/262**. Because this checkpoint changes no production code or tests, that is acceptable.

## 21. Fresh exact Document183 publication CI passes

Exact reviewed commit: `38e0263c0e20d0d3a27df431142a6550335d8db6`.

Fresh GitHub Actions run `38683111522` is `completed / success`.

Validate job `116251844389` is `completed / success`.

The job completed at `2026-10-15T04:46:00Z`.

## 22. AI coverage may now advance to 60/85

Review184 accepts the ten new proposal records as a completed AI-screening checkpoint. Therefore AI-screen coverage may be reported as **60/85**, with **25** highest-risk candidates not yet AI visually screened.

This is an AI-coverage metric only.

## 23. Effective accepted total remains 50

There are no new human dispositions and no batch06 activation. Therefore the accepted current effective screen-level total remains **50**.

## 24. The next human step should cover all ten ranks

If these proposals are to become effective batch06 dispositions, the owner should review all exact ranks50..59. Do not silently accept the non-limited subset from AI alone.

## 25. Human handoff must remain categorical-only

For each rank require only:

1. Evidence sufficient? — Yes / No
2. If Yes: Same or derived content? — Yes / No
3. Personally inspected? — Yes / No
4. Is this your own decision? — Yes / No

No mandatory human-authored prose is required.

## 26. Deterministic human mapping remains unchanged

- Evidence insufficient -> `uncertain_insufficient_evidence`
- Evidence sufficient + same/derived Yes -> `confirmed_same_content_or_derived_lineage`
- Evidence sufficient + same/derived No -> `rejected_false_positive`

A confirmed same/derived answer must preserve the prospective scientific hard stop.

## 27. Do not prefill the human answer with the AI proposal

The owner should inspect evidence and choose independently. Prefer keeping the AI proposal hidden/collapsed until after pair submission.

This is particularly important because all ten AI proposals have the same disposition.

## 28. Human UI may flag visibility limits neutrally

The form may state that rank54 has haze and ranks56/58/59 have dim/crushed garment regions.

That notice should describe visibility constraints only, not suggest a disposition.

## 29. Correlation notice should be neutral

For ranks56..59, the form may state that some source videos/configurations are reused and therefore the evidence is correlated. It must not instruct the owner to reuse a previous answer.

## 30. Reuse the existing 30 assets

The human handoff should use the exact already-bound temporal A, temporal B, and trigger assets for each pair.

Do not decode more media or regenerate packet assets merely to create the form. If evidence is insufficient, uncertainty is the correct outcome.

## 31. Do not reintroduce human rationale fields

Do not require left/right descriptions, visibility paragraphs, or pair-specific rationale. Those fields add work and recreate avoidable AI/prose provenance ambiguity.

## 32. AI prose remains AI provenance

If AI rationale is later exposed in a supplementary audit record, it must remain labeled as AI-generated/proposed reasoning, never as human-authored rationale.

## 33. No activation is authorized by Review184

Review184 accepts only the AI checkpoint and preparation of a categorical human handoff. Human import, reconciliation, effective activation, and batch06 closure require separate reviewed checkpoints.

## 34. Rank60+ remains blocked

Required sequence:

1. Review184 accepts AI183.
2. Prepare categorical human handoff for 50..59.
3. Formal handoff review.
4. Genuine owner categorical answers.
5. Import/reconciliation.
6. Formal import review.
7. Separate additive activation.
8. Activation review.
9. Only then prepare rank60+.

## 35. Scientific/model stages remain blocked

This review does not establish exhaustive OULU content independence, capture independence, transformed-region independence, cross-dataset independence, source-dry-run readiness, analysis freeze, locked target evaluation, or classifier/risk-model execution readiness.

## Final disposition

**DOCUMENT 183 — ACCEPTED WITHOUT REWORK FOR AI-SCREENING / PROVENANCE SCOPE.**

**TEN AI PROPOSALS FOR RANKS50..59 — ACCEPTED AS NON-BINDING PROPOSALS.**

**AI-SCREEN COVERAGE = 60/85.**

**ACCEPTED CURRENT EFFECTIVE SCREEN-LEVEL TOTAL = 50.**

**NEXT AUTHORIZED STEP: A SEPARATE CATEGORICAL-ONLY HUMAN HANDOFF FOR ALL TEN RANKS50..59 USING THE EXISTING 30 BOUND ASSETS.**

Ranks54/56/58/59 require particular human attention because of visibility limitations, and ranks56..59 must be treated as correlated evidence rather than independent corroboration.

Do not expose AI disposition before the owner's pair decision if practical. Do not require human prose. Do not activate batch06 or proceed to rank60+ until the human/import/activation chain is separately completed and reviewed.
