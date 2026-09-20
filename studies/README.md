# Study map

For the current live state and cross-stage interpretation, read [`../RESEARCH_STATUS.md`](../RESEARCH_STATUS.md) first.

The manuscript combines several experiments with different inferential roles. The directories are preserved separately so that frozen protocols, source hashes, and execution history remain traceable.

| Stage | Directory | Role in the paper |
|---|---|---|
| Pilot | `cnn_first_pass/` | Historical first pass; not used as confirmatory evidence |
| A | `cnn_causal_milestone/` | 400-model alignment/intervention study and frozen-feature diagnostic |
| B | `cnn_release_experiment/` | 200-model, 200-epoch retention/release study |
| C | `cnn_patch_robustness/` | Post hoc patch-size/ranking sensitivity on saved Stage-B checkpoints |
| C control | `cnn_patch_energy_control/` | Post hoc validation-energy-matched control |
| D | `cnn_budget_confirmation/` | Frozen prospective primary test on 20 new blocks |
| E | `cnn_exhaustive_robustness/` | Predeclared secondary sensitivity study on 50 new blocks per setting |
| Metric audit | `cnn_metric_sensitivity/` | Frozen checkpoint-only metric-sensitivity analysis on saved Stage-D/E checkpoints; no retraining |
| F | `cnn_architecture_robustness/` | Frozen fresh-sample 25,600-model architecture robustness study |
| Audit | `cnn_checkpoint_audit/` | Independent reimplementation audit on fixed saved checkpoints |

## Recommended reading order

1. Read `../paper/main.tex` or build the manuscript with `python paper/build.py` from the repository root.
2. Read `cnn_budget_confirmation/PROTOCOL.md` and `../analysis/budget_confirmation_001/REPORT.md` for the prospective primary result.
3. Read `cnn_exhaustive_robustness/PROTOCOL.md` and `../analysis/exhaustive_robustness_001/REPORT.md` for the larger secondary sensitivity study.
4. Read `cnn_metric_sensitivity/PROTOCOL.md` and `../analysis/metric_sensitivity_001/REPORT.md` for the completed metric audit.
5. Read `cnn_architecture_robustness/PROTOCOL.md` for Stage F. Training, evaluation, and frozen analysis are complete; see the archived Stage-F report before interpreting or extending the study.
6. Read `cnn_checkpoint_audit/AUDIT_PROTOCOL.md` and `../analysis/checkpoint_audit/AUDIT_REPORT.md` for the independent implementation check.
7. Return to Stages A--C when tracing how the Stage-D estimand was developed.

Stages A--C motivated the final analysis but are not treated as independent confirmations of Stage D. Stage D contains the single prospective primary test. Stage E was separately frozen and is reported as a secondary sensitivity study; it does not redefine the Stage-D primary hypothesis. The metric audit was designed later, after the probability-space results were known, and is explicitly post hoc with respect to those results even though its alternative metrics were frozen before evaluation.

Historical source files are kept in place even when later code superseded them. This is deliberate: the repository is an archival research record, not a single production package.

Stage F was motivated by the completed metric audit: the TinyCNN patch-budget contrast remained under centered-logit and unnormalized probability-error metrics, while TwoLayerCNN showed substantially weaker or different behavior. Stage F therefore uses fresh data blocks and multiple paired initializations to decompose architecture effects prospectively.

## Completed architecture robustness

The clean CUDA architecture-robustness run is complete: all 25,600 training jobs, frozen evaluations, and frozen analyses finished successfully. Paper-facing outputs are archived under `../analysis/architecture_robustness_001/`. The earlier CPU-partial root is not part of the official analysis.

## Pre-submission strengthening

- `cnn_anchor_specificity/` — prospectively frozen fresh-sample anchor-specificity experiment; tests whether spatial template structure matters beyond exactly matched bank geometry.
- `cnn_architecture_posthoc/` — frozen outcome-informed diagnostic analysis of the completed architecture study; robust omnibus, random-channel, and structure/function diagnostics.

These are the active final strengthening workflows before submission. The anchor-specificity experiment now includes a frozen equivalence companion so that a nonsignificant structured-vs-pixel-permuted difference cannot be misread as equivalence. The manuscript should not be treated as final until these results are incorporated.
