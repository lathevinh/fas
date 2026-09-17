# Proposed Method

## Design principle

For image $x$, two predictors are trained independently:

$$p_D=f_D(x), \qquad p_V=f_V(x).$$

The method does not align their features and does not minimize
$D_{JS}(p_D,p_V)$. Their different pretraining objectives and natural error diversity
are the signal under study. Each branch raw logit is calibrated exactly once on source
validation data before disagreement is computed:

$$
\widehat p_D=\sigma(\ell_D/T_D),\qquad
\widehat p_V=\sigma(\ell_V/T_V),\qquad
d(x)=D_{JS}(\widehat p_D\|\widehat p_V).
$$

Temperature scaling is the primary $\operatorname{Cal}_D$ and
$\operatorname{Cal}_V$; no second calibrator is stacked afterward. Uncalibrated JS
remains a mandatory ablation. Calibration parameters are fit without target data and
frozen before target evaluation.

## DINO visual predictor

DINOv2-Reg returns patch, class, and register tokens:

$$
D(x)=\{d_1,\ldots,d_N,d_{cls},d_{reg}^1,\ldots,d_{reg}^R\}.
$$

The minimum implementation concatenates the class token with attention-pooled patch
features and trains binary PAD plus optional attack-family heads. Registers remain
internal context tokens and are not treated as spatial heatmaps.

This branch is called a visual or forensic predictor because its dense self-supervised
features can retain local texture. The name does not assert that every patch activation
is a verified physical forensic cue.

Training order:

1. pretrained `dinov2_vitb14_reg4`, frozen backbone, train prediction heads;
2. compare DINOv2 without registers as an ablation;
3. add LoRA/adapters to the last four blocks only after the frozen kill experiment;
4. do not full-fine-tune in the first implementation.

## VLM semantic predictor

A frozen OpenCLIP/SigLIP-style model uses an immutable binary core prompt bank
$T_{core}=T_{live}\cup T_{spoof}$ with generic live and artificial-presentation
wording. For each class $c$:

$$
s_c(x)=\frac{1}{|T_c|}\sum_{t\in T_c}\cos(v(x),e_t),\qquad
\ell_V(x)=s_{spoof}(x)-s_{live}(x),\qquad
\widehat p_V(x)=\sigma(\ell_V(x)/T_V).
$$

Temperature $T_V$ is fitted on source calibration data. Mean cosine is the primary
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
2. fit only temperature $T_V$ on source calibration data;
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
- class-conditional oracle APCER, BPCER, and ACER;
- DINO-error recoverable fraction and DINO false-accept rescue rate;
- both directional recovery rates as descriptive diagnostics;
- error correlation by domain and attack family.

This analysis is a gate before any learned reliability component. High disagreement
between two weak predictors is not useful complementarity.

## Source-only risk calibration

Create out-of-fold source records in two variants. Sample-OOF splits within each
source domain using subject/video-safe partitions. Domain-OOF holds out one complete
source domain or attack family as a pseudo-shift. Predictor training, prompt selection,
and score calibration for a fold use only the remaining source data. Within that
remainder, branch fitting, prompt selection, and probability calibration use disjoint
train/validation partitions. Domain-OOF is the primary protocol; sample-OOF is a less
stressful ablation.

The held-out fold provides features and error labels for the reliability model:

$$
z_{primary}(x)=[\widehat p_D,\widehat p_V,d_{abs}(x),q(x)],
$$

where $d_{abs}(x)=|\widehat p_D-\widehat p_V|$ is fixed before experiments and
$q(x)$ is a fixed image-quality vector. Entropy, branch
energy, hard/log-odds disagreement, and Mahalanobis are ablations or baselines rather
than primary features. Version 1 preregisters logistic regression with fixed regularization as the
primary failure-risk calibrator; nested pseudo-domain selection is a secondary
sensitivity analysis. Target-domain samples never train, select, or calibrate this
model.

Continuous OOF features are normalized using statistics from the corresponding
source-side fitting/calibration partition before held-out prediction. A domain-ID
classifier audits whether risk features encode OOF fold identity. High domain
predictability triggers feature-removal and normalization ablations, but is not alone
proof of leakage because genuine shift signals may also predict domain.

Correctness labels are defined for the deterministic post-VLM rule
$g_{ref}(x)=\mathbf{1}[(\widehat p_D+\widehat p_V)/2\ge\tau_{ref}]$, not at EER.
Learned fusion remains an ablation. The main calibrator estimates
$r_{err}(x)=P(g_{ref}(x)\neq y\mid z(x),\tau_{ref})$. Transfer to other APCER
policies is an ablation; policy-specific calibrators are optional and must be trained
source-only.
Failure risk is not interpreted as a generic OOD or unknownness score.

Every risk estimator is evaluated against the same labels
$e(x)=\mathbf{1}[g_{ref}(x)\neq y]$. Complete DINO-only and dual-foundation selective
systems are compared in a separate table because they change both prediction and risk.
Reserve a subject/video-disjoint source-only gate-calibration partition before fitting
the final gate. Fit the fixed logistic gate once on the remaining OOF records, select
its accept threshold on the untouched partition, and do not refit afterward. Meta-OOF
thresholding is a sensitivity analysis because a subsequent refit can change score scale.

Raw and independently calibrated disagreement remain mandatory baselines. Absolute
probability difference is primary; JS, hard decision disagreement, and log-odds
difference are ablations. The learned calibrator is useful
only if it generalizes beyond MSP, entropy, energy, and ordinary learned score fusion.
Because JS and entropy are deterministic transforms of branch probabilities, compare
capacity-matched logistic and MLP baselines using probabilities alone, probabilities
plus JS, and the same image-quality features. Also compare DINO embedding Mahalanobis
confidence as a representation-space baseline.
The fixed quality vector is $q(x)=$ [blur, mean luminance, contrast, face-area ratio,
detector confidence]. Report risk with and without $q$. Compare sample-OOF and
domain-OOF gates on identical final target predictions, and quantify OOF-to-full-source
feature drift using mean/standard-deviation shifts and KS distance.

## Decision and conditional inference

There are two separate gates:

1. **Routing gate:** DINO confidence and image quality decide whether to accept a
   high-confidence DINO result or invoke the VLM.
2. **Selective gate:** after VLM invocation, the fixed $g_{ref}$ produces the PAD
   decision and calibrated risk chooses only `accept` or `abstain`.

The scalar risk score does not choose among DINO, VLM, and fusion. Security-asymmetric
routing, where confident spoof predictions can exit earlier and live predictions use
a stricter threshold, is compared with symmetric confidence routing.

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

Only after the three primary research questions pass their kill criteria, evaluate:

- DINO patch deletion/insertion and context sensitivity;
- coarse VLM concept contributions;
- a small, manually audited cue set;
- semantic distillation to a compact production head.

Named micro-forensic cue maps, learned ontology edges, synthetic cue interventions,
and consistency losses are not part of version 1.
