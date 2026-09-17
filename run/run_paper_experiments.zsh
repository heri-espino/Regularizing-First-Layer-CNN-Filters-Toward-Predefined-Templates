#!/usr/bin/env zsh
# Run the frozen prospective confirmation followed by the separate
# Stage-E sensitivity study. Both child launchers use the same user-space
# Conda environment and require no administrator privileges.

set -e
set -u
setopt pipefail

SCRIPT_DIR="${0:A:h}"
REPO_ROOT="${SCRIPT_DIR:h}"
cd "$REPO_ROOT"

print "=== Stage D: frozen prospective confirmation (blocks 4000-4019) ==="
zsh studies/cnn_budget_confirmation/run_confirmation.zsh

print ""
print "=== Stage E: secondary sensitivity study (blocks 5000-5049) ==="
zsh studies/cnn_exhaustive_robustness/run_exhaustive.zsh

print ""
print "All planned paper experiments finished."
print "Primary confirmation report: results/budget_confirmation_001/analysis/budget_confirmation/REPORT.md"
print "Sensitivity-study report: results/exhaustive_robustness_001/analysis/REPORT.md"
