# Response to ChatGPT Review (Round 9)

Date: 2026-09-17

## Verdict

The review correctly identifies threshold-lineage and target-role ambiguities that
would weaken confirmatory inference. No architecture changes are required.

## Accepted

1. The charter now permits one committed pilot domain and prohibits confirmatory
   targets from selecting any checkpoint, prompt, threshold, or hyperparameter. The
   pilot is permanently excluded from the three-target confirmatory macro.
2. The cross-foundation title requires paired advantage over frozen DINOv2-Reg plus
   plain DINOv2; shared-encoder head diversity is only a sanity control.
3. Attack-OOF rotates pseudo-held-out families only within known SiW-M attacks. The
   final unseen attack never participates in fitting, calibration, or selection.
4. Every OOF fold selects $\tau_{ref}^{(k)}$ from its allowed remainder and carries
   signed operational margin $m_F^{(k)}$ into the risk representation. Distance to the
   operational boundary is a required simple baseline.
5. Gate-calibration set $G$ is stratified where possible and reports total, attack,
   error, and false-accept counts before threshold stability is claimed.
6. Reduced-data strict selective comparisons are separated from optional full-source
   literature-compatible branch results.
7. $\Delta_{CF}$ and $\Delta_{dis}$ are bound to prediction-error AUPR as the primary
   claim metric; excess-AURC and class-conditional endpoints remain mandatory support.
8. Affine calibration is class-balanced within domains and domain-balanced across
   sources. Outputs are called standardized source-calibrated PAD scores, not
   real-world posterior probabilities.
9. Spoof-only early exit is the primary routing policy. Direct-live and symmetric
   routing are security-bounded ablations; route-specific errors and end-to-end totals
   are both reported.
10. Pilot and post-pilot freeze milestones are immutable Git commits, and the source
    lineage table records global configuration roles.

## Accepted with qualification

### Complementarity lift

Strength-adjusted lift is useful as a diagnostic alongside raw paired rescue. It is
not a continuation or title kill criterion: subtracting standalone correctness can
penalize a uniformly strong second branch, and the quantity does not causally isolate
heterogeneous pretraining. Paired realized rescue against the strong same-family
control remains the primary cross-foundation evidence.

### Permanent gate holdout

Approach A is retained for auditability: $G$ is excluded from every deployed
component and all internal methods use the same $Source\setminus G$ data. This costs
training data, so full-source literature comparisons are descriptive and fully
cross-fitted threshold calibration remains a later data-efficiency extension.

## Claim wording

After pilot-based candidate selection, the whole research process is not target-free
over all four MICO domains. The precise claim is: risk calibration and decision
thresholds are source-only for each untouched confirmatory target; one preregistered
development domain selects within a committed candidate set and is excluded from
confirmatory inference.

## Implementation decision

Stage 1 proceeds with potential and realized rescue, paired strong-control comparison,
and a three-target confirmatory macro. Stage 2 uses fold-relative margins, nested
known-attack OOF, clean and sufficiently reported $G$, and conservative spoof-only
routing.