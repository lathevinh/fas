# 322 - Initialization stop and narrowly bounded compatibility amendment

Date:2026-10-28.
Status:321 stopped before scientific fitting. This amendment is preparation
for an explicitly approved retry, **not an automatic retry or a result**.

## 1. What actually happened

[Package321](321-executable-comparison-and-review320-response.md) was
published at`e3ec81a33dcd057d015d8524ecc4163974964249`.
Its exact-head [Actions40632254572](https://github.com/lathevinh/fas/actions/runs/40632254572)
passed. All587 local tests also passed, including18 package-specific tests.
The owner then explicitly approved the integrated321 execution form,
including the SiW limitation and resource envelope.

The supervisor started one attempt. Bounded ImageNet acquisition succeeded:

| Item | Observed value |
|---|---|
| Artifact | torchvision DenseNet161 ImageNet initialization, not PAD weights |
| URL |`https://download.pytorch.org/models/densenet161-8d451a50.pth`|
| Bytes |115730790|
| Full received SHA256 |`8d451a50bad6b9a83f477126c443716882a17af26e94d338154b058fb2dfd359`|
| Original terminal status |`stopped_no_retry`|
| Original terminal elapsed wall |119.90388991800137 seconds|
| Sampled combined peak RSS |1422905344 bytes|
| Scientific frozen-head / specialist / calibrator starts |0 /0 /0|

Before any fitting, the strict architecture probe rejected raw checkpoint
keys such as`features.denseblock1.denselayer1.norm.1.weight`.
The installed model expects`features.denseblock1.denselayer1.norm1.weight`.
The acquisition and pre-fit failure are retained privately, along with the
original seal, authority, logs and terminal. No supplementary PAD accuracy,
private-image forward, checkpoint-selected model or scientific fit exists.
No retry has been launched.

The earlier synthetic initialization test used a modern synthetic torchvision
state dictionary. It correctly verified tensor initialization for that
format but **did not cover the historical naming of the actual artifact**.
That compatibility coverage gap caused the startup stop; the failure is
not attributed to PAD difficulty, GPU time or model infeasibility.

## 2. Narrow root-cause repair

The existing [specialist module](../scripts/paper321/specialist.py) now
modernizes only historical DenseLayer`norm/relu/conv .1/.2` names before
strict complete backbone-state loading. This matches the compatibility
behavior in installed torchvision0.22.1's DenseNet loader. It does not
silently ignore keys, relax strict loading, replace weights or alter tensor
values. Colliding old/new names are an explicit error.

Regression checks add legacy-form synthetic state, exact loaded-encoder
tensor equality, missing historical BatchNorm-counter compatibility and
collision rejection to the existing isolated CPU network test. Preparation
also loads the **actual acquired bytes**, verifies finite tensors and
performs strict CPU architecture initialization without any image forward.
The [322 seal receipt](../results/phase1/paper322-execution-plan-v1.json)
records that actual-artifact compatibility check.

No scientific recipe changes: same12 contexts,36 heads,12 specialist
starts x50 epochs,48 calibrators,74400 specialist optimizer steps, four
systems, preprocessing, partitions, seeds, thresholds, bootstrap and SiW
video-group limitation. This is not a new baseline or rescue search.

## 3. Separate seal, no silent reopening of321

The original321 public/private plan and terminal are not overwritten.
The controller remains in the existing nested
[implementation directory](../scripts/paper321/), but its new default
output is the separate private`paper_comparison322_v1` package. Its
public receipt is separately named322. The original321 implementation can
be inspected at its published commit; its old code hashes are not claimed
to match this repaired HEAD.

Read-only preparation:

```sh
python scripts/paper321/runner.py --prepare
```

In addition to full original input/cache/subject checks, preparation binds
the original stopped terminal, original approval, acquisition receipt and
the exact full digest above. It requires zero original scientific fit starts.
Public proof redacts the local initialization path; biometric memberships
and individual scores remain private.

## 4. Proposed retry authority preserves the original envelope

A second execution requires an explicit owner amendment. The old321
approval cannot authorize322. The exact new answer is:

`approve_paper322_initialization_fix_same_original_deadline`

If approved:

- Reuse the already acquired, full-hash-bound artifact. **No new download.**
- Retain the original approval's boot ID, start time and monotonic deadline.
  Do not reset the12-hour total or11-hour work clock because startup failed
  or implementation took additional time. If that original budget has
  expired, reject approval rather than silently extending it.
- Retain40 minutes/context,12GiB combined sampled RSS,12GiB own CUDA,
  two threads and all original work limits.
- Count retained321 outputs together with322 outputs against the original
  8GiB new/temporary-artifact ceiling. The stopped old processes are not
  relaunched.
- Permit one amended attempt, one no-fit checkpoint reconstruction pass
  and the already specified2000 paired bootstrap draws/context.
- Stop again without automatic retry on any error or ceiling.

The18 focused tests include preservation of the original approval clock.
Four torch-dependent tests remain process-isolated so their memory peaks
cannot contaminate unrelated historical RSS-cap tests. Actual-artifact
strict loading is additionally observed in the private preparation, not
inferred from CI where torch-dependent tests may be skipped.

## 5. Paper and execution status

The [manuscript](paper319/manuscript.md) retains all pending supplementary
cells and explicitly notes the pre-fit startup stop. Historical309/314/316
results are unchanged. Neither the successful acquisition nor this repair
is a new scientific performance result.

There is currently no scientific training process. Publication of this
report and receipt is not a retry approval.
