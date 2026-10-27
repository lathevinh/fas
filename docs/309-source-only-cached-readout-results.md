# 309 - Source-only cached PAD readouts: results and saved-output closure

Date: 2026-10-27

Status: the owner-approved [package308](308-cache-only-supervised-readout-execution-package.md)
completed once, followed by successful saved-output reconstruction. This is
exploratory source development, not new target confirmation or a revision of301.

## Main result

**Supervised readout substantially improves OpenCLIP over its weak zero-shot
diagnostic, but does not beat the strong two-DINO comparator on the primary
source-domain generalization endpoint. Operating-point transfer remains poor.**

Across the12 overlapping domain-OOF exclusion/seed contexts, descriptive mean
source AUROC changes from **0.554171 to0.844040** for OpenCLIP:
delta **+0.289869**. Every context's conditional paired bootstrap interval for
supervised minus zero-shot CLIP is positive. This supports the narrower
conclusion that the cached image embeddings contain useful PAD information
not recovered by the fixed prompt readout.

Selected equal two-DINO remains stronger at **0.889780**. Supervised CLIP minus
selected two-DINO averages **-0.045740**;10 conditional intervals are negative,
2 inconclusive and none positive. Passing the source competence screen does
not establish incremental fusion value, unseen-target improvement or security.

The [aggregate verified receipt](../results/phase1/source-readout308-closure-v1.json)
contains every context, candidate diagnostic, selected configuration, source
metric, conditional interval, failure denominator and fit-artifact hash.

## 1. Authority, software and immutable inputs

Scientific execution used published commit
`f02a268832a412dd9cb58b71bea8649dca16ffa1`, after the owner explicitly approved
the complete480-head/144-calibrator scope. The sealed
[plan](../results/phase1/readout308-plan-v1.json) SHA256 is
`2192a5007432f4ea201d8745187cd216ab83490fcade536effb54a818c72c89d`.
Its historical `prepared_not_authorized` status is intentionally unchanged:
the later approval and terminal in the result receipt record the subsequent
authority and execution, rather than rewriting the pre-run inventory.

