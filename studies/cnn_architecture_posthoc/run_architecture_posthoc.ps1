param(
    [string]$StageFRoot = $(if ($env:STAGE_F_ROOT) {
        $env:STAGE_F_ROOT
    } else {
        Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'prior-templates-cnns\results\architecture_robustness_cuda_001'
    }),
    [string]$OutputRoot = $(if ($env:ARCH_POSTHOC_ROOT) {
        $env:ARCH_POSTHOC_ROOT
    } else {
        Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'prior-templates-cnns\results\architecture_posthoc_diagnostics_001'
    }),
    [string]$CondaEnv = $(if ($env:CNN_ENV_NAME) { $env:CNN_ENV_NAME } else { 'prior-templates-cnns' })
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Push-Location $RepoRoot
try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'git is required.' }

    $env:CNN_ENV_NAME = $CondaEnv
    . (Join-Path $RepoRoot 'scripts\use_conda_env.ps1')

    $EvaluationRoot = Join-Path $StageFRoot 'evaluation'
    if (-not (Test-Path (Join-Path $EvaluationRoot 'GRID_COMPLETE.json') -PathType Leaf)) {
        throw "Completed Stage-F evaluation not found: $EvaluationRoot"
    }

    New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

    $Protocol = 'studies/cnn_architecture_posthoc/PROTOCOL.md'
    $Analyzer = 'studies/cnn_architecture_posthoc/analyze.py'
    $Manifest = Join-Path $OutputRoot 'launch_manifest.json'

    function Get-GitBlobId([string]$RepoRelativePath) {
        $value = (& git rev-parse "HEAD:$RepoRelativePath").Trim()
        if ($LASTEXITCODE -ne 0 -or -not $value) {
            throw "Could not resolve committed Git blob for: $RepoRelativePath"
        }
        return $value
    }

    $record = [ordered]@{
        created_utc = [DateTime]::UtcNow.ToString('o')
        status = 'post_hoc_outcome_informed'
        repo_head_at_launch = (& git rev-parse HEAD).Trim()
        protocol_commit = (& git log -n 1 --format=%H -- $Protocol).Trim()
        protocol_git_blob = Get-GitBlobId $Protocol
        analyzer_git_blob = Get-GitBlobId $Analyzer
        architecture_core_git_blob = Get-GitBlobId 'studies/cnn_architecture_robustness/architecture_core.py'
        source_stage_f_root = (Resolve-Path $StageFRoot).Path
        source_evaluation_design_sha256 = (Get-FileHash (Join-Path $EvaluationRoot 'design.json') -Algorithm SHA256).Hash.ToLower()
        output_root = $OutputRoot
    }

    if (Test-Path $Manifest) {
        $old = Get-Content $Manifest -Raw | ConvertFrom-Json
        if ($old.protocol_git_blob -ne $record.protocol_git_blob -or
            $old.analyzer_git_blob -ne $record.analyzer_git_blob -or
            $old.architecture_core_git_blob -ne $record.architecture_core_git_blob -or
            $old.source_evaluation_design_sha256 -ne $record.source_evaluation_design_sha256) {
            throw 'Existing post hoc diagnostic manifest differs. Use a new OutputRoot.'
        }
    } else {
        $record | ConvertTo-Json -Depth 6 | Set-Content -Encoding utf8 $Manifest
    }

    Write-Host 'Running frozen post hoc architecture diagnostics...'
    Write-Host "Stage-F evaluation: $EvaluationRoot"
    Write-Host "Output:             $OutputRoot"
    Invoke-CnnPython $Analyzer '--input' $EvaluationRoot '--out' $OutputRoot

    Write-Host ''
    Write-Host 'Post hoc architecture diagnostics complete.'
    Write-Host "Report: $OutputRoot\REPORT.md"
    Write-Host 'Archive with: .\run\stage_architecture_posthoc_results.ps1'
}
finally {
    Pop-Location
}
