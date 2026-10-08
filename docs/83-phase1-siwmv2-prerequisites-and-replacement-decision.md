# Phase 1: SiW-Mv2 Prerequisites and Replay Replacement Decision

Date: 2026-10-08
Base commit: `f064a5f5ed27bb0158932af0213046b0b8428beb`
Authority: Documents 42 and 65; owner's conditional replacement request
Checkpoint: **1.3S prerequisite inspection complete; core replacement BLOCKED**

## Decision

The owner supplied `SiW/SiW-Mv2.zip` and the official ECCV22 reference repository.
This is **SiW-Mv2**, not SiW or SiW-M. It is a plausible fourth source/target
dataset, but the evidence currently does **not** justify activating it in place
of Replay-Attack under the frozen subject-safe source-role contract.

There are two concrete blockers, beyond the normal later acquisition/media audit:

1. Four pinned Protocol I lists do not match the archive's exact video universe.
2. The supplied documents/code do not establish video-to-participant/source-face
   identity groups across videos and attack types, required for permanent source
   fitting/calibration/gate roles and subject-clustered uncertainty estimates.

Do not set `subject_id = video_id`, assign unlisted videos arbitrarily, silently
drop the mismatch, or relax grouping to force readiness. No claim is made that
the original author's subject split is wrong; its subject-level authority cannot
be reconstructed from the inspected evidence alone.

The current executable benchmark remains the four MCIO domains. This document is
a dated **conditional amendment decision**, not a new frozen benchmark activation.
The owner's request authorizes considering a replacement, not falsifying missing
metadata or automatically moving beyond a review checkpoint.

## Actual Local Evidence

Inspection uses ZIP central-directory metadata, not extracted frames or decoded
video. No target predictions or performance statistics were inspected.

| Observation | Actual result |
|---|---:|
| Archive bytes | 20,268,115,012 |
| Header members | 1,719 |
| Non-directory files | 1,702 |
| Live video headers | 785 |
| Spoof video headers | 915 |
| Total video headers | 1,700 |
| Spoof folders | 14 |
| MOV / MP4 / AVI headers | 994 / 306 / 400 |
| Documents | README.pdf and DRA.pdf |

Counts match the supplied README's 785 live and 915 spoof videos. This is not
proof of archive completeness, valid CRC/media hashes or decoding. The entire
20 GB archive has not been hashed or extracted at this prerequisite checkpoint.

The three-page local README was read in memory. Its payload SHA-256 is
`40041ad7293c594847c9512d35aa224245201c7d719826a239ec0ea19bcf581f`.
It reports 785 live videos from 493 subjects and 915 spoof videos from 600 subjects.
Thus raw video counts cannot be substituted for unique participant counts.
The private DRA was not read, copied to Git or treated as access approval.

The folder vocabulary differs from the public README in one relevant detail:
the archive uses `Spoof/Paper`, while the README's directory illustration says
`Print`. The pinned author's `dataset.py` uses the `Paper` token. The inspector
checks the explicit folder/prefix pairs against that reference; no fuzzy aliases
or folder-derived subject identities are invented.

## Pinned Protocol Reconciliation

Reference: https://github.com/CHELSEA234/Multi-domain-learning-FAS

Commit: `8667dbcd316b38141729c057adf7517fe0602608`.

Six exact source files are hash-verified: `source_SiW_Mv2/README.md`, `dataset.py`,
and the four `pro_3_text` lists below. The public report records all six hashes.
Public sources are cached outside this repository; none is executed or imported.
The original TensorFlow/face-alignment environment and preprocessing are not adopted.

| List | Rows | Unique tokens | Tokens missing from archive |
|---|---:|---:|---:|
| trainlist_live.txt | 531 | 531 | 7 |
| testlist_live.txt | 265 | 265 | 4 |
| trainlist_all.txt | 1,400 | 533 | 0 |
| testlist_all.txt | 362 | 362 | 0 |

The 867 repeated spoof training rows are balancing repetitions described by the
reference README, not 867 extra videos or independent subjects. They are counted
without treating repeated list rows as duplicate physical archive files.

- Archive live tokens: 524 listed for training, 261 for testing; all 785 are listed.
  The lists nevertheless name another **11 live tokens absent from the archive**.
- Archive spoof tokens: 533 listed for training, 362 for testing, and **20 unlisted**.
- No exact train/test video-token overlap was found. This does not prove participant
  disjointness across those tokens or across attack types.

Public evidence: [redacted prerequisite report](../results/phase1/siwmv2-prerequisites.json).
The report's header-inventory digest hashes canonical sorted paths/sizes/CRC/header
attributes; it is expressly **not** a payload SHA-256 or an integrity check.
No raw video-token list, private path, media, agreement or access credential is
included in that report.

The exact discrepancy tokens are preserved in an immutable private artifact at
`/mnt/e/FAS-private/artifacts/phase1/siwmv2-partition-discrepancies-20261008.json`.
It is outside Git and available to the owner for provider reconciliation. Public
counts above do not require publishing that per-video list.

## Implemented Checkpoint

