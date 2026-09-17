# ChatGPT Research Review — Round 5

Date: 2026-09-17

This review evaluates the latest repository state after `15-review-response-round4.md`, with emphasis on:

- risk-target semantics;
- selective-action semantics;
- meta-validation leakage;
- selective PAD denominators;
- retry/transaction threat modeling;
- pilot versus confirmatory evaluation;
- statistical validity.

## Overall assessment

The repository is now mature enough to begin Stage 1.

The core architecture should remain frozen.

The remaining issues are primarily methodological rather than architectural. They should be resolved before Stage 2 so that the failure-risk calibrator and selective deployment claims are fully well-defined.

---

# 1. Some stale text still contradicts the latest decisions

Round 4 correctly concluded that:

- oracle analysis should be class-conditional;
- complementarity may be asymmetric;
- REF and false-accept rescue are more operational than symmetric recovery.

However, parts of `03-method.md` still describe:

\[
\text{oracle accuracy}=1-P_{ww}
\]

and emphasize two-sided recovery rates as if they were central continuation criteria.

Likewise, `06-risks-and-decisions.md` still includes language requiring two-sided recovery.

These should be synchronized with the newer design.

Recommended replacement:

- class-conditional oracle APCER;
- class-conditional oracle BPCER;
- oracle ACER;
- DINO-error recoverable fraction;
- DINO false-accept rescue rate.

If DINO is the intended primary deployed predictor, recovery from DINO failures is more operational than symmetric branch recovery.

---

# 2. The risk target and the selective-gate action space are currently mismatched

The current method trains a scalar failure-risk score:

\[
r_{\text{err}}(x)
=
P(\hat y\neq y\mid z(x),\tau_{\text{ref}}).
\]

This is a valid selective-classification target.

However, the selective gate is described as being able to:

- fuse;
- accept one branch;
- retry/abstain.

A scalar failure probability does not identify which branch or fusion rule should be chosen.

For example:

\[
r_{\text{err}}(x)=0.4
\]

does not tell the system whether:

- DINO is safer;
- VLM is safer;
- calibrated averaging is safer.

That would require action-specific risks such as:

\[
r_D(x),
\qquad
r_V(x),
\qquad
r_F(x),
\]

or a learned mixture-of-experts policy.

That is unnecessary complexity for version 1.

## Recommendation

Define a fixed post-VLM decision function:

\[
g_{\text{ref}}(x)
\]

for example calibrated averaging or the best source-selected fusion baseline.

Then train:

\[
r_{\text{err}}(x)
=
P(
g_{\text{ref}}(x)\neq y
\mid
z(x)
).
\]

The selective stage then has only two actions:

\[
\boxed{
\text{accept }g_{\text{ref}}
\quad\text{or}\quad
\text{abstain/retry}
}
\]

The pre-VLM routing gate remains separate.

This keeps the paper a selective-prediction paper rather than unintentionally turning it into a mixture-of-experts paper.

---

# 3. Domain-OOF still needs meta-level model-selection protection

The current domain-OOF design creates held-out source-domain records and concatenates them to train the reliability model.

This is good.

However, the following risk-model choices may still require selection:

- regularization strength;
- feature subset;
- logistic versus MLP;
- hidden size;
- image-quality feature set;
- selective-risk threshold.

If these choices are selected on the same concatenated OOF records used to train the final risk model, the pipeline still has a meta-level fit/select leakage.

## Option A — nested pseudo-domain validation

For source domains \(A,B,C\), rotate:

\[
A+B
\rightarrow
\text{risk training},
\qquad
C
\rightarrow
\text{risk validation}.
\]

Use these pseudo-domain validation results to select risk-model hyperparameters.

Then refit the chosen model on all available OOF source records.

## Option B — fixed low-capacity gate

For version 1, an even cleaner option is to preregister:

\[
\boxed{
\text{logistic regression + fixed regularization}
}
\]

and avoid meta-tuning entirely.

This may be preferable if the main contribution is the cross-foundation signal rather than the sophistication of the risk model.

---

# 4. OOF feature distributions may encode fold/domain identity

Domain-OOF records come from different predictors.

For example:

\[
B+C\rightarrow A,
\]

\[
A+C\rightarrow B,
\]

\[
A+B\rightarrow C.
\]

Even after probability calibration, auxiliary features such as:

- energy scores;
- Mahalanobis distances;
- image-quality features;
- embedding-derived scores;

may have different scales across folds.

If concatenated directly, the gate may learn:

\[
\text{which OOF domain produced the record}
\]

instead of:

\[
\text{whether this prediction is likely to fail}.
\]

## Recommendation

Normalize each feature using statistics obtained only from the corresponding source-side fitting/calibration portion:

\[
z'_j
=
\frac{
z_j-\mu_{j,\text{source}}
}{
\sigma_{j,\text{source}}
}.
\]

