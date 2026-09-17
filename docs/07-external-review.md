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
3. Can the consistency losses improve agreement while worsening correctness?
4. Does the ontology encode the answer using attack labels?
5. Are pseudo-labels evaluated independently from the model that generated them?
6. Are MICO and leave-one-attack-out protocols leakage-safe?
7. Does single-image inference remain true despite training on video datasets?
8. Are score fusion, capacity-matched fusion, and uncertainty baselines sufficient?
9. Do heatmap experiments test faithfulness rather than visual plausibility?
10. Is the deployment claim supported by an inference path without a large VLM?

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
