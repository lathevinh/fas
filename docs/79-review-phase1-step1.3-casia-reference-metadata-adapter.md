# 79 — Review of Phase 1 Step 1.3 CASIA-FASD Reference-Derived Metadata Adapter

Date: 2026-10-06
Repository: `lathevinh/fas`
Reviewed commit: `33051d219d24d8bae965d1e42e8653fc5c02e692`
Reviewed checkpoint: `docs/78-phase1-step1.3-casia-reference-metadata-adapter.md`

## Verdict

**APPROVED — CASIA-FASD reference-derived metadata adapter is accepted.**

No blocker or major issue was found that could cause incorrect binary labels, attack-family labels, subject identity conflation, train/test partition corruption, or false promotion to scientific readiness.

The next core-dataset adapter may proceed.

## Key findings

- The implementation pins Bob/Idiap reference commit `5320dac3101de913874242f56c5baa5961d2c13b`.
- The adapter independently hashes the exact controlling source files.
- The twelve CASIA filename codes match the pinned Bob reference.
- Quality mapping normal/low/high agrees with the pinned source.
- Canonical polarity remains `bona_fide=0`, `attack=1`.
- Train subjects 1-20 and test raw subjects 1-30 are preserved, with test canonical subject IDs offset by +20 exactly as in the pinned Bob implementation.
- The original Bob train/test groups are preserved; Bob cross-validation folds are explicitly not adopted.
- Unknown filename codes and malformed paths fail closed.
- Every observed subject must contain the complete twelve-code reference set.
- `--require-full-reference` compares the exact 600-path reference universe, not only counts.
- The supplied private archive passed the full-reference header reconciliation.
- RAR inspection is header-only; media payloads are not decoded or hashed.
- Acquisition, owner schema certification and scientific readiness remain explicitly false.
- Focused CASIA tests: 17 pass.
- Full regression: 127 pass.
- Fresh remote CI for exact commit `33051d219d24d8bae965d1e42e8653fc5c02e692`: completed / success.

## Provenance assessment

Using the pinned Bob/Idiap reference is acceptable for this checkpoint because the owner explicitly authorized this reference-derived route, the controlling mapping and identity logic were independently pinned and verified, the supplied archive's complete pathname universe reconciles against that reference, and the implementation never represents the mapping as CASIA-owner documentation.

This approval does **not** certify the CASIA release provenance or licensing.

## Non-blocking note

The record field `official_split` currently stores the Bob-reference train/test partition.

That does not change the result because `metadata_authority="bob-reference"`, `partition_source`, and the documentation make provenance explicit. Downstream code should preserve those provenance fields and must not reinterpret this as CASIA-owner-certified protocol evidence unless such evidence is later obtained.

## Final disposition

**CHECKPOINT 1.3 / CASIA-FASD REFERENCE-DERIVED METADATA ADAPTER — ACCEPTED**

Proceed to the next core-dataset adapter, e.g. Replay-Attack.

No CASIA metadata-adapter rework is required before continuing.
