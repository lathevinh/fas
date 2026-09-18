# Response to Document 43 - Implementation Plan Corrections

Date: 2026-09-18

## Decision

The review is accepted. It identifies protocol ambiguities rather than an architecture
or novelty failure. Document 42 is corrected before Phase 0 coding; the method,
backbones, two core RQs, and primary RQ1 estimand remain unchanged.

## Must-fix responses

### 1. Global immutable source roles - accepted

Each dataset now receives exactly one source-role manifest. Assignment depends on the
dataset release, source-eligible partition, role policy, and one split seed, never on
outer target or optimization seed. An outer fold only selects which three global
manifests are visible. If one dataset is infeasible, the policy is revised globally
before any outer-target result.

### 2. Fold-local target exclusion - accepted

Absolute label-sealing language is removed. In leave-one-domain-out MICO, a dataset is
naturally labeled when it serves as a source elsewhere. The enforceable claim is that
for outer target $T$, no $T$ sample, label, statistic, or result influences fitting,
calibration, thresholding, risk training, or global method choices for that fold.
Namespace isolation is optional hardening, not scientific proof.

### 3. Exact literature protocol - accepted with a Phase-1 hash gate

Track A pins the official SSDG implementation at commit
`c268920a7408ca78fb425954de2bf5745d1c660a` for the strict three-source MCIO sample
universe. It also pins the official FLIP implementation at commit
`4f95def259e135a0cbaff1d770f559ca739c4c9f` as a derivative list/preprocessing
cross-check. SSDG uses frame 6 for source training and frame 6 plus
$6+\lfloor N/2\rfloor$ for target video evaluation.

Phase 1 must copy FLIP's 16 list artifacts into the private audit, record upstream Git
blob and local SHA-256 hashes, and reconcile counts/labels against obtained dataset
releases. This is intentionally a hash gate: protected datasets have not yet been
downloaded, so exact local equivalence cannot honestly be claimed today.

Track A is Panel A of the visible main classifier-comparison table. Track B is Panel B
and remains the strict single-image selective protocol containing RQ1/RQ2. The two
tracks never share a headline number or imply an identical sample universe. FLIP's
published Benchmark-1 configuration includes CelebA-Spoof, so its numbers are labeled
extra-data and are not treated as equal-data strict-MICO comparisons.

### 4. Reference threshold partition - Option C accepted

The source `branch_calibration` partition fits the positive-slope affine calibrators
and selects $\tau_{ref}$. This avoids another statistically weak split, especially for
MSU-MFSD. The threshold is explicitly called source-optimized, not independently
validated or certified. Low-APCER claims remain empirical and event-count limited.

### 5. K=1 gate action - accepted

The operational gate is now an explicit predicted-live filter. Predicted spoof is
already terminal non-accept. Only predicted-live transactions are either accepted or
converted to abstain/non-accept according to risk threshold $u$. Risk ranking still
uses all fixed-classifier errors.

### 6. Target-level bootstrap - accepted

Each bootstrap replicate resamples clusters independently inside each target,
computes target-specific paired effects, and then takes the equal-weight four-target
macro. Datasets and seeds are not pooled as independent samples.

## Strong recommendations

### 7. Visible benchmark track - accepted

The literature-compatible Track A is promoted to a visible main classifier table.
It establishes external comparability; it does not test the Domain-OOF risk claim.

### 8. Security-specific support - accepted

`AP_error` remains the methodological RQ1 endpoint. False-accept ranking on the
preregistered attack/predicted-live population is reported when event counts permit,
and `FA_end2end` versus `BFNR_end2end` remains the deployment evidence. An AP gain
driven by false rejects cannot be described as a security improvement.

### 9. Quality normalization - accepted

OOF quality features use statistics from each fold's allowed fitting remainder;
target inference uses final source-fit statistics. An unstandardized-quality
sensitivity is required for physically defined or bounded features.

### 10. Double balancing - accepted

The primary DINO objective retains equal-domain, class-balanced BCE. Sampling balances
dataset exposure and then video/frame exposure, but does not force class or attack-
family balance a second time.

### 11. Comparator taxonomy - accepted

MSP, entropy, operational margin, and absolute disagreement are non-learned scores;
Mahalanobis is a source-statistic baseline; logistic and MLP models are learned risk
estimators. The plan no longer says all are fitted.

### 12. One global analysis-rule freeze - accepted

All analysis-rule generation code and selection logic freeze before the first
outer-target result. Numeric source thresholds may differ by fold only because the
same frozen algorithm receives different permitted source domains. Older normative
wording is synchronized.

## Clarifications retained

- The same-family conclusion remains limited to the studied DINOv2-Reg/plain-DINOv2
  control; no universal heterogeneous-versus-homogeneous claim is made.
- Training may use multiple images per source video while inference remains
  single-image.
- Detector failures remain terminal non-accept transactions in end-to-end
  denominators and stay outside risk-feature metrics.
- The common candidate-ID ledger and budget sensitivity remain mandatory for RQ1.
- Document 42 remains an internal reproducibility blueprint, not the manuscript
  Method section.

## Infrastructure simplification

Mandatory controls are immutable manifests/configs, Git/code hashes, fold-local
exclusion assertions, source-only thresholds, and no method changes after results.
Cryptographic signing, a separate label-release service, and OS-level namespaces are
optional. This preserves scientific integrity without making governance the dominant
engineering task.

## Updated verdict

**DOCUMENT 42 IS CORRECTED AND READY TO GOVERN PHASE 0.**

Phase 1 still has one explicit completion gate: verify downloaded releases against the
pinned Track-A list artifacts and commit only non-sensitive list hashes/counts before
dataset-facing training begins.