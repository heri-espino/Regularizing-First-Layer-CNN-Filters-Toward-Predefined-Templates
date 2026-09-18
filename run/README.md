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
| `stage_architecture_robustness_results.ps1` | Archive only Stage-F paper-facing outputs from `%LOCALAPPDATA%` directly into Git |

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

Stage F uses the user-writable default:

```text
%LOCALAPPDATA%\prior-templates-cnns\results\architecture_robustness_001
```

Run a smoke test, then the full frozen experiment:

```powershell
.\run\run_architecture_robustness.ps1 -Smoke
.\run\run_architecture_robustness.ps1
```

After the full analysis completes on a restricted worktree:

```powershell
.\run\stage_architecture_robustness_results.ps1
git diff --cached --stat
git status
git commit -m "analysis: add Stage-F architecture robustness results"
git push
```
