# Post hoc architecture diagnostics

Status: outcome-informed diagnostic analysis; not prospective confirmation.

## Sphericity-robust selected-channel architecture omnibus

| Metric | F | GG epsilon | GG p | permutation p | Holm permutation p | Friedman p |
|---|---:|---:|---:|---:|---:|---:|
| centered_logit_fidelity | 77.0874 | 0.1861 | 1.56e-34 | 1e-05 | 2e-05 | 3.52e-146 |
| prob_error_reduction | 656.7002 | 0.5973 | 0 | 1e-05 | 2e-05 | 7.79e-200 |

## Ranking-independence diagnostic: random channel orders

| Metric | random-B architecture permutation p | Holm p | selected/random architecture-mean Spearman rho |
|---|---:|---:|---:|
| centered_logit_fidelity | 1e-05 | 2e-05 | +0.256 |
| prob_error_reduction | 1e-05 | 2e-05 | +0.724 |

## Random-channel TinyGMP vs Plain2-GMP bridge

| Metric | mean difference in random B | 95% CI | Holm p |
|---|---:|---:|---:|
| centered_logit_fidelity | +0.002765 | [+0.000014, +0.005515] | 0.0488 |
| prob_error_reduction | +0.319871 | [+0.312788, +0.326953] | 2.76e-96 |

## Structural-versus-functional diagnostic

Architecture-level alignment/B summaries and within-architecture correlations are in the CSV outputs and alignment_B_scatter.pdf. Correlations are descriptive and are not interpreted as mediation.

## Integrity

- evaluated model JSONs: **25,600**
- maximum full-patch logit error: **0**
- maximum no-op logit error: **0**
