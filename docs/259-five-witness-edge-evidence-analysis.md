# 259 - Evidence Analysis of All Five OULU Witness Edges

Date: 2026-10-21

## Scope and Actual Work

[Review258](258-review-doc257-completed-investigation.md) accepts257's technical
completion and closes the256 final-verdict defect. This package analyzes all five
persisted witness edges, including the baseline-only finding and the two not
previously visually reviewed. No399-pair repeat, media decode, new crop/overlay,
native tier, method change, synthetic ablation or archive rehash was performed.

Eight existing contact sheets were opened in259, including five revisits for the
specific matched-order comparison and three previously unopened sheets:72 tiles
viewed, all five findings covered. Across257/259 there are13 sheet-open calls but
only eight unique sheets/72 unique sampled frames, not117 independent observations.
All eight sheets remain width288,height573 with nine96x171 preview tiles. Native integrity
checks from257 are reused, not confused with these visual observations.

Aliases A-E refer only to these five edges in their frozen order. Private mapping,
pair/media/endpoint parents, full inliers/matrices, exact order hashes and actual
image-tool calls remain private. Orders below are zero-based native decode orders,
not queue ranks or synchronized timestamps. Boxes are descriptive normalized
extents of stored inlier points, rounded for display, not newly searched crops or
semantic segmentation. Shared endpoints are dependent; no outcome propagates.

## Per-Edge Evidence

**A: mottled lower-torso texture, both branches.** Baseline and compensated chains
both pair left18/37/56 with right18/37/56. Baseline inliers87/71/21 occupy roughly
left x0.063-0.846,y0.695-0.906 and right x0.135-0.846,y0.678-0.863. Compensated
inliers71/65/30 mostly cover that lower region; its first pair also has limited
support as high as y0.496. The opened tiles show a dark upper garment and a broad
mottled printed region below it, with differences in tone and apparent framing.
Repeated motif arrangement supports a real texture correspondence, not a generic
room-only explanation. A recurring physical print/fold pattern can explain this;
reused recorded garment pixels can also explain it. Tonal/framing differences do
not reject recording transformations. Preview sampling does not resolve unique
fold/deformation or recording artifacts through the chain. **Unresolved:** no
observed discriminating material/recording detail; no capture or scoped negative
disposition is supported.

**B: baseline-only finding retained.** Baseline pairs left47/59/71 with right37/56/75,
with114/41/35 inliers. Most support is below y0.68; sparse upper points expand
the full extents to left y0.219-0.953/right y0.205-0.920. Opened views show the
mottled garment region beneath a dark chest band at these orders, with modest
framing/tone changes. Physical fabric reuse and recorded-region reuse remain
competing explanations. Compensation has17 individual supported geometries but
no accepted three-slot chain, versus20 baseline geometries. That difference does
not experimentally localize the cause or establish camera-background-only support;
compensated endpoint records were registered at all baseline-selected slots.
**Unresolved:** neither the previews nor suppression identify which explanation
caused the baseline chain. Do not discard this edge, label it a false positive or
infer clearance from the compensated branch.

**C: checked garment/dark outerwear, both branches.** Both branches pair left71/83/95
with right112/131/150. Baseline inliers21/42/43 and compensated27/25/25 mostly occupy
the lower-left/central garment area. Baseline second pair has extents approximately
left x0.163-0.490,y0.649-0.951/right x0.184-0.507,y0.628-0.920; the third pair has
sparse upper support as well. Opened tiles show a checked inner garment bordered
by dark outerwear. A repeating check grid, garment boundaries and physical folds
can generate local stable geometry, but reused recorded versions of those pixels
remain possible. Neither a repeated check pattern nor its spatial location proves
or excludes recording reuse. **Unresolved:** grid-cell/fold/occlusion evolution
and incidental recording detail are not separable at this preview resolution.

**D: mottled garment with sleeve/torso support, newly viewed.** Both branches pair
left54/72/90 with right18/37/56. Baseline inliers139/128/153 and compensated137/134/103
support multiple garment areas, not just a small isolated match. Baseline union
extents are roughly left x0.083-0.830,y0.295-0.945/right x0.094-0.854,y0.297-0.945.
Opened sheets show closely arranged mottled sleeve/torso motifs and garment
silhouette over a comparatively stable setting, with slight framing/brightness
differences. This makes specific fold/motif-junction and incidental recording-
artifact correspondence worth examining; it is not confirmation. A stable physical
garment/pose and derived recorded content both predict broad affine texture
support. **Unresolved:** no unique synchronized crease/occlusion/recording artifact
was resolved through these three order pairs. Larger inlier counts do not choose
between those hypotheses. A minimal additional-detail proposal is below.

**E: checked garment/outerwear, newly viewed; branch chains differ.** Baseline pairs
left108/126/145 with right112/131/150, inliers22/52/72. Compensated instead pairs
left72/90/108 with the same right112/131/150, inliers25/30/40. Baseline support is
roughly left x0.175-0.570,y0.633-0.959/right x0.188-0.563,y0.643-0.953; compensated
extends left to x0.642,y0.615/right x0.635,y0.627. Opened sheets show a checked
garment and dark outerwear consistent with the matched lower-frame regions.
Recurring near-static texture can support several temporal alignments; recorded
reuse can as well. These are first qualifying chains in fixed search order, not
estimates of true temporal synchronization or evidence that one branch found the
correct source sequence. **Unresolved:** branch-specific order ambiguity and
unresolved small fabric/fold details; no supported independent-capture or derived-
content judgment. E is assessed separately from C despite their shared endpoint.

