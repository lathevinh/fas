# ChatGPT Review — Document 44: Response to Document 43

Date: 2026-09-18  
Repository: `lathevinh/fas`  
Reviewed file: `docs/44-review-response-doc43.md`

## Overall verdict

Document 44 responds well to the previous review. Most of the important ambiguities in Document 42 are now corrected in the right direction, and the updated Document 42 reflects those changes.

I do **not** recommend reopening the architecture, research questions, or Q3 novelty story.

However, Document 44 introduces one new layer — the Track-A literature-compatible benchmark — and that layer now needs tighter wording and scope control.

The strongest remaining issues are:

1. Track A is **sample-universe/protocol compatible**, not an exact reproduction of published SSDG results;
2. the "one immutable source-role manifest per dataset" rule now needs clarification because Track A and Track B have different sample universes;
3. the Track-A frame/evaluation rule should be frozen from code, not summarized loosely;
4. source-optimized thresholding is acceptable, but its inferential role should remain clearly limited;
5. the updated documents still need one final terminology cleanup around MICO/MCIO and "confirmatory".

---

# 1. Document 44 correctly fixes the major problems from Document 43

The following responses are sound and should be retained:

- global source roles no longer depend on outer target;
- target-label secrecy is replaced by fold-local exclusion;
- Track A and Track B are separated;
- `branch_calibration` is explicitly reused for source-optimized threshold selection;
- the K=1 gate is written as a predicted-live filter;
- macro bootstrap is performed target-by-target before equal-weight aggregation;
- quality normalization is fold-local for OOF;
- DINO sampling no longer double-balances class/attack-family exposure;
- uncertainty heuristics are separated from learned risk estimators;
- all analysis-rule logic freezes before the first outer-target result.

These are genuine improvements rather than cosmetic wording changes.

---

# 2. Important: Track A is not an "SSDG reproduction"

Document 44 pins:

- SSDG official repository commit:
  `c268920a7408ca78fb425954de2bf5745d1c660a`;
- FLIP official repository commit:
  `4f95def259e135a0cbaff1d770f559ca739c4c9f`.

Both commits exist.

The SSDG code confirms that its `sample_frames` implementation selects frames starting from offset 6 and uses a deterministic interval rule.

However, the SSDG training scripts also evaluate on:

```text
tgt_valid_dataloader
```

during training and choose the best model according to target HTER.

Therefore the published SSDG pipeline is not target-blind in the same sense as the proposed strict source-only pipeline.

## Consequence

The proposed Track A can reproduce:

- sample universe;
- frame sampling convention;
- broad preprocessing/evaluation convention;

but it intentionally **does not reproduce SSDG model selection**.

Therefore the paper should never imply:

> exact SSDG protocol reproduction.

Recommended wording:

> **SSDG-compatible sample universe and evaluation view with source-only model selection**

or:

> **literature-compatible MCIO data/evaluation track**

rather than:

> SSDG reproduction.

If published SSDG numbers are shown in the same table, add a footnote such as:

> Published SSDG results use their original target-aware validation procedure; our Track-A model selection remains strictly source-only.

This distinction is scientifically important.

---

# 3. New inconsistency: one immutable source-role manifest vs two different tracks

Document 44 correctly changes source roles to:

> one immutable source-role manifest per dataset.

That is clean for Track B.

But Track A and Track B now have different sample universes.

Track A uses the SSDG/FLIP-style benchmark universe.

Track B uses the strict single-image canonical source-role universe.

Therefore "one source-role manifest per dataset" becomes ambiguous.

## Example

For OULU:

Track A may use:

\[
Train + Test,\quad exclude\ Dev
\]

as the literature-compatible universe.

Track B may use a different source-eligible official subset depending on the strict role policy.

A single role manifest cannot simultaneously describe both universes unless they are exactly identical.

## Recommendation

Make the rule:

\[
\boxed{
\text{one immutable source-role manifest per dataset per experimental track}
}
\]

Specifically:

### Track A

