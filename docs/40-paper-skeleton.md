# Frozen Paper Skeleton

Date: 2026-09-18

## Working title

**Source-Domain Cross-Fitted Failure-Risk Estimation for Selective Face Presentation
Attack Detection**

The method is named **Domain-OOF Failure Risk Estimation**. The title must not add
`Disagreement` unless its preregistered incremental test passes. Heterogeneous
foundation models are the primary instantiation, not the claimed algorithmic novelty.

## 1. Introduction

Cross-domain face PAD classifiers can be confidently wrong when capture conditions or
attack distributions shift. Conventional confidence learned from in-distribution or
sample-level held-out predictions may not expose those deployment-like failures.

We test whether leave-one-source-domain-out predictors create more transferable
failure supervision than matched sample-OOF predictors. The fixed primary
instantiation combines independently pretrained DINOv2-Reg and OpenCLIP predictors,
but the central object is the source-domain cross-fitting procedure used to generate
failure labels for a separate target-blind risk estimator.

The manuscript asks only two core questions:

1. **RQ1:** Does domain-OOF failure supervision improve error ranking for one fixed
   heterogeneous classifier over matched sample-OOF supervision?
2. **RQ2:** Does the complete DINOv2-Reg/OpenCLIP selective system outperform a matched
   DINOv2-Reg/plain-DINOv2 selective system under the same protocol?

Planned contributions, stated as methods and evaluations rather than results:

1. A source-domain cross-fitted failure-risk framework whose supervision comes from
   leave-one-source-domain-out prediction failures rather than random/sample-level
   OOF predictions.
2. A controlled heterogeneous DINOv2-Reg/OpenCLIP instantiation that preserves
   independent predictors and is compared with single-branch and matched same-family
   systems.
3. A strict fold-local target-exclusion evaluation connecting failure ranking to source-selected
   PAD security, usability, class coverage, and K=1 transaction outcomes over four
   MCIO folds.

## 2. Related Work

Organize the section around four boundaries:

1. **Domain-generalizable and language-guided FAS.** FLIP, AIM-FAS, DGPDL, CLIP-SA,
   and related methods establish that CLIP/VLM adaptation, prompts, and semantic
   alignment for cross-domain FAS are not novel.
2. **Reliability-aware FAS.** CA-FAS is a first-class competitor. A simple
   Mahalanobis score is only a representation-space control, not a CA-FAS
   reproduction.
3. **Reliability-aware VLM FAS.** RPSR-FAS uses reliability during classifier
   training. The proposed method instead learns a separate post-predictive selector
   from source-domain-held-out failures.
4. **General learned confidence and selective prediction.** Logistic confidence,
   abstention, cross-validation, and disagreement are established tools. The claim is
   their domain-OOF supervision and evaluation under the stated PAD shift protocol.

Required positioning sentence:

> Unlike reliability-aware FAS methods that use reliability to improve classifier
> training, we use source-domain-held-out prediction failures as supervision for a
> separate target-blind failure-risk model.

Do not claim first VLM FAS, first reliability-aware FAS, first learned confidence, or
first use of disagreement.

## 3. Method

### 3.1 Fixed independent predictors

- frozen `dinov2_vitb14_reg4`, class token plus mean patch pooling, and a small PAD
  head;
- frozen OpenCLIP `ViT-B-16`, `laion2b_s34b_b88k`, native 224 preprocessing, fixed
  generic binary prompts, and a fixed 1.30 context crop;
- independent monotone affine source calibration for each branch;
- calibrated average as the fixed reference classifier.

No feature alignment, agreement loss, adaptive primary prompt selection, or target
adaptation is part of the core method.

### 3.2 Domain-OOF Failure Risk Estimation

For source domains $\mathcal S=\{S_1,\ldots,S_K\}$, hold out each $S_k$ in turn,
fit and calibrate the branches on the allowed remainder, predict $S_k$, and record

$$
z_i=[\widehat p_D,\widehat p_V,|\widehat p_D-\widehat p_V|,q_i],
\qquad
e_i=\mathbf 1[g_{DV}(x_i)\ne y_i].
$$

