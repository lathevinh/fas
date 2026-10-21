# 249 - Review248 Response: Finite Temporal Method and Synthetic Controls

Date: 2026-10-21

## Prospective Method Lock

- Authority248 permits existing-record design and synthetic validation only. Fix
  all399 frozen edges/438 video-record endpoints and their91 components from241.
  No real media, images, source decode, pair judgment or clearance in this package.
- Propose sequential OpenCV ORB/Hamming features on motion-masked grayscale frames,
  downscaled with aspect ratio preserved to maximum512 pixels; no upscaling.
  Use at most9 distinct accepted-order quantiles floor((N-1)*i/8),i=0..8.
  The first sample supplies motion context only. This is not a primary-selector
  change; it is a proposed diagnostic sampling rule, not full temporal coverage.
- Lock ORB600/FAST12/edge15, abs-gray motion difference>12 dilated5x5, ratio<0.7,
  unique target matches, partial-affine RANSAC3px/2000iterations/confidence0.99/
  refine10/RNG0. Require20 inliers, fraction>=0.6 and convex-hull coverage>=0.02
  in both frames. Report support in full frame/four fixed quadrants; the quadrants
  are support accounting, not an independent crop search. Partial affine is a
  similarity transform, not arbitrary perspective/overlay/region registration.
- Test slot offsets -2..2 at unit slot speed, excluding context slot0. A witness
  needs3 consecutive supported slot pairs with projected full-frame corners within
  6px of the first fitted transform. First witness in fixed offset/start order
  is retained; do not choose thresholds from a real-data favorable outcome.
- Positive controls: fixed seeded textured moving foregrounds under identity,
  translation(16,12), centered scale0.8, rotation+6degrees, centered75% crop/rescale,
  brightness0.8+12, JPEG60 and one-slot temporal delay. Negative controls: distinct
  moving foregrounds with independent backgrounds or a shared static background.
  Static-identical and dark sequences are out-of-scope visibility/motion controls,
  not negative evidence about content reuse. Use seeds100..107 and200..207 as
  separate fixed development/held-out scene groups, no threshold tuning on either.
- Controls measure only this declared toy family. Report every miss/alarm and
  feature failure. No acceptable scientific miss rate, unknown-transform recall
  or representative-real-data validation is inferred. Failure may constrain or
  reject the proposed method in this same package, not authorize tuning secretly.
- Produce a metadata-only output row for every edge, component/endpoint joins,
  candidate finding=null, coverage=not_run, unresolved reason and required future
  scientific disposition. Reuse endpoint work if later execution is authorized.
 399-candidate coverage does not validate non-candidate recall.
- Publish actual code/tests/controls/resources and a decision-ready acceptance or
  limitation recommendation together. Do not run real media, silently expand the
  population, repair roles, contact providers or adopt scientific tolerances.

## Actual Results

Before supplemental challenge execution, lock eight seeds300..307 with a shared
textured background undergoing camera translation(2*slot,slot) but independently
generated moving foreground patches. A geometric match is a false alarm for
common foreground/capture inference even if it correctly finds the shared rendered
background. Record all alarms; no change to the primary matcher/thresholds.

### Locked Prototype and Actual Controls

[Matcher](../src/fas/content_correspondence.py) implements the locked rules on
RGB arrays. The [synthetic-only runner](../scripts/evaluate_oulu_method249.py)
has no video/real-image input option. Existing decode, identity guard, selectors,
roles, models and scientific gates are not modified. Thresholds were locked before
measurement; they are engineering proposals, not an approved error tolerance.

| Case | Development seeds100..107 | Held-out seeds200..207 |
|---|---:|---:|
| Identity | 8/8 witnesses | 8/8 witnesses |
| Translation16,12 | 8/8 | 8/8 |
| Centered scale0.8 | 8/8 | 8/8 |
| Rotation+6degrees | 8/8 | 8/8 |
| Centered75% crop/rescale | 8/8 | 8/8 |
| Brightness0.8+12 | 8/8 | 8/8 |
| JPEG quality60 | 8/8 | 8/8 |
| One-slot temporal delay | 8/8 | 8/8 |
| Independent foreground/background negatives | 0/8 alarms | 0/8 alarms |
| Different moving foreground/shared static background negatives | 0/8 alarms | 0/8 alarms |
| Identical static sequence, outside moving-content claim | 0/8 witnesses | 0/8 witnesses |
| Identical black sequence, visibility failure control | 0/8 witnesses | 0/8 witnesses |

