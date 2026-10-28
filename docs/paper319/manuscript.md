# Beyond AUROC: Operating-Point Transfer of Frozen Foundation Models for Face Presentation Attack Detection

**Working manuscript,2026-10-28. Not submission-ready.**
The official-partition supplementary study is specified but has not run.
Sections labeled pending contain no measured supplementary results.
Development results below retain their original populations and limitations.
Author names, affiliations and submission metadata remain to be supplied.

## Abstract

Face presentation attack detection (PAD) under dataset shift requires more
than favorable aggregate ranking: a decision threshold derived from available
source data must retain both attack rejection and bona-fide usability.
This study examines a small fixed set of frozen-feature PAD systems using
DINOv2 and OpenCLIP representations. We distinguish performance at
source-derived thresholds from evaluation-label oracle operating points,
the latter serving only as empirical diagnostics of fixed scalar scores.
In completed source-development analyses, none of54 held-out OULU
fixed-reference cases attains50% bona-fide acceptance at attack false
acceptance at most5%, even with oracle thresholds; all54 CASIA cases admit
such a threshold. A separate matched nested comparison of DINO-CLIP and
two-DINO mixtures yields no feasible selected policy under the declared
operating constraints. These observations distinguish threshold headroom
from insufficient low-FA score separation and do not constitute a deployable
adaptation method. A specified train-three/test-one comparison against a
matched specialist PAD model will evaluate this diagnosis under official
source-partition restrictions. **Those results and the final abstract
conclusion are pending.** The current evidence is developmental, not
confirmation on previously unseen datasets.

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

This paper develops the following empirical contributions, subject to the
pending matched comparison and closest-work assessment:

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
an established concern. Comparisons across papers require matching datasets,
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

George and Marcel [11] also examine foundation-model limits under zero-shot
and LoRA adaptation in a single-source MCIO setting. Gallin-Martel et al. [12]
already study register-DINO and multi-source MICO/LSD evaluation with
augmentation/loss interventions. Thus multi-source leave-one-out structure
and register-DINO are not novel contributions here either. The candidate
distinction is the explicitly paired source-policy and low-FA oracle
diagnosis, not those components in isolation.

### 2.3 Specialist PAD and operating diagnostics

DeepPixBiS [3] uses pixel-wise and global supervision for PAD. We propose
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
content crossings without altering the archival population. The proposed
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
- **Pending matched supplementary comparison:** official source train/
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
applies to the proposed model selection and threshold estimates as well as
the analysis. No filename-derived identities are fabricated.

## 4. Methods

### 4.1 Fixed representations and readouts

DINOv2 [4] ViT-B/14 with and without four register tokens [5] supplies concatenated
CLS and mean patch-token features,1536 dimensions. OpenCLIP ViT-B-16 with
laion2b_s34b_b88k initialization supplies normalized512-dimensional image
embeddings [6]. Encoders remain fixed. DINO and CLIP use their existing native
crop/normalization contracts; these are not identical resolutions.

Proposed frozen heads use200 epochs of FP64 full-batch AdamW with equal-source,
equal-class BCE. DINO learning rate is.001 and CLIP learning rate.01; weight
decay is.05, excluding bias. The minimum validation-BCE checkpoint is selected,
with earliest-epoch ties and no refit. These recipes were chosen during
earlier development, not independently preregistered before all data exposure.

The two-DINO reference is the fixed mean of separately calibrated register
and plain DINO probabilities. It has no new mixture-weight selection.

### 4.2 Proposed specialist comparator

The matched DeepPixBiS architecture uses a DenseNet161-derived representation,
a pixel map and a global binary output. Proposed initialization is ImageNet
DenseNet161 rather than pretrained PAD weights. Training uses the fixed
researcher-specified50-epoch recipe in the accompanying protocol, with
source-only checkpoint selection.

This is not claimed to reproduce the original paper's exact training
hyperparameters or reported accuracy. Specialist learning adapts its feature
extractor, whereas the foundation branches do not; compute, augmentation and
pretraining differences are disclosed. The comparison is not a causal
isolation of one architectural factor.

### 4.3 Proposed source-only protocol

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

The proposed supplementary analysis uses2000 paired cluster-bootstrap
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
results, not the pending official-partition comparison or a direct published
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

## 6. Pending matched comparison

**No results exist for this section.** The metadata preflight verifies
populations and cache receipt coverage, not classifier performance.

**Table3. Planned primary reporting layout, repeated for each of three seeds.**

| Target | System | AUROC, usable | Source-policy FA/BFA, all originals | Oracle BFA at5% FA | Support / conditional intervals |
|---|---|---|---|---|---|
| Each of four targets | DINO-Reg | Pending | Pending | Pending | Pending |
| Each of four targets | Supervised CLIP | Pending | Pending | Pending | Pending |
| Each of four targets | Fixed equal two-DINO | Pending | Pending | Pending | Pending |
| Each of four targets | Matched DeepPixBiS | Pending | Pending | Pending | Pending |

All48 target/system/seed rows must be retained, with no best-seed-only table.
The1%/10% sensitivity, low-FA ROC view, timing and memory will be reported
after the single approved computation. No expected winner is asserted.

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
comparison is needed to contextualize whether the observed limitations are
specific to these frozen readouts or also affect the selected PAD baseline.
Even that comparison cannot establish universality.

CLIP remains a comparator rather than a promised source of incremental
utility. A supervised readout improvement and absent feasible fusion policies
are compatible findings; neither should be hidden to sustain an improvement
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
links exact source reports and the pending specification. Dataset access
remains subject to original licenses; no new dataset acquisition is part
of this package.

## 9. Provisional conclusion

Completed developmental evidence distinguishes substantial threshold
headroom on CASIA from insufficient empirical low-FA separation on OULU
for the tested fixed scalar scores. Matched nested fusion does not yield
an available feasible selected policy. These findings motivate operating-
point reporting beyond AUROC but do not establish a deployable remedy.
**The final comparative conclusion awaits the specified specialist and
official-partition evaluation and must be revised to match those results.**

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

[11] A. George and S. Marcel. *LoRA-based Adaptation Alone Is Not Enough:
Understanding the Limits of Foundation Models for Face PAD.*
arXiv:2608.09633,2026.
https://arxiv.org/abs/2608.09633

[12] Gallin-Martel, Feng, Ito, and Aoki. *Benchmarking Vision Foundation
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
