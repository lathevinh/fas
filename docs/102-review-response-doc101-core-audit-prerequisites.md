# Response to Review 101 and Checkpoint 1.5A: Core Audit Prerequisite Inspection

Date: 2026-10-09
Review: [Document 101](101-review-doc100-permanent-source-role-freeze.md)
Reviewed implementation: `b551292d66ee72913b52661fbcbc7e25fa1b666c`
Base: `4abc1f2` (owner review upload)
Status: **1.4B accepted without rework; next core audit attempted at prerequisite
inspection, blocked on unstaged steward acquisition evidence. Full 1.5 is not complete.**

## Review Disposition

Review 101 accepts assignment-preserving freeze, source populations, group integrity,
approval lineage, reproducibility, provenance preservation and blocked scientific
gates. No allocator, split, registry or benchmark rework is required. The owner
requested processing this review and proceeding to the next step.

The minor field-name note is accepted as a terminology clarification only:
`roles_frozen_for_execution=true` means **roles permanently frozen as the future
execution definition**, not permission to execute. `execution_authorized=false`
remains decisive. Keep the frozen registry bytes unchanged; use the clearer wording
in future descriptions rather than invalidating accepted provenance to rename a key.

Fresh CI for the exact reviewed freeze commit was independently confirmed:
`validate`, `completed`, `success`, completed `2026-10-09T05:49:12Z`.
https://github.com/lathevinh/fas/actions/runs/37890376816/job/113689727710
This is not a CI result for the present prerequisite handoff.

## Next-Step Scope And Local Hypothesis

The next separate checkpoint is four-core intake/media audit, using the immutable
roles and [registry](../configs/role_policy_frozen_v2.yaml), never new role generation.
Start with acquisition evidence under Document 42 sections 3-4 and the accepted
[intake contract](70-phase1-step1.2-intake-contract.md).

The local blocker hypothesis is that no complete steward receipt is staged in the
checked private acquisition locations. The metadata inventories pin sample/mapping
provenance but do not supply official acquisition channel, license/access approval,
download date, permitted uses or a complete versioned raw/protocol inventory.
Checking staged receipt fields and frozen hashes can distinguish this blocker;
opening video payloads or guessing approval from archive presence cannot.

Read-only observations so far:

- The current private data root contains `downloads/`, not a staged `agreements/`
  or versioned `raw/` tree at its top level.
- The phase-1 artifact directory contains accepted metadata inventories, population
  records and manifest input pins, not a declared complete acquisition receipt.
- Owner-provided OULU/CASIA/SiW/MSU archive locations still exist. Their presence is
  not acquisition/licensing verification. OULU has a standalone README PDF; that
  does not replace a complete receipt or access approval.
- No claim is made that agreements cannot exist elsewhere or inside archives;
  those locations have not been certified or searched by opening archive payloads.

## Completion Criteria For This Bounded Inspection

| Criterion | Required outcome |
|---|---|
| Acceptance and terminology | Record 101 acceptance; preserve registry bytes and clarify permanent definition versus execution |
| Immutable study input preflight | Verify registry, accepted review/policy/summary pins and all 13 frozen artifacts against accepted hashes |
| Receipt prerequisite check | Check private staged JSON for complete core receipts; distinguish metadata/pin records from acquisition receipts |
| Correct readiness | Missing acquisition evidence remains blocked; no audit counts or execution permission promoted |
| Reproducibility and publication | Redacted immutable inspection record, existing schema/stage checks, changed-document links and whitespace |

The inspection is not an archive-integrity, decoded-media, duplicate-content or
detector audit. No actual acquisition receipt CLI success may be claimed when no
usable steward receipt is present. Synthetic intake tests establish checker behavior
only, not official evidence authenticity or lawful uses.

Actual inspection evidence:

- [Immutable prerequisite report](../results/phase1/core-audit-prerequisites-v1.json)
  records bounded search scope, inspected JSON hashes, zero acquisition receipt-shape
  matches per core dataset, accepted registry/13-file freeze pins and stage results.
- Ten staged JSON files checked in the known private data and phase-1 artifact roots;
  zero core receipt-schema matches. This is bounded absence, not a global search.
- Registry, Review 99, allocation policy, accepted summary and all 13 frozen file
  hashes verify. All hash-bound code/config artifacts and audit summary bytes remain
  unchanged. The 6887 accepted source assignments remain immutable.
- Schema exit 0; data audit, source dry-run, analysis freeze and locked evaluation
  each exit 1, expected. No actual acquisition receipt CLI ran because no usable
  receipt was staged; no fabricated input was substituted.
- This is a documentation/read-only prerequisite turn: no Python code changes or
  full regression rerun. The accepted 24 focused / 204 full results remain historical
  freeze-checkpoint evidence, not fresh tests for this handoff.

## Inputs Needed To Resume

For each of OULU-NPU, CASIA-FASD, MSU-MFSD and SiW-Mv2, the steward must provide:

1. An explicit private receipt path and authorized data root outside the repository,
   following the [receipt template](../manifests/intake_template_v1.json).
2. Actual owner/channel/release/protocol identifiers, download date and pinned
   channel, license, access-approval, release and protocol-documentation files.
   Owner-confirmed mirrors also require the equivalence evidence record.
3. Explicit `redistribution`, `derived_frames`, `model_weights` and `metadata_counts`
   declarations, plus steward interpretation/authorization for the audit operation.
   Hash verification itself does not interpret or grant rights.
4. Original archive inventories under the receipt's `downloads/` category and a
   versioned `raw/` plus `official_protocols/` layout, or separately authorized
   private migration/controlled extraction work to create that layout. Existing
   in-repository ignored archives are not moved or duplicated automatically.

Do not fabricate absent channel/license/approval evidence, infer permission from a
public reference, or label placeholders `complete`. Missing native release/schema
authority must remain explicit, especially for reference-derived CASIA metadata.
Private documents, protected URLs and credentials stay out of Git and chat.

Resume with one dataset's explicit authorized receipt/root at a time: validate
acquisition evidence, then separately perform authorized archive/media checks and
reconcile to the frozen canonical/role hashes. Do not switch datasets automatically
or combine evidence acceptance with model execution.

## Stop Boundary

Preserve all frozen roles, seed, source pools, weights, canonical populations and
historical proposal evidence. No media opened/decoded, archives extracted/moved,
fresh roles generated, audit summaries populated, predictions/inference/training
run or target outputs inspected in this inspection.

**Blocked pending steward acquisition inputs/authorization.** Publish this acceptance
response and prerequisite handoff; do not call full 1.5 or scientific readiness
complete. Fitted-error/gate-event feasibility remains downstream applicability and
cannot be used to revise these permanent roles.