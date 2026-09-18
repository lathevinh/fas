# ChatGPT Review — Document 48: Response to Document 47

Date: 2026-09-18  
Repository: `lathevinh/fas`  
Reviewed file: `docs/48-review-response-doc47.md`

## Overall verdict

Document 48 is a strong response and successfully closes most of the Track-A execution gaps raised in Document 47.

The core Q3 research plan remains coherent and should stay frozen.

No new architecture, research question, or novelty mechanism is needed.

The remaining issues are now almost entirely about **metric semantics and the strength of Track-A comparability claims**.

The most important corrections are:

1. `tau^A_HTER` is misnamed because its selection rule is EER-like, not HTER-minimizing;
2. `TPR@FPR=1%` is easy to misinterpret in PAD when attack is the positive class;
3. Track-A detector-success-only metrics are no longer evaluated on the exact effective sample set used by published SSDG;
4. one shared `track_a_validation` set is now used for checkpoint selection, calibration, and threshold selection, which is acceptable for context but should be explicitly described as source-optimized;
5. Track A should not support superiority claims against target-aware published SSDG numbers.

---

# 1. The lightweight Track-A split now makes the execution recipe complete

This correction is appropriate:

```text
track_a_fit
track_a_validation
```

`track_a_validation` is used for:

- DINO checkpoint selection;
- affine branch calibration;
- source operating-threshold selection.

This is sufficient for Track A and avoids importing the full Track-B risk infrastructure.

No additional split is necessary for a Q3-first paper unless data availability later proves generous.

However, the manuscript should explicitly call the resulting Track-A pipeline:

> source-optimized on a single held-out source validation partition

rather than implying independent validation of every stage.

---

# 2. Major terminology issue: `tau^A_HTER` is not selected by minimizing HTER

Document 48 defines:

\[
\tau^A_{HTER}
\]

by minimizing:

\[
|APCER-BPCER|.
\]

That is an **equal-error-style** criterion.

It is not the same as minimizing:

\[
HTER(\tau)
=
\frac{APCER(\tau)+BPCER(\tau)}{2}.
\]

These two thresholds can differ.

## Recommendation

Choose one of two clean definitions.

### Option A — source EER-style threshold

Keep the current rule:

\[
\tau^A_{EER}
=
\arg\min_\tau
|APCER_{macro}(\tau)-BPCER_{macro}(\tau)|.
\]

Rename it accordingly.

Then report target HTER at:

\[
\tau^A_{EER}.
\]

This is conventional and defensible.

### Option B — HTER-minimizing source threshold

Define:

\[
\tau^A_{HTER}
=
\arg\min_\tau
\frac{
APCER_{macro}(\tau)+BPCER_{macro}(\tau)
}{2}.
\]

Then the name matches the optimization rule.

For literature context, I prefer **Option A** because EER-style source thresholding is easier to interpret and avoids optimizing the exact reported target metric indirectly.

---

# 3. `TPR@FPR=1%` has dangerous PAD semantics

Document 48 defines attack as the positive class.

Therefore:

\[
TPR
=
P(\text{predict attack}\mid attack)
=
1-APCER,
\]

while:

\[
FPR
=
P(\text{predict attack}\mid bona\ fide)
=
BPCER.
\]

So:

> TPR@FPR=1%

actually means:

\[
1-APCER
\quad\text{at}\quad
BPCER\le1\%.
\]

It does **not** mean attack false-accept rate is fixed at 1%.

In biometric/PAD writing, readers may easily interpret “FPR” as the dangerous attack acceptance error.

## Recommendation

Avoid generic ROC terminology in the main PAD table.

Write it explicitly as either:

\[
TPR_{attack}@BPCER=1\%
\]

or equivalently:

\[
APCER@BPCER=1\%.
\]

If the security question instead wants the attack false-accept operating point, use:

\[
BPCER@APCER=1\%.
\]

These are very different operating points.

For the current Track-A literature-context panel, `APCER@BPCER=1%` is acceptable if that is the intended conventional ROC view.

For security interpretation, Track B should remain authoritative.

---

# 4. The 1% operating point needs a finite-sample rule

Document 48 says the 1% point is used:

> when the event count supports that operating point.

That is correct but underspecified.

Because the denominator for:

\[
FPR=P(score\ge\tau\mid bona\ fide)
\]

is the number of bona-fide validation events, a 1% empirical operating point has poor resolution when:

\[
N_{BF}<100.
\]

With equal-domain macro weighting, the issue is even more delicate because one small source domain can dominate the resolution of its own domain contribution.

## Recommendation

Freeze a simple applicability rule.

For example:

- require at least 100 bona-fide validation transactions in each contributing source domain; or
- if this is infeasible, report the operating point as `nominal 1%` and include the achieved source-domain BPCER values.

Do not interpolate a visually convenient 1% point and present it as an observed empirical rate without stating how it was obtained.

---

# 5. Detector-success-only Track-A metrics weaken direct literature comparability

Document 48 makes a sensible practical choice:

> Panel-A classifier metrics use detector-success videos only and report detector coverage separately.

This avoids assigning arbitrary classifier scores after detector failure.

However, it changes the effective evaluation population.

Suppose the pinned SSDG target universe contains:

\[
N
\]

videos, but your frozen detector succeeds on only:

\[
N'<N.
\]

Then your reported AUC/HTER is conditional on:

\[
detector\ success.
\]

Published SSDG numbers use SSDG's own MTCNN preprocessing and may have a different success population.

Therefore even with identical:

- source lists;
- target lists;
- frame indices;
- video aggregation;

the actual classifier metric population is not guaranteed to be identical.

## Recommendation

Use precise wording:

