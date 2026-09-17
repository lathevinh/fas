# ChatGPT Research Review — Round 4

Date: 2026-09-17

This review digs deeper into the experimental design after reading the current repository state, especially:

- `02-research-questions.md`
- `03-method.md`
- `04-data-and-protocols.md`
- `05-experiment-plan.md`
- `13-review-response-round3.md`

## Overall assessment

The architecture is now sufficiently stable.

I do **not** recommend adding new architectural modules before Stage 1.

The next risks are no longer mainly architectural. They concern:

- the semantics of the risk target;
- biometric operating-point validity;
- unit of evaluation;
- threshold dependence;
- fairness of uncertainty baselines;
- statistical validity;
- deployment latency interpretation.

These issues should be addressed before Stage 2, although Stage 1 can begin immediately.

---

# 1. RQ2 currently mixes two different problems: failure detection and unseen/OOD detection

The current RQ2 asks whether disagreement can detect:

- prediction errors;
- downstream-unseen attacks.

These are not the same target.

Suppose a downstream-unseen silicone-mask attack is correctly classified as spoof.

Then:

\[
\text{downstream-unseen}=1
\]

but:

\[
\text{prediction failure}=0.
\]

A failure-risk model trained using correctness labels has no reason to assign high risk to such a correctly classified unseen attack.

Therefore the core RQ2 should be narrowed to:

\[
\boxed{
\text{failure detection under unseen domain and attack shifts}
}
\]

The risk model should estimate approximately:

\[
r_{\text{err}}(x)
=
P(\hat y\neq y\mid z(x)).
\]

Downstream-unseen PAIs should primarily be evaluated by:

- APCER/BPCER;
- error rate on unseen attacks;
- selective performance on unseen attacks.

If a separate OOD or shift score is later studied, it should be treated as a secondary task:

\[
r_{\text{shift}}(x)
\neq
r_{\text{err}}(x).
\]

Do not use one score and claim both failure detection and unknownness unless the target is explicitly defined and justified.

---

# 2. Oracle complementarity should be biometric and class-conditional

The repository correctly removed ambiguous `oracle AUC`.

However, a generic oracle accuracy such as:

\[
1-P_{ww}
\]

is still dependent on the live/spoof class prevalence of the evaluated set.

For PAD, the more meaningful oracle quantities are class-conditional.

Define:

\[
APCER_{\text{oracle}}
=
P(D\text{ wrong}\land V\text{ wrong}\mid y=\text{attack}),
\]

and:

\[
BPCER_{\text{oracle}}
=
P(D\text{ wrong}\land V\text{ wrong}\mid y=\text{bona fide}).
\]

Then:

\[
ACER_{\text{oracle}}
=
\frac{
APCER_{\text{oracle}}
+
BPCER_{\text{oracle}}
}{2}.
\]

This is much more interpretable for biometric security.

---

# 3. Complementarity does not need to be symmetric

The current proposal emphasizes both:

\[
P_{cw}
\]

and:

\[
P_{wc}.
\]

This is useful descriptively, but it should not become a strict requirement that both directions be equally large.

If DINO is the primary deployed model, the more operational quantity is:

\[
R_{V|D}
=
P(V\text{ correct}\mid D\text{ wrong}).
\]

Most importantly:

\[
R^{FA}_{V|D}
=
P(
V\text{ blocks attack}
\mid
D\text{ false accepts}
).
\]

A weaker VLM overall could still be valuable if it corrects a large fraction of the security-critical false accepts made by DINO.

Therefore do not kill the project merely because complementarity is asymmetric.

The primary question should be:

> Does the second branch recover enough important errors from the primary branch to justify its cost?

---

# 4. Frame-level evaluation risks pseudo-replication

Many video FAS datasets provide multiple strongly correlated frames from the same video.

If several frames from one video are treated as independent observations when computing:

\[
P_{cc},P_{cw},P_{wc},P_{ww},
\]

confidence intervals and significance tests may become artificially optimistic.

The repository already recognizes subject/video leakage, but evaluation should explicitly distinguish two tracks.

## Benchmark-compatible track

Follow the conventional protocol of each dataset and published baselines.

If the literature aggregates frame scores to a video-level score, reproduce that behavior.

## Strict single-image track

For the single-image scientific claim, use either:

- exactly one deterministic frame per video; or
- multiple frame-level predictions but cluster all statistical inference by video/subject.

For bootstrap confidence intervals:

\[
\text{bootstrap unit}
=
\text{video or subject},
\]

not individual frame.

Joint correctness and oracle analyses should ideally be reported at both:

- image/frame level;
- video/transaction level.

This avoids pseudo-replication.

---

# 5. Source-selected deployment operating points must be separated from target-posthoc metrics

The repository correctly states that a source-selected constraint such as:

\[
APCER\leq 1\%
\]

cannot guarantee the unseen target will also satisfy 1% APCER.

