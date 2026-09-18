# Stage 0 Audit Outputs

This directory stores generated, non-sensitive audit outputs. Dataset counts are not
known yet and must not be inferred from papers or guessed.

Before pilot inspection:

1. populate `manifests/dataset_summary.csv` from official downloaded metadata;
2. generate immutable subject/video role manifests per dataset;
3. populate `manifests/split_summary.csv` from those manifests;
4. record each role-manifest SHA-256;
5. run `python scripts/validate_preregistration.py --stage data`;
6. pin model bytes/environment and generate source anchor registry;
7. run `python scripts/write_freeze_record.py`, commit it, and obtain owner attestation;
8. run `python scripts/validate_preregistration.py --stage pre-pilot`.

Until the final command prints `PRE-PILOT READY`, pilot labels must remain unopened.
