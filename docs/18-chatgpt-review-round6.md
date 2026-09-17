# ChatGPT Research Review — Round 6

Date: 2026-09-17

This review evaluates the repository after `17-review-response-round5.md`, especially the revised:

- `03-method.md`
- `04-data-and-protocols.md`
- `05-experiment-plan.md`
- `06-risks-and-decisions.md`

## Overall assessment

Round 5 was incorporated well.

The repository now has a coherent version-1 architecture:

\[
\text{DINO}
\rightarrow
\text{routing}
\rightarrow
\text{optional VLM}
\rightarrow
g_{\text{ref}}
\rightarrow
r_{\text{err}}
\rightarrow
\text{accept/abstain}.
\]

The risk estimator no longer chooses among experts, failure risk is separated from unknownness, selective denominators are explicit, and pilot/confirmatory targets are distinguished.

The remaining issues are now mostly about **identifiability and evaluation fairness**.

The two most important new points are:

1. risk estimators must be compared while holding the base decision rule fixed;
2. the accept/abstain threshold itself needs out-of-sample source-only selection after the risk model is fitted.

---

# 1. Risk-estimator comparisons must use the same base prediction rule

Stage 2 compares:

- DINO uncertainty;
- MSP;
- entropy;
- energy;
- Mahalanobis;
- calibrated JS;
- learned failure risk.

However, prediction-error AUPR and AURC depend on **which classifier generated the errors**.

Suppose:

\[
g_D(x)=\text{DINO decision}
\]

has 10% error, while:

\[
g_{\text{ref}}(x)=\text{calibrated fusion}
\]

has 5% error.

Then comparing:

\[
\text{DINO entropy on errors of }g_D
\]

against:

\[
r_{\text{err}}\text{ on errors of }g_{\text{ref}}
\]

does not isolate the quality of the uncertainty estimator.

The positive class in the two AUPR calculations is different.

## Recommendation

Separate two levels of evaluation.

### Risk-estimator comparison

Fix:

\[
g_{\text{ref}}
\]

for every compared risk score.

Define the shared target:

\[
e(x)
=
\mathbf 1[g_{\text{ref}}(x)\neq y].
\]

Then compare all risk scores against the **same error labels**:

\[
s_{\text{MSP}}(x),
\]

\[
s_{\text{entropy}}(x),
\]

\[
s_{\text{JS}}(x),
\]

\[
s_{\text{Mahalanobis}}(x),
\]

\[
r_{\text{err}}(x).
\]

If MSP/entropy are needed for a fused classifier, compute them from the fixed fused probability or define a clear source-only fusion uncertainty baseline.

### System comparison

Separately compare:

\[
\text{DINO-only selective system}
\]

versus:

\[
\text{dual-foundation selective system}.
\]

This second table is allowed to change both prediction accuracy and risk estimation.

Do not use the system-level comparison as evidence that the risk estimator itself is better.

---

# 2. Prediction-error AUPR is prevalence-sensitive

Prediction errors may have very different prevalence across:

- target domains;
- classifiers;
- operating points.

The random AUPR baseline is:

\[
\pi_{\text{err}}
=
P(e=1).
\]

Therefore:

\[
AUPR=0.30
\]

means something very different when:

\[
\pi_{\text{err}}=0.05
\]

than when:

\[
\pi_{\text{err}}=0.25.
\]

## Recommendation

Always report:

\[
\pi_{\text{err}},
\]

raw error AUPR, and optionally a prevalence-normalized score such as:

\[
AUPR_{\text{norm}}
=
\frac{
AUPR-\pi_{\text{err}}
}{
1-\pi_{\text{err}}
}.
\]

The primary inference should use **paired within-target differences** because the competing risk scores then face exactly the same error prevalence.

Macro-average the per-target deltas rather than pooling all frames from all domains.

---

# 3. The accept/abstain risk threshold also requires honest source-only selection

The repository correctly uses OOF records to fit:

\[
r_{\text{err}}.
\]

But after fitting the logistic gate, the system still needs a threshold:

\[
\rho
\]

such that:

\[
r_{\text{err}}(x)\le\rho
\Rightarrow
\text{accept}.
\]

If \(\rho\) is selected by evaluating the logistic model on the same OOF records used to fit it, the final selective operating point is optimistic.

Fixed regularization removes hyperparameter-selection leakage, but it does **not** solve decision-threshold leakage.

## Recommendation

Generate meta-OOF risk predictions.

For the three OOF source domains \(A,B,C\):

\[
\text{fit risk on }B+C
\rightarrow
\text{predict }A,
\]

\[
\text{fit risk on }A+C
\rightarrow
\text{predict }B,
\]

