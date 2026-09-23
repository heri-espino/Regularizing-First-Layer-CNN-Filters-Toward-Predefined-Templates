# CP-014 — Final readability and submission-readiness pass

**Date:** 2026-09-23  
**Status:** submission-polish complete; one final manual PDF build recommended before upload  
**Evidential role:** manuscript/repository packaging only; no new scientific outcomes  
**Contemporaneous:** yes

## Why this checkpoint exists

After the referee-driven scientific revision, the remaining task was not another experiment but a final pass for human readability, double-blind submission hygiene, figure/build ergonomics, and repository behavior.

## What was changed

### Readability

A sentence-length audit of the main manuscript identified only two remaining 45+ word prose sentences. Both were split without changing scientific content:

- the opening structured-filter literature sentence;
- the compact description of the 16-architecture grid.

A fresh static audit after these edits reports no prose sentences at or above 45 words under the same simple sentence-length heuristic.

### Double-blind manuscript filename

The manuscript build no longer produces an author-identifying filename.

Old:
- `paper/espino_2026_template-priors.pdf`

Current:
- `paper/tmlr_submission.pdf`

The generic filename is now used consistently by:
- `paper/build.py`;
- `paper/README.md`;
- root `README.md`;
- manuscript GitHub Actions artifacts.

### Anonymous-supplement warning

Added:
- `paper/SUBMISSION_CHECKLIST.md`

The checklist records that the working repository itself is not an anonymous review artifact and must not be uploaded wholesale.

Author-identifying archival metadata remain intentionally present in the working/public-release repository, including:
- `CITATION.cff`;
- `.zenodo.json`;
- `pyproject.toml`;
- `LICENSE`;
- project/checkpoint history.

Several versioned scientific execution manifests also preserve original local provenance paths containing `C:\Users\175199\...`.

For double-blind review, supplementary material should therefore be created by an allowlist-based clean export rather than by zipping the repository.

### GitHub Actions policy

Heavy derived-output workflows now follow the repository policy:

- `.github/workflows/paper_compile.yml` is manual-only via `workflow_dispatch`;
- `.github/workflows/paper_figures.yml` is manual-only via `workflow_dispatch`;
- the publication-figure workflow no longer auto-commits or pushes generated outputs;
- both workflows upload artifacts with `actions/upload-artifact@v4`;
- artifact retention is 30 days;
- artifact names are generic and include the commit SHA.

Lightweight reproducibility/static CI remains automatic.

## Fresh verification

Current-source static checks:

- missing bibliography keys: 0;
- unresolved cleveref references: 0;
- duplicate labels: 0;
- displayed equations: 13;
- displayed equations without labels: 0;
- raw `\ref` commands: 0;
- unnumbered bracket displays: 0;
- main-text sentences >=45 words under the audit heuristic: 0;
- paper build output: `paper/tmlr_submission.pdf`;
- paper-compile workflow: manual-only;
- paper-figures workflow: manual-only;
- paper-figures auto-commit/push: absent.

Fresh file-content checks on the manuscript-facing build/workflow/readme files find no author-name, ORCID, GitHub-username, or old author-identifying PDF filename tokens.

The full TeX build had already passed after CP-013. The CP-014 edits to `main.tex` are prose-only sentence splits, while the other changes affect output filenames/documentation/workflow triggers. Because heavy compilation is now intentionally manual-only and the current tool connection does not expose workflow dispatch, run the manual `paper-compile` workflow once before actual submission to obtain fresh end-to-end build evidence for the exact CP-014 commit.

## Current TMLR-facing submission constraints

As checked against current TMLR author/submission guidance:

- the review process is double blind and both paper and supplementary material must be anonymized;
- the official TMLR LaTeX style/template must be used without formatting modifications;
- supplementary data/code are encouraged but must also be anonymous;
- LLM assistance is permitted, with authors responsible for the content, and TMLR requires explicit disclosure in a first-page footnote;
- a broader-impact statement is required when the work carries significant risk of harm.

The manuscript already includes the first-page ChatGPT disclosure.

## Next actions

1. Manually run `paper-compile` from GitHub Actions or locally with:
   `python paper/build.py --clean`.
2. Visually inspect `paper/tmlr_submission.pdf`, including PDF properties.
3. If submitting supplementary code, create a clean allowlist-based anonymous ZIP; do not upload the working repository.
4. Search the extracted anonymous package for author names, ORCID, GitHub username, institutional names, local usernames/IDs, and identifying URLs.
5. Recheck TMLR's current author and submission guidelines immediately before upload.

## Do-not-forget constraints

- Do not restore an author-identifying review PDF filename.
- Do not make heavy paper/figure workflows automatic on push.
- Do not auto-commit generated heavy outputs from Actions.
- Do not upload the current repository wholesale as double-blind supplementary material.
- Public archival metadata should be restored/used only in the post-review public artifact, not the anonymous review package.