No face/identity inference was used. Shared physical texture is a competing
hypothesis, not an accepted explanation that clears any entire edge. Reused
recorded background would also remain material, not automatically excused by
location. There is no supported confirmation or scoped rejection from these
previews. Five explicit analysis outcomes are unresolved with the reasons above;
zero new effective/owner/semantic dispositions are entered. All399 scientific
relationships remain unadjudicated, not five confirmed leaks or394 accepted negatives.

## One Concrete Additional-Detail Decision

**Proposal only, not executed or authorized by258:** one matched-region check for
D, not a full-native pass over the five findings or399 pairs. The actual question
is whether small crease/motif-junction or incidental recording artifacts evolve
correspondingly across D's three selected pairs, beyond recurrence of the printed
material. Those details are missing from the96x171 previews. D is selected for
that visible multiregion hypothesis, not as a score-based scientific disposition.

- Exact source orders: left54/72/90, right18/37/56. Exact private media/parent/hash
  bindings are in the analysis record. No adaptive replacement or extra orders.
- Inspect only native garment windows x[86,929),y[1132,1824) on each1080x1920
  source frame, corresponding to the fixed normalized window x[0.08,0.86],
  y[0.59,0.95] with outward pixel rounding. These six843x692 crops test the lower
  garment allegation only; upper support and other regions remain unknown.
- Strict extraction would still stream each accepted video once to verify all
  native frames/count/EOF/hashes:146+151=297 frames,1,847,577,600 RGB bytes, from
  two selected payloads, not six whole-video native banks. Capture six crops only;
  their uncompressed RGB total is10,500,408 bytes. No raw frame bank, dense search,
  image upsampling, new matcher or threshold tuning is proposed.
- Proposed ceilings:1800s package,180s/decoder,2GiB aggregate RSS,128MiB temporary,
  256MiB persisted diagnostics,640MiB initial free reserve. Fixed six-crop output,
  final verdict consistency and complete affected-row accounting; stop if unsafe
  or insufficient rather than add evidence or raise caps. These are prospective
  ceilings, not measured259 resource claims or an execution authorization.
- Record the actual observed junction/fold/artifact correspondences or divergence
  with exact orders/regions. Print-motif similarity alone remains insufficient.
  Lack of matching incidental detail is not automatic whole-edge rejection. If
  the detail cannot discriminate, retain unresolved and report why; no automatic
  follow-on tier. Genuine corroborated prohibited derivation is a hard stop, not
  a role/selector/seed repair opportunity.

This is a substantive evidence-scope decision after an actual localized finding,
not a request to activate accepted257 or approve separate routine export/import
steps. No native view, provider contact or new real attempt has been performed.

## Missing Basis for394 Non-Detections

The [adopted247 definition](247-dated-finite-lineage-audit-amendment.md) requires a
validated finite protocol adequate to its stated allegations/coverage and explicit
disposition of material unresolved relationships; it does not demand universal
ancestry proof. The missing acceptance basis is specific:

- Nine quantiles and motion-mask ORB chains do not address known static-content,
  short-lived between-quantile, small/occluded-region or unvalidated transformation
  allegations. The earlier identical-static controls were missed, not a passed
  static-reuse test. No additional negative assurance follows from those blind spots.
- Synthetic moving-texture success and the camera-compensation ablation do not
  supply representative known-parent/independent-control validation for those
  material residual cases, or an adopted scientific uncertainty/miss-rate basis.
- Five witness-selected edges, shared endpoint dependence and texture-dominated
  geometry cannot estimate false-negative coverage for the394 non-detections or
  noncandidates. No leak rate, sensitivity or independent-rater confidence is
  computed from this selective analysis. AI agreement and absent exact overlap
  remain inadmissible shortcuts to clearance.

The D proposal can test one local recorded-content hypothesis; it cannot validate
the declared screen for394 negatives. No justified closure method/acceptance
decision for all394 is supplied by this evidence. Retain that gap explicitly,
without automatically commissioning a new matcher, rerunning394, demanding438
capture certificates or silently weakening247. Local OULU acceptance, cross-domain
assurance and later preprocessing/scientific prerequisites remain separate.

## Verification, State and Publication

Analysis checks bind the accepted257 summary/technical receipt, all five exact
pair records, their eight endpoint/media/PNG parents and matched-order/inlier
joins. Original records and images are read-only. Existing100 focused tests and
257 publication CI are inherited evidence, not rerun259 tests. This documentation/
analysis package changes no executable code, frozen config, status or owner answer.
The [aggregate](../results/phase1/oulu-witness259-analysis-v1.json) will bind actual
analysis/inspection receipts without publishing private identifiers, ranks, paths
or images. Final new publication CI must be observed for the actual new full head,
run/job and all12 successful steps including Complete job;257 CI is not a substitute.

Retain399/399 technical comparisons, five witness candidates,394 non-detections,
accepted85-prefix,6,555 residual context,zero noncandidate coverage increment,
4,950 originals/4,949 selected/one terminal failure,calibration990/989/zero score-fit,
historical disagreement1/unresolved0 and all8 not_audited. Scientific readiness is
false. Stop for one substantive review of these five evidence analyses and the
bounded D proposal; no extraction, automatic further experiment or status promotion.