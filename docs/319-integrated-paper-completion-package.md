# 319 - Integrated empirical PAD paper-completion package

Date: 2026-10-28

Status: **preparation delivered; supplementary scientific execution is not
authorized and is not yet executable.** This package implements the owner's
request to prepare steps1-3 together after
[Review318](318-review-proposal317-bounded-empirical-paper-route.md).
It includes a manuscript draft, focused positioning and a concrete proposed
protocol. No positive supplementary result is invented.

## 1. Deliverables and decision

- [Manuscript draft](paper319/manuscript.md): introduction, methods,
  completed-development results, planned comparison and limitations.
- [Closest-work and venue brief](paper319/related-work-and-venues.md):
  contribution boundaries and verified source links.
- [Machine-readable supplementary specification](paper319/supplementary-protocol.json):
  fixed systems, recipes, metrics, fit counts, uncertainty and proposed caps.
- [Actual metadata-only preflight](../results/phase1/paper319-metadata-preflight-v1.json):
  exact populations and private partition commitment, not an experiment result.
- [Preparation tool](../scripts/diagnostics/prepare_paper319.py) and
  [tests](../tests/test_paper319.py): deterministic group-safe partitioning,
  official-test exclusion from source use and zero-fit preparation.

Recommendation: keep the narrow empirical contribution, not a new architecture
or an improved-fusion claim. The ordinary ROC/oracle calculation is not a new
algorithm. Its value here is the comparative evidence separating available
source-policy failure from insufficient low-FA separation of fixed scores.

The closest-work check also confirms that multi-source train-three/test-one
and register-DINO comparisons already exist; neither is a standalone novelty
claim. Costa-Pazo2021's exact threshold methodology remains unverified because
its full text was inaccessible. The two venue candidates are provisional:
primary year/category-specific Q3 evidence could not be verified. No venue
is advertised as certified Q3 on secondary search summaries alone.

## 2. Concrete preparation findings

The accepted295 manifest was checked against SHA256
`7f9f54e6b097d7da0618cf8b3784e9eb3726b6aba8a3957455e26dda20da4580`.
The preparation reads saved metadata and hashes existing cache shard bytes.
It does not decode images/videos, load feature arrays, fit models or generate
predictions.

| Population | Original videos | Usable prepared images | Technical failures |
|---|---:|---:|---:|
| Archived four-dataset population | 7510 | 7479 | 31 |
| Active population after inherited five SiW source exclusions | 7505 | 7474 | 31 |
| Proposed source train/development union | 4562 | 4545 | 17 |
| Official target-test union | 2943 | 2929 | 14 |

These are unique unions, not independent samples across rotations.
SiW specifically denotes the adopted **Protocol-I local intersection**,
not the complete release:1680 originals match the supplied archive and
reference lists,20 supplied out-of-protocol originals are excluded and11
reference originals are absent. Its623 target originals are the declared
test-list intersection, not a claim of full-release test coverage. The
[accepted population receipt](../results/phase1/siwmv2-intersection-v1.json)
and unchanged benchmark amendment retain those distinctions.
All7474 proposed usable originals have receipt-level coverage in each of
the three feature branches.705 shard files totaling113246846 bytes match
their saved digests. This is **metadata/byte verification**, not full array-key,
crop-contract or numerical runtime revalidation. Those checks remain mandatory
before execution. If they pass, no new foundation-encoder inference is needed.
Existing frozen heads/calibrators cannot be reused under the narrower source
protocol.

Private partition manifest SHA256:
`2700baf9d757cc8c773247f104cd2a85c4ee9c288e461bb929cdbff9333c2996`.
The public receipt contains counts, not private IDs or individual scores.
Draft oracle tables are recalculated from316's public cases. In particular,
fixed equal DINO-CLIP's OULU mean is26.6694725%, displayed as26.669% at three
decimals rather than the26.670% printed in316's prose table. No saved result
or scientific conclusion is changed.

### Critical limitation found: SiW subjects are unknown

The accepted local SiW-Mv2 manifest has no subject IDs for any of1680 archived
originals. Its registered unit is video, not participant. No subject IDs are
inferred from filenames. OULU, CASIA and MSU have known subjects and disjoint
official-partition group sets.

Consequently,318's request for subject separation cannot be certified for
SiW from current evidence. The concrete proposed amendment is:

**retain SiW, use video-plus-exact-frame components and label its comparisons
and intervals video-grouped; do not claim participant-disjoint source
validation/calibration or participant-level uncertainty on SiW.**

This affects fitting, model selection, threshold estimation and interpretation,
not just interval wording. It is an explicit limitation requiring acceptance
in the one integrated scientific approval. If that scope is unacceptable,
recover trustworthy identity metadata before sealing execution; do not
silently replace SiW, add a dataset or invent subjects.

## 3. Exact proposed population and splitting rule

