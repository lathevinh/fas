# ChatGPT Research Review — Round 8

Date: 2026-09-17

This review evaluates the repository after `21-review-response-round7.md`, with emphasis on the now-stable architecture and the remaining issues in:

- data lineage;
- source-only calibration;
- domain-shift versus attack-shift calibration;
- heterogeneous-rescue estimands;
- probability calibration;
- preregistration logic;
- end-to-end selective PAD accounting.

## Overall assessment

Round 7 was incorporated well.

The architecture is now stable enough that I do not recommend further model redesign.

The remaining problems are mostly specification problems that can still create leakage, unfair comparisons, or ambiguous claims if they are not resolved before Stage 2.

The most important remaining issues are:

1. the risk gate's source-only calibration partition must also be clean with respect to the base predictors;
2. target-time risk-feature normalization is not fully defined;
3. domain-OOF and attack-OOF should be treated as distinct protocols;
4. potential branch rescue must be separated from realized system rescue;
5. the current RQ2 text is stale relative to the updated method.

---

# 1. The gate-calibration partition must also be out-of-sample for the base predictors

The method now proposes:

1. create OOF source records;
2. reserve a subject/video-disjoint source-only gate-calibration partition;
3. fit the final logistic gate on the remaining OOF records;
4. choose the accept threshold on the untouched gate-calibration partition;
5. do not refit afterward.

This is directionally correct.

However, "untouched by the risk gate" is not enough.

Suppose the final DINO/VLM source models were trained using samples from the gate-calibration partition.

Then the gate threshold is selected using:

\[
z(x)
\]

produced by base predictors that have already seen \(x\) during PAD fitting.

Those risk features can be unrealistically clean compared with target inference.

## Requirement

The gate-calibration partition \(G\) should be excluded from:

- DINO PAD-head fitting;
- CLIP visual-head fitting where used;
- branch probability calibration;
- fusion-rule selection;
- risk-gate fitting.

The frozen base predictors should generate predictions on \(G\) genuinely out of sample.

Then \(G\) can select the final accept threshold.

## Important consequence

If the final target-facing DINO/VLM models are later refit using \(G\), the score distribution changes again and the threshold is no longer calibrated to the deployed stack.

Therefore version 1 should use one of two clean approaches.

### Approach A — no final refit

Reserve \(G\), train the final source models without \(G\), calibrate the gate on \(G\), freeze everything, and evaluate targets.

All compared methods must use the same reduced source training data.

### Approach B — fully cross-fitted threshold calibration

Use cross-fitting to obtain out-of-sample gate scores for all source samples without a permanent holdout.

This uses more data but is more complex.

For the first paper, Approach A is easier to audit.

---

# 2. Target-time normalization of risk features is still underspecified

OOF features are normalized using statistics from the corresponding source-side fitting/calibration partition.

That means different folds may use different:

\[
(\mu_j,\sigma_j).
\]

The logistic gate is therefore trained on a mixture of fold-standardized coordinates.

But at target time the predictor is a full source-trained model.

Which normalization statistics are applied to:

\[
z_{\text{target}}?
\]

This must be explicit.

## Simplest recommendation

Do not standardize the already bounded probability features:

\[
\widehat p_D,
\qquad
\widehat p_V,
\qquad
d_{\text{abs}}.
\]

They already live on a common scale.

Standardize only continuous image-quality features:

\[
q(x)
\]

using statistics from the final source fitting data:

\[
q_j'
=
\frac{
q_j-\mu_{j,\text{source}}
}{
\sigma_{j,\text{source}}
}.
\]

This gives the risk gate a much clearer coordinate system.

If all features remain standardized, define exactly which final source statistics transform target features and quantify the resulting OOF-to-final mismatch.

---

# 3. Domain-OOF and attack-OOF are different estimands and should not be written as one protocol

The method currently describes domain-OOF as holding out:

> one complete source domain or attack family.

These are not interchangeable.

## Domain-OOF

Tests whether risk calibration transfers across capture/domain shift:

\[
\text{train risk evidence on domains }A,B
\rightarrow
\text{pseudo-shift }C.
\]

## Attack-OOF

Tests whether risk calibration transfers to a presentation-attack family not used in branch/risk fitting:

\[
\text{known attacks}
\rightarrow
\text{held-out attack family}.
\]

The data structure and failure modes are different.

## Recommendation

Define them as separate protocols:

\[
R_{\text{domain-OOF}}
\]

and:

\[
R_{\text{attack-OOF}}.
\]

For strict MICO, domain-OOF is the natural primary construction.

For SiW-M downstream-unseen attacks, attack-family OOF should be constructed according to the official known/held-out attack protocol where possible.

A mixed domain+attack OOF gate can be a secondary experiment.

Do not claim that a gate trained only with domain pseudo-shifts has already been calibrated for unseen attack-family shift.

