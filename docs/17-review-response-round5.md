# Response to ChatGPT Review (Round 5)

Date: 2026-09-17

## Verdict

The review finds real remaining inconsistencies and correctly narrows version 1 to a
fixed decision rule plus selective abstention. No architecture change is accepted.

## Accepted

1. Stale oracle and symmetric-recovery claims are replaced by class-conditional
   oracle APCER/BPCER/ACER, REF, and false-accept rescue.
2. The post-VLM rule $g_{ref}$ is fixed from source data. Scalar failure risk chooses
   only accept versus abstain; it does not select an expert or fusion action.
3. Fixed-regularization logistic regression is the primary gate to avoid meta-level
   model-selection leakage. Nested pseudo-domain tuning is secondary.
4. FARR continuation requires a preregistered minimum false-accept count and a 95%
   lower confidence bound, not only a point estimate.
5. Selective PAD reports class-specific coverage, covered-sample error, and end-to-end
   false acceptance with explicit denominators.
6. Version 1 uses one image attempt per authentication transaction ($K=1$). Any retry
   study must define attempts, rate limiting, dependence, and transaction success.
7. Symmetric and security-asymmetric routing are compared without adding a model.
8. Fixed semantic prompts are primary for unseen transfer; source-tuned prompts are a
   sensitivity ablation.
9. One preregistered MICO target is explicitly pilot/development; the remaining three
   become confirmatory only after configuration freeze.
10. Prediction-error AUPR and excess-AURC are the Stage 2 primary endpoints.
11. Subject/video bootstrap and cross-domain consistency provide scientific
    uncertainty; seed variance only measures optimization stability.
12. A dedicated confidence-aware FAS reproduction remains desirable and Mahalanobis
    is not presented as its replacement.

## Accepted with qualification

### OOF domain identity

OOF features are normalized with source-side statistics and domain identifiability is
audited. However, high domain-classification accuracy is not by itself proof of
leakage: a legitimate shift-sensitive feature may identify both domain and failure
risk. The response is an ablation across feature subsets and normalization choices,
not automatic removal of every domain-predictive feature.

### Risk-model selection

Nested pseudo-domain validation is statistically fragile with only three source
domains. The primary result therefore uses a preregistered low-capacity logistic gate;
nested selection is reported only as sensitivity analysis rather than treated as a
more reliable default.

## Implementation decision

Stage 1 remains DINO, fixed-prompt VLM, independent calibration, calibrated fusion,
joint correctness, class-conditional oracle headroom, REF, and confidence-bounded
FARR. Stage 2 starts only after the frozen confirmatory protocol passes the
source-preregistered continuation criteria.