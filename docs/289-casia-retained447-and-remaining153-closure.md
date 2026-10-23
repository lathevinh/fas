# 289 - CASIA retained447 plus remaining153 closure

Date: 2026-10-23
Governing review: [288](288-review-doc287-casia-recovery-and-partial-progress.md).

## Status

**CASIA local release/subject/integrity audit and primary-image preprocessing
are complete.** The600-original reconciliation, full saved-evidence/image
readback, actual three-sheet crop review and CASIA-only summary promotion
passed. There are594 detector successes, six retained detector failures and
zero pre-detector failures. No original is removed or assigned a replacement
frame. The original447 transactions were reused without source decoding or
detector inference;153 distinct remaining originals were newly processed.
OULU/MSU acceptances and frozen roles/labels are unchanged. SiW-Mv2 and later
scientific stages remain blocked.

The [software terminal](../results/phase1/casia-preprocessing289-resume-v1.json),
[actual visual review](../results/phase1/casia-preprocessing289-visual-review-v1.json),
[local audit](../results/phase1/casia-local-audit289-v1.json) and
[same-clock handoff receipt](../results/phase1/casia-native-ipc-handoff289-v1.json)
record separate creation-time stages. In particular, the earlier software
terminal correctly retains its then-false visual/local-completion flags.

## Prepared correction and measured envelope

The old synchronous current-tree walk was removed from foreground accounting.
The [budget implementation](../scripts/casia_budget289.py) uses full asynchronous
storage snapshots and a single-producer monotone write-reservation journal:

- Reserve before writing. A snapshot records only the completed reservation
  prefix observed **before its scan starts**. Every later or still-active write
  remains charged until a later scan can include it. Nested writes cannot
  prematurely release an outer reservation.
- Count all accepted historical outputs, failed/partial packages, current
  outputs, temporary/open-deleted files and native control files. A256MiB
  conservative control/log allowance is added; actual reservation peaks can
  exceed physical disk bytes without relaxing the cap.
- Capture subprocesses have hard16MiB per-file OS limits; their existing
  stdout/stderr/exit checks remain. Original FFmpeg/ffprobe arguments execute
  unchanged through the existing Python interpreter's file-limit transport.
  Replay's RGB pipe is not converted to a file or timestamp-adjusted.
- PNG reservations use a generous bound on the actual RGB uint8 array.
  Selective extraction reserves a conservative archive-payload upper bound.
  JSON, copies, raw diagnostics and final sheet/manifest generation are covered.
- Full scans wait30 seconds after completing, rather than continually
  competing with decoding. Snapshot age over90 seconds, bad bindings, invalid
  credits and scanner errors are fatal. No cached-success fallback is used.
- The scanner is an isolated process, not a thread joined through a long
  traversal during shutdown. Process-group termination is bounded and tested.

The [actual-filesystem synthetic preflight](../results/phase1/casia-observer289-preflight-v1.json)
populated600 directories/15000 files, added40 growth files, and sampled200
foreground measurements while a complete scan ran. Full scan:5.010609 seconds;
foreground median2.765ms, p95=5.310ms, maximum8.773ms. Required thresholds were
p95 below50ms and maximum below250ms. Growth was conservatively accounted for.
This was metadata-only synthetic evidence, not private CASIA throughput.

Before private execution,28 focused tests passed, including actual synthetic
AVI/B-frame probe/replay/PNG/readback under the new transport; exact153-of600
RAR extraction with the existing utility; prefix/no-repeat/systemic-stop
guards; reservation races; scanner errors/staleness; and bounded shutdown.
The accepted native parser/proof was unchanged; no new private normal/low/high
proof campaign or detector pilot was performed.

The planning envelope was15 minutes for retained verification/reuse,51 minutes
for153 remaining originals at20 seconds each,30 minutes for full readback,
actual visual/local closure and publication, and10 minutes shutdown:106 minutes,
plus14 minutes margin. The20-second assumption exceeds twice the previous
continuation's roughly8.96-second average. This supported a bounded proposal,
not a guarantee of successful private execution.

## Fresh authority and preserved evidence

