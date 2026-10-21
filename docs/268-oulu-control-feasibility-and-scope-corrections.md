# 268 - Existing-Control Feasibility and Scope Corrections

Date: 2026-10-21
Authority: owner request to read [267](267-review-doc266-copy-validation-proposal.md)
and continue; existing-record analysis and targeted design correction only.
This does not authorize SSCD, benchmark media or399-edge execution.

## Terminal Decision

**Trustworthy relevant real controls and allegation-specific applicability are
not established by the inspected existing records. Stop this proposed real-validation
approach before committing model resources.** Do not install/download a model,
decode benchmark media, select another model or request further native images.
This is267's control-unavailable outcome, not a failed SSCD measurement, universal
proof of control unavailability, or an assertion that image methods are futile.

The work supplies actual metadata manifest candidates, the evidence-label limit,
a measured read-only inventory, and the three targeted corrections below in one
package. It is not permission to prepare unspecified options later. No new owner
collection, provider outreach or administrative permission evidence is requested.
Existing owner research permission is reused; access to CSVs is not proof of
media availability or independent capture labels.

## Actual Existing Sources and Manifest Candidates

The [inventory script](../scripts/inventory_oulu_controls268.py) reads frozen
metadata/roles, the accepted private264 ledger, four historical synthetic-control
records,85 historical activation/pair records and eight witness media-index JSONs.
It opens no archive, payload, frame, gallery, feature bank or model. Every consumed
source has a recorded hash; frozen CSVs,264, witness indices and synthetic records
are checked against existing commitments.85 activation/original-pair hashes are
new observations of historical records, not an independently reverified full
activation chain. Earlier source/output records are not rewritten.

The [public inventory](../results/phase1/oulu-control268-feasibility-v1.json)
publishes counts, scope joins and a private-manifest hash. The immutable private
manifest contains all7510 actual metadata candidate rows, their video/group IDs,
assigned roles, known exposure exclusions, null copy/non-copy labels,85 original
screen-record references and source paths/hashes. These are actual candidates,
not fabricated control labels or already allocated development/held-out splits.
No private identities, source paths, original queue ranks or images are published.

| Existing frozen collection | Metadata rows/groups | Role-assigned rows/groups | Available label evidence |
|---|---|---|---|
| OULU-NPU |4950/55 subjects|4950/55 subjects| PAD labels, official split and frozen role; no independent real non-copy labels in these fields |
| CASIA-FASD |600/50 subjects|600/50 subjects| Same metadata limitation; no new media access/ancestry verification |
| MSU-MFSD |280/35 subjects|280/35 subjects| Same metadata limitation; no new media access/ancestry verification |
| SiW-Mv2 |1680/1680 video groups|1057/1057 video groups| Subject is unknown; count by video, not one empty-subject group. Video grouping does not certify capture independence. |

399 OULU decision edges use438 videos from47 subject groups. Excluding only those
videos leaves4512 rows, but excluding all their subject groups leaves720 videos
in8 groups. The accepted85-prefix exposes40 subject groups; excluding the union
of both known group sets leaves540 OULU rows in6 groups. Those exact candidates
are flagged in the private manifest. They are not540 trusted negatives or a clean
held-out benchmark: shared capture grouping and pretrained-model overlap remain
unknown. There is no selected checkpoint whose training overlap could be checked.
Other-domain candidates are not authenticated as OULU-representative substitutes;
none is declared clean merely because dataset names differ.

### Labels That Exist, and Labels That Do Not

-249 has192 primary toy controls and8 background challenges;253 has128 paired
  synthetic controls and8 dynamic-background challenges. Their existing records
  report zero real pairs screened. Retain these as engineering-control evidence,
  not independent real-recording negatives or new SSCD measurements.
- The85-prefix retains its accepted screen-level false-positive dispositions,
  owner answers, disagreement history and bounded rendered-content scope. It is
  not relabeled unresolved or discarded. That scope does not independently label
  the broader duration/region/transformation claim proposed in266. It cannot be
  circularly repurposed as a new capture-independent hard-negative benchmark.
- Metadata, subject IDs, different filenames and matcher failure are not non-copy
  labels. The actual candidate manifest therefore keeps `noncopy_label` and
  `copy_parent_label` null. A known positive copy-parent label would become
  available only after separately authorized deterministic derivation; none is
  generated here. Uncertain real examples are not negatives.

