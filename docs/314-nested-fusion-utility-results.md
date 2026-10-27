# 314 - Nested fusion utility results: neither selector found a feasible policy

Date: 2026-10-27

Status: **completed once and independently reconstructed from saved states.**
The owner explicitly approved the sealed
[package313](313-bounded-nested-fusion-utility-execution-package.md) after
implementation, full local regression and exact-commit CI. This later
approval, not review312 or the old308 approval, authorized execution.

## 1. Decision

**No demonstrated incremental value for retaining CLIP under the declared
operating-policy screen. This is not a finding that CLIP loses a measured
fusion comparison, or that CLIP features are universally useless.**

Neither the DINO-CLIP selector nor the equally budgeted two-DINO selector
found an inner-feasible weight. All30 unique selectors per family returned
`no_candidate_meets_declared_utility`; all36 primary evaluation folds
therefore have no selected policy for either family.

The immediate blocker is cross-source attack FA: **every one of the360
family/selector/weight candidates violated the5% FA condition on at least
one inner held-out source**. Some also failed50% bona-fide acceptance.
The50% usability floor alone did not cause universal infeasibility.

No lambda, threshold, recipe, constraint or seed was changed in response.
No fallback policy was silently inserted. The declared two-point utility
gain comparison is **unestimable**, not zero, because neither selected
family produced the required full endpoint.

## 2. Scope and execution evidence

