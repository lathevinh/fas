# 305 - Source-only geometry-preserving PAD experiment

Date: 2026-10-27.
Motivation: [Proposal303](303-proposal-improving-dino-openclip-pad.md).
Prior fixed evidence: [299](299-complete-source-experiment-and-clustered-evidence.md),
[301](301-locked-target-package-and-fixed-evaluation.md) and
[Review302](302-review-doc301-locked-target-results-and-final-claims.md).

Publication note: [Review304](304-review-proposal303-geometry-and-source-selected-fusion.md)
arrived on the remote branch while Git authentication was being restored, after
the exploratory execution and local report commit. The report is numbered 305
to preserve that review's number. Execution configs, private paths and receipts
retain their original checkpoint 304 identifiers; none were rewritten.
This execution is not a prospective response satisfying Review304's required
concrete protocol and bounded source-pilot prerequisites. Its nested-selection,
estimand and preregistration requirements remain open. No further execution is
authorized by publishing this report.

## Result and scope

**The G2 padding candidate completed all 12 source-only exclusion/seed contexts.
It does not show a uniform improvement over the stretched-input baseline.
DINO-Reg improves slightly on the descriptive context average; OpenCLIP
deteriorates in every context. No new target evaluation was performed.**

After Proposal303, the owner requested implementation and explicitly chose
source-only exploratory work using the existing datasets, rather than supplying
an unseen target. This changes neither the interpretation of 301 nor its
registered RQ1/RQ2 outcomes. Source-only here means the permanent accepted
source-use population, not a new official-train-only benchmark: OULU, CASIA and
MSU include official-test members already assigned source roles in the earlier
study. SiW null-role official tests and the five adopted source exclusions remain
excluded. These familiar datasets cannot establish independent confirmation of
a method developed after their previous results were observed.

This report closes the geometry experiment, **not all of Proposal303**.
Nested convex-fusion selection, a standalone plain-DINO comparison with its
own operational policy, direct-alignment G1, and independent-target validation
have not been completed.

## Controlled input change

The candidate uses G2, not G1:

1. Read the accepted shared face-context crop and verify its transaction,
   selected-frame join, raw RGB hash and dimensions.
2. Pad to `max(height, width)` with constant RGB `(0, 0, 0)`.
3. Center the original crop; any odd extra pixel goes to the bottom/right.
4. Resize the square isotropically with OpenCV bicubic interpolation to
   224 for OpenCLIP and 518 for the two DINO encoders.

This avoids unequal horizontal/vertical scaling. It preserves the *saved*
context pixels, not the original frame's full context: previously clipped
regions remain clipped. Padding also changes object size and introduces black
borders, so any metric change is not an isolated causal measurement of stretch.
G2 was chosen before fitting candidate scores because saved shared crops were
available across all four sources; the original CASIA preprocessing root had
no saved frame images. That is not proof that G1 is impossible.

The [geometry config](../configs/geometry_candidate304_v1.yaml),
[transform](../src/fas/geometry_candidate.py) and
[builder](../scripts/build_geometry_candidate304.py) are separate from the
accepted preprocessing-v3 implementation. Existing crops were not overwritten.
Source labels, original frame choices, groups and permanent roles were not
reassigned. Original detector/pre-detector failures remain non-accepts, without
invented crops, embeddings or model scores.

| Population / artifact | Count |
|---|---:|
| Source-use original denominator | 6,882 |
| Successful candidate source inputs | 6,855 |
| Retained technical failures | 27 |
| Candidate PNGs, two resolutions per success | 13,710 |
| Candidate PNG bytes | 2,443,394,727 |
| Complete cached feature rows, per encoder | 6,855 |

## Fitting protocol and optimizer amendment

The encoders, checkpoints, fixed prompts, native normalization, source
partitions, 200-epoch head recipe, calibration roles, quality-statistics
convention, source operating thresholds, risk features and diagnostic
bootstrap recipe are inherited from 299. The candidate regenerates all three
encoders' source features; old stretched-input embeddings are not mislabeled as
G2 features. Fixed text embeddings are reused by verified hash.

Each of four outer-source exclusions has three seeds. Within a context, the
excluded dataset never enters fitting, calibration or prediction. The
remaining three sources provide final and OOF fits; predictions are source OOF
or permanent G_domain diagnostics, not predictions on the excluded target.
G_domain remains outside head, calibrator and risk fitting.

