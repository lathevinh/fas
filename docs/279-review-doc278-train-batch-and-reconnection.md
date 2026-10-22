# 279 - Review of278: completed train batch and reconnection evidence

Date: 2026-10-22
Reviewed final commit: `b84e775fbe43d98da88b913832768a2584cc408f`
Compared launch/in-progress commit: `4b54c00`.

## Decision

**Accept278 without rework as the reported completed OULU source-train preprocessing milestone:2938 new transactions plus32 reused pilot transactions,2970 total.** No new blocking implementation defect was identified. Do not rerun the batch, recovery or pilot solely because the chat connection was lost. Keep OULU local audit complete.

Acceptance is based on published consistency, source review, targeted independent tests, current CI and bounded reported private execution evidence. It is not an independent inspection of all private records/images or proof that a disconnected agent remembered its instructions. The actual state/parent checks are the relevant evidence, with limits below.

## Reconnection and executed-source checks

The launch-publication snapshot correctly described an incomplete recovery and zero new transaction outputs. Final publication changes only README, report and the two public receipts. Batch/recovery/test source bytes are identical between the in-progress and final commits. Independently calculated repository-LF hashes:

| Source | SHA256 |
|---|---|
| scripts/preprocess_oulu278.py | `041709644b6ecf89ff6bb21ce2d0742a85495a672c239c40b28cbeb8b7ad770f` |
| scripts/recover_oulu278.py | `60e5ec158dca5b2be9feb7c5e098a6cc12644606a8f51be4dbdd6dbce3b21f1d` |
| tests/test_preprocessing_batch.py | `5045f3975fc05bd9e99ed2967d115851ffffb43b6f35d9959de28a8c303eb964` |

The code records persistent supervisor identity and runner commitment, immutable recovery/attempt/plan records, incremental outputs and a terminal receipt. `--status` is read-only; `--run-approved` refuses an existing package, so it is not a restart command. Worker/verifier children require the parent-bound attempt lease and fixed plan hash. Batch inputs/code/config are pinned and rechecked. Recovery must reach exact hash equality before the batch authority/deadline is created. The same six-hour clock covers batch preflight/execution/readback; reconnecting does not reset it.

The source comparison establishes no code change between the two published snapshots. The private supervisor/log/locks and their timestamps are unavailable for independent readback here, so I cannot independently certify launch count, precise interruption timing or equality of the actually recorded runner hash with the values above. Source checks and reported immutable records support the single-attempt claim; they do not replace raw execution history. Reuse those existing records if provenance is queried; do not regenerate them or create a new execution to prove the old one. Include their launch/runner/attempt reconciliation in the next ordinary handoff if needed, not another receipt-only checkpoint.

## Population, readback and visual evidence

Independently ran the actual two regression methods for exact partitioning and combined-ledger integrity against the actual published function ASTs. Tests pass for deterministic subtraction/reuse and refusal of duplicate/missing IDs, wrong reused parents, target-role intrusion, failed selected frames and failed rows misclassified as accept. This was a standard-library synthetic run, not a private-media/OpenCV replay.

Readback requires exact new transaction/asset sets; source/frame/media/config/model joins; source RGB pixel hashes; shared-context reconstruction; bicubic224/518 joins; explicit detector outcomes; and a combined ledger with the exact union of planned new/reused IDs. It revalidates the32 pilot results rather than inferring that any32 files count as reuse. Parent supervision runs worker and verifier separately, validates the combined record commitments and final guards/caps before acceptance. This addresses the earlier worker0-without-completion failure mode.

Public receipt arithmetic independently reconciles2938+32=2970; new successes2938/failures0; combined successes2970/failures0. New crop count8814 in the report equals2938*3. The visual receipt binds the same private readback and resource hashes as the machine aggregate and reports3 opened sheets/65 tiles. Creation-time visual-pending machine fields remain historical, not current evidence that no inspection occurred. The additive receipt supplies the reported later inspection without rewriting them.

The actual private2970-ID ledger, per-row assets, logs, approvals, recovery contents and sheet images are not available here. Therefore exact real ID uniqueness, private output hashes and actual image quality are reported execution/readback evidence, not independently recomputed from all records by this reviewer. I did not view those65 tiles. The executing assistant's sample usability check is not all-image inspection, independent human confirmation, detector accuracy or PAD validation. Those limits do not create a new requirement to manually inspect2970 faces.

## Resources and CI

The aggregate reports105116817408 recovery bytes in1245.471 seconds and exact three-archive equality; batch-authority-to-summary8264.377 seconds, below21600; measured RSS676708352 bytes, below4GiB; total retained output9367325346 bytes, below24GiB. Independently checked the published cap arithmetic and total-storage scope including274/276/model pack. Input payload61897964372 bytes is cumulative sequential input, not retained-output usage. No cap extension, download or retry is reported. Peaks remain measured/sampled observations, not continuous hardware maxima.

Exact-final-commit GitHub checks/job HTML confirms [run39741462342](https://github.com/lathevinh/fas/actions/runs/39741462342), [validate119699417130](https://github.com/lathevinh/fas/actions/runs/39741462342/job/119699417130), head `b84e775fbe43d98da88b913832768a2584cc408f`: all12 listed steps have success conclusions including Complete job. No exact API completion timestamp is asserted. CI is final-code software evidence, not private execution or owner-authority verification. No duplicate full local suite or real batch replay was needed for this review.

## Move forward

Train preprocessing is complete. Do not prepare another train pilot, redo105GB hashing absent genuine integrity drift, or reopen399 similarity findings. Preserve the accepted outputs/model/config and additive storage bindings.

The remaining OULU preprocessing population is1980 non-train originals/1979 selected frames plus the one existing calibration terminal failure. The next concrete scope should cover the frozen branch-calibration/g_domain image preprocessing only, if permitted by the study's access rules: exact selected frames, same detector/geometry, no scoring/fitting/threshold selection and no target access. Present one execution budget measured from278 and actual remaining media/storage cost, including current retained outputs; no automatic assumption that the existing24GiB/6-hour approval extends to other roles. If applicable approval is missing, request one combined scope for implementation checks, execution and readback, not separate runner/export/import activations.

Retain all failures and fixed denominators; do not choose frames based on detection success. Finish the full selected-image/crop manifest and the applicable active preprocessing configuration pin in that same authorized stage, rather than indefinitely leaving only a pilot configuration as the operational definition. Any frozen configuration transition must be explicit and preserve historical records; no new detector choice or scientific-method search is needed.

## Retained state

OULU dataset/split audit complete;source-train preprocessing2970 complete;other six dataset/split audit fields not_audited. Full4950-video preprocessing is not complete.4950 originals/4949 selected/preexisting terminal failure1;calibration990/989/zero fitted scores;399 similarity outcomes and historical accepted85/disagreement1/unresolved0 unchanged. Global scientific readiness, joined assurance, training/OOF, target evaluation, analysis freeze and locked evaluation remain separate gated stages.
