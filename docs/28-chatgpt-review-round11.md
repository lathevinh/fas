# ChatGPT Research Review — Round 11: Implementation Readiness

Date: 2026-09-17

This review evaluates the repository after `27-review-response-round10.md`.

## Overall assessment

The protocol-design phase is mature enough.

I agree with the Round-10 response that additional architecture variants should **not** be introduced before empirical evidence exists.

However, the repository is **not yet at an executable preregistration state**.

The current tree still contains only:

- documentation;
- literature references.

It does not yet contain the promised:

- `configs/`;
- prompt YAML files;
- VLM candidate list;
- pilot identity artifact;
- manifest generator;
- split manifests;
- permanent holdout manifests;
- seed list;
- metric tests;
- Stage-0 audit outputs.

Therefore the next scientific risk is no longer a missing idea.

It is a gap between:

\[
\text{protocol described in prose}
\]

and:

\[
\text{protocol enforced by executable artifacts}.
\]

The next milestone should be **implementation freeze**, not another architecture review.

---

# 1. Do not open pilot labels before the preregistration artifacts actually exist

The experiment plan says the project will commit:

```text
configs/prompts_core_v1.yaml
configs/prompts_aux_v1.yaml
configs/vlm_checkpoint_v1.yaml
```

and a finite VLM candidate set before pilot inspection.

These files are not yet present in the repository.

The exact prompt strings are also not present as a frozen artifact.

Therefore the statement:

> core prompts are frozen before pilot labels

is currently only an intention.

## Minimum hard gate before pilot inspection

The repository should contain, at minimum:

```text
configs/
    prompts_core_v1.yaml
    prompts_aux_v1.yaml
    vlm_candidates_v1.yaml
    pilot_selection_v1.yaml
    preprocessing_v1.yaml
    seeds_v1.yaml

manifests/
    dataset_summary.csv
    split_summary.csv
```

and an immutable Git commit should record them before any pilot result is inspected.

If pilot labels have already been inspected before this commit exists, the paper should not later describe these choices as preregistered.

---

# 2. The pilot dataset identity itself must be committed

The protocol repeatedly states:

> designate one MICO target in advance as the pilot/development domain.

But the current dossier does not name that dataset.

This remains a major degree of freedom.

After looking at preliminary training difficulty, the team could otherwise choose whichever dataset is most convenient as the development domain.

## Recommendation

Before any MICO target result is viewed, commit:

```yaml
pilot_domain: <exact dataset>
confirmatory_domains:
  - <dataset>
  - <dataset>
  - <dataset>
```

The pilot domain is then permanently development-only.

The remaining three form the confirmatory macro.

---

# 3. The finite VLM candidate set is not enough; every candidate needs an immutable ID

The selection rule is now deterministic:

> lowest pilot ACER under a latency ceiling, ties by latency and then lexical config ID.

Good.

But lexical config ID is meaningful only if the IDs and configurations are frozen beforehand.

Each candidate should record:

- model family;
- exact checkpoint/pretrained-weight identifier;
- input resolution;
- crop mode;
- normalization;
- tokenizer/text preprocessing;
- precision;
- inference backend.

For example:

```yaml
candidates:
  - id: clip_vit_l14_336_xxx
    checkpoint: ...
    resolution: 336
    crop: context_1p30
    precision: fp16
```

Do not allow a candidate to change preprocessing after pilot inspection while retaining the same ID.

---

# 4. Pilot candidate selection also needs a fixed DINO reference

Checkpoint selection is based on pilot ACER of:

\[
\text{DINO}+\text{VLM calibrated average}.
\]

But the result can change with:

- DINO seed;
- DINO head initialization;
- source sampling randomness.

Therefore VLM candidate selection is not deterministic unless the DINO side of the pilot comparison is also frozen.

## Recommendation

Before pilot labels, define either:

### Option A — one fixed selection checkpoint

Use one preregistered DINO seed/checkpoint only for VLM candidate selection.

### Option B — fixed seed average

Select candidates by the mean over a preregistered seed set.

Do not choose the VLM candidate using whichever DINO seed makes it look best.

This selection-only DINO policy can differ from the final three-seed confirmatory reporting, but it must be fixed in advance.

---

# 5. The latency ceiling needs an exact measurement protocol

The VLM candidate rule includes a pre-label latency ceiling.

The numerical ceiling and measurement conditions are not yet specified.

Latency can vary substantially with:

- GPU;
- driver;
- CUDA/PyTorch version;
- precision;
- warm-up;
- batch size;
- synchronization;
- image preprocessing;
- host-to-device transfer.

