# Response to ChatGPT Review

Date: 2026-09-17

This response records which recommendations in `08-chatgpt-review.md` were adopted
and where the revised plan deliberately differs.

## Verified prior work

The two central references in the review were independently verified:

- Cross-Scenario Unknown-Aware Face Anti-Spoofing With Evidential Semantic
  Consistency Learning, IEEE TIFS 2024, DOI `10.1109/TIFS.2024.3356234`;
- Reliability-Aware Vision-Language Face Anti-Spoofing via Progressive Semantic
  Reorganization, first online 2026-09-08, DOI `10.1007/s44443-026-01145-z`.

They make generic semantic-consistency, unknown-aware, and reliability-aware VLM
claims unsafe. The reading list now also includes confidence-aware FAS and a 2026
dual semantic consistency paper found during verification.

## Accepted corrections

1. Decision-level consistency was removed. It conflicted with disagreement-based
   failure detection.
2. The minimum experiment now tests branch complementarity before advanced modules.
3. DINOv2 versus DINOv2-Reg is an ablation, not a main research question.
4. Named forensic cues and ontology learning were deferred.
5. The compute plan now targets an RTX 4080 with 16 GB VRAM using sequential caching.
6. The core framing is selective cross-foundation disagreement, not dual-evidence
   consistency.

## Strengthened beyond the review

### Complementarity criterion

$P_{cw}+P_{wc}$ is not sufficient because two weak predictors may disagree often.
Continuation requires standalone competence, two-sided recovery, double-fault rate,
oracle gain over the better branch, subgroup persistence, and achievable fusion gain.

### Source-only reliability calibration

A learned gate introduces leakage unless its error labels come from samples unseen by
the branch training that generated their predictions. The revised method creates
out-of-fold records by holding out source domains or attack families. Target samples
never train or select the gate.

### Conditional inference semantics

Disagreement cannot decide whether to call the VLM before the VLM has run. The revised
deployment has two gates:

1. DINO uncertainty and quality route a request to the VLM;
2. post-VLM disagreement determines fusion, acceptance, or retry.

## Partially accepted recommendation

Forensic evidence analysis is demoted rather than deleted. DINO patch pooling remains
a representation choice, and patch deletion/insertion may be reported as secondary
analysis. It cannot become a contribution unless quantitative faithfulness succeeds.
Named micro-forensic concepts, pseudo-labels, and synthetic interventions are outside
version 1.

## Revised candidate claim

> Source-only calibrated cross-foundation disagreement for selective single-image
> face PAD under unseen domain and attack shifts.

Disagreement alone is not claimed as novel. The candidate contribution is the
source-only cross-fitted risk mechanism and its biometric security, coverage, and
latency evaluation. This claim remains conditional on outperforming conventional
uncertainty and learned-fusion baselines across multiple untouched targets.