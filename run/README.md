# Run helpers

This directory contains convenience launchers for reproducing the experiments and analyses used in the manuscript. The frozen study code itself remains in `../studies/`; these wrappers only provide shorter entry points.

| File | Purpose |
|---|---|
| `run.sh`, `run.ps1` | Stage-B retention/release experiment |
| `run_gpu.sh` | Stage-C patching evaluation on GPU/CPU |
| `review_robustness.sh` | Rebuild the Stage-C decomposition from saved outputs |
| `run_kernel_analysis.sh`, `run_kernel_analysis.ps1` | Kernel-template matching analysis |
| `run_paper_experiments.*` | Stage-D prospective confirmation followed by Stage-E sensitivity study |

Examples from the repository root:

```bash
bash run/run.sh smoke
bash run/run_gpu.sh check
bash run/run_kernel_analysis.sh
zsh run/run_paper_experiments.zsh
```

On Windows:

```powershell
.\run\run.ps1 smoke
.\run\run_kernel_analysis.ps1
.\run\run_paper_experiments.cmd
```

Read the corresponding study `README.md` and frozen `PROTOCOL.md` before launching the expensive Stage-D or Stage-E runs.
