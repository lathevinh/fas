# 88 - Dated Benchmark Amendment: SiW-Mv2 Protocol-I Intersection

Date: 2026-10-08
Checkpoint: 1.3A, benchmark/config amendment only
Base commit: `85c3c38a1ba991ff17d562f8db11a264e124c64b`
Status: checkpoint 1.3A accepted in Document 89; not data readiness or evaluation authorization

## 1. Authority and exact scope

This is the dated amendment authorized by the owner's replacement direction in
[Document 84](84-review-siwmv2-replacement-and-protocol-amendment.md), refined by
[Document 85](85-review-response-doc84-siwmv2-amendment.md), accepted with an eligible-coverage
requirement in [Document 86](86-review-doc85-siwmv2-amendment-response.md), and verified in
[Document 87](87-review-response-doc86-eligible-attack-coverage.md).
The amendment is accepted in [Document 89](89-review-doc88-benchmark-amendment.md);
its required dataset-holdout versus evaluation-population clarification is incorporated below.

For the specific benchmark population and grouping changes below, this amendment
supersedes the historical MCIO wording in Documents 04, 05, 38, 40 and 42.
[Document 42](42-data-to-experiment-implementation-plan.md) still controls every
unchanged method, fitting, gate, estimand, claim and evaluation rule. The checkpoint
approval policy in [Document 65](65-phase1-checkpoints-and-preflight.md) is unchanged.

This checkpoint does not implement a SiW-Mv2 metadata adapter, MSU adapter, role
allocator, media extraction, acquisition audit, model inference, training or target
evaluation. Header/list population definition is not accepted media metadata.

## 2. New study and historical lineage

Current study ID: `strict_single_image_ocmsiwmv2_oof_risk_v2`.

The primary domain set is OULU-NPU / CASIA-FASD / MSU-MFSD / SiW-Mv2:

| Outer target | Source domains |
|---|---|
| OULU-NPU | CASIA-FASD, MSU-MFSD, SiW-Mv2 |
| CASIA-FASD | OULU-NPU, MSU-MFSD, SiW-Mv2 |
| MSU-MFSD | OULU-NPU, CASIA-FASD, SiW-Mv2 |
| SiW-Mv2 | OULU-NPU, CASIA-FASD, MSU-MFSD |

The design is **cross-dataset held-out evaluation using dataset-specific frozen
source and evaluation populations**. Holding out a dataset excludes every sample
from that dataset from fitting and selection for the fold; it does not make the
entire physical release the evaluation population.

SiW-Mv2 is held out as a dataset in the OCM->S fold, and evaluation is performed on
its frozen Protocol-I test-intersection population (623 videos). No SiW-Mv2 sample
enters fitting, calibration, gate selection, or method selection for that fold.
The 1057 train-intersection videos are not target transactions in this fold; they
are source-eligible only in the other three outer folds. The combined 1680-video
benchmark inventory is not the SiW-Mv2 target population.

The previous `strict_single_image_mcio_oof_risk_v1` config is preserved byte-for-byte
in [experiment_core_mcio_v1.yaml](../configs/experiment_core_mcio_v1.yaml), SHA-256
`dc636a9bad8c427a83149a7697cc64a1bb38f31752303500cc2eb5b606e998b9`.
It is historical, not an active recipe. Track A is historical MCIO literature
context only; the new estimates must not be called MCIO estimates or exact MCIO
reproductions. Track B remains strict one-image-per-video evaluation.

The changed population also changes source composition in three folds, SiW-Mv2
source/target support, attack exposure and grouping approximation. RQ1/RQ2 formulas
and pass rules remain fixed, but their estimates are conditional on this new
four-domain population.

## 3. Exact SiW-Mv2 population freeze

Paper-facing name: **SiW-Mv2 Protocol-I intersection population**.
Population ID: `siwmv2_protocol_i_intersection_v1`.

Use unique video-token intersection of the supplied archive headers with the pinned
ECCV22 reference lists at commit `8667dbcd316b38141729c057adf7517fe0602608`.
All six source-file hashes are frozen in the
[redacted intersection evidence](../results/phase1/siwmv2-intersection-v1.json).
Protocol II unknown-attack LOO and Protocol III subdomains are not adopted.

| Partition | Bona fide | Attack | Total | Use |
|---|---:|---:|---:|---|
| Reference train intersection | 524 | 533 | 1057 | Eligible source pool when SiW-Mv2 is a source |
| Reference test intersection | 261 | 362 | 623 | Target transactions only when SiW-Mv2 is the outer target |
| Combined | 785 | 895 | 1680 | Exact benchmark population, not the full 1700-video release |

The 867 repeated spoof-train rows are deduplicated membership entries. They are not
extra transactions, independent groups, implicit sample weights or changes to the
frozen branch/risk objectives.

