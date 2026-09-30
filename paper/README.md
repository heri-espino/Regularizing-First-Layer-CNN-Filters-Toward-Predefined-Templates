# Paper

paper/main.tex is the working main manuscript. The current branch restructures the paper for a planned SN Computer Science resubmission. The scientific content is being reorganized before the final publisher-template conversion so that the pending additive-reconstruction analysis can be inserted without another structural rewrite.

## Main-paper logic

The main paper is now organized by scientific questions rather than by the chronology of experiments:

1. Does constant regularization preserve the predefined first-layer filter structure?
2. How does the release-versus-retention patching comparison change with intervention size?
3. How much of that intervention-size behavior can be reconstructed from singleton contributions, cancellation, model-tail non-additivity, and metric nonlinearity? This result is pending; only the frozen method is currently defined.
4. How strongly does downstream architecture change the same first-layer comparison?
5. Does the original two-dimensional filter arrangement matter relative to a Gram/rank/spectrum-matched pixel-permuted control?

The intended reading order for every result is:

finding → figure → principal magnitude → interpretation.

Complete test statistics, corrections, alternative rankings, schedules, and other exhaustive estimates are kept out of the main narrative unless they change interpretation.

## Main figures

The restructured manuscript uses a small figure-led set:

1. figures/fig00_overview.pdf plus figures/fig01_kernel_summary.pdf — presented together as the experimental system, predefined bank, a compact checkpoint-based subset of learned filters, and the patch point. The full 16-channel gallery remains in the supplement.
2. figures/fig02_intervention_size.pdf — retention and release curves plus their paired difference for the three evaluation metrics.
3. additive-reconstruction figure — pending the frozen post-hoc analysis under studies/cnn_patching_additivity/.
4. figures/fig04_architecture.pdf — the complete 16-architecture map, separated from the intervention-size figure.
5. figures/fig07_anchor_specificity.pdf — the spatial-control result.

paper/build_main_results_figure.py generates figures 2 and 4 from versioned analysis tables. It is presentation-only and does not retrain models or redefine inferential statistics.

## Main tables

The main text intentionally keeps only two compact tables:

- the evidence roadmap: task, architecture scope, comparison, renderer blocks, and evidential status;
- endpoint context for the four architectures used in the spatial-control follow-up, including test accuracy and filter similarity.

This keeps the important performance mismatch visible without reproducing the full architecture tables in the body.

## Supplement

paper/supplement.tex is now separate from paper/main.tex. It groups the existing exhaustive material into three roles:

1. methods and checks;
2. complete estimates and sensitivity analyses;
3. earlier exploratory analyses retained for provenance.

The previous appendix source files remain intact so no numerical record is discarded. The main manuscript no longer inputs them directly.

## Pending additive reconstruction

The frozen protocol is studies/cnn_patching_additivity/PROTOCOL.md. It is explicitly post-hoc and uses saved checkpoints without retraining. The manuscript already defines the additive reconstruction notation and reserves the result location immediately after the intervention-size result.

Do not insert an outcome before the frozen analysis finishes. In particular:

- metric curvature is not a model interaction;
- a nonzero residual is not automatically synergy or redundancy;
- the analysis is explanatory decomposition, not independent confirmation.

## Journal positioning

The bibliography now includes the three supplied SN Computer Science papers on interpretation regularization/robustness, explanation multiplicity, and deceptive XAI. They are cited where they sharpen the distinction between representation, intervention, and explanation fidelity rather than added only to increase same-journal citation counts.

## Build

From the repository root:

    python paper/build.py --clean

The build regenerates the manuscript figures from versioned aggregate tables before compiling the PDF. Heavy paper-generation workflows remain manual-only through workflow_dispatch.

The current output filename remains paper/tmlr_submission.pdf until the final SN Computer Science template migration. This prevents a template change from being mixed with the scientific restructuring.
