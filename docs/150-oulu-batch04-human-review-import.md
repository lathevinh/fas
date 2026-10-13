# Batch04 Genuine Human-Review Import

Date: 2026-10-13
Base commit: `5ec33a8`
Handoff: [Document149](149-review-response-doc148-oulu-batch04-human-handoff.md)
AI-scope authority: [Review148](148-review-doc147-oulu-batch04-ai-review.md)

## Prospective Criteria

Checkpoint1.5AA imports the owner's genuine JSON from the private handoff directory
for original ranks30..39 only. The owner explicitly states that the evidence page
was reviewed and its exported JSON supplied, not that a new external review
document was created. This authorizes import only, not effective activation.

- Bind successful exact handoff CI, published report/definition/page/assets,
  original owner JSON digest, scoped owner authorization and protected evidence.
- Preserve all original answers/rationales/attestations/raw source bytes. Map ranks
  only in memory through the pinned validator; restore original30..39 in outcomes.
- Retain conservative disagreement/uncertainty rules and confirmed scientific
  hard stop; never automatically activate or rewrite AI/human histories.
- Disclose repeated/generic rationale and unresolved heightened-scrutiny reasoning
  for38..39; syntactic validity/agreement is not independent evidence sufficiency.
- Independently reimport/read back13 files, verify overwrite refusal and regression
  in existing `fas`, protected snapshots/frozen13 and stage gates.
- Publish/push for checkpoint review and stop before reconciliation/activation,
  ranks40+, other datasets or models. No repeat human inspection is inferred or
  required merely to establish that the genuine JSON already exists.

## Actual Results

The supplied `oulu-batch04-human-review.json` exists beside the private handoff
page. Its definition, ten packet/asset bindings, original30..39, UTC timestamp,
owner-human identity and global/per-pair personal-review attestations validate.
The timestamp is `2026-10-13T02:16:39.495Z`. Human authorship/inspection remain
reviewer attestations, not independently authenticated or browser-verified facts.

| Item | Result |
|---|---:|
| Genuine human answers imported | 10 |
| Human `rejected_false_positive` | 10 |
| AI/human agreements | 10 |
| Disagreements / confirmed scientific hard stops | 0 / 0 |
| Effective activations | 0 |
| Unique nonblank human rationale texts | 1 across ten |
| Private import files | 13 |
| Independent reimport byte-identical | 13 / 13 |
| Protected prior roots unchanged | 26 |
| Focused / full regression, existing `fas` | 61 / 248 passed, 0 failures/errors |

The [separate adapter](../scripts/import_oulu_human_batch04.py) maps30..39 to
local0..9 only in memory through the unchanged pinned validator, then restores
original ranks. Inputs/definitions are not mutated. All original dispositions,
rationales, attestations and packet/asset fields are preserved in outcome rows.
The source JSON stays byte-identical. Canonical imported `human_input.json` has
the same parsed content, not necessarily the same original serialized bytes.

The validator's `effective_disposition` is a **comparison state only**, not an
accepted current ledger. All outcome activation flags remain false; summary
activation count is0 and batch04 accepted/reconciled state false. Human uncertainty
or disagreement stays uncertain pending separate reconciliation. Human confirmed
same/derived raises the scientific-stop flag; it cannot activate or continue queue.
Tests exercise these rules specifically for38..39 as well as malformed ranks,
missing attestation/rationale and altered definition/packet/asset bindings.

## Rationale And Scrutiny Limits

All ten human rationale strings are identical. Their text was not improved,
rewritten or replaced with AI reasoning. This is valid explicit nonblank input
under the pinned validator, but does not demonstrate pair-specific assessment.
In particular, the required heightened-scrutiny reasoning for haze/veil cases38..39
is **not verified or resolved**. Agreement with AI does not repair that limitation.

The immutable summary records pending Review148 haze scrutiny and no eligibility
for additive activation without further review. Original human rejection answers
are still preserved as answers, not automatically relabeled. A future checkpoint
must resolve the38..39 evidence-reasoning requirement or record an explicitly
reviewed conservative decision before accepted closure; AI cannot synthesize the
missing reasoning. No new inspection/authorship claim or independent accuracy/
inter-rater reliability follows from10 agreements or serialization equality.

The genuine JSON is already present and imported. This is not a missing-input
blocker or a request to repeat the whole review. The remaining issue is evidence
quality/heightened-scrutiny resolution, separate from software import completeness.

