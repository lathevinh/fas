# Response to ChatGPT Research Review - Round 11

Date: 2026-09-17

## Decision

The implementation-readiness criticism is accepted. This response is intentionally
not prose-only: it adds versioned configuration, manifest tables, executable readiness
validation, monotone calibration code, and unit tests.

The repository is now **configuration-frozen but not data-ready**. Pilot inspection is
blocked until real dataset counts, role-manifest hashes, source-derived effect gates,
and owner attestation pass the strict validator. Missing values are not filled from
memory or publication-level totals.

## Accepted corrections

1. **Concrete freeze artifacts.** Core/auxiliary prompts, two immutable OpenCLIP
   candidates, preprocessing, latency measurement, seeds, evaluation semantics, and
   pilot selection now live in `configs/` as JSON-compatible YAML.
2. **Pilot identity.** MSU-MFSD is development-only. OULU-NPU, CASIA-FASD, and
   Replay-Attack form the confirmatory macro.
3. **Deterministic selection.** VLM selection uses one fixed DINOv2-Reg selection seed.
   Every candidate receives its own source calibration and source-selected threshold;
   ties use measured latency and then immutable lexical ID.
4. **Latency protocol.** Batch size, precision, warm-up, timed runs, CUDA
   synchronization, preprocessing inclusion, device, statistic, and 100 ms ceiling are
   frozen.
5. **Claim wording.** Domain and attack-family shifts are separate primary tracks.
   The dossier no longer claims simultaneous joint shift.
6. **Confirmatory lineage.** No-data-use language now refers specifically to
   confirmatory targets; the pilot's development role is explicit.
7. **Meaningful effects and hierarchy.** Rescue, heterogeneity, cross-foundation risk,
   and explicit disagreement form an ordered claim sequence. Nonzero effect/LCB gates
   must be estimated on source pseudo-shifts and frozen before confirmatory labels;
   mere positivity is prohibited.
8. **OOF-to-final validity.** Frozen risk ranking on $G_{domain}$ must report error
   AUPR, AUROC, Brier, and risk-coverage, without tuning gate parameters.
9. **Evaluation populations.** Stage-2 risk metrics condition on detector success;
   end-to-end metrics include all transactions and report class-conditional detector
   failure rates.
10. **Global dataset roles.** Each dataset must have one immutable subject/video role
    manifest reused whenever it is a source, with hashes and independent event counts.
11. **Fixed randomness and inference.** Three exact seeds and dataset-level subject
    bootstrap units are frozen. Failed runs cannot be silently replaced.
12. **Paired control.** Heterogeneous and same-family rescue consume the exact same
    cached DINOv2-Reg anchor predictions.
13. **Calibration enforcement.** `MonotoneAffineCalibrator` parameterizes
    $a=softplus(\theta)+\epsilon$. Tests cover strict ordering, finite outputs, invalid
    inputs, and equal-domain natural-prevalence BCE.

## Qualified points

### Data readiness is not claimed

`manifests/dataset_summary.csv` and `manifests/split_summary.csv` contain explicit
`not_audited` rows because the restricted datasets are not present in this repository.
The strict validator fails on these rows. Counts and hashes must come from official
local metadata, not guessed values.

### Pilot-history attestation remains external

The assistant cannot know whether pilot labels were previously inspected. The config
therefore records `owner_attestation_pending`; strict readiness requires
`attested_not_inspected`. If labels were inspected, the eventual paper must call the
choice retrospective rather than preregistered.

### Effect sizes cannot be invented

Numerical $\delta_H$, $\delta_{CF}$, $\delta_{dis}$, harm tolerance, and the
OOF-to-final sanity threshold remain pending source-pseudo-shift estimation. The
validator blocks readiness until they are frozen. Choosing arbitrary numbers now would
look precise but would not be scientifically grounded.

### Bootstrap units are provisional metadata assumptions

Subject is frozen as the intended strongest clustering unit for all five datasets.
Stage 0 must verify official subject identifiers. If a dataset cannot support that
unit, the correction must occur before pilot inspection and be recorded as a config
version change, never selected by confidence-interval width.

## Not adopted

No joint unseen-domain-plus-unseen-attack protocol is added. The unsupported
"simultaneous" wording was removed instead. No architecture, loss family, or extra
endpoint was introduced.

## Executable checks

```bash
python -m unittest discover -s tests -v
python scripts/validate_preregistration.py --allow-incomplete-counts
python scripts/validate_preregistration.py
```

The first two commands must pass now. The strict command must fail until the data audit,
effect thresholds, and owner attestation are complete. Only a strict
`PREREGISTRATION READY` permits pilot-label inspection.

## Next milestone

Obtain official dataset metadata, generate immutable subject/video role manifests,
populate independent-event counts and hashes, evaluate split feasibility, derive the
source-only nonzero gates, and rerun strict validation. The next review should inspect
those generated artifacts or Stage-1 predictions, not propose another architecture.
