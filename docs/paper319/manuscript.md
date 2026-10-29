# Beyond AUROC: Operating-Point Transfer of Frozen Foundation Models for Face Presentation Attack Detection

**Results-complete working manuscript,2026-10-29. Not submission-ready.**
The official-partition matched comparison completed all12 contexts and
independent saved-checkpoint reconstruction. Its initial initialization stop
and later context timeout were resolved through explicitly approved amendments;
neither stopped attempt is interpreted as PAD performance evidence.
Development results retain their original populations and limitations.
All primary seed-level tables and conditional intervals are supplied in the
[completed result package](../../results/phase1/paper324-primary-tables-v1.md).
Author names, affiliations and submission metadata remain to be supplied.

## Abstract

Face presentation attack detection (PAD) under dataset shift requires more
than favorable aggregate ranking: a decision threshold derived from available
source data must retain both attack rejection and bona-fide usability.
We compare DINO-Reg, supervised OpenCLIP, a fixed two-DINO average and
matched-input DeepPixBiS architecture retraining under train-three/test-one
source-only fitting, model selection, calibration and threshold rules.
Three training seeds across four declared target-test populations produce
48 primary system/target/seed cases. None meets both empirical attack false
acceptance (FA)<=5% and bona-fide acceptance (BFA)>=50% at its source-derived
threshold, although15 meet the FA constraint alone. Evaluation-label oracle
thresholds on the same saved scores admit the joint utility in21 cases;
the remaining27 lack sufficient empirical low-FA score separation.
On OULU, oracle BFA averaged over seeds is58.70% for the specialist,
46.67% for DINO-Reg and23.43% for CLIP, whereas CLIP exceeds DINO-Reg's
oracle BFA on MSU. These are descriptive oracle diagnostics, not deployable
thresholds or a universal system ranking. Conditional paired cluster
bootstrap intervals accompany all source-policy results and differences.
A separate developmental nested fusion study finds no feasible selected
policy under its matched screen. The evidence distinguishes operating
threshold headroom from score-specific limitations without supplying a
target-label-free remedy. All datasets previously informed development;
SiW evaluation is a video-grouped local intersection with unknown subject
identities, not untouched participant-independent confirmation.

Keywords: face presentation attack detection; frozen representations;
cross-dataset evaluation; operating-point transfer; threshold diagnostics.

## 1. Introduction

PAD systems must distinguish bona-fide access attempts from presentation
attacks while maintaining a usable acceptance rate for legitimate users.
Cross-dataset evaluation exposes changes in capture conditions, attack
realizations and population composition that are not resolved by reporting
within-dataset classification alone.

General-purpose pretrained representations make lightweight PAD readouts
attractive. However, the broad claim that frozen foundation models perform
well within datasets and transfer unreliably across them is already studied
by Lorenz, George and Marcel [1]. Generalization failure in face PAD is
itself well established [2]. We therefore do not propose a new discovery of
domain shift, a large encoder leaderboard or a novel linear probe.

Our question is narrower: when an operating policy selected from source data
fails after transfer, does the fixed score retain a usable low-false-
acceptance operating point, or would even hindsight threshold selection fail?
AUROC summarizes ranking over the entire score range. An operational
threshold and a constrained empirical ROC point answer different questions.
Conflating them risks recommending calibration-only remedies where the
stored scores do not separate the classes sufficiently at the required
operating point.

This paper reports the following bounded empirical contributions. Their
positioning remains subject to closest-work assessment; none is a claim
that constrained ROC analysis itself is novel:

1. A controlled multi-source comparison of a small fixed frozen-feature PAD
   system set and one specialist architecture under explicit source-only
   training, validation, calibration and threshold rules.
2. A paired view of available source-threshold operating results and
   retrospective low-FA oracle headroom, identifying different observed
   limitations without claiming a new oracle algorithm.
3. Supporting evidence from a matched nested fusion study that preserves
   missing-policy outcomes instead of substituting a favorable fallback.

The contributions concern experimental evidence and interpretation, not a
new backbone, deployable oracle threshold, causal explanation of domain
shift or population-security guarantee.

## 2. Related work

### 2.1 Generalization evaluation in PAD

Costa-Pazo et al. [2] investigate the face PAD generalization problem under
realistic evaluation conditions. Our study treats cross-dataset failure as
an established concern. Their constrained operating analyses include APCER
at BPCER10% and working-point curves, as verified in the full-text review
accompanying this revision. Looking beyond aggregate metrics or inspecting
constrained ROC points is therefore not a new contribution. Our narrower
question pairs a source-available policy with a retrospective fixed-score
oracle at the same declared attack-FA constraint. This distinction does not
establish that their exact threshold pipeline is identical or wholly
different. Comparisons across papers require matching datasets,
partitions, frame sampling, preprocessing, training exposure and threshold
selection; an official train/test restriction alone does not ensure this.

