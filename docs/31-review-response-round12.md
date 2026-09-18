# Response to Review Round 12 - Executable Readiness

Date: 2026-09-18

## Decision

The review is accepted. Its negative probes exposed real defects in the Round-11
validator, and the phrase `configuration-frozen` was too strong. This response changes
code, tests, configs, and protocol semantics; it does not claim Stage 0 or Stage 1 is
complete.

The current truthful state is:

```text
schema ready
!= data ready
!= pre-pilot ready
!= confirmatory ready
```

## Fixed findings

### F1 - Evidence-backed staged validation

The boolean readiness mode is replaced by four explicit stages:

1. `schema`: typed config structure is valid;
2. `data`: required datasets, typed integer counts, private evidence files, hashes,
   role applicability, count reconciliation, and subject-role disjointness pass;
3. `pre-pilot`: owner attestation, exact model/environment pins, source-anchor
   registry, and an artifact-hash freeze record also pass;
4. `confirmatory`: positive source-derived effects, continuation/routing gates, and an
   executable OOF-validity threshold also pass.

`write_freeze_record.py` refuses to write a record before the data stage passes, and a
record is invalidated when a tracked config or summary changes. The validator now
rejects the review's empty-config, fake-count/hash, and frozen-null-effect probes.
Synthetic tests also exercise one valid reconciled evidence set and a subject-role
overlap failure.

### F2 - Family-unseen prompt semantics

The family-specific core string was removed. Core spoof prompts are generic; print,
replay/display, and mask names occur only in the auxiliary bank. Auxiliary prompts do
not alter primary binary PAD probability or primary risk. Consequently, the two
unseen-attack settings have identical primary binary predictions and differ only on
explicitly labeled auxiliary concept endpoints unless a future auxiliary-conditioned
policy is separately preregistered.

### F3 - Selection recipe and pin blockers

`source_recipe_v1.yaml` now freezes the DINO representation/head recipe, optimizer,
checkpoint rule, separate branch/risk objectives, source threshold rule, tie handling,
latency scope, and no-candidate fallback. Resolution is explicitly sourced from
`preprocessing_v1.yaml`.

Candidate configs now contain fields for library revisions and weight digests;
preprocessing contains the detector-weight digest; `environment_v1.yaml` represents
the model-stack lock. These are intentionally pending rather than fabricated.
Pre-pilot validation requires exact package pins, lockfile/hash, every VLM weight hash,
detector hash, and a source-trained anchor registry.

### F4 - Global pilot estimand

The project chooses the transparent test-partition-unseen estimand. OULU/CASIA/Replay
train/dev partitions may influence global candidate selection as sources in the
MSU-MFSD pilot fold. Their official evaluation partitions remain untouched. The dossier
no longer calls each entire confirmatory domain untouched or claims strict
outer-domain-unseen candidate selection.

### F5 - Timeline separation

Pending empirical thresholds no longer block schema, data audit, or source-only work.
They are required only at confirmatory readiness. Pilot inspection requires the data,
model-pin, anchor, attestation, and freeze-record evidence available before that event.

### F6 - Security language

The primary source APCER rule is now explicitly a nominal empirical constraint.
Certified language requires a disjoint certification set or a tested selection-aware
simultaneous procedure. Pointwise intervals after adaptive threshold search are not
presented as a joint guarantee.

### F7 - Calibration objectives and input validation

Risk fitting retains natural error prevalence within each pseudo-domain. Branch
calibration now has a separate class-balanced-within-domain, equal-domain BCE
primitive. Both reject nonfinite values and probabilities outside $[0,1]$; one-class
branch-calibration domains fail explicitly. The original out-of-range probe is now a
unit test.

### F8 - Confirmatory inference semantics

The config freezes 2,000 paired cluster-bootstrap resamples, subject pairing across
seeds, comparator recomputation inside each $\Delta_{CF}$ resample, and
`inconclusive` handling for zero false accepts, one-class risk labels, or
$N_{FA}<N_{min}$. Target-dependent operating-point switching is prohibited. Numerical
gates remain pending source pseudo-shifts and cannot pass confirmatory validation as
null values.

## Qualified or still open

- The monotone transform and two loss objectives are implemented, but a fitted
  serialization path with the declared L-BFGS solver is not. It remains a Stage-1
  blocker rather than being represented as complete.
- Exact package revisions and model/detector weight hashes are not known in this
  environment. They remain typed pre-pilot blockers.
- No restricted datasets are present, so real metadata parsing, split feasibility,
  latency, fitted anchors, and prediction caches cannot be produced in this commit.
- The validator reconciles non-sensitive summaries against ignored per-video metadata
  and role evidence. It does not claim official protocol correctness merely because
  internal arithmetic passes; `metadata_source` and subsequent dataset-specific
  parsers remain necessary.

## Verification

```bash
python -m unittest discover -s tests -v
python scripts/validate_preregistration.py --stage schema
python scripts/validate_preregistration.py --stage data
```

The tests and schema stage pass. The data stage must fail on the current repository
because all real datasets remain `not_audited` and private evidence files are absent.
That failure is the intended result.

## Next milestone

Implement dataset-specific official metadata parsers and deterministic role generation,
then populate the private evidence contract documented in `manifests/README.md`. After
data-stage validation passes, pin the model environment and bytes, implement the
calibration fitter and Stage-1 synthetic/source smoke pipeline, generate the anchor
registry, and only then attempt pre-pilot readiness.
