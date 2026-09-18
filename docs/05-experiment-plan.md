# Experiment and Implementation Plan

## Stage 0: Audit and infrastructure, weeks 1-2

Tasks:

- obtain datasets and archive their agreements;
- verify every official protocol and label mapping;
- implement manifests, leakage checks, metrics, and deterministic frame sampling;
- compare the exact settings of TIFS 2024 Evidential Semantic Consistency,
  Confidence Aware Learning, RPSR-FAS, DINO-VPT, and primitive-driven prompting;
- freeze the literature table and search for newer overlapping work.
- preregister `configs/prompts_core_v1.yaml`, `configs/prompts_aux_v1.yaml`, and a
  single primary `configs/vlm_checkpoint_v1.yaml` artifact before locked
  evaluation. The primary is OpenCLIP `ViT-B-16`, `laion2b_s34b_b88k`, native
  224-pixel preprocessing, and the fixed context crop. Record exact prompt strings,
  classes, weights, tokenizer, interpolation, normalization, and weight hash.
- defer checkpoint/preprocessing candidate search to a secondary robustness study;
  it cannot replace the globally fixed primary in the core tables.

Exit criteria:

- no subject/video leakage;
- independently reproducible split counts;
- APCER/BPCER/ACER tests pass on synthetic examples.
- core prompts, primary VLM/preprocessing, and all analysis-rule generation logic are
  frozen before the first of four outer-domain-held-out MCIO results.
- Round 15 records `METHODOLOGY ACCEPTED FOR IMPLEMENTATION PLANNING`; implementation
  begins only through the dependency gates in `docs/38-implementation-plan.md`.

The executable readiness scaffold is provisional and is not the normative research
plan. It must first be migrated to the accepted strict source-only method. Synthetic
fixtures may debug accounting without opening any target labels.

## Stage 1: Classifier complementarity analysis, weeks 3-5

Train under identical sampling:

1. DINOv2-Reg with a frozen backbone and trained PAD head;
2. frozen CLIP/SigLIP with a preregistered fixed prompt bank; source-tuned prompts are
  a transfer-sensitivity ablation;
3. raw score average as a diagnostic;
4. calibrated score average as the principal simple-fusion baseline;
5. regularized learned score fusion using calibrated source scores.

For every fitted DINO head, select the checkpoint by lowest equal-domain,
class-balanced BCE on a deterministic subject-disjoint inner split of the allowed
source-train pool; ties use the earlier epoch. Branch/gate/routing calibration and OOF
evaluation records cannot perform early stopping.

Add one required matched control without changing the proposed architecture:

6. frozen DINOv2 without Registers paired with DINOv2-Reg as the required stronger
  same-family control when retaining a cross-foundation title.

The DINOv2-Reg + plain-DINOv2 strong control and heterogeneous pair use identical
one-stage affine branch calibration, calibrated-average fusion, operating-point
selection, denominators, and bootstrap units.

A shared-encoder two-head diversity control and a source-supervised visual head on the
OpenCLIP image encoder are optional appendix diagnostics. They do not determine RQ1,
RQ2, or continuation to risk fitting.

Cache each frozen backbone's features independently so the branches never share GPU
memory. All four MCIO domains are strict outer-domain-held-out targets in turn. The globally fixed VLM
is reused in every fold; only fold-local source-fitted heads, calibrators, and
thresholds vary before target $T$ is evaluated. Required complementarity reporting is
standalone branch quality, the fixed fusion, the matched same-family control, joint
correctness/double fault, and a simple directional rescue summary. Extensive oracle,
correlation, and subgroup diagnostics are optional appendix analyses.

Report one descriptive directional rescue summary:
$REF_{VLM}=P(V\text{ correct}\mid D\text{ wrong})$ and the realized fusion counterpart
$REF_g=P(g_{ref}\text{ correct}\mid D\text{ wrong})$, with event counts and paired
subject/video uncertainty. On attacks, report false accepts blocked and newly admitted
by fusion. These diagnose the classifier but are not continuation thresholds or a
third claim gate. Use literally the same fitted DINOv2-Reg anchor predictions for
heterogeneous and same-family summaries at each target, seed, and configuration; cache
them once and never retrain the anchor by pair.

