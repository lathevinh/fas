# Response to Document 57: Population and Coverage Clarification

Date: 2026-09-18  
Responds to: `docs/57-chatgpt-review-doc56.md`  
Status: both wording clarifications accepted; plan remains frozen

## Decision

Document 57 is accepted. It requests no scientific or numerical change. The two
clarifications make the already intended population boundary and role of coverage
explicit, so they are applied consistently to every RQ2 owner document.

## 1. RQ2 AURC population

The heterogeneous and same-family systems share one deterministic frame manifest,
one fixed face detector, and one crop manifest. Therefore their RQ2 AURCs are computed
on the identical class-specific transaction mask:

$$
M_c=\{i:y_i=c\ \land\ detector\_success_i=1\},
\qquad c\in\{attack,bona\ fide\}.
$$

For both systems, $n_c=|M_c|$ and the class-conditional risk-coverage ordering contains
only transactions in $M_c$. No detector failure is assigned a classifier prediction,
failure-risk score, or artificial terminal rank. This preserves a like-for-like paired
comparison of the two classifier-plus-risk systems on their common valid input
population.

The scalar remains unchanged:

$$
U_{j,t,s}=\frac12\left(AURC_{attack,j,t,s}+AURC_{bona,j,t,s}\right),
$$

$$
\Delta_{RQ2,t,s}=U_{same,t,s}-U_{hetero,t,s}.
$$

Detector failures are not silently discarded from deployment accounting. Under K=1,
each failure is a terminal non-accept and enters:

$$
FA_{end2end}
=
\frac{N_{attack,accepted\ live}}{N_{attack,total}},
$$

$$
BFNR_{end2end}
=
\frac{N_{bona,not\ accepted}}{N_{bona,total}},
$$

where both denominators include detector-successful and detector-failed transactions.
Detector failures also reduce the reported class coverage. Thus the RQ2 scalar is
explicitly detector-success conditional, while the operational guardrails and
coverage expose the full transaction pipeline.

Because the detector and selected frame are shared, the detector-success mask must be
bit-identical between systems. A mismatch is a lineage/schema failure, not an observed
system difference; RQ2 evaluation stops until the artifact join is corrected without
examining or tuning against target outcomes.

## 2. Coverage has no additional pass/fail threshold

Coverage is mandatory supporting and explanatory output. It reports the population
remaining after detector success and source-selected risk gating, separately for
attack and bona-fide transactions. It prevents AURC and end-to-end rates from being
read without knowing how many transactions received decisions.

Coverage is not an additional RQ2 guardrail. In particular, H2 does not require:

- a minimum attack coverage;
- a minimum bona-fide coverage;
- coverage non-inferiority between systems;
- a target-level or macro coverage tolerance.

No such threshold is added now because that would alter the preregistered conjunctive
decision rule after it was frozen, duplicate information already exposed by raw AURC
and the full-denominator FA/BFNR guardrails, and create another post-target failure
criterion without a source-derived justification.

The H2 pass rule remains exactly the six conjuncts in Document 56: primary effect,
paired uncertainty, target consistency, seed consistency, selective-harm tolerance,
and end-to-end FA/BFNR guardrails. Coverage can explain a pass or failure but cannot
independently produce, rescue, or overturn one.

## 3. Synchronized owners

The clarifications are now present in:

- `docs/02-research-questions.md`;
- `docs/04-data-and-protocols.md`;
- `docs/05-experiment-plan.md`;
- `docs/38-implementation-plan.md`;
- `docs/40-paper-skeleton.md`;
- `docs/42-data-to-experiment-implementation-plan.md`;
- `docs/56-review-response-doc55.md`.

## 4. Phase-0 invariants

Implementation must assert:

1. Both RQ2 systems consume the same target transaction IDs and detector-success mask.
2. RQ2 AURC denominators contain detector-successful transactions only.
3. Detector failures have no fabricated classifier/risk scores.
4. Every detector failure remains in original-denominator K=1 FA/BFNR and class-
   coverage accounting as a terminal non-accept.
5. Coverage fields are mandatory report outputs but are absent from the H2 decision
   predicate.
6. No target observation can introduce a coverage threshold or alter this population
   boundary.

## Final disposition

Both requested wording clarifications are closed. They resolve an interpretation gap
without changing the architecture, scalar, thresholds, guardrails, RQ count, table
contract, or execution schedule.

The plan remains frozen. Phase 0 implementation should proceed, and further protocol
review should occur only if implementation exposes a concrete contradiction.