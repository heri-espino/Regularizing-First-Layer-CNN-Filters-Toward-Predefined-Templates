# Stage-F architecture robustness analysis

Status: prospectively frozen fresh-sample architecture study.

- evaluated models: **25,600 / 25,600**
- renderer blocks: **100**
- initialization replicates per block/treatment/architecture/task: **4**
- inferential unit: renderer block after averaging initialization replicates

## Primary architecture-heterogeneity tests

| Metric | F | df | partial eta^2 | p | Holm p |
|---|---:|---:|---:|---:|---:|
| centered_logit_fidelity | 77.0874 | 15, 1485 | 0.4378 | 2.4e-173 | 2.4e-173 |
| prob_error_reduction | 656.7002 | 15, 1485 | 0.8690 | 0 | 0 |

## Fresh-sample TinyCNN vs TwoLayer-form bridge

| Metric | mean difference in B | 95% interval | p | Holm p |
|---|---:|---:|---:|---:|
| centered_logit_fidelity | +0.162258 | [+0.149701, +0.174815] | 1.66e-45 | 1.66e-45 |
| prob_error_reduction | +0.889596 | [+0.862118, +0.917073] | 1.62e-82 | 3.24e-82 |

## Primary two-concepts architecture estimates

| Architecture | Metric | mean B | 95% interval |
|---|---|---:|---:|
| bn2_w16_gap | centered_logit_fidelity | -0.138167 | [-0.195965, -0.080369] |
| bn2_w16_gmp | centered_logit_fidelity | +0.016500 | [+0.002436, +0.030564] |
| bn4_w16_gap | centered_logit_fidelity | +0.144503 | [+0.117672, +0.171334] |
| bn4_w16_gmp | centered_logit_fidelity | +0.013176 | [+0.006297, +0.020056] |
| plain2_w16_gap | centered_logit_fidelity | +0.093623 | [+0.073394, +0.113851] |
| plain2_w16_gmp | centered_logit_fidelity | -0.016681 | [-0.022726, -0.010637] |
| plain2_w64_gap | centered_logit_fidelity | +0.221290 | [+0.202198, +0.240382] |
| plain2_w64_gmp | centered_logit_fidelity | -0.007205 | [-0.011272, -0.003139] |
| plain4_w16_gap | centered_logit_fidelity | +0.027709 | [+0.013847, +0.041570] |
| plain4_w16_gmp | centered_logit_fidelity | -0.016761 | [-0.021116, -0.012407] |
| plain4_w64_gap | centered_logit_fidelity | +0.051121 | [+0.040806, +0.061435] |
| plain4_w64_gmp | centered_logit_fidelity | -0.004859 | [-0.006778, -0.002939] |
| res4_w16_gap | centered_logit_fidelity | +0.044352 | [+0.027623, +0.061081] |
| res4_w16_gmp | centered_logit_fidelity | -0.017474 | [-0.021623, -0.013325] |
| tiny_gap | centered_logit_fidelity | +0.084926 | [+0.076433, +0.093419] |
| tiny_gmp | centered_logit_fidelity | +0.145577 | [+0.135166, +0.155987] |
| bn2_w16_gap | prob_error_reduction | -0.038992 | [-0.070565, -0.007419] |
| bn2_w16_gmp | prob_error_reduction | +0.012711 | [-0.012757, +0.038179] |
| bn4_w16_gap | prob_error_reduction | +0.075703 | [+0.053153, +0.098254] |
| bn4_w16_gmp | prob_error_reduction | -0.002345 | [-0.016269, +0.011579] |
| plain2_w16_gap | prob_error_reduction | +0.334773 | [+0.320702, +0.348844] |
| plain2_w16_gmp | prob_error_reduction | -0.058084 | [-0.075746, -0.040421] |
| plain2_w64_gap | prob_error_reduction | +0.324743 | [+0.304542, +0.344944] |
| plain2_w64_gmp | prob_error_reduction | -0.002051 | [-0.015212, +0.011109] |
| plain4_w16_gap | prob_error_reduction | +0.116007 | [+0.099200, +0.132815] |
| plain4_w16_gmp | prob_error_reduction | -0.056135 | [-0.067538, -0.044732] |
| plain4_w64_gap | prob_error_reduction | +0.001309 | [-0.014991, +0.017610] |
| plain4_w64_gmp | prob_error_reduction | -0.023797 | [-0.028169, -0.019425] |
| res4_w16_gap | prob_error_reduction | +0.097401 | [+0.075570, +0.119232] |
| res4_w16_gmp | prob_error_reduction | -0.044802 | [-0.055378, -0.034226] |
| tiny_gap | prob_error_reduction | +0.094358 | [+0.090145, +0.098571] |
| tiny_gmp | prob_error_reduction | +0.831512 | [+0.812226, +0.850798] |

## Integrity

- maximum full-patch logit identity error: **0**
- maximum no-op logit identity error: **0**

Pooling, depth, width, residual, BatchNorm, single_shape, denominator-scale, initialization-dispersion, and control contrasts are retained in the CSV outputs. No binary pass/fail rule is defined.
