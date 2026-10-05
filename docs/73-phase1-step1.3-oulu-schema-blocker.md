# Phase 1 Step 1.3: OULU-NPU Schema Prerequisite

Authority: Document 42 and the checkpoint sequence in Document 65
Base commit: `a38950b`
Status: **BLOCKED; OULU-NPU adapter not implemented or accepted**

## Accepted prerequisite

[Document 72](72-review-phase1-step1.2-intake-contract.md) accepts checkpoint
1.2 and authorizes checkpoint 1.3. No intake rework is required. Each of the
four core adapters still requires a separate approval before proceeding.

## Observed result

The public owner pages were read for schema documentation:

- https://sites.google.com/site/oulunpudatabase/welcome
- https://sites.google.com/site/oulunpudatabase/download

They describe six mobile devices, three recording sessions, print/replay attacks,
subject-disjoint subsets and four evaluation protocols. The download page
requires an approved EULA before providing the dataset download link.

The retrieved page text did **not** establish the exact protocol-row grammar,
raw label-token values, filename-field order, identifier coding tables or file
extension rules. This is a limitation of the evidence obtained, not a claim
that those rules are absent from every public source. Public GitHub searches
also returned third-party repositories; these were not adopted as official
release authority. No dataset lists, media or protected download links were
retrieved, and no local release was inventoried.

The owner confirmed in this session that no official documentation/release is
currently available locally. Consequently no parser, label mapping, synthetic
adapter fixture or OULU audit evidence has been introduced. An inferred format
must not become a frozen scientific contract.

## Input Needed to Resume

Provide the path to an authorized official README/protocol guide outside the
repository. Documentation is the immediate prerequisite; real media are not
needed to write the first synthetic parser tests. Do not provide credentials,
protected download links or actual sample lists in chat.

The guide must establish, or be accompanied by official documentation of:

| Boundary | Required evidence |
|---|---|
| Protocol records | Encoding, delimiter, column order, header/comment/blank-line rules and video-reference syntax |
| Labels | Raw tokens and explicit bona-fide/attack semantics, including attack subtypes |
| Identity | Documented subject/video/session/sensor coding; any permitted filename parsing rule |
| Partitions | Authoritative train/development/test files and protocol/fold membership |
| Release binding | Release/protocol identity and documentation provenance to record in the private intake receipt |

Unknown optional material/environment attributes must stay `unknown`; folders
must not supply labels or partition authority. If the guide leaves a controlling
rule ambiguous, that ambiguity remains a blocker rather than a guessed default.

## Adapter Acceptance Criteria After Unblocking

- Bind the implementation to documented schema and a versioned, hashed label
  mapping; preserve raw label tokens and their official source.
- Synthetic fixtures demonstrate canonical bona-fide/attack polarity, stable
  subject/video IDs and preservation of official protocol/fold partitions.
- Reject unknown labels, malformed records, duplicate IDs within the selected
  protocol scope, unsafe paths and protocol/filesystem reconciliation failures.
- Keep selected-protocol coverage distinct from complete-release coverage;
  synthetic counts must never certify an actual release.
- Keep private record-level inventories outside Git and publish only permitted
  summaries. Do not extract training tensors or inspect target results.
- Run focused checks and regressions in existing conda env `fas`, publish actual
  results, commit/push, and stop for OULU-specific owner approval.

These are future acceptance criteria, not checks passed by this document.
Real release/media acceptance remains separately required before core data audit.

## Verification Scope

This change records the blocker and updates checkpoint status only. The existing
[checkpoint-1.2 report](../results/phase1/intake-contract-verification.json)
contains the previously verified 17 intake / 93 regression tests; it is not
OULU adapter evidence. No environment, runtime code, frozen configuration,
dataset readiness flag or scientific gate is changed.

Documentation checks: `git diff --check` passed and editor diagnostics reported
no errors in the three changed Markdown files. Python tests were not rerun for
this documentation-only change. No fresh CI result is claimed for this commit.

## Disposition

Checkpoint 1.2 is accepted. Checkpoint 1.3 begins with OULU-NPU and remains
blocked on official schema documentation. Do not mark the adapter complete or
advance to CASIA-FASD, Replay-Attack, MSU-MFSD, manifests or core audit.