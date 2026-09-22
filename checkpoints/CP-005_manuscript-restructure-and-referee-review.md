# CP-005 — Manuscript restructure and strict referee review

**Date:** reconstructed 2026-09-21  
**Status:** manuscript + interpretation checkpoint  
**Evidential role:** synthesis/referee assessment  
**Contemporaneous:** no

## Why this checkpoint exists

After architecture robustness completed, the project had enough evidence to stop narrating itself as a sequence of internal “stages.” The manuscript needed to become a short scientific argument centered on one claim and its alternative explanations.

A strict referee pass also showed that the manuscript was **not yet submission-ready**.

## Scientific objective

Convert the experimental history into a concise evidence hierarchy:

1. structured regularization preserves first-layer template-like weights;
2. structural retention does not imply a simple functional patching signature;
3. the release-vs-retention comparison depends on channel budget;
4. the prespecified budget contrast survives alternative output metrics;
5. downstream architecture strongly conditions the measurement;
6. remaining alternatives must be isolated before submission.

## What was done

The manuscript was restructured so that paper-facing prose no longer uses Stage A--F labels.

Other manuscript conventions:

- `cleveref` used for cross-references;
- every displayed equation numbered and labeled;
- three main figures:
  1. renderer/template/patching overview;
  2. learned-kernel gallery;
  3. central channel-count + architecture result figure;
- redundant main-text numerical tables removed;
- complete numerical tables retained in appendices;
- results organized around scientific questions, not chronology.

## Evidence or results available now

No new scientific outcomes were generated in this checkpoint.

The referee-style review identified the following major remaining concerns:

1. **template-specificity is unisolated**: constant vs annealed regularization toward the same bank does not show that the effect is specific to structured edge/corner/ring anchors;
2. **random-channel controls matter**: architecture dependence appears even for random channel subsets, so the phenomenon may be more general than concept-ranked channels;
3. **sphericity robustness**: the 16-level repeated-measures ANOVA should be supplemented by assumption-robust diagnostics;
4. **metric wording**: robustness is of the prespecified (B), not of the entire pointwise curve;
5. **structure/function link**: directly compare template-retention difference with functional (B);
6. **architecture specification**: exact architecture definitions belong in the appendix;
7. **external validity remains narrow**: synthetic/small-CNN scope must stay explicit.

Provisional referee recommendation at this point: **Leaning Reject / major revision**, not because of weak experiments but because the paper's scientific identity was not yet fully isolated.

## Interpretation

The main bottleneck shifted from “more evidence generally” to **one decisive specificity experiment plus better analysis of existing evidence**.

Two possible final paper identities were recognized:

- **template-specific paper** if structured spatial anchors behave differently from matched controls;
- **measurement paper** if the same behavior appears for matched/random anchors.

## What this does not establish

- This checkpoint is not scientific evidence.
- The referee assessment is not a publication outcome.
- The manuscript title/abstract should not be finalized around template-specificity until the specificity experiment finishes.

## Repository / provenance pointers

- Manuscript: `paper/main.tex`
- Revision notes: `paper/REVISION_PLAN.md`
- Main-result figure builder: `paper/build_main_results_figure.py`
- Architecture report: `analysis/architecture_robustness_001/REPORT.md`

## Next actions at this historical point

1. Freeze a fresh anchor-specificity experiment.
2. Freeze post hoc architecture diagnostics using existing Stage-F outputs.
3. Do not add an external benchmark until the paper's identity is clearer.

## Do-not-forget constraints

- Keep paper-facing prose descriptive rather than Stage-letter based.
- Do not overstate pointwise metric robustness.
- Do not equate pretty/structured filters with interpretability.
