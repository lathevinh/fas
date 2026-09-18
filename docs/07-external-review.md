# External Review Guide

This document is a prompt and checklist for ChatGPT or another independent reviewer.

## Suggested review prompt

> Review this repository as a skeptical face anti-spoofing researcher and journal
> reviewer. Identify fatal novelty overlap, invalid assumptions, label leakage,
> unfair baselines, weak causal claims, and experiments that cannot support the
> stated conclusions. Distinguish fatal flaws from fixable weaknesses. Cite the
> repository document and section for every finding. Then propose the smallest
> revised method and experiment set that could still support a publishable claim.
> Do not assume proposed results are observed results.

## Current methodology-freeze instruction

Implementation audit is paused. Review the normative plan in `docs/00` through
`docs/06` and the latest response, not the provisional validator scaffold. The next
review must decide whether the frozen minimum method is feasible and whether its
conditional evidence package is sufficiently novel for a Q3 empirical-method paper.
Do not request another code patch unless a conceptual decision depends on executable
evidence that cannot be reasoned about from the protocol.

## Questions the reviewer should answer

1. Is the novelty distinct from MVP-FAS, DINO-VPT, FLIP, FaceShield, and
   primitive-driven compositional prompting?
2. Is forensic versus semantic evidence operationally defined or merely named?
3. Is cross-foundation disagreement itself too incremental to support the claim?
4. Are reliability records genuinely out-of-fold and source-only?
5. Does apparent complementarity come from a weak second branch?
6. Are MICO and leave-one-attack-out protocols leakage-safe?
7. Does single-image inference remain true despite training on video datasets?
8. Are score fusion, capacity-matched fusion, and uncertainty baselines sufficient?
9. Does the method detect shared failures where both branches confidently agree?
10. Does conditional inference save compute at matched biometric security and coverage?
11. Is per-target nested source-domain OOF candidate selection valid strict
   outer-domain-unseen model selection for all four MICO folds?
12. Does heterogeneous-vs-same-family attribution plus source-only cross-fitted
   failure-risk transfer clear a plausible Q3 novelty bar given the closest work?
13. Is the frozen-backbone, sequential cached-feature plan feasible on one RTX 4080
   16 GB, and what is the smallest necessary simplification if not?
14. Is any missing baseline or endpoint fatal to the five-condition claim hierarchy?
15. If no conceptual blocker remains, explicitly state `METHODOLOGY ACCEPTED FOR
   IMPLEMENTATION PLANNING`.

## Expected review format

```text
Fatal issues
- Finding, evidence, consequence, proposed correction

Major issues
- Finding, evidence, consequence, required experiment

Minor issues
- Terminology, reporting, or reproducibility concern

Novelty verdict
- Strong / plausible / weak / already occupied, with closest work

Minimum viable revision
- Method scope
- Dataset scope
- Baselines
- Decisive experiments
```

## Evidence standard

The reviewer should reject any statement that confuses:

- a planned result with an observed result;
- correlation with causal forensic evidence;
- agreement with correctness;
- attack-category supervision with cue-level supervision;
- a visually appealing heatmap with a faithful explanation;
- frame-level single-image inference with a leakage-safe video protocol.
