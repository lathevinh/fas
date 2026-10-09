# 99 — Review of Document 98: Role-Policy v2 Native-Subtype Rework

Date: 2026-10-09  
Repository: `lathevinh/fas`  
Reviewed commit: `4918b9de019f8fee70c9542f153f6b7c12e82744`  
Reviewed document: `docs/98-review-response-doc97-role-policy-v2.md`

## Verdict

**ROLE POLICY v2 — ACCEPTED FOR APPROVAL/FREEZE.**

The required correction from Review 97 has been implemented correctly and prospectively.

This acceptance applies to the permanent source-role policy itself. It does **not** certify media, fitted-error/gate-event feasibility, content-level disjointness, or full scientific readiness.

## 1. Review 97 requirement is satisfied

Policy v2 adds `reference_attack_type` to the role-allocation stratification signature:

1. `official_split`
2. `binary_label`
3. `attack_family`
4. `reference_attack_type`
5. `sensor_id`
6. `session_id`
7. `environment`

Missing/null/empty subtype metadata is represented as `unknown` for stratification and diagnostics only; no subtype is fabricated or written back into canonical records.

## 2. No seed search or post-hoc repair occurred

The split seed remains `20261009`.

The source pools remain unchanged.

The role weights remain `train : branch_calibration : g_domain = 3 : 1 : 1`.

The allocator still uses deterministic hash ordering and per-stratum largest-remainder quotas.

There is no seed retry, target-result inspection, post-hoc reassignment, group splitting, or rule requiring every subtype to appear in every role.

## 3. The concrete SiW-Mv2 defect is fixed

In policy v1, SiW-Mv2 `Mask_Paper` was:

- train: 11
- branch_calibration: 0
- g_domain: 0

Under v2 it becomes:

- train: 7
- branch_calibration: 2
- g_domain: 2

This is an observed consequence of the revised prospective stratification, not a hard-coded repair.

## 4. Canonical/source populations are unchanged

| Dataset | Canonical videos | Source videos |
|---|---:|---:|
| OULU-NPU | 4,950 | 4,950 |
| CASIA-FASD | 600 | 600 |
| MSU-MFSD | 280 | 280 |
| SiW-Mv2 | 1,680 | 1,057 |
| **Total** | **7,510** | **6,887** |

All canonical JSON and metadata CSV artifacts remain byte-identical to the accepted v1 canonical artifacts.

The 623 SiW-Mv2 Protocol-I test-intersection videos remain excluded from source-role assignment.

## 5. Group semantics remain correct

Role allocation continues to use subject groups for OULU-NPU, CASIA-FASD and MSU-MFSD, and video groups for SiW-Mv2.

No group crosses role boundaries.

Observed v2 group counts:

| Dataset | Train | Branch calibration | G-domain |
|---|---:|---:|---:|
| OULU-NPU | 33 | 11 | 11 |
| CASIA-FASD | 30 | 10 | 10 |
| MSU-MFSD | 21 | 7 | 7 |
| SiW-Mv2 | 632 | 215 | 210 |

Small changes in SiW role totals relative to v1 are expected because the semantic policy hash and strata changed.

## 6. v1 history is preserved

Verification confirms:

- all 17 v1 private artifacts remain unchanged;
- the retained v1 allocator reproduces the old v1 proposed roles;
- canonical bytes are unchanged;
- v2 outputs are generated separately.

## 7. Native-type diagnostics are now adequate

Per-role native-type counts are published for all four datasets.

For datasets with no meaningful native subtype metadata, `unknown` is explicit rather than inferred.

Bona-fide rows may appear under `none` or `unknown`, so these diagnostics must not be described as attack-only counts.

No requirement is imposed that every sparse subtype must occur in every role.

## 8. Reproducibility and tests pass

Observed verification:

- focused tests: 17/17;
- full regression: 197/197;
- zero failures/errors/skips;
- initial CLI: exit 0;
- overwrite attempt: exit 2;
- new-path rerun: exit 0;
- all generated artifact hashes identical on rerun;
- canonical joins and group disjointness pass.

Fresh CI on exact rework commit `4918b9de019f8fee70c9542f153f6b7c12e82744` completed successfully.

## 9. Policy may now be frozen before prediction-event feasibility

The source-role split should be frozen **before** looking at source prediction-error realizations.

Fitted-error and gate-event feasibility are downstream applicability checks, not criteria for selecting a nicer role split.

Therefore, after this review, policy v2 may be promoted from `proposal_not_approved` to the approved/frozen permanent role policy.

If later source-only dry runs reveal insufficient natural errors or gate events, the correct response is to apply the preregistered feasibility/applicability rules—not to retry the role seed or revise the split based on observed model outcomes.

## 10. Remaining requirements are still pending

Acceptance of policy v2 does not establish:

- sufficient fitted classifier errors;
- sufficient failure-risk training events;
- gate-event support;
- detector-success adequacy;
- media-content duplicate absence;
- media integrity;
- successful media decoding;
- acquisition/licensing verification;
- participant identity truth beyond existing metadata authority;
- scientific readiness.

The current blocked states for data audit, source dry run, analysis freeze and locked evaluation are therefore appropriate until their own requirements are satisfied.

## Required next action

Freeze policy v2 and its generated role assignments as the permanent source-role definition, preserving:

- seed `20261009`;
- source pools;
- 3:1:1 weights;
- v2 subtype-aware stratification;
- complete-group semantics;
- exact generated role hashes.

After freeze, do not change the role split in response to later source-model or target results.

Proceed to the next source-only feasibility/media-audit checkpoint according to the frozen project order.

## Final disposition

**DOCUMENT 98 — ACCEPTED.**

**ROLE POLICY v2 — ACCEPTED FOR FREEZE WITHOUT FURTHER REWORK.**

Full scientific/data readiness remains pending and must not be inferred from this acceptance.
