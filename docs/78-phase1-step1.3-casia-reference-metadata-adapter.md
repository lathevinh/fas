# Phase 1 Step 1.3: CASIA-FASD Reference-Derived Metadata Adapter

Date: 2026-10-06
Authority: Document 42 and staged checkpoints in Document 65
Base commit: `1c2ed74b79211fd6b2e5626624a26cb9328a2033`
Status: **Local checks passed; CASIA-specific owner review pending**

## Decision and Provenance

After the video-only archive inspection in Document 77, the owner supplied
`183amir/bob.db.casia_fasd` as a candidate reference and authorized implementation
after its mapping and compatibility were checked. This resolves the implementation
blocker for a **reference-derived metadata adapter**, not for owner-certified
schema, acquisition authenticity or dataset licensing. No official guide has
appeared, and the reference is not relabeled as CASIA-owner documentation.

Reference repository: https://github.com/183amir/bob.db.casia_fasd

Pinned commit: `5320dac3101de913874242f56c5baa5961d2c13b`.

The controlling `db_mappings` in `bob/db/casia_fasd/__init__.py` and the type,
quality and client-ID handling in `bob/db/casia_fasd/models.py` were inspected.
Both mapping tables in the former agree. SHA-256 of the exact source bytes:

| Source | SHA-256 |
|---|---|
| `bob/db/casia_fasd/__init__.py` | `c94996cf187279c2ca2a01eba277a088de92680471ff5edcde5e0ce42026dd1d` |
| `bob/db/casia_fasd/models.py` | `270c0933d6d517e4977683f86a50e658954b05baa4967a49c13faa7639fd227a` |

The CLI verifies those local source bytes on every run without importing Bob.
The source cache is private, outside Git. No Bob sample lists or cross-validation
folds are adopted. Archive comments, protected references and access credentials
are not schema authority and are not read by this adapter.

## Mapping and Identity Contract

| Quality | Bona fide | Warped print | Cut print | Replay video |
|---|---|---|---|---|
| normal | `1` | `3` | `5` | `7` |
| low | `2` | `4` | `6` | `8` |
| high | `HR_1` | `HR_2` | `HR_3` | `HR_4` |

Canonical classes are `bona_fide=0`, `attack=1`; warped/cut map to `print`,
video to `replay`. All twelve tokens are explicitly whitelisted. Unknown stems
fail closed rather than inheriting Bob's permissive fallback behavior. Score
polarity and error supervision are unchanged.

Accepted relative paths are exactly `train_release/<subject>/<code>.avi` and
`test_release/<subject>/<code>.avi`, with unpadded decimal subjects 1..20 and
1..30 respectively. Raw subject tokens are retained. Bob's global subject
namespace uses train IDs unchanged and test IDs plus 20, avoiding conflation of
equal raw IDs across partitions. Extensionless full paths identify videos and
source records deterministically. Original train/test are preserved **as documented
by this reference**; Bob's derived dev/fold splits and permanent project roles
are not introduced. Session, sensor, material and environment remain unknown;
quality alone does not establish any of them.

## Implementation and Private Execution

- [Adapter](../src/fas/casia.py): explicit versioned mapping and canonical mapping
  hash, strict path/label parser, source-byte verifier, deterministic inventory.
- [Private CLI](../scripts/inventory_casia.py): required `--unverified-local`,
  private input/output boundaries, immutable output, generic/redacted diagnostics.
- [Synthetic tests](../tests/test_casia.py): parser, namespace, source verification,
  membership, header bridge, CLI redaction and failure cases.

The header reader is `rarfile==4.2`, loaded from a temporary wheel whose SHA-256
is `8757e1e3757e32962e229cab2432efc1f15f210823cc96ccba0f6a39d17370c9`.
Both wheel bytes and imported module origin/version are checked. It is not installed
into the locked model stack; no environment config, dependency lock or Python
version was changed. All execution used existing conda env `fas`, Python 3.12.14.

