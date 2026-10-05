# Phase 1.2: Acquisition Receipt and Protocol-File Inventory Contract

Date: 2026-10-05
Authority: Document 42, sections 3-4; checkpoint plan in Document 65
Status: implemented and locally verified; awaiting owner confirmation before 1.3

## Entry and scope

[Document 69](69-review-phase1-step1.1-environment-lock.md) accepts checkpoint 1.1,
including successful fresh CI for `08d29c0`. The owner authorized this next step.
All execution used existing conda env `fas`, Python 3.12.14. No dependencies,
environment locks, model choices, dataset summaries or scientific gates changed.

This checkpoint implements acquisition/protocol-file receipt validation, not dataset
adapters or media inventories. It reads declared agreement/archive/protocol bytes
for SHA-256 without extracting archives, opening undeclared media, decoding tensors,
inferring labels/splits, downloading data, or contacting protected URLs.

## Deliverables

- [Validator](../src/fas/intake.py)
- [Read-only CLI](../scripts/check_intake.py)
- [Public pending template](../manifests/intake_template_v1.json)
- [Synthetic tests](../tests/test_intake.py)
- [Immutable verification evidence](../results/phase1/intake-contract-verification.json)

The template is not a completed receipt. Real receipts, official references,
agreements and raw data stay in an authorized private root outside the repository.
The CLI refuses repository-contained receipt inputs, including the public template;
test its pending contents through the synthetic suite or a private receipt instance.

## Version-1 schema

The exact top-level fields are:

| Field | Contract |
|---|---|
| version | Integer 1, not Boolean/float |
| status | `complete` required to verify; template is `pending` |
| dataset | Four canonical MCIO names; optional SiW-M/CelebA-Spoof recognized without activating them |
| release_id, protocol_id | Explicit nonempty steward identifiers; never derived from a folder |
| owner, channel_reference | Nonempty private acquisition provenance references |
| channel | `official`, `owner_designated`, or `owner_confirmed_mirror` |
| downloaded_on | Canonical ISO calendar date `YYYY-MM-DD` |
| permissions | Exactly redistribution, derived_frames, model_weights, metadata_counts |
| evidence | Exactly channel, license, access_approval, release, protocol_documentation |
| raw_root | Existing contained relative directory under `raw/` |
| archives | Nonempty inventory of original archive records under `downloads/` |
| protocols | Nonempty inventory of protocol records under raw_root/official_protocols |

Each artifact record contains exactly `id`, `relpath`, `sha256`: nonempty ID,
canonical POSIX relative path, and lowercase SHA-256 of actual nonempty file bytes.
Missing/unreadable files and mismatched hashes block. Archive/protocol inventories
reject duplicate IDs, duplicate relative paths, and aliases resolving to the same
file. Paths reject absolute forms, drive syntax, backslashes, traversal, empty/dot
components, control characters, symlink escape and symlink loops. The private root
must not overlap the repository in either direction.

Mirror acquisition additionally requires a hashed `mirror_equivalence` evidence
record from the owner. An unconfirmed unofficial mirror cannot verify. The tool
checks the record's declared identity and bytes, not the authenticity of its author.

Permission values are `allowed`, `prohibited` or `unknown`; missing categories and
Boolean shortcuts are rejected. Restrictive/unknown permissions do not prevent
read-only evidence/hash verification, and a verified result never grants extraction,
redistribution, publication or training rights. A data steward must interpret the
agreement and resolve the permissions required for each downstream operation.

## CLI and public report

Run only after the steward has an authorized local release and private receipt:

```bash
conda run -n fas python scripts/check_intake.py \
  --receipt "$FAS_DATA_ROOT/agreements/intake-receipt-v1.json" \
  --data-root "$FAS_DATA_ROOT" \
  --out "$FAS_RUN_ROOT/intake-check-v1.json"
```

Public output contains only schema version, verified/blocked status, field-local
errors, scope and `no_media_decoding`. It excludes receipt content, dataset/release
identifiers, private paths, protected references, agreement text and sample counts.
Errors do not echo user-provided values. Preserve the private receipt separately
for dataset-specific lineage; this redacted status report is not a provenance manifest.

Exit 0 means declared acquisition evidence/hashes verify; exit 1 means blockers;
exit 2 means input/output errors, a repository receipt, a private-input output path,
or refused overwrite. `--out` creates a new immutable record. It cannot overwrite
inputs or create a report inside the data root. The CLI performs no network access.

## Acceptance and actual results

| Acceptance criterion | Actual result |
|---|---|
| Complete synthetic receipt verifies without media | CLI 0; status verified |
| Missing identity/license/protocol evidence, wrong types, pending/unknown fields reject | Negative tests pass |
| Changed archive/protocol bytes or fabricated/missing hash reject | Negative tests pass; changed-archive CLI 1 |
| Unconfirmed mirror and absent equivalence reject | Negative tests pass |
| Unsafe paths, root overlap, symlink escape/loop and duplicate aliases reject | Negative tests pass |
| No folder-derived label/split and no media reading/decoding | No parser/decoder; guarded-media test passes |
| Report redaction and immutable writes | Tests pass; overwrite/input collision returns 2 |
| Pending public template cannot stand in for acquisition | Private template instance CLI 1; status blocked |
| Focused/full tests in fas | 17 / 93 tests, OK |
| Environment/schema remain ready | Both exit 0 |
| Unavailable scientific stages remain closed | Four current stages exit 1; retired names exit 2 |
| Freeze writer does not create/change a record | Exit 1; unchanged |
| Whitespace and Python diagnostics | Diff check passes; no diagnostics |

```bash
conda run -n fas python -m unittest discover -s tests -p test_intake.py -v
conda run -n fas python -m unittest discover -s tests -q
conda run -n fas python scripts/check_environment.py
conda run -n fas python scripts/validate_preregistration.py --stage schema
conda run -n fas python scripts/validate_preregistration.py --stage data-audit
git diff --check
```

Data-audit remains exit 1. No real release was acquired or accepted. This checkpoint
does not certify official document authenticity, completeness of undeclared release
parts, read-only permissions across the whole raw tree, official protocol semantics,
label mappings, subject/video identities, decoding, manifests or leakage audits.
Those remain adapter/audit responsibilities in checkpoints 1.3-1.5. No real labels,
samples, target statistics or training inputs were inspected.

Owner confirmation is required before separately implementing each dataset adapter
in 1.3. Fresh remote CI is a distinct check after publishing this checkpoint; the
Step-1.1 review is not reused as validation of these new files.