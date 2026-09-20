# Frozen post hoc architecture-diagnostics analysis

Protocol frozen: 2026-09-20

## Evidential status

This analysis is performed after the complete architecture-robustness outcomes are known. In addition, aggregate random-channel diagnostic means were inspected during referee-style review before this protocol was written.

Therefore this analysis is **post hoc and diagnostic**. It must never be described as prospective confirmation.

Its purpose is to test plausible alternative explanations of the already-observed architecture result using existing Stage-F checkpoints/evaluations only. No model retraining occurs.

Manuscript-facing terminology: **post hoc architecture diagnostics**.

## Inputs

Read only the frozen completed architecture-study root and archived paper-facing tables.

Expected external root:

`%LOCALAPPDATA%\prior-templates-cnns\results\architecture_robustness_cuda_001`

The analysis must verify the completed training/evaluation manifests and source hashes before reading outcomes.

Primary task for diagnostics: `two_concepts`.

Primary metrics:

- centered-logit fidelity;
- probability error reduction.

## Diagnostic 1: sphericity-robust architecture omnibus

Reconstruct one block-averaged selected-channel B value for each:

- renderer block (100);
- architecture (16);
- primary metric.

For each metric report the original repeated-measures F statistic plus:

### A. Greenhouse--Geisser correction

Estimate the within-block covariance matrix across the 16 architecture conditions and compute Greenhouse--Geisser epsilon.

Report:

- epsilon;
- corrected numerator and denominator degrees of freedom;
- F statistic;
- corrected upper-tail p value.

### B. Within-block permutation omnibus

Use the same repeated-measures architecture F statistic.

Null generation:

- independently permute the 16 architecture labels within each renderer block;
- fixed RNG seed;
- 100,000 permutations;
- p value with +1 correction.

The two metric permutation p values form one Holm-adjusted family.

### C. Friedman test

Report the Friedman chi-square statistic and p value as a rank-based sensitivity check.

These tests are robustness checks of the already-known architecture heterogeneity, not new independent evidence.

## Diagnostic 2: ranking-independence using random channel orders

For each block/architecture/metric:

1. compute treatment-difference curves separately for each of the eight random channel orders;
2. average the eight random-order metric values within treatment at each k;
3. compute random-channel (Delta(k));
4. compute
   [
   B_{mathrm{random}}
   =
   [Delta(4)+Delta(8)]/2
   -
   [Delta(1)+Delta(2)]/2.
   ]
5. average init replicates within renderer block before inference.

Report across architectures:

- mean and 95% CI of selected B;
- mean and 95% CI of random-channel B;
- selected-minus-random B;
- Spearman correlation across the 16 architecture means between selected B and random B;
- within-block permutation omnibus for random B;
- within-block permutation omnibus for selected-minus-random B;
- fresh TinyGMP minus Plain2-W16-GMP bridge for random B.

This diagnostic asks whether architecture dependence is fundamentally tied to the validation-derived channel ranking.

It does **not** turn the random controls into a new prospective primary endpoint.

## Diagnostic 3: structural-versus-functional separation

From `model_endpoints.csv`, calculate for each block/architecture after averaging init replicates:

[
Delta A_{b,a}
=
A^{mathrm{retention}}_{b,a}
-
A^{mathrm{release}}_{b,a}.
]

Join with selected-channel B for the same block/architecture.

Report:

### A. Architecture-level summary

For each architecture:

- mean (Delta A) and 95% CI;
- mean B and 95% CI for each primary metric.

Create a scatter plot of architecture-mean (Delta A) versus mean B with architecture labels.

Report Spearman rho across the 16 architecture means as a descriptive statistic only.

### B. Within-architecture association

For each architecture separately, compute Spearman correlation across the 100 renderer blocks between (Delta A_{b,a}) and B.

Report all 16 estimates and bootstrap 95% intervals. Holm-adjust p values only if p values are included; effect sizes/intervals are preferred.

### C. High-retention / heterogeneous-function statement

Report the range of mean (Delta A) across architectures and the range/sign of mean B. The manuscript may use this as direct evidence that large structural-retention differences can coexist with heterogeneous functional patching contrasts.

Do not interpret correlation as causal mediation.

## Diagnostic 4: exact architecture definitions

Produce a machine-generated appendix table from `ARCH_SPECS` containing:

- architecture ID;
- total convolution depth;
- downstream width;
- connectivity;
- downstream BatchNorm;
- pooling;
- parameter count.

This addresses manuscript reconstructability and must be included even if no other diagnostic changes the conclusions.

## Output directory

External analysis root:

`%LOCALAPPDATA%\prior-templates-cnns\results\architecture_posthoc_diagnostics_001`

Paper-facing archive target:

`analysis/architecture_posthoc_diagnostics_001/`

Required outputs:

- `REPORT.md`
- `selected_B_per_block.csv`
- `random_B_per_block.csv`
- `selected_random_summary.csv`
- `omnibus_robustness.csv`
- `alignment_B_per_block.csv`
- `alignment_B_architecture_summary.csv`
- `alignment_B_correlations.csv`
- `architecture_definitions.csv`
- `execution_manifest.json`

## Interpretation boundary

This is an outcome-informed robustness analysis. It can strengthen or weaken interpretations of the completed architecture study, but it cannot be used to claim that its diagnostics were prespecified before the architecture outcomes were known.
