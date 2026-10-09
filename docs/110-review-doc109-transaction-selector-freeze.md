# 110 — Review of Document 109: Technical Transaction and Primary-Frame Selector Freeze

Date: 2026-10-09  
Repository: `lathevinh/fas`  
Reviewed commit: `43b179757af371fb39820a226a41f770d0c683d8`  
Reviewed document: `docs/109-review-response-doc108-transaction-selector-freeze.md`

## Verdict

**DOCUMENT 109 — ACCEPTED.**

**CHECKPOINT 1.5E TECHNICAL-TRANSACTION / PRIMARY-FRAME SELECTOR FREEZE — ACCEPTED WITHOUT REWORK.**

No blocker or major methodological issue was found.

The checkpoint resolves the two outstanding issues from Review 108 prospectively and before model execution:

1. deterministic primary-frame selection for even-length videos;
2. explicit handling of pre-detector technical failures without changing frozen roles or silently changing denominators.

Scientific/data readiness remains pending.

## 1. Primary-frame rule is now explicit and prospective

The frozen rule is:

`zero_based_rank = floor((eligible_frame_count - 1) / 2)`

Therefore:

- odd-length sequence: unique middle frame;
- even-length sequence: earlier/lower central frame.

The valid interval is inclusive.

For OULU, the interval is the whole supplied video because accepted metadata provides no temporal trim bounds.

This is acceptable because the rule is frozen before detector/model execution and does not inspect:

- detector success;
- model scores;
- classifier errors;
- target outcomes.

There is also explicitly no detector-success replacement search.

This is consistent with the strict single-image study design.

## 2. The selector does not hide decode defects

The selector operates only on accepted decoded-frame evidence.

A failed decode cannot provide a selected frame.

An empty valid interval is also a technical failure.

Because Document 107 used strict full-video decoding, "successfully decoded frames" for a successful video does not create a loophole that silently skips corrupted frames in order to select a middle frame.

The one known OULU decode failure remains terminal.

## 3. The failed calibration transaction is handled correctly

The single failed OULU record remains:

- canonical ID retained;
- binary label retained;
- permanent role retained;
- original class denominator retained;
- technical-coverage denominator retained.

It does not receive:

- a model score;
- an embedding;
- a classifier error;
- a fabricated detector-success state.

Instead:

- `model_score = null`;
- `classifier_error = null`;
- `detector_status = not_run`;
- `final_k1_action = non_accept`.

This is methodologically correct.

## 4. Calibration fitting population is correctly conditional

For OULU `branch_calibration`:

| Population | Original | Frame available | Technical failure | Current score-fit rows |
|---|---:|---:|---:|---:|
| Bona fide | 198 | 197 | 1 | 0 |
| Attack | 792 | 792 | 0 | 0 |
| Total | 990 | 989 | 1 | 0 |

The report correctly distinguishes:

- original transaction denominator;
- frame-available population;
- later detector-success/model-score fitting population.

`989` is **not** claimed to be the final calibration sample count.

Actual calibration rows require a valid model score after successful detection.

This distinction prevents silent denominator drift.

## 5. Scoreless failures are correctly excluded from score-dependent metrics

A terminal pre-detector failure cannot enter:

- calibration fitting;
- classifier fitting;
- risk-model fitting;
- AP;
- AURC;
- classifier-error prevalence.

Those quantities require the relevant score/error evidence.

This is correct and consistent with the study's detector-success-only risk population.

At the same time, the transaction remains present in end-to-end accounting.

## 6. End-to-end K=1 accounting is coherent

A technical failure has terminal action:

`non_accept`.

Therefore:

- a bona-fide technical failure contributes to bona-fide non-accept / false-reject accounting;
- an attack technical failure cannot create a false accept.

This is a coherent conservative operational rule.

### Terminology note

The report calls the bona-fide contribution a `forced_bfnr_numerator`.

That is acceptable internally, but paper-facing language should make clear that this is an **end-to-end technical non-accept contribution**, not a measured model/classifier BFNR at this checkpoint.

Document 109 already states that no model BFNR or calibrated performance result is computed here.

This is a clarity note only, not a required rework.

## 7. The policy is properly frozen before model execution

`configs/transaction_policy_v1.yaml` records:

- `state = frozen_before_model_execution`;
- deterministic primary-frame selection;
- terminal technical-failure handling;
- denominator retention;
- no canonical/role rewrite;
- no split/seed retry;
- `model_execution_authorized = false`;
- `scientific_readiness = false`.

Its bytes are bound into future analysis-freeze lineage.

This is the correct order of operations.

## 8. Frozen study inputs remain unchanged

The checkpoint preserves:

- all 13 frozen canonical/role artifacts;
- split seed `20261009`;
- existing preprocessing;
- previous media evidence;
- permanent source roles.

No AVI was redecoded or repaired.

No role was regenerated.

No media defect triggered a seed retry.

This satisfies the prospective-study requirement.

## 9. Reproducibility evidence is strong

The private export contains:

- one frozen definition;
- 4,950 transaction records;
- one summary.

Total:

`4,952` artifacts.

Original and rerun exports are byte-identical.

An attempt to write into an existing output is rejected without changing existing bytes.

This is appropriate immutable-export behavior.

## 10. Primary-frame identities are fully reconciled

The export contains:

- 4,949 deterministic primary-frame identities;
- 1 retained terminal technical failure.

Each selected frame identity is checked against the accepted decode index.

No frame pixels are published.

This gives a clean bridge from media audit to future preprocessing without yet running the detector or model.

## 11. Tests are adequate

Reported tests:

- focused: **31/31**;
- full regression: **218/218**;
- zero failures/errors.

Coverage includes:

- odd/even/singleton selection;
- inclusive and empty intervals;
- failed calibration transaction;
- null classifier evidence;
- invalid frame indices;
- policy drift;
- duplicate identities;
- denominator retention;
- K=1 integration;
- private-output boundaries.

This is appropriate for the new policy layer.

## 12. Fresh CI passes

Fresh GitHub Actions on exact commit:

`43b179757af371fb39820a226a41f770d0c683d8`

completed successfully.

Therefore checkpoint acceptance is based on the actual pushed implementation rather than local-only evidence.

## 13. Scientific gates remain correctly blocked

Current state remains:

- schema: pass;
- data-audit: blocked;
- source-dry-run: blocked;
- analysis-freeze: blocked;
- locked-evaluation: blocked;
- model execution unauthorized;
- scientific readiness false.

This is correct.

Freezing an execution definition is not execution authorization.

## 14. Remaining work

The next major unresolved data-side tasks are now:

1. near-duplicate/content-lineage audit for OULU;
2. equivalent media audits for CASIA-FASD;
3. equivalent media audits for MSU-MFSD;
4. equivalent media audits for SiW-Mv2;
5. cross-dataset exact/near-duplicate checks once comparable per-video evidence exists;
6. then complete the core data-audit gate.

Only after those data gates are closed should source-only detector/model execution proceed.

Later event insufficiency or poor model behavior must not alter the frozen frame rule, role split or seed.

## Final disposition

**DOCUMENT 109 — ACCEPTED.**

**CHECKPOINT 1.5E TECHNICAL TRANSACTION / PRIMARY SELECTOR FREEZE — ACCEPTED WITHOUT REWORK.**

The previously unresolved OULU decode-failure handling and even-frame primary-selector convention are now prospectively frozen.

**No model execution or scientific-readiness promotion is authorized by this acceptance.**
