# ChatGPT Review — Document 42: Data-to-Experiment Implementation Plan

Date: 2026-09-18  
Repository: `lathevinh/fas`  
Reviewed file: `docs/42-data-to-experiment-implementation-plan.md`

## Overall verdict

The document is technically mature and is close to being a usable execution blueprint.

I do **not** recommend changing the architecture or expanding the first-paper scope.

However, several protocol details should be corrected before the document is treated as frozen. Four issues are particularly important:

1. the definition of immutable dataset roles conflicts with the stated fold-dependent role builder;
2. the "sealed target labels" language is stronger than what four-fold MICO can actually guarantee;
3. classifier threshold selection may currently reuse calibration data too aggressively;
4. the custom one-frame primary protocol may weaken comparability with published cross-domain FAS work unless the benchmark-compatible track is elevated.

The remaining comments are mostly clarifications that would make implementation and manuscript interpretation safer.

---

# 1. Major issue: immutable dataset roles and fold-dependent role assignment contradict each other

Section 2 states:

> Subject/video roles are assigned once per dataset and reused whenever that dataset is a source.

This is a strong and clean rule.

However, Section 6.2 later states that the role builder is deterministic given:

> dataset release, role-policy version, outer target, and seed.

It also says that for outer fold \(T\), the role builder may perform a feasibility pass using the three current source domains.

These two formulations are incompatible.

If role assignment depends on:

\[
T,
\]

then the same CASIA subject may be:

- `source_train` when OULU is target;
- `branch_calibration` when Replay is target.

That is not "assigned once per dataset".

## Recommendation

Prefer the simpler global interpretation.

For every dataset \(D\), create one immutable source-role manifest:

\[
R_D:
subject/video
ightarrow
\{
source\_train,
branch\_calibration,
gate\_domain,
routing\_validation
\}.
\]

This assignment depends only on:

- dataset release;
- official source-eligible partition;
- role-policy version;
- frozen split seed.

It does **not** depend on outer target.

Then reuse the same manifest whenever \(D\) acts as a source.

The outer fold only decides:

\[
	ext{which three dataset manifests are visible}.
\]

If a dataset is too small to support the global role split, revise the role policy **globally before any target evaluation**, rather than creating different role manifests per target fold.

This change substantially simplifies lineage auditing.

---

# 2. "Target labels are sealed" is too strong for four-fold MICO

The document states that target labels are sealed for outer target \(T\), while the same dataset may expose labels through a separate source namespace when it is a source in another outer fold.

This is technically possible at the command/API level, but it does **not** mean the research team has never seen those labels.

Example:

- in fold `T_oulu`, OULU is the target;
- in folds `T_casia`, `T_replay`, and `T_msu`, OULU is a labeled source.

Therefore OULU labels cannot be globally hidden from the researchers throughout the full experiment.

This is normal for leave-one-domain-out evaluation.

The important constraint is not:

> nobody has ever seen target-dataset labels.

It is:

\[
oxed{
	ext{the target dataset cannot influence any fitted artifact for the fold in which it is target}
}
\]

## Recommendation

Replace absolute "target sealing" language with **fold-local exclusion**.

For target \(T\):

- no sample from \(T\) may enter branch fitting;
- no \(T\) label may enter branch calibration;
- no \(T\) statistic may select threshold/hyperparameters;
- no \(T\) record may enter OOF/risk training;
- no result from \(T\) may modify the globally frozen method.

This is exactly what MICO requires and is easier to defend.

The access-controlled namespace remains useful as an engineering safeguard, but it should not be described as proof that the dataset labels were never visible elsewhere.

---

# 3. All four folds can be strict outer-domain evaluation, but "confirmatory" should be used carefully

The current plan treats all four MICO targets as confirmatory.

That is defensible only because:

- the architecture;
- VLM checkpoint;
- prompts;
- feature definitions;
- analysis rules;

are frozen before any target result.

However, because every dataset also serves as a labeled source in other folds, this is closer to a **pre-specified leave-one-domain-out evaluation** than four independent external confirmations.

## Recommendation

In the manuscript use:

> four strict outer-domain-held-out MICO folds

rather than repeatedly emphasizing:

> four independent confirmatory domains.

The four-target macro is still valid as an aggregate over the evaluated folds.

But its confidence interval should not be interpreted as uncertainty over a population of all possible real-world domains.

---

# 4. Source threshold selection in Section 9.1 needs one more explicit partition rule