This distinction should be made explicit in the final tables.

## Deployment-style evaluation

Select threshold/policy only on source data:

\[
\tau_{\text{source}}.
\]

Apply it unchanged to the target.

Report:

\[
APCER_{\text{target}}(\tau_{\text{source}})
\]

and:

\[
BPCER_{\text{target}}(\tau_{\text{source}}).
\]

These are the real domain-generalization deployment results.

## Post-hoc diagnostic evaluation

You may also report target ROC-derived metrics such as:

\[
BPCER @ APCER=1\%.
\]

But these are post-hoc diagnostics because target labels are used to locate the operating point.

They must not be presented as a deployable source-only threshold.

---

# 6. Source operating-point selection should consider worst-domain robustness

A pooled source threshold may hide one bad source domain.

For example:

\[
APCER_{\text{pooled}}=1\%
\]

could coexist with:

\[
APCER_{A}=0.2\%,
\qquad
APCER_{B}=0.8\%,
\qquad
APCER_{C}=8\%.
\]

A more robust threshold policy is:

\[
\max_{d\in\text{source}}
APCER_d(\tau)
\leq
\alpha.
\]

This may be conservative, but it better matches the claimed security-oriented deployment setting.

Recommended comparison:

1. pooled-source threshold;
2. worst-source constrained threshold.

This can itself become a useful deployment ablation.

---

# 7. Failure-risk labels are threshold-dependent

The risk calibrator is trained using correctness/error labels.

But correctness depends on the PAD decision threshold.

If the paper evaluates:

\[
\alpha\in\{0.5\%,1\%,5\%\},
\]

the corresponding classification thresholds differ.

The same sample can be:

- correct under one operating policy;
- incorrect under another.

Therefore a generic risk target is not automatically valid for every security operating point.

Two clean options exist.

## Option A — one pre-registered reference policy

Train:

\[
r_{\text{err}}(x)
\]

using correctness under one predefined source-selected operating point.

Then evaluate transfer to nearby operating points as an ablation.

## Option B — policy-specific risk models

Train:

\[
r_{\alpha}(x)
\]

for each security target:

\[
\alpha\in\{0.5\%,1\%,5\%\}.
\]

This is more expensive but conceptually cleaner.

Do not implicitly train risk labels at EER and then claim the same gate directly optimizes low-APCER security deployment.

---

# 8. JS and entropy are deterministic transforms of branch probabilities

The current feature vector includes:

\[
z=[
\widehat p_D,
\widehat p_V,
JS,
H_D,
H_V,
E_D,
E_V,
q
].
\]

But:

\[
JS
=
f(\widehat p_D,\widehat p_V),
\]

and:

\[
H_D=f(\widehat p_D),
\qquad
H_V=f(\widehat p_V).
\]

Therefore JS and entropy do not necessarily contain information beyond the calibrated probabilities.

They may simply provide useful engineered nonlinear features.

This is fine, but it needs a capacity-matched ablation.

Recommended baselines:

### Linear probability baseline

\[
\text{LogReg}(
\widehat p_D,
\widehat p_V
).
\]

### Linear + engineered disagreement

\[
\text{LogReg}(
\widehat p_D,
\widehat p_V,
JS
).
\]

### Nonlinear probability baseline

\[
\text{MLP}(
\widehat p_D,
\widehat p_V
).
\]

### Full proposed risk model

\[
\text{RiskModel}(
\widehat p_D,
\widehat p_V,
JS,
H_D,
H_V,
E_D,
E_V,
q
).
\]

If the proposed model includes image quality \(q\), a capacity-matched baseline must also include \(q\).

Otherwise gains could come from image quality rather than disagreement.

---

# 9. Reliability baselines should include a stronger FAS-specific confidence method

The current Stage 2 baseline set includes:

- MSP;
- entropy;
- energy;
- score averaging;
- learned fusion.

These are necessary but generic.

The related-work section already identifies confidence-aware FAS as a close competitor.

Therefore include at least one stronger representation-space confidence baseline.

A simple option is:

\[
\boxed{
\text{Mahalanobis confidence on DINO embedding}
}
\]

using source bona-fide/spoof feature distributions.

This gives a FAS-specific representation confidence baseline without reproducing an entire external method.

If cross-foundation disagreement cannot outperform a strong single-foundation confidence baseline, the reliability novelty becomes much weaker.

---

# 10. Conditional VLM reduces average compute, but may not reduce hard-case latency

The proposed conditional pipeline is:

\[
DINO
\rightarrow
\text{routing}
\rightarrow
VLM
\]

for escalated cases.

For an escalated request:

\[
T_{\text{conditional}}
=
T_D+T_V.
\]

If always-on DINO and VLM can execute in parallel:

\[
T_{\text{parallel}}
\approx
\max(T_D,T_V).
\]

Therefore conditional inference clearly reduces:

