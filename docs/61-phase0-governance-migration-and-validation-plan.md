# Phase 0 Work Package: Governance Migration and Validation

Date: 2026-09-18  
Status: implementation brief frozen before coding  
Authority: `docs/42-data-to-experiment-implementation-plan.md`  
Entry condition: final research and implementation specifications frozen at Document 60

## 1. Objective

Phase 0 replaces the legacy pilot-oriented preregistration scaffold with executable
governance contracts for the frozen source-only study. It does not implement dataset
adapters, backbones, feature extraction, classifier training, OOF fitting, risk
estimation, target prediction, or scientific analysis.

The phase succeeds when configuration, schema validation, freeze records, and
synthetic tests encode the final method strongly enough that an invalid or
target-informed run cannot unlock a later stage.

## 2. Starting state

The repository currently has useful primitives but validates an obsolete workflow:

| Current artifact | Reusable part | Required migration |
|---|---|---|
| `src/fas/preregistration.py` | Typed errors, staged validation, hashing, evidence reconciliation | Replace legacy config list/stages and pilot assumptions with final typed contracts |
| `scripts/validate_preregistration.py` | CLI failure reporting and nonzero exit | Expose final five stages and final artifact set |
| `scripts/write_freeze_record.py` | Commit/hash capture | Replace Stage-0/data freeze with source-only analysis freeze schema and refusal rules |
| `tests/test_preregistration.py` | Temporary-repository mutation tests | Replace pilot/confirmatory tests and add final governance/contract cases |
| `configs/vlm_candidates_v1.yaml` | Exact OpenCLIP recipe fields | Retain one fixed primary OpenCLIP; remove candidate selection |
| `configs/pilot_selection_v1.yaml` | Nothing normative | Delete from active contract and artifact hashing |
| `configs/preprocessing_v1.yaml` | Frame, detector, crop, hardware settings | Version/migrate to final branch-specific preprocessing contract |
| `configs/source_recipe_v1.yaml` | Calibration/risk solver details | Replace learned attention pooling with CLS plus mean-patch pooling and encode matched systems |
| `configs/evaluation_v1.yaml` | Population and bootstrap primitives | Replace pilot firewall, global claim order, null global gates, and obsolete endpoint names |
| `configs/seeds_v1.yaml` | Three fixed seeds | Preserve the three seeds; remove selection-seed semantics if unused |

Known legacy behavior that must not survive Phase 0:

- `CONFIG_FILES` requires `pilot_selection_v1.yaml` and two VLM candidates;
- readiness stages are `schema`, `data`, `pre-pilot`, and `confirmatory`;
- MSU-MFSD is privileged as a labeled pilot;
- `claim_sequence` begins with fusion rescue;
- DINO uses learned attention pooling;
- one global false-accept/event rule stands in for claim-specific applicability;
- the freeze record hashes only legacy configs and manifest summaries;
- passing `SCHEMA READY` certifies only the legacy schema.

## 3. Deliverables

### 3.1 Canonical configuration set

Create one canonical experiment entry point, proposed as
`configs/experiment_core_v1.yaml`, that references immutable typed component configs.
The resolved configuration must contain:

- four MCIO domains, each acting once as outer target;
- seeds `20260917`, `20260923`, and `20261001` with no selection seed;
- frozen DINOv2-Reg `dinov2_vitb14_reg4` with CLS plus mean-patch pooling;
- frozen plain DINOv2 ViT-B/14 with the same representation rule;
- frozen OpenCLIP `ViT-B-16` / `laion2b_s34b_b88k`, native 224 preprocessing,
  fixed generic prompts, and 1.30 context crop;
- calibrated heterogeneous and same-family average systems;
- immutable risk feature variants and matched OOF strategies;
- references to typed claim, population, bootstrap, competence, and freeze policies.

Configuration loading remains structured. JSON-compatible YAML may continue during
Phase 0; introducing a YAML dependency is unnecessary unless the final schema needs
features JSON cannot express.

### 3.2 Typed claim specifications

Replace `claim_sequence` and unscoped `minimum_effects` with claim IDs whose schemas
contain endpoint, population, comparator, sign, aggregation, uncertainty,
applicability, minimum effect, harm tolerance, dependencies, and outcome states.

Required claim records:

| Claim ID | Primary contract |
|---|---|
| `rq1_oof_transfer` | Non-interpolated error AP; domain-OOF minus matched sample-OOF on identical `e_DV` |
| `rq1_operational_utility` | Separate K=1 source-gate consequence; never an RQ1 conjunct |
| `rq2_complete_system` | Class-balanced raw AURC; `U_same - U_hetero`; fixed six-conjunct rule |
| `classifier_benefit` | APCER benefit with disclosed BPCER/BFNR harm and rescue accounting |
| `cross_foundation_attribution` | `R_DV` versus stronger single-branch risk baseline |
| `explicit_disagreement` | `R_DVd` versus capacity-matched `R_DV` |
| `quality_attribution` | With/without `q` on fixed heterogeneous errors |
| `optional_routing` | Disabled and absent from core readiness dependencies |

