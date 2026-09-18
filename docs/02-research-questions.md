# Research Questions and Hypotheses

## RQ1: Source-only failure-risk transfer

Does source-domain cross-fitted error supervision improve transferable failure ranking
and selective security-usability under unseen domains relative to sample-OOF training,
single-branch confidence, and matched learned-risk baselines?

**H1:** Domain-OOF risk training improves prediction-error AUPR and selective utility
for the fixed heterogeneous classifier. The paired four-target macro gain has a
positive preregistered lower confidence bound, at least three of four target estimates
are positive, and no target exceeds the preregistered class-specific harm tolerance.

**Falsification:** Failure ranking or selective utility does not improve over the
required controls, requires target-domain tuning, or hides attack/bona-fide harm.

## RQ2: Heterogeneous predictive value and attribution

Do independently pretrained self-supervised visual and vision-language models provide
failure information beyond either branch and a matched same-family pair?

For source-selected decision thresholds, report the joint correctness table on each
held-out official target evaluation partition:

| DINO | VLM | Probability |
|---|---|---:|
| correct | correct | $P_{cc}$ |
| correct | wrong | $P_{cw}$ |
| wrong | correct | $P_{wc}$ |
| wrong | wrong | $P_{ww}$ |

**H2:** Cross-foundation probabilities improve risk estimation beyond either
single-branch learned-risk model and the DINOv2-Reg plus plain-DINOv2 system at the
same claimed endpoint. Complementarity may be asymmetric; equal recovery in both
directions is not required.

**Falsification:** Cross-foundation risk transfer does not exceed either single-branch
baseline or matched same-family risk transfer. The claim then becomes a broader
selective-ensemble result if RQ1 still passes.

The cross-foundation-specific claim additionally requires positive paired
heterogeneity advantage over frozen DINOv2-Reg plus plain DINOv2 on confirmatory
targets. Shared-encoder head diversity is only a sanity control.

Required analyses include error correlation, double-fault, oracle gain, attack/domain
stratification, feasible fusion gain, a shared-encoder DINO head-diversity control,
and a supervised visual head on the frozen VLM image encoder. Conditional mutual information is
optional and must not replace the directly interpretable joint table.

### Secondary attribution hypotheses

Can a source-only cross-fitted risk model using independently calibrated
cross-foundation predictions improve failure detection under domain and attack shift,
and does explicit absolute-difference disagreement add value beyond the two branch
probabilities?

Domain-OOF and attack-OOF are separate protocols. For every MICO fold, the entire
target domain is excluded from model, checkpoint, preprocessing, threshold, prompt,
and risk-gate selection. The primary VLM, preprocessing, prompts, and analysis rules
are fixed globally before any target result; all four MICO targets are confirmatory.

On the preregistered primary metric, prediction-error AUPR,
cross-foundation probabilities plus fixed quality features outperform quality-only
and either single-branch learned-risk baseline
($\Delta_{CF}^{AUPR}>0$), while explicit absolute-difference disagreement adds
capacity-matched incremental value ($\Delta_{dis}^{AUPR}>0$).

If $\Delta_{CF}$ is not repeatably positive, the risk model requires
target-domain tuning, or failure detection collapses on shared errors. If only
$\Delta_{dis}$ fails, retain the dual-branch result but remove disagreement-centered
framing.

Explicit-disagreement wording requires positive $\Delta_{dis}$ from the fixed
absolute-difference feature over capacity-matched models receiving both branch
probabilities and the same quality features.
The signed policy margin is excluded from both scientific claim quantities; its
deployment contribution is measured separately as $\Delta_{margin}^{AUPR}$.

### Separate classifier hypothesis

Realized fusion rescue, net APCER change, and BPCER change test whether the fixed
calibrated average improves classification. FARR remains descriptive and cannot hide
attacks newly admitted by fusion. Failure here removes the classifier-benefit claim,
not RQ1 or RQ2.

## Secondary study: Conditional deployment

Does the semantic branch provide enough recoverable information to justify its cost,
and can it be invoked conditionally without losing the security benefit?

Compare DINO-only, VLM-only, always-on dual inference, score averaging, learned score
fusion, disagreement-aware selection, DINO-first conditional VLM, and an optional
distilled semantic head.

**Hypothesis:** Conditional VLM inference approaches always-on selective performance while
reducing VLM invocation rate or GPU-ms/request at matched APCER/BPCER and coverage.

**Falsification:** always-on VLM gives no gain over DINO, conditional invocation loses
the gain, or the desired operating point offers no useful security-coverage-compute
trade-off.

## Secondary ablations, not research questions

- DINOv2 versus DINOv2-Reg;
- fixed class-token plus mean-patch pooling versus learned attention pooling;
- face crop versus context crop;
- frozen versus LoRA-tuned branches;
- coarse semantic prompt families;
- qualitative patch evidence and deletion tests.

Named micro-forensic cues, learned ontology edges, counterfactual cue synthesis, and
conditional routing are deferred unless the two core research questions establish a
strong signal.
