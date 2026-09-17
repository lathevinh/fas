# Response to ChatGPT Review (Round 6)

Date: 2026-09-17

## Verdict

The review correctly identifies identifiability and fairness gaps that remain despite
the stable architecture. The main method stays frozen; controls and evaluation rules
are tightened before Stage 2.

## Accepted

1. Risk scores are compared on identical error labels from one fixed classifier;
   whole-system comparisons are reported separately.
2. Error prevalence, normalized AUPR context, paired within-target differences, and
   macro target deltas accompany raw prediction-error AUPR.
3. The accept threshold is selected from second-level meta-OOF source predictions,
   then the fixed logistic gate is refit on all OOF records.
4. The primary $g_{ref}$ is deterministic calibrated averaging; learned fusion is an
   ablation.
5. An immutable generic core PAD prompt bank is separated from auxiliary attack
   prompts, and the mean-cosine binary VLM formula is frozen before confirmation.
6. OOF-to-full-source feature drift, sample-OOF versus domain-OOF, finite-sample APCER
   confidence bounds, and risk probability calibration are reported.
7. Image-quality features, detector-failure action, and middle-valid-frame selection
   are fixed before target evaluation.
8. Resolved calibrator and transaction-policy questions are removed from the open list.

## Accepted with qualification

### Homogeneous ensemble control

This control is essential to distinguish cross-foundation rescue from generic
ensemble diversity. Two independently trained PAD heads on one frozen DINO encoder
are a cheap minimum control, but shared deterministic features can underestimate a
fully independent homogeneous ensemble. Conclusions will state that limitation; a
second DINO variant is a stronger follow-up if compute permits.

### CLIP/SigLIP supervised visual head

The control is useful because it holds the VLM image encoder fixed while changing
prompt-driven versus source-supervised adaptation. It does not causally isolate text
semantics by itself: the objectives and amount of FAS supervision also differ. The
paper may claim stronger evidence for semantic priors only when this control and
transfer subgroup results agree.

### Domain-identifiability and distribution shift

Feature normalization, domain-ID auditing, and OOF-to-full-source drift measurement
are accepted. Domain predictability remains a diagnostic rather than an automatic
invalidity criterion because genuine failure-relevant shift can also encode domain.

## Rejected or deferred

No central correction is rejected. Training multiple fully independent DINO
backbones is deferred from the minimum RTX 4080 experiment; the shared-backbone
multi-head control is explicitly labeled weaker rather than presented as definitive.

## Implementation decision

Stage 1 adds only diagnostic controls, not modules to the proposed model. Stage 2 uses
calibrated-average predictions, fixed-error risk comparison, meta-OOF thresholding,
and a separate end-to-end system table.