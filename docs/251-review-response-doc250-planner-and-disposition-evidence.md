# 251 - Review250 Response: Component Repair and Disposition Evidence

Date: 2026-10-21
Base commit: `6d9af4c`; authority: [Review250](250-review-doc249-temporal-method-controls.md).
Scope: repair and test the metadata planner; specify a substantive evidential
decision without executing real-media screening or adopting new tolerances.

## Recommendation

**Do not commission the399-edge witness-only pass as an audit-closure method.**
Keep the audit incomplete with the frozen population and scientific gates intact.
The repair below makes graph accounting fail closed; it does not repair the
scientific background confound or static/temporal blind spots. A run that may
resolve zero relationships must not be commissioned as if it will clear399.

This package supplies both the actual engineering correction and the prospective
disposition rubric requested by250. The rubric is not an executed adjudication,
validated new classifier, adopted acceptance tolerance or request to activate
unchanged wording. Amendment247 remains adopted; no universal capture-independence
proof or compulsory provenance paperwork for438 endpoints is added.

## Planner Repair and Measured Verification

The old planner checked ranks and endpoint unions but neither connectivity nor
global endpoint disjointness. A fresh regression first failed twice: `(a,b)` plus
`(b,c)` incorrectly passed as two components, and `(a,b)` plus `(c,d)` incorrectly
passed as one. Both failures were `ValueError not raised`, not media failures.

[Planner](../src/fas/content_correspondence.py) now traverses each component's
undirected adjacency and requires every vertex to be reached; a global assigned
vertex set rejects endpoints shared across components. Together with existing
exact rank coverage and endpoint checks, this enforces the connected-component
partition of the supplied graph. It preserves proposed component ordering,
digests, edge ranks, endpoint commitments and valid output schema, rather than
silently repartitioning malformed inputs or modifying the frozen population.

| Fresh check | Observed result |
|---|---|
| New regression before repair | Two failed subtests, both review counterexamples reproduced |
| New regression and three neighboring correspondence tests after repair | 4 passed,0.445s |
| Independent global-traversal oracle over every edge partition of all simple graphs on four named vertices | 64 graphs,877 partitions;64 accepted,813 rejected; no disagreement |
| Actual frozen graph | 399 edges/438 endpoints/91 components; canonical partition matches |
| Existing private249 rows | Every current output field equals the old row's value; old extra parent-evidence field remains in the untouched original record |
| Relevant immutable source records | 837 hashes checked; no archives or images read |
| Fresh OULU module | 96 passed,0 failures/errors/skips;7.681s including discovery,7.595s runner |
| Preservation | Matcher AST outside planner unchanged; all historical test AST unchanged; synthetic runner unchanged |

The exhaustive check is finite software verification, not exhaustive scientific
validation or a general graph-size runtime benchmark. It includes the empty graph.
No192-case primary or8-case challenge measurement was rerun. Their immutable
records and original code commitments remain historical evidence, not relabeled
as runs of the revised planner. New verification binds the source transition
additively. Existing archive-guard contexts are not implicitly updated or run.
Expected watchdog/45-byte toy rehash logs in the96 tests are negative controls,
not fresh real archive failures or reads. No fresh local full-suite claim is made;
new publication CI must run the repository gates on the exact new head.

## How Evidence Could Support an Individual Disposition

The following are **prospective scientific review criteria**, not implemented
score thresholds or accepted outcomes. A technical witness, an interpretation of
its location, and a disposition under42/247 must be recorded separately. A reviewer
must be able to trace a proposed outcome to exact existing pair/payload/frame
parents and stated coverage; hashes prove that binding, not the visual judgment.

| Evidence situation | Discriminating judgment and corroboration | Permissible outcome if substantively accepted |
|---|---|---|
| Witness on a purportedly reused foreground or region | Inspect the matched regions at identified order pairs and temporal context. Ask whether distinctive changing texture, occlusion or recording artifacts align under one interpretable transform, rather than merely the same pose, subject, room or generic shape. Corroboration may be a temporally distinctive sequence/artifact or an existing source-to-derived-content link. Repeated ORB scores, three renders of the same pixels, or AI agreement are not independent corroboration. | If the evidence actually establishes prohibited shared/derived content across the frozen boundary, record confirmation and stop affected science. A witness alone remains an investigation finding. |
| Support lies on background | Distinguish a common physical scene from reuse of recorded/rendered background pixels. Identify which inliers and temporal details support which explanation; quadrant counts cannot do this. Matching a room alone does not establish common capture. Conversely, distinctive reused background content can itself be a prohibited derivation: location outside the foreground is not a waiver. | An adequately supported ordinary-scene explanation may dispose of that particular apparent match, not automatically clear the edge. Distinctive prohibited reuse follows the hard-error branch; unresolved alternatives stay unresolved. |
| A candidate's specific suspicion is explained without prohibited reuse | A scoped not-supported disposition requires that the actual candidate reason has been localized and adequately tested, all other concrete material allegations for that edge are addressed, and the finite protocol's coverage/validation is accepted for that stated question. Visible divergence can corroborate a bounded observation but cannot establish arbitrary hidden-content absence. Do not assert that background caused the pHash rank without evidence of that contribution. | Only a genuine scientific decision can accept a scoped rejection of the candidate allegation, with residual limitations explicit. This is not a new automatic negative rule. Method249 has not established the required adequacy. |
| No witness, weak texture/motion, dark content, missing decode or unmodeled temporal/region relation | A non-detection says only that this finite matcher supplied no supported witness. A different result could come from a genuinely discriminating existing observation or interpretable authentic source relationship, if one actually exists. A different filename, subject/session label or graph vertex does not supply it. | Retain non-detection/failure separately from scientific uncertainty. No clearance or accepted rejection from a low score, exact-hash absence or nine samples alone. |
| Available evidence cannot decide between common content and shared-scene explanations | Name the precise pair-specific competing explanations and what observation would distinguish them. Identify a minimal additional region/order/context only if an actual hypothesis supports it and it is separately authorized; do not invent a mandatory native tier, all-frame replay or paperwork collection. | Materially unresolved relationship remains unresolved and audit incomplete. No new effective owner answer or disposition is fabricated. |

