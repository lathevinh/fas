# Response to Document 49 - Track-A Metric Semantics

Date: 2026-09-18

## Decision

The review is accepted. Its required changes correct Track-A terminology,
reproducibility, and comparison scope. They do not alter the architecture, RQ1/RQ2,
novelty boundary, Track-B selective protocol, or four-table paper contract. The core
Q3 plan remains frozen.

## Required corrections

### 1. EER-style threshold name - accepted

The plan adopts Option A. The threshold previously named $\tau^A_{HTER}$ is now
$\tau^A_{EER}$ because it minimizes the absolute difference between macro-source APCER
and BPCER. Target HTER is reported at this transferred source EER-style threshold. The
plan does not claim to minimize target or source HTER under that name.

Ties are resolved deterministically by lower macro-source HTER and then lower numeric
threshold.

### 2. PAD-explicit 1% metric - accepted

Generic `TPR@FPR=1%` terminology is removed from the Track-A contract. Attack remains
the positive class, and the reported metric is explicitly
$APCER@BPCER\leq1\%$. This makes clear that the source-selected constraint concerns
bona-fide rejection rather than attack false acceptance. Track B remains authoritative
for security operating points.

### 3. Finite-sample applicability - accepted

The 1% point is estimable only if every contributing source domain has at least 100
detector-successful bona-fide validation videos. Otherwise it is reported as `not
estimable`; no nominal or interpolated 1% result is shown. Per-source APCER and BPCER at
each selected threshold are reported alongside the equal-domain macro criterion.

### 4. Detector-conditional population - accepted

The matching claim now applies to the intended pre-detection video membership,
selected frame indices, and video-aggregation rule. In-house classifier metrics are
conditioned on success of the frozen detector. Detector failures stay in the protocol
manifest, are never replaced, and are exposed through frame- and video-level coverage
by target and class.

Consequently, the in-house scored population is not called identical to SSDG unless
detector coverage is 100%. Track B remains unchanged: detector failures are terminal
non-accept transactions in end-to-end denominators.

### 5. Deterministic threshold candidates - accepted

For each outer fold and system, the candidate set is frozen as

$$
\mathcal T
=
\{-\infty\}
\cup
\{\text{unique finite Track-A validation scores}\}
\cup
\{+\infty\}.
$$

$\tau^A_{EER}$ and the lowest threshold satisfying macro-source
$BPCER\leq1\%$ are selected only from this set. All estimable thresholds transfer
unchanged to the held-out target. This rule is deterministic and directly unit-testable.

### 6. Shared source optimization - accepted

`track_a_validation` performs checkpoint selection, affine branch calibration, and
operating-threshold selection. The records are not reclaimed for refitting. The paper
calls this source optimization on one shared validation partition, not independent
validation or certified source performance. Outer-target evaluation remains the
observed generalization result.

## Comparison boundary

Published SSDG HTER remains marked target-aware through validation and thresholding;
published SSDG AUC remains marked target-aware through checkpoint selection. These
historical values provide literature context only and cannot support a controlled
superiority claim. Clean controlled comparisons are among in-house systems under the
same frozen Track-A source-only recipe.

Panel A and Panel B retain separate captions and populations. They are not pooled,
ranked, or jointly bolded. Track-A competitiveness is not an RQ1 prerequisite beyond
the separately frozen minimum base-classifier competence criterion, and Track A gains
no risk estimator, selective gate, or heterogeneity claim.

## Verification boundary

The metric semantics and deterministic selection rules are now complete in the
specification. Dataset-dependent event counts, detector coverage, and protected-list
reconciliation remain Phase-1 audit outputs and cannot be asserted before acquisition.

## Updated verdict

**DOCUMENT 49 IS ANSWERED; TRACK-A METRIC SEMANTICS ARE CLOSED AND THE CORE Q3 PLAN REMAINS FROZEN.**
