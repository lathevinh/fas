# Response to Review 112: OULU Full-Frame Exact Evidence Slice

Date: 2026-10-09
Base commit: `1af05e4`
Review: [Document 112](112-review-doc111-oulu-content-screening.md)

Review 112 accepts checkpoint 1.5F for screening only and requires adjudication
of 6640 unresolved non-exact candidates, prioritizing the 484 cross-role pairs.
This checkpoint 1.5G performs a bounded **full-frame exact-evidence pass** for
every unresolved pair. It does **not** complete the required visual/re-encoded
content adjudication or certify content independence.

## Scope and Definition

[Prospective evidence policy](../configs/content_adjudication_v1.yaml),
[exact-content implementation](../src/fas/lineage.py) and
[private export runner](../scripts/triage_oulu_lineage.py) implement this slice.
No new pHash decision threshold is introduced. The accepted screening policy and
candidate bytes remain unchanged.

Use the entire accepted decoded index, not just the five screening samples.
A frame token is its width, height and decoded RGB SHA-256. Compare tokens across
each pair and compute the longest exactly equal contiguous ordered subsequence,
including start positions and repeated-frame handling.

Only a complete shorter sequence contained in the other sequence, with at least
two distinct RGB tokens, supports `confirmed_same_content_or_derived_lineage`
in this exact-evidence pass. Its scope is **same rendered decoded content**, not
proof of the original capture, release provenance or acquisition lineage.
An isolated/shared/static frame or incomplete overlap is not sufficient for that
disposition. This rule is recorded before the pass; no pair satisfies it here.

If exact evidence is insufficient, record `uncertain_insufficient_evidence`.
Never infer `rejected_false_positive` from no exact matches: re-encoding, crops,
overlays and transformations may change every decoded RGB hash. pHash distances,
different IDs, labels, subjects, roles or partitions cannot clear that uncertainty.
No visual review is claimed at this checkpoint.

## Completion Criteria

- Verify the accepted candidate chunks, full media record bundle and 13 frozen inputs.
- Examine exactly all 6640 unresolved pairs in Review 112's priority order.
- Bind each private disposition to both accepted media records and boundary metadata.
- Preserve the 13 known exact pairs separately and retain the failed-video denominator.
- Reproduce every export byte, independently verify exact evidence and reject overwrite.
- Pass focused/full tests, publish aggregate evidence and push for owner review.

## Actual Evidence

The [immutable aggregate report](../results/phase1/oulu-lineage-exact-evidence-v1.json)
binds Review 112, policy, code, accepted media/screening reports, frozen artifacts,
private summary and pair-record bundle. No pair identities, frame hashes, start
positions or biometric pixels are published.

All 6640 non-exact pairs were processed in the following **exclusive** order:

| Priority | Pair population | Processed |
|---|---|---:|
| 1 | Cross-role and conflicting-label | 85 |
| 2 | Remaining cross-role | 399 |
| 3 | Remaining cross-partition | 185 |
| 4 | Remaining conflicting-label | 91 |
| 5 | Remaining candidates | 5880 |
| Total | All unresolved non-exact pairs | 6640 |

These exclusive queue populations differ from the overlapping screening counts
484 cross-role, 466 cross-partition and 240 conflicting-label pairs. No boundary
is filtered out. Native metadata flags are rechecked against accepted media rows.

Observed dispositions:

| Disposition/evidence | Pairs |
|---|---:|
| Confirmed same rendered content by the exact-sequence rule | 0 |
| Rejected false positive | 0 |
| Uncertain, insufficient evidence | 6640 |
| Any shared dimension-and-RGB-hash token | 0 |

Thus this pass finds no exact decoded frame shared by any of the 6640 non-exact
candidate pairs. This is a narrow byte-identity result, **not** a near-duplicate
negative result, a recall estimate, zero leakage, or content-lineage clearance.
The 13 previously known full-video exact pairs remain accepted separately.

Original and rerun outputs each contain **6642 byte-identical files**: lineage,
6640 per-pair evidence records and summary. Independent verification checks every
pair against its accepted candidate and both full-frame records, every exact RGB
token intersection, the priority order and export hashes. Additionally, 500 seeded
synthetic sequence comparisons agree with an independent brute-force longest-run
implementation. Existing-output retry returns exit code 1 and preserves all bytes.

**42 focused / 229 full regression tests pass**, with zero failures/errors and no
editor diagnostics. Fixtures cover complete trimmed sequences, repeated/static
frames, reversed/partial/no overlap, invalid indexes/digests/dimensions, exclusive
priorities and private-output refusal. No dependency or environment is changed.

All 13 frozen canonical/role artifacts, prior study/preprocessing/transaction
definitions, selector, screening implementation/policy and earlier evidence bytes
remain unchanged. The original OULU denominator stays 4950 with the one retained
decode failure. No AVI is reopened/redecoded/repaired, no image is exported, and
no detector, model, embedding, score, training or target evaluation is run.

## Unresolved Requirement and Resume Boundary

**Review 112's required content adjudication remains pending.** Assigning an
explicit uncertain evidence disposition is not resolving the relationship.
Neither the 484 cross-role candidates nor the other candidates are cleared.

The limitation is evidential, not missing dataset access, permission or receipt
paperwork. Accepted exact hashes cannot decide whether visually similar but
byte-different videos are re-encodes/derived content or independent captures.
Threshold tuning to make these candidates disappear would not solve that problem.

After review of this bounded slice, the next checkpoint should inspect stronger
private content evidence from the supplied media, starting with the 85 cross-role
and conflicting-label pairs, followed by the 399 other cross-role pairs. Bind any
new visual/full-content observation to pinned payloads and accepted frame identities.
Resolution requires evidence-backed confirmed/rejected dispositions; genuinely
ambiguous relationships must remain uncertain rather than being forced to close
the gate. No original-capture provenance certification follows from visual similarity.

If cross-role shared content is confirmed, stop for an explicit prospective
scientific decision about the frozen study. Never delete candidates, reassign roles,
retry the split seed, change the primary selector or retrospectively optimize the
screening rule. Keep v1 screening and this evidence slice immutable.

Schema passes; data-audit, source-dry-run, analysis-freeze and locked-evaluation
remain blocked. Model execution authorization and scientific readiness remain false.
Stop for owner checkpoint review after publication; do not advance to another dataset.