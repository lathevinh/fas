# Response to ChatGPT Review (Round 2)

Date: 2026-09-17

This response records the adjustments made after the second review and clarifies the
remaining evidence requirements for a publishable claim.

## Accepted recommendations

1. The method now clearly distinguishes between a routing gate and a selective gate.
   The routing gate decides whether to escalate to the VLM; the selective gate decides
   whether to accept, fuse, or abstain after both branches have produced outputs.

2. The project keeps the novelty statement narrow and conditional. The claim is no
   longer framed as general disagreement novelty, but as source-only calibrated cross-
   foundation disagreement for selective single-image PAD under domain and attack shift.

3. The complementarity analysis is elevated to a primary experiment. The paper must
   report branch competence, disagreement patterns, double-fault rates, oracle gain,
   and target-domain subgroup persistence.

4. The VLM is explicitly treated as a semantic branch, not as a causal forensic
   explanation. We will avoid language implying that prompt concepts directly verify a
   physical spoof mechanism unless there is direct evidence.

5. The deployment section now includes coverage, security, and cost trade-offs. The
   selective method must beat conventional uncertainty and fusion baselines at matched
   operating points.

6. The out-of-fold calibration plan remains source-only. Prompt tuning, threshold
   selection, and gate training will use only source-domain validation splits.
7. DINO and VLM probabilities are calibrated independently before JS disagreement.
8. Sample-OOF and domain-OOF calibration are compared, with domain-OOF as primary.
9. Downstream-unseen PAIs and open-vocabulary zero-shot PAIs are reported separately.
10. Selective risk is reported at fixed APCER and fixed BPCER, not only at matched
   average coverage.

## Clarified contribution

The intended contribution is not the generic use of disagreement. It is the design of
an uncertainty-risk mechanism that exploits independent visual and semantic foundation
models under realistic source-to-target shift. The key question is whether the
combination offers a better selective deployment trade-off than standard uncertainty
methods, not whether disagreement is mathematically interesting in the abstract.

The final disagreement signal is computed after independent source calibration:

$$d(x)=D_{JS}(\operatorname{Cal}_D(p_D)\|\operatorname{Cal}_V(p_V)).$$

Uncalibrated JS remains a baseline, not the final signal.

## Evidence that must be shown before stronger claims

The paper will proceed only if the following are demonstrated on untouched target data:

- both branches have non-trivial standalone competence;
- disagreement identifies a meaningful subset of errors that the better branch can
  recover;
- the learned gate exceeds raw disagreement and standard uncertainty baselines;
- coverage and biometric security remain acceptable under the selective inference rule;
- the method does not collapse when source and target domains differ substantially.
- domain-OOF calibration is justified relative to sample-OOF;
- downstream-unseen PAI and open-vocabulary zero-shot PAI results are not conflated;
- selective risk is reported at fixed APCER and fixed BPCER.

## Non-claims retained

The project still does not claim that:

- combining DINO and a VLM is inherently novel;
- prompt concepts are a validated forensic explanation;
- disagreement alone is sufficient for a publication-worthy algorithm;
- the method is automatically better than strong baselines without held-out target
  evaluation.

## Final direction

The revised plan is to keep the method simple, leakage-safe, and empirically decisive:

- frozen DINOv2-Reg visual branch;
- frozen VLM semantic branch;
- source-only out-of-fold disagreement calibration;
- selective routing and abstention only if the evidence demonstrates real gain.

The immediate implementation gate is to calibrate both branches independently, run
sample-OOF and domain-OOF variants, and report fixed-security operating points before
adding any richer risk architecture.

This keeps the paper practical, reviewable, and defensible under Q3 constraints.
