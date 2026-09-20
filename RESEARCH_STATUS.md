# Research status and scientific handoff

Last updated: 2026-09-19

This document is the durable scientific state of the project. A new researcher or AI agent should read this file, `.ai_handoff`, `paper/REVISION_PLAN.md`, and the frozen protocols before changing experiments or rewriting the manuscript.

## 1. Project in one paragraph

This project studies the gap between **weight-space structure** and **functional intervention measurements** in small CNNs whose first convolution is initialized from a bank of predefined spatial templates. The first-layer filters are either kept close to their initial templates with a constant L2 penalty or allowed to move away as that penalty is annealed to zero. Constant regularization reliably preserves template-like filters, but the release-versus-retention difference measured by first-layer activation patching changes with the number of patched channels. The effect is strong in TinyCNN under multiple metrics and substantially different in TwoLayerCNN. The current Stage F experiment prospectively tests whether this difference is systematically associated with downstream architectural factors while keeping the first-layer intervention space fixed.

The intended contribution is **empirical and measurement-focused**. The paper does not claim that predefined templates automatically create human-interpretable concepts, that activation patching measures a unique causal quantity, or that the observed effect generalizes to natural images.

## 2. Current live state

### Stage F is running

The official Stage-F run is:

```text
%LOCALAPPDATA%\prior-templates-cnns\results\architecture_robustness_cuda_001
```

As of 2026-09-19:

- **training is complete: 25,600 / 25,600 models**;
- training used sequential CUDA on an NVIDIA RTX 4500 Ada Generation;
- **evaluation is in progress** over all 25,600 final checkpoints;
- no Stage-F scientific outcome should be interpreted until the frozen evaluator finishes and the frozen analysis is run;
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

The training phase will skip all completed models and the evaluator will skip already completed evaluation JSONs.

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

[
A=\frac1{16}\sum_i\max_j\langle\widehat W_i,\widehat T_j\rangle.
]

This is a **weight-space** similarity measurement. It should not be equated with concept representation, human interpretability, or functional causal importance.

### Training intervention

All template-based conditions initialize the first convolution from the same bank.

The regularized objective is:

[
\mathcal L
=
\mathcal L_{CE}
+
\lambda(e)
\frac{\|W-W_{anchor}\|_F^2}{\|W_{anchor}\|_F^2}.
]

Central conditions:

- `template_init`: template initialization, then no penalty;
- `retention_1`: constant lambda=1;
- `release_default`: lambda=1 through epoch 10, linearly decays to zero by epoch 80, then remains zero.

Historical Stages B/D/E use Adam, learning rate 0.003, batch size 128, 200 epochs, no scheduler, no early stopping. With 512 training images, there are four optimizer steps per epoch.

## 4. Activation patching and what it means

Patching occurs **after the first convolution and ReLU**. For a matched base/counterfactual pair, selected first-layer activation maps in the base run are replaced with the corresponding maps from the counterfactual run.

Historically, with output probabilities (p_0,p_1,p_S), the main metric was:

[
F_{prob}(S)
=
1-
\frac{\sum\|p_S-p_1\|_2^2}
     {\sum\|p_1-p_0\|_2^2}.
]

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

In new prose, prefer:

- **prespecified prospective follow-up**
- **prespecified prospective test**

Avoid calling Stage D generically “confirmatory” in narrative prose. Historical directory names and frozen reports contain “confirmation” language and should remain unchanged as provenance.

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

[
\Delta_b(k)=F_b^{release}(k)-F_b^{retention}(k)
]

and

[
B_b=
\frac{\Delta_b(4)+\Delta_b(8)}2
-
\frac{\Delta_b(1)+\Delta_b(2)}2.
]

A positive (B) means only that the release-minus-retention difference is larger for (k=4,8) than for (k=1,2). It does **not** imply monotonicity or that release is absolutely better at every larger budget.

Primary TinyCNN / `two_concepts` / contrast-ranking result:

[
B=+0.330976,
\quad
95\%\ CI=[+0.273680,+0.388273],
\quad
t_{19}=12.0905,
\quad
p=2.28\times10^{-10}.
]

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

[
\widetilde\ell
=
\ell-\mathrm{mean}(\ell)\mathbf 1.
]

Then:

