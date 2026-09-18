# ChatGPT Implementation Review — Phase 0 Governance Commit

Date: 2026-09-18  
Repository: `lathevinh/fas`  
Reviewed commit: `889f2106a047e750d35b525216144b595293f882`  
Commit message: `Implement Phase 0 governance contracts`

## Verdict

The Phase-0 implementation is substantial and generally moves in the correct direction, but it should **not yet be considered passed**.

There are several implementation defects that can cause:

- the implemented method to differ from the frozen research specification;
- readiness stages to be unlocked with insufficient evidence;
- later statistical analysis to lack required lineage/cluster identifiers;
- tests to pass while enforcing the wrong scientific contract.

The first four issues below should be treated as blockers before Phase 0 is accepted.

---

# BLOCKER 1 — DINO checkpoint rule contradicts the frozen method

Current `configs/source_recipe_v2.yaml` contains:

```text
checkpoint_rule:
lowest_source_validation_domain_macro_acer_then_earlier_epoch
```

However the frozen normative documents (`docs/04`, `docs/05`, and `docs/42`) specify:

\[
\boxed{
\text{select the DINO head checkpoint by lowest equal-domain,
class-balanced validation BCE}
}
\]

with earlier epoch as the tie-breaker.

This is not a cosmetic difference.

Selecting by ACER instead of validation BCE can choose a different model checkpoint, which can change:

- branch predictions;
- calibration;
- final classifier errors;
- domain-OOF records;
- sample-OOF records;
- failure-risk labels;
- downstream RQ1/RQ2 results.

The current governance tests also validate the ACER rule, so the test suite can pass while enforcing the wrong method.

## Required fix

Change the canonical source recipe to the frozen rule, for example:

```text
lowest_equal_domain_class_balanced_validation_bce_then_earlier_epoch
```

Update validator expectations and add a negative test proving that an ACER-based checkpoint rule is rejected.

---

# BLOCKER 2 — `source-dry-run` can currently pass with fake hash strings

Current `_validate_source_dry_run()` validates mainly that:

- schema version is correct;
- `no_target_selection_input == true`;
- named artifact values look like 64-character SHA-256 strings;
- `source_policy_sha256` looks like a hash.

This is insufficient.

A user can create an `evidence.json` containing arbitrary fake hashes of the correct shape without those hashes corresponding to real source artifacts.

That means:

\[
\boxed{
\text{source-dry-run readiness is currently format-valid,
not evidence-valid}
}
\]

This creates a serious false-confidence path.

## Required fix

`source-dry-run` validation must re-derive or verify every required evidence hash.

At minimum:

1. every named evidence artifact must resolve to a declared path or artifact ID;
2. the artifact must exist;
3. its SHA-256 must equal the recorded digest;
4. the evidence bundle must include the required competence/applicability artifacts when those become prerequisites;
5. the source policy hash must correspond to the actual frozen source policy artifact;
6. target-derived lineage markers must fail validation.

Do not accept arbitrary hash strings that cannot be reconciled to actual artifacts.

Add negative tests for:

- nonexistent artifact with valid-looking SHA;
- existing artifact with wrong SHA;
- unknown artifact name;
- modified artifact after evidence creation.

---

# BLOCKER 3 — `locked-evaluation` authorization is existence-only

Current `validate_stage()` effectively checks only whether:

```text
results/locked-evaluation/authorization.json
```

exists.

Its contents are not meaningfully validated.

Therefore an empty or unrelated JSON file can satisfy the final authorization existence check once the previous stage is bypassed or incorrectly satisfied.

That is not sufficient for a locked evaluation gate.

## Required fix

Define a typed authorization schema and validate it.

The authorization should be structurally tied to the analysis freeze, including at least:

```text
schema_version
analysis_freeze_hash
created_from_commit
config/claim identity
outer-target declaration
seed declaration
authorization state
```

Recommended invariant:

