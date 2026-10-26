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

The [actual successor record](../results/analysis-freeze/freeze_record301-v3.json)
was created normally from clean commit
`c41c3bd4684800a8e464e852a360d4ac92d0aafa`, pinning156 paths. Its SHA-256 is
`a79323e3cfbf88094ad71d1a9c69e84b737795d2acea019f991f35778d9b8404`.
The original source record remains at SHA-256
`004b0fb546bde3fd2c56977be07a028c63ec63b40134d95605c5462a017d8d91`.
The normal explicitly selected analysis-freeze gate passes; committed
persistence and the complete private execution bindings are checked again
before requesting human authority.

## Tests and bounded execution requirements

All482 configured local tests pass, including hand-computed/tied raw AURC,
integer cluster multiplicities, undefined AP, no seed deletion, both-class
failure denominators, harmful/inconclusive/inapplicable outcomes, source-only
gate exclusions, typed action ledgers and committed successor persistence.
The exact-sized synthetic20-replicate bootstrap took.182s; this is a planning
observation, not a promised actual runtime. Python compilation and publication
privacy/whitespace checks pass. No Pylance editor type-check is claimed.

The subsequently approved single authority covers four targets x three seeds,1857 maximum
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

## Actual authority, execution and resource accounting

The owner explicitly approved `approve_locked301_fixed_target_evaluation`
after the revision3 seal, source-policy decision and complete bounded scope.
The normal [authorization](../results/locked-evaluation/authorization.json) and
exact [authority receipt](../results/locked-evaluation/authority301-v1.json)
retain that decision and the original clock. This was one scientific worker,
not a repeated target experiment.

The [actual run receipt](../results/locked-evaluation/run301-v1.json) records
successful completion of every target/seed combination,8787 successful context
prediction rows,421776 risk values and35316 original action records across
both systems and both strategies. All2943 originals, including14 technical
failures, remain in the per-seed operational ledgers. The same2929 successful
originals per seed enter ranking; no missing/failure row is silently dropped
from original-denominator metrics.

Exactly1857 new image forwards extracted619 SiW images through three
backbones. The2310 existing target-success feature rows were reused per
backbone. No new source fitting, optimization, text inference, detector run,
download, threshold reselection or target tuning occurred.

| Actual bound | Observed |
|---|---:|
|Worker completion from original approval|219.838s|
|Saved-only closure from original approval|515.811s|
|Sampled combined process-tree peak RSS|2657857536 bytes|
|Owned new and temporary storage peak|74796159 bytes|
|Maximum per-backbone CUDA peak allocated|642748416 bytes|
|Maximum per-backbone CUDA peak reserved|704643072 bytes|

These observations are below the approved caps. CPU RSS is the supervisor's
sampled process-tree peak, not an unsampled exact maximum. The supervisor and
scientific worker exited; completion does not authorize another experiment.

## Saved-only closure and disclosed serialization defect

The original sealed `--close` reconstructed all twelve saved prediction/risk/
typed-ledger populations and their hashes, then failed its first point-table
comparison. Its in-memory
`operational/heterogeneous/source_class_counts/OULU-NPU` has integer keys
`0,1`; the unchanged saved JSON necessarily has string keys `"0","1"`.
Python dictionary equality therefore fails even when the metric values agree.
This is a readback-verifier defect, not a successful native closure command
and not a worker/model failure.

An additive saved-only verifier outside the frozen repository first proved
that all twelve saved point tables equal their reconstructed tables exactly
after JSON object-key normalization. It then invoked the unchanged full
closure replay with only its in-memory point-table comparison representation
normalized. The entire correction to the comparison representation is:

```python
original_metrics = run.cell_metrics
def canonical_metrics(*args, **kwargs):
    return json.loads(json.dumps(original_metrics(*args, **kwargs)))
run.cell_metrics = canonical_metrics
run.close()
```

