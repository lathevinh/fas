# 324 - Completed operating-transfer comparison and manuscript results

Date: 2026-10-29.
Status: **all12 contexts complete and independently reconstructed.**
This report publishes measured comparison results, not an unfinished-run
narrative or a claim that timeout is a scientific contribution.

## 1. Decision and scientific answer

At the declared primary utility, attack FA<=5% and bona-fide acceptance
BFA>=50%, **none of48 available source-derived policies succeeds**.
Fifteen meet the FA constraint alone. In contrast, evaluation-label oracle
thresholds on the same saved scores admit the joint utility in21/48 cases;
the other27 have insufficient empirical low-FA scalar-score separation.

These are48 system/target/seed cases, not48 independent datasets or trials.
Their target observations overlap across seeds and systems.
Oracle attainment is a hindsight diagnostic, not a deployable policy or
evidence that target-label-free threshold transfer can recover the headroom.

The specialist matters: it supplies3/3 oracle-attainable OULU cases where
all three frozen systems supply0/3 each. Yet all specialist source policies
on OULU remain FA-unsafe. Its performance is not universally better:
specialist oracle attainment is2/3 on CASIA,1/3 on MSU and0/3 on SiW.

**CLIP decision:** retain supervised CLIP as a comparator. Its MSU oracle
BFA exceeds DINO-Reg's, so the evidence does not justify calling CLIP
universally useless. Nothing here demonstrates incremental DINO-CLIP
fusion utility: the official-partition study has no such fusion system,
and the separate developmental matched selectors found no feasible policy.
Do not promote CLIP into a fusion architecture from these hindsight results.

## 2. Public evidence: all cases, not a best-seed table

| Artifact | Contents |
|---|---|
| [Aggregate closure](../results/phase1/paper324-comparison-v1.json) | Source hashes, successful terminal, independent verification,144 cases, all conditional/paired intervals, per-target seed ranges and36 macro/worst-target summaries |
| [Cases CSV](../results/phase1/paper324-cases-v1.csv) | All144 target/seed/system/alpha cases, integer supports and acceptances, original/usable-denominator rates, oracle results and source attack budgets |
| [Intervals CSV](../results/phase1/paper324-intervals-v1.csv) |756 records:432 conditional policy intervals and324 paired differences against DINO-Reg |
| [Target/system summary CSV](../results/phase1/paper324-target-summary-v1.csv) |48 descriptive summaries over three seeds, including seed minima/maxima and feasibility counts |
| [Complete primary tables](../results/phase1/paper324-primary-tables-v1.md) | All48 primary rows with support, counts and intervals; all108 primary paired metric differences |
| [Low-FA figure](../results/phase1/paper324-low-fa-v1.svg) | Four targets, four systems, every training seed and policy markers |

The [exporter](../scripts/paper324/export.py) requires a successful terminal,
the exact published323 plan, unchanged sealed scientific code/specification,
explicit approval and a bound no-fit reconstruction receipt. It independently
checks each saved oracle against the grouped ROC, all144 system/alpha cases,
integer feasibility, complete uncertainty inventories and reconstructed
macro summaries. It runs no fitting, prediction, new bootstrap or policy
selection. Export verification reproduces every published artifact byte.

No private images, subject/video identifiers, membership lists, coefficients,
checkpoints or individual scores are published.

## 3. Population and primary result table

The active population is7505 originals,7474 usable,31 technical failures,
including all source and target official partitions. Evaluation uses2943
target-test originals and2929 usable images, not all7505 as test samples.

| Target | Original attacks / BF | Usable attacks / BF | Technical failures |
|---|---:|---:|---:|
| OULU-NPU |1440 /360|1440 /360|0|
| CASIA-FASD |270 /90|265 /89|6|
| MSU-MFSD |120 /40|116 /40|4|
| SiW-Mv2 local test intersection |362 /261|359 /260|4|

SiW remains the adopted Protocol-I local intersection, not full-release
evaluation or participant-disjoint certification. Its resampling/model-
selection units are video/exact-frame components because subjects are unknown.
Other datasets use known-subject/exact-frame components.

Percentages below are equal means over the three training seeds. AUROC
uses usable images; policy FA/BFA and oracle BFA use all-original class
denominators with technical failures retained as nonacceptances.
Seed means are descriptive, not pooled estimates with invented CIs.

