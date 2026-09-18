# ChatGPT Review — Document 46: Response to Document 45

Date: 2026-09-18
Repository: `lathevinh/fas`
Reviewed file: `docs/46-review-response-doc45.md`

## Overall verdict

Document 46 is a strong response.

It correctly keeps the Q3 paper centered on Track B and limits Track A to literature context. The main research plan, RQ1/RQ2, and novelty boundary do **not** need to be reopened.

Most of the issues raised in Document 45 are now resolved.

The remaining concerns are narrower and mostly concern whether Track A is internally executable and whether its literature comparison is phrased conservatively enough.

The two most important remaining issues are:

1. Track A currently says it has no `branch_calibration` role, yet the proposed heterogeneous classifier elsewhere depends on affine branch calibration and a source-selected threshold;
2. published SSDG AUC is still affected by target-aware checkpoint selection, even though AUC itself is threshold-free.

---

# 1. Main remaining inconsistency: Track A has no calibration role, but the heterogeneous classifier needs calibration

Document 46 says:

> Track A records pinned protocol membership and a deterministic source-only fit/checkpoint split. It has no branch-calibration, gate-domain, routing, or risk-training roles.

This is clean if Track A evaluates only a single raw classifier.

However, the proposed heterogeneous classifier is defined elsewhere as:

\[
p_F
=
\frac{\widehat p_D+\widehat p_V}{2}
\]

where:

\[
\widehat p_D
=
Cal_D(p_D),
\qquad
\widehat p_V
=
Cal_V(p_V).
\]

The main classifier table also intends to show:

- DINOv2-Reg;
- OpenCLIP;
- calibrated heterogeneous average.

Therefore Track A still needs a source-only way to fit:

\[
Cal_D,
\qquad
Cal_V
\]

and, if HTER is reported using the proposed classifier, a source-only way to choose:

\[
\tau_{ref}.
\]

## Recommendation

Do not create the full Track-B role structure.

Instead define a lightweight Track-A source split:

```text
track_a_fit
track_a_validation
```

where `track_a_validation` is allowed to:

- select DINO checkpoint;
- fit affine branch calibrators;
- select the source operating threshold.

Then state explicitly:

> Track A uses one source-only development partition for checkpoint selection, branch calibration, and threshold selection. It does not train any failure-risk model or selective gate.

This is simple and consistent.

If the paper decides that Track A should show only raw DINO/OpenCLIP classifier outputs without calibrated fusion, then remove calibrated fusion from Track-A expectations instead.

The current wording leaves the execution recipe incomplete.

---

# 2. Published SSDG AUC is not cleanly target-blind either

Document 46 correctly states that:

- published SSDG HTER uses a target-derived threshold;
- SSDG checkpoint selection uses `tgt_valid_dataloader`;
- therefore published SSDG HTER is not a like-for-like target-blind comparison.

It then says:

> AUC provides the less threshold-dependent comparison.

This is true in a narrow sense:

\[
AUC
\]

does not require choosing an operating threshold.

However, the **model checkpoint itself** was selected using target HTER.

Therefore published SSDG AUC is still measured on a model whose selection was informed by the target distribution.

## Recommendation

Use wording such as:

> Published SSDG AUC is threshold-free at evaluation time, but the reported checkpoint is still target-aware because model selection used the held-out target loader.

Therefore:

- published SSDG AUC may be shown for historical context;
- it should not be presented as a strict target-blind baseline;
- in-house Track-A results are the clean source-only comparison.

This distinction is worth making explicit in the table footnote.

---

# 3. Track A is now correctly scoped as context, not novelty

This is one of the strongest improvements.

Document 46 explicitly states:

> Track A creates no third research question and no protocol novelty claim.

That should remain unchanged.

The manuscript logic is now clean:

### Track A

Classifier/literature context.

### Track B

Scientific evaluation of:

\[
\text{Domain-OOF Failure Risk Estimation}.
\]

Do not allow reviewer pressure during writing to turn Track A into a second methodological contribution.

---

# 4. Track-A detector failures need an explicit rule

Track A reuses the Track-B detector/context crop rather than SSDG's MTCNN/256 preprocessing.

