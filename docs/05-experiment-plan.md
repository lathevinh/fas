# Experiment and Implementation Plan

## Stage 0: Audit and infrastructure, weeks 1-2

Tasks:

- obtain datasets and archive their agreements;
- verify every official protocol and label mapping;
- implement manifests, leakage checks, metrics, and deterministic frame sampling;
- compare the exact settings of TIFS 2024 Evidential Semantic Consistency,
  Confidence Aware Learning, RPSR-FAS, DINO-VPT, and primitive-driven prompting;
- freeze the literature table and search for newer overlapping work.
- preregister the finite VLM candidate set and create versioned
  `configs/prompts_core_v1.yaml`, `configs/prompts_aux_v1.yaml`, and
  `configs/vlm_checkpoint_v1.yaml` artifacts before confirmatory evaluation. Record
  exact strings, classes, weights, text preprocessing, checkpoint/weights, tokenizer,
  resolution, interpolation, and normalization.
- freeze core prompts before pilot labels. Among committed checkpoint/preprocessing
  candidates under the pre-label latency ceiling, choose the one with lowest pilot
  ACER for calibrated-average fusion at the source-selected operating threshold.
  Candidates within 0.1 percentage point tie by lower median batch-1 latency, then
  lexical configuration ID. Do not choose among metrics after pilot inspection.

Exit criteria:

- no subject/video leakage;
- independently reproducible split counts;
- APCER/BPCER/ACER tests pass on synthetic examples.
- core prompts are frozen before pilot labels; the selected checkpoint/preprocessing
  artifact is frozen after pilot selection and before confirmatory MICO targets.

## Stage 1: Complementarity kill experiment, weeks 3-5

Train under identical sampling:

1. DINOv2-Reg with a frozen backbone and trained PAD head;
2. frozen CLIP/SigLIP with a preregistered fixed prompt bank; source-tuned prompts are
  a transfer-sensitivity ablation;
3. raw score average as a diagnostic;
4. calibrated score average as the principal simple-fusion baseline;
5. regularized learned score fusion using calibrated source scores.

Add two diagnostic controls without changing the proposed architecture:

6. a shared-encoder DINO head-diversity control using independent video bootstraps,
   augmentation streams, initialization, and small nonlinear heads;
7. a source-supervised linear PAD head on the same frozen CLIP/SigLIP image encoder.
8. frozen DINOv2 without Registers paired with DINOv2-Reg as the required stronger
  same-family control when retaining a cross-foundation title.

The first is a minimum homogeneous-diversity control but may underestimate ensembles
with independent representations. The third is therefore required for the
cross-foundation-specific confirmatory claim, while the CLIP visual control isolates prompt-driven versus
source-supervised adaptation on one VLM encoder; it does not alone prove that text
semantics causally produced any gain.
Match source labels, subject/video splits, head capacity, augmentation budget, crop
geometry, and calibration protocol across DINO and CLIP visual-head controls.
The DINOv2-Reg + plain-DINOv2 strong control and heterogeneous pair use identical
one-stage affine branch calibration, calibrated-average fusion, operating-point
selection, denominators, and bootstrap units.

Cache each branch independently so they never need to share GPU memory. Designate one
MICO target in advance as the pilot/development target for pipeline debugging. It is
not confirmatory evidence after inspection-driven changes. Freeze the Stage 1
configuration before evaluating the remaining three confirmatory targets, then report
the joint correctness table, double-fault, oracle gain, error correlation, and
attack/domain subgroups separately for pilot and confirmatory results.

Before opening any confirmatory MICO target labels, use domain-OOF source pseudo-shifts to lock
numeric continuation thresholds for recoverable error fraction
$REF_{VLM}=P(V\text{ correct}\mid D\text{ wrong})$ and potential false-accept rescue
$FARR_{VLM}=P(V\text{ blocks attack}\mid D\text{ false accepts})$. Also report
realized $REF_g=P(g_{ref}\text{ correct}\mid D\text{ wrong})$ and
$FARR_g=P(g_{ref}\text{ blocks attack}\mid D\text{ false accepts})$. Store the signed
preregistration with the run configuration; target results cannot redefine it.

