# Research Questions and Hypotheses

## RQ1: Cross-foundation complementarity

Do independently pretrained self-supervised visual and vision-language models make
usefully different errors under domain and attack shifts?

For source-selected decision thresholds, report the joint correctness table on each
held-out official target evaluation partition:

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

The cross-foundation-specific claim additionally requires positive paired
heterogeneity advantage over frozen DINOv2-Reg plus plain DINOv2 on confirmatory
targets. Shared-encoder head diversity is only a sanity control.

Required analyses include error correlation, double-fault, oracle gain, attack/domain
stratification, feasible fusion gain, a shared-encoder DINO head-diversity control,
and a supervised visual head on the frozen VLM image encoder. Conditional mutual information is
optional and must not replace the directly interpretable joint table.

## RQ2: Source-only failure detection under shift

Can a source-only cross-fitted risk model using independently calibrated
cross-foundation predictions improve failure detection under domain and attack shift,
and does explicit absolute-difference disagreement add value beyond the two branch
probabilities?

Domain-OOF and attack-OOF are separate protocols. Official confirmatory evaluation
partitions never train, select, or calibrate any model, threshold, prompt, or risk gate.
Under the global-development estimand, train/dev partitions from a future confirmatory
domain may have acted as sources when selecting the candidate on the MSU-MFSD pilot;
this is test-partition-unseen, not strict outer-domain-unseen selection.

**H2:** On the preregistered primary metric, prediction-error AUPR,
cross-foundation probabilities plus fixed quality features outperform quality-only
and either single-branch learned-risk baseline
($\Delta_{CF}^{AUPR}>0$), while explicit absolute-difference disagreement adds
capacity-matched incremental value ($\Delta_{dis}^{AUPR}>0$).

**Falsification:** $\Delta_{CF}$ is not repeatably positive, the risk model requires
target-domain tuning, or failure detection collapses on shared errors. If only
$\Delta_{dis}$ fails, retain the dual-branch result but remove disagreement-centered
framing.

Explicit-disagreement wording requires positive $\Delta_{dis}$ from the fixed
absolute-difference feature over capacity-matched models receiving both branch
probabilities and the same quality features.
The signed policy margin is excluded from both scientific claim quantities; its
deployment contribution is measured separately as $\Delta_{margin}^{AUPR}$.

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
