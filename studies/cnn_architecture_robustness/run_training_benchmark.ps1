param(
    [string]$OutputRoot = $(Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'prior-templates-cnns\benchmarks\stage_f_training'),
    [int]$CpuWorkers = 12,
    [ValidateSet('both','cpu','cuda')][string]$Mode = 'both',
    [int]$Repeats = 1,
    [string]$CondaEnv = $(if ($env:CNN_ENV_NAME) { $env:CNN_ENV_NAME } else { 'prior-templates-cnns' }),
    [string]$TorchIndexUrl = $(if ($env:TORCH_INDEX_URL) { $env:TORCH_INDEX_URL } else { 'https://download.pytorch.org/whl/cu128' })
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Push-Location $RepoRoot
try {
    $env:DEVICE = 'cuda'
    $env:CNN_ENV_NAME = $CondaEnv
    $env:TORCH_INDEX_URL = $TorchIndexUrl
    . (Join-Path $RepoRoot 'scripts\use_conda_env.ps1')

    $Benchmark = 'studies/cnn_architecture_robustness/benchmark_training.py'
    Invoke-CnnPython $Benchmark '--output' $OutputRoot '--cpu-workers' "$CpuWorkers" '--mode' $Mode '--repeats' "$Repeats"

    Write-Host ''
    Write-Host "Benchmark result: $OutputRoot\benchmark.json"
    Write-Host 'This benchmark is not part of Stage-F inferential data.'
}
finally {
    Pop-Location
}
