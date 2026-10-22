# 280 - Remaining OULU image preprocessing and explicit active parameter pin

Date: 2026-10-22
Implements: [Review279](279-review-doc278-train-batch-and-reconnection.md)
Parent: `388815c`

## Final status

**OULU selected-image preprocessing and full original-denominator manifest are
complete.** One approved1979-frame batch succeeded with zero new detector
failures. Full saved-output readback passed for all4949 selected frames,
including2970 reused train outputs. The immutable manifest contains4950 unique
original IDs and retains the one calibration decode failure without an image,
score or fabricated detector outcome. The process exited0.

The [machine aggregate](../results/phase1/oulu-preprocessing280-completion-v1.json)
records the accepted software result. All three fixed visual sheets were
actually opened after completion:32+32+26=90 tiles. The
[additive visual receipt](../results/phase1/oulu-preprocessing280-visual-review-v1.json)
records this later inspection without rewriting creation-time visual-pending
flags in the machine receipts. This is not training, calibration fitting,
target execution or global scientific readiness.

The historical launch report observed444 new rows and explicitly withheld
completion. That snapshot is superseded by the measured final result here,
not reinterpreted as an earlier acceptance.

Accepted2970 train outputs are reused, not inferred again. No archive recovery,
new pilot,105GB rehash, detector download or fitting is part of this stage.
The present recovered archive identities matched before launch.

## Measured execution and actual inspection

The authority-to-terminal batch clock was6843.697576761246 seconds
(1h54m03.698s), below4 hours. The separately supervised worker/readback portion
was6197.2964209090005 seconds (1h43m17.296s). Measured peak process-group RSS
was612544512 bytes (about584MiB), below4GiB. Peak declared total retained
storage across274/276/278/280 was15417831466 bytes (about15.42GB), below24GiB.
These are measured/sampled peaks, not continuous hardware maxima. GPU time0,
downloads0, archive rehashes0 and automatic retries0.

The new batch checked264824 native-frame commitments while extracting only
the1979 frozen selected frames; selected-video payload was42388241168 bytes of
cumulative sequential input, not retained output. Final readback reconstructed
all new and reused shared-context crops from selected RGB and verified both
bicubic branches, PNG/RGB hashes and exact asset sets. The full manifest binds
4949 selected-frame assets plus14847 crop assets (19796 image assets), all4950
originals and the active-v3 configuration SHA256.

Final role reconciliation:

| Role | Originals | Detector successes | Detector failures | Pre-detector failure |
|---|---:|---:|---:|---:|
| train, reused | 2970 | 2970 | 0 | 0 |
| branch_calibration | 990 | 989 | 0 | 1 |
| g_domain | 990 | 990 | 0 | 0 |
| Total | 4950 | 4949 | 0 | 1 |

After software completion, all published private receipt commitments, full
manifest original/selected/role joins, final cap arithmetic, active policy,
inherited source bindings and current archive guard were checked again before
the visual receipt was recorded. The opened sheets exactly match the90 unique
fixed planned indices and their saved hashes. Every tile shows a framed face
with eye/nose/mouth regions present; no blank or background-only crop was
observed. Closed eyes, pose, glasses, blur, strong exposure and low contrast are
retained original appearances, not reasons for replacement or relabeling.
Zero detector failures means no detector-failure sheets were expected. The
preexisting decode failure has no image to inspect.

This is the executing assistant's actual fixed-sample crop-usability inspection,
not an independent human rating, all4949-image visual inspection, detector
accuracy estimate or PAD validation. No model score, threshold selection or
fitting was performed.

## Combined owner authority and measured budget

The owner explicitly approved implementation checks, one execution/readback,
actual visual review, the full selected-image/crop manifest and the explicit
active-v3 parameter pin. Scope is fixed `branch_calibration`/`g_domain`
source-role images only: no model scores, score fitting, threshold selection,
backbone execution, target access, training or later evaluation.

Exact frozen remaining population:

