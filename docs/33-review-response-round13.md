# Response to Review Round 13 - Methodology Freeze Before Coding

Date: 2026-09-18

## Scope correction

The owner clarifies that the project is still deciding the research plan and method.
Rounds 11-13 moved prematurely into executable-readiness engineering. The code findings
in Round 13 are technically valid, but fixing successive validator probes does not
answer the two decisions that must precede implementation:

1. Is the proposed study feasible with the available compute and realistic PAD data?
2. Is the contribution sufficiently distinct and evidentially strong for a defensible
   Q3 submission?

Therefore no Round-13 implementation finding is patched in this response. They are
retained as an implementation backlog. Existing `configs/`, `src/`, `scripts/`, and
`tests/` are provisional scaffolding, not the normative method and not evidence that
implementation has started correctly.

## Methodology change prompted by the review

Round 13's firewall discussion reveals a genuine methodological weakness in the prior
**global labeled MICO pilot** design. Even if only train/dev partitions were used, a
future target domain could influence global candidate selection while acting as a
source for the pilot fold. That weakens the domain-generalization claim.

The labeled MICO pilot is removed.

For each target $T$ in OULU-NPU, CASIA-FASD, Replay-Attack, and MSU-MFSD:

1. treat the complete domain $T$ as unseen;
2. use only the other three domains as sources;
3. select among the finite frozen VLM/preprocessing candidates through nested
   source-domain OOF macro ACER with candidate-specific source thresholds;
4. fit final source components on the allowed source partitions;
5. evaluate $T$ once.

The candidate set and selection algorithm are global and fixed; the selected candidate
may differ by target because its source set differs. All four MICO targets are now
confirmatory. Synthetic data and source-only inner folds may debug the eventual
pipeline, but no labeled MICO target is a development pilot.

## Frozen minimum method

The proposed minimum paper contains only:

1. a frozen `dinov2_vitb14_reg4` image encoder with a small PAD head;
2. a frozen OpenCLIP/SigLIP candidate using a generic binary prompt bank;
3. one monotone affine source calibration per branch;
4. calibrated-average fusion as the fixed reference classifier;
5. a fixed-regularization logistic failure-risk model trained from source-domain OOF
   records for MICO and known-attack OOF records for SiW-M;
6. scientific risk features
   $[\widehat p_D,\widehat p_V,|\widehat p_D-\widehat p_V|,q]$;
7. an optional deployment gate that may additionally use signed policy margin, whose
   gain is reported separately as $\Delta_{margin}$;
8. abstention/risk-coverage evaluation, with conditional VLM routing only after the
   scientific kill criteria pass.

The first paper excludes full foundation-model fine-tuning, generative MLLMs, learned
cue ontologies, synthetic forensic generation, and elaborate localization claims.
LoRA, distillation, and semantic evidence maps remain post-success ablations.

## Feasibility assessment

**Compute:** feasible on one RTX 4080 16 GB. The backbones are frozen and run
sequentially. Features can be cached per dataset/candidate, so repeated outer folds and
three seeds retrain only small heads and calibrators. The protocol is time-consuming
but not GPU-memory prohibitive.

**Data:** conditionally feasible. Dataset access, official protocol parsing, reliable
subject/video IDs, and enough independent attacks for disjoint calibration/gate roles
are the real blockers. MSU-MFSD is the most likely weak point. Counts must be audited
before fixing low-APCER claims. If partitions are underpowered, the operational
threshold experiment must be simplified or labeled nominal; target data cannot repair
it.

**Engineering:** feasible but deliberately deferred. Round-13 requirements for
protocol maps, fold-aware roles, fitted-anchor lineage, two freeze snapshots, and
class-feasible partitions are sensible implementation acceptance criteria after the
method is agreed.

## Novelty and Q3 assessment

The plan does **not** claim that DINO + VLM, disagreement, logistic risk prediction, or
score averaging is individually novel. Generic semantic prompting and reliability-aware
FAS are already occupied by nearby work, especially FLIP/TeG-DG, evidential/confidence
methods, primitive prompting, and RPSR-FAS.

The defensible contribution is the combined scientific question and protocol:

> Do independently pretrained heterogeneous foundation predictors provide
> transferable, security-useful failure information for single-image PAD when all
> selection and risk calibration are source-only, and is that information stronger
> than same-family diversity and conventional uncertainty?

A Q3 paper is plausible if confirmatory results jointly establish:

1. realized DINO false-accept rescue with sufficient independent events;
2. positive paired heterogeneity advantage over DINOv2-Reg + plain DINOv2 under the
   identical calibration/fusion stack;
3. failure-risk AUPR and selective AURC improvement over MSP/entropy, boundary distance,
   Mahalanobis, and capacity-matched single/dual-probability risk baselines;
4. strict source-only transfer across the four MICO targets and separate SiW-M
   attack-family shifts;
5. a useful security-coverage-compute trade-off if conditional routing is retained.

Explicit disagreement remains title-worthy only if
$\Delta_{dis}^{AUPR}>0$ under the capacity-matched test. If heterogeneity does not beat
same-family diversity, the cross-foundation claim is rejected. If risk calibration
adds no transfer gain, the model-centric paper stops. This is a credible Q3
empirical-method contribution, not a guaranteed acceptance and not currently a strong
Q1/top-conference algorithmic claim.

## Requested reviewer decision

The next review should evaluate the methodology above, not add another executable
readiness probe. Please answer these questions directly:

1. **Feasibility:** Is the frozen-backbone, cached-feature, nested source-OOF design
   feasible on one RTX 4080 16 GB, subject to the stated data-count audit? If not,
   identify the minimal methodological simplification.
2. **Novelty:** Given the cited closest work, is the heterogeneous-vs-same-family
   attribution plus source-only cross-fitted failure-risk transfer a defensible Q3
   contribution? If not, name the exact overlap or missing scientific claim.
3. **Protocol validity:** Does removing the labeled MICO pilot and making all four
   targets strict outer-domain-unseen close the principal selection-leakage objection?
4. **Minimum evidence:** Are the five evidence conditions above sufficient to retain
   the claim hierarchy, or is one essential baseline/endpoint still missing?
5. **Freeze decision:** If there is no remaining conceptual blocker, explicitly state
   that the research plan and methodology are accepted for implementation planning.

Only after both sides agree on those five points will the repository produce a coding
plan or continue implementation. Round-13 code findings will then be converted into
acceptance tests in dependency order rather than driving the research design.
