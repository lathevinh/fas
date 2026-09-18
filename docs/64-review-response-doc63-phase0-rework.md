# Response to Document 63: Phase-0 Implementation Rework

Date: 2026-09-18  
Review: `docs/63-phase0-implementation-rework-review.md`  
Authority: `docs/42-data-to-experiment-implementation-plan.md`

## Disposition

The review is accepted. All six technical findings were reproducible and have been
corrected. The missing independent CI evidence is also addressed. Phase 1 remains
locked; this rework used synthetic fixtures only and did not access any dataset,
biometric sample, model weight, target label, or target result.

## Corrections

1. **Checkpoint selection:** the canonical DINO head rule is now lowest equal-domain,
   class-balanced validation BCE with earlier epoch as tie-break. Schema validation
   rejects the former ACER rule.
2. **Source dry-run evidence:** readiness requires the exact competence and
   applicability artifact set. The validator opens each artifact, verifies its actual
   SHA-256 and source-only marker, rejects unknown or missing artifacts, and re-derives
   the hash of `configs/source_recipe_v2.yaml` as the frozen source policy.
3. **Locked authorization:** file existence no longer authorizes evaluation. A typed
   authorization must exactly match the immutable freeze bytes, commit, canonical
   experiment and claim hashes, outer targets, seeds, and `authorized` state.
4. **Transaction ledger:** the contract now requires sample/dataset/subject/video/fold
   identity, PAD/risk/gate fields, and classifier/risk/policy artifact hashes. Detector
   failures require null PAD/risk/gate values and terminal non-accept. Paired systems
   require identical cluster/fold identity and detector masks.
5. **Optional routing:** core data audit accepts an empty routing-validation partition.
   If routing records are present, their counts must still be valid and reconcile.
6. **Seeds:** schema validation pins exactly `20260917`, `20260923`, and `20261001`,
   the shared-controls flag, and the no-silent-replacement policy.
7. **Independent execution:** `.github/workflows/phase0-governance.yml` runs the full
   suite and schema on Python 3.12, verifies all unavailable stages fail closed, and
   verifies all three legacy stage names are rejected.

## Validation Evidence

Focused red-green checks reproduced each reported defect before its correction.
After all corrections:

```text
python -m unittest discover -s tests -v
52 tests, OK

python scripts/validate_preregistration.py --stage schema
SCHEMA READY
```

The release matrix must remain:

```text
data-audit=1
source-dry-run=1
analysis-freeze=1
locked-evaluation=1
data=2
pre-pilot=2
confirmatory=2
```

No production analysis-freeze or authorization record was created. GitHub Actions is
the independent check for the pushed rework commit; a green workflow is required
before treating this response as final acceptance evidence.

## Outcome

Document 63 correctly identified release blockers. They are fixed without changing
the frozen research questions, endpoints, target populations, or Phase-1 boundary.