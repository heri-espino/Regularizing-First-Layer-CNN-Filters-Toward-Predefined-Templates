# CP-016 — BOM-safe source JSON compatibility fix

**Date:** 2026-09-30  
**Status:** design-preserving implementation fix; source-study validation pending rerun  
**Evidential role:** implementation-only / post-hoc workflow maintenance  
**Contemporaneous:** yes

## Why this checkpoint exists

The first real university-VM invocation of the patching-additivity workflow failed during both \`-Mode Inventory\` and \`-Mode Validate\` while reading the completed Stage-F \`execution_manifest.json\`.

Python raised:

\`\`\`text
json.decoder.JSONDecodeError: Unexpected UTF-8 BOM (decode using utf-8-sig)
\`\`\`

The source manifest was written by Windows PowerShell using UTF-8 with a byte-order mark (BOM). The new evaluator had assumed BOM-free UTF-8.

The attempted \`-Mode Main\` then correctly refused to run because the required validation/benchmark artifact had not been produced.

## Scientific question / engineering objective

Make the saved-checkpoint evaluator compatible with both BOM-prefixed Windows PowerShell JSON and ordinary BOM-free UTF-8 JSON without changing any scientific estimand, model, intervention, ranking, control, tolerance, or analysis rule.

## What was done

This is a **design-preserving implementation fix**.

In \`studies/cnn_patching_additivity/evaluate.py\`:

- added a single \`read_json(path)\` helper using \`Path.read_text(encoding="utf-8-sig")\`;
- routed source training designs, evaluation designs, execution manifests, original per-model evaluation JSON, and resumable additivity design JSON through that helper;
- retained \`atomic_json(..., encoding="utf-8")\` for newly written outputs.

\`utf-8-sig\` strips an optional BOM but reads BOM-free UTF-8 normally, so the change is backwards-compatible.

Added \`studies/cnn_patching_additivity/test_json_io.py\`, which writes the same payload once as plain UTF-8 and once as UTF-8 with BOM and requires \`read_json\` to return identical objects for both.

The lightweight GitHub Actions workflow now:

- compiles \`test_json_io.py\`;
- executes the BOM reader test;
- executes the algebra self-test;
- executes the analytic Tiny whole-channel additivity integration test.

## Evidence or results available now

No scientific Stage-F/G additivity outcomes are available or interpreted at this checkpoint.

Observed real-machine evidence before the fix:

- Python 3.11.16;
- PyTorch 2.11.0+cu128;
- CUDA available;
- NVIDIA RTX 4500 Ada Generation;
- 23.99 GiB VRAM;
- \`Inventory\` failed only at JSON decoding of the source execution manifest;
- \`Validate\` failed at the same read;
- \`Main\` correctly enforced the validation gate.

The JSON compatibility bug is fixed in source and covered by an explicit regression test. The real VM inventory/validation still needs to be rerun after pulling the fix.

## Interpretation

The failure did not indicate checkpoint corruption, missing models, CUDA problems, or a scientific inconsistency. It occurred before inventory of the source model grid and before any new patching-additivity outcome was evaluated.

The \`Main\` refusal is expected and desirable: the workflow prevented a full run after failed validation.

## What this does not establish

- It does not establish that source checkpoint counts or hashes pass inventory; that will be checked on rerun.
- It does not establish that the predetermined real-model additivity validation passes.
- It does not change the frozen post-hoc protocol.
- It does not create or alter any scientific result.

## Repository / provenance pointers

- Protocol: \`studies/cnn_patching_additivity/PROTOCOL.md\`
- Fixed evaluator: \`studies/cnn_patching_additivity/evaluate.py\`
- Regression test: \`studies/cnn_patching_additivity/test_json_io.py\`
- Launcher: \`run/run_patching_additivity.ps1\`
- Previous implementation checkpoint: \`checkpoints/CP-015_patching-additivity-implementation.md\`
- Source roots remain unchanged under \`%LOCALAPPDATA%\prior-templates-cnns\results\`

## Next actions

On the university VM:

\`\`\`powershell
git pull --ff-only origin main
.\run\run_patching_additivity.ps1 -Mode Inventory
.\run\run_patching_additivity.ps1 -Mode Validate
\`\`\`

Only after \`Validate\` completes successfully:

\`\`\`powershell
.\run\run_patching_additivity.ps1 -Mode Main
\`\`\`

## Do-not-forget constraints

- Do not delete or rewrite the original Stage-F/G manifests merely to remove their BOM.
- Do not bypass the validation gate.
- Treat any new failure after this fix as a separate integrity/compatibility issue rather than weakening checks.
- Do not interpret partial validation output as scientific evidence.
