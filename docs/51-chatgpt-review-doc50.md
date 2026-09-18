# ChatGPT Review — Document 50: Response to Document 49

Date: 2026-09-18  
Repository: `lathevinh/fas`  
Reviewed file: `docs/50-review-response-doc49.md`

## Overall verdict

Document 50 resolves the main terminology problems from Document 49 correctly.

In particular, it now:

- renames the transferred equal-error-style threshold to \(\tau^A_{EER}\);
- removes generic `TPR@FPR=1%` wording;
- fixes a deterministic threshold candidate set;
- defines a finite-sample applicability rule;
- explicitly conditions Track-A classifier metrics on detector success;
- labels SSDG AUC/HTER as historical target-aware context;
- keeps Track A outside RQ1/RQ2 and outside the core novelty.

The core Q3 plan remains frozen.

I do **not** recommend reopening the method.

However, two remaining semantic details should still be corrected before calling Track A completely closed.

---

# 1. Major issue: target result cannot be called `APCER@BPCER<=1%`

Document 50 defines a source threshold:

\[
\tau^A_{BPCER1}
\]

as the lowest threshold satisfying:

\[
BPCER^{source}_{macro}(\tau)\le 1\%.
\]

That threshold is then transferred unchanged to the held-out target.

This is correct source-only evaluation.

However, the document says the target reports:

\[
APCER@BPCER\le1\%.
\]

That notation is not generally valid.

The source constraint:

\[
BPCER^{source}_{macro}\le1\%
\]

does **not** imply:

\[
BPCER^{target}\le1\%.
\]

Under domain shift the target may achieve, for example:

\[
BPCER^{target}=7\%.
\]

Calling the result:

\[
APCER@BPCER\le1\%
\]

would then falsely imply a target operating point that was never achieved.

## Recommendation

Rename the transferred metric to something explicit, for example:

\[
APCER_{target}(\tau^A_{BPCER1})
\]

and always report beside it:

\[
BPCER_{target}(\tau^A_{BPCER1}).
\]

A table could show:

| Target | Source-selected criterion | Target APCER | Target BPCER |
|---|---|---:|---:|
| OULU | source macro BPCER <= 1% | ... | ... |

Then the claim is unambiguous:

> target performance at a threshold selected to satisfy a 1% bona-fide-error constraint on the source domains.

If the paper also reports conventional target:

\[
APCER@BPCER=1\%
\]

from the target ROC, that must be labeled **post-hoc diagnostic**, not transferred/deployable performance.

This is the most important remaining correction.

---

# 2. Two-frame Track-A detector success is underspecified

Track A uses two pinned target frames per video:

\[
f_1=6,
\qquad
f_2=6+\left\lfloor\frac N2\right\rfloor.
\]

SSDG aggregation averages their class-1 probabilities.

But your Track-A preprocessing uses the frozen Track-B detector, which may fail on:

- neither frame;
- one frame;
- both frames.

Document 50 says classifier metrics use:

> detector-success videos only.

It does not define what constitutes a detector-success **video**.

## Possible policies

### Policy A — complete-pair only

A video is scoreable only if both pinned frames succeed:

\[
success(video)
=
success(f_1)\land success(f_2).
\]

Then:

\[
p_{video}
=
\frac{p(f_1)+p(f_2)}{2}.
\]

This most closely preserves the pinned two-frame aggregation rule.

### Policy B — at least one frame

A video is scoreable when at least one frame succeeds and aggregation uses available frames.

This increases coverage but no longer reproduces the two-frame aggregation rule for partial failures.

### Policy C — fixed failure score

Map failed frames to a predefined score.

This mixes detector behavior with classifier performance and is not ideal for a literature classifier-context panel.

## Recommendation

Use **Policy A** for Track-A classifier comparability:

> both pinned frames must yield valid detector crops for the video to enter classifier metrics.

Report separately:

- frame detector coverage;
- complete-pair video coverage;
- class-conditional coverage.

Track B remains the proper end-to-end evaluation where detector failures become terminal non-accept.

This keeps Track A conceptually simple.

---

# 3. The EER-style threshold correction is now sound

The new definition:

\[
\tau^A_{EER}
=
\arg\min_{\tau\in\mathcal T}
\left|
APCER^{source}_{macro}(\tau)
-
BPCER^{source}_{macro}(\tau)
\right|
\]

with deterministic ties by:

1. lower macro HTER;
2. lower numeric threshold;

is internally consistent.

Target HTER is then correctly described as:

\[
HTER_{target}(\tau^A_{EER}).
\]

No further change is needed.

---

# 4. The deterministic threshold set is adequate

Document 50 freezes:

\[
\mathcal T
=
\{-\infty\}
\cup
\{\text{unique finite validation scores}\}
\cup
\{+\infty\}.
\]

With the decision rule:

\[
score\ge\tau
\Rightarrow attack,
\]

this represents all relevant empirical decision partitions, including the all-live and all-attack extremes.

