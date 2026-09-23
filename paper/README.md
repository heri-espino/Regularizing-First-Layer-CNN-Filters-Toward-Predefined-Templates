# Paper

`main.tex` is the authoritative manuscript source for **Activation-Patching Effects in Controlled CNNs Depend on the Number of Patched Channels, Network Architecture, and First-Layer Filter Structure**.

The current manuscript was rewritten from scratch after the final pixel-permuted control experiment on independent renderer blocks and a full review of the repository's extracted literature corpus. Paper-facing prose uses descriptive scientific names rather than the internal Stage A--G identifiers retained elsewhere for provenance.

The main argument is organized around five scientific claims:

1. constant regularization preserves the predefined first-layer spatial structure;
2. the release-versus-retention patching comparison depends on the number of patched channels;
3. the prespecified channel-budget contrast survives alternative output metrics, although the pointwise curves differ;
4. downstream architecture strongly conditions the contrast and that conclusion survives sphericity-robust, permutation, Friedman, and random-channel diagnostics;
5. the original 2D template arrangement has a selected-channel functional effect beyond a Gram/rank/spectrum-matched pixel-permuted control, but that effect is architecture- and metric-dependent.

Appendix material is split into five files:

- `specificity_robustness_results.tex` — pixel-permuted control specificity experiment and post hoc architecture diagnostics;
- `final_robustness_results.tex` — complete metric-sensitivity and prospective architecture-robustness summaries;
- `confirmation_robustness_results.tex` — complete prospective channel-budget and schedule/task sensitivity analyses;
- `supplementary_results.tex` — developmental analyses that motivated the prospective estimand;
- `kernel_matching_results.tex` — complete endpoint kernel-matching table.

The bibliography is `../literature/references.bib`. The minimal TMLR style files required for compilation are vendored in `tmlr/` and retain their upstream license.

## Cross-references and equations

The manuscript uses `cleveref` for cross-references. Every displayed equation uses a numbered `equation` environment with an explicit `eq:...` label. New displayed equations should follow the same convention rather than using `\[...\]`.

## Figures

The main text uses four principal figures:

1. `fig00_overview.pdf` — renderer examples, template bank, and patching intervention;
2. `fig05_kernel_gallery.pdf` — representative learned first-layer kernels;
3. `fig06_main_results.pdf` — prospective channel-budget curves and 16-architecture robustness;
4. `fig07_anchor_specificity.pdf` — matched-anchor spatial specificity, architecture interaction, and equivalence comparison for selected versus random channel sets.

The manuscript-generated figures are built directly from frozen definitions or versioned aggregate analysis tables:

```bash
python paper/build_overview_figure.py
python paper/build_main_results_figure.py
python paper/build_anchor_specificity_figure.py
```

`paper/build.py` regenerates all three manuscript-generated figures automatically on every build.

The remaining archived publication figures are regenerated from saved experimental artifacts with:

```bash
python -m pip install -e ".[experiments]"
python paper/build_figures.py
```

`plot_style.py` centralizes typography, colors, line styles, grid treatment, and PDF export settings. Figure-generation scripts are presentation-only: they do not retrain models or redefine scientific analyses.

## Build

From the repository root:

```bash
python paper/build.py
```

The compiled manuscript is written to:

```text
paper/tmlr_submission.pdf
```

For a clean rebuild:

```bash
python paper/build.py --clean
```

LaTeX intermediates are written to `paper/build/` and are ignored by Git. The final PDF is generated rather than versioned so a release artifact can be rebuilt from source.


## Submission readiness

Before a double-blind submission, read `paper/SUBMISSION_CHECKLIST.md`. The working repository itself is **not** an anonymous supplementary artifact because repository metadata and some provenance manifests contain author-identifying information and local machine paths. Do not upload the repository wholesale as TMLR supplementary material.