[
F_{clogit}(S)
=
1-
\frac{\sum\|\widetilde\ell_S-\widetilde\ell_1\|_2^2}
     {\sum\|\widetilde\ell_1-\widetilde\ell_0\|_2^2}.
]

### Unnormalized absolute probability error reduction

[
R_{prob}(S)
=
E_0^{prob}-E_S^{prob}.
]

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

[
100\ blocks
\times4\ init\ replicates
\times2\ tasks
\times2\ treatments
\times16\ architectures
=
25,600\ models.
]

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

[
\Delta^M_{b,s,a,t}(k)
=
M^{release}_{b,s,a,t}(k)
-
M^{retention}_{b,s,a,t}(k),
]

[
B^M_{b,s,a,t}
=
\frac{\Delta^M(4)+\Delta^M(8)}2
-
\frac{\Delta^M(1)+\Delta^M(2)}2.
]

Average the four initialization replicates:

[
\bar B^M_{b,a,t}
=
\frac14\sum_{s=0}^3 B^M_{b,s,a,t}.
]

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

### Stage-F interpretation logic

The goal is **not** to make every architecture support the TinyCNN result.

Scientifically useful outcomes include:

- **pooling dependence**: GMP and GAP differ strongly;
- **depth dependence**: the contrast changes as downstream depth increases;
- **width dependence**: capacity changes the contrast;
- **normalization/residual dependence**;
- **broad invariance**: the effect persists across many architectures;
- **metric dependence**: centered-logit and absolute probability metrics disagree in some architecture families.

Any of these can sharpen the paper. Stage F should map the **boundary of the phenomenon**, not manufacture universal support.

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

## 10. Claims the paper can currently support

Before Stage F results, the strongest defensible claims are:

1. Constant template regularization preserves first-layer template similarity much more strongly than release.
2. Weight-space template similarity does not imply uniformly larger selected-channel activation-patching effects.
3. In TinyCNN, the release-minus-retention patching comparison changes strongly with number of patched first-layer channels.
4. The TinyCNN channel-count contrast was supported in a prospective fresh-block Stage-D test.
5. The TinyCNN pattern persists across both synthetic tasks and several regularization schedules in Stage E.
6. The TinyCNN pattern persists under centered-logit fidelity and an unnormalized probability reconstruction-error reduction.
7. TwoLayerCNN behaves differently, so architecture independence is not supported.
8. Random/energy-matched baseline-relative comparisons must be decomposed because changes in the control term can drive selected-minus-control differences.
9. The implementation has an independent fixed-checkpoint audit that reproduces sampled metrics within frozen tolerances.

## 11. Claims the paper must NOT make

Do not claim:

- a unique causal mechanism;
- that (F) is a mediated causal fraction;
- that template similarity causes the patching pattern;
- that higher template similarity implies greater human interpretability;
- natural-image generalization;
- transformer generalization;
- architecture-independent behavior before Stage F supports it;
- causal “effect of depth” from the original TinyCNN/TwoLayerCNN comparison;
- that the metric audit is an independent replication;
- that Stage E is another primary confirmation;
- that the matched image pairs are independent inferential replicates.

Do not infer evidence from model count. The unit of inference is the independent renderer block according to each frozen protocol.

## 12. Current manuscript state

`paper/main.tex` is a **pre-Stage-F manuscript snapshot**.

It currently contains Stages A--E and the checkpoint audit, but it does not yet fully integrate:

- the completed metric-sensitivity audit;
- the denominator-scale finding;
- Stage F;
- the final architecture-factor interpretation.

Do not rewrite the manuscript while Stage-F evaluation is incomplete. The planned revision is documented in `paper/REVISION_PLAN.md`.

The current title is:

> Regularizing First-Layer CNN Filters Toward Predefined Templates: Activation-Patching Comparisons Vary with the Number of Patched Channels

The final title should be reconsidered only after Stage F. If architecture heterogeneity becomes central, the title may need to mention both channel count and architecture. Do not choose the final title from anticipated results.

## 13. What happens after Stage F finishes

1. Confirm evaluation completion:
   `evaluation/GRID_COMPLETE.json`.