Interpret `target labels` here as confirmatory-target labels after the pilot is
preregistered. The pilot may select only within the previously committed candidate set
and is permanently excluded from confirmatory statistics.

Also preregister the heterogeneity advantage
$\Delta_{hetero}=N_{FA}^{-1}\sum_i(r_i^V-r_i^H)$ on the same DINO false accepts,
with paired subject/video bootstrap and McNemar-style analysis when event counts are
small. Report both potential-branch and realized-fusion paired versions. If the strong
DINOv2 same-family comparison is not positive on confirmatory targets, weaken the
cross-foundation claim even when the broader selective ensemble remains useful.

Report complementarity lift relative to each second branch's standalone correctness
as a strength-adjusted diagnostic. Do not use it as a kill criterion: the subtraction
can penalize a uniformly strong branch and does not identify a causal source of diversity.
Also report normalized double fault
$NDF=P(E_D=1,E_B=1)/(P(E_D=1)P(E_B=1))$ overall and attack-conditionally. It is a
descriptive strength-normalized diagnostic, not a kill criterion, and must include
uncertainty because it is unstable when either marginal error rate is small.

Preregister a minimum DINO false-accept count $N_{min}$ and a 95% lower confidence
bound requirement $LCB_{95\%}(FARR_g)>\gamma$, both chosen from source pseudo-shifts.
If low-APCER pseudo-shifts yield too few false accepts, estimate complementarity at a
preregistered higher diagnostic APCER while retaining low-APCER points for deployment.

Define oracle gain on thresholded decisions using balanced accuracy/error and at
source-selected biometric operating points. Do not report an `oracle AUC` unless a
label-independent score construction is specified; choosing the correct branch per
sample uses ground-truth labels and does not define a deployable ROC score.
Report class-conditional oracle APCER, BPCER, and ACER; bootstrap by video or subject,
not by frame.

Exit criteria:

- both branches are competent enough for meaningful comparison;
- **Level 1, continue dual branch:** competent branches and realized $REF_g/FARR_g$
  pass preregistered confidence-bound criteria;
- **Level 2, retain cross-foundation claim:** paired $\Delta_{hetero}>0$ against the
  stronger DINOv2-Reg plus DINOv2 control;
- no target data influenced model selection.

Stop the dual-foundation direction if Level 1 fails. DINOv2 without Registers is
required only to retain the cross-foundation title; supervised backbones, LoRA, and
larger VLMs remain later ablations.

## Stage 2: Source-only risk calibration, weeks 6-8

Calibrate each branch independently on source validation data before computing the
primary absolute-difference disagreement and its JS ablation.
Then generate out-of-fold source records in two variants.

### Sample-OOF ablation

1. split within each source domain using subject/video-safe partitions after removing $G_{domain}$;
2. train/select both predictors using only the remainder;
3. calibrate each branch independently and predict held-out samples;
4. select fold-safe $\tau_{ref}^{(k)}$ on the allowed remainder and record correctness,
   probabilities, operational margin $m_F^{(k)}$, image quality, and disagreement;

### Domain-OOF primary MICO protocol

1. hold out one complete source capture domain after removing $G_{domain}$;
2. train/select both predictors using only the remainder;
3. fit one-stage monotone affine branch calibration on a disjoint, domain-balanced
  validation partition within the remainder;
4. select $\tau_{ref}^{(k)}$ only on the allowed remainder, then predict the held-out
  fold with margin $m_F^{(k)}=p_F^{(k)}-\tau_{ref}^{(k)}$;
5. repeat all folds and concatenate records;
6. train the preregistered fixed-regularization logistic failure-risk calibrator for
  calibrated-average $g_{ref}$;
7. generate out-of-sample predictions on permanent gate-calibration $G_{domain}$,
   which was excluded from every prior fit and selection step;
8. select the accept threshold on $G_{domain}$ and do not refit any component afterward.

Use $G_{domain}$ in MICO and a separate known-attack-only $G_{attack}$ in SiW-M.
Neither holdout selects routing thresholds or unrelated ablation policies.

Stratify $G_{domain}$ by source domain, class, and attack family where possible; report its
total, attack, error, and false-accept counts before claiming threshold stability.

Run attack-OOF separately for SiW-M using held-out attack families. A domain-OOF-only
gate cannot support an attack-shift calibration claim; mixed OOF is secondary.

