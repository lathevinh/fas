# 299 - Complete fixed source experiment and clustered source evidence

Date: 2026-10-26.
Governing review: [298](298-review-doc297-first-source-fitting-and-oof-results.md).

## Actual result

**All12 registered outer-target/seed combinations completed. The normal
schema, data-audit and scientific source-dry-run validators pass. Domain-OOF
does not win the primary heterogeneous source diagnostic: all12 paired
domain-minus-sample AP intervals are negative. Standalone OpenCLIP fails
competence in all12 combinations. Neither fact was tuned away.**

The [actual execution receipt](../results/phase1/source-run299-v1.json) includes
all combinations, controls, per-source drift, uncertainty/support and
claim-specific source applicability. The canonical
[competence](../results/source-dry-run/competence.json),
[applicability](../results/source-dry-run/applicability.json) and
[evidence](../results/source-dry-run/evidence.json) files are real outputs of
the completed worker, not readiness placeholders. Passing these source
prerequisites is not evidence that RQ1 or RQ2 succeeds on target data.

The immutable [analysis freeze](../results/analysis-freeze/freeze_record.json)
was created through the normal CLI from clean source-evidence commit
`14b29a4ff04f4d7ff40b276edf2eafe7e4a69cd1`. Normal analysis-freeze validation
passed before committing the record; its committed persistence is checked
again at publication. No locked-evaluation authorization exists.

## Scope

This package continues the fixed experiment rather than tuning away297's
unfavorable comparison. The registered backbones, fixed prompts,200-epoch head
budget, seeds, monotone calibration family, risk objectives and permanent roles
are unchanged. All accepted data/image milestones remain closed.

The [generalized controller](../scripts/run_source299.py) covers all four
outer-source rotations and all three registered seeds. A dataset's images may
be read as source for the other rotations; its complete population is excluded
from fitting, selection, calibration and prediction whenever it is the outer
target. There are no target predictions, target tuning or locked-evaluation
authorization.

| Outer target excluded | Original effective source denominator | Successful source-image inputs | Retained source failures |
|---|---:|---:|---:|
|OULU-NPU|1932|1906|26|
|CASIA-FASD|6282|6261|21|
|MSU-MFSD|6602|6583|19|
|SiW-Mv2|5830|5815|15|

These fold-local populations overlap. Their union remains6882 source-use
originals,6855 successful images and27 failures; it is not the7510-original
archive. SiW's623 null-role test originals and five adopted exclusions never
enter source consumers. The accepted prepared-image manifests retain their
historical unscored fields; new scores and genuine error labels live in
separate versioned prediction tables, not overwritten preprocessing receipts.
Failures remain original non-accepts without fabricated features/errors.

## Fresh combined authority and reuse

The owner explicitly selected
`approve_source299_complete_fixed_source_experiment` after executable code,
source/split inputs, counts and resource estimates had been sealed in the
[plan](../results/phase1/source-plan299-v1.json) and
[configuration](../configs/source_run299_v1.yaml).

Original authority start:1793005897.0693569 Unix seconds. The work cutoff is
5h30m and final deadline6h from that same clock. Caps are12GiB combined
process-tree RSS,12GiB CUDA allocated/reserved and4GiB owned new+temporary
artifacts. Planning allows20 minutes for extraction, two hours for fitting,
two hours for diagnostics/bootstrap and one hour for IO/readback/closure,
without promising a wall-time. The first failure/cap violation stops execution;
there is no automatic retry, extension, installation or model substitution.

The completed297 worker, fourteen fitted heads, twenty-one calibrators,
seven primary contexts, all original predictions and24 risk models are
hash-verified before reuse. Its1906-image features and quality are reused
without pixel decoding or model replay. Every unchanged budget context also
reuses its primary fitted state. No unchanged297 context is retrained.

Only4949 previously uncached OULU successful images need new features, and only
as source for the CASIA/MSU/SiW outer rotations. This permits14847 new image
forwards, not another6855-image extraction campaign. Existing registered
checkpoints and fixed text embeddings are reused by digest. The full feature
payload is98,273,280 FP32 bytes. No new weights/text inference, video decoding,
detector call or image-campaign adjudication is performed.

