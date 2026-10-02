# Supplement and reproducibility map

This file defines the submission-facing support package for the SN Computer Science manuscript **Activation Patching in Structured CNNs: Intervention Size, Architecture, and Additivity**.

## Deliverables

Build from the repository root:

    python paper/build.py --clean
    python paper/build_supplement.py --clean
    python paper/build_submission_package.py

This produces:

- paper/sn_submission.pdf — main article;
- paper/sn_supplement.pdf — standalone Supplementary Information;
- paper/dist/sn_submission_package.zip — allowlisted reproducibility package.

The package intentionally excludes raw training checkpoints, per-model evaluator JSON files, Git history, local absolute-path outputs, caches, and development-only notes.

## Main-figure provenance

| Main figure | Generator | Principal data/source |
|---|---|---|
| Fig. 1 — experimental system | paper/build_overview_figure.py | studies/cnn_release_experiment/core.py |
| Fig. 2 — intervention size + architectures | paper/build_main_results_figure.py | analysis/metric_sensitivity_001/stage_d_treatment_contrasts.csv; analysis/architecture_robustness_001/architecture_B_summary.csv |
| Fig. 3 — spatial specificity | paper/build_anchor_specificity_figure.py | analysis/anchor_specificity_001/secondary_anchor_contrasts.csv; primary_spatial_specificity.csv; random_channel_spatial_specificity.csv |
| Fig. 4 — direct additivity curves | paper/build_additivity_curves_figure.py | analysis/patching_additivity_001/architecture_analysis/curve_summary.csv |
| Fig. 5 — observed vs additive summary | paper/build_additivity_figure.py | analysis/patching_additivity_001/architecture_analysis/B_summary.csv; analysis/patching_additivity_001/anchor_analysis/structured_vs_pixel_permuted_B_averaged_architectures.csv |

## Main numerical claims

| Claim | Reproduction source |
|---|---|
| 20-block intervention-size contrast | analysis/budget_confirmation_001/budget_contrasts_per_block.csv and budget_contrasts.csv |
| Alternative-metric B values | analysis/metric_sensitivity_001/stage_d_budget_contrasts_B_per_block.csv and stage_d_budget_contrasts_B.csv |
| Architecture omnibus and architecture-specific B | analysis/architecture_robustness_001/treatment_delta_curves.csv, primary_architecture_omnibus.csv, architecture_B_summary.csv |
| Spatial structured-minus-permuted effect | analysis/anchor_specificity_001/primary_spatial_specificity_per_block.csv, secondary_anchor_contrasts_per_block.csv |
| BN2-GAP observed-minus-additive B | analysis/patching_additivity_001/architecture_analysis/B_per_block.csv |
| Tiny numerical additivity and residual-energy curves | analysis/patching_additivity_001/architecture_analysis/curve_summary.csv and model_integrity.csv |
| Spatial observed-minus-additive paired comparison | analysis/patching_additivity_001/anchor_analysis/B_per_block.csv |
| Filter/template endpoint similarity and accuracy quoted in Results | analysis/exhaustive_robustness_001/model_endpoint_summary.csv and model_endpoints.csv |
| Independent evaluator audit | analysis/checkpoint_audit/AUDIT_REPORT.md |

The paired two_concepts/bn2_w16_gap centered-logit comparison was independently checked from the archived block table: mean B_obs - B_add = -0.1799415521, Student-t 95% CI [-0.2008225633, -0.1590605409], n = 100.

## Frozen protocols

The package includes the protocols that govern the paper-facing analyses:

- studies/cnn_budget_confirmation/PROTOCOL.md
- studies/cnn_exhaustive_robustness/PROTOCOL.md
- studies/cnn_metric_sensitivity/PROTOCOL.md
- studies/cnn_architecture_robustness/PROTOCOL.md
- studies/cnn_anchor_specificity/PROTOCOL.md
- studies/cnn_patching_additivity/PROTOCOL.md
- studies/cnn_checkpoint_audit/AUDIT_PROTOCOL.md

## Scope of reproducibility

The included block-level and aggregate tables reproduce the reported plots and inferential summaries without retraining. Exact retraining also requires the retained raw output/checkpoint store and compute environment recorded in the study manifests; those large files are intentionally not part of the journal upload.

The renderer, architecture definitions, training/evaluation routines, and analysis code needed to inspect the experimental specification are included in the package. This distinction should remain explicit: the submission artifact supports numerical verification of the manuscript from archived result tables, while full checkpoint-level reruns use the separately retained raw experiment store.
