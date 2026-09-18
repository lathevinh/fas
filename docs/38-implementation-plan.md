# Dependency-Ordered Implementation Plan

Date: 2026-09-18

## Authority and boundary

This plan implements the methodology frozen in Rounds 14-16. Normative priority is:

1. `docs/00-project-charter.md` through `docs/06-risks-and-decisions.md`;
2. `docs/35-review-response-round14.md`;
3. `docs/36-chatgpt-review-round15.md` and
   `docs/37-review-response-round15.md`;
4. `docs/40-paper-skeleton.md` and `docs/41-review-response-round16.md`;
5. this dependency-ordered implementation plan and the execution-level data-to-
  experiment plan in `docs/42-data-to-experiment-implementation-plan.md`;
6. provisional configs and code only after reconciliation.

For outer fold $T$, no phase may use $T$ to tune a model, threshold, feature, effect
rule, or analysis choice. Synthetic fixtures and source-only pseudo-shifts are the only
debugging inputs before the global analysis freeze. All rule-generation logic freezes
before the first outer-target result; fold-specific numeric thresholds then follow the
same frozen algorithm. Code completion is not evidence for a scientific claim.

## Current scaffold

Reusable pieces:

- `src/fas/calibration.py`: monotone affine transform and equal-domain losses;
- `src/fas/preregistration.py`: hashing, staged validation, manifest reconciliation;
- `scripts/validate_preregistration.py` and `scripts/write_freeze_record.py`;
- calibration and preregistration unit tests.

Superseded contracts to replace, not preserve:

- labeled-pilot stages and `pilot_selection_v1.yaml`;
- a two-candidate primary VLM requirement;
- `claim_sequence` beginning with fusion rescue;
- routing thresholds as core locked-evaluation requirements;
- one global $N_{FA}$ rule for unrelated endpoints;
- a same-family row without risk estimation or abstention.

No data adapters, backbone wrappers, feature store, branch trainer, OOF engine, risk
pipeline, biometric metrics, bootstrap analysis, or experiment orchestrator currently
exists.

## Artifact model

Every generated artifact receives a schema version, producing commit, config hashes,
input manifest hashes, fold/seed, and upstream artifact hashes. Artifacts are immutable
once consumed downstream.

| Artifact | Minimum identity fields |
|---|---|
| Dataset manifest | dataset, subject, video, frame, label, official split, role, source record |
| Feature shard | sample IDs, backbone/weight hash, preprocessing hash, view, dtype, tensor shape |
| Branch model | target exclusion, fit domains, inner split, seed, feature hash, checkpoint rule |
| Calibrator | branch model hash, calibration partition, domains, class counts, objective |
| Prediction table | sample IDs, logits, calibrated scores, decision threshold, lineage hashes |
| OOF risk table | OOF scheme, held-out unit, fit sizes, error prevalence, features, labels |
| Risk model | feature variant, OOF scheme, regularization, weighting, training-table hash |
| Gate policy | risk-model hash, source holdout, objective, threshold, achieved source metrics |
| Analysis record | estimand ID, comparator IDs, resampling unit, effect rule, input hashes |

Private paths and biometric data never enter Git. Public summaries contain counts and
hashes only.

## Phase 0: reconcile governance contracts

Goal: make validation describe the frozen method before adding model code.

Planned changes:

- replace pilot-oriented config with one fixed primary-model config;
- split evaluation config into typed claim specifications for RQ1, RQ2, classifier
  benefit, disagreement, FARR, and optional routing;
- encode OpenCLIP `ViT-B-16` / `laion2b_s34b_b88k`, native 224 preprocessing, fixed
  1.30 context crop, DINOv2-Reg, and CLS-plus-mean-patch pooling;
- rename readiness stages to `schema`, `data-audit`, `source-dry-run`,
  `analysis-freeze`, and `locked-evaluation`;
- remove target/pilot label attestations and add explicit all-four-target exclusion;
- update freeze hashing to include analysis specifications and exclude superseded files.

Tests:

- reject more than one primary VLM;
- reject learned primary pooling;
- reject pilot-domain fields;
- reject global claim ordering;
- reject missing claim-specific endpoint/effect/event rules;
- reject optional routing as a core readiness dependency;
- accept a complete synthetic frozen-method configuration.

Exit gate: schema tests pass and every old scaffold mismatch has an explicit migration
or deletion decision. No real dataset is required.

## Phase 1: environment and dataset audit

Goal: establish reproducible inputs before feature extraction.

Modules and commands to add:

- package/lock configuration with exact Python, PyTorch, OpenCLIP, DINO, detector, and
  metric-library versions;
