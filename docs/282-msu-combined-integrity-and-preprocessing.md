# 282 - MSU-MFSD combined release integrity and primary-image preprocessing

Date: 2026-10-22
Governing reviews: [281](281-review-doc280-oulu-image-preprocessing-complete.md)
and [283](283-review-doc282-msu-recovery-in-progress.md).
Base commit: `0e07beb`.

## Final result: local MSU audit and primary-image preprocessing complete

The one additionally authorized recovery finished successfully. Its worker,
strict-replay verifier, full280-row output verifier and final supervisor checks
passed; both fixed visual sheets were actually opened afterward. The original
failed attempt and launch records remain immutable. No second recovery, OULU
rerun, detector change, score fitting or target access occurred.

This is the consolidated terminal handoff requested by283, not another
publication/import/activation checkpoint. The
[terminal software result](../results/phase1/msu-preprocessing282-recovery-v1.json),
[additive actual visual receipt](../results/phase1/msu-preprocessing282-visual-review-v1.json)
and [same-package local audit result](../results/phase1/msu-local-audit282-v1.json)
record the distinct software, visual and summary-update steps.

### Exact original-ID and failure accounting

| Scope | Originals | Selected/detector successes | Pre-detector failures | Detector failures |
| --- | ---: | ---: | ---: | ---: |
| Train | 168 | 163 | 5 | 0 |
| Branch calibration | 56 | 56 | 0 | 0 |
| g_domain | 56 | 53 | 3 | 0 |
| Total | **280** | **272** | **8** | **0** |

Exactly4 earlier provisional outputs were reconstructed and copied
byte-identically without reinference, plus276 newly attempted originals:
268 new selected-image successes and8 pre-detector failures. All280 IDs remain
in the final manifest, with unchanged labels, official partitions and frozen
roles. The8 strict-probe failures are recorded as
`invalid_or_undecodable_media`, `not_run/non_accept`, with no image, score,
classifier error or substitute frame. That generic strict-probe outcome is
not a new claim of proven physical corruption or a license to retry them.
Calibration retains56 originals/56 selected and zero actual fitted scores.

### Integrity, replay and all-output readback

- All8 original archive pins cover11,095,264,656 bytes. Recovery reused these
  exact local baseline hashes only after unchanged identities/header guards.
- All16 reconstructed volumes matched prior CRC/size/SHA; joined ZIP bytes
  were11,092,803,150. Exact inner headers/native metadata matched.
- All280 video payloads were CRC-read, totaling11,099,241,100 bytes, and all326
  non-directory ancillary entries were CRC/hash-read. No bundled executable
  was run and no supplied face annotation drove geometry.
- The272 successful full-decode records contain75,765 validated native frames.
  The268 newly selected units each have complete per-frame RGB identity,
  EOF, zero-exit and zero-stderr replay receipts. The four reused units passed
  accepted saved-pixel/parent reconstruction. The formerly failing fifth
  unit also passed the separate301-frame unchanged-RGB fix validation.
- All272 selected frames and matching shared/224/518 crops passed final
  saved-pixel geometry and exact RGB branch readback: **1088 image assets =
  272 selected frames +816 crops**. No orphan asset or leftover temporary
  ZIP/video remained.
- Exact whole-payload/decoded-sequence duplicate groups:0. Forbidden exact
  crossings:0. Frozen role subject groups are21/7/7 with all pairwise
  intersections0; official train/test subjects are15/20 and disjoint.
  Native documented print/replay construction remains subject-scoped.
  These checks do not certify hidden/transformed duplication or joined-domain
  ancestry.

### Actual bounded visual inspection

Opened both fixed label-free sheets:32+4=36 tiles, comprising35 selected face
crops and one explicit pre-detector-failure placeholder. All35 visible crops
show a framed face with eye/nose/mouth regions; no blank/background-only crop
was observed. Blur, low contrast, exposure variation, glasses, screen/print
appearance and some tight hair/chin margins remain; no frame, label or original
appearance was replaced. With zero detector failures, no detector-failure sheet
was required. All8 pre-detector failures have no image and remain in the manifest.

