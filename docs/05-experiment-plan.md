# Experiment and Implementation Plan

## Stage 0: Audit and infrastructure, weeks 1-2

Tasks:

- obtain datasets and archive their agreements;
- verify every official protocol and label mapping;
- implement manifests, leakage checks, metrics, and deterministic frame sampling;
- freeze the literature table and search for newer overlapping work.

Exit criteria:

- no subject/video leakage;
- independently reproducible split counts;
- APCER/BPCER/ACER tests pass on synthetic examples.

## Stage 1: Strong baselines, weeks 3-5

Train under identical sampling:

1. supervised ResNet/ViT baseline;
2. DINOv2 without registers, frozen probe;
3. DINOv2-Reg, frozen probe;
4. DINOv2-Reg with adapters/LoRA;
5. frozen CLIP/SigLIP class-prompt baseline;
6. ordinary score fusion.

Run one MICO target first as the cheap discriminating experiment, then all four.

Exit criteria:

- DINOv2-Reg is competitive with published/reproduced baselines;
- results are stable across three seeds;
- no target data influenced model selection.

## Stage 2: Independent evidence, weeks 6-9

### Forensic branch

- train patch cue maps and global heads;
- supervise with official labels and controlled intervention masks;
- measure deletion/insertion and cue intervention response.

### Semantic branch

- finalize concept ontology and prompt ensembles;
- calibrate zero-shot scores;
- create and manually audit pseudo-labels;
- add image-encoder LoRA only if frozen features are inadequate.

Exit criteria:

- each branch exceeds its trivial baseline;
- branch errors are demonstrably non-identical;
- evidence tests are better than random and generic attention maps.

## Stage 3: Consistency, weeks 10-12

Implement in this order:

1. fixed score average;
2. learned score fusion;
3. decision consistency only;
4. evidence consistency with fixed ontology;
5. sparse learnable ontology;
6. counterfactual consistency;
7. disagreement-aware abstention.

Do not add the next component unless the current comparison is understood.

Exit criteria:

- full consistency beats learned fusion beyond uncertainty intervals;
- disagreement predicts errors better than entropy/MSP/energy;
- shared wrong predictions are explicitly analyzed.

## Stage 4: Open-world evaluation, weeks 13-15

- complete four-target MICO;
- run SiW-M leave-one-attack-out;
- run external mask transfer when licensing permits;
- stratify results by sensor, illumination, attack instrument, and image quality;
- inspect worst false accepts and false rejects.

## Stage 5: Deployment variants, weeks 16-17

Evaluate:

- full DINO + VLM upper bound;
- conditional VLM called only for uncertain DINO samples;
- DINO plus distilled semantic head;
- DINO-only fallback.

Report parameters, FLOPs, peak memory, latency, throughput, and coverage at a fixed
security operating point. Hardware and batch size must be stated.

## Stage 6: Paper package, weeks 18-20

- freeze configs and final checkpoints;
- rerun main tables from clean manifests;
- complete statistical tests and confidence intervals;
- prepare evidence maps with quantitative tests, not cherry-picked examples;
- document failures and negative ablations;
- update the literature search immediately before submission.

## Core ablation matrix

| ID | DINO forensic | VLM semantic | Ontology | Counterfactual | Abstention |
|---|---:|---:|---:|---:|---:|
| A | Yes | No | No | No | No |
| B | No | Yes | No | No | No |
| C | Yes | Yes | No, average | No | No |
| D | Yes | Yes | No, learned fusion | No | No |
| E | Yes | Yes | Fixed | No | No |
| F | Yes | Yes | Sparse learned | No | No |
| G | Yes | Yes | Sparse learned | Yes | No |
| H | Yes | Yes | Sparse learned | Yes | Yes |

## Initial compute plan

- MVP: one 24 GB GPU, frozen backbones, mixed precision, cached frozen embeddings.
- Adapter stage: one 24-48 GB GPU depending on VLM/input resolution.
- Full evaluation: parallelize seeds/targets; do not reduce protocol coverage to
  finance unnecessary full fine-tuning.

Indicative starting values, to be selected on source validation only:

```yaml
dino_checkpoint: dinov2_vitb14_reg4
dino_input_size: 448
dino_tuning: frozen_then_lora_last_4
vlm_family: openclip_or_siglip
vlm_text_encoder: frozen
vlm_image_tuning: frozen_then_optional_lora
head_lr: 3.0e-4
adapter_lr: 3.0e-5
weight_decay: 0.05
frames_per_video_per_epoch: 3
```
