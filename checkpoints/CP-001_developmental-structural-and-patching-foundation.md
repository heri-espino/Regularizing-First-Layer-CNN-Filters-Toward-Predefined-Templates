# CP-001 — Developmental structural and patching foundation

**Date:** reconstructed 2026-09-21  
**Status:** historical reconstruction  
**Evidential role:** developmental + post hoc  
**Contemporaneous:** no

## Why this checkpoint exists

The early project established the distinction that later became the paper's central motivation: preserving template-like first-layer weights is not the same as obtaining a stable functional interpretation from activation patching.

## Scientific question / engineering objective

Determine whether predefined first-layer templates can be retained under training and whether that structural retention produces a correspondingly simple activation-patching signature.

## What was done

The project introduced a 16-filter first-layer bank of centered, unit-norm edge/corner/ring templates and trained small CNNs under several conditions, including:

- template initialization without continued regularization;
- constant regularization toward the initial template bank;
- annealed release of that regularizer.

The initial model family used a 16-channel (9\times9) first convolution followed by ReLU, with TinyCNN and a two-layer variant sharing the same first-layer intervention space.

Activation patching was performed after conv1+ReLU by replacing selected activation maps in a base example with maps from its matched counterfactual.

Developmental analyses also explored channel rankings, random controls, energy-matched controls, and patch budgets.

## Evidence or results available now

The early studies established two durable empirical facts:

1. constant template regularization strongly preserves template-like first-layer kernels in weight space;
2. the functional patching story is not a monotone translation of that structural similarity.

The early selected-minus-random results did not support a simple claim that stronger template retention automatically yields uniformly stronger patching effects.

These analyses were exploratory/developmental. They are not independent confirmation of later hypotheses.

## Interpretation

The correct early lesson was a **separation between structural retention and functional intervention behavior**.

That separation motivated later prospective experiments instead of just reporting attractive-looking kernels.

## What this does not establish

- It does not show that template-like weights are human-interpretable.
- It does not establish a unique causal mechanism.
- It does not establish that activation patching is a mediated fraction.
- It does not establish natural-image generalization.
- It does not establish the later channel-budget contrast prospectively.

## Repository / provenance pointers

- Early studies: `studies/cnn_causal_milestone/`, `studies/cnn_release_experiment/`
- Patching development: `studies/cnn_patch_robustness/`
- Energy control: `studies/cnn_patch_energy_control/`
- Current scientific summary: `RESEARCH_STATUS.md`

## Next actions at this historical point

1. Define a precise channel-budget estimand.
2. Test it on fresh blocks rather than reusing developmental data.
3. Separate selected-channel effects from baseline/control movement.

## Do-not-forget constraints

- Early stages are provenance, not retrospective confirmation.
- Weight-space similarity and patching behavior are different measurements.
