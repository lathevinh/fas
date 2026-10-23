# 292 - Review of291: SiW verified images and exact-crossing resolution

Date: 2026-10-23
Reviewed commit: `baecc438ed36f4b8dfb8cbf2eed39b093f3cda07`
Governing review: [290](290-review-doc289-casia-completion.md).

## Decision

**Accept291 as a truthful blocked-run report with completed saved-image verification and bounded crop inspection. Retain all1680 prepared originals and6672 image assets. Do not accept clean frozen-boundary/local-audit completion while five exact-content crossings remain. No new media-processing campaign is needed: resolve use eligibility through one explicit, versioned protocol decision and close from saved evidence.**

The practical distinction is that image production/readback is done; experimental use eligibility is not settled. The machine flag primary_image_preprocessing_complete=false remains historically correct under the combined acceptance gate, but must not be interpreted as missing1680 images. A subsequent additive receipt can separate image_artifacts_verified from protocol_use_accepted. OULU/MSU/CASIA remain closed for their accepted milestones.

## Evidence checked

Read report291, producer, non-accepting saved-output checker, completion interface, four public receipts and regression definitions. Independently executed the actual duplicate_groups/summary function ASTs with the repository's three ExactCrossingTests: all passed. This covers the synthetic3+2+1 crossing pattern, no double-counting of byte/decoded evidence, forbidden class crossings and distinct-content negatives. It is a focused function test without importing the private-media/OpenCV execution stack, not a complete local suite.

Additional independent standard-library checks passed for aggregate/per-role totals, image arithmetic, terminal/readback/visual hash links, the public checker source hash, unchanged summary hashes and reported time/memory/storage cap arithmetic. Raw media, per-original private records, approvals and sheets are unavailable here. Real-source verification/visual observations remain bounded producer-reported evidence; I did not independently decode or view those images. Technical byte/frame verification is not visual adjudication or independent scientific replication.

