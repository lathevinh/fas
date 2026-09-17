# Stage 0 Audit Outputs

This directory stores generated, non-sensitive audit outputs. Dataset counts are not
known yet and must not be inferred from papers or guessed.

Before pilot inspection:

1. populate `manifests/dataset_summary.csv` from official downloaded metadata;
2. generate immutable subject/video role manifests per dataset;
3. populate `manifests/split_summary.csv` from those manifests;
4. record each role-manifest SHA-256;
5. run `python scripts/validate_preregistration.py` without the incomplete-count flag.

Until that command prints `PREREGISTRATION READY`, pilot labels must remain unopened.
