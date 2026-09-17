# Response to ChatGPT Review (Round 4)

Date: 2026-09-17

## Verdict

The review correctly identifies that the remaining threats are primarily protocol
and estimand validity rather than architecture. The architecture remains frozen.

## Accepted

1. RQ2 now targets prediction failure under unseen shifts. Unknownness/OOD is a
   distinct optional estimand and cannot share an error-risk claim by default.
2. Oracle headroom is class-conditional: oracle APCER, BPCER, and ACER replace
   prevalence-sensitive oracle accuracy as the primary biometric quantities.
3. Complementarity may be asymmetric. REF and false-accept rescue rate are more
   operational than requiring both recovery directions to be equally large.
4. Single-image and benchmark-compatible video tracks are separated; bootstrap and
   significance units are video/subject rather than correlated frames.
5. Frozen source-threshold deployment results are separated from target-posthoc ROC
   diagnostics, with pooled-source and worst-source threshold policies compared.
6. Failure labels use a preregistered reference security policy rather than an
   unstated EER threshold.
7. Capacity-matched probability, JS, image-quality, and nonlinear risk baselines are
   required because JS/entropy are deterministic probability transforms.
8. Conditional inference is claimed as a security-coverage-compute trade-off. Mean,
   P50, and P95 latency still expose slower sequential escalation on hard cases.
9. Prompt exclusion follows family/instrument/subtype hierarchy; open-vocabulary
   similarities are auxiliary and do not change the fixed PAD probability geometry.

## Accepted with qualification

### Representation-space confidence

DINO embedding Mahalanobis confidence is added as a stronger simple baseline. It is
not described as a reproduction of confidence-aware FAS: it lacks that method's full
training objective and protocol. A published method should be reproduced separately
when code, data assumptions, and compute permit a fair comparison.

### Quantitative Stage 1 kill criteria

REF and FARR must have numeric continuation thresholds, but choosing them after target
inspection would create the same researcher degrees of freedom the review seeks to
remove. Thresholds will be selected and signed from domain-OOF source pseudo-shifts
after Stage 0, before any MICO target labels are opened. Target results can test but
cannot redefine those criteria.

## Rejected or deferred

No central correction is rejected. Policy-specific risk models for every APCER target
are deferred because a single preregistered reference-policy model is simpler and
matches version 1. Transfer across nearby operating policies will be reported as an
ablation; policy-specific models are only justified if transfer fails.

## Implementation decision

Stage 1 begins without a risk calibrator. Stage 2 proceeds only if source-preregistered
class-conditional oracle, REF, and FARR criteria pass on untouched target evaluation.