Exact-commit checks link [run39936224548](https://github.com/lathevinh/fas/actions/runs/39936224548), [validate120356301738](https://github.com/lathevinh/fas/actions/runs/39936224548/job/120356301738). At both review checks, checkout/setup steps were successful but remaining step conclusions were null and Complete job was absent. **CI completion is unconfirmed, not green and not proven failed.** The next ordinary closure must bind its eventual terminal conclusion; no standalone review round is needed just to collect it. Producer-reported51/54-test selections overlap and are not added into a unique total.

## Completed work should be preserved

| Population | Originals / selected | Detector successes | Detector failures |
|---|---:|---:|---:|
| Source train |632 /632|621|11|
| Source calibration |215 /215|214|1|
| Source g_domain |210 /210|210|0|
| Official test, null source role |623 /623|619|4|
| Total |1680 /1680|1664|16|

All totals reconcile:1664*4+16=6672 image assets,1680 strict replay receipts and306156 native frame hashes. Source roles sum1057;623 test originals retain null roles and preparation-only fit disposition. Unknown subjects remain unknown. Sixteen no-face detections stay non_accept with their selected images; no replacement frame is needed or permitted for this closure.

The saved-output checker verifies original bindings/CRC/size, reparses native probe evidence, validates images and replay hashes/EOF/exit/stderr, and seals original records without decode or detector calls. It has no promotion path. The additive full-readback receipt succeeds while the original producer terminal remains failed: this accurately separates an executed image pipeline from its boundary-gate stop.

Reported five-sheet inspection comprises108 viewed tiles:92 crops and16 selected failure images, zero placeholders. It is bounded usability inspection, not manual inspection of every original. Local visual closure13305.871357 seconds is below21600;783298560-byte RSS and24323719083-byte conservative storage are below4GiB/48GiB. Summary hashes remain unchanged, preserving both SiW not_audited statuses. These private execution observations were not independently reproduced here.

## The finding is finite and directly actionable

Six disjoint two-original member sets are reportedly identical both in payload bytes and in their complete native RGB sequences. These are six pairs, not twelve: the two hash kinds corroborate the same membership. Three pairs cross official train/test; two cross permanent source roles; one stays within a single partition/role/class. All are attack-labeled and there are no label crossings. Five distinct boundary-crossing pairs are forbidden under the current protocol.

This is a specific equality finding, not a request to investigate participant identity, find near-duplicates or revisit accepted datasets. A rerun cannot change identical source content. Keeping source/test copies active across a prohibited boundary also cannot be justified merely by successful image production.

## Recommended single protocol decision

Prepare a **versioned source-use exclusion overlay**, leaving the frozen canonical population, official test membership, historical roles,1680 image transactions and existing receipts untouched. This is a proposed protocol amendment, not an already adopted change or a silent waiver:

1. For each of the three official train/test pairs, retain the official test original and mark its source-side copy ineligible for all source fitting/calibration/domain-use stages. The test original remains null-role; no test scoring/evaluation is authorized.
2. For each of the two source-role pairs, retain exactly one active source original. Proposed fixed priority is g_domain, then branch_calibration, then train; exclude the lower-priority copy without moving the retained video's role. Publish this priority before use, independent of image quality, detector outcome or any classifier result. It preserves the more held-out role while removing cross-role reuse.
3. The sixth pair has no prohibited crossing. Retain it under the current rule, disclose its exact-content group and avoid inventing another completion blocker. A weighting/deduplication experiment is a separate later methodological choice.

Given the reported disjoint pairs, this recommendation excludes exactly five source originals from experimental use:1057 frozen source originals remain in inventory,1052 become source-use eligible, and623 official-test originals remain unchanged. The resulting active population is1675, while the archived/prepared denominator remains1680. These are conditional calculations, not a claim that an actual overlay already exists. Recompute active role/class and detector-success/failure counts from the five exact IDs; the public aggregates cannot identify their precise role breakdown. Do not treat all1052 eligible source originals as detector successes automatically.

The reason for an explicit decision is concrete: membership/use eligibility was frozen, and291 explicitly did not authorize dropping or regrouping originals. A review cannot silently change that policy. The agent should first produce the concrete five-ID overlay, before/after counts and deterministic rationale from already saved records, then obtain one owner adoption of that complete amendment if no existing explicit authority covers it. No new raw-media access or chained per-pair approvals are needed merely to prepare it. Do not ask the owner an open-ended question about how to solve duplicates without this concrete proposal.

## One closure package, no media rerun

After adoption, bind the overlay and policy version to downstream manifests and every source consumer. Validate the **effective-use population** has zero prohibited byte/decoded crossings while preserving the original six-pair finding in historical/full-inventory reports. Make the validator distinguish archived inventory from active use; never suppress a nonzero original finding or hard-code zero. Add regression coverage that excluded rows cannot enter fitting/calibration/domain consumers and that test/null rows stay ineligible for source use. The train/test and source-role guards remain strict for active use.

Reuse291's sealed image/readback/visual evidence by hash. Only validate overlay joins, effective counts, frozen-record preservation and downstream eligibility behavior; do not decode1680 videos, rerun the detector or open the same sheets again without changed assets. Record eventual CI success for the reviewed/final implementation and run appropriate focused protocol/consumer checks. Any summary promotion must explicitly describe the amended use policy, preserve original archive counts and pass the normal validator; no original frozen hash may be represented as the new effective-use manifest hash.

Publish the adopted policy, concrete overlay, before/after counts and final local acceptance in one package. If the owner rejects this proposed eligibility amendment, retain291's verified images and the existing blocked-use status; do not restart processing or invent a clean-boundary claim. No classifier training, target evaluation, participant-disjointness certification or global scientific readiness is authorized by this review.

**Next result: a five-source-exclusion proposal and, once adopted, one saved-evidence protocol closure. The1680-image job is already done and should not be repeated.**
