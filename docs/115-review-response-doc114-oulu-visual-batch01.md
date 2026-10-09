# Response to Review 114: OULU Private Visual Review Batch 01

Date: 2026-10-09
Base commit: `6e32106`
Review: [Document 114](114-review-doc113-oulu-lineage-exact-evidence.md)

Review 114 accepts checkpoint 1.5G for exact evidence only and requires stronger
private content adjudication. This checkpoint 1.5H starts that work with the
**first ten** already ordered cross-role + conflicting-label candidates. This is
a bounded visual batch, not adjudication of all 85 highest-risk or 6640 candidates.

## Prospective Definition

[Visual-review policy](../configs/visual_review_v1.yaml) is recorded before packet
preparation and inspection. Selection is queue ranks 0 through 9 from the frozen
priority order, independent of apparent ease, screening distance or review outcome.
No candidate, role, label, split, seed, selector or screening threshold is rewritten.

[Verified visual evidence](../src/fas/visual.py) and
[private packet runner](../scripts/prepare_oulu_visual_review.py) reread the pinned
media payloads and verify every full-resolution decoded RGB frame against the
accepted index before generating private thumbnails. Width/height, count, order,
RGB digest and strict FFmpeg errors are checked. Temporary AVIs are removed.

Each packet contains two temporal panels covering 17 fixed ranks
`floor((n - 1) * j / 16)`, `j=0..16`, and a larger paired trigger witness. The
witness is the earliest minimum-Hamming slot pair from accepted fingerprints;
it explains what triggered the screen, not an equivalence decision threshold.
Every full-frame thumbnail is available privately with its accepted RGB identity,
timestamp and thumbnail digest for further inspection.

The prospective visual disposition rule is:

- `confirmed_same_content_or_derived_lineage`: recognizable shared rendered
  sequence or specific derivation supported by temporal correspondence;
- `rejected_false_positive`: clear content divergence explaining the screen
  trigger without a recognizable corresponding rendered sequence;
- `uncertain_insufficient_evidence`: unresolved sampling, resolution,
  transformation or provenance ambiguity.

Rejection is scoped to the observed screen/rendered-sequence match, not proof of
independent acquisition, face identity or absence of every possible shared source.
No original-capture provenance certification is made. Similar ceiling/background
layouts or silhouettes alone cannot confirm lineage. Different labels/roles are
priority metadata, not evidence supporting rejection.

## Reviewer and Coverage Boundary

The reviewer is **GitHub Copilot, using AI-assisted visual observation** through
image-viewing tools. This is not an independent human, blinded second reviewer,
validated lineage classifier or inter-rater reliability study. No face identity,
demographic attribute or person relationship is inferred.

Exactly **30 images** were viewed: both temporal panels and the trigger witness
for each of ten pairs. That covers 17 temporal positions per video in each pair,
plus its trigger frame. **Not every original frame was visually inspected.**
Verification of all decoded RGB hashes must not be confused with visual inspection
of the full continuous timeline. Sparse positions and resized thumbnails can miss
short shared subsequences, fine overlays or transformed regions.

Private observations include pair-specific non-identity scene/foreground rationale,
limitations and the exact hashes of the viewed images. They are immutable review
records bound to the packet, policy and raw observation input. They remain
**proposals pending owner checkpoint review** and do not clear the data gate.
No biometric images, pair identities or detailed private observations are committed.

## Completion Criteria

- Verify accepted candidate/media evidence, payload pins and all 13 frozen artifacts.
- Prepare exactly the first ten highest-risk pairs without outcome-dependent selection.
- Verify all decoded RGB frames and export private temporal/trigger evidence.
- Actually view the declared images and record evidence-backed proposed dispositions.
- Re-extract reproducible packets, reject overwrite and preserve earlier records.
- Pass focused/full tests, publish aggregate evidence and push for owner review.

## Actual Evidence

[Immutable aggregate report](../results/phase1/oulu-visual-review-batch01-v1.json)
binds the review/policy/implementation, private packet lineage and summary, private
observation definition/summary/bundle, frozen hashes and validation results.

| Quantity | Observed |
|---|---:|
| Fixed first-batch candidate pairs | 10 |
| Unique supplied videos | 19 |
| Full-resolution decoded RGB frames verified | 2624 |
| Images actually viewed | 30 |
| Same/derived-content confirmation proposals | 0 |
| Screen false-positive rejection proposals | 9 |
| Uncertain, insufficient evidence | 1 |
| Highest-risk pairs not yet visually reviewed | 75 |
| All cross-role pairs not yet visually reviewed | 474 |
| All non-exact candidates not yet visually reviewed | 6630 |

The rejection proposals are supported by visible non-identity foreground/scene
differences at the trigger and fixed temporal positions, rather than by no exact
hash match, different metadata, or a tightened pHash threshold. One pair retains
uncertainty because coarse foreground/layout similarities and limited displayed
detail leave derived/partial-content hypotheses insufficiently resolved.

These are **batch reviewer proposals**, not nine accepted lineage clearances,
measured adjudication accuracy or a statement that cross-role leakage is absent.
The unreviewed counts describe coverage, not the number of confirmed-clear pairs.
Historical screening and exact-evidence dispositions remain unchanged; the new
review ledger is separately bound and no fitting/evaluation mask is changed.

Original and rerun packet exports contain **2685 byte-identical artifacts** each.
The rerun actually rereads and redecodes all 19 videos, not just saved fingerprints.
Verification checks all 2624 thumbnail digests/accepted frame joins, 19 manifests,
ten packets, viewed-image bindings, frozen/study/prior-screen/exact policy and code
hashes, cleanup and byte identity. Existing-output retry returns exit code 1 and
preserves every byte. Reproducible packets do not validate reviewer judgment.

**46 focused / 233 full regression tests pass**, with zero failures/errors and no
editor diagnostics. Tests cover fixed temporal ranks, full RGB reconciliation and
hash mismatch, PNG color/geometry and unsafe/existing output refusal, alongside
the existing media/selector/screening/exact-evidence suites. No dependency or
research environment is changed.

Private integrity-review thumbnails are now persisted outside Git. They are not
a detector crop, study single-image frame bank, embedding cache or training input.
Existing research preprocessing and the frozen primary selector remain unchanged.
No research detector, DINOv2/OpenCLIP/classifier/risk model, score, calibration,
training or target evaluation is executed. AI-assisted image review is explicitly
disclosed rather than described as human or model-free adjudication.

## Remaining Work

The original denominator stays 4950, including the retained decode failure; the
13 known exact pairs stay separate. All frozen roles, selector and split seed
20261009 remain unchanged. Schema passes; data-audit, source-dry-run,
analysis-freeze and locked-evaluation remain blocked. Scientific readiness and
model execution authorization remain false.

Stop here for owner review of the bounded method/evidence and proposal limits.
The next OULU slice should continue the 75 remaining highest-risk pairs in their
existing order and seek stronger evidence for the retained uncertain pair before
claiming closure. No dataset access or administrative receipts are missing.
An independent/higher-detail review may revise proposals via a new bound record,
never by overwriting the prior ledger or making unsupported clearance claims.

If cross-role shared content is confirmed, stop for an explicit prospective
scientific decision. Never silently delete videos, regenerate roles, retry seeds,
change the primary selector or tune screening thresholds to erase candidates.
The remaining 399 other cross-role pairs and other priority populations remain
later bounded batches, not automatic continuation to another dataset/model stage.