### 2.2 Frozen foundation-model probes

Lorenz et al. [1] benchmark24 frozen encoders on MCIO and include specialist
PAD references. Their study already establishes that intra-dataset success
does not reliably transfer across datasets. Our four-dataset combination
includes SiW-Mv2 instead of Replay-Attack and is not MCIO. We investigate a
smaller fixed set, multi-source training and low-FA operating diagnostics;
neither the smaller encoder set nor this dataset substitution is itself
claimed as novelty.

Lorenz, George and Marcel [11] also examine foundation-model limits under zero-shot
and LoRA adaptation in a single-source MCIO setting. Feng et al. [12]
already study register-DINO and multi-source MICO/LSD evaluation with
augmentation/loss interventions. Thus multi-source leave-one-out structure
and register-DINO are not novel contributions here either. The candidate
distinction is the explicitly paired source-policy and low-FA oracle
diagnosis, not those components in isolation.

### 2.3 Specialist PAD and operating diagnostics

DeepPixBiS [3] uses pixel-wise and global supervision for PAD. We use
matched-input architecture retraining as a specialist comparator, rather
than loading an OULU-trained PAD checkpoint and calling it source-exclusive.
Its inclusion is contextual evidence, not a novel comparison by itself.

Empirical ROC analysis and retrospective constrained threshold selection
are standard tools. The proposed value is their joint use with explicitly
available source-derived policies, source separation and reported support
in this PAD comparison. A focused literature table accompanies the draft;
no first-of-its-kind claim is made.

## 3. Data and evaluation populations

### 3.1 Prepared observations

Each video contributes its accepted earlier-middle successfully decoded
frame. Existing fixed preprocessing produces aligned RGB224 and RGB518
crops; detector/pre-detector failures remain non-acceptances without invented
feature vectors. This is single-frame-per-video PAD, not multi-frame
aggregation or a claim to reproduce published video-level protocols.

The local archive contains7510 originals from OULU-NPU, CASIA-FASD, MSU-MFSD
and SiW-Mv2. Five adopted SiW source exclusions resolve documented exact-
content crossings without altering the archival population. The completed
comparison contains7505 active originals,7474 usable images and31 failures.
The data-preparation and evaluation specifications bind exact private
manifests; aggregate counts and hashes are public.

OULU, CASIA and MSU dataset provenance is given in [7-9]. SiW-Mv2 here is
the adopted Protocol-I local intersection, not the entire release or a
reproduction of the original SiW-M study [10]. It contains1680 matching
originals;20 supplied out-of-protocol videos are excluded and11 reference
originals are absent from the local archive. Its623 target originals are
the declared test-list intersection. This coverage limitation is retained.

### 3.2 Distinct studies, not one pooled benchmark

We separate:

- **Completed development studies:** historical source-use roles, including
  official-test observations for some source datasets, supporting the
  readout, fusion and oracle analyses.
- **Completed matched supplementary comparison:** official source train/
  development populations only, with the held-out dataset's official test
  population for evaluation.

The former cannot be relabeled as the latter. Results from these populations
are never pooled into a single performance estimate. All four datasets have
already informed development; the supplementary study is not untouched
confirmation, despite excluding target labels from its fitting pipeline.

### 3.3 Grouping limitation

OULU/CASIA/MSU metadata identify subjects. Local SiW-Mv2 metadata do not
identify participants; SiW units are videos joined by exact-frame components
where applicable. Accordingly, participant-disjoint source validation and
participant-level uncertainty cannot be certified for SiW. This limitation
applies to the matched model selection and threshold estimates as well as
the analysis. No filename-derived identities are fabricated.

## 4. Methods

### 4.0 Completed developmental experiments

The completed analyses use6882 source-eligible originals: CASIA600/594
usable, MSU280/272, OULU4950/4949 and SiW1052/1040, totaling6855 usable
observations and27 technical failures. OULU/CASIA/MSU official-test members
assigned historical source roles remain included. SiW's623 null-role test
originals and five adopted exclusions do not enter these source analyses.
These are not the7505-active-original official-partition populations below.

