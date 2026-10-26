# 300 - Review of299: complete source evidence and analysis freeze

Date: 2026-10-26
Reviewed commit: `38ba0ec7a32db2d3cdafeed7d794b11c07c18d14`
Governing review: [298](298-review-doc297-first-source-fitting-and-oof-results.md).

## Decision

**DOCUMENT299 ACCEPTED WITHOUT REWORK for the completed fixed source experiment, source competence/applicability evidence and immutable source-analysis baseline. All twelve registered outer-target/seed combinations are present. Review298's source-completion requirement is closed. Do not interpret prerequisite eligibility or analysis freeze as a successful scientific hypothesis or locked-target execution authority.**

The primary heterogeneous source comparison is consistently unfavorable to domain-OOF, including the fit-size control. Accept that negative result. Do not repeat or tune the source experiment to reverse it. All four data milestones,295 integration/pilot and297's first result remain closed and preserved.

## Verification and CI

Reviewed report299, plan/config/run/closure, canonical source evidence, freeze record, experiment/diagnostic/closure code and freeze/validator changes. Exact final-head GitHub [run40303622261](https://github.com/lathevinh/fas/actions/runs/40303622261), [validate121507233886](https://github.com/lathevinh/fas/actions/runs/40303622261/job/121507233886) concludes success for all12 listed steps including Complete job. This is replacement-head success, not relabeling the earlier987bca5 failed CI. The reported fixture-only repair leaves pinned source artifacts unchanged.

Locally ran seven actual model-free299 regression cases: all passed. Coverage includes group-preserving budgets, weighted/tie-stable AP/AUROC, cluster multiplicities/competence uncertainty, paired intervals/one-class support, no-quality dimensions and rejection of corrupted saved head/prediction evidence. Numerical fitting, GPU execution, private source closure and the full471-test suite were not rerun on this host. The producer's471-test run and exact-head CI are separate evidence.

Independent checks passed for twelve unique outer-target/seed combinations,480 risk records, complete-system competence and claim states, all primary negative heterogeneous intervals, feature reuse/coverage, config/closure hashes, both source-evidence hashes and every one of147 freeze-pinned artifact hashes. Text hashes were normalized to Git LF on this Windows checkout. The freeze creation commit is an ancestor of HEAD; pinned paths have no Git changes since creation. This verifies the published immutable source baseline, not the unavailable private model/array contents.

Private inputs, approvals, model states, prediction tables and images remain unavailable here. Actual private execution, optimization and reconstruction are bounded producer-reported evidence supported by public aggregates and reviewed software. Technical hashes are not visual adjudication or independent scientific replication. No target predictions or new private-media replay was performed for this review.

## What is now complete

The experiment covers four outer-domain rotations and three seeds. Each outer target is wholly excluded from its own fitted/source-prediction context; images used as sources in other rotations do not turn those into target evaluations. Fold-local successful input counts are1906/6261/6583/5815 for outer OULU/CASIA/MSU/SiW respectively. These overlapping populations must not be added into distinct-original counts.

The frozen-feature union is6855 successful source images per backbone, with6882 failure-inclusive source-use originals and27 retained failures. It reuses1906 cached rows per backbone and adds4949 OULU rows only for rotations where OULU is a source:14847 new forwards, no new text/weight/video/detector campaign. FP32 feature payload98273280 bytes reconciles.

New work comprises274 DINO heads,411 calibrators,456 logistic risk models and48 domain-identifiability models. Preserved297 contributes14 heads,21 calibrators and24 risk models:288 distinct head states,432 calibrators and480 risk models overall. Identical budget contexts reuse primary state rather than count as fresh optimization. Saved-output closure reportedly reconstructs171612 context prediction rows, not171612 unique originals, with no additional inference or optimization.

Source role, outer/pseudo-target and group/exact-frame separation remain explicit. All required fit-size, no-quality, disagreement, domain-identifiability, OOF/final-drift and conditional clustered uncertainty outputs are now present. Canonical competence/applicability artifacts cover all twelve combinations; schema/data-audit/source-dry-run return zero errors in the reported private normal execution. Passing these validators means the required evidence is present and conforms, not that the preferred method wins.

## Main scientific finding: unfavorable source evidence

All twelve heterogeneous primary R_DVd contrasts have domain-minus-sample AP below zero with paired95% clustered intervals entirely below zero. Their point differences range approximately-0.348 to-0.138 AP. The fit-size sensitivity retains negative point differences in all twelve and negative intervals in eleven, one inconclusive. Smaller branch-fit pools therefore do not explain away the observed direction, although whole-group residual size differences and composition prevent a perfectly isolated causal interpretation.

Representative first-seed primary AP values are:

| Outer target excluded | Domain-OOF | Matched sample-OOF | Difference |
|---|---:|---:|---:|
|OULU|0.3168|0.6212|-0.3044|
|CASIA|0.2576|0.3959|-0.1383|
|MSU|0.2288|0.4286|-0.1998|
|SiW|0.1673|0.3439|-0.1766|

These APs rank actual errors of the same final classifier on its held-out source g_domain rows. They are not PAD accuracy or results on the named outer target. The first-seed examples illustrate the complete twelve-row evidence; they must not replace the full table in final scientific reporting.

Same-family primary comparisons have three supported negative intervals, four inconclusive outcomes and five underpowered outcomes, with no supported positive. Keep the low-error results visible. Shared examples across seeds/rotations mean twelve rows are not twelve independent replications; no simple binomial sign-test or unqualified pooled significance claim follows. Intervals are conditional on saved predictors, not uncertainty from retraining the full algorithm; exploratory contrast counts are not multiplicity-adjusted discoveries.

Standalone OpenCLIP fails competence in every combination: source macro BA is around0.50 and AUROC around0.53-0.58. The DINO anchor and both complete pairs pass their registered source prerequisites in every combination. Under the explicit claim dependency rules, a weak standalone branch does not automatically disqualify the complete pair. Conversely, the pair's competence does not establish cross-foundation benefit or erase the standalone failure. Do not replace prompts, polarity, backbone, risk vector, epoch budget or seeds based on these results.

The diagnostic story is coherent but not causal proof: domain remains readily identifiable from risk vectors (heterogeneous held-out domain BA0.7045-0.8615 versus chance1/3), and overall score/disagreement KS drift reaches0.5479 for domain-OOF versus0.2280 for sample-OOF. The final reference is in-sample; these are distributional diagnostics, not held-out competence or proof that drift causes the AP deficit. Quality drift is zero by construction under the shared-statistics convention.

Removing quality does not produce a domain-OOF win. Quality's added benefit is mixed/inconclusive, while the fixed no-quality disagreement increment has positive intervals in11/12 domain-OOF and12/12 sample-OOF heterogeneous contrasts. That supports a limited source diagnostic about explicit disagreement, not a rescue of the primary domain-OOF hypothesis or a license to select a new primary vector.199/288 heads select the fixed epoch200 endpoint; preserve the fixed-budget result without claiming convergence.

## Freeze is a source baseline, not permission to run targets

The freeze CLI correction is justified: committing a record should not invalidate unchanged pinned artifacts. The revised ancestor-plus-pinned-diff/current-hash/clean-tree checks preserve creation identity and reject changes to the frozen inputs. Current public hashes and ancestry agree with the record created from14b29a4. Historical execution receipts correctly retain their pre-freeze pending fields; the later immutable record establishes the new state.

The actual run still reports gate_selected=false and locked_evaluation_authorized=false. No target RQ1/RQ2 verdict exists. Accept source completion and the current source baseline; do not advertise a complete executable target-evaluation release until the evaluation implementation, operational source-selected k1 policy and exact fitted-artifact bindings have been prepared and checked. The primary risk-ranking/AURC endpoints and secondary operational policy must remain separately scoped.

The published freeze pins its explicit147-path map and source evidence, not every arbitrary private file or every future script. The next execution manifest must additionally bind actual training/extraction configs, checkpoint identities, selected fitted heads/calibrators/risk models, target population/masks, source thresholds, exact policy/evidence and evaluation code. Preserve the current freeze unchanged. If implementing the evaluator changes freeze-covered code or adds files covered by artifact discovery, use the normal versioned successor-freeze procedure before target prediction; never overwrite the old record or pretend changed code matches it. No source training or image campaign needs repeating solely for that publication step.

## Next concrete package

Prepare the **locked-evaluation implementation and complete execution manifest** now, using saved models/features and synthetic fixtures. Implement registered RQ1 error AP, RQ2 class-balanced raw AURC, paired subject/video clustering, three-seed/four-target aggregation, eligibility/support states and technical-failure denominators exactly as specified. Exercise insufficient-event and harmful/inconclusive outcomes, not just success paths. Complete/bind any source-only k1 selection required for secondary operational endpoints using saved source data; do not choose a risk variant or gate from target outcomes.

Seal the evaluation package, all necessary source-selected policies and any required successor freeze before asking once for the typed locked-evaluation authority. That authority must name the exact frozen package, target scope, resources and stop rules. Until then, prepare/test with saved source or synthetic records only. Readiness checks and freeze creation are not human execution approval.

After explicit authority, execute the fixed target evaluation and report all outcomes, including evidence against the hypotheses, inconclusive/underpowered cases and standalone failure. Do not add another source-confirmation loop, change the experiment to manufacture a favorable result or rerun twelve unchanged source combinations. A negative research outcome can still be a complete, valid experiment.

**The full source experiment is accepted and its main result is negative for domain-OOF. Next work is a concrete, frozen and explicitly authorized target-evaluation package; the target scientific verdict remains open.**
