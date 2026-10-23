# 287 - CASIA native-probe correction and partial recovery deadline stop

Date: 2026-10-23
Governing review: [286](286-review-doc285-casia-systematic-probe-blocker.md).

## Decision and terminal state

**Blocked, not complete.** The actual probe defect was diagnosed and a narrow
correction demonstrated. The additional recovery then stopped at its original
two-hour deadline before full600 readback or actual crop review. Neither CASIA
audit status is promoted. Previously accepted OULU/MSU outputs are unchanged.

The [terminal receipt](../results/phase1/casia-preprocessing287-recovery-v1.json)
reports a failed package, not600 media failures. Its final counts are null
because the complete verifier never finished. The additive
[partial accounting](../results/phase1/casia-preprocessing287-partial-v1.json)
inventories existing producer receipts without new decoding or pixel readback:

| Original execution state | Count | Acceptance |
|---|---:|---|
| Committed but provisional transactions |447| Not accepted as a completed package |
| Started, interrupted before transaction commit |1| Technical non-accept |
| Not attempted before the deadline stop |152| Not accepted; denominator retained |
| Total original denominator |600| No exclusions or replacement frames |

The447 committed transactions report447 selected originals:441 detector
successes and6 detector failures. The latter retain their selected image and
remain non-accept; no alternate frame was tried. There are1770 image files and
the same number of committed asset references:441 four-image sets plus6
selected failure images. These are **producer-reported provisional outputs,
not a completed independent image readback or usability acceptance**.

| Frozen role | Originals | Committed provisional | Uncommitted |
|---|---:|---:|---:|
| train |360|255|105|
| branch_calibration |120|108|12|
| g_domain |120|84|36|
| Total |600|447|153|

All50 subjects,150 bona fide/450 attack originals, original240/360 release
partitions and frozen30/10/10 subject roles remain unchanged. No training,
feature extraction, classifier scores/fits, target access or SiW work occurred.
Scientific readiness remains false.

## Authority and chronology

The owner explicitly approved one combined diagnosis, narrow correction/tests,
one600-original recovery, full readback/actual visual review and applicable local
handoff. Limits:7200 seconds including diagnosis/tests/execution,4GiB group RSS,
32GiB combined historical/new retained and temporary artifacts, CPU only; no new
tools/models, relaxed media checks, automatic retries or cap extension.

The immutable clock started2026-10-23 08:08:36.593676 UTC+7 and expired
10:08:36.593676 UTC+7. It was never reset at recovery or continuation launch.
The failed285 package and its original receipts are preserved.

During the run, the measured resource observer itself proved too expensive:
a full historical/new artifact scan took9.24 seconds; recent originals took
35.6-36.7 seconds each. The owner explicitly approved a controlled same-deadline
handoff, preserving completed originals without decoding/inference again.

That handoff preserved17 committed transactions and their hash commitments.
Their files were not rewritten. Interrupted, uncommitted probe evidence and the
first supervisor's failed terminal/ledger were quarantined, not overwritten.
The same600 already CRC-checked staged inputs were reused without re-extraction.
The continuation retained all original source pins, media checks and the
three-identical-consecutive-probe-failure stop.

The first observer optimization fully scanned historical roots continuously in
a background thread, with monotone conservative historical byte accounting,
lease-bound snapshots, fatal scan errors and a30-second freshness limit.
RSS/deleted-file usage and the entire growing current output tree were still
measured synchronously. Initial foreground measurement improved to0.387 seconds,
but at208 transactions it had grown to1.98 seconds; recent originals averaged
8.70 seconds. The current-tree traversal remained a throughput defect.

The owner subsequently approved fully asynchronous continuous storage sampling,
again with the **same deadline**, unchanged caps and no repeated committed
originals. By the time that answer was available, the supervisor had already
stopped at the expired deadline. **That second optimization/handoff was not
implemented or launched.** Its approval is retained as unexecuted; it is not
authority to start a fresh two-hour run.

After expiration, work was limited to administrative receipt inventory,
reporting/publication and tests of the administrative partial-ledger helper.
No further source probe, decode, inference, crop opening or local-completion
attempt occurred. The inefficient observer is an implementation limitation of
this package, not evidence of invalid source media.

## Actual first-original failure, not a synthetic diagnosis

The unchanged shared helper was instrumented on the fixed first failed original.
Its first propagated exception was `KeyError: best_effort_timestamp_time` while
reading the terminal frame, after160 parsed frames. Both original commands
returned zero with empty stderr: ffprobe metadata omitted that terminal field;
the unmodified FFmpeg framehash contained161 native RGB pictures.

The demonstrated source is AVI/MPEG4 with native B-frame reordering,25Hz native
timing and valid packet DTS. A guarded `ffprobe -fflags +genpts` metadata pass
exposed the missing terminal timestamp. It did not supply replacement pixels.

The additive [CASIA probe](../scripts/casia_probe287.py) leaves the accepted
shared helper and OULU/MSU producer bytes unchanged:

- Preserve every existing original timestamp. Generated metadata estimates
  that differ from already-present timestamps are recorded and ignored.
- Allow only a missing terminal timestamp for the demonstrated native format.
  Require valid packet DTS, native timebase/duration and original identity.
- Require that candidate to equal the native final packet end and the
  **original, unmodified** strict framehash PTS. No index/FPS/wall-clock
  timestamp assignment is accepted.
- Verify every original RGB hash, size and count, then strictly replay the
  same complete native RGB sequence before selecting the frozen middle frame.
