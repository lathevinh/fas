# ChatGPT Review — Document 54: Final Core-Plan Synchronization

Date: 2026-09-18  
Repository: `lathevinh/fas`  
Reviewed file: `docs/54-review-response-doc53.md`  
Cross-checked against updated `docs/02`, `05`, `40`, `42`

## Overall verdict

Document 54 is the first response in this review sequence that genuinely synchronizes the core Q3 plan across the normative documents.

The previous 12 synchronization items are now materially reflected in the research questions, experiment plan, paper skeleton, and execution blueprint.

The research plan does **not** need another broad redesign.

I find only four remaining points worth correcting before calling the plan completely frozen.

None requires a new architecture, dataset, model, or research question.

---

# 1. The base-classifier competence rule is slightly over-constraining the scientific question

Document 54 freezes the competence artifact for:

- DINOv2-Reg;
- OpenCLIP;
- heterogeneous average;
- same-family average.

It requires each affected classifier/system to satisfy approximately:

\[
AUROC_{macro}\ge0.55,
\]

\[
BA_{macro}\ge0.55,
\]

with AUROC LCB \(>0.50\), finite/nonconstant scores, and event-count checks.

The intent is good: prevent the paper from studying failure-risk estimation on degenerate classifiers.

However, requiring **every individual branch**, especially frozen OpenCLIP, to pass the same competence threshold may be stronger than necessary for RQ1.

A weak second branch can still contain useful complementary information when combined with a competent primary classifier.

For example:

\[
AUROC_V=0.53
\]

does not logically imply that:

\[
[\widehat p_D,\widehat p_V]
\]

contains no useful failure information beyond DINO alone.

## Recommendation

Separate:

### Reference-system competence — mandatory for RQ1

The final heterogeneous classifier:

\[
g_{DV}
\]

must pass the competence rule.

The DINOv2-Reg anchor should also be non-degenerate.

### Individual-branch competence — descriptive / claim-specific

If OpenCLIP fails the standalone competence threshold:

- do not claim it is a competent standalone PAD classifier;
- but do not automatically block RQ1 if the fixed heterogeneous classifier remains competent and the VLM score adds measurable risk information.

For RQ2, each complete system should pass the system competence rule.

This preserves the scientific question:

> does domain-OOF improve failure-risk supervision for the fixed classifier?

without accidentally turning it into:

> every constituent model must independently be a good FAS classifier.

---

# 2. RQ2 still needs one scalar primary decision rule, not a bundle of outcomes

The synchronized RQ2 now correctly compares complete heterogeneous and same-family systems.

But H2 says primary evidence combines:

- classification errors;
- `FA_end2end`;
- `BFNR_end2end`;
- class coverage;
- selective utility/AURC;

according to a "preregistered system-level rule."

The documents still need that exact rule to be explicit enough that the result cannot be chosen after target evaluation.

Otherwise one could later say:

- system A wins because FA is better;
- or system B wins because BFNR is better;
- or AURC decides;
- or coverage decides.

## Recommendation

Choose one primary RQ2 outcome and treat the rest as guardrails/support.

For example:

### Preferred simple rule

Primary:

\[
\Delta AURC_{system}
\]

or a clearly defined source-selected selective-utility scalar.

Security/usability guardrails:

\[
FA_{end2end}
\]

must not worsen beyond a frozen tolerance, and:

\[
BFNR_{end2end}
\]

must not worsen beyond another frozen tolerance.

Alternatively, define a lexicographic rule:

1. security non-inferiority;
2. then lower BFNR / higher coverage;
3. then AURC.

The exact choice matters less than having **one deterministic decision rule**.

Do not leave "whole-system outcome" as an informal multi-metric judgment.

---

# 3. The primary RQ1 pass rule should explicitly state how seed-level deltas become one target-level delta

Document 54 closes event eligibility:

- \(N_{error,min}=20\) per target and seed;
- target eligible if at least two of three seeds meet the count;
- at least three eligible targets required.

Good.

But the final directional rule still needs one explicit aggregation statement.

For target \(t\), there are three seed-level effects:

\[
\Delta_{t,1},\Delta_{t,2},\Delta_{t,3}.
\]

The documents should state exactly what becomes:

\[
\Delta_t.
\]

## Recommendation

Use the simple preregistered rule:

\[
\boxed{
\Delta_t
=
\frac{1}{3}
\sum_{s=1}^{3}\Delta_{t,s}
}
\]

or, if an underpowered seed is excluded from target-level claim aggregation:

\[
\Delta_t
=
\frac{1}{|S_t^{eligible}|}
\sum_{s\in S_t^{eligible}}\Delta_{t,s}.
\]

I prefer the first option:

- always report all three seeds;
- event eligibility determines whether the target may support the claim;
- do not silently drop an inconvenient seed from the point estimate.

Then:

\[
\Delta_{macro}
=
\frac14\sum_t\Delta_t.
\]

Bootstrap and seed variability remain separate.

This prevents ambiguity later.

---

# 4. The `N_error,min=20` rule is reasonable, but "independent errors" should mean independent transactions, not errors assumed statistically independent

Document 54 says:

> 20 independent target video errors.

Since multiple videos may come from the same subject, those errors are not necessarily statistically independent.

The rest of the protocol correctly cluster-bootstraps by subject/video.

## Recommendation

Use wording:

> at least 20 erroneous target transactions/videos, with dependence handled by the preregistered subject/video cluster bootstrap.

If the dataset has reliable subject IDs, 20 errors from 5 subjects should not be rhetorically presented as 20 independent events.

No numerical change is required.

This is a terminology/statistics cleanup.

---

# 5. The RQ1 synchronization is now strong

The updated RQ1 is now correctly centered on:

\[
\boxed{
\Delta_{OOF}^{AP}
=
AP(e,r^{domain})
-
AP(e,r^{sample})
}
\]

for the same final classifier errors.

Selective utility is now secondary operational validation.

This is exactly the clean separation needed for the Q3 paper.

No further change recommended.

---

# 6. The complete-construction claim is now correctly bounded

The updated documents explicitly say that RQ1 tests:

\[
\text{the complete domain-OOF construction}
\]

rather than a causal effect of domain identity alone.

Required diagnostics now include:

- fit size;
- OOF error prevalence;
- error composition;
- branch score/calibration distributions;
- risk-feature distributions.

This is strong and should remain unchanged.

---

# 7. Track A is correctly demoted

Track A is now outside the four main tables and only provides compact/supplementary literature context.

This matches the actual scientific priority.

Do not promote it again.

The paper should be readable even if the reader skips Track A entirely.

---

# 8. The failure-risk terminology is now correct

The default output is now a:

> failure-risk score.

Probability-language is conditional on:

- Brier;
- NLL;
- reliability checks.

This avoids an unnecessary calibration claim.

Keep this.

---

# 9. The with/without-q attribution is now in the right place

The main RQ1 analysis visibly compares:

\[
R_{DVd}
\]

with and without quality features \(q\).

This is important because domain-OOF may learn transferable nuisance information.

The interpretation is now appropriately bounded:

- branch-only gain -> stronger evidence for predictor-output failure information;
- gain only with \(q\) -> transferable nuisance/failure signatures.

No further change required.

---

# 10. The complementarity scope is now appropriate for a Q3-first paper

Required:

- DINO;
- OpenCLIP;
- fusion;
- same-family control;
- joint correctness/double fault;
- simple rescue summary.

Optional:

- supervised CLIP head;
- shared-head diversity;
- extensive oracle analysis;
- CMI.

This is much better scoped.

Do not re-expand it before seeing results.

---

# 11. Four-domain inference language is now appropriately conservative

The paper now limits its conclusion to:

> consistency across the evaluated MCIO held-out domains.

That is statistically appropriate.

Do not claim population-level proof over all future capture domains.

---

# Final required changes

I recommend exactly four final edits:

1. Make the competence rule mandatory for the **reference/complete systems**, not automatically a kill criterion for every individual branch.
2. Define one deterministic **primary RQ2 whole-system decision rule**.
3. Define explicitly how three seed-level RQ1 deltas form one target-level delta.
4. Replace "20 independent video errors" with "20 erroneous transactions/videos", with dependence handled by cluster bootstrap.

After these four edits, I do not see a scientific reason for another broad planning review.

---

# Final verdict

\[
\boxed{
\text{DOCUMENT 54 IS SUBSTANTIVELY ACCEPTED}
}
\]

The Q3 research plan is now coherent, synchronized, and narrow enough to execute.

The remaining four edits are decision-rule cleanup, not method changes.

The core paper should now remain:

\[
\boxed{
\text{strict single-image source-domain OOF failure-risk transfer}
}
\]

with:

\[
\boxed{
domain\text{-}OOF
\;vs\;
matched\ sample\text{-}OOF
}
\]

as the central experiment.

Once these four points are fixed, freeze the plan and move to Phase 0 implementation.
