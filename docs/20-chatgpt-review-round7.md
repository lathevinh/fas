# ChatGPT Research Review — Round 7

Date: 2026-09-17

This review evaluates the repository after `19-review-response-round6.md`, focusing on the latest:

- `02-research-questions.md`
- `03-method.md`
- `04-data-and-protocols.md`
- `05-experiment-plan.md`
- `06-risks-and-decisions.md`
- `references/reading-list.md`

## Overall assessment

Round 6 was incorporated carefully.

The repository now has:

- a fixed core semantic prompt bank;
- a deterministic calibrated-average post-VLM rule;
- fixed-error risk-estimator comparisons;
- second-level meta-OOF threshold selection;
- homogeneous and CLIP-visual controls;
- finite-sample APCER confidence bounds;
- end-to-end detector-failure accounting;
- deterministic single-image frame selection.

The architecture remains sufficiently stable.

The remaining concerns are now mostly about **mathematical definition, causal attribution, score comparability, and whether the title's emphasis on disagreement is actually supported by the planned experiment**.

---

# 1. The VLM pipeline currently risks double calibration

The design principle defines:

\[
\widehat p_V=\operatorname{Cal}_V(p_V).
\]

But the VLM section already defines:

\[
p_V(\mathrm{spoof}\mid x)
=
\sigma
\left(
\frac{
s_{\mathrm{spoof}}(x)-s_{\mathrm{live}}(x)
}{
T
}
\right),
\]

where \(T\) is fitted on source calibration data.

If \(T\) is a temperature-calibration parameter, then applying another:

\[
\operatorname{Cal}_V
\]

afterward creates an ambiguous two-stage calibration pipeline.

## Recommendation

Define a raw semantic logit:

\[
\ell_V(x)
=
s_{\mathrm{spoof}}(x)-s_{\mathrm{live}}(x).
\]

Then let the branch calibration be exactly:

\[
\widehat p_V(x)
=
\sigma
\left(
\frac{\ell_V(x)}{T_V}
\right).
\]

In other words:

\[
\boxed{
T_V \equiv \operatorname{Cal}_V
}
\]

for the primary VLM branch.

Likewise, define the DINO branch from a raw binary logit:

\[
\ell_D(x)
\]

and calibrate:

\[
\widehat p_D(x)
=
\sigma
\left(
\frac{\ell_D(x)}{T_D}
\right)
\]

or whatever preregistered source-only calibration method is selected.

This removes ambiguity about whether probabilities are being calibrated twice.

---

# 2. The fixed-prompt protocol and the VLM training-order text are still inconsistent

The protocol now correctly says that the fixed semantic prompt bank is primary.

However, the VLM training order still says approximately:

> select prompt templates and temperature using source validation.

That wording suggests the primary prompt templates themselves are source-selected.

This conflicts with the intended unseen-transfer setting.

## Recommendation

Rewrite the primary procedure as:

1. preregister and freeze \(T_{\text{core}}\);
2. freeze image and text encoders;
3. fit only branch calibration \(T_V\) on source calibration data;
4. keep source-tuned template/weight selection as a labeled ablation;
5. keep \(T_{\text{aux}}\) separate from the binary PAD score.

This should be synchronized across method, protocol, and experiment plan.

---

# 3. The paper title requires incremental evidence that "disagreement" matters

The current title is centered on:

> Cross-Foundation Disagreement.

But:

\[
d(x)
=
D_{JS}(\widehat p_D\|\widehat p_V)
\]

is a deterministic function of:

\[
(\widehat p_D,\widehat p_V).
\]

Therefore disagreement contains no new information in an information-theoretic sense once both probabilities are already given to a sufficiently expressive risk model.

A logistic model may benefit from JS because JS supplies a useful nonlinear basis. An MLP may learn a similar interaction itself.

## Required novelty test

Compare:

\[
R_1=
\operatorname{LogReg}(\widehat p_D,\widehat p_V,q),
\]

\[
R_2=
\operatorname{LogReg}(\widehat p_D,\widehat p_V,d,q),
\]