192 primary cases contain128 positives,32 negatives and32 outside-claim controls.
All128 declared moving-texture positives were detected and all32 simple negatives
were unflagged. The16 identical static cases are genuine reused pixel content
which this motion-based method misses: they are not evidence of independence.
Black/textureless cases likewise remain uninformative. These toy scenes share a
single construction; scene seeds are not independent real capture populations.
Held-out scene seeds prevent exact-scene reuse but not generator-family leakage.
No threshold was changed or selected from either group's results. No general
recall, confidence bound, acceptable miss rate or scientific tolerance is adopted.

**Supplemental confound:** all8 seeds300..307 produced witnesses when different
moving foregrounds shared a camera-translated textured background. These are8/8
alarms relative to the common-foreground/capture-negative hypothesis. The matched
background is actually shared rendered content, so the geometric witness itself
is not fabricated; its interpretation as common capture/foreground would be wrong.
Consequently, motion masking does not solve shared-room/camera-motion ambiguity.
The retained inlier points/matrices/quadrant counts permit checking where support
lies, but do not provide a validated foreground segmentation or adjudication rule.

The challenge was added after primary measurement, predeclared before its own
execution and stored separately. Primary controls were never overwritten. The
runner later gained only the challenge path and matcher gained only the metadata
planner/import. Reconstructing the original source bytes reproduces both original
control-code hashes; core matching and primary measurements did not change.
This is transparent exploratory challenge evidence, not a fresh held-out estimate.

### Resources and Tests Actually Measured

| Measurement | Actual result |
|---|---:|
| Primary192-case wall seconds | 14.083 |
| Primary process peak RSS bytes | 143,093,760 |
| Supplemental8-case wall seconds | 1.018 |
| Supplemental process peak RSS bytes | 86,114,304 |
| Primary immutable record bytes | 9,336,347 |
| Challenge immutable record bytes | 765,263 |
| Metadata-plan immutable record bytes | 864,179 |
| Fresh focused OULU tests | 95 passed,0 failures/errors/skips |
| Focused discovery-inclusive / runner seconds | 5.653 / 5.586 |

Peak RSS is Linux process high-water usage, not aggregate future decoder memory.
OpenCV4.11.0/NumPy1.26.4 in existing conda fas, single-threaded ORB and seeded
RANSAC were used; no dependencies were installed. Unit tests cover invalid input,
quantile sampling, missing temporal support, inconsistent geometry, blank features,
exact same-process witness replay, the camera-background confound and fail-closed
edge/component/endpoint joins. Three test methods were added to the existing
OULU module. Its historical watchdog/rehash logs are intentional synthetic tests,
not new real archive reads or export failures. No fresh full local suite is claimed;
final publication CI runs the complete suite.

### Exact Population and Edge Output

The metadata-only plan reconciles399 exact-pair records to the immutable241
membership/rank commitments and their438 media-record parents. All91 connected
component memberships and disjoint endpoint sets are retained, with exact accepted
frame indices validated.837 distinct source records were hash-bound (399 pairs
and438 media records); original archives/images were not opened or decoded.

Every frozen edge has an output row: actual rank/pair-record commitment, endpoint
parents, component index/digest, proposed orders, evidence=[], finding=null,
coverage=not_run, reason=real_media_method_execution_not_authorized, required
scientific disposition=pending_future_evidence_no_accepted_outcome, and effective
disposition=null. These are populated planning rows, not399 detection results or
399 newly accepted uncertain judgments. Detailed IDs/ranks/rows remain private;
the [aggregate](../results/phase1/oulu-temporal-method249-v1.json) exposes commitments
and counts only. Every current residual relationship remains unadjudicated.

All399 listed candidates would be examined in a later approved run, but this is
zero non-candidate coverage and does not validate the original candidate generator.
The closed85 prefix and other6156 residual-context edges are not new screening
population. Neither components nor exact aliases are independent observations.
Missing/failed endpoints must keep affected edge rows visible, not drop denominators.

### Concrete Proposed Real-Data Workload, Not Executed

Reuse features once per438 endpoint, then compare all399 edges in their components.
Choose9 quantile orders/video:3,942 sampled orders total, with the first/video used
only as motion context. Strict accepted-index verification still requires decoding
all58,733 native frames:365,366,246,400 RGB bytes, streamed rather than persisted.
Only8,588,737,576 selected payload bytes across3 archives need extraction once per
endpoint; largest payload41,868,758 bytes. Frame counts range56..151. Work is not
399 independent video exports/manual approval chains.

