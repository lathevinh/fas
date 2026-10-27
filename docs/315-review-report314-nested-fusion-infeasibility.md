# 315 - Review of314: completed nested fusion and operating infeasibility

Date: 2026-10-27
Reviewed commit: `518c223925454ff59d8434aef9bbb2c286589e08`
Execution package: [313](313-bounded-nested-fusion-utility-execution-package.md).
Prior planning review: [312](312-review-plan311-bounded-nested-fusion-utility.md).

## Decision

**Accept313/314's completed bounded nested-fusion experiment, saved reconstruction and explicit no-policy outcomes. Neither selector found a useful policy under the declared source-transfer utility. The selected-fusion incremental gain is unestimable, not zero and not a measured CLIP-versus-DINO defeat. Do not relax constraints, insert a fallback winner or automatically launch another scientific campaign.**

This closes312's F1 question for the fixed branches, six weights, calibration-derived thresholds and5%/50% empirical utility. It does not prove that all possible heterogeneous models, thresholds or PAD methods are infeasible.299/301/305/309, their scopes and previous negative/mixed findings remain unchanged. No new target or risk-gate model was evaluated here.

## What the experiment actually tested

The anchor is the old299 DINO-Reg readout. The added branches are309's fixed supervised CLIP recipe or the original plain DINO. Each family has the same six convex weights, including zero and one; fixed individual/equal systems and selected two-DINO references remain visible. New inner fits use cached features only, with group/exact-frame safety and no encoder changes.

Each complete domain-OOF evaluation excludes the outer dataset and pseudo-target source from fitting/selection/calibration. Weight selection uses new inner source holdouts inside the remaining sources. A candidate's classifier threshold is derived on its allowed calibration role, not selected from the held-out labels on which utility is measured. Final/g_domain evaluation also keeps g_domain out of weight/head/threshold selection. This prevents reusing309 evaluation labels to choose and score the same fusion.

Selection requires attack FA<=5% and bona-fide acceptance>=50% on **every** inner held-out source, with original denominators. Only feasible weights can compete by worst-source bona-fide acceptance and declared ties. This is an empirical operating screen, not a population-security certificate. The current fitting/validation/calibration support floors pass but are modest; passing them does not establish precise low-FA transfer under arbitrary domain shift.

Reported work is42 unique core pipelines,36 new heads/36 calibrators,90 reused core heads/calibrators,108 unique prediction tasks and492 unique threshold policies. Thirty unique selector instances per family yield60 family selections and360 family/selector/weight candidates. All12 outer-exclusion/seed combinations are covered. Scientific execution plus separate saved reconstruction completes once in36.05 seconds, with zero encoders/new targets. Private resource observations and execution were not independently replayed here.

## Verification

