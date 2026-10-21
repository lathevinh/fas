# 266 - Proposal: Validate Video-Copy Evidence Before Any New399-Edge Run

Date: 2026-10-21
Status: proposal for owner/reviewer criticism; not execution approval or results.
Authority for this document: the owner explicitly requested publication of the
proposed new method on Git for review after the conversational proposal.
This is a new substantive proposal, not an acknowledgment of
[Review265](265-review-doc264-terminal-reconciliation.md) or a reopening of its
closed existing-evidence reconciliation.

## Recommendation and Decision Requested

**Evaluate a frame-copy detector plus localized temporal verification on a
separate validation benchmark before considering another399-edge investigation.**
Do not rerun the old ORB matcher, increase D's image resolution, or reinterpret
the completed ledger as scientific clearance. Keep
[247](247-dated-finite-lineage-audit-amendment.md) unchanged.

The recommendation is to review this design first, then, only if substantively
approved, implement and test one bounded feasibility package. Such approval would
not authorize399-edge execution or dataset acceptance. This publication request
authorizes neither stage; no model, dependency, weights, media or provider is
accessed for this proposal.

## Proposed Method

1. **Frame-copy retrieval:** use SSCD embeddings to propose potentially copied
   frame pairs, including transformed copies that exact RGB hashes miss. The
   candidate implementation is the
   [official SSCD repository](https://github.com/facebookresearch/sscd-copy-detection).
   This is a proposed dependency, not a repository/model/checkpoint inspected,
   installed or validated in this package. Compatibility, model selection and
   exact code/weight hashes must be fixed before benchmark execution. No model
   or checkpoint search on the399 pairs is permitted.
2. **Localized verification:** test candidate frame pairs with a fixed local
   feature/geometric verifier, proposed SIFT plus RANSAC through OpenCV. Compare
   full-frame and predeclared fixed regions rather than treating a high global
   similarity score as a localized explanation. Region definitions and geometric
   thresholds must be frozen using development controls, not witness cases A-E.
3. **Temporal verification:** require an interpretable, monotonic sequence of
   localized correspondences across multiple frame pairs, allowing time offset
   and declared speed changes. Preserve the actual frame orders, transforms,
   support regions and sequence gaps. Repeated motifs, stationary geometry or
   several scores from the same recording are not independent corroboration.

SSCD is a retrieval stage, not a capture-ancestry oracle. SIFT/RANSAC and temporal
alignment can also match the same physical pattern across recordings. This
combination is useful only if the validation below demonstrates an advantage on
the actual discriminating problem. Adding a pretrained model does not solve that
problem by assumption. Visually indistinguishable recordings cannot be certified
as independent captures from pixels alone.

## Proposed Finite Scope

The initial feasibility target is recorded-content reuse lasting at least two
seconds, with the reused region occupying at least25 percent of the frame.
Use a fixed two-frame-per-second sampling schedule and predeclared full-frame
and2x2 regional views. Test reencoding, resize, crop, brightness/contrast change,
temporal offset and speed factors0.5/1/2, including declared combinations.
These are proposed test cells, not demonstrated detectable transformations.
Temporal sampling phase must vary within the held-out controls.

Small copied patches, brief events, heavy occlusion/overlay, untested transforms
and unknown capture ancestry remain outside this initial target. In particular,
passing this target cannot automatically discharge a smaller-region or different
concrete allegation on an OULU edge. The next scientific coverage decision must
compare validated scope with each actual allegation, not simply relabel394
non-detections as negatives. The proposed numeric scope is open to criticism;
no existing acceptance threshold or error tolerance is changed by publishing it.

## Validation Before Real Candidate Execution

The benchmark must be independent of the399-edge decision set. Do not use A-E,
the five subchain findings or their connected endpoints to select model,
threshold, region definitions or temporal rules. Split development and held-out
evaluation by originating video/group, not transformed frame. Variants of one
source must stay together. Overlapping source parents invalidate that split.

| Control family | What supplies its label | What it tests |
|---|---|---|
| Known copied content | Deterministic derivation from a known parent, with exact source/order/region/transform records | Detection of reencoded, resized, cropped, shifted and speed-changed copies, including static copied regions missed by the old motion-only method |
| Synthetic non-copy challenges | Separately generated scenes with controlled recurring texture and no copied rendered recording | Engineering resistance to texture, camera/background and geometric confounds; not representative real-OULU specificity |
| Real hard negatives | Existing evidence that supports distinct recordings despite similar clothing/room/texture, assessed independently of detector output | Whether the method distinguishes material recurrence from recorded-region reuse on relevant real imagery |
| Uncertain real challenges | No trustworthy copy/non-copy label is available | Report ambiguity only; never count these as ground-truth negatives or use them to tune away inconvenient findings |

Different filenames, subject/session labels, absent exact hashes, AI consensus or
a failed matcher do not establish the real hard-negative labels. No new438-video
provenance certificate collection or provider-contact workflow is proposed.
If suitable existing labeled material is unavailable, report that specific gap
and stop the real-validation gate; do not manufacture labels or substitute toy
performance for representative evidence. The current ledger does not itself
supply this trusted real-negative benchmark. No particular external dataset is
claimed to have the necessary labels without examination.

## Proposed Pass, Fail and Stop Rules

Before any benchmark run, freeze an explicit control manifest: parents/groups,
transform cells, counts, split, model/weights/code, sampling, thresholds, exclusions,
resource ceiling and objective checks. No justified numerical sample size or
population error bound follows from the current399-edge ledger. The manifest
must justify its counts before execution rather than promise statistical assurance
from an arbitrary small sample. These details are unresolved execution prerequisites,
not a claim that an executable validated protocol already exists.

For the feasibility gate, the proposed engineering requirement is detection of
every held-out positive in the declared cells and zero copied-content confirmations
on the trusted held-out negatives, with every denominator and failure reported.
This strict observed-control requirement is a proposal, not an accepted scientific
miss-rate tolerance or proof of zero population errors. Retrieval false alarms,
verification failures and unresolved cases must be reported separately; an
unresolved trusted negative cannot be hidden as a successful rejection.

Fail or stop if trusted real controls are missing, any evaluated required cell
fails, parent/split integrity fails, a resource ceiling is reached, or the method
still cannot discriminate recurring texture from copied recording. Preserve all
failures. No threshold changes after held-out results, automatic retry, larger
crop tier, method shopping or follow-on algorithm series is authorized.

Only after a successful relevant validation result should one substantive review
consider a separately authorized, single399-edge package. It must retain the
frozen399 rows, both evidence directions, all original parents, actual region/time
coverage and failures. Its resource caps require a measured feasibility basis;
none is invented or increased here. Noncandidate coverage remains a separate
explicit limitation, not silently supplied by these399 comparisons.

## Scientific Outcomes, Not Automatic Score Decisions

Any future pair result must distinguish:

- **Confirmed prohibited reuse:** distinctive linked recorded content or an
  established source-to-derived relationship crosses a forbidden boundary;
  invoke the existing hard-error stop. A detector score alone is insufficient.
- **Supported scoped rejection:** evidence and accepted finite validation address
  the original candidate reason and every concrete material allegation on that
  edge, with remaining limitations explicit. Not universal independence.
- **Unresolved:** evidence cannot discriminate, lies outside validated coverage,
  or required integrity/validation failed. Keep the scientific relationship open.

No proposal promises that all399 edges will resolve. Failure of this new approach
would not authorize silently weakening247, excluding videos, repairing roles or
starting another method series. Such scientific changes would require exact
prospective wording and their own applicable approval.

## What Is Published Now

This package contains the proposal and a README link only. No model setup,
installation/download, Python/source changes, benchmark construction, new images,
native decode, matcher execution, calibration, new disposition or fresh scientific
result occurs. It does not request another approval merely to restate265.

The concrete review questions are whether this proposed copy-detection scope is
relevant to the actual unresolved allegations, whether trustworthy hard-negative
controls can be supplied without circular labeling, and whether the proposed
engineering gate merits a bounded implementation/validation package. If not,
reject the approach here instead of commissioning an open-ended run.

Retain the accepted
[264 ledger](../results/phase1/oulu-completion264-ledger-v1.json):399 technical
comparisons complete; five unresolved witnesses, five subchain non-detections
and389 no-geometry cases;399 scientifically unadjudicated; zero new dispositions.
Accepted effective/semantic-owner/AI prefix85; disagreement1/unresolved0;
6555 residual context/noncandidate coverage increment0;4950 originals/4949
selected/one terminal failure; calibration990/989/zero actual score-fit.
Both OULU statuses and all8 dataset/split statuses remain not_audited;
scientific readiness is false. Joined ancestry, preprocessing, OOF training,
analysis freeze and locked evaluation remain separate gated milestones.

Document checks cover links, ASCII, proposal-only authority, retained state and
an insertion-only README diff. No unchanged local scientific suite is rerun.
Exact new-head publication CI is pending at creation; its actual status will be
reported in the final handoff, not copied from264 or retroactively fabricated.
Stop for one substantive review of this proposal; no implementation follows
from publication alone.