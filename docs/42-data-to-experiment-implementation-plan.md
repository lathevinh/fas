# Data-to-Experiment Implementation Plan

Date: 2026-09-18
Status: execution blueprint frozen before dataset-facing code

## 1. Purpose and authority

This document turns the frozen research method into an operational plan from dataset
access through confirmatory evaluation. It is subordinate to the scientific contracts
in `docs/00-project-charter.md` through `docs/06-risks-and-decisions.md`, the accepted
Round-14 through Round-16 responses, the dependency order in
`docs/38-implementation-plan.md`, and the paper contract in
`docs/40-paper-skeleton.md`.

This plan does not authorize target-driven debugging. Implementation proceeds through
synthetic tests, source-only audits, and source-only dry runs. A data custodian may
ingest labels to construct sealed manifests, but an experiment for outer target $T$
cannot expose $T$ labels, class/attack counts, or target-derived diagnostics before
the analysis freeze in Phase 7. The same dataset may expose labels through a separate
source namespace when it is a source in another outer fold.

The core track is four-fold MICO using OULU-NPU, CASIA-FASD, Replay-Attack, and
MSU-MFSD. SiW-M, CelebA-Spoof, LoRA, routing, and cue analysis are optional work after
the core RQ1 analysis.

## 2. Non-negotiable operating rules

1. Raw archives and biometric data never enter Git.
2. Official protocols are parsed before frames are extracted.
3. Subject/video roles are assigned once per dataset and reused whenever that dataset
   is a source.
4. A video, subject, or duplicate capture may not cross source roles.
5. Filesystem folders are storage locations, not labels or split authority. Versioned
   manifests are the sole source of truth.
6. No target sample selects a checkpoint, prompt, crop, feature, threshold, baseline,
   effect rule, or analysis choice.
7. Frozen encoders are run sequentially on the RTX 4080. Features are cached; labels
   never enter a feature cache key.
8. The primary experiment does not fine-tune either foundation backbone.
9. Every derived artifact carries hashes for code, configuration, input manifests,
   and upstream artifacts.
10. Detector failures remain transactions. They become terminal non-accept outcomes
    and are not silently removed from end-to-end metrics.

## 3. Storage and repository layout

Set private roots outside the repository:

```bash
export FAS_DATA_ROOT=/secure/fas-data
export FAS_ARTIFACT_ROOT=/secure/fas-artifacts
export FAS_RUN_ROOT=/secure/fas-runs
```

Expected private layout:

```text
$FAS_DATA_ROOT/
  agreements/                       # licenses, approvals, request records
  downloads/                        # original archives, never modified
    oulu_npu/<release>/
    casia_fasd/<release>/
    replay_attack/<release>/
    msu_mfsd/<release>/
    siw_m/<release>/                 # optional
  raw/                              # checksum-verified extraction, read-only
    <dataset>/<release>/
      media/
      official_protocols/
      release_documents/
  interim/
    media_inventory/<dataset>/<version>/
    frame_index/<dataset>/<version>/
    frames/<dataset>/<frame_version>/<video_id>/
    crops/<dataset>/<crop_version>/<video_id>/
  manifests-private/
    canonical/<dataset>/<manifest_version>.parquet
    roles/<dataset>/<role_version>.parquet
    folds/mico/<fold_version>/
    audits/<audit_version>/

$FAS_ARTIFACT_ROOT/
  features/<extractor_id>/<manifest_hash>/<shard>.safetensors
  models/<experiment_id>/<target>/<seed>/<component>/
  predictions/<experiment_id>/<target>/<seed>/
  oof/<experiment_id>/<target>/<seed>/<strategy>/
  risk/<experiment_id>/<target>/<seed>/<strategy>/
  policies/<experiment_id>/<target>/<seed>/

$FAS_RUN_ROOT/
  <experiment_id>/
    resolved-config.yaml
    environment.json
    lineage.json
    logs/
    metrics/
    figures/
```

The repository contains only code, schemas, fixed configs, private-manifest templates,
public aggregate counts/hashes, and non-sensitive result summaries. `data/` must not
be introduced inside the repository. Existing `manifests/` stores schemas and public
summaries only.

Do not physically duplicate frames into `train/`, `validation/`, and `test/`
directories. If a framework requires folder-shaped input, generate a disposable
read-only symlink view:

```text
$FAS_RUN_ROOT/<experiment_id>/views/<fold>/<role>/<class>/<sample_id>.jpg
```

The view is generated from a signed manifest, never edited manually, and never used
as the canonical split record.

## 4. Dataset acquisition and intake

### 4.1 Access checklist

For each dataset, the data steward must:

1. obtain the dataset from the official owner or owner-designated channel;
2. save the license, access approval, release/version, download date, and official
   protocol documentation under `agreements/` or `release_documents/`;
3. retain the original archive unchanged under `downloads/`;
4. compute SHA-256 for every archive and protocol file;
5. extract into a new versioned `raw/` directory and make it read-only;
6. record whether redistribution, derived frames, model weights, and metadata counts
   may be published;
7. reject unofficial mirrors unless the owner confirms equivalence.

Dataset-specific intake scope:

| Dataset | Core role | Intake requirement |
|---|---|---|
| OULU-NPU | MICO source/target | Preserve official protocol, device, session, environment, subject, and attack metadata |
| CASIA-FASD | MICO source/target | Preserve train/test metadata and quality/attack-medium identity when officially available |
| Replay-Attack | MICO source/target | Preserve official train/devel/test and controlled/adverse conditions |
| MSU-MFSD | MICO source/target | Verify subject/video identity carefully because the dataset is small |
| SiW-M | Optional attack-shift target | Obtain official zero-shot protocol and attack-family definitions before activation |
| CelebA-Spoof | Optional extra-data ablation | Keep entirely outside strict MICO source supervision |

No acquisition script will bypass authentication or redistribute protected URLs.
Adapters receive a local raw root after access is granted.

### 4.2 Intake acceptance report

Each adapter first emits a media inventory without decoding training tensors:

- release and protocol identifiers;
- archive and protocol SHA-256 values;
- relative media path, byte size, container/codec, duration, FPS, frame count, and
  decode status;
- official split and raw label tokens;
- parsed subject, video, session, device, environment, and attack identifiers;
- missing or ambiguous identifiers requiring manual resolution.

The adapter fails closed on unknown labels, duplicate official IDs, unreadable
protocol records, or disagreement between protocol and filesystem counts. Unknown
optional attributes remain `unknown`; they are never inferred from filenames without
a documented dataset rule.

## 5. Canonical labels and manifests

### 5.1 Label contract

The canonical semantic label is an enum:

```text
binary_label = bona_fide | attack
```

At the model boundary only, encode `bona_fide=0` and `attack=1`; larger PAD logits and
probabilities therefore mean greater attack probability. Preserve the original label
and mapping rule in separate fields. `attack_family`, `instrument`, and `material`
must be mapped through versioned per-dataset tables. Ambiguous values remain
`unknown`; no row is relabeled by visual inspection after target access.

### 5.2 Required video-level fields

```text
dataset, release_id, source_record_id, subject_id, video_id,
official_split, binary_label, attack_family, instrument, material,
session_id, sensor_id, environment, media_relpath, media_sha256,
duration_ms, fps, frame_count, decode_status, label_source
```

### 5.3 Required frame-level fields

```text
sample_id, dataset, subject_id, video_id, frame_id, frame_index,
timestamp_ms, frame_selector, frame_version, frame_relpath, frame_sha256,
binary_label, attack_family, official_split, source_role,
outer_target, detector_status, crop_relpath, crop_version,
face_box_xyxy, landmarks, detector_confidence, face_area_ratio,
mean_luminance, contrast, blur, manifest_version
```

`sample_id` is stable and content-independent:

```text
<dataset>/<release>/<subject_id>/<video_id>/<frame_selector>/<frame_index>
```

Private manifests may contain local paths. Public summaries contain only dataset-level
counts, schema versions, mapping versions, and hashes.

The required video-level fields additionally include `raw_label_token`,
`label_mapping_id`, `label_mapping_version`, and `label_mapping_hash`. Per-dataset
adapter fixtures must prove the canonical polarity `bona_fide=0`, `attack=1`, larger
classifier score means attack, and `error=1` means a wrong fixed-classifier decision.

## 6. Role assignment and MICO folds

### 6.1 Official protocol first

Every dataset adapter exposes official roles without rewriting them. A versioned
dataset policy then declares which official partitions are eligible when the dataset
acts as a source and which official evaluation partition is used when it acts as the
outer target. This mapping is approved during the data audit and frozen before any
target result. Where publications use a recognized cross-dataset convention, match
that convention and document any deviation.

