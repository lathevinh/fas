# 298 - Review of297: first actual source fitting and OOF results

Date: 2026-10-26
Reviewed commit: `70e7bed5a62211ddc1796a15dedd7ab62d5b7e5b`
Governing review: [296](296-review-doc295-source-integration-and-encoder-pilot.md).

## Decision

**Accept297's first-fold feature coverage, actual source fitting and saved-output closure as scoped execution evidence. No data/image/encoder rerun is required. Do not accept a completed scientific source-dry-run, a claim that domain-OOF wins, standalone OpenCLIP competence or target performance. Final published-head CI remains unconfirmed at review time.**

This is substantive progress beyond295: actual DINO classifiers, affine calibrators, source-held-out predictions/error labels and logistic risk models have been fitted. Only outer target OULU and seed20260917 are covered; it is one of the twelve registered outer-target/seed combinations. All data milestones and295 remain closed.

## What was actually done

CASIA/MSU/eligible SiW contribute1932 source originals:1906 successful image inputs and26 retained terminal failures. Permanent train/calibration/g_domain successful-image counts are1135/389/382, with original failure-inclusive denominators1156/391/385. OULU is excluded completely, as are SiW null-test originals and five adopted source exclusions. Failed originals receive no invented features, scores or error labels.

All1906 images have frozen DINO-Reg1536-dimensional, DINO-plain1536-dimensional and OpenCLIP512-dimensional features. Each model reuses24 compatible295 rows and computes1882 new rows:5646 new image forwards,72 reused rows and5718 sample/model joins. FP32 payload27324416 bytes reconciles. Registered checkpoint digests, native crops/normalization and runtime-aware keys are bound; no new weights, text inference, video decoding or detector campaign is reported.

Seven contexts are fitted: one final-source context, three complete source-domain exclusions and three group-safe matched-sample folds. Two DINO heads per context produce14 actual head fits. Three monotone affine calibrators per context produce21 fits, including OpenCLIP calibration without a learned OpenCLIP image/text head. Inner validation uses only train-role groups; branch calibration is separate. Each system's threshold is selected from its allowed calibration remainder under the declared empirical per-domain APCER constraint. No target threshold is selected.

Each OOF strategy predicts the same1524 successful train-plus-calibration originals exactly once, from contexts that exclude the held-out domain or group from branch fitting/selection/calibration. The final-source models predict382 untouched g_domain images. Saved predictions total3430 rows, with multiple branch/system values per row. Risk training uses only source-OOF error events, not g_domain labels: two systems x two strategies x six registered vectors =24 fitted logistic models. Permanent groups and exact selected-frame duplicates are joined before sample/inner splits.

The quality statistics are deliberately shared final-head-fitting-pool statistics, not separately estimated in every pseudo-domain remainder; they never use g_domain. Thus the complete pipeline must not be described as having every auxiliary preprocessing statistic estimated within each pseudo-domain remainder. The branch fitting/calibration exclusion is checked separately. Preserve the exact declared convention in later comparisons rather than silently changing it after results.

## Verification performed

Reviewed report297, config/plan/run/closure receipts, execution/cache/fitting/closure sources and focused regressions. Locally ran six actual partition/objective-weight/threshold/risk-vector tests: all passed. Three numerical optimization tests were skipped because SciPy is absent on this reviewer host. The OpenCV quality test, filesystem-dependent shard tests and full synthetic-controller test were not selected locally. No actual optimization/GPU/media replay was performed here; the producer's91-test report is separate evidence.

Independent public checks passed for config and closure-source hashes, unchanged accepted summaries, fold-local totals, seven-context head/calibrator counts,24 risk records, OOF candidate coverage/count arithmetic, per-domain macro AUROC/BA arithmetic, feature-call reuse and payload size. Private split IDs, models, arrays, approvals and prediction rows are unavailable here. Actual execution/reconstruction remains bounded producer-reported evidence supported by reviewed code/public commitments. Technical readback is not independent scientific replication or new visual adjudication.

