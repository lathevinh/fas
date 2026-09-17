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

Define exclusions at the declared semantic level
`family -> instrument -> subtype`. Holding out an entire family removes all matching
prompts from the auxiliary attack bank; holding out only a subtype may retain a generic
auxiliary family prompt. The immutable core PAD bank and its normalization never
change. Any allowed attack-specific open-vocabulary prompt produces a separate
auxiliary similarity score rather than changing the core PAD probability.

Compare a preregistered fixed semantic prompt bank with source-tuned template/weight
selection. The fixed bank is primary for unseen-attack transfer; source tuning is
reported separately to expose any known-source accuracy versus unseen-transfer trade-off.

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
5. For the strict single-image primary result, use the middle valid frame by a
  label-independent temporal rule; evaluate fixed 25%, 50%, and 75% positions as
  sensitivity analysis.
6. Perform image-level inference; aggregate scores only for separately reported
   protocol-compatible video metrics.
7. Hash manifests and save the preprocessing version with every run.

Report two evaluation tracks. The benchmark-compatible track follows each dataset's
official frame/video aggregation. The strict single-image track uses one deterministic
frame per video as its primary result; multi-frame sensitivity analyses cluster all
confidence intervals and tests by video or subject. Never treat correlated frames as
independent statistical units.

## Face crops

- Detect with one fixed detector such as SCRFD or RetinaFace.
- Align lightly using eyes; do not warp strongly.
- Retain a context margin of roughly 1.25-1.4 times the face box.
- Preserve screen, paper, and mask boundaries where possible.
- Record detector failures and evaluate them separately rather than silently dropping them.
- Map detector failure deterministically to terminal `abstain/non-accept` and include
  it in class coverage and end-to-end transaction metrics.
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

For deployment tables, apply the frozen source threshold to the target and report
target APCER/BPCER at that threshold. Report target-derived ROC points such as BPCER at
target APCER=1% in a separate post-hoc diagnostic block. Compare thresholds selected
from pooled sources with thresholds satisfying the APCER constraint on every source
domain.

Report empirical APCER with binomial confidence intervals. A statistically
constrained source policy requires $UCB_{95\%}(APCER_d)\leq\alpha$ for every source
domain. If attack counts cannot support that bound, label the operating point a
nominal empirical target rather than a certified security level.

Within each three-source training set, create out-of-fold reliability records by
holding out one source dataset at a time. Predictions on a held-out source must come
from branches that did not train on that source. Fit the final reliability calibrator
only after concatenating these out-of-fold records.

Inside each remaining-source fold, keep model fitting, prompt selection, and branch
probability calibration disjoint from the held-out OOF evaluation domain.

Compare this domain-OOF construction with sample-OOF records made inside each source
domain. Sample-OOF is an ablation, not a substitute for domain-OOF in the main claim.

Normalize each OOF risk feature using statistics from its source-side fitting and
calibration partition. Audit fold/domain identifiability from the normalized features;
report feature-removal sensitivity if domain prediction remains strong.

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
- prediction-error AUROC and AUPR;
- optional shift/OOD AUROC and AUPR under a separately defined shift target;
- prediction-error AUPR as the primary failure-detection endpoint;
- error prevalence $\pi_{err}$ and normalized
  $AUPR_{norm}=(AUPR-\pi_{err})/(1-\pi_{err})$ as context; primary comparisons use
  paired within-target AUPR differences and macro-average target deltas;
- excess-AURC as the primary selective-classification endpoint, with AURC and
  risk-coverage curves secondary;
- Brier score, failure-risk NLL, and reliability diagrams when interpreting
  $r_{err}$ as a probability;
- attack coverage $Coverage_A=N_{attack,decided}/N_{attack,total}$ and bona-fide
  coverage $Coverage_B=N_{bona,decided}/N_{bona,total}$;
- covered-sample $APCER_{covered}=N_{attack,accepted\ live}/N_{attack,decided}$ and
  the analogous $BPCER_{covered}$, always labeled with their changed denominators;
- end-to-end false acceptance
  $FA_{end2end}=N_{attack,accepted\ live}/N_{attack,total}$;
- secure recall and VLM invocation rate at those fixed operating points;
- bootstrap confidence intervals by subject/video;
- per-target results and macro aggregation across target domains;
- mean and standard deviation over at least three seeds as optimization variance,
  never as independent scientific replicates.

The primary experimental retry policy permits one image attempt per authentication
transaction ($K=1$), so `abstain` is recorded as a terminal non-accept outcome. Any
multi-attempt analysis must specify rate limiting, maximum attempts, dependence across
attempts, and transaction-level attack success; it is secondary to the single-image
claim.
