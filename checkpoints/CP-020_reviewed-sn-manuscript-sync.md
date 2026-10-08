# CP-020 — Reviewed SN manuscript synchronization

**Date:** 2026-10-08  
**Status:** manuscript / submission preparation  
**Evidential role:** presentation and implementation integrity only  
**Contemporaneous:** yes

## Why this checkpoint exists

The author reconfirmed SN Computer Science and requested repository consistency with the reviewed `sn_submission(5).pdf`. The default branch still contained the earlier compact SN source and title. The reviewed LaTeX revision was available in the working session and was synchronized rather than rewritten again.

## Scientific question / engineering objective

Make local builds produce the reviewed manuscript, with consistent training-regime terminology, citations, supplement title, figure numbering, and repository metadata.

## What was done

- Synchronized `paper/main.tex` with the reviewed revision, preserving its results and restrained contribution claims.
- Integrated the Vaidyanathan et al. (2026) entry into `literature/references.bib`; no separate bibliography file is required by the build or package.
- Changed the Figure 3 generator's treatment label from Annealed − constant to Release − retention.
- Updated the supplement title and figure/data provenance numbering to follow the current main-figure order.
- Allowed long provenance paths to wrap inside the supplement table rather than overflow its columns.
- Updated existing layout checks to find the current labels and compare relative positions rather than an obsolete absolute coordinate.
- Updated current README, checklist, citation/Zenodo metadata, scientific status, and operational handoff.
- Preserved historical checkpoints and frozen experiment/analysis sources.

## Evidence or results available now

No new scientific outcomes are available or interpreted at this checkpoint.

Local verification on 2026-10-08:

- `python paper/build.py --clean`: successful, 17-page main article.
- `python paper/build_supplement.py --clean`: successful, 6-page supplement.
- Both final LaTeX logs contain no undefined citations/references or overfull boxes. Remaining messages concern harmless float placement and a main-PDF bookmark-level jump.
- The seven existing publication-layout tests pass after updating stale selectors/coordinates.
- `python paper/build_submission_package.py`: successful, 133 archive entries, approximately 3.7 MiB compressed.
- ZIP integrity and byte-for-byte inclusion of the current main PDF, supplement, manuscript source, and bibliography were verified.
- All 17 cited bibliography keys resolve, including the newly integrated multiple-mediator reference.
- PDF text comparison with the reviewed version gives similarity 0.999631 after whitespace normalization; the intended Figure 3 terminology change is present. Prose before the first illustration matches exactly.
- The regenerated Figure 3 and the supplement's provenance page were rendered and visually checked.
- `git diff --check`: no whitespace errors.

Reviewed PDF provenance: `sn_submission(5).pdf`, SHA-256 `f404aa2a8f94f8194a2d60e39af7f7416b9f7086ed1ba99fe8afd8fe94986b56`.

Only text sources and documentation are part of this update. The author will regenerate the final PDFs and ZIP locally; generated experiment outputs are unchanged.

## Interpretation

The manuscript's empirical contribution concerns when individual logit changes explain a joint patching contrast and when the aggregate residual changes its interpretation. Prior multi-component interaction work is acknowledged explicitly. The synchronization does not turn that diagnostic into a new causal mediation estimand.

## What this does not establish

- Submission readiness does not predict editorial acceptance.
- No new training run, confirmatory replication, or natural-image evidence was introduced.
- The journal upload interface and final author-entered submission metadata are not verified here.
- Raw checkpoints remain in the separately retained experiment store.

## Repository / provenance pointers

- Manuscript: `paper/main.tex`
- Bibliography: `literature/references.bib`
- Figure 3 generator: `paper/build_main_results_figure.py`
- Supplement: `paper/sn_supplement.tex`
- Figure/statistic map: `paper/SUPPLEMENT_REPRODUCIBILITY.md`
- Existing scientific evidence: CP-017 and the archived `analysis/` tables
- Prior package audit: `checkpoints/CP-019_sn-submission-package-audit.md`
- Synchronization base: `4ed4439df378251f07238f0afa963427a3b86f3d`

## Next actions

From the repository root, after pulling the updated main branch:

```powershell
python paper/build.py --clean
python paper/build_supplement.py --clean
python paper/build_submission_package.py
```

Inspect the main PDF, standalone supplement, and ZIP from the same revision before submitting to SN Computer Science.

## Do-not-forget constraints

- Keep the journal target SN Computer Science unless the author changes it.
- Do not restart experiments or restore the historical appendices to the main paper.
- Keep the exact-additivity control, the BN2 sign reversal, and the spatial-control comparison distinct.
- Use narrative and parenthetical citation commands consistently.
- Rebuild both PDFs before packaging; do not combine current sources with old generated PDFs.
- Heavy PDF/figure workflows remain manual-only.