Proposed ceilings for one consolidated run:7200s total,180s/decoder,2GiB aggregate
RSS,128MiB temporary payload,128MiB feature arrays,256MiB persisted diagnostics and
640MiB initial free reserve. These are proposals requiring method/scope approval,
not measured or authorized real-data budgets. Nominal438*9*600*(32+8) descriptor/
coordinate bytes=94,608,000, excluding Python/ORB/decoder overhead. Sampled witness
patches or additional diagnostics must fit the fixed budget; no automatic evidence
reduction or cap increase. Boundaries/indices remain unchanged on failure.

Primary synthetic feature-extraction median/max per9-frame sequence was0.026411/
0.043871s; comparison median/max0.051221/0.062036s. Multiplying maxima by438/399
yields19.216/24.752s respectively, **not a real-data runtime prediction**. Synthetic
frames are256x384; native resizing/decode, guarded archive I/O and real feature
density have not been benchmarked.365GB RGB makes decode/I/O an unmeasured dominant
cost; the proposed7200s budget is not established feasible. Parent supervision,
strict RGB/EOF/stderr/member checks and a final successful readback must be adapted
and tested inside a later explicitly approved real-data package, not assumed
implemented by this array-only prototype. No second replay is needed unless a new
unverified nondeterministic property warrants it.

## Decision-Ready Recommendation and Completion Rule

**Do not approve this as a clearance classifier.** The method can supply bounded
moving-texture correspondence witnesses for the measured transform toy family.
The8/8 moving-background confound, static-content blind spot, quantile gaps and
absence of representative real validation prevent either positive capture
adjudication or negative clearance. No scoring cutoff fixes that by assertion.
Insufficient motion/features, unmodeled perspective/nonrigid/mirror/overlay changes,
speed variation, short transients between quantiles, small regions, darkness and
unregistered geometry remain unknown. No miss-rate acceptance is invented.

The concrete option for substantive decision is **witness-only triage of this
exact399/438 population under the declared sampling/transform/cap limits**, not
audit acceptance. Expected gain: explicit spatial/temporal inlier evidence and
per-edge visibility/method coverage beyond five pHash ranks, with endpoint reuse.
It cannot guarantee any relationship resolves or that non-candidates are clean.
Real execution is not authorized by this submission; approval would need to accept
this limited purpose and budget, not reapprove amendment247's existing wording.

Objective technical completion, if that option is approved: verify the exact
population/parents and accepted guard; produce438 endpoint success/failure feature
records and399 edge rows, recording every tested slot pair and witness geometry,
unavailable features/regions and failures. Verify deterministic parent/record joins,
all caps, successful supervisor metrics and final immutable readback. A timeout,
source/RGB mismatch or cap failure gives a bounded failed/partial report with every
affected row retained, never completion from a worker summary. Stop affected
science for credible prohibited derivation, preserving evidence; no role repair.

For every resulting edge, technical finding and scientific disposition remain
separate: witnesses route to a genuine scientific content-versus-common-background
decision; no-witness/insufficient-feature rows remain unresolved, never automatically
rejected. No AI agreement or absence of exact overlap substitutes for that decision.
A successful triage run would complete this finite technical comparison, **not**
OULU lineage audit acceptance. Audit closure still needs explicit dispositions of
materially unresolved prohibited relationships under247 and separately joined
cross-domain assurance. Only substantive cases requiring judgment are routed; do
not start399 categorical owner workflows by default.

If a method that can resolve lineage rather than merely collect witnesses is
required now, reject this prototype for that purpose. A distinct evidence route
with representative real controls and an explicit common-background discrimination
claim must then be substantively chosen; no alternative is validated here, and
no extra algorithm tuning, provider request or old-pair native tier is executed.
This limitation and the concrete witness-only option are delivered together, not
a request for another generic protocol/checklist to choose the same population.

## Publication and Retained State

Review248's accepted source247 CI is reused: full head
`02e2f335e464c2b0ddc0a4165647d67b377b09ac`,
[run39529091454](https://github.com/lathevinh/fas/actions/runs/39529091454),
[job118990593312](https://github.com/lathevinh/fas/actions/runs/39529091454/job/118990593312),
completed/success,12/12 steps. It is not new249 CI. New exact head/run/job CI is
pending at creation; final handoff/additive immutable receipt must verify success
and all12 steps including Complete job. CI does not validate scientific adequacy.

Zero real residual pairs screened/resolved;85 accepted prefix,399 unadjudicated,
6555 residual context,4950 originals/4949 selected/failure1/calibration990-989/zero
score-fit, historical disagreement1/unresolved0 remain. All8 statuses not_audited;
scientific readiness false. Existing owner/authorization/failure/pending evidence
is preserved. Stop for one substantive method/evidence-purpose decision; no new
real media, detector/model, provider contact, source/target science or status change.