This is a bounded assistant sample-based usability check, not visual inspection
of all272 outputs, independent human review, detector accuracy or PAD validation.
Creation-time software visual-pending fields remain unchanged and are closed by
the later additive visual receipt.

### Final resources and persistent evidence

| Measurement | Terminal observation | Authorized cap |
| --- | ---: | ---: |
| Diagnosis-authority to software terminal | 2282.4568321704865s (38m02.457s) | 14400s |
| Recovery supervised portion | 1583.3097660019994s (26m23.310s) | Same absolute deadline |
| Sampled peak group RSS | 373,174,272 bytes (about356MiB) | 4GiB |
| Sampled peak combined retained/temporary bytes | 26,880,827,017 | 40GiB |
| GPU / scores / fits / model downloads | 0 | None authorized |

The authority clock was not reset at inference start. Peak accounting carries
diagnosis peaks and includes the old failed282 package, new recovery package,
274/276/278/280/model and temporary ZIP/media. Terminal metadata receipts use the
reserved final-record space. Measurements are sampled, not continuous hardware
maxima. Producer, watcher and read-only terminal waiter have stopped.

Private terminal SHA256 commitments:

- Resources: `b442de7827f9e162de142208245b54cec156ae481162776acaf3ab37581504ac`.
- Full readback: `a4683dc87e856ddac1d198d9ad4d908eb606889d2d9cb9d87a763ef014feac38`.
- Full280 manifest: `1f9c40001fe76b9ac5093146dc35a9247ae3fde21b8f81777ea3484a8a26d504`.
- Strict replay readback: `418232be9a879b6a095f9e1dedcc12ce225fe2503e04e3aa55fbab38a6175818`.
- Actual visual review: `daa24f531773604cb941139e1027d7c5f9529c5160f5bc8e6689caf405cf9eb8`.
- Local audit: `9dbd7ad98d6cd808dc68995f70878c8b13aecd612e837fd7d73b35126eed5bf8`.
- Exact summary-update verification: `0387db28d09a118090f6917a427673ae63d4e432679e0c85e4aac72e76258508`.

### Local audit summary updates, not global readiness

Under the bounded benchmark checks and283 handoff, **MSU's local dataset and
split audits are complete**. Only the two MSU `audit_status` cells become
`complete`; its dataset provenance text now names this local integrity/group/
exact audit rather than metadata-only evidence. Original counts, groups,
metadata/role hashes, every other dataset field and all73 runtime source pins
remain unchanged. The [checker](../scripts/complete_msu282.py) verifies existing
terminal/visual evidence without opening or decoding any media.

The normal validator with the permanent frozen root initially returned exactly
six unaudited-status errors. After the two MSU updates it returns exactly four,
for CASIA-FASD and SiW-Mv2 only, with no other error. Schema passes. No predicate
is filtered or bypassed. OULU stays accepted. Scientific readiness, joined-domain
assurance, feature/competence work, OOF/calibration, analysis freeze and locked
evaluation remain separate and are not activated.

Final focused regression: **53 tests passed in37.874 seconds**, including the
new exact canonical-null-role to frozen-assigned-role projection regression.
An additional53 existing manifest/preregistration regressions passed in117.556
seconds after the two summary updates; this is a second targeted run, not a
claim of a newly executed full local suite.
The final metadata checker initially rejected that projection by comparing the
native `role:null` directly to the already frozen assigned role; it was corrected
to require exact equality to the canonical record with only the frozen assigned
role projected. No receipt was written by the failed check, no media was rerun,
and all other field drift still fails.

