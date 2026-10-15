# 194 — Review of Document 193: OULU Batch-07 AI Visual Proposals

Date: 2026-10-15  
Repository: `lathevinh/fas`  
Reviewed commit: `7f998d71dabd8f629f9f117970ce58acdacf7931`  
Reviewed document: `docs/193-review-response-doc192-oulu-batch07-ai-proposals.md`  
Reviewed aggregate: `results/phase1/oulu-visual-review-batch07-v1.json`

## Verdict

**DOCUMENT 193 — ACCEPTED WITHOUT REWORK FOR AI-SCREENING / PROVENANCE SCOPE.**

**THE TEN AI VISUAL PROPOSALS FOR EXACT RANKS 60..69 ARE ACCEPTED AS NON-BINDING PROPOSALS.**

**OBSERVED AI PROPOSALS: 9 `rejected_false_positive`, 1 `uncertain_insufficient_evidence`, 0 `confirmed_same_content_or_derived_lineage`.**

**THE UNCERTAIN PROPOSAL IS CORRECTLY RETAINED AS UNCERTAIN AND MUST NOT BE SILENTLY CONVERTED TO REJECTION.**

**NO SCIENTIFIC HARD STOP IS TRIGGERED BY THE AI PROPOSAL SET.**

**AI-SCREEN COVERAGE MAY NOW ADVANCE FROM 60/85 TO 70/85.**

**ACCEPTED CURRENT EFFECTIVE SCREEN-LEVEL TOTAL REMAINS 60.**

**NEXT AUTHORIZED STEP: PREPARE A SEPARATE CATEGORICAL-ONLY HUMAN HANDOFF FOR ALL TEN RANKS 60..69 USING THE ALREADY ACCEPTED 30 REVIEW ASSETS.**

**HUMAN INPUT COLLECTION ITSELF MUST WAIT FOR FORMAL REVIEW OF THAT HANDOFF.**

**DO NOT ACTIVATE BATCH07, DO NOT START RANK70+, AND DO NOT RUN RESEARCH-MODEL OR LATER SCIENTIFIC STAGES.**

---

## 1. Review192 authority existed before the AI stage

Review192 was committed in `fc0a61f03339b668d406e95b177f15cb5c6c9643` before Document193.

Review192 explicitly accepted Document191 packet preparation and authorized AI visual proposal/screening for exact ranks60..69 only.

There is no process-order violation.

## 2. Scope is exact

Document193 covers exactly `60,61,62,63,64,65,66,67,68,69`.

No rank70+ candidate is included.

## 3. The AI checkpoint is explicitly proposal-only

The aggregate records `review_type = "AI_assisted_visual_adjudication_proposals_only"`.

It also records human dispositions = 0, effective activations = 0, and AI checkpoint review pending = true.

## 4. The declared review assets were actually opened

Document193 records actual visual opening of `temporal_a.png`, `temporal_b.png`, and `trigger.png` for each of ten ranks.

Total: **30 visually opened assets**.

## 5. Visual inspection is correctly bounded

The checkpoint explicitly states all original frames visually inspected = false and additional frame/video assets opened = 0.

The 19 source videos contain 2464 technically verified full-RGB frames from packet191, but those technical verifications are not misrepresented as visual inspection.

## 6. Fixed temporal evidence remains unchanged

The two temporal panels expose the fixed 17 temporal slots per video occurrence.

The trigger remains the accepted earliest minimum-Hamming witness.

No new sampling policy is introduced.

## 7. AI reasoning is restricted to permitted non-identity evidence

The checkpoint states that reasoning uses visible garment structure, layering, closure/pattern/render geometry, scene/context, and presentation relationships.

It explicitly reports `face_identity_inferred = false`.

## 8. All three proposal outcomes remained available

Available dispositions are exactly:

- `confirmed_same_content_or_derived_lineage`
- `rejected_false_positive`
- `uncertain_insufficient_evidence`

There is no forced binary decision.

## 9. No rejection quota exists

The aggregate explicitly records `no_rejection_quota = true`.

## 10. The uncertain case is scientifically important

The actual AI outcome is:

- rejection: **9**
- uncertain: **1**
- confirmed same/derived: **0**

The uncertain proposal is retained because visible non-biometric structure was insufficient for a confident decision.

## 11. Uncertainty must not be promoted to rejection

The aggregate records `uncertainty_not_forced_to_rejection = true`.

Review194 accepts this behavior.

## 12. Darkness and pHash distance are not used as rejection shortcuts

