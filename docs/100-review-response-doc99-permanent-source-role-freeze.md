# Response to Review 99 and Checkpoint 1.4B: Permanent Source-Role Freeze

Date: 2026-10-09
Review: [Document 99](99-review-doc98-role-policy-v2.md)
Reviewed implementation: `4918b9de019f8fee70c9542f153f6b7c12e82744`
Base for this checkpoint: `ed10dea` (owner review upload)
Status: **policy v2 accepted for freeze; permanent-role freeze implemented and
locally verified. Await checkpoint review, not another policy-selection pass.**

## Acceptance And Execution Order

Document 99 accepts policy v2 without further rework and authorizes freezing the
reviewed assignments before observing source prediction errors. The owner then
requested the next step. This checkpoint performs that freeze only; it does not
combine it with media audit or model execution.

The split seed remains `20261009`, source pools and `3:1:1` weights are unchanged,
and native-subtype stratification preserves complete groups. Later natural-error,
gate-event or risk-model support checks apply the preregistered applicability rules;
they must not trigger a nicer seed, policy revision or post-hoc role reassignment.
Any future exceptional protocol change requires explicit prospective owner review,
not an automatic response to model or target results.

Fresh CI on the exact reviewed v2 implementation was independently confirmed:
`validate`, `completed`, `success`, completed `2026-10-09T04:29:37Z`.
https://github.com/lathevinh/fas/actions/runs/37884110245/job/113670150765
This does not assert CI success for the new freeze implementation commit.

## Freeze Design

The [authoritative registry](../configs/role_policy_frozen_v2.yaml) records owner
review bytes/SHA, reviewed commit, allocation-policy bytes/SHA, accepted summary
bytes/SHA and all 17 accepted proposal-bundle artifact hashes. Its scope is solely
the permanent Track-B source-role definition, not an analysis freeze or execution
authorization. It is included with the allocation-policy file in future
[analysis artifact lineage](../src/fas/preregistration.py).

The [freeze-record builder](../src/fas/manifests.py) and
[CLI freeze mode](../scripts/build_manifests.py) do not invoke the allocator.
Changing the allocation-policy `state` before reallocation would change its semantic
hash and possibly the assignments. Instead, the unchanged proposal config and
historical proposal JSON remain provenance; a separate registry promotes their
exact accepted assignments. The nested historical `proposal_not_approved` value is
not the current approval status: authority comes from the registry's outer
`approved_frozen` state and Review 99.

The private frozen bundle contains 13 files: four unchanged canonical JSON files,
four unchanged metadata CSV files, four permanent `*_roles.csv` files copied
byte-for-byte from accepted `*_roles_proposed.csv`, and `source_role_freeze.json` as
the final completion marker. Its receipt bytes equal the tracked registry bytes.
No rich historical role JSON is rewritten with contradictory approval flags.

Public approval references must resolve inside the repository and match their
pins; proposals and frozen row-level outputs stay outside Git in separate private
roots. Existing outputs and symlink artifacts are rejected. All validation happens
before output creation; a write failure cannot publish a completion marker.

## Completion Criteria And Actual Results

| Criterion | Actual result |
|---|---|
| Freeze accepted policy and assignments, no reallocation | All reviewed role CSV hashes preserved exactly; no allocator/model-outcome input |
| Preserve canonical/source populations | 7510 canonical / 6887 source videos; accepted canonical/metadata bytes unchanged |
| Complete-group joins and SiW target exclusion | Pass; SiW roles contain only 1057 train rows, not 623 test rows |
| Preserve proposal history | All v1 and v2 private proposal artifacts unchanged; public proposal evidence/configs unchanged |
| Immutable and reproducible freeze export | Actual CLI 0; overwrite 2 with original bytes unchanged; new-path rerun 0; all 13 hashes identical |
| Negative and lineage checks | Altered policy/summary/review/artifact/scope rejected; no allocator invocation; registry/allocation bytes bind future analysis lineage |
| Regression in existing `fas` | 24/24 focused; 204/204 full; zero failures/errors/skips |
| No scientific-readiness promotion | Schema 0; data audit, source dry-run, analysis freeze and locked evaluation each exit 1 |

| Dataset | Frozen source videos | Train groups | Calibration groups | Gate groups |
|---|---:|---:|---:|---:|
| OULU-NPU | 4950 | 33 | 11 | 11 |
| CASIA-FASD | 600 | 30 | 10 | 10 |
| MSU-MFSD | 280 | 21 | 7 | 7 |
| SiW-Mv2 | 1057 | 632 | 215 | 210 |

`Mask_Paper` remains 7 train / 2 calibration / 2 gate. Native-type diagnostics
remain those in the [accepted v2 report](../results/phase1/manifest-role-proposal-summary-v2.json),
including bona-fide `none`/`unknown` rows, not attack-event counts.
There is still no all-types-per-role requirement.

[New immutable verification](../results/phase1/source-role-freeze-verification-v2.json)
records approval lineage, exact accepted/frozen artifact hashes, actual joins,
overwrite/rerun, population/group counts, tests, stage gates and code/config hashes.
[Focused tests](../tests/test_manifests.py) include synthetic owner-approval fixtures;
those fixtures do not substitute for the actual pinned Review 99 export.

Reproduction:

```bash
conda run -n fas python -m unittest discover -s tests -p test_manifests.py -v
conda run -n fas python -m unittest discover -s tests -v
conda run -n fas python scripts/validate_preregistration.py --stage schema
conda run -n fas python scripts/build_manifests.py --freeze-bundle <accepted-private-v2-bundle> --policy configs/role_policy_proposal_v2.yaml --approval configs/role_policy_frozen_v2.yaml --out <new-private-root-directory>
```

## Remaining Requirements And Stop Boundary

The permanent-role registry sets `policy_approved=true` and
`roles_frozen_for_execution=true`, but **`execution_authorized=false`**,
`media_audit_verified=false` and `scientific_readiness=false`. Freeze CLI exit 0
means an exact approved-role export, not a successful data audit or permission to
fit a model. Frozen files are not installed as audited `manifests/private` evidence,
and audit summary counts remain untouched.

No archives/media were accessed, no detector/predictions were run, and no bulk
extraction, inference, training or target evaluation occurred. Active experiment,
benchmark, source recipe and optimization seeds are unchanged. Only the new role
registry and its future artifact-lineage hook are added.

Full 1.4 feasibility/content-disjointness obligations and overall scientific/data
readiness remain pending. The next separate checkpoint follows the frozen order:
core intake/media audit (1.5); fitted-error/gate-event applicability is evaluated
only when authorized source predictions exist, never to select this role split.
Audit evidence must use and reconcile the permanent role files/registry rather
than generating fresh roles. No target model outputs may be inspected.

**Stop for owner confirmation of 1.4B before starting the separate audit checkpoint.**
Fresh CI must be checked on the exact pushed freeze implementation commit.