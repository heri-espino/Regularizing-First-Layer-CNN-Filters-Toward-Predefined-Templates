# Paper

`main.tex` is the authoritative manuscript source for **Template Priors in Small CNNs: Activation-Patching Effects Depend on the Number of Patched Channels**.

The appendix material is split into three files so the main source remains readable:

- `confirmation_robustness_results.tex` — complete Stage-D and Stage-E numerical support
- `supplementary_results.tex` — historical Stages A--C
- `kernel_matching_results.tex` — complete endpoint kernel-matching table

The bibliography is `../literature/references.bib`. The minimal TMLR style files required for compilation are vendored in `tmlr/` and retain their upstream license.

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
