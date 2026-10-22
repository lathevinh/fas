# 278 - OULU remaining source-train batch execution

Date: 2026-10-22
Implements: [Review277](277-review-doc276-recovery-and-preprocessing-pilot.md)
Parent: `1130ee7`

## Final status

**Source-train preprocessing completed and the fixed visual sample was actually
inspected.** One recovery and one new2938-transaction batch completed without
retry. All2938 new detections succeeded; the combined immutable ledger contains
exactly2970 unique train IDs, including the32 reused pilot outputs, with2970
successes and zero detector failures. The supervised final readback passed and
the process exited0. This is train-only completion, not global preprocessing
activation or scientific readiness.

The [machine aggregate](../results/phase1/oulu-preprocessing278-train-v1.json)
records software completion. Its creation-time visual-pending flags remain
unchanged; the later
[additive visual receipt](../results/phase1/oulu-preprocessing278-visual-review-v1.json)
records actual inspection of all three fixed sheets/65 tiles.

Historical launch-publication snapshot: the supervisor was running. The latest
observed recovery log reports23622382472 bytes read from the first archive at
280.998 recovery wall seconds. No whole-archive hash result had been recorded,
the batch plan was not yet committed, and new train transaction outputs were0.
This is an in-progress observation, not a successful recovery or batch result.
The20-test result below validates synthetic software behavior, not those still
then-pending real-media outcomes. This snapshot is superseded by the measured
terminal outcome above, not reinterpreted as an earlier completion.

## Measured execution and readback

Recovery read exactly105116817408 bytes once in1245.470591098 seconds
(20m45.471s). All three SHA256 hashes matched the accepted anchors. Recovery
high-water RSS was79151104 bytes, below1GiB; the new additive binding was
published without changing276/219.

The batch-authority clock, including batch preflight and final readback, was
8264.376972436905 seconds (2h17m44.377s), below6 hours. The supervised
worker/readback portion was7411.584910224001 seconds. Measured process-group
RSS peaked at676708352 bytes (about645MiB), below4GiB. Peak declared total
retained output was9367325346 bytes (about9.37GB), below24GiB and including
the retained274/276 packages/model pack, new outputs, temporary payloads and
accounting. GPU time was0; there was no download, environment change, cap
extension or retry.

The new batch strictly verified392548 native frames while extracting only the
2938 frozen selected frames. Cumulative selected-video payload was61897964372
bytes; this is sequential input I/O, not concurrent retained output. No frame
was substituted. The verifier checked all new selected-frame assets and8814
success crop assets, reconstructed context geometry from frozen RGB pixels,
verified exact shared/224/518 hashes and bicubic joins, and rejected no rows.
The32 pilot results were reused with exact parent/model/config/output joins.
The2970-ID combined ledger and its record commitments were checked before
software acceptance.

After process completion, the published commitments for all private terminal
records were checked again. The combined ledger was read back as2970 unique
IDs with exactly32 reused rows. Resource thresholds and the three visual-sheet
SHA256 commitments were checked before recording visual inspection.

All three actual fixed label-free sheets were opened:32+32+1=65 tiles. Each
shows a framed face with eye/nose/mouth regions present; no blank or
background-only crop was observed. Pose, glasses, blur, illumination, closed
eyes and presentation appearance remain visible. Zero detector failures means
no additional failure sheets were expected. This is the executing assistant's
sample-based crop-usability check, not an independent human rating, inspection
of all2970 images, detector-accuracy estimate or PAD validation. The private
visual receipt is immutable and additive; it does not rewrite the original
machine pending flags.

## Owner decisions and actual preflight

The owner approved code generalization, tests, one remaining2938-frame batch,
readback and visual review: CPU only, at most6 hours and4GiB process-group RSS.
The24GiB storage limit is **total retained storage**, including the new package,
both274/276 packages, retained model pack/weight, selected frames, crops,
temporary payloads, manifests, logs and final records. There is no automatic
retry, frame replacement or cap extension.

Before starting, the recovered276 guard rejected the current archive identities.
Read-only metadata comparison established that all three archives differ only
in `device`; inode, byte size, mtime and ctime match276, each remains a regular
non-symlink file, and the three accepted recovery-row commitments match. This
is consistent with a WSL remount after the interrupted connection; it does not
establish corruption or unchanged content by itself. The guard was not bypassed.

