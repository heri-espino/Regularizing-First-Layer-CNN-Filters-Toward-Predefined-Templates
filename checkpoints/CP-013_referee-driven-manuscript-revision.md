# CP-013 — Referee-driven manuscript revision

**Date:** 2026-09-22  
**Status:** manuscript revision complete; build validation pending at checkpoint creation  
**Evidential role:** manuscript/framing only; no new scientific outcomes  
**Contemporaneous:** yes

## Why this checkpoint exists

A fresh referee-style review of the fully rewritten manuscript found no fatal experimental gap but identified four presentation/inference risks that could cause a reviewer to overread the evidence:

1. the experimental program was sequential and outcome-informed across follow-ups rather than jointly preregistered;
2. the TOST equivalence margins were prespecified but are study-specific, scale-relative conventions rather than externally validated practical thresholds;
3. equivalence statements average over four architectures despite a strong spatial-structure-by-architecture interaction;
4. retention versus release compares complete training regimes whose downstream weights co-adapt, not a direct post-training intervention on first-layer geometry alone.

## What was changed

### Sequential evidence design

Methods now state explicitly that:

- the channel-budget result motivated the architecture study;
- the architecture map then motivated the fresh matched-anchor question;
- the four matched-anchor diagnostic architectures were selected outcome-informed from the earlier map;
- two_concepts was designated primary in later follow-ups because earlier work showed the clearer diagnostic signal;
- each follow-up protocol and its fresh renderer blocks were frozen before that follow-up's outcomes were inspected.

The manuscript no longer risks implying one jointly preregistered experimental program.

### Training-regime interpretation

Methods and Discussion now state that retention-versus-release is a contrast between two complete training regimes. Downstream weights co-adapt to the evolving first layer, so the contrast is not interpreted as the direct causal effect of changing final first-layer geometry while holding the remainder of the trained network fixed.

### Equivalence interpretation

All paper-facing equivalence language is now qualified as **architecture-averaged** and tied explicitly to the frozen, scale-relative margin.

The margins were fixed before fresh matched-anchor outcomes as 20% of historical mean absolute B across the same four architecture forms.

The appendix now reports that the probability-error 90% interval would require a symmetric margin of approximately 0.05261 to support equivalence, about 16.0% of the historical scale used to define the frozen 20% margin. This makes the margin sensitivity visible rather than treating the SESOI as externally validated.

### Random-channel interpretation

The manuscript no longer implies that spatial specificity disappears for random channel sets. It states instead that architecture-averaged random-channel specificity is smaller and falls within the frozen margins, while architecture-dependent random-channel differences remain detectable.

### Methods completeness

The main Methods now:

- defines the renderer concept index used by the validation channel-ranking equation;
- states that two_concepts uses the toggled circle/triangle factor and single_shape uses the destination identity;
- states that ranking is concept/identity-specific and frozen on validation data;
- gives a compact description of the 16-architecture grid;
- states that the same global-max ranking rule is retained for GAP architectures to avoid changing ranking together with architecture.

The appendix now contains an exact 16-row architecture-definition table with total depth, downstream width, pooling, BatchNorm, connectivity, and parameter count.

### Related work and contribution boundary

Related Work now cites Bau et al. (2020) as a direct visual-network precedent for intervening on internal units.

The contribution boundary is sharpened:

- structured-filter work primarily studies representation structure or predictive performance;
- patching-robustness work primarily studies intervention methodology;
- this paper combines a controlled structured first layer, fresh channel-budget/architecture studies, and a Gram/rank/spectrum-matched spatial control.

The paper still explicitly does not claim that generic activation-patching sensitivity is novel.

### Abstract

The abstract now uses **100-block matched-anchor study** rather than advertising the 25,600 trained-model count, keeping the inferential unit clear.

It also states that the probability-error equivalence result is architecture-averaged and tied to the prespecified margin.

## Evidence or results available now

No new scientific outcomes were produced in this checkpoint.

Scientific results remain those recorded in CP-010 and CP-011.

## Static audit

After revision:

- missing bibliography keys: 0;
- unresolved cleveref references: 0;
- duplicate labels: 0;
- displayed equations: 13;
- displayed equations without labels: 0;
- raw ref commands: 0;
- unnumbered bracket displays: 0;
- visible internal Stage A--G names in main text: 0;
- main-text figures: 4;
- main-text result tables: 0.

## Interpretation

The manuscript now distinguishes:

- prospective with respect to fresh follow-up outcomes from jointly preregistered;
- statistical nonzero differences from architecture-averaged scale-relative equivalence;
- first-layer spatial structure from the complete training-regime contrast;
- smaller architecture-averaged random-channel effects from absence of architecture-dependent random-channel effects.

These distinctions are part of the scientific claim, not merely caveats.

## Next actions

1. Confirm CI compiles the exact revised source.
2. Perform one final referee pass focused on clarity/readability rather than adding new experiments.
3. Prepare the anonymous artifact/release metadata.
4. Do not add another large experiment unless a concrete unresolved threat is identified.

## Do-not-forget constraints

- Never state the probability-error matched-anchor result as globally/practically equivalent without the words architecture-averaged and the prespecified scale-relative margin.
- Never describe the follow-up sequence as jointly preregistered.
- Never interpret retention-versus-release as changing only first-layer kernels in an otherwise fixed trained model.
- Keep the random-channel architecture interaction visible.
- Keep the plain2_w16_gmp sign reversal visible.
