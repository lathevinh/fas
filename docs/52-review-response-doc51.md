# Response to Document 51 - Final Track-A Semantic Closure

Date: 2026-09-18

## Decision

The review is accepted. Its two required changes correct the naming of a transferred
operating point and define scoreability under partial detector failure. They do not
alter the architecture, RQ1/RQ2, novelty boundary, Track-B protocol, or four-table
paper contract. The core Q3 plan remains frozen.

## Required corrections

### 1. Transferred 1% threshold metric - accepted

The threshold $\tau^A_{BPCER1}$ is still selected only on source validation as the
lowest deterministic candidate satisfying equal-domain macro-source BPCER at most 1%.
After unchanged transfer, the target result is now reported as the pair

$$
APCER_{target}(\tau^A_{BPCER1}),
\qquad
BPCER_{target}(\tau^A_{BPCER1}).
$$

It is never labeled target `APCER@BPCER<=1%`, because the source constraint does not
imply that target BPCER achieves 1%. Any conventional target operating point selected
from the target ROC remains a post-hoc, non-deployable diagnostic.

### 2. Two-frame detector success - Policy A accepted

Track A adopts the complete-pair policy. A target video enters classifier-only metrics
only if both pinned frames produce valid detector crops. Its video score is then the
arithmetic mean of the two class-1 probabilities. A one-frame success is neither
averaged alone nor assigned a synthetic score, and pinned frames are never replaced.

The report includes frame coverage, complete-pair video coverage, and class-conditional
coverage for each target. This preserves the two-frame aggregation contract on the
scored population while exposing how detector failures change that population.
Track B remains unchanged: detector failures are terminal non-accept transactions in
end-to-end denominators.

## Clarifications

### Empirical resolution, not certification

The 1% source operating point requires at least 100 complete-pair bona-fide validation
videos in every contributing source domain. This is only an empirical resolution rule,
not a statistical guarantee. If any source fails it, the operating point is `not
estimable` and is not interpolated. Source error numerators, denominators, and achieved
per-domain APCER/BPCER are reported; a binomial interval is optional descriptive
context.

### Macro-source, not worst-source

The selection condition is equal-domain macro-source BPCER at most 1%. It does not
assert BPCER at most 1% in every source domain. Per-source values make any imbalance
visible. Worst-source security constraints remain outside Track A and belong, if ever
activated, to a separately specified Track-B deployment analysis.

## Closure boundary

Track A is now closed at specification level. It remains limited literature context,
with controlled comparisons only among in-house systems sharing its source-only
recipe. Published SSDG values remain target-aware historical context and cannot support
superiority claims.

Further Track-A refinement is deferred unless Phase-1 implementation reveals a concrete
artifact incompatibility. Research effort returns to Track B and the frozen primary
Domain-OOF versus sample-OOF estimand.

## Updated verdict

**DOCUMENT 51 IS ANSWERED; THE TRACK-A REVIEW LOOP IS CLOSED AND THE CORE Q3 PLAN REMAINS FROZEN.**
