#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
python_bin="${PYTHON:-python3}"
if ! "$python_bin" -c 'import torch, numpy, scipy, pandas, matplotlib, PIL' >/dev/null 2>&1; then
  echo 'Missing analysis dependencies. Activate your experiment environment, or run:' >&2
  echo "$python_bin -m pip install -r analysis/kernel_similarity/requirements.txt" >&2
  exit 1
fi
"$python_bin" analysis/kernel_similarity/analyze.py "$@"
