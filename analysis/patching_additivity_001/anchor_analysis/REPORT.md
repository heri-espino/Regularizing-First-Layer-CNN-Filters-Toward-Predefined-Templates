# Patching additivity report

Status: post-hoc analysis of previously trained checkpoints; no new training.

- source study: **anchor**
- evaluated checkpoint files: **12,800**
- renderer blocks represented: **100**
- maximum full-patch logit identity error: **0**
- maximum no-op logit identity error: **0**

## Central decomposition

For each matched pair, the centered-logit change is decomposed as `observed = additive singleton sum + residual`. All singleton geometry, cancellation, cross terms, and residual corrections are computed per pair before aggregation.

The squared-error decomposition is reported through the individual contribution sum, the pairwise cross-term correction, and the exact non-additivity correction. Curvature of fidelity/probability curves is therefore not treated as evidence of model non-additivity by itself.

## Release-minus-retention intervention-size contrast B

`B = mean(delta at k=4,8) - mean(delta at k=1,2)`, where delta is release minus retention. Intervals are renderer-block bootstrap intervals after averaging initialization replicates within each block.

| Task | Architecture | Anchor | Metric | Curve | Mean B | 95% block-bootstrap CI |
|---|---|---|---|---|---:|---:|
| single_shape | plain2_w16_gap | pixel_permuted_template | centered_logit_fidelity | observed | +0.019214 | [+0.010076, +0.028362] |
| single_shape | plain2_w16_gap | structured_template | centered_logit_fidelity | observed | +0.037548 | [+0.018122, +0.056331] |
| single_shape | plain2_w16_gmp | pixel_permuted_template | centered_logit_fidelity | observed | +0.010707 | [+0.006687, +0.014587] |
| single_shape | plain2_w16_gmp | structured_template | centered_logit_fidelity | observed | +0.051860 | [+0.048456, +0.055250] |
| single_shape | tiny_gap | pixel_permuted_template | centered_logit_fidelity | observed | -0.034684 | [-0.039525, -0.029865] |
| single_shape | tiny_gap | structured_template | centered_logit_fidelity | observed | -0.018431 | [-0.022474, -0.014335] |
| single_shape | tiny_gmp | pixel_permuted_template | centered_logit_fidelity | observed | +0.014886 | [+0.011260, +0.018529] |
| single_shape | tiny_gmp | structured_template | centered_logit_fidelity | observed | +0.061235 | [+0.056438, +0.066186] |
| two_concepts | plain2_w16_gap | pixel_permuted_template | centered_logit_fidelity | observed | +0.003535 | [-0.007819, +0.014597] |
| two_concepts | plain2_w16_gap | structured_template | centered_logit_fidelity | observed | +0.094628 | [+0.074333, +0.113502] |
| two_concepts | plain2_w16_gmp | pixel_permuted_template | centered_logit_fidelity | observed | +0.020411 | [+0.015764, +0.024893] |
| two_concepts | plain2_w16_gmp | structured_template | centered_logit_fidelity | observed | -0.024120 | [-0.029490, -0.018851] |
| two_concepts | tiny_gap | pixel_permuted_template | centered_logit_fidelity | observed | +0.014404 | [+0.003747, +0.024888] |
| two_concepts | tiny_gap | structured_template | centered_logit_fidelity | observed | +0.091308 | [+0.082757, +0.099779] |
| two_concepts | tiny_gmp | pixel_permuted_template | centered_logit_fidelity | observed | +0.042454 | [+0.037684, +0.047311] |
| two_concepts | tiny_gmp | structured_template | centered_logit_fidelity | observed | +0.148690 | [+0.140027, +0.157426] |
| single_shape | plain2_w16_gap | pixel_permuted_template | centered_logit_fidelity | additive | +0.021277 | [+0.012022, +0.030593] |
| single_shape | plain2_w16_gap | structured_template | centered_logit_fidelity | additive | +0.050265 | [+0.029828, +0.070468] |
| single_shape | plain2_w16_gmp | pixel_permuted_template | centered_logit_fidelity | additive | +0.012887 | [+0.009214, +0.016547] |
| single_shape | plain2_w16_gmp | structured_template | centered_logit_fidelity | additive | +0.026991 | [+0.023244, +0.030835] |
| single_shape | tiny_gap | pixel_permuted_template | centered_logit_fidelity | additive | -0.034684 | [-0.039595, -0.029788] |
| single_shape | tiny_gap | structured_template | centered_logit_fidelity | additive | -0.018431 | [-0.022433, -0.014350] |
| single_shape | tiny_gmp | pixel_permuted_template | centered_logit_fidelity | additive | +0.014886 | [+0.011200, +0.018577] |
| single_shape | tiny_gmp | structured_template | centered_logit_fidelity | additive | +0.061235 | [+0.056360, +0.066211] |
| two_concepts | plain2_w16_gap | pixel_permuted_template | centered_logit_fidelity | additive | -0.004213 | [-0.015396, +0.007187] |
| two_concepts | plain2_w16_gap | structured_template | centered_logit_fidelity | additive | +0.091608 | [+0.071696, +0.111030] |
| two_concepts | plain2_w16_gmp | pixel_permuted_template | centered_logit_fidelity | additive | +0.012669 | [+0.008578, +0.016756] |
| two_concepts | plain2_w16_gmp | structured_template | centered_logit_fidelity | additive | -0.037900 | [-0.042273, -0.033591] |
| two_concepts | tiny_gap | pixel_permuted_template | centered_logit_fidelity | additive | +0.014404 | [+0.003783, +0.024434] |
| two_concepts | tiny_gap | structured_template | centered_logit_fidelity | additive | +0.091308 | [+0.082913, +0.100203] |
| two_concepts | tiny_gmp | pixel_permuted_template | centered_logit_fidelity | additive | +0.042454 | [+0.037725, +0.047197] |
| two_concepts | tiny_gmp | structured_template | centered_logit_fidelity | additive | +0.148690 | [+0.139866, +0.157497] |
| single_shape | plain2_w16_gap | pixel_permuted_template | prob_error_reduction | observed | +0.162947 | [+0.151416, +0.174401] |
| single_shape | plain2_w16_gap | structured_template | prob_error_reduction | observed | +0.208723 | [+0.191782, +0.225313] |
| single_shape | plain2_w16_gmp | pixel_permuted_template | prob_error_reduction | observed | -0.017512 | [-0.026924, -0.008197] |
| single_shape | plain2_w16_gmp | structured_template | prob_error_reduction | observed | -0.015083 | [-0.024559, -0.005875] |
| single_shape | tiny_gap | pixel_permuted_template | prob_error_reduction | observed | +0.177355 | [+0.171906, +0.182656] |
| single_shape | tiny_gap | structured_template | prob_error_reduction | observed | +0.257995 | [+0.250163, +0.266024] |
| single_shape | tiny_gmp | pixel_permuted_template | prob_error_reduction | observed | +0.304880 | [+0.297648, +0.312116] |
| single_shape | tiny_gmp | structured_template | prob_error_reduction | observed | +0.352425 | [+0.342128, +0.363035] |
| two_concepts | plain2_w16_gap | pixel_permuted_template | prob_error_reduction | observed | +0.315536 | [+0.300561, +0.330579] |
| two_concepts | plain2_w16_gap | structured_template | prob_error_reduction | observed | +0.336104 | [+0.320442, +0.351690] |
| two_concepts | plain2_w16_gmp | pixel_permuted_template | prob_error_reduction | observed | +0.014231 | [+0.001874, +0.026284] |
| two_concepts | plain2_w16_gmp | structured_template | prob_error_reduction | observed | -0.066437 | [-0.082140, -0.050907] |
| two_concepts | tiny_gap | pixel_permuted_template | prob_error_reduction | observed | +0.051025 | [+0.048106, +0.053976] |
| two_concepts | tiny_gap | structured_template | prob_error_reduction | observed | +0.094105 | [+0.090543, +0.097664] |
| two_concepts | tiny_gmp | pixel_permuted_template | prob_error_reduction | observed | +0.645288 | [+0.632412, +0.658088] |
| two_concepts | tiny_gmp | structured_template | prob_error_reduction | observed | +0.844818 | [+0.827439, +0.862291] |
| single_shape | plain2_w16_gap | pixel_permuted_template | prob_error_reduction | additive | +0.166431 | [+0.155226, +0.177671] |
| single_shape | plain2_w16_gap | structured_template | prob_error_reduction | additive | +0.184825 | [+0.166579, +0.202992] |
| single_shape | plain2_w16_gmp | pixel_permuted_template | prob_error_reduction | additive | -0.062229 | [-0.069772, -0.054504] |
| single_shape | plain2_w16_gmp | structured_template | prob_error_reduction | additive | -0.053859 | [-0.063137, -0.044148] |
| single_shape | tiny_gap | pixel_permuted_template | prob_error_reduction | additive | +0.177355 | [+0.172036, +0.182699] |
| single_shape | tiny_gap | structured_template | prob_error_reduction | additive | +0.257995 | [+0.249853, +0.266081] |
| single_shape | tiny_gmp | pixel_permuted_template | prob_error_reduction | additive | +0.304880 | [+0.297760, +0.311934] |
| single_shape | tiny_gmp | structured_template | prob_error_reduction | additive | +0.352425 | [+0.342485, +0.362644] |
| two_concepts | plain2_w16_gap | pixel_permuted_template | prob_error_reduction | additive | +0.294361 | [+0.279580, +0.309578] |
| two_concepts | plain2_w16_gap | structured_template | prob_error_reduction | additive | +0.321282 | [+0.305927, +0.336898] |
| two_concepts | plain2_w16_gmp | pixel_permuted_template | prob_error_reduction | additive | -0.032130 | [-0.040629, -0.023648] |
| two_concepts | plain2_w16_gmp | structured_template | prob_error_reduction | additive | -0.137462 | [-0.149297, -0.125756] |
| two_concepts | tiny_gap | pixel_permuted_template | prob_error_reduction | additive | +0.051025 | [+0.048177, +0.053997] |
| two_concepts | tiny_gap | structured_template | prob_error_reduction | additive | +0.094105 | [+0.090580, +0.097754] |
| two_concepts | tiny_gmp | pixel_permuted_template | prob_error_reduction | additive | +0.645288 | [+0.632407, +0.658243] |
| two_concepts | tiny_gmp | structured_template | prob_error_reduction | additive | +0.844818 | [+0.827416, +0.861839] |