\[
\text{fit risk on }A+B
\rightarrow
\text{predict }C.
\]

Concatenate these risk predictions.

Use them to choose:

- accept/abstain threshold;
- target source coverage;
- source selective operating point.

Then refit the fixed logistic gate on all available OOF source records before target inference.

This is a second-level cross-fitting step, but it does not require tuning a larger model.

---

# 4. `g_ref` itself should be fixed by an explicit deterministic rule

The method now correctly defines a fixed post-VLM decision rule:

\[
g_{\text{ref}}.
\]

However, the repository still allows several candidates:

- calibrated averaging;
- learned score fusion;
- possibly other source-selected fusion.

If the final choice is made after inspecting many source pseudo-shift results, there is still substantial researcher flexibility.

## Recommendation

Choose one of these approaches before Stage 2.

### Simplest version

Set:

\[
\boxed{
g_{\text{ref}}
=
\text{calibrated average}
}
\]

as the primary rule.

Use learned fusion only as an ablation.

This makes the reliability result extremely interpretable.

### Alternative

Define a deterministic source-only selection rule before any target evaluation.

For example:

> choose the fusion rule with the lowest macro source-domain ACER subject to the preregistered APCER constraint.

Then freeze the selected rule.

Do not choose \(g_{\text{ref}}\) from confirmatory target performance.

---

# 5. The cross-foundation claim needs a homogeneous-ensemble control

This is now one of the most important missing controls.

Suppose:

\[
\text{DINO}+\text{VLM}
\]

shows useful disagreement.

A reviewer can still ask:

> Would two ordinary independently trained models give the same disagreement benefit?

If yes, the contribution is generic ensemble diversity, not cross-foundation visual-versus-semantic complementarity.

## Minimum control

Train two independent DINO PAD heads or two independently trained DINO variants:

\[
D_1,D_2.
\]

Evaluate:

\[
D_1+D_2
\]

with the same:

- calibration;
- joint error table;
- REF;
- FARR;
- disagreement-risk pipeline.

Then compare against:

\[
D+\text{VLM}.
\]

The key question becomes:

\[
\boxed{
\text{Does cross-foundation diversity provide more useful rescue than homogeneous diversity?}
}
\]

This directly supports the central framing of the paper.

---

# 6. Add a CLIP/SigLIP visual-head control to isolate the value of text semantics

The DINO branch is source-supervised through a PAD head.

The VLM branch is prompt-driven.

Therefore their difference is not only:

\[
\text{DINO pretraining}
\quad\text{vs}\quad
\text{vision-language pretraining}.
\]

It is also:

\[
\text{supervised PAD head}
\quad\text{vs}\quad
\text{text-prompt classifier}.
\]

A reviewer may argue that the observed complementarity comes from adaptation style rather than semantic text knowledge.

## Recommended control

Using the same frozen CLIP/SigLIP image encoder, train a simple source-supervised binary PAD head:

\[
p_{C,\text{linear}}
=
h_C(f_C(x)).
\]

Compare:

\[
\text{DINO}
+
\text{CLIP visual linear head}
\]

against:

\[
\text{DINO}
+
\text{CLIP prompt semantic branch}.
\]

If the prompt branch produces more false-accept rescue or more transferable complementarity, the semantic-prior claim becomes much stronger.

This is a more informative control than merely adding another large backbone.

---

# 7. The current unseen-prompt specification still has a logical tension

The protocol says:

- the primary PAD prompt bank stays fixed;
- holding out an entire attack family removes prompts from that family.

These statements conflict if the primary bank itself contains attack-family prompts such as:

```text
mask
printed face
display presentation
```

A bank cannot simultaneously be fixed across protocols and have family-specific prompts removed.

## Recommendation

Separate prompt banks explicitly.

### Immutable core PAD bank

This never changes across leave-one-attack-out splits.

For example, use generic concepts such as:

```text
a genuine live human face captured by a camera
an artificial presentation shown to a camera
a non-live facial presentation
```

Denote:

\[
T_{\text{core}}.
\]

The binary PAD probability:

\[
p_V
\]

must always come from this same core bank.

### Auxiliary semantic attack bank

Contains:

```text
print
display replay
silicone mask
paper mask
...
```

Denote:

\[
T_{\text{aux}}.
\]

This bank may be filtered according to:

\[
\text{family}\rightarrow\text{instrument}\rightarrow\text{subtype}
\]

for downstream-unseen versus open-vocabulary analysis.

Auxiliary attack similarities must not alter the denominator of the core binary PAD probability.

This resolves the current ambiguity.

---