- VLM invocation rate;
- average GPU compute;
- average energy/cost.

But it may increase latency for difficult cases.

Do not claim merely that conditional inference reduces latency.

Report:

- mean latency;
- P50 latency;
- P95 latency;
- GPU-ms/request;
- throughput;
- VLM invocation rate;
- retry rate.

The safer claim is:

\[
\boxed{
\text{security–coverage–compute trade-off}
}
\]

rather than simply:

\[
\text{lower latency}.
\]

---

# 11. Open-vocabulary prompt exclusion needs a semantic hierarchy

The unseen-attack protocol is now correctly separated into downstream-unseen and open-vocabulary settings.

However, there is still a finer semantic issue.

Suppose the held-out attack is:

\[
\text{silicone mask}.
\]

The prompt bank may still contain:

\[
\text{mask or artificial face}.
\]

Whether this is allowed depends on the level at which the attack is declared unseen.

The protocol should explicitly define a hierarchy such as:

\[
\text{family}
\rightarrow
\text{instrument}
\rightarrow
\text{subtype}.
\]

For example:

```text
mask
  ├── paper mask
  ├── rigid mask
  ├── silicone mask
  └── latex mask
```

If the protocol holds out the entire `mask` family, all mask-family prompts must be removed.

If only `silicone mask` is held out while other mask attacks remain known, a generic `mask` prompt may be legitimate.

Prompt exclusion must match the semantic level of the claimed unseen condition.

---

# 12. Open-vocabulary prompts should not alter the core PAD probability geometry

Adding a new attack-specific prompt to a shared softmax prompt bank may change all normalized probabilities because the denominator changes.

This creates a confound:

\[
\text{new semantic knowledge}
\]

versus:

\[
\text{changed score normalization}.
\]

A cleaner design is:

- keep the primary PAD prompt bank fixed;
- compute attack-specific open-vocabulary similarity as an auxiliary semantic score.

Then the main PAD score remains comparable across protocols.

This prevents an added prompt from changing the whole classifier geometry.

---

# 13. Replace vague "non-negligible oracle gain" with pre-registered rescue metrics

The Stage 1 kill criterion currently uses language such as:

> oracle gain is non-negligible.

This is too flexible after observing results.

Before running the first target, define at least one quantitative continuation criterion.

Two highly interpretable metrics are:

## Recoverable Error Fraction

\[
REF
=
\frac{
P(D\text{ wrong},V\text{ correct})
}{
P(D\text{ wrong})
}.
\]

This measures what fraction of DINO errors are recoverable by the VLM.

## False-Accept Rescue Rate

\[
FARR
=
\frac{
\#\{
\text{DINO false accepts corrected by VLM}
\}
}{
\#\{
\text{DINO false accepts}
\}
}.
\]

This is especially important for biometric security.

The project should continue only if these quantities show meaningful recoverable headroom across multiple targets/subgroups.

Exact thresholds should be pre-registered before target evaluation to reduce researcher degrees of freedom.

---

# 14. Recommended Stage 1 output package

Stage 1 does not need any risk calibrator yet.

For each MICO target, produce:

## Branch performance

- DINO APCER/BPCER/ACER/HTER/AUC;
- VLM APCER/BPCER/ACER/HTER/AUC;
- calibrated average;
- learned fusion.

## Joint correctness

\[
P_{cc},P_{cw},P_{wc},P_{ww}.
\]

## Security-specific complementarity

\[
R_{V|D}
=
P(V\text{ correct}\mid D\text{ wrong}),
\]

\[
R^{FA}_{V|D}
=
P(V\text{ blocks attack}\mid D\text{ false accepts}).
\]

## Oracle headroom

- oracle APCER;
- oracle BPCER;
- oracle ACER;
- gain over the better branch.

## Statistical reporting

- bootstrap by video/subject;
- not by frame.

Only after these results show meaningful recoverable information should Stage 2 begin.

---

# Final recommendation

The architecture should remain frozen.

The most important remaining corrections are experimental and semantic:

\[
\boxed{
\text{failure risk}
\neq
\text{unknownness}
}
\]

\[
\boxed{
\text{complementarity should be biometric and asymmetric}
}
\]

\[
\boxed{
\text{evaluation must separate frame/video and source-selected/target-posthoc operating points}
}
\]

\[
\boxed{
\text{risk labels depend on the security decision policy}
}
\]

Stage 1 can begin immediately with:

- DINO;
- VLM;
- independent calibration;
- calibrated averaging;
- joint correctness;
- rescue rates;
- class-conditional oracle headroom.

Do not build the source-only risk calibrator until Stage 1 proves that the VLM contains enough recoverable information to justify a second foundation model.

If:

\[
R_{V|D}
\]

and especially:

\[
R^{FA}_{V|D}
\]

are small, stop the dual-foundation direction.

If they are substantial across multiple untouched targets, then proceed to source-only risk calibration and selective deployment.
