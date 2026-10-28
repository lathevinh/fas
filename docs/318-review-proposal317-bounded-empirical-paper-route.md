# 318 - Review of317: narrow the contribution and move directly toward a paper

Date: 2026-10-28
Reviewed commit: `9998042ca3716326983fbbf55021481461b74432`.
Reviewed proposal: [317](317-q3-oriented-empirical-pad-paper-proposal.md).
Supporting results: [314](314-nested-fusion-utility-results.md),
[316](316-saved-score-oracle-threshold-diagnosis.md), and [Review315](315-review-report314-nested-fusion-infeasibility.md).

## Decision

**Accept the empirical-paper direction with the concrete amendments below.
317 is a reasonable scope proposal, but is not an executable experiment plan
or evidence that the paper has established novelty. Start the literature
comparison, manuscript draft and one supplementary-package specification
together. Do not create separate approval rounds for each preparatory task.**

The owner's objective is one defensible Q3-oriented paper. A new architecture,
positive fusion result, new dataset or state-of-the-art score is not inherently
required for that objective. Neither the target quartile nor the quantity of
completed artifacts establishes publishability. The remaining work should
improve the paper's evidence and positioning, rather than restart method search.

## 1. The main scientific risk is overlap with existing work

317 correctly leaves novelty unverified. This review supplies a concrete
closest reference that must be addressed, rather than requesting another
open-ended literature campaign.

