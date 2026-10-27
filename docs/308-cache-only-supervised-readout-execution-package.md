# 308 - Cache-only supervised PAD readout: executable source-development package

Date: 2026-10-27

Basis: [recommendations307](307-recommendations-improving-pad-classification-from-cached-features.md)
and [review306](306-review-doc305-source-geometry-ablation-and-ci-failure.md).

Status: software implementation and cache-only preflight; **not scientific fitting authorization**.

## Decision and concrete question

Keep the accepted original-geometry299 cache, permanent roles and failure
population. Compare a supervised OpenCLIP image-feature head against the fixed
zero-shot diagnostic and fair, source-selected DINO readouts. Preserve the old
DINO-Reg and equal two-DINO systems as visible anchors.

The primary question is whether supervised readout improves **held-out source
macro AUROC** over the zero-shot CLIP branch. The secondary comparisons are
against selected DINO-Reg and selected equal two-DINO. These are exploratory
source-development contrasts, not revised RQ1/RQ2 verdicts or unseen-target
confirmation. None of the four observed datasets becomes untouched by calling
it an outer exclusion in this study.

Implementation:

- [configuration](../configs/readout308_v1.yaml);
- [readout selection/scoring/metrics](../src/fas/readout_study.py);
- [preflight, approval, supervisor and saved-output verifier](../scripts/run_readout308.py);
- [synthetic regression tests](../tests/test_readout308.py);
- [sealed aggregate plan](../results/phase1/readout308-plan-v1.json).

## 1. Inputs and immutable boundaries

The original source-use manifest contains **6,882 eligible originals**:
**6,855 usable feature rows and 27 terminal technical failures**. Null-role
SiW official tests and the five adopted SiW exclusions remain ineligible.
Existing OULU/CASIA/MSU official-test members already assigned source roles
remain in those roles; this is not an official-train-only study.

Use only the original299 cache union:

| Branch | Ordered feature matrix | Input representation |
|---|---:|---|
| DINO-Reg | 6855 x 1536 | Original concatenated CLS and mean patch tokens |
| Plain DINO | 6855 x 1536 | Same original pooling contract |
| OpenCLIP | 6855 x 512 | Original normalized image embeddings |

The loader verifies the manifest,297/299 input/extraction/worker receipts,
sample order, crop/checkpoint/transform/runtime keys, every shard SHA256,
finite FP32 dimensions, normalized CLIP embeddings and the original cached
text embeddings. It recomputes the original cache keys using the existing
loader's helper. The plan additionally records the ordered feature-byte
hashes and all48 original fitted-context hashes.

No G2 feature cache, raw image/frame/crop decoding, encoder checkpoint loading,
image/text forward, download, target prediction file or target label table is
an input to the new controller. Loading the shared source feature union does
not authorize predicting the excluded domain in a particular context.

No canonical evidence, role assignment, old result, model, freeze or bound
historical config is overwritten.

## 2. Equal small candidate budgets

All three branches receive the same four declared readout candidates:

| Order | Candidate | Feature transform | Learning rate | Weight decay |
|---:|---|---|---:|---:|
| 0 | Exact old anchor | Raw cached vector | .001 | .05 |
| 1 | Unit-L2 | Deterministic whole-vector L2 normalization | .001 | .05 |
| 2 | Higher learning rate | Raw cached vector | .01 | .05 |
| 3 | Lower decay | Raw cached vector | .001 | .005 |

This is a four-point, one-factor perturbation set, **not** a Cartesian search
over every combination. L2 normalization uses only the individual vector;
there is no learned scaling or train/evaluation population normalization.
CLIP's cached embeddings are already approximately unit norm, so its L2
candidate is expected to be near-redundant, not a new representation.

Every candidate uses the inherited FP64 full-batch AdamW head, source/class
balanced BCE,200 epochs, bias excluded from decay, seeded initialization,
earliest minimum inner-validation BCE checkpoint and no post-selection refit.
Across candidates, choose minimum equal-source/class-balanced inner-validation
BCE; exact ties use the table order above. Each branch is selected separately.

The two DINO raw-anchor heads are reused from the exact original saved context
after hash/split/history/validation-objective reconstruction. CLIP has no
historical supervised anchor, so all four of its heads are fitted. Reuse saves
compute without removing either DINO candidate from selection.

Many old heads selected epoch200, but that is not proof of undertraining or
convergence. This package does not lengthen training. Full validation histories,
selected epochs and candidate selections are retained; endpoint selections
must remain visible when reporting the new results.

## 3. Nested source-only selection and calibration

Retain all12 original exclusion/seed contexts: four outer exclusions crossed
with seeds20260917,20260923,20261001.

Within each context use four original partitions:

1. Three **domain-OOF** partitions. Completely exclude the pseudo-target source
   from fitting, epoch/candidate selection, calibration and threshold choice.
   Evaluate its successful `train` and `branch_calibration` rows only.
2. One **final** source fit. Fit/select/calibrate on the remaining three
   sources' permitted roles; evaluate only their `g_domain` rows.