Corroborating visual cues may be complementary evidence from the same recording;
they are not statistically independent captures merely because several cues agree.
Authentic existing provenance is optional, not a requirement to contact providers
or obtain438 new attestations. No such material is invented or collected here.
Any genuine conflict between provenance and pixels must be preserved and reviewed,
not resolved by majority vote or by editing historical answers.

A component links dependent edges for reuse/accounting; it does not make a
neighboring edge inherit confirmation or rejection. An accepted explanation for
one localized hit does not discharge a different material allegation. Any local
finding remains bounded to that edge/evidence question;85-prefix acceptance and
the6555 residual context are not new independent controls or dispositions.

## Non-Detections and the Finite Claim

Under adopted247, finite audit completion is possible without certifying absence
of every unknown ancestry or transformation. It still requires an executed,
adequate finite protocol, reported controls and coverage, and explicit scientific
dispositions of detected or materially unresolved prohibited relationships.
An unexplored theoretical possibility is not by itself a new universal-proof
requirement. A current material unresolved candidate cannot be silently converted
into that harmless theoretical category just because this matcher missed it.

For249 specifically, the16 identical static misses,8/8 shared-moving-background
challenge witnesses, fixed slot speed/offsets, quantile gaps and lack of real
validation prevent using its non-detections as negative lineage evidence. Those
are inherited reported measurements accepted within250's verification limits,
not newly reproduced in251. No foreground classifier, background-excision rule,
arbitrary low-score threshold, miss-rate tolerance or new scientific method is
implemented/validated here. The disposition rubric does not fill that gap by prose.

An individual future edge might receive a supported confirmation or scoped
rejection under the rubric; there is no assurance that all399 could. Failure to
resolve a material edge means incomplete audit, not permission to drop the row,
repair roles or weaken the claim after seeing outcomes. Non-candidate coverage
remains zero; neither the candidate generator nor joined cross-domain assurance
is validated by repairing this graph function.

## Exact Scientific Choice and Execution Boundary

The present recommendation is to **retain incomplete status and decline a full
real-data witness-only run for closure**. No new pair evidence supplied by250/251
changes that recommendation. This does not assert that all existing438 endpoint
materials were searched or that no other content method could work.

The distinct choice, if diagnostic triage is wanted despite this recommendation,
is whether localized correspondence has enough investigative value to justify a
single run over exactly399 edges/438 endpoints while explicitly accepting that
zero pairs may resolve, all negative/ambiguous findings remain unresolved, and
successful technical completion is not audit acceptance. The proposed249 ceiling
is7200s total/180s per decoder/2GiB RSS/128MiB temporary payload/128MiB feature
arrays/256MiB diagnostics/640MiB initial reserve. Feasibility remains unmeasured:
strict decoding entails58,733 frames and365,366,246,400 native RGB bytes. Budget
or endpoint failure must retain all affected rows; no silent scope reduction.
No real runner or supervisor adaptation is implemented or commissioned here.

That limited-purpose/resource choice must not be inferred from acceptance of this
planner repair, amendment247 or a passing CI. If closure rather than investigation
is required, a genuinely discriminating finite evidence method with representative
validation must be chosen before a run; no such alternative is validated here.
There is no new publication/activation prerequisite or request to reapprove old
wording. This single package supplies the repair, measured checks, disposition
criteria, limitation and concrete optional-purpose decision together.

## Publication and Retained State

[Aggregate](../results/phase1/oulu-planner-disposition251-v1.json) binds the new
technical record and code transition. Source249 CI is accepted in250: head
`e57dbb483fabccaa1b37dc43a398aed1e9044dd9`,
[run39531461871](https://github.com/lathevinh/fas/actions/runs/39531461871),
[job118998086643](https://github.com/lathevinh/fas/actions/runs/39531461871/job/118998086643),
completed/success/all12 steps. It is not new251 CI. New head/run/job verification
is pending at creation; final handoff/additive private publication receipt must
verify completed-success and all12 actual steps including Complete job.

New real residual pairs screened0, new dispositions0;399 cross-role relationships
remain unadjudicated, not confirmed leakage; residual context6555/non-candidate
coverage0. Accepted effective/semantic-owner/AI prefix85 is unchanged. Preserve
historical disagreement1/unresolved0;4950 originals/4949 selected/one terminal
failure; calibration990 original/989 frame-available/zero actual score-fit.
All8 statuses remain not_audited; OULU audit and scientific readiness incomplete.
No media decode/visual adjudication/provider contact/model/detector/source/target
execution, analysis freeze, locked evaluation or unrelated dataset work occurs.