The RQ1 record must encode all-three-seed then all-four-target aggregation,
$N_{error,min}=20$, paired subject/video cluster bootstrap, and `pass`,
`evidence_against`, `inconclusive`, and `not_applicable` states.

The RQ2 record must encode the common detector-success mask, attack/bona-fide mean raw
AURC, $\delta_{min}=0.01$, positive 95% LCB, three positive targets, two positive seed
macros, 0.02 per-target selective harm, and FA/BFNR tolerances of 0.01 macro and 0.02
per target. Coverage is required output metadata and must not appear in the decision
predicate.

### 3.3 Population and transaction schemas

Define a transaction contract before any dataset adapter exists. At minimum it must
represent stable transaction/sample/subject/video IDs, dataset, outer target, label,
detector status, classifier/risk values, gate action, final K=1 action, and lineage
hashes.

Validation must enforce:

- detector failure preserves the transaction and requires null classifier/risk fields;
- risk views contain detector-successful rows only;
- heterogeneous and same-family RQ2 views have bit-identical transaction IDs and
  detector-success masks;
- end-to-end FA/BFNR and coverage use original pre-detection denominators;
- no fabricated score or rank exists after detector failure.

These are schema and synthetic-ledger contracts in Phase 0, not real metric
implementations.

### 3.4 Competence and applicability schemas

Encode dependencies rather than one global kill switch:

- RQ1 requires full heterogeneous-system competence;
- RQ2 requires both complete systems;
- shared DINO must pass nondegeneracy;
- standalone branch threshold failure blocks only its standalone claim;
- VLM incremental-risk wording requires its paired attribution result.

The full complete-system rule records macro AUROC and balanced accuracy at least 0.55,
macro-AUROC 95% LCB above 0.50, finite score range above $10^{-6}$, both-class support,
and finite calibration. The heterogeneous risk table additionally requires at least
20 errors and 20 correct predictions.

Event applicability counts erroneous transactions/videos. Dependence is represented
by subject/video bootstrap clusters, never by calling error events independent.

### 3.5 Final readiness stages

Replace the old stage enum with this monotone order:

1. `schema`;
2. `data-audit`;
3. `source-dry-run`;
4. `analysis-freeze`;
5. `locked-evaluation`.

Each stage validates all earlier requirements. Old names must be rejected and cannot
alias a new stage. Phase 0 implements complete `schema` validation and the structural
contracts/refusal behavior for later stages. Later stages remain blocked by explicit
missing evidence, never pass through placeholder/null values.

### 3.6 Freeze-record contract

Replace `results/stage0/freeze_record.json` semantics with a versioned analysis-freeze
record. The writer must refuse to run until its source-only prerequisites pass and
must never overwrite an existing consumed record.

The record schema must include:

- schema version, UTC creation time, clean 40-character Git commit;
- resolved canonical config and typed claim-spec hashes;
- code, environment lock, private/public manifest, source-count, policy, and upstream
  artifact hashes as applicable;
- all four excluded-target declarations and three seeds;
- source-only competence/applicability artifact hashes;
- explicit assertion that no target-derived selection input was used.

Validation must reject a dirty worktree, stale hash, changed claim spec, unknown
artifact, superseded config, malformed commit, target-derived lineage, and missing
prerequisite. Phase 0 may use synthetic source artifacts to test this behavior; it
must not create a real analysis freeze.

## 4. Implementation order

Use small test-first changes in this order:

1. Add failing tests for final stage names and rejection of old stages.
2. Add failing tests for one canonical model config and forbidden pilot/multi-VLM/
   learned-pooling fields.
3. Implement config discovery/loading and final schema primitives.
4. Add failing typed-claim tests for RQ1, RQ2, competence dependencies, and optional
   claim isolation.
5. Implement typed claim validation without metric computation.
6. Add synthetic transaction-ledger tests for detector failures, mask identity, and
   K=1 denominator reconciliation.
7. Add pure synthetic contract tests for seed/target aggregation, one-class/low-event
   states, tie-stable AURC, and paired cluster resampling interfaces.
8. Replace freeze hashing/writer semantics and test every refusal path in a temporary
   repository.
9. Remove superseded configs/tests from active discovery only after replacement tests
   pass; delete obsolete files rather than retaining ambiguous aliases.
10. Run focused and full validation from a clean checkout and produce the evidence
    bundle in Section 7.

Do not combine Phase 1 adapters, package installation, model downloads, GPU checks, or
real-data evidence with this change.

## 5. Required test matrix

### 5.1 Positive tests

- canonical config with exact pins resolves and passes `schema`;
- exactly four MCIO targets and exactly three fixed seeds pass;
- every required claim has a complete typed record;
- RQ1 averages three estimable seed deltas and then four target deltas;
- an estimable RQ1 seed below 20 errors remains in the point estimate but not event
  support;
- RQ2 positive sign favors lower heterogeneous class-balanced raw AURC;
- zero-error RQ2 class has raw AURC zero when class transactions exist;
- detector failures reconcile as terminal non-accepts in original denominators;
- standalone OpenCLIP competence failure leaves eligible complete-system claims
  untouched;
- synthetic clean source-only inputs produce a deterministic freeze-record payload.

