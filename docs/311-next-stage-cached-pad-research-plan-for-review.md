# 311 - Next-stage cached PAD research plan for critique

Date: 2026-10-27

Status: **proposal only; no new fitting, threshold selection or target
evaluation is authorized.** The owner requested publication for critique,
not execution. The previous308 execution approval does not carry forward.

Basis:
[recommendations307](307-recommendations-improving-pad-classification-from-cached-features.md),
[completed study309](309-source-only-cached-readout-results.md) and the newly
received [review310](310-review-doc309-supervised-cached-readout-results.md).
The completed308/309 study and its negative/limited-gain findings remain closed.

## 1. Decision requested from this review

The discussion suggested:

> Diagnose score/threshold transfer and readout optimization first; then test
> a small, genuinely nested fusion comparison; defer backbone/risk expansion.

Review310 accepts the cheap readout screen and gives the next scientific
priority to **incremental supervised-CLIP value under an operating utility**,
not another search for a more favorable readout number.

These are not silently treated as the same recommendation. This proposal
separates three work packages:

| Package | Question | New scientific fits? | Proposed disposition |
|---|---|---|---|
| D0: saved-output diagnosis | Where do ranking, calibration and operating transfer diverge? | No | First, before selecting a new experiment |
| S1: convergence-controlled linear comparator | Is the fixed200-epoch recipe a material readout limitation? | Yes | Optional fork requiring explicit review approval, not an automatic rerun |
| F1: nested source-only convex fusion | Does supervised CLIP add useful value beyond the strong DINO controls? | Possibly, for new inner contexts | Preferred next scientific question under310 |

**Working recommendation:** D0 first, then choose one bounded experiment.
Use D0 -> F1 as the default next-study proposal consistent with310. Retain
S1 as an explicit alternative from the discussion if the reviewer considers
the optimization limitation important enough to justify another comparator.
Do not silently expand F1 to include S1, or fit both and publish whichever
looks better. The choice and exact execution package must be settled first.

## 2. Established evidence and what it does not establish

Primary held-out-source mean AUROC in309:

| System | AUROC |
|---|---:|
| Original DINO-Reg | .885432 |
| Original equal two-DINO | .889609 |
| Zero-shot OpenCLIP | .554171 |
| Selected DINO-Reg | .879631 |
| Selected equal two-DINO | .889780 |
| Supervised OpenCLIP | .844040 |

Supervised CLIP contains useful task-specific information, but remains below
the two-DINO ranking comparator. Its improvement over zero-shot includes
supervised labels and a learned head; it is not an unsupervised or new-backbone
claim. Selected DINO-Reg loses primary AUROC in10/12 contexts despite lower
inner BCE; selected two-DINO's mean gain is only.000171 descriptively.

Operating failures are not solved:

- Supervised CLIP mean original-denominator FA/non-acceptance:
  **9.974% /53.942%**.
- Selected two-DINO: **35.066% /17.882%**.
- Held-out OULU selected two-DINO FA: **67.305%**.
- Held-out CASIA supervised CLIP AUROC.966878 coexists with bona-fide
  non-acceptance **66.389%**.

These use the5% source-calibration classifier reference rule, not301's
selective FA<=1% policy. Neither is an unseen-domain security guarantee.

### Additional read-only validation-tail observation

After309, the producer inspected the already saved selected-head histories;
no head was fitted or extended. For heads whose selected epoch is200, define
`absolute_drop = BCE[180] - BCE[200]` and
`relative_drop = absolute_drop / BCE[180]`, using one-based epoch numbering.

| Branch | Selected at200 | Median absolute drop,180->200 | Median relative drop |
|---|---:|---:|---:|
| DINO-Reg | 43/48 | .002299225 | 2.3197% |
| Plain DINO | 36/48 | .001730402 | 1.3099% |
| OpenCLIP | 48/48 | .012955952 | 4.3383% |

This is producer-side inspection of private histories whose fitted-artifact
hashes are bound by the
[public closure](../results/phase1/source-readout308-closure-v1.json).
It is not a new independent public replication. Complete histories remain
private; public summaries alone do not reproduce the tail calculation.

Validation BCE is still falling at the budget boundary, especially for CLIP.
That is **not** a training-gradient convergence test, evidence that more
epochs improve held-out-domain AUROC, or authority to extend the old run.
Equal nominal epoch budgets and candidate counts do not imply equal
optimization progress or effective search diversity across feature spaces.

