# Phase 1 Step 1.3: CASIA Archive Inspection and Schema Blocker

Date: 2026-10-06
Authority: Document 42 and staged checkpoints in Document 65
Base commit: `261a8757d900bc5a2421b7a0b1ea3bc7654f4fd9`
Status: **Private storage protection verified; CASIA semantic adapter still blocked**

## New Input and Actual Finding

The owner supplied a CASIA-FASD RAR archive in `casia-fasd`. Its headers were
inspected using `rarfile==4.2` from a temporary wheel through existing conda env
`fas`, Python 3.12.14. No distribution was installed, no lock was changed, and
the utility is not a new project/runtime dependency. An initial API-name error
was corrected before the successful inspection.

All regular members reported by the reader are AVI files. No README, protocol
guide or label file is bundled in this archive. The owner confirmed that no other
official guide/label file is available locally. No video payload was extracted,
decoded, visually inspected or used to infer a label.

The public owner page was checked again for controlling schema documentation:
http://www.cbsr.ia.ac.cn/english/FaceAntiSpoofDatabases.asp

Its retrieved text describes the database design but does not establish the
filename-to-label/quality/attack mapping or subject/partition coding required
by this adapter. That is a limit of the evidence obtained, not an exhaustive
claim about all public documentation. Archive comments and their references
are not accepted as official acquisition or schema authority; no referenced
download link was used. Comments, protected references, record paths/IDs and
data counts are not published here.

The earlier [Document 76](76-phase1-step1.3-casia-schema-blocker.md) describes
the pre-upload snapshot. Video presence is now established, but the controlling
schema blocker is not resolved. A readable archive cannot authenticate its
release identity or licensing and cannot establish label semantics.

## Completed Safety Work

With explicit owner approval, the supplied directory was moved to private
storage outside the repo and a symlink retained at its original location. The
move refused an existing destination rather than overwriting data. The archive
is still present and the symlink resolves outside the repository.

The root `.gitignore` rule `/casia-fasd` covers both a directory and a symlink.
The three existing freeze/governance/preregistration test-copy helpers now
exclude CASIA as well as OULU and assert both dataset directories are absent
from temporary clones. Without these exclusions, `shutil.copytree` follows the
symlinks and can copy private archives despite `.gitignore`.

No CASIA parser, label table, protocol membership, permanent role, real audit
count or scientific readiness flag was introduced. Existing OULU approval is
unchanged. No later dataset adapter is started.

## Verification Results

| Storage-protection criterion | Actual result |
|---|---|
| Supplied archive remains available outside repo | File present; resolved root is not inside repository |
| Original path retained without adding a Git artifact | Symlink works; `git check-ignore casia-fasd` succeeds |
| Temporary test clones do not copy private datasets | Assertions pass in all three touched suites |
| Focused test suites in fas | Freeze 4, governance 10, preregistration 22; 36 tests pass |
| Full regression in fas | 110 tests pass; no new CASIA semantic test |
| Locked environment preserved | Preflight exit 0, status ready; pinned config unchanged |
| Python diagnostics | No errors reported in touched test files |

Evidence: [immutable storage verification](../results/phase1/casia-private-storage-verification.json).
This report contains code hashes and verification flags, not raw data hashes,
archive comments, protected access details or video records. These tests verify
storage isolation and existing governance, not CASIA semantic correctness.
Fresh CI for this new commit is not yet verified.

## Exact Owner Action to Unblock

**You already supplied videos; do not redownload them just to start the parser.**
The missing input is the official README/protocol guide, official label table
or a provider-authored clarification that establishes the following rules:

1. Which video filenames/codes are bona fide and which are attacks, with their
   documented attack subtype and quality coding.
2. How official train/test membership is established; any applicable protocol
   list format and mapping to media identifiers.
3. How subject IDs are defined, including whether IDs restart across train/test
   and how disjoint identities are represented without conflating equal numbers.
4. Which release the rules describe and the source/provenance of the guide.

Ask the original authorized provider or the CASIA owner using its official
contact route on the page above. Request documentation of these rules, not a
recreated label file based on visual guesses or an unconfirmed repository.

Place the response/guide outside Git alongside the private input, and send only
its local path. Do not send passwords, protected download links or signed
agreements in chat. If provider access requires an application, an authorized
person must handle the agreement/approval directly with the provider.

Once the guide establishes those controlling rules, verify its provenance,
implement the smallest parser and synthetic positive/negative tests in `fas`,
then add private inventory reconciliation and publish actual checkpoint results
for owner approval. Missing optional attributes remain unknown, but unknown
labels or essential identity/partition rules are blockers, not defaults.

Acquisition channel, approval/license, release identity and publication/use
permissions still need the checkpoint-1.2 private receipt before a real audit
can be accepted. This storage check does not authenticate an acquisition or
silently approve an unconfirmed mirror.

## Recheck Commands

```bash
git check-ignore casia-fasd
conda run -n fas python -m unittest discover -s tests -p test_freeze.py -q
conda run -n fas python -m unittest discover -s tests -p test_governance.py -q
conda run -n fas python -m unittest discover -s tests -p test_preregistration.py -q
conda run -n fas python -m unittest discover -s tests -q
conda run -n fas python scripts/check_environment.py
git diff --check
```

Do not infer semantic adapter completion from these command exits. CASIA-FASD
remains blocked on official schema authority, while private storage protection
has passed its local checks.