2. Allow the frozen launcher to run `analyze.py`.
3. Archive paper-facing outputs from the official CUDA root:
   ```powershell
   .\run\stage_architecture_robustness_results.ps1 `
     -SourceRoot "$env:LOCALAPPDATA\prior-templates-cnns\results\architecture_robustness_cuda_001"
   ```
4. Inspect, in this order:
   - `REPORT.md`;
   - `primary_architecture_omnibus.csv`;
   - `primary_bridge_contrast.csv`;
   - `architecture_B_summary.csv`;
   - `architecture_factor_contrasts.csv`;
   - `treatment_delta_curves.csv`;
   - `input_effect_scale_contrasts.csv`;
   - `initialization_dispersion_summary.csv`;
   - `control_diagnostics.csv`.
5. Do not cherry-pick architecture families.
6. Summarize the frozen primary analyses before looking for mechanistic narratives in secondary contrasts.
7. Update `paper/REVISION_PLAN.md` with observed Stage-F conclusions.
8. Rewrite the manuscript.
9. Rebuild figures and paper.
10. Perform a final strict referee pass focused on claim/evidence alignment and whether every inferential role is labeled correctly.
11. Prefer stopping experimentation after Stage F unless the completed paper exposes a concrete fatal gap. More experiments should not be added merely to make the artifact larger.

## 14. Paper-level objective after Stage F

The final paper should be simpler than the experimental history.

The main narrative should become approximately:

1. A structured prior strongly preserves template-like first-layer weights.
2. Functional activation-patching comparisons do not track that structural similarity in a simple way.
3. The release-vs-retention comparison depends on how many first-layer channels are patched.
4. This dependence survives alternative output metrics, including one without the original denominator.
5. Architecture substantially conditions the observed pattern; Stage F maps which downstream factors matter.
6. Therefore structural similarity and functional patching measurements should be reported as distinct objects, and patching conclusions should be checked across intervention granularity and relevant architecture choices.

The paper should not read like “Stage A, then B, then C, then D...” in the main narrative. That chronology belongs in the methods/appendix. The main text should organize evidence around scientific questions.

## 15. Recommended final evidence hierarchy

Main text should prioritize:

1. structural retention result;
2. Stage-D prospective channel-count contrast;
3. metric-sensitivity result;
4. Stage-F architecture result;
5. one compact Stage-E robustness figure/table.

Move most of the following to appendix/supplement:

- full schedule grid;
- alternative rankings;
- random and energy-matched details;
- full k curves for every secondary combination;
- audit implementation history;
- exhaustive block-level tables.

This keeps the paper readable while preserving the full research record in the repository.

## 16. Repository and machine constraints

The user frequently runs on university-managed Windows machines without administrator privileges.

Observed constraints:

- the Git checkout may be partially non-writable;
- Git can still commit/push;
- creating new worktree directories may fail with `UnauthorizedAccessException`;
- `%LOCALAPPDATA%\prior-templates-cnns\...` is writable;
- therefore long experiment outputs live outside the repo.

Do not tell the user to rerun a completed experiment merely because the results are outside the worktree.

The result-staging helpers use `git hash-object` and `git update-index --cacheinfo` to archive external paper-facing files without requiring the destination directory to be created normally.

## 17. Source-of-truth reading order for a new agent

1. `RESEARCH_STATUS.md` — current scientific state.
2. `.ai_handoff` — current operational instructions.
3. `paper/REVISION_PLAN.md` — post-Stage-F manuscript plan.
4. `studies/cnn_architecture_robustness/PROTOCOL.md` — frozen live Stage-F design.
5. `analysis/metric_sensitivity_001/REPORT.md` — latest completed methodological audit.
6. `analysis/budget_confirmation_001/REPORT.md` — Stage-D prospective result.
7. `analysis/exhaustive_robustness_001/REPORT.md` — Stage-E robustness map.
8. `analysis/checkpoint_audit/AUDIT_REPORT.md` — implementation audit.
9. `paper/main.tex` — pre-Stage-F manuscript snapshot.
10. Earlier Stage A--C materials only when tracing historical development.

## 18. One-line handoff

**Stage F training is complete and its frozen CUDA evaluation is running; do not change the Stage-F scientific code, do not inspect/interpret partial Stage-F outcomes, and after completion use the frozen analysis to determine how architecture conditions a channel-count-dependent activation-patching comparison that already survived a prospective TinyCNN test and alternative output metrics.**
