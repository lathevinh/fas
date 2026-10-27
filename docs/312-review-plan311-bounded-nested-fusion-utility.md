# 312 - Review of plan311: one bounded nested-fusion utility study

Date: 2026-10-27
Reviewed commit: `c8a33ce05777eb26f69ae8ecf89f78d122b925a9`
Basis: [309](309-source-only-cached-readout-results.md), [310](310-review-doc309-supervised-cached-readout-results.md), [311](311-next-stage-cached-pad-research-plan-for-review.md).

## Decision and direct answers

**Accept311's direction as a planning basis, with the concrete decisions below incorporated into the executable package before new fits. Choose F1 as the next scientific question; include a small saved-output D0 section in that same package. Do not make D0 a separate mandatory review round or launch optional S1 first. This review is not execution authority.**

The completed readout study already shows that lower inner BCE need not improve held-out-domain AUROC. Falling validation tails do not establish that another solver or longer head run will change the fusion decision. S1 is a legitimate separate exploratory question, but currently adds scope rather than answering whether supervised CLIP helps. Keep its hypothesis parked unless F1 preparation exposes a specific numerical inability to fit the declared branches, not merely a disappointing metric.

The proposed old DINO-Reg anchor, frozen309 supervised-CLIP recipe, fixed/selected two-DINO references and matched-selector two-DINO control are appropriate. Keep the six proposed weights and zero-CLIP endpoint. Treat5% FA/50% bona-fide acceptance as explicit **exploratory empirical utility criteria**, not established product requirements or a deployable security standard. Do not change to1% solely to sound stricter; it requires a different support/precision plan. Nested domain-held-out selection is the right construction, but the feasibility, support and decision details below are necessary to make it executable.

## Strengths and evidence boundary

311 preserves source populations, old geometry/caches, original failures, the strong DINO baselines and all301 conclusions. It correctly recognizes that a learned heterogeneous weight beating a fixed average would confound selection opportunity with branch diversity; the matched-selector control addresses that. It also correctly requires refitting missing inner contexts rather than selecting weights from309's already evaluated OOF table.

The new validation-tail summaries are reported private-history observations, not a new independently reproduced numerical result. Their source hashes can anchor provenance, but public summary values do not reproduce those calculations. Even a4.34% tail BCE decline for CLIP does not establish gradient stationarity, target transfer or authority to extend the old run. The precise old/supervised source means and operating failures agree with the accepted309 report. No new model execution or performance improvement is present in311.

## 1. Keep D0 finite and inside the package

Use saved coefficients/predictions to generate only the needed source-by-class score/threshold tables and a small deterministic set of plots. Bind their inputs and distinguish final/g_domain from pseudo-domain-held-out results. Include the already reported validation tails; do not recreate the entire309 search or ask for another review merely to restate its averages.

D0 may explain score shifts and show feasibility/support obstacles, but should not adaptively choose a new lambda grid, head recipe, normalization or evaluation endpoint. Diagnostic curves remain descriptive; do not pick a threshold from the curve of the same held-out domain later used to claim utility. The allowed preparation is executable code/tests and existing-data inventory; private diagnostic execution still follows applicable existing authority. Avoid chaining separate approvals for ordinary parts of the same bounded package.

## 2. Declare what policy actually transfers

For each mixture weight, derive its classifier threshold only from the permitted calibration role under one fixed rule; retain attack-high/tie-is-attack and original class denominators. Inner held-out source labels evaluate that full fitted/calibrated/thresholded pipeline and choose the **weight**. They must not also calibrate or choose the threshold of the model being evaluated on those labels.

After weight selection, refit/select/calibrate the fixed branch recipes only on the allowed remainder and apply the chosen weight with the newly allowed-source threshold. That final threshold may differ from those used in inner evaluations. Record all memberships and mappings explicitly: an inner lambda feasible on one-source-trained models need not remain feasible for a two-source-trained model on the next unseen source. That failure is a substantive outcome, not a reason to choose another weight using evaluation labels.

For final/g_domain evaluation, select on internal source holdouts and keep g_domain untouched by head/weight/threshold selection. The domain-OOF and final/g_domain populations answer different questions and must be reported separately. Check source-group/exact-frame connected components for **every** new one-source inner train/validation/calibration/evaluation split before fitting. Do not fall back to within-domain validation if an inner source fold is infeasible.

## 3. Specify support and infeasibility before fitting

