# Response to Review 120: Pair-5 Evidence-Linked Reconciliation

Date: 2026-10-10
Base commit: `ed47045`
Review: [Document 120](120-review-doc119-oulu-human-review-import.md)

Review 120 accepts nine AI/human agreements as bounded screen-level rejections.
Pair 5 / queue rank 4 remains unresolved. This checkpoint examines that pair only
and records a separate evidence-linked reconciliation without rewriting the
original AI proposal, human submission or imported effective ledger.

## Prospective Scope and Completion Criteria

- Verify accepted handoff definition, imported human ledger and original AI record.
- Inspect existing full-resolution frames at the first, middle and last fixed
  temporal slots for each side: left orders 0/75/150 and right orders 0/60/120.
  These positions are chosen before viewing, not by apparent outcome.
- Record concrete frame-linked foreground/background and temporal observations,
  without inferring face identity or acquisition provenance.
- Create a separate immutable reconciliation record bound to both prior ledgers
  and all actually inspected image hashes. Do not change either original answer.
- Use one of the three accepted dispositions; retain uncertain if these sparse
  views cannot resolve possible partial/derived-content ambiguity.
- Treat this inspection as AI-assisted, not a new human reviewer or authenticated
  independent adjudication. An uncertainty-retaining record cannot close batch 01.
- Stop for review of the published reconciliation checkpoint before any next queue
  batch. Same/derived cross-role confirmation triggers a scientific decision stop.

## Actual Inspection and Result

Checkpoint **1.5K creates a separate Pair-5 reconciliation proposal**. The
reviewer is GitHub Copilot, using AI-assisted visual inspection; no new human
review, independent reviewer or owner reconciliation approval is fabricated.
The existing ten-item owner JSON is not requested again or changed.

Exactly **six** existing full-resolution 1080x1920 PNGs were newly viewed:

| Fixed temporal slot | Left decode order | Right decode order | Recorded evidence |
| --- | ---: | ---: | --- |
| First | 0 | 0 | Distinct foreground garment construction and inner-layer detail at the actual screening trigger frames |
| Middle | 75 | 60 | Those distinctions persist; background-grid/fixture configurations also differ |
| Last | 150 | 120 | Distinct foreground details remain; the inspected snapshots within each side are broadly stable |

These are relative sampling positions, **not established temporal alignment**.
The pair-specific private rationale identifies concrete foreground structures
and background details at each referenced frame, explains why the lower-detail
bulky-outerwear/ceiling composition previously looked ambiguous, and distinguishes
observed differences from assumptions about identity, roles or acquisition.
Detailed observations and identities remain private.

**Proposed reconciliation disposition: `rejected_false_positive`.** The enlarged
views distinguish persistent foreground constructions that were insufficiently
resolved in the earlier small panels. Their common coarse layout plausibly
explains the perceptual-screen trigger; the inspected ranks do not show a
recognizable shared rendered foreground sequence. This supports the owner's
screen-level rejection for the observed relationship, not an absence-of-any-source
claim. Both original dispositions remain recorded unchanged.

The result is **proposed pending owner checkpoint review**, not an accepted final
reconciliation. Original effective ledger: **9 rejection / 1 uncertain**. The
Pair-5 effective disposition remains `uncertain_insufficient_evidence` until an
explicit acceptance/reconciliation decision is separately recorded. This
checkpoint does not give an AI proposal authority to overwrite the prior ledger.
Review 120 already accepts the other nine as bounded screen-level rejections;
they need no repeat human JSON or new adjudication here.

## Limits and Alternatives

Only six of the 34 available full-resolution PNGs were newly inspected, not the
entire videos. Small changes within the inspected snapshots do not establish a
full motion trajectory or prove absence of motion/temporal correspondence.
Shifted short subsequences and intervening frames are not ruled out. No geometric
registration, transformed-region search or original-capture provenance analysis
was performed. Foreground differences cannot rule out arbitrary compositing,
editing or every shared background/source outside the observed screen scope.

If checkpoint review finds these distinctions insufficient for the scoped
rejection, **retain uncertain** and specify the additional temporal/region
evidence needed. No automatic closure is required merely to advance the queue.
There is no same/derived-content confirmation here. Such a later confirmation
still triggers a prospective scientific-decision stop before execution.

## Immutable Record and Verification

Private input observations and the two bound outputs are:

```text
/mnt/e/FAS-private/artifacts/phase1/oulu_pair5_reconciliation_observations_v1.json
/mnt/e/FAS-private/artifacts/phase1/oulu_pair5_reconciliation_v1/record.json
/mnt/e/FAS-private/artifacts/phase1/oulu_pair5_reconciliation_v1/summary.json
```

The record binds Review 120, accepted visual/import public reports, accepted
handoff definition, Pair-5 packet, original AI and human pair records, original
owner JSON, both pair bundles, frozen artifacts, observation input, immutable
writer code and all six actually inspected PNG/RGB hashes. Observations cite
`left:0/75/150` and `right:0/60/120` explicitly. The prospective-scope draft hash
is an authoring trace, not the hash of this completed document.

All six saved PNGs were read back: dimensions and RGB bytes match the accepted
full-resolution frame identities. Original AI/human dispositions and their full
accepted bundles were verified before writing. Protected snapshots cover the
accepted packet root, AI/human ledger roots, handoff root and 13 frozen files;
they remain unchanged after writing. The 67 original preparation files still
match their accepted preparation rerun.

The existing immutable writer creates the separate records and refuses a second
write. Serialization replay into `oulu_pair5_reconciliation_rerun_v1` produces
**two byte-identical files**. This is deterministic record serialization, not a
second independent visual judgment or new media decode. No new production code,
tests, policy, packages or environment were introduced.

[Public aggregate](../results/phase1/oulu-pair5-reconciliation-v1.json) bindings:

- Reconciliation record SHA-256: `c2b65b10b185888f94cdb8adc61f74e12a2d2fb51aa2d36269428f81f7eb08cb`.
- Summary SHA-256: `8d130a7ee0715cfba9d0c2429f92d1ea680f6111b483775b53fcdc15f9c87a52`.
- Observation input SHA-256: `a037205d2c31c269deae79f759457a7caa76d20d073871b6dc92670cee5566f2`.

Focused regression: **52/52**, zero failures/errors (4.186 seconds). Actual
record checks cover frame references, accepted PNG/RGB identities, source hashes,
readback, byte-identical replay, refusal to overwrite and unchanged protected
snapshots. Schema passes; data-audit/source-dry-run/analysis-freeze/locked-evaluation
remain blocked. Full 239-test regression is not rerun locally for this
data/documentation-only checkpoint; fresh pushed-commit CI runs the standard
suite/gates. No new extraction/decode, research detector/model, training or target
evaluation ran.

## Stop Point

**Reconciliation proposal written; reconciliation acceptance pending.** Review
this checkpoint's evidence-linked result and its narrow scope before any next
batch. Acceptance must be a separate explicit record bound to this proposal,
not silent promotion or rewriting the owner submission/AI ledger. If rejected
as insufficient, keep Pair 5 uncertain and obtain the specified stronger evidence.

The batch is not marked closed, the next **75 highest-risk pairs are not started**,
and model execution/scientific readiness remain false. Private frame-specific
rationale is available in the bound record for owner inspection; no second copy
of the ten-item human JSON is needed.