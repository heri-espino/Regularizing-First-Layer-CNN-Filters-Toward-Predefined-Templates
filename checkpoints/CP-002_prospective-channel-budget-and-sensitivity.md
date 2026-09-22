# CP-002 — Prospective channel-budget test and sensitivity map

**Date:** reconstructed 2026-09-21  
**Status:** results complete  
**Evidential role:** prospective primary follow-up + prespecified secondary sensitivity  
**Contemporaneous:** no

## Why this checkpoint exists

Developmental work suggested that the release-versus-retention comparison changes with the number of patched first-layer channels. A fresh-sample prospective test was needed to distinguish a real reproducible pattern from exploratory reuse.

## Scientific question

For TinyCNN on fresh renderer blocks, does the release-minus-retention patching difference change between small and medium channel budgets?

The frozen contrast was

[
B=
\frac{\Delta(4)+\Delta(8)}{2}
-
\frac{\Delta(1)+\Delta(2)}{2},
]

with

[
\Delta(k)=F_{\mathrm{release}}(k)-F_{\mathrm{retention}}(k).
]

## What was done

### Prospective channel-count experiment

- 20 fresh `two_concepts` renderer blocks;
- TinyCNN;
- paired retention/release conditions;
- probability-space normalized fidelity;
- inferential unit: renderer block.

### Prespecified sensitivity experiment

A larger fresh-sample map then evaluated:

- 50 renderer blocks;
- 2 tasks;
- 2 architectures;
- 6 schedule conditions;
- 1,200 trained models.

## Evidence or results available now

Prospective primary result:

[
B=0.3309763,
qquad
95\%\ \mathrm{CI}=[0.273680,0.388273],
]

with

[
t_{19}=12.0905,
qquad
p=2.2819\times10^{-10}.
]

All 20 renderer-block (B) values were positive.

Pointwise treatment differences were approximately:

- (k=1): (-0.3459)
- (k=2): (-0.3317)
- (k=4): (-0.0221)
- (k=8): (+0.0065)

The larger sensitivity study showed that TinyCNN retained a positive channel-budget contrast across tasks/schedules, while the TwoLayerCNN form behaved substantially differently.

Historical default release-minus-retention (B) values included:

| task / architecture | probability-fidelity (B) |
|---|---:|
| single_shape / TinyCNN | +0.07189 |
| single_shape / TwoLayerCNN | -0.01018 |
| two_concepts / TinyCNN | +0.28619 |
| two_concepts / TwoLayerCNN | -0.04156 |

## Interpretation

The channel-budget dependence is not just an exploratory artifact in TinyCNN: it was supported prospectively on fresh blocks.

However, architecture independence is not supported. The TwoLayerCNN result created a new scientific question rather than invalidating the TinyCNN result.

## What this does not establish

- It does not establish that the original normalized fidelity metric is scale-robust.
- It does not establish a universal architecture-independent effect.
- It does not establish that depth alone causes the architecture difference.
- It does not establish template-specificity.

## Repository / provenance pointers

- Prospective protocol: `studies/cnn_budget_confirmation/PROTOCOL.md`
- Prospective report: `analysis/budget_confirmation_001/REPORT.md`
- Sensitivity protocol: `studies/cnn_exhaustive_robustness/PROTOCOL.md`
- Sensitivity report: `analysis/exhaustive_robustness_001/REPORT.md`

## Next actions at this historical point

1. Audit whether the normalized output metric drives the effect.
2. Preserve the prospective (B) contrast while changing output-space metrics.
3. Investigate architecture heterogeneity with a controlled architecture grid.

## Do-not-forget constraints

- Renderer block is the inferential unit.
- Image pairs are measurements inside a model, not independent replicates.
- The sensitivity study is not a second primary confirmation.
