# 90 - Response to Document 89: Dataset Holdout and Evaluation Population

Date: 2026-10-09
Review: [Document 89](89-review-doc88-benchmark-amendment.md)
Reviewed implementation: `6ad2d37eabd1388f29844cc51c791e4885ad420b`
Owner review upload: `cf523eb`
Disposition: accept the required wording/estimand clarification; checkpoint 1.3A remains accepted

## 1. Acceptance and correction

Document 89 accepts the benchmark amendment without a population, decision-rule,
target-tuning or OOF-comparison blocker. Its required distinction is correct:
**dataset exclusion is not the same as evaluation of the entire dataset release**.
The existing counts, membership and executable source/target partition policy were
already correct. This response fixes their prose interpretation, not the experiment.

The design is cross-dataset held-out evaluation using dataset-specific frozen source
and evaluation populations. In OCM->S, SiW-Mv2 is held out as a dataset, and evaluation
uses its frozen Protocol-I test-intersection population of 623 videos. No SiW-Mv2
sample enters fitting, calibration, gate selection or method selection for that fold.
The 1057 train-intersection videos are not target transactions in that fold; they
are source-eligible only in other outer folds. The 1680-video combined inventory
is not the SiW-Mv2 target population.

The risk/conditional-score population is the prescribed detector-success subset of
the 623 attempted target transactions; end-to-end accounting retains genuine
detector failures. Missing references and out-of-protocol exclusions do not become
attempted transactions. These existing estimands and denominator rules do not change.

Source-domain OOF still excludes the complete source dataset from fitting in its
pseudo-fold, but scores its prescribed OOF candidate pool inside the frozen
source-eligible population. It does not import that dataset's outer-test partition.

## 2. Updated documents and unchanged contracts

The clarification is incorporated in the
[paper skeleton](40-paper-skeleton.md),
[canonical implementation plan](42-data-to-experiment-implementation-plan.md), and
[dated amendment](88-phase1-benchmark-amendment-siwmv2.md).
README and checkpoint governance now record Document 89's acceptance rather than
pending amendment review. Historical MCIO remains literature context only.

The five coarse families remain versioned project metadata, not the provider's
native ontology. The 14 reference attack types and the frozen type/family mapping
remain intact for future attack-shift analyses.

No code, configs, seeds, membership hashes, counts, source roles, fitting objectives,
RQ1/RQ2 formulas, decision rules or media-readiness status are changed by this response.
Document 88's 146-test implementation evidence belongs to the reviewed commit;
it is not a claim that full regression was rerun for this prose-only response.

## 3. Verification and next boundary

Verification criteria for this response: population wording in all three controlling
documents matches the frozen public evidence (1057 source, 623 target, 1680 combined);
schema remains ready in conda `fas`; all local document links resolve; executable
contracts and frozen evidence have no diff.

Observed local checks: population/prose assertions and local links pass; canonical
schema exits 0 in `fas`; `git diff --check` passes. Only Markdown files changed;
code, configs, tests, manifests and result artifacts are unchanged. Full regression
was not rerun locally for this documentation-only response.

Checkpoint 1.3A is accepted, not reopened for another conceptual review. Document 89
permits the SiW-Mv2 metadata adapter as the next separate implementation checkpoint.
This response does not start that adapter, the MSU adapter, media extraction,
training or target evaluation. The owner-confirmed incremental checkpoint policy
still governs each subsequent implementation and audit.