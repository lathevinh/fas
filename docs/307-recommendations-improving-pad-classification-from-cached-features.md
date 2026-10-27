# 307 - Recommendations: improve PAD classification using cached features first

Date: 2026-10-27
Basis: accepted fixed results301/Review302 and exploratory geometry305/Review306.
Status: implementation recommendations requested by the owner; not a new training or target-evaluation authorization.

## Main recommendation

**Prioritize supervised classification and operating-point selection on existing frozen features. Keep the accepted preprocessing-v3 baseline for the next comparison; do not automatically promote G2, force a50/50 heterogeneous fusion or start another image campaign.**

The immediate deliverable should be one compact executable comparison of DINO-Reg, the equal two-DINO baseline and a supervised linear probe on frozen OpenCLIP image features. Specify source-only nested selection, fixed metrics, resource/stop rules and exact cached inputs together. This is exploratory development on observed datasets, not a repair of301 or independent confirmation of a revised method.

## Why this priority

301 found standalone zero-shot OpenCLIP weak, heterogeneous superiority unsupported, and large target operating-point failures.305 found no established overall benefit from G2 padding: DINO-Reg source AUROC increased only0.002174 descriptively, while OpenCLIP and both equal-fusion systems declined on average. Changing geometry again is therefore not the first evidence-supported use of compute.

The weak zero-shot branch does not establish that OpenCLIP image embeddings lack PAD information. A supervised linear classifier on the already saved512-dimensional image features tests a different, concrete hypothesis at much lower cost than new encoder extraction or prompt/backbone tuning. Frozen DINO feature readout is also an established use of that representation. See the primary [CLIP paper](https://arxiv.org/abs/2103.00020) and [official DINOv2 implementation](https://github.com/facebookresearch/dinov2). These references motivate the approach; they do not promise improvement on these PAD datasets.

## 1. Strengthen and fairly select the DINO baseline

Compare DINO-Reg alone and the calibrated equal DINO-Reg/plain-DINO average using the accepted stretched-input feature cache. Keep the same sample/group identities, technical-failure denominators, permanent roles and SiW effective-use exclusions. Maintain a shared DINO anchor where comparing systems.

Before fitting, specify a small bounded candidate grid for feature normalization, regularization and learning rate. Include the exact old head recipe as an anchor. Fit any learned scaling on permitted training data only; validate deterministic per-vector transforms separately. Choose configurations with group-safe inner source validation, never target outcomes, and give methods comparable search budgets. Do not simultaneously expand geometry, prompts, backbone and feature selection.

Many existing heads selected epoch200, their fixed endpoint. Inspect saved train/validation diagnostics where available before interpreting this as undertraining. Endpoint selection does not prove convergence or justify arbitrary longer runs. If additional epochs are tested, preregister that candidate budget and early/checkpoint-selection rule in the new exploratory package; keep the old result unchanged.

## 2. Test supervised OpenCLIP features before more prompt work

Reuse the exact accepted512-dimensional frozen OpenCLIP image embeddings from the original geometry, verified by sample/checkpoint/transform/cache hashes. Train a binary linear logistic head on allowed source-train inputs, with separate allowed calibration and group-safe validation. Keep the current fixed-prompt zero-shot branch as a diagnostic comparator. No new CLIP encoder or text inference is needed for this probe.

Use the same label, role, group, outer/pseudo-target exclusion and fitting-budget discipline as DINO. Evaluate held-out source AUROC, balanced accuracy, calibration and error overlap/complementarity with DINO. Good supervised source performance does not by itself establish unseen-target improvement or useful heterogeneous fusion. If the probe remains weak or redundant, retain the negative result and stop forcing CLIP into the main system.

## 3. Make fusion conditional on measured incremental value

Only after branch readouts are specified should a bounded convex-fusion comparison be considered. Include DINO-only and CLIP-only endpoints and the fixed equal fusion; retain the strong equal two-DINO comparator. Select weights by a declared utility, source aggregation and deterministic tie rule inside nested group-safe source validation, not on a shared tuning/evaluation table. Weight zero for CLIP is a legitimate outcome, not a failed experiment to hide.

If risk models are also studied, classifier/fusion changes alter the error labels. Cross-fit the entire selected pipeline, including readout/calibration/fusion selection, before producing OOF risk supervision. Do not pick a weight using all source labels and then describe its predictions as honestly held out. Separate improving PAD classification from improving error ranking on a fixed classifier; neither metric substitutes for the other.

## 4. Treat operating-point transfer as a separate problem

301's near-perfect CASIA ranking AUROC alongside poor fixed-threshold ACER shows why ranking alone is insufficient. Source empirical FA<=1% did not transfer as a target guarantee. Inspect score distributions, calibration and FA/BFNR tradeoffs across held-out source domains. Report absolute attack false acceptance, bona-fide non-acceptance, coverage and technical failures on original class denominators, not only average accuracy or relative harms.

Specify the operating objective and allowed source-only threshold/calibration selection in advance. Do not lower a threshold on an observed target to advertise better accuracy while hiding increased attack acceptance. Keep operational coverage separate from ranking coverage; rejecting many bona-fide inputs is not good usability even if coverage or attack blocking looks favorable.

## 5. Escalate model capacity only after the cheap comparison

If the fixed-feature readout comparison has a clear limitation, consider a separate bounded partial-backbone fine-tuning study. Do not automatically add fine-tuning, prompt learning, new crops or multi-frame inference to this first package. Each changes capacity or the accepted task and needs its own concrete question and budget. No claim of expected percentage gain is justified by the existing evidence.

## Immediate execution package and reporting

1. Fix the dependency/test-contract CI errors identified in306 and preserve the failed-run history. This software correction does not require re-extracting images or rerunning private scientific models.
2. Prepare the cache-only classifier comparison with exact methods, small search grid, group-safe nested splits, objective/decision rules, input bindings and resource estimates. Reuse existing valid features. Ask once for any fresh execution authority required by that complete scope; this document alone does not authorize model fits or new target access.
3. Report all candidate/selected source results, variability and failures. At minimum separate AUROC, balanced accuracy/ACER and operational FA/BFNR/coverage. Keep the unmodified baseline, two-DINO comparator and zero-shot CLIP diagnostic visible. Do not select only the best seed or favorable domain.
4. Treat all four previously observed datasets as development/exploratory material for this revised method. Independent confirmation requires a genuinely unseen authorized dataset or prospective cohort with a locked protocol. This need does not block code preparation or a clearly labeled source-development study, but it prevents calling revised-method results on observed targets untouched confirmation.

**Recommended first action: implement and test the bounded supervised readout comparison using existing DINO/OpenCLIP caches. Do not spend on another geometry/encoder campaign before that cheaper question is answered.**