The new cache retains deterministic32-original atomic no-overwrite shards,
exact native RGB crop hashes/shapes, finite FP32 dimensions, sample/key joins
and saved readback. Keys bind full extraction/runtime/normalization contracts;
fitted state is never imported from a target-dependent context. Shards and
completed context files remain durable on interruption.

## Fixed comparisons and diagnostics

All seven primary contexts per outer/seed retain train-only head fitting/inner
validation, separate branch calibration, complete pseudo-domain or group-safe
OOF exclusions, and permanent G_domain separation. Both primary strategies
predict precisely the same non-gate original IDs once. The shared DINO anchor
is fitted once per context and reused by both complete pairs.

The [experiment implementation](../src/fas/source_experiment.py) and
[diagnostics](../src/fas/source_diagnostics.py) add the following in the same
execution package:

- **Fit-size sensitivity:** cap head-fitting inputs at that combination's
  smallest primary OOF fit pool. Select entire subject/video and exact-frame
  connected components by fixed hash rank and round-robin source/class
  strata. Inner validation/calibration and the OOF universe stay unchanged.
  The cap is407-779 images in this package. Whole groups occasionally leave
  a0-6-image shortfall; report actual counts rather than assert perfect count
  equality or split groups. Both risk strategies use the same original final
  classifier/G_domain errors, not new final classifiers.
- **Without-quality attribution:** fit R_DV and R_DVd with q removed, alongside
  the six registered +q vectors. Report paired with-minus-without-quality and
  no-quality disagreement diagnostics without changing the primary model.
- **Domain identifiability:** fixed C=1 multinomial logistic audit on R_DVd,
  with a deterministic group-safe held-out third within each source and
  equal-domain training weights. Chance is1/3. Audit results do not select a
  feature-removal policy.
- **OOF-to-final drift:** mean, standard deviation and KS distance for every
  R_DVd feature, overall and by source. Compare the same non-gate originals.
  Final-model reference predictions are explicitly in-sample source
  diagnostics, not held-out competence predictions.
- **Clustered uncertainty:**2000 source-domain-stratified bootstrap replicates,
  using subjects for OULU/CASIA/MSU and videos for SiW. Competence uses
  domain-OOF equal-source macro AUROC and its percentile95% lower bound.
  Paired G_domain AP contrasts use the same transactions, errors and cluster
  multiplicities. Invalid one-class replicates are counted, not filled with
  synthetic scores; fewer than95% valid replicates leaves uncertainty
  unestimable. This is conditional-on-saved-model uncertainty, not a bootstrap
  refit of the training algorithm.
- **Applicability:** derive complete-system and standalone point/uncertainty
  predicates, the shared-anchor nondegeneracy flag, source risk-fit event
  support and claim-specific eligible/not-applicable states. These are
  source prerequisites, not target RQ1/RQ2 decisions.

Quality statistics preserve297's explicit convention: estimate once from
the final head-fitting pool and share across both OOF strategies and controls.
They are not separately estimated inside every pseudo-domain remainder.
G_domain never fits those statistics, base models, calibrators or risk models.
Probabilities/disagreement remain unstandardized; risk fitting retains natural
error prevalence inside each equally weighted source domain.

The preflight maximum is274 new heads,411 new branch calibrators,456 new risk
fits and48 domain-audit fits, in addition to retained297 states. Inadequate
source error/correct counts produce a real not-applicable record, not a
degenerate fit.

## Numerical and freeze-tool fixes

A synthetic end-to-end regression exposed a real optimization-boundary issue:
OpenCLIP raw logits are FP32, and NumPy scalar promotion can leave an affine
objective in FP32 despite float64 optimization parameters. That quantization
caused an observed L-BFGS-B line-search failure. New calibrator optimization
inputs are explicitly converted to float64. The objective, positive-slope
family, optimizer limits and model settings do not change. This is a
pre-authority numerical guard, not a source-performance-driven adjustment.
The already accepted297 calibrators and their original predictions remain
byte-identical and are not retroactively refitted.

