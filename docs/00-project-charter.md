# Project Charter

## Objective

Build a single-frame RGB PAD model that is:

1. accurate under unseen capture domains and attack instruments;
2. able to preserve complementary visual and semantic inductive biases;
3. calibrated from source-only out-of-fold predictions to abstain on likely failures;
4. practical enough to deploy without a large generative VLM on every request.

## Intended contribution

Working title:

> Source-Only Calibrated Cross-Foundation Disagreement for Selective Single-Image Face PAD

The contribution must be the tested source-only reliability mechanism, not the
choice of two pretrained backbones or disagreement by itself:

1. intentionally independent DINOv2-Reg and VLM predictors;
2. cross-fitted disagreement calibration without target-domain labels;
3. selective and conditional inference evaluated as a security-coverage-latency trade-off.

Named forensic cue maps and ontology learning are optional follow-up work, not part
of the minimum viable paper.

## Primary outputs

- a reproducible training and evaluation codebase;
- normalized metadata manifests without redistributing restricted datasets;
- pretrained research checkpoints where licenses permit;
- cross-domain, unseen-attack, calibration, faithfulness, and efficiency results;
- a journal manuscript with explicit negative and failure results.

## Success criteria

The approach is worth a model-centric paper only if it:

- demonstrates non-trivial two-sided complementarity and oracle gain;
- beats DINOv2-Reg, VLM uncertainty, and learned score fusion on multiple unseen domains;
- improves unknown-attack/error detection over MSP, entropy, and energy baselines;
- retains the improvement across at least three random seeds;
- offers conditional VLM inference with a measured security-coverage-latency benefit.

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
