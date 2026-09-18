# Response to Document 55: Final Decision-Rule Closure

Date: 2026-09-18  
Responds to: `docs/55-chatgpt-review-doc54-final.md`  
Status: all four requested corrections accepted and frozen

## Executive decision

Document 55 is accepted without reopening the architecture, datasets, two-RQ scope,
Track-A role, or four-table paper contract. Its four findings expose genuine closure
gaps. This response resolves them in the owning normative documents and defines the
edge cases needed for deterministic implementation.

The frozen core remains:

$$
\text{strict single-image source-domain OOF failure-risk transfer}
$$

with domain-OOF versus matched sample-OOF as RQ1 and a complete heterogeneous versus
same-family selective-system comparison as RQ2.

## 1. Competence scope: accepted and narrowed

The numeric competence rule was correct but its dependency scope was too broad. The
Phase-7 artifact still records all four entries:

- DINOv2-Reg;
- OpenCLIP;
- calibrated DINOv2-Reg/OpenCLIP heterogeneous average;
- calibrated DINOv2-Reg/plain-DINOv2 same-family average.

For every entry it records finite and nonconstant scores, score range, both-class
support, finite calibration parameters, equal-domain pseudo-shift AUROC and balanced
accuracy, confidence bounds, and error/correct counts. Recording a diagnostic does
not make it a gate for every claim.

### Frozen dependency rule

| Claim | Mandatory competence dependency |
|---|---|
| RQ1 domain-OOF transfer | Heterogeneous complete system passes the full rule; shared DINO anchor passes nondegeneracy |
| RQ2 heterogeneous advantage | Heterogeneous and same-family complete systems both pass the full rule; shared DINO anchor passes nondegeneracy |
| Standalone DINO competence | DINO passes the full rule |
| Standalone OpenCLIP competence | OpenCLIP passes the full rule |
| VLM incremental risk information | Relevant complete-system gate plus its frozen paired attribution test |

The full rule is unchanged: equal-domain macro AUROC and balanced accuracy must each
be at least 0.55, the cluster-bootstrap 95% LCB for macro AUROC must exceed 0.50,
scores must be finite with range greater than $10^{-6}$, both classes must be present,
and calibration parameters must be finite. The heterogeneous source-OOF risk table
also requires at least 20 errors and 20 correct predictions.

For the core RQs, DINO nondegeneracy means finite scores, range greater than
$10^{-6}$, both-class support, and finite calibration. Its 0.55/LCB threshold is
required only for a standalone-DINO competence claim.

Therefore, an OpenCLIP standalone result below 0.55:

- forbids calling OpenCLIP a competent standalone PAD classifier;
- does not invalidate RQ1 if the heterogeneous reference passes;
- does not invalidate RQ2 if both complete systems pass;
- cannot itself establish VLM value, which still requires the paired incremental-risk
  attribution result.

No competence failure authorizes target-informed tuning or branch replacement.

## 2. RQ2 scalar: accepted and fully specified

Document 55 correctly rejects an informal bundle in which the preferred outcome could
be selected after target evaluation. RQ2 now has one primary scalar. Raw AURC is used,
not excess-AURC, because RQ2 compares complete systems: raw AURC retains both base
classifier error burden and failure-ranking quality. Excess-AURC is still reported as
a ranking-regret diagnostic.

For class $c\in\{attack,bona\}$, system $j$, target $t$, and seed $s$, sort
the common transaction population on which the single fixed face detector succeeded
for both systems from lowest to highest predicted failure risk. At retained coverage
$k/n_c$, let the class-conditional risk be the fraction of classification errors among
the first $k$ detector-successful transactions. Define empirical raw AURC as the
equal-width staircase mean over $k=1,\ldots,n_c$; tied scores use the expectation over
permutations within the tied block so transaction IDs cannot determine the result.
Detector failures receive no artificial risk rank and are absent from both systems'
AURC inputs. They remain terminal non-accepts in original-denominator K=1
`FA_end2end`/`BFNR_end2end` and are included in class-coverage accounting.

Define:

$$
U_{j,t,s}
=
\frac12\left(
AURC_{attack,j,t,s}+AURC_{bona,j,t,s}
\right),
$$

$$
\Delta_{RQ2,t,s}=U_{same,t,s}-U_{hetero,t,s}.
$$

Lower $U$ is better, so positive $\Delta_{RQ2}$ favors the heterogeneous system. The
unweighted class mean prevents attack/bona-fide prevalence from silently choosing the
security-usability weighting.

### Frozen RQ2 pass rule

Apply the seed-then-target aggregation and paired cluster bootstrap defined below. H2
passes only if all conditions hold:

1. $\Delta_{RQ2,macro}\ge0.01$.
2. The paired cluster-bootstrap 95% LCB of $\Delta_{RQ2,macro}$ is above zero.
3. At least three of four target-level deltas are positive.
4. At least two of three seed-level four-target macro deltas are positive.
5. No target has $U_{hetero}-U_{same}>0.02$.
6. At the two systems' independently source-selected gates, each of
   $FA_{end2end,hetero}-FA_{end2end,same}$ and
   $BFNR_{end2end,hetero}-BFNR_{end2end,same}$ is at most 0.01 in the equal-target
   macro and at most 0.02 on every target.

