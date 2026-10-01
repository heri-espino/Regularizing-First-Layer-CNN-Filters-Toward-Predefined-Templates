# SN Computer Science submission checklist

## Manuscript

- Build with `python paper/build.py --clean`.
- Submission PDF: `paper/sn_submission.pdf`.
- Keep the Springer Nature template files under `paper/sn-article-template/` unmodified.
- Confirm that the paper compiles without undefined citations or references.
- Check that the abstract remains concise and contains no citations or equations.
- Check all four figures at normal reading size.
- Keep the main article free of the historical Stage A--G naming used internally.
- Do not re-embed the five historical appendix files into the main manuscript.

## Front matter and declarations

Before submission, verify the final author list, affiliations, corresponding-author details, and any ORCID information required by the submission system.

Confirm that the declarations at the end of `main.tex` accurately state:

- funding;
- competing interests;
- ethics approval / consent;
- data availability;
- code availability;
- author contributions.

Update any statement that changes before submission rather than leaving a generic placeholder.

## Supplementary Information

Use an allowlist-based export rather than uploading the working repository wholesale.

Include only material needed to support or reproduce the paper, such as:

- frozen protocols;
- renderer and model definitions;
- analysis code;
- aggregate result tables;
- secondary robustness tables and figures;
- instructions for reproduction.

Raw checkpoints and tens of thousands of per-model evaluator JSON files are not needed in the submission package.

Remove local absolute paths, temporary machine-specific files, Git history, and unrelated development notes from the supplementary archive.

## Final visual pass

Compare the compiled article with recent SN Computer Science papers:

- section hierarchy should be simple;
- figures should carry most of the quantitative story;
- tables should be sparse and readable;
- Discussion should interpret rather than repeat Results;
- supporting audits and exhaustive secondary numbers should remain outside the main text.

The target is a conventional journal article, not an experiment log.
