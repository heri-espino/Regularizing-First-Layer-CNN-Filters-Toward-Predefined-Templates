# Patching metric-sensitivity analysis

Statistical status: frozen post hoc robustness analysis of saved Stage-D/E checkpoints. No model was retrained and no stored channel ranking was changed.

- protocol commit: 70450548a5c9feb4a2334eaef7f56707bb2c858f
- protocol Git blob: 670f8769348d5589b5fe0ae6d9582d6133bf6b86
- analysis Git blob: 1b99ceefce77b063da7cdf495384b93e4d161bd4
- Stage-D checkpoint evaluations: **80 / 80**
- Stage-E checkpoint evaluations: **1200 / 1200**

## Stage-D primary metric-sensitivity setting

Setting: two_concepts / TinyCNN / contrast, with the original release-minus-retention treatment pairing and B contrast.

| Metric | mean B | 95% interval | p | Holm p (2 metrics) |
|---|---:|---:|---:|---:|
| centered_logit_fidelity | +0.178881 | [+0.127268, +0.230494] | 6.95e-07 | 6.95e-07 |
| prob_error_reduction | +0.894411 | [+0.786301, +1.002522] | 4.3e-13 | 8.59e-13 |

### Pointwise release-minus-retention contrasts

| Metric | k | mean delta | 95% interval |
|---|---:|---:|---:|
| centered_logit_fidelity | 1 | -0.211342 | [-0.278993, -0.143691] |
| centered_logit_fidelity | 2 | -0.174516 | [-0.220782, -0.128250] |
| centered_logit_fidelity | 4 | -0.034049 | [-0.049388, -0.018710] |
| centered_logit_fidelity | 8 | +0.005954 | [+0.002533, +0.009374] |
| prob_error_reduction | 1 | -0.229423 | [-0.330326, -0.128520] |
| prob_error_reduction | 2 | +0.044926 | [-0.114430, +0.204281] |
| prob_error_reduction | 4 | +0.754287 | [+0.703273, +0.805301] |
| prob_error_reduction | 8 | +0.850038 | [+0.829147, +0.870929] |

## Stage-D input-effect normalization diagnostics

These are release-minus-retention differences in the model-level base-to-counterfactual squared-error scale used as the denominator of normalized metrics.

| Architecture | Input-effect scale | mean delta | 95% interval | p |
|---|---|---:|---:|---:|
| TinyCNN | prob_input_effect_mpp | +0.848558 | [+0.826701, +0.870416] | 1.28e-25 |
| TinyCNN | centered_logit_input_effect_mpp | +126.537 | [+120.845, +132.229] | 4.83e-21 |
| TinyCNN | raw_logit_input_effect_mpp | +127.726 | [+121.909, +133.543] | 6.1e-21 |
| TwoLayerCNN | prob_input_effect_mpp | +0.0620619 | [+0.0532861, +0.0708377] | 6.95e-12 |
| TwoLayerCNN | centered_logit_input_effect_mpp | +211.368 | [+200.319, +222.417] | 8.15e-20 |
| TwoLayerCNN | raw_logit_input_effect_mpp | +215.305 | [+204.104, +226.507] | 7.46e-20 |

## Stage-E default-release extension

Secondary B contrasts for release_default - retention_1 under the original contrast ranking.

| Task | Architecture | Metric | mean B | 95% interval | Holm p within Stage-E setting |
|---|---|---|---:|---:|---:|
| single_shape | TinyCNN | centered_logit_fidelity | +0.056604 | [+0.043908, +0.069299] | 2.71e-11 |
| single_shape | TinyCNN | prob_error_reduction | +0.337472 | [+0.304218, +0.370727] | 2.74e-25 |
| single_shape | TwoLayerCNN | centered_logit_fidelity | +0.057000 | [+0.048479, +0.065522] | 2.32e-17 |
| single_shape | TwoLayerCNN | prob_error_reduction | -0.016223 | [-0.041560, +0.009114] | 0.817 |
| two_concepts | TinyCNN | centered_logit_fidelity | +0.134268 | [+0.108511, +0.160025] | 1.68e-13 |
| two_concepts | TinyCNN | prob_error_reduction | +0.802385 | [+0.744980, +0.859791] | 2.88e-31 |
| two_concepts | TwoLayerCNN | centered_logit_fidelity | -0.019527 | [-0.036893, -0.002161] | 0.085 |
| two_concepts | TwoLayerCNN | prob_error_reduction | -0.054970 | [-0.110114, +0.000174] | 0.159 |

## Integrity

- maximum absolute difference between recomputed and stored probability fidelity: **1.24291e-07**
- maximum full-patch logit identity error: **0**
- maximum no-op logit identity error: **0**

Raw-logit fidelity, alternative rankings, architecture results, all Stage-E profiles, full k curves, and block-level values are retained in the CSV files. No binary pass/fail decision is defined by the frozen protocol.