False-accept rescue is descriptive because it conditions only on DINO false accepts.
Report the opposing count of attacks blocked by DINO but admitted by fusion, net
$APCER(D)-APCER(g_{ref})$, and the corresponding BPCER/BFNR change at source-selected
thresholds. Target-matched thresholds and curves are diagnostics, not deployed-policy
evidence.

Complementarity lift and normalized double fault are optional appendix diagnostics.
If reported, include uncertainty and do not use them as kill criteria.

If optional oracle gain is reported, define it on thresholded decisions using balanced
accuracy/error at source-selected biometric operating points. Never report `oracle
AUC` from ground-truth branch selection; bootstrap optional oracle diagnostics by
video or subject, not frame.

Exit criteria:

- the source-only base-classifier competence artifact is frozen and passes before any
  target result is opened;
- standalone branches, fixed fusion, matched same-family control, joint correctness/
  double fault, and the directional rescue summary are reproducibly reported;
- the complete target domain did not influence model or configuration selection.

These classifier diagnostics are separate from failure-risk transfer and do not stop
Stage 2. Heterogeneous advantage is decided only by the RQ2 matched whole-system rule.
Explicit disagreement remains a feature-attribution claim only.
Before held-out evaluation, source pseudo-shifts must freeze nonzero minimum meaningful
effects or positive paired lower-confidence-bound criteria for $\Delta_{CF}^{AP}$
and $\Delta_{dis}^{AP}$; $\Delta>0$ alone is insufficient.

DINOv2 without Registers is required for any heterogeneous-foundation claim;
supervised backbones, LoRA, and larger VLMs remain later ablations.

## Stage 2: Source-only risk estimation, weeks 6-8

Calibrate each branch independently on source validation data before computing the
primary absolute-difference disagreement and its JS ablation.
Then generate out-of-fold source records in two variants.

Use the globally fixed primary VLM in every OOF fold. Fit its branch calibration and
source-only threshold independently inside each allowed fold remainder.

### Sample-OOF ablation

1. split within each source domain using subject/video-safe partitions after removing $G_{domain}$;
2. train/select both predictors using only the remainder;
3. calibrate each branch independently and predict held-out samples;
4. select fold-safe $\tau_{ref}^{(k)}$ on the allowed remainder and record correctness,
   probabilities, operational margin $m_F^{(k)}$, image quality, and disagreement;

The sample-OOF and domain-OOF constructions use the same candidate universe of source
subjects/videos after removing $G_{domain}$, the same frame/video unit, source-macro
weighting, quality features, risk-model family, regularization, and optimization
budget. Sample-OOF is subject-disjoint and never splits frames from one subject/video
across fit and OOF evaluation. Report OOF record counts, effective branch-fit sizes,
and natural error prevalence for every pseudo-fold. If branch-fit sizes differ
materially, add a budget-matched sensitivity; otherwise attribute any gain to the
complete domain-OOF construction rather than domain holdout alone.

### Domain-OOF primary MCIO protocol

1. hold out one complete source capture domain after removing $G_{domain}$;
2. train/select both predictors using only the remainder;
3. fit one-stage monotone affine branch calibration on a disjoint, domain-balanced
  validation partition within the remainder;
4. select $\tau_{ref}^{(k)}$ only on the allowed remainder, then predict the held-out
  fold with margin $m_F^{(k)}=p_F^{(k)}-\tau_{ref}^{(k)}$;
5. repeat all folds and concatenate records;
6. train the preregistered fixed-regularization logistic failure-risk estimator for
  calibrated-average $g_{ref}$;
7. generate out-of-sample predictions on permanent gate-calibration $G_{domain}$,
   which was excluded from every prior fit and selection step;
8. select the accept threshold on $G_{domain}$ and do not refit any component afterward.

Use $G_{domain}$ in MCIO and a separate known-attack-only $G_{attack}$ in SiW-M.
Neither holdout selects routing thresholds or unrelated ablation policies.

Stratify $G_{domain}$ by source domain, class, and attack family where possible; report its
total, attack, error, and false-accept counts before claiming threshold stability.

Run attack-OOF separately for SiW-M using held-out attack families. A domain-OOF-only
gate cannot support an attack-shift calibration claim; mixed OOF is secondary.

Leave probabilities/disagreement unstandardized; normalize only fixed quality features
with final allowed source-fitting statistics reused at target time. Audit OOF domain
identifiability. Nested pseudo-domain hyperparameter selection is secondary because
three source domains provide a weak meta-validation sample.

