# TMLR submission-readiness checklist

This checklist is for the double-blind review package. The working repository is **not itself anonymous** and should not be uploaded wholesale.

## Manuscript PDF

- Build with `python paper/build.py --clean`.
- Submission PDF: `paper/tmlr_submission.pdf`.
- Keep the TMLR style files unmodified.
- Confirm the first-page ChatGPT/LLM-use footnote remains present.
- Confirm `pdfauthor` is empty and the manuscript contains no author names, affiliations, ORCID, personal URLs, acknowledgments, or identifying repository links.
- Check the final LaTeX pass for undefined citations/references.
- Do not submit a PDF whose filename contains an author name.

## Supplementary material

TMLR supplementary material is also double blind. Do **not** zip the working repository directly.

Exclude or sanitize at minimum:

- `.git/` and Git history;
- `CITATION.cff`;
- `.zenodo.json`;
- `LICENSE` in its current form because it names the author;
- `pyproject.toml` metadata fields containing author name, ORCID, or identifying repository URLs;
- project checkpoint/history files that identify the GitHub account or author;
- any README or metadata pointing to the identifying GitHub repository;
- execution/launch manifests containing local paths such as `C:\\Users\\175199\\...`;
- generated files or artifact names containing an author surname.

Prefer an **allowlist-based clean export** containing only the code, frozen protocols, synthetic-data definitions, aggregate paper-facing results, and instructions needed to reproduce the manuscript claims. Preserve scientific hashes/seeds where useful, but replace identifying absolute filesystem roots with anonymous placeholders.

## Current repository facts relevant to anonymization

The working repository intentionally contains author-identifying archival metadata for eventual public release, including citation/Zenodo/package metadata. Several scientific execution manifests also preserve original local paths for provenance. These are appropriate for the public archival artifact after review, but not for the double-blind supplementary ZIP.

## Before upload

- Open the final PDF and visually inspect the first page, figures, captions, references, and PDF properties.
- Inspect the supplementary ZIP contents after extraction in a clean directory.
- Search the extracted submission package for author names, surname, ORCID, GitHub username, institutional names, local usernames/IDs, and identifying URLs.
- Verify that no supplementary file links reviewers to a non-anonymous preprint or repository.
- Verify that the paper is not simultaneously under review at another archival peer-reviewed venue.
- Recheck TMLR's current author/submission guidelines immediately before submission.
