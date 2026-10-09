# Phase 1 Checkpoints and Preflight Evidence

Date: 2026-10-05
Authority: Document 42, with Document 38 supplying dependency order
Status: OULU per-video evidence accepted in Document 108; Document 109 freezes technical-failure accounting and lower-median selector with source roles unchanged; content lineage, other media audits and scientific readiness remain pending

## Approval boundary

Complete one checkpoint, publish its acceptance criteria and actual evidence,
commit and push it to GitHub, then stop for owner confirmation. A completed tool is not a completed environment or
dataset audit. Do not move to the next checkpoint automatically.

Current execution policy: all Python code, tests, validation and package installation
must use the existing conda environment `fas`. Do not use `base`, create another
environment, or change the Python version without owner approval.

No target-derived selection input is permitted. Raw data, private manifests, model
weights, and caches stay outside Git. Restricted dataset access requires the owner's
authorized local releases; no credentials or protected download links are requested
in chat.

On 2026-10-09 the owner confirms research permission for all supplied core datasets
and directs a technical, not administrative, audit workflow. Document 103 supersedes
Document 102's requirement to stage acquisition receipts before technical inspection.
Treat this as owner attestation, not independently verified agreement evidence.
Existing ignored archives may be read in place; do not migrate them automatically.
Technical integrity/decode/leakage gates and immutable roles remain mandatory.

## Checkpoint sequence

| Checkpoint | Deliverable | Acceptance criteria | Evidence to review |
|---|---|---|---|
| 0.R Prerequisite rework | Typed source evidence and explicit K=1 gate applicability | Reject empty/false evidence; gate applies only to predicted-live; focused/full suites pass; owner review and fresh CI | Document 66, approved; fresh CI success on 7775937 |
| 1.0 Preflight | Read-only runtime/lock checker and checkpoint plan | Phase-0 CI verified; positive/negative checker tests pass; real pending environment returns nonzero; no false readiness | JSON report, test counts, CI link, host observations below |
| 1.1 Environment lock | Existing conda env `fas`, approved Python 3.12 adjustment, exact package/source revisions, dependency lock and updated environment config | Recreate from lock; actual package versions match pins; required imports and CUDA synthetic tensor smoke pass; FFmpeg version recorded; regression and schema pass | Document 67 evidence; accepted by Document 69, fresh CI success on 08d29c0 |
| 1.2 Intake contract | Acquisition/protocol inventory schema and CLI | Reject missing release/license/protocol identity, changed archive hashes and unsafe paths; synthetic fixtures pass; never infer labels from folders | Document 70 evidence; accepted by Document 72, fresh CI success on e55641d |
| 1.3 Dataset adapters | Provenance-explicit metadata parser for each core dataset | Explicit label mapping; stable subject/video IDs; original partitions preserved with declared authority; unknown labels and duplicate IDs rejected; fixture counts reconcile | OULU accepted in 75; CASIA reference-derived accepted in 79, not owner-certified schema; SiW-Mv2/MSU implemented in 91/93; review 94 accepts MSU without rework and records all four adapters as accepted; fresh MSU CI success on 9355294; no real media audit acceptance |
| 1.3S SiW-Mv2 prerequisites | Safe header/list inspector and conditional replacement decision | Pinned source hashes, exact mismatch counts, no guessed subjects/splits, redacted immutable report, regression/schema pass, owner review | Document 83, accepted in Document 84; overstrict list/participant blockers corrected in Documents 85-87 |
| 1.3A Benchmark amendment | Dated new study/config, immutable exact-ID intersection, coverage and grouping policy | Preserve MCIO history; 1680 eligible videos and all-14 coverage pinned; no fake subjects or repeat weights; schema/full regression pass; later gates blocked; owner review | Document 88 and benchmark-amendment-verification.json; accepted in Document 89, clarification in Document 90; separate SiW-Mv2/MSU adapter checkpoints remain |
| 1.4 Immutable manifests/roles | Canonical manifests, source-only feasibility report and deterministic group-role builder | No subject/video/duplicate overlap; assignment independent of outer target and training seed; roles feasible; optional routing not required; rerun preserves hashes | Private local manifests, public counts/hashes, negative tests, role-policy version |
| 1.4A Metadata/proposal slice | Canonical metadata and source-role policy development | Accepted input/mapping pins, whole groups, SiW train-only, metadata-class feasibility, immutable/identical reruns, no audit promotion | Canonical accepted in 97; subtype-policy v2 rework in 98 accepted for freeze in 99; event/content audits pending |
| 1.4B Permanent role freeze | Owner-approved registry and exact permanent-role bytes | Reviewed v2 policy/role hashes unchanged; freeze before prediction errors; no reallocation; group joins and immutable reruns; no execution/readiness promotion | Document 100 accepted without rework in 101; 24 focused/204 full tests; 6887 frozen source assignments; exact b551 CI success |
| 1.5A Audit prerequisite inspection | Accepted freeze plus bounded acquisition-input inspection | Reverify exact registry/frozen hashes; missing steward receipts/permissions stay blocked; no placeholder approval or media access | Document 102; 10 staged JSON checked, zero core receipt-schema matches; 13 frozen hashes unchanged; acquisition/root inputs needed, not full audit |
| 1.5B Owner-authorized technical inspection | Frozen canonical/header/protocol reconciliation, OULU first | Owner-attested research permission; no administrative receipt requirement; exact identities/labels/partitions/roles preserved; no decoded-media readiness inference | Document 103; 4950 videos/42 protocol files and 17 focused tests pass; 105GB media TAR hash attempt stopped, hashes/decode/duplicates pending; stop before another dataset |
| 1.5C OULU archive byte pinning | Complete SHA-256 of three supplied OULU media TARs | All 105116817408 bytes read; sizes and file metadata stable; immutable private records/public aggregate; all frozen/study hashes unchanged; later gates blocked | Document 105; three complete digests, 17 focused tests pass; no individual video payload opened; stop before per-video decode/content audit |
| 1.5D OULU per-video evidence | Hash all 4950 payloads; strict full decode and frame index; exact duplicate/role reconciliation | Immutable private records, full population/size/role joins, no role or readiness promotion, publish errors/duplicates and unresolved scope | Document 107; 4949 decoded/1 failed, 13 exact duplicate pairs, zero cross-role/partition exact groups; 22 focused/209 full tests; stop for review |
| 1.5E Technical transactions/selector | Freeze scoreless failure accounting and deterministic single-frame tie rule from accepted OULU index | Original denominator retained; null classifier error; no detector/model or role rewrite; policy/code bound; exact immutable rerun | Document 109; 4949 primary identities/1 terminal failure; calibration 990 original/989 frame-available/0 fitted rows; 4952 byte-identical artifacts; 31 focused/218 full tests; stop for review |
| 1.5 Core audit | Four amended-domain intake/audit evidence bundles | Real official-release hashes and lineage verified; all four core datasets reconcile under Document 88; optional SiW-M not a core gate; no target output inspected | Public summaries, leakage audit, data-audit exit 0, full regression |