Exact recovery-implementation commit `3f3cd92a95fcd7845ca30af8f8a49ef5bf9c250d`
CI is now confirmed successful:
[run39765484713](https://github.com/lathevinh/fas/actions/runs/39765484713),
[validate119779750900](https://github.com/lathevinh/fas/actions/runs/39765484713/job/119779750900),
completed2026-10-22 10:47:15 UTC, all12 listed steps successful. This resolves
283's earlier pending observation; it is not a claim about an as-yet-unpublished
final commit's CI, private image quality or independent human verification.

**No further MSU execution is running or required by this package.** Do not
restart it on reconnection or silently retry the8 terminal technical failures.
Subsequent datasets remain outside this completed recovery's execution scope.
The following sections preserve the earlier launch/failure/recovery chronology.

## Historical state: additionally authorized recovery running

After publication of the failed attempt in commit `49e18a4`, the owner explicitly
approved one combined diagnosis/fix/tests/recovery package: CPU-only,4h/4GiB
group RSS/40GiB total private storage including historical packages and temporary
ZIP, preserving the failed attempt and allowing no further retry. The authority
clock started at **2026-10-22 10:32:47.171862 UTC** (17:32:47 UTC+7), with an
absolute deadline of14:32:47 UTC. Diagnosis, implementation/testing and recovery
share this deadline; starting inference did not reset the clock.

The diagnostic reconstruction read16 volume payloads to EOF and matched every
CRC/size/SHA against the first attempt. Original8 archive SHA pins were reused
only after exact regular-file identity/header guards; no redundant full archive
rehash was performed. The inner headers and native metadata hashes also matched.

### Established cause and verified narrow fix

The exact interrupted fifth video reproduced this FFmpeg diagnostic:

```text
Application provided invalid, non monotonically increasing dts to muxer in stream 0: 1 >= 1
```

The original rawvideo replay returned0 but emitted120 stderr bytes. This was
not evidence of a failed full image decode: the rawvideo output encoder's
default timebase quantized distinct native timestamps to the same muxer DTS.
The old helper correctly refused nonempty stderr; it did not retain the useful
payload. Its producer bytes and original failure records remain unchanged.

The additive [replay helper](../scripts/msu_replay282.py) sets output
`-enc_time_base -1`, preserving the source timebase rather than rounding to
the default frame-rate timebase. It does **not** suppress stderr, remove
`-xerror`, relax exit checks, retime the canonical media record, alter RGB
conversion, replace a frame or change the detector/geometry. It retains
per-video stderr and a durable replay receipt even on failure.

A synthetic fractional-timestamp ProRes MOV reproduced the original
non-monotonic-DTS error and passed after this change, with every RGB hash
unchanged. A single fixed replay of the exact original fifth video verified
**all301 original decoded RGB hashes**, returned0 with **zero stderr**, and
preserved the frozen middle-frame RGB. No detection/inference was used for
this validation.

### One recovery execution, separate from the preserved failed attempt

The [diagnostic stage](../scripts/diagnose_msu282_recovery.py) completed in
296.785 seconds. The [recovery driver](../scripts/recover_msu282.py) binds73
source/authority/diagnostic/prior-output commitments and writes to a new private
namespace. Its inference supervisor started at10:41:36.195362 UTC.

The first four provisional transaction/media/image sets were reconstructed and
validated using the accepted saved-pixel validator, then copied byte-identically
without rerunning detection. Each copy is checked against its new source pin,
and the original transaction hash must match the first attempt's terminal
failure ledger. The remaining276 original IDs are attempted once, beginning
with the formerly interrupted fifth video. That video now has a detector-success
row. At the first displayed recovery snapshot,16/280 rows were written; this
is progress, **not terminal acceptance**.

The same full280-row/asset/geometry verifier is reused, with additional exact
new-replay-record/stderr accounting and final receipt checks. The final manifest
still includes every original and preserves decode/detector failures. The
recovery cap counts both the old failed package and the new package plus
274/276/278/280/model/staged ZIP/media; original evidence is not deleted to
make space. The final resource receipt will carry the diagnosis-stage sampled
peaks as well as recovery peaks.

Before recovery execution, **52 focused tests passed in27.038 seconds**,
including the original45 and seven new recovery tests: exact prior-volume
staging/drift refusal, explicit additional authority, byte-identical saved-pixel
reuse without inference, final resource/missing-readback guards, strict
RGB/EOF/exit/stderr diagnostics, the real synthetic ProRes timebase regression
and exact replay-readback accounting. Actual metadata-only recovery preflight,
`py_compile` and whitespace checks also passed.

The [recovery launch receipt](../results/phase1/msu-preprocessing282-recovery-launch-v1.json)
preserves source hashes and chronology. A persistent30-second watcher and the
VS Code task **MSU282 Recovery Progress (30s, read-only)** were opened and verified.
Full readback, actual bounded visual inspection and terminal publication remain
pending. No global audit/scientific status is promoted.

## Preserved first terminal decision: concrete replay defect, stopped without retry

The single attempt stopped after383.804 seconds (6m23.804s), around
17:26:09 UTC+7. Reconnection inspection found an immutable failure receipt,
not a live supervisor. The connection loss is not established as the cause:
the worker traceback explicitly reports `ValueError: strict decoder exit/stderr`
while replaying raw RGB for the fifth original video.

All8 original archives were hashed, all16 volume payloads passed CRC/size
accounting, the joined ZIP/native metadata was verified, and all ancillary
entries were read before video processing. Five per-video media records and
five attempt records exist. Four transaction records report detector success;
these are **provisional outputs without final full readback**, not four accepted
images or a completed dataset.

For the interrupted fifth unit, the first strict probe/framehash pass reported
301 decoded640x480 frames with ProRes video. The subsequent raw-RGB replay
raised the shared helper's exit/stderr guard after reading its expected frame
payloads. The helper does not retain the decoder return code or stderr payload
in this exception, so this evidence cannot distinguish an exit failure from
nonempty diagnostic output or identify the underlying decoder cause. Do not
infer that it is harmless, relax strictness, substitute a frame, or claim the
video is definitively corrupt without diagnostic evidence.

The supervisor stopped, removed its named temporary joined ZIP/video, retained
all existing records, and wrote280 conservative failure-accounting rows.
No worker-completion record, full manifest, full readback or visual-inspection
receipt exists. No second attempt was launched. Source bindings remain equal
to the original30 plan commitments. Accepted OULU evidence is unchanged.

| Terminal measurement | Observed |
| --- | ---: |
| Authority-to-terminal wall time | 383.8040373325348 seconds |
| Supervised wall time | 341.1025115010016 seconds |
| Sampled peak group RSS | 353,169,408 bytes |
| Sampled peak combined retained/temporary storage | 26,597,692,527 bytes |
| Final temporary directory entries | 0 |
| Provisional detector-success transactions | 4 / 280 originals |
| Terminal completion claimed | false |
| Automatic retry / scores / fits / GPU / target work | none |

Caps were not the reported stopping condition. The public
[terminal aggregate](../results/phase1/msu-preprocessing282-v1.json) preserves
null final success/failure counts rather than presenting partial outputs as a
verified full result. Terminal private commitments:

- Resources:
  `5a992088b5f9ab20d95fdabbd1db5b7f62cf460be49eab79b962e24e51d429ac`.
- Release integrity:
  `5626233cd13af979baa9debbd7225c295d7630bda62e5207138ec91c7a5ab387`.
- Full280-row conservative failure accounting:
  `d82e25fe0b84091403651f9e08a6f8123498d05b65b0bc087f1076094d5ec29b`.

At this first terminal decision, renewed media diagnosis/recovery required
explicit additional authority because the original approval prohibited retry.
That additional authority was subsequently obtained as documented above. The
failed attempt and exact producer bytes remain preserved. There is no basis
for reprocessing OULU.

## Historical launch evidence

Review281 accepts OULU280 without rework. Its4950-original/4949-image manifest
and accepted images are preserved; this package does not rerun OULU.
The next concrete dataset is the supplied MSU-MFSD release. The owner explicitly
approved implementation/tests, release/role/group/integrity checks, strict video
decode, fixed-frame selection, the same active-v3 detector/crop export, full
manifest/readback and bounded actual visual inspection in one package.

The single persistent attempt started at **2026-10-22 10:19:45.223516 UTC**
(17:19:45 UTC+7), with an absolute four-hour deadline of14:19:45 UTC.
The supervisor was verified alive and the first original archive hash completed.
This historical section records launch evidence, not a terminal pass, release certification or an
estimate of frame-processing completion. No final selected-image counts,
readback success or visual observations are asserted yet.

The launch receipt is [here](../results/phase1/msu-preprocessing282-launch-v1.json).
Execution uses the [runner](../scripts/preprocess_msu282.py) and
[synthetic regressions](../tests/test_msu_preprocessing.py). Accepted OULU
producer/configuration bytes were not changed.

## Actual metadata scope and resource authority

| Item | Frozen or measured metadata |
| --- | ---: |
| Original outer archives | 8 |
| Original archive bytes | 11,095,264,656 |
| Contiguous inner ZIP volumes | 16 |
| Temporary logical joined ZIP bytes | 11,092,803,150 |
| Original video entries | 280 |
| Uncompressed video payload bytes | 11,099,241,100 |
| Largest individual video | 86,312,086 bytes |
| Native subjects | 35 |
| Native official train/test subjects | 15 / 20 |
| Frozen train/calibration/g_domain videos | 168 / 56 / 56 |
| Frozen train/calibration/g_domain subjects | 21 / 7 / 7 |
| Frame counts, FPS and durations before this run | Not probed; unknown |

Each subject retains all eight native combinations: android/laptop cameras
with live, ipad_video, iphone_video and printed_photo construction. Official
train and test subjects both belong to this source dataset; the separate SiW
target restriction is not applied to MSU. Native subject grouping and all
frozen IDs/classes/roles are unchanged.

The combined authority is CPU-only, at most14400 wall seconds,4GiB group RSS
and40GiB total retained/temporary storage. Storage includes the accepted
274/276/278/280 packages and reused model, the temporary joined ZIP, one
temporary video, and all282 images/records. The supervisor samples resource
usage every two seconds, reserves64MiB for terminal records and checks final
usage. This is a sampled bound, not a continuous hardware-maximum claim.
About278GB free disk was observed before launch; free space is not permission
to increase the40GiB cap.

No retry, cap increase, model download, executable launch from the supplied
release, detector search, scoring, fitting, training, feature extraction or
target evaluation is authorized. Only owned, explicitly named temporary ZIP
and video paths are removed. Original archives and older evidence are retained.

## Combined implementation

1. Reconcile the exact280 native inventory/canonical/metadata/role joins,
   official partitions and disjoint21/7/7 frozen subject populations. Bind30
   source/authority/configuration records, including the unchanged source
   roles and accepted detector/crop implementation.
2. Hash all eight original archives through stable regular-file descriptors
   and verify the accepted outer header inventory. These are local byte
   reproducibility pins, not unavailable publisher checksum certification.
3. Read all16 split volume payloads to EOF with outer CRC/size/SHA evidence
   into one private temporary ZIP. Verify exact accepted inner headers and
   rederive the native metadata inventory, including the native README and
   official subject lists. This avoids repeated random decompression through
   deflated outer split-volume members.
4. Read every non-video inner entry to EOF for CRC/hash accounting, including
   native sidecars and bundled binary bytes. Never execute bundled programs;
   native face annotations are not used for detector geometry.
5. For each original video, extract only one bounded temporary payload,
   verify inner CRC/SHA, run the existing strict FFprobe/FFmpeg full decode
   and frame hashes, then apply the unchanged selector:
   `floor((eligible_frame_count - 1) / 2)`. Selection precedes face detection.
   Replayed RGB must equal the selected decoded hash. No alternate frame is
   chosen after a detection failure.
6. Reuse the accepted CPU-only SCRFD model and active-v3 recipe. Save selected
   RGB and, on detector success, shared/224/518 RGB crops. A pre-detector
   failure remains `not_run/non_accept` without an image; a detector failure
   retains its frozen selected frame and `failed/non_accept`. All280 original
   denominators remain, with null model scores/classifier errors.
7. Check exact payload/whole-decoded-sequence groups. Forbidden exact groups
   crossing subjects, roles, official partitions or classes stop the package.
   Legitimate same-subject attack construction is preserved, not recast as
   independently acquired capture evidence.
8. Perform full280-row readback, exact record/asset-set checks, source joins,
   reconstruction of detector geometry/cubic RGB branch exports from saved
   selected pixels using the accepted validator, completion/CRC accounting,
   original-denominator manifest and final resource checks.
9. Produce the fixed outcome-independent36-tile sample and sheets for every
   detector failure. Pre-detector failures have explicit no-image placeholders
   in fixed samples and are retained in the full manifest. Actual opening and
   inspection are a later additive receipt, not implied by sheet creation.

The full manifest will cover all280 originals even if some videos have
technical failures. Software completion, individual detector success and
bounded visual usability are separate outcomes.

## Fixed policy and inherited evidence

- Active-v3 SHA256:
  `a4f1a27ffc6418c548702e38f3454d67a17ec834fda351ed46d6accaba738c71`.
- Reused SCRFD weight SHA256:
  `5838f7fe053675b1c7a08b633df49e7af5495cee0493c7dcf6697200b85b5b91`.
- Native inventory SHA256:
  `9852d0b712584f3986d0de8fc5811f02ebff12fcbcd7f3921700201647f3e465`.
- Frozen MSU canonical SHA256:
  `43d8348c4b020ae692ed2cec8bc14e27d7a8d71aed983cac3fc5f10ad8e94dab`.
- Frozen metadata SHA256:
  `6ba31c13256b01fb5990a6403285cac06f978da91546f75c9e54948226c125bc`.
- Frozen role SHA256:
  `57b2ff247590fdd078453448210d963d332b5d0c562e4a1cd1d934588d0339a5`.

Detector settings remain640x640, mean127.5/std128, score0.5/NMS0.4,
largest-face/confidence/lexicographic tie-breaking, five-point rotation and
shared1.30 context with constant-zero border/RGB bicubic224/518 exports.
No backbone normalization is applied to exported images. Historical v2/pilot
configuration and OULU records remain byte-preserved.

## Validation before launch

Actual metadata-only planning passed without opening video payloads or hashing
the original media archives. It verified both accepted header commitments,
exact native/frozen role/group populations, source bindings, model/config pins,
fixed sample indices and the installed FFmpeg/FFprobe4.4.2 toolchain.

Focused validation command:

```sh
PYTHONPATH=src:scripts:tests /home/lathevinh/miniforge3/envs/fas/bin/python \
  -m unittest test_msu test_msu_preprocessing test_preprocessing \
  test_preprocessing_completion -q
```

**45 tests passed in30.525 seconds.** Regressions include real synthetic
four-frame video decoding and middle-frame selection, saved-pixel geometry
readback, detector/decode failure preservation, exact280-row manifests,
missing completion/records, wrong counts, orphan assets, temporary cleanup,
auxiliary accounting, forbidden exact-content boundaries, original identity
drift, actual16-volume nested-ZIP transport, outer CRC corruption, deadlines,
spawn failure and final RSS/storage caps. Shared active/legacy recipe checks
and accepted OULU completion regressions also passed.

`py_compile` and `git diff --check` passed. Pylance's file syntax endpoint
could not resolve the workspace file URI; no Pylance diagnostic success is
claimed. Actual interpreter compilation and executed tests are the syntax and
runtime evidence.

## Historical progress setup and retained limits

A persistent read-only watcher writes a snapshot every30 seconds to private
progress records. The VS Code task **MSU282 Progress (30s, read-only)** displays
those snapshots and was opened successfully. It distinguishes archive hashing,
temporary assembly, video processing, readback and terminal state. A280/280
written-row counter does not certify final acceptance.

Reconnection inspection read the actual terminal resource/failure evidence and
confirmed the concrete defect above. No readback or inspection sheets were
produced, so no actual visual review is claimed. The terminal watcher must stop
with the failed package; do not start a second attempt automatically or rewrite
historical pending flags.

This package does not certify all-image manual inspection, independent human
confirmation, detector accuracy, near-duplicate/reencoded-content independence,
cross-dataset ancestry, joined-domain assurance or scientific readiness.
Native integrity and primary-image completion do not silently promote the
generic MSU audit summary: existing audit status fields remain unchanged.
Model features/competence, OOF/calibration, analysis freeze and locked
evaluation remain separate gates. CASIA-FASD and the defined SiW-Mv2 subset
are later work, not concurrent media access under this authority.
