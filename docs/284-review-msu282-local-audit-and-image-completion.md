# 284 - Final review of MSU282: local audit and primary-image completion

Date: 2026-10-23
Reviewed final commit: `1d420b8b6388dd172e8f0139a699e9fb3c287989`

## Decision

**Accept the completed MSU282 recovery, bounded local audit and primary selected-image preprocessing without rework. Keep both MSU audit_status fields complete.** All280 original IDs are accounted:272 selected-image/detector successes,8 retained pre-detector technical failures and zero detector failures. No repeat recovery, extra pilot, silent retry of the eight failures or separate activation review is requested.

This resolves283's pending execution outcome. Its earlier running-state assessment and the original failed-attempt records remain historical. OULU's accepted milestones remain unchanged. Two datasets now have accepted local audit and primary-image preprocessing milestones; remaining datasets and later model stages are separate work.

## Independent verification

Read the updated report, terminal software/visual/local-audit receipts, completion checker and regression. Counts reconcile4 reused+276 newly attempted=280;268 new selected successes+4 reused=272;272 selected+8 pre-detector failures=280. Role selected counts163+56+53=272 and technical failures5 train+3 g_domain=8; calibration56 originals/56 selected/zero fitted scores.1088 image assets correctly equal272 frames plus816 shared/224/518 crops.

Public visual receipt readback/resources/full-manifest/replay-readback hashes agree with the recovery result. The local checker source hash matches its published commitment after repository-LF normalization. Inspected final CSV changes: only MSU's audit_status in both summaries plus its dataset provenance description changed. Other datasets, counts, group assignments and frozen metadata/role hashes remain untouched.

Independently executed actual published group/canonical-reconciliation functions against the repository's synthetic280-video fixture. The canonical role-null to frozen assigned-role projection passes; wrong assigned role, changed native field, missing field, extra field and duplicate canonical record all fail. This validates the narrow schema correction without interpreting native role:null as a source-role assignment. It is not a private280-row recount or media replay.

Exact-final-commit GitHub checks/job HTML confirms [run39769685697](https://github.com/lathevinh/fas/actions/runs/39769685697), [validate119793807785](https://github.com/lathevinh/fas/actions/runs/39769685697/job/119793807785), head `1d420b8b6388dd172e8f0139a699e9fb3c287989`: all12 listed steps have success conclusions including Complete job. No exact API completion timestamp is asserted. This is the final handoff commit's CI, distinct from the earlier recovery-code CI.

The recovery producer/replay code remains the prior reviewed implementation; the terminal commit adds final evidence and the metadata completion checker rather than retrospectively changing the executed recovery method. The supplied final records resolve the previously pending state without rewriting the first failure or visual-pending machine fields.

## Technical and scientific assessment

The narrow output-timebase fix preserves expected RGB identities, strict exit/stderr/EOF checks and the fixed middle-frame selection. Recovery reports all268 new selected units have complete strict replay receipts; the four reused units were reconstructed from saved source pixels and copied byte-identically without reinference. Full manifest/readback and saved-pixel geometry checks support image-export completion. No additional decoder/model method search is warranted to accept that completed scope.

The eight `invalid_or_undecodable_media` outcomes must retain their exact meaning: failure of the configured strict probe/validation path. The shared helper maps several probe, timestamp, metadata or decoding failures to that generic reason. It is **not proof that eight physical files are corrupt**, nor permission to report280 usable images or replace their frames. Accepting explicit technical non-accept outcomes is consistent with the frozen original-denominator policy. Preserve available diagnostics for later debugging; this review does not commission another decode to classify the eight or delay dataset completion for that purpose.

Reported local audit verifies35 subjects, disjoint frozen21/7/7 roles and native15/20 official partitions;8 archive pins,16 volume CRC/size/SHA joins,280 video CRC reads and326 ancillary entries;zero exact duplicate groups/forbidden exact crossings. No executable from the supplied release was run. Local scientific assurance stays within these benchmark-based checks, not independent capture certification.

The additive visual receipt reports36 opened tiles:35 face crops and one explicit no-image placeholder. It does not imply36 successful crops or visual examination of272 outputs. The placeholder is correct failure accounting. No detector-failure sheet was expected because detector failures were zero; the eight pre-detector failures have no crop to inspect. Blur/exposure/glasses/tight margins are retained appearances, not grounds for replacement.

Private original videos,280-row manifest, raw authority/logs, actual crop sheets and exact CRC/hash receipts are unavailable for independent readback here. Their measured execution/visual observations remain bounded reported evidence supported by public source/receipt/CI consistency; I did not view the images or independently reproduce detector inference. The external-root validator's six-to-four status-error reduction is a reported normal validation result, not a private-root call rerun here. No predicate bypass is present in the published diff.

Resources report2282.457 seconds including diagnosis/recovery, below14400; sampled RSS373174272 bytes below4GiB; combined retained/temporary26880827017 bytes below40GiB. The authority clock was not reset at inference start. These are sampled measurements, not continuous hardware maxima. Old and new packages remain distinct; there was one failed attempt followed by one additionally approved recovery, not an unreported automatic retry.

## Next work

**Close MSU audit and primary-image export and move to CASIA-FASD using the same active-v3 detector/crop pipeline.** Keep one fixed middle frame/video as the owner currently accepts. Multiple training frames and25/75-percent sensitivity exports are separate later planned banks, not a reason to redo these primary-image milestones now.

For the supplied CASIA release, combine exact release/role/group/integrity accounting, fixed selected-frame decode, deterministic failures, full manifest/readback and bounded actual visual review in one authorized package. Use actual archive/frame/storage metadata to set its concrete CPU/time/storage scope. Reuse the pinned model and strict replay correction where compatible; test the actual decoder path rather than silently suppressing diagnostics or unnecessarily reintroducing the known timebase problem. No new detector selection or dataset-specific exploratory pilot series is requested.

If resource/acquisition authority is missing, request the one concrete combined scope with actual inputs/budget; routine code adaptation, export/readback and summary updates must not become separate approval checkpoints. A passed local audit should update CASIA's applicable statuses in the same handoff. A real failure should identify its specific cause and preserve denominators. No other dataset, target work or model scoring is implicitly authorized by this acceptance.

## Retained milestone boundaries

OULU local audit and primary selected-image exports complete. MSU local audit and280-original/272-image exports complete, with8 explicit terminal pre-detector failures. Remaining unaudited status fields: CASIA-FASD and SiW-Mv2 dataset/split fields, four total. Active-v3/model and source grouping unchanged;no model scores or fitted calibration scores. Joined assurance, optional additional image banks, features, training/OOF, analysis freeze and locked evaluation remain distinct stages; global scientific readiness is not claimed.