Train on three datasets and evaluate on the fourth, using seeds20260917,
20260923 and20261001:12 contexts per system. All official source tests are
excluded. Target labels never select heads, epochs, calibration or thresholds.
The targets have already informed development; this is not untouched
confirmation or an MCIO leaderboard reproduction.

Create components from registered groups and saved exact selected-frame
hashes. Preserve the five adopted SiW source exclusions. Reject a component
crossing an official partition or dataset boundary.

- OULU: official train for fitting; split official development components by
  deterministic hash rank, alternating validation/calibration.
- CASIA/MSU/SiW: official eligible train only; within dataset and component
  class-signature strata, hash-sort components and assign ranks modulo5:
  validation0, calibration1, fitting2/3/4.
- Fixed split seed20261028; the three training seeds do not change populations.
- Keep original failures in role denominators; only successes are model inputs.
  New protocol roles are separate from historical permanent roles and do not
  rewrite the old studies or source-use receipts.

Actual assigned counts below are **originals / usable**, not fitted results:

| Dataset | Fitting | Validation | Calibration | Target test |
|---|---:|---:|---:|---:|
| OULU-NPU | 1800 /1799 | 720 /720 | 630 /630 | 1800 /1800 |
| CASIA-FASD | 144 /144 | 48 /48 | 48 /48 | 360 /354 |
| MSU-MFSD | 72 /69 | 24 /23 | 24 /24 | 160 /156 |
| SiW-Mv2 | 630 /624 | 211 /206 | 211 /210 | 623 /619 |

Support floors are explicit in the specification and pass these partitions.
MSU calibration has only18 attacks and6 bona-fide originals, from3 subjects.
At5% the successful-attack error budget is zero. This permits calculation;
it does not establish precise low-FA transfer or population security.
Report this resolution limitation rather than enlarging support after scores
are observed.

## 4. Fixed systems and specialist feasibility

Use the accepted earlier-middle-frame crops: RGB518 for DINO branches and
RGB224 for CLIP/DeepPixBiS. No detector, frame replacement or geometry search.

| System | Proposed fixed recipe |
|---|---|
| DINO-Reg | Existing raw1536 feature contract; FP64 full-batch AdamW, lr.001, wd.05,200 epochs |
| Supervised CLIP | Existing normalized512 feature contract; same optimizer, lr.01, wd.05,200 epochs |
| Original equal two-DINO | Mean calibrated DINO-Reg/plain-DINO probabilities; plain branch lr.001, wd.05 |
| Matched DeepPixBiS | Official architecture, ImageNet DenseNet161 initialization, source-only50-epoch retraining; detailed fixed recipe in JSON |

For frozen heads, use minimum source-validation balanced BCE, earliest tie,
no post-selection refit. Three branch heads/context are shared by the first
three systems, not refitted for fusion.

### What was actually verified about DeepPixBiS

The authors' [GitHub pointer](https://github.com/anjith2006/bob.paper.deep_pix_bis_pad.icb2019)
contains a README and GPL license, pointing to Idiap GitLab. The original
GitLab endpoint was not reachable during preparation; it is not represented
as a verified training checkout.