The existing freeze CLI imported a nonexistent legacy domain constant and
could not receive the accepted external frozen/adopted-use roots. It now uses
the registered core domains and forwards both roots through the normal source
gate. Freeze validation also previously compared its creation commit to HEAD,
making the act of committing an otherwise unchanged record invalidate it.
The repaired check requires the original creation commit to be an ancestor,
all pinned code/config/evidence paths identical between that commit and HEAD,
current hashes equal the immutable record and a clean worktree. It does not
weaken source competence, artifact identity or target authorization.

A regression creates a real temporary Git repository, validates the untracked
record, commits it and validates again; a subsequent pinned-file change is
rejected. The immutable record is never rewritten to follow newer commits.

## Actual execution and saved-output closure

The original supervised attempt completed in1227.56s (20m27.56s).
Saved-output closure completed1298.07s after the same original approval.
Sampled combined supervisor/worker-tree RSS peaked at1,942,110,208 bytes;
owned new+temporary artifacts peaked at536,862,709 bytes. Maximum final CUDA
allocated/reserved peaks across encoders were642,748,416/704,643,072 bytes.
All are below the original caps. No retry, deadline reset or added authority
was used.

Each backbone now covers exactly6855 successful source images, reusing1906
rows and computing4949 new rows:14847 new image forwards total, zero new
text forwards/downloads. The new fits are274 DINO heads,411 monotone
calibrators,456 risk models and48 domain-audit models. Preserved297 contributes
fourteen heads, twenty-one calibrators and24 risk models. Twelve additional
budget contexts reuse an identical primary state rather than fitting again.
All480 risk fits meet their source training event requirements; there are no
invented not-applicable fitting records.

The [saved-output closure](../results/phase1/source-closure299-v1.json)
verifies all288 saved head states, including earliest-minimum selection and
the selected validation loss, all primary calibration threshold policies,
171612 reconstructed source prediction rows and480 risk models' held-out
probabilities/error labels/AP. It checks complete OOF table joins, shared
quality statistics, cache contracts/hashes and all seven reused297 contexts.
This count is context prediction rows, not distinct originals; identical
reused budget contexts are not counted twice. Closure performs zero encoder
calls and zero optimization calls. Private models, arrays, identities and
prediction rows remain private; public evidence contains aggregate results
and commitments only.

199 of288 heads select epoch200, the fixed endpoint. The other89 select
earlier epochs. Neither selection under this fixed budget nor closure proves
optimizer convergence or an optimal training duration.

Successful non-gate/G_domain counts per seed are1524/382 for outer OULU,
5009/1252 for CASIA,5264/1319 for MSU and4652/1163 for SiW. Both strategies
and both fit-size controls share those same original identities. Failure-
inclusive source denominators remain those reported above.

## Source competence and applicability

Each cell below is domain-OOF macro AUROC /95% lower bound /balanced accuracy.
All2000 clustered replicates are valid for every complete-system competence
record. DINO anchor, heterogeneous and same-family systems pass the fixed
competence predicates in all12 combinations. Both claim-specific
applicability records are **eligible** in all12; this is prerequisite
eligibility, not a positive hypothesis verdict.

| Outer target excluded | Seed | Heterogeneous | Same family |
|---|---:|---:|---:|
|OULU|20260917|.8912 /.8653 /.7596|.9453 /.9294 /.8068|
|OULU|20260923|.9159 /.8946 /.7912|.9521 /.9370 /.7688|
|OULU|20261001|.8983 /.8761 /.7485|.9336 /.9175 /.7633|
|CASIA|20260917|.8021 /.7747 /.7357|.8175 /.7970 /.7418|
|CASIA|20260923|.8201 /.7942 /.7472|.8420 /.8216 /.7687|
|CASIA|20261001|.8287 /.8035 /.7491|.8550 /.8348 /.7819|
|MSU|20260917|.8388 /.8231 /.7081|.8633 /.8465 /.6845|
|MSU|20260923|.8410 /.8252 /.6928|.8704 /.8523 /.6761|
|MSU|20261001|.8517 /.8359 /.6875|.8894 /.8716 /.6721|
|SiW|20260917|.8456 /.8184 /.6735|.8973 /.8758 /.6785|
|SiW|20260923|.8514 /.8240 /.6731|.9073 /.8880 /.6734|
|SiW|20261001|.8502 /.8221 /.6577|.9022 /.8814 /.6640|