This is correctly labeled only as:

> sample-universe/frame-rule compatible.

However, this introduces a practical issue.

The pinned SSDG sample universe assumes preprocessing produces a face sample.

Your detector may fail on some pinned Track-A frames.

Then what happens?

Possible choices are:

1. drop the sample;
2. replace the frame;
3. assign a fixed non-accept score;
4. report detector failure separately.

Dropping failed samples would silently change the pinned sample universe.

Replacing frames would violate frame-rule compatibility.

## Recommendation

For Track A:

- never replace the pinned frame;
- never silently drop a detector failure;
- record detector-failure rate;
- for literature classifier metrics that require a score, clearly define whether failed detections are excluded from the classifier-only table or mapped to a fixed operational outcome.

The cleanest presentation may be:

### Track-A classifier comparability

Evaluate only detector-success samples, and report detector coverage separately.

### Track-B end-to-end evaluation

Detector failures remain terminal non-accept in the full transaction denominator.

This prevents Track-A preprocessing mismatch from contaminating RQ1.

---

# 5. Track-A HTER and TPR@FPR=1% need a fully source-only threshold rule

The updated Document 42 says Track A will report:

- AUC;
- source-threshold HTER;
- TPR at FPR=1% when estimable.

That is good.

But the threshold-selection rule still needs to be connected to the lightweight Track-A validation split discussed above.

For example:

\[
\tau^{A}_{HTER}
\]

could be chosen at source EER or by a predefined source criterion.

For:

\[
TPR@FPR=1\%,
\]

the threshold must also be selected only from source validation.

Do not use the target ROC to find the 1% FPR point and then report TPR as if it were deployable.

## Recommendation

Distinguish:

### Source-selected operating metric

Use a threshold derived from Track-A source validation and transfer it to target.

### Post-hoc target ROC diagnostic

May report conventional target ROC/AUC, but label it diagnostic/non-deployable.

This is consistent with the rest of the dossier.

---

# 6. The exact video aggregation claim should be retained with provenance

Document 46 says the pinned SSDG evaluation averages:

\[
\text{class-1 softmax probability}
\]

over the two selected frames.

Assuming this was verified directly from the pinned evaluation code, this is exactly the kind of code-derived contract that should remain in Track A.

The implementation should store:

- repository;
- commit SHA;
- source file path;
- function name or code-line hash.

This prevents future ambiguity if the upstream repository changes.

No methodological change is needed.

---

# 7. "One immutable manifest per dataset per active track" is now the correct rule

This correction resolves the major inconsistency from Document 45.

Track A and Track B have different purposes and sample universes.

Therefore:

\[
\boxed{
\text{one immutable manifest per dataset per track}
}
\]

is the right abstraction.

Track A should stay lightweight.

Track B should retain:

- `source_train`;
- `branch_calibration`;
- `gate_domain`;
- optional routing-validation role.

No further change recommended.

---

# 8. Track A should not inherit Track-B risk infrastructure

Document 46 correctly removes:

- risk training;
- gate selection;
- routing;

from Track A.

Keep it that way.

Track A should never gain:

- domain-OOF risk models;
- abstention gates;
- selective-risk tables.

Otherwise the paper will duplicate the entire study under two incompatible sample universes.

Track B alone should host RQ1/RQ2.

---

# 9. The two-engineer-day Track-A stop rule is reasonable

This is not a scientific rule; it is project management.

That is fine.

The important scientific consequence is already correct:

> failure to exactly reconcile old benchmark artifacts does not invalidate Track B.

That protects the Q3 project from getting trapped reproducing an old preprocessing stack.

No change recommended.

---

# 10. MCIO terminology is now much cleaner

Using:

\[
MCIO
\]

consistently for:

- MSU;
- CASIA;
- Idiap Replay-Attack;
- OULU;

is preferable to alternating between MCIO/MICO.

Legacy internal paths named `mico` do not matter scientifically if documented.

No further change is necessary.

---

# 11. One wording issue remains: "sample/evaluation equivalence"

Document 42 says exact sample/evaluation equivalence is claimed after:

- lists;
- labels;
- frame selection;
- aggregation;

are reconciled.

