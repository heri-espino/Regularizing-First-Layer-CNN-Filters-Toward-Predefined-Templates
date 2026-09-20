# Manuscript revision plan after Stage F

Status: planned revision only.  
Do not execute the outcome-dependent parts of this plan until the frozen Stage-F evaluation and analysis are complete.

The current `paper/main.tex` is intentionally retained as a pre-Stage-F snapshot.

## 1. Revision objective

The final manuscript should no longer read primarily as a chronological accumulation of experiments. The experimental history is important for provenance, but the main paper should present a compact scientific argument:

1. structured first-layer regularization strongly preserves predefined filter structure;
2. structural similarity and activation-patching behavior are not interchangeable;
3. the release-versus-retention patching comparison depends on the number of patched channels;
4. the TinyCNN result survives a prospective fresh-block test;
5. the result survives alternative output metrics, including an unnormalized metric;
6. downstream architecture changes the comparison, with Stage F prospectively mapping that heterogeneity.

The paper should emphasize **measurement behavior and scope**, not universal mechanistic claims.

## 2. Title

Current title:

> Regularizing First-Layer CNN Filters Toward Predefined Templates: Activation-Patching Comparisons Vary with the Number of Patched Channels

Do not choose a new title until Stage F is complete.

Potential direction if Stage F shows substantial architecture heterogeneity:

> Regularizing First-Layer CNN Filters Toward Predefined Templates: Activation-Patching Comparisons Depend on Channel Count and Architecture

Potential direction if one architecture factor, such as pooling, clearly organizes the result:

> Template-Regularized CNNs Reveal Architecture-Dependent Activation-Patching Effects Across Channel Budgets

These are placeholders, not commitments.

## 3. Abstract

The current abstract is too centered on the historical probability-space Stage-D result and does not yet contain the metric audit or Stage F.

Final abstract should contain, in order:

1. problem: template-like filters are structural objects; activation patching is a functional measurement;
2. intervention: constant retention versus annealed release of the same first-layer template prior;
3. Stage-D prospective result in TinyCNN;
4. metric robustness: centered-logit and unnormalized probability-error results;
5. Stage-F architecture finding;
6. interpretation boundary.

Reduce or remove detailed discussion of the historical selected-minus-random (k=4) decomposition from the abstract unless space remains. That decomposition matters methodologically but is no longer the central headline.

Do not report 25,600 as if model count itself were inferential strength. If model count is mentioned, immediately state that inference uses renderer blocks.

## 4. Introduction

### Keep

- motivation for predefined/structured first-layer filters;
- distinction between weight-space similarity and activation-space intervention behavior;
- controlled synthetic counterfactual rationale;
- caution that patching is an intervention measurement, not proof of a unique causal mechanism.

### Change

The current introduction says the contribution is shown “under fixed counterfactual construction, output metric, intervention layer, and primary channel ranking.” After the metric audit, “fixed output metric” is no longer the strongest framing.

Replace that idea with:

> the channel-count dependence persists under multiple output-space definitions, while architecture changes its magnitude and sometimes its direction.

The novelty paragraph must explicitly avoid claiming that patching granularity sensitivity itself is new. Position the contribution as connecting structured first-layer priors to known measurement-sensitivity concerns in mechanistic interventions.

## 5. Related work

Retain two main strands:

### A. Predefined and structured convolutional filters

Use terminology already established in the literature:

- predefined filters;
- spatial filters;
- filter initialization;
- filter similarity;
- maintaining filter structure;
- filter kernels;
- learnable Gabor filters.

Do not convert weight similarity into an interpretability claim.

### B. Activation patching and intervention sensitivity

Make clear that prior work has already shown sensitivity to:

- corruption/intervention construction;
- output metric;
- granularity;
- ablation method.

The paper's contribution is not “patching metrics can be sensitive.” It is the controlled interaction between a structured training prior, patch-channel budget, and architecture while the intervention layer and counterfactual construction are held fixed.

## 6. Methods restructuring

The methods should include a compact experimental roadmap that extends through the metric audit and Stage F.

Recommended roles:

- A/B: development and structural/longitudinal evidence;
- C: post hoc measurement decomposition;
- D: prespecified prospective test;
- E: prespecified secondary robustness map;
- metric audit: frozen post hoc metric robustness;
- F: prospectively frozen architecture robustness;
- checkpoint audit: independent implementation verification.

