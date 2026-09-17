param(
    [ValidateSet('cuda','cpu')][string]$Device = $(if ($env:DEVICE) { $env:DEVICE } else { 'cuda' }),
    [string]$CondaEnv = $(if ($env:CNN_ENV_NAME) { $env:CNN_ENV_NAME } else { 'prior-templates-cnns' }),
    [int]$Workers = $(if ($env:WORKERS) { [int]$env:WORKERS } else { 8 }),
    [int]$ThreadsPerWorker = $(if ($env:THREADS_PER_WORKER) { [int]$env:THREADS_PER_WORKER } else { 2 }),
    [int]$ExhaustiveBatchSize = $(if ($env:EXHAUSTIVE_BATCH_SIZE) { [int]$env:EXHAUSTIVE_BATCH_SIZE } else { 256 }),
    [int]$ConfirmationBatchSize = $(if ($env:CONFIRMATION_BATCH_SIZE) { [int]$env:CONFIRMATION_BATCH_SIZE } else { 64 }),
    [int]$ConfirmationThreads = $(if ($env:CONFIRMATION_THREADS) { [int]$env:CONFIRMATION_THREADS } else { 2 })
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$LocalResultsRoot = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'prior-templates-cnns\results'
$ConfirmationRoot = Join-Path $LocalResultsRoot 'budget_confirmation_001'
$ExhaustiveRoot = Join-Path $LocalResultsRoot 'exhaustive_robustness_001'

Push-Location $RepoRoot
try {
    Write-Host '=== Stage D: frozen prospective confirmation (blocks 4000-4019) ==='
    & (Join-Path $RepoRoot 'studies\cnn_budget_confirmation\run_confirmation.ps1') `
        -OutputRoot $ConfirmationRoot -Device $Device -CondaEnv $CondaEnv `
        -BatchSize $ConfirmationBatchSize -Threads $ConfirmationThreads

    Write-Host ''
    Write-Host '=== Stage E: secondary sensitivity study (blocks 5000-5049) ==='
    & (Join-Path $RepoRoot 'studies\cnn_exhaustive_robustness\run_exhaustive.ps1') `
        -OutputRoot $ExhaustiveRoot -Device $Device -CondaEnv $CondaEnv `
        -Workers $Workers -ThreadsPerWorker $ThreadsPerWorker -BatchSize $ExhaustiveBatchSize

    Write-Host ''
    Write-Host 'All planned paper experiments finished.'
    Write-Host "Primary confirmation report: $(Join-Path $ConfirmationRoot 'analysis\budget_confirmation\REPORT.md')"
    Write-Host "Sensitivity-study report: $(Join-Path $ExhaustiveRoot 'analysis\REPORT.md')"
}
finally {
    Pop-Location
}