# 8. The VLM binary-score construction must be mathematically specified before experiments

The repository states that the VLM scores prompt ensembles and maps them to binary PAD probabilities.

That mapping is still underspecified.

Possible choices include:

- mean cosine;
- max cosine;
- log-sum-exp;
- prompt weighting;
- normalized softmax over all concepts;
- separate live/spoof prompt aggregation.

Different choices can materially change results.

## Recommendation

Predefine a reproducible formula.

For example, for prompt group \(T_c\):

\[
s_c(x)
=
\frac{1}{|T_c|}
\sum_{t\in T_c}
\cos(v(x),e_t).
\]

Then define:

\[
s_{\text{live}}(x)
\]

and:

\[
s_{\text{spoof}}(x),
\]

and compute:

\[
p_V(\text{spoof}\mid x)
=
\sigma
\left(
\frac{
s_{\text{spoof}}(x)-s_{\text{live}}(x)
}{
T
}
\right),
\]

where \(T\) is fitted only on source calibration data.

Alternative aggregation rules can be ablations.

The important point is to freeze the primary formula before confirmatory target evaluation.

---

# 9. Final full-source predictors create a remaining second-level distribution shift

The primary risk gate is trained from domain-OOF records such as:

\[
B+C\rightarrow A.
\]

But the final target predictor is trained on:

\[
A+B+C\rightarrow T.
\]

Thus the gate sees risk features generated by weaker subset-trained models during training, but full-source models at target inference.

This was recognized earlier, but the mismatch still exists.

## Recommendation

Quantify it explicitly.

On source validation data, compare the distribution of:

\[
z_{\text{OOF}}
\]

against:

\[
z_{\text{full-source}}.
\]

Report feature drift using simple statistics such as:

- mean/std shift;
- KS distance;
- Wasserstein distance where useful.

Also retain the sample-OOF gate as an important ablation because its predictors more closely resemble the final full-source model.

A useful comparison is therefore:

\[
\text{sample-OOF risk}
\]

versus:

\[
\text{domain-OOF risk}
\]

on exactly the same final target predictions.

If domain-OOF still generalizes better, that becomes meaningful evidence for pseudo-shift calibration.

---

# 10. Low-APCER security claims require finite-sample confidence bounds

The method proposes operating points such as:

\[
APCER\in\{0.5\%,1\%,5\%\}.
\]

At very low error rates, empirical APCER is unreliable when source validation attack counts are small.

For example, observing:

\[
0
\]

false accepts in:

\[
100
\]

attacks gives empirical:

\[
APCER=0\%,
\]

but does not establish a true 1% security level.

A rough 95% upper bound after zero observed events is approximately:

\[
\frac{3}{N}.
\]

Therefore to support an upper error probability near:

\[
1\%
\]

requires roughly several hundred attack trials, and 0.5% requires even more.

## Recommendation

For source security constraints, report both:

\[
\widehat{APCER}
\]

and a binomial confidence interval.

For a strong security-oriented threshold policy, consider requiring:

\[
UCB_{95\%}(APCER_d)
\le
\alpha
\]

for each source domain \(d\), rather than only:

\[
\widehat{APCER}_d\le\alpha.
\]

If the dataset does not contain enough attack trials to support such a claim, describe the operating point as a nominal empirical target rather than a statistically certified security level.

---

# 11. "Calibrated risk" should actually be evaluated for calibration

The Stage-2 primary metrics are currently:

- prediction-error AUPR;
- excess-AURC.

These measure ranking/selective quality.

But the method also describes:

\[
r_{\text{err}}(x)
\]

as a calibrated probability of failure.

A model can rank errors well and still be badly probabilistically calibrated.

## Recommendation

If the manuscript uses terms such as:

> calibrated failure risk

report at least one probability-calibration metric for:

\[
r_{\text{err}}.
\]

For example:

- Brier score;
- NLL;
- risk ECE/reliability diagram.

If probability calibration is not important and only ranking is used, call it:

> failure-risk score

rather than implying calibrated probabilities.

---

# 12. Image-quality features \(q(x)\) must be frozen before the target experiments

The full risk feature vector includes:

\[
q(x).
\]

This is a potentially large source of hidden flexibility.

Possible quality features include:

- blur;
- brightness;
- saturation;
- face size;
- detector confidence;
- pose;
- compression;
- illumination statistics.

If researchers repeatedly add/remove quality features after observing target failures, the final risk model can silently become target-engineered.

## Recommendation

Define a small fixed set before Stage 2.

For example:

\[
q(x)=
[
\text{blur},
\text{mean luminance},
\text{contrast},
\text{face-area ratio},
\text{detector confidence}
].
\]

