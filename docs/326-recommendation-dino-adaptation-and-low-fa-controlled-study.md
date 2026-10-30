# 326 - Recommendation: seek a measured contribution through controlled DINO adaptation

Date: 2026-10-30.
Evidence: [completed comparison324](324-completed-comparison-results-and-paper-update.md)
and [Review325](325-review-doc324-completed-results-and-paper319.md).

Status: **owner-requested publication of a research recommendation, not
authorization to train or evaluate new models.** The exact implementation,
adaptation recipe, loss, selection rule and execution budget remain to be
specified before scientific execution.

## Why the recommendation changes

The owner challenged whether the poor operating results provide sufficient
contribution for a Q3-oriented paper. That challenge is justified.
Review325 accepted a completed, correctly reported experiment; it did not
establish methodological novelty or an adequate publication contribution.
Its recommendation to proceed directly to submission preparation was too
optimistic if understood as evidence that the current paper is sufficient.

**This document supersedes325's recommendation that only editorial work
remains.** It preserves acceptance of324, all measured results, exclusions,
failure accounting and limitations. Further computation is a proposed new
study, not unfinished work owed by the completed comparison.

The existing work supplies a useful diagnosis, but no successful source-only
operating policy at the adopted primary utility. Domain shift, constrained
ROC analysis and frozen-feature transfer failure are already established
topics. Honest negative results and extensive verification do not substitute
for a distinct scientific answer.

## Proposed hypothesis and controlled comparison

Focus on DINO rather than adding CLIP, another backbone or a risk gate.
On OULU, the specialist's better low-FA score separation suggests that changing
the learned representation is worth testing. It does not prove that DINO
adaptation will improve either separation or threshold transfer.

PAD adaptation of DINO already exists; use an implemented published approach
as a strong reference, not as an invention of this project. A primary starting
reference is [Feng et al., Benchmarking Vision Foundation Models for
Domain-Generalizable Face Anti-Spoofing](https://arxiv.org/html/2604.19196v2).
Select one reproducible fixed recipe after checking its implementation and
hardware requirements; do not stage a contest among adaptation methods.

| Configuration | Purpose |
|---|---|
| Existing frozen DINO-Reg | Historical starting point; reuse only if all relevant evaluation bindings match |
| DINO adapted for PAD with ordinary BCE | Determine whether representation adaptation itself helps |
| Same adapted DINO with an additional low-FA learning objective | Determine whether emphasizing attacks most easily accepted adds value beyond adaptation |

The candidate hypothesis is that average BCE does not sufficiently prioritize
the attack-score tail responsible for false acceptance under source shift.
A source-specific hard-attack or low-FA ranking objective is a direction to
specify, not a finished loss or verified novelty claim. Check the closest
existing objectives before attributing novelty to the final formulation.

Keep the two new configurations identical in backbone, trainable parameters,
input processing, augmentation, initialization, training opportunity and
source-only selection except for the declared objective. If reproducing a
published adaptation pipeline requires departing from that control, explain
the departure and avoid claiming the loss alone caused the difference.
Do not select an objective or its strength by trying alternatives on targets.

## Small first stage

Propose two new configurations, one fixed seed and four train-three/test-one
rotations: **eight initial training runs**. This is an inventory proposal,
not a measured runtime or sealed resource budget. Include acquisition,
validation, calibration, prediction and analysis work in the final budget.

Retain the existing datasets, accepted single-middle-frame inputs, applicable
exclusions, technical-failure accounting and source-derived threshold rule.
Use source data only for fitting, objective settings, checkpoint selection
and calibration. Keep SiW's unknown-subject/local-intersection limitation.
All targets have already informed development; this study is exploratory,
not confirmation on untouched datasets.

Measure both available-policy FA/BFA and fixed-score low-FA separation, with
AUROC as supporting information. Keep5% FA/50% BFA as the existing primary
utility rather than relaxing it after seeing results. Oracle analysis stays
diagnostic and cannot choose deployable thresholds.

## Expansion and stopping decision

Before the first run, declare what constitutes sufficient signal to justify
the remaining two seeds: the primary improvement measure, practical margin,
cross-target consistency and tolerated regressions. These numerical choices
are not fixed by this recommendation and must not be selected afterward.

If the signal warrants expansion, run the remaining two seeds for the same
two configurations and four rotations:16 additional training runs,24 total.
The extra seeds assess training variability on the same observed targets;
they do not turn the exploratory first-stage decision into independent
confirmation or create new independent test populations.

If only AUROC improves, or only oracle BFA improves while source-policy
operation remains poor, report the narrower result. Low-FA learning does not
by itself solve threshold transfer. If the proposed objective does not add
value over ordinary adaptation, stop this hypothesis rather than add fusion,
gates or a new encoder to manufacture a favorable story.

The intended contribution, **if supported**, is an explicit adaptation
objective with measured benefit over both frozen DINO and ordinary adapted
DINO, plus analysis of where that benefit transfers. Neither success,
novelty nor Q3 acceptance is established in advance.

## Immediate deliverable

Prepare one concrete controlled-study specification: chosen reproducible
adaptation reference, exact trainable layers, objective and settings,
source-only selection, eight-run inventory, resource limits and expansion/
stop criteria. Preserve the completed324 report and paper as prior evidence.
Do not launch training merely because this recommendation has been committed.
