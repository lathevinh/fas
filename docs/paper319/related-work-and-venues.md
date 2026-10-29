# Paper319 - Closest work, contribution boundaries and provisional venues

Literature/venue sources last checked:2026-10-28.
Empirical claim map updated:2026-10-29 after the completed323 comparison.
Bounded positioning review, not a systematic survey; this update does not
claim a new retrieval or ranking-provider verification.
This brief distinguishes verified paper content from inaccessible evidence.
It does not establish a first-of-its-kind claim or guarantee publication.

## 1. Closest primary studies

| Study and primary source | Established overlap | Remaining candidate question / boundary |
|---|---|---|
| Lorenz, George and Marcel, *Foundation Models for Face Presentation Attack Detection: A Unified Linear-Probing Benchmark*, accepted IJCB2026; [arXiv2607.26993](https://arxiv.org/abs/2607.26993), [full text](https://arxiv.org/html/2607.26993v2) |24 frozen encoders; within/cross-dataset PAD; MCIO; DeepPixBiS and FSFM-FAS specialist references. Explicitly single-source, with development-EER thresholds and ACER reporting. | Our proposed multi-source operating analysis is not the same experiment. The examined text does not provide our side-by-side source-policy versus low-FA oracle diagnostic. Frozen probing, specialist inclusion and transfer failure are already covered. |
| Lorenz, George and Marcel, *LoRA-based Adaptation Alone Is Not Enough: Understanding the Limits of Foundation Models for Face PAD*; [arXiv2608.09633](https://arxiv.org/abs/2608.09633), [full text](https://arxiv.org/html/2608.09633v2) |32 foundation models, zero-shot/LoRA evaluation, MCIO, single-source transfer and development-EER-based ACER. Explicitly excludes multi-source LOO/LSD protocols. | Further weakens any generic novelty claim that foundation-model adaptation/transfer can fail. The examined text does not establish the proposed available-policy/oracle low-FA comparison. |
| Feng, Gallin-Martel, Ito and Aoki, *Benchmarking Vision Foundation Models for Domain-Generalizable Face Anti-Spoofing*, CVPRW2026; [arXiv2604.19196](https://arxiv.org/abs/2604.19196), [full text](https://arxiv.org/html/2604.19196v2) |15 pretrained models, DINOv2 registers, MICO train-three/test-one and limited-source settings, augmentation/loss interventions, HTER/AUC. | **Train-three/test-one and register-DINO are not new.** Its examined reporting does not supply the proposed source-derived-policy versus fixed-low-FA oracle comparison. Changing Replay to SiW is not itself novelty. |
| Costa-Pazo et al., *Face presentation attack detection. A comprehensive evaluation of the generalisation problem*, IET Biometrics10(4),408-429,2021; [DOI](https://doi.org/10.1049/bme2.12049), [full text](https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/bme2.12049) | GRAD-GPAD v2, realistic generalization protocols, attack categorization and demographic analysis. Review320 retrieved the full text and verifies constrained operating analysis including APCER at BPCER10% and working-point curves. | Constrained ROC analysis and moving beyond aggregate metrics are already covered. The narrower proposed question pairs the available source-derived threshold with an evaluation-label oracle under the same attack-FA constraint. Exact equivalence or absence of that pipeline has not been established; no absence-of-oracle claim is made. |

The three recent full texts were examined in the bounded research pass.
Statements about what those texts report are not proofs that no other paper
has studied the same question. Numerical results from them are not imported
as directly matched baselines.

The Costa-Pazo status above incorporates the explicit full-text evidence in
[review320](../320-review-doc319-and-paper319-preparation-and-manuscript.md).
The implementation host still received publisher403/repository retrieval
failures during its follow-up; this is not represented as an independent
full-text reread or evidence that the paper lacks constrained analysis.
The [authors' framework repository](https://github.com/acostapazo/gradgpad)
independently confirms its bibliographic record and generalization scope.
No unverified quotation or table number from search summaries is adopted.
Primary arXiv citation-author metadata confirms both corrected author orders.

## 2. Narrow contribution and claim-to-evidence map

Evidence-backed contribution candidate:

> We characterize low-false-acceptance operating transfer for a small fixed
> frozen-feature PAD system set under an explicitly defined multi-source
> protocol. We report available source-calibrated operating policies alongside
> evaluation-label oracle headroom on the same saved scores, distinguishing
> threshold-placement headroom from insufficient empirical low-FA separation.
> A matched specialist comparison and conditional grouped uncertainty
> contextualize these findings; a completed nested fusion study separately
> preserves missing-policy outcomes.

This is an empirical contribution candidate, not a new ROC algorithm,
calibration method, universal impossibility result or proposed deployment
solution. A conjunction of familiar components is not sufficient novelty
without a useful, defensible empirical answer.

| Intended statement | Current evidence | What remains |
|---|---|---|
| Full-range ranking and available operating transfer answer different questions | Completed323:0/48 primary source-policy joint-utility cases, despite usable AUROC up to99.94% in the descriptive seed means | Do not imply an AUROC theorem or a newly discovered general phenomenon |
| Threshold movement has different empirical headroom across sources and systems | Completed323:21/48 primary cases are oracle-attainable;27/48 are not. CASIA11/12, MSU7/12, OULU3/12, SiW0/12. The OULU specialist supplies all three attainable OULU cases | Same stored-score diagnostic, not target-label-free recoverable gain or a universal dataset impossibility |
| Adding another representation need not produce a feasible selected policy |314: matched nested families return no policies under the declared constraints | Keep as bounded supporting evidence, not proof that all fusion fails |
| The available-threshold problem is not confined to frozen readouts | Completed matched specialist:0/12 primary source-policy joint-utility cases; oracle attainment varies by dataset and seed, including3/3 on OULU | One researcher-fixed architecture recipe, not causal architecture isolation, exact original-paper reproduction or universality |
| A specific journal-level empirical gap remains | Examined closest studies differ in their reported operating analysis; Costa-Pazo already includes constrained points/curves | Keep the narrower paired policy/oracle positioning and assess empirical substance; exact pipeline overlap remains unresolved, with no first-ever claim |

**Positioning decision:** the completed comparison now supplies the missing
specialist context and differentiates operating-threshold failure from
fixed-score low-FA limitations. The stronger defensible narrative is that
the diagnosis changes with representation and target: OULU is not inherently
oracle-infeasible, and neither CLIP nor the specialist is universally best.
This is empirical substance for a manuscript, not established novelty.
Keep CLIP as an informative comparator; there is no new official-partition
DINO-CLIP fusion result or evidence to promote it as a fusion remedy.
Proceed to critique and a scope/venue decision, not another model campaign.
See [report324](../324-completed-comparison-results-and-paper-update.md) and
the [full seed-level tables](../../results/phase1/paper324-primary-tables-v1.md).

## 3. At most two provisional venue candidates

The preparation attempted publisher and ranking-provider retrieval.
SCImago/Scopus ranking pages were inaccessible in this environment.
Secondary pages/search summaries are not sufficient here to establish a
specific **provider + year + category + quartile** tuple.

| Candidate | Scope/access evidence | Ranking and cost status |
|---|---|---|
| *International Journal of Biometrics*, Inderscience; [publisher](https://www.inderscience.com/jhome.php?jcode=ijbm) | Publisher scope covers theoretical/practical biometrics and human identification/verification, with original articles and case studies. Publisher information describes a subscription route without publication charges unless optional OA is requested. | Q3 is reported by secondary listings, but exact SJR year/category/Q3 pairing is **not verified**. Do not equate its index coverage with JCR quartile or infer absence of JIF from ESCI. Recheck current author charges at submission. |
| *International Journal of Pattern Recognition and Artificial Intelligence*, World Scientific; [publisher](https://www.worldscientific.com/worldscinet/ijprai) | Pattern-recognition/AI scope is relevant in principle; detailed scope/access evidence in this pass is secondary because the publisher endpoint was inaccessible. | Q3 is reported by secondary listings, but exact provider/year/category is **not verified**. OA price, default publication charges and current indexing are **not independently verified**; no fee estimate is adopted. |

These are a shortlist, **not two certified-Q3 recommendations** and not a
locked submission decision. No amount of SJR/CiteScore agreement in a search
summary proves a category-specific quartile. A best-quartile label does not
assign that quartile to every listed category. ESCI inclusion does not imply
absence of a Journal Impact Factor.

The directly retrieved secondary pages were
[SLogix IJBM](https://slogix.in/research/journals/international-journal-of-biometrics/)
and [SLogix IJPRAI](https://slogix.in/research/journals/international-journal-of-pattern-recognition-and-artificial-intelligence/).
Their2025 labels refer to impact-factor/CiteScore fields, not an explicitly
dated SJR quartile block. IJBM's displayed Q3 category also conflicts with
its separate subject-category list. Thus these pages do not establish the
required year/category-specific Q3 classification. No unsupported APC or
index-to-JIF inference is adopted from search-generated summaries.

Before selecting the venue, obtain an accessible provider record or
institutional ranking evidence naming the relevant year and category,
and verify the publisher's then-current scope, article type and charges.
If the owner's institutional requirement is specifically JCR rather than
SJR, check JCR directly; do not substitute a Scopus/SCImago classification.
No payment or submission is authorized by this package.

## 4. Explicit unresolved facts

1. Exact pipeline equivalence with Costa-Pazo et al.2021, not whether that
   work already contains constrained operating analysis (review320 confirms it).
2. Category/year-specific primary ranking evidence for the two candidates.
3. World Scientific's directly verified current scope/charges.
4. Whether the now-completed paired-policy/oracle evidence provides enough
   incremental insight for the eventual venue. Positive specialist OULU
   oracle headroom and universal primary available-policy failure sharpen
   the empirical account, but neither completed computation nor artifact
   count establishes sufficient novelty.

These gaps are visible in the [integrated package](../319-integrated-paper-completion-package.md)
and [working manuscript](manuscript.md). They are not reasons to fabricate a
novelty claim, download another dataset or postpone all writing.