Leave probabilities/disagreement unstandardized; normalize only fixed quality features
with final allowed source-fitting statistics reused at target time. Audit OOF domain
identifiability. Nested pseudo-domain hyperparameter selection is secondary because
three source domains provide a weak meta-validation sample.

Compare raw/calibrated JS, absolute difference, hard disagreement, and log-odds
difference against fused MSP/entropy and learned risk on fixed $g_{ref}$ predictions.
Include $-|p_F-\tau_{ref}|$ as the primary simple operational-margin risk baseline;
branch-specific operational margins are secondary.
Add capacity-matched LogReg/MLP probability baselines with and without each explicit
disagreement feature and the same fixed image-quality vector. DINO embedding
Mahalanobis confidence is a strong simple
representation-space baseline, not a substitute for reproducing a published
confidence-aware FAS method when its implementation and protocol are available.

Use two distinct result tables. The risk-estimator table holds $g_{ref}$ and its error
labels fixed for fused MSP/entropy, JS, Mahalanobis, and learned risk scores. Report
error prevalence and paired within-target deltas. The end-to-end system table may
compare DINO-only, shared-encoder DINO head diversity, DINO plus CLIP visual head, semantic VLM, and
conditional dual systems because it explicitly measures combined classifier and risk
changes.

Report $\Delta_{dis}$ between capacity-matched models with and without the primary
absolute-difference feature. If it adds no repeatable gain to a nonlinear model already
receiving both probabilities and quality, reframe the method as cross-foundation
selective failure prediction and remove algorithmic emphasis on disagreement.
Freeze $R_q=[q]$, $R_D=[\widehat p_D,q]$, $R_V=[\widehat p_V,q]$,
$R_{DV}=[\widehat p_D,\widehat p_V,q]$,
$R_{DVd}=[\widehat p_D,\widehat p_V,d_{abs},q]$, and
$R_{DVdm}=[\widehat p_D,\widehat p_V,d_{abs},m_F,q]$. Define
$\Delta_{CF}^{AUPR}=AUPR(R_{DV})-\max(AUPR(R_D),AUPR(R_V))$ and
$\Delta_{dis}^{AUPR}=AUPR(R_{DVd})-AUPR(R_{DV})$ as scientific claim quantities,
and $\Delta_{margin}^{AUPR}=AUPR(R_{DVdm})-AUPR(R_{DVd})$ as an operational gain.
All use the same fixed-regularization logistic family and source lineage. Primary risk
fitting uses equal pseudo-domain weighting with unweighted BCE inside each domain;
class-weighted/focal ranking losses are labeled non-probabilistic ablations.

Exit criteria:

- prediction-error AUPR, the primary failure-detection endpoint, improves consistently
  over single-model uncertainty;
- excess-AURC, the primary selective endpoint, improves at matched class coverage;
- **Level 3, retain disagreement claim:** preregistered $\Delta_{dis}>0$;
- no target sample or statistic enters calibration.
- Brier/NLL and reliability diagrams support any probabilistic `calibrated risk`
  wording; otherwise describe the output only as a failure-risk score.

## Stage 3: Selective and conditional inference, weeks 9-11

Implement in this order:

1. always-on DINO + VLM reference under fixed $g_{ref}$;
2. fixed post-VLM fusion $g_{ref}$ followed by accept/abstain risk gating;
3. spoof-only early-exit routing using a DINO operational margin selected on separate
  branch validation to minimize VLM invocation subject to preregistered source BPCER
  or $BFNR_{end2end}$ increase $\le\beta$;
4. symmetric and direct-live routing only as security-bounded ablations;
5. optional semantic distillation after the upper bound is established.

Do not add the next component unless the current comparison is understood.

Exit criteria:

- classifier comparisons (DINO, VLM, calibrated average, learned fusion) and
  fixed-$g_{ref}$ risk-score comparisons are reported separately;
- explicit disagreement beats capacity-matched no-disagreement risk baselines or the
  framing is weakened as preregistered;
- conditional inference approaches always-on security/selective performance at fixed
  APCER, fixed BPCER, and matched coverage;
- VLM invocation rate or GPU-ms/request decreases materially at matched operating points;
- mean/P50/P95 latency exposes the sequential hard-case penalty against parallel
  always-on inference;
