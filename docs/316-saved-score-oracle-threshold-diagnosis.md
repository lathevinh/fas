# 316 - Saved-score oracle diagnosis: threshold transfer is not the only limitation

Date: 2026-10-27

Status: **completed saved-score diagnostic, explicitly requested by the
owner after314. No new fitting, encoder inference or model prediction.**
[Review315](315-review-report314-nested-fusion-infeasibility.md) was preserved
before this analysis. The accepted negative
[F1 result314](314-nested-fusion-utility-results.md) remains closed.

## 1. Answer and research disposition

**Changing only the decision threshold cannot meet the empirical5% attack
FA /50% bona-fide acceptance utility on held-out OULU for any of the six
fixed reference systems analyzed here.**

In the primary two-source-trained stage:

- CASIA:54/54 source/system cases admit an oracle threshold meeting utility.
- MSU:41/54 do.
- OULU:0/54 do. The best individual OULU result across all six fixed systems
  and nine applicable contexts is only43.56% bona-fide acceptance at FA<=5%.
- SiW:4/54 do.

This separates two limitations:

1. **Threshold placement:** for CASIA, fixed DINO-Reg can reach90.00% mean
   oracle BFA, versus41.39% under its original source-calibrated threshold.
   The frozen score has empirical operating headroom on this source.
2. **Low-FA score separation:** for OULU, even evaluation-label-selected
   thresholds cannot reach50% BFA with these stored scores. Merely moving a
   threshold is insufficient; calling the failure only calibration would
   be misleading.

These are sample-specific findings about fixed scalar scores and threshold
decisions. They do not prove that the embeddings, every possible head,
every mixture weight, risk gates or PAD methods are fundamentally incapable.
They do not promote CLIP or reverse314's missing-policy result.

## 2. What the oracle computes

For each fixed system, trained pipeline and held-out source, maximize:

`BFA(t) = accepted usable bona-fide originals / all bona-fide originals`

subject to:

`FA(t) = accepted usable attack originals / all attack originals <= 1/20`.

Attack-high scores are accepted **strictly below** threshold; equality
remains attack. Technical failures are non-acceptances, not invented scores.
With N original attacks the exact allowed error count is `floor(N/20)`.
To meet50% BFA, require `ceil(original_bona_fide_count/2)` acceptances.
Integer budgets avoid rounding a rate into eligibility.

The maximum safe threshold is the first successful-attack score whose
acceptance would exceed that budget. If every successful attack fits the
budget, the upper endpoint is the next float above1. Tied attacks cannot be
partially accepted. The minimum useful threshold is strictly above the
required bona-fide order statistic. Therefore a feasible interval has the
form `(bona_fide_lower, attack_upper]`, not a closed interval at both ends.

**The oracle deliberately uses evaluation labels. It is an empirical
diagnostic ceiling, not a source-only policy, deployable threshold,
population upper bound or independent generalization result.** It does not
estimate performance obtainable without those labels. No held-out threshold
is fed back into a model or the old evaluation.

Calibrated probability ties, including any floating-point saturation, are
retained exactly. These results concern stored probabilities, not an
exhaustive test of unrounded raw logits or alternative score functions.

## 3. Fixed scope and populations

Read only the hash-bound313 source manifest, completed plan/receipt,
108 saved prediction tasks and42 saved policy records. No feature shard,
image, model forward or optimizer is used.

| Diagnostic stage | Source-level prediction tasks | Fixed-system cases |
|---|---:|---:|
| One-source inner holdouts | 36 | 180 |
| Two-source primary domain-OOF | 36 | 216 |
| Three-source within-source g_domain | 36 | 216 |
| Total | 108 | 612 |

Fixed references are DINO-Reg only, plain-DINO only, supervised CLIP only,
fixed equal original two-DINO, inherited selected equal two-DINO and fixed
equal DINO-CLIP. The inherited selected reference does not exist for new
one-source models; it is not fabricated or fitted, so that stage has five
systems rather than six.