No custom train/calibration/gate role partition is required unless your Track-A classifier training needs it.

Use the pinned benchmark list universe directly and define only the source-only validation/checkpoint rule required by your model.

### Track B

Use the full immutable role structure:

- `source_train`;
- `branch_calibration`;
- `gate_domain`;
- optional `routing_validation`.

This avoids contaminating Track B's risk experiment with Track-A compatibility constraints.

---

# 4. Track A should remain classifier comparability only

Document 44 says Track A does not host RQ1.

That is exactly right.

Keep this boundary strict.

Track A answers:

> Is the chosen DINO/OpenCLIP instantiation broadly competitive under a recognizable MCIO literature view?

Track B answers:

> Does domain-OOF failure-risk supervision improve target-blind selective FAS?

Do not train Track-B risk estimators using Track-A frame rules.

Do not use Track-A published-number comparisons as evidence for RQ1.

Do not merge Track-A and Track-B four-domain macros.

They are separate estimands.

---

# 5. The Track-A preprocessing claim still needs careful wording

The updated Document 42 says Track A uses:

> the MTCNN-style alignment contract.

The original SSDG README explicitly uses MTCNN face detection/alignment and 256×256 RGB faces.

Your primary system elsewhere uses a frozen detector/context-crop design.

If Track A truly uses SSDG-style MTCNN preprocessing, then you now have two preprocessing pipelines:

- Track A: literature compatibility;
- Track B: strict proposed deployment pipeline.

That is acceptable.

But it should be stated explicitly.

If instead Track A keeps your SCRFD/RetinaFace-style context crop while only copying SSDG lists/frame indices, then it is **not preprocessing-compatible** with SSDG.

## Recommendation

Choose one of two labels:

### If Track A reproduces MTCNN/256 alignment

Call it:

> protocol + preprocessing compatible.

### If Track A keeps your own detector/crop

Call it:

> sample-universe/frame-rule compatible.

Do not use the stronger wording unless the preprocessing is actually replicated.

---

# 6. The exact SSDG frame rule should be recorded as code-derived, not paraphrased

Document 44 summarizes:

- source frame 6;
- target frame 6 plus \(6+\lfloor N/2\rfloor\).

The code's actual rule is:

\[
frame\_interval=
\left\lfloor
\frac{N}{num\_frames}
\right\rfloor
\]

and selected indices are:

\[
6+j\cdot frame\_interval.
\]

For:

\[
num\_frames=1,
\]

this gives the first selected frame at offset 6.

For:

\[
num\_frames=2,
\]

it gives:

\[
6,\quad
6+\left\lfloor\frac N2\right\rfloor.
\]

The summary is therefore correct **only because the relevant SSDG configs use one source frame and two target frames**.

## Recommendation

Document the actual function plus the config values rather than freezing only the simplified formula.

This protects against mistakes if a config differs across folds.

For example:

```text
SSDG sample_frames():
index_j = frame_list[6 + j * floor(N / num_frames)]

source num_frames = 1
target num_frames = 2
```

That is a stronger reproducibility record.

---

# 7. Verify the target video-score aggregation before claiming equivalence

Document 42 now says Track A uses:

> target video-score aggregation.

But the current response does not explicitly document how SSDG combines the two selected target frames into one video-level prediction.

This needs to be derived from the pinned evaluation code or literature implementation.

Possible choices include:

- mean probability;
- mean logit;
- majority decision;
- frame-level metrics with shared video IDs.

These are not equivalent.

## Recommendation

Before declaring Track A frozen, add:

```text
target_frame_to_video_aggregation:
    rule: ...
    source: <repo path + commit>
```

This is a Phase-1 verification item.

Do not infer the aggregation rule from the number of target frames alone.

---

# 8. The FLIP "16 list files" cross-check is useful but should not become a second authority

Document 44 uses SSDG as the main sample-universe reference and FLIP as a derivative cross-check.

That hierarchy is sensible.

Keep it explicit:

