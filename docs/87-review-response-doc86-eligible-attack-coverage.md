# Review Response to Document 86: Eligible Attack Coverage

Date: 2026-10-08
Reviewed document: [Document 86](86-review-doc85-siwmv2-amendment-response.md)
Document baseline: `d257cae`
Scope: review with actual header/list evidence, not benchmark/config activation

## Finding: Distinguish Reference Attack Types from Canonical Attack Families

**Medium priority, terminology/schema clarification; not a replacement blocker.**
Document 86's proposed table calls its 14 rows `attack_family`. The verified
14 categories are the reference dataset's **attack types**, not automatically
the project's canonical semantic families. For example, the existing CASIA
adapter preserves a reference attack type while separately mapping it to `print`
or `replay`. [The dataset plan](04-data-and-protocols.md#L67) likewise distinguishes
`family -> instrument -> subtype`.

Use `reference_attack_type` (or an explicitly defined `attack_type`) for this
14-row coverage table. Preserve the raw reference token and source folder, and
version any mapping to a broader canonical `attack_family` separately. Do not
invent a family mapping from a filename substring or silently redefine family
granularity between datasets. This distinction matters for role stratification,
attack-shift interpretation and optional family-level analyses; the binary PAD
label contract remains bona fide = 0, attack = 1.

No other blocking methodological objection to Document 86 was found. Its request
to verify eligible membership rather than raw-folder counts is correct, and the
required empirical check can be settled now rather than by another conceptual loop.

## Actual Eligible Coverage Check

Read the local ZIP central directory and six exact source files verified by
[the prerequisite inspector](../scripts/inspect_siwmv2.py). Reused the strict
folder/prefix validation before counting. Converted Protocol I balancing lists
to unique-token membership; no video payload, frame, detector or model was read.

Reference commit: `8667dbcd316b38141729c057adf7517fe0602608`.
Reference file hashes: [original prerequisite evidence](../results/phase1/siwmv2-prerequisites.json).
The freshly computed header-inventory digest matches the original report:
`2e08944154d49e531d727bd3320e798690e8b8ba144780153bbab857b5fb4582`.

| reference_attack_type | Eligible train | Eligible test | Eligible total | Out of protocol |
|---|---:|---:|---:|---:|
| Makeup_Co | 28 | 24 | 52 | 0 |
| Makeup_Im | 39 | 22 | 61 | 0 |
| Makeup_Ob | 12 | 10 | 22 | 0 |
| Mask_Half | 52 | 20 | 72 | 0 |
| Mask_Mann | 26 | 14 | 40 | 0 |
| Mask_Paper | 11 | 6 | 17 | 0 |
| Mask_Silicone | 9 | 8 | 17 | 0 |
| Mask_Trans | 24 | 35 | 59 | 1 |
| Paper | 79 | 56 | 135 | 0 |
| Partial_Eye | 34 | 23 | 57 | 0 |
| Partial_Funnyeye | 96 | 64 | 160 | 19 |
| Partial_Mouth | 17 | 12 | 29 | 0 |
| Partial_Paperglass | 47 | 29 | 76 | 0 |
| Replay | 59 | 39 | 98 | 0 |
| **Total** | **533** | **362** | **895** | **20** |

**All 14 reference attack types have nonzero eligible membership in both training
and testing.** The exclusions remove 19 `Partial_Funnyeye` videos and one
`Mask_Trans` video; they do not remove an entire type from either partition.
Counts are unequal and no balancing or minimum per-type performance claim follows.

With 524 live train and 261 live test members, the combined prospective population
remains 1,057 source-eligible training videos and 623 target-eligible test videos,
or 1,680 overall. Eleven unavailable live list references remain missing protocol
media, not attempted transactions; excluded videos remain in the raw inventory.

This table is a metadata evidence snapshot, not a frozen eligible-ID manifest or
an accepted data/media audit. The upcoming amendment must freeze its exact IDs,
mapping version, exclusion reasons and lineage. The historical blocked report is
not overwritten: its raw-universe/list-mismatch observations remain true.

## Refinements for the Amendment

- Accept Document 86's explicit **SiW-Mv2 Protocol-I intersection population** wording.
- Incorporate Document 85's grouping fallback at every split boundary. Video-level
  bootstrap must stay paired across systems/seeds and within target, without claiming
  verified participant clustering. With one Track-B transaction per video it is
  transaction/video-level resampling, as Document 86 correctly states.
- Preserve per-type coverage diagnostics after permanent source-role assignment.
  Presence in eligible train/test does not prove presence in every fitting/calibration/
  gate subset. Do not introduce an all-14-in-every-role gate or require per-type
  `N_error_min=20`; neither is part of the frozen primary decision rule.
- Any later feasibility adjustment uses only source-eligible metadata and the
  globally versioned role policy, not target performance. Do not manipulate
  membership/weights to make attack counts equal or pass an effect threshold.
- Leave unknown participant IDs unknown, retain duplicate/ancestry audits, and
  report video grouping's limitations rather than requesting a participant map as
  an unconditional prerequisite again.

## Disposition

**Document 86 accepted in substance, with the type/family field clarification.**
Its new eligible-coverage question is answered affirmatively by actual metadata:
all 14 types survive in each partition. No reason was found to reopen the
Replay-Attack replacement direction, demand provider list repair, or redesign
the RQ1/RQ2 formulas and frozen pass rules.

The next implementation checkpoint is the dated benchmark/config amendment,
including the exact intersection, new study identity, complete video fallback
policy, preserved historical MCIO/Track A context, and the verified coverage above.
Push and review that checkpoint before the metadata adapter and then MSU.
This review turn does not implement the amendment or authorize model execution.

Document 85's exact commit `5602428306bf5b6487579543b963751d5858393b` also has
independently verified `validate: completed / success` CI:
https://github.com/lathevinh/fas/actions/runs/37729261316/job/113154426314.
That is prior documentation/contract CI, not SiW-Mv2 scientific readiness.