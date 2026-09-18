param(
    [string]$StageDRoot = $(if ($env:STAGE_D_ROOT) { $env:STAGE_D_ROOT } else { Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'prior-templates-cnns\results\budget_confirmation_001' }),
    [string]$StageERoot = $(if ($env:STAGE_E_ROOT) { $env:STAGE_E_ROOT } else { Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'prior-templates-cnns\results\exhaustive_robustness_001' }),
    [string]$OutputRoot = $(if ($env:OUTPUT_ROOT) { $env:OUTPUT_ROOT } else { Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'prior-templates-cnns\results\metric_sensitivity_001' }),
    [ValidateSet('cuda','cpu')][string]$Device = $(if ($env:DEVICE) { $env:DEVICE } else { 'cuda' }),
    [int]$BatchSize = $(if ($env:BATCH_SIZE) { [int]$env:BATCH_SIZE } else { 256 }),
    [string]$CondaEnv = $(if ($env:CNN_ENV_NAME) { $env:CNN_ENV_NAME } else { 'prior-templates-cnns' }),
    [string]$TorchIndexUrl = $(if ($env:TORCH_INDEX_URL) { $env:TORCH_INDEX_URL } else { 'https://download.pytorch.org/whl/cu128' })
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($BatchSize -lt 1) { throw 'BatchSize must be positive.' }

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Push-Location $RepoRoot
try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'git is required for provenance recording.' }

    $env:DEVICE = $Device
    $env:CNN_ENV_NAME = $CondaEnv
    $env:TORCH_INDEX_URL = $TorchIndexUrl
    . (Join-Path $RepoRoot 'scripts\use_conda_env.ps1')

    $StageDRoot = (Resolve-Path $StageDRoot).Path
    $StageERoot = (Resolve-Path $StageERoot).Path
    foreach ($required in @(
        (Join-Path $StageDRoot 'training\design.json'),
        (Join-Path $StageDRoot 'patch_eval\design.json'),
        (Join-Path $StageERoot 'training\design.json'),
        (Join-Path $StageERoot 'evaluation\design.json')
    )) {
        if (-not (Test-Path $required)) { throw "Missing required frozen input: $required" }
    }

    $StageDOut = Join-Path $OutputRoot 'stage_d'
    $StageEOut = Join-Path $OutputRoot 'stage_e'
    $AnalysisOut = Join-Path $OutputRoot 'analysis'
    $Manifest = Join-Path $OutputRoot 'execution_manifest.json'
    $Protocol = 'studies/cnn_metric_sensitivity/PROTOCOL.md'
    $Evaluator = 'studies/cnn_metric_sensitivity/evaluate_metrics.py'
    $Analyzer = 'studies/cnn_metric_sensitivity/analyze_metrics.py'

    New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

    function Get-GitBlobId([string]$RepoRelativePath) {
        $value = (& git rev-parse "HEAD:$RepoRelativePath").Trim()
        if ($LASTEXITCODE -ne 0 -or -not $value) {
            throw "Could not resolve committed Git blob for: $RepoRelativePath"
        }
        return $value
    }

    function Get-PythonSha256([string]$Path) {
        $hashScript = @'
import hashlib
import sys
from pathlib import Path

path = Path(sys.argv[1])
with path.open("rb") as handle:
    print(hashlib.sha256(handle.read()).hexdigest())
'@
        $hashScriptPath = Join-Path ([System.IO.Path]::GetTempPath()) ("cnn_sha256_{0}.py" -f [guid]::NewGuid().ToString('N'))
        try {
            [System.IO.File]::WriteAllText($hashScriptPath, $hashScript, [System.Text.Encoding]::UTF8)
            $lines = @(Invoke-CnnPython $hashScriptPath $Path)
            $value = ($lines | Select-Object -Last 1).ToString().Trim()
            if (-not $value -or $value.Length -ne 64) {
                throw "Could not compute SHA-256 with project Python for: $Path"
            }
            return $value
        }
        finally {
            Remove-Item $hashScriptPath -Force -ErrorAction SilentlyContinue
        }
    }

    $protocolCommit = (& git log -n 1 --format=%H -- $Protocol).Trim()
    $protocolBlob = Get-GitBlobId $Protocol
    $record = [ordered]@{
        created_utc = [DateTime]::UtcNow.ToString('o')
        repo_head_at_launch = (& git rev-parse HEAD).Trim()
        protocol_commit = $protocolCommit
        protocol_git_blob = $protocolBlob
        device = $Device
        batch_size = $BatchSize
        conda_environment = $CondaEnv
        stage_d_root = $StageDRoot
        stage_e_root = $StageERoot
        source_git_blobs = [ordered]@{
            protocol = $protocolBlob
            evaluator = Get-GitBlobId $Evaluator
            analyzer = Get-GitBlobId $Analyzer
            core = Get-GitBlobId 'studies/cnn_release_experiment/core.py'
        }
        input_design_sha256 = [ordered]@{
            stage_d_training = Get-PythonSha256 (Join-Path $StageDRoot 'training\design.json')
            stage_d_rankings = Get-PythonSha256 (Join-Path $StageDRoot 'patch_eval\design.json')
            stage_e_training = Get-PythonSha256 (Join-Path $StageERoot 'training\design.json')
            stage_e_rankings = Get-PythonSha256 (Join-Path $StageERoot 'evaluation\design.json')
        }
        training_invoked = $false
    }

    if (Test-Path $Manifest) {
        $old = Get-Content $Manifest -Raw | ConvertFrom-Json
        if ($old.protocol_git_blob -ne $record.protocol_git_blob -or
            $old.device -ne $Device -or
            [int]$old.batch_size -ne $BatchSize -or
            $old.stage_d_root -ne $StageDRoot -or
            $old.stage_e_root -ne $StageERoot) {
            throw 'Existing metric-sensitivity manifest is incompatible. Use a new OutputRoot.'
        }
        foreach ($name in @('protocol','evaluator','analyzer','core')) {
            if ($old.source_git_blobs.$name -ne $record.source_git_blobs[$name]) { throw "Committed source changed since this run started: $name" }
        }
        foreach ($name in @('stage_d_training','stage_d_rankings','stage_e_training','stage_e_rankings')) {
            if ($old.input_design_sha256.$name -ne $record.input_design_sha256[$name]) { throw "Frozen input design changed since this run started: $name" }
        }
    } else {
        $record | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 $Manifest
    }

    Write-Host "Protocol commit: $protocolCommit"
    Write-Host "Protocol Git blob: $protocolBlob"
    Write-Host "No training will be run."
    Write-Host ''
    Write-Host '[1/3] Re-evaluating Stage D checkpoints under frozen alternative metrics...'
    Invoke-CnnPython $Evaluator '--stage' 'd' '--input-root' $StageDRoot '--output' $StageDOut '--device' $Device '--batch-size' "$BatchSize"

    Write-Host ''
    Write-Host '[2/3] Re-evaluating Stage E checkpoints under frozen alternative metrics...'
    Invoke-CnnPython $Evaluator '--stage' 'e' '--input-root' $StageERoot '--output' $StageEOut '--device' $Device '--batch-size' "$BatchSize"

    Write-Host ''
    Write-Host '[3/3] Applying the frozen metric-sensitivity analysis...'
    Invoke-CnnPython $Analyzer '--stage-d' $StageDOut '--stage-e' $StageEOut '--out' $AnalysisOut

    Write-Host ''
    Write-Host 'Metric-sensitivity study complete.'
    Write-Host "Report:   $AnalysisOut\REPORT.md"
    Write-Host "Manifest: $Manifest"
}
finally {
    Pop-Location
}
