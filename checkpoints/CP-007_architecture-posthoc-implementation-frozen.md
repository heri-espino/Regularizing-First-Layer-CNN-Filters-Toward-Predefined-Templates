# CP-007 — Post hoc architecture diagnostics frozen

**Date:** reconstructed 2026-09-21  
**Status:** implementation complete; diagnostic run pending/current  
**Evidential role:** outcome-informed post hoc robustness  
**Contemporaneous:** no

## Why this checkpoint exists

The completed architecture study is strong, but several reviewer-facing diagnostics can be answered using the saved Stage-F evaluator outputs without retraining:

- repeated-measures inference without relying on sphericity;
- whether architecture dependence survives random channel selection;
- whether structural retention differences directly track functional (B);
- exact reconstructable architecture definitions.

## Scientific / engineering objective

Reanalyze the completed Stage-F outputs under robust statistical and diagnostic views while preserving the distinction between prospective evidence and post hoc checks.

## What was done

A separate analysis workflow was frozen under `studies/cnn_architecture_posthoc/`.

It performs:

1. Greenhouse--Geisser corrected repeated-measures inference;
2. 100,000 within-block architecture-label permutations;
3. Friedman rank-based sensitivity tests;
4. random-channel (B) architecture omnibus;
5. selected-minus-random architecture diagnostics;
6. random-channel TinyGMP minus Plain2-GMP bridge;
7. direct template-retention difference vs functional (B);
8. within-architecture Spearman correlations with bootstrap intervals;
9. machine-generated exact architecture definitions and parameter counts.

No model retraining occurs.

## Evidence or results available now

At this checkpoint, no new post hoc output is interpreted yet.

However, referee inspection of archived aggregate random-channel controls already suggested that architecture-dependent (B) is not limited to validation-ranked channels. That observation motivated this formal diagnostic workflow and makes the analysis explicitly outcome-informed.

## Interpretation

If architecture heterogeneity remains strong for random channel sets, the main phenomenon should be framed more broadly as a property of **patch budget × downstream architecture × training condition**, not as something requiring specially ranked “concept” channels.

If selected-vs-random differences remain important, that becomes a separate modifier rather than the source of the entire architecture result.

## What this does not establish

- These diagnostics are not prospective confirmation.
- They cannot retroactively change Stage-F's frozen primary analysis.
- Correlation between structural retention and (B) is descriptive, not mediation.
- Robust significance does not imply universal architecture laws.

## Repository / provenance pointers

- Protocol: `studies/cnn_architecture_posthoc/PROTOCOL.md`
- Analyzer: `studies/cnn_architecture_posthoc/analyze.py`
- Launcher: `run/run_architecture_posthoc.ps1`
- Staging helper: `run/stage_architecture_posthoc_results.ps1`
- Source Stage-F evaluation root: `%LOCALAPPDATA%\prior-templates-cnns\results\architecture_robustness_cuda_001\evaluation`

## Next actions

1. Run `.\run\run_architecture_posthoc.ps1`.
2. Archive outputs.
3. Create a **new checkpoint** for the observed diagnostics.
4. Update manuscript inference language only after those outputs are reviewed.

## Do-not-forget constraints

- Always call this analysis “post hoc” or “outcome-informed.”
- Do not describe it as a fresh replication.
- No retraining is required.