- downstream-unseen and open-vocabulary zero-shot results are reported separately;
- attack/bona-fide coverage, covered errors, and end-to-end false acceptance use
  explicit denominators under the $K=1$ transaction policy;
- direct-DINO and VLM-invoked routes separately report transaction count, false
  accepts, bona-fide non-accepts, detector failures, and abstentions before end-to-end
  totals over the original denominator;
- shared wrong predictions are explicitly analyzed.

## Stage 4: Full open-world evaluation, weeks 12-14

- compute the primary confirmatory macro over the three untouched MICO targets;
- report all four MICO folds descriptively with the pilot labeled development-only and
  excluded from confirmatory inference;
- run SiW-M leave-one-attack-out;
- run external mask transfer when licensing permits;
- stratify results by sensor, illumination, attack instrument, and image quality;
- inspect worst false accepts and false rejects.

For each target and seed, train and score independently; never pool seed predictions
unless deploying an ensemble. Report mean/standard deviation of seed-level metrics and
subject/video bootstrap within each seed, with no $t$-test at $n=3$ and no best-seed
selection. A confirmatory delta passes only when its three-target macro mean is
positive, at least two of three target point estimates are positive, no target exceeds
a preregistered harm tolerance, and at least two of three seeds have positive
three-target macro deltas. Claims are limited to the evaluated confirmatory domains.

## Stage 5: Secondary representation ablations, weeks 15-16

Only after Stages 1-4 pass:

- DINOv2 versus DINOv2-Reg;
- class token versus attention-pooled patches;
- face versus context crop;
- frozen versus LoRA-tuned branches;
- optional patch deletion/insertion analysis;
- optional coarse semantic concept analysis.

Named cue ontology, cue pseudo-labeling, and counterfactual synthesis require a
separate go/no-go decision and are not assumed in the first paper.

## Stage 6: Deployment and paper package, weeks 17-20

- freeze configs and final checkpoints;
- rerun main tables from clean manifests;
- complete statistical tests and confidence intervals;
- prepare evidence maps with quantitative tests, not cherry-picked examples;
- document failures and negative ablations;
- report parameters, FLOPs, peak memory, latency, throughput, VLM invocation rate,
  and coverage at fixed security operating points;
- update the literature search immediately before submission.

## Core ablation matrix

| ID | DINO | VLM | Fusion/risk method | Conditional VLM | Abstain |
|---|---:|---:|---|---:|---:|
| A | Yes | No | DINO uncertainty | No | Optional |
| B | No | Yes | VLM uncertainty | No | Optional |
| C | Yes | Yes | Raw average | No | No |
| D | Yes | Yes | Calibrated average | No | No |
| E | Yes | Yes | Learned fusion of calibrated scores | No | No |
| F | Yes | Yes | Raw JS disagreement | No | Yes |
| G | Yes | Yes | Calibrated JS, sample-OOF | No | Yes |
| H | Yes | Yes | Source-only risk calibrator, domain-OOF | No | Yes |
| I | Yes | On demand | Domain-OOF calibrator | Yes | Yes |
| J | Yes | Distilled | Domain-OOF calibrator | No | Yes |
| K | Two heads | No | Shared-encoder head-diversity control | No | No |
| L | Yes | CLIP visual head | Calibrated average | No | No |
| M | Reg + plain DINOv2 | No | Strong same-family calibrated average | No | No |

## Initial compute plan

- MVP: one RTX 4080 16 GB, frozen backbones, mixed precision, sequential feature caching.
- Adapter stage: start with batch-size reduction and gradient accumulation; larger
  hardware is optional rather than assumed.
- Full evaluation: parallelize seeds/targets; do not reduce protocol coverage to
  finance unnecessary full fine-tuning.

Indicative starting values, to be selected on source validation only:

```yaml
dino_checkpoint: dinov2_vitb14_reg4
dino_input_size: 448
dino_tuning: frozen
vlm_family: openclip_or_siglip
vlm_text_encoder: frozen
vlm_image_tuning: frozen
head_lr: 3.0e-4
adapter_lr: 3.0e-5
weight_decay: 0.05
frames_per_video_per_epoch: 3
```
