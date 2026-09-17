# ChatGPT Research Review — Round 10

Date: 2026-09-17

This review evaluates the repository after `25-review-response-round9.md`.

The architecture is now sufficiently stable. The remaining review focuses on:

- attribution of Stage-2 gains;
- fold-relative threshold leakage;
- risk-loss weighting;
- attack-OOF gate calibration;
- pilot/config freeze semantics;
- routing-threshold selection;
- confirmatory aggregation across domains and seeds.

## Overall assessment

Round 9 was incorporated well.

The repository now correctly includes:

- one permanent development/pilot MICO domain;
- three untouched confirmatory MICO targets;
- strong same-family DINOv2-Reg + plain-DINOv2 control;
- nested known-attack OOF for SiW-M;
- fold-safe operational thresholds;
- signed operational margin;
- a required distance-to-boundary baseline;
- conservative spoof-only routing;
- route-specific end-to-end accounting.

At this point, no additional model architecture is needed.

The remaining problems are primarily **estimand and implementation-lineage problems**.

The most important new issue is:

\[
\boxed{
m_F,\widehat p_D,\widehat p_V
\text{ together algebraically reveal the fold-specific threshold}
}
\]

which can confound both domain-identifiability auditing and the attribution of cross-foundation risk gains.

---

# 1. The current primary risk vector exposes the OOF threshold exactly

The primary risk vector is:

\[
z=
[
\widehat p_D,
\widehat p_V,
d_{abs},
m_F,
q
]
\]

with:

\[
p_F=\frac{\widehat p_D+\widehat p_V}{2},
\]

and:

\[
m_F=p_F-\tau_{ref}^{(k)}.
\]

Therefore:

\[
\boxed{
\tau_{ref}^{(k)}
=
\frac{\widehat p_D+\widehat p_V}{2}
-
m_F
}
\]

can be reconstructed exactly from the risk features.

If every domain-OOF fold has its own:

\[
\tau_{ref}^{(k)},
\]

the gate receives an explicit fold-specific constant.

With only three source domains, this may act almost like a domain/fold identifier.

This is not merely a generic correlation problem; it is algebraically encoded by construction.

## Consequence

A domain-ID audit using this full feature vector is difficult to interpret because the policy threshold itself can identify the fold.

## Recommendation

Separate two feature spaces.

### Scientific attribution features

Do **not** include \(m_F\):

\[
z_{\text{science}}
=
[
\widehat p_D,
\widehat p_V,
d_{abs},
q
].
\]

Use these features for:

- \(\Delta_{CF}\);
- \(\Delta_{dis}\);
- the claim that cross-foundation predictions improve failure detection.

### Operational policy features

Allow:

\[
m_F
\]

only in the deployment-oriented gate:

\[
z_{\text{oper}}
=
[
\widehat p_D,
\widehat p_V,
d_{abs},
m_F,
q
].
\]

Then report the extra contribution of the policy margin separately.

This prevents the scientific cross-foundation claim from receiving credit merely because the model was told which fold-specific decision boundary generated its error label.

---

# 2. Add a third incremental quantity: policy-margin gain

The project now has:

\[
\Delta_{CF}
\]

for dual-foundation probabilities and:

\[
\Delta_{dis}
\]

for explicit disagreement.

The operational margin introduces a third source of gain.

Define:

\[
R_{DV}
=
R(
\widehat p_D,
\widehat p_V,
q
),
\]

\[
R_{DVd}
=
R(
\widehat p_D,
\widehat p_V,
d_{abs},
q
),
\]

and:

\[
R_{DVdm}
=
R(
\widehat p_D,
\widehat p_V,
d_{abs},
m_F,
q
).
\]

Then:

\[
\boxed{
\Delta_{CF}
=
Perf(R_{DV})
-
\max(
Perf(R_D),
Perf(R_V)
)
}
\]

\[
\boxed{
\Delta_{dis}
=
Perf(R_{DVd})
-
Perf(R_{DV})
}
\]

and:

\[
\boxed{
\Delta_{margin}
=
Perf(R_{DVdm})
-
Perf(R_{DVd}).
}
\]

This produces a very clean attribution:

1. gain from having two foundation predictors;
2. additional gain from explicit disagreement;
3. additional gain from knowing distance to the operational decision boundary.

The deployed risk gate may use all three, but the paper no longer confuses their contributions.

---

# 3. The current RQ2 formulation still partially confounds \(\Delta_{CF}\) with policy margin

RQ2 currently says that cross-foundation probabilities plus:

- quality;
- policy-margin features;

must outperform single-branch learned-risk baselines.

That makes the cross-foundation estimand ambiguous.

A model with two branch probabilities plus \(m_F\) is being compared to a single-branch model that cannot naturally compute the fused margin without using the other branch.

Therefore a positive \(\Delta_{CF}\) could partly be a policy-margin gain.

## Recommendation

Define the RQ2 claim quantities using:

\[
z_{\text{science}}
\]

without \(m_F\).

Then state separately:

> adding the policy-relative fused margin is an operational enhancement evaluated by \(\Delta_{margin}\).

This is the cleanest decomposition.

---

# 4. Explicitly define every Stage-2 baseline feature set

Names such as:

- \(R_q\);
- \(R_D\);
- \(R_V\);
- \(R_{DV}\);
- \(R_{DVd}\);

are currently conceptually clear but not yet fully specified.

Freeze them.

Recommended primary decomposition:

\[
R_q=[q]
\]

\[
R_D=[\widehat p_D,q]
\]

\[
R_V=[\widehat p_V,q]
\]

\[
R_{DV}=[\widehat p_D,\widehat p_V,q]
\]

\[
R_{DVd}=[\widehat p_D,\widehat p_V,d_{abs},q]
\]

\[
R_{DVdm}=[\widehat p_D,\widehat p_V,d_{abs},m_F,q].
\]

All use:

- the same logistic regression family;
- the same fixed regularization;
- the same source-lineage protocol.

This removes a large amount of hidden researcher flexibility.

---

# 5. Risk-gate training loss needs an explicit domain-weighting policy

Branch calibration is now carefully defined as:

- class-balanced within domains;
- equal-domain weighted across sources.

The failure-risk logistic gate does not yet have an equally explicit loss weighting rule.

Domain-OOF folds can differ greatly in sample count.

If all OOF samples are simply concatenated and ordinary BCE is minimized, the largest domain dominates.

## Recommendation

For domain-OOF risk fitting use equal pseudo-domain weighting:

\[
\mathcal L_{risk}
=
\frac{1}{K}
\sum_{k=1}^{K}
\frac{1}{N_k}
\sum_{i\in k}
BCE(r_i,e_i).
\]

If \(r_{err}\) is interpreted probabilistically, retain the natural error prevalence **within each pseudo-domain** rather than class-balancing correct/error labels.

Artificially balancing error labels would change the probability semantics.

If a class-weighted loss is useful for ranking rare errors, keep it as an AUPR-focused ablation and call its output a risk score rather than a calibrated failure probability.

---

# 6. Attack-OOF needs its own known-attack gate-calibration set

The final unseen attack:

\[
A^\star
\]

is now correctly untouched.

However, the SiW-M attack-OOF pipeline also needs an accept-threshold calibration set equivalent to \(G\).

That set must come only from known attacks.

## Recommendation

Before constructing pseudo-attack OOF records:

1. carve a subject/video-safe:
   \[
   G_{attack}
   \]
   from known attacks only;
2. exclude \(G_{attack}\) from branch fitting, branch calibration, pseudo-attack OOF, and risk fitting;
3. fit the attack-OOF risk gate from remaining known attacks;
4. select its accept threshold on \(G_{attack}\);
5. evaluate once on:
   \[
   A^\star.
   \]

Do not reuse the final unseen family for any gate-threshold operation.

The protocol should specify whether:

\[
G_{domain}
\]

and:

\[
G_{attack}
\]