Use “prespecified prospective test/follow-up” in narrative prose for Stage D. Historical files with “confirmation” remain untouched.

### Add explicit metric subsection

Define:

1. historical normalized probability fidelity (F_{prob});
2. centered-logit fidelity (F_{clogit});
3. absolute probability reconstruction-error reduction (R_{prob}).

Explain why centered logits remove the irrelevant common-logit offset.

Explicitly state that (F_{prob})'s denominator differs by model and that the metric audit found treatment-dependent denominator changes.

### Add Stage-F design

Describe:

- 100 fresh blocks;
- 4 initialization replicates averaged within block;
- 16 architectures;
- 2 tasks;
- 2 treatments;
- fixed first-layer intervention tensor;
- primary two-concepts task;
- two primary metrics;
- repeated-measures architecture omnibus;
- fresh Tiny-vs-plain2 bridge;
- factor contrasts.

Avoid using “25,600 independent models” as a statistical sample-size statement.

## 7. Results restructuring

Recommended main-text results order:

### Result 1 — template retention changes weights

Show that constant template regularization strongly preserves template similarity.

Keep predictive performance/context as secondary.

### Result 2 — patching comparison depends on channel count

Present the Stage-D prospective TinyCNN result:

[
B=0.330976,quad 95\% CI=[0.273680,0.388273].
]

Show the pointwise (k=1,2,4,8) curve so readers see that positive (B) does not mean release is better at every larger k.

### Result 3 — the original metric normalization matters, but does not explain away TinyCNN

Present the metric audit immediately after Stage D.

Key facts:

- denominator/input-effect scale differs strongly between treatments;
- centered-logit (B=0.178881);
- unnormalized probability-error-reduction (B=0.894411);
- both intervals are positive in the frozen Stage-D primary setting.

This should replace any implication that the historical normalized probability metric is uniquely privileged.

### Result 4 — architecture conditions the phenomenon

This becomes the Stage-F centerpiece.

First report:

1. primary architecture omnibus for centered-logit fidelity;
2. primary architecture omnibus for probability error reduction;
3. fresh bridge contrast between `tiny_gmp` and `plain2_w16_gmp`.

Then report architecture-factor contrasts.

Do not lead with the most visually dramatic secondary architecture.

### Result 5 — broader sensitivity map

Use Stage E more compactly after Stage F, as evidence that the historical two-architecture difference already appeared across tasks/schedules.

The full six-profile map belongs mainly in appendix/supplement.

### Result 6 — controls and audit

Random/energy-matched decomposition and checkpoint audit can be concise in the main text, with details in appendices.

## 8. Stage-F outcome branches

The manuscript must adapt to the actual frozen results rather than forcing one story.

### Branch A: strong architecture heterogeneity

If the omnibus tests show substantial heterogeneity across architectures:

Main claim:

> the training-intervention comparison is not architecture invariant.

Then identify which prespecified factors account for the largest paired differences.

Do not call the largest factor “the mechanism.” Say it is an architectural correlate or candidate explanation within the tested family.

### Branch B: pooling is the dominant factor

If GAP-vs-GMP contrasts are consistently large:

Frame this as evidence that downstream spatial aggregation strongly conditions how first-layer channel replacement propagates to outputs.

This is scientifically attractive because all models share the exact patched first-layer tensor.

Still avoid claiming pooling is the unique mechanism.

### Branch C: depth/width/connectivity dominate

Use the corresponding controlled matched contrasts.

Do not interpret the historical TinyCNN/TwoLayerCNN difference as pure depth if width/normalization/connectivity show interactions.

### Branch D: TinyCNN-like effect is broadly stable

If many architectures show positive (B) under both primary metrics, the paper can strengthen the scope from “TinyCNN-specific” to “observed across a broader controlled small-CNN family.”

Do not extrapolate to natural images or larger architectures.

### Branch E: primary metrics disagree

If centered-logit fidelity and absolute probability error reduction lead to materially different architecture maps:

Make **metric dependence itself** part of the central result.

Do not average the metrics or select the one that best matches the earlier narrative.

### Branch F: little architecture heterogeneity

If the omnibus is weak and bridge contrast is small in fresh data:

Report that Stage E's apparent architecture difference did not generalize strongly under the broader fresh-sample design.

