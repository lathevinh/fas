# ChatGPT Review — Document 52 and Final One-Pass Q3 Plan Audit

Date: 2026-09-18  
Repository: `lathevinh/fas`  
Primary reviewed file: `docs/52-review-response-doc51.md`  
Cross-checked: `docs/02`, `03`, `04`, `05`, `40`, `42`

## Executive verdict

Document 52 correctly closes the Track-A review loop.

I agree with the new project priority:

\[
\boxed{
\text{strict single-image Track B is the paper}
}
\]

while literature-compatible Track A is only enough to show that the base classifier is not obviously weak relative to existing FAS work.

I recommend **no further Track-A methodological review** unless implementation reveals a concrete incompatibility.

However, before declaring the whole Q3 research plan frozen, there are several remaining inconsistencies across the core documents. They should be corrected **in one synchronization pass**, rather than discovering them one by one later.

No new architecture is required.

---

# A. MUST-FIX BEFORE FINAL PLAN FREEZE

## 1. RQ1 currently mixes the scientific endpoint and deployment utility

`docs/02-research-questions.md` currently asks whether domain-OOF improves both:

- failure ranking;
- selective security-usability.

Its H1 also requires both.

But `docs/40-paper-skeleton.md` correctly says the primary scientific question is:

\[
\boxed{
\Delta_{OOF}
=
AP(e,r^{domain})
-
AP(e,r^{sample})
}
\]

and selective utility is downstream operational validation.

These are not the same hypothesis.

A risk estimator can rank errors better yet fail to improve one particular source-selected operating point.

Conversely, one favorable gate threshold does not prove generally better failure ranking.

### Fix

Rewrite RQ1 as:

> Does source-domain OOF failure supervision improve transferable prediction-error ranking over matched sample-OOF supervision for the same final classifier errors?

Primary endpoint:

\[
\Delta_{OOF}^{AP}>0.
\]

Then define a **secondary operational consequence**:

> Does the improved ranking translate into a better source-selected security-usability trade-off?

Do not make failure of one gate operating point automatically falsify RQ1.

This should be synchronized in `02`, `05`, and the claim matrix.

---

## 2. RQ2 is inconsistent between the RQ document and paper skeleton

`docs/02` currently frames RQ2 partly as:

> do cross-foundation probabilities improve risk estimation beyond either branch and the same-family pair?

But `docs/40` correctly recognizes that heterogeneous and same-family systems have:

- different classifiers;
- different error labels;
- different risk problems.

Therefore raw risk AP across the two systems is not a controlled estimator comparison.

### Fix

Make RQ2 exactly:

> Does the complete DINOv2-Reg + OpenCLIP selective system provide better held-out-domain system outcomes than a matched DINOv2-Reg + plain-DINOv2 selective system?

Primary evidence should be whole-system outcomes:

- classifier errors;
- `FA_end2end`;
- `BFNR_end2end`;
- class coverage;
- AURC/selective utility.

Each system's error AP remains descriptive.

Remove wording implying that higher cross-system risk AP alone proves heterogeneous predictive value.

---

## 3. The "secondary attribution hypothesis" reads like a third research question

Inside RQ2, `docs/02` still contains:

> Can a source-only cross-fitted risk model ... and does explicit disagreement add value...?

This is effectively another RQ.

It also mentions:

> domain and attack shift

even though SiW-M attack shift is optional for the first Q3 paper.

### Fix

Move this material into:

> **Attribution ablations**

with only:

\[
\Delta_{CF}^{AP}
\]

and:

\[
\Delta_{dis}^{AP}.
\]

Do not present it as an additional research question.

Remove attack-shift language from the core question. SiW-M remains optional external validation.

The paper should visibly contain only two RQs.

---

## 4. The primary paper table structure should now demote Track A

The user has correctly decided that strict single-image evaluation is the paper's main protocol.

The current `docs/40` still defines Table 1 as:

- Panel A: literature-compatible Track A;
- Panel B: strict single-image Track B.

This gives Track A too much visual status relative to its scientific role.

### Recommended final paper structure

### Main Table 1 — Strict single-image classifier competence

Track B only:

- DINOv2-Reg;
- OpenCLIP;
- heterogeneous average;
- same-family average.

### Main Table 2 — RQ1

Domain-OOF vs sample-OOF and fixed-error baselines.

### Main Table 3 — Selective utility

Source-selected risk gates and K=1 outcomes.

### Main Table 4 — RQ2

Heterogeneous vs same-family complete systems.

### Literature context

Move Track A to:

- a small preliminary/context table;
- supplementary material;
- or one compact subsection.

The goal is only:

> our classifier is not obviously incompetent relative to established MCIO literature.

Track A should not consume one half of the main classifier table.

This change better reflects the actual novelty hierarchy.

---

## 5. The "minimum base-classifier competence criterion" is repeatedly referenced but not actually defined

Several documents say Track-A competitiveness is not required and only a:

> separately frozen minimum base-classifier competence criterion

matters.

But the criterion itself is not concretely defined in the normative core documents.