The CLI reads RAR headers with `infolist()`, never payloads, archive comments,
CRC tests or extraction APIs. It rejects unsafe/duplicate paths, unsupported
members, redirects/links, encryption, zero-byte videos, unexpected files and
incomplete observed subjects. Both reference partitions must be present. With
`--require-full-reference`, the exact reference pathname set is compared, not
just the total count. Without that flag, only complete observed subjects in both
partitions are reconciled; this is not full-release completeness.

Actual supplied archive headers passed the full-reference check and both pinned
source files were verified. The immutable inventory remains outside Git; no real
record paths, IDs, archive hash, counts or protected access details are published.
Identifiers remain provisional. Media hash, container, codec, duration, FPS and
frame count are null, with `decode_status=not_probed`. Reference compatibility
does not authenticate the archive or prove its videos decode successfully.

## Completion Criteria and Results

| Criterion | Actual result |
|---|---|
| Every reference code has explicit polarity/subtype/quality; invalid codes fail | Passed |
| Stable IDs preserve raw subject and reference train/test separation | Passed |
| Missing/duplicate/unsafe/encrypted/redirected metadata fail closed | Passed |
| Source bytes and reader wheel/import origin are pinned | Passed locally; negative synthetic checks pass |
| Partial/full synthetic memberships reconcile without importing Bob or reading media/comments | Passed; synthetic fixtures contain 24/600 records |
| Private CLI refuses overwrite/repo/input collisions and redacts failures | Passed |
| Supplied local RAR matches full reference membership | Passed, header-only private execution |
| Focused CASIA suite in fas | 17 tests, OK |
| Full regression in fas | 127 tests, OK |
| Locked environment and schema | Exit 0 each; config hash unchanged |
| Later scientific stages remain blocked | Four current stages exit 1; three retired stage names exit 2 |
| Freeze remains locked | Writer exit 1; freeze record unchanged |
| Python diagnostics | No errors reported in three implementation/test files |

Public immutable evidence:
[CASIA adapter verification](../results/phase1/casia-adapter-verification.json).
It records code/config/source hashes, observed exits and execution flags, not
protected local records. Fresh CI for the new implementation commit is **not yet
verified**; local test success is not presented as remote CI acceptance.

## Recheck and Review Boundary

```bash
conda run -n fas python -m unittest discover -s tests -p test_casia.py -v
conda run -n fas python -m unittest discover -s tests -q
conda run -n fas python scripts/check_environment.py
conda run -n fas python scripts/validate_preregistration.py --stage schema
conda run -n fas python scripts/validate_preregistration.py --stage data-audit
git diff --check
```

Tests are offline and synthetic; they need neither a RAR wheel nor private data.
To rerun the actual header inventory, use existing private archive/source-cache
paths, the exact pinned wheel, explicit unverified identifiers and a **new** private
output path. Do not overwrite the prior inventory or publish it without permission:

```bash
conda run -n fas python scripts/inventory_casia.py \
  --archive /private/data/casia.rar \
  --reader-wheel /private/tools/rarfile-4.2-py3-none-any.whl \
  --bob-source-root /private/reference/bob-pinned-source \
  --release-id steward-unverified-release \
  --protocol-id bob-reference-unverified \
  --unverified-local --require-full-reference \
  --out /private/artifacts/new-casia-inventory.json
```

CLI exit 0 means reference metadata reconciled; exit 1 means incompatible,
encrypted, unsafe or unreadable archive metadata; exit 2 means input/output or
source/reader provenance refusal. No exit certifies acquisition or scientific
readiness. `acquisition_verified`, `owner_schema_certified` and
`scientific_readiness` always remain false.

Review this checkpoint's reference choice, parser/namespace contract, private
boundaries, actual evidence and fresh CI before approving the next adapter.
**Stop here for owner confirmation; Replay-Attack/MSU are not started.**

Acquisition approval/license, release identity and use/publication permissions
still require the checkpoint-1.2 private receipt. Full media hashes/decode, four-core
audit, canonical manifests, permanent roles, feature extraction, training and target
evaluation remain pending. No audited count or readiness config was promoted.