Scientific commit: `1aecf9cfb0e44f20cf7b0dfdd38485392eede814`.
Its [GitHub CI](https://github.com/lathevinh/fas/actions/runs/40481387620)
succeeded before the explicit execution decision.
All538 local unittest regressions and canonical schema validation passed.

The [public pre-run inventory](../results/phase1/fusion313-plan-v1.json)
is preserved in its original `prepared_not_authorized` state. The
[aggregate closure](../results/phase1/source-fusion313-closure-v1.json)
records the subsequent approval hash, one attempt, terminal, saved
reconstruction, all candidate utilities, thresholds, fold outcomes and
conditional uncertainty. Individual memberships, coefficients and
predictions remain private.

| Item | Observed |
|---|---:|
| Unique core pipelines | 42 |
| New heads /calibrators | 36 /36 |
| Reused core heads /calibrators | 90 /90 |
| Reused selected-reference head/calibrator access slots | 60 /60 |
| Family selectors /unique threshold policies | 60 /492 |
| Unique prediction tasks | 108 |
| Primary /g_domain evaluation folds | 36 /36 |
| Encoder forwards /new target evaluations | 0 /0 |
| Whole-attempt wall time from original approval | 36.053912 seconds |
| Combined supervisor/worker sampled peak RSS | 451002368 bytes,430.11MiB |
| Owned directory bytes before terminal | 35848298 bytes,34.19MiB |
| Limits | 6h,2 BLAS threads,4GiB sampled RSS,1GiB owned output |
| Automatic retry /scope amendment | None /none |

The wall/resource accounting includes the scientific worker and its separate
saved-reconstruction process. Sampling is not a kernel-enforced instantaneous
RSS maximum. The later public export copies aggregate evidence and figures;
it performs no model fitting, prediction or policy selection.

Important bindings:

- Private pre-run plan:
  `4e4902861b3abe2834abc0206764d668076ba357f62b8f048901c98a17d39e63`.
- Scientific completion:
  `881bb8d2b482d0f5e404c8d81a683a98cd10b3ce55d8e85f275260e70a9ab7d0`.
- Saved reconstruction:
  `bff7bc670af10728d3420f6e34e69a7a33f4ee22b878ad7ab92d2950bcb7709d`.
- Public aggregate receipt:
  `f0bf7dbe5982c45048bf3aa70e0d9f6ddf94dc9163034286053a1281881fceb8`.

The sealed scientific code/config/test/protocol inventory remains unchanged.
Reconstruction checks all saved fits, provenance, immutable fit ledgers,
predictions, selected weights, policies, metrics, bootstrap and plots without
calling either head or calibrator fitting.

## 3. Where the selectors became infeasible

The fixed six weights include zero added-branch weight. Counts below are
candidate observations, not independent samples or statistical replications.
FA and BFA violation columns overlap.

| Family | Parent source count | Selectors | Candidate weights | FA violation | BFA violation | Both | Feasible |
|---|---:|---:|---:|---:|---:|---:|---:|
| DINO-CLIP | 2 | 18 | 108 | 108 | 61 | 61 | 0 |
| DINO-CLIP | 3 | 12 | 72 | 72 | 45 | 45 | 0 |
| Matched two-DINO | 2 | 18 | 108 | 108 | 48 | 48 | 0 |
| Matched two-DINO | 3 | 12 | 72 | 72 | 34 | 34 | 0 |

Two-source parents select on one-source-trained inner models. Three-source
parents select on two-source-trained inner models. Both constructions
failed the same declared operating constraint; no within-domain replacement
or favorable-source removal occurred.

Every declared support preflight passed. The result is **utility
infeasibility**, not a missing-class support failure, optimizer crash,
expired deadline or resource stop. Conversely, passing the exploratory
support floors does not certify a5% population security rate.

## 4. Primary fold outcomes, including fixed references

A selected policy's transfer failure is different from not selecting any
policy. The fixed references always have a calibration-derived threshold
and can therefore be evaluated even when they fail the utility.

| System | No selected policy | Transfer failure | Empirically feasible |
|---|---:|---:|---:|
| Nested DINO-CLIP | 36 | 0 | 0 |
| Nested matched two-DINO | 36 | 0 | 0 |
| Original DINO-Reg only | 0 | 32 | 4 |
| Original plain-DINO only | 0 | 30 | 6 |
| Supervised CLIP only | 0 | 35 | 1 |
| Fixed equal original two-DINO | 0 | 30 | 6 |
| Inherited selected equal two-DINO | 0 | 30 | 6 |
| Fixed equal DINO-CLIP | 0 | 30 | 6 |

None is feasible on all36 primary folds. Equal counts of feasible folds
are not an equivalence or superiority test. A fixed heterogeneous average
is a descriptive reference, not a substitute for an infeasible selected
policy.

### Per-source fixed-reference rates

Percentages below are equal means over the nine applicable
outer-exclusion/seed observations. They retain original class denominators,
including technical non-acceptances. The per-fold screen above remains
stricter than these descriptive averages.

| Held-out source | D-only FA /BFA | Supervised C-only FA /BFA | Fixed original two-DINO FA /BFA |
|---|---:|---:|---:|
| CASIA-FASD | .216 /41.389 | .278 /33.611 | .031 /51.389 |
| MSU-MFSD | 42.527 /92.460 | 10.185 /64.881 | 39.484 /94.048 |
| OULU-NPU | 50.537 /89.184 | 13.289 /38.033 | 65.811 /93.603 |
| SiW-Mv2 | 24.895 /67.064 | 16.143 /47.706 | 30.005 /74.702 |

The familiar tradeoff remains: some systems have useful ranking but poor
operating transfer; reducing spoof acceptance may also reject many real
inputs. These are not new independent target results.

## 5. Compact D0: score/threshold transfer, not another tuning round

The saved diagnostics contain classwise raw/calibrated quantiles, allowed
calibration versus held-out source distributions, actual thresholds and
fixed-budget validation tails. They did not select another policy.

Illustrative threshold-relative score summaries:

| Branch /held-out source /class | Allowed-calibration median score minus threshold | Held-out median score minus threshold |
|---|---:|---:|
| DINO-Reg /OULU /attack | +.676352 | -.054618 |
| OpenCLIP /CASIA /bona fide | -.008918 | +.076395 |
| OpenCLIP /OULU /bona fide | -.061659 | +.029847 |

Attack-high scores are accepted below threshold. Negative attack margins
are therefore dangerous; positive bona-fide margins indicate rejection.
For each fold, the allowed-calibration summary takes the median of its two
source class-median margins; the table then takes the median over nine
applicable folds. These are descriptive medians of fold summaries, not a
pooled-image distribution or an uncertainty interval.

This documents score/threshold shift consistent with the rate failures.
It does not prove a specific causal mechanism or that another solver,
normalization or epoch budget would fix it.

Deterministic operating plots are in the
[diagnostic figures](../results/phase1/fusion313-diagnostics/), including
[primary OULU](../results/phase1/fusion313-diagnostics/domain_oof-OULU-NPU.svg)
and [primary CASIA](../results/phase1/fusion313-diagnostics/domain_oof-CASIA-FASD.svg).
Nested-family points are absent, explicitly counted as missing policies,
not drawn as zero-risk/zero-acceptance policies.

## 6. g_domain and uncertainty do not reverse the decision

The separate within-source held-out-group diagnostic has36 source-level
folds. Fixed D-only is empirically feasible in36/36; fixed original
two-DINO35/36; selected equal two-DINO34/36; CLIP-only33/36; fixed
DINO-CLIP32/36. These favorable within-source references do not establish
new-domain transfer.

Both nested families still have36 missing policies in this pool because
their weights had to be selected by source holdouts, not g_domain labels.
It would be leakage to select a favorable weight or threshold on g_domain
and present that as the registered result.

All2000 component-bootstrap draws retain both original classes in each
source, in both pools. Reference intervals are conditional saved-predictor
intervals with component multiplicities shared across overlapping contexts.
Selected-family R and gain intervals are **unestimable because policies are
missing**, not because a confidence interval happened to cross zero.
No selected-policy gain or significance claim is made.

## 7. Historical reference equality and implications

A separate saved-prediction audit checks four unchanged references against
the completed308/309 artifacts:

- 61695 successful repeated source rows across both pools.
- 246780 score/threshold/acceptance comparisons.
- Maximum score difference8.881784197001252e-16.
- Maximum threshold difference1.1102230246251565e-16.
- Every acceptance decision agrees exactly; numeric tolerance is
  `rtol=atol=1e-12`.

Thus the failed selector result was not obtained by silently degrading the
old anchors or replacing their input population. These repeated rows are
not61695 independent images. The aggregate receipt binds the export/audit
helper hash; private individual predictions are not published.

**Disposition:** do not promote CLIP into the declared useful policy, and
do not promote the matched two-DINO selector either. This fixed family of
calibration-derived policies does not solve source transfer under the
registered empirical5%/50% utility. No measured selected-fusion superiority
can be estimated.

The result does not justify a universal rejection of CLIP, a deployment
claim for DINO, immediate constraint relaxation, an S1 solver campaign or
another target evaluation. Any changed policy family would be a separate
predeclared exploratory study. All four observed datasets remain development
material and all accepted301 conclusions are preserved.
