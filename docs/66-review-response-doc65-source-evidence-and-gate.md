# Phase-0 Prerequisite Rework: Source Evidence and Gate Applicability

Date: 2026-10-05
Review: `docs/65-review-phase0-after-doc64.md`
Authority: Document 42
Base commit: `c035fbe`
Status: local checks passed; awaiting owner review and fresh CI before Phase 1.1

## Scope and disposition

Both technical blockers are confirmed and repaired. The old green CI run proved
test execution, not the correctness of the two missing contracts. Prior statements
that Phase 0 was fully accepted were premature.

This checkpoint changes source-evidence validation and K=1 gate applicability only.
No dataset, biometric sample, model weight, target output, package installation, or
environment version change was used. All Python execution and validation used the
existing conda environment `fas`.

## Source-evidence contract

`evidence.json` still requires the exact competence/applicability artifact set,
actual SHA-256 reconciliation, frozen policy hash and source-only lineage markers.
Those checks are now followed by typed content validation. A correctly hashed
`{"version":1,"no_target_selection_input":true}` is insufficient.

Both artifacts require integer schema version 1, the true source-only marker, and
12 records: each of the four outer-target exclusions paired with each frozen seed.
Each record contains:

| Field | Contract |
|---|---|
| `outer_target` | One of four MCIO domains; exclusion identity, not target evidence |
| `seed` | Exactly one of 20260917, 20260923, 20261001 |
| `source_domains` | Exactly the other three domains, no duplicates or outer target |

Missing, duplicate, replacement-seed or target-inclusive records fail closed.

### Competence

Each record's `systems` contains exactly `dino_reg`, `openclip`, `heterogeneous`
and `same_family`. Each system requires finite numeric `macro_auroc`,
`macro_balanced_accuracy`, `macro_auroc_lcb` in [0,1], nonnegative finite
`score_range`, and Boolean `finite_scores`, `both_classes`, `finite_calibration`,
and `pass`.

The validator re-derives `pass`: AUROC and balanced accuracy >=0.55, AUROC LCB
>0.50, score range >1e-6, and all three validity flags true. An asserted `pass=true`
cannot override weaker metrics or invalid flags.

`dino_anchor_pass` must match the shared DINO's finite, nonconstant, both-class,
finite-calibration predicate, independently of its standalone competence threshold.
`heterogeneous_risk_fit` requires nonnegative integer `error_count`, `correct_count`
and a Boolean `pass` matching both counts >=20. Booleans are not counts.

Source readiness requires the heterogeneous complete system, shared DINO anchor
and heterogeneous risk-fit support for every fold/seed. A weak standalone branch
does not block core readiness when those predicates pass. A weak same-family
complete system scopes RQ2 to `not_applicable`; it does not invalidate eligible RQ1.

### Applicability

The top-level artifact fixes `n_error_min=20` and
`target_event_support="not_inspected"`. Each record requires:

- `claims`: exactly RQ1 and RQ2, with `eligible` or `not_applicable` re-derived from
  the associated competence record, not an asserted scientific outcome.
- `source_events`: exactly the three non-target domains. Each contains integer
  error/correct counts and Boolean `ap_estimable` and `meets_n_error_min`.
- AP estimability requires both error and correct events. Event support requires
  estimability and at least 20 errors. The recorded flags must match those rules.
- Domain counts must sum to the associated heterogeneous reference source-OOF
  risk-fit counts. Inconsistent totals are rejected even with correct file hashes.

Low-event and one-class source slices are retained with their actual support flags,
not deleted or assigned fabricated AP. These are source diagnostics; they do not
establish target event eligibility, target AP, or final RQ1/RQ2 outcomes. The frozen
three-seed/four-target evaluation rules remain unchanged.

The complete synthetic payload is exercised by
`tests/test_preregistration.py::_write_source_evidence`. It is a temporary fixture,
not production evidence. The validator checks typed values and declarations; it does
not recompute source AUROC/LCBs from model predictions in this phase.

## Gate applicability

The ledger uses null rather than a new action enum for an inapplicable gate:

| State | Gate fields | Final K=1 action |
|---|---|---|
| Detector failure | PAD/risk/gate fields null, transaction retained | `non_accept` |
| Predicted attack | Finite PAD/risk fields; `gate_threshold=null`, `gate_action=null` | `non_accept` |
| Predicted bona fide | Finite gate threshold; `gate_action=accept` or `non_accept` | Must equal `gate_action` |

Already-spoof decisions cannot be represented as gate interventions. They remain
detector-successful observations in the risk-ranking population, and detector
failures still remain in original end-to-end denominators. Gate nullability does not
alter RQ2 transaction pairing or detector-mask identity.

## Acceptance evidence

Before the fix, tests reproduced two accepted empty artifacts and three gate defects.
After the fix, all checks below ran in `fas`:

| Check | Actual result |
|---|---|
| Preregistration suite | 22 tests, OK; includes 25 invalid science/lineage mutations |
| Contracts suite | 21 tests, OK |
| Full regression | 75 tests, OK |
| Schema CLI | Exit 0, `SCHEMA READY` |
| Data-audit / source-dry-run / analysis-freeze / locked-evaluation | Exit 1 each, fail closed |
| Legacy data / pre-pilot / confirmatory | Exit 2 each |
| Freeze writer | Exit 1; no production record created |
| Environment preflight | Exit 1, blocked |
| Whitespace check | `git diff --check`, exit 0 |
| Editor diagnostics in touched Python files | No errors reported |

Correctly hashed empty artifacts are rejected at source-dry-run, analysis-freeze
and locked-evaluation. Tests also verify standalone failure isolation, RQ2-only
same-family failure, consistent risk-fit totals, inclusive/exclusive threshold
boundaries, and gate action/nullability rules.

## Recheck commands

```bash
conda run -n fas python -m unittest discover -s tests -p test_preregistration.py -v
conda run -n fas python -m unittest discover -s tests -p test_contracts.py -v
conda run -n fas python -m unittest discover -s tests -v
conda run -n fas python scripts/validate_preregistration.py --stage schema
conda run -n fas python scripts/validate_preregistration.py --stage source-dry-run
conda run -n fas python scripts/write_freeze_record.py
conda run -n fas python scripts/check_environment.py
git diff --check
```

The last three Python commands currently return 1; this is expected, not readiness.

## Remaining approval boundary

Stop here for owner review. A fresh green workflow on the committed rework
revision is still required; the earlier green run does not certify these changes.
Commit and push this checkpoint before handing it to the owner for review. All
future checkpoints follow the same push-before-review boundary.

`fas` currently has Python 3.13.15, outside the registered >=3.11,<3.13 range.
The dependency-free contract tests passed there, but this does not certify the
registered model environment. Do not change Python or create another environment
without owner approval. Checkpoint 1.1 must use the existing `fas` environment.

The optional SiW-M data-audit gate discrepancy documented at checkpoint 1.0 remains
outside this rework and must be resolved before core data-audit acceptance.