# Project Charter

## Objective

Build a single-frame RGB PAD model that is:

1. accurate under unseen capture domains and attack instruments;
2. able to preserve complementary visual and semantic inductive biases;
3. calibrated from source-only out-of-fold predictions to abstain on likely failures;
4. practical enough to deploy without a large generative VLM on every request.

## Intended contribution

Working title:

> Source-Only Cross-Foundation Failure-Risk Calibration for Selective Single-Image Face PAD

Use `Disagreement` in the title only if explicit disagreement adds capacity-matched
gain. If heterogeneous rescue does not beat same-family diversity, reframe as a
selective-ensemble PAD study rather than making a cross-foundation novelty claim.

The contribution must be the tested source-only reliability mechanism on held-out
domains, not the choice of two pretrained backbones or disagreement by itself. No
labeled MICO target may influence candidate, checkpoint, threshold, or feature
selection for its fold:

1. intentionally independent DINOv2-Reg and VLM predictors;
2. source-only cross-fitted failure-risk calibration from heterogeneous predictors;
3. selective and conditional inference evaluated as a security-coverage-compute trade-off,
   with latency distributions reported explicitly.

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

- demonstrates source-preregistered DINO-error and false-accept rescue plus class-conditional oracle gain;
- exceeds the strong frozen DINOv2-Reg plus plain-DINOv2 same-family control in
    paired security-useful rescue;
- demonstrates incremental value from explicit disagreement over capacity-matched
    probability-only risk models, or weakens the title as preregistered;
- beats DINOv2-Reg, VLM uncertainty, and learned score fusion on multiple unseen domains;
- improves prediction-failure detection under unseen shifts over MSP, entropy, energy,
  representation-space confidence, and capacity-matched risk baselines;
- retains the improvement across at least three random seeds;
- offers conditional VLM inference with a measured security-coverage-compute benefit.

An improvement on one in-domain split is insufficient.

## Feasibility verdict

The minimum study is feasible on one RTX 4080 16 GB because both foundation backbones
remain frozen and are run sequentially; image features are cached once per frozen
candidate, while only small PAD heads, affine calibrators, and logistic risk models are
fitted. The expected heavy work is dataset preparation and repeated split-safe
evaluation, not simultaneous GPU memory. The primary scope excludes full fine-tuning,
large generative MLLMs, learned cue ontologies, and counterfactual generation.

The main feasibility blocker is dataset access and independent subject/video counts.
If official source partitions cannot support disjoint head validation, branch
calibration, and gate calibration, simplify the operational threshold experiment
before target evaluation; do not silently reuse a partition.

## Constraints

- Input at inference is exactly one RGB image.
- Video datasets may supply independent frames, but no temporal feature is used.
- For target $T$, every selection decision uses only the other three MICO source
    domains through nested source-domain OOF. The complete target domain is strict
    outer-domain-unseen until final evaluation. Pipeline debugging uses synthetic data
    or source-only folds, never a labeled MICO pilot target.
- Dataset licenses and biometric-data restrictions take precedence over convenience.
- Q3 publication is a target, not a guarantee; venue quartiles change by year/category.

## Threat model

The initial threat model covers attacks presented to a conventional RGB camera:

- printed face photographs;
- replayed face images or videos on a display;
- paper, partial, silicone, latex, or rigid masks when represented in the data.

It excludes adversarial perturbations, morphing, identity verification errors, and
purely digital deepfakes in the first study.