## Recommendation

Freeze a latency protocol such as:

```yaml
device: RTX_4080_16GB
batch_size: 1
precision: fp16
warmup_runs: 50
timed_runs: 500
cuda_synchronize: true
include_preprocessing: true
statistic: median
latency_ceiling_ms: <number>
```

Without this, "under the latency ceiling" is not reproducible.

---

# 6. The current novelty text overstates the evaluation as simultaneous domain and attack shift

The novelty document currently says the method is validated under:

> simultaneous PAD domain and attack shift.

But the primary protocols are:

- MICO **domain-OOF** for domain shift;
- SiW-M **attack-OOF** for attack-family shift.

These evaluate two shift types separately.

The mixed domain-plus-attack gate is explicitly secondary.

Therefore the main evidence does not yet establish simultaneous domain-and-attack shift.

## Recommendation

Change the unconditional wording to:

> operational validation under PAD domain shifts and attack-family shifts.

If the final paper wants:

> simultaneous domain and attack shift,

it must add a protocol where both dimensions are unseen together.

For example:

\[
\text{unseen capture domain}
+
\text{unseen attack family}
\]

in the same target evaluation.

Do not imply this from two separate experiments.

---

# 7. RQ2 still says "Target data never train, select, or calibrate either model"

This is too broad after adopting a pilot domain.

The project now explicitly permits one target domain to select the global VLM checkpoint/preprocessing from a committed candidate set.

The statement is correct only for **confirmatory targets**.

## Recommendation

Rewrite:

> Confirmatory-target data never train, select, or calibrate any model, threshold, prompt, or risk gate. The preregistered pilot domain is development-only and excluded from confirmatory inference.

This should be used consistently in:

- RQ2;
- method;
- abstract/manuscript claims later.

---

# 8. The three claim deltas still need minimum effect-size criteria

The project has clean estimands:

\[
\Delta_{\text{hetero}},
\]

\[
\Delta_{CF}^{AUPR},
\]

\[
\Delta_{dis}^{AUPR}.
\]

But current success logic is still mainly:

\[
\Delta>0.
\]

A tiny positive value such as:

\[
0.0002
\]

should not justify a title-level novelty claim.

## Recommendation

Before confirmatory labels, preregister either:

### Minimum meaningful effects

\[
\Delta_{\text{hetero}}\ge\delta_H,
\]

\[
\Delta_{CF}^{AUPR}\ge\delta_{CF},
\]

\[
\Delta_{dis}^{AUPR}\ge\delta_{dis}.
\]

or:

### Confidence-bound criterion

Require the paired lower confidence bound to exceed zero or a small practical threshold.

The thresholds may be chosen from:

- source pseudo-shifts;
- pilot evidence;

but must freeze before confirmatory evaluation.

The FARR criterion already uses an LCB concept; the title-level delta claims should receive equally strong treatment.

---

# 9. Use the claim hierarchy as a hierarchical testing sequence

The repository already has three logical levels:

1. continue the dual-foundation system;
2. retain the cross-foundation claim;
3. retain the explicit-disagreement claim.

This naturally defines a hierarchical evidence sequence.

## Recommended order

### Level 1

Test realized source-only rescue:

\[
REF_g,\quad FARR_g.
\]

If Level 1 fails, stop the model-centric direction.

### Level 2

Only if Level 1 passes, test:

\[
\Delta_{\text{hetero}}.
\]

If it fails, reframe as selective ensemble PAD.

### Level 3

Only if Levels 1-2 pass, test:

\[
\Delta_{dis}^{AUPR}.
\]

If it fails, use:

> Cross-Foundation Selective Failure Prediction

rather than disagreement-centered wording.

This hierarchy reduces the risk of mining multiple related endpoints until one becomes positive.

---

# 10. The OOF-to-final-model mismatch still needs an executable sanity gate

The risk gate is trained using predictions from OOF models.

At final inference, branch predictions come from a different model trained on all allowed:

\[
Source\setminus G.
\]

The permanent \(G_{domain}\) threshold set partially addresses this by giving genuinely out-of-sample final-model predictions.

However, selecting a threshold on \(G_{domain}\) cannot repair a failure in **risk ranking**.

If the OOF-trained gate learns the wrong feature-error relationship for the final predictors, threshold adjustment alone is insufficient.

## Recommendation

Before target evaluation, compute on \(G_{domain}\):

- prediction-error AUPR;
- AUROC;
- Brier score;
- risk-coverage curve.

