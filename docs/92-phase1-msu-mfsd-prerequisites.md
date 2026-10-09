# Phase 1 Step 1.3: MSU-MFSD Prerequisites

Date: 2026-10-09
Authority: Document 42, amended by Document 88, and checkpoint sequence in Document 65
Base commit: `10c16093ca6343a2309c05f5a43167cb60b7535b`
Status: **BLOCKED on local release and controlling metadata; no MSU adapter implemented**

Update 2026-10-09: the owner supplied all eight MSU ZIPs and authorized continuation.
[Document 93](93-phase1-msu-mfsd-metadata-adapter.md) records the native metadata
adapter and resolves this prerequisite blocker. The original checks below are
historical, not the current input status; media/acquisition readiness is unchanged.

## Transition And Checks

The owner's "next step" authorizes moving from the completed
[SiW-Mv2 metadata implementation](91-phase1-siwmv2-metadata-adapter.md) to this
separate MSU prerequisite checkpoint. No new review document was found on remote
main. Execution permission does not certify acquisition, media or scientific
readiness, and no formal review acceptance is inferred from an absent document.

The exact SiW-Mv2 implementation commit's GitHub Actions `validate` check was
observed as `in_progress`, conclusion null, when preparing this checkpoint:
https://github.com/lathevinh/fas/actions/runs/37868497123/job/113620833974
This is not a claim of fresh CI success. Document 91's local 27/162 test evidence
remains historical evidence for that implementation, not a new test run here.

Checks performed:

- Fetched origin; local/remote main match the base commit and the worktree was clean.
- Inspected the repository root: existing dataset locations are OULU, CASIA and SiW;
  no MSU release location was found there.
- Inspected the existing private data directory and its downloads directory: only
  OULU/CASIA download directories were present, with no MSU input found.
- Inspected the private reference-source directory: it contains the accepted CASIA
  and SiW-Mv2 reference caches, not an authorized MSU reference.
- Read the governing checkpoint rules and Document 42's MSU metadata requirement.
  Subject/video identity must be verified; the later Track-A projection uses subjects
  in official train and test lists. Preserve original membership rather than guessing
  a new split or using the projection as a substitute for release documentation.
- Checked the tracked intake template: it is a pending OULU example, not an MSU
  acquisition/protocol receipt.

This is a bounded local-location check, not a claim that no MSU release exists
elsewhere on the owner's machine. No archive headers or payloads were available to
reconcile. No dataset was downloaded, extracted or viewed, no external reference
was adopted, and no model inference/training or package/environment change ran.

## Owner Input Needed

1. Supply the local path to the authorized original **MSU-MFSD** archive(s) or release
   directory, preferably outside Git. Do not redownload an existing release merely
   for this checkpoint.
2. Supply its README/release guide and official train/test subject or video lists.
   Controlling evidence must establish filename-to-label rules, subject/video identity
   coding, partition membership and any documented attack-medium or capture-device
   attributes. Undocumented optional attributes will remain unknown.
3. If official documentation is unavailable, supply a concrete public provider/Bob
   reference for consideration and explicitly authorize a reference-derived route.
   Its controlling bytes/revision and compatibility with the local release must be
   checked before adoption. CASIA/SiW-specific reference authorization does not certify
   an arbitrary MSU source.
4. Acquisition identity, licensing and use/publication permissions remain separate
   private intake-receipt obligations. Send local paths or public documentation URLs,
   not credentials, protected download URLs or signed agreements in chat.

## Resume And Completion Criteria

Resume once the owner identifies the release location and controlling schema/list
authority. Metadata adapter implementation must then establish explicit versioned
label polarity, stable subject/video IDs, original partition provenance, strict
unsafe/unknown/duplicate rejection and unknown optional fields without fabrication.
Actual archive/list reconciliation and immutable private/redacted evidence are
required; synthetic tests alone do not certify the local release.

All code and validation must use the existing conda environment `fas`. Publish
focused/full test results, schema and fail-closed readiness checks with code/config
lineage, then commit/push and stop for a separate MSU adapter review. This document
completes only the prerequisite inspection, not the adapter or dataset audit.

For this documentation-only checkpoint, validate changed links, run the schema
validator and `git diff --check`; no new Python implementation or full-regression
test-count claim is introduced. Benchmark configs, frozen populations and audit
summaries stay unchanged. **Stop here for the missing input; do not start manifests,
role assignment, extraction, inference or training.**

Observed local validation: schema reports `SCHEMA READY`, exit 0 in `fas`;
all changed-document links resolve; `git diff --check` exits 0. No full regression
suite was rerun for this documentation-only prerequisite record.