# 168 — Review of Document 167: OULU Batch-05 Governance and Targeted Clarification Handoff

Date: 2026-10-14  
Repository: `lathevinh/fas`  
Reviewed commit: `de75c0b5a7dc91e58b4a74db8792fc6fcbf884e0`  
Reviewed document: `docs/167-review-response-doc166-oulu-batch05-clarification-handoff.md`  
Reviewed aggregate: `results/phase1/oulu-clarification-handoff-batch05-v1.json`  
Reviewed runner: `scripts/prepare_oulu_clarification_batch05.py`

## Verdict

**DOCUMENT 167 — ACCEPTED FOR GOVERNANCE CORRECTION, SCOPE BINDING, PROVENANCE, AND TECHNICAL PREPARATION.**

**CURRENT TARGETED HUMAN-CLARIFICATION UI — REWORK REQUIRED BEFORE HUMAN USE.**

**DO NOT ASK THE OWNER TO TYPE FREE-TEXT VISUAL DESCRIPTIONS OR RATIONALES.**

**NO NEW HUMAN INPUT SHOULD BE COLLECTED UNTIL THE FORM IS SIMPLIFIED AND REPUBLISHED WITH FRESH CI.**

The governance correction required by Review166 is implemented correctly. The six-rank evidence scope is also correct and the preparation checkpoint is technically reproducible. The remaining defect is the human-input interface: it requires the owner to type left/right visible structures, visibility limitations and pair-specific rationale even though these prose fields are not necessary to establish human decision ownership and have already created avoidable AI-wording provenance ambiguity.

The next form should collect only categorical human judgments and attestations. Descriptive prose should be generated separately by the system/AI from the already-bound visual evidence and must be labeled as machine-generated rather than human-authored.

---

## 1. Governance correction from Review166 is accepted

Document167 correctly records that the actual batch-05 order was:

1. Document164 handoff preparation;
2. owner human review / JSON export;
3. Document165 import;
4. Review166 external review.

It does not backdate Review166 acceptance and does not rewrite Document164, Document165, the raw owner input or imported human rows.

This is the correct additive treatment of the prior process-order deviation.

## 2. Rationale-authorship provenance is corrected appropriately

Document167 correctly narrows the previous overly broad claim about assistant-generated reasoning.

The additive governance state now distinguishes:

- owner-selected disposition;
- owner-attested personal inspection;
- importer non-generation/nonmutation;
- AI-assisted rationale drafting occurring or not being excludable;
- no claim of independently authored/blinded human rationale.

This is substantially more accurate than the historical Document165 field and should remain the authoritative additive interpretation.

## 3. Six-rank follow-up scope is correct

The targeted clarification union is exactly:

`40, 41, 42, 43, 48, 49`.

This matches Review166:

- mandatory self-contained clarification: `42,43,48,49`;
- heightened-scrutiny sufficiency check: `40,41,42,43,49`.

Clean ranks `44..47` are not reopened.

This scope is accepted.

## 4. Evidence reuse is correct

The new handoff copies only the 18 already-bound PNG assets for the six target ranks.

There is:

- no new frame extraction;
- no new media decode;
- no new AI visual review;
- no full-video expansion;
- no new research-model execution.

This preserves the original audit scope.

## 5. Rank48 treatment is correct

Rank48 is explicitly bound to evidence that is byte-identical to rank47.

The implementation correctly avoids:

- silently copying rank47 human prose;
- prescribing rank48's disposition;
- forcing a fresh visual inspection solely because the candidate has a different queue rank.

The previous personal inspection of identical evidence may be relied upon.

This is acceptable.

## 6. Technical reproducibility is strong

The main and independent sibling handoff each contain 21 files:

- 18 PNG assets;
- review definition;
- HTML;
- summary.

All 21/21 reproduce byte-identically.

Protected prior roots remain unchanged at 46.

Frozen 13 artifacts and 17 study configs remain unchanged.

Focused regression:

**69/69 passed.**

Full regression:

**256/256 passed.**

No technical regression blocker is present.

## 7. Fresh exact publication CI passes

Exact reviewed commit:

`de75c0b5a7dc91e58b4a74db8792fc6fcbf884e0`

Fresh GitHub Actions:

- run `38550598516`;
- status `completed`;
- conclusion `success`.

Validate job:

`115807325949`

also completed successfully.

The job passes:

- checkout;
- Python setup;
- FFmpeg installation;
- model-free screening dependencies;
- synthetic regression;
- canonical schema validation;
- unavailable-stage fail-closed verification;
- legacy-stage rejection verification.