Then concatenate normalized OOF records.

Also run a diagnostic:

> Can a simple classifier predict the OOF fold/domain from the risk features?

If fold/domain classification accuracy is very high, the risk representation contains strong domain shortcuts.

This should be reported or at least audited.

---

# 5. FARR can be statistically unstable at low APCER

The false-accept rescue rate is:

\[
FARR
=
\frac{
N_{\text{DINO false accepts corrected by VLM}}
}{
N_{\text{DINO false accepts}}
}.
\]

This is highly interpretable.

But at a low-security operating point, the denominator may be tiny.

Example:

\[
N_{\text{FA}}=4,
\]

\[
N_{\text{rescued}}=2.
\]

Then:

\[
FARR=50\%
\]

but the estimate is extremely uncertain.

## Recommendation

Preregister both:

\[
N_{\text{FA}}\ge N_{\min}
\]

and a confidence-bound requirement.

A stronger continuation criterion is:

\[
LCB_{95\%}(FARR)>\gamma.
\]

If low-APCER source pseudo-shifts do not provide enough false-accept events, use a higher Stage-1 diagnostic operating point for complementarity estimation, while keeping low-APCER points for final deployment evaluation.

Do not use a high FARR point estimate from only a handful of events as a Stage-1 success signal.

---

# 6. Selective PAD metrics need explicit denominators

Once the system can output:

\[
\text{retry/abstain},
\]

standard PAD error rates become ambiguous if computed only on covered samples.

A system could appear to achieve near-zero APCER by abstaining on nearly every attack.

Therefore report attack and bona-fide coverage separately:

\[
Coverage_A
=
\frac{
N_{\text{attack decided}}
}{
N_{\text{attack total}}
},
\]

\[
Coverage_B
=
\frac{
N_{\text{bona-fide decided}}
}{
N_{\text{bona-fide total}}
}.
\]

Also distinguish:

## Conditional error on covered samples

For example:

\[
APCER_{\text{covered}}
=
\frac{
N_{\text{attacks accepted live}}
}{
N_{\text{attacks decided}}
}.
\]

## End-to-end attack acceptance

\[
FA_{\text{end2end}}
=
\frac{
N_{\text{attacks accepted live}}
}{
N_{\text{all attacks}}
}.
\]

Do not label every selective error number simply as `APCER` if the denominator has changed.

The manuscript should define the estimand explicitly.

---

# 7. Retry creates a transaction-level threat model

If a rejected or abstained user is allowed to retry, the system is no longer purely per-image.

If an attacker has per-attempt success probability:

\[
p,
\]

and is allowed \(K\) attempts, then:

\[
P(\text{at least one successful attack})
=
1-(1-p)^K.
\]

Therefore the deployment protocol must specify:

- maximum retry count;
- whether retries belong to one authentication transaction;
- whether rate limiting exists;
- whether scores are independent across retries;
- whether final security metrics are per-image or per-transaction.

This is no longer an optional documentation detail because `retry` is part of the proposed output space.

A practical first-paper policy could simply state:

\[
K=1
\]

for experimental evaluation, while discussing multi-attempt transaction security separately.

---

# 8. The routing gate should be security-asymmetric

The current routing logic broadly says:

> confident DINO prediction may be accepted; uncertain DINO prediction invokes the VLM.

But a confident:

\[
\text{SPOOF}
\]

prediction and a confident:

\[
\text{LIVE}
\]

prediction do not have equal security consequences.

A more practical policy is:

```text
DINO confidently SPOOF
    -> reject directly

DINO says LIVE with only moderate confidence
    -> invoke VLM

DINO uncertain
    -> invoke VLM

DINO extremely confident LIVE
    -> accept only under a stricter source-selected threshold
```

This can reduce VLM compute mainly on obvious spoofs while protecting the security-critical LIVE path.

This is a policy ablation, not a new architecture.

Recommended comparison:

1. symmetric confidence routing;
2. security-asymmetric routing.

---

# 9. Source-tuned prompts may weaken unseen semantic transfer

The VLM currently allows prompt-template selection and temperature calibration using source validation data.

This is reasonable for cross-domain performance.

However, strict MICO sources are dominated by known attack families such as print and replay.

If prompt weights or template selection are strongly optimized for these source families, concepts related to unseen attacks such as masks may be implicitly downweighted.

Therefore compare:

## Fixed semantic VLM

\[
V_{\text{fixed}}
\]

using a preregistered semantic prompt bank selected before target evaluation.

## Source-tuned semantic VLM

\[
V_{\text{tuned}}
\]

using source-only prompt/template selection.

This comparison will reveal whether source tuning improves known-domain accuracy at the expense of unseen semantic transfer.

For the strongest unseen-attack claim, the fixed-prompt branch is important.

---