Section 9.1 currently does:

1. fit branch calibrators on `branch_calibration`;
2. produce calibrated source predictions;
3. select the reference classifier threshold using a source-only operating-point rule.

It is not fully explicit **which records select the threshold**.

If the same `branch_calibration` records are used both to fit:

\[
(a_D,b_D),(a_V,b_V)
\]

and select:

\[
	au_{ref},
\]

the source operating point is somewhat optimistic.

This is not target leakage, but it matters if the paper claims a source-certified APCER constraint.

## Recommendation

Define one of these approaches explicitly.

### Option A — separate threshold subset

Split `branch_calibration` into:

\[
calibration\_fit
\]

and:

\[
threshold\_selection.
\]

This is statistically clean but costs data.

### Option B — cross-fitted source threshold estimation

Fit calibration on folds and generate calibrated out-of-fold source predictions for threshold selection.

This uses data efficiently but adds complexity.

### Option C — accept joint calibration/threshold fitting

If source datasets are too small, explicitly state:

> branch calibration and source operating-point selection share the source calibration partition; therefore the threshold is source-optimized, not an independently validated security guarantee.

For a Q3 paper, Option C may be acceptable if the wording is honest and low-APCER claims are conservative.

But the current document should choose one.

---

# 5. Strong issue for publication: exact MICO protocol mapping is still underspecified

Section 6.1 says:

> Where publications use a recognized cross-dataset convention, match that convention and document any deviation.

This is too open for a frozen research plan.

Cross-dataset FAS comparison depends strongly on exactly which official partitions are used from:

- OULU-NPU;
- CASIA-FASD;
- Replay-Attack;
- MSU-MFSD.

## Recommendation

Add a frozen table:

| Dataset | Source-eligible official split(s) | Target evaluation split | Literature convention |
|---|---|---|---|
| OULU-NPU | ... | ... | ... |
| CASIA-FASD | ... | ... | ... |
| Replay-Attack | ... | ... | ... |
| MSU-MFSD | ... | ... | ... |

This must be resolved from the protocols used by the closest cross-domain FAS papers.

Without this table, the eventual numbers may be difficult to compare fairly with FLIP, CA-FAS, DINO-VPT, VFM benchmark, etc.

This is more important than adding another model ablation.

---

# 6. The strict single-frame protocol is scientifically valid but cannot replace benchmark comparability

The plan uses one deterministic 50% frame per video as the strict primary evaluation.

That is appropriate for the paper's single-image deployment claim.

However, much of the FAS literature uses dataset-specific frame/video evaluation and aggregation.

If the paper's headline performance tables only use the custom one-frame protocol, a reviewer may say:

> the method cannot be compared directly with existing cross-domain FAS results.

The document already includes a benchmark-compatible track, but labels it secondary.

## Recommendation

Use **two co-existing main evaluation tracks**.

### Track A — literature-compatible MICO

Follow the established protocol exactly.

Purpose:

- compare with prior work;
- validate classifier competitiveness.

### Track B — strict single-image

One deterministic frame per video.

Purpose:

- validate the actual research setting;
- run the clean failure-risk/selective analysis.

The novelty table can remain Track B.

But the paper needs a visible Track-A table to establish external comparability.

I would not bury benchmark-compatible results as a minor appendix.

---

# 7. The gate action should be written explicitly as a live-decision filter

Under \(K=1\):

- predicted spoof = terminal non-accept;
- abstain = terminal non-accept.

Therefore applying an abstention gate to an already predicted-spoof sample cannot improve end-to-end access control.

The meaningful policy is:

\[
	ext{if }g_{ref}(x)=spoof
\Rightarrow
non\text{-}accept,
\]

and:

\[
	ext{if }g_{ref}(x)=live:
egin{cases}
accept,&r(x)\le u\\
abstain/non\text{-}accept,&r(x)>u.
\end{cases}
\]

## Recommendation

Put this exact action rule into Section 9.5 or 11.5.

Risk ranking can still be evaluated on all classifier errors.

But end-to-end selective utility should make clear that the gate operationally filters **live decisions**.

This removes ambiguity around coverage and avoids meaningless abstention of spoof decisions.

---

# 8. RQ1 overall error AP and security utility should remain separate

The main RQ1 endpoint:

\[
AP(e_{DV},r)
\]

uses all prediction errors:

- false accepts;
- false rejects.

That is reasonable for failure-risk transfer.