There is no CI blocker.

## 8. Current human form is unnecessarily burdensome

The current runner explicitly creates free-text controls for:

- `left_visible_foreground_structure`;
- `right_visible_foreground_structure`;
- `visibility_limitation`;
- `rationale`.

Its completion gate requires all of these text fields to be nonblank.

This should be removed.

The project already binds the exact images, exact candidate, exact queue rank, AI observation history and prior human disposition. Requiring the owner to manually rewrite a prose description of those images does not materially improve decision ownership.

Instead it creates several problems:

1. It wastes human-review time.
2. It encourages copy/paste across similar candidates.
3. It makes semantic quality depend on writing style rather than the actual categorical judgment.
4. It recreates the same AI-assisted-wording provenance problem that Review166 had to correct.
5. It blurs the distinction between **who made the decision** and **who wrote the explanatory prose**.

Therefore the current free-text requirement should not be used for the next human pass.

## 9. Human responsibility should be reduced to categorical decisions

For each target pair, the owner should only be required to inspect the bound evidence and answer simple categorical questions.

The preferred two-step human decision is:

### Question A

**Is the available bound evidence sufficient to make a content-lineage judgment?**

- Yes
- No

### Question B — shown only if A = Yes

**Does the pair show the same rendered content or content derived from the same source?**

- Yes
- No

This maps deterministically to the existing dispositions:

| Evidence sufficient? | Same/derived? | Disposition |
|---|---|---|
| No | — | `uncertain_insufficient_evidence` |
| Yes | Yes | `confirmed_same_content_or_derived_lineage` |
| Yes | No | `rejected_false_positive` |

This preserves all three scientifically relevant outcomes without requiring prose.

## 10. Human attestation should also remain categorical

The owner may additionally be required to answer:

**Did you personally inspect the bound evidence for this pair?**

- Yes
- No

**Is this categorical disposition your own decision?**

- Yes
- No

For a valid record both should be Yes.

These categorical attestations are enough to preserve human decision ownership.

## 11. Remove per-pair wording-assistance disclosure

The current clarification handoff asks the owner to select:

- no AI wording assistance;
- AI-assisted wording;
- cannot exclude.

If the new form contains no owner-authored rationale text, this field becomes unnecessary at the pair level.

The historical batch-05 governance record should continue to disclose that AI-assisted wording occurred or could not be excluded in the earlier round.

For the new categorical-only review there is no prose-authorship question to resolve.

## 12. Machine-generated descriptions should be separate from human decisions

If a textual audit narrative is desired, the system may generate after the human categorical decision:

- left visible structure;
- right visible structure;
- visibility limitation;
- pair-specific rationale.

These fields must be explicitly labeled, for example:

- `AI_generated_left_observation`;
- `AI_generated_right_observation`;
- `AI_generated_visibility_note`;
- `AI_generated_rationale`.

They must **not** be labeled as human reasoning.

They must not determine or overwrite the human disposition.

The human categorical choice remains the authoritative human adjudication record.

## 13. Optional human confirmation of machine prose may also be Yes/No

If the project wants additional assurance that a machine-generated textual summary is reasonable, it can optionally ask:

**Does the generated summary accurately describe the visible evidence?**

- Yes
- No

If No, the record should simply retain:

`machine_summary_human_confirmed = false`

and the human should not be forced to rewrite the text.

A machine summary failure must not erase or alter the independently recorded human categorical disposition.

## 14. Do not show AI's proposed disposition before the owner's decision

The form may display the bound images and neutral visibility notice.

The prior AI result should remain hidden/collapsed until after the owner submits the categorical judgment for the pair, if practical.

This reduces anchoring.

The human decision should not require agreement with the earlier AI proposal.

## 15. Suggested minimal per-pair record

A sufficient human record can be as small as:

```json
{
  "queue_rank": 42,
  "evidence_sufficient": true,
  "same_or_derived_content": false,
  "personal_inspection_attested": true,
  "owner_decision_attested": true
}
```

The importer can derive:

```text
evidence_sufficient=true + same_or_derived_content=false
    -> rejected_false_positive
```

No free-text field is required for the owner's decision.

## 16. Scientific hard stop remains intact

If:

`evidence_sufficient = true`

and:

`same_or_derived_content = true`

then the importer must map to:

`confirmed_same_content_or_derived_lineage`

and preserve the prospective scientific hard stop.

The simplified interface must not weaken this rule.

## 17. Insufficient evidence remains a real outcome

If the owner answers:

`evidence_sufficient = false`

the disposition must be:

`uncertain_insufficient_evidence`.

