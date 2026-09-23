# Terminology and Wording Guide

This file is the terminology source of truth for the paper and paper-facing documentation.

It was created after comparing the manuscript against all 43 papers in `literature/extracted/`. The goal is not to force every phrase to appear verbatim in prior work. The goal is to prefer established vocabulary when the literature already has a standard term, and to reserve new terminology for quantities that are genuinely specific to this project.

## General rule

Prefer concrete objects and operations over abstract project-internal labels.

Write about **filters, filter banks, channels, activations, interventions, evaluation metrics, network architectures, and patching effects** whenever those are the objects actually being measured.

Avoid turning implementation names, analysis-directory names, or long chains of modifiers into scientific terminology.

A term with zero occurrences in the literature corpus is not automatically bad. Project-specific quantities may need project-specific names. The important question is whether an established term already exists for the same concept.

## Corpus anchors

Observed usage in the 43-paper extracted corpus motivated the preferred vocabulary below. Counts are corpus-search counts and should be treated as orientation rather than bibliometric statistics because PDF extraction and hyphenation can affect exact totals.

| Term | Approx. corpus count | Guidance |
| --- | ---: | --- |
| activation patching | 118 | canonical name for the intervention method |
| patching effect / patching effects | 58 | preferred name for the measured effect |
| Gabor filters | 162 | prefer over abstract Gabor parameterization wording |
| spatial filters | 63 | canonical filter wording |
| network architecture | 51 | preferred architecture term |
| evaluation metric / evaluation metrics | 51 | prefer over output metric |
| filter bank | 39 | preferred for a collection of predefined filters |
| granularity | 28 | use for the level/type of patched component |
| pre-defined filters | 22 | established literature wording; manuscript house style may use `predefined` |
| intervention size | 19 | preferred for how many components are intervened on |
| learnable Gabor filters | 12 | prefer over learnable Gabor parameterizations |
| maintaining filter structure | 6 | literature-default phrasing for preserving filter structure |

## Canonical terminology

| Concept | Prefer | Avoid or use only historically | Notes |
| --- | --- | --- | --- |
| intervention method | **activation patching** | activation replacement analysis, patching procedure as a coined label | Use the standard method name. |
| measured intervention quantity | **patching effect** | functional signature, patching signature, functional influence, intervention-based functional measurement | If a metric-specific quantity is meant, name the metric explicitly. |
| number of components patched | **intervention size** | channel budget, patch budget, channel-count effect, repeatedly saying number of patched channels | At first use, define intervention size as the number (k) of first-layer channels patched. |
| type/level of patched component | **component granularity** or **patching granularity** | intervention size when the issue is channel vs. layer vs. head | Granularity and size are different concepts. |
| metric used to score an intervention | **evaluation metric** | output metric | Use metric names directly when possible. |
| architecture | **network architecture**, **CNN architecture**, **differences across architectures** | downstream architecture as a standalone concept, architecture heterogeneity as house terminology | When necessary, say “architecture after the first layer.” |
| first convolutional weights | **first-layer filters**, **spatial filters**, **filter kernels** | weight-space structure | Prefer the physical object. |
| collection of predefined filters | **filter bank**, **predefined filter bank** | anchor bank | `reference filter bank` is acceptable when contrasting several banks. |
| preserving filters during training | **maintaining filter structure**, **keeping filters close to the predefined bank** | structural retention as a general concept | `Retention` remains valid as the defined name of one training condition. |
| similarity of learned and predefined filters | **filter similarity**, **filter-template similarity** | weight-space structure, structural score when a concrete similarity score is meant | Define the exact score separately. |
| Gabor terminology | **Gabor filters**, **learnable Gabor filters**, **Gabor initialization** | learnable Gabor parameterizations | Match the filter literature. |
| architectural bias introduced by fixed/structured filters | **inductive bias** | spatial prior when used as a generic label | “Spatial prior” is acceptable only when a cited source specifically uses it. |
| semantic/causal consequence | **effect on model behavior** | functional influence | Do not infer interpretability from filter similarity. |
| source/target in patching | **source input**, **target input**, **base run**, **counterfactual run** as context requires | source of replacement activations | Follow activation-patching language. |
| counterfactual data | **matched counterfactual pairs**, **matched counterfactual image pairs** | exact matched counterfactual pairs | If exactness matters, explain what is held fixed rather than stacking adjectives. |
| channels chosen by validation data | **channels selected on the validation set** | validation-selected channels in prose | Short table headers may use “selected channels.” |
| random comparison channels | **random channel sets**, **random channel subsets** | random-channel diagnostic as a concept name | “Random-channel analysis” is acceptable when naming an analysis. |
| control that permutes spatial positions | **pixel-permuted control**, **pixel-permuted filter bank** | matched-anchor experiment, anchor-specificity experiment | Define the shared permutation once. |
| training comparison | **training conditions**, **training regimes**, **retention and release conditions** | treatment comparison when unnecessary | `Retention` and `Release` are project-defined condition names. |
| pre-analysis specification | **pre-specified** | prospectively frozen, prespecified, frozen protocol in manuscript prose | Do not call a study preregistered unless it actually was. |
| after-the-fact analysis | **post-hoc** | post hoc | Keep hyphenation consistent. |
| equivalence testing | **equivalence margin**, **equivalence test**, **TOST** | scale-relative margin, practical-effect margin | Explain how the margin was chosen. |

