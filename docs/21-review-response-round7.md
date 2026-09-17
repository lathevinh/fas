# Response to ChatGPT Review (Round 7)

Date: 2026-09-17

## Verdict

The review correctly exposes remaining mathematical ambiguity and places valid kill
conditions on both `cross-foundation` and `disagreement` in the title. The architecture
does not change.

## Accepted

1. Each branch has one raw logit and one temperature calibrator. $T_V$ is
   $\operatorname{Cal}_V$, so no second probability calibration is stacked.
2. The immutable core prompt bank is primary; source-tuned prompts remain an ablation.
3. Explicit disagreement must add value over capacity-matched models receiving both
   branch probabilities and quality, otherwise disagreement-centered framing is removed.
4. Absolute probability difference is frozen as the simplest primary score. JS,
   hard-decision, and log-odds disagreement are ablations rather than source-selected
   alternatives.
5. Classifier, fixed-prediction risk-score, and end-to-end system comparisons remain
   separate through Stage 3.
6. The primary feature vector is frozen to two calibrated probabilities, one selected
   disagreement score, and five fixed quality features. Entropy, energy, and
   Mahalanobis are ablations/baselines.
7. False-accept/false-reject AUPR and class-aware risk-coverage complement global
   prediction-error AUPR and excess-AURC.
8. Independent-video counts determine whether low-APCER points are statistically
   constrained or only nominal diagnostics.
9. The middle protocol frame is selected before face detection; always-on dual is a
   reference under fixed $g_{ref}$, not an accuracy upper bound.
10. Resolution and preprocessing are reported and treated as possible diversity
    confounds.
11. Heterogeneity advantage over same-family diversity becomes a central estimand.

## Accepted with qualification

### Gate-threshold selection

The review is right that a meta-OOF threshold need not retain its meaning after a
final refit. Version 1 uses a subject/video-disjoint source-only gate-calibration
partition: fit the final gate once, select its threshold on that untouched partition,
and never refit afterward. Meta-OOF remains a sensitivity analysis.

### Same-family control

Two independently trained heads on one frozen DINO representation are renamed a
`shared-encoder head-diversity control`. Independent video bootstraps, augmentations,
initialization, and nonlinear heads make it less trivial, but it remains weaker than
independent representations. Frozen DINOv2-Reg plus plain DINOv2 is the stronger
follow-up when compute permits.

### Mechanistic interpretation

The system claim is empirical heterogeneous rescue. Local-forensic versus semantic
inductive bias remains a hypothesis because CLIP visual-head, prompt, resolution, and
preprocessing controls do not establish a unique causal mechanism.

## Rejected or deferred

The three named 2026 papers and class-aware selective-classification work are not
added as verified citations solely from review text. They enter a verification queue
until title, authors, venue, year, and DOI or stable publisher record are independently
confirmed. This avoids propagating plausible but unverified bibliography.

## Reframing rules

- Strong heterogeneous rescue but no incremental explicit-disagreement gain:
  `Cross-Foundation Selective Failure Prediction`.
- No advantage over same-family diversity: broader selective-ensemble PAD framing.
- Neither rescue nor selective reliability passes preregistered criteria: stop the
  dual-foundation model-centric direction.