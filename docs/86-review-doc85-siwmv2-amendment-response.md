# 86 — Review of Document 85: SiW-Mv2 Amendment Response

Date: 2026-10-08
Repository: `lathevinh/fas`
Reviewed commit: `5602428306bf5b6487579543b963751d5858393b`
Reviewed document: `docs/85-review-response-doc84-siwmv2-amendment.md`

## Verdict

**Document 85 is scientifically sound and its correction to Document 84 is accepted.**

No fatal objection was found. Its four requested clarifications should be incorporated into the dated benchmark amendment.

However, one additional requirement should be added before the amendment is accepted as executable: verify and freeze **attack-family coverage inside the actual 1,680-video Protocol-I intersection**, not merely in the 1,700-video raw archive.

## What Document 85 gets right

### 1. Video fallback must apply at every split boundary

This is an important correction.

If SiW-Mv2 participant identity is genuinely unavailable, the same video-group unit must be used consistently for:

- permanent source roles;
- head inner validation;
- matched sample-OOF;
- fold-local calibration;
- derived frame/crop ancestry;
- target uncertainty resampling.

It is not sufficient to use video groups only for permanent roles.

This is fully consistent with Document 42, which already permits complete video groups when subject identity is genuinely unavailable.

### 2. Video grouping does not imply participant-disjointness

Document 85 correctly prevents an overclaim.

Video-group separation guarantees that frames/crops from one video do not cross split boundaries, but it does not prove that two videos from the same person are separated.

Therefore the paper must not describe SiW-Mv2 source roles or bootstrap intervals as verified subject-disjoint or participant-clustered.

This is a limitation, not an automatic blocker under the frozen protocol.

### 3. The 1,680-video intersection policy is coherent

The current evidence supports:

- train live: 524
- train attack: 533
- test live: 261
- test attack: 362
- combined: 1,680

The 867 repeated spoof rows in `trainlist_all.txt` are balancing repetitions, not additional physical videos. Document 85 correctly requires unique-token membership and forbids those repetitions from becoming transactions or implicit weights.

The 20 observed spoof videos not present in the pinned lists should remain in the raw inventory but outside the primary benchmark.

The 11 live list entries without media should remain explicit missing references and should not become attempted transactions.

### 4. The estimand population is genuinely new

Document 85 is right that saying “only the target set changes” is incomplete.

The new study changes:

- one of four domains;
- source composition in three folds;
- the SiW-Mv2 source and target population;
- grouping approximation for SiW-Mv2;
- attack-family exposure.

RQ1/RQ2 formulas and pass criteria can remain fixed, but the resulting estimates are conditional on a new four-domain population and are not MCIO estimates.

Track A should remain historical MCIO literature context only.

## Additional required clarification

### Attack-family coverage must be verified on the eligible intersection

Document 84 proposed retaining all 14 SiW-Mv2 attack types, and Document 85 says the upcoming amendment should include the “all-14-attack scope.”

The current prerequisite evidence only proves that the **raw archive** contains 14 spoof folders. It does not yet show the per-attack membership after applying the Protocol-I intersection.

This matters because 20 observed spoof videos are excluded as out-of-protocol. In principle, those exclusions could disproportionately affect one attack family or even remove a family from either train or test.

Before freezing the amendment, generate and freeze a table for the **eligible 895 attack videos**:

| attack_family | train_count | test_count | total_count |
|---|---:|---:|---:|
| each of 14 mapped types | ... | ... | ... |

Acceptance rules:

1. every eligible video has exactly one versioned attack-family mapping;
2. counts sum exactly to 533 train + 362 test = 895;
3. the exact excluded 20 videos have explicit `out_of_protocol` reason;
4. the claim “all 14 attack types are used” is made only if all 14 have nonzero eligible membership;
5. if a family is absent from either source or target partition, report that fact rather than implying balanced or complete family coverage.

This is not a demand for equal attack counts. It is a semantic verification needed to make the population definition truthful.

## One wording refinement

Avoid calling the 1,680-video population simply “Protocol I” in paper-facing prose.

Safer wording:

**“SiW-Mv2 Protocol-I intersection population”**

or

**“pinned-reference Protocol-I intersection”**

because the study deliberately intersects the supplied archive with pinned reference lists and excludes mismatches. Document 85 already makes this distinction internally; the amendment and manuscript should preserve it.

## Statistical interpretation

Video-cluster bootstrap for SiW-Mv2 is allowed by the frozen plan. Because Track B has one evaluation transaction per video, on the SiW-Mv2 target this is effectively transaction/video-level resampling.

It must not be presented as subject-level resampling.

For source-side sample-OOF and inner validation, video grouping remains important because training candidate banks may contain multiple derived frames from each video.

## Final disposition

**DOCUMENT 85 — ACCEPTED WITH ONE REQUIRED ADDITION TO THE UPCOMING AMENDMENT.**

Required before benchmark amendment acceptance:

- incorporate Document 85's four clarifications;
- freeze the 1,680-video exact eligible-ID population;
- add per-attack train/test counts over the 895 eligible spoof videos;
- verify whether all 14 attack families actually survive the Protocol-I intersection;
- use explicit “Protocol-I intersection” wording.

No need to reopen the decision to replace Replay-Attack with SiW-Mv2.

The next checkpoint should be the actual dated benchmark/config amendment, not another conceptual review loop.