## Statistical wording

Prefer direct statistical statements.

| Prefer | Avoid |
| --- | --- |
| **differs from zero** | statistically nonzero |
| **the confidence interval excludes zero** | statistically distinguishable from zero when the interval is already reported |
| **the 90% interval lies within the pre-specified equivalence margin** | precisely nonzero but equivalent |
| **the 90% interval lies outside the pre-specified equivalence margin** | non-equivalent as the only explanation |
| **the same conclusion holds after Greenhouse--Geisser correction / permutation tests / Friedman tests** | the conclusion survives diagnostics |
| **differences across architectures remain** | architecture heterogeneity survives |
| **substantially smaller** | practically much smaller unless a practical threshold was actually tested |
| **supporting analysis** or the exact analysis name | diagnostic when no diagnostic property is being tested |

Use **practically equivalent** only when it is explicitly tied to the pre-specified equivalence procedure. Do not use “practically smaller/larger” as an informal intensifier.

## Preferred sentence patterns

Use these as models for future prose.

- “The patching effect depends on **intervention size**.”
- “Intervention size is the number (k) of first-layer channels patched.”
- “The difference in patching effect between **release and retention** changes with intervention size.”
- “The result also depends on **network architecture** and the **evaluation metric**.”
- “For **channels selected on the validation set**, the centered-logit difference…”
- “The **difference between the structured and pixel-permuted filter banks**…”
- “The original spatial arrangement changes the patching effect relative to the pixel-permuted control.”
- “The same conclusion holds after Greenhouse--Geisser correction, permutation tests, and Friedman tests.”
- “The 90% interval lies within the pre-specified equivalence margin.”
- “Filter similarity does not by itself determine the patching effect.”
- “Matched counterfactual pairs change one factor while holding the remaining factors fixed.”

## Avoid noun stacks

Do not convert a sequence of experimental qualifiers into one compound noun.

Avoid:

- “architecture-specific selected-channel structured-minus-pixel-permuted (B) differences”
- “release-minus-retention base-to-counterfactual error scales”
- “probability input-effect-scale contrast”
- “selected-channel centered-logit structured-minus-pixel-permuted effect”

Prefer full clauses:

- “the difference in (B) between the structured and pixel-permuted filter banks for channels selected on the validation set, shown separately for each architecture”
- “the difference between release and retention in the base-to-counterfactual error denominator”
- “the centered-logit difference between the two filter banks”

As a practical rule, if a noun has more than about three stacked modifiers, rewrite it as a clause.

## Project-specific terms that are allowed

The following are intentionally project-specific and should not be replaced merely because they are absent from the literature corpus:

- **renderer block** — the independent generated-data unit used for inference; define once.
- **Retention** — the training condition that maintains the regularization penalty.
- **Release** — the training condition that anneals the penalty to zero.
- **centered-logit fidelity** — a project-defined evaluation metric; define mathematically.
- **probability error reduction** — a project-defined evaluation metric; define mathematically.
- **pixel-permuted control** — the project-defined filter-bank control; define the common spatial permutation.
- (B) — the pre-specified intervention-size contrast; always explain the (k=1,2) versus (k=4,8) definition.

Names of historical directories, checkpoints, labels, and analysis folders may retain older terminology for provenance. Do not copy those names into new manuscript prose.

## Terms to avoid in new paper-facing prose

Do not introduce these unless quoting or describing historical project artifacts:

- channel budget
- patch budget
- spatial prior structure
- functional signature
- patching signature
- functional concentration
- functional influence
- weight-space structure
- matched-anchor experiment
- anchor-specificity experiment
- fresh-sample study
- prospectively frozen
- architecture heterogeneity
- conditioning variable
- scale-relative margin
- historical effect scale
- downstream architecture as a named concept
- output metric
- validation-selected channels
- exact matched counterfactual pairs
- statistically nonzero
- practically much smaller
- input-effect-scale contrast
- structured-minus-pixel-permuted as a long compound modifier

## Maintenance

Before introducing a new recurring term into the manuscript:

1. Check this guide first.
2. If the concept already has a preferred term here, use it.
3. If the concept is genuinely new and project-specific, define it once in plain language.
4. If it may overlap with an established literature term, search `literature/extracted/` before coining a label.
5. Add any new approved terminology to this file so future revisions remain consistent.

The manuscript should sound like the literature, not like the names of the project’s scripts, stages, checkpoints, or analysis folders.
