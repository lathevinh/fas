# 320 - Review of319 and paper319: accept preparation and complete the bounded study

Date: 2026-10-28
Reviewed commit: `0720c58d0e4f8aaa3809b1abc6b2a077bcea6708`.
Package: [319](319-integrated-paper-completion-package.md).
Draft: [paper319](paper319/manuscript.md).
Prior direction: [Review318](318-review-proposal317-bounded-empirical-paper-route.md).

## Decision and immediate next action

**Accept319 as a completed metadata/preparation deliverable and paper319 as
a useful working manuscript. It contains no new supplementary model result
and is not ready for journal submission. Continue directly with technical
implementation and sealing of this same bounded comparison, while revising
the draft. No new scientific proposal, dataset or model-selection campaign
is needed.**

319 implements the requested integrated preparation: a real manuscript,
focused related work, a fixed four-system specification and concrete source
partitions. Its explicit pending results are correct. The48 comparison rows
are planned rows, not48 completed evaluations. Acceptance of preparation
must not be advertised as acceptance of a trained specialist or new accuracy.

The unimplemented controller is the main remaining execution task. Build and
synthetically check it now within the existing preparation scope, including
checkpoint selection, cache bindings, calibration, prediction, resource
enforcement and saved-score analysis. Do not request the same scientific
direction again.319 explicitly reserves scientific execution for a subsequent
single integrated owner decision; this review does not fabricate that approval.

## Verified evidence

