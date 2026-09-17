# Research Questions and Hypotheses

## RQ1: Forensic representation

Does DINOv2-Reg encode transferable local evidence for single-image PAD better
than supervised ViT, DINOv2 without registers, and CLIP visual features?

**H1:** Under identical heads and training data, DINOv2-Reg improves mean
cross-domain HTER/ACER and evidence faithfulness.

**Falsification:** no statistically meaningful improvement across the MICO targets.

## RQ2: Complementarity

Does a structured VLM semantic branch make different and useful errors relative
to the forensic branch?

**H2:** The semantic branch recovers a measurable subset of DINO errors involving
global material or geometry, while DINO recovers VLM errors involving fine texture.

**Falsification:** predictions and errors are nearly identical, or one branch strictly
dominates the other in every subgroup.

## RQ3: Evidence consistency

Does ontology-guided consistency outperform ordinary score or feature fusion?

**H3:** Evidence consistency improves unseen-domain and unseen-attack metrics over
an equally tuned learned-fusion baseline.

**Falsification:** learned fusion matches the full model within confidence intervals.

## RQ4: Reliability

Can disagreement identify model errors and unknown attacks?

**H4:** Combined decision/evidence disagreement yields higher error-detection and
OOD AUROC than maximum softmax probability, entropy, and energy score.

**Falsification:** disagreement is not better than these single-model uncertainty
baselines or remains low on shared failures.

## RQ5: Faithfulness

Do evidence maps represent decision-relevant artifacts rather than attractive
visualizations?

**H5:** Removing high-evidence patches degrades the corresponding prediction more
than removing matched random or low-evidence patches; controlled cue insertion
changes the intended concept more than unrelated concepts.

**Falsification:** evidence maps fail deletion, insertion, or counterfactual tests.

## RQ6: Deployment

Can semantic knowledge be retained without running the full VLM on every image?

**H6:** A distilled semantic head retains most of the full model's cross-domain and
selective-prediction gain at substantially lower latency.

**Falsification:** distillation removes the gains or calibration quality.
