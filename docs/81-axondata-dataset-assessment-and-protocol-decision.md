# AxonData Dataset Assessment and Protocol Decision

Date: 2026-10-06
Authority: Document 42; owner requested assessment of an alternative to Replay-Attack
Base commit: `0045e71d2c75bdfac5cd8b4b24a64b009f4f8b9a`
Status: **Metadata assessment complete; not qualified as a core replacement**

## Recommendation

Do not replace Replay-Attack with the currently public AxonData sample. Broader
advertised attack coverage and newer capture devices could make the full dataset
useful, but neither establishes protocol suitability or superiority. The public
release does not supply enough verified labels, identities or splits to implement
our leakage-safe source roles and subject-group evaluation.

Keep the frozen four-domain MCIO core unchanged. AxonData is an **unactivated
candidate** for a separately preregistered external physical-attack stress test,
conditional on sufficient metadata, permissions and full-release access. It is
not added to source supervision, core audited counts or readiness gates.

## Evidence and Scope

Repository: https://huggingface.co/datasets/AxonData/liveness-detection-dataset

Pinned source revision: `c28f25c20328748b77c794853134e009df3b36fa`.

Pinned README SHA-256:
`3a0623e3372f2c1926a9b29bd6b9567353a0dffeec38b1fd45843a1cc328c1ee`.

The card, public REST repository metadata, recursive file tree and dataset-server
schema/splits were checked using existing conda env `fas`. No media was downloaded,
decoded or visually inspected; no model output, target performance, installation
or commercial purchase was involved. The dataset-server response does not expose
its source revision, so it is a current observation, not pinned-revision proof.
Its 51 rows agree with the pinned tree's video-file total.

Machine-readable evidence:
[public metadata assessment](../results/phase1/axondata-dataset-assessment.json).

| Property | Publisher card / observed public release |
|---|---|
| Advertised size | Approximately 100,000+ videos in the full commercial offering; not verified |
| Actual public video files | 51: 28 MP4 and 23 MOV |
| Other public media | 25 JPG files under `Selfies` |
| Total public repository file size | 2,240,134,782 bytes, approximately 2.24 GB; not downloaded |
| Advertised attack coverage | Print/replay and multiple mask types; 11+ types claimed |
| Observed video directory groups | Paper masks 18, latex masks 10, silicone masks 11, textile masks 12 |
| Dataset-server schema | Only `video: Video`; no label, subject, session or device columns |
| Dataset-server splits | Only `train`, 51 rows; no documented subject-disjoint split |
| Non-media repository files | Only README and Git attributes; no annotation/protocol manifest found |
| Public card license | Publisher declares CC BY-NC 4.0; commercial full-version terms are separate |

Directory groups are storage observations, **not accepted label annotations**.
No labeled bona-fide, print or replay video group was observed in that tree; media
content was not checked. The README's `live` class and attack table describe the
offering, not a row-level mapping of these public files. `Selfies` does not establish
live-video availability, paired subjects, genuine presentation or evaluation roles.
Do not build a classifier split where image/video modality is confounded with class.

## Why It Cannot Currently Replace Replay-Attack

1. **Public sample versus full release.** The accessible 51 videos are not the
   advertised 100,000-video corpus. Its participant count, class balance, recording
   diversity and representativeness cannot be inferred from sales copy.
2. **Essential labels and identity are unresolved.** Our adapter needs authoritative
   bona-fide/attack labels and stable subject/video/capture IDs. Mask numbers or
   `id` folder tokens do not establish biometric identity. Unknown subject IDs cannot
   be treated as independent videos or synthesized to make grouping pass.
3. **Leakage controls are unavailable.** No subject-disjoint roles or original-capture
   lineage is documented. Multiple clips, extracted selfies, shared masks, attack
   performers and the biometric identity being presented may require different
   grouping. Related Axon releases may overlap; actual overlap remains unknown.
4. **Benchmark meaning would change.** MCIO specifically denotes the four established
   OULU/CASIA/Replay/MSU domains. Substitution creates a different benchmark even if
   there are still four domains. A mask-heavy sample also changes physical attack
   coverage; it does not preserve Replay's print/replay and environment protocols.
5. **Access and provenance still matter.** The public license is non-commercial,
   not permission to use an unspecified commercial release or proof of participant
   consent and third-party provenance. The card's aggregation wording does not
   establish whether source material overlaps any core benchmark.

Better image quality, diversity and downstream performance have not been measured.
The publisher's iBeta-level labels do not certify this dataset, our model or any
ISO/IEC 30107-3 evaluation; certification requires the applicable independent test
process and evidence. Larger/newer is not automatically a stronger research protocol.

## Conditions for Later Use

Ask the publisher for the following before acquisition or activation:

- A versioned sample/full-release manifest with authoritative per-video labels,
  attack family/instrument/material, live-video coverage and class counts.
- Stable biometric subject IDs, attack-performer IDs where distinct, session,
  video and original-capture IDs; explicit lineage for paired/extracted images
  and duplicate/near-duplicate grouping. Record device and environment when available.
- Documented subject-disjoint splits or enough identity/lineage evidence to freeze
  independent roles before any fitting. A literal folder called `train` is not a protocol.
- Acquisition origin and derivation: original Axon collection versus reused data,
  overlap with core benchmarks and related Axon products, consent/use authority,
  license/access approval and publication permissions for the exact release.
- Actual participant/class/session/device counts, not only marketing totals;
  any source document supporting claimed certification or testing status.

After those inputs pass intake and metadata/media audits, define a dated external
protocol before computing its model predictions: eligible RGB physical attacks,
subject/capture grouping, frame sampling, evaluation transactions and outcomes,
fixed source-only thresholds, bootstrap units and separate reporting of mixed-domain
versus genuinely held-out attack-family transfer. Do not tune prompts, thresholds,
crop settings or method choices on the external target. Attack-family novelty is
defined relative to source supervision, not the publisher's product name.

If the owner instead chooses a core substitution after these requirements are met,
that requires an explicit dated amendment and new benchmark name before affected
target output exists. Update the charter/data plan/paper contract, domain constants,
manifest contracts, four folds, frame rules, role policy, evidence schemas, validation
tests and readiness gates together; do not merely rename Replay in one YAML file.
Any revised core would be reported separately, not as canonical MCIO.

## Current Protocol and Next Action

No frozen config, domain constant, canonical plan algorithm, seed or readiness
count changed. Replay-Attack prerequisites in
[Document 80](80-phase1-step1.3-replay-attack-prerequisites.md) remain unresolved.
This assessment is based only on metadata/access suitability, not target results.

The owner can either provide Replay's local metadata/release to resume the accepted
core, or obtain the Axon manifest/access clarification above for a new eligibility
review. No Axon adapter or optional experiment is activated by this assessment.
Documentation/evidence consistency and the schema gate are checked in `fas`;
there is no new model-quality result or new adapter test-count claim.