are separate constructions.

---

# 7. The risk-margin baseline should be absolute, while the signed margin is an operational feature

The required simple baseline is currently:

\[
-|p_F-\tau_{ref}|.
\]

Good.

That measures generic proximity to the decision boundary.

The signed margin:

\[
m_F=p_F-\tau_{ref}
\]

adds predicted-side information.

These are not identical.

A signed-margin risk model can exploit class asymmetry:

- live-side near-boundary samples;
- spoof-side near-boundary samples;

may have different risks.

That is potentially useful, but the role should be explicit.

## Recommendation

Use:

\[
-|m_F|
\]

as the simple threshold-distance baseline.

Use signed:

\[
m_F
\]

only in the learned operational gate.

Then any gain from class-side information is attributed to:

\[
\Delta_{margin}
\]

rather than to simple uncertainty distance.

---

# 8. The primary spoof-only routing threshold should be constrained by bona-fide rejection, not APCER

The primary conditional policy is now:

```text
DINO confidently SPOOF
    -> terminal non-accept

everything else
    -> invoke VLM
```

This is conservative and good.

Importantly, this route cannot introduce a new attack false accept.

An attack sent to early spoof rejection is already blocked.

The routing threshold's main failure mode is:

\[
\text{bona-fide user}
\rightarrow
\text{incorrect early spoof rejection}.
\]

Therefore the primary routing threshold should be selected by a constraint such as:

\[
BPCER_{\text{early-route}}\le\beta
\]

or:

\[
\Delta BFNR_{\text{end2end}}\le\beta.
\]

Then minimize:

\[
\text{VLM invocation rate}.
\]

## Recommendation

Primary routing objective:

\[
\min
P(\text{invoke VLM})
\]

subject to a preregistered source-side bona-fide rejection constraint.

Only direct-LIVE routing ablations require strong APCER/false-accept constraints.

This aligns the optimization objective with the actual security consequence of each route.

---

# 9. Do not use the same holdout \(G\) repeatedly for many unrelated threshold choices

The permanent gate-calibration set \(G\) is now valuable because it is untouched.

But if it is used to choose:

- failure-risk accept threshold;
- routing threshold;
- several operating points;
- several ablation thresholds;

it gradually becomes a general-purpose development set.

That recreates holdout overfitting.

## Recommendation

For the primary experiment:

- use \(G\) only for the final post-VLM accept/abstain threshold;
- choose spoof-only routing threshold from a separate source-only routing-validation procedure.

A practical option is to use the branch-validation partition with a fully preregistered routing criterion.

If the same \(G\) must support multiple fixed thresholds because data are small, predefine all threshold rules before examining \(G\) and do not select among alternatives based on its performance.

---

# 10. The exact pilot candidate-selection rule must be preregistered, not only the candidate set

The repository now commits a finite VLM candidate set before pilot labels.

Good.

But a finite set alone does not determine selection.

Suppose there are several checkpoints and preprocessing variants.

The final candidate could be chosen by:

- AUC;
- ACER;
- FARR;
- latency;
- a subjective trade-off;
- whichever metric looks best.

That still creates pilot-level researcher degrees of freedom.

## Recommendation

Before opening pilot labels, commit:

1. the finite candidate set;
2. the primary pilot-selection metric;
3. tie-breaking rules;
4. any compute/latency constraint.

For example:

> Choose the candidate with highest pilot ACER improvement subject to frozen-branch competence and a fixed latency ceiling; ties use lower latency.

The exact rule can differ.

The important requirement is deterministic selection from the committed candidate set.

---

# 11. The prompt-freeze wording is still slightly inconsistent

The method says:

> preregister and freeze \(T_{core}\)

before training.

The experiment plan says prompt/checkpoint YAML artifacts are:

> frozen after pilot selection.

These imply different timelines.

## Two valid choices

### Choice A — core prompts fixed before pilot

Pilot selects only:

- VLM checkpoint;
- perhaps image resolution/preprocessing.

Then \(T_{core}\) is truly preregistered.

