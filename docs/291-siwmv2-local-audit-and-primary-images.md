# 291 - SiW-Mv2 local audit and primary-image preparation

Date: 2026-10-23
Governing review: [290](290-review-doc289-casia-completion.md).

## Status and authority

**All1680 originals have committed image transactions, but SiW local acceptance
is blocked by real exact-content crossings.** The producer stopped at its
existing duplicate-boundary gate; no membership or gate is changed to force
completion. Both SiW audit statuses remain `not_audited`.
CASIA is accepted without rework under290; OULU/MSU/CASIA are not restarted.

The owner explicitly selected `approve_combined_siw291_full1680`: one combined
code/tests, compatibility/resource preflight, native integrity/decode,
fixed-image/crop, full readback, actual bounded visual/local-audit and
publication package. Its clock starts13:16:09.103914 UTC+7 and ends
19:16:09.103914; work subprocesses stop by19:06:09, reserving ten minutes.
CPU only,21600 seconds,4GiB combined group RSS,48GiB combined historical/new
retained and temporary artifacts; no automatic retry, extension or new
tool/model installation. Preparation and tests count against this clock.

All1680 frozen eligible originals are in scope:1057 source videos retain
632/215/210 permanent roles;623 official-test videos remain role `null`.
The latter are explicitly authorized only for fixed preprocessing and local
integrity/decode audit, not source roles, classifier scoring/fitting,
evaluation or method selection. Unknown subjects remain unknown and grouping
remains by video. No participant-disjointness claim is introduced.

## Supplied release and metadata-only preflight

Current ZIP headers exactly reproduce the accepted private inventory SHA256
`6d105949c6f626dae750ce1a0f22b0a5bf8a85de8b77a9eec4929b7137761d60`.
The pinned reference sources and exact canonical/native metadata also match.
There are1719 entries:1700 video members, two documents and17 directories.
The accepted intersection excludes20 supplied out-of-protocol videos;11
reference IDs absent from the archive are not invented or counted as attempted
originals.

The supplied ZIP is20268115012 bytes. All members total20394222613 unpacked
bytes; the largest is55085047 bytes. Eligible payloads total20350945235
bytes, of which12564442559 are source videos. Supplied video extensions are
994 MOV,306 MP4 and400 AVI; this does not imply a shared codec.
Approximately276.49GB free output storage was observed before execution.
This inspection read headers/reference files, not video payloads.

An initial reference-root check failed explicitly because the cached commit
directory contains the actual `source_SiW_Mv2` subdirectory. Checking that
correct root verified every pinned source; no file was fetched or changed.

## Execution and closure design

The [controller](../scripts/preprocess_siw291.py) stages one exact native ZIP
member at a time, checking EOF, size, CRC32 and SHA256 and deleting only its
owned staged file. It hashes the whole supplied archive once under supervision,
then guards its exact file identity rather than gratuitously rehashing it.
Only1680 eligible video payloads are staged; the20 excluded videos and document
payloads are not processed.

Active snapshot/journal/progress controls live on native Linux storage from
the beginning. The accepted asynchronous snapshot/reservation implementation
is reused, including90-second stale/error failure, bounded per-capture files,
conservative pre-write credits and historical/current/native-control accounting.
The populated-root foreground check requires p95 below50ms and maximum below
250ms. A direct read-only30-second watcher avoids blocking VS Code task calls.
The actual initial scan counted17368919577 physical retained bytes in
15.826457 seconds. Fifty foreground samples on native IPC measured p95
1.107ms and maximum1.364ms; initial conservative accounted storage was
17637355033 bytes including the control reserve. Both latency thresholds
passed before the media worker started. These are observer measurements,
not a private-decoding throughput claim.

The first committed units cover each supplied extension and both official
partitions. Their actual timings support a conservative remaining-time check,
including40 minutes for closure; they are not decoded/inferred again as a
separate pilot. A failed compatibility sample or three consecutive probe
failures stops bulk work with precise evidence, not a generic all-failure
completion claim.
All six actual compatibility originals passed with detector success. They
contained four MPEG4 and two MJPEG streams, spanning native AVI and MOV/MP4
containers; no CASIA-specific timestamp/count repair was needed. Unit times
were7.984,8.436,6.013,9.923,2.568 and2.656 seconds. Using the slowest observed
unit for every remaining original plus2400 seconds of closure gave
19011.473 seconds, below the then-remaining19724.026 work seconds.
This is a conservative launch-time envelope, not a guarantee about later
clips; watchdog caps and saved exact failure evidence remain authoritative.