This is not for tuning gate parameters.

It is a preregistered **validity check**.

For example:

> if final-model risk AUPR on \(G_{domain}\) falls below a source-preregistered sanity threshold, do not claim the OOF risk mapping transfers to the deployed source model.

The gate threshold may still be selected on \(G_{domain}\), but the ranking validity should also be reported.

---

# 11. Detector failures define a different evaluation population for Stage 2

Detector failure is correctly mapped to:

\[
\text{terminal non-accept}.
\]

But when the face detector fails, the system has no:

\[
\widehat p_D,\widehat p_V,d_{abs},m_F
\]

for the risk model.

Therefore Stage-2 risk-estimator metrics necessarily apply only to:

\[
\text{detector-success samples}.
\]

End-to-end security metrics apply to all transactions.

## Recommendation

State explicitly:

### Risk-model population

\[
\mathcal D_{\text{risk}}
=
\{x:\text{face detector succeeds}\}.
\]

All:

- error AUPR;
- \(\Delta_{CF}\);
- \(\Delta_{dis}\);
- AURC;

are evaluated on this population.

### End-to-end population

All original transactions, including detector failures.

Also report:

\[
P(\text{detector failure}\mid attack)
\]

and:

\[
P(\text{detector failure}\mid bona\ fide).
\]

This prevents difficult detector-failure attacks from disappearing from the apparent reliability results.

---

# 12. Permanent split roles should be assigned globally per dataset

For reproducibility, source roles should not be re-randomized independently every time a dataset appears as a source in a different MICO fold.

A cleaner implementation is to create one immutable per-dataset subject/video partition.

For each dataset:

```text
train pool
branch-calibration pool
gate-calibration candidate pool
routing-validation pool
```

Then when that dataset acts as a source, use the same subject/video role assignment.

When it acts as a target, use its official target protocol and do not use those source-role partitions.

## Benefit

This makes role lineage auditable across all four MICO folds and prevents accidental reuse caused by independent per-experiment splitting.

Publish hashes of every manifest.

---

# 13. The actual split-count budget must be computed before the permanent holdouts are frozen

The protocol now requires:

- source train;
- branch calibration;
- OOF held-out folds;
- \(G_{domain}\);
- routing validation;
- sometimes strong-control training;
- three seeds.

For small datasets such as MSU-MFSD, these partitions may become statistically weak.

The prose protocol cannot establish feasibility.

## Required Stage-0 table

For every dataset report:

| Dataset | subjects | bona videos | attack videos | train | branch calib | G | routing val |
|---|---:|---:|---:|---:|---:|---:|---:|

Also stratify attack videos by family/instrument where possible.

Then compute whether each partition contains enough independent attack events for:

- affine calibration;
- low-APCER threshold selection;
- FARR estimation;
- gate calibration.

If not, simplify the split design **before pilot labels**, rather than changing it after observing results.

---

# 14. Freeze the random seed IDs, not only the number of seeds

The plan says at least three random seeds and prohibits best-seed reporting.

Good.

But if seeds are not fixed, researchers can run many and later report an arbitrary three.

## Recommendation

Commit before confirmatory evaluation:

```yaml
seeds:
  - 20260917
  - ...
  - ...
```

Every primary method/control uses the same seed list where meaningful.

Failed runs must be documented rather than silently replaced unless a preregistered failure rule applies.

---

# 15. Bootstrap clustering must be dataset-specific and frozen

The current protocol says:

> bootstrap by subject/video.

That is still ambiguous.

If one subject contributes several correlated videos, video bootstrap underestimates dependency.

If subject IDs are unavailable/reliable only in some datasets, subject bootstrap may not be possible everywhere.

## Recommendation

Create a dataset-level bootstrap config:

```yaml
OULU-NPU: subject
CASIA-FASD: subject
Replay-Attack: subject_or_video
MSU-MFSD: subject
SiW-M: subject
```

using the strongest valid clustering unit supported by official metadata.

Do not select the bootstrap unit after seeing which gives narrower confidence intervals.

---

# 16. The strong same-family comparison needs an identical first-branch anchor

The heterogeneity comparison is defined on:

> the same DINO false accepts.

Therefore the primary DINO branch must literally be the same fitted DINOv2-Reg predictor for both pairs:

\[
(DINO_{\text{Reg}},VLM)
\]

and:

\[
(DINO_{\text{Reg}},DINO_{\text{plain}}).
\]

Do not independently retrain the anchor DINO for each pair.

