# Datasets and Protocols

## Dataset roles

| Dataset | Intended use | Useful labels/properties | Restrictions or caveats |
|---|---|---|---|
| CelebA-Spoof | Large-scale PAD/concept pretraining | 625,537 images, 10,177 subjects, spoof type, illumination, environment | Non-commercial research; image-style source differs from video PAD sets |
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

### Controlled forensic interventions

- localized halftone or print degradation;
- calibrated moire/pixel-grid patterns;
- display-like color banding or reflection;
- localized boundary or flatness proxies where physically defensible.

Each intervention stores its spatial mask and affected concept. Synthetic data
supervise only the intervention that was actually generated; they are not treated
as complete replicas of real attacks.

## Annotation strategy

Priority order:

1. official labels;
2. deterministic high-precision mapping from attack instrument;
3. VLM/MLLM pseudo-label with confidence;
4. human verification.

Audit 1,000-2,000 balanced samples across datasets and attacks. Report agreement
and per-concept precision. Low-precision concepts are removed or treated as latent.

## Evaluation protocols

### MICO cross-domain

For OULU-NPU, CASIA-FASD, Replay-Attack, and MSU-MFSD, train on three and test on
the fourth. Hyperparameters and thresholds use source-domain validation only.

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
- bootstrap confidence intervals by subject/video;
- mean and standard deviation over at least three seeds.
