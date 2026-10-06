# Phase 1 Step 1.3: OULU-NPU Metadata Adapter

Date: 2026-10-06
Authority: Document 42; staged approval sequence in Document 65
Base commit: `cf2f28326967b7e63eb0fc32eea8d8efbdfb2ed3`
Status: **Metadata adapter accepted in Document 75; acquisition/media audit remains pending**

[Document 75](75-review-phase1-step1.3-oulu-metadata-adapter.md) accepts this
checkpoint and confirms successful fresh CI for commit `8797a6f`. The local
implementation evidence below is retained; approval does not widen its scope.

## Scope and Source

The owner supplied the release README PDF, protocol archive, three media archives
and baseline archive. The README and protocol grammar resolve the schema blocker
recorded in [Document 73](73-phase1-step1.3-oulu-schema-blocker.md).

This checkpoint implements official metadata parsing and archive-header inventory,
not final acquisition acceptance, a complete media audit or canonical manifests.
All Python commands used existing conda env `fas`, Python 3.12.14. To read the PDF,
a temporary `pypdf==6.1.1` wheel was imported through that interpreter without
installing a distribution or changing the locked environment. The PDF reader is
not an adapter dependency. The adapter and tests use the standard library only.

No protected README, protocol list, video, landmark file, acquisition reference,
record-level inventory or actual local data hash is published by this checkpoint.
The public evidence contains synthetic counts, code hashes and verification status.

## Official Rules Used

The README defines the video identifier as `Phone_Session_User_File`, with AVI
media and a corresponding landmark text file. The supplied protocol CSVs use
the identifier stem, without an extension, and two-digit subject tokens.

- Phone: 1 through 6; session: 1 through 3; subject: 1 through 55.
- Subject ranges: training 1-20, development 21-35, testing 36-55.
- Access code: 1 bona fide, 2/3 print from printer 1/2, 4/5 replay from display 1/2.
- Train/development labels: `+1` bona fide, `-1` attack.
- Test labels: `+1` bona fide, `-1` print, `-2` replay.
- Protocols I/II have one train/development/test scope each; the supplied III/IV
  files have six camera folds, including separate `Test_i.txt` files.

The parser verifies session, attack-instrument and held-out-phone constraints
against the documented protocol rules. It rejects a raw token inconsistent with
the access code. Optional material/environment values remain `unknown`; session
and sensor identifiers are preserved separately.

The versioned mapping preserves canonical `bona_fide` / `attack`. The model-boundary
helper encodes them as 0 / 1. The mapping SHA-256 covers the label/access/instrument
tables and boundary encoding. Synthetic tests demonstrate score polarity and the
wrong-decision `error=1` contract; no trained classifier or real score is tested.

The README's Protocol-I test table contains an internally inconsistent attack
count. Its LOCO prose also says `Test.txt`, while the supplied archive has
`Test_i.txt`. The adapter does not silently adopt the inconsistent count or invent
a shared test list: official list contents, documented membership constraints
and actual archive membership are reconciled, with each observed fold preserved.

## Implementation

- [Parser/inventory](../src/fas/oulu.py): strict identifiers and labels, protocol
  scope parsing, mapping hash, safe archive members and exact scope reconciliation.
- [Private CLI](../scripts/inventory_oulu.py): explicit unverified-local mode,
  immutable private output and redacted stdout; no network or extraction.
- [Synthetic tests](../tests/test_oulu.py): parser, protocol/fold membership,
  archive omissions, path/link safety, byte hashing, output redaction and immutability.

Each video retains all official protocol/fold memberships and their raw tokens
and source files. Top-level label provenance is a deterministic representative
from those equivalent memberships, not a replacement for the full membership set.
Official splits are established from the parsed lists; storage folders only undergo
consistency checks against the documented subject rule. No source/target eligibility
or permanent training role is assigned.

The inventory requires all official protocol scopes and matching video/landmark
file identities. For every scope it compares list membership with eligible media
under the documented selector; a missing protocol row cannot hide behind another
protocol that references the same video. Full-release mode additionally checks the
complete documented identifier universe. Synthetic fixtures deliberately use a
smaller universe and cannot pass the full-release gate.

Default inventory is header-only: media byte sizes are read from tar headers and
media payloads are never opened. `media_sha256`, container/codec, duration, FPS and
frame count remain null, with `decode_status=not_probed`. Optional `--hash-media`
computes actual archive/member SHA-256 without decoding; it was validated using
synthetic bytes, not run over the real media archives. It requires two full reads
of the large media archives and must not be confused with a decode audit.

