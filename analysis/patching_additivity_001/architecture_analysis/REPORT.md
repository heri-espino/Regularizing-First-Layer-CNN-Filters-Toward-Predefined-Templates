# Patching additivity report

Status: post-hoc analysis of previously trained checkpoints; no new training.

- source study: **architecture**
- evaluated checkpoint files: **25,600**
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
| single_shape | bn2_w16_gap | — | centered_logit_fidelity | observed | -0.270125 | [-0.352544, -0.186589] |
| single_shape | bn2_w16_gmp | — | centered_logit_fidelity | observed | +0.066767 | [+0.058073, +0.075317] |
| single_shape | bn4_w16_gap | — | centered_logit_fidelity | observed | +0.377254 | [+0.284079, +0.471758] |
| single_shape | bn4_w16_gmp | — | centered_logit_fidelity | observed | +0.002785 | [-0.001752, +0.007121] |
| single_shape | plain2_w16_gap | — | centered_logit_fidelity | observed | +0.044875 | [+0.027955, +0.062353] |
| single_shape | plain2_w16_gmp | — | centered_logit_fidelity | observed | +0.052514 | [+0.048867, +0.056138] |
| single_shape | plain2_w64_gap | — | centered_logit_fidelity | observed | +0.043184 | [+0.031895, +0.054880] |
| single_shape | plain2_w64_gmp | — | centered_logit_fidelity | observed | +0.032065 | [+0.030057, +0.034060] |
| single_shape | plain4_w16_gap | — | centered_logit_fidelity | observed | +0.155123 | [+0.125219, +0.184962] |
| single_shape | plain4_w16_gmp | — | centered_logit_fidelity | observed | +0.014343 | [+0.011956, +0.016789] |
| single_shape | plain4_w64_gap | — | centered_logit_fidelity | observed | +0.080766 | [+0.061721, +0.099610] |
| single_shape | plain4_w64_gmp | — | centered_logit_fidelity | observed | +0.002140 | [+0.001579, +0.002714] |
| single_shape | res4_w16_gap | — | centered_logit_fidelity | observed | +0.153869 | [+0.130282, +0.177872] |
| single_shape | res4_w16_gmp | — | centered_logit_fidelity | observed | +0.013942 | [+0.011768, +0.016124] |
| single_shape | tiny_gap | — | centered_logit_fidelity | observed | -0.013547 | [-0.017526, -0.009546] |
| single_shape | tiny_gmp | — | centered_logit_fidelity | observed | +0.056896 | [+0.052111, +0.061441] |
| two_concepts | bn2_w16_gap | — | centered_logit_fidelity | observed | -0.138167 | [-0.193944, -0.080892] |
| two_concepts | bn2_w16_gmp | — | centered_logit_fidelity | observed | +0.016500 | [+0.002479, +0.030306] |
| two_concepts | bn4_w16_gap | — | centered_logit_fidelity | observed | +0.144503 | [+0.118154, +0.171383] |
| two_concepts | bn4_w16_gmp | — | centered_logit_fidelity | observed | +0.013176 | [+0.006506, +0.019896] |
| two_concepts | plain2_w16_gap | — | centered_logit_fidelity | observed | +0.093623 | [+0.073987, +0.113805] |
| two_concepts | plain2_w16_gmp | — | centered_logit_fidelity | observed | -0.016681 | [-0.022476, -0.010689] |
| two_concepts | plain2_w64_gap | — | centered_logit_fidelity | observed | +0.221290 | [+0.201841, +0.239724] |
| two_concepts | plain2_w64_gmp | — | centered_logit_fidelity | observed | -0.007205 | [-0.011185, -0.003163] |
| two_concepts | plain4_w16_gap | — | centered_logit_fidelity | observed | +0.027709 | [+0.013890, +0.040989] |
| two_concepts | plain4_w16_gmp | — | centered_logit_fidelity | observed | -0.016761 | [-0.021029, -0.012349] |
| two_concepts | plain4_w64_gap | — | centered_logit_fidelity | observed | +0.051121 | [+0.040961, +0.061715] |
| two_concepts | plain4_w64_gmp | — | centered_logit_fidelity | observed | -0.004859 | [-0.006642, -0.002920] |
| two_concepts | res4_w16_gap | — | centered_logit_fidelity | observed | +0.044352 | [+0.028035, +0.061060] |
| two_concepts | res4_w16_gmp | — | centered_logit_fidelity | observed | -0.017474 | [-0.021582, -0.013476] |
| two_concepts | tiny_gap | — | centered_logit_fidelity | observed | +0.084926 | [+0.076570, +0.093387] |
| two_concepts | tiny_gmp | — | centered_logit_fidelity | observed | +0.145577 | [+0.135526, +0.155741] |
| single_shape | bn2_w16_gap | — | centered_logit_fidelity | additive | +0.349549 | [+0.153591, +0.544306] |
| single_shape | bn2_w16_gmp | — | centered_logit_fidelity | additive | +0.343618 | [+0.317756, +0.370057] |
| single_shape | bn4_w16_gap | — | centered_logit_fidelity | additive | +1.649098 | [+1.432909, +1.862568] |
| single_shape | bn4_w16_gmp | — | centered_logit_fidelity | additive | +0.024176 | [+0.015562, +0.032212] |
| single_shape | plain2_w16_gap | — | centered_logit_fidelity | additive | +0.057436 | [+0.040173, +0.074623] |
| single_shape | plain2_w16_gmp | — | centered_logit_fidelity | additive | +0.028018 | [+0.023959, +0.031825] |
| single_shape | plain2_w64_gap | — | centered_logit_fidelity | additive | +0.044580 | [+0.034051, +0.055662] |
| single_shape | plain2_w64_gmp | — | centered_logit_fidelity | additive | +0.026418 | [+0.024449, +0.028404] |
| single_shape | plain4_w16_gap | — | centered_logit_fidelity | additive | +0.117562 | [+0.093923, +0.141288] |
| single_shape | plain4_w16_gmp | — | centered_logit_fidelity | additive | +0.006727 | [+0.003805, +0.009532] |
| single_shape | plain4_w64_gap | — | centered_logit_fidelity | additive | +0.112608 | [+0.091159, +0.134652] |
| single_shape | plain4_w64_gmp | — | centered_logit_fidelity | additive | +0.001117 | [+0.000563, +0.001672] |
| single_shape | res4_w16_gap | — | centered_logit_fidelity | additive | +0.135691 | [+0.115222, +0.157254] |
| single_shape | res4_w16_gmp | — | centered_logit_fidelity | additive | +0.009559 | [+0.007559, +0.011476] |
| single_shape | tiny_gap | — | centered_logit_fidelity | additive | -0.013547 | [-0.017517, -0.009508] |
| single_shape | tiny_gmp | — | centered_logit_fidelity | additive | +0.056896 | [+0.052367, +0.061520] |
| two_concepts | bn2_w16_gap | — | centered_logit_fidelity | additive | +0.041774 | [-0.013551, +0.094151] |
| two_concepts | bn2_w16_gmp | — | centered_logit_fidelity | additive | +0.152819 | [+0.118175, +0.186992] |
| two_concepts | bn4_w16_gap | — | centered_logit_fidelity | additive | +0.096738 | [+0.072429, +0.121367] |
| two_concepts | bn4_w16_gmp | — | centered_logit_fidelity | additive | +0.011705 | [+0.005270, +0.018037] |
| two_concepts | plain2_w16_gap | — | centered_logit_fidelity | additive | +0.090328 | [+0.069989, +0.111408] |
| two_concepts | plain2_w16_gmp | — | centered_logit_fidelity | additive | -0.034202 | [-0.039240, -0.029200] |
| two_concepts | plain2_w64_gap | — | centered_logit_fidelity | additive | +0.236883 | [+0.216938, +0.255792] |
| two_concepts | plain2_w64_gmp | — | centered_logit_fidelity | additive | -0.025004 | [-0.028624, -0.021516] |
| two_concepts | plain4_w16_gap | — | centered_logit_fidelity | additive | +0.018664 | [+0.004512, +0.032545] |
| two_concepts | plain4_w16_gmp | — | centered_logit_fidelity | additive | -0.020150 | [-0.024006, -0.016440] |
| two_concepts | plain4_w64_gap | — | centered_logit_fidelity | additive | +0.063740 | [+0.054342, +0.073099] |
| two_concepts | plain4_w64_gmp | — | centered_logit_fidelity | additive | -0.008124 | [-0.009992, -0.006097] |
| two_concepts | res4_w16_gap | — | centered_logit_fidelity | additive | +0.034013 | [+0.018593, +0.050017] |
| two_concepts | res4_w16_gmp | — | centered_logit_fidelity | additive | -0.017166 | [-0.020606, -0.013817] |
| two_concepts | tiny_gap | — | centered_logit_fidelity | additive | +0.084926 | [+0.076590, +0.093288] |
| two_concepts | tiny_gmp | — | centered_logit_fidelity | additive | +0.145577 | [+0.135387, +0.155902] |
| single_shape | bn2_w16_gap | — | prob_error_reduction | observed | -0.033998 | [-0.056700, -0.010659] |
| single_shape | bn2_w16_gmp | — | prob_error_reduction | observed | +0.115517 | [+0.096742, +0.134200] |
| single_shape | bn4_w16_gap | — | prob_error_reduction | observed | +0.038335 | [+0.016049, +0.061136] |
| single_shape | bn4_w16_gmp | — | prob_error_reduction | observed | +0.010161 | [+0.002268, +0.017987] |
| single_shape | plain2_w16_gap | — | prob_error_reduction | observed | +0.202605 | [+0.186658, +0.218121] |
| single_shape | plain2_w16_gmp | — | prob_error_reduction | observed | -0.020305 | [-0.030152, -0.010367] |
| single_shape | plain2_w64_gap | — | prob_error_reduction | observed | +0.152512 | [+0.134997, +0.169437] |
| single_shape | plain2_w64_gmp | — | prob_error_reduction | observed | -0.046304 | [-0.052226, -0.040276] |
| single_shape | plain4_w16_gap | — | prob_error_reduction | observed | +0.147495 | [+0.127046, +0.168044] |
| single_shape | plain4_w16_gmp | — | prob_error_reduction | observed | +0.011543 | [+0.005825, +0.017211] |
| single_shape | plain4_w64_gap | — | prob_error_reduction | observed | +0.092254 | [+0.072686, +0.111466] |
| single_shape | plain4_w64_gmp | — | prob_error_reduction | observed | +0.001468 | [-0.000349, +0.003290] |
| single_shape | res4_w16_gap | — | prob_error_reduction | observed | +0.124088 | [+0.103802, +0.143548] |
| single_shape | res4_w16_gmp | — | prob_error_reduction | observed | +0.019399 | [+0.014276, +0.024642] |
| single_shape | tiny_gap | — | prob_error_reduction | observed | +0.264353 | [+0.257044, +0.271980] |
| single_shape | tiny_gmp | — | prob_error_reduction | observed | +0.345929 | [+0.334706, +0.357246] |
| two_concepts | bn2_w16_gap | — | prob_error_reduction | observed | -0.038992 | [-0.070334, -0.007672] |
| two_concepts | bn2_w16_gmp | — | prob_error_reduction | observed | +0.012711 | [-0.012772, +0.037548] |
| two_concepts | bn4_w16_gap | — | prob_error_reduction | observed | +0.075703 | [+0.053520, +0.098136] |
| two_concepts | bn4_w16_gmp | — | prob_error_reduction | observed | -0.002345 | [-0.016450, +0.011318] |
| two_concepts | plain2_w16_gap | — | prob_error_reduction | observed | +0.334773 | [+0.320813, +0.348746] |
| two_concepts | plain2_w16_gmp | — | prob_error_reduction | observed | -0.058084 | [-0.075563, -0.040938] |
| two_concepts | plain2_w64_gap | — | prob_error_reduction | observed | +0.324743 | [+0.304959, +0.344624] |
| two_concepts | plain2_w64_gmp | — | prob_error_reduction | observed | -0.002051 | [-0.014980, +0.011080] |
| two_concepts | plain4_w16_gap | — | prob_error_reduction | observed | +0.116007 | [+0.099495, +0.132604] |
| two_concepts | plain4_w16_gmp | — | prob_error_reduction | observed | -0.056135 | [-0.067060, -0.044758] |
| two_concepts | plain4_w64_gap | — | prob_error_reduction | observed | +0.001309 | [-0.014585, +0.017545] |
| two_concepts | plain4_w64_gmp | — | prob_error_reduction | observed | -0.023797 | [-0.028153, -0.019458] |
| two_concepts | res4_w16_gap | — | prob_error_reduction | observed | +0.097401 | [+0.075790, +0.118326] |
| two_concepts | res4_w16_gmp | — | prob_error_reduction | observed | -0.044802 | [-0.055327, -0.034203] |
| two_concepts | tiny_gap | — | prob_error_reduction | observed | +0.094358 | [+0.090237, +0.098497] |
| two_concepts | tiny_gmp | — | prob_error_reduction | observed | +0.831512 | [+0.812491, +0.850350] |
| single_shape | bn2_w16_gap | — | prob_error_reduction | additive | +0.049082 | [+0.024348, +0.074186] |
| single_shape | bn2_w16_gmp | — | prob_error_reduction | additive | +0.132187 | [+0.116274, +0.147916] |
| single_shape | bn4_w16_gap | — | prob_error_reduction | additive | +0.053248 | [+0.033796, +0.072988] |
| single_shape | bn4_w16_gmp | — | prob_error_reduction | additive | +0.009796 | [+0.003354, +0.016374] |
| single_shape | plain2_w16_gap | — | prob_error_reduction | additive | +0.176099 | [+0.159595, +0.192175] |
| single_shape | plain2_w16_gmp | — | prob_error_reduction | additive | -0.053986 | [-0.064113, -0.043649] |
| single_shape | plain2_w64_gap | — | prob_error_reduction | additive | +0.150541 | [+0.132533, +0.168508] |
| single_shape | plain2_w64_gmp | — | prob_error_reduction | additive | -0.045950 | [-0.052517, -0.039483] |
| single_shape | plain4_w16_gap | — | prob_error_reduction | additive | +0.113030 | [+0.092388, +0.133660] |
| single_shape | plain4_w16_gmp | — | prob_error_reduction | additive | -0.004563 | [-0.009050, -0.000120] |
| single_shape | plain4_w64_gap | — | prob_error_reduction | additive | +0.017793 | [+0.003734, +0.031467] |
| single_shape | plain4_w64_gmp | — | prob_error_reduction | additive | -0.000679 | [-0.002171, +0.000794] |
| single_shape | res4_w16_gap | — | prob_error_reduction | additive | +0.111110 | [+0.094156, +0.128213] |
| single_shape | res4_w16_gmp | — | prob_error_reduction | additive | +0.000635 | [-0.003451, +0.004847] |
| single_shape | tiny_gap | — | prob_error_reduction | additive | +0.264353 | [+0.256940, +0.271834] |
| single_shape | tiny_gmp | — | prob_error_reduction | additive | +0.345929 | [+0.334384, +0.357268] |
| two_concepts | bn2_w16_gap | — | prob_error_reduction | additive | +0.084220 | [+0.050515, +0.117187] |
| two_concepts | bn2_w16_gmp | — | prob_error_reduction | additive | +0.063070 | [+0.041871, +0.085466] |
| two_concepts | bn4_w16_gap | — | prob_error_reduction | additive | +0.048706 | [+0.029703, +0.067406] |
| two_concepts | bn4_w16_gmp | — | prob_error_reduction | additive | -0.017508 | [-0.028563, -0.006733] |
| two_concepts | plain2_w16_gap | — | prob_error_reduction | additive | +0.319454 | [+0.305808, +0.333090] |
| two_concepts | plain2_w16_gmp | — | prob_error_reduction | additive | -0.134898 | [-0.148708, -0.120745] |
| two_concepts | plain2_w64_gap | — | prob_error_reduction | additive | +0.320080 | [+0.300823, +0.339409] |
| two_concepts | plain2_w64_gmp | — | prob_error_reduction | additive | -0.092624 | [-0.102586, -0.082737] |
| two_concepts | plain4_w16_gap | — | prob_error_reduction | additive | +0.090126 | [+0.074380, +0.106002] |
| two_concepts | plain4_w16_gmp | — | prob_error_reduction | additive | -0.069782 | [-0.078088, -0.062112] |
| two_concepts | plain4_w64_gap | — | prob_error_reduction | additive | +0.014453 | [+0.000399, +0.028714] |
| two_concepts | plain4_w64_gmp | — | prob_error_reduction | additive | -0.025193 | [-0.028713, -0.021661] |
| two_concepts | res4_w16_gap | — | prob_error_reduction | additive | +0.068548 | [+0.048077, +0.088084] |
| two_concepts | res4_w16_gmp | — | prob_error_reduction | additive | -0.052104 | [-0.059484, -0.044874] |
| two_concepts | tiny_gap | — | prob_error_reduction | additive | +0.094358 | [+0.090225, +0.098500] |
| two_concepts | tiny_gmp | — | prob_error_reduction | additive | +0.831512 | [+0.812139, +0.850549] |

## Observed minus additive reconstruction

Positive values mean the observed metric is larger than the additive reconstruction; negative values mean it is smaller. For centered logits, the corresponding residual and exact squared-error correction are reported separately.

## Interpretation frame

- **Additive account:** agreement between observed and reconstructed curves, together with nonzero cancellation/cross terms and small residual energy, supports a superposition-plus-metric explanation.
- **Non-additive account:** reproducible reconstruction gaps accompanied by non-negligible residual energy and exact residual correction identify where downstream computation departs from the singleton superposition model.
- **Combined account:** both can coexist and should be quantified by architecture, treatment, task, and filter bank rather than collapsed into a single mechanism label.

## Limits

This analysis is post-hoc and reuses the same models and matched counterfactual pairs as the source studies. It does not provide an independent confirmatory sample, identify a unique semantic mechanism, or establish natural-image generalization. Tiny architectures are an analytic implementation control: because their tail is pooling followed by a linear classifier, whole-channel patching should be additive in logits up to numerical error even when fidelity or probability curves are nonlinear.
