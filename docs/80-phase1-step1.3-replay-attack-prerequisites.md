# Phase 1 Step 1.3: Replay-Attack Prerequisites

Date: 2026-10-06
Authority: Document 42 and the checkpoint sequence in Document 65
Base commit: `21e93fe868b40c8accfd13d2ee116c5dbf905f23`
Status: **BLOCKED on local input and controlling metadata; no Replay parser implemented**

## Accepted Previous Checkpoint

[Review 79](79-review-phase1-step1.3-casia-reference-metadata-adapter.md) accepts
the CASIA reference-derived metadata adapter at exact implementation commit
`33051d219d24d8bae965d1e42e8653fc5c02e692` and confirms fresh successful remote CI.
The owner also authorized the next step. No CASIA rework is required, and its
acquisition, licensing, owner-schema and media-audit limitations remain unchanged.

The next selected adapter is **face Replay-Attack**, not MSU, manifests or training.

## Checks Performed

- Synced the owner's review using a fast-forward; the worktree was clean.
- Inspected the repository root and the existing private downloads directory.
  Only OULU and CASIA dataset locations were found there; no Replay-Attack input
  was found in these checked locations. This does not rule out another owner path.
- Read Document 42: preserve train/devel/test and controlled/adverse conditions.
  The later Track-A projection uses train+test, excluding devel; the adapter must
  not silently discard devel or substitute a new permanent split.
- Read the public provider page:
  https://www.idiap.ch/en/scientific-research/data/replayattack
- Followed that page's displayed GET DATA link:
  https://zenodo.org/records/4580204

The provider page describes face videos, disjoint train/devel/test subjects,
enrollment, lighting conditions and attack modalities. It does not provide enough
controlling filename grammar, subject coding or actual membership syntax in the
retrieved text to implement a strict parser. Its public aggregate counts are not
local acquisition or inventory evidence.

The linked Zenodo record retrieved on this date is titled **VoicePA**, describing
speaker recognition and voice presentation attacks, not the face Replay-Attack
release. Its restricted-file conditions are not adopted as Replay-Attack access
rules. Do not request or download VoicePA as a substitute. This is an observed
page/link mismatch, not a claim that the correct face dataset is unavailable.

No protected access was attempted, no files downloaded, no unofficial mirror
adopted, no guessed mapping introduced and no readiness count changed.

## Exact Owner Input Needed

1. If you already hold face Replay-Attack, provide the local path to its original
   archive(s), README/release guide and official protocol or membership files.
   Keep them outside Git, preferably under a private `replay-attack` directory.
   Do not redownload an existing authorized release merely for this checkpoint.
2. Documentation must establish filename-to-label/attack-medium rules, subject
   identity coding, original train/devel/test membership, controlled/adverse
   coding and the treatment of enrollment. The adapter will preserve documented
   metadata and leave undocumented optional fields unknown.
3. If you do not have it, contact Idiap through its official contact route and
   request the correct **face Replay-Attack** release/documentation/access channel,
   noting that the current GET DATA link resolves to VoicePA. Any authorization
   or agreement must be handled directly by an authorized person with the provider.
4. Alternatively, supply a concrete provider/Bob reference for consideration.
   Its controlling source and local compatibility must be verified and its use
   explicitly authorized before adopting a reference-derived route. The earlier
   CASIA-specific authorization does not certify an arbitrary Replay reference.

Send local paths or a public documentation/reference URL, not passwords, protected
download links or signed agreements. Acquisition provenance and use/publication
permissions remain separate checkpoint-1.2 private-receipt requirements.

## Resume and Completion Criteria

Resume parser implementation once controlling schema/membership evidence is
available, with declared authority and an owner-confirmed input location. Synthetic
parser checks can then run in existing conda env `fas`; actual reconciliation
requires the corresponding local metadata/archive headers.

The adapter's acceptance criteria will be explicit versioned labels, stable
subject/video IDs, preserved original partitions, documented environment and
attack attributes, fail-closed unknown/duplicate/unsafe records, fixture and real
metadata reconciliation, immutable private/redacted inventory, passing focused/full
tests and unchanged fail-closed scientific gates. Commit/push the implementation
and stop for a separate Replay-Attack review before MSU.

This document records the prerequisite check, **not adapter completion**. No real
Replay inventory, media audit, manifests, extraction, training or target evaluation
has run. Documentation changes are checked with the schema validator and
`git diff --check`; no new Python code or test-count claim is introduced here.