The first source analysis stopped after seven completed contexts on a genuine
L-BFGS-B risk-fit error in `MSU-MFSD-20260923`, domain-OOF heterogeneous
`R_DV_noq`. Inputs were finite, with 5,264 rows and 2,772 errors. The default
line search returned `ABNORMAL` after 19 iterations, with gradient infinity
norm approximately `1.1263e-5`; it was not accepted as a successful model.

An explicit exploratory amendment raises the risk optimizer's `maxls` from
SciPy's default 20 to 50. The objective, regularization, initial values,
`maxiter=1000`, `ftol=1e-12` and `gtol=1e-7` are unchanged. The exact failing
saved-input reproduction converged by the optimizer's relative-objective
criterion after 20 iterations. All 12 contexts were then fitted afresh under
the same amended risk optimizer, reusing only hash-verified candidate features,
not the seven earlier completed contexts. All 480 final risk models record
`line_search_maximum=50`.

The [original execution config](../configs/source_geometry304_v1.yaml) and
[amended config](../configs/source_geometry304_v2.yaml) preserve that distinction.
The [extraction/initial runner](../scripts/run_geometry_candidate304.py) and
[uniform amended runner](../scripts/run_geometry_candidate304_v2.py) reuse the
299 fitting implementation without editing it. The amended risk routine is
isolated in the new candidate module; it does not repair or refit historical
299/301 models.

This is **not** a prospectively sealed/reviewed execution package equivalent
to 299/301. Implementation errors and the optimizer amendment occurred during
development; current public controller source also includes subsequent import,
path-restoration and validation repairs. Do not equate current code inspection
or saved-output reconstruction with a pre-run code freeze.

## Comparison with 299

Each cell below is the descriptive mean of 12 *overlapping source contexts*.
Within each context, AUROC is an equal-source macro from domain-OOF predictions.
The contexts are not 12 independent datasets or replications. The difference
is G2 minus the exact accepted 299 source result; it is not target performance.

| System | Baseline source AUROC | G2 source AUROC | Difference | Positive contexts |
|---|---:|---:|---:|---:|
| DINO-Reg | 0.885432 | 0.887607 | +0.002174 | 8/12 |
| OpenCLIP | 0.554171 | 0.518196 | -0.035975 | 0/12 |
| Equal DINO-Reg/OpenCLIP | 0.852912 | 0.852442 | -0.000471 | 4/12 |
| Equal DINO-Reg/plain-DINO | 0.889609 | 0.885614 | -0.003995 | 1/12 |

The following rows average seeds for each exclusion. The named dataset is
**excluded**, not evaluated; the numbers describe its three remaining sources.

| Outer source exclusion | DINO-Reg baseline | DINO-Reg G2 | OpenCLIP baseline | OpenCLIP G2 |
|---|---:|---:|---:|---:|
| OULU-NPU | 0.926474 | 0.925736 | 0.578760 | 0.558527 |
| CASIA-FASD | 0.827217 | 0.820184 | 0.544497 | 0.531435 |
| MSU-MFSD | 0.896403 | 0.899290 | 0.560214 | 0.491411 |
| SiW-Mv2 | 0.891636 | 0.905217 | 0.533214 | 0.491411 |

OpenCLIP still fails the inherited standalone competence gate in all 12
contexts. Source primary heterogeneous domain-OOF-minus-matched-sample risk AP
has seven negative saved intervals, four inconclusive intervals and one
positive interval; only one point contrast is positive. These intervals compare
OOF strategies **within G2**, not G2 versus baseline. There is no paired
geometry-effect interval in this report and no claim that the small DINO
average gain is statistically supported.

Full per-context AUROC comparisons, competence pass flags and saved primary
source diagnostic intervals are in the
[aggregate verification/comparison receipt](../results/phase1/source-geometry304-closure-v1.json).
Do not promote G2, OpenCLIP fusion, or a favorable exclusion based on these
descriptive means.

## Saved-output verification

The public [readback verifier](../scripts/close_geometry_candidate304.py):

- Rejoins all source-use rows to the accepted immutable manifest and rebuilds
  the group-safe primary/budget partitions.
- Reconstructs every candidate PNG from the hash-verified original shared crop
  and compares actual decoded RGB pixels and padding metadata: all 13,710 pass.
- Verifies the pinned feature-cache file and numeric-payload hashes, shapes and
  exact row joins; it does not rerun an encoder.
- Verifies all 288 heads and 432 calibrators' saved fitted states/bindings,
  selected head validation losses and source policies; reconstructs 171,612
  primary/budget context prediction rows.
- Reconstructs all 480 G_domain risk-model predictions and AP point values,
  error supervision and quality-statistics provenance; checks the uniform
  line-search amendment.
