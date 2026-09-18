# ChatGPT Review — Document 58: Population and Coverage Clarification

Date: 2026-09-18  
Repository: `lathevinh/fas`  
Reviewed file: `docs/58-review-response-doc57.md`

## Verdict

**Document 58 is accepted.**

The two final clarification items from Document 57 are now explicitly synchronized into the normative research and implementation documents.

I do not identify any remaining scientific-design issue that justifies another broad research-plan review.

The Q3 plan should now be treated as frozen.

---

# 1. RQ2 AURC population is now correctly defined

The response explicitly freezes the common detector-success mask:

\[
M_c
=
\{i:y_i=c \land detector\_success_i=1\}.
\]

Both the heterogeneous and same-family systems compute class-conditional AURC on exactly this same population.

This is correct because failure-risk scores do not exist after detector failure.

The design now cleanly separates:

## Risk/selective-ranking population

\[
detector\_success=1
\]

used for:

- risk ordering;
- class-conditional AURC;
- RQ2 primary scalar.

## End-to-end population

all original transactions, including detector failures, used for:

- `FA_end2end`;
- `BFNR_end2end`;
- coverage;
- K=1 system accounting.

This is the correct separation.

The additional invariant that the detector-success mask must be bit-identical across RQ2 systems is particularly strong and should remain.

---

# 2. Coverage semantics are now unambiguous

Coverage is explicitly:

- mandatory to report;
- explanatory/supporting;
- not an extra H2 pass/fail threshold.

This is a good choice.

RQ2 already has:

- class-balanced raw AURC as the primary scalar;
- FA guardrails;
- BFNR guardrails;
- target-harm tolerance.

Adding a separate coverage non-inferiority threshold would over-constrain the claim and introduce another arbitrary criterion.

The current interpretation is clean:

> coverage explains how the selective system obtained its operating outcome, but cannot independently pass, rescue, or invalidate H2.

Keep this.

---

# 3. RQ2 is now fully deterministic

The RQ2 scientific comparison now has:

\[
U_j
=
\frac12
(AURC_{attack,j}+AURC_{bona,j})
\]

and:

\[
\Delta_{RQ2}
=
U_{same}-U_{hetero}.
\]

Positive values favor the heterogeneous system.

The pass rule is frozen before target inspection and includes:

1. minimum meaningful macro gain;
2. paired uncertainty;
3. target consistency;
4. seed consistency;
5. per-target selective-harm tolerance;
6. end-to-end FA/BFNR guardrails.

There is no longer room to select a favorable metric after seeing results.

No further methodological change is recommended.

---

# 4. RQ1 remains cleanly separated from RQ2

RQ1 remains:

\[
\Delta_{OOF}
=
AP(e,r^{domain})
-
AP(e,r^{sample})
\]

on identical final classifier errors.

RQ2 compares complete systems whose classifiers and error sets differ.

The documents correctly avoid treating raw cross-system risk AP as the RQ2 scientific contrast.

This distinction is now stable and should not be revisited.

---

# 5. Detector failures are handled consistently across the full project

The final logic is now coherent:

- no artificial classifier score after detector failure;
- no fabricated failure-risk score;
- detector failure is terminal non-accept under K=1;
- detector failures remain in original denominators for end-to-end metrics;
- detector failures reduce reported coverage;
- ranking metrics operate only where scores actually exist.

This is a strong design choice.

---

# 6. No additional coverage guardrail should be added later

This deserves an explicit warning for implementation and manuscript writing.

After target results are available, do **not** introduce rules such as:

\[
coverage_{hetero}
\ge
coverage_{same}-\epsilon
\]

because one system happens to look unfavorable or favorable.

The frozen rule already states that coverage is explanatory only.

Any future deployment-specific minimum-coverage constraint would require a separate source-only predefined analysis, not a retrospective amendment to RQ2.

---

# 7. Track A should remain closed

Nothing in Document 58 changes the earlier conclusion.

Track A remains only:

> literature context showing that the base classifier is not obviously weak.

It should not return to the main scientific narrative.

No more SSDG/FLIP protocol refinement is warranted unless the implementation encounters an actual incompatible artifact.

---

# 8. Final frozen Q3 story

The complete paper story is now concise.

## Primary problem

Failure prediction for strict single-image face PAD under unseen capture-domain shift.

## Primary method

Source-domain cross-fitted failure-risk estimation.

## RQ1

\[
domain\text{-}OOF
\quad vs \quad
matched\ sample\text{-}OOF
\]

on identical classifier errors.

## Primary RQ1 metric

Prediction-error average precision.

## Operational validation

K=1 selective security/usability using source-selected gates.

## RQ2

DINOv2-Reg + OpenCLIP complete selective system versus matched DINOv2-Reg + plain-DINOv2 system.

## Literature context

Secondary only.

This is sufficiently focused for the intended Q3-first submission.

---

# Final disposition

\[
\boxed{
\text{DOCUMENT 58 ACCEPTED — RESEARCH PLAN FROZEN}
}
\]

I recommend ending the broad protocol-review loop here.

The next review should inspect only concrete Phase-0/implementation artifacts such as:

- configs;
- schemas;
- manifest contracts;
- synthetic metric tests;
- split-generation code;
- lineage assertions.

A new broad methodological review should occur only if implementation exposes a real contradiction with the frozen plan.