Because preprocessing remains different from SSDG, the phrase:

> exact sample/evaluation equivalence

can still sound stronger than intended.

## Recommendation

Use:

> exact **sample-membership/frame-selection/video-aggregation equivalence**

instead.

That precisely names what is matched.

Then separately state:

> image preprocessing and model-selection rules differ intentionally.

This avoids ambiguity.

---

# 12. Track A and Track B should use separate table captions and no direct number mixing

The response already says the tracks do not share a headline number.

Good.

Make this visually obvious in the paper.

Recommended Table 1:

### Panel A — Literature context

Published methods + in-house Track-A models.

### Panel B — Strict single-image proposed protocol

DINO / OpenCLIP / heterogeneous average / same-family control.

Do not compute a single macro ranking across Panels A and B.

Do not bold "best" across incompatible protocols.

---

# 13. AP_FA remains correctly secondary

Document 46 keeps:

\[
AP_{error}
\]

as the main RQ1 endpoint and:

\[
AP_{FA}
\]

as security-specific support.

This is the correct hierarchy.

Do not promote AP_FA later merely because it yields a stronger result.

---

# 14. Quality-feature attribution remains essential

The required comparison:

\[
R_{DVd}
\]

with versus without:

\[
q
\]

should remain.

If domain-OOF gains depend heavily on image-quality variables, that is not necessarily a failure.

It means the mechanism is closer to:

> source-domain pseudo-shifts teach the risk model transferable nuisance/failure signatures.

That is still publishable.

But the paper must not then attribute the gain primarily to heterogeneous branch disagreement.

Document 46 handles this correctly.

---

# 15. One remaining risk: Track-A fit/checkpoint split may reduce source data unfairly

If Track A creates a source-only development split for checkpoint/calibration/threshold selection, your in-house model trains on less data than old methods that may use all source samples plus target validation.

That is scientifically cleaner but can lower classifier performance.

## Recommendation

Accept this tradeoff.

Do not reclaim the held-out source validation samples after selecting the checkpoint unless the entire refit/recalibration procedure is specified in advance.

In the table caption, emphasize:

> our Track-A pipeline is strictly source-selected.

The goal is context, not necessarily beating every target-aware published number.

---

# 16. Do not make Track-A competitiveness a prerequisite for RQ1

This is important.

Suppose Track A classifier performance is mediocre relative to recent literature, but Track B shows:

\[
domain\text{-}OOF risk
>
sample\text{-}OOF risk
\]

strongly and consistently.

The scientific RQ1 may still be valid.

Of course, the base classifier must be competent enough that the study is meaningful.

But "not state of the art in Track A" should not automatically kill the failure-risk contribution.

Use a minimum competence criterion, not an SOTA criterion.

---

# 17. The updated core plan is now sufficiently stable

At this point, I do not see a reason to continue modifying:

- backbone choice;
- VLM choice;
- fusion rule;
- RQ1;
- RQ2;
- Track-B selective design.

The remaining Track-A details are benchmarking hygiene.

That means the research plan itself is effectively frozen.

---

# Required final corrections

Before calling Track A fully executable, I recommend only these corrections:

1. Add a lightweight Track-A `fit/validation` split because checkpoint selection, affine calibration, and source-threshold selection need source-only development data.
2. State that published SSDG AUC is still target-aware through checkpoint selection.
3. Define how detector failures are handled in Track-A classifier metrics.
4. Define source-only threshold rules for Track-A HTER and TPR@FPR=1%.
5. Replace "exact sample/evaluation equivalence" with the narrower:
   > sample-membership/frame-selection/video-aggregation equivalence.

---

# Final verdict

\[
\boxed{
\text{DOCUMENT 46 IS SOUND; ONLY TRACK-A EXECUTION DETAILS REMAIN}
}
\]

The Q3 research plan should remain frozen.

No new research question, architecture, or novelty mechanism is needed.

The most important remaining technical correction is the Track-A validation/calibration issue:

\[
\text{calibrated heterogeneous classifier}
\Rightarrow
\text{source-only calibration data must exist}.
\]

Once that is made explicit, the Track-A contract is internally complete enough to implement.