\[
SSDG\ primary\ reference
\]

\[
FLIP\ cross\text{-}check
\]

Do not attempt to reconcile disagreements by silently choosing whichever list gives more favorable results.

If SSDG and FLIP membership differ:

1. record the discrepancy;
2. identify why;
3. freeze one declared Track-A authority before results.

The paper should then name the adopted convention.

---

# 9. FLIP published Benchmark-1 extra-data distinction is handled correctly

Document 44 correctly notes that FLIP's published Benchmark-1 configuration includes CelebA-Spoof and therefore should not be treated as an equal-data strict-MICO baseline.

This is an important and correct qualification.

Keep two categories in the classifier comparison:

### Equal-data / strict source

Methods using only the three MCIO/MICO source datasets.

### Extra-data

Methods using additional labeled PAD data such as CelebA-Spoof.

Do not rank them in one undifferentiated leaderboard.

---

# 10. Option C threshold reuse is acceptable for this Q3 paper

Document 44 chooses:

> fit branch calibration and select \(\tau_{ref}\) on the same `branch_calibration` partition.

This is not ideal statistical separation, but it is a reasonable compromise because MSU-MFSD is small.

The wording is appropriately conservative:

- source-optimized;
- not independently validated;
- not certified.

I agree with this choice for the first paper.

## One remaining recommendation

Do not use a confidence interval computed on that same partition to claim:

> validated source APCER guarantee.

The threshold itself is optimized there.

Confidence intervals on that partition are descriptive.

The real test is performance after transfer to the outer target.

---

# 11. K=1 gate semantics are now correctly specified

The response fixes the main ambiguity:

- predicted spoof is already non-accept;
- only predicted-live transactions are filtered by the risk gate.

This is the right deployment interpretation.

The risk estimator can still be trained/evaluated on all classifier errors for RQ1.

But the operational security curve should be computed only through the rule:

\[
g(x)=live
\land
r(x)\le u
\Rightarrow accept.
\]

No further change is needed.

---

# 12. Security-specific AP should be clearly labeled secondary/supporting

Document 44 adds false-accept ranking when event counts permit.

Good.

Do not make this another co-primary endpoint.

Keep:

\[
AP_{error}
\]

as the RQ1 primary methodological endpoint.

Use:

\[
AP_{FA}
\]

as security-specific supporting evidence.

This prevents endpoint proliferation and preserves the clean paper story.

---

# 13. Fold-local normalization is correct, but domain identity remains an expected signal

The response chooses fold-local normalization of quality features.

That is the leakage-safe choice.

However, because:

\[
q(x)
\]

contains domain-sensitive quantities such as:

- luminance;
- blur;
- detector confidence;
- face area;

the risk model may legitimately learn domain-shift signatures.

That is not automatically a shortcut.

The important attribution experiment is still:

\[
R_{DVd}
\]

with versus without:

\[
q.
\]

If most of the domain-OOF gain disappears without \(q\), the paper should say that failure transfer relies substantially on source-observed quality/domain nuisance signals.

That would still be a valid empirical result, but it changes the interpretation.

---

# 14. The double-balancing correction is good

The updated DINO plan now uses:

- approximately uniform dataset exposure;
- video/frame sampling;

while class/domain balancing is handled in the loss.

This is cleaner than balancing both sampler and loss.

Keep this version.

---

# 15. Macro bootstrap needs one more seed-level clarification

Document 44 correctly says:

- resample within targets;
- compute target effect;
- equal-weight four-target macro;
- do not pool datasets or seeds as independent samples.

Good.

One detail should remain explicit:

For each seed:

\[
\Delta_{macro}^{(s)}
=
\frac14\sum_t\Delta_t^{(s)}.
\]

Bootstrap uncertainty should primarily reflect subject/video sampling within that seed.

Then seed-to-seed variation is reported separately.

Do not combine the three seeds inside one bootstrap resample as if they were three independent observations of the same subjects.

The current plan mostly says this already; retain it in implementation.

---