- Preserve strict exit/stderr/EOF checks. Save bounded raw stdout/stderr,
  command/exit commitments and specific failure stages for each attempted input.

## Native timing samples are accounted for, not waived

The fixed low-quality representative passed. The fixed high-quality
representative initially failed its literal count check:132 declared timing
samples/native packets but131 decoded RGB pictures.

Native packet/codec inspection found one six-byte MPEG4 non-coded VOP.
The [native count helper](../scripts/casia_counts287.py) parses the native
VOL clock resolution and VOP coded flag. It requires all declared samples to
equal the native packet count; every coded packet must map to exactly one
decoded picture, and every non-picture sample must be an explicitly parsed
non-coded VOP. Unknown/packed shapes and unaccounted mismatches still fail.
No missing RGB picture is fabricated, dropped, repeated or selected instead.

The same predetermined normal/low/high originals passed the final native
clock/count proof:161+133+131=425 strictly replayed RGB frames, unchanged source
hashes and frozen middle choices. Earlier failed development proofs remain
historical; the final native proof, not an earlier helper hash, gates recovery.
No detector inference was used to choose these representatives.

The447 committed producer receipts report82774 native decoded pictures,
447 guarded native-DTS timestamp transports and99 explicitly non-coded VOPs.
These aggregate existing receipts; they do not stand in for full600 readback.

## Integrity, selection and remaining failures

The source container remains the accepted876296302-byte RAR5 archive with
652 typed entries:600 AVI files and52 directories. Payload bytes total866586586.
Current archive identity and native header CRC guards bind the accepted
container SHA; no publication-driven full archive rehash was added.
All600 staged files passed native unpacked CRC32/size/SHA joins against285's
commitments before recovery. Extraction success alone was not treated as CRC
proof. No tool/model installation or download occurred.

The detector/config, source identities/roles/labels, original denominators and
middle-before-detection policy are unchanged. The six recorded detector failures
are distinct from the deadline interruption and152 not-run originals. Among
the447 committed transactions no pre-detector failure was reported; that does
not classify the153 uncommitted originals as valid or invalid.

The original generic failed-package ledger conservatively marks uncommitted
rows as not attempted. The additive private600-row partial ledger explicitly
corrects that execution distinction for the one existing started receipt:
**interrupted before commit**, not never attempted. It preserves the original
ledger and keeps every package-level final action non-accept.

## Resources and completion gates

- Terminal failure: `TimeoutError: combined two-hour CASIA287 deadline`.
- Terminal package clock:7208.954565 seconds, including shutdown/cleanup after
  the deadline signal; supervised continuation:3851.223104 seconds.
  **Wall-cap compliance is not claimed.**
- Sampled peak group RSS:395608064 bytes, approximately377.28MiB.
- Sampled combined retained/temporary storage:17282819455 bytes,
  approximately17.28GB; historical accepted packages are included.
- GPU seconds, classifier/model scores and fitted scores:0.
- Owned bulk staged originals were removed. Fixed diagnostic/proof inputs,
  raw probe evidence, partial outputs and immutable source commitments remain.

There is no complete600-row/pixel/probe readback, no actual bounded crop
inspection, no crop-usability pass and no CASIA local-audit completion.
[Dataset summary](../manifests/dataset_summary.csv) and
[split summary](../manifests/split_summary.csv) retain both CASIA `not_audited`
statuses and their existing provenance. SiW-Mv2 also remains unaudited.

The public [completion checker](../scripts/complete_casia287.py) contains gated
future visual/local modes, but **none was executed**. Only its administrative
`--report-partial` mode ran after expiration; it does not open media or certify
images. It reports accounting/image/local completion false.

Review286's historical285 checker is not equated with a current runner hash.
The actual source basename is `record_casia285_visual_review.py`, SHA256
`7555cd9d030488c71d988d0d4bfd56e6d81ed46d775c83a3f1ba160d645e8988`.
An administrative source-hash check confirmed those source bytes agree with
[285's checker receipt](../results/phase1/casia-local-audit285-v1.json).
That historical source is private, not the current public runner, and was not
used as a recovery acceptance gate. The current public completion-checker SHA
is recorded separately in the additive partial receipt.

## Software evidence and reproducibility boundaries

Before the original recovery,42 focused CASIA/native-clock/count/strict-replay
and resource/stop tests passed. A separate29-test completion/image regression
selection passed. Before the controlled continuation,15 focused observer,
completion-projection and recovery tests passed; these selections overlap and
are not claimed as86 distinct tests. New sources were compiled and whitespace
checks passed. After expiration,3 administrative partial-accounting/projection
tests passed; this is not additional real-source validation.

The [original recovery controller](../scripts/recover_casia287.py),
[explicit continuation controller](../scripts/handoff_casia287.py),
[historical storage observer](../scripts/casia_resource287.py),
[native regression tests](../tests/test_casia_recovery.py) and
[observer tests](../tests/test_casia_resource_observer.py) are public for review.
The synchronous growing-tree cost is a known unresolved performance defect,
not a ready-to-run recommendation. Do not restart these one-shot controllers
or infer fresh authority from their presence in the repository.

Private original bytes, per-original identifiers/records, raw approvals,
diagnostic command outputs and images are not published. Public aggregate
receipts and source hashes provide bounded reported evidence, not independent
access to those private artifacts. GitHub CI verifies software, not completion
of the private CASIA dataset.

**Handoff:** retain the diagnosis, proof and447 provisional transactions; keep
CASIA blocked. Any further execution requires new explicit authority because
the unchanged approved deadline has expired. No retry or cap increase is
started by this report.