### 6.2 Immutable source roles

Within the eligible source pool, assign complete subject groups, or complete video
groups if subject identity is genuinely unavailable, to these immutable roles:

| Role | Purpose | May train a fitted component? |
|---|---|---:|
| `source_train` | Branch fitting and fold-local inner validation | Yes |
| `branch_calibration` | One-stage branch affine calibration | Calibrator only |
| `gate_domain` | Final post-VLM gate threshold and ranking sanity check | No |
| `routing_validation` | Optional routing threshold after core claims | No |

Do not freeze universal percentages before seeing source-side event counts. For outer
fold $T$, the role builder takes preregistered fractions as initial values, then may
perform one feasibility pass using only its three source domains and their
domain/class/attack-event counts. Target $T$ statistics cannot influence that fold's
roles. Any rule change that would affect all folds must be chosen without inspecting
any target result, applied symmetrically, documented, and frozen before confirmatory
evaluation. The algorithm is deterministic given dataset release, role-policy
version, outer target, and seed.

Stratification priority is dataset protocol, subject, binary class, attack family,
device/session, then environment. If exact stratification is impossible, preserve
group integrity and report the imbalance rather than splitting a subject or video.

### 6.3 Outer folds

Create exactly four MICO folds:

| Fold | Source domains | Untouched target domain |
|---|---|---|
| `T_oulu` | CASIA-FASD, Replay-Attack, MSU-MFSD | OULU-NPU |
| `T_casia` | OULU-NPU, Replay-Attack, MSU-MFSD | CASIA-FASD |
| `T_replay` | OULU-NPU, CASIA-FASD, MSU-MFSD | Replay-Attack |
| `T_msu` | OULU-NPU, CASIA-FASD, Replay-Attack | MSU-MFSD |

For fold $T$, only source-role manifests from the other three datasets are visible to
training commands. The target loader is a separate evaluation-only API and rejects
fit, calibration, threshold, and configuration-selection modes.

The data custodian writes separate access-controlled namespaces for each outer fold.
Experiment code receives either `source/<T>` with labels or `target/<T>` with labels
sealed. The evaluator releases target labels only to the locked analysis command and
never returns per-sample labels to training or configuration code.

### 6.4 Inner and OOF splits

- **Head inner validation:** deterministic subject-disjoint split inside the allowed
  `source_train` remainder; used only for checkpoint selection.
- **Domain-OOF:** rotate one whole source dataset as pseudo-target. Its branch
  calibration and OOF predictions come only from the other allowed source domains.
- **Sample-OOF:** within each source domain, create subject-disjoint folds while all
  three source domains remain represented in each fitting remainder.
- **Permanent gate set:** `gate_domain` is removed before either OOF strategy and is
  used only after the final source models and risk estimators are frozen.

Before either OOF strategy, create one immutable candidate-ID ledger from eligible
`source_train` records after removing `gate_domain`, `branch_calibration`, and optional
routing records. Domain-OOF and sample-OOF must each emit exactly one prediction for
every ledger ID. The engine rejects missing, duplicate, or unequal ID sets. For every
pseudo-fold it records disjoint fit IDs, fold-local calibration IDs, and held-out
prediction IDs; no held-out candidate may calibrate the predictor that scores it.

Group overlap, near-duplicate media hashes, and derived-frame ancestry are checked
across every role and fold. Any overlap is a hard error.

## 7. Frame extraction and face preprocessing

### 7.1 Decode index

Build a deterministic frame index with a pinned FFmpeg version. Record presentation
timestamp, decode order, keyframe status, dimensions, and decode success. Selection is
defined over successfully decoded frames inside the official valid interval, not over
nominal FPS alone.

### 7.2 Frame banks

Create two distinct banks:

1. **Training candidate bank:** deterministic uniformly spaced candidate indices per
   source video. The exact candidate count is fixed after a source-only storage and
   throughput audit. During each head-training epoch, the hierarchical sampler draws
   at most three candidates from a video using the run seed.
2. **Evaluation bank:** one primary frame at the 50% decoded position plus fixed 25%
   and 75% frames for sensitivity analysis. The primary selector chooses the middle
   frame that decodes in the official interval before face detection. It must not
   search for a detector-successful substitute.

