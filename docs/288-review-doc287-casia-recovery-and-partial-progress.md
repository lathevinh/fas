# 288 - Review of287: CASIA native-probe recovery and partial progress

Date: 2026-10-23
Reviewed commit: `6aa992dd7369902cc064535d89117aba0ee925f3`

## Decision

**Accept287's narrow probe diagnosis, native-clock/count correction and honest deadline-stopped partial report. Do not accept CASIA preprocessing or local-audit completion. Preserve447 provisional committed transactions; finish the remaining153 originals and verify the retained outputs in one recovery package after fixing the observer bottleneck.**

This is useful progress: the previous all-original generic probe failure has been diagnosed and the corrected route reportedly produced real selected images. A deadline stop does not invalidate every committed transaction or justify restarting600 videos. Existing OULU/MSU acceptances stand. CASIA summary statuses remain not_audited until the completion gates pass.

## Evidence and limits

Reviewed report287, its two public aggregate receipts, native probe/count parser, recovery/handoff controllers, resource observer and regression definitions. Exact-commit public GitHub job HTML confirms [run39894917027](https://github.com/lathevinh/fas/actions/runs/39894917027), [validate120222995843](https://github.com/lathevinh/fas/actions/runs/39894917027/job/120222995843): all12 listed steps conclude success, including Complete job. This verifies the software CI result, not private CASIA completion.

Private media, raw approvals, transaction records, full replay evidence and images are unavailable in this checkout. Real-source counts and resource observations remain producer-reported, with public consistency and source review. No independent private-video replay, pixel readback or visual adjudication was performed for this review. Reading test definitions is not a local test execution; the producer's overlapping test selections are not added into a unique total.

## Diagnosis is specific enough to retain

The reported fixed AVI/MPEG4 B-frame example has a missing terminal ffprobe timestamp despite successful commands and native RGB decoding. The correction is restricted to this supported shape: retain every existing native timestamp, require native packet clock evidence and require the transported final timestamp to equal both the native final packet end and the original framehash PTS. Generated timestamps cannot replace existing ones. No index/FPS-derived frame is fabricated.

The separate declared-count discrepancy is accounted for by explicitly parsed non-coded MPEG4 VOP packets. The public parser requires coded packet positions to match decoded picture positions and bounds the exceptional non-coded payload. This is stronger than ignoring a frame-count mismatch. Reported fixed low/normal/high proofs cover425 strict RGB frames; these proofs support the narrow correction, not all600 originals. Keep these receipts and do not repeat them without a changed implementation or new failure.

## Partial accounting reconciles; completion does not

| Item | Reported count |
|---|---:|
| Original denominator |600|
| Committed provisional transactions / selected images |447|
| Detector successes |441|
| Detector failures |6|
| Interrupted before commit |1|
| Not attempted after deadline |152|
| Referenced image assets |1770|

The split commitment255 train +108 calibration +84 g_domain equals447. Against original360/120/120, remaining work is105/12/36, totaling153. Asset count reconciles441 successes with four assets each plus six selected failure images:1770. A detector failure retains its original and selected-frame evidence; it does not permit a replacement frame.

The additive partial ledger correctly distinguishes one started interruption from152 never started. Do not classify these153 as invalid media. The447 committed units are provisional until readback and required crop inspection pass. The report explicitly leaves accounting/image/local completion false and scientific readiness false; that boundary is correct.

Terminal wall time7208.954565 seconds exceeded the7200-second allowance including shutdown;287 explicitly does not claim wall-cap compliance. Reported RSS395608064 bytes and combined storage17282819455 bytes are below their respective caps. Record the stop honestly and improve bounded shutdown; no repeat execution is needed merely to obtain a cleaner resource receipt.

## Actionable performance defect

`casia_resource287.measured()` still calls `tree_bytes(current)` synchronously during foreground measurement. `casia_probe287.capture()` measures repeatedly while waiting for subprocesses. Consequently, growing output directories add traversal work to every probe. The background historical scanner also starts another full scan after only0.05 seconds of waiting. Moving only historical scans off the foreground did not remove the growing current-tree cost or potential storage contention.

Reported measurement cost rose from0.387 seconds to1.98 seconds by208 rows, with recent per-original time around8.7 seconds. A small-tree preflight below two seconds is not a throughput guarantee at600 rows. Fix this concrete observer cost before executing the remaining originals. Preserve resource caps and fatal handling of stale/failed measurements; use a bounded asynchronous accounting design with conservative treatment of writes between snapshots. Avoid continual whole-tree scans at a cadence that competes with decoding. Verify growth, stale/error behavior and foreground latency on a representative synthetic populated tree before private-media execution.

## One finish-oriented recovery package

1. Prepare the observer correction, focused regressions and a resume plan in the same change. No separate diagnosis-only checkpoint or new native proof campaign is needed for the unchanged parser.
2. Verify the447 committed transaction bindings, source/config/model identities and retained asset hashes before reuse. Perform their pending image readback and bounded crop inspection; do not rerun their detector or decoding merely because the package stopped. Repair only a specifically identified incomplete/corrupt unit, with an explicit receipt.
3. Resume exactly153 uncommitted originals, including the one interrupted before commit. Preserve immutable prior receipts and quarantine incomplete artifacts. Bulk staged inputs were removed, so stage the required remaining inputs as necessary with the existing archive integrity checks; do not rerun the entire600-original extraction/processing workflow.
4. Close with one600-row reconciliation, success/failure reasons, selected-frame identity, image readback, bounded crop inspection and resource/stop receipt. Keep all originals and use the accepted fixed-middle-frame policy. Update CASIA summary statuses only after those checks actually pass. Do not add classifier fitting, target evaluation or unrelated dataset work to this execution.

The old deadline has expired. A late asynchronous-observer approval does not reset it. This review authorizes preparation of the correction and concrete resume package; it does not invent a fresh private-execution clock. Present one combined fresh request covering remaining153, verification of447 retained transactions and final600-row closure, with explicit wall/RSS/combined-storage limits and no automatic extension. A proposed two-hour/4GiB/32GiB envelope must include verification and shutdown and must be supported by the corrected latency estimate before submission. If available authority already explicitly covers this fresh scope, bind that authority rather than asking again. Do not request approvals separately for each ordinary completion substep.

**Next useful result: a completed, verified CASIA package using the retained447 transactions and the remaining153 originals. No restart of the accepted datasets or of the full CASIA run.**
