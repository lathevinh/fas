# 97 — Review of Document 96: Canonical Manifests and Source-Role Proposal

Date: 2026-10-09  
Repository: `lathevinh/fas`  
Reviewed commit: `7c69474d3cfa99cc6a96b1b7bef5321acadc34ec`  
Reviewed document: `docs/96-phase1-canonical-manifests-and-role-proposal.md`

## Verdict

**CHECKPOINT 1.4A CANONICAL MANIFESTS — ACCEPTED.**

**ROLE POLICY PROPOSAL v1 — REQUIRES ONE REVISION BEFORE APPROVAL/FREEZE.**

No leakage blocker or canonical-population error was found. Canonical metadata export, source-pool isolation, whole-group assignment, reproducibility and inactive-policy safeguards are sound.

The role policy must not yet become executable because current stratification can leave a known source attack subtype completely absent from both `branch_calibration` and `g_domain`.

## Accepted

- Canonical populations reconcile to 7,510 videos:
  - OULU-NPU: 4,950
  - CASIA-FASD: 600
  - MSU-MFSD: 280
  - SiW-Mv2: 1,680
- Source-eligible population is 6,887 videos:
  - OULU-NPU: 4,950
  - CASIA-FASD: 600
  - MSU-MFSD: 280
  - SiW-Mv2: 1,057 train-intersection videos only
- The 623 SiW-Mv2 test-intersection videos remain outside fitting and source-role assignment.
- OULU/CASIA/MSU use subject groups; SiW-Mv2 uses video groups.
- Split seed `20261009` is separate from optimization seeds and outer-target identity.
- Initial role weights `train:branch_calibration:g_domain = 3:1:1` are reasonable.
- Deterministic whole-group assignment and byte-identical reruns are acceptable.
- The proposal remains `proposal_not_approved` and is not wired into the active experiment config.
- 14/14 focused tests and 194/194 full regression tests pass.
- Fresh CI on exact commit `7c69474d3cfa99cc6a96b1b7bef5321acadc34ec` succeeds.

Observed group allocation:

| Dataset | Train groups | Calibration groups | G-domain groups |
|---|---:|---:|---:|
| OULU-NPU | 33 | 11 | 11 |
| CASIA-FASD | 30 | 10 | 10 |
| MSU-MFSD | 21 | 7 | 7 |
| SiW-Mv2 | 632 | 213 | 212 |

## Required revision before role-policy freeze

Current stratification uses:

- `official_split`
- `binary_label`
- `attack_family`
- `sensor_id`
- `session_id`
- `environment`

but not dataset-native `reference_attack_type`.

The realized SiW-Mv2 proposal exposes a concrete hole:

| `Mask_Paper` | Count |
|---|---:|
| train | 11 |
| branch_calibration | 0 |
| g_domain | 0 |

Thus a known source attack subtype is absent from both held-out source roles.

This does not invalidate the canonical manifests, but it should be fixed before permanent role freeze because `branch_calibration` and `g_domain` are intended to characterize source-side held-out behavior.

## Required policy change

Add `reference_attack_type` to the stratification signature where available.

Recommended order:

1. `official_split`
2. `binary_label`
3. `attack_family`
4. `reference_attack_type`
5. `sensor_id`
6. `session_id`
7. `environment`

For datasets where the field is unavailable, preserve explicit `none/unknown` rather than inventing a subtype.

Create a new policy version, e.g. `role_policy_proposal_v2`, regenerate globally, and preserve the same split seed:

`20261009`

Do **not** search for a prettier seed after observing the split.

There is no requirement that every attack type must occur in every role. The requirement is only to preserve subtype information in prospective stratification, keep complete groups intact, and report the resulting coverage without post-hoc repair.

## Remaining non-accepted scientific requirements

`metadata_class_feasible = true` is only a metadata sanity condition. It does not establish:

- fitted-error sufficiency;
- gate-event sufficiency;
- stable risk-model support;
- detector-success population adequacy;
- media-content disjointness;
- media integrity or decode readiness.

Therefore the existing states:

- `fitted_error_and_gate_event_feasibility = not_evaluated_no_source_predictions`
- `content_duplicate_audit = not_verified_no_media_hashes`

should remain pending.

## Final disposition

### Accepted now
- canonical metadata construction;
- canonical/source population definitions;
- source-pool definitions;
- SiW target isolation;
- whole-group semantics;
- split-seed independence;
- 3:1:1 initial weights;
- deterministic and immutable outputs;
- inactive proposal safeguards;
- current stage gating.

### Required before policy approval/freeze
1. Add `reference_attack_type` to stratification where available.
2. Version the policy.
3. Keep split seed `20261009`.
4. Regenerate all four source-role proposals.
5. Re-run group-disjointness and reproducibility checks.
6. Publish per-role `reference_attack_type` diagnostics.
7. Keep fitted-error/event feasibility and content-duplicate audit pending.

**CHECKPOINT 1.4A CANONICAL MANIFESTS — ACCEPTED.**

**ROLE POLICY PROPOSAL v1 — REVISE BEFORE APPROVAL/FREEZE.**
