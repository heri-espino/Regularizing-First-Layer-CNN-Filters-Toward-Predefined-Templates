# CP-012 — Manuscript rewritten from final evidence and full literature corpus

**Date:** 2026-09-22  
**Status:** manuscript rewrite complete; referee pass pending  
**Evidential role:** manuscript/framing only; no new scientific outcomes  
**Contemporaneous:** yes

## Why this checkpoint exists

The fresh anchor-specificity experiment and the post hoc architecture diagnostics materially changed the paper's scientific identity. The previous manuscript was written before those final results and still carried too much of the project's chronological development history.

A strict referee pass had also identified that the related-work positioning was too narrow. Before rewriting the manuscript, the complete `literature/extracted/` corpus was reviewed.

## Scientific question / engineering objective

Rewrite the paper from scratch around the strongest final claim supported by the full evidence:

> activation-patching comparisons in a controlled CNN setting are conditioned by channel budget, downstream architecture, output metric, spatial prior structure, and channel selection; preserving template-like weights is a distinct structural measurement rather than a guarantee of stable functional behavior.

The rewrite should be short, literature-grounded, explicit about evidential status, and difficult to attack through overclaiming.

## What was done

### Literature review

All **43 files** under `literature/extracted/` were reviewed before the rewrite. The corpus spans:

- predefined/fixed/Gabor first-layer filters;
- early CNN filter structure;
- concept-based XAI and concept alignment;
- representation-versus-influence failures;
- activation patching methodology;
- faithfulness/ablation sensitivity;
- causal abstraction and mechanistic-identifiability limits.

The literature-grounded positioning is now:

1. structured first-layer filters can be useful and can be maintained or degraded during learning;
2. representational alignment, decodability, and functional influence are distinct;
3. activation patching is conditional on intervention granularity, input construction, output metric, ablation/replacement choice, and other methodological details;
4. the paper does **not** claim generic patching sensitivity as novel.

### Manuscript rewrite

`paper/main.tex` was replaced rather than incrementally patched.

New title:

> **Activation-Patching Comparisons in Controlled CNNs Depend on Channel Budget, Architecture, and Spatial Prior Structure**

The title explicitly scopes the result to controlled CNNs rather than CNNs generally.

The main manuscript is now organized by scientific question:

1. Introduction;
2. Related work;
3. Experimental framework;
4. Results:
   - structural retention versus functional patching;
   - channel-budget and metric robustness;
   - prospective architecture heterogeneity;
   - fresh matched-anchor spatial specificity;
   - integrity/secondary evidence;
5. Discussion;
6. Limitations;
7. Conclusion;
8. Data and code availability.

Internal Stage A--G names are absent from manuscript-facing prose.

### New final evidence in the manuscript

The rewrite integrates:

- the prospective 20-block channel-budget test;
- the frozen metric robustness analysis;
- the prospectively frozen 16-architecture study;
- Greenhouse--Geisser/permutation/Friedman/random-channel post hoc architecture diagnostics;
- the fresh 25,600-model matched-anchor specificity experiment;
- the frozen equivalence interpretation for anchor specificity.

The probability-error spatial-specificity result is explicitly reported as **statistically nonzero but practically equivalent** under the frozen margin.

The negative structured-minus-pixel-permuted effect in `plain2_w16_gmp` is explicitly reported rather than hidden.

### Figures and appendices

Added:

- `paper/build_anchor_specificity_figure.py`;
- generated figure `fig07_anchor_specificity.pdf`;
- `paper/specificity_robustness_results.tex`.

The main paper now uses four principal figures:

1. renderer/templates/patching overview;
2. learned-kernel gallery;
3. channel-budget + 16-architecture robustness;
4. matched-anchor specificity + equivalence/ranking comparison.

The main text contains no result tables; complete numerical detail remains in appendices.

### Build and static checks

`paper/build.py` now regenerates `fig00`, `fig06`, and `fig07`.

Static source audit after the rewrite:

- missing bibliography keys: 0;
- unresolved cleveref labels: 0;
- duplicate labels: 0;
- raw `\ref`: 0;
- unlabeled displayed equations: 0;
- raw `\[...\]` displays: 0;
- visible internal Stage A--G names: 0.

The manuscript contains approximately 4,600 main-text words before appendices and four principal figures.

GitHub Actions successfully compiled the rewritten manuscript with the new specificity figure. The generated PDF has 25 pages including appendices. `paper/build.py` subsequently received one additional fixed LaTeX pass to stabilize long-chain cleveref references.

## Evidence or results available now

No new scientific outcomes were generated by this checkpoint.

The scientific results being integrated are documented in:

- `checkpoints/CP-010_architecture-posthoc-results.md`;
- `checkpoints/CP-011_anchor-specificity-results.md`.

This checkpoint records only manuscript synthesis, literature positioning, figure integration, and build-state changes.

## Interpretation

The final manuscript identity is no longer:

> predefined filters are interpretable or universally improve patching.

It is:

> in a controlled vision system with an explicitly structured first layer and exact matched counterfactuals, release-versus-retention activation-patching comparisons depend on channel budget and downstream architecture; the original 2D spatial prior contributes selectively to validation-selected channel behavior beyond matched bank geometry, but that contribution is architecture- and metric-dependent.

The paper should be read as a **measurement study with a structured spatial prior**, not as evidence for a unique mechanism or human-interpretable filters.

## What this does not establish

- Natural-image generalization.
- Large-CNN or transformer generalization.
- Human interpretability of the filters.
- A unique causal mechanism.
- Architecture-independent spatial-template effects.
- Practical importance of the average probability-error specificity effect.
- Novelty of generic activation-patching sensitivity to methodology.

## Repository / provenance pointers

- Manuscript: `paper/main.tex`
- Paper documentation: `paper/README.md`
- New specificity figure builder: `paper/build_anchor_specificity_figure.py`
- New specificity appendix: `paper/specificity_robustness_results.tex`
- Anchor-specificity report: `analysis/anchor_specificity_001/REPORT.md`
- Post hoc architecture report: `analysis/architecture_posthoc_diagnostics_001/REPORT.md`
- Literature corpus: `literature/extracted/`
- Bibliography: `literature/references.bib`
- Current state: `RESEARCH_STATUS.md`

## Next actions

1. Perform a new strict referee pass on the rewritten manuscript.
2. Tighten any claims or missing methodological details identified by that pass.
3. Check anonymous-artifact presentation and citation/release metadata.
4. Do not add another large experiment unless the new referee pass identifies a concrete unresolved threat that existing controls cannot address.

## Do-not-forget constraints

- Keep the probability-error anchor-specificity result described as statistically nonzero **and** practically equivalent under the frozen margin.
- Keep the `plain2_w16_gmp` sign reversal visible.
- Keep the random-channel specificity result visible; it materially constrains interpretation.
- Do not turn the paper back into a stage chronology.
- Do not equate template similarity with interpretability or influence.
- Do not call the post hoc architecture diagnostics prospective.
- The inferential unit in the two 25,600-model studies is 100 renderer blocks, not model count.
