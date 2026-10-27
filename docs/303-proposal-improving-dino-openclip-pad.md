# 303 - Proposal: improve DINO/OpenCLIP PAD without reusing observed targets

Date: 2026-10-27.
Motivation: accepted fixed locked-target results in [301](301-locked-target-package-and-fixed-evaluation.md)
and [review302](302-review-doc301-locked-target-results-and-final-claims.md).

## Status and decision boundary

**This is a research proposal only. It authorizes no data access, preprocessing,
training, prompt/threshold selection, target evaluation, freeze update or
resource expenditure.** The 301 analysis remains complete and immutable:
RQ1 is inconclusive; RQ2 is evidence against the registered heterogeneous
superiority claim. No result below retrospectively changes those outcomes.

The purpose is to define a small, falsifiable next study rather than start
another target-tuning loop on already observed data.

## Evidence motivating a new study

The fixed system has three separately frozen image encoders/branches:

- DINOv2 ViT-B/14 with registers (`dino_reg`), using concatenated CLS and
  mean-patch features with a source-trained linear head.
- Plain DINOv2 ViT-B/14 (`dino_plain`), with the same feature/head recipe.
- OpenCLIP ViT-B/16 LAION2B zero-shot prompt logits at native 224 resolution.

Each branch has its own source-fitted monotone calibration. The heterogeneous
system is the equal average of calibrated DINO-Reg and OpenCLIP probabilities;
the same-family comparator averages DINO-Reg and plain DINO probabilities.
The image encoders are frozen; this is not end-to-end joint training.

On the four observed targets, standalone OpenCLIP mean AUROC ranges from
.487 to .582, versus .840 to 1.000 for DINO-Reg. Registered heterogeneous
raw-AURC improvement is -.032897 (95% paired clustered CI
[-.055779, -.012521]); three of four target means favor same-family. RQ1's
domain-OOF minus matched-sample AP macro is -.019232 (CI
[-.039570, .009115]) with mixed target effects. These results argue against
assuming that a 50/50 probability fusion helps, but do not prove OpenCLIP is
universally useless or DINO universally superior.

There is a separate preprocessing concern. The saved shared face-context
crop can be rectangular (the inspected OULU example is 744x1013), then both
encoder branches are resized directly to square inputs (224x224 and 518x518).
That changes horizontal and vertical scale unequally. The 301 experiment used
the frozen pipeline consistently; this observation is a hypothesis about a
possible limitation, not evidence that it caused the target results.

## Proposed research question

Does a geometry-preserving face-context input and source-only branch selection
improve cross-dataset PAD error-risk ranking and operational utility on a
genuinely unseen target, relative to the frozen current pipeline?

The next paper should emphasize the observed limitations and the controlled
test of this question. It should not be framed as a repair of, or a new
positive interpretation for, 301.

## Proposed staged design

### A. Resolve the evaluation boundary first

The four 301 target datasets have already been inspected for target outcomes.
Further development on them is exploratory. In addition, OULU, CASIA and MSU
official-test members were assigned permanent source roles and were used as
sources in other outer-domain rotations. Therefore their prior target holdout
does not make them untouched evidence for a new preprocessing/fusion choice.
SiW's official-test intersection was excluded from source use, but its results
were also observed in 301; it is not an untouched target for revised-method
selection either.

Before any revised-method fitting, identify and pin either:

1. an independently licensed, genuinely unseen PAD dataset/release with a
   compatible binary endpoint and defensible capture/subject grouping; or
2. a prospective new capture/test cohort collected after the revised pipeline
   is locked.

Use only authorized official development/training partitions for source
selection and keep the new target labels/metrics inaccessible until the single
predeclared final evaluation. If no such target is available, publish the
next work explicitly as source-side/exploratory analysis, not independent
target confirmation. Do not silently relabel permanent source roles or reuse
the four observed targets as if they were untouched.

### B. Treat geometry as one controlled factor

Keep the current released preprocessing and its cached features as the exact
baseline. Create a versioned candidate that avoids independent horizontal/
vertical stretching:

- **Candidate G1 (preferred first comparison):** apply the pinned five-point
  similarity transform directly from the selected-frame landmarks to each
  model's square canvas, retaining the registered context scale, eye-centred
  rotation, RGB interpolation and border semantics.
- **Candidate G2 (secondary ablation only if specified in advance):** pad the
  rectangular shared crop to a square with a fixed, label-independent rule,
  then resize isotropically. Freeze the padding color/placement and handling
  of clipping before seeing model scores.

