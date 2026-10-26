# 301 - Locked-target package and fixed evaluation

Date: 2026-10-26.
Governing review: [300](300-review-doc299-complete-source-evidence-and-analysis-freeze.md).

## Accepted source baseline and next execution boundary

Review300 accepts299 without source rework. All four data/image milestones,
integration/pilot295, first result297 and complete source experiment299 remain
closed. All twelve primary heterogeneous source AP contrasts favor matched
sample-OOF, and standalone OpenCLIP fails competence in all twelve combinations.
Neither source finding is tuned away or used to substitute a new primary.

This package implements locked target evaluation using saved selected models.
Its preparation uses saved source G_domain predictions and metadata/hashes
only, not target pixels, feature values, predictions or scientific outcomes.
Readiness, a committed manifest and successor freeze are not execution
authority. The final release is revision3; revisions1/2 were never authorized
or executed and are retained as superseded preflight provenance.

## Executable package and exact target scope

- [Configuration](../configs/locked_run301_v1.yaml).
- [Controller, authority, supervisor and closure](../scripts/run_locked301.py).
- [Fixed estimands and source-only gate selection](../src/fas/locked_metrics.py).
- [Final execution manifest](../results/locked-evaluation/execution-manifest301-v3.json).
- [48 final source-selected policies](../results/locked-evaluation/source-policies301-v3.json).

| Official target evaluation partition | Originals | Detector successes | Retained failures |
|---|---:|---:|---:|
|OULU-NPU test|1800|1800|0|
|CASIA-FASD test|360|354|6|
|MSU-MFSD test|160|156|4|
|SiW-Mv2 frozen Protocol-I test intersection|623|619|4|
|Distinct-original total|2943|2929|14|

All four targets and three registered seeds are mandatory. Target evaluation
is official test only, not each domain's full source population. Failure-
inclusive originals retain their class denominators; failures have no
fabricated scores, error labels or rank.

2310 successful target images already have compatible cached features from
rotations where those images were authorized sources. Only619 SiW official
test successes are uncached: at most1857 new image forwards across the three
registered encoders, zero new text forwards/downloads. Source roles/exclusions
are not applied as a target-test membership filter; SiW's five source-only
train exclusions do not delete official test originals.

The manifest binds source completion/closure, original source freeze,
training/extraction configs, exact checkpoints and runtime, cached shards,
selected final heads/calibrators/reference thresholds, all480 risk models,
source-selected policies, and exact target populations/masks. Its private
input hash also binds every original detector transaction.1378 aggregate
logical artifact hashes are public; raw IDs, private paths, features, models,
labels/prediction rows and transaction ledgers remain private.

The active manifest SHA-256 is
`e5a6ae6d706597c974089083fcf909514f3410d0bec4368a205a57a94330b41f`.
The configuration filename's v1 denotes the fixed recipe; manifest/preflight
revision3 identifies the tested implementation and exact artifact bindings.

## Source-only K=1 policy decision

Before target prediction, the owner explicitly selected
`worst_source_fa_1pct_max_coverage`. For each outer-target/seed and each of the
two systems/two OOF risk strategies, select only a threshold on saved,
permanent eligible source G_domain originals, excluding the whole outer
target. No head, calibrator, normalization or risk model is refitted.

Maximize equal-source-domain operational coverage subject to empirical
FA_end2end <=1% in each source domain, using original attack denominators.
Ties select lower macro BFNR, then lower macro FA, then smaller threshold.
Candidate thresholds include reject-all and all distinct saved risk scores.
This is source-selected empirical performance, not independently validated
or certified security, and not a target guarantee.

The gate filters only predicted-live decisions. Predicted spoof is already
a covered terminal PAD decision and receives no gate action/threshold.
Pre-detector and detector failures are terminal non-accepts, uncovered, with
null scores/errors. Operational coverage counts successful predicted-spoof
or accepted-live decisions; the separate ranking risk-coverage/AURC curve
ranks all detector-success errors. Abstaining an already spoof decision
cannot be counted as a new security intervention.

Actual source-selected ranges across twelve combinations:

| Risk strategy/system | Macro operational coverage | Macro BFNR_end2end |
|---|---:|---:|
|Domain-OOF heterogeneous|.7803-.9821|.0841-.8876|
|Domain-OOF same family|.6746-.9821|.0440-1.0000|
|Sample-OOF heterogeneous|.8750-.9848|.0841-.5383|
|Sample-OOF same family|.6720-.9821|.0356-1.0000|

Worst achieved empirical per-source FA is.0096154 across all48 policies.
High bona-fide rejection is retained and disclosed, not tuned away.

## Registered endpoints and decision states