## Observed minus additive reconstruction

Positive values mean the observed metric is larger than the additive reconstruction; negative values mean it is smaller. For centered logits, the corresponding residual and exact squared-error correction are reported separately.

## Structured versus pixel-permuted filter banks

The table below compares the structured and pixel-permuted banks on B after averaging the four architectures within each renderer block.

| Task | Metric | Curve | Mean structured-pixel-permuted B | 95% block-bootstrap CI |
|---|---|---|---:|---:|
| single_shape | centered_logit_fidelity | additive | +0.026424 | [+0.020383, +0.032537] |
| single_shape | centered_logit_fidelity | observed | +0.030522 | [+0.024821, +0.036215] |
| single_shape | prob_error_reduction | additive | +0.038737 | [+0.031458, +0.045869] |
| single_shape | prob_error_reduction | observed | +0.044097 | [+0.037337, +0.050964] |
| two_concepts | centered_logit_fidelity | additive | +0.057098 | [+0.050999, +0.063501] |
| two_concepts | centered_logit_fidelity | observed | +0.057426 | [+0.051433, +0.063614] |
| two_concepts | prob_error_reduction | additive | +0.041050 | [+0.033339, +0.048832] |
| two_concepts | prob_error_reduction | observed | +0.045628 | [+0.037148, +0.053742] |

## Interpretation frame

- **Additive account:** agreement between observed and reconstructed curves, together with nonzero cancellation/cross terms and small residual energy, supports a superposition-plus-metric explanation.
- **Non-additive account:** reproducible reconstruction gaps accompanied by non-negligible residual energy and exact residual correction identify where downstream computation departs from the singleton superposition model.
- **Combined account:** both can coexist and should be quantified by architecture, treatment, task, and filter bank rather than collapsed into a single mechanism label.

## Limits

This analysis is post-hoc and reuses the same models and matched counterfactual pairs as the source studies. It does not provide an independent confirmatory sample, identify a unique semantic mechanism, or establish natural-image generalization. Tiny architectures are an analytic implementation control: because their tail is pooling followed by a linear classifier, whole-channel patching should be additive in logits up to numerical error even when fidelity or probability curves are nonlinear.
