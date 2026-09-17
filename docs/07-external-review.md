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
