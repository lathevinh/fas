# 297 - First source-fold features and genuine source-only OOF fitting

Date: 2026-10-26.
Governing review: [296](296-review-doc295-source-integration-and-encoder-pilot.md).

## Result

**The approved first outer-source fold completed: full1906-image feature
coverage for all three encoders,14 actual DINO head fits,21 actual affine
calibrators and24 actual source-OOF logistic risk fits. Saved model, feature,
threshold, label and prediction reconstruction passed. This is genuine source
fitting, but not a completed scientific source-dry-run or target evaluation.**

Public evidence:

- [Sealed execution plan](../results/phase1/source-plan297-v1.json).
- [Actual execution and source diagnostics](../results/phase1/source-run297-v1.json).
- [Additive saved-output closure](../results/phase1/source-closure297-v1.json).

## Scope and immutable boundary

Review296 accepts295 without rework. This package advances from the accepted
technical pilot to full fold-local feature coverage and actual fitted source
predictions. It does not repeat dataset acceptance, source-video decoding,
SCRFD inference or the two-pass24-image pilot.

The first outer target is OULU-NPU; its images and predictions are entirely
outside this package. The sources are CASIA-FASD, MSU-MFSD and the adopted SiW
source-use population. Only seed20260917 is included. No result here represents
all four target rotations and all three registered seeds.

| Source | Original source-use denominator | Successful feature inputs | Retained failures |
|---|---:|---:|---:|
|CASIA-FASD|600|594|6|
|MSU-MFSD|280|272|8|
|SiW-Mv2|1052|1040|12|
|Total|1932|1906|26|

| Permanent role | Original denominator | Successful images | Retained failures |
|---|---:|---:|---:|
|train|1156|1135|21|
|branch_calibration|391|389|2|
|g_domain|385|382|3|

These are fold-local source counts, not the7510-original archive or the
6855-image union across rotations. The27th union source failure belongs to the
excluded OULU dataset. SiW's623 official-test originals and five adopted
exclusions remain source-ineligible. All accepted archive/role/summary receipts
are preserved. Failure rows retain terminal non-accept and original
denominators; no image, feature, classifier score or error label is fabricated.

## Executable package and fresh combined authority

The [controller](../scripts/run_source297.py),
[cache contracts](../src/fas/feature_cache.py),
[source-fitting implementation](../src/fas/source_fitting.py) and
[fixed execution configuration](../configs/source_run297_v1.yaml) were
implemented and tested before permission to execute on actual images.
The [sealed plan receipt](../results/phase1/source-plan297-v1.json) binds exact
code, config, runtime, group splits, crop/checkpoint identities and source-use
binding. Private original/sample IDs are not published.

The owner explicitly selected
`approve_source297_full_features_and_source_fitting`.
This is new combined extraction/fitting authority, not reuse of the completed
pilot295 permission. Its original clock is1793001701.1905353 Unix seconds:
110-minute work cutoff and120-minute final deadline,8GiB combined process-tree
RSS,12GiB CUDA allocated/reserved and2GiB owned new+temporary artifacts.
The existing1,291,302,227 checkpoint bytes are reused by exact digest and
are not new allocations on disk. No download, installation, model substitution,
automatic retry or budget extension is authorized.

Preflight hashed48 existing crop files from24 evenly spaced identity-sorted
source rows:8,658,378 bytes in1.3725s, without decoding pixels or calling a
model. The linear three-encoder-plus-quality IO projection is218.0s, not a
wall-time guarantee. The fixed plan allows30 minutes for IO and30 minutes for
fitting/readback inside its hard caps. The source manifest SHA remains
`7f9f54e6b097d7da0618cf8b3784e9eb3726b6aba8a3957455e26dda20da4580`;
the exact first-fold input/split SHA is
`35969a893bb64d8f4015c580e742778d05eaad58408f1d45f7c659f1dda05a5c`.

## Cache, reuse and interruption semantics

Frozen encoders run sequentially, batch1 FP32, TF32/mixed precision disabled,
deterministic PyTorch operations. The cached checkpoints, pinned DINO checkout,
strict local weights-only loading, native224/518 normalization and patch-only
pooling are unchanged from295. No remote model code is fetched.

Each new crop read verifies saved SHA256, RGB mode and native dimensions.
Each model uses deterministic32-original shards. A shard includes its ordered
unique provenance keys and finite FP32 matrix; exact saved readback precedes
atomic no-overwrite publication and directory fsync. Complete coverage,
one-to-one sample/key joins and SHA verification are required before fitting.
Successful shards survive interruption. An interrupted atomic publication
does not invalidate earlier shards or require their inference again.

Keys bind original identity, crop, checkpoint, active preprocessing,
representation and dtype, plus the full normalization/resolution/runtime/
precision/pooling/controller contract. Labels do not enter cache keys.
The explicit295 compatibility adapter verifies the accepted worker, original
pilot code/config, exact sample keys, normalization, checkpoint and shard bytes
before importing its24 features per model into the stronger cache contract.
The eight fixed prompt embeddings are hash-verified and reused; no new text
inference or prompt selection is needed.