An official Idiap organization mirror provides accessible
[architecture/inference source at pinned commit555f181](https://github.com/bioidiap/bob.pad.face/blob/555f181a76fa39d20f0c61ef1dc616bd85b817c1/src/bob/pad/face/deep_pix_bis.py)
and a [pipeline configuration](https://github.com/bioidiap/bob.pad.face/blob/555f181a76fa39d20f0c61ef1dc616bd85b817c1/src/bob/pad/face/config/deep_pix_bis.py).
This verifies RGB224, ImageNet normalization, a DenseNet161-derived
384x14x14 representation, pixel/global outputs and default pixel-mean
bona-fide scoring. Its classifier's fit method does not train a model.
The configuration loads OULU-trained weights; using those as a clean
cross-dataset comparator would be inappropriate here.

The [GPL repository license](https://github.com/bioidiap/bob.pad.face/blob/555f181a76fa39d20f0c61ef1dc616bd85b817c1/COPYING)
must be respected in any distributed implementation. Do not copy upstream
code into the project without appropriate license/notice handling.

Therefore specify a **matched-input architecture retraining**, not an exact
reproduction of the original paper's recipe or published accuracy.
Researcher-fixed choices are Adam lr1e-4, wd1e-6, batch16,50 epochs, constant
schedule, equal-source/class sampling, horizontal flip only, and equal-weight
pixel/global BCE. The validation loss selects the earliest best checkpoint.
All details are frozen in JSON; these hyperparameters are not falsely
attributed to the original paper.

Installed torch2.7.1/torchvision0.22.1 and CUDA availability on an RTX4080SUPER
were checked without constructing a model. Torchvision's
DenseNet161 IMAGENET1K_V1 initialization URL was verified; weights are not
cached and were not downloaded. Architecture training compatibility,
throughput and watchdog enforcement are not yet demonstrated.

## 5. Policy, analysis and uncertainty

Fit four positive-affine sigmoid calibrators/context: DINO-Reg, plain-DINO,
CLIP and specialist. Average the two calibrated DINO branches without another
calibrator. For specialist use attack score1 minus mean pixel probability,
then a declared clipped logit input to its calibrator.

For each system use one common threshold derived only from source calibration:
the minimum per-source FA-safe attack order statistic under successful
calibration denominators, with integer budgets and strict score<threshold
acceptance. Keep5% primary;1% and10% are sensitivity views, not replacement
success rules. This conservative calibration denominator differs explicitly
from the failure-inclusive evaluation denominator.

For each target/system/seed report:

1. Usable-only AUROC and its support.
2. Source-policy accepted attack/BF counts, original-denominator FA/BFA and
   compatible usable-only errors. No made-up scores for technical failures.
3. Evaluation-label oracle maximum original-denominator BFA at the same FA
   budgets, labeled descriptive and never fed into policy/model selection.
4. The5%/50% empirical utility status and its integer support.

Use paired2000-replicate target-cluster bootstrap, conditional on fitted
models and source thresholds. Known subjects are the units for OULU/CASIA/MSU;
SiW uses video/exact-frame components under the limitation above. Report seeds
separately. Do not turn four observed datasets into a population-of-domains
confidence interval. Oracle estimates are descriptive point estimates in
this package; no invalid fixed-threshold bootstrap interval is attached to
an optimized oracle point.

Do not present overall attack FA as a worst-attack-species APCER or claim ISO
conformance. Attack-specific metrics require reliable attack metadata and
explicit denominators; they are not prerequisites for silently changing the
main population.

## 6. Inventory, proposed budget and execution boundary

| Work item | Maximum / declared output |
|---|---:|
| Frozen-feature head starts | 36 |
| Specialist training starts | 12 |
| Calibrator starts | 48 |
| Specialist epochs | 600 |
| Specialist optimizer steps, based on actual fitting counts and batch16 | 74400 |
| Source threshold records,4 systems x12 contexts x3 FA levels | 144 |
| Target oracle diagnostic records | 144 |
| Target/system/seed main rows | 48 |
| Foundation encoder forwards, dataset downloads, detector runs | 0 |

Proposed single-authority limits:12h total,11h work cutoff,40min per
specialist context,12GiB combined sampled RSS,12GiB CUDA allocated/reserved,
8GiB owned new+temporary artifacts,256MiB maximum initialization acquisition,
two BLAS threads, no automatic retry. These are stop ceilings, not measured
completion predictions. Best checkpoints replace only owned temporary files;
no full per-epoch checkpoint archive is planned.

No grid, alternative baseline contest, rescue calibrator, new dataset or
automatic shortened training follows a failure. A cap violation produces an
incomplete receipt, not a success-shaped partial comparison.

**This is a concrete review specification, not a sealed executable package.**
Before the one execution decision, implement and test the training/analysis/
watchdog controller, resolve license handling, bind runtime and initialization
acquisition rules, revalidate cache contracts and retain exact code/input
hashes. This technical completion stays within the same preparatory work;
it does not require separate scientific proposals per dataset or seed.
No scientific run is requested under unimplemented enforcement.

## 7. Paper progression and stopping rule

The manuscript starts now with completed-development evidence and explicit
pending main results. Existing314/316 tables stay separate from the new
official-partition comparison. Neither prior locked-target conclusions nor
missing selected policies are upgraded by reframing the paper.

After review and technical sealing, request one integrated owner decision
covering SiW's grouping limitation, acquisition, exact implementation and
budget. Then run once, verify, fill the paper and stop model search.
If the empirical gap is too weak, make one explicit scope/venue decision;
do not automatically add architectures to obtain a favorable result.

## 8. Preparation verification

The12 new preparation tests pass with the existing FAS Python environment:

```bash
python -m unittest discover -s tests -p test_paper319.py -v
```

They cover order-independent deterministic splits, all12 contexts, native
development isolation, unknown subjects, inherited exclusions, technical
failure denominators, exact-frame boundary rejection and forbidden
fit/predict/feature-load calls. An additional direct check verifies every
context's exact target-test membership and known-subject disjointness.
All24 draft oracle means and24 feasibility counts match316's public cases.
The existing313/316 code inventories and316 analysis-plan binding remain
unchanged. No old result is overwritten.

Pylance's syntax service was unavailable because its MCP transport failed;
runtime imports and the actual unittest run provide the Python validation
reported here, not a successful editor type check.

The preparation command has already written immutable private/public records.
Do not rerun it expecting overwrite or treat its metadata status as permission
to launch the supplementary study. Its12 contexts are planned inputs, not12
completed model evaluations.