Preassigned, group-separated roles are training, branch calibration and
represented-source diagnostic evaluation (`g_domain`). Only the training
role supplies head fitting and checkpoint validation. Within each allowed
source set and seed, training components are stratified by dataset and
class signature, ranked by SHA256 of seed and smallest component identity,
then assigned round-robin to five folds; fold0 is validation and folds1-4
are fitting. Calibration uses the separate branch-calibration role.
Registered groups and exact selected-frame components are checked against
cross-role leakage; immutable manifests bind actual memberships.

There are four named outer exclusions and seeds20260917,20260923,20261001.
The named outer dataset is absent from both fitting and evaluation. In each
context, each of the other three datasets becomes a pseudo-target and is
excluded from head fitting, validation, calibration, threshold choice and
model/mixture selection. The resulting primary head is trained on the other
two sources. Each evaluated source occurs under three other outer exclusions
and three seeds: nine overlapping cases, not nine independent populations.
Represented-source `g_domain` predictions instead use three-source models
on their separate diagnostic role and are not domain-OOF transfer.

Study309 compares four readout candidates for each branch: raw vectors with
lr.001/wd.05; unit-L2 vectors with lr.001/wd.05; raw vectors with
lr.01/wd.05; and raw vectors with lr.001/wd.005. Each uses200-epoch FP64
full-batch AdamW, equal-source/class BCE, earliest minimum-validation-BCE
checkpoint and no refit. Candidate selection minimizes validation BCE,
with candidate-order ties. Separate positive-affine sigmoid calibration
and the minimum per-source safe attack order statistic use only allowed
calibration rows. Thus the reported309 CLIP mean is **source-domain-OOF**,
not the separate completed train-three/official-target result.

The matched fusion experiment fixes original DINO-Reg/plain readouts at
lr.001/wd.05 and supervised CLIP at lr.01/wd.05. It compares
`(1-lambda)*DINO-Reg + lambda*CLIP` with
`(1-lambda)*DINO-Reg + lambda*plain-DINO` over the identical
`[0,.1,.25,.5,.75,1]` calibrated-probability weights.
For each two-source primary parent, one-source inner models train on one
allowed source and evaluate on the other, then reverse. A weight is eligible
only if every inner held-out source has FA<=5% and BFA>=50%. Maximize minimum
source BFA, then minimize worst-source FA, then added-branch weight.
The parent gets its own permitted-source calibration and threshold; inner
thresholds are not transferred. Three-source diagnostic parents analogously
use two-source inner holdouts. If no weight is eligible, no selected policy
or selected-policy gain is reported; there is no fallback.

Six fixed references remain evaluable independently of those selectors:
DINO-Reg, plain DINO, supervised CLIP, original equal two-DINO, inherited
selected equal two-DINO from309, and fixed equal DINO-CLIP. The inherited
selected reference is not another matched selector and is absent for new
one-source models. Study316 uses only saved predictions and policies:
one-source inner holdouts yield180 cases (36 tasks x5 references);
two-source primary domain-OOF yields216 (36x6); three-source `g_domain`
yields216 (36x6). Its612 cases are retrospective fixed-score diagnostics;
no head, calibrator or absent selected policy is fitted or fabricated.

| Study | Population and training exposure | Selection / evaluation endpoint |
|---|---|---|
|309 readouts | Historical6882 originals; primary heads on two allowed sources | Validation-BCE recipe/epoch selection; source-domain-OOF AUROC and source-policy errors |
|313/314 fusion | Same historical roles; two-source primary parents, one-source inner models | Matched six-weight feasibility-first selection;36 primary folds, including missing policies |
|316 oracle | Saved scores from the same historical experiment; three distinct stages |612 fixed-reference cases; retrospective BFA at original-denominator FA<=5%, no deployable selection |
| Completed319/321-323 comparison |7505 active originals; official source train/development only | Three-source heads/specialist, fixed recipes; fourth dataset's declared official test,48 primary system/seed/target rows |

Sections4.1-4.6 describe this last, completed study. They do not
retroactively describe the populations or candidate selection of309/314/316.

### 4.1 Fixed representations and readouts

DINOv2 [4] ViT-B/14 with and without four register tokens [5] supplies concatenated
CLS and mean patch-token features,1536 dimensions. OpenCLIP ViT-B-16 with
laion2b_s34b_b88k initialization supplies normalized512-dimensional image
embeddings [6]. Encoders remain fixed. DINO and CLIP use their existing native
crop/normalization contracts; these are not identical resolutions.

Frozen heads use200 epochs of FP64 full-batch AdamW with equal-source,
equal-class BCE. DINO learning rate is.001 and CLIP learning rate.01; weight
decay is.05, excluding bias. The minimum validation-BCE checkpoint is selected,
with earliest-epoch ties and no refit. These recipes were chosen during
earlier development, not independently preregistered before all data exposure.