All 20 archive videos absent from the lists stay in raw inventory with explicit
`out_of_protocol` reason, outside primary source and target populations. The 11
missing live references stay explicit (`train: 7`, `test: 4`) with
`listed_missing_from_archive` reason; they are not attempted transactions or detector
failures. Do not change denominator accounting for genuine detector failures.

The immutable exact-ID record `siwmv2_protocol_i_intersection_v1.json` is outside Git.
It contains eligible membership, reference split, label, type/family, null subject,
video group and individual exclusion/missing-reference reasons. No IDs, media or
access documents are published.

| Identity | SHA-256 |
|---|---|
| Private membership record bytes | `47ca2bb8896d5937ff7ea735242dd410f83f8a65e6b5655a6709ef2b4e1fb3ae` |
| Train eligible IDs | `1ad6cf790d7258c7e1d3b9e4cadf5217283a6f0a0d65ce7f74d35829efb103f6` |
| Test eligible IDs | `32bc58db1c6c871e57c64392bc21053a7bdbcfe1878349eff016ca12e02edad6` |
| ZIP header inventory | `2e08944154d49e531d727bd3320e798690e8b8ba144780153bbab857b5fb4582` |
| Public intersection evidence bytes | `7ccbd4b4a10aaa8249efe2b122e149b1f4fe4b3ec8fbd1bf23d2d42a3a734190` |

Eligible-ID hashes use sorted IDs joined with LF plus one terminal LF. Private-record
hash uses the exact UTF-8 JSON bytes written by the immutable-record writer. Header
inventory hash is not an archive SHA-256 or integrity/decode certification.

## 4. Type coverage and separate family mapping

Mapping version: `siwmv2_attack_family_v1`. Preserve the exact reference type token;
the operational coarse family is a separate field, not an inferred instrument,
material, participant identity or certified provider ontology.

| reference_attack_type | attack_family | Train | Test | Eligible total | Excluded |
|---|---|---:|---:|---:|---:|
| Makeup_Co | makeup | 28 | 24 | 52 | 0 |
| Makeup_Im | makeup | 39 | 22 | 61 | 0 |
| Makeup_Ob | makeup | 12 | 10 | 22 | 0 |
| Mask_Half | mask | 52 | 20 | 72 | 0 |
| Mask_Mann | mask | 26 | 14 | 40 | 0 |
| Mask_Paper | mask | 11 | 6 | 17 | 0 |
| Mask_Silicone | mask | 9 | 8 | 17 | 0 |
| Mask_Trans | mask | 24 | 35 | 59 | 1 |
| Paper | print | 79 | 56 | 135 | 0 |
| Partial_Eye | partial | 34 | 23 | 57 | 0 |
| Partial_Funnyeye | partial | 96 | 64 | 160 | 19 |
| Partial_Mouth | partial | 17 | 12 | 29 | 0 |
| Partial_Paperglass | partial | 47 | 29 | 76 | 0 |
| Replay | replay | 59 | 39 | 98 | 0 |
| Total | 5 coarse families, 14 reference types | 533 | 362 | 895 | 20 |

Every eligible attack has one mapping, and all 14 types have nonzero train and test
membership. This is not a balance claim, unknown-attack evaluation, or assurance
that every future source role contains all 14 types. Report role-level type counts
and any zero cells during role feasibility; do not invent an all-14-per-role gate or
per-type `N_error_min=20` claim gate.

## 5. Grouping policy at every boundary

OULU-NPU, CASIA-FASD and MSU-MFSD retain the required subject-group policy; actual
identity authority must still be verified in pending dataset/media audits. SiW-Mv2 uses
complete video groups because participant identity is genuinely unavailable. Its
`subject_id` stays null in JSON and empty in CSV; never copy the video ID into the
subject field or use one shared `unknown` subject group.

The same declared grouping unit applies to permanent source roles, head inner
validation, matched sample-OOF, fold-local calibration, all derived frame/crop ancestry
and target bootstrap. No frame/crop from one video may cross those boundaries.
Domain-OOF still excludes a whole source dataset from pseudo-fold fitting and
calibration, not videos in place of datasets. Its pseudo-target predictions cover
the prescribed OOF candidate pool inside that dataset's frozen source-eligible
population, not every video in its physical release or its outer-test partition.

Permanent roles remain independent of outer target and training seed. Only the 1057
train-intersection videos may receive SiW-Mv2 source roles. Test videos must not be
reclassified into source-train, validation, calibration or gate pools.

For SiW-Mv2, paired uncertainty resampling is video-clustered within target, using
the same multiplicities across methods/seeds. One Track-B transaction per video makes
this transaction/video resampling. It is not participant-clustered CI; dependence
between different videos of one person remains uncontrolled and may make intervals
optimistic. No participant-disjointness claim is permitted.

## 6. Executable contracts and unchanged method

