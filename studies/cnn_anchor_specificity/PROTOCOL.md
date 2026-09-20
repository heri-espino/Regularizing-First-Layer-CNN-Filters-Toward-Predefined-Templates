# Stage G: Frozen fresh-sample anchor-specificity study

Protocol frozen: 2026-09-20

## Evidential status

This study was designed after the completed architecture-robustness study and after a referee-style review of the revised manuscript. The motivating concern was identified before any full Stage-G scientific outcome existed:

> the existing experiments compare constant versus annealed regularization toward the same predefined bank, so the observed channel-budget and architecture dependence might reflect anchor retention/release generally rather than the spatial structure of the predefined templates.

Stage G is therefore a **prospectively frozen fresh-sample specificity experiment**. It does not redefine or replace earlier results.

Internal Stage-G naming is repository provenance only. Manuscript-facing text should call this the **anchor-specificity experiment**.

Implementation-only smoke tests are permitted before the full run. They may verify execution, numerical identities, and anchor invariants, but their scientific outcomes must not be used to redesign the experiment.

## Scientific question

Holding fixed:

- renderer and matched counterfactual construction;
- first-layer width, kernel size, ReLU, and patching location;
- constant-versus-annealed anchor-regularization schedules;
- downstream architecture;
- validation-only channel ranking;
- patch budgets;
- output metrics;
- training duration and optimizer;

does the channel-count treatment contrast depend specifically on the **spatial structure of the predefined template bank**, or does it also arise for matched/random anchors?

## Fresh sampling plan

Use:

- renderer blocks: **7000--7099** (100 fresh blocks);
- tasks: **single_shape**, **two_concepts**;
- initialization/anchor replicates per block: **4**, indexed 0--3;
- architectures:
  - **tiny_gmp**;
  - **tiny_gap**;
  - **plain2_w16_gmp**;
  - **plain2_w16_gap**;
- treatments:
  - **retention_1**;
  - **release_default**;
- anchor families: the four frozen families below;
- epochs: 200;
- batch size: 128;
- Adam learning rate: 0.003;
- no scheduler;
- no early stopping;
- final checkpoint only.

Total models:

\[
100\times4\times2\times4\times2\times4=25{,}600.
\]

The four architectures form a balanced \(2\times2\) diagnostic grid:

- no downstream convolution versus one downstream convolution;
- GMP versus GAP.

This is the smallest balanced architecture family containing the original TinyCNN/TwoLayer-form comparison and the pooling factor that was prominent in the completed architecture study. The choice is outcome-informed from the completed architecture study but is frozen prospectively for this fresh anchor-specificity experiment.

The inferential unit is the **renderer block**. The four initialization/anchor replicates are averaged within block before primary inference.

## Frozen anchor families

Represent a first-layer bank as a \(16\times81\) matrix after flattening each \(9\times9\) filter. Every anchor row is centered and unit norm before training.

### 1. structured_template

The existing 16-filter edge/corner/ring bank used throughout the project.

Properties:

- 16 filters;
- centered;
- unit row norm;
- numerical rank 10 under the frozen float32-safe rank tolerance.

### 2. pixel_permuted_template

For each block/init replicate, draw one random permutation of the 81 spatial pixel coordinates and apply **the same permutation to every row** of the structured bank.

This control exactly preserves, up to floating-point tolerance:

- every row's multiset of weights;
- row means;
- row norms;
- all pairwise row inner products;
- the complete \(16\times16\) Gram matrix;
- rank;
- singular spectrum.

It destroys the original 2D spatial arrangement of edges/corners/rings while preserving the bank's channel geometry. This is the primary structure-matched control.

The spatial permutation is shared across task, architecture, and treatment for the same block/init replicate.

### 3. random_rank10

Generate a random centered 10-dimensional spatial subspace in the 80-dimensional zero-mean pixel subspace. Draw 16 random coefficient vectors in that subspace, map them to \(9\times9\) filters, center numerically, and normalize rows.

This produces a generic random rank-10 bank with no designed edge/corner/ring geometry.

The random rank-10 bank is shared across task, architecture, and treatment for the same block/init replicate.

### 4. random_fullrank

Draw 16 independent Gaussian \(9\times9\) filters, center each filter, and normalize rows. The bank is almost surely rank 16.

The full-rank random bank is shared across task, architecture, and treatment for the same block/init replicate.

## Pairing and seeds

Use a seed namespace disjoint from all earlier experiments.

