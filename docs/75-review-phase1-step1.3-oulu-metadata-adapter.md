# 75 — Review of Phase 1 Step 1.3 OULU-NPU Metadata Adapter

Date: 2026-10-06
Repository: `lathevinh/fas`
Reviewed commit: `8797a6fd35853e0e71de2ba9dda9c34fc9d68a5a`
Reviewed checkpoint: `docs/74-phase1-step1.3-oulu-metadata-adapter.md`

## Verdict

**APPROVED — OULU-NPU metadata adapter checkpoint is complete.**

No blocker or major issue was found that could cause wrong OULU labels, wrong official split/fold membership, duplicate/missing sample identities, or accidental promotion of this metadata step into scientific-readiness status.

The next dataset adapter may proceed.

## Key findings

- Video ID grammar is strict and preserves subject, phone/sensor, session and access type.
- Canonical labels are stable: bona fide -> 0, attack -> 1.
- Train/development tokens (+1/-1) and test tokens (+1/-1/-2) are checked against access type.
- Protocol I/II and III/IV fold structures are explicitly parsed.
- Subject/session/attack-medium/camera rules are used as consistency checks, while official protocol lists remain the authoritative memberships.
- Every video keeps all protocol/fold memberships rather than collapsing them into a single rewritten role.
- Missing protocol rows, missing media, incomplete protocol scope coverage and duplicate identifiers fail closed.
- Video and landmark-file inventories must reconcile.
- Full-release mode checks the documented complete 4950-video identifier universe.
- Header-only mode does not open AVI payloads or decode media.
- Optional media SHA-256 hashing remains distinct from decode/media audit.
- Archive traversal, links, duplicate members and unsafe input paths are rejected.
- CLI output remains private/redacted and does not claim acquisition or scientific readiness.
- Focused tests: 17 pass.
- Full regression: 110 pass.
- Fresh CI for the exact implementation commit completed successfully.

## Scope note

This approval is for the **OULU metadata adapter** only.

It does not approve:
- acquisition/license lineage,
- publication permissions,
- full media hashes,
- codec/FPS/frame-count/decode audit,
- canonical manifests/roles,
- cross-dataset leakage audit,
- target evaluation.

Those remain later checkpoints.

## Final disposition

**CHECKPOINT 1.3 / OULU-NPU METADATA ADAPTER — ACCEPTED**

Proceed to the next core-dataset adapter.

No OULU metadata-adapter rework is required before continuing.
