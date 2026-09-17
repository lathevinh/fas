# Response to ChatGPT Research Review - Round 10

Date: 2026-09-17

## Decision

The review is accepted as the final protocol review before implementation. Its main
criticism is correct: because

$$
\tau_{ref}^{(k)}=(\widehat p_D+\widehat p_V)/2-m_F,
$$

the previous primary feature vector exposed a fold-specific constant and confounded
scientific attribution with operational policy information.

No architecture is added. The dossier now closes the remaining estimand and lineage
ambiguities and moves next to manifests, split counts, and Stage 1 measurements.

## Accepted changes

1. **Scientific versus operational risk.** Scientific models use
   $z_{science}=[\widehat p_D,\widehat p_V,d_{abs},q]$; only the deployed policy model
   may use $z_{oper}=[\widehat p_D,\widehat p_V,d_{abs},m_F,q]$.
2. **Three-part attribution.** $\Delta_{CF}$ measures dual-score gain,
   $\Delta_{dis}$ explicit-disagreement gain, and $\Delta_{margin}$ the separate
   policy-margin gain.
3. **Fixed Stage-2 models.** $R_q$, $R_D$, $R_V$, $R_{DV}$, $R_{DVd}$, and
   $R_{DVdm}$ now have exact feature sets and share one fixed-regularization logistic
   family and lineage.
4. **Risk loss.** The primary probabilistic gate averages unweighted BCE equally over
   pseudo-domains while preserving natural within-domain error prevalence.
   Class-weighted/focal variants are ranking-only risk-score ablations.
5. **Attack gate holdout.** Subject/video-safe $G_{attack}$ is carved only from known
   attacks and is separate from MICO $G_{domain}$.
6. **Margin roles.** $-|m_F|$ remains the simple boundary-distance baseline; signed
   $m_F$ is an operational learned feature only.
7. **Routing.** Spoof-only routing minimizes VLM invocation subject to a preregistered
   source bona-fide rejection constraint on separate routing validation. Gate holdouts
   are not reused for routing or ablation selection.
8. **Pilot selection.** Core prompts freeze before pilot labels. Checkpoint and
   preprocessing selection is deterministic: lowest pilot ACER for calibrated-average
   fusion at the source-selected threshold under a pre-label latency ceiling; ties
   within 0.1 percentage point use latency, then lexical configuration ID.
9. **Confirmatory aggregation.** Target and seed outputs stay independent. A delta
   requires positive three-target macro mean, positive estimates on at least two
   targets, no target beyond a frozen harm tolerance, and positive target-macro delta
   for at least two of three seeds. No best-seed reporting or $t$-test at $n=3$.
10. **Fair strong control.** DINOv2-Reg + plain-DINOv2 receives the same affine
    calibration, calibrated-average fusion, operating-point rule, denominators, and
    bootstrap units as the heterogeneous pair.
11. **Neutral novelty wording.** The unconditional contribution is source-only
    cross-fitted failure-risk calibration from independent heterogeneous predictors.
    Disagreement remains in the contribution only if $\Delta_{dis}$ passes.
12. **Pilot lineage.** The pilot cannot be a confirmatory target but may be a labeled
    source when a different MICO domain is targeted.

## Qualified point

Normalized double fault is added overall and attack-conditionally as a descriptive
strength-adjusted diagnostic with uncertainty. It is not a continuation or kill
criterion: its denominator becomes unstable when either branch has a small marginal
error rate, and it does not replace raw rescue, false-accept rescue, or the paired
heterogeneity comparison.

## Not adopted

No new architecture, loss family, or extra title claim is adopted. The review itself
correctly says the architecture is stable. Further prose-only review rounds would now
have lower value than executable lineage checks and empirical counts.

## Files synchronized

- `docs/00-project-charter.md`
- `docs/01-related-work-and-novelty.md`
- `docs/02-research-questions.md`
- `docs/03-method.md`
- `docs/04-data-and-protocols.md`
- `docs/05-experiment-plan.md`
- `docs/06-risks-and-decisions.md`
- `README.md`

## Next gate

Begin Stage 0/1 implementation. The next review artifact should contain dataset
manifests, subject/video split counts, permanent holdout counts, candidate configuration
hashes, and first pilot outputs. It should not introduce another architecture variant
without empirical failure evidence.
