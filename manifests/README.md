# Manifest Evidence Contract

Tracked summary files contain only aggregate, non-sensitive counts and SHA-256 values.
Restricted row-level evidence remains under ignored `manifests/private/`.

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

## Permanent role manifest

One file per dataset: `<dataset_slug>_roles.csv`.

```text
dataset,subject_id,video_id,binary_label,role
```

Roles are `train`, `branch_calibration`, `g_domain`, `routing_validation`, and
`g_attack`. A subject may occur in only one role. `g_domain` applies to MICO datasets;
`g_attack` applies to SiW-M. The validator recomputes role counts, detects overlap, and
checks each private file against the tracked summary hash.

Run `conda run -n fas python scripts/validate_preregistration.py --stage data-audit` after populating the
private files. Images and biometric data must never be committed.