The OOF, branch-calibration, gate, and strict single-image target tables use the same
primary one-frame-per-video unit. Multi-frame and benchmark-compatible aggregation are
reported separately and retain subject/video-clustered uncertainty.

Store extracted RGB images losslessly when permitted. Otherwise use a single frozen
JPEG quality setting and record encoder/version metadata. Never repeatedly transcode.

### 7.3 Face detection and crop

Use one pinned detector and checkpoint, selected before target access. The initial
implementation may support SCRFD or RetinaFace behind one interface, but the Phase-0
config must name exactly one primary detector/checkpoint from documented operational
availability without comparing FAS dataset outcomes. Later source-only coverage tests
validate that frozen choice; they cannot select between detectors.

For every selected frame:

1. run the detector once with fixed thresholds;
2. choose the deterministic primary face by the frozen rule;
3. apply light eye alignment when landmarks are valid;
4. expand the face box by the fixed 1.30 context factor and clip to image bounds;
5. save shared crop geometry and quality features;
6. derive branch-native resized/normalized tensors from the same crop.

If detection fails, write `detector_status=failed`, retain the transaction, and do not
create fake branch features. Do not retry with another frame. DINO and OpenCLIP share
crop geometry but keep their native resize, interpolation, and normalization.

### 7.4 Extraction validation

Before full extraction, validate a balanced source-only shard:

- frame indices and checksums repeat exactly;
- no video contributes more units than configured;
- crop coordinates remain within image bounds;
- visual contact sheets contain no labels and are reviewed source-only;
- detector failures are counted by dataset and class;
- frame/crop manifests join one-to-one with their parent videos;
- disk and decode throughput fit the available budget.

## 8. Model and feature plan

### 8.1 Primary DINOv2-Reg branch

- Backbone: pretrained `dinov2_vitb14_reg4` with frozen weights.
- Representation: concatenate the 768-dimensional CLS token and 768-dimensional mean
  patch token; register tokens remain internal and are not pooled as spatial evidence.
- Primary head: one linear binary layer over the 1536-dimensional frozen vector.
- Loss: equal-domain, class-balanced BCE on source fitting data.
- Sampling: dataset, class, attack family, video, then frame; at most three frames per
  video per epoch.
- Selection: lowest equal-domain class-balanced BCE on fold-local subject-disjoint
  inner validation; ties choose the earlier epoch.
- Seeds: the three globally frozen seeds from `configs/seeds_v1.yaml` after Phase 0
  reconciliation.

Head optimizer, learning rate, weight decay, maximum epochs, batch size, and patience
are frozen using synthetic tests and source-only dry runs. They cannot change after an
outer target is opened.

### 8.2 Primary OpenCLIP branch

- Model: OpenCLIP `ViT-B-16`, weights `laion2b_s34b_b88k`.
- Preprocessing: checkpoint-native 224-pixel resize/normalization on the shared 1.30
  context crop.
- Encoders: image and text encoders frozen.
- Prediction: immutable generic live/spoof core prompts, class-wise mean cosine, and
  raw logit $\ell_V=s_{spoof}-s_{live}$.
- Fitted parameters: only the positive-slope affine branch calibrator.

No prompt search, supervised visual head, template weighting, or VLM checkpoint search
may replace this primary path. Those are labeled secondary diagnostics.

### 8.3 Same-family control

Use frozen plain DINOv2 ViT-B/14 with the same CLS-plus-mean-patch representation,
linear-head capacity, sampling, loss, checkpoint selection, branch calibration,
fusion, risk estimation, gate selection, and transaction accounting. Reuse the exact
fitted DINOv2-Reg anchor artifacts across heterogeneous and same-family comparisons.

### 8.4 Feature extraction and cache

Run one encoder at a time:

1. DINOv2-Reg source features;
2. plain DINOv2 source features;
3. OpenCLIP source image features and frozen text embeddings;
4. after the analysis freeze, the corresponding target extraction.

Each feature shard stores sample IDs, representation name, tensor shape/dtype,
extractor/checkpoint hash, preprocessing/crop hash, manifest hash, and numerical
parity metadata. Use FP16 storage only after FP32-versus-FP16 source parity passes;
compute calibration and metrics in FP32 or FP64 as specified. A resumed shard must
match every identity field or be rejected.

### 8.5 Fine-tuning policy

