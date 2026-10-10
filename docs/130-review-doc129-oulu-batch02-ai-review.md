# 130 — Review of Document 129: OULU Batch-02 AI Visual Proposals

Date: 2026-10-10  
Repository: `lathevinh/fas`  
Reviewed commit: `44c774aeea87945c1617780c8cb64ffc4e6fb2dc`  
Reviewed document: `docs/129-review-response-doc128-oulu-batch02-ai-review.md`

## Verdict

**DOCUMENT 129 — ACCEPTED FOR AI-PROPOSAL SCOPE.**

**CHECKPOINT 1.5O OULU BATCH-02 AI-ASSISTED VISUAL PROPOSALS — ACCEPTED WITHOUT METHOD REWORK.**

**BATCH 02 SCIENTIFIC / EFFECTIVE CLOSURE — NOT ACCEPTED YET.**

The checkpoint correctly performs the bounded AI-assisted visual inspection authorized by Review 128 and keeps all ten outcomes explicitly at proposal level.

The result is unusually uniform — ten `rejected_false_positive` proposals out of ten — but the public evidence does not show a protocol violation, quota forcing, queue skipping or threshold retuning. The uniformity therefore does not by itself invalidate the checkpoint.

However, because the pair-level detailed visual rationales and images are private, the public repository cannot independently establish that all ten visual judgments are scientifically correct. Genuine human review remains required before any of these proposals become effective dispositions.

## 1. Queue scope is correct

The checkpoint reviews exactly frozen queue ranks 10 through 19.

No additional pair is opened, skipped or substituted.

The roles, selector, seed and perceptual-screening threshold remain unchanged.

## 2. Actual visual inspection is distinguished from software verification

For each pair, the checkpoint opens both temporal panels and the trigger witness.

Therefore 10 pairs correspond to 30 actually viewed bound images.

Each pair has 17 fixed temporal slots per video occurrence represented across its two temporal panels.

The document correctly distinguishes visual inspection from PNG/hash verification.

## 3. AI proposal result

| Proposed disposition | Count |
|---|---:|
| `rejected_false_positive` | 10 |
| `uncertain_insufficient_evidence` | 0 |
| `confirmed_same_content_or_derived_lineage` | 0 |

At this checkpoint:

- human dispositions: 0;
- effective dispositions: 0.

This separation is correct.

## 4. Ten out of ten rejection proposals deserve scrutiny but are not automatically suspicious

A 10/10 rejection outcome can arise if the perceptual screening rule has high false-positive yield in this region of the candidate queue.

The checkpoint gives a plausible visual mechanism:

- persistent foreground garment topology differences;
- layering differences;
- garment structure/pattern differences;
- contextual geometry differences;
- coarse centered-torso / pale-background / ceiling similarity explaining the screen trigger.

The report explicitly states that no uncertainty was converted into rejection for quota or queue progression.

No public evidence currently contradicts that statement.

Therefore I do not reject the checkpoint merely because all ten proposals share the same disposition.

## 5. Public verification cannot validate the visual correctness of all ten proposals

The detailed pair-level rationales and images remain private.

The public aggregate verifies existence and binding of the proposal records, viewed assets and packet hashes, but cannot independently establish that each proposed rejection is visually correct.

Accordingly, the ten proposed rejections must remain AI proposals pending genuine human review.

## 6. Disposition scope is correctly narrow

The rejection proposals concern only the observed perceptual-screen rendered-content relationship.

They do not establish:

- independent original capture;
- absence of all shared source material;
- absence of short shifted common subsequences;
- absence of transformed/cropped compositing;
- full-video independence;
- subject/face identity difference.

## 7. Garment differences are acceptable evidence only for content lineage, not identity

Using foreground garment construction and layering as evidence is acceptable here because the question is whether two candidate videos show recognizable corresponding rendered content.

It must not be interpreted as biometric identity evidence.

Document 129 explicitly avoids face-identity inference.

## 8. Sparse sampling remains a limitation

Only fixed sparse temporal panels and trigger witnesses were visually inspected.

No full frame-by-frame review, temporal registration, geometric registration, transformed-region search or full-video alignment was performed.