The aggregate explicitly records `darkness_or_pHash_distance_used_as_rejection_rule = false`.

## 13. Nine rejections are limited to visible positive divergence

Document193 states that rejection proposals rely on visible structural divergence.

Hidden regions are not claimed to have been compared.

## 14. No confirmed same/derived proposal exists

Confirmed count is **0**.

Therefore no AI-triggered prospective scientific hard stop is present.

## 15. Hard-stop semantics remain preserved

The AI definition retains `confirmed_same_content_or_derived_lineage` as an available outcome.

Had such a proposal occurred, the workflow would require prospective hard-stop handling rather than automatic activation or queue continuation.

## 16. Pair-specific rationale and visibility records exist privately

The aggregate states that each pair has pair-specific rationale, visibility limitations, and exact sampling/evidence bindings.

These records remain private.

Review194 accepts their provenance/existence for AI-screening scope; it does not convert AI-written rationale into human reasoning.

## 17. Correlated evidence is disclosed

The aggregate reports at least one exact reused-video rank group.

Document193 also notes related garment/configuration reuse.

Separate AI proposals do not constitute independent trials or independent corroboration.

## 18. Correlation does not collapse candidate-level review

Ranks60..69 remain distinct frozen queue candidates.

A later human handoff should require a separate categorical decision for every rank.

## 19. Packet provenance is strongly rebound

The AI checkpoint binds accepted packet aggregate, packet preflight, packet verification, packet lineage, packet summary, frozen queue, exact packet candidate, manifests, temporal sampling, full-RGB/thumbnail hashes, and trigger witness.

## 20. Exact viewed-asset hashes are verified

The aggregate reports **30 viewed asset hash readbacks**.

## 21. No packet regeneration occurred

Document193 performs no media decode, archive extraction, packet re-export, or archive rehash.

## 22. No new code/test/policy/environment changes occur

The commit changes only:

- `README.md`
- Document193
- the public batch07 AI aggregate

No production code or test file changes are present.

## 23. Protected prior evidence remains unchanged

The aggregate reports:

- protected roots unchanged: 67
- frozen artifacts unchanged: 13
- study configs unchanged: 17
- owner source bytes/fields unchanged
- historical packet pending/nonadjudicated flags unchanged
- accepted source/helper/test pins unchanged

## 24. Packet191 historical state remains immutable

The accepted packet records still say review pending / awaiting visual review as creation-time state.

Document193 does not rewrite those packet records.

## 25. Main/sibling AI roots are deterministic serialization replay

Each AI root contains definition, ledger, ten proposed pair records, and summary: **13 files per root**.

Main and sibling match **13/13 byte-for-byte**.

This is serialization reproducibility only, not another AI visual pass or an independent reviewer.

## 26. Output guards remain active

Actual probes refuse existing main output, existing sibling output, repository output, source-overlap output, and symlink output.

## 27. Immutable overwrite refusals pass

Overwrite attempts against preflight, observation input, and first proposed row raise `FileExistsError`.

## 28. Existing focused regression remains clean

Document193 reports **78/78 focused tests passed**.

## 29. Full-suite baseline remains valid

Document193 does not claim a new local full-suite run.

The accepted Document191 baseline remains **265/265 passed**.

Because Document193 changes no code or tests, this is acceptable.

## 30. Fresh exact Document193 publication CI passes

Exact reviewed commit: `7f998d71dabd8f629f9f117970ce58acdacf7931`.

Fresh GitHub Actions run `38706506199` is `completed / success`.

Validate job `116327125698` is `completed / success`.

The validate job completed at `2026-10-15T08:34:15Z`.

There is no publication-CI blocker.

## 31. AI coverage may now advance to 70/85

Before Review194, accepted AI coverage was **60/85**.

Document193 actually completed visual screening for ten more frozen candidates.

Review194 accepts that AI-screening checkpoint.

Therefore current accepted AI-screen coverage may now be reported as **70/85**.

## 32. Fifteen candidates remain not yet AI-screened

The frozen highest-risk queue contains 85 candidates.

After accepting the ten batch07 AI screens, **15 candidates remain not yet AI visually screened**.

## 33. Effective accepted total remains 60

No human decision exists for ranks60..69.

No batch07 import or activation exists.

Therefore **accepted current effective screen-level total = 60**.

## 34. The nine AI rejections are not effective dispositions

The nine rejection proposals are AI-only.

They must not be directly activated.

## 35. The one AI uncertainty is not an error condition

