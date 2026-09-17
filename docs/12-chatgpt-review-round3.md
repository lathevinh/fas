# ChatGPT Research Review — Round 3

Date: 2026-09-17

This review evaluates `11-review-response-round2.md` together with the revised:

- `03-method.md`
- `04-data-and-protocols.md`
- `05-experiment-plan.md`

## Overall assessment

The revised proposal is now substantially cleaner and is ready to move from proposal refinement to implementation.

The Round 2 response was not merely rhetorical. The main recommendations were actually reflected in the method and protocol:

- branch probabilities are calibrated independently before disagreement is computed;
- sample-OOF and domain-OOF are both included;
- fixed APCER/BPCER operating points are now part of evaluation;
- routing and selective gates are explicitly separated;
- the method remains simple and avoids returning to ontology-heavy evidence learning.

At this point, I do not recommend another major architectural redesign.

However, one protocol definition is still incorrect and should be fixed before the plan is frozen.

---

# 1. The definitions of true unknown and open-vocabulary unknown are currently reversed

The current protocol states approximately:

- **true unknown PAI:** attack instrument/family absent from training;
- **open-vocabulary unknown:** semantic description absent from the prompt bank.

The second definition is incorrect.

Open-vocabulary recognition is precisely the setting where a class may be absent from image supervision but its text description is available to the vision-language model.

Assume the held-out attack is:

\[
\text{silicone mask}.
\]

## True downstream-unseen PAI

The attack is absent from downstream FAS image supervision **and** its attack-specific text description is not provided.

The prompt bank must not contain phrases such as:

```text
silicone mask
latex mask
3D silicone face
```

It may contain generic concepts such as:

```text
live human face
printed presentation
display presentation
artificial presentation
```

The model must therefore detect the presentation as suspicious or unfamiliar without being told the exact semantic class.

Formally:

\[
\boxed{
\text{downstream-unseen PAI}
=
\text{no downstream FAS image supervision}
+
\text{no attack-specific text prompt}
}
\]

## Open-vocabulary zero-shot PAI

The attack is absent from downstream image supervision, but its text description is allowed.

For example:

```text
a face wearing a silicone mask
```

is permitted in the VLM prompt bank.

This evaluates semantic zero-shot transfer:

\[
\boxed{
\text{open-vocabulary PAI}
=
\text{no downstream FAS image supervision}
+
\text{attack-specific text prompt allowed}
}
\]

These two protocols must not be pooled into one result.

Recommended presentation:

- main unseen-attack table: downstream-unseen PAI;
- secondary/supplementary table: open-vocabulary zero-shot PAI.

---

# 2. Avoid the absolute phrase "true unknown"

There is an important foundation-model caveat.

CLIP, SigLIP, and similar VLMs are pretrained on very large internet-scale datasets. It is impossible to guarantee that the model has never encountered images or text related to:

- silicone masks;
- printed faces;
- replay attacks;
- artificial faces.

Therefore the manuscript should not imply that the attack is globally unknown to the pretrained foundation model.

A cleaner term is:

> **downstream-unseen PAI**

or:

> **FAS-unseen PAI**

The manuscript should explicitly state:

> The attack is unseen with respect to downstream FAS supervision and attack-specific prompting; exposure during generic foundation-model pretraining is uncontrolled.

This avoids an unnecessary reviewer objection.

---

# 3. Stage 1 ensemble baselines should use calibrated scores for fairness

The method now defines:

\[
\tilde p_D=\operatorname{Cal}_D(p_D),
\]

\[
\tilde p_V=\operatorname{Cal}_V(p_V),
\]

before disagreement is computed.

This is correct.

However, Stage 1 currently lists:

```text
fixed score average
regularized learned score fusion
```

without explicitly stating whether raw or calibrated scores are used.

The principal ensemble baseline should use calibrated probabilities:

\[
p_{\text{avg}}
=
\frac{\tilde p_D+\tilde p_V}{2}.
\]

Recommended reporting:

1. raw score average;
2. calibrated score average;
3. regularized learned fusion using calibrated source scores.

The calibrated average should be the main simple-fusion baseline.

Otherwise the proposed calibrated disagreement mechanism would be compared against an unnecessarily weak uncalibrated ensemble.

---

# 4. Separate \(r_{FA}\) and \(r_{FR}\) heads are not necessary for version 1

A previous review suggested possibly estimating:

\[
r_{FA}(x)
\]

and:

\[
r_{FR}(x)
\]

separately.

The revised plan instead evaluates a generic risk model at fixed:

- APCER;
- BPCER;
- coverage;
- VLM invocation rate.

This is a good simplification.

Do not add two separate risk heads unless the experiments show that generic risk estimation fails to control security operating points.

For version 1, a cleaner deployment question is:

\[
\max \text{Coverage}
\]

subject to:

\[
APCER\le\alpha.
\]

Useful operating points include:

\[
\alpha \in \{0.5\%,1\%,5\%\}.
\]

At each security operating point report:

- coverage;
- BPCER;
- VLM invocation rate;
- retry rate;
- latency.

