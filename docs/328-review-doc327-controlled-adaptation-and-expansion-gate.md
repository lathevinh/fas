# 328 - Review of327: keep the paired study, repair the expansion criterion

Date: 2026-10-30.
Reviewed commit: `4431c39bb5d74525fbcd62e0aa88e380e1fad9c9`.
Preparation: [327](327-controlled-dino-adaptation-preparation.md).
Specification: [paper327](paper327/specification.json).
Prior recommendation: [326](326-recommendation-dino-adaptation-and-low-fa-controlled-study.md).

## Decision

**Accept327's preparation and paired-reference direction, with required
amendments to the expansion rule and objective interpretation before execution.
Do not accept the current gate unchanged. Continue implementing this same
eight-run study; another research-direction proposal is unnecessary.**

327 is not a completed scientific experiment. Scientific training starts,
dataset image reads and target evaluations are all zero. The recorded GPU
experiment demonstrates capacity for a synthetic backbone backward pass,
not PAD improvement or readiness of the full augmentation/attention pipeline.
Publication of this review does not supply the execution approval reserved
by327. Complete the concrete implementation before that single decision.

## What is well specified

The reference is an independently reconstructed full DINO-Reg PAD pipeline,
not a BCE-only model advertised as a reproduction of a stronger published
method. The proposed candidate adds exactly one fixed tail term. Both arms
share inputs, initialization, sampling, augmentations, checkpoint criterion,
calibration, threshold rule and evaluation populations. This directly tests
the incremental objective under the reconstructed reference.

