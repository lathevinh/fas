# 101 — Review of Document 100: Permanent Source-Role Freeze

Date: 2026-10-09  
Repository: `lathevinh/fas`  
Reviewed commit: `b551292d66ee72913b52661fbcbc7e25fa1b666c`  
Reviewed document: `docs/100-review-response-doc99-permanent-source-role-freeze.md`

## Verdict

**CHECKPOINT 1.4B — ACCEPTED.**

The accepted v2 source-role assignments have been frozen without reallocation, without seed search, without model-output inspection, and without promoting scientific/data readiness.

No blocker or major methodological issue was found.

## 1. Freeze is assignment-preserving

The freeze implementation does not invoke the role allocator.

The permanent role CSV files are copied byte-for-byte from the already reviewed v2 proposed-role CSV files.

The accepted assignment hashes are preserved exactly:

- CASIA-FASD roles: `289fd009...`
- MSU-MFSD roles: `57b2ff24...`
- OULU-NPU roles: `ed415897...`
- SiW-Mv2 roles: `a3cc84b6...`

This is the correct behavior after Review 99. The freeze checkpoint promotes already-reviewed assignments; it does not generate a new split.

## 2. Policy-selection variables are unchanged

The permanent registry preserves:

- split seed `20261009`;
- source pools;
- initial weights `3:1:1`;
- v2 subtype-aware stratification;
- complete subject/video groups;
- exact reviewed commit and approval lineage.

No later model result may trigger a nicer seed, new role split, or post-hoc reassignment.

## 3. Source populations remain correct

Frozen source videos remain:

| Dataset | Frozen source videos |
|---|---:|
| OULU-NPU | 4,950 |
| CASIA-FASD | 600 |
| MSU-MFSD | 280 |
| SiW-Mv2 | 1,057 |
| **Total** | **6,887** |

The SiW-Mv2 623-video target/test population remains excluded from all source roles.

Frozen group counts remain:

| Dataset | Train | Branch calibration | G-domain |
|---|---:|---:|---:|
| OULU-NPU | 33 | 11 | 11 |
| CASIA-FASD | 30 | 10 | 10 |
| MSU-MFSD | 21 | 7 | 7 |
| SiW-Mv2 | 632 | 215 | 210 |

The previously reviewed SiW-Mv2 `Mask_Paper` distribution remains 7 / 2 / 2.

## 4. Canonical and proposal history is preserved

The freeze keeps:

- accepted canonical JSON bytes unchanged;
- accepted metadata CSV bytes unchanged;
- all v1 proposal artifacts unchanged;
- all v2 proposal artifacts unchanged;
- the original v2 policy file unchanged.

This is good provenance practice.

The implementation correctly avoids editing `proposal_not_approved` inside the historical allocation-policy file, because changing the policy body would alter its semantic hash and could invalidate the exact reviewed split.

Instead, a separate authoritative registry records current approval state.

## 5. Approval registry design is sound

`configs/role_policy_frozen_v2.yaml` binds:

- Review 99 bytes/hash;
- reviewed commit;
- allocation-policy file/hash;
- accepted summary file/hash;
- accepted proposal artifact hashes;
- final frozen artifact hashes.

The registry scope is explicitly limited to the permanent source-role definition.

It does not claim analysis freeze, media readiness or model-execution authorization.

This separation is methodologically cleaner than rewriting historical proposal artifacts with new approval flags.

## 6. Reproducibility and negative checks pass

Verification reports:

- focused tests: 24/24;
- full regression: 204/204;
- zero failures/errors/skips;
- freeze CLI: exit 0;
- overwrite attempt: exit 2;
- new-path rerun: exit 0;
- all 13 frozen artifact hashes identical on rerun;
- canonical-role joins pass;
- group disjointness passes;
- accepted assignment hashes preserved.

The freeze record also explicitly reports that no allocator seed search, post-hoc repair, model outcome, training or target evaluation was used.

## 7. Fresh CI passes

Fresh GitHub Actions for exact freeze commit:

`b551292d66ee72913b52661fbcbc7e25fa1b666c`

completed successfully.

Therefore the checkpoint is not relying on CI from the earlier policy-v2 commit.

## 8. Scientific gates remain correctly blocked

The freeze registry sets:

- `policy_approved = true`;
- permanent roles frozen;
- `execution_authorized = false`;
- `media_audit_verified = false`;
- `scientific_readiness = false`.

Stage results remain:

- schema: pass;
- data-audit: blocked;
- source-dry-run: blocked;
- analysis-freeze: blocked;
- locked-evaluation: blocked.

This is correct.

Freezing the role split before observing source prediction errors protects the study from later split tuning.

## 9. Minor terminology note

The field:

`roles_frozen_for_execution = true`

can be misread because the same registry also says:

`execution_authorized = false`.

The current implementation is not scientifically wrong because Document 100 explicitly defines the distinction: roles are frozen as the future execution definition, while execution itself is still unauthorized.

For future schemas/paper-facing descriptions, clearer naming would be something like:

- `roles_permanently_frozen = true`, or
- `roles_frozen_as_execution_definition = true`.

This is a **minor clarity issue only**, not a checkpoint blocker, and it does not require changing the frozen registry if doing so would disturb provenance.

## 10. Remaining requirements

Checkpoint 1.4B acceptance does not establish:

- acquisition/license verification;
- archive/media integrity;
- decode success;
- content-level duplicate absence;
- detector-success adequacy;
- fitted-error sufficiency;
- gate-event support;
- risk-model support;
- target evaluation authorization;
- scientific readiness.

These remain downstream obligations.

The frozen split must not be revised if those later checks reveal poor model behavior. Feasibility/applicability rules must handle such outcomes.

## Final disposition

**DOCUMENT 100 — ACCEPTED.**

**CHECKPOINT 1.4B PERMANENT SOURCE-ROLE FREEZE — ACCEPTED WITHOUT REWORK.**

The frozen v2 role assignments should now be treated as immutable study inputs.

Proceed to the separate core intake/media audit checkpoint using these exact frozen role files and registry. No fresh role generation is permitted.