# 10. The first MICO target cannot remain fully "untouched" if it is used as a pilot

Stage 1 currently proposes running one MICO target first and then deciding whether the project continues.

If the research team sees that target result and subsequently changes:

- prompt choices;
- thresholds;
- architecture;
- calibration;
- kill criteria;
- preprocessing;

then that target has become a development target.

It should not later be described as one of four untouched confirmatory targets.

Two clean strategies exist.

## Strategy A — all targets confirmatory

Freeze the complete Stage-1 configuration and run all four MICO targets once.

## Strategy B — explicit pilot target

Choose one target in advance as:

\[
\text{pilot/development target}.
\]

Use it for pipeline debugging and early diagnosis.

Then treat the remaining three as confirmatory targets.

Either strategy is valid, but the role of the first target must be explicit.

---

# 11. Stage 2 needs a preregistered primary endpoint

Stage 2 currently reports many metrics:

- error AUROC;
- error AUPR;
- risk-coverage;
- APCER/BPCER;
- selective risk;
- security operating points.

This is useful descriptively, but without a primary endpoint the final paper may appear to select whichever metric looks best.

Recommended primary failure-detection metric:

\[
\boxed{
\text{prediction-error AUPR}
}
\]

because prediction errors may be relatively rare and AUPR is sensitive to class imbalance.

Recommended primary selective-classification metric:

\[
\boxed{
AURC
}
\]

or preferably:

\[
\boxed{
\text{Excess-AURC}
}
\]

if implemented correctly.

All other metrics can remain secondary.

The primary endpoint should be specified before target evaluation.

---

# 12. Three random seeds are not three independent scientific replicates

Reporting:

\[
\text{mean}\pm\text{std over 3 seeds}
\]

is useful for optimization stability.

But the three seeds should not be treated as \(n=3\) independent scientific replicates for hypothesis tests.

The primary uncertainty should come from:

- paired bootstrap by subject/video;
- per-target-domain results;
- macro aggregation across target domains.

Seed variance should be reported separately as implementation variance.

If the manuscript claims consistent improvement, the strongest evidence is:

\[
\Delta_d>0
\]

across multiple independent target domains, not merely a pooled frame-level improvement.

---

# 13. Confidence-aware FAS should remain an important final baseline

The repository correctly distinguishes:

\[
\text{Mahalanobis on DINO embedding}
\]

from a full reproduction of confidence-aware FAS.

This distinction is necessary.

A simple Mahalanobis baseline is useful, but it does not reproduce a dedicated reliability-aware FAS method that jointly optimizes its representation and confidence structure.

If an official or sufficiently reproducible implementation is available, the final paper should attempt a fair comparison against a dedicated confidence-aware FAS baseline.

Otherwise explicitly state why full reproduction was not feasible and avoid implying that the simple Mahalanobis baseline represents the entire prior method.

---

# 14. Recommended final Stage-2 formulation

The cleanest pipeline is:

```text
RGB image
   |
DINO
   |
routing policy
   |
   +------ if escalated ------> VLM
                                |
                      fixed fusion g_ref
                                |
                       risk estimator r_err
                                |
                     accept / abstain-retry
```

The post-VLM decision rule is fixed:

\[
g_{\text{ref}}(x).
\]

The risk target is then unambiguous:

\[
\boxed{
r_{\text{err}}(x)
=
P(
g_{\text{ref}}(x)\neq y
\mid
z(x)
)
}
\]

The risk score does **not** choose among DINO/VLM/fusion.

It only determines:

\[
\boxed{
\text{accept}
\quad\text{vs}\quad
\text{abstain/retry}
}
\]

This is the cleanest version for a first selective-PAD paper.

---

# Final recommendation

The repository is ready for Stage 1.

No additional architecture should be added before real data are collected.

Before Stage 2, lock the following:

1. synchronize stale oracle/complementarity text across all documents;
2. define a fixed post-VLM decision rule \(g_{\text{ref}}\);
3. make the risk gate accept/abstain rather than choose among experts;
4. define nested or fixed risk-model hyperparameter selection;
5. normalize OOF features and audit domain-identifiability;
6. require sufficient false-accept event counts and confidence intervals for FARR;
7. define selective PAD denominators and transaction/retry policy;
8. compare symmetric and security-asymmetric routing;
9. compare fixed versus source-tuned prompt banks;
10. explicitly designate pilot versus confirmatory MICO targets;
11. preregister Stage-2 primary metrics;
12. use video/subject bootstrap and domain-level consistency for inference.

Stage 1 should remain simple:

- DINO;
- VLM;
- independent calibration;
- calibrated averaging;
- joint correctness;
- class-conditional oracle headroom;
- REF;
- FARR.

If Stage 1 does not demonstrate meaningful and statistically supported recoverable DINO errors, especially false-accept rescue, stop the dual-foundation direction before building the risk calibrator.
