# CP-022 — Second readability pass

## 1. Status, date, and evidential role

2026-10-09. Editorial revision complete and typesetting-checked. Baseline: `9400af1417ac215a17916c9c0d03f6d0326be079`. This is a second pass on the active manuscript and supplement, not a new scientific analysis.

## 2. Why this checkpoint exists

The author requested a second readability pass after CP-021. The goal is fluent, direct prose rather than repeated rewriting or further compression.

## 3. Objective

Remove remaining repetition, ambiguous referents, abstract transitions, and difficult sentence structure while retaining mathematical precision and the scope of the claims.

## 4. What was done

- Reviewed both active LaTeX sources in full against the current remote revision.
- Clarified that centered-logit changes are summed before the reconstructed output is scored.
- Replaced abstract statements about comparisons with explicit statements about the reported contrast.
- Removed the repeated conclusion about the surrounding architecture.
- Separated inference procedures and equivalence interpretation into clearer paragraphs.
- Made section headings state the observed result directly.
- Replaced ambiguous supplement pronouns with explicit operations and training-condition names.
- Explained preservation of filter coefficients in ordinary language while retaining values and multiplicities.
- Updated current handoff notes and the latest-checkpoint pointer. CP-021 and older checkpoints remain unchanged.

## 5. Evidence available now

Fresh source checks against the baseline verified unchanged:

- 14 displayed main-text equations and one displayed supplementary equation;
- 138 main-text and 42 supplementary inline mathematical expressions, in the same order;
- all decimal values (75 main-text, 68 supplementary), in the same order;
- citation commands, labels, cross-reference targets, and five main-figure input paths.

Both LaTeX sources compiled successfully using the vendored Springer Nature class, unchanged bibliography, and existing tracked figures. Final output is 17 pages for the main paper and 6 pages for the supplement. Final logs show no unresolved citations or references, duplicate labels, or overfull boxes. Visual contact-sheet inspection found no clipping or overlapping text.

This was a typesetting check with existing figure assets; the full main builder that regenerates figures and the submission package builder were not run in this validation snapshot. No generated PDFs, ZIPs, figure assets, experiments, or archived numerical inputs are committed.

## 6. Interpretation

The second pass improves transitions and makes the stated operation or result easier to identify. It retains the distinction between score dependence under exact logit additivity and joint logit changes that individual patches fail to reconstruct.

## 7. What this does not establish

No new experiment, independent replication, causal attribution, or external-validity claim is introduced. Equivalence remains tied to the pre-specified margins, and an interval containing zero is not treated as proof of equivalence.

## 8. Repository pointers

- `paper/main.tex`
- `paper/sn_supplement.tex`
- `literature/TERMINOLOGY.md`
- `checkpoints/CP-021_direct-language-editorial-pass.md`
- `paper/build.py`, `paper/build_supplement.py`, `paper/build_submission_package.py`

## 9. Next actions

Pull the revision and regenerate the main PDF, supplement, and submission package together. Inspect those outputs before uploading.

## 10. Do-not-forget constraints

Prefer direct language without removing technical distinctions. Preserve the renderer-block inferential unit, post-hoc status, numerical definitions, paired comparisons, and limits of causal and generalization claims. Keep frozen protocols and historical results unchanged.
