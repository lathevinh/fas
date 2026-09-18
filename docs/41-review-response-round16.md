# Response to Review Round 16 - Q3 Paper Plan Frozen

Date: 2026-09-18

## Decision

The owner accepts Review Round 16.

**RESEARCH PLAN READY TO FREEZE FOR A Q3-FIRST PAPER. PAPER STORY AND MAIN TABLES
FROZEN BEFORE CODING.**

This response changes documentation only. It does not implement Phase 0, inspect any
target label, run a PAD experiment, or turn a planned contribution into a finding.

## Paper identity

The working title is:

> Source-Domain Cross-Fitted Failure-Risk Estimation for Selective Face Presentation
> Attack Detection

The method is named **Domain-OOF Failure Risk Estimation**. Heterogeneous DINOv2-Reg
and OpenCLIP predictors are the primary instantiation. The paper's method claim is the
generation of failure supervision from source-domain pseudo-shifts, not DINO plus VLM,
probability averaging, logistic regression, disagreement, or abstention by themselves.

Only two questions remain core:

1. domain-OOF versus matched sample-OOF risk supervision for a fixed heterogeneous
   classifier and identical errors;
2. the complete heterogeneous selective system versus the matched same-family
   selective system.

Disagreement, classifier rescue, SiW-M, policy margin, and routing remain secondary.

## Literature update

The three Round-16 neighbors were independently checked against Crossref and OpenAlex
metadata and now have stable DOI records in the reading list:

- AIM-FAS, Pattern Recognition 2026, `10.1016/j.patcog.2026.113101`;
- DGPDL, IEEE TPAMI 2026, `10.1109/TPAMI.2026.3674204`;
- CLIP-SA, IEEE Transactions on Multimedia 2026,
  `10.1109/TMM.2026.3668651`.

They establish that VLM adaptation, domain-guided prompts, and semantic alignment for
generalizable FAS are occupied. The proposed method does none of those things in its
core path: prompts and encoders remain fixed, predictors remain independent, and a
separate post-predictive risk model learns from held-out-domain failures.

The RPSR-FAS distinction is now explicit: training-time reliability that reorganizes
classifier supervision is different from post-predictive, source-domain-held-out
failure supervision for a target-blind selector. No broad first-reliability claim is
made.

CA-FAS is promoted to a first-class reliability competitor. Source-fitted
Mahalanobis confidence on frozen DINO features remains a required simple control, but
is not described as a faithful CA-FAS reproduction. A reproduction is included only
when its objective and protocol can be matched fairly.

## Manuscript contract

The frozen skeleton contains the requested Introduction, Related Work, Method,
Experimental Protocol, Planned Main Tables, and Claim/Falsification Matrix. It also
freezes these four main-table roles before coding:

1. classifier quality;
2. fixed-error RQ1 risk transfer;
3. selective PAD utility with K=1 accounting;
4. heterogeneous versus same-family complete systems.

The RQ1 ranking claim and operational utility claim remain logically separate. A
positive error-AP result is not erased by one weak operating point, while good error
ranking without useful selective trade-offs cannot support the practical utility
claim.

## Handoff

No architecture, loss, backbone, routing mechanism, or cue module is added. The next
authorized engineering task remains Phase 0 of the dependency-ordered implementation
plan: migrate the provisional governance scaffold to the frozen source-only contracts
and validate them on synthetic fixtures before any model or dataset-facing work.