- dataset adapters that parse official metadata without changing official roles;
- deterministic frame selector and face-crop geometry module;
- manifest CLI that writes private evidence plus public count/hash summaries;
- leakage audit CLI for subject/video overlap, duplicate samples, role overlap, class
  feasibility, and missing identifiers.

Required audit outputs per dataset:

- license/access status and official protocol source;
- subject, video, class, attack-family, and detector-failure counts;
- counts available for train, branch calibration, $G_{domain}$ or $G_{attack}$, and
  optional routing validation;
- lowest estimable security operating point based on independent attack events.

Exit gate: all four MCIO datasets have verified subject/video lineage and feasible
source roles, or the operational split is simplified in documentation before any target
result. SiW-M failure removes only the attack-shift claim.

## Phase 2: metric and action-semantics contracts

Goal: test analysis mathematics before training any backbone head.

Planned modules:

- `metrics.py`: APCER, BPCER/BFNR, ACER, non-interpolated AP, AUROC, Brier, NLL, and
  risk-coverage/AURC;
- `transactions.py`: detector failure, live/spoof decision, abstention, K=1 terminal
  action, `FA_end2end`, and `BFNR_end2end`;
- `resampling.py`: paired subject/video cluster bootstrap and deterministic seed
  pairing;
- `estimands.py`: typed RQ1/RQ2/classifier/disagreement/FARR estimand definitions.

Synthetic tests must prove:

- AP uses error=1 and higher-risk polarity;
- spoof and abstain both map to terminal non-accept under K=1;
- gating a fixed classifier cannot reduce BFNR while rejecting additional live
  decisions;
- detector failures stay in end-to-end denominators but outside risk-feature metrics;
- zero false accepts invalidate FARR only, not estimable error AP;
- one-class error labels invalidate ranking endpoints only;
- paired deltas preserve transaction IDs and cluster units;
- target-derived threshold matching is impossible through the analysis API.

Exit gate: hand-computed fixtures match every metric and transaction identity.

## Phase 3: frozen feature extraction

Goal: produce reusable, lineage-safe features without fitting on target labels.

Planned components:

- fixed face detector and deterministic frame/crop pipeline;
- DINOv2-Reg extractor returning CLS and mean patch vectors;
- plain DINOv2 extractor for the same-family control;
- OpenCLIP image/text wrapper with immutable core prompts and mean-cosine logits;
- sharded feature store with checksums, resumability, shape validation, and sample-ID
  joins.

Rules:

- run encoders sequentially on the RTX 4080;
- use mixed precision only where numerical parity tests permit;
- never cache learned attention-pooled vectors for the primary system;
- keep branch-native resizing/normalization while sharing crop geometry;
- benchmark storage throughput and disk footprint on a small source-only shard before
  full extraction.

Exit gate: repeated extraction is deterministic within tolerance, feature/sample joins
are exact, checkpoint and preprocessing hashes are recorded, and no labels enter the
encoder cache key.

## Phase 4: branch fitting and source calibration

Goal: create fold-local branch predictions with auditable lineage.

Planned components:

- small DINO PAD head trainer with deterministic subject-disjoint inner validation;
- fixed OpenCLIP prompt logit path with no primary prompt/checkpoint selection;
- supervised OpenCLIP visual-head diagnostic;
- monotone affine calibrator fitting with class-balanced within-domain and
  equal-domain loss;
- source operating-threshold selector with fixed score polarity;
- prediction registry keyed by target exclusion, fold, seed, and branch.

Tests:

- held-out OOF domain cannot appear in branch fit, checkpoint selection, calibration,
  or threshold selection;
- target domain cannot appear anywhere upstream;
- affine slope remains positive and calibration occurs exactly once;
- the identical DINOv2-Reg anchor prediction artifact is reused for heterogeneous and
  same-family comparisons;
- source threshold selection handles ties and infeasible APCER deterministically.

Exit gate: synthetic three-source rotations produce lineage-valid branch/calibrator
artifacts and deterministic predictions.

## Phase 5: matched OOF record generation

Goal: build the two RQ1 supervision tables fairly.

Implement one OOF engine with two strategies:

- `domain_oof`: hold out one complete source domain;
- `sample_oof`: hold out subject-disjoint folds within each source domain.

Both strategies share source candidate universe after $G_{domain}$ removal, frame/video
unit, quality features, source-macro weighting, risk feature code, and optimization
budget. Each table records effective branch-fit sizes, OOF count, domain/class/error
prevalence, and every upstream hash.