\[
hash(\text{referenced freeze record})
=
authorization.analysis\_freeze\_sha256
\]

The validator must reject:

- empty authorization;
- malformed authorization;
- stale authorization;
- authorization referencing a different freeze;
- authorization referencing a different commit/config;
- overwritten/superseded freeze identity.

The final stage must be evidence-backed, not file-existence-backed.

---

# BLOCKER 4 — Transaction ledger schema does not enforce the frozen lineage contract

The current transaction validator requires approximately:

```text
transaction_id
system
label
detector_status
classifier_score
risk_score
final_k1_action
```

The frozen specification in Document 42 requires a substantially richer transaction ledger:

```text
transaction_id
sample_id
dataset
subject_id
video_id
outer_target
ground_truth
detector_status
pad_score
pad_threshold
pad_decision
risk_score
gate_threshold
gate_action
final_k1_action
classifier_artifact_hash
risk_artifact_hash
policy_artifact_hash
```

This information is not optional bookkeeping.

It is required later for:

- subject/video cluster bootstrap;
- exact target/fold reconciliation;
- paired-system identity;
- leakage auditing;
- result lineage;
- artifact reproducibility;
- gate/policy tracing.

If Phase 0 blesses a weaker ledger, later code may produce scientifically unusable outputs even though the transaction validator passes.

## Required fix

Expand the typed transaction contract now.

At minimum enforce:

- stable `transaction_id`;
- stable `sample_id`;
- `dataset`;
- `subject_id`;
- `video_id`;
- `outer_target`;
- ground-truth label;
- detector status;
- classifier score/decision fields;
- risk score;
- gate action;
- final K=1 action;
- classifier/risk/policy artifact hashes.

Required nullability rules should depend on detector status.

Example:

```text
detector failure:
    classifier_score = null
    risk_score = null
    pad_decision = null
    gate_action = null
    final_k1_action = non_accept
```

Add tests that reject missing cluster/lineage fields.

---

# MAJOR 5 — `routing_validation` is incorrectly required during data audit

Current data-audit code includes:

```python
required_roles = {
    "train",
    "branch_calibration",
    "routing_validation",
}
```

But routing is explicitly optional in the frozen plan.

Document 42 defines:

```text
routing_validation = optional routing threshold after core claims
```

Making it mandatory can unnecessarily reserve data from the source fitting pool and therefore change:

- effective training-set size;
- calibration/statistical power;
- pseudo-shift composition.

This is not just a naming problem.

## Required fix

Do not require `routing_validation` for core Phase-1/Track-B readiness.

It should be either:

- empty/not applicable for the core study; or
- instantiated only when the optional routing study is separately enabled.

Add a test showing a valid core manifest passes with no routing-validation partition.

---

# MAJOR 6 — Seeds are not actually pinned by the validator

The config currently contains the correct frozen seeds:

\[
[20260917,20260923,20261001].
\]

However the validator checks only:

- exactly three seeds;
- unique;
- integers.

Therefore replacing the three seeds with other integers would still pass schema validation.

The frozen study explicitly pins these values.

## Required fix

Validate exact equality:

```python
seeds == [20260917, 20260923, 20261001]
```

Also verify:

```text
shared_across_primary_controls = true
```

and the frozen replacement policy if it is normative.

Add a negative test for a replacement seed.

---

# MAJOR 7 — GitHub does not independently prove the full test suite passed

The commit contains substantial test code, including:

- governance tests;
- transaction/contract tests;
- freeze tests;
- updated preregistration tests.

However, no GitHub CI status or workflow run is currently attached to commit:

```text
889f2106a047e750d35b525216144b595293f882
```

Therefore the repository content proves that tests were written, but it does **not independently prove** that the entire suite passed on this exact commit.

## Required evidence before Phase-0 acceptance

Run and record:

```bash
python -m unittest discover -s tests -v
python scripts/validate_preregistration.py --stage schema
python scripts/validate_preregistration.py --stage data-audit
python scripts/validate_preregistration.py --stage source-dry-run
python scripts/validate_preregistration.py --stage analysis-freeze
python scripts/validate_preregistration.py --stage locked-evaluation
```

Expected current repository behavior:

```text
schema -> PASS
data-audit -> FAIL CLOSED until real audit evidence exists
source-dry-run -> FAIL CLOSED
analysis-freeze -> FAIL CLOSED
locked-evaluation -> FAIL CLOSED
```

Also verify old stages are rejected:

```text
data
pre-pilot
confirmatory
```

The PR/commit evidence should include exact pass/fail counts and exit codes.

---

# GOOD PARTS — KEEP THESE

The following implementation choices are good and should not be redesigned.

## Final stage enum

```text
schema
data-audit
source-dry-run
analysis-freeze
locked-evaluation
```

This correctly replaces the pilot workflow.

## Canonical model set

The canonical config correctly moves toward:

- DINOv2-Reg;
- plain DINOv2 control;
- fixed OpenCLIP ViT-B/16;
- calibrated heterogeneous system;
- calibrated same-family system.

## Legacy candidate/pilot configs removed from active discovery

This is correct.

## Immutable freeze writer

The no-overwrite behavior and atomic creation pattern are good.

## Dirty-worktree freeze refusal

This is appropriate.

## RQ1 fixed-error pairing checks

The validator correctly requires matching transaction IDs/predictions/error labels between domain-OOF and matched sample-OOF.

## RQ2 detector-mask identity

This is correctly enforced.

## Detector failure semantics

Keeping detector-failed transactions in the ledger with null scores and terminal K=1 non-accept is correct.

## Standalone OpenCLIP competence does not kill core claims

This correctly follows the frozen claim-specific competence logic.

---

# REQUIRED REWORK ORDER

Implement the fixes in this order.

## 1. Fix scientific recipe mismatch

Correct:

```text
DINO checkpoint selection:
ACER -> equal-domain class-balanced validation BCE
```

Update schema tests immediately.

## 2. Harden source-dry-run evidence reconciliation

Make recorded hashes refer to and validate actual source artifacts.

## 3. Harden locked-evaluation authorization

Replace existence-only authorization with a typed record tied to the immutable analysis freeze.

## 4. Complete transaction ledger contract

Add dataset/subject/video/fold and artifact-lineage fields.

## 5. Remove mandatory routing-validation role

Keep it optional.

## 6. Pin exact seeds

Reject any replacement seed.

## 7. Run and publish validation evidence

Record exact commands, exit codes, test counts, commit SHA, and expected blocked stages.

---

# Acceptance criteria for the revised implementation

Phase 0 can be accepted when all of the following hold:

1. Canonical checkpoint rule matches the frozen BCE rule.
2. Schema rejects the old ACER checkpoint rule.
3. `source-dry-run` cannot pass with invented hashes.
4. `locked-evaluation` cannot pass with an empty/arbitrary authorization file.
5. Transaction ledger enforces required cluster and lineage fields.
6. Core data audit does not require routing-validation records.
7. Exact frozen seeds are enforced.
8. Full synthetic/unit suite passes on one clean commit.
9. `schema` passes.
10. All unavailable later stages fail closed on the current repository state.
11. Old stage names fail.
12. No real target output was accessed during this rework.

---

# Final disposition

\[
\boxed{
\text{PHASE 0 IMPLEMENTATION REQUIRES REWORK BEFORE ACCEPTANCE}
\]

The implementation is not fundamentally off-track.

Most of the migration is useful and should be retained.

The main concern is that the current test suite can report success while:

- enforcing one wrong scientific rule;
- accepting weakly verified evidence;
- leaving the final evaluation gate insufficiently authenticated.

Those issues can create incorrect results or false confidence in protocol compliance and should be fixed before proceeding to Phase 1.
