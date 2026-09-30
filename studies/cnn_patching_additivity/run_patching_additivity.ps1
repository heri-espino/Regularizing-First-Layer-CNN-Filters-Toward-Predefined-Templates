param(
    [ValidateSet('Inventory','Validate','Main','Secondary','Analyze')][string]$Mode = 'Validate',
    [string]$ArchitectureRoot = $(Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'prior-templates-cnns\results\architecture_robustness_cuda_001'),
    [string]$AnchorRoot = $(Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'prior-templates-cnns\results\anchor_specificity_cuda_001'),
    [string]$OutputRoot = $(Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'prior-templates-cnns\results\patching_additivity_001'),
    [ValidateSet('cpu','cuda')][string]$Device = 'cuda',
    [int]$BatchSize = 256,
    [string]$CondaEnv = $(if ($env:CNN_ENV_NAME) { $env:CNN_ENV_NAME } else { 'prior-templates-cnns' })
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($BatchSize -lt 1) { throw 'BatchSize must be positive.' }

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Push-Location $RepoRoot
try {
    $env:DEVICE = $Device
    $env:CNN_ENV_NAME = $CondaEnv
    . (Join-Path $RepoRoot 'scripts\use_conda_env.ps1')

    $Eval = 'studies/cnn_patching_additivity/evaluate.py'
    $Validate = 'studies/cnn_patching_additivity/validate.py'
    $Analyze = 'studies/cnn_patching_additivity/analyze.py'
    New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

    if ($Mode -eq 'Inventory') {
        Invoke-CnnPython $Eval 'inventory' '--source' 'architecture' '--input' $ArchitectureRoot '--output' (Join-Path $OutputRoot 'inventory_architecture.json')
        Invoke-CnnPython $Eval 'inventory' '--source' 'anchor' '--input' $AnchorRoot '--output' (Join-Path $OutputRoot 'inventory_anchor.json')
        return
    }

    if ($Mode -eq 'Validate') {
        Invoke-CnnPython $Validate `
            '--architecture-root' $ArchitectureRoot `
            '--anchor-root' $AnchorRoot `
            '--output' (Join-Path $OutputRoot 'validation') `
            '--device' $Device '--batch-size' "$BatchSize"
        return
    }

    if ($Mode -eq 'Main') {
        if ($Device -ne 'cuda') {
            throw 'The full additivity grid is intentionally not launched silently on CPU. Run Validate/Inventory on CPU or explicitly call evaluate.py yourself.'
        }
        $Benchmark = Join-Path $OutputRoot 'validation\VALIDATION_AND_BENCHMARK.json'
        if (-not (Test-Path -LiteralPath $Benchmark)) {
            throw 'Run -Mode Validate first. The full run requires the predetermined technical validation and benchmark artifact.'
        }
        Invoke-CnnPython $Eval 'run' `
            '--source' 'architecture' '--input' $ArchitectureRoot '--output' (Join-Path $OutputRoot 'architecture') `
            '--device' $Device '--batch-size' "$BatchSize" `
            '--set-families' 'selected' 'random' 'energy'

        Invoke-CnnPython $Eval 'run' `
            '--source' 'anchor' '--input' $AnchorRoot '--output' (Join-Path $OutputRoot 'anchor') `
            '--device' $Device '--batch-size' "$BatchSize" `
            '--anchor-families' 'structured_template' 'pixel_permuted_template' `
            '--set-families' 'selected' 'random' 'energy'

        Invoke-CnnPython $Analyze '--source' 'architecture' '--input' (Join-Path $OutputRoot 'architecture') '--out' (Join-Path $OutputRoot 'architecture_analysis')
        Invoke-CnnPython $Analyze '--source' 'anchor' '--input' (Join-Path $OutputRoot 'anchor') '--out' (Join-Path $OutputRoot 'anchor_analysis')
        return
    }


    if ($Mode -eq 'Secondary') {
        if ($Device -ne 'cuda') {
            throw 'The secondary full-anchor extension is not launched silently on CPU.'
        }
        $Benchmark = Join-Path $OutputRoot 'validation\VALIDATION_AND_BENCHMARK.json'
        if (-not (Test-Path -LiteralPath $Benchmark)) {
            throw 'Run -Mode Validate first.'
        }
        $Bench = Get-Content -LiteralPath $Benchmark -Raw | ConvertFrom-Json
        if (-not [bool]$Bench.secondary_anchor_predeclared_cost_rule.run_secondary_anchors) {
            throw 'The frozen cost-only benchmark rule does not permit the secondary random-anchor extension.'
        }
        Invoke-CnnPython $Eval 'run' `
            '--source' 'anchor' '--input' $AnchorRoot '--output' (Join-Path $OutputRoot 'anchor_secondary') `
            '--device' $Device '--batch-size' "$BatchSize" `
            '--anchor-families' 'random_rank10' 'random_fullrank' `
            '--set-families' 'selected' 'random' 'energy'
        Invoke-CnnPython $Analyze '--source' 'anchor' '--input' (Join-Path $OutputRoot 'anchor_secondary') '--out' (Join-Path $OutputRoot 'anchor_secondary_analysis')
        return
    }

    if ($Mode -eq 'Analyze') {
        Invoke-CnnPython $Analyze '--source' 'architecture' '--input' (Join-Path $OutputRoot 'architecture') '--out' (Join-Path $OutputRoot 'architecture_analysis')
        Invoke-CnnPython $Analyze '--source' 'anchor' '--input' (Join-Path $OutputRoot 'anchor') '--out' (Join-Path $OutputRoot 'anchor_analysis')
        return
    }
}
finally {
    Pop-Location
}