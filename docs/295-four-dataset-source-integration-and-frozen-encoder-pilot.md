# 295 - Four-dataset source integration and authorized frozen-encoder pilot

Date: 2026-10-26.
Governing review: [294](294-review-doc293-siw-closure-and-four-dataset-handoff.md).

## Result and boundary

**The four accepted prepared datasets are now joined into one versioned
source-stage handoff. Model-free fold/role consumers pass. A separately,
explicitly authorized24-image frozen-encoder pilot also passes. This is not
classifier fitting, a completed scientific source-dry-run, full feature
extraction or target evaluation.**

Review294 accepts the four data milestones without rework. This package does
not reopen their acceptance, repeat video/detector campaigns or inspect sheets
again. Both archived summary files remain byte-identical to accepted293.
The SiW source-use amendment, five exclusions and historical duplicate findings
are unchanged. Participant identity and scientific readiness are not promoted.

Public evidence:

- [Integration receipt](../results/phase1/source-integration295-v1.json).
- [Concrete approved pilot plan](../configs/source_pilot295_v1.yaml).
- [Executed encoder-pilot receipt](../results/phase1/source-encoder-pilot295-v1.json).
- [Final source-stage handoff](../results/phase1/source-handoff295-v1.json).

## Prepared-image and permanent-role join

The [integration command](../scripts/integrate_source295.py) joins each accepted
full-image manifest to unchanged canonical IDs, labels, official partitions,
group identities and permanent role CSVs. Accepted readback/manifest hashes
anchor provenance. Raw prepared transactions are hash-joined; existing asset
paths are checked without opening/redecoding pixels. Original selected
earlier-middle-frame commitments are retained. No model score or classifier
error is invented.

The OULU historical image schema legitimately omitted `classifier_error`.
The adapter explicitly permits that omission only for reused records with its
exact accepted historical recipe hash and an absent model score; modern records
still require the field. This fixes a concrete integration mismatch, not an
image-policy change. OULU's one pre-detector failure remains bound to its
accepted plan terminal rather than an invented successful transaction.

SiW uses the actual adopted context and exact policy/overlay/effective-manifest
binding. Source-eligible transactions pass its existing hash-bound consumer
routes. All623 null-role test originals and five source exclusions remain in
archive accounting but cannot enter source consumers.

| Dataset | Archived originals | Source-use originals | Valid model-image inputs | Retained source-use failures | Actual scored-fit rows |
|---|---:|---:|---:|---:|---:|
|OULU-NPU|4950|4950|4949|1|0|
|MSU-MFSD|280|280|272|8|0|
|CASIA-FASD|600|600|594|6|0|
|SiW-Mv2|1680|1052|1040|12|0|
|Total|7510|6882|6855|27|0|

The archived population has nine pre-detector and22 detector failures. Four of
the latter are SiW test failures; source-use failures are therefore27, not31.
Five excluded successful SiW originals remain archival successes, not failures.
Successful crops are eligible model inputs, **not** scored-fit rows while
classifier scores remain absent.

| Permanent source role | Archived originals | Effective source-use denominator | Valid model-image inputs |
|---|---:|---:|---:|
|train|4130|4126|4105|
|branch_calibration|1381|1381|1378|
|g_domain|1376|1375|1372|

Archived role totals exclude the623 null-role SiW test originals. Original
official partitions are not reinterpreted as universal source prohibitions:
CASIA/MSU/OULU use their accepted frozen source policy, while SiW test remains
strictly preparation-only. A dataset acting as the outer target is excluded
in its entirety, regardless of its official partition.

The [source-stage contracts](../src/fas/source_stage.py) provide fold-local
fitting/calibration/domain-use views with separate failure-inclusive
denominators and successful-image inputs. All four outer-domain rotations,
all role routes and12 domain-OOF fitting exclusions were exercised on the
actual integrated rows. Outer targets, complete pseudo-target datasets,
wrong-role rows and source-ineligible originals are rejected. These are
model-free population checks, not fitted OOF predictions or competence evidence.
Downstream consumers must use the sealed handoff and exact SiW binding, not
arbitrary unverified row dictionaries or archived CSV counts alone.