The two-DINO reference is the fixed mean of separately calibrated register
and plain DINO probabilities. It has no new mixture-weight selection.

### 4.2 Matched specialist comparator

The matched DeepPixBiS architecture uses a DenseNet161-derived representation,
a pixel map and a global binary output. Initialization is ImageNet
DenseNet161 rather than pretrained PAD weights. Training uses the fixed
researcher-specified50-epoch recipe in the accompanying protocol, with
source-only checkpoint selection.

This is not claimed to reproduce the original paper's exact training
hyperparameters or reported accuracy. Specialist learning adapts its feature
extractor, whereas the foundation branches do not; compute, augmentation and
pretraining differences are disclosed. The comparison is not a causal
isolation of one architectural factor.

### 4.3 Source-only protocol

Train on three datasets and evaluate on the fourth, with three fixed training
seeds and one fixed model-free source partition per dataset. OULU official
train supplies fitting; its official development subjects are divided into
validation and calibration. Other source datasets' eligible official train
components are assigned approximately60%/20%/20% to fitting/validation/
calibration by deterministic hash rank. All official source tests are excluded.

Target official tests are used only for evaluation. This is an explicitly
defined four-dataset protocol, not an established benchmark designation.
Known subjects and exact-frame components cannot cross model-selection
boundaries. SiW retains the video-group limitation described above.

### 4.4 Scores, calibration and source thresholds

Scores are attack-high; an observation is accepted iff its score is strictly
less than the threshold. Ties are rejected. Each branch has a positive-affine
sigmoid calibrator fitted on its source calibration role. The two-DINO
system averages calibrated branch probabilities.

For specialist output, the raw attack score is one minus mean pixel
bona-fide probability. A fixed clipped logit feeds its monotone calibrator.
All oracle conclusions therefore concern the stored scalar scores, including
ties or saturation, not every possible transformation of raw embeddings.

Choose a single system threshold satisfying empirical attack FA<=5% in
each source's successful calibration observations. Integer budgets determine
eligibility. Calibration failures remain separately reported non-acceptances
and do not increase that successful-image budget. Additional1% and10%
operating points are declared sensitivity analyses.

### 4.5 Evaluation metrics and oracle diagnosis

For a target with original attack count N_A and bona-fide count N_B:

`FA(t) = accepted usable attacks / N_A`

`BFA(t) = accepted usable bona-fide observations / N_B`.

Technical failures are non-acceptances in these original-denominator metrics.
AUROC is computed on usable observations only. Report integer supports and
usable-only errors alongside end-to-end rates; no synthetic failure score
is inserted into ROC calculations.

For a fixed score vector, the oracle maximizes BFA subject to
`accepted attacks <= floor(alpha * N_A)`. With strict acceptance, tied scores
cannot be partially accepted. The5%/50% utility asks whether a threshold
also accepts at least`ceil(N_B/2)` bona-fide originals.

The oracle uses evaluation labels. It is a sample-specific diagnostic,
not a source-only success, selectable deployment policy, population bound
or future guarantee. If it is unattainable, threshold movement alone cannot
meet the requirement for those stored scores on those samples. If it is
attainable, a practical target-label-free threshold has not thereby been found.

### 4.6 Uncertainty

The supplementary analysis uses2000 paired cluster-bootstrap
replicates per target and training seed, with source policies fixed.
Subjects are the units where known; SiW uses video/exact-frame components.
Report conditional percentile95% intervals and invalid one-class replicate
counts. If fewer than95% of ranking replicates are valid, mark the ranking
interval unestimable.

Training seeds describe training variability and are not independent test
populations. Oracle points remain descriptive without confidence intervals
in this package. Four observed datasets do not support a population-of-
domains security interval.

## 5. Completed development results

### 5.1 Readout improvement is not equivalent to useful operating transfer

The completed cached-readout study reports mean domain-OOF CLIP AUROC
increasing from.554171 for the tested zero-shot score to.844040 for supervised
readout. Selected equal two-DINO reaches.889780 under that study's selection.
The supervised CLIP mean original-denominator attack FA is9.974%, with
bona-fide non-acceptance53.942%. These are study309's descriptive source
results, not the separate official-partition comparison or a direct published
leaderboard match.

### 5.2 Matched nested fusion can return no policy

Study313/314 gives DINO-CLIP and two-DINO selectors the same six weights,
including both endpoints. All360 family/selector/weight candidates violate
the5% FA constraint on at least one inner held-out source. Neither family
selects a policy in any of30 unique selectors. Both therefore have36/36
missing primary selected policies.