The inherited partition builder defines the final split's `evaluation` field
as empty. The new controller explicitly joins its held-out `g_domain` rows;
it does not mistake that empty field for an empty evaluation population.

Use inherited group/frame-safe inner validation: fixed fold0 of five
source/class-signature group folds within allowed `train`; other folds fit
the heads. Candidate and epoch selection happen entirely inside this inner
validation. Group identities and exact selected-frame content may not cross
fitting/validation/calibration/evaluation boundaries; the final `g_domain`
boundary is checked explicitly too.

Selected heads receive a positive-slope affine sigmoid calibration using
allowed `branch_calibration` only, with the original balanced BCE/L-BFGS-B
recipe. Calibration failure is failure, not identity calibration or a reason
to try another grid after seeing the results.

No matched-sample control, fusion-weight optimization or risk model is needed
for this first classifier question. A later risk study must cross-fit the
entire selected pipeline afresh; these source results alone do not authorize it.

## 4. Six visible systems

1. Original299 DINO-Reg.
2. Original299 calibrated equal DINO-Reg/plain-DINO.
3. Original299 fixed-prompt, calibrated zero-shot OpenCLIP.
4. Source-selected DINO-Reg.
5. Equal calibrated selected DINO-Reg/plain-DINO, sharing the very same
   selected DINO-Reg branch as system4.
6. Source-selected supervised OpenCLIP.

The two-DINO averages always have fixed equal weights. There is **no new
heterogeneous fusion or learned fusion weight**, and the old systems are not
silently replaced by their selected successors.

## 5. Metrics, thresholds and decision discipline

Report domain-OOF and `g_domain` separately. The former is primary; the latter
is a secondary internal held-out source diagnostic, not a new target test.
They have different training-domain compositions and populations, so their
difference is not a controlled treatment effect.

For every system and source domain report:

- AUROC, balanced accuracy and ACER on the common successful-image mask;
- successful-image APCER/BPCER, Brier score and NLL, clipping probabilities to
  `[1e-12, 1-1e-12]` for NLL only;
- original counts by class, technical-failure counts by class and ranking
  coverage;
- attack false acceptance, bona-fide non-acceptance and operational acceptance
  coverage on **original** denominators;
- successful score ranges and CLIP/DINO error-overlap counts.

Use attack-high scores; a tie at the threshold is attack/non-acceptance.
Choose each selected system's threshold on its allowed calibration rows by
the inherited largest-threshold rule satisfying empirical APCER<=5% in every
calibration source. Preserve each old system's exact old threshold.
Calibration and threshold selection share that allowed calibration role;
neither uses the held-out evaluation labels.

This is the old classifier reference policy, **not**301's selective FA<=1%
guardrail and not a target security guarantee. Threshold transfer remains a
separate measured limitation, not something fixed by high source AUROC.

Technical failures receive no invented score or classifier label. Their
existing non-accept action is retained. They therefore increase original
bona-fide non-acceptance and reduce ranking/acceptance coverage; failed attacks
are blocked rather than counted as accepted attacks. Successful ACER is not
relabeled as an original-denominator classifier ACER.

Macro summaries give each source equal weight. Retain every exclusion, seed,
candidate's inner-validation history and held-out candidate AUROC. Candidate
held-out AUROC is diagnostic **after** the selected model has been saved; it
must not select or revise the candidate set.

Use2000 paired dataset-stratified registered-group bootstrap draws for each
context/pool, identical draws for all systems. Report individual macro-AUROC
intervals and supervised-CLIP minus zero-shot/selected-DINO/selected-two-DINO
intervals. Require both-class support in at least95% of draws or stop with an
explicit support error. These are conditional saved-predictor intervals:
not retraining, new-domain or independent12-repetition uncertainty. They are
unadjusted descriptive intervals, not a familywise superiority test. Existing
registered groups are the resampling units; exact-frame unions are used for
split safety, not a new bootstrap clustering scheme.

Retain the inherited exploratory competence screen: macro AUROC>=.55,
balanced accuracy>=.55, AUROC lower bound>.5 and nondegenerate finite scores,
after finite successful calibration. A passing screen or positive paired
interval permits only discussion of a subsequent bounded study, **not**
automatic fusion promotion, tuning or target access. Report weak/redundant
CLIP and negative effects as outcomes, not triggers for a replacement run.

## 6. One execution and resource envelope

There are48 source fitting contexts and576 branch/candidate states:

-96 exact reused DINO heads;
-480 new heads, at most96,000 new training epochs;
-144 new selected-head calibrators;
-0 new image/text encoder forwards,0 GPU work,0 excluded-outer predictions;
-no risk models or learned fusion weights.

Execution uses the exact Python/NumPy/SciPy/threadpool runtime recorded in the
config, two BLAS threads, offline mode and a hidden CUDA device list. The one
approval starts one **6-hour** deadline for supervised preflight, fitting,
scoring, bootstrap and in-worker model/readback closure. Stop on any optimizer,
identity, population, readback or support error; do not retry automatically.