Then use exactly the same vector for all targets.

Report:

\[
\text{risk without }q
\]

versus:

\[
\text{risk with }q.
\]

This shows whether the gain comes from cross-foundation disagreement or simply obvious image-quality failures.

---

# 13. Face-detector failures must enter the end-to-end security accounting

The protocol already says detector failures are recorded rather than silently dropped.

This should be carried through to deployment metrics.

If an attack causes the face detector to fail and the sample is excluded from APCER calculation, performance can be biased.

## Recommendation

Specify a deterministic detector-failure policy.

For example:

\[
\text{detector failure}
\rightarrow
\text{abstain/non-accept}.
\]

Then include detector failures in:

- attack coverage;
- bona-fide coverage;
- transaction success;
- end-to-end false acceptance.

This is especially important because the product claim is an end-to-end single-RGB PAD system, not PAD conditioned on perfect face detection.

---

# 14. The deterministic single-image frame must itself be preregistered

The strict single-image track now uses one deterministic frame per video.

Good.

But the frame-selection rule matters.

For example:

- first frame;
- middle frame;
- best detector-confidence frame;
- sharpest frame;

produce different levels of difficulty.

A quality-selected frame is no longer equivalent to a random camera snapshot and may leak nuisance information.

## Recommendation

Use a label-independent temporal rule as the primary protocol, such as:

\[
\boxed{\text{middle valid frame}}
\]

after protocol parsing.

Then run sensitivity analysis using fixed relative positions such as:

\[
25\%,50\%,75\%.
\]

Do not select the easiest frame using target-dependent quality or PAD scores.

---

# 15. Some `06-risks` open decisions are no longer open

The repository now already decided:

- primary calibrator: fixed-regularization logistic regression;
- primary transaction policy: \(K=1\);
- abstention: terminal non-accept for the main experiment.

However, `06-risks-and-decisions.md` still lists questions such as:

- which low-capacity calibrator;
- whether abstention is per-image or per-transaction.

These should be removed from `Open decisions` or rewritten as resolved decisions.

Keeping resolved questions marked open makes the dossier look less internally synchronized than it actually is.

---

# Recommended Stage-2 evaluation structure

To make the paper maximally clean, use two separate tables.

## Table A — Risk estimator quality with fixed predictions

Fix:

\[
g_{\text{ref}}.
\]

Every method ranks the same set of errors.

Compare:

- fused MSP;
- fused entropy;
- raw JS;
- calibrated JS;
- Mahalanobis-derived score;
- LogReg probabilities only;
- LogReg probabilities + JS;
- full risk model.

Primary:

\[
\text{error AUPR}
\]

and:

\[
\text{excess-AURC}.
\]

Secondary:

- error AUROC;
- Brier/NLL if probabilistic calibration is claimed.

## Table B — End-to-end selective system

Compare complete systems:

- DINO only;
- DINO + DINO homogeneous ensemble;
- DINO + CLIP supervised visual head;
- DINO + semantic VLM;
- always-on dual;
- conditional dual.

Report:

- APCER/BPCER;
- attack/bona-fide coverage;
- end-to-end false acceptance;
- VLM invocation;
- GPU-ms/request;
- P50/P95 latency.

This separation makes it much harder for a reviewer to argue that risk-estimator gains are merely classifier-accuracy gains.

---

# Final recommendation

The repository remains ready for Stage 1.

Before Stage 2, resolve the following:

1. compare uncertainty estimators on exactly the same base predictions;
2. choose accept/abstain thresholds from meta-OOF source risk predictions;
3. freeze the exact definition of \(g_{\text{ref}}\);
4. add a homogeneous DINO ensemble control;
5. add a CLIP/SigLIP supervised visual-head control;
6. separate immutable core PAD prompts from auxiliary attack prompts;
7. specify the mathematical VLM prompt-to-probability mapping;
8. quantify OOF-to-full-source risk-feature shift;
9. use finite-sample confidence bounds for very low APCER claims;
10. evaluate calibration if \(r_{\text{err}}\) is described probabilistically;
11. freeze image-quality features before target evaluation;
12. include detector failures in end-to-end accounting;
13. preregister the deterministic frame-selection rule;
14. clean resolved items out of `Open decisions`.

The biggest scientific question is now no longer whether DINO and a VLM can be combined.

It is:

\[
\boxed{
\text{Does heterogeneous visual-semantic diversity provide more security-useful rescue than ordinary homogeneous ensemble diversity?}
}
\]

That control is essential if the final paper wants to justify the phrase **cross-foundation disagreement** rather than simply **ensemble disagreement**.
