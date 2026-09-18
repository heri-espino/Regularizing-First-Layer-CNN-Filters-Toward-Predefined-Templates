# Stage F: Frozen fresh-sample architecture robustness study

Protocol frozen: 2026-09-18

## Evidential status

Stage F is designed after Stages D and E and after the frozen checkpoint-only metric-sensitivity analysis were completed and inspected. Those earlier results showed that the channel-count contrast is strong for TinyCNN across probability, centered-logit, and unnormalized probability-error metrics, while the corresponding effect is much weaker or changes sign in TwoLayerCNN. Stage F therefore targets **architecture dependence** directly.

This is a **prospectively frozen fresh-sample architecture robustness study**. It uses renderer blocks and model-initialization replicates not used in Stages A--E. No Stage-F outcome may be inspected before this protocol is committed. The study does not redefine any earlier stage.

The study is deliberately computationally large because compute cost is not a binding constraint. Its purpose is not to maximize model count for its own sake, but to separate architecture factors that were confounded in the original TinyCNN versus TwoLayerCNN comparison.

## Scientific question

Holding fixed:

- the synthetic tasks and counterfactual construction;
- the 16-channel, 9x9 first convolution;
- the 16 predefined first-layer templates;
- the first-layer intervention point;
- the template-retention versus template-release training contrast;
- the validation-only channel-ranking rule;
- the patch budgets;
- and the output metrics,

how does downstream CNN architecture change the release-versus-retention activation-patching contrast as the number of patched first-layer channels increases?

## Fresh sampling plan

Stage F uses:

- tasks: `single_shape`, `two_concepts`;
- renderer blocks: **6000--6099** (100 fresh blocks);
- initialization replicates per renderer block: **4**, indexed 0--3;
- treatments: `retention_1` and `release_default`;
- architectures: the 16 frozen variants below;
- epochs: 200;
- batch size: 128;
- Adam learning rate: 0.003;
- no scheduler;
- no early stopping;
- final checkpoint only.

The total planned number of trained models is

[
100\times4\times2\times2\times16
=
25{,}600.
]

The four initialization replicates share the same renderer data within a block but use distinct downstream initialization and minibatch-order streams. The same initialization replicate is paired across the two treatments.

The inferential unit is the **renderer block**, not the individual image, matched pair, model, or initialization replicate. Initialization replicates are averaged within renderer block before primary inference.

## Fixed first layer and intervention point

Every architecture begins with exactly

[
\operatorname{Conv2d}(1,16,9\times9,\mathrm{padding}=4,\mathrm{bias}=\mathrm{False})
]

followed by ReLU. This tensor is the Stage-F patching intervention point.

The first-layer bank is initialized to the same 16 centered unit-norm edge/corner/ring templates used in the earlier stages. No architecture changes the number of first-layer channels, kernel size, first-layer activation, or intervention location.

Consequently the intervention budget always has the same meaning:

[
k=1,\ldots,16
]

patched first-layer channels.

Batch normalization, when present, occurs **only downstream** of the first-layer intervention tensor.

## Frozen architecture grid

Pooling is global max pooling (GMP) or global average pooling (GAP).

| ID | Total conv depth | Downstream width | Connectivity | Downstream normalization | Pool |
|---|---:|---:|---|---|---|
| `tiny_gmp` | 1 | 16 | none | none | GMP |
| `tiny_gap` | 1 | 16 | none | none | GAP |
| `plain2_w16_gmp` | 2 | 16 | plain | none | GMP |
| `plain2_w16_gap` | 2 | 16 | plain | none | GAP |
| `plain4_w16_gmp` | 4 | 16 | plain | none | GMP |
| `plain4_w16_gap` | 4 | 16 | plain | none | GAP |
| `plain2_w64_gmp` | 2 | 64 | plain | none | GMP |
| `plain2_w64_gap` | 2 | 64 | plain | none | GAP |
| `plain4_w64_gmp` | 4 | 64 | plain | none | GMP |
| `plain4_w64_gap` | 4 | 64 | plain | none | GAP |
| `res4_w16_gmp` | 4 | 16 | residual | none | GMP |
| `res4_w16_gap` | 4 | 16 | residual | none | GAP |
| `bn2_w16_gmp` | 2 | 16 | plain | BatchNorm after downstream conv | GMP |
| `bn2_w16_gap` | 2 | 16 | plain | BatchNorm after downstream conv | GAP |
| `bn4_w16_gmp` | 4 | 16 | plain | BatchNorm after each downstream conv | GMP |
| `bn4_w16_gap` | 4 | 16 | plain | BatchNorm after each downstream conv | GAP |

