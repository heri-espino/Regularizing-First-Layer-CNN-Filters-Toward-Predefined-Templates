# Anchor-specificity experiment

Read `PROTOCOL.md` first. The protocol was committed before any outcome from this study exists.

This fresh-sample experiment asks whether the channel-count treatment contrast specifically requires the designed spatial template structure or also appears under matched/random anchors.

The four anchor families are:

- structured edge/corner/ring templates;
- a common random pixel permutation of the template bank, preserving the full Gram matrix/rank/singular spectrum exactly;
- a generic random rank-10 bank;
- a generic full-rank random bank.

The architecture grid is the balanced diagnostic 2 x 2:

- Tiny vs one downstream convolution;
- GMP vs GAP.

Full study size: **25,600 models**.

## Smoke test

From the repository root:

```powershell
.\run\run_anchor_specificity.ps1 -Smoke
```

## Full CUDA run

```powershell
.\run\run_anchor_specificity.ps1
```

Default external output:

```text
%LOCALAPPDATA%\prior-templates-cnns\results\anchor_specificity_cuda_001
```

Training and evaluation are incremental and resumable. Completed models/evaluations are skipped. The execution manifest freezes the committed protocol and source blobs for the output root.

After completion:

```powershell
.\run\stage_anchor_specificity_results.ps1
git diff --cached --stat
git status
git commit -m "analysis: add anchor specificity results"
git push
```

Do not inspect partial scientific outcomes. Either a null or non-null structured-vs-pixel-permuted result is useful and has a frozen interpretation in the protocol.