The owner selected `approve_combined_casia289`. The new immutable clock starts
2026-10-23 11:20:17.405225 UTC+7 and ends13:20:17.405225 UTC+7.
Limits:7200 seconds, CPU only,4GiB group RSS and32GiB combined historical/new
retained/temporary artifacts. No tool/model installation, automatic retry or
extension. Work subprocesses stop by13:10:17, preserving ten minutes before the
final ceiling for bounded shutdown/closure.

The [initial controller](../scripts/resume_casia289.py) verified the447 retained
transaction/media/config/model/replay bindings, all1770 image assets and their
pending pixel readback. Immutable records/raw evidence/images were copied and
hash-checked; the originals were not rewritten. The interrupted original's
evidence was quarantined. The original600 CRC commitments remain bound by
current archive identity and re-read typed/header-CRC guards.

Exactly153 archive members were then selectively staged, each independently
checked for size/CRC32/SHA against those commitments. The whole600-video
extraction/processing workflow was not repeated. No archive rehash was added.

## Concrete IPC failure and explicitly approved manual handoff

The [first newly approved supervisor](../results/phase1/casia-preprocessing289-observer-stop-v1.json)
stopped after277.363476 package seconds
(224.271288 supervised seconds), having committed17 additional transactions.
It failed closed on `FileNotFoundError` opening its write journal. The file
existed again when inspected after the stop. This was an observer/control
transport failure, not a media diagnosis or permission to restart everything.

A bounded [synthetic concurrent-publication probe](../results/phase1/casia-observer289-ipc-reproduction-v1.json)
reproduced the filesystem
problem using the same atomic-replace helper:200 publications on the actual
v9fs workspace produced344 successful reads and960 missing-file reads.
The same probe on native Linux storage produced28528 successful reads and
zero missing/partial-JSON reads. No source video or image was involved.
The populated-tree latency preflight had not stressed concurrent control-file
replacement and therefore had not exposed this publication-visibility defect.

An attempted VS Code progress-task creation blocked the caller for roughly
70 minutes before returning, delaying discovery of the first stop. This idle
gap remained inside the original fresh clock; it was not subtracted from
elapsed time. The continuation used a direct read-only30-second shell watcher
instead of another UI task call.

The owner explicitly approved `approve_native_ipc_handoff289_same_deadline`:
preserve464 committed transactions (458 detector successes and6 failures),
move only active journal/snapshot IPC to native Linux storage, and process only
the136 still-uncommitted originals. The original13:20:17 deadline and all caps
remain unchanged. There was no automatic retry or new two-hour clock.

The [handoff controller](../scripts/finish_casia289.py) preserves the first
failed terminal, ledger and lease, quarantines uncommitted artifacts and seals
the464 transaction hashes. It verifies all retained bindings, the original447
readback commitments and the additional17 pixel/replay evidence without source
decoding or detector inference. Native control storage is included in the
accounted root set and the same reservation protocol; missing/stale/error
handling remains fatal.

Only136 members are restaged after the failed supervisor's cleanup. Thus153
distinct originals require new processing, while the136 pending source files
are extracted a second time for this explicitly authorized continuation.
Neither the original447 nor the17 newly committed originals is reprocessed.
Twenty focused handoff/budget/resume tests passed before this continuation,
including real136-only synthetic RAR staging and concurrent native IPC.
These test selections overlap; they are not added into a unique total.

## Full closure and audit boundary

The final verifier reconciled all600 original rows and native CRC/SHA
parents; reparsed saved native timestamps/count/framehash evidence; verified
selected-frame identity, strict replay receipts, every selected/crop PNG and
pixel identity; and accounted for all detector/technical failures and originals.
The metadata-only native-count JSON is validated as count evidence, not
mistaken for a subprocess receipt with stdout/stderr fields. A targeted
regression checks that its hash cannot be changed or silently ignored.