The primary paper is a frozen-backbone experiment. No full fine-tuning is planned.
Only after the core frozen experiment and claim decisions are complete may a separate
ablation add LoRA/adapters to the last four DINO blocks or the OpenCLIP image encoder.
Such an ablation gets new configs, caches, models, and tables; it may not overwrite or
retroactively tune the confirmatory system. Joint consistency/agreement training and
text-encoder fine-tuning remain prohibited.

## 9. Training and calibration workflow

For every outer target $T$ and seed:

### 9.1 Final source classifier

1. Load only the three source-domain role manifests.
2. Remove `gate_domain`, `branch_calibration`, and optional routing records from head
   fitting.
3. Derive and serialize the subject-disjoint inner validation split.
4. Train the frozen-feature DINOv2-Reg linear head and select its checkpoint.
5. Produce raw DINO and fixed OpenCLIP logits on `branch_calibration`.
6. Fit one positive-slope affine calibrator per branch with class-balanced loss inside
   each source domain and equal weighting across domains.
7. Produce calibrated source predictions and choose the fixed reference classifier
   threshold using the source-only operating-point rule.
8. Freeze the calibrated average
   $p_F=(\widehat p_D+\widehat p_V)/2$ as the heterogeneous classifier.

Calibration occurs exactly once. Do not stack a fusion calibrator or recalibrate on
OOF, gate, or target samples.

### 9.2 Domain-OOF risk records

For each of the three source domains in turn:

1. hold that domain out completely;
2. train/select the DINO head on the allowed remainder;
3. fit both branch calibrators on disjoint calibration records from that remainder;
4. choose a fold-local reference threshold on allowed source records;
5. predict the held-out domain's primary frames;
6. record calibrated probabilities, absolute disagreement, fixed image-quality
   features, operational margin, prediction, and error label.

Concatenate the three held-out-domain tables with equal pseudo-domain weighting.

### 9.3 Matched sample-OOF records

Use the identical source candidate universe, frame unit, feature code, model family,
regularization, and optimization budget. Replace only the held-out unit with
subject-disjoint within-domain folds. Record effective fit size and natural error
prevalence per pseudo-fold. If fit sizes differ beyond the source-frozen tolerance,
run the preregistered budget-matched sensitivity without downsampling errors.

### 9.4 Risk fitting

Fit fixed-regularization logistic models for:

```text
R_q     = [q]
R_D     = [p_D, q]
R_V     = [p_V, q]
R_DV    = [p_D, p_V, q]
R_DVd   = [p_D, p_V, abs(p_D - p_V), q]       # RQ1 primary
R_DVdm  = [p_D, p_V, abs(p_D - p_V), margin, q]
```

Only quality features `[blur, mean_luminance, contrast, face_area_ratio,
detector_confidence]` are standardized, using allowed source-fit statistics. Preserve
natural error prevalence and average unweighted BCE equally across pseudo-domains.
Fit required MSP/entropy, policy-margin, Mahalanobis, and capacity-matched nonlinear
comparators on the same fixed classifier errors.

### 9.5 Gate selection

Apply frozen final branches and risk models to the untouched `gate_domain` records.
First report risk AUPR, AUROC, Brier, and risk-coverage validity against the frozen
source sanity criterion. Then select only the post-VLM accept/abstain threshold under
the source-only utility/security rule. Do not refit any branch, calibrator, risk model,
or feature normalization after this step.

## 10. Planned command surface

Commands are implemented in dependency order; names below define the intended CLI
contract rather than asserting that they already exist:

```bash
# Phase 0: governance and synthetic contracts
python -m fas.cli.validate_config --stage schema --config configs/experiment_core_v1.yaml
python -m pytest tests/governance tests/contracts

# Phase 1: private dataset intake
python -m fas.cli.inventory --dataset <name> --raw-root <path> --out <private-path>
python -m fas.cli.build_manifest --dataset <name> --policy <policy.yaml>
python -m fas.cli.assign_roles --dataset <name> --policy configs/roles_v1.yaml
python -m fas.cli.audit_manifest --manifest <roles.parquet>

# Frames and crops
python -m fas.cli.index_video --manifest <video-manifest>
python -m fas.cli.extract_frames --manifest <frame-index> --config configs/frames_v1.yaml
python -m fas.cli.detect_crop --manifest <frames> --config configs/preprocessing_v2.yaml

# Frozen features
python -m fas.cli.extract_features --backbone dinov2_reg --manifest <frames>
python -m fas.cli.extract_features --backbone dinov2_plain --manifest <frames>
python -m fas.cli.extract_features --backbone openclip --manifest <frames>

# Source training and OOF
python -m fas.cli.fit_branches --target <target> --seed <seed> --config <freeze.yaml>
python -m fas.cli.build_oof --strategy domain_oof --target <target> --seed <seed>
python -m fas.cli.build_oof --strategy sample_oof --target <target> --seed <seed>
python -m fas.cli.fit_risk --target <target> --seed <seed>
python -m fas.cli.select_gate --target <target> --seed <seed>

# Freeze, confirmatory prediction, and analysis
python -m fas.cli.freeze_analysis --config <resolved.yaml>
python -m fas.cli.predict_target --target <target> --seed <seed> --freeze <record.json>
python -m fas.cli.evaluate --experiment <id> --freeze <record.json>
```