No blanket repeated extraction is performed. Resuming after a failure requires
a separate explicit immutable resume authorization bound to the failed terminal
and original approval; it cannot reset the original deadline. Completed
extraction/quality/fit checkpoints are verified and reused. A corrupt or
incompatible cache is an explicit error, not a silent cache miss or replacement.

## Actual fitting rules, not synthetic evidence

There are seven fitting contexts: final source model, three complete
domain-OOF exclusions and three matched sample-OOF folds. The latter uses
subject/video-safe groups within each domain and class-signature stratum.
Exact selected-frame duplicates are unioned with original groups before any
sample or inner split, so the retained within-role duplicate cannot be split
between fitting and held-out predictions.

Both OOF strategies predict the identical1524 successful source-train plus
branch-calibration originals exactly once. G_domain's382 images never enter
head fitting, inner validation, calibration, OOF records, quality statistics or
risk fitting. In domain-OOF, the entire pseudo-target dataset is absent from
all fitted/selection/calibration partitions. In matched sample-OOF, complete
held-out groups are absent from those same partitions.

Within each allowed remainder:

- Train-role groups alone derive a deterministic one-in-five inner validation
  split, serialized per context. The remaining train groups fit two linear
  logistic heads on frozen DINO-Reg/plain features.
- A fixed200-epoch full-batch float64 AdamW budget uses learning rate0.001,
  weight decay0.05 on weights only, fixed seed and equal-domain/class-balanced
  BCE. Only the lowest corresponding inner-validation BCE selects a checkpoint;
  exact ties retain the earlier epoch. There is no refit using validation.
- Registered monotone affine calibration fits once per branch on the disjoint
  branch-calibration role, with positive softplus(theta)+1e-6 slope and
  equal-domain/class-balanced BCE. OpenCLIP has no learned image/text head:
  its raw logit remains mean-spoof minus mean-live cosine over the frozen bank.
- Each branch/complete system chooses its own attack-high reference threshold
  on that context's calibration remainder, maximizing the threshold subject
  to empirical APCER<=5% in every source domain. Ties predict attack.
  Selection conservatively uses successful calibration images only; failures
  remain explicitly reported original non-accepts, never invented scores.
  This is a nominal source rule, not a certified security bound.
- Held-out source predictions serialize actual calibrated probabilities,
  source-selected thresholds, binary correctness/error events and exact fitted
  checkpoint hashes. The two complete pairs share the same fitted DINO anchor,
  never retraining it by pair.

The fixed quality vector is native224-crop Laplacian variance, grayscale mean
and population standard deviation, saved detector face-area/original-frame
ratio and saved detector confidence. Crop and raw detector-transaction hashes
bind each value. Quality computation does not rerun detection. Statistics come
only from the final head-fitting pool and are identical across both OOF
strategies; probabilities/disagreement are never standardized. Constant quality
dimensions, if present, are disclosed and use scale1.

Risk fitting uses the six registered feature variants, natural class prevalence
within each domain, equal domain weighting, L2 C=1 with unpenalized intercept,
and one fixed float64 L-BFGS-B budget. Both error and correct counts must be at
least20; otherwise that system/strategy is explicitly not applicable and no
degenerate or placeholder fit is created. Predictions on untouched G_domain
are diagnostics only: no gate is selected and no calibrated deployment-risk
probability claim is made.

## Executed feature and model evidence

| Encoder | Complete saved FP32 coverage | New image forwards | Reused295 rows | Extraction seconds | Final CUDA peak allocated / reserved bytes |
|---|---|---:|---:|---:|---:|
|DINOv2-Reg|1906 x1536|1882|24|119.03|430709760 /488636416|
|DINOv2 plain|1906 x1536|1882|24|54.15|430602240 /488636416|
|OpenCLIP|1906 x512|1882|24|95.75|642748416 /704643072|

Exactly5646 new image forwards and72 reused feature rows cover all5718
original/model joins, with27,324,416 feature payload bytes. There are no new
text forwards, repeated full passes or checkpoint downloads. Final allocator
peaks are persisted after each encoder's entire work; text is reused rather
than omitted from a newly executed peak scope.

The terminal completed418.31s after the original approval. Additive saved-output
closure completed442.04s after approval. Sampled combined peak RSS was
2,418,397,184 bytes; peak owned new+temporary storage was44,819,878 bytes.
All were below the original caps. No retry or resume occurred. No encoder
process remained on the GPU afterward.

The additive [closure command](../scripts/close_source297.py), which does not
change the pinned executed worker, verified every saved feature shard and
complete sample/runtime key. It reconstructed14 selected head checkpoints,
21 calibrators and their source-selected threshold policies,3430 source
prediction rows (1524 per OOF strategy plus382 G_domain), actual error labels
and all24 risk models' saved G_domain predictions. This made zero encoder or
optimization calls. Checks used saved features, model coefficients, exact
split IDs and frozen source labels; they were not a second extraction run.

