# Phase 1: SiW-Mv2 metadata adapter

Date: 2026-10-09. Status: implementation and local verification complete;
owner acceptance pending. This is the authorized metadata checkpoint following
[review 89](89-review-doc88-benchmark-amendment.md) and the
[population clarification](90-review-response-doc89-population-clarification.md).

## Scope and authority

The adapter consumes the already accepted Protocol-I intersection, not a new
population definition. It verifies the exact private membership bytes, six pinned
reference files and the complete ZIP central-directory fingerprint before
normalizing metadata. Reference authority remains the upstream commit
`8667dbcd316b38141729c057adf7517fe0602608`; this is reference-derived project
metadata, not provider certification of acquisition or participant identities.

- [Adapter](../src/fas/siwmv2.py): strict path/membership parser, versioned mapping,
  pinned provenance verification and archive-header reconciliation.
- [Private inventory CLI](../scripts/inventory_siwmv2.py): immutable output outside
  Git and redacted stdout. Exit 0 means reconciled metadata only; exit 1 means
  incompatible/unsafe archive metadata; exit 2 means invalid input, provenance or
  output. Existing files are never overwritten.
- [Tests](../tests/test_siwmv2.py): 11 retained prerequisite tests and 16 new adapter
  tests. The earlier inspection CLI now imports the same reference constants;
  its historical reports and frozen population bytes remain unchanged.

## Completion Criteria And Results

| Criterion | Observed result |
|---|---|
| Exact accepted population and header fingerprint, not counts alone | Pass on actual supplied ZIP; all six reference files match pins |
| Source/test eligibility remains disjoint and exact | 1057 train-intersection; 623 test-intersection |
| Label polarity and mapping provenance are explicit | bona fide = 0, attack = 1; canonical mapping hash verified |
| Missing/excluded records do not become transactions or failures | 20 observed out-of-protocol videos excluded; 11 absent references separate |
| No fabricated participant/role/media fields | Subjects null; video groups; roles unset; media fields unprobed |
| Private immutable inventory and public aggregate report | Actual CLI exit 0; second write exit 2 with original bytes unchanged |
| Safety and header-only behavior | Unsafe paths, aliases, duplicates, symlinks, encryption, wrong file kinds, empty entries, changed headers/pins and corrupt ZIP rejected |
| Focused/full regression and readiness gates in `fas` | 27/27 focused; 162/162 full; schema 0; four later stages 1 |

Actual normalized population:

| Partition | Bona fide | Attack | Total |
|---|---:|---:|---:|
| Source-eligible train | 524 | 533 | 1057 |
| Target-eligible test | 261 | 362 | 623 |
| Combined inventory, not target population | 785 | 895 | 1680 |

All 14 reference attack types occur in both partitions, with exact counts matching
the frozen coverage report. They remain distinct from the five operational project
families; the mapping does not claim a provider-native family ontology. Repeated
training-list tokens do not create additional groups, transactions or weights.

For OCM->S, **all SiW-Mv2 samples are excluded from fitting, calibration, gate
selection and method selection; evaluation includes only the 623 test-intersection
videos**. The 1057 train-intersection videos are source eligible only when SiW-Mv2
is a source domain. Combined 1680 is never the target population.

## Evidence And Privacy

Public evidence contains aggregates, policy and hashes, not raw paths, release IDs
or exact video tokens:

- [Actual inventory summary](../results/phase1/siwmv2-adapter-inventory-v1.json).
- [Verification record](../results/phase1/siwmv2-adapter-verification.json), binding
  working-tree code/config/test hashes to base commit `0c4b305` and executed checks.
- [Previously frozen population](../results/phase1/siwmv2-intersection-v1.json).

The private inventory's logical basename is `siwmv2_metadata_inventory_v1.json`;
it remains outside Git. Its exact-byte SHA256 is
`6d105949c6f626dae750ce1a0f22b0a5bf8a85de8b77a9eec4929b7137761d60`.
Accepted membership SHA256 remains
`47ca2bb8896d5937ff7ea735242dd410f83f8a65e6b5655a6709ef2b4e1fb3ae`;
header fingerprint remains
`2e08944154d49e531d727bd3320e798690e8b8ba144780153bbab857b5fb4582`.
Mapping SHA256 is
`09329456b68587ca2e8bec0ba97247625d024d9ac53a1fb3b80a11a3af0b827f`.

After the final adapter change, actual inventory bytes were reconstructed exactly
with `ZipFile.open` forbidden. This checks central-directory-only behavior, not
payload integrity: header CRC is recorded but never recomputed against media.
No archive extraction, full-archive SHA, video payload read, decoder, inference or
training ran. Acquisition, integrity, decoding, participant identity and scientific
readiness flags remain false. Codec, duration, FPS, frame count and media SHA are
unknown. Canonical CSV export, source-role allocation and derived ancestry are
later checkpoints; this adapter does not claim to enforce their downstream groups.
Complete-video grouping remains required at all six frozen boundaries, with the
participant-dependence limitation retained.

## Reproduction And Stop Boundary

Run code only in the existing environment:

```bash
conda run -n fas python -m unittest discover -s tests -p test_siwmv2.py -v
conda run -n fas python -m unittest discover -s tests -v
conda run -n fas python scripts/validate_preregistration.py --stage schema
```

The inventory CLI additionally requires the private archive, pinned reference
directory, accepted private membership file, explicit steward release ID,
`--unverified-local` and a new private output path. Reusing the completed inventory
path intentionally fails. The verification record includes the four later stage
exit codes; no readiness counts, audit summaries or benchmark configs changed.

Fresh GitHub CI must be observed on the exact pushed implementation commit;
previous amendment CI is not evidence for this adapter. Owner review should verify
the criteria above against the linked artifacts and code. **Stop here pending
adapter acceptance: no MSU adapter, extraction, inference or training is started.**