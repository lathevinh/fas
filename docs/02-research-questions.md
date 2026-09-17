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

**H1:** Both $P_{cw}$ and $P_{wc}$ are non-trivial, the double-fault rate $P_{ww}$
permits an oracle accuracy $1-P_{ww}$ above the better branch, and complementarity
persists across multiple domains or attack families.

**Falsification:** one branch dominates, errors are nearly identical, or oracle gain
over the better branch is negligible. A large $P_{cw}+P_{wc}$ alone is insufficient
when both predictors are weak.

Required analyses include error correlation, double-fault, oracle gain, attack/domain
stratification, and feasible fusion gain. Conditional mutual information is optional
and must not replace the directly interpretable joint table.

## RQ2: Source-only failure and unknown detection

Can natural cross-foundation disagreement estimate errors and unknown attacks better
than conventional single-model uncertainty without target-domain calibration?

The raw baseline is:

$$D(x)=D_{JS}(p_D\|p_V).$$

The proposed calibrator is trained from out-of-fold source predictions. Each fold
holds out a source domain or attack family as a pseudo-shift, trains the predictors
on the remainder, and records correctness, uncertainty, and disagreement on the
held-out fold. Target data never train or select the calibrator.

**H2:** Raw or source-calibrated disagreement improves error/unknown AUROC and AUPR,
and selective risk at matched coverage, over maximum softmax probability, entropy,
energy, and the better branch's uncertainty.

**Falsification:** disagreement does not consistently beat these baselines, fails on
shared errors, or requires target-domain labels or tuning.

## RQ3: Selective deployment

Does the semantic branch provide enough recoverable information to justify its cost,
and can it be invoked conditionally without losing the security benefit?

Compare DINO-only, VLM-only, always-on dual inference, score averaging, learned score
fusion, disagreement-aware selection, DINO-first conditional VLM, and an optional
distilled semantic head.

**H3:** Conditional VLM inference approaches always-on selective performance while
reducing median latency or VLM invocation rate at matched APCER/BPCER and coverage.

**Falsification:** always-on VLM gives no gain over DINO, conditional invocation loses
the gain, or the desired operating point offers no useful security-latency trade-off.

## Secondary ablations, not research questions

- DINOv2 versus DINOv2-Reg;
- class token versus attention-pooled patch features;
- face crop versus context crop;
- frozen versus LoRA-tuned branches;
- coarse semantic prompt families;
- qualitative patch evidence and deletion tests.

Named micro-forensic cues, learned ontology edges, and counterfactual cue synthesis
are deferred unless RQ1-RQ3 establish a strong signal.