But security utility under the K=1 gate depends mainly on identifying dangerous **live decisions**, especially attack false accepts.

Therefore a model could improve overall error AP mainly by detecting false rejects without providing much security benefit.

The document already separates selective utility, which is good.

## Recommendation

Keep the hierarchy explicit:

### Methodological endpoint

\[
AP_{error}
\]

tests failure-risk transfer.

### Security-specific support

Also report one of:

\[
AP_{FA}
\]

or false-accept risk ranking among the relevant attack/live-decision population.

### Deployment endpoint

\[
FA_{end2end}
\]

versus:

\[
BFNR_{end2end}.
\]

Do not let a false-reject-driven AP gain be described as a security improvement.

---

# 9. The quality-feature normalization rule still needs precision

The plan says only quality features are standardized using allowed source-fit statistics.

The quality vector is:

\[
q=
[
blur,
luminance,
contrast,
face\ area,
detector\ confidence
].
\]

For domain-OOF records, there are two possible choices.

### Fold-local normalization

Use statistics from the two allowed fitting domains.

Pros: no held-out-domain leakage.

Cons: OOF records from different folds live in slightly different normalized coordinate systems.

### Global source normalization

Use statistics from all three source domains.

Pros: common coordinate system.

Cons: held-out pseudo-domain statistics leak into its own OOF representation.

## Recommendation

Prefer fold-local normalization for OOF generation and final-source normalization for target inference.

Then explicitly state that risk training receives fold-relative normalized nuisance variables.

Run a simple sensitivity using **unstandardized physically bounded/defined quality features**.

This is especially important because the primary claim is about domain-shift supervision.

---

# 10. Double balancing in DINO head training should be checked

The DINO training plan uses:

- hierarchical approximately balanced sampling across dataset/class/attack family;
- equal-domain, class-balanced BCE.

These two mechanisms both compensate imbalance.

Using both may over-weight rare classes/families more than intended.

## Recommendation

Pick one primary optimization definition.

For example:

### Recommended

Hierarchical sampler for:

- dataset;
- video/frame exposure;

and class-balanced/equal-domain loss for the actual objective.

Do not additionally force exact class balancing in the sampler.

Alternatively, use balanced sampling and ordinary BCE.

The precise choice is less important than avoiding an accidental double correction.

---

# 11. "Fit MSP/entropy/policy-margin" is inaccurate wording

Section 9.4 says:

> Fit required MSP/entropy, policy-margin, Mahalanobis...

MSP, entropy, and policy margin are deterministic scoring heuristics.

They are not fitted.

Mahalanobis may require source statistics.

## Recommendation

Split into:

### Non-learned risk scores

- MSP;
- entropy;
- operational margin;
- absolute disagreement.

### Source-statistic baseline

- Mahalanobis.

### Learned risk models

- logistic;
- capacity-matched MLP.

This matters because the paper should distinguish learning failure risk from simply computing uncertainty heuristics.

---

# 12. The same-family control is fair, but the paper should not over-interpret it

DINOv2-Reg + plain DINOv2 is a good practical same-family control.

However, they are still very closely related representations.

If DINO/OpenCLIP beats this pair, the valid conclusion is:

> the studied heterogeneous pair outperforms this matched same-family control.

Not:

> heterogeneous foundation models are universally better than homogeneous ensembles.

Document 42 is mostly careful about this already.

Keep that conservative wording in the manuscript.

---

# 13. The data-custodian architecture may be overengineered for the actual team

The target namespace, sealed evaluator, signed freeze record, immutable artifact graph, and dirty-code rejection are scientifically excellent.

But for a small research team, implementation cost can become substantial.

This is not a methodological flaw, but it can delay the paper.

## Recommendation

Distinguish:

### Mandatory scientific controls

- fold-local target exclusion;
- immutable configs;
- manifest hashes;
- source-only thresholds;
- no post-target changes.

### Optional infrastructure hardening

- cryptographic signed freeze;
- separate label-release service;
- OS-level namespace isolation.

Git commits + immutable manifests + scripted lineage assertions may already be enough for a Q3 research paper.

Do not let governance infrastructure consume more time than the actual experiment.

---

# 14. Frame-bank training and one-frame calibration are coherent

This part is reasonable.

Training may use multiple frames/video because the model remains image-based.

Calibration/OOF/evaluation use one fixed image/video.

That does not violate the single-image inference claim.

