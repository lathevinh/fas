# 302 - Review of301: locked target results and final claim outcomes

Date: 2026-10-27
Reviewed commit: `21ad66f81de5ac5fe0cb1a24a989ef3df5fe957e`
Governing review: [300](300-review-doc299-complete-source-evidence-and-analysis-freeze.md).

## Decision

**Accept301's completed fixed locked-target execution, registered RQ1/RQ2 point/uncertainty aggregation and disclosed additive saved-output verification. RQ1 is inconclusive; RQ2 has evidence against the registered heterogeneous-superiority claim. No repeat target experiment, source retraining, target threshold reselection or hypothesis-rescuing configuration change is justified.**

The original frozen native --close command did not pass: its integer-versus-string JSON-key comparison has a real serialization defect. Acceptance is explicitly of the reported additive normalization-only closure, not a claim that the sealed native verifier is repaired. Private verifier source and raw predictions remain unavailable here. Preserve that limitation in final reproducibility reporting.

All four data milestones, source experiment299 and source-only findings remain accepted history. This target result supersedes neither the source tables nor their scope: domain-OOF can fail on source diagnostics yet improve on some targets. The registered overall target decision must use all four targets and seeds, not a favorable subset.

## Verification and authority boundary

Reviewed report301, final revision3 config/manifest/policies/freeze, public typed authority, authorization, run/closure/verifier receipts, evaluator/controller and regression definitions. Exact final-head GitHub [run40314282943](https://github.com/lathevinh/fas/actions/runs/40314282943), [validate121542852412](https://github.com/lathevinh/fas/actions/runs/40314282943/job/121542852412) concludes success for all12 listed steps, including Complete job. This is final publication CI, separately from preparation CI.

Locally attempted all11 evaluator tests: ten passed; the supervisor publication case errored at Windows sandbox-denied os.link in the existing immutable-record helper. The metric/claim/paired-bootstrap/source-policy/mask/failure/typed-ledger cases passed. This is not11 passing tests or local GPU/private execution. The producer's482 full tests and74 later focused tests are separate, overlapping evidence.

Independent checks passed for all156 successor freeze pins, creation ancestry and unchanged pinned Git paths, exact manifest/freeze/authority bindings, the preserved original source-freeze hash,12-cell arithmetic, seed-then-target aggregation, all operational-harm aggregates, registered claim predicates and bootstrap-valid counts. Recomputing aggregate/decide from public saved point tables reproduces RQ1 inconclusive and RQ2 evidence_against. No bootstrap sampling or model execution was repeated.

The public typed authority names the approved revision3 manifest, successor freeze, target populations, three seeds and original resource envelope. Earlier revisions1/2 remain unapproved/unexecuted preparation history. The successor freeze explicitly covers evaluator code, config, exact artifact manifest and source-only policies; the prior source freeze is unchanged. This closes300's preparation/authority requirement on the reported evidence. Raw human approval, private models/features/labels/transactions and additive verifier source are unavailable for independent inspection. Technical hash/metric verification is not independent scientific replication or visual adjudication.

## Actual execution coverage

| Target official test population | Originals | Successful ranking inputs | Retained technical failures |
|---|---:|---:|---:|
|OULU-NPU|1800|1800|0|
|CASIA-FASD|360|354|6|
|MSU-MFSD|160|156|4|
|SiW-Mv2|623|619|4|
|Total|2943|2929|14|

All2943 originals remain in per-seed operational accounting;2929 successes per seed yield8787 context prediction rows.421776 risk values equal48 diagnostics per successful context row.35316 original action records reconcile2943 originals x three seeds x two systems x two strategies. Failures have no invented score/error/rank and remain terminal non-accepts in original class denominators.

Only619 SiW official-test successes require new frozen features:1857 forwards across three encoders. Compatible2310 target-success rows per backbone are reused from prior source rotations. The reported locked execution uses the correct target-excluded fitted states and fixed source thresholds; cache reuse is not source-model refitting. No new optimization, text inference, checkpoint download, detector, target gate selection or target tuning is reported.

Reported worker219.838s and additive closure515.811s remain within the original authority; RSS2657857536 bytes, new storage74796159 bytes and final CUDA peaks are below caps. These private sampled execution observations were not independently replayed.

## RQ1: target-dependent transfer, no supported overall win

Delta is heterogeneous error AP from domain-OOF risk minus matched-sample risk on identical final classifier/error sets. Higher is better. Every target satisfies the registered event-support criterion; no low-event seed is dropped.

| Target | Three-seed AP delta | Paired95% clustered interval |
|---|---:|---|
|OULU|+0.103973|[+0.078204,+0.136000]|
|CASIA|-0.232858|[-0.300831,-0.146020]|
|MSU|+0.092808|[+0.056029,+0.148976]|
|SiW|-0.040851|[-0.081534,-0.000829]|
|Equal-target macro|-0.019232|[-0.039570,+0.009115]|

OULU/MSU favor domain-OOF; CASIA/SiW favor sample-OOF. Overall macro is slightly negative with an interval spanning zero, and only two target means are positive rather than the required three. The registered outcome is **inconclusive**. It is neither a positive general-transfer claim nor evidence of uniform domain-OOF inferiority. No target/seed pooling, favorable-target selection or retrospective removal of CASIA is allowed. Confidence intervals are conditional on fitted models and these four targets, not new-domain guarantees or bootstrap retraining.

## RQ2: evidence against heterogeneous selective-risk superiority

Delta is same-family minus heterogeneous class-balanced raw AURC, so positive favors heterogeneous. Macro=-0.032897,95% interval[-0.055779,-0.012521]. OULU is positive(+0.044038); CASIA/MSU/SiW are negative(-0.070221/-0.065241/-0.040162), each with negative intervals. Minimum+0.01 effect, positive lower bound, three positive targets and two positive seed macros all fail; three target selective-harm point limits are also breached. The registered outcome is **evidence_against**, not simply missing power or an inapplicable claim.

This comparison concerns complete systems with different classifier error sets and a common success mask; it cannot isolate a causal benefit/harm of one backbone or of disagreement alone. Source complete-system competence permits this test, but does not predetermine superiority. Weak standalone OpenCLIP remains disclosed rather than removed after target observation.

## Operational utility is a substantive failure mode

The source-only K=1 rule is empirical worst-source FA<=1% with maximum coverage. It applies only to predicted-live decisions; predicted spoof is already a covered PAD rejection, and technical failures are uncovered terminal non-accepts. The fix to coverage counting occurred before authority. Ranking coverage/AURC and operational coverage are appropriately different quantities.

The source constraint does not transfer as a target security guarantee. Three-seed mean heterogeneous target FA is26.67% on OULU,14.17% on MSU and5.71% on SiW, despite zero on CASIA. Heterogeneous bona-fide non-accept is78.15% on CASIA and81.23% on SiW. These fixed policies are not demonstrated deployable PAD security/usability policies.

Relative operational guardrails also fail: MSU heterogeneous-minus-same-family FA harm=+0.069444 and SiW BFNR harm=+0.455939, exceeding the+0.02 per-target limits. Favorable macro harms do not cancel those breaches. High coverage, especially CASIA's97.22%, does not mean high usability: many bona-fide inputs receive covered spoof rejections. Likewise high CASIA AUROC with poor fixed-threshold ACER is not a threshold-tuning invitation or a replacement endpoint.

## Serialization defect and reproducibility

The native closure recomputes domain class-count dictionaries with integer0/1 keys while JSON necessarily saves them as strings. A JSON-roundtrip normalization converts representation without rounding numerical values. The disclosed additive verifier reportedly proves equality of all twelve point tables under that representation and reuses the unchanged closure for8787 rows/421776 risks; no inference, optimizer or bootstrap replay is reported. The verifier/worker hashes and receipts agree publicly.

This is a credible narrow readback explanation, not a failed scientific worker or license for arbitrary post-hoc repairs. Still, the actual private verifier source cannot be checked from its hash alone. Include a minimal inspectable normalization-only verifier and synthetic roundtrip regression in the final reproducibility bundle, with its exact digest and explicit separation from frozen code. Do not modify the executed successor freeze or claim native --close success; do not repeat target predictions merely to obtain a clean native closure receipt.

## Next work: finish reporting this experiment

The registered target experiment is complete with RQ1 inconclusive and RQ2 evidence against. Prepare the final results/reproducibility package from saved evidence now: all12 point tables, target/seed macros and intervals, event support, both success-mask and original-denominator operational metrics, source/target contrast, complete negative/inconclusive outcomes, exact artifact/freeze/authority chain and the disclosed additive-verifier procedure. Keep the registered primary endpoints separate from fixed exploratory diagnostics and multiple comparisons.

No extra confirmation campaign or hyperparameter/prompt/threshold search is required to close this experiment. Correct ordinary reporting/serialization defects through additive provenance, not rewritten history. If a revised method is desired later, create a separately preregistered exploratory experiment; these targets have now been observed and cannot be presented as untouched validation for that revision. Current authority is consumed, not permission for automatic target retries or new model selection.

**The valid outcome is a completed fixed experiment with mixed transfer and evidence against the proposed heterogeneous superiority, plus serious operational limitations. The next deliverable is the final scientific report, not another round of tuning.**