Every command supports `--dry-run`, prints input/output hashes, refuses unexpected
roles, and writes atomically. Confirmatory commands require a valid signed freeze
record and refuse dirty or mismatched analysis code.

## 11. Evaluation plan

### 11.1 Populations

- **Risk population:** primary frames where face detection succeeds. Use this for
  error AP/AUROC, Brier/NLL, risk-coverage, AURC, and fixed-error RQ1 contrasts.
- **End-to-end population:** every original transaction, including detector failures.
  Use this for security, usability, coverage, and K=1 outcomes.

Report detector-failure rate separately for attacks and bona fide.

### 11.2 Transaction ledger

Create one row per authentication attempt before face detection:

```text
transaction_id, sample_id, dataset, subject_id, video_id, outer_target,
ground_truth, detector_status, pad_score, pad_threshold, pad_decision,
risk_score, gate_threshold, gate_action, final_k1_action,
classifier_artifact_hash, risk_artifact_hash, policy_artifact_hash
```

`transaction_id` is stable across all systems compared in a paired analysis. Missing
branch or risk values are explicit nulls after detector failure; the row itself cannot
be dropped. End-to-end metrics are computed only from this ledger and must reconcile
exactly to the pre-detection target manifest. Risk metrics use an explicit filtered
view where `detector_status=success`.

### 11.3 Classifier table

For DINOv2-Reg, OpenCLIP, calibrated heterogeneous average, and matched same-family
average, report per target and four-target macro:

- APCER, BPCER, ACER/HTER, and AUROC;
- error prevalence;
- joint correctness, double fault, recoverable errors, and realized fusion rescue;
- target threshold curves only as clearly labeled post-hoc diagnostics.

Deployment metrics use the frozen source threshold.

### 11.4 RQ1 fixed-error risk table

Score the identical final heterogeneous classifier errors with domain-OOF and matched
sample-OOF `R_DVd`, plus all required baselines. Primary endpoint:

$$
\Delta_{OOF,t,s}=AP(e_{DV},r_{DVd}^{domain})-
AP(e_{DV},r_{DVd}^{sample}).
$$

Use non-interpolated average precision with `error=1` and larger score meaning higher
risk. Also report error AUROC, AURC/excess-AURC, error prevalence, and paired deltas.

### 11.5 Selective utility table

At source-selected thresholds report:

- attack coverage and bona-fide coverage;
- covered APCER/BPCER with explicit changed denominators;
- `FA_end2end` and `BFNR_end2end`;
- attacks newly blocked, attacks newly admitted, bona-fide decisions newly rejected,
  and detector failures;
- risk-coverage curves and class-conditional curves.

Under K=1, spoof and abstain are both terminal non-accept. Aggregate coverage alone
cannot establish benefit.

### 11.6 RQ2 complete-system table

Compare DINOv2-Reg plus OpenCLIP with DINOv2-Reg plus plain DINOv2 on identical target
transactions and matched recipes. Report classifier quality, error prevalence, each
system's own risk AP, selective utility, and K=1 outcomes. Cross-system AP is
descriptive because the systems have different errors; the scientific comparison is
the paired whole-system outcome.

### 11.7 Benchmark-compatible track

In addition to the strict one-frame primary track, each dataset adapter provides a
versioned benchmark evaluation policy matching its official protocol: eligible frame
indices, frame-score aggregation into a video score, official population, required
metrics, and threshold convention. Benchmark outputs are secondary and kept separate
from the strict single-image tables. Confidence intervals and tests still cluster by
subject where possible, otherwise video; correlated frames are never replicates.

