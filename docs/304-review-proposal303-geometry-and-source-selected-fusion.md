# 304 - Review of proposal303: geometry and source-selected fusion

Date: 2026-10-27
Reviewed commit: `dca6692075ebd4116d1217f40833c7c9ef481a13`
Prior experiment: [301](301-locked-target-package-and-fixed-evaluation.md), accepted within [302](302-review-doc301-locked-target-results-and-final-claims.md).

## Decision

**Accept303 as a reasonable exploratory research direction, but require a revised concrete protocol before treating it as an executable or confirmatory study. The current proposal changes multiple factors, omits a necessary strong comparator and leaves geometry, optimization objective and acceptance rules underspecified. It provides no execution authority.**

Do not reopen301: RQ1 stays inconclusive and RQ2 stays evidence against the registered heterogeneous-superiority claim. Preserve its sources, models, target results and additive-verifier disclosure.303 is not evidence that an improved pipeline works or that distorted crops caused the negative result.

## What is sound

The proposal correctly separates a new hypothesis from the completed experiment, recognizes that all four target outcomes have been observed, retains frozen backbones for a bounded initial study and distinguishes ranking from operating-point utility. Source-only nested selection, retained failures, fixed prompts, paired group uncertainty and explicit negative-result reporting are appropriate. A new independent target or prospective cohort would strengthen later confirmation; the current four datasets cannot become untouched again.

The reported301 figures are consistent with the accepted result: weak standalone OpenCLIP, macro heterogeneous raw-AURC difference-0.032897 and RQ1 AP difference-0.019232. Neither proves that OpenCLIP features are intrinsically useless: the experiment tested a particular zero-shot prompt branch, calibration and equal fusion. Likewise, no target result tests the proposed geometry interventions yet. Journal quartile speculation contributes no evidence to the design and should be omitted from the scientific rationale.

## 1. Separate geometry from model selection

The proposed main question combines geometry-preserving input and source-selected fusion. Comparing old stretched50/50 fusion with new geometry plus new fusion weight cannot identify which change helped or harmed. State separate estimands: geometry effect under a fixed classifier; fusion effect under fixed geometry; and, only if budgeted in advance, their interaction.

A small staged protocol is sufficient. First compare G0, the exact current geometry, with one candidate geometry using the same frozen DINO-Reg/head/calibration/splits. Then evaluate a predetermined compact model comparison under both geometries if the broader study is pursued. Do not select a favorable geometry, model, risk vector and operating point jointly using a single validation table and report the resulting gain as an isolated geometry effect. Any screening/stop decision must be declared before new model results and remain source-development-only.

## 2. Prefer the minimal geometry intervention first; G1 is not equivalence

Public code confirms shared_context_crop uses the five-point fitted rotation normalized to unit scale, rotates around the original eye midpoint, expands the rotated box by1.30, clips to the image and saves a potentially rectangular crop. The current branches resize that rectangle to square. For the proposal's reported744x1013 example, horizontal/vertical scale ratio becomes1013/744=1.36156. That demonstrates anisotropic scaling for that example; its private pixels and dataset-wide frequency were not inspected here. Distortion is a legitimate hypothesis, not a proven universal defect or cause of301's result.

The existing direct alignment_matrix/align_face path instead fits a full isotropic scale/rotation/translation to a five-landmark template and square canvas. Executing its actual matrix function on synthetic landmarks confirms equal singular values but a changed eye location/canvas mapping. It does not simply preserve the current rotation about a fixed eye midpoint or its clipped box context. The same numerical1.30 has different geometric meaning in these paths. G1 can change face scale, centering, visible context, clipping and resampling as well as remove stretching. Its present claim to retain all those semantics is too strong.

For the first controlled comparison, recommend303's G2: pad the **same retained rectangular shared-context crop** to square, then resize isotropically. This is simpler to isolate and may reuse saved context crops without detector/video reruns. Explicitly fix padding RGB value, centering, odd-pixel allocation, interpolation/rounding, empty/degenerate input handling and resolution mapping. Padding still changes occupancy and introduces borders; call it a controlled padding intervention, not perfect context/scale equivalence or guaranteed improvement. It cannot be reconstructed faithfully from already stretched224/518 crops. If native context crops are unavailable, use the retained selected RGB and saved detector geometry under separately authorized execution, not a new frame/detector search.

Keep G1 as a separately specified later alignment ablation if needed. Pin template coordinates, matrix direction/solver, canvas/context definition and border/resampling details. Synthetic transform/landmark tests and a small deterministic **source** usability inspection must precede broad feature regeneration. No target image inspection should be used to pick the transform.

## 3. Restore the strong same-family comparator

