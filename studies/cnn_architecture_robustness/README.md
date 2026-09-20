# Stage F: architecture robustness

> **Live status (2026-09-19):** the official clean CUDA run has completed all **25,600 / 25,600** training jobs and is currently evaluating the frozen first-layer patching grid. Do not inspect/interpret partial Stage-F outcomes or modify the frozen scientific source files while the run may need to resume.

This directory implements the frozen fresh-sample architecture study described in `PROTOCOL.md`.

## Design

Stage F trains 25,600 models:

- 100 fresh renderer blocks (6000--6099);
- 4 paired initialization replicates per block;
- 2 tasks;
- 2 treatments (`retention_1`, `release_default`);
- 16 downstream architecture variants.

All models preserve exactly the same 16-channel 9x9 first convolution, predefined template bank, ReLU intervention tensor, and patch budgets k=1,...,16.

The primary inferential unit is the renderer block after averaging the four initialization replicates.

## Why this study exists

The frozen metric-sensitivity analysis showed a strong TinyCNN patch-budget treatment contrast under centered-logit fidelity and unnormalized probability error reduction, but a much weaker/different pattern in TwoLayerCNN. Stage F therefore targets architecture dependence directly rather than simply adding more seeds to the original networks.

## Windows / university machine

The official full CUDA output is deliberately outside the repository:

```text
%LOCALAPPDATA%\prior-templates-cnns\results\architecture_robustness_cuda_001
```

An earlier CPU-partial run exists under `architecture_robustness_001`; it is not part of the official Stage-F analysis.

The original CPU-multiprocessing default was benchmarked and found to be much slower than sequential CUDA on the university workstation: 110.13 versus 1167.55 models/hour. The official run therefore uses CUDA training and evaluation.

Resume the official run after interruption with:

```powershell
.\run\run_architecture_robustness.ps1 \`
  -OutputRoot "$env:LOCALAPPDATA\prior-templates-cnns\results\architecture_robustness_cuda_001" \`
  -TrainDevice cuda \`
  -TrainWorkers 1 \`
  -EvalDevice cuda \`
  -EvalBatchSize 256
```

All completed training checkpoints and evaluation JSONs are skipped automatically.

Do not change blocks, architecture grid, treatments, metrics, or primary analysis after inspecting Stage-F outcomes.

## Outputs

```text
architecture_robustness_cuda_001/
├── execution_manifest.json
├── training/
│   ├── design.json
│   ├── environment.json
│   ├── GRID_COMPLETE.json
│   ├── data/...
│   └── runs/...              # 25,600 final checkpoints
├── evaluation/
│   ├── design.json
│   ├── GRID_COMPLETE.json
│   └── runs/...              # per-model patching outputs
└── analysis/
    ├── REPORT.md
    ├── summary.json
    ├── primary_architecture_omnibus.csv
    ├── primary_bridge_contrast.csv
    ├── architecture_B_summary.csv
    ├── architecture_factor_contrasts.csv
    ├── treatment_delta_curves.csv
    ├── initialization_dispersion_summary.csv
    ├── input_effect_scale_contrasts.csv
    ├── control_diagnostics.csv
    └── model_endpoints.csv
```

Raw checkpoints and per-model evaluator JSONs remain in the external results directory and should not be committed.

On restricted university worktrees, archive the paper-facing outputs directly into Git with:

```powershell
.\run\stage_architecture_robustness_results.ps1
git diff --cached --stat
git status
git commit -m "analysis: add Stage-F architecture robustness results"
git push
```

This staging helper does not require creating a new folder in the worktree.

## Source-freeze warning

The execution manifest records the committed blobs for `PROTOCOL.md`, `architecture_core.py`, `train_grid.py`, `evaluate_grid.py`, `analyze.py`, and the legacy core. While the official evaluation is incomplete, do not edit those files. Documentation-only changes do not alter the live scientific run.
