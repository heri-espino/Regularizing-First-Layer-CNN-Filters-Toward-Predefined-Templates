# Supplement and reproducibility map

This file defines the submission-facing support package for the SN Computer Science manuscript **When Do Activation-Patching Effects Add Up? Evidence from Controlled CNNs**.

## Deliverables

Build from the repository root:

    python paper/build.py --clean
    python paper/build_supplement.py --clean
    python paper/build_submission_package.py --verify

This produces:

- paper/dist/manuscript.pdf — main article (copy of paper/sn_submission.pdf);
- paper/dist/supplementary_information.pdf — standalone supporting article (copy of paper/sn_supplement.pdf);
- paper/dist/manuscript_sources.zip — LaTeX sources, bibliography, template, figures, and required derived figure tables;
- paper/dist/activation_patching_reproducibility.zip — self-contained reproducibility runner, data, code, protocols, and SHA-256 manifest.

The reproducibility ZIP excludes raw training checkpoints, per-model evaluator JSON files, Git history, local absolute-path outputs, caches, and development-only notes. The separate source ZIP contains the Springer class/BibTeX style, figure inputs, and bibliography needed by the manuscript build scripts. The publisher's PDF and supplemental upload fields should receive the two PDFs separately rather than embedding them in a code archive.

**Independent acceptance check:** `--verify` extracts both ZIPs to empty temporary directories, verifies inventory and SHA-256 checksums, regenerates eleven figure PDFs from exported CSV/NPZ inputs, and recomputes the budget means and paired BN2-GAP observed-minus-additive Student-t interval. The archive includes instructions for installing dependencies. The other derived inferential summaries remain archived rather than being recomputed by this compact entry point.

## Main-figure provenance

| Main figure | Generator | Principal data/source |
|---|---|---|
| Fig. 1 — experimental system | paper/build_overview_figure.py | studies/cnn_release_experiment/core.py |
| Fig. 3 — direct additivity curves | paper/build_additivity_curves_figure.py | analysis/patching_additivity_001/architecture_analysis/curve_summary.csv |
| Fig. 4 — intervention size + architectures | paper/build_main_results_figure.py | analysis/metric_sensitivity_001/stage_d_treatment_contrasts.csv; analysis/architecture_robustness_001/architecture_B_summary.csv |
| Fig. 5 — spatial specificity | paper/build_anchor_specificity_figure.py | analysis/anchor_specificity_001/secondary_anchor_contrasts.csv; primary_spatial_specificity.csv; random_channel_spatial_specificity.csv |
| Fig. 6 — observed vs additive summary | paper/build_additivity_figure.py | analysis/patching_additivity_001/architecture_analysis/B_summary.csv; analysis/patching_additivity_001/anchor_analysis/structured_vs_pixel_permuted_B_averaged_architectures.csv |
| Fig. 2 — compact filter gallery | paper/build_figures.py | analysis/kernel_similarity/results/kernel_gallery.npz |

## Restored supplementary-figure provenance

| Supplementary figure | Generator | Immutable input |
|---|---|---|
| S1 — learning dynamics | paper/build_figures.py | results/retention_release_001/analysis/learning_curves.csv |
| S2 — patching curves | paper/build_figures.py | analysis/exhaustive_robustness_001/full_budget_curves.csv |
| S3 — filter matching trajectories | paper/build_figures.py | analysis/kernel_similarity/results/per_checkpoint.csv |
| S4 — similarity matrices | paper/build_figures.py | per_checkpoint.csv and analysis/kernel_similarity/results/similarity_matrices.npz |
| S5 — complete kernel gallery | paper/build_figures.py | analysis/kernel_similarity/results/kernel_gallery.npz |

The compact gallery and S5 use the same normalized kernel arrays, Hungarian one-to-one matching, and symmetric color scale. They show `two_concepts`, TinyCNN, block 2000, with original templates and retained/released training at epoch 200 (S5 also includes all five original conditions at epochs 0 and 200). The NPZ is exported once using `python paper/prepare_kernel_gallery.py` from the retained checkpoints and then suffices for PyTorch-free gallery reproduction. The exporter records the original checkpoint identifiers and content hashes inside the NPZ; the reproducibility ZIP manifest independently records file hashes and descriptive export paths. S1 and S3 plot run means ± standard deviations; S2 uses the archived interval bounds. S4 and S5 are a single illustrative run.

## Main numerical claims

| Claim | Reproduction source |
|---|---|
| 20-block intervention-size contrast | analysis/budget_confirmation_001/budget_contrasts_per_block.csv and budget_contrasts.csv |
| Alternative-metric B values | analysis/metric_sensitivity_001/stage_d_budget_contrasts_B_per_block.csv and stage_d_budget_contrasts_B.csv |
| Architecture omnibus and architecture-specific B | analysis/architecture_robustness_001/treatment_delta_curves.csv, primary_architecture_omnibus.csv, architecture_B_summary.csv |
| Greenhouse-Geisser, permutation, Friedman, and random-channel architecture checks | analysis/architecture_posthoc_diagnostics_001/omnibus_robustness.csv, random_B_per_block.csv, selected_random_summary.csv |
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
- studies/cnn_architecture_posthoc/PROTOCOL.md (outcome-informed robustness analysis)
- studies/cnn_anchor_specificity/PROTOCOL.md
- studies/cnn_patching_additivity/PROTOCOL.md
- studies/cnn_checkpoint_audit/AUDIT_PROTOCOL.md

## Scope of reproducibility

The included block-level/aggregate tables and compact NPZ reproduce the published figures without retraining. The independent entry point checks selected numeric claims, not every original inference or bootstrap. Exact retraining also requires the retained raw output/checkpoint store and compute environment recorded in the study manifests; those large files are intentionally not part of the journal upload.

The renderer, architecture definitions, training/evaluation routines, and analysis code needed to inspect the experimental specification are included in the package. This distinction should remain explicit: the submission artifact supports numerical verification of the manuscript from archived result tables, while full checkpoint-level reruns use the separately retained raw experiment store.
