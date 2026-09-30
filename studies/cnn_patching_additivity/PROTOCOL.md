# Frozen post-hoc protocol: first-layer patching additivity

**Frozen:** 2026-09-30  
**Status:** post-hoc analysis of already trained/saved models; no new training  
**Study directory:** `studies/cnn_patching_additivity/`  
**External result root:** `%LOCALAPPDATA%\prior-templates-cnns\results\patching_additivity_001`

## 1. Scientific question

How much of the dependence of activation-patching curves on **intervention size** can be reconstructed from singleton channel effects, and how much requires a non-additive joint effect of the trained network?

Three mechanisms are kept distinct:

1. **Additive singleton contributions with cancellation.** Singleton logit changes sum, but their directions can oppose one another.
2. **Non-additivity of the model tail.** A multi-channel intervention differs from the sum of singleton interventions around the same base state.
3. **Nonlinearity of the evaluation metric.** Squared error and softmax probabilities can yield nonlinear intervention-size curves even when logits are exactly additive.

Metric curvature is not called a model interaction. A nonzero residual is not by itself interpreted as synergy, redundancy, or a unique causal mechanism.

This analysis was specified after the source outcomes were known. It improves decomposition and auditability but is not an independent confirmatory experiment.

## 2. Frozen source studies

The two source roots are read-only:

```text
%LOCALAPPDATA%\prior-templates-cnns\results\architecture_robustness_cuda_001
%LOCALAPPDATA%\prior-templates-cnns\results\anchor_specificity_cuda_001
```

Each source root must contain `training/`, `evaluation/`, and `execution_manifest.json`. The additivity evaluator checks the source manifests, frozen Git blobs, designs, completion markers, checkpoint counts, and stored evaluation files before scientific evaluation. It loads checkpoints with `torch.load(..., map_location="cpu", weights_only=True)`.

The partially completed CPU directory `architecture_robustness_001` is excluded.

## 3. Intervention and notation

For each stored model and each original matched counterfactual pair:

- `x0`: base/receiver input;
- `x1`: donor/counterfactual input;
- `h0,h1`: the 16 first-layer feature maps immediately after ReLU;
- `S`: patched channel set;
- `l0,l1,lS`: base, donor, and patched logits;
- `P = I - 11^T/C`: class-logit centering operator;
- `z = P l`.

Whole spatial maps are replaced exactly at the source studies' intervention tensor. Stored validation rankings are reused and independently recomputed from validation data; disagreement is a hard failure.

For each pair:

```text
v   = z1 - z0
d_j = z_{j} - z0
a_S = sum_{j in S} d_j
z_hat_S = z0 + a_S
r_S = z_S - z_hat_S
```

All 16 singleton interventions are newly evaluated. `ranking_effects` from the source JSON are not treated as singleton patching effects.

The primary decomposition is in centered-logit space. The same residual is also computed in raw logits to diagnose common-mode shifts.

## 4. Exact squared-error decomposition

Per pair:

```text
G_obs(S) = ||v||^2 - ||v - a_S - r_S||^2
G_add(S) = ||v||^2 - ||v - a_S||^2
```

The implementation must satisfy, in float64 accumulation,

```text
G_add(S)
= 2 v^T a_S - ||a_S||^2
= sum_j [2 v^T d_j - ||d_j||^2]
  - 2 sum_{i<j} d_i^T d_j
```

and

```text
G_obs(S) - G_add(S)
= 2 (v-a_S)^T r_S - ||r_S||^2.
```

The first sum is stored as the singleton contribution term, the pairwise-dot-product expression as the cross term, and the last expression as the exact non-additivity correction.

Cancellation is

```text
K(S) = 1 - ||sum_j d_j|| / sum_j ||d_j||.
```

If the denominator is at most `1e-12`, `K` is undefined and the frequency is reported; it is never silently set to zero.

For each singleton channel,

```text
q_j = d_j^T v / ||v||
```

when `||v|| > 1e-12`. Negative `q_j` means opposition to the base-to-donor change in centered-logit space; it is not labeled as a harmful channel. Parallel, orthogonal, magnitude, and common-mode diagnostics are computed per pair before model-level aggregation. The full 16 x 16 matrix of centered singleton cross-products, `E_n[d_i^T d_j]`, is also stored per model after computing each entry within pair.

## 5. Observed and reconstructed metrics

The stored validation-selected order is evaluated for `k=0,1,...,16`. `k=0` is the base identity and `k=16` must be the donor identity.

Centered-logit fidelity uses the same denominator for observed and reconstructed curves:

```text
F(S) = 1 - sum_n ||z_S,n-z_1,n||^2 / sum_n ||z_0,n-z_1,n||^2.
```

The additive curve substitutes `z_hat_S` for `z_S`. Sums are taken across pairs before the ratio.

For probabilities, additive probabilities are obtained by applying softmax to the reconstructed logits. The probability error reduction is relative to the donor model distribution, not a one-hot label:

```text
G_prob(S) = mean_n [ ||p0,n-p1,n||^2 - ||pS,n-p1,n||^2 ].
```

Singleton metric values are never added to reconstruct a joint metric; singleton **logit changes** are added first, then the metric is evaluated.

Primary source-study metrics:

- centered-logit fidelity;
- unnormalized probability error reduction.

Raw-logit fidelity/error reduction and probability fidelity are retained as diagnostics.