For plain depth-4 networks, the downstream path contains three 3x3 convolutions after the fixed first layer. Width-64 variants use 16->64 on the first downstream convolution and 64->64 thereafter.

For residual depth-4 networks, all downstream tensors remain width 16. The third downstream convolution is added to the original first-layer activation tensor before the final ReLU, providing one residual skip while preserving total convolution depth 4.

The classifier is a learned linear map from the pooled downstream width to four classes, matching the role of the classifier in the earlier networks.

## Frozen treatments

Both treatments begin from the predefined first-layer template bank.

### `retention_1`

Constant template regularization:

[
\lambda(e)=1
]

for all 200 epochs.

### `release_default`

Linear release matching the Stage-E default schedule:

[
\lambda(e)=
\operatorname{clip}\left(\frac{80-e}{80-10},0,1\right).
]

Thus regularization begins to release at epoch 10 and reaches zero by epoch 80.

No additional training profile is introduced in Stage F.

## Randomness and pairing

Renderer data depend on task and renderer block exactly as in the existing renderer.

Model initialization uses a Stage-F seed namespace containing:

- master seed;
- renderer block;
- task;
- architecture ID;
- initialization replicate.

The treatment identifier is intentionally **not** part of the initialization seed, so paired retention/release runs begin with identical downstream random parameters for the same block/task/architecture/init replicate.

The minibatch-order generator also uses a Stage-F namespace and the same paired structure.

## Fixed validation-only channel ranking

Stage F uses one ranking rule only: the existing standardized validation activation contrast ranking.

For each concept and first-layer channel, compute the standardized difference in pooled first-layer activation between concept-positive and concept-negative validation examples, rank channels by absolute effect, and freeze that ranking before test patching.

No test-set quantity, Stage-F patching outcome, or alternative metric is used to select channels.

Using one ranking rule is intentional: Stages D/E already studied ranking sensitivity, while Stage F isolates architecture.

## Patching procedure

For every matched base/counterfactual test pair:

1. compute the first-layer activation tensor;
2. replace the selected first-layer channel maps of the base example with the corresponding maps from its matched counterfactual;
3. pass the patched tensor through the architecture-specific downstream network and classifier.

Evaluate all budgets

[
k=1,2,\ldots,16.
]

Full-patch and no-op identities must satisfy the existing numerical tolerances.

## Primary output metrics

Stage F carries forward the two primary metrics from the frozen metric-sensitivity study.

### 1. Centered-logit fidelity

[
F_{\mathrm{clogit}}(S)
=
1-
\frac{\sum\|\widetilde\ell_S-\widetilde\ell_1\|_2^2}
     {\sum\|\widetilde\ell_1-\widetilde\ell_0\|_2^2}.
]

### 2. Absolute probability reconstruction-error reduction

[
R_{\mathrm{prob}}(S)
=
\frac1N\sum\|p_0-p_1\|_2^2
-
\frac1N\sum\|p_S-p_1\|_2^2.
]

The original normalized probability fidelity

[
F_{\mathrm{prob}}(S)
=
1-
\frac{\sum\|p_S-p_1\|_2^2}
     {\sum\|p_1-p_0\|_2^2}
]

is retained as a prespecified secondary bridge metric.

Also retain raw-logit fidelity, centered/raw-logit absolute error reductions, counterfactual-target accuracy, agreement with the actual counterfactual prediction, classification accuracy, first-layer template alignment, and model-level base-to-counterfactual error scales.

No metric is dropped after results are seen.

## Controls

For the frozen contrast ranking:

- eight same-size random channel-order controls are evaluated at every k=1,...,16;
- eight validation-replacement-energy-matched channel subsets are evaluated at k in {1,2,4,8}.

Control construction uses validation activations only.

Selected-minus-random and selected-minus-energy-matched differences are retained as secondary diagnostics. The Stage-F primary architecture analysis is defined on the selected-channel metrics above.

## Per-model treatment contrast

For metric M, architecture a, task t, renderer block b, initialization replicate s, and budget k,

[
\Delta^M_{b,s,a,t}(k)
=
M^{\mathrm{release}}_{b,s,a,t}(k)
-
M^{\mathrm{retention}}_{b,s,a,t}(k).
]

Define

[
B^M_{b,s,a,t}
=
\frac{\Delta^M(4)+\Delta^M(8)}{2}
-
\frac{\Delta^M(1)+\Delta^M(2)}{2}.
]

Average the four initialization replicates within renderer block:

[
\bar B^M_{b,a,t}
=
\frac14\sum_{s=0}^{3}B^M_{b,s,a,t}.
]