\[
R_3=
\operatorname{MLP}(\widehat p_D,\widehat p_V,q),
\]

and:

\[
R_4=
\operatorname{MLP}(\widehat p_D,\widehat p_V,d,q).
\]

Then measure the incremental gain from explicit disagreement:

\[
\Delta_{\mathrm{JS}}
=
Perf(R_{\text{with JS}})
-
Perf(R_{\text{without JS}}).
\]

## Novelty kill condition

If:

\[
\Delta_{\mathrm{JS}}\approx 0
\]

for capacity-matched nonlinear models, then the paper should not claim that explicit disagreement is the key algorithmic mechanism.

The framing should shift toward:

> cross-foundation selective failure prediction

rather than:

> disagreement-based failure prediction.

This is important because the current title and novelty statement put substantial weight on disagreement itself.

---

# 4. Add simpler disagreement scores before treating JS as special

JS is reasonable, but there is currently no reason to assume it is the best disagreement operator.

Mandatory simple baselines should include:

\[
d_{\mathrm{abs}}
=
|\widehat p_D-\widehat p_V|,
\]

hard decision disagreement:

\[
d_{\mathrm{hard}}
=
\mathbf 1[
\hat y_D\neq\hat y_V
],
\]

and optionally log-odds disagreement:

\[
d_{\mathrm{logit}}
=
\left|
\operatorname{logit}(\widehat p_D)
-
\operatorname{logit}(\widehat p_V)
\right|.
\]

If absolute probability difference performs as well as JS, use the simpler score in the final method.

The paper should not imply novelty in the mathematical choice of JS unless data justify it.

---

# 5. Stage 3 still mixes classifier and confidence comparisons

The experiment plan still contains an exit criterion similar to:

> calibrated disagreement beats learned fusion and entropy/MSP/energy.

This mixes two different objects.

A learned fusion method changes:

\[
g(x),
\]

the classifier.

Disagreement, entropy, MSP, and the risk model change:

\[
s(x),
\]

the confidence/risk score.

These are not direct substitutes.

## Recommendation

Keep the separation introduced in Stage 2 all the way through Stage 3.

### Classifier comparison

Compare:

- DINO;
- VLM;
- calibrated average;
- learned fusion.

### Risk-score comparison for fixed \(g_{\text{ref}}\)

Compare:

- fused MSP;
- fused entropy;
- absolute disagreement;
- JS disagreement;
- Mahalanobis-derived confidence where defined;
- learned failure-risk score.

### End-to-end system comparison

Compare complete selective systems separately.

Remove wording that says a risk score "beats learned fusion" unless the metric is explicitly end-to-end system performance.

---

# 6. The homogeneous two-head control is weaker than it appears

Two independently trained heads on one frozen deterministic DINO representation are described as a homogeneous DINO ensemble control.

This is useful, but if the head is linear or nearly convex and both heads see almost identical data, they may converge to almost the same function.

Then the control artificially has very low diversity.

This would make:

\[
DINO+VLM
\]

look more special than it really is.

## Recommendation

Rename the minimum control:

> shared-encoder head-diversity control

rather than a definitive homogeneous ensemble.

Use at least:

- independent subject/video bootstrap samples;
- independent augmentation streams;
- independent head initialization;
- preferably a small nonlinear head.

A stronger same-family representation control should be promoted if compute permits, for example:

\[
DINOv2\text{-Reg}
+
DINOv2\text{ without Registers}.
\]

Since both backbones can be frozen and features cached sequentially, this may be feasible even on the RTX 4080.

The paper's central cross-foundation claim becomes much stronger if:

\[
DINO_{\mathrm{Reg}}+VLM
\]

provides more security-useful rescue than:

\[
DINO_{\mathrm{Reg}}+DINO_{\mathrm{plain}}.
\]

---

# 7. Meta-OOF threshold selection has a remaining score-scale problem after final refit

The current procedure is:

1. fit risk model on two OOF domains;
2. predict the third;
3. concatenate meta-OOF predictions;
4. select accept threshold \(\rho\);
5. refit the logistic gate on all OOF source records;
6. apply the same frozen threshold to the refitted gate.

