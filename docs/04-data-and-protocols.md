# Datasets and Protocols

## Dataset roles

| Dataset | Intended use | Useful labels/properties | Restrictions or caveats |
|---|---|---|---|
| CelebA-Spoof | Optional extra-data pretraining/analysis | 625,537 images, 10,177 subjects, spoof type, illumination, environment | Excluded from strict MICO; non-commercial research only |
| OULU-NPU | MICO and mobile domain evaluation | Print/replay, protocols for environment/device variation | Preserve official protocols |
| CASIA-FASD | MICO source/target | Print, cut-photo, replay and quality variation | Verify redistribution/access terms |
| Replay-Attack | MICO source/target | Print/replay and controlled/adverse settings | Preserve official train/dev/test split |
| MSU-MFSD | MICO source/target | Print/replay across capture devices | Small dataset; high leakage risk |
| SiW-M | Main unseen-attack evaluation | 13 diverse attack types and zero-shot protocols | Access and current official protocol must be verified |
| 3DMAD/HiFiMask | External mask transfer | 3D mask evidence | Sensor/modality and access may not match RGB-only scope |
| UniAttackData | Later unified physical/digital extension | Diverse physical and digital attacks | Out of first-paper scope unless physical subset is cleanly defined |

Dataset facts and licenses must be rechecked against downloaded documentation.
Only CelebA-Spoof details above have been directly checked against its public paper
and repository during this planning pass.

## Data available to each model

### Strict MICO track

For each target among OULU-NPU, CASIA-FASD, Replay-Attack, and MSU-MFSD:

- DINO uses generic pretrained weights plus labels from the other three source datasets;
- the VLM uses its generic pretrained weights, source images/labels for prompt and
  temperature selection, and no target samples;
- the reliability calibrator uses only out-of-fold predictions generated within the
  three source datasets;
- CelebA-Spoof and SiW-M are not additional labeled training data.

This is the main comparison track. A separate `+CelebA-Spoof` experiment may measure
the value of extra FAS supervision, but it must not be compared as if training data
were equal.

### Unseen-attack track

Use the official SiW-M split/protocol. The held-out attack family cannot participate
in branch tuning, prompt selection, reliability calibration, or threshold selection.

Report two distinct downstream-unseen settings:

- **downstream-unseen PAI:** the attack instrument/family is absent from downstream FAS
  image supervision and its attack-specific text description is excluded;
- **open-vocabulary zero-shot PAI:** the attack is absent from downstream FAS image
  supervision, but its attack-specific text description is allowed in the prompt bank.

Do not pool these into one unknown score because they test different abilities.
Neither setting proves that the attack was absent from generic foundation-model
pretraining; foundation-model pretraining exposure at web scale is uncontrolled.

## Unified metadata manifest

Each sample should have a non-sensitive metadata row:

```json
{
  "sample_id": "dataset/subject/video/frame",
  "dataset": "OULU-NPU",
  "subject_id": "...",
  "video_id": "...",
  "frame_path": "...",
  "binary_label": "attack",
  "attack_family": "replay",
  "instrument": "phone_display",
  "material": "display",
  "environment": "indoor",
  "sensor": "...",
  "label_confidence": 1.0,
  "label_source": "official"
}
```

Unknown values remain `unknown`; they must not be guessed from coarse labels.

## Leakage-safe processing

1. Parse official protocol files before extracting frames.
2. Verify that subject and video identifiers do not cross splits.
3. Extract frames after split assignment.
4. During training, sample at most 1-3 random frames per video per epoch.
5. During evaluation, use a deterministic frame index list.
6. Perform image-level inference; aggregate scores only for separately reported
   protocol-compatible video metrics.
7. Hash manifests and save the preprocessing version with every run.

## Face crops

- Detect with one fixed detector such as SCRFD or RetinaFace.
- Align lightly using eyes; do not warp strongly.
- Retain a context margin of roughly 1.25-1.4 times the face box.
- Preserve screen, paper, and mask boundaries where possible.
- Record detector failures and evaluate them separately rather than silently dropping them.
- Derive face and context views from the same RGB input.

Each backbone receives its own resize and normalization. Geometry is shared, pixel
normalization is not.

## Sampling

Use a hierarchical sampler:

1. sample dataset approximately uniformly;
2. sample bona fide/attack approximately uniformly;
3. sample attack family approximately uniformly;
4. sample video, then a frame.

This prevents CelebA-Spoof and long videos from dominating optimization.

## Augmentation policy

### Label-preserving nuisance transforms

- horizontal flip;
- mild crop/scale and pose-preserving geometry;
- mild brightness, contrast, gamma, and white-balance changes;
- mild sensor noise and compression.

### Optional controlled forensic interventions

- localized halftone or print degradation;
- calibrated moire/pixel-grid patterns;
- display-like color banding or reflection;
- localized boundary or flatness proxies where physically defensible.

Each intervention stores its spatial mask and affected concept. Synthetic data
supervise only the intervention that was actually generated; they are not treated
as complete replicas of real attacks. These interventions are deferred until the
minimum disagreement study succeeds.

## Optional cue annotation strategy

Priority order:

1. official labels;
2. deterministic high-precision mapping from attack instrument;
3. VLM/MLLM pseudo-label with confidence;
4. human verification.

If the evidence extension proceeds, audit 1,000-2,000 balanced samples across
datasets and attacks. Report agreement and per-concept precision. Low-precision
concepts are removed or treated as latent. The core disagreement experiment does
not require cue-level pseudo-labels.

## Evaluation protocols

### MICO cross-domain

For OULU-NPU, CASIA-FASD, Replay-Attack, and MSU-MFSD, train on three and test on
the fourth. Hyperparameters and thresholds use source-domain validation only.

Within each three-source training set, create out-of-fold reliability records by
holding out one source dataset at a time. Predictions on a held-out source must come
from branches that did not train on that source. Fit the final reliability calibrator
only after concatenating these out-of-fold records.

Inside each remaining-source fold, keep model fitting, prompt selection, and branch
probability calibration disjoint from the held-out OOF evaluation domain.

Compare this domain-OOF construction with sample-OOF records made inside each source
domain. Sample-OOF is an ablation, not a substitute for domain-OOF in the main claim.

### Leave-one-attack-out

Use SiW-M official zero-shot protocols where obtainable. Exclude one attack type
from training and evaluate it as unknown.

### External mask transfer

Train without the target mask dataset and test transfer. Clearly distinguish RGB
frames from depth/IR and never use unavailable modalities.

### Metrics

- APCER, BPCER, ACER;
- HTER, EER, ROC-AUC;
- BPCER at fixed APCER where protocol permits;
- ECE and NLL;
- error/OOD AUROC and AUPR;
- selective risk versus coverage;
- selective risk at fixed APCER and fixed BPCER;
- secure recall and VLM invocation rate at those fixed operating points;
- bootstrap confidence intervals by subject/video;
- mean and standard deviation over at least three seeds.
