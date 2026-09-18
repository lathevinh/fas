# Manifest Evidence Contract

Tracked summary files contain only aggregate, non-sensitive counts and SHA-256 values.
Restricted row-level evidence remains under ignored `manifests/private/`.

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

Run `python scripts/validate_preregistration.py --stage data` after populating the
private files. Images and biometric data must never be committed.