> pre-detection sample membership is pinned to the literature protocol; in-house classifier metrics are conditioned on success of the frozen proposed detector, with coverage reported separately.

Do **not** call the final evaluated classifier set exactly sample-equivalent to SSDG unless detector coverage is 100%.

---

# 6. This also affects the phrase "sample-membership/frame-selection/video-aggregation equivalence"

The narrower phrase adopted in Document 48 is much better than "evaluation equivalence".

But even this phrase should refer to the **preprocessing input ledger**, not necessarily the scored population.

Recommended wording:

> equivalence of the intended pre-detection video membership, selected frame indices, and video aggregation rule.

Then state:

> detector failures may reduce the classifier-score population and are reported through coverage.

That removes the final ambiguity.

---

# 7. Published SSDG AUC is correctly downgraded, but the manuscript should go one step further

Document 48 now recognizes that SSDG AUC is:

- threshold-free at evaluation time;
- still target-aware through checkpoint selection.

Good.

Therefore the paper should never write:

> our source-only method outperforms SSDG under the same protocol

based only on a higher AUC.

The correct wording is:

> historical SSDG values are shown for literature context; differences are not interpreted as a controlled target-blind superiority comparison.

The clean controlled comparisons are the in-house systems under the frozen Track-A source-only recipe.

---

# 8. One validation partition doing three jobs is acceptable, but it creates selection optimism

The same `track_a_validation` partition is used for:

1. checkpoint selection;
2. affine calibration;
3. threshold selection.

This is a practical choice.

For Track A, which exists only as classifier context, I agree with it.

But the result is not an independently validated operating point.

## Recommendation

Add one sentence:

> Track-A operating metrics are source-optimized on a shared validation partition and are intended for literature context, not for certified source performance.

Do not compute a source-validation confidence interval and present it as if it were an independent generalization estimate.

Outer target performance remains the actual generalization observation.

---

# 9. The threshold rule should define candidate thresholds exactly

Document 48 says:

> lowest candidate threshold satisfying macro-source FPR <= 1%.

What are the candidate thresholds?

Possibilities include:

- every unique source score;
- midpoints between sorted scores;
- a fixed numeric grid.

This affects deterministic reproducibility.

## Recommendation

Freeze:

\[
\mathcal T
=
\{-\infty\}
\cup
\{\text{unique validation scores}\}
\cup
\{+\infty\}
\]

or an equivalent deterministic midpoint rule.

Then apply the documented tie-breaking logic.

The same principle should apply to the source EER/HTER threshold.

This is a small detail but easy to unit-test.

---

# 10. Equal-source weighting is scientifically reasonable

Document 48 selects Track-A thresholds using equal source-domain weighting.

That is a good choice for cross-domain evaluation because a large dataset should not dominate the source operating point.

Keep:

\[
APCER_{macro}
=
\frac{1}{3}
\sum_d APCER_d
\]

and:

\[
BPCER_{macro}
=
\frac{1}{3}
\sum_d BPCER_d.
\]

However, report the per-source values at the selected threshold.

A good macro can hide a severe failure on one source domain.

This is descriptive in Track A, not a new claim criterion.

---

# 11. Track A should not introduce another same-family risk comparison

Document 48 says the lightweight split completes the recipe for the same-family classifier control.

That is fine.

But Track A should compare only classifier performance.

Do not add:

- same-family risk estimator;
- selective gating;
- heterogeneity advantage;

under Track A.

Those remain exclusively Track-B scientific questions.

The current response respects this boundary; keep it that way.

---

# 12. The Track-A stop rule remains useful

The two-engineer-day limit is sensible.

The remaining details are now sufficiently narrow that Track A should not consume much research time.

If exact protected-list reconciliation fails, the paper can still show:

- published literature values with clear caveats;
- only verified in-house context results.

This does not affect the core RQ1 experiment.

---

# 13. Core Q3 research plan remains frozen

Nothing in Document 48 changes the main scientific story:

\[
\boxed{
domain\text{-}OOF failure supervision
\;vs\;
matched\ sample\text{-}OOF
}
\]

on the same final classifier errors.

Nor does it change RQ2:

\[
\boxed{
DINOv2\text{-Reg}+OpenCLIP
\;vs\;
DINOv2\text{-Reg}+DINOv2
}
\]

under the matched Track-B selective protocol.

That is good.

Do not use the remaining Track-A benchmark hygiene as a reason to reopen the method.

---

# Required corrections

Before declaring Document 48 completely closed, I recommend:

1. Rename `tau^A_HTER` to an EER-style threshold, or actually minimize HTER.
2. Replace ambiguous `TPR@FPR=1%` wording with PAD-explicit notation such as:
   \[
   APCER@BPCER=1\%
   \]
   or the intended converse.
3. Freeze an event-count/applicability rule for the 1% operating point.
4. Clarify that detector-success-only Track-A metrics are conditional metrics and therefore not evaluated on an identical effective population to published SSDG.
5. Define the deterministic threshold candidate set.
6. State explicitly that `track_a_validation` performs shared source optimization for checkpoint/calibration/threshold and is not an independent validation estimate.

---

# Final verdict

\[
\boxed{
\text{DOCUMENT 48 IS SOUND; ONLY METRIC SEMANTICS NEED FINAL CLEANUP}
}
\]

The Q3 research plan remains frozen.

The biggest correction is not methodological; it is terminological:

\[
\arg\min |APCER-BPCER|
\]

should not be called an HTER-minimizing threshold.

And in PAD, generic `FPR` terminology should be avoided whenever it could be confused with attack false acceptance.

Once these are cleaned up, Track A is sufficiently specified for its intended role as limited literature context.
