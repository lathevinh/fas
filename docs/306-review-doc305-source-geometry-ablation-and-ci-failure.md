# 306 - Review of305: exploratory G2 geometry ablation and failed CI

Date: 2026-10-27
Reviewed commit: `57af7fe1083416d19dda7a4f0172de42630272ac`
Prior review: [304](304-review-proposal303-geometry-and-source-selected-fusion.md).

## Decision

**Accept305 as a transparently reported source-only exploratory ablation with saved-output verification. Do not accept G2 as a demonstrated improvement, independent target evidence, completion of Proposal303/Review304, or a passing software release. Exact-head CI fails and needs a dependency/test-contract correction. No scientific run needs repeating solely for that CI repair.**

305 explicitly places execution before receipt of remote Review304 and reports separate owner authorization for source exploration. It is not a prospective implementation of that review's full protocol. Do not impose retrospective preregistration or imply that current source bytes were necessarily the executed pre-run version. Existing299/301 results and all accepted data milestones remain unchanged.

## What was achieved

G2 is a real, bounded geometry intervention: read the accepted shared rectangular crop, preserve its RGB pixels, center-pad with black to the larger dimension, assign odd excess to bottom/right, then bicubic-resize isotropically to224/518. It introduces borders and changes face occupancy; it does not restore context clipped before the crop. It is not G1 direct alignment or simply a different label on the old stretched embeddings.

Reported coverage is6882 source-use originals,6855 successes and27 retained failures;13710 new PNGs,2443394727 image bytes and6855 feature rows per encoder. Twelve source-exclusion/seed contexts are completed with288 head states,432 calibrators,480 risk models and171612 reconstructed context prediction rows. The final comparison preserves the old source IDs, roles, primary/budget partitions and counts. Source exclusion names identify a domain absent from that context, not a newly evaluated target.

The final analysis reuses verified G2 features but refits all contexts uniformly after the optimizer amendment. Initial failed attempts are retained.20565 encoder forwards describe the complete feature-cache generation only, not total development-campaign inference; several earlier extractions also ran. Stage timings and self RSS are not a combined campaign wall/RSS cap receipt. This honest distinction is necessary and correctly made in305.

## Descriptive result: no reason to promote G2

| System | Baseline mean source AUROC | G2 mean source AUROC | Change | Positive contexts |
|---|---:|---:|---:|---:|
|DINO-Reg|0.885432|0.887607|+0.002174|8/12|
|OpenCLIP|0.554171|0.518196|-0.035975|0/12|
|Equal DINO-Reg/OpenCLIP|0.852912|0.852442|-0.000471|4/12|
|Equal two DINO|0.889609|0.885614|-0.003995|1/12|

DINO-Reg gains approximately0.22 AUROC percentage points on this descriptive average, not0.22% proven generalization gain. OpenCLIP loses approximately3.60 points and still fails competence in every context. The two-DINO comparator is present, addressing an omission in303's proposed panel, but its average also declines. There is no uniform geometry benefit and no evidence that removing stretch repairs OpenCLIP.

These are twelve overlapping source contexts, not twelve independent trials or unseen-target results. No paired **G2-minus-G0 geometry-effect interval** is supplied. The seven negative/four inconclusive/one positive AP intervals compare domain-OOF versus sample-OOF **inside G2**; they do not establish improvement over299. Differences in classifier behavior also change error sets, so raw error AP across geometry settings is not automatically an identical-error-set ranking comparison. Keep head AUROC and downstream risk claims distinct.

Padding plausibly removes anisotropic scaling, but can suppress useful facial detail at fixed224 resolution or alter contextual cues. Such mechanisms are hypotheses, not established explanations of the observed OpenCLIP drop. Do not use the small DINO average increase to select favorable domains, declare G2 universally superior, tune prompts or justify a new target evaluation.

## Optimizer amendment and provenance

The first analysis stopped on a real L-BFGS-B line-search failure; the failure was not labeled success. Increasing maxls20 to50 preserves the declared loss/regularization family and tolerances, but may change the numerical solution. Uniformly applying it to all candidate risk fits is preferable to keeping a selectively patched context. Report convergence by its actual criterion; relative-objective convergence is not evidence that gradient norm met gtol.