RQ1 is non-interpolated error AP on the identical final heterogeneous
classifier/error set, domain-OOF R_DVd minus matched-sample R_DVd. One-class
error labels give undefined AP, never a synthetic score. Every estimable seed,
including one below20 errors, keeps weight1/3. A target is event-eligible only
when all three seed AP contrasts exist and at least two seeds have20 errors.
An undefined seed prevents a four-target primary macro; fewer than three
eligible targets is inconclusive. A pass requires positive macro, positive95%
LCB and at least three eligible positive target deltas.

RQ2 is same-family minus heterogeneous class-balanced raw AURC, using
domain-OOF R_DVd and the same detector-success mask. Each class raw AURC
uses expected random ordering inside exact-risk ties; it is not excess AURC.
Pass requires macro >=.01,95% LCB >0, three positive target deltas, two
positive seed-level four-target macros, no target selective harm >.02,
and heterogeneous-minus-same-family operational FA/BFNR harm <=.01 macro
and <=.02 on every target. Coverage is explanatory, not an extra pass gate.
Class-conditional excess AURC, cross-system AP and classifier metrics are
reported separately and cannot replace the primary scalar.

Both endpoints use seed-then-target equal means, never pooled predictions or
best-seed selection.2000 paired subject/video cluster replicates resample
within each target, sharing multiplicities across all methods, systems and
three seeds. Per-seed, per-target and macro intervals retain invalid-replicate
counts; fewer than95% valid replicates makes uncertainty unestimable.
Failures remain in original-cluster resampling for operational denominators
but never enter ranking. Uncertainty is conditional on these fitted models
and four targets, not a bootstrap retraining/generalization guarantee.

Claim dependencies come from accepted source evidence. Outputs distinguish
pass, evidence_against, inconclusive and not_applicable. A supported negative
interval or observed RQ2 guardrail breach is not concealed by another metric.
All40 saved risk variants per combination and eight fixed nonlearned
score diagnostics are scored without choosing a different primary.

Private typed per-original action ledgers cover both systems and strategies.
They retain original pre-detector `not_run` disposition plus explicit terminal
technical failure, rather than pretending the detector ran and failed.
Both systems share original IDs and the exact success mask.

## Pre-authorization fixes and immutable successor

Synthetic tests exposed an operational/ranking coverage conflation: an
all-spoof fixture incorrectly had zero operational coverage at a reject-all
live gate. The existing transaction contract explicitly forbids applying
the gate to spoof decisions. That counting bug was fixed before target
authority or predictions. Revision1 is superseded, not overwritten.

Revision2 then exposed a backward-compatibility error in the extended
technical-failure ledger check: older valid fixtures omit the optional
classifier_error field. The null check now rejects a non-null value when
present without requiring that optional historical field. Revision2 is also
superseded and never executed. The final revision3 follows the complete
482-test regression pass.

The source freeze is preserved byte-for-byte. Four formerly pinned files
change deliberately: the two governance CLIs, freeze-path validation, and the
typed technical-failure ledger contract. New evaluator files are also found
by artifact discovery. Consequently the old source record is not advertised
as matching the expanded evaluator. A new versioned record is created with
the normal source gate from a clean commit; explicit `--freeze-record`
selection retains current hashes, creation ancestry, unchanged pinned Git
paths and clean-tree checks. No old record is overwritten.

The execution manifest and source policies are also discovered as freeze
artifacts, so actual selected policies/configs/code cannot drift independently
of the successor record. Final target outputs are not selection inputs and
are not added to the frozen input map.

## Tests and bounded execution requirements

All482 configured local tests pass, including hand-computed/tied raw AURC,
integer cluster multiplicities, undefined AP, no seed deletion, both-class
failure denominators, harmful/inconclusive/inapplicable outcomes, source-only
gate exclusions, typed action ledgers and committed successor persistence.
The exact-sized synthetic20-replicate bootstrap took.182s; this is a planning
observation, not a promised actual runtime. Python compilation and publication
privacy/whitespace checks pass. No Pylance editor type-check is claimed.

The proposed single authority covers four targets x three seeds,1857 maximum
new image forwards, saved-model predictions,2000 bootstrap replicates and
saved-only closure. Limits are4h original-clock final deadline,3h30m work
cutoff,12GiB combined process-tree RSS,12GiB CUDA allocated/reserved and4GiB
owned new+temporary storage. Stop on any missing/changed input, nonfinite
output, mask/join error, cap or deadline. No automatic retry, reset, extension,
installation, checkpoint download, fitting, substitution or target tuning.

Successful outputs remain private until saved-only closure verifies exact
feature contracts,8787 context prediction rows, risk values and all original
actions/point metrics. This preserves a clean frozen worktree for the normal
execution/closure gates; only then are aggregate receipts published.