- Recomputes source competence AUROC/balanced-accuracy points and all reported
  candidate-minus-baseline arithmetic from saved predictions/results.

Policy threshold readback uses the existing verifier convention of
`rtol=atol=1e-12`; evaluating a selected matrix slice versus selecting from a
full matrix multiplication produced differences of approximately `1e-16`.
Other policy fields and class error/action records must still agree. This
normal floating-point tolerance does not rewrite a threshold or scientific
result. Bootstrap intervals are retained as saved execution outputs; closure
does not resample or independently reproduce their bounds.

Closure completed in 202.76 seconds, with no new encoder or optimization calls.
The final amended source fitting pass took 968.91 seconds and reported
1,151,021,056 bytes peak process RSS. Candidate image generation took 847.08
seconds. These are separate stages, **not** total campaign time or combined
resource measurements across failed attempts. There was no process-tree
supervisor/independent resource observer comparable to 299/301; periodic
in-process checks do not constitute hard OS resource guarantees.

Both original and successor freeze-record files remain byte-identical to
the pre-304 HEAD. All 156 current successor301 pins match. A direct current-tree
check of the original 147-pin source freeze still finds four historical tool/
contract mismatches, each already byte-identical to pre-304 HEAD:
`scripts/validate_preregistration.py`, `scripts/write_freeze_record.py`,
`src/fas/contracts.py` and `src/fas/preregistration.py`. This work did not
introduce or silently repair those differences; do not describe the original
source freeze as having all current-tree hashes match.

All 12 contexts also have row IDs, primary/budget partitions, budget caps and
original population counts identical to the accepted 299 inputs.

Validation at publication: 12 candidate geometry/controller regression tests,
15 existing source-fitting tests and 11 existing source299 tests pass (38
tests total). No full-suite or independent scientific replication claim is made.

## Artifact organization and failed attempts

Private data remain outside Git. Paths relative to the workspace parent:

| Private location | Purpose |
|---|---|
| `FAS-private/artifacts/phase1/geometry_candidate304_source_v1/` | Completed G2 PNGs and generation receipt; PNGs under `crops/<dataset>/<sample-key>/224.png` and `518.png` |
| `FAS-private/artifacts/phase1/source_geometry304_v4/features/` | Complete G2 feature/quality cache; not a completed source analysis |
| `FAS-private/artifacts/phase1/source_geometry304_v5/` | Final uniformly amended 12-context fits, predictions, results and closure |
| `FAS-private/artifacts/phase1/source_integration295_v1/source_manifest.json` | Authoritative source ID, label, official-split, role and original transaction joins |

Sample directories use SHA256 of `dataset + NUL + video_id`. They are not new
identities or labels. Join them through the generation receipt and original
manifest. Preserve official split separately from experimental role.

Earlier attempt directories remain history, not alternative winning runs:

- `source_geometry304_v1`: failed before image inference because normalization
  was incorrectly sought in acquisition metadata.
- `source_geometry304_v2`: DINO extraction ran, then OpenCLIP stopped because
  the deterministic CuBLAS workspace environment variable was absent.
- `source_geometry304_v3`: all three extractions ran, then receipt assembly
  failed by looking for fixed text metadata in the wrong generation's receipt.
- `source_geometry304_v4`: complete feature cache, but only seven source
  contexts completed before the default line-search failure above. A transient
  missing-contract-variable error was corrected before this extraction.
- `source_geometry304_v5`: the final amended analysis. A preflight receipt
  timing comparison was corrected before its successful fitting pass.

The observed failed attempts were manually corrected, not a claimed single
successful bounded run. Their transient arrays were not all persisted, so the
20,565 image forwards attached to the complete feature cache must not be
reported as the entire development campaign's inference count.

## Decision and next work

1. Keep the 299 baseline and the completed 301 conclusions unchanged.
2. Retain G2 as a tested exploratory ablation, not an accepted improvement.
3. If continuing source-only development, preregister the exact nested
   group-safe fusion-selection procedure and competence gate before computing
   new selection results. OpenCLIP's repeated gate failure must be retained,
   not tuned away by target prompts or post-hoc subgroup selection.
4. Any G1/direct-alignment study needs verified original-frame provenance and
   its own versioned scope, rather than silently replacing G2.
5. Publication as exploratory/negative evidence is possible; a claim of
   independent generalization improvement still requires a genuinely unseen
   licensed dataset or prospective cohort. No Q3 acceptance promise follows
   from this experiment.