The supervisor samples worker-process-group plus its own RSS and all owned
output/temporary bytes every0.5seconds: stop at **4GiB combined sampled RSS**
or **1GiB new owned artifacts**. These are polling stop limits, not cgroup
instantaneous hard guarantees; deadline detection may lag one polling period
and termination allows up to10seconds before killing the same worker PID.
Existing baseline caches/artifacts are read-only and not charged as new output.
Within the output cap,64KiB is reserved for the immutable terminal and its
atomic temporary copy; a successful terminal cannot use that reserve for fits.
The later optional `--verify` performs only saved-output reconstruction, not
new fitting or a renewed execution clock.

Each fit start and completed head/calibrator is checkpointed immutably with
plan/baseline hashes. An incomplete attempt preserves completed candidates,
its precise last-started stage, traceback and stopped terminal, but does not
become a successful result or receive an automatic second attempt. Final
fit/prediction/metric/bootstrap reconstruction checks model selection,
validation BCE, calibration BCE, policies, identities, counters and hashes.
Numeric saved readback allows only `rtol=atol=1e-12`; categorical/identity
fields remain exact.

The6-hour value is a conservative upper stop envelope, not a promised runtime
or a right to expand the480/144 fit counts.

## 7. Artifact layout and execution gate

Private output root:
`/mnt/e/FAS-private/artifacts/phase1/source_readout308_v1/`.

| Path below that root | Meaning |
|---|---|
| `execution_plan.json` | Sealed software/runtime/cache/context/budget inventory |
| `execution_approval.json` | Absent until explicit owner approval of this complete package |
| `attempt_lock.json` | One supervisor attempt; cannot silently resume/retry |
| `worker.log`, `terminal.json` | Exact progress/failure/resource terminal |
| `combinations/<exclusion-seed>/<split-hash>.json` | All candidate heads, selected calibrators and policies |
| `combinations/<exclusion-seed>/checkpoints/` | Per-fit start/completion provenance, including partial attempts |
| `combinations/<exclusion-seed>/predictions.json` | Separate domain-OOF and `g_domain` successful prediction pools |
| `combinations/<exclusion-seed>/result.json` | All selections, candidate diagnostics, metrics and conditional uncertainty |
| `worker_completion.json` | Full12-context completion, only after complete verified fit counts |

Preparation reads/verifies caches and existing models but does not fit:

```bash
/home/lathevinh/miniforge3/envs/fas/bin/python scripts/run_readout308.py --prepare
```

Only after explicit approval of the sealed plan may the operator run
`--approve` followed by `--execute`. An absent approval, changed code/config,
expired original clock or existing attempt lock blocks fitting. `--worker`
also requires the live approving supervisor as its actual parent.
`--verify` requires a successful terminal and exact completion hash.

Publish only aggregate scientific outputs after successful saved closure;
keep per-image identities, labels, embeddings, coefficients and predictions
private. No scientific result is claimed by this preparation document.

## 8. CI correction and validation

The failed [workflow40464144686](https://github.com/lathevinh/fas/actions/runs/40464144686)
remains part of history. The previous workflow installed NumPy/OpenCV but the
new tests imported Pillow and numerical SciPy paths. The
[synthetic dependency profile](../configs/ci-synthetic308.in) now explicitly
installs Pillow, SciPy, scikit-learn and threadpoolctl alongside NumPy/OpenCV.
The [workflow](../.github/workflows/phase0-governance.yml) still runs the entire
suite, canonical schema validation and unavailable/legacy fail-closed checks.
No whole-module skip or private scientific rerun substitutes for those tests.

A regression test first reproduced `ModuleNotFoundError` instead of the
required invalid-input `ValueError` without SciPy. Candidate risk input
validation now precedes the optional SciPy import. Valid-input risk objective,
optimizer settings and historical outputs are unchanged.

An isolated Python3.12 environment created from the declared CI profile passed
the full514-test suite before the additional partial-fit-ledger hardening.
The final21 focused readout tests passed after that hardening, including
synthetic fitting, saved-output closure without refitting, held-out-label
invariance, exact baseline scores, failure denominators, fit/resource caps
and optimizer failure with persistent completed candidates. Canonical schema
and all seven expected unavailable/legacy stage rejections passed.
Release-green additionally requires checking Actions on the actual published
commit, not treating this local validation as a remote CI result.

Pylance's MCP transport was unavailable; no editor diagnostic/type-check claim
is made. Direct execution/imports and numerical regression tests provide the
available validation evidence.

For306's wording concern, the historical G2 config's phrase "same ...
coefficients" means the same parameterization/objective/initialization, **not**
guaranteed identical fitted coefficients. A larger line-search cap can change
the optimized solution. This clarification does not rewrite bound G2 configs
or reinterpret the negative/mixed geometry result.

## Owner decision required

Approve or decline **this complete480-head/144-calibrator source-only package**
and its6-hour/4GiB/1GiB envelope once. Until that decision, only software tests,
cache verification and publication of this proposal/plan are in scope.
Independent confirmation and Q3 publication claims remain a separate question
requiring defensible results and genuinely unseen authorized validation.
