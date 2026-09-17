#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if [[ -n "${PYTHON:-}" ]]; then
  py="$PYTHON"
elif [[ -x studies/cnn_release_experiment/.venv/bin/python ]]; then
  py=studies/cnn_release_experiment/.venv/bin/python
else
  py=python3
fi

exec "$py" analysis/patch_robustness_gpu_001/review.py
