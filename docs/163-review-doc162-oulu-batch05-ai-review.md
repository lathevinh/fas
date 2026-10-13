# 163 — Review of Document 162: OULU Batch-05 AI Visual Proposals

Date: 2026-10-13  
Repository: `lathevinh/fas`  
Reviewed commit: `629c8020b16325a6fab0f32ad7f5a3d4f4e7372d`  
Reviewed document: `docs/162-review-response-doc161-oulu-batch05-ai-review.md`  
Reviewed aggregate: `results/phase1/oulu-visual-review-batch05-v1.json`

## Verdict

**DOCUMENT 162 — ACCEPTED FOR AI-PROPOSAL CHECKPOINT SCOPE.**

**CHECKPOINT 1.5AH OULU BATCH-05 AI-ASSISTED VISUAL PROPOSALS — ACCEPTED WITHOUT REWORK.**

**GENUINE HUMAN HANDOFF IS AUTHORIZED FOR RANKS 40–49 ONLY.**

The ten AI rejection proposals are accepted as properly recorded AI proposals, not as independently validated scientific truth and not as current effective dispositions.

Batch 05 is not closed. The accepted current screen-level total remains **40 relationships**. Current AI visual coverage is **50/85**, leaving **35/85** highest-risk candidates unreviewed.

## 1. Scope is correctly restricted to ranks 40–49

Checkpoint 1.5AH covers exactly ranks `40..49`. Document 162 states that exactly three bound images were opened per pair: `temporal_a`, `temporal_b`, and `trigger`, for **30 total visual assets**.

No rank 50+, extra frame, full video, or unbound image is included in the recorded AI review.

## 2. The checkpoint records proposals only

The aggregate reports:

- AI proposed `rejected_false_positive`: 10;
- uncertain: 0;
- confirmed same/derived: 0;
- human dispositions: 0;
- effective dispositions activated: 0;
- `batch05_accepted_reconciled_disposition_state = false`.

This is correct. Document 162 does not promote AI proposals to accepted human or effective outcomes.

## 3. Accepted current total correctly remains 40

Batch-05 AI review does not increase the accepted current screen-level count. The correct interpretation is:

- 40 accepted current screen-level relationships from batches 01–04;
- 10 batch-05 pairs with AI proposals only;
- 35 highest-risk pairs not yet AI visually reviewed.

Do not report 50 accepted/resolved relationships at this stage.

## 4. The all-reject pattern is not itself a protocol failure

All ten AI proposals are `rejected_false_positive`. A 10/10 reject result can occur in a pHash-prioritized false-positive queue and is not, by itself, evidence of procedural bias.

Document 162 explicitly records `no_rejection_quota = true`. This is important.

However, the 10/10 pattern should later be reported as an observed queue yield and must not be presented as ten independent validation successes.

## 5. AI semantic reasoning is materially better than a hash-only judgment

The document summarizes pair-specific reasoning based on persistent rendered foreground structure, including garment pattern, hood/collar configuration, snaps, layering, closures, quilting, zipper/placket geometry, drawstrings, inner openings, and chest-zip construction.

The stated reasoning is therefore not merely based on pHash, brightness, background, exposure, or face identity.

This is the correct qualitative evidence class for the declared perceptual-screen audit.

## 6. No facial-identity inference is claimed

The aggregate explicitly records `face_identity_inferred = false`.

This is appropriate. The audit should remain based on rendered-content correspondence/divergence rather than claims about whether the depicted people are the same or different individuals.

## 7. Visibility limitations are properly disclosed

Document 162 reports:

- ranks 41–42: veil limits fine/lower-torso details;
- ranks 40, 43 and 49: darkness limits some detail.

The document states that visible foreground structure remained available and that veil/darkness alone was not used as a rejection rule.

This is acceptable for an AI-proposal checkpoint.

## 8. Human handoff should preserve heightened scrutiny for low-visibility pairs

