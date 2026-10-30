# 325 - Review of324 and completed paper319: close experiments and finish the paper

Date: 2026-10-30.
Reviewed commit: `afe2e03d29378dbd1c6457c78e3514f2411a3e90`.
Result: [324](324-completed-comparison-results-and-paper-update.md).
Manuscript: [paper319](paper319/manuscript.md).
Prior review: [320](320-review-doc319-and-paper319-preparation-and-manuscript.md).

## Verdict

**Accept the completed bounded comparison, public numerical reporting and
results-complete manuscript as the basis for final editorial work. Close the
scientific package. No result-changing error was found in the inspected code
and public evidence. Do not launch another model, fusion or calibration campaign
to improve the outcome.**

This accepts the experiment and its bounded negative/mixed conclusions. It
does not accept the systems as operationally successful or guarantee journal
acceptance. The remaining work is a standalone paper, reproducibility summary
and venue selection, rather than another experiment-direction proposal.

## What has actually finished

All four declared target populations, three training seeds and four systems
are complete:12 fitted contexts and48 primary system/target/seed cases.
Training uses only the allowed official source training/development roles;
the fourth dataset's declared test population supplies evaluation. The four
systems are DINO-Reg, supervised CLIP, fixed equal two-DINO and matched-input
DeepPixBiS architecture retraining. The latter updates its feature extractor;
the foundation branches remain frozen. This is not a causal architecture test
or reproduction of the specialist paper's exact recipe.

Target evaluation includes2943 originals,2929 successful images and14 technical
failures. Each original contributes the accepted single middle frame.
Three seeds reuse the same targets and are not three independent test sets.
SiW remains the disclosed video-grouped local intersection with unknown
participant identities. No new foundation-encoder inference was required.

The initial321 startup failed before fitting because historical DenseNet
checkpoint names required compatibility conversion.322 then exceeded its
combined context budget.323 records an explicitly approved operational
continuation: four complete contexts and one completed specialist checkpoint
are retained. The final cumulative inventory is39 frozen-head starts,
12 specialist starts and52 calibrators, including three/four disclosed recovery
refits. Specialist work remains600 epochs/74400 optimizer steps. Nothing in
those operational stops is negative PAD evidence. The reported9.07-hour323
wall time does not include all prior work and must not become a total-cost claim.

## Main numerical answer

At the primary empirical objective, FA<=5% and BFA>=50%:

| Outcome | Cases /48 |
|---|---:|
| Source-derived policy meets both constraints |0|
| Source-derived policy meets FA alone |15|
| Same fixed scores admit a joint-utility oracle threshold |21|
| Same fixed scores remain oracle-infeasible |27|

Oracle thresholds use evaluation labels.21 attainable cases mean that these
scores have retrospective operating headroom, not that an available policy
has recovered it. The27 failures are specific low-FA score limitations on
the observed samples, not impossibility results for all embeddings or heads.

Useful equal-seed mean contrasts, in percent:

| Target /system | AUROC | Source-policy FA | Source-policy BFA | Oracle BFA at5% FA |
|---|---:|---:|---:|---:|
|OULU /DINO-Reg|87.77|36.13|91.94|46.67|
|OULU /DeepPixBiS|91.98|15.12|81.11|58.70|
|CASIA /DINO-Reg|99.94|0.00|39.26|98.89|
|CASIA /DeepPixBiS|86.61|1.48|42.59|54.81|
|MSU /CLIP|89.22|9.17|65.00|57.50|
|MSU /two-DINO|92.67|22.78|92.50|68.33|
|SiW /CLIP|85.02|3.59|31.42|38.19|
|SiW /DeepPixBiS|76.00|49.82|87.36|23.75|

These are descriptive means, with per-seed intervals in the public products;
they are not pooled independent-replication estimates.

- CASIA supplies the clearest threshold-headroom example: near-perfect DINO
  ranking,0% observed policy FA, but only39.26% BFA versus98.89% oracle BFA.
  This motivates investigating threshold transfer but does not demonstrate
  a label-free remedy or zero population attack risk.
- On OULU, the specialist is oracle-attainable in all three seeds and the
  three frozen systems are unattainable in every seed. Its policy is still
  FA-unsafe. This is an informative counterexample to interpreting the
  earlier frozen-score failure as a limitation of every PAD method.
- MSU has heterogeneous oracle outcomes. CLIP's AUROC-minus-DINO-Reg
  conditional intervals all include zero; its higher descriptive oracle
  BFA is not a statistically established deployable-policy improvement.
- SiW has0/12 primary oracle-attainable cases. CLIP is FA-safe but accepts
  too few bona-fide observations. Retain the participant/coverage limitations.

OULU specialist-minus-DINO-Reg AUROC intervals are positive in all three seeds;
CASIA's are negative in all three. These conditional, unadjusted comparisons
support dataset-dependent behavior under the fixed recipes, not a universal
ranking or three independent confirmations.

Sensitivity is properly retained:1% gives0/48 policy joint successes and12/48
oracle successes;10% gives10/48 and42/48. Do not substitute10% for the failed
primary objective. Policy FA-safe counts can be nonmonotone because alpha
changes the source-derived threshold as well as the evaluation constraint.

## Verification and its limits