## Provenance And Verification

Fresh prerequisite handoff CI is completed/success for exact commit
`5ec33a829e8e3fcd65337f427a126ab01baf461c`,
[run38336188705](https://github.com/lathevinh/fas/actions/runs/38336188705),
[validate115096680331](https://github.com/lathevinh/fas/actions/runs/38336188705/job/115096680331).
Official Actions web evidence binds the full commit and job; absolute completion
time is unavailable and stored null. This is not new-import-checkpoint CI.

Owner authorization is the direct supplied-JSON request clarified as human review
of the evidence page, not a new external review document. No formal external
review of149 was present at import preflight; none is fabricated or silently
substituted. The authorization is scoped to this import, not automatic activation.

Both independent import executions produced13 immutable files: lineage,
canonical human input,ten outcomes,summary. All13 are byte-identical. Actual
readback checks every original input field against outcomes. Existing-output CLI
exits1 and all13 files remain unchanged. Twenty-six protected roots are the prior24
plus original human handoff34 files (including genuine JSON) and rerun33 files.
All accepted33 handoff files remain unchanged; the only additional source file
is the owner JSON. Frozen13, configs, accepted implementations, AI/current/
historical evidence and standalone private evidence remain unchanged.

The [public report](../results/phase1/oulu-human-review-import-batch04-v1.json)
contains aggregate counts, hashes and limitations, no biometric assets, video IDs,
candidate bodies or raw rationale text. Only this new import-only runner, one
neighboring test and public checkpoint files changed. PAGE, pinned validator,
accepted runners, environment and CI workflow remain unchanged.

| Record | SHA256 |
|---|---|
| Original owner JSON | `196ddd68ee2c51385f23de5b1c1d26b253ba8b9ec1f976f4d84ef62c10d42ab6` |
| Import code | `a52ac2e31a958bc277039eac555df2bcdbdebf47b02f05381fe5febfbcdb467d` |
| Private preflight | `9dd7dfcc7f1bf35d7345d1de46c1913dc13ee538fc1152a2139728c4c4b467af` |
| Lineage | `b896c7cf67dcd23e590465a7036f17d83d5bdc6f7d6ea6f6d070236bb60d08d5` |
| Canonical input | `c437c8f1c5801794aaf73cdab3567268d1048f5636faf6b3a750d175511297fd` |
| Outcome bundle | `61777b738988172a7aec763246ef36b13d54d8f20b4721612eb62d7abd0f5e02` |
| Private summary | `5966bf3e79be1ab8b5cbb9a390ff5ab25cf870c1d780a3cdf64a6776c06dd66a` |
| Private verification | `4774bfdf6673fe521ab26ee824cee7c2570d3aadd4b210da18aedaff5efcf115` |

Outcome bundle:SHA256 of ascending `six_digit_rank.json:sha256\n` lines.
Preflight and lineage bind handoff authority, owner input, successful CI, import
code/validator, protected snapshots and scoped owner request. Serialization
reproducibility does not establish independent human review accuracy.

```text
/mnt/e/FAS-private/artifacts/phase1/oulu_owner_review_batch04_v1/oulu-batch04-human-review.json
/mnt/e/FAS-private/artifacts/phase1/oulu_human_dispositions_batch04_v1
/mnt/e/FAS-private/artifacts/phase1/oulu_human_dispositions_batch04_rerun_v1
/mnt/e/FAS-private/artifacts/phase1/oulu_batch04_human_import_preflight_v1.json
/mnt/e/FAS-private/artifacts/phase1/oulu_batch04_human_import_verification_v1.json
```

## Completion And Stop

**Checkpoint1.5AA genuine import is complete, not effective/scientific closure.**
No new human input is missing. Batch04 now has10 human rejects recorded,10 AI
agreements and0 effective activations, with generic rationale and pending38..39
scrutiny disclosed. Prior30 accepted screen relationships remain current; AI
coverage remains40/85 with45 unreviewed, not40 effective relationships.

Stop for review of this pushed import checkpoint and exact CI before separate
scrutiny resolution/reconciliation or any additive activation. No ranks40+, other
dataset, extraction, role/selector/seed/threshold change, research detector/model
or target evaluation is started. Schema passes; data-audit/source-dry-run/analysis-
freeze/locked-evaluation remain fail-closed. No capture certification, global
lineage clearance or scientific readiness is claimed.