All primary inference uses the 100 values (ar B^M_{b,a,t}) for each architecture/task/metric.

The same averaging rule is applied to pointwise (Delta(k)) curves.

## Primary Stage-F analysis

The primary task is `two_concepts`. The two primary metrics are:

- centered-logit fidelity;
- absolute probability error reduction.

### A. Omnibus architecture heterogeneity

For each primary metric separately, test whether mean (ar B) differs across the 16 architectures using a one-factor repeated-measures ANOVA with renderer block as the repeated unit.

The two omnibus p-values form one Holm-adjusted two-test family.

This is the primary Stage-F test of architecture dependence.

### B. Fresh-sample bridge contrast

The prespecified bridge compares the two original architectural forms under GMP:

[
C^M_{\mathrm{bridge},b}
=
\bar B^M_{b,\mathrm{tiny\_gmp}}
-
\bar B^M_{b,\mathrm{plain2\_w16\_gmp}}.
]

Report its mean, SD, 95% paired Student-t interval, t statistic, and two-sided p value for each primary metric.

The two bridge p-values form a separate Holm-adjusted two-test family.

This bridge is a fresh-sample test of the architecture difference that motivated Stage F; it does not retroactively make earlier architecture observations prospective.

## Prespecified architecture-factor contrasts

For both tasks and each metric, report paired block-level contrasts with 95% intervals. P values are two-sided and Holm-adjusted **within metric, task, and factor family**.

### Pooling family

GAP minus GMP within each of the eight matched backbone families:

- tiny;
- plain2 width16;
- plain4 width16;
- plain2 width64;
- plain4 width64;
- residual4 width16;
- BN2 width16;
- BN4 width16.

### Depth family

At width16, no BN, plain connectivity:

- plain2 minus tiny, separately for GMP and GAP;
- plain4 minus plain2, separately for GMP and GAP.

### Width family

Plain connectivity, no BN:

- width64 minus width16 at depth2, separately for GMP and GAP;
- width64 minus width16 at depth4, separately for GMP and GAP.

### Residual family

At depth4/width16:

- residual minus plain, separately for GMP and GAP.

### Batch-normalization family

At width16:

- BN2 minus plain2, separately for GMP and GAP;
- BN4 minus plain4, separately for GMP and GAP.

These contrasts are descriptive/mechanistic decomposition of architecture heterogeneity; they do not replace the primary omnibus test.

## Secondary analyses

Secondary analyses include:

- `single_shape` using the identical architecture analysis;
- original probability fidelity;
- all full k=1,...,16 treatment-difference curves;
- initialization-replicate dispersion within block;
- selected-minus-random controls;
- selected-minus-energy-matched controls;
- input-effect denominator differences;
- classification accuracy and template-alignment summaries.

No image pair is treated as an inferential replicate.

## Repeated-measures ANOVA definition

For a matrix (Y_{b,a}) containing one block-averaged B value for each renderer block b and architecture a, the frozen omnibus statistic uses the standard balanced one-factor repeated-measures decomposition:

- architecture sum of squares from architecture means;
- renderer-block sum of squares from block means;
- residual sum of squares after removing grand, architecture, and block effects;
- df_architecture = A-1;
- df_error = (A-1)(N-1).

The F statistic is

[
F
=
\frac{SS_{architecture}/(A-1)}
     {SS_{error}/((A-1)(N-1))}.
]

The corresponding upper-tail F-distribution p value is reported.

Effect estimates and intervals remain primary for interpretation; statistical significance is not used as a binary scientific verdict.

## Integrity and inclusion rules

- All 25,600 planned training jobs must complete before the primary analysis is marked complete.
- No model is excluded based on training accuracy, patching magnitude, alignment, denominator size, or whether it supports the earlier result.
- Numerical failures abort the affected run and must be documented; they are not silently removed.
- Undefined normalized metrics remain undefined when their denominator is below 1e-10.
- Full-patch and no-op identities are checked for every evaluated model.
- Renderer data hashes, model checkpoint hashes, source provenance, environment information, and frozen design manifests are retained.
- Training and evaluation are resumable only under an identical frozen design.
- No architecture, block, seed, metric, budget, ranking, or contrast may be removed after outcomes are inspected.

## Interpretation boundary

Stage F can establish whether the observed patch-budget treatment contrast is stable or heterogeneous across a substantially broader **controlled small-CNN architecture family** while preserving the same first-layer intervention space.

It does not establish natural-image generalization, transformer generalization, human interpretability, or a unique causal mechanism. Architecture-factor contrasts are controlled within this synthetic renderer and training setup and should not be generalized beyond that scope without further evidence.