Missing policies are not reject-all successes or measured zero incremental
gain. The registered selected-policy gain is unestimable. Fixed references
remain evaluable: DINO-Reg meets the5%/50% utility in4/36 primary folds,
plain DINO in6/36, CLIP in1/36, fixed original two-DINO in6/36 and fixed
DINO-CLIP in6/36. Equal counts do not imply equal performance.

This is bounded evidence about the tested recipes, weights and source-
calibration threshold rule, not exhaustion of all fusion methods.

### 5.3 Oracle headroom distinguishes observed limitations

Study316 reconstructs612 source/system cases and240 same-pipeline
threshold-intersection groups from saved scores without fitting or new
model predictions. The primary two-source-trained stage contains216 cases:
six fixed systems, four sources and nine applicable contexts/source.
The contexts overlap in samples and training sources.

**Table1. Mean oracle BFA (%) at attack FA<=5% in the completed primary
source-development study. These are evaluation-label-selected diagnostics.**

| Fixed system | CASIA | MSU | OULU | SiW |
|---|---:|---:|---:|---:|
| DINO-Reg | 90.000 | 53.968 | 39.590 | 31.185 |
| Plain DINO | 94.167 | 62.302 | 29.714 | 28.481 |
| Supervised CLIP | 79.444 | 59.524 | 19.416 | 23.628 |
| Original equal two-DINO | 95.648 | 67.063 | 38.356 | 34.818 |
| Inherited selected two-DINO | 93.796 | 66.865 | 38.019 | 33.439 |
| Fixed equal DINO-CLIP | 91.019 | 70.040 | 26.669 | 29.727 |

**Table2. Cases admitting a5% FA /50% BFA oracle threshold.**

| Fixed system | CASIA | MSU | OULU | SiW |
|---|---:|---:|---:|---:|
| DINO-Reg | 9/9 | 6/9 | 0/9 | 0/9 |
| Plain DINO | 9/9 | 6/9 | 0/9 | 0/9 |
| Supervised CLIP | 9/9 | 8/9 | 0/9 | 0/9 |
| Original equal two-DINO | 9/9 | 6/9 | 0/9 | 2/9 |
| Inherited selected two-DINO | 9/9 | 6/9 | 0/9 | 1/9 |
| Fixed equal DINO-CLIP | 9/9 | 9/9 | 0/9 | 1/9 |

**Table3. Paired source-policy and oracle operating results for three fixed
representative systems. Rates are percentages, equally averaged over nine
applicable primary contexts per source. FA-safe and utility counts refer to
individual source-policy cases, not the mean.**

| System | Source | Policy FA | Policy BFA | Oracle BFA at5% FA | FA-safe /9 | FA<=5%, BFA>=50% /9 |
|---|---|---:|---:|---:|---:|---:|
| DINO-Reg | CASIA |0.216|41.389|90.000|9|4|
| DINO-Reg | MSU |42.526|92.460|53.968|0|0|
| DINO-Reg | OULU |50.537|89.184|39.590|0|0|
| DINO-Reg | SiW |24.895|67.064|31.185|0|0|
| Supervised CLIP | CASIA |0.278|33.611|79.444|9|0|
| Supervised CLIP | MSU |10.185|64.881|59.524|4|1|
| Supervised CLIP | OULU |13.289|38.033|19.416|3|0|
| Supervised CLIP | SiW |16.143|47.706|23.628|0|0|
| Original equal two-DINO | CASIA |0.031|51.389|95.648|9|6|
| Original equal two-DINO | MSU |39.484|94.048|67.063|0|0|
| Original equal two-DINO | OULU |65.811|93.603|38.356|0|0|
| Original equal two-DINO | SiW |30.005|74.702|34.818|0|0|

An average is not an all-case safety claim; the FA-safe counts expose fold
variation. Where the source policy violates FA<=5%, its BFA and the oracle's
BFA have different security operating conditions. Their difference is
**not a same-security calibration loss or recoverable gain**. Even where
both satisfy the bound, oracle headroom does not establish a target-label-
free procedure that recovers it.

CASIA has54/54 attainable cases, MSU41/54, OULU0/54 and SiW4/54.
The best OULU case reaches43.5606% BFA. For CASIA, DINO-Reg's mean original
source-threshold BFA is41.39%, versus90.00% oracle BFA. The CASIA contrast
documents headroom; OULU shows that threshold movement alone is insufficient
for these scores at this utility.

These counts are not54 independent replications, and the oracle counts do
not authorize choosing the heterogeneous mixture retrospectively. None of
the unattainable cases is due solely to a technical-failure BFA ceiling
below50%.

