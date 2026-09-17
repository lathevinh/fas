# Proposed Method

## Design principle

For image $x$, two predictors are trained independently:

$$p_D=f_D(x), \qquad p_V=f_V(x).$$

The method does not align their features and does not minimize
$D_{JS}(p_D,p_V)$. Their different pretraining objectives and natural error diversity
are the signal under study. Each branch is calibrated independently on source
validation data before disagreement is computed:

$$
\widehat p_D=\operatorname{Cal}_D(p_D),\qquad
\widehat p_V=\operatorname{Cal}_V(p_V),\qquad
d(x)=D_{JS}(\widehat p_D\|\widehat p_V).
$$

Uncalibrated JS remains a mandatory ablation. Calibration parameters are fit without
target data and frozen before target evaluation.

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

A frozen OpenCLIP/SigLIP-style model scores prompt ensembles for coarse concepts:

- bona fide or natural face;
- printed face or paper presentation;
- replayed face or display presentation;
- mask or artificial face.

Prompt scores are calibrated on source validation data and mapped to binary PAD and,
where supported, attack-family probabilities. Free-form generated rationales and
fine-grained concepts such as moire are outside the minimum implementation.

Training order:

1. freeze image and text encoders;
2. select prompt templates and temperature using source validation only;
3. compare fixed prompts with a small learned calibration/head;
4. consider image-encoder LoRA only if a frozen branch is competent but underfits;
5. keep the text encoder frozen to preserve its semantic space.

The VLM must remain independently useful. Fine-tuning both branches jointly on a
shared consistency loss is prohibited in the main method.

## Complementarity analysis

For each target sample, record whether each branch is correct and estimate
$P_{cc},P_{cw},P_{wc},P_{ww}$. Report:

- each branch's standalone performance;
- double-fault rate $P_{ww}$;
- oracle accuracy $1-P_{ww}$ and oracle gain over the better branch;
- two-sided recovery rates $P_{cw}$ and $P_{wc}$;
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
z(x)=[\widehat p_D,\widehat p_V,d(x),H(\widehat p_D),H(\widehat p_V),E_D,E_V,q(x)],
$$

where $H$ denotes entropy, $E$ optional energy scores, and $q(x)$ image-quality
features. A small regularized calibrator estimates failure risk $r(x)$. Target-domain
samples never train, select, or calibrate this model.

Correctness labels are defined under one preregistered source-selected reference
policy, not at EER. The main calibrator estimates
$r_{err}(x)=P(\hat y\neq y\mid z(x),\tau_{ref})$. Transfer to other APCER policies is
an ablation; policy-specific calibrators are optional and must be trained source-only.
Failure risk is not interpreted as a generic OOD or unknownness score.

Raw and independently calibrated JS disagreement remain mandatory baselines. The learned calibrator is useful
only if it generalizes beyond MSP, entropy, energy, and ordinary learned score fusion.
Because JS and entropy are deterministic transforms of branch probabilities, compare
capacity-matched logistic and MLP baselines using probabilities alone, probabilities
plus JS, and the same image-quality features. Also compare DINO embedding Mahalanobis
confidence as a representation-space baseline.

## Decision and conditional inference

There are two separate gates:

1. **Routing gate:** DINO confidence and image quality decide whether to accept a
   high-confidence DINO result or invoke the VLM.
2. **Selective gate:** after VLM invocation, cross-model disagreement and calibrated
   risk decide whether to fuse, accept one branch, or return `retry/abstain`.

This distinction avoids claiming that disagreement can route a request before the VLM
has run. Always-on dual inference is the accuracy upper bound; conditional inference
is evaluated against it at fixed APCER, fixed BPCER, and matched coverage.

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
