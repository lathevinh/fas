# 294 - Review of293: SiW closure and four-dataset handoff

Date: 2026-10-23
Reviewed commit: `be12c18b046170635bd5ca2ba6901b3486a86d69`
Governing review: [292](292-review-doc291-siw-images-and-exact-crossing-resolution.md).

## Decision

**DOCUMENT293 ACCEPTED WITHOUT REWORK. Accept SiW-Mv2 local audit, primary-image preparation and effective source-use closure under the explicitly owner-adopted siwmv2-source-use-exclusions-v1 amendment. Review292 is closed. All four datasets have completed their agreed local audit and primary-image preparation milestones. Move on to source-stage integration; do not create another dataset-acceptance round or rerun the image campaigns.**

This accepts the amended effective-use population while preserving the original exact-crossing finding. It does not certify clean original boundaries, participant identity, independent scientific replication or model performance. OULU/MSU/CASIA acceptances stand. Classifier fitting, target evaluation and global scientific readiness retain their existing gates.

## Verification

Reviewed report293, adopted policy, public overlay/closure receipts, finite proposal and closure scripts, source-use context, transaction selector changes, normal validator changes and regression definitions. Exact-commit GitHub checks confirm [run39941439757](https://github.com/lathevinh/fas/actions/runs/39941439757), [validate120373566559](https://github.com/lathevinh/fas/actions/runs/39941439757/job/120373566559): all12 listed steps conclude success, including Complete job. This supplies the final implementation CI that the immutable pre-publication receipt correctly left pending collection.

Independently ran nine repository regression cases against the actual source-use and transaction modules and extracted actual proposal/duplicate functions. All passed: deterministic five-exclusion selection, independence from detector outcome, rejection of class conflicts and missing byte/sequence corroboration, preservation of source/test identities, all three consumer eligibility routes, mandatory calibration context, pending-score behavior, adoption/transaction hash failures and rehashed eligibility/partition/crossing tampering. Extraction avoided importing the private-media runtime; the two normal-validator/dry-run integration cases were not rerun locally. This is not the full producer/CI suite.

Independent public checks also passed for the exact five policy indices, effective role totals, policy/implementation/summary hashes and original-versus-effective crossing totals. Reviewed summary diff changes only SiW audit_status and its dataset provenance; original counts, frozen hashes and other datasets are unchanged. Producer-reported38 focused plus29 existing protocol tests remain separate evidence from these local checks.

Private adoption, full effective manifest, per-original records and imagery are unavailable here. Owner adoption and actual private normal-validator/consumer closure remain bounded reported evidence, supported by the reviewed bindings and tests. No private pixel replay or new visual adjudication was performed. Reusing291's committed readback and bounded visual evidence is appropriate; technical hash checks do not themselves establish image usability or independent scientific replication.

## The adopted change matches the finite proposal

The public ordinals bind five source exclusions to the original291 plan:1606 retains1642;1614 retains1653;1644 retains1623;1662 retains1654;1665 retains1663. All five excluded originals are attack-labeled detector successes. Three retain their official test partner; two retain the higher-priority source role. Fixed g_domain > branch_calibration > train priority is independent of detector outcome or model scores. The within-role pair1612/1652 stays active and disclosed under the agreed rule.

No original, role or image is removed from archival accounting. The policy and private-use artifacts bind the proposal, explicit owner adoption, governing review and original plan. The loader checks exact exclusions against adoption, retained exact-content partners, role priority, full inventory uniqueness, source/test eligibility and effective byte/full-sequence boundaries. It recomputes the active signatures; it does not hard-code a clean result.

| Population | Archived originals | Effective-use originals | Effective detector successes / failures |
|---|---:|---:|---:|
| Source train |632|628|617 /11|
| Source calibration |215|215|214 /1|
| Source g_domain |210|209|209 /0|
| All source |1057|1052|1040 /12|
| Official test, null source role |623|623|619 /4|
| All |1680|1675|1659 /16|

The five exclusions reconcile1057-5=1052 source originals and1680-5=1675 active originals. Archived785/895 bona fide/attack totals become785/890 for active use; archived1664 detector successes become1659 active successes. All16 detector failures remain retained, including12 source failures; eligible population counts are not automatically scored-fit counts. The calibration selector correctly yields zero actual fit rows while scores are absent.

Historical inventory still has six duplicate pairs and five prohibited crossings. Effective use has one allowed within-role pair and zero prohibited crossings. Nested historical/effective exact-group summaries retain their non-promoting creation semantics; final top-level local_audit_complete/protocol_use_accepted describe the separately adopted closure. That is not a claim that the historical producer ran successfully or that the original inventory became clean.

## Integration and completion boundary

SourceUseContext binds raw transaction bytes and exposes fitting/calibration/domain-use populations by permanent role. Excluded, test/null, wrong-role and mismatched-binding rows fail. The calibration selector requires context for SiW-tagged/bound rows. The normal validator requires private frozen and source-use roots, joins active eligibility to original IDs/labels/partitions/roles and detects evidence drift. Source-dry-run records using SiW must carry the adopted policy/overlay/manifest binding; freeze inputs include the policy.

These are the appropriate integration points for the present package. There is no implemented SiW classifier trainer here, so acceptance does not assert that a future arbitrary consumer is already safe. Future training code must use this context and retain the exclusions; reading archived role CSVs alone would be an implementation defect to catch in that code's tests, not a reason to reopen this completed data milestone. Historical untagged generic transaction behavior is preserved; future SiW inputs must be explicitly identified and bound.

The private normal validator reportedly returns DATA-AUDIT READY with zero errors. Both summary statuses become complete under the amendment while archived counts/hashes remain original. The final closure reuses6672 assets and291's1680 replay/readback records and108 viewed tiles by hash, with zero additional decode/inference/sheet openings. The previously executed291 transaction-contract source remains pinned to its historical Git blob; prospective selector evolution does not rewrite that execution.

## Next work: one source-stage handoff

Dataset preparation is closed for OULU-NPU, MSU-MFSD, CASIA-FASD and SiW-Mv2. Prepare the next source-stage package directly against the existing source recipe and active preprocessing contract:

1. Join prepared images, technical outcomes and permanent roles for all four datasets. Use SiW's adopted effective-use context and exact binding; retain archival and failure denominators separately from score-eligible inputs. Preserve the chosen single middle-frame policy.
2. Run the existing schema/data-audit and model-free source-consumer dry-run checks in the same integration package. Exercise SiW exclusions/null-test rejection and role boundaries end to end, report only actual remaining stage errors and fix concrete integration defects there. Reuse frozen manifests/images rather than repeating media audits.
3. Produce the concrete source-only model pilot/execution plan required by the existing stage gates: checkpoint/runtime availability, inputs, resource estimate and stop conditions together. Proceed within existing explicit authority where applicable; if fresh model execution authority is needed, request it once for that concrete package. Do not treat this review as permission to fit models, score target data or waive scientific gates.

No new image campaign, manual sheet review, participant investigation or standalone confirmation document is required to move beyond data preparation. Subsequent reviews should assess the next implemented source-stage result, not re-certify the same four datasets.

**All four local audit/image-preparation milestones are accepted. Next work is source-stage integration and its existing model-execution gates.**