Compare raw/calibrated JS, absolute difference, hard disagreement, and log-odds
difference against fused MSP/entropy and learned risk on fixed $g_{ref}$ predictions.
Include $-|p_F-\tau_{ref}|$ as the primary simple operational-margin risk baseline;
branch-specific operational margins are secondary.
Add capacity-matched LogReg/MLP probability baselines with and without each explicit
disagreement feature and the same fixed image-quality vector. DINO embedding
Mahalanobis confidence is a strong simple
representation-space baseline, not a substitute for reproducing a published
confidence-aware FAS method when its implementation and protocol are available.

Use two distinct result tables. The risk-estimator table holds $g_{ref}$ and its error
labels fixed for fused MSP/entropy, JS, Mahalanobis, and learned risk scores. Report
error prevalence and paired within-target deltas. The end-to-end system table may
compare DINO-only, shared-encoder DINO head diversity, DINO plus CLIP visual head, semantic VLM, and
conditional dual systems because it explicitly measures combined classifier and risk
changes.

Define AP as non-interpolated average precision with prediction error as the positive
class and larger scores meaning higher risk; do not substitute trapezoidal PR-AUC.
The RQ1 primary feature variant is $R_{DVd}$, fixed before target evaluation. For
target $t$ and seed $s$, both OOF variants score the same final heterogeneous
classifier errors $e_{DV}$:

$$
\Delta_{OOF,t,s}=AP(e_{DV},r_{DVd}^{domain})-
AP(e_{DV},r_{DVd}^{sample}).
$$

This contrast holds final base predictions, error labels, features, loss, and
regularization fixed, but tests the complete domain-OOF construction rather than a
causal effect of domain identity alone. Branch fit size, error prevalence/composition,
score distributions, and calibration difficulty may differ from sample-OOF. Report
those diagnostics and risk-feature distributions by strategy. Add a source-predefined
prevalence/difficulty-matched weighting sensitivity where feasible; it cannot replace
the unweighted primary contrast. $R_{DV}$ and $R_{DVdm}$ remain attribution and
operational variants; they cannot replace the RQ1 primary after viewing targets.

RQ2 compares complete heterogeneous and same-family selective systems on the same
transactions using source-selected policies. Each system has its own classifier,
error labels, risk estimator, and gate, so raw cross-system AP difference is
descriptive rather than evidence that one estimator is intrinsically better. The
primary system-level endpoint is class-balanced raw AURC. For system $j$, integrate
class-conditional classification-error risk over coverage in $[0,1]$ on the common
fixed-detector-success transaction mask and define

$$
U_{j,t,s}=\frac12(AURC_{attack,j,t,s}+AURC_{bona,j,t,s}),\qquad
\Delta_{RQ2,t,s}=U_{same,t,s}-U_{hetero,t,s}.
$$

Positive values favor the heterogeneous system. Average seeds and targets in the same
order as RQ1. A pass requires $\Delta_{RQ2,macro}\ge0.01$, its paired cluster-bootstrap
95% LCB above zero, at least three positive target deltas, at least two positive
seed-level four-target macros, and no target with $U_{hetero}-U_{same}>0.02$. At each
system's independently source-selected gate, heterogeneous-minus-same-family
`FA_end2end` and `BFNR_end2end` may each be at most 0.01 in the four-target macro and
0.02 on every target. The original transaction denominators and K=1 semantics apply;
detector failures are absent from both systems' AURC rows but enter these end-to-end
guardrails as terminal non-accepts and enter class-coverage accounting. Coverage is a
mandatory explanatory result, not an additional pass/fail guardrail. Thus
one favorable metric cannot offset a violated guardrail. Classification quality,
error prevalence, each system's error AP, and achieved attack/bona-fide coverage are
mandatory supporting results but cannot replace the scalar endpoint. This rule claims
only an advantage of the studied pair in this protocol, not a causal pretraining
effect. Report class-conditional excess-AURC as ranking-regret support, not as an
alternative primary outcome.