Section C lists DINO-Reg alone and plain DINO alone but omits their calibrated equal average, the very comparator that outperformed the heterogeneous system on the registered301 endpoint. Add it. Comparing a tuned heterogeneous weight to individual DINO heads alone risks an unfair conclusion about heterogeneous benefit. Keep the DINO anchor/head recipe, tuning budget, role splits and calibration treatment comparable; do not spend extra search only on the proposed method.

For a minimal confirmatory model panel retain DINO-Reg alone, the fixed two-DINO average, the fixed DINO-Reg/OpenCLIP average and the prespecified source-selected convex fusion. Plain DINO-alone can remain a secondary branch diagnostic. A selected DINO-only endpoint is a valid outcome, but must not be labeled a cross-foundation gain. A scalar model-selection/fusion study is distinct from tuning prompts or training CLIP weights.

The new standalone competence gate must be defined explicitly. The prior study scoped standalone failure to standalone claims;303 can adopt a stricter rule prospectively, but must not pretend it was the old rule or apply it retroactively. In particular, clarify whether an ineligible OpenCLIP branch forces weight zero or merely limits claims. Retain every measured branch result either way.

## 4. Define the actual nested selection and ranking pipeline

"Optimize preregistered primary utility" is a placeholder, not an algorithm. Specify candidate weights/endpoints, primary scalar, source-domain aggregation, group folds, selection budget and deterministic ties. Fit branch heads, calibration and reference thresholds only in their allowed inner data. Evaluate candidate weights on held-out inner groups; do not optimize and evaluate a weight on the same calibration labels or use external/observed-target metrics. Preserve exact-frame connected components with original groups.

Because fusion changes classifier predictions and error labels, the risk task also changes. State which system's errors define each comparison, whether the DINO anchor is shared and how risk models and error supervision are cross-fitted **after accounting for fusion selection**. Cross-fit the selected pipeline, including selection steps; choosing a weight on all source labels and then calling predictions OOF is not sufficient. Pin risk features, quality-statistics scope, OOF strategy, event support and normalization before execution. Source selection of geometry plus fusion also needs to be included inside any honest internal performance estimate, rather than treated as a label-free fixed transform.

## 5. Replace endpoint placeholders with a falsifiable claim

Specify exact ranking endpoint, score polarity, raw versus excess AURC if used, common-success masks, original failure denominators, seeds and target aggregation, paired cluster intervals, minimum effect/support and pass/evidence-against/inconclusive/not-applicable predicates. Distinguish comparing risk rankings on one fixed error set from comparing complete classifiers with different errors. Specify an operating objective and absolute utility/security reporting as well as relative harms:301 showed that favorable relative numbers or high coverage can coexist with high target FA/BFNR.

One untouched target can support a locked external test on that population, not broad transfer across target domains. Subject/video resampling quantifies within-target conditional uncertainty, not uncertainty over new domains. Freeze a limited family of primary comparisons and clearly label secondary ablations; avoid selecting a favorable target after screening several new releases or reading target outcomes.

## 6. Avoid an unnecessary data-acquisition blocker

Section A's "before any revised-method fitting" unseen-target requirement conflicts with its valid exploratory fallback. It is not necessary to secure a new dataset before writing geometry code, checking source-only dimensions or doing a clearly labeled source-development pilot. The four observed datasets can be development material, with their prior exposure disclosed, including their previously official-test members if the new study explicitly assigns them development roles. They cannot supply new untouched confirmation of a method chosen after301.

Do not silently repurpose the old permanent manifests or unexpectedly impose official-train-only membership on the accepted old experiment. If the new study elects official-train-only development, create a separate explicit population version and explain the reduced denominators. A prospective target should be pinned before confirmatory execution, with official protocol, labels/evaluation access, rights and grouping checked. "Collected after locking" alone does not guarantee compatible attacks, sufficient event support or independence. If no independent target is available, end with a source-exploratory conclusion rather than stall indefinitely or claim new confirmation from the observed four.

## Concrete next deliverable

Replace303's open choices with one compact versioned experimental specification and executable synthetic/source-pilot package: exact G0/G2 transform definitions; preserved two-DINO comparator; nested fusion and risk supervision algorithm; fixed estimands/decision rules; deterministic small source-development sample and resource envelope; and either a named independent target/protocol or an explicit exploratory-only scope. Include the minimal inspectable301 normalization verifier in the final prior-study reproducibility bundle, without changing frozen executed code.

No broad preprocessing, feature regeneration, training or new target acquisition/evaluation is approved by this review. Preparing code/tests and a concrete study package is the next useful work; seek one combined execution decision only when its actual inputs, implementation and resource scope are reviewable. Do not turn each ordinary transform/test/manifest step into another approval round. No re-audit of the accepted datasets, recreation of old images or reinterpretation of301 is required.

**303 motivates a plausible new exploratory study, not a demonstrated fix. Narrow the intervention, restore the strong comparator and make selection/claims executable before spending on a new run.**