The constants are frozen now, before target inspection. A 0.01 primary threshold is a
one-percentage-point reduction in integrated class-balanced selective risk; the 0.02
per-target bounds prevent a favorable macro from hiding material target harm.

The end-to-end guardrails use original attack and bona-fide transaction denominators
under K=1. Each system uses its own source-selected gate; target thresholds are never
matched or retuned. A favorable AURC, FA, BFNR, or coverage result cannot compensate
for failure of another conjunct. A guardrail violation is evidence against H2, not an
invitation to choose another primary metric.

Classification quality, error prevalence, each system's own error AP, raw/excess-AURC,
attack coverage, bona-fide coverage, `FA_end2end`, and `BFNR_end2end` remain mandatory
table entries. They explain the scalar outcome but cannot replace it. Cross-system AP
remains descriptive because the classifiers induce different error labels. Coverage
is supporting and explanatory only: H2 has no minimum-coverage threshold or additional
coverage pass/fail guardrail. Its role is to expose the detector/gate population and
prevent a selective metric from being interpreted without its achieved coverage.

If a required class has no transactions for a target/seed, class-balanced AURC is
undefined and RQ2 is inconclusive. A zero-error class is valid and has raw AURC zero;
it is not treated as missing.

## 3. RQ1 seed aggregation: accepted and fully specified

For target $t$ and seed $s$:

$$
\Delta_{OOF,t,s}
=
AP(e_{DV},r_{DVd}^{domain})
-
AP(e_{DV},r_{DVd}^{sample}).
$$

Whenever all three seed deltas are estimable, the only target-level point estimate is:

$$
\boxed{
\Delta_{OOF,t}=\frac13\sum_{s=1}^{3}\Delta_{OOF,t,s}
}
$$

and the only primary macro is:

$$
\boxed{
\Delta_{OOF,macro}=\frac14\sum_{t=1}^{4}\Delta_{OOF,t}.
}
$$

All three seeds enter with equal weight. A seed below $N_{error,min}=20$ remains in
the point estimate if AP is estimable; it simply cannot provide event support. It is
never silently dropped, replaced, or downweighted.

A target is event-eligible only if:

- all three seed deltas are estimable; and
- at least two of three seeds contain at least 20 erroneous target transactions.

If any seed has one-class error labels, prediction-error AP is undefined. That target
is ineligible and the required four-target primary macro is not estimable, so RQ1 is
reported as inconclusive. The protocol does not insert AP=0, AP=1, a prevalence
surrogate, or a two-seed average.

For each of 2,000 bootstrap replicates, resample subject/video clusters within each
target using the same cluster multiplicities for domain-OOF, sample-OOF, and all seeds
where the common target manifest provides the same identities. Compute seed-level
deltas, average the three seeds within target, and then average the four targets.
Seeds are optimization replicates, not bootstrap units. Their variability is reported
separately as mean/standard deviation and the three seed-level four-target macros.

## 4. Error-event terminology: accepted

The frozen applicability phrase is now:

> at least 20 erroneous target transactions/videos per target and seed, with
> dependence handled by the preregistered subject/video cluster bootstrap.

The count is an information/applicability threshold, not an independence assumption.
Twenty errors from a small number of subjects remain 20 erroneous transactions but
are not described as 20 independent statistical events. Reliable subject IDs take
precedence as the bootstrap cluster; otherwise the highest reliable video/transaction
grouping is used as already specified by the protocol.

## 5. Cross-document synchronization

The corrections are applied to the following owners:

- `docs/02-research-questions.md`: H2 scalar, sign, thresholds, and guardrails;
- `docs/04-data-and-protocols.md`: raw class-conditional AURC semantics;
- `docs/05-experiment-plan.md`: complete rules, edge cases, and bootstrap order;
- `docs/38-implementation-plan.md`: Phase-7 artifacts and executable claim contracts;
- `docs/40-paper-skeleton.md`: main-table and claim wording;
- `docs/42-data-to-experiment-implementation-plan.md`: implementation formulas and
  failure states;
- `docs/54-review-response-doc53.md`: amendment of the two statements directly
  corrected by Document 55.

## 6. Frozen invariants for Phase 0

The implementation and tests must enforce these invariants:

1. Branch-level 0.55/LCB failure cannot automatically set RQ1 or RQ2 to failed.
2. RQ1 requires heterogeneous complete-system competence; RQ2 requires both complete
   systems; the shared DINO anchor must be nondegenerate.
3. RQ2 has exactly one primary metric and fixed sign: positive
   $U_{same}-U_{hetero}$ favors heterogeneous.
4. RQ2 support metrics cannot be substituted for the primary scalar.
5. RQ1 target deltas use exactly three equally weighted estimable seeds.
6. Event eligibility never changes point-estimate weights.
7. Undefined seed AP produces an inconclusive primary claim, never seed deletion or a
   synthetic score.
8. Error counts are transaction counts; uncertainty respects subject/video clusters.
9. Target results cannot alter any competence threshold, effect threshold, harm
   tolerance, feature, comparator, gate, or aggregation rule.

## Final disposition

All four required changes from Document 55 are accepted and closed. They alter claim
dependencies and decision semantics only; they do not add a model, dataset, research
question, or main table.

The research plan is now frozen for Phase 0 implementation. Further changes to these
rules require a dated amendment made before any affected target result is inspected.