| Fitting context | Head fit | Inner validation | Branch calibration | Selected epoch Reg /plain |
|---|---:|---:|---:|---:|
|Final source|899|236|389|200 /200|
|Domain-OOF excludes CASIA|616|164|270|200 /200|
|Domain-OOF excludes MSU|775|197|333|200 /200|
|Domain-OOF excludes SiW|407|111|175|200 /103|
|Matched sample fold0|608|168|224|137 /59|
|Matched sample fold1|585|155|285|200 /174|
|Matched sample fold2|599|155|269|200 /200|

Fit sizes differ materially across complete-domain exclusions and matched
sample folds. No budget-matched sensitivity was executed under this first
package. Both strategy risk fits retain the same1524-original candidate
universe and their natural source error prevalence, not an error-balanced
replacement set.

### Source diagnostics, including unfavorable results

These are point estimates from held-out source predictions. Balanced accuracy
uses each fold's independently source-selected threshold, never a threshold
fitted on that held-out pseudo-domain. AUROC and balanced accuracy are
equal-domain means. No bootstrap LCB or competence pass is claimed.

| System | Domain-OOF macro AUROC /BA | Domain-OOF errors | Matched sample macro AUROC /BA | Matched sample errors |
|---|---:|---:|---:|---:|
|DINO-Reg|0.925129 /0.740563|347|0.986548 /0.870852|162|
|OpenCLIP|0.578760 /0.506145|616|0.560270 /0.508997|605|
|Heterogeneous average|0.891155 /0.759575|343|0.986606 /0.904754|136|
|Same-family average|0.945292 /0.806826|277|0.987641 /0.883827|154|

OpenCLIP's standalone balanced accuracy is below the frozen0.55 competence
point requirement in both strategies. Do not call it a competent standalone
PAD branch. This does not by itself invalidate the complete-pair claim
dependencies; those still need their actual clustered uncertainty and complete
fold/seed evidence. No negative source result triggered tuning or replacement.

For the registered primary risk vector R_DVd, all four system/strategy
combinations have sufficient source-OOF fitting events:

| System | Strategy | OOF error /correct | G_domain errors /382 | G_domain error AP | Brier /NLL |
|---|---|---:|---:|---:|---:|
|Heterogeneous|domain-OOF|343 /1181|27|0.316771|0.070133 /0.250401|
|Heterogeneous|matched sample-OOF|136 /1388|27|0.621164|0.044058 /0.156559|
|Same-family|domain-OOF|277 /1247|15|0.395060|0.047675 /0.193127|
|Same-family|matched sample-OOF|154 /1370|15|0.565616|0.030594 /0.136347|

**This first held-out G_domain diagnostic does not favor domain-OOF: matched
sample-OOF has higher primary-vector error AP for both systems.** The same
final fitted classifier/error set is used across risk strategies within each
system. These are not target results, paired uncertainty estimates or a primary
RQ1 verdict. The same-family G_domain has only15 errors; support is explicitly
small. G_domain diagnostics did not select a model, feature variant, gate,
threshold or optimizer change. Brier/NLL are reported measurements, not proof
of calibrated deployment probabilities.

## Scientific limits and normal gates

This first fold/seed does not satisfy the normal twelve-fold/seed
competence/applicability contract. No partial metric is installed as a complete
artifact, no missing bootstrap lower bound is replaced by a point estimate,
and no placeholder evidence promotes readiness.

Still required are the other outer rotations/seeds; clustered source
competence lower bounds and claim-specific applicability; branch-fit-size
budget-matched sensitivity where sizes differ materially; the registered
without-quality attribution and domain-identifiability/OOF-to-final drift
diagnostics; and the complete source evidence/gate-policy bundle.
The matched sample comparison holds candidate universe, optimizer epochs,
feature definitions and risk objectives fixed, but does not claim that
effective branch-fit sample counts are equal. Any apparent gain concerns the
complete OOF construction, not a causal effect of domain holdout alone.

All public source diagnostics are source-only, not OULU performance or evidence
for RQ1/RQ2. Target access/tuning and locked evaluation remain forbidden.

The actual normal validator returned:

| Stage | Actual result |
|---|---|
|schema|No errors|
|data-audit, with accepted frozen/adopted-use roots|No errors|
|source-dry-run|`missing source-dry-run evidence`|
|analysis-freeze|Above plus `missing immutable analysis-freeze record`|
|locked-evaluation|Above plus `locked-evaluation remains blocked until typed authorization exists`|

These are actual existing validator results, not a new relaxed readiness
definition. Both accepted summary SHA256 values are unchanged. No incomplete
competence/applicability artifact was placed at the validator's authoritative
paths. Scientific readiness remains false.

## Validation

The combined focused suite passed91 tests, including actual synthetic
head/calibrator/risk optimization, complete controller OOF joins, permanent gate
isolation, completed-fit resume without retraining, shard atomicity/readback,
source-use contracts and existing scientific gates. This count is testing
evidence, not actual source model execution. All five new Python files compile.
The Pylance MCP endpoint failed initialization, so editor diagnostic/type-check
success is not claimed. Exact-head public CI is collected after publication.
