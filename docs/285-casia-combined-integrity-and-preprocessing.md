# 285 - CASIA-FASD combined release integrity and primary-image preprocessing

Date: 2026-10-23
Governing acceptance: [review284](284-review-msu282-local-audit-and-image-completion.md).

## Authorized scope and current state

One combined600-original package is authorized: code/tests, release and frozen
role/group reconciliation, archive/file integrity, strict decode, one frozen
middle frame/video, unchanged active-v3 face/crop export, full manifest/pixel
readback, bounded actual visual review, applicable local-audit summary updates
and publication. CPU-only;14400 seconds,4GiB sampled group RSS and32GiB combined
historical/new private retained artifacts plus temporary storage. No automatic
retry, cap extension, download, tool installation or extra pilot is authorized.

The four-hour clock conservatively starts at the original review284 request,
2026-10-23T00:22:55Z, before the combined approval and implementation. It is not
reset at inference start. Existing read-only source archives are not newly
created output storage. Previously accepted OULU/MSU packages remain unchanged.

**Blocked: all600 originals produced pre-detector technical failures and zero
selected images. CASIA primary-image preprocessing/local completion is not
accepted; both CASIA audit statuses remain `not_audited`.** A persistent private supervisor/lease,
immutable receipts and an execution log survive a chat disconnection. A
read-only VS Code progress task reports phases/counts every30 seconds.600
written rows alone will not mean that readback, visual inspection, local audit
or publication have passed.

## Actual input and provenance

- One RAR5 container:876296302 bytes;600 AVI payloads:866586586 bytes.
  Largest original video:5052628 bytes.652 visible entries:600 files and52
  directories. Header-only preflight confirms unpacked CRC32 fields on all600.
-50 canonical subjects;150 bona fide and450 attack originals.
- Bob/Idiap reference partitions:240 train and360 test videos,20/30 disjoint
  canonical subjects. Repeated raw train/test subject tokens are not conflated.
- Frozen source roles:360 train,120 branch_calibration,120 g_domain videos;
 30/10/10 subject groups. Both original partitions belong to this source pool.
- The twelve filename codes/subject are the already accepted pinned
  Bob-reference mapping, not new owner-certified release documentation.
  Reference commit: `5320dac3101de913874242f56c5baa5961d2c13b`.
  No controlling native README/protocol or publisher checksum is manufactured.
- Before media execution, duration/FPS/frame counts remained unprobed. No
  original video was opened for a dataset-specific exploratory detector pilot.

Actual frozen metadata-only preflight passed600 IDs, the reference schema,
frozen roles/metadata, archive headers,36 source/config/tool commitments and64
outcome-independent fixed visual indices. Combined retained artifact storage
at that preflight was15708197575 bytes, including the newly written authority.

## CRC defect caught before production

A genuine stored-RAR4 synthetic corruption regression demonstrated that the
available `bsdtar` can return zero with no stderr despite an altered payload.
Utility success therefore does **not** establish file CRC verification.
No real CASIA extraction/decode had started at this point.