[Lorenz, George and Marcel, *Foundation Models for Face Presentation Attack
Detection: A Unified Linear-Probing Benchmark*, IJCB2026](https://arxiv.org/abs/2607.26993)
already studies24 frozen encoders and reports strong within-dataset results
that transfer poorly across datasets. Its full text uses single-source
cross-dataset evaluation and a development-derived EER threshold. Thus
“frozen foundation features generalize poorly” and “use a specialist PAD
comparator” are already represented in closely related work.

The earlier [Costa-Pazo et al., *Face presentation attack detection. A
comprehensive evaluation of the generalisation problem*,2021](https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/bme2.12049)
also develops realistic generalization evaluation. Generalization failure
itself cannot be presented as a newly discovered PAD problem.

**Recommended narrower contribution:** characterize low-FA operating transfer
of a small fixed set of frozen-feature PAD systems, separating (a) failure
of a source-derived operating threshold from (b) insufficient empirical
low-FA separation of the stored scalar scores, with matched multi-source
evaluation, uncertainty and explicit missing-policy outcomes.

This is a candidate contribution requiring a focused prior-work comparison,
not a verified first-of-its-kind claim. The oracle is ordinary empirical ROC
analysis; do not market its order-statistic implementation as a new algorithm.
The comparison should explain whether the *combined empirical evidence*
answers a question absent from the closest papers. Two pages covering the
closest studies and a claim-to-evidence table are enough for the immediate
decision; an exhaustive survey is unnecessary.

## 2.316 strengthens the diagnosis, but changes the proposed story

I recomputed all public summaries from612 exported cases and240 common-threshold
groups and checked the public JSON hash against its verification proof.
Primary oracle-attainable counts are CASIA54/54, MSU41/54, OULU0/54 and SiW4/54.
The best OULU case has43.5606% BFA at attack FA<=5%, below the adopted50% floor.

Consequently, a paper claiming merely that “AUROC is good but the threshold
is wrong” would be incomplete. CASIA exhibits substantial threshold headroom;
OULU has insufficient empirical low-FA separation even with hindsight threshold
selection for every tested fixed reference. These are different observed
failure modes. Do not generalize the latter to all embeddings or classifiers.

Keep three quantities separate in the paper:

| Quantity | Meaning |
|---|---|
| AUROC | Ranking across the full score range |
| Source-derived threshold FA/BFA | Measured operating transfer of an available policy |
| Evaluation-label oracle BFA at FA<=5% | Sample-specific fixed-score diagnostic headroom |

All5%/50% utility claims remain specific to the adopted exploratory objective.
Oracle maxima are not deployment results or population guarantees. Neither
the54 cases nor overlapping folds/seeds are54 independent replications.
The missing selected policies in314 remain missing;316 does not supply them.

## 3.317 should not turn protocol comparability into another dataset project

The proposal leaves the main protocol and comparator undecided. That is the
largest execution gap. My recommended default for the supplementary package is:

- Keep OULU, CASIA, MSU and SiW. Do not add Replay-Attack merely to reproduce
  an MCIO leaderboard. State explicitly that this four-dataset combination
  differs from MCIO.
- Use train-on-three/test-on-the-fourth as the principal supplementary
  comparison, with3 fixed seeds:12 final evaluation contexts per system.
  Source fitting/validation/calibration must use only declared official
  source training/development populations, with subject separation and the
  existing applicable exclusions. Resolve datasets without a native dev
  split by one documented source-only group split before fitting.
- Evaluate on the declared official target test populations. Do not tune
  models, thresholds or epochs on target labels. These targets have already
  informed development, so describe the new study as developmental and
  comparative, not untouched confirmation.
- Keep the accepted single-middle-frame processing for the matched study.
  Declare it prominently. It does not reproduce published multi-frame or
  video aggregation protocols, and its scores must not be compared as if it did.
- Use4 systems: fixed DINO-Reg, supervised CLIP, fixed original equal two-DINO,
  and one specialist comparator. Keep314's nested selection study and316's
  source-development diagnostic as separate supporting evidence, rather
  than pooling them with a differently defined protocol.

This is an explicit cross-dataset design, not permission to label a custom
split an established benchmark. Official-partition restriction improves
interpretability; it does not by itself make differing datasets, frame rules,
training procedures and published results directly comparable.

**Comparator recommendation:** first check the official DeepPixBiS implementation
and training recipe as a compact specialist candidate, rather than defaulting
to a more expensive full-encoder FLIP campaign. This is a feasibility preference,
not a claim that its license, code or recipe has been verified here. Check those
items once while preparing the package. If unsuitable, name one replacement
and explain the reason in that same package; do not benchmark a menu of methods
to choose a favorable opponent. Distinguish matched-input retraining from an
exact reproduction of the original paper.

Existing features can be reused only where image/preprocessing bindings match.
Heads trained using a broader historical source population cannot simply be
relabelled official-training-only. Refit the affected heads and calibrators.
With no recipe grid, the recommended maximum final fits are36 frozen-feature
heads plus12 specialist training runs across the12 contexts; the two-DINO
system reuses its component fits. Any calibration fits, validation passes and
inference are additional work that must be counted explicitly. This inventory
is not a sealed resource budget: set the comparator's epoch/compute ceiling
and exact fixed recipe in the single execution package before running it.

## 4. The final analysis must answer a small, fixed set of questions

Use AUROC, source-threshold FA/BFA and compatible PAD error metrics with explicit
failure denominators. Retain5%/50% as the existing diagnostic endpoint; add only
a small predeclared low-FA sensitivity view. The oracle and source policy must
appear side by side, with integer supports and error counts.

Report conditional uncertainty by subject or justified connected group,
preserving paired comparisons. Describe seeds separately as training
variability; do not treat repeated images or folds as independent samples.
For retrospectively chosen oracle operating points, label the estimate as
descriptive. If intervals are provided, account for reselection of the oracle
inside the resampling procedure and state their limited interpretation.

Do not infer causation from a dataset/camera/attack-type breakdown. Do not
claim classifier calibration alone fixes OULU. Do not claim fusion has a
measured negative gain where selection returned no policy.

## 5. Concrete progression and stopping rule

The next deliverable should be **one integrated paper-completion package**:

1. A short closest-work table, precise contribution paragraph, and at most
   two venue candidates with verified scope and ranking source/year/category.
2. The above main protocol resolved to exact manifests, source splits,4
   systems, fixed recipes, thresholds, uncertainty rules and resource limits.
3. A manuscript draft containing the introduction, related work, methods,
   existing-result tables and limitations. Leave only supplementary-result
   cells pending. Writing begins now, rather than after finding a positive result.

Preparation and writing can proceed immediately within the requested planning
scope.317 itself explicitly excludes scientific execution; this review does
not override that boundary. After the integrated package, obtain one owner
decision for the bounded computation, then execute, verify and fill the paper.
Do not insert a separate review/approval gate for every table, dataset or seed.
Technical repairs within the agreed experiment need no new scientific proposal
unless they change the question, recipe, data access or budget.

After that single supplementary package, stop model search and finish the
manuscript. Retain unfavorable outcomes. If the comparison adds no defensible
contribution, make one explicit scope/venue decision; do not automatically
launch calibration rescues, risk gates, new encoders or another dataset.
An external dataset is optional for a stronger future claim, not a prerequisite
for this explicitly developmental empirical paper.

## Verification and scope of this review

Exact-head [CI40620168328](https://github.com/lathevinh/fas/actions/runs/40620168328),
[validate122592009142](https://github.com/lathevinh/fas/actions/runs/40620168328/job/122592009142)
shows success for all12 listed steps, including the synthetic regression suite.
Locally,13 existing oracle/common-interval tests passed using AST-extracted
actual functions and test classes, including150 randomized exhaustive-threshold
comparisons. Public612-case summaries,240-group counts and normalized public
JSON hash were verified. This is partial local numerical verification, not a
full controller import/run, private-score replay or external scientific replication.
The proposal has no new trained model or accuracy result to accept.

**Final disposition:317's direction is accepted with this narrower contribution
and consolidated completion route. Proceed to the integrated package and draft;
do not create another open-ended literature or fusion-search cycle.**
