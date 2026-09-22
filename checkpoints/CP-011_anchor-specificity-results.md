# CP-011 — Fresh anchor-specificity experiment complete

**Date:** 2026-09-22  
**Status:** results-complete  
**Evidential role:** prospectively frozen fresh-sample experiment  
**Contemporaneous:** yes

## Why this checkpoint exists

The referee pass identified the strongest unresolved scientific risk in the manuscript: all previous retention-versus-release experiments used the same designed edge/corner/ring template bank, so the observed patch-budget phenomenon might reflect generic anchor regularization rather than the spatial structure of predefined templates.

A new fresh-sample experiment was frozen before its outcomes to separate spatial template structure from channel geometry, rank, and generic anchoring.

## Scientific question / engineering objective

Does the release-versus-retention channel-count contrast depend specifically on the original 2D spatial arrangement of the predefined template bank, beyond the bank's Gram matrix, rank, singular spectrum, row norms, and coefficient multisets?

## What was done

The experiment trained and evaluated:

- 100 fresh renderer blocks, 7000--7099;
- 4 init/anchor replicates per block;
- 2 tasks;
- 4 diagnostic architectures: `tiny_gmp`, `tiny_gap`, `plain2_w16_gmp`, `plain2_w16_gap`;
- 2 treatments: constant retention and default annealed release;
- 4 anchor families:
  1. structured edge/corner/ring templates;
  2. a common pixel permutation of the structured bank;
  3. generic random rank-10 bank;
  4. generic random full-rank bank.

Total trained/evaluated models: **25,600 / 25,600**.

The pixel-permuted control preserves the complete structured-bank Gram matrix, numerical rank, singular spectrum, row norms, and row coefficient multisets while destroying the original 2D spatial arrangement.

The inferential unit is the renderer block after averaging four init/anchor replicates, so primary (n=100).

Primary task: `two_concepts`.

Primary metrics:

- centered-logit fidelity;
- unnormalized probability error reduction.

Primary selected-channel contrast: structured minus pixel-permuted (B), averaged over the four diagnostic architectures.

The difference tests use 100,000 sign-flip permutations with Holm correction across the two primary metrics. A TOST equivalence companion and margins were frozen before the full run.

## Evidence or results available now

Integrity:

- training: 25,600 / 25,600 complete;
- evaluation: 25,600 / 25,600 complete;
- maximum full-patch logit error: 0;
- maximum no-op logit error: 0;
- maximum structured-versus-pixel-permuted Gram error: (6.66\times10^{-16}).

### Primary selected-channel spatial specificity

Centered-logit fidelity:

- mean structured-minus-pixel-permuted (B=+0.057426);
- 95% CI ([+0.051165,+0.063686]);
- sign-flip Holm (p=2.0\times10^{-5});
- frozen equivalence margin (\delta=0.017040);
- 90% CI ([+0.052187,+0.062664]);
- Holm TOST (p=1): **not equivalent**.

Probability error reduction:

- mean structured-minus-pixel-permuted (B=+0.045628);
- 95% CI ([+0.037281,+0.053975]);
- sign-flip Holm (p=2.0\times10^{-5});
- frozen equivalence margin (\delta=0.065936);
- 90% CI ([+0.038643,+0.052613]);
- Holm TOST (p=5.03\times10^{-6}): **practically equivalent within the prespecified margin despite being statistically nonzero**.

These two statements are not contradictory: the probability-error difference is precisely estimated away from zero but remains smaller than the frozen smallest effect size of interest.

### Spatial-structure × architecture interaction

Centered-logit fidelity:

- (F(3,297)=91.7943);
- partial (eta^2=0.4811);
- permutation Holm (p=2.0\times10^{-5}).

Probability error reduction:

- (F(3,297)=157.6951);
- partial (eta^2=0.6143);
- permutation Holm (p=2.0\times10^{-5}).

Architecture-specific structured-minus-pixel-permuted selected-channel differences on `two_concepts`:

Centered logits:

- `tiny_gmp`: (+0.10624);
- `tiny_gap`: (+0.07690);
- `plain2_w16_gap`: (+0.09109);
- `plain2_w16_gmp`: **(-0.04453)**.

Probability error reduction:

- `tiny_gmp`: (+0.19953);
- `tiny_gap`: (+0.04308);
- `plain2_w16_gap`: (+0.02057);
- `plain2_w16_gmp`: **(-0.08067)**.

Thus spatial structure has no architecture-independent direction.

### Prespecified random-channel diagnostic

Averaged over architectures, structured minus pixel-permuted random-channel (B):

Centered logits:

- mean (+0.005709);
- 95% CI ([+0.003919,+0.007498]);
- sign-flip (p=1.0\times10^{-5});
- the entire 90% CI lies within the frozen (pm0.017040) margin: practically equivalent.