Model weights and real-data execution are not part of checkpoint 1.0. Synthetic
contract tests do not substitute for official dataset acceptance. If access is
unavailable at a dataset checkpoint, report `blocked`, not synthetic completion.
Phase 2 metrics and Phase 3 extraction remain separate later phases.

## Checkpoint 1.0 acceptance

- A matching synthetic environment passes.
- Python 3.10 and 3.13 fail; 3.11 and 3.12 pass the declared range check.
- Missing/changed packages, unpinned versions, omitted required packages, wrong
  platform/schema, and missing/changed/out-of-repository lockfiles fail.
- Current pending repository environment remains blocked, including on Python 3.12.
- The CLI emits structured JSON, returns 1 for blockers and 2 for checker/output
  failures, and refuses to overwrite a report.
- No dataset, model weight, training job, or package installation is accessed.

The checker verifies declarations, installed distribution metadata and actual lock
bytes. It does not import models, certify transitive dependency completeness, test
CUDA, or certify model/checkpoint identity. Those are checkpoint 1.1/3 acceptance
checks, not implied by this tool's `ready` status.

## Observed evidence

The following is the historical checkpoint-1.0 snapshot, not current runtime state.
Current locked-environment evidence is in Document 67; the original JSON is retained.

Base commit: `a39cac2d6b0f4e173f2b0805fe98c7569406fbd9`.

Phase-0 GitHub Actions `validate`: `completed`, `success`:
https://github.com/lathevinh/fas/actions/runs/35337658258/job/105576136358

Host observations:

- Terminal Python: 3.13.13; outside declared `>=3.11,<3.13`.
- Platform: `linux_x86_64`; matches config.
- Required model-stack distributions: not installed in that interpreter.
- Environment config: `pending_model_stack_lock`; package pins and lock identity null.
- FFmpeg: `4.4.2-0ubuntu0.22.04.1`; observed, not yet a reproducibility lock.
- `/usr/lib/wsl/lib/nvidia-smi`: RTX 4080 SUPER, driver 591.86, 16376 MiB.
  Not on the terminal PATH; this is not evidence that the GPU is absent.
- Editor-selected interpreter and CUDA tensor execution: not verified.

Machine-readable report: `results/phase1/environment-preflight.json`.
Actual preflight exit: 1, expected for the pending environment.

Validation after implementation:

- Focused environment suite: 11 tests, OK.
- Full regression: 63 tests, OK.
- Canonical validator: `SCHEMA READY`, exit 0.
- `git diff --check`: exit 0.
- Editor diagnostics for the added Python files: no errors reported.

Checkpoint 1.0 implementation passes its local acceptance checks. Environment
provisioning remains blocked/not performed; checkpoint 1.1 awaits owner confirmation.

## Recheck commands

Run from the repository root:

```bash
conda run -n fas python -m unittest discover -s tests -p test_environment.py -v
conda run -n fas python -m unittest discover -s tests -v
conda run -n fas python scripts/check_environment.py
conda run -n fas python scripts/validate_preregistration.py --stage schema
git diff --check
```

For a new immutable snapshot, choose a new output path:

```bash
conda run -n fas python scripts/check_environment.py --out /tmp/fas-environment-review.json
```

Preflight was `blocked` at checkpoint 1.0; the current locked config returns `ready`
after checkpoint 1.1. An existing output path is refused. The original checked-in
report describes checkpoint 1.0, not current runtime state; Document 67 links the
new locked preflight and CUDA evidence.

## Next approval

Checkpoint 1.1 is accepted in Document 69 and checkpoint 1.2 in Document 72.
The owner supplied OULU-NPU documentation and archives, resolving Document 73's
schema blocker. Its metadata adapter and private archive-header inventory are
accepted in Document 75. The owner subsequently authorized a pinned Bob reference
for CASIA-FASD metadata; its parser and private full-reference header inventory
passed local checks in [Document 78](78-phase1-step1.3-casia-reference-metadata-adapter.md).
CASIA-specific owner review in Document 79 accepts that adapter and confirms fresh
successful CI on exact implementation commit 33051d2. This resolves only the
reference-derived implementation checkpoint, not CASIA-owner schema certification.
Replay-Attack access remains blocked as recorded in
[Document 80](80-phase1-step1.3-replay-attack-prerequisites.md). On 2026-10-08 the
owner supplied SiW-Mv2 and authorized conditional replacement consideration.
[Document 83](83-phase1-siwmv2-prerequisites-and-replacement-decision.md) records
checkpoint 1.3S's prerequisite evidence; Document 84 accepts it. Documents 85-87
permit the prospectively frozen intersection and complete-video fallback rather
than requiring a participant map. [Document 88](88-phase1-benchmark-amendment-siwmv2.md)
implements checkpoint 1.3A's benchmark/config amendment, accepted in
[Document 89](89-review-doc88-benchmark-amendment.md). Its required evaluation-population
wording is resolved in [Document 90](90-review-response-doc89-population-clarification.md).
[Document 91](91-phase1-siwmv2-metadata-adapter.md) implements the authorized
SiW-Mv2 metadata adapter with actual private header reconciliation, redacted evidence,
27 focused tests and 162 full regression tests. Review 94's final disposition
records aggregate acceptance of the four core adapters. The owner authorized
the next step on 2026-10-09;
[Document 92](92-phase1-msu-mfsd-prerequisites.md) records the separate MSU prerequisite
inspection, initially blocked on local release and controlling metadata. The owner
then supplied eight ZIPs and authorized continuation;
[Document 93](93-phase1-msu-mfsd-metadata-adapter.md) implements native metadata
reconciliation with 18 focused / 180 full tests and private/redacted inventory.
[Document 94](94-review-doc93-msu-mfsd-metadata-adapter.md) accepts MSU without
rework; exact implementation commit 9355294 CI is independently verified successful.
[Document 95](95-review-response-doc94.md) records acceptance and retained limitations.
The owner then authorized checkpoint 1.4 implementation.
[Document 96](96-phase1-canonical-manifests-and-role-proposal.md) records the bounded
1.4A canonical metadata and source-role proposal slice.
[Review 97](97-review-doc96-canonical-manifests-role-policy.md) accepts canonical
construction, source pools, seed and initial weights, but requires native subtype
information in prospective strata before policy approval/freeze.
[Response 98](98-review-response-doc97-role-policy-v2.md) implements inactive v2,
keeps the seed/pools/weights, regenerates all four proposals and preserves v1.
[Review 99](99-review-doc98-role-policy-v2.md) accepts v2 for freeze without further
rework and clarifies that source prediction-event feasibility is downstream, not
a role-selection criterion. The owner authorizes the next step;
[Document 100](100-review-response-doc99-permanent-source-role-freeze.md) freezes
the exact accepted policy/assignments in a separate registry and private permanent
CSV bundle without reallocation. Stop for freeze checkpoint confirmation before
core audit was that checkpoint's boundary.
[Review 101](101-review-doc100-permanent-source-role-freeze.md) now accepts 1.4B
without rework; exact b551292 CI is independently confirmed successful. The owner
authorizes the next step. [Document 102](102-review-response-doc101-core-audit-prerequisites.md)
starts core audit at bounded receipt/input inspection and records a genuine missing-
steward-evidence blocker. No frozen inputs are regenerated or renamed for the minor
terminology note. That inspection's receipt prerequisite is subsequently superseded
by the owner's direct research-permission attestation and instruction to skip
administrative work, recorded in
[Document 103](103-owner-authorized-technical-audit.md). Continue technical checks
using the supplied archives and exact frozen inputs, without demanding administrative
JSON/email/license files or inventing them. Full event/content and decoded-media
obligations remain pending; this does not authorize model fitting or target evaluation.
Amendment acceptance and successful metadata reconciliation do not certify media.
The existing `fas` environment remains outside this repository.
Existing temporary-repository tests copy the working tree, so do not introduce a
large in-tree environment.

Checkpoint 1.3A aligns the readiness validator with the amended four-dataset core;
optional SiW-M is no longer mandatory. This is recorded and negatively tested in
Document 88 before any target results. Do not fabricate optional data evidence.