[benchmark_amendment_v2.yaml](../configs/benchmark_amendment_v2.yaml) is referenced by
the active experiment config and included in analysis artifact hashes together with
the public population evidence and historical config snapshot.

Schema validation rejects old domains/study ID, changed population pins, missing
group boundaries, fake participant certification, changed repeat semantics, evidence
drift and historical snapshot drift. Source-evidence, seed aggregation, transaction
ledger and freeze construction use the same amended domain set, rejecting MCIO
records in the active study. Intake still recognizes historical releases; recognizing
a dataset for intake never makes it active core data.

Data-summary schema now distinguishes `group_unit` and group counts from participant
counts. SiW-Mv2 subject count remains empty, never 1680. Its metadata requires separate
`reference_attack_type` and `attack_mapping_version` columns. Data-audit checks exact
partition ID hashes, class counts, type counts/mapping and train-only source roles,
not merely self-consistent CSV hashes. Public summaries remain `not_audited`.

Only the four core datasets are mandatory in data readiness. Optional SiW-M is not
SiW-Mv2 and is not a core readiness dependency; this closes the pre-existing mismatch
explicitly recorded in Document 65 before checkpoint 1.5.

No change to models, prompts, preprocessing, seeds, fitting losses, calibrators,
fixed fusion, risk feature sets, competence dependencies, source operating-point
selection, K=1 accounting, RQ1 fixed-error AP, RQ2 class-balanced raw AURC, aggregation,
effect thresholds or harm guardrails is authorized. For SiW-Mv2 only, historical
"subject-disjoint" inner/sample-OOF wording is interpreted as video-group-disjoint
under this explicit fallback; it does not assert subject separation.

## 7. Acceptance criteria and checks

1. Active config specifies a new study and exactly four amended domains; MCIO
   historical config bytes and Track-A context remain intact.
2. Exact private eligible/excluded/missing-reference membership is immutable and
   pinned; public hashes/counts reproduce from the supplied headers and pinned lists.
3. Train/test attack counts reconcile to 533/362; all 14 reference types survive both
   partitions and the separate mapping is versioned.
4. Video fallback covers all six boundaries without fabricated subjects or
   participant-disjointness/CI claims; optional SiW-M cannot block core readiness.
5. Focused negative/positive tests and full regression pass in `fas`; schema exits 0,
   while data-audit, source-dry-run, analysis-freeze and locked-evaluation remain blocked.
6. Push this checkpoint and stop for owner confirmation before any dataset adapter.

Local verification is recorded in
[benchmark amendment verification](../results/phase1/benchmark-amendment-verification.json).
Full regression: 146 tests, zero failures/errors/skips, in conda `fas` on Python 3.12.14.
Focused suites: SiW-Mv2 11, governance 13, preregistration 24, statistical/ledger
contracts 23, freeze 5. Actual CLI exits: schema 0; all four later stages 1 (blocked).
The actual private membership and redacted summary were rederived with ZIP payload
opening prohibited; both match the frozen bytes/hashes. Method-config bytes and the
historical MCIO config snapshot were independently checked against the base commit.
Synthetic readiness fixtures use fictional membership and explicitly repin their
temporary evidence hash; they do not claim that fictional media are the real dataset.
Historical immutable prerequisite results remain historical, including Document 83's
now-corrected list/subject blocker wording. Documents 85-88 govern the correction.

Recheck focused tests and schema:

```bash
conda run -n fas python -m unittest discover -s tests -p test_siwmv2.py -v
conda run -n fas python -m unittest discover -s tests -p test_governance.py -v
conda run -n fas python -m unittest discover -s tests -p test_preregistration.py -v
conda run -n fas python -m unittest discover -s tests -v
conda run -n fas python scripts/validate_preregistration.py --stage schema
```

Recreate the population freeze only into new output paths:

```bash
conda run -n fas python scripts/inspect_siwmv2.py \
  --archive "<local-SiW-Mv2.zip>" \
  --reference-root "<private-pinned-source_SiW_Mv2>" \
  --intersection-private-out "<new-private-ID-record-outside-Git>" \
  --out "<new-redacted-summary.json>"
```

Intersection-freeze mode exits 0 for successful definition, not scientific readiness;
the original prerequisite-inspection mode retains exit 1 for its blocked readiness
report. Both refuse overwrite and read no media payload. The owner-supplied archive
is not moved or modified by this checkpoint.

## 8. Stop boundary

Checkpoint 1.3A is accepted by Document 89, which confirms successful CI on the
exact implementation commit `6ad2d37eabd1388f29844cc51c791e4885ad420b`. The required
population wording clarification is incorporated here and in the controlling
implementation plan and paper skeleton; no benchmark redesign or config change is
required. The next permitted checkpoint is the SiW-Mv2 metadata adapter consuming
these frozen pins and grouping rules. MSU remains a separate later adapter checkpoint.
This prose update does not implement either adapter. All acquisition/media and
model-execution gates remain pending.