# Research status and scientific handoff

Last updated: 2026-09-21

This document is the durable current scientific state of the project. The chronological research memory is now `checkpoints/`. A new researcher or AI agent must first read `checkpoints/README.md`, the latest `CP-XXX_*.md`, this file, `.ai_handoff`, and the active frozen protocols before changing experiments or rewriting the manuscript.

## 1. Project in one paragraph

This project studies the gap between **weight-space structure** and **functional intervention measurements** in small CNNs whose first convolution is initialized from a bank of predefined spatial templates. The first-layer filters are either kept close to their initial templates with a constant L2 penalty or allowed to move away as that penalty is annealed to zero. Constant regularization reliably preserves template-like filters, but the release-versus-retention difference measured by first-layer activation patching changes with the number of patched channels. The effect is strong in TinyCNN under multiple metrics and is strongly conditioned by downstream architecture in the completed fresh-sample architecture study. The active final fresh-sample experiment now tests whether the phenomenon specifically depends on the designed spatial template arrangement or instead reflects anchor retention/release more generally.

The intended contribution is **empirical and measurement-focused**. The paper does not claim that predefined templates automatically create human-interpretable concepts, that activation patching measures a unique causal quantity, or that the observed effect generalizes to natural images.

## 2. Current live state

### Stage F is complete

The official Stage-F run is:

```text
%LOCALAPPDATA%\prior-templates-cnns\results\architecture_robustness_cuda_001
```

As of 2026-09-20:

- **training complete: 25,600 / 25,600 models**;
- **evaluation complete: 25,600 / 25,600 models**;
- the frozen Stage-F analysis has completed and been archived under `analysis/architecture_robustness_001/`;
- training used sequential CUDA on an NVIDIA RTX 4500 Ada Generation;
- maximum full-patch logit identity error = 0;
- maximum no-op logit identity error = 0;
- Stage-F raw checkpoints and per-model evaluator JSONs remain outside the repository.

The run was launched with the frozen design and a clean CUDA output root. If the server is restarted, resume with exactly:

```powershell
.\run\run_architecture_robustness.ps1 `
  -OutputRoot "$env:LOCALAPPDATA\prior-templates-cnns\results\architecture_robustness_cuda_001" `
  -TrainDevice cuda `
  -TrainWorkers 1 `
  -EvalDevice cuda `
  -EvalBatchSize 256
