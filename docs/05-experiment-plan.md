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
2. frozen CLIP/SigLIP with source-selected prompt ensemble and temperature;
3. fixed score average;
4. regularized learned score fusion.

Cache each branch independently so they never need to share GPU memory. Run one
MICO target first, selected before observing results, then construct the joint
correctness table and report $P_{cc},P_{cw},P_{wc},P_{ww}$, double-fault, oracle gain,
error correlation, and attack/domain subgroups.

Exit criteria:

- both branches are competent and neither simply dominates every subgroup;
- oracle gain over the better branch is non-negligible;
- both $P_{cw}$ and $P_{wc}$ are non-trivial;
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
3. calibrate each branch independently on validation data within the remainder;
4. predict the held-out source fold and record the same features;
5. repeat all folds and concatenate records;
6. train a small regularized failure-risk calibrator;
7. freeze it before target evaluation.

Compare raw JS disagreement and the calibrator against MSP, entropy, energy, branch
ensembles, and ordinary learned fusion.

Exit criteria:

- target error/unknown AUROC and AUPR improve consistently over single-model uncertainty;
- selective risk improves at matched coverage;
- no target sample or statistic enters calibration.

## Stage 3: Selective and conditional inference, weeks 9-11

Implement in this order:

1. always-on DINO + VLM upper bound;
2. disagreement-aware accept/retry policy;
3. DINO-confidence routing that calls the VLM only for uncertain samples;
4. post-VLM selective fusion or retry;
5. optional semantic distillation after the upper bound is established.

Do not add the next component unless the current comparison is understood.

Exit criteria:

- calibrated disagreement beats learned fusion and entropy/MSP/energy;
- conditional inference approaches always-on security/selective performance at fixed
  APCER, fixed BPCER, and matched coverage;
- VLM invocation rate or latency decreases materially at matched operating points;
- true-unknown and open-vocabulary-unknown results are reported separately;
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

| ID | DINO | VLM | Fusion/risk method | Conditional VLM | Retry |
|---|---:|---:|---|---:|---:|
| A | Yes | No | DINO uncertainty | No | Optional |
| B | No | Yes | VLM uncertainty | No | Optional |
| C | Yes | Yes | Fixed average | No | No |
| D | Yes | Yes | Learned score fusion | No | No |
| E | Yes | Yes | Raw JS disagreement | No | Yes |
| F | Yes | Yes | Calibrated JS, sample-OOF | No | Yes |
| G | Yes | Yes | Source-only risk calibrator, domain-OOF | No | Yes |
| H | Yes | On demand | Domain-OOF calibrator | Yes | Yes |
| I | Yes | Distilled | Domain-OOF calibrator | No | Yes |

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