---

# 4. Move the stronger same-family representation control into Stage 1 if the cross-foundation title is retained

The shared-encoder multi-head DINO control is correctly labeled weak.

Two heads on one frozen representation are not a strong test of whether cross-foundation diversity exceeds same-family representation diversity.

The stronger control:

\[
DINOv2\text{-Reg}
+
DINOv2\text{-plain}
\]

is currently optional.

Because both backbones can be frozen and their features cached sequentially, this control is relatively affordable compared with full fine-tuning.

## Recommendation

If the final title retains:

> Cross-Foundation ...

make:

\[
DINOv2\text{-Reg}+DINOv2
\]

a required Stage-1 confirmatory control.

Keep the shared-encoder head-diversity control as a cheap sanity check.

A cross-foundation-specific claim should not rest only on a deliberately weak homogeneous baseline.

---

# 5. Separate potential branch rescue from realized system rescue

Current Stage-1 metrics include:

\[
FARR
=
P(
VLM\text{ blocks attack}
\mid
DINO\text{ false accepts}
).
\]

This is a useful measure of **potential complementarity**.

But the deployed system does not simply replace DINO with the VLM whenever DINO is wrong.

The deployed post-VLM rule is:

\[
g_{\text{ref}}
=
\text{calibrated average}.
\]

Therefore two different rescue quantities are needed.

## Potential VLM rescue

\[
FARR_{\text{VLM}}
=
P(
VLM\text{ correct}
\mid
DINO\text{ false accept}
).
\]

This measures branch complementarity.

## Realized fusion rescue

\[
FARR_{g}
=
P(
g_{\text{ref}}\text{ blocks attack}
\mid
DINO\text{ false accept}
).
\]

This measures actual recoverable benefit under the proposed system.

A VLM can have high potential rescue while calibrated averaging fails to exploit it.

The paper should report both.

The same distinction should be made for general recoverable error fraction:

\[
REF_{\text{VLM}}
\]

versus:

\[
REF_g.
\]

---

# 6. Heterogeneity advantage should be a paired rescue comparison

The current estimand is:

\[
\Delta_{\text{hetero}}
=
FARR(DINO,VLM)
-
FARR(DINO,DINO_2).
\]

This is good, but both rescue methods are evaluated on the **same set of DINO false accepts**.

Therefore the comparison should exploit pairing.

For each DINO false-accept event \(i\), define:

\[
r_i^V
=
\mathbf 1[
VLM\text{ rescues }i
],
\]

and:

\[
r_i^H
=
\mathbf 1[
DINO_2\text{ rescues }i
].
\]

Then:

\[
\Delta_{\text{hetero}}
=
\frac{1}{N_{FA}}
\sum_i
(r_i^V-r_i^H).
\]

Use:

- paired subject/video bootstrap;
- exact McNemar-style analysis where event counts are small.

This is stronger than subtracting two independently reported FARR confidence intervals.

Also report the paired realized-fusion version if both heterogeneous and homogeneous ensembles have explicit fusion rules.

---

# 7. The preregistration hierarchy now needs to be made explicit

The project has accumulated several go/no-go quantities:

- branch competence;
- class-conditional oracle gain;
- REF;
- FARR lower confidence bound;
- minimum false-accept count;
- \(\Delta_{\text{hetero}}\);
- \(\Delta_{\text{dis}}\);
- Stage-2 error AUPR;
- excess-AURC.

This is scientifically useful, but without a hierarchy it can create another form of researcher flexibility.

## Recommendation

Define three different decision levels.

### Level 1 — continue the dual-branch project

For example:

\[
\text{competent branches}
\land
\text{realized rescue above threshold}.
\]

### Level 2 — permit the `cross-foundation` claim

Require:

\[
\Delta_{\text{hetero}}>0
\]

under the preregistered confirmatory analysis.

### Level 3 — permit the `disagreement` claim

Require:

\[
\Delta_{\text{dis}}>0
\]

over capacity-matched probability-only risk models.

This produces clean reframing rules.

A project may pass Level 1 while failing Level 2 or Level 3.

That should weaken the title, not necessarily kill the whole study.

---

# 8. Branch probability calibration needs a clearly defined source calibration distribution

The training sampler is intentionally hierarchical and approximately balances:

- datasets;
- bona fide versus attack;
- attack families.

But the actual evaluation datasets have different class and domain prevalences.

Probability calibration depends on the distribution used to fit the calibrator.

Therefore source calibration must specify whether it uses:

- pooled natural source prevalence;
- equal class weighting;
- equal domain weighting;
- hierarchical weighting matching training.

Otherwise two researchers can obtain materially different:

\[
\widehat p_D,\widehat p_V
\]

from the same logits.

## Recommendation

For cross-domain PAD, use a preregistered domain-balanced source calibration objective.

