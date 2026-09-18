# Frozen metric-sensitivity analysis on saved Stage-D and Stage-E checkpoints

Protocol frozen: 2026-09-18

## Status and motivation

This study is designed **after** the Stage-D and Stage-E probability-space patching results are known and after manuscript review identified dependence on the normalization used by the patching metric as a remaining methodological concern. It is therefore a **post hoc robustness analysis of existing checkpoints**, not a new confirmation sample and not an independent replication.

The protocol is frozen **before any centered-logit fidelity or unnormalized reconstruction-error results from Stage D or Stage E are generated or inspected**.

No model is retrained. No channel ranking, checkpoint, intervention budget, task, architecture, regularization profile, or matched counterfactual pair is changed based on the new metrics.

## Inputs

### Stage D

Read the completed budget_confirmation_001 artifact:

- task: two_concepts;
- architectures: TinyCNN, TwoLayerCNN;
- blocks: 4000--4019;
- conditions: template_retention_1, template_release;
- checkpoint: epoch 200;
- stored validation-only rankings: contrast, auroc, validation_patch;
- intervention budgets: k in {1,2,4,8}.

The exact stored ranking arrays from the original Stage-D patch evaluation are reused rather than recomputed.

### Stage E

Read the completed exhaustive_robustness_001 artifact:

- tasks: single_shape, two_concepts;
- architectures: TinyCNN, TwoLayerCNN;
- blocks: 5000--5049;
- profiles: template_init, retention_0p1, retention_1, release_early, release_default, release_late;
- checkpoint: epoch 200;
- stored validation-only rankings: contrast, auroc, validation_patch;
- intervention budgets: k=1,...,16.

The exact stored Stage-E ranking arrays are reused.

## Fixed patching procedure

For every saved model and test matched pair, let

- \(\ell_0\): base-image logits,
- \(\ell_1\): actual counterfactual-image logits,
- \(\ell_S\): patched-base logits after replacing first-layer activation maps for channel set \(S\),
- \(p_0,p_1,p_S\): the corresponding softmax probability vectors.

The first-layer activation replacement itself is unchanged from Stages C--E. Full-channel and no-op identities must hold within the existing numerical tolerances.

The hundreds of matched pairs within a model are used only to construct one metric value for that model/block/condition/profile. They are not inferential replicates.

## Metrics

### Existing probability fidelity: integrity anchor

Recompute the original metric

\[
F_{\mathrm{prob}}(S)
=
1-
\frac{\sum\|p_S-p_1\|_2^2}
     {\sum\|p_1-p_0\|_2^2}.
\]

The recomputed value must agree with the stored Stage-D/Stage-E selected-channel fidelity within tolerance. This is an evaluator integrity check, not a new result.

### Primary robustness metric 1: centered-logit fidelity

Raw logits have an arbitrary common-offset degree of freedom because adding the same scalar to all class logits leaves softmax probabilities unchanged. Therefore define per-example centered logits

\[
\widetilde\ell
=
\ell-\frac{1}{C}\mathbf 1\mathbf 1^\top\ell,
\]

equivalently subtracting the mean logit across classes for each example.

The first primary metric-sensitivity measure is

\[
F_{\mathrm{clogit}}(S)
=
1-
\frac{\sum\|\widetilde\ell_S-\widetilde\ell_1\|_2^2}
     {\sum\|\widetilde\ell_1-\widetilde\ell_0\|_2^2}.
\]

It has the same error-reduction interpretation as \(F_{\mathrm{prob}}\), but in centered-logit space.

### Primary robustness metric 2: absolute probability error reduction

To remove the model-specific normalization by the input-induced output change, define the mean per-pair probability reconstruction errors

\[
E^{\mathrm{prob}}_0
=
\frac1N\sum\|p_0-p_1\|_2^2,
\qquad
E^{\mathrm{prob}}_S
=
\frac1N\sum\|p_S-p_1\|_2^2,
\]

and the absolute reduction

\[
R_{\mathrm{prob}}(S)
=
E^{\mathrm{prob}}_0-E^{\mathrm{prob}}_S.
\]

Positive values mean that patching moves the model output closer to the actual counterfactual output. This quantity is not divided by \(E^{\mathrm{prob}}_0\).

