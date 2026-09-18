# Response to Document 53 - Final Core-Plan Synchronization

Date: 2026-09-18

## Decision

The one-pass audit is accepted. All 12 synchronization items are applied together to
the normative research, method, experiment, paper, and implementation contracts. The
changes remove cross-document ambiguity; they add no architecture, research question,
or novelty mechanism.

Strict single-image Track B is the paper. Track A remains closed and moves outside the
four main tables as compact or supplementary literature context.

## Must-fix responses

### 1. RQ1 ranking primary, utility secondary - accepted

RQ1 now asks only whether domain-OOF supervision improves non-interpolated
prediction-error AP over matched sample-OOF supervision on identical final classifier
errors. Selective security-usability is a separately tested operational consequence.
Failure at one gate operating point cannot by itself falsify a supported fixed-error
RQ1 result.

### 2. RQ2 whole-system comparison - accepted

RQ2 now compares the complete DINOv2-Reg/OpenCLIP selective system with the matched
DINOv2-Reg/plain-DINOv2 selective system. Its evidence is the frozen paired
whole-system rule over classification errors, `FA_end2end`, `BFNR_end2end`, class
coverage, and selective utility/AURC. Each system's risk AP is descriptive because its
classifier and error labels differ; cross-system AP alone cannot establish superiority.

### 3. No quasi-third RQ - accepted

The former secondary attribution hypothesis is renamed `Attribution ablations, not
research questions`. $\Delta_{CF}^{AP}$ and $\Delta_{dis}^{AP}$ remain fixed-error
attribution analyses. SiW-M attack shift stays optional and outside both core RQs. The
normative RQ document contains exactly two RQ headings.

### 4. Track A demoted from main tables - accepted

The four main tables are now exclusively:

1. Track-B strict single-image classifier competence;
2. RQ1 fixed-error risk transfer;
3. selective PAD utility;
4. RQ2 heterogeneous versus same-family complete systems.

Track A is a compact preliminary subsection or supplementary table. Its source-only,
detector-conditional, SSDG/FLIP caveats and two-engineer-day stop rule remain unchanged.
It hosts no main-table panel, RQ, novelty, or controlled superiority claim.

### 5. Base-classifier competence rule - amended by Document 56

Before target commands unlock, Phase 7 writes one immutable source-only competence
artifact for DINOv2-Reg, OpenCLIP, the heterogeneous average, and the same-family
average. Document 56 narrows the scope of the numeric rule without changing it:

- $\delta_{competence}=0.05$;
- equal-domain macro AUROC and balanced accuracy must each be at least 0.55;
- macro-AUROC cluster-bootstrap 95% lower bound must exceed 0.50;
- scores must be finite with range greater than $10^{-6}$ and both classes present;
- pseudo-domain balanced accuracy uses a threshold selected only on that fold's
  allowed source remainder;
- the heterogeneous reference source-OOF table must contain at least 20 errors and
  20 correct predictions.

The heterogeneous complete system must pass this rule for RQ1, and both complete
systems must pass it for RQ2. DINOv2-Reg must pass the nondegeneracy checks. A branch
that misses the 0.55/LCB threshold loses only its standalone-competence claim;
OpenCLIP failure does not block a core RQ whose required complete systems pass.
Failure cannot trigger target-informed model alteration. Track-A literature rank is
irrelevant to competence.

### 6. Complete-construction estimand - accepted

The documents now state that RQ1 tests the complete domain-OOF construction, not a
causal effect of domain identity. Required diagnostics compare effective fitting-set
sizes, OOF error prevalence and type composition, branch score/calibration
distributions, and risk-feature distributions. A source-predefined
prevalence/difficulty-matched weighting sensitivity is run where feasible but never
replaces the unweighted primary contrast.

### 7. Primary error-event rule - seed aggregation amended by Document 56

Freeze $N_{error,min}=20$ erroneous target transactions/videos per target and seed,
with dependence handled by subject/video cluster bootstrap. Below this count, AP,
paired delta, counts, and uncertainty remain reported when estimable, but the
contribution is underpowered and cannot count as event support.

For target $t$, Document 56 freezes
$\Delta_t=(\Delta_{t,1}+\Delta_{t,2}+\Delta_{t,3})/3$ using all three estimable seed
deltas, including any seed below 20 errors, followed by the equal-weight four-target
macro. A target is event-eligible only when all three deltas are estimable and at least
two seeds meet the count. An undefined one-class seed makes the primary macro and RQ1
claim inconclusive; it is never dropped or assigned a synthetic value. A pass also
requires at least three eligible targets, and an ineligible target cannot satisfy the
three-of-four positive-target rule.

### 8. Failure-risk score terminology - accepted

The default output is a `failure-risk score`. Equal pseudo-domain weighting does not
imply a deployment posterior. Probability or calibrated-risk language is allowed only
when held-out source Brier, NLL, and reliability checks support it.

## Strong-recommendation responses

### 9. With/without-quality attribution visible - accepted

Main RQ1 attribution visibly reports domain-OOF and sample-OOF $R_{DVd}$ both with and
without $q$. If only `+q` succeeds, the mechanism is described as transferable
nuisance/failure signatures, not heterogeneous disagreement alone.

### 10. Domain-ID audit remains diagnostic - accepted

Domain predictability can trigger only source-predefined sensitivity analyses. It can
never replace the frozen primary feature set after target evaluation.

### 11. Complementarity scope reduced - accepted

Required first-paper analyses are standalone DINOv2-Reg and OpenCLIP, fixed fusion,
matched DINOv2-Reg/plain-DINOv2, joint correctness/double fault, and a simple directional
rescue summary. Shared-head diversity, supervised OpenCLIP visual heads, extensive
oracle/correlation analyses, and conditional mutual information are optional appendix
work and cannot block either RQ.

### 12. Four-domain inference bounded - accepted

Bootstrap intervals are interpreted conditionally on the evaluated four MCIO domains
and fitted procedures. Claims use `consistent across the evaluated MCIO held-out
domains`, never sampling-based proof over all future capture domains.

## Cross-document invariants

The synchronized contracts now enforce these invariants:

- exactly two RQs and exactly four main tables;
- RQ1 AP and downstream operational utility have separate pass/fail states;
- RQ2 is whole-system, never a raw cross-system AP comparison;
- final target predictions and error labels are identical across RQ1 OOF strategies;
- target results cannot alter competence thresholds, features, comparators, or event
  rules;
- Track A cannot block or redefine Track B;
- optional attack shift, routing, and complementarity diagnostics cannot rescue or
  invalidate the primary estimand.

## Updated verdict

**DOCUMENT 53 IS ANSWERED. THE CORE Q3 PLAN IS SYNCHRONIZED, FINALLY FROZEN, AND READY TO MOVE TO PHASE-0 IMPLEMENTATION WITHOUT ANOTHER BROAD PROTOCOL-REVIEW CYCLE.**