This is currently a dangling decision rule.

### Fix

Before real target evaluation, define a source-only competence rule.

It does **not** need to demand SOTA.

For example, it may require that the fixed branches and reference classifier are:

- non-degenerate;
- meaningfully above chance on source pseudo-shifts;
- able to produce enough errors for risk estimation without pathological collapse.

The exact numeric threshold should be frozen from source-only evidence before target results.

Important:

> target performance must not be used to decide whether the method is "competent enough" and then alter the method.

The target only reports the result.

---

## 6. RQ1 still has a difficulty/prevalence confound that must be explicitly acknowledged

Domain-OOF and sample-OOF use the same candidate universe and risk model, which is good.

But their OOF predictors are structurally different.

For a source set:

\[
S_1,S_2,S_3,
\]

domain-OOF prediction on \(S_3\) trains branches only on:

\[
S_1,S_2.
\]

Sample-OOF prediction for records from \(S_3\) can train on other subjects from:

\[
S_1,S_2,S_3.
\]

Therefore domain-OOF records are likely to contain:

- more errors;
- more extreme shift;
- different probability distributions;
- different calibration difficulty.

That is partly the intended pseudo-domain-shift mechanism.

But it means the study does **not** isolate a pure mathematical effect of "domain labels versus sample labels".

It estimates the effect of the **complete domain-OOF construction**.

### Fix

State this directly in the paper:

> RQ1 tests the complete source-domain OOF supervision procedure, not a causal effect of domain identity alone.

Required diagnostics:

- OOF error prevalence by strategy;
- error type composition;
- branch probability distributions;
- risk-feature distributions;
- effective fitting-set sizes.

Strongly recommended diagnostic:

- a source-only prevalence/difficulty-matched weighting sensitivity, where feasible, to check whether the gain survives simple differences in error abundance.

Do not overclaim:

> domain structure itself causes the gain.

The valid claim is:

> the domain-OOF construction yields more transferable failure supervision.

---

## 7. Define a minimum error-event rule for the primary AP endpoint

RQ1 uses prediction-error average precision:

\[
AP_{error}.
\]

If a target classifier makes very few errors, AP becomes highly unstable.

The current documents handle:

- one-class labels;
- false-accept event scarcity;

but do not define a general minimum number of error events for the primary RQ1 ranking endpoint.

### Fix

Before targets, freeze:

\[
N_{error,min}.
\]

If a target has fewer than this number of classifier errors:

- report AP;
- report counts and uncertainty;
- mark that target's RQ1 contribution as underpowered/inconclusive according to the predefined rule.

Do not conflate:

> very few errors

with either:

> perfect risk estimation

or:

> evidence against the hypothesis.

This is more important for strict one-frame-per-video evaluation because target sample counts are smaller than frame-level evaluations.

---

## 8. Default terminology should be "failure-risk score", not calibrated failure probability

`docs/03` currently writes:

\[
r_\theta(z)\approx P(e=1\mid z).
\]

But the primary logistic model uses:

- equal pseudo-domain weighting;
- fold-dependent source constructions;
- natural error prevalence within each pseudo-domain.

This does not automatically imply a calibrated deployment posterior probability.

The dossier later correctly says Brier/NLL and reliability must support calibrated-probability language.

### Fix

Make the default method output:

\[
r_\theta(z)=\text{failure-risk score}.
\]

Only call it a calibrated:

\[
P(error\mid z)
\]

if held-out source validity checks justify that wording.

This avoids an unnecessary probabilistic claim.

---

# B. STRONGLY RECOMMENDED CLEANUP

## 9. Make the with/without-quality-feature comparison a first-class attribution result

The primary feature set contains:

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

These variables can strongly identify capture domains.

If domain-OOF wins mainly because \(q\) identifies source shift, that is scientifically interesting but different from a claim about cross-foundation disagreement.

### Fix

Always report:

\[
R_{DVd}
\]

with and without \(q\).

Interpretation:

### If both win

Strong support that branch outputs themselves transfer useful failure information.

### If only `+q` wins

The main result becomes:

> domain-OOF learns transferable failure/nuisance signatures.

Do not then emphasize heterogeneous disagreement as the mechanism.

This should be visible in the main RQ1 ablation, not hidden in supplementary material.

---

## 10. Domain-ID predictability audit must remain diagnostic, not a route to changing the primary model

`docs/03` says high domain predictability can trigger feature-removal/normalization ablations.

That is fine as analysis.

But the primary feature set has already been frozen.

### Fix

State:

> domain-ID audit never changes the preregistered primary RQ1 feature set after target evaluation.

Any feature-removal result is:

- a source-only predefined sensitivity;
- or a secondary attribution analysis.

This prevents an apparently innocuous audit from becoming researcher-driven feature selection.

---

## 11. Reduce required classifier-complementarity analyses

`docs/02` still calls many things required:

- joint correctness;
- oracle gain;
- shared-encoder head-diversity control;
- supervised visual head on VLM image encoder;
- multiple directional rescue measures;
- etc.

For a Q3-first paper centered on failure-risk transfer, this is too much.

