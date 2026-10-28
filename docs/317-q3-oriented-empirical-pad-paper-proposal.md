# 317 - Proposal: a bounded empirical PAD paper rather than another fusion search

Date: 2026-10-28

Status: **proposal for owner/reviewer critique only.** The owner requested
publication of the discussed direction, not execution of another study.
No new baseline, fitting, feature extraction, dataset download, target
evaluation or oracle-based policy selection is authorized by this document.
Accepted studies and their conclusions remain unchanged.

## 1. Recommendation and intended paper

Aim for a focused empirical paper about the operating transfer of frozen
foundation-model features for face presentation attack detection (PAD).
Do not make an unsupported improved-fusion claim or keep searching until a
positive result appears.

Provisional question:

> When frozen foundation-model PAD scores transfer across datasets, does
> useful low-false-acceptance performance transfer too, and can failure be
> attributed to threshold placement versus limited score separation?

Provisional title:

**Beyond AUROC: Operating-Point Transfer of Frozen Foundation Models for
Face Presentation Attack Detection**

The title is a working framing, not a verified novelty claim. A Q3-oriented
submission is a venue-fit objective, not an acceptance prediction or a
reason to lower scientific standards. Quartile must be checked against a
named ranking source, year and subject category.

## 2. What the completed evidence supports

| Evidence | Supported statement | Unsupported extension |
|---|---|---|
| [Readout309](309-source-only-cached-readout-results.md) | Supervised CLIP improves over the tested zero-shot readout, while operating transfer remains poor | Supervised CLIP is a new state of the art or necessarily useful at low FA |
| [Fusion314](314-nested-fusion-utility-results.md) and [Review315](315-review-report314-nested-fusion-infeasibility.md) | Matched nested DINO-CLIP and two-DINO selectors produce no feasible policies under the declared rule | Selected fusion loses by a measured margin, or all possible fusion is ineffective |
| [Oracle316](316-saved-score-oracle-threshold-diagnosis.md) | The tested fixed scalar scores have threshold headroom on CASIA but insufficient empirical low-FA separation on OULU | The embeddings or every possible head are incapable, or oracle thresholds are deployable |
| Represented-domain versus held-out-domain results | Strong represented-domain performance does not establish transfer | A causal explanation of domain shift or independent confirmation |

In316, primary OULU has0/54 attainable fixed-reference cases at attack
FA<=5% and bona-fide acceptance (BFA)>=50%; the best case reaches43.56% BFA.
CASIA has54/54 attainable cases. These are sample-specific oracle diagnostics
using evaluation labels, not source-selected operating results.

The proposed contribution is a controlled empirical comparison and a useful
failure diagnosis. Whether that contribution is sufficiently distinct from
prior work has **not yet been established**. Negative findings alone do not
make the paper publishable.

## 3. Stage A: establish novelty and venue fit before more computation

Prepare a targeted literature comparison covering:

1. Frozen self-supervised and vision-language features for PAD.
2. Cross-dataset PAD and its training/evaluation protocols.
3. Low-FA evaluation, threshold transfer and oracle operating diagnostics.

For the closest studies, record the exact protocol, training data, backbone
adaptation, decision-threshold rule, operating metrics, uncertainty treatment
and released code. Distinguish genuine differences from renamed metrics or
an ordinary ROC analysis.

Deliverable for critique: a short evidence table and a claim-to-prior-work
map, with verified primary references. No claim that the oracle algorithm
itself is novel is assumed.

Shortlist a small number of venues whose recent scope accommodates empirical
biometric evaluation. Verify current scope, ranking basis, fees and data/code
requirements. Do not select solely on a Q3 label or promise acceptance.

**Gate A:** proceed only if a defensible, venue-relevant gap can be stated.
If the nearest work already answers the same question convincingly, revise
the framing or stop before spending another experiment budget.

## 4. Stage B: specify one final supplementary package

Subject to Gate A, design one bounded package for separate review and explicit
execution approval. Candidate additions are below; this is not a ready-to-run
protocol and does not seal a baseline, dataset or numerical budget.

### B1. One specialist PAD comparator

Prefer one reproducible PAD-specific baseline outside the current
frozen-feature/readout family, not a collection of new architectures.
Before selecting it, verify:

- Code, weights, license and inference/training requirements.
- Pretraining and supervised training datasets, including known overlap.
- Whether a fixed pretrained evaluation or retraining is needed for a
  meaningful comparison under the chosen protocol.
