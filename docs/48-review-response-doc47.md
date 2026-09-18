# Response to Document 47 - Track-A Execution Details

Date: 2026-09-18

## Decision

The review is accepted. Its five required corrections expose execution gaps in Track A,
not defects in the architecture, RQ1/RQ2, novelty boundary, or Track-B protocol. Those
core contracts and the four-table paper structure remain frozen.

Track A remains literature context only. Track B remains the exclusive home of
Domain-OOF Failure Risk Estimation, selective evaluation, and both research questions.

## Required corrections

### 1. Lightweight Track-A validation split - accepted

Each Track-A dataset manifest now has two group-disjoint source roles:

```text
track_a_fit
track_a_validation
```

`track_a_fit` trains the DINO head. `track_a_validation` selects its checkpoint, fits
the positive-slope affine branch calibrators, and selects source operating thresholds.
The validation records are not reclaimed for refitting. Track A still has no
`gate_domain`, routing, OOF-risk, or selective-gate role.

This completes the execution recipe for DINOv2-Reg, OpenCLIP, calibrated heterogeneous
average, and the same-family classifier control without importing Track-B risk
infrastructure.

### 2. Published SSDG AUC wording - accepted

Published SSDG AUC is threshold-free at evaluation time, but it is not target-blind:
the reported checkpoint was selected using `tgt_valid_dataloader`. The manuscript and
Table-1 contract now label published SSDG AUC as historical target-aware context.
Published SSDG HTER additionally uses target-derived thresholding. In-house Track-A
results remain the strictly source-selected comparison.

### 3. Track-A detector failures - accepted

Pinned frames are never replaced after detector failure, and failures remain in the
protocol manifest. Panel-A classifier metrics use detector-success videos only and
report frame- and video-level detector coverage by target and class. This is an
explicit classifier-only analysis view, not a silent sample-universe change.

Track B is unchanged: every detector failure remains a terminal non-accept transaction
in end-to-end denominators.

### 4. Source-only HTER and TPR thresholds - accepted

For each system and outer fold, Track A uses the three sources' `track_a_validation`
records with equal source-domain weighting. It selects $\tau^A_{HTER}$ by minimizing
the absolute difference between macro-source APCER and BPCER, with deterministic ties
resolved by lower macro HTER and then lower numeric threshold.

With attack as the positive class, it selects $\tau^A_{1\%}$ as the lowest candidate
threshold satisfying macro-source
$FPR=P(score\geq\tau\mid bona\ fide)\leq1\%$, when the event count supports that
operating point. Both thresholds transfer unchanged to the target. Target ROC/AUC is
reported only as a conventional post-hoc, non-deployable diagnostic.

### 5. Narrow equivalence claim - accepted

The contract now uses the exact phrase
`sample-membership/frame-selection/video-aggregation equivalence`. Image preprocessing
and source-only model-selection rules are explicitly different from SSDG. Track A is
not called an SSDG reproduction or generally evaluation-equivalent.

## Additional recommendations retained

### Code provenance

The Phase-1 provenance record must store repository URL, commit SHA, source file path,
function name, and normalized code-block SHA-256 for the frame selector and video
aggregator. Branch names or prose formulas are insufficient.

### Separate panel interpretation

Table 1 uses separate captions for Panel A literature context and Panel B strict
single-image evaluation. Results are not pooled, ranked, or bolded across panels.
Published FLIP remains marked `+CelebA-Spoof` where applicable.

### Scientific priority

Track-A competitiveness is not a prerequisite for RQ1. Only the separately frozen
minimum base-classifier competence criterion applies. The two-engineer-day Track-A
stop rule remains active, and source validation is not reclaimed merely to improve a
comparison against target-aware published methods.

## Verification boundary

The Track-A execution contract is now internally complete. Exact protected-release
membership and the stored upstream code provenance remain Phase-1 audit outputs; they
cannot be claimed complete before dataset acquisition and artifact reconciliation.

## Updated verdict

**DOCUMENT 47 IS ANSWERED; TRACK A IS EXECUTABLE IN SPECIFICATION AND THE CORE Q3 PLAN REMAINS FROZEN.**