### Keep as required

- standalone DINO;
- standalone OpenCLIP;
- fixed heterogeneous fusion;
- same-family DINO-Reg + DINO control;
- joint correctness/double fault;
- simple rescue summary.

### Move to optional/appendix

- supervised visual head on CLIP image encoder;
- shared-encoder two-head diversity;
- conditional mutual information;
- extensive oracle diagnostics.

They do not determine RQ1.

This reduces implementation scope substantially without weakening the paper.

---

## 12. Clarify uncertainty interpretation for the four-target macro

The bootstrap procedure resamples subjects/videos within each target and then averages target-specific effects.

That is reasonable.

But it estimates uncertainty conditional on:

- these four datasets;
- the fitted training procedures.

It does not estimate uncertainty over the universe of all possible future capture domains.

### Fix

Use wording:

> consistent across the evaluated four MCIO held-out domains.

Avoid:

> proven to generalize to unseen domains in general.

This is mostly a manuscript-language issue, not an experimental redesign.

---

# C. THINGS THAT ARE ALREADY GOOD — DO NOT CHANGE THEM

The following parts are now strong enough and should stop being redesigned.

## Strict one-frame transaction definition

One deterministic middle frame/video before detection is a clean primary single-image unit.

The 25%/75% frames are sensitivity only.

Keep this.

---

## Detector-failure accounting

Risk metrics use detector-success samples.

End-to-end K=1 metrics keep all transactions.

This is correct.

---

## Fixed-error RQ1 comparison

Domain-OOF and sample-OOF risk estimators score the **same final classifier errors**.

This is the key design strength.

Keep it.

---

## Same-family RQ2 control

DINOv2-Reg + plain DINOv2 is sufficient as the primary same-family comparator.

Do not add many more ensemble families before evidence exists.

---

## Disagreement remains secondary

Keep:

\[
\Delta_{dis}
\]

as attribution only.

Do not put "disagreement" in the title before results.

---

## SiW-M remains optional

Do not make attack-shift experiments block the first paper.

---

## Routing remains optional

Do not implement routing before RQ1 and basic selective utility are understood.

---

## Track A is closed

Document 52 correctly closes it.

Do not continue optimizing SSDG compatibility unless real implementation exposes a concrete incompatibility.

---

# D. FINAL RECOMMENDED Q3 PAPER CONTRACT

After the above synchronization, the first paper should be reducible to this.

## Problem

Single-image face PAD fails unpredictably under capture-domain shift.

## Method

Use leave-one-source-domain-out prediction failures to train a separate source-only failure-risk score.

## Main comparison

\[
\boxed{
domain\text{-}OOF
\quad vs \quad
matched\ sample\text{-}OOF
}
\]

on identical final classifier errors.

## Primary endpoint

\[
\boxed{
\Delta_{OOF}^{AP}
=
AP_{domain}
-
AP_{sample}
}
\]

## Operational validation

Does the ranking improvement produce a better source-selected:

\[
FA_{end2end}
\leftrightarrow
BFNR_{end2end}
\]

trade-off?

## Secondary system question

Does:

\[
DINOv2\text{-Reg}+OpenCLIP
\]

give better complete-system outcomes than:

\[
DINOv2\text{-Reg}+DINOv2?
\]

## Literature context

Only enough to show the classifier is not obviously weak.

No novelty claim lives there.

---

# E. FINAL ONE-PASS ACTION LIST

I recommend making exactly one synchronization commit that does all of the following:

1. Rewrite RQ1 as **error-ranking primary**, selective utility secondary.
2. Rewrite RQ2 as **complete-system heterogeneous-vs-same-family comparison**.
3. Remove the quasi-third RQ from `docs/02`; keep \(\Delta_{CF}\)/\(\Delta_{dis}\) as attribution.
4. Demote Track A from the main-table structure to compact literature context/appendix.
5. Define the source-only minimum base-classifier competence rule.
6. State that RQ1 tests the **complete domain-OOF construction**, not a causal effect of domain identity.
7. Freeze a minimum primary error-event applicability rule.
8. Use "failure-risk score" as the default term; reserve probability wording for validated calibration.
9. Promote `R_DVd` with/without \(q\) to a visible attribution result.
10. Make domain-ID audit diagnostic only.
11. Remove nonessential complementarity controls from the required first-paper experiment set.
12. Clarify that four-target macro inference is limited to the evaluated MCIO domains.

After those 12 items, I would stop plan review.

---

# Final verdict

\[
\boxed{
\text{DOCUMENT 52 CLOSES TRACK A, BUT ONE FINAL CORE-DOCUMENT SYNCHRONIZATION IS NEEDED}
}
\]

The remaining changes are **not new research design**.

They are mostly about making all normative documents tell the same simple story.

The strongest final Q3 story is:

\[
\boxed{
\text{strict single-image failure-risk transfer under domain shift}
}
\]

with literature compatibility only as supporting context.

Once the 12-item synchronization pass is complete, I recommend freezing the plan and moving to implementation without another broad protocol-review cycle.
