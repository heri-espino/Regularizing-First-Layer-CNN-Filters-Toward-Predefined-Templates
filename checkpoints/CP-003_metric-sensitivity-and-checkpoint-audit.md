# CP-003 — Metric sensitivity and fixed-checkpoint audit

**Date:** reconstructed 2026-09-21  
**Status:** results complete  
**Evidential role:** frozen post hoc robustness + implementation audit  
**Contemporaneous:** no

## Why this checkpoint exists

A referee could reasonably argue that the original normalized probability fidelity

[
F=1-\frac{\|p_S-p_1\|^2}{\|p_1-p_0\|^2}
]

is sensitive to a treatment-dependent denominator. The core TinyCNN contrast therefore needed to be recomputed on saved checkpoints under metrics with different scaling conventions.

## Scientific question

Does the prespecified channel-budget contrast remain positive when the output-space metric is changed, including an unnormalized probability-error reduction?

## What was done

No models were retrained.

Saved prospective/sensitivity checkpoints were reevaluated using:

1. centered-logit fidelity;
2. unnormalized probability reconstruction-error reduction;
3. raw-logit and other secondary diagnostics.

A separate fixed-checkpoint implementation audit recomputed historical metrics and patch identities.

## Evidence or results available now

For the prospective TinyCNN `two_concepts` contrast:

### Centered-logit fidelity

[
B=+0.178881,
qquad
95\%\ \mathrm{CI}=[0.127268,0.230494].
]

### Unnormalized probability error reduction

[
B=+0.894411,
qquad
95\%\ \mathrm{CI}=[0.786301,1.002522].
]

The pointwise curves were **not identical across metrics**.

Centered-logit treatment differences were approximately:

[
(-0.211342,-0.174516,-0.034049,+0.005954)
]

for (k=(1,2,4,8)).

Unnormalized probability-error differences were approximately:

[
(-0.229423,+0.044926,+0.754287,+0.850038).
]

The metric audit also showed that the release-minus-retention base-to-counterfactual output scale differs substantially between treatments.

Integrity checks:

- maximum historical probability-fidelity recomputation discrepancy: about (1.24\times10^{-7});
- full-patch identity: exact within stored audit;
- no-op identity: exact within stored audit.

## Interpretation

The defensible robustness claim is:

> the **prespecified (B) contrast remains positive** under centered-logit fidelity and unnormalized probability-error reduction.

It is **not** correct to say the full pointwise curves are metric invariant.

The denominator of the original normalized probability fidelity is not harmless; it changes substantially by treatment. The paper must say this explicitly.

## What this does not establish

- It does not make the metric audit an independent fresh-sample replication.
- It does not establish equivalence of pointwise curves across metrics.
- It does not resolve architecture dependence.
- It does not resolve template-specificity.

## Repository / provenance pointers

- Protocol: `studies/cnn_metric_sensitivity/PROTOCOL.md`
- Report: `analysis/metric_sensitivity_001/REPORT.md`
- Fixed-checkpoint audit: `analysis/checkpoint_audit/AUDIT_REPORT.md`

## Next actions at this historical point

1. Treat centered-logit fidelity and probability-error reduction as primary architecture metrics.
2. Run a fresh architecture experiment instead of arguing from TinyCNN/TwoLayerCNN alone.
3. Rewrite manuscript language from “same qualitative curve” to “same prespecified (B) contrast.”

## Do-not-forget constraints

- Metric sensitivity is post hoc with respect to earlier probability-fidelity outcomes.
- Never describe the denominator-scale concern as disproven.
