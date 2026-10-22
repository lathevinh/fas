# 281 - Review of280: OULU selected-image preprocessing complete

Date: 2026-10-22
Reviewed final commit: `216f565307d71b95cc07b71c194ef39ce2cc17ee`
Compared launch commit: `9d4ce39`.

## Decision

**Accept280 without rework. OULU local audit and primary selected-image/crop preprocessing are complete:4950 original IDs,4949 successful selected images, one preserved pre-detector failure.** The active-v3 parameter pin and combined manifest correctly incorporate the2970 accepted train outputs plus1979 new non-train outputs. No rerun, extra pilot, duplicate full readback or acknowledgment-only activation report is requested.

This milestone covers selected primary images and shared/224/518 crops. It does not assert completion of every possible training-candidate/sensitivity bank, model feature extraction, score fitting, training, evaluation or global readiness. Do not use those later milestones to reopen this completed image-export task.

## Independent verification

Read the full report/receipts, producer, shared policy, schema/config diff and regression definitions. Independently ran three actual test methods against the published partition/manifest functions and actual standard-library policy module: active/legacy recipe equivalence with parameter-drift refusal; exact1979 subtraction and retained failure accounting; full4950 manifest refusal of missing/duplicate IDs, wrong role/frame, fabricated scores/failure pixels and wrong active hash. All three passed. These are synthetic functional checks, not local OpenCV/private-output replay.

Independently verified aggregate arithmetic:1979+2970=4949; role original counts2970+990+990=4950; role detector successes2970+989+990=4949. One calibration decode failure remains not_run/non_accept with no image, score or classifier error. Selected-frame plus three crop assets per success yields4949+14847=19796 image assets as reported. Zero new detector failures is a reported output count, not an accuracy guarantee.

The active-v3 repository-LF SHA256 matches `a4f1a27ffc6418c548702e38f3454d67a17ec834fda351ed46d6accaba738c71`. The actual policy validates exact detector/geometry and equivalence to the unchanged pilot recipe; the canonical experiment now references v3. The schema requires v3 while retaining historical v2. This is an explicit reported owner-approved pin, not silent editing of old train records or a detector-method search. Old records keep their original config commitments and join through declared recipe equivalence.

Producer, policy, new completion tests and active-v3 config are byte-identical between launch and final commits after line-ending normalization. No later source adjustment is hidden behind the terminal success report. The public278 reconciliation hashes also match the values accepted in279; the reported supervisor/attempt/plan correspondence is recorded as an existing-private-record check, not a new historical execution witness.

Visual receipt readback/resources/full-manifest hashes match the machine aggregate. Its actual-inspection statement covers three sheets/90 tiles, not all4949 images. Creation-time machine visual-pending flags remain historical and are supplemented by that later receipt; they are not an inconsistent final result.

Exact-final-commit GitHub checks/job HTML confirms [run39759609590](https://github.com/lathevinh/fas/actions/runs/39759609590), [validate119760224858](https://github.com/lathevinh/fas/actions/runs/39759609590/job/119760224858), head `216f565307d71b95cc07b71c194ef39ce2cc17ee`: all12 listed steps have success conclusions including Complete job. No exact API completion timestamp is asserted. CI verifies final software/governance, not independent private image quality.

## Review of completion and isolation

The producer restricts new inference to branch_calibration/g_domain selected frames, requires exact frozen parent joins, preserves the original failure and refuses duplicate/missing or substituted units. The verifier reconstructs both new and reused shared crops from saved frozen RGB pixels and validates exact bicubic branch outputs, record/asset sets, full manifest and role counts. Parent supervision checks final manifest/readback commitments and resources before acceptance. No new blocking defect was identified in the reviewed scope.

Reported authority-to-terminal6843.698 seconds is below14400; measured RSS612544512 bytes is below4GiB; declared total retained15417831466 bytes is below24GiB. Scope includes inherited packages/model and new assets/records. Input payload42388241168 bytes is cumulative sequential read volume, not retained storage. No rehash, download, inference on reused train images, score fitting or target access is reported. Resource peaks are measured/sampled, not continuous hardware maxima.

The private4950-row manifest, full output pixels, raw approval, execution logs, resource readback and visual images are unavailable here. Actual all-image hash/pixel joins, private launch history and90-tile usability observations remain bounded reported evidence supported by public source/receipt/CI consistency, not independent artifact readback or human rating by this reviewer. I did not view the private sheets. The claimed source crop quality is sample-based; preserved blur/exposure/closed eyes are not grounds for outcome-driven replacement.

The progress counter measured rows produced, not final readback acceptance. The report distinguishes these states and uses immutable terminal records plus additive inspection evidence. Connection loss alone does not require another run; the supplied persistent-state/source reconciliation is the appropriate recovery approach.

## Move to the remaining datasets

**Close this OULU image-export stage and reuse its fixed detector/policy and implementation patterns.** Recommended next concrete priority is the small MSU-MFSD release, then CASIA-FASD and the already defined SiW-Mv2 subset, subject to actual available inputs and existing authority. Do not change detector or start another model-selection/pilot series per dataset.

For each available dataset, combine release/role/group/integrity accounting, fixed selected-frame preprocessing, failure-preserving manifest and bounded visual checks in one appropriately authorized package. Establish its actual byte/frame/output cost from existing metadata, use the same active parameters, and emit one final pass or concrete defect report. Preserve documented dataset-specific grouping and subset rules. Do not request separate approvals for routine runner, export, readback and manifest activation when the combined work is already authorized. New resource/media-access authority, if needed, must concern that concrete scope rather than another generic preparation task.

No extra OULU confirmation is needed before preparing the next available dataset package. Existing scientific gates remain separate: model features/competence, OOF/calibration, joined-domain assurance, analysis freeze and locked evaluation are not automatically authorized by preprocessing completion. Reuse the complete OULU manifest as an input when those stages are actually commissioned.

## Accepted milestone and retained limits

OULU local dataset/split audit complete;all4950 original IDs accounted;4949 primary selected-image successes and matching crop exports;one existing calibration pre-detector failure preserved. Train2970,calibration989 usable/g_domain990 usable;zero fitted scores. Active-v3 pinned;historical v2/pilot and old output records preserved. Other six dataset/split statuses remain not_audited;scientific readiness false. No model-training, target evaluation or other unapproved execution is created by this review.