# 16. Terminology: MCIO vs MICO should be standardized

The literature often uses:

\[
M,C,I,O
\]

or permutations when naming the four datasets:

- MSU;
- CASIA;
- Idiap;
- OULU.

The repo currently uses both "MICO" and "MCIO".

This is minor but easy for reviewers to notice.

## Recommendation

Pick one convention in your manuscript.

For example:

> MCIO benchmark (MSU, CASIA, Idiap Replay-Attack, OULU)

and use explicit fold notation:

\[
CIO\rightarrow M,
\quad
MOI\rightarrow C,
\quad
MCO\rightarrow I,
\quad
MCI\rightarrow O.
\]

Or keep "MICO" as internal naming but explain once that it denotes the same four-dataset leave-one-domain-out benchmark.

Avoid switching acronyms casually.

---

# 17. "Confirmatory" wording is still stronger than necessary

The updated documents sometimes call all four outer folds confirmatory.

Because this is a fully prespecified evaluation, that is not wrong.

But the more conventional terminology for the paper is simply:

> four leave-one-domain-out held-out target folds.

That avoids unnecessary preregistration-style language that reviewers may find unusual in a standard FAS paper.

Use "preregistered/frozen" to describe internal governance if desired.

Use ordinary cross-domain benchmark language in the manuscript.

---

# 18. Document 44 should explicitly say no new research claim was created by Track A

Track A is a comparability mechanism.

It is not a third research question.

It should not become:

> We propose two protocols.

The paper still has two core RQs:

1. domain-OOF failure-risk transfer;
2. heterogeneous pair versus same-family control.

Track A only answers:

> Is the classifier instantiation reasonably comparable to established MCIO literature?

This distinction should be stated explicitly in the response.

---

# 19. One publication risk: Track A can consume disproportionate implementation time

Reproducing:

- old MTCNN preprocessing;
- old SSDG lists;
- old frame conventions;
- video aggregation;
- extra classifier evaluation;

can become a substantial engineering project.

For a Q3-first paper, the priority remains Track B.

## Recommendation

Define a stop rule:

If exact Track-A reproduction becomes blocked by:

- missing list artifacts;
- dataset release mismatch;
- preprocessing incompatibility;

then publish a clearly labeled literature-context table from reported papers and keep your own benchmark-compatible result only where equivalence is verifiable.

Do not delay the RQ1 experiment for weeks just to perfectly emulate a 2020 preprocessing stack.

---

# 20. Final assessment of Document 44

Document 44 successfully fixes the important protocol ambiguities from Document 43.

The core research method remains coherent.

The only substantial new issue is that the newly introduced Track A must be prevented from becoming overclaimed.

## Required final corrections

1. Clarify source-role manifests are Track-B objects, or define one immutable manifest per dataset **per track**.
2. Rename Track A as sample-universe/evaluation compatible unless preprocessing is exactly replicated.
3. Freeze the actual SSDG `sample_frames` function and config values, not only the simplified frame formula.
4. Verify and freeze target frame-to-video aggregation.
5. Explicitly footnote that original SSDG training uses target validation for best-model selection, while your Track A remains source-only.
6. Standardize MCIO/MICO terminology.

## Strong recommendations

7. Keep Track A out of RQ1/RQ2 novelty claims.
8. Keep `AP_FA` secondary, not co-primary.
9. Preserve with/without-quality-feature attribution.
10. Add a Track-A implementation stop rule so comparability work cannot derail the core Q3 study.

---

# Final verdict

\[
\boxed{
\text{DOCUMENT 44 IS SOUND AND THE CORE PLAN CAN REMAIN FROZEN}
}
\]

No research-plan redesign is needed.

The next changes should be limited to tightening the Track-A benchmarking contract and terminology.

The most important sentence to add is:

> Track A reproduces a pinned literature sample/evaluation convention for classifier comparability, while all scientific claims on source-domain failure-risk transfer are evaluated exclusively under Track B.

That keeps the Q3 story clean.
