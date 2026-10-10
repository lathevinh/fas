# 118 — Review of Document 117: OULU Bound Human-Review Handoff

Date: 2026-10-10  
Repository: `lathevinh/fas`  
Reviewed commit: `41264039919a844e7c3bd6553348c64405eb4f75`  
Reviewed document: `docs/117-review-response-doc116-oulu-human-review-handoff.md`

## Verdict

**DOCUMENT 117 — ACCEPTED.**

**CHECKPOINT 1.5I OULU BOUND HUMAN-REVIEW HANDOFF — ACCEPTED WITHOUT REWORK.**

This checkpoint correctly prepares the human review required by Review 116 without fabricating any human adjudication result.

**Actual human reviews remain 0/10.**

Therefore the nine AI-assisted rejection proposals from Document 115 are still not final scientific lineage clearances.

## 1. The handoff preserves the AI ledger

The accepted AI proposal records are preserved unchanged.

The human-review interface does not overwrite or silently promote:

- 9 AI `rejected_false_positive` proposals;
- 1 AI `uncertain_insufficient_evidence` proposal.

The human ledger is separate.

This is the correct provenance design.

## 2. No human answer is prefilled

The ten review records are prepared with blank human disposition and rationale fields.

The tool does not treat:

- opening a page;
- loading an image;
- the prior AI answer;
- metadata labels;
- role differences

as a human adjudication.

This is essential.

## 3. Exact same ten pairs are retained

The handoff covers the same frozen first ten queue entries from batch 01.

No candidate is replaced based on:

- AI outcome;
- apparent ambiguity;
- screening distance;
- reviewer convenience.

The next 75 high-risk candidates are not started.

This avoids outcome-dependent queue progression.

## 4. Evidence is cryptographically bound

The human-review definition binds:

- the accepted AI ledger;
- accepted packet hashes;
- Review 116;
- implementation hashes;
- all relevant frozen artifacts;
- copied and newly generated image hashes.

Import validates those bindings before accepting a human record.

This provides a good chain of evidence from pinned media through AI review to human adjudication.

## 5. Additional evidence for the uncertain pair is appropriate

For the one AI-uncertain pair, the handoff adds:

- 34 private full-resolution PNGs;
- 17 fixed temporal positions per video;
- both trigger frames;
- 1080 × 1920 resolution.

These images are tied back to accepted payload/frame identities.

This is a sensible attempt to improve adjudication evidence without changing the screening rule or selector.

## 6. The added evidence still does not constitute full-video visual inspection

The document correctly states that:

- the 34 frames are sparse temporal samples;
- continuous video is not fully visually reviewed;
- no absence-of-shared-source claim follows automatically.

This limitation must remain explicit.

## 7. Human attestation is handled conservatively

The import layer requires an explicit reviewer identity/type, rationale, timestamp and personal-inspection attestation.

However, Document 117 correctly states that these are attestations rather than cryptographic proof of human authorship.

A forged declaration would still pass schema-level structure if its fields were fabricated.

This is an acceptable documented boundary for this project, but it should not later be described as authenticated independent review.

## 8. Disagreement handling is correct

If human and AI dispositions differ:

- both are preserved;
- a disagreement flag is retained;
- effective disposition remains uncertain until reconciliation.

This is a strong methodological choice.

The human review does not automatically override prior evidence simply because it is human-labelled.

## 9. Confirmed cross-role content still triggers a stop

If any human reviewer confirms same/derived rendered content across roles, the workflow requires:

- stop before model execution;
- explicit prospective scientific decision;
- no automatic deletion;
- no role reassignment;
- no selector/seed modification;
- no queue continuation as if nothing happened.

This remains consistent with the frozen-study constraints.

## 10. Import is fail-closed

The preparation/import workflow rejects:

- incomplete human records;
- unbound records;
- attempts to treat AI as human;
- unsafe output roots;
- existing outputs;
- mismatched packet/image hashes.

No review output is created for an incomplete record.

That behavior is appropriate.

## 11. Reproducibility evidence passes

The handoff reports:

- 67 private export files;
- original/rerun byte-identical;
- rerun actually rereads/redecodes source media;
- temporary AVI count returns to zero.

The previous AI ledger and all 13 frozen artifacts remain unchanged.

## 12. Tests and CI pass

Reported tests:

- focused: **52/52**;
- full regression: **239/239**;
- zero failures/errors.

Fresh GitHub Actions on exact commit:

`41264039919a844e7c3bd6553348c64405eb4f75`

completed successfully.

## 13. Browser usability is not verified

The one operational limitation is explicit:

`browser_UI_verified = false`

The integrated browser could not access the private external folder and returned 403; no local browser/Node runtime was available in the research environment.

This does **not** invalidate the scientific handoff definition or evidence bindings.

However, before relying on the owner export, the human reviewer should verify that the generated page works correctly in a normal local browser.

If UI behavior is broken, fix the presentation/import tooling prospectively without altering existing evidence or human answers.

## 14. Current scientific status remains unchanged

At this checkpoint:

- actual human reviews: **0/10**;
- AI proposals scientifically cleared: **false**;
- content-lineage adjudication complete: **false**;
- highest-risk pairs still remaining before further review: **75**;
- model execution authorized: **false**;
- scientific readiness: **false**.

This is correct.

## Required next action

The owner or designated human reviewer must now inspect all ten bound pair packets and submit one complete human-review JSON.

For each pair, record:

- human disposition;
- rationale;
- reviewer identity/type;
- inspection attestation;
- timestamp.

Use `uncertain_insufficient_evidence` whenever the available evidence does not justify a stronger disposition.

After import:

1. compare human vs AI dispositions;
2. preserve disagreements;
3. stop if any cross-role pair is confirmed same/derived content;
4. do not continue to the remaining 75 high-risk pairs until batch 01 has an accepted/reconciled disposition state.

## Final disposition

**DOCUMENT 117 — ACCEPTED.**

**CHECKPOINT 1.5I BOUND HUMAN-REVIEW HANDOFF — ACCEPTED WITHOUT REWORK.**

The project has correctly prepared the second-review mechanism but has not yet performed the second review.

**Human adjudication remains the next required input; 9 AI rejection proposals remain non-final, and the one uncertain pair remains unresolved.**
