# Phase 1 Step 1.3: MSU-MFSD Native Metadata Adapter

Date: 2026-10-09. Status: implementation and local verification complete;
owner adapter acceptance pending. The owner supplied eight ZIPs in the ignored
MSU directory and authorized continuation after
[Document 92](92-phase1-msu-mfsd-prerequisites.md). This resolves that bounded
missing-input/schema blocker, not acquisition, licensing or media audit acceptance.

## Native Authority And Packaging

The supplied ZIPs contain one outer README and all sixteen numbered volumes of
`MSU-MFSD-Publish.zip`. Total outer archive size is 11,095,264,656 bytes. A bounded,
seekable logical reader accesses the inner ZIP without materializing a joined
archive or extracting videos. Inner headers contain 280 videos, 280 face sidecars
and native metadata/helpers. No bundled executable or MATLAB code is run.

The native **inner README and official subject lists** control filename grammar,
labels and original partitions. Their exact raw-byte SHA256 pins are in the
[adapter](../src/fas/msu.py). The inner README contains a UTF-8 BOM; provenance
verification includes it before decoding any text. The outer README is separately
pinned by the [CLI](../scripts/inventory_msu.py). The two README copies differ in
title/citation wording and download/acknowledgement sections, not the controlling
schema/protocol sections; they are not incorrectly treated as byte-identical.

Authority is supplied native release documentation, not an external Bob reference,
nor independent provider certification of this copy or receipt permissions.
Original train/test lists are retained without fabricated IDs, offsets or splits.
Subjects share the native client namespace, with three-digit canonical IDs.

## Completion Criteria And Actual Results

| Criterion | Observed result |
|---|---|
| Native README and subject lists pinned as raw bytes | Pass, including README BOM and separate outer README pin |
| All split-container volumes present and unambiguous | Sixteen contiguous volumes in eight ZIPs; unsafe/duplicate/unknown entries fail closed |
| Actual population reconciles by identity, not counts alone | Every listed subject has exactly eight distinct camera/type combinations and matching sidecars |
| Stable IDs, labels and original membership | Native subject/video IDs; bona fide = 0, attack = 1; train/test subject sets disjoint |
| Versioned type/family and sensor provenance | iPad/iPhone video = replay; printed photo = print; documented camera/resolution/scenario tokens retained |
| Immutable private output and redacted report | Actual CLI exit 0; repeated output exit 2, bytes unchanged |
| No video/sidecar/helper entry access | Actual and fixture guard pass; only container volumes and bounded native text entries opened |
| Focused and full checks in existing `fas` | 18 focused tests and 180 full tests pass, no failures/errors/skips |
| Scientific gates remain blocked | Schema exit 0; data-audit, source-dry-run, analysis-freeze, locked-evaluation each exit 1 |

| Original partition | Subjects | Bona fide | Attack | Total |
|---|---:|---:|---:|---:|
| Train | 15 | 30 | 90 | 120 |
| Test | 20 | 40 | 120 | 160 |
| Total | 35 | 70 | 210 | 280 |

Each attack type has 70 videos; both Android and laptop cameras have 140 videos.
The preserved native partitions are metadata, not a newly invented source-role
allocation. The later Document 42 MSU projection uses official train+test subjects;
the SiW-Mv2-specific source-train/target-test policy is not silently applied to MSU.

## Evidence And Limitations

- [Public inventory summary](../results/phase1/msu-adapter-inventory-v1.json):
  counts, native provenance and hashes, without raw paths, subject/video IDs or
  steward release identifiers.
- [Verification record](../results/phase1/msu-adapter-verification.json): actual
  guarded CLI, overwrite rejection, exact inventory rederivation, tests/gates and
  working-tree code/config/test hashes, based on commit `15b363e`.
- [Tests](../tests/test_msu.py): polarity, strict grammar, official-list overlap,
  incomplete/replaced identity sets, sidecar pairing, raw pins/BOM, transport
  boundaries, corrupt ZIP/decompression, encryption, links, unsafe paths,
  redaction and immutable private output.

The private inventory's logical basename is `msu_metadata_inventory_v1.json`;
it stays outside Git. Exact-byte SHA256:
`9852d0b712584f3986d0de8fc5811f02ebff12fcbcd7f3921700201647f3e465`.
The inner-header fingerprint is
`5c6ae90fc3b4cee4b6d6203ae10cee0fae0c2ef73dd21a2bf58afb9a7a6f6d92`;
mapping SHA256 is
`cc59cdf60575a828ceb8a88c1b0cf0e82b237ded40c0a7492bd64512aab6f9e5`.
Git ignore and all three temporary-repository copy helpers exclude the MSU directory.
Owner archives remain in place and unchanged; no private artifacts are committed.

**Reader scope is not zero container-payload access:** seeking within outer ZIP
volume entries may decompress opaque container bytes, including compressed media
bytes. The verified guarantee is that no inner video, face sidecar or helper entry
is opened, decoded or used. No video hashes, full archive hashes, full-volume CRC
audit, face-coordinate consumption, tensors, inference or training ran. Ancillary
sidecars are checked by header identity only, not geometry or integrity.

Acquisition, archive/media integrity, media decoding, participant identity and
scientific readiness remain unverified. Actual container/codec/duration/FPS/frame
count fields remain null despite README descriptions. Roles remain unset;
canonical CSV export, ancestry and deterministic source-role allocation are later
checkpoints. Benchmark configs, frozen populations and audit summary counts do not
change because of this metadata reconciliation.

## Reproduction And Stop Boundary

```bash
conda run -n fas python -m unittest discover -s tests -p test_msu.py -v
conda run -n fas python -m unittest discover -s tests -v
conda run -n fas python scripts/validate_preregistration.py --stage schema
```

The inventory CLI requires `--archive-dir MSU`, an explicit `--release-id`,
`--unverified-local` and `--out` pointing to a new private path outside Git and
inputs. A repeated output path intentionally fails. Fresh remote CI must be checked
on the exact pushed implementation commit, not inherited from another adapter.

**Stop for owner review here.** No canonical manifests, source-role assignment,
bulk extraction, inference, training or dataset-audit readiness is authorized by
completion of this metadata checkpoint.