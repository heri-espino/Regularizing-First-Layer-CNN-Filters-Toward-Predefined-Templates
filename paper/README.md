# Paper

`main.tex` is the authoritative manuscript source for **Regularizing First-Layer CNN Filters Toward Predefined Templates: Activation-Patching Comparisons Depend on Channel Count and Architecture**.

The manuscript uses descriptive scientific names rather than the internal Stage A--F identifiers retained elsewhere in the repository for provenance. The main text is organized around the final evidence: structural template retention, the prospective channel-count result, metric robustness, and architecture robustness.

Appendix material is split into four files so the main source remains readable:

- `final_robustness_results.tex` — metric-sensitivity and architecture-robustness results
- `confirmation_robustness_results.tex` — complete prospective channel-count and schedule/task sensitivity analyses
- `supplementary_results.tex` — developmental analyses that motivated the prospective estimand
- `kernel_matching_results.tex` — complete endpoint kernel-matching table

The bibliography is `../literature/references.bib`. The minimal TMLR style files required for compilation are vendored in `tmlr/` and retain their upstream license.

## Cross-references and equations

The manuscript uses `cleveref` for cross-references. Every displayed equation uses a numbered `equation` environment with an explicit `eq:...` label. New displayed equations should follow the same convention rather than using `\[...\]`.

## Figures

The main paper now begins with a reproducible overview showing representative renderer outputs, the complete template bank, and the first-layer activation-patching intervention. It is generated directly from the frozen renderer/template formulas by:

```bash
python paper/build_overview_figure.py
```

`paper/build.py` regenerates this overview automatically on every manuscript build.

The remaining archived publication figures are regenerated from saved experimental artifacts with:

```bash
python -m pip install -e ".[experiments]"
python paper/build_figures.py
```

The revised main text uses the learned-kernel gallery as the principal structural visualization; the historical learning-curve and robustness figures remain available in the artifact and appendices.

`plot_style.py` centralizes typography, colors, line styles, grid treatment, and PDF export settings. Figure-generation scripts are presentation-only: they do not retrain models or redefine any analysis.

## Build

From the repository root:

```bash
python paper/build.py
```

The compiled manuscript is written to:

```text
paper/espino_2026_template-priors.pdf
```

For a clean rebuild:

```bash
python paper/build.py --clean
```

LaTeX intermediates are written to `paper/build/` and are ignored by Git. The final PDF is generated rather than versioned so a release artifact can be rebuilt from source.
