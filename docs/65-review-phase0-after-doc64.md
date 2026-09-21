# ChatGPT Review — Phase 0 Rework Verification after Document 64

Date: 2026-09-18  
Repository: `lathevinh/fas`  
Reviewed commit: `a39cac2d6b0f4e173f2b0805fe98c7569406fbd9`  
Previous implementation commit: `889f2106a047e750d35b525216144b595293f882`  
Reviewed report: `docs/64-review-response-doc63-phase0-rework.md`

# Overall verdict

The rework is real and most of the previously reported defects were actually fixed in code.

Verified fixes:

1. DINO checkpoint selection now uses frozen equal-domain class-balanced validation BCE.
2. Exact frozen seeds are enforced.
3. `routing_validation` is no longer mandatory for the core data audit.
4. Transaction ledger now includes dataset/subject/video/fold and artifact-lineage fields.
5. Locked-evaluation authorization is tied to the analysis-freeze bytes and frozen identities.
6. Source-dry-run artifact hashes are now reconciled to actual files rather than accepted as arbitrary 64-character strings.
7. A GitHub Actions workflow was added for the Phase-0 regression matrix.

However, **Phase 0 should not yet be considered fully accepted** because two important issues remain.

---

# BLOCKER 1 — Source-dry-run competence/applicability artifacts are still semantically empty

The current validator requires exactly:

```text
results/source-dry-run/competence.json
results/source-dry-run/applicability.json
```

and correctly verifies:

- file existence;
- SHA-256;
- artifact set;
- `version == 1`;
- `no_target_selection_input == true`.

But it does **not** validate the scientific contents of those artifacts.

The current tests explicitly construct both artifacts as only:

```json
{
  "version": 1,
  "no_target_selection_input": true
}
```

and expect:

```text
source-dry-run -> READY
```

This means the source-dry-run stage can still be unlocked without containing actual competence or applicability evidence.

That is inconsistent with the frozen contract, where source-dry-run/analysis-freeze must carry source-only evidence such as:

- heterogeneous complete-system competence;
- same-family complete-system competence;
- DINO anchor nondegeneracy;
- AUROC / balanced accuracy;
- AUROC LCB;
- finite/nonconstant score checks;
- class support;
- calibration validity;
- heterogeneous risk-fit error/correct counts;
- claim applicability/event-support information.

## Why this matters

A correctly hashed empty JSON file is now trusted as competence evidence.

Therefore the chain:

```text
data-audit
-> source-dry-run
-> analysis-freeze
-> locked-evaluation
```

can be structurally valid without proving the conditions that are supposed to authorize the scientific evaluation.

This is a governance false-positive, not merely a missing report field.

## Required fix

Define typed schemas for `competence.json` and `applicability.json`.

At minimum, `competence.json` should encode enough data to evaluate the frozen competence predicates, e.g.:

```text
heterogeneous_complete:
    macro_auroc
    macro_balanced_accuracy
    macro_auroc_lcb
    score_range
    both_classes
    finite_calibration
    pass

same_family_complete:
    ...

dino_anchor:
    finite_scores
    nonconstant
    both_classes
    pass

heterogeneous_risk_fit:
    error_count
    correct_count
    pass

no_target_selection_input
```

`applicability.json` should similarly encode claim-specific event support and status.

Phase 0 does not need to compute these values from real data yet, but the structural validator must reject an empty artifact.

Add negative tests proving that:

```json
{"version":1,"no_target_selection_input":true}
```

is insufficient.

---

# BLOCKER 2 — K=1 gate semantics are still ambiguous in the transaction validator

The frozen protocol states:

> The gate changes only predicted-live decisions; predicted spoof remains terminal non-accept.

Current transaction validation requires, for every detector-successful transaction:

```text
gate_action in {"accept", "non_accept"}
```

including rows whose:

```text
pad_decision == "attack"
```

This means a predicted-spoof transaction is forced to have a gate action even though the gate should not be applied to it.

That can later create ambiguity in derived quantities such as:

- live decisions blocked by the gate;
- attacks newly blocked by the gate;
- bona-fide transactions newly rejected;
- selective coverage and gate intervention accounting.

A downstream implementation may incorrectly count an already-spoof decision with:

```text
gate_action = non_accept
```

as a gate intervention.

## Required fix

Encode gate applicability explicitly.

Recommended contract:

### Predicted attack/spoof

```text
pad_decision = attack
gate_threshold = null
gate_action = not_applied   # or null
final_k1_action = non_accept
```

### Predicted bona fide/live

```text
pad_decision = bona_fide
gate_threshold = finite
gate_action in {accept, non_accept}
final_k1_action = gate_action
```

The exact representation (`null` vs `"not_applied"`) is less important than making the distinction machine-checkable.

Add tests ensuring:

- predicted attack cannot be recorded as a gate-blocked live transaction;
- only predicted-live rows can have a real gate decision.

---

# CI / validation evidence status

Document 64 reports:

```text
52 tests, OK
SCHEMA READY
```

and adds `.github/workflows/phase0-governance.yml`.

The workflow content is sensible and checks:

- full unittest suite;
- schema readiness;
- all unavailable later stages fail;
- legacy stage names fail.

However, from the available GitHub integration I could not independently confirm a completed green workflow/status for commit:

```text
a39cac2d6b0f4e173f2b0805fe98c7569406fbd9
```

No combined status or associated workflow run was returned.

This does not prove CI failed; it means the independent green run is not currently verifiable from the available interface.

Since Document 64 itself says a green workflow is required before final acceptance, keep that requirement.

---

# Previously reported defects — verification status

| Previous issue | Status |
|---|---|
| DINO checkpoint ACER vs BCE | **Fixed** |
| Fake arbitrary source artifact hashes | **Mostly fixed** — hashes now reconcile, but semantic artifact validation remains incomplete |
| Authorization existence-only | **Fixed** |
| Incomplete transaction identity/lineage | **Fixed** |
| Mandatory `routing_validation` | **Fixed** |
| Seeds not exactly pinned | **Fixed** |
| Independent CI evidence | **Workflow added; green run not independently verified** |

---

# Non-blocking observations

The following are acceptable and should not delay Phase 0 after the two blockers are fixed:

- source policy hash is re-derived from `configs/source_recipe_v2.yaml`;
- authorization uses exact freeze bytes;
- detector-mask identity is paired across RQ2 systems;
- artifact hashes cover configs, manifests, Python source, and scripts;
- old stage names are rejected;
- optional routing remains outside the core claim path.

---

# Required rework

Before Phase 0 acceptance:

1. Add real typed structural validation for `competence.json`.
2. Add real typed structural validation for `applicability.json`.
3. Reject empty placeholder source evidence even when correctly hashed.
4. Encode `gate_action` as not applicable for predicted-spoof transactions.
5. Add tests for gate applicability semantics.
6. Obtain/record the green CI run for the final rework commit.

---

# Final disposition

\[
\boxed{
\text{REWORK IS MOSTLY CORRECT, BUT TWO BLOCKERS REMAIN}
}
\]

The implementation is now close.

Do **not** reopen the research design.

Fix only the source-evidence semantic schema and K=1 gate applicability, then rerun the Phase-0 suite.

If those are corrected and the green CI run is recorded, I would accept Phase 0 and allow Phase 1 to start.