```

The run is complete. The resume command is retained only for provenance/recovery; completed training and evaluation artifacts are skipped automatically.

**Do not modify** any of the following while the official Stage-F run may need to resume:

- `studies/cnn_architecture_robustness/PROTOCOL.md`
- `architecture_core.py`
- `train_grid.py`
- `evaluate_grid.py`
- `analyze.py`

The execution manifest freezes source hashes. Documentation-only changes are safe.

### Earlier CPU attempt

Before the CUDA benchmark, approximately 1,000 Stage-F models were completed under the original CPU-multiprocessing root:

```text
%LOCALAPPDATA%\prior-templates-cnns\results\architecture_robustness_001
```

Those checkpoints were not deleted, but they are **not part of the official Stage-F analysis**. Do not merge CPU-partial checkpoints with the clean CUDA run.

### Runtime benchmark

A separate implementation benchmark found:

| mode | throughput | effective time/model |
|---|---:|---:|
| CPU, 12 workers | 110.13 models/hour | 32.69 s |
| CUDA, sequential | 1167.55 models/hour | 3.08 s |

CUDA was about 10.6x faster. This benchmark is operational evidence only and is not part of Stage-F inference.

## 3. Core scientific setup

### Tasks

The experiments use two controlled synthetic image tasks:

- `single_shape`
- `two_concepts`

The renderer provides matched counterfactual image pairs and known concept/nuisance structure. The synthetic setting is intentional: it gives exact interventions and controlled counterfactuals. It is **not** intended to approximate the full complexity of natural images.

### Historical architectures

The original two architectures are:

- **TinyCNN**: bias-free 1->16, 9x9 convolution; ReLU; global max pooling; four-class linear head.
- **TwoLayerCNN**: the same first layer, followed by a bias-free 16->16, 3x3 convolution and ReLU before global max pooling.

The original comparison changed depth and parameterization simultaneously and therefore was never a clean causal intervention on depth.

### Template bank

The first-layer template bank contains 16 centered unit-norm filters:

- 8 edge filters;
- 4 two-ray corners;
- 4 rings.

The bank has rank 10 because some edge directions are redundant.

Filter-template similarity is summarized by the mean best signed centered cosine:

$$
A=\frac1{16}\sum_i\max_j\langle\widehat W_i,\widehat T_j\rangle.
$$

This is a **weight-space** similarity measurement. It should not be equated with concept representation, human interpretability, or functional causal importance.

### Training intervention

All template-based conditions initialize the first convolution from the same bank.

The regularized objective is:

$$
\mathcal L
=
\mathcal L_{CE}
+
\lambda(e)
\frac{\|W-W_{anchor}\|_F^2}{\|W_{anchor}\|_F^2}.
$$

Central conditions:

- `template_init`: template initialization, then no penalty;
- `retention_1`: constant lambda=1;
- `release_default`: lambda=1 through epoch 10, linearly decays to zero by epoch 80, then remains zero.

Historical Stages B/D/E use Adam, learning rate 0.003, batch size 128, 200 epochs, no scheduler, no early stopping. With 512 training images, there are four optimizer steps per epoch.

## 4. Activation patching and what it means

Patching occurs **after the first convolution and ReLU**. For a matched base/counterfactual pair, selected first-layer activation maps in the base run are replaced with the corresponding maps from the counterfactual run.

Historically, with output probabilities (p_0,p_1,p_S), the main metric was:

$$
F_{prob}(S)
=
1-
\frac{\sum\|p_S-p_1\|_2^2}
     {\sum\|p_1-p_0\|_2^2}.
$$

Interpretation:

- (F=0): no-op reconstruction level;
- (F=1): full first-layer patch reproduces the counterfactual output;
- (F<0): patched output is farther from the counterfactual than the unpatched base output.

This is a **counterfactual reconstruction-error reduction normalized by the model's own base-to-counterfactual output difference**.

It is **not**:

- a mediated causal fraction;
- a general measure of feature importance;
- evidence that a channel has a unique semantic meaning;
- a general measure of mechanistic faithfulness.

The denominator is model-specific. The metric-sensitivity audit later showed that this denominator can differ strongly between training treatments.

### Channel rankings

Three historical validation-only ranking rules were studied:

1. standardized first-layer activation contrast;
2. absolute deviation of validation concept AUROC from 0.5;
3. singleton validation-patching score.

The standardized activation contrast is the primary ranking for Stage D and Stage F because it was historically central and does not rank channels by the downstream patching endpoint itself.

### Controls

The project also uses:

- same-size random channel sets;
- validation replacement-energy-matched channel sets.

The selected-minus-control difference is informative as a decomposition, but the control term can move independently. It is not the primary Stage-D/F estimand.

## 5. Experimental chronology and evidential roles

The project deliberately preserves stages instead of pretending all analyses were planned from the beginning.

| Stage | Evidence | Evidential role |
|---|---|---|
| Pilot | historical first pass | exploratory only |
| A | 400 models, 40 epochs | early alignment/intervention tests |
| B | 200 models, 200 epochs | longitudinal retention/release study; exploratory contrasts |
| C | 80 saved Stage-B checkpoints, rankings and k sensitivity | post hoc measurement decomposition |
| C energy control | saved checkpoints | post hoc replacement-energy control |
| D | 80 new models, blocks 4000--4019 | **prespecified prospective follow-up/test** with one primary TinyCNN contrast |
| E | 1,200 new models, blocks 5000--5049 | prespecified secondary sensitivity map |
| Metric audit | 1,280 saved D/E checkpoints | frozen post hoc metric-sensitivity analysis; no retraining |
| Checkpoint audit | 32 fixed Stage-B checkpoints | independent reimplementation check |
| F | 25,600 new models, blocks 6000--6099 | prospectively frozen fresh-sample architecture robustness study |

Do not pool stages as if they were independent repetitions of one preregistered hypothesis.

### Terminology

For all new paper-facing prose, `literature/TERMINOLOGY.md` is the terminology source of truth. Read it before introducing or revising recurring terms. It supersedes older wording preserved in historical stage descriptions, checkpoints, analysis folders, and frozen reports.

Use **pre-specified** consistently. Do not call Stage D generically “confirmatory” or describe any follow-up as preregistered unless the record supports that claim. Historical directory names and frozen reports remain unchanged as provenance.

## 6. What each stage taught us

### Stage A — structural retention is real, functional story was not simple

Stage A established that constant template regularization strongly increases first-layer filter-template similarity. However, the initial selected-minus-random functional comparison did not provide a simple corresponding benefit after multiplicity correction.

This is the first important separation:

> preserving template-like weights is not the same thing as obtaining uniformly stronger activation-patching effects.

### Stage B — long training and release

Stage B extended training to 200 epochs and introduced annealed release of the template regularizer. The resulting checkpoints became the basis for the later patch-budget analyses.

Stage-B contrasts are exploratory. Do not retrospectively describe Stage B as an independent confirmation of later hypotheses.

### Stage C — the original selected-minus-random story decomposes

Stage C reused Stage-B checkpoints and varied:

- number of patched channels (k\in\{1,2,4,8\});
- channel ranking;
- random and energy-matched controls.

The important finding was that a positive selected-minus-random difference at (k=4) could arise partly because the **random baseline decreased**, not because selected-channel patching itself became larger.

This motivated dropping selected-minus-random (U) as the primary quantity and focusing directly on the selected-channel patching effect.

Stage C also exposed strong **patch-budget dependence**: the release-minus-retention comparison changed as more channels were patched.

### Stage D — prospective test on fresh blocks

Stage D froze a primary contrast before generating/evaluating blocks 4000--4019.

For block (b):

$$
\Delta_b(k)=F_b^{release}(k)-F_b^{retention}(k)
$$

and

$$
B_b=
\frac{\Delta_b(4)+\Delta_b(8)}2
-
\frac{\Delta_b(1)+\Delta_b(2)}2.
$$

A positive (B) means only that the release-minus-retention difference is larger for (k=4,8) than for (k=1,2). It does **not** imply monotonicity or that release is absolutely better at every larger budget.

Primary TinyCNN / `two_concepts` / contrast-ranking result:

$$
B=+0.330976,
\quad
95\%\ CI=[+0.273680,+0.388273],
\quad
t_{19}=12.0905,
\quad
p=2.28\times10^{-10}.
$$

All 20 block-level (B_b) values were positive.

Pointwise release-minus-retention differences:

| k | Delta F_prob | 95% CI |
|---:|---:|---:|
| 1 | -0.3459 | [-0.4033, -0.2885] |
| 2 | -0.3317 | [-0.4082, -0.2552] |
| 4 | -0.0221 | [-0.0424, -0.0019] |
| 8 | +0.0065 | [+0.0037, +0.0093] |

Alternative validation rankings showed the same broad TinyCNN channel-count dependence.

TwoLayerCNN did **not** show the same pattern, which became a central architecture question rather than something to hide.

### Stage E — robustness map, not another primary test

Stage E used 50 fresh blocks for each task/architecture setting and six regularization schedules, yielding 1,200 models.

For the default release schedule relative to constant lambda=1 under contrast ranking:

| task | architecture | B_prob | 95% CI |
|---|---|---:|---:|
| single_shape | TinyCNN | +0.07189 | [+0.05444,+0.08934] |
| single_shape | TwoLayerCNN | -0.01018 | [-0.02290,+0.00254] |
| two_concepts | TinyCNN | +0.28619 | [+0.25389,+0.31850] |
| two_concepts | TwoLayerCNN | -0.04156 | [-0.06983,-0.01329] |

All five non-reference schedules produced positive (B) for TinyCNN on both tasks under the contrast ranking. TwoLayerCNN estimates were near zero or negative depending on task/schedule.

The schedule results are a **sensitivity map**, not evidence for a monotone causal dose law.

### Checkpoint audit — implementation reproducibility

An independent implementation recomputed central metrics at 32 fixed Stage-B checkpoints.

Final audit status: **PASS**.

Maximum discrepancies included:

- filter-template similarity: (2.22\times10^{-16});
- selected-channel probability fidelity: (2.39\times10^{-7});
- random-channel probability fidelity: (1.14\times10^{-7});
- selected-minus-random: (2.19\times10^{-7});
- ordinary and patched-run accuracies: zero discrepancy.

Full-patch and no-op probability identity errors were zero.

This supports implementation reproducibility on the sampled checkpoints. It is not external replication.

## 7. Metric-sensitivity audit

A major reviewer risk was that (F_{prob}) divides by a model-specific base-to-counterfactual change. The metric audit was therefore frozen before generating its alternative-metric outputs, but **after** the original Stage-D/E probability results were known. It is correctly described as a **frozen post hoc robustness analysis**, not an independent confirmation.

It introduced two primary robustness metrics.

### Centered-logit fidelity

Raw logits admit a common additive offset that leaves probabilities unchanged. Center logits per example:

$$
\widetilde\ell
=
\ell-\mathrm{mean}(\ell)\mathbf 1.
$$

Then:

$$
F_{clogit}(S)
=
1-
\frac{\sum\|\widetilde\ell_S-\widetilde\ell_1\|_2^2}
     {\sum\|\widetilde\ell_1-\widetilde\ell_0\|_2^2}.
$$

### Unnormalized absolute probability error reduction

$$
R_{prob}(S)
=
E_0^{prob}-E_S^{prob}.
$$

This removes division by (E_0^{prob}) entirely.

### Stage-D primary setting under alternative metrics

TinyCNN / `two_concepts` / contrast ranking:

| metric | mean B | 95% CI | Holm-adjusted p |
|---|---:|---:|---:|
| centered-logit fidelity | +0.178881 | [+0.127268,+0.230494] | 6.95e-07 |
| probability error reduction | +0.894411 | [+0.786301,+1.002522] | 8.59e-13 |

Thus the TinyCNN channel-count contrast is **not solely an artifact of the original normalized probability metric**.

However, normalization differences are real. Release-minus-retention differences in base-to-counterfactual error scale were large, for example:

- TinyCNN probability input-effect scale: +0.848558;
- TinyCNN centered-logit input-effect scale: +126.537.

Therefore the manuscript must explicitly acknowledge that the original (F_{prob}) comparison is influenced by treatment-dependent normalization scale. The correct robustness statement is that the TinyCNN pattern persists under centered-logit and unnormalized probability-error metrics, not that the denominator was harmless.

### Stage-E metric extension

Default release minus retention under contrast ranking:

| task / architecture | B_clogit | B_Rprob |
|---|---:|---:|
| single_shape / TinyCNN | +0.056604 | +0.337472 |
| single_shape / TwoLayerCNN | +0.057000 | -0.016223 |
| two_concepts / TinyCNN | +0.134268 | +0.802385 |
| two_concepts / TwoLayerCNN | -0.019527 | -0.054970 |

Again, TinyCNN is comparatively stable while TwoLayerCNN is metric/task dependent. This directly motivated Stage F.

Integrity:

- maximum historical probability-fidelity recomputation difference: (1.24\times10^{-7});
- maximum full-patch logit identity error: 0;
- maximum no-op logit identity error: 0.

## 8. Stage F — the current architecture study

Frozen protocol commit:

```text
6dccf0948204e4af05d232f4d944b7b3903e5387
```

Stage F was designed **after** D/E and the metric audit were known, but before any Stage-F outcome was inspected.

### Scientific question

Holding fixed:

- synthetic tasks;
- matched counterfactual construction;
- first-layer 1->16, 9x9 convolution;
- same 16 templates;
- ReLU intervention point;
- retention-vs-release comparison;
- validation-only contrast ranking;
- patch budgets;
- output metrics;

how does **downstream architecture** change the release-versus-retention patch-budget contrast?

### Scale

$$
100\ blocks
\times4\ init\ replicates
\times2\ tasks
\times2\ treatments
\times16\ architectures
=
25,600\ models.
$$

Fresh renderer blocks are 6000--6099.

Four initialization replicates are **not** four independent inferential observations. They are averaged within renderer block. Primary inference therefore uses (n=100) independent renderer-block summaries per architecture/task/metric.

### Architecture factors

Stage F systematically varies:

- GMP vs GAP;
- convolutional depth 1, 2, 4;
- downstream width 16 vs 64;
- plain vs residual connectivity;
- downstream BatchNorm vs no BatchNorm.

All 16 architectures preserve the exact same first-layer 16-channel intervention tensor.

### Primary metrics

Primary Stage-F metrics:

1. centered-logit fidelity;
2. unnormalized absolute probability error reduction.

Historical probability fidelity is retained as a secondary bridge metric.

### Primary estimand

For metric (M):

$$
\Delta^M_{b,s,a,t}(k)
=
M^{release}_{b,s,a,t}(k)
-
M^{retention}_{b,s,a,t}(k),
$$

$$
B^M_{b,s,a,t}
=
\frac{\Delta^M(4)+\Delta^M(8)}2
-
\frac{\Delta^M(1)+\Delta^M(2)}2.
$$

Average the four initialization replicates:

$$
\bar B^M_{b,a,t}
=
\frac14\sum_{s=0}^3 B^M_{b,s,a,t}.
$$

### Frozen primary analyses

Primary task: `two_concepts`.

For each of the two primary metrics:

1. repeated-measures omnibus test of architecture heterogeneity across all 16 architectures;
2. fresh-sample bridge contrast:
   [
   \bar B_{tiny\_gmp}-\bar B_{plain2\_w16\_gmp}.
   ]

The two metric p-values in each primary family are Holm adjusted.

### Prespecified architecture-factor decompositions

Secondary paired block-level contrasts decompose:

- pooling;
- depth;
- width;
- residual connectivity;
- BatchNorm.

These help locate where architecture heterogeneity arises. They should not be turned into a post hoc winner ranking.

### Stage-F observed primary results

Stage F found strong architecture heterogeneity on the frozen primary `two_concepts` task under **both** primary metrics.

Repeated-measures omnibus tests across 16 architectures:

| metric | F(15,1485) | partial eta^2 | Holm-adjusted p |
|---|---:|---:|---:|
| centered-logit fidelity | 77.0874 | 0.4378 | 2.40e-173 |
| probability error reduction | 656.7002 | 0.8690 | numerically underflowed to 0 |

The fresh TinyCNN-vs-TwoLayer-form bridge also strongly replicated the architecture difference:

| metric | mean B difference: tiny_gmp - plain2_w16_gmp | 95% CI |
|---|---:|---:|
| centered-logit fidelity | +0.162258 | [+0.149701,+0.174815] |
| probability error reduction | +0.889596 | [+0.862118,+0.917073] |

The corresponding architecture means were:

- `tiny_gmp`: B = +0.145577 centered-logit; +0.831512 probability-error reduction;
- `plain2_w16_gmp`: B = -0.016681 centered-logit; -0.058084 probability-error reduction.

Thus the architecture difference first suggested by Stage E was **prospectively reproduced on 100 fresh renderer blocks** and is not specific to the historical normalized probability metric.

### Stage-F architecture-factor interpretation

The strongest qualitative lesson is not a single monotone architecture factor. Instead, the channel-count contrast depends on **interactions among downstream pooling, depth, normalization, and metric**.

#### Pooling is important, but its direction depends on the backbone

For `two_concepts`, GAP minus GMP is:

- Tiny: -0.06065 centered-logit; -0.73715 probability-error reduction;
- Plain depth-2 width-16: +0.11030; +0.39286;
- Plain depth-4 width-16: +0.04447; +0.17214;
- Plain depth-2 width-64: +0.22850; +0.32679;
- Plain depth-4 width-64: +0.05598; +0.02511;
- Residual depth-4 width-16: +0.06183; +0.14220;
- BN depth-2 width-16: -0.15467; -0.05170;
- BN depth-4 width-16: +0.13133; +0.07805.

All eight pooling-family contrasts are Holm-significant for both primary metrics.

Therefore the correct paper-level statement is:

> spatial aggregation strongly conditions the patch-budget treatment contrast, but there is no architecture-independent direction for GAP versus GMP.

In particular, TinyCNN is unusual: GMP produces a much larger positive unnormalized-probability B than GAP, whereas most multi-layer plain/residual backbones show the opposite sign for GAP-minus-GMP.

#### Depth has a large interaction with pooling

Under GMP:

- plain2 - tiny = -0.16226 centered-logit and -0.88960 probability-error reduction;
- plain4 - plain2 is approximately zero under both primary metrics.

This indicates that the **first added downstream convolution** accounts for nearly all of the Tiny-vs-plain depth difference under GMP; adding further plain depth from 2 to 4 does little under GMP.

Under GAP:

- plain2 - tiny is near zero for centered-logit fidelity but +0.24041 for probability-error reduction;
- plain4 - plain2 is negative under both metrics.

Depth is therefore not a single monotone causal factor; it interacts with pooling and metric.

#### Width is secondary and metric-dependent

Increasing width 16->64 produces small-to-moderate changes. Centered-logit contrasts are positive in all four frozen width comparisons, while probability-error reduction is positive under GMP but null/negative under some GAP comparisons. Width does not explain the dominant Tiny-vs-plain2 GMP contrast.

#### Residual connectivity is not a major driver here

Residual4 - plain4 intervals include zero for both GMP and GAP under both primary metrics after the frozen family correction. This is one of the cleanest negative findings of Stage F.

#### BatchNorm strongly changes some settings, but not with a universal direction

At depth 2 with GAP, BatchNorm sharply reduces B under both metrics. At depth 4 with GAP, centered-logit B increases but probability-error-reduction B decreases. Under GMP, BN produces modest positive changes. Therefore normalization is another interaction term, not a simple main effect.

### Stage-F metric and scale interpretation

Architecture heterogeneity is visible under both:

1. normalized centered-logit fidelity;
2. unnormalized probability reconstruction-error reduction.

This is important because their scaling conventions differ.

The unnormalized probability measure also exposes large architecture-specific differences in the release-minus-retention base-to-counterfactual output scale. For example on `two_concepts`, the probability input-effect-scale contrast is approximately:

- `tiny_gmp`: +0.8375;
- `tiny_gap`: +0.1901;
- `plain2_w16_gap`: +0.7420;
- `plain2_w16_gmp`: +0.0611.

Thus absolute probability-error magnitudes should not be interpreted as architecture-invariant units. The architecture result is strengthened by the fact that the centered-logit normalized metric also shows strong heterogeneity and the same fresh Tiny-vs-plain2 bridge.

### Secondary task

The `single_shape` task also shows substantial architecture dependence, but several architecture/metric combinations differ qualitatively from `two_concepts`. This supports the paper's scope claim: architecture and task both condition the observed patching comparison.

### Final Stage-F interpretation

Stage F should **not** be summarized as “GAP fixes the effect,” “depth destroys the effect,” or “one architecture is correct.”

The defensible conclusion is:

> the release-versus-retention activation-patching comparison is strongly architecture-dependent. Pooling and the first downstream convolution produce especially large changes, but their effects interact with backbone structure, normalization, task, and output metric.

This is a stronger and more interesting result than universal replication because it maps a reproducible boundary of the measurement phenomenon.

## 9. Novelty and positioning

Do **not** claim that activation patching being sensitive to intervention granularity is itself novel. Prior mechanistic-interpretability work already discusses sensitivity to corruption, metric, intervention choice, ablation method, and granularity.

The narrower contribution is:

> under fixed counterfactual construction, intervention layer, channel-ranking procedure, and training comparison, changing the strength/duration of a structured first-layer prior produces patching differences whose apparent effect depends on the number of patched channels and on downstream architecture; this occurs even though constant template regularization strongly preserves weight-space similarity.

The project therefore connects two literatures:

1. predefined/structured first-layer filters and template retention;
2. activation-patching/mechanistic-intervention measurement sensitivity.

The key conceptual separation is:

> **template-like weights do not guarantee a stable functional interpretation under activation patching.**

Relevant literature already incorporated in the project includes work on predefined filters, learnable/maintained Gabor structure, activation patching methodology and metric/granularity sensitivity, and ablation-method sensitivity.

Use literature terminology such as:

- predefined filters;
- spatial filters;
- filter initialization;
- filter similarity;
- maintaining filter structure;
- filter kernels.

Avoid inventing stronger terminology such as “interpretable filters” unless the evidence specifically supports it.

## 9.1 Publication target and current reviewer risks

The manuscript uses anonymous TMLR style; the working publication target remains **TMLR**.

The strict referee pass that motivated the final strengthening round has now been addressed by two completed analyses:

1. the fresh matched-anchor specificity experiment, which separates the original two-dimensional template arrangement from a Gram/rank/spectrum-matched pixel-permuted control;
2. post hoc architecture diagnostics using Greenhouse--Geisser correction, within-block permutation tests, Friedman tests, and random channel orders.

The principal remaining reviewer risks are now scope and interpretation rather than missing internal controls:

- synthetic-only external validity;
- small-model scope;
- patched hybrid states may still be off-manifold;
- pointwise conclusions and practical-effect conclusions differ across output metrics;
- architecture heterogeneity survives random channels, while spatial specificity is substantially stronger for validation-selected channels;
- the spatial effect reverses sign in plain2_w16_gmp, so there is no universal positive template effect;
- the selected-channel probability-error spatial difference is statistically nonzero but practically equivalent under the frozen SESOI.

The default response to these risks is precise scope and presentation, not another large experiment.

## 10. Final fresh-sample anchor-specificity result

The frozen anchor-specificity experiment is complete and archived under analysis/anchor_specificity_001/.

Scale:

- 25,600 / 25,600 trained models;
- 25,600 / 25,600 evaluations;
- 100 fresh renderer blocks;
- four init/anchor replicates averaged within block;
- primary task: two_concepts;
- primary metrics: centered-logit fidelity and probability error reduction.

The primary control applies one common spatial permutation to every template row. It preserves the complete bank Gram matrix, row norms, numerical rank, singular spectrum, and row coefficient multisets while destroying the original 2D edge/corner/ring arrangement.

Primary selected-channel structured-minus-pixel-permuted B, averaged over the four diagnostic architectures:

| metric | mean difference | 95% CI | Holm sign-flip p | frozen equivalence conclusion |
|---|---:|---:|---:|---|
| centered-logit fidelity | +0.057426 | [+0.051165,+0.063686] | 2.0e-05 | **not equivalent** under +/-0.017040 |
| probability error reduction | +0.045628 | [+0.037281,+0.053975] | 2.0e-05 | **practically equivalent** under +/-0.065936 |

For probability error reduction, the mean difference is estimated away from zero but remains smaller than the prespecified smallest effect size of interest.

Spatial-structure x architecture interaction:

- centered logits: F(3,297)=91.7943, partial eta^2=0.4811, Holm permutation p=2.0e-05;
- probability error reduction: F(3,297)=157.6951, partial eta^2=0.6143, Holm permutation p=2.0e-05.

Architecture-specific selected-channel structured-minus-pixel-permuted effects on two_concepts:

| architecture | centered logit | probability error |
|---|---:|---:|
| tiny_gmp | +0.10624 | +0.19953 |
| tiny_gap | +0.07690 | +0.04308 |
| plain2_w16_gap | +0.09109 | +0.02057 |
| plain2_w16_gmp | **-0.04453** | **-0.08067** |

Thus spatial structure has no architecture-independent direction.

The prespecified random-channel version is much smaller:

- centered logits: +0.005709, 95% CI [+0.003919,+0.007498];
- probability error reduction: +0.020068, 95% CI [+0.017225,+0.022911].

Both random-channel averages are practically equivalent under the frozen margins.

Secondary anchor contrasts show that pixel-permuted, generic random rank-10, and generic random full-rank anchors are usually similar on the primary task. Numerical rank alone does not explain the selected-channel spatial-specificity result.

Integrity:

- maximum full-patch logit error = 0;
- maximum no-op logit error = 0;
- maximum structured-versus-pixel-permuted Gram discrepancy = 6.66e-16.

The final interpretation is:

> preserving designed first-layer spatial structure changes how the release-versus-retention patch-budget comparison concentrates in validation-selected channels, but the magnitude and even direction of that structure-specific effect depend on downstream architecture and output metric.

## 11. Completed post hoc architecture diagnostics

Archived under analysis/architecture_posthoc_diagnostics_001/.

These diagnostics are outcome-informed and post hoc. They retrain no models.

The prospectively observed architecture heterogeneity survives:

- Greenhouse--Geisser correction;
- 100,000 within-block architecture permutations;
- Friedman rank-based inference.

For both primary metrics, the architecture permutation Holm p value is 2.0e-05.

Architecture dependence also persists when B is averaged over eight random channel orders:

- centered-logit architecture permutation Holm p=2.0e-05;
- probability-error architecture permutation Holm p=2.0e-05.

Selected-versus-random architecture-mean Spearman correlations are 0.256 for centered logits and 0.724 for probability error reduction.

Random-channel TinyGMP-minus-Plain2-GMP bridge:

- centered logits: +0.002765, 95% CI [+0.000014,+0.005515], Holm p=0.0488;
- probability error reduction: +0.319871, 95% CI [+0.312788,+0.326953], Holm p=2.76e-96.

Therefore the architecture conclusion is not solely a consequence of the validation-derived ranking, although ranking materially changes effect size and architecture ordering.

## 12. Current manuscript state

paper/main.tex was rewritten from scratch after the final independent-block results.

Before the rewrite, the complete literature/extracted/ corpus was reviewed: **43 extracted works** spanning predefined/fixed filters, early CNN filters, concept-based XAI, activation patching, circuit-faithfulness methodology, causal abstraction, and mechanistic-identifiability limitations.

Current title:

> **Activation-Patching Effects in Controlled CNNs Depend on Intervention Size, Network Architecture, and First-Layer Filter Structure**

The main manuscript is organized by scientific question rather than project chronology:

1. predefined first-layer filters and the distinction between filter similarity and effects on model behavior;
2. the pre-specified intervention-size result;
3. sensitivity of the intervention-size contrast to the evaluation metric;
4. differences across network architectures plus post-hoc statistical analyses;
5. the pixel-permuted filter-bank control for the original 2D spatial arrangement.

Manuscript conventions:

- no visible Stage A--G identifiers in paper-facing prose;
- cleveref for all cross-references;
- every displayed equation numbered and explicitly labeled;
- four principal figures:
  1. renderer/template/patching overview;
  2. learned-kernel gallery;
  3. intervention size + 16-architecture results;
  4. pixel-permuted filter-bank control;
- complete numerical detail remains in appendices;
- no main-text tables;
- approximately 4,600 main-text words before appendices.

The paper now includes paper/specificity_robustness_results.tex for the pixel-permuted control and post-hoc architecture analyses.

## 13. Literature-grounded positioning

The extracted literature does **not** support equating visually structured first-layer kernels with interpretability.

The final positioning connects three established literatures:

1. predefined and structured filters: fixed/Gabor/predefined first layers can be useful and their structure can be maintained or degraded during training;
2. alignment versus influence: concept alignment, decodability, and causal influence are distinct quantities;
3. activation-patching measurement dependence: patch direction, granularity, input construction, ablation/replacement choice, and evaluation metric condition the question being measured.

Accordingly, do not claim that sensitivity of activation patching to methodology is itself novel.

The narrower contribution is:

> in controlled CNNs with matched counterfactuals, the patching-effect difference between release and retention depends on intervention size and network architecture; a pixel-permuted filter-bank control further shows that the original 2D spatial arrangement changes the patching effect for channels selected on the validation set beyond matched Gram-matrix, rank, and singular-spectrum properties.

Use literature-standard terminology such as predefined filters, spatial filters, filter initialization, filter similarity, maintaining filter structure, filter kernels, activation patching, and counterfactual/interchange intervention.

Avoid stronger labels such as interpretable filters unless discussing prior work or explicitly denying that inference.

## 14. Claims the paper can support

1. Constant regularization strongly preserves the predefined first-layer spatial structure.
2. Filter similarity does not determine a unique patching effect.
3. In the pre-specified TinyCNN test, release-versus-retention differences depend on intervention size.
4. The pre-specified contrast between $k=1,2$ and $k=4,8$ remains positive under centered-logit and unnormalized probability evaluation metrics, while values at individual intervention sizes differ.
5. The intervention-size contrast differs strongly across the 16 pre-specified network architectures.
6. Differences across architectures remain after Greenhouse--Geisser correction, within-block permutation tests, Friedman tests, and random-channel analyses.
7. The original 2D filter arrangement changes the centered-logit patching effect for channels selected on the validation set relative to a pixel-permuted control matched on Gram matrix, rank, and singular spectrum.
8. The difference between the structured and pixel-permuted filter banks depends on architecture and reverses sign in one tested architecture.
9. The selected-channel probability-error difference averaged across architectures differs from zero but falls within the pre-specified equivalence margin.
10. The difference between the structured and pixel-permuted filter banks is much smaller on average for random channel subsets, and both random-channel averages fall within the pre-specified equivalence margins.

## 15. Claims the paper must not make

Do not claim:

- a unique causal mechanism;
- a mediated causal fraction;
- that template similarity causes the patching pattern;
- that structured filters are automatically human-interpretable;
- a universal positive effect of predefined templates;
- that the architecture-averaged probability-error difference between structured and pixel-permuted banks is practically important;
- architecture-independent behavior;
- natural-image, transformer, or large-model generalization;
- that post hoc architecture diagnostics are prospective confirmation;
- that image pairs, init replicates, or model count are independent inferential observations.

## 16. Next action

A fresh strict referee pass has been completed and its four substantive concerns have been incorporated into the manuscript:

1. sequential/outcome-informed follow-up design is now explicit;
2. pixel-permuted-control equivalence is explicitly averaged across architectures and tied to a study-specific pre-specified margin;
3. retention-versus-release is explicitly interpreted as a complete training-regime contrast with downstream co-adaptation;
4. Methods now fully define the concept-specific ranking and architecture grid.

The referee-driven revision is build-validated in GitHub Actions. The final LaTeX pass produces a 27-page PDF including appendices with no undefined citations, undefined references, duplicate labels, or unstable cross-references; remaining warnings are typographic Underfull/float-placement notices.

The final readability and submission-readiness pass is complete. The remaining pre-upload step is a fresh manual manuscript build plus visual inspection of the anonymous PDF and any anonymous supplementary ZIP.

Do **not** add another large experiment by default.

Only consider additional empirical work if a final review identifies a concrete unresolved threat that cannot be addressed by the existing fresh-sample controls, robustness analyses, or narrower scope.

## 17. Source-of-truth reading order

1. checkpoints/README.md
2. latest checkpoints/CP-XXX_*.md
3. RESEARCH_STATUS.md
4. .ai_handoff
5. literature/TERMINOLOGY.md
6. paper/main.tex
7. analysis/anchor_specificity_001/REPORT.md
8. analysis/architecture_posthoc_diagnostics_001/REPORT.md
9. analysis/architecture_robustness_001/REPORT.md
10. analysis/metric_sensitivity_001/REPORT.md
11. analysis/budget_confirmation_001/REPORT.md
12. earlier developmental analyses only when provenance is needed.

## 18. One-line handoff

**The pixel-permuted filter-bank control and post-hoc architecture analyses are complete. The manuscript was rewritten from scratch after reviewing all 43 extracted literature sources and then received repeated terminology and referee passes. Sequential study design, equivalence averaged across architectures, downstream co-adaptation, channel ranking, and the exact architecture grid are explicit. The next task is final readability/anonymization/submission polish, not another experiment by default.**
