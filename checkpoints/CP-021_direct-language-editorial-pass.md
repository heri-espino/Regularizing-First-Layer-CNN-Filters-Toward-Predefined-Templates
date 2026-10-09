# CP-021 — Direct-language editorial pass

## 1. Status, date, and evidential role

Date: 2026-10-09. Status: editorial source revision complete and typesetting-checked. This is a presentation change, not a new experiment, statistical analysis, or replication. Baseline source commit: `0f44357232457b0e5c8c4c5fe6f309678bee5dd2`.

## 2. Why this checkpoint exists

After reviewing `sn_submission(6).pdf`, the author requested a full pass to replace unnecessarily difficult expressions with direct wording. The request applies throughout the active manuscript, not only to the three examples initially discussed.

## 3. Objective

Make the argument easier to read while preserving the mathematical definitions, experimental results, uncertainty, evidential status, and limits of the claims.

## 4. What was done

- Reviewed the full main manuscript and standalone supplement.
- Replaced abstract labels such as “singleton superposition,” “individual-effect geometry,” “metric-transformed sum,” and “bank-based training regimes” with explicit descriptions of channel patches, sums of logit changes, metric evaluation, and training.
- Split long sentences in the literature comparison, statistical methods, architecture results, and interpretation of the spatial control.
- Rewrote long modifier chains in prose and captions as clauses.
- Kept standard technical vocabulary where it carries precision: activation patching, centered logits, additivity, residual, Gram matrix, equivalence margin, and higher-order interactions.
- Updated `literature/TERMINOLOGY.md`, `paper/README.md`, and current handoff notes so later revisions follow the same rule.

## 5. Evidence available now

Fresh source comparisons verified that:

- all 14 displayed main-text equations and the supplement's displayed equation are unchanged;
- all 75 main-text and 68 supplementary decimal values are unchanged and remain in the same order;
- citation commands, equation/section/figure/table labels, cross-reference targets, and figure input paths are unchanged;
- the identified unnecessarily dense expressions no longer occur in active manuscript prose.

Typesetting validation used the vendored Springer Nature class and bibliography style, the unchanged central bibliography, and the five existing tracked figure PDFs. The main manuscript compiled to 17 pages; the standalone supplement compiled with its official builder to 6 pages. Final logs contain no unresolved citations/references, duplicate-label warnings, or overfull boxes. Contact-sheet inspection found no clipping or overlapping text.

The full main builder was not run in this validation snapshot: figure-generation scripts and archived numerical inputs are unchanged. The author will run the normal main builder, which regenerates the figures, and then rebuild the supplement and submission package. No generated PDFs or ZIP files are committed in this revision.

## 6. Interpretation

The revision improves wording and sentence structure. It preserves the distinction between a score changing with intervention size under exact logit additivity and a joint logit response that individual changes fail to predict.

## 7. What this does not establish

This editorial pass provides no new scientific outcomes, no fresh-sample confirmation of the post-hoc reconstruction, and no additional external-validity evidence. It does not change the interpretation of equivalence tests or identify a unique causal mechanism.

## 8. Repository pointers

- Active manuscript: `paper/main.tex`.
- Active supplement: `paper/sn_supplement.tex`.
- Writing guide: `literature/TERMINOLOGY.md`.
- Prior reviewed-source synchronization: `checkpoints/CP-020_reviewed-sn-manuscript-sync.md`.
- Main build: `paper/build.py`.
- Supplement build: `paper/build_supplement.py`.
- Submission package: `paper/build_submission_package.py`.

## 9. Next actions

Pull the source revision, rebuild the main manuscript and supplement, and rebuild the submission ZIP from the same revision. Inspect the regenerated submission files before upload.

## 10. Do-not-forget constraints

Use the most direct wording that preserves meaning. Do not sum scalar single-channel scores to predict a joint score: sum logit changes first and apply the metric afterwards. Keep renderer blocks as the inferential unit, preserve post-hoc status, and distinguish an interval containing zero from an equivalence result. Preserve frozen protocols, archived outputs, executable identifiers, and historical checkpoints.