This bounded inventory does not claim that no suitable evidence can exist
elsewhere. It establishes that the named available metadata, accepted screen
labels and toy controls do not supply the relevant trusted real labels needed
for the proposed gate. No time is spent searching inaccessible media or replacing
missing labels with assertions.

## Correction1: Control and Split Discipline

Any later genuinely new evidence must identify the actual trusted label basis,
originating capture groups, parents and exposure history before model resources.
Subject/video group keys above are known metadata exclusions, not authenticated
capture-group truth. All transformed descendants and shared capture groups must
remain in one development or held-out split. Excluding A-E alone is insufficient.
No benchmark split is assigned now because the label prerequisite failed.

If that prerequisite were satisfied by new evidence, freeze the held-out manifest
before result-driven choices. The proposed development budget is at most12
configurations: cosine thresholds0.80/0.90/0.95, geometry inlier minima12/20,
and temporal support minima4/5. Log every configuration; no held-out retuning,
checkpoint shopping or silent replacement is allowed. These are proposed
engineering settings, not calibrated or accepted scientific thresholds.

## Correction2: Executable Duration and Region Meaning

For a prospective feasibility claim, require **both** the source interval and
transformed-query interval to last at least two seconds. Intervals are half-open
`[start,end)` using decoded presentation timestamps, not frame-count/fps guesses.
Thus a2x query needs at least four source seconds to remain inside this proposed
claim; a two-source-second copy compressed to one query second is explicitly
outside it, not a passing two-second case. Include that boundary as an out-of-scope
challenge, without counting it as a required in-scope detection.

Proposed sampling is a global0.5-second schedule with phases0/0.125/0.25/0.375
seconds. Select the nearest decoded timestamp within0.04 seconds; ties choose
the earlier frame. Do not duplicate a native frame to manufacture support. Require
at least4 distinct pairs, or5 for that development setting, with observed native
first-to-last spans at least1.4 seconds on both sides. Fit query time as
`offset + source_time/speed`, speed in0.5/1/2 within2 percent, maximum timestamp
residual0.08 seconds. Report actual spans, residuals and missed samples. Sampling
and monotonicity remain technical evidence, not recording-origin discrimination.

Define25 percent as the **visible copied-content mask area divided by the full
unpadded decoded frame area**, separately in source and transformed query after
crop/resize. Occluded/out-of-frame pixels do not count; every supporting frame
must meet the fraction on both sides. Ground-truth masks come from known control
derivation, never from an inlier bounding rectangle or embedding score.

Full-frame plus2x2 views remain a finite proposed retrieval set, not guaranteed
coverage. A quarter-frame patch centered across quadrant boundaries need not be
contained in a quadrant. Required control placements include the3x3 combinations
of top-left offsets0/0.25/0.5 for a half-width/half-height patch, especially the
center straddling case. Cross declared speed/phase conditions with relevant
transform cells before evaluation; freeze exact cell members/counts and their
diagnostic justification first. Occlusion reducing visible area below25 percent
is outside the claim. Failure on an in-scope straddling/speed/phase cell fails the
approach; do not add views after seeing a held-out miss.

### Applicability to Existing Allegations, Without Tuning

Read existing259 order/region joins and accepted timestamp indices only. No
matcher or visual observation is repeated. Selected-chain spans are descriptive
first-to-last timestamps, not continuous copy-duration labels.

| Witness | Selected source-side span, seconds | Other-side span, seconds | Spatial applicability limit |
|---|---:|---:|---|
| A |1.266167|1.251952| Baseline inlier bboxes about0.118-0.159 frame area; no true copy-area label |
| B |1.203451|1.251952| Baseline bboxes vary about0.151-0.518; compensated chain absent |
| C |1.203451|1.251959| Some bboxes about0.093-0.098; larger boxes do not establish copied area |
| D |1.206414|1.251872| Bboxes about0.350-0.489 across branches; native result still inconclusive |
| E |1.242260 baseline /1.208686 compensated|1.251959| Bboxes about0.067-0.157; branch order differences retained |

