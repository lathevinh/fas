# 170 — Review of Document 169: OULU Batch-05 Categorical-Only Clarification Handoff

Date: 2026-10-15  
Repository: `lathevinh/fas`  
Reviewed commit: `de9ab7fcd15bb5772ba1a63b67f3946a08bf1f95`  
Reviewed document: `docs/169-review-response-doc168-oulu-batch05-categorical-handoff.md`

## Verdict

**DOCUMENT 169 — ACCEPTED WITHOUT REWORK.**

**CATEGORICAL-ONLY BATCH-05 HUMAN HANDOFF — ACCEPTED FOR GENUINE OWNER USE.**

**OWNER MAY NOW COMPLETE THE NEW CATEGORICAL FORM FOR RANKS 40, 41, 42, 43, 48, 49 ONLY.**

**DO NOT USE THE OLD DOCUMENT167 PROSE FORM OR ITS OLD SIX-ROW JSON.**

**FOLLOW-UP IMPORT, SEMANTIC ACCEPTANCE, ACTIVATION, AND RANKS 50+ REMAIN SEPARATE BLOCKED CHECKPOINTS.**

Document169 directly fixes the blocker raised in Review168: it removes all required owner-authored visual descriptions/rationales and retains only the categorical judgments and attestations needed for scientific adjudication.

## 1. Review168 requirement is satisfied

The form now requires only:

- `evidence_sufficient`;
- `same_or_derived_content`;
- `personal_inspection_attested`;
- `owner_decision_attested`.

No human prose is required and no per-pair wording-assistance disclosure is required.

## 2. Categorical mapping is correct

| Evidence sufficient | Same/derived | Disposition |
|---|---|---|
| No | null | `uncertain_insufficient_evidence` |
| Yes | Yes | `confirmed_same_content_or_derived_lineage` |
| Yes | No | `rejected_false_positive` |

Insufficient evidence with a populated same/derived value is rejected as invalid.

## 3. Scientific hard stop is preserved

`evidence_sufficient=true` plus `same_or_derived_content=true` maps to `confirmed_same_content_or_derived_lineage` and sets the prospective scientific hard stop.

Rejection and uncertainty do not.

## 4. Human workload is now appropriate

The owner only needs to inspect the bound images and answer Yes/No questions. No visual description, visibility paragraph, rationale, or writing-assistance prose is required.

This cleanly separates human decision ownership from machine-generated explanatory wording.

## 5. Human decision ownership is preserved

Each valid pair requires:

- personal inspection = Yes;
- own decision = Yes.

This is sufficient to record human adjudication without conflating it with prose authorship.

## 6. AI context is delayed appropriately

Earlier AI context remains hidden until the owner submits a valid pair judgment. Editing the pair invalidates submission and hides AI context again.

This reduces anchoring while correctly avoiding a claim of full blinding.

## 7. Old-form input is not reused

The previously supplied six-row Document167 JSON remains preserved but unimported. It is not converted, prefilled, or relabeled as a categorical review.

New categorical answers must be genuinely supplied using the new accepted form.

## 8. Scope is correct

Targets remain exactly:

`40, 41, 42, 43, 48, 49`.

Clean ranks `44..47` are not reopened.

Only 18 already-bound PNG assets are used. No new decode, extraction, AI visual review, or model execution occurs.

## 9. Rank48 treatment is correct

Rank48 remains bound to evidence byte-identical to rank47. Prior inspection of the identical evidence may be relied upon, but rank48 still requires its own categorical decision.

No earlier answer is copied.

## 10. Dependent-state logic is correct

Changing evidence sufficiency resets the same/derived answer to null.

The same/derived question is shown only when evidence is sufficient.

Any edit invalidates the prior submission.

This prevents stale or inconsistent records.

## 11. Image loading is only a technical safeguard

All three assets must load before a pair can be submitted. This is useful technically, but the project correctly keeps personal inspection as a separate explicit attestation.

## 12. Export gate is adequate

Export requires:

- all six valid submitted judgments;
- all three images loaded per pair;
- personal inspection = Yes;
- own decision = Yes;
- nonblank reviewer ID.

This is sufficient for the intended record.

## 13. No new machine narrative is generated

No machine descriptive prose is generated in this checkpoint.

If prose is later needed, it must remain separate from the authoritative human categorical judgment and be explicitly labeled machine-generated.

## 14. Reproducibility is strong

Each new private root contains 21 files:

- 18 PNG assets;
- definition;
- HTML;
- summary.

Main and sibling match **21/21 byte-identically**.

Protected roots remain 48; frozen artifacts remain 13; study configs remain 17.

## 15. Regression evidence is strong

Document169 reports:

- focused regression: **70/70 passed**;
- full regression: **257/257 passed**;
- pure-JS synthetic tests: **32 cases passed**.

The JS tests cover the three valid mappings, invalid boolean/null combinations, missing attestations, missing assets, submission/export gates, hard-stop derivation, bindings/ranks, absence of human prose export, and AI-context hide/reveal behavior.

## 16. Private-browser 403 is not a blocker

Automated opening of the actual private HTML still returns 403 because it is outside the trusted folder. Real desktop/mobile rendering and actual local export are therefore not independently automated-verified.

This limitation remains correctly disclosed.

The owner may use the local form in a normal browser. If the real form fails, do not manually fabricate JSON; fix it in a new checkpoint.

## 17. Fresh exact publication CI passes

Exact reviewed commit:

`de9ab7fcd15bb5772ba1a63b67f3946a08bf1f95`

Fresh GitHub Actions run:

`38555628657`

completed successfully.

Validate job:

`115823926504`

also completed successfully.

There is no publication-CI blocker.

## 18. Formal review ordering is now restored

Document169 stopped before collecting new categorical answers.

This Review170 supplies the required formal review.

The intended order is now:

`prepare categorical handoff -> formal review -> genuine owner decisions -> separate import`.

The owner may now use the new form.

## 19. Exact form to use

Use only:

`E:\FAS-private\artifacts\phase1\oulu_owner_categorical_batch05_v1\index.html`

Export:

`oulu-batch05-categorical-review.json`

Do not use the old Document167 prose form or `oulu-batch05-targeted-clarification.json`.

## 20. What the owner needs to answer

For each pair:

1. Evidence sufficient? — Yes / No
2. If Yes: Same or derived content? — Yes / No
3. Personally inspected? — Yes / No
4. Is this your own decision? — Yes / No

No prose is required.

## 21. What remains blocked after export

The new categorical JSON must be handled by a separate importer checkpoint that verifies Review170 authority, exact form/definition/source hashes, categorical mapping, hard-stop behavior, immutable history, regressions, and fresh CI.

That imported state then requires review before activation.

## 22. Current state remains unchanged

At this review:

- new categorical human reviews: 0;
- effective batch05 activations: 0;
- accepted current total: 40;
- batch05 remains open;
- semantic clearance remains pending;
- AI coverage remains 50/85;
- 35 highest-risk candidates remain unreviewed.

## Final disposition

**DOCUMENT169 — ACCEPTED WITHOUT REWORK.**

**THE NEW CATEGORICAL-ONLY FORM IS AUTHORIZED FOR GENUINE OWNER USE ON RANKS 40,41,42,43,48,49 ONLY.**

The implementation now matches the intended policy:

**human makes categorical decisions; human does not have to write prose.**

After the owner exports `oulu-batch05-categorical-review.json`, stop and create a separate reviewed categorical-import checkpoint.

Do not activate batch05 or continue to ranks50+ directly.
