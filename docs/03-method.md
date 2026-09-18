# Proposed Method

## Design principle

For image $x$, two predictors are trained independently:

$$\ell_D=f_D(x), \qquad \ell_V=f_V(x).$$

The method does not align their features and does not minimize
$D_{JS}(\widehat p_D,\widehat p_V)$. Their different pretraining objectives and natural error diversity
are the signal under study. Each branch raw logit is calibrated exactly once on source
validation data before disagreement is computed:

$$
\widehat p_D=\sigma(a_D\ell_D+b_D),\qquad
\widehat p_V=\sigma(a_V\ell_V+b_V),\qquad a_D,a_V>0,
d_{abs}(x)=|\widehat p_D-\widehat p_V|.
$$

Monotone affine logistic calibration is the one and only $\operatorname{Cal}_D$ and
$\operatorname{Cal}_V$; temperature-only scaling and JS disagreement are ablations.
Calibration loss is class-balanced within each source domain and then averaged equally
across domains. The output is a standardized source-calibrated PAD score, not a
real-world deployment posterior. No second calibrator is stacked afterward, and all
parameters freeze before target evaluation.

## DINO visual predictor

DINOv2-Reg returns patch, class, and register tokens:

$$
D(x)=\{d_1,\ldots,d_N,d_{cls},d_{reg}^1,\ldots,d_{reg}^R\}.
$$

The minimum implementation concatenates the class token with mean-pooled patch
features and trains a binary PAD head. This pooling is fixed, so pooled frozen features
can be cached without fold-dependent lineage. Learned attention pooling and optional
attack-family heads are secondary ablations. Registers remain internal context tokens
and are not treated as spatial heatmaps.

This branch is called a visual or forensic predictor because its dense self-supervised
features can retain local texture. The name does not assert that every patch activation
is a verified physical forensic cue.

Training order:

1. pretrained `dinov2_vitb14_reg4`, frozen backbone, train prediction heads;
2. compare DINOv2 without registers as an ablation;
3. add LoRA/adapters to the last four blocks only after the frozen kill experiment;
4. do not full-fine-tune in the first implementation.

## VLM semantic predictor

A frozen OpenCLIP `ViT-B-16` model with `laion2b_s34b_b88k` weights, native 224-pixel
preprocessing, and the preregistered context crop uses an immutable binary core prompt bank
$T_{core}=T_{live}\cup T_{spoof}$ with generic live and artificial-presentation
wording. For each class $c$:

$$
s_c(x)=\frac{1}{|T_c|}\sum_{t\in T_c}\cos(v(x),e_t),\qquad
\ell_V(x)=s_{spoof}(x)-s_{live}(x),\qquad
\widehat p_V(x)=\sigma(a_V\ell_V(x)+b_V),\qquad a_V>0.
$$

The affine parameters are fitted once on domain-balanced source calibration data.
Mean cosine is the primary
aggregation; max and log-sum-exp are ablations. A separate auxiliary attack bank
$T_{aux}$ scores coarse concepts such as:

- bona fide or natural face;
- printed face or paper presentation;
- replayed face or display presentation;
- mask or artificial face.

Auxiliary scores never alter the core binary PAD denominator. Free-form generated
rationales and fine-grained concepts such as moire are outside the minimum
implementation.

Training order:

1. preregister and freeze $T_{core}$, then freeze image and text encoders;
2. fit only monotone affine calibration $(a_V,b_V)$ on source calibration data;
3. compare source-tuned templates/weights and a small learned head only as ablations;
4. consider image-encoder LoRA only if a frozen branch is competent but underfits;
5. keep the text encoder frozen to preserve its semantic space.

The VLM must remain independently useful. Fine-tuning both branches jointly on a
shared consistency loss is prohibited in the main method.

## Complementarity analysis

For each target sample, record whether each branch is correct and estimate
$P_{cc},P_{cw},P_{wc},P_{ww}$. Report:

- each branch's standalone performance;
- double-fault rate $P_{ww}$;
- one simple directional DINO-error recovery and false-accept rescue summary.

Class-conditional oracle metrics, both-direction recovery, detailed error correlation,
the supervised OpenCLIP visual head, and shared-encoder head diversity are optional
appendix diagnostics. They are not RQ1 gates.

This analysis diagnoses classifier complementarity but is not a gate for the learned
risk study. High disagreement between two weak predictors is not useful
complementarity, while limited fusion rescue does not preclude useful failure ranking.

