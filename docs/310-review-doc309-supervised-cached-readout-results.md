# 310 - Review of309: supervised cached readouts and source transfer

Date: 2026-10-27
Reviewed commit: `afc2e520dea36e32db9b9cfdeef3acbf4ab85490`
Execution package: [308](308-cache-only-supervised-readout-execution-package.md).
Recommendations: [307](307-recommendations-improving-pad-classification-from-cached-features.md).

## Decision

**Accept308/309's completed cache-only source-readout study and saved-output closure. Supervised OpenCLIP clearly improves over the fixed zero-shot branch on held-out source ranking, but does not beat the strong two-DINO comparator or solve operating-point transfer. Do not promote a new heterogeneous system or revised target claim from this result.**

This closes307's cheap readout-screen question without another encoder/geometry campaign. DINO head selection was also tested fairly against its old anchors, with mixed/negative ranking results retained. Fusion selection, risk cross-fitting for a selected pipeline, backbone fine-tuning and independent target confirmation have not been done and are not implicitly authorized.301's RQ1 inconclusive/RQ2 evidence-against outcomes remain unchanged.

## Verification and publication checks

Reviewed308/309, config/plan/aggregate closure, readout selection/scoring/metrics and controller/saved-verifier code. Exact final-head GitHub [run40472879618](https://github.com/lathevinh/fas/actions/runs/40472879618), [validate122083958273](https://github.com/lathevinh/fas/actions/runs/40472879618/job/122083958273) has success conclusions for all12 listed steps, including numerical-dependency installation, regression suite, schema and stage checks.306's failed publication is historical; the dependency correction is now verified without repeating that scientific campaign.

Independently checked pre-execution code/config/plan hashes against both current public bytes and the reported scientific execution commit f02a268832a412dd9cb58b71bea8649dca16ffa1. All matched. Checks also passed for twelve unique contexts,576 candidate-state accounting,480 new heads/144 calibrators,61695 prediction rows/370170 system scores, every descriptive metric mean, paired contrast means/sign counts and2000 valid draws per pool/context.

Five actual metric/readback repository regressions passed locally using the actual metric module and extracted unchanged check_reconstruction function. A normal whole-module import was unavailable because this reviewer environment lacks threadpoolctl; no full local numerical/controller suite success is claimed. Private approval, caches, model coefficients and prediction rows were not accessed; actual source fitting/readback is bounded producer-reported evidence supported by reviewed code, commitments and exact-head CI. Hash reconstruction is not independent scientific replication or new visual adjudication.

## What was actually executed

The original299 stretched-input caches are reused:6882 source-use originals,6855 usable inputs and27 retained failures, with the existing permanent roles and SiW exclusions. Each outer exclusion/seed has final-source and three complete-domain-OOF fitting contexts, totaling48. Its excluded outer dataset enters neither fitting nor evaluation in that context. The held-out pseudo-source domain is absent from fitting, epoch/grid selection, calibration and threshold selection. Final g_domain remains separate from all selection/calibration.

Each branch gets four predeclared candidates: exact old recipe, unit-L2 features, higher learning rate and lower weight decay. Selection uses inner equal-domain/class-balanced validation BCE with fixed candidate-order ties; head epoch selection retains earliest minimum. No extra candidate or epoch was introduced after seeing held-out results.96 DINO anchor heads are reused,480 new heads fitted, and144 selected heads calibrated. The fixed equal two-DINO system shares its selected DINO-Reg branch with the standalone comparator. No new learned heterogeneous weight or risk model is fitted.

One reported approved attempt completes in253.64s with sampled combined RSS635604992 bytes and111476262 owned bytes before terminal, below its caps. The later141.84-second saved-only verification is separately accounted for. There are zero new encoder forwards, raw image decodes or target evaluations.61695 rows equal6855 originals repeated nine times, not61695 independent samples. Prediction rows are49347 domain-OOF plus12348 g_domain; repeated original-denominator instances61938 include243 failures.

## Result: useful CLIP embeddings, not a winning replacement

| System | Primary source AUROC | Balanced accuracy | Success-only ACER |
|---|---:|---:|---:|
|Old DINO-Reg|0.885432|0.714898|0.285102|
|Old equal two-DINO|0.889609|0.723324|0.276676|
|Zero-shot CLIP|0.554171|0.501294|0.498706|
|Selected DINO-Reg|0.879631|0.733053|0.266947|
|Selected equal two-DINO|0.889780|0.735689|0.264311|
|Supervised CLIP|0.844040|0.681211|0.318789|

Supervised CLIP gains0.289869 AUROC versus zero-shot, with positive conditional paired intervals in12/12 contexts. This supports307's narrower hypothesis: the existing image embeddings contain PAD information that the fixed text-prompt readout did not extract. It does not establish a novel backbone, unsupervised improvement or unseen-target generalization; supervised labels and a learned head add task-specific information/capacity relative to zero-shot.

CLIP remains below selected two-DINO by0.045740 on average: ten negative conditional intervals, two inconclusive, none positive. Against selected DINO-Reg it is lower by0.035591, with seven negative/five inconclusive intervals. All selected branches pass the source competence screen, but competence is not incremental value or a reason to assign CLIP positive fusion weight automatically.

Selected two-DINO improves old-anchor AUROC by only0.000171 descriptively (five positive/seven negative contexts), with no registered paired selected-minus-old interval. Selected DINO-Reg declines0.005802, worse in ten primary contexts. Lower inner validation BCE and better thresholded BA do not imply better ranking on a new source domain. Keep the strong old two-DINO anchor visible; do not claim the grid found a superior DINO recipe.

All48 DINO-Reg/CLIP contexts choose higher learning rate; CLIP selects epoch200 in48/48 and Reg in43/48. These are outcomes under the fixed budget, not convergence proofs, global hyperparameter optima or authority to keep enlarging the search. Unit-L2 is especially close to the already normalized CLIP representation; equal nominal grids do not mean identical effective search diversity across encoders.

The strong g_domain CLIP AUROC0.977420 is a within-source held-out-group result under three-source fitting, not unseen-domain performance. Primary0.844040 is the relevant domain-transfer screen. Do not promote the larger number as the main generalization result. Lower CLIP Brier is a probability-scoring observation, not evidence of universally better calibration or classification.

## Operating-point accuracy is still not adequate

At the source-calibration APCER<=5% reference thresholds, primary descriptive original-denominator FA/non-acceptance means are9.97%/53.94% for supervised CLIP and35.07%/17.88% for selected two-DINO. The former still rejects over half of bona-fide inputs; the latter accepts too many attacks. On held-out OULU source rows, selected two-DINO FA is67.31%. CASIA CLIP AUROC0.966878 coexists with66.39% bona-fide non-acceptance. No source threshold constraint has transferred as a target security guarantee.

Compared with the old two-DINO recipe, selected two-DINO improves BA but increases mean original FA from33.83% to35.07% while reducing bona-fide non-acceptance. This is a tradeoff, not an unqualified accuracy/security gain. Preserve successful ACER separately from original-denominator failure effects. The new field operational_acceptance_coverage is the **accepted fraction**, not301's coverage including covered spoof decisions; do not compare those differently defined percentages as one utility metric. Error-overlap counts likewise are not a class-balanced fusion objective.

## Interpretation and next bounded decision

The study answers the immediate supervised-readout question positively for CLIP versus its own zero-shot baseline, negatively for replacing the two-DINO ranking baseline, and leaves deployment utility unresolved. Twelve overlapping contexts and unadjusted conditional intervals are not twelve independent replications, a joint mean interval or retraining/new-domain uncertainty. Source-only development after observing301 remains exploratory even with careful new OOF splits.

Keep the old geometry/cache, old two-DINO baseline and this supervised CLIP branch as separately versioned results. Do not rerun extraction, geometry, the readout grid or old target evaluation. Do not automatically proceed to backbone fine-tuning or select a favorable candidate from the newly public held-out candidate tables.

If the owner chooses one further source experiment, the concrete next question is **incremental supervised-CLIP fusion value under a declared operating utility**, not merely whether CLIP's own AUROC rose. Prepare a compact group-safe nested protocol: shared DINO anchor, old/selected two-DINO comparators, fixed convex weights including zero CLIP, exact source-domain aggregation and security/usability constraints, deterministic ties and all selection steps inside the held-out pipeline. Select by the intended source-transfer/operating objective; do not assume that within-domain BCE will choose the best unseen-domain model. If risk supervision is included, cross-fit head/calibration/fusion selection before generating error labels. Reuse cached features and keep observed targets out of method selection claims.

No new fit is authorized by this review. Publish the concrete protocol/resource scope first and request one execution decision if needed; if no added utility is found, stop forcing heterogeneous fusion. Independent confirmation of any revised method still needs genuinely unseen authorized data. Completing a clear exploratory negative/limited-gain report is preferable to indefinite searches for a favorable number.

**309 is a useful successful screen: supervised CLIP works much better than zero-shot, but two-DINO remains the stronger source-ranking baseline and operating transfer is still the main unsolved issue.**
