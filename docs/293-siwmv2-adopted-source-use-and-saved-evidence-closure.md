# 293 - SiW adopted source-use exclusions and saved-evidence closure

Date: 2026-10-23.
Governing review: [292](292-review-doc291-siw-images-and-exact-crossing-resolution.md).
Preserved image campaign: [291](291-siwmv2-local-audit-and-primary-images.md),
commit `baecc438ed36f4b8dfb8cbf2eed39b093f3cda07`.

## Decision

**Local audit and primary-image preparation are complete under the explicitly
owner-adopted `siwmv2-source-use-exclusions-v1` amendment. Image production is
not repeated. Experimental source-use eligibility is resolved by five exclusions,
not by changing the archived population or claiming the original boundaries
were clean. Scientific readiness remains false.**

The [adopted policy](../configs/siwmv2_source_use_v1.yaml),
[concrete indexed overlay receipt](../results/phase1/siwmv2-source-use-overlay293-v1.json)
and [final local closure](../results/phase1/siwmv2-local-closure293-v1.json)
separate archived inventory from effective use. Both SiW summary audit statuses
are now `complete` under this explicit amendment. Their original counts and
frozen metadata/role hashes remain unchanged. OULU/MSU/CASIA rows are unchanged.

## Concrete proposal and owner adoption

The [proposal preparer](../scripts/resolve_siw293.py) reads only saved metadata.
It verifies all5040 original attempt/media/transaction seals, the original plan,
failed terminal and saved readback/visual/full-manifest commitments. It recomputes
the six disjoint byte/full-decoded-sequence pairs and all before/after counts.
It rejects class conflicts, uncorroborated or overlapping groups rather than
expanding this finite amendment.

Before any use policy was adopted, the owner was shown all five exact private
IDs, their retained partners, fixed rationale and complete role/class/detector
counts. The owner selected `adopt_siw293_source_use_exclusions_v1` for the whole
proposal once. There were no chained per-pair approvals or inferred adoption.

Private proposal SHA256:
`de9486756f811b15b269da67284673dee1cb9624ec5a594b6764f4a97f277583`.
Private owner-adoption receipt SHA256:
`d6daac4cd7ab834af3e6486a0162a0ee5d49f36e2c25f0611985806ceaf8ea04`.

Concrete public membership below uses the original291 transaction ordinals,
bound to the unchanged original plan; the private overlay also retains exact
video IDs. Raw video IDs/paths and images remain private.

| Excluded source ordinal | Frozen role retained in inventory | Retained partner ordinal | Partner partition / role | Rationale |
|---|---|---|---|---|
|1606|train|1642|official train / branch_calibration|Retain more held-out source role|
|1614|train|1653|official train / g_domain|Retain more held-out source role|
|1644|train|1623|official test / null|Retain official test original|
|1662|g_domain|1654|official test / null|Retain official test original|
|1665|train|1663|official test / null|Retain official test original|

All five excluded originals are attack-labeled detector successes. They remain
in inventory, transactions, image storage and historical accounting; only source
fitting/calibration/domain-use eligibility changes. Official test copies remain
null-role and source-ineligible. No test scoring/evaluation is authorized.

Fixed retention priority is official test first; among source roles,
`g_domain > branch_calibration > train`. It was published in the complete
proposal before adoption/use and is independent of image quality, detector
success and classifier results. The within-role pair1612/1652 remains active
and disclosed; no extra deduplication/weighting experiment is introduced.

## Reconciled denominators

| Population | Archived originals | Effective originals | Effective bona fide / attack | Effective detector success / failure |
|---|---:|---:|---:|---:|
|Source train|632|628|314 /314|617 /11|
|Source branch_calibration|215|215|105 /110|214 /1|
|Source g_domain|210|209|105 /104|209 /0|
|All source|1057|1052|524 /528|1040 /12|
|Official test, null role|623|623|261 /362|619 /4|
|All|1680|1675|785 /890|1659 /16|

Archived/prepared totals remain1680 originals,785 bona fide/895 attack,
1664 detector successes/16 failures,6672 image assets,1680 strict replay
receipts and306156 native RGB frame hashes. No denominator or frozen role is
rewritten to the effective counts. The SHA256 fields in both CSV summaries still
refer to original frozen metadata/role evidence, not the new effective manifest.
All16 detector failures retain their original selected image and non_accept
disposition. Twelve are source-use eligible but not valid scored-fit examples.
Successful images likewise do not invent model scores: actual fit rows remain0.

The original inventory still contains six pairs/five forbidden crossings:
three official train/test, two source-role-only and one within-role pair.
Effective-use validation recomputes one remaining within-role pair and **zero
forbidden crossings for both byte and full decoded-sequence hashes**. The
original finding is never replaced by zero or waived.