This is sufficient and more practical than adding another model component.

---

# 5. Current architecture should now be frozen for Stage 1

The recommended minimum architecture is:

```text
RGB image
   |
   +-----------------------+
   |                       |
DINOv2-Reg              VLM
   |                       |
 p_D                     p_V
   |                       |
 Cal_D                   Cal_V
   |                       |
 \tilde p_D            \tilde p_V
   |                       |
   +-----------+-----------+
               |
      calibrated disagreement
               |
       small risk model
               |
     accept / invoke / retry
```

The disagreement signal is:

\[
d(x)
=
D_{JS}(\tilde p_D\|\tilde p_V).
\]

A risk feature vector may be:

\[
z(x)
=
[
\tilde p_D,
\tilde p_V,
d(x),
H_D,
H_V,
q(x)
].
\]

The main version should not include:

- ontology learning;
- feature consistency losses;
- decision consistency;
- MLLM reasoning;
- synthetic forensic cue supervision;
- named micro-forensic concept maps;
- complex heatmap explanations.

These can remain future extensions only if the core hypothesis succeeds.

---

# 6. Stage 1 should now be the immediate implementation target

The next experiment should focus entirely on whether complementary information exists.

## DINO branch

Use:

\[
x
\rightarrow
\text{DINOv2-B/14-Reg}
\rightarrow
\text{PAD head}.
\]

Freeze the backbone initially.

## VLM branch

Use:

\[
x
\rightarrow
\text{CLIP/SigLIP image encoder}
\]

with:

- fixed or source-selected prompt ensemble;
- source-only temperature calibration;
- no target information.

## Calibrate branches independently

Store both raw and calibrated outputs:

\[
p_D,\tilde p_D,p_V,\tilde p_V.
\]

## Build the joint correctness table

For every untouched target sample:

| DINO | VLM | category |
|---|---|---|
| correct | correct | \(P_{cc}\) |
| correct | wrong | \(P_{cw}\) |
| wrong | correct | \(P_{wc}\) |
| wrong | wrong | \(P_{ww}\) |

Then measure:

- standalone performance;
- double-fault rate;
- two-sided recovery;
- error correlation;
- subgroup persistence;
- oracle upper bound.

---

# 7. The critical kill metric is oracle gain

The most important decision quantity is:

\[
\boxed{
\Delta_{\text{oracle}}
=
Perf_{\text{oracle}}
-
\max(Perf_D,Perf_V)
}
\]

If \(\Delta_{\text{oracle}}\) is very small, then the second model contains little recoverable information and there is no reason to build a sophisticated risk architecture.

Example:

\[
AUC_D=95.5,
\]

\[
AUC_V=92.0,
\]

\[
AUC_{\text{oracle}}=96.0.
\]

The recoverable headroom is probably too small to justify the cost of a second foundation model.

In contrast, if the VLM recovers a meaningful subset of DINO failures and the oracle upper bound is substantially higher, then the project has a real signal worth exploiting.

This should remain a hard go/no-go criterion.

---

# 8. Current novelty position is sufficiently separated from nearby work

The strongest current formulation is:

\[
\boxed{
\text{independent DINOv2-Reg}
+
\text{independent VLM}
\rightarrow
\text{cross-foundation disagreement}
\rightarrow
\text{source-only selective risk}
\rightarrow
\text{security-aware conditional inference}
}
\]

The method should not claim novelty in:

- disagreement itself;
- cross-fitting itself;
- selective classification itself;
- VLM-based FAS itself;
- DINO-based FAS itself.

The contribution is the empirical and methodological combination under a realistic PAD shift setting:

1. **Cross-foundation complementarity analysis for PAD**  
   Quantify whether independently pretrained visual and semantic foundation models recover different errors under domain and attack shifts.

2. **Source-only selective-risk calibration**  
   Use only source-domain out-of-fold predictions to estimate whether cross-model disagreement generalizes to untouched target domains and unseen PAIs.

3. **Security-aware conditional VLM inference**  
   Evaluate whether semantic inference can be invoked only when needed while maintaining biometric operating constraints.

This is appropriate for a practical Q3-oriented paper if the empirical gains are real.

---

# Final recommendation

The proposal phase is now mature enough.

Do not start another major architecture redesign before obtaining Stage 1 results.

Before implementation, make only these final protocol corrections:

1. fix the open-vocabulary versus downstream-unseen PAI definitions;
2. use "downstream-unseen PAI" or "FAS-unseen PAI" instead of the absolute phrase "true unknown";
3. ensure simple fusion baselines use calibrated branch outputs;
4. keep security-aware evaluation simple using fixed APCER/BPCER operating points.

After these changes, begin the complementarity kill experiment.

The next useful research discussion should be based on actual measurements:

\[
P_{cc},P_{cw},P_{wc},P_{ww}
\]

and especially:

\[
\Delta_{\text{oracle}}.
\]

If oracle gain is negligible, stop the dual-foundation direction.

If oracle gain is substantial, proceed to source-only risk calibration and selective deployment.
