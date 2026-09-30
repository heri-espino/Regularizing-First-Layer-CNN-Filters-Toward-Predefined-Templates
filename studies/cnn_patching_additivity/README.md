# CNN patching additivity

Post-hoc mechanistic decomposition of the completed architecture-robustness and filter-bank-control checkpoints. This study **never trains models** and never overwrites the source runs.

Read [`PROTOCOL.md`](PROTOCOL.md) before execution. [`IMPLEMENTATION_MANIFEST.json`](IMPLEMENTATION_MANIFEST.json) records the exact implementation/source Git blobs and the implementation-only validation state.

## Inputs

Default university-machine roots:

```powershell
$ArchRoot   = "$env:LOCALAPPDATA\prior-templates-cnns\results\architecture_robustness_cuda_001"
$AnchorRoot = "$env:LOCALAPPDATA\prior-templates-cnns\results\anchor_specificity_cuda_001"
$OutRoot    = "$env:LOCALAPPDATA\prior-templates-cnns\results\patching_additivity_001"
```

Each source root must already contain completed `training/` and `evaluation/` trees plus `execution_manifest.json`.

## 1. Inventory only

```powershell
python studies/cnn_patching_additivity/evaluate.py inventory `
  --source architecture --input $ArchRoot `
  --output "$OutRoot\inventory_architecture.json"

python studies/cnn_patching_additivity/evaluate.py inventory `
  --source anchor --input $AnchorRoot `
  --output "$OutRoot\inventory_anchor.json"
```

This verifies counts, completion markers, sample checkpoint loading, source manifests, and frozen source Git blobs.

## 2. Predetermined technical validation + benchmark

```powershell
python studies/cnn_patching_additivity/validate.py `
  --architecture-root $ArchRoot `
  --anchor-root $AnchorRoot `
  --output "$OutRoot\validation" `
  --device cuda `
  --batch-size 256
```

The validator uses the first renderer block by numeric identifier, the four core architectures, both tasks/treatments, all four initialization replicates, and both primary filter banks. It checks:

- no-op and full-patch identities;
- singleton (`k=1`) residual identity;
- exact tiny-network additivity;
- the three algebraic decompositions;
- stored versus recomputed validation rankings;
- reproduction of source metrics;
- batch-size stability (64 vs 256);
- no mutation of cached activations;
- resume behavior;
- runtime and storage estimates.

Do not run the full grid if this step fails.

## 3. Full primary run

The convenience launcher evaluates exact selected, random, and energy-matched source sets and resumes after interruption:

```powershell
.\studies\cnn_patching_additivity\run_patching_additivity.ps1 -Mode Main
```

Equivalent direct commands:

```powershell
python studies/cnn_patching_additivity/evaluate.py run `
  --source architecture `
  --input $ArchRoot `
  --output "$OutRoot\architecture" `
  --device cuda --batch-size 256 `
  --set-families selected random energy

python studies/cnn_patching_additivity/evaluate.py run `
  --source anchor `
  --input $AnchorRoot `
  --output "$OutRoot\anchor" `
  --device cuda --batch-size 256 `
  --anchor-families structured_template pixel_permuted_template `
  --set-families selected random energy
```

Running either command again is the resume operation: complete model JSON files are skipped after the design/source compatibility check.

## 4. Analysis and report

```powershell
python studies/cnn_patching_additivity/analyze.py `
  --source architecture `
  --input "$OutRoot\architecture" `
  --out "$OutRoot\architecture_analysis"

python studies/cnn_patching_additivity/analyze.py `
  --source anchor `
  --input "$OutRoot\anchor" `
  --out "$OutRoot\anchor_analysis"
```

The reports aggregate at renderer-block level after averaging the four initialization replicates. Per-model JSON also retains the 16 x 16 mean singleton cross-product matrix. Outputs include observed-versus-additive curves, residual/cancellation geometry, exact squared-error correction terms, release-minus-retention `B`, structured-versus-pixel-permuted contrasts, pointwise block-bootstrap intervals, and explicitly labeled simultaneous across-intervention-size reconstruction-gap bands.

## Optional per-pair arrays

For a small predetermined diagnostic run only:

```powershell
python studies/cnn_patching_additivity/evaluate.py run `
  --source architecture --input $ArchRoot `
  --output "$OutRoot\pair_array_debug" `
  --device cuda --max-blocks 1 `
  --architectures tiny_gmp tiny_gap plain2_w16_gmp plain2_w16_gap `
  --set-families selected `
  --save-pair-arrays
```

The full grid computes all quantities per pair before aggregation but does not save pair arrays by default because they can dominate storage.

## Secondary random filter banks

`random_rank10` and `random_fullrank` are not part of the central filter-bank decomposition. The technical benchmark writes `VALIDATION_AND_BENCHMARK.json` and applies the frozen cost-only rule in the protocol. If and only if that file says `run_secondary_anchors: true`, run them into a separate output tree before inspecting their additivity outcomes:

```powershell
.\studies\cnn_patching_additivity\run_patching_additivity.ps1 -Mode Secondary
```

The launcher refuses this mode when the cost-only rule does not permit it.

## Pure algebra tests

```powershell
python studies/cnn_patching_additivity/test_math.py
python studies/cnn_patching_additivity/test_integration.py
```

These tests require no saved checkpoints. The second test verifies whole-channel logit additivity for a tiny pooling-plus-linear tail.