For each renderer block and init replicate:

- renderer data are shared across anchor families, architectures, and treatments within a task;
- downstream model initialization is paired across anchor families and treatments within architecture/task;
- randomized anchor realization is paired across architectures, tasks, and treatments;
- minibatch order is paired across anchor families and treatments within architecture/task/init replicate.

Anchor-family labels are intentionally omitted from downstream-parameter initialization seeds. Treatment labels are omitted from both downstream and anchor seeds.

## Training objective

For anchor bank \(W_{\mathrm{anchor}}\),

\[
\mathcal L
=
\mathcal L_{\mathrm{CE}}
+
\lambda(e)
\frac{\lVert W-W_{\mathrm{anchor}}\rVert_F^2}
{\lVert W_{\mathrm{anchor}}\rVert_F^2}.
\]

Treatments:

### retention_1

\[
\lambda(e)=1
\]

for all 200 epochs.

### release_default

\[
\lambda(e)
=
\operatorname{clip}\!\left(\frac{80-e}{70},0,1\right).
\]

Thus the schedule matches the completed architecture experiment exactly.

## Ranking and patching

Use the same validation-only standardized first-layer global-max activation-contrast ranking as the completed architecture experiment.

Evaluate selected-channel patching at every

\[
k=1,\ldots,16.
\]

Also evaluate eight same-size random channel orders at every \(k\). This random-channel analysis is prespecified because the completed architecture diagnostics suggested that some architecture dependence may not require the selected-channel ranking.

Evaluate the existing validation-energy-matched controls at \(k\in\{1,2,4,8\}\) as secondary diagnostics.

No test-set quantity may select channels.

## Primary metrics and estimand

Primary metrics:

1. centered-logit fidelity \(F_{\mathrm{clogit}}\);
2. unnormalized probability reconstruction-error reduction \(R_{\mathrm{prob}}\).

Historical normalized probability fidelity remains a secondary bridge metric.

For metric \(M\), define

\[
\Delta^M_{b,s,a,h,t}(k)
=
M^{\mathrm{release}}_{b,s,a,h,t}(k)
-
M^{\mathrm{retention}}_{b,s,a,h,t}(k),
\]

where \(h\) indexes anchor family.

Define

\[
B^M_{b,s,a,h,t}
=
\frac{\Delta^M(4)+\Delta^M(8)}{2}
-
\frac{\Delta^M(1)+\Delta^M(2)}{2}.
\]

Average the four init/anchor replicates within block:

\[
\bar B^M_{b,a,h,t}
=
\frac14\sum_{s=0}^{3}B^M_{b,s,a,h,t}.
\]

The same definitions are applied to the mean over the eight random channel orders, yielding \(B^M_{\mathrm{random}}\).

## Primary task

Primary task: **two_concepts**.

**single_shape** is a prespecified secondary replication/scope task.

## Primary hypothesis family A: spatial-template specificity

For each primary metric compute

\[
C^M_{\mathrm{spatial},b}
=
\frac14\sum_a
\left(
\bar B^M_{b,a,\mathrm{structured}}
-
\bar B^M_{b,a,\mathrm{pixelperm}}
\right).
\]

This averages over the four frozen architecture variants before inference.

Report:

- mean;
- SD;
- paired 95% Student-\(t\) interval;
- paired \(t\) statistic;
- two-sided sign-flip randomization \(p\) value with fixed seed and 100,000 permutations.

The two primary metrics form one Holm-adjusted two-test family.

A statistically nonzero contrast supports sensitivity to the original 2D spatial arrangement beyond the exactly Gram/rank/spectrum-matched pixel-permuted control.

### Frozen equivalence companion

Failure to reject a zero difference is **not** evidence of equivalence. Therefore, before full Stage-G outcomes are inspected, the study also freezes a two-one-sided-tests (TOST) equivalence companion.

For each primary metric, the smallest effect size of interest is defined as **20% of the historical Stage-F mean absolute \(B\)** across the same four diagnostic architecture forms on **two_concepts**.

The historical Stage-F architecture means are:

- centered-logit fidelity: \(0.1455765,\,0.0849262,\,-0.0166814,\,0.0936226\);
- probability error reduction: \(0.8315121,\,0.0943583,\,-0.0580836,\,0.3347732\).

Therefore the frozen symmetric equivalence margins are

\[
\delta_{\mathrm{clogit}}=0.017040331170505053,
\]

