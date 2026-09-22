# CP-008 — Current pre-submission state

**Date:** 2026-09-21  
**Status:** current project snapshot  
**Evidential role:** mixed synthesis + implementation state  
**Contemporaneous:** reconstructed immediately before adopting the append-only checkpoint policy

## Why this checkpoint exists

The project now has a large experimental history, a restructured manuscript, one final fresh-sample experiment ready to run, and one post hoc diagnostic workflow ready to execute.

This checkpoint defines the state a new researcher or AI agent should inherit before any further work.

## Current scientific state

Supported before the final strengthening run:

1. constant regularization preserves template-like first-layer weights strongly;
2. weight-space template similarity does not imply a simple activation-patching signature;
3. the TinyCNN release-vs-retention comparison depends strongly on patched channel count;
4. that channel-budget contrast was supported prospectively on fresh blocks;
5. the prespecified (B) contrast survives centered-logit fidelity and unnormalized probability-error reduction;
6. downstream architecture strongly conditions the contrast on 100 fresh blocks;
7. architecture dependence is not safely interpretable as one simple main effect of pooling/depth/width/residual/BatchNorm.

Still unresolved:

1. whether the phenomenon is specific to the designed spatial template arrangement;
2. robust post hoc architecture inference without sphericity;
3. formal random-channel architecture dependence;
4. direct structural-retention-vs-functional-(B) relationship;
5. whether an external controlled benchmark is necessary after final framing.

## Current manuscript state

`paper/main.tex` has been rewritten around scientific questions instead of internal stage chronology.

Current conventions:

- descriptive experiment names rather than Stage A--F in paper-facing prose;
- `cleveref`;
- labels on all displayed equations;
- three main visual figures;
- no redundant main-text numerical tables;
- detailed tables in appendices;
- explicit metric/architecture limitations.

The manuscript is **not submission-ready yet**.

## Active work

### Fresh anchor-specificity experiment

`studies/cnn_anchor_specificity/PROTOCOL.md`

- 25,600 models;
- blocks 7000--7099;
- structured vs Gram/rank/spectrum-matched pixel-permuted anchor is the primary specificity contrast;
- formal frozen equivalence companion;
- full run must be interpreted only after completion.

### Post hoc architecture diagnostics

`studies/cnn_architecture_posthoc/PROTOCOL.md`

- no retraining;
- sphericity-robust omnibus;
- random-channel diagnostics;
- structure/function analysis;
- architecture-definition export.

## Immediate commands

From Windows:

```powershell
git pull --ff-only origin main
conda activate prior-templates-cnns
nvidia-smi

.\run\run_architecture_posthoc.ps1
.\run\run_anchor_specificity.ps1 -Smoke
.\run\run_anchor_specificity.ps1
```

Outcome-blind full-run progress:

```powershell
.\run\status_anchor_specificity.ps1
```

## Interpretation decision after anchor specificity

### If structured vs pixel-permuted differs reproducibly

The paper can retain a narrow claim that designed 2D template structure contributes beyond matched bank geometry.

### If practical equivalence is supported

The paper should pivot away from template-specificity. The structured bank becomes the controlled case study, and the contribution becomes anchor-retention / activation-patching measurement sensitivity.

### If neither is established

Template-specificity remains unresolved; do not force either story.

## Repository / provenance pointers

Read in this order:

1. `checkpoints/README.md`
2. this checkpoint
3. `RESEARCH_STATUS.md`
4. `.ai_handoff`
5. active protocols
6. `paper/main.tex`
7. archived Stage-F / metric / prospective reports

Repository was renamed to:

`heri-espino/Regularizing-First-Layer-CNN-Filters-Toward-Predefined-Templates`

## Next actions

1. Run the post hoc architecture diagnostics.
2. Create a new checkpoint when those outputs are available.
3. Run the full anchor-specificity experiment.
4. Create a new checkpoint immediately when its frozen analysis completes.
5. Rewrite title/abstract/discussion only after the specificity result determines the final scientific identity.
6. Reassess external controlled validation only then.
7. Perform one final referee pass before submission.

## Do-not-forget constraints

- **Every new implementation or new result requires a new checkpoint file.**
- Do not edit historical checkpoints to fit later results.
- Do not inspect partial full-run Stage-G outcomes.
- Do not call post hoc architecture diagnostics prospective.
- Do not treat model count as inferential sample size.
- Do not add experiments merely to increase compute volume.