The paper still retains the robust channel-count and metric-sensitivity findings.

This would narrow, not invalidate, the contribution.

## 9. Interpretation/discussion

The discussion should distinguish three layers:

### Structural

Constant regularization preserves predefined first-layer filters.

### Functional measurement

Activation patching measures how replacing a chosen activation subset changes counterfactual output reconstruction.

### Architecture

Downstream computation determines how the same first-layer intervention propagates.

The central conceptual point should be that a stable structural representation does not imply a stable intervention-based functional comparison.

### Denominator caveat

The original (F_{prob}) normalization must be discussed explicitly. Do not bury the metric audit in an appendix.

Correct framing:

> model-specific normalization differs across treatments, but the principal TinyCNN channel-count contrast persists under centered-logit and unnormalized probability-space measures.

## 10. Figures

Target a small number of high-information main figures.

### Figure 1 — experimental schematic

Show:

- template bank;
- retention vs release;
- first-layer patch point;
- base/counterfactual pair;
- multiple k values.

### Figure 2 — structural vs functional separation

Combine:

- template-similarity retention effect;
- representative patch-budget curves.

### Figure 3 — metric robustness

Show Stage-D release-minus-retention curves under:

- historical probability fidelity;
- centered-logit fidelity;
- absolute probability error reduction.

Because scales differ, use separate panels/axes rather than forcing a shared y-axis.

### Figure 4 — Stage-F architecture map

Preferred form depends on results.

Possible designs:

- architecture-by-metric forest plot of (B);
- paired GMP/GAP architecture families;
- factor-contrast forest plot.

Avoid a giant unreadable 16 x many-metric table in the main paper.

### Appendix figures

Move:

- full k=1..16 curves for every architecture;
- all schedule profiles;
- all rankings;
- control matching diagnostics;
- initialization dispersion.

## 11. Tables

Main tables should be minimal.

Recommended:

1. compact experiment/evidential-role roadmap;
2. Stage-D + metric-audit primary estimates;
3. Stage-F primary omnibus/bridge summary.

Architecture-factor contrasts can be an appendix table unless one factor is central enough for the main text.

## 12. Statistical language

Always state the inferential unit.

Examples:

- Stage D: 20 independent renderer blocks.
- Stage E: 50 independent renderer blocks per setting.
- Stage F: 100 independent renderer blocks after averaging 4 initialization replicates.

Do not write “25,600 independent models.”

Use effect estimates and confidence intervals as the primary language. P values support the frozen tests but are not binary scientific verdicts.

Stage-F repeated-measures architecture tests should be reported as frozen omnibus tests, followed by the prespecified factor contrasts.

## 13. Terminology and claim discipline

Prefer:

- patching effect;
- number of patched channels;
- channel count;
- counterfactual reconstruction;
- template similarity;
- constant template regularization;
- annealed template regularization.

Avoid:

- “causal importance” without qualification;
- “mediated fraction”;
- “interpretable filter” as an empirical conclusion;
- “patch size” when “number of patched channels” is clearer;
- generic “confirmation” language for Stage D in new prose.

## 14. What should be cut or demoted

The paper has accumulated a large research history. Do not put every experiment in the main narrative.

Demote to appendix/supplement:

- most Stage-A companion outcomes;
- most Stage-B trajectories;
- all alternative Stage-C rankings in full detail;
- exhaustive Stage-E schedule tables;
- energy-matching implementation details;
- block-level values;
- audit debugging history.

Keep them in the repository for reproducibility.

## 15. What not to add after Stage F

Do not automatically create Stage G/H/I.

After Stage F, additional experiments should require a specific manuscript-level reason, such as:

- a fatal confound revealed by Stage F;
- a reviewer-critical integrity problem;
- an implementation inconsistency.

“More evidence would look stronger” is not sufficient.

The main remaining work should be:

- synthesis;
- figure design;
- literature positioning;
- manuscript compression;
- strict claim auditing.

## 16. Final paper objective

The final manuscript should leave a reader with one clear message:

> A first-layer template prior can strongly stabilize filter structure without producing a simple, architecture-independent activation-patching signature. The measured release-versus-retention functional difference depends on intervention granularity, survives alternative output metrics in TinyCNN, and must be interpreted together with downstream architecture.

The exact architecture clause must be updated from the frozen Stage-F results rather than predicted in advance.
