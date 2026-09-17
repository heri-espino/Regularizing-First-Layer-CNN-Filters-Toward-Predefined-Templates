# Manuscript source

`main.tex` is the authoritative manuscript source.

The appendix material is split into three files to keep the main source readable:

- `confirmation_robustness_results.tex` — complete Stage-D and Stage-E numerical support
- `supplementary_results.tex` — historical Stages A--C
- `kernel_matching_results.tex` — complete endpoint kernel-matching table

The bibliography is `../literature/references.bib`. The minimal TMLR style files needed for compilation are vendored in `tmlr/` and retain their upstream license.

## Build

Run from the repository root:

```bash
python build.py
```

The compiled manuscript is written to:

```text
espino_2026_template-priors.pdf
```

Use a clean rebuild when changing bibliography or style files:

```bash
python build.py --clean
```

LaTeX intermediates are written to `papers/build/` and are ignored by Git.

The Markdown drafts and editorial planning files used during development are intentionally excluded from the archival manuscript directory; the LaTeX source and frozen analysis outputs are the publication record.
