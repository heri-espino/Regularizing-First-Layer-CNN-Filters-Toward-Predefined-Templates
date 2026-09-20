param(
    [string]$OutputRoot = $(if ($env:STAGE_G_ROOT) {
        $env:STAGE_G_ROOT
    } else {
        Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'prior-templates-cnns\results\anchor_specificity_cuda_001'
    }),
    [ValidateSet('cpu','cuda')][string]$TrainDevice = 'cuda',
    [int]$TrainWorkers = 1,
    [int]$ThreadsPerWorker = 1,
    [ValidateSet('cpu','cuda')][string]$EvalDevice = 'cuda',
    [int]$EvalBatchSize = 256,
    [string]$CondaEnv = $(if ($env:CNN_ENV_NAME) { $env:CNN_ENV_NAME } else { 'prior-templates-cnns' }),
    [string]$TorchIndexUrl = $(if ($env:TORCH_INDEX_URL) { $env:TORCH_INDEX_URL } else { 'https://download.pytorch.org/whl/cu128' }),
    [switch]$Smoke
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($TrainWorkers -lt 1 -or $ThreadsPerWorker -lt 1 -or $EvalBatchSize -lt 1) {
    throw 'Workers, threads, and batch size must be positive.'
}
if ($TrainDevice -eq 'cuda' -and $TrainWorkers -ne 1) {
    throw 'CUDA training requires TrainWorkers=1.'
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Push-Location $RepoRoot
try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw 'git is required for frozen provenance recording.'
    }

    $env:DEVICE = $EvalDevice
    $env:CNN_ENV_NAME = $CondaEnv
    $env:TORCH_INDEX_URL = $TorchIndexUrl
    . (Join-Path $RepoRoot 'scripts\use_conda_env.ps1')

    if ($Smoke -and $OutputRoot -like '*anchor_specificity_cuda_001') {
        $OutputRoot = $OutputRoot -replace 'anchor_specificity_cuda_001
    $EvaluationRoot = Join-Path $OutputRoot 'evaluation'
    $AnalysisRoot = Join-Path $OutputRoot 'analysis'
    $Manifest = Join-Path $OutputRoot 'execution_manifest.json'
    New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

    $Protocol = 'studies/cnn_anchor_specificity/PROTOCOL.md'
    $Core = 'studies/cnn_anchor_specificity/anchor_core.py'
    $Trainer = 'studies/cnn_anchor_specificity/train_grid.py'
    $Evaluator = 'studies/cnn_anchor_specificity/evaluate_grid.py'
    $Analyzer = 'studies/cnn_anchor_specificity/analyze.py'

    function Get-GitBlobId([string]$RepoRelativePath) {
        $value = (& git rev-parse "HEAD:$RepoRelativePath").Trim()
        if ($LASTEXITCODE -ne 0 -or -not $value) {
            throw "Could not resolve committed Git blob for: $RepoRelativePath"
        }
        return $value
    }

    $protocolCommit = (& git log -n 1 --format=%H -- $Protocol).Trim()
    $record = [ordered]@{
        created_utc = [DateTime]::UtcNow.ToString('o')
        repo_head_at_launch = (& git rev-parse HEAD).Trim()
        protocol_commit = $protocolCommit
        protocol_git_blob = Get-GitBlobId $Protocol
        source_git_blobs = [ordered]@{
            protocol = Get-GitBlobId $Protocol
            anchor_core = Get-GitBlobId $Core
            trainer = Get-GitBlobId $Trainer
            evaluator = Get-GitBlobId $Evaluator
            analyzer = Get-GitBlobId $Analyzer
            architecture_core = Get-GitBlobId 'studies/cnn_architecture_robustness/architecture_core.py'
            legacy_core = Get-GitBlobId 'studies/cnn_release_experiment/core.py'
        }
        output_root = $OutputRoot
        train_device = $TrainDevice
        train_workers = $TrainWorkers
        threads_per_worker = $ThreadsPerWorker
        eval_device = $EvalDevice
        eval_batch_size = $EvalBatchSize
        smoke = [bool]$Smoke
    }

    if (Test-Path $Manifest) {
        $old = Get-Content $Manifest -Raw | ConvertFrom-Json
        foreach ($name in @('protocol','anchor_core','trainer','evaluator','analyzer','architecture_core','legacy_core')) {
            if ($old.source_git_blobs.$name -ne $record.source_git_blobs[$name]) {
                throw "Stage-G source changed since this output root was initialized: $name. Use a new OutputRoot."
            }
        }
        if ($old.protocol_git_blob -ne $record.protocol_git_blob -or
            $old.train_device -ne $TrainDevice -or
            [int]$old.train_workers -ne $TrainWorkers -or
            [int]$old.threads_per_worker -ne $ThreadsPerWorker -or
            $old.eval_device -ne $EvalDevice -or
            [int]$old.eval_batch_size -ne $EvalBatchSize -or
            [bool]$old.smoke -ne [bool]$Smoke) {
            throw 'Existing Stage-G manifest is incompatible. Use a new OutputRoot.'
        }
    } else {
        $record | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 $Manifest
    }

    Write-Host "Anchor-specificity protocol commit: $protocolCommit"
    Write-Host "Output root: $OutputRoot"
    Write-Host "Training: $TrainDevice"
    Write-Host "Evaluation: $EvalDevice"
    Write-Host ''

    $trainArgs = @(
        $Trainer,
        '--output', $TrainingRoot,
        '--device', $TrainDevice,
        '--workers', "$TrainWorkers",
        '--threads-per-worker', "$ThreadsPerWorker"
    )
    if ($Smoke) { $trainArgs += '--smoke' }

    Write-Host '[1/3] Training frozen anchor-specificity grid...'
    Invoke-CnnPython @trainArgs

    Write-Host ''
    Write-Host '[2/3] Evaluating patch budgets and controls...'
    $evalArgs = @(
        $Evaluator,
        '--input', $TrainingRoot,
        '--output', $EvaluationRoot,
        '--device', $EvalDevice,
        '--batch-size', "$EvalBatchSize"
    )
    if ($Smoke) { $evalArgs += '--smoke' }
    Invoke-CnnPython @evalArgs

    if ($Smoke) {
        Write-Host ''
        Write-Host 'Anchor-specificity smoke run complete. Frozen inferential analysis skipped.'
        Write-Host "Smoke output: $OutputRoot"
        return
    }

    Write-Host ''
    Write-Host '[3/3] Applying frozen anchor-specificity analysis...'
    Invoke-CnnPython $Analyzer '--input' $EvaluationRoot '--out' $AnalysisRoot

    Write-Host ''
    Write-Host 'Anchor-specificity experiment complete.'
    Write-Host "Report:   $AnalysisRoot\REPORT.md"
    Write-Host "Manifest: $Manifest"
    Write-Host ''
    Write-Host 'Archive paper-facing outputs with:'
    Write-Host '  .\run\stage_anchor_specificity_results.ps1'
}
finally {
    Pop-Location
}
, 'anchor_specificity_smoke'
        # Smoke outputs are implementation-only and intentionally disposable.
        # Clearing the default smoke root prevents stale source manifests from
        # blocking a fresh smoke after code/protocol hardening.
        if (Test-Path -LiteralPath $OutputRoot) {
            Remove-Item -LiteralPath $OutputRoot -Recurse -Force
        }
    }

    $TrainingRoot = Join-Path $OutputRoot 'training'
    $EvaluationRoot = Join-Path $OutputRoot 'evaluation'
    $AnalysisRoot = Join-Path $OutputRoot 'analysis'
    $Manifest = Join-Path $OutputRoot 'execution_manifest.json'
    New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

    $Protocol = 'studies/cnn_anchor_specificity/PROTOCOL.md'
    $Core = 'studies/cnn_anchor_specificity/anchor_core.py'
    $Trainer = 'studies/cnn_anchor_specificity/train_grid.py'
    $Evaluator = 'studies/cnn_anchor_specificity/evaluate_grid.py'
    $Analyzer = 'studies/cnn_anchor_specificity/analyze.py'

    function Get-GitBlobId([string]$RepoRelativePath) {
        $value = (& git rev-parse "HEAD:$RepoRelativePath").Trim()
        if ($LASTEXITCODE -ne 0 -or -not $value) {
            throw "Could not resolve committed Git blob for: $RepoRelativePath"
        }
        return $value
    }

    $protocolCommit = (& git log -n 1 --format=%H -- $Protocol).Trim()
    $record = [ordered]@{
        created_utc = [DateTime]::UtcNow.ToString('o')
        repo_head_at_launch = (& git rev-parse HEAD).Trim()
        protocol_commit = $protocolCommit
        protocol_git_blob = Get-GitBlobId $Protocol
        source_git_blobs = [ordered]@{
            protocol = Get-GitBlobId $Protocol
            anchor_core = Get-GitBlobId $Core
            trainer = Get-GitBlobId $Trainer
            evaluator = Get-GitBlobId $Evaluator
            analyzer = Get-GitBlobId $Analyzer
            architecture_core = Get-GitBlobId 'studies/cnn_architecture_robustness/architecture_core.py'
            legacy_core = Get-GitBlobId 'studies/cnn_release_experiment/core.py'
        }
        output_root = $OutputRoot
        train_device = $TrainDevice
        train_workers = $TrainWorkers
        threads_per_worker = $ThreadsPerWorker
        eval_device = $EvalDevice
        eval_batch_size = $EvalBatchSize
        smoke = [bool]$Smoke
    }

    if (Test-Path $Manifest) {
        $old = Get-Content $Manifest -Raw | ConvertFrom-Json
        foreach ($name in @('protocol','anchor_core','trainer','evaluator','analyzer','architecture_core','legacy_core')) {
            if ($old.source_git_blobs.$name -ne $record.source_git_blobs[$name]) {
                throw "Stage-G source changed since this output root was initialized: $name. Use a new OutputRoot."
            }
        }
        if ($old.protocol_git_blob -ne $record.protocol_git_blob -or
            $old.train_device -ne $TrainDevice -or
            [int]$old.train_workers -ne $TrainWorkers -or
            [int]$old.threads_per_worker -ne $ThreadsPerWorker -or
            $old.eval_device -ne $EvalDevice -or
            [int]$old.eval_batch_size -ne $EvalBatchSize -or
            [bool]$old.smoke -ne [bool]$Smoke) {
            throw 'Existing Stage-G manifest is incompatible. Use a new OutputRoot.'
        }
    } else {
        $record | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 $Manifest
    }

    Write-Host "Anchor-specificity protocol commit: $protocolCommit"
    Write-Host "Output root: $OutputRoot"
    Write-Host "Training: $TrainDevice"
    Write-Host "Evaluation: $EvalDevice"
    Write-Host ''

    $trainArgs = @(
        $Trainer,
        '--output', $TrainingRoot,
        '--device', $TrainDevice,
        '--workers', "$TrainWorkers",
        '--threads-per-worker', "$ThreadsPerWorker"
    )
    if ($Smoke) { $trainArgs += '--smoke' }

    Write-Host '[1/3] Training frozen anchor-specificity grid...'
    Invoke-CnnPython @trainArgs

    Write-Host ''
    Write-Host '[2/3] Evaluating patch budgets and controls...'
    $evalArgs = @(
        $Evaluator,
        '--input', $TrainingRoot,
        '--output', $EvaluationRoot,
        '--device', $EvalDevice,
        '--batch-size', "$EvalBatchSize"
    )
    if ($Smoke) { $evalArgs += '--smoke' }
    Invoke-CnnPython @evalArgs

    if ($Smoke) {
        Write-Host ''
        Write-Host 'Anchor-specificity smoke run complete. Frozen inferential analysis skipped.'
        Write-Host "Smoke output: $OutputRoot"
        return
    }

    Write-Host ''
    Write-Host '[3/3] Applying frozen anchor-specificity analysis...'
    Invoke-CnnPython $Analyzer '--input' $EvaluationRoot '--out' $AnalysisRoot

    Write-Host ''
    Write-Host 'Anchor-specificity experiment complete.'
    Write-Host "Report:   $AnalysisRoot\REPORT.md"
    Write-Host "Manifest: $Manifest"
    Write-Host ''
    Write-Host 'Archive paper-facing outputs with:'
    Write-Host '  .\run\stage_anchor_specificity_results.ps1'
}
finally {
    Pop-Location
}
