# Stage G: Frozen fresh-sample anchor-specificity study

Protocol frozen: 2026-09-20

## Evidential status

This study is designed after the complete architecture-robustness study and after a referee-style review of the revised manuscript. The motivating concern is specific and was identified before any Stage-G outcome exists:

> the current experiments compare constant versus annealed regularization toward the same predefined bank, so the observed channel-budget and architecture dependence might reflect anchor retention/release generally rather than the spatial structure of the predefined templates.

Stage G is therefore a **prospectively frozen fresh-sample specificity experiment**. No Stage-G outcome may be inspected before this protocol is committed. The study does not redefine or replace earlier results.

Internal Stage-G naming is repository provenance only. Any manuscript-facing text should call this the **anchor-specificity experiment**.

## Scientific question

Holding fixed:

- renderer and matched counterfactual construction;
- first-layer width, kernel size, ReLU, and patching location;
- constant-versus-annealed anchor regularization schedules;
- downstream architecture;
- validation-only channel ranking;
- patch budgets;
- output metrics;
- training duration and optimizer;

does the channel-count treatment contrast depend specifically on the **spatial structure of the predefined template bank**, or does it also arise for matched/random anchors?

## Fresh sampling plan

Use:

- renderer blocks: **7000--7099** (100 fresh blocks);
- tasks: `single_shape`, `two_concepts`;
- initialization/anchor replicates per block: **4**, indexed 0--3;
- architectures:
  - `tiny_gmp`;
  - `tiny_gap`;
  - `plain2_w16_gmp`;
  - `plain2_w16_gap`;
- treatments:
  - `retention_1`;
  - `release_default`;
- anchor families: the four frozen families below;
- epochs: 200;
- batch size: 128;
- Adam learning rate: 0.003;
- no scheduler;
- no early stopping;
- final checkpoint only.

Total models:

[
100	imes 4	imes 2	imes 4	imes 2	imes 4 = 25{,}600.
]

The four architecture variants form a balanced 2 x 2 diagnostic grid:

- no downstream convolution versus one downstream convolution;
- GMP versus GAP.

This grid is chosen because it is the smallest balanced architecture family that contains the original TinyCNN/TwoLayer-form comparison and the pooling factor that was prominent in the completed architecture study. The choice is outcome-informed but frozen prospectively for Stage G.

The inferential unit is the renderer block. The four initialization/anchor replicates are averaged within block before primary inference.

## Frozen anchor families

Represent a first-layer bank as a 16 x 81 matrix after flattening each 9 x 9 filter. Every anchor row is centered and unit norm before training.

### 1. `structured_template`

The existing 16-filter edge/corner/ring bank used throughout the project.

Properties:

- 16 filters;
- centered;
- unit row norm;
- empirical rank 10.

### 2. `pixel_permuted_template`

For each block/init replicate, draw one random permutation of the 81 spatial pixel coordinates and apply **the same permutation to every row** of the structured bank.

This control exactly preserves, for that anchor realization:

- every row's multiset of weights;
- row means;
- row norms;
- all pairwise row inner products;
- the full 16 x 16 Gram matrix;
- rank;
- singular values.

It destroys the original 2D spatial arrangement of edges/corners/rings while preserving the bank's channel geometry. This is the primary structure-matched control.

The spatial permutation is shared across task, architecture, and treatment for the same block/init replicate.

### 3. `random_rank10`

Generate a random centered 10-dimensional spatial subspace in the 80-dimensional zero-mean pixel subspace. Draw 16 random coefficient vectors in that subspace, map them to 9 x 9 filters, center numerically, and normalize rows.

This produces a generic random bank with rank at most 10 and no designed edge/corner/ring geometry.

The random rank-10 bank is shared across task, architecture, and treatment for the same block/init replicate.

### 4. `random_fullrank`

Draw 16 independent Gaussian 9 x 9 filters, center each filter, and normalize rows. The bank is almost surely rank 16.

The full-rank random bank is shared across task, architecture, and treatment for the same block/init replicate.

## Pairing and seeds

Use a new seed namespace disjoint from all earlier experiments.

For each renderer block and init replicate:

- renderer data are shared across anchor families, architectures, and treatments within a task;
- downstream model initialization is paired across anchor families and treatments within architecture/task;
- the randomized anchor realization is paired across architectures, tasks, and treatments;
- minibatch order is paired across anchor families and treatments within architecture/task/init replicate.

Anchor-family labels must not be included in downstream-parameter initialization seeds. Treatment labels must not be included in downstream or anchor seeds.

## Training objective

For anchor bank (W_{mathrm{anchor}}),

[
mathcal L
=
mathcal L_{mathrm{CE}}
+
lambda(e)
rac{|W-W_{mathrm{anchor}}|_F^2}
{|W_{mathrm{anchor}}|_F^2}.
]

Treatments:

### `retention_1`

[
lambda(e)=1
]

for all 200 epochs.

### `release_default`

[
lambda(e)=
operatorname{clip}left(rac{80-e}{70},0,1ight).
]

Thus the schedule matches the completed architecture experiment exactly.

## Ranking and patching

Use the same validation-only standardized first-layer global-max activation contrast ranking as the completed architecture experiment.

Evaluate selected-channel patching at every

[
k=1,ldots,16.
]