Report $\Delta_{dis}$ between capacity-matched models with and without the primary
absolute-difference feature. If it adds no repeatable gain to a nonlinear model already
receiving both probabilities and quality, reframe the method as cross-foundation
selective failure prediction and remove algorithmic emphasis on disagreement.
Freeze $R_q=[q]$, $R_D=[\widehat p_D,q]$, $R_V=[\widehat p_V,q]$,
$R_{DV}=[\widehat p_D,\widehat p_V,q]$,
$R_{DVd}=[\widehat p_D,\widehat p_V,d_{abs},q]$, and
$R_{DVdm}=[\widehat p_D,\widehat p_V,d_{abs},m_F,q]$. Define
$\Delta_{CF}^{AP}=AP(R_{DV})-\max(AP(R_D),AP(R_V))$ and
$\Delta_{dis}^{AP}=AP(R_{DVd})-AP(R_{DV})$ as scientific claim quantities,
and $\Delta_{margin}^{AP}=AP(R_{DVdm})-AP(R_{DVd})$ as an operational gain.
All use the same fixed-regularization logistic family and source lineage. Primary risk
fitting uses equal pseudo-domain weighting with unweighted BCE inside each domain;
class-weighted/focal ranking losses are labeled non-probabilistic ablations.

Exit criteria:

- RQ1 $\Delta_{OOF}$ passes its preregistered effect and uncertainty rule and the
  domain-OOF risk score improves over the fixed list of primary risk baselines;
- selective utility is evaluated separately over source-selected comparator gates
  under K=1, with both achieved attack and bona-fide coverage reported. Failure of
  this operational consequence does not by itself falsify RQ1;
- retain the disagreement claim only if preregistered $\Delta_{dis}>0$ against the
  capacity-matched nonlinear probability-only model;
- no target sample or statistic enters calibration.
- Brier/NLL and reliability diagrams support any probabilistic `calibrated risk`
  wording; otherwise describe the output only as a failure-risk score.

### Source-only competence and primary-event gates

Before opening any target result, Phase 7 writes an immutable competence artifact from
source pseudo-shifts for DINOv2-Reg, OpenCLIP, the calibrated heterogeneous average,
and the matched same-family average. Every entry records nonconstant score variance,
both-class support, finite calibration parameters, source-pseudo-shift
AUROC/balanced accuracy, and error counts. The two complete systems are mandatory
competence gates for RQ2, and the heterogeneous reference is mandatory for RQ1.
Freeze $\delta_{competence}=0.05$: each gated complete system must achieve equal-domain
macro AUROC and balanced accuracy of at least 0.55, with cluster-bootstrap 95% LCB for
macro AUROC above 0.50. Scores must be finite with range greater than $10^{-6}$ and
both ground-truth classes present. Each pseudo-domain balanced accuracy uses a
threshold selected only on that fold's allowed source remainder, never its held-out
pseudo-domain scores. The heterogeneous reference's concatenated source-OOF records
must additionally contain at least 20 errors and 20 correct predictions so binary risk
fitting is defined.

For the core RQs, the shared DINOv2-Reg anchor must pass nondegeneracy, finite-score,
both-class-support, and finite-calibration checks; its standalone 0.55/LCB result is
descriptive unless a standalone-competence claim is made. The same claim-specific rule
applies to OpenCLIP: failing its standalone 0.55/LCB threshold forbids calling it a
competent standalone PAD classifier, but does not block RQ1 or RQ2 when the relevant
complete systems pass. Any VLM incremental-risk claim still requires its own frozen
paired attribution test; complete-system competence alone cannot establish that
mechanism. These are source-only gates, not target performance guarantees. Failure
blocks exactly the dependent claim and triggers no target-informed alteration;
Track-A SOTA rank is irrelevant.

Freeze $N_{error,min}=20$ erroneous target transactions/videos per target and seed for
the primary AP applicability rule; dependence is handled by the preregistered
subject/video cluster bootstrap. Below this count, report every estimable AP, paired
delta, count, and uncertainty, but mark that target/seed contribution underpowered and
do not count that seed as event support. For every target with estimable AP in all
three seeds, define

$$
\Delta_{OOF,t}=\frac13\sum_{s=1}^{3}\Delta_{OOF,t,s},\qquad
\Delta_{OOF,macro}=\frac14\sum_{t=1}^{4}\Delta_{OOF,t}.
$$