No new weight search, recipe comparison or selected-family oracle is added.
The nested selected policies were absent in314 and remain absent here.
All6882 eligible originals,6855 usable rows,27 technical failures, permanent
roles and adopted source-use exclusions are unchanged. This source use is
not official-train-only.

Primary source means contain nine applicable source-subset/seed cases.
These share samples and are not nine independent replications. All cases,
including every seed and individual failure, are exported rather than only
the mean or best context.

## 4. Primary result: oracle BFA at attack FA<=5%

Values below are percentages, averaged equally over the nine applicable
contexts for each source. **Every value is hindsight oracle BFA, not measured
performance of a transferable selected policy.**

| Fixed system | CASIA | MSU | OULU | SiW |
|---|---:|---:|---:|---:|
| DINO-Reg only | 90.000 | 53.968 | 39.590 | 31.185 |
| Plain-DINO only | 94.167 | 62.302 | 29.714 | 28.481 |
| Supervised CLIP only | 79.444 | 59.524 | 19.416 | 23.628 |
| Fixed equal original two-DINO | 95.648 | 67.063 | 38.356 | 34.818 |
| Inherited selected equal two-DINO | 93.796 | 66.865 | 38.019 | 33.439 |
| Fixed equal DINO-CLIP | 91.019 | 70.040 | 26.670 | 29.727 |

Mean above50% does not imply every context is feasible. Exact per-source
counts meeting both constraints:

| Fixed system | CASIA | MSU | OULU | SiW | All primary cases |
|---|---:|---:|---:|---:|---:|
| DINO-Reg only | 9/9 | 6/9 | 0/9 | 0/9 | 15/36 |
| Plain-DINO only | 9/9 | 6/9 | 0/9 | 0/9 | 15/36 |
| Supervised CLIP only | 9/9 | 8/9 | 0/9 | 0/9 | 17/36 |
| Fixed equal original two-DINO | 9/9 | 6/9 | 0/9 | 2/9 | 17/36 |
| Inherited selected equal two-DINO | 9/9 | 6/9 | 0/9 | 1/9 | 16/36 |
| Fixed equal DINO-CLIP | 9/9 | 9/9 | 0/9 | 1/9 | 19/36 |

For OULU, DINO-Reg's nine oracle BFA values range32.83%-42.68%;
CLIP's range13.51%-26.01%. No favorable mean hides a passing context.
None of the unattainable cases is caused by a technical-failure BFA ceiling
below50%; the recorded non-acceptances remain included nonetheless.

The fixed heterogeneous reference's19/36 versus other oracle counts is not
a registered fusion win, independent significance test or authority to
choose that system post hoc.

## 5. Inner and within-source contrasts

One-source inner models have oracle-attainable counts:

| System | Oracle-attainable /36 |
|---|---:|
| DINO-Reg only | 9 |
| Plain-DINO only | 12 |
| Supervised CLIP only | 12 |
| Fixed equal original two-DINO | 14 |
| Fixed equal DINO-CLIP | 17 |

Every one-source fixed reference is below50% oracle BFA on every held-out
OULU and SiW case. Thus the original inner-selection obstacle is not
explained only by a misplaced threshold for these fixed references.
This does not exhaust intermediate fusion weights.

Conversely, g_domain has36/36 oracle-attainable cases for each of the six
systems. For DINO-Reg, original within-source utility was already feasible
36/36. This is consistent with strong discrimination inside represented
domains and much worse transfer; it does not replace the primary population
or establish that known-domain behavior transfers to new domains.

## 6. Can one threshold serve multiple sources?

Intersect feasible intervals **only for exactly the same fitted pipeline,
seed, system and diagnostic stage**, never across differently trained
models or averaged scores.

- A one-source pipeline has three held-out source intervals.
- A two-source pipeline has two held-out source intervals.
- A final g_domain pipeline has three represented-source intervals.

