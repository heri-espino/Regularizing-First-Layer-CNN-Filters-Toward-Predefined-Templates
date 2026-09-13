# Main manuscript status

Editable submission manuscript: [`main.tex`](main.tex). Historical Markdown sources are not automatically synchronized with the LaTeX manuscript. Stage-D and Stage-E numerical appendices are in [`confirmation_robustness_results.tex`](confirmation_robustness_results.tex); earlier Stage A--C numerical appendices remain in [`supplementary_results.tex`](supplementary_results.tex); and [`kernel_matching_results.tex`](kernel_matching_results.tex) retains the complete endpoint matching table because its visual summaries were promoted to the main Results section.

## Current title

**Template Priors in Small CNNs: Activation-Patching Effects Depend on the Number of Patched Channels**

## Terminology policy

The final language pass removes paper-specific labels where established or direct wording is available.

- `activation patching` is used for the intervention procedure.
- `selected-channel fidelity` is retained because it is explicitly defined by the paper's equation.
- `number of patched channels` or `patch size` is used instead of `intervention budget`.
- The primary statistic is called the **predeclared contrast `B`** rather than an `intervention-budget contrast`.
- `kernel-template similarity` or `alignment` is used instead of `weight morphology` where possible.
- Stage E is described as a **secondary sensitivity study** rather than a `robustness map`.
- `U_random` is described as a selected-versus-random fidelity difference rather than `relative usefulness` or `causal usefulness`.

The copyedit also removes rhetorical constructions such as `the headline is not X; it is Y`, numbered `threefold` contribution prose, and similar claim-marketing language. Established technical terms such as activation patching, AUROC, IoU, Holm adjustment, one-to-one assignment, causal identifiability, and counterfactual accuracy are unchanged.

## Current scientific status

- **Stage A:** 400-model alignment/control experiment. Persistent retention strongly increases template alignment, but the four locally prospective `U` tests do not survive Holm correction.
- **Stage B:** 200-model, 200-epoch retention/release experiment. Template initialization does not uniformly accelerate learning; release reduces alignment and improves compositional accuracy relative to constant retention.
- **Stage C:** post hoc 80-checkpoint measurement analysis. Decomposition shows that the positive TinyCNN `k=4` release effect in `U_random` is partly explained by the random-channel baseline. Selected fidelity is strongly negative at small patch sizes, near zero/slightly negative at `k=4`, and slightly positive at `k=8`.
- **Stage D:** frozen prospective confirmation on 80 newly trained models from blocks 4000--4019. The single primary `two_concepts / TinyCNN / contrast` predeclared contrast is **CONFIRMED**: mean `B=+0.330976`, 95% CI `[+0.273680,+0.388273]`, `p=2.2819e-10` over 20 previously unused blocks.
- **Stage E:** separately frozen 1,200-model secondary sensitivity study on blocks 5000--5049. The default-release value of `B` is positive for TinyCNN on both tasks (`+0.07189` single_shape; `+0.28619` two_concepts), but not for TwoLayerCNN (`-0.01018` and `-0.04156`, respectively). Full `k=1..16` curves and all six prior profiles are retained.
- **Independent checkpoint audit:** 32/32 fixed Stage-B checkpoint evaluations completed and passed all frozen tolerances after correcting an audit-only first-layer selection bug. Maximum selected-fidelity discrepancy is `2.39e-7`; full/no-op probability errors are zero.

## Current claim

Within the tested small-CNN setting, persistent template retention produces high first-layer kernel-template similarity, while the release-minus-retention difference measured by activation patching changes with the number of patched channels and differs between TinyCNN and TwoLayerCNN. The paper does not claim a unique mechanism, human interpretability, or generalization to natural images.

## Results layout

The main evidence is visible in the paper rather than being carried by the appendices. The Stage-E architecture comparison and full selected-fidelity curves are in the main Results section. The one-to-one matching trajectories, fixed-block kernel/template similarity matrices, and matched kernel gallery are also in the main text. The appendices retain complete numerical breakdowns and the endpoint matching table.

## Build and visual validation

GitHub Actions `paper-compile` run `34751929284` completed successfully for commit `62de14fb4a9f39b7663b50cf9fd9bacb8e09532b`. The manuscript is 19 pages. The compile log contains no overfull boxes, undefined references, or LaTeX warnings requiring correction; only non-clipping underfull spacing warnings remain.

The compiled PDF was rendered and inspected after the terminology pass. The new title fits the TMLR title block, the abstract remains on the first page, tables and figures are readable, and the appendices contain no clipped or overlapping content.

## Remaining submission preparation

The experiments, prospective confirmation, implementation audit, language pass, compile check, and visual inspection are complete. Remaining work is submission packaging and human/coauthor review. The current public working repository should not be linked from the anonymous manuscript because it identifies the authors.
