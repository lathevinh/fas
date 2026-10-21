# 253 - Camera-Compensated Motion: New Synthetic A/B Evidence

Date: 2026-10-21

## Prospective Experiment Lock

- Review252 accepts251 without rework. This is not an acknowledgment/activation
  response: it tests a new, specific extension against249's measured shared-moving-
  background confound under existing safe-synthetic engineering permission.
- Hypothesis: remove estimated global camera translation before residual-motion
  masking to suppress shared-camera-background witnesses while retaining witnesses
  for independently moving, shared foreground texture. This is not semantic
  foreground segmentation, capture adjudication, static-reuse detection or clearance.
- Existing matcher/planner249/251 and synthetic runner249 remain unchanged.
  New array-only experiment computes paired baseline and compensated features.
  Reuse9 quantiles/context-only first slot, ORB600/FAST12/edge15 and all existing
  correspondence/temporal thresholds. No descriptor or witness threshold tuning.
- Estimate previous-to-current translation with OpenCV phaseCorrelate on float32
  grayscale. Require finite shift/response, response>=0.15 and displacement<=10%
  of each dimension. Warp previous grayscale; threshold residual>12, dilate5x5;
  intersect with warped valid support eroded5x5. No window, optical-flow model,
  learned segmentation, rotation/perspective registration or threshold search.
  Rejected registration produces no features/unknown, never a negative disposition.
- Freeze development seeds400..407 and held-out500..507, same toy scene generator,
  no tuning after either group. Eight paired cases per seed: shared camera content,
  its JPEG60 and translation16,12 variants; shared moving foreground on independent
  backgrounds; different foregrounds on shared moving background; independent
  moving-camera scenes; identical static and black sequences as outside-claim
  visibility/motion controls. Camera translation is(2*slot,slot).128 new paired cases.
  Original192 primary/8 challenge records are not regenerated or overwritten.
- Store all cases, baseline/revised witnesses with inlier points, frame hashes,
  registration shifts/responses/availability and timing/RSS. No scene is dropped
  for failure. Single fixed900s synthetic budget; no silent reruns or tuning.
- A/B changes can support/reject only the proposed residual-mask mechanism on this
  generator. Held-out seeds do not supply real capture diversity. No real-media
  purpose/budget, miss-rate tolerance, role repair or status promotion is adopted.
  Explain how localization might change a future finding and where no disposition
  follows; do not publish another generic request to choose an alternative method.

## Actual Results

### Supplemental Challenge Lock

After the primary128-case result, predeclare seeds600..607. Overlay an identical
72x112 textured background panel at y8..79,x16+slot..127+slot in both sequences,
with distinct moving foregrounds and the same camera translation as above. The
panel moves independently of camera translation; it never overlaps the designated
foreground. Record baseline/compensated witnesses and retained inlier locations.
A remaining panel witness is a false foreground/capture inference but genuine
shared rendered background content, potentially important rather than a waiver.
No parameter change or primary-record overwrite. This is exploratory follow-up,
not a second held-out estimate or an attempt to tune away the first result.

### Measurements

[Experiment code](../scripts/evaluate_oulu_motion253.py) stores paired baseline
and revised findings, inlier coordinates, frame hashes and registration metadata.
All parameters were fixed before the relevant run. Primary and supplemental
records were written once and read back successfully; neither old249 measurements
nor new primary253 measurements were overwritten or rerun to obtain these results.

Each cell below gives baseline/revised witness counts out of8 scene seeds.

| New primary case | Development400..407 | Held-out500..507 |
|---|---:|---:|
| Same content under shared camera motion | 8/8 | 8/8 |
| Same content plus JPEG60 | 8/8 | 8/8 |
| Same content plus translation16,12 | 8/8 | 8/8 |
| Same moving foreground, different backgrounds | 8/8 | 8/8 |
| Shared camera background, different moving foregrounds | 8/0 | 8/0 |
| Independent moving-camera scenes | 0/0 | 0/0 |
| Identical static reused content | 0/0 | 0/0 |
| Identical black sequence | 0/0 | 0/0 |

Across128 new paired cases, the revised branch retained64/64 shared-content/
foreground witnesses and removed16/16 camera-background witnesses for the
different-foreground hypothesis. Independent-scene cases had0/16 witnesses in
both branches. Static reused content still had0/16;16 black cases were also
uninformative. These are toy-case counts, not a real false-positive/miss-rate
estimate, not128 independent captures, and not proof of capture independence.
The baseline measurements here are fresh253 A/B controls, not re-labeled249 runs.

For the16 shared-foreground/different-background cases, all14,572 retained inlier
coordinate observations across both sides and three-slot chains lay within the
known rendered foreground boxes. This is a synthetic localization check; repeated
coordinates/slots are dependent, not14,572 independent observations. Boxes are
used only for post-run evaluation, never supplied to registration or matching.

**Supplemental failure:** all8 independently moving-background-panel cases still
produced witnesses in both branches. Revised support was concentrated in the panel:
2,862/2,872 inlier coordinate observations inside, versus797/7,634 for baseline.
The remaining10 revised points are outside the box; descriptor support can cross
region boundaries. Thus camera compensation is not foreground segmentation and
does not remove independently moving background content. These are false common-
foreground inferences if interpreted that way, but genuine shared rendered pixels,
potentially relevant prohibited reuse rather than evidence to discard.

