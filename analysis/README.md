# Analysis outputs

This directory contains the paper-facing numerical summaries, figures, and audit reports produced from the experiment outputs. The corresponding protocols and executable study code live under `../studies/`.

## Main analyses

| Directory | Contents |
|---|---|
| `budget_confirmation_001/` | Stage-D prospective confirmation, per-block effects, primary contrast, integrity checks |
| `exhaustive_robustness_001/` | Stage-E 1,200-model sensitivity study, full patch-size curves, profile comparisons, energy controls |
| `metric_sensitivity_001/` | Frozen post hoc checkpoint-only comparison of probability, centered-logit, and unnormalized patching metrics |
| `architecture_robustness_001/` | Stage-F paper-facing architecture robustness outputs after the frozen 25,600-model run completes |
| `checkpoint_audit/` | Independent checkpoint reimplementation audit |
| `retention_release_001/` | Stage-B learning and alignment trajectories |
| `patch_robustness_gpu_001/` | Stage-C patch-size/ranking sensitivity and selected-vs-control decomposition |
| `kernel_similarity/` | One-to-one kernel-template matching analysis and figures |

The reports most closely aligned with the final manuscript are:

- `budget_confirmation_001/REPORT.md`
- `exhaustive_robustness_001/REPORT.md`
- `metric_sensitivity_001/REPORT.md`
- `architecture_robustness_001/REPORT.md` after Stage F completes
- `checkpoint_audit/AUDIT_REPORT.md`
- `kernel_similarity/results/REPORT.md`

Large row-level CSV files are retained because they support the aggregate tables and diagnostics reported in the manuscript. They are data products, not additional independent experiments.

## Relationship to `results/`

`results/` contains imported experiment outputs from earlier stages. `analysis/` contains derived, paper-facing analyses. The distinction is retained so that downstream analyses can be traced back to the stored experimental outputs without mixing raw/imported data with manuscript summaries.
