# Paper

`main.tex` is the authoritative manuscript source for **Template Priors in Small CNNs: Activation-Patching Effects Depend on the Number of Patched Channels**.

The appendix material is split into three files so the main source remains readable:

- `confirmation_robustness_results.tex` — complete Stage-D and Stage-E numerical support
- `supplementary_results.tex` — historical Stages A--C
- `kernel_matching_results.tex` — complete endpoint kernel-matching table

The bibliography is `../literature/references.bib`. The minimal TMLR style files required for compilation are vendored in `tmlr/` and retain their upstream license.

## Figures

The five figures used by the manuscript are publication assets in `figures/`. They are regenerated from saved experimental artifacts with:

```bash
python -m pip install -e ".[experiments]"
python paper/build_figures.py
```

`plot_style.py` centralizes typography, colors, line styles, grid treatment, and PDF export settings. The plotting system uses a restrained white-grid theme, a color-blind-friendly palette, and a serif stack headed by Latin/Computer Modern so figure typography matches the TMLR manuscript closely.

Figures are exported as PDF. Curves, axes, text, and annotations remain vector; dense heatmaps and kernel images are selectively rasterized inside the PDF. The figure builder is presentation-only: it reads saved CSV/NPZ outputs and fixed checkpoints and does not retrain models or redefine any analysis.

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

LaTeX intermediates are written to `paper/build/` and are ignored by Git. The final PDF is also generated rather than versioned, so a release artifact can always be rebuilt from the archived source.
