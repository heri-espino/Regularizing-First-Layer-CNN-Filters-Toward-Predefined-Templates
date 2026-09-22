# CP-010 — Post hoc architecture diagnostics complete

**Date:** 2026-09-22  
**Status:** results-complete  
**Evidential role:** post hoc robustness analysis  
**Contemporaneous:** yes

## Why this checkpoint exists

A strict referee pass identified two architecture-related reviewer risks after the prospectively frozen architecture study: the original univariate repeated-measures omnibus relied on sphericity assumptions, and the headline architecture dependence might partly reflect the validation-derived selected-channel ranking. The frozen post hoc diagnostic workflow was created to address those concerns without retraining.

## Scientific question / engineering objective

Do the completed architecture-study conclusions survive inference that does not rely on uncorrected sphericity, and does architecture dependence remain when patching random channel subsets rather than validation-ranked channels?

## What was done

The frozen post hoc analysis reuses the completed 25,600-model architecture evaluator outputs and retrains no models.

It reports:

- Greenhouse--Geisser-corrected repeated-measures tests;
- within-block 100,000-permutation architecture omnibus tests;
- Friedman sensitivity tests;
- architecture heterogeneity for the mean over eight random channel orders;
- selected-versus-random architecture-mean comparisons;
- a random-channel TinyGMP-minus-Plain2-GMP bridge;
- structural-retention-versus-functional-B descriptive summaries;
- exact architecture definitions and parameter counts.

The workflow is explicitly outcome-informed and must not be described as prospective confirmation.

## Evidence or results available now

Primary task: `two_concepts`.

Inferential unit: renderer block, (n=100), after averaging the four initialization replicates within block.

### Sphericity-robust selected-channel architecture omnibus

Centered-logit fidelity:

- original repeated-measures (F=77.0874);
- Greenhouse--Geisser epsilon (=0.1861);
- GG-corrected (p=1.56\times10^{-34});
- within-block permutation (p=1.0\times10^{-5});
- Holm-adjusted permutation (p=2.0\times10^{-5});
- Friedman (p=3.52\times10^{-146}).

Probability error reduction:

- original repeated-measures (F=656.7002);
- Greenhouse--Geisser epsilon (=0.5973);
- GG-corrected (p) numerically underflowed to 0;
- within-block permutation (p=1.0\times10^{-5});
- Holm-adjusted permutation (p=2.0\times10^{-5});
- Friedman (p=7.79\times10^{-200}).

Thus the architecture result is not dependent on the uncorrected sphericity assumption.

### Random-channel architecture dependence

Using the mean over eight random channel orders:

- centered-logit architecture permutation (p=1.0\times10^{-5}), Holm (p=2.0\times10^{-5});
- probability-error architecture permutation (p=1.0\times10^{-5}), Holm (p=2.0\times10^{-5}).

Selected-versus-random architecture-mean Spearman correlations:

- centered-logit fidelity: (ho=+0.256);
- probability error reduction: (ho=+0.724).

Random-channel TinyGMP-minus-Plain2-GMP bridge:

- centered logits: mean (+0.002765), 95% CI ([+0.000014,+0.005515]), Holm (p=0.0488);
- probability error reduction: mean (+0.319871), 95% CI ([+0.312788,+0.326953]), Holm (p=2.76\times10^{-96}).

Integrity:

- evaluated model JSONs: 25,600;
- maximum full-patch logit error: 0;
- maximum no-op logit error: 0.

## Interpretation

Architecture dependence is robust to sphericity correction, within-block permutation inference, and rank-based Friedman inference.

Architecture dependence also remains when the patched channel sets are random. Therefore the main architecture result cannot be attributed solely to the validation-derived selected-channel ranking.

However, the selected-versus-random architecture pattern is substantially more similar for probability error reduction than for centered-logit fidelity. This constrains any claim that one ranking-independent mechanism fully explains both metrics.

The random-channel TinyGMP-versus-Plain2-GMP bridge remains clearly positive for probability error reduction and is only marginally positive for centered logits. The architecture effect is therefore partly ranking-independent, but its magnitude and metric dependence remain important.

## What this does not establish

- These diagnostics are post hoc, not prospective.
- Random-channel persistence does not identify a unique mechanism.
- It does not imply that ranking is irrelevant; selected and random patterns differ, especially for centered logits.
- Correlations between structural retention and functional B are descriptive and must not be interpreted as mediation or causation.
- The results remain restricted to the controlled synthetic tasks and tested small-CNN family.

## Repository / provenance pointers

- Protocol: `studies/cnn_architecture_posthoc/PROTOCOL.md`
- Implementation: `studies/cnn_architecture_posthoc/analyze.py`
- Analysis: `analysis/architecture_posthoc_diagnostics_001/`
- Report: `analysis/architecture_posthoc_diagnostics_001/REPORT.md`
- Architecture definitions: `analysis/architecture_posthoc_diagnostics_001/architecture_definitions.csv`
- Manuscript: `paper/main.tex`
- Source architecture analysis: `analysis/architecture_robustness_001/`

## Next actions

1. Integrate the sphericity-robust omnibus and random-channel result into the revised manuscript.
2. Keep the existing prospective architecture experiment as the primary evidential source and label these additions explicitly post hoc.
3. Interpret the fresh anchor-specificity experiment before finalizing the paper's scientific identity.

## Do-not-forget constraints

- Never call these diagnostics prospective or confirmatory.
- Architecture dependence survives random channel subsets; this should not be hidden.
- Ranking still matters quantitatively, especially for centered-logit fidelity.
- Do not infer evidence from 25,600 model count; the inferential unit is 100 renderer blocks.
