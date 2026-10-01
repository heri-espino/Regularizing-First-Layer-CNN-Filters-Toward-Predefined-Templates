# CP-018 — Compact SN Computer Science rewrite

**Date:** 2026-10-01  
**Status:** manuscript / venue-format migration  
**Evidential role:** manuscript framing and presentation; no new scientific evidence  
**Contemporaneous:** yes

## Why this checkpoint exists

The previous manuscript remained too long and too similar to an experiment archive. The target format is now the Springer Nature article template used for SN Computer Science, and the user explicitly requested a shorter paper resembling recent SN Computer Science articles rather than the earlier TMLR-style submission.

Two 2024 SN Computer Science papers supplied in the project sources were used as the primary editorial references:

- Schneider et al., *Deceptive XAI: Typology, Creation and Detection*;
- Gunasekaran et al., *Which Explanation Should be Selected: A Method Agnostic Model Class Reliance Explanation for Model and Explanation Multiplicity*.

The rewrite follows their conventional journal organization and density rather than reproducing the earlier appendix-heavy structure.

## Scientific question / engineering objective

Produce a much shorter, conventional journal article that preserves the final scientific conclusions while removing experiment-log detail from the main manuscript.

Migrate the paper from the TMLR class to the vendored Springer Nature `sn-jnl.cls` template and make the paper buildable as an SN Computer Science submission.

## What was done

### Main manuscript

`paper/main.tex` was rewritten from scratch using:

```latex
\documentclass[pdflatex,sn-basic]{sn-jnl}
```

New title:

> **Activation Patching in Structured CNNs: Intervention Size, Architecture, and Additivity**

The paper now has the following simple structure:

1. Abstract
2. Introduction
3. Related work
4. Method
5. Results
6. Discussion
7. Conclusion
8. Springer-style declarations

The historical Stage A--G chronology is absent from the publication-facing narrative.

### Length reduction

The new `main.tex` is approximately **3,000 prose words** before references and declarations.

The five historical appendix files are no longer included in the main paper:

- `specificity_robustness_results.tex`
- `final_robustness_results.tex`
- `confirmation_robustness_results.tex`
- `supplementary_results.tex`
- `kernel_matching_results.tex`

They remain versioned for provenance and may be used to construct Supplementary Information.

The main article uses only:

- 4 figures;
- 1 compact study-design table;
- 6 central equations.

### Figures

The main figures are:

1. `fig00_overview.pdf`
2. `fig06_main_results.pdf`
3. `fig07_anchor_specificity.pdf`
4. `fig08_additivity.pdf`

A new presentation-only script, `paper/build_additivity_figure.py`, produces the fourth figure directly from archived additivity summary tables.

### Build system

`paper/build.py` now:

- uses `paper/sn-article-template/sn-jnl.cls`;
- uses Springer Nature bibliography styles under `paper/sn-article-template/bst/`;
- writes `paper/sn_submission.pdf`;
- rebuilds the four publication figures.

The manual GitHub Actions paper workflow now uploads `sn_submission.pdf` under an SN Computer Science artifact name.

The obsolete tracked `paper/tmlr_submission.pdf` was removed.

### Documentation

Updated:

- `paper/README.md`
- `paper/SUBMISSION_CHECKLIST.md`
- `paper/.gitignore`

The checklist is now specific to SN Computer Science rather than TMLR double-blind submission.

## Evidence or results available now

No new scientific outcomes were generated in this checkpoint.

The manuscript preserves the completed results recorded in CP-017, including:

- intervention-size dependence under multiple metrics;
- strong architecture dependence;
- structured versus pixel-permuted filter-bank effects;
- singleton-additive reconstruction showing that (k)-dependence is not itself evidence of channel interaction;
- genuine downstream non-additivity in selected deeper architectures.

Mechanical checks on the new manuscript source show:

- approximately 3,041 words before references/declarations under a simple LaTeX token count;
- all citation keys used by the manuscript exist in `literature/references.bib`;
- no missing `\ref` targets;
- balanced LaTeX environments;
- balanced braces;
- no duplicate labels.

## Interpretation

The paper is now positioned as a conventional empirical XAI / mechanistic-interpretability article rather than as a detailed audit trail.

The publication-facing story is:

1. template retention changes filter geometry;
2. patching behavior depends on intervention size and downstream architecture;
3. the original 2D filter arrangement has a functional effect beyond a matched pixel permutation;
4. intervention-size dependence must be separated from genuine multi-channel non-additivity.

The large robustness and provenance record remains available without dominating the main text.

## What this does not establish

- This checkpoint does not add new evidence.
- The new manuscript has not yet been visually inspected after a successful local Springer Nature PDF build.
- Final author metadata and journal-submission declarations should still be checked before submission.
- Historical appendix files are not yet packaged into a clean Supplementary Information document.

## Repository / provenance pointers

- Manuscript: `paper/main.tex`
- Springer template: `paper/sn-article-template/`
- Build script: `paper/build.py`
- New additivity figure: `paper/build_additivity_figure.py`
- Paper guide: `paper/README.md`
- Submission checklist: `paper/SUBMISSION_CHECKLIST.md`
- Previous scientific interpretation checkpoint: `checkpoints/CP-017_patching-additivity-results.md`
- Main compact rewrite commit: `c2a9cf6277caa6a27c4953a98b6a496011aea8ce`

## Next actions

1. Pull `main` and run `python paper/build.py --clean`.
2. Inspect the compiled Springer Nature PDF for page count, figure scale, table fit, and float placement.
3. Fix only visual/layout issues unless the compiled paper exposes a substantive wording problem.
4. Build a separate compact Supplementary Information file from the retained historical appendix sources rather than restoring them to the main paper.

## Do-not-forget constraints

- Do not restore the five historical appendices to `main.tex`.
- Keep the publication-facing paper near the current level of density.
- Do not reintroduce Stage A--G experiment chronology into the paper.
- Keep robustness audits and exhaustive numbers in Supplementary Information or `analysis/`.
- Preserve the CP-017 scientific distinction between intervention-size dependence and downstream non-additivity.
