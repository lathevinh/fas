# Response to Review 108: Technical Transactions and Primary Selector

Date: 2026-10-09
Base commit: `dce0937`
Review: [Document 108](108-review-doc107-oulu-per-video-media-audit.md)

Review 108 accepts checkpoint 1.5D without rework. This checkpoint 1.5E freezes
the prospective pre-detector failure handling and primary-frame tie convention
before any model execution. It does not regenerate the split, repair media, run
models, perform near-duplicate analysis or advance to another dataset.

## Frozen Definition

[Transaction policy](../configs/transaction_policy_v1.yaml) is a new explicit
definition, not a claim that the old policy already specified a median tie.
Existing preprocessing, canonical records, source roles and split seed 20261009
are unchanged. The new policy bytes are bound into future analysis-freeze lineage.

Select the lower median of successfully decoded frames in the valid interval:
zero-based eligible rank `floor((n - 1) / 2)`. For even `n`, choose the earlier
central frame. Interval bounds are inclusive. Selection never examines model
scores, classifier errors or face-detector success, and never searches for a
detector-successful replacement. Empty eligible intervals are terminal failures.
OULU uses the whole supplied video because accepted metadata has no temporal
trim bounds; no independently certified interval is invented.

A pre-detector technical failure retains its canonical ID, label and permanent
role. It remains in original class and technical-coverage denominators and has
terminal K=1 `non_accept`. A failed bona fide contributes one forced BFNR
numerator; a failed attack cannot contribute a false accept. These are accounting
contributions, not computed model/system performance results.

No model score, embedding or classifier error is fabricated: these stay null and
detector status is `not_run`. Score-dependent calibration, classifier/risk fitting,
AP/AURC and classification-error prevalence cannot include a scoreless failure.
Their conditional masks/counts must be reported alongside original transaction
denominators, identically across paired systems. Calibration additionally requires
an actually valid model score after detector success, not mere frame availability.
Failure of class/event feasibility is an applicability outcome, never a seed or
split retry. When OULU is the outer target, none of its roles authorize source fitting.

## Completion Criteria

- Verify the accepted 4950-record media bundle and all 13 frozen artifacts.
- Export one immutable private selector/disposition record per canonical ID.
- Preserve all failures and original role/class denominators without fitting.
- Bind policy, selector implementation, review and accepted media evidence.
- Reproduce identical private artifact hashes; refuse existing/unsafe output.
- Pass focused/full tests, publish aggregate evidence and push for owner review.

[Selector/accounting](../src/fas/transactions.py) and
[export CLI](../scripts/freeze_oulu_transactions.py) implement this definition.
The existing K=1 accounting contract now accepts `detector_status=not_run` only
for a terminal pre-detector technical failure, and rejects invented classifier
evidence. Its original class denominators are unchanged.

## Actual Evidence

The [immutable aggregate report](../results/phase1/oulu-transaction-selector-freeze-v1.json)
binds the policy, Review 108, accepted media bundle, selector/export implementation
and private definition/transaction bundle. Original and rerun private exports have
**4952 byte-identical artifacts** each: definition, 4950 transaction records and
summary. An existing-output retry returns exit code 1 without changing any bytes.

Every selected identity was independently matched to the accepted decode index:
**4949** deterministic primary frames, **1** retained terminal decode failure.
No AVI was reopened or redecoded, no frame pixels were exported, and no detector,
classifier, calibration or risk model was run. All model scores/classifier errors
remain null. All 13 canonical/role artifacts, old preprocessing and split seed
remain unchanged; the earlier accepted reports are preserved.

| Calibration population | Original denominator | Frame available | Terminal technical failure | Actual score-fit rows |
|---|---:|---:|---:|---:|
| Bona fide | 198 | 197 | 1 | 0 |
| Attack | 792 | 792 | 0 | 0 |
| Total | 990 | 989 | 1 | 0 |

The failed bona fide retains its `branch_calibration` assignment. Its forced
non-accept contribution is one BFNR numerator under the original 198 bona-fide
transactions. No model BFNR, calibrated performance or applicability result is
computed here. Later detector/score availability can further reduce the fitting
population; 989 is a frame-available count, not a fitted calibration sample count.

**31 focused / 218 full regression tests pass**, with zero failures/errors and
no editor diagnostics. Tests cover odd/even/singleton selection, inclusive/empty
intervals, failed calibration/null errors, invalid indices, policy drift, private
output boundaries, duplicate IDs, denominator retention and K=1 integration.
Policy bytes are included in future analysis-freeze artifact hashes.

Schema passes; data-audit, source-dry-run, analysis-freeze and locked-evaluation
remain blocked. This freezes an execution definition, not execution authorization.
Stop for owner checkpoint review after publication. Near-duplicate lineage,
cross-dataset checks and the other three media audits remain separate checkpoints.