# 114 — Review of Document 113: OULU Full-Frame Exact Evidence Slice

Date: 2026-10-09  
Repository: `lathevinh/fas`  
Reviewed commit: `691684a1fdb328430e4cb412c89ebe5ff6d6fa20`  
Reviewed document: `docs/113-review-response-doc112-oulu-lineage-exact-evidence.md`

## Verdict

**DOCUMENT 113 — ACCEPTED FOR ITS EXACT-EVIDENCE SCOPE.**

**CHECKPOINT 1.5G OULU FULL-FRAME EXACT-EVIDENCE SLICE — ACCEPTED WITHOUT REWORK.**

**OULU NEAR-DUPLICATE / CONTENT-LINEAGE ADJUDICATION — STILL NOT COMPLETE.**

The checkpoint correctly examines all 6,640 unresolved non-exact candidates using complete accepted decoded-frame identities and deliberately refuses to treat absence of exact RGB matches as proof of independent content.

No frozen role, selector, split seed, preprocessing rule or scientific-readiness state is changed.

## 1. All unresolved non-exact candidates are processed

The checkpoint processes exactly:

`6,640`

non-exact candidate pairs from Document 111/Review 112.

Exclusive priority ordering is:

| Priority | Population | Pairs |
|---|---|---:|
| 1 | Cross-role + conflicting-label | 85 |
| 2 | Remaining cross-role | 399 |
| 3 | Remaining cross-partition | 185 |
| 4 | Remaining conflicting-label | 91 |
| 5 | Remaining candidates | 5,880 |
| **Total** | | **6,640** |

This is consistent with the earlier overlapping screening totals:

- 484 cross-role;
- 466 cross-partition;
- 240 conflicting-label.

No boundary-risk category is silently omitted.

## 2. Full accepted decoded-frame evidence is used

Unlike the five-frame pHash screen, this checkpoint uses each video's complete accepted decoded frame index.

A frame identity token consists of:

- width;
- height;
- decoded RGB SHA-256.

The implementation validates:

- successful decoded status;
- complete frame count;
- decode order;
- dimensions;
- RGB digest format;
- monotone timestamps.

This is appropriate for exact rendered-content evidence.

## 3. Confirmation rule is conservative

A pair is confirmed as `confirmed_same_content_or_derived_lineage` only when:

- the entire shorter decoded sequence is contained contiguously in the other sequence; and
- the contained sequence includes at least two distinct RGB frame tokens.

This avoids confirming lineage from:

- one isolated shared frame;
- static repeated frames;
- weak partial overlap.

The scope is correctly limited to same rendered decoded content.

It does **not** claim original-capture provenance.

## 4. Observed exact-evidence result

Across all 6,640 non-exact candidates:

- confirmed same rendered content: **0**
- rejected false positive: **0**
- uncertain insufficient evidence: **6,640**
- pairs with any shared exact RGB frame token: **0**

Therefore there is no exact decoded-frame overlap among the previously non-exact candidate pairs.

This is a useful negative exact-identity result.

It is **not** evidence that the pairs are independent captures.

## 5. The decision not to reject candidates is correct

The implementation/report explicitly refuses to infer `rejected_false_positive` from absence of exact RGB hashes.

That is scientifically correct because:

- re-encoding can change every decoded pixel;
- resize/crop can change every frame hash;
- overlays can change every frame hash;
- color conversion/compression can alter hashes;
- temporal offsets may preserve lineage without exact matched frames.

Therefore all 6,640 pairs correctly remain:

`uncertain_insufficient_evidence`

at this checkpoint.

## 6. Cross-role candidates remain unresolved

The 484 cross-role candidates have **not** been cleared.

This includes the 85 cross-role + conflicting-label pairs, which remain the highest-priority lineage-review population.

Document 113 must not be summarized as:

> No cross-role duplicate leakage exists.

The valid current statement is:

> No exact decoded RGB frame overlap was observed among the 484 cross-role non-exact screening candidates.

That is substantially narrower.

## 7. Existing 13 exact pairs remain separate

The earlier 13 full-video exact duplicate pairs are not reclassified by this pass.

