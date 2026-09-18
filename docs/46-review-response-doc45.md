# Response to Document 45 - Track-A Benchmark Contract

Date: 2026-09-18

## Decision

The review is accepted. It confirms that Document 44 resolved the material protocol
ambiguities and that the core plan can remain frozen. The corrections below tighten
Track A and terminology only. They do not change the architecture, two research
questions, primary RQ1 estimand, Track-B protocol, or four-table paper contract.

Track A reproduces a pinned literature sample/evaluation convention for classifier
comparability, while all scientific claims on source-domain failure-risk transfer are
evaluated exclusively under Track B.

## Required corrections

### 1. Track-specific role manifests - accepted

Document 42 now defines one immutable manifest per dataset per active track. Track A
records pinned protocol membership and a deterministic source-only fit/checkpoint
split. It has no branch-calibration, gate-domain, routing, or risk-training roles.
Track B retains the full role structure. Neither track's assignment depends on outer
target or optimization seed.

### 2. Compatibility wording - accepted

Track A is now called an `MCIO sample/evaluation view`. Its first implementation reuses
the frozen Track-B detector and context crop, so it claims sample-universe/frame-rule
compatibility only. It is neither SSDG preprocessing compatible nor an SSDG
reproduction. Any later exact MTCNN/256 variant must be reported separately.

### 3. Exact frame function and configuration - accepted

The pinned SSDG rule is frozen as

```text
index_j = sorted_frame_list[6 + j * floor(N / num_frames)]
source num_frames = 1
target num_frames = 2
```

Phase 1 must still reconcile this code-derived rule, list contents, counts, labels, and
release identities against the locally obtained protected datasets before claiming
sample-level equivalence.

### 4. Video aggregation - accepted

The official SSDG evaluation code was inspected at pinned commit
`c268920a7408ca78fb425954de2bf5745d1c660a`. Track A freezes its target aggregation as
the arithmetic mean of class-1 softmax probabilities across the selected frames of
each video. Scores or logits are not averaged instead.

### 5. SSDG target-aware validation disclosure - accepted

The pinned implementation derives the EER threshold from target video scores, and its
training code selects checkpoints with `tgt_valid_dataloader`. Published SSDG HTER
therefore receives an explicit target-aware validation/threshold footnote and is not
presented as like-for-like target-blind HTER. Our Track A keeps checkpoint and threshold
selection source-only; AUC provides the less threshold-dependent comparison.

### 6. MCIO terminology - accepted

`MCIO` is the sole manuscript acronym for MSU-MFSD, CASIA-FASD, Idiap Replay-Attack,
and OULU-NPU. Current normative documents use MCIO and ordinary leave-one-domain-out
wording. Existing lowercase `mico` artifact paths remain internal legacy identifiers
for the same benchmark and will be migrated only where Phase 0 changes schemas.

## Strong recommendations

### 7. Track A outside novelty - accepted

Track A creates no third research question and no protocol novelty claim. It appears
only as Panel A of classifier Table 1 for limited literature context. RQ1 and RQ2 are
estimated exclusively in Track B.

### 8. `AP_FA` remains secondary - accepted

`AP_error` remains the primary RQ1 endpoint. `AP_FA` and selective false-accept metrics
are security-specific supporting evidence and are never co-primary.

### 9. Quality attribution - retained

The required $R_{DVd}$ with/without-$q$ comparison remains in the method and execution
plan. A gain that depends on $q$ is interpreted as reliance on source-observed
quality/domain nuisance signals, not cross-branch evidence alone.

### 10. Track-A stop rule - accepted

Track-A reproduction work stops after two engineer-days if artifacts cannot be
reconciled or the old stack is incompatible. The paper then uses clearly labeled
reported literature context and only verified in-house comparisons. Track A cannot
delay Track-B RQ1 execution.

## Verification boundary

The code-level frame selector, video aggregation, and target-aware SSDG behavior have
been verified against the pinned repository. Exact protected-release/list equivalence
cannot be verified before dataset acquisition. It remains an explicit Phase-1 hash,
count, label, and membership gate rather than a present claim.

## Updated verdict

**DOCUMENT 45 IS ANSWERED; THE CORE PLAN REMAINS FROZEN AND PHASE 0 REMAINS AUTHORIZED.**
