# Response to Document 59 and Final Implementation Freeze

Date: 2026-09-18  
Responds to: `docs/59-chatgpt-review-doc58.md`  
Status: review accepted; research and implementation specifications frozen

## Verdict on Document 59

Document 59 is correct. Its acceptance of Document 58 follows from the synchronized
contracts, and it identifies no residual scientific-design defect. I agree with its
recommendation to stop broad protocol review and move to concrete Phase-0 artifacts.

This is not an uncritical acceptance. The final audit tested whether the review's
conclusion held across the actual implementation owners rather than only Document 58.
The audit found:

- one common fixed-detector-success population for both RQ2 AURCs;
- original-transaction K=1 denominators for detector failures;
- coverage mandatory but absent from the H2 predicate;
- one signed RQ2 scalar and one deterministic RQ1 aggregation;
- claim-specific competence dependencies;
- no stale independent-error wording in the normative owners.

No scientific contradiction was found. One editorial governance gap remained: the
authority metadata of Documents 38 and 42 still referred to earlier review rounds and
did not name a single final implementation authority. That gap did not invalidate the
method, but leaving it open could let implementation choose between parallel plans.
It is corrected here.

## Canonical implementation authority

`docs/42-data-to-experiment-implementation-plan.md` is now the canonical final
implementation specification. It controls data, artifacts, populations, metrics,
claims, gates, phase exits, and locked evaluation.

`docs/38-implementation-plan.md` remains the companion dependency order and pull-
request sequence. If wording differs, Document 42 controls. Documents 43-59 preserve
review rationale and amendments but are not parallel executable specifications.

The scientific contracts in Documents 00-06 and the four-table paper contract in
Document 40 remain upstream constraints. No implementation convenience may override
them.

## Final frozen implementation contract

### Scope and systems

- Core data: four pre-specified MCIO outer-held-out folds.
- Core input: one deterministic RGB frame per video/transaction.
- Frozen encoders: `dinov2_vitb14_reg4`, plain DINOv2 ViT-B/14 control, and OpenCLIP
  `ViT-B-16` with `laion2b_s34b_b88k`.
- Primary heterogeneous classifier: calibrated DINOv2-Reg/OpenCLIP average.
- Same-family control: calibrated DINOv2-Reg/plain-DINOv2 average.
- Three fixed optimization seeds; no best-seed selection or prediction pooling.
- Track A is compact literature context only. SiW-M, routing, LoRA, distillation, and
  cue analyses remain optional and cannot rescue a core claim.

### Population contract

One immutable pre-detection transaction ledger is the denominator authority. The
deterministic frame is selected before face detection, and the same fixed detector and
crop manifest feed both RQ2 systems.

- Risk metrics use rows with `detector_status=success`.
- Both RQ2 systems must use a bit-identical detector-success mask.
- Detector failures have null classifier/risk values and no artificial rank.
- Detector failures are terminal non-accepts under K=1 and remain in
  `FA_end2end`, `BFNR_end2end`, and coverage denominators.
- Attack and bona-fide coverage are always reported but do not enter the H2 predicate.

### RQ1 contract

RQ1 compares domain-OOF and matched sample-OOF risk supervision on the identical
heterogeneous classifier errors:

$$
\Delta_{OOF,t,s}
=AP(e_{DV},r_{DVd}^{domain})-AP(e_{DV},r_{DVd}^{sample}).
$$

The primary endpoint is non-interpolated prediction-error AP. For estimable seeds:

$$
\Delta_{OOF,t}=\frac13\sum_{s=1}^{3}\Delta_{OOF,t,s},
\qquad
\Delta_{OOF,macro}=\frac14\sum_{t=1}^{4}\Delta_{OOF,t}.
$$

