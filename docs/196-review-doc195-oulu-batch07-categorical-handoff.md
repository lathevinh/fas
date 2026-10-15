# 196 — Review of Document 195: OULU Batch-07 Categorical Human Handoff

Date: 2026-10-15  
Repository: `lathevinh/fas`  
Reviewed commit: `3f648377a7d273fc1f35202d101692423e4d9d40`  
Reviewed document: `docs/195-review-response-doc194-oulu-batch07-categorical-handoff.md`  
Reviewed aggregate: `results/phase1/oulu-categorical-handoff-batch07-v1.json`  
Reviewed runner: `scripts/prepare_oulu_categorical_batch07.py`

## Verdict

**DOCUMENT 195 — ACCEPTED WITHOUT REWORK.**

**BATCH-07 CATEGORICAL-ONLY HUMAN HANDOFF FOR EXACT RANKS 60..69 — ACCEPTED FOR GENUINE OWNER USE.**

**THE OWNER MAY NOW OPEN THE NEW BATCH-07 LOCAL FORM AND SUPPLY CATEGORICAL DECISIONS FOR ALL TEN RANKS.**

**NO HUMAN PROSE IS REQUIRED.**

**THE NINE AI REJECTIONS AND ONE AI UNCERTAINTY REMAIN NON-BINDING AND MUST NOT BE PREFILLED OR SUBSTITUTED FOR OWNER DECISIONS.**

**AFTER EXPORT, STOP FOR A SEPARATE CATEGORICAL IMPORT / RECONCILIATION CHECKPOINT.**

**BATCH-07 ACTIVATION, RANK70+, OTHER DATASETS, SOURCE DRY RUN, ANALYSIS FREEZE, LOCKED EVALUATION, AND RESEARCH-MODEL EXECUTION REMAIN BLOCKED.**

Accepted effective screen-level total remains **60**. Accepted AI-screen coverage remains **70/85**.

## Key findings

Review194 was committed before Document195 and explicitly authorized preparation of this human handoff only. There is no governance-order violation.

The handoff covers exactly ranks `60..69`. All ten ranks require separate human decisions; the single AI-uncertain case is not isolated for special handling, and the nine AI rejections are not silently promoted to human decisions.

All human fields start blank/null. The required categorical fields remain:
- evidence sufficiency;
- same/derived content when sufficient;
- personal-inspection attestation;
- own-decision attestation.

The strict mapping is preserved:
- insufficient evidence -> `uncertain_insufficient_evidence`;
- sufficient + same/derived Yes -> `confirmed_same_content_or_derived_lineage` and scientific hard stop;
- sufficient + same/derived No -> `rejected_false_positive`.

Changing evidence sufficiency resets the dependent same/derived answer. Any answer edit invalidates pair submission and re-hides AI context. AI context is revealed only after a valid pair submission. The workflow correctly does not claim full blinding because AI data remain embedded in the page.

No AI answer is preselected. In particular, the accepted AI distribution of 9 rejection proposals + 1 uncertain proposal remains non-binding.

The runner provides neutral visibility notices for reflection, grain/color cast, haze/darkness, occlusion, underexposure, veil, and dark garment regions. These notices do not prescribe a disposition. Correlated reuse for ranks67..68 is disclosed and each rank still requires a separate decision.

The handoff reuses exactly the existing three accepted assets per rank: temporal A, temporal B, and trigger. No extra media was decoded or created merely because the AI retained one uncertain case.

Every rank is rebound to its accepted packet, AI row, frozen pair record and exact asset hashes. Each source asset is checked before copy, and each copied asset is rehashed against its expected digest.

Main and sibling preparations each contain 33 files: 30 PNG assets, review definition, HTML page and summary. They match **33/33 byte-for-byte**. This is deterministic preparation replay only, not independent adjudication.

The initial whole-page comparison difference was correctly traced to JSON key ordering after immutable sorted serialization. Structured embedded DATA equality plus non-DATA byte equality resolved the issue without regenerating or overwriting the prepared evidence.

