# Manifest Evidence Contract

Tracked summary files contain only aggregate, non-sensitive counts and SHA-256 values.
Restricted row-level evidence remains under ignored `manifests/private/`.

The 2026-10-08 [benchmark amendment](../docs/88-phase1-benchmark-amendment-siwmv2.md)
defines four active core datasets. Summaries now declare `group_unit` and group
counts separately from `subjects`; all actual counts remain unaudited. SiW-M is
optional, distinct from core SiW-Mv2, and not a mandatory readiness row.

## Acquisition receipt

[intake_template_v1.json](intake_template_v1.json) defines the version-1 acquisition
and protocol-file inventory fields. Its null hashes and pending status intentionally
block verification. Completed receipts and acquisition evidence must remain in
authorized private roots outside the repository, not in this directory.

Use `conda run -n fas python scripts/check_intake.py --receipt <private-receipt>
--data-root <private-root> --out <new-report-outside-data-root>` for a redacted
immutable report. See [checkpoint 1.2](../docs/70-phase1-step1.2-intake-contract.md)
for schema, exit codes, permissions and acceptance evidence. This does not parse
media inventories or populate the existing data-audit summaries below.

## Per-video metadata

One file per dataset: `<dataset_slug>_metadata.csv`.

```text
dataset,subject_id,video_id,binary_label,attack_family,official_split
```

Each `(subject_id, video_id)` is unique. `binary_label` is `bona_fide` or `attack`.
The validator derives subject, bona-fide video, attack-video, and attack-family counts
and reconciles them with `dataset_summary.csv`.

For SiW-Mv2 the metadata columns are instead:

```text
dataset,subject_id,video_id,binary_label,attack_family,official_split,reference_attack_type,attack_mapping_version
```

Its `subject_id` and subject count remain empty, `group_unit` is `video`, and groups
are complete videos. The type/family mapping version is `siwmv2_attack_family_v1`;
live rows have empty type/family. IDs, partition counts and type coverage must match
the frozen intersection evidence exactly. The external immutable exact-ID population
record is not a canonical adapter manifest or audited release.

## Permanent role manifest

One file per dataset: `<dataset_slug>_roles.csv`.

```text
dataset,subject_id,video_id,binary_label,role
```

Roles are `train`, `branch_calibration`, `g_domain`, `routing_validation`, and
`g_attack`. A declared group may occur in only one role. `g_domain` applies to all
four amended core datasets; optional `g_attack` belongs to the separate SiW-M track.
The validator recomputes group counts, detects overlap and checks private file hashes.
SiW-Mv2 source roles may contain only its 1057 reference-train intersection videos,
never its reference-test videos. Group fallback applies at every boundary listed in
the amendment, not just this permanent-role manifest.

## Metadata-Only Proposal Export

[Checkpoint 1.4A](../docs/96-phase1-canonical-manifests-and-role-proposal.md) provides
rich canonical JSON and exact metadata CSV projections outside Git. Its separate
`*_roles_proposed.csv` files are unapproved proposals, not the active audited
`*_roles.csv` evidence above. The explicit proposed policy is not referenced by the
active experiment config. Do not copy these files into readiness evidence or mark
summary rows complete merely because the proposal CLI returns 0. Metadata-class
feasibility is not fitted-error/gate-event feasibility or media-content duplicate
verification; all later scientific gates remain blocked.

[Review 97](../docs/97-review-doc96-canonical-manifests-role-policy.md) accepts
canonical metadata but requires subtype-aware role stratification. The
[v2 rework](../docs/98-review-response-doc97-role-policy-v2.md) retains v1 artifacts,
uses the same split seed and source pools, and adds `reference_attack_type` with
explicit unknown handling. All four proposals are regenerated, with per-role type
counts reported; no all-types-per-role guarantee or post-hoc repair is imposed.
At Document 98's checkpoint the proposal was inactive/unapproved.

## Approved Permanent Source Roles

[Review 99](../docs/99-review-doc98-role-policy-v2.md) accepts v2 for freeze without
further rework. [Checkpoint 1.4B](../docs/100-review-response-doc99-permanent-source-role-freeze.md)
promotes the exact accepted assignments through a separate
[frozen registry](../configs/role_policy_frozen_v2.yaml). Historical proposal bytes
and their semantic policy hash remain unchanged; changing proposal state and rerunning
allocation is not the promotion mechanism.

The private frozen bundle contains exact canonical/metadata bytes, permanent
`*_roles.csv` byte-identical to the accepted proposal CSVs, and a last-written
`source_role_freeze.json` marker. Freeze mode checks pinned review/policy/summary and
all accepted artifacts, rejects changed bytes, and does not call the allocator.
Use `--freeze-bundle`, `--approval`, `--policy` and `--out` with the existing builder.
Input/output row-level artifacts remain outside Git; future analysis artifact hashes
include the approved registry and allocation policy.

Roles are frozen before source prediction errors. Later natural-error/gate-event
applicability cannot be used to retry the seed or select a nicer split. This does
not verify content duplicates, media integrity, detector adequacy or scientific
readiness, and does not authorize execution. Permanent files are not yet installed
as audited evidence here, and dataset/split summary counts remain unchanged.
Later audit must reconcile against these exact permanent assignments, not rebuild them.

[Review 101](../docs/101-review-doc100-permanent-source-role-freeze.md) accepts this
freeze without rework. Interpret the retained `roles_frozen_for_execution` key as
"roles permanently frozen as the future execution definition", not permission to
execute; the registry's `execution_authorized=false` remains decisive. Keep the
accepted registry bytes unchanged rather than renaming a provenance-bound field.
[Core-audit prerequisite inspection](../docs/102-review-response-doc101-core-audit-prerequisites.md)
is blocked on unstaged steward acquisition evidence. Archive presence and accepted
metadata/role hashes do not establish channel/license/access approval or decode
readiness, and cannot populate audit summaries.

Run `conda run -n fas python scripts/validate_preregistration.py --stage data-audit` after populating the
private files. Images and biometric data must never be committed.