### Choice B — finite prompt-bank candidates before pilot

Pilot may select one prompt bank from a committed finite set.

Then the correct wording is:

> pilot-selected and confirmatory-frozen

rather than:

> preregistered immutable before pilot.

Pick one and synchronize all documents.

For the cleanest unseen-transfer story, Choice A is preferable.

---

# 12. Three confirmatory domains require a preregistered cross-domain success rule

The current plan says quantities such as:

\[
\Delta_{hetero}>0
\]

must hold on confirmatory targets.

But it does not define exactly what that means across three targets.

Possible interpretations include:

- positive on all 3;
- positive on at least 2/3;
- positive macro average;
- macro confidence interval excludes zero.

These can lead to different conclusions.

## Recommendation

Predefine a rule such as:

1. macro mean across three confirmatory targets is positive;
2. at least two of three targets have positive paired point estimates;
3. no target shows a large preregistered harm beyond tolerance.

Do the same for:

\[
\Delta_{CF}^{AUPR}
\]

and:

\[
\Delta_{dis}^{AUPR}.
\]

With only three target domains, avoid claiming inference to a statistical population of all possible domains.

Use language such as:

> consistent across the evaluated confirmatory domains.

---

# 13. Seed aggregation also needs a preregistered rule

The dossier requires at least three random seeds.

However, it does not yet state how seeds enter:

- continuation criteria;
- \(\Delta_{hetero}\);
- \(\Delta_{CF}\);
- \(\Delta_{dis}\).

Do not pool predictions from different seeds unless the deployed system is actually an ensemble.

## Recommendation

For each target and seed:

1. train the full pipeline independently;
2. compute the paired metric/delta independently;
3. report the mean and standard deviation over seed-level metrics;
4. perform subject/video bootstrap within each seed;
5. require directional consistency across seeds according to a preregistered rule.

Do not perform a conventional \(t\)-test with \(n=3\) seeds.

Do not pick the best seed for confirmatory reporting.

---

# 14. The strong same-family control must use the same fusion/calibration protocol as the heterogeneous pair

The strong control:

\[
DINOv2\text{-Reg}+DINOv2
\]

is now required for the cross-foundation title.

For a fair rescue comparison it must receive the same treatment as:

\[
DINOv2\text{-Reg}+VLM.
\]

That includes:

- one-stage affine source calibration per branch;
- the same source data lineage;
- the same calibrated-average fusion rule;
- the same reference operating-point selection rule;
- the same false-accept denominator;
- the same bootstrap units.

Do not allow the heterogeneous pair to use a better fusion/calibration stack than the same-family pair.

This should be explicit because:

\[
\Delta_{hetero}
\]

is now a central claim quantity.

---

# 15. Add a strength-normalized error-dependence diagnostic

Raw rescue remains the correct operational primary metric.

Complementarity lift is already included as a diagnostic.

Another useful strength-adjusted diagnostic is normalized double-fault dependence.

Let:

\[
E_D=\mathbf 1[DINO\ wrong],
\]

\[
E_B=\mathbf 1[second\ branch\ wrong].
\]

Define:

\[
NDF
=
\frac{
P(E_D=1,E_B=1)
}{
P(E_D=1)P(E_B=1)
}.
\]

Interpretation:

- \(NDF\approx1\): approximately independent errors;
- \(NDF>1\): errors cluster together;
- \(NDF<1\): unusually complementary errors.

Compute it overall and attack-conditionally.

This does not replace rescue or \(\Delta_{hetero}\), but it helps distinguish:

> second branch is strong

from:

> second branch is specifically diverse where DINO fails.

---

# 16. Risk-score calibration and risk-score ranking should use different loss variants only if explicitly separated

The primary risk gate is expected to support:

- AUPR ranking;
- Brier/NLL calibration;
- accept/abstain thresholding.

A class-weighted loss may improve rare-error ranking but destroys straightforward probability interpretation.

An unweighted BCE preserves source error prevalence but can be dominated by correct samples.

