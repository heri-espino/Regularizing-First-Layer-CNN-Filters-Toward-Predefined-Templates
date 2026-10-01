# Paper

`main.tex` is the authoritative **Springer Nature / SN Computer Science** manuscript source for:

> **Activation Patching in Structured CNNs: Intervention Size, Architecture, and Additivity**

The manuscript uses the vendored Springer Nature article template under `paper/sn-article-template/` and is intentionally much shorter than the earlier TMLR draft.

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

The previous five embedded appendices are **not included in `main.tex`**. Their source files remain in the repository for provenance and can be converted into Supplementary Information if needed:

- `specificity_robustness_results.tex`
- `final_robustness_results.tex`
- `confirmation_robustness_results.tex`
- `supplementary_results.tex`
- `kernel_matching_results.tex`

Complete numerical tables also remain versioned under `analysis/`. The main paper reports only the estimates needed to support the central argument.

## Main figures

The compact manuscript uses four figures:

1. `fig00_overview.pdf` — controlled renderer, predefined filters, and patch location;
2. `fig06_main_results.pdf` — intervention-size and 16-architecture results;
3. `fig07_anchor_specificity.pdf` — structured versus pixel-permuted filter bank;
4. `fig08_additivity.pdf` — observed versus singleton-additive reconstruction.

The generated figures are rebuilt automatically by `paper/build.py`.

## Build

From the repository root:

```bash
python paper/build.py --clean
```

The compiled manuscript is written to:

```text
paper/sn_submission.pdf
```

The build uses:

- `paper/sn-article-template/sn-jnl.cls`;
- the Springer Nature bibliography styles under `paper/sn-article-template/bst/`;
- `../literature/references.bib`.

The generated PDF and LaTeX intermediates are not intended to be committed; the GitHub Actions `paper-compile` workflow uploads the compiled PDF as an artifact.

## Writing rule

Keep the main paper compact. New robustness checks, large tables, implementation audits, and exhaustive secondary analyses belong in `analysis/` or Supplementary Information unless they change the central scientific conclusion.
