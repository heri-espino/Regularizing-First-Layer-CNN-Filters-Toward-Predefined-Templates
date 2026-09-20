# Run helpers

This directory contains convenience launchers for reproducing the experiments and analyses used in the manuscript. The frozen study code itself remains in `../studies/`; these wrappers only provide shorter entry points.

| File | Purpose |
|---|---|
| `run.sh`, `run.ps1` | Stage-B retention/release experiment |
| `run_gpu.sh` | Stage-C patching evaluation on GPU/CPU |
| `review_robustness.sh` | Rebuild the Stage-C decomposition from saved outputs |
| `run_kernel_analysis.sh`, `run_kernel_analysis.ps1` | Kernel-template matching analysis |
| `run_paper_experiments.*` | Stage-D prospective test followed by Stage-E sensitivity study |
| `run_metric_sensitivity.ps1`, `run_metric_sensitivity.zsh` | Re-evaluate saved Stage-D/E checkpoints under frozen alternative patching metrics; no training |
| `stage_metric_sensitivity_results.ps1` | Stage completed metric-sensitivity analysis directly from `%LOCALAPPDATA%` into Git when the Windows worktree cannot create new directories |
| `run_architecture_robustness.ps1` | Run the frozen Stage-F 25,600-model architecture robustness study |
| `stage_architecture_robustness_results.ps1` | Archive only Stage-F paper-facing outputs from the official external CUDA root directly into Git |
| `benchmark_architecture_training.ps1` | Implementation-only CPU-vs-CUDA Stage-F training throughput benchmark |

Examples from the repository root:

```bash
bash run/run.sh smoke
bash run/run_gpu.sh check
bash run/run_kernel_analysis.sh
zsh run/run_paper_experiments.zsh
zsh run/run_metric_sensitivity.zsh
```

On Windows:

```powershell
.\run\run.ps1 smoke
.\run\run_kernel_analysis.ps1
.\run\run_paper_experiments.cmd
.\run\run_metric_sensitivity.ps1
.\run\run_architecture_robustness.ps1 -Smoke
.\run\run_architecture_robustness.ps1
```

Read the corresponding study `README.md` and frozen `PROTOCOL.md` before launching Stage D/E. The metric-sensitivity helper is checkpoint-only but should also be run only after reading its frozen protocol, because its outputs are intended to be interpreted without redesign after inspection.


## Restricted university Windows worktrees

Some university-managed Windows machines allow Git commits but deny creation of new directories inside the checkout. Metric-sensitivity outputs are therefore written to the user-writable default:

```text
%LOCALAPPDATA%\prior-templates-cnns\results\metric_sensitivity_001
```

After a completed run, archive the paper-facing outputs without copying them into the worktree:

```powershell
git pull --ff-only origin main
.\run\stage_metric_sensitivity_results.ps1
git diff --cached --stat
git status
git commit -m "analysis: add metric sensitivity results"
git push
```

The staging helper writes the external files into Git's object database and index directly. It does not rerun the experiment and does not require administrator privileges.


## Stage F

The official Stage-F run uses:

```text
%LOCALAPPDATA%\prior-templates-cnns\results\architecture_robustness_cuda_001
```

Stage F is complete and its paper-facing analysis is archived. The command below remains only as the resumable provenance-preserving launcher:

```powershell
.\run\run_architecture_robustness.ps1 `
  -OutputRoot "$env:LOCALAPPDATA\prior-templates-cnns\results\architecture_robustness_cuda_001" `
  -TrainDevice cuda `
  -TrainWorkers 1 `
  -EvalDevice cuda `
  -EvalBatchSize 256
```

The earlier CPU-partial root `architecture_robustness_001` is not part of the official Stage-F analysis.

The implementation benchmark measured 110.13 models/hour with 12 CPU workers and 1167.55 models/hour with sequential CUDA. Benchmark outputs are operational only.

After the full frozen analysis completes:

```powershell
.\run\stage_architecture_robustness_results.ps1
git diff --cached --stat
git status
git commit -m "analysis: add Stage-F architecture robustness results"
git push
```

Do not modify the frozen Stage-F scientific source retroactively; new analyses belong in separate versioned workflows.

## Final pre-submission strengthening

The fresh anchor-specificity experiment is now frozen and CI-smoke-tested. Run the implementation smoke first:

```powershell
.\run\run_anchor_specificity.ps1 -Smoke
```

Then launch the official full CUDA run:

```powershell
.\run\run_anchor_specificity.ps1
```

Default external root:

```text
%LOCALAPPDATA%\prior-templates-cnns\results\anchor_specificity_cuda_001
```

The full design is 25,600 models: 100 fresh blocks × 4 init/anchor replicates × 2 tasks × 4 diagnostic architectures × 4 anchor families × 2 treatments. Training and evaluation are incremental and resumable.

The outcome-informed architecture diagnostics use the already-completed Stage-F evaluator outputs and require no retraining:

```powershell
.\run\run_architecture_posthoc.ps1
```

They add Greenhouse--Geisser/permutation/Friedman omnibus checks, random-channel architecture diagnostics, structural-versus-functional summaries, and an exact architecture-definition table.

After completion, archive only paper-facing outputs:

```powershell
.\run\stage_anchor_specificity_results.ps1
.\run\stage_architecture_posthoc_results.ps1
```

Read the corresponding frozen protocols before interpreting outputs. The anchor-specificity primary structured-vs-pixel-permuted analysis includes a prespecified equivalence test; nonsignificance alone is not evidence of equivalence.