Standalone OpenCLIP AUROC/BA is.5788/.5061 for outer OULU,
.5445/.4968 for CASIA,.5602/.5010 for MSU and.5332/.5012 for SiW,
unchanged across the three seeds within each rotation. It fails the
registered BA competence requirement everywhere. These outcomes do not
justify replacing the branch, altering prompts or reversing score polarity.

## Primary paired source risk comparison

R_DVd includes quality. AP ranks errors, not PAD accuracy. Delta is
domain-OOF minus matched sample-OOF on the same final classifier, G_domain
originals and error labels; the interval is paired clustered95%.

| Outer target excluded | Seed | Errors /G_domain | Domain AP | Sample AP | Delta [95% interval] |
|---|---:|---:|---:|---:|---:|
|OULU|20260917|27 /382|.3168|.6212|-.3044 [-.4511,-.1474]|
|OULU|20260923|25 /382|.1873|.5197|-.3324 [-.4861,-.1989]|
|OULU|20261001|26 /382|.2748|.6226|-.3478 [-.5004,-.1770]|
|CASIA|20260917|84 /1252|.2576|.3959|-.1383 [-.2531,-.0450]|
|CASIA|20260923|85 /1252|.1787|.3906|-.2119 [-.3201,-.1407]|
|CASIA|20261001|83 /1252|.1663|.4184|-.2521 [-.3816,-.1685]|
|MSU|20260917|36 /1319|.2288|.4286|-.1998 [-.3801,-.0370]|
|MSU|20260923|45 /1319|.3237|.5878|-.2641 [-.3860,-.1071]|
|MSU|20261001|40 /1319|.3218|.5268|-.2050 [-.3417,-.0640]|
|SiW|20260917|40 /1163|.1673|.3439|-.1766 [-.4070,-.0400]|
|SiW|20260923|54 /1163|.1791|.3798|-.2007 [-.4463,-.0961]|
|SiW|20261001|38 /1163|.1611|.3114|-.1502 [-.3664,-.0458]|

All twelve heterogeneous comparisons have >=20 errors, valid uncertainty
and negative intervals. This is unfavorable source evidence for domain-OOF,
not an infrastructure defect and not yet a target RQ1 verdict.

Same-family results are also retained rather than discarded:

| Outer target excluded | Seed | Errors | Domain /sample AP | Delta [95% interval] | Status |
|---|---:|---:|---:|---:|---|
|OULU|20260917|15|.3951 /.5656|-.1706 [-.3706,.0406]|underpowered|
|OULU|20260923|23|.2832 /.5349|-.2518 [-.4149,-.1078]|negative|
|OULU|20261001|15|.2065 /.4833|-.2768 [-.4836,-.0454]|underpowered|
|CASIA|20260917|29|.0496 /.1754|-.1258 [-.3133,-.0489]|negative|
|CASIA|20260923|47|.0869 /.2361|-.1492 [-.2645,-.0807]|negative|
|CASIA|20261001|23|.0463 /.1293|-.0830 [-.3356,.0083]|inconclusive|
|MSU|20260917|26|.1068 /.1157|-.0090 [-.1608,.0448]|inconclusive|
|MSU|20260923|21|.1196 /.1312|-.0116 [-.1552,.0413]|inconclusive|
|MSU|20261001|19|.0556 /.0964|-.0407 [-.2274,.0100]|underpowered|
|SiW|20260917|14|.1052 /.1083|-.0031 [-.1554,.1660]|underpowered|
|SiW|20260923|17|.0854 /.1166|-.0312 [-.1730,.2446]|underpowered|
|SiW|20261001|27|.2732 /.3826|-.1094 [-.3177,.1803]|inconclusive|

Five same-family combinations have fewer than20 G_domain errors; their
point estimates/intervals are shown, but not promoted to supported signs,
even when an interval is negative. Shared examples and three seeds mean
these rows are not twelve independent replications. No pooled target effect,
deployment-risk calibration or target performance is claimed.

## Controls, attribution and drift

Across the twelve combinations, paired domain-minus-sample AP statuses are:

| System | Quality | Fit-size control | Negative | Inconclusive | Underpowered | Positive |
|---|---|---|---:|---:|---:|---:|
|Heterogeneous|with q|primary|12|0|0|0|
|Heterogeneous|with q|budget matched|11|1|0|0|
|Heterogeneous|without q|primary|6|6|0|0|
|Heterogeneous|without q|budget matched|9|3|0|0|
|Same family|with q|primary|3|4|5|0|
|Same family|with q|budget matched|4|3|5|0|
|Same family|without q|primary|3|4|5|0|
|Same family|without q|budget matched|2|5|5|0|

Fit-size sensitivity therefore does not reverse the primary heterogeneous
direction; all twelve point deltas remain negative after budget matching.
This group-preserving sensitivity is not a perfectly equal-sized causal
experiment: residual0-6-image shortfalls and source composition remain.

For heterogeneous domain-OOF, adding quality has two positive, four negative
and six inconclusive paired AP intervals; for sample-OOF all twelve quality
contrasts are inconclusive. The q-free disagreement increment
R_DVd_noq minus R_DV_noq is positive in11/12 domain-OOF and12/12 sample-OOF
contrasts, with one domain-OOF inconclusive. Same-family disagreement has
four positive, three inconclusive and five underpowered contrasts for each
strategy. Same-family quality contrasts are mostly inconclusive/underpowered,
with one positive/one negative for domain-OOF and one negative for sample-OOF.
These are fixed descriptive source contrasts, not multiple-testing-adjusted
target discoveries or a license to select another risk vector.

All48 domain-identifiability audits complete. Held-out balanced-accuracy
ranges (chance1/3) are.7045-.8615 for heterogeneous domain-OOF versus
.6664-.8044 sample-OOF, and.6199-.8477 for same-family domain-OOF versus
.6081-.7916 sample-OOF. Source domain remains identifiable in these vectors;
domain-OOF is not demonstrated domain-invariant.

Maximum overall KS distance among the three score/disagreement features is
.5479 domain-OOF versus.2280 sample-OOF for heterogeneous, and.5507 versus
.2132 for same-family. Full feature means/std/KS and per-source breakdowns
are in the execution receipt. Quality drift is zero by construction because
the same originals and fixed quality statistics are compared. Final-model
reference is in-sample, so these are drift diagnostics, not competence
estimates or proof that drift causes the AP difference.

## Gates and publication discipline

Actual complete competence/applicability files must exist before the normal
source-dry-run validator is called. Failing competence or event support is a
scientific outcome, not a reason to relax the gate, omit a seed or tune the
model. Analysis freeze is attempted only after that source gate succeeds and
the source package is committed cleanly. No locked-evaluation authorization
is created. G_domain diagnostics do not select a gate or risk variant.

The source/evidence commit precedes the separate freeze-record commit.
Creation-time execution/closure receipts retain their original
`pending_clean_commit_and_existing_gate` field; they are not rewritten after
freeze. The immutable record and normal post-commit validation establish the
later state. Published-head CI is checked separately against its exact SHA;
local tests or an unfinished Actions job are not labeled CI success.

The [297 CI terminal receipt](../results/phase1/source297-ci-terminal-v1.json)
closes the previously unconfirmed publication check: exact-head
run40290548935/job121464322107 completed successfully at08:39:08Z with all12
listed steps, including Complete job. The FFmpeg installation alone occupied
08:11:36-08:38:23Z. Historical297 receipts are not rewritten and its private
model campaign was not repeated.

## Validation

64 distinct focused cases passed:35 source/cache/optimization/control tests
and29 preregistration tests. They include an actual synthetic complete
combination with all controls, numerical fits, bootstrap, group-safe audits,
reuse without refitting and persisted-freeze identity checks. These synthetic
tests are distinct from the actual source execution evidence. Changed Python
files compile. Pylance MCP was unavailable earlier; no editor type-check
success is claimed.

The final combined64-test run also exposed a test-fixture assumption:
the external-root negative test inherited newly real source evidence from
the workspace. It now explicitly removes named source/freeze evidence only
inside its isolated temporary fixture, preserving its intended missing-
evidence assertions without deleting real outputs or weakening validation.