The problem is subtle.

The numerical risk-score scale of:

\[
r^{(-A)}(x),r^{(-B)}(x),r^{(-C)}(x)
\]

is not guaranteed to equal the score scale of the final:

\[
r^{(\mathrm{all})}(x).
\]

Even logistic probability outputs can shift after refitting on all domains.

Therefore a threshold learned on the cross-fitted models may not correspond to the same acceptance semantics after refitting.

## Recommendation

Choose one of the following.

### Option A — reserve a source-only gate-calibration split

After the final gate is fitted, evaluate it on a source subset that was never used to fit that final gate and use only that subset to select \(\rho\).

This is the cleanest if enough source data exist.

### Option B — use an ensemble of meta-risk gates

Avoid a final single refit and use an ensemble of the cross-fitted risk gates whose score semantics were used during threshold selection.

### Option C — threshold by a preregistered source coverage quantile

If probability calibration is not central, select a target source coverage level from meta-OOF and map it onto the final gate score distribution using source-only data.

Whichever option is chosen, the current assumption that a probability threshold transfers unchanged after refitting should be tested rather than assumed.

---

# 8. The primary risk-feature set is still not fully frozen

The current risk vector includes:

\[
[
\widehat p_D,
\widehat p_V,
d,
H_D,
H_V,
E_D,
E_V,
q
].
\]

However:

- entropy is deterministic from the probabilities;
- energy is marked optional;
- energy for a prompt-derived VLM needs a precise raw-logit definition;
- adding/removing these terms creates researcher flexibility.

## Recommendation

Freeze one primary version now.

A simple primary feature vector is:

\[
\boxed{
z_{\mathrm{primary}}
=
[
\widehat p_D,
\widehat p_V,
d,
q
]
}
\]

with:

\[
q=
[
\text{blur},
\text{luminance},
\text{contrast},
\text{face-area ratio},
\text{detector confidence}
].
\]

Then treat:

- entropy;
- DINO energy;
- VLM energy;
- Mahalanobis;

as ablations/baselines.

If energy remains in the primary model, define exactly which raw logits generate it for both branches.

---

# 9. Overall error AUPR may hide the security-critical failure type

The primary Stage-2 endpoint is prediction-error AUPR.

But PAD errors are asymmetric.

A risk estimator could detect many bona-fide false rejects while missing attack false accepts and still achieve a strong overall error AUPR.

## Recommendation

Keep overall error AUPR as the general failure-detection endpoint, but add mandatory class-conditional failure endpoints.

### Attack-conditional false-accept detection

Among attack samples:

\[
e_{FA}(x)
=
\mathbf 1[
g_{\text{ref}}(x)=\text{live}
].
\]

Report:

\[
AUPR_{FA}
\]

for ranking false accepts above correctly blocked attacks.

### Bona-fide false-reject detection

Among bona-fide samples:

\[
e_{FR}(x)
=
\mathbf 1[
g_{\text{ref}}(x)=\text{spoof}
].
\]

Report:

\[
AUPR_{FR}.
\]

For a security-oriented PAD paper:

\[
AUPR_{FA}
\]

is especially important.

This aligns the reliability claim with the threat model rather than treating all classification errors as equally important.

---

# 10. Standard excess-AURC can still hide class-asymmetric rejection behavior

The protocol already reports:

- attack coverage;
- bona-fide coverage;
- covered APCER/BPCER.

That is good.

However, a single global AURC or excess-AURC can still reward a selector that rejects one class disproportionately.

Recent selective-classification work has explicitly highlighted this limitation and proposed class-aware risk-coverage evaluation.

## Recommendation

In addition to global excess-AURC, report:

- attack-only risk-coverage curve;
- bona-fide-only risk-coverage curve;
- class-averaged AURC or an equivalent class-balanced summary.

Do not let one global selective metric dominate the security conclusion.

---

# 11. The low-APCER confidence-bound policy may be infeasible on MICO at the independent-video level

