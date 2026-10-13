# 146 — Review of Document 145: OULU Batch-04 Packet Preparation

Date: 2026-10-13  
Repository: `lathevinh/fas`  
Reviewed commit: `d13904f450c7642d4be5b7cbd866771793b4fe68`  
Reviewed document: `docs/145-review-response-doc144-oulu-batch04-packets.md`

## Verdict

**DOCUMENT 145 — ACCEPTED.**

**CHECKPOINT 1.5X OULU BATCH-04 PRIVATE PACKET PREPARATION — ACCEPTED WITHOUT REWORK.**

**BATCH 04 VISUAL ADJUDICATION HAS NOT STARTED YET.**

Document 145 correctly performs only the bounded evidence-preparation step authorized by Review 144. It prepares the next fixed frozen queue batch, ranks 30–39, preserves the prior accepted state, performs no AI/human/effective adjudication, and stops before ranks 40+.

With this review acceptance, AI-assisted visual review of ranks 30–39 may begin.

## 1. Queue progression is correct

The batch-04 runner requires accepted batch-03 closure before any new candidate can be selected.

Specifically, it requires:

- `batch03_accepted_reconciled_disposition_state = true`;
- `effective_dispositions_activated = 10`;
- `current_effective_disposition_counts = {"rejected_false_positive": 10}`.

Only after these checks pass does it select:

```python
records[30:40]
```

It then verifies every selected row has:

- queue rank exactly 30 through 39;
- priority exactly `cross_role_conflicting_label`.

This is a strong fail-closed continuation rule.

## 2. No outcome-dependent selection is visible

The selected ranks are fixed:

30, 31, 32, 33, 34, 35, 36, 37, 38, 39.

The public aggregate explicitly records:

`outcome_dependent_selection = false`.

There is no evidence of:

- skipped candidates;
- candidate replacement;
- threshold retuning;
- role repair;
- seed retry;
- outcome-dependent queue modification.

## 3. Preparation remains cleanly separated from adjudication

The batch-04 packets retain:

- `review_performed = false`;
- `disposition = awaiting_visual_review`.

The checkpoint reports:

- AI dispositions: 0;
- human dispositions: 0;
- effective dispositions: 0;
- images actually visually reviewed: 0.

Therefore successful decode/hash verification is not being misrepresented as visual clearance.

## 4. Evidence generation is internally consistent

Document 145 reports:

- 10 fixed pair packets;
- 15 unique source videos;
- 1,690 accepted RGB frames verified;
- 1,690 private frame PNGs;
- 20 temporal-panel PNGs;
- 10 trigger PNGs;
- 15 video manifests;
- lineage + summary;
- total private export files: 1,747.

The arithmetic is consistent:

`1690 + 20 + 10 + 15 + 10 + 2 = 1747`.

The total persisted PNG count is also consistent:

`1690 + 20 + 10 = 1720`.

## 5. Full RGB verification is stronger than file-existence checking

For every selected source video, the runner:

- reopens the pinned archive;
- verifies archive-member metadata;
- extracts the selected media payload;
- verifies payload byte size;
- verifies payload SHA-256;
- decodes the video;
- verifies decoded RGB frames against the accepted media audit;
- persists private thumbnails only after verification.

This binds the prepared review evidence to the already accepted source-media state.

## 6. Trigger selection remains deterministic

The runner recomputes the minimum pHash Hamming witness from the accepted fingerprint samples.

It requires the recomputed distance to equal the frozen candidate's:

`candidate["minimum_hamming"]`.

The trigger decode orders are therefore derived from previously accepted screening evidence rather than selected after visual inspection.

This is a useful protection against outcome-driven evidence selection.

## 7. Temporal evidence remains fixed and reproducible

Each video manifest stores:

- verified frame identities;
- accepted RGB SHA-256 values;
- thumbnail SHA-256 values;
- fixed 17-slot temporal review orders.

The temporal panels are reconstructed from these fixed orders.

This ensures that later visual review sees the evidence prepared by the frozen protocol, not manually substituted frames.

## 8. Accepted upstream evidence is revalidated

Before preparing batch 04, the runner verifies:

- Review 144 authority;
- exact successful batch-03 activation CI;
- accepted batch-03 activation report;
- activation summary;
- activation record;
- successful-CI observation;
- current effective pair bundle;
- exact candidate queue bundle;
- frozen source-role artifacts;
- accepted visual code/policy;
- prior packet-runner hashes;
- media-audit bundle;
- fingerprint bundle;
- archive pins and file identities;
- locked FFmpeg version.

