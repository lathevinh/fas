# Phase 1 Step 1.3: CASIA-FASD Schema Prerequisite

Date: 2026-10-06
Authority: Document 42 and the checkpoint sequence in Document 65
Base commit: `d332210`
Status: **BLOCKED; CASIA-FASD adapter not implemented or accepted**

Update: the owner subsequently supplied a video-only archive. Its inspection and
storage protection are recorded in [Document 77](77-phase1-step1.3-casia-archive-schema-check.md).
The earlier observations below describe the pre-upload snapshot; official schema
documentation is still missing, so the semantic adapter remains blocked.

## Accepted Prerequisite

[Document 75](75-review-phase1-step1.3-oulu-metadata-adapter.md) accepts the
OULU-NPU metadata adapter and authorizes the next core-dataset adapter. That
review confirms fresh successful CI for implementation commit
`8797a6fd35853e0e71de2ba9dda9c34fc9d68a5a`. No OULU metadata rework is required.
Its acquisition/media-audit limitations remain unchanged.

The next selected checkpoint is CASIA-FASD, not manifests, extraction or training.

## What Was Checked

- Checked the workspace root and the current private download directory; neither
  contains a CASIA-FASD release/documentation folder.
- Searched the existing references for a CASIA schema source; none was found.
- Read the public owner page:
  http://www.cbsr.ia.ac.cn/english/FaceAntiSpoofDatabases.asp
- Asked whether official documentation/release exists at another local location;
  the owner confirmed it is not currently available.

The owner page describes quality levels, warped-photo/cut-photo/video attacks,
evaluation scenarios and an agreement-based application/download procedure.
The retrieved text does not establish exact release filename-to-label mappings,
subject/video coding or authoritative train/test record syntax. This is a limit
of the evidence obtained, not a claim that no other public source exists.

Public database descriptions are not local release audit evidence. No media,
protected download link, sample list or target output was retrieved. No parser
or synthetic fixture was created using remembered or third-party label rules.

## Why This Blocks Implementation

The adapter must preserve official labels, subjects, partitions and documented
quality/attack-medium identifiers. A guessed video-number mapping can silently
invert bona-fide/attack labels; a guessed partition or subject convention can
break the official evaluation population or identity separation. Folder names
alone cannot supply that authority.

## Exact Owner Action Needed

1. Obtain the official README/protocol guide from the CASIA-FASD provider. If
   access is required, use the owner page above: download/sign the agreement and
   submit it through the provider's submission channel. Signing and access
   approval must be handled by an authorized person, not this assistant.
2. After approval, obtain the documentation/release through the authorized owner
   channel. Provider availability and approval timing have not been verified;
   if the application site is unavailable, request the guide through the owner's
   official contact route rather than using an unconfirmed mirror.
3. Store the documentation/archives outside the repository, for example in
   `/mnt/e/FAS-private/data/downloads/casia-fasd`. The full video release is not
   needed for the first synthetic parser tests; the official guide is sufficient
   if it fully specifies the controlling schema.
4. Send only the local path in chat. Do not send credentials, protected download
   links, signed agreements or sample-list contents in chat or public Git.

## Condition to Resume

The supplied official documentation must establish:

| Boundary | Required information |
|---|---|
| Video identity | Filename/path grammar, video-number meaning and subject coding |
| Labels | Explicit bona-fide/attack mapping and documented attack subtypes |
| Partitions | Official train/test membership authority and any protocol/list grammar |
| Optional attributes | Official quality and attack-medium coding; unresolved attributes remain unknown |
| Release binding | Documentation provenance and release/protocol identity, without invented acquisition claims |

Once those rules are verified, implement the smallest parser slice, run synthetic
positive/negative tests in existing conda env `fas`, add private inventory checks,
publish acceptance criteria/results, commit/push and stop for CASIA-specific
approval. If a rule is still missing, name that exact rule and the question the
owner needs to ask the provider.

Future acceptance requires canonical `bona_fide=0` / `attack=1`, preserved official
partitions and stable identities, versioned label mapping, rejection of unknown
labels/duplicates/malformed records, and protocol/filesystem reconciliation.
Those criteria are not passed by this document.

## Verification Scope and Disposition

This change records acceptance and a prerequisite blocker only. No runtime code,
environment, frozen configuration, audit count or scientific gate is changed.
The prior 17 OULU / 110 regression tests and CI belong to the accepted OULU
checkpoint, not CASIA validation. Python tests are not rerun for this
documentation-only change.

CASIA-FASD remains blocked until the documentation path is supplied and its schema
is verified. Do not mark the adapter complete or silently skip to another dataset.