# Post hoc architecture diagnostics

This workflow reanalyzes the completed architecture experiment without retraining any model.

Read `PROTOCOL.md` first. The analysis is explicitly **outcome-informed and post hoc**. It addresses three reviewer concerns:

1. repeated-measures architecture inference without relying on sphericity alone;
2. whether architecture heterogeneity survives when channels are chosen randomly rather than by the validation ranking;
3. direct structural-versus-functional comparison between template-retention difference and the patch-budget contrast.

It also exports an exact architecture-definition table for the manuscript appendix.

## Run

From the repository root:

```powershell
.\run\run_architecture_posthoc.ps1
```

Default input:

```text
%LOCALAPPDATA%\prior-templates-cnns\results\architecture_robustness_cuda_001\evaluation
```

Default output:

```text
%LOCALAPPDATA%\prior-templates-cnns\results\architecture_posthoc_diagnostics_001
```

The analysis performs 100,000 within-block permutations per omnibus and 5,000 bootstrap replicates for within-architecture structural/functional correlations.

After completion:

```powershell
.\run\stage_architecture_posthoc_results.ps1
git diff --cached --stat
git status
git commit -m "analysis: add post hoc architecture diagnostics"
git push
```

Do not describe these diagnostics as prospective confirmation.
