# 313 - Bounded nested-fusion utility execution package

Date: 2026-10-27

Status: implementation package, **not an execution approval**. The owner
accepted the feasibility-first method in discussion after
[review312](312-review-plan311-bounded-nested-fusion-utility.md).
The exact sealed workload and resource envelope require one subsequent owner
decision before private fitting or D0 diagnostic execution. Approval308 does
not apply. [Study309](309-source-only-cached-readout-results.md) remains closed.

## 1. One question and fixed pipelines

Does supervised CLIP add useful source-transfer operating performance beyond
DINO alone and an equally selected two-DINO mixture?

- D: original299 DINO-Reg, raw cached features, lr.001, wd.05.
- P: original299 plain-DINO, raw cached features, lr.001, wd.05.
- C: supervised309 OpenCLIP recipe, raw cached features, lr.01, wd.05.
- All heads use the inherited FP64 full-batch AdamW,200 epochs, unpenalized
  bias and earliest minimum equal-source/class-balanced validation-BCE
  checkpoint. No readout grid or post-selection refit is added.
- Each branch has its own inherited positive-slope sigmoid calibrator on
  permanent branch-calibration rows. An unsuccessful optimizer stops the
  attempt; there is no identity fallback.

Compare `(1-lambda)*D + lambda*C` against `(1-lambda)*D + lambda*P`, using
the identical grid `[0,.1,.25,.5,.75,1]`. Both selectors use the same utility,
threshold rule and tie-break. They share exactly the same D branch.
Also report D-only, P-only, C-only, fixed equal two-DINO, inherited selected
two-DINO and fixed equal DINO-CLIP. The selected reference is not another
branch-matched causal control or a new candidate search.

This matches selection opportunity and permitted source memberships, not
encoder capacity, optimization progress, pretraining information or latency.
The C recipe was informed by309; these are development-data comparisons, not
an independent test of intrinsic feature-family superiority.

## 2. Nested selection and transferred policies

Keep the four historical outer exclusions and three historical seeds.
Each outer context retains three source domains:

1. For a primary pseudo-domain holdout, exclude that pseudo-domain and the
   named outer dataset from all head fitting, checkpoint selection,
   calibration and weight selection. The final pipeline has two sources.
2. Select its weight using two inner domain holdouts: fit the full branch
   pipeline on one source and evaluate on the other, then reverse.
3. For each inner model/weight, choose the threshold using only that
   model's permitted successful calibration rows. Use the existing largest
   threshold satisfying empirical attack FA<=5% in every calibration source.
   This successful-calibration denominator is conservative relative to
   retaining calibration failures as non-acceptances.
4. Evaluate inner utility on original held-out class denominators. A weight
   is eligible only if every inner source has FA<=5% and bona-fide
   acceptance>=50%. Maximize minimum source bona-fide acceptance; ties use
   lower worst-source FA, then lower added-branch weight.
5. Apply the independently selected weight to the two-source pipeline,
   with its own allowed-source calibration threshold, on the outside
   pseudo-domain. Do not copy an inner threshold or use outside labels to
   repair this final threshold.

For final/g_domain diagnostics, fit on three sources and select weights using
three internal two-source holdouts. g_domain never selects heads, weights or
thresholds. Its results cannot replace the primary domain-OOF endpoint.

One shared source-set/seed pipeline may legitimately serve multiple contexts.
Reuse does not permit any context to borrow labels from its excluded domains.
Some final-fit inner prediction tasks are also primary outer predictions
elsewhere; the selection lineage remains bound to its own allowed sources.
Primary two-source selectors use only new one-source inner predictions, never
the same rows on which their selected policy is evaluated.

## 3. Exact support and leakage preflight

Preserve6882 eligible originals,6855 usable rows and27 failures; original299
geometry, all permanent roles, adopted exclusions, features and checkpoints
remain unchanged. Source use is not official-train-only. No raw image,
encoder, target population, risk model, G2, prompt or new solver is used.

Registered source groups and global exact selected-frame hashes form
transitive connected components. No component may cross fitting, validation,
calibration or evaluation boundaries. Check every new one-source split and
every prediction task, including failures with known groups/frame hashes.
Missing frame hashes on technical failures are not invented.