Output safety remains fail-closed. Actual probes reject existing outputs, repository paths, source-overlap paths and symlink outputs. Additional authority probes reject wrong source193 CI, wrong Review194 authority and premature human-collection authorization. Immutable overwrite probes also fail as expected.

Protected prior state remains stable: 69 prior roots, frozen13, config17, prior owner bytes/fields, historical pending/nonactivation records and accepted helper/source pins remain unchanged.

Local regressions are clean:
- focused **79/79 passed**;
- full **266/266 passed**;
- synthetic JavaScript **50 cases passed**.

The synthetic JS checks cover blank initial state, all three categorical outcomes, strict boolean/null handling, asset and attestation gates, explicit pair submission, reviewer gating, hidden/revealed/re-hidden AI context, export bindings, no mandatory human prose and hard-stop propagation.

The integrated browser still cannot exercise the private local page because it returns:

`403 Forbidden. File does not reside within a trusted folder.`

Therefore actual private browser rendering, clicks and export remain unverified in that environment. This is a real limitation but not a blocker for genuine owner use in the owner's normal local browser.

If the local form fails to render, load assets, respond to controls or export, **do not manually fabricate the categorical JSON**. Stop and create a reviewed UI-fix checkpoint.

Fresh exact Document195 publication CI passes:
- commit `3f648377a7d273fc1f35202d101692423e4d9d40`;
- run `38710625142` — `completed / success`;
- validate job `116340807019` — `completed / success`.

## Additive acceptance

Historical creation-time fields in Document195 remain immutable, including:
- `checkpoint_review_required_before_human_input = true`;
- `human_input_collection_authorized = false`;
- `import_authorized = false`;
- `effective_activation_authorized = false`.

Do not rewrite those fields.

**Review196 is the additive authority that now permits genuine owner use of the prepared batch07 categorical handoff.**

## Owner action now authorized

For every rank60..69:

1. inspect the three bound assets;
2. answer whether evidence is sufficient;
3. if sufficient, answer same/derived Yes or No;
4. attest personal inspection;
5. attest the decision is the owner's own;
6. submit the pair.

No explanatory prose is required.

The AI-uncertain rank remains a normal human decision: the owner may independently decide uncertain, confirmed same/derived, or rejected false positive according to the categorical mapping.

Likewise, the nine AI rejection proposals remain non-binding.

## Stop boundary after owner export

After the genuine batch07 categorical JSON is exported:

- do not activate dispositions;
- do not edit historical records;
- do not start rank70+;
- do not run source dry run/model/scientific stages.

The next checkpoint must be a separate importer/reconciliation stage.

That importer should independently rederive dispositions and hard-stop state from the strict categorical answers, preserve AI and owner results separately, and explicitly record any AI/human disagreement.

Effective activation must remain a later separate checkpoint.

## Current state

- accepted effective screen-level total: **60**
- accepted AI-screen coverage: **70/85**
- remaining not yet AI-screened: **15**
- genuine batch07 human decisions before owner uses form: **0**
- batch07 activation: **0**

## Final disposition

**DOCUMENT 195 — ACCEPTED WITHOUT REWORK.**

**BATCH07 CATEGORICAL-ONLY HUMAN HANDOFF FOR EXACT RANKS60..69 — ACCEPTED FOR GENUINE OWNER USE.**

**NO HUMAN PROSE IS REQUIRED.**

**ALL HUMAN ANSWERS MUST BEGIN BLANK.**

**THE NINE AI REJECTIONS AND ONE AI UNCERTAINTY REMAIN NON-BINDING.**

**OWNER INPUT MAY NOW BE COLLECTED THROUGH THE ACCEPTED LOCAL FORM.**

**AFTER EXPORT, STOP FOR A SEPARATE CATEGORICAL IMPORT / RECONCILIATION CHECKPOINT.**

**ACCEPTED EFFECTIVE TOTAL REMAINS 60.**

**AI-SCREEN COVERAGE REMAINS 70/85.**

**RANK70+, OTHER DATASETS, AND RESEARCH-MODEL / LATER SCIENTIFIC STAGES REMAIN BLOCKED.**

If the actual local form fails, do not fabricate the JSON manually; fix the form in a new reviewed checkpoint.
