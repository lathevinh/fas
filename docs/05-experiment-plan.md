# Experiment and Implementation Plan

## Stage 0: Audit and infrastructure, weeks 1-2

Tasks:

- obtain datasets and archive their agreements;
- verify every official protocol and label mapping;
- implement manifests, leakage checks, metrics, and deterministic frame sampling;
- compare the exact settings of TIFS 2024 Evidential Semantic Consistency,
  Confidence Aware Learning, RPSR-FAS, DINO-VPT, and primitive-driven prompting;
- freeze the literature table and search for newer overlapping work.

Exit criteria:

- no subject/video leakage;
- independently reproducible split counts;
- APCER/BPCER/ACER tests pass on synthetic examples.

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

The first is a minimum homogeneous-diversity control but may underestimate ensembles
with independently tuned backbones; frozen DINOv2-Reg plus plain DINOv2 is the stronger
same-family follow-up when compute permits. The second isolates prompt-driven versus
source-supervised adaptation on one VLM encoder; it does not alone prove that text
semantics causally produced any gain.
Match source labels, subject/video splits, head capacity, augmentation budget, crop
geometry, and calibration protocol across DINO and CLIP visual-head controls.

Cache each branch independently so they never need to share GPU memory. Designate one
MICO target in advance as the pilot/development target for pipeline debugging. It is
not confirmatory evidence after inspection-driven changes. Freeze the Stage 1
configuration before evaluating the remaining three confirmatory targets, then report
the joint correctness table, double-fault, oracle gain, error correlation, and
attack/domain subgroups separately for pilot and confirmatory results.

Before opening any MICO target labels, use domain-OOF source pseudo-shifts to lock
numeric continuation thresholds for recoverable error fraction
$REF=P(D\text{ wrong},V\text{ correct})/P(D\text{ wrong})$ and false-accept rescue
rate $FARR=P(V\text{ blocks attack}\mid D\text{ false accepts})$. Store the signed
preregistration with the run configuration. Target results may test these criteria but
may not redefine them.

Also preregister the heterogeneity advantage
$\Delta_{hetero}=FARR(DINO,VLM)-FARR(DINO,DINO_2)$ with video/subject-clustered
uncertainty. If it is not positive on confirmatory targets, weaken the cross-foundation
claim even when the broader selective ensemble remains useful.

Preregister a minimum DINO false-accept count $N_{min}$ and a 95% lower confidence
bound requirement $LCB_{95\%}(FARR)>\gamma$, both chosen from source pseudo-shifts.
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
- class-conditional oracle gain passes the preregistered criterion;
- REF and security-critical FARR pass their preregistered criteria, even if recovery
  is asymmetric;
- no target data influenced model selection.

Stop the dual-foundation direction if these conditions fail. DINOv2 without registers,
supervised backbones, LoRA, and larger VLMs are later ablations, not prerequisites.

## Stage 2: Source-only risk calibration, weeks 6-8

Calibrate each branch independently on source validation data before computing JS.
Then generate out-of-fold source records in two variants.

### Sample-OOF ablation

1. split within each source domain using subject/video-safe partitions;
2. train/select both predictors using only the remainder;
3. calibrate each branch independently and predict held-out samples;
4. record correctness, probabilities, entropy, energy,
   image quality, and cross-model divergence;

### Domain-OOF primary protocol

1. hold out one complete source domain or attack family;
2. train/select both predictors using only the remainder;
3. calibrate each branch independently on a disjoint validation partition within the remainder;
4. predict the held-out source fold and record the same features;
5. repeat all folds and concatenate records;
6. train the preregistered fixed-regularization logistic failure-risk calibrator for
  calibrated-average $g_{ref}$;
7. reserve a subject/video-disjoint gate-calibration partition before final gate fit;
8. fit once on the remaining OOF records, select the accept threshold on the untouched
  partition, and do not refit before target evaluation.

Normalize fold features with source-side statistics and audit OOF domain
identifiability. Nested pseudo-domain hyperparameter selection is secondary because
three source domains provide a weak meta-validation sample.

Compare raw/calibrated JS, absolute difference, hard disagreement, and log-odds
difference against fused MSP/entropy and learned risk on fixed $g_{ref}$ predictions.
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

Exit criteria:

- prediction-error AUPR, the primary failure-detection endpoint, improves consistently
  over single-model uncertainty;
- excess-AURC, the primary selective endpoint, improves at matched class coverage;
- no target sample or statistic enters calibration.
- Brier/NLL and reliability diagrams support any probabilistic `calibrated risk`
  wording; otherwise describe the output only as a failure-risk score.

## Stage 3: Selective and conditional inference, weeks 9-11

Implement in this order:

1. always-on DINO + VLM reference under fixed $g_{ref}$;
2. fixed post-VLM fusion $g_{ref}$ followed by accept/abstain risk gating;
3. symmetric DINO-confidence routing;
4. security-asymmetric routing with a stricter direct-live threshold;
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
- shared wrong predictions are explicitly analyzed.

## Stage 4: Full open-world evaluation, weeks 12-14

- complete four-target MICO;
- run SiW-M leave-one-attack-out;
- run external mask transfer when licensing permits;
- stratify results by sensor, illumination, attack instrument, and image quality;
- inspect worst false accepts and false rejects.

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