The human handoff should neutrally preserve visibility warnings for ranks:

`40,41,42,43,49`.

These warnings must not prescribe rejection.

For these pairs, the reviewer must remain free to choose:

- `rejected_false_positive`;
- `uncertain_insufficient_evidence`;
- `confirmed_same_content_or_derived_lineage`.

If evidence is insufficient, `uncertain_insufficient_evidence` is the correct conservative outcome.

## 9. Correlated evidence is correctly disclosed

Document 162 reports correlated foreground occurrences:

- ranks 40–43 share/repeat a left foreground and related opposite configurations;
- ranks 47–48 use closely related evidence.

These remain valid separate queue entries, but they must not be interpreted as ten independent observations of AI accuracy, human accuracy, or screening precision.

Future summaries should distinguish candidate-level count from repeated/correlated evidence families.

## 10. Sparse-view scope remains an important limitation

Only 30 bound images were visually inspected.

The AI did not visually inspect all 1956 source frames, full videos, exhaustive spatial alignments, arbitrary crops, or transformed/re-encoded variants.

Therefore the proposals support only observed perceptual-screen relationship judgments at the declared sparse-evidence scope.

They do not certify global content independence.

## 11. The AI proposals do not establish capture provenance

Even if all ten proposals are later confirmed by humans, this does not prove independent recording sessions, independent source captures, absence of all shared source material, absence of transformed partial overlap, or global OULU content-lineage clearance.

The checkpoint states these limits correctly.

## 12. Provenance binding is strong

The AI review definition binds Review 161, accepted batch-05 packet report, packet summary/lineage, preparation preflight, exact successful Document-160 CI, AI observation input, immutable writer, and visual evidence policy.

Each pair row additionally binds:

- exact queue/candidate;
- packet;
- three viewed image hashes;
- both video manifests;
- interleaved 17-slot decode orders;
- trigger decode orders;
- accepted RGB hashes.

This is a strong provenance chain for an AI-observation checkpoint.

## 13. Historical preparation packets remain immutable

The original packet records remain `review_performed = false`, which is correct because those records describe preparation state at creation time.

AI observations are stored in a separate ledger rather than patching preparation artifacts retroactively.

## 14. AI rows remain nonhuman and nonactivating

Every new AI row retains:

- `human_review_performed = false`;
- `effective_disposition_activated = false`.

This separation is necessary.

The next human handoff must not silently convert an AI proposal into a human answer or preselect the AI result as the human disposition.

## 15. Serialization replay is reproducible but not adjudication validation

The private AI ledger contains one definition, ten pair rows, and one summary: **12 files**.

A fresh sibling reproduces **12/12 byte-identically**.

This establishes deterministic record serialization, not that the ten visual judgments are correct.

## 16. Overwrite protection and protected history are correct

The checkpoint reports existing-output refusal, record-overwrite refusal, originals unchanged, both accepted 2014-file packet roots unchanged, 40 protected prior roots unchanged, and frozen 13 artifacts unchanged.

This is consistent with the immutable audit trail.

## 17. No new media processing or model execution occurred

The aggregate records no extra unbound frame/video opening, no new media decode/extraction, no research frame bank, no research model execution, and no model authorization.

This preserves the separation between audit evidence and research-model execution.

## 18. Focused regression is sufficient for this record-only checkpoint

Focused regression reports **66/66 passed**.

The full suite was not rerun locally, which is acceptable because this commit changes only README, Document 162, and the public aggregate. No production code, tests, policy, environment, or CI workflow changed.

The accepted full baseline remains **253/253** from Document 160.

## 19. Exact prerequisite CI is correctly bound

The AI checkpoint binds the exact accepted Document-160 CI:

- commit `acfce3aecd2345a91f146835afab93f1c9cadeae`;
- run `38377925777`;
- validate job `115230867707`;
- `completed / success`.

This is the correct prerequisite authority.

