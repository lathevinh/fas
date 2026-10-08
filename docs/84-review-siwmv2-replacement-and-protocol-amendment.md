# 84 — Review of SiW-Mv2 Replacement Prerequisite and Required Protocol Amendment

Date: 2026-10-08
Repository: `lathevinh/fas`
Reviewed commit: `c9147e84f695e5e513942f6da6e4bd9b22f82169`
Reviewed document: `docs/83-phase1-siwmv2-prerequisites-and-replacement-decision.md`

## Verdict

**Checkpoint 1.3S prerequisite inspection: ACCEPTED.**

**Requested scientific change “replace Replay-Attack with SiW-Mv2 and rewrite the protocol/plan”: NOT YET COMPLETE.**

Document 83 correctly inspects the supplied SiW-Mv2 archive, pins the ECCV22 reference implementation, identifies protocol-list discrepancies, keeps the current benchmark unchanged, and refuses to invent missing metadata. The exact implementation commit also has fresh successful CI.

However, the owner has now explicitly decided that Replay-Attack is unavailable and SiW-Mv2 will replace it. Therefore the next step should be a dated benchmark amendment, not continued waiting for Replay-Attack.

## Important correction to Document 83

Document 83 treats the absence of a provider-authorized video-to-participant mapping as a blocker to core replacement.

That is stricter than the already frozen implementation plan.

Document 42 explicitly allows source roles to be assigned using complete subject groups, **or complete video groups if subject identity is genuinely unavailable**.

The statistical plan likewise permits subject/video clusters.

Therefore lack of participant IDs is a limitation to disclose, but is **not by itself a blocker** if the project formally records that SiW-Mv2 subject identity is unavailable and uses immutable video-group roles and video-clustered bootstrap for that dataset.

No fake `subject_id = video_id` should be created. Use `subject_id = unknown` (or the schema-approved equivalent) and an explicit video grouping/clustering policy.

## Protocol-list discrepancy can be resolved prospectively

The pinned Protocol-I lists and supplied archive can be reconciled with an explicit pre-target intersection policy.

### Bona fide

- supplied archive: 785 live videos;
- every supplied live video is assigned by the pinned Protocol-I train/test lists;
- pinned lists additionally reference 11 unavailable live videos.

Policy: use the 785 available listed live videos; record the 11 unavailable references as missing protocol media.

### Attack

- supplied archive: 915 spoof videos;
- 895 are assigned by the pinned Protocol-I train/test lists;
- 20 supplied spoof videos are not assigned by Protocol I.

Policy: exclude the 20 unlisted spoof videos from the primary benchmark as out-of-protocol media. Preserve them in the inventory but do not silently assign them to train or test.

This gives a protocol-controlled primary SiW-Mv2 universe of 1,680 videos: 785 live + 895 attack.

## Required benchmark amendment

Replace the primary four-domain benchmark:

`OULU-NPU / CASIA-FASD / Replay-Attack / MSU-MFSD`

with:

`OULU-NPU / CASIA-FASD / MSU-MFSD / SiW-Mv2`

Do **not** call the new benchmark `MCIO`. Keep `MCIO` as the historical MSU/CASIA/Idiap/OULU benchmark identity.

Use a neutral name such as `four-domain amended benchmark` or explicit domain set `{O,C,M,S}`, where `S = SiW-Mv2`.

Outer folds:

- `C + M + S -> O`
- `O + M + S -> C`
- `O + C + S -> M`
- `O + C + M -> S`

Domain-OOF remains structurally unchanged because each fold still has three source domains.

## SiW-Mv2 source/target policy

Use **Protocol I only** for the primary study.

When SiW-Mv2 is a source:
- source universe = reconciled Protocol-I training membership;
- assign immutable source roles by complete video groups when participant identity is unavailable;
- keep the same source-only calibration/gate rules.

When SiW-Mv2 is the target:
- target universe = reconciled Protocol-I test membership;
- use the fixed one-frame-per-video Track-B rule;
- no target sample influences fitting/calibration/gate/method selection;
- bootstrap uses video clusters for SiW-Mv2.

Do not use Protocol II/III in primary RQ1/RQ2.

## Attack scope

Use all 14 SiW-Mv2 attack types present in reconciled Protocol I.

Do not silently reduce to print/replay merely to imitate Replay-Attack.

This means the held-out SiW-Mv2 fold contains both dataset/acquisition shift and attack-family shift. Manuscript wording should therefore prefer `cross-dataset failure-risk transfer` or `held-out dataset/domain transfer`, not imply pure sensor/environment domain shift in every fold.

## RQ1/RQ2

The estimands and pass rules do not need redesign.

Only the target set changes to `{O,C,M,S}`.

Keep:
- 4 outer targets;
- 3 frozen seeds;
- equal target macro;
- >=3/4 positive-target rule;
- same N_error_min;
- same bootstrap procedure;
- same K=1 gate semantics and harm tolerances.

No criterion should be retuned because SiW-Mv2 may be harder.

## Track A

SSDG/FLIP Track A is tied to historical MCIO and has no SiW-Mv2 member.

Do not force SiW-Mv2 into Track A.

Keep Track A as historical/literature MCIO context only, clearly separated from the new Track-B primary population.

## Required amendment scope

Update the canonical scientific docs/configs/preregistration target-domain enumeration and tests before model output. Preserve old MCIO freeze as historical provenance and create a new dated study/config identity rather than rewriting history.

## Final disposition

**1.3S SiW-Mv2 prerequisite inspection — ACCEPTED.**

**Core replacement — APPROVED IN PRINCIPLE, but the repo has not yet implemented the requested protocol/plan rewrite.**

Proceed next with:
1. dated benchmark/protocol amendment;
2. SiW-Mv2 metadata adapter using the Protocol-I intersection/exclusion policy above;
3. remaining MSU adapter.

Do not start model inference before the amended benchmark/config hashes are frozen.
