# 267 - Review of266: video-copy validation proposal

Date: 2026-10-21
Reviewed commit: `a939dc9e4ecd199d603efd5ef6b6d380503a6963`

## Verdict

**Accept the relevance of the proposed copy-retrieval/local/temporal validation direction. Do not approve266 as an executable validation protocol or authorize another399-edge run. Targeted design corrections are needed, not another generic literature or image-escalation series.**266 is a substantive proposal and does not violate265's instruction against acknowledgment-only reports.

Its strongest feature is testing the actual material-recurrence versus recorded-copy problem independently of the399 decision set. Its largest unresolved prerequisite is trustworthy relevant real hard-negative material. A new embedding model cannot supply those labels. Without them, this would risk repeating the toy-success/real-ambiguity loop.

## Evidence checked

Read the full proposal and README diff. No code, weights, dependencies, media or scientific results were added. Official [SSCD documentation](https://github.com/facebookresearch/sscd-copy-detection) describes an image-copy descriptor and pretrained inference models; it does not establish this proposal's video/region thresholds or real-OULU capture discrimination. Documentation also offers standalone TorchScript inference. If selected, prefer the smallest compatible inference integration rather than importing a training stack unnecessarily. No particular checkpoint or runtime is approved here; pins/preprocessing must be fixed before held-out evaluation.

Public exact-commit GitHub checks/job HTML confirms [run39581448968](https://github.com/lathevinh/fas/actions/runs/39581448968), [validate119159766024](https://github.com/lathevinh/fas/actions/runs/39581448968/job/119159766024), head `a939dc9e4ecd199d603efd5ef6b6d380503a6963`: all12 listed steps have success conclusions including Complete job. No API completion timestamp is asserted. Proposal publication CI does not validate SSCD or the proposed benchmark. No scientific tests/downloads were needed for this document review.

## Three concrete corrections before numerical validation

**1. Identify actual controls before committing model resources.** Name the available source collections/groups, lawful access, copy-parent labels and the independent evidence supporting real non-copy labels. Keep transformed descendants and shared originating capture groups in one split. Freeze held-out controls before result-driven choices; development tuning is permitted only within its declared design budget and must be logged. Excluding A-E and their connected endpoints from tuning is necessary but does not by itself establish a clean held-out population or prevent training-data overlap. State known overlap/access limits honestly. Do not classify uncertain controls as negatives from metadata, matcher failure or AI consensus.

The initial read-only feasibility check should produce actual manifest candidates and label evidence, not a promise to find them later. If no suitable material exists under current access/authority, stop the proposed real-validation route there and report that exact gap. No provider outreach or new collection is implied. This check belongs inside the single feasibility package, not a separate receipt/activation approval chain.

**2. Make the duration/region target executable and relevant.** State whether two seconds is measured in the source or transformed query. At2x speed, two source seconds become one query second, so two-fps sampling cannot be assumed to give the same sequence support. Define minimum supported samples, endpoint convention, timestamp alignment, permitted speed/offset errors and phase coverage. Define25% in source/query coordinates after crop/resize and visibility/occlusion treatment. A25% patch can straddle all four2x2 cells; full-frame plus quadrant views do not guarantee a wholly contained quarter-frame patch. Include boundary-straddling and speed/phase cases in controls, or narrow the claim explicitly. No guaranteed performance follows from those geometric counterexamples; they identify test requirements, not empirical failure.

Use existing264/259 evidence to map which actual allegations could fall inside that validated scope. Do not tune on those cases. The proposed two-second/25% target is an engineering feasibility scope, not already justified local-audit coverage. Regions smaller than that target and unknown durations cannot be silently discharged. Passing a convenient scope that cannot address the remaining allegations would not advance closure.

**3. Define the decision algorithm and observed-control gate without pretending statistical assurance.** Pin retrieval shortlist/score policy, preprocessing, local geometry, temporal-chain rules and the rule separating confirmation/rejection/uncertainty. Report end-to-end retrieval misses as misses; do not measure verification only conditional on successful retrieval. Distinguish static recorded-copy detection from recurrence of a physical stationary pattern: temporal monotonicity alone does not resolve it. Multiple views/frames and variants of one source are dependent controls.

266's every-positive/zero-confirmation gate may serve as a strict engineering smoke gate, not a population error guarantee. Freeze finite cells/counts and justify their diagnostic purpose before held-out evaluation. Report rates/denominators and failures by originating group and cell, not only pooled totals. A trusted negative marked unresolved is not a correct rejection, as266 already states. Do not loosen thresholds after a failed held-out result; equally, do not create an endless prerequisite to demonstrate literally zero population errors. Benchmark passing would support only the measured finite claim and still require allegation-specific applicability review before OULU execution/acceptance.

## One bounded route forward

Recommend one consolidated feasibility package, with a declared wall/compute/storage/development budget and a terminal report. First determine actual control availability and scope relevance from existing records; do not download/install/run models before that prerequisite is satisfied under applicable authority. If it is satisfied and numerical work is authorized, combine manifest, implementation, tests, locked evaluation and measured resource result in the same package. Do not request separate approvals for runner, weights receipt, export, import or activation. No repeated review is needed merely to restate these design requirements.

The final report must recommend one decision: relevant validation supports a concrete next OULU scope; the method fails a named discriminating cell; or trustworthy controls/applicability are unavailable. In the latter cases stop this approach without automatically selecting another model or requesting more native images. In the first case supply the exact proposed OULU purpose, applicability to the ledger, uncertainty rule and measured budget together. Do not promise all399 resolutions or full dataset completion from an untested method.

This review supplies criticism and a bounded recommendation, not execution authority for pretrained-model inference, benchmark media or399 candidates. The owner's current request is review. Any requested substantive authorization must concern the concrete scope/resources already specified, not permission to prepare another unspecified proposal. Ordinary read-only source/control inventory may proceed under existing-record-analysis authority where records are available; external contact or new acquisition is not included.

## Retained state

No new scientific evidence, method validation or dispositions.399 completed technical comparisons remain5 unresolved witnesses,5 subchain non-detections and389 no-geometry cases; all399 scientifically unadjudicated. Accepted effective/semantic-owner/AI85; historical disagreement1/unresolved0;6555 residual context/noncandidate coverage increment0;4950 originals/4949 selected/one terminal failure;calibration990/989/zero score-fit. All8 statuses remain `not_audited` and scientific readiness false. Detector/FAS training, other datasets, source/target experiments, freeze and locked evaluation remain separate blocked stages. No contract waiver, role repair or negative clearance follows from this proposal review.