Within represented-source g_domain evaluation, every fixed system is
oracle-attainable in36/36 cases. This contrast supports a transfer concern,
not a causal account of why a particular source is difficult.

## 6. Completed matched comparison

### 6.1 Evaluation support and complete reporting

All12 target/seed contexts and144 policy/oracle operating cases completed
and were independently reconstructed from saved checkpoints without new
fitting. Target tests contain2943 originals and2929 usable images; the
7505/7474 totals in Section3 include all active official partitions, not
just target tests. The same target observations recur across seeds and
systems and must not be counted as independent replications.

| Target | Original attacks / bona fide | Usable attacks / bona fide | Technical failures |
|---|---:|---:|---:|
| OULU-NPU |1440 /360|1440 /360|0|
| CASIA-FASD |270 /90|265 /89|6|
| MSU-MFSD |120 /40|116 /40|4|
| SiW-Mv2 local test intersection |362 /261|359 /260|4|

**Table4. Primary source-policy and oracle results (%), equally averaged
over the three training seeds. AUROC uses usable observations; FA/BFA use
all originals. FA-safe and oracle utility counts are individual seed cases.
Every source-policy utility count is0/3. Seed means have no pooled CI.**

| Target | System | AUROC | Policy FA | Policy BFA | Oracle BFA at5% FA | Policy FA-safe /3 | Oracle utility /3 |
|---|---|---:|---:|---:|---:|---:|---:|
| OULU | DINO-Reg |87.77|36.13|91.94|46.67|0|0|
| OULU | Supervised CLIP |79.20|16.62|53.70|23.43|0|0|
| OULU | Fixed two-DINO |86.60|58.87|97.13|41.11|0|0|
| OULU | Matched DeepPixBiS |91.98|15.12|81.11|58.70|0|3|
| CASIA | DINO-Reg |99.94|0.00|39.26|98.89|3|3|
| CASIA | Supervised CLIP |98.20|0.00|46.67|85.56|3|3|
| CASIA | Fixed two-DINO |99.94|0.00|40.37|98.89|3|3|
| CASIA | Matched DeepPixBiS |86.61|1.48|42.59|54.81|3|2|
| MSU | DINO-Reg |87.56|41.67|90.00|42.50|0|0|
| MSU | Supervised CLIP |89.22|9.17|65.00|57.50|0|3|
| MSU | Fixed two-DINO |92.67|22.78|92.50|68.33|0|3|
| MSU | Matched DeepPixBiS |92.98|8.89|79.17|52.50|0|1|
| SiW | DINO-Reg |88.01|9.67|58.24|34.87|0|0|
| SiW | Supervised CLIP |85.02|3.59|31.42|38.19|3|0|
| SiW | Fixed two-DINO |87.38|16.02|74.33|45.72|0|0|
| SiW | Matched DeepPixBiS |76.00|49.82|87.36|23.75|0|0|

All48 seed-level primary rows, their integer support/acceptance counts,
conditional policy intervals and108 primary paired metric differences
are in the [complete tables](../../results/phase1/paper324-primary-tables-v1.md).
The [case CSV](../../results/phase1/paper324-cases-v1.csv) retains all144
operating cases, including usable-only errors, source limiting datasets
and integer attack budgets. No best seed is selected.

### 6.2 Available policies and empirical oracle headroom

At5% attack FA,15/48 source policies are empirically FA-safe but0/48 also
reach50% BFA. Oracle thresholds admit the joint utility in21/48 cases:
11/12 CASIA,7/12 MSU,3/12 OULU and0/12 SiW. All27 remaining failures are
classified as insufficient low-FA separation of the stored scalar scores;
none is caused solely by a technical-failure BFA ceiling below50%.

The CASIA policies demonstrate threshold-placement headroom particularly
clearly: all are FA-safe, yet accept too few bona-fide observations.
For DINO-Reg, mean policy BFA39.26% contrasts with oracle BFA98.89%.
This is hindsight headroom, not evidence that a target-label-free threshold
can recover the difference. On targets where the policy violates5% FA,
subtracting its BFA from the constrained oracle's BFA is not a same-security
gain or calibration loss.

The specialist changes the narrower OULU diagnosis: it attains the oracle
utility in3/3 seeds, whereas the three frozen systems attain0/3 each.
Its oracle BFA ranges56.39--61.94%, while its actual source policies all
violate5% FA. Conversely, specialist oracle attainment is seed-dependent
on CASIA (2/3) and MSU (1/3), and fails on SiW (0/3).
The completed specialist comparison therefore rejects a universal
``OULU is impossible'' interpretation of the developmental frozen-score
results, while not supplying a deployable OULU policy.