A fixed-regularization logistic model learns a failure-risk score $r_\theta(z)$ from
the union of held-out-domain records. Probability language is reserved for cases where
held-out source Brier, NLL, and reliability checks support calibration. The matched
sample-OOF control uses the same candidate universe, feature family, loss, weighting,
optimization budget, and final target predictions; only the OOF supervision
construction differs. RQ1 tests this complete construction, not a causal effect of
domain identity alone.

The primary RQ1 estimand is

$$
\Delta_{OOF}=AP(e_{DV},r_{DVd}^{domain})-
AP(e_{DV},r_{DVd}^{sample}),
$$

with error as the positive class and larger scores indicating greater risk.

### 3.3 Selective policy

Gate thresholds are selected only from allowed source holdouts. Under K=1, predicted
spoof and abstain are both terminal non-accept. Report attack and bona-fide coverage,
blocked live decisions, attacks newly blocked, bona-fide transactions newly rejected,
`FA_end2end`, and `BFNR_end2end`.

### 3.4 Secondary analyses

Explicit disagreement, fusion rescue, SiW-M attack shift, policy margin, routing,
LoRA, and cue analysis are secondary. Their failure cannot invalidate a supported RQ1
risk-ranking result, and their success cannot rescue a failed primary estimand.

## 4. Experimental Protocol

- Four pre-specified MCIO outer-domain-held-out folds: three source domains and one
   excluded target per fold. They are not described as independent external domains.
- No labeled pilot and no target-dependent model, prompt, threshold, feature, or
  analysis selection.
- Three fixed seeds, per-target reporting, and paired subject/video cluster bootstrap.
- Primary RQ1 endpoint: non-interpolated prediction-error AP on fixed errors.
- Primary AP applicability: at least 20 erroneous target transactions/videos per seed,
   with dependence handled by subject/video cluster bootstrap;
   underpowered target/seed contributions remain reported but cannot count as positive
   evidence, and a pass requires at least three eligible targets.
- Operational validation: AURC/selective curves and end-to-end K=1 outcomes.
- RQ2 compares complete heterogeneous and same-family systems; cross-system raw AP is
  descriptive because the classifiers and error sets differ.
- SiW-M is optional external attack-shift validation and does not block the core paper.

### Literature context outside the main tables

Track A is a compact preliminary subsection or supplementary table only. It establishes
that the classifier is not obviously incompetent relative to historical MCIO work and
hosts no RQ, novelty claim, controlled superiority claim, or main-table panel. Preserve
its frozen source-only thresholds, detector-conditional population, SSDG/FLIP caveats,
and two-engineer-day stop rule from Document 42.

## 5. Planned Main Tables

The identities and purposes of these four tables are frozen before implementation.
Columns may gain lineage or uncertainty fields, but a table may not be replaced or
redefined after target inspection.

### Table 1: Strict single-image classifier competence

Use only the Track-B transaction/sample universe. Report per-target and four-domain
macro classifier quality before risk gating. Source-only competence is frozen before
target evaluation. The heterogeneous reference must pass for RQ1 and both complete
systems must pass for RQ2: finite nonconstant scores, both-class support, finite
calibration, macro AUROC and balanced accuracy at least 0.55, and macro-AUROC 95% LCB
above 0.50. Reference source-OOF risk labels also require at least 20 errors and 20
correct predictions. The shared DINO anchor must be nondegenerate. A branch missing
the 0.55/LCB rule loses only its standalone-competence claim; in particular, OpenCLIP
failure does not block a core RQ if the dependent complete systems pass. Target
outcomes report performance but never trigger method alteration.

| System | APCER | BPCER | ACER/HTER | AUROC | Error prevalence |
|---|---:|---:|---:|---:|---:|
| DINOv2-Reg | planned | planned | planned | planned | planned |
| OpenCLIP | planned | planned | planned | planned | planned |
| Calibrated heterogeneous average | planned | planned | planned | planned | planned |
| DINOv2-Reg + plain-DINOv2 average | planned | planned | planned | planned | planned |

Purpose: establish branch and reference-classifier competence without treating
classifier improvement as evidence for risk-estimator quality.

### Table 2: RQ1 risk transfer

