# Phase 1 Checkpoint 1.4A: Canonical Metadata And Role Proposal

Date: 2026-10-09. Status: canonical metadata export and proposal tooling locally
verified; owner review/policy approval pending. **Full checkpoint 1.4 is not yet
complete.** The owner authorized the next step after
[review 94](94-review-doc93-msu-mfsd-metadata-adapter.md) and
[response 95](95-review-response-doc94.md).

## Scope And Decisions For Review

There was no preregistered permanent-role policy, initial fractions or split seed
in the existing configs. The three optimization seeds must not silently become
split seeds. The [explicit proposal](../configs/role_policy_proposal_v1.yaml)
therefore remains `proposal_not_approved`, is not referenced by the active experiment
config, and cannot freeze executable roles in this builder.

Proposed choices, requiring review before adoption:

- Track B only; source pools are all native train/development/test for OULU,
  train+test for CASIA/MSU, and the already frozen train intersection for SiW-Mv2.
  The OULU development inclusion is an explicit proposed Track-B choice, not an
  inferred SSDG/Track-A membership rule. No Track-A manifests are built here.
- One separate split seed, `20261009`, shared across datasets and independent of
  optimization seeds and outer targets.
- Initial group weights `train:branch_calibration:g_domain = 3:1:1`; these are
  candidate starting weights, not frozen universal percentages. Optional routing
  and SiW-M attack-gate roles are not activated.
- Stratify whole subject/video groups by official partition, class, attack family,
  sensor/session and environment profile. Use deterministic hash ordering within
  strata and integer largest-remainder quotas, with fixed role-order ties.
  Preserve native OULU protocol memberships in canonical records; exact per-native-
  protocol/fold balancing is not claimed. Do not split a group to repair imbalance.
- The minimum of one video of each class per role is only a necessary metadata
  sanity check. It is **not** a preregistered model-error/event sufficiency threshold.
  No retry or target-dependent policy selection is performed.

Review should accept/revise these choices globally before freezing source roles;
this record does not amend the active frozen method by itself.

## Implementation And Completion Criteria

The [canonicalizer/allocator](../src/fas/manifests.py) verifies inventory bytes,
accepted adapter mapping bodies/hashes, labels, stable IDs, required video fields,
null SiW subjects and source/test flags. The [CLI](../scripts/build_manifests.py)
requires explicit private input pins and policy. It exports outside Git:

- Rich per-dataset canonical JSON retaining native provenance and unknown media
  fields; exact minimal metadata CSV projections for the existing validator.
- Per-dataset proposed-role JSON and CSV, distinct from active audited role files.
- A final aggregate bundle marker written only after all outputs succeed.

Existing outputs are refused; partial write failure never creates the completion
marker. Inputs, outputs and receipt paths must be separate private locations.

| Criterion for this limited checkpoint | Actual result |
|---|---|
| Canonical metadata from four accepted inventories | 7510 videos; fields/mapping provenance preserved |
| Source-only proposal with complete-group assignments | 6887 source-eligible videos; no subject/video group crosses roles |
| SiW held-out population isolation | Only 1057 train videos get proposed roles; 623 test videos stay out |
| CSV joins/schema/null subject encoding | Pass; roles join canonical records; SiW CSV subjects empty |
| Immutable and reproducible artifact bytes | Existing output exit 2; new output rerun exit 0; all 17 file hashes identical |
| Focused/full regression in existing `fas` | 14/14 focused; 194/194 full; zero failures/errors/skips |
| Scientific stages unchanged | Schema exit 0; all four later stages exit 1 |

| Dataset | Canonical videos | Source videos | Source groups | Train groups | Calibration groups | Gate groups |
|---|---:|---:|---:|---:|---:|---:|
| OULU-NPU | 4950 | 4950 | 55 subjects | 33 | 11 | 11 |
| CASIA-FASD | 600 | 600 | 50 subjects | 30 | 10 | 10 |
| MSU-MFSD | 280 | 280 | 35 subjects | 21 | 7 | 7 |
| SiW-Mv2 | 1680 | 1057 | 1057 videos | 632 | 213 | 212 |

Every dataset has both classes in all three proposed roles. Actual weights can
differ slightly after per-stratum integer rounding. Type/family coverage is
diagnostic, not an all-types-per-role event gate. For OCM->S, all SiW samples still
stay out of fitting/selection; target evaluation remains the 623-test population,
not the 1680-row canonical inventory.

## Evidence And Unfinished Requirements

- [Aggregate bundle report](../results/phase1/manifest-role-proposal-summary-v1.json):
  input/canonical/CSV/proposal hashes, class/group counts and family coverage.
- [Verification](../results/phase1/manifest-role-proposal-verification.json):
  actual joins, rerun/overwrite, CSV schema, reference-type diagnostics, test/gate
  results and code/config/test lineage based on `8375977`.
- [Tests](../tests/test_manifests.py): input pin drift, mapping body drift, unsafe
  paths/IDs, group cuts, hidden target/optimization-seed policy keys, undersized
  source pools, redaction, private boundaries and partial/immutable outputs.

MSU/SiW input bytes match their previously accepted public inventory pins.
Historical OULU/CASIA reports did not record exact private inventory byte hashes;
their existing accepted cache snapshots are newly byte-pinned here, and mapping
bodies/hashes are checked against accepted adapters. This is not retroactive
cryptographic certification by those earlier reports.

Private receipt, canonical records and proposed roles remain outside Git. Neither
raw archives nor media were accessed; no predictions, detector outputs, tensors,
inference or training ran. No audited summary counts are populated.

Still pending: owner approval of source pools/seed/weights, fitted-error and
conditional gate-event feasibility, content-duplicate audit using verified media
hashes, and final executable-role freeze. Metadata groups disjoint by identity do
not prove media-content disjointness. Archive/acquisition/media/participant truth
and scientific readiness remain unverified. Changing policy requires a new
version/output and a global source-only check before any outer-target evaluation.

## Reproduction And Stop Boundary

```bash
conda run -n fas python -m unittest discover -s tests -p test_manifests.py -v
conda run -n fas python -m unittest discover -s tests -v
conda run -n fas python scripts/validate_preregistration.py --stage schema
```

The bundle CLI takes `--inputs <private-pins.json>`,
`--policy configs/role_policy_proposal_v1.yaml`, and `--out <new-private-directory>`.
Exit 0 means metadata/proposal export only, never policy approval or data readiness.
Fresh CI must be checked on this exact pushed implementation commit.

**Stop for owner review of 1.4A.** Do not mark full 1.4 complete, activate proposed
roles, start core audit/bulk extraction, or run inference/training/target evaluation.