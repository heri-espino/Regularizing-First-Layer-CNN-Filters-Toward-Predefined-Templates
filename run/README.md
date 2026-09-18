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
```

Read the corresponding study `README.md` and frozen `PROTOCOL.md` before launching Stage D/E. The metric-sensitivity helper is checkpoint-only but should also be run only after reading its frozen protocol, because its outputs are intended to be interpreted without redesign after inspection.