The supplied release is RAR5. A bounded stdlib
[RAR5 header reader](../src/fas/rar5.py), grounded in the official
[RAR5 format](https://www.rarlab.com/technote.htm), independently validates
header CRC32, reads unpacked file CRC32 commitments and skips compressed data.
It rejects missing CRCs, unsafe/duplicate paths, split/multivolume containers,
encrypted headers/members, filesystem redirections and invalid/truncated
bounds. Its typed file/size universe must match both the existing extractor
listing and the accepted canonical inventory.

Production then hashes the stable original container, extracts once using the
existing tool, retains strict exit/stderr checks and independently reads every
extracted AVI through EOF for size/CRC32/SHA256. Each later strict probe must
join that SHA/size commitment. The final600-row verifier joins the same CRC,
SHA and size parents. This is a local container baseline plus native CRC
validation, **not** an authenticated publisher checksum.

Tests use real stored-RAR5 fixtures and the actual existing extractor when
available, including deliberate data corruption, missing members and changed
source identity. Pure header/bounds/CRC refusal tests run without that utility.
CI does not silently install a new archive tool to enable the optional
transport-specific regression.

## Unchanged image and failure policy

The [combined runner](../scripts/preprocess_casia285.py) reuses the accepted
SCRFD_10G_KPS weight, active-v3 policy and source-timebase-corrected
[strict replay](../scripts/msu_replay282.py). Every expected native RGB frame
must match before the fixed selected frame is accepted. Exit/stderr/EOF checks
remain strict; decoder warnings are not suppressed.

Primary selection remains `floor((eligible_frame_count-1)/2)` before detector
execution. No detector failure triggers a replacement frame. Pre-detector
technical failures retain their original role/denominator, `not_run/non_accept`
and no image. Detector failures retain the frozen selected RGB and
`failed/non_accept`, with no invented crop or score.

All600 original rows, exact assets, all replay/diagnostic records and frozen
parent joins must pass complete readback. All64 precommitted fixed visual tiles
and every detector-failure tile must actually be opened after software
completion; later visual receipts are additive, not rewrites of creation-time
pending fields. Near/transformed-duplicate independence, joined-domain capture
assurance, all-image human inspection and scientific readiness are not claimed.
No features, training, model/calibration scores or target access are authorized.

## Validation before launch

-27 CASIA tests passed, including genuine extraction/corruption checks,
 600-row readback refusal cases, final resource caps, no-retry supervision and
  owned temporary cleanup.
-62 combined CASIA/replay/image/batch/completion regressions passed in49.170s.
  An earlier combined invocation had a transient failure in the historical
  OULU recovery cap regression; that exact test passed isolated, and the
  complete same62-test sequence then passed. No accepted OULU/MSU code changed.
- Python compilation and normal canonical schema validation passed.
- The production plan pins executed source/config/tool bytes. They are not
  edited while the run is live.

The terminal aggregate receipt, bounded visual findings and any applicable
CASIA-only local-audit status changes will be added to this same report after
actual checks. The actual blocked outcome follows; no automatic retry occurred.
SiW-Mv2 and later model stages remain separate work.

## Terminal outcome: complete accounting, zero usable image exports

The single authorized run has terminated and all producer/watcher work has
finished. The [software terminal receipt](../results/phase1/casia-preprocessing285-v1.json)
records successful execution of its accounting/readback requirements, **not
successful primary-image preprocessing**. Its creation-time
`completion_claimed:true` and visual-pending fields mean that the600-row
software ledger was verified. They are preserved chronologically, not
retrospectively rewritten into image acceptance.

| Check | Actual result |
|---|---:|
| Original IDs / subjects |600 /50 |
| Original archive SHA256 |`03b66ac559cf3e40a228570064a456e85974c15f23507c8e9eeb2e704506eb35` |
| Independently checked video CRC32/size/SHA joins |600 |
| Original AVI payload bytes |866586586 |
| Train / calibration / g_domain originals |360 /120 /120 |
| Retained pre-detector technical failures |600 |
| Selected images / detector successes / detector failures |0 /0 /0 |
| Accepted native-frame sequences / strict selected-frame replays |0 /0 |
| Exported frame/crop assets |0 |
| Per-unit media/attempt/transaction records verified |1800 |
| Exact encoded duplicate groups / forbidden crossings |0 /0 |
| Retained staged original videos after cleanup |0 |

All600 saved media records report `invalid_or_undecodable_media` from the
configured strict `probe_video` path. They retain their original roles and
`not_run/non_accept`, without replacement frames, images, detector inference
or model scores. Partial saved metadata identifies AVI/MPEG4 and contains
FPS/duration, but no validated frame index/sequence.

**The exact underlying probe/metadata/timestamp/decode failure has not been
established.** The accepted shared helper collapses several exception paths to
this generic reason and does not retain its underlying ffprobe/framehash
stdout/stderr as separate diagnostic files. It would be incorrect to assert
that600 physical files are corrupt, that the archive extractor caused the
failures, that a timestamp fix is known to solve them, or that any selected
frame completed strict replay. CRC success proves consistency with the supplied
archive commitments, not multimedia validity or publisher authenticity.

No additional original was reopened to diagnose the cause, no strict check was
relaxed, and no failed original was retried. The staged source copies have been
removed; original archive, immutable media/transaction/attempt records, full
failure-preserving manifest, exact checks and readback remain private.

## Actual visual accounting and blocked local-audit handoff

Actually opened both fixed sheets,32 tiles each. All64 tiles visibly say
`DECODE FAILURE`; **zero face crops were available for visual usability
assessment**. There are no detector-failure sheets because the detector was
never reached. This is inspection of no-image accounting, not crop acceptance.

The additive [visual receipt](../results/phase1/casia-preprocessing285-visual-review-v1.json)
therefore records64 opened placeholders, zero inspected face crops and
`sample_crop_usability_check_pass:false`. The additive
[local assessment](../results/phase1/casia-local-audit285-v1.json) explicitly
records `blocked_no_selected_images`, `local_audit_complete:false` and
`primary_image_preprocessing_complete:false`.

Release/reference/frozen-role/subject/integrity subchecks and the600-row ledger
passed, but these do not justify promoting CASIA's combined milestone when no
image was exported. Neither summary CSV was modified. Normal external
frozen-root `data-audit` validation still returns exactly four errors:
CASIA-FASD and SiW-Mv2 remain unaudited in both dataset/split summaries. OULU/MSU
acceptances, frozen hashes, roles, model and active-v3 policy remain unchanged.
Scientific readiness remains false.

Resources:

- Conservative combined clock to software terminal:1578.127894 seconds
  (26m18.128s), including implementation/tests before launch.
- Supervised worker/readback:235.544271 seconds (3m55.544s).
- Sampled RSS peak:265527296 bytes, below4GiB.
- Sampled combined historical/new retained artifacts plus staged media:
 16576978904 bytes, below32GiB. These are sampled, not continuous hardware
  maxima.
- One production attempt; zero automatic retries; GPU/model/calibration scores0.

Further original-media diagnosis and any recovery need explicit additional
authority because this approval forbids retry. A bounded next scope would
capture the exact failing strict-probe command/metadata on a single committed
failed original, reproduce and test any narrowly demonstrated fix, preserve
these records and only then undertake an additionally authorized recovery.
No decoder/metadata check may be silently suppressed to obtain600 image rows.