Add an optional budget-matched sensitivity when effective training sizes differ beyond
a preregistered source-derived tolerance. Never downsample errors to equalize natural
prevalence.

Exit gate: negative tests catch subject/video overlap, holdout reuse, missing folds,
duplicate predictions, changed final target predictions, feature drift, and unequal
budgets not disclosed by metadata.

## Phase 6: risk estimators and source-selected gates

Goal: train all fixed-classifier comparators on identical labels and all whole-system
comparators with matched recipes.

Implement:

- quality-only, DINO-only, VLM-only, $R_{DV}$, primary $R_{DVd}$, and operational
  $R_{DVdm}$ logistic estimators;
- capacity-matched nonlinear probability-only comparator and with-disagreement variant;
- fused MSP/entropy, policy margin, and DINO Mahalanobis baselines;
- domain-OOF and matched sample-OOF versions of primary $R_{DVd}$;
- a matched domain-OOF risk estimator and gate for DINOv2-Reg plus plain DINOv2;
- source-only gate policy selection on permanent $G_{domain}$.

All fixed-$g_{DV}$ risk-estimator comparisons use identical `e_DV`. Whole-system
comparisons disclose their different classifiers, error prevalence, and achieved class
coverage.

Exit gate: the RQ1 synthetic test changes only OOF strategy; the RQ2 test compares
complete systems on identical transactions; no API reports cross-system raw AP as
estimator-quality evidence.

## Phase 7: source-only analysis freeze

Goal: convert source pseudo-shift information into immutable claim rules.

For each claim freeze:

- estimand and primary endpoint;
- required comparator conjunction;
- $\delta_{min}$ and whether pass requires point gain $\geq\delta_{min}$ plus
  LCB $>0$;
- target harm tolerance;
- event-count applicability;
- bootstrap unit/repetitions and seed aggregation;
- inconclusive versus evidence-against outcomes.

Primary contracts:

- RQ1: paired four-target macro of $\Delta_{OOF}$ on fixed `e_DV`;
- RQ2: whole-system selective/end-to-end advantage over the matched same-family
  selective system;
- classifier benefit: net APCER plus BPCER/BFNR harm, with FARR descriptive;
- disagreement: $R_{DVd}$ versus capacity-matched nonlinear probability-only risk;
- routing: absent unless optional deployment work is explicitly activated.

Exit gate: signed freeze record hashes configs, source counts, effect rules, code commit,
and analysis specification. Locked-evaluation commands refuse to run without this record.

## Phase 8: pre-specified four-fold MCIO execution

Goal: evaluate four strict outer-domain-held-out folds under one frozen procedure.

Execution order per target and seed:

1. verify target exclusion and artifact hashes;
2. fit source branches, calibrators, thresholds, OOF risk models, and source gates;
3. generate target predictions without adapting any component;
4. write immutable per-transaction results;
5. compute the preregistered estimands and paired cluster bootstrap;
6. publish per-target results before computing the four-target macro.

Guardrails:

- no best-seed selection or pooled seed prediction;
- no target threshold switching or class-specific target matching;
- no feature/comparator changes after the first target;
- false-accept event insufficiency affects only relevant endpoints;
- inconclusive, evidence against, and pass remain distinct states.

Exit gate: reproducibility rerun from manifests and hashes yields identical decisions
and metrics within declared numerical tolerance.

## Phase 9: optional claims

Run only after the core RQ1 analysis is complete and only with an explicit dependency:

- SiW-M attack-OOF for an attack-shift claim;
- conditional routing for a compute-saving claim;
- learned attention pooling, alternative VLM/crop, LoRA, or distillation as secondary
  robustness/representation studies;
- evidence maps or cue analysis only under a separate preregistration.

Optional failure cannot invalidate an already evaluated core claim, and optional
success cannot rescue a failed core estimand.

## Pull-request sequence

Keep implementation reviews small and executable:

1. governance/config migration;
2. metrics and K=1 transaction tests;
3. manifests and leakage audit;
4. feature extractors and cache contracts;
5. branch fitting/calibration/thresholds;
6. OOF engine and lineage tests;
7. risk estimators and same-family selective system;
8. analysis freeze and bootstrap;
9. source-only dry run;
10. locked-evaluation runner.

Each change must pass focused unit tests first, then the full synthetic suite. Real-data
smoke tests use source roles only until the analysis freeze is signed.

## Immediate next action

Implement Phase 0 only: replace superseded pilot/candidate/claim-sequence contracts and
write failing synthetic tests for the frozen configuration. Do not begin backbone or
dataset-facing code until that migration is reviewed and passes.