Otherwise the false-accept denominator changes and the paired rescue comparison is no longer truly paired.

The implementation should cache one anchor prediction file per:

- target;
- seed;
- configuration.

Both second-branch rescue analyses must consume that same file.

---

# 17. The pilot selection metric must recompute source-selected thresholds per candidate

The candidate rule uses pilot ACER for calibrated-average fusion at a source-selected operating threshold.

For candidate VLM \(V_j\), its calibrated fusion distribution differs.

Therefore each candidate needs its own threshold:

\[
\tau_j
\]

selected only from its allowed source data.

Do not select one threshold using the best candidate and reuse it across all candidates.

The selection pipeline should be:

\[
V_j
\rightarrow
\text{source calibration}
\rightarrow
\tau_j
\rightarrow
\text{pilot ACER}_j.
\]

This must be automated before pilot scores are viewed.

---

# 18. "Source-calibrated score" requires an implementation test for monotonicity

The calibrator is:

\[
\widehat p=\sigma(a\ell+b),
\qquad
a>0.
\]

The positivity constraint is central because it preserves score ordering.

The implementation must enforce it rather than assume it.

A robust parameterization is:

\[
a=\operatorname{softplus}(\theta)+\epsilon.
\]

Add a unit test verifying:

\[
\ell_1<\ell_2
\Rightarrow
\widehat p(\ell_1)<\widehat p(\ell_2).
\]

Also test:

- finite outputs;
- calibration reproducibility;
- source-domain weighting.

This is a small implementation detail but an important reproducibility guarantee.

---

# 19. The project should not claim "simultaneous shift" without a joint protocol

This deserves repeating because it affects novelty wording.

Current main evidence supports:

\[
\text{domain shift}
\]

and:

\[
\text{attack-family shift}
\]

in separate experimental tracks.

That is already valuable.

Until a joint target is constructed, use:

> robust under domain and attack-family shifts

rather than:

> simultaneous domain and attack shift.

A joint protocol can remain future work.

---

# 20. The next review should reject further prose-only expansion

The Round-10 response itself correctly says that the next review should contain:

- manifests;
- split counts;
- holdout counts;
- candidate hashes;
- first pilot outputs.

I agree.

Therefore after this synchronization pass, another response that only edits `docs/*.md` without adding executable artifacts should not be considered meaningful progress.

## Minimum next-review package

The next pull should contain some combination of:

```text
configs/
src/ or scripts/
tests/
manifests/
results/stage0/
```

with at least:

- exact prompt YAML;
- pilot domain;
- candidate VLM configs;
- seed IDs;
- split counts;
- independent attack-video counts;
- G/routing-validation counts;
- manifest hashes;
- calibration test;
- first Stage-1 branch predictions or pilot table.

---

# Recommended final synchronization fixes before implementation

1. replace "simultaneous domain and attack shift" with separate-shift wording unless a joint protocol is added;
2. change RQ2's "target data never..." to "confirmatory-target data never...";
3. preregister minimum meaningful effects or confidence-bound criteria for \(\Delta_{\text{hetero}},\Delta_{CF},\Delta_{dis}\);
4. make the three claim levels explicitly hierarchical;
5. add a preregistered OOF-to-final risk validity check on \(G_{domain}\);
6. explicitly condition Stage-2 risk metrics on detector success;
7. freeze global per-dataset subject/video role manifests;
8. compute partition/event-count feasibility before freezing holdouts;
9. commit exact seed IDs and bootstrap units;
10. use one identical anchor DINO predictor for heterogeneous and same-family paired rescue;
11. recompute source-selected pilot threshold independently for every VLM candidate;
12. implement and test the \(a>0\) calibration constraint;
13. stop prose-only review after these fixes and move to executable Stage 0/1 artifacts.

---

# Final recommendation

The conceptual protocol is ready.

The repository itself is not yet experimentally ready because the protocol is still represented almost entirely by prose.

The next scientific milestone should be:

\[
\boxed{
\text{prose protocol}
\rightarrow
\text{versioned executable protocol}
}
\]

The most important evidence on the next pull is not another equation.

It is a table of real counts such as:

\[
N_{\text{subjects}},
N_{\text{videos}},
N_{\text{attacks}},
N_G,
N_{\text{false accepts}}
\]

and immutable configuration hashes showing that the intended lineage can actually be executed on the available datasets.

If those counts reveal that the current number of holdouts/calibration partitions is infeasible, simplify the protocol before pilot inspection.

That is now a more valuable research decision than adding any new model component.
