# 112 — Review of Document 111: OULU Model-Free Content Candidate Screening

Date: 2026-10-09  
Repository: `lathevinh/fas`  
Reviewed commit: `f76d982147628ac06d1de8e01f155db4f5e0cf89`  
Reviewed document: `docs/111-review-response-doc110-oulu-content-screening.md`

## Verdict

**DOCUMENT 111 — ACCEPTED FOR ITS SCREENING SCOPE.**

**CHECKPOINT 1.5F OULU MODEL-FREE CONTENT CANDIDATE SCREENING — ACCEPTED WITHOUT REWORK.**

**OULU NEAR-DUPLICATE / CONTENT-LINEAGE ADJUDICATION — NOT YET COMPLETE.**

The checkpoint correctly implements a prospective, model-free candidate generator and does not misclassify candidate pairs as confirmed duplicates or leakage events.

No role, selector, split seed or scientific-readiness state is changed.

## 1. Comparison population is complete for successfully decoded OULU videos

Successfully decoded/fingerprinted videos:

`4,949`

The number of unordered pairs is exactly:

\[
\binom{4949}{2}=12,243,826
\]

The report compares all of them.

There is no filtering by:

- source role;
- label;
- native partition;
- model output.

This is essential because filtering those attributes could hide candidate leakage across important boundaries.

## 2. The failed video remains visible in coverage accounting

The previously identified undecodable OULU video is not fingerprinted because no valid decoded content exists.

However, it remains part of the original 4,950-video coverage denominator.

It is not:

- repaired;
- substituted;
- silently dropped from the canonical population;
- reassigned.

This is consistent with the frozen transaction policy.

## 3. Screening policy is explicit and prospective

The frozen screening definition uses five fixed temporal ranks:

`floor((n - 1) * j / 4), j = 0..4`

For each sampled frame, a fixed 64-bit DCT fingerprint is computed using:

- RGB to grayscale;
- INTER_AREA resize to 32×32;
- top-left 8×8 DCT block;
- median threshold over 63 non-DC coefficients;
- DC bit forced to zero.

Candidate rule:

- any of 25 temporal-slot comparisons has Hamming distance ≤ 4; **or**
- at least 3 of 5 aligned temporal slots have Hamming distance ≤ 8.

The policy explicitly states:

`threshold_tuning = false`

and labels these values as screening heuristics, not validated duplicate-equivalence thresholds.

For the current purpose—candidate generation rather than scientific equivalence classification—this is acceptable.

## 4. Screening must not be interpreted as confirmed lineage

Observed candidate counts:

| Category | Pairs |
|---|---:|
| All candidate pairs | 6,653 |
| Known exact pairs | 13 |
| Unresolved non-exact candidates | 6,640 |
| Cross-role unresolved candidates | 484 |
| Cross-partition unresolved candidates | 466 |
| Conflicting-label unresolved candidates | 240 |

The final three categories overlap and are not additive.

The document correctly does **not** call the 6,640 pairs duplicates.

In particular:

- 484 cross-role candidates are not 484 leakage events;
- 466 cross-partition candidates are not confirmed partition leakage;
- 240 conflicting-label candidates are not evidence of mislabeled duplicate media.

They are prioritization sets for adjudication.

## 5. Recovery of all known exact pairs is a useful sanity check

All 13 previously confirmed exact-content pairs are recovered by the screen.

This is useful positive-control evidence that the screen can retrieve the known exact duplicates in this dataset.

However, this is **not** a recall estimate for unknown near duplicates because the study has no independent complete near-duplicate ground truth.

Document 111 correctly acknowledges this limitation.

## 6. Non-candidates do not certify content independence

The sparse five-frame sampling can miss:

- crops;
- overlays;
- large temporal shifts;
- short shared subsequences;
- derived/re-encoded content;
- capture-lineage relations that are visually less similar.

Therefore a non-candidate pair cannot be interpreted as proven independent content.

The correct current claim is:

> The prospective screen generated 6,653 OULU candidate pairs for further lineage review.

It is not yet valid to claim:

> OULU is near-duplicate-free outside those candidates.

## 7. Candidate reproducibility is adequately checked

The report states that:

- saved fingerprints reproduce identical candidate bytes;
- a different comparison block size produces identical candidate output;
- scalar Hamming distances were independently checked for all 6,653 candidates;
- 5,000 deterministically sampled arbitrary pairs were independently reclassified.