| Target | System | AUROC | Policy FA | Policy BFA | Oracle BFA at5% FA | FA-safe /3 | Policy utility /3 | Oracle utility /3 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| OULU | DINO-Reg |87.77|36.13|91.94|46.67|0|0|0|
| OULU | Supervised CLIP |79.20|16.62|53.70|23.43|0|0|0|
| OULU | Fixed two-DINO |86.60|58.87|97.13|41.11|0|0|0|
| OULU | Matched DeepPixBiS |91.98|15.12|81.11|58.70|0|0|3|
| CASIA | DINO-Reg |99.94|0.00|39.26|98.89|3|0|3|
| CASIA | Supervised CLIP |98.20|0.00|46.67|85.56|3|0|3|
| CASIA | Fixed two-DINO |99.94|0.00|40.37|98.89|3|0|3|
| CASIA | Matched DeepPixBiS |86.61|1.48|42.59|54.81|3|0|2|
| MSU | DINO-Reg |87.56|41.67|90.00|42.50|0|0|0|
| MSU | Supervised CLIP |89.22|9.17|65.00|57.50|0|0|3|
| MSU | Fixed two-DINO |92.67|22.78|92.50|68.33|0|0|3|
| MSU | Matched DeepPixBiS |92.98|8.89|79.17|52.50|0|0|1|
| SiW | DINO-Reg |88.01|9.67|58.24|34.87|0|0|0|
| SiW | Supervised CLIP |85.02|3.59|31.42|38.19|3|0|0|
| SiW | Fixed two-DINO |87.38|16.02|74.33|45.72|0|0|0|
| SiW | Matched DeepPixBiS |76.00|49.82|87.36|23.75|0|0|0|

### Reading the contrast correctly

- **CASIA:** all12 policies satisfy empirical FA<=5%, but none reaches50%
  BFA. Oracle attainment11/12 supplies substantial score-specific headroom.
  DINO-Reg policy/oracle mean BFA is39.26%/98.89%.
- **OULU:** all12 policies are FA-unsafe. The specialist has56.39--61.94%
  oracle BFA across seeds, unlike the frozen systems. This is a changed
  score diagnosis, not a working specialist source policy.
- **MSU:** oracle attainment7/12 is system/seed-dependent. CLIP mean oracle
  BFA57.50% exceeds DINO-Reg42.50%, but this does not establish source-policy
  superiority or a target-label-free remedy.
- **SiW:** all12 scores remain oracle-infeasible at the primary utility.
  CLIP's three FA-safe policies accept only31.42% of bona-fide originals.
  The grouping/coverage limitations preclude broad participant-level claims.

On FA-unsafe policies, a difference between policy BFA and constrained
oracle BFA is **not a same-security calibration loss or recoverable gain**.
All27 primary oracle-infeasible cases have the saved reason
`low_FA_score_separation_insufficient`, not a technical-failure ceiling
below50%. This statement concerns the stored scores and observed samples.

## 4. Conditional paired uncertainty and sensitivities

All756 interval records have2000/2000 valid paired cluster-bootstrap draws.
The source threshold and fitted model remain fixed within each context.
There are no primary oracle confidence intervals and no confidence interval
for an average that pools seeds as independent test populations.

Examples, not a replacement for the complete table:

| Paired usable-AUROC difference, percentage points | Seed20260917 | Seed20260923 | Seed20261001 |
|---|---:|---:|---:|
| OULU specialist minus DINO-Reg |+4.49 [1.06,7.68]|+4.23 [1.03,6.96]|+3.90 [0.69,6.80]|
| CASIA specialist minus DINO-Reg |-15.82 [-21.27,-11.07]|-13.47 [-17.37,-9.90]|-10.70 [-14.24,-7.21]|
| MSU CLIP minus DINO-Reg |+1.55 [-5.27,9.12]|+1.66 [-5.15,9.28]|+1.79 [-5.13,9.53]|

These intervals are conditional, exploratory and not multiple-testing-
adjusted. The MSU CLIP intervals all include zero. The opposite specialist
directions on OULU and CASIA argue against a universal architecture ranking,
not for pooling seeds into a significance claim. A zero observed FA with
a degenerate bootstrap interval cannot certify zero population attack risk.

| Predeclared attack-FA constraint | Cases | Policy FA-safe | Policy joint utility | Oracle joint utility |
|---|---:|---:|---:|---:|
|1%|48|22|0|12|
|5%, primary|48|15|0|21|
|10%|48|15|10|42|

Transferred FA-safe policy counts need not increase with alpha because
source thresholds also change. The10% sensitivity does not replace the
primary endpoint after seeing the results.