Direct alignment and padding alter context and pixel sampling differently.
Choose between them using source-only validation and image-usability checks;
do not choose the better-looking transform after opening target outcome
tables. Store dimensions, landmark geometry and branch lineage in per-image
records. A detector failure remains a terminal non-accept with the original
denominator retained. No image, frame, crop or identity is replaced.

### C. Make DINO the primary model and OpenCLIP a controlled comparator

For the first revised study, hold the image encoders frozen to limit
degrees of freedom. Compare a compact, preregistered set:

1. DINO-Reg alone.
2. Plain DINO alone.
3. The current equal calibrated DINO-Reg/OpenCLIP fusion, retained as a
   replication comparator under the new preprocessing.
4. A source-selected convex fusion of calibrated branch probabilities,
   including endpoints (DINO-only and CLIP-only), selected wholly inside
   nested source validation.

Select fusion weight, if any, using group-safe source-only inner folds,
optimizing the preregistered primary utility with a deterministic tie rule.
Report branch competence and calibration separately. If OpenCLIP fails the
predeclared source competence/support gate, retain its result but do not
silently promote a fusion that depends on it. Do not tune prompts on the
observed targets. Prompt tuning or CLIP fine-tuning, if later pursued, is a
separate higher-capacity study requiring its own source-only protocol and
untouched target.

### D. Evaluate ranking and operation separately

Preregister one primary risk-ranking endpoint and one primary operating-point
endpoint, with exact denominators, failure treatment, target/seed aggregation,
grouped uncertainty, minimum event support and claim decision rules. Keep
ranking coverage distinct from operational coverage. Select any operating
threshold using source data only and report target FA, BFNR, coverage and
technical failures with original class denominators. Do not interpret
source-constrained empirical FA as a target security guarantee.

Use paired subject/video cluster resampling within dataset, with shared
multiplicities across compared systems. Intervals describe conditional
uncertainty on the tested fitted systems; they are not retraining uncertainty
or a guarantee for all future domains. Make the new target a single locked
evaluation, with no follow-up prompt, crop, fusion-weight or threshold search.

## Analysis and publication plan

1. Publish a manifest of data rights, official splits, permanent study roles,
   sample/group counts, detector failures, image/crop hashes and preprocessing
   parameters. Explain official split versus cross-domain role explicitly.
2. Before training, freeze the candidate transform(s), encoder/checkpoint
   hashes, prompts, features, calibration, fusion-selection objective, risk
   models, exclusions, estimands, bootstrap and resource/stop rules.
3. Establish image geometry parity and independent spot checks without
   displaying target labels or outcome tables. Preserve every failed
   transaction in the denominator.
4. Fit/choose exclusively within source development data with nested
   group-safe splits. Keep subject/video and exact-frame derived components
   intact across every inner split.
5. Execute once on the predeclared unseen target. Publish all systems,
   targets, seeds, failures, negative/inconclusive results and code/data
   commitments. Do not call internal cross-validation an independent
   benchmark replication.
6. Report 301 as the prior fixed experiment and the new work as a separately
   specified study. Disclose the native closure serialization issue and make
   the additive readback verifier source inspectable in the reproducibility
   bundle; its digest alone is not source-level reproducibility.

## Expected contribution and limitations

The defensible contribution is an empirical account of (i) geometry-preserving
versus stretched face crops, (ii) DINO versus zero-shot OpenCLIP competence,
(iii) whether source-selected branch weighting adds value, and (iv) the gap
between source operating constraints and target FA/BFNR. This could support a
Q3 submission if the unseen evaluation, implementation provenance and
literature positioning are strong; journal quartile or acceptance cannot be
promised by this proposal.

Risks include the availability/licensing of a truly untouched target,
benchmark-specific attack/camera shifts, crop-context tradeoffs, small
group counts, detector failures, OpenCLIP prompt sensitivity, and the cost of
regenerating features for every candidate geometry. A result that favors
DINO-only or finds no geometry benefit is still reportable and must not trigger
post-hoc selection of a favorable target.

## Explicit non-actions

This proposal does not change `preprocessing_v3.yaml`, any original crop,
feature cache, model, threshold, role or result. It does not repair or
overwrite the 301 source freeze, repeat the four-target run, authorize
preprocessing/training, reserve a new target dataset, or claim that either
candidate will improve performance. Those require a separate reviewed,
preregistered package and explicit owner authority.