For each of DINO-Reg, plain-DINO, fixed original two-DINO and fixed
DINO-CLIP, the18 primary pipeline groups comprise15 with an individually
unattainable source and3 where each source is individually attainable but
the intervals do not intersect. None has a common oracle threshold.

CLIP has16 individually blocked groups and2 with a common oracle interval.
The selected two-DINO reference has15 individually blocked groups,2 with
incompatible individually feasible intervals and1 common interval.
These exceptions do not solve the all-source problem.

All60 one-source/system groups contain an individually unattainable source.
All72 g_domain groups admit a common oracle interval. All240 intersections
are reconstructed and checked by directly evaluating the maximum jointly
FA-safe threshold. These remain hindsight diagnostics, not learned policies.

## 7. Verification, artifacts and reproducibility

- 19 new synthetic tests plus14 directly related contracts pass (33 tests).
- 150 randomized cases agree with exhaustive threshold enumeration.
- Separate `--verify` reconstructs all612 cases and public summaries,
  checks each oracle using an independent complete grouped-score curve,
  and directly verifies all common-interval decisions.
- Repeated verification is read-only and does not overwrite its proof.
- Execution:1.420 seconds,97148928-byte process peak RSS.
- Separate verification:1.337 seconds,97243136-byte process peak RSS.
- Each process is bounded to600 seconds,1GiB checked peak RSS,2 BLAS
  threads and64MiB owned diagnostic output including atomic write copies.
- 0 fits,0 new model predictions,0 encoder forwards,0 new target evaluations.

These are separate producer processes and algorithms, not external
scientific replication. Editor Pylance transport was unavailable; Python
runtime/import tests and the numerical checks above were used instead.
There is no bootstrap confidence interval or population-security claim for
these evaluation-label-selected maxima.

Artifacts:

- [Aggregate result, all612 cases and240 common-threshold groups](../results/phase1/source-oracle316-v1.json).
- [Per-source/seed cases CSV](../results/phase1/source-oracle316-cases-v1.csv).
- [Saved verification proof](../results/phase1/source-oracle316-verification-v1.json).
- [Diagnostic implementation](../scripts/diagnostics/oracle316.py).
- [Synthetic tests](../tests/test_oracle316.py).

Public exports omit individual identities, coefficients, raw score arrays
and oracle threshold values. The code is deliberately under
`scripts/diagnostics/`: adding a flat `scripts/*.py` would alter313's sealed
code inventory. No old scientific code/config/result is modified.

Bindings:

- Public diagnostic JSON:
  `716973dc9358d8352759a2c7b2b5b450e10bbbfde54e426ff6e4b8183f5688d9`.
- Private detailed result:
  `00eb560b3517ed2d922ef4a16c5b150db50cb215ebd90fc0a2fae43ba862edd2`.
- Verification proof:
  `2449f4d97dae91a9d9f8a83c86ae2531945782d3ef36c9f5343aa68378080180`.

```bash
# Original saved inputs and declared FAS numerical environment required:
python scripts/diagnostics/oracle316.py --execute  # immutable, already completed
python scripts/diagnostics/oracle316.py --verify   # repeatable; no fitting
```

## 8. Next-step recommendation, not another execution

Do not open a calibration-only campaign expecting it to rescue all four
domains with these fixed scores. It cannot meet the empirical utility on
OULU even with evaluation-label access.

If pursuing unseen-domain PAD, a future method must improve low-FA
discrimination of the score/decision function, not merely relocate the
threshold. Whether another objective, head or representation can do so is
not established here; neither more epochs nor a new backbone is automatically
justified. If the goal changes to a known deployment site with supervised
adaptation, declare that different setting and require independent held-out
subjects/time/attacks rather than relabel existing source data as confirmation.

No such method is fitted or selected by this diagnostic. Preserve the
negative F1 outcome and all301/305/309 conclusions. These four datasets
remain observed development material.
