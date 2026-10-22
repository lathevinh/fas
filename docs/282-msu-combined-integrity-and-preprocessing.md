# 282 - MSU-MFSD combined release integrity and primary-image preprocessing

Date: 2026-10-22
Governing review: [281](281-review-doc280-oulu-image-preprocessing-complete.md).
Base commit: `0e07beb`.

## Current decision: one authorized package running, not yet complete

Review281 accepts OULU280 without rework. Its4950-original/4949-image manifest
and accepted images are preserved; this package does not rerun OULU.
The next concrete dataset is the supplied MSU-MFSD release. The owner explicitly
approved implementation/tests, release/role/group/integrity checks, strict video
decode, fixed-frame selection, the same active-v3 detector/crop export, full
manifest/readback and bounded actual visual inspection in one package.

The single persistent attempt started at **2026-10-22 10:19:45.223516 UTC**
(17:19:45 UTC+7), with an absolute four-hour deadline of14:19:45 UTC.
The supervisor was verified alive and the first original archive hash completed.
This is launch evidence, not a terminal pass, release certification or an
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

## Progress, finalization and retained limits

A persistent read-only watcher writes a snapshot every30 seconds to private
progress records. The VS Code task **MSU282 Progress (30s, read-only)** displays
those snapshots and was opened successfully. It distinguishes archive hashing,
temporary assembly, video processing, readback and terminal state. A280/280
written-row counter does not certify final acceptance.

On terminal notification, read the actual immutable resources/readback/manifest,
verify receipts/caps, open the fixed and failure sheets, and publish one final
pass or concrete defect report plus an additive visual receipt. Do not start a
second attempt automatically or rewrite historical pending flags.

This package does not certify all-image manual inspection, independent human
confirmation, detector accuracy, near-duplicate/reencoded-content independence,
cross-dataset ancestry, joined-domain assurance or scientific readiness.
Native integrity and primary-image completion do not silently promote the
generic MSU audit summary: existing audit status fields remain unchanged.
Model features/competence, OOF/calibration, analysis freeze and locked
evaluation remain separate gates. CASIA-FASD and the defined SiW-Mv2 subset
are later work, not concurrent media access under this authority.