## Domain-OOF Failure Risk Estimation

Create source records in three distinct protocols. Sample-OOF splits within domains;
domain-OOF holds out one complete capture domain and is primary for MCIO; attack-OOF
holds out one attack family and is primary for SiW-M downstream-unseen evaluation.
A mixed domain/attack gate is secondary. Predictor fitting and branch calibration use
only the allowed remainder with subject/video-safe disjoint partitions.

The held-out fold provides separate scientific-attribution and operational features:

$$
z_{science}(x)=[\widehat p_D,\widehat p_V,d_{abs}(x),q(x)],
$$

$$
z_{oper}(x)=[\widehat p_D,\widehat p_V,d_{abs}(x),m_F(x),q(x)].
$$

where $d_{abs}(x)=|\widehat p_D-\widehat p_V|$ is fixed before experiments and
$m_F(x)=p_F(x)-\tau_{ref}$ is the signed operational margin for
$p_F=(\widehat p_D+\widehat p_V)/2$. The vector $q(x)$ contains fixed image-quality
features. Entropy, branch
energy, hard/log-odds disagreement, and Mahalanobis are ablations or baselines rather
than primary features. Version 1 preregisters logistic regression with fixed regularization as the
primary failure-risk estimator; nested pseudo-domain selection is a secondary
sensitivity analysis. For target $T$, no sample from $T$ trains, selects, or calibrates
any component. The primary VLM checkpoint, preprocessing, crop, and prompt bank are
fixed a priori and identical in every fold. Candidate search is a secondary robustness
study performed only after the core analysis is frozen.

Bounded $\widehat p_D$, $\widehat p_V$, and $d_{abs}$ are never standardized. Only
quality features are standardized with statistics from the final allowed source
fitting partition; those same frozen statistics transform target quality features. A domain-ID
classifier audits whether risk features encode OOF fold identity. High domain
predictability is reported diagnostically and motivates only source-predefined
feature-removal or normalization sensitivities. It never changes the preregistered
primary RQ1 feature set after any target evaluation. Domain predictability is not alone
proof of leakage because genuine shift signals may also predict domain.

For OOF fold $k$, select $\tau_{ref}^{(k)}$ using only that fold's allowed remainder
and define policy-relative labels and margins:

$$
g_{ref}^{(k)}(x)=\mathbf{1}[p_F^{(k)}(x)\ge\tau_{ref}^{(k)}],\qquad
m_F^{(k)}(x)=p_F^{(k)}(x)-\tau_{ref}^{(k)}.
$$

At target inference use source-only $\tau_{ref}^{final}$ and
$m_F^{target}=p_F-\tau_{ref}^{final}$. This exposes policy-relative confidence despite
fold-specific thresholds. Because $m_F$ algebraically reveals the fold threshold when
paired with both probabilities, it is excluded from scientific $\Delta_{CF}$ and
$\Delta_{dis}$ models and contributes only to operational $\Delta_{margin}$. The final
post-VLM rule is not selected at EER.
Learned fusion remains an ablation. The primary model outputs a failure-risk score
$r_{err}(x)$ for the event $g_{ref}(x)\neq y$. Equal pseudo-domain weighting means this
score is not assumed to equal a deployment posterior probability. It may be described
as an estimate of $P(g_{ref}(x)\neq y\mid z_{oper}(x),\tau_{ref})$ only if held-out
source Brier, NLL, and reliability checks support calibrated-probability wording.
Transfer to other APCER policies is an ablation; policy-specific models are optional
and must be trained source-only.
Failure risk is not interpreted as a generic OOD or unknownness score.

Every risk estimator is evaluated against the same labels
$e(x)=\mathbf{1}[g_{ref}(x)\neq y]$. Complete DINO-only and dual-foundation selective
systems are compared in a separate table because they change both prediction and risk.
Reserve a subject/video-disjoint source-only gate-calibration partition $G_{domain}$
before any fitting. Exclude it from branch/head fitting, branch calibration, fusion
selection, risk fitting, and preregistration statistics. Frozen base predictors produce
genuinely out-of-sample features there; select only the post-VLM gate threshold on it
and never refit either base models or risk gate. All compared methods use the same
reduced source data. Fully cross-fitted thresholding is a future data-efficiency
alternative; attack-OOF uses its separate known-attack-only $G_{attack}$.

