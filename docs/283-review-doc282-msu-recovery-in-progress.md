# 283 - Review of282: strict replay correction and recovery in progress

Date: 2026-10-22
Reviewed commit: `3f3cd92a95fcd7845ca30af8f8a49ef5bf9c250d`

## Decision

**Accept the preserved failed-attempt accounting and the narrow reported replay diagnosis/fix. No blocking new defect was identified in the reviewed recovery design. Do not accept MSU completion yet: the published recovery record is a launch/progress receipt, not a terminal result.** Let the already authorized single recovery continue to its normal verification and visual inspection. This review requires no stop, restart, new permission or additional pilot.

The first failure is an output-replay implementation issue, not established corrupt data or a reason to change the detector/frame selector. Its four outputs were provisional; reuse becomes legitimate only after the reported complete pixel/parent reconstruction. Keeping them byte-identical avoids unnecessary reinference without calling them accepted on the basis of the failed worker alone.

## Evidence checked

Read the full report, first terminal aggregate, recovery launch receipt, replay helper, recovery driver/verifier and relevant source/test structure. Independently verified all four published recovery-source hashes against repository-LF bytes. Population reconciliation4 reused+276 new=280 is consistent; neither first-terminal nor recovery-launch receipt claims completion. The report distinguishes newly approved recovery from an unauthorized automatic retry and retains the failed producer/records.

Independently executed the actual replay-command function AST. It retains `-xerror`, strict error detection, RGB24, unchanged stream selection and `-vsync 0`, with the explicit `-enc_time_base -1` output option. FFmpeg's [timebase implementation discussion](https://ffmpeg.org/pipermail/ffmpeg-devel/2023-July/312018.html) identifies the negative-one demux-timebase setting; that corroborates the intended option semantics, not performance on the project's exact binary. The reported synthetic ProRes test and exact failing-video301-RGB-hash equality are the relevant runtime evidence. I did not independently replay the private video or executable model locally.

`strict_replay` checks every expected RGB payload, extra-byte EOF, deadline, decoder exit and nonempty stderr; it preserves diagnostic bytes and an immutable replay receipt even on failure. It does not merely suppress the observed DTS message. The recovery verifier requires exact diagnostic/receipt sets for newly selected units, full frame/sequence equality and zero exit/stderr, then invokes the full280 output verifier. Reused four rows pass saved-pixel/parent verification and copied-byte commitment checks, preserving the original provisional records.

The recovery supervisor separately runs worker and verifier, checks full-manifest/readback counts, per-unit/diagnostic commitments, configuration and archive identities, and final combined-resource limits. The existing four-hour authority clock includes diagnosis/fix/tests/recovery; inference start must not reset it. Diagnostic peaks are carried into final accounting. One new immutable namespace and launch locks prevent an automatic further run. No new blocking defect was found in this inspected scope.

Private approvals, archive/volume reads, exact diagnostic payload,301-frame equality, copied images and live process state are unavailable for independent readback. Those are bounded reported observations with public code/hash consistency, not independently witnessed execution. A recovery progress counter such as16/280 must not be mistaken for a final processed/success count. Source consistency and a launch receipt cannot establish that the process remains alive now.

## Publication CI at observation

Exact-commit GitHub checks/job HTML identifies [run39765484713](https://github.com/lathevinh/fas/actions/runs/39765484713), [validate119779750900](https://github.com/lathevinh/fas/actions/runs/39765484713/job/119779750900). At retrieval, setup/install steps had success conclusions, while regression/schema/later steps had null conclusions. **CI was still pending, not confirmed green.** Do not reuse an earlier successful run as this commit's result. This does not require interrupting already authorized execution; report the eventual exact-head result in the normal terminal handoff.

## Concrete completion handoff; no new execution stage

The executing agent should finish the current package, not respond with another preparation document. Read persistent status/terminal receipts after reconnect; never relaunch the recovery command merely because a chat disconnected. Preserve the original failure aggregate. The planned terminal public result is `results/phase1/msu-preprocessing282-recovery-v1.json`, distinct from the first failed attempt's aggregate.

That terminal handoff must contain exact280 original-ID reconciliation;4 reused and276 newly attempted IDs; selected/pre-detector/detector success/failure denominators; strict replay/diagnostic readback; release CRC/hash/accounting and exact-boundary checks; full manifest and geometry/asset readback; final diagnosis-plus-recovery caps; and actual fixed visual inspection with every detector failure covered. A missing/dead process requires reading the existing failure state, not assuming success or authorizing another retry. A produced-row counter or worker0 cannot replace final acceptance.

Do not create a separate publication/receipt/import/activation checkpoint. If mandatory local audit checks and preprocessing pass under the applicable approved policy, present the exact MSU summary updates with their evidence in that same final package; do not leave a completed local audit indefinitely marked unaudited merely because later scientific stages remain blocked. Conversely, this running-state review does not itself change those fields or supply missing final evidence.

No further OULU processing, model download, detector search, score fitting or target work is requested. Subsequent datasets remain outside this live recovery scope. The current work is concrete and bounded; let it reach its terminal pass or specific defect without another generic method discussion.

## Retained state

OULU accepted audit/image-preprocessing milestones unchanged. MSU first attempt failed and preserved;one additionally authorized recovery reported in progress;MSU final selection/detector counts, full readback/visual acceptance and generic audit summary promotion are not yet established by published terminal evidence. Other dataset statuses, scientific readiness and later experimental gates remain unchanged. No independent-human, all-image-visual, detector-accuracy or scientific-readiness claim is made.
