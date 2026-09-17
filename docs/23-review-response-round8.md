# Response to ChatGPT Review (Round 8)

Date: 2026-09-17

## Verdict

The review correctly identifies source-lineage and estimand gaps that would otherwise
invalidate Stage 2. The architecture remains unchanged.

## Accepted

1. Gate-calibration partition $G$ is excluded from branch/head fitting, branch
   calibration, fusion selection, risk fitting, and preregistration statistics. No
   component is refit with $G$ after threshold selection.
2. Bounded branch probabilities and absolute disagreement are not standardized. Only
   fixed quality features use frozen final-source statistics at target time.
3. Domain-OOF and attack-OOF are separate primary protocols for MICO and SiW-M;
   domain-only pseudo-shifts cannot support an attack-shift calibration claim.
4. Potential branch rescue ($REF_{VLM},FARR_{VLM}$) is separated from realized fusion
   rescue ($REF_g,FARR_g$).
5. Heterogeneity advantage uses paired events on the same DINO failures with clustered
   bootstrap or McNemar-style inference.
6. Three decision levels separately govern project continuation, cross-foundation
   wording, and disagreement wording.
7. Branch calibration uses equal-domain source weighting and end-to-end usability
   includes $BFNR_{end2end}$ under terminal abstention.
8. Source data lineage is explicit, and exact prompt/checkpoint artifacts must freeze
   after pilot selection and before confirmatory targets.

## Accepted with qualification

### One-stage branch calibration

The offset concern is valid. Version 1 therefore uses one monotone affine logistic
calibrator $\sigma(a\ell+b)$ with $a>0$, not temperature followed by a second stage.
Temperature-only scaling remains an ablation. This preserves ordering while allowing
the fixed prompt bank's live/spoof offset to be corrected.

### Strong same-family control

Frozen DINOv2-Reg plus plain DINOv2 is promoted to required Stage 1 confirmation only
when retaining a cross-foundation title. The cheaper shared-encoder control remains a
sanity check. Failure to beat the strong control triggers reframing, not automatic
rejection of a useful selective-ensemble result.

### Versioned prompt and checkpoint artifacts

The artifact paths and required fields are fixed now, but their final checkpoint value
is not invented before pilot evidence. A finite candidate set must be preregistered;
pilot selection then freezes the exact YAML artifacts before three confirmatory MICO
targets. Confirmatory performance cannot influence that choice.

## Additional decision

RQ2 now decomposes cross-foundation probability gain
$\Delta_{CF}=Perf(R_{DV})-\max(Perf(R_D),Perf(R_V))$ from explicit disagreement gain
$\Delta_{dis}=Perf(R_{DVd})-Perf(R_{DV})$. Quality-only and single-branch learned-risk
baselines prevent image quality or one strong branch from receiving cross-foundation
credit.

## Implementation decision

Stage 1 reports potential and realized rescue plus paired strong-control advantage.
Stage 2 proceeds with clean $G$, separate OOF protocols, one-stage affine calibration,
and the preregistered three-level continuation/reframing hierarchy.