The protocol correctly proposes:

\[
UCB_{95\%}(APCER_d)\le\alpha.
\]

But the effective independent sample size is approximately the number of independent attack videos/transactions, not the number of highly correlated frames.

After zero observed false accepts, a rough 95% upper bound is:

\[
\frac{3}{N}.
\]

Therefore approximately:

\[
N\gtrsim 300
\]

independent attack trials are needed even to support an upper bound near:

\[
1\%.
\]

For:

\[
0.5\%
\]

the requirement is roughly twice as large.

Many classical FAS source domains may not provide that many independent attack videos in a validation split.

## Recommendation

Before preregistering:

\[
\alpha\in\{0.5\%,1\%,5\%\},
\]

compute the actual independent attack counts available in each source calibration domain.

If the counts are insufficient:

- use 5% as the statistically supported primary research operating point;
- report 1% and 0.5% as nominal diagnostic operating points;
- never create artificial sample size by treating multiple frames from one video as independent attack trials.

This should be decided from dataset manifests before Stage 1/2 claims are locked.

---

# 12. "Middle valid frame" must not mean "middle face-detectable frame"

The strict single-image protocol uses the middle valid frame.

The face-detector policy separately says detector failure maps to terminal abstention.

These rules become inconsistent if "valid" means:

> a frame where the face detector succeeds.

That would silently skip a detector failure and search for an easier frame.

## Recommendation

Define `valid` only at the file/protocol level:

- frame decodes successfully;
- frame belongs to the official evaluation interval.

Select the temporal frame **before face detection**.

Then:

\[
\text{detector failure on the selected frame}
\rightarrow
\text{abstain/non-accept}.
\]

Do not search forward/backward for a detectable face in the primary single-image protocol.

---

# 13. "Always-on dual inference is the accuracy upper bound" is not technically correct

The method still describes always-on dual inference as an accuracy upper bound.

It is not.

Always-on dual inference with fixed:

\[
g_{\text{ref}}
\]

is merely the no-routing reference for that decision rule.

An oracle branch selector, learned fusion, or other classifier could achieve higher accuracy.

## Recommendation

Rename it:

> always-on dual reference

or:

> compute-unconstrained dual reference under the fixed \(g_{\text{ref}}\).

The routing experiment then asks:

> How closely can conditional inference approach the always-on dual reference while reducing compute?

This is precise and defensible.

---

# 14. Input resolution is a hidden confound in the complementarity claim

DINO currently uses:

\[
448\times448.
\]

The exact VLM checkpoint and native image resolution are still open.

If the eventual VLM operates at 224, 336, 384, or another resolution, observed error diversity may partly come from different spatial resolution rather than different visual-versus-semantic inductive biases.

This does not invalidate the system result, but it weakens a causal statement about why complementarity exists.

## Recommendation

At minimum report:

- exact DINO input resolution;
- exact VLM input resolution;
- crop geometry;
- interpolation;
- normalization.

If practical, add one resolution-sensitivity experiment.

Do not claim that error diversity is caused purely by pretraining objective or semantic knowledge unless resolution/context confounds have been considered.

---

# 15. The literature audit is missing several important 2026 VLM-FAS papers

The current reading list is strong but incomplete for late 2026.

At minimum add and position:

- **AIM-FAS — Vision-language adaptation with imbalance mitigation for generalizable face anti-spoofing**, Pattern Recognition, 2026;
- **DGPDL — Domain-Guided Prompt Distribution Learning for Generalizable Face Anti-spoofing**, IEEE TPAMI, 2026;
- **CLIP-SA — CLIP-Guided Semantic Alignment for Generalizable Face Anti-spoofing**, IEEE Transactions on Multimedia, 2026.

These do not appear to implement the exact proposed cross-foundation failure-risk mechanism, but they make the VLM/DG-FAS neighborhood denser.

The manuscript should explain why the current work is not another prompt-adaptation or semantic-alignment method.

Also add recent selective-classification work on class-aware AURC/risk-coverage evaluation because the paper now makes selective-deployment claims in a security-asymmetric setting.

