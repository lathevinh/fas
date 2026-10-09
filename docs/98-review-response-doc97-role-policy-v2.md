# Response to Review 97: Prospective Native-Subtype Stratification

Date: 2026-10-09
Review: [Document 97](97-review-doc96-canonical-manifests-role-policy.md)
Reviewed implementation: `7c69474d3cfa99cc6a96b1b7bef5321acadc34ec`
Base for this rework: `ab1733c` (owner review upload)
Status: **canonical metadata accepted; role-policy v2 rework locally verified,
awaiting owner review before approval/freeze. Full 1.4 remains incomplete.**

## Accepted Scope And Required Rework

Review 97 accepts canonical/source populations, source pools, SiW target isolation,
whole-group semantics, separate split seed `20261009`, initial weights `3:1:1`,
determinism, immutable outputs, inactive proposal safeguards and stage gating.
These accepted choices are retained, not reopened or silently altered.

The review does not approve policy v1 for execution: its stratum signature omits
native subtype information, and actual SiW `Mask_Paper` coverage was 11 train /
0 calibration / 0 gate. This is a source-role proposal defect, not a canonical
population or target leakage defect.

Fresh CI for the exact reviewed commit was independently confirmed via its
check-run endpoint: `validate`, `completed`, `success`, completed
`2026-10-09T03:41:03Z`.
https://github.com/lathevinh/fas/actions/runs/37880373534/job/113658456544
This is not evidence of CI success for the new rework commit.

## Revision And Completion Criteria

The [v2 policy](../configs/role_policy_proposal_v2.yaml) adds native
`reference_attack_type` after `attack_family`, ahead of sensor/session/environment.
Absent/null/empty subtype is represented as `unknown` in stratification and public
diagnostics; no subtype is invented or written back into canonical records.

The [allocator](../src/fas/manifests.py) retains explicit v1 support and rejects
version/signature mismatches. Full subject/video groups remain indivisible. The
same prospective hash ordering and per-stratum largest-remainder quotas are used;
there is no retry, seed search, target inspection or post-hoc reassignment to fill
missing types. Versioning changes the semantic policy hash, so globally regenerated
role memberships may change even for datasets whose group totals are unchanged.

The [CLI](../scripts/build_manifests.py) now publishes per-role native-type counts,
including zero counts for known source types absent from a role and explicit
unknown counts. These diagnostics include bona-fide rows whose native subtype is
unknown and therefore must not be interpreted as attack-only event counts.

| Review requirement | Actual result |
|---|---|
| Add native subtype prospectively | v2 ordered signature includes `reference_attack_type`; missing stays unknown |
| Version policy, retain seed | New v2 config; seed remains `20261009`; source pools/weights/minimum unchanged |
| Regenerate globally | All four proposals rebuilt from the same pinned receipt into a new private directory |
| Complete groups and source-only populations | Exact joins/populations and group-role disjointness pass; SiW 623 test rows excluded |
| Immutable reproducibility | Actual CLI 0; overwrite 2 with bytes unchanged; new-path rerun 0, all 17 hashes identical |
| Publish native-type diagnostics | All four datasets/all three roles in new public aggregate and verification |
| Preserve scientific pending states | Prediction-error/gate-event and content-duplicate feasibility remain unverified |

## Actual Evidence

| Dataset | Canonical videos | Source videos | Train groups | Calibration groups | Gate groups |
|---|---:|---:|---:|---:|---:|
| OULU-NPU | 4950 | 4950 | 33 | 11 | 11 |
| CASIA-FASD | 600 | 600 | 30 | 10 | 10 |
| MSU-MFSD | 280 | 280 | 21 | 7 | 7 |
| SiW-Mv2 | 1680 | 1057 | 632 | 215 | 210 |

Total populations remain **7510 canonical / 6887 source videos**. All four
canonical JSON and metadata CSV pairs are byte-identical to accepted v1 artifacts.
All 17 private v1 files are unchanged, and the retained v1 allocator reproduces
the old proposed-role JSON exactly. Old configs and immutable public evidence are
preserved, not overwritten.

Actual `Mask_Paper` counts are now **7 train / 2 calibration / 2 gate**. This is an
observed consequence of prospective subtype strata and integer rounding, not a
new requirement to put every type into every role. Sparse strata may still yield
missing-role coverage; report that rather than retrying or breaking complete groups.

- [v2 aggregate report](../results/phase1/manifest-role-proposal-summary-v2.json):
  input/output hashes, role counts, native-type coverage and proposal-only states.
- [v2 verification](../results/phase1/manifest-role-proposal-verification-v2.json):
  exact joins, preserved v1 artifacts, reproduced v1 assignments, unchanged canonical
  bytes, actual overwrite/rerun, code/config/test hashes and stage results.
- [Focused tests](../tests/test_manifests.py): **17/17 pass**; native-subtype quotas,
  missing/null equivalence, input-order independence, version/signature rejection
  and existing identity/group/private-output protections.
- Full regression: **197/197 pass**, zero failures/errors/skips, in existing `fas`.
- Schema: exit 0. Data audit, source dry-run, analysis freeze and locked evaluation:
  exit 1, expected. Frozen active configs and audit summary counts remain unchanged.

Reproduction:

```bash
conda run -n fas python -m unittest discover -s tests -p test_manifests.py -v
conda run -n fas python -m unittest discover -s tests -v
conda run -n fas python scripts/validate_preregistration.py --stage schema
conda run -n fas python scripts/build_manifests.py --inputs <private-pins.json> --policy configs/role_policy_proposal_v2.yaml --out <new-private-directory>
```

Private inputs/outputs remain outside Git. The existing receipt pins are reused;
OULU/CASIA byte-pin history retains the limitations recorded in Document 96.
Neither archives nor media were accessed. No predictions, detector outputs,
extraction, inference, training or target evaluation ran.

## Stop Boundary

Policy v2 remains `proposal_not_approved`, is not wired into the active experiment
config, and keeps `policy_approved=false`, `roles_frozen_for_execution=false` and
`scientific_readiness=false`. No audited counts or executable roles are promoted.

Fitted-error sufficiency, gate-event support, risk-model support, detector-success
adequacy, media-content disjointness and media/decode integrity remain separate
pending scientific requirements. Metadata class feasibility is only a necessary
sanity condition. The role-policy rework must receive owner review before approval
or freeze; full checkpoint 1.4 is not complete. Stop here, not at core audit 1.5.
Fresh CI must be observed for the exact pushed rework commit separately.