- Comparable input population, preprocessing, failure accounting and
  source-only model/threshold selection.
- Feasibility on available hardware within a stated budget.

A pretrained model with incompatible training exposure may be a contextual
reference, not a clean matched baseline. Do not silently mix these meanings.
If no suitable comparator is reproducible, report the limitation and decide
whether the narrowed paper remains viable before approving computation.

### B2. One recognized evaluation protocol

Choose one established cross-dataset protocol with explicit datasets,
official partitions, subject/group exclusions and training restrictions.
The current source-development population is not official-train-only and
must not be compared directly to published numbers using different splits.

Use the smallest justified system set, provisionally DINO-Reg, supervised
CLIP, fixed original two-DINO and the specialist comparator. Retain the
completed matched-fusion failure as evidence; do not reopen its grid.
The exact systems remain a review decision, not a post-result choice.

If existing artifacts violate the selected protocol, rebuild the affected
pipeline under an approved plan or state that a matched comparison cannot be
made. Renaming a table is not protocol compliance.

All four existing datasets have already informed development. A new split
or protocol on them improves comparability but does **not** create an
untouched confirmation set. A genuinely unused external dataset could
strengthen confirmation only after access, license, overlap, support and
cost checks. It is an optional separately approved extension, not a hidden
requirement or permission to inspect new target data.

### B3. Focused analysis rather than another model search

Prefer saved-score analysis where it answers the question:

- Full ROC and a low-FA view; freeze a small set of additional operating
  points before the new analysis and retain the original5%/50% endpoint.
  Additional points are sensitivity analyses, not a relaxed replacement
  success criterion.
- Side-by-side source-calibrated operating results, explicitly labeled
  oracle diagnostics and represented-domain references.
- Per-source attack/bona-fide support, integer error counts, technical
  failures and uncertainty appropriate to the sampling unit.
- Paired uncertainty based on subject or independent connected groups where
  justified; overlapping folds, shared samples and seeds are not independent
  replications. State whether intervals condition on fitted models.
- Standard PAD metrics only with explicit definitions and compatible
  populations. Do not mechanically rename original-denominator FA/BFA as
  standard metrics; separate usable-only and end-to-end views if needed.
- A limited descriptive error breakdown using available, reliable metadata.
  Do not convert camera/attack-type associations into causal explanations.

**Gate B:** publish the exact protocol, system identities, selection rules,
input bindings, fit/inference inventory, resource ceilings, uncertainty plan,
failure handling and stop rules before requesting execution approval.
Any new target must have a separate, valid access and locking plan.

## 5. Paper structure and the role of CLIP

1. Motivation: discrimination summaries do not answer operating transfer.
2. Related work and the verified empirical gap.
3. Data, source-use restrictions, model selection and threshold protocols.
4. Compact main comparison under the declared evaluation conditions.
5. Threshold-transfer versus fixed-score-separation diagnosis.
6. Matched fusion study, including missing selected policies.
7. Limitations, computational cost and reproducibility.

Keep CLIP as a meaningful comparator, not a promised improvement.
Keep a small representative system set in the main text; put the full
variant inventory, completed negative studies and detailed receipts in
supplementary material. Do not hide contrary cases.

Historical studies may motivate this question but should not be pooled as
one homogeneous benchmark. Separate protocol populations, development
analyses, any later standard-protocol evaluation and any genuine external
confirmation. Preserve [301's prior conclusions](301-locked-target-package-and-fixed-evaluation.md)
and the closed313/314 decision; no paper framing retroactively upgrades them.

## 6. Stop rule and decisions requested

Open at most one final supplementary package after the novelty review.
Do not automatically add backbones, solver grids, fusion weights, calibration
rescues, risk gates or fine-tuning if its results are negative.

After that package, write the empirical paper if the contribution is
defensible. If novelty, protocol validity or evidence remains insufficient,
document the gap and reconsider scope or venue instead of chasing a win.
A change in scope requires a new decision.

Requested review decisions:

1. Is operating-transfer diagnosis the right primary paper question?
2. What is the nearest prior work, and what specific gap remains?
3. Which recognized protocol and one PAD comparator are both fair and feasible?
4. Is a previously unused external confirmation dataset necessary for the
   chosen claim, or should the claim remain explicitly developmental?
5. What budget and execution package should be proposed after these answers?

**Immediate recommended action: literature/venue and protocol feasibility
review, then a sealed supplementary-package proposal. No new scientific
execution is authorized by publishing317.**
