# Research Questions and Hypotheses

## RQ1: Source-only failure-risk transfer

Does source-domain OOF failure supervision improve transferable prediction-error
ranking over matched sample-OOF supervision for the same final classifier errors?

**H1:** Domain-OOF risk training yields a positive preregistered paired four-target
macro gain in non-interpolated prediction-error AP for the fixed heterogeneous
classifier, relative to matched sample-OOF training. The claim also requires the
frozen minimum effect, consistency, event-count, and uncertainty rules.

**Falsification:** The fixed-error AP contrast does not pass its frozen rule or requires
target-domain tuning. Failure of one selective operating point does not by itself
falsify a supported RQ1 ranking result.

**Secondary operational consequence:** Test whether any ranking gain translates into
a better source-selected security-usability trade-off with explicit attack/bona-fide
coverage and K=1 accounting. This is downstream validation, not part of H1.

RQ1 evaluates the complete domain-OOF construction, whose held-out-domain predictors
may have different fit sizes, error prevalence, error composition, and calibration
difficulty from sample-OOF predictors. It does not identify a causal effect of domain
identity alone. The valid claim is that the complete construction yields more
transferable failure supervision across the evaluated MCIO domains.

## RQ2: Heterogeneous versus same-family complete systems

Does the complete DINOv2-Reg plus OpenCLIP selective system provide better held-out-
domain system outcomes than a matched DINOv2-Reg plus plain-DINOv2 selective system?

For source-selected decision thresholds, report the joint correctness table on each
held-out official target evaluation partition:

| DINO | VLM | Probability |
|---|---|---:|
| correct | correct | $P_{cc}$ |
| correct | wrong | $P_{cw}$ |
| wrong | correct | $P_{wc}$ |
| wrong | wrong | $P_{ww}$ |

**H2:** Under matched data, calibration, risk fitting, gate selection, and transaction
accounting, the heterogeneous system reduces class-balanced AURC relative to
the same-family control. For system $j$, define

$$
U_j=\frac12(AURC_{attack,j}+AURC_{bona,j}),
$$

and $\Delta_{RQ2}=U_{same}-U_{hetero}$, so positive values favor the heterogeneous
system. Both systems' AURCs use the identical fixed-detector-success transaction mask;
detector failures enter only full-denominator K=1 `FA_end2end`, `BFNR_end2end`, and
coverage accounting. The paired macro must have 95% lower bound above zero and point gain at least
$\delta_{RQ2,min}=0.01$. At each system's source-selected gate, heterogeneous-minus-
same-family `FA_end2end` and `BFNR_end2end` may each increase by at most 0.01 in the
four-target macro and 0.02 on any target. Classification errors, each system's error
AP, and achieved class coverage are mandatory supporting results, not alternative
primary outcomes. Coverage is explanatory only and is not an additional H2 pass/fail
guardrail.

**Falsification:** The scalar contrast or either operational guardrail does not pass
its frozen rule. Each
system's risk AP remains descriptive because the classifiers and error labels differ;
higher cross-system risk AP alone cannot establish heterogeneous predictive value.

Required classifier diagnostics are standalone DINOv2-Reg and OpenCLIP performance,
the fixed heterogeneous fusion, the matched DINOv2-Reg/plain-DINOv2 control, joint
correctness/double fault, and a simple directional rescue summary. Complementarity may
be asymmetric. Extensive oracle diagnostics, a supervised CLIP visual head,
shared-encoder head diversity, and conditional mutual information are optional
appendix analyses and cannot determine RQ1.

### Attribution ablations, not research questions

Domain-OOF and attack-OOF are separate protocols. For every MCIO fold, the entire
target domain is excluded from model, checkpoint, preprocessing, threshold, prompt,
and risk-gate selection. The primary VLM, preprocessing, prompts, and analysis rules
are fixed globally before any target result; all four MCIO targets are pre-specified
outer-domain-held-out folds.

On fixed heterogeneous classifier errors, report whether cross-foundation probabilities
outperform either single-branch learned-risk baseline
($\Delta_{CF}^{AP}>0$), and whether explicit absolute-difference disagreement adds
capacity-matched incremental value ($\Delta_{dis}^{AP}>0$). Report $R_{DVd}$ with and
without quality features $q$ as a visible attribution result.

If only the `+q` variant succeeds, interpret the mechanism as transferable
failure/nuisance signatures rather than cross-branch evidence alone. If
$\Delta_{dis}$ fails, remove disagreement-centered framing. SiW-M attack-shift
evaluation remains optional and is not part of either core RQ.

Explicit-disagreement wording requires positive $\Delta_{dis}$ from the fixed
absolute-difference feature over capacity-matched models receiving both branch
probabilities and the same quality features.
The signed policy margin is excluded from both scientific claim quantities; its
deployment contribution is measured separately as $\Delta_{margin}^{AP}$.

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