Minimum usable support **per class and source**:

| Partition | Usable images | Independent connected components |
|---|---:|---:|
| Fitting | 2 | 2 |
| Checkpoint validation | 2 | 2 |
| Calibration | 10 | 5 |
| Inner/outer evaluation | 10 | 5 |

These are exploratory computability/stability floors, not confidence-based
security certification. Inventory also publishes actual original/usable
counts, registered groups, components, failures and `1/N` empirical rate
granularity. It does not substitute the old risk-model error-count rule.
For example,14 MSU calibration bona-fide originals give a7.14-percentage-point
bona-fide rate step;42 calibration attacks give a2.38-point attack rate step.

Fitting/validation memberships contain usable inputs only, exactly as299.
Unusable training-role originals are counted separately in the training-role
inventory, not arbitrarily assigned an invented fitted checkpoint fold.
The calibration-role original inventory similarly exposes omitted failures.
All evaluation failures remain original-denominator non-acceptances.
Insufficient declared support blocks preparation; do not silently substitute
within-domain evaluation, remove a fold or lower a support floor.

## 4. Infeasibility and the exact retain-CLIP screen

Each selected family/fold has exactly one outcome:

- `no_candidate_meets_declared_utility`: no inner weight is eligible;
  selected weight, policy and selected-policy metrics are null.
- `transfer_failure`: a selected policy violates5% FA or50% bona-fide
  acceptance on the held-out source.
- `transfer_feasible`: both empirical outside constraints are met.

Do not convert missing policies to reject-all successes or invent scores for
failed images. All36 primary evaluation folds remain in the denominator.
For this conservative exploratory screen, a family is fully feasible only
when **all36 primary folds have a selected policy and satisfy both bounds**.
One bad seed/source is not hidden in a favorable average.

When every selected policy exists, compute each domain's rate as the equal
mean over its nine outer-exclusion/seed observations, then take the minimum
of these four mean bona-fide acceptance rates:

`R(system) = min_domain mean_applicable_context_seed BFA(system, domain)`.

Do not take the minimum before averaging or pool repeated images as
independent observations. Missing selected policies make the full R endpoint
unestimable; never average just the surviving folds.

The owner accepted **feasibility before raw bona-fide acceptance**, refining
review312's suggested screen. Compare DINO-CLIP separately with D-only and
matched-selector two-DINO:

1. If DINO-CLIP is not fully feasible: no demonstrated incremental value
   under this declared screen.
2. If DINO-CLIP is fully feasible but a comparator is not: record
   `feasibility_advantage_only`. Do not claim a2-point acceptance gain over
   an insecure comparator or assign a numeric gain to a missing policy.
3. If both are fully feasible: require `R(CLIP)-R(comparator)>=.02` and no
   reduction in any domain's mean bona-fide acceptance. A numerical1e-12
   tolerance applies to these difference comparisons only.
4. Retain CLIP **for independent validation**, not deployment, only if it
   has a feasibility advantage or practical gain against **both** comparators.
   Otherwise report no demonstrated incremental value in this package.

Both feasible systems may have different FA within the5% bound: this is not
an FA non-inferiority claim. Publish per-source FA and bona-fide differences.
Positive CLIP weight, a higher AUROC or a majority of favorable seeds alone
cannot satisfy the screen.5%/50% and2 absolute percentage points are explicit
exploratory choices, not inferred product requirements.

## 5. Conditional uncertainty and compact D0

Use2000 source-stratified connected-component bootstrap draws, seed20261027.
Draw each source component once per replicate and share its multiplicity
across every system, seed and overlapping context. Include technical
failures in class denominators. Intervals for R differences recompute the
worst domain on each draw; also report paired per-source BFA/FA differences.
At least95% of draws must retain both original classes in every source for
interval estimation. Otherwise report uncertainty as unestimable. Missing
selected policies likewise make the corresponding full-endpoint interval
unestimable, not a complete-case estimate.

Intervals are descriptive, conditional on saved fitted/selected policies.
They do not resample fitting/selection, establish unseen-domain safety,
adjust for multiple comparisons, or act as an additional post-hoc retain
gate. The primary decision is the predeclared empirical point screen above.
Do not label it an independent significance test.

