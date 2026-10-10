# Response to Review 116: Bound Human-Review Handoff

Date: 2026-10-10
Base commit: `d079c90`
Review: [Document 116](116-review-doc115-oulu-visual-batch01.md)

Review 116 accepts checkpoint 1.5H as AI-assisted evidence/proposals, not final
scientific clearance. This checkpoint **1.5I prepares the required owner/human
review of batch 01**. It does not manufacture a second reviewer, adjudicate the
ten pairs or continue the remaining 75 highest-risk candidates.

## Completion Criteria and Results

| Preparation criterion | Actual result |
| --- | --- |
| Preserve accepted AI ledger, packets, policy and implementation | Existing hashes verified; originals not rewritten |
| Keep exact first ten queue ranks, without prefilling human answers | Ten pairs prepared; human disposition and rationale blank |
| Add higher-detail temporal evidence for the uncertain pair | 34 private 1080x1920 PNGs: 17 fixed ranks per video, including both trigger frames |
| Bind extra evidence to accepted payloads and full-resolution RGB | Archive identity/pins, payload SHA-256, decoded RGB and saved-PNG RGB verified |
| Reproduce evidence through actual reread/redecode | Original/rerun: 67 byte-identical files each |
| Reject incomplete, AI-as-human or unbound records | Negative synthetic tests pass; incomplete record creates no review output |
| Preserve disagreements; never authorize models automatically | Separate human ledger; reconciliation required on disagreement; confirmed cross-role stops for explicit scientific decision |
| Keep all 13 frozen artifacts and scientific gates unchanged | Schema passes; four later stages remain blocked |
| Verify browser interaction/layout | **Not completed**: private-folder access refused by integrated browser (403); no local browser/Node runtime in `fas` |

Focused regression: **52/52**. Full regression: **239/239**, zero failures/errors
(34.445 seconds). No new local package or environment was installed. Temporary
AVIs are removed. No research detector/model, training or target evaluation ran.
Preparation is complete as a bound evidence handoff; browser usability and the
actual human review remain unverified/uncompleted, respectively.

## Separate Evidence and Human Ledger

[Human-review primitives](../src/fas/human_review.py) verify explicit human
attestations against the exact review definition, all ten unique pair ranks,
packet hashes, required image hashes, nonblank rationale and UTC timestamp.
The uncertain pair cannot omit the new full-resolution evidence binding.

[Preparation/import runner](../scripts/prepare_oulu_owner_review.py) writes a
private static HTML page, an immutable definition and a preparation summary.
The page has pair navigation, the original two panels and trigger, enlarged
full-resolution evidence, image zoom, reviewer identity/type, separate human
disposition/rationale, personal-inspection attestation and JSON export. Earlier
AI proposals are separately labeled and collapsed initially. No human decision
is prefilled, and merely viewing/loading an image is **not** a human review.

The definition binds the accepted AI records, packets, review 116, implementation,
frozen artifacts and every copied/new image. Import verifies its hash against the
[public aggregate](../results/phase1/oulu-human-review-handoff-v1.json), rechecks
the private image/AI-record hashes, validates the supplied human record and
creates a **new** immutable ledger. Existing outputs or destinations inside the
repository or protected evidence roots are refused. Private images, identities,
AI observations and human rationales are not committed to Git.

The timestamp/identity are reviewer attestations, not independent authentication
of human authorship or inter-rater reliability. A forged declaration cannot be
made trustworthy merely by a schema validator. Synthetic test reviewers never
count as actual dataset reviewers.

On differing AI/human dispositions, both values and an explicit disagreement
flag are retained; effective disposition remains uncertain until reconciliation.
Any human same/derived-content confirmation triggers a prospective scientific
decision stop, even when it disagrees with the AI rejection proposal. No
automatic sample exclusion, role reassignment, selector/seed change or queue
continuation occurs. Any visual rejection remains scoped to the observed
rendered-content screening relationship, not original capture independence.

## Private Handoff and Owner Action

Open the generated static page in a normal local browser:

```text
/mnt/e/FAS-private/artifacts/phase1/oulu_owner_review_batch01_v1/index.html
```

On the host Windows drive corresponding to this WSL mount, the same file is:

```text
E:\FAS-private\artifacts\phase1\oulu_owner_review_batch01_v1\index.html
```

No dev server is needed. The integrated VS Code browser refused this external
private folder; that limitation was not bypassed by moving biometrics into Git
or exposing a public server. Desktop/mobile screenshots, browser interaction
and rendered JavaScript runtime remain unverified. The owner should report a
UI failure before relying on an export. Pair answers persist while navigating
the page, but are not persisted across a browser reload.

The owner or designated **human** reviewer must inspect all ten bound packets,
including the full-resolution evidence of **Pair 5 / queue rank 4**, and enter
their own disposition/rationale. Choose `uncertain_insufficient_evidence` when
detail or temporal sampling is insufficient. A hash match, different labels,
different roles or the earlier AI answer does not by itself settle lineage.
Click **Export Human Review** only after actual inspection and ten completed
entries. Provide the resulting JSON path for validation/import; no human record
has been submitted or imported by this checkpoint.

Import command after the actual reviewer supplies their JSON:

```bash
conda run --no-capture-output -n fas python scripts/prepare_oulu_owner_review.py import \
  --review-root /mnt/e/FAS-private/artifacts/phase1/oulu_owner_review_batch01_v1 \
  --human-input /absolute/path/to/oulu-batch01-human-review.json \
  --out-root /mnt/e/FAS-private/artifacts/phase1/oulu_human_dispositions_batch01_v1
```

The output root must not exist. Original all-frame thumbnails remain available
in the accepted private packet root if the reviewer needs additional temporal
inspection. The 34 new full-resolution frames are sparse samples, **not** a full
continuous-video review and not proof that every possible shared region/source
relationship is absent.

## Bindings and Stop Point

- Review definition SHA-256: `45a89ba93ffa380d502dc7c240dbe8f95f4e6c7e82c970442080aab9dde85bf6`.
- HTML SHA-256: `94a3029de3aa8cf954b22d9f0342727f99418f5c4d0bfc6cb73fcca50ba3d46a`.
- Accepted AI summary SHA-256 remains `da03065a14026ed12179293d4537723046ca7a5afb080effb933814e0513a6f0`.
- Frozen registry remains `dcb6860522c04bc1a69d7c5a4b62809a7c046ee57e25132b6988b131e59a4e8f`.

**Actual human reviews: 0/10.** Nine AI rejection proposals are still not final
scientific lineage clearances. The uncertain pair is not closed by generating
higher-resolution PNGs alone. The remaining queue is unchanged and not advanced.

Required input to resume: genuine bound human dispositions for all ten pairs,
with any disagreement/uncertainty preserved. Import is an evidence checkpoint,
not execution authorization. A confirmed cross-role relationship must first be
handled by an explicit prospective scientific decision; uncertainty or unresolved
disagreement requires further evidence/reconciliation before scientific clearance.
The owner must review this published checkpoint before any next batch. All
data-audit/source-dry-run/analysis-freeze/locked-evaluation gates stay blocked.