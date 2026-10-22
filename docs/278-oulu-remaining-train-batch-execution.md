# 278 - OULU remaining source-train batch execution

Date: 2026-10-22
Implements: [Review277](277-review-doc276-recovery-and-preprocessing-pilot.md)
Parent: `1130ee7`

## Status at this report

**Execution launched, not completed.** The persistent supervisor has started the
additional approved remount recovery. No new train outputs, final detector
counts, crop-quality conclusion or completed train milestone is claimed here.
The authoritative live state and terminal receipts are on disk, not dependent
on the chat transcript. A final public aggregate is written automatically when
the package exits; it must be read before making any completion claim.

Publication snapshot: the live supervisor was confirmed running. The latest
observed recovery log reports23622382472 bytes read from the first archive at
280.998 recovery wall seconds. No whole-archive hash result had been recorded,
the batch plan was not yet committed, and new train transaction outputs were0.
This is an in-progress observation, not a successful recovery or batch result.
The20-test result below validates synthetic software behavior, not those still
pending real-media outcomes.

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

Visual coverage is fixed before outcomes, stratified by label and the first
two frozen filename components, supplemented by every100th manifest position.
All failed detections get additional source-frame sheets. These label-free
sheets are reconstructed and saved for actual inspection; producing sheets
alone never claims they were opened. A software-success aggregate explicitly
remains `software_complete_visual_review_pending` until a separate inspection
receipt reports what was actually viewed.

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
If software succeeds, open the fixed sheets and every failure sheet, record
actual observations separately, and update this report with measured outcomes.
Do not infer human visual review, detector accuracy, or all-success from exit0.

## Unchanged scientific scope

OULU dataset/split audit remains complete; the other six fields stay not_audited.
The399 similarity findings,4950 originals/4949 selected/one preexisting terminal
failure, calibration990/989/zero fitted scores and all frozen role/selection
boundaries remain unchanged. No global preprocessing_v2 activation, calibration,
g_domain/target processing, training, OOF or scientific-readiness promotion is
included. Train-only completion is not full4950-video preprocessing completion.