Also evaluate eight same-size random channel orders at every k. This random-channel analysis is prespecified because the completed architecture diagnostics suggested that some architecture dependence may not require the selected-channel ranking.

Evaluate the existing validation-energy-matched controls at k in {1,2,4,8} as secondary diagnostics.

No test-set quantity may select channels.

## Primary metrics

Primary metrics:

1. centered-logit fidelity (F_{mathrm{clogit}});
2. unnormalized probability reconstruction-error reduction (R_{mathrm{prob}}).

Historical normalized probability fidelity remains a secondary bridge metric.

For metric M define

[
Delta^M_{b,s,a,h,t}(k)
=
M^{mathrm{release}}_{b,s,a,h,t}(k)
-
M^{mathrm{retention}}_{b,s,a,h,t}(k),
]

where h indexes anchor family.

Define

[
B^M_{b,s,a,h,t}
=
rac{Delta^M(4)+Delta^M(8)}2
-
rac{Delta^M(1)+Delta^M(2)}2.
]

Average four init/anchor replicates within block:

[
ar B^M_{b,a,h,t}
=
rac14sum_{s=0}^3 B^M_{b,s,a,h,t}.
]

The same definitions are applied to the mean over the eight random channel orders, yielding (B^M_{mathrm{random}}).

## Primary task

Primary task: `two_concepts`.

`single_shape` is a prespecified secondary replication/scope task.

## Primary hypothesis family A: spatial-template specificity

For each primary metric compute the block-level contrast

[
C^M_{mathrm{spatial},b}
=
rac14sum_a
left(
ar B^M_{b,a,mathrm{structured}}
-
ar B^M_{b,a,mathrm{pixelperm}}
ight).
]

This averages over the four frozen architecture variants before inference.

Report:

- mean;
- SD;
- paired 95% Student-t interval;
- paired t statistic;
- exact/Monte-Carlo two-sided sign-flip randomization p value with fixed seed and at least 100,000 permutations.

The two primary metrics form one Holm-adjusted two-test family.

Interpretation:

- near-zero (C_{mathrm{spatial}}) means the headline channel-count contrast does not require the original 2D template arrangement once bank geometry is matched;
- nonzero (C_{mathrm{spatial}}) means spatial structure changes the contrast on average across the frozen architecture grid.

This is the study's main specificity test.

## Primary hypothesis family B: spatial-structure x architecture interaction

For each primary metric form the 100 x 4 matrix

[
D^M_{b,a}
=
ar B^M_{b,a,mathrm{structured}}
-
ar B^M_{b,a,mathrm{pixelperm}}.
]

Test architecture heterogeneity in D using a within-block permutation omnibus:

- statistic: balanced repeated-measures architecture F statistic;
- null generation: independently permute the four architecture labels within each renderer block;
- fixed random seed;
- at least 100,000 permutations;
- p value calculated with the +1 correction.

The two metric p values form one Holm-adjusted family.

This tests whether any effect of spatial template structure depends on downstream architecture.

## Primary ranking-independence diagnostic

Repeat hypothesis families A and B using (B_{mathrm{random}}), where each metric is averaged over the eight random channel orders before forming B.

These are prespecified robustness diagnostics, not an additional primary family. They answer whether any anchor-specificity conclusion depends on the validation channel-ranking rule.

## Secondary anchor contrasts

For each metric/task/architecture report paired block-level contrasts:

1. structured minus pixel-permuted;
2. pixel-permuted minus random-rank10;
3. random-rank10 minus random-fullrank;
4. structured minus random-fullrank.

Use 95% paired intervals and Holm adjustment within metric, task, and contrast family.

These contrasts are decomposition aids. Only contrast 1 isolates spatial arrangement while holding the bank Gram matrix/rank/spectrum exactly fixed.

## Structural measurements

At epoch 200 report:

- similarity to the model's own anchor bank;
- similarity to the original structured template bank;
- one-to-one Hungarian matching versions of both where applicable;
- anchor bank rank and singular values before training;
- test accuracy.

The central structural quantity for all anchor families is **retention to their own anchor**, not similarity to the original templates.

## Integrity checks

Before analysis is marked complete:

- all 25,600 training jobs complete;
- all patching evaluations complete;
- no-op/full-patch identities pass frozen numerical tolerances;
- every generated anchor is centered and unit row norm;
- pixel-permuted anchors match the original template Gram matrix to numerical tolerance;
- pixel-permuted anchors have rank 10;
- random-rank10 anchors have numerical rank <=10 and target rank 10 except documented numerical failures;
- full-rank random anchors have numerical rank 16;
- anchor hashes and generation seeds are recorded;
- no model is excluded based on outcome.

## Interpretation boundary

Stage G can answer whether the project's channel-budget treatment contrast requires the designed spatial arrangement of the predefined template bank within this controlled small-CNN setting.

It cannot establish semantic interpretability, natural-image generalization, or a unique mechanism.

Crucially, either outcome is scientifically useful:

- if structured and pixel-permuted anchors behave similarly, the paper should pivot away from template-specificity and present predefined templates as a controlled case study of anchor-retention/patching measurement behavior;
- if they differ reproducibly, the paper gains direct evidence that spatial template structure contributes beyond bank rank/Gram geometry.