Private source-manifest SHA256:
`7f9f54e6b097d7da0618cf8b3784e9eb3726b6aba8a3957455e26dda20da4580`.
Integration took422.31s, dominated by private saved-record/path IO; it did not
decode source video or images. No new dataset-audit inference is claimed.

## Concrete pilot and fresh authority

Before model acquisition/execution, the owner received and explicitly approved
one complete package:
`approve_source295_checkpoint_and_frozen_encoder_pilot`.
The approval binds the exact plan bytes and review294, with one non-resettable
90-minute clock, an80-minute work cutoff,8GiB process-tree RSS,12GiB PyTorch
CUDA allocated/reserved memory and8GiB owned new+temporary artifacts.
No automatic retry, replacement checkpoint, installation or deadline extension
is permitted. Earlier image-campaign authorities were not reused for models.

Inputs were sealed before approval:24 existing successful train-role crops,
eight each from CASIA/MSU/SiW, four per binary class, deterministic SHA256 rank.
OULU is the sole pilot outer target and is completely excluded; calibration,
g_domain, SiW test/exclusions and failed images are not pilot inputs.
Labels stratify this fixed IO sample but never enter feature cache keys,
checkpoint selection or an optimization objective.

Private pilot-input SHA256:
`07f110e9a32f7b5da98334a5cba913ea2a5b16f6c4bcee24e4c3ac0dce85ac7f`.

Actual preflight: locked environment checker READY, Python3.12.14,
PyTorch2.7.1+cu126, OpenCLIP3.0.0, CUDA available on RTX4080SUPER.
The pinned DINO source checkout is clean at
`7764ea0f912e53c92e82eb78a2a1631e92725fc8`.
The registered checkpoints were absent from the scoped standard/FAS caches;
an unrelated small DINO checkpoint was not substituted.

Exactly1,291,302,227 bytes of registered weights were acquired once from the
official endpoints named in the plan. DINO byte sizes and EOF were verified;
their computed SHA256 values are local acquired-byte identities, not falsely
claimed upstream published digests. OpenCLIP additionally matches its upstream
LFS SHA at pinned revision `7288da5a0d6f0b51c4a2b27c624837a9236d0112`.

| Frozen checkpoint | Bytes | Actual SHA256 |
|---|---:|---|
|DINOv2 ViT-B/14-Reg4|346393545|`73182a088cf94833c94b1666d1c99e02fe87e2007bff57b564fb6206e25dba71`|
|DINOv2 ViT-B/14|346378731|`0b8b82f85de91b424aded121c7e1dcc2b7bc6d0adeea651bf73a13307fad8c73`|
|OpenCLIP ViT-B-16 / laion2b_s34b_b88k|598529951|`1f16b1274ca25493b1f36225efe81d05f66a3f33c487acd1a07c5ba87920de6f`|

The registered Reg4 name maps explicitly to the pinned upstream factory
`dinov2_vitb14_reg`, which creates four register tokens. This is an API-name
adapter, not a different backbone. Models load strict local state dictionaries
with `weights_only=True`; no remote model code or installation runs.

## Actual frozen-encoder execution

The [single-run controller](../scripts/pilot_source295.py) runs encoders
sequentially, batch1, FP32, deterministic operations, TF32/mixed precision off.
A supervisor enforces original deadlines, combined worker/supervisor RSS and
owned storage; PyTorch's process memory fraction bounds its allocator.
The first acquisition/model/cap/parity failure terminates without retry.

Each existing RGB crop is SHA-verified and loaded at its native224/518 size.
No new resize, alignment, frame selection or detector runs. DINO uses official
normalization, concatenating768 CLS features and the768-dimensional mean of
patch-only normalized tokens; register tokens do not enter the mean. OpenCLIP
uses registered checkpoint-native normalization and normalized512-dimensional
image embeddings. The [feature contracts](../src/fas/frozen_features.py) enforce
shape, finite FP32, label-free cache provenance and numeric parity.