Therefore a rejection proposal cannot rule out every possible partial, shifted or transformed relationship.

## 9. Pair-specific rationales are claimed and bound

Document 129 states that all ten pairs have separate nonblank concrete rationales in the private observation input and proposal rows.

The private records bind each rationale to the exact pair packet, viewed image hashes, video manifests, temporal panel decode-order lists and trigger frame/RGB identity.

This is an appropriate evidence structure.

## 10. Provenance and immutability are adequate

The checkpoint binds Review 128, the accepted packet report, packet summary/lineage, preparation preflight, successful preparation CI, visual policy, private observation input and immutable writer.

The ledger contains:

- one definition;
- ten pair proposal rows;
- one summary.

Total: **12 private ledger files**.

Serialization replay is byte-identical, existing output is refused, the original 2,192 packet files remain unchanged, and all prior protected/frozen artifacts remain unchanged.

## 11. Tests and fresh CI are sufficient

Local focused regression:

- **53/53 passed**;
- zero failures/errors.

The 240-test full local regression was not rerun because production code/tests/policy/environment did not change.

Fresh GitHub Actions on exact checkpoint commit:

`44c774aeea87945c1617780c8cb64ffc4e6fb2dc`

completed successfully.

The exact CI job successfully completed synthetic regression, canonical schema validation, unavailable-stage fail-closed checks and legacy-stage rejection checks.

## 12. Batch 02 is correctly not closed

Current state:

- AI proposals: 10 rejected;
- human judgments: 0;
- effective dispositions: 0;
- `batch02_accepted_reconciled_disposition_state = false`.

The AI proposal ledger must not be promoted directly into effective scientific dispositions.

## 13. Genuine human review is the required next step

The next checkpoint should prepare a bound human-review handoff for these exact ten pairs.

It should:

1. preserve the AI proposal ledger unchanged;
2. use exactly queue ranks 10..19;
3. provide the same bound temporal panels/triggers;
4. leave all human answers blank;
5. optionally keep prior AI proposals hidden/collapsed initially to reduce anchoring;
6. require explicit human disposition and rationale for every pair;
7. preserve AI/human disagreement rather than automatically overriding either side.

## 14. Disagreement handling must remain conservative

If AI says reject and human says uncertain, effective state remains `uncertain_insufficient_evidence`.

If AI says reject and human says confirmed same/derived, trigger the cross-role scientific hard stop.

If AI and human agree on reject, the pair may move toward a bounded screen-level effective rejection using the same additive activation discipline as batch 01.

## 15. Do not start queue ranks 20+ yet

Queue ranks 20+ should remain untouched until batch-02 human review and any required reconciliation are resolved.

This keeps queue progression auditable and avoids accumulating unresolved proposal debt.

## 16. Current coverage must not be mistaken for clearance

After batch-02 AI review:

- highest-risk AI visual coverage: 20/85;
- highest-risk candidates not yet AI visually reviewed: 65;
- cross-role candidates not yet AI visually reviewed: 464;
- non-exact candidates not yet AI visually reviewed: 6,620.

This is coverage, not clearance.

## 17. Scientific gates remain correctly blocked

The checkpoint does not authorize data-audit completion, source-dry-run, analysis-freeze, locked target evaluation, detector/model execution, target-domain experiments or scientific readiness.

## Final disposition

**DOCUMENT 129 — ACCEPTED FOR ITS AI-PROPOSAL SCOPE.**

**CHECKPOINT 1.5O OULU BATCH-02 AI VISUAL PROPOSALS — ACCEPTED WITHOUT METHOD REWORK.**

Result:

**10 AI `rejected_false_positive` proposals, 0 uncertain, 0 confirmed, 0 human, 0 effective.**

The uniform 10/10 rejection result is not by itself grounds for rejection because the queue, evidence rules and immutable bindings remain fixed and each pair reportedly has a concrete private rationale.

However, the public checkpoint cannot independently validate the correctness of all ten private visual judgments.

**Required next step: genuine bound human review of these exact ten pairs before any effective batch-02 closure or progression to queue ranks 20+.**