The owner then explicitly approved one additional sequential recovery over
exactly105116817408 bytes, at most120 minutes,1GiB recovery-process RSS and16MiB
recovery records. Only exact equality with the existing three SHA256 anchors
permits the train batch. A new immutable binding extends276; neither276 nor219
is rewritten. The recovery has its own absolute deadline; the6-hour batch clock
starts only after successful recovery and includes batch preflight and readback.
Any further real identity drift stops the affected work.

## Implementation and validation

[Runner](../scripts/preprocess_oulu278.py) leaves the accepted hardcoded pilot
producer unchanged. It joins the frozen4950 transaction records to their frozen
roles, requires exactly2970 train transactions, and subtracts the exact32 pilot
transactions by complete parent/frame equality. The remaining2938 IDs are
fixed before detector outcomes; failed frames cannot be replaced.

The acquired SCRFD weight and preprocessing-pilot configuration remain pinned.
Strict selected-video payload hashes and full native-frame RGB commitments are
checked before inference on each frozen selected frame. Incremental immutable
attempt/result records preserve explicit success or terminal detector failure.
Expected detection/geometry failures remain `non_accept`; unexpected exceptions
stop the batch rather than dropping units.

A separately supervised verifier checks the exact new record/asset sets, frame
pixels, shared1.30 context geometry, all shared/224/518 PNG and RGB commitments,
bicubic branch joins and completion counts. Accepted32 outputs are read back
and reused without new inference. A combined2970-ID ledger retains both reused
and newly processed results. Interrupted/rejected attempts receive a separate
denominator-preserving failure ledger. Final record joins, deadline, storage
and RSS checks precede software acceptance.

Visual coverage was fixed before outcomes, stratified by label and the first
two frozen filename components, supplemented by every100th manifest position.
All failed detections get additional source-frame sheets. These label-free
sheets were reconstructed and saved for actual inspection; producing sheets
alone did not claim they were opened. The software-success aggregate retains
its creation-time `software_complete_visual_review_pending` status. The later
additive receipt now records what was actually opened.

[Additional recovery](../scripts/recover_oulu278.py) checks non-device identities,
stable regular-file descriptors and paths before/after reads, exact archive byte
counts/hashes, authority/code commitments and additive binding readback. It does
not replay old forensic image folders or download anything.

Final focused validation before launch:

```sh
python -m unittest discover -s tests -p 'test_preprocessing*.py' -q
```

20 tests passed in4.310s in the existing `fas` environment, covering the original
pilot and [new batch/recovery regressions](../tests/test_preprocessing_batch.py).
Tests use synthetic images/archives, not study media or an executable model.
Python compilation and whitespace checks also passed. VS Code test discovery
did not find these unittest files, so the existing CLI runner was used.

## Recovering live state after another lost chat

From the existing `fas` environment at the repository root:

```sh
python scripts/preprocess_oulu278.py --status
```

This is read-only. **Do not rerun `--run-approved`**: the package and immutable
locks deliberately prohibit an automatic second attempt.

The private `oulu_preprocessing278_v1` package contains:

- `owner_approval.json`: both owner decisions and exact resource scopes.
- `supervisor.json`: persistent PID, start time and runner commitment.
- `execution.log`: incremental recovery, worker and readback progress.
- `recovery/attempt.json`, per-archive records and successful `binding.json`.
- `batch_authority.json`: the batch clock, created only after recovery equality.
- `plan.json`, per-unit `attempts/` and `transactions/`, frames and crops.
- On batch completion: `combined_ledger.json`, `readback.json`, visual sheets,
  and `resources.json`.
- On rejection: explicit failure records; no automatic retry.

The terminal public aggregate is
`results/phase1/oulu-preprocessing278-train-v1.json`. It contains only scope,
counts, resource measurements and private-record commitments, not media or row
identities. Absence of that aggregate means no terminal outcome is published.
For this completed run, both aggregates and the private visual-review receipt
now exist. The terminal process and the30-second read-only progress monitor
have stopped. Do not infer independent human review or detector accuracy from
exit0 or from the65-tile assistant inspection.

## Unchanged scientific scope

OULU dataset/split audit remains complete; the other six fields stay not_audited.
The399 similarity findings,4950 originals/4949 selected/one preexisting terminal
failure, calibration990/989/zero fitted scores and all frozen role/selection
boundaries remain unchanged. No global preprocessing_v2 activation, calibration,
g_domain/target processing, training, OOF or scientific-readiness promotion is
included. Train-only completion is not full4950-video preprocessing completion.
The remaining non-train population is1980 originals/1979 selected frames,
including the unchanged one calibration terminal failure. No execution of that
remaining population is commissioned by this report.