Exact-head [run40625396397](https://github.com/lathevinh/fas/actions/runs/40625396397),
[validate122608976875](https://github.com/lathevinh/fas/actions/runs/40625396397/job/122608976875)
shows success for all12 listed steps, including synthetic regression.
All12 actual `test_paper319.py` tests passed locally through the normal
repository import path. No AST extraction was needed for this suite.

Independent public checks confirm:

- All four implementation hashes in the preflight receipt match normalized
  repository file bytes.
- Source roles total4562 originals/4545 usable, and evaluation totals2943/2929.
  Together these give7505 active originals/7474 usable/31 failures.
- The proposed per-context fitting counts, batch16,50 epochs and3 seeds imply
  exactly74400 specialist optimizer steps, matching the inventory.
- All24 oracle means and24 feasibility cells in the manuscript match316's
  public summary at the displayed precision. The corrected26.669% OULU
  fixed-DINO-CLIP mean is accurate.

These checks verify synthetic behavior, public arithmetic and code bindings.
Private partition membership, actual705 cache shard digests, image contracts
and runtime observations remain producer-reported: this host did not replay
the private metadata or load private arrays. Byte verification is not numerical
feature revalidation, visual adjudication or independent scientific replication.

## Main findings requiring concrete amendments

### 1. High priority: the manuscript does not yet explain the methods behind its completed results

Sections4.1-4.6 largely describe the proposed official-partition study, while
Section5 reports309/314/316 under different historical source roles and nested
training conditions. Section3.2 acknowledges this distinction, but a reader
still cannot reconstruct the completed experiment from the paper alone.

Add a compact completed-study methods subsection or supplement before final
submission. Specify the source-role populations, outer exclusion versus
pseudo-target holdout, which datasets fit each head, the nested weight
selection and calibration rules, six fixed references, and how the nine
applicable cases per source arise. Explain whether the reported309 CLIP
mean is source-domain-OOF rather than the pending final train-three/test-one
official-target result. Include a small study/population/selection/endpoint
table. Repository report numbers can remain provenance links, but cannot
substitute for scientific methods in a standalone paper.

This is a writing repair using existing evidence; no experiment is required.

### 2. High priority: the central policy-versus-oracle comparison is not yet a main result table

The current completed-result tables contain oracle BFA and attainability,
with only a few source-policy numbers in surrounding prose. Yet the stated
contribution is the *paired* available-policy/oracle diagnosis. Put source
FA, source-policy BFA and oracle BFA alongside one another for a small fixed
representative system set. The existing316 public summaries already contain
the necessary historical per-source means; no refitting is needed.

Show whether the available policy itself satisfies the FA constraint. If it
does not, the difference between its BFA and oracle BFA is not an attainable
same-security performance gain: the two operating points have different
attack error rates. Do not turn that difference into an unsigned “calibration
loss” or claim that target-label-free recalibration recovers the oracle.

For the pending study, retain the specified side-by-side48-row reporting and
one compact low-FA ROC figure. Keep historical and new populations separate.
If useful for diagnosis, save which source determines each minimum common
threshold; this follows directly from the already required source order
statistics and does not introduce another policy search or fitting task.

### 3. Medium priority: close the now-accessible prior-work gap and repair author attribution

The [Costa-Pazo2021 publisher full text](https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/bme2.12049)
is accessible in this review. It reports constrained operating-point analysis
(including APCER at BPCER10%), generalization evaluations and working-point
curves. Update the brief's “full text inaccessible” preparation status and
compare these existing analyses with the narrower policy-versus-oracle
question. Do not imply that looking beyond a single aggregate metric or
examining constrained ROC points is new. This review does not establish
that its exact threshold pipeline matches319 or that it exhausts all overlap.

Two bibliographic errors are directly verifiable:

- Reference[11] and the corresponding related-work row omit first author
  Peter Lorenz. Use Lorenz, George and Marcel for
  [arXiv2608.09633](https://arxiv.org/html/2608.09633v2).
- Reference[12] and its related-work row reverse the first two authors. The
  [primary text](https://arxiv.org/html/2604.19196v2) lists Mika Feng, Pierre
  Gallin-Martel, Koichi Ito and Takafumi Aoki. Use Feng et al. in the text.

The narrow empirical positioning remains reasonable. Resolving these items
is bounded editing, not a reason to reopen an indefinite novelty gate or
delay implementation of the already chosen comparison. No certified-Q3
venue has yet been established; ranking verification can proceed alongside
technical completion and does not determine model execution.

### 4. Medium priority: SiW is a declared video-grouped component, not a subject-independent benchmark

319 correctly exposes the missing SiW participant metadata and its local
Protocol-I intersection. This is material: it affects source checkpoint and
threshold selection as well as target uncertainty. The draft appropriately
does not invent participants or claim full-release coverage.

**Recommended disposition:** retain this declared video-grouped amendment
in the one integrated owner execution decision. Do not make identity recovery
or replacement with a new dataset a default prerequisite for this developmental
comparison. Keep participant-independent conclusions restricted to datasets
where that property is verified. SiW bootstrap intervals may understate
uncertainty from repeated participants and must remain labelled conditional
video-component intervals. The four-dataset macro is descriptive of this
heterogeneous design, not a uniform participant-independent benchmark.

For the final controller, carry forward direct known-subject isolation checks.
The preparation's connected-component function joins `group_id` and exact
frame hashes; it does not independently enforce that all records sharing a
known `subject_id` have the same group. No actual subject leak was established
here. Add the direct assertion when revalidating final private inputs, rather
than relying only on the existence of a nonempty subject field.

### 5. The specialist choice is coherent; its implementation and runtime are still unverified

I inspected the pinned [official DeepPixBiS source](https://github.com/bioidiap/bob.pad.face/blob/555f181a76fa39d20f0c61ef1dc616bd85b817c1/src/bob/pad/face/deep_pix_bis.py).
Its DenseNet161 feature slice,384-channel14x14 pixel map, global head and
pixel-mean inference support319's architecture description. Its classifier
`fit` does not implement training.319 correctly proposes architecture
retraining and does not pretend the accessible inference wrapper is a ready
training pipeline or use OULU-trained PAD weights as a clean comparator.

Keep the researcher-fixed recipe and license handling explicit. Before
execution, use synthetic inputs to verify the exact pixel/global computation,
gradient flow, ImageNet feature initialization, train/eval behavior, score
polarity and checkpoint restore. Fix the model initialization seed, sampler
and augmentation randomness, deterministic runtime, calibrator initialization
and solver settings in the sealed implementation. Do not choose these after
seeing target performance. Compatibility checks do not require a scientific
pilot or a menu of baseline recipes.

The40-minute/context and12-hour package ceilings are proposed limits, not
demonstrated feasibility. Verify enforcement synthetically, then honor the
single-run incomplete-result rule if a ceiling is reached. The12 intended
training starts are not12 independent test sets. Do not retrospectively
shorten training and still label the result the same completed comparison.

MSU calibration's18 attacks/6 bona-fide originals are correctly disclosed.
At FA5%, its attack error budget is zero; at1% it is also zero. Therefore
different declared sensitivity levels can produce the same threshold because
of sample resolution. Report realized error budgets rather than interpreting
repeated thresholds as evidence of robust low-FA calibration. This is a
precision limitation, not a reason to change the split after observing scores.

## What should happen next, without another proposal cycle

1. Implement the existing fixed training/analysis/watchdog package, validate
   its synthetic behavior, and bind exact runtime, initialization and inputs.
   Keep36 frozen-head starts,12 specialist starts,48 calibrators and the
   current four-system/no-grid scope.
2. In parallel, make the methods/table/reference amendments above. Preserve
   pending cells until the supplementary experiment runs. Move detailed
   historical fusion bookkeeping to supplementary material if it obscures
   the primary operating-transfer question.
3. Present one executable package for the single owner decision already
   anticipated in319, including the explicit SiW limitation and existing
   budget. Do not solicit separate decisions per dataset, seed or table.
4. Run once after that decision, verify saved results, fill the main comparison
   and finish the manuscript. Keep negative results. Do not add a backbone,
   gate, dataset or rescue grid because the outcome is unfavorable.

**Final verdict:319's preparation and numerical transcription are accepted.
Paper319 is accepted as a working draft requiring the identified amendments
and the pending matched results. It is not submission-ready. The next work
is implementation plus manuscript revision within the same bounded package,
not another round of research-direction proposals.**