Inventory original/usable bona-fide and attack counts, independent registered groups and failure counts for every inner fold/domain. Publish the exact empirical rate granularity and minimum support rule. Risk-model error-count>=20 from earlier work is not a suitable substitute for original attack/bona-fide support in an operating-policy study. At5%, sample size determines how many errors are allowed and how coarse the feasible threshold set is; correlated frames/videos/subjects also affect precision.

For the first exploratory study, keep selection explicitly empirical and attach group-resampled conditional uncertainty for reporting rather than silently turning the5% point condition into an unplanned confidence-bound constraint. If uncertainty/support is to gate eligibility, state exact minimum groups/counts, valid-replicate rule and what is unestimable in the plan. Low estimated FA from few independent groups must not be called a validated security rate.

If no lambda is feasible in inner selection, write no_candidate_meets_declared_utility and produce no selected useful operating policy. Keep candidate diagnostics and original failure accounting. Do not silently substitute an unconstrained winner, remove the context or count a reject-all fallback as success. If a fail-safe reject-all action is needed for software completeness, label it separately from a selected useful policy and count it as utility infeasibility.

If a selected policy subsequently violates5% FA or50% bona-fide acceptance on the outer held-out source, retain that result as transfer failure. Do not retrospectively label it inner-selection infeasibility, retune or drop it. Separate these two outcomes in the output schema and aggregate denominator. Predeclared worst-source validation is more important than finding a favorable average.

## 4. Turn incremental benefit into one explicit decision rule

Primary comparator should be the **matched-selector two-DINO system**, with D-only and fixed old/selected two-DINO kept as visible references. Select each family independently under the same inner utility; do not choose between families on the evaluated held-out rows and report that choice as an untouched comparison. A positive selected CLIP weight is not itself evidence of benefit.

Before execution, state an exact held-out utility estimand and aggregation: per-domain original attack FA and bona-fide acceptance, worst-source values, equal-source/seed descriptive summaries, selected-policy feasibility rate and outcomes of every infeasible fold. Retain acceptance fraction and ranking metrics as secondary, not substitutes for the50% bona-fide condition or301's differently defined operational coverage.

Recommended exploratory retain-CLIP screen: require held-out empirical security/usability feasibility and an improvement in the declared worst-source bona-fide acceptance over both D-only and matched-selector two-DINO. Pick a minimum practically relevant gain before fitting; **two absolute percentage points** is a concrete working margin, not an inferred product requirement. Report paired conditional intervals for the chosen scalar and no-worsening checks on other sources. Describe overlapping-context aggregation and any multiple comparisons honestly; neither majority-of-seeds nor twelve correlated positive point estimates is an independent significance test.

If the package instead chooses a different margin or formal interval predicate, justify it before execution and keep it fixed. With no defensible utility margin, limit the claim to a descriptive exploration and do not call a tiny favorable difference a practical success. If all families fail feasibility, the correct conclusion is that this fixed family of policies does not solve source transfer; do not immediately relax constraints or launch S1.

## 5. Preserve attribution and realistic scope

Using the old DINO-Reg branch avoids replacing a stronger established anchor with309's worse selected Reg. Selected two-DINO is still useful as an additional performance reference, but it is not a branch-matched causal control. The matched selector matches weight-selection opportunity, not head-training information, feature dimension or encoder latency. Report those distinctions and any extra CLIP deployment cost before claiming an advantage.

Do not add risk fits, G2, prompts, backbone tuning or an expanded readout grid to F1. Do not mine existing held-out candidate tables to choose the branch recipe again. The approved question can end in zero CLIP weight or no useful policy.311's observed datasets remain development data; a source-only positive result would still need an independent locked target before generalization claims.

## Concrete next deliverable

Implement one F1 package with the compact D0 appendix: exact split/support inventory, fixed weight/threshold algorithms, feasibility and gain predicates, candidate/model/policy provenance, no-feasible/evaluation-failure schemas, unique fit/reuse counts, synthetic tests and profiled resource/stop rules. Preserve all old results and reuse only exactly matching cached fitted states. The proposed6h/4GiB/1GiB envelope is not yet validated for this nested workload; count inner fits/calibrators and publication artifacts first. Bound single-attempt execution and saved-output reconstruction; do not rerun309 wholesale.

The owner can then make **one decision on that concrete execution package**, using existing explicit authority when it actually covers the scope. No execution is authorized by311 or this review. No new D0-only review, S1 campaign, target evaluation or dataset/image preparation is required to prepare it.

**Proceed with one bounded nested-fusion utility package, not another open-ended readout search. Its value is answering whether supervised CLIP adds useful operating performance over a fairly selected two-DINO control, including the possibility that it does not.**
