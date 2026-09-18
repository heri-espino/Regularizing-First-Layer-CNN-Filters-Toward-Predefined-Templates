# Patching metric-sensitivity study

This directory contains the final checkpoint-only robustness experiment for the template-prior CNN paper.

It addresses a specific remaining question: is the Stage-D/Stage-E channel-count result tied to the original normalized probability-space patching metric?

## Evidential status

Read PROTOCOL.md first.

This analysis was designed after the original Stage-D/E results were known, but before any centered-logit or unnormalized-error results were generated. It is therefore a **frozen post hoc robustness analysis**, not a new confirmation sample.

No model is retrained.

## What is recomputed

The evaluator loads the completed Stage-D and Stage-E epoch-200 checkpoints and **reuses the exact stored channel-ranking arrays** from their original evaluation artifacts.

The two primary robustness metrics are:

1. centered-logit fidelity

   \[
   F_{\mathrm{clogit}}
   =
   1-
   \frac{\sum\|\widetilde\ell_S-\widetilde\ell_1\|^2}
        {\sum\|\widetilde\ell_1-\widetilde\ell_0\|^2};
   \]

2. absolute probability reconstruction-error reduction

   \[
   R_{\mathrm{prob}}
   =
   \frac1N\sum\|p_0-p_1\|^2
   -
   \frac1N\sum\|p_S-p_1\|^2.
   \]

The evaluator also stores raw-logit fidelity, centered/raw-logit absolute error reductions, counterfactual accuracy, agreement, and the base-to-counterfactual input-effect scales.

The historical probability fidelity is recomputed as an integrity check and must match the stored value within tolerance.

## Required existing artifacts

The launcher expects the already completed experiment roots:

- Stage D: budget_confirmation_001, containing training/ and patch_eval/.
- Stage E: exhaustive_robustness_001, containing training/ and evaluation/.

No files in those roots are modified.

## Windows / PowerShell

From the repository root:

~~~powershell
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File .\studies\cnn_metric_sensitivity\run_metric_sensitivity.ps1
~~~

Override paths when needed:

~~~powershell
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File .\studies\cnn_metric_sensitivity\run_metric_sensitivity.ps1 -StageDRoot "D:\results\budget_confirmation_001" -StageERoot "D:\results\exhaustive_robustness_001" -OutputRoot "D:\results\metric_sensitivity_001" -Device cuda -BatchSize 256
~~~

## Zsh

~~~zsh
zsh studies/cnn_metric_sensitivity/run_metric_sensitivity.zsh
~~~

Default POSIX paths are:

- results/budget_confirmation_001
- results/exhaustive_robustness_001
- results/metric_sensitivity_001

They can be overridden with STAGE_D_ROOT, STAGE_E_ROOT, OUTPUT_ROOT, DEVICE, and BATCH_SIZE.

## Smoke test

A smoke test evaluates one saved model and does not produce inferential output. Use a separate output directory:

~~~powershell
python studies/cnn_metric_sensitivity/evaluate_metrics.py --stage d --input-root "D:\results\budget_confirmation_001" --output "D:\results\metric_sensitivity_smoke" --device cuda --batch-size 256 --smoke
~~~

Do not use smoke results in the manuscript.

## Outputs

The full run creates:

~~~text
metric_sensitivity_001/
├── execution_manifest.json
├── stage_d/
│   ├── design.json
│   ├── EVAL_COMPLETE.json
│   └── runs/...
├── stage_e/
│   ├── design.json
│   ├── EVAL_COMPLETE.json
│   └── runs/...
└── analysis/
    ├── REPORT.md
    ├── summary.json
    ├── stage_d_primary_metric_robustness.csv
    ├── stage_d_treatment_contrasts.csv
    ├── stage_d_input_effect_scale_contrasts.csv
    ├── stage_e_budget_contrasts_B.csv
    ├── stage_e_metric_curves.csv
    └── block-level CSV files
~~~

The manuscript should not be rewritten until the full frozen analysis completes. If the alternative metrics disagree with the historical probability metric, that disagreement is itself the result and must be retained.