Reviewed313/314, config/plan/aggregate receipt, split/support/selection/summary code and regression definitions. Exact final-head [run40482817286](https://github.com/lathevinh/fas/actions/runs/40482817286), [validate122117110821](https://github.com/lathevinh/fas/actions/runs/40482817286/job/122117110821) concludes success for all12 listed steps, including the numerical regression suite, schema and stage checks. The reported scientific package CI/538 local tests are separate from this final publication check.

Nine actual repository fusion-contract tests passed locally using the actual fusion module and extracted test class. Coverage includes connected components, original failure denominators, score/threshold ties, worst-source/tie selection, explicit infeasibility, insecure high-acceptance rejection, practical gain and complete-fold handling. No numerical head/calibrator fitting or full controller suite was run on this host.

Independent public checks passed for all plan code pins, plan/terminal/reconstruction bindings, all60 selector results, all360 candidate FA violations and recomputation of both36-fold summaries using the actual select_weight/summarize functions. This supports the published arithmetic and outcome semantics, not access to private models, approvals, labels or coefficients. Actual fitting, prediction reconstruction, reference parity and bootstrap remain bounded producer-reported evidence. Technical checks are not independent scientific replication or visual adjudication. The report's independent reconstruction is a separate producer process, not an external replication by this reviewer.

## Main result: operating transfer, not the BFA floor alone, blocks selection

Every one of360 candidates breaches5% attack FA on at least one inner held-out source. Some also breach50% bona-fide acceptance. Therefore lowering only the usability floor would not make this same candidate/threshold family feasible. Zero added-branch weight also fails, and the matched two-DINO family fails as well; the finding cannot be assigned solely to adding CLIP.

Neither family selects a weight in any of30 unique selectors. Consequently both have missing selected policies in all36 primary source-level evaluation folds and all36 separate g_domain folds. Missing policies are correctly not scored as reject-all policies with artificial zero FA, not replaced by a favorable fixed mixture and not omitted from the denominator. The predeclared two-point gain and its interval are undefined because the required policies do not exist.

The fixed references still have defined calibration-derived policies and can be evaluated:

| Fixed/reference system | Primary folds meeting5% FA and50% BFA | Folds failing transfer |
|---|---:|---:|
|DINO-Reg alone|4/36|32/36|
|Plain DINO alone|6/36|30/36|
|Supervised CLIP alone|1/36|35/36|
|Fixed equal original two-DINO|6/36|30/36|
|Inherited selected equal two-DINO|6/36|30/36|
|Fixed equal DINO-CLIP|6/36|30/36|

These small feasible subsets do not justify choosing the fixed50/50 mixture post hoc or calling equal counts equal performance. The fixed policies are descriptive references, not successful outcomes of nested selection. Also, this experiment did not exhaust all possible thresholds: it tests six weights **with the specified source-calibration threshold rule**, not the existence of any point on an arbitrary held-out ROC curve. Do not pick a held-out threshold afterward and relabel that as source-only success.

## D0 diagnosis is consistent with the failure, not a causal explanation

The source-held-out OULU DINO attack margin shifts from positive calibration score-minus-threshold to negative held-out margin. CASIA/OULU CLIP bona-fide margins shift in the opposite harmful direction, from below to above the threshold. These descriptive, nested medians document score/threshold transfer problems. They do not prove that another solver, normalization, epoch count or gate would repair them.

Per-source averages preserve the practical cost: DINO-only FA is approximately50.54% on held-out OULU and42.53% on MSU; CLIP-only bona-fide acceptance is approximately33.61% on CASIA and38.03% on OULU. Means are explanatory, while the registered pass rule applies per fold/source. All are source-development results, not new independent target measurements or a directly matched published benchmark result.

Within-source g_domain reference performance is much better (DINO-only feasible36/36), but both selectors still have missing policies because selection correctly refuses to use g_domain labels. The source holdout versus g_domain contrast is a useful warning about domain transfer. It does not authorize choosing weights on g_domain or replacing the primary population with the easier pool.

The unchanged-reference audit reportedly covers61695 repeated successful rows and246780 score/threshold/action comparisons, with differences at floating-point roundoff and exact action equality. This is appropriate evidence that the old anchors were not silently degraded. These repeated rows/overlapping folds and shared selectors are not independent replications. Conditional component-bootstrap validity cannot create a gain interval where the selected policies are absent.

## Consequences for the research decision

This does **not** show that supervised CLIP lacks information:309's strong improvement over zero-shot still stands. It shows that useful AUROC/readout competence and convex averaging are insufficient to deliver this worst-source operating utility. No downstream risk gate was fitted here, so314 cannot claim to have tested whether risk filtering helps. Under the accepted live-only non-accept gate, adding a gate could lower FA only by preserving or decreasing bona-fide acceptance; it would not rescue an already low BFA by reaccepting rejected bona-fide samples.

Keep missing-policy, defined-but-failing-transfer and unsupported-statistical-certification states distinct. The5%/50% criterion was an adopted exploratory objective, not a universal definition of a good PAD system. Failure under it is informative and valid; relaxing it after seeing universal infeasibility would answer a new question. No new S1 optimizer, wider weights, target calibration, prompts or fine-tuning follows automatically.

## Next deliverable

Close this fixed F1 study as negative utility evidence and incorporate it into the final source-development/reproducibility report, alongside301,305 and309. Include all candidate failures, missing-policy denominators, fixed-reference tables, source/g_domain contrast, support inventory, exact calibration rules and the distinction between weak zero-shot CLIP and useful supervised embeddings. Preserve final CI and execution/reference-parity/reconstruction provenance.

Do not rerun the selected-fusion screen or create another confirmation checkpoint. If the owner wants a different method/policy family, prepare one separately specified exploratory proposal explaining which failure mechanism it targets and why it is worth testing; retain the existing results and require independent data for revised generalization confirmation. A proposal for such a study is optional, not an unfinished requirement of this completed experiment.

**314 is a completed, correctly reported infeasibility result. The declared nested fusion family has not yielded a useful transferable policy; further incremental benefit is not measurable here, and another automatic search is not justified.**