## 20. Fresh exact CI for Document 162 passes

Exact reviewed commit:

`629c8020b16325a6fab0f32ad7f5a3d4f4e7372d`

Fresh GitHub Actions:

- run `38384928998`;
- status `completed`;
- conclusion `success`.

Validate job:

`115254244024`

also completed successfully.

The exact job passes checkout, Python/FFmpeg setup, model-free dependencies, synthetic regression, canonical schema validation, unavailable-stage fail-closed verification, and legacy-stage rejection verification.

There is no publication-CI blocker.

## 21. Human review is now the necessary next evidence layer

The human handoff should preserve procedural independence:

- AI proposal must not be preselected as the human answer;
- human fields should start blank;
- AI reasoning may be collapsible/contextual but must not become human rationale automatically;
- the reviewer must personally inspect the bound evidence;
- uncertainty remains a valid outcome;
- same/derived remains a valid outcome and triggers the hard-stop path.

## 22. Human rationales should be pair-specific

The batch-04 experience showed why generic repeated rationale is weak.

For batch 05, require pair-specific rationale or pair-specific visible-structure description for every human disposition, especially the low-visibility pairs.

This reduces the chance of another semantic-remediation checkpoint.

## 23. No agreement quota is permitted

The fact that all ten AI proposals are rejection proposals must not become a target for the human reviewer.

If the human reviewer independently chooses uncertain or same/derived for any pair, preserve that outcome.

If all ten are genuinely rejected, preserve those genuine answers and proceed through normal import/review.

## 24. Batch 05 remains open

After this review:

- batch-05 packet preparation is accepted;
- batch-05 AI proposal recording is accepted;
- human review has not occurred;
- no effective batch-05 disposition exists;
- accepted current total remains 40.

Therefore batch 05 is not closed.

## 25. Ranks 50+ remain blocked

Do not prepare or inspect ranks 50+ yet.

Required order:

1. accepted packet preparation;
2. accepted AI proposal checkpoint;
3. genuine human handoff for ranks 40–49;
4. human import;
5. disagreement reconciliation or targeted semantic clarification if required;
6. separate additive activation;
7. review activation;
8. only then proceed to rank 50+.

## 26. Scientific/model gates remain blocked

This checkpoint does not authorize OULU content-lineage completion, full data-audit completion, source-dry-run, analysis freeze, locked target evaluation, detector/classifier/risk-model execution, other-dataset processing, capture-provenance certification, or scientific readiness.

All later scientific gates remain fail-closed.

## Final disposition

**DOCUMENT 162 — ACCEPTED FOR AI-PROPOSAL CHECKPOINT SCOPE.**

**CHECKPOINT 1.5AH BATCH-05 AI-ASSISTED VISUAL PROPOSALS — ACCEPTED WITHOUT REWORK.**

Recorded state:

- ranks 40–49 only;
- 30 bound images actually viewed;
- 10 AI rejection proposals;
- 0 uncertain;
- 0 confirmed same/derived;
- 0 human dispositions;
- 0 effective dispositions;
- 12/12 deterministic ledger replay;
- 40 protected roots unchanged;
- 13 frozen artifacts unchanged;
- focused 66/66 passed;
- exact publication CI succeeded.

The all-reject AI pattern is acceptable as a proposal result, but it is **not an independently validated scientific outcome**.

The accepted current total remains **40**.

AI visual coverage is **50/85**, with **35 highest-risk candidates still unreviewed**.

**GENUINE HUMAN HANDOFF FOR RANKS 40–49 IS NOW AUTHORIZED.**

The human handoff should preserve neutral visibility warnings for ranks 40, 41, 42, 43 and 49, require genuine personal inspection and pair-specific reasoning, and retain uncertainty/same-derived as real options.

Do not begin rank 50+, batch-05 activation, other datasets, or research-model execution until subsequent staged checkpoints are completed.
