# 296 - Review of295: source integration and frozen-encoder pilot

Date: 2026-10-26
Reviewed commit: `3cf01c6f1f5fcb79ddfe314e39b8b389653a44db`
Governing review: [294](294-review-doc293-siw-closure-and-four-dataset-handoff.md).

## Decision

**DOCUMENT295 ACCEPTED WITHOUT REWORK for four-dataset integration, model-free fold/role routing and the authorized24-image frozen-encoder pilot. These technical milestones are complete. Proceed to implemented full source-feature extraction and genuine source fitting/OOF evidence; do not repeat dataset acceptance or the same technical pilot.**

This accepts a successful technical execution, not a completed scientific source-dry-run, trained classifier, calibrated risk estimator or target evaluation. All four data milestones remain closed. The report correctly keeps scientific_source_dry_run_complete=false, classifier/calibrator/risk fits zero and scientific readiness false.

## Verification and limits

Reviewed report295, three public integration/pilot/handoff receipts, approved pilot configuration, integration/encoder/closure controllers, source-stage and frozen-feature contracts and their tests. Exact-head GitHub [run40287461101](https://github.com/lathevinh/fas/actions/runs/40287461101), [validate121454401672](https://github.com/lathevinh/fas/actions/runs/40287461101/job/121454401672) has success conclusions for all12 listed steps, including Complete job. This closes the final-CI collection item in the immutable prepublication handoff without rewriting that receipt.

Locally attempted all17 source-stage/frozen-feature tests. After redirecting temporary fixtures into the writable workspace,15 passed and two errored at Windows sandbox-denied os.link publication in the existing immutable-record helper. No model or GPU test was run locally. The initial default-temporary-directory attempt also encountered sandbox permissions. These are environment-limited local results, not a claim of17 passing tests or a demonstrated production logic failure. Exact-head Linux CI is green; the producer separately reports37 focused tests. Do not rerun the private pilot to resolve a reviewer-host filesystem restriction.

Independent standard-library checks passed for integrated/role arithmetic, public implementation/config/summary hashes, unchanged accepted summaries, pilot manifest/input/worker links, feature shapes and payloads, forward-call totals and reported zero repeat differences. Private rows, checkpoints, shards, owner approval, GPU logs and images are unavailable here. Their real execution and saved-array verification remain bounded producer-reported evidence supported by reviewed gates. Technical byte/frame/array verification is not visual adjudication or independent scientific replication.

## Integration is a usable handoff

| Dataset | Archived originals | Source-use originals | Successful model-image inputs | Retained source-use failures |
|---|---:|---:|---:|---:|
|OULU-NPU|4950|4950|4949|1|
|MSU-MFSD|280|280|272|8|
|CASIA-FASD|600|600|594|6|
|SiW-Mv2|1680|1052|1040|12|
|Total|7510|6882|6855|27|

Totals reconcile7510=6882+623 null-role test originals+five source exclusions, and6882=6855+27 failures. Archived nine pre-detector and22 detector failures include four SiW test failures; they must not become31 source failures. Effective train/calibration/g_domain input counts4105/1378/1372 sum6855. Actual scored-fit rows remain zero until scores exist. No missing image is fabricated for the accepted OULU terminal failure.

The adapter preserves accepted earlier-middle selections, native224/518 crops, frozen identities/roles and SiW eligibility binding. The narrowly recognized historical OULU classifier_error omission does not relax modern records. Model-free source routing excludes the entire outer target and entire pseudo-target domain from fitting, retains role-specific failure denominators and rejects test/excluded/wrong-role inputs. The actual integration reportedly exercises all four outer rotations and12 pseudo-domain exclusions. Future consumers must load the sealed handoff; these helper functions do not authenticate arbitrary caller-supplied dictionaries on their own.

## The encoder pilot proves the intended technical scope

The sealed sample is24 successful train inputs from CASIA/MSU/SiW, eight per domain and four per class. OULU is completely absent as the pilot outer target. Labels define the predetermined IO sample, not an optimization objective or cache key. No calibration/g_domain/test/excluded/failed row is a pilot input.

Three exact registered checkpoints were acquired under a reported fresh single pilot authority. DINO SHA256 values are appropriately described as local acquired-byte identities rather than publisher digests; OpenCLIP also binds its published LFS digest/revision. Strict state loading, the explicit Reg4 factory alias, frozen eval/inference mode, FP32 and deterministic settings are consistent with the declared pilot. Cached weights should now be reused by exact digest rather than downloaded again.

DINO pooling concatenates768 CLS and768 mean patch-only features from1369 native518 patches; register tokens cannot enter the mean. OpenCLIP produces normalized512-dimensional image embeddings with checkpoint-native normalization. Reported24x1536,24x1536 and24x512 arrays have correct FP32 payloads and zero repeat maximum absolute difference under the predeclared tolerance.144 image forwards and two text forwards reconcile with two passes over24 inputs for three encoders. Saved-array/crop/cache-key joins and fixed-prompt cosine-logit reconstruction are appropriate technical checks, not evidence of predictive accuracy or superiority of any branch.

The397.83-second approval-through-closure duration and reported RSS/storage remain below the pilot caps. Persisted GPU peaks explicitly cover image passes; text peaks were checked but their final numbers were not retained. Keep that honest limitation; it does not justify replaying the pilot. In the next controller, persist the final allocator peaks after all image/text work and bind the full extraction transform/runtime contract to cache provenance when code, normalization or precision can change.

The6855-input projection of307.81 forward-only seconds and98,273,280 feature bytes is arithmetically consistent, but excludes IO/startup/sharding/fitting and spans the union of source-eligible datasets across rotations. It is not a single outer fold's source population, a full-wall estimate or permission to score its outer target.

## Concrete next package

**Implement full source-feature caching and the first genuine source-only fitting/OOF run now.** A practical first outer fold keeps OULU as target, reusing the already tested source combination. Its complete successful source-image population is1906=272 MSU+594 CASIA+1040 SiW, across their permanent source roles. Use train for fitting, calibration for the registered calibrators and g_domain for its registered purpose; do not pool roles or fit on all1906 indiscriminately. Keep failure-inclusive population denominators even though failures have no feature vector.

The next package should contain the following together, not another plan-only checkpoint:

1. A deterministic resumable extraction controller over the sealed fold-local source manifest, reusing the exact acquired checkpoints and valid295 sample features by compatible keys. Verify every newly read crop hash, native shape/normalization, finite feature shape, one-to-one cache joins, shard readback and complete coverage. Commit shards atomically, preserve successful shards on interruption and avoid repeated model inference merely to recreate receipts. No new video/detector campaign or blanket two-pass extraction is needed.
2. Actual source-recipe implementation for DINO linear heads, registered monotone affine calibrators and fixed OpenCLIP branch behavior, with deterministic checkpoints/seeds and role isolation. Generate genuine held-out source predictions and error labels using the registered OOF strategies. For domain-OOF fitting, exclude the entire pseudo-target domain; validate matched-sample OOF according to the existing recipe rather than inventing a shortcut. Fit the specified risk/competence/applicability components only from appropriately separated source evidence.
3. One bounded execution plan with measured IO allowance, extraction/fitting resource estimates, stop conditions and exact inputs. The completed295 authority was for24 pilot images only and is not authority for1906/full extraction or classifier fitting. Prepare the executable package first, then obtain one combined fresh authority if existing explicit permission does not already cover it. Keep OULU target image access/predictions, target tuning and locked evaluation outside this source-only package.
4. Publish actual feature coverage, fitted-model/prediction provenance, OOF joins and the normal source-dry-run validator result. If the first run implements only part of required scientific evidence, report the specific remaining components; never fill missing competence/applicability artifacts with placeholders or call extraction alone a scientific dry-run.

For additional outer rotations, retain the same immutable cache contract and filter each consumer by its own outer/pseudo-target roles. Cache reuse must not import fitted state or target-dependent choices across folds. No need to re-certify the data or rerun295 before implementing this next stage. Scientific/analysis-freeze/locked-evaluation gates change only when their actual evidence is produced and authorized.

**295 closes integration and the technical pilot. Next progress must be full source features and actual source fitting/OOF results, with the existing scientific gates honestly reported.**