All three seeds remain equally weighted, including an estimable seed below 20 errors.
$N_{error,min}=20$ counts erroneous transactions/videos and controls event support,
not point-estimate weight. A target is eligible when all seed deltas are estimable and
at least two seeds meet the count. Undefined one-class AP makes the four-target claim
inconclusive; no seed is deleted and no synthetic AP is inserted. Uncertainty uses
paired subject/video cluster bootstrap within target, followed by seed-then-target
aggregation.

Selective K=1 utility is a secondary operational consequence. It neither replaces nor
becomes a conjunct of the RQ1 AP claim.

### RQ2 contract

For each complete system, compute class-conditional raw AURC on the common detector-
success population and define:

$$
U_{j,t,s}=\frac12(AURC_{attack,j,t,s}+AURC_{bona,j,t,s}),
\qquad
\Delta_{RQ2,t,s}=U_{same,t,s}-U_{hetero,t,s}.
$$

Positive values favor heterogeneous. H2 requires the frozen conjunction:

1. Four-target macro gain at least 0.01.
2. Paired cluster-bootstrap 95% LCB above zero.
3. At least three positive target deltas.
4. At least two positive seed-level four-target macros.
5. No target with heterogeneous selective harm above 0.02.
6. At source-selected gates, heterogeneous-minus-same-family `FA_end2end` and
   `BFNR_end2end` each no greater than 0.01 macro and 0.02 per target.

Raw cross-system error AP, classification metrics, error prevalence, excess-AURC, and
coverage are mandatory explanatory outputs. None is an alternative primary outcome.

### Competence and attribution

- RQ1 requires the heterogeneous complete system to pass the full source-only
  competence rule.
- RQ2 requires both complete systems to pass it.
- The shared DINO anchor must pass finite/nonconstant, both-class, and calibration
  nondegeneracy checks.
- A branch below the 0.55/LCB threshold loses only its standalone-competence claim.
- OpenCLIP standalone weakness cannot automatically fail a core RQ whose complete
  systems pass.
- Incremental VLM, cross-foundation, disagreement, quality-feature, margin, fusion,
  and routing claims each require their own frozen attribution test.

### Leakage and lineage

For outer target $T$, no sample, label, statistic, result, or artifact derived from
$T$ may select a model, checkpoint, calibrator, threshold, prompt, crop, feature,
comparator, effect rule, or analysis path. Every artifact records schema, code/config,
input/upstream hashes, fold, seed, and exclusion lineage. Locked evaluation refuses
dirty or mismatched freeze records.

### Four-table output contract

1. Strict single-image classifier competence.
2. RQ1 fixed-error risk transfer.
3. Selective PAD utility under K=1.
4. RQ2 complete heterogeneous versus same-family systems.

Track A cannot displace one of these tables or become a core claim.

## Implementation state and next action

The **specification is frozen**, but the repository is not yet Phase-0 complete. The
current validator/config scaffold still contains superseded pilot stages and claim
ordering. Existing 17 passing tests and `SCHEMA READY` validate that legacy scaffold;
they do not certify the final implementation contract.

Document 42 now contains the ten-item Phase-0 definition of done. The only authorized
implementation work is the first pull request in Document 38:

> migrate governance, configs, schemas, freeze records, and synthetic contracts to
> the final source-only specification.

Dataset administration may proceed in parallel. Real-data training, target-result
inspection, and backbone-facing implementation remain blocked until the Phase-0
review passes.

## Change-control rule

The broad research-plan review loop ends with Document 59. Future reviews inspect
concrete artifacts: schemas, configs, manifests, synthetic metric tests, split code,
lineage assertions, and freeze enforcement.

A specification amendment is allowed only when implementation exposes a concrete
contradiction, and it must be dated and committed before any affected target output is
available. Runtime inconvenience, optional-study failure, or an unfavorable result is
not grounds for amendment.

## Final disposition

Document 59 is accepted. No additional research-plan correction is required.
Document 42 is the canonical final implementation plan, Document 38 defines its
dependency order, and Phase 0 governance migration is now the sole next technical
step.