# 274 - SCRFD acquired; OULU pilot stopped at archive identity guard

Date: 2026-10-22
Parent: `bea81e0f1fe3132d3d74c4b33c1db386967dfad8`

## Decision and actual outcome

[Review273](273-review-doc272-oulu-local-audit-complete.md) is implemented without reopening the completed OULU local audit. The owner approved one combined acquisition/pinning and source-only pilot package: at most32 train-role transactions,30 wall minutes including download,10 GPU minutes,4GiB RSS and512MiB private output. No environment change, model substitution, frame replacement or automatic extension was approved.

**Acquisition succeeded. The existing archive identity guard then rejected the current inputs, before any OULU payload access. No pilot attempt, media decode or detector inference occurred.** This is an input-integrity blocker, not an observed detector/crop failure or an accepted pilot. No receipt-only activation or additional lineage work is requested.

## Actual model acquisition

Downloaded once from [official InsightFace buffalo_l release](https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip), redirected to `release-assets.githubusercontent.com`; extracted only `det_10g.onnx`. Pack288621354 bytes, detector16923827 bytes. SHA256:

```text
pack  80ffe37d8a5940d59a7384c201a2a38d4741f2f3c51eef46ebb28218a7b0ca2f
model 5838f7fe053675b1c7a08b633df49e7af5495cee0493c7dcf6697200b85b5b91
```

ONNX checker passed:4225835 parameters, one640x640 input, nine outputs for strides8/16/32, with score/box/five-landmark widths1/4/10. ONNX Runtime1.22.0 created a single-thread CPU session; no `session.run` was performed. The pin commits to the obtained file, not an independently signed publisher checksum or independent model certification. ZIP member CRC was checked during extraction; no claim of checking every unrelated ZIP member is made.

Acquisition wall time51.78403067588806s. Private package size at blocker recording305549643 bytes, including retained pack/model/receipts, below512MiB. Acquisition peak RSS was not instrumented, so compliance with the4GiB peak cap is **not certified**. No GPU inference ran. The prospective pilot watchdog was not executed and cannot retroactively certify acquisition resources.

## Concrete input blocker

One read-only invocation of the unchanged accepted archive guard raised `archive identity drift from accepted219; separate review required`. A subsequent `lstat` comparison found all three archives differ from219 **only in device**; inode, byte size, mtime_ns and ctime_ns match. All are regular non-symlink files. Exact identities stay private. Matching four stat fields is not proof of current byte identity: no archive bytes were rehashed and the guard was not weakened or bypassed.

The immutable private blocker binds approval, acquisition,273, accepted219 binding, guard source, all three expected/current stat identities and zero pilot counters.4955 frozen parent files (4950 OULU transaction records plus transaction definition/summary, canonical metadata JSON, metadata CSV and role CSV) were hash-verified against272. Existing calibration990/989/zero fitted scores and originals4950/selected4949/failure1 remain intact.

No plan, attempt lock, worker completion, resource receipt, crops or contact sheet exists for this pilot. A blocked preflight is not a failed32-unit execution. The runner now rejects a recorded blocker before reading parents or opening models/media; there is no automatic recovery/retry.

## Prepared code, not real-pilot validation

[Preprocessing helpers](../src/fas/preprocessing.py) implement fixed640x640 SCRFD decoding, score threshold0.5, NMS0.4, deterministic primary-face selection and five-landmark light rotation. The actual prospective shared-crop path expands the aligned bounding box1.30, clips image bounds, preserves RGB and bicubic-resizes to224/518. The separate canonical-square helper is a synthetic geometry probe, not the research shared-crop path. No backbone normalization or PAD execution is claimed.

[Pilot-only config](../configs/preprocessing_pilot_v1.yaml) pins this detector and geometry. [Active preprocessing config](../configs/preprocessing_v2.yaml) remains unchanged with its historical null detector hash; the pilot config does not activate whole-study preprocessing. [Runner](../scripts/preprocess_oulu274.py) contains acquisition and prospective supervised execution. Its worker/watchdog/media/export paths have **not** been end-to-end validated on real OULU or certified production-ready. The fixed selection rule is16 transactions per binary label from train, ordered by SHA256 of `oulu274:` plus video identity, with no outcome filtering or replacement; no real32-unit plan was materialized.

Six [focused synthetic tests](../tests/test_preprocessing.py) cover similarity/dimensions/repeatability, invalid landmarks, context expansion/clipping, SCRFD threshold/NMS/no-face/RGB, balanced order-independent selection without failure replacement, and fail-closed recorded-blocker handling. They use no study media or model inference. Passing these tests is not observed face alignment quality, contact-sheet review, pilot throughput or a full-suite result. The aggregate's publication/CI status is creation-time pending; exact-commit publication evidence is recorded separately, without rewriting successful receipts.

## Resumption and retained state

The next substantive task is **input identity recovery**, not399-pair investigation or another download. Do not simply replace the stored device ID. Recommend one separately authorized package that verifies all three archive bytes against the accepted full hashes, writes a new recovery binding without overwriting219, and only after success executes one freshly budgeted source-only pilot. Recovery needs an explicit byte-I/O/time budget for the approximately105GB archives; it is not covered by this package's30-minute/512MiB pilot permission. The original package must not be extended or silently retried. If byte equality fails, stop on that concrete integrity discrepancy instead.

Both OULU audit statuses remain complete, the other six remain not_audited;399 lineage outcomes remain unknown with no new dispositions. Frozen roles/selectors, grouping, summaries, active configs and validator predicates are unchanged. Joined assurance, full preprocessing, training, OOF/calibration, target/locked evaluation and scientific readiness remain unapproved or blocked as before. This report requests one substantive review of acquired model evidence and the concrete recovery scope, not an acknowledgment/activation cycle.