Generic probes preserve stdout/stderr/exit receipts, original metadata and
native RGB framehash evidence. Native integer timestamp ticks are compared
with the displayed decimal within its rounding precision and used as exact
rationals. Encoder timebase preservation avoids FPS quantization; dimensions,
timestamps, counts, byte sizes and every strict replay RGB hash/EOF remain
checked. CASIA's AVI terminal-timestamp and non-coded-VOP repairs are **not**
automatically applied to SiW. Actual incompatibilities require their own
saved evidence and a narrow justified correction within applicable authority.

Selection remains the earlier middle successfully decoded frame, fixed before
detection. Existing detector/model/config, five-point alignment,1.30 context
and RGB bicubic224/518 branches are reused. Test rows keep null roles and a
separate `not_authorized_test_preparation_only` fit disposition; no source
role is fabricated merely to reuse image validation. Detector failures retain
their selected original image and non_accept status, without replacement.
Technical failures retain the original/class/partition denominators and exact
durable reasons without fabricated frames or crops.

The [completion checker](../scripts/complete_siw291.py) requires all1680
bindings, saved native/probe/replay/PNG/pixel readback, actual opening of every
predetermined fixed/failure sheet and crop-usability acceptance before allowing
only SiW's two audit statuses/provenance description to change. The normal
external-frozen-root validator must move from its exact two SiW status errors
to zero; no scientific stage is thereby authorized.

Before launch,51 focused tests passed in2.731 seconds across the new SiW
preprocessing, accepted metadata adapter and reservation-budget modules.
They include actual synthetic H264 MP4, ProRes MOV and FFV1 AVI native
timestamp/framehash/replay/PNG/pixel readback, genuine corrupt-file diagnostics,
null-target/source-role separation, CRC/size limits, no timestamp/count waiver,
and durable no-retry failure on worker or final-scanner error. All three new
Python files compiled successfully. These tests are not private-media results.

## Concrete terminal stop: exact duplicates across frozen boundaries

The [original terminal](../results/phase1/siwmv2-preprocessing291-v1.json)
failed closed after all1680 per-original commits, at the existing
`preprocess_msu282.exact_checks` boundary guard:
`ValueError: forbidden exact media/decoded-content group crossing`.
This is not a decoder compatibility error, detector failure or network loss.
The worker stopped before its completion receipt/full readback phase; the
creation-time terminal correctly retains false completion flags and null
not-yet-reconciled output totals. Those historical bytes are preserved.

Direct saved-record reconciliation found1680 decoded/selected originals,
1664 detector successes,16 detector failures,306156 native RGB frames and
6672 image assets (1664*4+16). Permanent source roles remain632/215/210 and
all623 test roles remain null. No pre-detector failure was observed.

There are six byte-identical member sets, each containing two distinct frozen
original IDs. The very same six pairs also have identical full native decoded
RGB sequence hashes. These are not12 distinct duplicate pairs:

| Distinct duplicate pairs | Count |
|---|---:|
| Official train/test crossings |3|
| Within official train, crossing permanent source roles |2|
| Within one official partition/role/class |1|
| Total / originals involved |6 /12|
| Forbidden distinct pairs |5|
| Binary-label crossings |0|

All are attack originals. Native per-member CRC/size commitments, independently
computed payload SHA256, saved decoded sequence hashes and unchanged archive
identity bind the finding to the supplied release. Video grouping/unknown
subjects do not excuse byte-identical content crossing source roles or
official source/test partitions. No original is dropped, relabeled, moved
between roles or silently collapsed into another original. Participant
identity or a near-duplicate search is not needed to establish exact equality.

The original terminal took12369.055496 seconds (3h26m09.06s) from approval,
including preparation and the whole-archive hash. Sampled RSS783298560 bytes
and conservative storage24323719083 bytes are below4GiB/48GiB; owned staging
was cleaned and the producer/scanner/watcher stopped. No automatic retry or
second media campaign was launched.