| Encoder | Saved shape | Payload bytes | Two-pass maximum absolute difference | Median image-forward time |
|---|---|---:|---:|---:|
|DINOv2-Reg4|24 x1536|147456|0.0|17.13ms|
|Plain DINOv2|24 x1536|147456|0.0|16.69ms|
|OpenCLIP|24 x512|49152|0.0|4.71ms|

All144 image forwards and two fixed-prompt text forwards completed.
Predeclared repeat tolerance was rtol1e-5/atol1e-6; no tolerance was changed
after observing outputs. Three immutable NumPy feature shards passed exact
saved-array readback and one-to-one sample/cache-key joins.
The frozen eight core prompts produce mean-spoof-cosine minus mean-live-cosine
logits, without calibration, threshold selection or performance measurement.
Saved text features/logits also pass readback and model-free reconstruction.
No claim of accuracy, competence, error prevalence or model comparison follows.

Original approval through pilot terminal:245.99s (4m05.99s).
Through additive source closure:397.83s (6m37.83s), below5400s.
Sampled peak combined RSS2,206,892,032 bytes; owned new+temporary
storage1,291,715,120 bytes at terminal, both below caps.
Persisted GPU peaks cover the image passes: maximum reserved704,643,072 bytes.
Text-pass allocator peaks were checked against12GiB but their final numeric
peak was not separately persisted; the receipt does not claim otherwise.
The pilot exited successfully and the WSL GPU process list was empty afterward.

The small-source timing projects about307.81s of forward-only work and
98,273,280 bytes of FP32 feature payload for6855 successful source inputs.
This excludes full input/hash/PNG IO, startup, text, sharding and fold logic:
it is **not** a full-wall-time guarantee or authority for full extraction.
The preapproval30-minute planning estimate was explicitly unmeasured, not a
reported benchmark. Reusable acquired weights/features remain private.

## Existing stage gates and next implementation boundary

The [closure checker](../scripts/close_source295.py) validates executed source
hashes, input identity, acquired weights, all pilot shards/crop hashes, cache-key
joins and fixed-prompt reconstruction without more model calls. Actual normal
validator results with both private frozen and adopted-use roots:

| Stage | Actual errors |
|---|---|
|schema|none|
|data-audit|none|
|source-dry-run|missing source-dry-run evidence|
|analysis-freeze|missing source-dry-run evidence; missing immutable analysis-freeze record|
|locked-evaluation|the preceding two; locked-evaluation remains blocked until typed authorization exists|

No placeholder competence/applicability artifacts are written to satisfy these
gates. The technical pilot does not fit the DINO linear heads, monotone affine
calibrators or risk models required by the existing
[source recipe](../configs/source_recipe_v2.yaml). It does not construct genuine
OOF error labels, measure branch competence or unlock an analysis freeze.
No target prediction is authorized. Full extraction and source fitting require
their next concrete implemented package and applicable authority; the completed
data milestones must not be re-certified as a substitute for that work.

Validation:37 focused source/feature/SiW/legacy-transaction tests passed in3.279s;
all new Python compiled and whitespace checks passed. Tests cover unchanged
failure denominators, exact native crops, role/outer/pseudo-target exclusions,
SiW context/null-test handling, deterministic label-free cache lineage,
CLS/patch-only pooling, finite/shape/parity thresholds, acquisition EOF/SHA,
combined storage/deadline caps and explicit no-retry failed terminals.
Pylance editor diagnostics were unavailable because its local MCP endpoint
failed initialization; no successful editor type-check is claimed.
Exact published-head CI is collected after publication, not invented inside
the immutable prepublication handoff receipt.

No data-summary/accepted-image receipt is changed, and no video/detector job,
full extraction, classifier/calibration/risk fit or target evaluation is running.