Exact-head [run40861764855](https://github.com/lathevinh/fas/actions/runs/40861764855),
[validate123406512621](https://github.com/lathevinh/fas/actions/runs/40861764855/job/123406512621)
shows success for all12 listed steps, including numerical regressions.
The reported594 local producer tests and GPU execution are separate evidence.

Independent checks on this host passed for all187 sealed implementation pins,
all five exported-product hashes, all144 public integer-budget/rate/feasibility
cases, all36 macro/worst-target summaries, all48 target/system/alpha summaries
and the published sensitivity totals. Four products were rebuilt byte-for-byte
from the public contexts: case CSV, interval CSV, summary CSV and primary tables.
Line endings were normalized to the Linux/Git convention for byte comparisons.

The normal local exporter-test import is unavailable because this host lacks
`threadpoolctl`. Three existing exporter tests instead passed using AST-extracted
actual exporter/aggregate/reconstruction functions, without importing the
private execution controller. This is partial functional verification, not
a full local suite, controller execution or GPU training test.

Public contexts omit individual scores and full grouped ROC arrays. Therefore
this review did not independently replay each real-data oracle from raw scores,
rerun the2000-draw bootstrap, inspect private approvals, reproduce checkpoints
or certify actual private resource observations. The public terminal and
verification bindings consistently report complete12-context no-fit checkpoint
reconstruction. That reconstruction is a separate producer process, not
external scientific replication by this reviewer. Use that wording in the
paper instead of an ambiguous claim of independent replication.

## Critique: what the paper can and cannot claim

### 1. The result applies to the declared source policy, not every source-only threshold strategy

The single common threshold is the minimum FA-safe source order statistic.
With small source supports this can be conservative. State the rule in the
main paper, not just a linked configuration.0/48 does not prove that every
threshold-transfer method, calibration strategy or PAD approach fails.

The saved primary limiting-source records provide useful context at no new
scientific cost: OULU's12 cases are limited by MSU in8 and SiW in4; CASIA's
by OULU in6, MSU in3 and SiW in3; MSU's by SiW in8 and OULU in4; SiW's
by MSU in6 and OULU in6. Include a compact explanation using these already
saved records. They identify the numerical bottleneck of this threshold rule,
not a causal explanation of dataset shift. No threshold redesign is required.

### 2. The specialist adds real context but is not a matched-capacity superiority test

The specialist makes the paper stronger by changing the OULU score diagnosis,
while its much worse CASIA/SiW results prevent an easy winner narrative.
Keep the stated researcher-fixed recipe, ImageNet initialization and source-only
selection. Different pretraining, augmentation, trainable capacity, input
resolution and compute preclude attributing the difference solely to frozen
versus adapted representations. A weak specialist result under this recipe
does not refute published DeepPixBiS results. Do not add a tuning campaign to
address this limitation; describe the actual contextual comparison accurately.

### 3. Paired intervals support limited comparisons, not a security certificate

The2000-draw pairing and known-subject/exact-frame grouping are appropriate
for the declared conditional analysis. Source-threshold estimation and training
uncertainty are conditioned out. Zero-error bootstrap intervals cannot bound
unseen attack risk, and SiW video-group resampling does not recover unknown
participant dependence.756 records include repeated metrics across alpha;
they are not756 independent statistical findings. Retain per-seed reporting,
no oracle intervals and the explicit multiplicity limitation.

### 4. Finish a scientific paper rather than preserve a project diary

320's principal requested repairs are now addressed: completed-study methods,
separate populations, paired source-policy/oracle tables, corrected references
and measured specialist results. Accept those repairs; do not ask for the
same work again.

The manuscript remains too centered on internal study numbers and historical
fusion bookkeeping. Lead with the completed four-system comparison and its
two observed failure modes. Move most historical309/314/316 inventories,
attempt histories and seal details to supplementary material. Keep the
development exposure and operational amendments transparently summarized.
Include the fixed specialist hyperparameters and resource/cost definition in
a standalone methods/supplement table so an outside reader need not navigate
project documents to reconstruct the comparison.

The candidate contribution is this controlled empirical evidence and
interpretation, not the ordinary ROC calculation or the statement that domain
shift exists. State one precise contribution paragraph and a short closest-work
comparison; avoid both unsupported novelty claims and repeated project-internal
disclaimers in every section. Dataset substitution and a large artifact count
are not novelty. Q3 acceptance is still an editorial assessment, not a score
threshold guaranteed by completed computation.

## Next deliverable and stopping rule

**No further scientific run is required by this review.** Finish one submission
draft from the existing results: reorganize the main comparison, summarize
the threshold-limiting evidence, move historical details to the supplement,
finalize references/author metadata and select a venue using verified
provider/year/category ranking and current author requirements. These are
editing and submission-preparation tasks, not a fresh experiment proposal.

Retain all48 primary cases and all unfavorable sensitivity results. Do not
alter the5%/50% criterion, choose a best seed, use target-label oracle thresholds
as operational results or add another system to obtain a favorable narrative.
Submission/payment remains a separate owner action, not implied by this review.

**Final disposition:324 completes the intended experiment and provides a
defensible bounded empirical result. Close the experiment, revise the paper
for readers outside the project, and proceed to a concrete submission draft.**
