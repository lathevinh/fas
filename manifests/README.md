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

Run `conda run -n fas python scripts/validate_preregistration.py --stage data-audit` after populating the
private files. Images and biometric data must never be committed.
