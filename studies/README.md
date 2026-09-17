# Study map

The manuscript combines several experiments with different inferential roles. The directories are preserved separately so that frozen protocols, source hashes, and execution history remain traceable.

| Stage | Directory | Role in the paper |
|---|---|---|
| Pilot | `cnn_first_pass/` | Historical first pass; not used as confirmatory evidence |
| A | `cnn_causal_milestone/` | 400-model alignment/intervention study and frozen-feature diagnostic |
| B | `cnn_release_experiment/` | 200-model, 200-epoch retention/release study |
| C | `cnn_patch_robustness/` | Post hoc patch-size/ranking sensitivity on saved Stage-B checkpoints |
| C control | `cnn_patch_energy_control/` | Post hoc validation-energy-matched control |
| D | `cnn_budget_confirmation/` | Frozen prospective confirmation on 20 new blocks |
| E | `cnn_exhaustive_robustness/` | Predeclared secondary 1,200-model sensitivity study on 50 new blocks |
| Audit | `cnn_checkpoint_audit/` | Independent reimplementation audit on fixed saved checkpoints |

## Recommended reading order

1. Read `../paper/main.tex` or build the manuscript with `python paper/build.py` from the repository root.
2. Read `cnn_budget_confirmation/PROTOCOL.md` and `../analysis/budget_confirmation_001/REPORT.md` for the prospective primary result.
3. Read `cnn_exhaustive_robustness/PROTOCOL.md` and `../analysis/exhaustive_robustness_001/REPORT.md` for the larger secondary sensitivity study.
4. Read `cnn_checkpoint_audit/AUDIT_PROTOCOL.md` and `../analysis/checkpoint_audit/AUDIT_REPORT.md` for the independent implementation check.
5. Return to Stages A--C when tracing how the final confirmatory estimand was developed.

Stages A--C motivated the final analysis but are not treated as independent confirmations of Stage D. Stage D contains the single prospective primary test. Stage E was separately frozen and is reported as a secondary sensitivity study; it does not redefine the Stage-D primary hypothesis.

Historical source files are kept in place even when later code superseded them. This is deliberate: the repository is an archival research record, not a single production package.