Exact-head checks identify [run40290548935](https://github.com/lathevinh/fas/actions/runs/40290548935), [validate121464322107](https://github.com/lathevinh/fas/actions/runs/40290548935/job/121464322107). On both checks, setup/checkout were successful but later conclusions were null and Complete job was absent. CI is **unconfirmed**, not proven success or failure. Collect its terminal result in the next ordinary package; if it fails, fix the concrete defect and rerun appropriate checks, without blindly repeating the private model campaign.

Reported terminal418.31s and closure442.04s, combined RSS2418397184 bytes and owned storage44819878 bytes are below the declared caps. Final GPU allocator peaks are now persisted after extraction; fixed text is reused. Saved-output closure reportedly reconstructs14 selected heads,21 calibrators/threshold policies,3430 prediction rows/error events and24 risk-model g_domain predictions without new inference/optimization. These private observations were not independently reproduced.

## Interpretation: encouraging execution, unfavorable primary comparison

| System | Domain-OOF macro AUROC /BA | Matched sample-OOF macro AUROC /BA |
|---|---:|---:|
|DINO-Reg|0.925129 /0.740563|0.986548 /0.870852|
|OpenCLIP|0.578760 /0.506145|0.560270 /0.508997|
|Heterogeneous average|0.891155 /0.759575|0.986606 /0.904754|
|Same-family average|0.945292 /0.806826|0.987641 /0.883827|

These are source-held-out point diagnostics. Balanced accuracy averages bona-fide and attack recall and is not ordinary overall accuracy; AUROC measures ranking and does not certify an operating threshold. Matched sample and unseen-domain validation answer different generalization questions. More favorable sample-OOF branch scores do not alone establish which strategy learns the best transferable risk model.

Standalone OpenCLIP is approximately0.51 BA in both strategies, below the registered0.55 competence point requirement. It cannot be presented as a competent standalone PAD branch. Do not tune prompts/checkpoints, flip score polarity or replace the branch in response. Claim-specific dependencies can still be assessed for the complete system; standalone failure is not automatic proof of every pair claim failing.

For the primary R_DVd risk vector, g_domain error AP is:

| Complete system | Domain-OOF | Matched sample-OOF | Same held-out error count |
|---|---:|---:|---:|
|Heterogeneous|0.316771|0.621164|27 /382|
|Same-family|0.395060|0.565616|15 /382|

Higher AP means better ranking of actual errors, not higher PAD classification accuracy. Both comparisons currently favor matched sample-OOF. Its Brier/NLL are also lower: heterogeneous0.044058/0.156559 versus0.070133/0.250401; same-family0.030594/0.136347 versus0.047675/0.193127. These are diagnostics, not proof of calibrated deployment risk. The same final classifier and error set are shared across risk strategies within each system.

The low15-error same-family g_domain support makes uncertainty material. The >=20 error/correct fitting check applies to source-OOF risk training, where it passes; it does not magically give this15-error diagnostic strong precision. Do not retrospectively discard that unfavorable or low-support result, select another vector or tune on g_domain. No paired clustered intervals, target results or twelve-combination aggregate exist yet.

Most head contexts select epoch200, the fixed budget endpoint. This establishes selection under that budget, not optimizer convergence or an optimal training duration. Preserve it as the registered result; no result-driven epoch extension is needed to accept the execution. Domain-exclusion and matched-sample head-fitting sizes also differ substantially, so a causal claim about domain holdout alone would be confounded until the already required budget-matched sensitivity is produced.

## Next package: finish the fixed comparison, reuse completed work

1. Generalize the controller to the remaining eleven outer-target/seed combinations under the existing recipe and applicable explicit execution authority. Preserve this completed first result. Reuse the1906-image frozen features across source seeds/folds by verified compatible keys; only4949 OULU successful inputs remain uncached in the6855-image union, to be accessed when OULU is an authorized source for other rotations. Being a source in another rotation does not authorize predictions on the current outer target.
2. In the same implementation/execution package, add the already registered fit-size sensitivity, no-quality attribution, domain-identifiability and OOF-to-final drift diagnostics, clustered competence uncertainty and claim-specific applicability. Reuse saved features/predictions whenever possible. Do not turn each missing diagnostic into a separate permission/review loop or change model settings to reverse this first comparison.
3. Publish one complete source evidence bundle with actual fold/seed coverage, original/score-eligible denominators, paired comparisons, uncertainty/support and explicit pass/fail/not-applicable outcomes. Keep weak OpenCLIP and unfavorable domain-OOF findings. A failed hypothesis or inapplicable claim is a valid scientific outcome, not an infrastructure failure to conceal with more tuning.
4. Run the normal source-dry-run validator only when those required artifacts actually exist, then create the analysis freeze through its existing gate. No placeholder evidence, target tuning, target evaluation or immediate locked-evaluation authorization is inferred from297. The current missing-source-evidence/freeze errors are honestly reported and should be resolved by completing evidence, not changing readiness definitions.

Prepare the executable generalized package, resource estimates and one combined request if fresh authority is needed;297's completed one-fold/one-seed authority does not automatically cover expansion. No checkpoint re-download, dataset re-audit, repeated feature campaign or retraining of unchanged completed contexts is needed. Bind eventual exact-head CI success without rewriting historical receipts.

**297 completes real first-fold source fitting. The current primary risk comparison favors matched sample-OOF; finish the fixed experiment and quantify uncertainty before deciding the scientific claims.**