D0 is inside this single package: per-source/class raw and calibrated
quantiles at `[0,.1,.5,.9,1]`, allowed-calibration versus held-out score
tables, saved thresholds, validation tails and eight deterministic operating
scatter plots (four domains, two separate pools). They describe failures;
they never choose another recipe, threshold, endpoint or lambda grid.

## 6. Workload, bounded execution and saved reconstruction

Existing-data inventory establishes:

| Item | Count |
|---|---:|
| Unique source-set/seed core pipelines | 42 |
| New one-source pipelines | 12 |
| New heads / new calibrators | 36 /36 |
| Reused core head /calibrator slots | 90 /90 |
| Reused selected-reference head/calibrator slots | 60 /60 |
| Maximum new training epochs | 7200 |
| Unique threshold policies, including fixed reference | 492 |
| Independent family weight selections | 60 |
| Unique prediction tasks, shared when lineage matches | 108 |
| Primary domain-OOF /g_domain evaluation folds | 36 /36 |

There are4+6+4 source subsets of size1,2,3 per seed. The two/three-source
pipelines reuse exact299 D/P heads/calibrators and fixed309 C states.
The selected-reference counts are access slots, not60 necessarily distinct
extra coefficient vectors. No rerun of309's candidate grid occurs.
Reuse candidates are chosen by deterministic context ordering, not outcomes,
and must match ordered fit/validation/calibration memberships, seed, recipe,
transforms, cache bindings and published saved-state hashes.

Proposed enforced envelope for the **whole single attempt, including separate
saved reconstruction**:

- 6 hours from the original owner-approval timestamp; no clock reset.
- 2 BLAS threads, CPU only, offline model access.
- 4GiB combined supervisor/worker sampled RSS; sampled every.5 seconds.
- 1GiB owned output/log/temporary space, including65536 bytes reserved for
  terminal audit and its atomic temporary copy.
- 36 new head starts and36 new calibrator starts, immutable per-fit ledgers.
- 0 image/text encoder forwards and0 new target evaluations.
- No automatic resume, retry, recipe amendment or budget expansion.

Read-only real inventory profiling:3.49 seconds elapsed,339936KiB process
maximum RSS. This measures preparation, **not** a completed nested workload
or a promise of full runtime. The caps enforce stopping if extrapolation is
wrong. Synthetic end-to-end testing covers fitting, policy selection,
infeasibility, conditional uncertainty and reconstruction without fitting.

The supervisor runs the scientific worker and then a separate reconstruction
process under the same deadline/resource envelope. Reconstruction refits
nothing: it checks memberships, saved validation/calibration objectives,
immutable fit starts/completions, original-state reuse, all predictions,
weight choices, thresholds, metrics, bootstrap and plots. Completion requires
both phases. A failed optimizer or reconstruction is a stopped attempt, not
permission to patch the code and reuse its approval.

## 7. Entry points and authority

- [Config](../configs/fusion313_v1.yaml)
- [Controller](../scripts/run_fusion313.py)
- [Statistical core](../src/fas/fusion_study.py)
- [Synthetic regression tests](../tests/test_fusion313.py)
- Public inventory: `results/phase1/fusion313-plan-v1.json` after sealing.
- Private memberships/models/predictions:
  `/mnt/e/FAS-private/artifacts/phase1/source_fusion313_v1/`.

```bash
python scripts/run_fusion313.py --inventory
python scripts/run_fusion313.py --prepare
# Only after explicit owner approval of this sealed package:
python scripts/run_fusion313.py --approve
python scripts/run_fusion313.py --execute
```

Use the declared FAS numerical environment, not an arbitrary base Python.
The public inventory excludes individual original memberships; its hash
binds the private plan. Code/config/tests and this protocol are sealed.
Ordinary package preparation needs no separate D0 review round.

All four datasets remain observed development material. Neither a positive
screen nor g_domain rescues untouched-target status, overwrites301's negative
conclusions, or authorizes another experiment. A negative outcome does not
automatically launch S1, relax utility constraints or trigger fine-tuning.