This amendment does not itself explain branch AUROC changes, because risk optimization is downstream of head/calibrator predictions. However, candidate-versus-baseline **risk** contrasts would mix geometry with the optimizer-setting change. A future isolated risk-effect claim must account for that, potentially through a saved-feature optimizer control, without rerunning encoders. No such new control is required merely to retain this honest exploratory result. Correct the config phrase "same ... coefficients" if read as equality of fitted weights: the same parameterization/initialization is not a promise of identical output coefficients.

Current controller source includes later development repairs, and no299/301-equivalent process-tree supervisor or sealed execution provenance is claimed. Saved-output reconstruction establishes artifact consistency, not historical execution of every current code byte or hard resource compliance across all attempts. No retrospective authority/freeze claim should be manufactured. Owner authorization is producer-reported; the private approval and complete development logs are unavailable here.

## Verification and concrete CI blocker

Read305, configs, geometry and amended-risk functions, generation/fitting/closure controllers, public comparison and tests. Independently executed the actual compare_results function with its repository signed-delta/population-preservation regression: passed. Additional checks passed for all twelve299 baseline joins, candidate-minus-baseline arithmetic, descriptive means/sign counts, image/failure totals, closure-source hash and all156 current successor301 pins. Private image reconstruction, feature arrays, optimization and bootstrap bounds were not replayed locally. OpenCV/SciPy are unavailable on this reviewer host, so no local pixel-transform/numerical-fit test success is claimed. Technical hash checks are not independent scientific replication or visual adjudication.

Exact-head [run40464144686](https://github.com/lathevinh/fas/actions/runs/40464144686), [validate122055414329](https://github.com/lathevinh/fas/actions/runs/40464144686/job/122055414329) has **Run synthetic regression suite: failure**; schema and downstream gate checks were skipped. Reading the actual job logs confirms491 discovered tests, four errors and nine skips. Three geometry risk tests error on missing scipy; test_geometry_candidate_controllers cannot import because PIL/Pillow is missing. A successful cleanup/Complete job step does not make the validate job green.

Fix the concrete CI dependency/test split before claiming a verified software publication: declare Pillow for the new controller-import tests; either run numerical tests in a dependency-declared numerical CI job or mark genuinely optional numerical cases consistently with the existing lightweight profile while separately exercising them in the full numerical environment. Keep model-free geometry/population tests active. Prefer validating malformed inputs before the optional SciPy import so their contract can be tested without the optimizer runtime. Do not simply suppress import errors, skip the whole module or weaken scientific checks. Publish exact corrected-head test/CI results; no private scientific model rerun is needed.

Both freeze files remain unchanged. All156 active301 pins match; the original299 source freeze's four current-tree mismatches were already introduced by the accepted301 successor work and are not new geometry damage. New exploratory modules do not retroactively belong to the old execution. Preserve separate original/source-successor/exploratory identities.

## Next work without another exploration loop

1. Correct CI/dependency handling and include the exact failure/correction in the same ordinary reporting update. Keep current models, images and305's negative/mixed result; no dataset re-audit or full extraction/refitting is needed.
2. Retain G2 as a completed exploratory ablation, not the default replacement for preprocessing-v3. Finish the prior experiment's reproducibility/reporting bundle, including the inspectable301 normalization-only verifier. No independent target claim is available for G2.
3. Do not automatically launch nested-fusion or G1 just because they remain open in303. The present evidence does not justify an open-ended search to rescue OpenCLIP. If the owner elects a further study, first provide the compact protocol requested in304: explicit endpoints, strong comparator, nested group-safe selection/risk supervision, stopping rule, resource envelope and exploratory-versus-independent scope. Use saved baseline/G2 artifacts where compatible; obtain fresh explicit execution scope only once the package is concrete.

**305 answers the exploratory padding question with a small DINO change, consistent OpenCLIP deterioration and no established overall gain. Accept that result; repair CI and report it before deciding whether another study is worth running.**