No seed is dropped or reweighted because it falls below 20 errors. A target is
event-eligible only when all three seed deltas are estimable and at least two seeds
meet $N_{error,min}$. If a seed has one-class error labels, its AP delta is undefined,
the target is ineligible, and the four-target primary macro is not estimable; report
RQ1 as inconclusive rather than inserting a synthetic value or averaging the other
seeds. Otherwise always compute the frozen equal-weight four-target macro. A primary
pass additionally requires at least three event-eligible targets, and an ineligible
target cannot satisfy the three-of-four positive-target rule. Fewer than three
eligible targets makes RQ1 inconclusive. Scarcity is neither perfect risk estimation
nor evidence against RQ1.

## Stage 3: Selective and conditional inference, weeks 9-11

Implement in this order:

1. always-on DINO + VLM reference under fixed $g_{ref}$;
2. fixed post-VLM fusion $g_{ref}$ followed by accept/abstain risk gating;
3. spoof-only early-exit routing using a DINO operational margin selected on separate
  branch validation to minimize VLM invocation subject to preregistered source BPCER
  or $BFNR_{end2end}$ increase $\le\beta$;
4. symmetric and direct-live routing only as security-bounded ablations;
5. optional semantic distillation after the upper bound is established.

Do not add the next component unless the current comparison is understood.

Steps 1-2 are the core system. Steps 3-5 are optional routing/deployment extensions.
Under the primary $K=1$ policy, predicted spoof and abstain are both terminal
non-accept. For gate threshold $u$, report

$$
FA_{end2end}(u)=P(detector\ success,g_{ref}=live,r\leq u\mid attack),
$$

$$
BFNR_{end2end}(u)=1-P(detector\ success,g_{ref}=live,r\leq u\mid bona\ fide).
$$

Against the same ungated classifier, gating can only weakly reduce false accepts and
weakly increase bona-fide non-accepts. Therefore the access-control claim is a better
source-selected security-usability trade-off than comparator risk gates, not a claim
that abstention improves both axes. Report live decisions blocked by the gate, attacks
newly blocked, bona-fide transactions newly rejected, and both achieved class
coverages. Failure diagnosis on false rejects is not by itself security utility.

Conditional routing is an operational extension, not required to establish the core
scientific claim. Implement it only after source-only risk transfer passes its criteria;
failure of classifier rescue does not by itself block this optional study.

Exit criteria:

- classifier comparisons (DINO, VLM, calibrated average, learned fusion) and
  fixed-$g_{ref}$ risk-score comparisons are reported separately;
- explicit disagreement beats capacity-matched no-disagreement risk baselines or the
  framing is weakened as preregistered;
- conditional inference approaches always-on security/selective performance at fixed
  APCER, fixed BPCER, and matched coverage;
- VLM invocation rate or GPU-ms/request decreases materially at matched operating points;
- mean/P50/P95 latency exposes the sequential hard-case penalty against parallel
  always-on inference;
- downstream-unseen and open-vocabulary zero-shot results are reported separately;
- attack/bona-fide coverage, covered errors, and end-to-end false acceptance use
  explicit denominators under the $K=1$ transaction policy;
- direct-DINO and VLM-invoked routes separately report transaction count, false
  accepts, bona-fide non-accepts, detector failures, and abstentions before end-to-end
  totals over the original denominator;
- shared wrong predictions are explicitly analyzed.

## Stage 4: Full open-world evaluation, weeks 12-14

- compute the primary macro over all four strict outer-domain-unseen MCIO
  targets;
- run SiW-M leave-one-attack-out;
- run external mask transfer when licensing permits;
- stratify results by sensor, illumination, attack instrument, and image quality;
- inspect worst false accepts and false rejects.

