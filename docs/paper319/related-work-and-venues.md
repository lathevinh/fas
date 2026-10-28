# Paper319 - Closest work, contribution boundaries and provisional venues

Date checked:2026-10-28. Bounded positioning review, not a systematic survey.
This brief distinguishes verified paper content from inaccessible evidence.
It does not establish a first-of-its-kind claim or guarantee publication.

## 1. Closest primary studies

| Study and primary source | Established overlap | Remaining candidate question / boundary |
|---|---|---|
| Lorenz, George and Marcel, *Foundation Models for Face Presentation Attack Detection: A Unified Linear-Probing Benchmark*, accepted IJCB2026; [arXiv2607.26993](https://arxiv.org/abs/2607.26993), [full text](https://arxiv.org/html/2607.26993v2) |24 frozen encoders; within/cross-dataset PAD; MCIO; DeepPixBiS and FSFM-FAS specialist references. Explicitly single-source, with development-EER thresholds and ACER reporting. | Our proposed multi-source operating analysis is not the same experiment. The examined text does not provide our side-by-side source-policy versus low-FA oracle diagnostic. Frozen probing, specialist inclusion and transfer failure are already covered. |
| George and Marcel, *LoRA-based Adaptation Alone Is Not Enough: Understanding the Limits of Foundation Models for Face PAD*; [arXiv2608.09633](https://arxiv.org/abs/2608.09633), [full text](https://arxiv.org/html/2608.09633v2) |32 foundation models, zero-shot/LoRA evaluation, MCIO, single-source transfer and development-EER-based ACER. Explicitly excludes multi-source LOO/LSD protocols. | Further weakens any generic novelty claim that foundation-model adaptation/transfer can fail. The examined text does not establish the proposed available-policy/oracle low-FA comparison. |
| Gallin-Martel, Feng, Ito and Aoki, *Benchmarking Vision Foundation Models for Domain-Generalizable Face Anti-Spoofing*, CVPRW2026; [arXiv2604.19196](https://arxiv.org/abs/2604.19196), [full text](https://arxiv.org/html/2604.19196v2) |15 pretrained models, DINOv2 registers, MICO train-three/test-one and limited-source settings, augmentation/loss interventions, HTER/AUC. | **Train-three/test-one and register-DINO are not new.** Its examined reporting does not supply the proposed source-derived-policy versus fixed-low-FA oracle comparison. Changing Replay to SiW is not itself novelty. |
| Costa-Pazo et al., *Face presentation attack detection. A comprehensive evaluation of the generalisation problem*, IET Biometrics10(4),408-429,2021; [DOI](https://doi.org/10.1049/bme2.12049) | Verified abstract/metadata describe GRAD-GPAD v2, realistic generalization protocols, attack categorization and demographic analysis. Generalization failure is an established problem. | **Full text could not be retrieved** from the publisher/repository in this preparation. Its exact threshold and low-FA analysis remain unresolved; no absence-of-oracle claim is made for this paper. |

The three recent full texts were examined in the bounded research pass.
Statements about what those texts report are not proofs that no other paper
has studied the same question. Numerical results from them are not imported
as directly matched baselines.

## 2. Narrow contribution and claim-to-evidence map

Proposed contribution paragraph:

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
| Full-range ranking and available operating transfer answer different questions |309 reports stronger supervised CLIP ranking but poor operating transfer | Complete side-by-side matched four-system evaluation; do not imply an AUROC theorem or new phenomenon |
| Threshold movement has different empirical headroom across sources |316: CASIA54/54 oracle-attainable, OULU0/54 for the fixed primary references | Repeat diagnosis on scores from the proposed narrower-source models; do not transfer the old oracle to a new fitted model |
| Adding another representation need not produce a feasible selected policy |314: matched nested families return no policies under the declared constraints | Keep as bounded supporting evidence, not proof that all fusion fails |
| The pattern is relevant beyond these frozen readouts | No completed matched specialist result exists | DeepPixBiS architecture retraining under the exact proposed population |
| A specific journal-level empirical gap remains | Examined closest studies differ in their reported operating analysis | Resolve Costa-Pazo full-text overlap and assess whether the combined evidence is substantial enough; no first-ever claim |

**Positioning decision:** proceed with the bounded paper-completion direction,
not with a claim of established novelty. If the remaining comparison adds
little beyond existing work, make a scope/venue decision instead of adding
another model campaign.

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

1. Full-text threshold methodology of Costa-Pazo et al.2021.
2. Category/year-specific primary ranking evidence for the two candidates.
3. World Scientific's directly verified current scope/charges.
4. Whether the completed matched comparison will provide enough empirical
   insight for the eventual venue; this cannot be known from artifact count.

These gaps are visible in the [integrated package](../319-integrated-paper-completion-package.md)
and [working manuscript](manuscript.md). They are not reasons to fabricate a
novelty claim, download another dataset or postpone all writing.