For example:

1. compute calibration loss separately per source domain;
2. average domains equally.

This prevents a large source dataset from dominating temperature/affine calibration.

Record the exact calibration weighting policy in configs.

---

# 9. Temperature scaling without a bias term may be too restrictive for the VLM semantic logit

The VLM branch defines:

\[
\ell_V
=
s_{\text{spoof}}-s_{\text{live}}
\]

and then:

\[
\widehat p_V
=
\sigma(\ell_V/T_V).
\]

A temperature changes scale but not offset.

If the frozen prompt bank has an intrinsic live/spoof bias, temperature scaling cannot correct it.

For example, if the semantic logit is systematically shifted:

\[
\ell_V'
=
\ell_V+b,
\]

temperature alone cannot estimate \(b\).

## Recommendation

Evaluate a simple affine logistic calibration:

\[
\widehat p
=
\sigma(a\ell+b),
\]

with:

\[
a>0
\]

if monotonicity is desired.

This is ordinary Platt-style calibration.

Compare:

- temperature-only;
- affine logistic calibration.

Choose the primary rule from source-only evidence and freeze it before confirmatory targets.

If temperature-only is retained for simplicity, explicitly acknowledge that decision thresholds absorb residual offset but probabilistic calibration may remain imperfect.

This matters because the method later averages calibrated probabilities.

---

# 10. Cross-foundation risk must show incremental value over quality-only and single-branch learned-risk baselines

The risk model includes:

\[
q(x)
\]

with blur, luminance, contrast, face size, and detector confidence.

A large gain could come almost entirely from obvious image-quality failures rather than cross-foundation information.

The current plan includes with/without-\(q\) tests, but the most informative baseline decomposition should be explicit.

Compare:

\[
R_q
=
\operatorname{LogReg}(q),
\]

\[
R_D
=
\operatorname{LogReg}(\widehat p_D,q),
\]

\[
R_V
=
\operatorname{LogReg}(\widehat p_V,q),
\]

\[
R_{DV}
=
\operatorname{LogReg}(\widehat p_D,\widehat p_V,q),
\]

and:

\[
R_{DVd}
=
\operatorname{LogReg}(\widehat p_D,\widehat p_V,d,q).
\]

This creates a clean decomposition:

### cross-foundation probability gain

\[
\Delta_{CF}
=
Perf(R_{DV})
-
\max(
Perf(R_D),Perf(R_V)
).
\]

### explicit disagreement gain

\[
\Delta_{dis}
=
Perf(R_{DVd})
-
Perf(R_{DV}).
\]

These two quantities map directly to two different claims.

---

# 11. RQ2 is now stale relative to the method

RQ2 still introduces the raw baseline as:

\[
D(x)=D_{JS}(p_D\|p_V)
\]

and H2 says:

> raw or source-calibrated disagreement improves ...

But the current primary method has already changed to:

\[
d_{\text{abs}}
=
|\widehat p_D-\widehat p_V|
\]

inside a fixed logistic failure-risk model.

JS is now only an ablation.

## Recommendation

Rewrite RQ2 around the actual proposed method.

For example:

> Can a source-only cross-fitted risk model using independently calibrated cross-foundation predictions improve failure detection under domain and attack shift, and does an explicit disagreement feature add incremental value beyond the two branch probabilities themselves?

Then split H2 into:

### H2a — cross-foundation risk value

\[
R_{DV}
>
R_D,R_V.
\]

### H2b — explicit disagreement value

\[
R_{DVd}
>
R_{DV}.
\]

This perfectly matches the preregistered reframing rule.

---

# 12. End-to-end bona-fide failure should include abstention

The protocol carefully defines:

\[
FA_{\text{end2end}}
=
\frac{
N_{\text{attack accepted live}}
}{
N_{\text{attack total}}
}.
\]

Good.

However, the user-side counterpart is missing.

With \(K=1\), abstention is a terminal non-accept outcome.

For a bona-fide user, both:

- explicit spoof classification;
- abstention;

cause authentication failure.

## Recommendation

Add:

\[
BFNR_{\text{end2end}}
=
\frac{
N_{\text{bona fide not accepted}}
}{
N_{\text{bona fide total}}
}.
\]

Equivalently:

\[
BFAR_{\text{end2end}}
=
\frac{
N_{\text{bona fide accepted}}
}{
N_{\text{bona fide total}}
}.
\]

This is more deployment-relevant than covered-sample BPCER alone.

The final security/usability trade-off should therefore include:

\[
FA_{\text{end2end}}
\]

versus:

\[
BFNR_{\text{end2end}}.
\]

---

# 13. The source-only split roles should be documented as a data-lineage table

The source pipeline now has many distinct roles:

- branch training;
- branch probability calibration;
- OOF pseudo-shift prediction;
- risk-gate fitting;
- gate-threshold calibration;
- prompt calibration;
- Stage-1 preregistration statistics.

This is now complex enough that prose alone will be hard to audit.

## Recommendation

Add a table such as:

| Partition | DINO fit | VLM fit | branch calibration | risk fit | gate threshold | preregistration |
|---|---:|---:|---:|---:|---:|---:|
| source train | yes | frozen/head where relevant | no | no | no | no |
| branch-calib | no | no | yes | no | no | no |
| OOF pseudo-shift | no | no | fold-specific | yes-record generation | no | yes |
| gate-calib | no | no | no | no | yes | no |
| target | no | no | no | no | no | evaluation only |

The exact table can differ, but every sample must have one clearly defined role in each stage.

This will prevent subtle reuse errors when implementation begins.

---

# 14. The exact fixed prompt bank and VLM checkpoint must become versioned artifacts

The repository says the core prompt bank is immutable, but the exact strings are not yet part of the method file.

The exact OpenCLIP/SigLIP checkpoint is also still an open decision.

For reproducibility, these should become explicit versioned configuration artifacts before confirmatory evaluation.

For example:

```text
configs/
  prompts_core_v1.yaml
  prompts_aux_v1.yaml
  vlm_checkpoint_v1.yaml
```

The core prompt file should include:

- exact prompt text;
- class assignment;
- template formatting;
- ensemble weighting;
- text preprocessing.

The checkpoint config should include:

- model name;
- pretrained weight identifier;
- input resolution;
- normalization;
- tokenizer/text preprocessing.

If several VLM candidates are explored on the pilot target, define the candidate set before looking at pilot results and freeze the selected checkpoint before the three confirmatory MICO targets.

---

# 15. The stronger same-family control is especially important because the current title is conditional, not yet earned

The charter correctly says the title will weaken if:

- explicit disagreement adds no incremental value;
- heterogeneous rescue does not beat same-family diversity.

That is good.

However, the current cross-foundation-specific success criterion still relies primarily on the shared-encoder DINO control.

For a strong final claim, the hierarchy should be:

### sanity control

\[
DINO_{\text{Reg}} + DINO_{\text{Reg-head2}}
\]

### strong same-family control

\[
DINO_{\text{Reg}} + DINO_{\text{plain}}
\]

### heterogeneous system

\[
DINO_{\text{Reg}} + VLM.
\]

If the heterogeneous pair only beats the first but not the second, the evidence for a specifically cross-foundation advantage is weak.

Because frozen feature extraction is relatively cheap, I recommend moving the strong same-family control into the confirmatory Stage-1 package rather than leaving it as an optional late ablation.

---

# Recommended synchronization fixes

Before Stage 2 implementation:

1. rewrite RQ2 to match the actual absolute-difference/logistic risk method;
2. define source calibration weighting for branch probabilities;
3. test temperature-only versus affine calibration;
4. define target-time normalization of risk features;
5. separate domain-OOF and attack-OOF protocols;
6. ensure the gate-calibration partition is also out-of-sample for base predictors;
7. distinguish potential VLM rescue from realized fusion rescue;
8. use paired inference for heterogeneity advantage;
9. define explicit go/no-go versus title-reframing criteria;
10. add quality-only and single-branch learned-risk baselines;
11. add an end-to-end bona-fide non-accept metric;
12. add a source data-lineage table;
13. version the exact prompt bank and VLM checkpoint;
14. promote the stronger DINO-Reg + DINO-plain control if the cross-foundation title is retained.

---

# Final recommendation

The project remains ready for Stage 1.

The most useful Stage-1 outputs are now not only:

\[
FARR_{\text{VLM}}
\]

and:

\[
\Delta_{\text{hetero}},
\]

but also the realized system quantity:

\[
FARR_g
=
P(
g_{\text{ref}}\text{ corrects a DINO false accept}
\mid
DINO\text{ false accept}
).
\]

The core evidence chain should become:

\[
\boxed{
\text{DINO fails}
\rightarrow
\text{VLM has recoverable information}
\rightarrow
\text{fusion actually exploits it}
\rightarrow
\text{heterogeneous rescue exceeds same-family rescue}
}
\]

For Stage 2, the clean claim decomposition should be:

\[
\boxed{
\Delta_{CF}
=
\text{gain from having both foundation predictions}
}
\]

and:

\[
\boxed{
\Delta_{dis}
=
\text{additional gain from explicitly engineering disagreement}
}
\]

If:

\[
\Delta_{CF}>0
\]

but:

\[
\Delta_{dis}\approx0,
\]

the project can still support a strong cross-foundation selective-failure-prediction paper, but the title should stop emphasizing disagreement.

If the heterogeneous pair does not outperform a strong same-family representation control, the paper should be reframed as a broader selective-ensemble PAD study.
