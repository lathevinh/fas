# 89 — Review of Document 88: Dated SiW-Mv2 Benchmark Amendment

Date: 2026-10-09
Repository: `lathevinh/fas`
Reviewed commit: `6ad2d37eabd1388f29844cc51c791e4885ad420b`
Reviewed document: `docs/88-phase1-benchmark-amendment-siwmv2.md`

## Verdict

**CHECKPOINT 1.3A — ACCEPTED, with one required wording/estimand clarification before paper-facing freeze.**

No blocker was found that would make the benchmark population wrong, alter the frozen RQ1/RQ2 decision rules, introduce target-performance tuning, or break the domain-OOF/sample-OOF comparison.

The benchmark/config amendment is executable and the SiW-Mv2 metadata adapter may proceed.

## Main findings

- The new study identity is distinct from historical MCIO, while the old MCIO config is preserved byte-for-byte.
- The amended four-fold structure still leaves exactly three source datasets per outer target, so domain-OOF construction remains valid.
- The SiW-Mv2 Protocol-I intersection is concretely frozen at 1,680 videos: 1,057 source/train eligible and 623 target/test eligible.
- Exact membership hashes, out-of-protocol exclusions, and missing-reference semantics are frozen.
- `reference_attack_type` is preserved separately from the versioned coarse project mapping `siwmv2_attack_family_v1`.
- Video grouping is propagated through permanent roles, inner validation, matched sample-OOF, calibration, derived ancestry, and target bootstrap.
- `subject_id` remains unknown for SiW-Mv2; participant-disjointness and participant-clustered-CI claims are forbidden.
- Executable contracts use the amended domain set, and the exact implementation commit has successful CI.
- Verification reports 146 tests with zero failures/errors/skips; schema is ready while data/model-facing stages remain blocked.

## Required clarification

Document 88 inherits historical wording about holding out a complete domain. For SiW-Mv2, the operational populations are role-dependent:

- when SiW-Mv2 is a source, only the 1,057 Protocol-I train-intersection videos are source-eligible;
- when SiW-Mv2 is the outer target, only the 623 Protocol-I test-intersection videos are evaluated;
- the 1,057 train videos are not target transactions in that fold.

Therefore paper-facing prose should not literally claim that the OCM→S fold evaluates the “entire SiW-Mv2 domain” or that all 1,680 SiW-Mv2 videos constitute the target population.

Recommended wording:

> “SiW-Mv2 is held out as a dataset in the OCM→S fold, and evaluation is performed on its frozen Protocol-I test-intersection population (623 videos). No SiW-Mv2 sample enters fitting, calibration, gate selection, or method selection for that fold.”

Describe the design as **cross-dataset held-out evaluation using dataset-specific frozen source and evaluation populations**, rather than implying that every target equals the complete physical release.

This is an interpretive clarification, not an experiment redesign.

## Non-blocking note

The coarse families (`makeup`, `mask`, `print`, `partial`, `replay`) are reasonable as a versioned project mapping. Future attack-shift analyses should still retain the 14 reference attack types and must not imply that the five coarse families are the native provider ontology.

## Final disposition

**DOCUMENT 88 / CHECKPOINT 1.3A — ACCEPTED.**

Required before final manuscript/preregistration prose:
- replace any literal “entire SiW-Mv2 domain is the target” wording with the frozen Protocol-I test-intersection population definition;
- preserve the distinction between dataset holdout and protocol-specific evaluation population.

Proceed to the **SiW-Mv2 metadata adapter**. No benchmark redesign is required.