### Secondary metric diagnostics

Also retain:

1. raw-logit fidelity
   \[
   F_{\mathrm{logit}}(S)
   =
   1-
   \frac{\sum\|\ell_S-\ell_1\|_2^2}
        {\sum\|\ell_1-\ell_0\|_2^2};
   \]
2. centered-logit absolute error reduction
   \[
   R_{\mathrm{clogit}}(S)
   =
   E^{\mathrm{clogit}}_0-E^{\mathrm{clogit}}_S;
   \]
3. raw-logit absolute error reduction;
4. patched-run counterfactual-target accuracy;
5. agreement with the model's actual counterfactual prediction;
6. the three model-level input-effect scales
   \(E^{\mathrm{prob}}_0\), \(E^{\mathrm{clogit}}_0\), and \(E^{\mathrm{logit}}_0\).

No metric is dropped after seeing its outcome.

## Stage-D metric-sensitivity estimand

For metric \(M\), block \(b\), ranking \(r\), and budget \(k\), define

\[
\Delta^M_{b,r}(k)
=
M^{\mathrm{release}}_{b,r}(k)
-
M^{\mathrm{retention}}_{b,r}(k).
\]

For compatibility with the frozen Stage-D analysis define

\[
B^M_{b,r}
=
\frac{\Delta^M_{b,r}(4)+\Delta^M_{b,r}(8)}{2}
-
\frac{\Delta^M_{b,r}(1)+\Delta^M_{b,r}(2)}{2}.
\]

The **primary metric-sensitivity setting** remains two_concepts / TinyCNN / contrast. Report, for both primary robustness metrics \(F_{\mathrm{clogit}}\) and \(R_{\mathrm{prob}}\):

- all four \(\Delta^M(k)\) means and marginal 95% paired Student-t intervals;
- block-level \(B^M_b\);
- mean \(B^M\), SD, 95% Student-t interval, t statistic, and two-sided p value.

The two primary metric p-values are Holm-adjusted as one two-test family. This robustness analysis has **no binary confirmation/rejection rule**; effect sizes and intervals are primary.

Raw-logit fidelity and all alternative rankings/architectures are secondary diagnostics.

Also compare the model-level input-effect scales between release and retention across the same 20 paired blocks. This directly exposes whether the denominator of a normalized metric changes across treatments.

## Stage-E extension

Stage E remains secondary. For each metric, profile \(p\), block \(b\), task/architecture setting \(s\), ranking \(r\), and budget \(k\), compute

\[
\Delta^M_{b,p,s,r}(k)
=
M_{b,p,s,r}(k)
-
M_{b,\mathrm{retention1},s,r}(k),
\]

and the same \(B^M\) contrast using \(k\in\{1,2,4,8\}\).

For each metric separately, five profile-versus-retention_1 p-values are Holm-adjusted within each task/architecture/ranking family, matching the Stage-E multiplicity structure. Full \(k=1,...,16\) curves are retained for the primary contrast ranking.

Stage-E results do not redefine the Stage-D metric-sensitivity question.

## Integrity and provenance

- No training code is invoked.
- Existing checkpoints and stored ranking arrays are read-only.
- Every output records checkpoint and ranking-file hashes.
- Existing Stage-D/Stage-E probability fidelity is recomputed and compared with the stored value.
- Full-patch logits must reproduce actual counterfactual logits within tolerance.
- No-op logits must reproduce base logits within tolerance.
- Undefined normalized metrics are retained as undefined if their denominator is below \(10^{-10}\).
- Source hashes, protocol hash/commit, execution environment, input design hashes, and output manifests are retained.
- Partial results may be resumed only under an identical design/source manifest.
- No result from this study may be used to alter this protocol.

## Interpretation boundary

This study asks whether the previously observed channel-count contrast is specific to the original normalized probability-space metric.

Agreement across \(F_{\mathrm{prob}}\), centered-logit fidelity, and absolute probability error reduction would strengthen robustness to metric choice and to the normalization denominator. Disagreement would be reported as metric dependence rather than hidden or averaged away.

Even agreement across these metrics would not establish a unique mechanism, natural-image generalization, human interpretability, or architecture-independent behavior.