[Inspector](../scripts/inspect_siwmv2.py) and
[focused tests](../tests/test_siwmv2.py) implement:

- exact pinned reference-byte verification;
- strict known folder/prefix grammar and rejection of unsafe paths, unknown files,
  encrypted/link/unsupported members, empty media and duplicate paths/video tokens;
- deterministic aggregate header inventory and independent live/spoof list comparison;
- explicit balancing-repeat counts without silently deduplicating into training records;
- immutable redacted JSON output, generic CLI errors and no media-payload reads;
- unconditional false subject/acquisition/media/scientific/core-activation flags.

Exit codes: **1** means an inspection report was successfully written but scientific
prerequisites remain blocked; **2** means invalid inputs/provenance/headers or output
failure. This prerequisite tool cannot return a scientific-ready success.

`/SiW` is ignored in Git. All three temporary-repository test-copy helpers also
exclude it and assert its absence, since `copytree` does not respect `.gitignore`.
The owner's original archive remains unchanged in its supplied location; private
storage relocation must precede canonical intake/extraction.

Checkpoint acceptance criteria: redacted real report reproduces the counts above;
negative fixtures fail closed; a fully reconciled synthetic video universe still
cannot claim subject/scientific readiness; no ZIP payload is read by the CLI; no
archive is tracked/copied by tests; schema/regression pass; commit/push and stop
for owner validation. Acceptance is for this tool and blocker evidence only.

Verification: [local execution summary](../results/phase1/siwmv2-prerequisite-verification.json).
No fresh remote CI success is claimed until independently observed.

Focused recheck in the existing environment:

```bash
conda run -n fas python -m unittest discover -s tests -p test_siwmv2.py -v
conda run -n fas python -m unittest discover -s tests -q
conda run -n fas python scripts/validate_preregistration.py --stage schema
```

The inspector requires a local private reference cache containing the six pinned
relative files. Use a new output filename on each run; the original public evidence
is deliberately immutable:

```bash
conda run -n fas python scripts/inspect_siwmv2.py \
   --archive SiW/SiW-Mv2.zip \
   --reference-root /mnt/e/FAS-private/reference-sources/Multi-domain-learning-FAS/8667dbcd316b38141729c057adf7517fe0602608/source_SiW_Mv2 \
   --out /tmp/fas-siwmv2-owner-review.json
```

Expected exit: 1 with a structured blocked report, not scientific-ready success.

## Conditional Benchmark Amendment

If the blockers are resolved and the owner approves the next checkpoint, a distinct
four-domain study can use **OULU-NPU, CASIA-FASD, MSU-MFSD and SiW-Mv2**. Keep
four outer targets and three sources per fold, avoiding the two-source cross-fit
problem of simply dropping Replay. It must not be called canonical MCIO or be
pooled with published MCIO results.

Before activation, freeze a new study/config identity and preserve the previous
MCIO configuration as history. Declare Protocol I membership authority, unresolved
or omitted membership handling, participant/source-identity grouping and the exact
attack scope. Full SiW-Mv2 includes makeup, partial covering and mask attacks as
well as print/replay, changing the training/evaluation distribution. Choosing only
print/replay would be a different declared subset, not an invisible compatibility fix.

Reconcile the amendment across data/protocol documents, RQ/paper wording,
configs, readiness/freeze validators, test fixtures and manifests before any model
output exists. Retain independent fixed predictors, source-only fitting, OOF controls,
three seeds, security/usability accounting and checkpoint approval discipline.
Any changed primary population/effect/aggregation contract needs an explicit
pre-target justification; do not automatically carry the MCIO claim to a new population.

SiW-Mv2 is not automatically the existing optional SiW-M zero-shot track. If used
as core source in some folds, it cannot simultaneously be described as wholly unseen
extra-domain data. No Protocol II/III result is implied by adopting Protocol I lists.

## Exact Owner Action and Resume Condition

1. Review this pushed checkpoint's inspector, tests and aggregate report.
2. Supply provider-authorized corrected Protocol I lists or release notes that
   explain the 11 missing live tokens and 20 unlisted spoof videos. A documented
   intersection/exclusion policy can be considered, but must be explicitly frozen
   and cannot be presented as exact full-release reconciliation.
3. Supply a provider-authorized video-to-participant/source-face identity mapping
   across live and attack types, or documentation establishing how equivalent safe
   grouping is obtained. An author's assertion of subject-disjoint train/test does
   not alone define our three permanent source roles inside training.
4. Keep access approval, signed agreements, release provenance and permissions in
   private intake records; do not send signatures, passwords or protected links in chat.

If these items are absent from the download, ask the SiW-Mv2 provider via the
reference's public contact (`guoxia11@msu.edu`) for the metadata and list discrepancy
explanation. The pinned lists are all under `source_SiW_Mv2/pro_3_text/`; both
release counts and observed mismatch counts are provided above for that request.

Resume with a separately reviewed amendment/metadata-adapter checkpoint once the
scope, list handling and subject grouping are established. Until then no replacement,
canonical manifest, source-role allocation, extraction, backbone inference, training
or target evaluation is authorized by this checkpoint. MSU work is not advanced.