## 3. Boundaries common to every proposed package

- Keep original299 geometry, preprocessing, sample identities, checkpoint
  hashes, feature matrices, permanent roles and SiW effective-use exclusions.
- Preserve6882 eligible originals,6855 successes and27 retained failures.
  Keep technical non-acceptance on original class denominators; invent no
  scores for failed inputs.
- Source use is not official-train-only: the historically adopted source
  roles include some OULU/CASIA/MSU official-test members. SiW null-role tests
  and adopted exclusions remain ineligible.
- No raw image decoding, new image/text encoder forward, prompt/backbone
  change, G2 promotion, fine-tuning or new target prediction.
- No canonical source-evidence, old model/result/config or freeze replacement.
- All four observed datasets remain development material. New source analyses
  do not restore untouched-target status.
- Results must retain every declared seed/domain, infeasible case and failure.
  No best-seed reporting, unsupported optimizer success or automatic retry.

## 4. D0 - saved-output diagnosis before any new fitting

### D0.1 Optimization description, not another training campaign

Summarize saved validation histories, selected epochs and candidate choices
by branch, permitted-source set and seed. Separate selected-head summaries
from all-candidate diagnostics. Do not fit another candidate or extend a head.

The output should distinguish:

1. A fixed recipe ending while validation BCE still improves.
2. Lower inner BCE failing to improve held-out-source ranking.
3. Numerical convergence, which the histories alone cannot establish.

Do not choose a new learning rate, normalization or epoch count by mining the
public held-out candidate ranking table.

### D0.2 Score and threshold transfer

Reconstruct scores from verified saved coefficients/caches where necessary;
this is linear prediction, not new encoder inference or fitting. For each
context/system/source, compare:

- Raw logits and calibrated score distributions by class.
- Allowed calibration populations versus the held-out pseudo-source.
- Class-conditional quantiles and the location of the saved threshold.
- Successful score support, original class counts, technical failures and
  numbers of registered groups contributing to each rate.
- FA, bona-fide non-acceptance and their tradeoff, separately per domain.

A positive-slope monotone calibrator does not generally repair discrimination:
apart from numerical ties it preserves within-domain score ordering.
Conversely, a good AUROC does not locate a transferable threshold.
Brier/NLL are probability-scoring diagnostics, not pure calibration evidence.

Use the existing domain-OOF and g_domain pools separately. Diagnostic curves
must be marked **not selected operating policies**. Held-out labels may
describe failures here but may not select/recalibrate the evaluated policy.
Do not derive an operating threshold from an observed301 target.

### D0.3 Deliverable and gate

Produce one compact diagnostic report with per-source plots/tables, exact
saved-input bindings, definitions and resource accounting. No model fits.
It should explain which uncertainty remains and recommend F1 or a justified
S1 alternative; it must not claim to have resolved either by inspection.

D0 is proposed work too: publishing311 does not automatically launch it.

## 5. S1 - optional convergence-controlled linear comparator

This is **not** a repeat or extension of308, and not a mandatory prerequisite
for every fusion study. Its sole question would be whether a separately
defined, adequately optimized linear comparator changes the readout picture.

If explicitly chosen:

- Keep raw cached representations fixed; do not combine solver, geometry,
  feature-normalization and fusion searches.
- Retain the old AdamW200-epoch and309 systems as unchanged anchors.
- Specify a source/class-balanced logistic objective, explicit L2 penalty
  on weights, unpenalized intercept and documented loss/penalty scaling.
- Use a small predeclared positive-regularization grid and comparable search
  budgets for all branches. Ground scaling decisions in permitted training
  inputs only; equal nominal penalty numbers need not have equal effects.
- Keep head fitting, candidate selection, calibration and evaluation roles
  separate. Fix the inner selection metric and deterministic ties before
  fitting, not after reading held-out outcomes.
- Declare solver, stationarity/success tests, tolerances, iteration/line-search
  limits and terminal-error handling. A max-iteration warning is not convergence.
- Preserve all candidates, solver statuses, objectives and selected models.

Decoupled AdamW weight decay is not automatically identical to this explicit
L2 objective. S1 would compare declared readout recipes, not establish that
the old optimizer solved the same objective incorrectly.