The exact package commit passed
[Actions40470569695](https://github.com/lathevinh/fas/actions/runs/40470569695):
516 discovered tests,3 existing RAR transport tests skipped because `bsdtar`
was unavailable, all numerical/readout tests successful, canonical schema
successful and all expected unavailable/legacy stage rejections successful.
The failed workflow identified in306 remains historical; it was not hidden
by rerunning private science.

Use the original299 stretched-input caches, not G2, with unchanged checkpoints,
crops, roles, labels and source-use exclusions:

| Dataset | Eligible originals | Usable originals | Technical failures |
|---|---:|---:|---:|
| CASIA-FASD | 600 | 594 | 6 |
| MSU-MFSD | 280 | 272 | 8 |
| OULU-NPU | 4950 | 4949 | 1 |
| SiW-Mv2 | 1052 | 1040 | 12 |
| Total | 6882 | 6855 | 27 |

OULU/CASIA/MSU official-test members historically assigned source roles remain
source-use members. SiW null-role official tests and the five adopted
exclusions remain ineligible. This is not official-train-only development.

All four observed datasets remain development material. The named outer
exclusion is excluded from that context's fitting **and evaluation**; its
name is not the domain being evaluated. Domain-OOF evaluates the other three
sources, each completely held out as a pseudo-target from fitting, epoch/grid
selection, calibration and threshold choice in its own fold.

No raw image decoding, new image/text encoder forward, backbone update,
new target prediction, heterogeneous weight selection or risk fitting occurred.
Original source evidence, old results and both original freezes were not
replaced.

## 2. Registered readout comparison actually executed

All three branches received the same four candidates:

1. Raw cached vectors, learning rate.001, weight decay.05: exact old anchor.
2. Per-vector unit-L2 normalization, learning rate.001, weight decay.05.
3. Raw vectors, learning rate.01, weight decay.05.
4. Raw vectors, learning rate.001, weight decay.005.

Every candidate used the inherited200-epoch FP64 full-batch AdamW head, fixed
group-safe inner validation, balanced source/class BCE, earliest minimum-BCE
epoch and no refit. Candidate selection used only inner validation BCE with
declared candidate-order ties. There was no post-result grid expansion,
additional epoch budget, optimizer amendment or retry.

The96 exact old DINO heads were reused as anchors;480 new heads were fitted.
All144 selected heads received allowed-source calibration. The two-DINO
average has fixed equal weights and shares the selected DINO-Reg branch with
the standalone selected system; it is not a newly learned fusion.

Selected candidates across48 source fitting contexts per branch:

| Branch | Old anchor | Unit-L2 | Higher LR | Lower decay | Selected epoch200 |
|---|---:|---:|---:|---:|---:|
| DINO-Reg | 0 | 0 | 48 | 0 | 43/48 |
| Plain DINO | 6 | 0 | 34 | 8 | 36/48 |
| OpenCLIP | 0 | 0 | 48 | 0 | 48/48 |

Lower inner-validation BCE did not guarantee improved held-out-domain AUROC:
selected DINO-Reg is worse than its old anchor in10/12 primary contexts.
All CLIP selections reaching epoch200 does not prove undertraining or
authorize extending the cap.

## 3. Primary domain-OOF classification results

Each cell below is the descriptive mean of12 equal-source macro metrics.
The same originals recur across seeds and exclusions; these are not12
independent experiments or a pooled unseen-test sample.

| System | AUROC | Balanced accuracy | Successful ACER | Brier |
|---|---:|---:|---:|---:|
| Original DINO-Reg | .885432 | .714898 | .285102 | .254452 |
| Original equal two-DINO | .889609 | .723324 | .276676 | .239646 |
| Original zero-shot CLIP | .554171 | .501294 | .498706 | .256056 |
| Selected DINO-Reg | .879631 | .733053 | .266947 | .250467 |
| Selected equal two-DINO | .889780 | .735689 | .264311 | .233164 |
| Supervised CLIP | .844040 | .681211 | .318789 | .196216 |

The reconstructed old AUROC means agree with the unchanged299 anchors used
in305. Selected DINO-Reg minus old DINO-Reg averages-.005802.
Selected two-DINO minus its old anchor averages only+.000171, with5 positive
and7 negative contexts; no paired selected-versus-old CI was registered here.
Do not promote this tiny descriptive difference as an established improvement.

CLIP's lower Brier score is useful probability-scoring evidence on the
declared population, not proof of superior ranking or pure calibration.
Brier/NLL depend on discrimination and class distribution as well as
calibration. NLL and score ranges remain available in the full receipt.

All12 primary AUROC rows, including unfavorable contexts:

| Excluded outer source / seed | Old Reg | Old two-DINO | Selected Reg | Selected two-DINO | Zero-shot CLIP | Supervised CLIP |
|---|---:|---:|---:|---:|---:|---:|
| OULU-NPU /20260917 | .925129 | .945292 | .914795 | .949377 | .578760 | .921674 |
| OULU-NPU /20260923 | .935914 | .952060 | .932031 | .956536 | .578760 | .914057 |
| OULU-NPU /20261001 | .918379 | .933571 | .913072 | .929778 | .578760 | .918865 |
| CASIA-FASD /20260917 | .812458 | .817502 | .805692 | .816001 | .544497 | .773142 |
| CASIA-FASD /20260923 | .828489 | .841971 | .821077 | .834596 | .544497 | .767245 |
| CASIA-FASD /20261001 | .840705 | .854972 | .827746 | .848571 | .544497 | .788876 |
| MSU-MFSD /20260917 | .896025 | .863283 | .895242 | .871718 | .560214 | .808488 |
| MSU-MFSD /20260923 | .890569 | .870449 | .893336 | .879196 | .560214 | .794804 |
| MSU-MFSD /20261001 | .902614 | .889421 | .907218 | .900334 | .560214 | .815760 |
| SiW-Mv2 /20260917 | .888521 | .897257 | .878198 | .888962 | .533214 | .872830 |
| SiW-Mv2 /20260923 | .891007 | .907329 | .890744 | .904104 | .533214 | .878126 |
| SiW-Mv2 /20261001 | .895381 | .902202 | .876418 | .898192 | .533214 | .874613 |

### Conditional uncertainty, not new-domain confirmation

Every pool/context had2000/2000 valid paired registered-group bootstrap draws.
The same draws were used for all systems. Primary contrast summaries:

| Supervised CLIP minus comparator | Mean AUROC delta | Positive CI | Negative CI | Inconclusive CI |
|---|---:|---:|---:|---:|
| Zero-shot CLIP | +.289869 | 12 | 0 | 0 |
| Selected DINO-Reg | -.035591 | 0 | 7 | 5 |
| Selected equal two-DINO | -.045740 | 0 | 10 | 2 |

These are individual unadjusted conditional saved-predictor intervals, not a
joint interval for the mean, retraining uncertainty, independent replications
or a familywise superiority test. Existing registered groups are resampling
units; exact-frame unions enforce split safety, not a new bootstrap scheme.
All selected/supervised systems pass the inherited source competence screen
in12/12 primary contexts; zero-shot CLIP passes0/12. Passing the screen alone
does not select a heterogeneous system.

## 4. Operational transfer remains a separate problem

Thresholds were selected on allowed calibration rows only, using the
registered empirical APCER<=5% per calibration source. Ties are attack/high
and not accepted. Original old thresholds were preserved.

The following are equal-source means across12 primary contexts, on original
class denominators, **in percent**:

| System | Attack FA | Bona-fide non-acceptance | Operational acceptance coverage |
|---|---:|---:|---:|
| Original DINO-Reg | 29.544 | 27.476 | 42.410 |
| Original equal two-DINO | 33.833 | 21.565 | 47.396 |
| Original zero-shot CLIP | 5.667 | 94.043 | 5.738 |
| Selected DINO-Reg | 30.589 | 22.829 | 44.195 |
| Selected equal two-DINO | 35.066 | 17.882 | 49.200 |
| Supervised CLIP | 9.974 | 53.942 | 20.635 |

The CLIP readout improves usability relative to near-reject-all zero-shot,
but also increases attack acceptance relative to that diagnostic. It still
rejects over half of bona-fide originals on this macro summary. Two-DINO's
stronger ranking does not make its transferred operating point secure.

Per evaluated source, means of its nine overlapping primary contexts:

| Held-out source | CLIP AUROC | Selected two-DINO AUROC | CLIP FA % | CLIP BF non-accept % | Two-DINO FA % | Two-DINO BF non-accept % |
|---|---:|---:|---:|---:|---:|---:|
| CASIA-FASD | .966878 | .989369 | .278 | 66.389 | .525 | 38.333 |
| MSU-MFSD | .906977 | .928632 | 10.185 | 35.119 | 39.153 | 4.960 |
| OULU-NPU | .734883 | .838760 | 13.289 | 61.967 | 67.305 | 5.429 |
| SiW-Mv2 | .767422 | .802360 | 16.143 | 52.294 | 33.281 | 22.806 |

CASIA's high CLIP ranking alongside66.389% bona-fide non-acceptance and OULU's
67.305% two-DINO attack acceptance illustrate why AUROC alone is inadequate.
These are not a repeat of301's target evaluation. This stage uses the5%
classifier reference policy, not301's selective FA<=1% guardrail, and neither
source-calibration number transfers as a security guarantee.

All27 original technical failures retain non-acceptance, without invented
scores. There are24 failures in the domain-OOF role pool and3 in `g_domain`.
Successful ACER is not relabeled as original-denominator classifier ACER.
Error-overlap counts in the receipt are on common successful rows at each
system's source-selected threshold; they are neither class-balanced utility
nor proof that any fusion will improve the chosen operating objective.

## 5. Secondary `g_domain` results

| System | Mean AUROC | Mean balanced accuracy |
|---|---:|---:|
| Original DINO-Reg | .994853 | .925453 |
| Original equal two-DINO | .995329 | .968590 |
| Original zero-shot CLIP | .540416 | .501754 |
| Selected DINO-Reg | .994600 | .949731 |
| Selected equal two-DINO | .993661 | .971065 |
| Supervised CLIP | .977420 | .865962 |

Supervised minus zero-shot CLIP averages+.437003, with12 positive conditional
intervals. Against selected DINO-Reg: mean-.017180,10 negative and2
inconclusive intervals. Against selected two-DINO: mean-.016241,7 negative
and5 inconclusive intervals. No positive CLIP-versus-selected-DINO interval
occurs here either.

These are held-out groups within the fitted source domains, under a
three-source final fit, not the primary pseudo-target-domain transfer test.
The impressive.977420 must not be presented as unseen-domain performance.
The different pool and training-domain composition also prevent interpreting
its difference from.844040 as a controlled treatment effect.

## 6. Execution and independent saved-output verification

One attempt completed without errors, numerical amendments, partial reruns or
post-result selection:

| Quantity | Observed |
|---|---:|
| Exclusion/seed combinations | 12 |
| Source fitting contexts | 48 |
| Candidate heads reconstructed | 576 =480 new +96 reused |
| New selected-head calibrators | 144 |
| Successful prediction rows, domain-OOF | 49347 |
| Successful prediction rows, `g_domain` | 12348 |
| Total successful prediction rows | 61695 |
| Six-system probability values | 370170 |
| New encoder forwards / target evaluations | 0 /0 |
| Supervised execution wall time | 253.644825 seconds |
| Sampled combined supervisor/worker peak RSS | 635604992 bytes,606.160 MiB |
| Owned output before terminal | 111476262 bytes,106.312 MiB |
| Subsequent no-fit saved closure wall time | 141.836 seconds |

Each usable original appears in nine source contexts: three other outer
exclusions crossed with three seeds. Thus61695 is a repeated prediction-row
count, **not**61695 independent images. There are61938 repeated original
denominator instances, including243 repeated technical-failure instances.

The observed supervised terminal satisfies the approved6-hour,4GiB combined
sampled RSS and1GiB owned-output bounds, including the reserved audit space.
Polling bounds are not instantaneous cgroup hard limits. The later standalone
readback verification is accounted separately and did not fit models.

The fixed [verifier](../scripts/run_readout308.py) reconstructed all12 saved
combinations without optimization: candidate epoch/grid selection, selected
head validation BCE, calibrator objectives, policies, artifact hashes,
identities, fit counts, predictions, metrics and conditional bootstrap results.
Its numeric readback tolerance is `rtol=atol=1e-12`; identities and categories
remain exact. A second export check confirmed576 candidate states,61695
prediction rows, no excluded-outer predictions and no per-image identities or
coefficients in the public receipt.

The private worker-completion SHA256 is
`58067b3af7a43995cf22141f6ebaac14f29e5f00b5ee10ad0499ff066334c089`.
The public aggregate closure SHA256 is
`fab44c7460cbf54f78db7be0ae1ecb877101f73b2d64e9ddfbacb8ccb8fef44b`.
The receipt binds the approval, terminal, no-fit closure log, every fit state
and immutable per-fit start/completion ledger.

Private artifacts remain under
`/mnt/e/FAS-private/artifacts/phase1/source_readout308_v1/`:
the original sealed plan, later owner approval, single attempt lock, worker
log/terminal,48 fitted-state files, per-fit checkpoints,12 combination result
and prediction files, and complete worker receipt. Per-image identities,
labels, embeddings and coefficients remain private. All candidate
inner-validation summaries and held-out candidate ranking diagnostics are
public in the aggregate; complete200-epoch validation histories remain in the
private fitted-state files.

## 7. Research decision, without authorizing another experiment

1. **Keep the strong old two-DINO anchor visible.** This small grid did not
   establish an overall ranking improvement; do not silently promote the
   selected successor on the strength of inner BCE or a tiny mean difference.
2. **Do not dismiss OpenCLIP embeddings because zero-shot CLIP failed.** The
   supervised head is now a competent source-development branch, although
   weaker than selected DINO on the primary ranking endpoint.
3. **Do not force a heterogeneous average.** The next defensible proposal
   would test incremental value using a bounded nested source-only fusion
   utility, endpoints including zero CLIP weight, the shared DINO anchor and
   the strong two-DINO comparator. These error-overlap tables do not authorize
   selecting a fusion weight from the evaluation results. Risk supervision
   would require cross-fitting the entire selected pipeline.
4. **Treat security/usability transfer explicitly.** The absolute FA/BFNR
   failures are not solved by the improved CLIP AUROC. A later operating
   policy study must specify its objective, permitted roles and validation
   boundary before fitting or threshold selection.
5. **Q3 remains a research goal, not an outcome of this screen.** A known
   supervised linear probe plus a source-only improvement is not sufficient
   methodological novelty or independent confirmation. A genuinely unseen
   authorized dataset/prospective cohort and a locked subsequent protocol
   remain necessary for revised-method generalization claims.

301's accepted RQ1 inconclusive/RQ2 evidence-against results are unchanged.
No new fusion, risk model, fine-tuning, geometry campaign or target evaluation
is started by this result or its publication.