### 5.2 Negative and boundary tests

- reject `pilot_domain`, `confirmatory_domains`, pilot attestations, candidate
  selection, multiple primary VLMs, learned primary pooling, and global claim order;
- reject an omitted MCIO fold, duplicate seed, replacement seed, wrong model/weight,
  non-native OpenCLIP preprocessing, or changed crop/prompt policy;
- reject RQ1 comparators with different transaction IDs, classifier predictions, or
  `e_DV` labels;
- reject seed deletion/reweighting and a synthetic AP for one-class labels;
- reject RQ2 AP as primary, reversed delta sign, pooled-class AURC, differing detector
  masks, coverage in the H2 predicate, or missing FA/BFNR guardrails;
- reject competence rules that make standalone OpenCLIP a core kill switch;
- reject detector-failed rows with classifier/risk scores or omission from the K=1
  ledger;
- reject frame-level bootstrap when subject/video clustering is available;
- reject old readiness stage names and null placeholders that attempt to unlock a
  later stage;
- reject freeze creation from dirty, stale, unhashed, target-derived, or incomplete
  inputs and reject overwrite of an immutable record.

## 6. Validation procedure

The final CLI named in Document 42 does not exist yet. During implementation, use the
focused test command after every edit; at completion, validate through the new public
CLI as well.

### 6.1 Fast development loop

```bash
python -m unittest tests.test_governance tests.test_contracts -v
```

If Phase 0 retains one test module initially, use explicit test classes or methods
rather than falsely claiming the final package layout exists.

### 6.2 Full synthetic regression

```bash
python -m unittest discover -s tests -v
```

All legacy calibration tests must remain green. Replaced preregistration tests must
test final semantics; old pilot behavior must not be preserved merely to keep a test
passing.

### 6.3 Public schema CLI

Target command after implementation:

```bash
python scripts/validate_preregistration.py --stage schema
```

Expected result:

```text
SCHEMA READY
```

The artifact listing must contain the canonical final config set and must not contain
`pilot_selection_v1.yaml` or a multi-candidate selection config.

### 6.4 Stage refusal checks

Before real evidence exists, each command below must fail nonzero with specific
missing-prerequisite messages rather than generic exceptions:

```bash
python scripts/validate_preregistration.py --stage data-audit
python scripts/validate_preregistration.py --stage source-dry-run
python scripts/validate_preregistration.py --stage analysis-freeze
python scripts/validate_preregistration.py --stage locked-evaluation
```

Also verify that old stage names fail argument parsing:

```bash
python scripts/validate_preregistration.py --stage pre-pilot
python scripts/validate_preregistration.py --stage confirmatory
```

Expected result: nonzero exit for all six commands. A later stage passing on current
placeholder manifests is a release blocker.

### 6.5 Freeze writer refusal

The migrated freeze writer must be exercised against synthetic fixtures:

- incomplete prerequisites: nonzero, no record written;
- dirty worktree: nonzero, no record written;
- target-derived lineage marker: nonzero, no record written;
- complete clean synthetic source fixture: deterministic payload accepted in a
  temporary repository;
- second write to the same immutable path: nonzero, original bytes unchanged.

Do not write or commit a production analysis-freeze record in Phase 0.

### 6.6 Static repository checks

```bash
git diff --check
git status --short
grep -RInE 'pilot_domain|confirmatory_domains|claim_sequence|attention_pooled_patch_tokens|pre-pilot|confirmatory' configs src scripts tests
```

The grep command must return no active-contract matches. A historical migration note
may mention old terms only outside executable directories.

## 7. Validation evidence bundle

The Phase-0 pull request must report:

- changed/deleted/added file list and migration mapping;
- focused test command and exact pass count;
- full synthetic suite command and exact pass count;
- final `schema` command and `SCHEMA READY` output;
- expected nonzero results for all four unavailable later stages and both rejected old
  stage names;
- freeze-writer refusal-test results;
- canonical config hashes and Git commit used by validation;
- stale-term scan and `git diff --check` result;
- explicit statement that no dataset, target label/result, model weight, or biometric
  sample was accessed.

Do not commit generated temporary freeze records, private manifests, raw data, model
weights, caches, or test bytecode.

## 8. Acceptance and release gate

Phase 0 passes only when all ten Definition-of-Done items in Document 42 are backed by
executable tests or explicit blocked-stage validation, every command in Section 6 has
the expected exit behavior, and an independent code review finds no target-informed
path or legacy alias.

Outcome classification:

- **Pass:** all positive, negative, refusal, full-suite, and static checks succeed.
- **Blocked:** environment/tooling prevents execution; record the exact unavailable
  prerequisite and do not authorize Phase 1.
- **Fail:** a final contract is absent, mutable, bypassable, or contradicted; repair
  Phase 0 and rerun the complete matrix.

Phase 1 remains locked after document completion. Writing this brief authorizes the
Phase-0 code change only; it is not evidence that Phase 0 has passed.

## 9. First coding action

Create failing governance tests for the final stage enum and forbidden legacy fields,
then replace config discovery. This is the cheapest discriminating change: it proves
the validator has stopped recognizing the pilot workflow before more schemas are
added.