## Consumer and validator integration

[Source-use contexts](../src/fas/source_use.py) validate the owner adoption,
overlay, effective-manifest hashes, exact original joins, role retention,
source/null-test eligibility and active byte/decoded boundary signatures.
They expose role-specific fitting/calibration/domain-use populations, retain
technical-failure denominators and hash-join original saved transactions.
Every bound consumer row carries the exact policy/overlay/manifest binding.
Excluded/test/null and wrong-role rows are rejected before source use.

The [calibration row selector](../src/fas/transactions.py) now requires this
context for SiW-tagged rows; untagged historical/OULU generic behavior remains
unchanged. There is no SiW classifier trainer in this package. Prospective SiW
source consumers must use the verified context, not the archived role CSV alone.
Source-dry-run evidence and every record using SiW as a source must bind the
exact policy, overlay and effective manifest. Analysis-freeze hashes include
the policy, so a later policy change cannot silently reuse a prior freeze.

The normal [validator](../scripts/validate_preregistration.py) now verifies both
archived and effective evidence:

```bash
python scripts/validate_preregistration.py --stage data-audit \
  --frozen-root <permanent-source-roles-v2> \
  --source-use-root <private-siwmv2-source-use293-v1>
```

Actual result: **DATA-AUDIT READY**, zero errors. Omitting the use root, changing
adoption/overlay bytes, reactivating excluded/test rows or violating an active
boundary fails closed. Canonical IDs/labels/partitions and archived role counts
must still reconcile with unchanged frozen bytes. Public-only execution without
private evidence does not become ready.

The [closure checker](../scripts/complete_siw293.py) validates all1052 eligible
source transactions through the appropriate consumer routes. Each route rejects
all628 source-ineligible originals (five excluded plus623 test originals).
It verifies original record seals and unchanged historical evidence again,
reconciles every summary difference against291 and runs the normal validator.
No accepted dataset is reprocessed.

Only the prospective transaction contract evolves among291's pinned producer
sources. Its original SHA256 is checked against the exact reviewed Git blob;
the executed291 source remains recoverable bit-for-bit at the reviewed commit.
Historical source pins, failed terminal, receipts and transactions are not
rewritten, and the old failed producer is not represented as a clean execution.

## Reused image evidence, checks and publication

Closure reuses291's full6672-asset readback and actual five-sheet/108-tile
inspection by hash. It makes **zero media decode calls, zero detector calls,
zero model scores/fits and zero sheet reopenings**. No additional raw-media
campaign, replacement frame or renewed manual-image claim is made.
The bounded92-crop/16-failure-image inspection remains producer-reported evidence,
not independent replication or manual inspection of every original.

Private closure SHA256:
`c627c4ad80a65d6a20af0cea2883e46b51a3321fbe707ff85e57f4bc37088cec`.
Policy SHA256:
`1fc6e58f12733880071834eee6781472409d2fe0f9ebdaeb6e04b10fc810ed8f`.
Overlay SHA256:
`a66de1a67d0f84a60d88e9b515201b94e1bc798d8838c95fea8f4f974b6537a1`.
Effective-manifest SHA256:
`0fd8aeffc230d521ab2f82648812aaec54bc91dcb0c4f08682569a89094a7754`.

Validation:38 focused SiW/eligibility/legacy transaction tests passed in2.611s;
29 separate existing protocol tests passed in100.773s. These are67 distinct
test cases, not sums of the earlier overlapping291 selections. Python compilation,
public schema and the actual private normal-validator/consumer closure passed.
Regression coverage includes all three source consumer routes, raw transaction
hashes, missing eligibility context, test/null rejection, deterministic priority,
preserved within-role duplication, rehashed active-crossing tampering, frozen
metadata joins and per-record source-dry-run provenance.

The eventual reviewed291 CI result is now confirmed:
[run39936224548](https://github.com/lathevinh/fas/actions/runs/39936224548) and
[job120356301738](https://github.com/lathevinh/fas/actions/runs/39936224548/job/120356301738)
completed **success**, including Complete job, for exactly
`baecc438ed36f4b8dfb8cbf2eed39b093f3cda07`. Its installation step took about32m34s;
the earlier pending conclusion was truthful, not a failed scientific gate.
The final implementation's exact published-head CI must be collected after
push; this pre-publication immutable receipt does not invent its own future CI.

Acquisition authenticity, participant identity/disjointness, near-duplicate
independence and transformed/joined ancestry remain uncertified. No classifier
training, target evaluation or global scientific readiness is authorized.