### 11.8 Statistical analysis

- Run all four outer targets and three fixed optimization seeds.
- Never select the best seed or pool seed predictions.
- Bootstrap paired differences by subject where possible, otherwise video; never by
  frame.
- Aggregate target effects with the preregistered four-target macro.
- Report point estimate, 95% interval, event counts, applicability, and pass,
  inconclusive, or evidence-against state.
- Apply claim-specific minimum effects, lower-bound rules, consistency requirements,
  and target harm tolerance frozen from source pseudo-shifts.

## 12. Execution phases and gates

| Phase | Deliverable | Exit gate |
|---|---|---|
| 0. Governance | Reconciled schemas/configs and synthetic fixtures | No pilot fields or stale claim ordering; tests pass |
| 1. Intake | Verified raw releases, canonical manifests, role manifests | License/protocol evidence, hashes, no overlap, feasible event counts |
| 2. Metrics | Metric, transaction, estimand, and bootstrap modules | Hand-computed synthetic identities pass |
| 3. Frames/features | Deterministic frame/crop manifests and frozen feature shards | Repeatability, exact joins, parity, disk budget pass |
| 4. Branches | Fold-local heads, calibrators, thresholds, prediction registry | Exclusion and one-stage calibration tests pass |
| 5. OOF | Matched domain-OOF and sample-OOF tables | Lineage, overlap, fit-budget, and fixed-prediction checks pass |
| 6. Risk/gates | Risk models, baselines, same-family system, source gates | Fixed-error and whole-system synthetic tests pass |
| 7. Freeze | Signed source-only analysis record | Config/code/count/effect hashes complete; target commands unlock |
| 8. MICO | Four targets by three seeds | Immutable transaction outputs and reproducible metrics |
| 9. Optional | SiW-M, LoRA, routing, or cue studies | Separate preregistration; no overwrite of core results |

## 13. Compute, storage, and scheduling

Use the RTX 4080 16 GB for one frozen encoder at a time. Begin with a balanced
source-only shard to measure examples/second, peak VRAM, shard size, detector cost,
and total projected storage. Set shard size and worker count from this measurement,
not from target throughput.

Expected expensive operations are frame decoding, face detection, and three frozen
feature passes. OOF repetitions train only small heads/calibrators/risk models against
cached features. Keep source and target feature namespaces separate so target
extraction cannot be mistaken for source dry-run completion.

Recommended work sequence:

1. Week 1: Phase 0 governance migration and synthetic contracts.
2. Weeks 2-3: access verification, adapters, inventory, role manifests, leakage audit.
3. Week 4: frame/crop pipeline, source shard benchmark, metrics and transaction tests.
4. Week 5: complete frozen extraction and branch fitting on source-only dry runs.
5. Week 6: OOF engine and matched-record audits.
6. Week 7: risk estimators, baselines, gate selection, same-family system.
7. Week 8: source-only dry run, event-count decisions, and signed analysis freeze.
8. Weeks 9-10: four-fold confirmatory MICO execution and locked analysis.
9. Later: optional claims only after the core result state is recorded.

Dates are planning estimates, not permission to bypass an exit gate.

## 14. Reproducibility and failure handling

Every run records Python/package lock, CUDA/cuDNN, GPU, FFmpeg, detector, backbone and
weight hashes, environment variables excluding secrets, command line, resolved config,
Git SHA, manifest hashes, and random seeds.

Hard failures include role overlap, target lineage upstream of evaluation, missing
subject/video IDs, unknown required labels, duplicate predictions, changed sample
universe between RQ1 comparators, negative affine slope, repeated calibration,
unmatched DINO anchor artifacts, and target-derived threshold selection.

Recoverable outcomes are reported rather than patched:

- insufficient false accepts makes only FARR-style claims inconclusive;
- one-class error labels invalidate ranking for that slice;
- detector failure reduces class coverage but remains in end-to-end denominators;
- weak frozen branches trigger the predefined claim reframe, not target-guided
  fine-tuning;
- optional dataset access failure removes only the corresponding optional study.

## 15. Immediate authorization

The first coding change is Phase 0 only: reconcile the provisional preregistration
scaffold with the frozen source-only contracts and make synthetic governance tests
pass. Dataset downloads may proceed administratively in parallel, but no real-data
training, target inspection, or backbone-facing code begins until Phase 0 is reviewed.