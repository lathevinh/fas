# Review Response to Document 84: SiW-Mv2 Amendment

Date: 2026-10-08
Reviewed document: [Document 84](84-review-siwmv2-replacement-and-protocol-amendment.md)
Document baseline: `9586482`
Scope: critical review and correction of Document 83, not amendment implementation

## Findings

### 1. High Priority: Extend Video Fallback to Every Split Boundary

Document 84's source-role policy and bootstrap policy are valid, but the amendment
must also explicitly cover **head inner validation and matched sample-OOF**.
[Document 42 Section 6.4](42-data-to-experiment-implementation-plan.md#L396) and
[Section 8.1](42-data-to-experiment-implementation-plan.md#L489) currently describe
these as subject-disjoint. Merely changing permanent source roles and the target
bootstrap leaves those requirements undefined for SiW-Mv2.

Freeze one dataset-specific grouping policy: known participant/source-identity
groups when available, otherwise complete video groups for SiW-Mv2. Apply it to
permanent roles, head inner folds, matched sample-OOF, fold-local calibration and
all derived frames/crops. Unknown subject identity must remain an explicit missing
value, not a fabricated unique identity or a single common group containing every
video. Both OOF comparators must use the same candidate ledger and grouping unit.

This is a required amendment detail before split-builder implementation, not an
argument for blocking the replacement indefinitely. An implementation that invents
subject IDs, cannot construct sample-OOF, or lets frames of one video cross split
boundaries would not implement the intended comparison.

### 2. Medium Priority: Video Fallback Is Not Proof of Participant Disjointness

Document 84 correctly calls missing participant identity a limitation. State its
exact consequence in the new manifest/analysis contract: video-group separation
does not certify participant-disjoint roles or eliminate dependence between videos
of the same person/source face. The local README's 785 live videos from 493 subjects
already establishes that videos are not interchangeable with unique people.

Video-cluster bootstrap is permitted by the existing plan, but its uncertainty
must be described at the declared video-group approximation, not as a verified
participant-clustered confidence interval. Preserve paired multiplicities across
methods and seeds and resample separately inside each target. Do not claim a pure
unseen-subject result or generalization beyond the evaluated dataset set.

Keep exact/near-duplicate and derived-frame ancestry checks as required gates;
unavailable participant IDs do not waive those checks. A later provider identity
map could support additional grouped sensitivity analysis, but obtaining that map
is not a prerequisite imposed by this review for the permitted video fallback.

### 3. Medium Priority: Make the Intersection an Executable, Versioned Population

The proposed 1,680-video universe is arithmetically supported by
[the real prerequisite report](../results/phase1/siwmv2-prerequisites.json):

| Eligible Protocol I subset | Live | Attack | Total |
|---|---:|---:|---:|
| Source-training membership | 524 | 533 | 1,057 |
| Target-test membership | 261 | 362 | 623 |
| Combined primary universe | 785 | 895 | 1,680 |

The adapter must implement the intersection of available raw video tokens with
the **unique** tokens in the four pinned lists. In particular, the spoof training
file contains 1,400 rows but only 533 unique tokens: its 867 balancing repeats
must not become extra transactions, source-role allocations or implicit weights.
Keep the frozen equal-domain/class training and natural-prevalence risk objectives;
do not inherit the reference model's balancing recipe silently.

Freeze the list revision/hashes, label mapping, exclusion reason and eligible-ID
digest. Preserve all 1,700 observed videos in the raw inventory, mark the 20 unlisted
spoof videos out of primary scope, and record the 11 listed-but-unavailable live
references separately (7 train, 4 test). Do not label the 1,680 intersection as
complete official Protocol I release reconciliation or count missing references
as attempted target transactions. Test exact IDs, not only matching totals.

This policy can be defined prospectively without provider correction. Provider
clarification would improve provenance/comparability but is not inherently required
to define this explicitly named derivative benchmark. Acquisition approval and
payload/hash/decode audits remain separate ordinary intake gates.

### 4. Medium Priority: Retain Decision Rules, but Acknowledge a New Estimand Population

Document 84's recommendation not to retune minimum effects or pass rules is sound.
However, "only the target set changes" is too narrow if read as an implementation
contract. Source-training composition changes in three folds; the SiW-Mv2 target
uses an intersected population and video clustering, and attack-family exposure
differs from historical MCIO.

Keep the RQ formulas, seeds, consistency/event rules, paired comparisons, macro
weighting and harm tolerances. Describe the resulting estimands as evaluated on
the **new four-domain Protocol-I-intersection population**, not as another estimate
of the old MCIO population. Macro gains are conditional on these four datasets and
the fixed recipes; they do not isolate an acquisition-only or attack-family-only
causal effect. Domain-OOF is still dataset-OOF, not attack-family-OOF.

Track A should remain separately labeled historical MCIO/literature context, as
Document 84 proposes. No historical Track-A checkpoint, calibration, threshold,
sample membership or result may substitute for fitting/evaluation under the new
primary Track-B source set. The old MCIO artifact history must remain identifiable.

## Corrections I Accept

**Document 84 is right about the central correction.**
[Document 42 Section 6.2](42-data-to-experiment-implementation-plan.md#L353)
expressly allows complete video groups when subject identity is genuinely unavailable,
and Section 11.8 permits subject/video cluster bootstrap. My Document 83 assertion
that a provider participant map was necessarily required for core replacement was
too strict. I retract that unconditional blocker; do not keep waiting for a map merely
because Document 83 requested one.

Likewise, exact equality to the original lists need not block a **new, prospectively
defined intersection benchmark**. Preserve the immutable prerequisite report as
historical evidence; produce new eligibility/adapter artifacts rather than rewriting
its mismatch counts or readiness flags into a claim of full-release equivalence.

The lack of participant IDs should be documented from the inspected release rather
than claimed as knowledge about all metadata the provider might possess. The known
fallback is preferable to pretending that video tokens encode participant identity.

The CI statement in Document 84 was independently checked: GitHub Actions `validate`
on exact implementation commit `c9147e84f695e5e513942f6da6e4bd9b22f82169` is
`completed / success`, finishing at 2026-10-08T04:33:08Z:
https://github.com/lathevinh/fas/actions/runs/37728007608/job/113150471651.
This certifies that implementation check, not dataset access or scientific readiness.

## Disposition and Next Checkpoint

**Approve the amendment direction; require the four clarifications above in the
implementation contract. No fatal objection to the proposed replacement was found.**

Checkpoint 1.3S is accepted by Document 84. The next separately reviewed checkpoint
should implement and freeze the dated four-domain amendment, including the explicit
video-group fallback, Protocol I intersection, source/test counts and all-14-attack
scope. Freeze a new study identity and update every active domain enumeration,
claim-population reference, validator and test before accepting the rewrite.

After that checkpoint is pushed and approved, implement/review the SiW-Mv2 metadata
adapter, then separately advance MSU. Preserve the existing checkpoint discipline;
Document 84's three-item next-step list is not permission to run all three without
intermediate review. No model inference starts before the amended prerequisite
gates and artifact/config lineage are satisfied.

This response changes no active configs, source roles, manifests, readiness gates
or training authorization. It records the review, corrects my prior reasoning and
identifies what the upcoming amendment must make unambiguous.