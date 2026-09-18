# Project Charter

## Objective

Build a single-frame RGB PAD model that is:

1. accurate under unseen capture domains and attack instruments;
2. able to preserve complementary visual and semantic inductive biases;
3. able to estimate failure risk from source-only out-of-fold predictions and abstain;
4. practical enough to deploy without a large generative VLM on every request.

## Intended contribution

Working title:

> Source-Only Failure-Risk Estimation for Selective Face Presentation Attack Detection with Heterogeneous Foundation Models

Use `Disagreement` in the title only if explicit disagreement adds capacity-matched
gain. If heterogeneous risk transfer does not beat same-family diversity, reframe as
a selective-ensemble PAD study rather than making a heterogeneous-foundation claim.

The contribution must be the tested source-only reliability mechanism on held-out
domains, not the choice of two pretrained backbones or disagreement by itself. No
labeled MICO target may influence candidate, checkpoint, threshold, or feature
selection for its fold:

1. intentionally independent DINOv2-Reg and fixed OpenCLIP ViT-B/16 predictors;
2. source-only cross-fitted failure-risk estimation from heterogeneous predictors;
3. selective inference evaluated with target-blind security, usability, and coverage
    accounting.

Fusion rescue is a separate classifier claim. Explicit disagreement is a secondary
attribution claim. Conditional routing and its compute trade-off are optional follow-up
work and cannot determine whether the core paper proceeds.

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

- improves prediction-error AUPR under unseen shifts over margin, MSP/entropy,
    representation-space confidence, sample-OOF, and capacity-matched learned-risk
    baselines;
- improves selective security-usability over the same baselines without hiding
    attack or bona-fide harm through aggregate coverage;
- exceeds the strong frozen DINOv2-Reg plus plain-DINOv2 same-family control at the
    risk-transfer and selective endpoints used for the heterogeneous-foundation claim;
- retains the improvement across at least three random seeds;
- uses a positive lower confidence bound for the paired four-target macro gain, at
    least three of four positive target estimates, and a preregistered harm tolerance.

Realized fusion rescue is required only for a classifier-improvement claim. Explicit
disagreement must beat a capacity-matched nonlinear probability-only model to enter
the title. Routing must show a compute benefit only if an optional routing claim is
retained.

An improvement on one in-domain split is insufficient.

## Feasibility verdict

The minimum study is feasible on one RTX 4080 16 GB because both foundation backbones
remain frozen and are run sequentially. The primary DINO head uses fixed class-token
plus mean-patch pooling, so frozen pooled features can be cached; only small PAD heads,
affine calibrators, and logistic risk models are fitted repeatedly. Learned attention
pooling is a secondary ablation that requires fold-safe patch-token caching. The
expected heavy work is dataset preparation, storage/I/O, and repeated split-safe
evaluation, not simultaneous GPU memory. The primary scope excludes full fine-tuning,
large generative MLLMs, learned cue ontologies, and counterfactual generation.

The main feasibility blocker is dataset access and independent subject/video counts.
If official source partitions cannot support disjoint head validation, branch
calibration, and gate calibration, simplify the operational threshold experiment
before target evaluation; do not silently reuse a partition.

## Constraints

- Input at inference is exactly one RGB image.
- Video datasets may supply independent frames, but no temporal feature is used.
- The primary VLM is fixed globally as OpenCLIP `ViT-B-16` with
    `laion2b_s34b_b88k` weights, native 224-pixel preprocessing, the immutable generic
    core prompt bank, and the preregistered context crop. It is not selected per fold.
- For target $T$, every fitted component and threshold uses only the other three MICO
    source domains. The complete target domain is strict outer-domain-unseen until
    final evaluation. Pipeline debugging uses synthetic data or source-only folds,
    never a labeled MICO pilot target.
- Dataset licenses and biometric-data restrictions take precedence over convenience.
- Q3 publication is a target, not a guarantee; venue quartiles change by year/category.

## Threat model

The initial threat model covers attacks presented to a conventional RGB camera:

- printed face photographs;
- replayed face images or videos on a display;
- paper, partial, silicone, latex, or rigid masks when represented in the data.

It excludes adversarial perturbations, morphing, identity verification errors, and
purely digital deepfakes in the first study.