No grid, optimizer limits or fit count is sealed by this document. Those
must be made executable and reviewed if S1 is selected. If it brings no
useful generalization/operating benefit, retain that result and stop expanding
the readout search. Feeding an S1-selected branch into F1 would require an
explicitly revised F1 package; it is not an implicit adaptive extra arm.

## 6. F1 - preferred next scientific question: incremental fusion utility

### F1.1 Fixed branches and visible comparators

Working branch proposal, subject to critique:

- D: original299 DINO-Reg recipe and its allowed-source calibration.
- C: supervised CLIP raw-feature, learning-rate.01, weight-decay.05,
 200-epoch recipe from309, with allowed-source checkpoint selection and
 calibration. Freezing this recipe now is an exploratory development choice
 informed by309, not an untouched confirmation.

Use `p_lambda = (1-lambda) * p_D + lambda * p_C` with the proposed fixed grid:
`[0, 0.1, 0.25, 0.5, 0.75, 1]`.

Keep D-only, C-only, fixed equal fusion, original equal two-DINO and selected
equal two-DINO visible. D is shared exactly between its standalone system and
the heterogeneous candidate. The original two-DINO comparator shares that
old DINO-Reg anchor; selected two-DINO is an additional stronger-reference
candidate, not a branch-matched causal control.

For attribution beyond merely tuning an average, also propose a
**matched-selector two-DINO control**: combine the same D with original299
plain-DINO using the same six weights, inner utility, threshold rules and
selection budget. Keep the fixed equal controls too. Otherwise a learned
heterogeneous mixture beating a fixed average could reflect weight selection
rather than an advantage of heterogeneous embeddings. This matches selection
opportunity, not backbone capacity or encoder latency.

No readout hyperparameter grid, learned fusion network or quality/risk model
is added to F1. Weight zero for CLIP is a legitimate result.

### F1.2 Working operating utility for critique

Do not select by within-domain BCE and assume source-transfer security follows.
The numerical working proposal is:

- Inner held-out-source empirical attack FA<=**5% in every source**.
- Bona-fide acceptance>=**50% in every inner held-out source**, to exclude
  trivial reject-all as a useful operating solution.
- Among feasible weights, maximize the **minimum source bona-fide acceptance**.
- Exact ties: lower worst-source FA, then lower CLIP weight.

Apply the identical rule to the matched two-DINO selector, with lower added
plain-DINO weight as its final tie rule.

These5%/50% values are **reviewable proposal choices**, not existing product
requirements, statistical population guarantees or a claim that the current
systems satisfy them.5% preserves comparability with309's classifier
reference; a deployment-motivated1% alternative requires explicit agreement
and adequate attack/group support before sealing.

Define rates on original class denominators. Technical failures retain
non-acceptance. Bona-fide acceptance is `1 - original_bona_fide_non_acceptance`;
it is not overall accepted fraction. Keep ranking coverage separate.
As310 notes,309's `operational_acceptance_coverage` is the accepted fraction,
not301's coverage including covered spoof decisions.

If no candidate satisfies both constraints, record
`no_candidate_meets_declared_utility`. Do not relax constraints, hide the
case, label reject-all as a useful success or select an unconstrained
"best available" winner. Report all declared candidates descriptively.

Report finite-sample/group support and uncertainty. Empirical feasibility
on a few source groups is not a statistically established low-FA guarantee,
and even adequate source precision cannot guarantee arbitrary domain shift.
The exact support/uncertainty acceptance rules must be fixed in the execution
package, especially if1% is requested.

### F1.3 Nested selection: the existing OOF table cannot select lambda

Retain the12 outer-exclusion/seed combinations and separate domain-OOF and
final/g_domain evaluations.

For each domain-OOF evaluation:

1. Exclude the named outer dataset entirely from that context.
2. Exclude the pseudo-target source from every fitting/selection/calibration
   operation. It is the final evaluation population for this fold.
3. Inside the two remaining permitted source domains, generate inner
   source-held-out predictions with the **entire** fixed-branch pipeline:
   head checkpoint selection, calibration, each candidate fusion and its
   allowed-source threshold.
4. Evaluate the declared utility on those inner held-out predictions and
   choose lambda using the fixed feasible/tie rules, separately for each
   declared mixture family with matched selection opportunities.
5. Apply the chosen lambda with the pipeline fitted/calibrated only on the
   permitted sources, then evaluate the untouched pseudo-target fold.

For final three-source fitting, perform the analogous inner source holdouts;
g_domain remains outside all selection and calibration.

