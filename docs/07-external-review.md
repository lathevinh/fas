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

## Current handoff instruction

Research direction and revised core methodology were accepted in Round 15. Round 16
then accepted the Q3-first paper plan, named Domain-OOF Failure Risk Estimation, and
froze the manuscript structure and four main tables in `docs/40-paper-skeleton.md`.
Future implementation review should assess Phase 0 scaffold migration against
normative `docs/00` through `docs/06`, Rounds 14-16, and the paper skeleton. Do not
reopen settled architecture choices without new evidence or a concrete contradiction.

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
11. Does the globally fixed OpenCLIP primary remove selector influence from every
   domain-OOF risk record and all four outer MICO folds?
12. Does heterogeneous-vs-same-family attribution plus source-only cross-fitted
   failure-risk transfer clear a plausible Q3 novelty bar given the closest work?
13. Is the frozen-backbone, sequential cached-feature plan feasible on one RTX 4080
   16 GB, and what is the smallest necessary simplification if not?
14. Does the implementation plan preserve separate classifier, risk, disagreement,
   and routing claims with the required baselines and endpoint semantics?
15. Does each implementation acceptance test trace to the frozen methodology rather
   than to superseded provisional configuration behavior?

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