The interface must not ask the owner to choose same/not-same after declaring evidence insufficient.

This is cleaner than the current text-heavy logic.

## 18. Human prose is not required for scientific rigor

For this audit, scientific rigor comes primarily from:

- frozen candidate selection;
- immutable evidence binding;
- exact asset hashes;
- predetermined adjudication options;
- no post-hoc candidate skipping;
- human personal-inspection attestation;
- preservation of uncertainty;
- prospective hard stop on confirmed leakage;
- immutable categorical outcomes.

It does **not** require the owner to write several sentences for every pair.

Detailed prose can be machine-generated and reported separately with correct provenance.

## 19. Current Document167 form should therefore not be used yet

Document167 itself correctly stops before genuine human input.

That stop should remain in force.

Do **not** ask the owner to fill the currently generated form.

Instead:

1. keep the governance correction and evidence bindings;
2. revise the clarification renderer to categorical-only human input;
3. regenerate the six-rank handoff;
4. run focused/full tests;
5. publish a new additive response/checkpoint;
6. obtain fresh exact CI;
7. review that checkpoint;
8. only then collect the six owner decisions.

## 20. Recommended implementation change

In `prepare_oulu_clarification_batch05.py`, remove human-required textareas for:

- left structure;
- right structure;
- visibility limitation;
- rationale.

Replace the semantic gate with two categorical fields:

```text
evidence_sufficient: null | true | false
same_or_derived_content: null | true | false
```

Validation:

```text
if evidence_sufficient == false:
    same_or_derived_content must be null
    disposition = uncertain_insufficient_evidence

if evidence_sufficient == true:
    same_or_derived_content must be boolean
    true  -> confirmed_same_content_or_derived_lineage
    false -> rejected_false_positive
```

Also retain:

```text
personal_inspection_attested == true
owner_decision_attested == true
```

The owner should never have to type explanatory prose merely to satisfy the completion gate.

## 21. Tests should be updated accordingly

The current synthetic JS gate reports 21 cases because it exercises three dispositions times three wording-disclosure states plus failures.

After simplification, test at minimum:

- sufficient + same;
- sufficient + not-same;
- insufficient + no same/derived answer;
- invalid insufficient + same/derived populated;
- missing sufficiency;
- missing personal inspection;
- missing owner-decision attestation;
- missing asset;
- confirmed same/derived sets hard stop;
- reject does not set hard stop;
- uncertain does not set hard stop.

The exact number of test cases is not important; semantic mapping and fail-closed behavior are.

## 22. Paper/supplement provenance becomes cleaner under this design

This design permits a much cleaner statement later:

> Human reviewers inspected the bound candidate evidence and supplied categorical sufficiency and same/derived-content judgments. Descriptive audit text was generated separately and was not treated as human-authored rationale.

That is more defensible than requiring prose that was partly AI-assisted anyway.

## 23. Current project state remains unchanged

Until the reworked form is reviewed and genuine human decisions are imported:

- targeted clarification completed: 0;
- effective batch-05 activations: 0;
- accepted current total: 40;
- batch05 remains open;
- AI coverage remains 50/85;
- 35 highest-risk candidates remain unreviewed;
- ranks50+ remain blocked;
- model execution remains blocked.

## Final disposition

**DOCUMENT 167 — ACCEPTED FOR GOVERNANCE/PROVENANCE/TECHNICAL PREPARATION.**

**CURRENT HUMAN CLARIFICATION FORM — REWORK REQUIRED.**

The strongest parts of Document167 are accepted:

- correct additive governance repair;
- accurate AI-wording provenance correction;
- exact six-rank scope;
- 18 existing bound assets only;
- rank48-to47 identity binding;
- 21/21 deterministic reexport;
- 46 protected roots unchanged;
- frozen13/config17 unchanged;
- focused 69/69 and full 256/256 passing;
- exact publication CI passing.

However, **human input is not authorized on the current form** because it unnecessarily requires manually typed descriptions and rationales.

### Required UX/protocol rule for this and future manual checks

If the project needs the owner to verify something manually, ask only categorical questions such as:

- **Evidence sufficient? Yes / No**
- **Same or derived content? Yes / No**
- **Personally inspected? Yes / No**
- **Your own decision? Yes / No**

Do not require the owner to type visual descriptions or rationale.

If prose is needed, generate it separately with AI/system tooling and label it as machine-generated. Do not represent it as independently authored human rationale.

**Next step: regenerate the six-rank clarification handoff using categorical-only human input, publish with fresh CI, and review it before collecting new owner answers.**
