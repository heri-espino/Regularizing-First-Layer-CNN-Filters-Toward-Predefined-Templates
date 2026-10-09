# Paper

`main.tex` is the authoritative **Springer Nature / SN Computer Science** manuscript source for:

> **When Do Activation-Patching Effects Add Up? Evidence from Controlled CNNs**

The manuscript uses the vendored Springer Nature article template under `paper/sn-article-template/`. It is based on the reviewed `sn_submission(6).pdf` revision, followed by the direct-language pass (CP-021) and the second readability pass recorded in `checkpoints/CP-022_second-readability-pass.md`. Figure 3 uses **Release − retention**, matching the training-regime terminology in the text; narrative citations use `\citet` and parenthetical citations use `\citep`. The Vaidyanathan et al. (2026) entry is included in the central `literature/references.bib` database.

## Editorial structure

The main paper now follows the structure used by recent SN Computer Science research articles:

1. Abstract and keywords
2. Introduction
3. Related work
4. Method
5. Results
6. Discussion
7. Conclusion
8. Springer-style declarations

The paper is organized around the scientific story rather than the chronological Stage A--G experiment history.

## What moved out of the main paper

The previous five embedded appendices are **not included in `main.tex`**. Their source files remain in the repository for provenance, but the authoritative submission-facing supplement is now `paper/sn_supplement.tex`:

- `specificity_robustness_results.tex`
- `final_robustness_results.tex`
- `confirmation_robustness_results.tex`
- `supplementary_results.tex`
- `kernel_matching_results.tex`

Complete numerical tables also remain versioned under `analysis/`. The main paper reports only the estimates needed to support the central argument. The file `paper/SUPPLEMENT_REPRODUCIBILITY.md` maps every main figure and principal statistic to its archived inputs and frozen protocol.

## Main figures

The compact manuscript uses five figures:

1. `fig00_overview.pdf` — controlled renderer, predefined filters, and patch location;
2. `fig09_additivity_curves.pdf` — direct observed/additive curves and residual energy;
3. `fig06_main_results.pdf` — intervention-size and 16-architecture results;
4. `fig07_anchor_specificity.pdf` — structured versus pixel-permuted filter bank;
5. `fig08_additivity.pdf` — architecture-wide and spatial-control additive reconstruction.

The generated figures are rebuilt automatically by `paper/build.py`. Rebuild both PDFs before making the ZIP so the manuscript, supplement title, figure numbering, and bibliography all reflect the same source revision.

## Build

From the repository root:

```bash
python paper/build.py --clean
python paper/build_supplement.py --clean
python paper/build_submission_package.py
```

The generated submission files are:

```text
paper/sn_submission.pdf
paper/sn_supplement.pdf
paper/dist/sn_submission_package.zip
```

The build uses:

- `paper/sn-article-template/sn-jnl.cls`;
- the Springer Nature bibliography styles under `paper/sn-article-template/bst/`;
- `../literature/references.bib`.

The generated PDFs, ZIP, and LaTeX intermediates are not intended to be committed; the manual-only GitHub Actions `paper-compile` workflow builds and uploads the manuscript, supplement, logs, and allowlisted reproducibility ZIP as an artifact.

## Writing rule

Keep the main paper compact. New robustness checks, large tables, implementation audits, and exhaustive secondary analyses belong in `analysis/` or Supplementary Information unless they change the central scientific conclusion.


Use the most direct wording that preserves the meaning. Prefer familiar technical terms and explicit descriptions of operations to abstract labels or chains of modifiers. The rules and examples in `literature/TERMINOLOGY.md` apply to the main manuscript, captions, and standalone supplement. Simplifying prose must preserve metric definitions, uncertainty, post-hoc status, and the limits of causal claims.