## 6. Exact reuse of source sets

The central analysis uses the validation-selected sets. The evaluator can additionally reconstruct the exact source random-set seed namespaces and the exact validation-energy-matched controls. In a full run, the launcher evaluates `selected`, `random`, and `energy` families. Energy-matched controls exist only at `k in {1,2,4,8}`.

Source metric reproduction is a hard integrity check. For selected, random-average, and energy-average quantities, newly evaluated observed metrics must agree with the source evaluation JSON within `5e-6` absolute tolerance.

## 7. Scope

### Architecture source

Primary full scope: all 16 architectures, both tasks, 100 renderer blocks, four paired initializations, and both treatments: **25,600 checkpoints**.

Mechanistic presentation/control subset:

```text
tiny_gmp
tiny_gap
plain2_w16_gmp
plain2_w16_gap
```

### Filter-bank source

Primary scope:

```text
structured_template
pixel_permuted_template
```

across the four architectures above, both tasks, 100 renderer blocks, four initializations, and both treatments: **12,800 checkpoints**.

`random_rank10` and `random_fullrank` are secondary. They are not inspected before the cost decision. After technical validation, they may be run only if the benchmark projects both:

- additional runtime <= 35% of the central architecture+primary-anchor run;
- additional model-summary storage <= 10 GiB.

This rule is based only on timing/storage, never on additivity outcomes.

## 8. Mandatory analytic and technical controls

The evaluator hard-fails on:

- source grid or evaluation incompleteness;
- frozen source Git-blob mismatch with the source execution manifest;
- stored versus recomputed validation-ranking disagreement;
- `k=0` no-op mismatch;
- `k=16` donor/full-patch mismatch;
- source metric reproduction outside tolerance;
- algebraic identity error above `5e-9`;
- mutation of cached first-layer activations.

For `k=1`, the residual must be numerically zero because the additive prediction is the same singleton intervention.

For `tiny_gmp` and `tiny_gap`, the model tail is per-channel pooling followed by a linear classifier. Whole-channel replacement therefore implies exact logit additivity up to floating-point error. The centered-logit residual must remain below `5e-5` at every intervention size. A failure stops interpretation.

Batch-size stability is checked on deterministic earliest-block checkpoints by re-evaluating at batch sizes 64 and 256. The validation driver also calls the same requested scope twice and verifies that completed per-model outputs are not rewritten.

BatchNorm architectures are always evaluated in `model.eval()` using stored running statistics. TF32 and mixed precision are disabled.

## 9. Predetermined technical validation

Before the full run, evaluate the earliest renderer block by numeric identifier for:

- four core architectures;
- both tasks;
- both treatments;
- all four initialization replicates;
- and, for the filter-bank source, both primary filter banks.

This is 64 architecture-source models and 128 primary filter-bank-source models. No model is chosen by its outcome.

The validator records runtime and JSON storage, benchmarks one all-control checkpoint per source, estimates the full-run cost, and applies the secondary-anchor cost rule before those outcomes are inspected.

## 10. Aggregation and uncertainty

The inferential unit is the **renderer block**.

1. Compute quantities per model and per pair internally.
2. Average the four initialization replicates within each renderer block.
3. Form paired release-minus-retention contrasts within that block.
4. Keep tasks separate.
5. Never pair blocks across the two source studies as if they were the same samples.

The intervention-size contrast copies the source orientation exactly:

```text
delta_k = release_default - retention_1
B = (delta_4 + delta_8)/2 - (delta_1 + delta_2)/2.
```

Intervals use a fixed renderer-block bootstrap seed `20260930` with 10,000 replicates. Primary outputs are effect estimates and intervals; no new primary null-hypothesis p-value family is introduced in this post-hoc decomposition. This avoids an unnecessary multiplicity layer. Pointwise curve intervals and simultaneous across-k reconstruction-gap bands are labeled separately.

Residual normalization is performed as an aggregate energy ratio `sum ||r||^2 / sum ||v||^2`, with small-denominator diagnostics. Unstable pairwise ratios are not averaged.

Percent “effect explained” is not reported when observed contrasts approach zero; absolute observed-minus-additive differences are primary.

## 11. Storage and resumption

All detailed outputs remain outside the repository. Per-model JSON files are written atomically. Existing complete files are skipped. The run design contains source hashes, source manifest hashes, frozen Git-blob checks, code hashes, device/batch settings, scopes, tolerances, and set families. A changed design requires a new output root.

Per-pair arrays are **off by default** for the full grid because they can dominate disk usage. The computations are nevertheless performed per pair before aggregation. `--save-pair-arrays` is available for predetermined validation/debugging and stores compressed selected-set geometry only.

No original source artifact is overwritten.

## 12. Interpretation constraints

The report is organized as:

- **Thesis:** additive reconstruction plus cancellation/cross terms and metric nonlinearity reproduce much of a curve;
- **Antithesis:** reproducible reconstruction gaps coincide with non-negligible model residuals and exact residual corrections;
- **Synthesis:** both contributions are quantified by architecture, treatment, task, and filter bank.

Tiny networks are an analytic control showing that nonlinear fidelity/probability curves do not imply non-additive model computation.

The analysis does not establish a unique causal mechanism, semantic meaning for channels, natural-image generalization, or the cause of the prior editorial rejection.