\[
\delta_{R_{\mathrm{prob}}}=0.06593636028899892.
\]

For each metric, perform paired TOST at \(\alpha=0.05\) for the interval
\([-\delta_M,+\delta_M]\), equivalently reporting the 90% CI. The metric-level TOST \(p\) value is the maximum of the two one-sided \(p\) values. The two metric-level TOST \(p\) values are Holm-adjusted as one two-test family.

Interpretation is frozen as:

- **difference supported:** the Holm-adjusted difference test rejects zero;
- **practical equivalence supported:** the Holm-adjusted TOST rejects effects outside the frozen margin;
- **inconclusive:** neither criterion is met.

A nonsignificant difference test alone must never be described as evidence that spatial template structure does not matter.

## Primary hypothesis family B: spatial-structure × architecture interaction

For each primary metric form the \(100\times4\) matrix

\[
D^M_{b,a}
=
\bar B^M_{b,a,\mathrm{structured}}
-
\bar B^M_{b,a,\mathrm{pixelperm}}.
\]

Test architecture heterogeneity in \(D\) using a within-block permutation omnibus:

- statistic: balanced repeated-measures architecture \(F\) statistic;
- null generation: independently permute the four architecture labels within each renderer block;
- fixed random seed;
- 100,000 permutations;
- \(p\) value with the \(+1\) correction.

The two metric \(p\) values form one Holm-adjusted family.

This tests whether any spatial-template effect depends on downstream architecture.

## Prespecified ranking-independence diagnostic

Repeat hypothesis families A and B using \(B_{\mathrm{random}}\), where each metric is averaged over the eight random channel orders before forming \(B\).

These are prespecified robustness diagnostics, not an additional primary family. They answer whether any anchor-specificity conclusion depends on the validation-derived channel-ranking rule.

The same frozen equivalence margins may be reported descriptively for the random-channel version, but the selected-channel family remains primary.

## Secondary anchor contrasts

For each metric/task/architecture report paired block-level contrasts:

1. structured minus pixel-permuted;
2. pixel-permuted minus random-rank10;
3. random-rank10 minus random-fullrank;
4. structured minus random-fullrank.

Use 95% paired intervals and Holm adjustment within metric, task, and contrast family.

Only contrast 1 isolates spatial arrangement while holding the bank Gram matrix, rank, and singular spectrum fixed.

## Structural measurements

At epoch 200 report:

- similarity to the model's own anchor bank;
- similarity to the original structured template bank;
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
- pixel-permuted anchors have numerical rank 10;
- random-rank10 anchors have numerical rank 10;
- random-fullrank anchors have numerical rank 16;
- anchor hashes and generation seeds are recorded;
- no model is excluded based on outcome.

## Interpretation boundary

This experiment can answer whether the project's channel-budget treatment contrast requires the designed spatial arrangement of the predefined template bank within the controlled small-CNN setting.

It cannot establish semantic interpretability, natural-image generalization, or a unique mechanism.

Either outcome is scientifically useful:

- if structured and pixel-permuted anchors are practically equivalent under the frozen TOST criterion, the paper should pivot away from template-specificity and present predefined templates as a controlled case study of anchor-retention/patching measurement behavior;
- if they differ reproducibly, the paper gains direct evidence that spatial template structure contributes beyond bank Gram/rank/spectrum geometry;
- if neither difference nor equivalence is established, the spatial-specificity question remains unresolved.

## Protocol amendments

### Amendment 1 — numerical rank tolerance

Committed during implementation validation and before any full Stage-G scientific outcome was generated or inspected.

The original template bank is algebraically rank 10, but float32 storage lifts nominally zero singular values to approximately \(10^{-8}\). All Stage-G rank-integrity checks therefore use an absolute singular-value tolerance of

\[
10^{-6}.
\]

This is an implementation-level numerical tolerance only and does not alter the scientific design.

### Amendment 2 — equivalence interpretation

Committed before any full Stage-G scientific outcome was generated or inspected.

The original protocol incorrectly allowed a “near-zero” structured-minus-pixel-permuted estimate to motivate a no-difference interpretation without a formal equivalence criterion. Amendment 2 freezes the TOST procedure and numerical margins above so that absence of statistical difference cannot be misinterpreted as evidence of equivalence.

### Formatting repair

The protocol was re-rendered in clean Markdown/LaTeX after implementation validation because an earlier write introduced escaped control characters in several equations. This repair changes no scientific design, sample, contrast, metric, or analysis rule.
