# Response to Review 110: OULU Content Candidate Screening

Date: 2026-10-09
Base commit: `4487e95`
Review: [Document 110](110-review-doc109-transaction-selector-freeze.md)

Review 110 accepts checkpoint 1.5E without rework. This checkpoint 1.5F starts
the next OULU near-duplicate/content-lineage task with model-free candidate
screening. **Screening is complete; lineage adjudication is not complete.**
No other dataset, detector, model, training or target evaluation is executed.

## Prospective Screening Definition

[Screening policy](../configs/content_screening_v1.yaml) is recorded before the
real run. It is separate from, and does not change, the approved primary-frame
selector or study preprocessing. No threshold is tuned from observed candidates,
labels, roles, model scores or target outcomes.

For each accepted successfully decoded video, sample five fixed decode ranks:
`floor((n - 1) * j / 4)` for `j = 0..4`. The middle slot is the frozen lower-median
primary identity. Short videos repeat the prescribed slots rather than search for
replacements. OULU uses the whole supplied video, as already accepted.

Each sampled RGB payload must match the SHA-256 in the accepted full-decode index.
Using the existing OpenCV library, compute a 64-bit DCT perceptual fingerprint:
RGB-to-gray, INTER_AREA resize to 32x32, top-left 8x8 DCT, median of the 63 non-DC
coefficients, DC bit forced to zero. No learned model or face detector is involved.

Compare every unordered pair of successfully decoded videos, without filtering
by label, source role or official partition. A candidate has either:

- Hamming distance at most 4 for any of the 25 temporal-slot comparisons; or
- distance at most 8 for at least three of the five aligned slot comparisons.

These fixed thresholds are conservative screening heuristics, not scientifically
validated equivalence thresholds. A candidate is **not** a confirmed duplicate,
capture lineage link or leakage event. Sparse temporal sampling may miss crops,
overlays, large temporal shifts or other derived content; common scenes and
backgrounds may produce false positives. Non-candidates do not certify absence
of shared content or independent acquisition provenance.

## Completion Criteria

- Bind the accepted 4950-record media bundle, archive pins and all 13 frozen inputs.
- Reconcile sampled RGB identities against accepted evidence, retaining the failure.
- Compare all successful unordered pairs and preserve private candidate evidence.
- Reproduce candidate bytes from saved fingerprints and independently check distances.
- Reject existing/unsafe output without changing earlier evidence.
- Pass focused/full synthetic tests, publish aggregates and push for owner review.

[Fingerprint implementation](../src/fas/content.py) and
[runner](../scripts/screen_oulu_content.py) implement this bounded screening.
The runner reads pinned TARs with four workers, verifies each successful payload,
and keeps only sampled pixels in RAM. Temporary private AVIs are removed; no
frame bank or persistent frame pixels are created. The previously failed video is
not reopened, repaired or substituted. Its unavailable fingerprint is retained
in the original 4950-video coverage denominator.

## Actual Evidence

[Immutable public report](../results/phase1/oulu-content-screening-v1.json) binds
the private summary, fingerprint bundle, candidate chunk, policy, implementation,
review and frozen artifacts. Private evidence is outside Git under the existing
FAS-private artifact area; no individual identities, sampled RGB hashes, pHashes
or pair identities are published.

| Quantity | Observed |
|---|---:|
| Original video population | 4950 |
| Successfully fingerprinted videos | 4949 |
| Retained unavailable decode failure | 1 |
| Unordered successful-video pairs compared | 12243826 |
| Candidate pairs | 6653 |
| Previously known full-video exact pairs | 13 |
| Unresolved non-exact candidate pairs | 6640 |
| Cross-role unresolved candidate pairs | 484 |
| Cross-official-partition unresolved candidate pairs | 466 |
| Conflicting-label unresolved candidate pairs | 240 |

The final three counts are overlapping subsets, not additive. All 13 previously
known exact pairs are recovered. Exact pairs remain within a role and partition,
with no conflicting label. The 6640 other pairs have **no confirmed lineage
disposition** at this checkpoint. Cross-role candidates are a review priority,
not proof that the frozen assignment leaks. They must not trigger silent deletion,
role regeneration, selector changes or split/seed retries.

Independent verification confirms all 4950 record joins, all 4949 sampled RGB and
primary identities, scalar Hamming distances for all 6653 candidates, and scalar
classification for 5000 deterministically sampled arbitrary pairs. Repeating the
all-pairs computation with a different block size reproduces the exact candidate
bytes from saved fingerprints. This verifies comparison reproducibility, **not**
a second independent extraction of all fingerprints or validated screening recall.

The private output has 4953 immutable files: lineage, 4950 fingerprint records,
one candidate chunk and summary. Existing-output retry returns exit code 1 and
preserves every byte. All 13 frozen canonical/role artifacts and previous study,
selector, preprocessing and media-evidence hashes remain unchanged.

**36 focused / 223 full regression tests pass**, with zero failures/errors and no
editor diagnostics. Fixtures cover fixed ranks, brightness/re-encode sensitivity,
different-content rejection, cross-role pair inclusion, RGB mismatch rejection,
failed-video coverage, duplicate identities and private-output refusal. CI now
explicitly installs NumPy 1.26.4 and OpenCV-headless 4.11.0.86 for synthetic tests;
the existing research `fas` environment is unchanged.

## Remaining Boundary

Schema passes. Data-audit, source-dry-run, analysis-freeze and locked-evaluation
remain blocked; scientific readiness and model execution authorization remain
false. No claim of completed OULU near-duplicate/content-lineage audit is made.

The next bounded OULU task is candidate adjudication, prioritizing cross-role,
cross-partition and conflicting-label pairs, with private content evidence and
explicit confirmed/rejected/uncertain dispositions. Visual similarity alone does
not certify original capture provenance. Any confirmed overlap needs a prospective
documented scientific decision under the frozen-study constraints, not automatic
repair of this split. Threshold adjustment, if ever justified, must be separately
versioned with v1 evidence preserved, never optimized to erase inconvenient pairs.

Equivalent media audits for CASIA-FASD, MSU-MFSD and SiW-Mv2, cross-dataset checks,
and eventual core data-audit closure remain later checkpoints. Stop here for owner
review after publication; do not advance to another dataset or model execution.