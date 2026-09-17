#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
mode="${1:-main}"
if [[ $# -gt 0 ]]; then shift; fi

if [[ -n "${PYTHON:-}" ]]; then
  py="$PYTHON"
elif [[ -x studies/cnn_release_experiment/.venv/bin/python ]]; then
  py=studies/cnn_release_experiment/.venv/bin/python
else
  py=python3
fi

case "$mode" in
  check)
    "$py" -c 'import torch; print("PyTorch:",torch.__version__); assert torch.cuda.is_available(), "CUDA unavailable; activate your CUDA PyTorch environment"; print("GPU:",torch.cuda.get_device_name(0)); print("VRAM GiB:",round(torch.cuda.get_device_properties(0).total_memory/2**30,1)); x=torch.randn(16,16,device="cuda"); print("CUDA operation:",(x@x).sum().item())'
    ;;
  smoke)
    "$py" studies/cnn_patch_robustness/evaluate_gpu.py --smoke --output outputs/patch_robustness_smoke "$@"
    ;;
  main)
    "$py" studies/cnn_patch_robustness/evaluate_gpu.py "$@"
    ;;
  report)
    "$py" studies/cnn_patch_robustness/summarize.py "${1:-outputs/patch_robustness}"
    ;;
  *)
    echo 'Usage: bash run/run_gpu.sh [check|smoke|main|report] [options]'
    exit 2
    ;;
esac