This is an appropriately strict provenance chain.

## 9. Prior accepted evidence remains unchanged

Twenty protected prior roots remain byte-identical.

All 13 frozen artifacts remain unchanged.

Accepted batch-01, batch-02 and batch-03 runners and records remain unchanged.

No previous human input or current/historical ledger is reopened or rewritten.

## 10. Independent redecode/reexport is strong

The initial export contains:

**1,747 files.**

A fresh independent run:

- reopens the same 15 media payloads;
- re-decodes the videos;
- re-verifies the source frames;
- reconstructs the private evidence;
- writes to a separate fresh root.

Result:

**1,747 / 1,747 files are byte-identical.**

This is strong evidence-generation reproducibility.

## 11. PNG readback is complete

The checkpoint reports:

**1,720 / 1,720 persisted PNGs decoded and hash-verified.**

This covers:

- 1,690 frame thumbnails;
- 20 temporal panels;
- 10 trigger images.

The readback also verifies packet/manifests and panel/trigger reconstruction.

## 12. Overwrite protection is correct

Existing-output execution exits with code 1.

The original evidence remains unchanged.

Both original and replay output roots exist as immutable sibling roots rather than overwriting accepted artifacts.

Temporary AVI extraction files are not retained.

This is appropriate evidence hygiene.

## 13. The new selector test is useful

The newly added regression test protects the batch-transition logic.

It checks that batch-04 preparation fails when the prior batch is not properly closed or when the queue/rank conditions are not exact.

This directly reduces the risk of accidentally starting the wrong queue slice.

## 14. Local regression evidence is strong

Document 145 reports:

- focused regression: **59/59 passed**;
- full regression: **246/246 passed**;
- zero failures/errors.

A full regression rerun is appropriate because the new batch-04 runner and test were introduced.

## 15. Fresh CI for the exact Document-145 commit passes

Fresh GitHub Actions for exact commit:

`d13904f450c7642d4be5b7cbd866771793b4fe68`

completed successfully.

Run:

`38328370472`

Validate job:

`115072236960`

completed successfully.

The exact job passes:

- checkout/setup;
- FFmpeg installation;
- model-free screening dependencies;
- synthetic regression suite;
- canonical schema validation;
- unavailable-stage fail-closed checks;
- legacy-stage rejection checks.

There is therefore no CI blocker on checkpoint 1.5X.

## 16. Current queue state is correct

Before batch-04 adjudication:

- 30 highest-risk relationships are already resolved at screen level;
- 55 highest-risk relationships still lack AI visual review;
- 10 of those 55, ranks 30–39, now have prepared packets;
- 45 remain not yet prepared.

Thus:

**30 resolved + 10 prepared/pending review + 45 not prepared = 85.**

## 17. Preparation is not clearance

The current 10 prepared pairs have not been visually adjudicated.

Packet preparation does not establish:

- content independence;
- capture independence;
- full-video independence;
- absence of crop/re-encode relationships;
- absence of partial/shifted/transformed overlap;
- global OULU lineage clearance.

The document correctly avoids those claims.

## 18. Next permitted step

After acceptance of Document 145, the project may perform:

**AI-assisted visual review of ranks 30–39 only.**

The visual-review checkpoint should:

- inspect only the 30 bound assets;
- preserve frozen queue order;
- record pair-specific rationale;
- allow uncertainty;
- immediately trigger a scientific hard stop if any pair is `confirmed_same_content_or_derived_lineage`;
- create AI proposals only;
- create no human or effective dispositions.

## 19. Ranks 40+ remain paused

Ranks 40+ should not be prepared yet.

The batch-04 AI review must first be published and reviewed before the next workflow step.

This preserves the same prospective staged structure used for previous batches.

## 20. Scientific/model gates remain blocked

This checkpoint does not authorize:

- OULU data-audit completion;
- source-dry-run;
- analysis freeze;
- locked target evaluation;
- classifier/risk-model execution;
- target-domain experiments;
- scientific readiness.

These stages remain fail-closed.

## Final disposition

**DOCUMENT 145 — ACCEPTED.**

**CHECKPOINT 1.5X OULU BATCH-04 EVIDENCE PREPARATION — ACCEPTED WITHOUT REWORK.**

Batch 04 is now validly prepared:

**10 fixed pairs (ranks 30–39), 15 videos, 1,690 verified RGB frames, 30 bound review images, 0 new dispositions.**

**The next permitted step is AI-assisted visual review of ranks 30–39 only.**

Do not begin ranks 40+ or research-model execution yet.