There is no numeric rounding, tolerance relaxation, score modification,
predicate change or scientific-code edit. The additive verifier checks the
normal original authority/deadline and exact completed-worker digest before
replay; it does not bypass the clean-tree/hash gate. It performs no encoder
or optimization calls and does not repeat bootstrap sampling. The original
frozen controller still contains the disclosed serialization defect; this
report does not advertise it as fixed in the sealed executable.

The [closure receipt](../results/locked-evaluation/closure301-v1.json) records
all8787 prediction rows and421776 risk values reconstructed from immutable
saved artifacts. Its accompanying
[verifier provenance](../results/locked-evaluation/closure-verifier301-v1.json)
binds the additive verifier SHA and the normalization-only scope. Read these
receipts together, not as evidence that unmodified native `--close` passed.
The completed scientific worker SHA remains
`09a090e8bae36da0618e61009dcc9ed7d49aa609a6f550fd53e038a0aaf729b0`.
All code/config/manifest/policy bytes pinned by revision3 remain unchanged.

## Actual locked-target results: all twelve combinations

All entries below are the registered outputs, not a selected subset.
H denotes heterogeneous and S denotes same-family. AP is heterogeneous
classifier-error AP; U is class-balanced raw AURC with domain-OOF risk.
All twelve heterogeneous error counts exceed20, so all four targets meet
the registered event-support rule. All2000 bootstrap replicates are valid
for every published endpoint/operational-harm seed, target and macro interval.

| Target | Seed | Successes | H errors | Domain AP | Sample AP | RQ1 delta | U H | U S | RQ2 delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|OULU-NPU|20260917|1800|574|.432913|.334359|.098554|.139449|.191803|.052354|
|OULU-NPU|20260923|1800|581|.437288|.323606|.113682|.146578|.193456|.046878|
|OULU-NPU|20261001|1800|578|.403267|.303583|.099684|.142239|.175123|.032884|
|CASIA-FASD|20260917|354|60|.634191|.824833|-.190642|.391439|.278171|-.113268|
|CASIA-FASD|20260923|354|70|.721292|.889856|-.168564|.440604|.451485|.010881|
|CASIA-FASD|20261001|354|66|.540210|.879578|-.339368|.449516|.341239|-.108277|
|MSU-MFSD|20260917|156|42|.518832|.358760|.160071|.186300|.125893|-.060407|
|MSU-MFSD|20260923|156|29|.272210|.239169|.033042|.168173|.100166|-.068007|
|MSU-MFSD|20261001|156|39|.403533|.318222|.085310|.188688|.121378|-.067310|
|SiW-Mv2|20260917|619|146|.277059|.317993|-.040934|.326496|.275361|-.051135|
|SiW-Mv2|20260923|619|133|.271316|.304013|-.032697|.282261|.277580|-.004681|
|SiW-Mv2|20261001|619|139|.260719|.309641|-.048921|.307693|.243022|-.064670|

### RQ1: inconclusive, not a positive primary claim

| Target or equal-target macro | Three-seed mean AP delta | Paired cluster95% CI |
|---|---:|---|
|OULU-NPU|.103973|[.078204,.136000]|
|CASIA-FASD|-.232858|[-.300831,-.146020]|
|MSU-MFSD|.092808|[.056029,.148976]|
|SiW-Mv2|-.040851|[-.081534,-.000829]|
|Macro|-.019232|[-.039570,.009115]|

Exact macro is-.019231811843688933. Seed macros are.006762425586500323,
-.013634216926001308 and-.05082364419156582 in registered seed order.
All four targets are event-eligible, but only two have positive target means;
macro positivity, positive lower bound and three positive supported targets
all fail. The macro interval crosses zero, hence **inconclusive**, not a
uniform negative-domain result. OULU/MSU improvements and CASIA/SiW reversals
are retained together. Negative source diagnostics did not establish this
target verdict in advance.

### RQ2: evidence against the registered heterogeneous superiority claim