### 6.3 Conditional paired uncertainty and seed variability

All756 conditional/paired interval records retain2000/2000 valid draws.
The [interval CSV](../../results/phase1/paper324-intervals-v1.csv) supplies
FA, BFA and AUROC intervals and corresponding paired differences from
DINO-Reg at all three alpha values, with explicit resampling units.
These condition on saved models and fixed source policies, are not
multiple-testing-adjusted and do not establish population security.
In particular, a zero empirical FA and degenerate bootstrap interval
cannot exclude attack events absent from the sample.

For illustration, specialist-minus-DINO-Reg usable AUROC on OULU is
+4.49,+4.23,+3.90 percentage points across the three seeds, with conditional
95% intervals[1.06,7.68],[1.03,6.96],[0.69,6.80].
On CASIA those differences are-15.82,-13.47,-10.70 points, with all three
intervals below zero. This is a dataset-dependent comparison, not a pooled
superiority test. CLIP-minus-DINO-Reg AUROC differences on MSU are positive
(+1.55 to+1.79 points), but all three paired intervals include zero.
Its higher MSU oracle BFA must not be promoted to a confidence-backed
general superiority claim.

### 6.4 Sensitivity and computation

**Table5. Individual-case utility counts at predeclared attack-FA bounds;
the50% BFA floor is unchanged. The5% endpoint remains primary.**

| Attack-FA bound | Cases | Source-policy FA-safe | Source-policy joint utility | Oracle joint utility |
|---|---:|---:|---:|---:|
|1%|48|22|0|12|
|5%|48|15|0|21|
|10%|48|15|10|42|

Changing alpha also changes each source-derived threshold, so the count
of transferred FA-safe policies need not be monotone. The10% sensitivity
does not rescue or replace the failed primary5% source-policy endpoint.
The [low-FA curves](../../results/phase1/paper324-low-fa-v1.svg) retain each
seed; equal-target macro and worst-target results for every seed/alpha are
in the [aggregate closure](../../results/phase1/paper324-comparison-v1.json).
They report FA alongside BFA and do not rank unsafe policies on BFA alone.

The explicitly approved323 continuation and reconstruction took32643.85
seconds (9.07 hours), with sampled combined peak RSS2.20GiB and275.56MiB
owned outputs across attempts before terminal closure. Earlier stopped
attempts are separate sunk execution costs, not included in that wall time.
Across322/323 there were39 frozen-head,12 specialist and52 calibrator fit
starts; three heads and four calibrators were deterministic recovery refits.
There were600 specialist epochs,74400 specialist optimizer steps and no new
foundation-encoder forwards. Execution changes concerned compatibility and
phase budgets, not the scientific recipe or target-label model selection.

## 7. Discussion

The completed evidence cautions against describing every transferred
operating failure as calibration. A score with large oracle headroom
and a score whose low-FA oracle remains unusable present different practical
problems. The first motivates investigation of target-label-free threshold
transfer; the second requires a different score or decision function if the
same empirical utility is to be reached.

Neither diagnosis identifies a successful remedy. Positive monotone
calibration does not generally repair ranking, and hindsight thresholds
must not be used to claim a source-only improvement. The matched specialist
comparison shows that the OULU score limitation is not shared by every
tested representation: the specialist retains empirical oracle headroom.
Yet its source policies still fail the declared utility, and it performs
worse on other targets. This comparison cannot establish universality.

CLIP remains a comparator rather than a promised source of incremental
utility. Its MSU oracle performance prevents an unqualified claim that CLIP
is useless, while its poor OULU operating results and the separate absent
feasible fusion policies do not justify retaining it as a fusion component.
There is no new matched DINO-CLIP fusion result in the official-partition
comparison. These distinctions must not be hidden to sustain an improvement
narrative.

## 8. Limitations, reproducibility and responsible interpretation

- All four datasets have informed method development. No untouched
  confirmation is claimed.
- Earlier and supplementary studies use different source populations and
  may not be pooled or directly compared to unmatched literature scores.
- Single-middle-frame sampling omits temporal information and does not
  reproduce video aggregation.
- SiW participant identities are unknown. Video-level grouping may retain
  dependence between videos of the same person.
- Calibration support is small in some sources; low empirical FA is not
  a statistically certified security rate. Aggregate attack FA can hide
  attack-species variation.
- Bootstrap intervals condition on fitted models and thresholds and do not
  capture full training or domain-selection uncertainty.
- Oracle analysis is exploratory and score-specific, including stored
  probability ties and saturation.