| Risk score on fixed heterogeneous errors | Error AP | Error AUROC | AURC/excess-AURC | Paired delta vs domain-OOF |
|---|---:|---:|---:|---:|
| Fused MSP/entropy | planned | planned | planned | planned |
| Operational boundary distance | planned | planned | planned | planned |
| DINO Mahalanobis control | planned | planned | planned | planned |
| Matched sample-OOF $R_{DVd}$ without $q$ | planned | planned | planned | planned |
| Matched sample-OOF $R_{DVd}$ | planned | planned | planned | planned |
| Domain-OOF $R_{DVd}$ without $q$ | planned | planned | planned | planned |
| Domain-OOF $R_{DVd}$ | planned | planned | planned | reference |

Purpose: test the primary methodological claim while holding classifier predictions
and error labels fixed. A faithful CA-FAS row is added only if protocol-compatible
reproduction is feasible; it is never relabeled as the Mahalanobis control.

### Table 3: Selective PAD utility

| Source-selected gate | Attack coverage | Bona-fide coverage | `FA_end2end` | `BFNR_end2end` | AURC |
|---|---:|---:|---:|---:|---:|
| Required comparator gates | planned | planned | planned | planned | planned |
| Sample-OOF risk gate | planned | planned | planned | planned | planned |
| Domain-OOF risk gate | planned | planned | planned | planned | planned |

Purpose: validate whether ranking gains yield a useful security-usability trade-off.
Lack of gain at one operating point weakens that operational claim but does not by
itself falsify a positive fixed-error ranking result.

### Table 4: RQ2 heterogeneous versus same-family systems

| Complete system | Classification quality | Error prevalence | Error AP | Selective utility | K=1 outcomes |
|---|---|---:|---:|---|---|
| DINOv2-Reg + OpenCLIP | planned | planned | planned | planned | planned |
| DINOv2-Reg + plain DINOv2 | planned | planned | planned | planned | planned |

Purpose: compare complete matched systems without claiming that heterogeneous
pretraining causally produces any observed difference. The sole primary scalar is
$\Delta_{RQ2}=U_{same}-U_{hetero}$, where $U$ is the equally weighted attack/bona-fide
raw AURC. A pass requires macro $\Delta\ge0.01$, paired 95% LCB above zero, three
positive targets, two positive seed macros, and no target selective harm above 0.02.
Both systems use the common fixed-detector-success population for AURC. Detector
failures enter full-denominator K=1 end-to-end metrics and coverage accounting, not
the AURC ordering.
At source-selected gates, neither macro `FA_end2end` nor macro `BFNR_end2end` may
worsen by more than 0.01, and neither may worsen by more than 0.02 on any target.
Classification quality, error AP, error prevalence, and class coverage are supporting
results and cannot substitute for this rule. Coverage is explanatory and has no
additional RQ2 pass/fail threshold.

## 6. Claim and Falsification Matrix

| Claim | Primary evidence | Required controls | Falsification or reframe |
|---|---|---|---|
| Domain-OOF supervision transfers better | Positive preregistered paired macro $\Delta_{OOF}^{AP}$ on fixed errors, with minimum effect, consistency, uncertainty, and $N_{error,min}$ applicability | Matched sample-OOF and fixed-error confidence baselines | If unsupported, stop the Domain-OOF method claim |
| Failure ranking is operationally useful | Better source-selected selective trade-off with explicit class coverage and K=1 accounting | Comparator gates under identical transaction semantics | If unsupported, retain at most a ranking result and remove practical utility wording |
| Studied heterogeneous system is advantageous | Better complete-system outcomes than the matched DINO-DINO system | Shared DINO anchor, data, calibration, risk, gate, and accounting | If unsupported, remove heterogeneous-foundation advantage and reframe around RQ1 |
| Explicit disagreement adds value | Capacity-matched positive $\Delta_{dis}$ on fixed errors | Nonlinear probability-only risk model | If unsupported, remove disagreement from title and contributions |
| Fusion improves classification | Net APCER benefit with disclosed BPCER/BFNR harm and rescue counts | Branches and same-family classifier | If unsupported, remove only classifier-benefit wording |
| Routing saves compute | Matched-security/coverage latency and invocation benefit | Always-on dual system | If unsupported or unrun, omit routing claim |

## Freeze rule

This skeleton freezes the paper story, two core RQs, primary estimand, four main-table
roles, and claim dependencies before Phase 0 coding. Later changes require a dated
amendment made before any affected target result is inspected. No planned cell is an
observed result.