| Target or equal-target macro | Three-seed mean U(S)-U(H) | Paired cluster95% CI |
|---|---:|---|
|OULU-NPU|.044038|[.017434,.075717]|
|CASIA-FASD|-.070221|[-.117042,-.031892]|
|MSU-MFSD|-.065241|[-.142305,-.006653]|
|SiW-Mv2|-.040162|[-.064876,-.017732]|
|Macro|-.032897|[-.055779,-.012521]|

Exact macro is-.03289657699948494. Seed macros are-.04311403179672533,
-.0037323651789490445 and-.051843334022780456. The macro interval is wholly
negative; three target means violate the selective-harm limit of-.02.
The minimum+.01 effect, positive lower bound, three positive targets and two
positive seed macros all fail. This is **evidence_against**, not underpowered
or not-applicable and not an alternative-metric success.

### Source-selected K=1 target operations and original denominators

These are three-seed means under the preselected domain-OOF policies.
FA and BFNR use original attack/bona-fide denominators; coverage is
original-population operational coverage, not success-only/ranking coverage.

| Target | H FA | H BFNR | H coverage | S FA | S BFNR | S coverage |
|---|---:|---:|---:|---:|---:|---:|
|OULU-NPU|.266667|.242593|.872778|.310880|.424074|.792037|
|CASIA-FASD|.000000|.781481|.972222|.000000|.859259|.916667|
|MSU-MFSD|.141667|.308333|.845833|.072222|.566667|.739583|
|SiW-Mv2|.057090|.812261|.764045|.152855|.356322|.936865|

FA harm H-S averages-.0176332 macro, but MSU is+.0694444 and exceeds
the+.02 per-target limit. BFNR harm H-S averages-.0154135 macro, but SiW
is+.4559387 and exceeds+.02. Passing both macro operational guardrails
cannot erase either per-target breach. Source empirical FA<=1% plainly does
not imply target FA<=1%: no target policy was reselected to conceal this.
High BFNR remains a substantive utility cost, including the high-coverage
CASIA case where many bona-fide inputs receive a covered spoof decision.

### Fixed classifier diagnostics, not replacement endpoints

The cells are three-seed mean ACER/AUROC on the common success population;
these classifier metrics do not include fabricated failures as scored images.
Original-denominator technical effects are retained separately above.

| Target | DINO-Reg ACER/AUROC | OpenCLIP ACER/AUROC | H ACER/AUROC | S ACER/AUROC |
|---|---|---|---|---|
|OULU-NPU|.213542/.872420|.496875/.486532|.227662/.821054|.263657/.865445|
|CASIA-FASD|.402622/.999633|.479754/.578037|.367041/.998276|.294007/.999929|
|MSU-MFSD|.200144/.872629|.487500/.512069|.204454/.860417|.158046/.908477|
|SiW-Mv2|.245700/.839769|.497348/.581980|.243554/.840433|.234673/.849711|

High CASIA AUROC alongside poor fixed-threshold ACER illustrates why neither
ranking AUROC nor a new target threshold may replace the frozen operating
point. Weak standalone OpenCLIP is not removed after observing these results.
The aggregate run receipt retains all48 registered risk diagnostics per cell,
sample-OOF operating results, complementarity, classifier metrics and paired
intervals/valid counts; the displayed primary tables do not select a new method.

## Publication and interpretation boundary

The report and aggregate execution/closure/verifier receipts contain no raw
original/video/group identifiers, crops, features, model states or private
paths. The original source freeze and revision3 successor coexist unchanged.
Preparation-head CI40311973150 succeeded; that is preparation evidence, not
a claim about a later publication SHA's CI.
After final receipts were present,74 focused evaluator/governance/contracts/
source299 regression tests passed. Their test-module path was explicitly set
to match repository discovery; an initial differently scoped invocation had
an import-path error, not a scientific-worker failure.

The locked experiment is complete with a disclosed additive readback verifier,
RQ1 inconclusive and RQ2 evidence against. This supports neither calibrated
deployment risk nor certified security, nor uniform domain-OOF inferiority.
No source-confirmation loop or automatic target retry follows these results.