Probability error reduction:

- mean (+0.020068);
- 95% CI ([+0.017225,+0.022911]);
- sign-flip (p=1.0\times10^{-5});
- the entire 90% CI lies within the frozen (pm0.065936) margin: practically equivalent.

Random-channel spatial-structure × architecture interaction remains nonzero:

- centered logits: partial (eta^2=0.0683), permutation (p=8.0\times10^{-5});
- probability error reduction: partial (eta^2=0.2910), permutation (p=1.0\times10^{-5}).

### Secondary anchor comparisons

On the primary `two_concepts` task, pixel-permuted and generic random rank-10 anchors are generally very similar, and random rank-10 versus random full-rank contrasts are also near zero across the four diagnostic architectures after the frozen within-family corrections.

In contrast, structured-versus-random comparisons reproduce the architecture-dependent sign pattern.

This suggests that the original 2D spatial arrangement, rather than rank alone or generic random channel geometry, is the distinguishing anchor property in the selected-channel analysis.

## Interpretation

The fresh experiment closes the strongest template-specificity objection, but the result is nuanced.

1. **Spatial structure matters for selected-channel centered-logit B.** The structured bank differs clearly and non-equivalently from an exactly Gram/rank/spectrum-matched pixel-permuted bank.
2. **For unnormalized probability-error B, the average spatial effect is statistically nonzero but practically small by the frozen equivalence criterion.** The manuscript must report both facts.
3. **Spatial specificity is strongly architecture-dependent.** The effect reverses sign for `plain2_w16_gmp`, so it is incorrect to claim that structured templates uniformly increase B.
4. **Spatial specificity is much weaker for random channel sets.** Both random-channel metric averages are practically equivalent within the frozen margins even though they are statistically distinguishable from zero.
5. **Rank alone does not explain the result.** Pixel-permuted, random-rank10, and random-fullrank anchors behave similarly in many secondary contrasts.

The strongest final scientific story is therefore not “templates always produce a larger patching effect.” It is:

> preserving the designed 2D structure of first-layer templates changes how the release-versus-retention patch-budget comparison concentrates in validation-selected channels, and this structure-specific effect is strongly conditioned by downstream architecture and output metric.

This is stronger and more precise than the previous generic template-retention framing.

## What this does not establish

- It does not establish a unique mechanism.
- It does not imply human interpretability.
- It does not establish natural-image or large-model generalization.
- It does not show an architecture-independent positive template effect.
- A statistically nonzero probability-error difference must not be described as practically important when the frozen TOST supports equivalence.
- Random-channel equivalence does not mean the full selected-channel phenomenon is an artifact; it shows that spatial specificity is concentrated much more strongly in the selected-channel analysis.

## Repository / provenance pointers

- Protocol: `studies/cnn_anchor_specificity/PROTOCOL.md`
- Implementation: `studies/cnn_anchor_specificity/`
- Analysis: `analysis/anchor_specificity_001/`
- Report: `analysis/anchor_specificity_001/REPORT.md`
- Primary specificity table: `analysis/anchor_specificity_001/primary_spatial_specificity.csv`
- Architecture interaction: `analysis/anchor_specificity_001/primary_spatial_architecture_interaction.csv`
- Random-channel specificity: `analysis/anchor_specificity_001/random_channel_spatial_specificity.csv`
- Complete anchor/architecture summaries: `analysis/anchor_specificity_001/anchor_architecture_B_summary.csv`
- Structural endpoints: `analysis/anchor_specificity_001/structural_endpoint_summary.csv`
- Execution manifest launch head: `396950dc6fecac2738d79aab808710419701a3fb`
- External run root at execution: `%LOCALAPPDATA%\prior-templates-cnns\results\anchor_specificity_cuda_001`

## Next actions

1. Update `RESEARCH_STATUS.md` and `.ai_handoff` with the completed fresh-sample result.
2. Rewrite the manuscript around the now-supported structure-specific but architecture/metric-dependent conclusion.
3. Add the anchor-specificity result to the main results figure or a compact new panel/figure.
4. Integrate the post hoc sphericity-robust/random-channel architecture diagnostics as secondary robustness evidence.
5. Perform a new referee pass after the rewrite before deciding whether any external controlled benchmark is still necessary.

## Do-not-forget constraints

- Report the probability-error result as statistically nonzero **and** practically equivalent under the frozen margin.
- Do not collapse the four architectures into a universal positive template effect.
- Do not hide the negative `plain2_w16_gmp` structured-minus-pixel-permuted contrast.
- Keep random-channel specificity in the paper; it materially constrains interpretation.
- The inferential sample is 100 renderer blocks, not 25,600 models.
- Do not alter the frozen protocol retrospectively.