Both predetermined fixed sheets and the complete detector-failure sheet were
actually opened:70 viewed tiles =63 face crops +7 selected-failure tiles +
zero placeholders. One failure original appears in both the fixed sample and
failure sheet; there are six distinct detector-failure originals, not seven.
Successful samples contain upright, centered facial regions with eyes, nose
and mouth retained. Source blur/exposure differences, glasses reflections and
presentation-media borders remain visible. Failure images also contain real
facial content; dark exposure/reflections are observations, not proven failure
causes. The bounded crop-usability check passed. This does not claim that
all600 images were manually inspected.

The [completion checker](../scripts/complete_casia289.py) and
[additional handoff gates](../scripts/complete_finish289.py) required successful
full software/readback/resources and actual crop usability before the CASIA-only
summary promotion. The normal external-frozen-root validator moved from
the four CASIA/SiW audit-status errors to exactly the two remaining SiW errors.
All other summary fields/frozen hashes and OULU/MSU statuses are unchanged.
Classifier scores/fits, target access and global scientific readiness stay false.

The actual historical285 private checker is identified separately from these
public current checkers: basename `record_casia285_visual_review.py`, SHA256
`7555cd9d030488c71d988d0d4bfd56e6d81ed46d775c83a3f1ba160d645e8988`.
Its source identity is checked if carried into local handoff evidence; it is
not used as the current recovery acceptance gate or equated with a new runner.

## Final reconciliation, resources and validation

| Item | Verified result |
|---|---:|
| Original videos / subjects |600 /50|
| Bona fide / attack originals |150 /450|
| Frozen train / calibration / g_domain originals |360 /120 /120|
| Frozen role subjects |30 /10 /10|
| Selected original frames / strict replay receipts |600 /600|
| Detector successes / failures / pre-detector failures |594 /6 /0|
| Referenced and pixel-validated image assets |2382|
| Native RGB frames in saved strict-decode evidence |111029|
| Explicitly parsed non-coded MPEG4 VOPs |137|
| Exact native sequence duplicate groups / forbidden crossings |0 /0|
| Newly processed originals after retained447 |153|
| New successes before / after manual handoff |17 /136|

The2382 assets are594 successful sets of four images plus six retained
selected failure images. No failed detector receives invented crops or becomes
an accepted detector result. All600 saved timestamp evidence records use the
accepted native-packet-DTS-guarded transport. This is evidence readback, not a
new decoding campaign for the retained originals. Native integrity joins cover
600 payloads /866586586 bytes; the archive was not rehashed. Official release
subjects remain20 train /30 test; frozen roles are a separate unchanged overlay.
No subject boundary crossing was found. Zero exact duplicates does not certify
near-duplicate independence or transformed/joined ancestry.

Software reconciliation completed at12:52:09.884674 UTC+7,5512.479448 seconds
(91m52.48s) after the fresh approval. Actual visual/local closure completed
at12:57:27.716438,5830.311212 seconds (97m10.31s) after approval, before the
unchanged13:20:17.405225 deadline. Both figures include the earlier stop and
long idle/UI delay; neither resets the clock at the manual handoff.

The first stop and successful continuation receipts report maximum sampled
RSS543854592 bytes (518.66MiB) and conservative accounted storage21702982075
bytes (20.21GiB), below4GiB/32GiB. Storage includes historical/partial/current
outputs, native controls and reservations; it is not a claim that physical
files alone occupied that many bytes. The terminal temporary-bytes field is
zero, and closure separately verified the owned staging directory was empty.
Supervisor, worker, scanner and read-only watcher have stopped; no289 process
is left running. There were no GPU use, classifier scores/fits, target access,
new tools/models or automatic retry.

After summary promotion, one combined targeted run passed **76 tests** in
106.038 seconds across budget/resume/handoff/local-completion and
manifest/preregistration modules. Canonical schema validation passed. Earlier
28- and20-test selections overlap this run and are not added to its count.
Public exact-commit CI remains a separate publication check; software CI is
not independent private-media replay or visual adjudication.

## Reproducibility limits

Original media, individual source identities/paths, raw approvals, private
per-unit records and images are not published. Public source, aggregate
receipts and hashes provide bounded reported evidence. CI verifies software,
not an independent private-media replay or visual adjudication.
Earlier287 and initial289 failure receipts remain historical evidence; they
must not be rewritten into a successful chronology.
