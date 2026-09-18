# ChatGPT Review — Document 56: Final Decision-Rule Closure

Date: 2026-09-18  
Repository: `lathevinh/fas`  
Reviewed file: `docs/56-review-response-doc55.md`

## Verdict

Document 56 successfully closes the four decision-rule gaps from Document 55.

The core Q3 research plan is now scientifically coherent and should remain frozen.

Only two wording clarifications remain:

1. State explicitly that RQ2 class-balanced AURC is computed on the common detector-success transaction population. Detector failures enter only end-to-end FA/BFNR guardrails and coverage accounting.
2. State explicitly that coverage is supporting/explanatory only and is not an additional RQ2 pass/fail guardrail, unless the project intentionally chooses to add such a guardrail now.

## Why the rest is sound

- Competence dependencies are now claim-specific: RQ1 requires the heterogeneous complete system; RQ2 requires both complete systems; weak standalone OpenCLIP does not automatically invalidate RQ1/RQ2.
- RQ2 now has one deterministic primary scalar:
  \[
  U_j=\frac12(AURC_{attack,j}+AURC_{bona,j}),
  \qquad
  \Delta_{RQ2}=U_{same}-U_{hetero}.
  \]
- The RQ2 pass rule is explicit: minimum macro effect, positive paired lower bound, target consistency, seed consistency, target-harm tolerance, and FA/BFNR guardrails.
- Raw AURC is appropriate for RQ2 because it compares complete systems and therefore jointly reflects classifier error burden and failure-risk ordering.
- RQ1 seed aggregation is now deterministic:
  \[
  \Delta_{OOF,t}=\frac13\sum_{s=1}^{3}\Delta_{OOF,t,s},
  \qquad
  \Delta_{OOF,macro}=\frac14\sum_{t=1}^{4}\Delta_{OOF,t}.
  \]
- Underpowered seeds remain in the point estimate if AP is defined; undefined AP makes the target and primary claim inconclusive rather than silently deleting a seed.
- The wording “20 erroneous target transactions/videos” is now statistically correct; dependence is handled by cluster bootstrap.

## Final paper hierarchy

- Core protocol: strict single-image Track B.
- RQ1: domain-OOF vs matched sample-OOF on identical final classifier errors.
- Primary RQ1 endpoint: prediction-error AP delta.
- Operational validation: selective K=1 security/usability.
- RQ2: heterogeneous complete system vs matched same-family complete system.
- Track A: literature context only.
- SiW-M, routing, LoRA, extended complementarity: optional.

## Final recommendation

After the two wording clarifications above:

\[
\boxed{\text{FREEZE THE PLAN AND MOVE TO PHASE 0}}
\]

No further broad protocol review is warranted unless implementation exposes a concrete contradiction in the frozen specification.
