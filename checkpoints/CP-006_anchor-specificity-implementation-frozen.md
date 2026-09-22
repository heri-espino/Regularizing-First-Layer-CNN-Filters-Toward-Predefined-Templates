# CP-006 — Anchor-specificity experiment frozen and implementation-ready

**Date:** reconstructed 2026-09-21  
**Status:** implementation complete; full scientific run not yet interpreted  
**Evidential role:** prospective fresh-sample design + implementation checks  
**Contemporaneous:** no

## Why this checkpoint exists

The strongest unresolved reviewer objection is whether the patch-budget phenomenon is actually about **predefined spatial templates** or merely about keeping a first layer near any anchor.

This experiment was designed to isolate that distinction directly.

## Scientific question

Does the release-versus-retention patch-budget contrast depend on the original 2D spatial organization of edge/corner/ring templates once bank geometry, rank, and spectrum are controlled?

## What was done

A fresh 25,600-model experiment was frozen:

[
100\ \text{blocks}
\times4\ \text{reps}
\times2\ \text{tasks}
\times4\ \text{architectures}
\times4\ \text{anchors}
\times2\ \text{treatments}.
]

Fresh blocks: 7000--7099.

Architectures:

- `tiny_gmp`
- `tiny_gap`
- `plain2_w16_gmp`
- `plain2_w16_gap`

Anchor families:

1. `structured_template`
2. `pixel_permuted_template`
3. `random_rank10`
4. `random_fullrank`

The pixel-permuted control applies one common permutation of the 81 spatial coordinates to every structured template row. It preserves, up to numerical tolerance:

- row coefficient multisets;
- row means/norms;
- pairwise inner products;
- complete Gram matrix;
- numerical rank;
- singular spectrum.

It destroys the original 2D edge/corner/ring arrangement.

Primary task: `two_concepts`.

Primary metrics:

- centered-logit fidelity;
- probability error reduction.

Primary specificity contrast: structured minus pixel-permuted (B), averaged across the four diagnostic architectures.

## Frozen equivalence companion

Failure to reject zero is not evidence of equivalence.

TOST equivalence margins were frozen before the full run using 20% of the historical Stage-F mean absolute (B) across the same four architecture forms:

- centered-logit fidelity: **0.017040331170505053**
- probability error reduction: **0.06593636028899892**

Interpretation is fixed:

- significant difference test -> spatial structure changes the contrast;
- significant TOST -> practical equivalence within the frozen margin;
- neither -> inconclusive.

## Evidence or results available now

No full-run scientific outcome is interpreted at this checkpoint.

Implementation validation passed:

- Python compilation;
- PowerShell syntax;
- anchor centering/unit-norm/rank checks;
- pixel-permuted Gram preservation;
- paired downstream initialization across anchor families;
- equivalence helper;
- one-epoch CPU train/eval smoke.

The implementation also supports outcome-blind progress reporting.

## Interpretation

The design cleanly separates three possibilities:

- spatial template arrangement matters beyond bank geometry;
- spatial arrangement is practically irrelevant within the frozen margin;
- available precision is insufficient to decide.

Either substantive result can improve the final paper because the interpretation rule is frozen in advance.

## What this does not establish

- No scientific conclusion can be drawn before the full run and frozen analysis complete.
- A nonsignificant difference alone is not equivalence.
- The experiment still concerns controlled small CNNs and synthetic tasks.
- It does not establish semantic interpretability or natural-image generalization.

## Repository / provenance pointers

- Protocol: `studies/cnn_anchor_specificity/PROTOCOL.md`
- Core: `studies/cnn_anchor_specificity/anchor_core.py`
- Trainer: `studies/cnn_anchor_specificity/train_grid.py`
- Evaluator: `studies/cnn_anchor_specificity/evaluate_grid.py`
- Analyzer: `studies/cnn_anchor_specificity/analyze.py`
- Launcher: `run/run_anchor_specificity.ps1`
- Outcome-blind status: `run/status_anchor_specificity.ps1`
- External full root: `%LOCALAPPDATA%\prior-templates-cnns\results\anchor_specificity_cuda_001`

## Next actions

1. Pull latest `main`.
2. Run `.\run\run_anchor_specificity.ps1 -Smoke`.
3. Run `.\run\run_anchor_specificity.ps1`.
4. Do not inspect partial scientific outcomes.
5. After completion, stage paper-facing outputs with `run/stage_anchor_specificity_results.ps1`.
6. Create a **new checkpoint** immediately when the full results are available.

## Do-not-forget constraints

- Full-run partial outcomes must not be used to redesign the study.
- Completed models/evaluations are resumable and skipped after reboot.
- Do not mix smoke outputs with the official full root.
- Do not rewrite this checkpoint after seeing results; create CP-009 or later.
