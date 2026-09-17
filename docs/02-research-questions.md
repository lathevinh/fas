# Research Questions and Hypotheses

## RQ1: Cross-foundation complementarity

Do independently pretrained self-supervised visual and vision-language models make
usefully different errors under domain and attack shifts?

For source-selected decision thresholds, report the joint correctness table on each
untouched target:

| DINO | VLM | Probability |
|---|---|---:|
| correct | correct | $P_{cc}$ |
| correct | wrong | $P_{cw}$ |
| wrong | correct | $P_{wc}$ |
| wrong | wrong | $P_{ww}$ |

**H1:** The VLM recovers a useful fraction of DINO errors, especially false accepts,
and class-conditional double-fault rates permit lower oracle APCER/BPCER than the
better branch across multiple domains or attack families. Complementarity may be
asymmetric; equal recovery in both directions is not required.

**Falsification:** VLM recovery of DINO errors and false accepts falls below the
source-preregistered continuation criteria, errors are nearly identical, or
class-conditional oracle gain is negligible. A large $P_{cw}+P_{wc}$ alone is
insufficient when both predictors are weak.

The cross-foundation-specific claim additionally requires positive heterogeneity
advantage over the shared-encoder head-diversity control on confirmatory targets.

Required analyses include error correlation, double-fault, oracle gain, attack/domain
stratification, feasible fusion gain, a shared-encoder DINO head-diversity control,
and a supervised visual head on the frozen VLM image encoder. Conditional mutual information is
optional and must not replace the directly interpretable joint table.

## RQ2: Source-only failure detection under shift

Can natural cross-foundation disagreement estimate prediction failures under unseen
domain and attack shifts better than conventional single-model uncertainty without
target-domain calibration?

The raw baseline is:

$$D(x)=D_{JS}(p_D\|p_V).$$

The proposed calibrator is trained from out-of-fold source predictions. Each fold
holds out a source domain or attack family as a pseudo-shift, trains the predictors
on the remainder, and records correctness, uncertainty, and disagreement on the
held-out fold. Target data never train or select the calibrator.

**H2:** Raw or source-calibrated disagreement improves error AUROC/AUPR and selective
risk at matched coverage over maximum softmax probability, entropy, energy,
representation-space confidence, and the better branch's uncertainty.

**Falsification:** disagreement does not consistently beat these baselines, fails on
shared errors, or requires target-domain labels or tuning.

Explicit-disagreement wording additionally requires positive $\Delta_{dis}$ from the
fixed absolute-difference feature over capacity-matched models receiving both branch
probabilities and the same quality features.

## RQ3: Selective deployment

Does the semantic branch provide enough recoverable information to justify its cost,
and can it be invoked conditionally without losing the security benefit?

Compare DINO-only, VLM-only, always-on dual inference, score averaging, learned score
fusion, disagreement-aware selection, DINO-first conditional VLM, and an optional
distilled semantic head.

**H3:** Conditional VLM inference approaches always-on selective performance while
reducing VLM invocation rate or GPU-ms/request at matched APCER/BPCER and coverage.

**Falsification:** always-on VLM gives no gain over DINO, conditional invocation loses
the gain, or the desired operating point offers no useful security-coverage-compute
trade-off.

## Secondary ablations, not research questions

- DINOv2 versus DINOv2-Reg;
- class token versus attention-pooled patch features;
- face crop versus context crop;
- frozen versus LoRA-tuned branches;
- coarse semantic prompt families;
- qualitative patch evidence and deletion tests.

Named micro-forensic cues, learned ontology edges, and counterfactual cue synthesis
are deferred unless RQ1-RQ3 establish a strong signal.