## 5. Execution lineage and closure

The [323 amendment](323-completing-comparison-after-analysis-timeout.md)
was explicitly approved by the owner after34 focused regressions and
actual saved-analysis equivalence checks. It preserved the fixed recipe
and bound parent artifacts while replacing the expired combined context
clock with disclosed phase budgets.

| Item | Observed |
|---|---:|
| Target/seed contexts and primary system cases |12 /48|
| All policy/oracle operating cases |144|
| Reused complete322 contexts |4|
| New323 frozen-head /specialist /calibrator starts |24 /7 /32|
| Cumulative322+323 starts |39 /12 /52|
| Explicit deterministic recovery refits |3 heads +4 calibrators;0 specialist|
| Specialist epochs /optimizer steps across322+323 |600 /74400|
| New foundation-encoder forwards /export fits or predictions |0 /0|
| Independent reconstruction |12/12 contexts;0 new fits|
|323 wall time, including verification |32643.848698 seconds,9.07h|
| Combined sampled peak RSS |2359939072 bytes,2.20GiB|
| Owned outputs across attempts before terminal |288950836 bytes,275.56MiB|
| Final status /failure /automatic retry |`complete` /null /false|

The323 wall time excludes prior stopped321/322 wall time and implementation
work. RSS is sampled, not an unsampled instantaneous kernel-enforced maximum.
Operational amendments and recovery costs are visible, not hidden within
the original36-head/48-calibrator inventory.

Important SHA256 bindings:

-323 private plan:
  `4f7dd4a8649c4654c07680b0653d3a5821342176be0b67904e7bb62fc8378d67`.
- Scientific worker completion:
  `1cc3c948d8071533cfaab5cc0f6b3a081c65877a6286cf9dd89367d8529f8e63`.
- Public aggregate closure:
  `5dea308b3170310dc14017166e4af196fdcdfb1d95a35be41f56e1f7b12e32c6`.

The scientific321-323 code, tests, protocol and original sealed reports
are not edited by this publication. New export code lives in the separate
[paper324 directory](../scripts/paper324/), outside those code pins.

## 6. Manuscript decision and issues for critique

The [manuscript](paper319/manuscript.md) now reports completed methods,
measured primary results, conditional differences, sensitivity and
execution accounting rather than pending result cells.
The [positioning brief](paper319/related-work-and-venues.md) is updated
with the completed evidence, not a fabricated new literature search.

The candidate contribution is **a controlled empirical characterization
of available-policy failure versus low-FA score limitations**, including
the specialist counterexample on OULU and explicit dataset/seed dependence.
It is not a new ROC method, a new backbone, a successful adaptation method,
or proof that all frozen representations, specialist PAD or fusion fail.

The next review should challenge:

1. Whether this precise available-policy/oracle comparison adds sufficient
   empirical insight beyond the closest frozen-model and constrained-ROC work.
2. Whether the researcher-fixed specialist recipe and unequal architecture/
   pretraining/compute make the contextual comparison fair enough, without
   presenting it as exact original-paper reproduction or causal isolation.
3. Whether the explicit SiW video-group/local-coverage limitation is acceptable
   for the intended empirical claim, rather than silently treating it as
   participant-independent benchmark evidence.
4. Whether limited source calibration supports and integer attack budgets
   adequately explain the threshold rule's scope; no5% population security
   guarantee follows from these empirical budgets.

Do not start a new model campaign merely to improve these numbers.
Current results can support a concrete critique and venue-fit decision,
not a promise of Q3 acceptance. Exact provider/year/category quartile
evidence and current publisher charges remain unverified in the
[venue brief](paper319/related-work-and-venues.md); neither submission nor
payment is authorized. Author metadata, bibliographic formatting and
closest-work positioning still require final editorial decisions.

## 7. Publication validation

All594 local repository unittest regressions passed in the existing `fas`
environment, including37 focused paper-preparation/continuation/export
tests. Canonical schema validation passed. The six public products were
rebuilt and verified byte-for-byte; all32 manually transcribed result rows
across this report and the manuscript were checked against exported values.
All local links resolved, the SVG contained all48 system/seed curves, and
the public closure was checked for prohibited individual-data fields.
No new scientific fit or prediction was performed during publication.

Reproduce the aggregate export in the existing project environment:

```sh
/home/lathevinh/miniforge3/envs/fas/bin/python scripts/paper324/export.py --verify
```