| Role | Originals | Selected frames | Retained pre-detector failure |
|---|---:|---:|---:|
| branch_calibration | 990 | 989 | 1 |
| g_domain | 990 | 990 | 0 |
| Total | 1980 | 1979 | 1 |

Read-only accepted media metadata established42388241168 cumulative selected-video
payload bytes and264824 native frames for those1979 selected transactions.
Existing274/276/278 retained storage was9351144291 bytes. The measured278
selected-pixel ratio predicts approximately5566.781 seconds (1h32m47s) and
6017281770 additional output bytes, about15.37GB combined. These are planning
estimates, not measured new throughput or storage guarantees.

The approved execution cap is **4 wall hours/4GiB process-group RSS/24GiB total
retained storage**, CPU only, one attempt, no automatic retry or cap extension.
The same four-hour clock includes this batch's preflight, execution and full
readback. Total storage includes274/276/278/280, the retained pack/model,
frames, crops, temporary payloads, manifests, logs and final records. A64MiB
reserve is kept for final/failure accounting. A genuine further archive
identity drift stops the package; reconnecting does not reset the deadline.

## Explicit configuration transition, not an image-method change

The owner approved making the concrete accepted parameters operational without
rewriting their historical inputs:

- [preprocessing_v2](../configs/preprocessing_v2.yaml) remains byte-unchanged,
  including its historically null detector hash.
- [pilot_v1](../configs/preprocessing_pilot_v1.yaml) remains byte-unchanged.
- [active preprocessing_v3](../configs/preprocessing_v3.yaml) pins the existing
  SCRFD weight,640 input, mean127.5/std128, score0.5/NMS0.4, one-thread CPU
  provider, largest-area deterministic primary face and accepted five-point
  rotation-about-eye-midpoint/shared1.30 clipped context geometry.
- [Canonical experiment](../configs/experiment_core_v1.yaml) now refers to v3.
  [Schema validation](../src/fas/preregistration.py) requires that explicit
  active pin while retaining v2 among the historical hashed inputs.
- [Shared policy checks](../src/fas/preprocessing_policy.py) require exact
  active parameters and exact equivalence to the accepted pilot geometry and
  detector recipe. Image exports still do not apply backbone normalization;
  checkpoint-native224 and official DINOv2518 normalization declarations are
  preserved for separately authorized later model stages.

The active-v3 SHA256 is
`a4f1a27ffc6418c548702e38f3454d67a17ec834fda351ed46d6accaba738c71`.
New per-unit records use that actual v3 hash. Old train records retain their
original pilot-parameter hash; the full manifest explicitly joins them to the
equivalent active pin without editing accepted records.

This is a parameter-definition transition, not permission to execute another
dataset/fold or a claim of global scientific readiness. The study population,
model families, source roles, frame selector and scientific estimands do not
change.

## Execution and denominator invariants

[Runner280](../scripts/preprocess_oulu280.py) joins all4950 immutable transactions
to frozen role/class parents. It requires exactly2970 accepted train IDs,
989 selected calibration IDs,990 selected g_domain IDs and the one original
calibration pre-detector failure. It refuses duplicate/missing IDs, role
intrusion, altered selected frames and detector-success replacement.

The worker may infer only the two approved non-train roles. Strict selected-video
payload hashes, full native decode commitments and frozen selected RGB pixels
are checked before detection. Selected frames and shared/224/518 crops are
written incrementally with immutable result records. Expected detector/geometry
failures are explicit terminal `non_accept`; unexpected exceptions stop the
package. No failed transaction disappears from original denominators.

A separate supervised verifier reads all1979 new and2970 retained selected
outputs, checks exact frame/crop sets, source/frame/role/media/config/model
joins, frozen RGB hashes, recomputed shared context and exact bicubic branch
pixels. Re-reading accepted train output pixels is not re-running inference
or replaying historical forensic image folders. The completed full manifest
must cover exactly4950 originals/4949 selected frames/one preexisting failure.
That failure remains `detector_status=not_run`, has no image/score/classifier
error, and retains its calibration class and original denominator.