## Private Storage

With explicit owner approval, the supplied data were moved outside the repository
and a symlink was retained at the original `oulu-npu` location. All six supplied
files remain present. The root ignore rule covers both a directory and a symlink.
Three existing test-copy helpers now exclude `oulu-npu` and assert it is absent
from their temporary clones, so regression cannot copy the private archives.

The real inventory is an immutable JSON artifact outside Git. Local release and
protocol identifiers are explicitly provisional/unverified. The CLI refuses input
roots overlapping the repo, public inventory output, input/output overlap and
overwrites. Stdout does not contain video IDs, release identifiers, private paths
or data counts.

## Acceptance and Actual Results

| Metadata-checkpoint criterion | Actual result |
|---|---|
| Documented grammar and label polarity | Focused tests pass; supplied official CSV grammar parses |
| Stable subject/video/session/sensor identity | Synthetic identity assertions pass; unknown optional fields retained |
| Preserve official splits and all camera folds | Membership tests and local protocol reconciliation pass |
| Reject unknown/inconsistent labels, duplicate IDs and malformed records | Negative tests pass |
| Reconcile each protocol against media; reject missing rows/files/scopes | Synthetic negatives pass; local full-release header inventory passes |
| Do not open video payloads in header-only mode | Guarded test passes; actual run used this mode |
| Reject unsafe archive paths, links, duplicate members and escaped inputs | Negative tests pass |
| Private immutable inventory and redacted CLI | Tests pass; successful CLI 0, metadata blockers 1, input/output refusals 2 |
| Focused/full tests in fas | 17 OULU / 110 total tests, OK |
| Environment/schema remain ready | Both exit 0; locked config unchanged |
| Later scientific stages and freeze remain closed | Four stages exit 1, retired names exit 2, freeze writer 1 with record unchanged |
| Python diagnostics and whitespace | No Python diagnostics; diff check passes |

Evidence: [final immutable verification report](../results/phase1/oulu-adapter-verification-v2.json).
The final revision includes a required-file symlink-loop redaction regression;
focused/full suites were rerun after that repair. The earlier verification
snapshot is retained privately, not overwritten or published as current evidence.
Synthetic inventory has 22 videos and all 42 protocol scopes. The real run also
reconciled the documented complete release, but its counts/IDs remain in the private
artifact; publication permissions have not been verified. No target scores,
images, metrics or selection input were inspected. Fresh remote CI is not claimed
until verified for the published commit.

## Recheck Commands

```bash
conda run -n fas python -m unittest discover -s tests -p test_oulu.py -v
conda run -n fas python -m unittest discover -s tests -q
conda run -n fas python scripts/check_environment.py
conda run -n fas python scripts/validate_preregistration.py --stage schema
conda run -n fas python scripts/validate_preregistration.py --stage data-audit
git diff --check
```

For an authorized local metadata check, use the real private input directory and
a new private output path:

```bash
conda run -n fas python scripts/inventory_oulu.py \
  --input-root "$FAS_OULU_INPUT_ROOT" \
  --release-id local-upload-unverified \
  --protocol-id local-protocols-unverified \
  --unverified-local --require-full-release \
  --out "$FAS_OULU_INVENTORY_OUT"
```

CLI exit 0 means metadata reconciliation succeeded only. Reports always retain
`acquisition_verified=false` and `scientific_readiness=false`. This command does
not register a release or authorize extraction/training/publication.

## Remaining Requirements and Owner Action

This metadata checkpoint is accepted. The next adapter, CASIA-FASD, is blocked
on official schema documentation; see [Document 76](76-phase1-step1.3-casia-schema-blocker.md)
for the exact owner action needed. Phase 1 and the four-core audit are not complete.

Before real acquisition/media audit acceptance, the owner must supply the private
intake receipt and real evidence of channel, approval/license, release identity,
download date and use/publication permissions. File presence or a readable README
cannot prove those human agreements; do not send credentials or protected URLs
in chat. Use the checkpoint-1.2 receipt contract, not invented acquisition values.

Actual archive/video hashes, container/codec/duration/FPS/frame-count probing,
decode-failure accounting and verified intake lineage remain unperformed for the
real media. Canonical manifests/roles, cross-dataset leakage auditing and pinned
SSDG/FLIP sample-universe provenance remain later checkpoint work. Neither optional
datasets nor real-data readiness counts are activated by this metadata inventory.