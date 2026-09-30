# CP-015 — Post-hoc patching-additivity study implemented

**Date:** 2026-09-30  
**Status:** implementation validated; source-study execution pending on the university VM  
**Evidential role:** post hoc / implementation-only at this checkpoint  
**Contemporaneous:** yes

## Why this checkpoint exists

A new post-hoc mechanistic analysis was requested after the TMLR rejection to explain the already observed dependence of first-layer activation-patching curves on intervention size. The analysis reuses the completed architecture-robustness and filter-bank-control checkpoints; it does not train new models and does not alter either frozen source study.

## Scientific question / engineering objective

Quantify how much of each patching curve is reproduced by summing singleton channel effects in centered-logit space, and how much remains as a non-additive residual after that reconstruction. Keep additive cancellation, downstream model non-additivity, and nonlinearity of the evaluation metric distinct.

## What was done

Created \`studies/cnn_patching_additivity/\` with a frozen post-hoc protocol and independent implementation:

- all 16 singleton first-layer channel patches are evaluated for each saved model;
- exact original matched pairs, post-ReLU intervention point, validation-only channel ranking, random-set seed namespaces, and validation-energy-matched controls are reused;
- selected sets are evaluated for \`k=0,...,16\`; random controls for \`k=1,...,16\`; energy-matched controls for \`k in {1,2,4,8}\`;
- centered-logit additive reconstruction, raw-logit diagnostics, cancellation, parallel/orthogonal singleton geometry, a 16x16 singleton cross-product matrix, residual energy, and the exact squared-error correction are recorded;
- source metric reproduction is a hard check;
- \`tiny_gmp\` and \`tiny_gap\` are mandatory analytic additivity controls;
- the implementation is atomic and resumable and never overwrites source artifacts;
- the full architecture source remains 25,600 checkpoints; the primary structured-vs-pixel-permuted filter-bank scope is 12,800 checkpoints;
- renderer block remains the inferential unit after averaging four initialization replicates;
- uncertainty uses a fixed block bootstrap, with pointwise intervals separated from simultaneous across-intervention-size bands;
- random rank-10/full-rank banks are governed by a predeclared cost-only benchmark rule before their new outcomes are inspected.

A predetermined technical validation driver uses the earliest renderer block by identifier, the four core architectures, both tasks/treatments, all four initialization replicates, and both primary filter banks where applicable. It checks no-op/full-patch identities, singleton and Tiny additivity, algebraic identities, source metric reproduction, batch-size stability, cached-activation immutability, resume behavior, runtime, and storage.

During a synthetic end-to-end analyzer test, an implementation issue was found: an all-missing \`anchor_family\` index caused pandas pivot operations to discard the architecture-study rows. This was fixed by using an explicit \`not_applicable\` level for the architecture source. Both architecture-shaped and anchor-shaped synthetic analyses now complete.

## Evidence or results available now

No scientific outcomes from the saved Stage-F/Stage-G checkpoints are available or interpreted at this checkpoint.

Implementation/integrity evidence available now:

- \`python studies/cnn_patching_additivity/test_math.py\` — PASS;
- \`python studies/cnn_patching_additivity/test_integration.py\` — PASS;
- analytic pooling-plus-linear whole-channel additivity test passes for both max and average pooling;
- Python syntax compilation passes for the evaluator, validator, analyzer, and tests;
- synthetic architecture-source analysis completes through report generation;
- synthetic structured/pixel-permuted analysis completes through report generation.

The current ChatGPT execution environment cannot mount or access the user's Windows \`%LOCALAPPDATA%\` roots, so the real 38,400-checkpoint central evaluation has not been falsely marked complete. The repository launcher is prepared for the VM where those artifacts exist.

## Interpretation

The new study is ready for source inventory and predetermined validation on the machine that holds the completed checkpoints. Passing pure algebra and analytic Tiny controls validates the decomposition logic, but it is not scientific evidence about the trained models.

## What this does not establish

- No conclusion yet about whether the observed intervention-size curves are mainly additive, non-additive, or mixed.
- No conclusion yet about where structured and pixel-permuted filter banks differ in singleton geometry, cancellation, or residuals.
- No independent confirmation is created by this post-hoc reuse of the same models and pairs.
- A nonzero residual will not by itself be labeled synergy, redundancy, or a unique causal mechanism.
- Nothing here establishes natural-image or larger-model generalization or explains the unknown editorial rejection reason.

## Repository / provenance pointers

- Protocol: \`studies/cnn_patching_additivity/PROTOCOL.md\`
- Implementation: \`studies/cnn_patching_additivity/evaluate.py\`, \`math_core.py\`, \`validate.py\`, \`analyze.py\`
- Launcher: \`studies/cnn_patching_additivity/run_patching_additivity.ps1\`
- Documentation: \`studies/cnn_patching_additivity/README.md\`
- Tests: \`studies/cnn_patching_additivity/test_math.py\`, \`test_integration.py\`
- Source architecture root: \`%LOCALAPPDATA%\prior-templates-cnns\results\architecture_robustness_cuda_001\`
- Source filter-bank root: \`%LOCALAPPDATA%\prior-templates-cnns\results\anchor_specificity_cuda_001\`
- External result root: \`%LOCALAPPDATA%\prior-templates-cnns\results\patching_additivity_001\`
- Source repository head inspected before implementation: \`fa5fae0295747ba48ec8a4f222aac07e58fc5ace\`

## Next actions

1. On the university VM, pull the implementation and run \`-Mode Inventory\`.
2. Run \`-Mode Validate\`; do not launch the complete grid if any integrity or analytic control fails.
3. If validation passes, run \`-Mode Main\`. Reinvoking it resumes and skips completed per-model JSON files.
4. Apply the frozen cost-only rule before deciding whether to run \`-Mode Secondary\` for the two random filter-bank families.
5. After complete source evaluation, create a new results checkpoint with block-level estimates, intervals, negative/null results, and exact report paths before changing the manuscript.

## Do-not-forget constraints

- Do not retrain models for this study.
- Do not use the old partial \`architecture_robustness_001\` CPU root.
- Do not modify frozen Stage-F or Stage-G scientific implementations.
- Do not inspect random-anchor additivity outcomes before applying the predeclared cost-only rule.
- Do not pool the two source studies as independent matched blocks.
- Do not report percentages of effect explained when the observed contrast is near zero.
- Do not present implementation tests or partial runs as completed scientific results.