They remain known exact content pairs from the accepted per-video media audit.

This is correct because checkpoint 1.5G is explicitly scoped to the 6,640 previously non-exact candidates.

## 8. Implementation logic is sound for exact sequence evidence

The longest contiguous run is computed over full ordered RGB-token sequences.

The implementation:

- indexes token positions;
- tracks contiguous equal runs;
- reports run starts;
- counts shared unique RGB tokens;
- tests whether the shorter sequence is fully contained;
- requires multiple distinct frames before confirming rendered-content lineage.

This is suitable for the stated exact-evidence objective.

It does not overreach into perceptual or provenance inference.

## 9. Reproducibility evidence is strong

The report records:

- original and rerun outputs: **6,642 byte-identical files**;
- all 6,640 pair records independently checked;
- priority ordering checked;
- export hashes checked;
- 500 seeded synthetic comparisons agree with an independent brute-force longest-run implementation;
- existing-output retry is refused.

This is good evidence for implementation correctness and immutable output.

## 10. Tests and CI pass

Reported tests:

- focused: **42/42**
- full regression: **229/229**
- zero failures/errors.

Test fixtures include:

- complete trimmed sequence;
- repeated/static frames;
- reversed overlap;
- partial overlap;
- no overlap;
- invalid indices/digests/dimensions;
- exclusive priority assignment;
- private-output refusal.

Fresh GitHub Actions on exact commit:

`691684a1fdb328430e4cb412c89ebe5ff6d6fa20`

completed successfully.

## 11. Frozen study state remains intact

The checkpoint preserves:

- all 13 frozen canonical/role artifacts;
- source roles;
- transaction policy;
- primary selector;
- screening policy;
- prior media evidence;
- split seed `20261009`.

There is:

- no role rewrite;
- no selector rewrite;
- no seed retry;
- no media repair;
- no model execution.

This is correct.

## 12. This checkpoint does not close OULU lineage review

The exact-evidence pass only answers:

> Do any of the 6,640 candidate pairs share exactly identical decoded RGB frames/sequences?

Observed answer:

> No.

It does **not** answer:

> Are these videos derived from the same source capture/content after re-encoding, crop, overlay or transformation?

That remains unresolved.

Therefore OULU content-lineage audit is still open.

## 13. Required next checkpoint

The next step should use stronger private evidence, beginning with the highest-risk populations:

1. 85 cross-role + conflicting-label pairs;
2. 399 other cross-role pairs;
3. 185 additional cross-partition pairs;
4. 91 additional conflicting-label pairs;
5. remaining candidates if required for closure.

Each reviewed pair should receive one of:

- `confirmed_same_content_or_derived_lineage`;
- `rejected_false_positive`;
- `uncertain_insufficient_evidence`.

Evidence may include stronger full-content/visual/temporal comparison, but the method and adjudication rule must be documented prospectively.

Visual similarity alone should not be mislabeled as original capture provenance.

## 14. Scientific action if cross-role lineage is confirmed

If any cross-role same/derived-content relationship is confirmed:

- stop before model execution;
- document the affected IDs and boundary privately;
- make an explicit prospective scientific decision;
- do not silently delete a sample;
- do not regenerate roles;
- do not retry seed `20261009`;
- do not tune the screen to make the pair disappear.

This remains the correct frozen-study response.

## 15. Scientific gates remain blocked

Current state appropriately remains:

- schema: pass;
- data-audit: blocked;
- source-dry-run: blocked;
- analysis-freeze: blocked;
- locked-evaluation: blocked;
- model execution unauthorized;
- scientific readiness false.

## Final disposition

**DOCUMENT 113 — ACCEPTED.**

**CHECKPOINT 1.5G OULU FULL-FRAME EXACT-EVIDENCE SLICE — ACCEPTED WITHOUT REWORK.**

The checkpoint provides useful and reproducible negative exact-identity evidence:

> none of the 6,640 non-exact candidates share any exact decoded RGB frame token.

However:

**all 6,640 remain uncertain for near-duplicate/derived-content lineage, including all 484 cross-role candidates.**

The required stronger private adjudication remains the next OULU task.
