# CP-017 — Patching-additivity results and manuscript reinterpretation

**Date:** 2026-10-01  
**Status:** results-complete / interpretation / manuscript  
**Evidential role:** post hoc saved-checkpoint mechanistic analysis; manuscript reinterpretation  
**Contemporaneous:** yes

## Why this checkpoint exists

The saved-checkpoint patching-additivity study is now complete, its paper-facing outputs are archived under `analysis/patching_additivity_001/`, and the results materially change how the earlier intervention-size findings should be interpreted.

The manuscript has therefore been updated to distinguish intervention-size dependence from genuine interaction among patched channels.

## Scientific question / engineering objective

How much of the observed dependence of activation-patching effects on intervention size can be reconstructed by summing singleton channel effects, and where is an additional non-additive downstream residual required?

A second question is whether the structured-versus-pixel-permuted filter-bank difference is primarily carried by singleton-effect geometry or by multi-channel downstream interaction.

## What was done

No models were retrained.

The completed analysis re-evaluated saved checkpoints from:

- the 16-architecture study: **25,600 checkpoints**;
- the primary structured/pixel-permuted filter-bank study: **12,800 checkpoints**.

For each matched pair, the analysis computed every singleton channel patch, formed the additive logit reconstruction
[
\widehat\ell_S=\ell_0+\sum_{j\in S}(\ell_{\{j\}}-\ell_0),
]
and compared it with the jointly patched logits (ell_S). The residual
[
r_S=\ell_S-\widehat\ell_S
]
isolates failure of singleton superposition at the output-logit level.

The same centered-logit fidelity and probability-error metrics were then applied to both observed and reconstructed logits. Cancellation among singleton effects was also measured from the norm of their vector sum.

The inferential unit remains the renderer block after averaging the four initialization replicates. The archived block-bootstrap summaries use **100 renderer blocks**.

The manuscript `paper/main.tex` was updated to add:

- a concise additive-decomposition methods subsection;
- a results subsection separating additive geometry, metric nonlinearity, and downstream non-additivity;
- revised abstract, introduction findings, discussion, limitations, conclusion, and data/code statement.

No new large numerical appendix was added.

## Evidence or results available now

### 1. Exact-additivity controls retain large intervention-size effects

For `two_concepts/tiny_gmp` in the architecture study:

- centered-logit (B): observed **+0.14558**, additive **+0.14558**;
- probability-error-reduction (B): observed **+0.83151**, additive **+0.83151**.

Observed and additive curves agree to numerical precision throughout the tiny architectures, as expected from their pooling-plus-linear downstream tail.

Therefore a large intervention-size contrast does **not** require interactions among patched channels.

### 2. Singleton effects increasingly cancel

In the structured-filter, release condition on `single_shape`, the mean cancellation score across the four spatial-control architectures is approximately:

- (K=0.20) at (k=4);
- (K=0.32) at (k=8);
- (K=0.45) at (k=16).

Thus multi-channel effects depend on the directions of singleton logit changes, not only on their magnitudes.

### 3. Some deeper architectures show strong genuine non-additivity

On `single_shape/bn2_w16_gap`, centered-logit (B) is:

- observed: **-0.27012**;
- additive reconstruction: **+0.34955**.

The sign reverses.

On `single_shape/bn4_w16_gap`:

- observed: **+0.37725**;
- additive: **+1.64910**.

These cases require substantial downstream non-additivity and cannot be explained by score nonlinearity alone.

### 4. The structured-versus-pixel-permuted effect is largely preserved additively

Averaged across the four spatial-control architectures on `two_concepts`:

- centered-logit structured-minus-permuted (B): observed **+0.05743**, additive **+0.05710**;
- probability-error-reduction difference: observed **+0.04563**, additive **+0.04105**.

All corresponding 95% renderer-block bootstrap intervals for the averaged structured-minus-permuted contrasts remain positive.

This supports the interpretation that much of the spatial-filter effect is already present in singleton contribution geometry, while downstream non-additivity modifies it in an architecture-dependent way.

### 5. Integrity checks

The archived summaries report:

- maximum full-patch logit identity error: **0**;
- maximum no-op logit identity error: **0**;
- validation batch-size stability max absolute discrepancy:
  - architecture source: (1.04\times10^{-6});
  - anchor source: (4.56\times10^{-6}).

The validation benchmark permitted the predeclared secondary random-anchor extension by cost, but the central interpretation above uses the completed primary structured/pixel-permuted scope.

## Interpretation

The earlier result “patching depends on intervention size” must not be presented as evidence that larger channel sets reveal nonlinear channel interactions.

The completed decomposition supports a three-part account:

1. **singleton geometry and cancellation** can create strong dependence on (k);
2. **the evaluation functional** can curve the measured score even when logit propagation is exactly additive;
3. **downstream non-additivity** exists in deeper architectures and can materially alter or reverse the additive prediction.

The structured spatial bank affects the first two components strongly enough that the structured-versus-pixel-permuted contrast is reproduced closely by the additive reconstruction. The architecture study then identifies where the third component becomes important.

This is a more precise mechanistic interpretation than the previous manuscript framing.

## What this does not establish

- The decomposition is post hoc and reuses the same checkpoints, test pairs, rankings, and renderer blocks as the source studies; it is not an independent replication.
- A nonzero output-logit residual does not uniquely localize the downstream layer or operation responsible for the interaction.
- The results do not identify a unique semantic circuit or causal abstraction.
- The controlled synthetic tasks do not establish natural-image or large-model generalization.
- The retention-versus-release contrast still compares complete training regimes whose downstream weights co-adapt.

## Repository / provenance pointers

- Protocol: `studies/cnn_patching_additivity/PROTOCOL.md`
- Implementation: `studies/cnn_patching_additivity/`
- Validation: `analysis/patching_additivity_001/validation/VALIDATION_AND_BENCHMARK.json`
- Architecture analysis: `analysis/patching_additivity_001/architecture_analysis/`
- Anchor analysis: `analysis/patching_additivity_001/anchor_analysis/`
- Reports:
  - `analysis/patching_additivity_001/architecture_analysis/REPORT.md`
  - `analysis/patching_additivity_001/anchor_analysis/REPORT.md`
- Manuscript: `paper/main.tex`
- Result archival commit: `bd8b513f7b67695fd0caa12f065efdddd8f4d7be`
- Manuscript integration commit: `2aee58db1958f5c4a67272e78b484c45a7fa7462`
- External result root: `%LOCALAPPDATA%\prior-templates-cnns\results\patching_additivity_001`

## Next actions

1. Compile the paper and inspect page flow/overfull boxes after the new subsection.
2. Perform a referee-style pass focused on whether the new decomposition simplifies rather than expands the paper.
3. Consider replacing some older numerical detail with the mechanistic interpretation if the manuscript becomes too long.
4. Ensure the anonymous supplementary artifact includes the compact additivity summaries and analysis code.

## Do-not-forget constraints

- Do not describe intervention-size dependence alone as evidence of channel interaction.
- Preserve the distinction between additive singleton geometry, metric nonlinearity, and downstream non-additivity.
- Keep the tiny architectures framed as analytic controls, not as evidence that all architectures are additive.
- Keep the structured-versus-pixel-permuted effect architecture-dependent; do not claim a universal positive effect.
- Do not promote this post-hoc decomposition to prospective evidence.
