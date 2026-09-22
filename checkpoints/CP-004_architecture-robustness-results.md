# CP-004 — Architecture robustness completed

**Date:** reconstructed 2026-09-21  
**Status:** results complete  
**Evidential role:** prospectively frozen fresh-sample architecture robustness  
**Contemporaneous:** no

## Why this checkpoint exists

The metric audit showed the TinyCNN channel-budget contrast survived alternative output metrics, while the TwoLayerCNN form remained different. Architecture was therefore the largest unresolved conditioning variable.

## Scientific question

Holding fixed the first-layer intervention space, counterfactual construction, training comparison, channel-ranking procedure, and metrics, how strongly does downstream architecture change the release-versus-retention patch-budget contrast?

## What was done

Fresh architecture study:

- 100 renderer blocks, 6000--6099;
- 4 paired initialization replicates per block;
- 2 tasks;
- 2 treatments;
- 16 architectures;
- 25,600 trained models.

The four init replicates are averaged within renderer block. The inferential sample size is (n=100), not 400.

Architecture factors include:

- GMP vs GAP;
- total convolution depth 1/2/4;
- downstream width 16/64;
- plain vs residual connectivity;
- downstream BatchNorm.

Primary metrics:

- centered-logit fidelity;
- unnormalized probability-error reduction.

## Evidence or results available now

Primary `two_concepts` architecture omnibus:

| metric | (F(15,1485)) | partial (eta^2) |
|---|---:|---:|
| centered-logit fidelity | 77.0874 | 0.4378 |
| probability error reduction | 656.7002 | 0.8690 |

Holm-adjusted probability for the centered-logit omnibus was about (2.40\times10^{-173}); the probability-error result numerically underflowed to zero.

Fresh TinyGMP minus Plain2-W16-GMP bridge:

### Centered-logit fidelity

[
\Delta B=+0.162258,
qquad
95\%\ \mathrm{CI}=[+0.149701,+0.174815].
]

### Probability error reduction

[
\Delta B=+0.889596,
qquad
95\%\ \mathrm{CI}=[+0.862118,+0.917073].
]

Architecture means for the bridge forms:

- `tiny_gmp`: (B=+0.145577) centered-logit; (+0.831512) probability error reduction;
- `plain2_w16_gmp`: (B=-0.016681); (-0.058084).

The factor decomposition showed:

- pooling strongly modifies the contrast, but not with one universal direction;
- the Tiny-to-Plain2 transition under GMP accounts for most of that particular depth-form difference;
- additional plain depth from 2 to 4 under GMP adds little;
- residual connectivity is not a major driver in the tested family;
- BatchNorm and width are context/metric dependent.

## Interpretation

Architecture dependence is decisively reproduced on fresh data under both primary metrics.

The correct conclusion is **interaction/conditioning**, not “GAP fixes it,” “depth destroys it,” or “one architecture is correct.”

This result strengthens the paper by mapping a boundary of the measurement phenomenon rather than pretending the effect is universal.

## What this does not establish

- It does not establish natural-image generalization.
- It does not establish a universal causal effect of depth, pooling, width, residuals, or BatchNorm.
- It does not establish that template structure is the reason the phenomenon occurs.
- The repeated-measures omnibus still deserved sphericity-robust post hoc diagnostics.

## Repository / provenance pointers

- Protocol: `studies/cnn_architecture_robustness/PROTOCOL.md`
- Report: `analysis/architecture_robustness_001/REPORT.md`
- Paper-facing outputs: `analysis/architecture_robustness_001/`
- Official external run root: `%LOCALAPPDATA%\prior-templates-cnns\results\architecture_robustness_cuda_001`

## Next actions at this historical point

1. Reanalyze architecture heterogeneity with Greenhouse--Geisser/permutation/Friedman diagnostics.
2. Examine random-channel controls explicitly.
3. Directly compare structural retention difference with functional (B).
4. Decide whether the paper is really about predefined templates or about patching measurement sensitivity in an anchor-regularized setting.

## Do-not-forget constraints

- Do not merge the earlier CPU-partial run with the official CUDA run.
- Do not use model count as inferential (n).
- Stage-F science is frozen; later diagnostics must be versioned separately.