The [Feng primary paper](https://arxiv.org/html/2604.19196v2) supports the main
reference components: FAS-Aug, PDA, global classification and attention-weighted
patch supervision, with the declared224 input/batch32 training settings.
327 correctly distinguishes researcher-fixed reconstruction details from
reported author settings, and does not claim an exact original-paper result.

Keep the explicit differences from the publication: source-only checkpoint/
threshold selection, accepted single-frame inputs and the SiW local intersection.
The old frozen DINO518/CLS-plus-mean-patch comparator is historical context;
it cannot isolate the causal effect of adaptation against the new224/CLS
pipeline. The present eight-run comparison can test the added term. Do not
claim a matched frozen-versus-adapted ablation from it, or add another arm
automatically to fill that separate question.

## Required amendment1: the gate can reject a clear operational improvement

`gate.py` currently requires two targets with both reference and candidate
FA-safe and at least5pp BFA gain. It also rejects a BFA drop greater than5pp
on any target, including where the reference violates the FA constraint.
These choices can penalize removing the reference's unsafe acceptances.

I ran this synthetic counterexample through the actual gate. All class
supports are100 originals and percentages equal integer acceptance counts:

| Target | Reference FA /BFA | Candidate FA /BFA |
|---|---:|---:|
|OULU|40 /90|5 /60|
|CASIA|0 /40|0 /60|
|MSU|20 /90|5 /65|
|SiW|10 /80|5 /60|

The candidate changes joint-utility success from0/4 to4/4 with no newly unsafe
target. Yet the gate returns `stop`: three raw BFA regressions and only one
qualifying safe-paired BFA gain. This is not an integer arithmetic bug; it
is an unsuitable criterion for the intended operating-improvement question.
Unsafe-reference BFA is not a same-security usability baseline.

**Recommended replacement, to fix before any real outcomes are inspected:**

1. Count a target as improved if the candidate meets joint utility and the
   reference does not, **or** if both are FA-safe and candidate BFA improves
   by at least5pp. Count each target once. Require at least two improved targets.
2. Retain an increase of at least one in joint-utility target count.
3. Retain zero newly FA-unsafe targets where the reference was FA-safe.
4. Apply the5pp BFA-regression veto only where both policies are FA-safe.
   Report all other FA/BFA changes without treating an unsafe reference's
   greater acceptance as an automatic usability veto.
5. Retain complete eight-run reconstruction, all primary rows, exact integer
   supports and explicit missing-policy failure. The controller, not the
   count-only gate, must establish these prerequisites.

This remains a practical exploratory budget decision, not a statistical
significance claim or guarantee of deployment safety. Add the counterexample
and the existing gain/security boundaries to the gate regressions. Update
specification, prose and implementation together before sealing. Do not retain
both rules and choose whichever passes after target evaluation.

## Required amendment2: this minibatch objective is hardest-attack ranking, not resolved5% pAUC

The score orientation is correct: `softplus(1+b-a)` increases when an attack
has a low attack score or bona-fide has a high one. Minimization pushes those
scores in the appropriate directions. Source-balanced averaging is explicit.

However, for n attacks and tail fraction q with `n*q<=1`, the implemented
fractional-tail mean is **exactly the maximum hardness**. At batch32 with the
declared10-11 observations/source, even post-augmentation class changes leave
at most11 attacks/source. Thus q=5% selects the single hardest attack/source;
it does not resolve a5% empirical region. Fractions small enough to satisfy
the same inequality produce the same loss, apart from numerical roundoff.

327 acknowledges this limitation, but the final method must name the actual
learning rule plainly: **source-balanced hardest-attack ranking with a
cross-source bona-fide comparison**. The5% evaluation objective remains valid;
it is not a proof that this minibatch loss optimizes population pAUC at5%.
No larger batch, memory bank or extra candidate is required by this review.
Keep the fixed candidate and test its utility honestly.

The [LibAUC primary documentation](https://docs.libauc.org/api/libauc.losses.html#libauc.losses.auc.pAUC_CVaR_Loss)
already describes hard-negative pairwise partial-AUC optimization.327 properly
does not claim equivalence or a new CVaR algorithm. Source balancing and a
hard-example term are not sufficient novelty by naming alone. During the
existing reference audit, add a compact closest-PAD-loss comparison explaining
the exact distinction; do not create an open-ended novelty review gate.
Positive measured benefit over the strong reference is necessary evidence,
but still would not by itself prove methodological novelty or Q3 acceptance.

## Implementation work that should proceed now

Complete the already chosen FAS-Aug/PDA/APL reference, not a substitute selected
because it is easier to implement. Honor the owner's independent-reconstruction
choice; waiting indefinitely for author training code is unnecessary.
Where exact settings are unavailable, disclose one fixed reconstruction choice.
Do not assign attack labels to generic degradations without a defensible
primary-reference label rule. Complete that audit in the same implementation
deliverable rather than issuing one document per augmentation.

The shared full-batch redraw rule changes the realized augmentation distribution.
Use addressed RNG streams so both arms receive identical accepted source
examples, donor/mask choices and redraw outcomes at each common epoch/step.
Record post-augmentation source/class counts and redraw counts. Tests should
cover exhausted donors/classes, the32-attempt failure path and paired identity
of accepted batches. Log ordinary and tail loss separately and require finite
gradients; do not silently change the0.1 weight after observing their scale.

Implement attention extraction through a path whose actual output can be
verified:256 image patches at224 input, correct CLS/register exclusion,
normalized detached weights and patch labels consistent with the PDA mask.
The optimized attention backend may not expose weights directly; make any
necessary attention-path change identical in both arms and include it in
the integrated synthetic probe. A backbone-only timing does not validate APL.

The proposed72-hour envelope is a ceiling, not a runtime prediction. Its eight
6-hour context caps,12-hour reconstruction and6-hour analysis leave6 hours
for other work if all phase maxima are reached. Validate actual integrated
memory, checkpoint handling and total-phase accounting. Retain the existing
no-automatic-retry and no-shortened-success rules without adding approval
rounds per target or component.

## Verification and limits

Exact-head [CI40986450385](https://github.com/lathevinh/fas/actions/runs/40986450385),
[validate123838496529](https://github.com/lathevinh/fas/actions/runs/40986450385/job/123838496529)
shows success for all12 listed steps, including synthetic regressions.
The reported601 producer tests and measured GPU probe are separate evidence.

On this Windows host, five gate/specification tests passed normally. The
receipt test fails on raw working-tree bytes because Git converted LF to
CRLF; both receipt pins match after normalization to the Linux/Git convention.
This is a portability issue in that test, not evidence that the measured
Linux code changed. The torch objective test was skipped because torch is
not installed here. No local GPU/gradient or complete-reference test is claimed.
The real gate counterexample above was executed locally using the actual module.

The proxy receipt consistently reports roughly0.189s and0.193s per measured
step, approximately6.4GiB allocated memory, ten synthetic optimizer steps
and zero scientific starts. Only three timed steps/arm were measured; no
claim about full training throughput, convergence or target accuracy follows.
Previous324 results remain untouched. Technical readbacks are not visual
adjudication, external scientific replication or a successful PAD result.

## Next deliverable

Deliver **the implemented eight-run package**, containing the corrected gate,
accurately named fixed objective, complete reconstructed reference, paired
data/attention tests, integrated synthetic measurements and bound execution
inputs. Then present the single execution decision anticipated in327.
No additional direction-selection document is needed.

After the first eight runs, apply the one sealed practical gate, preserve
every target and decide whether the remaining two seeds merit the separately
defined expansion. A gate failure ends this objective; a pass is eligibility
for further assessment, not evidence of independent confirmation. Neither
outcome authorizes retuning on these targets.

**Final verdict: preparation accepted with the above amendments. Fix the
operating gate and objective claims, finish implementation, and move to the
bounded experiment rather than another planning cycle.**