The supervisor checks the readback/manifest counts and all record commitments,
current guards and final resource caps before software acceptance. A rejected
attempt receives separate denominator-preserving failure accounting; it does
not trigger a second attempt.

Visual indices are fixed before outcomes by role, class and the first two
frozen filename components, supplemented by every100th manifest position.
All new detector failures get additional source-frame sheets. Sheets are
reconstructed during readback, then must actually be opened before an additive
visual receipt claims inspection. No mandatory all4950-image or independent
human inspection is inferred from this sample.

## Reconnection/source reconciliation requested by279

As part of this ordinary stage, not a new receipt-only checkpoint, actual
private278 receipts and current source bytes were reconciled:

- The three278 source hashes equal the values independently listed in279.
- The existing private supervisor's runner hash matches the accepted runner.
- The attempt lease's parent PID matches that supervisor and its plan hash
  matches the accepted immutable plan.
- The existing terminal resources report one attempt, no retry and successful
  readback; the additive visual receipt joins the same resources/readback.
- All7951 inherited source pins and the current recovered archive guard passed
  before launch.

This bounded reconciliation of existing recorded evidence does not claim an
independent witness to historical launch count or private execution timing.
No old record was regenerated to establish that claim. The reconciliation
commitments are carried into this plan and its terminal public aggregate.

## Validation before actual launch

```sh
PYTHONPATH=src:scripts:tests python -m unittest \
  test_preprocessing test_preprocessing_batch \
  test_preprocessing_completion test_preregistration -q
```

57 tests passed in116.866 seconds in the existing `fas` environment.
[New synthetic regressions](../tests/test_preprocessing_completion.py) cover
exact1979 subtraction and original denominators, active/legacy equivalence,
refusal of train/target inference, actual saved-pixel readback, missing/duplicate
outputs, expected detection failures, full4950 manifest checks, wrong final
readback summaries, spawn failure and final wall/RSS/storage caps. Existing
pilot/train tests remain unchanged. Schema tests require the pinned active
weight and keep later readiness gates blocked.

Python compilation, whitespace checks and actual canonical schema validation
also passed. Tests use synthetic media and no executable detector. No full
private-media replay or duplicate full repository suite is claimed.

## Persistent progress and handoff

Use the existing `fas` environment:

```sh
python scripts/preprocess_oulu280.py --status
```

This is read-only. Do not use `--run-approved` as a reconnect/restart command;
the package refuses an existing output root.

The private `oulu_preprocessing280_v1` package contains the actual owner
authority, persistent supervisor, immutable plan/attempt lease, incremental
records, execution log and a read-only30-second `progress.log`. It now contains
`worker_completion.json`, `full_manifest.json`, `readback.json`,
visual sheets, terminal `resources.json` and the additive `visual_review.json`.
All source/media identities and images remain private.

The local VS Code task `OULU280 Progress (30s, read-only)` is configured.
The VS Code tool client initially disconnected while opening it; after
reconnection its actual terminal output was confirmed. The independent batch
stayed alive throughout. Both the production process and detached progress
watcher have now exited0. The displayed100-percent counter described new
records written, not completion of the subsequent full4949-image readback.

The terminal public aggregate is
`results/phase1/oulu-preprocessing280-completion-v1.json`. It contains
counts, source-reconciliation commitments, the active configuration pin and
resource measurements, not private row identities. Final visual observations
are in the separate additive receipt, preserving creation-time pending flags.

## Retained scientific state

OULU local audit and accepted2970 train preprocessing remain complete.
Full4950-original accounting/4949 selected-image preprocessing is now complete
under the explicit active-v3 parameter pin. The one calibration decode failure
remains terminal and is not counted as a successfully preprocessed image.
The other six dataset/split audit fields remain not_audited;399 similarity
outcomes, accepted85/historical disagreement1/unresolved0, calibration990/989
and zero fitted scores remain unchanged. Joined assurance, training/OOF,
target evaluation, analysis freeze, locked evaluation and scientific readiness
are separate gated work and are not commissioned here.