- Encoders, input resolution, pretraining exposure and specialist training
  differ. This is not a causal architecture ablation.
- Source manifests contain exclusions and technical failures; their
  denominators must remain visible.
- Private biometric images, video IDs and individual scores are not
  redistributed. Public aggregate receipts, hashes, code and permitted
  protocol details support auditing but are not external replication.

Existing results and implementation are available in the
[project repository](https://github.com/lathevinh/fas).
The [integrated package](../319-integrated-paper-completion-package.md)
links exact source reports and the original specification. The
[completed comparison report](../324-completed-comparison-results-and-paper-update.md)
binds all measured supplementary exports. Dataset access
remains subject to original licenses; no new dataset acquisition is part
of this package.

## 9. Conclusion

The completed official-partition comparison distinguishes failed available
operating policies from score-specific low-FA limitations: no primary
source-derived policy meets the joint utility, while21/48 saved scores
admit it under evaluation-label oracle thresholds. The specialist supplies
OULU oracle headroom absent from the tested frozen systems but not a usable
source-only policy or universal improvement. CLIP remains an informative
comparator, not a demonstrated fusion remedy. Historical nested fusion
infeasibility is supporting evidence from a distinct population.

The contribution is a bounded empirical characterization, not a new
thresholding algorithm, a target-label-free adaptation method or proof that
all PAD methods fail. Whether its exact paired-policy/oracle evidence adds
sufficient insight beyond closest work remains a venue and peer-review
question; completed computation alone does not establish novelty or
publication readiness.

## References

[1] P. Lorenz, A. George, and S. Marcel. *Foundation Models for Face
Presentation Attack Detection: A Unified Linear-Probing Benchmark.*
Accepted at IJCB2026; arXiv:2607.26993.
https://arxiv.org/abs/2607.26993

[2] A. Costa-Pazo et al. *Face presentation attack detection. A comprehensive
evaluation of the generalisation problem.* IET Biometrics,2021.
https://doi.org/10.1049/bme2.12049

[3] A. George and S. Marcel. *Deep Pixel-wise Binary Supervision for Face
Presentation Attack Detection.* ICB,2019.
https://publications.idiap.ch/attachments/papers/2019/George_ICB2019.pdf

[4] M. Oquab et al. *DINOv2: Learning Robust Visual Features without
Supervision.* arXiv:2304.07193,2023.
https://arxiv.org/abs/2304.07193

[5] T. Darcet, M. Oquab, J. Mairal, and P. Bojanowski.
*Vision Transformers Need Registers.* arXiv:2309.16588,2023.
https://arxiv.org/abs/2309.16588

[6] M. Cherti et al. *Reproducible Scaling Laws for Contrastive Language-Image
Learning.* CVPR,2023.
https://doi.org/10.1109/CVPR52729.2023.00276

[7] Z. Boulkenafet et al. *OULU-NPU: A Mobile Face Presentation Attack
Database with Real-World Variations.* FG,2017.
https://doi.org/10.1109/FG.2017.77

[8] Z. Zhang et al. *A Face Antispoofing Database with Diverse Attacks.*
ICB,2012.
https://doi.org/10.1109/ICB.2012.6199754

[9] D. Wen, H. Han, and A. K. Jain. *Face Spoof Detection With Image
Distortion Analysis.* IEEE TIFS,2015.
https://doi.org/10.1109/TIFS.2015.2400395

[10] Y. Liu, J. Stehouwer, A. Jourabloo, and X. Liu. *Deep Tree Learning for
Zero-Shot Face Anti-Spoofing.* CVPR,2019.
https://doi.org/10.1109/CVPR.2019.00481

[11] P. Lorenz, A. George and S. Marcel. *LoRA-based Adaptation Alone Is Not Enough:
Understanding the Limits of Foundation Models for Face PAD.*
arXiv:2608.09633,2026.
https://arxiv.org/abs/2608.09633

[12] M. Feng, P. Gallin-Martel, K. Ito, and T. Aoki. *Benchmarking Vision Foundation
Models for Domain-Generalizable Face Anti-Spoofing.* CVPRW,2026;
arXiv:2604.19196.
https://arxiv.org/abs/2604.19196

The SiW-Mv2 release-list provenance and local intersection are documented in
the [accepted population receipt](../../results/phase1/siwmv2-intersection-v1.json),
not inferred from the original SiW-M paper. Bibliographic formatting and
complete author lists must follow the selected venue before submission.
Development evidence: [309](../309-source-only-cached-readout-results.md),
[314](../314-nested-fusion-utility-results.md) and
[316](../316-saved-score-oracle-threshold-diagnosis.md).