---

# 16. The cross-foundation claim needs a quantitative "heterogeneity advantage"

The repository now contains a homogeneous control.

That enables a stronger explicit estimand.

Define:

\[
Rescue_{cross}
=
FARR(DINO,VLM)
\]

and:

\[
Rescue_{homo}
=
FARR(DINO,DINO_2).
\]

Then define:

\[
\boxed{
\Delta_{\text{hetero}}
=
Rescue_{cross}
-
Rescue_{homo}
}
\]

and similarly for REF or selective failure metrics.

A central claim about cross-foundation diversity should require:

\[
\Delta_{\text{hetero}}>0
\]

with uncertainty bounds on confirmatory targets.

If cross-foundation rescue is no better than homogeneous diversity, the paper remains a useful selective-ensemble study, but the specific cross-foundation story becomes weaker.

---

# 17. The CLIP visual-head control should use matched supervision and preprocessing

The new CLIP/SigLIP supervised visual head is useful.

For a fair comparison against DINO:

- use the same source labels;
- use the same train/validation subject splits;
- use comparable head capacity;
- use comparable augmentation budgets;
- report the same crop geometry;
- calibrate both on the same source calibration protocol.

Otherwise differences between:

\[
DINO
\]

and:

\[
CLIP_{\text{visual-head}}
\]

may come from training budget or preprocessing rather than representation.

This is especially important if the paper argues that prompt-driven semantics add something beyond the VLM image representation itself.

---

# 18. Explicitly separate system novelty from mechanistic interpretation

The system-level claim can be:

> heterogeneous foundation predictors provide useful recoverable errors for selective PAD.

This can be supported empirically.

The stronger mechanistic claim:

> DINO captures local forensic evidence while the VLM contributes semantic evidence.

requires additional evidence.

The current controls improve that case, but they do not prove it causally.

Therefore the manuscript should distinguish:

## System claim

\[
\text{DINO+VLM has useful complementary errors.}
\]

## Mechanistic hypothesis

\[
\text{The complementarity may arise from different local/semantic inductive biases.}
\]

The second should remain an interpretation unless stronger intervention or representation analysis is added.

This keeps the contribution defensible even if the semantic mechanism is not fully identified.

---

# Recommended synchronization fixes

Before implementation, synchronize the following text across the dossier:

1. define raw VLM semantic logit and remove double-calibration ambiguity;
2. make fixed core prompts primary everywhere;
3. remove any wording that compares risk scores directly against learned fusion classifiers;
4. rename always-on dual inference from "accuracy upper bound" to "always-on reference";
5. define `middle valid frame` independently of face detection;
6. freeze the primary risk feature vector;
7. move entropy/energy to explicit ablations unless fully defined;
8. add class-conditional failure-detection endpoints;
9. quantify heterogeneity advantage over the homogeneous control.

---

# Final recommendation

The repository remains ready for Stage 1.

The next major scientific decision should depend on three quantities:

\[
FARR_{\text{cross}},
\]

\[
FARR_{\text{homo}},
\]

and:

\[
\Delta_{\text{hetero}}
=
FARR_{\text{cross}}
-
FARR_{\text{homo}}.
\]

The core cross-foundation hypothesis is strongest if:

1. the VLM rescues a meaningful fraction of DINO false accepts;
2. this rescue is statistically supported;
3. the rescue persists on confirmatory target domains;
4. the rescue exceeds what is obtained from a homogeneous DINO diversity control.

For Stage 2, the paper should additionally require an incremental disagreement test:

\[
\Delta_{\mathrm{JS}}>0
\]

over capacity-matched models that already receive:

\[
(\widehat p_D,\widehat p_V,q).
\]

If cross-foundation rescue is strong but explicit JS adds no incremental value, keep the dual-foundation system but weaken the algorithmic emphasis on JS disagreement.

If cross-foundation rescue itself does not exceed homogeneous ensemble diversity, reframe the work as a broader selective-ensemble PAD study rather than a cross-foundation-specific contribution.