Before target evaluation, report non-interpolated prediction-error AP, AUROC, Brier score, and the
risk-coverage curve of the frozen OOF-trained gate on final-model predictions from
$G_{domain}$. This validity check cannot tune gate parameters. Its nonzero sanity
threshold is derived from source pseudo-shifts and frozen before held-out evaluation;
failure blocks OOF-risk transfer claims even if a threshold can still be selected.

Raw and independently calibrated disagreement remain mandatory baselines. Absolute
probability difference is primary; JS, hard decision disagreement, and log-odds
difference are ablations. The learned calibrator is useful
only if it generalizes beyond MSP, entropy, energy, and ordinary learned score fusion.
Because JS and entropy are deterministic transforms of branch probabilities, compare
capacity-matched logistic and MLP baselines using probabilities alone, probabilities
plus JS, and the same image-quality features. Also compare DINO embedding Mahalanobis
confidence as a representation-space baseline.
The fixed quality vector is $q(x)=$ [blur, mean luminance, contrast, face-area ratio,
detector confidence]. Report primary domain-OOF and matched sample-OOF $R_{DVd}$ both
with and without $q$ in the visible RQ1 attribution result. If only `+q` improves,
interpret the mechanism as transferable nuisance/failure signatures rather than
cross-foundation disagreement. Compare both OOF strategies on identical final target
predictions, and quantify OOF-to-full-source feature drift using
mean/standard-deviation shifts and KS distance.

All primary risk models use fixed-regularization logistic regression. The exact
feature sets are $R_q=[q]$, $R_D=[\widehat p_D,q]$,
$R_V=[\widehat p_V,q]$, $R_{DV}=[\widehat p_D,\widehat p_V,q]$,
$R_{DVd}=[\widehat p_D,\widehat p_V,d_{abs},q]$, and
$R_{DVdm}=[\widehat p_D,\widehat p_V,d_{abs},m_F,q]$.
Risk fitting averages unweighted BCE equally across pseudo-domains while retaining
natural error prevalence within each domain. Class-weighted/focal variants are ranking
ablations called risk scores, not calibrated failure probabilities.

Stage-2 risk metrics use only
$\mathcal D_{risk}=\{x:\text{face detector succeeds}\}$ because branch features do
not exist after detector failure. End-to-end security and coverage use all original
transactions. Report detector-failure rates separately for attacks and bona fide.

## Decision and conditional inference

The core system is always-on dual inference followed by one selective gate: the fixed
$g_{ref}$ produces the PAD decision and the risk score chooses only `accept` or
`abstain`. Conditional routing is an optional deployment extension with a separate
gate:

1. **Core selective gate:** after always-on dual inference, gate the fixed
   $g_{ref}$ decision using its risk score.
2. **Optional routing gate:** DINO confidence decides whether to emit a confident
   spoof as terminal non-accept or invoke the VLM for every other detector-successful
   sample.

The scalar risk score does not choose among DINO, VLM, and fusion. The primary routing
policy is spoof-only early exit: DINO samples beyond a source-selected confident-spoof
margin become terminal non-accepts; every other detector-successful sample invokes the
VLM. Select the routing threshold on source-only validation under the same finite-sample
error accounting. Direct-live exit and symmetric routing are ablations and cannot use
held-out target data.

This distinction avoids claiming that disagreement can route a request before the VLM
has run. Always-on dual inference is the compute-unconstrained reference under fixed
$g_{ref}$, not an accuracy upper bound; conditional inference is evaluated against it
at fixed APCER, fixed BPCER, and matched coverage.

The primary deployment objective is maximum coverage subject to a source-selected
security constraint such as $APCER\leq\alpha$, with
$\alpha\in\{0.5\%,1\%,5\%\}$. Report achieved target APCER rather than implying that
an unseen target is guaranteed to satisfy the source constraint.
Compare pooled-source and worst-source constrained threshold selection. Target ROC
operating points are reported only as post-hoc diagnostics and are never described as
deployable source-only policies.

## Optional evidence extension

Only after the two primary research questions pass their criteria, evaluate:

- DINO patch deletion/insertion and context sensitivity;
- coarse VLM concept contributions;
- a small, manually audited cue set;
- semantic distillation to a compact production head.

Named micro-forensic cue maps, learned ontology edges, synthetic cue interventions,
and consistency losses are not part of version 1.
