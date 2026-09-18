# Response to Review Round 15 - Estimands Locked and Planning Opened

Date: 2026-09-18

## Decision

The owner accepts Review Round 15 in full.

**METHODOLOGY ACCEPTED FOR IMPLEMENTATION PLANNING. IMPLEMENTATION PLAN AUTHORIZED.**

The review does not reopen architecture or novelty. Its requirements are analysis
contracts for the accepted method. They are incorporated into the normative experiment
plan and the dependency-ordered implementation plan. No model code, experiment, or
target-label inspection occurs in this response.

## RQ1: fixed-classifier risk-transfer estimand

RQ1 holds the final heterogeneous classifier and its error labels fixed. Average
precision means non-interpolated AP with prediction error as the positive class and a
larger score indicating greater risk. The primary feature variant is fixed as
$R_{DVd}$ before target evaluation.

For target $t$ and seed $s$:

$$
\Delta_{OOF,t,s}=AP(e_{DV},r_{DVd}^{domain})-
AP(e_{DV},r_{DVd}^{sample}).
$$

Both variants use identical final base predictions, error labels, feature family,
loss, regularization, and optimization budget. The contrast tests the complete
source-domain OOF construction against matched sample-OOF training. It does not claim
that domain holdout alone caused the gain when branch-fit budgets differ.

## RQ2: whole-system matched control

The heterogeneous and same-family systems have different classifiers, errors, risk
estimators, and gates. Their raw AP difference is descriptive, not an estimator-quality
contrast. The required DINOv2-Reg plus plain-DINOv2 control therefore receives its own
matched domain-OOF risk estimator and source-selected selective gate.

RQ2 compares the two complete systems on the same transactions using classification
quality, error prevalence, selective curves, and end-to-end K=1 outcomes. The claim is
limited to an advantage of the studied DINO-OpenCLIP pair over the matched DINO-DINO
pair under this protocol. It is not a causal claim about heterogeneous pretraining.

## K=1 utility semantics

For the core action policy, predicted spoof and abstain are both terminal non-accept.
Gating the same classifier can weakly reduce false accepts only by weakly increasing
bona-fide non-accepts. The utility claim is therefore a better source-selected
security-usability trade-off than comparator risk gates, not simultaneous improvement
of both axes over ungated classification.

Every selective result reports achieved attack and bona-fide coverage, live decisions
blocked by the gate, attacks newly blocked, bona-fide transactions newly rejected,
`FA_end2end`, and `BFNR_end2end`. Target labels cannot select separate class thresholds
or matched-coverage operating points.

## Matched OOF fairness

Sample-OOF and domain-OOF use the same source subject/video universe after permanent
gate-holdout exclusion, frame/video unit, source-macro weighting, quality features,
risk family, regularization, and optimization budget. Sample-OOF is subject-disjoint.
Each pseudo-fold reports OOF record count, effective branch-fit size, and natural error
prevalence. A budget-matched sensitivity is required if fit sizes differ materially;
otherwise interpretation is limited to the full construction.

## Claim-specific inference

Each claim has its own endpoint, fixed comparator set, delta, minimum meaningful
effect, harm tolerance, event requirement, and pass rule. The primary rule requires a
positive paired four-target macro lower confidence bound, point gain at least
$\delta_{min}$, at least three of four positive target estimates, no target beyond its
harm tolerance, and at least two of three positive seed-level macro deltas.

False-accept counts govern only false-accept-conditioned endpoints. Missing FARR events
do not invalidate estimable error AP, and false-reject-driven AP gain does not establish
attack utility. Underpowered is reported as inconclusive, separately from evidence
against. Required comparator claims use a preregistered conjunction rather than
post-target comparator selection.

## Superseded scaffold

The existing scaffold still encodes a labeled pilot, multiple primary VLM candidates,
a global claim sequence, and routing gates as readiness requirements. Those artifacts
are explicitly non-normative. The implementation plan replaces their contracts before
any model or target-facing work. Historical review files remain unchanged.

## Handoff

The new implementation plan maps the frozen method to modules, artifacts, tests,
lineage gates, and execution phases. Work begins with scaffold reconciliation and
synthetic contract tests. Dataset acquisition and metadata audit follow. Confirmatory
target evaluation remains disabled until source-derived analysis rules and immutable
artifact hashes are frozen.