The additive [non-accepting readback checker](../scripts/readback_siw291_blocked.py)
seals all5040 original attempt/media/transaction records, original terminal,
whole-archive integrity and pinned plan/source identities, then reads only
saved probes/replay receipts/images. It does not extract/decode/infer an
original again. It records all duplicate groups rather than returning a
hard-coded zero, preserves the forbidden result and writes separately under
`blocked_closure`. There is no promotion path in this checker.

Fifty-four combined targeted tests passed in2.603 seconds before this saved-
output closure. This includes a synthetic exact reproduction of six pairs
with the same3+2+1 boundary pattern, tests that byte/decoded pairs are not
double-counted, and confirmation that class crossings remain forbidden.
Earlier51-test selections overlap and are not added to54.

Full saved-output readback and actual fixed/failure/duplicate sheet inspection
are now finished. The [blocked readback receipt](../results/phase1/siwmv2-blocked-readback291-v1.json)
verifies all1680 saved native probes and strict replay receipts, all306156
frame-hash entries and all6672 selected/crop PNG assets. The new reader made
zero source-decode and zero detector calls and preserved every original record.
The original failed terminal is not rewritten into a successful chronology.

All five sheets were actually opened: three predetermined fixed sheets,
the complete16-image detector-failure sheet and the12-original duplicate
sheet. Total108 viewed tiles =92 successful face/presentation crops +
16 selected failure images +zero placeholders. The fixed sample includes
profiles, closed eyes, makeup, masks/mannequins, print/replay borders and
deliberate partial occlusions. Successful crops retain the facial/presentation
region rather than fabricated pixels. Failure images include visible faces,
an off-frame subject and a blurred moving subject; these observations do not
prove all detector failure causes. The six duplicate pairs also appear
identical in their dedicated sheet, consistent with exact byte/full-sequence
evidence rather than an appearance-based participant-identity claim.

The [actual visual receipt](../results/phase1/siwmv2-blocked-visual291-v1.json)
records a bounded crop-usability pass, **not** dataset acceptance or manual
inspection of all1680 images. Saved-output readback completed13160.169159
seconds after approval; actual visual closure completed13305.871357 seconds
(3h41m45.87s), at16:57:54.975271 UTC+7, before the unchanged19:16:09 deadline.
Peak measured resources remained747.01MiB RSS and22.65GiB conservative
accounted storage. Supervisor, worker, scanners and progress watcher are all
stopped; staged originals remain cleaned.

| Frozen population | Originals / selected | Detector successes | Detector failures |
|---|---:|---:|---:|
| Source train |632 /632|621|11|
| Source calibration |215 /215|214|1|
| Source g_domain |210 /210|210|0|
| Official test, null source role |623 /623|619|4|
| Total |1680 /1680|1664|16|

Every detector failure is `no_face_above_frozen_threshold` and remains
non_accept, with a real selected image and no crop replacement. The original
785 bona fide /895 attack denominators and all1680 identities remain intact.
The supplied archive's one-time local SHA256 is
`4e89fea38c93caab15c166e55554910538581ab7bdbbb9d88e20d88792708846`;
this is a local identity pin, not acquisition-authenticity certification.

The [definitive local assessment](../results/phase1/siwmv2-local-assessment291-v1.json)
therefore distinguishes verified image artifacts from blocked acceptance:
`image_artifacts_verified=true`, but `local_audit_complete=false`,
`primary_image_preprocessing_complete=false`, `promotion_permitted=false`
and `scientific_readiness=false`. Both summary files are byte-for-byte
unchanged from the accepted290 checkout. The normal external-frozen-root
validator still reports exactly the two SiW audit-status errors; OULU/MSU/CASIA
remain complete.

Next work requires an explicit decision on exact duplicates in the frozen
population/roles, preserving these receipts and outputs. This report does
not authorize reassigning groups, removing the12 originals, changing seeds,
waiving the boundary guard or starting training/target evaluation. Re-running
the same1680 videos would not fix byte-identical content in the release.

## Reporting limits

Real media, individual source IDs/paths, raw approvals, private per-original
records and images are not published. Public software/aggregate commitments
are not independent private-media replay or visual adjudication. Acquisition
authenticity, participant identity/disjointness, near-duplicate independence
and joined/transformed ancestry are not inferred from local structural checks.
Historical accepted receipts and the earlier failed CASIA attempts are not
rewritten.
