#!/usr/bin/env zsh
# Frozen checkpoint-only patching metric-sensitivity analysis.
# No training code is invoked.

set -e
setopt pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

if [[ -z "$STAGE_D_ROOT" ]]; then STAGE_D_ROOT="results/budget_confirmation_001"; fi
if [[ -z "$STAGE_E_ROOT" ]]; then STAGE_E_ROOT="results/exhaustive_robustness_001"; fi
if [[ -z "$OUTPUT_ROOT" ]]; then OUTPUT_ROOT="results/metric_sensitivity_001"; fi
if [[ -z "$DEVICE" ]]; then DEVICE="cuda"; fi
if [[ -z "$BATCH_SIZE" ]]; then BATCH_SIZE="256"; fi
if [[ -z "$CNN_ENV_NAME" ]]; then CNN_ENV_NAME="prior-templates-cnns"; fi
export CNN_ENV_NAME

if [[ "$DEVICE" != "cuda" && "$DEVICE" != "cpu" ]]; then
  print -u2 "DEVICE must be cuda or cpu; got: $DEVICE"
  exit 2
fi
if (( BATCH_SIZE < 1 )); then
  print -u2 "BATCH_SIZE must be positive."
  exit 2
fi
if ! command -v git >/dev/null 2>&1; then
  print -u2 "git is required for provenance recording."
  exit 2
fi

source "$REPO_ROOT/scripts/use_conda_env.zsh"

for required in \
  "$STAGE_D_ROOT/training/design.json" \
  "$STAGE_D_ROOT/patch_eval/design.json" \
  "$STAGE_E_ROOT/training/design.json" \
  "$STAGE_E_ROOT/evaluation/design.json"; do
  if [[ ! -f "$required" ]]; then
    print -u2 "Missing required frozen input: $required"
    exit 2
  fi
done

STAGE_D_OUT="$OUTPUT_ROOT/stage_d"
STAGE_E_OUT="$OUTPUT_ROOT/stage_e"
ANALYSIS_OUT="$OUTPUT_ROOT/analysis"
MANIFEST="$OUTPUT_ROOT/execution_manifest.json"
PROTOCOL="studies/cnn_metric_sensitivity/PROTOCOL.md"
EVALUATOR="studies/cnn_metric_sensitivity/evaluate_metrics.py"
ANALYZER="studies/cnn_metric_sensitivity/analyze_metrics.py"

mkdir -p "$OUTPUT_ROOT"
PROTOCOL_COMMIT="$(git log -n 1 --format=%H -- "$PROTOCOL")"
REPO_HEAD="$(git rev-parse HEAD)"

cnn_python - \
  "$MANIFEST" \
  "$REPO_HEAD" \
  "$PROTOCOL_COMMIT" \
  "$DEVICE" \
  "$BATCH_SIZE" \
  "$STAGE_D_ROOT" \
  "$STAGE_E_ROOT" <<'PY'
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy
import scipy
import torch

manifest = Path(sys.argv[1])
repo_head, protocol_commit, device, batch_size, stage_d_root, stage_e_root = sys.argv[2:]
stage_d_root = Path(stage_d_root).resolve()
stage_e_root = Path(stage_e_root).resolve()

protocol = Path("studies/cnn_metric_sensitivity/PROTOCOL.md")
evaluator = Path("studies/cnn_metric_sensitivity/evaluate_metrics.py")
analyzer = Path("studies/cnn_metric_sensitivity/analyze_metrics.py")
core = Path("studies/cnn_release_experiment/core.py")

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

record = {
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "repo_head_at_launch": repo_head,
    "protocol_commit": protocol_commit,
    "protocol_sha256": sha(protocol),
    "device": device,
    "batch_size": int(batch_size),
    "stage_d_root": str(stage_d_root),
    "stage_e_root": str(stage_e_root),
    "python": sys.version,
    "python_executable": sys.executable,
    "platform": platform.platform(),
    "torch": torch.__version__,
    "numpy": numpy.__version__,
    "scipy": scipy.__version__,
    "cuda_available": torch.cuda.is_available(),
    "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    "source_sha256": {
        "protocol": sha(protocol),
        "evaluator": sha(evaluator),
        "analyzer": sha(analyzer),
        "core": sha(core),
    },
    "input_design_sha256": {
        "stage_d_training": sha(stage_d_root / "training" / "design.json"),
        "stage_d_rankings": sha(stage_d_root / "patch_eval" / "design.json"),
        "stage_e_training": sha(stage_e_root / "training" / "design.json"),
        "stage_e_rankings": sha(stage_e_root / "evaluation" / "design.json"),
    },
    "training_invoked": False,
}

immutable = [
    "protocol_sha256",
    "device",
    "batch_size",
    "stage_d_root",
    "stage_e_root",
    "source_sha256",
    "input_design_sha256",
    "training_invoked",
]
if manifest.exists():
    old = json.loads(manifest.read_text())
    changed = [k for k in immutable if old.get(k) != record.get(k)]
    if changed:
        raise SystemExit(
            "Existing metric-sensitivity manifest is incompatible ("
            + ", ".join(changed)
            + "). Use a new OUTPUT_ROOT."
        )
else:
    tmp = manifest.with_suffix(".tmp")
    tmp.write_text(json.dumps(record, indent=2) + "\n")
    tmp.replace(manifest)

print("Execution manifest:", manifest)
print("Protocol commit:", protocol_commit)
print("Conda Python:", sys.executable)
print("GPU:", record["gpu"])
print("Training invoked:", record["training_invoked"])
PY

print ""
print "Protocol commit: $PROTOCOL_COMMIT"
print "No training will be run."

print ""
print "[1/3] Re-evaluating Stage D checkpoints under frozen alternative metrics..."
cnn_python "$EVALUATOR" \
  --stage d \
  --input-root "$STAGE_D_ROOT" \
  --output "$STAGE_D_OUT" \
  --device "$DEVICE" \
  --batch-size "$BATCH_SIZE"

print ""
print "[2/3] Re-evaluating Stage E checkpoints under frozen alternative metrics..."
cnn_python "$EVALUATOR" \
  --stage e \
  --input-root "$STAGE_E_ROOT" \
  --output "$STAGE_E_OUT" \
  --device "$DEVICE" \
  --batch-size "$BATCH_SIZE"

print ""
print "[3/3] Applying the frozen metric-sensitivity analysis..."
cnn_python "$ANALYZER" \
  --stage-d "$STAGE_D_OUT" \
  --stage-e "$STAGE_E_OUT" \
  --out "$ANALYSIS_OUT"

print ""
print "Metric-sensitivity study complete."
print "Report:   $ANALYSIS_OUT/REPORT.md"
print "Manifest: $MANIFEST"
