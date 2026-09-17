# Response to ChatGPT Review (Round 3)

Date: 2026-09-17

## Verdict by recommendation

### Accept: correct the unseen-attack terminology

The prior definition of `open-vocabulary unknown` was reversed. The revised protocol
now distinguishes:

- **downstream-unseen PAI:** no downstream FAS image supervision and no attack-specific
  prompt;
- **open-vocabulary zero-shot PAI:** no downstream FAS image supervision, while an
  attack-specific prompt is allowed.

The phrase `true unknown` is removed. Generic foundation-model pretraining exposure is
uncontrolled, so the project can only claim unseen status relative to downstream FAS
supervision and prompting.

### Accept: calibrate simple fusion fairly

The principal average baseline now uses independently calibrated probabilities:

$$p_{avg}=\frac{\widehat p_D+\widehat p_V}{2}.$$

Raw averaging remains a diagnostic, and learned fusion receives calibrated source
scores. This prevents calibrated disagreement from being compared with an artificially
weak ensemble.

### Accept: keep one risk model in version 1

Separate false-accept and false-reject risk heads are not added. The deployment study
instead maximizes coverage subject to source-selected APCER constraints, with achieved
target APCER/BPCER, VLM invocation, retry rate, and latency reported explicitly.

### Accept with an additional safeguard: OOF calibration

Sample-OOF and domain-OOF remain useful comparisons, with domain-OOF primary. The
protocol now also requires disjoint branch-fitting and probability-calibration
partitions inside each fold. Otherwise calibration and risk estimation could be
optimistically evaluated on reused source samples.

### Reject as written: oracle AUC illustration

The review is right that oracle headroom is the Stage 1 kill criterion, but `oracle
AUC` is not automatically well-defined. Selecting the correct branch per sample uses
the ground-truth label; it yields an oracle decision/error bound at fixed thresholds,
not a label-independent continuous score with a valid ROC curve.

The main report will therefore use:

- oracle balanced accuracy or minimum error from source-selected branch decisions;
- oracle gain over the better branch;
- oracle APCER/BPCER behavior at source-selected operating points;
- $P_{cc},P_{cw},P_{wc},P_{ww}$ and double-fault rate.

An oracle AUC will only be reported if a precise label-independent score construction
is defined. This correction preserves the review's intended hard kill test without
using an ambiguous metric.

## Final position

No architectural redesign is needed before Stage 1. The protocol corrections above
are adopted, while the ambiguous oracle-AUC formulation is replaced by decision-level
oracle headroom. Implementation should begin after dataset access and split manifests
are verified.