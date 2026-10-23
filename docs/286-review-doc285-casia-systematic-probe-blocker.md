# 286 - Review of285: CASIA zero-image systematic probe blocker

Date: 2026-10-23
Reviewed commit: `c69d54214b7a284f5d1f580193e2fc4108d707bf`

## Decision

**Accept285's release-integrity/accounting evidence as a bounded blocked-run report. Reject CASIA primary-image or local-audit completion:600 originals yielded zero selected images. Require one concrete probe diagnosis/correction/recovery package rather than accepting600 generic failures as an adequate dataset result.** Keep CASIA statuses not_audited. Previously accepted datasets remain complete.

All600 entries failing at the same helper with no detector execution is a strong systemic compatibility/validation signal, not proof of600 damaged files. No actual root cause has been captured. The next useful action is to identify the exact failing stage on a fixed original, not change detector, retry all600 blindly or restart provenance research.

## Verification

Read the full report, aggregates, producer, RAR5 reader and test definitions. Public counts reconcile600 originals/600 pre-detector failures/zero images, zero strict replays/inferences and zero accepted native sequences. The local assessment explicitly blocks completion and the visual receipt reports placeholders, not usable crops. CRC/size/SHA joins support consistency with supplied archive contents, not multimedia validity or publisher authentication.

Exact-commit GitHub checks/job HTML confirms [run39880703819](https://github.com/lathevinh/fas/actions/runs/39880703819), [validate120177125085](https://github.com/lathevinh/fas/actions/runs/39880703819/job/120177125085), head `c69d54214b7a284f5d1f580193e2fc4108d707bf`: all12 listed steps have success conclusions including Complete job. CI validates software tests, not real CASIA decoding or successful preprocessing. The real-source compatibility gap survives green synthetic tests.

Private archive/extracted bytes,600 per-unit records, approvals, raw execution logs and placeholder images are unavailable for independent readback. Integrity/resource and image-opening observations remain bounded reported evidence. I have not viewed the private sheets or decoded a CASIA payload. The local assessment's checker_sha256 names a checker not identified as a public file; it must not be equated with the current published runner hash. Carry its actual source identity in the next ordinary recovery handoff if relied upon; no standalone provenance checkpoint is needed.

## Established software limitation; actual cause still unknown

The shared `fas.media.probe_video` catches multiple metadata/timestamp/framehash errors and emits only `invalid_or_undecodable_media`. The producer binds that generic result and proceeds through all600 entries. It does not save the stage, original exception or ffprobe/framehash stderr. That design makes a systematic software failure indistinguishable from invalid files in the final600 rows.

Independently executed the actual helper AST with a controlled successful ffprobe response containing valid codec/FPS/duration but a missing per-frame timestamp. It produces the same generic invalid-media reason. This reproduces the loss of diagnostic specificity; it is an illustrative synthetic case, **not** the actual CASIA diagnosis. The partial codec/FPS/duration in the report narrows where processing reached but cannot choose among timestamp, frame-count, framehash, schema or decode failures.

The previous rawvideo timebase correction does not automatically fix the initial framehash/metadata probe. It is only reached after successful selection. Do not assume the same timestamp issue, apply flags blindly, suppress stderr or relax frame-count checks. Capture actual outputs and demonstrate the specific fix first. Similarly, the reported extractor CRC regression justifies independent payload CRC checks; it does not establish extraction caused these probe failures.

## Completion semantics

The machine completion_claimed=true currently means the600-row accounting/verifier finished. That interpretation is defensible only alongside the explicit blocked local assessment; it is not dataset preprocessing success. Future recovery receipts should expose accounting_complete and primary_image_preprocessing_complete separately, plus selected/success/failure counts, so a zero-image batch cannot appear green to a downstream summary-only consumer. Preserve the original immutable receipt; add the corrected interpretation rather than rewriting history.

Opening64 DECODE FAILURE placeholders is accounting inspection, not crop quality acceptance. Do not spend another review opening the same placeholders. Retaining every original, no substitute frames and unchanged audit summaries is correct. Zero selected images makes successful dataset acceptance impossible for this run regardless of correct accounting.

## One actionable recovery package

Recommend one additional combined authorization, if the original no-retry scope has ended: diagnosis, narrow implementation fix, meaningful tests, one600-original recovery, final readback and actual crop review. Proposed combined ceiling:2 wall hours including diagnosis/tests/execution,4GiB process-group RSS,32GiB total retained/temporary artifacts, CPU only, no new model/tool installation, no automatic retry/cap increase. Use measured original866586586 payload bytes and the same small archive; do not introduce an unbounded benchmark task. These are proposed limits, not current execution authority or measured recovery throughput.

1. Choose a fixed failed original from the saved plan, record its original archive path/CRC/size/SHA, and extract it under existing safe transport checks. Capture the exact ffprobe JSON/stderr/exit and FFmpeg framehash stdout/stderr/exit, command/version and the first failing exception/stage. Bound diagnostic output. Do not decode all600 again just to learn that the generic error repeats.
2. Correct only the demonstrated metadata/probe/output-transport defect. Preserve strict input/CRC/RGB/EOF/exit/stderr and the one-middle-frame-before-detection rule. If input timestamps genuinely violate a mandatory constraint, report that fact instead of inventing timestamps. Add a regression reproducing the actual failure and prove the correction on the same original. Include fixed format/quality representatives in that package if the demonstrated issue requires them; no separate pilot approvals or favorable replacement.
3. If validated, execute one additive600-original recovery with retained failed285 evidence, unchanged source IDs/roles/labels, detector/config and denominators. No image from285 is reusable because none exists. Reuse accepted source integrity commitments only with appropriate current identity/CRC guards; no gratuitous full rehash merely for publication.
4. Save durable stage-specific failures for every remaining non-accept. If the same newly identified systemic failure persists across a small predeclared consecutive set, stop the recovery and report that concrete defect rather than silently processing the whole release into another generic zero-image ledger. Retain all not-run rows. Genuine isolated media failures remain explicit technical non-accept, not hidden exclusions.
5. Finish full600-row/frame/crop readback and actual bounded face-crop inspection. Report both technical accounting and image milestone outcome. Update CASIA summary fields only when mandatory local checks support acceptance; deliver these together without runner/export/receipt/import/activation approval chains.

If the single diagnostic original cannot establish a correction within the combined budget, preserve the exact failure evidence and stop that recovery scope. That is a specific technical result, not an invitation to another detector or forensic project. No other dataset or accepted output needs reprocessing.

## Retained state

CASIA release/group/integrity subchecks and600-row accounting reported complete;primary-image preprocessing and local audit blocked;600 technical failures do not establish600 corrupt files. OULU/MSU accepted audit and primary-image milestones remain unchanged. One frame at the fixed middle remains the owner's accepted current policy. Active detector/config, roles and original denominators unchanged. No scores, fits, training, target access or global scientific-readiness promotion.
