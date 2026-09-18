#!/usr/bin/env zsh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec zsh "$SCRIPT_DIR/../studies/cnn_metric_sensitivity/run_metric_sensitivity.zsh" "$@"
