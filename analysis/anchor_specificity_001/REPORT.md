# Anchor-specificity analysis

Status: prospectively frozen fresh-sample specificity experiment.

- evaluated models: **25,600 / 25,600**
- renderer blocks: **100**
- init/anchor replicates averaged within block: **4**
- primary task: **two_concepts**

## Primary spatial-template specificity

| Metric | mean structured-pixelperm B | 95% CI | sign-flip Holm p | equivalence margin | 90% CI | equivalence Holm p |
|---|---:|---:|---:|---:|---:|---:|
| centered_logit_fidelity | +0.057426 | [+0.051165, +0.063686] | 2e-05 | 0.017040 | [+0.052187, +0.062664] | 1 |
| prob_error_reduction | +0.045628 | [+0.037281, +0.053975] | 2e-05 | 0.065936 | [+0.038643, +0.052613] | 5.03e-06 |

## Spatial-structure x architecture interaction

| Metric | F | partial eta^2 | permutation p | Holm p |
|---|---:|---:|---:|---:|
| centered_logit_fidelity | 91.7943 | 0.4811 | 1e-05 | 2e-05 |
| prob_error_reduction | 157.6951 | 0.6143 | 1e-05 | 2e-05 |

## Prespecified random-channel diagnostic

| Metric | mean structured-pixelperm random-B | 95% CI | sign-flip p |
|---|---:|---:|---:|
| centered_logit_fidelity | +0.005709 | [+0.003919, +0.007498] | 1e-05 |
| prob_error_reduction | +0.020068 | [+0.017225, +0.022911] | 1e-05 |

## Integrity

- maximum full-patch logit error: **0**
- maximum no-op logit error: **0**
- maximum pixel-permuted Gram error: **6.66134e-16**

Interpretation rule: a nonzero difference test supports spatial-structure sensitivity; equivalence requires the frozen TOST margin; if neither criterion is met, the result is inconclusive rather than evidence of no difference.