This is good implementation/reproducibility evidence.

It verifies the comparison computation.

It does not provide a second independent extraction pipeline for all fingerprints, and Document 111 correctly does not claim that it does.

## 8. Frozen evidence and study definitions remain intact

The checkpoint preserves:

- all 13 frozen canonical/role artifacts;
- permanent source roles;
- transaction policy;
- primary-frame selector;
- prior media evidence;
- split seed `20261009`.

No role/selector rewrite occurs.

No candidate triggers automatic exclusion.

No seed/split retry is performed.

This is mandatory and correctly enforced.

## 9. No learned model contamination

The content screen is model-free and does not use:

- face detector;
- DINO;
- OpenCLIP;
- classifier outputs;
- risk scores;
- target-domain outcomes.

This is appropriate for a pre-model data-integrity checkpoint.

## 10. Test and dependency evidence is acceptable

Reported tests:

- focused: **36/36**;
- full regression: **223/223**;
- zero failures/errors.

Synthetic coverage includes:

- fixed temporal ranks;
- brightness/re-encode sensitivity;
- different-content rejection;
- cross-role pair inclusion;
- RGB hash mismatch rejection;
- failed-video coverage;
- duplicate identities;
- private-output refusal.

CI explicitly installs:

- NumPy 1.26.4;
- OpenCV-headless 4.11.0.86.

The research `fas` environment itself remains unchanged.

Fresh GitHub Actions on exact commit:

`f76d982147628ac06d1de8e01f155db4f5e0cf89`

completed successfully.

## 11. Threshold semantics must remain screening-only

The Hamming thresholds 4 and 8 have not been scientifically calibrated as equivalence thresholds.

Therefore they must not later be presented as:

- a near-duplicate decision boundary;
- a leakage probability threshold;
- a capture-lineage classifier.

If threshold revision is later justified, it must:

- preserve v1 results;
- receive a new version;
- have an explicit prospective rationale;
- not be tuned merely to reduce inconvenient candidate counts.

Document 111 already states this correctly.

## 12. Candidate adjudication is now the critical next step

Because there are **484 cross-role unresolved candidates**, the project cannot close OULU content-lineage review based only on this screen.

The next checkpoint should adjudicate candidates with highest scientific risk first:

1. cross-role + conflicting-label;
2. cross-role;
3. cross-partition;
4. conflicting-label;
5. remaining same-role/same-partition candidates as needed.

Each pair should receive an explicit disposition such as:

- `confirmed_same_content_or_derived_lineage`;
- `rejected_false_positive`;
- `uncertain_insufficient_evidence`.

Adjudication must preserve private biometric evidence and publish only aggregate/bound lineage evidence.

## 13. Visual similarity alone is not capture-provenance proof

Even a highly similar pair may arise from:

- repeated acquisition conditions;
- common backgrounds;
- same subject/session but independent captures;
- repeated replay/display material;
- actual duplicated/re-encoded media.

Therefore confirmed *visual similarity* and confirmed *same original capture lineage* are not identical claims.

Any scientific remediation decision should distinguish those cases.

Document 111 correctly warns about this distinction.

## 14. Scientific gates remain correctly blocked

Current state remains:

- schema: pass;
- data-audit: blocked;
- source-dry-run: blocked;
- analysis-freeze: blocked;
- locked-evaluation: blocked;
- model execution unauthorized;
- scientific readiness false.

This is correct.

## Required next action

Proceed with bounded private adjudication of the 6,640 unresolved non-exact candidate pairs, prioritizing the 484 cross-role candidates.

Do not:

- automatically delete candidate videos;
- regenerate roles;
- retry split seed;
- change the primary selector;
- tune screening thresholds to erase candidate pairs.

If genuine cross-role shared-content lineage is confirmed, the project should stop and make an explicit prospective scientific decision about how that affects the frozen study design rather than silently repairing the split.

## Final disposition

**DOCUMENT 111 — ACCEPTED.**

**CHECKPOINT 1.5F OULU MODEL-FREE CONTENT CANDIDATE SCREENING — ACCEPTED WITHOUT REWORK.**

The screening computation is complete and reproducible.

**Near-duplicate/content-lineage adjudication remains pending; the 6,640 unresolved non-exact pairs, especially 484 cross-role candidates, must not be interpreted as either confirmed leakage or cleared content independence until adjudicated.**
