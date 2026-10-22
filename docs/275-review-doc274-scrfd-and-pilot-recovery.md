# 275 - Review of274: acquired SCRFD and blocked pilot

Date: 2026-10-22
Reviewed commit: `cc77a5bfd8cd20a54ddbbf053732d640325e323a`

## Decision

**Accept274 as an acquisition/preflight-blocker report, not a completed or failed detector pilot. Keep OULU local audit complete. Require the supervisor correction below before real pilot execution.** The acquired detector should be reused; no second download, model switch,399-pair investigation or manual similarity review is requested.

Reported device-only archive identity drift is a concrete storage-binding problem, not evidence of detector failure or new lineage leakage. Matching inode/size/timestamps suggests an environment/mount change but does not prove unchanged bytes. Do not silently replace the device field or claim corruption without evidence. Resolve the binding once, then proceed to preprocessing within one package.

## Evidence checked

Read the full report/aggregate, new helper/config/runner and six tests. Weight pin and input/output schema are concrete reported acquisition evidence; no inference is claimed. Active preprocessing_v2 remains unchanged; the pilot config is scoped separately. The shared-context path, not the canonical-square probe, is used for pilot crops. Primary selection is balanced16/16 and independent of detector outcomes; frozen frames must not be replaced on failure.

Private download/model,4955 parent readbacks, original approval and archive-stat receipts are unavailable for independent readback here. The reported model hash binds the acquired file, not a signed publisher checksum. ONNX validation/session construction is not detector inference or observed crop quality. Acquisition peak RSS was uninstrumented; the stated4GiB cap is not retrospectively certified. This missing measurement is a disclosed limitation, not a reason to download the same model again.

Exact-commit GitHub checks/job HTML confirms [run39701963062](https://github.com/lathevinh/fas/actions/runs/39701963062), [validate119573063061](https://github.com/lathevinh/fas/actions/runs/39701963062/job/119573063061), head `cc77a5bfd8cd20a54ddbbf053732d640325e323a`: all12 listed steps have success conclusions including Complete job. No exact API completion timestamp is asserted. CI does not validate private acquisition or an unexecuted pilot.

## Required implementation correction: worker exit is not pilot acceptance

`supervise` currently sets `completion_claimed` from `code == 0` and publishes resources without validating `worker_completion.json`, the exact32 transaction rows, selected parents, crop assets or final readback/caps. Independently executed the actual supervisor function AST with stubbed process/clock/authority boundaries: a worker returning0 with no worker-completion record and no transaction assets produced `completion_claimed: true`. No model or study media was involved. This is a reproducible producer defect, not a claim that274's blocked attempt emitted false success.

Before pilot execution, require exact completion and readback:32 unique planned transactions, expected role/class/frame/media/model/config joins, explicit detector success/failure per row, no replacement, all success PNG/hash/shape joins and fixed geometry, plus correct failed-row/non-accept accounting. Materialize affected partial rows on failure; no denominator loss. Validate the completion record against those rows, then apply final deadline/output/RSS accounting before publishing consistent authoritative summary/resources. Missing completion, partial rows, corrupt crops or final-cap failure must not pass on worker0. Add focused regressions for these paths, alongside one complete-success control.

This is a bounded software correction already relevant to the requested pilot, not a scientific redesign or separate approval gate. The existing six synthetic tests do not exercise this supervisor acceptance path. Reuse the final-readback pattern from257/261 rather than recreate the old zero-exit shortcut. No real crop-quality acceptance should be claimed before actual source-only sheet inspection.

## Concrete recovery plus pilot package

Recommend one explicit combined scope where existing authority does not cover the extra I/O: one read-only full-byte recovery of the three accepted archives, additive new identity binding, the supervisor repair/tests, and one fresh32-transaction pilot. The old30-minute package has ended and cannot be silently stretched to cover archive recovery. Do not ask separately for a hash receipt, binding activation, runner, export and pilot import.

Proposed recovery ceiling: at most120 wall minutes; one sequential pass over exactly the sum of the three accepted archive byte sizes;1GiB process RSS;16MiB new recovery records; no archive copies, mutation, extraction or model work during hashing. Stream through stable open regular-file descriptors and check descriptor/path identity before and after each hash. Compare every digest and exact byte count with the accepted full hashes. Preserve219 and274 and write an additive recovery binding only on equality. Timeout/change/mismatch stops with a concrete report, without automatic retry or cap increase. These are proposed resource limits, not measured throughput or current execution authorization.

On successful recovery, execute one newly bound pilot using the already acquired detector, unchanged source-only selection/geometry and the original pilot ceilings:32 transactions,30 wall minutes,10 GPU minutes maximum,4GiB RSS,512MiB private package output including retained pack/model. CPU execution is proposed by274 and must be reported as such. Give recovery and pilot separate measured durations inside the single package; no double counting or false claim that105GB hashing fit the old30-minute budget. A fresh explicit approval must cover any new attempt not already authorized. Routine implementation/tests and preparation of this concrete scope need no separate permission.

If trusted environment evidence can prove the storage mapping transition without a full hash, present that specific alternative evidence and its limits together; do not automatically waive the existing guard or invent a universal rehash requirement for every future mount. The full-byte option above is a concrete sufficient route available for this event. Do not repeat it just to publish another report after successful recovery.

Pilot outcome must report actual processed/success/failure counts, selected-frame integrity, crop geometry, timings/storage, and actual sheet inspection. A pass enables a measured proposal for remaining preprocessing; a failure identifies the concrete input/implementation defect. No reopened OULU data audit or renewed similarity research follows automatically.

## Retained state

Model acquisition reported complete;pilot attempts0, payload accesses0, decodes0, inferences0, crop inspections0. OULU dataset/split audit statuses remain complete;other six remain not_audited.399 similarity outcomes retain their existing unknown meanings and do not become pilot prerequisites.4950 originals/4949 selected/failure1;calibration990/989/zero score-fit;accepted85 and historical disagreement1/unresolved0 preserved. Global readiness, full preprocessing, training/OOF, target work, freeze and locked evaluation remain separate gated stages.
