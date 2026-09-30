# CP-015 — SN Computer Science figure-led manuscript restructure

Date: 2026-09-30
Branch: paper-restructure-sncs
Status: main scientific restructure implemented; additive-reconstruction results pending

## Objective

Reduce numerical/table burden in the main manuscript and make the argument readable as a sequence of scientific questions rather than a chronological experiment log. This checkpoint does not attribute the previous desk rejection to manuscript length or style.

## Implemented

- Rewrote paper/main.tex around Introduction, Related work, Experimental design, Results, Discussion and limitations, and Conclusion.
- Removed the five appendix inputs from the main manuscript.
- Added a standalone paper/supplement.tex that preserves the exhaustive material in three evidential blocks.
- Added one evidence-roadmap table with inferential unit and analysis status.
- Moved compact accuracy/filter-similarity context for the four spatial-control architectures into the main paper.
- Split the former combined intervention-size/architecture figure generator into:
  - fig02_intervention_size.pdf: retention and release curves plus paired differences;
  - fig04_architecture.pdf: full 16-architecture forest plot.
- Reserved the additive-reconstruction result immediately after the intervention-size result.
- Defined only the frozen additive method in the paper; no pending outcome is anticipated.
- Added the three supplied SN Computer Science references and cited them only where they sharpen the argument.

## Main narrative

1. constant regularization preserves the predefined first-layer structure;
2. structural similarity does not determine intervention behavior;
3. release-versus-retention differences change with intervention size;
4. the pending decomposition asks how much is reconstructable from singleton contributions, cancellation, model-tail non-additivity, and metric nonlinearity;
5. downstream architecture strongly changes the comparison;
6. the original spatial arrangement contributes beyond the pixel-permuted Gram/rank/spectrum-matched control, but conditionally on architecture, metric, and channel selection.

## Additivity boundary

The analysis under studies/cnn_patching_additivity/ is post-hoc on frozen checkpoints. Its role is explanatory decomposition, not independent confirmation.

Do not:
- call metric curvature a model interaction;
- call a nonzero residual synergy or redundancy without further evidence;
- revise the abstract/title around an additive or non-additive story before the frozen results exist.

## Remaining work after the running analysis completes

1. insert the additive-reconstruction figure and one result subsection;
2. update abstract and title only after that result is known;
3. perform a final claim/terminology pass;
4. migrate the stabilized manuscript to the current SN Computer Science publisher template;
5. compile and visually inspect both main manuscript and supplement;
6. merge this branch only after the final paper-level review.
