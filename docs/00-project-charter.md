# Project Charter

## Objective

Build a single-frame RGB PAD model that is:

1. accurate under unseen capture domains and attack instruments;
2. able to expose localized forensic and structured semantic evidence;
3. calibrated enough to abstain when its evidence branches conflict;
4. practical enough to deploy without a large generative VLM on every request.

## Intended contribution

Working title:

> Dual-Evidence Consistency Learning for Reliable Open-World Single-Image Face PAD

The contribution must be the tested mechanism, not the choice of two pretrained
backbones:

1. a forensic branch that extracts localized physical artifacts from DINOv2-Reg;
2. a semantic branch that represents material, geometry, and attack concepts;
3. ontology-guided evidence consistency plus disagreement-aware selective prediction.

## Primary outputs

- a reproducible training and evaluation codebase;
- normalized metadata manifests without redistributing restricted datasets;
- pretrained research checkpoints where licenses permit;
- cross-domain, unseen-attack, calibration, faithfulness, and efficiency results;
- a journal manuscript with explicit negative and failure results.

## Success criteria

The approach is worth a model-centric paper only if it:

- beats DINOv2-Reg and learned score fusion on multiple unseen domains;
- improves unknown-attack/error detection using branch disagreement;
- produces evidence that passes intervention and deletion tests;
- retains the improvement across at least three random seeds;
- offers a deployable DINO-only or distilled-semantic configuration.

An improvement on one in-domain split is insufficient.

## Constraints

- Input at inference is exactly one RGB image.
- Video datasets may supply independent frames, but no temporal feature is used.
- Target-domain labels cannot select checkpoints, prompts, thresholds, or hyperparameters.
- Dataset licenses and biometric-data restrictions take precedence over convenience.
- Q3 publication is a target, not a guarantee; venue quartiles change by year/category.

## Threat model

The initial threat model covers attacks presented to a conventional RGB camera:

- printed face photographs;
- replayed face images or videos on a display;
- paper, partial, silicone, latex, or rigid masks when represented in the data.

It excludes adversarial perturbations, morphing, identity verification errors, and
purely digital deepfakes in the first study.
