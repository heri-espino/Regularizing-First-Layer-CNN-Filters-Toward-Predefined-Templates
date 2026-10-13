# SN Computer Science submission checklist

## Manuscript

- Build with `python paper/build.py --clean`.
- Submission PDF: `paper/sn_submission.pdf`.
- Keep the Springer Nature template files under `paper/sn-article-template/` unmodified.
- Confirm that the paper compiles without undefined citations or references.
- Check that the abstract remains concise and contains no citations or equations.
- Check all five figures at normal reading size, especially the Figure 2 residual legend and the internal metric labels in Figure 5.
- Confirm that Figure 3 labels the treatment difference **Release − retention**, matching the text.
- Confirm the main PDF, supplement, and citation metadata use **When Do Activation-Patching Effects Add Up? Evidence from Controlled CNNs**.
- Check narrative citations for duplicated author names; use `\citet` for narrative citations and `\citep` for parenthetical citations.
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

- Build `paper/sn_supplement.pdf` with `python paper/build_supplement.py --clean`.
- Confirm Supplementary Section S1 is **Architecture and training specification**, matching the citation in the main text.
- Confirm the numerical tables in Sections S2--S5 agree with the current analysis CSVs.
- Review `paper/SUPPLEMENT_REPRODUCIBILITY.md` for the figure/statistic provenance map.

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

Create all four deliverables with `python paper/build_submission_package.py --verify`. This runs a clean extraction, checksum verification, all five figure generators, and selected numeric checks. Inspect:

- `paper/dist/manuscript.pdf` — main manuscript upload;
- `paper/dist/supplementary_information.pdf` — supplementary PDF upload;
- `paper/dist/manuscript_sources.zip` — independently rebuildable LaTeX sources;
- `paper/dist/activation_patching_reproducibility.zip` — reviewer-facing reproduction material.

Confirm that the reproduction ZIP's README links resolve after extraction; `reproduce.py --all` regenerates five figure PDFs and produces a verification report. Its `manifest.json` records original-to-exported paths, SHA-256 checksums, and source commit when available. No raw model checkpoints or per-model JSONs are included. The code-only experiment scripts are archived for inspection, not advertised as end-to-end train/evaluate commands.

Submit the files in the appropriate publisher fields; do not upload a single archive that mixes manuscript PDF, supplementary PDF, and code. Remove the obsolete `paper/dist/sn_submission_package.zip` from local dist if one exists: it is not produced by the new exporter.

## Final visual pass

Compare the compiled article with recent SN Computer Science papers:

- section hierarchy should be simple;
- figures should carry most of the quantitative story;
- tables should be sparse and readable;
- Discussion should interpret rather than repeat Results;
- supporting audits and exhaustive secondary numbers should remain outside the main text.

The target is a conventional journal article, not an experiment log.