This is reproducible and unit-testable.

No midpoint grid is required.

---

# 5. The 100-bona-fide rule is acceptable as an applicability rule, not a precision guarantee

Document 50 requires every source domain to have at least:

\[
N_{BF}\ge100
\]

detector-successful bona-fide validation videos before estimating the source 1% constraint.

This is a reasonable minimum-resolution rule because one error corresponds to roughly 1%.

However:

\[
N=100
\]

does not make a 1% error rate statistically precise.

Therefore the manuscript should not interpret this as a certified 1% operating point.

## Recommendation

Keep the rule, but report:

- numerator/denominator;
- per-source achieved BPCER;
- optional binomial interval.

The wording should remain:

> empirical source-selected 1% constraint.

Not:

> statistically guaranteed 1% BPCER.

---

# 6. Macro-source BPCER <= 1% does not guarantee every source domain <= 1%

The threshold is selected using:

\[
BPCER^{source}_{macro}
=
\frac13\sum_{d=1}^{3}BPCER_d.
\]

Therefore it is possible to have:

\[
BPCER_1=0\%,\quad
BPCER_2=0\%,\quad
BPCER_3=3\%
\]

while:

\[
BPCER_{macro}=1\%.
\]

Document 50 already requires per-source reporting, which is good.

## Recommendation

For Track A, macro selection is acceptable.

Do not describe it as:

> BPCER <= 1% on all source domains.

Say:

> equal-domain macro-source BPCER <= 1%.

If a later deployment/security claim requires worst-source control, that belongs to Track B, not this literature-context panel.

---

# 7. Shared source optimization is correctly disclosed

Using `track_a_validation` for:

1. checkpoint selection;
2. affine calibration;
3. operating-threshold selection;

is acceptable for Track A because its purpose is literature context.

The response correctly says this is:

> shared source optimization

rather than independent validation or certification.

Keep this wording.

No additional split is needed for the Q3-first study.

---

# 8. The detector-conditional comparability boundary is now mostly correct

Document 50 correctly states that:

- intended pre-detection membership is pinned;
- frame indices are pinned;
- aggregation rule is pinned;
- in-house classifier metrics are conditional on detector success;
- the effective scored population may therefore differ from SSDG.

This is scientifically honest.

After resolving the two-frame partial-detection rule from Issue 2, the Track-A comparability contract will be sufficiently precise.

---

# 9. Published SSDG values are now appropriately downgraded

Document 50 states:

- SSDG HTER is target-aware through checkpoint selection and target thresholding;
- SSDG AUC is threshold-free but still target-aware through checkpoint selection;
- neither supports a controlled superiority claim.

This is exactly the right interpretation.

The controlled comparison should be among your own in-house systems under the same source-only Track-A recipe.

No further change needed.

---

# 10. One paper-presentation recommendation

Panel A now contains multiple kinds of numbers:

### Historical published values

Potentially target-aware and using their own preprocessing.

### In-house Track-A values

Source-only, frozen detector, shared Track-A recipe.

Make this visually explicit.

For example:

```text
Published literature context
----------------------------
SSDG ...
FLIP ...

Our source-only Track-A systems
-------------------------------
DINOv2-Reg ...
OpenCLIP ...
DINO+OpenCLIP ...
```

Do not create a single `Best` column spanning both groups.

This is already consistent with the current contract.

---

# 11. Track A should now stop generating review work

After correcting:

1. transferred 1%-threshold metric naming;
2. partial detector-failure aggregation;

I would consider Track A sufficiently specified.

Further refinement of Track A is unlikely to improve the scientific paper.

The research effort should remain focused on the core Track-B question:

\[
\boxed{
AP(e,r^{domain\text{-}OOF})
>
AP(e,r^{sample\text{-}OOF})
}
\]

under the matched fixed-error design.

---

# Final required corrections

## Must fix

1. Replace target `APCER@BPCER<=1%` with:
   \[
   APCER_{target}(\tau^A_{BPCER1})
   \]
   and report achieved:
   \[
   BPCER_{target}(\tau^A_{BPCER1}).
   \]

2. Define Track-A video detector success for the two pinned frames. Recommended:
   both frames must succeed for classifier-only video metrics.

## Clarify

3. The 100-video rule provides empirical resolution, not statistical certification.
4. The 1% constraint is **macro-source**, not worst-source.

---

# Final verdict

\[
\boxed{
\text{DOCUMENT 50 IS SOUND; TWO SMALL BUT IMPORTANT SEMANTIC GAPS REMAIN}
}
\]

The core Q3 research plan remains frozen.

The main outstanding issue is that a threshold satisfying a source-domain constraint cannot be named as though the same constraint is achieved after transfer:

\[
BPCER^{source}\le1\%
\not\Rightarrow
BPCER^{target}\le1\%.
\]

Once this and the two-frame detector-success rule are fixed, I recommend ending the Track-A review loop and moving attention back to the core Track-B experiment.