An uncertain AI proposal is a valid outcome.

It does not require re-running AI with more evidence merely to obtain a binary answer.

## 36. Do not expand evidence merely because AI was uncertain

The accepted human handoff should use the existing bound review evidence: temporal A, temporal B, and trigger.

Do not automatically decode more frames, inspect full video, or create new evidence solely to eliminate uncertainty.

## 37. Human handoff should cover all ten ranks

The next human step should not review only the one AI-uncertain candidate.

All ranks60..69 require owner/human categorical disposition.

## 38. Human handoff must remain categorical-only

For every rank require only:

1. Evidence sufficient? — Yes / No
2. If sufficient: Same or derived content? — Yes / No
3. Personally inspected? — Yes / No
4. Own decision? — Yes / No

No mandatory human-authored prose is required.

## 39. Deterministic human mapping remains unchanged

- evidence insufficient -> `uncertain_insufficient_evidence`
- sufficient + same/derived Yes -> `confirmed_same_content_or_derived_lineage`
- sufficient + same/derived No -> `rejected_false_positive`

A confirmed human result must preserve the prospective scientific hard stop.

## 40. Do not prefill the human answer from AI

The form should initialize all human categorical fields blank.

The AI proposal should not be preselected.

Prefer hiding/collapsing AI disposition/context until after the owner submits the pair decision.

## 41. Neutral visibility notices are allowed

The handoff may surface visibility limitations neutrally.

It should not translate those limitations into a recommended disposition.

## 42. Correlation notices should remain neutral

Where source-video/configuration reuse exists, the human form may state that evidence is correlated.

It must not instruct the owner to copy a previous answer.

## 43. Review194 authorizes handoff preparation, not immediate human input

The next checkpoint may prepare the categorical-only human handoff for exact ranks60..69.

That handoff should receive a formal review before genuine owner input is collected.

## 44. No batch07 activation is authorized

Review194 does not authorize human import in advance, reconciliation in advance, effective activation, or batch07 closure.

## 45. Rank70+ remains blocked

Even though only 15 frozen candidates remain un-screened, do not start rank70+ yet.

The batch07 ranks60..69 chain must proceed through the accepted governance sequence before queue continuation.

## 46. Other datasets remain blocked

No CASIA/MSU/SiW audit continuation is authorized by Review194.

## 47. Research-model stages remain blocked

Review194 does not authorize source dry run, classifier/risk-model execution, analysis freeze, locked target evaluation, or model training/evaluation.

## 48. Scientific readiness remains false

The AI screen does not establish capture independence, exhaustive transformed-region independence, global lineage clearance, cross-dataset independence, disposition accuracy, or inter-rater reliability.

## Current state after Review194

### Accepted effective screen-level dispositions

**60 / 85**

### Accepted AI-screen coverage

**70 / 85**

### Batch07 AI proposal result

- rejection proposals: **9**
- uncertain proposals: **1**
- confirmed same/derived proposals: **0**
- AI-triggered hard stop: **false**

### Remaining AI screen work

**15 / 85 candidates remain not yet AI-screened.**

### Immediate next task

Prepare a **categorical-only human handoff for all ranks60..69**, using the existing accepted 30 bound assets.

Then stop for formal handoff review before collecting owner answers.

## Final disposition

**DOCUMENT 193 — ACCEPTED WITHOUT REWORK FOR AI-SCREENING / PROVENANCE SCOPE.**

**TEN NON-BINDING AI PROPOSALS FOR RANKS60..69 — ACCEPTED.**

**9 REJECTION PROPOSALS, 1 UNCERTAIN PROPOSAL, 0 CONFIRMED SAME/DERIVED.**

**THE UNCERTAIN PROPOSAL REMAINS UNCERTAIN.**

**NO SCIENTIFIC HARD STOP IS TRIGGERED.**

**AI-SCREEN COVERAGE = 70/85.**

**ACCEPTED CURRENT EFFECTIVE SCREEN-LEVEL TOTAL = 60.**

**15 HIGHEST-RISK CANDIDATES REMAIN NOT YET AI-SCREENED.**

**NEXT AUTHORIZED STEP: PREPARE A SEPARATE CATEGORICAL-ONLY HUMAN HANDOFF FOR ALL RANKS60..69 USING THE EXISTING 30 ACCEPTED ASSETS.**

Do not collect owner input before that handoff is formally reviewed. Do not activate batch07 or proceed to rank70+, other datasets, or research-model execution.