Thresholds for each candidate are selected from its allowed calibration
roles only, using the fixed reference rule. Inner validation evaluates that
entire operating pipeline; it does not supply calibration labels to the
same held-out-source model. Registered groups and exact-frame components
remain disjoint at every boundary.

Inner one-source fits may have inadequate group/class support; preflight
must detect and report this before execution, not silently substitute
within-domain validation. Existing309 aggregate/prediction tables cannot
replace these new inner predictions: choosing lambda on their evaluation
labels and reporting the same rows would leak selection into evaluation.

Reuse saved states only when training/validation/calibration memberships,
recipes, transforms and bindings match exactly. New inner-context fits may
be necessary. Do not redo the completed309 grid or claim that all new
selection is free simply because the image features are cached.

### F1.4 Endpoints and stopping decision

Primary: feasibility and held-out-source security/usability under the fixed
declared utility, including the worst source and all infeasible folds.
Secondary: AUROC, successful BA/ACER, Brier/NLL, original-denominator FA/BFNR,
accepted fraction, ranking coverage and conditional paired uncertainty.

Keep all per-domain/seed results. Twelve overlapping contexts are not twelve
independent replications. Intervals based on saved predictors do not cover
retraining or unseen-domain uncertainty.

If positive CLIP weights do not add utility relative to D-only and the strong
fixed/selected/matched-selector two-DINO controls, retain the negative result
and stop forcing heterogeneity.
An AUROC increase with an unacceptable FA/BFNR tradeoff is not an operating
success. No risk model or follow-up search starts automatically.

## 7. Execution package still required after critique

Only the selected work package should be implemented. Before any new fitting,
publish its tested code, exact candidate/utility/support rules, input/feature
and saved-model hashes, split inventory, unique-fit/reuse ledger, full
calibration/threshold accounting, output schema and a resource/stop manifest.

For F1, the proposed scope is still CPU/cache-only with two BLAS threads,
zero image/text encoder forwards and no target evaluations. A provisional
upper envelope of6hours,4GiB combined sampled RSS and1GiB new owned artifacts
is offered for critique, **not approved or resource-profiled for this study**.
Exact head/calibrator/policy counts must be computed from the nested plan,
including inner support and any hash-verified reuse, before approval.
S1 needs its own optimizer/candidate counts if chosen instead.

Use one immutable attempt and original deadline; log fit starts and outcomes,
preserve failures, enforce combined resource monitoring and independently
reconstruct saved results. No automatic retry, silent calibration fallback,
unregistered solver amendment or favorable-result-driven budget extension.

After the concrete package is sealed, request one explicit execution decision.
Neither311,310 nor the old308 approval supplies that authority.

## 8. Paper direction and explicitly deferred scope

The potential question is **when a supervised foundation-model branch adds
value under domain shift at a useful operating point**, not simply whether
its own AUROC exceeds its weak zero-shot readout.

A linear probe or weighted average alone is not demonstrated methodological
novelty. Literature positioning, a clear contribution, strong baselines,
negative outcomes and appropriate evaluation are still required; no Q3
acceptance or percentage improvement is promised. Independent confirmation
of revised-method generalization requires genuinely unseen authorized data
or a prospective cohort after the method/protocol is locked.

Defer backbone/partial fine-tuning, prompts, geometry, multi-frame inference
and risk-model expansion. If risk supervision is later approved, cross-fit
the entire selected readout/calibration/fusion pipeline before producing
error labels. Preserve301's accepted RQ1 inconclusive/RQ2 evidence-against
results as historical outcomes.

## 9. Questions for the critique

1. After D0, prefer F1 directly as310 recommends, or justify the separate S1
   convergence-controlled comparator first? What decision would S1 change?
2. Is the proposed shared old DINO-Reg anchor plus fixed supervised CLIP
   recipe the right comparison, with fixed/selected two-DINO references and
   the matched-selector two-DINO control retained?
3. Are5% FA and50% minimum bona-fide acceptance appropriate exploratory
   utility constraints, or should another operating target be fixed first?
4. Are the nested source-held-out construction, support rules and explicit
   infeasibility outcome adequate, without using309 evaluation labels to
   choose the new policy?
5. What precise incremental benefit would justify retaining CLIP, and which
   claims would still need genuinely unseen validation?

Until these points are resolved and a concrete package is sealed, the
deliverable is this plan for critique only.