The supplemental challenge was declared after observing primary results and before
its own execution. It is exploratory falsification, not an untouched held-out set.
Only challenge functions/CLI routing were subsequently added. Reconstructing the
original script bytes reproduces the primary code hash exactly; residual masking,
primary cases and parameters did not change. No further threshold/scene tuning
or escalation was attempted after the8/8 failure.

| Actual resource/check | Result |
|---|---:|
| Primary128 paired cases wall seconds | 27.671 |
| Primary Linux process peak RSS bytes | 131,948,544 |
| Supplemental8 paired cases wall seconds | 2.205 |
| Supplemental process peak RSS bytes | 89,014,272 |
| Primary noncontext registrations accepted/unavailable | 1,792 /256 |
| Fresh OULU module tests | 97 passed,0 failures/errors/skips |
| Test seconds runner/discovery-inclusive | 8.754 /8.899 |

Existing fas/OpenCV4.11.0/NumPy1.26.4 were used without installation. Timings include
both branches and repeated feature extraction, not isolated compensation speed or
an optimized438-endpoint implementation. The900s check is a soft between-case
primary limit, not a production parent watchdog. Native decode/guard/I/O and any
real-workload budget remain unmeasured. The new unit test checks translation sign,
zero residual for pure camera translation, unknown registration, input hash
preservation, lack of automatic disposition and the challenge's shared-panel/
different-foreground construction. Historical test AST is unchanged. Historical
watchdog/45-byte rehash test logs are toy negative controls, not real archive work.
No fresh local full-suite count is claimed; exact new publication CI is required.

## What New Evidence Changes a Possible Decision

This extension addresses one measured failure from249/251: uncorrected camera
translation can put ordinary shared-background texture inside the motion mask.
The paired128-case result supports using compensation as an additional diagnostic
on that generator, not replacing the baseline with a purportedly cleaner truth.

| Paired evidence in a later separately authorized investigation | Concrete interpretation boundary |
|---|---|
| Baseline witness disappears after compensation and support is camera-consistent | The witness may be driven by global scene motion. Inspect its localized content before alleging common foreground/capture. Disappearance is not a rejected edge: camera-consistent recorded background reuse could itself matter. |
| Witness remains with localized independently moving texture | It supplies a more specific region/time hypothesis than a whole-frame match. A substantive reviewer can test distinctive foreground texture/occlusion/artifact correspondence under251's rubric; no capture conclusion follows from the residual mask alone. |
| Witness remains on independently moving background or a display/panel | Preserve it as background-content evidence, not a foreground label. Ordinary recurring scene activity and reused recorded content still require a discriminating interpretation; the8-case failure shows that compensation cannot adjudicate this. |
| No witness, unavailable registration or inadequate visibility | Retain non-detection/unknown and the baseline evidence. No automatic clearance, row removal, neighbor-edge outcome propagation or low-score negative rule. |

This can change which allegation is worth investigating and where corroboration
is needed; it cannot provide an accepted scientific disposition by itself. Keep
both witness streams, failed registrations and spatial evidence if this diagnostic
is ever selected. Do not discard a potential shared-background violation merely
because the compensated branch suppresses it. Synthetic truth regions are not
available as an oracle for real videos, and no438-video annotation/paperwork tier
is instituted by this experiment.

## Adequacy and Actual Stop

**Recommendation: retain this as a synthetic diagnostic result, not an audit-
closure method or permission for a399-edge real run.** It improves a specific
camera-translation confound while demonstrably retaining the dynamic-background
ambiguity and static-content blind spot. It does not validate semantic segmentation,
rotation/perspective/parallax, large foreground-dominated camera estimates, repeated
textures, camera drift beyond10%, speed changes, quantile gaps or transient reuse.
Registration rejection is unknown, not safe absence. Development and held-out
seeds share the same generator; no representative-real-data claim or tolerance
is supplied. No universal hidden-ancestry proof is required by adopted247.

No real-media purpose/resource choice is inferred from this safe synthetic work.
Investigative use would explicitly accept possible zero resolutions and both
branches' limitations; closure still lacks demonstrated evidence adequacy. This
submission is the concrete measured extension requested in252, not a generic
protocol to choose an alternative or an acknowledgment/activation of251. Stop
this experiment without another unchanged-status response checkpoint or automatic
native tier. No method, scientific tolerance, provider contact or real budget is
adopted; no future experiment or real screening is silently queued.

## Publication and Retained State

[Aggregate](../results/phase1/oulu-motion253-ablation-v1.json) binds new controls,
locks, code transition and technical verification. Source251 CI accepted by252
is reused without re-query: head`7da0e727f20450124e2b97b09c23d7789c2cc5f7`,
[run39533196022](https://github.com/lathevinh/fas/actions/runs/39533196022),
[job119003691285](https://github.com/lathevinh/fas/actions/runs/39533196022/job/119003691285),
completed/success/all12 steps. New exact head/run/job CI is pending at creation;
final handoff/additive receipt must verify all12 actual successful completed steps
including Complete job. CI is not independent scientific replication.

Matcher/planner251, runner249 and frozen399-edge/438-endpoint/91-component records
are untouched. No new399 planning rows or source rehashes were needed. No real
media decode/image inspection, pair screening or dispositions occurred. Preserve
85 accepted effective/semantic-owner/AI prefix,399 unadjudicated cross-role edges,
6555 residual context/noncandidate coverage0; historical disagreement1/unresolved0;
4950 originals/4949 selected/terminal failure1; calibration990 original/989 frame-
available/zero actual score-fit. All8 statuses not_audited; audit/scientific readiness
incomplete. Other dataset work, model/detector/source/target execution, analysis
freeze and locked evaluation remain blocked.