The public inventory preserves exact rational timestamps and every selected bbox
fraction per side/branch. None of A-E has established eligibility for the proposed
two-second/25-percent copied-content scope. A short selected chain does not prove
longer reuse absent; a small inlier box does not prove the true copied region is
small. Conversely, neither can be inflated into adequate target coverage.
The five subchain and389 no-geometry cases have no ground-truth copy-duration or
visible-mask labels either. Passing a convenient benchmark scope would therefore
not automatically address the399 allegations or close the local audit.

## Correction3: Decision Algorithm and Observed-Control Gate

If trustworthy controls/applicability were later supplied, the proposed candidate
algorithm is bidirectional SSCD retrieval, top5 matches per sampled frame among
the comparison video's fixed views above the chosen development cosine threshold.
Record all attempted queries and shortlist losses. A positive lost in retrieval
is an end-to-end miss, not removed from the verification denominator.

Proposed geometry uses SIFT with at most2000 features, ratio0.75, mutual matches,
RANSAC residual at most3 pixels after a declared512-pixel-long-side local-verifier
resize, and the development inlier minimum. This resize is for local geometry,
not an invented SSCD input recipe. A compatible standalone TorchScript checkpoint,
exact hash, descriptor normalization and official model preprocessing remain
unselected because the prerequisite failed; no executable model protocol is
claimed. No training stack is imported merely to prepare this document.

Build monotonic chains using the duration/speed/residual rules above. Choose the
development configuration by positive misses, then negative false confirmations,
then negative unresolved outcomes; deterministic ties prefer the higher threshold,
inlier minimum and support minimum. Freeze that selection once. Only a technical
copy candidate is produced by score/geometry/chain agreement. Scientific
confirmation additionally needs distinctive linked recorded detail or an
established source-to-derived link. Static pattern recurrence without that
discriminator remains uncertain, including if temporal monotonicity is perfect.
Scoped rejection needs accepted validation relevant to the actual allegation;
neither low score nor no shortlist supplies it automatically.

Every required held-out positive must be detected end-to-end in its declared
cell. Every trusted negative must receive a supported rejection; uncertainty is
not a correct rejection. Report originating-group/cell denominators, retrieval
misses, geometry/chain failures, false confirmations and unresolved cases
separately. Positive detection is not the same as confirmed scientific lineage.
Dependent frame/view/transform variants do not multiply independent groups.
These are finite engineering smoke conditions, not a zero-population-error
promise. Counts, checkpoint and held-out allocation remain null rather than
fabricated where the prerequisite is unavailable. No numerical run occurs.

## Budget, Checks and Unchanged State

For this metadata inventory: wall ceiling600 seconds, CPU120 seconds, process
RSS512MiB and combined output records16MiB. Record actual inventory wall/CPU/high-
water RSS and serialized bytes in the aggregate. These measurements exclude
agent drafting, tests, Git/network and CI time. The desk package has a maximum
four active agent-hours, not a measured four-hour duration. Model/GPU/decode/
development execution budget is zero under current authority; the12-configuration
recipe is unexecuted. No resource ceiling is increased to overcome a failure.

Three focused tests cover grouping without empty-subject collapse, identity/hash
drift refusal, and rational timestamps without copied-area/duration inference.
The previous107 test methods remain unchanged; no unchanged full local suite or
synthetic ablation is rerun. Schema/manifest/privacy/parent/link and insertion-only
README checks bind the published result. No benchmark results are invented.

Retain399 technical comparisons; five unresolved witnesses/five subchain/389
no-geometry cases, all399 scientifically unadjudicated, zero new dispositions;
accepted effective/semantic-owner/AI85; disagreement1/unresolved0;6555 residual
context/noncandidate increment0;4950 originals/4949 selected/one terminal failure;
calibration990/989/zero actual score-fit. All8 statuses remain not_audited and
scientific readiness false.247, the264 ledger and historical owner answers remain
unchanged. Other domains are inventoried as metadata candidates only; joined
ancestry, detector/crop, OOF, model training, freeze and locked evaluation are
not executed or promoted.

Exact new publication CI is pending at creation and will be recorded in the final
handoff/additive receipt, without rewriting old pending fields. Stop for one
substantive268 review of this control-unavailable result and targeted corrections;
no implementation, new collection, model switch or399 run follows automatically.