For each target and seed, train and score independently; never pool seed predictions
unless deploying an ensemble. Point contrasts first average the three seed-level
deltas within target and then average the four target deltas. Report mean/standard deviation of seed-level metrics and
subject/video bootstrap within each seed, with no $t$-test at $n=3$ and no best-seed
selection. Every claim preregisters its endpoint, fixed comparator set, delta, minimum
meaningful effect, harm tolerance, and event-count requirement. A primary claim passes
only when its paired four-target macro lower confidence bound is positive, its point
gain is at least the claim-specific $\delta_{min}$, at least three of four target point
estimates are positive, no target exceeds its harm tolerance, and at least two of
three seeds have positive four-target macro deltas. Claims against multiple required
comparators use the preregistered conjunction; no post-target comparator selection is
allowed. Claims are limited to consistency across the evaluated four MCIO held-out
domains. The cluster bootstrap is conditional on these datasets and fitted procedures;
it does not sample from or establish generalization over a universe of future domains.
Use 2,000 paired cluster-bootstrap resamples. Within a target, use the same resampled
subject/video cluster multiplicities for both methods/systems and all three seeds when
cluster identities permit, compute seed deltas, average the three seeds, and only then
average the four target deltas. Seed variability is reported separately and seeds are
never bootstrap sampling units. Mark
one-class risk labels or fewer than $N_{error,min}$ errors as inconclusive for
error-ranking endpoints. Zero
false-accept denominators and $N_{FA}<N_{min}$ are inconclusive only for FARR and other
false-accept-conditioned endpoints; they do not invalidate estimable error AP. Report
inconclusive separately from evidence against. Recompute the stronger of $R_D/R_V$
inside every paired $\Delta_{CF}$ resample; never switch operating thresholds after
viewing a target.

## Stage 5: Secondary representation ablations, weeks 15-16

Only after the core RQ1 risk-transfer result passes; each optional ablation states any
additional claim-specific dependency:

- DINOv2 versus DINOv2-Reg;
- fixed class-token plus mean-patch pooling versus learned attention pooling;
- face versus context crop;
- frozen versus LoRA-tuned branches;
- optional patch deletion/insertion analysis;
- optional coarse semantic concept analysis.

Named cue ontology, cue pseudo-labeling, and counterfactual synthesis require a
separate go/no-go decision and are not assumed in the first paper.

## Stage 6: Deployment and paper package, weeks 17-20

- freeze configs and final checkpoints;
- rerun main tables from clean manifests;
- complete statistical tests and confidence intervals;
- prepare evidence maps with quantitative tests, not cherry-picked examples;
- document failures and negative ablations;
- report parameters, FLOPs, peak memory, latency, throughput, VLM invocation rate,
  and coverage at fixed security operating points;
- update the literature search immediately before submission.

## System matrix

Rows A-H and M cover the core classifier, fixed-error, and same-family comparisons.
Rows I-J are optional deployment extensions. Rows K-L are optional appendix diagnostics
and cannot block either RQ.

| ID | DINO | VLM | Fusion/risk method | Conditional VLM | Abstain |
|---|---:|---:|---|---:|---:|
| A | Yes | No | DINO uncertainty | No | Optional |
| B | No | Yes | VLM uncertainty | No | Optional |
| C | Yes | Yes | Raw average | No | No |
| D | Yes | Yes | Calibrated average | No | No |
| E | Yes | Yes | Learned fusion of calibrated scores | No | No |
| F | Yes | Yes | Raw JS disagreement | No | Yes |
| G | Yes | Yes | Matched $R_{DVd}$ risk estimator, sample-OOF | No | Yes |
| H | Yes | Yes | Primary $R_{DVd}$ risk estimator, domain-OOF | No | Yes |
| I | Yes | On demand | Domain-OOF calibrator | Yes | Yes |
| J | Yes | Distilled | Domain-OOF calibrator | No | Yes |
| K | Two heads | No | Shared-encoder head-diversity control | No | No |
| L | Yes | CLIP visual head | Calibrated average | No | No |
| M | Reg + plain DINOv2 | No | Same-family average + matched domain-OOF risk gate | No | Yes |

## Initial compute plan

- MVP: one RTX 4080 16 GB, frozen backbones, mixed precision, sequential feature caching.
- Adapter stage: start with batch-size reduction and gradient accumulation; larger
  hardware is optional rather than assumed.
- Full evaluation: parallelize seeds/targets; do not reduce protocol coverage to
  finance unnecessary full fine-tuning.

Indicative starting values, to be selected on source validation only:

```yaml
dino_checkpoint: dinov2_vitb14_reg4
dino_input_size: 448
dino_tuning: frozen
vlm_model: ViT-B-16
vlm_pretrained: laion2b_s34b_b88k
vlm_input_size: 224
vlm_text_encoder: frozen
vlm_image_tuning: frozen
head_lr: 3.0e-4
adapter_lr: 3.0e-5
weight_decay: 0.05
frames_per_video_per_epoch: 3
```