## Recommendation

Primary probabilistic risk model:

- equal pseudo-domain weighting;
- natural correct/error prevalence within each pseudo-domain;
- unweighted BCE within domain.

Optional ranking-focused ablation:

- error-class weighting or focal loss.

If the latter is used, describe it as a **risk score**, not a calibrated failure probability.

This keeps the probability-calibration claim internally consistent.

---

# 17. The novelty document should no longer say "disagreement calibration" as the unconditional core contribution

The charter and novelty text still contain phrases equivalent to:

> cross-fitted disagreement calibration.

But the project now explicitly allows the possibility that:

\[
\Delta_{dis}\approx0.
\]

In that case the scientifically valid core becomes:

\[
\text{cross-fitted cross-foundation failure-risk calibration}
\]

rather than explicit disagreement calibration.

## Recommendation

Use neutral core wording now:

> source-only cross-fitted failure-risk calibration from independently trained heterogeneous foundation predictors.

Then say:

> explicit disagreement is retained in the title/contribution only if its preregistered incremental test passes.

This makes the dossier consistent before the result is known.

---

# 18. The pilot domain can be used as source data for confirmatory folds, but that fact should be stated

Once one MICO domain is used as the pilot, the remaining three domains are confirmatory targets.

For each of those confirmatory MICO folds, the pilot dataset is naturally one of the labeled source datasets.

That is valid.

However, it can confuse readers who see:

> pilot target labels were used during development

and later:

> source-only confirmatory evaluation.

## Recommendation

State explicitly:

> The development domain is excluded as a confirmatory target but remains an allowed labeled source domain when another dataset is the confirmatory target, exactly as required by that MICO fold.

This is not leakage into a confirmatory target.

It should simply be transparent.

---

# Recommended synchronization fixes

Before Stage 2 implementation:

1. separate scientific risk features from operational-margin features;
2. add \(\Delta_{margin}\);
3. freeze exact baseline feature sets;
4. define equal-domain risk loss weighting;
5. create a known-attack-only \(G_{attack}\) for SiW-M;
6. use absolute margin as the simple boundary-distance baseline;
7. select spoof-only routing based primarily on bona-fide rejection/compute trade-off;
8. do not repeatedly tune unrelated thresholds on \(G\);
9. preregister the pilot candidate-selection metric and tie-breaking rule;
10. resolve whether core prompts are pre-pilot fixed or pilot-selected from a finite set;
11. preregister cross-domain success aggregation over the three confirmatory targets;
12. preregister seed aggregation and consistency criteria;
13. match calibration/fusion exactly for strong same-family and heterogeneous pairs;
14. add normalized double-fault as a diagnostic;
15. separate probabilistic risk fitting from ranking-focused class-weighted ablations;
16. make novelty wording conditional on \(\Delta_{dis}\) from the start.

---

# Final recommendation

The project is ready to start Stage 1 implementation.

The next review should ideally be driven by actual manifests, split counts, and first pilot outputs rather than further architecture prose.

The cleanest Stage-2 attribution hierarchy is now:

\[
\boxed{
\Delta_{CF}
=
\text{gain from two heterogeneous branch scores}
}
\]

\[
\boxed{
\Delta_{dis}
=
\text{additional gain from explicit disagreement}
}
\]

\[
\boxed{
\Delta_{margin}
=
\text{additional gain from policy-relative decision margin}
}
\]

This three-part decomposition is important because the operational margin is powerful but should not be mistaken for evidence that cross-foundation disagreement itself is the mechanism.

The strongest remaining protocol risk is the exact algebraic relation:

\[
\tau_{ref}^{(k)}
=
\frac{\widehat p_D+\widehat p_V}{2}
-
m_F.
\]

If the gate sees all three terms, it sees the fold-specific threshold.

Therefore either:

- keep policy-margin features out of the scientific attribution model; or
- explicitly treat them as a separate operational contribution.

Once that is resolved, the research plan is difficult to attack on basic leakage or comparison-fairness grounds.