However, manuscript wording should say:

> single-image inference

rather than:

> training uses only one image per video.

No change required to the plan.

---

# 15. Detector-failure treatment is strong and should remain

Mapping detector failure to:

\[
terminal\ non\text{-}accept
\]

and retaining it in end-to-end denominators is methodologically clean.

The separation:

\[
\mathcal D_{risk}
=
\{detector\ success\}
\]

versus all-transaction end-to-end metrics is also correct.

No change recommended.

---

# 16. The candidate-ID ledger for matched OOF is a very good design

The requirement that domain-OOF and sample-OOF produce exactly one prediction for the same candidate universe is one of the strongest parts of Document 42.

Keep it.

It makes the main RQ1 comparison much harder to attack.

The only remaining caveat is different effective model-training budgets, which the plan already records and handles through sensitivity analysis.

---

# 17. Freeze claim rules globally before all four target results

Document 42 Phase 7 correctly places the analysis freeze before Phase 8.

This should override any older wording elsewhere such as:

> before opening each target, derive thresholds from its sources.

The safest rule is:

\[
oxed{
	ext{all analysis-rule generation code and rule-selection logic freeze before the first target result}
}
\]

Fold-specific numeric source thresholds may still differ because source domains differ.

But the **algorithm that derives them** must be frozen globally.

Synchronize older documents if necessary.

---

# 18. Bootstrap aggregation should be described at the target level

The final macro is across four target domains.

Do not pool all target subjects into one giant bootstrap because large datasets would dominate.

Recommended procedure:

For each bootstrap replicate:

1. resample clusters inside each target separately;
2. compute target-specific metric difference:
   \[
   \Delta_t;
   \]
3. compute equal-weight macro:
   \[
   \Delta_{macro}
   =
   \frac14
   \sum_t\Delta_t.
   \]

This preserves the meaning of a domain macro.

Seeds should remain separate optimization replicates, not be pooled as extra subjects.

---

# 19. One important manuscript-level simplification

Document 42 contains enough engineering detail for an internal execution plan, but most of it should **not** enter the paper.

The manuscript Method section should not discuss:

- environment variables;
- symlink views;
- atomic writes;
- storage trees;
- raw archive layout;
- SHA handling.

The paper needs only:

1. source/target split;
2. branch model;
3. branch calibration;
4. domain-OOF risk construction;
5. matched sample-OOF control;
6. risk model;
7. selective policy;
8. metrics.

Keep Document 42 as the reproducibility blueprint, not as the manuscript structure.

---

# 20. Recommended corrections before declaring Document 42 frozen

## Must fix

1. Remove the contradiction between globally immutable dataset roles and outer-target-dependent role assignment.
2. Replace absolute target-label sealing with fold-local exclusion language.
3. Freeze the exact MICO source/target official split convention in a table.
4. Define exactly which source partition selects \(\tau_{ref}\).
5. Write the gate as a filter on predicted-live decisions for K=1 utility.
6. Specify target-level macro bootstrap rather than pooled-dataset bootstrap.

## Strongly recommended

7. Elevate benchmark-compatible MICO results from a minor secondary track to a visible main comparison track.
8. Add security-specific failure-ranking support such as false-accept ranking.
9. Clarify fold-local quality-feature normalization.
10. Avoid double class/domain balancing during DINO head training.
11. Distinguish non-learned uncertainty scores from fitted risk baselines.
12. Freeze all analysis-rule logic before the first of the four targets is evaluated.

## Optional simplification

13. Reduce label-sealing / cryptographic infrastructure if it threatens project schedule; preserve the scientific lineage checks.

---

# Final verdict

\[
oxed{
	ext{DOCUMENT 42 IS FUNDAMENTALLY SOUND, BUT NOT YET COMPLETELY FROZEN}
}
\]

No architectural redesign is needed.

The largest conceptual correction is the role-splitting inconsistency:

\[
	ext{assigned once per dataset}
\neq
	ext{depends on outer target}.
\]

The largest publication correction is that the exact MICO benchmark convention must be fixed before implementation, otherwise the resulting numbers may not be comparable with existing cross-domain FAS literature.

The largest selective-PAD clarification is:

\[
	ext{risk ranking can use all errors}
\]

but under \(K=1\):

\[
	ext{the operational gate should filter predicted-live decisions}.
\]

Once these points are corrected, Document 42 is a strong enough blueprint to implement the frozen Q3-first research plan.
